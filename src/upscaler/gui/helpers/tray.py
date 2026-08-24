from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QObject, QSettings, QTimer
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from ..icons import load_icon
from ...window import get_window_icon, list_windows, WindowInfo

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
        parent: Optional[QObject] = None,
    ) -> None:
        """
        Args:
            main_window: The application's main window.
            daemon_ctrl: The daemon controller (for toggling daemon mode).
            parent: Optional QObject parent.
        """
        super().__init__(parent)
        self._main_window = main_window
        self._daemon_ctrl = daemon_ctrl
        self._settings = QSettings("linux-rt-upscaler")

        # Cache used for change detection
        self._daemon_action: Optional[QAction] = None
        self._cached_signature: Optional[Tuple] = None
        self._icon_cache: Dict[int, QIcon] = {}

        # Create the tray icon
        self.tray_icon = QSystemTrayIcon(load_icon("app/app", 64, 64), self)
        self.tray_icon.setToolTip("Real-Time Upscaler")

        # Build a persistent QMenu; its contents are refreshed as needed
        self._menu = QMenu()
        self._menu.aboutToShow.connect(self._update_daemon_check_state)
        self.tray_icon.setContextMenu(self._menu)

        # Tray icon activation
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Timer to periodically check for changes and refresh the menu
        # while it is not open.
        self._check_timer = QTimer(self)
        self._check_timer.setInterval(2000)  # ms
        self._check_timer.timeout.connect(self.refresh_menu)

        # Initial build
        self._rebuild_menu()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def show(self) -> None:
        """Show the tray icon and start the change-detection timer."""
        self.tray_icon.show()
        self._check_timer.start()

    def hide(self) -> None:
        """Hide the tray icon and stop the timer."""
        self.tray_icon.hide()
        self._check_timer.stop()

    # ------------------------------------------------------------------
    #  Change detection
    # ------------------------------------------------------------------
    def _get_visible_windows(self) -> List[WindowInfo]:
        """
        Return a list of windows to display, excluding the GUI itself.

        If enumeration fails, an empty list is returned and a warning is
        logged.
        """
        gui_handle = self._main_window.winId()
        try:
            windows = list_windows()
        except Exception:
            logger.exception("Failed to list windows for tray menu")
            return []
        return [w for w in windows if w.handle != gui_handle]

    def _get_tray_option_states(self) -> Tuple[Any, Any]:
        """Return current (close_to_tray, minimize_to_tray) settings."""
        return (
            self._settings.value("tray/close_to_tray", False, type=bool),
            self._settings.value("tray/minimize_to_tray", False, type=bool),
        )

    def _is_main_window_visible(self) -> bool:
        """Check if the main window is visible."""
        return self._main_window.isVisible() and not self._main_window.isMinimized()

    def _get_signature(
        self,
        windows: List[WindowInfo],
        session_active: bool,
        daemon_active: bool,
        close_to_tray: bool,
        minimize_to_tray: bool,
        main_window_visible: bool,
    ) -> Tuple:
        """
        Build a hashable signature representing the current menu state.

        The window list is sorted by (handle, title) to ensure a stable
        order and to detect any change in the set of visible windows.
        """
        window_sig = tuple(sorted((w.handle, w.title or "") for w in windows))
        return (
            window_sig,
            session_active,
            daemon_active,
            close_to_tray,
            minimize_to_tray,
            main_window_visible,
        )

    def refresh_menu(self) -> None:
        """
        Rebuild the menu only if the cached signature differs from the
        current state. Does nothing while the menu is visible to avoid
        native rendering glitches.
        """
        if self._menu.isVisible():
            return

        # Gather current state
        windows = self._get_visible_windows()
        session_active = self._main_window.manual_session is not None
        daemon_active = self._daemon_ctrl.active
        close_to_tray, minimize_to_tray = self._get_tray_option_states()
        main_window_visible = self._is_main_window_visible()

        new_signature = self._get_signature(
            windows,
            session_active,
            daemon_active,
            close_to_tray,
            minimize_to_tray,
            main_window_visible,
        )

        if new_signature != self._cached_signature:
            self._cached_signature = new_signature
            self._rebuild_menu(
                windows=windows,
                session_active=session_active,
                daemon_active=daemon_active,
                close_to_tray=close_to_tray,
                minimize_to_tray=minimize_to_tray,
                main_window_visible=main_window_visible,
            )

    # ------------------------------------------------------------------
    #  Menu construction
    # ------------------------------------------------------------------
    def _rebuild_menu(
        self,
        windows: Optional[List[WindowInfo]] = None,
        session_active: Optional[bool] = None,
        daemon_active: Optional[bool] = None,
        close_to_tray: Optional[bool] = None,
        minimize_to_tray: Optional[bool] = None,
        main_window_visible: Optional[bool] = None,
    ) -> None:
        """
        Rebuild the entire tray menu from scratch.

        This method should only be called while the menu is not visible.
        If optional arguments are omitted, current values are fetched.
        """
        # If no explicit data is provided, gather everything
        if windows is None:
            windows = self._get_visible_windows()
        if session_active is None:
            session_active = self._main_window.manual_session is not None
        if daemon_active is None:
            daemon_active = self._daemon_ctrl.active
        if close_to_tray is None or minimize_to_tray is None:
            close_to_tray, minimize_to_tray = self._get_tray_option_states()
        if main_window_visible is None:
            main_window_visible = self._is_main_window_visible()

        # Update the cached signature for consistency
        self._cached_signature = self._get_signature(
            windows,
            session_active,
            daemon_active,
            close_to_tray,
            minimize_to_tray,
            main_window_visible,
        )

        # Clear and rebuild the menu
        self._menu.clear()

        # --------------------------------------------------------------
        # Dynamic window list (only when no manual session is active)
        # --------------------------------------------------------------
        if not session_active:
            for win in windows:
                title = win.title or "Unknown"
                action = self._menu.addAction(title)
                action.setIcon(self._get_window_icon(win.handle))
                action.setData(win)
                action.triggered.connect(
                    lambda checked=False, w=win: self._start_upscaling(w)
                )
            if windows:
                self._menu.addSeparator()

        # --------------------------------------------------------------
        # Show / Stop action (single action whose text/icon changes)
        # --------------------------------------------------------------
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
            stop_action.triggered.connect(self._stop_upscaling)
        else:
            if main_window_visible:
                label = self.tr("Hide")
                icon_name = "actions/hide"
                handler = self._hide_main_window
            else:
                label = self.tr("Show")
                icon_name = "actions/show"
                handler = self._show_main_window

            action = self._menu.addAction(label)
            action.setIcon(
                load_icon(
                    icon_name, 16, 16, color=self._main_window.gui_config.palette.icon
                )
            )
            action.triggered.connect(handler)

        # --------------------------------------------------------------
        # Daemon Mode toggle
        # --------------------------------------------------------------
        daemon_action = self._menu.addAction(self.tr("Daemon Mode"))
        daemon_action.setCheckable(True)
        daemon_action.setChecked(daemon_active)
        daemon_action.toggled.connect(self._main_window.set_daemon_mode)
        daemon_action.toggled.connect(lambda _: self.refresh_menu())
        self._daemon_action = daemon_action

        self._menu.addSeparator()

        # --------------------------------------------------------------
        # Tray options
        # --------------------------------------------------------------
        close_to_tray_action = self._menu.addAction(self.tr("Close to Tray"))
        close_to_tray_action.setCheckable(True)
        close_to_tray_action.setChecked(close_to_tray)
        close_to_tray_action.toggled.connect(
            lambda checked: self._settings.setValue("tray/close_to_tray", checked)
        )

        minimize_to_tray_action = self._menu.addAction(self.tr("Minimize to Tray"))
        minimize_to_tray_action.setCheckable(True)
        minimize_to_tray_action.setChecked(minimize_to_tray)
        minimize_to_tray_action.toggled.connect(
            lambda checked: self._settings.setValue("tray/minimize_to_tray", checked)
        )

        keep_running_action = self._menu.addAction(
            self.tr("Keep running after Exit hotkey")
        )
        keep_running_action.setCheckable(True)
        keep_running_action.setChecked(
            self._settings.value("tray/keep_running_on_exit", False, type=bool)
        )
        keep_running_action.toggled.connect(
            lambda checked: self._settings.setValue(
                "tray/keep_running_on_exit", checked
            )
        )

        self._menu.addSeparator()

        # --------------------------------------------------------------
        # Exit
        # --------------------------------------------------------------
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
    #  Slots / helpers
    # ------------------------------------------------------------------
    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle double‑click (or platform equivalent) to show the window."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self._is_main_window_visible():
                self._hide_main_window()
            else:
                self._show_main_window()

    def _update_daemon_check_state(self) -> None:
        """Update the state of the daemon checkbox."""
        if self._daemon_action is not None:
            self._daemon_action.blockSignals(True)
            self._daemon_action.setChecked(self._daemon_ctrl.active)
            self._daemon_action.blockSignals(False)

    def _get_window_icon(self, handle: int) -> QIcon:
        """Return a cached QIcon for the given window, fetching it if needed."""
        if handle not in self._icon_cache:
            img = get_window_icon(handle, size=16)
            if img is not None and not img.isNull():
                self._icon_cache[handle] = QIcon(QPixmap.fromImage(img))
            else:
                self._icon_cache[handle] = QIcon()  # empty icon
        return self._icon_cache[handle]

    def _start_upscaling(self, win_info: WindowInfo) -> None:
        """Start a manual upscaling session for the given window."""
        self._main_window._on_window_selected(win_info)
        # Immediate refresh because session state changed
        self.refresh_menu()

    def _stop_upscaling(self) -> None:
        """Stop the active manual session."""
        self._main_window.stop_manual_session()
        self.refresh_menu()

    def _hide_main_window(self) -> None:
        """Hide the main window."""
        self._main_window.hide_gui()
        self.refresh_menu()

    def show_upscaling_message(self):
        """Show a message, informing upscaling is in progress and which window."""
        session = self._main_window.manual_session
        if session is not None and session.window_info is not None:
            title = session.window_info.title
            message = f"Upscaling: {title}\n\nUse Stop from the tray menu to return."
        else:
            message = "Upscaling in progress.\n\nUse Stop from the tray menu to return."

        self.tray_icon.showMessage(
            "Real-Time Upscaler",
            message,
            QSystemTrayIcon.MessageIcon.Information,
            5000,
        )

    def _show_main_window(self) -> None:
        """Show the main window, unless a manual session is active."""
        if self._main_window.manual_session is not None:
            self.show_upscaling_message()
            return
        self._main_window.show_gui()
        self.refresh_menu()

    def _quit_app(self) -> None:
        """Clean up and quit the application."""
        self._main_window._cleanup_before_quit()
        QApplication.quit()
