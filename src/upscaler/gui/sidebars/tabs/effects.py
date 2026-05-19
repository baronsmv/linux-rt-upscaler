from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ....shaders import BUILT_IN_PRESETS

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class EffectsTab(SettingsTab):
    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        parent=None,
    ) -> None:
        self._config = config
        super().__init__(
            gui_config,
            title="Effects",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Debanding ----
        self._add_section("Debanding")
        self._deband_cb = self._add_cb(
            "Enable Deband",
            self._config.deband_enabled,
            self._on_deband_enabled,
            baseline=self.baseline_config.deband_enabled,
            help="Smooth harsh color banding in gradients before upscaling. "
            "Helps skies, fog and smooth backgrounds.",
        )
        self._deband_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.deband_strength * 100),
            scale_factor=100,
            float_slot=self._on_deband_strength,
            baseline=self.baseline_config.deband_strength,
            help="Debanding intensity (0 = off, 1 = maximum). Low values (0.1-0.3) "
            "are sufficient for most content.",
        )
        self._deband_str.setEnabled(self._config.deband_enabled)

        # ---- CAS ----
        self._add_section("CAS Sharpening")
        self._cas_cb = self._add_cb(
            "Enable CAS",
            self._config.cas_enabled,
            self._on_cas_enabled,
            baseline=self.baseline_config.cas_enabled,
            help="Contrast Adaptive Sharpening: enhances text and line art without "
            "the halos of traditional unsharp masks.",
        )
        self._cas_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.cas_strength * 100),
            scale_factor=100,
            float_slot=self._on_cas_strength,
            baseline=self.baseline_config.cas_strength,
            help="Sharpening amount (0 = none, 1 = max). 0.2-0.5 gives pleasant crispness.",
        )
        self._cas_str.setEnabled(self._config.cas_enabled)

        # ---- Bloom ----
        self._add_section("Bloom (Glow)")
        self._bloom_cb = self._add_cb(
            "Enable Bloom",
            self._config.bloom_enabled,
            self._on_bloom_enabled,
            baseline=self.baseline_config.bloom_enabled,
            help="Soft glow around bright areas, creating a cinematic look.",
        )
        self._bloom_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.bloom_strength * 100),
            scale_factor=100,
            float_slot=self._on_bloom_strength,
            baseline=self.baseline_config.bloom_strength,
            help="Bloom intensity (0 = off, 1 = max). Subtle values (0.02-0.06) "
            "add a gentle, polished look.",
        )
        self._bloom_str.setEnabled(self._config.bloom_enabled)

        self._bloom_thresh = self._add_slider(
            "Threshold",
            0,
            100,
            int(self._config.bloom_threshold * 100),
            scale_factor=100,
            float_slot=self._on_bloom_threshold,
            baseline=self.baseline_config.bloom_threshold,
            help="Brightness cutoff for bloom. Only pixels above this contribute. "
            "Lower values include more of the scene.",
        )
        self._bloom_thresh.setEnabled(self._config.bloom_enabled)

        self._bloom_radius = self._add_slider(
            "Radius",
            1,
            16,
            self._config.bloom_radius,
            self._on_bloom_radius,
            baseline=self.baseline_config.bloom_radius,
            help="Blur radius in pixels. Larger radii spread the glow further.",
        )
        self._bloom_radius.setEnabled(self._config.bloom_enabled)

        # ---- Vignette ----
        self._add_section("Vignette")
        self._vignette_cb = self._add_cb(
            "Enable Vignette",
            self._config.vignette_enabled,
            self._on_vignette_enabled,
            baseline=self.baseline_config.vignette_enabled,
            help="Radial darkening of screen edges, drawing focus to the center.",
        )
        self._vignette_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.vignette_strength * 100),
            scale_factor=100,
            float_slot=self._on_vignette_strength,
            baseline=self.baseline_config.vignette_strength,
            help="Edge darkening intensity (0 = none, 1 = max). Moderate values "
            "(0.3-0.6) give a subtle framing effect.",
        )
        self._vignette_str.setEnabled(self._config.vignette_enabled)

        self._vignette_radius = self._add_slider(
            "Radius",
            0,
            200,
            int(self._config.vignette_radius * 100),
            scale_factor=100,
            float_slot=self._on_vignette_radius,
            baseline=self.baseline_config.vignette_radius,
            help="Distance from center where darkening begins. Higher values keep "
            "the center bright longer.",
        )
        self._vignette_radius.setEnabled(self._config.vignette_enabled)

        self._vignette_falloff = self._add_slider(
            "Falloff",
            10,
            1000,
            int(self._config.vignette_falloff * 100),
            scale_factor=100,
            float_slot=self._on_vignette_falloff,
            baseline=self.baseline_config.vignette_falloff,
            help="Softness of the vignette transition. Low values = gentle, "
            "high values = sharp ring.",
        )
        self._vignette_falloff.setEnabled(self._config.vignette_enabled)

        # ---- Film Grain ----
        self._add_section("Film Grain")
        self._grain_cb = self._add_cb(
            "Enable Grain",
            self._config.grain_enabled,
            self._on_grain_enabled,
            baseline=self.baseline_config.grain_enabled,
            help="Simulated film grain for a photochemical, organic look.",
        )
        self._grain_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.grain_strength * 100),
            scale_factor=100,
            float_slot=self._on_grain_strength,
            baseline=self.baseline_config.grain_strength,
            help="Grain intensity (0 = off, 1 = max). Low values (0.1-0.2) mimic "
            "fine photochemical grain.",
        )
        self._grain_str.setEnabled(self._config.grain_enabled)

        self._grain_size = self._add_slider(
            "Size",
            100,
            1000,
            int(self._config.grain_size * 100),
            scale_factor=100,
            float_slot=self._on_grain_size_changed,
            baseline=self.baseline_config.grain_size,
            help="Apparent particle size of the grain. Larger values produce "
            "coarser, more visible grain.",
        )
        self._grain_size.setEnabled(self._config.grain_enabled)

        # ---- Color Grading (LUT) ----
        self._add_section("Color Grading (3D LUT)")
        self._lut_cb = self._add_cb(
            "Enable LUT",
            self._config.lut_enabled,
            self._on_lut_enabled,
            baseline=self.baseline_config.lut_enabled,
            help="Apply a cinematic color-lookup table for instant film-stock "
            "emulation or color grading.",
        )
        self._lut_combo = self._add_combo(
            "Preset",
            list(BUILT_IN_PRESETS.keys()),
            self._config.lut_preset,
            self._on_lut_preset,
            baseline=self.baseline_config.lut_preset,
            help="Built-in 3D LUT preset. Choose from warm, cool, film, sepia, etc.",
        )
        self._lut_combo.setEnabled(self._config.lut_enabled)

        self._lut_intensity = self._add_slider(
            "Intensity",
            0,
            100,
            int(self._config.lut_intensity * 100),
            scale_factor=100,
            float_slot=self._on_lut_intensity,
            baseline=self.baseline_config.lut_intensity,
            help="Blend between original and graded image (0 = original, 1 = full effect).",
        )
        self._lut_intensity.setEnabled(self._config.lut_enabled)

    def _on_deband_enabled(self, state: int):
        enabled = bool(state)
        self._config.deband_enabled = enabled
        self._deband_str.setEnabled(enabled)
        self.config_changed.emit()

    def _on_cas_enabled(self, state: int):
        enabled = bool(state)
        self._config.cas_enabled = enabled
        self._cas_str.setEnabled(enabled)
        self.config_changed.emit()

    def _on_bloom_enabled(self, state: int):
        enabled = bool(state)
        self._config.bloom_enabled = enabled
        self._bloom_str.setEnabled(enabled)
        self._bloom_thresh.setEnabled(enabled)
        self._bloom_radius.setEnabled(enabled)
        self.config_changed.emit()

    def _on_vignette_enabled(self, state: int):
        enabled = bool(state)
        self._config.vignette_enabled = enabled
        self._vignette_str.setEnabled(enabled)
        self._vignette_radius.setEnabled(enabled)
        self._vignette_falloff.setEnabled(enabled)
        self.config_changed.emit()

    def _on_lut_enabled(self, state: int):
        enabled = bool(state)
        self._config.lut_enabled = enabled
        self._lut_combo.setEnabled(enabled)
        self._lut_intensity.setEnabled(enabled)
        self.config_changed.emit()

    def _on_grain_enabled(self, state: int):
        enabled = bool(state)
        self._config.grain_enabled = enabled
        self._grain_str.setEnabled(enabled)
        self._grain_size.setEnabled(enabled)
        self.config_changed.emit()

    def _on_deband_strength(self, value: float):
        self._config.deband_strength = value
        self.config_changed.emit()

    def _on_cas_strength(self, value: float):
        self._config.cas_strength = value
        self.config_changed.emit()

    def _on_bloom_strength(self, value: float):
        self._config.bloom_strength = value
        self.config_changed.emit()

    def _on_bloom_threshold(self, value: float):
        self._config.bloom_threshold = value
        self.config_changed.emit()

    def _on_bloom_radius(self, value: int):
        self._config.bloom_radius = value
        self.config_changed.emit()

    def _on_vignette_strength(self, value: float):
        self._config.vignette_strength = value
        self.config_changed.emit()

    def _on_vignette_radius(self, value: float):
        self._config.vignette_radius = value
        self.config_changed.emit()

    def _on_vignette_falloff(self, value: float):
        self._config.vignette_falloff = value
        self.config_changed.emit()

    def _on_lut_preset(self, text: str):
        self._config.lut_preset = text
        self.config_changed.emit()

    def _on_lut_intensity(self, value: float):
        self._config.lut_intensity = value
        self.config_changed.emit()

    def _on_grain_strength(self, value: float):
        self._config.grain_strength = value
        self.config_changed.emit()

    def _on_grain_size_changed(self, value: float):
        self._config.grain_size = value
        self.config_changed.emit()
