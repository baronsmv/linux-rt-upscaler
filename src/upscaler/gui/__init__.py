#!/usr/bin/env python3

from ..env import setup_environment

setup_environment()

import signal
import sys

from PySide6.QtWidgets import QApplication

from .config import GUIConfig
from .icons import load_icon
from .main import MainWindow
from ..config import load_config, parse_args, validate_overrides


def main() -> None:
    # Parse CLI arguments (the GUI accepts the same options)
    overrides, profile_name, config_path = parse_args()
    validate_overrides(overrides)

    config, _ = load_config(
        profile_name=profile_name,
        config_path=config_path,
        overrides=overrides,
    )

    app = QApplication(sys.argv)
    app.setWindowIcon(load_icon("app/app", 256, 256))
    app.setApplicationName("upscaler-gui")
    app.setStyleSheet(
        """
        QComboBox QAbstractItemView {
            border: none;
            background: palette(window);
            padding: 0px;
            margin: 0px;
        }
    """
    )

    # The main window will stay visible until the user starts.
    window = MainWindow(
        config,
        config_path=config_path,
        profile_name=profile_name,
    )
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        sys.exit(app.exec())
    except Exception as e:
        import logging

        logging.getLogger(__name__).exception("GUI event loop failed")
        sys.exit(1)
