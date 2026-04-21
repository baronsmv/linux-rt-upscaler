import logging
import struct
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class TileProcessor(ABC):
    """
    Abstract base for tile-based upscaling strategies.

    Subclasses must implement `process_tiles` to handle dirty tiles
    and populate `self.output_texture`.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        variant: str,
        push_constant_size: int,
    ):
        """
        Common initialization for tile processors.

        Args:
            crop_width, crop_height: Dimensions of the captured crop area.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Input tile size in pixels.
            variant: Shader variant suffix ("_offset" or "_tile").
            push_constant_size: Size of push constant block (bytes).
        """
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.double_upscale = double_upscale

        # Tile output dimensions after first and final stage
        self.tile_out_w_first = tile_size * 2
        self.tile_out_h_first = tile_size * 2
        if double_upscale:
            self.tile_out_w_final = tile_size * 4
            self.tile_out_h_final = tile_size * 4
        else:
            self.tile_out_w_final = self.tile_out_w_first
            self.tile_out_h_final = self.tile_out_h_first

        # Final output texture (full frame)
        out_w = crop_width * (4 if double_upscale else 2)
        out_h = crop_height * (4 if double_upscale else 2)
        self.output_texture = Texture2D(out_w, out_h)

        # Shared pipeline factory for all SRCNN stages
        config = load_cunny_model(model_name, variant=variant)
        config.push_constant_size = push_constant_size
        self.factory = PipelineFactory(config)

        # Staging buffer for uploading tile data (reused)
        self.staging = Buffer(tile_size * tile_size * 4, heap_type=HEAP_UPLOAD)

        # Subclasses should populate self.stages (list of SRCNN instances)
        self.stages: List[SRCNN] = []

        # Pre-computed dispatch groups for each stage
        self.groups_per_stage: List[Tuple[int, int]] = []

    @abstractmethod
    def process_tiles(self, dirty_tiles) -> None:
        """Process a batch of dirty tiles and update the output texture."""
        pass

    def _build_dispatch_sequence(
        self, tile_batch: List[Tuple[int, int, int, Optional[bytes]]]
    ) -> List[Tuple]:
        """
        Build a list of dispatches for a batch of tiles.

        Args:
            tile_batch: List of (tile_x, tile_y, layer, push_data) tuples.

        Returns:
            List of (Compute, groups_x, groups_y, groups_z, push_data) ready
            for `dispatch_sequence`.
        """
        dispatches = []
        for tx, ty, layer, push_data in tile_batch:
            for stage_idx, srnn in enumerate(self.stages):
                groups_x, groups_y = self.groups_per_stage[stage_idx]
                for pipe in srnn.pipelines:
                    dispatches.append((pipe, groups_x, groups_y, 1, push_data))
        return dispatches


class OffsetTileProcessor(TileProcessor):
    """
    Tile processing without caching.

    Dirty tiles are uploaded to a single-layer input texture and compute
    shaders write directly to the final output texture with a `dstOffset`.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
    ):
        super().__init__(
            crop_width,
            crop_height,
            model_name,
            double_upscale,
            tile_size,
            variant="_offset",
            push_constant_size=12,  # uint inputLayer + uint2 dstOffset
        )

        # Create SRCNN stages for offset mode
        self._create_stages()

    def _create_stages(self) -> None:
        """Create SRCNN instances for each upscaling stage."""
        # Stage 1 input: single 2D texture (reused per tile)
        input_tex1 = Texture2D(
            self.tile_size, self.tile_size, slices=1, force_array_view=True
        )

        # Stage 1 output (intermediate) – 2D texture sized for 2x tile
        inter_tex = Texture2D(
            self.tile_out_w_first,
            self.tile_out_h_first,
            slices=1,
            force_array_view=True,
        )
        outputs_1 = {"output": inter_tex}
        for i in range(self.factory.config.num_textures):
            outputs_1[f"t{i}"] = Texture2D(
                self.tile_out_w_first,
                self.tile_out_h_first,
                slices=1,
                force_array_view=True,
            )

        srcnn_1 = SRCNN(
            factory=self.factory,
            width=self.tile_size,
            height=self.tile_size,
            input_texture=input_tex1,
            output_textures=outputs_1,
            push_constant_size=self.factory.config.push_constant_size,
        )
        self.stages.append(srcnn_1)
        self.groups_per_stage.append(
            dispatch_groups(
                self.tile_out_w_first, self.tile_out_h_first, last_pass=False
            )
        )

        if self.double_upscale:
            # Stage 2 input = Stage 1 output
            input_tex_2 = inter_tex
            outputs_2 = {"output": self.output_texture}
            for i in range(self.factory.config.num_textures):
                outputs_2[f"t{i}"] = Texture2D(
                    self.tile_out_w_final,
                    self.tile_out_h_final,
                    slices=1,
                    force_array_view=True,
                )

            srcnn_2 = SRCNN(
                factory=self.factory,
                width=self.tile_out_w_first,
                height=self.tile_out_h_first,
                input_texture=input_tex_2,
                output_textures=outputs_2,
                push_constant_size=self.factory.config.push_constant_size,
            )
            # Final pass of second stage writes 2x2 per thread
            self.groups_per_stage[-1] = dispatch_groups(
                self.tile_out_w_final, self.tile_out_h_final, last_pass=True
            )
        else:
            # For 2x only, stage 1 writes directly to final output
            outputs_1["output"] = self.output_texture
            # Recreate SRCNN with updated output textures
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=self.tile_size,
                height=self.tile_size,
                input_texture=input_tex1,
                output_textures=outputs_1,
                push_constant_size=self.factory.config.push_constant_size,
            )
            # Final pass of first stage now writes 2x2 per thread
            self.groups_per_stage[0] = dispatch_groups(
                self.tile_out_w_final, self.tile_out_h_final, last_pass=True
            )

        # Store input texture reference for uploads
        self.input_tex = self.stages[0].input

    def process_tiles(self, dirty_tiles: List[Tuple[int, int, bytes]]) -> None:
        if not dirty_tiles:
            return

        tile_data_size = self.tile_size * self.tile_size * 4
        total_staging = len(dirty_tiles) * tile_data_size

        # Ensure staging buffer is large enough
        if self.staging.size < total_staging:
            self.staging = Buffer(total_staging, heap_type=HEAP_UPLOAD)

        # Prepare tile tuples for the batch
        tile_batch = []
        for tx, ty, data in dirty_tiles:
            dst_x = tx * self.tile_out_w_final
            dst_y = ty * self.tile_out_h_final
            push_data = struct.pack("III", 0, dst_x, dst_y)
            tile_batch.append((dst_x, dst_y, push_data, data))

        groups_x, groups_y = self.groups_per_stage[
            0
        ]  # For the first pipeline (offset mode uses first stage's pipelines)
        self.stages[0].pipelines[0].execute_tile_batch(
            tile_batch,
            self.input_tex,
            self.staging,
            self.tile_size,
            groups_x,
            groups_y,
        )


class CachedTileProcessor(TileProcessor):
    """
    Tile processing with an LRU cache.

    Uses an atlas of layers to store input/output tiles. Tiles are uploaded
    and computed only on cache misses. All tiles (hits + misses) are copied
    from the output atlas to the final 2D texture.
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
    ):
        super().__init__(
            crop_width,
            crop_height,
            model_name,
            double_upscale,
            tile_size,
            variant="_tile",
            push_constant_size=8,  # uint inputLayer + uint outputLayer
        )

        self.cache_capacity = cache_capacity
        self.cache_threshold = cache_threshold

        from .cache import TileAtlasManager

        self.atlas_manager = TileAtlasManager(
            capacity=cache_capacity,
            tile_width=self.tile_out_w_final,
            tile_height=self.tile_out_h_final,
        )

        self._create_stages()

        # Output atlas reference for final copy
        self.final_atlas = self.stages[-1].outputs["output"]

    def _create_stages(self) -> None:
        """Create SRCNN stages with texture atlases."""
        # Input atlas shared across stages
        input_atlas = Texture2D(
            self.tile_size, self.tile_size, slices=self.cache_capacity
        )

        # Stage 1
        inter_atlas = Texture2D(
            self.tile_out_w_first, self.tile_out_h_first, slices=self.cache_capacity
        )
        outputs1 = {"output": inter_atlas}
        for i in range(self.factory.config.num_textures):
            outputs1[f"t{i}"] = Texture2D(
                self.tile_out_w_first, self.tile_out_h_first, slices=self.cache_capacity
            )

        srnn1 = SRCNN(
            factory=self.factory,
            width=self.tile_size,
            height=self.tile_size,
            input_texture=input_atlas,
            output_textures=outputs1,
            push_constant_size=self.factory.config.push_constant_size,
        )
        self.stages.append(srnn1)
        self.groups_per_stage.append(
            dispatch_groups(
                self.tile_out_w_first, self.tile_out_h_first, last_pass=False
            )
        )

        if self.double_upscale:
            # Stage 2
            output_atlas = Texture2D(
                self.tile_out_w_final, self.tile_out_h_final, slices=self.cache_capacity
            )
            outputs2 = {"output": output_atlas}
            for i in range(self.factory.config.num_textures):
                outputs2[f"t{i}"] = Texture2D(
                    self.tile_out_w_final,
                    self.tile_out_h_final,
                    slices=self.cache_capacity,
                )

            srnn2 = SRCNN(
                factory=self.factory,
                width=self.tile_out_w_first,
                height=self.tile_out_h_first,
                input_texture=inter_atlas,
                output_textures=outputs2,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.stages.append(srnn2)
            self.groups_per_stage[-1] = dispatch_groups(
                self.tile_out_w_final, self.tile_out_h_final, last_pass=True
            )
        else:
            # For 2x only, the first stage's final pass writes 2x2 per thread
            self.groups_per_stage[0] = dispatch_groups(
                self.tile_out_w_final, self.tile_out_h_final, last_pass=True
            )

        self.input_atlas = input_atlas

    def total_tiles(self) -> int:
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty: int) -> bool:
        threshold = int(self.total_tiles() * self.cache_threshold)
        return num_dirty <= threshold

    def process_tiles(self, dirty_tiles: List[Tuple[int, int, int, bytes]]) -> None:
        """
        Process dirty tiles with caching.

        Args:
            dirty_tiles: List of (tile_x, tile_y, hash, data_bytes).
        """
        if not dirty_tiles:
            return

        # Separate cache hits and misses
        misses = []
        hits = []
        for tx, ty, tile_hash, data in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, tile_hash)
            if was_cached:
                hits.append((tx, ty, layer))
            else:
                misses.append((tx, ty, layer, data))

        # Upload misses to input atlas
        upload_list = []
        for tx, ty, layer, data in misses:
            upload_list.append((data, 0, 0, self.tile_size, self.tile_size, layer))
        if upload_list:
            self.input_atlas.upload_subresources(upload_list)

        # Build dispatches for misses
        tile_batch = []
        for tx, ty, layer, _ in misses:
            push_data = struct.pack("II", layer, layer)
            tile_batch.append((tx, ty, layer, push_data))

        dispatches = self._build_dispatch_sequence(tile_batch)
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

        # Copy all tiles (hits + misses) from final atlas to output texture
        all_tiles = hits + [(tx, ty, layer) for tx, ty, layer, _ in misses]
        for tx, ty, layer in all_tiles:
            dst_x = tx * self.tile_out_w_final
            dst_y = ty * self.tile_out_h_final
            copy_w = min(self.tile_out_w_final, self.output_texture.width - dst_x)
            copy_h = min(self.tile_out_h_final, self.output_texture.height - dst_y)
            if copy_w > 0 and copy_h > 0:
                self.final_atlas.copy_to(
                    self.output_texture,
                    src_slice=layer,
                    dst_x=dst_x,
                    dst_y=dst_y,
                    width=copy_w,
                    height=copy_h,
                )
