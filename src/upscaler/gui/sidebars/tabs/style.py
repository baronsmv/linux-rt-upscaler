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
    COLOR_CATEGORIES: List[Dict[str, Union[str, List[Tuple[str, str, str]]]]] = [
        {
            "title": "Background & Surfaces",
            "fields": [
                (
                    "background",
                    "Primary Background",
                    "Main background color of the application window and dialogs.",
                ),
                (
                    "input",
                    "Input Background",
                    "Background color of text fields, combo boxes, and editable areas.",
                ),
                (
                    "input_hover",
                    "Input Background (hover)",
                    "Background color when the mouse hovers over an input field.",
                ),
                (
                    "input_disabled",
                    "Input Background (disabled)",
                    "Background color for disabled (greyed-out) input fields.",
                ),
                (
                    "button",
                    "Button Background",
                    "Background color of buttons.",
                ),
                (
                    "button_hover",
                    "Button Background (hover)",
                    "Background color of a button when the mouse hovers over it.",
                ),
                (
                    "caption_background",
                    "Caption Background",
                    "Semi-transparent background color of each window titles.",
                ),
            ],
        },
        {
            "title": "Text & Icons",
            "fields": [
                (
                    "text",
                    "Primary Text",
                    "Text color of body text and labels.",
                ),
                (
                    "text_hover",
                    "Primary Text (hover)",
                    "Text color when the mouse hovers over clickable items.",
                ),
                (
                    "text_subtle",
                    "Secondary Text",
                    "Text color for secondary information, captions, and section headers.",
                ),
                (
                    "icon",
                    "Icon Fill",
                    "Fill color of sidebar and toolbar icons.",
                ),
            ],
        },
        {
            "title": "Borders & Separators",
            "fields": [
                (
                    "border",
                    "Border",
                    "Border color for input fields, buttons, and panels.",
                ),
                (
                    "border_hover",
                    "Border (hover)",
                    "Border color when hovering over interactive elements.",
                ),
            ],
        },
        {
            "title": "Controls & Highlights",
            "fields": [
                (
                    "control",
                    "Accent",
                    "Primary accent color for checkboxes, sliders and other interactive controls.",
                ),
                (
                    "control_hover",
                    "Accent (hover)",
                    "Accent color when the mouse hovers over an interactive control.",
                ),
                (
                    "reset",
                    "Revert Button",
                    "Background color of the 'Reset' button.",
                ),
                (
                    "reset_hover",
                    "Revert Button (hover)",
                    "'Reset' button background color on hover.",
                ),
                (
                    "handle",
                    "Handle",
                    "Fill color of scrollbar handles and subtle interactive areas.",
                ),
                (
                    "handle_hover",
                    "Handle (hover)",
                    "Handle control fill color on hover.",
                ),
            ],
        },
    ]

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
            title="GUI Style",
            baseline_config=None,
            parent=parent,
        )

    def _build_content(self) -> None:
        self._picker_widgets: Dict[str, ColorPickerRow] = {}

        # ── Preset selector ───────────────────────────────────────
        self._add_section("Palette Preset")
        self._preset_combo = self._add_combo(
            "Preset",
            ["Custom"] + list(PRESETS.keys()),
            "Auto",
            self._on_preset_changed,
            help="Select a pre-built color scheme for the GUI.",
        )

        # Block signals to avoid premature _on_preset_changed
        self._preset_combo.blockSignals(True)
        initial_preset = find_matching_preset(palette_to_stylesheet(self._palette))
        self._preset_combo.setCurrentText(initial_preset)
        self._preset_combo.blockSignals(False)

        # ── Grouped color pickers ─────────────────────────────────
        for category in self.COLOR_CATEGORIES:
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
