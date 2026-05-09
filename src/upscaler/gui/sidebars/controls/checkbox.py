from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox

if TYPE_CHECKING:
    from ...config import GUIConfig


class CheckBox(QCheckBox):
    """
    A QCheckBox that includes its descriptive text and applies a polished
    stylesheet from :class:`GUIConfig`. No additional label is needed.

    Emits the standard ``stateChanged(int)`` and a convenience
    ``toggled(bool)`` signal.
    """

    def __init__(
        self,
        text: str,
        gui_config: GUIConfig,
        checked: bool = False,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(text, parent)
        self._cfg = gui_config
        self._checked_color = gui_config.sidebar_checkbox_color
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        self.setStyleSheet(self._make_style(True))

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self.setStyleSheet(self._make_style(enabled))

    def _make_style(self, enabled: bool) -> str:
        color = self._checked_color if enabled else "#555"
        text_color = self._cfg.sidebar_tab_text_color if enabled else "#555"
        border = self._cfg.sidebar_checkbox_color if enabled else "#555"
        return f"""
            QCheckBox {{
                spacing: 8px;
                color: {text_color};
                font-size: {self._cfg.sidebar_tab_font_size}px;
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
                background-color: {color};
                border-color: {color};
            }}
        """
