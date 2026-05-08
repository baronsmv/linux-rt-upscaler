from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPalette, QColor, QPixmap, QPainter, QIcon
from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel

# Minimalist SVG icons (grayish-blue)
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
    A search bar with icons embedded inside the text field.

    Left icon is a magnifying glass; right clear button appears when
    there is text. Both are drawn via SVG for a clean, scalable look.
    The whole bar brightens on hover (configurable colour).
    """

    focus_grid_requested = Signal()
    filter_changed = Signal(str)

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self._cfg = gui_config

        # ----- Bar size -----
        self.setFixedHeight(gui_config.filter_height)
        self.setAttribute(Qt.WA_Hover, True)

        # ----- Line edit (filling the whole bar) -----
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText("Filter windows…")
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.installEventFilter(self)

        # Adjust left/right padding so text doesn't overlap icons
        icon_size = 20
        pad = gui_config.filter_padding_h + icon_size + 6  # 6px gap
        self._line_edit.setStyleSheet("")  # will be set by _update_style
        self._line_edit.setTextMargins(pad, 0, pad, 0)

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

    # ------------------------------------------------------------------
    #  Resize event – position icons inside the line edit
    # ------------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        # Search icon: left side
        left_margin = self._cfg.filter_padding_h + 6
        icon_y = (self.height() - self._search_icon.height()) // 2
        self._search_icon.move(left_margin, icon_y)

        # Clear button: right side
        right_margin = self._cfg.filter_padding_h + 6
        clear_x = self.width() - right_margin - self._clear_button.width()
        self._clear_button.move(clear_x, icon_y)

        # Resize line edit to fill the whole bar (icons are on top)
        self._line_edit.setGeometry(0, 0, self.width(), self.height())

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------
    def _render_svg(self, svg: str, w: int, h: int) -> QPixmap:
        """Render an SVG string to a QPixmap of the given size."""
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
        """Turn SVG into a QIcon."""
        return QIcon(self._render_svg(svg, size, size))

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
                padding: 0px;  /* padding handled by text margins */
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
