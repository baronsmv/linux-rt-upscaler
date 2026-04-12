import ctypes
import logging
import os
from typing import Any, List, Tuple

logger = logging.getLogger(__name__)

_lib_path = os.path.join(os.path.dirname(__file__), "capture_x11.so")
_lib = ctypes.CDLL(_lib_path)

_MAX_DAMAGE_RECTS = 256


class DamageRect(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("width", ctypes.c_int),
        ("height", ctypes.c_int),
    ]


_lib.capture_create.argtypes = [
    ctypes.c_ulong,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
]
_lib.capture_create.restype = ctypes.c_void_p

_lib.capture_grab_damage.argtypes = [
    ctypes.c_void_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.POINTER(DamageRect),
    ctypes.c_int,
]
_lib.capture_grab_damage.restype = ctypes.c_int

_lib.capture_destroy.argtypes = [ctypes.c_void_p]
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
        self._rects_buffer = (DamageRect * _MAX_DAMAGE_RECTS)()

        self._ctx = _lib.capture_create(
            self.handle, self.crop_left, self.crop_top, self.width, self.height
        )
        if not self._ctx:
            raise RuntimeError("Failed to create capture context")

        logger.info(f"FrameGrabber initialized: {self.width}x{self.height}")

    def grab(self) -> Tuple[memoryview, bool, List[Tuple[int, int, int, int]]]:
        num_rects = _lib.capture_grab_damage(
            self._ctx, self.buffer, self._rects_buffer, _MAX_DAMAGE_RECTS
        )
        if num_rects == -1:
            raise RuntimeError("capture failed")
        is_dirty = num_rects > 0
        rects = []
        if is_dirty:
            for i in range(num_rects):
                r = self._rects_buffer[i]
                rects.append((r.x, r.y, r.width, r.height))
        return memoryview(self.buffer), is_dirty, rects

    def close(self):
        if hasattr(self, "_ctx") and self._ctx:
            _lib.capture_destroy(self._ctx)
            self._ctx = None

    def __del__(self):
        if hasattr(self, "_ctx") and self._ctx:
            _lib.capture_destroy(self._ctx)
