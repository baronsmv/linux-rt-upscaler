from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple, Union

from .config import GUIPalette
from .presets import PRESETS
from ...config import default_config_path, load_yaml_config, save_yaml_config

logger = logging.getLogger(__name__)

_ZOOM_MIN = 50
_ZOOM_MAX = 400


def load_gui_style(config_path: Optional[str] = None) -> Tuple[GUIPalette, int]:
    """Load a GUI palette, using a preset if stored."""
    config_path = config_path or default_config_path("gui-config.yaml")

    try:
        general, _ = load_yaml_config(config_path=config_path)
        zoom = max(_ZOOM_MIN, min(_ZOOM_MAX, int(general.get("zoom", 100))))

        # Prefer a named preset
        preset_name: Optional[str] = general.get("palette_preset")
        if preset_name and preset_name in PRESETS:
            return PRESETS[preset_name], zoom

        # Fallback to the full palette snapshot
        full_palette: Optional[Dict] = general.get("palette")
        if full_palette:
            return GUIPalette(**full_palette), zoom

    except Exception:
        logger.warning("Failed to load GUI style, using defaults", exc_info=True)

    return PRESETS["Auto"], 100


def save_gui_style(
    palette: Dict[str, str],
    preset: Optional[str] = None,
    zoom: int = 100,
    config_path: Optional[str] = None,
) -> None:
    """Save the GUI style to YAML. If *preset* is given, also store its name."""
    data: Dict[str, Union[str, int, Dict[str, str]]] = {"palette": palette}
    if preset:
        data["palette_preset"] = preset
    if zoom != 100:
        data["zoom"] = int(zoom)

    config_path = config_path or default_config_path("gui-config.yaml")
    save_yaml_config(data, config_path=config_path)
