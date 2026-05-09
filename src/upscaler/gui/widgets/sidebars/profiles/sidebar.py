from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout

from ..utils import SidebarBase
from ...filter_bar import FilterBar
from ....config import GUIConfig


class ProfilesSidebar(SidebarBase):
    """Left sidebar with Filter and Profiles tabs."""

    def __init__(self, gui_config: GUIConfig, parent=None):
        super().__init__(gui_config, parent)

        # ---- Filter tab ----
        filter_tab = QWidget()
        filter_layout = QVBoxLayout(filter_tab)
        filter_layout.setContentsMargins(12, 12, 12, 12)
        self.filter_bar = FilterBar(gui_config)
        filter_layout.addWidget(self.filter_bar)
        filter_layout.addStretch()

        # ---- Profiles tab (placeholder) ----
        profiles_tab = QWidget()
        profiles_layout = QVBoxLayout(profiles_tab)
        profiles_layout.setContentsMargins(12, 12, 12, 12)
        profiles_layout.addStretch()

        self.add_tab(filter_tab, "Filter")
        self.add_tab(profiles_tab, "Profiles")
