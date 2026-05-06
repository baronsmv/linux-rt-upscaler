import logging
import sys
from subprocess import Popen
from typing import Tuple

from .args import Config, DEFAULT_CONFIG, apply_overrides, parse_args
from .loader import load_yaml_config
from .logging import setup_logging
from .parsers import parse_config
from .profiles import find_profile, find_matching_profile
from .validators import validate_config, validate_overrides
from ..window import acquire_target_window, WindowInfo

logger = logging.getLogger(__name__)


def setup_config() -> Tuple[Config, WindowInfo, Popen]:
    # CLI options (only provided, not default ones)
    provided_args, profile_name, config_path = parse_args()
    validate_overrides(provided_args)

    # Base config overrid with CLI options
    config = DEFAULT_CONFIG
    setup_logging(config.log_level, config.log_file)
    apply_overrides(config, provided_args)

    # Base config overrid with YAML options
    yaml_options, profiles = load_yaml_config(config_path)
    apply_overrides(config, yaml_options)

    # Config profiling by arg
    manual_profile = None
    if profile_name:
        manual_profile = find_profile(profiles, profile_name)
        if manual_profile:
            apply_overrides(config, manual_profile.get("options", {}))
            logger.info(f"Applied manual profile '{profile_name}'")
        else:
            logger.warning(f"Profile '{profile_name}' not found, ignoring.")

    # Target window acquisition
    win_info, proc = acquire_target_window(config)
    if win_info is None:
        sys.exit(0 if config.select else 1)

    # Config profiling by match
    auto_profile = None
    if not manual_profile:
        profile_name, auto_profile = find_matching_profile(profiles, win_info.title)
        if auto_profile:
            apply_overrides(config, auto_profile.get("options", {}))
            logger.info(f"Auto-applied profile for window '{win_info.title}'")

    # Final configuration and logging
    apply_overrides(config, provided_args)
    validate_config(config)

    if config_path:
        logger.info(f"Configuration found in '{config_path}'.")
    if auto_profile:
        logger.info(f"Match with profile '{profile_name}'")

    logger.info(
        f'Upscaling "{win_info.title}" (%d\u00d7%d)',
        win_info.width,
        win_info.height,
    )
    logger.debug("Window handle: 0x%x", win_info.handle)

    parse_config(config)

    return config, win_info, proc
