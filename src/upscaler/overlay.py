import logging
import time
from typing import Any, List, Optional, Tuple, Union

from PySide6.QtCore import QEvent, QPoint, Qt, Slot
from PySide6.QtWidgets import QMainWindow, QApplication
from Xlib import X, display
from Xlib.protocol import event as xevent

from .utils.config import OverlayMode

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """
    An overlay window that can present upscaled content in various modes.
    It can optionally forward mouse events to the target window.
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
        offset_x: int = 0,
        offset_y: int = 0,
        crop_left: int = 0,
        crop_top: int = 0,
        crop_width: Optional[int] = None,
        crop_height: Optional[int] = None,
        scale_factor: float = 1.0,
    ) -> None:
        """
        Create and show the overlay window.

        :param width:           Desired width of the overlay (may be larger than screen).
        :param height:          Desired height.
        :param mode:            OverlayMode value.
        :param target:          WindowInfo of the target window.
        :param initial_x:       Initial X position (for windowed mode).
        :param initial_y:       Initial Y position.
        :param content_width:   Logical width of the content (if different from overlay).
        :param content_height:  Logical height of the content.
        :param scale_mode:      How the content is scaled within the overlay.
        :param background_color: Color for areas not covered by content.
        """
        super().__init__()
        start_time = time.perf_counter()
        logger.info(
            f"Initializing OverlayWindow: mode={mode}, size={width}x{height}, "
            f"target_handle={target.handle}, scale_mode={scale_mode}"
        )

        self.mode = mode
        self.map_events = mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT

        self.scaling_rect: List[int] = [0, 0, 0, 0]  # x, y, w, h
        self.target_handle = target.handle
        self.client_width = target.width
        self.client_height = target.height
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_width = crop_width if crop_width is not None else self.client_width
        self.crop_height = (
            crop_height if crop_height is not None else self.client_height
        )

        self.content_width = content_width if content_width is not None else width
        self.content_height = content_height if content_height is not None else height
        self.scale_mode = scale_mode
        self.scale_factor = scale_factor
        self.background_color = background_color

        # X11 connection for event forwarding
        self._x_display: Optional[display.Display] = None
        self._x_root: Optional[int] = None

        # Forwarding enabled (disabled when minimized)
        self._forwarding_enabled = self.map_events

        # Log the configuration
        logger.debug(
            f"Overlay config: map_events={self.map_events}, forwarding_enabled={self._forwarding_enabled}, "
            f"content={self.content_width}x{self.content_height}, crop={self.crop_left},{self.crop_top} "
            f"{self.crop_width}x{self.crop_height}, offsets=({offset_x},{offset_y})"
        )

        # Set window flags and geometry according to mode
        self._setup_window(width, height, initial_x, initial_y)

        self.setMouseTracking(self.map_events)  # track mouse moves only if mapping
        self.resize(width, height)  # force size after possible WM interference
        QApplication.processEvents()

        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        if self.map_events:
            self._open_x_display()
            self.installEventFilter(self)

        logger.debug(
            f"OverlayWindow initialized in {(time.perf_counter() - start_time)*1000:.2f} ms"
        )

    def _setup_window(self, width: int, height: int, x: int, y: int) -> None:
        """Apply the appropriate window flags and geometry for the chosen mode."""
        flags = Qt.Window

        if self.mode == OverlayMode.FULLSCREEN:
            flags |= Qt.FramelessWindowHint
            self.setGeometry(x, y, width, height)
            self.showFullScreen()
            logger.info(
                f"Overlay set to fullscreen on geometry ({x},{y},{width}x{height})"
            )
            return

        if self.mode == OverlayMode.WINDOWED:
            self.setGeometry(x, y, width, height)
            self.setFixedSize(width, height)
            logger.info(
                f"Overlay set to windowed mode at ({x},{y}) size {width}x{height}"
            )
        elif self.mode == OverlayMode.ALWAYS_ON_TOP:
            flags |= Qt.X11BypassWindowManagerHint
            self.setGeometry(x, y, width, height)
            logger.info(
                f"Overlay set to always-on-top mode at ({x},{y}) size {width}x{height}"
            )
        elif self.mode == OverlayMode.ALWAYS_ON_TOP_TRANSPARENT:
            flags |= Qt.X11BypassWindowManagerHint | Qt.WindowTransparentForInput
            self.setGeometry(x, y, width, height)
            logger.info(
                f"Overlay set to transparent always-on-top mode at ({x},{y}) size {width}x{height}"
            )
        else:
            raise ValueError(f"Unknown overlay mode: {self.mode}")

        self.setWindowFlags(flags)
        self.show()

    def changeEvent(self, event: QEvent) -> None:
        """Detect window state changes (minimized) to enable/disable forwarding."""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                if self._forwarding_enabled:
                    logger.debug("Window minimized – disabling event forwarding")
                    self._forwarding_enabled = False
            else:
                if not self._forwarding_enabled:
                    logger.debug("Window restored – enabling event forwarding")
                    self._forwarding_enabled = True
        super().changeEvent(event)

    def closeEvent(self, event: QEvent) -> None:
        """Quit the application when the overlay window is closed."""
        logger.info("Overlay window closed – quitting application.")
        QApplication.quit()
        self._close_x_display()
        super().closeEvent(event)

    def _x_error_handler(self, error: Any, request: Any) -> None:
        """
        Custom X error handler – suppresses default stderr printing and logs silently.
        """
        if hasattr(error, "get_text"):
            error_text = error.get_text()
        else:
            error_text = str(error)
        logger.debug(f"X error: {error_text} (request: {request})")

    def _open_x_display(self) -> None:
        """Open a connection to the X server and install a custom error handler."""
        try:
            self._x_display = display.Display()
            self._x_root = int(self._x_display.screen().root.id)
            self._x_display.set_error_handler(self._x_error_handler)
            logger.debug(
                f"Opened X display with custom error handler. Root: {self._x_root}"
            )
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
            logger.warning(
                "Event forwarding disabled due to X display failure. Window is now click-through."
            )

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
        if self.scaling_rect != rect:
            self.scaling_rect = rect
            logger.debug(f"Scaling rect set to {rect}")
        else:
            logger.debug(f"Scaling rect unchanged ({rect})")

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
        Transform overlay local coordinates to target window client coordinates
        using the pipeline's computed scaling rectangle.
        """
        rect = self.scaling_rect
        if len(rect) != 4:
            logger.error(f"Invalid scaling rect {rect}, cannot map")
            return 0, 0, False

        rx, ry, rw, rh = rect
        if rw == 0 or rh == 0:
            logger.info("Scaling rect has zero size, cannot map")
            return 0, 0, False

        # Check if the click is inside the content area
        if not (rx <= local_x < rx + rw and ry <= local_y < ry + rh):
            logger.debug(
                f"Click at ({local_x},{local_y}) outside scaling rect ({rx},{ry},{rw},{rh})"
            )
            return 0, 0, False

        # Compute position within the content rectangle (normalized)
        norm_x = (local_x - rx) / rw * self.scale_factor
        norm_y = (local_y - ry) / rh * self.scale_factor

        # Map to content coordinates (logical content size)
        content_x = int(norm_x * self.content_width)
        content_y = int(norm_y * self.content_height)

        # Clamp to content bounds
        content_x = max(0, min(content_x, self.content_width - 1))
        content_y = max(0, min(content_y, self.content_height - 1))

        # Apply crop transformation to get target window coordinates
        target_x = self.crop_left + int(
            content_x * self.crop_width / self.content_width
        )
        target_y = self.crop_top + int(
            content_y * self.crop_height / self.content_height
        )

        # Clamp to window bounds
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))

        logger.debug(
            f"Mapped: ({local_x},{local_y}) -> content ({content_x},{content_y}) -> target ({target_x},{target_y})"
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
        # Log only if non-zero to reduce noise
        if state:
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

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """Update the crop region (used for mouse mapping)."""
        if (left, top, width, height) != (
            self.crop_left,
            self.crop_top,
            self.crop_width,
            self.crop_height,
        ):
            self.crop_left = left
            self.crop_top = top
            self.crop_width = width
            self.crop_height = height
            logger.debug(
                f"Overlay crop updated: left={left}, top={top}, size={width}x{height}"
            )
        else:
            logger.debug("Overlay crop unchanged")

    def set_content_dimensions(self, width: int, height: int) -> None:
        """Update the logical content dimensions (used for mouse mapping)."""
        if (width, height) != (self.content_width, self.content_height):
            self.content_width = width
            self.content_height = height
            logger.debug(f"Overlay content dimensions updated to {width}x{height}")
        else:
            logger.debug("Overlay content dimensions unchanged")

    def set_target_handle(self, handle: int) -> None:
        """Update the XID of the target window (used for sending events)."""
        if handle != self.target_handle:
            self.target_handle = handle
            logger.debug(f"Overlay target handle updated to {handle}")
        else:
            logger.debug("Overlay target handle unchanged")

    def set_target_size(self, width: int, height: int) -> None:
        """Update the actual target window size (used for clamping mouse coordinates)."""
        if (width, height) != (self.client_width, self.client_height):
            self.client_width = width
            self.client_height = height
            logger.debug(f"Overlay target size updated to {width}x{height}")
        else:
            logger.debug("Overlay target size unchanged")

    @Slot()
    def on_pipeline_stopped(self) -> None:
        """Called from the pipeline thread when it exits due to an error."""
        logger.info("Pipeline stopped – quitting application.")
        QApplication.quit()
