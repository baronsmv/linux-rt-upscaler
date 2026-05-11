from dataclasses import dataclass
from typing import Tuple


@dataclass
class GUIConfig:
    """
    Centralised GUI style and layout constants.

    All visual parameters live here, making it trivial to tune the
    appearance or add themes later.
    """

    # ---- Tile geometry -----------------------------------------------
    tile_width: int = 340
    tile_height: int = 260
    tile_radius: int = 12
    tile_aspect_ratio: float = (
        4 / 3
    )  # overrides default; 0 = use tile_width/tile_height
    tile_spacing: int = 12  # minimum absolute spacing (pixels)
    tile_spacing_ratio: float = (
        0.075  # proportional spacing (0 = use tile_spacing only)
    )
    grid_margin: int = 20  # inner margin of the grid container
    grid_columns: int = 3

    # ---- Pop-out animation -------------------------------------------
    pop_scale: float = 1.05  # maximum scale factor on hover
    pop_duration: int = 200  # animation duration in ms

    # ---- Colors ------------------------------------------------------
    background_color: str = "#121212"
    tile_background: str = "#1e1e1e"
    tile_hover_border: str = "#2b5b84"
    tile_selected_border: str = "#4a9eff"
    tile_title_overlay_start: Tuple[int, int, int, int] = (0, 0, 0, 0)
    tile_title_overlay_mid: Tuple[int, int, int, int] = (0, 0, 0, 160)
    tile_title_overlay_end: Tuple[int, int, int, int] = (0, 0, 0, 200)

    # ---- Drop shadow -------------------------------------------------
    shadow_blur_radius: int = 20
    shadow_offset: Tuple[int, int] = (0, 4)
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 120)
    # when hovered the shadow darkens and spreads
    shadow_hover_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
    shadow_hover_blur_radius: int = 30

    # ---- Title font --------------------------------------------------
    title_font_family: str = "Segoe UI"
    title_font_size: int = 12
    title_font_bold: bool = True
    title_text_color: str = "#ffffff"

    # ---- Filter bar --------------------------------------------------
    filter_background: str = "#2a2a2a"
    filter_hover_background: str = "#353535"
    filter_border_color: str = "#444"
    filter_border_focus_color: str = "#2b5b84"
    filter_text_color: str = "#eee"
    filter_placeholder_color: str = "#666"
    filter_icon_color: str = "#7A9EB1"
    filter_font_size: int = 16
    filter_padding_h: int = 16
    filter_padding_v: int = 16
    filter_border_radius: int = 12
    filter_height: int = 80
    filter_icon_size: int = 24
    filter_icon_gap: int = -8
    filter_horizontal_margin: int = 18
    filter_vertical_margin: int = 6

    # ---- Selection / focus indicators --------------------------------
    selection_border_width: int = 3
    hover_border_width: int = 2

    # ---- Empty-grid placeholder --------------------------------------
    empty_text: str = "No windows found"
    empty_text_color: str = "#666"
    empty_text_size: int = 18

    # ---- Timing ------------------------------------------------------
    auto_refresh_ms: int = 3000
    tile_preview_interval_ms: int = 40  # how often live preview updates

    # ---- Scaling / layout helpers ------------------------------------
    min_columns: int = 1
    scroll_margin: int = 20  # extra space for scroll-into-view

    # ---- Right and Left Sidebars -------------------------------------
    sidebar_width: int = 400
    sidebar_background: str = "#161616"
    sidebar_tab_background: str = "#1e1e1e"
    sidebar_tab_background_active: str = "#2c2c2c"
    sidebar_tab_text_color: str = "#cccccc"
    sidebar_tab_text_color_active: str = "#ffffff"
    sidebar_tab_font_size: int = 18
    sidebar_tab_icon_size: int = 20
    sidebar_tab_indicator_color: str = "#4a9eff"
    sidebar_tab_indicator_width: int = 3
    sidebar_section_title_color: str = "#888888"
    sidebar_section_title_size: int = 18
    sidebar_row_height: int = 32
    sidebar_checkbox_color: str = "#4a9eff"
    sidebar_slider_color: str = "#4a9eff"
    sidebar_combo_border_color: str = "#444444"
    sidebar_combo_border_focus: str = "#4a9eff"
    sidebar_icon_columns: int = 5
    sidebar_icon_size: int = 32
    sidebar_row_spacing: int = 6

    # ---- Control row generic states ------------------------------------
    control_disabled_text: str = "#555"
    control_disabled_bg: str = "#1e1e1e"
    control_disabled_border: str = "#444"

    # ---- Checkbox --------------------------------------------------------
    checkbox_indicator_size: int = 18
    checkbox_indicator_radius: int = 4
    checkbox_spacing: int = 8
    checkbox_padding_v: int = 4
    checkbox_disabled_color: str = "#555"

    # ---- Combo box -------------------------------------------------------
    combo_background: str = "#2a2a2c"
    combo_background_disabled: str = "#1e1e1e"
    combo_text_color: str = "#ddd"
    combo_text_color_disabled: str = "#555"
    combo_border_color: str = "#3a3a3c"
    combo_border_color_disabled: str = "#444"
    combo_border_hover_color: str = "#555555"
    combo_border_focus_color: str = "#4a9eff"
    combo_padding_h: int = 8
    combo_padding_v: int = 4
    combo_border_radius: int = 6
    combo_dropdown_width: int = 20
    combo_popup_background: str = "#2a2a2c"
    combo_popup_selection_background: str = "#4a9eff"
    combo_popup_text_color: str = "#ddd"

    # ---- Slider ----------------------------------------------------------
    slider_groove_bg: str = "#333"
    slider_groove_bg_disabled: str = "#222"
    slider_handle_color: str = "#4a9eff"  # overridden by sidebar_slider_color
    slider_handle_color_disabled: str = "#555"
    slider_handle_hover_color: str = "#6aade5"
    slider_handle_hover_color_disabled: str = "#555"
    slider_sub_page_color_disabled: str = "#444"
    slider_value_edit_width: int = 72

    # ---- Editable text fields (LineEdit, editable sliders, path picker) ---
    edit_background: str = "#2a2a2c"
    edit_background_disabled: str = "#1e1e1e"
    edit_text_color: str = "#ddd"
    edit_text_color_disabled: str = "#555"
    edit_border_radius: int = 6
    edit_padding_h: int = 8
    edit_padding_v: int = 4
    edit_border_color: str = "#3a3a3c"
    edit_border_focus_color: str = "#4a9eff"
    edit_border_hover_color: str = "#555555"
    edit_selection_background: str = "#4a9eff"

    # ---- Color swatch button ---------------------------------------------
    color_swatch_width: int = 36
    color_swatch_height: int = 24
    color_swatch_border: str = "#777"
    color_swatch_disabled_bg: str = "#555"

    # ---- Path picker browse button ---------------------------------------
    path_browse_button_width: int = 32

    # ---- Splitter handle style ---------------------------------------
    splitter_handle_width: int = 3
    splitter_handle_color: str = "#2a2a2a"
    splitter_handle_hover_color: str = "#2a2a2a"

    # ---- Visual hints for non-default values -------------------------
    highlight_border_width: int = 4
    highlight_border_color: str = "#5b9eff"
    highlight_label_color: str = "#5b9eff"
    highlight_background_color: str = "#1a2b3c"
    highlight_background_enabled: bool = True
    highlight_indicator_gap: int = 8

    # ---- Footer buttons -------------------------------------------------
    footer_button_height: int = 42  # consistent total height
    footer_button_padding_h: int = 18
    footer_button_padding_v: int = 6
    footer_button_radius: int = 8

    # Save button
    footer_save_bg: str = "#1e1e1e"  # sidebar_tab_background
    footer_save_text: str = "#ffffff"  # sidebar_tab_text_color_active
    footer_save_border: str = "#4a9eff"  # sidebar_tab_indicator_color
    footer_save_hover_bg: str = "#2c2c2c"  # sidebar_tab_background_active
    footer_save_hover_border: str = "#4a9eff"  # sidebar_combo_border_focus
    footer_save_disabled_bg: str = "#1e1e1e"
    footer_save_disabled_text: str = "#555"
    footer_save_disabled_border: str = "#444"

    # Reset button (main area)
    footer_reset_bg: str = "#1e1e1e"
    footer_reset_text: str = "#cccccc"
    footer_reset_border: str = "#914343"
    footer_reset_hover_bg: str = "#2c2c2c"
    footer_reset_hover_border: str = "#b55a5a"
    footer_reset_disabled_bg: str = "#1e1e1e"
    footer_reset_disabled_text: str = "#555"
    footer_reset_disabled_border: str = "#444"
    footer_reset_split_border: str = "#914343"
    footer_reset_dropdown_border_inactive: str = "#6b2e2e"

    # Reset dropdown menu
    footer_menu_bg: str = "#2a2a2c"  # combo_popup_background
    footer_menu_border: str = "#444444"  # sidebar_combo_border_color
    footer_menu_text: str = "#ddd"  # combo_popup_text_color
    footer_menu_selection_bg: str = "#4a9eff"  # combo_popup_selection_background
    footer_menu_selection_text: str = "#ffffff"

    # ---- Profile sidebar ------------------------------------------------
    profile_title_font_size: int = 18
    profile_title_font_weight: str = "bold"
    profile_title_color: str = "#888888"
    profile_item_height: int = 40
    profile_item_icon_size: int = 32
    profile_item_text_color: str = "#cccccc"
    profile_item_text_color_active: str = "#ffffff"
    profile_item_background: str = "transparent"
    profile_item_background_hover: str = "#2c2c2c"
    profile_item_background_active: str = "#2c2c2c"
    profile_item_border_radius: int = 6
    profile_item_spacing: int = 4
    profile_toolbar_button_size: int = 36
    profile_toolbar_button_icon_size: int = 24
    profile_toolbar_button_background_hover: str = "#2c2c2c"
    profile_toolbar_button_border_radius: int = 8
    profile_capture_icon_size: int = 128

    # ---- Dialog style constants -----------------------------------------
    dialog_background: str = "#1e1e1e"
    dialog_text_color: str = "#ddd"
    dialog_label_color: str = "#ccc"
    dialog_label_font_size: int = 14
    dialog_input_background: str = "#2a2a2c"
    dialog_input_border: str = "#3a3a3c"
    dialog_input_focus_border: str = "#4a9eff"
    dialog_input_border_radius: int = 4
    dialog_input_padding: str = "4px 8px"
    dialog_combo_min_width: int = 120
    dialog_button_background: str = "#2c2c2c"
    dialog_button_hover_background: str = "#3a3a3c"
    dialog_button_pressed_background: str = "#222"
    dialog_button_border: str = "#444"
    dialog_button_border_radius: int = 4
    dialog_button_padding: str = "4px 12px"
    dialog_button_disabled_color: str = "#555"
    dialog_groupbox_title_color: str = "#888"
    dialog_groupbox_border: str = "#333"
    dialog_groupbox_border_radius: int = 6
    dialog_list_background: str = "#1e1e1e"
    dialog_list_border: str = "#333"
    dialog_list_border_radius: int = 6
    dialog_list_item_padding: str = "4px 8px"
    dialog_list_item_border_radius: int = 4
    dialog_list_item_hover_background: str = "#2c2c2c"
    dialog_list_item_selected_background: str = "#3a3a3c"
    dialog_match_label_font_size: int = 18
    dialog_icon_button_size: int = 32
    dialog_icon_button_icon_size: int = 24
