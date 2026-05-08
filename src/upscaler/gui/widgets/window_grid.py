from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import QWidget, QScrollArea, QGridLayout, QLabel

from .preview_tile import PreviewTile
from ...window import WindowInfo


class WindowGrid(QScrollArea):
    """
    A scrollable mosaic of live preview tiles.

    Features:
        - Automatic layout in columns based on available width.
        - Keyboard navigation (arrows, enter, space, escape).
        - Hover pop‑out animation handled by each `PreviewTile`.
        - Selection state management.
    """

    # Emitted when the user confirms a window choice (click / enter)
    window_selected = Signal(WindowInfo)

    # To avoid rebuilding the grid too often, we track maximum visible columns.
    _MIN_COLUMNS = 1
    _SCROLL_MARGIN = 20

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self._cfg = gui_config

        # Container widget that will be laid out manually.
        self._grid_container = QWidget()
        self._grid_container.setAttribute(
            Qt.WA_PaintUnclipped
        )  # allow tiles to paint outside
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(
            gui_config.grid_margin,
            gui_config.grid_margin,
            gui_config.grid_margin,
            gui_config.grid_margin,
        )
        self._grid_layout.setSpacing(gui_config.tile_spacing)

        self.setWidget(self._grid_container)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setStyleSheet("background: transparent; border: none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Empty placeholder
        self._empty_label = QLabel(gui_config.empty_text, self._grid_container)
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setStyleSheet(
            f"color: {gui_config.empty_text_color}; font-size: {gui_config.empty_text_size}px;"
        )
        self._empty_label.hide()

        # Internal state
        self._tiles: List[PreviewTile] = []
        self._selected_index: int = -1
        self._columns: int = 1

        # Accept keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def set_windows(self, windows: List[WindowInfo]) -> None:
        """
        Replace the displayed tiles with the given list of windows.

        Existing tiles are reused when their handle matches; old ones
        are stopped and destroyed.
        """
        # Build a map of existing tiles by handle
        old_tiles = {tile.window_info.handle: tile for tile in self._tiles}
        new_tiles: List[PreviewTile] = []

        for win in windows:
            if win.handle in old_tiles:
                tile = old_tiles[win.handle]
            else:
                tile = PreviewTile(win, self._cfg, parent=self._grid_container)
                tile.clicked.connect(self._on_tile_clicked)
            new_tiles.append(tile)

        # Stop and remove tiles that are no longer in the list
        for tile in self._tiles:
            if tile not in new_tiles:
                tile.stop()
                tile.setParent(None)
                tile.deleteLater()

        self._tiles = new_tiles
        self._relayout_grid()
        self._restore_selection()

    def clear_selection(self) -> None:
        """Remove any current selection (e.g., when filter changes)."""
        if 0 <= self._selected_index < len(self._tiles):
            self._tiles[self._selected_index].selected = False
        self._selected_index = -1

    def clear_all(self) -> None:
        """Stop and remove all tiles (used before pipeline launch)."""
        for tile in self._tiles:
            tile.stop()
        self._tiles.clear()
        self._selected_index = -1
        # Remove all widgets from layout
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def selected_window(self) -> Optional[WindowInfo]:
        if 0 <= self._selected_index < len(self._tiles):
            return self._tiles[self._selected_index].window_info
        return None

    # ------------------------------------------------------------------
    #  Layout logic
    # ------------------------------------------------------------------
    def _relayout_grid(self) -> None:
        """Recalculate number of columns and reposition tiles."""
        # Remove all items from grid layout (but keep widgets)
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            # We don't delete the widget; it stays in self._grid_container

        if not self._tiles:
            self._empty_label.show()
            return
        self._empty_label.hide()

        # Determine number of columns
        available_width = self.viewport().width()
        if available_width <= 0:
            available_width = self.width() - 40  # fallback
        tile_width = self._cfg.tile_width + self._cfg.tile_spacing
        self._columns = max(1, available_width // tile_width)

        # Grid layout: row, col
        for i, tile in enumerate(self._tiles):
            row = i // self._columns
            col = i % self._columns
            # Ensure the widget is still a child of the container
            if tile.parent() != self._grid_container:
                tile.setParent(self._grid_container)
            self._grid_layout.addWidget(tile, row, col)

        # Scroll to keep selected tile visible
        self._ensure_selected_visible()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        # Re‑layout only when the number of columns might change
        new_cols = self._calculate_columns()
        if new_cols != self._columns:
            self._relayout_grid()

    def _calculate_columns(self) -> int:
        viewport_width = self.viewport().width()
        if viewport_width <= 0:
            viewport_width = self.width() - 40
        tile_width = self._cfg.tile_width + self._cfg.tile_spacing
        return max(1, (viewport_width - self._SCROLL_MARGIN) // tile_width)

    # ------------------------------------------------------------------
    #  Selection handling
    # ------------------------------------------------------------------
    def _set_selection(self, index: int) -> None:
        """Change the selected tile, deselecting the previous one."""
        if 0 <= self._selected_index < len(self._tiles):
            self._tiles[self._selected_index].selected = False
        self._selected_index = index
        if 0 <= index < len(self._tiles):
            tile = self._tiles[index]
            tile.selected = True
            self._ensure_tile_visible(tile)

    def _restore_selection(self) -> None:
        """Try to keep the same window selected after a refresh."""
        if self._selected_index != -1 and self._selected_index < len(self._tiles):
            # The index might have changed; better to match by handle
            current_handle = self._tiles[self._selected_index].window_info.handle
            for i, tile in enumerate(self._tiles):
                if tile.window_info.handle == current_handle:
                    self._set_selection(i)
                    return
        self.clear_selection()

    def _ensure_selected_visible(self) -> None:
        """Scroll so the selected tile is in view."""
        if 0 <= self._selected_index < len(self._tiles):
            self._ensure_tile_visible(self._tiles[self._selected_index])

    def _ensure_tile_visible(self, tile: PreviewTile) -> None:
        self.ensureWidgetVisible(
            tile, xmargin=self._SCROLL_MARGIN, ymargin=self._SCROLL_MARGIN
        )

    # ------------------------------------------------------------------
    #  Keyboard navigation
    # ------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            sel = self.selected_window()
            if sel:
                self.window_selected.emit(sel)
            return

        if key == Qt.Key_Right:
            self._move_selection(1)
        elif key == Qt.Key_Left:
            self._move_selection(-1)
        elif key == Qt.Key_Down:
            self._move_selection(self._columns)
        elif key == Qt.Key_Up:
            self._move_selection(-self._columns)
        elif key == Qt.Key_Escape:
            self.clear_selection()
        else:
            super().keyPressEvent(event)

    def _move_selection(self, delta: int) -> None:
        if not self._tiles:
            return
        if self._selected_index == -1:
            new_idx = 0 if delta > 0 else len(self._tiles) - 1
        else:
            new_idx = max(0, min(len(self._tiles) - 1, self._selected_index + delta))
        self._set_selection(new_idx)

    # ------------------------------------------------------------------
    #  Slot for tile clicks
    # ------------------------------------------------------------------
    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        # Update selection and emit
        for i, tile in enumerate(self._tiles):
            if tile.window_info.handle == win_info.handle:
                self._set_selection(i)
                self.window_selected.emit(win_info)
                return
        # If we didn't find (shouldn't happen), emit anyway as fallback
        self.window_selected.emit(win_info)

    # ------------------------------------------------------------------
    #  Hover management (pop‑out is done in PreviewTile, grid only
    #  ensures no multiple pop‑outs)
    # ------------------------------------------------------------------
    def _tile_enter(self, tile: PreviewTile) -> None:
        # Optional: could stop other tiles' animations, but it's fine
        pass

    def _tile_leave(self, tile: PreviewTile) -> None:
        pass
