from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLineEdit,
    QPushButton,
    QWidget,
)

from ._base import BaseRow
from ...styles import file_dialog_style, line_edit_style, path_browse_button_style

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

        # Label
        self._init_label(label)

        if tooltip:
            self.setToolTip(tooltip)

        # Path field
        self._edit = QLineEdit(initial_path)
        self._edit.setFixedHeight(self._gui_config.sidebar.row_height)
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText(f"Select directory{chr(8230)}")
        self._edit.textChanged.connect(self._on_text_changed)
        self._content_layout.addWidget(self._edit, stretch=1)

        # Browse button
        self._browse_btn = QPushButton(chr(8230))
        self._browse_btn.setFixedSize(
            self._gui_config.swatch.browse_button_width,
            self._gui_config.sidebar.row_height,
        )
        self._browse_btn.setToolTip("Browse for directory.")
        self._browse_btn.setCursor(Qt.PointingHandCursor)
        self._browse_btn.clicked.connect(self._browse)
        self._content_layout.addWidget(self._browse_btn)

        self._apply_style()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def path(self) -> str:
        return self._edit.text()

    def setPath(self, path: str) -> None:
        self._edit.setText(path)

    # ------------------------------------------------------------------
    #  BaseRow overrides
    # ------------------------------------------------------------------
    def _on_enabled_changed(self, enabled: bool) -> None:
        self._browse_btn.setEnabled(enabled)
        self._edit.setReadOnly(not enabled)
        self._apply_style()

    def _is_highlighted(self) -> bool:
        if self._baseline is None:
            return False
        return self._edit.text() != self._baseline

    def _on_text_changed(self, text: str) -> None:
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------
    def _apply_style(self) -> None:
        self._edit.setStyleSheet(
            line_edit_style(self._gui_config, enabled=self.isEnabled())
        )
        self._browse_btn.setStyleSheet(
            path_browse_button_style(self._gui_config, enabled=self.isEnabled())
        )

    def _browse(self) -> None:
        current = self._edit.text() or os.path.expanduser("~")
        dlg = QFileDialog(parent=self, caption="Choose Screenshot Directory")
        dlg.setDirectory(current)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setOption(QFileDialog.DontResolveSymlinks, True)
        dlg.setStyleSheet(file_dialog_style(self._gui_config))
        if dlg.exec() == QFileDialog.Accepted:
            chosen = dlg.selectedFiles()[0]
            if chosen:
                self._edit.setText(chosen)
                self.pathChanged.emit(chosen)
