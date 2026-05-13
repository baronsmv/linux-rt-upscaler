from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ._styles import list_stylesheet
from ..icons import load_pixmap
from ...window import WindowInfo, list_windows, get_window_icon

if TYPE_CHECKING:
    from ..config import GUIConfig


class WindowPickerDialog(QDialog):
    """Dialog to select a window from the list of open windows, with icons
    and double-click support.  Excludes the main GUI window if its handle
    is provided.
    """

    def __init__(
        self,
        gui_config: GUIConfig,
        parent: QWidget | None = None,
        exclude_handle: int = 0,
    ):
        super().__init__(parent)
        self.setWindowTitle("Select Window")
        self.setMinimumSize(500, 400)
        self._cfg = gui_config
        self._exclude_handle = exclude_handle

        self.setStyleSheet(list_stylesheet(gui_config))

        layout = QVBoxLayout(self)

        # Filter input
        self._filter = QLineEdit()
        self._filter.setPlaceholderText(f"Filter windows{chr(8230)}")
        self._filter.textChanged.connect(self._populate)
        layout.addWidget(self._filter)

        # List of windows
        self._list = QListWidget()
        self._list.setIconSize(
            QSize(
                gui_config.profile_item_icon_size,
                gui_config.profile_item_icon_size,
            )
        )
        self._list.itemDoubleClicked.connect(self._accept)
        layout.addWidget(self._list)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._selected_win: WindowInfo | None = None

        # Pre-load the fallback icon (generic window)
        pix = load_pixmap(
            "tabs/window",
            gui_config.profile_item_icon_size,
            gui_config.profile_item_icon_size,
            color=self._cfg.icon_color,
        )
        self._fallback_icon = QIcon(pix)

        self._populate()

    def _populate(self) -> None:
        self._list.clear()
        filter_text = self._filter.text().lower().strip()

        try:
            all_windows = list_windows()
        except Exception:
            QMessageBox.warning(self, "Error", "Could not list windows.")
            return

        # Sort by title, case-insensitive
        all_windows.sort(key=lambda w: w.title.lower())

        for win in all_windows:
            if not win.title.strip():
                continue
            if filter_text and filter_text not in win.title.lower():
                continue
            # Exclude our own GUI window
            if self._exclude_handle and win.handle == self._exclude_handle:
                continue

            # Build item text with size info
            item_text = f"{win.title}  ({win.width}{chr(215)}{win.height})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, win)

            # Try to fetch window icon; use fallback if not available
            try:
                img = get_window_icon(
                    win.handle, size=self._cfg.profile_capture_icon_size
                )
                if img and not img.isNull():
                    from PySide6.QtGui import QPixmap

                    pix = QPixmap.fromImage(img)
                else:
                    pix = load_pixmap(
                        "tabs/window",
                        self._cfg.profile_item_icon_size,
                        self._cfg.profile_item_icon_size,
                        color=self._cfg.icon_color,
                    )
            except Exception:
                pix = load_pixmap(
                    "tabs/window",
                    self._cfg.profile_item_icon_size,
                    self._cfg.profile_item_icon_size,
                    color=self._cfg.icon_color,
                )

            item.setIcon(QIcon(pix))
            self._list.addItem(item)

    def _accept(self) -> None:
        item = self._list.currentItem()
        if item is None:
            QMessageBox.warning(self, "No selection", "Select a window first.")
            return
        self._selected_win = item.data(Qt.UserRole)
        self.accept()

    def selected_window(self) -> WindowInfo | None:
        return self._selected_win
