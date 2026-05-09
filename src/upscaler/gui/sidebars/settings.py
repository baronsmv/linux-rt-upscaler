from __future__ import annotations

from typing import TYPE_CHECKING

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

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        super().__init__(gui_config, parent)

        tabs = [
            (GeneralTab(gui_config, config), "general", "General"),
            (DisplayTab(gui_config, config), "display", "Display"),
            (EffectsTab(gui_config, config), "effects", "Effects"),
            (ExtrasTab(gui_config, config), "extras", "Extras"),
            (AdvancedTab(gui_config, config), "advanced", "Advanced"),
        ]

        for tab, icon, tooltip in tabs:
            self.add_tab(tab, f"tabs/{icon}", tooltip)
            tab.config_changed.connect(self.config_changed.emit)
