# File: gui/main_window.py

from __future__ import annotations

import logging
from typing import List, Optional, TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QGridLayout,
    QLabel,
    QMessageBox,
    QApplication,
)

from .widgets import PreviewTile
from ..config import Config
from ..pipeline.launcher import create_pipeline_session
from ..window import WindowInfo, list_windows, activate_window

if TYPE_CHECKING:
    from ..pipeline.launcher import PipelineSession

logger = logging.getLogger(__name__)


class SelectorWindow(QMainWindow):
    """
    Immersive window selector – a mosaic of live previews.

    Shows all candidate windows as clickable tiles with real‑time thumbnails.
    A filter bar at the top lets you narrow the selection.
    """

    TILE_SIZE = 240

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self._session: Optional[PipelineSession] = None
        self._tiles: List[PreviewTile] = []
        self._selected_win_info: Optional[WindowInfo] = None

        self.setWindowTitle("Upscaler – Select Window")
        self.resize(1100, 680)
        self.setMinimumSize(600, 400)

        self._setup_ui()
        self._populate_grid()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        # ---- Header ----
        header = QHBoxLayout()
        title = QLabel("Choose a window to upscale")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ccc;")
        header.addWidget(title)
        header.addStretch()

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by title…")
        self.filter_edit.setFixedWidth(260)
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        header.addWidget(self.filter_edit)

        layout.addLayout(header)

        # ---- Grid area ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        self.grid_layout.setSpacing(12)
        scroll.setWidget(self.grid_widget)

        layout.addWidget(scroll, stretch=1)

        # Stylesheet
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #121212;
            }
            QLineEdit {
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
                background: #2a2a2a;
                color: #eee;
            }
            QLineEdit:focus {
                border-color: #2b5b84;
            }
            QScrollArea {
                background: transparent;
            }
            """
        )

    def _populate_grid(self, filter_text: str = "") -> None:
        # Clear existing tiles
        for tile in self._tiles:
            tile.stop()
            self.grid_layout.removeWidget(tile)
            tile.deleteLater()
        self._tiles.clear()

        try:
            windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        own_handle = int(self.winId())
        filter_lower = filter_text.lower().strip()

        col = 0
        row = 0
        # Calculate columns based on available width (simple heuristic)
        columns = max(1, (self.width() - 30) // (self.TILE_SIZE + 12))

        for win in windows:
            if win.handle == own_handle:
                continue
            if not win.title.strip():
                continue
            if filter_lower and filter_lower not in win.title.lower():
                continue

            tile = PreviewTile(win, tile_size=self.TILE_SIZE, parent=self.grid_widget)
            tile.clicked.connect(self._on_tile_clicked)

            self.grid_layout.addWidget(tile, row, col)
            self._tiles.append(tile)

            col += 1
            if col >= columns:
                col = 0
                row += 1

    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        self._selected_win_info = win_info
        self._on_start()

    @Slot(str)
    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text)

    def _on_start(self) -> None:
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        activate_window(win_info.handle)
        logger.info("Starting upscale for: %s", win_info.title)

        self.hide()
        for tile in self._tiles:
            tile.stop()

        try:
            self._session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    def closeEvent(self, event) -> None:
        for tile in self._tiles:
            tile.stop()
        super().closeEvent(event)
