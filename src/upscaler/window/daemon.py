import logging
import threading
import time
from typing import Dict, Optional, Any

from PySide6.QtCore import QObject, Signal

from .acquisition import activate_window, list_windows
from .connection import open_xcb_connection, close_xcb_connection
from .info import WindowInfo
from ..config import find_matching_profile

logger = logging.getLogger(__name__)


class DaemonMonitor(QObject):
    """
    Periodically scans visible windows and emits a signal when one matches
    any profile.

    The monitor runs its own daemon thread with a dedicated XCB connection.
    It stops automatically once a match is found.  Call :meth:`start` again
    to resume polling.
    """

    match_found = Signal(WindowInfo)

    def __init__(
        self,
        profiles: Dict[str, Any],
        interval: float = 2.0,
    ) -> None:
        super().__init__()
        self._profiles = profiles
        self._interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start (or restart) the polling thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(
                target=self._poll, name="DaemonMonitor", daemon=True
            )
            self._thread.start()
            logger.debug("Daemon: Monitor started")

    def stop(self) -> None:
        """Stop the polling thread."""
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.debug("Daemon: Monitor stopped")

    # ------------------------------------------------------------------
    #  Polling loop
    # ------------------------------------------------------------------
    def _poll(self) -> None:
        conn = open_xcb_connection()
        if conn is None:
            logger.error("Daemon: Monitor failed to open XCB connection")
            return

        try:
            while self._running:
                try:
                    windows = list_windows(conn=conn)
                    for win in windows:
                        if not self._running:
                            break
                        name, data = find_matching_profile(self._profiles, win.title)
                        if data is not None:
                            # Per-profile daemon exclusion (daemon=False)
                            profile_daemon = data.get("options", {}).get("daemon")
                            if profile_daemon is False:
                                logger.debug(
                                    "Skipping profile '%s' (daemon=False)", name
                                )
                                continue
                            logger.info(
                                "Daemon: Matched window '%s' with profile '%s'",
                                win.title,
                                name,
                            )
                            activate_window(win.handle)
                            self.match_found.emit(win)
                            self._running = False  # stop polling
                            return
                except Exception as e:
                    logger.error(f"Daemon: Polling error: {e}", exc_info=True)

                time.sleep(self._interval)

        finally:
            close_xcb_connection(conn)
            logger.debug("Daemon: Monitor thread finished")
