import argparse
import logging
from importlib.metadata import version, PackageNotFoundError
from typing import Tuple, Dict, Optional, Any

from .models import Config, OverlayMode

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = Config()


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


def parse_args() -> Tuple[Dict, Optional[str], Optional[str]]:
    """Parse command line arguments and return (args, profile_name, config_path)."""
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
        help="""Path to config file (YAML)
By default, it looks in '~/.config/linux-rt-upscaler/config.yaml',
in the project source and in the current directory""",
    )
    parser.add_argument(
        "-p",
        "--profile",
        help="Name of a profile to explicitly apply from the config file",
    )

    # Program argument
    parser.add_argument("program", nargs="*", help="Program to launch and scale")

    # General section
    interaction_group = parser.add_argument_group("INTERACTION OPTIONS")
    interaction_group.add_argument(
        "-s",
        "--select",
        action="store_true",
        help="Select a window from the list of open windows",
    )
    interaction_group.add_argument(
        "-f",
        "--follow-focus",
        action="store_true",
        help="Follow the currently focused window (automatically switch when focus changes)",
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
        default=DEFAULT_CONFIG.model,
        help="Upscaling model to use (ordered from best to worst quality)\n"
        f"Default: {DEFAULT_CONFIG.model}",
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
        default=DEFAULT_CONFIG.monitor,
        help=f"""Monitor to cover: 'primary', 'all' (to cover all
multi-monitor space), or monitor name/index
(e.g., 'HDMI-1', 0).
Default: {DEFAULT_CONFIG.monitor}""",
    )
    display_group.add_argument(
        "--scale-factor",
        type=float,
        default=DEFAULT_CONFIG.scale_factor,
        help="""Wayland scale factor used (e.g., 2.0 for 200%% scaling).
It's used to calculate physical pixels of the screen""",
    )

    # Overlay options
    overlay_group = parser.add_argument_group("OVERLAY OPTIONS")
    overlay_group.add_argument(
        "-o",
        "--output-geometry",
        default=DEFAULT_CONFIG.output_geometry,
        help=f"""Specify the output window size and scaling behaviour.
Default: {DEFAULT_CONFIG.output_geometry}

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
        default=DEFAULT_CONFIG.overlay_mode,
        help=f"""Overlay window behaviour.
Default: {DEFAULT_CONFIG.overlay_mode}

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
        default=DEFAULT_CONFIG.crop_top,
        help="Pixels to crop from top border of the target window",
    )
    overlay_group.add_argument(
        "--crop-bottom",
        type=int,
        default=DEFAULT_CONFIG.crop_bottom,
        help="Pixels to crop from bottom border of the target window",
    )
    overlay_group.add_argument(
        "--crop-left",
        type=int,
        default=DEFAULT_CONFIG.crop_left,
        help="Pixels to crop from left border of the target window",
    )
    overlay_group.add_argument(
        "--crop-right",
        type=int,
        default=DEFAULT_CONFIG.crop_right,
        help="Pixels to crop from right border of the target window",
    )
    overlay_group.add_argument(
        "--offset-x",
        type=int,
        default=DEFAULT_CONFIG.offset_x,
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
        default=DEFAULT_CONFIG.offset_y,
        help="""Vertical offset from centered position (pixels, positive
moves down, negative moves up)

Note: Same as above.

    """,
    )
    overlay_group.add_argument(
        "--background-color",
        default=DEFAULT_CONFIG.background_color,
        help=f"""Color for letterbox bars.
Can be a CSS color name (e.g., 'black', 'red') or a hex
code (e.g., '#000000', '#FF0000')
Default: {DEFAULT_CONFIG.background_color}""",
    )

    # Timeout / window detection section
    timeout_group = parser.add_argument_group("WINDOW DETECTION OPTIONS")
    timeout_group.add_argument(
        "--target-delay",
        type=int,
        default=DEFAULT_CONFIG.target_delay,
        help="Seconds to wait before capturing active window",
    )
    timeout_group.add_argument(
        "--pid-timeout",
        type=int,
        default=DEFAULT_CONFIG.pid_timeout,
        help="Seconds to try PID‑based window detection",
    )
    timeout_group.add_argument(
        "--class-timeout",
        type=int,
        default=DEFAULT_CONFIG.class_timeout,
        help="Seconds to try class‑based window detection",
    )
    timeout_group.add_argument(
        "--total-timeout",
        type=int,
        default=DEFAULT_CONFIG.total_timeout,
        help="Total seconds before giving up",
    )
    timeout_group.add_argument(
        "--starting-phase",
        type=int,
        choices=[1, 2],
        default=DEFAULT_CONFIG.starting_phase,
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
    profile_name = args.profile
    config_path = args.config

    # Add log_level to args
    if args.debug:
        args.log_level = "DEBUG"
    elif args.quiet:
        args.log_level = "ERROR"
    else:
        args.log_level = "WARNING"

    provided_args = {
        key: value
        for key in DEFAULT_CONFIG.__dataclass_fields__.keys()
        if (value := getattr(args, key, None)) is not None
        and value != getattr(DEFAULT_CONFIG, key)
    }

    return provided_args, profile_name, config_path


def apply_overrides(config: Config, overrides: Dict[str, Any]) -> None:
    """Update config with values from overrides dict (only keys that exist)."""
    for key, value in overrides.items():
        if hasattr(config, key) and value is not None:
            setattr(config, key, value)
            logger.debug(f"Applied override: {key} = {value!r}")
        else:
            logger.warning(f"Ignoring unknown configuration key: '{key}'")
