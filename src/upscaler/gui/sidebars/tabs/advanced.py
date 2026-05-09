from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ....config import VulkanPresentMode

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class AdvancedTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Advanced", parent)

    def _build_content(self) -> None:
        # ---- Lanczos Resampler ----
        self._add_section("Lanczos Resampler")
        self._blur = self._add_slider(
            "Blur",
            1,
            200,
            max(1, int(self._config.lanczos_blur * 100)),
            self._on_blur,
        )
        self._antiring = self._add_slider(
            "Antiring Strength",
            0,
            100,
            int(self._config.lanczos_antiring_strength * 100),
            self._on_antiring,
        )
        self._linear_cb = self._add_cb(
            "Linear Light", self._config.lanczos_linear_light, self._on_linear_light
        )
        self._tight_cb = self._add_cb(
            "Tight Antiring",
            self._config.lanczos_tight_antiring,
            self._on_tight_antiring,
        )

        # ---- Vulkan Rendering ----
        self._add_section("Vulkan Rendering")
        self._present_combo = self._add_combo(
            "Present Mode",
            [e.value for e in VulkanPresentMode],
            self._config.vulkan_present_mode,
            self._on_present_mode,
        )
        self._buffer_pool = self._add_slider(
            "Buffer Pool Size",
            2,
            16,
            self._config.vulkan_buffer_pool_size,
            self._on_buffer_pool,
        )
        self._frame_timeout = self._add_slider(
            "Frame Timeout (ms)",
            1,
            1000,
            max(1, self._config.frame_timeout // 1_000_000),
            self._on_frame_timeout,
        )

        # ---- Tile‑Based Processing ----
        self._add_section("Tile‑Based Processing")
        self._tile_mode_cb = self._add_cb(
            "Enable Tile Mode", self._config.use_tile_processing, self._on_tile_mode
        )
        self._damage_cb = self._add_cb(
            "Damage Tracking",
            self._config.use_damage_tracking,
            self._on_damage_tracking,
        )
        self._tile_size = self._add_slider(
            "Tile Size",
            16,
            128,
            self._config.tile_size,
            self._on_tile_size,
        )
        self._margin = self._add_slider(
            "Context Margin",
            4,
            24,
            self._config.tile_context_margin,
            self._on_margin,
        )
        self._max_layers = self._add_slider(
            "Max Tiles per Frame",
            4,
            32,
            self._config.max_tile_layers,
            self._on_max_layers,
        )
        self._area_thresh = self._add_slider(
            "Area Threshold %",
            10,
            100,
            int(self._config.area_threshold * 100),
            self._on_area_threshold,
        )

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

    def _on_present_mode(self, text):
        self._config.vulkan_present_mode = text
        self.config_changed.emit()

    def _on_buffer_pool(self, val):
        self._config.vulkan_buffer_pool_size = val
        self.config_changed.emit()

    def _on_frame_timeout(self, val):
        self._config.frame_timeout = val * 1_000_000
        self.config_changed.emit()

    def _on_tile_mode(self, state):
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking(self, state):
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size(self, val):
        self._config.tile_size = val
        self.config_changed.emit()

    def _on_margin(self, val):
        self._config.tile_context_margin = val
        self.config_changed.emit()

    def _on_max_layers(self, val):
        self._config.max_tile_layers = val
        self.config_changed.emit()

    def _on_area_threshold(self, val):
        self._config.area_threshold = val / 100.0
        self.config_changed.emit()
