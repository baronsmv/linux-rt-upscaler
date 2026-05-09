from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap, QImage, QPainter
from PySide6.QtWidgets import QWidget

from ...capture import FrameGrabber
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """
    A widget that displays a live, scaled preview of an X11 window.

    Captures the full window content, forces alpha to opaque, and draws
    the result inside the widget's area, maintaining aspect ratio.

    Call :meth:`set_target` with a :class:`WindowInfo` to start previewing,
    or with ``None`` to stop and show a placeholder.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grabber: Optional[FrameGrabber] = None
        self._full_w: int = 0
        self._full_h: int = 0
        self._pixmap: Optional[QPixmap] = None
        self._placeholder: bool = True

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(300)  # ~3 fps, enough for a mosaic

        self.setMinimumSize(20, 20)  # allow shrinking
        self.setStyleSheet("background-color: #2d2d2d;")

    def set_target(self, win_info: Optional[WindowInfo]) -> None:
        self._stop()
        if win_info is None:
            self._placeholder = True
            self._pixmap = None
            self.update()
            return

        w, h = win_info.width, win_info.height
        if w <= 0 or h <= 0:
            self._placeholder = True
            self._pixmap = None
            self.update()
            return

        try:
            self._grabber = FrameGrabber(
                win_info,
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                tile_size=64,
            )
        except Exception:
            logger.exception("Failed to create preview grabber")
            self._placeholder = True
            self.update()
            return

        self._full_w = w
        self._full_h = h
        self._placeholder = False
        self._pixmap = None
        self._timer.start()
        self.update()

    def _stop(self) -> None:
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None
        self._full_w = 0
        self._full_h = 0

    @Slot()
    def _refresh(self) -> None:
        if self._grabber is None or self._full_w == 0:
            return
        try:
            frame, _, _ = self._grabber.grab()
        except RuntimeError as e:
            logger.warning("Preview grab failed: %s", e)
            self._placeholder = True
            self._pixmap = None
            self._timer.stop()
            self.update()
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

        # Scale to fit the current widget size, maintaining aspect ratio
        scaled = qimg.scaled(
            self.width(),
            self.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._pixmap = QPixmap.fromImage(scaled)
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        if self._placeholder or self._pixmap is None:
            painter.setPen(Qt.gray)
            font = painter.font()
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "Preview")
        else:
            # Center the pixmap
            x = (self.width() - self._pixmap.width()) // 2
            y = (self.height() - self._pixmap.height()) // 2
            painter.drawPixmap(x, y, self._pixmap)
        painter.end()

    def closeEvent(self, event) -> None:
        self._stop()
        super().closeEvent(event)
