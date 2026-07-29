from __future__ import annotations

import logging
import re
from typing import Tuple

from PySide6.QtGui import QColor

logger = logging.getLogger(__name__)


def color_string_to_float4(
    color: str | Tuple[float, float, float, float],
) -> Tuple[float, float, float, float]:
    """
    Convert any valid CSS color string to normalized (b, g, r, a) for the shader.
    The shader expects BGRA order, so it returns blue, green, red, alpha.

    Supports:
        - Named colors: "red", "blue", "black", "transparent", etc.
        - Hex: "#RGB", "#RRGGBB", "#RRGGBBAA", "#AARRGGBB"
        - Functional: "rgb(255,0,0)", "rgba(255,0,0,0.5)", "hsl(120,100%,50%)"

    If ``color`` is already a 4-tuple of floats, it is returned unchanged.
    This makes the function safe to call multiple times on the same config object.
    """
    # If it's already a tuple, assume it's valid and return as-is
    if isinstance(color, tuple):
        if len(color) == 4 and all(isinstance(v, (float, int)) for v in color):
            return color
        else:
            logger.warning("Invalid tuple color %s, falling back to black", color)
            return 0.0, 0.0, 0.0, 1.0

    # Continue with original string-to-tuple logic
    color_str = color.strip() if isinstance(color, str) else str(color)
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


def color_tuple_to_string(color: Tuple[float, float, float, float]) -> str:
    """Convert a (b, g, r, a) float tuple to a hex string."""
    b, g, r, a = color
    if a >= 1.0:
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    else:
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}{int(a*255):02x}"


def qcolor_to_rgba_hex(q_color: QColor) -> str:
    """Helper to consistently return #RRGGBBAA from QColor."""
    argb = q_color.name(QColor.HexArgb)  # Returns #AARRGGBB
    return f"#{argb[3:9]}{argb[1:3]}"  # Returns #RRGGBBAA


def rgba_hex_to_qcolor(hex_str: str) -> QColor:
    """Safely converts a #RRGGBBAA string to a QColor."""
    if not isinstance(hex_str, str) or not hex_str.startswith("#") or len(hex_str) != 9:
        return QColor(hex_str)

    rrggbb = hex_str[1:7]
    aa = hex_str[7:9]
    return QColor(f"#{aa}{rrggbb}")  # Construct as #AARRGGBB for Qt


def normalize_to_hex(color_data) -> str:
    """Converts strings or (B, G, R, A) tuples to #RRGGBBAA."""
    if isinstance(color_data, (tuple, list)):
        b, g, r, a = color_data[0], color_data[1], color_data[2], color_data[3]
        qc = QColor.fromRgbF(r, g, b, a)
    else:
        # Use the parser instead of QColor(color_data)
        qc = rgba_hex_to_qcolor(color_data)
        if isinstance(color_data, str) and len(color_data) <= 7:
            qc.setAlpha(255)

    return qcolor_to_rgba_hex(qc) if qc.isValid() else "#000000ff"
