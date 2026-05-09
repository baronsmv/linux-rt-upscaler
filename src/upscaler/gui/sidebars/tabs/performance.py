from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import ComboRow, SectionLabel, SliderRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class PerformanceTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Performance", parent)

    def _build_content(self) -> None:
        self._add_section("Vulkan Rendering")
        self._present_combo = ComboRow(
            "Present Mode",
            self.gui_config,
            ["fifo", "mailbox", "immediate"],
            self._config.vulkan_present_mode,
        )
        self._present_combo.currentTextChanged.connect(self._on_present_mode)
        self.content_layout.addWidget(self._present_combo)

        self._buffer_pool = self._add_slider(
            "Buffer Pool Size",
            2,
            16,
            self._config.vulkan_buffer_pool_size,
            self._on_buffer_pool,
            show_val=True,
        )
        timeout_ms = max(1, self._config.frame_timeout // 1_000_000)
        self._frame_timeout = self._add_slider(
            "Frame Timeout (ms)",
            1,
            1000,
            timeout_ms,
            self._on_frame_timeout,
            show_val=True,
        )

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

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

    def _on_present_mode(self, text):
        self._config.vulkan_present_mode = text
        self.config_changed.emit()

    def _on_buffer_pool(self, val):
        self._config.vulkan_buffer_pool_size = val
        self.config_changed.emit()

    def _on_frame_timeout(self, val):
        self._config.frame_timeout = val * 1_000_000
        self.config_changed.emit()
