import logging
from typing import Optional, Tuple

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QScreen
from screeninfo import get_monitors

logger = logging.getLogger(__name__)


def _get_screen(screen_spec: str) -> QScreen:
    """
    Return a single QScreen based on the specification.
    - 'primary'          - primary screen
    - integer as string  - screen at that index (e.g., '0')
    - screen name        - case-insensitive substring match (e.g., 'HDMI-1')
    Raises ValueError if no matching screen is found.
    Note: The 'all' spec is not handled here – _get_virtual_desktop() handles that.
    """
    screens = QGuiApplication.screens()
    if not screens:
        raise RuntimeError("No screens found")

    if screen_spec == "primary":
        primary = QGuiApplication.primaryScreen()
        if primary is None:
            raise RuntimeError("Primary screen not available")
        return primary

    # Try as integer index
    try:
        idx = int(screen_spec)
        if 0 <= idx < len(screens):
            return screens[idx]
        else:
            raise ValueError(f"Monitor index {idx} out of range (0..{len(screens)-1})")
    except ValueError:
        pass  # not an integer, continue

    # Try as screen name (case-insensitive substring)
    spec_lower = screen_spec.lower()
    matches = [s for s in screens if spec_lower in s.name().lower()]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        logger.warning(
            f"Multiple screens match '{screen_spec}': {[s.name() for s in matches]}. Using first."
        )
        return matches[0]

    # No match found
    raise ValueError(
        f"Screen spec '{screen_spec}' did not match any screen. Available: {[s.name() for s in screens]}"
    )


def _get_virtual_desktop() -> QRect:
    """Return the bounding rectangle of all screens combined."""
    screens = QGuiApplication.screens()
    if not screens:
        raise RuntimeError("No screens found")
    virtual = QRect()
    for screen in screens:
        virtual = virtual.united(screen.geometry())
    return virtual


def _get_physical_resolution(screen_name: str) -> Optional[Tuple[int, int]]:
    """
    Return (width_px, height_px) of the physical monitor matching the given screen name.
    First tries exact case-insensitive match, then substring match.
    Returns None if no match is found.
    """
    monitors = get_monitors()
    name_lower = screen_name.lower()

    # Exact match (case-insensitive)
    for m in monitors:
        if m.name.lower() == name_lower:
            return m.width, m.height

    # Substring fallback
    for m in monitors:
        if name_lower in m.name.lower():
            logger.debug(f"Substring match: '{screen_name}' -> '{m.name}'")
            return m.width, m.height

    logger.warning(f"No physical monitor found for screen name '{screen_name}'")
    return None


def _get_scale_factor(q_screen: QScreen) -> float:
    """
    Compute the scaling factor for a QScreen.
    Returns physical_width / logical_width, or 1.0 if physical data unavailable.
    Also validates that the height scaling matches within 1% tolerance.
    """
    logical_geom = q_screen.geometry()
    logical_w = logical_geom.width()
    logical_h = logical_geom.height()

    phys = _get_physical_resolution(q_screen.name())
    if phys is None:
        logger.warning(
            f"No physical data for {q_screen.name()}, using scale factor 1.0"
        )
        return 1.0

    phys_w, phys_h = phys
    scale_w = phys_w / logical_w
    scale_h = phys_h / logical_h

    if abs(scale_w - scale_h) > 0.01:
        logger.warning(
            f"Asymmetric scaling for {q_screen.name()}: width scale {scale_w:.3f}, "
            f"height scale {scale_h:.3f}. Using width scale."
        )

    return scale_w


def _get_screen_geometry(
    q_screen: QScreen, scale_factor: Optional[float] = None
) -> Tuple[int, int, int, int, float]:
    """
    Return (x, y, width, height) of the given QScreen in physical pixels.
    If scale_factor is None, it is computed automatically via get_scale_factor().
    """
    geom = q_screen.geometry()
    x, y = geom.x(), geom.y()
    logical_w, logical_h = geom.width(), geom.height()

    if scale_factor is None:
        scale_factor: float = _get_scale_factor(q_screen)

    physical_w = int(round(logical_w * scale_factor))
    physical_h = int(round(logical_h * scale_factor))

    return x, y, physical_w, physical_h, scale_factor


def get_base_geometry(
    monitor_spec: str, scale_factor: Optional[float] = None
) -> Tuple[int, int, int, int, float]:
    """
    Return (x, y, width, height, scale_factor) in physical pixels for the
    given monitor spec.
    """
    if monitor_spec == "all":
        if scale_factor is None:
            raise ValueError("scale_factor required for 'all' virtual desktop")
        rect = _get_virtual_desktop()
        return (
            rect.x(),
            rect.y(),
            int(rect.width() * scale_factor),
            int(rect.height() * scale_factor),
            scale_factor,
        )
    else:
        q_screen = _get_screen(monitor_spec)
        return _get_screen_geometry(q_screen, scale_factor)
