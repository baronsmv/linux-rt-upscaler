from __future__ import annotations

from typing import TYPE_CHECKING

from .common import SidebarBase
from .tabs import AdvancedTab, EffectsTab, GeneralTab

if TYPE_CHECKING:
    from ..config import GUIConfig
    from ...config import Config


class SettingsSidebar(SidebarBase):
    """Right sidebar with three intuitive categories."""

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        super().__init__(gui_config, parent)

        # Create tabs
        general = GeneralTab(gui_config, config)
        effects = EffectsTab(gui_config, config)
        advanced = AdvancedTab(gui_config, config)

        # Add to sidebar
        self.add_tab(general, "General")
        self.add_tab(effects, "Effects")
        self.add_tab(advanced, "Advanced")

        # Forward their change signals to the sidebar's config_changed signal
        general.config_changed.connect(self.config_changed.emit)
        effects.config_changed.connect(self.config_changed.emit)
        advanced.config_changed.connect(self.config_changed.emit)
