import logging
from typing import List, Tuple

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication

logger = logging.getLogger(__name__)


def get_monitor_list() -> List[str]:
    return [screen.name() for screen in QGuiApplication.screens()]


def get_monitor(monitor_spec: str) -> QRect:
    """
    Return the monitor specified.
    - 'primary'          → primary screen
    - 'all'              → union of all screens (virtual desktop)
    - integer as string  → screen at that index (e.g., '0')
    - monitor name       → case‑insensitive substring match (e.g., 'HDMI-1')
    Falls back to primary if not found.
    """
    screens = QGuiApplication.screens()
    if not screens:
        raise RuntimeError("No screens found")

    primary = QGuiApplication.primaryScreen()

    if monitor_spec == "primary":
        geom = primary.geometry()
        return geom

    if monitor_spec == "all":
        virtual = QRect()
        for screen in screens:
            virtual = virtual.united(screen.geometry())
        return virtual

    # Try as integer index
    try:
        idx = int(monitor_spec)
        if 0 <= idx < len(screens):
            geom = screens[idx].geometry()
            return geom
        else:
            logger.warning(f"Monitor index {idx} out of range. Using primary.")
    except ValueError:
        pass

    # Try as monitor name (case‑insensitive substring)
    spec_lower = monitor_spec.lower()
    for screen in screens:
        if spec_lower in screen.name().lower():
            geom = screen.geometry()
            return geom

    # Fallback
    logger.warning(f"Monitor spec '{monitor_spec}' not recognised. Using primary.")
    geom = primary.geometry()
    return geom


def get_monitor_geometry(
    monitor: QRect, scale_factor: float
) -> Tuple[int, int, int, int]:
    """Return (x, y, width, height) of the monitor(s) specified."""
    return (
        monitor.x(),
        monitor.y(),
        int(monitor.width() * scale_factor),
        int(monitor.height() * scale_factor),
    )
