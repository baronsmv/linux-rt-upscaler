import itertools
import logging
from typing import Dict, Optional, Tuple

import xcffib
from PySide6.QtCore import QObject, QSocketNotifier, Signal
from xcffib.xproto import GrabMode, KeyPressEvent, ModMask, Setup

from ..utils import KEYSYM_MAP, parse_hotkey

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """
    Global hotkey manager using a separate XCB connection + QSocketNotifier.
    """

    # Signals
    toggle_scaling = Signal()
    exit_app = Signal()

    screenshot = Signal()

    cycle_model = Signal()
    cycle_geometry = Signal()

    restore_view = Signal()

    zoom_in = Signal()
    zoom_out = Signal()

    offset_left = Signal()
    offset_right = Signal()
    offset_up = Signal()
    offset_down = Signal()

    # Lock masks (NumLock, CapsLock, ScrollLock)
    _LOCK_MASKS = [0, ModMask._2, ModMask.Lock, ModMask._5]

    def __init__(self, config_hotkeys: Dict[str, str]) -> None:
        super().__init__()
        self._config_hotkeys = config_hotkeys
        self._grabbed: Dict[Tuple[int, int], str] = {}
        self._conn: Optional[xcffib.Connection] = None
        self._root: Optional[int] = None
        self._setup: Optional[Setup] = None
        self._keycode_cache: Dict[str, int] = {}
        self._socket_notifier: Optional[QSocketNotifier] = None

        # Compute lock mask combinations
        self._lock_combinations = list(
            {
                sum(comb)
                for r in range(len(self._LOCK_MASKS) + 1)
                for comb in itertools.combinations(self._LOCK_MASKS, r)
            }
        )

    def start(self) -> None:
        """Open XCB connection, grab keys, and start listening."""
        try:
            self._conn = xcffib.connect()
        except Exception as e:
            logger.error(f"Failed to open XCB connection: {e}")
            return

        self._setup = self._conn.get_setup()
        self._root = self._setup.roots[0].root

        self._grab_keys()
        self._setup_event_listener()
        logger.debug("XCB hotkey manager started (standalone connection)")

    def stop(self) -> None:
        """Ungrab keys and close connection."""
        if self._conn is None:
            return

        if self._socket_notifier:
            self._socket_notifier.setEnabled(False)
            self._socket_notifier = None

        self._ungrab_keys()
        self._conn.disconnect()
        self._conn = None
        logger.debug("XCB hotkey manager stopped")

    def _grab_keys(self) -> None:
        for action, hotkey_str in self._config_hotkeys.items():
            # Verify the action corresponds to a defined signal
            if not hasattr(self, action):
                logger.warning("Unknown action '%s'", action)
                continue

            # Empty string means explicitly disabled
            if not hotkey_str:
                continue

            try:
                mod_mask, key_name = parse_hotkey(hotkey_str)
            except ValueError as e:
                logger.warning("Invalid hotkey '%s': %s", hotkey_str, e)
                continue

            keycode = self._key_name_to_keycode(key_name)
            if keycode is None:
                logger.warning("Unknown key '%s' in '%s'", key_name, hotkey_str)
                continue

            for lock_mask in self._lock_combinations:
                self._conn.core.GrabKey(
                    owner_events=True,
                    grab_window=self._root,
                    modifiers=mod_mask | lock_mask,
                    key=keycode,
                    pointer_mode=GrabMode.Async,
                    keyboard_mode=GrabMode.Async,
                )

            self._grabbed[(mod_mask, keycode)] = action
            logger.debug(
                f"Grabbed '{action}': '{hotkey_str}' (mod={mod_mask}, keycode={keycode})"
            )

        self._conn.flush()

    def _ungrab_keys(self) -> None:
        """Ungrab all registered key combinations."""
        if self._conn is None:
            return

        for (mod_mask, keycode), _ in self._grabbed.items():
            for lock_mask in self._lock_combinations:
                self._conn.core.UngrabKey(keycode, self._root, mod_mask | lock_mask)
        self._conn.flush()
        self._grabbed.clear()

    def _key_name_to_keycode(self, name: str) -> Optional[int]:
        """Convert a key name to an X11 keycode using the current keyboard mapping."""
        if name in self._keycode_cache:
            return self._keycode_cache[name]

        keysym = KEYSYM_MAP.get(name)
        if keysym is None:
            logger.warning(f"Unsupported key name: {name}")
            return None

        min_kc = self._setup.min_keycode
        max_kc = self._setup.max_keycode
        count = max_kc - min_kc + 1

        reply = self._conn.core.GetKeyboardMapping(min_kc, count).reply()
        if not reply:
            return None

        keysyms_per_keycode = reply.keysyms_per_keycode
        for i in range(count):
            base = i * keysyms_per_keycode
            for offset in range(keysyms_per_keycode):
                if reply.keysyms[base + offset] == keysym:
                    kc = min_kc + i
                    self._keycode_cache[name] = kc
                    return kc
        return None

    def _setup_event_listener(self) -> None:
        """Watch the XCB connection file descriptor using QSocketNotifier."""
        fd = self._conn.get_file_descriptor()
        self._socket_notifier = QSocketNotifier(fd, QSocketNotifier.Type.Read, self)
        self._socket_notifier.activated.connect(self._process_x_events)

    def _process_x_events(self) -> None:
        """Read all pending events from the XCB connection."""
        while self._conn is not None:
            try:
                event = self._conn.poll_for_event()
            except Exception as e:
                logger.error(f"Error polling for XCB event: {e}")
                break
            if not event:
                break
            self._handle_event(event)

    def _handle_event(self, event) -> None:
        """Dispatch KeyPress events to the appropriate signal."""
        if not isinstance(event, KeyPressEvent):
            return

        keycode = event.detail
        state = event.state
        for lock in self._LOCK_MASKS:
            state &= ~lock

        for (mod_mask, grabbed_keycode), action in self._grabbed.items():
            if grabbed_keycode == keycode and (state & mod_mask) == mod_mask:
                # Retrieve the bound signal by name and emit
                signal = getattr(self, action, None)
                if signal is not None:
                    signal.emit()
                    logger.debug(f"Hotkey '{action}' triggered")
                break
