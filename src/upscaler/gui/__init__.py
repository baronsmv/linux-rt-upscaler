#!/usr/bin/env python3

from ..env import setup_environment

setup_environment()

import signal
import sys

from PySide6.QtWidgets import QApplication

from .main import SelectorWindow
from ..config import load_config, parse_args, validate_overrides


def main() -> None:
    # Parse CLI arguments (the GUI accepts the same options)
    overrides, profile_name, config_path = parse_args()
    validate_overrides(overrides)

    config, profiles = load_config(
        profile_name=profile_name,
        config_path=config_path,
        overrides=overrides,
    )

    app = QApplication(sys.argv)
    app.setApplicationName("upscaler-gui")

    # The main window will stay visible until the user starts.
    window = SelectorWindow(config, profiles)
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        sys.exit(app.exec())
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception("GUI event loop failed")
        sys.exit(1)
