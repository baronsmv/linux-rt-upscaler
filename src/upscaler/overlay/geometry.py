from dataclasses import dataclass
from typing import Optional

from ..config import Config, OverlayMode
from ..utils import get_base_geometry, parse_output_geometry
from ..window import WindowInfo


@dataclass(frozen=True)
class OverlayGeometry:
    """
    All geometry values needed to create and update the overlay.

    Attributes:
        overlay_x: X position of the overlay window on the screen (pixels).
        overlay_y: Y position of the overlay window on the screen (pixels).
        overlay_width: Width of the overlay window (pixels).
        overlay_height: Height of the overlay window (pixels).
        physical_overlay_width: Physical width of the overlay window (pixels).
        physical_overlay_height: Physical height of the overlay window (pixels).
        content_width: Logical width of the content (before scaling, after cropping).
        content_height: Logical height of the content (before scaling, after cropping).
        scale_mode: Scaling mode string (e.g., "fit", "stretch", "cover").
        crop_left: Number of pixels cropped from the left of the target window.
        crop_top: Number of pixels cropped from the top of the target window.
        crop_width: Width of the cropped region from the target window.
        crop_height: Height of the cropped region from the target window.
        offset_x: Additional horizontal offset applied to the content (only in non-windowed modes).
        offset_y: Additional vertical offset applied to the content.
    """

    overlay_x: int = 0
    overlay_y: int = 0
    overlay_width: int = 0
    overlay_height: int = 0
    physical_overlay_width: int = 0
    physical_overlay_height: int = 0
    content_width: int = 0
    content_height: int = 0
    scale_mode: str = "fit"
    crop_left: int = 0
    crop_top: int = 0
    crop_width: int = 0
    crop_height: int = 0
    offset_x: int = 0
    offset_y: int = 0


def compute_overlay_geometry(
    config: Config, win_info: Optional[WindowInfo]
) -> OverlayGeometry:
    """
    Compute all geometry parameters for the overlay based on configuration and target window.

    The function performs the following steps:
        1. Determine the base screen geometry (monitor selection and scale factor).
        2. Perform an initial parse of the output geometry using the original window dimensions
           to get the overlay size and mode.
        3. Adjust overlay position and size based on the selected overlay mode.
        4. Compute cropped dimensions from the target window (removing borders).
        5. Re-parse the output geometry using the cropped dimensions to obtain the final
           logical content size.

    Args:
        config: Application configuration (monitor, output geometry, crop values, offsets, overlay mode).
        win_info: Target window information (handle, width, height, title).

    Returns:
        OverlayGeometry dataclass containing all computed values.

    Raises:
        ValueError: If cropping results in non-positive dimensions.
    """
    # Determine base screen geometry
    base_x, base_y, logical_w, logical_h, scale = get_base_geometry(
        config.monitor, config.scale_factor
    )
    phys_base_w = int(round(logical_w * scale))
    phys_base_h = int(round(logical_h * scale))

    # Initial parse using original window dimensions
    overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
        config.output_geometry,
        win_info.width,
        win_info.height,
        phys_base_w,
        phys_base_h,
    )

    # Adjust overlay position and size based on overlay mode
    if config.overlay_mode == OverlayMode.WINDOWED.value:
        # Windowed mode: center on the monitor, apply offsets, and use computed size
        win_x = base_x + (phys_base_w - overlay_w) // 2 + config.offset_x
        win_y = base_y + (phys_base_w - overlay_h) // 2 + config.offset_y
        physical_overlay_w, physical_overlay_h = overlay_w, overlay_h
        offset_x = 0
        offset_y = 0
    else:
        # Non-windowed modes (fullscreen, always-on-top, transparent): cover the whole monitor
        win_x, win_y = base_x, base_y
        overlay_w, overlay_h = phys_base_w, phys_base_h
        physical_overlay_w, physical_overlay_h = phys_base_w, phys_base_h
        offset_x = config.offset_x
        offset_y = config.offset_y

    # Convert overlay size to logical for the Qt window
    logical_overlay_w = int(round(overlay_w / scale))
    logical_overlay_h = int(round(overlay_h / scale))

    # Compute cropped dimensions
    crop_width = win_info.width - config.crop_left - config.crop_right
    crop_height = win_info.height - config.crop_top - config.crop_bottom
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError(
            f"Invalid crop: resulting dimensions {crop_width}x{crop_height} "
            f"(original {win_info.width}x{win_info.height}, "
            f"crop left={config.crop_left}, right={config.crop_right}, "
            f"top={config.crop_top}, bottom={config.crop_bottom})"
        )

    # Re-parse output geometry using cropped dimensions to get final logical content size
    final_content_w, final_content_h, _, _, mode = parse_output_geometry(
        config.output_geometry,
        crop_width,
        crop_height,
        phys_base_w,
        phys_base_h,
    )
    logical_content_w = int(round(final_content_w / scale))
    logical_content_h = int(round(final_content_h / scale))

    return OverlayGeometry(
        overlay_x=win_x,
        overlay_y=win_y,
        overlay_width=logical_overlay_w,
        overlay_height=logical_overlay_h,
        physical_overlay_width=physical_overlay_w,
        physical_overlay_height=physical_overlay_h,
        content_width=logical_content_w,
        content_height=logical_content_h,
        scale_mode=mode,
        crop_left=config.crop_left,
        crop_top=config.crop_top,
        crop_width=crop_width,
        crop_height=crop_height,
        offset_x=offset_x,
        offset_y=offset_y,
    )
