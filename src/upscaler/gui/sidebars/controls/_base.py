from __future__ import annotations

from abc import abstractmethod
from typing import Any, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QLabel

if TYPE_CHECKING:
    from ...config import GUIConfig


class BaseRow(QWidget):
    """
    Base class for settings rows that support visual hints.

    Provides:
    - A coloured left‑side indicator bar.
    - An optional label (can be None for checkbox‑style rows).
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
        self._indicator: Optional[QFrame] = None
        self._label: Optional[QLabel] = None

    # ------------------------------------------------------------------
    #  Subclass API
    # ------------------------------------------------------------------
    def _init_indicator(self) -> QFrame:
        """Create and return the indicator widget. Subclasses add it to their layout."""
        self._indicator = QFrame()
        self._indicator.setFixedWidth(self._cfg.highlight_border_width)
        self._indicator.setStyleSheet(
            f"background: {self._cfg.highlight_border_color}; border: none;"
        )
        self._indicator.hide()
        return self._indicator

    def _init_label(self, text: str) -> QLabel:
        """Create and return a standard row label. Subclasses may call this to get a label."""
        self._label = QLabel(text)
        self._label.setStyleSheet(
            f"color: {self._cfg.sidebar_tab_text_color}; font-size: {self._cfg.sidebar_tab_font_size}px;"
        )
        self._label.setFixedHeight(self._cfg.sidebar_row_height)
        self._label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
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
        if self._indicator:
            self._indicator.setVisible(highlighted)
        self._apply_highlight_style(highlighted)

    def _apply_highlight_style(self, highlighted: bool) -> None:
        """
        Override to adjust the appearance of the row when highlighted.
        Default changes the label colour.
        """
        if self._label:
            color = (
                self._cfg.highlight_label_color
                if highlighted
                else self._cfg.sidebar_tab_text_color
            )
            self._label.setStyleSheet(
                f"color: {color}; font-size: {self._cfg.sidebar_tab_font_size}px;"
            )

    def set_baseline(self, baseline: Any) -> None:
        self._baseline = baseline
        self._update_highlight()
