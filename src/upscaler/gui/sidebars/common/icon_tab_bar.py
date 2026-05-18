from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QButtonGroup

from ...icons import load_pixmap
from ...styles import icon_tab_bar_style, icon_tab_button_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class IconTabBar(QWidget):
    """
    Grid-based icon bar. Call `add_icon(name, tooltip)` for each tab,
    then connect `currentChanged` to a `QStackedWidget`.
    """

    currentChanged = Signal(int)

    def __init__(self, gui_config: GUIConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._cfg = gui_config
        self._columns = gui_config.sidebar_icon_columns
        self._icon_size = gui_config.sidebar_icon_size

        self.setStyleSheet(icon_tab_bar_style(gui_config))

        layout = QGridLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setHorizontalSpacing(6)
        layout.setVerticalSpacing(6)

        self._grid = layout
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.idClicked.connect(self.currentChanged.emit)

        self._count = 0

    def count(self) -> int:
        """Return the total number of icon tabs."""
        return self._count

    def current_index(self) -> int:
        """Return the index of the currently checked icon, or 0 if none."""
        checked_id = self._button_group.checkedId()
        return checked_id if checked_id != -1 else 0

    def set_current_index(self, index: int) -> None:
        """Programmatically check the icon at the given index."""
        if 0 <= index < self._count:
            button = self._button_group.button(index)
            if button is not None:
                button.setChecked(True)

    def add_icon(self, icon_name: str, tooltip: str) -> QPushButton:
        """Append a new icon button and return it."""
        index = self._count
        row = index // self._columns
        col = index % self._columns

        btn = QPushButton()
        btn.setIcon(self._load_icon(icon_name, self._icon_size))
        btn.setIconSize(QSize(self._icon_size, self._icon_size))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(self._icon_size + 12, self._icon_size + 12)
        btn.setStyleSheet(icon_tab_button_style(self._cfg))

        self._grid.addWidget(btn, row, col)
        self._button_group.addButton(btn, index)
        self._count += 1

        # Select first button automatically
        if self._count == 1:
            btn.setChecked(True)
        return btn

    def _load_icon(self, name: str, size: int) -> QIcon:
        pixmap = load_pixmap(name, size, size, color=self._cfg.icon_color)
        return QIcon(pixmap)
