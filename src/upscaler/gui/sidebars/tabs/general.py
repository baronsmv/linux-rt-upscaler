from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import CheckBox, ComboRow, SectionLabel

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class GeneralTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "General", parent)

    def _build_content(self) -> None:
        # ---- Model & double upscale ----
        self.content_layout.addWidget(SectionLabel("Upscaling Model", self.gui_config))
        self._model_combo = ComboRow(
            "Model",
            self.gui_config,
            [
                "fast",
                "faster",
                "veryfast",
                "4x32",
                "4x24",
                "4x16",
                "4x12",
                "3x12",
                "8x32",
            ],
            self._config.model,
        )
        self._model_combo.currentTextChanged.connect(self._on_model_changed)
        self.content_layout.addWidget(self._model_combo)

        self._double_cb = CheckBox(
            "Double Upscale (4x)", self.gui_config, self._config.double_upscale
        )
        self._double_cb.stateChanged.connect(self._on_double_changed)
        self.content_layout.addWidget(self._double_cb)

        # ---- Output Geometry ----
        self.content_layout.addWidget(SectionLabel("Output Geometry", self.gui_config))
        self._geom_combo = ComboRow(
            "Scaling mode",
            self.gui_config,
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
        )
        self._geom_combo.currentTextChanged.connect(self._on_geometry_changed)
        self.content_layout.addWidget(self._geom_combo)

    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_double_changed(self, state: int) -> None:
        self._config.double_upscale = bool(state)
        self.config_changed.emit()

    def _on_geometry_changed(self, text: str) -> None:
        self._config.output_geometry = text
        self.config_changed.emit()
