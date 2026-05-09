from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from .common import IconSidebarBase
from .tabs import (
    DisplayTab,
    EffectsTab,
    GeneralTab,
    AdvancedTab,
    ExtrasTab,
)
from ...config import DEFAULT_CONFIG, parse_config

if TYPE_CHECKING:
    from ..config import GUIConfig
    from ...config import Config


class SettingsSidebar(IconSidebarBase):
    """Right sidebar with icon tabs, footer buttons, and dirty‑state tracking."""

    save_settings = Signal()
    reset_settings = Signal()

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        super().__init__(gui_config, parent)

        # ---- Baseline = system defaults ----
        self._bc = copy.deepcopy(DEFAULT_CONFIG)
        parse_config(self._bc)

        self._config = config
        self._dirty = False

        tabs = [
            (GeneralTab(gui_config, config, self._bc), "general", "General"),
            (DisplayTab(gui_config, config, self._bc), "display", "Display & Overlay"),
            (EffectsTab(gui_config, config, self._bc), "effects", "Effects"),
            (ExtrasTab(gui_config, config, self._bc), "extras", "Extras"),
            (AdvancedTab(gui_config, config, self._bc), "advanced", "Advanced"),
        ]

        for tab, icon, tooltip in tabs:
            self.add_tab(tab, f"tabs/{icon}", tooltip)
            tab.config_changed.connect(self._on_config_changed)

        # ---- Footer with Save & Reset buttons ----
        footer = self._create_footer()
        self.layout().addWidget(footer)

        self._check_dirty()

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_config_changed(self) -> None:
        """Any setting was modified; re‑evaluate dirty state."""
        self._check_dirty()

    # ------------------------------------------------------------------
    #  Dirty‑state logic
    # ------------------------------------------------------------------
    def _check_dirty(self) -> None:
        """Enable buttons only if at least one setting differs from the baseline."""
        dirty = self._has_changes()
        if dirty != self._dirty:
            self._dirty = dirty
            self._save_btn.setEnabled(dirty)
            self._reset_btn.setEnabled(dirty)

    def _has_changes(self) -> bool:
        """Compare the current config with the baseline config field by field."""
        import dataclasses

        for field in dataclasses.fields(self._config):
            # Skip internal fields never edited via the UI
            if field.name in ("config_file", "log_level", "log_file"):
                continue
            cur_val = getattr(self._config, field.name)
            base_val = getattr(self._bc, field.name)
            if cur_val != base_val:
                return True
        return False

    # ------------------------------------------------------------------
    #  Footer
    # ------------------------------------------------------------------
    def _create_footer(self) -> QWidget:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QPushButton, QWidget, QHBoxLayout

        cfg = self.gui_config
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Save button
        self._save_btn = QPushButton("Save")
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.clicked.connect(self.save_settings.emit)
        self._save_btn.setStyleSheet(
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
            QPushButton:disabled {{
                background: {cfg.sidebar_tab_background};
                color: {cfg.control_disabled_text};
                border-color: {cfg.control_disabled_border};
            }}
        """
        )
        layout.addWidget(self._save_btn, 1)

        # Reset button
        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.clicked.connect(self.reset_settings.emit)
        self._reset_btn.setStyleSheet(
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
            QPushButton:disabled {{
                background: {cfg.sidebar_tab_background};
                color: {cfg.control_disabled_text};
                border-color: {cfg.control_disabled_border};
            }}
        """
        )
        layout.addWidget(self._reset_btn, 1)

        return footer
