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
        self._auto_device = self.tr("Auto (best)", "GPU automatic device option")
        super().__init__(
            gui_config,
            title=self.tr("Display", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Devices ----
        self._add_section(self.tr("Devices", "Settings section"))
        self._monitor_combo = self._add_combo(
            self.tr("Monitor", "Label of setting (must be short)"),
            list_monitors(),
            self._config.monitor,
            self._on_monitor_changed,
            baseline=self.baseline_config.monitor,
            help=self.tr(
                "Monitor used for upscaling: the primary monitor, multi-monitor, "
                "or a specific output name (for example, HDMI-1).",
                "Description of a setting (tooltip)",
            ),
        )
        device_names = [self._auto_device] + [
            _short_device_name(d.name) for d in get_discovered_devices()
        ]
        current_name = self._config.gpu if self._config.gpu else self._auto_device
        if current_name not in device_names:
            current_name = self._auto_device
        self._gpu_combo = self._add_combo(
            self.tr("GPU", "Label of setting (must be short)"),
            device_names,
            current_name,
            self._on_gpu_changed,
            baseline=(
                self.baseline_config.gpu
                if self.baseline_config.gpu
                else self._auto_device
            ),
            help=self.tr(
                "GPU used for upscaling.\n"
                "Select '{0}' to automatically use the most powerful available GPU.",
                "Description of a setting (tooltip)",
            ).format(self._auto_device),
        )

        # ---- V-Sync ----
        self._add_section(self.tr("V-Sync", "Settings section"))
        self._present_combo = self._add_combo(
            self.tr("Present Mode", "Label of setting (must be short)"),
            [e.value for e in VulkanPresentMode],
            self._config.vulkan_present_mode,
            self._on_present_mode,
            baseline=self.baseline_config.vulkan_present_mode,
            help=self.tr(
                "Vulkan presentation mode:\n"
                "• fifo: VSync on, lowest power, no tearing\n"
                "• mailbox: tear-free, lower latency, higher power\n"
                "• immediate: no VSync, lowest latency, may tear",
                "Description of a setting (tooltip). "
                "Do not translate fifo, mailbox and immediate: "
                "they are Vulkan presentation mode identifiers.",
            ),
        )
        self._fps_cap_cb = self._add_cb(
            self.tr("Limit FPS", "Label of setting (must be short)"),
            self._config.max_fps is not None,
            self._on_fps_cap_toggle,
            baseline=self.baseline_config.max_fps is not None,
            help=self.tr(
                "Enable a maximum frame rate.\n"
                "For best results, use the 'mailbox' presentation mode when limiting FPS.",
                "Description of a setting (tooltip)",
            ),
        )
        self._fps_slider = self._add_slider(
            self.tr("Max FPS", "Label of setting (must be short)"),
            1,
            240,
            self._config.max_fps if self._config.max_fps is not None else 60,
            slot=self._on_fps_slider,
            baseline=(
                self.baseline_config.max_fps
                if self.baseline_config.max_fps is not None
                else 60
            ),
            help=self.tr(
                "Target maximum frames per second.",
                "Description of a setting (tooltip)",
            ),
        )
        self._fps_slider.setEnabled(self._config.max_fps is not None)

        # ---- Scale Factor ----
        self._add_section(self.tr("Scale Factor", "Settings section"))
        self._auto_scale_cb = self._add_cb(
            self.tr("Auto Scale", "Label of setting (must be short)"),
            self._config.scale_factor is None,
            self._on_auto_scale_changed,
            baseline=self.baseline_config.scale_factor is None,
            help=self.tr(
                "Automatically detect the correct scale factor based on the physical monitor resolution.",
                "Description of a setting (tooltip)",
            ),
        )
        self._scale_slider = self._add_slider(
            self.tr("Scale Factor", "Label of setting (must be short)"),
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
            help=self.tr(
                "Set the scale factor manually as a percentage (for example, 1.50 for 150% scaling).\n"
                "Only available when Auto Scale is off.",
                "Description of a setting (tooltip)",
            ),
        )
        self._scale_slider.setEnabled(self._config.scale_factor is not None)

    def _on_monitor_changed(self, text: str):
        self._config.monitor = text
        self.config_changed.emit()

    def _on_gpu_changed(self, text: str) -> None:
        self._config.gpu = None if text == self._auto_device else text
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
