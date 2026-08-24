#!/usr/bin/env python3

from ..env import setup_environment

setup_environment()

import logging
import signal
import sys
from pathlib import Path

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

from .config import ConfigManager, GUIConfig, GUIPalette, PRESETS, load_gui_style
from .helpers import InstanceManager
from .icons import load_icon
from .main import MainWindow
from .styles import message_box_style
from ..config import parse_args, setup_logging, validate_overrides
from ..utils import ConfigError

LOCALE_DIR = Path(__file__).parent / "locale"


def _install_translators(app: QApplication) -> None:
    """Install the application translation and Qt's base translation."""
    locale = QLocale.system()

    # Try full locale first, then language only: de_DE -> de
    candidates = []
    name = locale.name()  # e.g. "de_DE"
    if name:
        candidates.append(name)
    if "_" in name:
        candidates.append(name.split("_")[0])

    for candidate in candidates:
        translator = QTranslator(app)
        if translator.load(f"upscale_gui_{candidate}", str(LOCALE_DIR)):
            app.installTranslator(translator)
            break

    # Load Qt's own translations for standard buttons/dialogs
    qt_translator = QTranslator(app)
    qt_translations_dir = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    if qt_translator.load(f"qtbase_{locale.name()}", qt_translations_dir):
        app.installTranslator(qt_translator)


def main() -> None:
    """Start the upscaler GUI application."""
    # Single-instance guard
    manager = InstanceManager("linux-rt-upscaler-gui")
    if not manager.is_primary:
        # Another instance is already running
        sys.exit(0)

    # Parse CLI arguments (the GUI accepts the same options as the non-GUI version)
    try:
        overrides, profile_name, config_path = parse_args()
        validate_overrides(overrides)
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    # Set up logging early
    log_level = overrides.get("log_level", "INFO")
    log_file = overrides.get("log_file", None)
    setup_logging(log_level, log_file)

    # Configuration manager
    config_manager = ConfigManager(config_path, cli_overrides=overrides)

    # Qt application
    app = QApplication(sys.argv)
    _install_translators(app)
    app.setWindowIcon(load_icon("app/app", 256, 256))
    app.setApplicationName("upscale-gui")
    app.setDesktopFileName("io.github.baronsmv.linux-rt-upscaler")

    # Main window
    window = MainWindow(config_manager, profile_name=profile_name)
    manager.show_requested.connect(window.activate_from_second_instance)
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
