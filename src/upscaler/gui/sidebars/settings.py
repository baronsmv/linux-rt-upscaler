from __future__ import annotations

from typing import TYPE_CHECKING

from .common import SidebarBase
from .tabs import EffectsTab, UpscalingTab

if TYPE_CHECKING:
    from ..config import GUIConfig
    from ...config import Config


class SettingsSidebar(SidebarBase):
    """Right sidebar containing Upscaling and Effects tabs."""

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        super().__init__(gui_config, parent)

        # Create tabs
        upscaling = UpscalingTab(gui_config, config)
        effects = EffectsTab(gui_config, config)

        # Add to sidebar
        self.add_tab(upscaling, "Upscaling")
        self.add_tab(effects, "Effects")

        # Forward their change signals to the sidebar's config_changed signal
        upscaling.config_changed.connect(self.config_changed.emit)
        effects.config_changed.connect(self.config_changed.emit)
