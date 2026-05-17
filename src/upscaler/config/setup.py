from __future__ import annotations

import copy
import logging
import sys
from subprocess import Popen
from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

from .args import apply_overrides, parse_args
from .logging import setup_logging
from .models import Config, DEFAULT_CONFIG
from .parsers import parse_config
from .profiles import find_profile, apply_window_profile
from .validators import validate_config, validate_overrides
from .yaml import load_yaml_config

if TYPE_CHECKING:
    from ..window import WindowInfo

logger = logging.getLogger(__name__)


def load_config(
    *,
    profile_name: Optional[str] = None,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Tuple[Config, Dict[str, Any]]:
    """
    Load and validate configuration from YAML file, profile, and CLI overrides.

    Parameters
    ----------
    profile_name : str or None
        Explicit profile name to apply (equivalent to ``--profile``).
    config_path : str or None
        Path to a YAML configuration file (equivalent to ``--config``).
    overrides : dict or None
        Additional key/value overrides (as produced by :func:`~config.args.parse_args`).

    Returns
    -------
    tuple[Config, dict]
        * The merged and validated :class:`Config` object.
        * The raw profiles dictionary from the YAML file (empty if no file loaded).
          This is intended for later automatic profile matching once the target
          window is known.

    Raises
    ------
    SystemExit
        If validation fails (via ``validators`` module).
    """
    # Start from the default configuration
    config = DEFAULT_CONFIG

    # 1. Apply CLI overrides first (so they influence YAML/profile loading)
    if overrides:
        apply_overrides(config, overrides)

    # 2. YAML
    yaml_options, profiles = load_yaml_config(config_path)
    apply_overrides(config, yaml_options)

    # 3. Manual profile
    if profile_name:
        profile = find_profile(profiles, profile_name)
        if profile:
            apply_overrides(config, profile.get("options", {}))
            logger.info("Applied manual profile '%s'", profile_name)
        else:
            logger.warning("Profile '%s' not found, ignoring.", profile_name)

    # 4. CLI overrides take final precedence
    if overrides:
        apply_overrides(config, overrides)

    # 5. Set up logging with the final values
    setup_logging(config.log_level, config.log_file)

    # 6. Validate and parse
    validate_config(config)
    parse_config(config)

    return config, profiles


def finalize_config(
    config: Config,
    win_info: Optional[WindowInfo] = None,
    profiles: Optional[Dict[str, Any]] = None,
    profile_name: Optional[str] = None,
    extra_overrides: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Apply window-matching profile, extra overrides, and then finalize the
    config object (parse colors, set up logging, validate).

    Parameters
    ----------
    config : Config
        The configuration to modify in place.
    win_info : WindowInfo or None
        The target window; required if *profiles* is given and no
        *profile_name* was set.
    profiles : dict or None
        Raw profiles dictionary (from `load_yaml_config`).
    profile_name : str or None
        If set, window-matching is skipped (a manual profile was already in use).
    extra_overrides : dict or None
        Additional overrides to apply **after** the auto profile (e.g.
        GUI-user modifications).
    """
    # Auto-profile if no manual profile was given
    if profiles and not profile_name and win_info is not None:
        apply_window_profile(config, win_info, profiles)

    # Apply extra overrides (these win over everything)
    if extra_overrides:
        apply_overrides(config, extra_overrides)

    # Reparse string colors
    parse_config(config)

    # Ensure logging matches the final log_level / log_file
    setup_logging(config.log_level, config.log_file)

    # Final validation
    validate_config(config)


def setup_config() -> (
    Tuple[Config, Config, Dict[str, Any], Optional[WindowInfo], Optional[Popen]]
):
    """
    Load configuration, acquire target window, apply automatic profile, and
    return:
        - final config (after profile + extra overrides)
        - base config (before any window-specific profile was applied)
        - raw profiles dict
        - WindowInfo
        - optionally the launched process handle
    """
    from ..window import acquire_target_window

    # Parse the command line
    overrides, profile_name, config_path = parse_args()
    validate_overrides(overrides)

    # Build the full configuration (YAML, profile, overrides)
    config, profiles = load_config(
        profile_name=profile_name,
        config_path=config_path,
        overrides=overrides,
    )

    # Save a deepcopy of the config *before* we apply the auto-profile
    base_config = copy.deepcopy(config)

    # Acquire the target window
    win_info, proc = acquire_target_window(config)
    if win_info is None and not config.daemon:
        if not config.select:
            logger.error("No window was found, exiting.")
            sys.exit(0)
        sys.exit(1)

    # Post-window merging and finalization (this applies the auto-profile)
    finalize_config(
        config,
        win_info=win_info,
        profiles=profiles,
        profile_name=profile_name,
        extra_overrides=overrides,
    )

    # Log summary
    if win_info is not None:
        logger.info(
            'Upscaling "%s" (%d%s%d)',
            win_info.title,
            win_info.width,
            chr(215),
            win_info.height,
        )
        logger.debug("Window handle: 0x%x", win_info.handle)
    else:
        logger.info("Daemon mode – waiting for a matching window.")

    return config, base_config, profiles, win_info, proc
