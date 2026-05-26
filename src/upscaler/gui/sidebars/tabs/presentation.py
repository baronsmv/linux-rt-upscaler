from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ..controls import normalize_to_hex
from ....config import OverlayMode

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
        # ---- Overlay ----
        self._add_section("Overlay")
        self._overlay_combo = self._add_combo(
            "Overlay mode",
            [e.value for e in OverlayMode],
            self._config.overlay_mode,
            self._on_overlay_mode,
            baseline=self.baseline_config.overlay_mode,
            help="Overlay window behaviour:\n"
            f"{chr(8226)} always-on-top: floating, cannot be focused (recommended)\n"
            f"{chr(8226)} top-transparent: click-through (mouse passes to window below)\n"
            f"{chr(8226)} fullscreen: covers entire monitor\n"
            f"{chr(8226)} windowed: normal window with decorations",
        )
        self._geom_combo = self._add_combo(
            "Output geometry",
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
            self._on_geometry_changed,
            baseline=self.baseline_config.output_geometry,
            help="How the upscaled content fits the overlay:\n"
            f"{chr(8226)} fit: letterbox, preserves aspect ratio\n"
            f"{chr(8226)} stretch: fill, aspect ratio may be distorted\n"
            f"{chr(8226)} cover: fill and crop to fit",
        )

        # ---- Cursor ----
        self._add_section("Cursor")
        self._hide_cursor_cb = self._add_cb(
            "Hide cursor",
            self._config.hide_cursor is not None,
            self._on_hide_cursor_toggle,
            baseline=self.baseline_config.hide_cursor is not None,
            help="Automatically hide the mouse cursor after a period of inactivity.",
        )
        bl_ms = self.baseline_config.hide_cursor
        if bl_ms is not None and bl_ms > 0:
            bl_seconds = bl_ms / 1000.0
        elif bl_ms == 0:
            bl_seconds = 0.0
        else:
            bl_seconds = 2.0
        self._hide_cursor_timeout = self._add_slider(
            "Hide Timeout (s)",
            0,
            10000,
            self._config.hide_cursor if self._config.hide_cursor is not None else 2000,
            scale_factor=1000,
            float_slot=self._on_hide_cursor_timeout,
            baseline=bl_seconds,
            help="Time in seconds after which the cursor disappears.",
        )
        self._hide_cursor_timeout.setEnabled(self._config.hide_cursor is not None)

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

    def _on_overlay_mode(self, text: str):
        self._config.overlay_mode = text
        self.config_changed.emit()

    def _on_hide_cursor_toggle(self, state: int) -> None:
        enabled = bool(state)
        self._hide_cursor_timeout.setEnabled(enabled)
        if enabled:
            self._config.hide_cursor = self._hide_cursor_timeout.value()
        else:
            self._config.hide_cursor = None
        self.config_changed.emit()

    def _on_hide_cursor_timeout(self, value: int) -> None:
        if self._hide_cursor_timeout.isEnabled():
            self._config.hide_cursor = int(value * 1000)
            self.config_changed.emit()

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
