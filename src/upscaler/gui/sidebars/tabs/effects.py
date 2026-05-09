from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class EffectsTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Effects", parent)

    def _build_content(self) -> None:
        # ---- Debanding (pre‑processing) ----
        self._add_section("Debanding")
        self._deband_cb = self._add_cb(
            "Enable Deband", self._config.deband_enabled, self._on_deband_enabled
        )
        self._deband_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.deband_strength * 100),
            self._on_deband_strength,
            show_val=True,
        )

        # ---- CAS ----
        self._add_section("CAS Sharpening")
        self._cas_cb = self._add_cb(
            "Enable CAS", self._config.cas_enabled, self._on_cas_enabled
        )
        self._cas_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.cas_strength * 100),
            self._on_cas_strength,
            show_val=True,
        )

        # ---- Bloom ----
        self._add_section("Bloom (Glow)")
        self._bloom_cb = self._add_cb(
            "Enable Bloom", self._config.bloom_enabled, self._on_bloom_enabled
        )
        self._bloom_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.bloom_strength * 100),
            self._on_bloom_strength,
            show_val=True,
        )
        self._bloom_thresh = self._add_slider(
            "Threshold",
            0,
            100,
            int(self._config.bloom_threshold * 100),
            self._on_bloom_threshold,
            show_val=True,
        )

        # ---- Vignette ----
        self._add_section("Vignette")
        self._vignette_cb = self._add_cb(
            "Enable Vignette", self._config.vignette_enabled, self._on_vignette_enabled
        )
        self._vignette_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.vignette_strength * 100),
            self._on_vignette_strength,
            show_val=True,
        )

        # ---- Color Grading (LUT) ----
        self._add_section("Color Grading (3D LUT)")
        self._lut_cb = self._add_cb(
            "Enable LUT", self._config.lut_enabled, self._on_lut_enabled
        )
        self._lut_combo = self._add_combo(
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
            self._config.lut_preset,
            self._on_lut_preset,
        )

        # ---- Film Grain ----
        self._add_section("Film Grain")
        self._grain_cb = self._add_cb(
            "Enable Grain", self._config.grain_enabled, self._on_grain_enabled
        )
        self._grain_str = self._add_slider(
            "Strength",
            0,
            100,
            int(self._config.grain_strength * 100),
            self._on_grain_strength,
            show_val=True,
        )

    def _on_deband_enabled(self, state):
        self._config.deband_enabled = bool(state)
        self.config_changed.emit()

    def _on_deband_strength(self, val):
        self._config.deband_strength = val / 100.0
        self.config_changed.emit()

    def _on_cas_enabled(self, state):
        self._config.cas_enabled = bool(state)
        self.config_changed.emit()

    def _on_cas_strength(self, val):
        self._config.cas_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_enabled(self, state):
        self._config.bloom_enabled = bool(state)
        self.config_changed.emit()

    def _on_bloom_strength(self, val):
        self._config.bloom_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_threshold(self, val):
        self._config.bloom_threshold = val / 100.0
        self.config_changed.emit()

    def _on_vignette_enabled(self, state):
        self._config.vignette_enabled = bool(state)
        self.config_changed.emit()

    def _on_vignette_strength(self, val):
        self._config.vignette_strength = val / 100.0
        self.config_changed.emit()

    def _on_lut_enabled(self, state):
        self._config.lut_enabled = bool(state)
        self.config_changed.emit()

    def _on_lut_preset(self, text):
        self._config.lut_preset = text
        self.config_changed.emit()

    def _on_grain_enabled(self, state):
        self._config.grain_enabled = bool(state)
        self.config_changed.emit()

    def _on_grain_strength(self, val):
        self._config.grain_strength = val / 100.0
        self.config_changed.emit()
