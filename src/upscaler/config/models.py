import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Union, Dict

from platformdirs import user_pictures_dir

UPSCALING_MODELS = (
    "8x32",
    "4x32",
    "4x24",
    "4x16",
    "4x12",
    "3x12",
    "fast",
    "faster",
    "veryfast",
)
OUTPUT_GEOMETRIES = ("fit", "stretch", "cover")
PROCESSING_MODES = ("full", "tile", "cache")

DEFAULT_HOTKEYS = {
    "toggle_scaling": "Alt+Shift+S",
    "cycle_model": "Alt+Shift+M",
    "cycle_geometry": "Alt+Shift+G",
    "screenshot": "Alt+Shift+P",
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
    # General
    program: Optional[List[str]] = None
    select: bool = False
    follow_focus: bool = False
    pause_on_focus_loss: bool = True

    # Overlay
    overlay_mode: str = OverlayMode.ALWAYS_ON_TOP.value
    overlay_opacity_min: float = 0.2  # Not in argparser
    overlay_opacity_max: float = 1.0  # Not in argparser

    # Display
    monitor: str = "primary"
    scale_factor: Optional[float] = None

    # Upscaling
    model: str = "fast"
    double_upscale: bool = False
    lanczos_blur: float = 1.0

    # Output geometry
    output_geometry: str = "fit"
    crop_top: int = 0
    crop_bottom: int = 0
    crop_left: int = 0
    crop_right: int = 0
    offset_x: int = 0
    offset_y: int = 0
    background_color: BackgroundColor = "black"

    # Screenshots
    screenshot_dir: str = os.path.join(user_pictures_dir(), "Screenshots")
    screenshot_filename: str = "Screenshot_{timestamp:%Y%m%d_%H%M%S}"
    screenshot_format: str = "png"
    screenshot_jpeg_quality: int = 95

    # OSD
    show_osd: bool = True
    osd_duration: float = 1.5

    # Window detection
    target_delay: int = 5
    pid_timeout: int = 5
    class_timeout: int = 5
    total_timeout: int = 60
    starting_phase: int = 1

    # Vulkan
    vulkan_present_mode: str = VulkanPresentMode.FIFO.value
    vulkan_buffer_pool_size: int = 8
    frame_timeout_ns: int = 1_000_000_000

    # Processing mode
    processing_mode: str = "tile"
    tile_size: int = 64
    area_threshold: float = 0.3

    # Full mode
    use_damage_tracking: bool = True

    # Tile and cache modes
    tile_context_margin: int = 16
    max_tile_layers: int = 8

    # Cache mode
    cache_capacity: int = 512

    # Logging (set via flags, not directly from CLI)
    log_level: str = "WARNING"
    log_file: Optional[str] = None

    # Config file (not a configurable option, just used internally)
    config_file: Optional[str] = None
    hotkeys: Dict[str, str] = field(default_factory=lambda: DEFAULT_HOTKEYS.copy())
