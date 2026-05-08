import logging
import re
from typing import Any, Dict, Optional, Tuple

from . import Config
from .args import apply_overrides
from .yaml import load_yaml_config, save_yaml_config
from ..window import WindowInfo

logger = logging.getLogger(__name__)


def add_or_update_profile(
    name: str,
    match: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None,
) -> str:
    """
    Add or update a named profile in the user’s YAML configuration.

    If the file does not exist, it will be created.  Existing profiles
    under the same name are replaced; other profiles are left untouched.

    Parameters
    ----------
    name : str
        Profile name (case‑sensitive).
    match : dict, optional
        Match criteria to include in the profile (e.g. ``{"title": "Firefox"}``).
    options : dict, optional
        Option overrides to include.
    config_path : str, optional
        Path to the YAML file.  Uses the default XDG location when ``None``.

    Returns
    -------
    str
        The absolute path of the file that was written.
    """
    general, profiles = load_yaml_config(config_path)
    profile = {}
    if match:
        profile["match"] = match
    if options:
        profile["options"] = options
    profiles[name] = profile

    return save_yaml_config(general, profiles, config_path)


def find_profile(profiles: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    """Find a profile by name (case-insensitive)."""
    name_lower = name.lower()
    for profile_name, profile_data in profiles.items():
        if profile_name.lower() == name_lower:
            return profile_data
    return None


def find_matching_profile(
    profiles: Dict[str, Any],
    window_title: str,
    window_class: Optional[str] = None,
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Find the first profile whose match criteria match the window.
    Currently uses only window_title. Later can use window_class.
    Match criteria are evaluated with OR logic: any match qualifies.
    """
    for profile_name, profile_data in profiles.items():
        match_criteria = profile_data.get("match", {})
        if not match_criteria:
            continue

        # Check each criterion; if any matches, return the profile
        for key, value in match_criteria.items():
            if key == "title":
                if window_title.lower() == value.lower():
                    return profile_name, profile_data
                continue
            if key == "title_regex":
                try:
                    pattern = re.compile(value, re.IGNORECASE)
                    if pattern.search(window_title):
                        return profile_name, profile_data
                except re.error:
                    logger.warning(
                        f"Invalid regex in profile '{profile_name}': {value}"
                    )
                continue
            if key == "title_contains":
                if value.lower() in window_title.lower():
                    return profile_name, profile_data
                continue
            if key == "title_startswith":
                if window_title.lower().startswith(value.lower()):
                    return profile_name, profile_data
                continue
            if key == "title_endswith":
                if window_title.lower().endswith(value.lower()):
                    return profile_name, profile_data
                continue

            # Future class-based matches (when window_class is available)
            """
            if window_class and key == "class":
                if window_class.lower() == value.lower():
                    return profile_name, profile_data
                continue
            if window_class and key == "class_regex":
                try:
                    pattern = re.compile(value, re.IGNORECASE)
                    if pattern.search(window_class):
                        return profile_name, profile_data
                except re.error:
                    logger.warning(
                        f"Invalid regex in profile '{profile_name}': {value}"
                    )
                continue
            if window_class and key == "class_contains":
                if value.lower() in window_class.lower():
                    return profile_name, profile_data
                continue
            if window_class and key == "class_startswith":
                if window_class.lower().startswith(value.lower()):
                    return profile_name, profile_data
                continue
            if window_class and key == "class_endswith":
                if window_class.lower().endswith(value.lower()):
                    return profile_name, profile_data
                continue
            """

            logger.debug(
                f"Ignoring unknown match key '{key}' in profile '{profile_name}'"
            )

    return None, None


def apply_window_profile(
    config: Config,
    win_info: WindowInfo,
    profiles: Dict[str, Any],
) -> bool:
    """
    Apply the first profile whose ``match`` criteria fits *win_info*.

    This function does nothing if a manual profile was already selected
    (caller must ensure that). It only applies automatic profiles.

    Parameters
    ----------
    config: Config
        The configuration object to modify in place.
    win_info: WindowInfo
        The target window to match against.
    profiles: dict
        Raw profiles dictionary as returned by :func:`load_yaml_config`.

    Returns
    -------
    bool
        ``True`` if a profile was applied, ``False`` otherwise.
    """
    profile_name, profile_data = find_matching_profile(
        profiles, win_info.title, window_class=None
    )
    if profile_data is None:
        return False
    apply_overrides(config, profile_data.get("options", {}))
    logger.info(
        "Auto-applied profile '%s' for window '%s'", profile_name, win_info.title
    )
    return True
