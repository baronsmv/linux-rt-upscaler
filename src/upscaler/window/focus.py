import logging
import threading
import time
from typing import Optional, Callable

from Xlib.display import Display
from ewmh import EWMH

from .acquisition import get_active_window
from .info import WindowInfo

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
        # Use a separate X connection to avoid interfering with other threads
        display = Display()
        ewmh = EWMH(display)

        while self._running:
            try:
                active = ewmh.getActiveWindow()
                if active and active.id != self._current_handle:
                    # Get full window info
                    win_info = get_active_window(display, ewmh)
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

        display.close()
