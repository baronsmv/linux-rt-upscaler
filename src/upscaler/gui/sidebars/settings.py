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
    StyleTab,
)
from ..styles import reset_button_style, reset_submenu_style, save_button_style
from ...config import Config, parse_config

if TYPE_CHECKING:
    from ..config import GUIConfig, GUIPalette


class SettingsSidebar(IconSidebarBase):
    """Right sidebar with icon tabs, footer buttons, and dirty-state tracking."""

    save_settings = Signal()
    reset_settings = Signal()
    restore_defaults = Signal()
    daemon_toggled = Signal(bool)
    style_applied = Signal(object)

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
        style_tab_args = gui_config, gui_config.palette, self._on_style_apply

        general_tab = GeneralTab(*tab_args, profile_active=profile_active)
        general_tab.daemon_toggled.connect(self.daemon_toggled)
        self._style_tab: Optional[StyleTab] = None

        tabs = [
            (
                general_tab,
                "general",
                self.tr("General", "Name of a settings tab"),
            ),
            (
                ScalingTab(*tab_args),
                "scaling",
                self.tr("Scaling", "Name of a settings tab"),
            ),
            (
                DisplayTab(*tab_args),
                "display",
                self.tr("Display", "Name of a settings tab"),
            ),
            (
                PresentationTab(*tab_args),
                "presentation",
                self.tr("Presentation", "Name of a settings tab"),
            ),
            (
                EffectsTab(*tab_args),
                "effects",
                self.tr("Effects", "Name of a settings tab"),
            ),
            (
                AdvancedTab(*tab_args),
                "advanced",
                self.tr("Advanced", "Name of a settings tab"),
            ),
            (
                ExtrasTab(*tab_args),
                "extras",
                self.tr("Extras", "Name of a settings tab"),
            ),
            (
                StyleTab(*style_tab_args),
                "style",
                self.tr("GUI Style", "Name of a settings tab"),
            ),
        ]

        for tab, icon, tooltip in tabs:
            self.add_tab(tab, f"tabs/{icon}", tooltip)
            if isinstance(tab, StyleTab):
                self._style_tab = tab
                tab.style_dirty_changed.connect(self._on_style_dirty_changed)
            else:
                tab.config_changed.connect(self._on_config_changed)

        # Listen to tab changes
        self._tab_bar.currentChanged.connect(self.on_tab_changed)

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

    def _on_style_apply(self, new_palette: GUIPalette) -> None:
        self.style_applied.emit(new_palette)

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
            reset_button_style(self.gui_config, active=self._dirty_yaml)
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
        """
        Creates the footer bar with Save/Reset buttons.

        The buttons are connected to internal delegating methods instead
        of directly emitting signals. This allows the footer to switch
        behavior seamlessly when the Style tab is active without
        disconnecting/reconnecting signals.

        - _on_footer_save: dispatches to StyleTab._apply_clicked() or save_settings
        - _on_footer_reset: dispatches to StyleTab._reset_style()   or reset_settings
        """
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
        self._save_btn = QPushButton(
            self.tr("Save Profile", "Save button")
            if self._profile_active
            else self.tr("Save", "Save button")
        )
        self._save_btn.setCursor(Qt.PointingHandCursor)
        self._save_btn.setFixedHeight(cfg.footer.button_height)
        self._save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._save_btn.clicked.connect(self._on_footer_save)
        self._save_btn.setStyleSheet(save_button_style(cfg))
        button_layout.addWidget(self._save_btn, 1)

        # ---- Reset split-button ----
        self._reset_btn = QToolButton()
        self._reset_btn.setText(self.tr("Reset", "Reset button"))
        self._reset_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._reset_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self._reset_btn.setCursor(Qt.PointingHandCursor)
        self._reset_btn.setFixedHeight(cfg.footer.button_height)
        self._reset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._reset_btn.clicked.connect(self._on_footer_reset)

        # Drop-down menu
        self._config_reset_menu = QMenu(self._reset_btn)
        restore_text = (
            self.tr("Clear profile overrides", "Reset button")
            if self._profile_active
            else self.tr("Restore system defaults", "Reset button")
        )
        self._restore_action = self._config_reset_menu.addAction(restore_text)
        self._restore_action.triggered.connect(self.restore_defaults.emit)
        self._config_reset_menu.setStyleSheet(reset_submenu_style(cfg))

        self._style_reset_menu = QMenu(self._reset_btn)
        self._style_reset_last_action = self._style_reset_menu.addAction(
            self.tr("Reset to last applied", "Reset button")
        )
        self._style_reset_auto_action = self._style_reset_menu.addAction(
            self.tr("Restore Auto preset", "Reset button")
        )
        self._style_reset_menu.setStyleSheet(reset_submenu_style(cfg))

        self._reset_btn.setMenu(self._config_reset_menu)
        button_layout.addWidget(self._reset_btn, 1)
        outer_layout.addWidget(button_widget)

        # Initial state: buttons disabled, Reset style set accordingly
        self._save_btn.setEnabled(False)
        self._reset_btn.setEnabled(False)
        self._reset_btn.setStyleSheet(reset_button_style(cfg, active=False))

        return outer

    def _on_footer_save(self):
        """If the Style tab is active, apply style; otherwise save config."""
        if self._is_style_tab_active():
            self._style_tab.apply_clicked()
        else:
            self.save_settings.emit()

    def _on_footer_reset(self):
        """If the Style tab is active, reset to last applied; otherwise reset config."""
        if self._is_style_tab_active():
            self._style_tab.reset_style()
        else:
            self.reset_settings.emit()

    def _is_style_tab_active(self) -> bool:
        return (
            self._style_tab is not None
            and self._stack.currentWidget() is self._style_tab
        )

    def on_tab_changed(self, index: int):
        """
        When the user clicks a tab icon, adjust the footer buttons.

        If the new tab is the Style tab:
          - Change labels to "Apply Style" / "Reset Style"
          - Replace the Reset button's dropdown with style-specific actions
          - Update enabled states based on the style's dirty flag
        Otherwise:
          - Restore the normal labels and config reset menu
          - Refresh the normal dirty-state tracking
        """
        if self._is_style_tab_active():
            # === Style tab active ===
            self._save_btn.setText(self.tr("Apply Style", "Apply button"))
            self._reset_btn.setText(self.tr("Reset Style", "Reset button"))
            # Swap menu
            self._reset_btn.setMenu(self._style_reset_menu)
            # Connect style menu actions
            try:
                self._style_reset_last_action.triggered.disconnect()
                self._style_reset_auto_action.triggered.disconnect()
            except Exception:
                pass
            self._style_reset_last_action.triggered.connect(self._style_tab.reset_style)
            self._style_reset_auto_action.triggered.connect(
                self._style_tab.restore_auto_preset
            )

            # Update enabled state from style dirty flag
            self._update_style_footer_state()
        else:
            # === Normal config tab ===
            self._save_btn.setText(
                self.tr("Save Profile", "Save button")
                if self._profile_active
                else self.tr("Save", "Save button")
            )
            self._reset_btn.setText(self.tr("Reset", "Reset button"))
            self._reset_btn.setMenu(self._config_reset_menu)
            # Restore normal config dirty-state logic
            self._check_dirty()  # existing method already sets enabled states

    def _on_style_dirty_changed(self, dirty: bool):
        """Called whenever the Style tab's dirty state changes."""
        if self._is_style_tab_active():
            self._update_style_footer_state()

    def _update_style_footer_state(self):
        """Enable Apply / Reset buttons based solely on style default/dirty state."""
        dirty = self._style_tab.is_dirty()
        is_default = self._style_tab.is_default()

        # Apply button is enabled only when there are unsaved changes
        self._save_btn.setEnabled(dirty)
        self._reset_btn.setEnabled(dirty or not is_default)
        self._reset_btn.setStyleSheet(reset_button_style(self.gui_config, active=dirty))

        # Dropdown actions
        self._style_reset_last_action.setEnabled(dirty)
        self._style_reset_auto_action.setEnabled(not is_default)
