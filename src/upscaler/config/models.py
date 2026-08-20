import os
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QStandardPaths

from ..utils import color_string_to_float4, color_tuple_to_string

UPSCALING_MODELS = (
    "veryfast",
    "faster",
    "fast",
    "3x12",
    "4x12",
    "4x16",
    "4x24",
    "4x32",
    "8x32",
)
UPSAMPLERS: Dict[str, str] = {
    "Lanczos-2": "lanczos",
    "FSR 1.0": "fsr",
    "NIS (NVIDIA)": "nis",
}
DOWNSAMPLERS: Dict[str, str] = {
    "Catmull-Rom": "catmull",
    "Lanczos (adaptive)": "lanczos",
}
OUTPUT_GEOMETRIES = ("fit", "stretch", "cover")
ZOOM_LEVELS = tuple(f"{level}%" for level in range(50, 401, 25))

DEFAULT_HOTKEYS = {
    "toggle_scaling": "Alt+Shift+S",
    "exit_app": "Alt+Shift+Escape",
    "screenshot": "Alt+Shift+P",
    "cycle_model": "Alt+Shift+M",
    "cycle_geometry": "Alt+Shift+G",
    "restore_view": "Alt+Shift+R",
    "zoom_in": "Alt+Shift+Plus",
    "zoom_out": "Alt+Shift+Minus",
    "offset_up": "Alt+Shift+Up",
    "offset_down": "Alt+Shift+Down",
    "offset_left": "Alt+Shift+Left",
    "offset_right": "Alt+Shift+Right",
}


class OverlayMode(str, Enum):
    """Overlay window behavior modes."""

    ALWAYS_ON_TOP = "always-on-top"
    ALWAYS_ON_TOP_TRANSPARENT = "top-transparent"
    FULLSCREEN = "fullscreen"
    WINDOWED = "windowed"


class VulkanPresentMode(Enum):
    FIFO = "fifo"
    MAILBOX = "mailbox"
    IMMEDIATE = "immediate"


BackgroundColor = Union[str, Tuple[float, float, float, float]]


@dataclass
class Config:
    """
    Global configuration for the upscaler.

    Most values can be set via the CLI, YAML configuration file, or
    programmatically. The ``to_dict`` method can be used for YAML export.

    Attributes:
        program: Command and arguments to launch before starting to upscale.
        select: If True, interactively select a window from a list.
        daemon: If True, run in daemon mode and automatically match profiles.
        daemon_exclude: If True, exclude the active window from daemon matching.
        target_title: Substring to match when selecting a window by title.
        target_title_regex: Regular expression to match a window title.
        follow_focus: If True, follow the currently focused window.
        pause_on_focus_loss: If True, hide overlay when the target loses focus.
        focus_poll_interval: Seconds between focus checks.
        daemon_poll_interval: Seconds between daemon window scans.
        pipeline_poll_interval: Seconds between pipeline idle checks.
        target_delay: Seconds to wait before capturing the active window.
        pid_timeout: Seconds for PID‑based window detection.
        class_timeout: Seconds for WM_CLASS‑based detection.
        total_timeout: Maximum seconds to wait for a window.
        starting_phase: Which detection phase to try first (1 or 2).
        model: SRCNN model name.
        double_upscale: If True, chain two 2x passes for 4x upscaling.
        upsampler: Final upsampling filter (lanczos, fsr, nis).
        downsampler: Final downsampling filter (catmull, lanczos).
        blur: Kernel width for final resampling.
        antiring_strength: Anti‑ringing strength.
        tight_antiring: If True, use tight anti‑ringing.
        kernel_radius: Override automatic Lanczos radius.
        deband_enabled: If True, apply debanding before scaling.
        deband_strength: Debanding intensity.
        cas_enabled: If True, apply Contrast Adaptive Sharpening.
        cas_strength: CAS intensity.
        bloom_enabled: If True, apply bloom.
        bloom_strength: Bloom intensity.
        bloom_threshold: Brightness threshold for bloom.
        bloom_radius: Blur radius for bloom in pixels.
        vignette_enabled: If True, apply vignette.
        vignette_strength: Vignette intensity.
        vignette_radius: Distance from center where vignette starts.
        vignette_falloff: Softness of vignette transition.
        lut_enabled: If True, apply 3D color LUT.
        lut_intensity: Blend between original and graded image.
        lut_preset: Built‑in LUT preset name.
        grain_enabled: If True, apply film grain.
        grain_strength: Film grain intensity.
        grain_size: Apparent particle size.
        gpu: GPU selection identifier.
        monitor: Monitor to cover ('primary', 'all', name, or index).
        scale_factor: Manual scale factor override.
        output_geometry: Output sizing mode (fit, stretch, cover, custom).
        crop_top: Pixels to crop from top.
        crop_bottom: Pixels to crop from bottom.
        crop_left: Pixels to crop from left.
        crop_right: Pixels to crop from right.
        background_color: Color for letterbox bars.
        offset_x: Horizontal content offset in pixels.
        offset_y: Vertical content offset in pixels.
        overlay_mode: Overlay window behavior.
        hide_cursor: Milliseconds of inactivity before hiding cursor.
        overlay_opacity_min: Minimum overlay opacity.
        overlay_opacity_max: Maximum overlay opacity.
        screenshot_dir: Directory for screenshots.
        screenshot_filename: Filename template for screenshots.
        show_osd: If True, show on‑screen display messages.
        osd_duration: How long OSD messages stay visible.
        max_fps: Maximum pipeline frames per second.
        vulkan_present_mode: Vulkan presentation mode (fifo, mailbox, immediate).
        vulkan_buffer_pool_size: Number of staging buffers.
        frame_timeout: GPU frame fence timeout in nanoseconds.
        use_tile_processing: If True, enable tile‑based processing.
        use_damage_tracking: If True, transfer only damaged regions.
        tile_size: Tile interior size in pixels.
        tile_context_margin: Extra border pixels added to each tile.
        max_tile_layers: Maximum tiles to process per frame.
        area_threshold: Dirty area fraction that forces full‑frame fallback.
        max_capture_failures: Consecutive capture failures before shutdown.
        capture_failure_delay: Seconds to wait after a capture failure.
        swapchain_debounce: Minimum seconds between swapchain recreations.
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional log file path.
        config_file: Internal path of loaded config file.
        hotkeys: Mapping of action names to hotkey strings.
    """

    # Program
    program: Optional[List[str]] = None

    # Target selection
    select: bool = False
    daemon: bool = False
    daemon_exclude: bool = False
    target_title: Optional[str] = None
    target_title_regex: Optional[str] = None

    # Focus tracking
    follow_focus: bool = False
    pause_on_focus_loss: bool = True

    # Timing
    focus_poll_interval: float = 0.2
    daemon_poll_interval: float = 2.0
    pipeline_poll_interval: float = 0.1

    # Window detection
    target_delay: float = 5
    pid_timeout: float = 5
    class_timeout: float = 5
    total_timeout: float = 60
    starting_phase: int = 1

    # Upscaling
    model: str = "fast"
    double_upscale: bool = False

    # Samplers
    upsampler: str = "lanczos"
    downsampler: str = "catmull"
    blur: float = 1.0
    antiring_strength: float = 0.8
    tight_antiring: bool = True
    kernel_radius: Optional[int] = None

    # Debanding
    deband_enabled: bool = False
    deband_strength: float = 0.3

    # Contrast Adaptive Sharpening
    cas_enabled: bool = False
    cas_strength: float = 0.4

    # Bloom
    bloom_enabled: bool = False
    bloom_strength: float = 0.03
    bloom_threshold: float = 0.85
    bloom_radius: int = 4

    # Vignette
    vignette_enabled: bool = False
    vignette_strength: float = 0.5
    vignette_radius: float = 0.3
    vignette_falloff: float = 2.0

    # Color Grading (3D LUT)
    lut_enabled: bool = False
    lut_intensity: float = 1.0
    lut_preset: str = "identity"
    # TODO: LUT file path, for now we use identity LUT built-in

    # Film Grain
    grain_enabled: bool = False
    grain_strength: float = 0.15
    grain_size: float = 1.0

    # GPU
    gpu: Optional[str] = None

    # Display
    monitor: str = "primary"
    scale_factor: Optional[float] = None

    # Presentation
    output_geometry: str = "fit"
    crop_top: int = 0
    crop_bottom: int = 0
    crop_left: int = 0
    crop_right: int = 0
    background_color: BackgroundColor = "black"
    offset_x: int = 0
    offset_y: int = 0

    # Overlay
    overlay_mode: str = OverlayMode.ALWAYS_ON_TOP.value
    hide_cursor: Optional[int] = None
    overlay_opacity_min: float = 0.2  # Not in argparser
    overlay_opacity_max: float = 1.0  # Not in argparser

    # Screenshots
    screenshot_dir: str = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.PicturesLocation), "Screenshots"
    )
    screenshot_filename: str = "Screenshot_{timestamp:%Y%m%d_%H%M%S}.png"

    # OSD
    show_osd: bool = True
    osd_duration: float = 1.5

    # Vulkan
    max_fps: Optional[int] = None
    vulkan_present_mode: str = VulkanPresentMode.FIFO.value
    vulkan_buffer_pool_size: int = 8
    frame_timeout: int = 1_000_000_000

    # Tile processing
    use_tile_processing: bool = True
    use_damage_tracking: bool = True
    tile_size: int = 64
    tile_context_margin: int = 16
    max_tile_layers: int = 16
    area_threshold: float = 0.3

    # Error handling
    max_capture_failures: int = 10
    capture_failure_delay: float = 0.05
    swapchain_debounce: float = 1.0

    # Logging (set via flags, not directly from CLI)
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Config file (not a configurable option, just used internally)
    config_file: Optional[str] = None

    # Hotkeys
    hotkeys: Dict[str, str] = field(default_factory=lambda: DEFAULT_HOTKEYS.copy())

    # ----------------------------------------------------------------------------------
    # Convert to a serializable dict
    # ----------------------------------------------------------------------------------
    def to_dict(self, diff_only: bool = True) -> Dict[str, Any]:
        """Convert config to a dict suitable for YAML dump."""
        result = {}
        defaults = Config()
        defaults.background_color = color_string_to_float4(defaults.background_color)
        default_bg = defaults.background_color

        for f in fields(self):
            name = f.name
            # Fields we never save to the YAML file
            if name in ("config_file", "log_level", "log_file", "program"):
                continue

            value = getattr(self, name)
            default_value = getattr(defaults, name)

            if diff_only:
                if name == "background_color":
                    # Normalize to tuple for comparison
                    current_tuple = color_string_to_float4(value)
                    if current_tuple == default_bg:
                        continue
                    # Convert to hex string for YAML output
                    value = color_tuple_to_string(current_tuple)
                else:
                    if value == default_value:
                        continue

            result[name] = value

        # Always include hotkeys if they differ from defaults
        if diff_only and self.hotkeys == DEFAULT_CONFIG.hotkeys:
            result.pop("hotkeys", None)
        else:
            result["hotkeys"] = self.hotkeys

        return result


DEFAULT_CONFIG: Config = Config()
