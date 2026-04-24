"""
X11 event forwarding using pure XCB (xcffib).

This module provides an X11EventForwarder class that sends synthetic
X11 mouse events (motion, button press/release, wheel) to a target window.
It is designed to be used from the Qt main thread and opens its own
dedicated XCB connection, ensuring thread safety.

The event structures are manually packed according to the X11 protocol
specification (32-byte wire format) and sent via xcb_send_event.
"""

import logging
import struct
from typing import Optional

import xcffib
import xcffib.xproto
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ..window import open_xcb_connection, close_xcb_connection

logger = logging.getLogger(__name__)

# Mapping from Qt mouse buttons to X11 button numbers.
# See /usr/include/X11/X.h for X11 button definitions.
BUTTON_MAP = {
    Qt.LeftButton: 1,
    Qt.MiddleButton: 2,
    Qt.RightButton: 3,
    Qt.XButton1: 8,  # Back
    Qt.XButton2: 9,  # Forward
}


class X11EventForwarder:
    """
    Forwards mouse events to a target X11 window using synthetic X11 events.

    The forwarder opens a dedicated XCB connection and sends ButtonPress,
    ButtonRelease, and MotionNotify events to the specified window ID.
    Event forwarding can be enabled/disabled via the `enabled` attribute.

    All X11 event structures are packed manually as 32-byte arrays according
    to the core X11 protocol. This avoids dependency on higher-level libraries.

    Attributes:
        conn (xcffib.Connection): XCB connection used for event sending.
        target_handle (int | None): X11 window ID to forward events to.
        enabled (bool): If False, events are silently dropped.
    """

    def __init__(self) -> None:
        """Create an X11EventForwarder and open an XCB connection."""
        self.conn: Optional[xcffib.Connection] = None
        self._root: Optional[int] = None
        self.target_handle: Optional[int] = None
        self.enabled: bool = True
        self._open_connection()

    def _open_connection(self) -> None:
        """
        Open a dedicated XCB connection and retrieve the root window ID.

        If the connection fails, `enabled` is set to False and a warning is logged.
        """
        self.conn = open_xcb_connection()
        if self.conn:
            self._root = self.conn.get_setup().roots[0].root
            logger.debug(
                f"Opened XCB connection for event forwarding. Root: {self._root}"
            )
        else:
            self.enabled = False
            logger.warning("XCB connection unavailable - event forwarding disabled")

    def close(self) -> None:
        """Close the XCB connection and release resources."""
        close_xcb_connection(self.conn)
        self.conn = None
        self._root = None

    def _send_event(self, event_data: bytes, event_mask: int) -> None:
        """
        Send a generic 32-byte X11 event to the target window.

        Args:
            event_data: 32-byte packed representation of the event struct.
            event_mask: X11 event mask (e.g., ButtonPressMask) for propagation.
        """
        if not self.enabled:
            logger.debug("Forwarding disabled, event not sent")
            return
        if self.conn is None or self.target_handle is None:
            logger.error("Cannot send event: no XCB connection or target handle")
            return

        try:
            # SendEvent(propagate=False, destination, event_mask, event_data)
            self.conn.core.SendEvent(
                False,  # propagate
                self.target_handle,  # destination
                event_mask,  # event_mask
                event_data,  # 32-byte event payload
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

        The MotionNotify event structure (32 bytes):
            - response_type: 6 (MotionNotify opcode)
            - detail: 0 (unused)
            - seq: 0 (filled by server)
            - time: CurrentTime
            - root: root window ID
            - event: target window ID
            - child: 0 (none)
            - root_x, root_y: 16-bit screen coordinates
            - event_x, event_y: 16-bit window-relative coordinates
            - state: button/modifier mask
            - same_screen: 1 (True)
            - pad: 0

        Args:
            screen_x, screen_y: Global screen coordinates (root coordinates).
            target_x, target_y: Coordinates within the target window.
            button_state: Bitmask of currently pressed buttons (XCB ButtonMask).
        """
        # MotionNotify opcode = 6
        motion = xcffib.xproto.MotionNotifyEvent.synthetic(
            detail=0,
            time=xcffib.xproto.Time.CurrentTime,
            root=self._root,
            event=self.target_handle,
            child=0,
            root_x=screen_x,
            root_y=screen_y,
            event_x=target_x,
            event_y=target_y,
            state=button_state,
            same_screen=True,
        )
        mask = (
            xcffib.xproto.EventMask.ButtonPress
            | xcffib.xproto.EventMask.ButtonRelease
            | xcffib.xproto.EventMask.PointerMotion
        )
        self._send_event(motion.pack(), mask)

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

        The ButtonPress/ButtonRelease event structure (32 bytes) is identical
        except for the opcode (4 for press, 5 for release) and the event mask.

        Args:
            qt_button: Qt button constant (e.g., Qt.LeftButton).
            press: True for press, False for release.
            screen_x, screen_y: Global screen coordinates.
            target_x, target_y: Coordinates within the target window.
        """
        x11_button = BUTTON_MAP.get(qt_button)
        if x11_button is None:
            logger.warning(f"Unmapped Qt button {qt_button}, ignoring")
            return

        # Get the current button state (already pressed buttons) *before* this event.
        # This is important for proper drag and drop behaviour.
        state = self.get_current_button_state()

        # Use the synthetic classmethod to build the event structure.
        if press:
            btn_event = xcffib.xproto.ButtonPressEvent.synthetic(
                detail=x11_button,
                time=xcffib.xproto.Time.CurrentTime,
                root=self._root,
                event=self.target_handle,
                child=0,
                root_x=screen_x,
                root_y=screen_y,
                event_x=target_x,
                event_y=target_y,
                state=state,
                same_screen=True,
            )
            mask = xcffib.xproto.EventMask.ButtonPress
        else:
            btn_event = xcffib.xproto.ButtonReleaseEvent.synthetic(
                detail=x11_button,
                time=xcffib.xproto.Time.CurrentTime,
                root=self._root,
                event=self.target_handle,
                child=0,
                root_x=screen_x,
                root_y=screen_y,
                event_x=target_x,
                event_y=target_y,
                state=state,
                same_screen=True,
            )
            mask = xcffib.xproto.EventMask.ButtonRelease

        # The synthetic event object has a .pack() method that returns the 32-byte wire format.
        self._send_event(btn_event.pack(), mask)

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

        X11 traditionally uses buttons 4 (up), 5 (down), 6 (left), 7 (right)
        for wheel scrolling. Each "click" of the wheel is sent as a press
        immediately followed by a release.

        Args:
            delta: Signed wheel movement (positive = up/right, negative = down/left).
            horizontal: True for horizontal scroll, False for vertical.
            screen_x, screen_y: Global screen coordinates.
            target_x, target_y: Coordinates within the target window.
        """
        if horizontal:
            button = 6 if delta > 0 else 7  # 6 = right, 7 = left
        else:
            button = 4 if delta > 0 else 5  # 4 = up, 5 = down

        steps = max(1, abs(delta) // 120)  # Qt uses 120 units per wheel click

        for _ in range(steps):
            # ButtonPress (opcode 4)
            press_event = struct.pack(
                "<BBHIIIIIHHHHBB",
                4,  # ButtonPress
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

            # ButtonRelease (opcode 5)
            release_event = struct.pack(
                "<BBHIIIIIHHHHBB",
                5,  # ButtonRelease
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
        """
        Return an X11 button state mask based on currently pressed Qt buttons.

        The mask is a bitwise OR of values like Button1Mask, Button2Mask, etc.
        This is used to populate the `state` field of MotionNotify events.

        Returns:
            int: X11 button mask (see xcffib.xproto.ButtonMask).
        """
        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= 256  # Button1Mask
        if buttons & Qt.MiddleButton:
            state |= 512  # Button2Mask
        if buttons & Qt.RightButton:
            state |= 1024  # Button3Mask
        return state
