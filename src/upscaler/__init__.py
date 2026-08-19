"""Real-Time Upscaler for Linux"""

import sys

from .api import UpscalerSession, exceptions, acquisition

sys.modules.setdefault(__name__ + ".acquisition", acquisition)
sys.modules.setdefault(__name__ + ".exceptions", exceptions)

__all__ = [
    "UpscalerSession",
    "acquisition",
    "exceptions",
]
__version__ = "1.1.1.post2"
