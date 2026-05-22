import logging
from typing import Optional, Tuple, List

import xcffib
from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication, QScreen
from xcffib.randr import Connection as RandRConnection

from ..window import open_xcb_connection, close_xcb_connection

logger = logging.getLogger(__name__)


def _get_randr_connection(conn: xcffib.Connection) -> RandRConnection:
    """Return the RandR extension connection for the given XCB connection."""
    conn.randr = conn(xcffib.randr.key)
    return conn.randr


def _list_monitor_names(conn: xcffib.Connection) -> List[str]:
    """
    Return a list of output names (e.g., 'HDMI-1', 'eDP-1') from RandR.
    Requires the RandR extension to be present.
    """
    randr = _get_randr_connection(conn)
    root = conn.get_setup().roots[0].root
    resources = randr.GetScreenResources(root).reply()
    names = []
    for output_id in resources.outputs:
        output_info = randr.GetOutputInfo(output_id, xcffib.CurrentTime).reply()
        if output_info and output_info.name_len:
            name = bytes(output_info.name).decode("utf-8")
            names.append(name)
    return names


def list_monitors() -> List[str]:
    """
    Return a sorted list of display names known to the system using XCB RandR.
    Prepends 'primary' and 'all'.
    """
    conn = open_xcb_connection()
    if not conn:
        logger.warning("Cannot enumerate monitors: no XCB connection")
        return ["primary", "all"]
    try:
        names = sorted(_list_monitor_names(conn))
    except Exception as e:
        logger.warning(f"Could not enumerate monitors: {e}")
        names = []
    finally:
        close_xcb_connection(conn)
    return ["primary", "all"] + names


def _get_screen(screen_spec: str) -> QScreen:
    """
    Return a single QScreen based on the specification.
    - 'primary'          - primary screen
    - integer as string  - screen at that index (e.g., '0')
    - screen name        - case-insensitive substring match (e.g., 'HDMI-1')
    Raises ValueError if no matching screen is found.
    Note: The 'all' spec is not handled here: _get_virtual_desktop() handles that.
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
            f"Multiple screens match '{screen_spec}': {[s.name() for s in matches]}, using first"
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


def _get_screen_geometry(
    q_screen: QScreen, scale_factor: Optional[float] = None
) -> Tuple[int, int, int, int, float]:
    """
    Return (x, y, width, height) of the given QScreen.
    If scale_factor is None, it is computed automatically via get_scale_factor().
    """
    geom = q_screen.geometry()
    x, y = geom.x(), geom.y()
    logical_w, logical_h = geom.width(), geom.height()

    if scale_factor is None:
        scale_factor: float = q_screen.devicePixelRatio()

    return x, y, logical_w, logical_h, scale_factor


def get_base_geometry(
    monitor_spec: str, scale_factor: Optional[float] = None
) -> Tuple[int, int, int, int, float]:
    """
    Return (x, y, logical_width, logical_height, scale_factor) for the
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
