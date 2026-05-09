from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

if TYPE_CHECKING:
    from ...config import GUIConfig


class BaseRow(QWidget):
    """
    Base class for settings rows that support visual hints.

    Provides:
    - A colored left‑side indicator bar that collapses to zero width when hidden.
    - An optional label (added directly to the content layout).
    - A content container with configurable spacing for the actual controls.
    - Abstract `_is_highlighted()` that subclasses implement.
    - `set_baseline()` and automatic highlight updates.
    """

    def __init__(
        self,
        cfg: GUIConfig,
        baseline: Any = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._cfg = cfg
        self._baseline = baseline

        # Main layout: indicator | content container
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- Coloured Bar ----
        self._indicator = QFrame()
        self._indicator.setFixedWidth(cfg.highlight_border_width)
        self._indicator.setStyleSheet(
            f"background: {cfg.highlight_border_color}; border: none;"
        )
        self._indicator.hide()
        main_layout.addWidget(self._indicator)

        # ---- Transparent gap (only visible when highlighted) ----
        self._indicator_spacer = QWidget()
        self._indicator_spacer.setFixedWidth(0)
        main_layout.addWidget(self._indicator_spacer)

        # ---- Content container ----
        self._content_container = QWidget()
        self._content_layout = QHBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(cfg.sidebar_row_spacing)
        main_layout.addWidget(self._content_container)

        # ---- Label (created by subclass via _init_label) ----
        self._label: Optional[QLabel] = None

    # ------------------------------------------------------------------
    #  Subclass API
    # ------------------------------------------------------------------
    def _init_label(self, text: str) -> QLabel:
        """Create a standard row label and add it to the content layout."""
        self._label = QLabel(text)
        self._label.setStyleSheet(
            f"color: {self._cfg.sidebar_tab_text_color}; "
            f"font-size: {self._cfg.sidebar_tab_font_size}px;"
        )
        self._label.setFixedHeight(self._cfg.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self._content_layout.addWidget(self._label)
        return self._label

    # ------------------------------------------------------------------
    #  Highlight logic
    # ------------------------------------------------------------------
    @abstractmethod
    def _is_highlighted(self) -> bool:
        """Return True if the current value differs from the baseline."""
        raise NotImplementedError

    def _update_highlight(self) -> None:
        """Called whenever the value or baseline changes."""
        highlighted = self._is_highlighted()
        if highlighted and self.isEnabled():
            self._indicator.show()
            self._indicator_spacer.setFixedWidth(self._cfg.highlight_indicator_gap)
            if self._cfg.highlight_background_enabled:
                self._content_container.setStyleSheet(
                    f"background: {self._cfg.highlight_background_color}; border-radius: 4px;"
                )
        else:
            self._indicator.hide()
            self._indicator_spacer.setFixedWidth(0)
            self._content_container.setStyleSheet("background: transparent;")
        self._apply_highlight_style(highlighted)

    def _apply_highlight_style(self, highlighted: bool) -> None:
        """
        Update the label colour.
        Disabled always wins – dimmed text, no highlight styling.
        """
        if self._label is None:
            return
        if not self.isEnabled():
            color = self._cfg.control_disabled_text
        elif highlighted:
            color = self._cfg.highlight_label_color
        else:
            color = self._cfg.sidebar_tab_text_color

        self._label.setStyleSheet(
            f"color: {color}; font-size: {self._cfg.sidebar_tab_font_size}px;"
        )

    def set_baseline(self, baseline: Any) -> None:
        self._baseline = baseline
        self._update_highlight()

    def changeEvent(self, event: QEvent) -> None:
        """Re‑highlight when enabled state changes."""
        if event.type() == QEvent.EnabledChange:
            self._on_enabled_changed(self.isEnabled())
            self._update_highlight()
        super().changeEvent(event)

    def _on_enabled_changed(self, enabled: bool) -> None:
        """
        Override in subclasses to update control‑specific styles
        when the row is enabled or disabled.
        """
        pass

    def _make_input_style(self, enabled: bool, extra: str = "") -> str:
        """Return a common stylesheet for QLineEdit-based controls."""
        cfg = self._cfg
        bg = cfg.edit_background if enabled else cfg.edit_background_disabled
        text_color = cfg.edit_text_color if enabled else cfg.edit_text_color_disabled
        border = cfg.edit_border_color if enabled else cfg.control_disabled_border
        focus = cfg.edit_border_focus_color if enabled else cfg.control_disabled_border
        hover = cfg.edit_border_hover_color if enabled else cfg.control_disabled_border
        selection = cfg.edit_selection_background
        return f"""
            QLineEdit {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {cfg.edit_border_radius}px;
                padding: {cfg.edit_padding_v}px {cfg.edit_padding_h}px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
                selection-background-color: {selection};
            }}
            QLineEdit:hover {{
                border-color: {hover};
            }}
            QLineEdit:focus {{
                border-color: {focus};
            }}
            {extra}
        """

    def _make_combo_style(self, enabled: bool) -> str:
        """Return a common stylesheet for QComboBox-based controls."""
        cfg = self._cfg
        bg = cfg.combo_background if enabled else cfg.combo_background_disabled
        text_color = cfg.combo_text_color if enabled else cfg.combo_text_color_disabled
        border = cfg.combo_border_color if enabled else cfg.combo_border_color_disabled
        focus = cfg.combo_border_focus_color if enabled else cfg.control_disabled_border
        hover = cfg.combo_border_hover_color if enabled else cfg.control_disabled_border
        popup_bg = cfg.combo_popup_background
        popup_selection = cfg.combo_popup_selection_background
        popup_text = cfg.combo_popup_text_color

        return f"""
            QComboBox {{
                background: {bg};
                border: 1px solid {border};
                border-radius: {cfg.combo_border_radius}px;
                padding: {cfg.combo_padding_v}px {cfg.combo_padding_h}px;
                color: {text_color};
                font-size: {cfg.sidebar_tab_font_size}px;
            }}
            QComboBox:hover {{
                border-color: {hover};
            }}
            QComboBox:focus {{
                border-color: {focus};
            }}
            QComboBox::drop-down {{
                width: 0px;
                background: transparent;
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background: {popup_bg};
                border: none;
                border-radius: 0px;
                padding: 0px;
                selection-background-color: {popup_selection};
                color: {popup_text};
                outline: none;
            }}
        """
