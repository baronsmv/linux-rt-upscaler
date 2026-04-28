import logging
import struct
from dataclasses import dataclass
from typing import List, Tuple

from ..config import Config
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_model
from ..vulkan import Buffer, Compute, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TileSpec:
    """
    Immutable geometry of one tile in the final upscaled frame.

    The crop area is divided into a grid of `tile_size` cells (low-resolution).
    Each dirty cell is expanded by a context margin, upscaled through the SRCNN
    stages, and its interior region is written directly into the full output texture.

    Attributes:
        tx, ty: Tile grid indices (0-based).
        valid_lr_offset_x, valid_lr_offset_y: Offset from the expanded tile’s top-left
            to the start of the valid interior (≤ margin). Provided by the extraction
            step; currently unused by the shader but kept for debugging.
        dst_out_px_x, dst_out_px_y: Top-left of the output rectangle (upscaled pixels).
        tile_out_extent_w, tile_out_extent_h: Output region size (may be clipped at
            the right / bottom image border).
    """

    tx: int
    ty: int
    valid_lr_offset_x: int
    valid_lr_offset_y: int
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
        # Top-left of the output rectangle (in upscaled pixels)
        dst_out_x = tx * tile_size * scale
        dst_out_y = ty * tile_size * scale

        # The tile at the right or bottom edge may be clipped
        extent_w = min(tile_size * scale, full_out_w - dst_out_x)
        extent_h = min(tile_size * scale, full_out_h - dst_out_y)

        return cls(tx, ty, valid_x, valid_y, dst_out_x, dst_out_y, extent_w, extent_h)


def _collect_intermediate_names(model_config):
    """Return a set of all UAV names used by the model, excluding 'output'."""
    return {
        name
        for srv_list, uav_list in model_config.srv_uav
        for name in uav_list
        if name != "output"
    }


class TileProcessor:
    """
    Direct tile-based upscaling (2x or 4x).

    The crop area is partitioned into a grid of `tile_size x tile_size` cells.
    When a damage rectangle overlaps a cell, the cell’s expanded region
    (`tile_size + 2xmargin`) is extracted from the full low-res frame, edge-clamped
    if it extends beyond the crop boundary, and uploaded to one slice of a 2D-array
    texture. All dirty tiles are processed in a single batch via the SRCNN compute
    pipeline; the final pass writes each tile’s 2x2 output block directly into the
    final 2D output texture.

    Two residual textures keep the "skip connection" fed:
    - `residual_1x` - the full low-res frame (updated by the caller).
    - `residual_2x` - (4x only) the full 2x upscaled frame, prepared by the caller
       using the first SRCNN stage.

    Attributes:
        output_texture (Texture2D): The final upscaled image (plain 2D, used by Lanczos).
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
        model_variant: str = "_tile",
        push_constant_size: int = 32,  # 8 uint32 fields (see _make_push_bytes)
    ) -> None:
        # --- Validation ----------------------------------------------------------
        if crop_width <= 0 or crop_height <= 0:
            raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")
        if config.tile_size <= 0 or config.max_tile_layers <= 0:
            raise ValueError("Invalid tile_size or max_layers")

        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.margin = config.tile_context_margin
        self.tile_size = config.tile_size
        self.double_upscale = config.double_upscale
        self.max_layers = config.max_tile_layers

        # --------------------------------------------------------------------------
        # Derived sizes
        # --------------------------------------------------------------------------
        self.expanded_tile_size = self.tile_size + 2 * self.margin
        self.scale = 4 if self.double_upscale else 2
        self.full_out_w = crop_width * self.scale
        self.full_out_h = crop_height * self.scale

        # --------------------------------------------------------------------------
        # Model & pipeline factory
        # --------------------------------------------------------------------------
        model_config = load_model(
            config.model, variant=model_variant, push_constant_size=push_constant_size
        )
        self.model_config = model_config
        self.intermediate_format = model_config.intermediate_format
        self.push_constant_size = push_constant_size
        self.factory = PipelineFactory(model_config)

        # All UAV names used by the model (except "output")
        self.intermediate_names = _collect_intermediate_names(model_config)

        # --------------------------------------------------------------------------
        # Residual textures (updated by UpscalerManager before tile processing)
        # --------------------------------------------------------------------------
        self.residual_1x = Texture2D(
            crop_width, crop_height, slices=1, force_array_view=True
        )
        self.residual_2x = (
            Texture2D(crop_width * 2, crop_height * 2, force_array_view=True)
            if self.double_upscale
            else None
        )
        # Persistent staging buffer for residual uploads (reused every frame)
        self.residual_staging = Buffer(
            crop_width * crop_height * 4, heap_type=HEAP_UPLOAD
        )

        # --------------------------------------------------------------------------
        # SRCNN stages and dispatch groups
        # --------------------------------------------------------------------------
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []
        self._create_stages()

        # --------------------------------------------------------------------------
        # Final pipeline (replaces the last pass’s built-in pipeline)
        # --------------------------------------------------------------------------
        self._finalize_pipeline()

        logger.info(
            "TileProcessor ready: crop=%dx%d, tile=%d, margin=%d, scale=%dx, layers=%d",
            crop_width,
            crop_height,
            self.tile_size,
            self.margin,
            self.scale,
            self.max_layers,
        )

    # ======================================================================
    #  Internal factory helpers
    # ======================================================================

    def _make_array_tex(self, width: int, height: int, slices: int) -> Texture2D:
        """Return a 2D‑array texture with the model’s intermediate format."""
        return Texture2D(
            width,
            height,
            slices=slices,
            format=self.intermediate_format,
            force_array_view=True,
        )

    # ======================================================================
    #  Stage creation
    # ======================================================================
    def _create_stages(self) -> None:
        """Create the SRCNN stages (one for 2x, two for 4x) using array textures."""
        lr = self.expanded_tile_size  # low-res feature map size
        half = lr * 2  # after first 2x upscale
        full = lr * 4  # after second 2x upscale (4x total)

        # Input array texture - one slice per concurrent tile
        input_tex = self._make_array_tex(lr, lr, self.max_layers)

        # ---- Stage 1: low-res to 2x --------------------------------------------
        stage1_textures = {
            name: self._make_array_tex(lr, lr, self.max_layers)
            for name in self.intermediate_names
        }
        inter_tex = self._make_array_tex(half, half, self.max_layers)
        stage1_textures["output"] = inter_tex

        srnn1 = SRCNN(
            factory=self.factory,
            width=lr,
            height=lr,
            input_texture=input_tex,
            output_textures=stage1_textures,
            push_constant_size=self.push_constant_size,
        )
        self.stages.append(srnn1)
        self.groups_per_stage.append(dispatch_groups(lr, lr, last_pass=False))

        if self.double_upscale:
            # Stage 2: 2x to 4x
            stage2_textures = {
                name: self._make_array_tex(half, half, self.max_layers)
                for name in self.intermediate_names
            }
            final_out_array = self._make_array_tex(full, full, self.max_layers)
            stage2_textures["output"] = final_out_array

            srnn2 = SRCNN(
                factory=self.factory,
                width=half,
                height=half,
                input_texture=inter_tex,
                output_textures=stage2_textures,
                push_constant_size=self.push_constant_size,
            )
            self.stages.append(srnn2)
            self.groups_per_stage.append(dispatch_groups(half, half, last_pass=False))
        else:
            # Single stage: reuse the same array layout
            stage1_textures["output"] = self._make_array_tex(
                half, half, self.max_layers
            )
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=lr,
                height=lr,
                input_texture=input_tex,
                output_textures=stage1_textures,
                push_constant_size=self.push_constant_size,
            )
            self.groups_per_stage[0] = dispatch_groups(lr, lr, last_pass=False)

        # Final output - plain 2D texture required by Lanczos scaler
        self.output_texture = Texture2D(self.full_out_w, self.full_out_h)

    # ======================================================================
    #  Custom final pipeline (replaces the built-in last pass)
    # ======================================================================
    def _finalize_pipeline(self) -> None:
        """
        Build a pipeline that replaces the last pass’s built-in pipeline.

        The built-in last pass would write to the array texture `final_out_array`.
        Here we create a *custom* Compute pipeline that writes directly into
        `self.output_texture` (a plain 2D image). The constant buffer
        is populated with:
          - in_width / in_height: feature-map size for the last stage
            (expanded_tile_size x scale).
          - out_width / out_height: full upscaled frame size.
          - in_dx / in_dy: 1 / (feature-map size).
          - out_dx / out_dy: 1 / (full upscaled size).
        These match the `Constants` cbuffer in `Pass4_tile.hlsl`.
        """
        final_pass_idx = self.model_config.passes - 1
        final_shader = self.model_config.shaders[final_pass_idx]

        last_stage = self.stages[-1] if self.double_upscale else self.stages[0]
        last_stage_outputs = last_stage.outputs

        # Feature-map size for the last pass (e.g. expanded_tile_size * scale)
        feat_size = self.expanded_tile_size * (2 if self.double_upscale else 1)

        # Constant buffer (in_width, in_height, out_width, out_height, recip.)
        cb_data = struct.pack(
            "IIIIffff",
            feat_size,  # in_width
            feat_size,  # in_height
            self.full_out_w,  # out_width
            self.full_out_h,  # out_height
            1.0 / feat_size,  # in_dx
            1.0 / feat_size,  # in_dy
            1.0 / self.full_out_w,  # out_dx
            1.0 / self.full_out_h,  # out_dy
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        # Residual texture (input for the last pass)
        residual = self.residual_2x if self.double_upscale else self.residual_1x

        # SRV list - respect the order defined in model.json
        final_srvs_spec, _ = self.model_config.srv_uav[final_pass_idx]
        srv_list = []
        for name in final_srvs_spec:
            if name == "input":
                srv_list.append(residual)
            else:
                if name not in last_stage_outputs:
                    raise KeyError(f"Feature map '{name}' not in stage outputs")
                srv_list.append(last_stage_outputs[name])

        # UAV list – plain 2D output
        uav_list = [self.output_texture]

        # Samplers for the final pass
        sampler_list = [
            self.factory.get_sampler(t)
            for t in self.model_config.samplers[final_pass_idx]
        ]

        final_pipe = Compute(
            final_shader,
            cbv=[final_cb],
            srv=srv_list,
            uav=uav_list,
            samplers=sampler_list,
            push_size=self.push_constant_size,
        )

        # Replace the last pipeline in the appropriate stage
        last_stage.pipelines[-1] = final_pipe

    # ======================================================================
    #  Tile processing (CPU extraction + upload)
    # ======================================================================
    def process_tiles(
        self,
        dirty_tiles: List[Tuple[int, int, bytes, int, int]],
    ) -> None:
        """
        Process a batch of dirty tiles.

        All tiles are uploaded to consecutive slices of the input array texture
        and then processed by the SRCNN stages in one dispatch sequence.

        Args:
            dirty_tiles: List of (tx, ty, pixel_data, valid_x, valid_y).
                         The pixel data *must* already be expanded and edge-clamped.
        """
        if not dirty_tiles:
            return

        batch = dirty_tiles[: self.max_layers]
        spec_list = []
        upload_list = []
        tile_bytes = self.expanded_tile_size * self.expanded_tile_size * 4

        for layer, (tx, ty, data, vx, vy) in enumerate(batch):
            # Build tile geometry
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
            spec_list.append(spec)

            # Sanitize pixel data length (pad / truncate if necessary)
            safe_data = data
            if len(data) != tile_bytes:
                safe_data = data.ljust(tile_bytes, b"\x00")[:tile_bytes]

            upload_list.append(
                (
                    safe_data,
                    0,
                    0,
                    self.expanded_tile_size,
                    self.expanded_tile_size,
                    layer,
                )
            )

        # Upload all tiles to the array texture (one slice each)
        if upload_list:
            self.stages[0].input.upload_subresources(upload_list)

        # Dispatch the compute stages
        if self.double_upscale:
            self._dispatch_double(spec_list)
        else:
            self._dispatch_single(spec_list)

    # ======================================================================
    #  Push constant helpers
    # ======================================================================
    def _make_push_bytes(self, layer: int, spec: TileSpec, margin: int) -> bytes:
        """
        Serialise the `TileParams` push-constant block (8 uint32 fields).

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
            layer,
            spec.dst_out_px_x,
            spec.dst_out_px_y,
            self.full_out_w,
            self.full_out_h,
            margin,
            spec.tile_out_extent_w,
            spec.tile_out_extent_h,
        )

    # ======================================================================
    #  Dispatch sequences
    # ======================================================================
    def _dispatch_single(self, specs: List[TileSpec]) -> None:
        """2x upscale: one stage, all tiles in a single `dispatch_sequence`."""
        gx, gy = self.groups_per_stage[0]
        dispatches = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin)
            for pipe in self.stages[0].pipelines:
                dispatches.append((pipe, gx, gy, 1, push))
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

    def _dispatch_double(self, specs: List[TileSpec]) -> None:
        """4x upscale: two stages submitted separately to ensure barriers."""
        # Stage 1
        gx1, gy1 = self.groups_per_stage[0]
        s1 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin)
            for pipe in self.stages[0].pipelines:
                s1.append((pipe, gx1, gy1, 1, push))
        if s1:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=s1)

        # Stage 2
        gx2, gy2 = self.groups_per_stage[1]
        s2 = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, self.margin * 2)
            for pipe in self.stages[1].pipelines:
                s2.append((pipe, gx2, gy2, 1, push))
        if s2:
            self.stages[1].pipelines[0].dispatch_sequence(sequence=s2)
