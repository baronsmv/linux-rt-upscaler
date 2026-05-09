from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import ComboRow, SectionLabel, SliderRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class DisplayTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Display", parent)

    def _build_content(self) -> None:
        # ---- Monitor & Scale ----
        self._add_section("Monitor")
        self._monitor_combo = ComboRow(
            "Monitor",
            self.gui_config,
            ["primary", "all", "HDMI-1", "HDMI-2", "DP-1", "DP-2", "eDP-1"],
            self._config.monitor,
        )
        self._monitor_combo.currentTextChanged.connect(self._on_monitor_changed)
        self.content_layout.addWidget(self._monitor_combo)

        # Handle scale_factor = None (automatic)
        scale = self._config.scale_factor
        if scale is None:
            scale = 1.0  # default display value when automatic
        self._scale_factor = self._add_slider(
            "Scale Factor",
            100,
            400,
            max(100, int(scale * 100)),
            self._on_scale_factor,
            show_val=True,
        )

        # ---- Overlay Mode ----
        self._add_section("Overlay Mode")
        self._overlay_combo = ComboRow(
            "Mode",
            self.gui_config,
            ["always-on-top", "top-transparent", "fullscreen", "windowed"],
            self._config.overlay_mode,
        )
        self._overlay_combo.currentTextChanged.connect(self._on_overlay_mode)
        self.content_layout.addWidget(self._overlay_combo)

        # ---- Crop ----
        self._add_section("Crop")
        self._crop_left = self._add_slider(
            "Left", 0, 200, self._config.crop_left, self._on_crop_left, show_val=True
        )
        self._crop_top = self._add_slider(
            "Top", 0, 200, self._config.crop_top, self._on_crop_top, show_val=True
        )
        self._crop_right = self._add_slider(
            "Right", 0, 200, self._config.crop_right, self._on_crop_right, show_val=True
        )
        self._crop_bottom = self._add_slider(
            "Bottom",
            0,
            200,
            self._config.crop_bottom,
            self._on_crop_bottom,
            show_val=True,
        )

        # ---- Offsets ----
        self._add_section("Offset")
        self._offset_x = self._add_slider(
            "X Offset",
            -200,
            200,
            self._config.offset_x,
            self._on_offset_x,
            show_val=True,
        )
        self._offset_y = self._add_slider(
            "Y Offset",
            -200,
            200,
            self._config.offset_y,
            self._on_offset_y,
            show_val=True,
        )

        # ---- Background Colour ----
        self._add_section("Background Colour")
        self._bg_combo = ComboRow(
            "Colour",
            self.gui_config,
            ["black", "white", "transparent", "#000000", "#FFFFFF", "#00000080"],
            self._config.background_color,
        )
        self._bg_combo.currentTextChanged.connect(self._on_bg_colour)
        self.content_layout.addWidget(self._bg_combo)

    # Helpers
    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

    def _add_slider(
        self,
        label: str,
        min_val: int,
        max_val: int,
        value: int,
        slot,
        show_val: bool = False,
    ) -> SliderRow:
        slider = SliderRow(
            label, self.gui_config, min_val, max_val, value, show_value=show_val
        )
        slider.valueChanged.connect(slot)
        self.content_layout.addWidget(slider)
        return slider

    # Handlers
    def _on_monitor_changed(self, text):
        self._config.monitor = text
        self.config_changed.emit()

    def _on_scale_factor(self, val):
        # Convert slider int (e.g., 150) to float (1.5)
        self._config.scale_factor = val / 100.0
        self.config_changed.emit()

    def _on_overlay_mode(self, text):
        self._config.overlay_mode = text
        self.config_changed.emit()

    def _on_crop_left(self, val):
        self._config.crop_left = val
        self.config_changed.emit()

    def _on_crop_top(self, val):
        self._config.crop_top = val
        self.config_changed.emit()

    def _on_crop_right(self, val):
        self._config.crop_right = val
        self.config_changed.emit()

    def _on_crop_bottom(self, val):
        self._config.crop_bottom = val
        self.config_changed.emit()

    def _on_offset_x(self, val):
        self._config.offset_x = val
        self.config_changed.emit()

    def _on_offset_y(self, val):
        self._config.offset_y = val
        self.config_changed.emit()

    def _on_bg_colour(self, text):
        self._config.background_color = text
        self.config_changed.emit()
