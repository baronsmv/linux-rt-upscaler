from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....config import DOWNSAMPLERS, UPSAMPLERS

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config

UPSAMPLER_NAMES = {v: k for k, v in UPSAMPLERS.items()}
DOWNSAMPLER_NAMES = {v: k for k, v in DOWNSAMPLERS.items()}


class ScalingTab(SettingsTab):

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
            title="Scaling",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
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

        # ---- Sampler Options ----
        self._add_section("Downsampler Options")
        self._blur = self._add_slider(
            "Blur",
            1,
            200,
            max(1, int(self._config.blur * 100)),
            scale_factor=100,
            float_slot=self._on_blur,
            baseline=self.baseline_config.blur,
            help="Kernel width (blur factor) for Lanczos and Catmull-Rom.\n"
            "Lower values increase sharpness/ringing, while higher values smooth the result.\n"
            "Recommended range: 0.8 - 1.2.",
        )
        self._antiring = self._add_slider(
            "Antiring Strength",
            0,
            100,
            int(self._config.antiring_strength * 100),
            scale_factor=100,
            float_slot=self._on_antiring,
            baseline=self.baseline_config.antiring_strength,
            help="Anti-ringing strength (0.0 - 1.0) for Adaptive Lanczos and Catmull-Rom.\n"
            "Lower values soften the clamp, preserving more detail at the cost of possible ringing.\n"
            "Recommended range: 0.7 - 1.0.",
        )

        # ---- Sampler Options ----
        self._add_section("Lanczos Options")
        self._tight_cb = self._add_cb(
            "Tight Antiring",
            self._config.tight_antiring,
            self._on_tight_antiring,
            baseline=self.baseline_config.tight_antiring,
            help="Use only the central 2x2 neighborhood for anti-ringing bounds.\n"
            "Keeps thin text and line art sharp. Disable if you see distant ringing artifacts "
            "on high-contrast edges.",
        )
        self._radius_override_cb = self._add_cb(
            "Override Lanczos Radius",
            self._config.kernel_radius is not None,
            self._on_radius_override_toggle,
            baseline=self.baseline_config.kernel_radius is not None,
            help="Force a specific Lanczos kernel radius instead of the automatic selection.\n"
            "When unchecked, radius is chosen automatically (2 for upscaling, variable for downscaling).",
        )
        self._radius_slider = self._add_slider(
            "Radius",
            2,
            10,
            self._config.kernel_radius if self._config.kernel_radius is not None else 2,
            slot=self._on_radius_slider,
            baseline=(
                self.baseline_config.kernel_radius
                if self.baseline_config.kernel_radius is not None
                else 2
            ),
            help="Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6‑tap, etc.).\n"
            "Higher radii reduce aliasing but increase GPU load.",
        )
        self._radius_slider.setEnabled(self._config.kernel_radius is not None)

    def _on_upsampler(self, text: str):
        self._config.upsampler = UPSAMPLERS.get(text, "lanczos")
        self.config_changed.emit()

    def _on_downsampler(self, text: str):
        self._config.downsampler = DOWNSAMPLERS.get(text, "catmull")
        self.config_changed.emit()

    def _on_blur(self, value: float):
        self._config.blur = value
        self.config_changed.emit()

    def _on_antiring(self, value: float):
        self._config.antiring_strength = value
        self.config_changed.emit()

    def _on_tight_antiring(self, state: int):
        self._config.tight_antiring = bool(state)
        self.config_changed.emit()

    def _on_radius_override_toggle(self, state: int) -> None:
        enabled = bool(state)
        self._radius_slider.setEnabled(enabled)
        if enabled:
            self._config.kernel_radius = self._radius_slider.value()
        else:
            self._config.kernel_radius = None
        self.config_changed.emit()

    def _on_radius_slider(self, value: int) -> None:
        if self._radius_slider.isEnabled():
            self._config.kernel_radius = value
            self.config_changed.emit()
