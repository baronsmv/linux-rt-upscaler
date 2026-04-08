import logging
from typing import Optional

from Xlib import X
from Xlib.display import Display
from Xlib.error import XError, BadWindow
from Xlib.xobject.drawable import Window as XlibWindow

from .display import open_x_display, close_x_display

logger = logging.getLogger(__name__)


class WindowTracker:
    """
    Tracks a target X11 window for changes in its handle and size.
    Provides a quick alive check and updates internal state on changes.
    """

    def __init__(self, initial_handle: int, initial_width: int, initial_height: int):
        self.handle = initial_handle
        self.width = initial_width
        self.height = initial_height
        self.alive = True
        self.active = True
        self.minimized = False

        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        self._open_x_display()

    def _open_x_display(self) -> None:
        """Open a fresh X display and create the window resource."""
        try:
            self._x_display = open_x_display()
            if self._x_display:
                self._x_window = self._x_display.create_resource_object(
                    "window", self.handle
                )
            else:
                logger.warning("Failed to open X display for WindowTracker")
                self.alive = False
        except Exception as e:
            logger.error(f"Unexpected error opening X display: {e}")
            self.alive = False

    def close(self) -> None:
        """Close the X display and release resources."""
        close_x_display(self._x_display)
        self._x_display = None
        self._x_window = None

    def check_alive(self) -> bool:
        """
        Quickly check if the tracked window still exists.
        Updates the internal `alive` flag and returns the current status.
        """
        if not self.alive:
            return False

        # If no valid X connection, try to reopen
        if self._x_window is None:
            self._open_x_display()
            if self._x_window is None:
                self.alive = False
                return False

        try:
            # Lightweight call
            self._x_window.get_attributes()
            return True
        except BadWindow:
            logger.debug("Window no longer exists (BadWindow in check_alive)")
            self.alive = False
            self.handle = 0
            return False
        except XError as e:
            logger.debug(f"X error during alive check: {e}")
            # Treat other X errors as potentially transient, but if repeated
            # the caller should eventually see alive=False from update()
            return True
        except Exception as e:
            logger.error(f"Unexpected error in check_alive: {e}")
            return True  # assume alive to avoid false positives

    def update(self, force: bool = False, depth: int = 0) -> bool:
        """
        Query the current window handle and size. Returns True if a change occurred.
        If force is True, always attempt to refresh even if no change.
        """
        if not self.alive:
            return False

        # Prevent infinite recursion
        if depth > 2:
            logger.warning("WindowTracker.update recursion depth exceeded")
            return False

        # Ensure we have a valid X window handle
        if self._x_window is None:
            if depth == 0:
                self._open_x_display()
            return False

        try:
            geom = self._x_window.get_geometry()
            attrs = self._x_window.get_attributes()
            new_handle = self._x_window.id
            new_width = geom.width
            new_height = geom.height
            self.minimized = attrs.map_state != X.IsViewable

            # Query active window from root
            root = self._x_display.screen().root
            atom = self._x_display.intern_atom("_NET_ACTIVE_WINDOW")
            prop = root.get_full_property(atom, X.AnyPropertyType)
            if prop and prop.value:
                active_handle = prop.value[0]
                self.active = active_handle == self.handle
            else:
                self.active = False
        except BadWindow:
            logger.debug("Window no longer exists (BadWindow in update)")
            self.alive = False
            self.handle = 0
            return False
        except XError as e:
            logger.debug(f"X error when querying window geometry: {e}")
            # Attempt to recover by reopening the display once
            if depth == 0:
                self.close()
                self._open_x_display()
                return self.update(force, depth + 1)
            return False
        except Exception as e:
            logger.error(f"Unexpected error in update: {e}")
            return False

        handle_changed = new_handle != self.handle
        size_changed = new_width != self.width or new_height != self.height

        if handle_changed or size_changed or force:
            logger.info(
                f"WindowTracker: change detected: handle {self.handle} "
                f"-> {new_handle}, size {self.width}x{self.height} "
                f"-> {new_width}x{new_height}"
            )
            self.handle = new_handle
            self.width = new_width
            self.height = new_height
            return True

        return False
