from __future__ import annotations

import copy
import logging
from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QApplication

from ...config import apply_overrides, parse_config
from ...pipeline import create_pipeline_session
from ...window import WindowInfo

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .grid import WindowGridManager
    from ..config import ConfigManager
    from ..main import MainWindow
    from ...pipeline import PipelineSession


class DaemonController:
    """
    Controls a single long-running daemon pipeline and reacts to its signals
    to show/hide the GUI and manage the window grid.

    Parameters
    ----------
    main_window: MainWindow
        The main window that will be hidden / shown.
    config_manager: ConfigManager
        The source of effective configuration (including unsaved changes).
    grid_mgr: WindowGridManager
        The grid manager whose timer must be paused / resumed.
    """

    def __init__(
        self,
        main_window: MainWindow,
        config_manager: ConfigManager,
        grid_mgr: WindowGridManager,
    ) -> None:
        self._main_window = main_window
        self._config_manager = config_manager
        self._grid_mgr = grid_mgr
        self._active: bool = False
        self._session: Optional[PipelineSession] = None
        self._restore_gui_visible: Optional[bool] = None

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

    def request_switch(self, win_info: WindowInfo) -> None:
        """Ask the running daemon pipeline to switch to a different window."""
        if self._session:
            self._session.pipeline.request_switch(win_info)

    def update_base_config(self, new_base):
        """Push the latest effective config to the running pipeline."""
        if self._session:
            self._session.pipeline.update_base_config(new_base)

    def start(self) -> None:
        """Start the daemon. The GUI hides when a matching window is found."""
        if self._active or self._main_window.manual_session is not None:
            return
        self._active = True
        logger.info("Daemon: Waiting for a matching window...")

        # Build a clean base config for future daemon window matches
        clean_base = copy.deepcopy(self._config_manager.global_baseline)
        apply_overrides(clean_base, self._config_manager.cli_overrides)
        parse_config(clean_base)

        eff = copy.deepcopy(self._config_manager.effective_config)
        eff.daemon = True

        dummy = WindowInfo(0, 0, 0, "daemon-pending")
        self._session = create_pipeline_session(
            eff,
            dummy,
            base_config=clean_base,
            profiles=self._config_manager.profiles,
            on_exit=self.shutdown,
        )

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
            try:
                self._session.shutdown()
            except Exception:
                logger.exception("Error shutting down daemon session")
            self._session = None
        self._show_gui()

    def shutdown(self) -> None:
        """Tear down the daemon pipeline and quit the application immediately, unless tray keep-running is set."""
        if self._main_window.settings.value(
            "tray/enabled", False, type=bool
        ) and self._main_window.settings.value(
            "tray/keep_running_on_exit", False, type=bool
        ):
            # Stop daemon but keep app running
            self.stop()
        else:
            if self._active:
                self._active = False
                if self._session:
                    try:
                        self._session.shutdown()
                    except Exception:
                        logger.exception("Error shutting down daemon session")
                    self._session = None
            QApplication.instance().quit()

    # ------------------------------------------------------------------
    # Pipeline signal slots
    # ------------------------------------------------------------------
    def _on_target_acquired(self) -> None:
        """Daemon matched a window, stop GUI resources and hide."""
        self._restore_gui_visible = (
            self._main_window.isVisible() and not self._main_window.isMinimized()
        )
        self._main_window.hide_gui()

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
            try:
                self._session.shutdown()
            except Exception:
                logger.exception("Error shutting down daemon session")
            self._session = None
        self._show_gui()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _show_gui(self) -> None:
        """Restore GUI visibility based on pre-upscaling state and restart grid."""
        # Determine whether to show or hide the main window
        if self._restore_gui_visible is None or self._restore_gui_visible:
            self._main_window.show_gui()
        else:
            self._main_window.hide_gui()

        self._restore_gui_visible = None
