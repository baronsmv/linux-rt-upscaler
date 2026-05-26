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
    PresentationTab,
    ScalingTab,
)
from ..styles import (
    footer_menu_style,
    footer_reset_button_style,
    footer_save_button_style,
)
from ...config import Config, parse_config

if TYPE_CHECKING:
    from ..config import GUIConfig


class SettingsSidebar(IconSidebarBase):
    """Right sidebar with icon tabs, footer buttons, and dirty-state tracking."""

    save_settings = Signal()
    reset_settings = Signal()
    restore_defaults = Signal()
    daemon_toggled = Signal(bool)

    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        profile_active: bool = False,
        profile_has_options: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(gui_config, parent)
        self._dirty_yaml = False
        self._dirty_system = False
        self._profile_active = profile_active
        self._profile_has_options = profile_has_options

        # ---- Baseline = snapshot of the currently loaded config ----
        self._config = config
        self._bc = copy.deepcopy(baseline_config)
        self._system_defaults = Config()
        parse_config(self._system_defaults)
        self._dirty = False

        tab_args = gui_config, config, self._bc
        general_tab = GeneralTab(*tab_args, profile_active=profile_active)
        general_tab.daemon_toggled.connect(self.daemon_toggled)

        tabs = [
            (general_tab, "general", "General"),
            (ScalingTab(*tab_args), "scaling", "Scaling"),
            (DisplayTab(*tab_args), "display", "Display & Overlay"),
            (PresentationTab(*tab_args), "presentation", "Presentation"),
            (EffectsTab(*tab_args), "effects", "Effects"),
            (ExtrasTab(*tab_args), "extras", "Extras"),
            (AdvancedTab(*tab_args), "advanced", "Advanced"),
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
    def is_dirty(self) -> bool:
        return self._dirty_yaml

    def _check_dirty(self) -> None:
        """Enable buttons only if at least one setting differs from the baseline."""
        self._dirty_yaml = self._has_changes(self._bc)
        self._dirty_system = self._has_changes(self._system_defaults)

        self._save_btn.setEnabled(self._dirty_yaml)

        # Determine whether the restore (dropdown) action should be available
        if self._profile_active:
            restore_enabled = self._profile_has_options
        else:
            restore_enabled = self._dirty_system

        self._restore_action.setEnabled(restore_enabled)

        # Reset button is enabled when its own action or the dropdown is usable
        self._reset_btn.setEnabled(self._dirty_yaml or restore_enabled)

        # Visual indicator for the dropdown (property used by stylesheet)
        self._reset_btn.setProperty(
            "dropdownActive", restore_enabled and not self._dirty_yaml
        )
        self._reset_btn.style().unpolish(self._reset_btn)
        self._reset_btn.style().polish(self._reset_btn)

        # Apply the reset button's stylesheet (dynamic colors based on state)
        self._reset_btn.setStyleSheet(
            footer_reset_button_style(
                self.gui_config,
                main_active=self._dirty_yaml,
                enabled=self._reset_btn.isEnabled(),
            )
        )

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
        self._save_btn = QPushButton("Save Profile" if self._profile_active else "Save")
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.setFixedHeight(cfg.footer_button_height)
        self._save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._save_btn.clicked.connect(self.save_settings.emit)
        self._save_btn.setStyleSheet(footer_save_button_style(cfg))
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
        restore_text = (
            "Clear profile overrides"
            if self._profile_active
            else "Restore system defaults"
        )
        self._restore_action = menu.addAction(restore_text)
        self._restore_action.triggered.connect(self.restore_defaults.emit)
        self._reset_btn.setMenu(menu)

        menu.setStyleSheet(footer_menu_style(cfg))

        button_layout.addWidget(self._reset_btn, 1)
        outer_layout.addWidget(button_widget)

        # Initial state: buttons disabled, Reset style set accordingly
        self._save_btn.setEnabled(False)
        self._reset_btn.setEnabled(False)
        self._reset_btn.setStyleSheet(
            footer_reset_button_style(cfg, main_active=False, enabled=False)
        )

        return outer
