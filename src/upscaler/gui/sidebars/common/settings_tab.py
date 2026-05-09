from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)

from . import styles
from ..controls import (
    CheckBox,
    ColorPickerRow,
    ComboRow,
    LineEditRow,
    PathPickerRow,
    SectionLabel,
    SliderRow,
)

if TYPE_CHECKING:
    from ...config import GUIConfig


class SettingsTab(QWidget):
    """
    A scrollable, styled tab page to be placed inside a ``SidebarBase``.

    Subclasses override :meth:`_build_content` to populate the page.
    A ``config_changed`` signal is available to notify the sidebar that
    a setting has been modified (optional, depending on concrete tab).

    The class provides convenience methods for adding rows with labels,
    section headers, and separators – all styled consistently.
    """

    config_changed = Signal()

    def __init__(
        self, gui_config: GUIConfig, title: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.gui_config = gui_config
        self.title = title

        self.setContentsMargins(0, 0, 0, 0)

        # ---- Outer vertical layout holds only the scroll area ---------------
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(styles.scroll_area())

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
        label.setStyleSheet(styles.section_label(self.gui_config))

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(styles.separator_line())

        self.content_layout.addWidget(label)
        self.content_layout.addWidget(line)

    def _add_row(self, label_text: str, widget: QWidget) -> None:
        """Place a label and a control side‑by‑side on one row."""
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel(label_text)
        lbl.setStyleSheet(styles.row_label(self.gui_config))
        lbl.setFixedHeight(self.gui_config.sidebar_row_height)
        lbl.setAlignment(Qt.AlignVCenter)
        row.addWidget(lbl)
        row.addStretch()

        widget.setFixedHeight(self.gui_config.sidebar_row_height)
        row.addWidget(widget)

        self.content_layout.addLayout(row)

    def _add_section(self, title: str) -> None:
        self.content_layout.addWidget(SectionLabel(title, self.gui_config))

    def _add_cb(self, label: str, checked: bool, slot) -> CheckBox:
        cb = CheckBox(label, self.gui_config, checked)
        cb.stateChanged.connect(slot)
        self.content_layout.addWidget(cb)
        return cb

    def _add_slider(
        self,
        label: str,
        min_val: int,
        max_val: int,
        value: int,
        slot,
        show_val: bool = False,
    ) -> SliderRow:
        slider = SliderRow(
            label, self.gui_config, min_val, max_val, value, show_value=show_val
        )
        slider.valueChanged.connect(slot)
        self.content_layout.addWidget(slider)
        return slider

    def _add_named_slider(
        self,
        label: str,
        names: list[str],
        current_name: str,
        slot,
    ) -> SliderRow:
        """A slider whose value readout displays a string from *names*."""
        try:
            index = names.index(current_name)
        except ValueError:
            index = 0

        slider = SliderRow(
            label,
            self.gui_config,
            0,
            len(names) - 1,
            index,
            show_value=True,
            value_formatter=lambda v: names[v] if 0 <= v < len(names) else "?",
        )
        slider.valueChanged.connect(slot)
        self.content_layout.addWidget(slider)
        return slider

    def _add_combo(
        self,
        label: str,
        items: list[str],
        current: str | None,
        slot,
    ) -> ComboRow:
        """Add a labelled combo box row and return it."""
        combo = ComboRow(label, self.gui_config, items, current)
        combo.currentTextChanged.connect(slot)
        self.content_layout.addWidget(combo)
        return combo

    def _add_text(
        self,
        label: str,
        text: str,
        slot,
    ) -> LineEditRow:
        """Add a labelled single‑line text edit and return it."""
        editor = LineEditRow(label, self.gui_config, text)
        editor.textChanged.connect(slot)
        self.content_layout.addWidget(editor)
        return editor

    def _add_path_picker(
        self,
        label: str,
        initial_path: str,
        slot,
    ) -> PathPickerRow:
        """Add a directory picker row (line edit + browse) and return it."""
        picker = PathPickerRow(label, self.gui_config, initial_path)
        picker.pathChanged.connect(slot)
        self.content_layout.addWidget(picker)
        return picker

    def _add_color_picker(
        self,
        label: str,
        initial_color: str,
        slot,
    ) -> ColorPickerRow:
        """Add a colour picker row (swatch + dialog) and return it."""
        picker = ColorPickerRow(label, self.gui_config, initial_color)
        picker.colorChanged.connect(slot)
        self.content_layout.addWidget(picker)
        return picker
