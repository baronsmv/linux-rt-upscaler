from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel, QPushButton


class FilterBar(QWidget):
    """
    A prominent, self‑contained search bar.

    Features:
        - Magnifying‑glass icon on the left.
        - Clear button (✕) on the right when text is present.
        - Subtle hover brightening (configurable).
        - Arrow‑down moves focus to the window grid; arrow‑up
          (handled externally) brings focus back.
        - All colours and sizes derived from :class:`GUIConfig`.
    """

    focus_grid_requested = Signal()  # Down arrow pressed
    filter_changed = Signal(str)  # emitted on every keystroke

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self._cfg = gui_config

        # --- Layout ---------------------------------------------------------
        layout = QHBoxLayout(self)
        layout.setContentsMargins(gui_config.grid_margin, 6, gui_config.grid_margin, 6)
        layout.setSpacing(8)

        # --- Search icon ----------------------------------------------------
        self._search_icon = QLabel("🔍")
        self._search_icon.setFixedSize(24, 24)
        self._search_icon.setAlignment(Qt.AlignCenter)
        self._search_icon.setStyleSheet(
            f"color: {gui_config.filter_icon_color}; font-size: 16px; border: none; background: transparent;"
        )
        layout.addWidget(self._search_icon)

        # --- Text field -----------------------------------------------------
        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText("Filter windows…")
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.installEventFilter(self)

        layout.addWidget(self._line_edit, stretch=1)

        # --- Clear button ---------------------------------------------------
        self._clear_button = QPushButton("✕")
        self._clear_button.setFixedSize(24, 24)
        self._clear_button.setFlat(True)
        self._clear_button.setCursor(Qt.ArrowCursor)
        self._clear_button.setStyleSheet(
            f"QPushButton {{ color: {gui_config.filter_icon_color}; font-size: 14px; border: none; background: transparent; }}"
            f"QPushButton:hover {{ color: {gui_config.filter_text_color}; }}"
        )
        self._clear_button.clicked.connect(self._line_edit.clear)
        self._clear_button.hide()
        layout.addWidget(self._clear_button)

        # --- Styling --------------------------------------------------------
        self._update_line_style(hover=False)
        self._line_edit.setMinimumHeight(
            gui_config.filter_height
        )  # TODO: derive from height - paddings

        # Hover tracking on the whole widget
        self.setAttribute(Qt.WA_Hover, True)

    # ------------------------------------------------------------------
    #  Style helpers
    # ------------------------------------------------------------------

    def _update_line_style(self, hover: bool) -> None:
        cfg = self._cfg
        bg = cfg.filter_hover_background if hover else cfg.filter_background
        self._line_edit.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {cfg.filter_border_color};
                border-radius: {cfg.filter_border_radius}px;
                padding: {cfg.filter_padding_v}px {cfg.filter_padding_h}px;
                background: {bg};
                color: {cfg.filter_text_color};
                font-size: {cfg.filter_font_size}px;
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
            # Up is handled externally (the grid will trigger it)
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    #  Hover effect
    # ------------------------------------------------------------------

    def enterEvent(self, event) -> None:
        self._update_line_style(hover=True)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._update_line_style(hover=False)
        super().leaveEvent(event)
