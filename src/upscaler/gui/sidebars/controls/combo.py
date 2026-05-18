from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QWidget

from ._base import BaseRow
from ...styles import combo_box_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class ComboRow(BaseRow):
    currentTextChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        items: List[str],
        current: Optional[str] = None,
        tooltip: Optional[str] = None,
        baseline: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)

        # Label
        self._init_label(label)

        # Combo box
        self._combo = QComboBox()
        self._combo.addItems(items)
        if current is not None and current in items:
            self._combo.setCurrentText(current)
        self._combo.setFixedHeight(gui_config.sidebar_row_height)
        self._combo.setMinimumWidth(100)
        self._combo.currentTextChanged.connect(self._on_current_text_changed)
        self._content_layout.addWidget(self._combo)

        if tooltip:
            self.setToolTip(tooltip)

        self._apply_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def currentText(self) -> str:
        return self._combo.currentText()

    def setCurrentText(self, text: str) -> None:
        self._combo.setCurrentText(text)
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._combo.setEnabled(enabled)
        self._apply_style()

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
        self._combo.setStyleSheet(combo_box_style(self._cfg, enabled=self.isEnabled()))
