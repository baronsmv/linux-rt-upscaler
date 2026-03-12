import ctypes
import os

_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "captureRGBX.so"))


class FrameGrabber:
    def __init__(self, window_info):
        self.handle = window_info.handle
        self.width = window_info.width
        self.height = window_info.height
        self.buffer_size = self.width * self.height * 4
        self.buffer = (ctypes.c_ubyte * self.buffer_size)()

    def grab(self):
        """Capture a frame and return a memoryview of the raw RGBA data."""
        _lib.captureBGRX(0, 0, self.width, self.height, self.handle, self.buffer)
        return memoryview(self.buffer)
