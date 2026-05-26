from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

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
        parent: Optional[QWidget] = None,
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

        # ---- Overlay ----
        self._add_section("Overlay")
        self._overlay_combo = self._add_combo(
            "Mode",
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

    def _on_monitor_changed(self, text: str):
        self._config.monitor = text
        self.config_changed.emit()

    def _on_auto_scale_changed(self, state: bool) -> None:
        auto = state
        self._scale_slider.setEnabled(not auto)
        if auto:
            self._config.scale_factor = None
        else:
            # When disabled, set the config to the current slider value
            self._config.scale_factor = self._scale_slider.value() / 100.0
        self.config_changed.emit()

    def _on_scale_slider_changed(self, value: float) -> None:
        if self._scale_slider.isEnabled():
            self._config.scale_factor = value
            self.config_changed.emit()

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
