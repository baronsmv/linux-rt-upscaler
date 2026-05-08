import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QLabel, QWidget

from ...capture import FrameGrabber
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """
    A widget that displays a real‑time, low‑resolution preview of a target X11 window.

    Captures the full window content using :class:`FrameGrabber` at native
    resolution, forces the alpha channel to fully opaque, then downscales
    and displays it in a centered :class:`QLabel`. Updates at 5 fps.

    When no window is selected, a dark placeholder with 'No preview' is shown.
    """

    def __init__(self, parent=None, preview_width: int = 260):
        super().__init__(parent)
        self._preview_w = preview_width
        self._preview_h = int(preview_width * 3 / 4)

        self.setFixedSize(self._preview_w, self._preview_h)
        self.setStyleSheet("background-color: #2d2d2d;")

        self._grabber: Optional[FrameGrabber] = None
        self._full_w: int = 0
        self._full_h: int = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(200)  # 5 fps

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setScaledContents(False)
        self._label.setStyleSheet("background-color: transparent; border: none;")

        self._show_placeholder()

    def set_target(self, win_info: Optional[WindowInfo]) -> None:
        """Start (or stop) previewing the given window."""
        self._stop()
        if win_info is None:
            self._show_placeholder()
            return

        w, h = win_info.width, win_info.height
        if w <= 0 or h <= 0:
            self._show_placeholder()
            return

        scale = self.width() / max(w, h)
        pw = max(1, int(w * scale))
        ph = max(1, int(h * scale))

        self._label.setFixedSize(pw, ph)
        self._label.move(
            (self.width() - pw) // 2,
            (self.height() - ph) // 2,
        )

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
            self._show_placeholder()
            return

        self._full_w = w
        self._full_h = h
        self._label.clear()
        self._timer.start()
        logger.debug("Preview started for 0x%x (%dx%d)", win_info.handle, w, h)

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
            self._show_placeholder()
            self._timer.stop()
            return

        expected = self._full_w * self._full_h * 4
        if len(frame) != expected:
            return

        # Force alpha to 255 to make the image fully opaque
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

        pixmap = QPixmap.fromImage(
            qimg.scaled(
                self._label.width(),
                self._label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
        if pixmap.isNull():
            return
        self._label.setPixmap(pixmap)
        self._label.repaint()

    def _show_placeholder(self) -> None:
        self._label.clear()
        self._label.setText("No preview")
        self._label.setFixedSize(self.width(), self.height())
        self._label.move(0, 0)
        self._label.setAlignment(Qt.AlignCenter)

    def closeEvent(self, event) -> None:
        self._stop()
        super().closeEvent(event)
