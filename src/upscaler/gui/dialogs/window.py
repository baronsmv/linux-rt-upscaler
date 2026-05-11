from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
)

from ...window import WindowInfo, list_windows


class WindowPickerDialog(QDialog):
    """Dialog to select a window from the list of open windows."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Window")
        self.setMinimumSize(450, 350)

        # Dark theme
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1e1e1e;
                color: #ddd;
            }
            QLineEdit {
                background: #2a2a2c;
                border: 1px solid #3a3a3c;
                border-radius: 4px;
                padding: 6px 10px;
                color: #ddd;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
            QListWidget {
                background: #1e1e1e;
                border: 1px solid #333;
                border-radius: 6px;
                outline: none;
                color: #ddd;
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #2c2c2c;
                color: #fff;
            }
            QListWidget::item:selected {
                background: #3a3a3c;
                color: #fff;
            }
            QPushButton {
                background: #2c2c2c;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px 16px;
                color: #ddd;
            }
            QPushButton:hover {
                background: #3a3a3c;
                border-color: #555;
            }
            QPushButton:disabled {
                color: #555;
            }
        """
        )

        layout = QVBoxLayout(self)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filter windows…")
        self._filter.textChanged.connect(self._populate)
        layout.addWidget(self._filter)

        self._list = QListWidget()
        layout.addWidget(self._list)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._selected_win: Optional[WindowInfo] = None
        self._populate()

    def _populate(self):
        self._list.clear()
        filter_text = self._filter.text().lower().strip()
        try:
            windows = list_windows()
        except Exception:
            QMessageBox.warning(self, "Error", "Could not list windows.")
            return
        for win in windows:
            if not win.title.strip():
                continue
            if filter_text and filter_text not in win.title.lower():
                continue
            item = QListWidgetItem(f"{win.title} ({win.width}x{win.height})")
            item.setData(Qt.UserRole, win)
            self._list.addItem(item)

    def _accept(self):
        item = self._list.currentItem()
        if item:
            self._selected_win = item.data(Qt.UserRole)
            self.accept()
        else:
            QMessageBox.warning(self, "No selection", "Select a window.")

    def selected_window(self) -> Optional[WindowInfo]:
        return self._selected_win
