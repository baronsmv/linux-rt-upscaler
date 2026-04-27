import logging
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import xcffib
import xcffib.xproto

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Information about an X11 window."""

    handle: int  # X11 window ID (XID)
    width: int  # Window width in pixels
    height: int  # Window height in pixels
    title: str  # Window title (UTF-8 or fallback)

    @property
    def size(self) -> Tuple[int, int]:
        """Return (width, height) as a tuple."""
        return self.width, self.height


class AtomCache:
    """
    Caches interned atoms for an XCB connection.

    Atom interning is a round-trip to the X server; caching avoids repeated
    round trips for the same atom name.
    """

    def __init__(self, conn: xcffib.Connection) -> None:
        """
        Initialize the cache with an XCB connection.

        Args:
            conn: The XCB connection to use for interning atoms.
        """
        self._conn = conn
        self._cache: Dict[str, int] = {}

    def get(self, name: str) -> int:
        """
        Return the atom ID for the given name, interning if necessary.

        Args:
            name: The atom name (e.g., "_NET_WM_NAME").

        Returns:
            The atom ID (integer).
        """
        if name not in self._cache:
            cookie = self._conn.core.InternAtom(False, len(name), name)
            reply = cookie.reply()
            self._cache[name] = reply.atom
            logger.debug(f"Interned atom '{name}' -> {reply.atom}")
        return self._cache[name]


def get_window_geometry(
    conn: xcffib.Connection, win: int
) -> Optional[Tuple[int, int, int, int]]:
    """
    Get the geometry (x, y, width, height) of a window relative to its parent.

    Args:
        conn: XCB connection.
        win: X11 window ID.

    Returns:
        A tuple (x, y, width, height) if successful, otherwise None.
        Note: x and y are relative to the parent window, not the root.
    """
    try:
        geom = conn.core.GetGeometry(win).reply()
        if geom:
            return geom.x, geom.y, geom.width, geom.height
    except Exception as e:
        logger.debug(f"Failed to get geometry for window {win:#x}: {e}")
    return None


def get_window_name(
    conn: xcffib.Connection, win: int, atoms: AtomCache
) -> Optional[str]:
    """
    Retrieve the window title using _NET_WM_NAME (UTF-8) or fallback to WM_NAME.

    Args:
        conn: XCB connection.
        win: X11 window ID.
        atoms: AtomCache instance for the connection.

    Returns:
        Window title as a string, or None if no title is available.
    """
    # Prefer _NET_WM_NAME (UTF-8)
    cookie = conn.core.GetProperty(
        False,
        win,
        atoms.get("_NET_WM_NAME"),
        atoms.get("UTF8_STRING"),
        0,
        1024,
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        try:
            # xcffib returns a buffer; use .buf() or .to_string()
            raw = reply.value.buf()
            return raw.decode("utf-8", errors="ignore").strip()
        except (UnicodeDecodeError, AttributeError):
            pass

    # Fallback to WM_NAME (legacy, usually Latin-1)
    cookie = conn.core.GetProperty(
        False,
        win,
        atoms.get("WM_NAME"),
        atoms.get("STRING"),
        0,
        1024,
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        try:
            raw = reply.value.buf()
            return raw.decode("latin1", errors="ignore").strip()
        except (UnicodeDecodeError, AttributeError):
            pass

    return None


def get_window_class(
    conn: xcffib.Connection, win: int, atoms: AtomCache
) -> Optional[Tuple[str, str]]:
    """
    Retrieve the WM_CLASS property.

    WM_CLASS contains two strings: instance name and class name, separated by a null byte.

    Args:
        conn: XCB connection.
        win: X11 window ID.
        atoms: AtomCache instance.

    Returns:
        A tuple (instance, class) if found, otherwise None.
    """
    cookie = conn.core.GetProperty(
        False,
        win,
        atoms.get("WM_CLASS"),
        atoms.get("STRING"),
        0,
        256,
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        data = reply.value.buf()
        try:
            # Split on null byte; WM_CLASS is two null-terminated strings
            strings = data.decode("latin1").split("\x00")
            if len(strings) >= 2:
                return strings[0], strings[1]
        except (UnicodeDecodeError, AttributeError):
            pass
    return None


def get_window_pid(
    conn: xcffib.Connection, win: int, atoms: AtomCache
) -> Optional[int]:
    """
    Retrieve the _NET_WM_PID property of a window.

    Args:
        conn: XCB connection.
        win: X11 window ID.
        atoms: AtomCache instance.

    Returns:
        PID as an integer, or None if not set or invalid.
    """
    cookie = conn.core.GetProperty(
        False,
        win,
        atoms.get("_NET_WM_PID"),
        xcffib.xproto.Atom.CARDINAL,
        0,
        1,
    )
    reply = cookie.reply()
    if reply and reply.value_len >= 4:
        # _NET_WM_PID is a 32-bit unsigned integer
        raw = reply.value.buf()
        # xcffib may return a buffer or bytes; unpack as little-endian
        return int.from_bytes(raw[:4], byteorder="little")
    return None


def is_viewable(conn: xcffib.Connection, win: int) -> bool:
    """
    Determine if a window is viewable (i.e., mapped and not iconified).

    Args:
        conn: XCB connection.
        win: X11 window ID.

    Returns:
        True if the window is viewable (map_state == MapState.Viewable),
        False otherwise (including errors).
    """
    try:
        attr = conn.core.GetWindowAttributes(win).reply()
        if attr is None:
            return False
        # MapState: 0 = Unmapped, 1 = Unviewable, 2 = Viewable
        return attr.map_state == xcffib.xproto.MapState.Viewable
    except Exception:
        return False


def is_application_window(
    conn: xcffib.Connection,
    win: int,
    atoms: AtomCache,
    min_width: int = 200,
    min_height: int = 200,
) -> bool:
    """
    Heuristic to decide if a window is a normal application window.

    Checks:
      - Viewable (mapped and not iconified).
      - Minimum size (default 200x200).
      - Title - exclude small windows with "xwayland"/"wayland" in the name.
      - Window type - must be NORMAL (or no type but then class check).
      - Exclude known non-application types (DESKTOP, DOCK, TOOLBAR, MENU, UTILITY, SPLASH).
      - If no window type, exclude windows with WM_CLASS containing "xwayland".

    Args:
        conn: XCB connection.
        win: X11 window ID.
        atoms: AtomCache instance.
        min_width: Minimum width to consider.
        min_height: Minimum height to consider.

    Returns:
        True if considered an application window, False otherwise.
    """
    if not is_viewable(conn, win):
        return False

    geom = get_window_geometry(conn, win)
    if geom is None:
        return False
    _, _, w, h = geom
    if w < min_width or h < min_height:
        return False

    # Exclude XWayland helpers by title pattern
    name = get_window_name(conn, win, atoms)
    if name and ("xwayland" in name.lower() or "wayland" in name.lower()):
        # XWayland helpers are typically small (e.g., 200x200)
        if w < 300 and h < 300:
            logger.debug(f"Excluding XWayland helper window '{name}' ({w}x{h})")
            return False

    # Window type check via _NET_WM_WINDOW_TYPE
    cookie = conn.core.GetProperty(
        False,
        win,
        atoms.get("_NET_WM_WINDOW_TYPE"),
        xcffib.xproto.Atom.ATOM,
        0,
        16,
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
        klass = get_window_class(conn, win, atoms)
        if klass:
            instance, cls = klass
            if "xwayland" in instance.lower() or "xwayland" in cls.lower():
                return False

    return True


def enumerate_all_windows(conn: xcffib.Connection) -> List[int]:
    """
    Recursively collect all window IDs from the root window downwards.

    This function uses recursion; for deep window trees, consider an iterative
    stack if recursion depth becomes a problem.

    Args:
        conn: XCB connection.

    Returns:
        List of X11 window IDs (integers).
    """
    root = conn.get_setup().roots[0].root
    result: List[int] = []

    def recurse(win: int) -> None:
        result.append(win)
        try:
            tree = conn.core.QueryTree(win).reply()
            if tree:
                for child in tree.children:
                    recurse(child)
        except Exception:
            # Window may have disappeared; skip
            pass

    recurse(root)
    return result
