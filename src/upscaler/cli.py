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

from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from .monitor import get_monitor, get_monitor_geometry, get_monitor_list
from .overlay import OverlayWindow
from .pipeline import Pipeline
from .utils.config import Config
from .utils.logging import setup_logging
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

    monitor = get_monitor(config.monitor)
    screen_x, screen_y, screen_w, screen_h = get_monitor_geometry(monitor)
    logger.info(f"Overlay geometry: ({screen_x},{screen_y}) {screen_w}x{screen_h}")

    if config.log_level != "ERROR":
        print(f"Screen resolution: {screen_w}x{screen_h}")

    map_clicks = not config.disable_forwarding
    overlay = OverlayWindow(
        screen_w,
        screen_h,
        map_clicks=map_clicks,
        target_handle=win_info.handle if map_clicks else None,
        initial_x=screen_x,
        initial_y=screen_y,
    )

    if map_clicks:
        overlay.set_client_size(win_info.width, win_info.height)
        logger.debug("Client size set on overlay for click mapping")
    else:
        logger.debug("Click mapping disabled, overlay is transparent to input")

    # Let Qt map the window
    time.sleep(0.5)
    QApplication.processEvents()
    logger.debug("Overlay window mapped")

    # Create swapchain
    display_id = get_display()
    logger.debug(
        f"Creating swapchain with display_id={display_id}, overlay.xid={overlay.xid}"
    )
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)

    # Start pipeline
    pipeline = Pipeline(
        win_info,
        screen_w,
        screen_h,
        overlay,
        swapchain,
        map_clicks=map_clicks,
        model_name=config.model,
        double_upscale=config.double_upscale,
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
