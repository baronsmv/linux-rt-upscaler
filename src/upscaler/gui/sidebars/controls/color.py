from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class ColorPickerRow(QWidget):
    """A row with a label and a color‑swatch button."""

    colorChanged = Signal(str)  # emits a hex string (e.g., "#FF0000")

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        initial_color: str = "#000000",
        tooltip: Optional[str] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config
        self._current_color = (
            QColor(initial_color)
            if QColor.isValidColor(initial_color)
            else QColor("#000000")
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label)
        lbl.setStyleSheet(styles.row_label(gui_config))
        lbl.setFixedHeight(gui_config.sidebar_row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        layout.addWidget(lbl)
        layout.addStretch()

        if tooltip:
            self.setToolTip(tooltip)

        self._button = QPushButton()
        self._button.setFixedSize(36, 24)
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._pick_color)
        self._apply_color()
        layout.addWidget(self._button)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(
            initial=self._current_color,
            parent=self,
            title="Choose Background Color",
            options=QColorDialog.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_color = color
            self._apply_color()
            self.colorChanged.emit(color.name(QColor.HexArgb))

    def _apply_color(self) -> None:
        """Update the button's background to the current color."""
        self._button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._current_color.name(QColor.HexArgb)};
                border: 1px solid #777;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: {self._cfg.sidebar_combo_border_focus};
            }}
        """
        )
