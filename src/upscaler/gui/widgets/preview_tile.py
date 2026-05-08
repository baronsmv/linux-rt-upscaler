from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from .preview import PreviewWidget
from ...window import WindowInfo


class PreviewTile(QFrame):
    """
    A clickable tile showing a live preview of a window and its title.

    Emits :attr:`clicked` when the user clicks on the tile.
    """

    clicked = Signal(WindowInfo)

    def __init__(self, win_info: WindowInfo, tile_size: int = 200, parent=None):
        super().__init__(parent)
        self._win_info = win_info
        self.setFixedSize(tile_size, tile_size + 30)
        self.setCursor(Qt.PointingHandCursor)
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        self.preview = PreviewWidget(self)
        layout.addWidget(self.preview, stretch=1)

        self.title_label = QLabel(win_info.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("color: #ccc; font-size: 11px; border: none;")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(28)
        layout.addWidget(self.title_label)

        # Start preview
        self.preview.set_target(win_info)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._win_info)
        super().mousePressEvent(event)

    def stop(self) -> None:
        self.preview.set_target(None)
