"""Real-Time Upscaler for Linux"""

import sys

from .api import UpscalerSession, exceptions, windows

sys.modules.setdefault(__name__ + ".exceptions", exceptions)
sys.modules.setdefault(__name__ + ".windows", windows)

__all__ = [
    "UpscalerSession",
    "exceptions",
    "windows",
]
__version__ = "1.1.1.post2"
