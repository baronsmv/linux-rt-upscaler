import logging
import os
from typing import Optional, Tuple, Dict, Any

import yaml

logger = logging.getLogger(__name__)


def load_yaml_config(
    custom_path: Optional[str] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load a YAML config file from the given path or default locations.
    Returns (general_options, profiles).
    """
    paths = []
    if custom_path:
        paths.append(custom_path)
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        default_path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")
        paths.append(default_path)
        # paths.append("./config.yaml")

    general_options = {}
    profiles = {}

    for path in paths:
        if os.path.isfile(path):
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                    if data:
                        general_options.update(data)
                        profiles = data.pop("profiles", {})
                        general_options = data
                    logger.debug(f"Loaded config from {path}")
            except Exception as e:
                logger.warning(f"Failed to load config {path}: {e}")
            break

    return general_options, profiles


def save_yaml_config(
    general_options: dict,
    profiles: dict,
    config_path: Optional[str] = None,
) -> str:
    """
    Write general options and profiles to a YAML file.

    If *config_path* is `None`, the default XDG location is used.
    The parent directory is created if it does not exist.

    Returns the absolute path that was written.
    """
    data = dict(general_options) if general_options else {}
    if profiles:
        data["profiles"] = profiles

    if config_path is None:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        config_path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

    return config_path
