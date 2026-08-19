"""Real-Time Upscaler for Linux"""

from .api import UpscalerSession, exceptions, windows

__all__ = [
    "UpscalerSession",
    "exceptions",
    "windows",
]
__version__ = "1.1.1.post2"
