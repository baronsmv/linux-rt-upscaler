import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication

from .pipeline import Pipeline
from ..config import Config
from ..overlay import OverlayWindow
from ..window import DaemonMonitor, FocusMonitor, HotkeyManager, WindowInfo

logger = logging.getLogger(__name__)


@dataclass
class PipelineSession:
    """Holds the live objects of a running upscaling session."""

    config: Config
    window_info: WindowInfo
    overlay: OverlayWindow
    pipeline: Pipeline
    monitor: Optional[FocusMonitor] = None
    daemon_monitor: Optional[DaemonMonitor] = None
    hotkey_manager: Optional[HotkeyManager] = None


def create_pipeline_session(
    config: Config,
    win_info: WindowInfo,
    base_config: Optional[Config] = None,
    profiles: Optional[Dict[str, Any]] = None,
) -> PipelineSession:
    """
    Create the overlay, pipeline, and all supporting systems.

    This function does **not** enter an event loop: it only creates the
    required objects and starts the pipeline’s background thread.

    The caller must ensure that a `QApplication` already exists.

    Parameters
    ----------
    config : Config
        Fully validated configuration object.
    win_info : WindowInfo
        The initially targeted window.
    base_config : Config, optional
        A copy of the base configuration before contextual overrides.
    profiles : Dict[str, Any], optional
        User profiles with match and options.

    Returns
    -------
    PipelineSession
        A container holding all live objects. The session must be kept alive
        for the duration of the upscaling run.
    """
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication not created yet")

    # ---- Overlay ---------------------------------------------------------
    try:
        overlay = OverlayWindow(config, win_info)
    except ValueError as e:
        logger.error(str(e))
        raise

    # Create the native window handle without becoming visible
    time.sleep(0.1)
    overlay.winId()
    app.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)

    # For non-daemon modes, show the overlay immediately.
    if not config.daemon:
        overlay.show()

    # ---- Pipeline --------------------------------------------------------
    pipeline = Pipeline(
        config,
        win_info if not config.daemon else None,
        overlay,
        base_config=base_config,
        profiles=profiles,
    )
    pipeline.start()

    # ---- Focus monitor ---------------------------------------------------
    if config.follow_focus:
        monitor = FocusMonitor(interval=config.focus_poll_interval)
        monitor.focus_changed.connect(lambda w: pipeline.request_switch(w))
        if not config.daemon:  # start only if not waiting for daemon first match
            monitor.start()
    else:
        monitor = None

    # ---- Daemon monitor --------------------------------------------------
    if config.daemon:
        daemon_monitor = DaemonMonitor(
            profiles or {}, interval=config.daemon_poll_interval
        )
        daemon_monitor.match_found.connect(
            lambda w: (daemon_monitor.stop(), pipeline.request_switch(w))
        )
        daemon_monitor.start()  # begin scanning
    else:
        daemon_monitor = None

    # ---- Pipeline signals to handle Daemon + Follow-focus scenario -------
    if config.daemon and config.follow_focus:

        # When daemon acquires a target, start focus monitor
        pipeline.daemon_target_acquired.connect(monitor.start)

        # When daemon target closes, stop focus and restart daemon scanning
        pipeline.daemon_scan_start.connect(monitor.stop)
        pipeline.daemon_scan_start.connect(daemon_monitor.start)

    # ---- Hotkey manager --------------------------------------------------
    hotkey_manager = HotkeyManager(config.hotkeys)
    controller = pipeline.controller

    hotkey_manager.toggle_scaling.connect(controller.toggle_overlay)
    hotkey_manager.exit_app.connect(controller.exit_app)
    hotkey_manager.screenshot.connect(controller.take_screenshot)
    hotkey_manager.cycle_model.connect(controller.switch_model)
    hotkey_manager.cycle_geometry.connect(controller.switch_geometry)
    hotkey_manager.zoom_in.connect(controller.zoom_in)
    hotkey_manager.zoom_out.connect(controller.zoom_out)
    hotkey_manager.offset_up.connect(controller.offset_up)
    hotkey_manager.offset_down.connect(controller.offset_down)
    hotkey_manager.offset_left.connect(controller.offset_left)
    hotkey_manager.offset_right.connect(controller.offset_right)

    hotkey_manager.start()

    return PipelineSession(
        config=config,
        window_info=win_info,
        overlay=overlay,
        pipeline=pipeline,
        monitor=monitor if config.follow_focus else None,
        daemon_monitor=daemon_monitor if config.daemon else None,
        hotkey_manager=hotkey_manager,
    )
