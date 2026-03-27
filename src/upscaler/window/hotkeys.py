import logging
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QObject, Signal, QSocketNotifier
from Xlib import X, display
from Xlib.keysymdef import latin1, miscellany

from .display import open_x_display, close_x_display

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """
    Global hotkey manager. Emits Qt signals when configured hotkeys are pressed.
    """

    # Signals for each supported action
    toggle_scaling = Signal()
    next_profile = Signal()
    prev_profile = Signal()
    screenshot = Signal()
    cycle_geometry = Signal()

    # Mapping from action name to signal
    _action_to_signal = {
        "toggle_scaling": toggle_scaling,
        "next_profile": next_profile,
        "prev_profile": prev_profile,
        "screenshot": screenshot,
        "cycle_geometry": cycle_geometry,
    }

    # Modifier name to X11 mask
    _MODIFIER_MAP = {
        "Ctrl": X.ControlMask,
        "Control": X.ControlMask,
        "Alt": X.Mod1Mask,
        "Shift": X.ShiftMask,
        "Super": X.Mod4Mask,
        "Win": X.Mod4Mask,
    }

    def __init__(self, config_hotkeys: Dict[str, str]) -> None:
        """
        :param config_hotkeys: dictionary mapping action names to hotkey strings,
                               e.g., {'toggle_scaling': 'Ctrl+Alt+S'}
        """
        super().__init__()
        self._config_hotkeys = config_hotkeys
        self._display: Optional[display.Display] = None
        self._socket_notifier: Optional[QSocketNotifier] = None
        self._grabbed_keys: list = []  # store (keycode, modifier) for ungrab

    def start(self) -> None:
        """Open X display, grab hotkeys, and start listening."""
        self._display = open_x_display()
        if not self._display:
            logger.error("Cannot start hotkey manager: X display unavailable")
            return

        self._grab_keys()
        self._setup_event_listener()
        logger.info("Hotkey manager started")

    def stop(self) -> None:
        """Ungrab keys and clean up."""
        self._ungrab_keys()
        if self._socket_notifier:
            self._socket_notifier.setEnabled(False)
            self._socket_notifier = None
        close_x_display(self._display)
        self._display = None
        logger.info("Hotkey manager stopped")

    def _grab_keys(self) -> None:
        """Grab each configured hotkey."""
        root = self._display.screen().root
        for action, hotkey_str in self._config_hotkeys.items():
            try:
                mod_mask, keysym = self._parse_hotkey_string(hotkey_str)
            except ValueError as e:
                logger.warning(
                    f"Invalid hotkey '{hotkey_str}' for action '{action}': {e}"
                )
                continue

            # Convert keysym to keycode
            keycode = self._display.keysym_to_keycode(keysym)
            if keycode == 0:
                logger.warning(f"Unknown key '{keysym}' in hotkey '{hotkey_str}'")
                continue

            # Grab the key
            root.grab_key(keycode, mod_mask, True, X.GrabModeAsync, X.GrabModeAsync)
            self._grabbed_keys.append((keycode, mod_mask))
            logger.debug(
                f"Grabbed {action}: {hotkey_str} (keycode={keycode}, mod_mask={mod_mask})"
            )

    def _ungrab_keys(self) -> None:
        """Ungrab all grabbed keys."""
        root = self._display.screen().root
        for keycode, mod_mask in self._grabbed_keys:
            root.ungrab_key(keycode, mod_mask, True)
        self._grabbed_keys.clear()

    def _parse_hotkey_string(self, hotkey_str: str) -> Tuple[int, int]:
        """
        Parse a hotkey string like "Ctrl+Alt+S" into (modifier_mask, keysym).
        Returns a tuple (modifier_mask, keysym).
        Raises ValueError on parsing failure.
        """
        parts = hotkey_str.split("+")
        modifiers = 0
        keysym_part = None

        for part in parts:
            # Check if part is a modifier
            if part in self._MODIFIER_MAP:
                modifiers |= self._MODIFIER_MAP[part]
            else:
                # Assume it's the key name
                if keysym_part is not None:
                    raise ValueError(f"Multiple key names in hotkey: {hotkey_str}")
                keysym_part = part

        if keysym_part is None:
            raise ValueError("No key name specified")

        # Convert key name to keysym
        keysym = self._name_to_keysym(keysym_part)
        if keysym == 0:
            raise ValueError(f"Unknown key name: {keysym_part}")

        return modifiers, keysym

    def _name_to_keysym(self, name: str) -> int:
        """
        Convert a key name like 'S', 'Right', 'P' to an X11 keysym.
        Uses Xlib's keysym lookup functions.
        """
        # Common keys
        common = {
            "S": latin1.XK_S,
            "P": latin1.XK_P,
            "O": latin1.XK_O,
            "Left": miscellany.XK_Left,
            "Right": miscellany.XK_Right,
            "Up": miscellany.XK_Up,
            "Down": miscellany.XK_Down,
            "F1": miscellany.XK_F1,
            "F2": miscellany.XK_F2,
            "F3": miscellany.XK_F3,
            "F4": miscellany.XK_F4,
            "F5": miscellany.XK_F5,
            "F6": miscellany.XK_F6,
            "F7": miscellany.XK_F7,
            "F8": miscellany.XK_F8,
            "F9": miscellany.XK_F9,
            "F10": miscellany.XK_F10,
            "F11": miscellany.XK_F11,
            "F12": miscellany.XK_F12,
            "Space": latin1.XK_space,
            "Shift": miscellany.XK_Shift_L,
            "Return": miscellany.XK_Return,
            "Tab": miscellany.XK_Tab,
            "Escape": miscellany.XK_Escape,
        }
        if name in common:
            return common[name]

        logger.warning(
            f"Unsupported key name: {name}. Use a key from the list: letters, arrows, F1-F12, Space, Return, Tab, Escape"
        )
        return 0

    def _setup_event_listener(self) -> None:
        """Set up a QSocketNotifier to watch the X connection file descriptor."""
        fd = self._display.display.fileno()
        self._socket_notifier = QSocketNotifier(fd, QSocketNotifier.Type.Read, self)
        self._socket_notifier.activated.connect(self._process_x_events)

    def _process_x_events(self) -> None:
        """Called when X events are available. Read all pending events."""
        while True:
            try:
                event = self._display.next_event()
                self._handle_event(event)
            except Exception:
                break

    def _handle_event(self, event) -> None:
        """Dispatch key press events to the appropriate signal."""
        if event.type != X.KeyPress:
            return

        keycode = event.detail
        state = event.state

        # Check if the key is one we grabbed
        for action, hotkey_str in self._config_hotkeys.items():
            try:
                mod_mask, keysym = self._parse_hotkey_string(hotkey_str)
            except ValueError:
                continue

            # Check if the keycode matches and the modifier state includes the required modifiers
            if (
                self._display.keycode_to_keysym(keycode, 0) == keysym
                and (state & mod_mask) == mod_mask
            ):
                # Emit the signal
                signal = self._action_to_signal.get(action)
                if signal:
                    signal.emit()
                    logger.debug(f"Hotkey {action} triggered")
                return
