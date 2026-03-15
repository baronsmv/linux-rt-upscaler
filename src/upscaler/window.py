import logging
import time
from typing import Optional, List, Set, Dict

import psutil
from Xlib import X
from Xlib.display import Display
from Xlib.error import XError
from Xlib.xobject.drawable import Window
from ewmh import EWMH

logger = logging.getLogger(__name__)


class WindowInfo:
    """Holds information about an X11 window."""

    def __init__(self, handle: int, width: int, height: int, title: str) -> None:
        self.handle = handle
        self.width = width
        self.height = height
        self.title = title
        logger.debug(
            f"WindowInfo created: handle={handle}, {width}x{height}, title='{title}'"
        )

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height


def _get_all_windows(disp: Display) -> List[Window]:
    """Recursively collect all windows (including children) from the root."""
    logger.debug("Starting to collect all windows recursively")
    root = disp.screen().root
    windows: List[Window] = []
    count = 0

    def recurse(win: Window) -> None:
        nonlocal count
        windows.append(win)
        count += 1
        try:
            children = win.query_tree().children
            logger.debug(f"Window {win.id} has {len(children)} children")
            for child in children:
                recurse(child)
        except XError as e:
            logger.warning(f"XError while querying children of window {win.id}: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error while recursing window {win.id}: {e}", exc_info=True
            )

    recurse(root)
    logger.info(f"Collected {count} windows total")
    return windows


def _intern_atoms(disp: Display, atom_names: List[str]) -> Dict[str, int]:
    """Intern a list of atom names and return a dict mapping name -> atom."""
    atoms = {}
    for name in atom_names:
        atoms[name] = disp.intern_atom(name)
        logger.debug(f"Interned atom '{name}' -> {atoms[name]}")
    return atoms


def _check_window_for_match(
    win: Window,
    disp: Display,
    ewmh: EWMH,
    pids: Set[int],
    class_hint_lower: Optional[str],
    check_pid: bool = True,
    check_class: bool = True,
) -> Optional[WindowInfo]:
    """
    Check a single window against PID set and/or class hint.
    Returns a WindowInfo if it matches, otherwise None.
    """
    try:
        attrs = win.get_attributes()
        if not attrs or attrs.map_state != X.IsViewable:
            return None

        # PID check (if enabled)
        if check_pid:
            win_pid_list = ewmh.getWmPid(win)
            if win_pid_list and win_pid_list[0] in pids:
                geom = win.get_geometry()
                name = ewmh.getWmName(win) or "unknown"
                logger.debug(f"Window {win.id} matched by PID")
                return WindowInfo(win.id, geom.width, geom.height, name)

        # Class hint check (if enabled and hint provided)
        if check_class and class_hint_lower:
            class_prop = win.get_full_property(disp.intern_atom("WM_CLASS"), 0)
            if class_prop:
                data = class_prop.value
                strings = data.decode("latin1").split("\x00")
                if len(strings) >= 2:
                    instance, klass = strings[0], strings[1]
                    logger.debug(
                        f"Window {win.id} WM_CLASS: instance='{instance}', class='{klass}'"
                    )
                    if (
                        class_hint_lower in instance.lower()
                        or class_hint_lower in klass.lower()
                    ):
                        geom = win.get_geometry()
                        name = ewmh.getWmName(win) or "unknown"
                        logger.debug(f"Window {win.id} matched by class hint")
                        return WindowInfo(win.id, geom.width, geom.height, name)
    except (XError, TypeError, IndexError) as e:
        logger.debug(f"Error while checking window {getattr(win, 'id', '?')}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in _check_window_for_match: {e}", exc_info=True)

    return None


def list_windows() -> List[WindowInfo]:
    """
    Enumerate all visible X11 application windows and return a list of WindowInfo.
    Filters out panels, desktops, and other non‑normal windows.
    """
    logger.info("Starting window enumeration")

    disp = Display()
    logger.debug(f"Connected to X display {disp.get_display_name()}")
    root = disp.screen().root
    logger.debug(f"Root window ID: {root.id}")

    # Intern all needed atoms at once
    atom_names = [
        "_NET_WM_WINDOW_TYPE",
        "_NET_WM_WINDOW_TYPE_NORMAL",
        "_NET_WM_WINDOW_TYPE_DESKTOP",
        "_NET_WM_WINDOW_TYPE_DOCK",
        "_NET_WM_WINDOW_TYPE_TOOLBAR",
        "_NET_WM_WINDOW_TYPE_MENU",
        "_NET_WM_WINDOW_TYPE_UTILITY",
        "_NET_WM_WINDOW_TYPE_SPLASH",
        "_NET_WM_WINDOW_TYPE_DIALOG",
    ]
    atoms = _intern_atoms(disp, atom_names)

    windows: List[WindowInfo] = []

    def is_application_window(win: Window) -> bool:
        """Return True if the window is a normal application window."""
        try:
            # Must be viewable
            attrs = win.get_attributes()
            if not attrs:
                logger.debug(f"Window {win.id}: no attributes")
                return False
            if attrs.map_state != X.IsViewable:
                logger.debug(
                    f"Window {win.id}: map_state={attrs.map_state} not viewable"
                )
                return False

            # Must have reasonable size
            geom = win.get_geometry()
            if geom.width < 100 or geom.height < 100:
                logger.debug(
                    f"Window {win.id}: geometry {geom.width}x{geom.height} too small"
                )
                return False

            # Check window type
            type_prop = win.get_full_property(atoms["_NET_WM_WINDOW_TYPE"], 0)
            if type_prop:
                atom_list = type_prop.value
                logger.debug(
                    f"Window {win.id} has _NET_WM_WINDOW_TYPE atoms: {atom_list}"
                )
                for atom in atom_list:
                    if atom == atoms["_NET_WM_WINDOW_TYPE_NORMAL"]:
                        logger.debug(f"Window {win.id} is type NORMAL, accepting")
                        return True
                    if atom in (
                        atoms["_NET_WM_WINDOW_TYPE_DESKTOP"],
                        atoms["_NET_WM_WINDOW_TYPE_DOCK"],
                        atoms["_NET_WM_WINDOW_TYPE_TOOLBAR"],
                        atoms["_NET_WM_WINDOW_TYPE_MENU"],
                        atoms["_NET_WM_WINDOW_TYPE_UTILITY"],
                        atoms["_NET_WM_WINDOW_TYPE_SPLASH"],
                    ):
                        logger.debug(f"Window {win.id} is non-normal type, rejecting")
                        return False
                logger.debug(f"Window {win.id} has unknown type atoms, falling through")
                return False
            else:
                logger.debug(
                    f"Window {win.id} has no _NET_WM_WINDOW_TYPE, assuming normal"
                )
        except XError as e:
            logger.warning(f"XError checking window {win.id}: {e}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error checking window {win.id}: {e}", exc_info=True
            )
            return False

        return True

    def recurse(win: Window) -> None:
        try:
            if is_application_window(win):
                # Get name
                name = None
                try:
                    name_prop = win.get_full_property(
                        disp.intern_atom("_NET_WM_NAME"), 0
                    )
                    if name_prop:
                        name = name_prop.value.decode("utf-8", errors="ignore")
                        logger.debug(f"Window {win.id} _NET_WM_NAME: '{name}'")
                except Exception as e:
                    logger.debug(f"Failed to get _NET_WM_NAME for {win.id}: {e}")

                if not name:
                    try:
                        name_prop = win.get_full_property(
                            disp.intern_atom("WM_NAME"), 0
                        )
                        if name_prop:
                            name = name_prop.value.decode("utf-8", errors="ignore")
                            logger.debug(f"Window {win.id} WM_NAME: '{name}'")
                    except Exception as e:
                        logger.debug(f"Failed to get WM_NAME for {win.id}: {e}")

                if name and name.strip():
                    geom = win.get_geometry()
                    winfo = WindowInfo(win.id, geom.width, geom.height, name.strip())
                    windows.append(winfo)
                    logger.info(
                        f"Found application window: {winfo.title} ({winfo.width}x{winfo.height})"
                    )
                else:
                    logger.debug(
                        f"Window {win.id} passed filter but has no name, skipping"
                    )

            # Recurse children
            for child in win.query_tree().children:
                recurse(child)
        except XError as e:
            logger.warning(f"XError during recursion on window {win.id}: {e}")
        except Exception as e:
            logger.error(
                f"Unexpected error in recurse for window {win.id}: {e}", exc_info=True
            )

    recurse(root)
    disp.close()
    logger.info(f"Enumeration complete, found {len(windows)} windows")
    return windows


def find_by_pid(
    pid: int,
    pid_timeout: int = 5,
    class_hint: Optional[str] = None,
    class_timeout: int = 5,
    total_timeout: Optional[int] = 60,
    starting_phase: int = 1,
) -> WindowInfo:
    """
    Loop indefinitely, alternating between:
      1. Searching by PID (and also checking WM_CLASS) for `pid_timeout` seconds.
      2. If `class_hint` is given, searching purely by WM_CLASS for `class_timeout` seconds.
    If `total_timeout` is provided, the search stops after that time and raises TimeoutError.
    Returns a WindowInfo as soon as a matching viewable window is found.
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
    except psutil.NoSuchProcess as e:
        logger.warning(f"Process {pid} not found: {e}. Using only provided PID.")
        pids = {pid}
    logger.info(f"Tracking PIDs: {pids}")

    class_hint_lower = class_hint.lower() if class_hint else None
    phase = starting_phase

    overall_start = time.time()

    # Helper to check total timeout
    def check_total_timeout() -> None:
        if total_timeout is not None and (time.time() - overall_start) > total_timeout:
            logger.error(f"Total timeout {total_timeout}s exceeded")
            raise TimeoutError(
                f"No matching window found within total timeout of {total_timeout} seconds"
            )

    while True:
        check_total_timeout()  # before starting a new phase

        disp = Display()
        logger.debug(f"Opened X display {disp.get_display_name()} for search loop")
        ewmh = EWMH(disp)
        phase_start = time.time()

        if phase == 1:
            # Phase 1: search by PID and class hint
            logger.info(f"Phase 1: Trying PID+class for {pid_timeout} seconds...")
            while time.time() - phase_start < pid_timeout:
                check_total_timeout()

                windows = _get_all_windows(disp)
                logger.debug(f"Phase 1 iteration: checking {len(windows)} windows")
                for win in windows:
                    match = _check_window_for_match(
                        win,
                        disp,
                        ewmh,
                        pids,
                        class_hint_lower,
                        check_pid=True,
                        check_class=(class_hint_lower is not None),
                    )
                    if match:
                        logger.info(f"Found window in phase 1: {match.title}")
                        disp.close()
                        return match
                time.sleep(0.2)

            # Phase 1 timed out – move to phase 2 if class hint exists, otherwise restart
            if class_hint_lower:
                phase = 2
                logger.info(
                    "Phase 1 timed out, switching to phase 2 (pure class search)."
                )
            else:
                logger.info("Phase 1 timed out, restarting (no class hint available).")

        else:  # phase == 2
            # Phase 2: pure class‑based search
            logger.info(
                f"Phase 2: Trying pure class hint for {class_timeout} seconds..."
            )
            while time.time() - phase_start < class_timeout:
                check_total_timeout()

                windows = _get_all_windows(disp)
                logger.debug(f"Phase 2 iteration: checking {len(windows)} windows")
                for win in windows:
                    match = _check_window_for_match(
                        win,
                        disp,
                        ewmh,
                        pids,
                        class_hint_lower,
                        check_pid=False,
                        check_class=True,
                    )
                    if match:
                        logger.info(f"Found window in phase 2: {match.title}")
                        disp.close()
                        return match
                time.sleep(0.2)

            # Phase 2 timed out – go back to phase 1
            logger.info("Phase 2 timed out, restarting phase 1.")
            phase = 1

        disp.close()
        logger.debug("Closed X display at end of phase")


def get_active_window() -> WindowInfo:
    """Return WindowInfo for the currently active window."""
    logger.info("Getting active window")
    disp = Display()
    logger.debug(f"Connected to X display {disp.get_display_name()}")
    ewmh = EWMH(disp)
    active = ewmh.getActiveWindow()
    if not active:
        logger.error("No active window found")
        raise RuntimeError("No active window found")
    geom = active.get_geometry()
    name = ewmh.getWmName(active) or "unknown"
    winfo = WindowInfo(active.id, geom.width, geom.height, name)
    logger.info(f"Active window: {winfo.title} ({winfo.width}x{winfo.height})")
    disp.close()
    return winfo
