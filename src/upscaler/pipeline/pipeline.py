import logging
import threading
import time
from enum import Enum, auto
from queue import Empty, Queue
from typing import List, Optional, Tuple

from PySide6.QtCore import QMetaObject, Qt

from .controller import PipelineController
from .osd import OSDManager
from .presenter import Presenter
from .swapchain import SwapchainManager
from .upscaler import UpscalerManager
from ..capture import FrameGrabber
from ..config import Config, OUTPUT_GEOMETRIES, UPSCALING_MODELS, OverlayMode
from ..overlay import OverlayWindow
from ..utils import parse_output_geometry
from ..vulkan import configure_device, device_wait_idle
from ..window import WindowInfo, WindowTracker

logger = logging.getLogger(__name__)


class PauseReason(Enum):
    """Reasons why the pipeline may be paused."""

    NONE = auto()
    USER = auto()  # Manually paused via hotkey
    MINIMIZED = auto()  # Target window minimized
    FOCUS_LOST = auto()  # Target window lost focus (when pause_on_focus_loss is set)


class Pipeline:
    """
    Main processing pipeline for real‑time X11 window upscaling.

    Captures a target window, upscales it using SRCNN (full‑frame or tile‑cache),
    scales to the overlay size via Lanczos, and presents via Vulkan swapchain.

    The pipeline runs in its own thread and communicates with the main thread
    via thread‑safe queues and Qt signals.

    Attributes:
        config (Config): Global configuration.
        overlay (OverlayWindow): The overlay Qt window.
        controller (PipelineController): Handles hotkeys and user requests.
        osd (OSDManager): On‑screen display manager.
        presenter (Presenter): Handles final scaling and presentation.
        upscaler_mgr (UpscalerManager): Manages SRCNN upscaling (full/tile).
    """

    def __init__(
        self, config: Config, win_info: WindowInfo, overlay: OverlayWindow
    ) -> None:
        """
        Initialize the pipeline.

        Args:
            config: Full configuration (model, crop, output geometry, etc.).
            win_info: Initial target window information.
            overlay: The overlay window (already shown).
        """
        self.config = config
        self._win_info = win_info
        self.overlay = overlay

        # Crop and dimension attributes
        self._crop_left = config.crop_left
        self._crop_top = config.crop_top
        self._crop_right = config.crop_right
        self._crop_bottom = config.crop_bottom
        self.crop_width = win_info.width - config.crop_left - config.crop_right
        self.crop_height = win_info.height - config.crop_top - config.crop_bottom

        self._scale_factor = config.scale_factor
        self._screen_width = overlay.width()
        self._screen_height = overlay.height()

        # Controller for external commands
        self.controller = PipelineController(self)
        self.controller.set_initial_model_index(config.model)
        self.controller.set_initial_geometry_index(config.output_geometry)

        # Vulkan device setup
        configure_device(config.vulkan_buffer_pool_size)

        # Swapchain manager
        self._swapchain_manager = SwapchainManager(
            overlay.xid,
            self._screen_width,
            self._screen_height,
            present_mode=config.vulkan_present_mode,
        )

        # On‑screen display manager
        osd_texts = tuple(
            [f"Model: {m}" for m in UPSCALING_MODELS]
            + [f"Geometry: {g}" for g in OUTPUT_GEOMETRIES]
            + ["Screenshot saved", "Screenshot failed"]
        )
        self.osd = OSDManager(osd_texts, self._screen_width, self._screen_height)

        # Presenter (Lanczos + OSD + swapchain)
        self.presenter = Presenter(
            screen_width=self._screen_width,
            screen_height=self._screen_height,
            content_width=overlay.content_width,
            content_height=overlay.content_height,
            scale_mode=overlay.scale_mode,
            background_color=config.background_color,
            offset_x=config.offset_x,
            offset_y=config.offset_y,
            osd_manager=self.osd,
            swapchain_manager=self._swapchain_manager,
        )

        # Upscaler manager (full‑frame and optional tile cache)
        self.upscaler_mgr = UpscalerManager(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=config.model,
            double_upscale=config.double_upscale,
            tile_size=config.tile_size,
            use_cache=config.use_cache,
            cache_capacity=config.cache_capacity,
            cache_threshold=config.cache_threshold,
        )

        # Window tracker for handle/size changes
        self._window_tracker = WindowTracker(
            win_info.handle, win_info.width, win_info.height
        )

        # Mouse mapping rectangle (updated per frame)
        overlay.scaling_rect = [0, 0, 0, 0]

        # Threading control
        self._running = False
        self._pause_reason = PauseReason.NONE
        self._thread: Optional[threading.Thread] = None
        self._stopped_event = threading.Event()

        # Queues for cross‑thread communication
        self._switch_queue: Queue[Optional[WindowInfo]] = Queue()
        self.osd_queue: Queue[Tuple[str, float]] = Queue()

        # Frame grabber (created in thread)
        self._grabber: Optional[FrameGrabber] = None

        # Performance counters
        self._frame_count = 0
        self._last_fps_log = time.time()
        self._last_frame_time = time.time()

        # Prepare OSD textures
        device_wait_idle()
        self.osd.prepare_textures()

    # ----------------------------------------------------------------------
    # Public API
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
        self._swapchain_manager = None

    def request_switch(self, new_win_info: WindowInfo) -> None:
        """Request a switch to a new target window (thread‑safe)."""
        self._switch_queue.put(new_win_info)

    def recreate_upscaler(self) -> None:
        """
        Recreate the upscaler manager (e.g., after model change or crop resize).
        This must be called from the pipeline thread.
        """
        logger.info("Recreating upscaler manager")
        self.upscaler_mgr = UpscalerManager(
            crop_width=self.crop_width,
            crop_height=self.crop_height,
            model_name=self.config.model,
            double_upscale=self.config.double_upscale,
            tile_size=self.config.tile_size,
            use_cache=self.config.use_cache,
            cache_capacity=self.config.cache_capacity,
            cache_threshold=self.config.cache_threshold,
        )
        # Update presenter's source texture to the new full‑frame output
        self.presenter.set_source_texture(self.upscaler_mgr.full_upscaler.output)

    def clear_frame_queue(self) -> None:
        """Clear any stale frames (no‑op, kept for API compatibility)."""
        pass

    # ----------------------------------------------------------------------
    # Pause state management
    # ----------------------------------------------------------------------
    @property
    def user_paused(self) -> bool:
        return self._pause_reason == PauseReason.USER

    @user_paused.setter
    def user_paused(self, value: bool) -> None:
        if value:
            self._set_pause_reason(PauseReason.USER)
        elif self._pause_reason == PauseReason.USER:
            self._set_pause_reason(PauseReason.NONE)

    def _set_pause_reason(self, reason: PauseReason) -> None:
        """Update pause reason and show/hide overlay accordingly."""
        old_reason = self._pause_reason
        self._pause_reason = reason
        if old_reason == PauseReason.NONE and reason != PauseReason.NONE:
            self.overlay.hide()
        elif old_reason != PauseReason.NONE and reason == PauseReason.NONE:
            self.overlay.show()

    # ----------------------------------------------------------------------
    # Frame processing
    # ----------------------------------------------------------------------
    def _process_one_frame(self) -> None:
        """Capture, upscale, and present a single frame."""
        # 1. Grab frame
        try:
            frame, is_dirty, rects = self._grabber.grab()
        except RuntimeError as e:
            logger.error(f"Frame grab failed: {e}")
            return

        if not self._running:
            return

        # 2. OSD and overlay opacity
        osd_tex, needs_redraw = self.osd.update()
        if needs_redraw:
            is_dirty = True
        self.overlay.update_opacity()

        if not is_dirty and osd_tex is None:
            self.presenter.present()
            return

        # 3. Upscale
        if self.upscaler_mgr.should_use_tile_mode(len(rects) if rects else 0):
            dirty_tiles = self.upscaler_mgr.extract_dirty_tiles(rects, frame)
            self.upscaler_mgr.process_tile_frame(dirty_tiles)
            src_tex = self.upscaler_mgr.upscaled_output
        else:
            self.upscaler_mgr.upload_full_frame(
                frame=frame,
                rects=rects,
                use_damage_tracking=self.config.use_damage_tracking,
                crop_width=self.crop_width,
                crop_height=self.crop_height,
                margin=self.config.tile_context_margin,
            )
            src_tex = self.upscaler_mgr.full_upscaler.output

        # 4. Present
        self.presenter.set_source_texture(src_tex)
        self.presenter.update_lanczos_constants(src_tex.width, src_tex.height)
        self.presenter.present()

        # 5. Update mouse mapping
        self.overlay.scaling_rect = self.presenter.get_scaling_rect(self._scale_factor)

        # 6. Check swapchain recreation
        if self._swapchain_manager.needs_recreation():
            if self._swapchain_manager.is_out_of_date():
                logger.info("Swapchain out-of-date, recreating")
                self._recreate_swapchain()

    def _upload_full_frame(self, frame: bytes, rects: List) -> None:
        """
        Upload full frame (or damage regions) to the full‑frame upscaler.

        Args:
            frame: Raw BGRA pixel data.
            rects: Damage rectangles (used only if damage tracking is enabled).
        """
        upscaler = self.upscaler_mgr.full_upscaler
        if self.config.use_damage_tracking and rects:
            upload_list = []
            stride = self.crop_width * 4
            for ex, ey, ew, eh in self._expand_damage_rects(rects):
                sub_data = bytearray()
                for row in range(ey, ey + eh):
                    start = row * stride + ex * 4
                    sub_data.extend(frame[start : start + ew * 4])
                upload_list.append((bytes(sub_data), ex, ey, ew, eh))
            upscaler.input.upload_subresources(upload_list)
        else:
            upscaler.staging.upload(frame)

    def _expand_damage_rects(self, rects: List) -> List[Tuple[int, int, int, int]]:
        """
        Expand damage rectangles by the configured margin to include context.

        Args:
            rects: List of (x, y, width, height, hash) from FrameGrabber.

        Returns:
            List of expanded rectangles (x, y, width, height).
        """
        margin = self.config.tile_context_margin
        expanded = []
        for rx, ry, rw, rh, _ in rects:
            ex0 = max(0, rx - margin)
            ey0 = max(0, ry - margin)
            ex1 = min(self.crop_width, rx + rw + margin)
            ey1 = min(self.crop_height, ry + rh + margin)
            if ex1 > ex0 and ey1 > ey0:
                expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))
        return expanded

    # ----------------------------------------------------------------------
    # Window change handling
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
        """Recalculate content dimensions based on current overlay and crop."""
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
        """Recreate swapchain and related resources (e.g., after overlay resize)."""
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
        self.osd.clear_compute_cache()

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
    # Target window switching
    # ----------------------------------------------------------------------
    def _switch_target(self, new_win_info: WindowInfo) -> None:
        """
        Switch the pipeline to a new target window.

        Args:
            new_win_info: Information about the new window.
        """
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
    # Main loop
    # ----------------------------------------------------------------------
    def _run(self) -> None:
        """Main pipeline loop (runs in dedicated thread)."""
        logger.info("Pipeline thread started")
        self._create_grabber()

        while self._running:
            try:
                # Process window switch requests
                self._process_switch_requests()

                # Check window aliveness
                if not self.config.follow_focus:
                    self._window_tracker.check_alive()
                    if not self._window_tracker.alive:
                        logger.info("Target window closed – exiting")
                        break

                # Update window state and handle pause conditions
                changed = self._window_tracker.update()
                if self._update_pause_state():
                    time.sleep(0.1)
                    continue

                if changed:
                    self._handle_window_change()

                if self._pause_reason != PauseReason.NONE:
                    time.sleep(0.1)
                    continue

                # Process frame
                self._process_one_frame()
                self._frame_count += 1

                # Handle controller requests (model/geometry switches)
                self.controller.process_requests()

                # Show pending OSD messages
                self._process_osd_requests()

                # Periodic FPS logging
                self._log_fps()

            except Exception as e:
                logger.exception(f"Fatal error in pipeline loop: {e}")
                break

        self._stopped_event.set()
        QMetaObject.invokeMethod(
            self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
        )
        logger.info("Pipeline thread stopped")

    def _process_switch_requests(self) -> None:
        """Process any pending window switch requests."""
        try:
            while True:
                new_win = self._switch_queue.get_nowait()
                self._switch_target(new_win)
        except Empty:
            pass

    def _update_pause_state(self) -> bool:
        """
        Update pause reason based on window state.

        Returns:
            True if the pipeline is currently paused.
        """
        # Minimized pause
        if self._window_tracker.minimized:
            self._set_pause_reason(PauseReason.MINIMIZED)
            return True
        elif self._pause_reason == PauseReason.MINIMIZED:
            self._set_pause_reason(PauseReason.NONE)

        # Focus loss pause
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
        """Show any pending OSD messages."""
        try:
            text, duration = self.osd_queue.get_nowait()
            self.osd.show(text, duration)
        except Empty:
            pass

    def _log_fps(self) -> None:
        """Log FPS every 2 seconds."""
        now = time.time()
        if now - self._last_fps_log >= 2.0:
            elapsed = now - self._last_frame_time
            if elapsed > 0:
                fps = self._frame_count / elapsed
                logger.info(f"FPS: {fps:.1f}")
            self._last_frame_time = now
            self._frame_count = 0
            self._last_fps_log = now
