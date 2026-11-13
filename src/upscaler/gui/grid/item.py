from __future__ import annotations

import logging
import os
import re
from typing import Optional, Tuple, TYPE_CHECKING

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QRectF,
    Property,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QPointF,
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
    QColor,
    QFont,
    QPen,
    QPainterPath,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsObject,
    QGraphicsItem,
    QGraphicsSceneContextMenuEvent,
    QMenu,
    QStyleOptionGraphicsItem,
    QWidget,
)

from ..styles import dropdown_submenu_style
from ...capture import FrameGrabber
from ...window import WindowInfo

if TYPE_CHECKING:
    from ..config import GUIConfig

logger = logging.getLogger(__name__)

BADGE_HEIGHT = 22
BADGE_INSET = 8
BADGE_EXTRA_WIDTH = 10

MORE_BUTTON_SIZE = 22
MORE_BUTTON_INSET = 8
MORE_ICON_DOT_RADIUS = 1.5
MORE_ICON_DOT_SPACING = 4.0


class _BadgeHitArea(QGraphicsItem):
    """Invisible child item scoping the profile tooltip to the badge region."""

    def __init__(self, parent: QGraphicsItem) -> None:
        super().__init__(parent)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setAcceptHoverEvents(False)
        self._rect = QRectF()

    def set_geometry(self, x: float, y: float, w: float, h: float) -> None:
        """Move/resize in parent-local coordinates. w or h ≤ 0 disables hit-testing."""
        self.prepareGeometryChange()
        self.setPos(x, y)
        self._rect = QRectF(0.0, 0.0, w, h)

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(self, painter, option, widget=None) -> None:
        pass


def _profile_initials(name: str, limit: int = 2) -> str:
    """Short label for a profile badge, up to `limit` characters."""
    # Strip parenthetical clarifications
    stripped = re.sub(r"\([^)]*\)", "", name).strip()
    if stripped:
        name = stripped

    words = [w for w in name.split() if any(c.isalnum() for c in w)]
    if not words:
        return "?"

    def first_alnum(s: str) -> str:
        return next((c for c in s if c.isalnum()), "")

    # Multi-word, first letter of each word capped at `limit`
    if len(words) >= 2:
        return "".join(first_alnum(w) for w in words[:limit]).upper()

    # Single word
    alnum = "".join(c for c in words[0] if c.isalnum())
    if not alnum:
        return "?"

    # Token fits within the limit
    if len(alnum) <= limit:
        return alnum.upper()

    # Uppercase acronym
    upper_run = 0
    for c in alnum:
        if c.isupper():
            upper_run += 1
        else:
            break
    if upper_run >= limit:
        return alnum[:limit].upper()

    return alnum[0].upper()


class WindowTileItem(QGraphicsObject):
    """
    A single live-preview tile in the window-selection mosaic.

    Local coordinates are **centered** at (0,0), so scaling expands
    symmetrically.  A constant bounding rectangle, pre-computed for
    the maximum pop-out scale plus shadow, is returned by
    :meth:`boundingRect`: this avoids layout recalculations during
    animations and makes keyboard navigation flicker-free.

    All visual parameters are taken from a :class:`GUIConfig` instance.

    Signals:
        clicked(WindowInfo)
    """

    clicked = Signal(WindowInfo)
    open_in_window_requested = Signal(WindowInfo)
    create_profile_requested = Signal(WindowInfo)
    copy_info_requested = Signal(WindowInfo)

    # ------------------------------------------------------------------
    #  Initialisation
    # ------------------------------------------------------------------

    def __init__(
        self,
        win_info: WindowInfo,
        gui_config: GUIConfig,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent)
        self._win_info: WindowInfo = win_info
        self._gui_config: GUIConfig = gui_config
        self._grid_focused: bool = True
        self._more_button_hovered: bool = False
        self._matched_profile: Optional[str] = None
        self._profile_pixmap: Optional[QPixmap] = None
        self._profile_pixmap_path: Optional[str] = None

        # --- Geometry -------------------------------------------------------
        self._half_w = gui_config.tile.width / 2.0
        self._half_h = gui_config.tile.height / 2.0
        self._tile_size = (gui_config.tile.width, gui_config.tile.height)
        self._max_bounding_rect = self._compute_max_bounding_rect()

        # --- State (hover & selection determine the animation target) -------
        self._hover = False
        self._selected = False
        self._scale = 1.0  # current scale (animated)
        self._target_scale = 1.0  # desired scale (1.0 or pop_scale)

        # --- Badge -------
        self._badge_label: Optional[str] = None
        self._badge_font: Optional[QFont] = None

        # --- Animation ------------------------------------------------------
        self._anim = QPropertyAnimation(self, b"scale", self)
        self._anim.setDuration(gui_config.tile.pop_duration)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        # --- Capture --------------------------------------------------------
        self._grabber: Optional[FrameGrabber] = None
        self._scaled_pixmap: Optional[QPixmap] = None
        self._full_w = 0
        self._full_h = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(gui_config.tile_preview_interval_ms)

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self._badge_hit = _BadgeHitArea(self)
        self._init_grabber()
        self._timer.start()

        if not gui_config.tile.show_title:
            self.setToolTip(self._win_info.title)

    # ------------------------------------------------------------------
    #  Geometry helpers
    # ------------------------------------------------------------------

    def _resting_rect(self) -> QRectF:
        return QRectF(-self._half_w, -self._half_h, self._half_w * 2, self._half_h * 2)

    def _compute_max_bounding_rect(self) -> QRectF:
        base = self._resting_rect()
        s = self._gui_config.tile.pop_scale
        shadow = 4.0 * s
        w = base.width() * s + 2.0 * shadow
        h = base.height() * s + 2.0 * shadow
        return QRectF(-w / 2.0, -h / 2.0, w, h)

    def boundingRect(self) -> QRectF:
        return self._max_bounding_rect

    def tile_size(self) -> Tuple[float, float]:
        return self._tile_size

    def set_tile_size(self, width: float, height: float) -> None:
        """Resize the tile. Stops animation, resets scale, clears cache."""
        self._anim.stop()
        self._half_w = width / 2.0
        self._half_h = height / 2.0
        self._tile_size = (width, height)
        self._scale = 1.0
        self._target_scale = 1.0
        self._max_bounding_rect = self._compute_max_bounding_rect()
        self._scaled_pixmap = None
        self._sync_badge_hit()
        self.update()
        self._update_animation_target()

    # ------------------------------------------------------------------
    #  Scale property (animated)
    # ------------------------------------------------------------------

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, value: float) -> None:
        if self._scale != value:
            self._scale = value
            self.update()

    scale = Property(float, get_scale, set_scale)

    # ------------------------------------------------------------------
    #  Animation target (unified for hover & selection)
    # ------------------------------------------------------------------

    def set_hover(self, hover: bool) -> None:
        """Programmatically set the hover state (used when focus leaves the grid)."""
        if self._hover == hover:
            return
        self._hover = hover
        self.setZValue(1 if hover else 0)
        self.update()
        self._update_animation_target()

    def set_grid_focused(self, focused: bool) -> None:
        """Tell the tile whether the owning grid currently has focus."""
        if self._grid_focused == focused:
            return
        self._grid_focused = focused
        self.update()
        self._update_animation_target()

    def _update_animation_target(self) -> None:
        """Re-evaluate the pop target and animate toward it."""
        target = self._gui_config.tile.pop_scale if self._hover else 1.0
        if target == self._target_scale:
            return
        self._target_scale = target
        self._anim.stop()
        self._anim.setStartValue(self._scale)
        self._anim.setEndValue(target)
        self._anim.start()

    # ------------------------------------------------------------------
    #  Profiles match
    # ------------------------------------------------------------------

    def set_matched_profile(
        self, name: Optional[str], icon_path: Optional[str] = None
    ) -> None:
        """Set the matched profile for the corner badge (None clears it)."""
        if self._matched_profile == name and self._profile_pixmap_path == icon_path:
            return
        self._matched_profile = name
        self._profile_pixmap_path = icon_path

        # Load the icon
        if icon_path and os.path.isfile(icon_path):
            self._profile_pixmap = QPixmap(icon_path)
            if self._profile_pixmap.isNull():
                self._profile_pixmap = None
        else:
            self._profile_pixmap = None

        # Build label + cached font
        if name and self._profile_pixmap is None:
            self._badge_label = _profile_initials(name)
            family = self._gui_config.font_family
            f = QFont(family) if family else QFont(QApplication.font())
            f.setPointSize(12 if len(self._badge_label) == 1 else 10)
            f.setBold(True)
            self._badge_font = f
        else:
            self._badge_label = None
            self._badge_font = None

        self._sync_badge_hit()
        self.update()

    # ------------------------------------------------------------------
    #  Selection state (managed by WindowGridScene)
    # ------------------------------------------------------------------

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        if self._selected != value:
            self._selected = value
            self.update()
            self._update_animation_target()

    # ------------------------------------------------------------------
    #  Mouse events
    # ------------------------------------------------------------------

    def hoverEnterEvent(self, event) -> None:
        self.set_hover(True)
        super().hoverEnterEvent(event)

    def hoverMoveEvent(self, event) -> None:
        rect = self._more_button_rect()
        hovered = rect is not None and rect.contains(event.pos())
        if hovered != self._more_button_hovered:
            self._more_button_hovered = hovered
            self.update()
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        if self._more_button_hovered:
            self._more_button_hovered = False
            self.unsetCursor()
            self.update()
        self.set_hover(False)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            rect = self._more_button_rect()
            if rect is not None and rect.contains(event.pos()):
                screen_pos = self._local_to_global(rect.center())
                self._show_context_menu_at(screen_pos)
                event.accept()
                return
            self.clicked.emit(self._win_info)
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit(self._win_info)
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        """Right-click on the tile opens the menu at the cursor."""
        self._show_context_menu_at(event.screenPos())

    def _local_to_global(self, local_pos: QPointF) -> QPoint:
        """Convert an item-local point to a global screen point."""
        scene_pos = self.mapToScene(local_pos)
        views = self.scene().views() if self.scene() else []
        if not views:
            return QPoint(int(local_pos.x()), int(local_pos.y()))
        view = views[0]
        return view.mapToGlobal(view.mapFromScene(scene_pos))

    def _show_context_menu_at(self, screen_pos: QPoint) -> None:
        """Build and show the context menu at the given global position."""
        menu = QMenu()
        menu.setStyleSheet(dropdown_submenu_style(self._gui_config))

        open_action = menu.addAction(self.tr("Open in window"))
        menu.addSeparator()
        create_action = menu.addAction(self.tr("Create profile for this window"))
        copy_action = menu.addAction(self.tr("Copy window info"))

        chosen = menu.exec(screen_pos)
        if chosen is open_action:
            self.open_in_window_requested.emit(self._win_info)
        elif chosen is create_action:
            self.create_profile_requested.emit(self._win_info)
        elif chosen is copy_action:
            self.copy_info_requested.emit(self._win_info)

    # ------------------------------------------------------------------
    #  Capture logic
    # ------------------------------------------------------------------

    def _init_grabber(self) -> None:
        try:
            self._grabber = FrameGrabber(
                self._win_info,
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                tile_size=64,
            )
            self._full_w = self._win_info.width
            self._full_h = self._win_info.height
        except Exception:
            logger.exception("Preview grabber failed for '%s'", self._win_info.title)
            self._grabber = None

    def _refresh(self) -> None:
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            logger.warning("Preview grab failed for '%s'", self._win_info.title)
            self.stop_capture()
            return

        if len(frame) != self._full_w * self._full_h * 4:
            return

        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        avail_w = max(1, int(self._tile_size[0]) - 8)
        avail_h = max(1, int(self._tile_size[1]) - 8)
        self._scaled_pixmap = QPixmap.fromImage(
            QImage(
                bytes(data),
                self._full_w,
                self._full_h,
                self._full_w * 4,
                QImage.Format_RGBA8888,
            )
            .rgbSwapped()
            .scaled(avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.update()

    def stop_capture(self) -> None:
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None

    # ------------------------------------------------------------------
    #  Painting
    # ------------------------------------------------------------------

    def _badge_rect(self) -> Optional[QRectF]:
        """Local-coord rect of the badge, or None when no badge is shown."""
        if not self._gui_config.tile.show_profile or not self._matched_profile:
            return None
        if self._profile_pixmap is not None:
            badge_w = BADGE_HEIGHT
        elif self._badge_label is not None and len(self._badge_label) > 1:
            badge_w = BADGE_HEIGHT + BADGE_EXTRA_WIDTH
        else:
            badge_w = BADGE_HEIGHT
        return QRectF(
            self._half_w - badge_w - BADGE_INSET,
            -self._half_h + BADGE_INSET,
            badge_w,
            BADGE_HEIGHT,
        )

    def _sync_badge_hit(self) -> None:
        """Position the tooltip hit area over the badge (or hide it)."""
        rect = self._badge_rect()
        if rect is None:
            self._badge_hit.setVisible(False)
            self._badge_hit.setToolTip("")
            return
        self._badge_hit.setVisible(True)
        self._badge_hit.set_geometry(rect.x(), rect.y(), rect.width(), rect.height())
        self._badge_hit.setToolTip(
            self.tr("Profile: {0}", "Badge tooltip").format(self._matched_profile)
        )

    def _more_button_rect(self) -> Optional[QRectF]:
        """Local-coord rect of the more-options button, or None when not hovered."""
        if not self._hover:
            return None
        return QRectF(
            self._half_w - MORE_BUTTON_SIZE - MORE_BUTTON_INSET,
            self._half_h - MORE_BUTTON_SIZE - MORE_BUTTON_INSET,
            MORE_BUTTON_SIZE,
            MORE_BUTTON_SIZE,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Scale animation support
        if abs(self._scale - 1.0) > 0.001:
            painter.scale(self._scale, self._scale)

        base = self._resting_rect()
        w, h = base.width(), base.height()
        radius = self._gui_config.tile.radius

        # Shadow
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(base, radius, radius)
        painter.setOpacity(0.12)
        painter.fillPath(shadow_path, QColor(0, 0, 0))
        painter.setOpacity(1.0)

        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(base, radius, radius)
        painter.fillPath(bg_path, QColor(self._gui_config.palette.button))

        # Preview image
        if self._scaled_pixmap and not self._scaled_pixmap.isNull():
            px = (w - self._scaled_pixmap.width()) / 2.0
            py = (h - self._scaled_pixmap.height()) / 2.0
            painter.drawPixmap(int(-w / 2 + px), int(-h / 2 + py), self._scaled_pixmap)

        if self._gui_config.tile.show_title:
            painter.save()
            painter.setClipPath(bg_path)

            # Title
            title = self._win_info.title
            family = self._gui_config.font_family
            font = QFont(family) if family else QFont(QApplication.font())
            font.setPointSize(self._gui_config.tile.title_font_size)
            font.setBold(self._gui_config.tile.title_font_bold)
            font.setHintingPreference(QFont.PreferFullHinting)
            painter.setFont(font)
            painter.setRenderHint(QPainter.TextAntialiasing, True)

            fm = painter.fontMetrics()
            text_width = fm.horizontalAdvance(title)
            text_height = fm.height()

            left_margin = 10
            right_margin = 10 + MORE_BUTTON_SIZE + MORE_BUTTON_INSET + 4
            max_w = w - left_margin - right_margin
            natural_w = text_width + 16

            if natural_w <= max_w:
                pill_w = natural_w
                pill_x = -pill_w / 2.0
            else:
                pill_w = max_w
                pill_x = -w / 2.0 + left_margin

            pill_h = text_height + 6
            pill_y = h / 2 - pill_h - 6
            pill_rect = QRectF(pill_x, pill_y, pill_w, pill_h)
            pill_radius = 4

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self._gui_config.palette.caption_background))
            painter.drawRoundedRect(pill_rect, pill_radius, pill_radius)

            text_rect = pill_rect.adjusted(8, 0, -8, 0)
            elided = fm.elidedText(title, Qt.ElideRight, int(text_rect.width()))
            painter.setPen(QColor(self._gui_config.palette.text_hover))
            painter.drawText(text_rect, Qt.AlignCenter, elided)

            painter.restore()

        # Border
        if self._selected and self._grid_focused:
            pen = QPen(
                QColor(self._gui_config.palette.control),
                self._gui_config.tile.selection_border_width,
            )
        elif self._hover:
            pen = QPen(
                QColor(self._gui_config.palette.control_hover),
                self._gui_config.tile.hover_border_width,
            )
        else:
            pen = QPen(Qt.NoPen)

        if pen.style() != Qt.NoPen:
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(bg_path)

        # Profile badge
        badge_rect = self._badge_rect()
        if badge_rect is not None:
            badge_h = badge_rect.height()
            badge_w = badge_rect.width()

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(self._gui_config.palette.caption_background))
            painter.drawRoundedRect(badge_rect, badge_h / 2.0, badge_h / 2.0)

            if self._profile_pixmap is not None:
                inner = badge_h - 8
                scaled = self._profile_pixmap.scaled(
                    inner, inner, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                px = badge_rect.left() + (badge_w - scaled.width()) / 2.0
                py = badge_rect.top() + (badge_h - scaled.height()) / 2.0
                painter.drawPixmap(int(px), int(py), scaled)
            else:
                painter.setFont(self._badge_font)
                painter.setPen(QColor(self._gui_config.palette.text_hover))
                painter.drawText(badge_rect, Qt.AlignCenter, self._badge_label)

        # More-options button
        button_rect = self._more_button_rect()
        if button_rect is not None:
            # Background
            bg_color = QColor(
                self._gui_config.palette.control
                if self._more_button_hovered
                else self._gui_config.palette.caption_background
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(bg_color)
            painter.drawEllipse(button_rect)

            # Icon
            painter.setBrush(QColor(self._gui_config.palette.text_hover))
            center = button_rect.center()
            for offset in (-MORE_ICON_DOT_SPACING, 0.0, MORE_ICON_DOT_SPACING):
                painter.drawEllipse(
                    QPointF(center.x(), center.y() + offset),
                    MORE_ICON_DOT_RADIUS,
                    MORE_ICON_DOT_RADIUS,
                )

        painter.restore()

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------

    @property
    def window_info(self) -> WindowInfo:
        return self._win_info
