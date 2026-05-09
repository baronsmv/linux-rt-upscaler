from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
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

        # Indicator – hidden by default, width collapsed
        self._indicator = QFrame()
        self._indicator.setStyleSheet(
            f"background: {cfg.highlight_border_color}; border: none;"
        )
        self._indicator_full_width = cfg.highlight_border_width
        self._indicator.setFixedWidth(0)  # collapsed
        self._indicator.hide()
        main_layout.addWidget(self._indicator)

        # Content container – holds label, control, and optional value
        self._content_container = QWidget()
        self._content_layout = QHBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(cfg.sidebar_row_spacing)  # original spacing
        main_layout.addWidget(self._content_container)

        # Label (created by subclass via _init_label)
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
        # Collapse indicator width to 0 when hidden, preserving spacing exactly
        if highlighted and self.isEnabled():
            self._indicator.setFixedWidth(self._indicator_full_width)
            self._indicator.show()
        else:
            self._indicator.hide()
            self._indicator.setFixedWidth(0)
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
