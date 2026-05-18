from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Signal

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
        # ---- Model & double upscale ----
        self._add_section("Upscaling Model")
        self._add_named_slider(
            "Model",
            UPSCALING_MODELS,
            self._config.model,
            self._on_model_changed,
            baseline=self.baseline_config.model,
            help="Upscaling model to use. Models are ordered from worst to best quality. "
            "Larger numbers indicate deeper networks (slower, higher quality).",
        )
        self._double_cb = self._add_cb(
            "Double Upscale (4x)",
            self._config.double_upscale,
            self._on_double_changed,
            baseline=self.baseline_config.double_upscale,
            help="Perform two 2x passes (total 4x) for higher resolution screens (4k, 1440p) "
            "or low-resolution sources. Uses more GPU resources.",
        )

        # ---- Daemon ----
        self._add_section("Daemon")
        self._daemon_cb = self._add_cb(
            "Daemon Mode",
            self._config.daemon,
            self._on_daemon_changed,
            baseline=self.baseline_config.daemon,
            help="Automatically upscale any window matching a profile.",
        )

        # ---- Focus Tracking ----
        self._add_section("Focus Tracking")
        self._follow_focus_cb = self._add_cb(
            "Follow Focus",
            self._config.follow_focus,
            self._on_follow_focus,
            baseline=self.baseline_config.follow_focus,
            help="Automatically switch the upscaling target to the currently focused window. "
            "Useful when moving between multiple windows.",
        )
        self._pause_focus_loss_cb = self._add_cb(
            "Pause on Focus Loss",
            self._config.pause_on_focus_loss,
            self._on_pause_focus_loss,
            baseline=self.baseline_config.pause_on_focus_loss,
            help="When the target window loses focus, hide the overlay until it regains focus. "
            "Uncheck to keep the overlay always visible.",
        )

    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_double_changed(self, state: bool) -> None:
        self._config.double_upscale = bool(state)
        self.config_changed.emit()

    def _on_daemon_changed(self, state: bool) -> None:
        self._config.daemon = bool(state)
        self.config_changed.emit()
        self.daemon_toggled.emit(bool(state))

    def _on_follow_focus(self, state: bool):
        self._config.follow_focus = bool(state)
        self.config_changed.emit()

    def _on_pause_focus_loss(self, state: bool):
        self._config.pause_on_focus_loss = bool(state)
        self.config_changed.emit()
