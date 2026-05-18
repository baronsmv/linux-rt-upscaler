import logging
import os
import shutil
from typing import Optional, Tuple, Dict, Any

import yaml

from .parsers import parse_profile_colors

logger = logging.getLogger(__name__)

DEFAULT_MAX_BACKUPS = 5


def load_yaml_config(
    custom_path: Optional[str] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load a single YAML config file and return (general_options, profiles).

    If *custom_path* is None, the default XDG location is used.
    All errors are caught and logged; on failure empty dicts are returned.

    Returns
    -------
    tuple[dict, dict]
        The first dict contains the top-level key/value pairs (excluding
        'profiles'), the second dict contains the named profiles.
    """
    if custom_path:
        path = custom_path
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")

    general_options: Dict[str, Any] = {}
    profiles: Dict[str, Any] = {}

    if not os.path.isfile(path):
        logger.debug("No config file found at '%s'", path)
        return general_options, profiles

    data = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        # Race condition between isfile and open: just return empty
        return general_options, profiles
    except PermissionError as e:
        logger.warning("Permission denied reading '%s': %s", path, e)
        return general_options, profiles
    except yaml.YAMLError as e:
        logger.warning("YAML syntax error in '%s': %s", path, e)
        return general_options, profiles
    except RecursionError:
        logger.warning(
            "YAML recursion depth exceeded in %s. "
            "The file may contain circular references or be overly deep, ignoring it",
            path,
        )
        return general_options, profiles
    except Exception as e:
        logger.warning("Failed to load config '%s': %s", path, e)
        return general_options, profiles

    if data is None:
        logger.debug("Config file %s was empty", path)
        return general_options, profiles

    if not isinstance(data, dict):
        logger.warning(
            "Config file %s is not a mapping (type %s), ignoring it",
            path,
            type(data).__name__,
        )
        return general_options, profiles

    # Separate profiles from general options
    profiles = data.pop("profiles", {})
    general_options = data

    logger.debug("Loaded config from '%s'", path)
    return general_options, profiles


def save_yaml_config(
    general_options: dict,
    profiles: Dict,
    config_path: Optional[str] = None,
    max_backups: int = DEFAULT_MAX_BACKUPS,
) -> str:
    """
    Write general options and profiles to a YAML file, with backup rotation.

    Parameters
    ----------
    general_options : dict
        Top-level configuration keys (excluding 'profiles').
    profiles : dict
        Profile definitions.
    config_path : str or None
        Target file path.  Uses the default XDG location if None.
    max_backups : int
        Number of .bak files to keep (default 5).  Set to 0 to disable.

    Returns
    -------
    str
        The absolute path that was written.

    Notes
    -----
    Before overwriting *config_path*, existing backups are rotated:
    ``config.yaml`` -> ``config.yaml.bak1``,
    ``config.yaml.bak1`` -> ``config.yaml.bak2``, etc.
    The oldest backup is deleted.
    """
    # Build the output data
    data = dict(general_options) if general_options else {}
    if profiles:
        data["profiles"] = parse_profile_colors(profiles)

    # Determine the target path
    if config_path is None:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        config_path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")

    # Ensure the parent directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    # ---- Backup rotation ----
    if max_backups > 0 and os.path.isfile(config_path):
        # Delete the oldest backup first
        oldest = f"{config_path}.bak{max_backups}"
        if os.path.isfile(oldest):
            try:
                os.remove(oldest)
            except OSError as e:
                logger.debug("Could not remove oldest backup '%s': %s", oldest, e)

        # Shift existing backups
        for i in range(max_backups - 1, 0, -1):
            src = f"{config_path}.bak{i}" if i > 1 else config_path
            dst = f"{config_path}.bak{i+1}"
            if os.path.isfile(src):
                try:
                    shutil.move(src, dst)
                except OSError as e:
                    logger.debug(
                        "Backup rotation failed at '%s' -> '%s': %s", src, dst, e
                    )

    # ---- Write the new file ----
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False
            )
    except OSError as e:
        logger.error("Failed to write config to '%s': %s", config_path, e)
        raise

    logger.debug("Configuration saved to '%s'", config_path)
    return config_path
