from dataclasses import dataclass, field
from typing import Tuple

from .palette import GuiPalette
from .presets import DARK


@dataclass
class GUIConfig:
    """
    Centralised GUI style and layout constants.
    All visual parameters live here; colors and fonts are delegated to
    :class:`GuiPalette` to make theme editing trivial.
    """

    # ── Theme token bag ────────────────────────────────────────
    palette: GuiPalette = field(default_factory=lambda: DARK)

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

    # ── Tile‑specific colors (delegated to palette) ────────────
    @property
    def main_background(self) -> str:
        return self.palette.bg_deep

    @property
    def tile_background(self) -> str:
        return self.palette.bg_surface

    @property
    def tile_hover_border(self) -> str:
        return self.palette.accent_cyan

    @property
    def tile_selected_border(self) -> str:
        return self.palette.accent_blue

    @property
    def tile_title_overlay_start(self) -> Tuple[int, int, int, int]:
        return (0, 0, 0, 0)

    @property
    def tile_title_overlay_mid(self) -> Tuple[int, int, int, int]:
        return (0, 0, 0, 160)

    @property
    def tile_title_overlay_end(self) -> Tuple[int, int, int, int]:
        return (0, 0, 0, 200)

    # ── Drop shadow ────────────────────────────────────────────
    shadow_blur_radius: int = 20
    shadow_offset: Tuple[int, int] = (0, 4)

    @property
    def shadow_color(self) -> Tuple[int, int, int, int]:
        return self.palette.shadow_color

    shadow_hover_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
    shadow_hover_blur_radius: int = 30

    # ── Title font ─────────────────────────────────────────────
    @property
    def title_font_family(self) -> str:
        return self.palette.font_family

    @property
    def title_font_size(self) -> int:
        return self.palette.font_size_sm

    title_font_bold: bool = True

    @property
    def title_text_color(self) -> str:
        return self.palette.text_primary

    # ── Filter bar ─────────────────────────────────────────────
    @property
    def filter_background(self) -> str:
        return self.palette.bg_filter

    @property
    def filter_hover_background(self) -> str:
        return self.palette.bg_filter_hover

    @property
    def filter_border_color(self) -> str:
        return self.palette.border_subtle

    @property
    def filter_border_focus_color(self) -> str:
        return self.palette.accent_cyan

    @property
    def filter_text_color(self) -> str:
        return self.palette.text_filter

    @property
    def filter_placeholder_color(self) -> str:
        return self.palette.text_placeholder

    @property
    def filter_icon_color(self) -> str:
        return self.palette.accent_icon

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

    # ── Empty‑grid placeholder ─────────────────────────────────
    empty_text: str = "No windows found"

    @property
    def empty_text_color(self) -> str:
        return self.palette.text_placeholder

    empty_text_size: int = 18

    # ── Timing ─────────────────────────────────────────────────
    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60

    min_columns: int = 1
    scroll_margin: int = 20

    # ── Sidebar common ─────────────────────────────────────────
    sidebar_width: int = 400

    @property
    def sidebar_background(self) -> str:
        return self.palette.bg_panel

    @property
    def sidebar_tab_background(self) -> str:
        return self.palette.bg_surface

    @property
    def sidebar_tab_background_active(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def sidebar_tab_text_color(self) -> str:
        return self.palette.text_secondary

    @property
    def sidebar_tab_text_color_active(self) -> str:
        return self.palette.text_primary

    sidebar_tab_font_size: int = 18
    sidebar_tab_icon_size: int = 20

    @property
    def sidebar_tab_indicator_color(self) -> str:
        return self.palette.accent_blue

    sidebar_tab_indicator_width: int = 3

    @property
    def sidebar_section_title_color(self) -> str:
        return self.palette.text_dim

    sidebar_section_title_size: int = 18
    sidebar_row_height: int = 32

    @property
    def sidebar_checkbox_color(self) -> str:
        return self.palette.accent_blue

    @property
    def sidebar_slider_color(self) -> str:
        return self.palette.accent_blue

    @property
    def sidebar_combo_border_color(self) -> str:
        return self.palette.border_subtle

    @property
    def sidebar_combo_border_focus(self) -> str:
        return self.palette.accent_blue

    sidebar_icon_columns: int = 5
    sidebar_icon_size: int = 32
    sidebar_row_spacing: int = 6

    # ── Scrollbar ──────────────────────────────────────────────
    @property
    def scrollbar_handle_color(self) -> str:
        return self.palette.scrollbar_handle

    @property
    def scrollbar_handle_hover_color(self) -> str:
        return self.palette.scrollbar_handle_hover

    # ── Preview widget ─────────────────────────────────────────
    @property
    def preview_background(self) -> str:
        return self.palette.bg_preview

    # ── Profile dialog icon border ─────────────────────────────
    @property
    def icon_preview_border_color(self) -> str:
        return self.palette.border_icon_preview

    # ── Controls: disabled state ───────────────────────────────
    @property
    def control_disabled_text(self) -> str:
        return self.palette.text_disabled

    @property
    def control_disabled_bg(self) -> str:
        return self.palette.bg_surface

    @property
    def control_disabled_border(self) -> str:
        return self.palette.border_subtle

    # ── CheckBox ───────────────────────────────────────────────
    checkbox_indicator_size: int = 18
    checkbox_indicator_radius: int = 4
    checkbox_spacing: int = 8
    checkbox_padding_v: int = 4

    @property
    def checkbox_disabled_color(self) -> str:
        return self.palette.text_disabled

    # ── ComboBox ───────────────────────────────────────────────
    @property
    def combo_background(self) -> str:
        return self.palette.bg_input

    @property
    def combo_background_disabled(self) -> str:
        return self.palette.bg_input_disabled

    @property
    def combo_text_color(self) -> str:
        return self.palette.text_secondary

    @property
    def combo_text_color_disabled(self) -> str:
        return self.palette.text_disabled

    @property
    def combo_border_color(self) -> str:
        return self.palette.border_subtle

    @property
    def combo_border_color_disabled(self) -> str:
        return self.palette.border_subtle

    @property
    def combo_border_hover_color(self) -> str:
        return self.palette.border_hover

    @property
    def combo_border_focus_color(self) -> str:
        return self.palette.accent_blue

    combo_padding_h: int = 8
    combo_padding_v: int = 4
    combo_border_radius: int = 6
    combo_dropdown_width: int = 20

    @property
    def combo_popup_background(self) -> str:
        return self.palette.bg_input

    @property
    def combo_popup_selection_background(self) -> str:
        return self.palette.accent_blue

    @property
    def combo_popup_text_color(self) -> str:
        return self.palette.text_secondary

    # ── Slider ─────────────────────────────────────────────────
    @property
    def slider_groove_bg(self) -> str:
        return self.palette.slider_groove

    @property
    def slider_groove_bg_disabled(self) -> str:
        return self.palette.slider_groove_disabled

    @property
    def slider_handle_color(self) -> str:
        return self.palette.accent_blue

    @property
    def slider_handle_color_disabled(self) -> str:
        return self.palette.text_disabled

    @property
    def slider_handle_hover_color(self) -> str:
        return self.palette.accent_blue_light

    @property
    def slider_handle_hover_color_disabled(self) -> str:
        return self.palette.text_disabled

    @property
    def slider_sub_page_color_disabled(self) -> str:
        return self.palette.border_subtle

    slider_value_edit_width: int = 72

    # ── Editable text fields ───────────────────────────────────
    @property
    def edit_background(self) -> str:
        return self.palette.bg_input

    @property
    def edit_background_disabled(self) -> str:
        return self.palette.bg_input_disabled

    @property
    def edit_text_color(self) -> str:
        return self.palette.text_secondary

    @property
    def edit_text_color_disabled(self) -> str:
        return self.palette.text_disabled

    edit_border_radius: int = 6
    edit_padding_h: int = 8
    edit_padding_v: int = 4

    @property
    def edit_border_color(self) -> str:
        return self.palette.border_subtle

    @property
    def edit_border_focus_color(self) -> str:
        return self.palette.accent_blue

    @property
    def edit_border_hover_color(self) -> str:
        return self.palette.border_hover

    @property
    def edit_selection_background(self) -> str:
        return self.palette.accent_blue

    # ── Color swatch button ────────────────────────────────────
    color_swatch_width: int = 36
    color_swatch_height: int = 24

    @property
    def color_swatch_border(self) -> str:
        return self.palette.border_hover

    @property
    def color_swatch_disabled_bg(self) -> str:
        return self.palette.text_disabled

    path_browse_button_width: int = 32

    # ── Splitter handle ────────────────────────────────────────
    splitter_handle_width: int = 3

    @property
    def splitter_handle_color(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def splitter_handle_hover_color(self) -> str:
        return self.palette.bg_surface_hover

    # ── Visual hints (highlight indicators) ────────────────────
    highlight_border_width: int = 4

    @property
    def highlight_border_color(self) -> str:
        return self.palette.accent_blue

    @property
    def highlight_label_color(self) -> str:
        return self.palette.accent_blue

    @property
    def background_color(self) -> str:
        return self.palette.bg_deep

    @property
    def separator_line_color(self) -> str:
        return self.palette.separator_color

    @property
    def dialog_button_hover_border_color(self) -> str:
        return self.palette.border_hover

    @property
    def highlight_background_color(self) -> str:
        return self.palette.accent_blue_bg

    @property
    def dialog_button_pressed_background(self) -> str:
        return self.palette.bg_button_pressed

    highlight_background_enabled: bool = True
    highlight_indicator_gap: int = 8

    # ── Footer buttons ─────────────────────────────────────────
    footer_button_height: int = 42
    footer_button_padding_h: int = 18
    footer_button_padding_v: int = 6
    footer_button_radius: int = 8

    @property
    def footer_save_bg(self) -> str:
        return self.palette.bg_surface

    @property
    def footer_save_text(self) -> str:
        return self.palette.text_primary

    @property
    def footer_save_border(self) -> str:
        return self.palette.accent_blue

    @property
    def footer_save_hover_bg(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def footer_save_hover_border(self) -> str:
        return self.palette.accent_blue

    @property
    def footer_save_disabled_bg(self) -> str:
        return self.palette.bg_surface

    @property
    def footer_save_disabled_text(self) -> str:
        return self.palette.text_disabled

    @property
    def footer_save_disabled_border(self) -> str:
        return self.palette.border_subtle

    @property
    def footer_reset_bg(self) -> str:
        return self.palette.bg_surface

    @property
    def footer_reset_text(self) -> str:
        return self.palette.text_secondary

    @property
    def footer_reset_border(self) -> str:
        return self.palette.border_red

    @property
    def footer_reset_hover_bg(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def footer_reset_hover_border(self) -> str:
        return self.palette.border_red_hover

    @property
    def footer_reset_disabled_bg(self) -> str:
        return self.palette.bg_surface

    @property
    def footer_reset_disabled_text(self) -> str:
        return self.palette.text_disabled

    @property
    def footer_reset_disabled_border(self) -> str:
        return self.palette.border_subtle

    @property
    def footer_reset_split_border(self) -> str:
        return self.palette.border_red

    @property
    def footer_reset_dropdown_border_inactive(self) -> str:
        return self.palette.border_red_dim

    @property
    def footer_menu_bg(self) -> str:
        return self.palette.bg_input

    @property
    def footer_menu_border(self) -> str:
        return self.palette.border_subtle

    @property
    def footer_menu_text(self) -> str:
        return self.palette.text_secondary

    @property
    def footer_menu_selection_bg(self) -> str:
        return self.palette.accent_blue

    @property
    def footer_menu_selection_text(self) -> str:
        return self.palette.text_primary

    # ── Profile sidebar ────────────────────────────────────────
    @property
    def profile_title_font_size(self) -> int:
        return self.sidebar_section_title_size

    @property
    def profile_title_font_weight(self) -> str:
        return "bold"

    @property
    def profile_title_color(self) -> str:
        return self.palette.text_dim

    profile_title_left_padding: int = 2
    profile_item_height: int = 40
    profile_item_icon_size: int = 32

    @property
    def profile_item_text_color(self) -> str:
        return self.palette.text_secondary

    @property
    def profile_item_text_color_active(self) -> str:
        return self.palette.text_primary

    @property
    def profile_item_background(self) -> str:
        return "transparent"

    @property
    def profile_item_background_hover(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def profile_item_background_active(self) -> str:
        return self.palette.bg_surface_hover

    profile_item_border_radius: int = 6
    profile_item_spacing: int = 4
    profile_toolbar_button_size: int = 36
    profile_toolbar_button_icon_size: int = 24

    @property
    def profile_toolbar_button_background_hover(self) -> str:
        return self.palette.bg_surface_hover

    profile_toolbar_button_border_radius: int = 8
    profile_capture_icon_size: int = 128

    @property
    def profile_header_bottom_border(self) -> str:
        return self.palette.border_profile_sep

    @property
    def profile_toolbar_top_border(self) -> str:
        return self.palette.border_profile_sep

    @property
    def profile_item_indicator_color(self) -> str:
        return self.palette.accent_blue

    profile_item_indicator_width: int = 3

    # ── Icon tab bar (right sidebar) ───────────────────────────
    @property
    def icon_tab_bar_background(self) -> str:
        return self.palette.bg_icon_tab_bar

    # ── Dialog style constants ─────────────────────────────────
    @property
    def dialog_background(self) -> str:
        return self.palette.bg_surface

    @property
    def dialog_text_color(self) -> str:
        return self.palette.text_secondary

    @property
    def dialog_label_color(self) -> str:
        return self.palette.text_secondary

    @property
    def dialog_label_font_size(self) -> int:
        return self.palette.font_size_base

    @property
    def dialog_input_background(self) -> str:
        return self.palette.bg_input

    @property
    def dialog_input_border(self) -> str:
        return self.palette.border_subtle

    @property
    def dialog_input_focus_border(self) -> str:
        return self.palette.accent_blue

    dialog_input_border_radius: int = 4
    dialog_input_padding: str = "4px 8px"
    dialog_combo_min_width: int = 120

    @property
    def dialog_button_background(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def dialog_button_hover_background(self) -> str:
        return self.palette.bg_input

    @property
    def dialog_button_pressed_background(self) -> str:
        return self.palette.bg_button_pressed

    @property
    def dialog_button_border(self) -> str:
        return self.palette.border_subtle

    @property
    def dialog_button_border_radius(self) -> int:
        return self.palette.radius_sm

    dialog_button_padding: str = "4px 12px"

    @property
    def dialog_button_disabled_color(self) -> str:
        return self.palette.text_disabled

    @property
    def dialog_groupbox_title_color(self) -> str:
        return self.palette.text_dim

    @property
    def dialog_groupbox_border(self) -> str:
        return self.palette.border_profile_sep

    dialog_groupbox_border_radius: int = 6

    @property
    def dialog_list_background(self) -> str:
        return self.palette.bg_surface

    @property
    def dialog_list_border(self) -> str:
        return self.palette.border_profile_sep

    dialog_list_border_radius: int = 6
    dialog_list_item_padding: str = "4px 8px"
    dialog_list_item_border_radius: int = 4

    @property
    def dialog_list_item_hover_background(self) -> str:
        return self.palette.bg_surface_hover

    @property
    def dialog_list_item_selected_background(self) -> str:
        return self.palette.bg_input

    dialog_match_label_font_size: int = 18
    dialog_icon_button_size: int = 32
    dialog_icon_button_icon_size: int = 24
