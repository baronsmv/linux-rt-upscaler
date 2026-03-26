"""Window modules."""

from .acquisition import acquire_target_window
from .display import open_x_display, close_x_display, get_display
from .focus import FocusMonitor
from .info import WindowInfo
from .tracker import WindowTracker

__all__ = [
    "FocusMonitor",
    "WindowInfo",
    "WindowTracker",
    "acquire_target_window",
    "close_x_display",
    "get_display",
    "open_x_display",
]
