from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QMainWindow, QApplication
from Xlib import X, display
from Xlib.protocol import event as xevent


class OverlayWindow(QMainWindow):
    def __init__(
        self, screen_width, screen_height, map_clicks=False, target_handle=None
    ):
        super().__init__()
        self.map_clicks = map_clicks
        self.target_handle = target_handle
        self.scaling_rect = [0, 0, 0, 0]  # x, y, w, h
        self.setWindowOpacity(1.0)
        self.setGeometry(0, 0, screen_width, screen_height)
        flags = self.windowFlags() | Qt.X11BypassWindowManagerHint
        if not map_clicks:
            flags |= Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        self.setMouseTracking(map_clicks)
        self.show()
        self.xid = int(self.winId())

        if map_clicks:
            self.disp = display.Display()
            self.installEventFilter(self)

    def set_scaling_rect(self, rect):
        self.scaling_rect = rect

    def eventFilter(self, obj, event):
        if not self.map_clicks:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.MouseMove:
            self._handle_mouse(event)
            return True
        elif event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            self._handle_mouse(event)
            return True
        return super().eventFilter(obj, event)

    def _map_coordinates(self, screen_x, screen_y):
        """Transform screen coordinates to target window client coordinates."""
        dx, dy, dw, dh = self.scaling_rect
        if not (dx <= screen_x < dx + dw and dy <= screen_y < dy + dh):
            return 0, 0, False
        if not hasattr(self, "client_width"):
            return 0, 0, False
        target_x = int((screen_x - dx) * self.client_width / dw)
        target_y = int((screen_y - dy) * self.client_height / dh)
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))
        return target_x, target_y, True

    def set_client_size(self, w, h):
        self.client_width = w
        self.client_height = h

    def _send_event(self, ev):
        if not hasattr(self, "disp") or not self.target_handle:
            return
        self.disp.send_event(
            int(self.target_handle),
            ev,
            event_mask=X.ButtonPressMask | X.ButtonReleaseMask | X.PointerMotionMask,
        )
        self.disp.flush()

    def _handle_mouse(self, event):
        pos = event.position().toPoint()
        screen_x, screen_y = pos.x(), pos.y()
        target_x, target_y, inside = self._map_coordinates(screen_x, screen_y)
        if not inside:
            return

        # Compute button state mask for motion
        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= X.Button1Mask
        if buttons & Qt.RightButton:
            state |= X.Button3Mask
        if buttons & Qt.MiddleButton:
            state |= X.Button2Mask

        root_id = int(self.disp.screen().root.id)
        window_id = int(self.target_handle)

        if event.type() == QEvent.MouseMove:
            ev = xevent.MotionNotify(
                window=window_id,
                root=root_id,
                same_screen=1,
                root_x=int(screen_x),
                root_y=int(screen_y),
                time=int(X.CurrentTime),
                detail=0,
                state=int(state),
                event_x=int(target_x),
                event_y=int(target_y),
                child=0,
            )
            self._send_event(ev)
        else:
            # Map Qt button to X11 button numbers
            btn = event.button()
            if btn == Qt.LeftButton:
                x11_button = 1
            elif btn == Qt.RightButton:
                x11_button = 3
            elif btn == Qt.MiddleButton:
                x11_button = 2
            else:
                x11_button = btn.value

            if event.type() == QEvent.MouseButtonPress:
                ev = xevent.ButtonPress(
                    window=window_id,
                    root=root_id,
                    same_screen=1,
                    root_x=int(screen_x),
                    root_y=int(screen_y),
                    time=int(X.CurrentTime),
                    detail=x11_button,
                    state=0,
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
                    state=0,
                    event_x=int(target_x),
                    event_y=int(target_y),
                    child=0,
                )
            self._send_event(ev)
