#!/usr/bin/env python3

import faulthandler
import sys

from .window import FocusMonitor

faulthandler.enable()

from .utils.environment import setup_environment as setup_env

setup_env()

import logging
import signal
import time

from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QApplication

from .overlay import OverlayWindow
from .pipeline import Pipeline
from .utils.config import (
    apply_overrides,
    default_config,
    find_matching_profile,
    find_profile,
    load_yaml_config,
    parse_args,
)
from .utils.logging import setup_logging
from .utils.validators import validate_config, validate_overrides
from .window import acquire_target_window

logger = logging.getLogger(__name__)


def main() -> None:
    overall_start = time.perf_counter()

    # CLI options (only provided, not default ones)
    provided_args, profile_name, config_path = parse_args()
    validate_overrides(provided_args)

    # Base config overrid with CLI options
    config = default_config
    apply_overrides(config, provided_args)
    setup_logging(config.log_level, config.log_file)

    # Base config overrid with YAML options
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

    logger.info(f"Target window confirmed: {win_info}")

    # Config profiling by match
    auto_profile = None
    if not manual_profile:
        profile_name, auto_profile = find_matching_profile(profiles, win_info.title)
        if auto_profile:
            apply_overrides(config, auto_profile.get("options", {}))
            logger.info(f"Auto-applied profile for window '{win_info.title}'")

    # Final configuration and logging
    apply_overrides(config, provided_args)
    validate_config(config)

    if config.log_level != "ERROR":
        if config_path:
            print(f"Configuration found in '{config_path}'.")
        print(
            f"Target window: handle={win_info.handle}, {win_info.width}x{win_info.height}, title={win_info.title}"
        )
        if auto_profile:
            print(f"Match with profile '{profile_name}'")

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

    if config.follow_focus:
        monitor = FocusMonitor(interval=0.5)  # poll every 0.5 sec
        monitor.start(
            lambda new_win: (
                pipeline.request_switch(new_win)
                if new_win.handle != overlay.xid  # ignore the overlay
                else None
            )
        )

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
        logger.debug("Cleanup complete")
        sys.exit(0)


if __name__ == "__main__":
    main()
