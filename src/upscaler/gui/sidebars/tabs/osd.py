from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, SliderRow, StyledCheckBox

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class OSDTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "OSD", parent)

    def _build_content(self) -> None:
        self._add_section("On‑Screen Display")
        self._osd_enabled = self._add_cb(
            "Show OSD", self._config.show_osd, self._on_osd_enabled
        )
        self._osd_duration = self._add_slider(
            "Duration (s)",
            1,
            10,
            int(self._config.osd_duration),
            self._on_osd_duration,
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

    def _on_osd_enabled(self, state):
        self._config.show_osd = bool(state)
        self.config_changed.emit()

    def _on_osd_duration(self, val):
        self._config.osd_duration = float(val)
        self.config_changed.emit()
