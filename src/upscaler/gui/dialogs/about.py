from __future__ import annotations

from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..icons import load_icon
from ..styles import (
    close_dialog_button_style,
    about_dialog_description_style,
    about_dialog_link_style,
    about_dialog_name_style,
    dialog_style,
    about_dialog_version_style,
)
from ...config import get_version

if TYPE_CHECKING:
    from .. import GUIConfig


LINKS = {
    "GitHub": "https://github.com/baronsmv/linux-rt-upscaler",
    "Docs": "https://baronsmv.github.io/linux-rt-upscaler/",
}


def _separate_labels(label_list: List[QLabel], sep: QLabel) -> List[QLabel]:
    result = []
    for i, item in enumerate(label_list):
        if i:
            result.append(sep)
        result.append(item)
    return result


def _links_layout(links: Dict[str, str], gui_config: GUIConfig) -> QHBoxLayout:
    """Build layout for links."""
    label_list: List[QLabel] = []
    for label, url in links.items():
        link = QLabel()
        link.setText(
            f"<a href='{url}' style='color: #4a9eff; text-decoration: none;'>{label}</a>"
        )
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignCenter)
        link.setCursor(Qt.PointingHandCursor)
        link.setStyleSheet(about_dialog_link_style(gui_config))
        label_list.append(link)

    # Links separator
    sep = QLabel("|")
    sep.setAlignment(Qt.AlignCenter)
    sep.setStyleSheet(about_dialog_link_style(gui_config))

    # Links layout
    links_layout = QHBoxLayout()
    for label in _separate_labels(label_list, sep):
        links_layout.addWidget(label)
    links_layout.setSpacing(gui_config.about.link_spacing)
    links_layout.setAlignment(Qt.AlignCenter)

    return links_layout


class AboutDialog(QDialog):
    """Modal dialog displaying application information."""

    def __init__(self, gui_config: GUIConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        cfg = gui_config
        a = cfg.about

        self.setWindowTitle(self.tr("About"))
        self.setFixedSize(a.width, a.height)
        self.setStyleSheet(dialog_style(cfg))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            a.padding_h, a.padding_top, a.padding_h, a.padding_bottom
        )
        layout.setSpacing(0)

        # App icon
        icon = QLabel()
        pixmap = load_icon(
            "app/app", a.icon_size, a.icon_size, color=cfg.palette.control
        ).pixmap(a.icon_size, a.icon_size)
        icon.setPixmap(pixmap)
        icon.setFixedSize(a.icon_size, a.icon_size)

        icon_container = QVBoxLayout()
        icon_container.addStretch()
        icon_container.addWidget(icon, alignment=Qt.AlignCenter)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        # App name
        name = QLabel(self.tr("Real-Time Upscaler", "Name of the application"))
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(about_dialog_name_style(gui_config))
        layout.addWidget(name)

        # Version
        version = QLabel(
            self.tr("Version {0}", "Version of the upscaler").format(get_version())
        )
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(about_dialog_version_style(gui_config))
        layout.addWidget(version)

        # Description
        desc = QLabel(
            self.tr(
                "A real-time SRCNN upscaler for any X-Window on GNU/Linux.",
                "Description of the upscaler",
            )
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(about_dialog_description_style(gui_config))
        layout.addWidget(desc)

        # Links
        layout.addLayout(_links_layout(LINKS, gui_config=gui_config))
        layout.addStretch()

        # Close button
        close_btn = QPushButton(self.tr("Close", "Close button"))
        close_btn.setFixedSize(a.close_button_width, a.close_button_height)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(close_dialog_button_style(gui_config))

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addLayout(btn_layout)
