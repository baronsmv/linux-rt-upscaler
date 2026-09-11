"""GUI config public module."""

from .config import GUIConfig, GUIPalette
from .manager import ConfigManager
from .presets import PRESETS
from .scaling import scale_gui_config
from .yaml import load_gui_style, save_gui_style

__all__ = [
    "ConfigManager",
    "GUIConfig",
    "GUIPalette",
    "PRESETS",
    "load_gui_style",
    "save_gui_style",
    "scale_gui_config",
]
