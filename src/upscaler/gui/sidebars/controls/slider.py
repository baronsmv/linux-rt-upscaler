from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QLineEdit

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class SliderRow(QWidget):
    valueChanged = Signal(int)  # raw integer slider value
    floatValueChanged = Signal(float)  # scaled real value

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        min_val: int = 0,
        max_val: int = 100,
        value: int = 50,
        show_value: bool = False,
        value_formatter: Optional[Callable[[int], str]] = None,
        scale_factor: int = 1,  # <--- new
        editable: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config
        self._formatter = value_formatter
        self._editable = editable
        self._scale_factor = scale_factor

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # -- Label --
        self._label = QLabel(label)
        self._label.setStyleSheet(styles.row_label(gui_config))
        self._label.setFixedHeight(gui_config.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self._label)

        # -- Slider --
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(value)
        self._slider.setFixedHeight(gui_config.sidebar_row_height)
        self._slider.setStyleSheet(self._slider_style())
        self._slider.setCursor(Qt.PointingHandCursor)
        self._slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self._slider, stretch=1)

        # -- Value display / editable field --
        if show_value or editable:
            if editable:
                # Show real value initially
                initial_text = self._format(value)
                self._value_edit = QLineEdit(initial_text)
                self._value_edit.setFixedWidth(60)
                self._value_edit.setFixedHeight(gui_config.sidebar_row_height)
                self._value_edit.setStyleSheet(self._edit_style())
                self._value_edit.setAlignment(Qt.AlignCenter)
                self._value_edit.editingFinished.connect(self._on_edit_finished)
                self._value_label = None
                layout.addWidget(self._value_edit)
            else:
                self._value_label = QLabel(self._format(value))
                self._value_label.setFixedHeight(gui_config.sidebar_row_height)
                self._value_label.setStyleSheet(styles.row_label(gui_config))
                self._value_edit = None
                layout.addWidget(self._value_label)

    def setEnabled(self, enabled: bool) -> None:
        """Disable the slider and grey out the label / edit field."""
        super().setEnabled(enabled)
        if hasattr(self, "_label") and self._label is not None:
            self._label.setStyleSheet(
                styles.row_label(self._cfg)
                if enabled
                else f"color: #555; font-size: {self._cfg.sidebar_tab_font_size}px;"
            )
        if hasattr(self, "_value_edit") and self._value_edit is not None:
            self._value_edit.setReadOnly(not enabled)
            self._value_edit.setStyleSheet(
                self._edit_style()
                if enabled
                else self._edit_style()
                .replace("#ddd", "#555")
                .replace("#2a2a2c", "#1e1e1e")
            )
        if hasattr(self, "_value_label") and self._value_label is not None:
            self._value_label.setStyleSheet(
                styles.row_label(self._cfg)
                if enabled
                else f"color: #555; font-size: {self._cfg.sidebar_tab_font_size}px;"
            )

    # ----------------------------------------------------------------
    def _format(self, val: int) -> str:
        """Convert raw slider value to display string using formatter."""
        if self._formatter is not None:
            return self._formatter(val)
        # If scale factor > 1, show real float value unless formatter overrides
        if self._scale_factor > 1:
            return f"{val / self._scale_factor:.2f}"
        return str(val)

    def _on_value_changed(self, val: int) -> None:
        # Update read-only label
        if self._value_label is not None:
            self._value_label.setText(self._format(val))
        # Update editable field (avoid loop)
        if self._value_edit is not None:
            self._value_edit.blockSignals(True)
            self._value_edit.setText(self._format(val))
            self._value_edit.blockSignals(False)

        self.valueChanged.emit(val)
        if self._scale_factor > 1:
            self.floatValueChanged.emit(val / self._scale_factor)

    def _on_edit_finished(self) -> None:
        text = self._value_edit.text().strip()
        try:
            num = float(text)
        except ValueError:
            self._value_edit.setText(self._format(self._slider.value()))
            return

        # Convert to slider integer
        raw = round(num * self._scale_factor)
        clamped = max(self._slider.minimum(), min(self._slider.maximum(), raw))
        self._slider.setValue(clamped)
        # Self._on_value_changed will update label, but we can also set display to format
        self._value_edit.setText(self._format(clamped))

    def _slider_style(self) -> str:
        cfg = self._cfg
        return f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 4px;
                background: #333;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {cfg.sidebar_slider_color};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #6aade5;
            }}
            QSlider::sub-page:horizontal {{
                background: {cfg.sidebar_slider_color};
                border-radius: 2px;
            }}
        """

    def _edit_style(self) -> str:
        cfg = self._cfg
        return f"""
            QLineEdit {{
                background: #2a2a2c;
                border: 1px solid {cfg.sidebar_combo_border_color};
                border-radius: 6px;
                padding: 4px 6px;
                color: #ddd;
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {cfg.sidebar_combo_border_focus};
            }}
        """

    # Public API
    def value(self) -> int:
        return self._slider.value()

    def floatValue(self) -> float:
        return self._slider.value() / self._scale_factor

    def setValue(self, val: int) -> None:
        self._slider.setValue(val)
