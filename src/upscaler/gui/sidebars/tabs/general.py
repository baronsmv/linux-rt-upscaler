from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....config import DOWNSAMPLERS, UPSAMPLERS, UPSCALING_MODELS

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

        # ---- Sampler Selection ----
        self._add_section("Sampler Algorithm")
        self._upsampler_combo = self._add_combo(
            "Upsampler",
            UPSAMPLERS,
            self._config.upsampler,
            self._on_upsampler,
            baseline=self.baseline_config.upsampler,
            help="Spatial upscaler used when the output is larger than the input.\n"
            f"{chr(8226)} lanczos: Fixed Lanczos-2 (sharp, linear-light, best for 2D art)\n"
            f"{chr(8226)} fsr: AMD FidelityFX Super Resolution 1.0 (edge-adaptive, best for 3D content)\n"
            f"{chr(8226)} nis: NVIDIA Image Scaling (directional sharpening, sRGB, may look oversharpened)",
        )
        self._downsampler_combo = self._add_combo(
            "Downsampler",
            DOWNSAMPLERS,
            self._config.downsampler,
            self._on_downsampler,
            baseline=self.baseline_config.downsampler,
            help="Spatial downscaler used when the output is smaller than the input.\n"
            f"{chr(8226)} catmull: Catmull-Rom bicubic (sharp, fast, linear-light)\n"
            f"{chr(8226)} lanczos: Adaptive Lanczos (variable radius, high quality for any ratio)",
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

        # ---- Daemon ----
        self._add_section("Automatic Upscaling")
        if self._profile_active:
            self._auto_cb = self._add_cb(
                "Exclude from Daemon Mode",
                self._config.daemon_exclude,
                self._on_daemon_exclude_changed,
                baseline=self.baseline_config.daemon_exclude,
                help="Exclude this profile from automatic upscaling.",
            )
        else:
            self._daemon_cb = self._add_cb(
                "Daemon Mode",
                self._config.daemon,
                self._on_daemon_changed,
                baseline=self.baseline_config.daemon,
                help="Automatically upscale any window matching a profile.",
            )

    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_double_changed(self, state: int) -> None:
        self._config.double_upscale = bool(state)
        self.config_changed.emit()

    def _on_upsampler(self, text: str):
        self._config.upsampler = text
        self.config_changed.emit()

    def _on_downsampler(self, text: str):
        self._config.downsampler = text
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
