import logging
import re
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


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
