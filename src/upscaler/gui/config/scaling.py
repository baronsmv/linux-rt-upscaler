from __future__ import annotations

import re
from dataclasses import fields, is_dataclass, replace
from typing import Any, Dict

from .config import (
    GUIConfig,
    GUIPalette,
    DialogLayout,
    ProfileLayout,
    SidebarLayout,
    TileLayout,
)

#: Field names that must NOT be scaled, keyed by dataclass.
_EXEMPT: Dict[type, frozenset] = {
    GUIConfig: frozenset(
        {
            "auto_refresh_ms",  # timing
            "tile_preview_interval_ms",  # timing
        }
    ),
    TileLayout: frozenset(
        {
            "aspect_ratio",  # unitless multiplier
            "spacing_ratio",  # unitless multiplier
            "pop_scale",  # unitless multiplier
            "pop_duration",  # milliseconds
            "columns",  # count
            "title_font_family",
            "title_font_bold",
        }
    ),
    SidebarLayout: frozenset({"icon_columns"}),  # count
    ProfileLayout: frozenset({"saved_icon_size"}),  # runtime capture size
    DialogLayout: frozenset(
        {
            # String paddings handled separately, see _rescale_padding.
            "input_padding",
            "button_padding",
            "list_item_padding",
            "info_max_lines",
        }
    ),
}

#: Matches ``Npx`` tokens inside a padding string.
_PADDING_RE = re.compile(r"(\d+)px")


def scale_gui_config(cfg: GUIConfig, zoom_percent: int) -> GUIConfig:
    """
    Return a copy of *cfg* with dimensional fields scaled by *zoom_percent*.

    ``zoom_percent`` is the user-facing percentage, e.g. ``100`` for 1×,
    ``150`` for 1.5×.
    """
    if zoom_percent <= 0:
        raise ValueError(f"Zoom must be positive, got {zoom_percent}")
    return _scale_dataclass(cfg, zoom_percent / 100.0)


def _scale_dataclass(obj: Any, factor: float) -> Any:
    """Recursively scale a frozen dataclass instance."""
    if not is_dataclass(obj):
        return obj

    exempt = _EXEMPT.get(type(obj), frozenset())
    updates: Dict[str, Any] = {}

    for f in fields(obj):
        name = f.name
        if name in exempt:
            continue

        value = getattr(obj, name)

        if isinstance(value, GUIPalette):
            continue  # palette is zoom-invariant
        if is_dataclass(value) and not isinstance(value, type):
            updates[name] = _scale_dataclass(value, factor)
        elif isinstance(value, str):
            updates[name] = _rescale_padding(value, factor)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            updates[name] = _scale_number(value, factor)

    return replace(obj, **updates)


def _scale_number(value: float, factor: float) -> Any:
    """Scale an int or float, preserving the original type and a 1px floor."""
    scaled = value * factor
    if isinstance(value, int):
        return max(1, round(scaled))
    return scaled


def _rescale_padding(value: str, factor: float) -> str:
    """Rescale any ``Npx`` tokens inside *value*; other strings pass through."""
    if "px" not in value:
        return value

    def sub(match: re.Match) -> str:
        return f"{max(1, round(int(match.group(1)) * factor))}px"

    return _PADDING_RE.sub(sub, value)
