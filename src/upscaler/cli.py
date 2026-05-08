#!/usr/bin/env python3

import faulthandler
import sys

faulthandler.enable()

from .env import setup_environment

setup_environment()

import logging
import signal
import time

from PySide6.QtWidgets import QApplication

from .config import setup_config
from .pipeline import create_pipeline_session

logger = logging.getLogger(__name__)


def main() -> None:
    overall_start = time.perf_counter()

    # Window acquisition and config setup
    config, win_info, proc = setup_config()

    # Create the Qt application
    app = QApplication([])
    app.setApplicationName("upscaler-overlay")
    app.setApplicationDisplayName("Upscaler Overlay")
    logger.debug("Qt application initialized.")

    # Launch pipeline session
    session = create_pipeline_session(config, win_info)
    logger.debug(
        f"Total initialization time: {time.perf_counter() - overall_start:.2f}s"
    )

    # Event loop
    exit_code = 0
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    try:
        exit_code = app.exec()
        logger.debug(f"Qt event loop exited with code {exit_code}")
    except Exception as e:
        logger.error(f"Unexpected error in Qt event loop: {e}", exc_info=True)
        exit_code = 1
    finally:
        session.pipeline.stop()
        if session.monitor is not None:
            session.monitor.stop()
        if proc is not None:
            logger.debug(f"Terminating launched process {proc.pid}")
            proc.terminate()
            proc.wait()
        session.hotkey_manager.stop()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
