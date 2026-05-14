from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QColor

from ..common import SettingsTab
from ....config import OverlayMode
from ....utils import list_monitors

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class DisplayTab(SettingsTab):
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
            title="Display & Overlay",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Monitor & Scale ----
        self._add_section("Monitor")
        self._monitor_combo = self._add_combo(
            "Monitor",
            list_monitors(),
            self._config.monitor,
            self._on_monitor_changed,
            baseline=self.baseline_config.monitor,
            help="Monitor to cover: 'primary', 'all' (multi-monitor), "
            "or a specific output name (e.g., 'HDMI-1').",
        )

        # ---- Scale Factor ----
        self._add_section("Scale Factor")
        self._auto_scale_cb = self._add_cb(
            "Auto Scale",
            self._config.scale_factor is None,
            self._on_auto_scale_changed,
            baseline=self.baseline_config.scale_factor is None,
            help="Let the application automatically detect the correct scale factor "
            "based on the physical monitor resolution.",
        )
        self._scale_slider = self._add_slider(
            "Scale Factor %",
            100,
            400,
            max(100, int((self._config.scale_factor or 1.0) * 100)),
            scale_factor=100,
            float_slot=self._on_scale_slider_changed,
            baseline=(
                self.baseline_config.scale_factor
                if self.baseline_config.scale_factor is not None
                else 1.0
            ),
            help="Manual scale factor (e.g., 1.50 for 150% scaling). "
            "Only available when 'Auto Scale' is disabled.",
        )
        self._scale_slider.setEnabled(self._config.scale_factor is not None)

        # ---- Overlay Mode ----
        self._add_section("Overlay Mode")
        self._overlay_combo = self._add_combo(
            "Mode",
            [e.value for e in OverlayMode],
            self._config.overlay_mode,
            self._on_overlay_mode,
            baseline=self.baseline_config.overlay_mode,
            help="Overlay window behaviour:\n"
            f"{chr(8226)} always-on-top - floating, cannot be focused (recommended)\n"
            f"{chr(8226)} top-transparent - click-through (mouse passes to window below)\n"
            f"{chr(8226)} fullscreen - covers entire monitor\n"
            f"{chr(8226)} windowed - normal window with decorations",
        )

        # ---- Output Geometry ----
        self._add_section("Output Geometry")
        self._geom_combo = self._add_combo(
            "Scaling mode",
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
            self._on_geometry_changed,
            baseline=self.baseline_config.output_geometry,
            help="How the upscaled content fits the overlay:\n"
            f"{chr(8226)} fit - letterbox, preserves aspect ratio\n"
            f"{chr(8226)} stretch - fill, aspect ratio may be distorted\n"
            f"{chr(8226)} cover - fill and crop to fit",
        )

        # ---- Crop ----
        self._add_section("Crop")
        for label, field, slot in [
            ("Left", "crop_left", self._on_crop_left),
            ("Top", "crop_top", self._on_crop_top),
            ("Right", "crop_right", self._on_crop_right),
            ("Bottom", "crop_bottom", self._on_crop_bottom),
        ]:
            self._add_slider(
                label,
                0,
                200,
                getattr(self._config, field),
                slot,
                baseline=getattr(self.baseline_config, field),
                help=f"Pixels to crop from the {label.lower()} border of the target window.",
            )

        # ---- Offsets ----
        self._add_section("Offset")
        for label, field, slot in [
            ("X Offset", "offset_x", self._on_offset_x),
            ("Y Offset", "offset_y", self._on_offset_y),
        ]:
            self._add_slider(
                label,
                -200,
                200,
                getattr(self._config, field),
                slot,
                baseline=getattr(self.baseline_config, field),
                help=f"{'Horizontal' if 'X' in label else 'Vertical'} offset from the "
                "centered position (positive = {'right' if 'X' in label else 'down'}).",
            )

        # ---- Background Color ----
        self._add_section("Background Color")
        bg = self._config.background_color
        if isinstance(bg, tuple):
            # convert (b, g, r, a) to #AARRGGBB
            r, g, b, a = bg[2], bg[1], bg[0], bg[3]
            r8, g8, b8, a8 = [int(c * 255) for c in (r, g, b, a)]
            bg = f"#{a8:02x}{r8:02x}{g8:02x}{b8:02x}"

        elif isinstance(bg, str) and not bg.startswith("#"):
            # named color - convert to hex via QColor
            qc = QColor(bg)
            if qc.isValid():
                bg = qc.name(QColor.HexArgb)

        # Baseline background color
        baseline_bg = self.baseline_config.background_color
        if isinstance(baseline_bg, tuple):
            r, g, b, a = baseline_bg[2], baseline_bg[1], baseline_bg[0], baseline_bg[3]
            r8, g8, b8, a8 = [int(c * 255) for c in (r, g, b, a)]
            baseline_bg = f"#{a8:02x}{r8:02x}{g8:02x}{b8:02x}"
        elif isinstance(baseline_bg, str) and not baseline_bg.startswith("#"):
            qc = QColor(baseline_bg)
            if qc.isValid():
                baseline_bg = qc.name(QColor.HexArgb)

        self._bg_picker = self._add_color_picker(
            "Color",
            bg,
            self._on_bg_color,
            baseline=baseline_bg,
            help="Color of the letterbox bars. Supports transparency.",
        )

    def _on_monitor_changed(self, text: str):
        self._config.monitor = str(text)
        self.config_changed.emit()

    def _on_auto_scale_changed(self, state: int) -> None:
        auto = bool(state)
        self._scale_slider.setEnabled(not auto)
        if auto:
            self._config.scale_factor = None
        else:
            # When disabled, set the config to the current slider value
            self._config.scale_factor = self._scale_slider.value() / 100.0
        self.config_changed.emit()

    def _on_scale_slider_changed(self, val: float) -> None:
        if self._scale_slider.isEnabled():
            self._config.scale_factor = val
            self.config_changed.emit()

    def _on_overlay_mode(self, text: str):
        self._config.overlay_mode = str(text)
        self.config_changed.emit()

    def _on_geometry_changed(self, text: str) -> None:
        self._config.output_geometry = str(text)
        self.config_changed.emit()

    def _on_crop_left(self, val: int):
        self._config.crop_left = int(val)
        self.config_changed.emit()

    def _on_crop_top(self, val: int):
        self._config.crop_top = int(val)
        self.config_changed.emit()

    def _on_crop_right(self, val: int):
        self._config.crop_right = int(val)
        self.config_changed.emit()

    def _on_crop_bottom(self, val: int):
        self._config.crop_bottom = int(val)
        self.config_changed.emit()

    def _on_offset_x(self, val: int):
        self._config.offset_x = int(val)
        self.config_changed.emit()

    def _on_offset_y(self, val: int):
        self._config.offset_y = int(val)
        self.config_changed.emit()

    def _on_bg_color(self, text: str):
        r, g, b, a = QColor(text).getRgbF()
        self._config.background_color = (b, g, r, a)
        self.config_changed.emit()
