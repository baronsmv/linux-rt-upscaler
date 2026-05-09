from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, SliderRow, StyledCheckBox

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class ScalerTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Scaler", parent)

    def _build_content(self) -> None:
        self._add_section("Lanczos Resampler")
        self._blur = self._add_slider(
            "Blur",
            1,
            200,
            max(1, int(self._config.lanczos_blur * 100)),
            self._on_blur,
            show_val=True,
        )
        self._antiring = self._add_slider(
            "Antiring Strength",
            0,
            100,
            int(self._config.lanczos_antiring_strength * 100),
            self._on_antiring,
            show_val=True,
        )
        self._linear_cb = self._add_cb(
            "Linear Light", self._config.lanczos_linear_light, self._on_linear_light
        )
        self._tight_cb = self._add_cb(
            "Tight Antiring",
            self._config.lanczos_tight_antiring,
            self._on_tight_antiring,
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

    def _on_blur(self, val: int):
        self._config.lanczos_blur = max(0.01, val / 100.0)
        self.config_changed.emit()

    def _on_antiring(self, val: int):
        self._config.lanczos_antiring_strength = val / 100.0
        self.config_changed.emit()

    def _on_linear_light(self, state: int):
        self._config.lanczos_linear_light = bool(state)
        self.config_changed.emit()

    def _on_tight_antiring(self, state: int):
        self._config.lanczos_tight_antiring = bool(state)
        self.config_changed.emit()
