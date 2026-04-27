import logging
import time
from typing import Optional

import xcffib
import xcffib.xproto
from PySide6.QtCore import QObject
from PySide6.QtGui import QCursor

from ..window import WindowInfo, open_xcb_connection, close_xcb_connection

logger = logging.getLogger(__name__)


class OpacityController(QObject):
    """
    Controls overlay opacity based on mouse position relative to a target window.

    The controller periodically checks whether the mouse cursor is inside the
    target window. If inside, overlay opacity is set to 1.0; if outside, the
    opacity is reduced to a configurable minimum value.

    The check is throttled to avoid excessive XCB queries (default 10 Hz).
    The controller uses its own XCB connection and automatically reconnects
    if it becomes invalid.

    Attributes:
        overlay: The QWidget (or QMainWindow) whose opacity is controlled.
        target_handle (int): X11 window ID of the target window.
        target_width (int): Current width of the target window (updated automatically).
        target_height (int): Current height of the target window.
        min_opacity (float): Opacity when mouse is outside (default 0.2).
        max_opacity (float): Opacity when mouse is inside (default 1.0).
    """

    def __init__(
        self,
        overlay: QObject,
        win_info: WindowInfo,
        min_opacity: float = 0.2,
        max_opacity: float = 1.0,
    ) -> None:
        """
        Initialize the opacity controller.

        Args:
            overlay: The Qt window whose opacity will be adjusted.
            win_info: Initial target window information.
            min_opacity: Opacity value when mouse is outside (0.0 - 1.0).
            max_opacity: Opacity value when mouse is inside (0.0 - 1.0).
        """
        super().__init__()
        self.overlay = overlay
        self.target_handle = win_info.handle
        self.target_width = win_info.width
        self.target_height = win_info.height
        self.min_opacity = min(max(min_opacity, 0.0), 1.0)
        self.max_opacity = min(max(max_opacity, 0.0), 1.0)

        # XCB connection and related objects
        self._conn: Optional[xcffib.Connection] = None
        self._root: Optional[int] = None

        # Throttling
        self._last_update_time: float = 0.0
        self._update_interval: float = 0.1  # seconds (10 Hz)

        self._open_connection()

    def _open_connection(self) -> None:
        """Open an XCB connection and cache the root window ID."""
        # Close any existing connection first
        self.close()

        self._conn = open_xcb_connection()
        if self._conn:
            self._root = self._conn.get_setup().roots[0].root
            logger.debug("OpacityController: XCB connection opened")
        else:
            logger.warning("OpacityController: failed to open XCB connection")

    def close(self) -> None:
        """Close the XCB connection and release resources."""
        close_xcb_connection(self._conn)
        self._conn = None
        self._root = None

    def update(self) -> None:
        """
        Update the overlay opacity based on current mouse position.

        This method is throttled to avoid excessive XCB queries. It checks
        whether the mouse cursor is inside the target window and sets the
        overlay opacity accordingly. If the target window no longer exists,
        the connection is closed and will be reopened on the next call.
        """
        # Throttle updates
        now = time.time()
        if now - self._last_update_time < self._update_interval:
            return
        self._last_update_time = now

        # If event forwarding is active, we don't dim (user is interacting with overlay)
        # This is set by the overlay when map_events is True.
        if hasattr(self.overlay, "map_events") and self.overlay.map_events:
            self.overlay.setWindowOpacity(self.max_opacity)
            return

        # Ensure we have a valid connection
        if self._conn is None:
            self._open_connection()
            if self._conn is None:
                # No connection - can't determine position, assume inside
                self.overlay.setWindowOpacity(self.max_opacity)
                return

        try:
            mouse = QCursor.pos()
            # Get target window geometry relative to root
            root_x, root_y, win_width, win_height = self._get_target_root_geometry()
            if root_x is None:
                # Window not found (may have been destroyed)
                self.overlay.setWindowOpacity(self.max_opacity)
                self.close()  # force reopen on next update
                return

            # Check if mouse is inside the target window
            inside = (
                root_x <= mouse.x() < root_x + win_width
                and root_y <= mouse.y() < root_y + win_height
            )
            opacity = self.max_opacity if inside else self.min_opacity
            self.overlay.setWindowOpacity(opacity)

        except (xcffib.ConnectionError, xcffib.xproto.BadWindow) as e:
            logger.debug(f"XCB error in opacity update: {e}, reopening connection")
            self.close()
            self._open_connection()
            # Fallback to full opacity
            self.overlay.setWindowOpacity(self.max_opacity)
        except Exception as e:
            logger.error(f"Unexpected error in opacity update: {e}", exc_info=True)
            self.overlay.setWindowOpacity(self.max_opacity)

    def _get_target_root_geometry(
        self,
    ) -> tuple[Optional[int], Optional[int], int, int]:
        """
        Get the target window's geometry (x, y, width, height) in root (screen) coordinates.

        Returns:
            A tuple (root_x, root_y, width, height). If the window cannot be queried,
            root_x and root_y are None, and width/height default to 0.
        """
        if self._conn is None or self._root is None:
            return None, None, 0, 0

        try:
            # Get window geometry (relative to parent)
            geom_cookie = self._conn.core.GetGeometry(self.target_handle)
            geom = geom_cookie.reply()
            if geom is None:
                return None, None, 0, 0

            # Translate coordinates from target window to root
            trans_cookie = self._conn.core.TranslateCoordinates(
                self.target_handle,
                self._root,
                0,  # src_x
                0,  # src_y
            )
            trans = trans_cookie.reply()
            if trans is None:
                return None, None, 0, 0

            return trans.dst_x, trans.dst_y, geom.width, geom.height

        except (xcffib.xproto.BadWindow, xcffib.xproto.BadDrawable):
            logger.debug(f"Target window {self.target_handle:#x} no longer exists")
            return None, None, 0, 0
        except Exception as e:
            logger.debug(f"Failed to get target window geometry: {e}")
            return None, None, 0, 0

    def update_target_info(self, handle: int, width: int, height: int) -> None:
        """
        Update the target window information.

        If the handle changes, the XCB connection is closed and reopened to
        ensure valid state.

        Args:
            handle: New X11 window ID.
            width: New target width.
            height: New target height.
        """
        if handle != self.target_handle:
            logger.debug(
                f"OpacityController: target changed from {self.target_handle:#x} to {handle:#x}"
            )
            self.target_handle = handle
            self.close()
            self._open_connection()
        self.target_width = width
        self.target_height = height
