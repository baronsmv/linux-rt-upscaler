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
    An overlay window that presents upscaled content and forwards mouse events.

    The overlay adapts to the chosen mode (always-on-top, fullscreen, windowed,
    or transparent click-through). It uses a CoordinateMapper to translate
    overlay-relative mouse coordinates to target window coordinates, and an
    X11EventForwarder to send synthetic events.

    Attributes:
        content_width (int): Logical width of the upscaled content (before scaling).
        content_height (int): Logical height of the upscaled content.
        map_events (bool): Whether mouse events are currently being forwarded.
        scaling_rect (List[int]): The rectangle (x, y, w, h) in overlay coordinates
                                  where the content is drawn.
    """

    def __init__(self, config: Config, win_info: WindowInfo) -> None:
        """
        Create and show the overlay window.

        Args:
            config: Full configuration (monitor, offsets, crop, overlay mode, etc.).
            win_info: Initial information about the target window.
        """
        super().__init__()
        start_time = time.perf_counter()
        logger.info(
            f"Initializing OverlayWindow: mode={config.overlay_mode}, "
            f"target_handle={win_info.handle:#x}, scale_mode={config.output_geometry}"
        )

        # Store configuration and window info
        self._config = config
        self._win_info = win_info

        # Transparency support (if background has alpha or we want click-through)
        if self._config.background_color[3] < 1.0:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setStyleSheet("background: transparent;")

        # Compute initial geometry
        self._geometry = compute_overlay_geometry(config, win_info)
        self.scale_mode: str = self._geometry.scale_mode

        # Initialize subcomponents
        self._mapper = CoordinateMapper()
        self._forwarder = X11EventForwarder()

        # Determine whether we should forward events
        self._should_forward = (
            config.overlay_mode != OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value
        )
        self._forwarder.enabled = self._should_forward
        self._forwarder.target_handle = win_info.handle

        # Configure coordinate mapper with initial values
        self._update_mapper()

        # Set up the Qt window according to mode
        self._setup_window(self._geometry, config.overlay_mode)

        # Enable mouse tracking if we forward events
        self.setMouseTracking(self._should_forward)

        # Opacity controller (dim overlay when mouse leaves target window)
        self._opacity_controller = OpacityController(self, win_info)

        # Force final geometry after window flags are applied
        self.resize(self._geometry.overlay_width, self._geometry.overlay_height)

        # Store XID for debugging
        self.xid: int = int(self.winId())
        logger.debug(f"Overlay XID: {self.xid:#x}")

        # Install event filter for mouse forwarding
        if self._should_forward and self._forwarder.conn is not None:
            self.installEventFilter(self)
        elif self._should_forward and self._forwarder.conn is None:
            logger.warning(
                "Event forwarding disabled due to XCB failure. Window is now click-through."
            )
            flags = self.windowFlags() | Qt.WindowTransparentForInput
            self.setWindowFlags(flags)
            self.show()

        logger.debug(
            f"OverlayWindow initialized in {(time.perf_counter() - start_time) * 1000:.2f} ms"
        )

    # ----------------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------------

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

    # ----------------------------------------------------------------------
    # Internal setup
    # ----------------------------------------------------------------------

    def _setup_window(self, geometry: OverlayGeometry, mode: str) -> None:
        """
        Apply the appropriate window flags and geometry for the chosen mode.

        Args:
            geometry: OverlayGeometry object containing all required dimensions.
            mode: One of the OverlayMode values.
        """
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

    def _update_mapper(self) -> None:
        """Update the coordinate mapper with current crop, content, and target sizes."""
        self._mapper.set_target_size(self._win_info.width, self._win_info.height)
        self._mapper.set_crop(
            self._geometry.crop_left,
            self._geometry.crop_top,
            self._geometry.crop_width,
            self._geometry.crop_height,
        )
        self._mapper.set_content_dimensions(
            self._geometry.content_width, self._geometry.content_height
        )

    # ----------------------------------------------------------------------
    # Public update methods (called from pipeline or focus monitor)
    # ----------------------------------------------------------------------

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """
        Update the crop region of the target window.

        Args:
            left, top: Offset from target window origin.
            width, height: Size of the cropped region.
        """
        self._mapper.set_crop(left, top, width, height)

    def set_content_dimensions(self, width: int, height: int) -> None:
        """
        Update the logical content dimensions.

        Args:
            width: New content width.
            height: New content height.
        """
        self._mapper.set_content_dimensions(width, height)

    def set_target_handle(self, handle: int) -> None:
        """
        Update the X11 window ID of the target window.

        Args:
            handle: New target window XID.
        """
        self._forwarder.target_handle = handle
        self._opacity_controller.update_target_info(
            handle, self._mapper.client_width, self._mapper.client_height
        )

    def set_target_size(self, width: int, height: int) -> None:
        """
        Update the actual target window dimensions.

        Args:
            width: New target width.
            height: New target height.
        """
        self._mapper.set_target_size(width, height)
        self._opacity_controller.update_target_info(
            self._forwarder.target_handle, width, height
        )

    def update_geometry(self, win_info: WindowInfo) -> None:
        """
        Recompute overlay geometry after a window or monitor change.

        Args:
            win_info: Updated target window information.
        """
        self._win_info = win_info
        self._geometry = compute_overlay_geometry(self._config, win_info)
        self.scale_mode = self._geometry.scale_mode
        self._update_mapper()

        # Apply new geometry to the overlay window
        if self._config.overlay_mode == OverlayMode.FULLSCREEN.value:
            # Fullscreen mode uses the entire monitor, so no resize needed
            pass
        else:
            self.setGeometry(
                self._geometry.overlay_x,
                self._geometry.overlay_y,
                self._geometry.overlay_width,
                self._geometry.overlay_height,
            )
            if self._config.overlay_mode == OverlayMode.WINDOWED.value:
                self.setFixedSize(
                    self._geometry.overlay_width, self._geometry.overlay_height
                )

        logger.info(
            f"Overlay geometry updated: {self._geometry.overlay_width}x{self._geometry.overlay_height}"
        )

    def update_opacity(self) -> None:
        """Update the window opacity based on mouse position relative to target."""
        self._opacity_controller.update()

    # ----------------------------------------------------------------------
    # Qt event handlers
    # ----------------------------------------------------------------------

    def changeEvent(self, event: QEvent) -> None:
        """
        Detect window state changes (minimized) to enable/disable event forwarding.

        Args:
            event: The change event.
        """
        if event.type() == QEvent.WindowStateChange:
            minimized = bool(self.windowState() & Qt.WindowMinimized)
            if minimized and self._forwarder.enabled:
                logger.debug("Window minimized - disabling event forwarding")
                self._forwarder.enabled = False
            elif not minimized and not self._forwarder.enabled and self._should_forward:
                logger.debug("Window restored - enabling event forwarding")
                self._forwarder.enabled = True
        super().changeEvent(event)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Quit the application when the overlay window is closed.

        Args:
            event: The close event.
        """
        logger.info("Overlay window closed - quitting application.")
        self._opacity_controller.close()
        self._forwarder.close()
        QApplication.quit()
        super().closeEvent(event)

    @Slot()
    def on_pipeline_stopped(self) -> None:
        """Slot called from the pipeline thread when it exits due to an error."""
        logger.info("Pipeline stopped - quitting application.")
        QApplication.quit()

    @Slot(str)
    def set_scale_mode(self, mode: str) -> None:
        """
        Set the scaling mode (fit, stretch, cover) dynamically.

        Args:
            mode: New scaling mode string.
        """
        self.scale_mode = mode

    # ----------------------------------------------------------------------
    # Mouse event forwarding
    # ----------------------------------------------------------------------

    def eventFilter(self, obj: Any, event: QEvent) -> bool:
        """
        Filter mouse events and forward them when forwarding is enabled.

        Args:
            obj: The object that generated the event.
            event: The event to filter.

        Returns:
            True if the event was handled (and should not be processed further),
            False otherwise.
        """
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

            # Swallow the event (prevents interaction with underlying window)
            return True

        return super().eventFilter(obj, event)

    def _handle_mouse(self, event: QEvent) -> None:
        """
        Convert a Qt mouse event to X11 events and forward them.

        This method uses the CoordinateMapper to transform overlay coordinates
        to target window coordinates, then calls the appropriate forwarder method.

        Args:
            event: The Qt mouse event (MouseMove, ButtonPress, ButtonRelease, or Wheel).
        """
        if self._forwarder.conn is None or self._forwarder.target_handle is None:
            logger.debug("_handle_mouse called but forwarding not available")
            return

        # Get positions
        pos = event.position().toPoint()  # local overlay coordinates
        screen_x = int(event.globalPosition().x())  # root X coordinate
        screen_y = int(event.globalPosition().y())  # root Y coordinate

        # Map to target window coordinates
        target_x, target_y, inside = self._mapper.map(pos.x(), pos.y())
        if not inside:
            logger.debug(
                f"Ignoring mouse event outside scaling rect: ({pos.x()},{pos.y()})"
            )
            return

        # Dispatch based on event type
        if event.type() == QEvent.MouseMove:
            self._forwarder.forward_motion(screen_x, screen_y, target_x, target_y)

        elif event.type() == QEvent.MouseButtonPress:
            self._forwarder.forward_button(
                event.button(), True, screen_x, screen_y, target_x, target_y
            )

        elif event.type() == QEvent.MouseButtonRelease:
            self._forwarder.forward_button(
                event.button(), False, screen_x, screen_y, target_x, target_y
            )

        elif event.type() == QEvent.Wheel:
            delta = event.angleDelta()
            # Process vertical and horizontal separately
            if delta.y() != 0:
                self._forwarder.forward_wheel(
                    delta.y(), False, screen_x, screen_y, target_x, target_y
                )
            if delta.x() != 0:
                self._forwarder.forward_wheel(
                    delta.x(), True, screen_x, screen_y, target_x, target_y
                )

        else:
            logger.warning(f"Unexpected event type in _handle_mouse: {event.type()}")
