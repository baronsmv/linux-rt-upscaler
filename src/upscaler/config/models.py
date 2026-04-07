from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union


class OverlayMode(str, Enum):
    """Overlay window behavior modes."""

    ALWAYS_ON_TOP = "always-on-top"
    ALWAYS_ON_TOP_TRANSPARENT = "top-transparent"
    FULLSCREEN = "fullscreen"
    WINDOWED = "windowed"


BackgroundColor = Union[str, Tuple[float, float, float, float]]


@dataclass
class Config:
    # General
    program: Optional[List[str]] = None
    select: bool = False
    follow_focus: bool = False

    # Overlay
    overlay_mode: str = OverlayMode.ALWAYS_ON_TOP.value

    # Display
    monitor: str = "primary"
    scale_factor: Optional[float] = None

    # Upscaling
    model: str = "fast"
    double_upscale: bool = False

    # Output geometry
    output_geometry: str = "fit"
    crop_top: int = 0
    crop_bottom: int = 0
    crop_left: int = 0
    crop_right: int = 0
    offset_x: int = 0
    offset_y: int = 0
    background_color: BackgroundColor = "black"

    # Window detection
    target_delay: int = 5
    pid_timeout: int = 5
    class_timeout: int = 5
    total_timeout: int = 60
    starting_phase: int = 1

    # Logging (set via flags, not directly from CLI)
    log_level: str = "WARNING"
    log_file: Optional[str] = None

    # Config file (not a configurable option, just used internally)
    config_file: Optional[str] = None
