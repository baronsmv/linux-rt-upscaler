#!/usr/bin/env python3

from ..env import setup_environment

setup_environment()

import logging
import signal
import sys

from PySide6.QtCore import QSharedMemory
from PySide6.QtWidgets import QApplication, QMessageBox

from .config import ConfigManager, GUIConfig, presets
from .icons import load_icon
from .main import MainWindow
from .styles import message_box_style
from ..config import parse_args, setup_logging, validate_overrides
from ..utils import system_color_scheme


def main() -> None:
    """Start the upscaler GUI application."""
    # Single-instance guard
    shared = QSharedMemory("linux-rt-upscaler")
    if not shared.create(1):
        # Another instance is already running
        print("Another instance of upscale-gui is already running.")

        # Dialog
        tmp_app = QApplication(sys.argv)
        scheme = system_color_scheme()
        gui_config = GUIConfig(
            palette=presets.DARK if scheme == "dark" else presets.LIGHT
        )
        tmp_app.setStyleSheet(message_box_style(gui_config))
        QMessageBox.warning(
            None,
            "Already Running",
            "Real-Time Upscaler is already running.\n\n"
            "Only one instance of the GUI can be open at a time.",
        )
        sys.exit(0)

    # Parse CLI arguments (the GUI accepts the same options as the non-GUI version)
    overrides, profile_name, config_path = parse_args()
    validate_overrides(overrides)

    # Set up logging early
    log_level = overrides.get("log_level", "INFO")
    log_file = overrides.get("log_file", None)
    setup_logging(log_level, log_file)

    # Configuration manager
    config_manager = ConfigManager(config_path, cli_overrides=overrides)

    # Qt application
    app = QApplication(sys.argv)
    app.setWindowIcon(load_icon("app/app", 256, 256))
    app.setApplicationName("upscale-gui")
    app.setDesktopFileName("io.github.baronsmv.linux-rt-upscaler")

    # Main window
    window = MainWindow(config_manager, profile_name=profile_name)
    window.show()

    # Ctrl+C behave as expected
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        sys.exit(app.exec())
    except Exception:
        logging.getLogger(__name__).exception("GUI event loop failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
