from __future__ import annotations

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ....utils import HOTKEY_GROUPS

if TYPE_CHECKING:
    from ..controls import HotkeyRow
    from ...config import GUIConfig
    from ....config import Config


class ExtrasTab(SettingsTab):
    def __init__(
        self,
        gui_config: GUIConfig,
        config: Config,
        baseline_config: Config,
        parent: Optional[QWidget] = None,
    ) -> None:
        self._config = config
        self._hotkey_rows: Dict[str, HotkeyRow] = {}
        super().__init__(
            gui_config,
            title=self.tr("Extras", "Name of a settings tab"),
            baseline_config=baseline_config,
            parent=parent,
        )

    def _hotkey_group_titles(self) -> Dict[str, str]:
        """Return translated titles for each hotkey group key."""
        return {
            "session": self.tr("Session Hotkeys", "Hotkey group title"),
            "view": self.tr("View Hotkeys", "Hotkey group title"),
            "zooming": self.tr("Zooming Hotkeys", "Hotkey group title"),
            "panning": self.tr("Panning Hotkeys", "Hotkey group title"),
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
        # ---- Screenshot Location ----
        self._add_section(self.tr("Screenshot Location", "Settings section"))
        self._dir_picker = self._add_path_picker(
            self.tr("Directory", "Label of setting (must be short)"),
            self._config.screenshot_dir,
            self._on_dir_changed,
            baseline=self.baseline_config.screenshot_dir,
            help=self.tr(
                "Folder where screenshots are saved.",
                "Description of a setting (tooltip)",
            ),
        )
        self._file_input = self._add_text(
            self.tr("Template", "Label of setting (must be short)"),
            self._config.screenshot_filename,
            self._on_file_changed,
            baseline=self.baseline_config.screenshot_filename,
            help=self.tr(
                "Filename template for screenshots. You can use these placeholders:\n"
                "• {timestamp}: capture time (supports strftime, for example "
                "{timestamp:%Y-%m-%d-%H-%M-%S})\n"
                "• {title}: current window title\n"
                "• {profile}: active profile name (or the window title if no profile)\n"
                "• {model}: active upscaling model\n"
                "• {width}: upscaled image width\n"
                "• {height}: upscaled image height",
                "Description of a setting (tooltip). "
                "Keep all placeholders exactly as they are, including braces, "
                "for example {timestamp} and the strftime format inside it.",
            ),
        )

        # ---- On-Screen Display ----
        self._add_section(self.tr("On-Screen Display", "Settings section"))
        self._osd_enabled = self._add_cb(
            self.tr("Show OSD", "Label of setting (must be short)"),
            self._config.show_osd,
            self._on_osd_enabled,
            baseline=self.baseline_config.show_osd,
            help=self.tr(
                "Show on-screen messages when the model, window geometry, or zoom changes, "
                "or after taking a screenshot.",
                "Description of a setting (tooltip)",
            ),
        )
        self._osd_duration = self._add_slider(
            self.tr("Duration (s)", "Label of setting (must be short)"),
            1,
            1000,
            int(self._config.osd_duration * 100),
            scale_factor=100,
            float_slot=self._on_osd_duration,
            baseline=self.baseline_config.osd_duration,
            help=self.tr(
                "How many seconds on-screen messages remain visible before fading out.",
                "Description of a setting (tooltip)",
            ),
        )
        self._osd_duration.setEnabled(self._config.show_osd)

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

    def _on_dir_changed(self, path: str) -> None:
        self._config.screenshot_dir = path
        self.config_changed.emit()

    def _on_file_changed(self, text: str) -> None:
        self._config.screenshot_filename = text
        self.config_changed.emit()

    def _on_osd_enabled(self, state: int):
        enabled = bool(state)
        self._config.show_osd = enabled
        self._osd_duration.setEnabled(enabled)
        self.config_changed.emit()

    def _on_osd_duration(self, value: float):
        self._config.osd_duration = value
        self.config_changed.emit()
