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
                    logger.info(f"Loaded config from {path}")
            except Exception as e:
                logger.warning(f"Failed to load config {path}: {e}")
            break

    return general_options, profiles
