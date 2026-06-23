from __future__ import annotations

import logging
import struct
from dataclasses import dataclass
from typing import List, Optional, Tuple, TYPE_CHECKING

from ..config import Config
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_model
from ..vulkan import Buffer, Compute, Texture2D

if TYPE_CHECKING:
    from .utils import DirtyTiles, DirtyTilesCoords, DirtyTilesRects

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
        dst_out_px_x, dst_out_px_y: Top-left of the output rectangle (upscaled pixels).
        tile_out_extent_w, tile_out_extent_h: Output region size (may be clipped at
            the right / bottom image border).
    """

    tx: int
    ty: int
    dst_out_px_x: int
    dst_out_px_y: int
    tile_out_extent_w: int
    tile_out_extent_h: int

    @classmethod
    def from_raw(
        cls,
        tx: int,
        ty: int,
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

        return cls(tx, ty, dst_out_x, dst_out_y, extent_w, extent_h)


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

    - Single upscaling mode: a single tiled SRCNN stage operates on low-res patches.
    - Double upscaling mode: the first SRCNN stage runs full-frame, while the second
      is tiled.
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
        residual_1x_texture: Optional[Texture2D] = None,
        residual_2x_texture: Optional[Texture2D] = None,
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

        # -------------------------------------------------------------------
        # Derived sizes
        # -------------------------------------------------------------------
        self.expanded_tile_size = self.tile_size + 2 * self.margin
        self.scale = 4 if self.double_upscale else 2
        self.full_out_w = crop_width * self.scale
        self.full_out_h = crop_height * self.scale

        # -------------------------------------------------------------------
        # Model & pipeline factory
        # -------------------------------------------------------------------
        model_config = load_model(
            config.model, variant=model_variant, push_constant_size=push_constant_size
        )
        self.model_config = model_config
        self.intermediate_format = model_config.intermediate_format
        self.push_constant_size = push_constant_size
        self.factory = PipelineFactory(model_config)

        # All UAV names used by the model (except "output")
        self.intermediate_names = _collect_intermediate_names(model_config)

        # ------------------------------------------------------------------
        # Residual textures
        # ------------------------------------------------------------------
        self.residual_1x = residual_1x_texture or Texture2D(crop_width, crop_height)
        if self.double_upscale:
            self.residual_2x = residual_2x_texture or Texture2D(
                crop_width * 2, crop_height * 2, format=self.intermediate_format
            )
        else:
            self.residual_2x = None

        # -------------------------------------------------------------------
        # SRCNN stages and dispatch groups
        # -------------------------------------------------------------------
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []
        self._create_stages()

        # ------------------------------------------------------------------
        # Final pipeline override
        # ------------------------------------------------------------------
        self._finalize_pipeline()

        logger.debug(
            "TileProcessor ready: crop=%dx%d, tile=%d, margin=%d, "
            "scale=%dx, layers=%d",
            crop_width,
            crop_height,
            self.tile_size,
            self.margin,
            self.scale,
            self.max_layers,
        )

    @property
    def _shader_margin(self) -> int:
        """Feature‑map margin used by the shader (doubled for 4×)."""
        return self.margin * (2 if self.double_upscale else 1)

    # ======================================================================
    #  Internal factory helpers
    # ======================================================================

    def _make_array_tex(self, width: int, height: int, slices: int) -> Texture2D:
        """Return a 2D-array texture with the model’s intermediate format."""
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
        """Create the tiled SRCNN stages."""
        lr = self.expanded_tile_size  # low-res expanded tile size
        half = lr * 2  # 2x expanded tile size

        if self.double_upscale:
            # --- Double upscaling (4x): only the second stage is tiled ---
            feat_2x = self.expanded_tile_size * 2  # feature-map size for second stage
            self.stage_input = self._make_array_tex(feat_2x, feat_2x, self.max_layers)

            stage_outs = {
                name: self._make_array_tex(feat_2x, feat_2x, self.max_layers)
                for name in self.intermediate_names
            }
            # Dummy output array, the final pass is overridden to write to output_texture
            stage_outs["output"] = self._make_array_tex(
                feat_2x * 2, feat_2x * 2, self.max_layers
            )

            srcnn = SRCNN(
                factory=self.factory,
                width=feat_2x,
                height=feat_2x,
                input_texture=self.stage_input,
                output_textures=stage_outs,
                push_constant_size=self.push_constant_size,
            )
            self.stages.append(srcnn)
            self.groups_per_stage.append(
                dispatch_groups(feat_2x, feat_2x, last_pass=False)
            )
        else:
            # --- Single upscaling (2x): single tiled stage ----
            input_tex = Texture2D(lr, lr, slices=self.max_layers, force_array_view=True)
            stage_outs = {
                name: self._make_array_tex(lr, lr, self.max_layers)
                for name in self.intermediate_names
            }
            stage_outs["output"] = self._make_array_tex(half, half, self.max_layers)

            srcnn = SRCNN(
                factory=self.factory,
                width=lr,
                height=lr,
                input_texture=input_tex,
                output_textures=stage_outs,
                push_constant_size=self.push_constant_size,
            )
            self.stages.append(srcnn)
            self.groups_per_stage.append(dispatch_groups(lr, lr, last_pass=False))

        # Final output, plain 2D texture for the overlay
        self.output_texture = Texture2D(self.full_out_w, self.full_out_h)

    # ======================================================================
    #  Custom final pipeline (replaces the built-in last pass)
    # ======================================================================
    def _finalize_pipeline(self) -> None:
        """Override the last pass to write into `output_texture`."""
        final_pass_idx = self.model_config.passes - 1
        final_shader = self.model_config.shaders[final_pass_idx]

        stage = self.stages[0]
        stage_outs = stage.outputs

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
        cb = Buffer(len(cb_data))
        cb.upload(cb_data)

        # Residual: 2x intermediate for 4x, 1x frame for 2x
        residual = self.residual_2x if self.double_upscale else self.residual_1x

        # Build the replacement pipeline
        final_srvs_spec, _ = self.model_config.srv_uav[final_pass_idx]
        srv_list = []
        for name in final_srvs_spec:
            if name == "input":
                srv_list.append(residual)
            else:
                srv_list.append(stage_outs[name])

        # Samplers for the final pass
        sampler_list = [
            self.factory.get_sampler(t)
            for t in self.model_config.samplers[final_pass_idx]
        ]

        new_pipe = Compute(
            final_shader,
            cbv=[cb],
            srv=srv_list,
            uav=[self.output_texture],
            samplers=sampler_list,
            push_size=self.push_constant_size,
        )
        stage.pipelines[-1] = new_pipe

    # ======================================================================
    #  Tile processing (CPU extraction + upload)
    # ======================================================================
    def process_tiles(self, dirty_tiles: DirtyTiles) -> bool:
        """
        Process a batch of dirty tiles.

        `dirty_tiles` is a list of (tx, ty, pixel_data, valid_x, valid_y)
        as returned by `extract_expanded_tiles`. For 4x upscaling, the
        `pixel_data` field is ignored, the 2x patches are copied directly
        from `residual_2x` via GPU image copies.
        """
        if not dirty_tiles:
            return True

        batch = dirty_tiles[: self.max_layers]

        if self.double_upscale:
            return self._process_4x(batch)
        else:
            self._process_2x(batch)
            return True

    def _process_4x(self, batch: DirtyTilesCoords) -> bool:
        """4x tile processing: copy 2x patches, then dispatch the second stage."""
        # Copy the required 2x regions from residual_2x into the input array
        regions = []
        for layer, (tx, ty) in enumerate(batch):
            if (
                tx * self.tile_size - self.margin < 0
                or ty * self.tile_size - self.margin < 0
                or (tx + 1) * self.tile_size + self.margin > self.crop_width
                or (ty + 1) * self.tile_size + self.margin > self.crop_height
            ):
                # Edge tile, would need clamping: skip tile mode for this frame
                return False

            exp_x0 = max(0, tx * self.tile_size - self.margin)
            exp_y0 = max(0, ty * self.tile_size - self.margin)
            exp_x1 = min(self.crop_width, (tx + 1) * self.tile_size + self.margin)
            exp_y1 = min(self.crop_height, (ty + 1) * self.tile_size + self.margin)

            # 2x region in residual_2x
            src_x = exp_x0 * 2
            src_y = exp_y0 * 2
            src_w = (exp_x1 - exp_x0) * 2
            src_h = (exp_y1 - exp_y0) * 2
            regions.append((src_x, src_y, layer, src_w, src_h))

        if regions:
            self.residual_2x.batch_copy_to_array(self.stage_input, regions)

        # Build output specs and dispatch
        specs = []
        for layer, (tx, ty) in enumerate(batch):
            spec = TileSpec.from_raw(
                tx,
                ty,
                self.tile_size,
                scale=4,
                full_out_w=self.full_out_w,
                full_out_h=self.full_out_h,
            )
            specs.append(spec)

        self._dispatch(specs, margin=self._shader_margin)
        return True

    def _process_2x(self, batch: DirtyTilesRects) -> None:
        """2x tile processing: upload low-res patches and dispatch."""
        specs = []
        upload_list = []
        tile_bytes = self.expanded_tile_size * self.expanded_tile_size * 4

        for layer, (tx, ty, data, _vx, _vy) in enumerate(batch):  # vx,vy ignored
            spec = TileSpec.from_raw(
                tx,
                ty,
                self.tile_size,
                scale=2,
                full_out_w=self.full_out_w,
                full_out_h=self.full_out_h,
            )
            specs.append(spec)

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

        if upload_list:
            self.stages[0].input.upload_subresources(upload_list)

        self._dispatch(specs, margin=self.margin)

    # ======================================================================
    #  Push constant helpers
    # ======================================================================
    def _make_push_bytes(self, layer: int, spec: TileSpec, margin: int) -> bytes:
        """
        Serialize the `TileParams` push-constant block (8 uint32 fields).

        ┌─────────────────┬──────────────────────────────────────────┐
        │ Field           │ Description                              │
        ├─────────────────┼──────────────────────────────────────────┤
        │ dstOffset.x     │ Top-left X of the output rectangle       │
        │ dstOffset.y     │ Top-left Y of the output rectangle       │
        │ tileOutExtent.w │ Width of the tile’s output region        │
        │ tileOutExtent.h │ Height of the tile’s output region       │
        │ fullOut.w       │ Width of the final upscaled frame        │
        │ fullOut.h       │ Height of the final upscaled frame       │
        │ inputLayer      │ Array slice of the tile input data       │
        │ margin          │ Context margin (in feature-map pixels)   │
        │                 │ Stage 1 = self.margin                    │
        │                 │ Stage 2 = self.margin * 2                │
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
            spec.dst_out_px_x,
            spec.dst_out_px_y,
            spec.tile_out_extent_w,
            spec.tile_out_extent_h,
            self.full_out_w,
            self.full_out_h,
            layer,
            margin,
        )

    # ======================================================================
    #  Dispatch sequences
    # ======================================================================
    def _dispatch(self, specs: List[TileSpec], margin: int) -> None:
        """Execute all tiles in a single command buffer."""
        gx, gy = self.groups_per_stage[0]

        dispatches = []
        for i, spec in enumerate(specs):
            push = self._make_push_bytes(i, spec, margin)
            for pipe in self.stages[0].pipelines:
                dispatches.append((pipe, gx, gy, 1, push))

        self.stages[0].pipelines[0].dispatch_sequence(
            sequence=dispatches, output_texture=self.output_texture
        )
