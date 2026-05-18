from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QSplitter, QSplitterHandle

if TYPE_CHECKING:
    from ..config import GUIConfig


class StyledSplitterHandle(QSplitterHandle):
    """A splitter handle that paints a subtle vertical grip."""

    def __init__(self, orientation: Qt.Orientation, splitter: QSplitter) -> None:
        super().__init__(orientation, splitter)
        self._cfg: Optional[GUIConfig] = None

    def set_config(self, cfg: GUIConfig) -> None:
        self._cfg = cfg

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cfg = self._cfg
        handle_color = QColor(cfg.splitter_handle_color)
        hover_color = QColor(cfg.splitter_handle_hover_color)
        handle_width = cfg.splitter_handle_width

        # Determine if mouse is hovering (simplistic: use underMouse)
        is_hover = self.underMouse()
        color = hover_color if is_hover else handle_color

        w = self.width()
        h = self.height()

        if self.orientation() == Qt.Horizontal:
            # Vertical handle
            cx = w // 2
            pen = QPen(color)
            pen.setWidth(handle_width)
            painter.setPen(pen)
            painter.drawLine(cx, 0, cx, h)

            # Optional: small grip dots
            dot_color = color.lighter(150) if is_hover else color.darker(120)
            painter.setPen(Qt.NoPen)
            painter.setBrush(dot_color)
            radius = 2
            spacing = 8
            num_dots = 3
            total_height = (num_dots - 1) * spacing * 2
            start_y = (h - total_height) // 2
            for i in range(num_dots):
                painter.drawEllipse(
                    cx - radius,
                    start_y + i * spacing * 2 - radius,
                    radius * 2,
                    radius * 2,
                )
        else:
            # Horizontal handle (not used in our layout, but handled for completeness)
            cy = h // 2
            pen = QPen(color)
            pen.setWidth(handle_width)
            painter.setPen(pen)
            painter.drawLine(0, cy, w, cy)

        painter.end()


class StyledSplitter(QSplitter):
    """A QSplitter that uses StyledSplitterHandle for a modern look."""

    def __init__(self, orientation: Qt.Orientation, gui_config: GUIConfig, parent=None):
        super().__init__(orientation, parent)
        self._cfg = gui_config
        self.setHandleWidth(
            gui_config.splitter_handle_width + 10
        )  # enough for grip dots
        self.setStyleSheet("QSplitter::handle { background: transparent; }")

    def createHandle(self) -> QSplitterHandle:
        handle = StyledSplitterHandle(self.orientation(), self)
        handle.set_config(self._cfg)
        return handle
