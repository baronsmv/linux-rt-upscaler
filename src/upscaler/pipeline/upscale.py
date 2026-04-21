import logging
from typing import List, Optional, Tuple, Union

import xxhash

from .tiles import OffsetTileProcessor, CachedTileProcessor
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class UpscalerManager:
    """
    Manages SRCNN upscaling in full-frame, offset-tile, or cached-tile mode.

    The manager is responsible for:
        - Creating and configuring the SRCNN stages (1 for 2x, 2 for 4x).
        - Handling frame uploads (full or partial damage regions).
        - Dispatching compute work.
        - Providing the final upscaled texture.

    Tile-based modes delegate to `TileProcessor` subclasses, which are
    instantiated with the shared pipeline factory.

    Attributes:
        mode (str): The active processing mode ("full", "offset", "cache").
        output (Texture2D): The final upscaled texture (full frame).
        staging (Buffer): Staging buffer for full-frame uploads (full mode only).
        input (Texture2D): Input texture for full-frame mode.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        tile_context_margin: int,
        cache_capacity: int,
        cache_threshold: float,
        mode: str = "full",
    ) -> None:
        """
        Initialize the upscaler manager.

        Args:
            crop_width: Width of the captured crop area (pixels).
            crop_height: Height of the captured crop area (pixels).
            model_name: Name of the CuNNy model subdirectory (e.g., "fast").
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal input tile size for tile-based modes.
            tile_context_margin: Extra border pixels for convolution context.
            cache_capacity: Maximum number of tiles stored in cache mode.
            cache_threshold: Fraction of total tiles above which full-frame is used.
            mode: Processing mode. Must be one of "full", "offset", "cache".
        """
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.tile_context_margin = tile_context_margin
        self.double_upscale = double_upscale

        if mode not in ("full", "offset", "cache"):
            raise ValueError(f"Unknown mode: {mode}")

        self.mode = mode

        # Full-frame specific resources (populated in _init_full_mode)
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []

        # Tile processor instance (for offset/cache modes)
        self.tile_processor: Optional[
            Union[OffsetTileProcessor, CachedTileProcessor]
        ] = None

        if mode == "full":
            self._init_full_mode(model_name)
        elif mode == "offset":
            self._init_offset_mode(model_name)
        else:  # mode == "cache"
            self._init_cache_mode(model_name, cache_capacity, cache_threshold)

        logger.info(
            f"UpscalerManager initialized: mode={mode}, crop={crop_width}x{crop_height}"
        )

    # ----------------------------------------------------------------------
    # Initialization helpers
    # ----------------------------------------------------------------------
    def _init_full_mode(self, model_name: str) -> None:
        """Set up full-frame upscaling (one or two SRCNN stages)."""
        config = load_cunny_model(model_name, variant="")
        factory = PipelineFactory(config)

        in_w, in_h = self.crop_width, self.crop_height
        out_w_first = in_w * 2
        out_h_first = in_h * 2

        self.input = Texture2D(in_w, in_h)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)

        inter_tex = Texture2D(out_w_first, out_h_first)
        outputs1 = {"output": inter_tex}
        for i in range(config.num_textures):
            outputs1[f"t{i}"] = Texture2D(in_w, in_h)

        srnn1 = SRCNN(
            factory=factory,
            width=in_w,
            height=in_h,
            input_texture=self.input,
            output_textures=outputs1,
            push_constant_size=0,
        )
        self.full_stages.append(srnn1)
        self.full_groups.append(dispatch_groups(in_w, in_h, last_pass=False))

        if self.double_upscale:
            out_w_final = out_w_first * 2
            out_h_final = out_h_first * 2
            self.output = Texture2D(out_w_final, out_h_final)

            outputs2 = {"output": self.output}
            for i in range(config.num_textures):
                outputs2[f"t{i}"] = Texture2D(out_w_first, out_h_first)

            srnn2 = SRCNN(
                factory=factory,
                width=out_w_first,
                height=out_h_first,
                input_texture=inter_tex,
                output_textures=outputs2,
                push_constant_size=0,
            )
            self.full_stages.append(srnn2)
            self.full_groups.append(
                dispatch_groups(out_w_first, out_h_first, last_pass=False)
            )
        else:
            self.output = inter_tex
            outputs1["output"] = self.output
            self.full_stages[0] = SRCNN(
                factory=factory,
                width=in_w,
                height=in_h,
                input_texture=self.input,
                output_textures=outputs1,
                push_constant_size=0,
            )

    def _init_offset_mode(self, model_name: str) -> None:
        """Set up offset-tile mode (no cache)."""
        self.tile_processor = OffsetTileProcessor(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=model_name,
            double_upscale=self.double_upscale,
            tile_size=self.tile_size,
            tile_context_margin=self.tile_context_margin,
        )
        self.output = self.tile_processor.output_texture

    def _init_cache_mode(
        self, model_name: str, cache_capacity: int, cache_threshold: float
    ) -> None:
        """Set up cached-tile mode."""
        self.tile_processor = CachedTileProcessor(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=model_name,
            double_upscale=self.double_upscale,
            tile_size=self.tile_size,
            cache_capacity=cache_capacity,
            cache_threshold=cache_threshold,
        )
        self.output = self.tile_processor.output_texture

    # ----------------------------------------------------------------------
    # Full-frame mode API
    # ----------------------------------------------------------------------
    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        margin: int,
    ) -> None:
        """
        Upload full-frame (or partial damage regions) to the input texture.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber (x, y, w, h, hash).
            use_damage_tracking: If True, upload only the expanded damage regions.
            margin: Number of pixels to expand each damage rectangle.
        """
        if self.mode != "full":
            raise RuntimeError("upload_full_frame called in non-full mode")

        if use_damage_tracking and rects:
            expanded = self._expand_damage_rects(rects, margin)
            uploads = []
            stride = self.crop_width * 4
            for ex, ey, ew, eh in expanded:
                sub_data = bytearray(ew * eh * 4)
                for row in range(eh):
                    src_start = (ey + row) * stride + ex * 4
                    dst_start = row * ew * 4
                    sub_data[dst_start : dst_start + ew * 4] = frame[
                        src_start : src_start + ew * 4
                    ]
                uploads.append((bytes(sub_data), ex, ey, ew, eh))
            self.input.upload_subresources(uploads)
        else:
            self.staging.upload(frame)
            self.staging.copy_to(self.input)

    def process_full_frame(self) -> None:
        """Execute the compute dispatches for the full frame."""
        if self.mode != "full":
            raise RuntimeError("process_full_frame called in non-full mode")

        for srnn, (gx, gy) in zip(self.full_stages, self.full_groups):
            srnn.dispatch(gx, gy, 1)

    # ----------------------------------------------------------------------
    # Tile mode API
    # ----------------------------------------------------------------------
    def extract_dirty_tiles(
        self, rects: List[Tuple[int, int, int, int, int]], frame: memoryview
    ) -> List[Tuple[int, int, bytes, int, int]]:
        """
        Convert damage rectangles to expanded tile data with margin.

        Delegates to the static method of OffsetTileProcessor.

        Returns:
            List of (tile_x, tile_y, data_bytes, valid_x, valid_y).
        """
        return OffsetTileProcessor.extract_expanded_tiles(
            frame=frame,
            rects=rects,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            tile_size=self.tile_size,
            margin=self.tile_context_margin,
        )

    def extract_dirty_tiles_with_hash(
        self, rects: List[Tuple[int, int, int, int, int]], frame: memoryview
    ) -> List[Tuple[int, int, int, bytes]]:
        """
        Convert damage rectangles to tile data with content hash.

        Used by cache mode. The hash is computed on the valid pixels only.

        Args:
            rects: Damage rectangles (x, y, w, h, hash).
            frame: Raw BGRA pixel data for the entire crop area.

        Returns:
            List of (tile_x, tile_y, hash, data_bytes).
        """
        stride = self.crop_width * 4
        tile_w = self.tile_size
        tile_h = self.tile_size
        tiles_x = (self.crop_width + tile_w - 1) // tile_w
        tiles_y = (self.crop_height + tile_h - 1) // tile_h

        dirty_tiles = set()
        for rx, ry, rw, rh, _ in rects:
            tx0 = rx // tile_w
            ty0 = ry // tile_h
            tx1 = (rx + rw + tile_w - 1) // tile_w
            ty1 = (ry + rh + tile_h - 1) // tile_h
            for ty in range(ty0, min(ty1, tiles_y)):
                for tx in range(tx0, min(tx1, tiles_x)):
                    dirty_tiles.add((tx, ty))

        result = []
        for tx, ty in dirty_tiles:
            x = tx * tile_w
            y = ty * tile_h
            w = min(tile_w, self.crop_width - x)
            h = min(tile_h, self.crop_height - y)

            valid_data = bytearray()
            for row in range(h):
                src_start = (y + row) * stride + x * 4
                valid_data.extend(frame[src_start : src_start + w * 4])
            tile_hash = xxhash.xxh64(valid_data).intdigest()

            full_data = bytearray(tile_w * tile_h * 4)
            for row in range(h):
                src_start = (y + row) * stride + x * 4
                dst_start = row * tile_w * 4
                full_data[dst_start : dst_start + w * 4] = frame[
                    src_start : src_start + w * 4
                ]

            result.append((tx, ty, tile_hash, bytes(full_data)))

        return result

    def process_tile_frame(
        self,
        dirty_tiles: Union[
            List[Tuple[int, int, bytes, int, int]],  # offset mode
            List[Tuple[int, int, int, bytes]],  # cache mode
        ],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process a frame using the active tile processor.

        Args:
            dirty_tiles: Pre-extracted tile data (format depends on mode).
            rects: Original damage rectangles (needed by offset mode for
                uploading the residual texture).
            frame_data: Full captured frame (used by offset mode residual upload).
        """
        if self.mode not in ("offset", "cache"):
            raise RuntimeError("process_tile_frame called in non-tile mode")

        if self.mode == "offset":
            # Upload expanded damage regions to the residual texture.
            self.tile_processor.upload_full_frame(frame_data, rects)

        self.tile_processor.process_tiles(dirty_tiles)

    def should_use_tile_mode(self, num_dirty: int) -> bool:
        """
        Determine whether to use tile mode for the current frame.

        For offset mode, always returns True if there is damage.
        For cache mode, returns True if the number of dirty tiles is below
        the threshold fraction of total tiles.

        Args:
            num_dirty: Number of dirty rectangles reported by FrameGrabber.

        Returns:
            True if tile processing should be used, False otherwise.
        """
        if self.mode == "offset":
            return num_dirty > 0
        elif self.mode == "cache":
            return self.tile_processor.should_use_tile_mode(num_dirty)
        return False

    # ----------------------------------------------------------------------
    # Output
    # ----------------------------------------------------------------------
    def get_output_texture(self) -> Texture2D:
        """Return the final upscaled texture."""
        return self.output

    # ----------------------------------------------------------------------
    # Internal utilities
    # ----------------------------------------------------------------------
    def _expand_damage_rects(
        self, rects: List[Tuple[int, int, int, int, int]], margin: int
    ) -> List[Tuple[int, int, int, int]]:
        """
        Expand damage rectangles by a margin, clamped to crop bounds.

        Args:
            rects: Original damage rectangles (x, y, w, h, hash).
            margin: Number of pixels to expand on each side.

        Returns:
            List of expanded rectangles (x, y, width, height).
        """
        expanded = []
        for rx, ry, rw, rh, _ in rects:
            ex0 = max(0, rx - margin)
            ey0 = max(0, ry - margin)
            ex1 = min(self.crop_width, rx + rw + margin)
            ey1 = min(self.crop_height, ry + rh + margin)
            if ex1 > ex0 and ey1 > ey0:
                expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))
        return expanded
