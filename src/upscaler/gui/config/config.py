from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class GuiPalette:
    """Semantic colors, fonts, and shared spacing tokens for the entire GUI.

    Every color used by a style sheet **must** be a palette field.
    This allows themes to be swapped by simply providing a different
    :class:`GuiPalette` instance, with no other configuration changes.
    """

    # ── Backgrounds ──────────────────────────────────────────────
    bg_deep: str = "#121212"  # main background behind the window grid
    bg_panel: str = "#161616"  # sidebars, footer area
    bg_surface: str = "#1e1e1e"  # tiles, tab backgrounds, disabled elements
    bg_surface_hover: str = "#2c2c2c"  # hovered tiles, active tab, list items
    bg_input: str = "#2a2a2c"  # combo boxes, line edits
    bg_input_disabled: str = "#1e1e1e"
    bg_filter: str = "#2a2a2a"  # filter bar normal background
    bg_filter_hover: str = "#353535"  # filter bar hover background
    bg_preview: str = "#2d2d2d"  # icon previews, etc.
    bg_icon_tab_bar: str = "#1a1a1a"  # the icon‑only tab bar on the right
    bg_button_pressed: str = "#222"  # dialog buttons when pressed

    # ── Borders & separators ─────────────────────────────────────
    border_subtle: str = "#444"  # subtle borders (tabs, panels)
    border_focus: str = "#4a9eff"  # focus ring on inputs
    border_hover: str = "#555555"  # hover border on controls
    border_red: str = "#914343"  # red border (reset button, errors)
    border_red_hover: str = "#b55a5a"
    border_red_dim: str = "#6b2e2e"
    border_profile_sep: str = "#333"  # separators in the profile sidebar
    border_icon_preview: str = "#444"  # border around icon previews

    # ── Tile overlay (gradient stops) ────────────────────────────
    tile_overlay_start: str = "#00000000"
    tile_overlay_mid: str = "#88000000"
    tile_overlay_end: str = "#dd000000"
    tile_title_bg: str = "#99000000"  # background behind the tile title
    tile_title_text: str = "#ffffff"  # color of the tile title text

    # ── Text ─────────────────────────────────────────────────────
    text_primary: str = "#ffffff"  # main text on dark backgrounds
    text_secondary: str = "#cccccc"  # secondary labels
    text_dim: str = "#888888"  # dimmed hints, placeholder
    text_disabled: str = "#555"  # disabled control text
    text_placeholder: str = "#666"  # placeholder in filter bar
    text_filter: str = "#eee"  # text inside the filter bar

    # ── Accent colors ───────────────────────────────────────────
    accent_blue: str = "#4a9eff"  # primary accent: focus, selections, sliders
    accent_blue_light: str = "#6aade5"  # lighter version for hover states
    accent_blue_bg: str = "#1a2b3c"  # highlighted row background
    accent_cyan: str = "#2b5b84"  # tile hover border, filter focus
    accent_icon: str = "#7A9EB1"  # color of monochrome SVG icons

    # ── Slider, scrollbar, etc. ──────────────────────────────────
    slider_groove: str = "#333"
    slider_groove_disabled: str = "#222"
    scrollbar_handle: str = "#3a3a3c"
    scrollbar_handle_hover: str = "#4a4a4c"
    separator_color: str = "#333"  # horizontal rule color
    splitter_handle: str = "#2c2c2c"
    splitter_handle_hover: str = "#2c2c2c"


@dataclass(frozen=True)
class TileLayout:
    """Geometry, animation, shadow, and title style for window tiles."""

    width: int = 340  # tile width in pixels
    height: int = 260  # tile height in pixels
    radius: int = 12  # corner radius
    aspect_ratio: float = 4 / 3  # used for placeholder calculations
    spacing: int = 12  # space between tiles
    spacing_ratio: float = 0.075  # spacing as fraction of tile width (alternative)
    margin: int = 20  # grid margin from window edges
    columns: int = 3  # number of columns in the grid
    min_columns: int = 1  # minimum columns when window is narrow
    scroll_margin: int = 20  # margin that triggers scroll during drag
    pop_scale: float = 1.05  # scale factor on hover
    pop_duration: int = 200  # animation duration in ms

    # ── Selection & hover borders ────────────────────────────
    selection_border_width: int = 3
    hover_border_width: int = 2

    # ── Drop shadow ─────────────────────────────────────────
    shadow_blur_radius: int = 20
    shadow_offset: Tuple[int, int] = (0, 4)
    shadow_hover_blur_radius: int = 30

    # ── Title label ─────────────────────────────────────────
    title_font_size: int = 12  # Font size used by default
    title_font_bold: bool = True  # whether the title is bold


@dataclass(frozen=True)
class FilterLayout:
    """Sizes and spacing of the filter bar."""

    height: int = 80
    font_size: int = 16  # filter input font size
    padding_h: int = 16  # horizontal padding inside the filter field
    padding_v: int = 16  # vertical padding
    border_radius: int = 12
    icon_size: int = 24  # search / filter icon size
    icon_gap: int = -8  # space between icon and text (negative = overlap)
    horizontal_margin: int = 18  # margin left/right of the filter bar
    vertical_margin: int = 6  # margin above/below the filter bar@dataclass(frozen=True)


@dataclass(frozen=True)
class SidebarLayout:
    """Common dimensions for left and right sidebars."""

    width: int = 400  # default sidebar width
    tab_font_size: int = 18  # font size for tab labels and row labels
    tab_icon_size: int = 20  # icon size inside tabs
    tab_indicator_width: int = 3  # thickness of the active tab indicator
    section_title_size: int = 18  # font size of section headings ("Overlay", ...)
    row_height: int = 32  # minimum height of a settings row
    icon_columns: int = 7  # columns in the icon picker grid
    icon_size: int = 28  # icon size inside the icon picker
    row_spacing: int = 6  # spacing between consecutive rows


@dataclass(frozen=True)
class CheckBoxLayout:
    """Dimensions for checkboxes in settings rows."""

    indicator_size: int = 18
    indicator_radius: int = 4
    spacing: int = 8  # space between checkbox box and its label
    padding_v: int = 4  # vertical padding around the checkbox row


@dataclass(frozen=True)
class ComboBoxLayout:
    """Dimensions for combo boxes."""

    padding_h: int = 8
    padding_v: int = 4
    border_radius: int = 6
    dropdown_width: int = 20  # width of the drop‑down arrow area (hidden via CSS)


@dataclass(frozen=True)
class SliderLayout:
    """Dimensions for sliders."""

    value_edit_width: int = 72  # width of the spinbox next to the slider


@dataclass(frozen=True)
class EditFieldLayout:
    """Dimensions for editable text fields."""

    border_radius: int = 6
    padding_h: int = 8
    padding_v: int = 4


@dataclass(frozen=True)
class ColorSwatchLayout:
    """Dimensions for the color swatch button."""

    swatch_width: int = 36
    swatch_height: int = 24
    browse_button_width: int = 32  # width of the "browse" button next to a path field


@dataclass(frozen=True)
class SplitterLayout:
    """Splitter handle width (colors live in the palette)."""

    handle_width: int = 3


@dataclass(frozen=True)
class FooterLayout:
    """Dimensions of the Save / Reset buttons at the bottom of the settings sidebar."""

    button_height: int = 42
    button_padding_h: int = 18
    button_padding_v: int = 6
    button_radius: int = 8


@dataclass(frozen=True)
class ProfileLayout:
    """Appearance of the profile list in the left sidebar."""

    title_font_size: int = 18
    title_font_weight: str = "bold"
    title_left_padding: int = 2
    item_height: int = 40
    item_icon_size: int = 32
    item_border_radius: int = 6
    item_spacing: int = 4
    toolbar_button_size: int = 36
    toolbar_button_icon_size: int = 24
    toolbar_button_border_radius: int = 8
    capture_icon_size: int = 128
    indicator_width: int = 3


@dataclass(frozen=True)
class DialogLayout:
    """Sizes and padding strings for dialogs."""

    combo_min_width: int = 120
    label_font_size: int = 18
    match_label_font_size: int = 18
    info_font_size: int = 16
    icon_button_size: int = 32
    icon_button_icon_size: int = 24
    button_border_radius: int = 8
    input_padding: str = "4px 8px"
    button_padding: str = "4px 12px"
    list_item_padding: str = "4px 8px"
    list_item_border_radius: int = 4
    input_border_radius: int = 4  # for QLineEdit / QComboBox in dialogs
    groupbox_border_radius: int = 6  # for QGroupBox
    list_border_radius: int = 6  # for QListWidget


# ---------------------------------------------------------------------------
#  GUIConfig – the top-level configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GUIConfig:
    """Central GUI configuration.

    All layout constants are grouped into frozen sub‑configurations.
    colors, fonts, and shared spacing live exclusively in :attr:`palette`.

    Attributes:
        palette: The active theme (semantic color tokens).
        tile: Tile geometry, shadows, title style.
        filter: Filter bar dimensions.
        sidebar: Sidebar common layout.
        checkbox: Checkbox indicator dimensions.
        combo: Combo box padding and radius.
        slider: Slider‑related numbers.
        edit_field: Text field dimensions.
        swatch: Color swatch button sizes.
        splitter: Splitter handle width.
        footer: Footer button sizes.
        profile: Profile sidebar item sizes.
        dialog: Dialog dimensions and padding strings.
        auto_refresh_ms: Window list refresh interval (ms).
        tile_preview_interval_ms: Tile thumbnail update interval (ms).
        highlight_background_enabled: Whether highlighted rows get a background color.
    """

    palette: GuiPalette = field(default_factory=lambda: GuiPalette())

    tile: TileLayout = field(default_factory=TileLayout)
    filter: FilterLayout = field(default_factory=FilterLayout)
    sidebar: SidebarLayout = field(default_factory=SidebarLayout)
    checkbox: CheckBoxLayout = field(default_factory=CheckBoxLayout)
    combo: ComboBoxLayout = field(default_factory=ComboBoxLayout)
    slider: SliderLayout = field(default_factory=SliderLayout)
    edit_field: EditFieldLayout = field(default_factory=EditFieldLayout)
    swatch: ColorSwatchLayout = field(default_factory=ColorSwatchLayout)
    splitter: SplitterLayout = field(default_factory=SplitterLayout)
    footer: FooterLayout = field(default_factory=FooterLayout)
    profile: ProfileLayout = field(default_factory=ProfileLayout)
    dialog: DialogLayout = field(default_factory=DialogLayout)

    font_family: str = "Segoe UI"  # default UI font

    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60

    highlight_border_width: int = 4
    highlight_indicator_gap: int = 8
    highlight_background_enabled: bool = True
