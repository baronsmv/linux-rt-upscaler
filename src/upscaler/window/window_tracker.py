import logging
from typing import Optional

from Xlib.display import Display
from Xlib.error import XError, BadWindow
from Xlib.xobject.drawable import Window as XlibWindow

from upscaler.utils.x11 import open_x_display, close_x_display

logger = logging.getLogger(__name__)


class WindowTracker:
    """
    Tracks a target X11 window for changes in its handle and size.
    Provides callbacks for when changes occur.
    """

    def __init__(self, initial_handle: int, initial_width: int, initial_height: int):
        self.handle = initial_handle
        self.width = initial_width
        self.height = initial_height

        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        self._open_x_display()

    def _open_x_display(self) -> None:
        self._x_display = open_x_display()
        if self._x_display:
            self._x_window = self._x_display.create_resource_object(
                "window", self.handle
            )

    def close(self) -> None:
        close_x_display(self._x_display)
        self._x_display = None
        self._x_window = None

    def update(self, force: bool = False, depth: int = 0) -> bool:
        """
        Query the current window handle and size. Returns True if a change occurred.
        If force is True, always attempt to refresh even if no change.
        """
        if depth > 2:
            return False

        if self._x_window is None:
            if depth == 0:
                self._open_x_display()
            return False

        try:
            geom = self._x_window.get_geometry()
            new_handle = self._x_window.id
            new_width = geom.width
            new_height = geom.height
        except (BadWindow, XError) as e:
            logger.debug(f"X error when querying window: {e}")
            if force:
                return False
            self.close()
            self._open_x_display()
            if self._x_window is None:
                return False
            return self.update(force=True, depth=depth + 1)

        handle_changed = new_handle != self.handle
        size_changed = new_width != self.width or new_height != self.height

        if handle_changed or size_changed or force:
            logger.info(
                f"Target window changed: handle {self.handle} -> {new_handle}, "
                f"size {self.width}x{self.height} -> {new_width}x{new_height}"
            )
            self.handle = new_handle
            self.width = new_width
            self.height = new_height
            return True

        return False
