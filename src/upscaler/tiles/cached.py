import logging
import struct
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

from .tile import TileProcessor, TileSpec
from ..vulkan import Buffer, Compute, Texture2D

logger = logging.getLogger(__name__)


class CachedTileProcessor(TileProcessor):
    """
    Cache‑based tile processor with an atlas of already upscaled tiles.

    Extends the direct tile processor to avoid reprocessing tiles whose
    content has not changed. Each tile is stored in an atlas layer; on
    subsequent frames the tile is simply recomposited from the atlas
    rather than reprocessed from scratch.

    - atlas : 2D‑array texture holding the upscaled interior of each tile
              (size = tile_size * scale, max_layers slices).
    - cache : OrderedDict mapping (tx, ty) → atlas_layer (LRU eviction).

    A composition pass copies the relevant atlas layers into the full
    output texture.
    """

    def __init__(self, config, crop_width: int, crop_height: int) -> None:
        # Compute scale and tile size early (they are set in base __init__
        # but we need them to create the atlas before super().__init__() is called).
        self.scale = 4 if config.double_upscale else 2
        self.tile_size = config.tile_size
        self.margin = config.tile_context_margin

        # Build the output atlas – each layer holds one upscaled tile interior
        self.atlas_tile_size = self.tile_size * self.scale
        self.atlas = Texture2D(
            self.atlas_tile_size,
            self.atlas_tile_size,
            slices=config.max_tile_layers,
            force_array_view=True,
        )

        self.cache: Dict[Tuple[int, int], int] = OrderedDict()
        self.compose_pipeline: Optional[Compute] = None

        # Now let the base class initialise everything (and call _finalize_pipeline,
        # which will now find self.atlas already created).
        super().__init__(
            config,
            crop_width,
            crop_height,
            model_variant="_cache",
            push_constant_size=40,
        )

        # After base init, the full output_texture exists – create the composition pipeline.
        self._create_compose_pipeline()

    # ------------------------------------------------------------------
    #  Override – custom final pipeline writes to atlas
    # ------------------------------------------------------------------
    def _finalize_pipeline(self) -> None:
        """Custom final pass that writes the upscaled interior into self.atlas."""
        final_pass_idx = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_idx]

        if self.double_upscale:
            feat_lr = self.expanded_tile_size * 2
        else:
            feat_lr = self.expanded_tile_size

        cb_data = struct.pack(
            "IIIIffff",
            feat_lr,
            feat_lr,
            self.full_out_w,
            self.full_out_h,
            1.0 / feat_lr,
            1.0 / feat_lr,
            1.0 / self.full_out_w,
            1.0 / self.full_out_h,
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        pre_final = self.stages[-1] if self.double_upscale else self.stages[0]
        srv_list = [self.residual_tex]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final.outputs[f"t{i}"])

        # Write into the atlas, not the full output texture
        uav_list = [self.atlas]
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
            push_size=44,
        )

        if self.double_upscale:
            self.stages[-1].pipelines[-1] = final_pipe
        else:
            self.stages[0].pipelines[-1] = final_pipe

    # ------------------------------------------------------------------
    #  Push constants for an atlas output layer
    # ------------------------------------------------------------------
    def _make_push_bytes_for_layer(
        self, layer: int, spec: TileSpec, atlas_layer: int
    ) -> bytes:
        """Build push constant block where inputLayer = tile index,
        outputLayer = atlas layer to write to."""
        return struct.pack(
            "I" * 10,
            layer,  # inputLayer – used for sampling the tile's data
            spec.dst_out_px_x,
            spec.dst_out_px_y,
            self.full_out_w,
            self.full_out_h,
            spec.valid_lr_offset_x,
            spec.valid_lr_offset_y,
            spec.tile_out_extent_w,
            spec.tile_out_extent_h,
            atlas_layer,  # outputLayer – write to this atlas slice
        )

    # ------------------------------------------------------------------
    #  Override – hash‑driven tile processing
    # ------------------------------------------------------------------
    def process_tiles(
        self, dirty_tiles: List[Tuple[int, int, int, bytes, int, int]]
    ) -> None:
        """
        Process tiles with caching.

        Args:
            dirty_tiles: List of (tx, ty, hash, data, valid_x, valid_y)
        """
        if not dirty_tiles:
            return

        num_tiles = len(dirty_tiles)
        expected_data = self.expanded_tile_size * self.expanded_tile_size * 4
        total_staging = num_tiles * expected_data
        self._ensure_staging(total_staging)

        # Assign atlas layers – reuse cached layer if hash still matches,
        # otherwise evict LRU and allocate a new layer.
        layer_assignments: Dict[int, int] = {}  # tile_index → atlas_layer
        for i, (tx, ty, h, data, vx, vy) in enumerate(dirty_tiles):
            key = (tx, ty)
            if key in self.cache:
                cached_layer = self.cache.pop(key)
                self.cache[key] = cached_layer
                layer_assignments[i] = cached_layer
            else:
                if len(self.cache) >= self.max_layers:
                    evicted_key = next(iter(self.cache))
                    del self.cache[evicted_key]
                # Use the tile index as the atlas layer (safe because batch≤max_layers)
                layer = i
                self.cache[key] = layer
                layer_assignments[i] = layer

        # Upload expanded pixel data to input array (layer = tile index)
        uploads = []
        for i, (tx, ty, h, data, vx, vy) in enumerate(dirty_tiles):
            data = self._sanitize_data(data, expected_data)
            uploads.append(
                (data, 0, 0, self.expanded_tile_size, self.expanded_tile_size, i)
            )
        self.stages[0].input.upload_subresources(uploads)

        # Build TileSpec objects for the interior
        specs = [
            TileSpec.from_raw(
                tx,
                ty,
                vx,
                vy,
                self.tile_size,
                self.scale,
                self.full_out_w,
                self.full_out_h,
            )
            for (tx, ty, h, data, vx, vy) in dirty_tiles
        ]

        # Dispatch stages, writing into the atlas layers
        if self.double_upscale:
            self._dispatch_double_with_atlas(specs, layer_assignments)
        else:
            self._dispatch_single_with_atlas(specs, layer_assignments)

        # Composite the updated atlas layers into the full output texture
        self._compose_atlas(layer_assignments, specs)

    # ------------------------------------------------------------------
    #  Dispatch helpers for atlas output
    # ------------------------------------------------------------------
    def _dispatch_single_with_atlas(
        self, specs: List[TileSpec], layer_assignments: Dict[int, int]
    ) -> None:
        gx, gy = self.groups_per_stage[0]
        dispatches = []
        for i, spec in enumerate(specs):
            atlas_layer = layer_assignments[i]
            push = self._make_push_bytes_for_layer(i, spec, atlas_layer)
            for pipe in self.stages[0].pipelines:
                dispatches.append((pipe, gx, gy, 1, push))
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

    def _dispatch_double_with_atlas(
        self, specs: List[TileSpec], layer_assignments: Dict[int, int]
    ) -> None:
        # Stage 1 (lr → 2×)
        gx1, gy1 = self.groups_per_stage[0]
        dispatches_s1 = []
        for i in range(len(specs)):
            for pipe in self.stages[0].pipelines:
                dispatches_s1.append((pipe, gx1, gy1, 1, b""))
        if dispatches_s1:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches_s1)

        # Stage 2 (2× → 4×)
        gx2, gy2 = self.groups_per_stage[1]
        dispatches_s2 = []
        for i, spec in enumerate(specs):
            atlas_layer = layer_assignments[i]
            push = self._make_push_bytes_for_layer(i, spec, atlas_layer)
            for pipe in self.stages[1].pipelines:
                dispatches_s2.append((pipe, gx2, gy2, 1, push))
        if dispatches_s2:
            self.stages[1].pipelines[0].dispatch_sequence(sequence=dispatches_s2)

    # ------------------------------------------------------------------
    #  Atlas composition (layer → output texture)
    # ------------------------------------------------------------------
    def _create_compose_pipeline(self) -> None:
        """
        Create a tiny compute shader that copies the interior of an atlas
        layer to the full output texture. If performance becomes an issue,
        this could be replaced by a dedicated shader; for now we use the
        existing copy_to method directly in _compose_atlas.
        """
        # The implementation below does NOT use a compute pipeline;
        # instead _compose_atlas calls Texture2D.copy_to directly.
        # This placeholder is kept for clarity and possible future extensions.
        pass

    def _compose_atlas(
        self, layer_assignments: Dict[int, int], specs: List[TileSpec]
    ) -> None:
        """Composite updated atlas layers into the output texture."""
        for i, spec in enumerate(specs):
            if i in layer_assignments:
                layer = layer_assignments[i]
                # The interior of the atlas tile starts at (0,0) – the custom
                # final shader writes the interior there (thanks to validOffset).
                self.atlas.copy_to(
                    self.output_texture,
                    width=spec.tile_out_extent_w,
                    height=spec.tile_out_extent_h,
                    src_x=0,
                    src_y=0,
                    dst_x=spec.dst_out_px_x,
                    dst_y=spec.dst_out_px_y,
                    src_slice=layer,
                    dst_slice=0,
                )
