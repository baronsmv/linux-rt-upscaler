import ctypes
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_lib_path = os.path.join(os.path.dirname(__file__), "captureRGBX.so")
_lib = ctypes.CDLL(_lib_path)
logger.debug(f"Loaded capture library from {_lib_path}")


class FrameGrabber:
    """
    Grabs frames from an X11 window using the fast C extension.
    The buffer is allocated once and reused.
    """

    def __init__(self, window_info: Any) -> None:
        """
        :param window_info: A WindowInfo object (from the window module) containing
                            handle, width, height.
        """
        self.handle = window_info.handle
        self.width = window_info.width
        self.height = window_info.height
        self.buffer_size = self.width * self.height * 4
        self.buffer = (ctypes.c_ubyte * self.buffer_size)()
        logger.info(
            f"FrameGrabber initialized: handle={self.handle}, "
            f"{self.width}x{self.height}, buffer={self.buffer_size} bytes"
        )

    def grab(self) -> memoryview:
        """
        Capture a frame and return a memoryview of the raw RGBA data.
        The C function `captureBGRX` writes directly into `self.buffer`.
        """
        logger.debug(f"Grabbing frame from window {self.handle}")
        try:
            _lib.captureBGRX(0, 0, self.width, self.height, self.handle, self.buffer)
            logger.debug("Frame grabbed successfully")
        except Exception as e:
            logger.error(f"Exception during captureBGRX call: {e}", exc_info=True)
            # Re-raise because we cannot recover from a C crash
            raise
        return memoryview(self.buffer)
