import argparse
import logging
import os
from enum import Enum
from importlib.metadata import version, PackageNotFoundError
from typing import Any, List, Optional, Self, Dict

import yaml

from . import validators

logger = logging.getLogger(__name__)


class OverlayMode(str, Enum):
    """Overlay window behavior modes."""

    ALWAYS_ON_TOP = "always-on-top"
    ALWAYS_ON_TOP_TRANSPARENT = "top-transparent"
    FULLSCREEN = "fullscreen"
    WINDOWED = "windowed"


DEFAULTS: Dict[str, Any] = {
    # General
    "program": None,
    "select": False,
    # Overlay
    "overlay_mode": OverlayMode.ALWAYS_ON_TOP.value,
    # Display
    "monitor": "primary",
    # Upscaling
    "model": "fast",
    "double_upscale": False,
    # Output geometry
    "output_geometry": "fit",
    "crop_top": 0,
    "crop_bottom": 0,
    "crop_left": 0,
    "crop_right": 0,
    "offset_x": 0,
    "offset_y": 0,
    "background_color": "black",
    # Window detection
    "target_delay": 5,
    "pid_timeout": 5,
    "class_timeout": 5,
    "total_timeout": 60,
    "starting_phase": 1,
    # Logging (these are set via flags, not directly from CLI)
    "log_level": "WARNING",
    "log_file": None,
    # Config file
    "config_file": None,
}


def get_version() -> str:
    """Return the package version, with a fallback for development."""
    try:
        return version("linux-rt-upscaler")
    except PackageNotFoundError:
        try:
            from . import __version__

            return __version__
        except ImportError:
            return "unknown (development mode)"


class Config:
    """
    Configuration container that loads defaults, then a YAML file,
    then overrides with command‑line arguments.
    """

    def __init__(self, **kwargs) -> None:
        # Initialize with defaults, then override with any provided kwargs
        for key, value in DEFAULTS.items():
            setattr(self, key, kwargs.get(key, value))
        logger.debug("Config object created with default values")

    @classmethod
    def from_cli(cls) -> Self:
        """Parse command line and config files, returning a fully populated Config."""
        parser = argparse.ArgumentParser(
            description="Real‑Time Upscaler for Linux",
            epilog="See source code for details: https://github.com/baronsmv/linux-rt-upscaler",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser._positionals.title = "POSITIONAL ARGUMENTS"
        parser._optionals.title = "GENERAL OPTIONS"
        parser.add_argument(
            "-v", "--version", action="version", version=f"%(prog)s {get_version()}"
        )
        parser.add_argument(
            "-c",
            "--config",
            help="Path to config file (YAML)",
        )

        # Program argument
        parser.add_argument("program", nargs="*", help="Program to launch and scale")

        # General section
        general_group = parser.add_argument_group("INTERACTION OPTIONS")
        general_group.add_argument(
            "-s",
            "--select",
            action="store_true",
            help="Select a window from the list of open windows",
        )

        # Upscaling section
        upscaling_group = parser.add_argument_group("UPSCALING OPTIONS")
        upscaling_group.add_argument(
            "-m",
            "--model",
            choices=(
                "8x32",
                "4x32",
                "4x24",
                "4x16",
                "4x12",
                "3x12",
                "fast",
                "faster",
                "veryfast",
            ),
            default=DEFAULTS["model"],
            help="Upscaling model to use (ordered from best to worst quality)\n"
            f"Default: {DEFAULTS['model']}",
        )
        upscaling_group.add_argument(
            "-2",
            "--double-upscale",
            action="store_true",
            help="EXPERIMENTAL: Perform two 2x passes (total 4x) for higher\n"
            "resolution screens (4k, 1440p) or low‑resolution sources",
        )

        # Display section
        display_group = parser.add_argument_group("DISPLAY OPTIONS")
        display_group.add_argument(
            "--monitor",
            type=str,
            default=DEFAULTS["monitor"],
            help=f"""Monitor to cover: 'primary', 'all' (to cover all
multi-monitor space), or monitor name/index
(e.g., 'HDMI-1', 0).
Default: {DEFAULTS['monitor']}.""",
        )

        # Overlay options
        overlay_group = parser.add_argument_group("OVERLAY OPTIONS")
        overlay_group.add_argument(
            "-o",
            "--output-geometry",
            default=DEFAULTS["output_geometry"],
            help=f"""Specify the output window size and scaling behaviour.
Default: {DEFAULTS["output_geometry"]}

Examples:
  fit          - Fit to full monitor/window (letterbox)
  stretch      - Stretch to full monitor/window (aspect
                 ratio not preserved)
  cover        - Cover full monitor/window

  1920x1080    - Fit content to 1920x1080
  1920x1080!   - Stretch content to 1920x1080
  1920x1080^   - Cover 1920x1080 (crop)

  50%%          - 50%% of monitor, content fitted
  50%%!         - 50%% of monitor, content stretched

  1920x        - Fixed width 1920, height proportional
                 (fit)
  1920x!       - Fixed width 1920, height proportional
                 (stretch)

  x1080        - Fixed height 1080, width proportional
                 (fit)
  x1080!       - Fixed height 1080, width proportional
                 (stretch)

""",
        )
        overlay_group.add_argument(
            "--overlay-mode",
            choices=[e.value for e in OverlayMode],
            default=DEFAULTS["overlay_mode"],
            help=f"""Overlay window behaviour.
Default: {DEFAULTS["overlay_mode"]}

Note: Keyboard events are NOT forwarded, so it's best to
keep the target window focused (if on a single monitor,
always-on-top works well for this).

Modes:
  always-on-top    - Floating overlay above all windows
                     and not focusable (bypasses WM).
  top-transparent  - Same as above but click‑through
                     (mouse passes to window below).
  fullscreen       - Fullscreen window without decorations
                     (covers entire monitor).
  windowed         - Normal window with decorations, fixed
                     size.

""",
        )
        overlay_group.add_argument(
            "--crop-top",
            type=int,
            default=DEFAULTS["crop_top"],
            help="Pixels to crop from top border of the target window",
        )
        overlay_group.add_argument(
            "--crop-bottom",
            type=int,
            default=DEFAULTS["crop_bottom"],
            help="Pixels to crop from bottom border of the target window",
        )
        overlay_group.add_argument(
            "--crop-left",
            type=int,
            default=DEFAULTS["crop_left"],
            help="Pixels to crop from left border of the target window",
        )
        overlay_group.add_argument(
            "--crop-right",
            type=int,
            default=DEFAULTS["crop_right"],
            help="Pixels to crop from right border of the target window",
        )
        overlay_group.add_argument(
            "--offset-x",
            type=int,
            default=DEFAULTS["offset_x"],
            help="""Horizontal offset from centered position (pixels, positive
moves right, negative moves left)

Note: To pass negative values, use either --offset-x=-1
(with an equals sign) or --offset-x "-1" (with quotes).
The form --offset-x -1 will be misinterpreted because the
shell treats -1 as a separate option.

""",
        )
        overlay_group.add_argument(
            "--offset-y",
            type=int,
            default=DEFAULTS["offset_y"],
            help="""Vertical offset from centered position (pixels, positive
moves down, negative moves up)

Note: Same as above.

""",
        )
        overlay_group.add_argument(
            "--background-color",
            default=DEFAULTS["background_color"],
            help=f"""Color for letterbox bars.
Can be a CSS color name (e.g., 'black', 'red') or a hex
code (e.g., '#000000', '#FF0000')
Default: {DEFAULTS['background_color']}""",
        )

        # Timeout / window detection section
        timeout_group = parser.add_argument_group("WINDOW DETECTION OPTIONS")
        timeout_group.add_argument(
            "--target-delay",
            type=int,
            default=DEFAULTS["target_delay"],
            help="Seconds to wait before capturing active window",
        )
        timeout_group.add_argument(
            "--pid-timeout",
            type=int,
            default=DEFAULTS["pid_timeout"],
            help="Seconds to try PID‑based window detection",
        )
        timeout_group.add_argument(
            "--class-timeout",
            type=int,
            default=DEFAULTS["class_timeout"],
            help="Seconds to try class‑based window detection",
        )
        timeout_group.add_argument(
            "--total-timeout",
            type=int,
            default=DEFAULTS["total_timeout"],
            help="Total seconds before giving up",
        )
        timeout_group.add_argument(
            "--starting-phase",
            type=int,
            choices=[1, 2],
            default=DEFAULTS["starting_phase"],
            help="Start with phase 1 (PID) or 2 (class)",
        )

        # Logging section
        log_group = parser.add_argument_group("LOGGING OPTIONS")
        log_group.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Decrease log verbosity (ERROR level)",
        )
        log_group.add_argument(
            "--debug",
            action="store_true",
            help="Increase log verbosity (DEBUG level)",
        )
        log_group.add_argument(
            "--log-file",
            help="Write logs to this file (parent directories are created)",
        )

        args = parser.parse_args()

        config = cls()

        # Load config file if specified or default
        config._load_config_file(args.config)

        # Override with CLI arguments
        config._apply_args(args)

        # Log level and file
        if args.debug:
            config.log_level = "DEBUG"
        elif args.quiet:
            config.log_level = "ERROR"
        if args.log_file:
            config.log_file = args.log_file

        # Validation
        validators.output_geometry(config.output_geometry)
        validators.background_color(config.background_color)

        return config

    def _load_config_file(self, custom_path: Optional[str] = None) -> None:
        """
        Load settings from a YAML file.
        If custom_path is given, try that path; otherwise search default locations.
        Only the first found file is loaded.
        """
        paths: List[str] = []
        if custom_path:
            paths.append(custom_path)
        else:
            # Default: ~/.config/linux-rt-upscaler/config.yaml
            xdg_config = os.environ.get(
                "XDG_CONFIG_HOME", os.path.expanduser("~/.config")
            )
            default_path = os.path.join(xdg_config, "linux-rt-upscaler", "config.yaml")
            paths.append(default_path)
            # Also check current directory for convenience
            paths.append("./config.yaml")

        for path in paths:
            if os.path.isfile(path):
                try:
                    with open(path, "r") as f:
                        data = yaml.safe_load(f)
                        if data:
                            self._update_from_dict(data)
                    logger.info(f"Loaded config from {path}")
                except Exception as e:
                    logger.warning(f"Failed to load config {path}: {e}")
                break  # use first found

    def _update_from_dict(self, data: dict[str, Any]) -> None:
        """Update config attributes from a dictionary (YAML contents)."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Config set from file: {key} = {value!r}")
            else:
                logger.debug(f"Ignoring unknown config key: {key}")

    def _apply_args(self, args: argparse.Namespace) -> None:
        """Override config with command‑line arguments."""
        for arg in DEFAULTS.keys():
            arg_value = getattr(args, arg, None)
            if arg_value is not None:
                default_val = DEFAULTS.get(arg)
                if arg_value != default_val:
                    setattr(self, arg, arg_value)
                    logger.debug(f"CLI set {arg} = {arg_value!r}")
