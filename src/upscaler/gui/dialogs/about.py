from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from ..icons import load_icon
from ..styles import (
    about_dialog_close_button_style,
    about_dialog_description_style,
    about_dialog_link_style,
    about_dialog_name_style,
    about_dialog_style,
    about_dialog_version_style,
)
from ...config import get_version


class AboutDialog(QDialog):
    """Modal dialog displaying application information."""

    def __init__(self, gui_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(480, 400)
        self.setStyleSheet(about_dialog_style(gui_config))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 24)
        layout.setSpacing(0)

        # App icon
        icon = QLabel()
        pixmap = load_icon(
            "app/app", 96, 96, color=gui_config.palette.accent_blue
        ).pixmap(96, 96)
        icon.setPixmap(pixmap)
        icon.setFixedSize(96, 96)

        icon_container = QVBoxLayout()
        icon_container.addStretch()
        icon_container.addWidget(icon, alignment=Qt.AlignCenter)
        icon_container.addStretch()
        layout.addLayout(icon_container)

        # App name
        name = QLabel("Real-Time Upscaler")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet(about_dialog_name_style(gui_config))
        layout.addWidget(name)

        # Version
        version = QLabel(f"Version {get_version()}")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(about_dialog_version_style(gui_config))
        layout.addWidget(version)

        # Description
        desc = QLabel("A real-time SRCNN upscaler for any X-Window on GNU/Linux.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setStyleSheet(about_dialog_description_style(gui_config))
        layout.addWidget(desc)

        # GitHub link
        link = QLabel()
        link.setText(
            "<a href='https://github.com/baronsmv/linux-rt-upscaler' "
            "style='color: #4a9eff; text-decoration: none;'>GitHub</a>"
        )
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignCenter)
        link.setCursor(Qt.PointingHandCursor)
        link.setStyleSheet(about_dialog_link_style(gui_config))
        layout.addWidget(link)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(about_dialog_close_button_style(gui_config))

        btn_layout = QVBoxLayout()
        btn_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addLayout(btn_layout)
