import logging
from typing import List, Optional, Tuple

from ..config import Config
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_model
from ..tiles import TileProcessor, expand_damage_rects
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class UpscalerManager:
    """
    Orchestrates SRCNN upscaling - full-frame or tile-based.

    Full-frame resources are always created, allowing seamless fallback when
    tile mode cannot process a frame efficiently. Tile mode is enabled by
    `config.use_tile_processing`.

    In tile mode, damage rectangles are **expanded by the context margin**
    before dirty-tile detection, ensuring that any change inside the
    convolutional receptive field triggers reprocessing and prevents seams.

    Attributes:
        use_tile (bool): Whether tile processing is active.
        tiles_x, tiles_y (int): Grid dimensions (for fallback decisions).
        input (Texture2D): Full low-res frame (uploaded every tile frame).
        staging (Buffer): Persistent staging buffer for full-frame uploads.
        output (Texture2D): Final upscaled image (from tile processor or full-frame).
        full_stages, full_groups: SRCNN stages and dispatch groups for full-frame path.
        tile_processor (TileProcessor | None): Active tile processor when enabled.
        _first_tile_frame (bool): Used to seed the output on the first tile frame.
    """

    def __init__(self, config: Config, crop_width: int, crop_height: int) -> None:
        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.use_tile = config.use_tile_processing

        # Grid size for fallback decisions
        self.tiles_x = (crop_width + config.tile_size - 1) // config.tile_size
        self.tiles_y = (crop_height + config.tile_size - 1) // config.tile_size
        self.total_tiles = self.tiles_x * self.tiles_y

        # Full-frame resources (always created)
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []
        self._init_full_mode()

        # Tile processor (only when tile mode is enabled)
        self.tile_processor: Optional[TileProcessor] = None
        self._first_tile_frame = True
        if self.use_tile:
            self._init_tile_mode()

        logger.info(
            "UpscalerManager ready: tile_mode=%s, crop=%dx%d, tile=%d, margin=%d, "
            "grid=%dx%d (%d tiles)",
            self.use_tile,
            crop_width,
            crop_height,
            config.tile_size,
            config.tile_context_margin,
            self.tiles_x,
            self.tiles_y,
            self.total_tiles,
        )

    # ------------------------------------------------------------------
    #  Initialization helpers
    # ------------------------------------------------------------------

    def _init_full_mode(self) -> None:
        """Build full-frame SRCNN pipelines (one or two stages)."""
        model_config = load_model(self.config.model, variant="")
        factory = PipelineFactory(model_config)

        # Intermediate texture format from the model (e.g. rgba16f)
        fmt = model_config.intermediate_format

        # Collect all intermediate UAV names from every pass (excluding "output")
        intermediate_names = {
            name
            for srv_list, uav_list in model_config.srv_uav
            for name in uav_list
            if name != "output"
        }

        # Create the textures for the *first* stage (native resolution)
        self._intermediate_textures = {
            name: Texture2D(self.crop_width, self.crop_height, format=fmt)
            for name in intermediate_names
        }

        in_w, in_h = self.crop_width, self.crop_height
        out_first_w, out_first_h = in_w * 2, in_h * 2

        self.input = Texture2D(in_w, in_h)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)

        # First stage output (2x)
        inter_tex = Texture2D(out_first_w, out_first_h, format=fmt)
        outputs1 = self._intermediate_textures
        outputs1["output"] = inter_tex

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

        if self.config.double_upscale:
            out_final_w, out_final_h = out_first_w * 2, out_first_h * 2
            self.output = Texture2D(out_final_w, out_final_h)

            # Second stage intermediate textures - same names, but at 2x resolution
            outputs2 = {
                name: Texture2D(out_first_w, out_first_h, format=fmt)
                for name in intermediate_names
            }
            outputs2["output"] = self.output  # final output at 4x

            srnn2 = SRCNN(
                factory=factory,
                width=out_first_w,
                height=out_first_h,
                input_texture=inter_tex,
                output_textures=outputs2,
                push_constant_size=0,
            )
            self.full_stages.append(srnn2)
            self.full_groups.append(
                dispatch_groups(out_first_w, out_first_h, last_pass=False)
            )
        else:
            # Single stage: reuse the intermediate texture as final output
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

    def _init_tile_mode(self) -> None:
        """Create the tile processor and redirect the full-frame output."""
        self.tile_processor = TileProcessor(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

        if self.config.double_upscale:
            # Cache references needed for 2x residual generation
            self._residual_upscale_groups = self.full_groups[0]
            self._residual_src_tex = self.input  # 1x input
            self._residual_dst_tex = self.full_stages[0].outputs[
                "output"
            ]  # 2x intermediate

    def _rebind_full_frame_output(self) -> None:
        """Point the last full-frame stage at the current active output texture."""
        if not self.full_stages:
            return
        stage_idx = -1 if self.config.double_upscale else 0
        old_stage = self.full_stages[stage_idx]
        new_outputs = dict(old_stage.outputs)
        new_outputs["output"] = self.output
        self.full_stages[stage_idx] = SRCNN(
            factory=old_stage.factory,
            width=old_stage.width,
            height=old_stage.height,
            input_texture=old_stage.input,
            output_textures=new_outputs,
            push_constant_size=old_stage.push_constant_size,
        )
        logger.debug("Full-frame output rebound to current output")

    # ------------------------------------------------------------------
    #  Full-frame upload helpers
    # ------------------------------------------------------------------

    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        margin: int,
    ) -> None:
        """
        Upload the current frame (or damage regions) to `self.input`.

        When `use_damage_tracking` is True and the total expanded damage area
        is below the configured threshold, only the expanded rectangles are
        uploaded. Otherwise the entire frame is uploaded via the staging buffer.
        """
        if use_damage_tracking and rects:
            expanded = expand_damage_rects(
                rects, self.crop_width, self.crop_height, margin
            )
            total_area = sum(w * h for _, _, w, h in expanded)
            threshold = self.config.area_threshold * self.crop_width * self.crop_height
            if total_area <= threshold:
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
                return

        self.staging.upload(frame)
        self.staging.copy_to(self.input)

    def process_full_frame(self) -> None:
        """Execute all full-frame compute dispatches."""
        for srnn, (gx, gy) in zip(self.full_stages, self.full_groups):
            srnn.dispatch(gx, gy, 1)

    # ------------------------------------------------------------------
    #  Fallback decision (rect-based)
    # ------------------------------------------------------------------

    def _count_dirty_tile_cells(
        self, rects: List[Tuple[int, int, int, int, int]]
    ) -> int:
        """Number of unique tile cells overlapped by raw damage rectangles."""
        tile_size = self.config.tile_size
        tiles = set()
        for rx, ry, rw, rh, _ in rects:
            tx0 = rx // tile_size
            ty0 = ry // tile_size
            tx1 = min(self.tiles_x, (rx + rw + tile_size - 1) // tile_size)
            ty1 = min(self.tiles_y, (ry + rh + tile_size - 1) // tile_size)
            for ty in range(ty0, ty1):
                for tx in range(tx0, tx1):
                    tiles.add((tx, ty))
        return len(tiles)

    def _should_fallback(self, rects: List[Tuple[int, int, int, int, int]]) -> bool:
        """
        True if tile processing should be skipped in favour of a full-frame pass.

        Decision is based on:
        - number of dirty tile cells (raw rectangles) ≥ max_tile_layers
        - total expanded pixel area > area_threshold x total crop area
        """
        if self._count_dirty_tile_cells(rects) >= self.config.max_tile_layers:
            return True

        expanded = expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.config.tile_context_margin
        )
        total_area = sum(w * h for _, _, w, h in expanded)
        threshold = self.config.area_threshold * self.crop_width * self.crop_height
        return total_area > threshold

    def should_use_tile_mode(self, rects: List[Tuple[int, int, int, int, int]]) -> bool:
        """Return True if tile mode should be attempted for this frame."""
        return bool(rects) and not self._should_fallback(rects)

    # ------------------------------------------------------------------
    #  Tile-frame processing (single or double upscale)
    # ------------------------------------------------------------------

    def process_tile_frame(
        self,
        dirty_tiles: List[Tuple[int, int, bytes, int, int]],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process one frame via the tile processor.

        On the very first tile frame, a full-frame pass seeds the output.
        After that, the method decides whether to:

        1. **Fall back to full-frame** (if too many dirty tiles or too
           much expanded area) - entire output is refreshed.
        2. **Process tiles** - fresh low-res data is uploaded to
           `self.input`, the residual texture(s) are updated, and the
           dirty tiles are dispatched.

        For 4x upscaling (double stage), the 2x residual is generated
        from the freshly uploaded 1x input before the tile dispatches.
        """
        if not self.use_tile:
            raise RuntimeError("process_tile_frame called when tile mode is disabled")

        # ------------------------------------------------------------------
        # First tile frame: seed the output with a full-frame pass
        # ------------------------------------------------------------------
        if self._first_tile_frame:
            logger.debug("First tile frame - performing full capture")

            # Populate residual_1x with the whole low-res frame
            payload = bytes(frame_data)
            self.tile_processor.residual_1x.upload_subresources(
                [(payload, 0, 0, self.crop_width, self.crop_height, 0)]
            )
            # Full-frame upscale to obtain a complete output
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            self.process_full_frame()
            self._first_tile_frame = False
            return

        # ------------------------------------------------------------------
        # Fallback check (before extraction to avoid wasted work)
        # ------------------------------------------------------------------
        if self._should_fallback(rects):
            logger.debug("Fallback to full-frame (threshold exceeded)")

            # Update residual_1x so tile mode later has a fresh base
            payload = bytes(frame_data)
            self.tile_processor.residual_1x.upload_subresources(
                [(payload, 0, 0, self.crop_width, self.crop_height, 0)]
            )
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            self.process_full_frame()
            return

        # ------------------------------------------------------------------
        # Safety net - if the extraction produced more tiles than capacity
        # ------------------------------------------------------------------
        max_layers = self.config.max_tile_layers
        if len(dirty_tiles) > max_layers:
            logger.warning(
                "Extracted %d tiles > capacity %d - fallback to full-frame",
                len(dirty_tiles),
                max_layers,
            )
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            self.process_full_frame()
            return

        # ------------------------------------------------------------------
        # Actual tile processing
        # ------------------------------------------------------------------
        if self.config.double_upscale:
            # Upload full frame to self.input (needed for 1x to 2x residual)
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )

            # Run stage1 to produce a fresh 2x residual
            gx, gy = self._residual_upscale_groups
            self.full_stages[0].dispatch(gx, gy, 1)

            # Copy the 2x result to the tile processor’s residual_2x
            self._residual_dst_tex.copy_to(
                self.tile_processor.residual_2x,
                width=self.crop_width * 2,
                height=self.crop_height * 2,
            )
        else:
            # Upload the whole low-res frame to self.input (used as tile source)
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )

            # Keep residual_1x up-to-date (final pass uses it)
            self.tile_processor.residual_staging.upload(frame_data)
            self.tile_processor.residual_staging.copy_to(
                self.tile_processor.residual_1x,
            )

        # Dispatch the dirty tiles
        self.tile_processor.process_tiles(dirty_tiles)

    # ------------------------------------------------------------------
    #  Output access
    # ------------------------------------------------------------------

    def get_output_texture(self) -> Texture2D:
        """Return the final upscaled texture (tile-processor or full-frame)."""
        return self.output
