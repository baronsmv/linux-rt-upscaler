"""Window public modules."""

from .acquisition import acquire_target_window
from .connection import open_xcb_connection, close_xcb_connection
from .focus import FocusMonitor
from .hotkeys import HotkeyManager
from .info import WindowInfo
from .tracker import WindowTracker

__all__ = [
    "FocusMonitor",
    "HotkeyManager",
    "WindowInfo",
    "WindowTracker",
    "acquire_target_window",
    "open_xcb_connection",
    "close_xcb_connection",
]
