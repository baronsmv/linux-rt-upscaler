from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from .window import WindowPickerDialog
from ..icons import load_pixmap
from ...window import get_window_icon

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
        profile_name: str = "",
        match: Optional[Dict[str, str]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Profile Editor" if profile_name else "New Profile")
        self.setMinimumWidth(480)
        self._match_criteria: List[MatchCriterion] = []

        # ------------------------------------------------------------------
        # Dark theme stylesheet
        # ------------------------------------------------------------------
        self.setStyleSheet(
            """
            QDialog {
                background-color: #1e1e1e;
                color: #ddd;
            }
            QLabel {
                color: #ccc;
                font-size: 14px;
            }
            QLineEdit {
                background: #2a2a2c;
                border: 1px solid #3a3a3c;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ddd;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
            }
            QComboBox {
                background: #2a2a2c;
                border: 1px solid #3a3a3c;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ddd;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                width: 0px;
            }
            QComboBox QAbstractItemView {
                background: #2a2a2c;
                border: none;
                color: #ddd;
                selection-background-color: #4a9eff;
            }
            QPushButton {
                background: #2c2c2c;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 12px;
                color: #ddd;
            }
            QPushButton:hover {
                background: #3a3a3c;
                border-color: #555;
            }
            QPushButton:pressed {
                background: #222;
            }
            QPushButton:disabled {
                color: #555;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #888;
                border: 1px solid #333;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
            }
            QListWidget {
                background: #1e1e1e;
                border: 1px solid #333;
                border-radius: 6px;
                outline: none;
                color: #ddd;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #2c2c2c;
                color: #fff;
            }
            QListWidget::item:selected {
                background: #3a3a3c;
                color: #fff;
            }
        """
        )

        layout = QVBoxLayout(self)

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self._name_edit = QLineEdit(profile_name)
        name_layout.addWidget(self._name_edit)
        layout.addLayout(name_layout)

        # Icon
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(32, 32)
        self._icon_preview.setStyleSheet("border: 1px solid #444; border-radius: 4px;")
        self._icon_preview.setAlignment(Qt.AlignCenter)
        self._icon_preview.setPixmap(load_pixmap("profiles/profile", 32, 32))
        icon_layout.addWidget(self._icon_preview)
        capture_icon_btn = QPushButton("Capture icon")
        capture_icon_btn.clicked.connect(self._capture_icon)
        icon_layout.addWidget(capture_icon_btn)
        icon_layout.addStretch()
        layout.addLayout(icon_layout)

        # Match criteria group
        crit_group = QGroupBox("Match criteria")
        crit_layout = QVBoxLayout(crit_group)

        # List of criteria
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

        # Bottom buttons
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
        picker = WindowPickerDialog(self)
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                # Auto‑fill: title contains and class exact
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

    def _capture_icon(self):
        picker = WindowPickerDialog(self)
        if picker.exec() == QDialog.Accepted:
            win_info = picker.selected_window()
            if win_info:
                icon_img = get_window_icon(win_info.handle, size=128)
                if icon_img:
                    self._captured_icon = icon_img
                    # Show a 32px preview in the dialog
                    pix = QPixmap.fromImage(icon_img).scaled(
                        32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self._icon_preview.setPixmap(pix)
                else:
                    QMessageBox.information(
                        self, "No icon", "The selected window has no icon."
                    )

    def get_captured_icon(self) -> Optional[QImage]:
        return getattr(self, "_captured_icon", None)

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
