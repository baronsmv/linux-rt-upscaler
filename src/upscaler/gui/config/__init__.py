"""GUI config public module."""

from .config import GUIConfig, GUIStyleOverrides
from .manager import ConfigManager
from .palette import (
    GUIPalette,
    PRESETS,
    find_matching_preset,
    palette_to_internal,
    palette_to_stylesheet,
)
from .style import resolve_gui_config
from .yaml import load_gui_style, save_gui_style

__all__ = [
    "ConfigManager",
    "GUIConfig",
    "GUIPalette",
    "GUIStyleOverrides",
    "PRESETS",
    "find_matching_preset",
    "load_gui_style",
    "palette_to_internal",
    "palette_to_stylesheet",
    "resolve_gui_config",
    "save_gui_style",
]
