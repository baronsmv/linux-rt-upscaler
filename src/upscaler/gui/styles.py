from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .utils import background_rule

if TYPE_CHECKING:
    from .config import GUIConfig


# ---------------------------------------------------------------------------
#  Control common class
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ControlPalette:
    input: str
    input_hover: str
    text: str
    text_hover: str
    border: str
    border_hover: str
    action: str
    action_hover: str


def _control_palette(
    cfg: GUIConfig,
    enabled: bool = True,
    highlighted: bool = False,
) -> ControlPalette:
    if highlighted:
        return ControlPalette(
            input=cfg.palette.input,
            input_hover=cfg.palette.input_hover,
            text=cfg.palette.control,
            text_hover=cfg.palette.text_hover,
            border=cfg.palette.border,
            border_hover=cfg.palette.border_hover,
            action=cfg.palette.control,
            action_hover=cfg.palette.control_hover,
        )
    elif enabled:
        return ControlPalette(
            input=cfg.palette.input,
            input_hover=cfg.palette.input_hover,
            text=cfg.palette.text,
            text_hover=cfg.palette.text_hover,
            border=cfg.palette.border,
            border_hover=cfg.palette.border_hover,
            action=cfg.palette.control,
            action_hover=cfg.palette.control_hover,
        )
    else:
        return ControlPalette(
            input=cfg.palette.input_disabled,
            input_hover=cfg.palette.input_disabled,
            text=cfg.palette.text_subtle,
            text_hover=cfg.palette.text_subtle,
            border=cfg.palette.border,
            border_hover=cfg.palette.border,
            action=cfg.palette.border,
            action_hover=cfg.palette.border,
        )


# ---------------------------------------------------------------------------
#  Tooltip
# ---------------------------------------------------------------------------
def tooltip_style(cfg: GUIConfig) -> str:
    """Style for QToolTip in both light and dark themes."""
    return f"""
    QToolTip {{
        color: {cfg.palette.text_hover};
        {background_rule(cfg.palette.background)}
        border: 1px solid {cfg.palette.border};
        padding: 4px;
        border-radius: 4px;
        font-size: {cfg.dialog.label_font_size}px;
    }}
    """


# ---------------------------------------------------------------------------
#  Scrollbar
# ---------------------------------------------------------------------------
def scrollbar_style(cfg: GUIConfig) -> str:
    """Custom scrollbars (both orientations) for sidebars and lists."""
    s = cfg.scrollbar
    return f"""
    QScrollBar:vertical {{
        background: transparent;
        width: {s.width}px;
        margin: 0;
        border: none;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: {s.width}px;
        margin: 0;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background-color: {cfg.palette.handle};
        border-radius: {s.radius}px;
        min-height: {s.handle_min_length}px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {cfg.palette.handle};
        border-radius: {s.radius}px;
        min-width: {s.handle_min_length}px;
    }}
    QScrollBar::handle:vertical:hover,
    QScrollBar::handle:horizontal:hover {{
        background-color: {cfg.palette.handle_hover};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        background: none;
        border: none;
        width: 0px;
        height: 0px;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {{
        background: none;
        border: none;
    }}
    """


def scroll_area_style(_: GUIConfig) -> str:
    """Transparent scroll area that blends into the sidebar background."""
    return """
    QScrollArea {
        background: transparent;
        border: none;
    }
    QScrollArea > QWidget > QWidget {
        background: transparent;
    }
    """


# ---------------------------------------------------------------------------
#  Separator
# ---------------------------------------------------------------------------
def separator_style(cfg: GUIConfig) -> str:
    """Style for the separators."""
    return f"color: {cfg.palette.border};"


# ---------------------------------------------------------------------------
#  Filter bar
# ---------------------------------------------------------------------------
def filter_bar_style(cfg: GUIConfig, hover: bool = False) -> str:
    """Style for the filter bar QLineEdit, with optional hover state."""
    bg = cfg.palette.input_hover if hover else cfg.palette.input
    return f"""
    QLineEdit {{
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.filter.border_radius}px;
        background-color: {bg};
        color: {cfg.palette.text_hover};
        font-size: {cfg.filter.font_size}px;
        padding: 0px;
        selection-background-color: {cfg.palette.control_hover};
    }}
    QLineEdit:focus {{
        border-color: {cfg.palette.control_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Section
# ---------------------------------------------------------------------------
def section_title_style(cfg: GUIConfig) -> str:
    """Uppercase section title inside a settings tab."""
    s = cfg.sidebar
    return f"""
    font-size: {s.section_title_font_size}px;
    font-weight: bold;
    color: {cfg.palette.text_subtle};
    text-transform: uppercase;
    letter-spacing: {s.section_title_letter_spacing}px;
    padding: {s.section_title_padding_top}px 0px {s.section_title_padding_bottom}px 0px;
    """


def section_underline_style(cfg: GUIConfig) -> str:
    """Thin horizontal line used under section headers."""
    return f"""
    background-color: {cfg.palette.border};
    min-height: 1px;
    max-height: 1px;
    border: none;
    """


# ---------------------------------------------------------------------------
#  Setting
# ---------------------------------------------------------------------------
def setting_highlight_bar_style(cfg: GUIConfig) -> str:
    """Style for the colored indicator bar (left side of a highlighted row)."""
    return f"background-color: {cfg.palette.control}; border: none;"


def setting_highlight_background_style(cfg: GUIConfig, highlighted: bool) -> str:
    """Background style for the content container of a BaseRow."""
    if highlighted:
        r = cfg.sidebar.row_border_radius
        return f"background-color: {cfg.palette.input}; border-radius: {r}px;"
    return "background-color: transparent;"


def setting_highlight_label_style(cfg: GUIConfig, color: str) -> str:
    """Label style that reflects highlight state."""
    return f"color: {color}; font-size: {cfg.sidebar.tab_font_size}px;"


# ---------------------------------------------------------------------------
#  Control: Text field
# ---------------------------------------------------------------------------
def line_edit_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Base style for QLineEdit used inside settings rows."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    return f"""
    QLineEdit {{
        background-color: {palette.input};
        border: 1px solid {palette.border};
        border-radius: {cfg.edit_field.border_radius}px;
        padding: {cfg.edit_field.padding_v}px {cfg.edit_field.padding_h}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
        selection-background-color: {palette.action};
    }}
    QLineEdit:hover {{
        border-color: {palette.border_hover};
    }}
    QLineEdit:focus {{
        border-color: {palette.border_hover};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: Combo box
# ---------------------------------------------------------------------------
def combo_box_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for QComboBox used inside settings rows."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    return f"""
    QComboBox {{
        background-color: {palette.input};
        border: 1px solid {palette.border};
        border-radius: {cfg.combo.border_radius}px;
        padding: {cfg.combo.padding_v}px {cfg.combo.padding_h}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QComboBox:hover {{
        border-color: {palette.border_hover};
    }}
    QComboBox:focus {{
        border-color: {palette.border_hover};
    }}
    QComboBox::drop-down {{
        width: 0px;
        background-color: transparent;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {palette.input};
        border: none;
        border-radius: 0px;
        padding: 0px;
        selection-background-color: {palette.action};
        color: {palette.text};
        outline: none;
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: Checkbox
# ---------------------------------------------------------------------------
def checkbox_style(
    cfg: GUIConfig, enabled: bool = True, highlighted: bool = False
) -> str:
    """Style for a QCheckBox inside a settings row."""
    palette = _control_palette(cfg=cfg, enabled=enabled, highlighted=highlighted)
    return f"""
    QCheckBox {{
        spacing: {cfg.checkbox.spacing}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
        padding: {cfg.checkbox.padding_v}px 0;
    }}
    QCheckBox::indicator {{
        width: {cfg.checkbox.indicator_size}px;
        height: {cfg.checkbox.indicator_size}px;
        border: {cfg.checkbox.indicator_border_width}px solid {palette.action};
        border-radius: {cfg.checkbox.indicator_radius}px;
        background-color: transparent;
    }}
    QCheckBox::indicator:checked {{
        background-color: {palette.action};
        border-color: {palette.action};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: Color swatch
# ---------------------------------------------------------------------------
def color_swatch_style(
    cfg: GUIConfig, enabled: bool = True, current_color: str = "#000000"
) -> str:
    """Style for the QPushButton that acts as a color preview."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    return f"""
    QPushButton {{
        background-color: {current_color};
        border: 1px solid {palette.border};
        border-radius: {cfg.swatch.radius}px;
    }}
    QPushButton:hover {{
        border-color: {palette.border_hover};
    }}
    {tooltip_style(cfg)}
    """


def color_dialog_style(cfg: GUIConfig) -> str:
    """Style the QColorDialog."""
    return f"""
    QColorDialog {{
        {background_rule(cfg.palette.background)}
    }}
    QColorDialog QLabel {{
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QColorDialog QPushButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QColorDialog QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
        color: {cfg.palette.text_hover};
    }}
    QColorDialog QPushButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    QColorDialog QLineEdit,
    QColorDialog QSpinBox {{
        background-color: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: 4px;
        padding: 2px 6px;
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QColorDialog QLineEdit:focus,
    QColorDialog QSpinBox:focus {{
        border-color: {cfg.palette.control};
    }}
    QColorDialog QFrame#qt_colorscreen_frame {{
        border: 1px solid {cfg.palette.border};
        border-radius: 4px;
    }}
    QColorDialog QFrame#qt_colorscreen_frame > QWidget > QWidget {{
        border: none;
        border-radius: 3px;
    }}
    {scrollbar_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: Slider
# ---------------------------------------------------------------------------
def slider_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for a horizontal QSlider."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    s = cfg.slider
    groove_radius = max(0, (s.groove_height - 1) // 2)
    handle_radius = max(0, (s.handle_size - 1) // 2)
    handle_inset = max(0, (s.handle_size - s.groove_height) // 2)

    return f"""
    QSlider::groove:horizontal {{
        border: none;
        height: {s.groove_height}px;
        background-color: {palette.border};
        border-radius: {groove_radius}px;
    }}
    QSlider::handle:horizontal {{
        background-color: {palette.action};
        width: {s.handle_size}px;
        height: {s.handle_size}px;
        margin: -{handle_inset}px 0;
        border-radius: {handle_radius}px;
    }}
    QSlider::handle:horizontal:hover {{
        background-color: {palette.action_hover};
    }}
    QSlider::sub-page:horizontal {{
        background-color: {palette.action};
        border-radius: {groove_radius}px;
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: File dialog
# ---------------------------------------------------------------------------
def file_dialog_style(cfg: GUIConfig) -> str:
    """Style every relevant widget inside a QFileDialog."""
    return f"""
    QFileDialog {{
        {background_rule(cfg.palette.background)}
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QFileDialog QLabel {{
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QFileDialog QLineEdit,
    QFileDialog QComboBox,
    QFileDialog QSpinBox {{
        background-color: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QFileDialog QLineEdit:focus,
    QFileDialog QComboBox:focus,
    QFileDialog QSpinBox:focus {{
        border-color: {cfg.palette.control};
    }}
    QFileDialog QPushButton,
    QFileDialog QToolButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QFileDialog QPushButton:hover,
    QFileDialog QToolButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
        color: {cfg.palette.text_hover};
    }}
    QFileDialog QPushButton:pressed,
    QFileDialog QToolButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    QFileDialog QPushButton:disabled,
    QFileDialog QToolButton:disabled {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text_subtle};
        border-color: {cfg.palette.border};
    }}
    QFileDialog QListView,
    QFileDialog QTreeView,
    QFileDialog QTableView {{
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.list_border_radius}px;
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
        outline: none;
    }}
    QFileDialog QListView::item,
    QFileDialog QTreeView::item,
    QFileDialog QTableView::item {{
        border-radius: {cfg.dialog.list_item_border_radius}px;
        color: {cfg.palette.text};
    }}
    QFileDialog QListView::item:hover,
    QFileDialog QTreeView::item:hover,
    QFileDialog QTableView::item:hover {{
        background-color: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
    }}
    QFileDialog QListView::item:selected,
    QFileDialog QTreeView::item:selected,
    QFileDialog QTableView::item:selected {{
        background-color: {cfg.palette.control};
        color: {cfg.palette.text_hover};
    }}
        QFileDialog QHeaderView::section {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text};
        border: none;
        border-bottom: 1px solid {cfg.palette.border};
        padding: 2px 6px;
        height: {round(cfg.dialog.label_font_size * 1.3)}px;
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QFileDialog QScrollBar:vertical {{
        background: transparent;
        width: {cfg.scrollbar.width}px;
        margin: 0;
    }}
    QFileDialog QScrollBar::handle:vertical {{
        background-color: {cfg.palette.handle};
        border-radius: {cfg.scrollbar.radius}px;
        min-height: {cfg.scrollbar.handle_min_length}px;
    }}
    QFileDialog QScrollBar:handle:vertical:hover {{
        background-color: {cfg.palette.handle_hover};
    }}
    QFileDialog QScrollBar:horizontal {{
        background: transparent;
        height: {cfg.scrollbar.width}px;
        margin: 0;
    }}
    QFileDialog QScrollBar::handle:horizontal {{
        background-color: {cfg.palette.handle};
        border-radius: {cfg.scrollbar.radius}px;
        min-width: {cfg.scrollbar.handle_min_length}px;
    }}
    QFileDialog QScrollBar::handle:horizontal:hover {{
        background-color: {cfg.palette.handle_hover};
    }}
    QFileDialog QScrollBar::add-line:vertical,
    QFileDialog QScrollBar::sub-line:vertical,
    QFileDialog QScrollBar::add-line:horizontal,
    QFileDialog QScrollBar::sub-line:horizontal {{
        height: 0px;
        width: 0px;
    }}
    QFileDialog QScrollBar::add-page:vertical,
    QFileDialog QScrollBar::sub-page:vertical,
    QFileDialog QScrollBar::add-page:horizontal,
    QFileDialog QScrollBar::sub-page:horizontal {{
        background: none;
    }}
    QFileDialog QToolButton#qt_file_dialog_up_button,
    QFileDialog QToolButton#qt_file_dialog_back_button,
    QFileDialog QToolButton#qt_file_dialog_forward_button {{
        border: none;
        background-color: transparent;
        padding: 4px;
    }}
    QFileDialog QToolButton#qt_file_dialog_up_button:hover,
    QFileDialog QToolButton#qt_file_dialog_back_button:hover,
    QFileDialog QToolButton#qt_file_dialog_forward_button:hover {{
        background-color: {cfg.palette.button_hover};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: Browse button
# ---------------------------------------------------------------------------
def path_browse_button_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for the small browse button next to a path field."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    return f"""
    QPushButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {palette.border};
        border-radius: {cfg.edit_field.border_radius}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {palette.border_hover};
        color: {palette.text_hover};
    }}
    QPushButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    QPushButton:disabled {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text_subtle};
        border-color: {palette.border};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Control: hotkey button
# ---------------------------------------------------------------------------
def hotkey_button_style(
    cfg: GUIConfig,
    enabled: bool = True,
    conflict: bool = False,
) -> str:
    """
    Style for the QPushButton that captures a hotkey sequence.

    When *conflict* is True the border switches to the reset/warning color
    so a duplicated binding is visually obvious inside the tab.
    """
    palette = _control_palette(cfg=cfg, enabled=enabled)
    border = cfg.palette.reset if conflict else palette.border
    border_hover = cfg.palette.reset_hover if conflict else palette.border_hover
    focus_color = cfg.palette.reset if conflict else cfg.palette.control
    return f"""
    QPushButton {{
        background-color: {palette.input};
        border: 1px solid {border};
        border-radius: {cfg.edit_field.border_radius}px;
        padding: {cfg.edit_field.padding_v}px {cfg.edit_field.padding_h}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
        text-align: center;
    }}
    QPushButton:hover {{
        border-color: {border_hover};
    }}
    QPushButton:focus {{
        border-color: {focus_color};
        color: {palette.text_hover};
    }}
    QPushButton:disabled {{
        background-color: {cfg.palette.input_disabled};
        color: {cfg.palette.text_subtle};
    }}
    {tooltip_style(cfg)}
    """


def hotkey_clear_button_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for the small 'unbind' button next to a hotkey field."""
    palette = _control_palette(cfg=cfg, enabled=enabled)
    return f"""
    QToolButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {palette.border};
        border-radius: {cfg.edit_field.border_radius}px;
        color: {palette.text};
        font-size: {cfg.sidebar.tab_font_size + 2}px;
        font-weight: bold;
        padding: 0px;
    }}
    QToolButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {palette.border_hover};
        color: {palette.text_hover};
    }}
    QToolButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    QToolButton:disabled {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text_subtle};
        border-color: {palette.border};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Dialog
# ---------------------------------------------------------------------------
def dialog_style(cfg: GUIConfig) -> str:
    """Full stylesheet for QDialog used by ProfileDialog and WindowPickerDialog."""
    return f"""
    QDialog {{
        {background_rule(cfg.palette.background)}
        color: {cfg.palette.text};
    }}
    QLabel {{
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QLineEdit {{
        background-color: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text};
    }}
    QLineEdit:focus {{
        border-color: {cfg.palette.control};
    }}
    QComboBox {{
        background-color: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text};
        min-width: {cfg.dialog.combo_min_width}px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 0px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {cfg.palette.input};
        border: none;
        color: {cfg.palette.text};
        selection-background-color: {cfg.palette.control};
    }}
    QPushButton {{
        background-color: {cfg.palette.button};
        font-size: {cfg.dialog.label_font_size}px;
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
    }}
    QDialogButtonBox QPushButton {{
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
    }}
    QPushButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    QPushButton:disabled {{
        color: {cfg.palette.text_subtle};
    }}
    QGroupBox {{
        font-size: {cfg.dialog.label_font_size}px;
        font-weight: bold;
        color: {cfg.palette.text_subtle};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.groupbox_border_radius}px;
        margin-top: 8px;
        padding-top: 16px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
    }}
    QListWidget {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.list_border_radius}px;
        outline: none;
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QListWidget::item {{
        padding: {cfg.dialog.list_item_padding};
        border-radius: {cfg.dialog.list_item_border_radius}px;
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QListWidget::item:hover {{
        background-color: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
    }}
    QListWidget::item:selected {{
        background-color: {cfg.palette.control};
        color: {cfg.palette.text_hover};
    }}
    {scrollbar_style(cfg)}
    """


def dialog_header_label_style(_: GUIConfig) -> str:
    """Style for the header label in Profile Editor dialog."""
    return """
    font-weight: bold;
    """


def icon_preview_style(cfg: GUIConfig) -> str:
    """Style for icon preview in Profile Editor dialog."""
    d = cfg.dialog
    radius = max(2, d.icon_preview_size // 8)
    return f"""
    border: 1px solid {cfg.palette.border};
    border-radius: {radius}px;
    """


def dialog_info_label_style(cfg: GUIConfig) -> str:
    """Style for info label in Profile Editor dialog."""
    return f"""
    color: {cfg.palette.text_subtle};
    font-size: {cfg.dialog.info_font_size}px;
    padding-top: {cfg.dialog.info_padding_top}px;
    """


def dialog_match_label_style(cfg: GUIConfig) -> str:
    """Style for match label in Profile Editor dialog."""
    return f"""
    font-size: {cfg.dialog.input_font_size}px;
    font-weight: bold;
    """


def dialog_icon_button_style(cfg: GUIConfig) -> str:
    """Style for icon buttons in the Profile Editor dialog."""
    d = cfg.dialog
    radius = max(2, d.icon_button_size // 5)
    return f"""
    QToolButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {radius}px;
    }}
    QToolButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
    }}
    QToolButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Message box (mini dialog)
# ---------------------------------------------------------------------------
def message_box_style(cfg: GUIConfig) -> str:
    """Style for the QMessageBox that displays messages."""
    return f"""
    QMessageBox {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QMessageBox QLabel {{
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QMessageBox QPushButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
    }}
    QMessageBox QPushButton:pressed {{
        background-color: {cfg.palette.button_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Profile list (left sidebar)
# ---------------------------------------------------------------------------
def profile_list_style(cfg: GUIConfig) -> str:
    """Style for the QListWidget that displays profiles."""
    return f"""
    QListWidget {{
        font-size: {cfg.sidebar.tab_font_size}px;
        background-color: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        color: {cfg.palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
        background-color: transparent;
        border-radius: {cfg.profile.profile_border_radius}px;
        padding: {cfg.profile.profile_item_padding_v}px {cfg.profile.profile_item_padding_h}px;
        border-left: {cfg.profile.profile_border_left}px solid transparent;
    }}
    QListWidget::item:hover {{
        background-color: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
    }}
    QListWidget::item:selected {{
        background-color: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
        border-left: {cfg.profile.profile_border_left}px solid {cfg.palette.control};
    }}
    """


def profile_hint_style(cfg: GUIConfig) -> str:
    return f"""
    color: {cfg.palette.text_subtle};
    font-size: {cfg.profile.title_font_size}px;
    padding: 4px;
    """


def toolbar_button_style(cfg: GUIConfig) -> str:
    """Style for the small flat buttons (Add, Edit, Delete, Up, Down)."""
    return f"""
    QPushButton {{
        background-color: transparent;
        border: none;
        border-radius: {cfg.profile.toolbar_button_border_radius}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
    }}
    QPushButton:disabled {{
        opacity: 0.4;
    }}
    """


# ---------------------------------------------------------------------------
#  Buttons
# ---------------------------------------------------------------------------
def close_dialog_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Close' button in the About dialog."""
    a = cfg.about
    return f"""
    QPushButton {{
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {a.close_button_radius}px;
        padding: {a.close_button_padding_v}px {a.close_button_padding_h}px;
        color: {cfg.palette.text};
        font-size: {a.close_button_font_size}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
    }}
    """


def circular_button_style(cfg: GUIConfig, icon_size: int) -> str:
    """Style for small circular icon buttons."""
    radius = max(0, (icon_size - 1) // 2)
    return f"""
    QToolButton {{
        height: {icon_size}px;
        width: {icon_size}px;
        border-radius: {radius}px;
        border: none;
        background-color: transparent;
    }}
    QToolButton:hover {{
        background-color: {cfg.palette.button_hover};
    }}
    """


def icon_tab_button_style(cfg: GUIConfig) -> str:
    """Style for individual icon buttons inside the IconTabBar."""
    s = cfg.sidebar
    return f"""
    QPushButton {{
        background-color: transparent;
        border: {s.tab_button_border_width}px solid transparent;
        border-radius: {s.tab_button_radius}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    QPushButton:checked {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    """


def save_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Save' button in the settings footer."""
    return f"""
    QPushButton {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text_hover};
        border: 2px solid {cfg.palette.control};
        border-radius: {cfg.footer.button_radius}px;
        padding: {cfg.footer.button_padding_v}px {cfg.footer.button_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer.button_height}px;
    }}
    QPushButton:hover {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.control_hover};
    }}
    QPushButton:pressed {{
        background-color: {cfg.palette.button_hover};
        border-color: {cfg.palette.control_hover};
    }}
    QPushButton:disabled {{
        background-color: {cfg.palette.button};
        color: {cfg.palette.text_subtle};
        border-color: {cfg.palette.border};
    }}
    """


def reset_button_style(cfg: GUIConfig, active: bool) -> str:
    """Style for the 'Reset' split-button with dynamic split-line color."""
    if active:
        text = cfg.palette.text_hover
        bg_hover = cfg.palette.button_hover
        border = cfg.palette.reset
        border_hover = cfg.palette.reset_hover
        split_color = cfg.palette.reset
    else:
        text = cfg.palette.text_subtle
        bg_hover = cfg.palette.button
        border = cfg.palette.border
        border_hover = cfg.palette.border
        split_color = cfg.palette.border

    return f"""
    QToolButton {{
        background-color: {cfg.palette.button};
        color: {text};
        border: 2px solid {border};
        border-radius: {cfg.footer.button_radius}px;
        padding: {cfg.footer.button_padding_v}px {cfg.footer.button_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer.button_height}px;
    }}
    QToolButton:hover {{
        background-color: {bg_hover};
        border-color: {border_hover};
    }}
    QToolButton:pressed {{
        background-color: {bg_hover};
        border-color: {border_hover};
    }}
    QToolButton::menu-button {{
        background-color: transparent;
        border: none;
        border-left: 1px solid {split_color};
        width: {cfg.footer.menu_button_width}px;
    }}
    QToolButton::menu-arrow {{
        width: {cfg.footer.menu_arrow_size}px;
        height: {cfg.footer.menu_arrow_size}px;
    }}
    """


def reset_submenu_style(cfg: GUIConfig) -> str:
    """Style for the dropdown menu of the Reset button."""
    f = cfg.footer
    return f"""
    QMenu {{
        background-color: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: 4px;
        padding: {f.menu_padding}px;
    }}
    QMenu::separator {{
        height: 1px;
        background: {cfg.palette.border};
        margin: {f.menu_padding}px 0px;
    }}
    QMenu::item {{
        color: {cfg.palette.text};
        padding: {f.menu_item_padding_v}px {f.menu_item_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QMenu::item:selected {{
        background-color: {cfg.palette.control};
        color: {cfg.palette.text_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Text
# ---------------------------------------------------------------------------
def about_dialog_name_style(cfg: GUIConfig) -> str:
    """Style for the application name in the About dialog."""
    a = cfg.about
    return (
        f"color: {cfg.palette.text_hover}; "
        f"font-size: {a.name_font_size}px; "
        "font-weight: bold; "
        f"margin-top: {a.name_margin_top}px;"
    )


def about_dialog_version_style(cfg: GUIConfig) -> str:
    """Style for the version string in the About dialog."""
    a = cfg.about
    return (
        f"color: {cfg.palette.text}; "
        f"font-size: {a.version_font_size}px; "
        f"margin-top: {a.version_margin_top}px;"
    )


def about_dialog_description_style(cfg: GUIConfig) -> str:
    """Style for the description text in the About dialog."""
    a = cfg.about
    return (
        f"color: {cfg.palette.text_subtle}; "
        f"font-size: {a.body_font_size}px; "
        f"margin-top: {a.description_margin_top}px; "
        f"padding: 0 {a.description_padding_h}px;"
    )


def about_dialog_link_style(cfg: GUIConfig) -> str:
    """Style for the links in the About dialog."""
    a = cfg.about
    return f"font-size: {a.body_font_size}px; " f"margin-top: {a.link_margin_top}px;"


# ---------------------------------------------------------------------------
#  Window grid
# ---------------------------------------------------------------------------
def graphics_view_style(_: GUIConfig) -> str:
    """Transparent, borderless QGraphicsView."""
    return "background-color: transparent; border: none;"
