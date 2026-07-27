from dataclasses import dataclass
from typing import Tuple

from .palette import GuiPalette
from .presets import DARK


@dataclass(frozen=True)
class GUIConfig:
    """
    Centralised GUI style and layout constants.
    All visual parameters live here; colors and fonts are delegated to
    :class:`GuiPalette` to make theme editing trivial.
    """

    # ── Theme token bag ────────────────────────────────────────
    palette: GuiPalette = DARK

    # ── Tile geometry ──────────────────────────────────────────
    tile_width: int = 340
    tile_height: int = 260
    tile_radius: int = 12
    tile_aspect_ratio: float = 4 / 3
    tile_spacing: int = 12
    tile_spacing_ratio: float = 0.075
    grid_margin: int = 20
    grid_columns: int = 3
    pop_scale: float = 1.05
    pop_duration: int = 200

    # ── Tile-specific colors (delegated to palette) ────────────
    tile_background: str = palette.bg_surface
    tile_hover_border: str = palette.accent_cyan
    tile_selected_border: str = palette.accent_blue
    tile_overlay_start: str = palette.tile_overlay_start
    tile_overlay_mid: str = palette.tile_overlay_mid
    tile_overlay_end: str = palette.tile_overlay_end
    tile_title_bg: str = palette.tile_title_bg
    tile_title_text: str = palette.tile_title_text

    # ── Drop shadow ────────────────────────────────────────────
    shadow_blur_radius: int = 20
    shadow_offset: Tuple[int, int] = (0, 4)
    shadow_hover_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
    shadow_hover_blur_radius: int = 30

    # ── Title font ─────────────────────────────────────────────
    title_font_family: str = palette.font_family
    title_font_size: int = palette.font_size_sm
    title_font_bold: bool = True
    title_text_color: str = palette.text_primary

    # ── Filter bar ─────────────────────────────────────────────
    filter_background = palette.bg_filter
    filter_hover_background = palette.bg_filter_hover
    filter_border_color = palette.border_subtle
    filter_border_focus_color = palette.accent_cyan
    filter_text_color = palette.text_filter
    filter_placeholder_color: str = palette.text_placeholder
    filter_icon_color: str = palette.accent_icon
    filter_font_size: int = 16
    filter_padding_h: int = 16
    filter_padding_v: int = 16
    filter_border_radius: int = 12
    filter_height: int = 80
    filter_icon_size: int = 24
    filter_icon_gap: int = -8
    filter_horizontal_margin: int = 18
    filter_vertical_margin: int = 6

    # ── Selection / focus ──────────────────────────────────────
    selection_border_width: int = 3
    hover_border_width: int = 2

    # ── Empty-grid placeholder ─────────────────────────────────
    empty_text: str = "No windows found"
    empty_text_color: str = palette.text_placeholder
    empty_text_size: int = 18

    # ── Timing ─────────────────────────────────────────────────
    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60
    min_columns: int = 1
    scroll_margin: int = 20

    # ── Sidebar common ─────────────────────────────────────────
    sidebar_width: int = 400
    sidebar_background: str = palette.bg_panel
    sidebar_tab_background: str = palette.bg_surface
    sidebar_tab_background_active: str = palette.bg_surface_hover
    sidebar_tab_text_color: str = palette.text_secondary
    sidebar_tab_text_color_active: str = palette.text_primary
    sidebar_tab_font_size: int = 18
    sidebar_tab_icon_size: int = 20
    sidebar_tab_indicator_color: str = palette.accent_blue
    sidebar_tab_indicator_width: int = 3
    sidebar_section_title_color: str = palette.text_dim
    sidebar_section_title_size: int = 18
    sidebar_row_height: int = 32
    sidebar_checkbox_color: str = palette.accent_blue
    sidebar_slider_color: str = palette.accent_blue
    sidebar_combo_border_color: str = palette.border_subtle
    sidebar_combo_border_focus: str = palette.accent_blue
    sidebar_icon_columns: int = 7
    sidebar_icon_size: int = 28
    sidebar_row_spacing: int = 6

    # ── Scrollbar ──────────────────────────────────────────────
    scrollbar_handle_color: str = palette.scrollbar_handle
    scrollbar_handle_hover_color: str = palette.scrollbar_handle_hover

    # ── Preview widget ─────────────────────────────────────────
    preview_background: str = palette.bg_preview

    # ── Profile dialog icon border ─────────────────────────────
    icon_preview_border_color: str = palette.border_icon_preview

    # ── Controls: disabled state ───────────────────────────────
    control_disabled_text: str = palette.text_disabled
    control_disabled_bg: str = palette.bg_surface
    control_disabled_border: str = palette.border_subtle

    # ── CheckBox ───────────────────────────────────────────────
    checkbox_indicator_size: int = 18
    checkbox_indicator_radius: int = 4
    checkbox_spacing: int = 8
    checkbox_padding_v: int = 4
    checkbox_disabled_color: str = palette.text_disabled

    # ── ComboBox ───────────────────────────────────────────────
    combo_background: str = palette.bg_input
    combo_background_disabled: str = palette.bg_input_disabled
    combo_text_color: str = palette.text_secondary
    combo_text_color_disabled: str = palette.text_disabled
    combo_border_color: str = palette.border_subtle
    combo_border_color_disabled: str = palette.border_subtle
    combo_border_hover_color: str = palette.border_hover
    combo_border_focus_color: str = palette.accent_blue
    combo_padding_h: int = 8
    combo_padding_v: int = 4
    combo_border_radius: int = 6
    combo_dropdown_width: int = 20
    combo_popup_background: str = palette.bg_input
    combo_popup_selection_background: str = palette.accent_blue
    combo_popup_text_color: str = palette.text_secondary

    # ── Slider ─────────────────────────────────────────────────
    slider_groove_bg: str = palette.slider_groove
    slider_groove_bg_disabled: str = palette.slider_groove_disabled
    slider_handle_color: str = palette.accent_blue
    slider_handle_color_disabled: str = palette.text_disabled
    slider_handle_hover_color: str = palette.accent_blue_light
    slider_handle_hover_color_disabled: str = palette.text_disabled
    slider_sub_page_color_disabled: str = palette.border_subtle
    slider_value_edit_width: int = 72

    # ── Editable text fields ───────────────────────────────────
    edit_background: str = palette.bg_input
    edit_background_disabled: str = palette.bg_input_disabled
    edit_text_color: str = palette.text_secondary
    edit_text_color_disabled: str = palette.text_disabled
    edit_border_radius: int = 6
    edit_padding_h: int = 8
    edit_padding_v: int = 4
    edit_border_color: str = palette.border_subtle
    edit_border_focus_color: str = palette.accent_blue
    edit_border_hover_color: str = palette.border_hover
    edit_selection_background: str = palette.accent_blue

    # ── Color swatch button ────────────────────────────────────
    color_swatch_width: int = 36
    color_swatch_height: int = 24
    color_swatch_border: str = palette.border_hover
    color_swatch_disabled_bg: str = palette.text_disabled
    path_browse_button_width: int = 32

    # ── Splitter handle ────────────────────────────────────────
    splitter_handle_width: int = 3
    splitter_handle_color: str = palette.bg_surface_hover
    splitter_handle_hover_color: str = palette.bg_surface_hover

    # ── Visual hints (highlight indicators) ────────────────────
    highlight_border_width: int = 4
    highlight_border_color: str = palette.accent_blue
    highlight_label_color: str = palette.accent_blue
    background_color: str = palette.bg_deep
    separator_line_color: str = palette.separator_color
    dialog_button_hover_border_color: str = palette.border_hover
    highlight_background_color: str = palette.accent_blue_bg
    dialog_button_pressed_background: str = palette.bg_button_pressed
    highlight_background_enabled: bool = True
    highlight_indicator_gap: int = 8

    # ── Footer buttons ─────────────────────────────────────────
    footer_button_height: int = 42
    footer_button_padding_h: int = 18
    footer_button_padding_v: int = 6
    footer_button_radius: int = 8
    footer_save_bg: str = palette.bg_surface
    footer_save_text: str = palette.text_primary
    footer_save_border: str = palette.accent_blue
    footer_save_hover_bg: str = palette.bg_surface_hover
    footer_save_hover_border: str = palette.accent_blue
    footer_save_disabled_bg: str = palette.bg_surface
    footer_save_disabled_text: str = palette.text_disabled
    footer_save_disabled_border: str = palette.border_subtle
    footer_reset_bg: str = palette.bg_surface
    footer_reset_text: str = palette.text_secondary
    footer_reset_border: str = palette.border_red
    footer_reset_hover_bg: str = palette.bg_surface_hover
    footer_reset_hover_border: str = palette.border_red_hover
    footer_reset_disabled_bg: str = palette.bg_surface
    footer_reset_disabled_text: str = palette.text_disabled
    footer_reset_disabled_border: str = palette.border_subtle
    footer_reset_split_border: str = palette.border_red
    footer_menu_bg: str = palette.bg_input
    footer_menu_border: str = palette.border_subtle
    footer_menu_text: str = palette.text_secondary
    footer_menu_selection_bg: str = palette.accent_blue
    footer_menu_selection_text: str = palette.text_primary

    # ── Profile sidebar ────────────────────────────────────────
    profile_title_font_size: int = sidebar_section_title_size
    profile_title_font_weight: str = "bold"
    profile_title_color: str = palette.text_dim
    profile_title_left_padding: int = 2
    profile_item_height: int = 40
    profile_item_icon_size: int = 32
    profile_item_text_color: str = palette.text_secondary
    profile_item_text_color_active: str = palette.text_primary
    profile_item_background: str = "transparent"
    profile_item_background_hover: str = palette.bg_surface_hover
    profile_item_background_active: str = palette.bg_surface_hover
    profile_item_border_radius: int = 6
    profile_item_spacing: int = 4
    profile_toolbar_button_size: int = 36
    profile_toolbar_button_icon_size: int = 24
    profile_toolbar_button_background_hover: str = palette.bg_surface_hover
    profile_toolbar_button_border_radius: int = 8
    profile_capture_icon_size: int = 128
    profile_toolbar_separator: str = palette.border_profile_sep
    profile_item_indicator_color: str = palette.accent_blue
    profile_item_indicator_width: int = 3

    # ── Icon tab bar (right sidebar) ───────────────────────────
    icon_tab_bar_background: str = palette.bg_icon_tab_bar

    # ── Dialog style constants ─────────────────────────────────
    dialog_background: str = palette.bg_surface
    dialog_text_color: str = palette.text_secondary
    dialog_label_color: str = palette.text_secondary
    dialog_label_font_size: int = palette.font_size_base
    dialog_input_background: str = palette.bg_input
    dialog_input_border: str = palette.border_subtle
    dialog_input_focus_border: str = palette.accent_blue
    dialog_input_border_radius: int = 4
    dialog_input_padding: str = "4px 8px"
    dialog_combo_min_width: int = 120
    dialog_button_background: str = palette.bg_surface_hover
    dialog_button_hover_background: str = palette.bg_input
    dialog_button_border: str = palette.border_subtle
    dialog_button_border_radius: int = palette.radius_sm
    dialog_button_padding: str = "4px 12px"
    dialog_button_disabled_color: str = palette.text_disabled
    dialog_groupbox_title_color: str = palette.text_dim
    dialog_groupbox_border: str = palette.border_profile_sep
    dialog_groupbox_border_radius: int = 6
    dialog_list_background: str = palette.bg_surface
    dialog_list_border: str = palette.border_profile_sep
    dialog_list_border_radius: int = 6
    dialog_list_item_padding: str = "4px 8px"
    dialog_list_item_border_radius: int = 4
    dialog_list_item_hover_background: str = palette.bg_surface_hover
    dialog_list_item_selected_background: str = palette.bg_input
    icon_color: str = palette.accent_icon
    dialog_match_label_font_size: int = 18
    dialog_icon_button_size: int = 32
    dialog_icon_button_icon_size: int = 24
