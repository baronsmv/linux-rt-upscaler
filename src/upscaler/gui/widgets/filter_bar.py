from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit


class FilterBar(QWidget):
    """
    A search bar styled as a rounded, prominent tile.

    Provides:
        - Live filter text (`filter_changed` signal on each keystroke).
        - Arrow down to leave focus and enter the window grid.
        - Ctrl+F (handled externally) to return focus here.
        - All visual parameters from `GUIConfig`.
    """

    # Emitted when the user wants to move focus to the window grid
    focus_grid_requested = Signal()

    # Emitted whenever the filter text changes
    filter_changed = Signal(str)

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self._cfg = gui_config

        # ---------- layout (single line) ----------
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            gui_config.grid_margin,  # left
            6,  # top (tight)
            gui_config.grid_margin,  # right
            6,  # bottom
        )
        layout.setSpacing(0)

        # ---------- search input ----------
        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText("Filter windows…")
        self._line_edit.textChanged.connect(self.filter_changed)
        self._line_edit.installEventFilter(self)  # capture key events

        # --- styling ---
        self._update_style()
        layout.addWidget(self._line_edit)

        # --- enable keyboard focus ---
        self.setFocusProxy(self._line_edit)  # clicking the bar focusses the input

    # ------------------------------------------------------------------
    #  Style (from GUIConfig)
    # ------------------------------------------------------------------
    def _update_style(self) -> None:
        cfg = self._cfg
        self._line_edit.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {cfg.filter_border_color};
                border-radius: {cfg.filter_border_radius}px;
                padding: {cfg.filter_padding_v}px {cfg.filter_padding_h}px;
                background: {cfg.filter_background};
                color: {cfg.filter_text_color};
                font-size: {cfg.filter_font_size}px;
                selection-background-color: {cfg.filter_border_focus_color};
            }}
            QLineEdit:focus {{
                border-color: {cfg.filter_border_focus_color};
            }}
        """
        )
        # Placeholder colour (depends on palette)
        pal = self._line_edit.palette()
        pal.setColor(QPalette.PlaceholderText, QColor(cfg.filter_placeholder_color))
        self._line_edit.setPalette(pal)

    # ------------------------------------------------------------------
    #  Public interface
    # ------------------------------------------------------------------
    def text(self) -> str:
        return self._line_edit.text()

    def set_text(self, text: str) -> None:
        self._line_edit.setText(text)

    def clear(self) -> None:
        self._line_edit.clear()

    def set_focus(self) -> None:
        """Focus the text field and select all text."""
        self._line_edit.setFocus()
        self._line_edit.selectAll()

    # ------------------------------------------------------------------
    #  Keyboard handling – arrow down moves to grid, others pass through
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event: QEvent) -> bool:
        if obj == self._line_edit and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Down:
                # Move focus to the window grid
                self.focus_grid_requested.emit()
                return True  # swallow the event
            # Let other keys (left/right/enter etc) be handled normally
        return super().eventFilter(obj, event)
