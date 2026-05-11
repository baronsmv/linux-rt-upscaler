from __future__ import annotations

import os
from typing import Dict, List, Optional, TYPE_CHECKING

from PySide6.QtCore import Qt
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
    QVBoxLayout,
    QWidget,
)

from ._styles import list_stylesheet
from .window import WindowPickerDialog
from ..icons import load_pixmap
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
    """Dialog for adding or editing a profile’s match criteria."""

    def __init__(
        self,
        gui_config: GUIConfig,
        profile_name: str = "",
        match: Optional[Dict[str, str]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._exclude_handle = parent.winId() if parent else 0
        self.setWindowTitle("Profile Editor" if profile_name else "New Profile")
        self.setMinimumWidth(480)
        self._cfg = gui_config
        self._match_criteria: List[MatchCriterion] = []
        self._captured_icon: Optional[QImage] = None
        self._icon_removed = False

        self.setStyleSheet(list_stylesheet(gui_config))

        layout = QVBoxLayout(self)

        # ---- Name ----
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self._name_edit = QLineEdit(profile_name)
        name_layout.addWidget(self._name_edit)
        layout.addLayout(name_layout)

        # ---- Icon ----
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(32, 32)
        self._icon_preview.setStyleSheet("border: 1px solid #444; border-radius: 4px;")
        self._icon_preview.setAlignment(Qt.AlignCenter)

        # Try to load existing icon if profile_name is given and exists
        existing_icon = None
        if profile_name and parent is not None and hasattr(parent, "profiles"):
            profile_data = parent.profiles.get(profile_name, {})
            icon_path = profile_data.get("icon", "")
            if icon_path and os.path.isfile(icon_path):
                pix = QPixmap(icon_path).scaled(
                    32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self._icon_preview.setPixmap(pix)
                self._captured_icon = QImage(icon_path)  # store for possible keep
                existing_icon = True

        if not existing_icon:
            self._icon_preview.setPixmap(load_pixmap("actions/profile", 32, 32))

        icon_layout.addWidget(self._icon_preview)

        capture_icon_btn = QPushButton("Capture")
        capture_icon_btn.setToolTip("Grab icon from a window")
        capture_icon_btn.clicked.connect(self._capture_icon)
        icon_layout.addWidget(capture_icon_btn)

        file_btn = QPushButton("File…")
        file_btn.setToolTip("Choose an image file")
        file_btn.clicked.connect(self._select_icon_file)
        icon_layout.addWidget(file_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.setToolTip("Remove the current icon")
        remove_btn.clicked.connect(self._remove_icon)
        icon_layout.addWidget(remove_btn)

        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        # ---- Match criteria group ----
        crit_group = QGroupBox("Match criteria")
        crit_layout = QVBoxLayout(crit_group)

        self._crit_list = QListWidget()
        self._crit_list.setAlternatingRowColors(False)
        self._crit_list.setSelectionMode(QListWidget.ExtendedSelection)
        crit_layout.addWidget(self._crit_list)

        # Add / Remove row
        add_layout = QHBoxLayout()
        self._type_combo = QComboBox()
        for key, label in MATCH_TYPES.items():
            self._type_combo.addItem(label, key)
        add_layout.addWidget(self._type_combo)
        self._value_edit = QLineEdit()
        self._value_edit.setPlaceholderText("Value")
        add_layout.addWidget(self._value_edit)

        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._add_criterion)
        add_layout.addWidget(add_btn)

        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._remove_selected)
        add_layout.addWidget(remove_btn)

        crit_layout.addLayout(add_layout)
        layout.addWidget(crit_group)

        # ---- Bottom buttons ----
        btn_layout = QHBoxLayout()
        capture_btn = QPushButton("Capture from window")
        capture_btn.setToolTip("Select a window and auto-fill match criteria")
        capture_btn.clicked.connect(self._capture)
        btn_layout.addWidget(capture_btn)
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
    #  Criteria handling
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

    def _capture(self):
        """Open a window picker dialog and auto‑fill criteria."""
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                # Auto-fill: title contains and class exact
                self._match_criteria.append(
                    MatchCriterion("title_contains", win_info.title)
                )
                # Get WM_CLASS, TODO: further implement window-class
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
                            class_name = klass[1]  # the class part
                        close_xcb_connection(conn)
                except Exception:
                    pass
                self._match_criteria.append(MatchCriterion("class_exact", class_name))
                self._refresh_list()

    # ------------------------------------------------------------------
    #  Icon handling
    # ------------------------------------------------------------------
    def _capture_icon(self):
        """Grab an icon from a running window."""
        picker = WindowPickerDialog(
            self._cfg, self, exclude_handle=self._exclude_handle
        )
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
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
                    QMessageBox.information(
                        self, "No icon", "The selected window has no icon."
                    )

    def _select_icon_file(self):
        """Load an icon from a file."""
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
        """Mark the icon for removal (restores default preview)."""
        self._captured_icon = None
        self._icon_removed = True
        self._icon_preview.setPixmap(load_pixmap("actions/profile", 32, 32))

    def get_captured_icon(self) -> Optional[QImage]:
        """Return the image to save as profile icon, if any."""
        return self._captured_icon

    def is_icon_removed(self) -> bool:
        """Return True if the user requested icon removal."""
        return self._icon_removed

    # ------------------------------------------------------------------
    #  Validation and result accessors
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
