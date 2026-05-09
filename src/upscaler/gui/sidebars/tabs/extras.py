from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class ExtrasTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Extras", parent)

    def _build_content(self) -> None:
        # ---- Screenshot Location ----
        self._add_section("Screenshot Location")
        self._dir_picker = self._add_path_picker(
            "Directory",
            self._config.screenshot_dir,
            self._on_dir_changed,
        )

        self._add_section("Filename Template")
        self._file_input = self._add_text(
            "Template",
            self._config.screenshot_filename,
            self._on_file_changed,
        )

        # ---- On-Screen Display ----
        self._add_section("On-Screen Display")
        self._osd_enabled = self._add_cb(
            "Show OSD", self._config.show_osd, self._on_osd_enabled
        )
        self._osd_duration = self._add_slider(
            "Duration (s)",
            1,
            10,
            int(self._config.osd_duration),
            self._on_osd_duration,
        )
        self._osd_duration.setEnabled(self._config.show_osd)

    def _on_dir_changed(self, path: str) -> None:
        self._config.screenshot_dir = path
        self.config_changed.emit()

    def _on_file_changed(self, text: str) -> None:
        self._config.screenshot_filename = text
        self.config_changed.emit()

    def _on_osd_enabled(self, state):
        enabled = bool(state)
        self._config.show_osd = enabled
        self._osd_duration.setEnabled(enabled)
        self.config_changed.emit()

    def _on_osd_duration(self, val):
        self._config.osd_duration = float(val)
        self.config_changed.emit()
