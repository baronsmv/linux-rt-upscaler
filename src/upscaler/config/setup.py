import logging
import sys
from subprocess import Popen
from typing import Any, Dict, Optional, Tuple

from .args import DEFAULT_CONFIG, apply_overrides, parse_args
from .logging import setup_logging
from .models import Config
from .parsers import parse_config
from .profiles import find_profile, apply_window_profile
from .validators import validate_config, validate_overrides
from .yaml import load_yaml_config
from ..window import acquire_target_window, WindowInfo

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


def setup_config() -> Tuple[Config, WindowInfo, Popen]:
    """
    Load configuration, acquire target window, apply automatic profile, and
    return the resulting ``Config``, ``WindowInfo``, and optionally the
    launched process handle.
    """
    # 1. Parse the command line
    overrides, profile_name, config_path = parse_args()
    validate_overrides(overrides)

    # 2. Build the full configuration (YAML, profile, overrides)
    config, profiles = load_config(
        profile_name=profile_name,
        config_path=config_path,
        overrides=overrides,
    )

    # 3. Acquire the target window
    win_info, proc = acquire_target_window(config)
    if win_info is None:
        sys.exit(0 if config.select else 1)

    # 4. Apply automatic window‑matching profile if no manual profile was given
    if not profile_name:
        apply_window_profile(config, win_info, profiles)

    # 5. Re‑apply CLI overrides to guarantee they trump the auto‑profile
    apply_overrides(config, overrides)

    # 6. Parse any config value remaining (color string → tuple, etc.)
    parse_config(config)

    # 7.  Ensure logging matches the final, possibly overridden, log settings
    setup_logging(config.log_level, config.log_file)

    # 8. Final validation
    validate_config(config)

    # Log summary
    logger.info(
        'Upscaling "%s" (%d×%d)',
        win_info.title,
        win_info.width,
        win_info.height,
    )
    logger.debug("Window handle: 0x%x", win_info.handle)

    return config, win_info, proc
