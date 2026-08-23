from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....shaders import LUT_PRESETS

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class EffectsTab(SettingsTab):
    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._config = config
        super().__init__(
            gui_config,
            title=self.tr("Effects", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Debanding ----
        self._add_section(self.tr("Debanding", "Settings section"))
        self._deband_cb = self._add_cb(
            self.tr("Enable Deband", "Label of setting (must be short)"),
            self._config.deband_enabled,
            self._on_deband_enabled,
            baseline=self.baseline_config.deband_enabled,
            help=self.tr(
                "Smooth harsh color banding in gradients before upscaling. "
                "Helps skies, fog and smooth backgrounds.",
                "Description of a setting (tooltip)",
            ),
        )
        self._deband_str = self._add_slider(
            self.tr("Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.deband_strength * 100),
            scale_factor=100,
            float_slot=self._on_deband_strength,
            baseline=self.baseline_config.deband_strength,
            help=self.tr(
                "Debanding intensity (0 = off, 1 = maximum). Low values (0.1-0.3) "
                "are sufficient for most content.",
                "Description of a setting (tooltip)",
            ),
        )
        self._deband_str.setEnabled(self._config.deband_enabled)

        # ---- CAS ----
        self._add_section(self.tr("CAS Sharpening", "Settings section"))
        self._cas_cb = self._add_cb(
            self.tr("Enable CAS", "Label of setting (must be short)"),
            self._config.cas_enabled,
            self._on_cas_enabled,
            baseline=self.baseline_config.cas_enabled,
            help=self.tr(
                "Contrast Adaptive Sharpening: enhances text and line art without "
                "the halos of traditional unsharp masks.",
                "Description of a setting (tooltip)",
            ),
        )
        self._cas_str = self._add_slider(
            self.tr("Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.cas_strength * 100),
            scale_factor=100,
            float_slot=self._on_cas_strength,
            baseline=self.baseline_config.cas_strength,
            help=self.tr(
                "Sharpening amount (0 = none, 1 = max). 0.2-0.5 gives pleasant crispness.",
                "Description of a setting (tooltip)",
            ),
        )
        self._cas_str.setEnabled(self._config.cas_enabled)

        # ---- Bloom ----
        self._add_section(self.tr("Bloom (Glow)", "Settings section"))
        self._bloom_cb = self._add_cb(
            self.tr("Enable Bloom", "Label of setting (must be short)"),
            self._config.bloom_enabled,
            self._on_bloom_enabled,
            baseline=self.baseline_config.bloom_enabled,
            help=self.tr(
                "Soft glow around bright areas, creating a cinematic look.",
                "Description of a setting (tooltip)",
            ),
        )
        self._bloom_str = self._add_slider(
            self.tr("Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.bloom_strength * 100),
            scale_factor=100,
            float_slot=self._on_bloom_strength,
            baseline=self.baseline_config.bloom_strength,
            help=self.tr(
                "Bloom intensity (0 = off, 1 = max). Subtle values (0.02-0.06) "
                "add a gentle, polished look.",
                "Description of a setting (tooltip)",
            ),
        )
        self._bloom_str.setEnabled(self._config.bloom_enabled)

        self._bloom_thresh = self._add_slider(
            self.tr("Threshold", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.bloom_threshold * 100),
            scale_factor=100,
            float_slot=self._on_bloom_threshold,
            baseline=self.baseline_config.bloom_threshold,
            help=self.tr(
                "Brightness cutoff for bloom. Only pixels above this contribute. "
                "Lower values include more of the scene.",
                "Description of a setting (tooltip)",
            ),
        )
        self._bloom_thresh.setEnabled(self._config.bloom_enabled)

        self._bloom_radius = self._add_slider(
            self.tr("Radius", "Label of setting (must be short)"),
            1,
            16,
            self._config.bloom_radius,
            self._on_bloom_radius,
            baseline=self.baseline_config.bloom_radius,
            help=self.tr(
                "Blur radius in pixels. Larger radii spread the glow further.",
                "Description of a setting (tooltip)",
            ),
        )
        self._bloom_radius.setEnabled(self._config.bloom_enabled)

        # ---- Vignette ----
        self._add_section(self.tr("Vignette", "Settings section"))
        self._vignette_cb = self._add_cb(
            self.tr("Enable Vignette", "Label of setting (must be short)"),
            self._config.vignette_enabled,
            self._on_vignette_enabled,
            baseline=self.baseline_config.vignette_enabled,
            help=self.tr(
                "Radial darkening of screen edges, drawing focus to the center.",
                "Description of a setting (tooltip)",
            ),
        )
        self._vignette_str = self._add_slider(
            self.tr("Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.vignette_strength * 100),
            scale_factor=100,
            float_slot=self._on_vignette_strength,
            baseline=self.baseline_config.vignette_strength,
            help=self.tr(
                "Edge darkening intensity (0 = none, 1 = max). Moderate values "
                "(0.3-0.6) give a subtle framing effect.",
                "Description of a setting (tooltip)",
            ),
        )
        self._vignette_str.setEnabled(self._config.vignette_enabled)

        self._vignette_radius = self._add_slider(
            self.tr("Radius", "Label of setting (must be short)"),
            0,
            200,
            int(self._config.vignette_radius * 100),
            scale_factor=100,
            float_slot=self._on_vignette_radius,
            baseline=self.baseline_config.vignette_radius,
            help=self.tr(
                "Distance from center where darkening begins. Higher values keep "
                "the center bright longer.",
                "Description of a setting (tooltip)",
            ),
        )
        self._vignette_radius.setEnabled(self._config.vignette_enabled)

        self._vignette_falloff = self._add_slider(
            self.tr("Falloff", "Label of setting (must be short)"),
            10,
            1000,
            int(self._config.vignette_falloff * 100),
            scale_factor=100,
            float_slot=self._on_vignette_falloff,
            baseline=self.baseline_config.vignette_falloff,
            help=self.tr(
                "Softness of the vignette transition. Low values = gentle, "
                "high values = sharp ring.",
                "Description of a setting (tooltip)",
            ),
        )
        self._vignette_falloff.setEnabled(self._config.vignette_enabled)

        # ---- Film Grain ----
        self._add_section(self.tr("Film Grain", "Settings section"))
        self._grain_cb = self._add_cb(
            self.tr("Enable Grain", "Label of setting (must be short)"),
            self._config.grain_enabled,
            self._on_grain_enabled,
            baseline=self.baseline_config.grain_enabled,
            help=self.tr(
                "Simulated film grain for a photochemical, organic look.",
                "Description of a setting (tooltip)",
            ),
        )
        self._grain_str = self._add_slider(
            self.tr("Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.grain_strength * 100),
            scale_factor=100,
            float_slot=self._on_grain_strength,
            baseline=self.baseline_config.grain_strength,
            help=self.tr(
                "Grain intensity (0 = off, 1 = max). Low values (0.1-0.2) mimic "
                "fine photochemical grain.",
                "Description of a setting (tooltip)",
            ),
        )
        self._grain_str.setEnabled(self._config.grain_enabled)

        self._grain_size = self._add_slider(
            self.tr("Size", "Label of setting (must be short)"),
            100,
            1000,
            int(self._config.grain_size * 100),
            scale_factor=100,
            float_slot=self._on_grain_size_changed,
            baseline=self.baseline_config.grain_size,
            help=self.tr(
                "Apparent particle size of the grain. Larger values produce "
                "coarser, more visible grain.",
                "Description of a setting (tooltip)",
            ),
        )
        self._grain_size.setEnabled(self._config.grain_enabled)

        # ---- Color Grading (LUT) ----
        self._add_section(self.tr("Color Grading (3D LUT)", "Settings section"))
        self._lut_cb = self._add_cb(
            self.tr("Enable LUT", "Label of setting (must be short)"),
            self._config.lut_enabled,
            self._on_lut_enabled,
            baseline=self.baseline_config.lut_enabled,
            help=self.tr(
                "Apply a cinematic color-lookup table for instant film-stock "
                "emulation or color grading.",
                "Description of a setting (tooltip)",
            ),
        )
        self._lut_combo = self._add_combo(
            self.tr("Preset", "Label of setting (must be short)"),
            list(LUT_PRESETS.keys()),
            self._config.lut_preset,
            self._on_lut_preset,
            baseline=self.baseline_config.lut_preset,
            help=self.tr(
                "Built-in 3D LUT preset. Choose from warm, cool, film, sepia, etc.",
                "Description of a setting (tooltip)",
            ),
        )
        self._lut_combo.setEnabled(self._config.lut_enabled)

        self._lut_intensity = self._add_slider(
            self.tr("Intensity", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.lut_intensity * 100),
            scale_factor=100,
            float_slot=self._on_lut_intensity,
            baseline=self.baseline_config.lut_intensity,
            help=self.tr(
                "Blend between original and graded image (0 = original, 1 = full effect).",
                "Description of a setting (tooltip)",
            ),
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
