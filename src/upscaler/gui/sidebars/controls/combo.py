from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class ComboRow(BaseRow):
    """
    A row with a label and a styled QComboBox, plus highlight support.

    Emits ``currentTextChanged(str)`` when the user selects a different item.
    """

    currentTextChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        items: list[str],
        current: str | None = None,
        tooltip: Optional[str] = None,
        baseline: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Indicator and label from base
        indicator = self._init_indicator()
        layout.addWidget(indicator)
        label_w = self._init_label(label)
        layout.addWidget(label_w)

        # Combo box
        self._combo = QComboBox()
        self._combo.addItems(items)
        if current is not None and current in items:
            self._combo.setCurrentText(current)
        self._combo.setFixedHeight(gui_config.sidebar_row_height)
        self._combo.setMinimumWidth(100)
        self._combo.setStyleSheet(self._combo_style())
        self._combo.currentTextChanged.connect(self._on_current_text_changed)
        layout.addWidget(self._combo)

        if tooltip:
            self.setToolTip(tooltip)

        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._combo.setEnabled(enabled)
        self._combo.setStyleSheet(self._combo_style(enabled))

    def currentText(self) -> str:
        return self._combo.currentText()

    def setCurrentText(self, text: str) -> None:
        self._combo.setCurrentText(text)
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return self._combo.currentText() != self._baseline

    def _on_current_text_changed(self, text: str) -> None:
        self._update_highlight()
        self.currentTextChanged.emit(text)

    # ------------------------------------------------------------------
    #  Style helper
    # ------------------------------------------------------------------
    def _combo_style(self, enabled: bool = True) -> str:
        cfg = self._cfg
        bg = "#2a2a2c" if enabled else "#1e1e1e"
        text_color = "#ddd" if enabled else "#555"
        border = cfg.sidebar_combo_border_color if enabled else "#444"
        focus = cfg.sidebar_combo_border_focus if enabled else "#444"
        return f"""
            QComboBox {{
                background: {bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 4px 8px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QComboBox:hover {{
                border-color: {focus};
            }}
            QComboBox:focus {{
                border-color: {focus};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {border};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}
            QComboBox QAbstractItemView {{
                background: #2a2a2c;
                border: 1px solid {border};
                selection-background-color: {focus};
                color: #ddd;
            }}
        """
