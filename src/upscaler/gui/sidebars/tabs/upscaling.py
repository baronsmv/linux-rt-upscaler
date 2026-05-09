from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, StyledCheckBox, SliderRow, ComboRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class UpscalingTab(SettingsTab):
    """
    Tab for configuring the upscaling model, output geometry, and tile
    processing parameters. All changes are written directly to the
    provided ``Config`` instance.
    """

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Upscaling", parent)

    # ------------------------------------------------------------------
    #  Build the UI
    # ------------------------------------------------------------------
    def _build_content(self) -> None:
        # ---- Model ----
        self.content_layout.addWidget(SectionLabel("Model", self.gui_config))
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

        # ---- Geometry ----
        self.content_layout.addWidget(SectionLabel("Geometry", self.gui_config))
        self._geom_combo = ComboRow(
            "Scaling",
            self.gui_config,
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
        )
        self._geom_combo.currentTextChanged.connect(self._on_geometry_changed)
        self.content_layout.addWidget(self._geom_combo)

        # ---- Tile Processing ----
        self.content_layout.addWidget(SectionLabel("Tile Processing", self.gui_config))

        self._tile_mode_cb = StyledCheckBox(
            "Tile mode", self.gui_config, self._config.use_tile_processing
        )
        self._tile_mode_cb.stateChanged.connect(self._on_tile_mode_changed)
        self.content_layout.addWidget(self._tile_mode_cb)

        self._damage_cb = StyledCheckBox(
            "Damage tracking", self.gui_config, self._config.use_damage_tracking
        )
        self._damage_cb.stateChanged.connect(self._on_damage_tracking_changed)
        self.content_layout.addWidget(self._damage_cb)

        self._tile_size_slider = SliderRow(
            "Tile size",
            self.gui_config,
            16,
            128,
            self._config.tile_size,
            show_value=True,
        )
        self._tile_size_slider.valueChanged.connect(self._on_tile_size_changed)
        self.content_layout.addWidget(self._tile_size_slider)

        self._context_margin_slider = SliderRow(
            "Context margin",
            self.gui_config,
            4,
            24,
            self._config.tile_context_margin,
            show_value=True,
        )
        self._context_margin_slider.valueChanged.connect(
            self._on_context_margin_changed
        )
        self.content_layout.addWidget(self._context_margin_slider)

        self._max_layers_slider = SliderRow(
            "Max tile layers",
            self.gui_config,
            4,
            32,
            self._config.max_tile_layers,
            show_value=True,
        )
        self._max_layers_slider.valueChanged.connect(self._on_max_tile_layers_changed)
        self.content_layout.addWidget(self._max_layers_slider)

        self._area_thresh_slider = SliderRow(
            "Area threshold %",
            self.gui_config,
            10,
            100,
            int(self._config.area_threshold * 100),
            show_value=True,
        )
        self._area_thresh_slider.valueChanged.connect(self._on_area_threshold_changed)
        self.content_layout.addWidget(self._area_thresh_slider)

    # ------------------------------------------------------------------
    #  Signal handlers – update Config and emit config_changed
    # ------------------------------------------------------------------
    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_geometry_changed(self, text: str) -> None:
        self._config.output_geometry = text
        self.config_changed.emit()

    def _on_tile_mode_changed(self, state: int) -> None:
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking_changed(self, state: int) -> None:
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size_changed(self, val: int) -> None:
        self._config.tile_size = val
        self.config_changed.emit()

    def _on_context_margin_changed(self, val: int) -> None:
        self._config.tile_context_margin = val
        self.config_changed.emit()

    def _on_max_tile_layers_changed(self, val: int) -> None:
        self._config.max_tile_layers = val
        self.config_changed.emit()

    def _on_area_threshold_changed(self, val: int) -> None:
        self._config.area_threshold = val / 100.0
        self.config_changed.emit()
