import os
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QStandardPaths

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
ZOOM_LEVELS = ("50%", "75%", "100%", "150%", "200%", "300%", "400%")

DEFAULT_HOTKEYS = {
    "toggle_scaling": "Alt+Shift+S",
    "exit_app": "Alt+Shift+Escape",
    "screenshot": "Alt+Shift+P",
    "cycle_model": "Alt+Shift+M",
    "cycle_geometry": "Alt+Shift+G",
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
        from .parsers import color_string_to_float4, color_tuple_to_string

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
