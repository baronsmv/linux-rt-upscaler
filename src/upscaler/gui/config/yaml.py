from __future__ import annotations

from typing import Dict, Optional, Tuple, Union

from .config import GUIPalette
from .presets import PRESETS
from ...config import default_config_path, load_yaml_config, save_yaml_config


def load_gui_style(
    config_path: Optional[str] = None,
) -> Tuple[GUIPalette, float]:
    """Load a GUI palette, using a preset if stored."""
    config_path = config_path or default_config_path("gui-config.yaml")
    try:
        general, _ = load_yaml_config(config_path=config_path)
        # Prefer a named preset
        preset_name: Optional[str] = general.get("palette_preset", "Auto")
        zoom = max(0.5, min(4.0, float(general.get("zoom", 1.0))))
        if preset_name and preset_name in PRESETS:
            return PRESETS[preset_name], zoom
        # Fallback to the full palette
        full_palette: Optional[Dict] = general.get("palette")
        if full_palette:
            return GUIPalette(**full_palette), zoom
    except Exception:
        pass
    return None


def save_gui_style(
    palette: Dict[str, str],
    preset: Optional[str] = None,
    zoom: float = 1.0,
    config_path: Optional[str] = None,
) -> None:
    """Save the GUI style to YAML. If *preset* is given, also store its name."""
    data: Dict[str, Union[str, float, Dict[str, str]]] = {"palette": palette}
    if preset:
        data["palette_preset"] = preset
    if abs(zoom - 1.0) > 1e-6:
        data["zoom"] = round(zoom, 2)
    config_path = config_path or default_config_path("gui-config.yaml")
    save_yaml_config(data, config_path=config_path)
