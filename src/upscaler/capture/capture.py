import ctypes
import logging
import os
from typing import Any, Tuple

logger = logging.getLogger(__name__)

_lib_path = os.path.join(os.path.dirname(__file__), "capture_x11.so")
_lib = ctypes.CDLL(_lib_path)


class CaptureContext(ctypes.Structure):
    pass


_lib.capture_create.argtypes = [
    ctypes.c_ulong,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
]
_lib.capture_create.restype = ctypes.POINTER(CaptureContext)

_lib.capture_grab.argtypes = [
    ctypes.POINTER(CaptureContext),
    ctypes.POINTER(ctypes.c_ubyte),
]
_lib.capture_grab.restype = ctypes.c_int  # 0=success, 1=no damage, -1=error

_lib.capture_destroy.argtypes = [ctypes.POINTER(CaptureContext)]
_lib.capture_destroy.restype = None


class FrameGrabber:
    def __init__(
        self, window_info: Any, crop_left=0, crop_top=0, crop_right=0, crop_bottom=0
    ):
        self.handle = window_info.handle
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.width = window_info.width - crop_left - crop_right
        self.height = window_info.height - crop_top - crop_bottom

        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Invalid cropped dimensions: {self.width}x{self.height}")

        self.buffer_size = self.width * self.height * 4
        self.buffer = (ctypes.c_ubyte * self.buffer_size)()

        self._ctx = _lib.capture_create(
            self.handle, self.crop_left, self.crop_top, self.width, self.height
        )
        if not self._ctx:
            raise RuntimeError(
                "Failed to create capture context (XShm/XDamage unavailable)"
            )

        logger.info(f"FrameGrabber initialized: {self.width}x{self.height}")

    def grab(self) -> Tuple[memoryview, bool]:
        """
        Capture a frame.
        Returns:
            (memoryview of buffer, is_dirty)
            is_dirty is False if the window contents have not changed (damage tracking).
        """
        result = _lib.capture_grab(self._ctx, self.buffer)
        if result == -1:
            raise RuntimeError("capture_grab failed (window closed?)")
        is_dirty = result == 0
        return memoryview(self.buffer), is_dirty

    def __del__(self):
        if hasattr(self, "_ctx") and self._ctx:
            _lib.capture_destroy(self._ctx)
