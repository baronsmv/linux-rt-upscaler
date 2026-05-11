"""Window public modules."""

from .acquisition import acquire_target_window, activate_window, list_windows
from .connection import open_xcb_connection, close_xcb_connection
from .focus import FocusMonitor
from .hotkeys import HotkeyManager
from .info import WindowInfo, get_window_icon
from .tracker import WindowTracker

__all__ = [
    "FocusMonitor",
    "HotkeyManager",
    "WindowInfo",
    "WindowTracker",
    "acquire_target_window",
    "activate_window",
    "close_xcb_connection",
    "get_window_icon",
    "list_windows",
    "open_xcb_connection",
]
