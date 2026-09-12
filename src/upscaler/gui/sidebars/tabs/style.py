from __future__ import annotations

import copy
from dataclasses import fields
from typing import Callable, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from ..sidebar import SettingsTab
from ...config import (
    GUIPalette,
    GUIStyleOverrides,
    PRESETS,
    find_matching_preset,
    palette_to_internal,
    palette_to_stylesheet,
)
from ...utils import normalize_to_hex

if TYPE_CHECKING:
    from ..controls import ColorPickerRow
    from ...config import GUIConfig

_ASPECT_RATIOS: Tuple[Tuple[str, float], ...] = (
    ("1:1", 1.0),
    ("4:3", 4 / 3),
    ("16:10", 16 / 10),
    ("16:9", 16 / 9),
    ("21:9", 21 / 9),
)


def _aspect_to_name(ratio: float) -> str:
    """Return the preset name closest to *ratio*."""
    return min(_ASPECT_RATIOS, key=lambda item: abs(item[1] - ratio))[0]


class StyleTab(SettingsTab):
    """Tab to customize the GUI color palette, stored in a separate YAML file."""

    style_dirty_changed = Signal(bool)

    def __init__(
        self,
        gui_config: GUIConfig,
        initial: GUIStyleOverrides,
        on_apply: Callable[[GUIStyleOverrides], None],
        system_font_family: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        self._saved = initial
        self._palette = palette_to_internal(initial.palette)
        self._system_font_family = system_font_family
        self._on_apply = on_apply
        self._updating_from_preset = False

        self._zoom = initial.zoom
        self._font_family = initial.font_family
        self._profiles_width = initial.profiles_width
        self._settings_width = initial.settings_width
        self._tile_columns = initial.tile_columns
        self._tile_aspect_ratio = initial.tile_aspect_ratio
        self._auto_refresh_ms = initial.auto_refresh_ms
        self._tile_preview_interval_ms = initial.tile_preview_interval_ms

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
                            "Semi-transparent background color of the central grid window titles.",
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
                        self.tr("Reset Button", "Label of setting (must be short)"),
                        self.tr(
                            "Background color of the 'Reset' button.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "reset_hover",
                        self.tr(
                            "Reset Button (hover)", "Label of setting (must be short)"
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
                            "Fill color of scrollbar handles and other small controls.",
                            "Description of a setting (tooltip)",
                        ),
                    ),
                    (
                        "handle_hover",
                        self.tr("Handle (hover)", "Label of setting (must be short)"),
                        self.tr(
                            "Fill color of scrollbar handles when hovered.",
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

        # ── Interface scale ───────────────────────────────────────
        self._add_section(self.tr("Interface Scale", "Settings section"))
        self._zoom_slider = self._add_slider(
            self.tr("Zoom (%)", "Label of setting (must be short)"),
            50,
            400,
            self._zoom,
            self._on_zoom_changed,
            baseline=self._saved_zoom,
            help=self.tr(
                "Scales the entire interface.",
                "Description of a setting (tooltip)",
            ),
        )

        # ── Typography ────────────────────────────────────────────
        self._add_section(self.tr("Typography", "Settings section"))
        self._font_row = self._add_font_picker(
            self.tr("Font family", "Label of setting (must be short)"),
            self._font_family,
            self._system_font_family,
            self._on_font_changed,
            baseline=self._saved_font_family,
            help=self.tr(
                "Interface font. Leave at the system default for the best "
                "integration with your desktop.",
                "Description of a setting (tooltip)",
            ),
        )

        # ── Preset selector ───────────────────────────────────────
        self._add_section(self.tr("Palette Preset", "Settings section"))
        self._preset_combo = self._add_combo(
            self.tr("Preset", "Label of setting (must be short)"),
            ["Custom"] + list(PRESETS.keys()),
            "Auto",
            self._on_preset_changed,
            help=self.tr(
                "Select a pre-built color scheme for the GUI.",
                "Description of a setting (tooltip). Preset names are not translated.",
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

        # ── Sidebar ────────────────────────────────────────
        self._add_section(self.tr("Sidebars", "Settings section"))
        self._profiles_width_slider = self._add_slider(
            self.tr("Profiles sidebar width", "Label of setting (must be short)"),
            240,
            800,
            self._profiles_width,
            self._on_profiles_width_changed,
            baseline=self._saved.profiles_width,
            help=self.tr(
                "Width in pixels of the left profiles sidebar.",
                "Description of a setting (tooltip)",
            ),
        )
        self._settings_width_slider = self._add_slider(
            self.tr("Settings sidebar width", "Label of setting (must be short)"),
            240,
            800,
            self._settings_width,
            self._on_settings_width_changed,
            baseline=self._saved.settings_width,
            help=self.tr(
                "Width in pixels of the right settings sidebar.",
                "Description of a setting (tooltip)",
            ),
        )

        # ── Window Grid ────────────────────────────────────
        self._add_section(self.tr("Window Grid", "Settings section"))
        self._tile_columns_slider = self._add_slider(
            self.tr("Columns", "Label of setting (must be short)"),
            1,
            8,
            self._tile_columns,
            self._on_tile_columns_changed,
            baseline=self._saved.tile_columns,
            help=self.tr(
                "Number of window preview tiles per row.",
                "Description of a setting (tooltip)",
            ),
        )
        self._aspect_combo = self._add_combo(
            self.tr("Aspect Ratio", "Label of setting (must be short)"),
            [name for name, _ in _ASPECT_RATIOS],
            _aspect_to_name(self._tile_aspect_ratio),
            self._on_aspect_changed,
            baseline=_aspect_to_name(self._saved.tile_aspect_ratio),
            help=self.tr(
                "Shape of each window preview tile.",
                "Description of a setting (tooltip)",
            ),
        )
        self._refresh_slider = self._add_slider(
            self.tr("Refresh (ms)", "Label of setting (must be short)"),
            250,
            30000,
            self._auto_refresh_ms,
            self._on_refresh_changed,
            baseline=self._saved.auto_refresh_ms,
            help=self.tr(
                "How often the window list is rescanned for new or closed windows.\n"
                "Lower values are more responsive but use more CPU.",
                "Description of a setting (tooltip)",
            ),
        )
        self._preview_slider = self._add_slider(
            self.tr("Preview (ms)", "Label of setting (must be short)"),
            16,
            1000,
            self._tile_preview_interval_ms,
            self._on_preview_changed,
            baseline=self._saved.tile_preview_interval_ms,
            help=self.tr(
                "How often each tile's live preview is refreshed.\n"
                "Lower values result in smoother previews but use more CPU.",
                "Description of a setting (tooltip)",
            ),
        )

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_zoom_changed(self, value: int) -> None:
        if value == self._zoom:
            return
        self._zoom = value
        self._notify_dirty()

    def _on_font_changed(self, family: str) -> None:
        if family == self._font_family:
            return
        self._font_family = family
        self._notify_dirty()

    def _on_preset_changed(self, text: str) -> None:
        if text == "Custom" or self._updating_from_preset:
            return
        preset = PRESETS.get(text, PRESETS["Auto"])
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

    def _on_profiles_width_changed(self, value: int) -> None:
        if value == self._profiles_width:
            return
        self._profiles_width = value
        self._notify_dirty()

    def _on_settings_width_changed(self, value: int) -> None:
        if value == self._settings_width:
            return
        self._settings_width = value
        self._notify_dirty()

    def _on_tile_columns_changed(self, value: int) -> None:
        if value == self._tile_columns:
            return
        self._tile_columns = value
        self._notify_dirty()

    def _on_aspect_changed(self, name: str) -> None:
        ratio = dict(_ASPECT_RATIOS).get(name)
        if ratio is None or ratio == self._tile_aspect_ratio:
            return
        self._tile_aspect_ratio = ratio
        self._notify_dirty()

    def _on_refresh_changed(self, value: int) -> None:
        if value == self._auto_refresh_ms:
            return
        self._auto_refresh_ms = value
        self._notify_dirty()

    def _on_preview_changed(self, value: int) -> None:
        if value == self._tile_preview_interval_ms:
            return
        self._tile_preview_interval_ms = value
        self._notify_dirty()

    def is_dirty(self) -> bool:
        """Return True if any GUI value differs from the last applied state."""
        return self._current_overrides() != self._saved

    def is_default(self) -> bool:
        """Return False if any GUI value differs from the default ones."""
        return self._current_overrides() == GUIStyleOverrides(palette=PRESETS["Auto"])

    def _refresh_baselines(self) -> None:
        """Update every widget's baseline to the current saved state."""
        self._zoom_slider.set_baseline(self._saved_zoom)
        self._font_row.set_baseline(self._saved_font_family)
        self._profiles_width_slider.set_baseline(self._saved.profiles_width)
        self._settings_width_slider.set_baseline(self._saved.settings_width)
        self._tile_columns_slider.set_baseline(self._saved.tile_columns)
        self._aspect_combo.set_baseline(_aspect_to_name(self._saved.tile_aspect_ratio))
        self._refresh_slider.set_baseline(self._saved.auto_refresh_ms)
        self._preview_slider.set_baseline(self._saved.tile_preview_interval_ms)

        for field in fields(GUIPalette):
            name = field.name
            baseline_hex = normalize_to_hex(getattr(self._saved_palette, name))
            self._picker_widgets[name].set_baseline(baseline_hex)

    def apply_clicked(self) -> None:
        """Persist the style attributes, then rebuild the GUI."""
        overrides = self._current_overrides()
        self._saved = overrides
        self._refresh_baselines()
        self._on_apply(overrides)
        self._notify_dirty()

    def reset_style(self) -> None:
        """Revert the style attributes to the last applied state."""
        self._palette = copy.deepcopy(self._saved_palette)
        self._zoom = self._saved_zoom
        self._font_family = self._saved_font_family
        self._profiles_width = self._saved.profiles_width
        self._settings_width = self._saved.settings_width
        self._tile_columns = self._saved.tile_columns
        self._tile_aspect_ratio = self._saved.tile_aspect_ratio
        self._auto_refresh_ms = self._saved.auto_refresh_ms
        self._tile_preview_interval_ms = self._saved.tile_preview_interval_ms

        self._sync_widgets()
        self._refresh_baselines()
        self._notify_dirty()

    def restore_auto_preset(self) -> None:
        """Load the Auto preset and all defaults without applying."""
        preset = PRESETS["Auto"]
        defaults = GUIStyleOverrides(palette=preset)

        self._palette = palette_to_internal(preset)
        self._zoom = defaults.zoom
        self._font_family = defaults.font_family
        self._profiles_width = defaults.profiles_width
        self._settings_width = defaults.settings_width
        self._tile_columns = defaults.tile_columns
        self._tile_aspect_ratio = defaults.tile_aspect_ratio
        self._auto_refresh_ms = defaults.auto_refresh_ms
        self._tile_preview_interval_ms = defaults.tile_preview_interval_ms

        self._sync_widgets()
        self._notify_dirty()

    def _notify_dirty(self) -> None:
        """Emit the current dirty state (call after any change)."""
        self.style_dirty_changed.emit(self.is_dirty())

    def _current_overrides(self) -> GUIStyleOverrides:
        """Build a GUIStyleOverrides from the tab's current editing state."""
        return GUIStyleOverrides(
            palette=palette_to_stylesheet(self._palette),
            zoom=self._zoom,
            font_family=self._font_family,
            profiles_width=self._profiles_width,
            settings_width=self._settings_width,
            tile_columns=self._tile_columns,
            tile_aspect_ratio=self._tile_aspect_ratio,
            auto_refresh_ms=self._auto_refresh_ms,
            tile_preview_interval_ms=self._tile_preview_interval_ms,
        )

    def _sync_widgets(self) -> None:
        """Push the current local state into every widget, without emitting."""
        sliders = (
            (self._zoom_slider, self._zoom),
            (self._profiles_width_slider, self._profiles_width),
            (self._settings_width_slider, self._settings_width),
            (self._tile_columns_slider, self._tile_columns),
            (self._refresh_slider, self._auto_refresh_ms),
            (self._preview_slider, self._tile_preview_interval_ms),
        )
        for slider, value in sliders:
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)

        self._aspect_combo.blockSignals(True)
        self._aspect_combo.setCurrentText(_aspect_to_name(self._tile_aspect_ratio))
        self._aspect_combo.blockSignals(False)

        self._font_row.set_font_family(self._font_family)

        self._preset_combo.blockSignals(True)
        self._preset_combo.setCurrentText(
            find_matching_preset(palette_to_stylesheet(self._palette))
        )
        self._preset_combo.blockSignals(False)

        for field in fields(GUIPalette):
            picker = self._picker_widgets[field.name]
            picker.blockSignals(True)
            picker.set_color(getattr(self._palette, field.name))
            picker.blockSignals(False)

    @property
    def _saved_palette(self) -> GUIPalette:
        """Return the last applied palette, decoupled from the live one."""
        return palette_to_internal(self._saved.palette)

    @property
    def _saved_zoom(self) -> int:
        return self._saved.zoom

    @property
    def _saved_font_family(self) -> str:
        return self._saved.font_family
