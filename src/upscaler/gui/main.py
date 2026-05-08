from __future__ import annotations

import logging
from typing import List, Optional, Dict, TYPE_CHECKING

from PySide6.QtCore import Qt, Slot, QTimer, QEvent
from PySide6.QtGui import QKeyEvent
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

_STYLESHEET = """
QMainWindow { background: #121212; }
QLineEdit {
    border: 1px solid #444; border-radius: 4px; padding: 6px;
    font-size: 13px; background: #2a2a2a; color: #eee;
}
QLineEdit:focus { border-color: #2b5b84; }
QScrollArea { background: transparent; }
"""

_REFRESH_BUTTON_STYLE = """
QPushButton {
    background: #2a2a2a; border: 1px solid #444;
    border-radius: 4px; padding: 6px 12px; color: #eee; font-size: 13px;
}
QPushButton:hover { background: #333; }
QPushButton:disabled { color: #666; }
"""

TITLE_STYLE = "font-size: 16px; font-weight: bold; color: #ccc;"
EMPTY_STYLE = "color: #666; font-size: 18px;"


class SelectorWindow(QMainWindow):
    _AUTO_REFRESH_MS = 2000
    _ANIM_DURATION_MS = 400

    def __init__(self, config: Config, profiles: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.profiles = profiles
        self._session: Optional[PipelineSession] = None
        self._tiles: Dict[int, PreviewTile] = {}
        self._tile_order: List[PreviewTile] = []
        self._selected_index: int = -1
        self._selected_win_info: Optional[WindowInfo] = None
        self._refresh_btn: Optional[QPushButton] = None
        self._first_layout_done = False

        self.setWindowTitle("Upscaler – Select Window")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._auto_timer = QTimer(self)
        self._auto_timer.timeout.connect(self._auto_refresh)
        self._auto_timer.start(self._AUTO_REFRESH_MS)
        QTimer.singleShot(0, self._initial_populate)

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        self._central = central
        central.installEventFilter(self)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)

        # Header
        header = QHBoxLayout()
        self._title_label = QLabel("Choose a window to upscale")
        self._title_label.setStyleSheet(TITLE_STYLE)
        header.addWidget(self._title_label)
        header.addStretch()

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter by title…")
        self.filter_edit.setFixedWidth(260)
        self.filter_edit.textChanged.connect(self._on_filter_changed)
        self.filter_edit.installEventFilter(self)
        header.addWidget(self.filter_edit)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self._manual_refresh)
        self._refresh_btn.setStyleSheet(_REFRESH_BUTTON_STYLE)
        header.addWidget(self._refresh_btn)
        layout.addLayout(header)

        # Scrollable grid
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_widget = QWidget()
        self.grid_widget.setFocusPolicy(Qt.StrongFocus)
        self.grid_widget.installEventFilter(self)
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        self.grid_layout.setSpacing(12)
        self._scroll.setWidget(self.grid_widget)
        layout.addWidget(self._scroll, stretch=1)

        self._empty_label = QLabel("No windows found", self.grid_widget)
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(EMPTY_STYLE)
        self._empty_label.hide()

        self.setStyleSheet(_STYLESHEET)

    # ------------------------------------------------------------------
    #  Initial population
    # ------------------------------------------------------------------
    def _initial_populate(self) -> None:
        if self._first_layout_done:
            return
        self._first_layout_done = True
        self._populate_grid()
        self.grid_widget.setFocus()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        QTimer.singleShot(50, self._relayout_grid)
        self.showMaximized()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._first_layout_done:
            QTimer.singleShot(0, self._relayout_grid)

    # ------------------------------------------------------------------
    #  Grid population
    # ------------------------------------------------------------------
    def _populate_grid(self, filter_text: str = "", animate: bool = False) -> None:
        try:
            windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        own_handle = int(self.winId())
        filter_lower = filter_text.lower().strip()

        visible = set()
        new_tiles: Dict[int, PreviewTile] = {}

        for win in windows:
            if win.handle == own_handle:
                continue
            if not win.title.strip():
                continue
            if filter_lower and filter_lower not in win.title.lower():
                continue
            visible.add(win.handle)

            if win.handle in self._tiles:
                tile = self._tiles[win.handle]
                new_tiles[win.handle] = tile
            else:
                tile = PreviewTile(win, parent=self.grid_widget)
                tile.clicked.connect(self._on_tile_clicked)
                new_tiles[win.handle] = tile

        for handle, tile in self._tiles.items():
            if handle not in visible:
                tile.stop()
                self.grid_layout.removeWidget(tile)
                tile.deleteLater()

        self._tiles = new_tiles
        self._tile_order = [t for t in self._tiles.values()]

        self._restore_selection()
        self._relayout_grid()

        if animate:
            for tile in self._tiles.values():
                if tile.window_info.handle in self._tiles:
                    tile.animate_in()

    def _restore_selection(self) -> None:
        if self._selected_win_info is not None:
            for i, tile in enumerate(self._tile_order):
                if tile.window_info.handle == self._selected_win_info.handle:
                    self._set_selection(i)
                    return
            self._clear_selection()

    def _relayout_grid(self) -> None:
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        if not self._tile_order:
            self._empty_label.show()
            self._update_title_count(0)
            return
        self._empty_label.hide()

        vp_width = self._scroll.viewport().width()
        if vp_width <= 0:
            vp_width = self.width() - 40
        columns = max(1, (vp_width - 20) // (PreviewTile.TILE_W + 16))
        row = col = 0
        for tile in self._tile_order:
            self.grid_layout.addWidget(tile, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self._update_title_count(len(self._tile_order))
        self._ensure_selected_visible()

    def _update_title_count(self, count: int) -> None:
        suffix = "s" if count != 1 else ""
        self._title_label.setText(
            f"Choose a window to upscale – {count} window{suffix}"
        )

    # ------------------------------------------------------------------
    #  Refresh logic
    # ------------------------------------------------------------------
    def _auto_refresh(self) -> None:
        self._populate_grid(self.filter_edit.text(), animate=False)

    def _manual_refresh(self) -> None:
        if self._refresh_btn is None:
            return
        self._refresh_btn.setText("Refreshing…")
        self._refresh_btn.setEnabled(False)
        self._populate_grid(self.filter_edit.text(), animate=True)
        QTimer.singleShot(self._ANIM_DURATION_MS, self._enable_refresh_btn)

    def _enable_refresh_btn(self) -> None:
        if self._refresh_btn:
            self._refresh_btn.setText("Refresh")
            self._refresh_btn.setEnabled(True)

    # ------------------------------------------------------------------
    #  Focus & keyboard navigation
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event):
        if not hasattr(self, "grid_widget") or self.grid_widget is None:
            return super().eventFilter(obj, event)
        if obj == self.grid_widget and event.type() == QEvent.MouseButtonPress:
            self.grid_widget.setFocus()
            return False
        if (
            obj in (self._central, self.grid_widget, self.filter_edit)
            and event.type() == QEvent.KeyPress
        ):
            key = event.key()
            if self.filter_edit.hasFocus():
                if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape):
                    self.keyPressEvent(event)
                    return True
                return False
            if key in (
                Qt.Key_Up,
                Qt.Key_Down,
                Qt.Key_Left,
                Qt.Key_Right,
                Qt.Key_Return,
                Qt.Key_Enter,
                Qt.Key_Space,
                Qt.Key_Escape,
            ):
                self.keyPressEvent(event)
                return True
            return False
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            if 0 <= self._selected_index < len(self._tile_order):
                self._on_tile_clicked(
                    self._tile_order[self._selected_index].window_info
                )
            return
        elif key == Qt.Key_Right:
            self._keyboard_move(1)
        elif key == Qt.Key_Left:
            self._keyboard_move(-1)
        elif key == Qt.Key_Down:
            self._keyboard_move(self._columns_count())
        elif key == Qt.Key_Up:
            self._keyboard_move(-self._columns_count())
        elif key == Qt.Key_Escape:
            self._clear_selection()
            self._selected_win_info = None
        else:
            super().keyPressEvent(event)

    def _columns_count(self) -> int:
        vp_width = self._scroll.viewport().width()
        if vp_width <= 0:
            vp_width = self.width() - 40
        return max(1, (vp_width - 20) // (PreviewTile.TILE_W + 16))

    def _keyboard_move(self, delta: int) -> None:
        if not self._tile_order:
            return
        if self._selected_index == -1:
            new_idx = 0 if delta > 0 else len(self._tile_order) - 1
        else:
            new_idx = self._selected_index + delta
            new_idx = max(0, min(new_idx, len(self._tile_order) - 1))
        self._set_selection(new_idx)
        self._ensure_selected_visible()

    def _set_selection(self, index: int) -> None:
        if 0 <= self._selected_index < len(self._tile_order):
            self._tile_order[self._selected_index].selected = False
        self._selected_index = index
        if 0 <= index < len(self._tile_order):
            self._tile_order[index].selected = True
            self._selected_win_info = self._tile_order[index].window_info
        else:
            self._selected_win_info = None

    def _clear_selection(self) -> None:
        if 0 <= self._selected_index < len(self._tile_order):
            self._tile_order[self._selected_index].selected = False
        self._selected_index = -1

    def _ensure_selected_visible(self) -> None:
        if 0 <= self._selected_index < len(self._tile_order):
            self._scroll.ensureWidgetVisible(
                self._tile_order[self._selected_index], 20, 20
            )

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    @Slot(str)
    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text, animate=False)

    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        self._clear_selection()
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

    def closeEvent(self, event) -> None:
        self._auto_timer.stop()
        for tile in self._tiles.values():
            tile.stop()
        super().closeEvent(event)
