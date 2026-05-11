from pathlib import Path
from typing import Optional

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_ICONS_DIR = Path(__file__).parent


def _load_svg(name: str) -> str:
    """Read an SVG file from the icons directory."""
    path = _ICONS_DIR / f"{name}.svg"
    if not path.is_file():
        raise FileNotFoundError(f"Icon not found: {path}")
    return path.read_text(encoding="utf-8")


def load_pixmap(
    name: str, width: int = 256, height: int = 256, color: Optional[str] = None
) -> QPixmap:
    """Render an SVG icon to a QPixmap of the given size."""
    svg = _load_svg(name)
    if color is not None:
        svg = svg.replace("#7A9EB1", color)
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def load_icon(
    name: str, width: int = 24, height: int = 24, color: Optional[str] = None
) -> QIcon:
    """Load an SVG icon as a QIcon, suitable for buttons, labels, etc."""
    return QIcon(load_pixmap(name, width, height, color=color))
