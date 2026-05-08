from __future__ import annotations

import logging
from typing import List, Optional

from PySide6.QtCore import QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    QApplication,
)

from .config import GUIConfig
from .widgets.filter_bar import FilterBar
from .widgets.window_grid_scene import WindowGridScene
from .widgets.window_grid_view import WindowGridView
from ..config import Config
from ..pipeline.launcher import create_pipeline_session
from ..window import WindowInfo, activate_window, list_windows

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Central GUI window for selecting a window and starting the upscaling
    pipeline.

    Uses a modern QGraphicsView‑based mosaic for live preview tiles
    with hover pop‑out animations, and a styled filter bar.
    """

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self.gui_config = GUIConfig()

        # Basic window setup
        self.setWindowTitle("Linux Real-Time Upscaler")
        self.setMinimumSize(600, 400)

        # Central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, self.gui_config.filter_vertical_margin, 0, 0)
        layout.setSpacing(0)

        # Filter bar (no refresh button)
        self.filter_bar = FilterBar(self.gui_config)
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.filter_bar.focus_grid_requested.connect(self._focus_grid)
        layout.addWidget(self.filter_bar)

        # Graphics‑view‑based grid
        self._scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self._scene, self.gui_config)

        # Forward scene's window_selected to our handler
        self._scene.window_selected.connect(self._on_window_selected)
        self._scene.focus_filter_requested.connect(self.filter_bar.set_focus)

        # Connect Ctrl+F from the view as well
        self._view.focus_filter_requested.connect(self.filter_bar.set_focus)
        layout.addWidget(self._view, stretch=1)

        # Ctrl+F shortcut (in addition to view's own handling)
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # Auto‑refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(self.gui_config.auto_refresh_ms)

        # State
        self._selected_win_info: Optional[WindowInfo] = None
        self._session = None
        self._own_handle: Optional[int] = None

        # Show maximised and populate initial list
        self.showMaximized()
        QTimer.singleShot(0, self._initial_populate)

    # ------------------------------------------------------------------
    #  Window list management
    # ------------------------------------------------------------------

    def _initial_populate(self) -> None:
        self._own_handle = int(self.winId())
        self._populate_grid()

    def _populate_grid(self, filter_text: str = "") -> None:
        try:
            all_windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        own = self._own_handle
        filtered = []
        text_lower = filter_text.lower().strip()
        for win in all_windows:
            if own is not None and win.handle == own:
                continue
            if not win.title.strip():
                continue
            if text_lower and text_lower not in win.title.lower():
                continue
            filtered.append(win)

        self._scene.set_windows(filtered)

    def _auto_refresh(self) -> None:
        self._populate_grid(self.filter_bar.text())

    # ------------------------------------------------------------------
    #  Focus helpers
    # ------------------------------------------------------------------

    def _focus_grid(self) -> None:
        self._view.setFocus()
        self._scene.focus_first_tile()

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------

    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text)

    def _on_window_selected(self, win_info: WindowInfo) -> None:
        self._selected_win_info = win_info
        self._start_pipeline()

    # ------------------------------------------------------------------
    #  Pipeline launch
    # ------------------------------------------------------------------

    def _start_pipeline(self) -> None:
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        logger.info("Starting upscale for: %s", win_info.title)

        # Activate (raise + focus) the target window
        activate_window(win_info.handle)

        self.hide()
        self._scene.clear_all()  # stops all captures

        try:
            self._session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    def closeEvent(self, event) -> None:
        self._refresh_timer.stop()
        self._scene.clear_all()
        super().closeEvent(event)
