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

    def __init__(
        self,
        window_info: Any,
        crop_left: int = 0,
        crop_top: int = 0,
        crop_right: int = 0,
        crop_bottom: int = 0,
    ) -> None:
        """
        :param window_info: A WindowInfo object (from the window module) containing
                            handle, width, height.
        :param crop_left: How many pixels to crop from the left.
        :param crop_top: How many pixels to crop from the top.
        :param crop_right: How many pixels to crop from the right.
        :param crop_bottom: How many pixels to crop from the bottom.
        """
        self.handle = window_info.handle
        self.orig_width = window_info.width
        self.orig_height = window_info.height
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.width = self.orig_width - crop_left - crop_right
        self.height = self.orig_height - crop_top - crop_bottom
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Crop results in non‑positive dimensions")
        self.buffer_size = self.width * self.height * 4
        self.buffer = (ctypes.c_ubyte * self.buffer_size)()
        logger.info(
            f"FrameGrabber initialized: handle={self.handle}, "
            f"cropped {self.width}x{self.height} (original {self.orig_width}x{self.orig_height})"
            f", buffer={self.buffer_size} bytes"
        )

    def grab(self) -> memoryview:
        """
        Capture a frame and return a memoryview of the raw RGBA data.
        The C function `captureBGRX` writes directly into `self.buffer`.
        """
        logger.debug(f"Grabbing frame from window {self.handle}")
        result = _lib.captureBGRX(
            self.crop_left,
            self.crop_top,
            self.width,
            self.height,
            self.handle,
            self.buffer,
        )
        if result != 0:
            raise RuntimeError(
                f"captureBGRX failed with code {result} (window probably gone)"
            )
        logger.debug("Frame grabbed successfully")
        return memoryview(self.buffer)
