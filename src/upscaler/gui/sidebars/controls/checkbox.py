from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QWidget

from ._base import BaseRow
from ...styles import checkbox_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class CheckBox(BaseRow):
    """
    A row with a QCheckBox and highlight support.

    The base indicator is placed to the left, followed by the checkbox.
    Because the checkbox already contains its own text, no separate label
    is used. Highlight state changes the checkbox text and border color
    instead of a label.
    """

    # Signal emitted when the checkbox state changes (int: 0 = unchecked, 2 = checked)
    stateChanged = Signal(int)

    def __init__(
        self,
        text: str,
        gui_config: GUIConfig,
        checked: bool = False,
        tooltip: Optional[str] = None,
        baseline: Optional[bool] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)

        # Checkbox
        self._checkbox = QCheckBox(text)
        self._checkbox.setChecked(checked)
        self._checkbox.setCursor(Qt.PointingHandCursor)
        if tooltip:
            self._checkbox.setToolTip(tooltip)

        self._checkbox.stateChanged.connect(self._on_state_changed)
        self._content_layout.addWidget(self._checkbox, 1)

        # Initial style and highlight
        self._apply_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def isChecked(self) -> bool:
        return self._checkbox.isChecked()

    def setChecked(self, checked: bool) -> None:
        self._checkbox.setChecked(checked)

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._checkbox.setEnabled(enabled)

    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return self._checkbox.isChecked() != self._baseline

    def _apply_highlight_style(self, highlighted: bool) -> None:
        """
        Reapply the checkbox stylesheet to reflect highlight state.
        """
        self._apply_style(highlighted)

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------
    def _on_state_changed(self, state: int) -> None:
        self._update_highlight()
        self.stateChanged.emit(state)

    def _apply_style(self, highlighted: bool = False) -> None:
        self._checkbox.setStyleSheet(
            checkbox_style(
                self._cfg, self.isEnabled(), highlighted or self._is_highlighted()
            )
        )
