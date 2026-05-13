from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QSizePolicy,
)

from .icon_tab_bar import IconTabBar
from ...config import GUIConfig
from ...styles import sidebar_container


class IconSidebarBase(QWidget):
    """
    Sidebar with icon tabs at the top and a stacked page area.
    Call `add_tab(widget, icon_name, tooltip)` to populate.
    """

    config_changed = Signal()

    def __init__(self, gui_config: GUIConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.gui_config = gui_config
        self.setFixedWidth(gui_config.sidebar_width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # ---- Styling ----
        self.setObjectName("sidebar_container")
        self.setStyleSheet(sidebar_container(gui_config))

        # Shadow Effect (disable for better performance,
        # but might need to evaluate its real weight further later on
        """shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.gray)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)"""

        # ---- Layout ----
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self._tab_bar: IconTabBar | None = None
        self._stack = QStackedWidget()
        layout.addWidget(self._stack, stretch=1)

    @property
    def current_tab_index(self) -> int:
        return self._tab_bar.current_index() if self._tab_bar else 0

    @current_tab_index.setter
    def current_tab_index(self, index: int) -> None:
        if self._tab_bar and 0 <= index < self._tab_bar.count():
            self._tab_bar.set_current_index(index)
            self._stack.setCurrentIndex(index)

    def add_tab(self, widget: QWidget, icon_name: str, tooltip: str) -> None:
        """
        Register a new tab with an icon and tooltip. The icon bar is
        created / updated automatically.
        """
        # Lazy creation of icon bar (insert at index 0)
        if self._tab_bar is None:
            self._tab_bar = IconTabBar(self.gui_config)
            # Insert before the stack (index 0)
            self.layout().insertWidget(0, self._tab_bar)
            self._tab_bar.currentChanged.connect(self._stack.setCurrentIndex)

        self._tab_bar.add_icon(icon_name, tooltip)
        self._stack.addWidget(widget)
