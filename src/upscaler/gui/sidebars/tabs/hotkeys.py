from __future__ import annotations

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..sidebar import SettingsTab
from ....utils import HOTKEY_GROUPS

if TYPE_CHECKING:
    from ..controls import HotkeyRow
    from ...config import GUIConfig
    from ....config import Config


class HotkeysTab(SettingsTab):
    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        global_baseline: Config,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._hotkey_rows: Dict[str, HotkeyRow] = {}
        super().__init__(
            gui_config,
            title=self.tr("Hotkeys", "Name of a settings tab"),
            config=config,
            baseline_config=baseline_config,
            global_baseline=global_baseline,
            parent=parent,
        )

    def _hotkey_group_titles(self) -> Dict[str, str]:
        """Return translated titles for each hotkey group key."""
        return {
            "session": self.tr("Session", "Hotkey group title"),
            "view": self.tr("View", "Hotkey group title"),
            "zooming": self.tr("Zooming", "Hotkey group title"),
            "panning": self.tr("Panning", "Hotkey group title"),
        }

    def _hotkey_action_labels(self) -> Dict[str, Tuple[str, str]]:
        """Return translated ``(label, tooltip)`` pairs per hotkey action."""
        return {
            "toggle_scaling": (
                self.tr("Toggle overlay", "Hotkey action label"),
                self.tr(
                    "Show or hide the upscaled overlay window.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "exit_app": (
                self.tr("Exit session", "Hotkey action label"),
                self.tr(
                    "Close the overlay and end the current upscaling session.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "screenshot": (
                self.tr("Take screenshot", "Hotkey action label"),
                self.tr(
                    "Save the current upscaled output as an image.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "cycle_model": (
                self.tr("Cycle model", "Hotkey action label"),
                self.tr(
                    "Switch to the next SRCNN upscaling model.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "cycle_geometry": (
                self.tr("Cycle geometry", "Hotkey action label"),
                self.tr(
                    "Cycle through output sizing modes (fit, stretch, cover).",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "restore_view": (
                self.tr("Restore view", "Hotkey action label"),
                self.tr(
                    "Reset geometry, zoom and pan offsets to their initial values.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "zoom_in": (
                self.tr("Zoom in", "Hotkey action label"),
                self.tr(
                    "Increase the output zoom level.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "zoom_out": (
                self.tr("Zoom out", "Hotkey action label"),
                self.tr(
                    "Decrease the output zoom level.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "offset_left": (
                self.tr("Pan left", "Hotkey action label"),
                self.tr(
                    "Move the content to the left.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "offset_right": (
                self.tr("Pan right", "Hotkey action label"),
                self.tr(
                    "Move the content to the right.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "offset_up": (
                self.tr("Pan up", "Hotkey action label"),
                self.tr(
                    "Move the content up.",
                    "Hotkey action description (tooltip)",
                ),
            ),
            "offset_down": (
                self.tr("Pan down", "Hotkey action label"),
                self.tr(
                    "Move the content down.",
                    "Hotkey action description (tooltip)",
                ),
            ),
        }

    def _build_content(self) -> None:
        # ---- Hotkeys ----
        group_titles = self._hotkey_group_titles()
        action_labels = self._hotkey_action_labels()
        for group_key, actions in HOTKEY_GROUPS:
            self._add_section(group_titles.get(group_key, group_key.capitalize()))
            for action in actions:
                label, tooltip = action_labels[action]
                row = self._add_hotkey(
                    label,
                    self._config.hotkeys.get(action, ""),
                    lambda seq, a=action: self._on_hotkey_changed(a, seq),
                    baseline=self.baseline_config.hotkeys.get(action, ""),
                    help=tooltip,
                )
                self._hotkey_rows[action] = row

        self._validate_hotkeys()

    def _on_hotkey_changed(self, action: str, sequence: str) -> None:
        """
        Record a new sequence for *action*.

        An empty string is kept in the dict on purpose: it means
        "explicitly disabled", so the manager skips the grab and the
        default does not resurface on the next load.
        """
        self._config.hotkeys[action] = sequence
        self._validate_hotkeys()
        self.config_changed.emit()

    def _validate_hotkeys(self) -> None:
        """Flag every row whose sequence collides with another row."""
        users: Dict[str, List[str]] = {}
        for action, row in self._hotkey_rows.items():
            seq = row.sequence()
            if seq:
                users.setdefault(seq, []).append(action)

        for action, row in self._hotkey_rows.items():
            seq = row.sequence()
            row.set_conflict(bool(seq) and len(users[seq]) > 1)
