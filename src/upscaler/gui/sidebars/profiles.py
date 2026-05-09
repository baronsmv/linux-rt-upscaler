"""Left sidebar: Filter and Profiles tabs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from .common import SidebarBase
from ..grid import FilterBar

if TYPE_CHECKING:
    from ..config import GUIConfig


class ProfilesSidebar(SidebarBase):
    """Left sidebar containing the Filter bar and a Profiles placeholder."""

    def __init__(self, gui_config: GUIConfig, parent: QWidget | None = None) -> None:
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
        # (Add profile widgets here later)
        profiles_layout.addStretch()

        self.add_tab(filter_tab, "Filter")
        self.add_tab(profiles_tab, "Profiles")
