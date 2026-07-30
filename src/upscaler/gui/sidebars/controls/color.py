from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget

from ._base import BaseRow
from ...styles import color_dialog_style, color_swatch_style
from ...utils import qcolor_to_rgba_hex, rgba_hex_to_qcolor

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
        self._current_color = rgba_hex_to_qcolor(initial_color)
        if not self._current_color.isValid():
            self._current_color = QColor(0, 0, 0, 255)

        # Label
        self._init_label(label)
        self._content_layout.addStretch()

        if tooltip:
            self.setToolTip(tooltip)

        self._button = QPushButton()
        self._button.setFixedSize(
            gui_config.swatch.swatch_width, gui_config.swatch.swatch_height
        )
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._pick_color)
        self._content_layout.addWidget(self._button)

        self._update_highlight()
        self._apply_color()

    def set_color(self, color_str: str) -> None:
        """
        Set the swatch to *color_str* without emitting ``colorChanged``.

        Useful for initializing or resetting the picker from saved data.
        Accepts any valid CSS string (named, hex, ``#RRGGBBAA``, etc.).
        """
        qcolor = rgba_hex_to_qcolor(color_str)
        if qcolor.isValid():
            self._current_color = qcolor
            self._apply_color()
            self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._button.setEnabled(enabled)
        if enabled:
            self._apply_color()
        else:
            self._button.setStyleSheet(
                color_swatch_style(self._gui_config, enabled=False, current_color="")
            )

    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False

        current = qcolor_to_rgba_hex(self._current_color).lower()
        baseline_qc = rgba_hex_to_qcolor(self._baseline)
        baseline = qcolor_to_rgba_hex(baseline_qc).lower()

        return current != baseline

    # ------------------------------------------------------------------
    #  Color picking
    # ------------------------------------------------------------------
    def _pick_color(self) -> None:
        dlg = QColorDialog(self._current_color, self)
        dlg.setWindowTitle("Choose Background Color")
        dlg.setOptions(QColorDialog.DontUseNativeDialog | QColorDialog.ShowAlphaChannel)
        dlg.setStyleSheet(color_dialog_style(self._gui_config))
        if dlg.exec() == QColorDialog.Accepted:
            color = dlg.currentColor()
            self._current_color = color
            self._apply_color()
            self.colorChanged.emit(qcolor_to_rgba_hex(color))
            self._update_highlight()

    def _apply_color(self) -> None:
        """Update the button's background using a format Qt Stylesheets understand."""
        css_color = self._current_color.name(QColor.HexArgb)
        self._button.setStyleSheet(
            color_swatch_style(
                self._gui_config,
                enabled=True,
                current_color=css_color,
            )
        )
