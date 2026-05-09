from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QPushButton, QWidget

from ..common import styles
from ...config import GUIConfig


class ColorPickerRow(QWidget):
    """A row with a label and a color‑swatch button."""

    colorChanged = Signal(str)  # emits a hex string (e.g., "#FF0000")

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        initial_color: str = "#000000",
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

        self._button = QPushButton()
        self._button.setFixedSize(36, 24)
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._pick_color)
        self._apply_color()
        layout.addWidget(self._button)

    def _pick_color(self) -> None:
        dialog = QColorDialog(self._current_color, self)
        dialog.setOption(QColorDialog.ShowAlphaChannel, True)
        if dialog.exec() == QColorDialog.Accepted:
            self._current_color = dialog.currentColor()
            self._apply_color()
            hex_str = self._current_color.name(QColor.HexArgb)  # #AARRGGBB
            self.colorChanged.emit(hex_str)

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
