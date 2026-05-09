from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class SliderRow(QWidget):
    """
    A horizontal row containing a label, a QSlider, and optionally a
    trailing label that shows the current value. The slider's
    ``valueChanged(int)`` signal is re‑emitted directly.
    """

    valueChanged = Signal(int)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        min_val: int = 0,
        max_val: int = 100,
        value: int = 50,
        show_value: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label
        self._label = QLabel(label)
        self._label.setStyleSheet(styles.row_label(gui_config))
        self._label.setFixedHeight(gui_config.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter)

        # Slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(value)
        self._slider.setFixedHeight(gui_config.sidebar_row_height)
        self._slider.setStyleSheet(self._slider_style())
        self._slider.valueChanged.connect(self.valueChanged.emit)

        layout.addWidget(self._label)
        layout.addWidget(self._slider, stretch=1)

        # Optional value readout
        if show_value:
            self._value_label = QLabel(str(value))
            self._value_label.setFixedHeight(gui_config.sidebar_row_height)
            self._value_label.setStyleSheet(styles.row_label(gui_config))
            self._slider.valueChanged.connect(
                lambda v: self._value_label.setText(str(v))
            )
            layout.addWidget(self._value_label)

    def _slider_style(self) -> str:
        """Return the QSS string for the slider."""
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

    def value(self) -> int:
        return self._slider.value()

    def setValue(self, val: int) -> None:
        self._slider.setValue(val)
