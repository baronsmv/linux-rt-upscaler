from __future__ import annotations

from typing import TYPE_CHECKING

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
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._cfg = gui_config
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(self._make_style())

    def _make_style(self) -> str:
        """Build the full stylesheet string for the checkbox."""
        cfg = self._cfg
        return f"""
            QCheckBox {{
                spacing: 8px;
                color: {cfg.sidebar_tab_text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
                padding: 4px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                border-radius: 4px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {cfg.sidebar_checkbox_color};
                border-color: {cfg.sidebar_checkbox_color};
            }}
            QCheckBox::indicator:hover {{
                border-color: {cfg.sidebar_checkbox_color};
            }}
            QCheckBox::disabled {{
                color: #666;
            }}
        """
