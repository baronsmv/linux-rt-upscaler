#!/usr/bin/env python3

import ctypes
import logging
import signal
import subprocess
import sys
import time
from typing import Optional, List

from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from . import window
from .config import Config
from .overlay import OverlayWindow
from .pipeline import Pipeline

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_x11_display_id() -> int:
    """
    Return the X11 Display pointer as an integer for compushady.
    This is needed to create a swapchain tied to an X11 window.
    """
    logger.debug("Opening X11 display for swapchain")
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    display_ptr = xlib.XOpenDisplay(ctypes.c_int(0))
    logger.debug(f"XOpenDisplay returned: {display_ptr}")
    return display_ptr


def _select_window_interactive(
    windows: List[window.WindowInfo],
) -> Optional[window.WindowInfo]:
    """
    Interactively let the user choose a window from the list.
    Returns the selected WindowInfo or None if the user quits.
    """
    # Sort by title for easier browsing
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
            else:
                print(f"Please enter a number between 0 and {len(windows)-1}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def _launch_program_and_find_window(config: Config) -> Optional[window.WindowInfo]:
    """
    Launch the program from config.program and use find_by_pid to locate its window.
    Returns WindowInfo or None on failure/timeout.
    """
    program_name = config.program[0] if config.program else ""
    print(f"Launching: {' '.join(config.program)}")
    proc = subprocess.Popen(config.program)

    print("Waiting for window...")
    try:
        win_info = window.find_by_pid(
            proc.pid,
            pid_timeout=config.pid_timeout,
            class_hint=program_name,
            class_timeout=config.class_timeout,
            total_timeout=config.total_timeout,
            starting_phase=config.starting_phase,
        )
        logger.info(f"Found window for PID {proc.pid}: {win_info.title}")
        return win_info
    except TimeoutError as e:
        logger.error(f"Timeout while waiting for window: {e}")
        print(e)
        proc.terminate()
        proc.wait()
        return None


def _get_active_window_with_delay(config: Config) -> Optional[window.WindowInfo]:
    """
    Wait target_delay seconds and then return the currently active window.
    """
    print(
        f"No program specified. Will scale the currently active window in {config.target_delay} seconds..."
    )
    time.sleep(config.target_delay)
    try:
        win_info = window.get_active_window()
        logger.info(f"Got active window: {win_info.title}")
        return win_info
    except RuntimeError as e:
        logger.error(f"Failed to get active window: {e}")
        print(e)
        return None


def main() -> None:
    """Main entry point."""
    logger.info("Starting Real‑Time Upscaler for Linux")
    config: Config = Config.from_cli()
    win_info: Optional[window.WindowInfo] = None
    proc: Optional[subprocess.Popen] = None

    # Obtain target window
    if config.select:
        print("Enumerating open windows...")
        windows = window.list_windows()
        if not windows:
            logger.error("No visible windows found")
            print("No visible windows found.")
            sys.exit(1)

        win_info = _select_window_interactive(windows)
        if win_info is None:
            sys.exit(0)
        print(f"Selected: {win_info.title}")

    elif config.program:
        win_info, proc = _launch_program_and_find_window(config)
        if win_info is None:
            sys.exit(1)

    else:
        win_info = _get_active_window_with_delay(config)
        if win_info is None:
            sys.exit(1)

    assert win_info is not None
    print(
        f"Target window: handle={win_info.handle}, {win_info.width}x{win_info.height}, title={win_info.title}"
    )
    logger.info(f"Target window confirmed: {win_info}")

    # Qt and overlay setup
    app = QApplication([])
    screen = app.primaryScreen()
    screen_size = screen.size()
    screen_w, screen_h = screen_size.width(), screen_size.height()
    print(f"Screen resolution: {screen_w}x{screen_h}")
    logger.debug(f"Screen size: {screen_w}x{screen_h}")

    map_clicks = not config.disable_forwarding
    overlay = OverlayWindow(
        screen_w,
        screen_h,
        map_clicks=map_clicks,
        target_handle=win_info.handle if map_clicks else None,
    )
    if map_clicks:
        overlay.set_client_size(win_info.width, win_info.height)
        logger.debug("Client size set on overlay for click mapping")
    else:
        logger.debug("Click mapping disabled, overlay is transparent to input")

    # Swapchain creation
    display_id = get_x11_display_id()
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)
    logger.debug("Swapchain created")

    # Pipeline setup and start
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

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        # Enter Qt event loop
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
    finally:
        pipeline.stop()
        logger.debug("Pipeline stopped")
        if proc is not None:
            logger.info(f"Terminating launched process {proc.pid}")
            proc.terminate()
            proc.wait()


if __name__ == "__main__":
    main()
