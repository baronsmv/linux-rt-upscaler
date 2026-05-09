from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, SliderRow, StyledCheckBox

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class TilesTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Tiles", parent)

    def _build_content(self) -> None:
        self._add_section("Tile‑Based Processing")
        self._tile_mode_cb = self._add_cb(
            "Enable Tile Mode", self._config.use_tile_processing, self._on_tile_mode
        )
        self._damage_cb = self._add_cb(
            "Damage Tracking",
            self._config.use_damage_tracking,
            self._on_damage_tracking,
        )
        self._tile_size = self._add_slider(
            "Tile Size",
            16,
            128,
            self._config.tile_size,
            self._on_tile_size,
            show_val=True,
        )
        self._margin = self._add_slider(
            "Context Margin",
            4,
            24,
            self._config.tile_context_margin,
            self._on_margin,
            show_val=True,
        )
        self._max_layers = self._add_slider(
            "Max Tiles per Frame",
            4,
            32,
            self._config.max_tile_layers,
            self._on_max_layers,
            show_val=True,
        )
        self._area_thresh = self._add_slider(
            "Area Threshold %",
            10,
            100,
            int(self._config.area_threshold * 100),
            self._on_area_threshold,
            show_val=True,
        )

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

    def _add_cb(self, label: str, checked: bool, slot) -> StyledCheckBox:
        cb = StyledCheckBox(label, self.gui_config, checked)
        cb.stateChanged.connect(slot)
        self.content_layout.addWidget(cb)
        return cb

    def _add_slider(
        self,
        label: str,
        min_val: int,
        max_val: int,
        value: int,
        slot,
        show_val: bool = False,
    ) -> SliderRow:
        slider = SliderRow(
            label, self.gui_config, min_val, max_val, value, show_value=show_val
        )
        slider.valueChanged.connect(slot)
        self.content_layout.addWidget(slider)
        return slider

    def _on_tile_mode(self, state):
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking(self, state):
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size(self, val):
        self._config.tile_size = val
        self.config_changed.emit()

    def _on_margin(self, val):
        self._config.tile_context_margin = val
        self.config_changed.emit()

    def _on_max_layers(self, val):
        self._config.max_tile_layers = val
        self.config_changed.emit()

    def _on_area_threshold(self, val):
        self._config.area_threshold = val / 100.0
        self.config_changed.emit()
