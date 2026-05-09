from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from .common import SidebarBase

if TYPE_CHECKING:
    from ..config import GUIConfig


class ProfilesSidebar(SidebarBase):
    """Left sidebar – for now a single Profiles tab (empty)."""

    def __init__(self, gui_config: GUIConfig, parent: QWidget | None = None) -> None:
        super().__init__(gui_config, parent)

        # ---- Profiles tab (placeholder) ----
        profiles_tab = QWidget()
        layout = QVBoxLayout(profiles_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        label = QLabel("Profiles management will appear here.")
        label.setStyleSheet("color: #999; font-style: italic;")
        label.setWordWrap(True)
        layout.addWidget(label)
        layout.addStretch()

        self.add_tab(profiles_tab, "Profiles")
