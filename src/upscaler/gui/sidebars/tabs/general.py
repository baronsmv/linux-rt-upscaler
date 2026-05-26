from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....config import DOWNSAMPLERS, UPSAMPLERS, UPSCALING_MODELS

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config

UPSAMPLER_NAMES = {v: k for k, v in UPSAMPLERS.items()}
DOWNSAMPLER_NAMES = {v: k for k, v in DOWNSAMPLERS.items()}


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
            list(UPSAMPLERS.keys()),
            UPSAMPLER_NAMES.get(self._config.upsampler, "Lanczos"),
            self._on_upsampler,
            baseline=UPSAMPLER_NAMES.get(self.baseline_config.upsampler, "Lanczos"),
            help=f"Applied after SRCNN upscaling to reach the target output size (e.g., 1440p {chr(8594)} 4k).\n"
            f"{chr(8226)} Fixed Lanczos-2 {chr(8212)} sharp, linear-light, best for 2D art\n"
            f"{chr(8226)} AMD FidelityFX Super Resolution 1.0 {chr(8212)} fast, edge-adaptive, best for 3D content\n"
            f"{chr(8226)} NVIDIA Image Scaling {chr(8212)} directional sharpening, sRGB, may look oversharpened",
        )
        self._downsampler_combo = self._add_combo(
            "Downsampler",
            list(DOWNSAMPLERS.keys()),
            DOWNSAMPLER_NAMES.get(self._config.downsampler, "Catmull-Rom"),
            self._on_downsampler,
            baseline=DOWNSAMPLER_NAMES.get(
                self.baseline_config.downsampler, "Catmull-Rom"
            ),
            help=f"Applied after SRCNN upscaling to reduce the image to the target output size (e.g., 1440p {chr(8594)} 1080p).\n"
            f"{chr(8226)} Catmull-Rom (bicubic) {chr(8212)} sharper and faster than Lanczos for mild downscaling\n"
            f"{chr(8226)} Adaptive Lanczos {chr(8212)} variable radius, high quality even in extreme downscales",
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
        self._config.upsampler = UPSAMPLERS.get(text, "lanczos")
        self.config_changed.emit()

    def _on_downsampler(self, text: str):
        self._config.downsampler = DOWNSAMPLERS.get(text, "catmull")
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
