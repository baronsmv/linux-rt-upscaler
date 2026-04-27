import logging
import threading
import time
from typing import Optional

import xcffib
from PySide6.QtCore import QObject, Signal

from .acquisition import activate_window
from .connection import open_xcb_connection, close_xcb_connection
from .info import AtomCache, WindowInfo, get_window_geometry, get_window_name

logger = logging.getLogger(__name__)


class FocusMonitor(QObject):
    """
    Monitors the active X11 window and emits a signal when it changes.

    The monitor runs a polling loop in a separate daemon thread. It is
    safe to use from the main Qt thread because signals are automatically
    queued to the main thread.

    Signals:
        focus_changed: Emitted when the active window changes, providing the
                       new WindowInfo object.
    """

    focus_changed = Signal(WindowInfo)

    def __init__(self, interval: float = 1.0) -> None:
        """
        Initialize the focus monitor.

        Args:
            interval: Polling interval in seconds (default 1.0).
        """
        super().__init__()
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._current_handle: Optional[int] = None

    def start(self) -> None:
        """Start the focus monitor thread."""
        if self._running:
            logger.warning("FocusMonitor already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._poll, name="FocusMonitor")
        self._thread.daemon = True
        self._thread.start()
        logger.info("Focus monitor started")

    def stop(self) -> None:
        """Stop the focus monitor thread and wait for it to finish."""
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Focus monitor stopped")

    def _poll(self) -> None:
        """
        Poll the active window in a loop.

        This method runs in its own thread and uses a dedicated XCB connection.
        It reconnects automatically if the connection is lost.
        """
        # Open a dedicated XCB connection for this thread
        conn = open_xcb_connection()
        if conn is None:
            logger.error("Failed to open XCB connection for FocusMonitor")
            return

        atoms = AtomCache(conn)
        root = conn.get_setup().roots[0].root

        try:
            while self._running:
                try:
                    # Get the currently active window
                    active_handle = self._get_active_window(conn, root, atoms)
                    if (
                        active_handle is not None
                        and active_handle != self._current_handle
                    ):
                        # Fetch full window info
                        win_info = self._get_window_info(conn, active_handle, atoms)
                        if win_info:
                            logger.info(
                                f"Focus changed to: {win_info.handle:#x} - {win_info.title}"
                            )
                            self._current_handle = active_handle
                            activate_window(win_info.handle)

                            # Emit signal (queued to main thread)
                            self.focus_changed.emit(win_info)

                except (xcffib.ConnectionError, xcffib.xproto.BadWindow) as e:
                    logger.warning(f"XCB connection error in focus monitor: {e}")
                    # Attempt to reconnect
                    close_xcb_connection(conn)
                    conn = open_xcb_connection()
                    if conn is None:
                        logger.error("Focus monitor: reconnection failed, stopping")
                        break
                    atoms = AtomCache(conn)
                    root = conn.get_setup().roots[0].root
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected error in focus monitor: {e}", exc_info=True
                    )

                time.sleep(self.interval)

        finally:
            close_xcb_connection(conn)
            logger.debug("Focus monitor thread finished")

    def _get_active_window(
        self,
        conn: xcffib.Connection,
        root: int,
        atoms: AtomCache,
    ) -> Optional[int]:
        """
        Return the X11 window ID of the currently active window.

        Args:
            conn: Active XCB connection.
            root: Root window ID.
            atoms: AtomCache for the connection.

        Returns:
            Window ID, or None if no active window or property not found.
        """
        try:
            cookie = conn.core.GetProperty(
                False,
                root,
                atoms.get("_NET_ACTIVE_WINDOW"),
                xcffib.xproto.Atom.WINDOW,
                0,
                1,
            )
            reply = cookie.reply()
            if reply and reply.value_len:
                # The property value is a 32-bit window ID
                return reply.value.to_atoms()[0]
            return None
        except Exception as e:
            logger.debug(f"Failed to get active window: {e}")
            return None

    def _get_window_info(
        self,
        conn: xcffib.Connection,
        win_handle: int,
        atoms: AtomCache,
    ) -> Optional[WindowInfo]:
        """
        Fetch full window information (geometry and title) for a given XID.

        Args:
            conn: Active XCB connection.
            win_handle: X11 window ID.
            atoms: AtomCache for the connection.

        Returns:
            WindowInfo object, or None if the window is invalid or has no geometry.
        """
        try:
            geom = get_window_geometry(conn, win_handle)
            if geom is None:
                return None
            _, _, w, h = geom
            title = get_window_name(conn, win_handle, atoms) or "unknown"
            return WindowInfo(win_handle, w, h, title)
        except Exception as e:
            logger.debug(f"Failed to get window info for {win_handle:#x}: {e}")
            return None
