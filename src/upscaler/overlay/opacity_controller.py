import logging
import time
from typing import Optional

from PySide6.QtGui import QCursor
from Xlib.display import Display
from Xlib.error import XError, BadWindow
from Xlib.xobject.drawable import Window as XlibWindow

from ..utils.x11 import open_x_display, close_x_display

logger = logging.getLogger(__name__)


class OpacityController:
    """
    Controls overlay opacity based on mouse position relative to a target window.
    """

    def __init__(
        self, overlay, target_handle: int, target_width: int, target_height: int
    ):
        self.overlay = overlay
        self.target_handle = target_handle
        self.target_width = target_width
        self.target_height = target_height
        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        self._last_update_time = 0.0
        self._open_x_display()

    def _open_x_display(self) -> None:
        self._x_display = open_x_display()
        if self._x_display:
            self._x_window = self._x_display.create_resource_object(
                "window", self.target_handle
            )

    def close(self) -> None:
        close_x_display(self._x_display)
        self._x_display = None
        self._x_window = None

    def update(self) -> None:
        """Update overlay opacity based on mouse position (throttled to 10 Hz)."""
        now = time.time()
        if now - self._last_update_time < 0.1:
            return
        self._last_update_time = now

        if self.overlay.map_events:
            self.overlay.setWindowOpacity(1.0)
            return

        if self._x_window is None or self._x_display is None:
            self.overlay.setWindowOpacity(1.0)
            return

        try:
            mouse = QCursor.pos()
            geom = self._x_window.get_geometry()
            trans = geom.root.translate_coords(self._x_window, 0, 0)
            win_x, win_y = trans.x, trans.y

            inside = (
                win_x <= mouse.x() < win_x + self.target_width
                and win_y <= mouse.y() < win_y + self.target_height
            )
            opacity = 1.0 if inside else 0.2
            self.overlay.setWindowOpacity(opacity)
        except (BadWindow, XError) as e:
            logger.warning(f"Target window disappeared during opacity update: {e}")
            self.overlay.setWindowOpacity(1.0)
            self.close()  # release stale resources
        except Exception as e:
            logger.error(f"Unexpected error in opacity update: {e}", exc_info=True)
            self.overlay.setWindowOpacity(1.0)

    def update_target_info(self, handle: int, width: int, height: int) -> None:
        """Update the target window information."""
        if handle != self.target_handle:
            self.target_handle = handle
            self.close()
            self._open_x_display()
        self.target_width = width
        self.target_height = height
