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

from .overlay import OverlayWindow
from .pipeline import Pipeline
from .utils.config import Config, OverlayMode
from .utils.logging import setup_logging
from .utils.monitor import get_monitor, get_monitor_geometry, get_monitor_list
from .utils.parsers import parse_output_geometry
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
    start_time = time.perf_counter()
    if config.select:
        logger.info("Selecting window interactively.")
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
        logger.info(
            f"Window acquired interactively in {time.perf_counter() - start_time:.2f}s"
        )
        return win_info, None

    elif config.program:
        logger.info(f"Launching and finding window for program: {config.program}")
        result = launch_and_find_window(config)
        logger.info(
            f"Window acquired via program launch in {time.perf_counter() - start_time:.2f}s"
        )
        return result
    else:
        logger.info(
            "Acquiring currently active window (waiting {} seconds)".format(
                config.target_delay
            )
        )
        win_info = get_active_window_after_delay(config)
        if win_info:
            logger.info(
                f"Active window acquired in {time.perf_counter() - start_time:.2f}s"
            )
        return win_info, None


def _cleanup(pipeline: Pipeline, proc: Optional[subprocess.Popen]) -> None:
    """Ensure pipeline is stopped and launched process is terminated."""
    logger.debug("Cleaning up resources")
    pipeline.stop()
    if proc is not None:
        logger.info(f"Terminating launched process {proc.pid}")
        proc.terminate()
        proc.wait()
    logger.debug("Cleanup complete")
    sys.exit(0)


def main() -> None:
    """Main entry point."""
    overall_start = time.perf_counter()

    config = Config.from_cli()
    setup_logging(config.log_level, config.log_file)

    logger.info("=" * 60)
    logger.info("Starting Linux RT Upscaler")
    logger.info(f"Configuration: {config}")
    logger.debug(f"Command line arguments: {sys.argv}")

    # Acquire target window
    start = time.perf_counter()
    win_info, proc = _acquire_target_window(config)
    if win_info is None:
        logger.error("No target window available. Exiting.")
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
    logger.debug("Qt application initialized.")

    if config.log_level != "ERROR":
        monitors = get_monitor_list()
        print(f"Detected monitors: {monitors}")
        logger.debug(f"Monitors detected: {monitors}")

    # Determine base overlay size from monitor
    monitor = get_monitor(config.monitor)
    base_x, base_y, base_w, base_h = get_monitor_geometry(monitor, config.scale_factor)
    logger.info(
        f"Using monitor '{monitor}' with geometry: {base_w}x{base_h} at ({base_x},{base_y})"
    )

    # Parse geometry to get logical content size and mode (using original dimensions)
    overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
        config.output_geometry, win_info.width, win_info.height, base_w, base_h
    )
    logger.debug(
        f"Initial parse: overlay={overlay_w}x{overlay_h}, content={content_w}x{content_h}, mode={mode}"
    )

    # Determine overlay position and offsets based on mode
    if config.overlay_mode == OverlayMode.WINDOWED.value:
        # Windowed mode: overlay window is exactly the requested size
        win_x = base_x + (base_w - overlay_w) // 2 + config.offset_x
        win_y = base_y + (base_h - overlay_h) // 2 + config.offset_y
        content_offset_x = 0
        content_offset_y = 0
        logger.debug(
            f"Windowed mode: overlay position ({win_x},{win_y}), size {overlay_w}x{overlay_h}"
        )
    else:
        # Fullscreen modes: overlay covers the whole monitor
        win_x = base_x
        win_y = base_y
        overlay_w = base_w
        overlay_h = base_h
        content_offset_x = config.offset_x
        content_offset_y = config.offset_y
        logger.debug(
            f"Fullscreen mode: overlay covers monitor, offsets ({content_offset_x},{content_offset_y})"
        )

    # Compute cropped dimensions
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
    logger.debug(f"Cropped dimensions: {crop_width}x{crop_height}")

    # Re‑parse output geometry using cropped dimensions as the source
    content_w, content_h, _, _, mode = parse_output_geometry(
        config.output_geometry,
        crop_width,
        crop_height,
        base_w,
        base_h,
    )
    logger.info(
        f"Final content dimensions: {content_w}x{content_h}, scale mode: {mode}"
    )

    # Create overlay window
    start_overlay = time.perf_counter()
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
        scale_factor=config.scale_factor,
    )
    logger.debug(f"Overlay created in {time.perf_counter() - start_overlay:.3f}s")

    # Prepare window for Vulkan
    time.sleep(0.5)  # Give window manager time to map the window
    overlay.show()
    QApplication.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)
        logger.debug("Overlay surface type set to VulkanSurface")
    else:
        logger.warning("No window handle available for Vulkan surface type")

    # Create swapchain with Qt's X11 display
    display_id = get_display()
    logger.debug(f"Creating swapchain with display={display_id}, xid={overlay.xid}")
    start_swap = time.perf_counter()
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)
    logger.debug(f"Swapchain created in {time.perf_counter() - start_swap:.3f}s")

    # Create pipeline
    start_pipeline = time.perf_counter()
    pipeline = Pipeline(
        win_info,
        overlay.width(),
        overlay.height(),
        overlay,
        swapchain,
        display_id,
        overlay.xid,
        double_upscale=config.double_upscale,
        output_geometry=config.output_geometry,
        base_width=base_w,
        base_height=base_h,
        model_name=config.model,
        overlay_mode=config.overlay_mode,
        crop_left=config.crop_left,
        crop_top=config.crop_top,
        crop_right=config.crop_right,
        crop_bottom=config.crop_bottom,
    )
    logger.debug(f"Pipeline created in {time.perf_counter() - start_pipeline:.3f}s")

    pipeline.start()
    logger.info("Pipeline started")
    logger.info(
        f"Total initialization time: {time.perf_counter() - overall_start:.2f}s"
    )

    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # allow Ctrl+C to interrupt

    # Enter Qt event loop
    try:
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
    except Exception as e:
        logger.error(f"Unexpected error in Qt event loop: {e}", exc_info=True)
    finally:
        _cleanup(pipeline, proc)


if __name__ == "__main__":
    main()
