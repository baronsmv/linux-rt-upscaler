import logging
import time
import xcffib
import xcffib.xproto
from PySide6.QtGui import QCursor
from typing import Optional

from ..window import WindowInfo, open_xcb_connection, close_xcb_connection

logger = logging.getLogger(__name__)


class OpacityController:
    """Controls overlay opacity based on mouse position relative to a target window."""

    def __init__(self, overlay, win_info: WindowInfo):
        self.overlay = overlay
        self.target_handle = win_info.handle
        self.target_width = win_info.width
        self.target_height = win_info.height
        self._conn: Optional[xcffib.Connection] = None
        self._last_update_time = 0.0
        self._open_connection()

    def _open_connection(self) -> None:
        self._conn = open_xcb_connection()
        if not self._conn:
            logger.warning("XCB connection unavailable for opacity control")

    def close(self) -> None:
        close_xcb_connection(self._conn)
        self._conn = None

    def update(self) -> None:
        """Update overlay opacity based on mouse position (throttled to 10 Hz)."""
        now = time.time()
        if now - self._last_update_time < 0.1:
            return
        self._last_update_time = now

        if self.overlay.map_events:
            self.overlay.setWindowOpacity(1.0)
            return

        if self._conn is None:
            self.overlay.setWindowOpacity(1.0)
            return

        try:
            mouse = QCursor.pos()
            # Get window geometry to compute screen position
            geom_cookie = self._conn.core.GetGeometry(self.target_handle)
            geom = geom_cookie.reply()
            if not geom:
                self.overlay.setWindowOpacity(1.0)
                return

            # Translate coordinates to root (screen) coordinates
            trans_cookie = self._conn.core.TranslateCoordinates(
                self.target_handle, self._conn.get_setup().roots[0].root, 0, 0
            )
            trans = trans_cookie.reply()
            if not trans:
                self.overlay.setWindowOpacity(1.0)
                return

            win_x = trans.dst_x
            win_y = trans.dst_y

            inside = (
                win_x <= mouse.x() < win_x + geom.width
                and win_y <= mouse.y() < win_y + geom.height
            )
            opacity = 1.0 if inside else 0.2
            self.overlay.setWindowOpacity(opacity)
        except Exception as e:
            logger.debug(f"Opacity update failed: {e}")
            self.overlay.setWindowOpacity(1.0)
            self.close()  # release stale connection

    def update_target_info(self, handle: int, width: int, height: int) -> None:
        """Update the target window information."""
        if handle != self.target_handle:
            self.target_handle = handle
            self.close()
            self._open_connection()
        self.target_width = width
        self.target_height = height
