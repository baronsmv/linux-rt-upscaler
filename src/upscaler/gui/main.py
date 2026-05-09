from __future__ import annotations

import logging
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QMessageBox,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
)

from .config import GUIConfig
from .grid import WindowGridScene, WindowGridView, FilterBar
from .sidebars import ProfilesSidebar, SettingsSidebar
from .widgets import StyledSplitter
from ..config import Config
from ..pipeline import create_pipeline_session
from ..window import WindowInfo, activate_window, list_windows

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self.gui_config = GUIConfig()

        self.setWindowTitle("Linux Real-Time Upscaler")
        self.setMinimumSize(1200, 600)

        # ---- Central widget with horizontal splitter ----
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- Left sidebar (Profiles) ----
        self.left_sidebar = ProfilesSidebar(self.gui_config)

        # ---- Central column: filter bar + grid ----
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(
            0, self.gui_config.filter_vertical_margin, 0, 0
        )
        central_layout.setSpacing(0)

        self.filter_bar = FilterBar(self.gui_config)
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.filter_bar.focus_grid_requested.connect(self._focus_grid)
        central_layout.addWidget(self.filter_bar)

        self._scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self._scene, self.gui_config)
        self._scene.window_selected.connect(self._on_window_selected)
        self._scene.focus_filter_requested.connect(self.filter_bar.set_focus)
        self._view.focus_filter_requested.connect(self.filter_bar.set_focus)
        central_layout.addWidget(self._view, stretch=1)

        # ---- Right sidebar (Settings) ----
        self.right_sidebar = SettingsSidebar(self.gui_config, self.config)
        self.right_sidebar.save_settings.connect(self._on_save_settings)
        self.right_sidebar.reset_settings.connect(self._on_reset_settings)

        # ---- Assemble splitter ----
        splitter = StyledSplitter(Qt.Horizontal, self.gui_config)
        splitter.addWidget(self.left_sidebar)
        splitter.addWidget(central_widget)
        splitter.addWidget(self.right_sidebar)
        splitter.setSizes(
            [
                self.gui_config.sidebar_width,
                400,
                self.gui_config.sidebar_width,
            ]
        )

        main_layout.addWidget(splitter)

        # Ctrl+F shortcut
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # Auto‑refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(self.gui_config.auto_refresh_ms)

        # State
        self._selected_win_info: Optional[WindowInfo] = None
        self._session = None
        self._own_handle: Optional[int] = None

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
        QTimer.singleShot(0, self._start_pipeline)

    def _on_save_settings(self) -> None:
        """Save the current configuration (placeholder)."""
        logger.info("Save settings requested")
        # Here you would save the config to YAML (general or profile)
        # After saving, you may want to reset the baseline and dirty state.
        # For now, just accept the change as the new baseline.
        # self.right_sidebar.set_baseline_to_current()  # (future method)
        # self.right_sidebar._check_dirty()

    def _on_reset_settings(self) -> None:
        """Reset all settings to the baseline (placeholder)."""
        logger.info("Reset settings requested")
        # Here you would copy baseline config values back into self.config
        # Then you would need to refresh all SettingsTabs.
        # For now, just emit a signal that could trigger a full reload.
        # A real implementation would iterate over fields and setattr, then refresh the whole sidebar.

    # ------------------------------------------------------------------
    #  Pipeline launch
    # ------------------------------------------------------------------
    def _start_pipeline(self) -> None:
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        logger.info("Starting upscale for: %s", win_info.title)

        self._refresh_timer.stop()
        activate_window(win_info.handle)
        self.hide()
        self._scene.clear_all()

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
