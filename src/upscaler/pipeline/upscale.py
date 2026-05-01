import logging
import struct
from typing import Dict, List, Optional, Tuple

from ..config import Config
from ..srcnn import (
    ModelConfig,
    PipelineFactory,
    SRCNN,
    dispatch_groups,
    load_model,
)
from ..tiles import TileProcessor, expand_damage_rects
from ..vulkan import Buffer, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
#  Constant buffer packing helper
# ----------------------------------------------------------------------
def _pack_cb(in_w: int, in_h: int, out_w: int, out_h: int) -> bytes:
    """Pack constant buffer data for SRCNN shaders."""
    return struct.pack(
        "IIIIffff",
        in_w,
        in_h,
        out_w,
        out_h,
        1.0 / in_w,
        1.0 / in_h,
        1.0 / out_w,
        1.0 / out_h,
    )


# ----------------------------------------------------------------------
#  Helper to collect all UAV names used by a model (excluding "output")
# ----------------------------------------------------------------------
def _collect_intermediate_names(model_cfg: ModelConfig) -> set:
    """Return a set of all UAV names used by the model, excluding 'output'."""
    return {
        name
        for srv_list, uav_list in model_cfg.srv_uav
        for name in uav_list
        if name != "output"
    }


# ======================================================================
#  UpscalerManager
# ======================================================================
class UpscalerManager:
    """
    Orchestrates full‑frame or tile‑based SRCNN upscaling for a single
    standard depth‑to‑space model.

    All supported models must have a scale factor of at least 2. The
    manager handles both a single 2× upscale and a double‑upscale (two
    chained 2× stages) for 4× output. Tile processing is available for
    2× upscaling when enabled in the configuration.

    Attributes:
        use_tile: Whether tile‑based processing is currently active.
        tiles_x, tiles_y: Tile grid dimensions (used for fallback decisions).
        input: Full low‑res frame texture (uploaded every frame).
        staging: Persistent staging buffer for full‑frame uploads.
        output: Final upscaled image texture.
        full_stages: List of :class:`SRCNN` stages for the full‑frame path.
        full_groups: Corresponding dispatch group sizes for each stage.
        tile_processor: Active :class:`TileProcessor` when tile mode is on.
    """

    def __init__(self, config: Config, crop_width: int, crop_height: int) -> None:
        """
        Initialize the upscaler manager.

        Args:
            config: Global application configuration.
            crop_width: Width of the captured crop area (pixels).
            crop_height: Height of the captured crop area (pixels).
        """
        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height

        # ------------------------------------------------------------------
        #  Load model
        # ------------------------------------------------------------------
        model_cfg = load_model(self.config.model, variant="")
        self.model_cfg = model_cfg
        self.scale = model_cfg.scale

        # Tile mode can only be enabled for 2× upscalers (the tile shaders
        # are designed for a single 2× stage; for 4× we chain two 2× tile
        # stages internally, so it's also valid).
        self.use_tile = config.use_tile_processing and self.scale == 2

        # Pre‑compute tile grid size for fallback decisions.
        self.tiles_x = (crop_width + config.tile_size - 1) // config.tile_size
        self.tiles_y = (crop_height + config.tile_size - 1) // config.tile_size
        self.total_tiles = self.tiles_x * self.tiles_y

        # Full‑frame resources (always created)
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []

        # References for double‑upscale tile mode
        self._residual_upscale_groups: Optional[Tuple[int, int]] = None
        self._residual_dst_tex: Optional[Texture2D] = None

        self._init_full_mode()

        # Tile processor (created only when tile mode is active)
        self.tile_processor: Optional[TileProcessor] = None
        self._first_tile_frame = True
        if self.use_tile:
            self._init_tile_mode()

        logger.info(
            "UpscalerManager ready: tile_mode=%s, crop=%dx%d, scale=%d, "
            "tile=%d, margin=%d, grid=%dx%d (%d tiles)",
            self.use_tile,
            crop_width,
            crop_height,
            self.scale,
            config.tile_size,
            config.tile_context_margin,
            self.tiles_x,
            self.tiles_y,
            self.total_tiles,
        )

    # ==================================================================
    #  Initialisation helpers
    # ==================================================================

    def _init_full_mode(self) -> None:
        """
        Build the compute pipelines for the full‑frame path.

        The model is always a standard depth‑to‑space upscaler.  For
        ``scale >= 4`` and when ``config.double_upscale`` is enabled,
        two chained 2× SRCNN stages are created; otherwise a single
        stage handles the entire upscale.
        """
        out_w = self.crop_width * self.scale
        out_h = self.crop_height * self.scale
        fmt = self.model_cfg.intermediate_format

        # Shared input and staging resources
        self.input = Texture2D(self.crop_width, self.crop_height)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)

        factory = PipelineFactory(self.model_cfg)
        intermediate_names = _collect_intermediate_names(self.model_cfg)

        if self.config.double_upscale and self.scale >= 4:
            # ---- Two‑stage 2× → 4× upscaling ----
            stage1_in_w, stage1_in_h = self.crop_width, self.crop_height
            stage1_out_w, stage1_out_h = stage1_in_w * 2, stage1_in_h * 2
            stage2_out_w, stage2_out_h = stage1_out_w * 2, stage1_out_h * 2

            # Stage 1: low‑res → 2× intermediate
            stage1_textures: Dict[str, Texture2D] = {
                name: Texture2D(stage1_in_w, stage1_in_h, format=fmt)
                for name in intermediate_names
            }
            inter_tex = Texture2D(stage1_out_w, stage1_out_h, format=fmt)
            stage1_textures["output"] = inter_tex

            srnn1 = SRCNN(
                factory,
                stage1_in_w,
                stage1_in_h,
                self.input,
                stage1_textures,
            )
            self.full_stages.append(srnn1)
            self.full_groups.append(
                dispatch_groups(stage1_in_w, stage1_in_h, last_pass=False)
            )

            # Stage 2: 2× → 4× final output
            stage2_textures = {
                name: Texture2D(stage1_out_w, stage1_out_h, format=fmt)
                for name in intermediate_names
            }
            self.output = Texture2D(stage2_out_w, stage2_out_h)
            stage2_textures["output"] = self.output

            srnn2 = SRCNN(
                factory,
                stage1_out_w,
                stage1_out_h,
                inter_tex,
                stage2_textures,
            )
            self.full_stages.append(srnn2)
            self.full_groups.append(
                dispatch_groups(stage1_out_w, stage1_out_h, last_pass=False)
            )

            # Cache the 2× intermediate for tile‑mode residual generation.
            self._residual_dst_tex = inter_tex

        else:
            # ---- Single‑stage upscaling (e.g., 2×) ----
            stage_textures = {
                name: Texture2D(self.crop_width, self.crop_height, format=fmt)
                for name in intermediate_names
            }
            self.output = Texture2D(out_w, out_h)
            stage_textures["output"] = self.output

            srnn = SRCNN(
                factory,
                self.crop_width,
                self.crop_height,
                self.input,
                stage_textures,
            )
            self.full_stages.append(srnn)
            self.full_groups.append(
                dispatch_groups(self.crop_width, self.crop_height, last_pass=False)
            )

    def _init_tile_mode(self) -> None:
        """
        Create the tile processor and ensure full‑frame fallback writes
        to the same output texture.
        """
        self.tile_processor = TileProcessor(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

        # For double‑upscale, store references needed to generate the 2×
        # residual before tile processing.
        if self.config.double_upscale and len(self.full_stages) >= 2:
            self._residual_upscale_groups = self.full_groups[0]
            self._residual_dst_tex = self.full_stages[0].outputs["output"]
        else:
            self._residual_upscale_groups = None
            self._residual_dst_tex = None

    def _rebind_full_frame_output(self) -> None:
        """
        Re‑route the last full‑frame stage’s ``"output"`` UAV to
        ``self.output``.

        This is necessary when tile mode owns the final output texture
        and the full‑frame fallback (or the seeding first frame) must
        write to that same texture.
        """
        if not self.full_stages:
            return

        # The stage that writes the final output:
        #   – second stage for double‑upscale,
        #   – first (only) stage for single‑upscale.
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
        logger.debug("Full‑frame output rebound to tile processor output")

    # ==================================================================
    #  Full‑frame helpers
    # ==================================================================

    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        margin: int,
    ) -> None:
        """
        Upload the current frame (or damage regions) to ``self.input``.

        When damage‑tracking is enabled and the total expanded damage area
        is small, only the affected sub‑rectangles are uploaded.  Otherwise
        the entire frame is uploaded via the staging buffer.
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
        """
        Execute all full‑frame compute dispatches in a single command
        buffer per SRCNN stage, reducing submission overhead.
        """
        for stage, (gx, gy) in zip(self.full_stages, self.full_groups):
            seq = [(pipe, gx, gy, 1, b"") for pipe in stage.pipelines]
            stage.pipelines[0].dispatch_sequence(sequence=seq)

    # ==================================================================
    #  Fallback decision (rect‑based)
    # ==================================================================

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
        Return ``True`` if tile processing should be skipped in
        favour of a full‑frame pass.

        The decision is based on two criteria:
        * The number of dirty tile cells exceeds ``max_tile_layers``.
        * The total expanded pixel area exceeds ``area_threshold`` of
          the crop area.
        """
        if self._count_dirty_tile_cells(rects) >= self.config.max_tile_layers:
            return True

        expanded = expand_damage_rects(
            rects,
            self.crop_width,
            self.crop_height,
            self.config.tile_context_margin,
        )
        total_area = sum(w * h for _, _, w, h in expanded)
        threshold = self.config.area_threshold * self.crop_width * self.crop_height
        return total_area > threshold

    def should_use_tile_mode(self, rects: List[Tuple[int, int, int, int, int]]) -> bool:
        """Return ``True`` if tile mode should be attempted for this frame."""
        return bool(rects) and not self._should_fallback(rects)

    # ==================================================================
    #  Tile‑frame processing
    # ==================================================================

    def process_tile_frame(
        self,
        dirty_tiles: List[Tuple[int, int, bytes, int, int]],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process one frame through the tile processor.

        On the very first tile frame a full‑frame pass seeds the output.
        Subsequent frames either fall back to full‑frame (if the damage
        area is too large) or process the dirty tiles.  For double‑upscale
        the 2× residual is refreshed from a freshly computed low‑res → 2×
        pass.
        """
        if not self.use_tile:
            raise RuntimeError("process_tile_frame called when tile mode is disabled")

        # ---- First tile frame – seed with a full‑frame pass ----
        if self._first_tile_frame:
            logger.debug("First tile frame – performing full capture")
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
            self._first_tile_frame = False
            return

        # ---- Fallback check ----
        if self._should_fallback(rects):
            logger.debug("Fallback to full‑frame (threshold exceeded)")
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

        # ---- Safety net: too many tiles ----
        max_layers = self.config.max_tile_layers
        if len(dirty_tiles) > max_layers:
            logger.warning(
                "Extracted %d tiles > capacity %d – falling back to full‑frame",
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

        # ---- Actual tile processing ----
        if self.config.double_upscale:
            # Upload low‑res frame and compute the 2× residual.
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            if self._residual_upscale_groups is not None:
                gx, gy = self._residual_upscale_groups
                self.full_stages[0].dispatch(gx, gy, 1)
            if self._residual_dst_tex is not None and self.tile_processor is not None:
                self._residual_dst_tex.copy_to(
                    self.tile_processor.residual_2x,
                    width=self.crop_width * 2,
                    height=self.crop_height * 2,
                )
        else:
            # Single‑upscale: update the full low‑res residual.
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            if self.tile_processor is not None:
                self.tile_processor.residual_staging.upload(frame_data)
                self.tile_processor.residual_staging.copy_to(
                    self.tile_processor.residual_1x,
                )

        if self.tile_processor is not None:
            self.tile_processor.process_tiles(dirty_tiles)

    # ==================================================================
    #  Output access
    # ==================================================================

    def get_output_texture(self) -> Texture2D:
        """Return the final upscaled texture (tile‑processor or full‑frame)."""
        return self.output
