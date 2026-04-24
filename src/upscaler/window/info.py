import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List

import xcffib
import xcffib.xproto
from xcffib.xproto import Window

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
    """Caches interned atoms for an XCB connection."""

    def __init__(self, conn: xcffib.Connection) -> None:
        self._conn = conn
        self._cache: dict[str, int] = {}

    def get(self, name: str) -> int:
        """Return the atom ID for the given name, interning if necessary."""
        if name not in self._cache:
            cookie = self._conn.core.InternAtom(False, len(name), name)
            reply = cookie.reply()
            self._cache[name] = reply.atom
            logger.debug(f"Interned atom '{name}' -> {reply.atom}")
        return self._cache[name]


def get_window_geometry(
    conn: xcffib.Connection, win: Window
) -> Optional[Tuple[int, int, int, int]]:
    """Return (x, y, width, height) of a window, or None on error."""
    try:
        geom = conn.core.GetGeometry(win).reply()
        if geom:
            return geom.x, geom.y, geom.width, geom.height
    except Exception as e:
        logger.debug(f"Failed to get geometry for window {win}: {e}")
    return None


def get_window_name(
    conn: xcffib.Connection, win: Window, atoms: AtomCache
) -> Optional[str]:
    """Retrieve the window title using _NET_WM_NAME or WM_NAME."""
    # Prefer _NET_WM_NAME (UTF-8)
    cookie = conn.core.GetProperty(
        False, win, atoms.get("_NET_WM_NAME"), atoms.get("UTF8_STRING"), 0, 1024
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        try:
            # xcffib value is a buffer; use .buf() or .to_bytes()
            return reply.value.buf().decode("utf-8", errors="ignore").strip()
        except (UnicodeDecodeError, AttributeError):
            pass

    # Fallback to WM_NAME
    cookie = conn.core.GetProperty(
        False, win, atoms.get("WM_NAME"), atoms.get("STRING"), 0, 1024
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        try:
            return reply.value.buf().decode("latin1", errors="ignore").strip()
        except (UnicodeDecodeError, AttributeError):
            pass

    return None


def get_window_class(
    conn: xcffib.Connection, win: Window, atoms: AtomCache
) -> Optional[Tuple[str, str]]:
    """Return (instance, class) from WM_CLASS property."""
    cookie = conn.core.GetProperty(
        False, win, atoms.get("WM_CLASS"), atoms.get("STRING"), 0, 256
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        data = reply.value.buf()
        try:
            strings = data.decode("latin1").split("\x00")
            if len(strings) >= 2:
                return strings[0], strings[1]
        except UnicodeDecodeError:
            pass
    return None


def get_window_pid(
    conn: xcffib.Connection, win: Window, atoms: AtomCache
) -> Optional[int]:
    """Return the PID of the window via _NET_WM_PID."""
    cookie = conn.core.GetProperty(
        False, win, atoms.get("_NET_WM_PID"), xcffib.xproto.Atom.CARDINAL, 0, 1
    )
    reply = cookie.reply()
    if reply and reply.value_len >= 4:
        # _NET_WM_PID is a CARDINAL (32-bit)
        return int.from_bytes(reply.value.buf()[:4], byteorder="little")
    return None


def is_viewable(conn: xcffib.Connection, win: Window) -> bool:
    """Check if the window is mapped (viewable)."""
    try:
        attr = conn.core.GetWindowAttributes(win).reply()
        return attr is not None and attr.map_state == xcffib.xproto.MapState.VIEWABLE
    except Exception:
        return False


def is_application_window(
    conn: xcffib.Connection,
    win: Window,
    atoms: AtomCache,
    min_width: int = 200,
    min_height: int = 200,
) -> bool:
    """Heuristic to decide if a window is a normal application window."""
    if not is_viewable(conn, win):
        return False

    geom = get_window_geometry(conn, win)
    if geom is None:
        return False
    _, _, w, h = geom
    if w < min_width or h < min_height:
        return False

    # Check window type via _NET_WM_WINDOW_TYPE
    cookie = conn.core.GetProperty(
        False, win, atoms.get("_NET_WM_WINDOW_TYPE"), xcffib.xproto.Atom.ATOM, 0, 16
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        data = reply.value.buf()
        atom_list = list(struct.unpack(f"<{len(data)//4}I", data))
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
                return False
        if not is_normal:
            return False
    else:
        # No type property - check class to exclude XWayland helpers
        win_class = get_window_class(conn, win, atoms)
        if win_class:
            instance, cls = win_class
            if "xwayland" in instance.lower() or "xwayland" in cls.lower():
                return False

    return True


def enumerate_all_windows(conn: xcffib.Connection) -> List[Window]:
    """Recursively collect all windows (including children) from the root."""
    root = conn.get_setup().roots[0].root
    result: List[Window] = []

    def recurse(win: Window) -> None:
        result.append(win)
        try:
            tree = conn.core.QueryTree(win).reply()
            if tree:
                for child in tree.children:
                    recurse(child)
        except Exception:
            pass  # window may have disappeared

    recurse(root)
    return result
