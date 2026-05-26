"""Utility public modules."""

from .args import apply_overrides, get_version, parse_args
from .logging import setup_logging
from .models import (
    BackgroundColor,
    Config,
    OverlayMode,
    VulkanPresentMode,
    DEFAULT_CONFIG,
    DOWNSAMPLERS,
    OUTPUT_GEOMETRIES,
    UPSAMPLERS,
    UPSCALING_MODELS,
    ZOOM_LEVELS,
)
from .parsers import parse_config
from .profiles import (
    find_matching_profile,
    find_profile,
    move_profile_down,
    move_profile_up,
)
from .setup import load_config, setup_config
from .validators import validate_config, validate_overrides
from .yaml import load_yaml_config, save_yaml_config

__all__ = [
    "BackgroundColor",
    "Config",
    "OverlayMode",
    "VulkanPresentMode",
    "DEFAULT_CONFIG",
    "DOWNSAMPLERS",
    "OUTPUT_GEOMETRIES",
    "UPSAMPLERS",
    "UPSCALING_MODELS",
    "ZOOM_LEVELS",
    "apply_overrides",
    "find_matching_profile",
    "find_profile",
    "get_version",
    "load_config",
    "load_yaml_config",
    "move_profile_down",
    "move_profile_up",
    "parse_args",
    "parse_config",
    "validate_config",
    "validate_overrides",
    "save_yaml_config",
    "setup_config",
    "setup_logging",
]
