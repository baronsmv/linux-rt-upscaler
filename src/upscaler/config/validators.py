import logging
import re
from typing import Any, Optional, Dict, Tuple, Callable

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
                exit(1)
        else:
            if value <= left_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be > {left_limit}, got {value}"
                )
                exit(1)

    # Determine if the value violates the upper bound
    if right_limit is not None:
        if right_inclusive:
            if value > right_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be <= {right_limit}, got {value}"
                )
                exit(1)
        else:
            if value >= right_limit:
                logger.error(
                    f"Invalid argument: {arg_name} must be < {right_limit}, got {value}"
                )
                exit(1)


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
        exit(1)


def validate_color(color_str: str, _: str) -> None:
    """Validate CSS color string."""
    if not QColor(color_str).isValid():
        logger.error(f"Invalid color string '{color_str}'")
        exit(1)


_VALIDATORS: Dict[str, Tuple[Callable, str, ...]] = {
    "output_geometry": (validate_geometry, "output_geometry"),
    "background_color": (validate_color, "background_color"),
    "scale_factor": (validate_number, "scale_factor", 0, None, False, True),
    "crop_top": (validate_number, "crop_top", 0),
    "crop_bottom": (validate_number, "crop_bottom", 0),
    "crop_left": (validate_number, "crop_left", 0),
    "crop_right": (validate_number, "crop_right", 0),
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
