from __future__ import annotations

from typing import TYPE_CHECKING

from .common import IconSidebarBase
from .tabs import (
    CaptureTab,
    DisplayTab,
    EffectsTab,
    GeneralTab,
    OSDTab,
    AdvancedTab,
    ScreenshotsTab,
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
            (CaptureTab(gui_config, config), "capture", "Capture"),
            (ScreenshotsTab(gui_config, config), "screenshot", "Screenshots"),
            (OSDTab(gui_config, config), "osd", "OSD"),
            (AdvancedTab(gui_config, config), "advanced", "Advanced"),
        ]

        for tab, icon, tooltip in tabs:
            self.add_tab(tab, f"tabs/{icon}", tooltip)
            tab.config_changed.connect(self.config_changed.emit)
