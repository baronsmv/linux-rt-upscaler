from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ..controls import normalize_to_hex

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class PresentationTab(SettingsTab):
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
            title="Presentation",
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Output Geometry ----
        self._add_section("Output Geometry")
        self._geom_combo = self._add_combo(
            "Scaling mode",
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
            self._on_geometry_changed,
            baseline=self.baseline_config.output_geometry,
            help="How the upscaled content fits the overlay:\n"
            f"{chr(8226)} fit: letterbox, preserves aspect ratio\n"
            f"{chr(8226)} stretch: fill, aspect ratio may be distorted\n"
            f"{chr(8226)} cover: fill and crop to fit",
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
                help=(
                    "Horizontal offset from the centered position "
                    "(positive = right, negative = left)."
                    if "X" in label
                    else "Vertical offset from the centered position "
                    "(positive = down, negative = up)."
                ),
            )

        # ---- Background Color ----
        self._add_section("Background Color")
        bg = normalize_to_hex(self._config.background_color)
        baseline_bg = normalize_to_hex(self.baseline_config.background_color)
        self._bg_picker = self._add_color_picker(
            "Color",
            bg,
            self._on_bg_color,
            baseline=baseline_bg,
            help="Color of the letterbox bars. Supports transparency.",
        )

    def _on_geometry_changed(self, text: str) -> None:
        self._config.output_geometry = text
        self.config_changed.emit()

    def _on_crop_left(self, value: int):
        self._config.crop_left = value
        self.config_changed.emit()

    def _on_crop_top(self, value: int):
        self._config.crop_top = value
        self.config_changed.emit()

    def _on_crop_right(self, value: int):
        self._config.crop_right = value
        self.config_changed.emit()

    def _on_crop_bottom(self, value: int):
        self._config.crop_bottom = value
        self.config_changed.emit()

    def _on_offset_x(self, value: int):
        self._config.offset_x = value
        self.config_changed.emit()

    def _on_offset_y(self, value: int):
        self._config.offset_y = value
        self.config_changed.emit()

    def _on_bg_color(self, text: str):
        self._config.background_color = text
        self.config_changed.emit()
