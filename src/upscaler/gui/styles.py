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
        font-size: {cfg.dialog.label_font_size}px;
    }}
    """


# ---------------------------------------------------------------------------
#  Filter bar
# ---------------------------------------------------------------------------
def filter_bar_line_edit_style(cfg: GUIConfig, *, hover: bool = False) -> str:
    """Style for the filter bar QLineEdit, with optional hover state."""
    bg = cfg.palette.bg_filter_hover if hover else cfg.palette.bg_filter
    return f"""
    QLineEdit {{
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: {cfg.filter.border_radius}px;
        background: {bg};
        color: {cfg.palette.text_filter};
        font-size: {cfg.filter.font_size}px;
        padding: 0px;
        selection-background-color: {cfg.palette.accent_secondary};
    }}
    QLineEdit:focus {{
        border-color: {cfg.palette.accent_secondary};
    }}
    """


# ---------------------------------------------------------------------------
#  Sidebar containers / tabs / scroll
# ---------------------------------------------------------------------------
def sidebar_container_style(cfg: GUIConfig) -> str:
    """Outer rounded container for sidebars."""
    return f"""
    QWidget#sidebar_container {{
        background-color: {cfg.palette.bg_panel};
        border-radius: 12px;
    }}
    """


def sidebar_tab_widget_style(cfg: GUIConfig) -> str:
    """QTabWidget and its tab bar inside a sidebar."""
    return f"""
    QTabWidget::pane {{
        border: none;
        background: {cfg.palette.bg_panel};
        border-radius: 0px 0px 12px 12px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {cfg.palette.text_secondary};
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 500;
        padding: 10px 20px;
        margin-right: 4px;
        border: none;
        border-bottom: 2px solid transparent;
        min-width: 80px;
    }}
    QTabBar::tab:selected {{
        color: {cfg.palette.text_primary};
        border-bottom: 2px solid {cfg.palette.accent_primary};
    }}
    QTabBar::tab:hover {{
        color: {cfg.palette.text_primary};
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
    font-size: {cfg.sidebar.section_title_size}px;
    font-weight: bold;
    color: {cfg.palette.text_dim};
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 12px 0px 4px 0px;
    """


def row_label_style(cfg: GUIConfig) -> str:
    """Label placed next to a control in a settings row."""
    return f"color: {cfg.palette.text_secondary}; font-size: {cfg.sidebar.tab_font_size}px;"


def separator_line_style(cfg: GUIConfig) -> str:
    """Thin horizontal line used under section headers."""
    return f"color: {cfg.palette.separator_color};"


def scrollbar_style(cfg: GUIConfig) -> str:
    """Custom vertical scrollbar for sidebars."""
    return f"""
    QScrollBar:vertical {{
        background: {cfg.palette.bg_panel};
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {cfg.palette.scrollbar_handle};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {cfg.palette.scrollbar_handle_hover};
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
    return f"background: {cfg.palette.accent_primary}; border: none;"


def base_row_content_background_style(cfg: GUIConfig, *, highlighted: bool) -> str:
    """Background style for the content container of a BaseRow."""
    if highlighted and cfg.highlight_background_enabled:
        return f"background: {cfg.palette.accent_primary_bg}; border-radius: 4px;"
    return "background: transparent;"


def base_row_label_highlight_style(cfg: GUIConfig, *, color: str) -> str:
    """Label style that reflects highlight state."""
    return f"color: {color}; font-size: {cfg.sidebar.tab_font_size}px;"


def base_row_label_color(cfg: GUIConfig, *, highlighted: bool, enabled: bool) -> str:
    """Return the appropriate text color for a row label."""
    if not enabled:
        return cfg.palette.text_disabled
    if highlighted:
        return cfg.palette.accent_primary
    return cfg.palette.text_secondary


# ---------------------------------------------------------------------------
#  Line edit (editable text fields)
# ---------------------------------------------------------------------------
def line_edit_style(cfg: GUIConfig, *, enabled: bool = True) -> str:
    """Base style for QLineEdit used inside settings rows."""
    bg = cfg.palette.bg_input if enabled else cfg.palette.bg_input_disabled
    text_color = cfg.palette.text_secondary if enabled else cfg.palette.text_disabled
    border = cfg.palette.border_subtle if enabled else cfg.palette.border_subtle
    focus = cfg.palette.accent_primary if enabled else cfg.palette.border_subtle
    hover = cfg.palette.border_hover if enabled else cfg.palette.border_subtle
    selection = cfg.palette.accent_primary
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
    bg = cfg.palette.bg_input if enabled else cfg.palette.bg_input_disabled
    text_color = cfg.palette.text_secondary if enabled else cfg.palette.text_disabled
    border = cfg.palette.border_subtle if enabled else cfg.palette.border_subtle
    focus = cfg.palette.accent_primary if enabled else cfg.palette.border_subtle
    hover = cfg.palette.border_hover if enabled else cfg.palette.border_subtle
    popup_bg = cfg.palette.bg_input
    popup_selection = cfg.palette.accent_primary
    popup_text = cfg.palette.text_secondary

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
        text_color = (
            cfg.palette.accent_primary if highlighted else cfg.palette.text_secondary
        )
        indicator_color = (
            cfg.palette.accent_primary if highlighted else cfg.palette.accent_primary
        )

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
            border: 1px solid {cfg.palette.border_subtle};
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
        border-color: {cfg.palette.accent_primary};
    }}
    """


# ---------------------------------------------------------------------------
#  Slider
# ---------------------------------------------------------------------------
def slider_style(cfg: GUIConfig, enabled: bool = True) -> str:
    """Style for a horizontal QSlider."""
    groove = (
        cfg.palette.slider_groove if enabled else cfg.palette.slider_groove_disabled
    )
    handle_color = cfg.palette.accent_primary if enabled else cfg.palette.text_disabled
    sub_page = cfg.palette.accent_primary if enabled else cfg.palette.border_subtle
    hover = cfg.palette.accent_primary_light if enabled else cfg.palette.text_disabled

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
    color = cfg.palette.text_secondary if enabled else cfg.palette.text_disabled
    return f"color: {color}; font-size: {cfg.sidebar.tab_font_size}px;"


# ---------------------------------------------------------------------------
#  Dialog
# ---------------------------------------------------------------------------
def dialog_style(cfg: GUIConfig) -> str:
    """Full stylesheet for QDialog used by ProfileDialog and WindowPickerDialog."""
    return f"""
    QDialog {{
        background-color: {cfg.palette.bg_surface};
        color: {cfg.palette.text_secondary};
    }}
    QLabel {{
        color: {cfg.palette.text_secondary};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QLineEdit {{
        background: {cfg.palette.bg_input};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text_secondary};
    }}
    QLineEdit:focus {{
        border-color: {cfg.palette.accent_primary};
    }}
    QComboBox {{
        background: {cfg.palette.bg_input};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: {cfg.dialog.input_border_radius}px;
        padding: {cfg.dialog.input_padding};
        color: {cfg.palette.text_secondary};
        min-width: {cfg.dialog.combo_min_width}px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 0px;
    }}
    QComboBox QAbstractItemView {{
        background: {cfg.palette.bg_input};
        border: none;
        color: {cfg.palette.text_secondary};
        selection-background-color: {cfg.palette.accent_primary};
    }}
    QPushButton {{
        background: {cfg.palette.bg_surface_hover};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text_secondary};
    }}
    QPushButton:hover {{
        background: {cfg.palette.bg_input};
        border-color: {cfg.palette.border_hover};
    }}
    QPushButton:pressed {{
        background: {cfg.palette.bg_button_pressed};
    }}
    QPushButton:disabled {{
        color: {cfg.palette.text_disabled};
    }}
    QGroupBox {{
        font-size: {cfg.dialog.label_font_size}px;
        font-weight: bold;
        color: {cfg.palette.text_dim};
        border: 1px solid {cfg.palette.border_profile_separator};
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
        background: {cfg.palette.bg_surface};
        border: 1px solid {cfg.palette.border_profile_separator};
        border-radius: {cfg.dialog.list_border_radius}px;
        outline: none;
        color: {cfg.palette.text_secondary};
    }}
    QListWidget::item {{
        padding: {cfg.dialog.list_item_padding};
        border-radius: {cfg.dialog.list_item_border_radius}px;
    }}
    QListWidget::item:hover {{
        background: {cfg.palette.bg_surface_hover};
        color: {cfg.palette.text_primary};
    }}
    QListWidget::item:selected {{
        background: {cfg.palette.bg_input};
        color: {cfg.palette.text_primary};
    }}
    """


def dialog_header_label_style(cfg: GUIConfig) -> str:
    """Style for the header label in Profile Editor dialog."""
    return "font-weight: bold;"


def icon_preview_style(cfg: GUIConfig) -> str:
    """Style for icon preview in Profile Editor dialog."""
    return f"border: 1px solid {cfg.palette.border_icon_preview}; border-radius: 4px;"


def dialog_info_label_style(cfg: GUIConfig) -> str:
    """Style for info label in Profile Editor dialog."""
    return (
        f"color: {cfg.palette.text_dim}; "
        f"font-size: {cfg.dialog.info_font_size}px; "
        "padding-top: 6px;"
    )


def dialog_match_label_style(cfg: GUIConfig) -> str:
    """Style for match label in Profile Editor dialog."""
    return f"font-size: {cfg.dialog.match_label_font_size}px; font-weight: bold;"


# ---------------------------------------------------------------------------
#  Message box
# ---------------------------------------------------------------------------
def message_box_style(cfg: GUIConfig) -> str:
    """Style for the QMessageBox that displays messages."""
    return f"""
    QMessageBox {{
        background-color: {cfg.palette.bg_surface};
        color: {cfg.palette.text_secondary};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QMessageBox QLabel {{
        color: {cfg.palette.text_secondary};
        font-size: {cfg.dialog.label_font_size}px;
    }}
    QMessageBox QPushButton {{
        background: {cfg.palette.bg_surface_hover};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: {cfg.dialog.button_border_radius}px;
        padding: {cfg.dialog.button_padding};
        color: {cfg.palette.text_secondary};
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background: {cfg.palette.bg_input};
    }}
    QMessageBox QPushButton:pressed {{
        background: {cfg.palette.bg_button_pressed};
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
        color: {cfg.palette.text_secondary};
        background: transparent;
        border-radius: {cfg.profile.item_border_radius}px;
        padding: 4px 8px;
        border-left: {cfg.profile.indicator_width}px solid transparent;
    }}
    QListWidget::item:hover {{
        background: {cfg.palette.bg_surface_hover};
        color: {cfg.palette.text_primary};
    }}
    QListWidget::item:selected {{
        background: {cfg.palette.bg_surface_hover};
        color: {cfg.palette.text_primary};
        border-left: {cfg.profile.indicator_width}px solid {cfg.palette.accent_primary};
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
        background: {cfg.palette.bg_surface_hover};
    }}
    QPushButton:disabled {{
        opacity: 0.4;
    }}
    """


def profile_toolbar_separator_style(cfg: GUIConfig) -> str:
    """Style for the profile toolbar separators."""
    return f"color: {cfg.palette.border_profile_separator};"


# ---------------------------------------------------------------------------
#  Footer buttons (Save, Reset)
# ---------------------------------------------------------------------------
def footer_save_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Save' button in the settings footer."""
    return f"""
    QPushButton {{
        background: {cfg.palette.bg_surface};
        color: {cfg.palette.text_primary};
        border: 2px solid {cfg.palette.accent_primary};
        border-radius: {cfg.footer.button_radius}px;
        padding: {cfg.footer.button_padding_v}px {cfg.footer.button_padding_h}px;
        font-size: {cfg.sidebar.tab_font_size}px;
        font-weight: 600;
        height: {cfg.footer.button_height}px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.bg_surface_hover};
        border-color: {cfg.palette.accent_primary};
    }}
    QPushButton:pressed {{
        background: {cfg.palette.bg_surface_hover};
        border-color: {cfg.palette.accent_primary};
    }}
    QPushButton:disabled {{
        background: {cfg.palette.bg_surface};
        color: {cfg.palette.text_disabled};
        border-color: {cfg.palette.border_subtle};
    }}
    """


def footer_reset_button_style(
    cfg: GUIConfig, *, main_active: bool, enabled: bool
) -> str:
    """Style for the 'Reset' split-button with dynamic split-line color."""
    bg = cfg.palette.bg_surface if main_active else cfg.palette.bg_surface
    text = cfg.palette.text_secondary if main_active else cfg.palette.text_disabled
    border = cfg.palette.border_danger if main_active else cfg.palette.border_subtle
    hover_bg = cfg.palette.bg_surface_hover if main_active else cfg.palette.bg_surface
    hover_border = (
        cfg.palette.border_danger_hover if main_active else cfg.palette.border_subtle
    )
    split_color = (
        cfg.palette.border_danger if main_active else cfg.palette.border_subtle
    )

    if not enabled:
        bg = cfg.palette.bg_surface
        text = cfg.palette.text_disabled
        border = cfg.palette.border_subtle
        hover_bg = cfg.palette.bg_surface
        hover_border = cfg.palette.border_subtle
        split_color = cfg.palette.border_subtle

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
        background: {cfg.palette.bg_input};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: 4px;
        padding: 4px;
    }}
    QMenu::item {{
        color: {cfg.palette.text_secondary};
        padding: 6px 24px;
        font-size: {cfg.sidebar.tab_font_size}px;
    }}
    QMenu::item:selected {{
        background: {cfg.palette.accent_primary};
        color: {cfg.palette.text_primary};
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
        background: {cfg.palette.bg_surface_hover};
    }}
    """


def about_dialog_style(cfg: GUIConfig) -> str:
    """Style for the About dialog itself (background, border, rounded corners)."""
    return f"""
    QDialog {{
        background-color: {cfg.palette.bg_surface};
        border: 1px solid {cfg.palette.border_profile_separator};
        border-radius: 12px;
    }}
    """


def about_dialog_name_style(cfg: GUIConfig) -> str:
    """Style for the application name in the About dialog."""
    return f"color: {cfg.palette.text_primary}; font-size: 24px; font-weight: bold; margin-top: 16px;"


def about_dialog_version_style(cfg: GUIConfig) -> str:
    """Style for the version string in the About dialog."""
    return f"color: {cfg.palette.text_secondary}; font-size: 20px; margin-top: 4px;"


def about_dialog_description_style(cfg: GUIConfig) -> str:
    """Style for the description text in the About dialog."""
    return f"color: {cfg.palette.text_dim}; font-size: 18px; margin-top: 18px; padding: 0 24px;"


def about_dialog_link_style(cfg: GUIConfig) -> str:
    """Style for the GitHub link in the About dialog."""
    return f"font-size: 18px; margin-top: 10px;"


def about_dialog_close_button_style(cfg: GUIConfig) -> str:
    """Style for the 'Close' button in the About dialog."""
    return f"""
    QPushButton {{
        background: {cfg.palette.bg_surface_hover};
        border: 1px solid {cfg.palette.border_subtle};
        border-radius: 8px;
        padding: 6px 18px;
        color: {cfg.palette.text_secondary};
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {cfg.palette.bg_input};
        border-color: {cfg.palette.border_hover};
    }}
    """


# ---------------------------------------------------------------------------
#  Icon tab bar (right sidebar)
# ---------------------------------------------------------------------------
def icon_tab_bar_style(cfg: GUIConfig) -> str:
    """Background style for the IconTabBar widget."""
    return f"""
    QWidget {{
        background: {cfg.palette.bg_icon_tab_bar};
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
        background: {cfg.palette.bg_surface_hover};
        border-color: {cfg.palette.accent_primary};
    }}
    QPushButton:checked {{
        background: {cfg.palette.bg_surface_hover};
        border-color: {cfg.palette.accent_primary};
    }}
    """


# ---------------------------------------------------------------------------
#  Window grid
# ---------------------------------------------------------------------------
def graphics_view_style(cfg: GUIConfig) -> str:
    """Transparent, borderless QGraphicsView."""
    return "background: transparent; border: none;"
