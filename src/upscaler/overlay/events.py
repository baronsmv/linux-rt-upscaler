import logging
import struct
import xcffib
import xcffib.xproto
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from typing import Optional

from ..window import open_xcb_connection, close_xcb_connection

logger = logging.getLogger(__name__)

# Qt button to X11 button number mapping
BUTTON_MAP = {
    Qt.LeftButton: 1,
    Qt.MiddleButton: 2,
    Qt.RightButton: 3,
    Qt.XButton1: 8,
    Qt.XButton2: 9,
}


class X11EventForwarder:
    """
    Forwards mouse events to a target X11 window using XCB.

    The forwarder manages an XCB connection and sends ButtonPress,
    ButtonRelease, and MotionNotify events to a given window ID.
    """

    def __init__(self) -> None:
        self.conn: Optional[xcffib.Connection] = None
        self._root: Optional[int] = None
        self.target_handle: Optional[int] = None
        self.enabled: bool = True
        self._open_connection()

    def _open_connection(self) -> None:
        """Open the XCB connection."""
        self.conn = open_xcb_connection()
        if self.conn:
            self._root = self.conn.get_setup().roots[0].root
            logger.debug(
                f"Opened XCB connection for event forwarding. Root: {self._root}"
            )
        else:
            self.enabled = False
            logger.warning("XCB connection unavailable – event forwarding disabled")

    def close(self) -> None:
        close_xcb_connection(self.conn)
        self.conn = None
        self._root = None

    def _send_event(self, event_data: bytes, event_mask: int) -> None:
        """
        Send a generic X11 event to the target window.

        Args:
            event_data: Raw bytes of the event structure (32 bytes).
            event_mask: Mask for event propagation (e.g., ButtonPressMask).
        """
        if not self.enabled:
            logger.debug("Forwarding disabled, event not sent")
            return
        if self.conn is None or self.target_handle is None:
            logger.error("Cannot send event: no XCB connection or target handle")
            return

        try:
            # SendEvent(destination, propagate, event_mask, event)
            self.conn.core.SendEvent(
                False,  # propagate
                self.target_handle,  # destination
                event_mask,  # event_mask
                event_data,  # event (32 bytes)
            )
            self.conn.flush()
        except Exception as e:
            logger.error(f"Unexpected error sending X11 event: {e}", exc_info=True)

    def forward_motion(
        self,
        screen_x: int,
        screen_y: int,
        target_x: int,
        target_y: int,
        button_state: int,
    ) -> None:
        """
        Send a MotionNotify event to the target window.

        Args:
            screen_x, screen_y: Global screen coordinates (root coordinates).
            target_x, target_y: Coordinates within the target window.
            button_state: Bitmask of currently pressed buttons (XCB ButtonMask).
        """
        # MotionNotify event structure (32 bytes)
        # Format: response_type(1), detail(1), seq(2), time(4), root(4), event(4),
        #         child(4), root_x(2), root_y(2), event_x(2), event_y(2),
        #         state(2), same_screen(1), pad(1)
        event = struct.pack(
            "<BBHIIIIIHHHHBB",
            xcffib.xproto.MotionNotifyEvent._event_code,  # response_type
            0,  # detail (unused)
            0,  # seq (will be filled by server)
            xcffib.xproto.Time.CurrentTime,  # time
            self._root,  # root
            self.target_handle,  # event window
            0,  # child
            screen_x,
            screen_y,  # root coordinates (16-bit)
            target_x,
            target_y,  # event coordinates (16-bit)
            button_state,  # state
            1,  # same_screen
            0,  # pad
        )
        self._send_event(event, xcffib.xproto.EventMask.ButtonMotion)

    def forward_button(
        self,
        qt_button: Qt.MouseButton,
        press: bool,
        screen_x: int,
        screen_y: int,
        target_x: int,
        target_y: int,
    ) -> None:
        """
        Send a ButtonPress or ButtonRelease event.

        Args:
            qt_button: Qt button constant (Qt.LeftButton, etc.).
            press: True for press, False for release.
            screen_x, screen_y: Global screen coordinates.
            target_x, target_y: Coordinates within the target window.
        """
        x11_button = BUTTON_MAP.get(qt_button)
        if x11_button is None:
            logger.warning(f"Unmapped Qt button {qt_button}, ignoring")
            return

        event_code = (
            xcffib.xproto.ButtonPressEvent._event_code
            if press
            else xcffib.xproto.ButtonReleaseEvent._event_code
        )

        event = struct.pack(
            "<BBHIIIIIHHHHBB",
            event_code,
            x11_button,  # detail (button)
            0,  # seq
            xcffib.xproto.Time.CurrentTime,  # time
            self._root,  # root
            self.target_handle,  # event window
            0,  # child
            screen_x,
            screen_y,  # root coordinates (16-bit)
            target_x,
            target_y,  # event coordinates (16-bit)
            0,  # state (no modifiers for press/release)
            1,  # same_screen
            0,  # pad
        )
        mask = (
            xcffib.xproto.EventMask.ButtonPress
            if press
            else xcffib.xproto.EventMask.ButtonRelease
        )
        self._send_event(event, mask)

    def forward_wheel(
        self,
        delta: int,
        horizontal: bool,
        screen_x: int,
        screen_y: int,
        target_x: int,
        target_y: int,
    ) -> None:
        """
        Send wheel events (simulated as button presses/releases).

        Args:
            delta: Signed wheel movement (e.g., from angleDelta().y()).
            horizontal: True for horizontal scroll, False for vertical.
            screen_x, screen_y: Global screen coordinates.
            target_x, target_y: Coordinates within the target window.
        """
        if horizontal:
            button = 6 if delta > 0 else 7  # 6 = right, 7 = left
        else:
            button = 4 if delta > 0 else 5  # 4 = up, 5 = down

        steps = max(1, abs(delta) // 120)

        for _ in range(steps):
            # ButtonPress
            press_event = struct.pack(
                "<BBHIIIIIHHHHBB",
                xcffib.xproto.ButtonPressEvent._event_code,
                button,
                0,
                xcffib.xproto.Time.CurrentTime,
                self._root,
                self.target_handle,
                0,
                screen_x,
                screen_y,
                target_x,
                target_y,
                0,
                1,
                0,
            )
            self._send_event(press_event, xcffib.xproto.EventMask.ButtonPress)

            # ButtonRelease
            release_event = struct.pack(
                "<BBHIIIIIHHHHBB",
                xcffib.xproto.ButtonReleaseEvent._event_code,
                button,
                0,
                xcffib.xproto.Time.CurrentTime,
                self._root,
                self.target_handle,
                0,
                screen_x,
                screen_y,
                target_x,
                target_y,
                0,
                1,
                0,
            )
            self._send_event(release_event, xcffib.xproto.EventMask.ButtonRelease)

    def get_current_button_state(self) -> int:
        """Return an X11 button state mask based on currently pressed Qt buttons."""
        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= xcffib.xproto.ButtonMask.BUTTON_1
        if buttons & Qt.RightButton:
            state |= xcffib.xproto.ButtonMask.BUTTON_3
        if buttons & Qt.MiddleButton:
            state |= xcffib.xproto.ButtonMask.BUTTON_2
        # XCB lacks masks for extra buttons; ignore for simplicity
        return state
