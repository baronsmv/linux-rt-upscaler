"""Utility modules."""

from .color import color_string_to_float4, color_tuple_to_string
from .exceptions import (
    ConfigError,
    EventLoopError,
    SessionAlreadyRunning,
    UpscalerError,
    WindowNotFound,
)
from .geometry import (
    OverlayGeometry,
    calculate_scaling_rect,
    compute_overlay_geometry,
    parse_output_geometry,
)
from .screen import get_base_geometry, list_monitors
from .settings import scheme_is_light

__all__ = [
    "ConfigError",
    "EventLoopError",
    "OverlayGeometry",
    "SessionAlreadyRunning",
    "UpscalerError",
    "WindowNotFound",
    "calculate_scaling_rect",
    "color_string_to_float4",
    "color_tuple_to_string",
    "compute_overlay_geometry",
    "get_base_geometry",
    "list_monitors",
    "scheme_is_light",
    "parse_output_geometry",
]
