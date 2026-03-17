#!/usr/bin/env python3

import faulthandler
import sys

faulthandler.enable()


# Environment overrides
def _setup_environment() -> None:
    """Force X11 session and configure Vulkan drivers for X11 WSI."""
    import os

    os.environ["QT_QPA_PLATFORM"] = "xcb"  # Qt → X11
    os.environ["XDG_SESSION_TYPE"] = "x11"  # Tell toolkits we're in X11
    os.environ.pop("WAYLAND_DISPLAY", None)  # Remove Wayland socket reference

    # Vulkan driver‑specific overrides
    os.environ["MESA_VK_WSI"] = "x11"  # Mesa drivers (RADV/ANV)
    os.environ["RADV_DEBUG"] = "no_wayland_wsi"  # Fallback for older Mesa
    os.environ["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"  # NVIDIA proprietary driver


_setup_environment()

import ctypes
import logging
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Tuple

from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from .config import Config
from .monitor import get_monitor_list, get_monitor, get_monitor_geometry
from .overlay import OverlayWindow
from .pipeline import Pipeline
from .window import (
    find_by_pid,
    get_active_window,
    list_windows,
    WindowInfo,
)

logger = logging.getLogger(__name__)


def setup_logging(level: str, log_file: Optional[str]) -> None:
    """Configure logging with the given level and optional file output."""
    handlers = [logging.StreamHandler(sys.stderr)]
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )


def get_x11_display_id() -> int:
    """
    Return the X11 Display pointer as an integer for compushady.
    This is needed to create a swapchain tied to an X11 window.
    """
    logger.debug("Opening X11 display for swapchain")
    try:
        xlib = ctypes.cdll.LoadLibrary("libX11.so")
    except OSError as e:
        logger.error(f"Failed to load libX11.so: {e}")
        raise RuntimeError("X11 library not found – is X11 installed?") from e

    display_ptr = xlib.XOpenDisplay(ctypes.c_int(0))
    if display_ptr == 0:
        logger.error("XOpenDisplay failed. Is X11 running?")
        raise RuntimeError("Cannot open X display – is XWayland running?")

    logger.debug(f"XOpenDisplay returned: {display_ptr}")
    return display_ptr


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


def _launch_program_and_find_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """
    Launch the program from config.program and use find_by_pid to locate its window.
    Returns (WindowInfo, Popen) on success, or (None, None) on failure/timeout.
    """
    if not config.program:
        logger.error("No program specified in config")
        return None, None

    program_name = config.program[0]
    print(f"Launching: {' '.join(config.program)}")
    proc = subprocess.Popen(config.program)

    print("Waiting for window...")
    try:
        win_info = find_by_pid(
            proc.pid,
            pid_timeout=config.pid_timeout,
            class_hint=program_name,
            class_timeout=config.class_timeout,
            total_timeout=config.total_timeout,
            starting_phase=config.starting_phase,
        )
        logger.info(f"Found window for PID {proc.pid}: {win_info.title}")
        return win_info, proc
    except TimeoutError as e:
        logger.error(f"Timeout while waiting for window: {e}")
        print(e)
        proc.terminate()
        proc.wait()
        return None, None


def _get_active_window_with_delay(config: Config) -> Optional[WindowInfo]:
    """
    Wait target_delay seconds and then return the currently active window.
    """
    if config.log_level != "ERROR":
        print(
            f"No program specified. Will scale the currently active window in {config.target_delay} seconds..."
        )
    time.sleep(config.target_delay)
    try:
        win_info = get_active_window()
        logger.info(f"Got active window: {win_info.title}")
        return win_info
    except RuntimeError as e:
        logger.error(f"Failed to get active window: {e}")
        print(e)
        return None


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
        return _launch_program_and_find_window(config)

    else:
        win_info = _get_active_window_with_delay(config)
        return win_info, None


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
    display_id = get_x11_display_id()
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


def _cleanup(pipeline: Pipeline, proc: Optional[subprocess.Popen]) -> None:
    """Ensure pipeline is stopped and launched process is terminated."""
    logger.debug("Cleaning up resources")
    pipeline.stop()
    if proc is not None:
        logger.info(f"Terminating launched process {proc.pid}")
        proc.terminate()
        proc.wait()

    sys.exit(0)


if __name__ == "__main__":
    main()
