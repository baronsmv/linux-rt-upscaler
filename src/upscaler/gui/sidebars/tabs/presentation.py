from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ...utils import normalize_to_hex
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
            title=self.tr("Presentation", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _build_content(self) -> None:
        # ---- Overlay ----
        self._add_section(self.tr("Overlay", "Settings section"))
        self._overlay_combo = self._add_combo(
            self.tr("Overlay Mode", "Label of setting (must be short)"),
            [e.value for e in OverlayMode],
            self._config.overlay_mode,
            self._on_overlay_mode,
            baseline=self.baseline_config.overlay_mode,
            help=self.tr(
                "Overlay window behaviour:\n"
                "• always-on-top: floating, cannot be focused (recommended)\n"
                "• top-transparent: click-through (mouse passes to window below)\n"
                "• fullscreen: covers entire monitor\n"
                "• windowed: normal window with decorations",
                "Description of a setting (tooltip). Do not translate 'always-on-top', 'top-transparent', 'fullscreen', 'windowed': they are internal overlay mode identifiers.",
            ),
        )
        self._geom_combo = self._add_combo(
            self.tr("Output Geometry", "Label of setting (must be short)"),
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
            self._on_geometry_changed,
            baseline=self.baseline_config.output_geometry,
            help=self.tr(
                "How the upscaled content fits the overlay:\n"
                "• fit: letterbox, preserves aspect ratio\n"
                "• stretch: fill, aspect ratio may be distorted\n"
                "• cover: fill and crop to fit",
                "Description of a setting (tooltip). "
                "Do not translate 'fit', 'stretch', 'cover': "
                "they are internal output geometry identifiers.",
            ),
        )

        # ---- Cursor ----
        self._add_section(self.tr("Cursor", "Settings section"))
        self._hide_cursor_cb = self._add_cb(
            self.tr("Hide cursor", "Label of setting (must be short)"),
            self._config.hide_cursor is not None,
            self._on_hide_cursor_toggle,
            baseline=self.baseline_config.hide_cursor is not None,
            help=self.tr(
                "Automatically hide the mouse cursor after a period of inactivity.",
                "Description of a setting (tooltip)",
            ),
        )
        bl_ms = self.baseline_config.hide_cursor
        if bl_ms is not None and bl_ms > 0:
            bl_seconds = bl_ms / 1000.0
        elif bl_ms == 0:
            bl_seconds = 0.0
        else:
            bl_seconds = 2.0
        self._hide_cursor_timeout = self._add_slider(
            self.tr("Hide Timeout (s)", "Label of setting (must be short)"),
            0,
            10000,
            self._config.hide_cursor if self._config.hide_cursor is not None else 2000,
            scale_factor=1000,
            float_slot=self._on_hide_cursor_timeout,
            baseline=bl_seconds,
            help=self.tr(
                "Time in seconds after which the cursor disappears.",
                "Description of a setting (tooltip)",
            ),
        )
        self._hide_cursor_timeout.setEnabled(self._config.hide_cursor is not None)

        # ---- Crop ----
        self._add_section("Crop")
        for label, field, slot in [
            (self.tr("Left", "Crop border label"), "crop_left", self._on_crop_left),
            (self.tr("Top", "Crop border label"), "crop_top", self._on_crop_top),
            (self.tr("Right", "Crop border label"), "crop_right", self._on_crop_right),
            (
                self.tr("Bottom", "Crop border label"),
                "crop_bottom",
                self._on_crop_bottom,
            ),
        ]:
            self._add_slider(
                label,
                0,
                200,
                getattr(self._config, field),
                slot,
                baseline=getattr(self.baseline_config, field),
                help=self.tr(
                    "Pixels to crop from the {0} border of the target window.",
                    "Description of a setting (tooltip)",
                ).format(label.lower()),
            )

        # ---- Offsets ----
        self._add_section(self.tr("Offset", "Settings section"))
        for label, field, slot in [
            (
                self.tr("X Offset", "Label of setting (must be short)"),
                "offset_x",
                self._on_offset_x,
            ),
            (
                self.tr("Y Offset", "Label of setting (must be short)"),
                "offset_y",
                self._on_offset_y,
            ),
        ]:
            self._add_slider(
                label,
                -200,
                200,
                getattr(self._config, field),
                slot,
                baseline=getattr(self.baseline_config, field),
                help=(
                    self.tr(
                        "Horizontal offset from the centered position "
                        "(positive = right, negative = left).",
                        "Description of a setting (tooltip)",
                    )
                    if field == "offset_x"
                    else self.tr(
                        "Vertical offset from the centered position "
                        "(positive = down, negative = up).",
                        "Description of a setting (tooltip)",
                    )
                ),
            )

        # ---- Background Color ----
        self._add_section(self.tr("Background Color", "Settings section"))
        bg = normalize_to_hex(self._config.background_color)
        baseline_bg = normalize_to_hex(self.baseline_config.background_color)
        self._bg_picker = self._add_color_picker(
            self.tr("Color", "Label of setting (must be short)"),
            bg,
            self._on_bg_color,
            baseline=baseline_bg,
            help=self.tr(
                "Color of the letterbox bars. Supports transparency.",
                "Description of a setting (tooltip)",
            ),
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
