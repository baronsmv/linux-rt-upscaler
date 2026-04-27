import logging
from typing import Optional

import xcffib
import xcffib.xproto

from .connection import open_xcb_connection, close_xcb_connection
from .info import AtomCache, get_window_geometry

logger = logging.getLogger(__name__)


class WindowTracker:
    """
    Tracks a target X11 window for changes in its handle and size.

    The tracker maintains a dedicated XCB connection and periodically checks
    whether the window still exists, whether it is active (focused), minimized,
    and whether its size has changed. It automatically attempts to reopen the
    connection if it becomes invalid (e.g., after system suspend/resume).

    Attributes:
        handle (int): Current X11 window ID (immutable for a given window,
                      but set to 0 if window dies).
        width (int): Last known window width.
        height (int): Last known window height.
        alive (bool): True if the window still exists (XID valid and responding).
        active (bool): True if the window currently has input focus.
        minimized (bool): True if the window is iconified / not viewable.
    """

    def __init__(self, initial_handle: int, initial_width: int, initial_height: int):
        """
        Initialize the tracker with a target window.

        Args:
            initial_handle: X11 window ID of the target.
            initial_width: Initial window width (pixels).
            initial_height: Initial window height (pixels).
        """
        self.handle = initial_handle
        self.width = initial_width
        self.height = initial_height
        self.alive = True
        self.active = True
        self.minimized = False

        # XCB connection and helper objects
        self._conn: Optional[xcffib.Connection] = None
        self._atoms: Optional[AtomCache] = None
        self._root: Optional[int] = None

        self._open_connection()

    def _open_connection(self) -> None:
        """
        Open an XCB connection and initialise atoms and root window ID.

        If the connection fails, `alive` is set to False and a warning is logged.
        Subsequent calls will retry.
        """
        # Close any existing connection first
        self.close()

        try:
            self._conn = open_xcb_connection()
            if self._conn is None:
                logger.warning("Failed to open XCB connection for WindowTracker")
                self.alive = False
                return

            self._atoms = AtomCache(self._conn)
            setup = self._conn.get_setup()
            self._root = setup.roots[0].root
            self.alive = True
            logger.debug(f"Opened XCB connection for window {self.handle:#x}")
        except Exception as e:
            logger.error(f"Unexpected error opening XCB connection: {e}")
            self.alive = False
            self._conn = None
            self._atoms = None
            self._root = None

    def close(self) -> None:
        """Close the XCB connection and release resources."""
        close_xcb_connection(self._conn)
        self._conn = None
        self._atoms = None
        self._root = None

    def check_alive(self) -> bool:
        """
        Quickly check if the tracked window still exists.

        This method attempts to get the window attributes (a lightweight call).
        If the window is gone, `alive` is set to False and the handle is cleared.

        Returns:
            bool: True if the window exists and is reachable, False otherwise.
        """
        # If we already know it's dead, no need to check
        if not self.alive:
            return False

        # Ensure we have a valid connection
        if self._conn is None:
            # Try to reopen once
            self._open_connection()
            if self._conn is None:
                self.alive = False
                return False

        try:
            # Lightweight call: GetWindowAttributes
            self._conn.core.GetWindowAttributes(self.handle).reply()
            return True
        except xcffib.xproto.BadWindow:
            logger.debug(f"Window {self.handle:#x} no longer exists (BadWindow)")
            self.alive = False
            self.handle = 0
            return False
        except (xcffib.xproto.BadDrawable, xcffib.ConnectionError) as e:
            logger.debug(f"XCB error during alive check: {e}")
            # Could be a stale connection - attempt to reopen
            self._open_connection()
            if self._conn is not None:
                # Retry once with new connection
                try:
                    self._conn.core.GetWindowAttributes(self.handle).reply()
                    return True
                except xcffib.xproto.BadWindow:
                    self.alive = False
                    self.handle = 0
                    return False
            self.alive = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error in check_alive: {e}")
            # Assume still alive to avoid false positives
            return True

    def update(self, force: bool = False) -> bool:
        """
        Query the current window geometry and state. Returns True if any change occurred.

        The method refreshes the window's width, height, minimized status, and
        active (focused) status. It also attempts to recover from a dead connection
        by reopening it once.

        Args:
            force: If True, always treat the update as a change and refresh all internal
                   state even if dimensions didn't change (useful after a manual re-attach).

        Returns:
            bool: True if the window's size, handle, or state changed,
                  False if everything is unchanged.
        """
        if not self.alive:
            return False

        # Ensure we have a valid connection; if not, try to reopen
        if self._conn is None:
            self._open_connection()
            if self._conn is None:
                return False

        try:
            # Get window geometry (x, y, width, height)
            geom = get_window_geometry(self._conn, self.handle)
            if geom is None:
                raise xcffib.xproto.BadWindow(self.handle)

            _, _, new_width, new_height = geom

            # Get window attributes to determine minimised state
            attrs = self._conn.core.GetWindowAttributes(self.handle).reply()
            # MapState: 0 = Unmapped, 1 = Unviewable, 2 = Viewable
            self.minimized = attrs.map_state != xcffib.xproto.MapState.Viewable

            # Determine if the window is active (focused)
            self.active = self._is_active_window()

        except xcffib.xproto.BadWindow:
            logger.debug(f"Window {self.handle:#x} no longer exists (update)")
            self.alive = False
            self.handle = 0
            return False
        except (xcffib.xproto.BadDrawable, xcffib.ConnectionError) as e:
            logger.debug(f"XCB error during update: {e}, attempting reconnect")
            # Attempt to reopen the connection and retry once
            self._open_connection()
            if self._conn is not None:
                return self.update(force)  # Recursive retry (depth 1)
            self.alive = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error in update: {e}", exc_info=True)
            return False

        # Detect changes
        handle_changed = False  # X11 window IDs are immutable, but kept for clarity
        size_changed = (new_width != self.width) or (new_height != self.height)

        if size_changed or force:
            logger.info(
                f"WindowTracker: change detected: size {self.width}x{self.height} "
                f"-> {new_width}x{new_height}"
            )
            self.width = new_width
            self.height = new_height
            return True

        return False

    def _is_active_window(self) -> bool:
        """
        Check if the tracked window is currently the active (focused) window.

        Returns:
            bool: True if the window has focus, False otherwise.
        """
        if self._conn is None or self._root is None or self._atoms is None:
            return False

        try:
            cookie = self._conn.core.GetProperty(
                False,
                self._root,
                self._atoms.get("_NET_ACTIVE_WINDOW"),
                xcffib.xproto.Atom.WINDOW,
                0,
                1,
            )
            reply = cookie.reply()
            if reply and reply.value_len:
                # The property value is a 32-bit window ID
                active_handle = reply.value.to_atoms()[0]
                return active_handle == self.handle
            return False
        except Exception as e:
            logger.debug(f"Failed to get active window: {e}")
            return False
