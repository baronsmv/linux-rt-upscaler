#!/usr/bin/env python3

import faulthandler
import sys

faulthandler.enable()

from .utils import setup_environment

setup_environment()

import logging
import signal
import time

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication

from .config import setup_config
from .overlay import OverlayWindow
from .pipeline import Pipeline
from .window import FocusMonitor, HotkeyManager

logger = logging.getLogger(__name__)


def main() -> None:
    overall_start = time.perf_counter()

    # Window acquisition and config setup
    config, win_info, proc = setup_config()

    # Setup Qt application and overlay
    app = QApplication([])
    app.setApplicationName("upscaler-overlay")
    app.setApplicationDisplayName("Upscaler Overlay")
    logger.debug("Qt application initialized.")

    # Overlay creation
    try:
        overlay = OverlayWindow(config, win_info)
    except ValueError as e:
        logger.error(str(e))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Prepare window for Vulkan
    time.sleep(0.5)
    overlay.show()
    QApplication.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)
        logger.debug("Overlay surface type set to VulkanSurface")
    else:
        logger.warning("No window handle available for Vulkan surface type")

    # Pipeline creation
    pipeline = Pipeline(config, win_info, overlay)
    pipeline.start()
    logger.info("Pipeline started")
    logger.info(
        f"Total initialization time: {time.perf_counter() - overall_start:.2f}s"
    )

    # Monitor for change of focus
    if config.follow_focus:
        monitor = FocusMonitor(interval=0.5)  # poll every 0.5 sec
        monitor.start(
            lambda new_win: (
                pipeline.request_switch(new_win)
                if new_win.handle != overlay.xid  # ignore the overlay
                else None
            )
        )

    hotkey_manager = HotkeyManager(
        {
            "toggle_scaling": "Alt+Shift+S",
            "next_profile": "Alt+Shift+Right",
            "prev_profile": "Alt+Shift+Left",
            "screenshot": "Alt+Shift+P",
            "cycle_geometry": "Alt+Shift+O",
        }
    )
    controller = pipeline.controller

    # Connect signals
    hotkey_manager.toggle_scaling.connect(controller.toggle_overlay)
    hotkey_manager.next_profile.connect(
        lambda: controller.switch_model(next_model=True)
    )
    hotkey_manager.prev_profile.connect(
        lambda: controller.switch_model(next_model=False)
    )
    hotkey_manager.screenshot.connect(controller.take_screenshot)
    hotkey_manager.cycle_geometry.connect(controller.cycle_output_geometry)

    hotkey_manager.start()

    # Event loop
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
    except Exception as e:
        logger.error(f"Unexpected error in Qt event loop: {e}", exc_info=True)
    finally:
        logger.debug("Cleaning up resources")
        pipeline.stop()
        if config.follow_focus:
            monitor.stop()
        if proc is not None:
            logger.info(f"Terminating launched process {proc.pid}")
            proc.terminate()
            proc.wait()
        hotkey_manager.stop()
        logger.debug("Cleanup complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
