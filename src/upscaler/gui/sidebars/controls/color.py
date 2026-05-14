from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget

from ._base import BaseRow
from ...styles import color_swatch_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class ColorPickerRow(BaseRow):
    """
    A row with a label and a color-swatch button, plus highlight support.

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

        # Label
        self._init_label(label)
        self._content_layout.addStretch()

        if tooltip:
            self.setToolTip(tooltip)

        self._button = QPushButton()
        self._button.setFixedSize(
            gui_config.color_swatch_width, gui_config.color_swatch_height
        )
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._pick_color)
        self._content_layout.addWidget(self._button)

        self._update_highlight()
        self._apply_color()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._button.setEnabled(enabled)
        if enabled:
            self._apply_color()
        else:
            self._button.setStyleSheet(
                color_swatch_style(self._cfg, enabled=False, current_color="")
            )

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
            options=QColorDialog.DontUseNativeDialog | QColorDialog.ShowAlphaChannel,
        )
        if color.isValid():
            self._current_color = color
            self._apply_color()
            self.colorChanged.emit(color.name(QColor.HexArgb))
            self._update_highlight()

    def _apply_color(self) -> None:
        """Update the button's background to the current color."""
        self._button.setStyleSheet(
            color_swatch_style(
                self._cfg,
                enabled=True,
                current_color=self._current_color.name(QColor.HexArgb),
            )
        )
