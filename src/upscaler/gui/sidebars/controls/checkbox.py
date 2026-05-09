from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QWidget

from ._base import BaseRow

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
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Indicator
        layout.addWidget(self._init_indicator())

        # Checkbox
        self._checkbox = QCheckBox(text)
        self._checkbox.setChecked(checked)
        self._checkbox.setCursor(Qt.PointingHandCursor)
        if tooltip:
            self._checkbox.setToolTip(tooltip)

        self._checkbox.stateChanged.connect(self._on_state_changed)
        layout.addWidget(self._checkbox, 1)

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

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._checkbox.setEnabled(enabled)
        self._apply_style()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
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

    def _apply_style(self, highlighted: Optional[bool] = None) -> None:
        if highlighted is None:
            highlighted = self._is_highlighted()

        cfg = self._cfg
        enabled = self.isEnabled()

        text_color = (
            cfg.highlight_label_color if highlighted else cfg.sidebar_tab_text_color
        )
        if not enabled:
            text_color = cfg.checkbox_disabled_color

        indicator_color = (
            cfg.highlight_border_color
            if highlighted
            else (
                cfg.sidebar_checkbox_color if enabled else cfg.checkbox_disabled_color
            )
        )

        self._checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                spacing: {cfg.checkbox_spacing}px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
                padding: {cfg.checkbox_padding_v}px 0;
            }}
            QCheckBox::indicator {{
                width: {cfg.checkbox_indicator_size}px;
                height: {cfg.checkbox_indicator_size}px;
                border: 2px solid {indicator_color};
                border-radius: {cfg.checkbox_indicator_radius}px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {indicator_color};
                border-color: {indicator_color};
            }}
        """
        )
