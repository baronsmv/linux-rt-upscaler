from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class SliderRow(QWidget):
    valueChanged = Signal(int)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        min_val: int = 0,
        max_val: int = 100,
        value: int = 50,
        show_value: bool = False,
        value_formatter: callable | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config
        self._formatter = value_formatter

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # -- Label --
        self._label = QLabel(label)
        self._label.setStyleSheet(styles.row_label(gui_config))
        self._label.setFixedHeight(gui_config.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter)

        # -- Slider --
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        self._slider.setValue(value)
        self._slider.setFixedHeight(gui_config.sidebar_row_height)
        self._slider.setStyleSheet(self._slider_style())
        self._slider.setCursor(Qt.PointingHandCursor)
        self._slider.valueChanged.connect(self._on_value_changed)

        layout.addWidget(self._label)
        layout.addWidget(self._slider, stretch=1)

        # -- Optional value readout --
        if show_value:
            display = self._format(value)
            self._value_label = QLabel(display)
            self._value_label.setFixedHeight(gui_config.sidebar_row_height)
            self._value_label.setStyleSheet(styles.row_label(gui_config))
            layout.addWidget(self._value_label)
        else:
            self._value_label = None

    # ----------------------------------------------------------------
    #  Internal helpers
    # ----------------------------------------------------------------
    def _format(self, val: int) -> str:
        if self._formatter is not None:
            return self._formatter(val)
        return str(val)

    def _on_value_changed(self, val: int) -> None:
        if self._value_label is not None:
            self._value_label.setText(self._format(val))
        self.valueChanged.emit(val)

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

    # Public getter / setter
    def value(self) -> int:
        return self._slider.value()

    def setValue(self, val: int) -> None:
        self._slider.setValue(val)
