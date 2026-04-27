import logging
import re
import sys
from typing import Any, Optional, Dict, Tuple

from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


def validate_number(
    value: float,
    arg_name: str,
    left_limit: Optional[float] = None,
    right_limit: Optional[float] = None,
    left_inclusive: bool = True,
    right_inclusive: bool = True,
) -> None:
    """
    Validate that a numeric value lies within specified bounds.

    Args:
        value: The number to validate.
        arg_name: Name of the argument (for error messages).
        left_limit: Lower bound (optional).
        right_limit: Upper bound (optional).
        left_inclusive: If True, lower bound is inclusive (value >= left_limit).
                        If False, lower bound is exclusive (value > left_limit).
        right_inclusive: If True, upper bound is inclusive (value <= right_limit).
                         If False, upper bound is exclusive (value < right_limit).

    Raises:
        ValueError: If the value is outside the allowed range, with a detailed message.
    """
    # Determine if the value violates the lower bound
    if left_limit is not None:
        if left_inclusive:
            if value < left_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be >= {left_limit}, got {value}"
                )
                sys.exit(1)
        else:
            if value <= left_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be > {left_limit}, got {value}"
                )
                sys.exit(1)

    # Determine if the value violates the upper bound
    if right_limit is not None:
        if right_inclusive:
            if value > right_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be <= {right_limit}, got {value}"
                )
                sys.exit(1)
        else:
            if value >= right_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be < {right_limit}, got {value}"
                )
                sys.exit(1)


def validate_geometry(geometry: str, _: str) -> None:
    """Validate output geometry string."""
    geometry = geometry.strip()
    pattern = re.compile(
        r"^(stretch|fit|cover)$|"  # pure mode names
        r"^(\d+(?:\.\d+)?)%!?$|"  # percentage (optional !)
        r"^(\d+)x!?$|"  # fixed width (optional !)
        r"^x(\d+)!?$|"  # fixed height (optional !)
        r"^(\d+)x(\d+)[!^]?$"  # WxH with optional ! or ^
    )

    if not pattern.match(geometry):
        logger.error(
            f"Invalid geometry string: {geometry!r}\n"
            "Allowed formats:\n"
            "  stretch, fit, cover\n"
            "  50%, 50%!\n"
            "  1920x, 1920x!\n"
            "  x1080, x1080!\n"
            "  1920x1080, 1920x1080!, 1920x1080^"
        )
        sys.exit(1)


def validate_color(color_str: str, _: str) -> None:
    """Validate CSS color string, supporting #RRGGBBAA, #AARRGGBB, rgb(), rgba()."""
    color_str = color_str.strip()
    hex_match = re.match(r"^#([0-9A-Fa-f]{3,8})$", color_str)

    if hex_match:
        hex_val = hex_match.group(1)
        if len(hex_val) in (3, 4, 6, 8):
            return
        else:
            logger.error(
                f"Invalid hex color string '{color_str}' (must be 3, 4, 6, or 8 hex digits)"
            )
            sys.exit(1)

    # Check for rgb/rgba functional notation
    rgba_match = re.match(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
        color_str,
        re.IGNORECASE,
    )
    if rgba_match:
        r, g, b = (
            int(rgba_match.group(1)),
            int(rgba_match.group(2)),
            int(rgba_match.group(3)),
        )
        a = float(rgba_match.group(4)) if rgba_match.group(4) else 1.0
        if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0.0 <= a <= 1.0:
            return
        else:
            logger.error(
                f"Invalid rgb/rgba values in '{color_str}' (must be 0-255 for rgb, 0.0-1.0 for alpha)"
            )
            sys.exit(1)

    # Fallback to QColor for named colors and other formats
    if not QColor(color_str).isValid():
        logger.error(f"Invalid color string '{color_str}'")
        sys.exit(1)


_VALIDATORS: Dict[str, Tuple] = {
    "lanczos_blur": (validate_number, "lanczos_blur", 0),
    "scale_factor": (validate_number, "scale_factor", 0, None, False),
    "output_geometry": (validate_geometry, "output_geometry"),
    "background_color": (validate_color, "background_color"),
    "crop_top": (validate_number, "crop_top", 0),
    "crop_bottom": (validate_number, "crop_bottom", 0),
    "crop_left": (validate_number, "crop_left", 0),
    "crop_right": (validate_number, "crop_right", 0),
    "offset_x": (validate_number, "offset_x"),
    "offset_y": (validate_number, "offset_y"),
    "osd_duration": (validate_number, "osd_duration", 0),
    "vulkan_buffer_pool_size": (validate_number, "vulkan_buffer_pool_size", 0),
    "frame_timeout_ns": (validate_number, "frame_timeout_ns", 0),
    "tile_size": (validate_number, "tile_size", 0, None, False),
    "tile_context_margin": (validate_number, "tile_context_margin", 0),
    "max_tile_layers": (validate_number, "max_tile_layers", 0),
    "area_threshold": (validate_number, "area_threshold", 0, 1),
    "target_delay": (validate_number, "target_delay", 0),
    "pid_timeout": (validate_number, "pid_timeout", 0),
    "class_timeout": (validate_number, "class_timeout", 0),
    "total_timeout": (validate_number, "total_timeout", 0),
}


def validate_config(config: Any) -> None:
    """Validate a full Config instance (or any object with the required attributes)."""
    for field_name, (validator, arg_name, *args) in _VALIDATORS.items():
        value = getattr(config, field_name, None)
        if value is not None:
            validator(value, arg_name, *args)


def validate_overrides(overrides: Dict[str, Any]) -> None:
    """Validate only the keys present in the overrides dictionary."""
    for field_name, value in overrides.items():
        if field_name in _VALIDATORS:
            validator, arg_name, *args = _VALIDATORS[field_name]
            validator(value, arg_name, *args)
