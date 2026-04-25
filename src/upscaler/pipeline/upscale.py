import logging
from typing import List, Optional, Tuple, Union

from ..config import Config, PROCESSING_MODES
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..tile import CachedTileProcessor, TileProcessor
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class UpscalerManager:
    """
    Manages SRCNN upscaling in full-frame, tile, or cached-tile mode.

    The manager always creates full-frame resources (input texture, staging
    buffer, and SRCNN stages) to enable seamless fallback when tile mode cannot
    handle a frame efficiently (e.g., too many dirty tiles). In tile-based
    modes, it also instantiates a `TileProcessor` or `CachedTileProcessor`
    and delegates the actual tile processing to it.

    All configuration values are read directly from the `Config` object
    stored in `self.config`.  This means that changes to the config (e.g.
    `area_threshold`, `model`) are picked up immediately for subsequent
    frames, while structural changes (tile size, upscaling model) require
    a pipeline recreation (already handled by `Pipeline.recreate_upscaler()`).
    """

    def __init__(self, config: Config, crop_width: int, crop_height: int) -> None:
        if config.processing_mode not in PROCESSING_MODES:
            raise ValueError(
                f"Unknown mode '{config.processing_mode}'. Valid modes: {PROCESSING_MODES}"
            )

        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.mode = config.processing_mode
        self._first_tile_frame = True

        # Pre‑compute total number of tiles for quick fallback decisions
        self.tiles_x = (crop_width + config.tile_size - 1) // config.tile_size
        self.tiles_y = (crop_height + config.tile_size - 1) // config.tile_size
        self.total_tiles = self.tiles_x * self.tiles_y

        # Full‑frame resources (always created – used for fallback & seeding)
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []
        self._init_full_mode()

        # Tile processor (only for tile‑based modes)
        self.tile_processor: Optional[Union[TileProcessor, CachedTileProcessor]] = None
        if self.mode == "tile":
            self._init_tile_mode()
        elif self.mode == "cache":
            self._init_cache_mode()

        logger.info(
            "UpscalerManager initialized: mode=%s, crop=%dx%d, tile_size=%d, "
            "margin=%d, tiles=%sx%s (%d total)",
            self.mode,
            crop_width,
            crop_height,
            config.tile_size,
            config.tile_context_margin,
            self.tiles_x,
            self.tiles_y,
            self.total_tiles,
        )

    # ----------------------------------------------------------------------
    # Initialization helpers
    # ----------------------------------------------------------------------
    def _init_full_mode(self) -> None:
        """Set up full‑frame upscaling (one or two SRCNN stages)."""
        model_config = load_cunny_model(self.config.model, variant="")
        factory = PipelineFactory(model_config)

        in_w, in_h = self.crop_width, self.crop_height
        out_w_first = in_w * 2
        out_h_first = in_h * 2

        self.input = Texture2D(in_w, in_h)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)

        # Intermediate texture for first stage output
        inter_tex = Texture2D(out_w_first, out_h_first)
        outputs1 = {"output": inter_tex}
        for i in range(model_config.num_textures):
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

        if self.config.double_upscale:
            out_w_final = out_w_first * 2
            out_h_final = out_h_first * 2
            self.output = Texture2D(out_w_final, out_h_final)

            outputs2 = {"output": self.output}
            for i in range(model_config.num_textures):
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

    def _init_tile_mode(self) -> None:
        self.tile_processor = TileProcessor(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

    def _init_cache_mode(self) -> None:
        self.tile_processor = CachedTileProcessor(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

    def _rebind_full_frame_output(self) -> None:
        """Update the full‑frame SRCNN stages to write into the current output."""
        if not self.full_stages:
            return
        stage_idx = -1 if self.config.double_upscale else 0
        old_stage = self.full_stages[stage_idx]
        factory = old_stage.factory
        new_outputs = dict(old_stage.outputs)
        new_outputs["output"] = self.output
        new_stage = SRCNN(
            factory=factory,
            width=old_stage.width,
            height=old_stage.height,
            input_texture=old_stage.input,
            output_textures=new_outputs,
            push_constant_size=old_stage.push_constant_size,
        )
        self.full_stages[stage_idx] = new_stage
        logger.debug("Full‑frame output texture rebound to current active output")

    # ----------------------------------------------------------------------
    # Full‑frame processing (used for fallback and first tile frame)
    # ----------------------------------------------------------------------
    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        margin: int,
    ) -> None:
        """
        Upload full‑frame or partial damage regions to the input texture.

        When `use_damage_tracking` is True and the total expanded damage area
        is below `area_threshold`, only those regions are uploaded.
        """
        if use_damage_tracking and rects:
            expanded = TileProcessor.expand_damage_rects(
                rects, self.crop_width, self.crop_height, margin
            )
            total_area = sum(w * h for _, _, w, h in expanded)
            threshold_area = (
                self.config.area_threshold * self.crop_width * self.crop_height
            )
            if total_area <= threshold_area:
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
        """Execute the compute dispatches for the full frame."""
        for srnn, (gx, gy) in zip(self.full_stages, self.full_groups):
            srnn.dispatch(gx, gy, 1)

    # ----------------------------------------------------------------------
    # Early fallback decision (avoids expensive tile extraction)
    # ----------------------------------------------------------------------
    def _count_dirty_tile_cells(
        self, rects: List[Tuple[int, int, int, int, int]]
    ) -> int:
        """
        Return the number of unique tile grid cells that overlap any *raw* damage
        rectangle (no margin added). This matches the tile extraction logic.
        """
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
        Returns True if tile processing should be skipped in favor of full-frame.

        Decision is based on:
          - Number of *dirty tile cells* (raw rectangles, no margin).
          - Total expanded pixel area (damage expanded by context margin).
        """
        dirty_tile_count = self._count_dirty_tile_cells(rects)

        # Area check uses expanded rectangles (captured region size)
        expanded = TileProcessor.expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.config.tile_context_margin
        )
        total_area = sum(w * h for _, _, w, h in expanded)
        threshold_area = self.config.area_threshold * self.crop_width * self.crop_height

        # Tile capacity limits
        if self.mode == "tile":
            tile_limit = self.config.max_tile_layers
        else:  # cache
            tile_limit = self.config.cache_capacity

        return (dirty_tile_count >= tile_limit) or (total_area > threshold_area)

    # ----------------------------------------------------------------------
    # Tile mode entry point
    # ----------------------------------------------------------------------
    def should_use_tile_mode(self, rects: List[Tuple[int, int, int, int, int]]) -> bool:
        """
        Determine whether tile processing should be attempted for the current frame.

        - In direct tile mode: True if any damage is reported and the early
          fallback decision does **not** force full‑frame.
        - In cache mode: delegates to the cached processor's own heuristic,
          also augmented by the early fallback.
        """
        if not rects:
            return False

        if self.mode == "cache":
            # The cached processor may have its own logic; we add the early
            # fallback as an additional safety net.
            if self._should_fallback(rects):
                return False
            return self.tile_processor.should_use_tile_mode(len(rects))
        else:
            return not self._should_fallback(rects)

    def process_tile_frame(
        self,
        dirty_tiles: Union[
            List[
                Tuple[int, int, bytes, int, int]
            ],  # tile mode (tx,ty,data,valid_x,valid_y)
            List[Tuple[int, int, int, bytes]],  # cache mode (tx,ty,hash,data)
        ],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process a frame using the active tile processor.

        On the first tile frame a full capture is forced to seed the output.
        For subsequent frames, if the early fallback decision triggers (too many
        dirty tiles or too large area), the frame is processed in full‑frame mode
        without extracting individual tiles.
        """
        if self.mode not in ("tile", "cache"):
            raise RuntimeError("process_tile_frame called in non‑tile mode")

        # –– First tile frame: seed the output with a full‑frame pass ––
        if self._first_tile_frame:
            logger.debug("First tile frame – performing initial full capture")
            self.upload_full_frame(
                frame=frame_data,
                rects=rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            self.process_full_frame()
            self._first_tile_frame = False
            return

        # –– Early fallback decision – avoids extracting tiles if we will
        #     end up using full‑frame anyway ––
        if self._should_fallback(rects):
            logger.debug("Early fallback to full‑frame (threshold exceeded)")
            self.upload_full_frame(
                frame=frame_data,
                rects=rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            self.process_full_frame()
            return

        # –– Update the residual texture (full frame with damage regions) ––
        self.tile_processor.upload_full_frame(frame_data, rects)

        # –– Delegate tile processing (extraction already happened in the
        #     caller, but we can still enforce a safety bound) ––
        # Safety check: if extraction somehow exceeded the layer capacity
        max_dirty = (
            self.config.max_tile_layers
            if self.mode == "tile"
            else self.config.cache_capacity
        )
        if len(dirty_tiles) > max_dirty:
            logger.warning(
                "Extracted %d tiles exceeds capacity %d – falling back to full‑frame",
                len(dirty_tiles),
                max_dirty,
            )
            self.upload_full_frame(
                frame_data, rects, False, self.config.tile_context_margin
            )
            self.process_full_frame()
            return

        self.tile_processor.process_tiles(dirty_tiles)

    # ----------------------------------------------------------------------
    # Output access
    # ----------------------------------------------------------------------
    def get_output_texture(self) -> Texture2D:
        """Return the final upscaled texture."""
        return self.output
