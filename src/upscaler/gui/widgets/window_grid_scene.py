from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Set

from PySide6.QtCore import Qt, Signal, QRectF, QTimer
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from .window_tile_item import WindowTileItem
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class WindowGridScene(QGraphicsScene):
    """
    A responsive, centred grid of live window‑preview tiles.

    The scene automatically arranges :class:`WindowTileItem` instances
    in rows of *grid_columns* (from :class:`GUIConfig`).  Each tile is
    sized so that the full row exactly fills the viewport width (minus
    margins and the proportional or fixed spacing).

    Key features:
        - Tile *width* is computed from the available space and the
          configured column count.  Height follows the aspect ratio of
          the default tile dimensions.
        - *Spacing* between tiles can be proportional to the tile width
          (e.g. 5%) with a configurable minimum absolute value.
        - Rows with fewer than *grid_columns* tiles are centred.
        - The whole grid block is centred horizontally and top‑aligned.
        - Layout is only recalculated when the set of window handles
          changes or the viewport width varies by more than 10 px,
          avoiding flicker during animations.
        - Keyboard navigation, selection, and focus management are
          built in.
    """

    # Emitted when the user confirms a window (click or Enter / Space)
    window_selected = Signal(WindowInfo)
    # Emitted when pressing Up on the first row (towards the search bar)
    focus_filter_requested = Signal()

    _SCENE_MARGIN = 10  # extra padding around the grid block

    def __init__(
        self,
        gui_config,
        parent: Optional[QGraphicsView] = None,
    ) -> None:
        """
        Parameters
        ----------
        gui_config : GUIConfig
            Centralised GUI settings.  The following fields are relevant:
            ``grid_columns``, ``grid_margin``, ``tile_width``,
            ``tile_height`` (used only for aspect ratio), ``tile_spacing``,
            ``tile_spacing_ratio``.
        parent : QGraphicsView, optional
            The view that will display this scene.
        """
        super().__init__(parent)
        self._cfg = gui_config

        # --- Tile storage ----------------------------------------------------
        self._tiles: List[WindowTileItem] = []  # ordered grid order
        self._tile_by_handle: Dict[int, WindowTileItem] = {}  # handle → tile
        self._selected_handle: Optional[int] = None

        # --- Layout state ----------------------------------------------------
        self._columns = 1
        self._rows = 0
        # used to avoid redundant relayouts during auto‑refresh
        self._last_handles: Set[int] = set()
        self._last_vp_width: float = 0.0

        # Debounced relayout timer
        self._relayout_timer = QTimer(self)
        self._relayout_timer.setSingleShot(True)
        self._relayout_timer.timeout.connect(self._perform_relayout)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def set_windows(self, windows: List[WindowInfo]) -> None:
        """
        Replace the contents of the grid with a new list of windows.

        Existing tiles are *reused* when their handle matches one in the
        new list; missing tiles are stopped and deleted, and new tiles
        are created as needed.  The selection is preserved if the
        previously selected window is still in the list.

        Parameters
        ----------
        windows : list of WindowInfo
            The windows to display, in the order they should appear
            (usually sorted by title or another criterion).
        """
        new_handles = {win.handle for win in windows}
        old_handles = set(self._tile_by_handle.keys())

        # Remove tiles that are no longer present
        for handle in old_handles - new_handles:
            self._remove_tile(handle)

        # Build new ordered list, reusing where possible
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
        self._restore_selection()

        # Only relayout if the set of handles changed or the viewport grew/shrunk
        if self._needs_relayout(new_handles):
            self.schedule_relayout()
        self._last_handles = new_handles

    def clear_all(self) -> None:
        """Remove all tiles and reset the selection."""
        # Release any active mouse grab to avoid 'ungrabMouse' warnings
        grabber = self.mouseGrabberItem()
        if grabber is not None:
            grabber.ungrabMouse()

        for handle in list(self._tile_by_handle.keys()):
            self._remove_tile(handle)
        self._tiles.clear()
        self._selected_handle = None

    def selected_window(self) -> Optional[WindowInfo]:
        """Return the currently selected window, or ``None``."""
        if self._selected_handle is not None:
            tile = self._tile_by_handle.get(self._selected_handle)
            if tile:
                return tile.window_info
        return None

    def focus_first_tile(self) -> None:
        """Set the selection to the first tile in the grid, if any."""
        if self._tiles:
            self._set_selected_handle(self._tiles[0].window_info.handle)

    # ------------------------------------------------------------------
    #  Layout
    # ------------------------------------------------------------------

    def schedule_relayout(self) -> None:
        """Request a debounced relayout (coalesces rapid calls)."""
        self._relayout_timer.start(0)

    def _perform_relayout(self) -> None:
        """
        Reposition all tiles according to the current viewport width.

        Tile width is determined by the number of target columns
        (``grid_columns``) and the available horizontal space.  Spacing
        can be proportional (``tile_spacing_ratio > 0``) or fixed, with
        a configurable minimum floor (``tile_spacing``).  The aspect
        ratio of each tile is derived from the default ``tile_width``
        and ``tile_height``.
        """
        tiles = self._tiles
        if not tiles:
            self.setSceneRect(QRectF())
            return

        cfg = self._cfg

        # Viewport width (fallback for headless testing)
        view = self.views()[0] if self.views() else None
        vp_w = view.viewport().width() if view else 800

        margin = cfg.grid_margin
        target_cols = cfg.grid_columns

        # ---- 1. Determine actual column count (never more than tiles) -------
        cols = min(target_cols, len(tiles))
        self._columns = cols
        self._rows = math.ceil(len(tiles) / cols)

        # ---- 2. Compute tile width (fixed to full row, not per row) --------
        avail_w = vp_w - 2 * margin
        if target_cols > 1:
            # We'll first estimate tile width without spacing, then loop once
            # to settle proportional spacing if needed.
            tile_w = avail_w / target_cols

        # ---- 3. Compute actual spacing (proportional or fixed) -------------
        if cfg.tile_spacing_ratio > 0:
            spacing = max(cfg.tile_spacing, int(tile_w * cfg.tile_spacing_ratio))
        else:
            spacing = cfg.tile_spacing

        # ---- 4. Recompute tile width with spacing --------------------------
        if target_cols > 1:
            total_spacing = (target_cols - 1) * spacing
            tile_w = max(100.0, (avail_w - total_spacing) / target_cols)
            # Re‑evaluate spacing if proportional (it depends on tile_w)
            if cfg.tile_spacing_ratio > 0:
                spacing = max(cfg.tile_spacing, int(tile_w * cfg.tile_spacing_ratio))
                total_spacing = (target_cols - 1) * spacing
                tile_w = max(100.0, (avail_w - total_spacing) / target_cols)
        else:
            # Single column – spacing is irrelevant
            tile_w = max(100.0, avail_w)

        # ---- 5. Tile height from aspect ratio ------------------------------
        if cfg.tile_aspect_ratio > 0:
            aspect = cfg.tile_aspect_ratio
        else:
            aspect = cfg.tile_width / cfg.tile_height if cfg.tile_height else 1.0
        tile_h = tile_w / aspect

        # ---- 6. Update tile sizes (resize if changed) ----------------------
        for tile in tiles:
            cur_w, cur_h = tile.tile_size()
            if abs(cur_w - tile_w) > 1 or abs(cur_h - tile_h) > 1:
                tile.set_tile_size(tile_w, tile_h)

        # ---- 7. Position tiles ---------------------------------------------
        # centre of the first tile in a full row
        full_row_width = cols * tile_w + (cols - 1) * spacing
        start_x = (vp_w - full_row_width) / 2.0 + tile_w / 2.0
        start_y = margin + tile_h / 2.0

        for i, tile in enumerate(tiles):
            row = i // cols
            col = i % cols
            # For rows with fewer tiles than *cols*, centre the row group
            tiles_in_this_row = min(cols, len(tiles) - row * cols)
            row_width = tiles_in_this_row * tile_w + (tiles_in_this_row - 1) * spacing
            row_start_x = (vp_w - row_width) / 2.0 + tile_w / 2.0
            cx = row_start_x + col * (tile_w + spacing)
            cy = start_y + row * (tile_h + spacing)
            tile.setPos(cx, cy)

        # ---- 8. Set scene rect to exactly contain the grid + margins --------
        total_h = margin * 2 + self._rows * tile_h + (self._rows - 1) * spacing
        self.setSceneRect(
            -self._SCENE_MARGIN,
            -self._SCENE_MARGIN,
            vp_w + 2 * self._SCENE_MARGIN,
            total_h + 2 * self._SCENE_MARGIN,
        )

        # ---- 9. Keep selected tile in view ---------------------------------
        self._ensure_selected_visible()

    def _needs_relayout(self, new_handles: Set[int]) -> bool:
        """
        Return ``True`` if the set of window handles has changed or the
        viewport width changed by more than 10 px since the last layout.
        """
        if new_handles != self._last_handles:
            return True
        view = self.views()[0] if self.views() else None
        if view:
            vp_w = view.viewport().width()
            if abs(vp_w - self._last_vp_width) > 10:
                self._last_vp_width = vp_w
                return True
            self._last_vp_width = vp_w
        return False

    # ------------------------------------------------------------------
    #  Tile lifecycle
    # ------------------------------------------------------------------

    def _remove_tile(self, handle: int) -> None:
        """Stop capture, remove from scene, and schedule deletion."""
        tile = self._tile_by_handle.pop(handle, None)
        if tile:
            tile.stop_capture()
            self.removeItem(tile)
            tile.deleteLater()

    # ------------------------------------------------------------------
    #  Selection management
    # ------------------------------------------------------------------

    def _set_selected_handle(self, handle: Optional[int]) -> None:
        """Change the selected tile, deselecting the previous one."""
        if handle == self._selected_handle:
            return
        if self._selected_handle is not None:
            prev = self._tile_by_handle.get(self._selected_handle)
            if prev:
                prev.selected = False
        self._selected_handle = handle
        if handle is not None:
            tile = self._tile_by_handle.get(handle)
            if tile:
                tile.selected = True
                self._ensure_tile_visible(tile)

    def _restore_selection(self) -> None:
        """Re‑apply the selection after the tile list was rebuilt."""
        if (
            self._selected_handle is not None
            and self._selected_handle in self._tile_by_handle
        ):
            self._set_selected_handle(self._selected_handle)
        else:
            self._set_selected_handle(None)

    def _ensure_selected_visible(self) -> None:
        """Scroll the view so the selected tile is visible."""
        if self._selected_handle is not None:
            tile = self._tile_by_handle.get(self._selected_handle)
            if tile:
                self._ensure_tile_visible(tile)

    @staticmethod
    def _ensure_tile_visible(tile: WindowTileItem) -> None:
        """Ask the associated view to ensure *tile* is visible."""
        view = (
            tile.scene().views()[0] if tile.scene() and tile.scene().views() else None
        )
        if view:
            view.ensureVisible(tile, 20, 20)

    # ------------------------------------------------------------------
    #  Event handlers
    # ------------------------------------------------------------------

    def _on_tile_clicked(self, win_info: WindowInfo) -> None:
        """Slot connected to every tile's ``clicked`` signal."""
        self._set_selected_handle(win_info.handle)
        self.window_selected.emit(win_info)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle keyboard navigation:

        - Enter / Return / Space : confirm the selected tile.
        - Arrow keys : move the selection.
        - Escape : clear the selection.
        All other keys are passed to the base class.
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
        tiles = self._tiles
        if not tiles:
            return

        cols = self._columns
        if self._selected_handle is None:
            # If no tile selected and Up is pressed, go to filter bar
            if key == Qt.Key_Up:
                self.focus_filter_requested.emit()
                return
            # Otherwise start from first tile for other arrows
            new_idx = 0
        else:
            # Locate current index
            current_idx = -1
            for i, tile in enumerate(tiles):
                if tile.window_info.handle == self._selected_handle:
                    current_idx = i
                    break
            if current_idx == -1:
                new_idx = 0
            else:
                row = current_idx // cols
                col = current_idx % cols
                if key == Qt.Key_Right:
                    col = min(col + 1, cols - 1)
                elif key == Qt.Key_Left:
                    col = max(col - 1, 0)
                elif key == Qt.Key_Down:
                    row = min(row + 1, self._rows - 1)
                    # Clamp column index to a possibly shorter last row
                    row_start_idx = row * cols
                    row_len = min(cols, len(tiles) - row_start_idx)
                    col = min(col, row_len - 1)
                if key == Qt.Key_Up:
                    if current_idx // cols == 0:
                        self._set_selected_handle(None)
                        self.focus_filter_requested.emit()
                        return
                    row = max(row - 1, 0)
                    row_start_idx = row * cols
                    row_len = min(cols, len(tiles) - row_start_idx)
                    col = min(col, row_len - 1)
                new_idx = row * cols + col

        new_idx = max(0, min(new_idx, len(tiles) - 1))
        self._set_selected_handle(tiles[new_idx].window_info.handle)

    # ------------------------------------------------------------------
    #  View attachment
    # ------------------------------------------------------------------

    def attach_view(self, view: QGraphicsView) -> None:
        """
        Inform the scene about the view that displays it.

        The view is configured to accept focus, ensuring keyboard events
        reach the scene.
        """
        self._view = view
        view.setFocusPolicy(Qt.StrongFocus)
        view.setFocus()
