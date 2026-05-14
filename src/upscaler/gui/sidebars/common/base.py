from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QTabWidget,
    QSizePolicy,
)

from ...styles import sidebar_container_style, sidebar_tab_widget_style

if TYPE_CHECKING:
    from ...config import GUIConfig


class SidebarBase(QWidget):
    """
    A reusable sidebar panel that hosts a QTabWidget at its top.

    Call ``add_tab(widget, title)`` to populate tabs. The widget is styled
    with a rounded background and a soft drop shadow.
    """

    config_changed = Signal()

    def __init__(self, gui_config: GUIConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.gui_config = gui_config
        self.setFixedWidth(gui_config.sidebar_width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # ---- Visual identity ------------------------------------------------
        self.setObjectName("sidebar_container")
        self.setStyleSheet(sidebar_container_style(gui_config))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.gray)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # ---- Main layout (nothing but the tab widget) -----------------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(sidebar_tab_widget_style(gui_config))
        layout.addWidget(self.tab_widget)

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------
    def add_tab(self, widget: QWidget, title: str) -> None:
        """Add a new tab with the given title to the sidebar."""
        self.tab_widget.addTab(widget, title)
