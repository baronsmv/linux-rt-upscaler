from __future__ import annotations

import logging
from dataclasses import fields
from typing import Any, Dict, Optional, Tuple

from .config import GUIPalette, GUIStyleOverrides
from .palette import PRESETS, find_matching_preset
from ...config import default_config_path, load_yaml_config, save_yaml_config

logger = logging.getLogger(__name__)

_OVERRIDE_BOUNDS: Dict[str, Tuple[float, float]] = {
    "zoom": (50, 400),
    "profiles_width": (240, 800),
    "settings_width": (240, 800),
    "tile_columns": (1, 8),
    "tile_aspect_ratio": (0.5, 3.0),
    "auto_refresh_ms": (250, 30_000),
    "tile_preview_interval_ms": (16, 1000),
}


def load_gui_style(
    config_path: Optional[str] = None,
) -> GUIStyleOverrides:
    """
    Read the GUI style from YAML into a :class:`GUIStyleOverrides`.

    Missing or malformed values fall back to the dataclass defaults.
    Numeric values are clamped to :data:`_OVERRIDE_BOUNDS` so a
    hand-edited file cannot produce an unusable layout. The function
    never raises: an unreadable file yields the defaults.
    """
    defaults = GUIStyleOverrides(palette=PRESETS["Auto"])
    path = config_path or default_config_path("gui-config.yaml")

    try:
        general, _ = load_yaml_config(config_path=path)
    except Exception:
        logger.warning("Failed to load GUI style, using defaults", exc_info=True)
        return defaults

    return GUIStyleOverrides(
        palette=_resolve_palette(general, defaults.palette),
        zoom=_load_numeric("zoom", general.get("zoom"), defaults.zoom),
        font_family=str(general.get("font_family") or defaults.font_family),
        profiles_width=_load_numeric(
            "profiles_width", general.get("profiles_width"), defaults.profiles_width
        ),
        settings_width=_load_numeric(
            "settings_width", general.get("settings_width"), defaults.settings_width
        ),
        tile_columns=_load_numeric(
            "tile_columns", general.get("tile_columns"), defaults.tile_columns
        ),
        tile_aspect_ratio=_load_numeric(
            "tile_aspect_ratio",
            general.get("tile_aspect_ratio"),
            defaults.tile_aspect_ratio,
        ),
        auto_refresh_ms=_load_numeric(
            "auto_refresh_ms", general.get("auto_refresh_ms"), defaults.auto_refresh_ms
        ),
        tile_preview_interval_ms=_load_numeric(
            "tile_preview_interval_ms",
            general.get("tile_preview_interval_ms"),
            defaults.tile_preview_interval_ms,
        ),
    )


def save_gui_style(
    overrides: GUIStyleOverrides,
    config_path: Optional[str] = None,
) -> None:
    """
    Persist the GUI style to YAML, writing only non-default values.

    The full palette is always written so the file remains self-contained
    even if it is later moved to a machine where presets differ. Every
    other field is omitted when it matches its dataclass default, keeping
    the file compact for users who never touch the advanced controls.
    """
    defaults = GUIStyleOverrides(palette=overrides.palette)

    data: Dict[str, Any] = {
        "palette": {
            f.name: getattr(overrides.palette, f.name) for f in fields(GUIPalette)
        }
    }

    preset = find_matching_preset(overrides.palette)
    if preset and preset in PRESETS:
        data["palette_preset"] = preset

    for f in fields(GUIStyleOverrides):
        if f.name == "palette":
            continue
        value = getattr(overrides, f.name)
        if value != getattr(defaults, f.name):
            data[f.name] = value

    path = config_path or default_config_path("gui-config.yaml")
    save_yaml_config(data, config_path=path)


def _resolve_palette(general: Dict[str, Any], fallback: GUIPalette) -> GUIPalette:
    """
    Return the palette described by *general*, falling back to *fallback*.

    A named preset takes precedence over an inline palette snapshot; if
    both are present, the preset wins because it is more likely to be
    what the user last selected.
    """
    preset_name = general.get("palette_preset")
    if preset_name and preset_name in PRESETS:
        return PRESETS[preset_name]

    raw = general.get("palette")
    if isinstance(raw, dict):
        try:
            return GUIPalette(**raw)
        except TypeError:
            logger.warning("Malformed palette in gui-config.yaml, using fallback")

    return fallback


def _load_numeric(name: str, raw: Any, default: Any) -> Any:
    """
    Convert *raw* to the type of *default* and clamp to the field bounds.

    Returns *default* on any conversion failure. The bounds must be
    declared in :data:`_OVERRIDE_BOUNDS` for the field; a field without
    bounds is returned unchanged.
    """
    bounds = _OVERRIDE_BOUNDS.get(name)
    if bounds is None:
        return default
    lo, hi = bounds

    try:
        if isinstance(default, bool):
            return default
        if isinstance(default, int):
            return max(int(lo), min(int(hi), int(raw)))
        if isinstance(default, float):
            return max(float(lo), min(float(hi), float(raw)))
    except (TypeError, ValueError):
        return default
    return default
