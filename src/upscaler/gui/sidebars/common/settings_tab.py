from __future__ import annotations

from typing import Callable, List, Optional, TYPE_CHECKING

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
    LineEditRow,
    PathPickerRow,
    SectionLabel,
    SliderRow,
)
from ...styles import (
    row_label_style,
    section_label,
    separator_line_style,
    scroll_area_style,
    scrollbar_style,
)
from ....config import DEFAULT_CONFIG

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class SettingsTab(QWidget):
    """
    A scrollable, styled tab page to be placed inside a ``SidebarBase``.

    Subclasses override :meth:`_build_content` to populate the page.
    A ``config_changed`` signal is available to notify the sidebar that
    a setting has been modified (optional, depending on concrete tab).

    The class provides convenience methods for adding rows with labels,
    section headers, and separators - all styled consistently.
    """

    config_changed = Signal()

    def __init__(
        self,
        gui_config: GUIConfig,
        title: str,
        baseline_config: Optional[Config] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.gui_config = gui_config
        self.baseline_config = (
            baseline_config if baseline_config is not None else DEFAULT_CONFIG
        )
        self.title = title

        self.setContentsMargins(0, 0, 0, 0)

        # ---- Outer vertical layout holds only the scroll area ---------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.verticalScrollBar().setStyleSheet(scrollbar_style(gui_config))
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(scroll_area_style())

        # ---- Inner content widget and its layout ----------------------------
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(16, 8, 16, 8)
        self.content_layout.setSpacing(12)

        self._build_content()
        self.content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    # ------------------------------------------------------------------
    #  Subclass hook
    # ------------------------------------------------------------------
    def _build_content(self) -> None:
        """Override to add widgets to :attr:`content_layout`."""
        pass

    # ------------------------------------------------------------------
    #  Layout helpers (used by subclasses and external controls)
    # ------------------------------------------------------------------
    def _add_section_label(self, text: str) -> None:
        """Add an uppercase section header with a thin separator line below."""
        label = QLabel(text.upper())
        label.setStyleSheet(section_label(self.gui_config))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(separator_line_style(self.gui_config))

        self.content_layout.addWidget(label)
        self.content_layout.addWidget(line)

    def _add_row(self, label_text: str, widget: QWidget) -> None:
        """Place a label and a control side-by-side on one row."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(row_label_style(self.gui_config))
        lbl.setFixedHeight(self.gui_config.sidebar_row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        row.addWidget(lbl)
        row.addStretch()

        widget.setFixedHeight(self.gui_config.sidebar_row_height)
        row.addWidget(widget)

        self.content_layout.addLayout(row)

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

    def _add_cb(
        self,
        label: str,
        checked: bool,
        slot: Callable,
        baseline: Optional[bool] = None,
        help: Optional[str] = None,
    ) -> CheckBox:
        cb = CheckBox(
            label,
            self.gui_config,
            checked,
            baseline=baseline,
            tooltip=help,
        )
        cb.stateChanged.connect(slot)
        self.content_layout.addWidget(cb)
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
        help: Optional[str] = None,
    ) -> SliderRow:
        """Add a slider row, optionally with float output and editable field."""
        slider = SliderRow(
            label,
            self.gui_config,
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
        return slider

    def _add_named_slider(
        self,
        label: str,
        names: List[str],
        current_name: str,
        slot: Callable,
        editable: bool = False,
        baseline: Optional[str] = None,  # ← new parameter
        help: Optional[str] = None,
    ) -> SliderRow:
        """Add a slider that displays a name from a list instead of a number."""
        try:
            index = names.index(current_name)
        except ValueError:
            index = 0

        # Convert baseline string to index (or None if not provided)
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
            self.gui_config,
            min_val=0,
            max_val=len(names) - 1,
            value=index,
            show_value=True,
            value_formatter=formatter,
            editable=editable,
            baseline=baseline_index,
            tooltip=help,
        )
        # Map the integer index back to the name before calling the slot
        slider.valueChanged.connect(lambda val: slot(names[val]))
        self.content_layout.addWidget(slider)
        return slider

    def _add_combo(
        self,
        label: str,
        items: list[str],
        current: str | None,
        slot: Callable,
        baseline: Optional[str] = None,
        help: Optional[str] = None,
    ) -> ComboRow:
        """Add a labeled combo box row and return it."""
        combo = ComboRow(
            label,
            self.gui_config,
            items,
            current,
            baseline=baseline,
            tooltip=help,
        )
        combo.currentTextChanged.connect(slot)
        self.content_layout.addWidget(combo)
        return combo

    def _add_text(
        self,
        label: str,
        text: str,
        slot: Callable,
        baseline: Optional[str] = None,
        help: Optional[str] = None,
    ) -> LineEditRow:
        """Add a labeled single-line text edit and return it."""
        editor = LineEditRow(
            label,
            self.gui_config,
            text,
            baseline=baseline,
            tooltip=help,
        )
        editor.textChanged.connect(slot)
        self.content_layout.addWidget(editor)
        return editor

    def _add_path_picker(
        self,
        label: str,
        initial_path: str,
        slot: Callable,
        baseline: Optional[str] = None,
        help: Optional[str] = None,
    ) -> PathPickerRow:
        """Add a directory picker row (line edit + browse) and return it."""
        picker = PathPickerRow(
            label,
            self.gui_config,
            initial_path,
            baseline=baseline,
            tooltip=help,
        )
        picker.pathChanged.connect(slot)
        self.content_layout.addWidget(picker)
        return picker

    def _add_color_picker(
        self,
        label: str,
        initial_color: str,
        slot: Callable,
        baseline: Optional[str] = None,
        help: Optional[str] = None,
    ) -> ColorPickerRow:
        """Add a color picker row (swatch + dialog) and return it."""
        picker = ColorPickerRow(
            label,
            self.gui_config,
            initial_color,
            baseline=baseline,
            tooltip=help,
        )
        picker.colorChanged.connect(slot)
        self.content_layout.addWidget(picker)
        return picker
