from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, StyledCheckBox, SliderRow, ComboRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class EffectsTab(SettingsTab):
    """
    Tab for toggling and adjusting post‑processing effects. All changes
    are written directly to the ``Config`` object.
    """

    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Effects", parent)

    # ------------------------------------------------------------------
    #  Build the UI
    # ------------------------------------------------------------------
    def _build_content(self) -> None:
        # ---- CAS ----
        self.content_layout.addWidget(
            SectionLabel("Contrast Adaptive Sharpening", self.gui_config)
        )
        self._cas_cb = StyledCheckBox(
            "Enable CAS", self.gui_config, self._config.cas_enabled
        )
        self._cas_cb.stateChanged.connect(self._on_cas_enabled)
        self.content_layout.addWidget(self._cas_cb)

        self._cas_slider = SliderRow(
            "Strength",
            self.gui_config,
            0,
            100,
            int(self._config.cas_strength * 100),
            show_value=True,
        )
        self._cas_slider.valueChanged.connect(self._on_cas_strength)
        self.content_layout.addWidget(self._cas_slider)

        # ---- Bloom ----
        self.content_layout.addWidget(SectionLabel("Bloom (Glow)", self.gui_config))
        self._bloom_cb = StyledCheckBox(
            "Enable Bloom", self.gui_config, self._config.bloom_enabled
        )
        self._bloom_cb.stateChanged.connect(self._on_bloom_enabled)
        self.content_layout.addWidget(self._bloom_cb)

        self._bloom_strength_slider = SliderRow(
            "Strength",
            self.gui_config,
            0,
            100,
            int(self._config.bloom_strength * 100),
            show_value=True,
        )
        self._bloom_strength_slider.valueChanged.connect(self._on_bloom_strength)
        self.content_layout.addWidget(self._bloom_strength_slider)

        self._bloom_thresh_slider = SliderRow(
            "Threshold",
            self.gui_config,
            0,
            100,
            int(self._config.bloom_threshold * 100),
            show_value=True,
        )
        self._bloom_thresh_slider.valueChanged.connect(self._on_bloom_threshold)
        self.content_layout.addWidget(self._bloom_thresh_slider)

        # ---- Vignette ----
        self.content_layout.addWidget(SectionLabel("Vignette", self.gui_config))
        self._vignette_cb = StyledCheckBox(
            "Enable Vignette", self.gui_config, self._config.vignette_enabled
        )
        self._vignette_cb.stateChanged.connect(self._on_vignette_enabled)
        self.content_layout.addWidget(self._vignette_cb)

        self._vignette_slider = SliderRow(
            "Strength",
            self.gui_config,
            0,
            100,
            int(self._config.vignette_strength * 100),
            show_value=True,
        )
        self._vignette_slider.valueChanged.connect(self._on_vignette_strength)
        self.content_layout.addWidget(self._vignette_slider)

        # ---- Color Grading (LUT) ----
        self.content_layout.addWidget(
            SectionLabel("Color Grading (3D LUT)", self.gui_config)
        )
        self._lut_cb = StyledCheckBox(
            "Enable LUT", self.gui_config, self._config.lut_enabled
        )
        self._lut_cb.stateChanged.connect(self._on_lut_enabled)
        self.content_layout.addWidget(self._lut_cb)

        self._lut_combo = ComboRow(
            "Preset",
            self.gui_config,
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
        )
        self._lut_combo.currentTextChanged.connect(self._on_lut_preset)
        self.content_layout.addWidget(self._lut_combo)

        # ---- Film Grain ----
        self.content_layout.addWidget(SectionLabel("Film Grain", self.gui_config))
        self._grain_cb = StyledCheckBox(
            "Enable Grain", self.gui_config, self._config.grain_enabled
        )
        self._grain_cb.stateChanged.connect(self._on_grain_enabled)
        self.content_layout.addWidget(self._grain_cb)

        self._grain_slider = SliderRow(
            "Strength",
            self.gui_config,
            0,
            100,
            int(self._config.grain_strength * 100),
            show_value=True,
        )
        self._grain_slider.valueChanged.connect(self._on_grain_strength)
        self.content_layout.addWidget(self._grain_slider)

    # ------------------------------------------------------------------
    #  Signal handlers
    # ------------------------------------------------------------------
    def _on_cas_enabled(self, state: int) -> None:
        self._config.cas_enabled = bool(state)
        self.config_changed.emit()

    def _on_cas_strength(self, val: int) -> None:
        self._config.cas_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_enabled(self, state: int) -> None:
        self._config.bloom_enabled = bool(state)
        self.config_changed.emit()

    def _on_bloom_strength(self, val: int) -> None:
        self._config.bloom_strength = val / 100.0
        self.config_changed.emit()

    def _on_bloom_threshold(self, val: int) -> None:
        self._config.bloom_threshold = val / 100.0
        self.config_changed.emit()

    def _on_vignette_enabled(self, state: int) -> None:
        self._config.vignette_enabled = bool(state)
        self.config_changed.emit()

    def _on_vignette_strength(self, val: int) -> None:
        self._config.vignette_strength = val / 100.0
        self.config_changed.emit()

    def _on_lut_enabled(self, state: int) -> None:
        self._config.lut_enabled = bool(state)
        self.config_changed.emit()

    def _on_lut_preset(self, text: str) -> None:
        self._config.lut_preset = text
        self.config_changed.emit()

    def _on_grain_enabled(self, state: int) -> None:
        self._config.grain_enabled = bool(state)
        self.config_changed.emit()

    def _on_grain_strength(self, val: int) -> None:
        self._config.grain_strength = val / 100.0
        self.config_changed.emit()
