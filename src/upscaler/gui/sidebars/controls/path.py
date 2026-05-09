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

        lbl = QLabel(label)
        lbl.setStyleSheet(styles.row_label(gui_config))
        lbl.setFixedHeight(gui_config.sidebar_row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        layout.addWidget(lbl)

        if tooltip:
            self.setToolTip(tooltip)

        self._edit = QLineEdit(initial_path)
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText("Select directory…")
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
        layout.addWidget(self._edit, stretch=1)

        browse_btn = QPushButton("…")
        browse_btn.setFixedSize(32, gui_config.sidebar_row_height)
        browse_btn.setToolTip("Browse for directory")
        browse_btn.setCursor(Qt.PointingHandCursor)
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)

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
