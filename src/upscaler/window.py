import logging
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, Set
from typing import List, Optional, Tuple

import psutil
from Xlib import X
from Xlib.display import Display
from Xlib.error import XError
from Xlib.xobject.drawable import Window
from ewmh import EWMH

from .utils.config import Config

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Immutable information about an X11 window."""

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


def list_windows() -> List[WindowInfo]:
    """
    Enumerate all visible application windows using _NET_CLIENT_LIST.
    Returns a list of WindowInfo objects.
    """
    logger.info("Starting window enumeration")
    display = Display()
    atoms = AtomCache(display)
    root = display.screen().root

    # Get top‑level client windows
    client_list_prop = root.get_full_property(atoms.get("_NET_CLIENT_LIST"), 0)
    if not client_list_prop:
        logger.warning(
            "No _NET_CLIENT_LIST property found; falling back to recursive enumeration."
        )
        windows = enumerate_all_windows(display)
    else:
        window_ids = client_list_prop.value  # list of ints
        windows = [display.create_resource_object("window", wid) for wid in window_ids]

    result: List[WindowInfo] = []
    for win in windows:
        try:
            if not is_application_window(win, atoms):
                continue

            name = get_window_name(win, atoms)
            if not name:
                logger.debug(
                    f"Window {win.id} passed filters but has no name, skipping"
                )
                continue

            geom = get_window_geometry(win)
            if geom is None:
                continue
            _, _, w, h = geom
            result.append(WindowInfo(win.id, w, h, name))
            logger.info(f"Found application window: {name} ({w}x{h})")
        except XError as e:
            logger.debug(
                f"XError while processing window {getattr(win, 'id', '?')}: {e}"
            )

    display.close()
    logger.info(f"Enumeration complete, found {len(result)} windows")
    return result


def get_active_window() -> WindowInfo:
    """Return WindowInfo for the currently active window."""
    logger.info("Getting active window")
    display = Display()
    atoms = AtomCache(display)
    ewmh = EWMH(display)

    active = ewmh.getActiveWindow()
    if not active:
        display.close()
        raise RuntimeError("No active window found")

    geom = get_window_geometry(active)
    if geom is None:
        display.close()
        raise RuntimeError("Failed to get geometry of active window")
    _, _, w, h = geom

    name = get_window_name(active, atoms) or "unknown"
    info = WindowInfo(active.id, w, h, name)
    display.close()
    logger.info(f"Active window: {info.title} ({info.width}x{info.height})")
    return info


def find_by_pid(
    pid: int,
    pid_timeout: int = 5,
    class_hint: Optional[str] = None,
    class_timeout: int = 5,
    total_timeout: Optional[int] = 60,
    starting_phase: int = 1,
) -> WindowInfo:
    """
    Locate a window by process ID (and optionally by class hint) using a two‑phase search.

    The search alternates between:
      1. Phase 1: look for windows whose PID matches the process tree,
         and optionally also check the class hint.
      2. Phase 2: if a class hint is given, look purely by class hint
         (ignoring PID) for `class_timeout` seconds.

    Phases repeat until a window is found or `total_timeout` expires.

    Returns a WindowInfo as soon as a matching, viewable window is found.
    Raises TimeoutError if no window appears within the total timeout.
    """
    logger.info(
        f"find_by_pid called with pid={pid}, class_hint={class_hint}, "
        f"pid_timeout={pid_timeout}, class_timeout={class_timeout}, "
        f"total_timeout={total_timeout}, starting_phase={starting_phase}"
    )

    # Gather all PIDs in the process tree
    try:
        proc = psutil.Process(pid)
        pids: Set[int] = {pid} | {child.pid for child in proc.children(recursive=True)}
        logger.debug(f"Process tree for PID {pid}: {pids}")
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} not found; using only the provided PID.")
        pids = {pid}

    class_hint_lower = class_hint.lower() if class_hint else None
    phase = starting_phase  # 1 = PID+class, 2 = pure class

    overall_start = time.time()

    # Helper to enforce total timeout
    def check_total_timeout() -> None:
        if total_timeout is not None and (time.time() - overall_start) > total_timeout:
            raise TimeoutError(
                f"No matching window found within total timeout of {total_timeout} seconds"
            )

    # Single Display for the entire search (more efficient)
    display = Display()
    atoms = AtomCache(display)
    ewmh = EWMH(display)

    try:
        while True:
            check_total_timeout()
            phase_start = time.time()

            if phase == 1:
                # Phase 1: search by PID (optionally also check class)
                logger.info(f"Phase 1: Trying PID+class for {pid_timeout} seconds...")
                while time.time() - phase_start < pid_timeout:
                    check_total_timeout()
                    windows = enumerate_all_windows(display)
                    for win in windows:
                        if not is_viewable(win):
                            continue

                        # PID check
                        win_pid = get_window_pid(win, ewmh)
                        if win_pid is None or win_pid not in pids:
                            continue

                        # Optional class check (if hint provided)
                        if class_hint_lower:
                            klass = get_window_class(win, atoms)
                            if not klass:
                                continue
                            instance, cls = klass
                            if not (
                                class_hint_lower in instance.lower()
                                or class_hint_lower in cls.lower()
                            ):
                                continue

                        # Match found
                        geom = get_window_geometry(win)
                        if geom is None:
                            continue
                        _, _, w, h = geom
                        name = get_window_name(win, atoms) or "unknown"
                        logger.info(f"Found window in phase 1: {name}")
                        return WindowInfo(win.id, w, h, name)

                    time.sleep(0.2)

                # Phase 1 timed out
                if class_hint_lower:
                    phase = 2
                    logger.info(
                        "Phase 1 timed out, switching to phase 2 (pure class search)."
                    )
                else:
                    logger.info(
                        "Phase 1 timed out, restarting (no class hint available)."
                    )

            else:  # phase == 2
                logger.info(
                    f"Phase 2: Trying pure class hint for {class_timeout} seconds..."
                )
                while time.time() - phase_start < class_timeout:
                    check_total_timeout()
                    windows = enumerate_all_windows(display)
                    for win in windows:
                        if not is_viewable(win):
                            continue

                        # Class check only
                        if class_hint_lower:
                            klass = get_window_class(win, atoms)
                            if not klass:
                                continue
                            instance, cls = klass
                            if not (
                                class_hint_lower in instance.lower()
                                or class_hint_lower in cls.lower()
                            ):
                                continue

                            geom = get_window_geometry(win)
                            if geom is None:
                                continue
                            _, _, w, h = geom
                            name = get_window_name(win, atoms) or "unknown"
                            logger.info(f"Found window in phase 2: {name}")
                            return WindowInfo(win.id, w, h, name)

                    time.sleep(0.2)

                # Phase 2 timed out – go back to phase 1
                logger.info("Phase 2 timed out, restarting phase 1.")
                phase = 1

    finally:
        display.close()
        logger.debug("Closed X display at end of search")


def launch_and_find_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """
    Launch the program from config.program and use find_by_pid to locate its window.
    Returns (WindowInfo, Popen) on success, or (None, None) on failure/timeout.
    """
    if not config.program:
        logger.error("No program specified in config")
        return None, None

    program_name = config.program[0]
    print(f"Launching: {' '.join(config.program)}")
    proc = subprocess.Popen(config.program)

    print("Waiting for window...")
    try:
        win_info = find_by_pid(
            proc.pid,
            pid_timeout=config.pid_timeout,
            class_hint=program_name,
            class_timeout=config.class_timeout,
            total_timeout=config.total_timeout,
            starting_phase=config.starting_phase,
        )
        logger.info(f"Found window for PID {proc.pid}: {win_info.title}")
        return win_info, proc
    except TimeoutError as e:
        logger.error(f"Timeout while waiting for window: {e}")
        print(e)
        proc.terminate()
        proc.wait()
        return None, None


def get_active_window_after_delay(config: Config) -> Optional[WindowInfo]:
    """
    Wait target_delay seconds and then return the currently active window.
    """
    if config.log_level != "ERROR":
        print(
            f"No program specified. Will scale the currently active window in {config.target_delay} seconds..."
        )
    time.sleep(config.target_delay)
    try:
        win_info = get_active_window()
        logger.info(f"Got active window: {win_info.title}")
        return win_info
    except RuntimeError as e:
        logger.error(f"Failed to get active window: {e}")
        print(e)
        return None
