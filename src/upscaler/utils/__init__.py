"""Utility modules."""

from . import exceptions
from .color import color_string_to_float4, color_tuple_to_string
from .exceptions import (
    ConfigError,
    EventLoopError,
    SessionAlreadyRunning,
    SessionError,
    UpscalerError,
    WindowNotFound,
)
from .geometry import (
    OverlayGeometry,
    calculate_scaling_rect,
    compute_overlay_geometry,
    parse_output_geometry,
)
from .hotkeys import (
    DEFAULT_HOTKEYS,
    KEYSYM_MAP,
    MODIFIER_MAP,
    format_hotkey,
    merge_hotkeys,
    parse_hotkey,
)
from .screen import get_base_geometry, list_monitors
from .settings import scheme_is_light

__all__ = [
    "ConfigError",
    "EventLoopError",
    "OverlayGeometry",
    "SessionAlreadyRunning",
    "SessionError",
    "UpscalerError",
    "WindowNotFound",
    "DEFAULT_HOTKEYS",
    "KEYSYM_MAP",
    "MODIFIER_MAP",
    "calculate_scaling_rect",
    "color_string_to_float4",
    "color_tuple_to_string",
    "compute_overlay_geometry",
    "exceptions",
    "format_hotkey",
    "get_base_geometry",
    "list_monitors",
    "merge_hotkeys",
    "parse_hotkey",
    "scheme_is_light",
    "parse_output_geometry",
]
