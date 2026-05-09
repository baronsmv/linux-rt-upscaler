from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QWidget

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class ComboRow(BaseRow):
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

        # Indicator and label
        layout.addWidget(self._init_indicator())
        layout.addWidget(self._init_label(label))

        # Combo box
        self._combo = QComboBox()
        self._combo.addItems(items)
        if current is not None and current in items:
            self._combo.setCurrentText(current)
        self._combo.setFixedHeight(gui_config.sidebar_row_height)
        self._combo.setMinimumWidth(100)
        self._combo.currentTextChanged.connect(self._on_current_text_changed)
        layout.addWidget(self._combo)

        if tooltip:
            self.setToolTip(tooltip)

        self._apply_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._combo.setEnabled(enabled)
        self._apply_style()

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
    def _apply_style(self) -> None:
        cfg = self._cfg
        enabled = self.isEnabled()
        bg = cfg.combo_background if enabled else cfg.combo_background_disabled
        text_color = cfg.combo_text_color if enabled else cfg.combo_text_color_disabled
        border = (
            cfg.sidebar_combo_border_color
            if enabled
            else cfg.combo_border_color_disabled
        )
        focus = (
            cfg.sidebar_combo_border_focus if enabled else cfg.control_disabled_border
        )
        popup_bg = cfg.combo_popup_background
        popup_selection = cfg.combo_popup_selection_background
        popup_text = cfg.combo_popup_text_color
        self._combo.setStyleSheet(
            f"""
            QComboBox {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {cfg.combo_border_radius}px;
                padding: {cfg.combo_padding_v}px {cfg.combo_padding_h}px;
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
                width: {cfg.combo_dropdown_width}px;
                border-left: 1px solid {border};
                border-top-right-radius: {cfg.combo_border_radius}px;
                border-bottom-right-radius: {cfg.combo_border_radius}px;
            }}
            QComboBox QAbstractItemView {{
                background: {popup_bg};
                border: 1px solid {border};
                selection-background-color: {popup_selection};
                color: {popup_text};
            }}
        """
        )
