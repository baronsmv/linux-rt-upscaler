import ctypes
import logging
from typing import Dict, Optional, Tuple, List

from PySide6.QtGui import QGuiApplication
from Xlib import X
from Xlib.display import Display
from Xlib.error import XError
from Xlib.xobject.drawable import Window
from ewmh import EWMH

logger = logging.getLogger(__name__)


def _x_error_handler(error, request) -> None:
    """
    Custom X error handler that logs at DEBUG level and suppresses stderr.
    """
    if hasattr(error, "get_text"):
        error_text = error.get_text()
    else:
        error_text = str(error)
    logger.debug(f"X error: {error_text} (request: {request})")


def open_x_display() -> Optional[Display]:
    """
    Open an X11 display and install a custom error handler.
    Returns a Display object, or None if opening fails.
    """
    try:
        disp = Display()
        disp.set_error_handler(_x_error_handler)
        logger.debug("Opened X display with custom error handler.")
        return disp
    except Exception as e:
        logger.error(f"Failed to open X display: {e}", exc_info=True)
        return None


def close_x_display(disp: Optional[Display]) -> None:
    """Safely close an X11 display."""
    if disp is not None:
        try:
            disp.close()
            logger.debug("Closed X display.")
        except Exception as e:
            logger.warning(f"Error closing X display: {e}")


def get_display(allow_fallback: bool = True) -> int:
    """
    Return the X11 Display pointer used by Qt as an integer.
    If Qt's display cannot be obtained and allow_fallback is True,
    fall back to opening a new X11 connection via XOpenDisplay (with a warning).
    """
    display_ptr = 0
    methods_tried = []

    # Method 1: Qt6 native interface (via application instance)
    try:
        app = QGuiApplication.instance()
        if app is not None:
            native = app.nativeInterface()
            if native is not None and hasattr(native, "display"):
                ptr = native.display()
                if ptr is not None and ptr != 0:
                    display_ptr = int(ptr)
                    logger.debug("Got X11 display via Qt6 native interface")
                    methods_tried.append("Qt6_native")
    except Exception as e:
        logger.debug(f"Qt6 native interface failed: {e}")

    # Method 2: QX11Info (Qt5 compatibility)
    if display_ptr == 0:
        try:
            from PySide6.QtX11Extras import QX11Info

            ptr = QX11Info.display()
            if ptr != 0:
                display_ptr = int(ptr)
                logger.debug("Got X11 display via QX11Info")
                methods_tried.append("QX11Info")
        except ImportError:
            logger.debug("QX11Info not available (normal on Qt6)")
        except Exception as e:
            logger.debug(f"QX11Info failed: {e}")

    # Method 3: Fallback to XOpenDisplay (if allowed)
    if display_ptr == 0 and allow_fallback:
        logger.warning(
            "Falling back to XOpenDisplay – this may cause issues with Vulkan swapchain"
        )
        try:

            xlib = ctypes.cdll.LoadLibrary("libX11.so")
            xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
            xlib.XOpenDisplay.restype = ctypes.c_void_p
            ptr = xlib.XOpenDisplay(None)
            if ptr != 0:
                display_ptr = int(ptr)
                logger.debug(f"Opened X display via XOpenDisplay: {display_ptr}")
                methods_tried.append("XOpenDisplay")
            else:
                logger.error("XOpenDisplay returned NULL")
        except Exception as e:
            logger.error(f"XOpenDisplay failed: {e}")

    if display_ptr == 0:
        raise RuntimeError(
            f"Cannot obtain X11 display (tried: {', '.join(methods_tried) or 'none'}). "
            "Is X11 running and QT_QPA_PLATFORM=xcb set?"
        )

    return display_ptr


class AtomCache:
    """Caches interned atoms for a given X display."""

    def __init__(self, display: Display) -> None:
        self._display = display
        self._cache: Dict[str, int] = {}

    def get(self, name: str) -> int:
        """Return the atom ID for the given name, interning if necessary."""
        if name not in self._cache:
            self._cache[name] = self._display.intern_atom(name)
            logger.debug(f"Interned atom '{name}' -> {self._cache[name]}")
        return self._cache[name]


def get_window_geometry(window: Window) -> Optional[Tuple[int, int, int, int]]:
    """
    Safely get geometry (x, y, width, height) of a window.
    Returns None on X error.
    """
    try:
        geom = window.get_geometry()
        return geom.x, geom.y, geom.width, geom.height
    except XError as e:
        logger.debug(f"Failed to get geometry for window {window.id}: {e}")
        return None


def get_window_name(window: Window, atoms: AtomCache) -> Optional[str]:
    """
    Retrieve the window title using _NET_WM_NAME or WM_NAME.
    Returns None if unavailable.
    """
    try:
        # Prefer _NET_WM_NAME (UTF‑8)
        name_prop = window.get_full_property(atoms.get("_NET_WM_NAME"), 0)
        if name_prop:
            return name_prop.value.decode("utf-8", errors="ignore").strip()
        # Fallback to WM_NAME (legacy)
        name_prop = window.get_full_property(atoms.get("WM_NAME"), 0)
        if name_prop:
            return name_prop.value.decode("latin1", errors="ignore").strip()
    except (XError, TypeError, UnicodeDecodeError) as e:
        logger.debug(f"Error getting name for window {window.id}: {e}")
    return None


def get_window_class(window: Window, atoms: AtomCache) -> Optional[Tuple[str, str]]:
    """
    Return (instance, class) from WM_CLASS property, or None.
    """
    try:
        class_prop = window.get_full_property(atoms.get("WM_CLASS"), 0)
        if class_prop:
            data = class_prop.value
            strings = data.decode("latin1").split("\x00")
            if len(strings) >= 2:
                return strings[0], strings[1]
    except (XError, TypeError, UnicodeDecodeError) as e:
        logger.debug(f"Error getting WM_CLASS for window {window.id}: {e}")
    return None


def get_window_pid(window: Window, ewmh: EWMH) -> Optional[int]:
    """Return the PID of the window using EWMH, if available."""
    try:
        pid_list = ewmh.getWmPid(window)
        if pid_list:
            return pid_list[0]
    except (XError, TypeError) as e:
        logger.debug(f"Error getting PID for window {window.id}: {e}")
    return None


def is_viewable(window: Window) -> bool:
    """Check if the window is mapped (viewable)."""
    try:
        attrs = window.get_attributes()
        return attrs is not None and attrs.map_state == X.IsViewable
    except XError:
        return False


def is_application_window(
    window: Window,
    atoms: AtomCache,
    min_width: int = 200,
    min_height: int = 200,
) -> bool:
    """
    Heuristic to decide if a window is a normal application window.
    Checks size, viewable state, and excludes known non‑application types.
    """
    if not is_viewable(window):
        return False

    geom = get_window_geometry(window)
    if geom is None:
        return False
    _, _, w, h = geom
    if w < min_width or h < min_height:
        logger.debug(f"Window {window.id} too small ({w}x{h})")
        return False

    # Check window type via _NET_WM_WINDOW_TYPE
    type_prop = window.get_full_property(atoms.get("_NET_WM_WINDOW_TYPE"), 0)
    if type_prop:
        atom_list = type_prop.value
        is_normal = False
        for atom in atom_list:
            if atom == atoms.get("_NET_WM_WINDOW_TYPE_NORMAL"):
                is_normal = True
            elif atom in (
                atoms.get("_NET_WM_WINDOW_TYPE_DESKTOP"),
                atoms.get("_NET_WM_WINDOW_TYPE_DOCK"),
                atoms.get("_NET_WM_WINDOW_TYPE_TOOLBAR"),
                atoms.get("_NET_WM_WINDOW_TYPE_MENU"),
                atoms.get("_NET_WM_WINDOW_TYPE_UTILITY"),
                atoms.get("_NET_WM_WINDOW_TYPE_SPLASH"),
            ):
                logger.debug(f"Window {window.id} excluded by type")
                return False
        if not is_normal:
            # If we have a type but it's not normal, reject
            logger.debug(f"Window {window.id} has unknown type, rejecting")
            return False
    else:
        # No type property – check class to exclude XWayland helpers
        klass = get_window_class(window, atoms)
        if klass:
            instance, cls = klass
            if "xwayland" in instance.lower() or "xwayland" in cls.lower():
                logger.debug(f"Window {window.id} is an XWayland helper, rejecting")
                return False

    return True


def enumerate_all_windows(display: Display) -> List[Window]:
    """
    Recursively collect all windows (including children) from the root.
    """
    root = display.screen().root
    result: List[Window] = []

    def recurse(win: Window) -> None:
        result.append(win)
        try:
            children = win.query_tree().children
            for child in children:
                recurse(child)
        except XError:
            pass  # skip windows that disappeared

    recurse(root)
    return result
