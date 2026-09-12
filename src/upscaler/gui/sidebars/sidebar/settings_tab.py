from __future__ import annotations

import copy
from typing import Callable, List, Optional, Set, TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)

from ..controls import (
    CheckBox,
    ColorPickerRow,
    ComboRow,
    FontPickerRow,
    HotkeyRow,
    LineEditRow,
    PathPickerRow,
    SectionLabel,
    SliderRow,
)
from ...styles import (
    scroll_area_style,
    scrollbar_style,
    section_title_style,
    section_underline_style,
)
from ....config import Config, DEFAULT_CONFIG

if TYPE_CHECKING:
    from ...config import GUIConfig

_SYSTEM_DEFAULTS = Config()


class SettingsTab(QWidget):
    """
    A scrollable, styled tab page to be placed inside a ``SidebarBase``.

    Subclasses override :meth:`_build_content` to populate the page. Building
    is deferred until the tab is first shown (see :meth:`ensure_built`),
    because constructing every tab up front costs ~500 ms at startup, mostly
    in stylesheet parsing and font enumeration. A ``config_changed`` signal
    is available to notify the sidebar that a setting has been modified.
    """

    config_changed = Signal()

    def __init__(
        self,
        gui_config: GUIConfig,
        title: str,
        config: Optional[Config] = None,
        baseline_config: Optional[Config] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._gui_config = gui_config
        self._config = config if config is not None else DEFAULT_CONFIG
        self.baseline_config = (
            baseline_config if baseline_config is not None else DEFAULT_CONFIG
        )
        self.title = title
        self._built = False
        self._owned_fields: Set[str] = set()

        self.setContentsMargins(0, 0, 0, 0)

        # ---- Outer vertical layout holds only the scroll area ---------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.verticalScrollBar().setStyleSheet(scrollbar_style(gui_config))
        scroll.horizontalScrollBar().setStyleSheet(scrollbar_style(gui_config))
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(scroll_area_style(self._gui_config))

        # ---- Inner content widget and its layout ----------------------------
        s = gui_config.sidebar
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(
            s.content_margin_h,
            s.content_margin_v,
            s.content_margin_h,
            s.content_margin_v,
        )
        self.content_layout.setSpacing(s.content_spacing)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def ensure_built(self) -> None:
        """Populate the tab's content on first use."""
        if self._built:
            return
        self._built = True
        try:
            self._build_content()
        except Exception:
            self._built = False
            raise
        self.content_layout.addStretch()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.ensure_built()

    # ------------------------------------------------------------------
    #  Subclass hook
    # ------------------------------------------------------------------
    def _build_content(self) -> None:
        """Override to add widgets to :attr:`content_layout`."""
        pass

    # ------------------------------------------------------------------
    #  Revert methods
    # ------------------------------------------------------------------
    def revert_to_baseline(self) -> None:
        """Revert every field owned by this tab to the saved state."""
        if not self._owned_fields:
            return
        if self._config is DEFAULT_CONFIG:
            raise RuntimeError(
                f"{type(self).__name__} declares owned fields but received "
                "DEFAULT_CONFIG instead of the live Config instance. "
                "Pass config=config to super().__init__()."
            )
        for name in self._owned_fields:
            setattr(
                self._config,
                name,
                copy.deepcopy(getattr(self.baseline_config, name)),
            )
        self.config_changed.emit()

    def reset_to_defaults(self) -> None:
        """Reset every field owned by this tab to its shipped default."""
        if not self._owned_fields:
            return
        if self._config is DEFAULT_CONFIG:
            raise RuntimeError(
                f"{type(self).__name__} declares owned fields but received "
                "DEFAULT_CONFIG instead of the live Config instance. "
                "Pass config=config to super().__init__()."
            )
        for name in self._owned_fields:
            setattr(self._config, name, copy.deepcopy(getattr(_SYSTEM_DEFAULTS, name)))
        self.config_changed.emit()

    def tab_has_changes(self) -> bool:
        """True if any field owned by this tab differs from the saved baseline."""
        for name in self._owned_fields:
            if getattr(self._config, name) != getattr(self.baseline_config, name):
                return True
        return False

    def tab_differs_from_defaults(self) -> bool:
        """True if any field owned by this tab differs from system defaults."""
        for name in self._owned_fields:
            if getattr(self._config, name) != getattr(_SYSTEM_DEFAULTS, name):
                return True
        return False

    # ------------------------------------------------------------------
    #  Layout helpers (used by subclasses and external controls)
    # ------------------------------------------------------------------
    def _add_section_label(self, text: str) -> None:
        """Add an uppercase section header with a thin separator line below."""
        label = QLabel(text.upper())
        label.setStyleSheet(section_title_style(self._gui_config))

        line = QFrame()
        line.setFrameShape(QFrame.NoFrame)
        line.setStyleSheet(section_underline_style(self._gui_config))

        self.content_layout.addWidget(label)
        self.content_layout.addWidget(line)

    def _add_row(self, label_text: str, widget: QWidget) -> None:
        """Place a label and a control side-by-side on one row."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label_text)
        lbl.setFixedHeight(self._gui_config.sidebar.row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        row.addWidget(lbl)
        row.addStretch()

        widget.setFixedHeight(self._gui_config.sidebar.row_height)
        row.addWidget(widget)

        self.content_layout.addLayout(row)

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self._gui_config))

    def _add_cb(
        self,
        label: str,
        checked: bool,
        slot: Callable,
        baseline: Optional[bool] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> CheckBox:
        cb = CheckBox(
            label,
            self._gui_config,
            checked,
            baseline=baseline,
            tooltip=help,
        )
        cb.stateChanged.connect(slot)
        self.content_layout.addWidget(cb)
        if field is not None:
            self._owned_fields.add(field)
        return cb

    def _add_slider(
        self,
        label: str,
        min_val: int,
        max_val: int,
        value: int,
        slot: Callable = lambda v: None,
        show_val: bool = True,
        editable: bool = True,
        scale_factor: int = 1,
        float_slot: Optional[Callable] = None,
        baseline: Optional[float] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> SliderRow:
        """Add a slider row, optionally with float output and editable field."""
        slider = SliderRow(
            label,
            self._gui_config,
            min_val,
            max_val,
            value,
            show_value=show_val or editable,
            editable=editable,
            scale_factor=scale_factor,
            baseline=baseline,
            tooltip=help,
        )
        slider.valueChanged.connect(slot)
        if float_slot is not None:
            slider.floatValueChanged.connect(float_slot)
        self.content_layout.addWidget(slider)
        if field is not None:
            self._owned_fields.add(field)
        return slider

    def _add_named_slider(
        self,
        label: str,
        names: List[str],
        current_name: str,
        slot: Callable,
        editable: bool = False,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> SliderRow:
        """Add a slider that displays a name from a list instead of a number."""
        try:
            index = names.index(current_name)
        except ValueError:
            index = 0

        if baseline is not None:
            try:
                baseline_index = names.index(baseline)
            except ValueError:
                baseline_index = None
        else:
            baseline_index = None

        formatter = lambda v: names[v] if 0 <= v < len(names) else "?"

        slider = SliderRow(
            label,
            self._gui_config,
            min_val=0,
            max_val=len(names) - 1,
            value=index,
            show_value=True,
            value_formatter=formatter,
            editable=editable,
            baseline=baseline_index,
            tooltip=help,
        )
        slider.valueChanged.connect(lambda val: slot(names[val]))
        self.content_layout.addWidget(slider)
        if field is not None:
            self._owned_fields.add(field)
        return slider

    def _add_combo(
        self,
        label: str,
        items: List[str],
        current: Optional[str],
        slot: Callable,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> ComboRow:
        """Add a labeled combo box row and return it."""
        combo = ComboRow(
            label,
            self._gui_config,
            items,
            current,
            baseline=baseline,
            tooltip=help,
        )
        combo.currentTextChanged.connect(slot)
        self.content_layout.addWidget(combo)
        if field is not None:
            self._owned_fields.add(field)
        return combo

    def _add_text(
        self,
        label: str,
        text: str,
        slot: Callable,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> LineEditRow:
        """Add a labeled single-line text edit and return it."""
        editor = LineEditRow(
            label,
            self._gui_config,
            text,
            baseline=baseline,
            tooltip=help,
        )
        editor.textChanged.connect(slot)
        self.content_layout.addWidget(editor)
        if field is not None:
            self._owned_fields.add(field)
        return editor

    def _add_path_picker(
        self,
        label: str,
        initial_path: str,
        slot: Callable,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> PathPickerRow:
        """Add a directory picker row (line edit + browse) and return it."""
        picker = PathPickerRow(
            label,
            self._gui_config,
            initial_path,
            baseline=baseline,
            tooltip=help,
        )
        picker.pathChanged.connect(slot)
        self.content_layout.addWidget(picker)
        if field is not None:
            self._owned_fields.add(field)
        return picker

    def _add_color_picker(
        self,
        label: str,
        initial_color: str,
        slot: Callable,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> ColorPickerRow:
        """Add a color picker row (swatch + dialog) and return it."""
        picker = ColorPickerRow(
            label,
            self._gui_config,
            initial_color,
            baseline=baseline,
            tooltip=help,
        )
        picker.colorChanged.connect(slot)
        self.content_layout.addWidget(picker)
        if field is not None:
            self._owned_fields.add(field)
        return picker

    def _add_font_picker(
        self,
        label: str,
        current: str,
        system_family: str,
        slot: Callable,
        baseline: Optional[str] = None,
        field: Optional[str] = None,
        help: Optional[str] = None,
    ) -> FontPickerRow:
        """Add a labeled font-family picker row and return it."""
        row = FontPickerRow(
            self._gui_config,
            label,
            current,
            system_family,
            baseline=baseline,
            tooltip=help,
        )
        row.fontChanged.connect(slot)
        self.content_layout.addWidget(row)
        if field is not None:
            self._owned_fields.add(field)
        return row

    def _add_hotkey(
        self,
        label: str,
        sequence: str,
        slot: Callable,
        baseline: Optional[str] = None,
        help: Optional[str] = None,
    ) -> HotkeyRow:
        """Add a labeled hotkey capture row and return it."""
        row = HotkeyRow(
            self._gui_config,
            label,
            sequence,
            baseline=baseline,
            tooltip=help,
        )
        row.sequenceChanged.connect(slot)
        self.content_layout.addWidget(row)
        self._owned_fields.add("hotkeys")
        return row
