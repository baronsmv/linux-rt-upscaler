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
        color: {cfg.palette.text_primary};
        background-color: {cfg.palette.bg_surface};
        border: 1px solid {cfg.palette.border_subtle};
        padding: 4px;
        border-radius: 4px;
        font-size: {cfg.palette.font_size_sm}px;
    }}
    """


# ---------------------------------------------------------------------------
#  Filter bar
# ---------------------------------------------------------------------------
def filter_bar_line_edit_style(cfg: GUIConfig, *, hover: bool = False) -> str:
    """Style for the filter bar QLineEdit, with optional hover state."""
    bg = cfg.filter_hover_background if hover else cfg.filter_background
    return f"""
    QLineEdit {{
        border: 1px solid {cfg.filter_border_color};
        border-radius: {cfg.filter_border_radius}px;
        background: {bg};
        color: {cfg.filter_text_color};
        font-size: {cfg.filter_font_size}px;
        padding: 0px;
        selection-background-color: {cfg.filter_border_focus_color};
    }}
    QLineEdit:focus {{
        border-color: {cfg.filter_border_focus_color};
    }}
    """


# ---------------------------------------------------------------------------
#  Sidebar containers / tabs / scroll
# ---------------------------------------------------------------------------
def sidebar_container_style(cfg: GUIConfig) -> str:
    """Outer rounded container for sidebars."""
    return f"""
    QWidget#sidebar_container {{
        background-color: {cfg.sidebar_background};
        border-radius: 12px;
    }}
    """


def sidebar_tab_widget_style(cfg: GUIConfig) -> str:
    """QTabWidget and its tab bar inside a sidebar."""
    return f"""
    QTabWidget::pane {{
        border: none;
        background: {cfg.sidebar_background};
        border-radius: 0px 0px 12px 12px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {cfg.sidebar_tab_text_color};
        font-size: {cfg.sidebar_tab_font_size}px;
        font-weight: 500;
        padding: 10px 20px;
        margin-right: 4px;
        border: none;
        border-bottom: 2px solid transparent;
        min-width: 80px;
    }}
    QTabBar::tab:selected {{
        color: {cfg.sidebar_tab_text_color_active};
        border-bottom: 2px solid {cfg.sidebar_tab_indicator_color};
    }}
    QTabBar::tab:hover {{
        color: {cfg.sidebar_tab_text_color_active};
    }}
    QTabBar::tab:disabled {{
        color: {cfg.palette.text_disabled};
    }}
    """


def scroll_area_style(cfg: GUIConfig) -> str:
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
    font-size: {cfg.sidebar_section_title_size}px;
    font-weight: bold;
    color: {cfg.sidebar_section_title_color};
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 0px 4px 0px;
    """


def row_label_style(cfg: GUIConfig) -> str:
    """Label placed next to a control in a settings row."""
    return f"color: {cfg.sidebar_tab_text_color}; font-size: {cfg.sidebar_tab_font_size}px;"


def separator_line_style(cfg: GUIConfig) -> str:
    """Thin horizontal line used under section headers."""
    return f"color: {cfg.separator_line_color};"


def scrollbar_style(cfg: GUIConfig) -> str:
    """Custom vertical scrollbar for sidebars."""
    return f"""
    QScrollBar:vertical {{
        background: {cfg.sidebar_background};
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {cfg.scrollbar_handle_color};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {cfg.scrollbar_handle_hover_color};
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
    return f"background: {cfg.highlight_border_color}; border: none;"


def base_row_content_background_style(cfg: GUIConfig, *, highlighted: bool) -> str:
    """Background style for the content container of a BaseRow."""
    if highlighted and cfg.highlight_background_enabled:
        return f"background: {cfg.highlight_background_color}; border-radius: 4px;"
    return "background: transparent;"


def base_row_label_highlight_style(cfg: GUIConfig, *, color: str) -> str:
    """Label style that reflects highlight state."""
    return f"color: {color}; font-size: {cfg.sidebar_tab_font_size}px;"


def base_row_label_color(cfg: GUIConfig, *, highlighted: bool, enabled: bool) -> str:
    """Return the appropriate text color for a row label."""
    if not enabled:
        return cfg.control_disabled_text
    if highlighted:
        return cfg.highlight_label_color
    return cfg.sidebar_tab_text_color


# ---------------------------------------------------------------------------
#  Line edit (editable text fields)
# ---------------------------------------------------------------------------
def line_edit_style(cfg: GUIConfig, *, enabled: bool = True) -> str:
    """Base style for QLineEdit used inside settings rows."""
    bg = cfg.edit_background if enabled else cfg.edit_background_disabled
    text_color = cfg.edit_text_color if enabled else cfg.edit_text_color_disabled
    border = cfg.edit_border_color if enabled else cfg.control_disabled_border
    focus = cfg.edit_border_focus_color if enabled else cfg.control_disabled_border
    hover = cfg.edit_border_hover_color if enabled else cfg.control_disabled_border
    selection = cfg.edit_selection_background
    return f"""
    QLineEdit {{
        background: {bg};
        border: 1px solid {border};
        border-radius: {cfg.edit_border_radius}px;
        padding: {cfg.edit_padding_v}px {cfg.edit_padding_h}px;
        color: {text_color};
        font-size: {cfg.sidebar_tab_font_size}px;
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
    bg = cfg.combo_background if enabled else cfg.combo_background_disabled
    text_color = cfg.combo_text_color if enabled else cfg.combo_text_color_disabled
    border = cfg.combo_border_color if enabled else cfg.combo_border_color_disabled
    focus = cfg.combo_border_focus_color if enabled else cfg.control_disabled_border
    hover = cfg.combo_border_hover_color if enabled else cfg.control_disabled_border
    popup_bg = cfg.combo_popup_background
    popup_selection = cfg.combo_popup_selection_background
    popup_text = cfg.combo_popup_text_color

    return f"""
    QComboBox {{
        background: {bg};
        border: 1px solid {border};
        border-radius: {cfg.combo_border_radius}px;
        padding: {cfg.combo_padding_v}px {cfg.combo_padding_h}px;
        color: {text_color};
        font-size: {cfg.sidebar_tab_font_size}px;
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
        text_color = cfg.checkbox_disabled_color
        indicator_color = cfg.checkbox_disabled_color
    else:
        text_color = (
            cfg.highlight_label_color if highlighted else cfg.sidebar_tab_text_color
        )
        indicator_color = (
            cfg.highlight_border_color if highlighted else cfg.sidebar_checkbox_color
        )

    return f"""
    QCheckBox {{
        spacing: {cfg.checkbox_spacing}px;
        color: {text_color};
        font-size: {cfg.sidebar_tab_font_size}px;
        padding: {cfg.checkbox_padding_v}px 0;
    }}
    QCheckBox::indicator {{
        width: {cfg.checkbox_indicator_size}px;
        height: {cfg.checkbox_indicator_size}px;
        border: 2px solid {indicator_color};
        border-radius: {cfg.checkbox_indicator_radius}px;
        background: transparent;
    }}
    QCheckBox::indicator:checked {{
        background-color: {indicator_color};
        border-color: {indicator_color};
    }}
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
            background-color: {cfg.color_swatch_disabled_bg};
            border: 1px solid {cfg.control_disabled_border};
            border-radius: 4px;
        }}
        """
    border = cfg.color_swatch_border
    hover = cfg.sidebar_combo_border_focus
    return f"""
    QPushButton {{
        background-color: {current_color};
        border: 1px solid {border};
        border-radius: 4px;
    }}
    QPushButton:hover {{
        border-color: {hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Slider
# ---------------------------------------------------------------------------
def slider_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for a horizontal QSlider."""
    groove = cfg.slider_groove_bg if enabled else cfg.slider_groove_bg_disabled
    handle_color = (
        cfg.slider_handle_color if enabled else cfg.slider_handle_color_disabled
    )
    sub_page = (
        cfg.slider_handle_color if enabled else cfg.slider_sub_page_color_disabled
    )
    hover = (
        cfg.slider_handle_hover_color
        if enabled
        else cfg.slider_handle_hover_color_disabled
    )

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
    """


def slider_value_label_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for the QLabel that shows the slider value."""
    color = cfg.sidebar_tab_text_color if enabled else cfg.control_disabled_text
    return f"color: {color}; font-size: {cfg.sidebar_tab_font_size}px;"


# ---------------------------------------------------------------------------
#  Dialog
# ---------------------------------------------------------------------------
def dialog_style(cfg: GUIConfig) -> str:
    """Full stylesheet for QDialog used by ProfileDialog and WindowPickerDialog."""
    return f"""
    QDialog {{
        background-color: {cfg.dialog_background};
        color: {cfg.dialog_text_color};
    }}
    QLabel {{
        color: {cfg.dialog_label_color};
        font-size: {cfg.dialog_label_font_size}px;
    }}
    QLineEdit {{
        background: {cfg.dialog_input_background};
        border: 1px solid {cfg.dialog_input_border};
        border-radius: {cfg.dialog_input_border_radius}px;
        padding: {cfg.dialog_input_padding};
        color: {cfg.dialog_text_color};
    }}
    QLineEdit:focus {{
        border-color: {cfg.dialog_input_focus_border};
    }}
    QComboBox {{
        background: {cfg.dialog_input_background};
        border: 1px solid {cfg.dialog_input_border};
        border-radius: {cfg.dialog_input_border_radius}px;
        padding: {cfg.dialog_input_padding};
        color: {cfg.dialog_text_color};
        min-width: {cfg.dialog_combo_min_width}px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 0px;
    }}
    QComboBox QAbstractItemView {{
        background: {cfg.dialog_input_background};
        border: none;
        color: {cfg.dialog_text_color};
        selection-background-color: {cfg.dialog_input_focus_border};
    }}
    QPushButton {{
        background: {cfg.dialog_button_background};
        border: 1px solid {cfg.dialog_button_border};
        border-radius: {cfg.dialog_button_border_radius}px;
        padding: {cfg.dialog_button_padding};
        color: {cfg.dialog_text_color};
    }}
    QPushButton:hover {{
        background: {cfg.dialog_button_hover_background};
        border-color: {cfg.dialog_button_hover_border_color};
    }}
    QPushButton:pressed {{
        background: {cfg.dialog_button_pressed_background};
    }}
    QPushButton:disabled {{
        color: {cfg.dialog_button_disabled_color};
    }}
    QGroupBox {{
        font-size: {cfg.dialog_label_font_size}px;
        font-weight: bold;
        color: {cfg.dialog_groupbox_title_color};
        border: 1px solid {cfg.dialog_groupbox_border};
        border-radius: {cfg.dialog_groupbox_border_radius}px;
        margin-top: 8px;
        padding-top: 16px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
    }}
    QListWidget {{
        background: {cfg.dialog_list_background};
        border: 1px solid {cfg.dialog_list_border};
        border-radius: {cfg.dialog_list_border_radius}px;
        outline: none;
        color: {cfg.dialog_text_color};
    }}
    QListWidget::item {{
        padding: {cfg.dialog_list_item_padding};
        border-radius: {cfg.dialog_list_item_border_radius}px;
    }}
    QListWidget::item:hover {{
        background: {cfg.dialog_list_item_hover_background};
        color: {cfg.palette.text_primary};
    }}
    QListWidget::item:selected {{
        background: {cfg.dialog_list_item_selected_background};
        color: {cfg.palette.text_primary};
    }}
    """


def dialog_header_label_style(cfg: GUIConfig) -> str:
    """Style for the header label in Profile Editor dialog."""
    return "font-weight: bold;"


def icon_preview_style(cfg: GUIConfig) -> str:
    """Style for icon preview in Profile Editor dialog."""
    return f"border: 1px solid {cfg.icon_preview_border_color}; border-radius: 4px;"


def dialog_info_label_style(cfg: GUIConfig) -> str:
    """Style for info label in Profile Editor dialog."""
    return (
        f"color: {cfg.palette.text_dim}; "
        f"font-size: {cfg.palette.font_size_mid}px; "
        "padding-top: 6px;"
    )


def dialog_match_label_style(cfg: GUIConfig) -> str:
    """Style for match label in Profile Editor dialog."""
    return f"font-size: {cfg.dialog_match_label_font_size}px; font-weight: bold;"


# ---------------------------------------------------------------------------
#  Message box
# ---------------------------------------------------------------------------
def message_box_style(cfg: GUIConfig) -> str:
    """Style for the QMessageBox that displays messages."""
    return f"""
    QMessageBox {{
        background-color: {cfg.dialog_background};
        color: {cfg.dialog_text_color};
        font-size: {cfg.dialog_label_font_size}px;
    }}
    QMessageBox QLabel {{
        color: {cfg.dialog_text_color};
        font-size: {cfg.dialog_label_font_size}px;
    }}
    QMessageBox QPushButton {{
        background: {cfg.dialog_button_background};
        border: 1px solid {cfg.dialog_button_border};
        border-radius: {cfg.dialog_button_border_radius}px;
        padding: {cfg.dialog_button_padding};
        color: {cfg.dialog_text_color};
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background: {cfg.dialog_button_hover_background};
    }}
    QMessageBox QPushButton:pressed {{
        background: {cfg.dialog_button_pressed_background};
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
        color: {cfg.profile_item_text_color};
        background: {cfg.profile_item_background};
        border-radius: {cfg.profile_item_border_radius}px;
        padding: 4px 8px;
        border-left: {cfg.profile_item_indicator_width}px solid transparent;
    }}
    QListWidget::item:hover {{
        background: {cfg.profile_item_background_hover};
        color: {cfg.profile_item_text_color_active};
    }}
    QListWidget::item:selected {{
        background: {cfg.profile_item_background_active};
        color: {cfg.profile_item_text_color_active};
        border-left: {cfg.profile_item_indicator_width}px solid {cfg.profile_item_indicator_color};
    }}
    """


def profile_toolbar_button_style(cfg: GUIConfig) -> str:
    """Style for the small flat buttons (Add, Edit, Delete, Up, Down)."""
    return f"""
    QPushButton {{
        background: transparent;
        border: none;
        border-radius: {cfg.profile_toolbar_button_border_radius}px;
    }}
    QPushButton:hover {{
        background: {cfg.profile_toolbar_button_background_hover};
    }}
    QPushButton:disabled {{
        opacity: 0.4;
    }}
    """


def profile_toolbar_separator_style(cfg: GUIConfig) -> str:
    """Style for the profile toolbar separators."""
    return f"color: {cfg.profile_toolbar_separator};"


# ---------------------------------------------------------------------------
#  Footer buttons (Save, Reset)
# ---------------------------------------------------------------------------
def footer_save_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Save' button in the settings footer."""
    return f"""
    QPushButton {{
        background: {cfg.footer_save_bg};
        color: {cfg.footer_save_text};
        border: 2px solid {cfg.footer_save_border};
        border-radius: {cfg.footer_button_radius}px;
        padding: {cfg.footer_button_padding_v}px {cfg.footer_button_padding_h}px;
        font-size: {cfg.sidebar_tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer_button_height}px;
    }}
    QPushButton:hover {{
        background: {cfg.footer_save_hover_bg};
        border-color: {cfg.footer_save_hover_border};
    }}
    QPushButton:pressed {{
        background: {cfg.footer_save_hover_bg};
        border-color: {cfg.footer_save_border};
    }}
    QPushButton:disabled {{
        background: {cfg.footer_save_disabled_bg};
        color: {cfg.footer_save_disabled_text};
        border-color: {cfg.footer_save_disabled_border};
    }}
    """


def footer_reset_button_style(
    cfg: GUIConfig, *, main_active: bool, enabled: bool
) -> str:
    """Style for the 'Reset' split‑button with dynamic split‑line color."""
    bg = cfg.footer_reset_bg if main_active else cfg.footer_reset_disabled_bg
    text = cfg.footer_reset_text if main_active else cfg.footer_reset_disabled_text
    border = (
        cfg.footer_reset_border if main_active else cfg.footer_reset_disabled_border
    )
    hover_bg = (
        cfg.footer_reset_hover_bg if main_active else cfg.footer_reset_disabled_bg
    )
    hover_border = (
        cfg.footer_reset_hover_border
        if main_active
        else cfg.footer_reset_disabled_border
    )
    split_color = (
        cfg.footer_reset_split_border
        if main_active
        else cfg.footer_reset_disabled_border
    )

    if not enabled:
        bg = cfg.footer_reset_disabled_bg
        text = cfg.footer_reset_disabled_text
        border = cfg.footer_reset_disabled_border
        hover_bg = cfg.footer_reset_disabled_bg
        hover_border = cfg.footer_reset_disabled_border
        split_color = cfg.footer_reset_disabled_border

    return f"""
    QToolButton {{
        background: {bg};
        color: {text};
        border: 2px solid {border};
        border-radius: {cfg.footer_button_radius}px;
        padding: {cfg.footer_button_padding_v}px {cfg.footer_button_padding_h}px;
        font-size: {cfg.sidebar_tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer_button_height}px;
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
        background: {cfg.footer_menu_bg};
        border: 1px solid {cfg.footer_menu_border};
        border-radius: 4px;
        padding: 4px;
    }}
    QMenu::item {{
        color: {cfg.footer_menu_text};
        padding: 6px 24px;
        font-size: {cfg.sidebar_tab_font_size}px;
    }}
    QMenu::item:selected {{
        background: {cfg.footer_menu_selection_bg};
        color: {cfg.footer_menu_selection_text};
    }}
    """


# ---------------------------------------------------------------------------
#  About dialog (specific button)
# ---------------------------------------------------------------------------
def about_dialog_close_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Close' button in the About dialog."""
    return f"""
    QPushButton {{
        background: {cfg.dialog_button_background};
        border: 1px solid {cfg.dialog_button_border};
        border-radius: 8px;
        padding: 6px 18px;
        color: {cfg.dialog_text_color};
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {cfg.dialog_button_hover_background};
        border-color: {cfg.dialog_button_hover_border_color};
    }}
    """


# ---------------------------------------------------------------------------
#  Icon tab bar (right sidebar)
# ---------------------------------------------------------------------------
def icon_tab_bar_style(cfg: GUIConfig) -> str:
    """Background style for the IconTabBar widget."""
    return f"""
    QWidget {{
        background: {cfg.icon_tab_bar_background};
        border-radius: 8px;
    }}
    """


def icon_tab_button_style(cfg: GUIConfig) -> str:
    """Style for individual icon buttons inside the IconTabBar."""
    return f"""
    QPushButton {{
        background: transparent;
        border: 2px solid transparent;
        border-radius: 8px;
    }}
    QPushButton:hover {{
        background: {cfg.sidebar_tab_background_active};
        border-color: {cfg.sidebar_tab_indicator_color};
    }}
    QPushButton:checked {{
        background: {cfg.sidebar_tab_background_active};
        border-color: {cfg.sidebar_tab_indicator_color};
    }}
    """


# ---------------------------------------------------------------------------
#  Window grid
# ---------------------------------------------------------------------------


def graphics_view_style(cfg: GUIConfig) -> str:
    """Transparent, borderless QGraphicsView."""
    return "background: transparent; border: none;"
