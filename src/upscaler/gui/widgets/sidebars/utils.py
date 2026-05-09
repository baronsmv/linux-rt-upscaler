"""Shared utilities for sidebars: elegant styling and base widget factories."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QSlider,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QFrame,
    QGraphicsDropShadowEffect,
)

from ...config import GUIConfig

# ---------------------------------------------------------------------------
#  Styling constants – can be moved to GUIConfig if desired
# ---------------------------------------------------------------------------

STYLE_SIDEBAR = """
    QWidget#sidebar_container {
        background-color: #1a1a1c;
        border-radius: 12px;
    }
"""

STYLE_TABS = """
    QTabWidget::pane {
        border: none;
        background: #1a1a1c;
        border-radius: 0px 0px 12px 12px;
    }
    QTabBar::tab {
        background: transparent;
        color: #999;
        font-size: 13px;
        font-weight: 500;
        padding: 10px 20px;
        margin-right: 4px;
        border: none;
        border-bottom: 2px solid transparent;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        color: #ffffff;
        border-bottom: 2px solid #5b9bd5;
    }
    QTabBar::tab:hover {
        color: #ccc;
    }
    QTabBar::tab:disabled {
        color: #555;
    }
"""

STYLE_SCROLL = """
    QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollArea > QWidget > QWidget {
        background: transparent;
    }
"""

STYLE_SECTION_LABEL = """
    font-size: 11px;
    font-weight: bold;
    color: #777;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 0px 4px 0px;
"""

STYLE_LABEL = "color: #ccc; font-size: 12px;"

STYLE_CHECKBOX = """
    QCheckBox {
        spacing: 8px;
        color: #ccc;
        font-size: 12px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #555;
        border-radius: 4px;
        background: transparent;
    }
    QCheckBox::indicator:checked {
        background-color: #5b9bd5;
        border-color: #5b9bd5;
    }
    QCheckBox::indicator:hover {
        border-color: #5b9bd5;
    }
"""

STYLE_SLIDER = """
    QSlider::groove:horizontal {
        border: none;
        height: 4px;
        background: #333;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #5b9bd5;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }
    QSlider::handle:horizontal:hover {
        background: #6aade5;
    }
"""

STYLE_COMBO = """
    QComboBox {
        background: #2a2a2c;
        border: 1px solid #444;
        border-radius: 6px;
        padding: 4px 8px;
        color: #ddd;
        font-size: 12px;
        min-width: 90px;
    }
    QComboBox:hover {
        border-color: #5b9bd5;
    }
    QComboBox:focus {
        border-color: #5b9bd5;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #444;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    QComboBox QAbstractItemView {
        background: #2a2a2c;
        border: 1px solid #444;
        selection-background-color: #5b9bd5;
        color: #ddd;
    }
"""


class SidebarBase(QWidget):
    """
    A beautiful sidebar container with optional shadow and custom tabs.

    Call ``add_tab(widget, title)`` to populate.
    """

    config_changed = Signal()

    def __init__(self, gui_config: GUIConfig, parent=None):
        super().__init__(parent)
        self.gui_config = gui_config
        self.setFixedWidth(gui_config.sidebar_width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Main container with rounded corners and shadow
        self.setObjectName("sidebar_container")
        self.setStyleSheet(STYLE_SIDEBAR)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.gray)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        # Tab widget at top
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(STYLE_TABS)
        layout.addWidget(self.tab_widget)

    def add_tab(self, widget: QWidget, title: str) -> None:
        """Add a new tab with the given title."""
        self.tab_widget.addTab(widget, title)


class SettingsTab(QWidget):
    """
    Base for a sidebar content tab. Provides beautiful row helpers:
    sections, checkboxes, sliders, combos with consistent styling.
    """

    config_changed = Signal()

    def __init__(self, gui_config: GUIConfig, title: str, parent=None):
        super().__init__(parent)
        self.gui_config = gui_config
        self.title = title
        self.setContentsMargins(0, 0, 0, 0)

        # Outer layout with scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(STYLE_SCROLL)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(16, 8, 16, 8)
        self.content_layout.setSpacing(12)

        self._build_content()
        self.content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _build_content(self) -> None:
        """Override to populate the tab."""
        pass

    # ------------------------------------------------------------------
    #  Beautiful widget helpers
    # ------------------------------------------------------------------

    def _add_section_label(self, text: str) -> None:
        label = QLabel(text.upper())
        label.setStyleSheet(STYLE_SECTION_LABEL)
        # Add a thin separator line below the label
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #333;")
        self.content_layout.addWidget(label)
        self.content_layout.addWidget(line)

    def _add_row(self, label_text: str, widget: QWidget) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label_text)
        lbl.setStyleSheet(STYLE_LABEL)
        lbl.setFixedHeight(28)
        lbl.setAlignment(Qt.AlignVCenter)
        row.addWidget(lbl)
        row.addStretch()

        # Style the widget based on type
        if isinstance(widget, QCheckBox):
            widget.setStyleSheet(STYLE_CHECKBOX)
        elif isinstance(widget, QSlider):
            widget.setStyleSheet(STYLE_SLIDER)
            widget.setFixedHeight(40)
        elif isinstance(widget, QComboBox):
            widget.setStyleSheet(STYLE_COMBO)
        else:
            widget.setFixedHeight(28)
        row.addWidget(widget)
        self.content_layout.addLayout(row)

    def _add_checkbox_row(self, label: str, checked: bool, slot) -> QCheckBox:
        cb = QCheckBox(label)  # the label is inside the checkbox for a cleaner look
        cb.setChecked(checked)
        cb.stateChanged.connect(slot)
        self.content_layout.addWidget(cb)
        return cb

    def _add_slider_row(
        self, label: str, min_val: int, max_val: int, value: int, slot
    ) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(value)
        slider.valueChanged.connect(slot)
        self._add_row(label, slider)
        return slider

    def _add_combo_row(self, label: str, items: list, current: str, slot) -> QComboBox:
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentText(current)
        combo.currentTextChanged.connect(slot)
        self._add_row(label, combo)
        return combo
