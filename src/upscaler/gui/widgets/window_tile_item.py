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

    Local coordinates are centred: (0,0) is the tile’s centre, so scaling
    naturally expands from the middle without any offset.

    Signals:
        clicked(WindowInfo)
    """

    clicked = Signal(WindowInfo)

    def __init__(
        self,
        win_info: WindowInfo,
        gui_config,
        parent: Optional[QGraphicsItem] = None,
    ) -> None:
        super().__init__(parent)
        self._win_info = win_info
        self._cfg = gui_config

        # Half dimensions of the resting tile
        self._half_w = gui_config.tile_width / 2.0
        self._half_h = gui_config.tile_height / 2.0
        self._tile_size = (gui_config.tile_width, gui_config.tile_height)

        # State
        self._hover = False
        self._selected = False
        self._scale = 1.0

        # Capture
        self._grabber: Optional[FrameGrabber] = None
        self._scaled_pixmap: Optional[QPixmap] = None
        self._full_w = 0
        self._full_h = 0

        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(gui_config.tile_preview_interval_ms)

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self._init_grabber()
        self._timer.start()

    # ------------------------------------------------------------------
    #  Geometry helpers
    # ------------------------------------------------------------------
    def _resting_rect(self) -> QRectF:
        return QRectF(-self._half_w, -self._half_h, self._half_w * 2, self._half_h * 2)

    def _shadow_margin(self) -> float:
        """Extra space needed for the drop shadow (simple offset + blur)."""
        return (
            max(abs(self._cfg.shadow_offset[0]), abs(self._cfg.shadow_offset[1]))
            + self._cfg.shadow_blur_radius
        )

    def set_tile_size(self, width: float, height: float) -> None:
        """
        Resize the tile to new dimensions.
        Stops any active pop animation and resets the scale to 1.0.
        """
        self._stop_animation()
        self.prepareGeometryChange()
        self._half_w = width / 2.0
        self._half_h = height / 2.0
        self._tile_size = (width, height)
        self._scale = 1.0
        # Clear the cached pixmap so it is re‑scaled on the next refresh
        self._scaled_pixmap = None
        self.update()

    def boundingRect(self) -> QRectF:
        """
        Bounding rect that includes the tile at its current scale plus the
        scaled drop shadow (ensuring the shadow is never clipped).
        """
        base = self._resting_rect()
        s = self._scale
        # The shadow is painted as an offset of 4 px in local coordinates,
        # which scales with the painter.  Add that scaled margin.
        shadow = 4.0 * s
        w = base.width() * s + 2 * shadow
        h = base.height() * s + 2 * shadow
        return QRectF(-w / 2, -h / 2, w, h)

    # ------------------------------------------------------------------
    #  Scale property (for pop‑out animation)
    # ------------------------------------------------------------------
    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, value: float) -> None:
        if self._scale != value:
            self.prepareGeometryChange()
            self._scale = value
            self.update()

    scale = Property(float, get_scale, set_scale)

    def animate_pop_in(self) -> None:
        self._stop_animation()
        self._pop_anim = QPropertyAnimation(self, b"scale", self)
        self._pop_anim.setDuration(self._cfg.pop_duration)
        self._pop_anim.setStartValue(self._scale)
        self._pop_anim.setEndValue(self._cfg.pop_scale)
        self._pop_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pop_anim.start()

    def animate_pop_out(self) -> None:
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
    #  Capture logic (unchanged except use tile size)
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
            logger.exception("Preview grabber failed for %s", self._win_info.title)
            self._grabber = None

    def _refresh(self) -> None:
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            logger.warning("Preview grab failed for %s", self._win_info.title)
            self.stop_capture()
            return
        if len(frame) != self._full_w * self._full_h * 4:
            return

        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        # Pre‑scale to tile interior (8 px margin)
        avail_w = int(self._tile_size[0]) - 8
        avail_h = int(self._tile_size[1]) - 8
        if avail_w > 0 and avail_h > 0:
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
        else:
            self._scaled_pixmap = QPixmap()
        self.update()

    def stop_capture(self) -> None:
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
    #  Painting – all drawing relative to local centre
    # ------------------------------------------------------------------
    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Scale around (0,0) – the tile’s centre
        if abs(self._scale - 1.0) > 0.001:
            painter.scale(self._scale, self._scale)

        base = self._resting_rect()
        w = base.width()
        h = base.height()
        radius = self._cfg.tile_radius

        # 1. Shadow (simple, single offset)
        shadow_rect = base.adjusted(4, 4, 4, 4)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(shadow_rect, radius, radius)
        painter.setOpacity(0.15)
        painter.fillPath(shadow_path, QColor(0, 0, 0))
        painter.setOpacity(1.0)

        # 2. Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(base, radius, radius)
        painter.fillPath(bg_path, QColor(self._cfg.tile_background))

        # 3. Preview image
        if self._scaled_pixmap and not self._scaled_pixmap.isNull():
            px = (w - self._scaled_pixmap.width()) / 2.0
            py = (h - self._scaled_pixmap.height()) / 2.0
            painter.drawPixmap(int(-w / 2 + px), int(-h / 2 + py), self._scaled_pixmap)

        # 4. Gradient overlay at the bottom of the tile
        grad = QLinearGradient(0, h / 2 - 40, 0, h / 2)
        grad.setColorAt(0, QColor(*self._cfg.tile_title_overlay_start))
        grad.setColorAt(0.7, QColor(*self._cfg.tile_title_overlay_mid))
        grad.setColorAt(1.0, QColor(*self._cfg.tile_title_overlay_end))
        painter.fillRect(QRectF(-w / 2, h / 2 - 40, w, 40), grad)

        # 5. Title
        painter.setPen(QColor(self._cfg.title_text_color))
        font = QFont(self._cfg.title_font_family, self._cfg.title_font_size)
        font.setBold(self._cfg.title_font_bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(-w / 2 + 10, h / 2 - 32, w - 20, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._win_info.title,
        )

        # 6. Border
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
    #  Public helpers
    # ------------------------------------------------------------------
    @property
    def window_info(self) -> WindowInfo:
        return self._win_info

    def tile_size(self) -> Tuple[float, float]:
        return self._tile_size
