import logging
import re
from typing import Any, Optional

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


def validate_geometry(geometry: str) -> None:
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


def validate_color(color_str: str) -> None:
    if not QColor(color_str).isValid():
        logger.error(f"Invalid color string '{color_str}'")
        exit(1)


def validate_config(config: Any) -> None:
    validate_geometry(config.output_geometry)
    validate_color(config.background_color)
    validate_number(config.scale_factor, "scale_factor", 0, left_inclusive=False)
    validate_number(config.crop_top, "crop_top", 0)
    validate_number(config.crop_bottom, "crop_bottom", 0)
    validate_number(config.crop_left, "crop_left", 0)
    validate_number(config.crop_right, "crop_right", 0)
    validate_number(config.target_delay, "target_delay", 0)
    validate_number(config.pid_timeout, "pid_timeout", 0)
    validate_number(config.class_timeout, "class_timeout", 0)
    validate_number(config.total_timeout, "total_timeout", 0)
