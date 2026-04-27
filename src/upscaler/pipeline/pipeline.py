import logging
import threading
import time
from enum import Enum, auto
from queue import Empty, Queue
from typing import Optional, Tuple

import shiboken6
from PySide6.QtCore import QMetaObject, Qt

from .controller import PipelineController
from .osd import OSDManager
from .presenter import Presenter
from .swapchain import SwapchainManager
from .upscale import UpscalerManager
from ..capture import FrameGrabber
from ..config import Config, OverlayMode
from ..overlay import OverlayWindow
from ..tiles import extract_expanded_tiles
from ..utils import parse_output_geometry
from ..vulkan import configure_device
from ..window import WindowInfo, WindowTracker

logger = logging.getLogger(__name__)


class PauseReason(Enum):
    """Reasons why the pipeline may be paused."""

    NONE = auto()  # Pipeline is running normally.
    USER = auto()  # Manually paused via hotkey (overlay hidden).
    MINIMIZED = auto()  # Target window is minimized.
    FOCUS_LOST = auto()  # Target window lost focus (when pause_on_focus_loss is set).


class Pipeline:
    """
    Main real‑time upscaling pipeline.

    Captures a target X11 window, upscales the cropped area using a chosen model,
    scales the result to the overlay via Lanczos, and presents it with a Vulkan
    swapchain. All heavy work runs on a dedicated background thread.

    Supports two upscaling modes:
        - **Full‑frame** – always upscale the entire crop.
        - **Tile** – only upscale the tiles that overlap X11 damage rectangles
          (configurable fallback to full‑frame when too much of the screen changes).

    Attributes:
        config (Config): Global configuration.
        overlay (OverlayWindow): The overlay Qt window.
        controller (PipelineController): Handles hotkeys and user requests.
        osd (OSDManager): On‑screen display manager.
        presenter (Presenter): Final scaling and presentation.
        upscaler_mgr (UpscalerManager): SRCNN upscaling orchestration.
    """

    def __init__(
        self, config: Config, win_info: WindowInfo, overlay: OverlayWindow
    ) -> None:
        """Initialise the pipeline – resources are allocated later, on the pipeline thread."""
        self.config = config
        self._win_info = win_info
        self.overlay = overlay

        # Crop margins (fixed for the session)
        self._crop_left = config.crop_left
        self._crop_top = config.crop_top
        self._crop_right = config.crop_right
        self._crop_bottom = config.crop_bottom
        self.crop_width = win_info.width - config.crop_left - config.crop_right
        self.crop_height = win_info.height - config.crop_top - config.crop_bottom

        self._scale_factor = config.scale_factor
        self._screen_width = overlay.width()
        self._screen_height = overlay.height()

        # Controller for external commands (model / geometry / zoom / screenshot)
        self.controller = PipelineController(self)
        self.controller.set_initial_model_index(config.model)
        self.controller.set_initial_geometry_index(config.output_geometry)
        self.controller.set_initial_zoom_index()

        # Vulkan device configuration
        configure_device(config.vulkan_buffer_pool_size)

        # Swapchain for presentation
        self._swapchain_manager = SwapchainManager(
            overlay.xid,
            self._screen_width,
            self._screen_height,
            present_mode=config.vulkan_present_mode,
        )

        # On‑screen display (pre‑render all possible messages)
        osd_texts = tuple(
            [f"Model: {m}" for m in self.controller.available_models]
            + [f"Geometry: {g}" for g in self.controller.available_geometries]
            + [f"Zoom: {z}" for z in self.controller.available_zoom_levels]
            + ["Screenshot saved", "Screenshot failed"]
        )
        self.osd = OSDManager(osd_texts, self._screen_width, self._screen_height)

        # Presenter – Lanczos scaling + OSD blending + swapchain present
        self.presenter = Presenter(
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            content_width=overlay.content_width,
            content_height=overlay.content_height,
            scale_mode=overlay.scale_mode,
            config=self.config,
            osd_manager=self.osd,
            swapchain_manager=self._swapchain_manager,
        )

        # Upscaler manager – full‑frame or tile processing
        self.upscaler_mgr = UpscalerManager(
            config=self.config, crop_width=self.crop_width, crop_height=self.crop_height
        )

        # Window tracker (size, minimized, focus)
        self._window_tracker = WindowTracker(
            win_info.handle, win_info.width, win_info.height
        )

        # Mouse mapping rectangle – updated every frame
        overlay.scaling_rect = [0, 0, 0, 0]

        # Threading control
        self._running = False
        self._pause_reason = PauseReason.NONE
        self._thread: Optional[threading.Thread] = None
        self._stopped_event = threading.Event()

        # Cross‑thread queues
        self._switch_queue: Queue[Optional[WindowInfo]] = (
            Queue()
        )  # window switch requests
        self.osd_queue: Queue[Tuple[str, float]] = Queue()  # OSD messages

        # Frame grabber (created on pipeline thread)
        self._grabber: Optional[FrameGrabber] = None

        # Performance counters
        self._frame_count = 0
        self._last_fps_log = time.time()
        self._last_frame_time = time.time()

        # Pre‑upload OSD textures (requires Vulkan device to be ready)
        self.osd.prepare_textures()

    # ----------------------------------------------------------------------
    # Public API – lifecycle and external requests
    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the pipeline thread."""
        logger.info("Starting pipeline thread")
        self._running = True
        self._thread = threading.Thread(target=self._run, name="PipelineThread")
        self._thread.start()

    def stop(self) -> None:
        """Stop the pipeline thread and release resources."""
        logger.info("Stopping pipeline thread")
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._grabber:
            self._grabber.close()
        self._window_tracker.close()
        self._swapchain_manager.close()

    def request_switch(self, new_win_info: WindowInfo) -> None:
        """Request a switch to a new target window (thread‑safe)."""
        self._switch_queue.put(new_win_info)

    def recreate_upscaler(self) -> None:
        """Rebuild the upscaler manager (model change, crop resize)."""
        logger.info("Recreating upscaler manager")
        self.upscaler_mgr = UpscalerManager(
            config=self.config, crop_width=self.crop_width, crop_height=self.crop_height
        )
        # Update presenter's source texture to the new output.
        self.presenter.set_source_texture(self.upscaler_mgr.get_output_texture())

    def clear_frame_queue(self) -> None:
        """No‑op – kept for API compatibility."""
        pass

    # ----------------------------------------------------------------------
    # Pause state management
    # ----------------------------------------------------------------------
    @property
    def user_paused(self) -> bool:
        """True when manually paused via hotkey."""
        return self._pause_reason == PauseReason.USER

    @user_paused.setter
    def user_paused(self, value: bool) -> None:
        if value:
            self._set_pause_reason(PauseReason.USER)
        elif self._pause_reason == PauseReason.USER:
            self._set_pause_reason(PauseReason.NONE)

    def _set_pause_reason(self, reason: PauseReason) -> None:
        """Change pause reason; hide/show overlay when transitioning to/from NONE."""
        old = self._pause_reason
        self._pause_reason = reason
        if old == PauseReason.NONE and reason != PauseReason.NONE:
            self.overlay.hide()
        elif old != PauseReason.NONE and reason == PauseReason.NONE:
            self.overlay.show()

    # ----------------------------------------------------------------------
    # Core frame processing
    # ----------------------------------------------------------------------
    def _process_one_frame(self) -> None:
        """Capture one frame, upscale it, and present."""
        # --- Wait for the previous present to complete (GPU fence) ----------
        if not self._swapchain_manager.wait_for_last_present(
            timeout_ns=self.config.frame_timeout
        ):
            logger.warning("Frame fence wait timed out – possible GPU hang?")

        # --- 1. Capture ----------------------------------------------------
        try:
            frame, is_dirty, rects = self._grabber.grab()
        except RuntimeError as e:
            logger.error(f"Frame grab failed: {e}")
            return

        if not self._running:
            return

        # --- 2. OSD / opacity update ---------------------------------------
        osd_tex, needs_redraw = self.osd.update()
        if needs_redraw:
            is_dirty = True

        # Check overlay validity before using it
        if not shiboken6.isValid(self.overlay):
            self._running = False
            return
        self.overlay.update_opacity()

        # Skip frame if nothing changed and no OSD is active
        if not is_dirty and osd_tex is None:
            self.presenter.present()
            return

        # --- 3. Upscale ----------------------------------------------------
        if not self.upscaler_mgr.use_tile:
            # Full‑frame mode
            self.upscaler_mgr.upload_full_frame(
                frame=frame,
                rects=rects,
                use_damage_tracking=self.config.use_damage_tracking,
                margin=self.config.tile_context_margin,
            )
            self.upscaler_mgr.process_full_frame()
            src_tex = self.upscaler_mgr.get_output_texture()
        else:
            # Tile mode
            if self.upscaler_mgr.should_use_tile_mode(rects):
                # Extract dirty tiles (always CPU path, no GPU copy)
                dirty_tiles = extract_expanded_tiles(
                    frame=frame,
                    rects=rects,
                    crop_width=self.crop_width,
                    crop_height=self.crop_height,
                    tile_size=self.config.tile_size,
                    margin=self.config.tile_context_margin,
                    skip_interior=False,  # CPU extraction only
                )
                self.upscaler_mgr.process_tile_frame(dirty_tiles, rects, frame)
                src_tex = self.upscaler_mgr.get_output_texture()
            else:
                # Too many dirty tiles – fall back to full‑frame
                logger.debug("Tile threshold exceeded; using full‑frame for this frame")
                self.upscaler_mgr.upload_full_frame(
                    frame=frame,
                    rects=rects,
                    use_damage_tracking=self.config.use_damage_tracking,
                    margin=self.config.tile_context_margin,
                )
                self.upscaler_mgr.process_full_frame()
                src_tex = self.upscaler_mgr.get_output_texture()

        # --- 4. Present ----------------------------------------------------
        self.presenter.set_source_texture(src_tex)
        self.presenter.update_lanczos_constants(src_tex.width, src_tex.height)
        self.presenter.present()

        # --- 5. Update mouse mapping for event forwarding -------------------
        self.overlay.scaling_rect = self.presenter.get_scaling_rect(self._scale_factor)

        # --- 6. Handle swapchain recreation (overlay resize) ----------------
        if self._swapchain_manager.needs_recreation():
            if self._swapchain_manager.is_out_of_date():
                logger.info("Swapchain out‑of‑date, recreating")
                self._recreate_swapchain()

    # ----------------------------------------------------------------------
    # Window change / resize handling
    # ----------------------------------------------------------------------
    def _handle_window_change(self) -> None:
        """Recreate resources when the target window changes size or handle."""
        logger.info("Handling window change")
        self._win_info.handle = self._window_tracker.handle
        self._win_info.width = self._window_tracker.width
        self._win_info.height = self._window_tracker.height

        self.overlay.set_target_handle(self._win_info.handle)
        self.overlay.set_target_size(self._win_info.width, self._win_info.height)

        self.crop_width = self._win_info.width - self._crop_left - self._crop_right
        self.crop_height = self._win_info.height - self._crop_top - self._crop_bottom
        self.overlay.set_crop(
            self._crop_left, self._crop_top, self.crop_width, self.crop_height
        )

        self.update_content_dimensions()
        self.recreate_upscaler()
        self._create_grabber()

    def update_content_dimensions(self) -> None:
        """Recalculate content dimensions based on overlay size and output geometry."""
        overlay_w = self.overlay.width()
        overlay_h = self.overlay.height()

        new_cw, new_ch, _, _, _ = parse_output_geometry(
            self.config.output_geometry,
            self.crop_width,
            self.crop_height,
            overlay_w,
            overlay_h,
        )
        if (
            new_cw != self.presenter.content_width
            or new_ch != self.presenter.content_height
        ):
            self.presenter.content_width = new_cw
            self.presenter.content_height = new_ch
            self.overlay.set_content_dimensions(new_cw, new_ch)

    def _recreate_swapchain(self) -> None:
        """Recreate the swapchain and dependent resources (overlay resize)."""
        new_w = self.overlay.width()
        new_h = self.overlay.height()
        if new_w != self._screen_width or new_h != self._screen_height:
            self._screen_width = new_w
            self._screen_height = new_h
            self.presenter.resize(new_w, new_h)
            self._swapchain_manager.recreate(new_w, new_h)
            self.update_content_dimensions()
        else:
            self._swapchain_manager.recreate(new_w, new_h)
        self.osd.clear_compute_cache()  # screen texture changed

    def _create_grabber(self) -> None:
        """Create (or recreate) the FrameGrabber for the current target window."""
        if self._grabber:
            self._grabber.close()
        self._grabber = FrameGrabber(
            self._win_info,
            crop_left=self._crop_left,
            crop_top=self._crop_top,
            crop_right=self._crop_right,
            crop_bottom=self._crop_bottom,
            tile_size=self.config.tile_size,
        )

    # ----------------------------------------------------------------------
    # Window switching (focus follow)
    # ----------------------------------------------------------------------
    def _switch_target(self, new_win_info: WindowInfo) -> None:
        """Switch the pipeline to a new target window."""
        logger.info(f"Switching to window: {new_win_info.title}")
        test_tracker = WindowTracker(
            new_win_info.handle, new_win_info.width, new_win_info.height
        )
        test_tracker.update(force=True)
        if not test_tracker.alive:
            logger.warning("New window not alive, ignoring switch")
            test_tracker.close()
            return

        self._window_tracker.close()
        self._window_tracker = test_tracker
        self._win_info = new_win_info
        self._handle_window_change()
        self.overlay.set_target_handle(new_win_info.handle)
        self.overlay.set_target_size(new_win_info.width, new_win_info.height)

    # ----------------------------------------------------------------------
    # Main loop (runs in dedicated thread)
    # ----------------------------------------------------------------------
    def _run(self) -> None:
        """Main pipeline loop."""
        logger.info("Pipeline thread started")
        self._create_grabber()

        while self._running:
            try:
                # Process window switch requests
                self._process_switch_requests()

                # If not following focus, verify target is still alive
                if not self.config.follow_focus:
                    self._window_tracker.check_alive()
                    if not self._window_tracker.alive:
                        logger.info("Target window closed – exiting")
                        break

                # Update window state (size, minimized, focus)
                changed = self._window_tracker.update()
                if self._update_pause_state():
                    time.sleep(0.1)
                    continue

                if changed:
                    self._handle_window_change()

                if self._pause_reason != PauseReason.NONE:
                    time.sleep(0.1)
                    continue

                # Process a frame
                self._process_one_frame()
                self._frame_count += 1

                # Handle hotkey requests (model / geometry / screenshot)
                self.controller.process_requests()

                # Show pending OSD messages
                self._process_osd_requests()

                # Periodic FPS logging
                self._log_fps()

            except Exception as e:
                logger.exception(f"Fatal error in pipeline loop: {e}")
                break

        self._stopped_event.set()
        if shiboken6.isValid(self.overlay):
            try:
                QMetaObject.invokeMethod(
                    self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
                )
            except RuntimeError:
                pass
        logger.info("Pipeline thread stopped")

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _process_switch_requests(self) -> None:
        """Process pending window switch requests."""
        try:
            while True:
                new_win = self._switch_queue.get_nowait()
                self._switch_target(new_win)
        except Empty:
            pass

    def _update_pause_state(self) -> bool:
        """Check window state and update pause reason. Returns True if paused."""
        # Pause when minimized
        if self._window_tracker.minimized:
            self._set_pause_reason(PauseReason.MINIMIZED)
            return True
        elif self._pause_reason == PauseReason.MINIMIZED:
            self._set_pause_reason(PauseReason.NONE)

        # Pause when focus is lost (only for bypass‑WM overlay modes)
        bypass_wm = self.config.overlay_mode in (
            OverlayMode.ALWAYS_ON_TOP.value,
            OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value,
        )
        if (
            bypass_wm
            and self.config.pause_on_focus_loss
            and not self._window_tracker.active
        ):
            self._set_pause_reason(PauseReason.FOCUS_LOST)
            return True
        elif self._pause_reason == PauseReason.FOCUS_LOST:
            self._set_pause_reason(PauseReason.NONE)

        return self._pause_reason != PauseReason.NONE

    def _process_osd_requests(self) -> None:
        """Show pending OSD messages."""
        try:
            text, duration = self.osd_queue.get_nowait()
            if self.config.show_osd:
                self.osd.show(text, duration)
        except Empty:
            pass

    def _log_fps(self) -> None:
        """Log average FPS every 2 seconds."""
        now = time.time()
        if now - self._last_fps_log >= 2.0:
            elapsed = now - self._last_frame_time
            if elapsed > 0:
                fps = self._frame_count / elapsed
                logger.info(f"FPS: {fps:.1f}")
            self._last_frame_time = now
            self._frame_count = 0
            self._last_fps_log = now
