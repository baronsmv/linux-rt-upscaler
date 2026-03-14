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
    config: Config = Config.from_cli()
    win_info = None

    if config.select:
        print("Enumerating open windows...")
        windows = window.list_windows()
        if not windows:
            print("No visible windows found.")
            sys.exit(1)

        # Sort by title for easier browsing
        windows.sort(key=lambda w: w.title.lower())

        print("\nAvailable windows:")
        for i, w in enumerate(windows):
            print(f"{i:3d}: {w.title} ({w.width}x{w.height})")

        while True:
            try:
                choice = input("\nEnter window number (or 'q' to quit): ").strip()
                if choice.lower() == "q":
                    sys.exit(0)
                idx = int(choice)
                if 0 <= idx < len(windows):
                    win_info = windows[idx]
                    break
                else:
                    print(f"Please enter a number between 0 and {len(windows)-1}")
            except ValueError:
                print("Invalid input. Please enter a number.")
        print(f"Selected: {win_info.title}")

    # Window detection
    elif config.program:
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
                total_timeout=config.total_timeout,
                starting_phase=config.starting_phase,
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
        map_clicks=not config.disable_forwarding,
        target_handle=win_info.handle if not config.disable_forwarding else None,
    )
    if not config.disable_forwarding:
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
        map_clicks=not config.disable_forwarding,
        model_name=config.model,
        double_upscale=config.double_upscale,
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
