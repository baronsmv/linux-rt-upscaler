import logging
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
        - Hex: "#RGB", "#RRGGBB", "#RRGGBBAA"
        - Functional: "rgb(255,0,0)", "rgba(255,0,0,0.5)", "hsl(120,100%,50%)"

    If the string is invalid, falls back to black.
    """
    qcolor = QColor(color_str)

    # Return BGRA order to match shader expectations
    result = (qcolor.blueF(), qcolor.greenF(), qcolor.redF(), qcolor.alphaF())
    logger.debug(f"Parsed color '{color_str}' -> BGRA: {result}")
    return result


def parse_config(config: Config):
    config.background_color = _color_string_to_float4(config.background_color)
