from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
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

from ..icons import load_pixmap
from ..styles import dialog_style, line_edit_style
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
        parent: Optional[QWidget] = None,
        exclude_handle: int = 0,
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Select Window", "Select Window dialog title"))
        self.setMinimumSize(500, 400)
        self._gui_config = gui_config
        self._exclude_handle = exclude_handle

        self.setStyleSheet(dialog_style(gui_config))

        layout = QVBoxLayout(self)

        # Filter input
        self._filter = QLineEdit()
        self._filter.setStyleSheet(line_edit_style(self._gui_config))
        self._filter.setPlaceholderText(
            self.tr("Filter windows", "Filter windows placeholder") + "…"
        )
        self._filter.textChanged.connect(self._populate)
        layout.addWidget(self._filter)

        # List of windows
        self._list = QListWidget()
        self._list.setIconSize(
            QSize(
                gui_config.profile.profile_icon_size,
                gui_config.profile.profile_icon_size,
            )
        )
        self._list.itemDoubleClicked.connect(self._accept)
        layout.addWidget(self._list)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._selected_win: Optional[WindowInfo] = None

        # Pre-load the fallback icon (generic window)
        pix = load_pixmap(
            "tabs/window",
            gui_config.profile.profile_icon_size,
            gui_config.profile.profile_icon_size,
            color=self._gui_config.palette.icon,
        )
        self._fallback_icon = QIcon(pix)

        self._populate()

    def _populate(self) -> None:
        self._list.clear()
        filter_text = self._filter.text().lower().strip()

        try:
            all_windows = list_windows()
        except Exception:
            QMessageBox.warning(
                self,
                self.tr("Error", "Could not list windows error"),
                self.tr("Could not list windows.", "Could not list windows error"),
            )
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
                    win.handle, size=self._gui_config.profile.saved_icon_size
                )
                if img and not img.isNull():
                    pix = QPixmap.fromImage(img)
                else:
                    pix = load_pixmap(
                        "tabs/window",
                        self._gui_config.profile.profile_icon_size,
                        self._gui_config.profile.profile_icon_size,
                        color=self._gui_config.palette.icon,
                    )
            except Exception:
                pix = load_pixmap(
                    "tabs/window",
                    self._gui_config.profile.profile_icon_size,
                    self._gui_config.profile.profile_icon_size,
                    color=self._gui_config.palette.icon,
                )

            item.setIcon(QIcon(pix))
            self._list.addItem(item)

    def _accept(self) -> None:
        item = self._list.currentItem()
        if item is None:
            QMessageBox.warning(
                self,
                self.tr("No selection", "No window selected warning title"),
                self.tr("Select a window first.", "No window selected warning"),
            )
            return
        self._selected_win = item.data(Qt.UserRole)
        self.accept()

    def selected_window(self) -> Optional[WindowInfo]:
        return self._selected_win
