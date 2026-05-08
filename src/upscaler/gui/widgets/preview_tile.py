from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, QRectF, Property, QPropertyAnimation
from PySide6.QtGui import (
    QPainter,
    QPixmap,
    QImage,
    QLinearGradient,
    QColor,
    QFont,
    QPen,
    QPainterPath,
)
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

from ...capture import FrameGrabber
from ...window import WindowInfo


class PreviewTile(QWidget):
    """
    A tile showing a live window preview with gradient title overlay.

    Supports :attr:`hover` and :attr:`selected` states with distinct borders.
    Emits :signal:`clicked` when the tile is pressed.
    """

    clicked = Signal(WindowInfo)
    TILE_W = 340
    TILE_H = 260
    RADIUS = 12

    def __init__(self, win_info: WindowInfo, parent=None):
        super().__init__(parent)
        self._win_info = win_info
        self.setFixedSize(self.TILE_W, self.TILE_H)
        self.setCursor(Qt.PointingHandCursor)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        # Internal state
        self._grabber: Optional[FrameGrabber] = None
        self._pixmap: Optional[QPixmap] = None
        self._full_w = 0
        self._full_h = 0
        self._hover = False
        self._selected = False
        self._opacity = 1.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(250)  # ~4 fps per tile

        self._init_grabber()
        self._timer.start()

    # ------------------------------------------------------------------
    #  Opacity property (used for fade‑in animation)
    # ------------------------------------------------------------------
    def get_opacity(self) -> float:
        return self._opacity

    def set_opacity(self, value: float) -> None:
        self._opacity = value
        self.update()

    opacity = Property(float, get_opacity, set_opacity)

    def animate_in(self) -> None:
        """Fade in from transparency over 300 ms."""
        self._opacity = 0.0
        self.update()
        animation = QPropertyAnimation(self, b"opacity", self)
        animation.setDuration(300)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()

    # ------------------------------------------------------------------
    #  Selection & hover
    # ------------------------------------------------------------------
    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        if self._selected != value:
            self._selected = value
            self.update()

    @property
    def window_info(self) -> WindowInfo:
        return self._win_info

    # ------------------------------------------------------------------
    #  FrameGrabber management
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
            self._grabber = None

    def _refresh(self) -> None:
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            self.stop()
            return
        if len(frame) != self._full_w * self._full_h * 4:
            return

        # Force alpha to 255 (opaque)
        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        qimg = QImage(
            bytes(data),
            self._full_w,
            self._full_h,
            self._full_w * 4,
            QImage.Format_RGBA8888,
        ).rgbSwapped()  # BGRA → RGBA

        avail_w = self.width() - 8
        avail_h = self.height() - 8
        scaled = qimg.scaled(
            avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._pixmap = QPixmap.fromImage(scaled)
        self.update()

    def stop(self) -> None:
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None

    # ------------------------------------------------------------------
    #  Event handlers
    # ------------------------------------------------------------------
    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            # Transfer focus to the grid so keyboard navigation works
            if self.parent():
                self.parent().setFocus()
            self.clicked.emit(self._win_info)

    # ------------------------------------------------------------------
    #  Painting
    # ------------------------------------------------------------------
    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setOpacity(self._opacity)

        # Rounded clipping
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        painter.setClipPath(path)
        painter.fillPath(path, QColor("#1e1e1e"))

        # Live preview image (centered)
        if self._pixmap and not self._pixmap.isNull():
            x = (self.width() - self._pixmap.width()) // 2
            y = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(x, y, self._pixmap)

        # Gradient overlay at bottom
        gradient = QLinearGradient(0, self.height() - 40, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.7, QColor(0, 0, 0, 160))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 200))
        painter.fillRect(0, self.height() - 40, self.width(), 40, gradient)

        # Title text
        painter.setPen(Qt.white)
        font = QFont("Segoe UI", 12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, self.height() - 12, self._win_info.title)

        # Border: selected (bright blue) > hover (dim blue)
        if self._selected:
            pen = QPen(QColor("#4a9eff"), 3)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(1, 1, -1, -1), self.RADIUS, self.RADIUS
            )
        elif self._hover:
            pen = QPen(QColor("#2b5b84"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(1, 1, -1, -1), self.RADIUS, self.RADIUS
            )

        painter.end()
