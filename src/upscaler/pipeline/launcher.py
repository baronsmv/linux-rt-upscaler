import logging
import time
from dataclasses import dataclass
from typing import Optional

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication

from .pipeline import Pipeline
from ..config import Config
from ..overlay import OverlayWindow
from ..window import WindowInfo, FocusMonitor, HotkeyManager

logger = logging.getLogger(__name__)


@dataclass
class PipelineSession:
    """Holds the live objects of a running upscaling session."""

    config: Config
    window_info: WindowInfo
    overlay: OverlayWindow
    pipeline: Pipeline
    monitor: Optional[FocusMonitor] = None
    hotkey_manager: Optional[HotkeyManager] = None


def create_pipeline_session(config: Config, win_info: WindowInfo) -> PipelineSession:
    """
    Create the overlay, pipeline, and all supporting systems.

    This function does **not** enter an event loop - it only creates the
    required objects and starts the pipeline’s background thread.

    The caller must ensure that a `QApplication` already exists.

    Parameters
    ----------
    config : Config
        Fully validated configuration object.
    win_info : WindowInfo
        The initially targeted window.

    Returns
    -------
    PipelineSession
        A container holding all live objects.  The session must be kept alive
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

    # Prepare the overlay for Vulkan
    time.sleep(0.5)
    overlay.show()
    app.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)

    # ---- Pipeline --------------------------------------------------------
    pipeline = Pipeline(config, win_info, overlay)
    pipeline.start()

    app.aboutToQuit.connect(lambda: pipeline.stop())

    # ---- Focus monitor ---------------------------------------------------
    monitor: Optional[FocusMonitor] = None
    if config.follow_focus:
        monitor = FocusMonitor(interval=config.focus_poll_interval)
        monitor.focus_changed.connect(
            lambda new_win: (
                pipeline.request_switch(new_win)
                if new_win.handle != overlay.xid
                else None
            )
        )
        monitor.start()

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
        monitor=monitor,
        hotkey_manager=hotkey_manager,
    )
