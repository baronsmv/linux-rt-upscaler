from __future__ import annotations

from .config import GuiPalette

# ── Dark (current default) ──────────────────────────────────────────
DARK = GuiPalette()

# ── Light ───────────────────────────────────────────────────────────
LIGHT = GuiPalette(
    bg_deep="#f5f5f5",
    bg_panel="#fafafa",
    bg_surface="#ffffff",
    bg_surface_hover="#e8e8e8",
    bg_input="#f0f0f0",
    bg_input_disabled="#e0e0e0",
    bg_filter="#f0f0f0",
    bg_filter_hover="#e4e4e4",
    border_subtle="#cccccc",
    border_focus="#0066cc",
    border_hover="#999999",
    border_red="#cc3333",
    border_red_hover="#dd5555",
    border_red_dim="#aa6666",
    border_profile_sep="#dddddd",
    border_icon_preview="#aaaaaa",
    text_primary="#111111",
    text_secondary="#333333",
    text_dim="#888888",
    text_disabled="#aaaaaa",
    text_placeholder="#999999",
    text_filter="#222222",
    accent_blue="#0066cc",
    accent_blue_light="#3388dd",
    accent_blue_bg="#d6e8fa",
    accent_cyan="#0077aa",
    accent_icon="#555555",
    slider_groove="#cccccc",
    slider_groove_disabled="#eeeeee",
    bg_button_pressed="#c0c0c0",
    bg_icon_tab_bar="#e8e8e8",
    bg_preview="#e8e8e8",
    separator_color="#cccccc",
    shadow_color=(0, 0, 0, 40),
)

# ── Cyberpunk (neon contrast) ──────────────────────────────────────
CYBERPUNK = GuiPalette(
    bg_deep="#0a0a0f",
    bg_panel="#111118",
    bg_surface="#1a1a24",
    bg_surface_hover="#2a2a3c",
    bg_input="#1a1a24",
    bg_input_disabled="#0e0e14",
    bg_filter="#1a1a24",
    bg_filter_hover="#252535",
    border_subtle="#3a3a5c",
    border_focus="#ff00ff",
    border_hover="#aa55ff",
    border_red="#ff3366",
    border_red_hover="#ff6688",
    border_red_dim="#993355",
    border_profile_sep="#2a2a3c",
    text_primary="#e0e0ff",
    text_secondary="#9a9acc",
    text_dim="#6a6a88",
    text_disabled="#4a4a66",
    text_placeholder="#5a5a7a",
    text_filter="#d0d0ff",
    accent_blue="#ff00ff",
    accent_blue_light="#ff55ff",
    accent_blue_bg="#2a1a3c",
    accent_cyan="#00ccff",
    accent_icon="#aa88ff",
    slider_groove="#3a3a5c",
    slider_groove_disabled="#1a1a2c",
    bg_button_pressed="#2a1030",
    bg_preview="#1a1a24",
    border_icon_preview="#3a3a5c",
    bg_icon_tab_bar="#111118",
    shadow_color=(0, 0, 0, 180),
)

# ── Registry ────────────────────────────────────────────────────────
PRESETS = {
    "Dark": DARK,
    "Light": LIGHT,
    "Cyberpunk": CYBERPUNK,
}
