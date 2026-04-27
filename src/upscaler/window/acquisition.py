import logging
import subprocess
import sys
import time
from typing import List, Optional, Tuple, Set

import psutil
import xcffib

from .display import open_xcb_connection, close_xcb_connection
from .info import (
    WindowInfo,
    AtomCache,
    get_window_geometry,
    get_window_name,
    get_window_class,
    get_window_pid,
    is_viewable,
    is_application_window,
    enumerate_all_windows,
)
from ..config import Config

logger = logging.getLogger(__name__)


def _list_windows() -> List[WindowInfo]:
    """Enumerate all visible application windows using _NET_CLIENT_LIST."""
    logger.info("Starting window enumeration")
    conn = open_xcb_connection()
    if not conn:
        return []

    atoms = AtomCache(conn)
    root = conn.get_setup().roots[0].root

    # Get top-level client windows
    cookie = conn.core.GetProperty(
        False, root, atoms.get("_NET_CLIENT_LIST"), xcffib.xproto.Atom.WINDOW, 0, 1024
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        # Convert buffer to list of window IDs
        data = reply.value.buf()
        window_ids = list(struct.unpack(f"<{len(data)//4}I", data))
        windows = window_ids
    else:
        logger.warning(
            "No _NET_CLIENT_LIST property; falling back to recursive enumeration."
        )
        windows = enumerate_all_windows(conn)

    result: List[WindowInfo] = []
    for win in windows:
        try:
            if not is_application_window(conn, win, atoms):
                continue

            name = get_window_name(conn, win, atoms)
            if not name:
                continue

            geom = get_window_geometry(conn, win)
            if geom is None:
                continue
            _, _, w, h = geom
            result.append(WindowInfo(win, w, h, name))
            logger.info(f"Found application window: {name} ({w}x{h})")
        except Exception as e:
            logger.debug(f"Error processing window {win}: {e}")

    close_xcb_connection(conn)
    logger.info(f"Enumeration complete, found {len(result)} windows")
    return result


def get_active_window() -> Optional[WindowInfo]:
    """Return WindowInfo for the currently active window."""
    conn = open_xcb_connection()
    if not conn:
        return None

    try:
        atoms = AtomCache(conn)
        root = conn.get_setup().roots[0].root

        cookie = conn.core.GetProperty(
            False,
            root,
            atoms.get("_NET_ACTIVE_WINDOW"),
            xcffib.xproto.Atom.WINDOW,
            0,
            1,
        )
        reply = cookie.reply()
        if not reply or not reply.value_len:
            return None

        data = reply.value.buf()
        if len(data) < 4:
            return None
        active_win = int.from_bytes(data[:4], byteorder="little")
        if active_win == 0:
            return None

        geom = get_window_geometry(conn, active_win)
        if geom is None:
            return None
        _, _, w, h = geom

        name = get_window_name(conn, active_win, atoms) or "unknown"
        return WindowInfo(active_win, w, h, name)
    finally:
        close_xcb_connection(conn)


def _find_by_pid(
    pid: int,
    pid_timeout: int = 5,
    class_hint: Optional[str] = None,
    class_timeout: int = 5,
    total_timeout: Optional[int] = 60,
    starting_phase: int = 1,
) -> WindowInfo:
    """Locate a window by process ID (and optionally by class hint)."""
    logger.info(
        f"find_by_pid called with pid={pid}, class_hint={class_hint}, "
        f"pid_timeout={pid_timeout}, class_timeout={class_timeout}, "
        f"total_timeout={total_timeout}, starting_phase={starting_phase}"
    )

    try:
        proc = psutil.Process(pid)
        pids: Set[int] = {pid} | {child.pid for child in proc.children(recursive=True)}
        logger.debug(f"Process tree for PID {pid}: {pids}")
    except psutil.NoSuchProcess:
        logger.warning(f"Process {pid} not found; using only the provided PID.")
        pids = {pid}

    class_hint_lower = class_hint.lower() if class_hint else None
    phase = starting_phase
    overall_start = time.time()

    def check_total_timeout() -> None:
        if total_timeout is not None and (time.time() - overall_start) > total_timeout:
            raise TimeoutError(
                f"No matching window found within total timeout of {total_timeout} seconds"
            )

    conn = open_xcb_connection()
    if not conn:
        raise RuntimeError("Failed to open XCB connection")

    atoms = AtomCache(conn)

    try:
        while True:
            check_total_timeout()
            phase_start = time.time()

            if phase == 1:
                logger.info(f"Phase 1: Trying PID+class for {pid_timeout} seconds...")
                while time.time() - phase_start < pid_timeout:
                    check_total_timeout()
                    windows = enumerate_all_windows(conn)
                    for win in windows:
                        if not is_viewable(conn, win):
                            continue

                        win_pid = get_window_pid(conn, win, atoms)
                        if win_pid is None or win_pid not in pids:
                            continue

                        if class_hint_lower:
                            klass = get_window_class(conn, win, atoms)
                            if not klass:
                                continue
                            instance, cls = klass
                            if not (
                                class_hint_lower in instance.lower()
                                or class_hint_lower in cls.lower()
                            ):
                                continue

                        geom = get_window_geometry(conn, win)
                        if geom is None:
                            continue
                        _, _, w, h = geom
                        name = get_window_name(conn, win, atoms) or "unknown"
                        logger.info(f"Found window in phase 1: {name}")
                        return WindowInfo(win, w, h, name)

                    time.sleep(0.2)

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
                    windows = enumerate_all_windows(conn)
                    for win in windows:
                        if not is_viewable(conn, win):
                            continue

                        if class_hint_lower:
                            klass = get_window_class(conn, win, atoms)
                            if not klass:
                                continue
                            instance, cls = klass
                            if not (
                                class_hint_lower in instance.lower()
                                or class_hint_lower in cls.lower()
                            ):
                                continue

                            geom = get_window_geometry(conn, win)
                            if geom is None:
                                continue
                            _, _, w, h = geom
                            name = get_window_name(conn, win, atoms) or "unknown"
                            logger.info(f"Found window in phase 2: {name}")
                            return WindowInfo(win, w, h, name)

                    time.sleep(0.2)

                logger.info("Phase 2 timed out, restarting phase 1.")
                phase = 1

    finally:
        close_xcb_connection(conn)


def _launch_and_find_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """Launch the program and find its window."""
    if not config.program:
        logger.error("No program specified in config")
        return None, None

    program_name = config.program[0]
    print(f"Launching: {' '.join(config.program)}")
    proc = subprocess.Popen(config.program)

    print("Waiting for window...")
    try:
        win_info = _find_by_pid(
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


def _select_window_interactive(windows: List[WindowInfo]) -> Optional[WindowInfo]:
    """Interactively let the user choose a window."""
    windows.sort(key=lambda w: w.title.lower())
    print("\nAvailable windows:")
    for i, w in enumerate(windows):
        print(f"{i:3d}: {w.title} ({w.width}x{w.height})")

    while True:
        try:
            choice = input("\nEnter window number (or 'q' to quit): ").strip()
            if choice.lower() == "q":
                logger.info("User quit window selection")
                return None
            idx = int(choice)
            if 0 <= idx < len(windows):
                selected = windows[idx]
                logger.info(f"User selected window {idx}: {selected.title}")
                return selected
            print(f"Please enter a number between 0 and {len(windows)-1}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def _get_active_window_after_delay(config: Config) -> Optional[WindowInfo]:
    """Wait target_delay seconds and return the active window."""
    if config.log_level != "ERROR":
        print(
            f"No program specified. Will scale the currently active window in {config.target_delay} seconds..."
        )
    try:
        time.sleep(config.target_delay)
    except KeyboardInterrupt:
        sys.exit(0)

    try:
        win_info = get_active_window()
        if not win_info:
            print("No visible windows found.")
            sys.exit(1)
        logger.info(f"Got active window: {win_info.title}")
        return win_info
    except RuntimeError as e:
        logger.error(f"Failed to get active window: {e}")
        return None


def acquire_target_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """Determine which window to upscale based on config."""
    start_time = time.perf_counter()
    if config.select:
        logger.info("Selecting window interactively.")
        print("Enumerating open windows...")
        windows = _list_windows()
        if not windows:
            logger.error("No visible windows found")
            print("No visible windows found.")
            return None, None

        win_info = _select_window_interactive(windows)
        if win_info is None:
            return None, None
        if config.log_level != "ERROR":
            print(f"Selected: {win_info.title}")
        logger.info(
            f"Window acquired interactively in {time.perf_counter() - start_time:.2f}s"
        )
        return win_info, None

    elif config.program:
        logger.info(f"Launching and finding window for program: {config.program}")
        result = _launch_and_find_window(config)
        logger.info(
            f"Window acquired via program launch in {time.perf_counter() - start_time:.2f}s"
        )
        return result
    else:
        logger.info(
            f"Acquiring currently active window (waiting {config.target_delay} seconds)"
        )
        win_info = _get_active_window_after_delay(config)
        if win_info:
            logger.info(
                f"Active window acquired in {time.perf_counter() - start_time:.2f}s"
            )
        return win_info, None
