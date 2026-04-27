import argparse
import logging
import sys
from importlib.metadata import version, PackageNotFoundError
from typing import Tuple, Dict, Optional, Any

from .logging import setup_logging
from .models import Config, OverlayMode, UPSCALING_MODELS

logger = logging.getLogger(__name__)

DEFAULT_CONFIG: Config = Config()


def _get_version() -> str:
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
        description="Real-Time Upscaler for Linux",
        epilog="See source code for details: https://github.com/baronsmv/linux-rt-upscaler",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser._positionals.title = "POSITIONAL ARGUMENTS"
    parser._optionals.title = "GENERAL OPTIONS"
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {_get_version()}"
    )
    parser.add_argument(
        "-c",
        "--config",
        help="""Path to config file (YAML)
Default: '~/.config/linux-rt-upscaler/config.yaml'""",
    )
    parser.add_argument(
        "-p",
        "--profile",
        help="Name of a profile to explicitly apply from the config file",
    )

    # Program argument
    parser.add_argument("program", nargs="*", help="Program to launch and scale")

    # ----------------------------------------------------------------------
    # General section
    # ----------------------------------------------------------------------
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
        help="""Follow the currently focused window (automatically switch
when focus changes)""",
    )
    interaction_group.add_argument(
        "--focus-poll-interval",
        type=float,
        default=DEFAULT_CONFIG.focus_poll_interval,
        help="""How often (seconds) the application checks for window focus
changes when --follow-focus is activated.
Minimum is 0.05. Default: %(default)s""",
    )
    interaction_group.add_argument(
        "--no-focus-pause",
        action="store_false",
        dest="pause_on_focus_loss",
        help="""Do not pause/hide overlay when target window loses focus
(pause is enabled by default)""",
    )

    # ----------------------------------------------------------------------
    # Upscaling section
    # ----------------------------------------------------------------------
    upscaling_group = parser.add_argument_group("UPSCALING OPTIONS")
    upscaling_group.add_argument(
        "-m",
        "--model",
        choices=UPSCALING_MODELS,
        default=DEFAULT_CONFIG.model,
        help="""Upscaling model to use (ordered from best to worst quality)
Default: %(default)s""",
    )
    upscaling_group.add_argument(
        "-2",
        "--double-upscale",
        action="store_true",
        help="""Perform two 2x passes (total 4x) for higher resolution
screens (4k, 1440p) or low-resolution sources""",
    )
    upscaling_group.add_argument(
        "--lanczos-blur",
        type=float,
        default=DEFAULT_CONFIG.lanczos_blur,
        help="""Lanczos kernel blur factor. Values below 1.0 increase
sharpness and ringing; values above 1.0 smooth the result.
Recommended range: 0.8 - 1.2, default: %(default)s""",
    )

    # ----------------------------------------------------------------------
    # Display section
    # ----------------------------------------------------------------------
    display_group = parser.add_argument_group("DISPLAY OPTIONS")
    display_group.add_argument(
        "--monitor",
        type=str,
        default=DEFAULT_CONFIG.monitor,
        help="""Monitor to cover: 'primary', 'all' (to cover all
multi-monitor space), or monitor name/index
(e.g., 'HDMI-1', 0).
Default: %(default)s""",
    )
    display_group.add_argument(
        "--scale-factor",
        type=float,
        default=DEFAULT_CONFIG.scale_factor,
        help="""Override the automatic Wayland scale factor
(e.g., 1.5 for 150%% scaling).
By default, the scale factor is detected automatically
using physical monitor resolution. This override is
required when --monitor is set to 'all'.""",
    )

    # ----------------------------------------------------------------------
    # Overlay options
    # ----------------------------------------------------------------------
    overlay_group = parser.add_argument_group("OVERLAY OPTIONS")
    overlay_group.add_argument(
        "-o",
        "--output-geometry",
        default=DEFAULT_CONFIG.output_geometry,
        help="""Specify the output window size and scaling behaviour.
Default: %(default)s

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
        help="""Overlay window behaviour.
Default: %(default)s

Note: Keyboard events are NOT forwarded, so it's best to
keep the target window focused (if on a single monitor,
always-on-top works well for this).

Modes:
  always-on-top    - Floating overlay above all windows
                     and not focusable (bypasses WM).
  top-transparent  - Same as above but click-through
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

Note: To pass negative values, use --offset-x=-1 (with an
equals sign). The form --offset-x -1 will be misinterpreted
because the shell treats -1 as a separate option.
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
        help="""Color for letterbox bars (supports transparency).
Default: %(default)s

Can be a:
  CSS color name (e.g., 'black', 'red', 'transparent')
  Hex code (e.g., '#000000', '#FF0000', '#00000080')
  Functional notation ('rgb(255,0,0)', 'rgba(255,0,0,0.5)')

Note: RGB values must be integers 0-255.""",
    )

    # ----------------------------------------------------------------------
    # Screenshot section
    # ----------------------------------------------------------------------
    screenshot_group = parser.add_argument_group("SCREENSHOT OPTIONS")
    screenshot_group.add_argument(
        "--screenshot-dir",
        type=str,
        default=DEFAULT_CONFIG.screenshot_dir,
        help="""Directory to save screenshots.
Default: %(default)s""",
    )
    screenshot_group.add_argument(
        "--screenshot-filename",
        type=str,
        default=DEFAULT_CONFIG.screenshot_filename,
        help="""File name template for screenshots.
Default: Screenshot_{timestamp:%%Y%%m%%d_%%H%%M%%S}.png

Available placeholders:
  {timestamp}  - capture time (supports strftime,
                 e.g. {timestamp:%%Y-%%m-%%d_%%H-%%M-%%S})
  {model}      - active upscaling model
  {width}      - upscaled image width in pixels
  {height}     - upscaled image height in pixels

Example: "{model}/{timestamp:%%H-%%M-%%S}.png"
saves to "fast/14-30-22.png"
""",
    )

    # ----------------------------------------------------------------------
    # OSD section
    # ----------------------------------------------------------------------
    osd_group = parser.add_argument_group("OSD OPTIONS")
    osd_group.add_argument(
        "--no-osd",
        action="store_false",
        dest="show_osd",
        help="Disable on-screen display messages.",
    )
    osd_group.add_argument(
        "--osd-duration",
        type=float,
        default=DEFAULT_CONFIG.osd_duration,
        help="How long (seconds) OSD messages stay visible. Default: %(default)s",
    )

    # ----------------------------------------------------------------------
    # Vulkan Performance Options
    # ----------------------------------------------------------------------
    vulkan_group = parser.add_argument_group("VULKAN PERFORMANCE OPTIONS")
    vulkan_group.add_argument(
        "--vulkan-present-mode",
        choices=["fifo", "mailbox", "immediate"],
        default=DEFAULT_CONFIG.vulkan_present_mode,
        help="""Vulkan presentation mode.
Default: %(default)s

Modes:
  fifo      - V-Sync on. Limits FPS to display refresh rate.
              Lowest power consumption, no tearing.
  mailbox   - Tear-free, lower latency. GPU renders as fast
              as possible; only the latest complete frame
              is displayed. Higher power usage.
  immediate - Lowest latency, no V-Sync. Frames are displayed
              immediately, may cause visible tearing.

""",
    )
    vulkan_group.add_argument(
        "--vulkan-buffer-pool-size",
        type=int,
        default=DEFAULT_CONFIG.vulkan_buffer_pool_size,
        help="""Number of pre-allocated staging buffers used for uploading
partial texture updates.

A larger pool reduces the overhead of creating temporary
buffers on the fly during frequent damage updates, but
reserves a small amount of extra VRAM.

Raise this value if you notice stutters when many small
regions change rapidly.

Recommended range: 2-16, default: %(default)s

""",
    )
    vulkan_group.add_argument(
        "--frame-timeout",
        type=int,
        default=DEFAULT_CONFIG.frame_timeout,
        help="""Maximum time (in nanoseconds) to wait for the GPU to
complete the previous frame before starting the next
capture. If the GPU is still busy after this timeout, the
frame is skipped.

Lower values reduce CPU blocking but may cause dropped
frames under heavy load. Higher values guarantee each frame
completes before proceeding, at the cost of potential
pipeline stalls.

Recommended range: 16666667 (1/60 s) - 1000000000 (1 s)
Default: %(default)s
""",
    )

    # ----------------------------------------------------------------------
    # Tile Processing section
    # ----------------------------------------------------------------------
    tile_group = parser.add_argument_group("TILE PROCESSING OPTIONS")
    tile_group.add_argument(
        "--no-tile-processing",
        action="store_false",
        dest="use_tile_processing",
        default=DEFAULT_CONFIG.use_tile_processing,
        help="""Disable tile-based processing.

Tile mode divides the frame into smaller tiles and only
re-processes the ones that have changed. This is ideal for
mostly static content (e.g., text editors, visual novels)
where only small regions are updated each frame.

When disabled, the whole frame is upscaled in one pass,
better for video or rapidly changing content, or to avoid
any possible artifact from individual tile-processing.

""",
    )
    tile_group.add_argument(
        "--no-damage-tracking",
        action="store_false",
        dest="use_damage_tracking",
        help="""Always transfer the entire cropped frame to the GPU instead
of only the changed regions.

This increases PCIe bandwidth usage but guarantees the GPU
always has the full image, eliminating any potential risk
of missed updates from the compositor.

Keep enabled unless you suspect damage tracking causes
visual glitches.

""",
    )

    tile_group.add_argument(
        "--tile-size",
        type=int,
        default=DEFAULT_CONFIG.tile_size,
        help="""Size (in pixels) of each tile’s interior.

Small tiles track changes more precisely and process less
redundant data, but add CPU overhead during extraction.
Large tiles reduce CPU work but cause more over-processing.

Multiples of 32 work best with GPU workgroups.
Recommended range: 32-128, default: %(default)s

""",
    )

    tile_group.add_argument(
        "--tile-context-margin",
        type=int,
        default=DEFAULT_CONFIG.tile_context_margin,
        help="""Extra border pixels added around each tile before processing.

Provides the neural network with surrounding context to
avoid artifacts at tile boundaries.

Larger margins improve boundary quality but increase the
amount of data processed per tile. More complex models
benefit from higher values because their receptive field
is larger and they use deeper convolution stacks.

Recommended range: 4-24, default: %(default)s

""",
    )

    tile_group.add_argument(
        "--max-tile-layers",
        type=int,
        default=DEFAULT_CONFIG.max_tile_layers,
        help="""Maximum number of tiles processed per frame in tile mode.

When the count of dirty tiles exceeds this limit, the
pipeline falls back to full-frame processing to avoid
excessive GPU dispatches.

Higher values tolerate more scattered changes, but each
tile adds a GPU dispatch and may eventually hurt
performance.

Recommended range: 4-32, default: %(default)s

""",
    )

    tile_group.add_argument(
        "--area-threshold",
        type=float,
        default=DEFAULT_CONFIG.area_threshold,
        help="""Fraction of the window area (0.0-1.0) that, when dirty,
forces a fallback to full-frame processing in tile mode.

Smaller values (e.g., 0.15) fall back earlier, preventing
too many tiny tile dispatches. Larger values (e.g., 0.5)
try tile mode more aggressively. 0.0 always uses full-frame
for dirty frames; 1.0 never falls back.

Recommended range: 0.15-0.5, default: %(default)s
""",
    )

    # ----------------------------------------------------------------------
    # Timeout / window detection section
    # ----------------------------------------------------------------------
    window_detection_group = parser.add_argument_group("WINDOW DETECTION OPTIONS")
    window_detection_group.add_argument(
        "--target-delay",
        type=float,
        default=DEFAULT_CONFIG.target_delay,
        help="Seconds to wait before capturing active window",
    )
    window_detection_group.add_argument(
        "--pid-timeout",
        type=float,
        default=DEFAULT_CONFIG.pid_timeout,
        help="Seconds to try PID-based window detection",
    )
    window_detection_group.add_argument(
        "--class-timeout",
        type=float,
        default=DEFAULT_CONFIG.class_timeout,
        help="Seconds to try class-based window detection",
    )
    window_detection_group.add_argument(
        "--total-timeout",
        type=float,
        default=DEFAULT_CONFIG.total_timeout,
        help="Total seconds before giving up",
    )
    window_detection_group.add_argument(
        "--starting-phase",
        type=int,
        choices=[1, 2],
        default=DEFAULT_CONFIG.starting_phase,
        help="Start with phase 1 (PID) or 2 (class)",
    )

    # ----------------------------------------------------------------------
    # Logging section
    # ----------------------------------------------------------------------
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

    # Build a mapping from every option string to its destination name
    opt_to_dest = {
        opt: action.dest for action in parser._actions for opt in action.option_strings
    }
    args = parser.parse_args()

    # Scan sys.argv for options that were actually typed by the user
    explicit_dests = {
        dest
        for arg in sys.argv[1:]
        if (
            (dest := opt_to_dest.get(arg.split("=")[0]))
            and dest in DEFAULT_CONFIG.__dataclass_fields__
            and arg.startswith("-")
        )
    }

    # Build overrides only for explicitly supplied arguments
    provided_args = {
        key: getattr(args, key)
        for key in explicit_dests
        if getattr(args, key) is not None
    }

    if args.debug:
        provided_args["log_level"] = "DEBUG"
    elif args.quiet:
        provided_args["log_level"] = "ERROR"

    return provided_args, args.profile, args.config


def apply_overrides(config: Config, overrides: Dict[str, Any]) -> None:
    """Update config with values from overrides dict (only keys that exist)."""
    new_level = overrides.get("log_level", config.log_level)
    new_file = overrides.get("log_file", config.log_file)
    if (new_level != config.log_level) or (new_file != config.log_file):
        setup_logging(new_level, new_file)

    for key, value in overrides.items():
        if not hasattr(config, key):
            logger.warning(f"Ignoring unknown configuration key: '{key}'")
            continue

        if value is None:
            continue  # skip None values

        if key == "hotkeys" and isinstance(value, dict):
            # Merge dictionaries: user overrides take precedence
            config.hotkeys = {**config.hotkeys, **value}
            logger.debug("Applied hotkeys override")
        else:
            setattr(config, key, value)
            logger.debug(f"Applied configuration override: {key} = {value!r}")
