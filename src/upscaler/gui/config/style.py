from __future__ import annotations

import re
from dataclasses import fields, is_dataclass, replace
from typing import Any, Dict

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

from .config import (
    GUIConfig,
    GUIPalette,
    GUIStyleOverrides,
    DialogLayout,
    ProfileLayout,
    SidebarLayout,
    TileLayout,
)
from .palette import DARK, LIGHT
from ..utils import NON_COLOR_KEYWORDS, scheme_is_light

#: Field names that must NOT be scaled, keyed by dataclass.
_EXEMPT: Dict[type, frozenset[str]] = {
    GUIConfig: frozenset[str](
        {"auto_refresh_ms", "tile_preview_interval_ms", "font_family"}
    ),
    TileLayout: frozenset[str](
        {
            "aspect_ratio",
            "spacing_ratio",
            "pop_scale",
            "pop_duration",
            "columns",
            "title_font_bold",
        }
    ),
    SidebarLayout: frozenset[str]({"icon_columns"}),
    ProfileLayout: frozenset[str]({"saved_icon_size"}),
    DialogLayout: frozenset[str](
        {"input_padding", "button_padding", "list_item_padding", "info_max_lines"}
    ),
}

#: Matches ``Npx`` tokens inside a padding string.
_PADDING_RE = re.compile(r"(\d+)px")


def _apply_style_overrides(cfg: GUIConfig, overrides: GUIStyleOverrides) -> GUIConfig:
    """Return a copy of *cfg* with the user's style overrides applied."""
    return replace(
        cfg,
        palette=overrides.palette,
        tile=replace(
            cfg.tile,
            columns=overrides.tile_columns,
            aspect_ratio=overrides.tile_aspect_ratio,
        ),
        sidebar=replace(
            cfg.sidebar,
            profiles_width=overrides.profiles_width,
            settings_width=overrides.settings_width,
        ),
        font_family=overrides.font_family,
        auto_refresh_ms=overrides.auto_refresh_ms,
        tile_preview_interval_ms=overrides.tile_preview_interval_ms,
    )


def _scale_gui_config(cfg: GUIConfig, zoom_percent: int) -> GUIConfig:
    """Return a copy of *cfg* with dimensional fields scaled by *zoom_percent*."""
    if zoom_percent <= 0:
        raise ValueError(f"Zoom must be positive, got {zoom_percent}")
    return _scale_dataclass(cfg, zoom_percent / 100.0)


def _rescale_padding(value: str, factor: float) -> str:
    """Rescale any ``Npx`` tokens inside *value*; other strings pass through."""
    if "px" not in value:
        return value

    def sub(match: re.Match) -> str:
        return f"{max(1, round(int(match.group(1)) * factor))}px"

    return _PADDING_RE.sub(sub, value)


def _scale_number(value: float, factor: float) -> Any:
    """Scale an int or float, preserving the original type and a 1px floor."""
    scaled = value * factor
    if isinstance(value, int):
        return max(1, round(scaled))
    return scaled


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


def _resolve_auto_background(cfg: GUIConfig) -> GUIConfig:
    """Replace the Auto 'none' background with a concrete session color."""
    if cfg.palette.background.lower() not in NON_COLOR_KEYWORDS:
        return cfg

    is_light = scheme_is_light()

    app = QApplication.instance()
    if app is not None:
        color = app.palette().color(QPalette.ColorRole.Window)
        expected_dark = not is_light
        if (color.lightness() < 128) == expected_dark:
            return replace(
                cfg,
                palette=replace(cfg.palette, background=color.name()),
            )

    fallback = LIGHT.background if is_light else DARK.background
    return replace(cfg, palette=replace(cfg.palette, background=fallback))


def resolve_gui_config(overrides: GUIStyleOverrides) -> GUIConfig:
    """Build the effective GUIConfig from a set of style overrides."""
    base = GUIConfig(palette=overrides.palette)
    with_overrides = _apply_style_overrides(base, overrides)
    scaled = _scale_gui_config(with_overrides, overrides.zoom)
    return _resolve_auto_background(scaled)
