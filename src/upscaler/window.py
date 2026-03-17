import logging
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
from typing import Set

import psutil
from Xlib.display import Display
from Xlib.error import XError
from ewmh import EWMH

from .utils.config import Config
from .utils.x11 import (
    AtomCache,
    get_window_geometry,
    get_window_name,
    get_window_class,
    get_window_pid,
    is_viewable,
    is_application_window,
    enumerate_all_windows,
)

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
