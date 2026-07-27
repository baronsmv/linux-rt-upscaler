from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class GuiPalette:
    """Semantic colour tokens for the entire GUI.

    Every colour used by a style sheet must be a palette field.
    Themes are swapped by replacing this instance – no other config changes.
    All names describe the *role* of the colour, never its hue.
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
    border_focus: str = "#4a9eff"  # focus ring on inputs (may coincide with accent)
    border_hover: str = "#555555"  # hover border on controls
    border_danger: str = "#914343"  # red border (reset button, destructive actions)
    border_danger_hover: str = "#b55a5a"
    border_danger_dim: str = "#6b2e2e"
    border_profile_separator: str = "#333"  # separators in the profile sidebar
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
    text_dim: str = "#888888"  # dimmed hints, section titles
    text_disabled: str = "#555"  # disabled control text
    text_placeholder: str = "#666"  # placeholder in filter bar
    text_filter: str = "#eee"  # text inside the filter bar

    # ── Accent / interactive colors ─────────────────────────────
    accent_primary: str = "#4a9eff"  # primary action color (focus, selection, sliders)
    accent_primary_light: str = "#6aade5"  # lighter variant for hover states
    accent_primary_bg: str = "#1a2b3c"  # background for highlighted rows
    accent_secondary: str = (
        "#2b5b84"  # secondary accent (tile hover border, filter focus)
    )
    accent_icon: str = "#7A9EB1"  # colour of monochrome SVG icons

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
    """Geometry, animation, shadow, and title style for window tiles.

    Attributes:
        width: Default tile width in pixels.
        height: Default tile height in pixels.
        radius: Corner radius of the tile rectangle.
        aspect_ratio: Width/height ratio used to compute height from width.
        spacing: Minimum pixel space between tiles.
        spacing_ratio: Spacing as a fraction of tile width (overrides fixed spacing if > 0).
        margin: Distance from the window edges to the grid.
        columns: Desired number of tile columns (may be reduced when there are fewer tiles).
        min_columns: Minimum number of columns when the window is narrow.
        scroll_margin: Extra margin that triggers automatic scrolling during drag.
        pop_scale: Scale factor applied on hover/selection (1.0 = no scale).
        pop_duration: Duration of the pop animation in milliseconds.
        selection_border_width: Border width (px) when the tile is selected.
        hover_border_width: Border width (px) when the tile is hovered.
        shadow_blur_radius: Blur radius of the default shadow.
        shadow_offset: (x, y) offset of the default shadow.
        shadow_hover_blur_radius: Blur radius of the shadow when hovered.
        title_font_family: Font family used for the title.
        title_font_size: Font size for the tile title.
        title_font_bold: Whether the title is rendered in bold.
    """

    width: int = 340
    height: int = 260
    radius: int = 12
    aspect_ratio: float = 4 / 3
    spacing: int = 12
    spacing_ratio: float = 0.075
    margin: int = 20
    columns: int = 3
    min_columns: int = 1
    scroll_margin: int = 20
    pop_scale: float = 1.05
    pop_duration: int = 200
    selection_border_width: int = 3
    hover_border_width: int = 2
    shadow_blur_radius: int = 20
    shadow_offset: Tuple[int, int] = (0, 4)
    shadow_hover_blur_radius: int = 30
    title_font_family: str = "Segoe UI"
    title_font_size: int = 12
    title_font_bold: bool = True


@dataclass(frozen=True)
class FilterLayout:
    """Sizes and spacing of the filter bar.

    Attributes:
        height: Total height of the filter bar widget.
        font_size: Font size of the input text.
        padding_h: Horizontal padding inside the filter field.
        padding_v: Vertical padding inside the filter field.
        border_radius: Corner radius of the filter field.
        icon_size: Width and height of the search and clear icons.
        icon_gap: Gap between the icon and the text (negative values allow overlap).
        horizontal_margin: Outer left/right margin of the filter bar.
        vertical_margin: Outer top/bottom margin of the filter bar.
    """

    height: int = 80
    font_size: int = 16
    padding_h: int = 16
    padding_v: int = 16
    border_radius: int = 12
    icon_size: int = 24
    icon_gap: int = -8
    horizontal_margin: int = 18
    vertical_margin: int = 6


@dataclass(frozen=True)
class SidebarLayout:
    """Common dimensions for left and right sidebars.

    Attributes:
        width: Default sidebar width in pixels.
        tab_font_size: Font size for tab labels and row labels.
        tab_icon_size: Icon size inside tabs.
        tab_indicator_width: Thickness of the active tab indicator bar.
        section_title_size: Font size of section headings (e.g. "Overlay").
        row_height: Minimum height of a settings row.
        icon_columns: Number of columns in the icon picker grid.
        icon_size: Icon size inside the icon picker.
        row_spacing: Spacing between consecutive settings rows.
    """

    width: int = 400
    tab_font_size: int = 18
    tab_icon_size: int = 20
    tab_indicator_width: int = 3
    section_title_size: int = 18
    row_height: int = 32
    icon_columns: int = 7
    icon_size: int = 28
    row_spacing: int = 6


@dataclass(frozen=True)
class CheckBoxLayout:
    """Dimensions for checkboxes in settings rows.

    Attributes:
        indicator_size: Width and height of the check indicator box.
        indicator_radius: Corner radius of the indicator.
        spacing: Space between the indicator and the label text.
        padding_v: Vertical padding around the checkbox row.
    """

    indicator_size: int = 18
    indicator_radius: int = 4
    spacing: int = 8
    padding_v: int = 4


@dataclass(frozen=True)
class ComboBoxLayout:
    """Dimensions for combo boxes.

    Attributes:
        padding_h: Horizontal padding inside the combo box.
        padding_v: Vertical padding inside the combo box.
        border_radius: Corner radius of the combo box.
        dropdown_width: Width of the drop‑down arrow area (hidden via CSS).
    """

    padding_h: int = 8
    padding_v: int = 4
    border_radius: int = 6
    dropdown_width: int = 20


@dataclass(frozen=True)
class SliderLayout:
    """Slider‑related numbers.

    Attributes:
        value_edit_width: Width of the editable value field next to the slider.
    """

    value_edit_width: int = 72


@dataclass(frozen=True)
class EditFieldLayout:
    """Dimensions for editable text fields.

    Attributes:
        border_radius: Corner radius of the line edit.
        padding_h: Horizontal padding inside the line edit.
        padding_v: Vertical padding inside the line edit.
    """

    border_radius: int = 6
    padding_h: int = 8
    padding_v: int = 4


@dataclass(frozen=True)
class ColorSwatchLayout:
    """Dimensions for the color swatch button.

    Attributes:
        swatch_width: Width of the color preview swatch.
        swatch_height: Height of the color preview swatch.
        browse_button_width: Width of the "Browse" button next to a path field.
    """

    swatch_width: int = 36
    swatch_height: int = 24
    browse_button_width: int = 32


@dataclass(frozen=True)
class SplitterLayout:
    """Splitter handle width (colors live in the palette).

    Attributes:
        handle_width: Width of the splitter handle in pixels.
    """

    handle_width: int = 3


@dataclass(frozen=True)
class FooterLayout:
    """Dimensions of the Save / Reset buttons at the bottom of the settings sidebar.

    Attributes:
        button_height: Fixed height of the buttons.
        button_padding_h: Horizontal padding inside the buttons.
        button_padding_v: Vertical padding inside the buttons.
        button_radius: Corner radius of the buttons.
    """

    button_height: int = 42
    button_padding_h: int = 18
    button_padding_v: int = 6
    button_radius: int = 8


@dataclass(frozen=True)
class ProfileLayout:
    """Appearance of the profile list in the left sidebar.

    Attributes:
        title_font_size: Font size for the "PROFILES" section title.
        title_font_weight: Font weight of the section title (e.g. "bold").
        title_left_padding: Left padding for the title label.
        item_height: Height of each profile item in the list.
        item_icon_size: Icon size for profile icons.
        item_border_radius: Corner radius of profile items.
        item_spacing: Vertical spacing between profile items.
        toolbar_button_size: Fixed size of the toolbar buttons (Add, Edit, etc.).
        toolbar_button_icon_size: Icon size inside the toolbar buttons.
        toolbar_button_border_radius: Corner radius of the toolbar buttons.
        capture_icon_size: Size used when capturing an icon from a window.
        indicator_width: Left border width of the active profile item.
    """

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
    """Sizes and padding strings for dialogs.

    Attributes:
        combo_min_width: Minimum width of combo boxes inside dialogs.
        label_font_size: Default font size for dialog labels.
        match_label_font_size: Font size for match‑criteria labels.
        info_font_size: Font size for informational text.
        icon_button_size: Fixed size of icon buttons in the dialog.
        icon_button_icon_size: Icon size inside those buttons.
        button_border_radius: Corner radius for dialog buttons.
        input_padding: CSS padding string for line edits and combo boxes.
        button_padding: CSS padding string for push buttons.
        list_item_padding: CSS padding string for list widget items.
        list_item_border_radius: Corner radius of list widget items.
        input_border_radius: Corner radius of line edits/combo boxes in dialogs.
        groupbox_border_radius: Corner radius of QGroupBox.
        list_border_radius: Corner radius of QListWidget.
    """

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
    input_border_radius: int = 4
    groupbox_border_radius: int = 6
    list_border_radius: int = 6


# ---------------------------------------------------------------------------
#  GUIConfig – the top-level configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GUIConfig:
    """Central GUI configuration.

    All layout constants are grouped into frozen sub‑configurations.
    Colors, fonts, and shared spacing live exclusively in :attr:`palette`.

    Attributes:
        palette: The active theme (semantic color and font tokens).
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
        highlight_border_width: Width of the highlight indicator bar in settings rows.
        highlight_indicator_gap: Gap between the indicator bar and the row content.
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

    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60

    highlight_border_width: int = 4
    highlight_indicator_gap: int = 8
    highlight_background_enabled: bool = True
