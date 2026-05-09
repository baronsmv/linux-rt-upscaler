from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QHBoxLayout, QWidget

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class ColorPickerRow(BaseRow):
    """
    A row with a label and a color‑swatch button, plus highlight support.

    Emits ``colorChanged(str)`` with a hex string (e.g., "#AARRGGBB").
    """

    colorChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        initial_color: str = "#000000",
        tooltip: Optional[str] = None,
        baseline: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)
        self._current_color = (
            QColor(initial_color)
            if QColor.isValidColor(initial_color)
            else QColor("#000000")
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Indicator and label
        layout.addWidget(self._init_indicator())
        layout.addWidget(self._init_label(label))
        layout.addStretch()

        if tooltip:
            self.setToolTip(tooltip)

        self._button = QPushButton()
        self._button.setFixedSize(
            gui_config.color_swatch_width, gui_config.color_swatch_height
        )
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._pick_color)
        layout.addWidget(self._button)

        self._update_highlight()
        self._apply_color()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._button.setEnabled(enabled)
        if enabled:
            self._apply_color()
        else:
            self._button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self._cfg.color_swatch_disabled_bg};
                    border: 1px solid {self._cfg.control_disabled_border};
                    border-radius: 4px;
                }}
            """
            )

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return (
            self._current_color.name(QColor.HexArgb).lower() != self._baseline.lower()
        )

    # ------------------------------------------------------------------
    #  Color picking
    # ------------------------------------------------------------------
    def _pick_color(self) -> None:
        color = QColorDialog.getColor(
            initial=self._current_color,
            parent=self,
            title="Choose Background Color",
            options=QColorDialog.DontUseNativeDialog,
        )
        if color.isValid():
            self._current_color = color
            self._apply_color()
            self.colorChanged.emit(color.name(QColor.HexArgb))
            self._update_highlight()

    def _apply_color(self) -> None:
        """Update the button's background to the current color."""
        border = self._cfg.color_swatch_border
        hover = self._cfg.sidebar_combo_border_focus
        self._button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._current_color.name(QColor.HexArgb)};
                border: 1px solid {border};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: {hover};
            }}
        """
        )
