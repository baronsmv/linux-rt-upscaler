from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QSettings, QTimer
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from ..icons import load_icon
from ...window import list_windows

if TYPE_CHECKING:
    from .daemon import DaemonController
    from ..main import MainWindow

logger = logging.getLogger(__name__)


class TrayController(QObject):
    """Manages the system tray icon and its context menu."""

    def __init__(
        self,
        main_window: MainWindow,
        daemon_ctrl: DaemonController,
        parent: QObject = None,
    ) -> None:
        super().__init__(parent)
        self._main_window = main_window
        self._daemon_ctrl = daemon_ctrl
        self._settings = QSettings("linux-rt-upscaler")

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(load_icon("app/app", 64, 64), self)
        self.tray_icon.setToolTip("Real-Time Upscaler")

        # Persistent menu – its content is refreshed by a timer
        self._menu = QMenu()
        self.tray_icon.setContextMenu(self._menu)

        # Tray icon activation
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Periodic refresh (like the window grid)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(3000)  # 3 seconds
        self._refresh_timer.timeout.connect(self._rebuild_menu)

        # Build initial content
        self._rebuild_menu()

    def show(self) -> None:
        self.tray_icon.show()
        self._refresh_timer.start()

    def hide(self) -> None:
        self.tray_icon.hide()
        self._refresh_timer.stop()

    # ------------------------------------------------------------------
    #  Full menu rebuild
    # ------------------------------------------------------------------
    def _rebuild_menu(self) -> None:
        if self._menu.isVisible():
            return

        session_active = self._main_window.manual_session is not None
        self._menu.clear()

        # Window list
        if not session_active:
            try:
                windows = list_windows()
                gui_handle = self._main_window.winId()
                windows = [w for w in windows if w.handle != gui_handle]
            except Exception:
                logger.exception("Failed to list windows for tray menu")
                windows = []

            for win in windows:
                title = win.title or "Unknown"
                action = self._menu.addAction(title)
                action.setData(win)
                action.triggered.connect(
                    lambda checked=False, w=win: self._start_upscaling(w)
                )

            if windows:
                self._menu.addSeparator()

        # Show / Stop action
        if session_active:
            stop_action = self._menu.addAction(self.tr("Stop"))
            stop_action.setIcon(
                load_icon(
                    "actions/stop",
                    16,
                    16,
                    color=self._main_window.gui_config.palette.icon,
                )
            )
            stop_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
            stop_action.triggered.connect(self._stop_upscaling)
        else:
            show_action = self._menu.addAction(self.tr("Show"))
            show_action.setIcon(
                load_icon(
                    "actions/show",
                    16,
                    16,
                    color=self._main_window.gui_config.palette.icon,
                )
            )
            show_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
            show_action.triggered.connect(self._show_main_window)

        # Daemon mode
        daemon_action = self._menu.addAction(self.tr("Daemon Mode"))
        daemon_action.setCheckable(True)
        daemon_action.setChecked(self._daemon_ctrl.active)
        daemon_action.toggled.connect(self._daemon_ctrl.toggle)

        self._menu.addSeparator()

        # Tray options
        close_to_tray_action = self._menu.addAction(self.tr("Close to Tray"))
        close_to_tray_action.setCheckable(True)
        close_to_tray_action.setChecked(
            self._settings.value("tray/close_to_tray", False, type=bool)
        )
        close_to_tray_action.toggled.connect(
            lambda checked: self._settings.setValue("tray/close_to_tray", checked)
        )

        minimize_to_tray_action = self._menu.addAction(self.tr("Minimize to Tray"))
        minimize_to_tray_action.setCheckable(True)
        minimize_to_tray_action.setChecked(
            self._settings.value("tray/minimize_to_tray", False, type=bool)
        )
        minimize_to_tray_action.toggled.connect(
            lambda checked: self._settings.setValue("tray/minimize_to_tray", checked)
        )

        self._menu.addSeparator()

        # Exit
        exit_action = self._menu.addAction(self.tr("Exit"))
        exit_action.setIcon(
            load_icon(
                "actions/exit",
                16,
                16,
                color=self._main_window.gui_config.palette.icon,
            )
        )
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self._quit_app)

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_main_window()

    def _start_upscaling(self, win_info) -> None:
        self._main_window._on_window_selected(win_info)
        self._rebuild_menu()

    def _stop_upscaling(self) -> None:
        self._main_window.stop_manual_session()
        self._rebuild_menu()

    def _show_main_window(self) -> None:
        self._main_window.show()
        self._main_window.raise_()
        self._main_window.activateWindow()

    def _quit_app(self) -> None:
        self._main_window._cleanup_before_quit()
        QApplication.quit()
