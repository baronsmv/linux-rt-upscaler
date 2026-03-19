import logging
import re

from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


def output_geometry(geometry: str) -> None:
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


def background_color(color_str: str) -> None:
    if not QColor(color_str).isValid():
        logger.error(f"Invalid color string '{color_str}'")
        exit(1)
