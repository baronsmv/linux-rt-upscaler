#!/usr/bin/env python3

"""
Real‑time window upscaler using CuNNy (2×) + full‑screen scaling.
Usage:
    python main.py [-m] [program ...]
Options:
    -m, --map-clicks   Forward mouse clicks AND motion to the original window (scaled coordinates)
Press Ctrl‑C to exit.
"""

import argparse
import ctypes
import queue
import signal
import subprocess
import sys
import threading
import time
from threading import Lock

from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QMainWindow
from Xlib import X, display
from Xlib.protocol import event as xevent
from compushady import Swapchain, Texture2D
from compushady.formats import R8G8B8A8_UNORM

from .capture import capture as cap
from .shaders import srcnn

# Optional psutil for process tree tracking
try:
    import psutil

    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False
    print("psutil not installed; PID tracking limited to original process only.")

# Global flags and queues
running = True
capture_queue = queue.Queue(maxsize=1)
target_process = None
map_clicks = False  # set by command line

# Shared rectangle for scaling (destination on screen)
scaling_rect = [0, 0, 0, 0]  # x, y, width, height
rect_lock = Lock()

# Separate X display for event forwarding (main thread)
disp_events = None
target_window_handle = 0
client_width = 0
client_height = 0


def get_active_window():
    """Return (handle, width, height, title) of the currently active X11 window."""
    disp = display.Display()
    root = disp.screen().root
    active_atom = disp.intern_atom("_NET_ACTIVE_WINDOW")
    prop = root.get_full_property(active_atom, X.AnyPropertyType)
    if not prop:
        raise RuntimeError("Could not get active window")
    handle = prop.value[0]
    window = disp.create_resource_object("window", handle)
    geom = window.get_geometry()
    name_prop = window.get_full_property(disp.intern_atom("_NET_WM_NAME"), 0)
    title = name_prop.value.decode("utf-8") if name_prop else "unknown"
    return handle, geom.width, geom.height, title


def find_window_by_pid(pid, timeout=20):
    """PID‑based window detection (includes process tree if psutil available)."""
    pids_to_check = {pid}
    if HAVE_PSUTIL:
        try:
            proc = psutil.Process(pid)
            pids_to_check = {pid} | {
                child.pid for child in proc.children(recursive=True)
            }
        except psutil.NoSuchProcess:
            pass
    disp = display.Display()
    root = disp.screen().root
    pid_atom = disp.intern_atom("_NET_WM_PID")
    name_atom = disp.intern_atom("_NET_WM_NAME")
    start_time = time.time()
    while time.time() - start_time < timeout:
        for win in root.query_tree().children:
            attrs = win.get_attributes()
            if not attrs or attrs.map_state != X.IsViewable:
                continue
            pid_prop = win.get_full_property(pid_atom, X.AnyPropertyType)
            if pid_prop and pid_prop.value and pid_prop.value[0] in pids_to_check:
                geom = win.get_geometry()
                name_prop = win.get_full_property(name_atom, 0)
                title = name_prop.value.decode("utf-8") if name_prop else "unknown"
                return win.id, geom.width, geom.height, title
        time.sleep(0.2)
    raise TimeoutError(
        f"No viewable window with PID in {pids_to_check} found within {timeout} seconds"
    )


def find_window_by_class(class_hint, timeout=10):
    """Fallback: match any viewable window whose WM_CLASS contains class_hint."""
    disp = display.Display()
    root = disp.screen().root
    class_atom = disp.intern_atom("WM_CLASS")
    name_atom = disp.intern_atom("_NET_WM_NAME")
    start_time = time.time()
    class_hint_lower = class_hint.lower()
    while time.time() - start_time < timeout:
        for win in root.query_tree().children:
            attrs = win.get_attributes()
            if not attrs or attrs.map_state != X.IsViewable:
                continue
            class_prop = win.get_full_property(class_atom, 0)
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
                        name_prop = win.get_full_property(name_atom, 0)
                        title = (
                            name_prop.value.decode("utf-8") if name_prop else "unknown"
                        )
                        return win.id, geom.width, geom.height, title
        time.sleep(0.2)
    raise TimeoutError(
        f"No viewable window with class hint '{class_hint}' found within {timeout} seconds"
    )


class OverlayWindow(QMainWindow):
    """Full‑screen overlay. If map_clicks is True, it accepts mouse input and forwards events."""

    def __init__(self, width, height, opacity=100, map_clicks=False):
        super().__init__()
        self.map_clicks = map_clicks
        self.setWindowOpacity(opacity / 100.0)
        self.setGeometry(0, 0, width, height)
        flags = self.windowFlags() | Qt.X11BypassWindowManagerHint
        if not map_clicks:
            flags |= Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.setMouseTracking(map_clicks)  # receive move events even without buttons
        self.show()
        self.xid = int(self.winId())
        if map_clicks:
            self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.map_clicks:
            if event.type() == QEvent.MouseMove:
                self.handle_mouse_motion(event)
                return True
            elif event.type() in (
                QEvent.MouseButtonPress,
                QEvent.MouseButtonRelease,
            ):
                self.handle_mouse_button(event)
                return True
        return super().eventFilter(obj, event)

    def _map_coordinates(self, screen_x, screen_y):
        """Transform screen coordinates to target window client coordinates.
        Returns (target_x, target_y, inside) where inside indicates whether the point is inside the upscaled image area.
        """
        global scaling_rect, rect_lock
        with rect_lock:
            dx, dy, dw, dh = scaling_rect
        if not (dx <= screen_x < dx + dw and dy <= screen_y < dy + dh):
            return 0, 0, False
        src_w = client_width * 2
        src_h = client_height * 2
        src_x = (screen_x - dx) * src_w / dw
        src_y = (screen_y - dy) * src_h / dh
        target_x = int(src_x / 2)
        target_y = int(src_y / 2)
        target_x = max(0, min(target_x, client_width - 1))
        target_y = max(0, min(target_y, client_height - 1))
        return target_x, target_y, True

    def _send_event(self, ev):
        if not disp_events:
            return
        disp_events.send_event(
            int(target_window_handle),
            ev,
            event_mask=X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask,
        )
        disp_events.flush()

    def handle_mouse_motion(self, event):
        """Forward mouse motion to target window."""
        pos = event.position().toPoint()
        screen_x, screen_y = pos.x(), pos.y()
        target_x, target_y, inside = self._map_coordinates(screen_x, screen_y)
        if not inside:
            return

        # Compute button state mask (these are integer masks)
        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= X.Button1Mask  # X.Button1Mask is an integer mask
        if buttons & Qt.RightButton:
            state |= X.Button3Mask
        if buttons & Qt.MiddleButton:
            state |= X.Button2Mask

        # Get integer IDs
        root_id = int(disp_events.screen().root.id)
        window_id = int(target_window_handle)

        ev = xevent.MotionNotify(
            window=window_id,
            root=root_id,
            same_screen=1,
            root_x=int(screen_x),
            root_y=int(screen_y),
            time=int(X.CurrentTime),
            detail=0,  # not used for motion
            state=int(state),
            event_x=int(target_x),
            event_y=int(target_y),
            child=0,
        )
        self._send_event(ev)

    def handle_mouse_button(self, event):
        """Forward mouse button press/release to target window."""
        pos = event.position().toPoint()
        screen_x, screen_y = pos.x(), pos.y()
        target_x, target_y, inside = self._map_coordinates(screen_x, screen_y)
        if not inside:
            return

        # Map Qt button to X11 button numbers
        btn = event.button()
        if btn == Qt.LeftButton:
            x11_button = 1  # X.Button1
        elif btn == Qt.RightButton:
            x11_button = 3  # X.Button3
        elif btn == Qt.MiddleButton:
            x11_button = 2  # X.Button2
        else:
            # For other buttons (scroll, etc.), use the raw integer value
            x11_button = btn.value

        root_id = int(disp_events.screen().root.id)
        window_id = int(target_window_handle)
        state = 0  # could be improved to reflect actual button state

        if event.type() == QEvent.MouseButtonPress:
            ev = xevent.ButtonPress(
                window=window_id,
                root=root_id,
                same_screen=1,
                root_x=int(screen_x),
                root_y=int(screen_y),
                time=int(X.CurrentTime),
                detail=x11_button,
                state=state,
                event_x=int(target_x),
                event_y=int(target_y),
                child=0,
            )
        else:
            ev = xevent.ButtonRelease(
                window=window_id,
                root=root_id,
                same_screen=1,
                root_x=int(screen_x),
                root_y=int(screen_y),
                time=int(X.CurrentTime),
                detail=x11_button,
                state=state,
                event_x=int(target_x),
                event_y=int(target_y),
                child=0,
            )
        self._send_event(ev)


def compute_worker(
    upscaler,
    screen_tex,
    screen_swapchain,
    screen_w,
    screen_h,
    client_w,
    client_h,
    window_handle,
):
    """
    Worker thread: get captured frames, run CuNNy upscaling, then scale to screen and present.
    Also updates scaling_rect for click mapping.
    """
    global running, scaling_rect, rect_lock, map_clicks
    count = 0
    total_compute_time = 0.0

    # For mouse opacity control, we need the window's root position (only when not mapping clicks).
    if not map_clicks:
        disp = display.Display()
        window = disp.create_resource_object("window", window_handle)

    # Pre‑compute source size (upscaled)
    src_w = client_w * 2
    src_h = client_h * 2

    while running:
        # Wait for a captured frame
        bitmap = capture_queue.get()
        frame_start = time.perf_counter()

        # CuNNy upscaling
        upscaler.upload(bitmap)
        upscaler.compute()  # result in upscaler.output

        # Compute destination rectangle on CPU for click mapping
        src_aspect = src_w / src_h
        screen_aspect = screen_w / screen_h
        if src_aspect > screen_aspect:
            dst_w = screen_w
            dst_h = int(screen_w / src_aspect)
            dst_x = 0
            dst_y = (screen_h - dst_h) // 2
        else:
            dst_h = screen_h
            dst_w = int(screen_h * src_aspect)
            dst_x = (screen_w - dst_w) // 2
            dst_y = 0

        with rect_lock:
            scaling_rect[:] = [dst_x, dst_y, dst_w, dst_h]

        # Full‑screen scaling (aspect‑preserving)
        upscaler.scale_to(screen_tex, screen_w, screen_h, blur=1.0)

        compute_time = time.perf_counter() - frame_start
        total_compute_time += compute_time
        count += 1

        # Opacity control
        if map_clicks:
            # With click mapping, always keep overlay fully opaque
            overlay.setWindowOpacity(1.0)
        else:
            mouse = QCursor.pos()
            if mouse.x() == 0 and mouse.y() == 0:
                print(f"\nExit signal: mouse at (0,0). Frames processed: {count}")
                running = False
                break
            # Get window position
            geom = window.get_geometry()
            trans = geom.root.translate_coords(window, 0, 0)
            win_x, win_y = trans.x, trans.y
            inside = (win_x <= mouse.x() < win_x + client_w) and (
                win_y <= mouse.y() < win_y + client_h
            )
            opacity = 1.0 if inside else 0.2
            overlay.setWindowOpacity(opacity)

        # Present to screen
        screen_swapchain.present(screen_tex)

    # Cleanup
    if count > 0:
        print(
            f"Average compute time per frame: {(total_compute_time/count)*1000:.2f} ms"
        )


def main():
    global running, overlay, target_process, map_clicks
    global disp_events, target_window_handle, client_width, client_height

    parser = argparse.ArgumentParser(
        description="Upscale a window in real time using CuNNy."
    )
    parser.add_argument(
        "-m",
        "--map-clicks",
        action="store_true",
        help="Forward mouse clicks AND motion to the original window (scaled coordinates)",
    )
    parser.add_argument(
        "program", nargs="*", help="Program to launch and scale (optional)"
    )
    args = parser.parse_args()
    map_clicks = args.map_clicks

    if args.program:
        program_name = args.program[0]
        print(f"Launching: {' '.join(args.program)}")
        target_process = subprocess.Popen(args.program)

        # Try PID‑based detection first
        print("Waiting for window (PID‑based detection)...")
        try:
            handle, client_w, client_h, title = find_window_by_pid(
                target_process.pid, timeout=15
            )
            print(
                f"Found window via PID: handle={handle}, {client_w}x{client_h}, title={title}"
            )
        except TimeoutError:
            print(
                "PID‑based detection timed out. Falling back to class‑based matching..."
            )
            try:
                handle, client_w, client_h, title = find_window_by_class(
                    program_name, timeout=10
                )
                print(
                    f"Found window via class: handle={handle}, {client_w}x{client_h}, title={title}"
                )
            except TimeoutError as e:
                print(e)
                if target_process:
                    target_process.terminate()
                sys.exit(1)
    else:
        print(
            "No program specified. Will scale the currently active window in 5 seconds..."
        )
        time.sleep(5)
        handle, client_w, client_h, title = get_active_window()
        print(f"Target window: handle={handle}, {client_w}x{client_h}, title={title}")

    # Store globally for event forwarding
    target_window_handle = handle
    client_width = client_w
    client_height = client_h

    # Open a separate X display for event forwarding
    disp_events = display.Display()

    # Start Qt application and create overlay
    app = QApplication([])
    screen = app.primaryScreen()
    screen_size = screen.size()
    screen_w, screen_h = screen_size.width(), screen_size.height()
    print(f"Screen resolution: {screen_w}x{screen_h}")

    overlay = OverlayWindow(screen_w, screen_h, opacity=100, map_clicks=map_clicks)

    # Get X11 display handle for Swapchain
    xlib = ctypes.cdll.LoadLibrary("libX11.so")
    display_id = xlib.XOpenDisplay(ctypes.c_int(0))
    swapchain = Swapchain((display_id, overlay.xid), R8G8B8A8_UNORM, 3)

    # Create screen‑sized texture for final output
    screen_tex = Texture2D(screen_w, screen_h, R8G8B8A8_UNORM)

    # Initialize CuNNy upscaler
    upscaler = srcnn.SRCNN(client_w, client_h)

    # Start capture thread
    cap.running = True
    capture_thread = threading.Thread(
        target=cap.capture_worker,
        args=(capture_queue, handle, client_w, client_h),
    )
    capture_thread.start()

    # Start compute thread
    compute_thread = threading.Thread(
        target=compute_worker,
        args=(
            upscaler,
            screen_tex,
            swapchain,
            screen_w,
            screen_h,
            client_w,
            client_h,
            handle,
        ),
    )
    compute_thread.start()

    # Enable Ctrl+C handling
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        app.exec()
    finally:
        # Shutdown everything
        running = False
        cap.running = False
        # Unblock capture queue
        if capture_queue.empty():
            capture_queue.put(bytearray(client_w * client_h * 4))
        capture_thread.join()
        compute_thread.join()
        if target_process:
            target_process.terminate()
            target_process.wait()
        if disp_events:
            disp_events.close()
        print("Clean exit.")


if __name__ == "__main__":
    main()
