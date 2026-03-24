import logging
import time
from typing import Any, List, Optional, Union

from PySide6.QtCore import QEvent, Qt, Slot
from PySide6.QtWidgets import QMainWindow, QApplication

from .mapping import CoordinateMapper
from .mode import OverlayMode
from .x11 import X11EventForwarder

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """
    An overlay window that can present upscaled content in various modes.
    It can optionally forward mouse events to the target window using X11.

    The window delegates coordinate mapping to a CoordinateMapper instance and
    event forwarding to an X11EventForwarder instance.
    """

    def __init__(
        self,
        width: int,
        height: int,
        target: Any,  # WindowInfo instance (has handle, width, height)
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
    ) -> None:
        """
        Create and show the overlay window.

        Args:
            width, height: Desired size of the overlay window.
            target: WindowInfo object containing target window handle, size, etc.
            mode: OverlayMode value (e.g., FULLSCREEN, WINDOWED, ALWAYS_ON_TOP).
            initial_x, initial_y: Initial position (for windowed mode).
            content_width, content_height: Logical content size (if different from overlay).
            scale_mode: How the content is scaled within the overlay (stretch, etc.).
            background_color: Color for areas not covered by content.
            offset_x, offset_y: Offset of content relative to overlay (not used in mouse mapping?).
            crop_left, crop_top, crop_width, crop_height: Crop region of the target window.
        """
        super().__init__()
        start_time = time.perf_counter()
        logger.info(
            f"Initializing OverlayWindow: mode={mode}, size={width}x{height}, "
            f"target_handle={target.handle}, scale_mode={scale_mode}"
        )

        # Store configuration
        self.mode = OverlayMode(mode)  # ensure enum
        self._should_forward = self.mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT

        # Initialize components
        self._mapper = CoordinateMapper()
        self._forwarder = X11EventForwarder()
        self._forwarder.enabled = self._should_forward

        # Set target window info
        self._forwarder.target_handle = target.handle
        self._mapper.set_target_size(target.width, target.height)

        # Configure mapper with crop, offsets, etc.
        self._mapper.set_crop(
            crop_left,
            crop_top,
            crop_width if crop_width is not None else target.width,
            crop_height if crop_height is not None else target.height,
        )
        self._mapper.set_content_dimensions(
            content_width if content_width is not None else width,
            content_height if content_height is not None else height,
        )
        # Note: scaling_rect will be set later by the pipeline (via set_scaling_rect)

        # Other settings
        self.scale_mode = scale_mode
        self.background_color = background_color
        self.offset_x = offset_x
        self.offset_y = offset_y

        logger.debug(
            f"Overlay config: forward={self._should_forward}, "
            f"content={self._mapper.content_width}x{self._mapper.content_height}, "
            f"crop={self._mapper.crop_left},{self._mapper.crop_top} "
            f"{self._mapper.crop_width}x{self._mapper.crop_height}, "
            f"offsets=({offset_x},{offset_y})"
        )

        # Set up the actual Qt window
        self._setup_window(width, height, initial_x, initial_y)

        # Enable mouse tracking if we will forward events
        self.setMouseTracking(self._should_forward)

        # Force final size after window flags are applied
        self.resize(width, height)
        QApplication.processEvents()

        # Store XID for logging only (not used directly)
        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        # Install event filter to catch mouse events if needed
        if self._should_forward and self._forwarder._display is not None:
            self.installEventFilter(self)

        # If forwarder failed to open display, fall back to click-through
        if self._should_forward and self._forwarder._display is None:
            logger.warning(
                "Event forwarding disabled due to X display failure. Window is now click-through."
            )
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()

        logger.debug(
            f"OverlayWindow initialized in {(time.perf_counter() - start_time)*1000:.2f} ms"
        )

    @property
    def content_width(self) -> int:
        """Logical content width (before scaling)."""
        return self._mapper.content_width

    @property
    def content_height(self) -> int:
        """Logical content height (before scaling)."""
        return self._mapper.content_height

    @property
    def map_events(self) -> bool:
        """True if mouse events should be forwarded to the target window."""
        return self._should_forward

    @property
    def scaling_rect(self) -> List[int]:
        """Rectangle (x, y, width, height) in overlay coordinates where content is drawn."""
        return self._mapper.scaling_rect

    @scaling_rect.setter
    def scaling_rect(self, rect: List[int]) -> None:
        self._mapper.set_scaling_rect(rect)

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

    def set_scaling_rect(self, rect: List[int]) -> None:
        """Set the rectangle (in overlay screen coordinates) where content is drawn."""
        self._mapper.set_scaling_rect(rect)

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """Update the crop region of the target window."""
        self._mapper.set_crop(left, top, width, height)

    def set_content_dimensions(self, width: int, height: int) -> None:
        """Update the logical content dimensions."""
        self._mapper.set_content_dimensions(width, height)

    def set_target_handle(self, handle: int) -> None:
        """Update the XID of the target window."""
        self._forwarder.target_handle = handle

    def set_target_size(self, width: int, height: int) -> None:
        """Update the actual target window size."""
        self._mapper.set_target_size(width, height)

    def disable_click_forwarding(self) -> None:
        """Permanently disable forwarding (e.g., target window destroyed)."""
        if self._should_forward:
            logger.info("Disabling click forwarding.")
            self._should_forward = False
            self._forwarder.enabled = False
            self._forwarder.target_handle = None
            # Make window click-through
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()

    def changeEvent(self, event: QEvent) -> None:
        """Detect window state changes (minimized) to enable/disable forwarding."""
        if event.type() == QEvent.WindowStateChange:
            minimized = bool(self.windowState() & Qt.WindowMinimized)
            if minimized and self._forwarder.enabled:
                logger.debug("Window minimized – disabling event forwarding")
                self._forwarder.enabled = False
            elif not minimized and not self._forwarder.enabled and self._should_forward:
                logger.debug("Window restored – enabling event forwarding")
                self._forwarder.enabled = True
        super().changeEvent(event)

    def closeEvent(self, event: QEvent) -> None:
        """Quit the application when the overlay window is closed."""
        logger.info("Overlay window closed – quitting application.")
        self._forwarder.close()
        QApplication.quit()
        super().closeEvent(event)

    @Slot()
    def on_pipeline_stopped(self) -> None:
        """Called from the pipeline thread when it exits due to an error."""
        logger.info("Pipeline stopped – quitting application.")
        QApplication.quit()

    def eventFilter(self, obj: Any, event: QEvent) -> bool:
        """Filter mouse events and forward them when forwarding is enabled."""
        if not self._should_forward or not self._forwarder.enabled:
            return super().eventFilter(obj, event)

        # Only handle mouse events we care about
        if event.type() in (
            QEvent.MouseMove,
            QEvent.MouseButtonPress,
            QEvent.MouseButtonRelease,
            QEvent.Wheel,
        ):
            self._handle_mouse(event)
            return True  # swallow the event (so it doesn't reach the underlying window)

        return super().eventFilter(obj, event)

    def _handle_mouse(self, event: QEvent) -> None:
        """
        Convert a Qt mouse event to X11 events and forward them.

        This method uses the CoordinateMapper to transform overlay coordinates
        to target window coordinates, then calls the appropriate forwarder method.
        """
        if self._forwarder._display is None or self._forwarder.target_handle is None:
            logger.debug("_handle_mouse called but forwarding not available")
            return

        pos = event.position().toPoint()  # local overlay coordinates
        screen_x = event.globalPosition().x()  # root X coordinate
        screen_y = event.globalPosition().y()  # root Y coordinate

        # Map local to target coordinates
        target_x, target_y, inside = self._mapper.map(pos.x(), pos.y())
        if not inside:
            logger.debug(
                f"Ignoring mouse event outside scaling rect: ({pos.x()},{pos.y()})"
            )
            return

        # Dispatch based on event type
        if event.type() == QEvent.MouseMove:
            state = self._forwarder.get_current_button_state()
            self._forwarder.forward_motion(
                int(screen_x), int(screen_y), target_x, target_y, state
            )
        elif event.type() == QEvent.MouseButtonPress:
            self._forwarder.forward_button(
                event.button(), True, int(screen_x), int(screen_y), target_x, target_y
            )
        elif event.type() == QEvent.MouseButtonRelease:
            self._forwarder.forward_button(
                event.button(), False, int(screen_x), int(screen_y), target_x, target_y
            )
        elif event.type() == QEvent.Wheel:
            delta = event.angleDelta()
            # Process vertical and horizontal separately (Qt may combine both)
            if delta.y() != 0:
                self._forwarder.forward_wheel(
                    delta.y(), False, int(screen_x), int(screen_y), target_x, target_y
                )
            if delta.x() != 0:
                self._forwarder.forward_wheel(
                    delta.x(), True, int(screen_x), int(screen_y), target_x, target_y
                )
        else:
            logger.warning(f"Unexpected event type in _handle_mouse: {event.type()}")
