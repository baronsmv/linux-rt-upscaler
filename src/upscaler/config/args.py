import argparse
import logging
import sys
from importlib.metadata import version, PackageNotFoundError
from typing import Tuple, Dict, Optional, Any

from .logging import setup_logging
from .models import Config, OverlayMode, DEFAULT_CONFIG, UPSCALING_MODELS
from ..shaders import BUILT_IN_PRESETS

logger = logging.getLogger(__name__)


class FilteredHelpAction(argparse._HelpAction):
    """Print help with optional filtering of additional argument groups."""

    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        show_all=False,
        help=None,
    ):
        super().__init__(
            option_strings=option_strings, dest=dest, default=default, help=help
        )
        self.show_all = show_all

    def __call__(self, parser, namespace, values, option_string=None):
        if self.show_all:
            # Print everything (used for --help-all)
            parser.print_help()
        else:
            # Build a list of only essential actions
            essential_actions = [
                a
                for a in parser._actions
                if not getattr(a.container, "additional", False)
            ]

            # Filter argument groups
            original_groups = parser._action_groups
            essential_groups = [
                g for g in original_groups if not getattr(g, "additional", False)
            ]

            # Save originals and swap
            original_actions = parser._actions
            parser._actions = essential_actions
            parser._action_groups = essential_groups

            # Suppress epilog for short help
            original_epilog = parser.epilog
            parser.epilog = None

            # Print help message, now clean
            parser.print_help()

            # Restore everything
            parser._actions = original_actions
            parser._action_groups = original_groups
            parser.epilog = original_epilog

            print("\nFor additional and advanced options, see: upscale --help-all.")
        parser.exit()


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
        description="Real-Time Upscaler for Linux",
        add_help=False,
        epilog="See source code for details: https://github.com/baronsmv/linux-rt-upscaler.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser._positionals.title = "POSITIONAL ARGUMENTS"

    # ----------------------------------------------------------------------
    # General section
    # ----------------------------------------------------------------------
    parser._optionals.title = "GENERAL OPTIONS"
    parser.add_argument(
        "-h",
        "--help",
        action=FilteredHelpAction,
        show_all=False,
        help="Show a short help message with common options and exit.",
    )
    parser.add_argument(
        "--help-all",
        action=FilteredHelpAction,
        show_all=True,
        help="Show a full help message with all options and exit.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show program version and exit.",
    )

    # ----------------------------------------------------------------------
    # Configuration section
    # ----------------------------------------------------------------------
    configuration_group = parser.add_argument_group("CONFIGURATION OPTIONS")
    configuration_group.add_argument(
        "-c",
        "--config",
        help="""Path to config file (YAML).
Default: '~/.config/linux-rt-upscaler/config.yaml'.""",
    )
    configuration_group.add_argument(
        "-p",
        "--profile",
        help="Name of a profile to explicitly apply from the config file.",
    )

    # Program argument
    parser.add_argument("program", nargs="*", help="Program to launch and scale.")

    # ----------------------------------------------------------------------
    # Target Selection section
    # ----------------------------------------------------------------------
    target_selection_group = parser.add_argument_group("TARGET SELECTION OPTIONS")
    target_selection_group.add_argument(
        "-s",
        "--select",
        action="store_true",
        help="Select a window from the list of open windows.",
    )
    target_selection_group.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="""Run in background, automatically upscaling any window
matching a profile. Can be combined with --follow-focus.""",
    )
    target_selection_group.add_argument(
        "-t",
        "--target-title",
        type=str,
        default=DEFAULT_CONFIG.target_title,
        help="""Target a window whose title contains this string
(case-insensitive).""",
    )
    target_selection_group.add_argument(
        "--target-title-regex",
        type=str,
        default=DEFAULT_CONFIG.target_title_regex,
        help="Target a window whose title matches this regular expression.",
    )

    # ----------------------------------------------------------------------
    # Focus Tracking section
    # ----------------------------------------------------------------------
    focus_tracking_group = parser.add_argument_group("FOCUS TRACKING OPTIONS")
    focus_tracking_group.add_argument(
        "-f",
        "--follow-focus",
        action="store_true",
        help="""Follow the currently focused window (automatically switch
when focus changes). Can be combined with --daemon.""",
    )
    focus_tracking_group.add_argument(
        "--no-focus-pause",
        action="store_false",
        dest="pause_on_focus_loss",
        help="""Overlay is hidden when the target loses focus by default.
Use this flag to keep it always visible.""",
    )

    # ----------------------------------------------------------------------
    # Interval section
    # ----------------------------------------------------------------------
    interval_group = parser.add_argument_group("INTERVAL OPTIONS")
    interval_group.add_argument(
        "--daemon-poll-interval",
        type=float,
        default=DEFAULT_CONFIG.daemon_poll_interval,
        help="""How often (seconds) the application checks for active
windows when --daemon is activated.
Minimum is 0.1. Default: %(default)s.""",
    )
    interval_group.add_argument(
        "--focus-poll-interval",
        type=float,
        default=DEFAULT_CONFIG.focus_poll_interval,
        help="""How often (seconds) the application checks for window focus
changes when --follow-focus is activated.
Minimum is 0.01. Default: %(default)s.""",
    )
    interval_group.add_argument(
        "--pipeline-poll-interval",
        type=float,
        default=DEFAULT_CONFIG.pipeline_poll_interval,
        help="""How often (seconds) the pipeline thread checks its internal
state when idle or paused.
Minimum is 0.01. Default: %(default)s.""",
    )

    # ----------------------------------------------------------------------
    # Window detection section
    # ----------------------------------------------------------------------
    window_detection_group = parser.add_argument_group("WINDOW DETECTION OPTIONS")
    window_detection_group.add_argument(
        "--target-delay",
        type=float,
        default=DEFAULT_CONFIG.target_delay,
        help="""Seconds to wait before capturing active window.
Default: %(default)s.""",
    )
    window_detection_group.add_argument(
        "--pid-timeout",
        type=float,
        default=DEFAULT_CONFIG.pid_timeout,
        help="""Seconds to try PID-based window detection.
Default: %(default)s.""",
    )
    window_detection_group.add_argument(
        "--class-timeout",
        type=float,
        default=DEFAULT_CONFIG.class_timeout,
        help="""Seconds to try class-based window detection.
Default: %(default)s.""",
    )
    window_detection_group.add_argument(
        "--total-timeout",
        type=float,
        default=DEFAULT_CONFIG.total_timeout,
        help="""Total seconds before giving up.
Default: %(default)s.""",
    )
    window_detection_group.add_argument(
        "--starting-phase",
        type=int,
        choices=[1, 2],
        default=DEFAULT_CONFIG.starting_phase,
        help="""Start with phase 1 (PID) or 2 (class).
Default: %(default)s.""",
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
        help="""Upscaling model to use (ordered from worst to best quality).
Default: %(default)s.""",
    )
    upscaling_group.add_argument(
        "-2",
        "--double-upscale",
        action="store_true",
        help="""Perform two 2x passes (total 4x) for higher resolution
screens (4k, 1440p) or low-resolution sources.""",
    )

    # ----------------------------------------------------------------------
    # Lanczos Scaler Options
    # ----------------------------------------------------------------------
    lanczos_group = parser.add_argument_group("LANCZOS SCALER OPTIONS")
    lanczos_group.add_argument(
        "--lanczos-blur",
        type=float,
        default=DEFAULT_CONFIG.lanczos_blur,
        help="""Kernel width for the final resampling step (>0.0 - 2.0).

Lower values increase sharpness/ringing; higher values
smooth the result.

Recommended range: 0.8 - 1.2. Default: %(default)s.

""",
    )
    lanczos_group.add_argument(
        "--lanczos-antiring-strength",
        type=float,
        default=DEFAULT_CONFIG.lanczos_antiring_strength,
        help="""Anti-ringing strength (0.0 - 1.0).

Lower values soften the clamp, preserving more detail at
the cost of possible ringing.

Recommended range: 0.7 - 1.0. Default: %(default)s.

""",
    )
    lanczos_group.add_argument(
        "--no-lanczos-linear-light",
        action="store_false",
        dest="lanczos_linear_light",
        help="""Disable linear-light processing (sRGB-linear-sRGB).

Disabling it may improve text clarity on some content,
but colors could lose saturation when downscaling.

""",
    )
    lanczos_group.add_argument(
        "--no-lanczos-tight-antiring",
        action="store_false",
        dest="lanczos_tight_antiring",
        help="""Disable tight anti-ringing.

When enabled (default), ringing bounds are derived only
from the central 2x2 neighborhood, which keeps thin text
and line art sharp. When disabled, the full filter
footprint is used for a more conservative clamp that may
soften edge details.

Leave this enabled unless you notice distant ringing
artifacts on high-contrast edges.
""",
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
Default: %(default)s.

Note: using 'all' requires a manual scale factor.

""",
    )
    display_group.add_argument(
        "--scale-factor",
        type=float,
        default=DEFAULT_CONFIG.scale_factor,
        help="""Override the automatic Wayland scale factor
(e.g., 1.5 for 150%% scaling).

By default, the scale factor is detected automatically
using physical monitor resolution. This override is
required when --monitor is set to 'all'.
""",
    )

    # ----------------------------------------------------------------------
    # Overlay options
    # ----------------------------------------------------------------------
    overlay_group = parser.add_argument_group("OVERLAY OPTIONS")
    overlay_group.add_argument(
        "--overlay-mode",
        choices=[e.value for e in OverlayMode],
        default=DEFAULT_CONFIG.overlay_mode,
        help="""Overlay window behaviour.
Default: %(default)s.

Note: Keyboard events are NOT forwarded, so it's best to
keep the target window focused (if on a single monitor,
always-on-top works well for this).

Modes:
  always-on-top   - Floating overlay above all windows
                    and not focusable (bypasses WM).
  top-transparent - Same as above but click-through
                    (mouse passes to window below).
  fullscreen      - Fullscreen window without decorations
                    (covers entire monitor).
  windowed        - Normal window with decorations, fixed
                    size.
""",
    )

    # ----------------------------------------------------------------------
    # Presentation options
    # ----------------------------------------------------------------------
    presentation_group = parser.add_argument_group("PRESENTATION OPTIONS")
    presentation_group.add_argument(
        "-o",
        "--output-geometry",
        default=DEFAULT_CONFIG.output_geometry,
        help="""Output window sizing and scaling behaviour.
Default: %(default)s.

Common modes:
  fit     - Letterbox, preserve aspect ratio
  stretch - Fill, ignore aspect ratio
  cover   - Fill and crop to fit

Note: Custom modes (e.g., x1440p, 50%%) can be combined with
--overlay-mode windowed to define the overlay window size.

""",
    )
    presentation_group.add_argument(
        "--crop-top",
        type=int,
        default=DEFAULT_CONFIG.crop_top,
        help="Pixels to crop from top border of the target window.",
    )
    presentation_group.add_argument(
        "--crop-bottom",
        type=int,
        default=DEFAULT_CONFIG.crop_bottom,
        help="Pixels to crop from bottom border of the target window.",
    )
    presentation_group.add_argument(
        "--crop-left",
        type=int,
        default=DEFAULT_CONFIG.crop_left,
        help="Pixels to crop from left border of the target window.",
    )
    presentation_group.add_argument(
        "--crop-right",
        type=int,
        default=DEFAULT_CONFIG.crop_right,
        help="Pixels to crop from right border of the target window.",
    )
    presentation_group.add_argument(
        "--background-color",
        default=DEFAULT_CONFIG.background_color,
        help="""Color for letterbox bars (supports transparency).
Default: %(default)s.

Can be a:
  CSS color name (e.g., 'black', 'red', 'transparent').
  Hex code (e.g., '#000000', '#FF0000', '#00000080').
  Functional notation ('rgb(255,0,0)', 'rgba(255,0,0,0.5)').
""",
    )

    # ----------------------------------------------------------------------
    # Additional Presentation options
    # ----------------------------------------------------------------------
    additional_presentation_group = parser.add_argument_group(
        "ADDITIONAL PRESENTATION OPTIONS"
    )
    additional_presentation_group.add_argument(
        "--offset-x",
        type=int,
        default=DEFAULT_CONFIG.offset_x,
        help="""Horizontal offset from centered position (pixels, positive
moves right, negative moves left).

Note: To pass negative values, use --offset-x=-1 (with an
equals sign). The form --offset-x -1 will be misinterpreted
because the shell treats -1 as a separate option.

""",
    )
    additional_presentation_group.add_argument(
        "--offset-y",
        type=int,
        default=DEFAULT_CONFIG.offset_y,
        help="""Vertical offset from centered position (pixels, positive
moves down, negative moves up).

Note: Same as above.
""",
    )

    # ----------------------------------------------------------------------
    # Pre-processing options
    # ----------------------------------------------------------------------
    pre_processing_group = parser.add_argument_group("PRE-PROCESSING OPTIONS")

    # --- Debanding ---
    pre_processing_group.add_argument(
        "--enable-deband",
        action="store_true",
        default=DEFAULT_CONFIG.deband_enabled,
        dest="deband_enabled",
        help="""Apply a stochastic debanding pass before scaling.

Debanding smooths out harsh color steps (banding) that can
appear in gradients after AI upscaling, especially in skies,
fog, or smooth backgrounds.

""",
    )
    pre_processing_group.add_argument(
        "--deband-strength",
        type=float,
        default=DEFAULT_CONFIG.deband_strength,
        help="""Debanding intensity (0.0 - 1.0).

Low values (0.1 - 0.3) are sufficient for most content.
Higher values risk softening fine details.

Default: %(default)s.
""",
    )

    # ----------------------------------------------------------------------
    # Post-processing options
    # ----------------------------------------------------------------------
    post_processing_group = parser.add_argument_group("POST-PROCESSING OPTIONS")

    # --- CAS (Contrast Adaptive Sharpening) ---
    post_processing_group.add_argument(
        "--enable-cas",
        action="store_true",
        default=DEFAULT_CONFIG.cas_enabled,
        dest="cas_enabled",
        help="""Enable Contrast Adaptive Sharpening (CAS) after scaling.

CAS adds a subtle, perceptually-based sharpening that
enhances text and line art without the halos common in
traditional unsharp masks.

""",
    )
    post_processing_group.add_argument(
        "--cas-strength",
        type=float,
        default=DEFAULT_CONFIG.cas_strength,
        help="""CAS sharpening amount (0.0 - 1.0).

Values between 0.2 and 0.5 provide a pleasant crispness
without visible artifacts. Above 0.6, some ringing may
become noticeable on high-contrast edges.

Default: %(default)s.

""",
    )

    # --- Bloom ---
    post_processing_group.add_argument(
        "--enable-bloom",
        action="store_true",
        default=DEFAULT_CONFIG.bloom_enabled,
        dest="bloom_enabled",
        help="""Enable a soft bloom (glow) effect around bright regions.

Bloom creates a cinematic, dreamy look by feeding bright
pixels through a wide blur and screen-blending the result
back onto the image.

""",
    )
    post_processing_group.add_argument(
        "--bloom-strength",
        type=float,
        default=DEFAULT_CONFIG.bloom_strength,
        help="""Bloom intensity (0.0 - 1.0).

Subtle values (0.02 - 0.06) add a gentle, polished look.
Strength above 0.1 may cause bright UI elements to halo
noticeably.

Default: %(default)s.

""",
    )
    post_processing_group.add_argument(
        "--bloom-threshold",
        type=float,
        default=DEFAULT_CONFIG.bloom_threshold,
        help="""Brightness cutoff for bloom (0.0 - 1.0).

Only pixels whose blurred brightness exceeds this value
will contribute. Lower thresholds (e.g., 0.7) include more
of the scene; higher thresholds (0.9 - 0.95) restrict the
glow to pure highlights like glowing embers or bright sky.

Default: %(default)s.

""",
    )
    post_processing_group.add_argument(
        "--bloom-radius",
        type=int,
        default=DEFAULT_CONFIG.bloom_radius,
        help="""Blur radius in pixels for the bloom core (1 - 16).

Larger radii spread the glow further, creating a softer,
more ethereal look. Smaller radii keep the effect tight.

Default: %(default)s.

""",
    )

    # --- Vignette ---
    post_processing_group.add_argument(
        "--enable-vignette",
        action="store_true",
        default=DEFAULT_CONFIG.vignette_enabled,
        dest="vignette_enabled",
        help="""Enable a radial vignette that darkens screen edges.

A vignette naturally draws attention to the center of the
screen and can simulate the look of a camera lens.

""",
    )
    post_processing_group.add_argument(
        "--vignette-strength",
        type=float,
        default=DEFAULT_CONFIG.vignette_strength,
        help="""Intensity of edge darkening (0.0 - 1.0).

Moderate values (0.3 - 0.6) give a subtle framing effect
without overwhelming the image.

Default: %(default)s.

""",
    )
    post_processing_group.add_argument(
        "--vignette-radius",
        type=float,
        default=DEFAULT_CONFIG.vignette_radius,
        help="""Distance from center where darkening begins (0.0 - 2.0).

0.0 starts immediately, affecting most of the screen.
Values around 0.7 - 0.8 keep the center bright and only
darken the far edges. At 1.0+ the vignette is confined
to extreme corners.

Default: %(default)s.

""",
    )
    post_processing_group.add_argument(
        "--vignette-falloff",
        type=float,
        default=DEFAULT_CONFIG.vignette_falloff,
        help="""Softness of the vignette transition (0.1 - 10.0).

Low values (1.0) create a gentle, wide-rolloff effect.
Higher values (3.0 - 4.0) produce a sharp, distinct ring.

Default: %(default)s.

""",
    )

    # --- Film Grain ---
    post_processing_group.add_argument(
        "--enable-grain",
        action="store_true",
        default=DEFAULT_CONFIG.grain_enabled,
        dest="grain_enabled",
        help="""Enable simulated film grain on the final image.

An isotropic noise texture is added with a soft-light
blend, mimicking the look of real film emulsion.

""",
    )
    post_processing_group.add_argument(
        "--grain-strength",
        type=float,
        default=DEFAULT_CONFIG.grain_strength,
        help="""Grain intensity (0.0 - 1.0).

Low values (0.1 - 0.2) mimic fine photochemical grain.
Higher values (0.3+) give a more noticeable film look.

Default: %(default)s.

""",
    )
    post_processing_group.add_argument(
        "--grain-size",
        type=float,
        default=DEFAULT_CONFIG.grain_size,
        help="""Apparent particle size of the grain (1.0 - 10.0).

Larger values (2.0+) produce more visible, clumpier grain
typical of older film stocks.

Default: %(default)s.

""",
    )

    # --- color Grading (3D LUT) ---
    post_processing_group.add_argument(
        "--enable-lut",
        action="store_true",
        default=DEFAULT_CONFIG.lut_enabled,
        dest="lut_enabled",
        help="""Apply a cinematic 3D color-lookup table (LUT) at the end of
the pipeline.

A LUT remaps all colors through a pre-computed table,
enabling instant film-stock emulation, color-grading
presets, or any global color transform.

""",
    )
    post_processing_group.add_argument(
        "--lut-intensity",
        type=float,
        default=DEFAULT_CONFIG.lut_intensity,
        help="""Blend between original and graded image (0.0 - 1.0).

0.0 = original image (no effect).
1.0 = full color transform applied (default).

""",
    )
    post_processing_group.add_argument(
        "--lut-preset",
        type=str,
        choices=tuple(BUILT_IN_PRESETS.keys()),
        default=DEFAULT_CONFIG.lut_preset,
        help="""Built-in 3D LUT preset for color grading.

Available presets:
  identity - No color change (default).
  warm     - Golden-hour warmth: boosts reds/oranges.
  cool     - Moonlit night: lifts blues, mutes warm tones.
  split    - Cyan shadows + orange highlights.
  vivid    - Increased saturation, preserves luminance.
  pastel   - Soft, dreamy desaturation with a light glow.
  lofi     - Vintage LCD look, crushed blacks, muted colors.
  bleach   - Metallic desaturation, high contrast.
  film     - Subtle S-curve contrast + slight desaturation.
  noir     - High-contrast black and white.
  sepia    - Old-photo warmth, slightly faded.
  cyano    - Blue-cyan monochrome, blueprint style.
""",
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
Default: '%(default)s'.""",
    )
    screenshot_group.add_argument(
        "--screenshot-filename",
        type=str,
        default=DEFAULT_CONFIG.screenshot_filename,
        help="""File name template for screenshots.
Default: 'Screenshot_{timestamp:%%Y%%m%%d_%%H%%M%%S}.png'.

Available placeholders:
  {timestamp} - capture time (supports strftime,
                e.g. '{timestamp:%%Y-%%m-%%d_%%H-%%M-%%S}').
  {model}     - active upscaling model.
  {width}     - upscaled image width in pixels.
  {height}    - upscaled image height in pixels.

Example: '{model}/{timestamp:%%H-%%M-%%S}.png'.
saves to 'fast/14-30-22.png'.
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
        help="""How long (seconds) OSD messages stay visible.
Default: %(default)s.""",
    )

    # ----------------------------------------------------------------------
    # Vulkan Performance Options
    # ----------------------------------------------------------------------
    vulkan_group = parser.add_argument_group("VULKAN PERFORMANCE OPTIONS")
    vulkan_group.add_argument(
        "--max-fps",
        type=int,
        default=DEFAULT_CONFIG.max_fps,
        help="""Cap the pipeline frame rate to this value.
Useful for power saving or consistent frame pacing.

Note: This cap will not exceed the display refresh rate
when combined with V‑Sync (fifo present mode).

""",
    )
    vulkan_group.add_argument(
        "--vulkan-present-mode",
        choices=["fifo", "mailbox", "immediate"],
        default=DEFAULT_CONFIG.vulkan_present_mode,
        help="""Vulkan presentation mode.
Default: %(default)s.

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

Recommended range: 2 - 16. Default: %(default)s.

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
Default: %(default)s.
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

Damage tracking is enabled by default; use this flag to
disable it only if you suspect it causes glitches.

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
Recommended range: 32 - 128. Default: %(default)s.

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

Recommended range: 4 - 24. Default: %(default)s.

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

Recommended range: 4 - 32. Default: %(default)s.

""",
    )

    tile_group.add_argument(
        "--area-threshold",
        type=float,
        default=DEFAULT_CONFIG.area_threshold,
        help="""Fraction of the window area (0.0 - 1.0) that, when dirty,
forces a fallback to full-frame processing in tile mode.

Smaller values (e.g., 0.15) fall back earlier, preventing
too many tiny tile dispatches. Larger values (e.g., 0.5)
try tile mode more aggressively. 0.0 always uses full-frame
for dirty frames; 1.0 never falls back.

Recommended range: 0.15 - 0.5. Default: %(default)s.
""",
    )

    # ----------------------------------------------------------------------
    # Error Recovery Options
    # ----------------------------------------------------------------------
    error_group = parser.add_argument_group("ERROR RECOVERY OPTIONS")
    error_group.add_argument(
        "--max-capture-failures",
        type=int,
        default=DEFAULT_CONFIG.max_capture_failures,
        help="""Number of consecutive capture failures before shutting down.
Minimum is 1. Default: %(default)s.""",
    )
    error_group.add_argument(
        "--capture-failure-delay",
        type=float,
        default=DEFAULT_CONFIG.capture_failure_delay,
        help="""Seconds to wait after a capture failure before retrying.
Minimum is 0.0. Default: %(default)s.""",
    )
    error_group.add_argument(
        "--swapchain-recreate-debounce",
        type=float,
        default=DEFAULT_CONFIG.swapchain_recreate_debounce,
        help="""Minimum seconds between two Vulkan swapchain recreations.
Minimum is 0.0. Default: %(default)s.""",
    )

    # ----------------------------------------------------------------------
    # Logging section
    # ----------------------------------------------------------------------
    log_group = parser.add_argument_group("LOGGING OPTIONS")
    log_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Decrease log verbosity (ERROR level).",
    )
    log_group.add_argument(
        "--debug",
        action="store_true",
        help="Increase log verbosity (DEBUG level).",
    )
    log_group.add_argument(
        "--log-file",
        help="Write logs to this file (parent directories are created).",
    )

    # ----------------------------------------------------------------------
    # Additional groups
    # ----------------------------------------------------------------------
    additional_groups = [
        interval_group,
        window_detection_group,
        lanczos_group,
        pre_processing_group,
        post_processing_group,
        additional_presentation_group,
        osd_group,
        vulkan_group,
        tile_group,
        error_group,
    ]
    for grp in additional_groups:
        grp.additional = True

    # ----------------------------------------------------------------------
    # Argument parse and map
    # ----------------------------------------------------------------------

    # Build a mapping from every option string to its destination name
    opt_to_dest = {
        opt: action.dest for action in parser._actions for opt in action.option_strings
    }
    args = parser.parse_args()

    # Scan sys.argv for options that were actually typed by the user
    explicit_dests = set()
    for arg in sys.argv[1:]:
        if arg == "--":
            break
        if arg.startswith("--"):
            dest = opt_to_dest.get(arg.split("=")[0])
            if dest and dest in DEFAULT_CONFIG.__dataclass_fields__:
                explicit_dests.add(dest)
        elif arg.startswith("-") and len(arg) > 1 and arg[1] != "-":
            for char in arg[1:]:
                flag = f"-{char}"
                dest = opt_to_dest.get(flag)
                if dest and dest in DEFAULT_CONFIG.__dataclass_fields__:
                    explicit_dests.add(dest)

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
