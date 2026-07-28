from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import GUIConfig


# ---------------------------------------------------------------------------
#  Global / tooltip
# ---------------------------------------------------------------------------
def tooltip_style(cfg: GUIConfig) -> str:
    """Style for QToolTip in both light and dark themes."""
    return f"""
    QToolTip {{
        color: {cfg.palette.text_hover};
        background-color: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        padding: 4px;
        border-radius: 4px;
        font-size: {cfg.dialog.label_font_size}px;
    }}
    """


# ---------------------------------------------------------------------------
#  Filter bar
# ---------------------------------------------------------------------------
def filter_bar_line_edit_style(cfg: GUIConfig, *, hover: bool = False) -> str:
    """Style for the filter bar QLineEdit, with optional hover state."""
    bg = cfg.palette.input_hover if hover else cfg.palette.input
    return f"""
    QLineEdit {{
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.filter.border_radius}px;
        background: {bg};
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
#  Sidebar containers / tabs / scroll
# ---------------------------------------------------------------------------
def sidebar_container_style(_: GUIConfig) -> str:
    """Outer rounded container for sidebars."""
    return f"""
    QWidget#sidebar_container {{
        border-radius: 12px;
    }}
    """


def sidebar_tab_widget_style(cfg: GUIConfig) -> str:
    """QTabWidget and its tab bar inside a sidebar."""
    return f"""
    QTabWidget::pane {{
        border: none;
        border-radius: 0px 0px 12px 12px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {cfg.palette.text};
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 500;
        padding: 10px 20px;
        margin-right: 4px;
        border: none;
        border-bottom: 2px solid transparent;
        min-width: 80px;
    }}
    QTabBar::tab:selected {{
        color: {cfg.palette.text_hover};
        border-bottom: 2px solid {cfg.palette.control};
    }}
    QTabBar::tab:hover {{
        color: {cfg.palette.text_hover};
    }}
    QTabBar::tab:disabled {{
        color: {cfg.palette.text_disabled};
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


def sidebar_section_label_style(cfg: GUIConfig) -> str:
    """Uppercase section title inside a settings tab."""
    return f"""
    font-size: {cfg.sidebar.section_title_size}px;
    font-weight: bold;
    color: {cfg.palette.text_subtle};
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 0px 4px 0px;
    """


def row_label_style(cfg: GUIConfig) -> str:
    """Label placed next to a control in a settings row."""
    return f"color: {cfg.palette.text}; font-size: {cfg.sidebar.tab_font_size}px;"


def separator_line_style(cfg: GUIConfig) -> str:
    """Thin horizontal line used under section headers."""
    return f"color: {cfg.palette.border};"


def scrollbar_style(cfg: GUIConfig) -> str:
    """Custom vertical scrollbar for sidebars."""
    return f"""
    QScrollBar:vertical {{
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {cfg.palette.control_subtle};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {cfg.palette.control_subtle_hover};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
    """


# ---------------------------------------------------------------------------
#  BaseRow highlight helpers
# ---------------------------------------------------------------------------
def base_row_indicator_style(cfg: GUIConfig) -> str:
    """Style for the colored indicator bar (left side of a highlighted row)."""
    return f"background: {cfg.palette.control}; border: none;"


def base_row_content_background_style(cfg: GUIConfig, *, highlighted: bool) -> str:
    """Background style for the content container of a BaseRow."""
    if highlighted and cfg.highlight_background_enabled:
        return f"background: {cfg.palette.control_disabled}; border-radius: 4px;"
    return "background: transparent;"


def base_row_label_highlight_style(cfg: GUIConfig, *, color: str) -> str:
    """Label style that reflects highlight state."""
    return f"color: {color}; font-size: {cfg.sidebar.tab_font_size}px;"


def base_row_label_color(cfg: GUIConfig, *, highlighted: bool, enabled: bool) -> str:
    """Return the appropriate text color for a row label."""
    if not enabled:
        return cfg.palette.text_disabled
    if highlighted:
        return cfg.palette.control
    return cfg.palette.text


# ---------------------------------------------------------------------------
#  Line edit (editable text fields)
# ---------------------------------------------------------------------------
def line_edit_style(cfg: GUIConfig, *, enabled: bool = True) -> str:
    """Base style for QLineEdit used inside settings rows."""
    bg = cfg.palette.input if enabled else cfg.palette.input_disabled
    text_color = cfg.palette.text if enabled else cfg.palette.text_disabled
    border = cfg.palette.border if enabled else cfg.palette.border
    focus = cfg.palette.control if enabled else cfg.palette.border
    hover = cfg.palette.border_hover if enabled else cfg.palette.border
    selection = cfg.palette.control
    return f"""
    QLineEdit {{
        background: {bg};
        border: 1px solid {border};
        border-radius: {cfg.edit_field.border_radius}px;
        padding: {cfg.edit_field.padding_v}px {cfg.edit_field.padding_h}px;
        color: {text_color};
        font-size: {cfg.sidebar.tab_font_size}px;
        selection-background-color: {selection};
    }}
    QLineEdit:hover {{
        border-color: {hover};
    }}
    QLineEdit:focus {{
        border-color: {focus};
    }}
    """


# ---------------------------------------------------------------------------
#  Combo box
# ---------------------------------------------------------------------------
def combo_box_style(cfg: GUIConfig, *, enabled: bool = True) -> str:
    """Style for QComboBox used inside settings rows."""
    bg = cfg.palette.input if enabled else cfg.palette.input_disabled
    text_color = cfg.palette.text if enabled else cfg.palette.text_disabled
    border = cfg.palette.border if enabled else cfg.palette.border
    focus = cfg.palette.control if enabled else cfg.palette.border
    hover = cfg.palette.border_hover if enabled else cfg.palette.border
    popup_bg = cfg.palette.input
    popup_selection = cfg.palette.control
    popup_text = cfg.palette.text

    return f"""
    QComboBox {{
        background: {bg};
        border: 1px solid {border};
        border-radius: {cfg.combo.border_radius}px;
        padding: {cfg.combo.padding_v}px {cfg.combo.padding_h}px;
        color: {text_color};
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QComboBox:hover {{
        border-color: {hover};
    }}
    QComboBox:focus {{
        border-color: {focus};
    }}
    QComboBox::drop-down {{
        width: 0px;
        background: transparent;
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        width: 0px;
        height: 0px;
    }}
    QComboBox QAbstractItemView {{
        background: {popup_bg};
        border: none;
        border-radius: 0px;
        padding: 0px;
        selection-background-color: {popup_selection};
        color: {popup_text};
        outline: none;
    }}
    """


# ---------------------------------------------------------------------------
#  Checkbox
# ---------------------------------------------------------------------------
def checkbox_style(
    cfg: GUIConfig, enabled: bool = True, highlighted: bool = False
) -> str:
    """Style for a QCheckBox inside a settings row."""
    if not enabled:
        text_color = cfg.palette.text_disabled
        indicator_color = cfg.palette.text_disabled
    else:
        text_color = cfg.palette.control if highlighted else cfg.palette.text
        indicator_color = cfg.palette.control if highlighted else cfg.palette.control

    return f"""
    QCheckBox {{
        spacing: {cfg.checkbox.spacing}px;
        color: {text_color};
        font-size: {cfg.sidebar.tab_font_size}px;
        padding: {cfg.checkbox.padding_v}px 0;
    }}
    QCheckBox::indicator {{
        width: {cfg.checkbox.indicator_size}px;
        height: {cfg.checkbox.indicator_size}px;
        border: 2px solid {indicator_color};
        border-radius: {cfg.checkbox.indicator_radius}px;
        background: transparent;
    }}
    QCheckBox::indicator:checked {{
        background-color: {indicator_color};
        border-color: {indicator_color};
    }}
    {tooltip_style(cfg)}
    """


# ---------------------------------------------------------------------------
#  Color swatch button
# ---------------------------------------------------------------------------
def color_swatch_style(
    cfg: GUIConfig, *, enabled: bool = True, current_color: str = "#000000"
) -> str:
    """Style for the QPushButton that acts as a color preview."""
    if not enabled:
        return f"""
        QPushButton {{
            background-color: {cfg.palette.text_disabled};
            border: 1px solid {cfg.palette.border};
            border-radius: 4px;
        }}
        """
    return f"""
    QPushButton {{
        background-color: {current_color};
        border: 1px solid {cfg.palette.border_hover};
        border-radius: 4px;
    }}
    QPushButton:hover {{
        border-color: {cfg.palette.control};
    }}
    """


# ---------------------------------------------------------------------------
#  Slider
# ---------------------------------------------------------------------------
def slider_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for a horizontal QSlider."""
    groove = cfg.palette.control_subtle if enabled else cfg.palette.control_disabled
    handle_color = cfg.palette.control if enabled else cfg.palette.text_disabled
    sub_page = cfg.palette.control if enabled else cfg.palette.border
    hover = cfg.palette.control_hover if enabled else cfg.palette.text_disabled

    return f"""
    QSlider::groove:horizontal {{
        border: none;
        height: 4px;
        background: {groove};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {handle_color};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {hover};
    }}
    QSlider::sub-page:horizontal {{
        background: {sub_page};
        border-radius: 2px;
    }}
    {tooltip_style(cfg)}
    """


def slider_value_label_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for the QLabel that shows the slider value."""
    color = cfg.palette.text if enabled else cfg.palette.text_disabled
    return f"color: {color}; font-size: {cfg.sidebar.tab_font_size}px;"


# ---------------------------------------------------------------------------
#  Dialog
# ---------------------------------------------------------------------------
def dialog_style(cfg: GUIConfig) -> str:
    """Full stylesheet for QDialog used by ProfileDialog and WindowPickerDialog."""
    return f"""
    QDialog {{
        background-color: {cfg.palette.background};
        color: {cfg.palette.text};
    }}
    QLabel {{
        color: {cfg.palette.text};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QLineEdit {{
        background: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text};
    }}
    QLineEdit:focus {{
        border-color: {cfg.palette.control};
    }}
    QComboBox {{
        background: {cfg.palette.input};
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
        background: {cfg.palette.input};
        border: none;
        color: {cfg.palette.text};
        selection-background-color: {cfg.palette.control};
    }}
    QPushButton {{
        background: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
    }}
    QPushButton:hover {{
        background: {cfg.palette.button_hover};
        border-color: {cfg.palette.border_hover};
    }}
    QPushButton:pressed {{
        background: {cfg.palette.button_hover};
    }}
    QPushButton:disabled {{
        color: {cfg.palette.text_disabled};
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
        background: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.list_border_radius}px;
        outline: none;
        color: {cfg.palette.text};
    }}
    QListWidget::item {{
        padding: {cfg.dialog.list_item_padding};
        border-radius: {cfg.dialog.list_item_border_radius}px;
    }}
    QListWidget::item:hover {{
        background: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
    }}
    QListWidget::item:selected {{
        background: {cfg.palette.control};
        color: {cfg.palette.text_hover};
    }}
    """


def dialog_header_label_style(_: GUIConfig) -> str:
    """Style for the header label in Profile Editor dialog."""
    return "font-weight: bold;"


def icon_preview_style(cfg: GUIConfig) -> str:
    """Style for icon preview in Profile Editor dialog."""
    return f"border: 1px solid {cfg.palette.border}; border-radius: 4px;"


def dialog_info_label_style(cfg: GUIConfig) -> str:
    """Style for info label in Profile Editor dialog."""
    return (
        f"color: {cfg.palette.text_subtle}; "
        f"font-size: {cfg.dialog.info_font_size}px; "
        "padding-top: 6px;"
    )


def dialog_match_label_style(cfg: GUIConfig) -> str:
    """Style for match label in Profile Editor dialog."""
    return f"font-size: {cfg.dialog.match_label_font_size}px; font-weight: bold;"


def dialog_icon_button_style(cfg: GUIConfig) -> str:
    """Style for icon button in Profile Editor dialog."""
    return f"""
    QToolButton {{
        background: transparent;
        border: none;
    }}
    QToolButton:hover {{
        background: {cfg.palette.button_hover};
        border-radius: 4px;
    }}
    """


# ---------------------------------------------------------------------------
#  Message box
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
        background: {cfg.palette.button};
        border: 1px solid {cfg.palette.border};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text};
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background: {cfg.palette.button_hover};
    }}
    QMessageBox QPushButton:pressed {{
        background: {cfg.palette.button_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Profile list (left sidebar)
# ---------------------------------------------------------------------------
def profile_list_style(cfg: GUIConfig) -> str:
    """Style for the QListWidget that displays profiles."""
    return f"""
    QListWidget {{
        background: transparent;
        border: none;
        outline: none;
    }}
    QListWidget::item {{
        color: {cfg.palette.text};
        background: transparent;
        border-radius: {cfg.profile.item_border_radius}px;
        padding: 4px 8px;
        border-left: {cfg.profile.indicator_width}px solid transparent;
    }}
    QListWidget::item:hover {{
        background: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
    }}
    QListWidget::item:selected {{
        background: {cfg.palette.button_hover};
        color: {cfg.palette.text_hover};
        border-left: {cfg.profile.indicator_width}px solid {cfg.palette.control};
    }}
    """


def profile_toolbar_button_style(cfg: GUIConfig) -> str:
    """Style for the small flat buttons (Add, Edit, Delete, Up, Down)."""
    return f"""
    QPushButton {{
        background: transparent;
        border: none;
        border-radius: {cfg.profile.toolbar_button_border_radius}px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.button_hover};
    }}
    QPushButton:disabled {{
        opacity: 0.4;
    }}
    """


def profile_toolbar_separator_style(cfg: GUIConfig) -> str:
    """Style for the profile toolbar separators."""
    return f"color: {cfg.palette.border};"


# ---------------------------------------------------------------------------
#  Footer buttons (Save, Reset)
# ---------------------------------------------------------------------------
def footer_save_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Save' button in the settings footer."""
    return f"""
    QPushButton {{
        background: {cfg.palette.button};
        color: {cfg.palette.text_hover};
        border: 2px solid {cfg.palette.control};
        border-radius: {cfg.footer.button_radius}px;
        padding: {cfg.footer.button_padding_v}px {cfg.footer.button_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer.button_height}px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    QPushButton:pressed {{
        background: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    QPushButton:disabled {{
        background: {cfg.palette.button};
        color: {cfg.palette.text_disabled};
        border-color: {cfg.palette.border};
    }}
    """


def footer_reset_button_style(
    cfg: GUIConfig, *, main_active: bool, enabled: bool
) -> str:
    """Style for the 'Reset' split-button with dynamic split-line color."""
    bg = cfg.palette.button if main_active else cfg.palette.button
    text = cfg.palette.text if main_active else cfg.palette.text_disabled
    border = cfg.palette.button_revert if main_active else cfg.palette.border
    hover_bg = cfg.palette.button_hover if main_active else cfg.palette.button
    hover_border = (
        cfg.palette.button_revert_hover if main_active else cfg.palette.border
    )
    split_color = cfg.palette.button_revert if main_active else cfg.palette.border

    if not enabled:
        bg = cfg.palette.button
        text = cfg.palette.text_disabled
        border = cfg.palette.border
        hover_bg = cfg.palette.button
        hover_border = cfg.palette.border
        split_color = cfg.palette.border

    return f"""
    QToolButton {{
        background: {bg};
        color: {text};
        border: 2px solid {border};
        border-radius: {cfg.footer.button_radius}px;
        padding: {cfg.footer.button_padding_v}px {cfg.footer.button_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer.button_height}px;
    }}
    QToolButton:hover {{
        background: {hover_bg};
        border-color: {hover_border};
    }}
    QToolButton:pressed {{
        background: {hover_bg};
        border-color: {border};
    }}
    QToolButton::menu-button {{
        background: transparent;
        border: none;
        border-left: 1px solid {split_color};
        width: 20px;
    }}
    QToolButton::menu-arrow {{
        width: 12px;
        height: 12px;
    }}
    """


def footer_menu_style(cfg: GUIConfig) -> str:
    """Style for the dropdown menu of the Reset button."""
    return f"""
    QMenu {{
        background: {cfg.palette.input};
        border: 1px solid {cfg.palette.border};
        border-radius: 4px;
        padding: 4px;
    }}
    QMenu::item {{
        color: {cfg.palette.text};
        padding: 6px 24px;
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QMenu::item:selected {{
        background: {cfg.palette.control};
        color: {cfg.palette.text_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  About dialog
# ---------------------------------------------------------------------------
def about_button_style(cfg: GUIConfig) -> str:
    """Style for the small '?' About button next to the filter bar."""
    return f"""
    QToolButton {{
        border-radius: 16px;
        border: none;
        background: transparent;
    }}
    QToolButton:hover {{
        background: {cfg.palette.button_hover};
    }}
    """


def about_dialog_style(cfg: GUIConfig) -> str:
    """Style for the About dialog itself (background, border, rounded corners)."""
    return f"""
    QDialog {{
        background-color: {cfg.palette.background};
        border: 1px solid {cfg.palette.border};
        border-radius: 12px;
    }}
    """


def about_dialog_name_style(cfg: GUIConfig) -> str:
    """Style for the application name in the About dialog."""
    return f"color: {cfg.palette.text_hover}; font-size: 24px; font-weight: bold; margin-top: 16px;"


def about_dialog_version_style(cfg: GUIConfig) -> str:
    """Style for the version string in the About dialog."""
    return f"color: {cfg.palette.text}; font-size: 20px; margin-top: 4px;"


def about_dialog_description_style(cfg: GUIConfig) -> str:
    """Style for the description text in the About dialog."""
    return f"color: {cfg.palette.text_subtle}; font-size: 18px; margin-top: 18px; padding: 0 24px;"


def about_dialog_link_style(_: GUIConfig) -> str:
    """Style for the GitHub link in the About dialog."""
    return f"font-size: 18px; margin-top: 10px;"


def about_dialog_close_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Close' button in the About dialog."""
    return f"""
    QPushButton {{
        background: {cfg.palette.button_hover};
        border: 1px solid {cfg.palette.border};
        border-radius: 8px;
        padding: 6px 18px;
        color: {cfg.palette.text};
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.input};
        border-color: {cfg.palette.border_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Icon tab bar (right sidebar)
# ---------------------------------------------------------------------------
def icon_tab_button_style(cfg: GUIConfig) -> str:
    """Style for individual icon buttons inside the IconTabBar."""
    return f"""
    QPushButton {{
        background: transparent;
        border: 2px solid transparent;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    QPushButton:checked {{
        background: {cfg.palette.button_hover};
        border-color: {cfg.palette.control};
    }}
    """


# ---------------------------------------------------------------------------
#  Window grid
# ---------------------------------------------------------------------------
def graphics_view_style(_: GUIConfig) -> str:
    """Transparent, borderless QGraphicsView."""
    return "background: transparent; border: none;"
