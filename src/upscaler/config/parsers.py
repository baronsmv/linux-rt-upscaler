import logging
import re
from typing import Tuple

from PySide6.QtGui import QColor

from . import Config

logger = logging.getLogger(__name__)


def _color_string_to_float4(color_str: str) -> Tuple[float, float, float, float]:
    """
    Convert any valid CSS color string to normalized (b, g, r, a) for the shader.
    The shader expects BGRA order, so it returns blue, green, red, alpha.

    Supports:
        - Named colors: "red", "blue", "black", "transparent", etc.
        - Hex: "#RGB", "#RRGGBB", "#RRGGBBAA", "#AARRGGBB"
        - Functional: "rgb(255,0,0)", "rgba(255,0,0,0.5)", "hsl(120,100%,50%)"

    If the string is invalid, falls back to opaque black.
    """
    color_str = color_str.strip()
    hex_match = re.match(r"^#([0-9A-Fa-f]{3,8})$", color_str)

    if hex_match:
        hex_val = hex_match.group(1)
        # Convert #RGB -> #RRGGBB
        if len(hex_val) == 3:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
            a = 255
        elif len(hex_val) == 4:
            # #RGBA -> #RRGGBBAA (we'll reorder alpha to front for Qt)
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
            a = int(hex_val[3] * 2, 16)
        elif len(hex_val) == 6:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            a = 255
        elif len(hex_val) == 8:
            # Assume #RRGGBBAA, reorder to #AARRGGBB for Qt
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            a = int(hex_val[6:8], 16)
        else:
            r = g = b = 0
            a = 255

        qcolor = QColor(f"#{a:02x}{r:02x}{g:02x}{b:02x}")
        result = (qcolor.blueF(), qcolor.greenF(), qcolor.redF(), qcolor.alphaF())
        logger.debug(f"Parsed color '{color_str}' -> BGRA: {result}")
        return result

    # rgb/rgba functional notation
    rgba_match = re.match(
        r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)",
        color_str,
        re.IGNORECASE,
    )
    if rgba_match:
        r = int(rgba_match.group(1))
        g = int(rgba_match.group(2))
        b = int(rgba_match.group(3))
        a_str = rgba_match.group(4)
        a = float(a_str) if a_str else 1.0
        # Clamp values to valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        a = max(0.0, min(1.0, a))
        result = (b / 255.0, g / 255.0, r / 255.0, a)
        logger.debug(f"Parsed color '{color_str}' -> BGRA: {result}")
        return result

    # Named colors and other formats handled by QColor
    qcolor = QColor(color_str)
    if not qcolor.isValid():
        logger.warning(
            f"Invalid color string '{color_str}', falling back to opaque black"
        )
        return (0.0, 0.0, 0.0, 1.0)

    result = (qcolor.blueF(), qcolor.greenF(), qcolor.redF(), qcolor.alphaF())
    logger.debug(f"Parsed color '{color_str}' -> BGRA: {result}")
    return result


def parse_config(config: Config):
    config.background_color = _color_string_to_float4(config.background_color)
