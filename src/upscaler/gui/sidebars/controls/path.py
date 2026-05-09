from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class PathPickerRow(QWidget):
    """Row with a label, a readonly path field, and a browse button."""

    pathChanged = Signal(str)

    def __init__(
        self,
        label: str,
        gui_config: GUIConfig,
        initial_path: str = "",
        tooltip: Optional[str] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = gui_config

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(label)
        self._label.setStyleSheet(styles.row_label(gui_config))
        self._label.setFixedHeight(gui_config.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter)
        layout.addWidget(self._label)

        if tooltip:
            self.setToolTip(tooltip)

        self._edit = QLineEdit(initial_path)
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText("Select directory…")
        self._edit.setStyleSheet(self._edit_style())
        layout.addWidget(self._edit, stretch=1)

        self._browse_btn = QPushButton("…")
        self._browse_btn.setFixedSize(32, gui_config.sidebar_row_height)
        self._browse_btn.setToolTip("Browse for directory")
        self._browse_btn.setCursor(Qt.PointingHandCursor)
        self._browse_btn.clicked.connect(self._browse)
        layout.addWidget(self._browse_btn)

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
        # The browse button already uses the native disabled look, but we can dim it further
        self._browse_btn.setEnabled(enabled)
        self._label.setStyleSheet(
            styles.row_label(self._cfg)
            if enabled
            else f"color: #555; font-size: {self._cfg.sidebar_tab_font_size}px;"
        )

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

    def path(self) -> str:
        return self._edit.text()

    def setPath(self, path: str) -> None:
        self._edit.setText(path)
