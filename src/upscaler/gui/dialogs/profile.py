from __future__ import annotations

import os
from typing import Dict, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ._styles import list_stylesheet
from .window import WindowPickerDialog
from ..icons import load_icon, load_pixmap
from ...window import get_window_icon

if TYPE_CHECKING:
    from ..config import GUIConfig


class ProfileDialog(QDialog):
    """Dialog for creating or editing a profile’s name, icon, and match rules."""

    def __init__(
        self,
        gui_config: GUIConfig,
        profile_name: str = "",
        match: Optional[Dict[str, str]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._cfg = gui_config

        self._original_name = profile_name
        self.setWindowTitle("Profile Editor" if profile_name else "New Profile")
        self.setMinimumWidth(520)
        self.setStyleSheet(list_stylesheet(gui_config))

        # Exclude parent window from the picker
        self._exclude_handle = parent.winId() if parent else 0

        # Icon state
        self._captured_icon: Optional[QImage] = None
        self._icon_removed = False

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Header: Name + Icon ──────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        # Name field
        name_col = QVBoxLayout()
        name_label = QLabel("Name")
        name_label.setStyleSheet("font-weight: bold;")
        name_col.addWidget(name_label)
        self._name_edit = QLineEdit(profile_name)
        self._name_edit.setPlaceholderText("Profile name")
        name_col.addWidget(self._name_edit)
        header.addLayout(name_col, 1)

        # Icon
        icon_col = QVBoxLayout()
        icon_label = QLabel("Icon")
        icon_label.setStyleSheet("font-weight: bold;")
        icon_col.addWidget(icon_label)

        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(32, 32)
        self._icon_preview.setStyleSheet(
            f"border: 1px solid {self._cfg.icon_preview_border_color}; border-radius: 4px;"
        )
        self._icon_preview.setAlignment(Qt.AlignCenter)

        # Load existing icon
        existing_icon_loaded = False
        if profile_name and parent and hasattr(parent, "profiles"):
            profile_data = parent.profiles.get(profile_name, {})
            icon_path = profile_data.get("icon", "")
            if icon_path and os.path.isfile(icon_path):
                pix = QPixmap(icon_path).scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self._icon_preview.setPixmap(pix)
                self._captured_icon = QImage(icon_path)
                existing_icon_loaded = True

        if not existing_icon_loaded:
            self._icon_preview.setPixmap(
                load_pixmap("actions/profile", 32, 32, color=self._cfg.icon_color)
            )

        icon_col.addWidget(self._icon_preview)
        header.addLayout(icon_col)
        layout.addLayout(header)

        # ── Capture / Icon buttons ────────────────────────────────────
        actions_row = QHBoxLayout()
        actions_row.setSpacing(6)

        capture_win_btn = QPushButton("  Capture window")
        capture_win_btn.setIcon(
            load_icon("actions/capture", 20, 20, color=self._cfg.icon_color)
        )
        capture_win_btn.setToolTip("Fill name, icon, and match rules from a window")
        capture_win_btn.clicked.connect(self._capture_full)
        actions_row.addWidget(capture_win_btn)

        actions_row.addStretch()

        btn_size = gui_config.dialog_icon_button_size
        ico_size = gui_config.dialog_icon_button_icon_size

        self._capture_icon_btn = self._make_icon_button(
            "actions/camera",
            "Capture icon from window",
            self._capture_icon,
            btn_size,
            ico_size,
        )
        self._file_btn = self._make_icon_button(
            "actions/folder",
            "Load icon from file",
            self._select_icon_file,
            btn_size,
            ico_size,
        )
        self._remove_icon_btn = self._make_icon_button(
            "actions/delete", "Remove icon", self._remove_icon, btn_size, ico_size
        )

        actions_row.addWidget(self._capture_icon_btn)
        actions_row.addWidget(self._file_btn)
        actions_row.addWidget(self._remove_icon_btn)

        layout.addLayout(actions_row)

        # ── Match rules group ────────────────────────────────────────
        match_group = QGroupBox("Match rules")
        match_layout = QVBoxLayout(match_group)
        match_layout.setSpacing(8)

        # Title contains
        row1 = QHBoxLayout()
        lbl = QLabel("Title contains:")
        lbl.setStyleSheet(
            f"font-size: {self._cfg.dialog_match_label_font_size}px; font-weight: bold;"
        )
        row1.addWidget(lbl)
        self._match_title_contains = QLineEdit()
        self._match_title_contains.setPlaceholderText("e.g., VLC")
        row1.addWidget(self._match_title_contains)
        match_layout.addLayout(row1)

        # Title regex
        row2 = QHBoxLayout()
        lbl2 = QLabel("Title regex:")
        lbl2.setStyleSheet(
            f"font-size: {self._cfg.dialog_match_label_font_size}px; font-weight: bold;"
        )
        row2.addWidget(lbl2)
        self._match_title_regex = QLineEdit()
        self._match_title_regex.setPlaceholderText("e.g., (Yuzu|Ryujinx).*")
        row2.addWidget(self._match_title_regex)
        match_layout.addLayout(row2)

        # Title exact
        row3 = QHBoxLayout()
        lbl3 = QLabel("Title exact:")
        lbl3.setStyleSheet(
            f"font-size: {self._cfg.dialog_match_label_font_size}px; font-weight: bold;"
        )
        row3.addWidget(lbl3)
        self._match_title_exact = QLineEdit()
        self._match_title_exact.setPlaceholderText("e.g., Steam")
        row3.addWidget(self._match_title_exact)
        match_layout.addLayout(row3)

        layout.addWidget(match_group)

        # ── Pre‑fill existing match criteria ─────────────────────────
        if match:
            self._match_title_contains.setText(match.get("title_contains", ""))
            self._match_title_regex.setText(match.get("title_regex", ""))
            self._match_title_exact.setText(match.get("title_exact", ""))

        # ── Dialog buttons ───────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self._validate_and_accept)
        self._button_box.rejected.connect(self.reject)
        btn_row.addWidget(self._button_box)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _make_icon_button(
        self,
        icon_name: str,
        tooltip: str,
        callback,
        size: int,
        icon_size: int,
        enabled: bool = True,
    ) -> QToolButton:
        btn = QToolButton()
        btn.setIcon(
            load_icon(icon_name, icon_size, icon_size, color=self._cfg.icon_color)
        )
        btn.setToolTip(tooltip)
        btn.setFixedSize(size, size)
        btn.setIconSize(QSize(icon_size, icon_size))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setAutoRaise(True)
        btn.setEnabled(enabled)
        btn.clicked.connect(callback)
        return btn

    def _styled_msg_box(
        self, icon: QMessageBox.Icon, title: str, text: str
    ) -> QMessageBox:
        """Return a QMessageBox with the dialog's dark theme applied."""
        msg = QMessageBox(icon, title, text, QMessageBox.Ok, self)
        cfg = self._cfg
        msg.setStyleSheet(
            f"""
            QMessageBox {{
                background-color: {cfg.dialog_background};
                color: {cfg.dialog_text_color};
                font-size: {cfg.dialog_label_font_size}px;
            }}
            QMessageBox QLabel {{
                color: {cfg.dialog_text_color};
                font-size: {cfg.dialog_label_font_size}px;
            }}
            QMessageBox QPushButton {{
                background: {cfg.dialog_button_background};
                border: 1px solid {cfg.dialog_button_border};
                border-radius: {cfg.dialog_button_border_radius}px;
                padding: {cfg.dialog_button_padding};
                color: {cfg.dialog_text_color};
                min-width: 60px;
            }}
            QMessageBox QPushButton:hover {{
                background: {cfg.dialog_button_hover_background};
            }}
            QMessageBox QPushButton:pressed {{
                background: {cfg.dialog_button_pressed_background};
            }}
        """
        )
        return msg

    # ------------------------------------------------------------------
    #  Match rule auto‑fill
    # ------------------------------------------------------------------
    def _capture_full(self):
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if not win_info:
                return

            # Fill name if empty
            if not self._name_edit.text().strip():
                self._name_edit.setText(win_info.title)

            # Fill icon
            self._apply_icon_from_window(win_info)

            # Fill match rules (only if fields are empty)
            if not self._match_title_contains.text().strip():
                self._match_title_contains.setText(win_info.title)

    def _apply_icon_from_window(self, win_info):
        icon_img = get_window_icon(
            win_info.handle, size=self._cfg.profile_capture_icon_size
        )
        if icon_img:
            self._captured_icon = icon_img
            self._icon_removed = False
            pix = QPixmap.fromImage(icon_img).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._icon_preview.setPixmap(pix)
        else:
            QMessageBox.information(self, "No icon", "The selected window has no icon.")

    # ------------------------------------------------------------------
    #  Icon actions
    # ------------------------------------------------------------------
    def _capture_icon(self):
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                self._apply_icon_from_window(win_info)

    def _select_icon_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Icon", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.warning(
                    self, "Invalid image", "Could not load the selected file."
                )
                return
            self._captured_icon = img
            self._icon_removed = False
            pix = QPixmap.fromImage(img).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._icon_preview.setPixmap(pix)

    def _remove_icon(self):
        self._captured_icon = None
        self._icon_removed = True
        self._icon_preview.setPixmap(
            load_pixmap("actions/profile", 32, 32, color=self._cfg.icon_color)
        )

    def get_captured_icon(self) -> Optional[QImage]:
        return self._captured_icon

    def is_icon_removed(self) -> bool:
        return self._icon_removed

    # ------------------------------------------------------------------
    #  Validation & results
    # ------------------------------------------------------------------
    def _validate_and_accept(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Profile name cannot be empty.")
            return

        # Duplicate check, only if the name is different from the original (when editing)
        if name != self._original_name:
            parent = self.parent()
            if parent and hasattr(parent, "profiles") and name in parent.profiles:
                self._styled_msg_box(
                    QMessageBox.Warning,
                    "Duplicate name",
                    f"A profile named '{name}' already exists.\nPlease choose a different name.",
                ).exec()
                self._name_edit.setFocus()
                self._name_edit.selectAll()
                return

        self._profile_name = name
        self._match_dict = {}

        t1 = self._match_title_contains.text().strip()
        if t1:
            self._match_dict["title_contains"] = t1

        t2 = self._match_title_regex.text().strip()
        if t2:
            self._match_dict["title_regex"] = t2

        t3 = self._match_title_exact.text().strip()
        if t3:
            self._match_dict["title_exact"] = t3

        self.accept()

    def profile_name(self) -> str:
        return self._profile_name

    def match_criteria(self) -> Dict[str, str]:
        return self._match_dict
