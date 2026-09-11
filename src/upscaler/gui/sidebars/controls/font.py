from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFontComboBox,
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from .base import BaseRow
from ...styles import combo_box_style, hotkey_clear_button_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class FontPickerRow(BaseRow):
    """Labeled row with a font-family picker and a reset-to-system button."""

    fontChanged = Signal(str)

    def __init__(
        self,
        cfg: GUIConfig,
        label: str,
        current: str,
        system_family: str,
        baseline: Optional[str] = None,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            cfg,
            baseline=(current if baseline is None else baseline),
            parent=parent,
        )
        self._cfg = cfg
        self._current = current
        self._system_family = system_family

        self._init_label(label)
        self._content_layout.setStretchFactor(self._label, 1)

        self._combo = QFontComboBox()
        self._combo.setEditable(False)
        self._combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._combo.setMinimumContentsLength(12)
        self._combo.setStyleSheet(combo_box_style(cfg))
        self._combo.setFixedHeight(cfg.sidebar.row_height)
        self._combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        if tooltip:
            self._combo.setToolTip(tooltip)

        self._combo.blockSignals(True)
        self._combo.setCurrentFont(QFont(self._current or system_family))
        self._combo.blockSignals(False)
        self._combo.currentFontChanged.connect(self._on_font_changed)

        self._reset_btn = QToolButton()
        self._reset_btn.setText("\u21ba")  # ↺
        self._reset_btn.setToolTip(
            self.tr("Reset to system font", "Font row reset tooltip")
        )
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.setFixedSize(cfg.sidebar.row_height, cfg.sidebar.row_height)
        self._reset_btn.setStyleSheet(hotkey_clear_button_style(cfg))
        self._reset_btn.clicked.connect(self._on_reset_clicked)

        control = QWidget()
        control_layout = QHBoxLayout(control)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(cfg.sidebar.row_spacing)
        control_layout.addWidget(self._combo, 1)
        control_layout.addWidget(self._reset_btn)
        self._content_layout.addWidget(control, 1)

        self._refresh_reset_state()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def font_family(self) -> str:
        return self._current

    def set_font_family(self, family: str) -> None:
        """Programmatically set the value without emitting (reset flows)."""
        self._current = family
        self._combo.blockSignals(True)
        self._combo.setCurrentFont(QFont(family or self._system_family))
        self._combo.blockSignals(False)
        self._refresh_reset_state()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow hooks
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        return self._current != (self._baseline or "")

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_font_changed(self, font: QFont) -> None:
        family = font.family()
        # Preserve the "system default" sentinel: when the picked family
        # equals the platform default, store "" so the value survives a
        # config port to another machine.
        if family == self._system_family:
            family = ""
        if family == self._current:
            return
        self._current = family
        self._refresh_reset_state()
        self._update_highlight()
        self.fontChanged.emit(family)

    def _on_reset_clicked(self) -> None:
        if not self._current:
            return
        self._current = ""
        self._combo.blockSignals(True)
        self._combo.setCurrentFont(QFont(self._system_family))
        self._combo.blockSignals(False)
        self._refresh_reset_state()
        self._update_highlight()
        self.fontChanged.emit("")

    def _refresh_reset_state(self) -> None:
        self._reset_btn.setEnabled(bool(self._current))
