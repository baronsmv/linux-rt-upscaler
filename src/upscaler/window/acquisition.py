import logging
import shutil
import struct
import subprocess
import sys
import time
from typing import List, Optional, Tuple, Set

import psutil
import xcffib
from xcffib.xproto import Window

from .connection import open_xcb_connection, close_xcb_connection
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
    """
    Enumerate all visible application windows using _NET_CLIENT_LIST.

    Returns:
        List of WindowInfo objects for windows that are considered application
        windows (by size, type, and class). Returns empty list on failure.
    """
    logger.info("Starting window enumeration")
    conn = open_xcb_connection()
    if not conn:
        logger.error("Cannot open XCB connection for window enumeration")
        return []

    atoms = AtomCache(conn)
    root = conn.get_setup().roots[0].root

    # Get top-level client windows via EWMH _NET_CLIENT_LIST
    cookie = conn.core.GetProperty(
        False, root, atoms.get("_NET_CLIENT_LIST"), xcffib.xproto.Atom.WINDOW, 0, 1024
    )
    reply = cookie.reply()
    if reply and reply.value_len:
        # Unpack the list of window IDs
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
    """
    Return WindowInfo for the currently active (focused) window.

    Returns:
        WindowInfo object if an active window exists and is valid,
        otherwise None.
    """
    conn = open_xcb_connection()
    if not conn:
        logger.error("Cannot open XCB connection to get active window")
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

        active_win = reply.value.to_atoms()[0]
        if active_win == 0:
            return None

        geom = get_window_geometry(conn, active_win)
        if geom is None:
            return None
        _, _, w, h = geom

        name = get_window_name(conn, active_win, atoms) or "unknown"
        return WindowInfo(active_win, w, h, name)
    except Exception as e:
        logger.error(f"Failed to get active window: {e}")
        return None
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
    """
    Locate a window by process ID (and optionally by class hint) using a two-phase search.

    The search alternates between:
      1. Phase 1: look for windows whose PID matches the process tree,
         and optionally also check the class hint.
      2. Phase 2: if a class hint is given, look purely by class hint
         (ignoring PID) for `class_timeout` seconds.

    Phases repeat until a window is found or `total_timeout` expires.

    Args:
        pid: Process ID of the launched program.
        pid_timeout: Seconds to spend in phase 1 before switching to phase 2.
        class_hint: Optional string to match against WM_CLASS (instance or class).
        class_timeout: Seconds to spend in phase 2 before switching back.
        total_timeout: Maximum total search time. If None, no total timeout.
        starting_phase: 1 for PID+class first, 2 for pure class first.

    Returns:
        WindowInfo as soon as a matching, viewable window is found.

    Raises:
        TimeoutError: If no matching window appears within the total timeout.
    """
    logger.info(
        f"_find_by_pid called with pid={pid}, class_hint={class_hint}, "
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

    def check_total_timeout() -> None:
        if total_timeout is not None and (time.time() - overall_start) > total_timeout:
            raise TimeoutError(
                f"No matching window found within total timeout of {total_timeout} seconds"
            )

    # Single XCB connection for the entire search (more efficient)
    conn = open_xcb_connection()
    if not conn:
        raise RuntimeError("Failed to open XCB connection for window search")
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

                        # PID check
                        win_pid = get_window_pid(conn, win, atoms)
                        if win_pid is None or win_pid not in pids:
                            continue

                        # Optional class check (if hint provided)
                        if class_hint_lower:
                            klass_tuple = get_window_class(conn, win, atoms)
                            if not klass_tuple:
                                continue
                            instance, cls = klass_tuple
                            if not (
                                class_hint_lower in instance.lower()
                                or class_hint_lower in cls.lower()
                            ):
                                continue

                        # Match found
                        geom = get_window_geometry(conn, win)
                        if geom is None:
                            continue
                        _, _, w, h = geom
                        name = get_window_name(conn, win, atoms) or "unknown"
                        logger.info(f"Found window in phase 1: {name}")
                        return WindowInfo(win, w, h, name)

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
                    windows = enumerate_all_windows(conn)
                    for win in windows:
                        if not is_viewable(conn, win):
                            continue

                        if class_hint_lower:
                            klass_tuple = get_window_class(conn, win, atoms)
                            if not klass_tuple:
                                continue
                            instance, cls = klass_tuple
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

                # Phase 2 timed out - go back to phase 1
                logger.info("Phase 2 timed out, restarting phase 1.")
                phase = 1

    finally:
        close_xcb_connection(conn)
        logger.debug("Closed XCB connection after window search")


def _launch_and_find_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """
    Launch the program from config.program and use _find_by_pid to locate its window.

    Args:
        config: Configuration containing program list and timeout settings.

    Returns:
        A tuple (WindowInfo, Popen) on success, or (None, None) on failure/timeout.
    """
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
    """
    Interactively let the user choose a window from the list.

    Args:
        windows: List of WindowInfo objects to choose from.

    Returns:
        The selected WindowInfo, or None if the user quits.
    """
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
    """
    Wait target_delay seconds and then return the currently active window.

    Args:
        config: Configuration containing target_delay and log level.

    Returns:
        WindowInfo of the active window, or None on failure.
    """
    if config.log_level != "ERROR":
        print(
            f"No program specified. Will scale the currently active window "
            f"in {config.target_delay} seconds..."
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


def activate_window(win_handle: int) -> None:
    """
    Activate (raise + focus) the target window using the most reliable method.

    - Tries `xdotool windowactivate --sync` first because it respects EWMH and
      works across all window managers, including KWin on XWayland.
    - If `xdotool` is unavailable or the call fails, falls back to a direct
      XCB `SetInputFocus`, which at least gives keyboard focus even if the
      window doesn't pop to the front.

    Args:
        win_handle: X11 window ID to activate.
    """
    # Primary method: xdotool
    if shutil.which("xdotool"):
        try:
            subprocess.run(
                ["xdotool", "windowactivate", "--sync", str(win_handle)],
                check=True,
                timeout=3,
                capture_output=True,
            )
            logger.info(f"Activated window {win_handle:#x} via xdotool")
            return
        except subprocess.TimeoutExpired:
            logger.info(
                f"xdotool timed out activating window {win_handle:#x}; "
                "falling back to XCB focus."
            )
        except subprocess.CalledProcessError as e:
            logger.info(
                f"xdotool failed to activate window {win_handle:#x} (exit code {e.returncode}). "
                "Falling back to XCB focus."
            )
        except FileNotFoundError:
            pass

    # Fallback: just give the window input focus
    conn = open_xcb_connection()
    if conn is None:
        logger.info("Cannot focus window: XCB connection unavailable.")
        return

    try:
        conn.core.SetInputFocus(
            revert_to=xcffib.xproto.InputFocus.Parent,
            focus=win_handle,
            time=xcffib.xproto.Time.CurrentTime,
        )
        conn.flush()
        logger.info(f"Focused window {win_handle:#x} (raise not guaranteed)")
    except Exception as e:
        logger.info(f"Failed to focus window {win_handle:#x} via XCB: {e}")
    finally:
        close_xcb_connection(conn)


def acquire_target_window(
    config: Config,
) -> Tuple[Optional[WindowInfo], Optional[subprocess.Popen]]:
    """
    Determine which window to upscale based on configuration.

    This is the main entry point for window acquisition. It supports three
    modes:
      - `config.select = True`: Show interactive list of windows for the user.
      - `config.program` is set: Launch the program and wait for its window.
      - Otherwise: Wait `target_delay` seconds and take the currently active window.

    Args:
        config: Configuration object (must have fields: select, program, target_delay,
                pid_timeout, class_timeout, total_timeout, starting_phase, log_level).

    Returns:
        A tuple (WindowInfo, optional Popen process). If acquisition fails,
        returns (None, None). The Popen object is only non-None when a program
        was launched.
    """
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

        # Activate (raise + focus) the chosen window
        activate_window(win_info.handle)
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
