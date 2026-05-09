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
        self._edit.setReadOnly(True)
        self._edit.setPlaceholderText("Select directory…")
        self._edit.textChanged.connect(self._on_text_changed)
        self._content_layout.addWidget(self._edit, stretch=1)

        # Browse button
        self._browse_btn = QPushButton("…")
        self._browse_btn.setFixedSize(
            self._cfg.path_browse_button_width, self._cfg.sidebar_row_height
        )
        self._browse_btn.setToolTip("Browse for directory")
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
