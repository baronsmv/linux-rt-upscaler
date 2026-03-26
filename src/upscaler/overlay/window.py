import logging
import time
from typing import Any, List

from PySide6.QtCore import QEvent, Qt, Slot
from PySide6.QtWidgets import QMainWindow, QApplication

from .mapping import CoordinateMapper
from .x11 import X11EventForwarder
from ..utils.config import Config, OverlayMode
from ..utils.parsers import parse_output_geometry
from ..utils.screen import get_screen, get_screen_geometry
from ..utils.window import WindowInfo

logger = logging.getLogger(__name__)


class OverlayWindow(QMainWindow):
    """
    An overlay window that can present upscaled content in various modes.
    It can optionally forward mouse events to the target window using X11.

    The window delegates coordinate mapping to a CoordinateMapper instance and
    event forwarding to an X11EventForwarder instance.
    """

    def __init__(self, config: Config, win_info: WindowInfo) -> None:
        """
        Create and show the overlay window.

        Args:
            config: Full configuration (includes monitor, offsets, crop, etc.)
            win_info: Information about the target window.
        """
        super().__init__()
        start_time = time.perf_counter()
        logger.info(
            f"Initializing OverlayWindow: mode={config.overlay_mode}, "
            f"target_handle={win_info.handle}, scale_mode={config.output_geometry}"
        )

        # Store references
        self.config = config
        self.win_info = win_info

        # Determine base screen geometry
        monitor = get_screen(config.monitor)
        base_x, base_y, base_w, base_h = get_screen_geometry(
            monitor, config.scale_factor
        )

        # Parse output geometry (initial pass using original window dimensions)
        overlay_w, overlay_h, content_w, content_h, mode = parse_output_geometry(
            config.output_geometry, win_info.width, win_info.height, base_w, base_h
        )

        # Compute overlay position and content offsets
        if config.overlay_mode == OverlayMode.WINDOWED.value:
            win_x = base_x + (base_w - overlay_w) // 2 + config.offset_x
            win_y = base_y + (base_h - overlay_h) // 2 + config.offset_y
            content_offset_x = 0
            content_offset_y = 0
        else:
            win_x = base_x
            win_y = base_y
            overlay_w = base_w
            overlay_h = base_h
            content_offset_x = config.offset_x
            content_offset_y = config.offset_y

        # Compute cropped dimensions
        self.crop_width = win_info.width - config.crop_left - config.crop_right
        self.crop_height = win_info.height - config.crop_top - config.crop_bottom
        if self.crop_width <= 0 or self.crop_height <= 0:
            raise ValueError(
                f"Invalid crop: resulting dimensions {self.crop_width}x{self.crop_height} "
                f"(original {win_info.width}x{win_info.height})"
            )

        # Re‑parse output geometry using cropped dimensions (final content size)
        final_content_w, final_content_h, _, _, mode = parse_output_geometry(
            config.output_geometry, self.crop_width, self.crop_height, base_w, base_h
        )

        # Store for later use
        self.overlay_w = overlay_w
        self.overlay_h = overlay_h
        self.win_x = win_x
        self.win_y = win_y
        self.content_w = final_content_w
        self.content_h = final_content_h
        self.scale_mode = mode
        self.crop_left = config.crop_left
        self.crop_top = config.crop_top
        self.crop_right = config.crop_right
        self.crop_bottom = config.crop_bottom
        self.offset_x = content_offset_x
        self.offset_y = content_offset_y
        self.background_color = config.background_color

        # Initialize mapper and forwarder (as before)
        self._mapper = CoordinateMapper()
        self._forwarder = X11EventForwarder()
        self._should_forward = (
            config.overlay_mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value
        )
        self._forwarder.enabled = self._should_forward
        self._forwarder.target_handle = win_info.handle

        self._mapper.set_target_size(win_info.width, win_info.height)
        self._mapper.set_crop(
            self.crop_left, self.crop_top, self.crop_width, self.crop_height
        )
        self._mapper.set_content_dimensions(final_content_w, final_content_h)

        # Set up the actual Qt window
        self._setup_window(overlay_w, overlay_h, win_x, win_y, config.overlay_mode)

        # Enable mouse tracking if we will forward events
        self.setMouseTracking(self._should_forward)

        # Force final size after window flags are applied
        self.resize(overlay_w, overlay_h)
        QApplication.processEvents()

        # Store XID for logging only
        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        # Install event filter if needed and X display is available
        if self._should_forward and self._forwarder._display is not None:
            self.installEventFilter(self)

        # Fallback if forwarder failed
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

    def _setup_window(self, width: int, height: int, x: int, y: int, mode: str) -> None:
        """Apply the appropriate window flags and geometry for the chosen mode."""
        flags = Qt.Window

        if mode == OverlayMode.FULLSCREEN.value:
            flags |= Qt.FramelessWindowHint
            self.setGeometry(x, y, width, height)
            self.showFullScreen()
            logger.info(
                f"Overlay set to fullscreen on geometry ({x},{y},{width}x{height})"
            )
            return

        if mode == OverlayMode.WINDOWED.value:
            self.setGeometry(x, y, width, height)
            self.setFixedSize(width, height)
            logger.info(
                f"Overlay set to windowed mode at ({x},{y}) size {width}x{height}"
            )
        elif mode == OverlayMode.ALWAYS_ON_TOP.value:
            flags |= Qt.X11BypassWindowManagerHint
            self.setGeometry(x, y, width, height)
            logger.info(
                f"Overlay set to always-on-top mode at ({x},{y}) size {width}x{height}"
            )
        elif mode == OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value:
            flags |= Qt.X11BypassWindowManagerHint | Qt.WindowTransparentForInput
            self.setGeometry(x, y, width, height)
            logger.info(
                f"Overlay set to transparent always-on-top mode at ({x},{y}) size {width}x{height}"
            )
        else:
            raise ValueError(f"Unknown overlay mode: {mode}")

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
