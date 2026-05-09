from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import SectionLabel, StyledCheckBox, SliderRow, ComboRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class AdvancedTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Advanced", parent)

    def _build_content(self) -> None:
        # ---- Tile Processing ----
        self._add_section("Tile Processing")
        self._tile_cb = self._add_cb(
            "Tile mode", self._config.use_tile_processing, self._on_tile_mode
        )
        self._damage_cb = self._add_cb(
            "Damage tracking",
            self._config.use_damage_tracking,
            self._on_damage_tracking,
        )
        self._tile_size_slider = self._add_slider(
            "Tile size",
            16,
            128,
            self._config.tile_size,
            self._on_tile_size,
            show_val=True,
        )
        self._context_margin_slider = self._add_slider(
            "Context margin",
            4,
            24,
            self._config.tile_context_margin,
            self._on_context_margin,
            show_val=True,
        )
        self._max_layers_slider = self._add_slider(
            "Max tile layers",
            4,
            32,
            self._config.max_tile_layers,
            self._on_max_layers,
            show_val=True,
        )
        self._area_thresh_slider = self._add_slider(
            "Area threshold %",
            10,
            100,
            int(self._config.area_threshold * 100),
            self._on_area_threshold,
            show_val=True,
        )

        # ---- Lanczos Scaler ----
        self._add_section("Lanczos Scaler")
        self._blur_slider = self._add_slider(
            "Blur",
            1,
            200,
            max(1, int(self._config.lanczos_blur * 100)),
            self._on_blur,
            show_val=True,
        )
        self._antiring_slider = self._add_slider(
            "Antiring strength",
            0,
            100,
            int(self._config.lanczos_antiring_strength * 100),
            self._on_antiring,
            show_val=True,
        )
        self._linear_cb = self._add_cb(
            "Linear light", self._config.lanczos_linear_light, self._on_linear_light
        )
        self._tight_cb = self._add_cb(
            "Tight antiring",
            self._config.lanczos_tight_antiring,
            self._on_tight_antiring,
        )

        # ---- Vulkan ----
        self._add_section("Vulkan")
        self._present_combo = ComboRow(
            "Present mode",
            self.gui_config,
            ["fifo", "mailbox", "immediate"],
            self._config.vulkan_present_mode,
        )
        self._present_combo.currentTextChanged.connect(self._on_present_mode)
        self.content_layout.addWidget(self._present_combo)

        self._buffer_pool_slider = self._add_slider(
            "Buffer pool size",
            2,
            16,
            self._config.vulkan_buffer_pool_size,
            self._on_buffer_pool,
            show_val=True,
        )
        # Convert nanoseconds to milliseconds for slider (1ms = 1,000,000 ns)
        timeout_ms = max(1, self._config.frame_timeout // 1_000_000)
        self._frame_timeout_slider = self._add_slider(
            "Frame timeout (ms)",
            1,
            1000,
            timeout_ms,
            self._on_frame_timeout,
            show_val=True,
        )

    # ------------------------------------------------------------------
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

    # ---- Signal handlers ----
    def _on_tile_mode(self, state: int):
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking(self, state: int):
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size(self, val: int):
        self._config.tile_size = val
        self.config_changed.emit()

    def _on_context_margin(self, val: int):
        self._config.tile_context_margin = val
        self.config_changed.emit()

    def _on_max_layers(self, val: int):
        self._config.max_tile_layers = val
        self.config_changed.emit()

    def _on_area_threshold(self, val: int):
        self._config.area_threshold = val / 100.0
        self.config_changed.emit()

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

    def _on_present_mode(self, text: str):
        self._config.vulkan_present_mode = text
        self.config_changed.emit()

    def _on_buffer_pool(self, val: int):
        self._config.vulkan_buffer_pool_size = val
        self.config_changed.emit()

    def _on_frame_timeout(self, val: int):
        self._config.frame_timeout = val * 1_000_000
        self.config_changed.emit()
