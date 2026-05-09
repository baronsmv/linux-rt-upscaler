from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from ..common import styles

if TYPE_CHECKING:
    from ...config import GUIConfig


class SectionLabel(QWidget):
    """
    A section header widget that displays an uppercase title and a thin
    horizontal separator. The styling is derived from the provided
    :class:`GUIConfig`.
    """

    def __init__(
        self, text: str, gui_config: GUIConfig, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._cfg = gui_config

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._label = QLabel(text.upper())
        self._label.setStyleSheet(styles.section_label(gui_config))

        self._line = QFrame()
        self._line.setFrameShape(QFrame.HLine)
        self._line.setFrameShadow(QFrame.Sunken)
        self._line.setStyleSheet(styles.separator_line())

        layout.addWidget(self._label)
        layout.addWidget(self._line)
