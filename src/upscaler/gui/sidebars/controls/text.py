from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class LineEditRow(QWidget):
    """Row with a descriptive label and a QLineEdit."""

    textChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        text: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet(styles.row_label(gui_config))
        lbl.setFixedHeight(gui_config.sidebar_row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        layout.addWidget(lbl)

        self._edit = QLineEdit(text)
        self._edit.setStyleSheet(
            f"""
            QLineEdit {{
                background: #2a2a2c;
                border: 1px solid {gui_config.sidebar_combo_border_color};
                border-radius: 6px;
                padding: 4px 8px;
                color: #ddd;
                font-size: {gui_config.sidebar_tab_font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {gui_config.sidebar_combo_border_focus};
            }}
        """
        )
        self._edit.setFixedHeight(gui_config.sidebar_row_height)
        self._edit.textChanged.connect(self.textChanged.emit)
        layout.addWidget(self._edit, stretch=1)

    def text(self) -> str:
        return self._edit.text()

    def setText(self, text: str) -> None:
        self._edit.setText(text)
