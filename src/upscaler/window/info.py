import logging
from dataclasses import dataclass
from typing import Tuple, Dict, Optional, List

from Xlib import X
from Xlib.display import Display
from Xlib.error import XError
from Xlib.xobject.drawable import Window
from ewmh import EWMH

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Information about an X11 window."""

    handle: int
    width: int
    height: int
    title: str

    @property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height


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
