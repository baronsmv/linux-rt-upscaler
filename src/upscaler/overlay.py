import logging
from typing import Optional, List, Tuple, Any

from PySide6.QtCore import Qt, QEvent, QPoint
from PySide6.QtWidgets import QMainWindow, QApplication
from Xlib import X, display
from Xlib.protocol import event as xevent

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """
    A transparent overlay window that can either:
      - Remain click‑through (for displaying upscaled content), or
      - Forward mouse events to a target X11 window (for click mapping).
    """

    # Mapping from Qt button to X11 button number (1–3, 4–5 for scroll, 8–9 for extra)
    _BUTTON_MAP = {
        Qt.LeftButton: 1,
        Qt.MiddleButton: 2,
        Qt.RightButton: 3,
        Qt.XButton1: 8,
        Qt.XButton2: 9,
    }

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        map_clicks: bool = False,
        target_handle: Optional[int] = None,
        initial_x: int = 0,
        initial_y: int = 0,
    ) -> None:
        """
        Create and show the overlay window.

        :param screen_width: Width of the screen (overlay covers full screen).
        :param screen_height: Height of the screen.
        :param map_clicks: If True, mouse events are forwarded to the target window.
        :param target_handle: X11 window ID of the target window (required if map_clicks=True).
        """
        super().__init__()
        logger.info(
            f"Initializing OverlayWindow: {screen_width}x{screen_height}, "
            f"map_clicks={map_clicks}, target_handle={target_handle}"
        )

        self.map_clicks = map_clicks
        self.target_handle = target_handle
        self.scaling_rect: List[int] = [
            0,
            0,
            0,
            0,
        ]  # x, y, w, h (in screen coordinates)
        self.client_width: Optional[int] = None
        self.client_height: Optional[int] = None

        # X11 connection for event forwarding (only opened if map_clicks is True)
        self._x_display: Optional[display.Display] = None
        self._x_root: Optional[int] = None

        # Basic window properties
        self.setWindowOpacity(1.0)
        self.setGeometry(initial_x, initial_y, screen_width, screen_height)

        # Window flags: always bypass window manager (to stay on top),
        # and optionally transparent for input if not mapping clicks.
        flags = self.windowFlags() | Qt.X11BypassWindowManagerHint
        if not map_clicks:
            flags |= Qt.WindowTransparentForInput
            logger.debug("Window is transparent for input (click‑through).")
        else:
            logger.debug("Window will forward mouse events (click mapping enabled).")
        self.setWindowFlags(flags)

        self.setMouseTracking(map_clicks)  # track mouse moves only if mapping
        self.show()
        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        # If forwarding is enabled, open X display and install event filter
        if map_clicks:
            if target_handle is None:
                logger.error("map_clicks=True requires a target_handle")
                raise ValueError("target_handle must be provided when map_clicks=True")

            self._open_x_display()
            self.installEventFilter(self)

    def _x_error_handler(self, error, request) -> None:
        """
        Custom X error handler – suppresses default stderr printing and logs silently.
        """
        if error.error_code == 3:  # BadWindow
            logger.debug(f"Ignoring BadWindow (target window probably gone)")
        else:
            logger.error(f"Unexpected X error: {error}")
        # Do not raise; just return. The error is already handled.

    def _open_x_display(self) -> None:
        """Open a connection to the X server and install a custom error handler."""
        try:
            self._x_display = display.Display()
            self._x_root = int(self._x_display.screen().root.id)
            self._x_display.set_error_handler(self._x_error_handler)
            logger.debug("Opened X display with custom error handler.")
        except Exception as e:
            logger.error(f"Failed to open X display: {e}", exc_info=True)
            self._x_display = None
            self._x_root = None
            # Disable forwarding because we can't send events
            self.map_clicks = False
            # Update window flags to become click‑through
            self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
            self.show()  # re‑apply flags

    def closeEvent(self, event: Any) -> None:
        """Ensure X display is closed when the window is destroyed."""
        self._close_x_display()
        super().closeEvent(event)

    def _close_x_display(self) -> None:
        """Safely close the X display connection."""
        if self._x_display is not None:
            try:
                self._x_display.close()
                logger.debug("Closed X display.")
            except Exception as e:
                logger.warning(f"Error closing X display: {e}")
            finally:
                self._x_display = None
                self._x_root = None

    def disable_click_forwarding(self) -> None:
        """
        Permanently disable mouse forwarding (e.g., when target window is destroyed).
        This also makes the overlay click‑through.
        """
        if self.map_clicks:
            logger.info("Disabling click forwarding.")
            self.map_clicks = False
            self.target_handle = None
            self._close_x_display()
            # Make window transparent for input
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()  # re‑apply flags

    def set_scaling_rect(self, rect: List[int]) -> None:
        """
        Set the rectangle (in screen coordinates) where the upscaled content is drawn.
        Used to map screen coordinates to target window coordinates.
        """
        if len(rect) != 4:
            logger.error(f"set_scaling_rect expects list of 4 ints, got {rect}")
            return
        self.scaling_rect = rect
        logger.debug(f"Scaling rect set to {rect}")

    def set_client_size(self, w: int, h: int) -> None:
        """Set the original (client) size of the target window."""
        self.client_width = w
        self.client_height = h
        logger.debug(f"Client size set to {w}x{h}")

    def eventFilter(self, obj: Any, event: QEvent) -> bool:
        """Filter mouse events and forward them when map_clicks is enabled."""
        if not self.map_clicks:
            return super().eventFilter(obj, event)

        if event.type() == QEvent.MouseMove:
            self._handle_mouse(event)
            return True
        elif event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            self._handle_mouse(event)
            return True

        return super().eventFilter(obj, event)

    def _map_coordinates(self, screen_x: int, screen_y: int) -> Tuple[int, int, bool]:
        """
        Transform screen coordinates to target window client coordinates.

        Returns (target_x, target_y, inside_flag). If the point is outside the
        scaling rectangle or client size is not set, inside_flag is False.
        """
        if not self.scaling_rect or self.scaling_rect[2] == 0:
            logger.debug("_map_coordinates: scaling_rect not set")
            return 0, 0, False

        dx, dy, dw, dh = self.scaling_rect
        if not (dx <= screen_x < dx + dw and dy <= screen_y < dy + dh):
            logger.debug(
                f"_map_coordinates: ({screen_x},{screen_y}) outside scaling rect"
            )
            return 0, 0, False

        if self.client_width is None or self.client_height is None:
            logger.debug("_map_coordinates: client size not set yet")
            return 0, 0, False

        target_x = int((screen_x - dx) * self.client_width / dw)
        target_y = int((screen_y - dy) * self.client_height / dh)

        # Clamp to valid range
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))

        logger.debug(
            f"_map_coordinates: ({screen_x},{screen_y}) -> ({target_x},{target_y})"
        )
        return target_x, target_y, True

    def _get_current_button_state(self) -> int:
        """
        Return an X11 button state mask based on currently pressed Qt buttons.
        """
        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= X.Button1Mask
        if buttons & Qt.RightButton:
            state |= X.Button3Mask
        if buttons & Qt.MiddleButton:
            state |= X.Button2Mask
        logger.debug(f"Current button state mask: {state}")
        return state

    def _qt_button_to_x11(self, qt_button: Qt.MouseButton) -> int:
        """
        Convert a Qt button to the corresponding X11 button number.
        Defaults to 0 for unknown buttons (will likely be ignored).
        """
        x11_btn = self._BUTTON_MAP.get(qt_button, 0)
        if x11_btn == 0:
            logger.warning(f"Unmapped Qt button {qt_button}, using 0")
        return x11_btn

    def _send_event(self, ev: Any) -> None:
        """
        Send an X11 event to the target window and flush the display.
        The custom error handler will log errors without printing to stderr.
        """
        if self._x_display is None or self.target_handle is None:
            logger.error("Cannot send event: no X display or target handle")
            return

        try:
            self._x_display.send_event(
                int(self.target_handle),
                ev,
                event_mask=X.ButtonPressMask
                | X.ButtonReleaseMask
                | X.PointerMotionMask,
            )
            self._x_display.flush()
            logger.debug(f"Sent event: {ev}")
        except Exception as e:
            logger.error(f"Unexpected error sending X11 event: {e}", exc_info=True)

    def _handle_mouse(self, event: QEvent) -> None:
        """
        Convert a Qt mouse event to an X11 event and forward it.
        """
        if self._x_display is None or self.target_handle is None:
            logger.debug("_handle_mouse called but forwarding not available")
            return

        # Get global screen coordinates from the event
        pos: QPoint = event.position().toPoint()
        screen_x, screen_y = pos.x(), pos.y()

        # Map to target window coordinates
        target_x, target_y, inside = self._map_coordinates(screen_x, screen_y)
        if not inside:
            logger.debug(
                f"Ignoring mouse event outside scaling rect: ({screen_x},{screen_y})"
            )
            return

        # Common X11 fields
        root_id = self._x_root
        window_id = int(self.target_handle)
        time = X.CurrentTime  # could use event.timestamp() if needed

        if event.type() == QEvent.MouseMove:
            state = self._get_current_button_state()
            ev = xevent.MotionNotify(
                window=window_id,
                root=root_id,
                same_screen=1,
                root_x=screen_x,
                root_y=screen_y,
                time=time,
                detail=0,  # not used for motion
                state=state,
                event_x=target_x,
                event_y=target_y,
                child=0,
            )
            logger.debug(
                f"Forwarding MouseMove to ({target_x},{target_y}) with state {state}"
            )
            self._send_event(ev)

        elif event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
            # Convert Qt button to X11 button number
            qt_button = event.button()  # type: ignore
            x11_button = self._qt_button_to_x11(qt_button)

            if x11_button == 0:
                logger.warning(f"Ignoring unmapped button {qt_button}")
                return

            if event.type() == QEvent.MouseButtonPress:
                ev = xevent.ButtonPress(
                    window=window_id,
                    root=root_id,
                    same_screen=1,
                    root_x=screen_x,
                    root_y=screen_y,
                    time=time,
                    detail=x11_button,
                    state=0,  # no modifiers for press
                    event_x=target_x,
                    event_y=target_y,
                    child=0,
                )
                logger.debug(
                    f"Forwarding ButtonPress: button {x11_button} at ({target_x},{target_y})"
                )
            else:  # MouseButtonRelease
                ev = xevent.ButtonRelease(
                    window=window_id,
                    root=root_id,
                    same_screen=1,
                    root_x=screen_x,
                    root_y=screen_y,
                    time=time,
                    detail=x11_button,
                    state=0,
                    event_x=target_x,
                    event_y=target_y,
                    child=0,
                )
                logger.debug(
                    f"Forwarding ButtonRelease: button {x11_button} at ({target_x},{target_y})"
                )

            self._send_event(ev)

        else:
            logger.warning(f"Unexpected event type in _handle_mouse: {event.type()}")
