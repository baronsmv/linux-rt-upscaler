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


def _get_physical_resolution(screen_name: str) -> Optional[Tuple[int, int]]:
    """
    Return the physical pixel resolution (width, height) of the monitor
    matching *screen_name* using XCB RandR.
    """
    conn = open_xcb_connection()
    if not conn:
        logger.warning("Cannot get physical resolution: no XCB connection")
        return None
    try:
        randr = _get_randr_connection(conn)
        root = conn.get_setup().roots[0].root
        resources = randr.GetScreenResources(root).reply()
        name_lower = screen_name.lower()

        # First try exact match
        for output_id in resources.outputs:
            output_info = randr.GetOutputInfo(output_id, xcffib.CurrentTime).reply()
            if not output_info or output_info.name_len == 0:
                continue
            output_name = bytes(output_info.name).decode("utf-8")
            if output_name.lower() != name_lower:
                continue

            # Output must be connected and have a CRTC
            if (
                output_info.crtc == xcffib.xproto.Atom._None
                or output_info.connection != 0
            ):
                logger.debug(f"Output {output_name} is disconnected or has no CRTC")
                return None

            crtc_info = randr.GetCrtcInfo(output_info.crtc, xcffib.CurrentTime).reply()
            if crtc_info and crtc_info.width and crtc_info.height:
                return crtc_info.width, crtc_info.height
            else:
                logger.debug(f"CRTC for {output_name} has no valid dimensions")
                return None

        # Fallback to substring match
        for output_id in resources.outputs:
            output_info = randr.GetOutputInfo(output_id, xcffib.CurrentTime).reply()
            if not output_info or output_info.name_len == 0:
                continue
            output_name = bytes(output_info.name).decode("utf-8")
            if name_lower in output_name.lower():
                if output_info.crtc and output_info.connection == 0:
                    crtc_info = randr.GetCrtcInfo(
                        output_info.crtc, xcffib.CurrentTime
                    ).reply()
                    if crtc_info and crtc_info.width and crtc_info.height:
                        logger.debug(
                            f"Substring match: '{screen_name}' -> '{output_name}'"
                        )
                        return crtc_info.width, crtc_info.height
                break

        logger.warning(f"No physical monitor found for screen name '{screen_name}'")
        return None
    except Exception as e:
        logger.error(f"Error querying physical resolution: {e}")
        return None
    finally:
        close_xcb_connection(conn)


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
            f"height scale {scale_h:.3f}, using width scale"
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
