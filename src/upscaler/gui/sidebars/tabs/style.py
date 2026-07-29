from __future__ import annotations

import copy
from dataclasses import fields
from typing import Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ..controls import normalize_to_hex, qcolor_to_rgba_hex, rgba_hex_to_qcolor
from ...config import GUIPalette, PRESETS

if TYPE_CHECKING:
    from ..controls import ColorPickerRow
    from ...config import GUIConfig


class StyleTab(SettingsTab):
    """Tab to customize the GUI color palette, stored in a separate YAML file."""

    style_dirty_changed = Signal(bool)

    # ------------------------------------------------------------------
    #  Declarative color layout
    # ------------------------------------------------------------------
    # Each category is a section heading + a list of (field_name, label, tooltip).
    # All field names must match GUIPalette attributes exactly.
    COLOR_CATEGORIES: List[Dict[str, Union[str, List[Tuple[str, str, str]]]]] = [
        {
            "title": "Background & Surfaces",
            "fields": [
                (
                    "background",
                    "Window Background",
                    "Main background of the application window and dialogs.",
                ),
                (
                    "input",
                    "Input Background",
                    "Background of text fields, combo boxes, and editable areas.",
                ),
                (
                    "input_hover",
                    "Input Background (hover)",
                    "Background when the mouse hovers over an input field.",
                ),
                (
                    "input_disabled",
                    "Input Background (disabled)",
                    "Background for disabled (greyed-out) input fields.",
                ),
                (
                    "button",
                    "Button Background",
                    "Default background of push buttons.",
                ),
                (
                    "button_hover",
                    "Button Background (hover)",
                    "Background of a button when the mouse hovers over it.",
                ),
                (
                    "text_pillbox",
                    "Tile Caption Background",
                    "Semi-transparent overlay text (used in tile captions).",
                ),
            ],
        },
        {
            "title": "Text & Icons",
            "fields": [
                (
                    "text",
                    "Primary Text",
                    "Color of body text and control labels.",
                ),
                (
                    "text_hover",
                    "Primary Text (hover)",
                    "Text color when the mouse hovers over clickable items.",
                ),
                (
                    "text_subtle",
                    "Secondary Text",
                    "Used for secondary information, captions, and section headers.",
                ),
                (
                    "icon",
                    "Icon Fill",
                    "Color of sidebar icons, toolbar icons, and glyphs.",
                ),
            ],
        },
        {
            "title": "Borders & Separators",
            "fields": [
                (
                    "border",
                    "Border",
                    "Default border color for input fields, buttons, and panels.",
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
                    "Primary accent for checkboxes, selected items, sliders, and focused borders.",
                ),
                (
                    "control_hover",
                    "Accent (hover)",
                    "Accent color when the mouse hovers over an interactive control.",
                ),
                (
                    "button_revert",
                    "Revert Button",
                    "Background of the 'Revert' button when changes are present.",
                ),
                (
                    "button_revert_hover",
                    "Revert Button (hover)",
                    "Revert button background on hover.",
                ),
                (
                    "control_subtle",
                    "Handle",
                    "Background of scrollbar handles and subtle interactive areas.",
                ),
                (
                    "control_subtle_hover",
                    "Handle (hover)",
                    "Subtle control background on hover.",
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
        self._palette = self._palette_to_internal(initial_palette)
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
        initial_preset = self._find_matching_preset()
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

        # Convert preset to internal format and store
        self._palette = self._palette_to_internal(preset)

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

    @staticmethod
    def _normalized_color(color: str) -> str:
        """Convert any valid CSS color string to a normalized representation."""
        qc = QColor(color)
        if not qc.isValid():
            return color.lower()
        if qc.alpha() == 255:
            return qc.name(QColor.HexRgb).lower()  # "#rrggbb"
        else:
            return qc.name(QColor.HexArgb).lower()  # "#aarrggbb"

    def _find_matching_preset(self) -> str:
        """Compare current palette (internal) against all presets."""
        sheet = self._palette_to_stylesheet(self._palette)
        for preset_name, preset_palette in PRESETS.items():
            if all(
                self._normalized_color(getattr(preset_palette, f.name))
                == self._normalized_color(getattr(sheet, f.name))
                for f in fields(GUIPalette)
            ):
                return preset_name
        return "Custom"

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
        return self._find_matching_preset() == "Auto"

    def _refresh_baselines(self) -> None:
        """Update every picker’s baseline to the current saved palette."""
        for field in fields(GUIPalette):
            name = field.name
            baseline_hex = normalize_to_hex(getattr(self._saved_palette, name))
            self._picker_widgets[name].set_baseline(baseline_hex)

    def _apply_clicked(self) -> None:
        """Persist the palette and rebuild the GUI."""
        stylesheet_palette = self._palette_to_stylesheet(self._palette)
        self._saved_palette = copy.deepcopy(self._palette)
        self._refresh_baselines()
        self._on_apply(stylesheet_palette)
        self._notify_dirty()

    def _reset_style(self) -> None:
        """Revert all fields to the last applied palette."""
        self._palette = copy.deepcopy(self._saved_palette)
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            hex_color = normalize_to_hex(getattr(self._palette, field.name))
            self._picker_widgets[field.name].set_color(hex_color)
        self._updating_from_preset = False
        self._preset_combo.setCurrentText(self._find_matching_preset())
        self._refresh_baselines()
        self._notify_dirty()

    def _restore_auto_preset(self) -> None:
        """Load the Auto preset without applying."""
        preset = PRESETS["Auto"]
        self._palette = self._palette_to_internal(preset)
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

    # ------------------------------------------------------------------
    #  Format conversion helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _to_stylesheet_color(internal_color: str) -> str:
        """Convert any valid CSS color to a Qt-stylesheet-compatible string."""
        qc = rgba_hex_to_qcolor(internal_color)
        if not qc.isValid():
            return ""
        if qc.alpha() == 255:
            return qc.name(QColor.HexRgb)  # "#RRGGBB"
        else:
            return qc.name(QColor.HexArgb)  # "#AARRGGBB"

    @staticmethod
    def _preset_color_to_internal(stylesheet_color: str) -> str:
        """
        Convert a stylesheet color (preset or saved YAML) to internal #RRGGBBAA.
        Presets use #RRGGBB, #AARRGGBB, or named colors – all correctly parsed
        by QColor's constructor.
        """
        qc = QColor(stylesheet_color)
        if not qc.isValid():
            return ""
        return qcolor_to_rgba_hex(qc)

    @staticmethod
    def _palette_to_internal(pal: GUIPalette) -> GUIPalette:
        """Convert a whole stylesheet palette to internal format."""
        return GUIPalette(
            **{
                f.name: StyleTab._preset_color_to_internal(getattr(pal, f.name))
                for f in fields(GUIPalette)
            }
        )

    @staticmethod
    def _palette_to_stylesheet(pal: GUIPalette) -> GUIPalette:
        """Convert a whole internal palette to stylesheet format."""
        return GUIPalette(
            **{
                f.name: StyleTab._to_stylesheet_color(getattr(pal, f.name))
                for f in fields(GUIPalette)
            }
        )
