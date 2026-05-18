from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMainWindow

from ...pipeline import create_pipeline_session
from ...window import WindowInfo

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .grid import WindowGridManager
    from ..config import ConfigManager


class DaemonController:
    """
    Controls a single long-running daemon pipeline and reacts to its signals
    to show/hide the GUI and manage the window grid.

    Parameters
    ----------
    main_window: QMainWindow
        The main window that will be hidden / shown.
    config_manager: ConfigManager
        The source of effective configuration (including unsaved changes).
    grid_mgr: WindowGridManager
        The grid manager whose timer must be paused / resumed.
    """

    def __init__(
        self,
        main_window: QMainWindow,
        config_manager: ConfigManager,
        grid_mgr: WindowGridManager,
    ) -> None:
        self._mw = main_window
        self._cm = config_manager
        self._grid_mgr = grid_mgr
        self._active = False
        self._session = None

    @property
    def active(self) -> bool:
        """True while the daemon pipeline is running."""
        return self._active

    def toggle(self, enabled: bool) -> None:
        """Turn daemon mode on or off."""
        if enabled:
            self.start()
        else:
            self.stop()

    def update_base_config(self, new_base):
        """Push the latest effective config to the running pipeline."""
        if self._session:
            self._session.pipeline.update_base_config(new_base)

    def start(self) -> None:
        """Start the daemon. The GUI hides when a matching window is found."""
        if self._active:
            return
        self._active = True
        logger.info("Daemon: Waiting for a matching window...")

        eff = copy.deepcopy(self._cm.effective_config)
        eff.daemon = True

        dummy = WindowInfo(0, 0, 0, "daemon-pending")
        self._session = create_pipeline_session(
            eff,
            dummy,
            base_config=eff,
            profiles=self._cm.profiles,
        )
        self._session.overlay.closed.connect(self.stop)

        # Wire pipeline signals
        self._session.pipeline.daemon_target_acquired.connect(self._on_target_acquired)
        self._session.pipeline.daemon_scan_start.connect(self._on_scan_start)
        self._session.pipeline.finished.connect(self._on_error)

    def stop(self) -> None:
        """Stop the daemon pipeline, clean up, and restore the GUI."""
        if not self._active:
            return
        self._active = False

        if self._session:
            self._session.pipeline.finished.disconnect(self._on_error)
            self._teardown_session(self._session)
            self._session = None

        self._show_gui()

    # ------------------------------------------------------------------
    # Pipeline signal slots
    # ------------------------------------------------------------------
    def _on_target_acquired(self) -> None:
        """Daemon matched a window, stop GUI resources and hide."""
        self._grid_mgr.stop()
        self._mw.hide()

    def _on_scan_start(self) -> None:
        """Daemon returned to scanning, show GUI and restart grid."""
        self._show_gui()
        if self._session and self._session.daemon_monitor:
            self._session.daemon_monitor.start()

    def _on_error(self) -> None:
        """Pipeline exited unexpectedly, treat as stopped."""
        logger.warning("Daemon pipeline finished unexpectedly, stopping it")
        if not self._active:
            return

        self._active = False
        if self._session:
            # Avoid double cleanup
            self._session = None
        self._show_gui()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _teardown_session(session) -> None:
        """Safely stop all parts of a pipeline session."""
        try:
            session.pipeline.stop()
        except Exception:
            logger.exception("Error stopping pipeline")
        try:
            if session.monitor:
                session.monitor.stop()
        except Exception:
            pass
        try:
            if session.daemon_monitor:
                session.daemon_monitor.stop()
        except Exception:
            pass
        try:
            session.hotkey_manager.stop()
        except Exception:
            pass

    def _show_gui(self) -> None:
        """Show the main window and restart grid refreshes (if daemon active)."""
        self._mw.show()
        self._mw.raise_()
        self._mw.activateWindow()
        if self._active:
            self._grid_mgr.start()
