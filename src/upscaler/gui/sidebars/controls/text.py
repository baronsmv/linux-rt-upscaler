from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QWidget

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class LineEditRow(BaseRow):
    textChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        text: str = "",
        tooltip: Optional[str] = None,
        baseline: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, baseline, parent)

        # Label
        self._init_label(label)

        # Tooltip
        if tooltip:
            self.setToolTip(tooltip)

        # Line edit
        self._edit = QLineEdit(text)
        self._edit.setFixedHeight(gui_config.sidebar_row_height)
        self._edit.textChanged.connect(self._on_text_changed)
        self._content_layout.addWidget(self._edit, stretch=1)

        self._apply_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._edit.setReadOnly(not enabled)
        self._apply_style()
        self._update_highlight()

    def text(self) -> str:
        return self._edit.text()

    def setText(self, text: str) -> None:
        self._edit.setText(text)

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return self._edit.text() != self._baseline

    def _on_text_changed(self, text: str) -> None:
        self._update_highlight()
        self.textChanged.emit(text)

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------
    def _apply_style(self) -> None:
        cfg = self._cfg
        enabled = self.isEnabled()
        bg = cfg.edit_background if enabled else cfg.edit_background_disabled
        text_color = cfg.edit_text_color if enabled else cfg.edit_text_color_disabled
        border = (
            cfg.sidebar_combo_border_color if enabled else cfg.control_disabled_border
        )
        focus = (
            cfg.sidebar_combo_border_focus if enabled else cfg.control_disabled_border
        )
        self._edit.setStyleSheet(
            f"""
            QLineEdit {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {cfg.edit_border_radius}px;
                padding: {cfg.edit_padding_v}px {cfg.edit_padding_h}px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {focus};
            }}
        """
        )
