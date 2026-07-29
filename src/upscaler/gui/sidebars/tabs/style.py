from __future__ import annotations

import copy
from dataclasses import fields
from typing import Callable, Dict, Optional, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from ..common import SettingsTab
from ..controls import normalize_to_hex
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
        self._palette = copy.deepcopy(initial_palette)
        self._saved_palette = copy.deepcopy(initial_palette)
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
            help="Select a pre‑built color scheme. When you edit a color, "
            "this automatically switches to 'Custom'.",
        )

        # Block signals to prevent _on_preset_changed from running prematurely
        self._preset_combo.blockSignals(True)
        initial_preset = self._find_matching_preset()
        self._preset_combo.setCurrentText(initial_preset)
        self._preset_combo.blockSignals(False)

        # Determine initial preset (match the palette to a known preset)
        initial_preset = self._find_matching_preset()
        self._preset_combo.setCurrentText(initial_preset)

        # ── color pickers for every palette field ────────────────
        for field in fields(GUIPalette):
            name = field.name
            label = name.replace("_", " ").title()
            value = normalize_to_hex(getattr(self._saved_palette, name))
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
        self._palette = copy.deepcopy(preset)
        for field in fields(GUIPalette):
            hex_color = normalize_to_hex(getattr(preset, field.name))
            self._picker_widgets[field.name].set_color(hex_color)
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

    def _find_matching_preset(self) -> str:
        """Return the name of the preset that exactly matches the current palette, or 'Custom'."""
        for preset_name, preset_palette in PRESETS.items():
            match = True
            for field in fields(GUIPalette):
                if getattr(preset_palette, field.name) != getattr(
                    self._palette, field.name
                ):
                    match = False
                    break
            if match:
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
        """Persist the palette and trigger the main window to rebuild its UI."""
        stylesheet_palette = GUIPalette(
            **{
                field.name: self._to_stylesheet_color(
                    getattr(self._palette, field.name)
                )
                for field in fields(GUIPalette)
            }
        )
        self._saved_palette = copy.deepcopy(self._palette)
        self._on_apply(stylesheet_palette)
        self.style_apply.emit()
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
        """Load the Auto preset (but do NOT apply it automatically)."""
        preset = PRESETS["Auto"]
        self._palette = copy.deepcopy(preset)
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            hex_color = normalize_to_hex(getattr(self._palette, field.name))
            self._picker_widgets[field.name].set_color(hex_color)
        self._updating_from_preset = False
        self._preset_combo.setCurrentText("Auto")
        self._notify_dirty()

    def _notify_dirty(self) -> None:
        """Emit the current dirty state (call after any change)."""
        self.style_dirty_changed.emit(self.is_dirty())

    @staticmethod
    def _to_stylesheet_color(any_color: str) -> str:
        """Convert a color (e.g., #RRGGBBAA) to a Qt‑stylesheet‑compatible format."""
        qc = QColor(any_color)
        if not qc.isValid():
            return "#000000"
        if qc.alpha() == 255:
            return qc.name(QColor.HexRgb)  # "#RRGGBB"
        else:
            return qc.name(QColor.HexArgb)  # "#AARRGGBB"
