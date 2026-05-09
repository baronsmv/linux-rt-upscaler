from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ....config import VulkanPresentMode

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class AdvancedTab(SettingsTab):

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
            title="General",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Lanczos Resampler ----
        self._add_section("Lanczos Resampler")
        self._blur = self._add_slider(
            "Blur",
            1,
            200,
            max(1, int(self._config.lanczos_blur * 100)),
            scale_factor=100,
            float_slot=self._on_blur,
            baseline=self.baseline_config.lanczos_blur,
            help="Kernel width for the final resampling step (>0.0 - 2.0).\n"
            "Lower values increase sharpness/ringing; higher values smooth the result.\n"
            "Recommended range: 0.8 - 1.2.",
        )
        self._antiring = self._add_slider(
            "Antiring Strength",
            0,
            100,
            int(self._config.lanczos_antiring_strength * 100),
            scale_factor=100,
            float_slot=self._on_antiring,
            baseline=self.baseline_config.lanczos_antiring_strength,
            help="Anti-ringing strength (0.0 - 1.0).\n"
            "Lower values soften the clamp, preserving more detail at the cost of possible ringing.\n"
            "Recommended range: 0.7 - 1.0.",
        )
        self._linear_cb = self._add_cb(
            "Linear Light",
            self._config.lanczos_linear_light,
            self._on_linear_light,
            baseline=self.baseline_config.lanczos_linear_light,
            help=f"Process the image in linear light (sRGB {chr(8594)} linear {chr(8594)} sRGB).\n"
            "Disabling may improve text clarity on some content but colours could lose saturation when downscaling.",
        )
        self._tight_cb = self._add_cb(
            "Tight Antiring",
            self._config.lanczos_tight_antiring,
            self._on_tight_antiring,
            baseline=self.baseline_config.lanczos_tight_antiring,
            help="Use only the central 2x2 neighbourhood for anti-ringing bounds.\n"
            "Keeps thin text and line art sharp. Disable if you see distant ringing artifacts on high-contrast edges.",
        )

        # ---- Vulkan Rendering ----
        self._add_section("Vulkan Rendering")
        self._present_combo = self._add_combo(
            "Present Mode",
            [e.value for e in VulkanPresentMode],
            self._config.vulkan_present_mode,
            self._on_present_mode,
            baseline=self.baseline_config.vulkan_present_mode,
            help="Vulkan presentation mode:\n"
            f"{chr(8226)} fifo - VSync on, lowest power, no tearing\n"
            f"{chr(8226)} mailbox - tear-free, lower latency, higher power\n"
            f"{chr(8226)} immediate - no VSync, lowest latency, may tear",
        )
        self._buffer_pool = self._add_slider(
            "Buffer Pool Size",
            2,
            16,
            self._config.vulkan_buffer_pool_size,
            self._on_buffer_pool,
            baseline=self.baseline_config.vulkan_buffer_pool_size,
            help="Number of pre-allocated staging buffers for partial texture updates.\n"
            "Raise this if you notice stutters when many small regions change rapidly.\n"
            "Recommended range: 2 - 16.",
        )
        self._frame_timeout = self._add_slider(
            "Frame Timeout (ms)",
            1,
            1000,
            max(1, self._config.frame_timeout // 1_000_000),
            self._on_frame_timeout,
            baseline=self.baseline_config.frame_timeout // 1_000_000,
            help="Maximum time (in milliseconds) to wait for the GPU to finish the previous frame.\n"
            "Lower values reduce CPU blocking but may drop frames under heavy load.\n"
            "Recommended range: 17 (1/60 s) - 1000 (1 s).",
        )

        # ---- Tile-Based Processing ----
        self._add_section("Tile-Based Processing")
        self._tile_mode_cb = self._add_cb(
            "Enable Tile Mode",
            self._config.use_tile_processing,
            self._on_tile_mode,
            baseline=self.baseline_config.use_tile_processing,
            help="Divide the frame into tiles and only re-process the ones that have changed.\n"
            "Ideal for mostly static content (e.g. text editors, visual novels).\n"
            "When disabled, the whole frame is upscaled in one pass - better for video or rapid changes.",
        )
        self._damage_cb = self._add_cb(
            "Damage Tracking",
            self._config.use_damage_tracking,
            self._on_damage_tracking,
            baseline=self.baseline_config.use_damage_tracking,
            help="Transfer only the changed regions of the frame to the GPU instead of the entire image.\n"
            "Disable if you suspect missed updates from the compositor causing glitches.",
        )
        self._tile_size = self._add_slider(
            "Tile Size",
            16,
            128,
            self._config.tile_size,
            self._on_tile_size,
            baseline=self.baseline_config.tile_size,
            help="Interior size of each tile in pixels.\n"
            "Smaller tiles track changes more precisely but add CPU overhead.\n"
            "Multiples of 32 work best with GPU workgroups.\n"
            "Recommended range: 32 - 128.",
        )
        self._margin = self._add_slider(
            "Context Margin",
            4,
            24,
            self._config.tile_context_margin,
            self._on_margin,
            baseline=self.baseline_config.tile_context_margin,
            help="Extra border pixels added around each tile to provide context for the neural network.\n"
            "Larger margins improve boundary quality but increase processing.\n"
            "Recommended range: 4 - 24.",
        )
        self._max_layers = self._add_slider(
            "Max Tiles per Frame",
            4,
            32,
            self._config.max_tile_layers,
            self._on_max_layers,
            baseline=self.baseline_config.max_tile_layers,
            help="Maximum number of dirty tiles processed per frame.\n"
            "When exceeded, the pipeline falls back to full-frame processing to avoid excessive GPU dispatches.\n"
            "Recommended range: 4 - 32.",
        )
        self._area_thresh = self._add_slider(
            "Area Threshold %",
            0,
            100,
            int(self._config.area_threshold * 100),
            scale_factor=100,
            float_slot=self._on_area_threshold,
            baseline=self.baseline_config.area_threshold,
            help="Fraction of the window area (in %) that, when dirty, forces a fallback to "
            "full-frame processing.\n"
            "Smaller values fall back earlier, preventing too many tiny tile dispatches.\n"
            "Recommended range: 15% - 50%.",
        )

    def _on_blur(self, val: float):
        self._config.lanczos_blur = max(0.01, val)
        self.config_changed.emit()

    def _on_antiring(self, val: float):
        self._config.lanczos_antiring_strength = val
        self.config_changed.emit()

    def _on_linear_light(self, state: int):
        self._config.lanczos_linear_light = bool(state)
        self.config_changed.emit()

    def _on_tight_antiring(self, state: int):
        self._config.lanczos_tight_antiring = bool(state)
        self.config_changed.emit()

    def _on_present_mode(self, text: str):
        self._config.vulkan_present_mode = str(text)
        self.config_changed.emit()

    def _on_buffer_pool(self, val: int):
        self._config.vulkan_buffer_pool_size = int(val)
        self.config_changed.emit()

    def _on_frame_timeout(self, val: int):
        self._config.frame_timeout = val * 1_000_000
        self.config_changed.emit()

    def _on_tile_mode(self, state: bool):
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking(self, state: bool):
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size(self, val: int):
        self._config.tile_size = int(val)
        self.config_changed.emit()

    def _on_margin(self, val: int):
        self._config.tile_context_margin = int(val)
        self.config_changed.emit()

    def _on_max_layers(self, val: int):
        self._config.max_tile_layers = int(val)
        self.config_changed.emit()

    def _on_area_threshold(self, val: float):
        self._config.area_threshold = max(0.0, min(val, 1.0))
        self.config_changed.emit()
