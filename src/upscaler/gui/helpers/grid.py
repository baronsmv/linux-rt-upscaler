from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

import xcffib
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from ...window import (
    close_xcb_connection,
    list_windows,
    open_xcb_connection,
)

if TYPE_CHECKING:
    from ..config import GUIConfig
    from ..grid import WindowGridScene, FilterBar, WindowGridView
    from ..main import MainWindow
    from ...window import WindowInfo

logger = logging.getLogger(__name__)


class WindowGridManager:
    """
    Manages the central window grid: periodic XCB window enumeration,
    client-side filtering, and feeding the scene with WindowInfo objects.

    Parameters
    ----------
    main_window: MainWindow
        The owning main window (used to obtain the native window ID and
        as parent for QMessageBox dialogs).
    gui_config: GUIConfig
        Visual / timing parameters (auto_refresh_ms, etc.).
    scene: WindowGridScene
        The scene that visualizes the windows.
    view: WindowGridView
        The view that displays the scene.
    filter_bar:
        The filter bar widget whose text is used for filtering.
    """

    def __init__(
        self,
        main_window: MainWindow,
        gui_config: GUIConfig,
        scene: WindowGridScene,
        view: WindowGridView,
        filter_bar: FilterBar,
    ) -> None:
        self._main_window = main_window
        self._cfg = gui_config
        self._scene = scene
        self._view = view
        self._filter_bar = filter_bar

        self._conn: Optional[xcffib.Connection] = None
        self._own_handle: int = 0

        # Auto-refresh timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(gui_config.auto_refresh_ms)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """
        Begin capturing the window list. Called once after the main
        window is fully constructed.
        """
        self._own_handle = int(self._main_window.winId())
        self._timer.start()
        self._refresh()

    def stop(self) -> None:
        """
        Stop the timer and release all resources (scene, XCB connection).
        Safe to call multiple times.
        """
        self._timer.stop()
        self._scene.clear_all()
        self._disconnect_xcb()

    def populate(self) -> None:
        """Manually trigger a refresh (e.g. after filter text changes)."""
        self._refresh()

    def focus_grid(self) -> None:
        """Move keyboard focus to the first tile in the grid."""
        self._view.setFocus()
        self._scene.focus_first_tile()

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------
    def _connect_xcb(self) -> bool:
        """Ensure a persistent XCB connection exists. Returns True on success."""
        if self._conn is not None:
            return True
        try:
            self._conn = open_xcb_connection()
            return self._conn is not None
        except Exception:
            logger.exception("Failed to open XCB connection")
            return False

    def _disconnect_xcb(self) -> None:
        """Close the persistent XCB connection if open."""
        if self._conn is not None:
            close_xcb_connection(self._conn)
            self._conn = None

    def _refresh(self) -> None:
        """Full refresh cycle: enumerate windows, filter, update scene."""
        if not self._connect_xcb():
            return

        try:
            all_windows: List[WindowInfo] = list_windows(conn=self._conn)
        except Exception:
            logger.exception("Window enumeration failed")
            QMessageBox.warning(
                self._main_window, "Error", "Could not enumerate windows."
            )
            return

        # Filter out own window, empty titles, and apply filter bar text
        own = self._own_handle
        text_lower = self._filter_bar.text().lower().strip()
        filtered = []
        for win in all_windows:
            if own and win.handle == own:
                continue
            if not win.title.strip():
                continue
            if text_lower and text_lower not in win.title.lower():
                continue
            filtered.append(win)

        self._scene.set_windows(filtered)
