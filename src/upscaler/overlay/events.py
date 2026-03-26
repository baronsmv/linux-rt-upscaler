import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from Xlib import X, display
from Xlib.protocol import event as xevent

from ..window import open_x_display, close_x_display

logger = logging.getLogger(__name__)

# Mapping from Qt button to X11 button number (1–3, 4–5 for scroll, 8–9 for extra)
BUTTON_MAP = {
    Qt.LeftButton: 1,
    Qt.MiddleButton: 2,
    Qt.RightButton: 3,
    Qt.XButton1: 8,
    Qt.XButton2: 9,
}


class X11EventForwarder:
    """
    Forwards mouse events to a target X11 window.

    The forwarder manages an X11 display connection, sends ButtonPress,
    ButtonRelease, and MotionNotify events to a given window ID.

    Attributes:
        target_handle: X11 window ID of the target window (int).
        enabled: Whether forwarding is currently allowed (used for minimization).
    """

    def __init__(self) -> None:
        """Create an X11EventForwarder with no display connection (lazy open)."""
        self.display: Optional[display.Display] = None
        self._root: Optional[int] = None
        self.target_handle: Optional[int] = None
        self.enabled: bool = True

        self._open_display()

    def _open_display(self) -> None:
        """Open the X11 display and install a custom error handler."""
        self.display = open_x_display()
        if self.display:
            self._root = int(self.display.screen().root.id)
            logger.debug(f"Opened X display for event forwarding. Root: {self._root}")
        else:
            self.enabled = False
            logger.warning("X11 display unavailable – event forwarding disabled")

    def close(self) -> None:
        close_x_display(self.display)
        self.display = None
        self._root = None

    def _send_event(self, event: xevent.KeyButtonPointer) -> None:
        """
        Send an X11 event to the target window.

        The custom error handler will log errors without printing to stderr.
        """
        if not self.enabled:
            logger.debug("Forwarding disabled, event not sent")
            return
        if self.display is None or self.target_handle is None:
            logger.error("Cannot send event: no X display or target handle")
            return

        try:
            self.display.send_event(
                self.target_handle,
                event,
                event_mask=X.ButtonPressMask
                | X.ButtonReleaseMask
                | X.PointerMotionMask,
            )
            self.display.flush()
            logger.debug(f"Sent event: {event}")
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
            button_state: Bitmask of currently pressed buttons (X.Button*Mask).
        """
        ev = xevent.MotionNotify(
            window=self.target_handle,
            root=self._root,
            same_screen=1,
            root_x=screen_x,
            root_y=screen_y,
            time=X.CurrentTime,
            detail=0,  # not used for motion
            state=button_state,
            event_x=target_x,
            event_y=target_y,
            child=0,
        )
        self._send_event(ev)

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

        if press:
            ev = xevent.ButtonPress(
                window=self.target_handle,
                root=self._root,
                same_screen=1,
                root_x=screen_x,
                root_y=screen_y,
                time=X.CurrentTime,
                detail=x11_button,
                state=0,  # no modifiers for press (state is for events with buttons already down)
                event_x=target_x,
                event_y=target_y,
                child=0,
            )
        else:
            ev = xevent.ButtonRelease(
                window=self.target_handle,
                root=self._root,
                same_screen=1,
                root_x=screen_x,
                root_y=screen_y,
                time=X.CurrentTime,
                detail=x11_button,
                state=0,
                event_x=target_x,
                event_y=target_y,
                child=0,
            )
        self._send_event(ev)

    def forward_wheel(
        self,
        delta: int,  # positive = up/right, negative = down/left
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
        # Determine button number based on direction
        if horizontal:
            button = 6 if delta > 0 else 7  # 6 = right, 7 = left (X11 convention)
        else:
            button = 4 if delta > 0 else 5  # 4 = up, 5 = down

        # Calculate number of steps (usually delta is multiple of 120)
        steps = abs(delta) // 120
        if steps == 0:
            steps = 1

        for _ in range(steps):
            # Send press and release for each step
            press_ev = xevent.ButtonPress(
                window=self.target_handle,
                root=self._root,
                same_screen=1,
                root_x=screen_x,
                root_y=screen_y,
                time=X.CurrentTime,
                detail=button,
                state=0,
                event_x=target_x,
                event_y=target_y,
                child=0,
            )
            self._send_event(press_ev)

            release_ev = xevent.ButtonRelease(
                window=self.target_handle,
                root=self._root,
                same_screen=1,
                root_x=screen_x,
                root_y=screen_y,
                time=X.CurrentTime,
                detail=button,
                state=0,
                event_x=target_x,
                event_y=target_y,
                child=0,
            )
            self._send_event(release_ev)

    def get_current_button_state(self) -> int:
        """
        Return an X11 button state mask based on currently pressed Qt buttons.

        This method uses QApplication.mouseButtons() to get the current state.
        """

        state = 0
        buttons = QApplication.mouseButtons()
        if buttons & Qt.LeftButton:
            state |= X.Button1Mask
        if buttons & Qt.RightButton:
            state |= X.Button3Mask
        if buttons & Qt.MiddleButton:
            state |= X.Button2Mask
        # Additional buttons (XButton1, XButton2) are not part of the standard masks
        return state
