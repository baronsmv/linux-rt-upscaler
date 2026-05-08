from __future__ import annotations

import logging
from typing import Optional, Tuple

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QRectF,
    Property,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
    QLinearGradient,
    QColor,
    QFont,
    QPen,
    QPainterPath,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QGraphicsObject,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from ...capture import FrameGrabber
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class WindowTileItem(QGraphicsObject):
    """
    A single live‑preview tile in the window‑selection mosaic.

    Designed for use inside a :class:`QGraphicsScene`; the scene manages
    absolute positioning (via `setPos`) and the viewport handles
    scrolling.  The tile itself is responsible only for its visual
    appearance, capture, and animations.

    All visual parameters are taken from a :class:`GUIConfig` instance.
    The tile can be *selected* (persistent highlight) and *hovered*
    (transient highlight).  Both states trigger a smooth “pop‑out”
    scaling animation.

    Keyboard navigation is supported: when the tile has focus, pressing
    :kbd:`Enter`, :kbd:`Return`, or :kbd:`Space` emits :attr:`clicked`.

    Signals:
        clicked(WindowInfo): emitted when the user confirms this tile.
    """

    clicked = Signal(WindowInfo)

    # ------------------------------------------------------------------
    #  Initialisation
    # ------------------------------------------------------------------

    def __init__(
        self,
        win_info: WindowInfo,
        gui_config,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent)

        self._win_info = win_info
        self._cfg = gui_config

        # --- Geometry ---
        self._tile_rect = QRectF(0, 0, gui_config.tile_width, gui_config.tile_height)

        # --- State ---
        self._hover = False
        self._selected = False
        self._scale = 1.0  # 1.0 = normal, > 1.0 = popped

        # --- Capture ---
        self._grabber: Optional[FrameGrabber] = None
        self._full_image: Optional[QImage] = None  # latest raw capture
        self._scaled_pixmap: Optional[QPixmap] = None

        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(gui_config.tile_preview_interval_ms)

        # --- Graphics item flags ---
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        # Start capturing immediately
        self._init_grabber()
        self._timer.start()

    # ------------------------------------------------------------------
    #  Geometry helpers
    # ------------------------------------------------------------------

    def _calculate_shadow_extent(self) -> float:
        """Return the maximum distance the shadow reaches outside the tile."""
        ox, oy = self._cfg.shadow_offset
        blur = self._cfg.shadow_blur_radius
        # A simple approximation: offset + blur radius covers most of the shadow
        return max(abs(ox), abs(oy)) + blur * 1.5

    def boundingRect(self) -> QRectF:
        # Base tile rect
        base = self._tile_rect
        # Scale factor (current animation value)
        s = self._scale
        # Shadow offset (simple)
        shadow = 8.0  # maximum shadow blur + offset
        # Scaled width/height
        w = base.width() * s
        h = base.height() * s
        # Centre of scaled tile
        cx = base.center().x()
        cy = base.center().y()
        # Return inflated rect to include shadow
        return QRectF(
            cx - w / 2 - shadow, cy - h / 2 - shadow, w + 2 * shadow, h + 2 * shadow
        )

    # ------------------------------------------------------------------
    #  Scale property (for pop‑out animation)
    # ------------------------------------------------------------------

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, value: float) -> None:
        if self._scale != value:
            self.prepareGeometryChange()  # tell scene bounding rect may change
            self._scale = value
            self.update()  # repaint the new area

    scale = Property(float, get_scale, set_scale)

    def animate_pop_in(self) -> None:
        """Smoothly pop the tile out to the configured maximum scale."""
        self._stop_animation()
        self._pop_anim = QPropertyAnimation(self, b"scale", self)
        self._pop_anim.setDuration(self._cfg.pop_duration)
        self._pop_anim.setStartValue(self._scale)
        self._pop_anim.setEndValue(self._cfg.pop_scale)
        self._pop_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pop_anim.start()

    def animate_pop_out(self) -> None:
        """Smoothly return the tile to its resting scale."""
        self._stop_animation()
        self._pop_anim = QPropertyAnimation(self, b"scale", self)
        self._pop_anim.setDuration(self._cfg.pop_duration)
        self._pop_anim.setStartValue(self._scale)
        self._pop_anim.setEndValue(1.0)
        self._pop_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pop_anim.start()

    def _stop_animation(self) -> None:
        if hasattr(self, "_pop_anim") and self._pop_anim is not None:
            self._pop_anim.stop()
            self._pop_anim = None

    # ------------------------------------------------------------------
    #  Selection state
    # ------------------------------------------------------------------

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        if self._selected != value:
            self._selected = value
            self.update()
            if value:
                self.animate_pop_in()
            elif not self._hover:
                self.animate_pop_out()

    # ------------------------------------------------------------------
    #  Capture logic
    # ------------------------------------------------------------------

    def _init_grabber(self) -> None:
        """Create the FrameGrabber for this window."""
        try:
            self._grabber = FrameGrabber(
                self._win_info,
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                tile_size=64,  # could be configurable
            )
            self._full_w = self._win_info.width
            self._full_h = self._win_info.height
        except Exception:
            logger.exception(
                "Failed to create preview grabber for %s", self._win_info.title
            )
            self._grabber = None

    def _refresh(self):
        if self._grabber is None:
            return
        # Skip if the tile is not visible in any view
        if not self.isVisible() or not self.scene():
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            logger.warning("Preview grab failed for %s", self._win_info.title)
            self.stop_capture()
            return

        if len(frame) != self._full_w * self._full_h * 4:
            return

        # Force alpha to opaque
        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        self._full_image = QImage(
            bytes(data),
            self._full_w,
            self._full_h,
            self._full_w * 4,
            QImage.Format_RGBA8888,
        ).rgbSwapped()

        # Pre‑scale the image to the tile’s logical size (with a small
        # margin) so the paint method does not do expensive scaling every
        # frame.
        avail_w = int(self._tile_rect.width()) - 8
        avail_h = int(self._tile_rect.height()) - 8
        if avail_w > 0 and avail_h > 0:
            self._scaled_pixmap = QPixmap.fromImage(
                self._full_image.scaled(
                    avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        else:
            self._scaled_pixmap = QPixmap()

        self.update()

    def stop_capture(self) -> None:
        """Stop the refresh timer and release the grabber."""
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None

    # ------------------------------------------------------------------
    #  Event handling
    # ------------------------------------------------------------------

    def hoverEnterEvent(self, event) -> None:
        self.setZValue(1)
        self._hover = True
        self.update()
        self.animate_pop_in()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setZValue(0)
        self._hover = False
        self.update()
        self.animate_pop_out()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._win_info)
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit(self._win_info)
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    #  Painting
    # ------------------------------------------------------------------

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """
        Draw the tile.

        The drawing is performed in several layers:

        1. **Drop shadow** – a series of semi‑transparent rounded
           rectangles that simulate a soft shadow.
        2. **Tile background** – filled with the configured colour.
        3. **Live preview image** – the most recent capture, scaled to
           fit the tile.
        4. **Gradient overlay** – a dark gradient at the bottom that
           improves title readability.
        5. **Window title** – the window’s name.
        6. **Border** – a coloured border that indicates hover or
           selection state.
        """
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Apply pop‑out scaling around the tile’s centre
        if abs(self._scale - 1.0) > 0.001:
            c = self._tile_rect.center()
            painter.translate(c)
            painter.scale(self._scale, self._scale)
            painter.translate(-c)

        rect = self._tile_rect
        radius = self._cfg.tile_radius

        # 1. Drop shadow
        shadow_rect = rect.adjusted(4, 4, 4, 4)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(shadow_rect, radius, radius)
        painter.fillPath(shadow_path, QColor(0, 0, 0, 60))

        # 2. Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect, radius, radius)
        painter.fillPath(bg_path, QColor(self._cfg.tile_background))

        # 3. Preview image
        if self._scaled_pixmap and not self._scaled_pixmap.isNull():
            px = (rect.width() - self._scaled_pixmap.width()) / 2.0
            py = (rect.height() - self._scaled_pixmap.height()) / 2.0
            painter.drawPixmap(int(px), int(py), self._scaled_pixmap)

        # 4. Gradient overlay (bottom 40 px)
        grad = QLinearGradient(0, rect.height() - 40, 0, rect.height())
        grad.setColorAt(0, QColor(*self._cfg.tile_title_overlay_start))
        grad.setColorAt(0.7, QColor(*self._cfg.tile_title_overlay_mid))
        grad.setColorAt(1.0, QColor(*self._cfg.tile_title_overlay_end))
        painter.fillRect(0, rect.height() - 40, rect.width(), 40, grad)

        # 5. Title
        painter.setPen(QColor(self._cfg.title_text_color))
        font = QFont(self._cfg.title_font_family, self._cfg.title_font_size)
        font.setBold(self._cfg.title_font_bold)
        painter.setFont(font)
        painter.drawText(10, rect.height() - 12, self._win_info.title)

        # 6. Border (selected / hovered)
        if self._selected:
            pen = QPen(
                QColor(self._cfg.tile_selected_border), self._cfg.selection_border_width
            )
        elif self._hover:
            pen = QPen(
                QColor(self._cfg.tile_hover_border), self._cfg.hover_border_width
            )
        else:
            pen = QPen(Qt.NoPen)
        if pen.style() != Qt.NoPen:
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(bg_path)

        painter.restore()

    # ------------------------------------------------------------------
    #  Dynamic shadow drawing
    # ------------------------------------------------------------------

    def _draw_shadow(self, painter: QPainter, rect: QRectF, radius: float) -> None:
        """
        Render a soft drop shadow by drawing multiple semi‑transparent
        rounded rectangles with increasing offset and decreasing opacity.
        """
        ox, oy = self._cfg.shadow_offset
        blur = self._cfg.shadow_blur_radius
        base_color = QColor(*self._cfg.shadow_color)
        # Number of layers trades quality for performance; 4 is usually enough.
        layers = 4
        for i in range(layers):
            alpha = base_color.alpha() * (1.0 - i / layers)
            color = QColor(
                base_color.red(), base_color.green(), base_color.blue(), int(alpha)
            )
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            # Offset the layer progressively
            dx = ox * (i / layers)
            dy = oy * (i / layers)
            # Blur is imitated by expanding the rect slightly
            expand = blur * (i / layers) * 0.5
            shadow_rect = rect.adjusted(-expand, -expand, expand, expand)
            shadow_rect.translate(dx, dy)
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(shadow_rect, radius + expand, radius + expand)
            painter.drawPath(shadow_path)

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------

    @property
    def window_info(self) -> WindowInfo:
        return self._win_info

    def tile_size(self) -> Tuple[float, float]:
        """Return the logical tile dimensions (width, height)."""
        return self._tile_rect.width(), self._tile_rect.height()
