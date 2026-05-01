import logging
import struct
from typing import Dict, List, Optional, Tuple

from ..config import Config
from ..srcnn import ModelConfig, PipelineFactory, SRCNN, dispatch_groups, load_model
from ..tiles import TileProcessor, expand_damage_rects
from ..vulkan import Buffer, Compute, Texture2D, HEAP_UPLOAD

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
    Orchestrates full-frame or tile-based SRCNN upscaling for a single model.

    **Supported model types:**

    * **Standard depth-to-space** (``last_pass_upscale=True``, ``scale=2``):
      The last shader pass performs a 2x pixel shuffle and writes to the
      output at the upscaled resolution. This is the most common type
      (CNN upscalers, CuNNy, etc.). Tile mode is fully supported.

    * **GAN-style** (``last_pass_upscale=False``):
      The final pass is a normal convolution that writes **one pixel per
      thread** at the output resolution. The intermediate feature maps are
      processed at the native resolution. Tile mode is **not supported**
      for these models (the tile shaders lack the necessary upscale logic).

    * **1x effects** (``scale=1``, ``last_pass_upscale=True``):
      The model works at native resolution. All passes are executed
      inside a single SRCNN stage.

    **Full-frame mode** is always available. **Tile mode** is enabled
    only for standard 2x depth-to-space models when the configuration
    allows it.

    This class is designed to be **chainable**: the output texture of one
    `UpscalerManager` can serve as the input to another, enabling
    multi-model effects pipelines (denoise -> upscale -> sharpen).

    Attributes:
        use_tile (bool): Whether tile processing is active.
        tiles_x, tiles_y (int): Tile grid dimensions (for fallback
            decisions).
        input (Texture2D): Full low-res frame (uploaded every tile frame).
        staging (Buffer): Persistent staging buffer for full-frame uploads.
        output (Texture2D): Final upscaled image.
        full_stages, full_groups: SRCNN stages and their dispatch groups
            for the full-frame path.
        tile_processor (TileProcessor | None): Active tile processor when
            enabled.
        _first_tile_frame (bool): Used to seed the output on the first
            tile frame.
    """

    def __init__(self, config: Config, crop_width: int, crop_height: int) -> None:
        self.config = config
        self.crop_width = crop_width
        self.crop_height = crop_height

        # ------------------------------------------------------------------
        #  Load model and extract metadata
        # ------------------------------------------------------------------
        model_cfg = load_model(self.config.model, variant="")
        self.model_cfg = model_cfg
        self.scale = model_cfg.scale
        self.last_pass_upscale = model_cfg.last_pass_upscale
        self.tile_supported = model_cfg.tile_supported

        # Tile mode is only possible for standard 2x depth-to-space models
        self.use_tile = (
            config.use_tile_processing and self.tile_supported and self.scale == 2
        )

        # Grid size for fallback decisions (used even if tile disabled)
        self.tiles_x = (crop_width + config.tile_size - 1) // config.tile_size
        self.tiles_y = (crop_height + config.tile_size - 1) // config.tile_size
        self.total_tiles = self.tiles_x * self.tiles_y

        # Full-frame resources (always created)
        self.staging: Optional[Buffer] = None
        self.input: Optional[Texture2D] = None
        self.output: Optional[Texture2D] = None
        self.full_stages: List[SRCNN] = []
        self.full_groups: List[Tuple[int, int]] = []

        # Special objects for GAN-style final pass
        self._gan_final_pipe: Optional[Compute] = None
        self._gan_final_groups: Tuple[int, int] = (0, 0)

        # References needed for double-upscale tile mode
        self._residual_upscale_groups: Optional[Tuple[int, int]] = None
        self._residual_src_tex: Optional[Texture2D] = None
        self._residual_dst_tex: Optional[Texture2D] = None

        self._init_full_mode()

        # Tile processor (only when tile mode is enabled)
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
        Build the full-frame compute pipelines.

        Two distinct code paths exist:

        1. **Standard** (``last_pass_upscale=True``) - the last SRCNN
           pass does depth-to-space. All passes are handled by one (or
           two, for 4x) `SRCNN` stages.

        2. **GAN-style** (``last_pass_upscale=False``) - the last pass
           is a normal convolution that must be dispatched at the output
           resolution. Intermediate passes are an `SRCNN` stage, and
           the final pass is a custom `Compute` pipeline.
        """
        out_w = self.crop_width * self.scale
        out_h = self.crop_height * self.scale

        # Shared resources
        self.input = Texture2D(self.crop_width, self.crop_height)
        self.staging = Buffer(self.input.size, heap_type=HEAP_UPLOAD)
        fmt = self.model_cfg.intermediate_format

        # --------------------------------------------------------------
        # Path A - standard depth-to-space upscalers
        # --------------------------------------------------------------
        if self.last_pass_upscale:
            factory = PipelineFactory(self.model_cfg)
            intermediate_names = _collect_intermediate_names(self.model_cfg)

            if self.config.double_upscale and self.scale >= 4:
                # Two stages: 1x -> 2x -> 4x
                stage1_in_w, stage1_in_h = self.crop_width, self.crop_height
                stage1_out_w, stage1_out_h = stage1_in_w * 2, stage1_in_h * 2
                stage2_out_w, stage2_out_h = stage1_out_w * 2, stage1_out_h * 2

                # Stage 1 intermediates and output
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

                # Stage 2 intermediates and final output
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

                # For tile mode, cache the first stage’s output texture
                self._residual_dst_tex = inter_tex

            else:
                # Single SRCNN stage: 1x -> 2x (or other scale)
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

        # --------------------------------------------------------------
        # Path B - GAN-style (final pass does not upscale)
        # --------------------------------------------------------------
        else:
            num_passes = self.model_cfg.passes
            if num_passes < 2:
                raise ValueError("GAN model must have at least 2 passes")

            # Intermediate passes: 0 ... num_passes-2
            inter_passes = num_passes - 1
            inter_cfg = ModelConfig(
                passes=inter_passes,
                num_textures=self.model_cfg.num_textures,
                srv_uav=self.model_cfg.srv_uav[:-1],
                samplers=self.model_cfg.samplers[:-1],
                shaders=self.model_cfg.shaders[:-1],
                entry_point=self.model_cfg.entry_point,
                push_constant_size=0,
                intermediate_format=fmt,
                scale=self.scale,
                last_pass_upscale=True,  # intermediate passes are standard
                tile_supported=False,  # irrelevant for intermediates
            )
            inter_factory = PipelineFactory(inter_cfg)

            # All UAV names that need to exist as intermediate textures
            inter_uav_names: set = set()
            for _srv, uav in inter_cfg.srv_uav:
                inter_uav_names.update(uav)
            # Also include SRV names of the final pass that are not "input"
            final_srv_names = [n for n in self.model_cfg.srv_uav[-1][0] if n != "input"]
            inter_uav_names.update(final_srv_names)

            inter_textures: Dict[str, Texture2D] = {
                name: Texture2D(self.crop_width, self.crop_height, format=fmt)
                for name in inter_uav_names
            }

            # Build the intermediate SRCNN stage (if there are any intermediate passes)
            if inter_passes > 0:
                inter_srnn = SRCNN(
                    inter_factory,
                    self.crop_width,
                    self.crop_height,
                    self.input,
                    inter_textures,
                )
                self.full_stages.append(inter_srnn)
                self.full_groups.append(
                    dispatch_groups(self.crop_width, self.crop_height, last_pass=False)
                )

            # ---- Final pass (custom pipeline) ----
            final_shader = self.model_cfg.shaders[-1]
            final_cb = Buffer(struct.calcsize("IIIIffff"))
            final_cb.upload(_pack_cb(self.crop_width, self.crop_height, out_w, out_h))

            # Build SRV list for the final pass (respect order in model.json)
            final_srv_list = [self.input]  # binding 1024
            for name in self.model_cfg.srv_uav[-1][0]:
                if name != "input":
                    final_srv_list.append(inter_textures[name])

            self.output = Texture2D(out_w, out_h)

            sampler_list = [
                PipelineFactory.get_sampler(inter_factory, t)
                for t in self.model_cfg.samplers[-1]
            ]

            uav_list = [
                self.output,
                inter_textures["conv0ups"],
                inter_textures["conv0ups1"],
            ]
            self._gan_final_pipe = Compute(
                final_shader,
                cbv=[final_cb],
                srv=final_srv_list,
                uav=uav_list,
                samplers=sampler_list,
                push_size=0,
            )
            self._gan_final_groups = dispatch_groups(out_w, out_h, last_pass=False)

            # GAN models never use tile mode, so no more setup needed
            logger.debug(
                "GAN-style pipeline initialized: %dx%d -> %dx%d",
                self.crop_width,
                self.crop_height,
                out_w,
                out_h,
            )

    def _init_tile_mode(self) -> None:
        """
        Create the tile processor and ensure full-frame fallback writes
        to the same output texture.
        """
        self.tile_processor = TileProcessor(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )
        self.output = self.tile_processor.output_texture
        self._rebind_full_frame_output()

        # Double-upscale: store references needed for residual generation
        if self.config.double_upscale and len(self.full_stages) >= 2:
            self._residual_upscale_groups = self.full_groups[0]
            self._residual_dst_tex = self.full_stages[0].outputs["output"]
        else:
            # Single-upscale: residual is just the input
            self._residual_upscale_groups = None
            self._residual_dst_tex = None

    def _rebind_full_frame_output(self) -> None:
        """
        Re-route the last full-frame stage’s "output" UAV to the
        currently active `self.output` texture.

        This is required when tile mode is active because the tile
        processor owns the final output texture, and the full-frame
        fallback (as well as the first tile frame) must write to it.
        """
        if not self.full_stages or self._gan_final_pipe is not None:
            return

        # For standard depth-to-space models, the last SRCNN stage writes
        # to the output. In double-upscale mode the second stage holds
        # the final output; in single-upscale mode the first stage is
        # both the only stage and the final output.
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
        logger.debug("Full-frame output rebound to tile processor output")

    # ==================================================================
    #  Full-frame helpers
    # ==================================================================

    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        margin: int,
    ) -> None:
        """
        Upload the current frame (or damage regions) to `self.input`.

        When damage-tracking is enabled and the total expanded damage
        area is small, only the affected sub-rectangles are uploaded.
        Otherwise the entire frame is uploaded via the staging buffer.
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
        Execute all full-frame compute dispatches.

        For GAN-style models this runs the intermediate stage(s) and
        then the custom final pipeline.  For standard models it simply
        dispatches every stage in order.
        """
        if self._gan_final_pipe is not None:
            for stage, (gx, gy) in zip(self.full_stages, self.full_groups):
                stage.dispatch(gx, gy, 1)
            self._gan_final_pipe.dispatch(*self._gan_final_groups, 1)
        else:
            for stage, (gx, gy) in zip(self.full_stages, self.full_groups):
                stage.dispatch(gx, gy, 1)

    # ==================================================================
    #  Fallback decision (rect-based)
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
        True if tile processing should be skipped in favour of a
        full-frame pass.

        Decision criteria:
        * Number of dirty tile cells ≥ max_tile_layers
        * Total expanded pixel area > area_threshold x total crop area
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
        """Return True if tile mode should be attempted for this frame."""
        return bool(rects) and not self._should_fallback(rects)

    # ==================================================================
    #  Tile-frame processing
    # ==================================================================

    def process_tile_frame(
        self,
        dirty_tiles: List[Tuple[int, int, bytes, int, int]],
        rects: List[Tuple[int, int, int, int, int]],
        frame_data: memoryview,
    ) -> None:
        """
        Process one frame via the tile processor.

        On the very first tile frame a full-frame pass seeds the output.
        Subsequently the method decides whether to process tiles or fall
        back to full-frame.

        For double-upscale (4x) the 2x residual is generated from the
        freshly uploaded 1x input before the tile dispatches.
        """
        if not self.use_tile:
            raise RuntimeError("process_tile_frame called when tile mode is disabled")

        # ---- First tile frame - seed with a full-frame pass ----
        if self._first_tile_frame:
            logger.debug("First tile frame - performing full capture")
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
            logger.debug("Fallback to full-frame (threshold exceeded)")
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

        # ---- Safety net - too many tiles ----
        max_layers = self.config.max_tile_layers
        if len(dirty_tiles) > max_layers:
            logger.warning(
                "Extracted %d tiles > capacity %d - falling back to full-frame",
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
            # Upload full frame to self.input (needed for 1x -> 2x residual)
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            # Run stage1 to produce a fresh 2x residual
            if self._residual_upscale_groups is not None:
                gx, gy = self._residual_upscale_groups
                self.full_stages[0].dispatch(gx, gy, 1)
                # Copy the 2x result to the tile processor’s residual_2x
                if (
                    self._residual_dst_tex is not None
                    and self.tile_processor is not None
                ):
                    self._residual_dst_tex.copy_to(
                        self.tile_processor.residual_2x,
                        width=self.crop_width * 2,
                        height=self.crop_height * 2,
                    )
        else:
            # Upload the whole low-res frame to self.input (tile source)
            self.upload_full_frame(
                frame_data,
                rects,
                use_damage_tracking=False,
                margin=self.config.tile_context_margin,
            )
            # Keep residual_1x up-to-date (final pass uses it)
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
        """Return the final upscaled texture (tile-processor or full-frame)."""
        return self.output
