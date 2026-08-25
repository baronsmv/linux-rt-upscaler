"""Real-Time Upscaler for Linux"""

import sys

from .api import Config, UpscalerSession, WindowInfo, exceptions, acquisition

sys.modules.setdefault(__name__ + ".acquisition", acquisition)
sys.modules.setdefault(__name__ + ".exceptions", exceptions)

__all__ = [
    "Config",
    "UpscalerSession",
    "WindowInfo",
    "acquisition",
    "exceptions",
]
__version__ = "1.1.3"
