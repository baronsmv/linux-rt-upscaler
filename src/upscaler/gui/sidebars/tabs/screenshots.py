from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import LineEditRow, PathPickerRow, SectionLabel

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class ScreenshotsTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Screenshots", parent)

    def _build_content(self) -> None:
        self._add_section("Screenshot Location")
        self._dir_picker = PathPickerRow(
            "Directory",
            self.gui_config,
            initial_path=self._config.screenshot_dir,
        )
        self._dir_picker.pathChanged.connect(self._on_dir_changed)
        self.content_layout.addWidget(self._dir_picker)

        self._add_section("Filename Template")
        self._file_input = LineEditRow(
            "Template",
            self.gui_config,
            self._config.screenshot_filename,
        )
        self._file_input.textChanged.connect(self._on_file_changed)
        self.content_layout.addWidget(self._file_input)

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

    def _on_dir_changed(self, path: str) -> None:
        self._config.screenshot_dir = path
        self.config_changed.emit()

    def _on_file_changed(self, text: str) -> None:
        self._config.screenshot_filename = text
        self.config_changed.emit()
