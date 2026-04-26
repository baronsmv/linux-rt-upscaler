import logging
import struct
from dataclasses import dataclass
from typing import List, Tuple

from .utils import expand_damage_rects
from ..config import Config
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..vulkan import Buffer, Compute, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TileSpec:
    """Immutable description of a tile's geometry."""

    tx: int
    ty: int
    valid_lr_offset_x: int  # interior offset inside expanded tile (low-res pixels)
    valid_lr_offset_y: int  # same

    # derived quantities (cached for convenience)
    dst_out_px_x: int
    dst_out_px_y: int
    tile_out_extent_w: int
    tile_out_extent_h: int

    @classmethod
    def from_raw(
        cls,
        tx: int,
        ty: int,
        valid_x: int,
        valid_y: int,
        tile_size: int,
        scale: int,
        full_out_w: int,
        full_out_h: int,
    ) -> "TileSpec":
        dst_out_x = tx * tile_size * scale
        dst_out_y = ty * tile_size * scale
        extent_w = min(tile_size * scale, full_out_w - dst_out_x)
        extent_h = min(tile_size * scale, full_out_h - dst_out_y)
        return cls(tx, ty, valid_x, valid_y, dst_out_x, dst_out_y, extent_w, extent_h)


class TileProcessor:
    """
    Direct tile-based upscaling processor.

    The processor divides the captured crop area into a grid of tiles of size
    `tile_size`. Each dirty tile (overlapping a damage rectangle) is expanded
    by a context margin, uploaded to a dedicated layer of an array texture,
    and processed by the SRCNN pipeline. The final pass writes the interior
    region directly to the full output texture (a 2D array with 1 slice).

    Attributes:
        crop_width (int): Width of the captured crop area in pixels.
        crop_height (int): Height of the captured crop area in pixels.
        tile_size (int): Nominal tile size (interior region) in pixels.
        margin (int): Context margin added around each tile.
        double_upscale (bool): If True, perform 4x upscaling (two 2x stages).
        max_layers (int): Maximum concurrent tiles per batch.
        expanded_tile_size (int): tile_size + (2 * margin).
        tile_out_w_final (int): Width of final upscaled tile.
        tile_out_h_final (int): Height of final upscaled tile.
        output_texture (Texture2D): Final full-frame upscaled texture (1 slice).
        factory (PipelineFactory): Shared factory for SRCNN pipelines.
        stages (List[SRCNN]): SRCNN stage instances.
        groups_per_stage (List[Tuple[int, int]]): Dispatch groups per stage.
        input_tex (Texture2D): Input array texture for tile data.
        full_input_tex (Texture2D): Residual texture (full frame, updated per damage).
        staging (Buffer): Staging buffer for tile uploads.
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
        model_variant: str = "_tile",
        push_constant_size: int = 40,
    ) -> None:
        """
        Initialize the direct tile processor.

        Args:
            config: Global configuration object (may be updated at runtime).
            crop_width: Width of the captured crop area in pixels.
            crop_height: Height of the captured crop area in pixels.
            max_layers: Maximum concurrent tiles per batch.
            model_variant: Suffix of the shaders used.
            push_constant_size: TileParams push data size.

        Raises:
            ValueError: If crop dimensions are non-positive.
            FileNotFoundError: If model files are missing.
        """
        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.margin = config.tile_context_margin
        self.tile_size = config.tile_size
        self.double_upscale = config.double_upscale
        self.area_threshold = config.area_threshold
        self.max_layers = config.max_tile_layers

        if crop_width <= 0 or crop_height <= 0:
            raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")
        if self.tile_size <= 0 or self.max_layers <= 0:
            raise ValueError("Invalid tile_size or max_layers")

        # Sizes
        self.expanded_tile_size = self.tile_size + 2 * self.margin
        self.scale = 4 if self.double_upscale else 2
        self.full_out_w = crop_width * self.scale
        self.full_out_h = crop_height * self.scale

        # Factory
        model_config = load_cunny_model(
            config.model, variant=model_variant, push_constant_size=push_constant_size
        )
        self.push_constant_size = push_constant_size
        self.factory = PipelineFactory(model_config)

        # Residual (full low-res frame), updated each frame with damage
        self.residual_tex = Texture2D(
            crop_width, crop_height, slices=1, force_array_view=True
        )
        self.residual_staging = Buffer(
            crop_width * crop_height * 4, heap_type=HEAP_UPLOAD
        )

        # Staging for tile data - resized on demand in process_tiles
        self.staging = Buffer(
            self.expanded_tile_size * self.expanded_tile_size * 4,
            heap_type=HEAP_UPLOAD,
        )

        # SRCNN stages and dispatch groups
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []
        self._create_stages()

        # Custom final pipeline (writes to the full output texture)
        self._finalize_pipeline()

        logger.info(
            f"TileProcessor: crop={crop_width}x{crop_height}, "
            f"tile={self.tile_size}, margin={self.margin}, "
            f"scale={self.scale}x, layers={self.max_layers}"
        )

    # ------------------------------------------------------------------
    #  Stage creation
    # ------------------------------------------------------------------
    def _create_stages(self) -> None:
        """Set up SRCNN stages with array textures correctly sized."""
        # Common sizes
        lr = self.expanded_tile_size  # low-res
        single_2x = lr * 2
        single_4x = lr * 4

        # Input texture (array, low-res)
        input_tex = Texture2D(lr, lr, slices=self.max_layers, force_array_view=True)

        # Stage 1: lr to 2x
        inter_tex = Texture2D(
            single_2x, single_2x, slices=self.max_layers, force_array_view=True
        )
        out1 = {"output": inter_tex}
        for i in range(self.factory.config.num_textures):
            out1[f"t{i}"] = Texture2D(
                lr, lr, slices=self.max_layers, force_array_view=True
            )

        srnn1 = SRCNN(
            factory=self.factory,
            width=lr,
            height=lr,
            input_texture=input_tex,
            output_textures=out1,
            push_constant_size=self.push_constant_size,
        )
        self.stages.append(srnn1)
        self.groups_per_stage.append(dispatch_groups(lr, lr, last_pass=False))

        if self.double_upscale:
            # Stage 2: 2x to 4x
            final_out_array = Texture2D(
                single_4x, single_4x, slices=self.max_layers, force_array_view=True
            )
            out2 = {"output": final_out_array}
            for i in range(self.factory.config.num_textures):
                out2[f"t{i}"] = Texture2D(
                    single_2x, single_2x, slices=self.max_layers, force_array_view=True
                )

            srnn2 = SRCNN(
                factory=self.factory,
                width=single_2x,
                height=single_2x,
                input_texture=inter_tex,
                output_textures=out2,
                push_constant_size=self.push_constant_size,
            )
            self.stages.append(srnn2)
            self.groups_per_stage.append(
                dispatch_groups(single_2x, single_2x, last_pass=False)
            )
        else:
            # Single stage: reuse output textures at final size
            final_out_array = Texture2D(
                single_2x, single_2x, slices=self.max_layers, force_array_view=True
            )
            out1["output"] = final_out_array
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=lr,
                height=lr,
                input_texture=input_tex,
                output_textures=out1,
                push_constant_size=self.push_constant_size,
            )
            self.groups_per_stage[0] = dispatch_groups(lr, lr, last_pass=False)

        # Output texture accessible from outside
        self.output_texture = Texture2D(
            self.full_out_w, self.full_out_h, slices=1, force_array_view=True
        )

    # ------------------------------------------------------------------
    #  Custom final pipeline
    # ------------------------------------------------------------------
    def _finalize_pipeline(self) -> None:
        """Build a custom pipeline that writes the final pass into self.output_texture."""
        final_pass_idx = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_idx]

        # The feature map resolution for the last SRCNN stage
        if self.double_upscale:
            feat_lr = self.expanded_tile_size * 2
            pre_final = self.stages[-2]
        else:
            feat_lr = self.expanded_tile_size
            pre_final = self.stages[0]

        # Constant buffer for the final shader
        cb_data = struct.pack(
            "IIIIffff",
            feat_lr,
            feat_lr,  # in_width, in_height (feature map size)
            self.full_out_w,
            self.full_out_h,
            1.0 / feat_lr,
            1.0 / feat_lr,
            1.0 / self.full_out_w,
            1.0 / self.full_out_h,
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        srv_list = [self.residual_tex]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final.outputs[f"t{i}"])

        uav_list = [self.output_texture]
        sampler_list = [
            self.factory._get_sampler(t)
            for t in self.factory.config.samplers[final_pass_idx]
        ]

        final_pipe = Compute(
            final_shader,
            cbv=[final_cb],
            srv=srv_list,
            uav=uav_list,
            samplers=sampler_list,
            push_size=self.push_constant_size,
        )

        # Replace the original final pipeline in the appropriate stage
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = final_pipe
        else:
            self.stages[0].pipelines[-1] = final_pipe

    # ------------------------------------------------------------------
    #  Residual (full-frame) updates
    # ------------------------------------------------------------------
    def upload_residual(
        self, frame: memoryview, rects: List[Tuple[int, int, int, int, int]]
    ) -> None:
        """Update the residual texture with damage regions."""
        if not rects:
            return

        expanded = expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.margin
        )
        if not expanded:
            return

        total_area = sum(w * h for _, _, w, h in expanded)
        threshold = self.area_threshold * self.crop_width * self.crop_height

        if total_area <= threshold:
            uploads = []
            stride = self.crop_width * 4
            for ex, ey, ew, eh in expanded:
                rect_data = bytearray(ew * eh * 4)
                for row in range(eh):
                    src_start = (ey + row) * stride + ex * 4
                    dst_start = row * ew * 4
                    rect_data[dst_start : dst_start + ew * 4] = frame[
                        src_start : src_start + ew * 4
                    ]
                uploads.append((bytes(rect_data), ex, ey, ew, eh, 0))
            self.residual_tex.upload_subresources(uploads)
        else:
            frame_bytes = bytes(frame)
            self.residual_tex.upload_subresources(
                [(frame_bytes, 0, 0, self.crop_width, self.crop_height, 0)]
            )

    # ------------------------------------------------------------------
    #  Tile processing
    # ------------------------------------------------------------------
    def process_tiles(
        self, dirty_tiles: List[Tuple[int, int, bytes, int, int]]
    ) -> None:
        """
        Process a batch of dirty tiles.

        Args:
            dirty_tiles: List of (tx, ty, data, valid_x, valid_y)
        """
        if not dirty_tiles:
            return

        batch = dirty_tiles[: self.max_layers]
        num_tiles = len(batch)

        expected_data = self.expanded_tile_size * self.expanded_tile_size * 4
        total_staging = num_tiles * expected_data
        self._ensure_staging(total_staging)

        # Build TileSpec objects for each tile
        specs = []
        for tx, ty, data, vx, vy in batch:
            spec = TileSpec.from_raw(
                tx,
                ty,
                vx,
                vy,
                self.tile_size,
                self.scale,
                self.full_out_w,
                self.full_out_h,
            )
            specs.append(spec)

        # Upload pixel data to input array layers 0..num_tiles-1
        uploads = []
        for i, (tx, ty, data, vx, vy) in enumerate(batch):
            data = self._sanitize_data(data, expected_data)
            uploads.append(
                (data, 0, 0, self.expanded_tile_size, self.expanded_tile_size, i)
            )
        self.stages[0].input.upload_subresources(uploads)

        if self.double_upscale:
            self._dispatch_double(specs)
        else:
            self._dispatch_single(specs)

    def _ensure_staging(self, required: int) -> None:
        if self.staging.size < required:
            self.staging = Buffer(required, heap_type=HEAP_UPLOAD)

    @staticmethod
    def _sanitize_data(data: bytes, expected: int) -> bytes:
        if len(data) != expected:
            if len(data) < expected:
                data += b"\x00" * (expected - len(data))
            else:
                data = data[:expected]
        return data

    # ------------------------------------------------------------------
    #  Push constant helpers
    # ------------------------------------------------------------------
    def _make_push_bytes(
        self, layer: int, spec: TileSpec, margin: int, valid_offset_mult: int = 1
    ) -> bytes:
        """
        Build push constant bytes for one tile and one stage.

        valid_offset_mult: 1 for first stage (low-res),
                           2 for second stage (2x upscaled tile).
        """
        return struct.pack(
            "I" * 10,
            layer,  # inputLayer
            spec.dst_out_px_x,
            spec.dst_out_px_y,  # dstOffset
            self.full_out_w,
            self.full_out_h,
            margin,
            spec.valid_lr_offset_x * valid_offset_mult,
            spec.valid_lr_offset_y * valid_offset_mult,
            spec.tile_out_extent_w,
            spec.tile_out_extent_h,
        )

    # ------------------------------------------------------------------
    #  Dispatch sequences
    # ------------------------------------------------------------------
    def _dispatch_single(self, specs: List[TileSpec]) -> None:
        """Single-stage dispatch."""
        gx, gy = self.groups_per_stage[0]
        dispatches = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin, valid_offset_mult=1)
            for pipe in self.stages[0].pipelines:
                dispatches.append((pipe, gx, gy, 1, push))
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

    def _dispatch_double(self, specs: List[TileSpec]) -> None:
        """Two-stage dispatch with correct push constants for every pass."""
        # Stage 1 (lr to 2x) - push constants with valid_offset_mult=1
        gx1, gy1 = self.groups_per_stage[0]
        dispatches_s1 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin, valid_offset_mult=1)
            for pipe in self.stages[0].pipelines:
                dispatches_s1.append((pipe, gx1, gy1, 1, push))

        # Stage 2 (2x to 4x) - push constants with valid_offset_mult=2
        gx2, gy2 = self.groups_per_stage[1]
        dispatches_s2 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin * 2, valid_offset_mult=2)
            for pipe in self.stages[1].pipelines:
                dispatches_s2.append((pipe, gx2, gy2, 1, push))

        # Submit both sequences separately
        if dispatches_s1:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches_s1)
        if dispatches_s2:
            self.stages[1].pipelines[0].dispatch_sequence(sequence=dispatches_s2)
