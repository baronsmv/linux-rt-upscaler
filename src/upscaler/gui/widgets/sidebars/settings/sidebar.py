from __future__ import annotations

from ..utils import SidebarBase, SettingsTab
from ....config import GUIConfig


class UpscalingTab(SettingsTab):
    def __init__(self, gui_config, config, parent=None):
        self.config = config
        super().__init__(gui_config, "Upscaling", parent)

    def _build_content(self):
        # ----- Model -----
        self._add_section_label("Model")
        self._add_combo_row(
            "Model",
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
            self.config.model,
            self._on_model_changed,
        )

        # ----- Geometry -----
        self._add_section_label("Geometry")
        self._add_combo_row(
            "Scaling",
            ["fit", "stretch", "cover"],
            self.config.output_geometry,
            self._on_geometry_changed,
        )

        # ----- Tile Processing -----
        self._add_section_label("Tile Processing")
        self._add_checkbox_row(
            "Tile mode",
            self.config.use_tile_processing,
            self._on_tile_processing_changed,
        )
        self._add_checkbox_row(
            "Damage tracking",
            self.config.use_damage_tracking,
            self._on_damage_tracking_changed,
        )
        self._add_slider_row(
            "Tile size", 16, 128, self.config.tile_size, self._on_tile_size_changed
        )
        self._add_slider_row(
            "Context margin",
            4,
            24,
            self.config.tile_context_margin,
            self._on_tile_context_margin_changed,
        )
        self._add_slider_row(
            "Max tile layers",
            4,
            32,
            self.config.max_tile_layers,
            self._on_max_tile_layers_changed,
        )
        self._add_slider_row(
            "Area threshold %",
            10,
            100,
            int(self.config.area_threshold * 100),
            self._on_area_threshold_changed,
        )

    # ---- Slots (unchanged) ----
    def _on_model_changed(self, text):
        self.config.model = text
        self.config_changed.emit()

    def _on_geometry_changed(self, text):
        self.config.output_geometry = text
        self.config_changed.emit()

    def _on_tile_processing_changed(self, state):
        self.config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking_changed(self, state):
        self.config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size_changed(self, val):
        self.config.tile_size = val
        self.config_changed.emit()

    def _on_tile_context_margin_changed(self, val):
        self.config.tile_context_margin = val
        self.config_changed.emit()

    def _on_max_tile_layers_changed(self, val):
        self.config.max_tile_layers = val
        self.config_changed.emit()

    def _on_area_threshold_changed(self, val):
        self.config.area_threshold = val / 100.0
        self.config_changed.emit()


class EffectsTab(SettingsTab):
    def __init__(self, gui_config, config, parent=None):
        self.config = config
        super().__init__(gui_config, "Effects", parent)

    def _build_content(self):
        # ----- CAS -----
        self._add_section_label("Contrast Adaptive Sharpening")
        self._add_checkbox_row(
            "Enable CAS", self.config.cas_enabled, self._on_cas_enabled
        )
        self._add_slider_row(
            "Strength",
            0,
            100,
            int(self.config.cas_strength * 100),
            self._on_cas_strength,
        )

        # ----- Bloom -----
        self._add_section_label("Bloom (Glow)")
        self._add_checkbox_row(
            "Enable Bloom", self.config.bloom_enabled, self._on_bloom_enabled
        )
        self._add_slider_row(
            "Strength",
            0,
            100,
            int(self.config.bloom_strength * 100),
            self._on_bloom_strength,
        )
        self._add_slider_row(
            "Threshold",
            0,
            100,
            int(self.config.bloom_threshold * 100),
            self._on_bloom_threshold,
        )

        # ----- Vignette -----
        self._add_section_label("Vignette")
        self._add_checkbox_row(
            "Enable Vignette", self.config.vignette_enabled, self._on_vignette_enabled
        )
        self._add_slider_row(
            "Strength",
            0,
            100,
            int(self.config.vignette_strength * 100),
            self._on_vignette_strength,
        )

        # ----- Color Grading -----
        self._add_section_label("Color Grading (3D LUT)")
        self._add_checkbox_row(
            "Enable LUT", self.config.lut_enabled, self._on_lut_enabled
        )
        self._add_combo_row(
            "Preset",
            [
                "identity",
                "warm",
                "cool",
                "split",
                "vivid",
                "pastel",
                "lofi",
                "bleach",
                "film",
                "noir",
                "sepia",
                "cyano",
            ],
            self.config.lut_preset,
            self._on_lut_preset,
        )

        # ----- Film Grain -----
        self._add_section_label("Film Grain")
        self._add_checkbox_row(
            "Enable Grain", self.config.grain_enabled, self._on_grain_enabled
        )
        self._add_slider_row(
            "Strength",
            0,
            100,
            int(self.config.grain_strength * 100),
            self._on_grain_strength,
        )

    # ---- Slots ----
    def _on_cas_enabled(self, state):
        self.config.cas_enabled = bool(state)
        self.config_changed.emit()

    def _on_cas_strength(self, val):
        self.config.cas_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_enabled(self, state):
        self.config.bloom_enabled = bool(state)
        self.config_changed.emit()

    def _on_bloom_strength(self, val):
        self.config.bloom_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_threshold(self, val):
        self.config.bloom_threshold = val / 100.0
        self.config_changed.emit()

    def _on_vignette_enabled(self, state):
        self.config.vignette_enabled = bool(state)
        self.config_changed.emit()

    def _on_vignette_strength(self, val):
        self.config.vignette_strength = val / 100.0
        self.config_changed.emit()

    def _on_lut_enabled(self, state):
        self.config.lut_enabled = bool(state)
        self.config_changed.emit()

    def _on_lut_preset(self, text):
        self.config.lut_preset = text
        self.config_changed.emit()

    def _on_grain_enabled(self, state):
        self.config.grain_enabled = bool(state)
        self.config_changed.emit()

    def _on_grain_strength(self, val):
        self.config.grain_strength = val / 100.0
        self.config_changed.emit()


class SettingsSidebar(SidebarBase):
    """Right sidebar with upscaling & effects tabs."""

    def __init__(self, gui_config: GUIConfig, config, parent=None):
        super().__init__(gui_config, parent)
        self.config = config

        upscaling = UpscalingTab(gui_config, config)
        effects = EffectsTab(gui_config, config)

        self.add_tab(upscaling, "Upscaling")
        self.add_tab(effects, "Effects")

        upscaling.config_changed.connect(self.config_changed)
        effects.config_changed.connect(self.config_changed)
