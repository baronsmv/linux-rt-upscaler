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
    """
    Immutable description of one tile's geometry in the final upscaled frame.

    The processor divides the crop area into a grid of `tile_size x tile_size`
    cells (low-resolution).  Each cell is expanded by a context margin, upscaled
    through the SRCNN stages, and then the interior is written back to the full
    output texture.  This class holds the per-tile values that are packed into
    the push-constant block (`TileParams` in HLSL).
    """

    tx: int  # tile grid X coordinate (0-based)
    ty: int  # tile grid Y coordinate (0-based)

    # These two fields are computed during tile extraction and represent the
    # offset (in low-res pixels) from the top-left of the *expanded* tile to
    # the start of the valid interior region.  At the image borders the
    # expansion is clamped, so this value may be smaller than `margin`.
    # The shader currently does NOT read these fields - they are kept for
    # future use or for debugging.
    valid_lr_offset_x: int
    valid_lr_offset_y: int

    # Pre-computed output destination in the full upscaled frame.
    dst_out_px_x: int  # top-left X of this tile’s output rectangle
    dst_out_px_y: int  # top-left Y
    tile_out_extent_w: int  # width  of the region to write (may be clipped)
    tile_out_extent_h: int  # height (clipped at right/bottom edges)

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
        """
        Create a TileSpec from tile grid coordinates and raw valid offsets.

        Parameters:
            tx, ty: Tile grid indices.
            valid_x, valid_y: Valid interior offset inside the expanded tile
                              (in low-res pixels), computed during extraction.
            tile_size: Nominal tile size in low-res pixels.
            scale: Upscale factor (2 for 2x, 4 for 4x).
            full_out_w, full_out_h: Dimensions of the final upscaled frame.
        """
        # Top-left of the output rectangle (in upscaled pixels).
        dst_out_x = tx * tile_size * scale
        dst_out_y = ty * tile_size * scale

        # The tile at the right or bottom edge may be clipped.
        extent_w = min(tile_size * scale, full_out_w - dst_out_x)
        extent_h = min(tile_size * scale, full_out_h - dst_out_y)

        return cls(tx, ty, valid_x, valid_y, dst_out_x, dst_out_y, extent_w, extent_h)


class TileProcessor:
    """
    Direct tile-based upscaling processor.

    The processor divides the captured crop area into a grid of tiles of size
    `tile_size`.  Each *dirty* tile (overlapping a damage rectangle) is
    expanded by a context margin, uploaded to a dedicated layer of an
    **array texture**, and processed by the SRCNN pipeline.  The final pass
    writes the interior region directly to the full output texture.

    Overview of the tile pipeline:
    1. **Expanded tile extraction** (in `tiles/utils.py`):
       - For each tile that touches a damage rectangle, an expanded region
         `(tile_size + 2*margin) x (tile_size + 2*margin)` is extracted.
       - At image borders the expansion is clamped and missing pixels are
         filled by edge replication.

    2. **Upload to array texture**:
       - Each expanded tile is uploaded to a separate slice of a 2D array
         texture.  Up to `max_layers` tiles can be processed concurrently.

    3. **SRCNN passes 1-3 (or 1-2 for single upscale)**:
       - The intermediate passes operate entirely on array textures, using the
         push-constant field `inputLayer` to select the correct slice.
       - The dispatch grid covers the expanded tile size (e.g. 40x40 for a
         32x32 tile with margin 4).

    4. **Final shuffle pass (Pass4)**:
       - This pass reads the residual texture (the full low-res frame, kept
         up-to-date with damage regions) and the feature maps produced by the
         last intermediate stage.
       - It writes 2x2 upscaled pixel blocks **directly into the final 2D
         output texture** at the correct global coordinates.
       - The push-constant `dstOffset` and `tileOutExtent` tell the shader
         *where* to write; `margin` tells it the starting offset inside the
         expanded feature map so it correctly aligns the convolution sampling.

    Why a separate final pass?
       The intermediate passes use array textures for concurrency, but the
       Lanczos presentation scaler expects a **plain 2D** texture.  The final
       pass merges the residual frame and feature maps into a single 2D output,
       avoiding any texture type mismatch.
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
        model_variant: str = "_tile",
        push_constant_size: int = 32,  # 8 uint fields x 4 bytes (see _make_push_bytes)
    ) -> None:
        """
        Initialize the tile processor.

        Parameters:
            config: Global configuration (model, tile size, margin, etc.).
            crop_width, crop_height: Dimensions of the captured crop area in pixels.
            model_variant: Suffix for shader files (e.g., "_tile").
            push_constant_size: Size of the push-constant block in bytes.
        """
        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.margin = config.tile_context_margin  # context margin in pixels
        self.tile_size = config.tile_size  # nominal interior size
        self.double_upscale = config.double_upscale  # True -> 4x, False -> 2x
        self.area_threshold = config.area_threshold
        self.max_layers = config.max_tile_layers  # how many tiles per batch

        if crop_width <= 0 or crop_height <= 0:
            raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")
        if self.tile_size <= 0 or self.max_layers <= 0:
            raise ValueError("Invalid tile_size or max_layers")

        # --- Derived sizes ---------------------------------------------------
        # Expanded tile includes the context margin on all four sides.
        self.expanded_tile_size = self.tile_size + 2 * self.margin
        self.scale = 4 if self.double_upscale else 2
        self.full_out_w = crop_width * self.scale
        self.full_out_h = crop_height * self.scale

        # --- Model & pipeline factory ----------------------------------------
        model_config = load_cunny_model(
            config.model, variant=model_variant, push_constant_size=push_constant_size
        )
        self.push_constant_size = push_constant_size
        self.factory = PipelineFactory(model_config)

        # --- Residual texture -------------------------------------------------
        # Holds the *full* low-res frame, updated each frame with the damage
        # regions.  This is read by the final pass to supply the YUV reference
        # for the residual addition (the “skip connection” in the shuffle).
        self.residual_tex = Texture2D(
            crop_width, crop_height, slices=1, force_array_view=True
        )
        self.residual_staging = Buffer(
            crop_width * crop_height * 4, heap_type=HEAP_UPLOAD
        )

        # --- Staging buffer for tile pixel data ------------------------------
        # Will be resized on demand in process_tiles().
        self.staging = Buffer(
            self.expanded_tile_size * self.expanded_tile_size * 4,
            heap_type=HEAP_UPLOAD,
        )

        # --- SRCNN stages and dispatch groups --------------------------------
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []
        self._create_stages()

        # --- Custom final pipeline (writes into self.output_texture) --------
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
        """
        Create the SRCNN stages (one for 2x, two for 4x) with array textures.

        All intermediate textures are 2D arrays with `max_layers` slices.
        This allows multiple tiles to be processed concurrently: each tile
        occupies its own slice, selected by the push constant `inputLayer`.
        """
        lr = self.expanded_tile_size  # low-res feature map size
        single_2x = lr * 2
        single_4x = lr * 4

        # Input: array texture to hold the expanded tile data.
        input_tex = Texture2D(lr, lr, slices=self.max_layers, force_array_view=True)

        # ---- Stage 1: low-res -> 2x -----------------------------------------
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
            # ---- Stage 2: 2x -> 4x ------------------------------------------
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
            # Single stage: reuse output textures at final size.
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

        # The final output texture is a *plain 2D* image, which matches the
        # Lanczos scaler’s input requirement.
        self.output_texture = Texture2D(self.full_out_w, self.full_out_h)

    # ------------------------------------------------------------------
    #  Custom final pipeline
    # ------------------------------------------------------------------
    def _finalize_pipeline(self) -> None:
        """
        Build a pipeline that replaces the last pass’s built-in pipeline.

        The built-in last pass would write to the array texture `final_out_array`.
        Here we create a *custom* Compute pipeline that writes directly into
        `self.output_texture` (a plain 2D image).  The constant buffer
        is populated with:
          - in_width / in_height: feature-map size for the last stage
            (expanded_tile_size x scale).
          - out_width / out_height: full upscaled frame size.
          - in_dx / in_dy: 1 / (feature-map size).
          - out_dx / out_dy: 1 / (full upscaled size).
        These match the `Constants` cbuffer in `Pass4_tile.hlsl`.
        """
        final_pass_idx = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_idx]

        if self.double_upscale:
            feat_lr = self.expanded_tile_size * 2  # 2x upscaled tile
            pre_final = self.stages[-1]
        else:
            feat_lr = self.expanded_tile_size
            pre_final = self.stages[0]

        cb_data = struct.pack(
            "IIIIffff",
            feat_lr,  # in_width
            feat_lr,  # in_height
            self.full_out_w,  # out_width
            self.full_out_h,  # out_height
            1.0 / feat_lr,  # in_dx
            1.0 / feat_lr,  # in_dy
            1.0 / self.full_out_w,  # out_dx
            1.0 / self.full_out_h,  # out_dy
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        # SRV list: residual texture + the feature maps from the last stage.
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

        # Replace the original built-in pipeline for the last pass.
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
        """
        Update the residual (full low-res frame) with damage regions.

        The residual is used by the final shuffle pass to provide the
        “original” pixel values for the YUV conversion.  Only the areas
        that have changed (expanded by the context margin) are uploaded
        to save bandwidth; if the total damaged area exceeds a threshold,
        the entire frame is uploaded.
        """
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
            # Partial upload: extract each expanded rectangle from the frame.
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
            # Full upload.
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

        Each dirty tile contains the expanded pixel data and the valid
        interior offset.  The tiles are uploaded to consecutive slices
        of the input array texture, and then the SRCNN stages are
        dispatched with per-tile push constants.

        Parameters:
            dirty_tiles: List of (tx, ty, pixel_data, valid_x, valid_y).
        """
        if not dirty_tiles:
            return

        batch = dirty_tiles[: self.max_layers]
        num_tiles = len(batch)

        expected_data = self.expanded_tile_size * self.expanded_tile_size * 4
        total_staging = num_tiles * expected_data
        self._ensure_staging(total_staging)

        # Build TileSpec objects for each tile (pre-computes output coords).
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

        # Upload each tile’s pixel data to array slices 0 ... num_tiles-1.
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
    def _make_push_bytes(self, layer: int, spec: TileSpec, margin: int) -> bytes:
        """
        Serialize the push-constant block for one tile and one stage.

        Layout (8 x uint32 = 32 bytes) - must match `struct TileParams` in HLSL:

        ┌─────────────────┬──────────────────────────────────────────┐
        │ Field           │ Description                              │
        ├─────────────────┼──────────────────────────────────────────┤
        │ inputLayer      │ Array slice of the tile input data       │
        │ dstOffset.x     │ Top-left X of the output rectangle       │
        │ dstOffset.y     │ Top-left Y of the output rectangle       │
        │ fullOutWidth    │ Width of the final upscaled frame        │
        │ fullOutHeight   │ Height of the final upscaled frame       │
        │ margin          │ Context margin (in feature-map pixels)   │
        │                 │ Stage 1 = self.margin                    │
        │                 │ Stage 2 = self.margin * 2                │
        │ tileOutExtent.w │ Width of the tile’s output region        │
        │ tileOutExtent.h │ Height of the tile’s output region       │
        └─────────────────┴──────────────────────────────────────────┘

        Parameters:
            layer:  Which array slice the tile’s input data lives on.
            spec:   TileSpec containing pre-computed output coords & extents.
            margin: Context margin in the *current stage’s* feature-map pixels.
                    For stage 1 this is `self.margin`; for stage 2 (double
                    upscale) it is `self.margin * 2` because the feature map
                    has been upscaled by 2x.
        """
        return struct.pack(
            "I" * 8,
            layer,  # inputLayer
            spec.dst_out_px_x,  # dstOffset.x
            spec.dst_out_px_y,  # dstOffset.y
            self.full_out_w,  # fullOutWidth
            self.full_out_h,  # fullOutHeight
            margin,  # margin
            spec.tile_out_extent_w,  # tileOutExtent.w
            spec.tile_out_extent_h,  # tileOutExtent.h
        )

    # ------------------------------------------------------------------
    #  Dispatch sequences
    # ------------------------------------------------------------------
    def _dispatch_single(self, specs: List[TileSpec]) -> None:
        """
        Dispatch all passes for single (2x) upscaling.

        Each tile in `specs` gets its own push constant block; all are
        submitted together in one `dispatch_sequence` call per stage.
        """
        gx, gy = self.groups_per_stage[0]
        dispatches = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin)
            for pipe in self.stages[0].pipelines:
                dispatches.append((pipe, gx, gy, 1, push))
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

    def _dispatch_double(self, specs: List[TileSpec]) -> None:
        """
        Dispatch all passes for double (4x) upscaling - two stages.

        Stage 1 (low-res -> 2x):
          - margin = self.margin
          - valid_offset_mult = 1 (feature map is still low-res)

        Stage 2 (2x -> 4x):
          - margin = self.margin * 2
          - valid_offset_mult = 2 (feature map is now 2x larger)
        """
        # ---- Stage 1 --------------------------------------------------------
        gx1, gy1 = self.groups_per_stage[0]
        dispatches_s1 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin)
            for pipe in self.stages[0].pipelines:
                dispatches_s1.append((pipe, gx1, gy1, 1, push))

        # ---- Stage 2 --------------------------------------------------------
        gx2, gy2 = self.groups_per_stage[1]
        dispatches_s2 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin * 2)
            for pipe in self.stages[1].pipelines:
                dispatches_s2.append((pipe, gx2, gy2, 1, push))

        # Submit the two stages separately to ensure proper barriers between them.
        if dispatches_s1:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches_s1)
        if dispatches_s2:
            self.stages[1].pipelines[0].dispatch_sequence(sequence=dispatches_s2)
