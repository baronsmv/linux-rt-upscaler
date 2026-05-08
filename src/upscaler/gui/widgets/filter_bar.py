from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon
from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel

# SVG icons
SEARCH_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#7A9EB1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="11" cy="11" r="8"/>
    <line x1="21" y1="21" x2="16.65" y2="16.65"/>
</svg>
"""

CLEAR_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#7A9EB1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/>
    <line x1="6" y1="6" x2="18" y2="18"/>
</svg>
"""


class FilterBar(QWidget):
    """
    A search bar with embedded icons and configurable geometry.

    All dimensional constants and colours are taken from a :class:`GUIConfig`
    instance. The bar uses symmetrical horizontal and vertical padding,
    and places icons inside the text field with a configurable gap.
    """

    focus_grid_requested = Signal()
    filter_changed = Signal(str)

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self._cfg = gui_config
        cfg = gui_config

        # Fixed height from config; no separate “height” field needed for the line edit.
        self.setFixedHeight(cfg.filter_height)
        self.setAttribute(Qt.WA_Hover, True)

        # ----- Line edit (fills the whole widget minus margins) -----
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText("Filter windows…")
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.installEventFilter(self)

        # Search icon – fixed size
        icon_size = cfg.filter_icon_size
        icon_gap = cfg.filter_icon_gap

        # Outer horizontal margin (replaces grid_margin for the bar)
        outer_h_margin = cfg.filter_horizontal_margin
        inner_h_pad = cfg.filter_padding_h  # space from bar edge to icon
        text_left_pad = outer_h_margin + inner_h_pad + icon_size + icon_gap
        text_right_pad = outer_h_margin + inner_h_pad + icon_size + icon_gap
        self._line_edit.setTextMargins(text_left_pad, 0, text_right_pad, 0)

        # ----- Search icon (QLabel) -----
        self._search_icon = QLabel(self)
        self._search_icon.setFixedSize(icon_size, icon_size)
        self._search_icon.setPixmap(
            self._render_svg(SEARCH_ICON_SVG, icon_size, icon_size)
        )

        # ----- Clear button -----
        self._clear_button = QPushButton(self)
        self._clear_button.setFixedSize(icon_size, icon_size)
        self._clear_button.setIcon(self._render_svg_icon(CLEAR_ICON_SVG, icon_size))
        self._clear_button.setFlat(True)
        self._clear_button.setCursor(Qt.ArrowCursor)
        self._clear_button.clicked.connect(self._line_edit.clear)
        self._clear_button.hide()

        # Apply initial style
        self._update_bar_style(hover=False)

        # Force an initial layout pass
        self._position_elements()

    # ------------------------------------------------------------------
    #  Resize handling
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_elements()

    def _position_elements(self) -> None:
        """Place the line edit and icons according to config margins/padding."""
        cfg = self._cfg
        outer_margin = cfg.filter_horizontal_margin
        inner_h_pad = cfg.filter_padding_h
        vertical_pad = cfg.filter_padding_v
        icon_size = cfg.filter_icon_size

        # Line edit fills the bar, inset by margins
        lx = outer_margin
        ly = vertical_pad
        lw = self.width() - 2 * outer_margin
        lh = self.height() - 2 * vertical_pad
        self._line_edit.setGeometry(lx, ly, lw, lh)

        # Search icon – flush with the left edge of the line edit + inner horizontal pad
        icon_x = lx + inner_h_pad
        icon_y = (self.height() - icon_size) // 2
        self._search_icon.move(icon_x, icon_y)

        # Clear button – same spacing from the right edge
        clear_x = lx + lw - inner_h_pad - icon_size
        self._clear_button.move(clear_x, icon_y)

    # ------------------------------------------------------------------
    #  SVG rendering helpers
    # ------------------------------------------------------------------
    def _render_svg(self, svg: str, w: int, h: int) -> QPixmap:
        from PySide6.QtSvg import QSvgRenderer
        from PySide6.QtCore import QByteArray

        renderer = QSvgRenderer(QByteArray(svg.encode()))
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return pixmap

    def _render_svg_icon(self, svg: str, size: int) -> QIcon:
        return QIcon(self._render_svg(svg, size, size))

    # ------------------------------------------------------------------
    #  Style (hover / normal)
    # ------------------------------------------------------------------
    def _update_bar_style(self, hover: bool) -> None:
        cfg = self._cfg
        bg = cfg.filter_hover_background if hover else cfg.filter_background
        self._line_edit.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {cfg.filter_border_color};
                border-radius: {cfg.filter_border_radius}px;
                background: {bg};
                color: {cfg.filter_text_color};
                font-size: {cfg.filter_font_size}px;
                padding: 0px;  /* handled via setTextMargins */
                selection-background-color: {cfg.filter_border_focus_color};
            }}
            QLineEdit:focus {{
                border-color: {cfg.filter_border_focus_color};
            }}
        """
        )
        pal = self._line_edit.palette()
        pal.setColor(QPalette.PlaceholderText, QColor(cfg.filter_placeholder_color))
        self._line_edit.setPalette(pal)

    # ------------------------------------------------------------------
    #  Text changes
    # ------------------------------------------------------------------
    def _on_text_changed(self, text: str) -> None:
        self._clear_button.setVisible(bool(text))
        self.filter_changed.emit(text)

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------
    def text(self) -> str:
        return self._line_edit.text()

    def set_text(self, text: str) -> None:
        self._line_edit.setText(text)

    def clear(self) -> None:
        self._line_edit.clear()

    def set_focus(self) -> None:
        self._line_edit.setFocus()
        self._line_edit.selectAll()

    # ------------------------------------------------------------------
    #  Keyboard navigation
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event: QEvent) -> bool:
        if obj == self._line_edit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Down:
                self.focus_grid_requested.emit()
                return True
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    #  Hover effect
    # ------------------------------------------------------------------
    def enterEvent(self, event) -> None:
        self._update_bar_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._update_bar_style(hover=False)
        super().leaveEvent(event)
