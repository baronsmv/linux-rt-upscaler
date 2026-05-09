from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class ComboRow(QWidget):
    """
    A horizontal row with a descriptive label and a styled QComboBox.

    Emits ``currentTextChanged(str)`` when the user selects a different item.
    """

    currentTextChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        items: list[str],
        current: str | None = None,
        tooltip: Optional[str] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        self._label = QLabel(label)
        self._label.setStyleSheet(styles.row_label(gui_config))
        self._label.setFixedHeight(gui_config.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter)

        # Combo box
        self._combo = QComboBox()
        self._combo.addItems(items)
        if current is not None and current in items:
            self._combo.setCurrentText(current)
        self._combo.setFixedHeight(gui_config.sidebar_row_height)
        self._combo.setMinimumWidth(100)
        self._combo.setStyleSheet(self._combo_style())
        self._combo.currentTextChanged.connect(self.currentTextChanged.emit)

        if tooltip:
            self.setToolTip(tooltip)

        layout.addWidget(self._label)
        layout.addStretch()
        layout.addWidget(self._combo)

    def _combo_style(self) -> str:
        """Return the QSS string for the combo box."""
        cfg = self._cfg
        return f"""
            QComboBox {{
                background: #2a2a2c;
                border: 1px solid {cfg.sidebar_combo_border_color};
                border-radius: 6px;
                padding: 4px 8px;
                color: #ddd;
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QComboBox:hover {{
                border-color: {cfg.sidebar_combo_border_focus};
            }}
            QComboBox:focus {{
                border-color: {cfg.sidebar_combo_border_focus};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {cfg.sidebar_combo_border_color};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox QAbstractItemView {{
                background: #2a2a2c;
                border: 1px solid {cfg.sidebar_combo_border_color};
                selection-background-color: {cfg.sidebar_combo_border_focus};
                color: #ddd;
            }}
        """

    def currentText(self) -> str:
        return self._combo.currentText()

    def setCurrentText(self, text: str) -> None:
        self._combo.setCurrentText(text)
