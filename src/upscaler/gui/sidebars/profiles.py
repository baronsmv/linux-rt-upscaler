from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
)

from .common import styles
from ..config import GUIConfig
from ..icons import load_icon


class ProfilesSidebar(QWidget):
    profile_selected = Signal(str)
    add_profile_requested = Signal()
    edit_profile_requested = Signal(str)
    delete_profile_requested = Signal(str)
    move_up_requested = Signal(str)
    move_down_requested = Signal(str)

    def __init__(
        self,
        gui_config: GUIConfig,
        profiles: Dict,
        active_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._cfg = gui_config
        self._profiles = profiles
        self._current_index = -1
        self.setObjectName("sidebar_container")
        self.setStyleSheet(styles.sidebar_container(gui_config))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Title
        title = QLabel("Profiles")
        title.setStyleSheet(
            f"color: {gui_config.sidebar_tab_text_color}; "
            f"font-size: {gui_config.sidebar_tab_font_size}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(title)

        # List
        self._list = QListWidget()
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        layout.addWidget(self._list, stretch=1)

        # Toolbar
        toolbar = QHBoxLayout()
        self._add_btn = QPushButton()
        self._add_btn.setIcon(load_icon("profiles/add", 24))
        self._add_btn.setToolTip("Add profile")
        self._add_btn.clicked.connect(self.add_profile_requested.emit)
        toolbar.addWidget(self._add_btn)

        self._edit_btn = QPushButton()
        self._edit_btn.setIcon(load_icon("profiles/edit", 24))
        self._edit_btn.setToolTip("Edit match criteria")
        self._edit_btn.clicked.connect(self._emit_edit)
        self._edit_btn.setEnabled(False)
        toolbar.addWidget(self._edit_btn)

        self._delete_btn = QPushButton()
        self._delete_btn.setIcon(load_icon("profiles/delete", 24))
        self._delete_btn.setToolTip("Delete profile")
        self._delete_btn.clicked.connect(self._emit_delete)
        self._delete_btn.setEnabled(False)
        toolbar.addWidget(self._delete_btn)

        toolbar.addStretch()

        self._up_btn = QPushButton()
        self._up_btn.setIcon(load_icon("profiles/up", 24))
        self._up_btn.setToolTip("Move up")
        self._up_btn.clicked.connect(self._emit_move_up)
        self._up_btn.setEnabled(False)
        toolbar.addWidget(self._up_btn)

        self._down_btn = QPushButton()
        self._down_btn.setIcon(load_icon("profiles/down", 24))
        self._down_btn.setToolTip("Move down")
        self._down_btn.clicked.connect(self._emit_move_down)
        self._down_btn.setEnabled(False)
        toolbar.addWidget(self._down_btn)

        layout.addLayout(toolbar)

        self.populate_list(active_name)

    def populate_list(self, active_name: Optional[str] = None):
        self._list.blockSignals(True)
        self._list.clear()
        # Add default entry
        default_item = QListWidgetItem("(default)")
        default_item.setData(Qt.UserRole, "")  # empty = no profile
        self._list.addItem(default_item)
        if active_name is None or active_name == "":
            self._list.setCurrentRow(0)

        for name in self._profiles.keys():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, name)
            self._list.addItem(item)
            if name == active_name:
                self._list.setCurrentRow(self._list.count() - 1)
        self._list.blockSignals(False)

    def update_profiles(self, profiles: dict) -> None:
        self._profiles = profiles

    def _on_current_item_changed(self, current, previous):
        if current:
            name = current.data(Qt.UserRole)
            self._edit_btn.setEnabled(name != "")
            self._delete_btn.setEnabled(name != "")
            self._up_btn.setEnabled(
                name != "" and self._list.row(current) > 1
            )  # after default
            self._down_btn.setEnabled(
                name != "" and self._list.row(current) < self._list.count() - 1
            )
            self.profile_selected.emit(name)
        else:
            self._edit_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
            self._up_btn.setEnabled(False)
            self._down_btn.setEnabled(False)

    def _emit_edit(self):
        item = self._list.currentItem()
        if item and item.data(Qt.UserRole):
            self.edit_profile_requested.emit(item.data(Qt.UserRole))

    def _emit_delete(self):
        item = self._list.currentItem()
        if item and item.data(Qt.UserRole):
            self.delete_profile_requested.emit(item.data(Qt.UserRole))

    def _emit_move_up(self):
        item = self._list.currentItem()
        if item and item.data(Qt.UserRole):
            self.move_up_requested.emit(item.data(Qt.UserRole))

    def _emit_move_down(self):
        item = self._list.currentItem()
        if item and item.data(Qt.UserRole):
            self.move_down_requested.emit(item.data(Qt.UserRole))
