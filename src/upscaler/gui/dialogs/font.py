from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..styles import dialog_style, line_edit_style

if TYPE_CHECKING:
    from ..config import GUIConfig


class FontPickerDialog(QDialog):
    """Modal font-family picker with live filtering and a preview."""

    def __init__(
        self,
        cfg: GUIConfig,
        current_family: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = cfg

        self.setWindowTitle(self.tr("Select Font", "Font picker dialog title"))
        self.setStyleSheet(dialog_style(cfg))
        self.setMinimumSize(360, 460)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # ---- Filter -------------------------------------------------------
        self._filter = QLineEdit()
        self._filter.setPlaceholderText(
            self.tr("Filter", "Font picker filter placeholder")
        )
        self._filter.setStyleSheet(line_edit_style(cfg))
        self._filter.textChanged.connect(self._apply_filter)
        layout.addWidget(self._filter)

        # ---- Family list --------------------------------------------------
        self._list = QListWidget()
        self._list.setUniformItemSizes(True)
        self._list.itemSelectionChanged.connect(self._update_preview)
        self._list.itemDoubleClicked.connect(lambda _: self.accept())
        layout.addWidget(self._list, 1)

        # ---- Preview ------------------------------------------------------
        preview_label = QLabel(self.tr("Preview", "Font picker preview label"))
        layout.addWidget(preview_label)

        self._preview = QLabel(
            self.tr(
                "The quick brown fox jumps over the lazy dog. 0123456789",
                "Font picker preview text",
            )
        )
        self._preview.setStyleSheet(
            f"border: 1px solid {cfg.palette.border}; "
            f"border-radius: {cfg.dialog.input_border_radius}px; "
            f"padding: {cfg.dialog.input_padding}; "
            f"color: {cfg.palette.text};"
        )
        layout.addWidget(self._preview)

        # ---- Buttons ------------------------------------------------------
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate(current_family)

        self._filter.setFocus()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def selected_family(self) -> str:
        """Return the family name of the highlighted item, or empty string."""
        item = self._list.currentItem()
        return item.text() if item is not None else ""

    # ------------------------------------------------------------------
    #  Internals
    # ------------------------------------------------------------------
    def _populate(self, current_family: str) -> None:
        """Fill the list from the font database and highlight the current entry."""
        families = QFontDatabase.families()
        for family in sorted(families, key=str.lower):
            item = QListWidgetItem(family)
            self._list.addItem(item)

        # Highlight the current family, if it is still installed.
        target = current_family.lower()
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.text().lower() == target:
                self._list.setCurrentRow(i)
                self._list.scrollToItem(item, QListWidget.PositionAtCenter)
                break

    def _apply_filter(self, text: str) -> None:
        """Hide items that do not contain *text* (case-insensitive)."""
        needle = text.strip().lower()
        first_match: Optional[QListWidgetItem] = None
        for i in range(self._list.count()):
            item = self._list.item(i)
            matches = not needle or needle in item.text().lower()
            item.setHidden(not matches)
            if matches and first_match is None:
                first_match = item

        # Keep a sensible selection while the user types
        if first_match is not None:
            current = self._list.currentItem()
            if current is None or current.isHidden():
                self._list.setCurrentItem(first_match)

    def _update_preview(self) -> None:
        """Render the preview text in the currently highlighted family."""
        item = self._list.currentItem()
        if item is None:
            return
        font = QFont(item.text())
        font.setPixelSize(self._cfg.dialog.label_font_size)
        self._preview.setFont(font)
