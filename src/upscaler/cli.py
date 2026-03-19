#!/usr/bin/env python3

import faulthandler
import sys

faulthandler.enable()

from .utils.environment import setup_environment as setup_env

setup_env()

import logging
import signal
import subprocess
import time
from typing import Optional, List, Tuple

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from .overlay import OverlayWindow, OverlayMode
from .pipeline import Pipeline
from .utils.config import Config
from .utils.logging import setup_logging
from .utils.monitor import get_monitor, get_monitor_geometry, get_monitor_list
from .utils.parsers import parse_output_geometry, validate_geometry
from .utils.x11 import get_display
from .window import (
    list_windows,
    WindowInfo,
    launch_and_find_window,
    get_active_window_after_delay,
)

logger = logging.getLogger(__name__)


def _select_window_interactive(windows: List[WindowInfo]) -> Optional[WindowInfo]:
    """
    Interactively let the user choose a window from the list.
    Returns the selected WindowInfo or None if the user quits.
    """
    windows.sort(key=lambda w: w.title.lower())
    print("\nAvailable windows:")
    for i, w in enumerate(windows):
        print(f"{i:3d}: {w.title} ({w.width}x{w.height})")

    while True:
        try:
            choice = input("\nEnter window number (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                logger.info("User quit window selection")
                return None
            idx = int(choice)
            if 0 <= idx < len(windows):
                selected = windows[idx]
                logger.info(f"User selected window {idx}: {selected.title}")
                return selected
            print(f"Please enter a number between 0 and {len(windows)-1}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def _acquire_target_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """
    Determine which window to upscale based on config.
    Returns (WindowInfo, optional Popen) or (None, None) on failure/exit.
    """
    if config.select:
        print("Enumerating open windows...")
        windows = list_windows()
        if not windows:
            logger.error("No visible windows found")
            print("No visible windows found.")
            return None, None

        win_info = _select_window_interactive(windows)
        if win_info is None:
            return None, None  # user quit
        if config.log_level != "ERROR":
            print(f"Selected: {win_info.title}")
        return win_info, None

    elif config.program:
        return launch_and_find_window(config)
    else:
        win_info = get_active_window_after_delay(config)
        return win_info, None


def _cleanup(pipeline: Pipeline, proc: Optional[subprocess.Popen]) -> None:
    """Ensure pipeline is stopped and launched process is terminated."""
    logger.debug("Cleaning up resources")
    pipeline.stop()
    if proc is not None:
        logger.info(f"Terminating launched process {proc.pid}")
        proc.terminate()
        proc.wait()

    sys.exit(0)


def main() -> None:
    """Main entry point."""
    config = Config.from_cli()
    setup_logging(config.log_level, config.log_file)

    logger.info("Starting Linux RT Upscaler")

    # Validations
    try:
        validate_geometry(config.output_geometry)
    except ValueError as e:
        logger.error(e)
        print(f"Error parsing geometry argument '{config.output_geometry}'")
        sys.exit(1)

    # Acquire target window
    win_info, proc = _acquire_target_window(config)
    if win_info is None:
        sys.exit(0 if config.select else 1)

    if config.log_level != "ERROR":
        print(
            f"Target window: handle={win_info.handle}, {win_info.width}x{win_info.height}, title={win_info.title}"
        )
    logger.info(f"Target window confirmed: {win_info}")

    # Set up Qt application and overlay
    app = QApplication([])
    app.setApplicationName("upscaler-overlay")
    app.setApplicationDisplayName("Upscaler Overlay")

    if config.log_level != "ERROR":
        print(f"Detected monitors: {get_monitor_list()}")

    # Determine base overlay size from monitor (position and size)
    monitor = get_monitor(config.monitor)
    base_x, base_y, base_w, base_h = get_monitor_geometry(monitor)

    # Parse geometry to get logical content size and mode
    overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
        config.output_geometry, win_info.width, win_info.height, base_w, base_h
    )

    if config.overlay_mode == OverlayMode.WINDOWED.value:
        # Windowed mode: overlay window is exactly the requested size
        win_x = base_x + (base_w - overlay_w) // 2 + config.offset_x
        win_y = base_y + (base_h - overlay_h) // 2 + config.offset_y
        # For windowed mode, content fills the overlay (scale_mode handles scaling)
        content_offset_x = 0
        content_offset_y = 0
    else:
        # Fullscreen modes: overlay covers the whole monitor
        win_x = base_x
        win_y = base_y
        overlay_w = base_w
        overlay_h = base_h
        # Offsets are applied to the content rectangle
        content_offset_x = config.offset_x
        content_offset_y = config.offset_y

    crop_width = win_info.width - config.crop_left - config.crop_right
    crop_height = win_info.height - config.crop_top - config.crop_bottom

    if crop_width <= 0 or crop_height <= 0:
        logger.error(
            f"Invalid crop: resulting dimensions {crop_width}x{crop_height} "
            f"(original {win_info.width}x{win_info.height})"
        )
        print(
            "Error: Crop values too large – would result in empty area.",
            file=sys.stderr,
        )
        sys.exit(1)

    overlay = OverlayWindow(
        width=overlay_w,
        height=overlay_h,
        mode=config.overlay_mode,
        target=win_info,
        initial_x=win_x,
        initial_y=win_y,
        content_width=content_w,
        content_height=content_h,
        scale_mode=mode,
        background_color=config.background_color,
        offset_x=content_offset_x,
        offset_y=content_offset_y,
        crop_left=config.crop_left,
        crop_top=config.crop_top,
        crop_width=crop_width,
        crop_height=crop_height,
    )

    # Prepare window for Vulkan
    time.sleep(0.5)
    overlay.show()
    QApplication.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)

    # Create swapchain with Qt's X11 display
    display_id = get_display()
    logger.debug(f"Creating swapchain with display={display_id}, xid={overlay.xid}")
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)

    pipeline = Pipeline(
        win_info,
        overlay.width(),
        overlay.height(),
        overlay,
        swapchain,
        model_name=config.model,
        double_upscale=config.double_upscale,
        crop_left=config.crop_left,
        crop_top=config.crop_top,
        crop_right=config.crop_right,
        crop_bottom=config.crop_bottom,
    )
    pipeline.start()
    logger.info("Pipeline started")

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # allow Ctrl+C to interrupt

    # Enter Qt event loop
    try:
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
    finally:
        _cleanup(pipeline, proc)


if __name__ == "__main__":
    main()
