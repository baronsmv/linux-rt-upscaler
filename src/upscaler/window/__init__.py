"""Window public modules."""

from .acquisition import acquire_target_window, activate_window, list_windows
from .connection import open_xcb_connection, close_xcb_connection
from .daemon import DaemonMonitor
from .focus import FocusMonitor
from .hotkeys import HotkeyManager
from .info import AtomCache, WindowInfo, get_window_icon, get_window_name
from .tracker import WindowTracker

__all__ = [
    "AtomCache",
    "DaemonMonitor",
    "FocusMonitor",
    "HotkeyManager",
    "WindowInfo",
    "WindowTracker",
    "acquire_target_window",
    "activate_window",
    "close_xcb_connection",
    "get_window_icon",
    "get_window_name",
    "list_windows",
    "open_xcb_connection",
]
