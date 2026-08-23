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
            title=self.tr("Scaling", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Sampler Selection ----
        self._add_section(self.tr("Sampler Algorithm", "Settings section"))
        self._upsampler_combo = self._add_combo(
            self.tr("Upsampler", "Label of setting (must be short)"),
            list(UPSAMPLERS.keys()),
            UPSAMPLER_NAMES.get(self._config.upsampler, "Lanczos"),
            self._on_upsampler,
            baseline=UPSAMPLER_NAMES.get(self.baseline_config.upsampler, "Lanczos"),
            help=self.tr(
                "Applied after SRCNN upscaling to reach the target output size (for example, 1440p → 4K).\n"
                "• Lanczos-2 — sharp, best for 2D art and text (recommended)\n"
                "• AMD FSR 1.0 — fast, best for 3D but may introduce artifacts on fine details\n"
                "• NVIDIA Image Scaling — oversharpens and introduces ringing, not recommended",
                "Description of a setting (tooltip). "
                "Do not translate the filter names (Lanczos-2, Lanczos-3, FSR, NIS).",
            ),
        )
        self._downsampler_combo = self._add_combo(
            self.tr("Downsampler", "Label of setting (must be short)"),
            list(DOWNSAMPLERS.keys()),
            DOWNSAMPLER_NAMES.get(self._config.downsampler, "Catmull-Rom"),
            self._on_downsampler,
            baseline=DOWNSAMPLER_NAMES.get(
                self.baseline_config.downsampler, "Catmull-Rom"
            ),
            help=self.tr(
                "Applied after SRCNN upscaling to reduce the image to the target output size (e.g., 1440p → 1080p).\n"
                "• Catmull-Rom (bicubic) — sharp and fast, excellent tradeoff for most cases (recommended)\n"
                "• Adaptive Lanczos — slower, best overall quality, handles extreme downscaling well",
                "Description of a setting (tooltip). "
                "Do not translate the filter names (Catmull-Rom, Adaptive Lanczos).",
            ),
        )

        # ---- Sampler Options ----
        self._add_section(self.tr("Sampler Options", "Settings section"))
        self._blur = self._add_slider(
            self.tr("Blur", "Label of setting (must be short)"),
            1,
            200,
            max(1, int(self._config.blur * 100)),
            scale_factor=100,
            float_slot=self._on_blur,
            baseline=self.baseline_config.blur,
            help=self.tr(
                "Kernel width (blur factor) for Lanczos and Catmull-Rom.\n"
                "Lower values are sharper but may ring; higher values are smoother.\n"
                "Recommended range: 0.8 - 1.2.",
                "Description of a setting (tooltip)",
            ),
        )
        self._antiring = self._add_slider(
            self.tr("Antiring Strength", "Label of setting (must be short)"),
            0,
            100,
            int(self._config.antiring_strength * 100),
            scale_factor=100,
            float_slot=self._on_antiring,
            baseline=self.baseline_config.antiring_strength,
            help=self.tr(
                "Anti-ringing strength (0.0 - 1.0) for Adaptive Lanczos and Catmull-Rom.\n"
                "Lower values preserve more detail but may allow ringing.\n"
                "Recommended range: 0.7 - 1.0.",
                "Description of a setting (tooltip)",
            ),
        )

        # ---- Sampler Options ----
        self._add_section(self.tr("Lanczos Options", "Settings section"))
        self._tight_cb = self._add_cb(
            self.tr("Tight Antiring", "Label of setting (must be short)"),
            self._config.tight_antiring,
            self._on_tight_antiring,
            baseline=self.baseline_config.tight_antiring,
            help=self.tr(
                "Use only the central 2x2 area for anti-ringing.\n"
                "Keeps thin text and line art sharp. Turn off if you see ringing on high-contrast edges.",
                "Description of a setting (tooltip)",
            ),
        )
        self._radius_override_cb = self._add_cb(
            self.tr("Override Lanczos Radius", "Label of setting (must be short)"),
            self._config.kernel_radius is not None,
            self._on_radius_override_toggle,
            baseline=self.baseline_config.kernel_radius is not None,
            help=self.tr(
                "Force a specific Lanczos kernel radius instead of automatic selection.\n"
                "When off, the radius is chosen automatically (2 for upscaling, variable for downscaling).",
                "Description of a setting (tooltip)",
            ),
        )
        self._radius_slider = self._add_slider(
            self.tr("Radius", "Label of setting (must be short)"),
            2,
            10,
            self._config.kernel_radius if self._config.kernel_radius is not None else 2,
            slot=self._on_radius_slider,
            baseline=(
                self.baseline_config.kernel_radius
                if self.baseline_config.kernel_radius is not None
                else 2
            ),
            help=self.tr(
                "Lanczos kernel radius (2 = standard Lanczos2, 3 = sharper 6-tap).\n"
                "Higher radii reduce aliasing but increase GPU load.",
                "Description of a setting (tooltip)",
            ),
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
