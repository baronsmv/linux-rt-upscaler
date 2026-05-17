import copy
import logging
import threading
import time
from enum import Enum, auto
from queue import Empty, Queue
from typing import Any, Dict, Optional, Tuple

import shiboken6
from PySide6.QtCore import QMetaObject, QObject, Qt, Signal

from .controller import PipelineController
from .osd import OSDManager
from .presenter import Presenter
from .swapchain import SwapchainManager
from .upscale import UpscalerManager
from ..capture import FrameGrabber
from ..config import (
    Config,
    OverlayMode,
    apply_overrides,
    find_matching_profile,
    parse_config,
    validate_config,
)
from ..overlay import OverlayWindow
from ..tiles import extract_expanded_tiles
from ..utils import get_base_geometry, parse_output_geometry
from ..vulkan import configure_device
from ..window import WindowInfo, WindowTracker

logger = logging.getLogger(__name__)


class PauseReason(Enum):
    """Reasons why the pipeline may be paused."""

    NONE = auto()  # Pipeline is running normally.
    USER = auto()  # Manually paused via hotkey (overlay hidden).
    MINIMIZED = auto()  # Target window is minimized.
    FOCUS_LOST = auto()  # Target window lost focus (when pause_on_focus_loss is set).
    DAEMON_WAITING = auto()  # Daemon waiting for new window match.


class Pipeline(QObject):
    """
    Main real-time upscaling pipeline.

    Captures a target X11 window, upscales the cropped area using a chosen model,
    scales the result to the overlay via Lanczos, and presents it with a Vulkan
    swapchain. All heavy work runs on a dedicated background thread.

    Supports two upscaling modes:
        - **Full-frame**: always upscale the entire crop.
        - **Tile**: only upscale the tiles that overlap X11 damage rectangles
          (configurable fallback to full-frame when too much of the screen changes).

    Attributes:
        config (Config): Global configuration.
        overlay (OverlayWindow): The overlay Qt window.
        controller (PipelineController): Handles hotkeys and user requests.
        osd (OSDManager): On-screen display manager.
        presenter (Presenter): Final scaling and presentation.
        upscaler_mgr (UpscalerManager): SRCNN upscaling orchestration.
    """

    # Signals (emitted from pipeline thread, automatically queued to main thread)
    daemon_scan_start = Signal()  # go back to scanning for windows
    daemon_target_acquired = Signal()  # daemon window was successfully switched to

    def __init__(
        self,
        config: Config,
        win_info: Optional[WindowInfo],
        overlay: OverlayWindow,
        base_config: Optional[Config] = None,
        profiles: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the pipeline. Resources are allocated later, on the pipeline thread."""
        QObject.__init__(self)
        self.config = config
        self._win_info = win_info
        self.overlay = overlay
        self.base_config = base_config or copy.deepcopy(config)
        self.profiles = profiles or {}

        # Crop margins (fixed for the session)
        self._crop_left = config.crop_left
        self._crop_top = config.crop_top
        self._crop_right = config.crop_right
        self._crop_bottom = config.crop_bottom

        if win_info is not None:
            self.crop_width = win_info.width - config.crop_left - config.crop_right
            self.crop_height = win_info.height - config.crop_top - config.crop_bottom
        else:
            self.crop_width = 0
            self.crop_height = 0

        self._scale_factor = config.scale_factor
        if self._scale_factor is None:
            _, _, _, _, self._scale_factor = get_base_geometry(
                config.monitor or "primary", None
            )
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

        # On-screen display (pre-render all possible messages)
        osd_texts = tuple(
            [f"Model: {m}" for m in self.controller.available_models]
            + [f"Geometry: {g}" for g in self.controller.available_geometries]
            + [f"Zoom: {z}" for z in self.controller.available_zoom_levels]
            + ["Screenshot saved", "Screenshot failed"]
        )
        self.osd = OSDManager(osd_texts, self._screen_width, self._screen_height)

        # Presenter: Lanczos scaling + OSD blending + swapchain present
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
        self._last_present_state_hash: Optional[int] = None
        self._presenter_params_stale = True

        # Upscaler manager: full-frame or tile processing
        self.upscaler_mgr: Optional[UpscalerManager] = None
        if win_info is not None and self.crop_width > 0 and self.crop_height > 0:
            self.upscaler_mgr = UpscalerManager(
                config=self.config,
                crop_width=self.crop_width,
                crop_height=self.crop_height,
            )

        # Window tracker (size, minimized, focus)
        self._window_tracker: Optional[WindowTracker] = None
        if win_info is not None:
            self._window_tracker = WindowTracker(
                win_info.handle, win_info.width, win_info.height
            )

        # Mouse mapping rectangle: updated every frame
        overlay.scaling_rect = [0, 0, 0, 0]

        # Pause reason
        if self.config.daemon and self._window_tracker is None:
            self._pause_reason = PauseReason.DAEMON_WAITING
        else:
            self._pause_reason = PauseReason.NONE

        # Threading control
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stopped_event = threading.Event()

        # Cross-thread queues
        self._switch_queue: Queue[Optional[WindowInfo]] = (
            Queue()
        )  # window switch requests
        self.osd_queue: Queue[Tuple[str, float]] = Queue()  # OSD messages

        # Frame grabber (created on pipeline thread)
        self._grabber: Optional[FrameGrabber] = None

        # Failure counters
        self._consecutive_capture_failures = 0
        self._max_capture_failures = 10
        self._pause_after_failure = 0.05

        # Pre-upload OSD textures (requires Vulkan device to be ready)
        self.osd.prepare_textures()

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the pipeline thread."""
        logger.debug("Starting pipeline thread.")
        self._running = True
        self._thread = threading.Thread(target=self._run, name="PipelineThread")
        self._thread.start()

    def stop(self) -> None:
        """Stop the pipeline thread and release resources."""
        if not self._running:
            return

        logger.debug("Stopping pipeline thread.")
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._grabber:
            self._grabber.close()
        self._window_tracker.close()
        self._swapchain_manager.close()

    def request_switch(self, new_win_info: WindowInfo) -> None:
        """Request a switch to a new target window (thread-safe)."""
        self._switch_queue.put(new_win_info)

    def recreate_upscaler(self) -> None:
        """Rebuild the upscaler manager (model change, crop resize)."""
        if self.crop_width <= 0 or self.crop_height <= 0:
            logger.debug("Skipping upscaler recreation, invalid crop size.")
            return

        logger.debug("Recreating upscaler manager.")
        self.upscaler_mgr = UpscalerManager(
            config=self.config,
            crop_width=self.crop_width,
            crop_height=self.crop_height,
        )

        # Update presenter's source texture to the new output
        self.presenter.set_upscaled_source(self.upscaler_mgr.get_output_texture())

        # Force full render
        self._presenter_params_stale = True

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
    # Configuration change
    # ----------------------------------------------------------------------
    def _apply_configuration_for_window(self, win_info: WindowInfo) -> None:
        """
        Rebuild the configuration from the base snapshot, apply any
        matching profile for the new window, and reconfigure all
        pipeline components.
        """
        # Copy of the base config
        new_config = copy.deepcopy(self.base_config)

        # Try to match a profile
        profile_name, profile_data = find_matching_profile(
            self.profiles, win_info.title
        )
        if profile_data:
            apply_overrides(new_config, profile_data.get("options", {}))
            logger.info("Auto-applied profile '%s'.", profile_name)
        else:
            logger.debug(
                "No matching profile for '%s', using base config.",
                win_info.title,
            )
        parse_config(new_config)
        validate_config(new_config)

        # Update and recreate
        self.config = new_config
        self._crop_left = new_config.crop_left
        self._crop_top = new_config.crop_top
        self._crop_right = new_config.crop_right
        self._crop_bottom = new_config.crop_bottom
        self.presenter.reconfigure_effects(new_config)
        self.overlay.set_scale_mode(new_config.output_geometry)

    # ----------------------------------------------------------------------
    # Core frame processing
    # ----------------------------------------------------------------------
    def _process_one_frame(self) -> None:
        """Capture one frame, upscale it, and present."""
        # --- Wait for the previous present to complete (GPU fence) ---------
        if not self._swapchain_manager.wait_for_last_present(
            timeout_ns=self.config.frame_timeout
        ):
            logger.warning("Frame fence wait timed out, possible GPU hang?")

        # --- 1. Capture ----------------------------------------------------
        try:
            frame, is_dirty, rects = self._grabber.grab()
        except RuntimeError as e:
            logger.error(f"Frame grab failed: {e}")
            self._consecutive_capture_failures += 1
            if self._consecutive_capture_failures >= self._max_capture_failures:
                logger.critical("Too many consecutive capture failures, shutting down.")
                self._running = False
            time.sleep(self._pause_after_failure)
            return

        # If we get here, capture succeeded, so reset the counter
        self._consecutive_capture_failures = 0

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

        # --- 3. Idle frame detection ---------------------------------------
        current_hash = self._compute_present_state_hash()
        idle = (
            not is_dirty
            and osd_tex is None
            and not self._presenter_params_stale
            and current_hash == self._last_present_state_hash
        )

        if idle:
            # Re-present the exact same frame, zero compute cost
            self.presenter.present_unchanged()
            self.overlay.scaling_rect = self.presenter.get_scaling_rect(
                self._scale_factor
            )
            return

        # Full render: mark params as fresh
        self._presenter_params_stale = False
        self._last_present_state_hash = current_hash

        # --- 4. Upscale ----------------------------------------------------
        if not self.upscaler_mgr.use_tile:
            # Full-frame mode
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
                # Too many dirty tiles, fall back to full-frame
                logger.debug(
                    "Tile threshold exceeded, using full-frame for this frame."
                )
                self.upscaler_mgr.upload_full_frame(
                    frame=frame,
                    rects=rects,
                    use_damage_tracking=self.config.use_damage_tracking,
                    margin=self.config.tile_context_margin,
                )
                self.upscaler_mgr.process_full_frame()
                src_tex = self.upscaler_mgr.get_output_texture()

        # --- 5. Present ----------------------------------------------------
        self.presenter.set_upscaled_source(src_tex)
        self.presenter.present()

        # --- 6. Update mouse mapping for event forwarding -------------------
        self.overlay.scaling_rect = self.presenter.get_scaling_rect(self._scale_factor)

        # --- 7. Handle swapchain recreation (overlay resize) ----------------
        if self._swapchain_manager.needs_recreation():
            if self._swapchain_manager.is_out_of_date():
                logger.debug("Swapchain out-of-date, recreating.")
                self._recreate_swapchain()

    # ----------------------------------------------------------------------
    # Window change / resize handling
    # ----------------------------------------------------------------------
    def _handle_window_change(self) -> None:
        """Recreate resources when the target window changes size or handle."""
        logger.debug("Handling window change.")
        self._win_info.handle = self._window_tracker.handle
        self._win_info.width = self._window_tracker.width
        self._win_info.height = self._window_tracker.height

        self.overlay.update_geometry(self._win_info)
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
        self._recreate_swapchain()
        self._presenter_params_stale = True

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
        self.osd.clear_compute_cache()

        # Force full render
        self._presenter_params_stale = True

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
        logger.info("Switching to window: '%s'", new_win_info.title)

        # Verify alive
        test_tracker = WindowTracker(
            new_win_info.handle, new_win_info.width, new_win_info.height
        )
        test_tracker.update(force=True)
        if not test_tracker.alive:
            logger.warning("New window not alive, ignoring switch.")
            test_tracker.close()
            return
        test_tracker.close()

        # Apply config/profile for this window
        self._apply_configuration_for_window(new_win_info)

        # Set up tracker and geometry
        self._window_tracker = WindowTracker(
            new_win_info.handle, new_win_info.width, new_win_info.height
        )
        self._win_info = new_win_info
        self._handle_window_change()

        # Exit daemon waiting state
        if self._pause_reason == PauseReason.DAEMON_WAITING:
            self._pause_reason = PauseReason.NONE
            self.daemon_target_acquired.emit()

    # ----------------------------------------------------------------------
    # Main loop (runs in dedicated thread)
    # ----------------------------------------------------------------------
    def _run(self) -> None:
        """Main pipeline loop."""
        logger.debug("Pipeline thread started.")

        if self._window_tracker is not None:
            self._create_grabber()

        while self._running:
            try:
                # Process window switch requests
                self._process_switch_requests()

                # When not following focus or daemon, exit if target dies.
                if not self.config.follow_focus and not self.config.daemon:
                    if self._window_tracker:
                        self._window_tracker.check_alive()
                        if not self._window_tracker.alive:
                            logger.info("Target window closed, exiting.")
                            break
                elif self.config.daemon and self._window_tracker:
                    # Daemon mode: check alive, if dead, go back to waiting.
                    self._window_tracker.check_alive()
                    if not self._window_tracker.alive:
                        logger.info("Daemon target window closed, resuming scanning.")
                        self._pause_reason = PauseReason.DAEMON_WAITING
                        self._window_tracker = None
                        self._win_info = None
                        self.daemon_scan_start.emit()
                        time.sleep(0.1)
                        continue

                # Update window state only if we have a tracker
                if self._window_tracker:
                    changed = self._window_tracker.update()
                    if self._update_pause_state():
                        time.sleep(0.1)
                        continue
                    if changed:
                        self._handle_window_change()
                else:
                    # No target window, just wait for a switch request
                    time.sleep(0.1)
                    continue

                if self._pause_reason != PauseReason.NONE:
                    time.sleep(0.1)
                    continue

                # Process a frame if upscaler exists
                if self.upscaler_mgr:
                    self._process_one_frame()
                else:
                    time.sleep(0.1)

                # Handle hotkey requests (model / geometry / screenshot)
                self.controller.process_requests()

                # Show pending OSD messages
                self._process_osd_requests()

            except Exception as e:
                logger.exception("Fatal error in pipeline loop: '%s'.", e)
                break

        self._stopped_event.set()
        if shiboken6.isValid(self.overlay):
            try:
                QMetaObject.invokeMethod(
                    self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
                )
            except RuntimeError:
                pass
        logger.debug("Pipeline thread stopped.")

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _compute_present_state_hash(self) -> int:
        """Return a hash of all config and geometry state that affects screen output."""
        c = self.config
        p = self.presenter
        # Include only parameters that alter pixel values or placement.
        return hash(
            (
                c.output_geometry,
                c.offset_x,
                c.offset_y,
                c.background_color,
                round(c.lanczos_blur, 6),
                round(c.lanczos_antiring_strength, 6),
                c.lanczos_linear_light,
                c.lanczos_tight_antiring,
                c.cas_enabled,
                c.bloom_enabled,
                c.vignette_enabled,
                c.lut_enabled,
                c.lut_preset,
                c.grain_enabled,
                p.content_width,
                p.content_height,
                p.scale_mode,
                p.offset_x,
                p.offset_y,
            )
        )

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

        # Pause when focus is lost (only for bypass-WM overlay modes)
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
