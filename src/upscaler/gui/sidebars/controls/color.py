from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget

from ._base import BaseRow
from ...styles import color_swatch_style

if TYPE_CHECKING:
    from ...config import GUIConfig


def qcolor_to_rgba_hex(q_color: QColor) -> str:
    """Helper to consistently return #RRGGBBAA from QColor."""
    argb = q_color.name(QColor.HexArgb)  # Returns #AARRGGBB
    return f"#{argb[3:9]}{argb[1:3]}"  # Returns #RRGGBBAA


def rgba_hex_to_qcolor(hex_str: str) -> QColor:
    """Safely converts a #RRGGBBAA string to a QColor."""
    if not isinstance(hex_str, str) or not hex_str.startswith("#") or len(hex_str) != 9:
        return QColor(hex_str)

    rrggbb = hex_str[1:7]
    aa = hex_str[7:9]
    return QColor(f"#{aa}{rrggbb}")  # Construct as #AARRGGBB for Qt


def normalize_to_hex(color_data) -> str:
    """Converts strings or (B, G, R, A) tuples to #RRGGBBAA."""
    if isinstance(color_data, (tuple, list)):
        b, g, r, a = color_data[0], color_data[1], color_data[2], color_data[3]
        qc = QColor.fromRgbF(r, g, b, a)
    else:
        # Use the parser instead of QColor(color_data)
        qc = rgba_hex_to_qcolor(color_data)
        if isinstance(color_data, str) and len(color_data) <= 7:
            qc.setAlpha(255)

    return qcolor_to_rgba_hex(qc) if qc.isValid() else "#000000ff"


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

        current = qcolor_to_rgba_hex(self._current_color).lower()
        baseline_qc = rgba_hex_to_qcolor(self._baseline)
        baseline = qcolor_to_rgba_hex(baseline_qc).lower()

        return current != baseline

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
            self.colorChanged.emit(qcolor_to_rgba_hex(color))
            self._update_highlight()

    def _apply_color(self) -> None:
        """Update the button's background using a format Qt Stylesheets understand."""
        css_color = self._current_color.name(QColor.HexArgb)
        self._button.setStyleSheet(
            color_swatch_style(
                self._cfg,
                enabled=True,
                current_color=css_color,
            )
        )
