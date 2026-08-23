from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class ExtrasTab(SettingsTab):
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
            title=self.tr("Extras", self.TAB),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Screenshot Location ----
        self._add_section(self.tr("Screenshot Location", self.SECTION))
        self._dir_picker = self._add_path_picker(
            self.tr("Directory", self.SETTING),
            self._config.screenshot_dir,
            self._on_dir_changed,
            baseline=self.baseline_config.screenshot_dir,
            help=self.tr("Folder where screenshots will be saved.", self.DESCRIPTION),
        )
        self._file_input = self._add_text(
            self.tr("Template", self.SETTING),
            self._config.screenshot_filename,
            self._on_file_changed,
            baseline=self.baseline_config.screenshot_filename,
            help=self.tr(
                "Filename template for screenshots. Available placeholders:\n"
                "• {timestamp}: capture time (supports strftime, e.g. "
                "{timestamp:%Y-%m-%d-%H-%M-%S})\n"
                "• {title}: current window title\n"
                "• {profile}: active profile name (fallback to {{title}} if no profile)\n"
                "• {model}: active upscaling model\n"
                "• {width}: upscaled image width\n"
                "• {height}: upscaled image height",
                self.DESCRIPTION,
            ),
        )

        # ---- On-Screen Display ----
        self._add_section(self.tr("On-Screen Display", self.SECTION))
        self._osd_enabled = self._add_cb(
            self.tr("Show OSD", self.SETTING),
            self._config.show_osd,
            self._on_osd_enabled,
            baseline=self.baseline_config.show_osd,
            help=self.tr(
                "Show on-screen messages when model, geometry, or zoom changes, "
                "and after taking a screenshot.",
                self.DESCRIPTION,
            ),
        )
        self._osd_duration = self._add_slider(
            self.tr("Duration (s)", self.SETTING),
            1,
            1000,
            int(self._config.osd_duration * 100),
            scale_factor=100,
            float_slot=self._on_osd_duration,
            baseline=self.baseline_config.osd_duration,
            help=self.tr(
                "How many seconds OSD messages remain visible before fading out.",
                self.DESCRIPTION,
            ),
        )
        self._osd_duration.setEnabled(self._config.show_osd)

    def _on_dir_changed(self, path: str) -> None:
        self._config.screenshot_dir = path
        self.config_changed.emit()

    def _on_file_changed(self, text: str) -> None:
        self._config.screenshot_filename = text
        self.config_changed.emit()

    def _on_osd_enabled(self, state: int):
        enabled = bool(state)
        self._config.show_osd = enabled
        self._osd_duration.setEnabled(enabled)
        self.config_changed.emit()

    def _on_osd_duration(self, value: float):
        self._config.osd_duration = value
        self.config_changed.emit()
