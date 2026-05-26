from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class AdvancedTab(SettingsTab):

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
            title="Advanced",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Vulkan Rendering ----
        self._add_section("Vulkan Rendering")
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
            "When disabled, the whole frame is upscaled in one pass: better for video or rapid changes.",
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

        # ---- Timing ----
        self._add_section("Timing")
        self._add_slider(
            "Daemon Poll (s)",
            1,
            100,
            int(self._config.daemon_poll_interval * 10),
            float_slot=self._on_daemon_poll_interval_changed,
            scale_factor=10,
            baseline=self.baseline_config.daemon_poll_interval,
            help="How often the daemon scans for matching windows.",
        )
        self._add_slider(
            "Focus Poll (s)",
            1,
            1000,
            int(self._config.focus_poll_interval * 100),
            float_slot=self._on_focus_poll_interval_changed,
            scale_factor=100,
            baseline=self.baseline_config.focus_poll_interval,
            help="How often the focus monitor checks for active window changes.",
        )
        self._add_slider(
            "Pipeline Idle (s)",
            1,
            1000,
            int(self._config.pipeline_poll_interval * 100),
            float_slot=self._on_pipeline_poll_interval_changed,
            scale_factor=100,
            baseline=self.baseline_config.pipeline_poll_interval,
            help="How often the pipeline checks its internal state when idle.",
        )

        # ---- Error Recovery ----
        self._add_section("Error Recovery")
        self._add_slider(
            "Max Capture Failures",
            1,
            100,
            self._config.max_capture_failures,
            slot=self._on_max_capture_failures_changed,
            scale_factor=1,
            baseline=self.baseline_config.max_capture_failures,
            help="Consecutive frame-grab failures before the pipeline stops.",
        )
        self._add_slider(
            "Capture Failure Delay (s)",
            0,
            500,
            int(self._config.capture_failure_delay * 100),
            float_slot=self._on_capture_failure_delay_changed,
            scale_factor=100,
            baseline=self.baseline_config.capture_failure_delay,
            help="Pause after a capture failure before retrying.",
        )
        self._add_slider(
            "Swapchain Debounce (s)",
            0,
            100,
            int(self._config.swapchain_debounce * 10),
            float_slot=self._on_swapchain_recreate_debounce_changed,
            scale_factor=10,
            baseline=self.baseline_config.swapchain_debounce,
            help="Minimum time between two Vulkan swapchain recreations.",
        )

    def _on_buffer_pool(self, value: int):
        self._config.vulkan_buffer_pool_size = value
        self.config_changed.emit()

    def _on_frame_timeout(self, value: int):
        self._config.frame_timeout = value * 1_000_000
        self.config_changed.emit()

    def _on_tile_mode(self, state: int):
        self._config.use_tile_processing = bool(state)
        self.config_changed.emit()

    def _on_damage_tracking(self, state: int):
        self._config.use_damage_tracking = bool(state)
        self.config_changed.emit()

    def _on_tile_size(self, value: int):
        self._config.tile_size = value
        self.config_changed.emit()

    def _on_margin(self, value: int):
        self._config.tile_context_margin = value
        self.config_changed.emit()

    def _on_max_layers(self, value: int):
        self._config.max_tile_layers = value
        self.config_changed.emit()

    def _on_area_threshold(self, value: float):
        self._config.area_threshold = value
        self.config_changed.emit()

    def _on_daemon_poll_interval_changed(self, value: float):
        self._config.daemon_poll_interval = value
        self.config_changed.emit()

    def _on_focus_poll_interval_changed(self, value: float):
        self._config.focus_poll_interval = value
        self.config_changed.emit()

    def _on_pipeline_poll_interval_changed(self, value: float):
        self._config.pipeline_poll_interval = value
        self.config_changed.emit()

    def _on_max_capture_failures_changed(self, value: int):
        self._config.max_capture_failures = value
        self.config_changed.emit()

    def _on_capture_failure_delay_changed(self, value: float):
        self._config.capture_failure_delay = value
        self.config_changed.emit()

    def _on_swapchain_recreate_debounce_changed(self, value: float):
        self._config.swapchain_debounce = value
        self.config_changed.emit()
