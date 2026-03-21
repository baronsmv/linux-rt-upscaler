#!/usr/bin/env python3

import faulthandler
import sys

from upscaler.utils.validators import validate_config
from upscaler.utils.window import acquire_target_window

faulthandler.enable()

from .utils.environment import setup_environment as setup_env

setup_env()

import logging
import signal
import time

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication
from compushady import Swapchain
from compushady.formats import R8G8B8A8_UNORM

from .overlay import OverlayWindow
from .pipeline import Pipeline
from .utils.config import (
    Config,
    OverlayMode,
    apply_overrides,
    find_matching_profile,
    find_profile,
    load_yaml_config,
    parse_args,
)
from .utils.logging import setup_logging
from .utils.monitor import get_monitor, get_monitor_geometry, get_monitor_list
from .utils.parsers import parse_output_geometry
from .utils.x11 import get_display

logger = logging.getLogger(__name__)


def main() -> None:
    overall_start = time.perf_counter()

    # Base config with defaults
    args, profile_name, config_path = parse_args()
    validate_config(args)
    config = Config()
    yaml_options, profiles = load_yaml_config(config_path)
    apply_overrides(config, yaml_options)

    # Config profiling by arg
    manual_profile = None
    if profile_name:
        manual_profile = find_profile(profiles, profile_name)
        if manual_profile:
            apply_overrides(config, manual_profile.get("options", {}))
            logger.info(f"Applied manual profile '{profile_name}'")
        else:
            logger.warning(f"Profile '{profile_name}' not found, ignoring.")

    # Target window acquisition
    win_info, proc = acquire_target_window(config)
    if win_info is None:
        sys.exit(0 if config.select else 1)

    # Config profiling by match
    if not manual_profile:
        auto_profile = find_matching_profile(profiles, win_info.title)
        if auto_profile:
            apply_overrides(config, auto_profile.get("options", {}))
            logger.info(f"Auto-applied profile for window '{win_info.title}'")

    # Final configuration
    cli_overrides = vars(args)
    apply_overrides(config, cli_overrides)
    validate_config(config)
    setup_logging(config.log_level, config.log_file)

    # Target window info
    if config.log_level != "ERROR":
        print(
            f"Target window: handle={win_info.handle}, {win_info.width}x{win_info.height}, title={win_info.title}"
        )
    logger.info(f"Target window confirmed: {win_info}")

    # Setup Qt application and overlay
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

    # Parse geometry to get logical content size and mode
    overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
        config.output_geometry, win_info.width, win_info.height, base_w, base_h
    )
    logger.debug(
        f"Initial parse: overlay={overlay_w}x{overlay_h}, content={content_w}x{content_h}, mode={mode}"
    )

    # Determine overlay position and offsets
    if config.overlay_mode == OverlayMode.WINDOWED.value:
        win_x = base_x + (base_w - overlay_w) // 2 + config.offset_x
        win_y = base_y + (base_h - overlay_h) // 2 + config.offset_y
        content_offset_x = 0
        content_offset_y = 0
        logger.debug(
            f"Windowed mode: overlay position ({win_x},{win_y}), size {overlay_w}x{overlay_h}"
        )
    else:
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
            f"Invalid crop: resulting dimensions {crop_width}x{crop_height} (original {win_info.width}x{win_info.height})"
        )
        print(
            "Error: Crop values too large – would result in empty area.",
            file=sys.stderr,
        )
        sys.exit(1)
    logger.debug(f"Cropped dimensions: {crop_width}x{crop_height}")

    # Re‑parse output geometry using cropped dimensions
    content_w, content_h, _, _, mode = parse_output_geometry(
        config.output_geometry, crop_width, crop_height, base_w, base_h
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
    )
    logger.debug(f"Overlay created in {time.perf_counter() - start_overlay:.3f}s")

    # Prepare window for Vulkan
    time.sleep(0.5)
    overlay.show()
    QApplication.processEvents()
    if overlay.windowHandle():
        overlay.windowHandle().setSurfaceType(QWindow.VulkanSurface)
        logger.debug("Overlay surface type set to VulkanSurface")
    else:
        logger.warning("No window handle available for Vulkan surface type")

    # Create swap chain
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
        scale_factor=config.scale_factor,
    )
    logger.debug(f"Pipeline created in {time.perf_counter() - start_pipeline:.3f}s")

    pipeline.start()
    logger.info("Pipeline started")
    logger.info(
        f"Total initialization time: {time.perf_counter() - overall_start:.2f}s"
    )

    # Signal handling
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code {exit_code}")
    except Exception as e:
        logger.error(f"Unexpected error in Qt event loop: {e}", exc_info=True)
    finally:
        logger.debug("Cleaning up resources")
        pipeline.stop()
        if proc is not None:
            logger.info(f"Terminating launched process {proc.pid}")
            proc.terminate()
            proc.wait()
        logger.debug("Cleanup complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
