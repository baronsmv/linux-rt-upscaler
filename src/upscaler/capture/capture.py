"""
X11 window capture module using a custom C library.
Provides a capture_worker function that puts raw bitmap data into a queue.
"""

import ctypes
import os

LibName = "captureRGBX.so"
AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LibName
cap = ctypes.CDLL(AbsLibPath)

# Global flag to signal worker thread to stop
running = True


def capture_worker(capture_queue, handle, clientW, clientH):
    """
    Worker thread that continuously captures the specified X11 window.
    Puts a ctypes buffer (clientW*clientH*4 bytes) into capture_queue.
    """
    global running
    cbuffer = (ctypes.c_ubyte * clientW * clientH * 4)()
    # Timing variables (optional)
    count = 0

    while running:
        # Note: window must not be minimized, otherwise capture may fail.
        cap.captureBGRX(0, 0, clientW, clientH, handle, cbuffer)
        if running:
            capture_queue.put(cbuffer)
        count += 1
