# File: gui/main_window.py

from __future__ import annotations

import logging
from typing import List, Optional, Dict, TYPE_CHECKING

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QGridLayout,
    QLabel,
    QPushButton,
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
    A filter bar at the top lets you narrow the selection. The grid refreshes
    automatically every 2 seconds to pick up newly created windows.
    """

    _REFRESH_INTERVAL_MS = 2000

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self._session: Optional[PipelineSession] = None
        self._tiles: Dict[int, PreviewTile] = {}  # handle -> tile
        self._selected_win_info: Optional[WindowInfo] = None

        self.setWindowTitle("Upscaler – Select Window")
        self.setMinimumSize(600, 400)

        self._setup_ui()
        self._populate_grid()

        # Auto refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh_grid)
        self._refresh_timer.start(self._REFRESH_INTERVAL_MS)

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        # ---- Header ----
        header = QHBoxLayout()
        self._title_label = QLabel("Choose a window to upscale")
        self._title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #ccc;"
        )
        header.addWidget(self._title_label)
        header.addStretch()

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by title…")
        self.filter_edit.setFixedWidth(260)
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        header.addWidget(self.filter_edit)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_grid)
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px 12px;
                color: #eee;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #333;
            }
            """
        )
        header.addWidget(refresh_btn)

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

        # Empty state label (overlaid when grid is empty)
        self._empty_label = QLabel("No windows found", self.grid_widget)
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet("color: #666; font-size: 18px;")
        self._empty_label.hide()

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

    # ------------------------------------------------------------------
    #  Grid management
    # ------------------------------------------------------------------

    def _populate_grid(self, filter_text: str = "") -> None:
        """Re‑read the window list and update tiles (preserve unchanged ones)."""
        try:
            windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        own_handle = int(self.winId())
        filter_lower = filter_text.lower().strip()

        # Build a set of handles that are visible
        visible = set()
        new_tiles = {}

        for win in windows:
            if win.handle == own_handle:
                continue
            if not win.title.strip():
                continue
            if filter_lower and filter_lower not in win.title.lower():
                continue
            visible.add(win.handle)

            # Reuse existing tile if available
            if win.handle in self._tiles:
                tile = self._tiles[win.handle]
                # The preview is still active; just keep it
                new_tiles[win.handle] = tile
            else:
                tile = PreviewTile(win, parent=self.grid_widget)
                tile.clicked.connect(self._on_tile_clicked)
                new_tiles[win.handle] = tile

        # Remove tiles that are no longer visible
        for handle, tile in self._tiles.items():
            if handle not in visible:
                tile.stop()
                self.grid_layout.removeWidget(tile)
                tile.deleteLater()

        self._tiles = new_tiles

        # Rearrange the grid
        self._relayout_grid()

    def _relayout_grid(self) -> None:
        """Place tiles in a grid, updating empty state."""
        # Remove all widgets from grid (but tiles are still alive)
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)  # detach temporarily

        tile_list = list(self._tiles.values())
        if not tile_list:
            self._empty_label.show()
            self._update_title_count(0)
            return
        self._empty_label.hide()

        # Compute columns
        columns = max(1, (self.grid_widget.width() - 20) // (PreviewTile.TILE_W + 16))
        row = col = 0
        for tile in tile_list:
            self.grid_layout.addWidget(tile, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self._update_title_count(len(tile_list))

    def _update_title_count(self, count: int) -> None:
        """Update the header text with the window count."""
        if count == 0:
            self._title_label.setText("Choose a window to upscale")
        else:
            self._title_label.setText(
                f"Choose a window to upscale – {count} window{'s' if count != 1 else ''}"
            )

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------

    @Slot()
    def _refresh_grid(self) -> None:
        """Refresh the entire grid, preserving the current filter."""
        self._populate_grid(self.filter_edit.text())

    @Slot(str)
    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text)

    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        self._selected_win_info = win_info
        self._on_start()

    def _on_start(self) -> None:
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        activate_window(win_info.handle)
        logger.info("Starting upscale for: %s", win_info.title)

        self.hide()
        for tile in self._tiles.values():
            tile.stop()

        try:
            self._session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    # ------------------------------------------------------------------
    #  Cleanup
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        self._refresh_timer.stop()
        for tile in self._tiles.values():
            tile.stop()
        super().closeEvent(event)
