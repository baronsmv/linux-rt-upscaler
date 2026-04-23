import logging
import struct
from typing import List, Tuple

import xxhash

from .atlas import TileAtlasManager
from .tile import TileProcessor
from ..vulkan import Texture2D, Buffer, Compute

logger = logging.getLogger(__name__)


class CachedTileProcessor(TileProcessor):
    """
    Tile processing with an LRU cache.

    Inherits all the expanded-tile processing logic from `DirectTileProcessor`,
    but writes the final output to an atlas (array texture) instead of directly
    to the full output texture. A cache manager (`TileAtlasManager`) tracks
    which tiles are already present in the atlas.

    On each frame:
        - For cache hits: skip all CNN passes and simply copy the atlas layer
          to the output texture.
        - For cache misses: process the tile as usual (using the superclass
          logic), which writes to an atlas layer; then copy to output.

    This dramatically reduces GPU work for static or slowly changing content.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        cache_capacity: int,
        cache_threshold: float,
        tile_context_margin: int = 0,
    ) -> None:
        """
        Initialize the cached tile processor.

        Args:
            crop_width, crop_height: Dimensions of the captured crop area.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling.
            tile_size: Nominal input tile size.
            cache_capacity: Maximum number of tiles stored in the cache.
            cache_threshold: Fraction of total tiles above which full-frame is used.
            tile_context_margin: Extra border pixels for convolution context.
        """
        # Cache capacity determines the number of atlas layers.
        super().__init__(
            crop_width=crop_width,
            crop_height=crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
            tile_size=tile_size,
            tile_context_margin=tile_context_margin,
            max_layers=cache_capacity,
        )

        self.cache_capacity = cache_capacity
        self.cache_threshold = cache_threshold

        self.atlas_manager = TileAtlasManager(
            capacity=cache_capacity,
            tile_width=self.tile_out_w_final,
            tile_height=self.tile_out_h_final,
        )

        # Override the final output to be an atlas instead of a 2D texture.
        self._convert_output_to_atlas()

    def _convert_output_to_atlas(self) -> None:
        """
        Replace the final output texture (2D) with an array texture (atlas)
        of `cache_capacity` slices. Also patch the final pipeline's UAV
        to bind the atlas instead.
        """
        # Create the output atlas.
        self.output_atlas = Texture2D(
            self.tile_out_w_final,
            self.tile_out_h_final,
            slices=self.cache_capacity,
            force_array_view=True,
        )

        # Recreate the final pipeline with the atlas as the UAV.
        final_pass_index = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_index]

        scale = 4 if self.double_upscale else 2
        full_out_w = self.crop_width * scale
        full_out_h = self.crop_height * scale
        cb_data = struct.pack(
            "IIIIffff",
            self.expanded_tile_size,
            self.expanded_tile_size,
            full_out_w,
            full_out_h,
            1.0 / self.expanded_tile_size,
            1.0 / self.expanded_tile_size,
            1.0 / full_out_w,
            1.0 / full_out_h,
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        srv_list = [self.full_input_tex]
        pre_final_stage = self.stages[-2] if self.double_upscale else self.stages[0]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final_stage.outputs[f"t{i}"])

        # UAV is now the output atlas.
        uav_list = [self.output_atlas]

        sampler_list = [
            self.factory._get_sampler(t)
            for t in self.factory.config.samplers[final_pass_index]
        ]

        self.final_pipeline = Compute(
            final_shader,
            cbv=[final_cb],
            srv=srv_list,
            uav=uav_list,
            samplers=sampler_list,
            push_size=self.factory.config.push_constant_size,
        )

        # Replace the original final pass pipeline.
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = self.final_pipeline
        else:
            self.stages[0].pipelines[-1] = self.final_pipeline

    def total_tiles(self) -> int:
        """Total number of tile grid cells in the crop area."""
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty: int) -> bool:
        """Return True if the number of dirty tiles is below the threshold."""
        threshold = int(self.total_tiles() * self.cache_threshold)
        return num_dirty <= threshold

    # ----------------------------------------------------------------------
    #  Override tile extraction to include content hash for cache key
    # ----------------------------------------------------------------------
    @staticmethod
    def extract_dirty_tiles_with_hash(
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        tile_size: int,
        margin: int,
    ) -> List[Tuple[int, int, int, bytes]]:
        """
        Extract expanded tiles and compute their content hash.

        This method reuses the base class `extract_expanded_tiles` to perform
        the heavy lifting of edge clamping and data extraction, then computes
        an xxHash64 over the interior region (excluding margin) for cache keys.

        Returns:
            List of (tile_x, tile_y, hash, data_bytes).
        """
        # Expanded tiles using the base class method
        expanded_tiles = TileProcessor.extract_expanded_tiles(
            frame=frame,
            rects=rects,
            crop_width=crop_width,
            crop_height=crop_height,
            tile_size=tile_size,
            margin=margin,
        )

        result = []
        expanded_size = tile_size + 2 * margin
        for tx, ty, data, valid_x, valid_y in expanded_tiles:
            # The interior region starts at (valid_x, valid_y) within the expanded tile
            interior_start = (valid_y * expanded_size + valid_x) * 4
            interior_data = data[
                interior_start : interior_start + tile_size * tile_size * 4
            ]
            tile_hash = xxhash.xxh64(interior_data).intdigest()
            result.append((tx, ty, tile_hash, data))

        return result

    # ----------------------------------------------------------------------
    #  Main tile processing with caching
    # ----------------------------------------------------------------------
    def process_tiles(self, dirty_tiles: List[Tuple[int, int, int, bytes]]) -> None:
        """
        Process dirty tiles using the LRU cache.

        Args:
            dirty_tiles: List of (tile_x, tile_y, hash, data_bytes) as returned
                by `extract_dirty_tiles_with_hash`.
        """
        if not dirty_tiles:
            return

        misses = []
        hits = []

        # Separate hits and misses
        for tx, ty, tile_hash, data in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, tile_hash)
            if was_cached:
                hits.append((tx, ty, layer))
            else:
                misses.append((tx, ty, layer, data))

        # Process cache misses using the superclass logic
        miss_tiles_for_super = [
            (tx, ty, data, self.margin, self.margin) for tx, ty, layer, data in misses
        ]
        if miss_tiles_for_super:
            # Temporarily adjust max_layers to process all misses in one batch
            original_max = self.max_layers
            self.max_layers = len(miss_tiles_for_super)
            super().process_tiles(miss_tiles_for_super)
            self.max_layers = original_max

        # Copy all tiles (hits + misses) from the output atlas to the final texture
        all_tiles = hits + [(tx, ty, layer) for tx, ty, layer, _ in misses]
        scale = 4 if self.double_upscale else 2
        for tx, ty, layer in all_tiles:
            dst_x = tx * self.tile_size * scale
            dst_y = ty * self.tile_size * scale
            copy_w = min(self.tile_out_w_final, self.output_texture.width - dst_x)
            copy_h = min(self.tile_out_h_final, self.output_texture.height - dst_y)
            if copy_w > 0 and copy_h > 0:
                self.output_atlas.copy_to(
                    self.output_texture,
                    src_slice=layer,
                    dst_x=dst_x,
                    dst_y=dst_y,
                    width=copy_w,
                    height=copy_h,
                )
