from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....config import UPSCALING_MODELS

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class GeneralTab(SettingsTab):

    daemon_toggled = Signal(bool)

    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        profile_active: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._config = config
        self._profile_active = profile_active
        super().__init__(
            gui_config,
            title=self.tr("General", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Model & double upscale ----
        self._add_section(self.tr("Upscaling Model", "Settings section"))
        self._add_named_slider(
            self.tr("Model", "Label of setting (must be short)"),
            UPSCALING_MODELS,
            self._config.model,
            self._on_model_changed,
            baseline=self.baseline_config.model,
            help=self.tr(
                "Upscaling SRCNN model to use.\n"
                "All models upscale to 2x, and are ordered from lower to higher quality.\n"
                "Rightmost models are deeper and slower, but produce better results.",
                "Description of a setting (tooltip)",
            ),
        )
        self._double_cb = self._add_cb(
            self.tr("Double Upscale (4x)", "Label of setting (must be short)"),
            self._config.double_upscale,
            self._on_double_changed,
            baseline=self.baseline_config.double_upscale,
            help=self.tr(
                "Perform two 2x upscales in a row for a total of 4x (for example, 720p to 2880p).\n"
                "Useful for high-resolution screens (4K) and low-resolution sources.\n"
                "Uses more GPU power.",
                "Description of a setting (tooltip)",
            ),
        )

        # ---- Focus Tracking ----
        self._add_section(self.tr("Focus Tracking", "Settings section"))
        self._follow_focus_cb = self._add_cb(
            self.tr("Follow Focus", "Label of setting (must be short)"),
            self._config.follow_focus,
            self._on_follow_focus,
            baseline=self.baseline_config.follow_focus,
            help=self.tr(
                "Automatically upscale the window that currently has focus.\n"
                "Useful when working with multiple windows.",
                "Description of a setting (tooltip)",
            ),
        )
        self._pause_focus_loss_cb = self._add_cb(
            self.tr("Pause on Focus Loss", "Label of setting (must be short)"),
            self._config.pause_on_focus_loss,
            self._on_pause_focus_loss,
            baseline=self.baseline_config.pause_on_focus_loss,
            help=self.tr(
                "Hide the upscaled overlay when the target window loses focus, and show it again when focus returns.\n"
                "Turn off to keep the overlay always visible.",
                "Description of a setting (tooltip)",
            ),
        )

        # ---- Daemon ----
        self._add_section(self.tr("Automatic Upscaling", "Settings section"))
        if self._profile_active:
            self._auto_cb = self._add_cb(
                self.tr("Exclude from Daemon Mode", "Label of setting (must be short)"),
                self._config.daemon_exclude,
                self._on_daemon_exclude_changed,
                baseline=self.baseline_config.daemon_exclude,
                help=self.tr(
                    "When Daemon Mode is active, "
                    "this profile will not be used to automatically upscale matching windows.",
                    "Description of a setting (tooltip)",
                ),
            )
        else:
            self._daemon_cb = self._add_cb(
                self.tr("Daemon Mode", "Label of setting (must be short)"),
                self._config.daemon,
                self._on_daemon_changed,
                baseline=self.baseline_config.daemon,
                help=self.tr(
                    "When enabled, a background process automatically upscales "
                    "any window that matches a profile.\n"
                    "Turn off to manually select a window from the grid.",
                    "Description of a setting (tooltip)",
                ),
            )

    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_double_changed(self, state: int) -> None:
        self._config.double_upscale = bool(state)
        self.config_changed.emit()

    def _on_follow_focus(self, state: int):
        self._config.follow_focus = bool(state)
        self.config_changed.emit()

    def _on_pause_focus_loss(self, state: int):
        self._config.pause_on_focus_loss = bool(state)
        self.config_changed.emit()

    def _on_daemon_changed(self, state: int) -> None:
        enabled = bool(state)
        self._config.daemon = enabled
        self.config_changed.emit()
        self.daemon_toggled.emit(enabled)

    def _on_daemon_exclude_changed(self, state: int) -> None:
        self._config.daemon_exclude = bool(state)
        self.config_changed.emit()
