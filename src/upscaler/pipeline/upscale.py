import logging
from typing import List, Optional, Tuple, Union

from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..tile import CachedTileProcessor, TileProcessor
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD, device_wait_idle

logger = logging.getLogger(__name__)


class UpscalerManager:
    """
    Manages SRCNN upscaling in full-frame, tile, or cached-tile mode.

    The manager always creates full-frame resources (input texture, staging
    buffer, and SRCNN stages) to enable seamless fallback when tile mode cannot
    handle a frame efficiently (e.g., too many dirty tiles). In tile-based
    modes, it also instantiates a `TileProcessor` or `CachedTileProcessor`
    and delegates the actual tile processing to it.

    Attributes:
        crop_width (int): Width of the captured crop area in pixels.
        crop_height (int): Height of the captured crop area in pixels.
        tile_size (int): Nominal input tile size for tile-based modes.
        tile_context_margin (int): Extra border pixels for convolution context.
        double_upscale (bool): If True, perform 4x upscaling (two 2x stages).
        max_tiles_per_batch (int): Maximum concurrent tiles in tile mode.
        mode (str): Active processing mode ("full", "tile", "cache").
        output (Texture2D): Final upscaled texture (full frame).
        staging (Buffer): Staging buffer for full-frame uploads.
        input (Texture2D): Input texture for full-frame mode.
        full_stages (List[SRCNN]): SRCNN stages for full-frame processing.
        full_groups (List[Tuple[int, int]]): Dispatch groups for full-frame.
        tile_processor (Optional): Tile processor for tile/cache modes.
    """

    # Supported processing modes.
    VALID_MODES = ("full", "tile", "cache")

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
        max_tiles_per_batch: int = 16,
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
            mode: Processing mode. Must be one of "full", "tile", "cache".
            max_tiles_per_batch: Maximum concurrent tiles in tile mode.

        Raises:
            ValueError: If an invalid mode is provided.
        """
        if mode not in self.VALID_MODES:
            raise ValueError(f"Unknown mode '{mode}'. Valid modes: {self.VALID_MODES}")

        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.tile_context_margin = tile_context_margin
        self.double_upscale = double_upscale
        self.max_tiles_per_batch = max_tiles_per_batch
        self.mode = mode

        # Internal state.
        self._first_tile_frame = True

        # Full-frame resources (always created – used for fallback and first tile frame).
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []

        # Create full-frame pipeline.
        self._init_full_mode(model_name)

        # Tile processor (only for tile-based modes).
        self.tile_processor: Optional[Union[TileProcessor, CachedTileProcessor]] = None

        if mode == "tile":
            self._init_tile_mode(model_name)
        elif mode == "cache":
            self._init_cache_mode(model_name, cache_capacity, cache_threshold)

        logger.info(
            f"UpscalerManager initialized: mode={mode}, "
            f"crop={crop_width}x{crop_height}, tile_size={tile_size}, "
            f"margin={tile_context_margin}"
        )

    # ----------------------------------------------------------------------
    # Initialization helpers
    # ----------------------------------------------------------------------
    def _init_full_mode(self, model_name: str) -> None:
        """
        Set up full-frame upscaling (one or two SRCNN stages).

        This method creates the input texture, staging buffer, and all
        intermediate/output textures required for a full-frame upscale.
        The resulting stages are stored in `self.full_stages` and can be
        used directly or as a fallback.
        """
        config = load_cunny_model(model_name, variant="")
        factory = PipelineFactory(config)

        in_w, in_h = self.crop_width, self.crop_height
        out_w_first = in_w * 2
        out_h_first = in_h * 2

        # Input texture and staging buffer
        self.input = Texture2D(in_w, in_h)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)

        # Intermediate texture for the first stage output
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
            # Second stage for 4x upscaling
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
            # Single stage 2x upscaling
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

    def _init_tile_mode(self, model_name: str) -> None:
        """Instantiate the tile (non-cached) tile processor."""
        self.tile_processor = TileProcessor(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=model_name,
            double_upscale=self.double_upscale,
            tile_size=self.tile_size,
            tile_context_margin=self.tile_context_margin,
            max_layers=self.max_tiles_per_batch,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

    def _init_cache_mode(
        self, model_name: str, cache_capacity: int, cache_threshold: float
    ) -> None:
        """Instantiate the cached tile processor."""
        self.tile_processor = CachedTileProcessor(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=model_name,
            double_upscale=self.double_upscale,
            tile_size=self.tile_size,
            cache_capacity=cache_capacity,
            cache_threshold=cache_threshold,
            tile_context_margin=self.tile_context_margin,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

    def _rebind_full_frame_output(self) -> None:
        """
        Update the full-frame SRCNN stages to use the current `self.output`.

        When a tile processor replaces the output texture (e.g., with its own
        full-frame texture), the full-frame fallback pipeline must be updated
        to write to that same texture. This method recreates the final SRCNN
        stage(s) with the new output UAV.
        """
        if not self.full_stages:
            return

        # Determine which stage holds the final output UAV
        stage_idx = -1 if self.double_upscale else 0
        old_stage = self.full_stages[stage_idx]
        factory = old_stage.factory  # Shared PipelineFactory

        # Update the output dict to point to the new output texture
        new_outputs = dict(old_stage.outputs)
        new_outputs["output"] = self.output

        # Create a new SRCNN stage with the same inputs and updated outputs
        new_stage = SRCNN(
            factory=factory,
            width=old_stage.width,
            height=old_stage.height,
            input_texture=old_stage.input,
            output_textures=new_outputs,
            push_constant_size=old_stage.push_constant_size,
        )

        # Replace the old stage
        self.full_stages[stage_idx] = new_stage
        logger.debug("Full-frame output texture rebound to current active output")

    # ----------------------------------------------------------------------
    # Full-frame processing API (used for fallback and first tile frame)
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

        This method always uses the full-frame resources created at
        initialization. It supports either uploading the entire frame or
        only the expanded damage regions.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber (x, y, w, h, hash).
            use_damage_tracking: If True, upload only the expanded damage regions.
            margin: Number of pixels to expand each damage rectangle.
        """
        if use_damage_tracking and rects:
            # Expand damage rectangles and upload only those regions
            expanded = TileProcessor.expand_damage_rects(
                rects, self.crop_width, self.crop_height, margin
            )
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
            # Upload the entire frame
            self.staging.upload(frame)
            self.staging.copy_to(self.input)

    def process_full_frame(self) -> None:
        """
        Execute the compute dispatches for the full frame.

        This method uses the full-frame SRCNN stages created at initialization.
        It is used as a fallback when tile mode cannot handle the frame
        efficiently, and also for the first tile frame to prime the output.
        """
        for srnn, (gx, gy) in zip(self.full_stages, self.full_groups):
            srnn.dispatch(gx, gy, 1)

    # ----------------------------------------------------------------------
    # Tile mode entry point
    # ----------------------------------------------------------------------
    def process_tile_frame(
        self,
        dirty_tiles: Union[
            List[Tuple[int, int, bytes, int, int]],  # tile mode
            List[Tuple[int, int, int, bytes]],  # cache mode
        ],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process a frame using the active tile processor.

        This method implements the following logic:

        - On the very first tile frame, a full capture is performed to
          initialize the output texture. Subsequent frames only update
          dirty tiles.
        - In tile mode, if the number of dirty tiles exceeds
          `max_tiles_per_batch`, the frame is processed using the full-frame
          fallback instead.
        - In tile mode, the residual texture (`full_input_tex`) is updated
          with the expanded damage regions before tile processing.
        - The actual tile processing is delegated to `self.tile_processor`.

        Args:
            dirty_tiles: Pre-extracted tile data. Format depends on mode:
                - tile mode: (tile_x, tile_y, data_bytes, valid_x, valid_y)
                - cache mode:  (tile_x, tile_y, hash, data_bytes)
            rects: Original damage rectangles (used by tile mode for
                uploading the residual texture).
            frame_data: Full captured frame (used by tile mode for residual
                texture uploads).

        Raises:
            RuntimeError: If called when not in a tile-based mode.
        """
        if self.mode not in ("tile", "cache"):
            raise RuntimeError("process_tile_frame called in non-tile mode")

        # First tile frame: prime the output with a full capture.
        if self._first_tile_frame:
            logger.debug("First tile frame – performing initial full capture")
            self.upload_full_frame(
                frame=frame_data,
                rects=rects,
                use_damage_tracking=False,  # Upload whole frame.
                margin=self.tile_context_margin,
            )
            self.process_full_frame()
            device_wait_idle()
            self._first_tile_frame = False
            return

        # Direct mode specific: fallback if too many tiles, and residual upload.
        if self.mode == "tile":
            if len(dirty_tiles) > self.max_tiles_per_batch:
                logger.debug(
                    f"Too many dirty tiles ({len(dirty_tiles)} > "
                    f"{self.max_tiles_per_batch}), falling back to full-frame"
                )
                self.upload_full_frame(
                    frame=frame_data,
                    rects=rects,
                    use_damage_tracking=True,
                    margin=self.tile_context_margin,
                )
                self.process_full_frame()
                device_wait_idle()
                return

            # Update the residual texture with expanded damage regions.
            # This provides the network with the surrounding context.
            self.tile_processor.upload_full_frame(frame_data, rects)

        # Delegate tile processing to the tile processor.
        self.tile_processor.process_tiles(dirty_tiles)

    def should_use_tile_mode(self, num_dirty_rects: int) -> bool:
        """
        Determine whether tile mode should be used for the current frame.

        - In tile mode: tile mode is used whenever there is any damage
          (the fallback inside `process_tile_frame` will handle excessive
          tiles).
        - In cache mode: tile mode is used only if the number of dirty tiles
          is below the configured threshold (as determined by the cached
          processor).

        Args:
            num_dirty_rects: Number of damage rectangles reported by the grabber.

        Returns:
            True if tile processing should be attempted, False otherwise.
        """
        if self.mode == "tile":
            return num_dirty_rects > 0
        elif self.mode == "cache":
            return self.tile_processor.should_use_tile_mode(num_dirty_rects)
        return False

    # ----------------------------------------------------------------------
    # Output access
    # ----------------------------------------------------------------------
    def get_output_texture(self) -> Texture2D:
        """Return the final upscaled texture."""
        return self.output
