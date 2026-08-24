from __future__ import annotations

import logging
import threading
from typing import Dict, Optional, Any

from PySide6.QtCore import QObject, Signal

from ..config import find_matching_profile
from ..window import (
    WindowInfo,
    activate_window,
    close_xcb_connection,
    list_windows,
    open_xcb_connection,
)

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
        self._wake_event = threading.Event()
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start (or restart) the polling thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._wake_event.clear()
            self._thread = threading.Thread(
                target=self._poll, name="DaemonMonitor", daemon=True
            )
            self._thread.start()
            logger.debug("Daemon: Monitor started")

    def stop(self) -> None:
        """Stop the polling thread."""
        with self._lock:
            self._running = False
            self._wake_event.set()
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
                    for profile_name, profile_data in self._profiles.items():
                        if not self._running:
                            break

                        # Skip daemon-excluded profiles entirely
                        if profile_data.get("options", {}).get("daemon_exclude", False):
                            logger.debug(
                                "Skipping profile '%s' (daemon_exclude=True)",
                                profile_name,
                            )
                            continue

                        # Check windows for this profile, using the existing
                        # find_matching_profile with a single-profile dict
                        for win in windows:
                            if not self._running:
                                break

                            matched_name, _ = find_matching_profile(
                                {profile_name: profile_data}, win
                            )
                            if matched_name is not None:
                                logger.info(
                                    "Daemon: Matched window '%s' with profile '%s'",
                                    win.title,
                                    profile_name,
                                )
                                activate_window(win.handle)
                                self.match_found.emit(win)
                                self._running = False  # stop polling
                                return
                except Exception as e:
                    logger.error(f"Daemon: Polling error: {e}", exc_info=True)

                self._wake_event.wait(timeout=self._interval)
                self._wake_event.clear()

        finally:
            close_xcb_connection(conn)
            logger.debug("Daemon: Monitor thread finished")
