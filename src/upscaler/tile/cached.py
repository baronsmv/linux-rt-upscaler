import logging
from typing import List, Tuple

import xxhash

from .atlas import TileAtlasManager
from .tile import TileProcessor
from .utils import extract_expanded_tiles
from ..config import Config
from ..vulkan import Texture2D

logger = logging.getLogger(__name__)


class CachedTileProcessor(TileProcessor):
    """
    Tile processor with an LRU cache for tile outputs.

    Inherits the whole tile-processing pipeline (stage creation, dispatch,
    residual upload) from `TileProcessor`. All CNN passes write directly to
    the full output texture - exactly like direct mode. A separate **cache
    atlas** stores a copy of each processed tile. On subsequent frames:
      - Hits:   the tile is copied from the atlas back to the output texture
                (no CNN pass needed).
      - Misses: the tile is processed normally (via the base class), then a
                copy of the upscaled result is stored in the atlas for future
                reuse.

    The atlas is sized to `cache_capacity` slices; an LRU eviction policy
    keeps the most frequently used tiles.
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
    ) -> None:
        # Capacity must be known before calling base __init__, because the
        # input and intermediate texture arrays need that many slices.
        self.cache_capacity = config.cache_capacity

        super().__init__(
            config=config,
            crop_width=crop_width,
            crop_height=crop_height,
            max_layers=self.cache_capacity,  # array textures sized for cache
        )

        # ------------------------------------------------------------------
        # Cache atlas - a plain storage array, never bound to any pipeline
        # ------------------------------------------------------------------
        self.output_atlas = Texture2D(
            self.tile_out_w_final,
            self.tile_out_h_final,
            slices=self.cache_capacity,
            force_array_view=True,
        )

        # ------------------------------------------------------------------
        # LRU layer manager
        # ------------------------------------------------------------------
        self.atlas_manager = TileAtlasManager(
            capacity=self.cache_capacity,
            tile_width=self.tile_out_w_final,
            tile_height=self.tile_out_h_final,
        )

        logger.info(
            "CachedTileProcessor ready - cache capacity %d tiles", self.cache_capacity
        )

    # ----------------------------------------------------------------------
    #  Public helpers
    # ----------------------------------------------------------------------
    def total_tiles(self) -> int:
        """Total number of tile grid cells in the crop area."""
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty_rects: int) -> bool:
        """
        Return True if the number of dirty rectangles is below the threshold.
        """
        threshold = int(self.total_tiles() * self.area_threshold)
        return num_dirty_rects <= threshold

    # ----------------------------------------------------------------------
    #  Main processing - cache hits and misses
    # ----------------------------------------------------------------------
    def process_tiles(
        self,
        dirty_tiles: List[Tuple[int, int, int, bytes, int, int]],
    ) -> None:
        """
        Process dirty tiles using the LRU cache.

        Args:
            dirty_tiles: List of
                (tile_x, tile_y, hash, data_bytes, valid_x, valid_y)
        """
        if not dirty_tiles:
            return

        hits: List[Tuple[int, int, int]] = []  # (tx, ty, layer)
        misses: List[Tuple[int, int, int, bytes, int, int]] = []  # +data,valid

        # ---- 1. Separate hits and misses -----------------------------------
        for tx, ty, tile_hash, data, valid_x, valid_y in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, tile_hash)
            if was_cached:
                hits.append((tx, ty, layer))
            else:
                misses.append((tx, ty, layer, data, valid_x, valid_y))

        # ---- 2. Process misses in chunks that fit the pipeline arrays ------
        for chunk in self._chunk_misses(misses):
            miss_batch = [
                (tx, ty, data, valid_x, valid_y)
                for tx, ty, layer, data, valid_x, valid_y in chunk
            ]
            super().process_tiles(miss_batch)

        # ---- 3. Store freshly upscaled miss tiles into the cache atlas -----
        scale = 4 if self.double_upscale else 2
        for tx, ty, layer, _, _, _ in misses:
            dst_x = tx * self.tile_size * scale
            dst_y = ty * self.tile_size * scale
            copy_w = min(self.tile_size * scale, self.output_texture.width - dst_x)
            copy_h = min(self.tile_size * scale, self.output_texture.height - dst_y)
            if copy_w > 0 and copy_h > 0:
                # Copy from the full-frame output into the atlas layer
                self.output_texture.copy_to(
                    self.output_atlas,
                    src_x=dst_x,
                    src_y=dst_y,
                    width=copy_w,
                    height=copy_h,
                    src_slice=0,  # output texture is a single slice
                    dst_slice=layer,  # target atlas layer
                    dst_x=0,
                    dst_y=0,  # top-left of atlas tile
                )

        # ---- 4. Blit all cache hits back to the output texture -------------
        for tx, ty, layer in hits:
            dst_x = tx * self.tile_size * scale
            dst_y = ty * self.tile_size * scale
            copy_w = min(self.tile_size * scale, self.output_texture.width - dst_x)
            copy_h = min(self.tile_size * scale, self.output_texture.height - dst_y)
            if copy_w > 0 and copy_h > 0:
                self.output_atlas.copy_to(
                    self.output_texture,
                    dst_x=dst_x,
                    dst_y=dst_y,
                    width=copy_w,
                    height=copy_h,
                    src_slice=layer,  # atlas layer
                    dst_slice=0,
                )

    # ----------------------------------------------------------------------
    #  Helper - split misses into chunks that fit in max_layers
    # ----------------------------------------------------------------------
    def _chunk_misses(self, misses: List) -> List[List]:
        """Yield sub-lists of misses with at most `self.max_layers` items."""
        for i in range(0, len(misses), self.max_layers):
            yield misses[i : i + self.max_layers]

    # ----------------------------------------------------------------------
    #  Static utility - extract tiles with content hash
    # ----------------------------------------------------------------------
    @staticmethod
    def extract_dirty_tiles_with_hash(
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        tile_size: int,
        margin: int,
    ) -> List[Tuple[int, int, int, bytes, int, int]]:
        expanded_tiles = extract_expanded_tiles(
            frame, rects, crop_width, crop_height, tile_size, margin
        )
        result = []
        for tx, ty, data, valid_x, valid_y in expanded_tiles:
            h = xxhash.xxh64(data).intdigest()
            result.append((tx, ty, h, data, valid_x, valid_y))
        return result
