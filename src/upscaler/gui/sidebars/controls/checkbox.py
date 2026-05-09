from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
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
        self._checked_value = checked

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Indicator from base (no label)
        indicator = self._init_indicator()
        layout.addWidget(indicator)

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

    def _apply_style(self, highlighted: Optional[bool] = None) -> None:
        if highlighted is None:
            highlighted = self._is_highlighted()

        cfg = self._cfg
        enabled = self.isEnabled()

        text_color = (
            cfg.highlight_label_color if highlighted else cfg.sidebar_tab_text_color
        )
        if not enabled:
            text_color = "#555"
        border = (
            cfg.highlight_border_color
            if highlighted
            else (cfg.sidebar_checkbox_color if enabled else "#555")
        )

        self._checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                spacing: 8px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {border};
                border-radius: 4px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {border};
                border-color: {border};
            }}
        """
        )
