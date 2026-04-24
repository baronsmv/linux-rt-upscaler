import logging
import struct
from typing import List, Tuple, Dict

from .atlas import TileAtlasManager
from .tile import TileProcessor
from .utils import compute_tile_hash, extract_expanded_tiles
from ..config import Config
from ..vulkan import Texture2D, Buffer, Compute

logger = logging.getLogger(__name__)


class CachedTileProcessor(TileProcessor):
    """
    Tile processor with an LRU cache for tile outputs.

    Inherits all expanded-tile extraction and dispatch logic from `TileProcessor`.
    Overrides template methods to:
      - Create an output atlas (multi-slice array) instead of a 1-slice texture.
      - Manage cache hits/misses using `TileAtlasManager`.
      - Include the correct `outputLayer` in push constants.

    On each frame:
      - For cache hits: the tile is simply copied from the atlas to the final
        output texture; no CNN passes are executed.
      - For cache misses: the tile is processed normally (via superclass logic),
        which writes to an atlas layer; afterwards it is copied to the output.

    The cache capacity limits the number of concurrently stored tiles. The
    least-recently-used tile is evicted when the cache is full.

    Attributes:
        cache_capacity (int): Maximum number of tiles in the cache.
        cache_threshold (float): Fraction of total tiles above which full-frame
                                 fallback is triggered.
        atlas_manager (TileAtlasManager): Manages layer allocation and LRU.
        output_atlas (Texture2D): Array texture storing cached tile outputs.
        _miss_layer_map (Dict): Temporary mapping from tile coords to atlas layer
                                during processing of misses.
    """

    def __init__(
        self,
        config: Config,
        crop_width: int,
        crop_height: int,
    ) -> None:
        """
        Initialize the cached tile processor.

        Args:
            crop_width: Width of the captured crop area in pixels.
            crop_height: Height of the captured crop area in pixels.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal input tile size (without margin).
            cache_capacity: Maximum number of tiles stored in the cache.
            cache_threshold: Fraction of total tiles above which full-frame is used.
            tile_context_margin: Extra border pixels for convolution context.
        """
        # The base class uses max_layers = cache_capacity (atlas slices)
        super().__init__(
            config=config,
            crop_width=crop_width,
            crop_height=crop_height,
        )

        self.cache_capacity = config.cache_capacity

        # Manager for LRU cache and layer allocation
        self.atlas_manager = TileAtlasManager(
            capacity=self.cache_capacity,
            tile_width=self.tile_out_w_final,
            tile_height=self.tile_out_h_final,
        )

        # Temporary mapping used during process_tiles to pass outputLayer
        self._miss_layer_map: Dict[Tuple[int, int], int] = {}

        # Replace the base output texture with an atlas and rebind pipeline
        self._convert_output_to_atlas()

    # --------------------------------------------------------------------------
    #  Override: Create output atlas and rebind final pipeline
    # --------------------------------------------------------------------------
    def _convert_output_to_atlas(self) -> None:
        """
        Replace the 1-slice output texture with a multi-slice atlas.

        This method:
          1. Creates `self.output_atlas`, an array texture with `cache_capacity`
             slices, sized to hold one final upscaled tile per slice.
          2. Re-creates the final pass pipeline, binding `self.output_atlas` as
             the UAV instead of `self.output_texture`.
          3. The original `self.output_texture` remains as the final 2D target
             for copies (it is still needed for presentation).
        """
        # Create the output atlas (array of final tile size)
        self.output_atlas = Texture2D(
            self.tile_out_w_final,
            self.tile_out_h_final,
            slices=self.cache_capacity,
            force_array_view=True,
        )

        # Recreate the final pipeline with the atlas as UAV
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

        # SRVs: residual texture + intermediate textures
        srv_list = [self.full_input_tex]
        pre_final_stage = self.stages[-2] if self.double_upscale else self.stages[0]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final_stage.outputs[f"t{i}"])

        # UAV is now the output atlas (array)
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

        # Replace the final pass in the appropriate stage
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = self.final_pipeline
        else:
            self.stages[0].pipelines[-1] = self.final_pipeline

        logger.debug("Output atlas created and final pipeline rebound")

    # --------------------------------------------------------------------------
    #  Override: Push constant generation (include outputLayer)
    # --------------------------------------------------------------------------
    def _make_push_data(
        self,
        tx: int,
        ty: int,
        layer_idx: int,
        valid_x: int,
        valid_y: int,
        full_out_w: int,
        full_out_h: int,
        actual_out_w: int,
        actual_out_h: int,
    ) -> bytes:
        """
        Build push constant data including the correct output layer.

        The output layer is retrieved from `self._miss_layer_map`, which is
        populated before processing cache misses.

        Returns:
            Packed bytes (60 bytes) with `outputLayer` set to the atlas slice.
        """
        scale = 4 if self.double_upscale else 2
        dst_x = tx * self.tile_size * scale
        dst_y = ty * self.tile_size * scale

        valid_block_x = valid_x * scale
        valid_block_y = valid_y * scale

        # Use the mapped atlas layer; fallback to layer_idx (should never happen)
        output_layer = self._miss_layer_map.get((tx, ty), layer_idx)

        return struct.pack(
            "IIIIIIIIIII",  # 11 unsigned ints
            layer_idx,  # inputLayer
            dst_x,
            dst_y,  # dstOffset
            self.margin,  # margin
            full_out_w,
            full_out_h,  # fullOutWidth, fullOutHeight
            valid_block_x,
            valid_block_y,  # validOffset
            actual_out_w,
            actual_out_h,  # tileOutExtent
            output_layer,  # outputLayer
        )

    # --------------------------------------------------------------------------
    #  Public: Threshold check for fallback
    # --------------------------------------------------------------------------
    def total_tiles(self) -> int:
        """Total number of tile grid cells in the crop area."""
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty_rects: int) -> bool:
        """
        Return True if the number of dirty rectangles is below the threshold.

        The threshold is a fraction (`cache_threshold`) of the total number of
        tiles. This heuristic prevents cache mode from being overwhelmed when
        a large portion of the frame changes.
        """
        threshold = int(self.total_tiles() * self.cache_threshold)
        return num_dirty_rects <= threshold

    # --------------------------------------------------------------------------
    #  Override: Main tile processing with caching
    # --------------------------------------------------------------------------
    def process_tiles(self, dirty_tiles: List[Tuple[int, int, int, bytes]]) -> None:
        """
        Process dirty tiles using the LRU cache.

        This method overrides the base implementation to:
          1. Separate tiles into cache hits and misses.
          2. For misses, call the superclass `process_tiles` with the expanded
             tile data, using the assigned atlas layer.
          3. For both hits and misses, copy the final tile from the output atlas
             to the correct position in the full output texture.

        Args:
            dirty_tiles: List of (tile_x, tile_y, hash, data_bytes) as returned
                by `extract_dirty_tiles_with_hash`.
        """
        if not dirty_tiles:
            return

        misses: List[Tuple[int, int, int, bytes]] = []  # (tx, ty, layer, data)
        hits: List[Tuple[int, int, int]] = []  # (tx, ty, layer)

        # 1. Separate hits and misses, acquire layers from cache
        for tx, ty, tile_hash, data in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, tile_hash)
            if was_cached:
                hits.append((tx, ty, layer))
            else:
                misses.append((tx, ty, layer, data))

        # 2. Process misses using the base class logic
        if misses:
            # Build the miss batch in the format expected by super().process_tiles
            miss_batch = [
                (tx, ty, data, self.margin, self.margin)
                for tx, ty, layer, data in misses
            ]
            # Store the layer mapping for _make_push_data
            self._miss_layer_map = {(tx, ty): layer for tx, ty, layer, _ in misses}

            # Temporarily adjust max_layers to process all misses in one batch
            original_max = self.max_layers
            self.max_layers = len(miss_batch)
            try:
                super().process_tiles(miss_batch)
            finally:
                self.max_layers = original_max
                self._miss_layer_map.clear()

        # 3. Copy all tiles (hits + misses) from atlas to output texture
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

    # --------------------------------------------------------------------------
    #  Static utility: Extract tiles with content hash
    # --------------------------------------------------------------------------
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

        This is a convenience wrapper that reuses `tile_utils.extract_expanded_tiles`
        and adds an xxHash64 over the interior region.

        Returns:
            List of (tile_x, tile_y, hash, data_bytes).
        """
        expanded_tiles = extract_expanded_tiles(
            frame, rects, crop_width, crop_height, tile_size, margin
        )
        expanded_size = tile_size + 2 * margin
        result = []
        for tx, ty, data, valid_x, valid_y in expanded_tiles:
            h = compute_tile_hash(data, expanded_size, valid_x, valid_y, tile_size)
            result.append((tx, ty, h, data))
        return result
