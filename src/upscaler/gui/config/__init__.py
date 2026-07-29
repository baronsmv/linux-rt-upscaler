"""GUI config public module."""

from .config import GUIConfig, GUIPalette
from .manager import ConfigManager
from .presets import PRESETS

__all__ = [
    "ConfigManager",
    "GUIConfig",
    "GUIPalette",
    "PRESETS",
]
