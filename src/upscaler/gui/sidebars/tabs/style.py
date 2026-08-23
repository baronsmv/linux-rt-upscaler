from __future__ import annotations

import copy
from dataclasses import fields
from typing import Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ...config import GUIPalette, PRESETS
from ...utils import (
    find_matching_preset,
    normalize_to_hex,
    palette_to_internal,
    palette_to_stylesheet,
)

if TYPE_CHECKING:
    from ..controls import ColorPickerRow
    from ...config import GUIConfig


class StyleTab(SettingsTab):
    """Tab to customize the GUI color palette, stored in a separate YAML file."""

    style_dirty_changed = Signal(bool)

    def __init__(
        self,
        gui_config: GUIConfig,
        initial_palette: GUIPalette,
        on_apply: Callable[[GUIPalette], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        self._palette = palette_to_internal(initial_palette)
        self._saved_palette = copy.deepcopy(self._palette)
        self._on_apply = on_apply
        self._updating_from_preset = False
        super().__init__(
            gui_config,
            title=self.tr("GUI Style", "Name of a settings tab"),
            baseline_config=None,
            parent=parent,
        )

    # ------------------------------------------------------------------
    #  Translated color categories
    # ------------------------------------------------------------------
    def _get_color_categories(
        self,
    ) -> List[Dict[str, Union[str, List[Tuple[str, str, str]]]]]:
        """Return the color category structure with translated strings."""
        return [
            {
                "title": self.tr("Background & Surfaces", "Settings section"),
                "fields": [
                    (
                        "background",
                        self.tr(
                            "Primary Background", "Label of setting (must be short)"
                        ),
                        self.tr(
                            "Main background color of the application window and dialogs.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "input",
                        self.tr("Input Background", "Label of setting (must be short)"),
                        self.tr(
                            "Background color of text fields, combo boxes, and editable areas.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "input_hover",
                        self.tr(
                            "Input Background (hover)",
                            "Label of setting (must be short)",
                        ),
                        self.tr(
                            "Background color when the mouse hovers over an input field.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "input_disabled",
                        self.tr(
                            "Input Background (disabled)",
                            "Label of setting (must be short)",
                        ),
                        self.tr(
                            "Background color for disabled (greyed-out) input fields.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "button",
                        self.tr(
                            "Button Background", "Label of setting (must be short)"
                        ),
                        self.tr(
                            "Background color of buttons.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "button_hover",
                        self.tr(
                            "Button Background (hover)",
                            "Label of setting (must be short)",
                        ),
                        self.tr(
                            "Background color of a button when the mouse hovers over it.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "caption_background",
                        self.tr(
                            "Caption Background", "Label of setting (must be short)"
                        ),
                        self.tr(
                            "Semi-transparent background color of each window titles.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                ],
            },
            {
                "title": self.tr("Text & Icons", "Settings section"),
                "fields": [
                    (
                        "text",
                        self.tr("Primary Text", "Label of setting (must be short)"),
                        self.tr(
                            "Text color of body text and labels.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "text_hover",
                        self.tr(
                            "Primary Text (hover)", "Label of setting (must be short)"
                        ),
                        self.tr(
                            "Text color when the mouse hovers over clickable items.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "text_subtle",
                        self.tr("Secondary Text", "Label of setting (must be short)"),
                        self.tr(
                            "Text color for secondary information, captions, and section headers.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "icon",
                        self.tr("Icon Fill", "Label of setting (must be short)"),
                        self.tr(
                            "Fill color of sidebar and toolbar icons.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                ],
            },
            {
                "title": self.tr("Borders & Separators", "Settings section"),
                "fields": [
                    (
                        "border",
                        self.tr("Border", "Label of setting (must be short)"),
                        self.tr(
                            "Border color for input fields, buttons, and panels.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "border_hover",
                        self.tr("Border (hover)", "Label of setting (must be short)"),
                        self.tr(
                            "Border color when hovering over interactive elements.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                ],
            },
            {
                "title": self.tr("Controls & Highlights", "Settings section"),
                "fields": [
                    (
                        "control",
                        self.tr("Accent", "Label of setting (must be short)"),
                        self.tr(
                            "Primary accent color for checkboxes, sliders and other interactive controls.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "control_hover",
                        self.tr("Accent (hover)", "Label of setting (must be short)"),
                        self.tr(
                            "Accent color when the mouse hovers over an interactive control.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "reset",
                        self.tr("Revert Button", "Label of setting (must be short)"),
                        self.tr(
                            "Background color of the 'Reset' button.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "reset_hover",
                        self.tr(
                            "Revert Button (hover)", "Label of setting (must be short)"
                        ),
                        self.tr(
                            "'Reset' button background color on hover.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "handle",
                        self.tr("Handle", "Label of setting (must be short)"),
                        self.tr(
                            "Fill color of scrollbar handles and subtle interactive areas.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "handle_hover",
                        self.tr("Handle (hover)", "Label of setting (must be short)"),
                        self.tr(
                            "Handle control fill color on hover.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                ],
            },
        ]

    # ------------------------------------------------------------------
    #  UI construction
    # ------------------------------------------------------------------
    def _build_content(self) -> None:
        self._picker_widgets: Dict[str, ColorPickerRow] = {}

        # ── Preset selector ───────────────────────────────────────
        self._add_section(self.tr("Palette Preset", "Settings section"))
        self._preset_combo = self._add_combo(
            self.tr("Preset", "Label of setting (must be short)"),
            ["Custom"] + list(PRESETS.keys()),
            "Auto",
            self._on_preset_changed,
            help=self.tr(
                "Select a pre-built color scheme for the GUI.",
                "Description of a setting (tooltip)",
            ),
        )

        # Block signals to avoid premature _on_preset_changed
        self._preset_combo.blockSignals(True)
        initial_preset = find_matching_preset(palette_to_stylesheet(self._palette))
        self._preset_combo.setCurrentText(initial_preset)
        self._preset_combo.blockSignals(False)

        # ── Grouped color pickers ─────────────────────────────────
        for category in self._get_color_categories():
            self._add_section(str(category["title"]))
            for field_name, label, tooltip in category["fields"]:
                picker = self._add_color_picker(
                    label,
                    normalize_to_hex(getattr(self._palette, field_name)),
                    self._make_color_slot(field_name),
                    baseline=normalize_to_hex(getattr(self._saved_palette, field_name)),
                    help=tooltip,
                )
                self._picker_widgets[field_name] = picker

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_preset_changed(self, text: str) -> None:
        if text == "Custom" or self._updating_from_preset:
            return
        preset_name = text if text != "Auto" else "Auto"
        preset = PRESETS.get(preset_name, PRESETS["Auto"])
        self._updating_from_preset = True
        self._palette = palette_to_internal(preset)

        # Update all swatches with the internal color values
        for field in fields(GUIPalette):
            self._picker_widgets[field.name].set_color(
                getattr(self._palette, field.name)
            )
        self._updating_from_preset = False
        self._notify_dirty()

    def _make_color_slot(self, field_name: str):
        """Return a slot that records manual color changes and updates 'Custom'."""

        def slot(value: str) -> None:
            setattr(self._palette, field_name, value)
            if not self._updating_from_preset:
                self._preset_combo.setCurrentText("Custom")
            self._notify_dirty()

        return slot

    def is_dirty(self) -> bool:
        """Return True if the current palette differs from the last applied one."""
        for field in fields(GUIPalette):
            if getattr(self._palette, field.name) != getattr(
                self._saved_palette, field.name
            ):
                return True
        return False

    def is_default(self) -> bool:
        """Return True if the current palette matches the Auto preset."""
        return find_matching_preset(palette_to_stylesheet(self._palette)) == "Auto"

    def _refresh_baselines(self) -> None:
        """Update every picker’s baseline to the current saved palette."""
        for field in fields(GUIPalette):
            name = field.name
            baseline_hex = normalize_to_hex(getattr(self._saved_palette, name))
            self._picker_widgets[name].set_baseline(baseline_hex)

    def apply_clicked(self) -> None:
        """Persist the palette and rebuild the GUI."""
        self._saved_palette = copy.deepcopy(self._palette)
        self._refresh_baselines()
        self._on_apply(palette_to_stylesheet(self._palette))
        self._notify_dirty()

    def reset_style(self) -> None:
        """Revert all fields to the last applied palette."""
        self._palette = copy.deepcopy(self._saved_palette)
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            hex_color = normalize_to_hex(getattr(self._palette, field.name))
            self._picker_widgets[field.name].set_color(hex_color)
        self._updating_from_preset = False
        self._preset_combo.setCurrentText(
            find_matching_preset(palette_to_stylesheet(self._palette))
        )
        self._refresh_baselines()
        self._notify_dirty()

    def restore_auto_preset(self) -> None:
        """Load the Auto preset without applying."""
        preset = PRESETS["Auto"]
        self._palette = palette_to_internal(preset)
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            self._picker_widgets[field.name].set_color(
                getattr(self._palette, field.name)
            )
        self._updating_from_preset = False
        self._preset_combo.setCurrentText("Auto")
        self._notify_dirty()

    def _notify_dirty(self) -> None:
        """Emit the current dirty state (call after any change)."""
        self.style_dirty_changed.emit(self.is_dirty())
