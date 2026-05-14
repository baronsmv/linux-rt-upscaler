from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSlider, QLineEdit, QLabel, QWidget

from ._base import BaseRow
from ...styles import line_edit_style, slider_style, slider_value_label_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class SliderRow(BaseRow):
    valueChanged = Signal(int)
    floatValueChanged = Signal(float)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        min_val: int = 0,
        max_val: int = 100,
        value: int = 50,
        show_value: bool = False,
        value_formatter: Optional[Callable[[int], str]] = None,
        scale_factor: int = 1,
        editable: bool = False,
        baseline: Optional[float] = None,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)
        self._formatter = value_formatter
        self._editable = editable
        self._scale_factor = scale_factor

        # Label
        self._init_label(label)

        # Slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(value)
        self._slider.setFixedHeight(gui_config.sidebar_row_height)
        self._slider.setCursor(Qt.PointingHandCursor)
        self._slider.valueChanged.connect(self._on_value_changed)
        self._content_layout.addWidget(self._slider, stretch=1)

        # Tooltip
        if tooltip:
            self._slider.setToolTip(tooltip)

        # Optional value display/edit
        self._value_label = None
        self._value_edit = None
        if show_value or editable:
            if editable:
                # Show real value initially
                initial_text = self._format(value)
                self._value_edit = QLineEdit(initial_text)
                self._value_edit.setFixedWidth(self._cfg.slider_value_edit_width)
                self._value_edit.setFixedHeight(gui_config.sidebar_row_height)
                self._value_edit.setAlignment(Qt.AlignCenter)
                self._value_edit.editingFinished.connect(self._on_edit_finished)
                self._content_layout.addWidget(self._value_edit)
            else:
                self._value_label = QLabel(self._format(value))
                self._value_label.setFixedHeight(gui_config.sidebar_row_height)
                self._content_layout.addWidget(self._value_label)

        self._apply_slider_style()
        self._apply_edit_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._apply_slider_style()
        self._apply_edit_style()
        self._apply_label_style()

    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        current = (
            self._slider.value() / self._scale_factor
            if self._scale_factor > 1
            else self._slider.value()
        )
        return abs(current - self._baseline) > 1e-6

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def value(self) -> int:
        return self._slider.value()

    def floatValue(self) -> float:
        return self._slider.value() / self._scale_factor

    def setValue(self, val: int) -> None:
        self._slider.setValue(val)

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------
    def _format(self, val: int) -> str:
        if self._formatter:
            return self._formatter(val)
        if self._scale_factor > 1:
            return f"{val / self._scale_factor:.2f}"
        return str(val)

    def _on_value_changed(self, val: int) -> None:
        if self._value_label:
            self._value_label.setText(self._format(val))
        if self._value_edit:
            self._value_edit.blockSignals(True)
            self._value_edit.setText(self._format(val))
            self._value_edit.blockSignals(False)
        self.valueChanged.emit(val)
        if self._scale_factor > 1:
            self.floatValueChanged.emit(val / self._scale_factor)
        self._update_highlight()

    def _on_edit_finished(self) -> None:
        text = self._value_edit.text().strip()
        try:
            num = float(text)
        except ValueError:
            self._value_edit.setText(self._format(self._slider.value()))
            return
        raw = round(num * self._scale_factor)
        clamped = max(self._slider.minimum(), min(self._slider.maximum(), raw))
        self._slider.setValue(clamped)
        self._value_edit.setText(self._format(clamped))

    def _apply_slider_style(self) -> None:
        self._slider.setStyleSheet(slider_style(self._cfg, enabled=self.isEnabled()))

    def _apply_edit_style(self) -> None:
        for w in (self._value_edit,):
            if w is not None:
                w.setStyleSheet(line_edit_style(self._cfg, enabled=self.isEnabled()))

    def _apply_label_style(self) -> None:
        if self._value_label:
            self._value_label.setStyleSheet(
                slider_value_label_style(self._cfg, enabled=self.isEnabled()),
            )
