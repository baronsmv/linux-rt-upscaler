"""Public helpers for discovering and acquiring target windows."""

from __future__ import annotations

import logging
import subprocess
from typing import List, Optional, Tuple

from ..utils import WindowNotFound
from ..window import (
    AtomCache as _AtomCache,
    WindowInfo,
    close_xcb_connection as _close_xcb_connection,
    find_window_by_pid as _find_window_by_pid,
    find_window_by_title as _find_window_by_title,
    get_active_window as _get_active_window,
    get_window_class as _get_window_class,
    list_windows as _list_windows,
    open_xcb_connection as _open_xcb_connection,
)

logger = logging.getLogger(__name__)


def list_windows() -> List[WindowInfo]:
    """Return a list of all currently visible application windows."""
    try:
        return _list_windows()
    except Exception as e:
        logger.warning(f"Failed to enumerate windows: {e}")
        return []


def get_active_window() -> Optional[WindowInfo]:
    """Return the currently active (focused) window, or ``None`` if none."""
    try:
        return _get_active_window()
    except Exception as e:
        logger.warning(f"Failed to get active window: {e}")
        return None


def find_window_by_title(
    contains: Optional[str] = None,
    regex: Optional[str] = None,
) -> WindowInfo:
    """
    Find the first visible window whose title matches the given criteria.

    Priority: `regex` is used if provided, otherwise `contains` (case-insensitive).
    At least one of `contains` or `regex` must be given.

    Args:
        contains: Substring to search for in the window title.
        regex: Regular expression to search for in the window title.

    Returns:
        WindowInfo of the first matching window.

    Raises:
        ValueError: If neither `contains` or `regex` are provided.
        WindowNotFound: If no matching window is found.
    """
    if contains is None and regex is None:
        raise ValueError("Either 'contains' or 'regex' must be provided.")

    result = _find_window_by_title(contains=contains, regex=regex)
    if result is None:
        criteria = f"regex='{regex}'" if regex else f"contains='{contains}'"
        raise WindowNotFound(f"No window found matching {criteria}.")
    return result


def find_window_by_pid(
    pid: int,
    pid_timeout: float = 5.0,
    class_hint: Optional[str] = None,
    class_timeout: float = 5.0,
    total_timeout: Optional[float] = 60.0,
    starting_phase: int = 1,
) -> WindowInfo:
    """
    Wait for and return a window belonging to the given process ID.

    This function uses a two-phase search (PID and optionally WM_CLASS) as
    described in the internal `_find_by_pid`. It blocks until a matching
    viewable window is found or the total timeout expires.

    Args:
        pid: Process ID of the launched program.
        pid_timeout: Seconds to spend in the PID-based phase before switching.
        class_hint: Optional substring to match against WM_CLASS (instance/class).
        class_timeout: Seconds to spend in the pure-class phase.
        total_timeout: Maximum total search time. ``None`` means no limit.
        starting_phase: 1 for PID+class first, 2 for pure class first.

    Returns:
        WindowInfo of the first matching window.

    Raises:
        WindowNotFound: If no matching window appears within the total timeout.
    """
    return _find_window_by_pid(
        pid,
        pid_timeout=pid_timeout,
        class_hint=class_hint,
        class_timeout=class_timeout,
        total_timeout=total_timeout,
        starting_phase=starting_phase,
    )


def find_window_by_class(
    instance: Optional[str] = None, cls: Optional[str] = None
) -> WindowInfo:
    """
    Find the first visible window whose WM_CLASS matches the given criteria.

    At least one of `instance` or `cls` must be provided. Both are compared
    case-insensitively as substrings.

    Args:
        instance: Substring to match against the instance name.
        cls: Substring to match against the class name.

    Returns:
        WindowInfo of the first matching window.

    Raises:
        ValueError: If neither `instance` or `cls` are provided.
        WindowNotFound: If no matching window is found.
    """
    if instance is None and cls is None:
        raise ValueError("Either 'instance' or 'cls' must be provided.")

    conn = _open_xcb_connection()
    if conn is None:
        raise WindowNotFound("Cannot open XCB connection for window search.")

    try:
        atoms = _AtomCache(conn)
        for win in list_windows():
            try:
                klass = _get_window_class(conn, win.handle, atoms)
                if klass is None:
                    continue
                inst, cl = klass
                if instance is not None and instance.lower() not in inst.lower():
                    continue
                if cls is not None and cls.lower() not in cl.lower():
                    continue
                return win
            except Exception:
                continue
        raise WindowNotFound(
            f"No window found matching class instance='{instance}', class='{cls}'."
        )
    finally:
        _close_xcb_connection(conn)


def launch_window(
    program: List[str],
    pid_timeout: float = 5.0,
    class_hint: Optional[str] = None,
    class_timeout: float = 5.0,
    total_timeout: Optional[float] = 60.0,
    starting_phase: int = 1,
) -> Tuple[WindowInfo, subprocess.Popen]:
    """
    Launch a program and wait for its main window to appear.

    If the window cannot be found within the timeout, the launched process
    is terminated.

    Args:
        program: List of command and arguments (e.g., `["myapp", "--flag"]`).
        pid_timeout: Seconds to spend in the PID phase.
        class_hint: Optional substring for class phase.
        class_timeout: Seconds to spend in the class phase.
        total_timeout: Maximum total wait time. ``None`` means no limit.
        starting_phase: 1 for PID first, 2 for class first.

    Returns:
        A tuple `(WindowInfo, subprocess.Popen)`.

    Raises:
        WindowNotFound: If no window appears within the timeout or the program
            fails to start.
    """
    if not program:
        raise ValueError("The 'program' list must not be empty.")

    proc = subprocess.Popen(program)
    try:
        win_info = _find_window_by_pid(
            proc.pid,
            pid_timeout=pid_timeout,
            class_hint=class_hint,
            class_timeout=class_timeout,
            total_timeout=total_timeout,
            starting_phase=starting_phase,
        )
        return win_info, proc
    except WindowNotFound:
        proc.terminate()
        proc.wait()
        raise
    except Exception as e:
        proc.terminate()
        proc.wait()
        raise WindowNotFound(
            f"Failed to find window for program '{program}': {e}"
        ) from e
