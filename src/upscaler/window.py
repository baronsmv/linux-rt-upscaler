import time
from typing import Optional

import psutil
from Xlib import X
from Xlib.display import Display
from Xlib.error import XError
from ewmh import EWMH


class WindowInfo:
    def __init__(self, handle, width, height, title):
        self.handle = handle
        self.width = width
        self.height = height
        self.title = title

    @property
    def size(self):
        return self.width, self.height


def _get_all_windows(disp):
    """Recursively collect all windows (including children) from the root."""
    root = disp.screen().root
    windows = []

    def recurse(win):
        windows.append(win)
        try:
            for child in win.query_tree().children:
                recurse(child)
        except XError:
            pass

    recurse(root)
    return windows


def find_by_pid(
    pid,
    pid_timeout: int = 5,
    class_hint: Optional[str] = None,
    class_timeout: int = 5,
    total_timeout: Optional[int] = 60,
    starting_phase: int = 1,
):
    """
    Loop indefinitely, alternating between:
      1. Searching by PID (and checking WM_CLASS as well) for pid_timeout seconds.
      2. If class_hint is given, searching purely by WM_CLASS for class_timeout seconds.
    If total_timeout (in seconds) is provided, the search will stop after that total time
    and raise TimeoutError. Otherwise, it loops forever until a matching window is found.
    Returns a WindowInfo as soon as a matching viewable window is found.
    """
    # Gather all PIDs in the process tree
    try:
        proc = psutil.Process(pid)
        pids = {pid} | {child.pid for child in proc.children(recursive=True)}
    except psutil.NoSuchProcess:
        pids = {pid}
    print(f"Tracking PIDs: {pids}")

    class_hint_lower = class_hint.lower() if class_hint else None
    phase = starting_phase

    overall_start = time.time()

    # Outer infinite loop – will only exit when a window is found or total timeout reached
    while True:
        # Check total timeout before starting a new phase
        if total_timeout is not None and (time.time() - overall_start) > total_timeout:
            raise TimeoutError(
                f"No matching window found within total timeout of {total_timeout} seconds"
            )

        disp = Display()
        ewmh = EWMH(disp)
        phase_start = time.time()

        if phase == 1:
            # Phase 1: Search by PID (and also check class hint if given)
            print(f"Phase 1: Trying PID+class for {pid_timeout} seconds...")
            while time.time() - phase_start < pid_timeout:
                # Optional: check total timeout more granularly inside the loop
                if (
                    total_timeout is not None
                    and (time.time() - overall_start) > total_timeout
                ):
                    raise TimeoutError(
                        f"No matching window found within total timeout of {total_timeout} seconds"
                    )

                windows = _get_all_windows(disp)
                for win in windows:
                    try:
                        attrs = win.get_attributes()
                        if not attrs or attrs.map_state != X.IsViewable:
                            continue

                        # PID check
                        win_pid_list = ewmh.getWmPid(win)
                        if win_pid_list and win_pid_list[0] in pids:
                            geom = win.get_geometry()
                            name = ewmh.getWmName(win) or "unknown"
                            return WindowInfo(win.id, geom.width, geom.height, name)

                        # Class hint check (if provided)
                        if class_hint_lower:
                            class_prop = win.get_full_property(
                                disp.intern_atom("WM_CLASS"), 0
                            )
                            if class_prop:
                                data = class_prop.value
                                strings = data.decode("latin1").split("\x00")
                                if len(strings) >= 2:
                                    instance, klass = strings[0], strings[1]
                                    if (
                                        class_hint_lower in instance.lower()
                                        or class_hint_lower in klass.lower()
                                    ):
                                        geom = win.get_geometry()
                                        name = ewmh.getWmName(win) or "unknown"
                                        return WindowInfo(
                                            win.id, geom.width, geom.height, name
                                        )
                    except (XError, TypeError, IndexError):
                        continue
                time.sleep(0.2)
            # Phase 1 timed out – move to phase 2 if class hint is available
            if class_hint_lower:
                phase = 2
                print("Phase 1 timed out, switching to phase 2 (pure class search).")
            else:
                # No class hint, just restart phase 1
                print("Phase 1 timed out, restarting (no class hint available).")
        else:  # phase == 2
            # Phase 2: Pure class‑based search (only if class_hint was given)
            print(f"Phase 2: Trying pure class hint for {class_timeout} seconds...")
            while time.time() - phase_start < class_timeout:
                # Optional: check total timeout more granularly inside the loop
                if (
                    total_timeout is not None
                    and (time.time() - overall_start) > total_timeout
                ):
                    raise TimeoutError(
                        f"No matching window found within total timeout of {total_timeout} seconds"
                    )

                windows = _get_all_windows(disp)
                for win in windows:
                    try:
                        attrs = win.get_attributes()
                        if not attrs or attrs.map_state != X.IsViewable:
                            continue

                        class_prop = win.get_full_property(
                            disp.intern_atom("WM_CLASS"), 0
                        )
                        if class_prop:
                            data = class_prop.value
                            strings = data.decode("latin1").split("\x00")
                            if len(strings) >= 2:
                                instance, klass = strings[0], strings[1]
                                if (
                                    class_hint_lower in instance.lower()
                                    or class_hint_lower in klass.lower()
                                ):
                                    geom = win.get_geometry()
                                    name = ewmh.getWmName(win) or "unknown"
                                    return WindowInfo(
                                        win.id, geom.width, geom.height, name
                                    )
                    except XError:
                        continue
                time.sleep(0.2)
            # Phase 2 timed out – go back to phase 1
            print("Phase 2 timed out, restarting phase 1.")
            phase = 1


def find_by_class(class_hint, timeout=5):
    """Find a viewable window whose WM_CLASS contains class_hint (case‑insensitive)."""
    disp = Display()
    ewmh = EWMH(disp)
    start = time.time()
    class_hint_lower = class_hint.lower()

    while time.time() - start < timeout:
        windows = _get_all_windows(disp)
        for win in windows:
            try:
                attrs = win.get_attributes()
                if not attrs or attrs.map_state != X.IsViewable:
                    continue

                class_prop = win.get_full_property(disp.intern_atom("WM_CLASS"), 0)
                if class_prop:
                    data = class_prop.value
                    strings = data.decode("latin1").split("\x00")
                    if len(strings) >= 2:
                        instance, klass = strings[0], strings[1]
                        if (
                            class_hint_lower in instance.lower()
                            or class_hint_lower in klass.lower()
                        ):
                            geom = win.get_geometry()
                            name = ewmh.getWmName(win) or "unknown"
                            return WindowInfo(win.id, geom.width, geom.height, name)
            except XError:
                continue

        time.sleep(0.2)

    raise TimeoutError(
        f"No viewable window with class hint '{class_hint}' found within {timeout} seconds"
    )


def get_active_window():
    """Return WindowInfo for the currently active window."""
    disp = Display()
    ewmh = EWMH(disp)
    active = ewmh.getActiveWindow()
    if not active:
        raise RuntimeError("No active window found")
    geom = active.get_geometry()
    name = ewmh.getWmName(active) or "unknown"
    return WindowInfo(active.id, geom.width, geom.height, name)
