from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from ._base import BaseRow
from ...styles import hotkey_button_style
from ....utils import KEYSYM_MAP, format_hotkey

if TYPE_CHECKING:
    from ...config import GUIConfig


class HotkeyCaptureButton(QPushButton):
    """
    Push button that captures a keyboard shortcut on click.

    Recording rules
    ---------------
    - Clicking enters recording mode and installs an application-level event
      filter, so global Qt shortcuts (``Ctrl+F``, ``Ctrl+Q``, ...) do not
      steal the keypress.
    - Modifier-only presses are previewed but do not commit.
    - A binding must contain at least one modifier; bare keys are rejected
      because XCB would grab them system-wide.
    - ``Escape`` cancels, ``Backspace``/``Delete`` clear the binding.
    - Losing focus cancels silently (the previous value is kept).

    Signals
    -------
    sequenceChanged(str)
        Emitted with the new canonical sequence whenever a commit occurs.
    """

    sequenceChanged = Signal(str)

    #: Modifier keys and the modifier name they represent.
    _MODIFIER_KEYS: Dict[int, str] = {
        Qt.Key_Shift: "Shift",
        Qt.Key_Control: "Ctrl",
        Qt.Key_Alt: "Alt",
        Qt.Key_Meta: "Super",
        Qt.Key_AltGr: "Alt",
    }

    #: Qt key code -> name used in :data:`KEYSYM_MAP`.
    _QT_KEY_TO_NAME: Dict[int, str] = {
        Qt.Key_Left: "Left",
        Qt.Key_Right: "Right",
        Qt.Key_Up: "Up",
        Qt.Key_Down: "Down",
        Qt.Key_Return: "Return",
        Qt.Key_Enter: "Return",
        Qt.Key_Tab: "Tab",
        Qt.Key_Escape: "Escape",
        Qt.Key_Space: "Space",
        Qt.Key_BracketLeft: "LeftBracket",
        Qt.Key_BracketRight: "RightBracket",
        Qt.Key_Backslash: "Backslash",
        Qt.Key_Semicolon: "Semicolon",
        Qt.Key_Apostrophe: "Apostrophe",
        Qt.Key_Comma: "Comma",
        Qt.Key_Period: "Period",
        Qt.Key_Slash: "Slash",
        Qt.Key_Plus: "Plus",
        Qt.Key_Minus: "Minus",
        Qt.Key_Equal: "Equal",
        Qt.Key_QuoteLeft: "Grave",
        **{getattr(Qt, f"Key_F{i}"): f"F{i}" for i in range(1, 13)},
        **{getattr(Qt, f"Key_{c}"): c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
        **{getattr(Qt, f"Key_{d}"): d for d in "0123456789"},
    }

    def __init__(
        self,
        cfg: GUIConfig,
        sequence: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._sequence = sequence
        self._recording = False

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(cfg.sidebar.row_height)
        self.setStyleSheet(hotkey_button_style(cfg))
        self._refresh_text()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def sequence(self) -> str:
        return self._sequence

    def set_sequence(self, sequence: str) -> None:
        """Programmatically set the displayed sequence (no signal emitted)."""
        if sequence == self._sequence:
            return
        self._sequence = sequence
        self._refresh_text()

    # ------------------------------------------------------------------
    #  Recording lifecycle
    # ------------------------------------------------------------------
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self._recording:
            self._start_recording()
            event.accept()
            return
        super().mousePressEvent(event)

    def focusOutEvent(self, event) -> None:
        if self._recording:
            self._cancel_recording()
        super().focusOutEvent(event)

    def _start_recording(self) -> None:
        self._recording = True
        self.setText(self.tr("Press keys…", "Hotkey recording prompt"))
        QApplication.instance().installEventFilter(self)

    def _stop_recording(self) -> None:
        self._recording = False
        QApplication.instance().removeEventFilter(self)
        self._refresh_text()

    def _cancel_recording(self) -> None:
        self._stop_recording()

    # ------------------------------------------------------------------
    #  Key handling
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event) -> bool:  # noqa: N802 (Qt naming)
        if not self._recording or event.type() != QEvent.KeyPress:
            return False
        self._handle_recording_key(event)
        return True  # swallow every keypress while recording

    def _handle_recording_key(self, event) -> None:
        key = event.key()

        if key == Qt.Key_Escape:
            self._cancel_recording()
            return

        if key in (Qt.Key_Backspace, Qt.Key_Delete):
            self._commit("")
            return

        if key in self._MODIFIER_KEYS:
            # Preview the current modifier set, wait for a real key.
            mods = self._modifier_names(event.modifiers() | self._modifier_bit(key))
            preview = "+".join(list(mods) + ["…"]) if mods else "…"
            self.setText(preview)
            return

        name = self._QT_KEY_TO_NAME.get(key)
        if name is None or name not in KEYSYM_MAP:
            return

        mods = self._modifier_names(event.modifiers())
        if not mods:
            self.setText(self.tr("Needs a modifier", "Hotkey recording error"))
            return

        self._commit(format_hotkey(mods, name))

    def _commit(self, sequence: str) -> None:
        self._stop_recording()
        if sequence == self._sequence:
            return
        self._sequence = sequence
        self._refresh_text()
        self.sequenceChanged.emit(sequence)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _modifier_bit(key: int) -> int:
        """Qt modifier flag corresponding to a bare modifier key press."""
        return {
            Qt.Key_Shift: Qt.ShiftModifier,
            Qt.Key_Control: Qt.ControlModifier,
            Qt.Key_Alt: Qt.AltModifier,
            Qt.Key_Meta: Qt.MetaModifier,
        }.get(key, 0)

    @staticmethod
    def _modifier_names(flags) -> tuple[str, ...]:
        names = []
        if flags & Qt.ControlModifier:
            names.append("Ctrl")
        if flags & Qt.AltModifier:
            names.append("Alt")
        if flags & Qt.ShiftModifier:
            names.append("Shift")
        if flags & Qt.MetaModifier:
            names.append("Super")
        return tuple(names)

    def _refresh_text(self) -> None:
        self.setText(
            self._sequence or self.tr("(unbound)", "Displayed when no hotkey is bound")
        )


class HotkeyRow(BaseRow):
    """
    One labeled row inside the Extras tab that binds a single action.

    Forwards the button's :attr:`sequenceChanged` signal and uses the
    standard :class:`BaseRow` highlight logic: the row is highlighted when
    the current sequence differs from the baseline.
    """

    sequenceChanged = Signal(str)

    def __init__(
        self,
        cfg: GUIConfig,
        label: str,
        sequence: str,
        baseline: Optional[str] = None,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            cfg,
            baseline=(sequence if baseline is None else baseline),
            parent=parent,
        )
        self._init_label(label)

        self._button = HotkeyCaptureButton(cfg, sequence=sequence)
        if tooltip:
            self._button.setToolTip(tooltip)
        self._button.sequenceChanged.connect(self._on_sequence_changed)
        self._content_layout.addWidget(self._button, 1)

        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def sequence(self) -> str:
        return self._button.sequence()

    def set_sequence(self, sequence: str) -> None:
        """Set the value without emitting (used by reset / restore flows)."""
        self._button.set_sequence(sequence)
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow hooks
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        return self._button.sequence() != (self._baseline or "")

    def _on_sequence_changed(self, sequence: str) -> None:
        self._update_highlight()
        self.sequenceChanged.emit(sequence)
