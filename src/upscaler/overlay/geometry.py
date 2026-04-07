from dataclasses import dataclass

from ..config import OverlayMode, Config
from ..utils import get_base_geometry, parse_output_geometry
from ..window import WindowInfo


@dataclass(frozen=True)
class OverlayGeometry:
    """All geometry values needed to create and update the overlay."""

    overlay_x: int
    overlay_y: int
    overlay_width: int
    overlay_height: int
    content_width: int
    content_height: int
    scale_mode: str
    crop_left: int
    crop_top: int
    crop_width: int
    crop_height: int
    offset_x: int
    offset_y: int


def compute_overlay_geometry(config: Config, win_info: WindowInfo) -> OverlayGeometry:
    """Compute all geometry parameters for the overlay."""
    # Determine base screen geometry
    base_x, base_y, base_w, base_h, config.scale_factor = get_base_geometry(
        config.monitor, config.scale_factor
    )

    # Parse output geometry (initial pass using original window dimensions)
    overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
        config.output_geometry, win_info.width, win_info.height, base_w, base_h
    )

    # Compute overlay position and content offsets
    if config.overlay_mode == OverlayMode.WINDOWED.value:
        win_x = base_x + (base_w - overlay_w) // 2 + config.offset_x
        win_y = base_y + (base_h - overlay_h) // 2 + config.offset_y
        offset_x = 0
        offset_y = 0
    else:
        win_x = base_x
        win_y = base_y
        overlay_w = base_w
        overlay_h = base_h
        offset_x = config.offset_x
        offset_y = config.offset_y

    # Compute cropped dimensions
    crop_width = win_info.width - config.crop_left - config.crop_right
    crop_height = win_info.height - config.crop_top - config.crop_bottom
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError(
            f"Invalid crop: resulting dimensions {crop_width}x{crop_height} "
            f"(original {win_info.width}x{win_info.height})"
        )

    # Re‑parse output geometry using cropped dimensions (final content size)
    final_content_w, final_content_h, _, _, mode = parse_output_geometry(
        config.output_geometry, crop_width, crop_height, base_w, base_h
    )

    return OverlayGeometry(
        overlay_x=win_x,
        overlay_y=win_y,
        overlay_width=overlay_w,
        overlay_height=overlay_h,
        content_width=final_content_w,
        content_height=final_content_h,
        scale_mode=mode,
        crop_left=config.crop_left,
        crop_top=config.crop_top,
        crop_width=crop_width,
        crop_height=crop_height,
        offset_x=offset_x,
        offset_y=offset_y,
    )
