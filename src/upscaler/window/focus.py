import logging
import threading
import time
from typing import Optional, Callable

import xcffib
import xcffib.xproto

from .acquisition import get_active_window
from .display import open_xcb_connection, close_xcb_connection
from .info import AtomCache, WindowInfo

logger = logging.getLogger(__name__)


class FocusMonitor:
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[WindowInfo], None]] = None
        self._current_handle: Optional[int] = None

    def start(self, callback: Callable[[WindowInfo], None]) -> None:
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._poll, name="FocusMonitor")
        self._thread.daemon = True
        self._thread.start()
        logger.info("Focus monitor started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            logger.info("Focus monitor stopped")

    def _poll(self) -> None:
        # Use a separate XCB connection for monitoring
        conn = open_xcb_connection()
        if not conn:
            return

        try:
            atoms = AtomCache(conn)
            root = conn.get_setup().roots[0].root

            while self._running:
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
                        active_win = reply.value.to_atoms()[0]
                        if active_win != 0 and active_win != self._current_handle:
                            win_info = get_active_window()
                            if win_info:
                                logger.info(
                                    f"Focus changed to: {win_info.handle} - {win_info.title}"
                                )
                                self._current_handle = win_info.handle
                                if self._callback:
                                    self._callback(win_info)
                except Exception as e:
                    logger.debug(f"Error polling active window: {e}")

                time.sleep(self.interval)
        finally:
            close_xcb_connection(conn)
