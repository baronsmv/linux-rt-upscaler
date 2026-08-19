from dataclasses import fields
from typing import List, Set, Tuple, Union

from PySide6.QtGui import QColor

from ..config import GUIPalette, PRESETS

_NON_COLOR_KEYWORDS: Set[str] = {"", "none", "transparent"}


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


def normalize_to_hex(color_data: Union[str, Tuple, List]) -> str:
    """Converts strings or (B, G, R, A) tuples to #RRGGBBAA."""
    if isinstance(color_data, str) and color_data.lower() in _NON_COLOR_KEYWORDS:
        return color_data
    if isinstance(color_data, (tuple, list)):
        b, g, r, a = color_data[0], color_data[1], color_data[2], color_data[3]
        qc = QColor.fromRgbF(r, g, b, a)
    else:
        # Use the parser instead of QColor(color_data)
        qc = rgba_hex_to_qcolor(color_data)
        if isinstance(color_data, str) and len(color_data) <= 7:
            qc.setAlpha(255)

    return qcolor_to_rgba_hex(qc) if qc.isValid() else "#000000ff"


def _to_stylesheet_color(internal_color: str) -> str:
    """Convert an internal #RRGGBBAA color to a Qt-stylesheet-compatible string."""
    if internal_color.lower() in _NON_COLOR_KEYWORDS:
        return internal_color
    qc = rgba_hex_to_qcolor(internal_color)
    if not qc.isValid():
        return ""
    if qc.alpha() == 255:
        return qc.name(QColor.HexRgb)  # "#RRGGBB"
    else:
        return qc.name(QColor.HexArgb)  # "#AARRGGBB"


def _preset_color_to_internal(stylesheet_color: str) -> str:
    """Convert a stylesheet color (preset or saved YAML) to internal #RRGGBBAA."""
    if stylesheet_color.lower() in _NON_COLOR_KEYWORDS:
        return stylesheet_color
    qc = QColor(stylesheet_color)
    if not qc.isValid():
        return ""
    return qcolor_to_rgba_hex(qc)


def palette_to_internal(pal: GUIPalette) -> GUIPalette:
    """Convert a whole stylesheet palette to internal #RRGGBBAA format."""
    return GUIPalette(
        **{
            f.name: _preset_color_to_internal(getattr(pal, f.name))
            for f in fields(GUIPalette)
        }
    )


def palette_to_stylesheet(palette: GUIPalette) -> GUIPalette:
    """Convert a whole internal palette to stylesheet format."""
    return GUIPalette(
        **{
            f.name: _to_stylesheet_color(getattr(palette, f.name))
            for f in fields(GUIPalette)
        }
    )


def _normalized_color(color: str) -> str:
    """Canonical lowercase hex representation for comparison (#rrggbb or #aarrggbb)."""
    qc = QColor(color)
    if not qc.isValid():
        return color.lower()
    if qc.alpha() == 255:
        return qc.name(QColor.HexRgb).lower()
    else:
        return qc.name(QColor.HexArgb).lower()


def find_matching_preset(palette: GUIPalette) -> str:
    """Compare a stylesheet palette against all built-in presets.
    Returns the preset name if an exact match is found, otherwise 'Custom'.
    """
    for preset_name, preset_palette in PRESETS.items():
        if all(
            _normalized_color(getattr(preset_palette, f.name))
            == _normalized_color(getattr(palette, f.name))
            for f in fields(GUIPalette)
        ):
            return preset_name
    return "Custom"
