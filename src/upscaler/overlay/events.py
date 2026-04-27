import logging
from typing import Optional

import xcffib
import xcffib.xproto
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ..window import close_xcb_connection, open_xcb_connection

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

# X11 event masks (standard values)
X11_BUTTON1_MASK = 256
X11_BUTTON2_MASK = 512
X11_BUTTON3_MASK = 1024
X11_SHIFT_MASK = 1
X11_CONTROL_MASK = 4
X11_MOD1_MASK = 8  # Alt
X11_MOD4_MASK = 64  # Super


class X11EventForwarder:
    """
    Forwards mouse events to a target X11 window using synthetic X11 events.

    The forwarder opens a dedicated XCB connection and sends ButtonPress,
    ButtonRelease, MotionNotify, and wheel events (as paired button press/release)
    to the specified window ID. Event forwarding can be enabled/disabled via the
    `enabled` attribute.

    All event structures are built using xcffib.xproto synthetic event classes,
    which guarantee proper wire format.

    Attributes:
        conn (xcffib.Connection | None): XCB connection used for event sending.
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
                self.target_handle,  # destination window
                event_mask,  # event_mask
                event_data,  # 32-byte event payload
            )
            self.conn.flush()
        except Exception as e:
            logger.error(f"Unexpected error sending X11 event: {e}", exc_info=True)

    def _get_current_state(self) -> int:
        """
        Return the current X11 button + modifier mask.

        Combines currently pressed mouse buttons (from QApplication) and
        keyboard modifiers (Shift, Ctrl, Alt, Meta) into an X11 state mask.
        Uses standard X11 numeric constants for reliability across xcffib versions.

        Returns:
            int: X11 state mask (bitwise OR of ButtonMask and ModMask values).
        """
        state = 0

        # Mouse button masks (X11 Button1Mask = 256, Button2Mask = 512, Button3Mask = 1024)
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= X11_BUTTON1_MASK  # Button1Mask
        if buttons & Qt.MiddleButton:
            state |= X11_BUTTON2_MASK  # Button2Mask
        if buttons & Qt.RightButton:
            state |= X11_BUTTON3_MASK  # Button3Mask

        # Keyboard modifier masks
        mods = QApplication.keyboardModifiers()
        if mods & Qt.ShiftModifier:
            state |= X11_SHIFT_MASK  # ShiftMask
        if mods & Qt.ControlModifier:
            state |= X11_CONTROL_MASK  # ControlMask
        if mods & Qt.AltModifier:
            state |= X11_MOD1_MASK  # Mod1Mask (Alt)
        if mods & Qt.MetaModifier:
            state |= X11_MOD4_MASK  # Mod4Mask (Super/Win)

        return state

    def forward_motion(
        self,
        screen_x: int,
        screen_y: int,
        target_x: int,
        target_y: int,
    ) -> None:
        """
        Send a MotionNotify event to the target window.

        The event includes the current button and modifier state, ensuring
        that the target window sees the correct cursor shape and any active
        drag operations.

        Args:
            screen_x, screen_y: Global screen coordinates (root coordinates).
            target_x, target_y: Coordinates within the target window.
        """
        state = self._get_current_state()

        motion_event = xcffib.xproto.MotionNotifyEvent.synthetic(
            detail=0,  # not used for motion
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
        mask = (
            xcffib.xproto.EventMask.ButtonPress
            | xcffib.xproto.EventMask.ButtonRelease
            | xcffib.xproto.EventMask.PointerMotion
        )
        self._send_event(motion_event.pack(), mask)

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
            qt_button: Qt button constant (e.g., Qt.LeftButton).
            press: True for press, False for release.
            screen_x, screen_y: Global screen coordinates.
            target_x, target_y: Coordinates within the target window.
        """
        x11_button = BUTTON_MAP.get(qt_button)
        if x11_button is None:
            logger.warning(f"Unmapped Qt button {qt_button}, ignoring")
            return

        # Get the current state (buttons + modifiers) before this event.
        # This is important for proper drag and drop behavior, as the state
        # field in a press event typically does not yet include the button being pressed.
        state = self._get_current_state()

        if press:
            event = xcffib.xproto.ButtonPressEvent.synthetic(
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
            event = xcffib.xproto.ButtonReleaseEvent.synthetic(
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

        self._send_event(event.pack(), mask)

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

        X11 traditionally uses buttons 4 (up), 5 (down), 6 (right), 7 (left)
        for wheel scrolling. Each "click" of the wheel is sent as a press
        immediately followed by a release. Multiple steps are emitted when
        `abs(delta) >= 120` (Qt uses 120 units per wheel click).

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

        steps = max(1, abs(delta) // 120)
        # Use the current button+modifier state for each step.
        # Note: some applications ignore the state field in wheel events.
        state = self._get_current_state()

        for _ in range(steps):
            # ButtonPress
            press_event = xcffib.xproto.ButtonPressEvent.synthetic(
                detail=button,
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
            self._send_event(press_event.pack(), xcffib.xproto.EventMask.ButtonPress)

            # ButtonRelease
            release_event = xcffib.xproto.ButtonReleaseEvent.synthetic(
                detail=button,
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
            self._send_event(
                release_event.pack(), xcffib.xproto.EventMask.ButtonRelease
            )
