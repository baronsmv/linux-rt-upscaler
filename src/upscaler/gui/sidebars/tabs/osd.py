from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class OSDTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "OSD", parent)

    def _build_content(self) -> None:
        self._add_section("On‑Screen Display")
        self._osd_enabled = self._add_cb(
            "Show OSD", self._config.show_osd, self._on_osd_enabled
        )
        self._osd_duration = self._add_slider(
            "Duration (s)",
            1,
            10,
            int(self._config.osd_duration),
            self._on_osd_duration,
            show_val=True,
        )

    def _on_osd_enabled(self, state):
        self._config.show_osd = bool(state)
        self.config_changed.emit()

    def _on_osd_duration(self, val):
        self._config.osd_duration = float(val)
        self.config_changed.emit()
