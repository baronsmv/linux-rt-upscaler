#!/usr/bin/env python3

import ctypes
import signal
import subprocess
import sys
import time

from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from . import window
from .config import Config
from .overlay import OverlayWindow
from .pipeline import Pipeline


def get_x11_display_id():
    """Return the X11 Display pointer as an integer for compushady."""
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    return xlib.XOpenDisplay(ctypes.c_int(0))


def main():
    config = Config.from_cli()

    # Window detection
    if config.program:
        program_name = config.program[0]
        print(f"Launching: {' '.join(config.program)}")
        proc = subprocess.Popen(config.program)

        print("Waiting for window...")
        try:
            win_info = window.find_by_pid(
                proc.pid,
                pid_timeout=config.pid_timeout,
                class_hint=program_name,
                class_timeout=config.class_timeout,
            )
        except TimeoutError as e:
            print(e)
            proc.terminate()
            sys.exit(1)
    else:
        print(
            f"No program specified. Will scale the currently active window in {config.target_delay} seconds..."
        )
        time.sleep(config.target_delay)
        try:
            win_info = window.get_active_window()
        except RuntimeError as e:
            print(e)
            sys.exit(1)

    print(
        f"Target window: handle={win_info.handle}, {win_info.width}x{win_info.height}, title={win_info.title}"
    )

    # Qt and overlay
    app = QApplication([])
    screen = app.primaryScreen()
    screen_size = screen.size()
    screen_w, screen_h = screen_size.width(), screen_size.height()
    print(f"Screen resolution: {screen_w}x{screen_h}")

    overlay = OverlayWindow(
        screen_w,
        screen_h,
        map_clicks=config.map_clicks,
        target_handle=win_info.handle if config.map_clicks else None,
    )
    if config.map_clicks:
        overlay.set_client_size(win_info.width, win_info.height)

    # Swapchain
    display_id = get_x11_display_id()
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)

    # Pipeline
    pipeline = Pipeline(
        win_info,
        screen_w,
        screen_h,
        overlay,
        swapchain,
        map_clicks=config.map_clicks,
        model_name=config.model,
    )
    pipeline.start()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        app.exec()
    finally:
        pipeline.stop()
        if config.program:
            proc.terminate()
            proc.wait()
        print("Clean exit.")


if __name__ == "__main__":
    main()
