from __future__ import annotations

import logging
from typing import Dict, List, Optional

from PySide6.QtCore import (
    Qt,
    Signal,
    QRectF,
    QTimer,
)
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from .window_tile_item import WindowTileItem
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class WindowGridScene(QGraphicsScene):
    """
    A scene that arranges :class:`WindowTileItem` instances in a
    responsive grid. It handles:

    * Automatic layout with configurable margins, spacing, and columns.
    * Efficient reuse of existing tiles when the window list changes
      (keyed by window handle).
    * Keyboard navigation (arrow keys, Enter, Space, Escape).
    * Single‑selection model that emits :attr:`window_selected` when the
      user confirms a tile.
    * Hover‑driven z‑ordering to make the popped tile appear above
      neighbours.

    All visual parameters are taken from the :class:`GUIConfig` instance
    passed to the constructor.
    """

    # Emitted when the user confirms a window (click or Enter/Space)
    window_selected = Signal(WindowInfo)

    # Constants
    _SCENE_MARGIN = 10  # small extra padding around the grid

    def __init__(self, gui_config, parent: Optional[QGraphicsView] = None) -> None:
        super().__init__(parent)
        self._cfg = gui_config

        # Tile data structures
        self._tiles: List[WindowTileItem] = []  # ordered list (grid order)
        self._tile_by_handle: Dict[int, WindowTileItem] = {}  # for reuse
        self._selected_handle: Optional[int] = None

        # Layout state
        self._columns = 1
        self._rows = 0

        # We need to handle key events at the scene level for navigation
        # when no item has focus. We'll install an event filter on the view
        # when attached, but for now we override keyPressEvent.

        # A QTimer for debounced relayout (optional)
        self._relayout_timer = QTimer(self)
        self._relayout_timer.setSingleShot(True)
        self._relayout_timer.timeout.connect(self.relayout)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def set_windows(self, windows: List[WindowInfo]) -> None:
        """
        Replace the displayed tiles with the given list.

        Tiles for windows that are already in the scene are preserved
        (including their capture state and animation).  New windows get
        freshly created :class:`WindowTileItem` instances.  Windows no
        longer in the list have their tiles removed.
        """
        new_handles = {win.handle for win in windows}
        old_handles = set(self._tile_by_handle.keys())

        # Remove tiles that are no longer in the list
        for handle in old_handles - new_handles:
            self._remove_tile(handle)

        # Create missing tiles and build the ordered list
        new_tiles: List[WindowTileItem] = []
        for win in windows:
            if win.handle in self._tile_by_handle:
                tile = self._tile_by_handle[win.handle]
            else:
                tile = WindowTileItem(win, self._cfg)
                tile.clicked.connect(self._on_tile_clicked)
                self.addItem(tile)
                self._tile_by_handle[win.handle] = tile
            new_tiles.append(tile)

        self._tiles = new_tiles

        # Restore selection if possible
        self._restore_selection()

        # Trigger relayout (debounced)
        self.schedule_relayout()

    def clear_all(self) -> None:
        """Remove all tiles and reset state."""
        for handle in list(self._tile_by_handle.keys()):
            self._remove_tile(handle)
        self._tiles.clear()
        self._selected_handle = None

    def selected_window(self) -> Optional[WindowInfo]:
        """Return the currently selected window, or `None`."""
        if self._selected_handle is not None:
            tile = self._tile_by_handle.get(self._selected_handle)
            if tile:
                return tile.window_info
        return None

    def focus_first_tile(self) -> None:
        """Select the first tile in the grid, if any."""
        if self._tiles:
            self._set_selected_handle(self._tiles[0].window_info.handle)

    # ------------------------------------------------------------------
    #  Layout
    # ------------------------------------------------------------------

    def schedule_relayout(self) -> None:
        """Debounce relayout to avoid redundant work during rapid updates."""
        self._relayout_timer.start(0)  # coalesced

    def relayout(self) -> None:
        """
        Position tiles in a grid based on current viewport width and
        update the scene rect accordingly.
        """
        if not self._tiles:
            self.setSceneRect(QRectF())
            return

        cfg = self._cfg
        margin = cfg.grid_margin
        spacing = cfg.tile_spacing
        tile_w = cfg.tile_width
        tile_h = cfg.tile_height

        # Determine number of columns from the attached view, if any
        view = self.views()[0] if self.views() else None
        if view:
            vp_width = view.viewport().width()
        else:
            vp_width = tile_w * 3 + 2 * spacing + 2 * margin  # fallback

        cols = max(1, (vp_width - margin * 2 + spacing) // (tile_w + spacing))
        self._columns = cols

        # Position tiles (setPos of each tile)
        for i, tile in enumerate(self._tiles):
            col = i % cols
            row = i // cols
            x = margin + col * (tile_w + spacing)
            y = margin + row * (tile_h + spacing)
            tile.setPos(x, y)

        # Update scene rect to contain all tiles plus some padding
        rows = (len(self._tiles) + cols - 1) // cols
        self._rows = rows
        total_w = margin * 2 + cols * tile_w + (cols - 1) * spacing
        total_h = margin * 2 + rows * tile_h + (rows - 1) * spacing
        self.setSceneRect(
            -self._SCENE_MARGIN,
            -self._SCENE_MARGIN,
            total_w + 2 * self._SCENE_MARGIN,
            total_h + 2 * self._SCENE_MARGIN,
        )

        # Ensure selected tile is visible
        self._ensure_selected_visible()

    # ------------------------------------------------------------------
    #  Tile management
    # ------------------------------------------------------------------

    def _remove_tile(self, handle: int) -> None:
        """Safely remove a tile from the scene."""
        tile = self._tile_by_handle.pop(handle, None)
        if tile is not None:
            tile.stop_capture()
            self.removeItem(tile)
            # deleteLater is safe because we're in the GUI thread
            tile.deleteLater()

    # ------------------------------------------------------------------
    #  Selection logic
    # ------------------------------------------------------------------

    def _set_selected_handle(self, handle: Optional[int]) -> None:
        """Update the selected tile."""
        # Deselect previous
        if self._selected_handle is not None:
            prev_tile = self._tile_by_handle.get(self._selected_handle)
            if prev_tile:
                prev_tile.selected = False
                prev_tile.update()

        self._selected_handle = handle

        if handle is not None:
            tile = self._tile_by_handle.get(handle)
            if tile:
                tile.selected = True
                tile.update()
                self._ensure_tile_visible(tile)

    def _restore_selection(self) -> None:
        """Keep the same window selected after a list refresh."""
        if (
            self._selected_handle is not None
            and self._selected_handle in self._tile_by_handle
        ):
            # It's still there, so just reaffirm selection
            self._set_selected_handle(self._selected_handle)
        else:
            self._set_selected_handle(None)

    def _ensure_selected_visible(self) -> None:
        """Scroll the view (if any) to make the selected tile visible."""
        if self._selected_handle is not None:
            tile = self._tile_by_handle.get(self._selected_handle)
            if tile:
                self._ensure_tile_visible(tile)

    def _ensure_tile_visible(self, tile: WindowTileItem) -> None:
        """Ask the associated view to ensure the tile is visible."""
        view = self.views()[0] if self.views() else None
        if view:
            view.ensureVisible(tile, 20, 20)

    # ------------------------------------------------------------------
    #  Event handlers
    # ------------------------------------------------------------------

    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        """Slot connected to each tile's clicked signal."""
        self._set_selected_handle(win_info.handle)
        self.window_selected.emit(win_info)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle keyboard navigation:
        - Enter / Return / Space: confirm selection
        - Arrow keys: move selection
        - Escape: clear selection
        """
        key = event.key()

        if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            sw = self.selected_window()
            if sw:
                self.window_selected.emit(sw)
            event.accept()
            return

        if key in (Qt.Key_Right, Qt.Key_Left, Qt.Key_Down, Qt.Key_Up):
            self._move_selection(key)
            event.accept()
            return

        if key == Qt.Key_Escape:
            self._set_selected_handle(None)
            event.accept()
            return

        super().keyPressEvent(event)

    def _move_selection(self, key: int) -> None:
        """Move the selection highlight in response to an arrow key."""
        if not self._tiles:
            return

        cols = self._columns
        if self._selected_handle is None:
            # Start from first tile
            new_idx = 0
        else:
            # Find index of currently selected tile
            current_idx = -1
            for i, tile in enumerate(self._tiles):
                if tile.window_info.handle == self._selected_handle:
                    current_idx = i
                    break
            if current_idx == -1:
                new_idx = 0
            else:
                row = current_idx // cols
                col = current_idx % cols
                if key == Qt.Key_Right:
                    new_col = min(col + 1, cols - 1)
                    new_idx = row * cols + new_col
                elif key == Qt.Key_Left:
                    new_col = max(col - 1, 0)
                    new_idx = row * cols + new_col
                elif key == Qt.Key_Down:
                    new_row = min(row + 1, self._rows - 1)
                    # Stay in same column, but might be shorter row
                    new_idx = min(new_row * cols + col, len(self._tiles) - 1)
                elif key == Qt.Key_Up:
                    new_row = max(row - 1, 0)
                    new_idx = min(new_row * cols + col, len(self._tiles) - 1)
                else:
                    return

        new_idx = max(0, min(new_idx, len(self._tiles) - 1))
        new_tile = self._tiles[new_idx]
        self._set_selected_handle(new_tile.window_info.handle)
        self._ensure_tile_visible(new_tile)

    # ------------------------------------------------------------------
    #  View attachment helper
    # ------------------------------------------------------------------

    def attach_view(self, view: QGraphicsView) -> None:
        """
        Connect the scene to a view.  This allows the scene to respond to
        resize events and ensures the view has the correct properties.
        """
        # The view already has the scene set; we just record it.
        self._view = view

        # Give the scene keyboard focus when the view is clicked.
        view.setFocusPolicy(Qt.StrongFocus)
        view.setFocus()
