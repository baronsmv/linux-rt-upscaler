from __future__ import annotations

import logging
from typing import Optional, List

from PySide6.QtCore import QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QApplication,
)

from .config import GUIConfig
from .widgets.filter_bar import FilterBar
from .widgets.window_grid import WindowGrid
from ..config import Config
from ..pipeline.launcher import create_pipeline_session
from ..window import WindowInfo, list_windows

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    The central GUI window that lets the user select a window and start
    the upscaling pipeline.

    Responsibilities:
        - Owns the global GUIConfig, FilterBar, and WindowGrid.
        - Runs a periodic auto‑refresh to keep the window list up‑to‑date.
        - Wires keyboard navigation between filter and grid.
        - Launches the pipeline session on selection confirmation.
    """

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self.gui_config = GUIConfig()  # store for future use

        # ---- Window setup ----------------------------------------------------
        self.setWindowTitle("Linux Real-Time Upscaler")
        self.setMinimumSize(600, 400)

        # ---- Central widget & layout -----------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Header label (counts windows) -----------------------------------
        self._title_label = QLabel("Choose a window to upscale")
        self._title_label.setStyleSheet(
            f"color: {self.gui_config.title_text_color}; "
            f"font-size: {self.gui_config.title_font_size + 4}px; "
            f"font-family: {self.gui_config.title_font_family}; "
            f"font-weight: bold; padding: 12px {self.gui_config.grid_margin}px 4px;"
        )
        layout.addWidget(self._title_label)

        # ---- Filter bar (no refresh button, styled) -------------------------
        self.filter_bar = FilterBar(self.gui_config)
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.filter_bar.focus_grid_requested.connect(self._focus_grid)
        layout.addWidget(self.filter_bar)

        # ---- Grid of window tiles -------------------------------------------
        self.window_grid = WindowGrid(self.gui_config)
        self.window_grid.window_selected.connect(self._on_window_selected)
        layout.addWidget(self.window_grid, stretch=1)

        # ---- Ctrl+F shortcut to focus filter bar ----------------------------
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # ---- Auto‑refresh timer ---------------------------------------------
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(self.gui_config.auto_refresh_ms)

        # State for pipeline launch
        self._selected_win_info: Optional[WindowInfo] = None
        self._session = None

        # Start maximised and do an initial population
        self.showMaximized()
        QTimer.singleShot(0, self._initial_populate)

        # Ensure we can get our own window handle after show
        self._own_handle: Optional[int] = None

    # --------------------------------------------------------------------------
    #  Window list management
    # --------------------------------------------------------------------------
    def _initial_populate(self) -> None:
        """First call, after the window is on screen."""
        self._own_handle = int(self.winId())
        self._populate_grid()

    def _populate_grid(self, filter_text: str = "") -> None:
        """
        Refresh the tile grid with filtered results.
        Excludes our own window handle.
        """
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

        self.window_grid.set_windows(filtered)

        # Update title count
        count = len(filtered)
        suffix = "s" if count != 1 else ""
        self._title_label.setText(
            f"Choose a window to upscale – {count} window{suffix}"
        )

    def _auto_refresh(self) -> None:
        """Called periodically to keep the list fresh."""
        self._populate_grid(self.filter_bar.text())

    # --------------------------------------------------------------------------
    #  Focus management
    # --------------------------------------------------------------------------
    def _focus_grid(self) -> None:
        """Move keyboard focus to the window grid and select first tile."""
        self.window_grid.setFocus()
        if self.window_grid._tiles:
            self.window_grid._set_selection(0)

    # --------------------------------------------------------------------------
    #  Slots from filters and grid
    # --------------------------------------------------------------------------
    def _on_filter_changed(self, text: str) -> None:
        """Live filtering as the user types."""
        self._populate_grid(text)

    def _on_window_selected(self, win_info: WindowInfo) -> None:
        """The user confirmed a window via click or Enter."""
        self._selected_win_info = win_info
        self._start_pipeline()

    # --------------------------------------------------------------------------
    #  Pipeline launch
    # --------------------------------------------------------------------------
    def _start_pipeline(self) -> None:
        """Hide the GUI and start the upscaling session."""
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        logger.info("Starting upscale for: %s", win_info.title)

        self.hide()
        # Stop previews to free capture resources
        self.window_grid.clear_all()  # we'll add this method to WindowGrid

        try:
            self._session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    def closeEvent(self, event) -> None:
        """Clean up timer and tiles."""
        self._refresh_timer.stop()
        self.window_grid.clear_all()
        super().closeEvent(event)
