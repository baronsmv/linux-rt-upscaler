#!/usr/bin/env python3

from ..env import setup_environment

setup_environment()

import logging
import signal
import sys

from PySide6.QtWidgets import QApplication

from .config import ConfigManager
from .icons import load_icon
from .main import MainWindow
from ..config import parse_args, validate_overrides, setup_logging


def main() -> None:
    """Start the upscaler GUI application."""
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
    app.setApplicationName("upscaler-gui")

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
