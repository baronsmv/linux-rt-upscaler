from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class LineEditRow(BaseRow):
    """
    A row with a descriptive label and a QLineEdit, plus highlight support.

    Emits ``textChanged(str)`` when the text is modified.
    """

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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Indicator and label
        indicator = self._init_indicator()
        layout.addWidget(indicator)
        label_w = self._init_label(label)
        layout.addWidget(label_w)

        if tooltip:
            self.setToolTip(tooltip)

        # Line edit
        self._edit = QLineEdit(text)
        self._edit.setStyleSheet(
            f"""
            QLineEdit {{
                background: #2a2a2c;
                border: 1px solid {gui_config.sidebar_combo_border_color};
                border-radius: 6px;
                padding: 4px 8px;
                color: #ddd;
                font-size: {gui_config.sidebar_tab_font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {gui_config.sidebar_combo_border_focus};
            }}
            """
        )
        self._edit.setFixedHeight(gui_config.sidebar_row_height)
        self._edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._edit, stretch=1)

        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._edit.setReadOnly(not enabled)
        self._edit.setStyleSheet(
            """
            QLineEdit {
                background: %s;
                border: 1px solid %s;
                border-radius: 6px;
                padding: 4px 8px;
                color: %s;
                font-size: %dpx;
            }
            QLineEdit:focus {
                border-color: %s;
            }
            """
            % (
                "#2a2a2c" if enabled else "#1e1e1e",
                self._cfg.sidebar_combo_border_color if enabled else "#444",
                "#ddd" if enabled else "#555",
                self._cfg.sidebar_tab_font_size,
                self._cfg.sidebar_combo_border_focus if enabled else "#444",
            )
        )

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
