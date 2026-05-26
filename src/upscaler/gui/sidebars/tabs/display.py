from __future__ import annotations

import re
from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....config import VulkanPresentMode
from ....utils import list_monitors
from ....vulkan import get_discovered_devices

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


def _short_device_name(raw_name: str) -> str:
    """Return a compact version of a Vulkan device name."""
    cleaned = re.sub(r"\s*\([^)]+\)$", "", raw_name).strip()
    return cleaned or raw_name


class DisplayTab(SettingsTab):
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
            title="Display",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Devices ----
        self._add_section("Devices")
        self._monitor_combo = self._add_combo(
            "Monitor",
            list_monitors(),
            self._config.monitor,
            self._on_monitor_changed,
            baseline=self.baseline_config.monitor,
            help="Monitor to cover: 'primary', 'all' (multi-monitor), "
            "or a specific output name (e.g., 'HDMI-1').",
        )
        device_names = ["Auto (best)"] + [
            _short_device_name(d.name) for d in get_discovered_devices()
        ]
        current_name = self._config.gpu if self._config.gpu else "Auto (best)"
        if current_name not in device_names:
            current_name = "Auto (best)"
        self._gpu_combo = self._add_combo(
            "GPU",
            device_names,
            current_name,
            self._on_gpu_changed,
            baseline=(
                self.baseline_config.gpu if self.baseline_config.gpu else "Auto (best)"
            ),
            help="Vulkan GPU used for rendering. Auto (best) selects the most powerful GPU found.",
        )

        # ---- V-Sync ----
        self._add_section("V-Sync")
        self._present_combo = self._add_combo(
            "Present Mode",
            [e.value for e in VulkanPresentMode],
            self._config.vulkan_present_mode,
            self._on_present_mode,
            baseline=self.baseline_config.vulkan_present_mode,
            help="Vulkan presentation mode:\n"
            f"{chr(8226)} fifo: VSync on, lowest power, no tearing\n"
            f"{chr(8226)} mailbox: tear-free, lower latency, higher power\n"
            f"{chr(8226)} immediate: no VSync, lowest latency, may tear",
        )
        self._fps_cap_cb = self._add_cb(
            "Limit FPS",
            self._config.max_fps is not None,
            self._on_fps_cap_toggle,
            baseline=self.baseline_config.max_fps is not None,
            help="Enable an upper frame-rate limit.\n"
            "It's recommended to use 'mailbox' presentation mode when limiting FPS.",
        )
        self._fps_slider = self._add_slider(
            "Max FPS",
            1,
            240,
            self._config.max_fps if self._config.max_fps is not None else 60,
            slot=self._on_fps_slider,
            baseline=(
                self.baseline_config.max_fps
                if self.baseline_config.max_fps is not None
                else 60
            ),
            help="Target maximum frames per second.",
        )
        self._fps_slider.setEnabled(self._config.max_fps is not None)

        # ---- Scale Factor ----
        self._add_section("Scale Factor")
        self._auto_scale_cb = self._add_cb(
            "Auto Scale",
            self._config.scale_factor is None,
            self._on_auto_scale_changed,
            baseline=self.baseline_config.scale_factor is None,
            help="Let the application automatically detect the correct scale factor "
            "based on the physical monitor resolution.",
        )
        self._scale_slider = self._add_slider(
            "Scale Factor %",
            100,
            400,
            max(100, int((self._config.scale_factor or 1.0) * 100)),
            scale_factor=100,
            float_slot=self._on_scale_slider_changed,
            baseline=(
                self.baseline_config.scale_factor
                if self.baseline_config.scale_factor is not None
                else 1.0
            ),
            help="Manual scale factor (e.g., 1.50 for 150% scaling). "
            "Only available when 'Auto Scale' is disabled.",
        )
        self._scale_slider.setEnabled(self._config.scale_factor is not None)

    def _on_monitor_changed(self, text: str):
        self._config.monitor = text
        self.config_changed.emit()

    def _on_gpu_changed(self, text: str) -> None:
        self._config.gpu = None if text == "Auto (best)" else text
        self.config_changed.emit()

    def _on_fps_cap_toggle(self, state: int) -> None:
        enabled = bool(state)
        self._fps_slider.setEnabled(enabled)
        if enabled:
            self._config.max_fps = self._fps_slider.value()
        else:
            self._config.max_fps = None
        self.config_changed.emit()

    def _on_fps_slider(self, value: int) -> None:
        if self._fps_slider.isEnabled():
            self._config.max_fps = value
            self.config_changed.emit()

    def _on_present_mode(self, text: str):
        self._config.vulkan_present_mode = text
        self.config_changed.emit()

    def _on_auto_scale_changed(self, state: bool) -> None:
        auto = state
        self._scale_slider.setEnabled(not auto)
        if auto:
            self._config.scale_factor = None
        else:
            # When disabled, set the config to the current slider value
            self._config.scale_factor = self._scale_slider.value() / 100.0
        self.config_changed.emit()

    def _on_scale_slider_changed(self, value: float) -> None:
        if self._scale_slider.isEnabled():
            self._config.scale_factor = value
            self.config_changed.emit()
