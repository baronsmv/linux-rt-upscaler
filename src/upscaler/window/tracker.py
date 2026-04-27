import logging
from typing import Optional

import xcffib
import xcffib.xproto

from .display import open_xcb_connection, close_xcb_connection
from .info import AtomCache, get_window_geometry

logger = logging.getLogger(__name__)


class WindowTracker:
    """Tracks a target X11 window for changes in its handle and size."""

    def __init__(self, initial_handle: int, initial_width: int, initial_height: int):
        self.handle = initial_handle
        self.width = initial_width
        self.height = initial_height
        self.alive = True
        self.active = True
        self.minimized = False

        self._conn: Optional[xcffib.Connection] = None
        self._atoms: Optional[AtomCache] = None
        self._open_connection()

    def _open_connection(self) -> None:
        """Open an XCB connection."""
        try:
            self._conn = open_xcb_connection()
            if self._conn:
                self._atoms = AtomCache(self._conn)
            else:
                logger.warning("Failed to open XCB connection for WindowTracker")
                self.alive = False
        except Exception as e:
            logger.error(f"Unexpected error opening XCB connection: {e}")
            self.alive = False

    def close(self) -> None:
        """Close the XCB connection."""
        close_xcb_connection(self._conn)
        self._conn = None
        self._atoms = None

    def check_alive(self) -> bool:
        """Quickly check if the tracked window still exists."""
        if not self.alive or self._conn is None:
            return False

        try:
            # Try to get window attributes (lightweight)
            self._conn.core.GetWindowAttributes(self.handle).reply()
            return True
        except Exception:
            logger.debug("Window no longer exists (error in check_alive)")
            self.alive = False
            self.handle = 0
            return False

    def update(self, force: bool = False, depth: int = 0) -> bool:
        """Query current window handle and size. Returns True if changed."""
        if not self.alive or self._conn is None:
            return False

        if depth > 2:
            logger.warning("WindowTracker.update recursion depth exceeded")
            return False

        try:
            # Get geometry
            geom = get_window_geometry(self._conn, self.handle)
            if geom is None:
                raise Exception("Geometry query failed")
            _, _, new_width, new_height = geom

            # Check if minimized (map_state)
            attr = self._conn.core.GetWindowAttributes(self.handle).reply()
            if attr:
                self.minimized = attr.map_state != xcffib.xproto.MapState.Viewable
            else:
                self.minimized = True

            # Check if active
            root = self._conn.get_setup().roots[0].root
            active_cookie = self._conn.core.GetProperty(
                False,
                root,
                self._atoms.get("_NET_ACTIVE_WINDOW"),
                xcffib.xproto.Atom.WINDOW,
                0,
                1,
            )
            active_reply = active_cookie.reply()
            if active_reply and active_reply.value_len:
                active_handle = active_reply.value.to_atoms()[0]
                self.active = active_handle == self.handle
            else:
                self.active = False

        except Exception as e:
            logger.debug(f"Error querying window: {e}")
            if depth == 0:
                # Attempt to reconnect once
                self.close()
                self._open_connection()
                return self.update(force, depth + 1)
            self.alive = False
            self.handle = 0
            return False

        handle_changed = False  # handle cannot change in XCB (window ID is constant)
        size_changed = new_width != self.width or new_height != self.height

        if handle_changed or size_changed or force:
            logger.info(
                f"WindowTracker: change detected: size {self.width}x{self.height} "
                f"-> {new_width}x{new_height}"
            )
            self.width = new_width
            self.height = new_height
            return True

        return False
