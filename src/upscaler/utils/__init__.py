"""Utility modules."""

from .config import (
    OverlayMode,
    get_version,
    Config,
    parse_args,
    load_yaml_config,
    apply_overrides,
    find_profile,
    find_matching_profile,
)
from .environment import setup_environment
from .logging import logger, setup_logging
from .monitor import logger, get_monitor_list, get_monitor, get_monitor_geometry
from .parsers import logger, color_string_to_float4, parse_output_geometry
from .validators import (
    validate_number,
    validate_geometry,
    validate_color,
    validate_config,
)
from .window import (
    WindowInfo,
    list_windows,
    get_active_window,
    find_by_pid,
    launch_and_find_window,
    select_window_interactive,
    acquire_target_window,
    get_active_window_after_delay,
)
from .x11 import (
    get_display,
    AtomCache,
    get_window_geometry,
    get_window_name,
    get_window_class,
    get_window_pid,
    is_viewable,
    is_application_window,
    enumerate_all_windows,
)

__all__ = [
    "AtomCache",
    "Config",
    "OverlayMode",
    "WindowInfo",
    "acquire_target_window",
    "apply_overrides",
    "color_string_to_float4",
    "enumerate_all_windows",
    "find_by_pid",
    "find_matching_profile",
    "find_profile",
    "get_active_window",
    "get_active_window_after_delay",
    "get_display",
    "get_monitor",
    "get_monitor_geometry",
    "get_monitor_list",
    "get_version",
    "get_window_class",
    "get_window_geometry",
    "get_window_name",
    "get_window_pid",
    "is_application_window",
    "is_viewable",
    "launch_and_find_window",
    "list_windows",
    "load_yaml_config",
    "parse_args",
    "parse_output_geometry",
    "select_window_interactive",
    "setup_environment",
    "setup_logging",
    "validate_color",
    "validate_config",
    "validate_geometry",
    "validate_number",
]
