from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ._base import BaseRow

if TYPE_CHECKING:
    from ...config import GUIConfig


class PathPickerRow(BaseRow):
    """
    A row with a label, a readonly path field, and a browse button.

    Emits ``pathChanged(str)`` when the directory is changed.
    """

    pathChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        initial_path: str = "",
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

        # Path field
        self._edit = QLineEdit(initial_path)
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText("Select directory…")
        self._edit.setStyleSheet(self._edit_style())
        self._edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._edit, stretch=1)

        # Browse button
        self._browse_btn = QPushButton("…")
        self._browse_btn.setFixedSize(32, gui_config.sidebar_row_height)
        self._browse_btn.setToolTip("Browse for directory")
        self._browse_btn.setCursor(Qt.PointingHandCursor)
        self._browse_btn.clicked.connect(self._browse)
        layout.addWidget(self._browse_btn)

        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._edit.setReadOnly(not enabled)
        self._edit.setStyleSheet(
            self._edit_style()
            if enabled
            else self._edit_style()
            .replace("#ddd", "#555")
            .replace("#2a2a2c", "#1e1e1e")
        )
        self._browse_btn.setEnabled(enabled)

    def path(self) -> str:
        return self._edit.text()

    def setPath(self, path: str) -> None:
        self._edit.setText(path)

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return self._edit.text() != self._baseline

    def _on_text_changed(self, text: str) -> None:
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Style
    # ------------------------------------------------------------------
    def _edit_style(self) -> str:
        cfg = self._cfg
        return f"""
            QLineEdit {{
                background: #2a2a2c;
                border: 1px solid {cfg.sidebar_combo_border_color};
                border-radius: 6px;
                padding: 4px 8px;
                color: #ddd;
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {cfg.sidebar_combo_border_focus};
            }}
        """

    def _browse(self) -> None:
        current = self._edit.text() or os.path.expanduser("~")
        chosen = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Choose Screenshot Directory",
            dir=current,
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if chosen:
            self._edit.setText(chosen)
            self.pathChanged.emit(chosen)
