from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from .common import IconSidebarBase
from .tabs import (
    DisplayTab,
    EffectsTab,
    GeneralTab,
    AdvancedTab,
    ExtrasTab,
)

if TYPE_CHECKING:
    from ..config import GUIConfig
    from ...config import Config


class SettingsSidebar(IconSidebarBase):
    """Right sidebar with three intuitive categories."""

    save_settings = Signal()
    reset_settings = Signal()

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        super().__init__(gui_config, parent)

        tabs = [
            (GeneralTab(gui_config, config), "general", "General"),
            (DisplayTab(gui_config, config), "display", "Display & Overlay"),
            (EffectsTab(gui_config, config), "effects", "Effects"),
            (ExtrasTab(gui_config, config), "extras", "Extras"),
            (AdvancedTab(gui_config, config), "advanced", "Advanced"),
        ]

        for tab, icon, tooltip in tabs:
            self.add_tab(tab, f"tabs/{icon}", tooltip)
            tab.config_changed.connect(self.config_changed.emit)

        # ---- Footer with Save & Reset buttons ----
        footer = self._create_footer()
        # Append footer to the sidebar's main vertical layout
        self.layout().addWidget(footer)

    def _create_footer(self) -> QWidget:
        cfg = self.gui_config
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Save button – blue accent
        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings.emit)
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {cfg.sidebar_tab_background};
                color: {cfg.sidebar_tab_text_color_active};
                border: 2px solid {cfg.sidebar_tab_indicator_color};
                border-radius: 8px;
                padding: 6px 18px;
                font-size: {cfg.sidebar_tab_font_size}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {cfg.sidebar_tab_background_active};
                border-color: {cfg.sidebar_combo_border_focus};
            }}
            QPushButton:pressed {{
                background: {cfg.sidebar_tab_background_active};
                border-color: {cfg.sidebar_tab_indicator_color};
            }}
        """
        )
        layout.addWidget(save_btn, 1)

        # Reset button – red accent
        reset_btn = QPushButton("Reset")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self.reset_settings.emit)
        reset_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {cfg.sidebar_tab_background};
                color: {cfg.sidebar_tab_text_color};
                border: 2px solid #914343;
                border-radius: 8px;
                padding: 6px 18px;
                font-size: {cfg.sidebar_tab_font_size}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {cfg.sidebar_tab_background_active};
                border-color: #b55a5a;
            }}
            QPushButton:pressed {{
                background: {cfg.sidebar_tab_background_active};
                border-color: #914343;
            }}
        """
        )
        layout.addWidget(reset_btn, 1)

        return footer
