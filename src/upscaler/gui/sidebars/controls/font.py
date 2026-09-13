from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from .base import BaseRow
from ...dialogs import FontPickerDialog
from ...styles import hotkey_button_style, hotkey_clear_button_style

if TYPE_CHECKING:
    from ...config import GUIConfig


# ---------------------------------------------------------------------------
#  Row
# ---------------------------------------------------------------------------
class FontPickerRow(BaseRow):
    """Labeled row with a font-family button and a reset-to-system button."""

    fontChanged = Signal(str)

    def __init__(
        self,
        cfg: GUIConfig,
        label: str,
        current: str,
        system_family: str,
        baseline: Optional[str] = None,
        tooltip: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            cfg,
            baseline=(current if baseline is None else baseline),
            parent=parent,
        )
        self._cfg = cfg
        self._current = current
        self._system_family = system_family

        self._init_label(label, tooltip)
        self._content_layout.setStretchFactor(self._label, 1)

        # ---- Font-family button -------------------------------------------
        self._button = QPushButton()
        self._button.setStyleSheet(hotkey_button_style(cfg))
        self._button.setFixedHeight(cfg.sidebar.row_height)
        self._button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._button.clicked.connect(self._open_picker)
        if tooltip:
            self._button.setToolTip(tooltip)

        # ---- Reset-to-system button ---------------------------------------
        self._reset_btn = QToolButton()
        self._reset_btn.setText("\u21ba")  # ↺
        self._reset_btn.setToolTip(
            self.tr("Reset to system font", "Font row reset tooltip")
        )
        self._reset_btn.setFixedSize(cfg.sidebar.row_height, cfg.sidebar.row_height)
        self._reset_btn.setStyleSheet(hotkey_clear_button_style(cfg))
        self._reset_btn.clicked.connect(self._on_reset_clicked)

        control = QWidget()
        control_layout = QHBoxLayout(control)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(cfg.sidebar.row_spacing)
        control_layout.addWidget(self._button, 1)
        control_layout.addWidget(self._reset_btn)
        self._content_layout.addWidget(control, 1)

        self._refresh_button_text()
        self._refresh_reset_state()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def font_family(self) -> str:
        return self._current

    def set_font_family(self, family: str) -> None:
        """Programmatically set the value without emitting (reset flows)."""
        self._current = family
        self._refresh_button_text()
        self._refresh_reset_state()
        self._update_highlight()

    # ------------------------------------------------------------------
    #  BaseRow hooks
    # ------------------------------------------------------------------
    def _is_highlighted(self) -> bool:
        return self._current != (self._baseline or "")

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _open_picker(self) -> None:
        dialog = FontPickerDialog(self._cfg, self._current or self._system_family, self)
        if dialog.exec() != QDialog.Accepted:
            return
        family = dialog.selected_family()
        if not family:
            return
        # Preserve the "system default" sentinel: when the picked family
        # equals the platform default, store "" so the value survives a
        # config port to another machine.
        new_value = "" if family == self._system_family else family
        if new_value == self._current:
            return
        self._current = new_value
        self._refresh_button_text()
        self._refresh_reset_state()
        self._update_highlight()
        self.fontChanged.emit(new_value)

    def _on_reset_clicked(self) -> None:
        if not self._current:
            return
        self._current = ""
        self._refresh_button_text()
        self._refresh_reset_state()
        self._update_highlight()
        self.fontChanged.emit("")

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _refresh_button_text(self) -> None:
        self._button.setText(self._current or self._system_family)

    def _refresh_reset_state(self) -> None:
        self._reset_btn.setEnabled(bool(self._current))
