from PySide6.QtCore import Qt, QTimer, Signal, QRectF
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
    A stylish tile showing a live window preview with gradient title overlay.
    Emits clicked when the tile is pressed.
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

        # Shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

        self._grabber = None
        self._pixmap = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._full_w = 0
        self._full_h = 0
        self._hover = False

        self._init_grabber()
        self._timer.start(250)  # ~4 fps per tile, adjustable

    def _init_grabber(self):
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

    def _refresh(self):
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError:
            self.stop()
            return
        if len(frame) != self._full_w * self._full_h * 4:
            return

        data = bytearray(frame)
        for i in range(3, len(data), 4):
            data[i] = 255

        qimg = QImage(
            bytes(data),
            self._full_w,
            self._full_h,
            self._full_w * 4,
            QImage.Format_RGBA8888,
        ).rgbSwapped()

        # Scale to fit tile interior (leave space for gradient)
        avail_w = self.width() - 8
        avail_h = self.height() - 8
        scaled = qimg.scaled(
            avail_w, avail_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._pixmap = QPixmap.fromImage(scaled)
        self.update()

    def stop(self):
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None

    def enterEvent(self, event):
        self._hover = True
        self.update()

    def leaveEvent(self, event):
        self._hover = False
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._win_info)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background rounded rect
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)
        painter.setClipPath(path)
        painter.fillPath(path, QColor("#1e1e1e"))

        # Draw pixmap centered
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

        # Hover border
        if self._hover:
            pen = QPen(QColor("#2b5b84"), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(
                QRectF(self.rect()).adjusted(1, 1, -1, -1), self.RADIUS, self.RADIUS
            )

        painter.end()
