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

    # ---- Pop‑out animation -------------------------------------------
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

    # ---- Empty‑grid placeholder --------------------------------------
    empty_text: str = "No windows found"
    empty_text_color: str = "#666"
    empty_text_size: int = 18

    # ---- Timing ------------------------------------------------------
    auto_refresh_ms: int = 3000
    tile_preview_interval_ms: int = 40  # how often live preview updates

    # ---- Scaling / layout helpers ------------------------------------
    min_columns: int = 1
    scroll_margin: int = 20  # extra space for scroll‑into‑view

    # ---- Right and Left Sidebars -------------------------------------
    sidebar_width: int = 360
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
