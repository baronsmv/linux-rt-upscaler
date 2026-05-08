import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ...capture import FrameGrabber
from ...window import WindowInfo

logger = logging.getLogger(__name__)


class PreviewWidget(QWidget):
    """
    A widget that displays a real‑time, low‑res preview of a window.

    It uses a :class:`FrameGrabber` to fetch the window contents at a
    reduced size (preserving aspect ratio) and converts the raw BGRA
    data to a :class:`QPixmap` for display.

    The preview updates automatically when :meth:`set_target` is called
    with a valid :class:`WindowInfo`.  If the window cannot be captured,
    a static placeholder is shown.
    """

    def __init__(self, parent=None, preview_width: int = 320):
        super().__init__(parent)
        self._preview_w = preview_width
        self._grabber: Optional[FrameGrabber] = None
        self._target_handle: Optional[int] = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.setInterval(200)  # 5 fps

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setMinimumSize(1, 1)
        self._label.setStyleSheet("background-color: #1e1e1e;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

    def set_target(self, win_info: Optional[WindowInfo]) -> None:
        """Start (or stop) previewing the given window."""
        self._stop()
        if win_info is None:
            self._label.clear()
            return

        # Compute a preview size that keeps the aspect ratio
        w, h = win_info.width, win_info.height
        if w > 0 and h > 0:
            scale = self._preview_w / max(w, h)
            pw = max(1, int(w * scale))
            ph = max(1, int(h * scale))
        else:
            pw, ph = self._preview_w, self._preview_w // 2

        try:
            self._grabber = FrameGrabber(
                win_info,
                crop_left=0,
                crop_top=0,
                crop_right=0,
                crop_bottom=0,
                tile_size=64,  # not used but required by constructor
            )
            self._target_handle = win_info.handle
            self._preview_w = pw
            self._preview_h = ph
            self._label.setFixedSize(pw, ph)
            self._timer.start()
            logger.debug("Preview started for 0x%x (%dx%d)", win_info.handle, pw, ph)
        except Exception:
            logger.exception("Failed to create preview grabber")
            self._show_placeholder()

    def _stop(self) -> None:
        self._timer.stop()
        if self._grabber:
            self._grabber.close()
            self._grabber = None
        self._target_handle = None

    @Slot()
    def _refresh(self) -> None:
        """Capture one frame and update the preview image."""
        if self._grabber is None:
            return
        try:
            frame, _, _ = self._grabber.grab()
            # Frame is a memoryview of BGRA bytes, size = self._preview_w*self._preview_h*4
            # Convert to QImage
            qimg = QImage(
                frame,
                self._preview_w,
                self._preview_h,
                self._preview_w * 4,
                QImage.Format_RGBA8888,  # BGRA is byteswapped, we'll fix later
            )
            # If format mismatch, swap R/B channels (BGRA → RGBA)
            qimg = qimg.rgbSwapped()
            pixmap = QPixmap.fromImage(qimg)
            self._label.setPixmap(pixmap)
        except Exception:
            logger.debug("Preview grab failed, falling back to placeholder")
            self._show_placeholder()

    def _show_placeholder(self) -> None:
        """Display a static placeholder when capture is impossible."""
        self._label.setText("No preview")
        self._label.setFixedSize(self._preview_w, self._preview_w // 2)

    def closeEvent(self, event) -> None:
        self._stop()
        super().closeEvent(event)
