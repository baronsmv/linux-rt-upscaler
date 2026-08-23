from __future__ import annotations

import os
from typing import Callable, Dict, Optional, TYPE_CHECKING

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

from .window import WindowPickerDialog
from ..icons import load_icon, load_pixmap
from ..styles import (
    dialog_header_label_style,
    dialog_icon_button_style,
    dialog_info_label_style,
    dialog_match_label_style,
    dialog_style,
    icon_preview_style,
    line_edit_style,
    message_box_style,
)
from ...window import get_window_icon

if TYPE_CHECKING:
    from ..config import GUIConfig


class ProfileDialog(QDialog):
    """Dialog for creating or editing a profile's name, icon, and match rules."""

    def __init__(
        self,
        gui_config: GUIConfig,
        profile_name: str = "",
        match: Optional[Dict[str, str]] = None,
        profiles: Optional[Dict[str, dict]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._gui_config = gui_config
        self._original_name = profile_name
        self._profiles = profiles or {}
        self._match = match

        self.setWindowTitle(
            self.tr("Profile Editor", "Window title of the profile editor")
            if profile_name
            else self.tr("New Profile", "Window title of the profile creator")
        )
        self.setMinimumWidth(520)
        self.setStyleSheet(dialog_style(self._gui_config))

        # Exclude parent window from the picker
        self._exclude_handle = parent.winId() if parent else 0

        # Icon state
        self._captured_icon: Optional[QImage] = None
        self.icon_removed = False

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Header: Name + Icon ──────────────────────────────────────
        header = QHBoxLayout()
        header.setSpacing(10)

        # Name field
        name_col = QVBoxLayout()
        name_label = QLabel(
            self.tr("Name", disambiguation="Profile dialog label of profile 'Name'")
        )
        name_label.setStyleSheet(dialog_header_label_style(self._gui_config))
        name_col.addWidget(name_label)
        self._name_edit = QLineEdit(profile_name)
        self._name_edit.setStyleSheet(line_edit_style(self._gui_config))
        self._name_edit.setPlaceholderText(
            self.tr("Profile name", "Profile name label")
        )
        self._name_edit.setToolTip(
            self.tr(
                "A unique name for this profile. Required.",
                "Tooltip of profile name text input",
            )
        )
        name_col.addWidget(self._name_edit)
        header.addLayout(name_col, 1)

        # Icon
        icon_col = QVBoxLayout()
        icon_label = QLabel(self.tr("Icon", "Label of Icon button"))
        icon_label.setStyleSheet(dialog_header_label_style(self._gui_config))
        icon_col.addWidget(icon_label)

        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(32, 32)
        self._icon_preview.setStyleSheet(icon_preview_style(self._gui_config))
        self._icon_preview.setAlignment(Qt.AlignCenter)

        # Load existing icon
        existing_icon_loaded = False
        if profile_name and self._profiles:
            profile_data = self._profiles.get(profile_name, {})
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
                load_pixmap(
                    "actions/profile",
                    32,
                    32,
                    color=self._gui_config.palette.icon,
                )
            )

        icon_col.addWidget(self._icon_preview)
        header.addLayout(icon_col)
        layout.addLayout(header)

        # ── Capture / Icon buttons ────────────────────────────────────
        self._actions_row = QHBoxLayout()
        self._actions_row.setSpacing(6)

        # Capture window
        capture_win_btn = QPushButton(
            "\u2009\u2009" + self.tr("Capture window", "'Capture window' button")
        )
        capture_win_btn.setIcon(
            load_icon("actions/capture", 20, 20, color=self._gui_config.palette.icon)
        )
        capture_win_btn.setToolTip(
            self.tr(
                "Fill name, icon, and match rules from a window.",
                "Capture window tooltip",
            )
        )
        capture_win_btn.clicked.connect(self._capture_full)
        self._actions_row.addWidget(capture_win_btn)
        self._actions_row.addStretch()

        # Capture icon
        self._add_icon_button(
            "actions/camera",
            self.tr("Capture icon from window", "Capture icon tooltip"),
            self._capture_icon,
        )
        # Load icon
        self._add_icon_button(
            "actions/folder",
            self.tr("Load icon from file", "Load icon tooltip"),
            self._select_icon_file,
        )
        # Remove icon
        self._add_icon_button(
            "actions/delete",
            self.tr("Remove icon", "Remove icon tooltip"),
            self._remove_icon,
        )
        layout.addLayout(self._actions_row)

        # ── Match rules group ────────────────────────────────────────
        match_group = QGroupBox(self.tr("Match rules", "Match rules group label"))
        match_group.setToolTip(
            self.tr(
                "All filled rules must match for the profile to apply (AND logic).\n"
                "Examples:\n"
                "• Match any Firefox windows wider than 1280px:\n"
                "    • Title (exact): Firefox\n"
                "    • Width: >1280\n"
                "• Match any VLC window (regardless of its size):\n"
                "    • Title contains: VLC\n"
                "• Match emulator windows between 720px and 1080px tall:\n"
                "    • Title (regex): (Yuzu|Ryujinx).*\n"
                "    • Height: 720-1080",
                "Match rules tooltip",
            )
        )
        self._match_layout = QVBoxLayout(match_group)
        self._match_layout.setSpacing(8)
        self._match_rows: Dict[str, QLineEdit] = {}

        # Title exact
        self._match_title_exact = self._add_match_row(
            rule="title_exact",
            label=self.tr("Title (exact):", "Match rule label"),
            placeholder=self.tr("e.g., Steam", "Match rule placeholder"),
            tooltip=(
                self.tr(
                    "Match if the window title exactly equals this text "
                    "(case-insensitive).",
                    "Match rule tooltip",
                )
            ),
        )
        # Title contains
        self._match_title_contains = self._add_match_row(
            rule="title_contains",
            label=self.tr("Title contains:", "Match rule label"),
            placeholder=self.tr("e.g., VLC", "Match rule placeholder"),
            tooltip=(
                self.tr(
                    "Match if the window title contains this text (case-insensitive).",
                    "Match rule tooltip",
                )
            ),
        )
        # Title regex
        self._match_title_regex = self._add_match_row(
            rule="title_regex",
            label=self.tr("Title (regex):", "Match rule label"),
            placeholder=self.tr("e.g., (Yuzu|Ryujinx).*", "Match rule placeholder"),
            tooltip=(
                self.tr(
                    "Match if the window title matches this regular expression "
                    "(case-insensitive).",
                    "Match rule tooltip",
                )
            ),
        )

        # Width
        self._match_width = self._add_match_row(
            rule="width",
            label=self.tr("Width:", "Match rule label"),
            placeholder=self.tr("e.g., >1280", "Match rule placeholder"),
            tooltip=(
                self.tr(
                    "Match if the window width satisfies this condition:\n"
                    "• Exact: 1920\n"
                    "• Comparison: <800, >1024, <=1366, >=1920\n"
                    "• Range: 1280-1920, 720..1080, 1024,1366",
                    "Match rule tooltip",
                )
            ),
        )
        # Height
        self._match_height = self._add_match_row(
            rule="height",
            label=self.tr("Height:", "Match rule label"),
            placeholder=self.tr("e.g., >800", "Match rule placeholder"),
            tooltip=(
                self.tr(
                    "Match if the window height satisfies this condition:\n"
                    f"• Exact: 1080\n"
                    f"• Comparison: <600, >900, <=768, >=1440\n"
                    f"• Range: 480-1080, 600..900, 720,1024",
                    "Match rule tooltip",
                )
            ),
        )

        # Info note
        info = QLabel(
            self.tr(
                "Profiles let you override settings for specific windows and setups.\n"
                "A profile is applied automatically when the upscaled window matches "
                "all the rules defined here, or when manually selected before upscaling.\n"
                "Profiles are checked top-to-bottom: the first match wins.\n"
                "Leave a rule blank to ignore that property.",
                "Profile note",
            )
        )
        info.setWordWrap(True)
        info.setStyleSheet(dialog_info_label_style(self._gui_config))
        self._match_layout.addWidget(info)

        # Add match group
        layout.addWidget(match_group)

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
    def _add_match_row(
        self, rule: str, label: str, placeholder: str, tooltip: str
    ) -> QLineEdit:
        """Add a row to the match rules list."""
        match_label = QLabel(label)
        match_label.setStyleSheet(dialog_match_label_style(self._gui_config))
        line_edit = QLineEdit()
        line_edit.setStyleSheet(line_edit_style(self._gui_config))
        line_edit.setPlaceholderText(placeholder)
        line_edit.setToolTip(tooltip)
        box_layout = QHBoxLayout()
        box_layout.addWidget(match_label)
        box_layout.addWidget(line_edit)
        self._match_layout.addLayout(box_layout)

        if self._match:
            line_edit.setText(self._match.get(rule, ""))

        self._match_rows[rule] = line_edit

        return line_edit

    def _add_icon_button(
        self,
        icon_name: str,
        tooltip: str,
        callback: Callable,
        enabled: bool = True,
    ) -> QToolButton:
        """Add an icon button to the profile toolbar."""
        button_size = self._gui_config.dialog.icon_button_size
        icon_size = self._gui_config.dialog.icon_button_icon_size
        icon_color = self._gui_config.palette.icon
        button = QToolButton()
        button.setIcon(load_icon(icon_name, icon_size, icon_size, color=icon_color))
        button.setStyleSheet(dialog_icon_button_style(self._gui_config))
        button.setToolTip(tooltip)
        button.setFixedSize(button_size, button_size)
        button.setIconSize(QSize(icon_size, icon_size))
        button.setCursor(Qt.PointingHandCursor)
        button.setAutoRaise(True)
        button.setEnabled(enabled)
        button.clicked.connect(callback)
        self._actions_row.addWidget(button)
        return button

    # ------------------------------------------------------------------
    #  Match rule auto-fill
    # ------------------------------------------------------------------
    def _capture_full(self):
        picker = WindowPickerDialog(
            self._gui_config, self, exclude_handle=self._exclude_handle
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
            if not self._match_width.text().strip():
                self._match_width.setText(str(win_info.width))
            if not self._match_height.text().strip():
                self._match_height.setText(str(win_info.height))

    def _apply_icon_from_window(self, win_info):
        icon_img = get_window_icon(
            win_info.handle, size=self._gui_config.profile.saved_icon_size
        )
        if icon_img:
            self._captured_icon = icon_img
            self.icon_removed = False
            pix = QPixmap.fromImage(icon_img).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._icon_preview.setPixmap(pix)
        else:
            QMessageBox.information(
                self,
                self.tr("No icon", "No icon warning"),
                self.tr("The selected window has no icon.", "No icon warning"),
            )

    # ------------------------------------------------------------------
    #  Icon button actions
    # ------------------------------------------------------------------
    def _capture_icon(self) -> None:
        picker = WindowPickerDialog(
            self._gui_config, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                self._apply_icon_from_window(win_info)

    def _select_icon_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Select Icon", "Select Icon dialog title"),
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if file_path:
            img = QImage(file_path)
            if img.isNull():
                QMessageBox.warning(
                    self,
                    self.tr("Invalid image", "Invalid image warning"),
                    self.tr(
                        "Could not load the selected file.", "Invalid image warning"
                    ),
                )
                return
            self._captured_icon = img
            self.icon_removed = False
            pix = QPixmap.fromImage(img).scaled(
                32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self._icon_preview.setPixmap(pix)

    def _remove_icon(self) -> None:
        self._captured_icon = None
        self.icon_removed = True
        self._icon_preview.setPixmap(
            load_pixmap("actions/profile", 32, 32, color=self._gui_config.palette.icon)
        )

    def get_captured_icon(self) -> Optional[QImage]:
        """Return the QImage of the newly selected/captured icon, or None."""
        return self._captured_icon

    # ------------------------------------------------------------------
    #  Validation & results
    # ------------------------------------------------------------------
    def _validate_and_accept(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                self.tr("Missing name", "Warning while saving a profile without name"),
                self.tr(
                    "Profile name cannot be empty.",
                    "Warning while saving a profile without name",
                ),
            )
            return

        # Duplicate check using the provided profiles dictionary
        if name != self._original_name:
            if name in self._profiles:
                msg = QMessageBox(
                    QMessageBox.Warning,
                    self.tr(
                        "Duplicate name",
                        "Warning while saving a profile with an existing name",
                    ),
                    self.tr(
                        "A profile named '{0}' already exists.\nPlease choose a different name.",
                        "Warning while saving a profile with an existing name",
                    ).format(name),
                    QMessageBox.Ok,
                    self,
                )
                msg.setStyleSheet(message_box_style(self._gui_config))
                msg.exec()
                self._name_edit.setFocus()
                self._name_edit.selectAll()
                return

        self._profile_name = name
        self._match_dict = {
            rule: text
            for rule, box_layout in self._match_rows.items()
            if (text := box_layout.text().strip())
        }
        self.accept()

    def profile_name(self) -> str:
        """Return the entered profile name."""
        return self._profile_name

    def match_criteria(self) -> Dict[str, str]:
        """Return the match criteria dictionary."""
        return self._match_dict
