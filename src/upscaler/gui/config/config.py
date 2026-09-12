from dataclasses import dataclass, field

from .palette import GUIPalette


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
        button_size: Diameter of the circular tray / about buttons.
        button_icon_size: Icon size rendered inside those buttons.
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
    button_size: int = 36
    button_icon_size: int = 24


@dataclass(frozen=True)
class SidebarLayout:
    """Common dimensions for the left and right sidebars.

    Attributes:
        settings_width: Width of the settings sidebar (right).
        profiles_width: Width of the profiles sidebar (left).
        padding: Outer padding around the sidebar contents.
        content_margin_h: Horizontal margin inside a scrollable settings tab.
        content_margin_v: Vertical margin inside a scrollable settings tab.
        content_spacing: Vertical gap between sections inside a tab.
        tab_font_size: Font size for tab labels and row labels.
        section_title_size: Font size of section headings (e.g. "Overlay").
        section_title_padding_top: Padding above a section heading.
        section_title_padding_bottom: Padding below a section heading.
        section_title_letter_spacing: Extra tracking applied to section titles.
        row_height: Minimum height of a settings row.
        row_border_radius: Corner radius of a highlighted row's background.
        icon_columns: Number of columns in the icon tab bar.
        icon_size: Icon size inside the icon tab bar.
        row_spacing: Spacing between consecutive settings rows.
        tab_button_border_width: Border thickness of a tab button.
        tab_button_radius: Corner radius of a tab button.
        tab_button_padding: Padding inside each tab button, per side.
        tab_bar_padding_h: Horizontal padding of the icon tab bar container.
        tab_bar_padding_v: Vertical padding of the icon tab bar container.
        tab_bar_spacing: Gap between tab buttons in the grid.
    """

    settings_width: int = 420
    profiles_width: int = 380
    padding: int = 8
    content_margin_h: int = 16
    content_margin_v: int = 8
    content_spacing: int = 16
    tab_font_size: int = 18
    section_title_size: int = 18
    section_title_padding_top: int = 12
    section_title_padding_bottom: int = 4
    section_title_letter_spacing: int = 1
    row_height: int = 32
    row_border_radius: int = 4
    icon_columns: int = 9
    icon_size: int = 28
    row_spacing: int = 6
    tab_button_border_width: int = 2
    tab_button_radius: int = 8
    tab_button_padding: int = 6
    tab_bar_padding_h: int = 4
    tab_bar_padding_v: int = 8
    tab_bar_spacing: int = 6


@dataclass(frozen=True)
class CheckBoxLayout:
    """Dimensions for checkboxes in settings rows.

    Attributes:
        indicator_size: Width and height of the check indicator box.
        indicator_radius: Corner radius of the indicator.
        indicator_border_width: Border thickness of the indicator.
        spacing: Space between the indicator and the label text.
        padding_v: Vertical padding around the checkbox row.
    """

    indicator_size: int = 18
    indicator_radius: int = 4
    indicator_border_width: int = 2
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
    """Slider dimensions.

    Attributes:
        value_edit_width: Width of the editable value field next to the slider.
        groove_height: Thickness of the slider track.
        handle_size: Width and height of the handle (circle).
    """

    value_edit_width: int = 72
    groove_height: int = 4
    handle_size: int = 16


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
        radius: Corner radius of the color swatch.
    """

    swatch_width: int = 36
    swatch_height: int = 24
    browse_button_width: int = 32
    radius: int = 4


@dataclass(frozen=True)
class SplitterLayout:
    """Splitter handle width (colors live in the palette).

    Attributes:
        handle_width: Width of the splitter handle in pixels.
    """

    handle_width: int = 3


@dataclass(frozen=True)
class ScrollbarLayout:
    """Dimensions of scrollbars across the GUI.

    Attributes:
        width: Thickness of the scrollbar track (vertical or horizontal).
        radius: Corner radius of the handle.
        handle_min_length: Minimum handle length along the scroll axis.
    """

    width: int = 8
    radius: int = 4
    handle_min_length: int = 30


@dataclass(frozen=True)
class FooterLayout:
    """Dimensions of the Save / Reset buttons at the bottom of the settings sidebar.

    Attributes:
        button_height: Fixed height of the buttons.
        button_padding_h: Horizontal padding inside the buttons.
        button_padding_v: Vertical padding inside the buttons.
        button_radius: Corner radius of the buttons.
        margin: Outer margin around the footer's button row.
        spacing: Gap between the Save and Reset buttons.
        menu_button_width: Width of the Reset button's dropdown segment.
        menu_arrow_size: Size of the dropdown arrow glyph.
        menu_padding: Padding inside the Reset dropdown menu.
        menu_item_padding_v: Vertical padding of a dropdown menu item.
        menu_item_padding_h: Horizontal padding of a dropdown menu item.
    """

    button_height: int = 42
    button_padding_h: int = 18
    button_padding_v: int = 6
    button_radius: int = 8
    margin: int = 8
    spacing: int = 8
    menu_button_width: int = 20
    menu_arrow_size: int = 12
    menu_padding: int = 4
    menu_item_padding_v: int = 6
    menu_item_padding_h: int = 24


@dataclass(frozen=True)
class ProfileLayout:
    """Appearance of the profile list in the left sidebar.

    Attributes:
        title_font_size: Font size for the "PROFILES" section title.
        profile_height: Height of each profile item in the list.
        profile_icon_size: Icon size for profile icons.
        profile_border_left: Left border width of the active profile item.
        profile_border_radius: Corner radius of profile items.
        profile_item_padding_h: Horizontal padding inside a profile item.
        profile_item_padding_v: Vertical padding inside a profile item.
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
    profile_item_padding_h: int = 8
    profile_item_padding_v: int = 4
    profile_spacing: int = 4
    toolbar_button_size: int = 36
    toolbar_button_icon_size: int = 24
    toolbar_button_border_radius: int = 8
    saved_icon_size: int = 128


@dataclass(frozen=True)
class DialogLayout:
    """Sizes, spacing, and padding for dialogs.

    Attributes:
        min_width: Minimum width of the profile editor dialog.
        dialog_padding: Outer padding around the dialog contents.
        layout_spacing: Vertical gap between top-level sections.
        header_spacing: Gap between the name field and the icon column.
        actions_spacing: Gap between action buttons in the toolbar row.
        match_spacing: Gap between match-rule rows inside the group.
        icon_preview_size: Side length of the square icon preview.
        info_padding_top: Gap above the info note.
        info_max_lines: Height cap for the info note, in font lines.
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

    min_width: int = 520
    dialog_padding: int = 12
    layout_spacing: int = 12
    header_spacing: int = 10
    actions_spacing: int = 6
    match_spacing: int = 8
    icon_preview_size: int = 32
    info_padding_top: int = 6
    info_max_lines: int = 8
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


@dataclass(frozen=True)
class AboutLayout:
    """Dimensions of the About dialog.

    Attributes:
        width: Dialog width in pixels.
        height: Dialog height in pixels.
        padding_h: Horizontal padding inside the dialog.
        padding_top: Top padding inside the dialog.
        padding_bottom: Bottom padding inside the dialog.
        icon_size: Application icon size at the top of the dialog.
        name_font_size: Font size for the application name.
        name_margin_top: Gap above the application name.
        version_font_size: Font size for the version line.
        version_margin_top: Gap above the version line.
        body_font_size: Font size for description and link labels.
        description_margin_top: Gap above the description paragraph.
        description_padding_h: Horizontal inset of the description text.
        link_margin_top: Gap above the links row.
        link_spacing: Gap between individual links in the row.
        close_button_width: Width of the Close button.
        close_button_height: Height of the Close button.
        close_button_font_size: Font size of the Close button label.
        close_button_padding_h: Horizontal padding inside the Close button.
        close_button_padding_v: Vertical padding inside the Close button.
        close_button_radius: Corner radius of the Close button.
    """

    width: int = 480
    height: int = 400
    padding_h: int = 32
    padding_top: int = 28
    padding_bottom: int = 24

    icon_size: int = 96

    name_font_size: int = 24
    name_margin_top: int = 16
    version_font_size: int = 20
    version_margin_top: int = 4

    body_font_size: int = 18
    description_margin_top: int = 18
    description_padding_h: int = 24
    link_margin_top: int = 10
    link_spacing: int = 6

    close_button_width: int = 120
    close_button_height: int = 36
    close_button_font_size: int = 14
    close_button_padding_h: int = 18
    close_button_padding_v: int = 6
    close_button_radius: int = 8


# ---------------------------------------------------------------------------
#  GUIConfig, the top-level configuration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GUIConfig:
    """Central GUI configuration.

    Attributes:
        palette: The active theme (semantic color tokens).
        tile: Tile geometry, animation, shadows, title style.
        filter: Filter bar dimensions.
        sidebar: Sidebar layout (widths, tabs, content margins).
        checkbox: Checkbox indicator dimensions.
        combo: Combo box padding and radius.
        slider: Slider track and handle dimensions.
        edit_field: Text field dimensions.
        swatch: Color swatch and browse button sizes.
        splitter: Splitter handle width.
        scrollbar: Scrollbar thickness, radius, minimum handle length.
        footer: Save / Reset button and dropdown menu dimensions.
        profile: Profile sidebar item and toolbar dimensions.
        dialog: Dialog sizes, spacing, and padding strings.
        about: About dialog dimensions.
        font_family: Font family used for the interface.
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
    scrollbar: ScrollbarLayout = field(default_factory=ScrollbarLayout)
    footer: FooterLayout = field(default_factory=FooterLayout)
    profile: ProfileLayout = field(default_factory=ProfileLayout)
    dialog: DialogLayout = field(default_factory=DialogLayout)
    about: AboutLayout = field(default_factory=AboutLayout)

    font_family: str = ""

    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60

    highlight_border_width: int = 4
    highlight_indicator_gap: int = 8


@dataclass(frozen=True)
class GUIStyleOverrides:
    """User-configurable GUI style attributes.

    Attributes:
        palette: The active color palette.
        zoom: Interface zoom percentage (100 = native size).
        font_family: Interface font family. Empty string means the
            platform default.
        profiles_width: Logical width of the profiles sidebar (left),
            before zoom scaling.
        settings_width: Logical width of the settings sidebar (right),
            before zoom scaling.
        tile_columns: Number of columns in the window grid.
        tile_aspect_ratio: Tile aspect ratio (width / height).
        auto_refresh_ms: Window list refresh interval (ms).
        tile_preview_interval_ms: Tile thumbnail update interval (ms).
    """

    palette: GUIPalette
    zoom: int = 100
    font_family: str = ""
    profiles_width: int = 380
    settings_width: int = 420
    tile_columns: int = 3
    tile_aspect_ratio: float = 4 / 3
    auto_refresh_ms: int = 2000
    tile_preview_interval_ms: int = 60
