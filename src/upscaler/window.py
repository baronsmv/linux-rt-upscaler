import time

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


def find_by_pid(pid, pid_timeout=5, class_hint=None, class_timeout=5):
    """
    Find a viewable window whose _NET_WM_PID matches the given PID or any descendant.
    If class_hint is given, also check WM_CLASS during the same period, and if PID fails,
    continue with pure class‑based search for class_timeout seconds.
    Returns a WindowInfo object.
    """
    # Gather all PIDs in the process tree
    try:
        proc = psutil.Process(pid)
        pids = {pid} | {child.pid for child in proc.children(recursive=True)}
    except psutil.NoSuchProcess:
        pids = {pid}
    print(f"Tracking PIDs: {pids}")

    disp = Display()
    ewmh = EWMH(disp)
    start = time.time()
    class_hint_lower = class_hint.lower() if class_hint else None

    # Phase 1: try both PID and (if given) class hint simultaneously
    while time.time() - start < pid_timeout:
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
            except (XError, TypeError, IndexError):
                continue

        time.sleep(0.2)

    # Phase 2: if class hint given and still not found, do pure class‑based search
    if class_hint:
        print(
            f"PID‑based detection timed out. Falling back to class hint '{class_hint}'"
        )
        return find_by_class(class_hint, timeout=class_timeout)

    raise TimeoutError(
        f"No viewable window with PID in {pids} found within {pid_timeout} seconds"
    )


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
