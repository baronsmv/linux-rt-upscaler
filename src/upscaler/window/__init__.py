"""Window public modules."""

from .acquisition import (
    acquire_target_window,
    activate_window,
    get_active_window,
    get_window_class,
    find_window_by_pid,
    find_window_by_title,
    launch_and_find_window,
    list_windows,
)
from .connection import open_xcb_connection, close_xcb_connection
from .focus import FocusMonitor
from .hotkeys import HotkeyManager
from .info import AtomCache, WindowInfo, get_window_icon, get_window_name
from .tracker import WindowTracker

__all__ = [
    "AtomCache",
    "FocusMonitor",
    "HotkeyManager",
    "WindowInfo",
    "WindowTracker",
    "acquire_target_window",
    "activate_window",
    "close_xcb_connection",
    "get_active_window",
    "get_window_class",
    "find_window_by_pid",
    "find_window_by_title",
    "get_window_icon",
    "get_window_name",
    "launch_and_find_window",
    "list_windows",
    "open_xcb_connection",
]
