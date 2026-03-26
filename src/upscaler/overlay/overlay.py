import logging
import time
from typing import Any, List

from PySide6.QtCore import QEvent, Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QApplication

from .coordinates import CoordinateMapper
from .events import X11EventForwarder
from .geometry import compute_overlay_geometry, OverlayGeometry
from .opacity import OpacityController
from ..config import OverlayMode, Config
from ..window import WindowInfo

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
        self._config = config
        self._win_info = win_info

        # Compute geometry
        self._geometry = compute_overlay_geometry(config, win_info)
        self.scale_mode = self._geometry.scale_mode

        # Initialize subcomponents
        self._mapper = CoordinateMapper()
        self._forwarder = X11EventForwarder()
        self._should_forward = (
            config.overlay_mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value
        )
        self._forwarder.enabled = self._should_forward
        self._forwarder.target_handle = win_info.handle

        self._mapper.set_target_size(win_info.width, win_info.height)
        self._mapper.set_crop(
            self._geometry.crop_left,
            self._geometry.crop_top,
            self._geometry.crop_width,
            self._geometry.crop_height,
        )
        self._mapper.set_content_dimensions(
            self._geometry.content_width, self._geometry.content_height
        )

        # Set up the actual Qt window
        self._setup_window(self._geometry, config.overlay_mode)

        # Enable mouse tracking if we will forward events
        self.setMouseTracking(self._should_forward)

        # Create opacity controller
        self._opacity_controller = OpacityController(self, win_info)

        # Force final size after window flags are applied
        self.resize(self._geometry.overlay_width, self._geometry.overlay_height)
        QApplication.processEvents()

        # Store XID for logging only
        self.xid = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid}")

        # Install event filter if needed and X display is available
        if self._should_forward and self._forwarder.display is not None:
            self.installEventFilter(self)

        # Fallback if forwarder failed
        if self._should_forward and self._forwarder.display is None:
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

    def _setup_window(self, geometry: OverlayGeometry, mode: str) -> None:
        """Apply the appropriate window flags and geometry for the chosen mode."""
        width = geometry.overlay_width
        height = geometry.overlay_height
        x = geometry.overlay_x
        y = geometry.overlay_y

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

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """Update the crop region of the target window."""
        self._mapper.set_crop(left, top, width, height)

    def set_content_dimensions(self, width: int, height: int) -> None:
        """Update the logical content dimensions."""
        self._mapper.set_content_dimensions(width, height)

    def set_target_handle(self, handle: int) -> None:
        """Update the XID of the target window."""
        self._forwarder.target_handle = handle
        self._opacity_controller.update_target_info(
            handle, self._mapper.client_width, self._mapper.client_height
        )

    def set_target_size(self, width: int, height: int) -> None:
        """Update the actual target window size."""
        self._mapper.set_target_size(width, height)
        self._opacity_controller.update_target_info(
            self._forwarder.target_handle, width, height
        )

    def update_opacity(self) -> None:
        """Update the window opacity based on mouse position."""
        self._opacity_controller.update()

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """Quit the application when the overlay window is closed."""
        logger.info("Overlay window closed – quitting application.")
        self._opacity_controller.close()
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
        if self._forwarder.display is None or self._forwarder.target_handle is None:
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
