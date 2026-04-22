import logging
import struct
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD, Compute

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
#  TileProcessor – abstract base class
# ----------------------------------------------------------------------
class TileProcessor(ABC):
    """
    Abstract base for tile-based upscaling strategies.

    Subclasses must implement `process_tiles` to handle dirty tiles and
    populate `self.output_texture`. The base class provides common
    initialization and helper methods.

    Attributes:
        crop_width, crop_height: Dimensions of the captured crop area.
        tile_size: Nominal tile size (input to the network) in pixels.
        margin: Extra border pixels added around each tile for context.
        double_upscale: If True, perform 4x upscaling (two 2x stages).
        max_layers: Maximum number of concurrent tile layers (batch size).
        expanded_tile_size: Tile size including margin.
        tile_out_w_first, tile_out_h_first: Output size of first upscale stage.
        tile_out_w_final, tile_out_h_final: Final output size per tile.
        output_texture: Full-frame final upscaled image (2D).
        factory: Shared pipeline factory for all SRCNN stages.
        staging: Reusable upload buffer for tile data.
        stages: List of SRCNN instances (one per upscale stage).
        groups_per_stage: Dispatch group counts for each stage.
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
        tile_context_margin: int,
        max_layers: int,
    ):
        """
        Common initialisation for tile processors.

        Args:
            crop_width, crop_height: Dimensions of the captured crop area.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal tile size (input to the network) in pixels.
            variant: Shader variant suffix ("_offset" or "_tile").
            push_constant_size: Size of push constant block (bytes).
            tile_context_margin: Extra border pixels added around each tile
                to provide context for convolution layers.
            max_layers: Maximum number of tiles processed in one batch.
        """
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.margin = tile_context_margin
        self.double_upscale = double_upscale
        self.max_layers = max_layers

        # The actual input tile size after adding the margin.
        self.expanded_tile_size = tile_size + 2 * self.margin

        # Output dimensions for each stage (after upscaling).
        self.tile_out_w_first = self.expanded_tile_size * 2
        self.tile_out_h_first = self.expanded_tile_size * 2
        if double_upscale:
            self.tile_out_w_final = self.expanded_tile_size * 4
            self.tile_out_h_final = self.expanded_tile_size * 4
        else:
            self.tile_out_w_final = self.tile_out_w_first
            self.tile_out_h_final = self.tile_out_h_first

        # Final output texture (full frame, upscaled).
        out_w = crop_width * (4 if double_upscale else 2)
        out_h = crop_height * (4 if double_upscale else 2)
        self.output_texture = Texture2D(out_w, out_h)

        # Shared pipeline factory for all SRCNN stages.
        config = load_cunny_model(model_name, variant=variant)
        config.push_constant_size = push_constant_size
        self.factory = PipelineFactory(config)

        # Staging buffer for uploading tile data (reused).
        self.staging = Buffer(
            self.expanded_tile_size * self.expanded_tile_size * 4,
            heap_type=HEAP_UPLOAD,
        )

        # Subclasses populate these.
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []

    @abstractmethod
    def process_tiles(self, dirty_tiles) -> None:
        """Process a batch of dirty tiles and update the output texture."""
        pass

    def _build_dispatch_sequence(
        self, tile_batch: List[Tuple[int, int, int, Optional[bytes]]]
    ) -> List[Tuple[Compute, int, int, int, bytes]]:
        """
        Build a list of dispatches for a batch of tiles.

        Args:
            tile_batch: List of (tile_x, tile_y, layer, push_data) tuples.

        Returns:
            List of (Compute, groups_x, groups_y, groups_z, push_data) ready
            for `dispatch_sequence`.
        """
        dispatches = []
        for _, _, _, push_data in tile_batch:
            for stage_idx, srnn in enumerate(self.stages):
                groups_x, groups_y = self.groups_per_stage[stage_idx]
                for pipe in srnn.pipelines:
                    dispatches.append((pipe, groups_x, groups_y, 1, push_data))
        return dispatches

    def _get_pipelines_for_batch(self) -> List[Compute]:
        """
        Return the list of Compute pipelines to execute for a tile batch.
        Subclasses may override to inject a custom final pass.
        """
        pipelines = []
        for stage in self.stages:
            pipelines.extend(stage.pipelines)
        return pipelines


# ----------------------------------------------------------------------
#  OffsetTileProcessor – no cache, direct writes with dstOffset
# ----------------------------------------------------------------------
class OffsetTileProcessor(TileProcessor):
    """
    Tile processing without caching.

    Dirty tiles are expanded by a context margin, uploaded to an array
    texture with multiple layers (one per tile in the batch), and processed
    by the SRCNN stages. The final pass writes only the interior valid
    region directly into the full output texture.

    The number of concurrent tiles is limited by `max_layers`. If more
    tiles are dirty, the caller should fall back to full-frame mode.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        tile_context_margin: int = 0,
        max_layers: int = 16,
    ):
        super().__init__(
            crop_width,
            crop_height,
            model_name,
            double_upscale,
            tile_size,
            variant="_offset",
            push_constant_size=52,  # 13 uints (updated for validOffset)
            tile_context_margin=tile_context_margin,
            max_layers=max_layers,
        )

        # Texture holding the full captured frame (with damage regions uploaded).
        self.full_input_tex = Texture2D(
            crop_width, crop_height, slices=self.max_layers, force_array_view=True
        )
        full_size = crop_width * crop_height * 4
        self.full_staging = Buffer(full_size, heap_type=HEAP_UPLOAD)

        self._create_stages()

    # ------------------------------------------------------------------
    #  Stage construction
    # ------------------------------------------------------------------
    def _create_stages(self) -> None:
        """
        Create SRCNN instances for each upscaling stage.

        The input and intermediate textures are sized according to the
        expanded tile size (including margin). They are created as
        texture arrays with `max_layers` slices to support concurrent
        tile processing. The final output texture is the full‑frame 2D image.
        """
        # ------------------------------------------------------------------
        # Stage 1 input: a texture array sized for the expanded tile.
        # ------------------------------------------------------------------
        input_tex1 = Texture2D(
            self.expanded_tile_size,
            self.expanded_tile_size,
            slices=self.max_layers,
            force_array_view=True,
        )

        # ------------------------------------------------------------------
        # Stage 1 outputs (intermediate feature maps) – all arrays.
        # ------------------------------------------------------------------
        inter_tex = Texture2D(
            self.tile_out_w_first,
            self.tile_out_h_first,
            slices=self.max_layers,
            force_array_view=True,
        )
        outputs_1 = {"output": inter_tex}
        for i in range(self.factory.config.num_textures):
            outputs_1[f"t{i}"] = Texture2D(
                self.tile_out_w_first,
                self.tile_out_h_first,
                slices=self.max_layers,
                force_array_view=True,
            )

        srcnn_1 = SRCNN(
            factory=self.factory,
            width=self.expanded_tile_size,
            height=self.expanded_tile_size,
            input_texture=input_tex1,
            output_textures=outputs_1,
            push_constant_size=self.factory.config.push_constant_size,
        )
        self.stages.append(srcnn_1)
        nominal_out_w_first = self.tile_size * 2
        nominal_out_h_first = self.tile_size * 2
        self.groups_per_stage.append(
            dispatch_groups(nominal_out_w_first, nominal_out_h_first, last_pass=False)
        )

        if self.double_upscale:
            # Stage 2 input = Stage 1 output array.
            input_tex_2 = inter_tex
            outputs_2 = {"output": self.output_texture}  # final output is 2D
            for i in range(self.factory.config.num_textures):
                outputs_2[f"t{i}"] = Texture2D(
                    self.tile_out_w_final,
                    self.tile_out_h_final,
                    slices=self.max_layers,
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
            self.stages.append(srcnn_2)
            nominal_out_w_final = self.tile_size * 4
            nominal_out_h_final = self.tile_size * 4
            self.groups_per_stage[-1] = dispatch_groups(
                nominal_out_w_final, nominal_out_h_final, last_pass=True
            )
        else:
            # For 2x only, stage 1 writes directly to final output (2D)
            outputs_1["output"] = self.output_texture
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=input_tex1,
                output_textures=outputs_1,
                push_constant_size=self.factory.config.push_constant_size,
            )
            nominal_out_w_final = self.tile_size * 2
            nominal_out_h_final = self.tile_size * 2
            self.groups_per_stage[0] = dispatch_groups(
                nominal_out_w_final, nominal_out_h_final, last_pass=True
            )

        # Keep a reference to the input texture for uploads.
        self.input_tex = self.stages[0].input

        # ------------------------------------------------------------------
        #  Final pass pipeline (customised for offset writes)
        # ------------------------------------------------------------------
        final_pass_index = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_index]

        # Constant buffer for the final pass: describes the intermediate
        # feature map dimensions and the full output size.
        scale = 4 if self.double_upscale else 2
        full_out_w = self.crop_width * scale
        full_out_h = self.crop_height * scale
        cb_data = struct.pack(
            "IIIIffff",
            self.tile_out_w_first,  # in_width  (for T0/T1 sampling)
            self.tile_out_h_first,  # in_height
            full_out_w,  # out_width
            full_out_h,  # out_height
            1.0 / self.tile_out_w_first,  # in_dx
            1.0 / self.tile_out_h_first,  # in_dy
            1.0 / full_out_w,  # out_dx
            1.0 / full_out_h,  # out_dy
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        # SRV list: [full_input_tex] + intermediate textures (T0, T1, ...)
        srv_list = [self.full_input_tex]
        inter_stage = self.stages[-1] if self.double_upscale else self.stages[0]
        for i in range(self.factory.config.num_textures):
            srv_list.append(inter_stage.outputs[f"t{i}"])

        # UAV list: final output texture
        uav_list = [self.output_texture]

        # Samplers for the final pass.
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

        # Replace the original final pass pipeline with our custom one.
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = self.final_pipeline
        else:
            self.stages[0].pipelines[-1] = self.final_pipeline

    def _get_pipelines_for_batch(self) -> List[Compute]:
        """
        Override to replace the original final pass with our custom pipeline.
        """
        if self.double_upscale:
            return (
                self.stages[0].pipelines
                + self.stages[1].pipelines[:-1]
                + [self.final_pipeline]
            )
        else:
            return self.stages[0].pipelines[:-1] + [self.final_pipeline]

    # ------------------------------------------------------------------
    #  Damage region expansion (for residual texture)
    # ------------------------------------------------------------------
    @staticmethod
    def _expand_damage_rects(
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        margin: int,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Expand damage rectangles by a given margin, clamped to crop bounds.

        Args:
            rects: Damage rectangles as (x, y, w, h, hash).
            crop_width, crop_height: Dimensions of the full crop area.
            margin: Pixels to add on each side.

        Returns:
            List of expanded rectangles as (x, y, w, h).
        """
        expanded = []
        for rx, ry, rw, rh, _ in rects:
            ex0 = max(0, rx - margin)
            ey0 = max(0, ry - margin)
            ex1 = min(crop_width, rx + rw + margin)
            ey1 = min(crop_height, ry + rh + margin)
            if ex1 > ex0 and ey1 > ey0:
                expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))
        return expanded

    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
    ) -> None:
        """
        Upload expanded damage regions to the residual texture.

        This texture provides the network with the surrounding context
        needed for the final pass. Only the damaged areas are updated.
        """
        if not rects:
            return

        expanded_rects = self._expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.margin
        )
        uploads = []
        stride = self.crop_width * 4

        for ex, ey, ew, eh in expanded_rects:
            rect_data = bytearray(ew * eh * 4)
            for row in range(eh):
                src_start = (ey + row) * stride + ex * 4
                dst_start = row * ew * 4
                rect_data[dst_start : dst_start + ew * 4] = frame[
                    src_start : src_start + ew * 4
                ]
            # Upload to every layer (0 .. max_layers-1)
            for layer in range(self.max_layers):
                uploads.append((bytes(rect_data), ex, ey, ew, eh, layer))
        self.full_input_tex.upload_subresources(uploads)

    # ------------------------------------------------------------------
    #  Tile extraction (expanded, with valid region offsets)
    # ------------------------------------------------------------------
    @staticmethod
    def extract_expanded_tiles(
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        tile_size: int,
        margin: int,
    ) -> List[Tuple[int, int, bytes, int, int]]:
        """
        Extract expanded tiles for all dirty tile positions.

        For each tile in the grid that overlaps any damage rectangle,
        extract a region of size `(tile_size + 2*margin)²` (clamped to
        crop bounds). Return the raw pixel data together with the valid
        output offset (valid_x, valid_y) indicating where the interior
        `tile_size x tile_size` region begins within the expanded tile.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber.
            crop_width, crop_height: Dimensions of the crop area.
            tile_size: Nominal tile size (interior region).
            margin: Context margin to add on each side.

        Returns:
            List of tuples:
                (tile_x, tile_y, data_bytes, valid_x, valid_y)
            where valid_x and valid_y are the offset inside the expanded tile
            where the valid output region starts (usually margin, except at
            image boundaries where the expansion was clamped).
        """
        stride = crop_width * 4
        tiles_x = (crop_width + tile_size - 1) // tile_size
        tiles_y = (crop_height + tile_size - 1) // tile_size

        # Find dirty tile grid cells.
        dirty_tiles = set()
        for rx, ry, rw, rh, _ in rects:
            tx0 = rx // tile_size
            ty0 = ry // tile_size
            tx1 = (rx + rw + tile_size - 1) // tile_size
            ty1 = (ry + rh + tile_size - 1) // tile_size
            for ty in range(ty0, min(ty1, tiles_y)):
                for tx in range(tx0, min(tx1, tiles_x)):
                    dirty_tiles.add((tx, ty))

        expanded_size = tile_size + 2 * margin
        expanded_bytes = expanded_size * expanded_size * 4
        result = []

        for tx, ty in dirty_tiles:
            # Nominal tile top-left in crop coordinates.
            tile_x0 = tx * tile_size
            tile_y0 = ty * tile_size

            # Expanded region (before clamping).
            exp_x0 = tile_x0 - margin
            exp_y0 = tile_y0 - margin

            # Clamp source region to crop bounds
            src_x0 = max(0, exp_x0)
            src_y0 = max(0, exp_y0)
            src_x1 = min(crop_width, exp_x0 + expanded_size)
            src_y1 = min(crop_height, exp_y0 + expanded_size)

            # Destination offsets within the expanded tile buffer.
            dst_x0 = src_x0 - exp_x0
            dst_y0 = src_y0 - exp_y0
            copy_w = src_x1 - src_x0
            copy_h = src_y1 - src_y0

            data = bytearray(expanded_bytes)

            # Copy valid region
            for row in range(copy_h):
                src_start = (src_y0 + row) * stride + src_x0 * 4
                dst_start = ((dst_y0 + row) * expanded_size + dst_x0) * 4
                data[dst_start : dst_start + copy_w * 4] = frame[
                    src_start : src_start + copy_w * 4
                ]

            # Edge clamping for out-of-bounds areas
            # For each side (top, bottom, left, right) that is outside crop,
            # replicate the nearest row/column of pixels.
            # Top padding
            if exp_y0 < 0:
                # First valid row is at dst_y0
                first_valid_row = dst_y0
                for y in range(first_valid_row):
                    src_y = 0  # top edge of crop
                    src_start = src_y * stride + src_x0 * 4
                    dst_start = y * expanded_size * 4 + dst_x0 * 4
                    data[dst_start : dst_start + copy_w * 4] = frame[
                        src_start : src_start + copy_w * 4
                    ]
            # Bottom padding
            if exp_y0 + expanded_size > crop_height:
                last_valid_y = crop_height - 1
                last_valid_row = dst_y0 + copy_h - 1
                for y in range(last_valid_row + 1, expanded_size):
                    src_start = last_valid_y * stride + src_x0 * 4
                    dst_start = y * expanded_size * 4 + dst_x0 * 4
                    data[dst_start : dst_start + copy_w * 4] = frame[
                        src_start : src_start + copy_w * 4
                    ]
            # Left padding
            if exp_x0 < 0:
                for y in range(expanded_size):
                    dst_start = y * expanded_size * 4 + 0
                    # replicate first column of the valid region
                    src_col = src_x0
                    src_start = (
                        min(max(exp_y0 + y, 0), crop_height - 1)
                    ) * stride + src_col * 4
                    for x in range(dst_x0):
                        data[dst_start + x * 4 : dst_start + x * 4 + 4] = frame[
                            src_start : src_start + 4
                        ]
            # Right padding
            if exp_x0 + expanded_size > crop_width:
                for y in range(expanded_size):
                    dst_start = y * expanded_size * 4 + (dst_x0 + copy_w) * 4
                    src_col = crop_width - 1
                    src_y = min(max(exp_y0 + y, 0), crop_height - 1)
                    src_start = src_y * stride + src_col * 4
                    for x in range(expanded_size - (dst_x0 + copy_w)):
                        data[dst_start + x * 4 : dst_start + x * 4 + 4] = frame[
                            src_start : src_start + 4
                        ]

            result.append((tx, ty, bytes(data), dst_x0, dst_y0))

        return result

    # ------------------------------------------------------------------
    #  Tile processing (main entry point)
    # ------------------------------------------------------------------
    def process_tiles(
        self, dirty_tiles: List[Tuple[int, int, bytes, int, int]]
    ) -> None:
        """
        Process a batch of expanded dirty tiles using multi-layer array textures.

        The batch is limited to `self.max_layers`. Each tile is assigned a
        unique layer index, uploaded to the corresponding slice of the input
        array, and processed concurrently. The final pass writes the valid
        interior region directly to the full output texture.

        Args:
            dirty_tiles: List of (tile_x, tile_y, data_bytes, valid_x, valid_y)
                as returned by `extract_expanded_tiles`.
        """
        if not dirty_tiles:
            return

        # Limit batch size to maximum number of layers.
        batch = dirty_tiles[: self.max_layers]
        num_tiles = len(batch)

        expected_data_size = self.expanded_tile_size * self.expanded_tile_size * 4
        total_staging = num_tiles * expected_data_size

        # Ensure staging buffer is large enough.
        if self.staging.size < total_staging:
            self.staging = Buffer(total_staging, heap_type=HEAP_UPLOAD)

        full_out_w = self.crop_width * 2
        full_out_h = self.crop_height * 2

        uploads = []
        tile_batch = []  # (tx, ty, layer, push_data)

        for layer_idx, (tx, ty, data, valid_x, valid_y) in enumerate(batch):
            # Guarantee data length matches expected size.
            if len(data) != expected_data_size:
                logger.warning(f"Tile ({tx},{ty}) size mismatch, adjusting.")
                if len(data) < expected_data_size:
                    data += b"\x00" * (expected_data_size - len(data))
                else:
                    data = data[:expected_data_size]

            # Upload tile data to layer `layer_idx` of the input array.
            uploads.append(
                (
                    data,
                    0,
                    0,
                    self.expanded_tile_size,
                    self.expanded_tile_size,
                    layer_idx,
                )
            )

            # Compute source and destination offsets.
            src_x = tx * self.tile_size
            src_y = ty * self.tile_size
            dst_x = tx * self.tile_size * (4 if self.double_upscale else 2)
            dst_y = ty * self.tile_size * (4 if self.double_upscale else 2)

            # Scale the input‑pixel offsets to output‑pixel space
            scale = 4 if self.double_upscale else 2
            valid_x_out = valid_x * scale
            valid_y_out = valid_y * scale

            push_data = struct.pack(
                "IIIIIIIIIII",
                layer_idx,  # inputLayer
                src_x,
                src_y,  # srcOffset
                dst_x,
                dst_y,  # dstOffset
                self.crop_width,
                self.crop_height,
                full_out_w,
                full_out_h,
                valid_x_out,
                valid_y_out,  # validOffset in output pixels
            )
            tile_batch.append((tx, ty, layer_idx, push_data))

        # Upload all tiles to their respective layers.
        self.input_tex.upload_subresources(uploads)

        # Build and execute dispatch sequence
        dispatches = self._build_dispatch_sequence(tile_batch)
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)


# ----------------------------------------------------------------------
#  CachedTileProcessor – LRU cache with atlas textures
# ----------------------------------------------------------------------
class CachedTileProcessor(TileProcessor):
    """
    Tile processing with an LRU cache.

    Uses an atlas of layers (capacity = cache size) to store input/output
    tiles. Tiles are uploaded and computed only on cache misses. All tiles
    (hits + misses) are copied from the output atlas to the final 2D texture.

    Note: Margin support for cached mode is not yet implemented; the
    `tile_context_margin` parameter is ignored.
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
        tile_context_margin: int = 0,  # ignored for now
    ):
        # Cached mode currently ignores margin; pass 0 to base.
        super().__init__(
            crop_width,
            crop_height,
            model_name,
            double_upscale,
            tile_size,
            variant="_tile",
            push_constant_size=8,  # inputLayer + outputLayer
            tile_context_margin=0,
            max_layers=cache_capacity,  # atlas capacity = max concurrent tiles
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

        # Reference to the output atlas for final copy.
        self.final_atlas = self.stages[-1].outputs["output"]

    def _create_stages(self) -> None:
        """Create SRCNN stages with texture atlases (array layers = capacity)."""
        # Input atlas shared across stages.
        input_atlas = Texture2D(
            self.tile_size, self.tile_size, slices=self.cache_capacity
        )

        # Stage 1.
        inter_atlas = Texture2D(
            self.tile_out_w_first, self.tile_out_h_first, slices=self.cache_capacity
        )
        outputs1 = {"output": inter_atlas}
        for i in range(self.factory.config.num_textures):
            outputs1[f"t{i}"] = Texture2D(
                self.tile_out_w_first,
                self.tile_out_h_first,
                slices=self.cache_capacity,
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
            # Stage 2.
            output_atlas = Texture2D(
                self.tile_out_w_final,
                self.tile_out_h_final,
                slices=self.cache_capacity,
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
            self.groups_per_stage[0] = dispatch_groups(
                self.tile_out_w_final, self.tile_out_h_final, last_pass=True
            )

        self.input_atlas = input_atlas

    def total_tiles(self) -> int:
        """Total number of tile grid cells in the crop area."""
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty: int) -> bool:
        """Return True if the number of dirty tiles is below the threshold."""
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

        misses = []
        hits = []
        for tx, ty, tile_hash, data in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, tile_hash)
            if was_cached:
                hits.append((tx, ty, layer))
            else:
                misses.append((tx, ty, layer, data))

        # Upload misses to the input atlas.
        upload_list = [
            (data, 0, 0, self.tile_size, self.tile_size, layer)
            for _, _, layer, data in misses
        ]
        if upload_list:
            self.input_atlas.upload_subresources(upload_list)

        # Build dispatches for misses.
        tile_batch = [
            (tx, ty, layer, struct.pack("II", layer, layer))
            for tx, ty, layer, _ in misses
        ]
        dispatches = self._build_dispatch_sequence(tile_batch)
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

        # Copy all tiles (hits + misses) from final atlas to output texture.
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
