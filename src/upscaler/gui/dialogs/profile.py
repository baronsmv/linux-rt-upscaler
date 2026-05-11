from __future__ import annotations

import os
from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
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

MATCH_TYPES = {
    "title_contains": "Title contains",
    "title_regex": "Title regex",
    "title_exact": "Title exact",
    "class_contains": "Class contains",
    "class_regex": "Class regex",
    "class_exact": "Class exact",
}


class MatchCriterion:
    def __init__(self, key: str, value: str):
        self.key = key
        self.value = value


class ProfileDialog(QDialog):
    def __init__(
        self,
        gui_config: GUIConfig,
        profile_name: str = "",
        match: Optional[Dict[str, str]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._cfg = gui_config
        self._match_criteria: List[MatchCriterion] = []
        self._captured_icon: Optional[QImage] = None
        self._icon_removed = False

        self.setWindowTitle("Profile Editor" if profile_name else "New Profile")
        self.setMinimumWidth(520)
        self.setStyleSheet(list_stylesheet(gui_config))

        # Exclude our own window from the picker
        self._exclude_handle = parent.winId() if parent else 0

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

        # Icon area
        icon_col = QVBoxLayout()
        icon_label = QLabel("Icon")
        icon_label.setStyleSheet("font-weight: bold;")
        icon_col.addWidget(icon_label)

        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(32, 32)
        self._icon_preview.setStyleSheet("border: 1px solid #444; border-radius: 4px;")
        self._icon_preview.setAlignment(Qt.AlignCenter)

        # Load existing icon if any
        if profile_name and parent and hasattr(parent, "profiles"):
            icon_path = parent.profiles.get(profile_name, {}).get("icon", "")
            if icon_path and os.path.isfile(icon_path):
                pix = QPixmap(icon_path).scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self._icon_preview.setPixmap(pix)
                self._captured_icon = QImage(icon_path)
            else:
                self._icon_preview.setPixmap(load_pixmap("actions/profile", 32, 32))
        else:
            self._icon_preview.setPixmap(load_pixmap("actions/profile", 32, 32))

        icon_col.addWidget(self._icon_preview)
        header.addLayout(icon_col)
        layout.addLayout(header)

        # Action buttons: Capture Window, Capture Icon, File..., Remove
        actions_row = QHBoxLayout()
        actions_row.setSpacing(6)

        capture_win_btn = QPushButton("  Capture window")
        capture_win_btn.setIcon(load_icon("actions/capture", 20))
        capture_win_btn.setToolTip(
            "Fill name, icon, and basic match criteria from a window"
        )
        capture_win_btn.clicked.connect(self._capture_full)
        actions_row.addWidget(capture_win_btn)

        actions_row.addStretch()

        icon_btn_size = gui_config.dialog_icon_button_size
        icon_size = gui_config.dialog_icon_button_icon_size

        self._make_icon_btn = (
            lambda name, tip, slot, enabled=True: self._create_icon_button(
                name, tip, slot, icon_btn_size, icon_size, enabled
            )
        )

        self._capture_icon_btn = self._make_icon_btn(
            "actions/camera", "Capture icon from window", self._capture_icon
        )
        self._file_btn = self._make_icon_btn(
            "actions/folder", "Load icon from file", self._select_icon_file
        )
        self._remove_icon_btn = self._make_icon_btn(
            "actions/delete", "Remove icon", self._remove_icon
        )

        actions_row.addWidget(self._capture_icon_btn)
        actions_row.addWidget(self._file_btn)
        actions_row.addWidget(self._remove_icon_btn)

        layout.addLayout(actions_row)

        # ── Match criteria group ─────────────────────────────────────
        crit_group = QGroupBox("Match criteria")
        crit_layout = QVBoxLayout(crit_group)

        self._crit_list = QListWidget()
        self._crit_list.setAlternatingRowColors(False)
        self._crit_list.setSelectionMode(QListWidget.ExtendedSelection)
        crit_layout.addWidget(self._crit_list)

        add_remove_row = QHBoxLayout()
        self._type_combo = QComboBox()
        for key, label in MATCH_TYPES.items():
            self._type_combo.addItem(label, key)
        add_remove_row.addWidget(self._type_combo)
        self._value_edit = QLineEdit()
        self._value_edit.setPlaceholderText("Value")
        add_remove_row.addWidget(self._value_edit)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_criterion)
        add_remove_row.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_selected)
        add_remove_row.addWidget(remove_btn)

        crit_layout.addLayout(add_remove_row)
        layout.addWidget(crit_group)

        # ── Dialog buttons ───────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self._validate_and_accept)
        self._button_box.rejected.connect(self.reject)
        btn_layout.addWidget(self._button_box)
        layout.addLayout(btn_layout)

        # Populate existing criteria
        if match:
            for key, value in match.items():
                if key in MATCH_TYPES:
                    self._match_criteria.append(MatchCriterion(key, value))
        self._refresh_list()

    # ------------------------------------------------------------------
    #  Icon button helper
    # ------------------------------------------------------------------
    def _create_icon_button(
        self,
        icon_name: str,
        tooltip: str,
        callback,
        size: int,
        icon_size: int,
        enabled: bool = True,
    ) -> QToolButton:
        btn = QToolButton()
        btn.setIcon(load_icon(icon_name, icon_size))
        btn.setToolTip(tooltip)
        btn.setFixedSize(size, size)
        btn.setIconSize(QSize(icon_size, icon_size))
        btn.setCursor(Qt.PointingHandCursor)
        btn.setAutoRaise(True)
        btn.setEnabled(enabled)
        btn.clicked.connect(callback)
        return btn

    # ------------------------------------------------------------------
    #  Match criteria
    # ------------------------------------------------------------------
    def _add_criterion(self):
        key = self._type_combo.currentData()
        value = self._value_edit.text().strip()
        if not value:
            QMessageBox.warning(
                self, "Missing value", "Enter a value for the criterion."
            )
            return
        self._match_criteria.append(MatchCriterion(key, value))
        self._value_edit.clear()
        self._refresh_list()

    def _refresh_list(self):
        self._crit_list.clear()
        for crit in self._match_criteria:
            label = f"{MATCH_TYPES[crit.key]}: {crit.value}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, crit)
            self._crit_list.addItem(item)

    def _remove_selected(self):
        for item in self._crit_list.selectedItems():
            crit = item.data(Qt.UserRole)
            self._match_criteria.remove(crit)
            self._crit_list.takeItem(self._crit_list.row(item))

    # ------------------------------------------------------------------
    #  Full capture (name + icon + match)
    # ------------------------------------------------------------------
    def _capture_full(self):
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if not win_info:
                return

            # Fill name (only if empty or it's a new profile)
            if not self._name_edit.text().strip():
                self._name_edit.setText(win_info.title)

            # Fill icon
            self._apply_icon_from_window(win_info)

            # Fill match criteria
            self._match_criteria.append(
                MatchCriterion("title_contains", win_info.title)
            )
            class_name = "unknown"
            try:
                from ...window.info import (
                    get_window_class,
                    AtomCache,
                    open_xcb_connection,
                    close_xcb_connection,
                )

                conn = open_xcb_connection()
                if conn:
                    atoms = AtomCache(conn)
                    klass = get_window_class(conn, win_info.handle, atoms)
                    if klass:
                        class_name = klass[1]
                    close_xcb_connection(conn)
            except Exception:
                pass
            self._match_criteria.append(MatchCriterion("class_exact", class_name))
            self._refresh_list()

    # ------------------------------------------------------------------
    #  Icon capture from window
    # ------------------------------------------------------------------
    def _capture_icon(self):
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                self._apply_icon_from_window(win_info)

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
        self._icon_preview.setPixmap(load_pixmap("actions/profile", 32, 32))

    def get_captured_icon(self) -> Optional[QImage]:
        return self._captured_icon

    def is_icon_removed(self) -> bool:
        return self._icon_removed

    # ------------------------------------------------------------------
    #  Validation
    # ------------------------------------------------------------------
    def _validate_and_accept(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Profile name cannot be empty.")
            return
        self._profile_name = name
        self._match_dict = {}
        for crit in self._match_criteria:
            self._match_dict[crit.key] = crit.value
        self.accept()

    def profile_name(self) -> str:
        return self._profile_name

    def match_criteria(self) -> Dict[str, str]:
        return self._match_dict
