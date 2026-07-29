from dataclasses import dataclass, field


@dataclass
class GUIPalette:
    """Semantic color tokens for the entire GUI."""

    # Background
    background: str

    # Text
    text: str
    text_hover: str
    text_subtle: str
    text_pillbox: str

    # Icons
    icon: str

    # Borders
    border: str
    border_hover: str

    # Input
    input: str
    input_hover: str
    input_disabled: str

    # Controls
    control: str
    control_hover: str
    control_subtle: str
    control_subtle_hover: str

    # Buttons
    button: str
    button_hover: str
    button_revert: str
    button_revert_hover: str


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
        pop_scale: Scale factor applied on hover/selection (1.0 = no scale).
        pop_duration: Duration of the pop animation in milliseconds.
        selection_border_width: Border width (px) when the tile is selected.
        hover_border_width: Border width (px) when the tile is hovered.
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
    pop_scale: float = 1.05
    pop_duration: int = 200
    selection_border_width: int = 3
    hover_border_width: int = 2
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
        section_title_size: Font size of section headings (e.g. "Overlay").
        row_height: Minimum height of a settings row.
        icon_columns: Number of columns in the icon picker grid.
        icon_size: Icon size inside the icon picker.
        row_spacing: Spacing between consecutive settings rows.
    """

    width: int = 400
    tab_font_size: int = 18
    section_title_size: int = 18
    row_height: int = 32
    icon_columns: int = 8
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
    """

    padding_h: int = 8
    padding_v: int = 4
    border_radius: int = 6


@dataclass(frozen=True)
class SliderLayout:
    """Slider-related numbers.

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
        profile_height: Height of each profile item in the list.
        profile_icon_size: Icon size for profile icons.
        profile_border_left: Left border width of the active profile item.
        profile_border_radius: Corner radius of profile items.
        profile_spacing: Vertical spacing between profile items.
        toolbar_button_size: Fixed size of the toolbar buttons (Add, Edit, etc.).
        toolbar_button_icon_size: Icon size inside the toolbar buttons.
        toolbar_button_border_radius: Corner radius of the toolbar buttons.
        saved_icon_size: Size used when capturing an icon from a window.
    """

    title_font_size: int = 18
    profile_height: int = 40
    profile_icon_size: int = 32
    profile_border_left: int = 3
    profile_border_radius: int = 6
    profile_spacing: int = 4
    toolbar_button_size: int = 36
    toolbar_button_icon_size: int = 24
    toolbar_button_border_radius: int = 8
    saved_icon_size: int = 128


@dataclass(frozen=True)
class DialogLayout:
    """Sizes and padding strings for dialogs.

    Attributes:
        combo_min_width: Minimum width of combo boxes inside dialogs.
        label_font_size: Default font size for dialog labels.
        input_font_size: Font size for match-criteria labels.
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
    input_font_size: int = 18
    info_font_size: int = 16
    icon_button_size: int = 32
    icon_button_icon_size: int = 24
    button_border_radius: int = 8
    input_padding: str = "4px 8px"
    button_padding: str = "4px 8px"
    list_item_padding: str = "4px 8px"
    list_item_border_radius: int = 4
    input_border_radius: int = 4
    groupbox_border_radius: int = 6
    list_border_radius: int = 6


# ---------------------------------------------------------------------------
#  GUIConfig, the top-level configuration
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GUIConfig:
    """Central GUI configuration.

    All layout constants are grouped into frozen sub-configurations.
    Colors, fonts, and shared spacing live exclusively in :attr:`palette`.

    Attributes:
        palette: The active theme (semantic color and font tokens).
        tile: Tile geometry, shadows, title style.
        filter: Filter bar dimensions.
        sidebar: Sidebar common layout.
        checkbox: Checkbox indicator dimensions.
        combo: Combo box padding and radius.
        slider: Slider-related numbers.
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
    """

    palette: GUIPalette

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
