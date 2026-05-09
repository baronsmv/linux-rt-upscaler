from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab
from ..controls import ComboRow

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class CaptureTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "Capture", parent)

    def _build_content(self) -> None:
        self._add_section("Focus Tracking")
        self._follow_focus_cb = self._add_cb(
            "Follow Focus", self._config.follow_focus, self._on_follow_focus
        )
        self._pause_focus_loss_cb = self._add_cb(
            "Pause on Focus Loss",
            self._config.pause_on_focus_loss,
            self._on_pause_focus_loss,
        )
        self._focus_poll = self._add_slider(
            "Focus Poll Interval (ms)",
            50,
            2000,
            int(self._config.focus_poll_interval * 1000),
            self._on_focus_poll,
            show_val=True,
        )

        self._add_section("Window Detection")
        self._target_delay = self._add_slider(
            "Target Delay (s)",
            0,
            30,
            self._config.target_delay,
            self._on_target_delay,
            show_val=True,
        )
        self._pid_timeout = self._add_slider(
            "PID Timeout (s)",
            0,
            60,
            self._config.pid_timeout,
            self._on_pid_timeout,
            show_val=True,
        )
        self._class_timeout = self._add_slider(
            "Class Timeout (s)",
            0,
            60,
            self._config.class_timeout,
            self._on_class_timeout,
            show_val=True,
        )
        self._total_timeout = self._add_slider(
            "Total Timeout (s)",
            0,
            120,
            self._config.total_timeout,
            self._on_total_timeout,
            show_val=True,
        )
        self._starting_phase_combo = ComboRow(
            "Starting Phase",
            self.gui_config,
            ["1", "2"],
            str(self._config.starting_phase),
        )
        self._starting_phase_combo.currentTextChanged.connect(self._on_starting_phase)
        self.content_layout.addWidget(self._starting_phase_combo)

    def _on_follow_focus(self, state):
        self._config.follow_focus = bool(state)
        self.config_changed.emit()

    def _on_pause_focus_loss(self, state):
        self._config.pause_on_focus_loss = bool(state)
        self.config_changed.emit()

    def _on_focus_poll(self, val):
        self._config.focus_poll_interval = max(0.05, val / 1000.0)
        self.config_changed.emit()

    def _on_target_delay(self, val):
        self._config.target_delay = max(0, val)
        self.config_changed.emit()

    def _on_pid_timeout(self, val):
        self._config.pid_timeout = max(0, val)
        self.config_changed.emit()

    def _on_class_timeout(self, val):
        self._config.class_timeout = max(0, val)
        self.config_changed.emit()

    def _on_total_timeout(self, val):
        self._config.total_timeout = max(0, val)
        self.config_changed.emit()

    def _on_starting_phase(self, text):
        self._config.starting_phase = int(text)
        self.config_changed.emit()
