from __future__ import annotations

import copy
from dataclasses import fields
from typing import Callable, Dict, Optional, TYPE_CHECKING

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
            title="Style",
            baseline_config=None,
            parent=parent,
        )

    def _build_content(self) -> None:
        self._picker_widgets: Dict[str, ColorPickerRow] = {}

        # ── Preset selector ───────────────────────────────────────
        self._preset_combo = self._add_combo(
            "Preset",
            ["Custom"] + list(PRESETS.keys()),
            "Auto",
            self._on_preset_changed,
            help="Select a pre-built color scheme. When you edit a color, "
            "this automatically switches to 'Custom'.",
        )

        # Block signals to avoid premature _on_preset_changed
        self._preset_combo.blockSignals(True)
        initial_preset = self._find_matching_preset()
        self._preset_combo.setCurrentText(initial_preset)
        self._preset_combo.blockSignals(False)

        # ── Color pickers for every palette field ────────────────
        for field in fields(GUIPalette):
            name = field.name
            label = name.replace("_", " ").title()
            value = normalize_to_hex(getattr(self._palette, name))
            picker = self._add_color_picker(
                label,
                value,
                self._make_color_slot(name),
                help=f"Set the {label.lower()} color.",
            )
            self._picker_widgets[name] = picker

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
            self._picker_widgets[field.name].set_color(getattr(preset, field.name))
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

    def _apply_clicked(self) -> None:
        """Persist the palette and rebuild the GUI."""
        stylesheet_palette = self._palette_to_stylesheet(self._palette)
        self._saved_palette = copy.deepcopy(self._palette)
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
        self._notify_dirty()

    def _restore_auto_preset(self) -> None:
        """Load the Auto preset without applying."""
        preset = PRESETS["Auto"]
        self._palette = self._palette_to_internal(preset)
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            self._picker_widgets[field.name].set_color(getattr(preset, field.name))
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
