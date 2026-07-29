from __future__ import annotations

from dataclasses import fields
from typing import Callable, Dict, Optional, TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ..common import SettingsTab
from ..controls import normalize_to_hex
from ...config import GUIPalette, PRESETS

if TYPE_CHECKING:
    from ..controls import ColorPickerRow
    from ...config import GUIConfig


class StyleTab(SettingsTab):
    """Tab to customize the GUI color palette, stored in a separate YAML file."""

    def __init__(
        self,
        gui_config: GUIConfig,
        initial_palette: GUIPalette,
        on_apply: Callable[[GUIPalette], None],
        parent: Optional[QWidget] = None,
    ) -> None:
        self._palette = initial_palette
        self._on_apply = on_apply
        self._updating_from_preset = False  # guard against recursion
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

        # Determine initial preset (match the palette to a known preset)
        initial_preset = self._find_matching_preset()
        self._preset_combo.setCurrentText(initial_preset)

        # ── color pickers for every palette field ────────────────
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

        # ── Apply button (at the bottom of the tab) ───────────────
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()
        self._apply_btn = QPushButton("Apply Style")
        self._apply_btn.clicked.connect(self._apply_clicked)
        apply_layout.addWidget(self._apply_btn)
        self.content_layout.addLayout(apply_layout)

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_preset_changed(self, text: str) -> None:
        if text == "Custom" or self._updating_from_preset:
            return
        preset_name = text if text != "Auto" else "Auto"
        preset = PRESETS.get(preset_name, PRESETS["Auto"])
        self._updating_from_preset = True
        for field in fields(GUIPalette):
            color = getattr(preset, field.name)
            hex_color = normalize_to_hex(color)
            self._picker_widgets[field.name].setText(hex_color)  # update the UI
            setattr(self._palette, field.name, color)  # update internal
        self._updating_from_preset = False

    def _make_color_slot(self, field_name: str):
        """Return a slot that records manual color changes and updates 'Custom'."""

        def slot(value: str) -> None:
            # Update internal palette
            setattr(self._palette, field_name, value)
            # Switch preset to Custom (unless we're already in a preset load)
            if not self._updating_from_preset:
                self._preset_combo.setCurrentText("Custom")

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

    def _apply_clicked(self) -> None:
        """Save the palette to disk and trigger the main window to rebuild its UI."""
        self._on_apply(self._palette)
