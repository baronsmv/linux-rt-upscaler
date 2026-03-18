import logging
from enum import Enum
from typing import Any, List, Optional, Tuple, Union

from PySide6.QtCore import QEvent, QPoint, Qt, Slot
from PySide6.QtWidgets import QMainWindow, QApplication
from Xlib import X, display
from Xlib.protocol import event as xevent

logger = logging.getLogger(__name__)


class OverlayMode(str, Enum):
    # Always on top, click‑through or forwards (bypasses window manager)
    ALWAYS_ON_TOP = "always-on-top"

    # Always on top, click‑through (bypasses window manager)
    ALWAYS_ON_TOP_TRANSPARENT = "top-transparent"

    # Fullscreen without decorations
    FULLSCREEN = "fullscreen"

    # Normal window with decorations, fixed size
    WINDOWED = "windowed"


class OverlayWindow(QMainWindow):
    """
    An overlay window that can present upscaled content in various modes.
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
        width: int,
        height: int,
        target: Any,  # WindowInfo instance
        mode: Union[OverlayMode, str],
        initial_x: int = 0,
        initial_y: int = 0,
        content_width: Optional[int] = None,
        content_height: Optional[int] = None,
        scale_mode: str = "stretch",
        background_color: str = "black",
    ) -> None:
        """
        Create and show the overlay window.

        :param width:  Desired width of the overlay (for windowed mode) or full screen size.
        :param height: Desired height.
        :param mode:   OverlayMode value.
        :param target: X11 window of the target.
        :param initial_x: Initial X position (windowed mode only).
        :param initial_y: Initial Y position.
        """
        super().__init__()
        logger.info(
            f"Initializing OverlayWindow: mode={mode}, size={width}x{height}, "
            f", target_handle={target.handle}"
        )

        self.mode = mode
        self.map_events = mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT

        self.scaling_rect: List[int] = [0, 0, 0, 0]  # x, y, w, h
        self.target_handle = target.handle
        self.client_width = target.width
        self.client_height = target.height

        self.content_width = content_width if content_width is not None else width
        self.content_height = content_height if content_height is not None else height
        self.scale_mode = scale_mode
        self.background_color = background_color

        # X11 connection for event forwarding (to track mouse events)
        self._x_display: Optional[display.Display] = None
        self._x_root: Optional[int] = None

        # Forwarding enabled (disabled when minimized)
        self._forwarding_enabled = self.map_events

        # Set window flags and geometry according to mode
        self._setup_window(width, height, initial_x, initial_y)

        self.setMouseTracking(self.map_events)  # track mouse moves only if mapping
        self.show()
        self.resize(width, height)
        QApplication.processEvents()

        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        if self.map_events:
            self._open_x_display()
            self.installEventFilter(self)

    def _setup_window(self, width: int, height: int, x: int, y: int) -> None:
        """Apply the appropriate window flags and geometry for the chosen mode."""
        flags = Qt.Window

        if self.mode == OverlayMode.FULLSCREEN:
            flags |= Qt.FramelessWindowHint
            self.setGeometry(x, y, width, height)

        elif self.mode == OverlayMode.WINDOWED:
            self.setGeometry(x, y, width, height)
            self.setFixedSize(width, height)

        elif self.mode == OverlayMode.ALWAYS_ON_TOP:
            flags |= Qt.X11BypassWindowManagerHint
            self.setGeometry(x, y, width, height)

        elif self.mode == OverlayMode.ALWAYS_ON_TOP_TRANSPARENT:
            flags |= Qt.X11BypassWindowManagerHint | Qt.WindowTransparentForInput
            self.setGeometry(x, y, width, height)

        else:
            raise ValueError(f"Unknown overlay mode: {self.mode}")

        self.setWindowFlags(flags)

        if self.mode == OverlayMode.FULLSCREEN:
            self.showFullScreen()
        else:
            self.show()

    def changeEvent(self, event: QEvent) -> None:
        """Detect window state changes (minimized) to enable/disable forwarding."""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                logger.debug("Window minimized – disabling event forwarding")
                self._forwarding_enabled = False
            else:
                logger.debug("Window restored – enabling event forwarding")
                self._forwarding_enabled = True
        super().changeEvent(event)

    def closeEvent(self, event: Any) -> None:
        """Quit the application when the overlay window is closed."""
        logger.info("Overlay window closed – quitting application.")
        QApplication.quit()
        self._close_x_display()
        super().closeEvent(event)

    def _x_error_handler(self, error, request) -> None:
        """
        Custom X error handler – suppresses default stderr printing and logs silently.
        """
        logger.debug(f"X error: {error} (type: {type(error).__name__})")

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
            self.map_events = False
            self._forwarding_enabled = False
            # Fallback to click‑through
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()

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
        """Permanently disable forwarding (e.g., target window destroyed)."""
        if self.map_events:
            logger.info("Disabling click forwarding.")
            self.map_events = False
            self._forwarding_enabled = False
            self.target_handle = None
            self._close_x_display()
            # Make window click‑through
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()

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
        """Filter mouse events and forward them when map_events is enabled."""
        if not self.map_events or not self._forwarding_enabled:
            return super().eventFilter(obj, event)

        if event.type() in (
            QEvent.MouseMove,
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
        ):
            self._handle_mouse(event)
            return True

        return super().eventFilter(obj, event)

    def _map_coordinates(self, local_x: int, local_y: int) -> Tuple[int, int, bool]:
        """
        Transform overlay local coordinates to target window client coordinates.
        Returns (target_x, target_y, inside_flag).
        """
        win_w = self.width()
        win_h = self.height()

        # Step 1: overlay -> content coordinates
        if self.scale_mode == "stretch":
            # content fills overlay exactly
            cx = local_x * self.content_width / win_w
            cy = local_y * self.content_height / win_h

        elif self.scale_mode == "fit":
            # content centered, scaled to fit
            scale = min(win_w / self.content_width, win_h / self.content_height)
            out_w = self.content_width * scale
            out_h = self.content_height * scale
            off_x = (win_w - out_w) / 2
            off_y = (win_h - out_h) / 2
            if off_x <= local_x < off_x + out_w and off_y <= local_y < off_y + out_h:
                cx = (local_x - off_x) * self.content_width / out_w
                cy = (local_y - off_y) * self.content_height / out_h
            else:
                return 0, 0, False

        elif self.scale_mode == "cover":
            # content scaled to cover overlay, then cropped
            scale = max(win_w / self.content_width, win_h / self.content_height)
            content_drawn_w = self.content_width * scale
            content_drawn_h = self.content_height * scale
            off_x = (content_drawn_w - win_w) / 2
            off_y = (content_drawn_h - win_h) / 2
            cx = (off_x + local_x) * self.content_width / content_drawn_w
            cy = (off_y + local_y) * self.content_height / content_drawn_h

        else:
            return 0, 0, False

        # Step 2: content -> target window coordinates
        target_x = int(cx * self.client_width / self.content_width)
        target_y = int(cy * self.client_height / self.content_height)

        # Clamp to valid range
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))

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

    @Slot()
    def on_pipeline_stopped(self):
        """Called from the pipeline thread when it exits due to an error."""
        logger.info("Pipeline stopped – quitting application.")
        QApplication.quit()
