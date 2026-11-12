from __future__ import annotations

import logging
from dataclasses import fields
from typing import Any, Dict, Optional, Tuple

from .config import GUIPalette, GUIStyleOverrides
from .palette import PRESETS, find_matching_preset
from ...config import default_config_path, load_yaml_config, save_yaml_config

logger = logging.getLogger(__name__)

_OVERRIDE_BOUNDS: Dict[str, Tuple[float, float]] = {
    "zoom": (50, 250),
    "font_scale": (80, 150),
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
    Numeric values that have an entry in :data:`_OVERRIDE_BOUNDS` are
    clamped; numeric fields without bounds pass through unclamped.
    Bool fields accept true/false plus common YAML string aliases.
    The function never raises: an unreadable file yields the defaults.
    """
    defaults = GUIStyleOverrides(palette=PRESETS["Auto"])
    path = config_path or default_config_path("gui-config.yaml")

    try:
        general, _ = load_yaml_config(config_path=path)
    except Exception:
        logger.warning("Failed to load GUI style, using defaults", exc_info=True)
        return defaults

    kwargs: Dict[str, Any] = {}
    for f in fields(GUIStyleOverrides):
        if f.name == "palette":
            kwargs["palette"] = _resolve_palette(general, defaults.palette)
        else:
            kwargs[f.name] = _load_field(
                f.name, general.get(f.name), getattr(defaults, f.name)
            )
    return GUIStyleOverrides(**kwargs)


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


def _load_field(name: str, raw: Any, default: Any) -> Any:
    """
    Coerce *raw* to the type of *default*.

    Numeric fields with an entry in :data:`_OVERRIDE_BOUNDS` are clamped to
    that range; unbounded numerics are accepted as-is. Returns *default*
    when *raw* is missing or cannot be converted.
    """
    if raw is None:
        return default

    if isinstance(default, bool):
        return _load_bool(raw, default)

    bounds = _OVERRIDE_BOUNDS.get(name)

    if isinstance(default, int):
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return default
        if bounds:
            value = max(int(bounds[0]), min(int(bounds[1]), value))
        return value

    if isinstance(default, float):
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return default
        if bounds:
            value = max(float(bounds[0]), min(float(bounds[1]), value))
        return value

    if isinstance(default, str):
        return str(raw)

    return default


def _load_bool(raw: Any, default: bool) -> bool:
    """Coerce *raw* to bool, accepting YAML truthy/falsy string aliases."""
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        lowered = raw.strip().lower()
        if lowered in ("true", "yes", "on", "1"):
            return True
        if lowered in ("false", "no", "off", "0"):
            return False
        return default
    if isinstance(raw, int):
        return bool(raw)
    return default


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
