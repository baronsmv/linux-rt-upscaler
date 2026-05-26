from dataclasses import dataclass
from typing import Tuple


@dataclass
class GuiPalette:
    """All reusable color, font, and spacing tokens."""

    # ── Core background / surface ─────────────────────────────────
    bg_deep: str = "#121212"  # main background behind the grid
    bg_panel: str = "#161616"  # sidebars
    bg_surface: str = "#1e1e1e"  # tiles, tab background, disabled elements
    bg_surface_hover: str = "#2c2c2c"  # hovered tiles, active tab, etc.
    bg_input: str = "#2a2a2c"  # combo boxes, line edits
    bg_input_disabled: str = "#1e1e1e"
    bg_filter: str = "#2a2a2a"
    bg_filter_hover: str = "#353535"
    bg_preview: str = "#2d2d2d"
    bg_icon_tab_bar: str = "#1a1a1a"
    bg_button_pressed: str = "#222"

    # ── Borders & separators ──────────────────────────────────────
    border_subtle: str = "#444"
    border_focus: str = "#4a9eff"
    border_hover: str = "#555555"
    border_red: str = "#914343"
    border_red_hover: str = "#b55a5a"
    border_red_dim: str = "#6b2e2e"
    border_profile_sep: str = "#333"
    border_icon_preview: str = "#444"

    # ── Tile overlay ──────────────────────────────────────────────
    tile_overlay_start: str = "#00000000"
    tile_overlay_mid: str = "#88000000"
    tile_overlay_end: str = "#dd000000"
    tile_title_bg: str = "#99000000"
    tile_title_text: str = "#ffffff"

    # ── Text ──────────────────────────────────────────────────────
    text_primary: str = "#ffffff"
    text_secondary: str = "#cccccc"
    text_dim: str = "#888888"
    text_disabled: str = "#555"
    text_placeholder: str = "#666"
    text_filter: str = "#eee"

    # ── Accent colors ─────────────────────────────────────────────
    accent_blue: str = "#4a9eff"
    accent_blue_light: str = "#6aade5"
    accent_blue_bg: str = "#1a2b3c"
    accent_cyan: str = "#2b5b84"  # tile hover border
    accent_icon: str = "#7A9EB1"  # SVG icon stroke

    # ── Slider, scrollbar, checkbox, color-swatch ─────────────────
    slider_groove: str = "#333"
    slider_groove_disabled: str = "#222"
    scrollbar_handle: str = "#3a3a3c"
    scrollbar_handle_hover: str = "#4a4a4c"
    separator_color: str = "#333"

    # ── Fonts ─────────────────────────────────────────────────────
    font_family: str = "Segoe UI"
    font_size_sm: int = 12  # tile titles
    font_size_mid: int = 16  # visual hints
    font_size_base: int = 18  # dialogs
    font_size_lg: int = 24  # filter bar, maybe future

    # ── Spacing & radii ───────────────────────────────────────────
    radius_sm: int = 4
    radius_md: int = 6
    radius_lg: int = 8
    radius_xl: int = 12
    spacing_sm: int = 4
    spacing_md: int = 8
    spacing_lg: int = 12

    # ── Shadows (unused but kept) ─────────────────────────────────
    shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 120)
