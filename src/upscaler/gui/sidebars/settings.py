from __future__ import annotations

import copy
import dataclasses
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .common import IconSidebarBase
from .tabs import (
    AdvancedTab,
    DisplayTab,
    EffectsTab,
    ExtrasTab,
    GeneralTab,
)
from ...config import Config, parse_config

if TYPE_CHECKING:
    from ..config import GUIConfig


class SettingsSidebar(IconSidebarBase):
    """Right sidebar with icon tabs, footer buttons, and dirty-state tracking."""

    save_settings = Signal()
    reset_settings = Signal()
    restore_defaults = Signal()

    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, parent)

        # ---- Baseline = snapshot of the currently loaded config ----
        self._config = config
        self._bc = copy.deepcopy(baseline_config)
        self._system_defaults = Config()
        parse_config(self._system_defaults)
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
        """Any setting was modified; re-evaluate dirty state."""
        self._check_dirty()

    # ------------------------------------------------------------------
    #  Dirty-state logic
    # ------------------------------------------------------------------
    def _check_dirty(self) -> None:
        """Enable buttons only if at least one setting differs from the baseline."""
        dirty_yaml = self._has_changes(self._bc)  # vs YAML baseline
        dirty_system = self._has_changes(self._system_defaults)  # vs factory defaults

        # Save button is only meaningful for YAML delta
        self._save_btn.setEnabled(dirty_yaml)
        self._reset_btn.setEnabled(dirty_yaml or dirty_system)

        # Gray out the restore action if already at system defaults
        self._restore_action.setEnabled(dirty_system)

        self._update_reset_button_style()

    def _has_changes(self, baseline: Config) -> bool:
        """Compare the current config with the baseline config field by field."""
        for field in dataclasses.fields(self._config):
            if field.name in ("config_file", "log_level", "log_file"):
                continue
            if getattr(self._config, field.name) != getattr(baseline, field.name):
                return True
        return False

    # ------------------------------------------------------------------
    #  Footer
    # ------------------------------------------------------------------
    def _create_footer(self) -> QWidget:
        cfg = self.gui_config

        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(8, 8, 8, 8)
        button_layout.setSpacing(8)

        # ---- Save button ----
        self._save_btn = QPushButton("Save")
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.setFixedHeight(cfg.footer_button_height)
        self._save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._save_btn.clicked.connect(self.save_settings.emit)
        self._save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {cfg.footer_save_bg};
                color: {cfg.footer_save_text};
                border: 2px solid {cfg.footer_save_border};
                border-radius: {cfg.footer_button_radius}px;
                padding: {cfg.footer_button_padding_v}px {cfg.footer_button_padding_h}px;
                font-size: {cfg.sidebar_tab_font_size}px;
                font-weight: 600;
                height: {cfg.footer_button_height}px;
            }}
            QPushButton:hover {{
                background: {cfg.footer_save_hover_bg};
                border-color: {cfg.footer_save_hover_border};
            }}
            QPushButton:pressed {{
                background: {cfg.footer_save_hover_bg};
                border-color: {cfg.footer_save_border};
            }}
            QPushButton:disabled {{
                background: {cfg.footer_save_disabled_bg};
                color: {cfg.footer_save_disabled_text};
                border-color: {cfg.footer_save_disabled_border};
            }}
        """
        )
        button_layout.addWidget(self._save_btn, 1)

        # ---- Reset split-button ----
        self._reset_btn = QToolButton()
        self._reset_btn.setText("Reset")
        self._reset_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._reset_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.setFixedHeight(cfg.footer_button_height)
        self._reset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._reset_btn.clicked.connect(self.reset_settings.emit)

        # Drop-down menu
        menu = QMenu(self._reset_btn)
        self._restore_action = menu.addAction("Restore System Defaults")
        self._restore_action.triggered.connect(self.restore_defaults.emit)
        self._reset_btn.setMenu(menu)

        menu.setStyleSheet(
            f"""
            QMenu {{
                background: {cfg.footer_menu_bg};
                border: 1px solid {cfg.footer_menu_border};
                border-radius: 4px;
                padding: 4px;
            }}
            QMenu::item {{
                color: {cfg.footer_menu_text};
                padding: 6px 24px;
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QMenu::item:selected {{
                background: {cfg.footer_menu_selection_bg};
                color: {cfg.footer_menu_selection_text};
            }}
        """
        )

        button_layout.addWidget(self._reset_btn, 1)
        outer_layout.addWidget(button_widget)

        # Apply initial styles (also sets the correct split-line color)
        self._save_btn.setEnabled(False)
        self._reset_btn.setEnabled(False)
        self._update_reset_button_style()

        return outer

    def _update_reset_button_style(self) -> None:
        """Re-apply the Reset button stylesheet with the correct split-line color."""
        cfg = self.gui_config
        enabled = self._reset_btn.isEnabled()
        split = (
            cfg.footer_reset_split_border
            if enabled
            else cfg.footer_reset_disabled_border
        )

        self._reset_btn.setStyleSheet(
            f"""
            QToolButton {{
                background: {cfg.footer_reset_bg};
                color: {cfg.footer_reset_text};
                border: 2px solid {cfg.footer_reset_border};
                border-radius: {cfg.footer_button_radius}px;
                padding: {cfg.footer_button_padding_v}px {cfg.footer_button_padding_h}px;
                font-size: {cfg.sidebar_tab_font_size}px;
                font-weight: 600;
                height: {cfg.footer_button_height}px;
            }}
            QToolButton:hover {{
                background: {cfg.footer_reset_hover_bg};
                border-color: {cfg.footer_reset_hover_border};
            }}
            QToolButton:pressed {{
                background: {cfg.footer_reset_hover_bg};
                border-color: {cfg.footer_reset_border};
            }}
            QToolButton:disabled {{
                background: {cfg.footer_reset_disabled_bg};
                color: {cfg.footer_reset_disabled_text};
                border-color: {cfg.footer_reset_disabled_border};
            }}
            QToolButton::menu-button {{
                background: transparent;
                border: none;
                border-left: 1px solid {split};
                width: 20px;
            }}
            QToolButton::menu-arrow {{
                width: 12px;
                height: 12px;
            }}
        """
        )
