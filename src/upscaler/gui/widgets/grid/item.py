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

from ....capture import FrameGrabber
from ....window import WindowInfo

logger = logging.getLogger(__name__)


class WindowTileItem(QGraphicsObject):
    """
    A single live‑preview tile in the window‑selection mosaic.

    Local coordinates are **centred** at (0,0), so scaling expands
    symmetrically.  A constant bounding rectangle, pre‑computed for
    the maximum pop‑out scale plus shadow, is returned by
    :meth:`boundingRect` – this avoids layout recalculations during
    animations and makes keyboard navigation flicker‑free.

    All visual parameters are taken from a :class:`GUIConfig` instance.

    Signals:
        clicked(WindowInfo)
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

        # --- Geometry -------------------------------------------------------
        self._half_w = gui_config.tile_width / 2.0
        self._half_h = gui_config.tile_height / 2.0
        self._tile_size = (gui_config.tile_width, gui_config.tile_height)
        self._max_bounding_rect = self._compute_max_bounding_rect()

        # --- State (hover & selection determine the animation target) -------
        self.setCursor(Qt.PointingHandCursor)
        self._hover = False
        self._selected = False
        self._scale = 1.0  # current scale (animated)
        self._target_scale = 1.0  # desired scale (1.0 or pop_scale)

        # --- Animation ------------------------------------------------------
        self._anim = QPropertyAnimation(self, b"scale", self)
        self._anim.setDuration(gui_config.pop_duration)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.finished.connect(self._on_animation_finished)

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

        self._init_grabber()
        self._timer.start()

    # ------------------------------------------------------------------
    #  Geometry helpers
    # ------------------------------------------------------------------

    def _resting_rect(self) -> QRectF:
        return QRectF(-self._half_w, -self._half_h, self._half_w * 2, self._half_h * 2)

    def _compute_max_bounding_rect(self) -> QRectF:
        base = self._resting_rect()
        s = self._cfg.pop_scale
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
        self.update()

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

    def _should_pop(self) -> bool:
        """Return True if the tile should appear popped out."""
        return self._hover or self._selected

    def _update_animation_target(self) -> None:
        """
        Re‑evaluate the desired scale and smoothly animate toward it.
        Called whenever :attr:`_hover` or :attr:`_selected` changes.
        """
        target = self._cfg.pop_scale if self._should_pop() else 1.0
        if target == self._target_scale:
            return
        self._target_scale = target
        self._anim.stop()
        self._anim.setStartValue(self._scale)
        self._anim.setEndValue(target)
        self._anim.start()

    def _on_animation_finished(self) -> None:
        """Called when the pop‑in / pop‑out animation completes."""
        pass  # nothing needed; target already reached

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
        self.setZValue(1)
        self._hover = True
        self.update()
        self._update_animation_target()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        self.setZValue(0)
        self._hover = False
        self.update()
        self._update_animation_target()
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

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        if abs(self._scale - 1.0) > 0.001:
            painter.scale(self._scale, self._scale)

        base = self._resting_rect()
        w, h = base.width(), base.height()
        radius = self._cfg.tile_radius

        # Shadow
        shadow_rect = base.adjusted(4, 4, 4, 4)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(shadow_rect, radius, radius)
        painter.setOpacity(0.15)
        painter.fillPath(shadow_path, QColor(0, 0, 0))
        painter.setOpacity(1.0)

        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(base, radius, radius)
        painter.fillPath(bg_path, QColor(self._cfg.tile_background))

        # Preview image
        if self._scaled_pixmap and not self._scaled_pixmap.isNull():
            px = (w - self._scaled_pixmap.width()) / 2.0
            py = (h - self._scaled_pixmap.height()) / 2.0
            painter.drawPixmap(int(-w / 2 + px), int(-h / 2 + py), self._scaled_pixmap)

        # Gradient overlay
        grad = QLinearGradient(0, h / 2 - 40, 0, h / 2)
        grad.setColorAt(0, QColor(*self._cfg.tile_title_overlay_start))
        grad.setColorAt(0.7, QColor(*self._cfg.tile_title_overlay_mid))
        grad.setColorAt(1.0, QColor(*self._cfg.tile_title_overlay_end))
        painter.fillRect(QRectF(-w / 2, h / 2 - 40, w, 40), grad)

        # Title
        painter.setPen(QColor(self._cfg.title_text_color))
        font = QFont(self._cfg.title_font_family, self._cfg.title_font_size)
        font.setBold(self._cfg.title_font_bold)
        painter.setFont(font)
        painter.drawText(
            QRectF(-w / 2 + 10, h / 2 - 32, w - 20, 20),
            Qt.AlignLeft | Qt.AlignVCenter,
            self._win_info.title,
        )

        # Border
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
