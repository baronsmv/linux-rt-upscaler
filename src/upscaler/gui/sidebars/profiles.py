from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon
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
from ..icons import load_icon, load_pixmap


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
        self.setFixedWidth(gui_config.sidebar_width)
        self.setStyleSheet(styles.sidebar_container(gui_config))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ---- Title ----
        title = QLabel("Profiles")
        title.setStyleSheet(
            f"color: {gui_config.profile_title_color}; "
            f"font-size: {gui_config.profile_title_font_size}px; "
            f"font-weight: {gui_config.profile_title_font_weight};"
        )
        layout.addWidget(title)

        # ---- List ----
        self._list = QListWidget()
        self._list.setStyleSheet(self._list_stylesheet())
        self._list.setIconSize(
            QSize(gui_config.profile_item_icon_size, gui_config.profile_item_icon_size)
        )
        self._list.setSpacing(gui_config.profile_item_spacing)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        layout.addWidget(self._list, stretch=1)

        # ---- Toolbar ----
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        btn_cfg = {
            "size": gui_config.profile_toolbar_button_size,
            "icon_size": gui_config.profile_toolbar_button_icon_size,
            "hover_bg": gui_config.profile_toolbar_button_background_hover,
            "radius": gui_config.profile_toolbar_button_border_radius,
        }

        self._add_btn = self._make_tool_button(
            "profiles/add", "Add profile", self.add_profile_requested.emit, btn_cfg
        )
        self._edit_btn = self._make_tool_button(
            "profiles/edit",
            "Edit match criteria",
            self._emit_edit,
            btn_cfg,
            enabled=False,
        )
        self._delete_btn = self._make_tool_button(
            "profiles/delete",
            "Delete profile",
            self._emit_delete,
            btn_cfg,
            enabled=False,
        )

        toolbar.addWidget(self._add_btn)
        toolbar.addWidget(self._edit_btn)
        toolbar.addWidget(self._delete_btn)
        toolbar.addStretch()

        self._up_btn = self._make_tool_button(
            "profiles/up", "Move up", self._emit_move_up, btn_cfg, enabled=False
        )
        self._down_btn = self._make_tool_button(
            "profiles/down", "Move down", self._emit_move_down, btn_cfg, enabled=False
        )
        toolbar.addWidget(self._up_btn)
        toolbar.addWidget(self._down_btn)

        layout.addLayout(toolbar)

        self.populate_list(active_name)

    # ------------------------------------------------------------------
    #  List population
    # ------------------------------------------------------------------
    def populate_list(self, active_name: Optional[str] = None):
        self._list.blockSignals(True)
        self._list.clear()

        # Default entry
        default_item = QListWidgetItem("  (default)")
        default_item.setData(Qt.UserRole, "")
        default_item.setSizeHint(QSize(0, self._cfg.profile_item_height))
        self._list.addItem(default_item)
        if active_name is None or active_name == "":
            self._list.setCurrentRow(0)

        # Profile entries
        icon = QIcon(
            load_pixmap(
                "profiles/profile",
                self._cfg.profile_item_icon_size,
                self._cfg.profile_item_icon_size,
            )
        )
        for name in self._profiles.keys():
            item = QListWidgetItem(icon, f"  {name}")
            item.setData(Qt.UserRole, name)
            item.setSizeHint(QSize(0, self._cfg.profile_item_height))
            self._list.addItem(item)
            if name == active_name:
                self._list.setCurrentRow(self._list.count() - 1)

        self._list.blockSignals(False)

    def update_profiles(self, profiles: dict) -> None:
        self._profiles = profiles

    # ------------------------------------------------------------------
    #  List styling
    # ------------------------------------------------------------------
    def _list_stylesheet(self) -> str:
        c = self._cfg
        return f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                color: {c.profile_item_text_color};
                background: {c.profile_item_background};
                border-radius: {c.profile_item_border_radius}px;
                padding: 4px 8px;
            }}
            QListWidget::item:hover {{
                background: {c.profile_item_background_hover};
                color: {c.profile_item_text_color_active};
            }}
            QListWidget::item:selected {{
                background: {c.profile_item_background_active};
                color: {c.profile_item_text_color_active};
            }}
        """

    # ------------------------------------------------------------------
    #  Toolbar button factory
    # ------------------------------------------------------------------
    def _make_tool_button(
        self, icon_name: str, tooltip: str, callback, cfg: Dict, enabled: bool = True
    ) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(load_icon(icon_name, cfg["icon_size"]))
        btn.setIconSize(QSize(cfg["icon_size"], cfg["icon_size"]))
        btn.setToolTip(tooltip)
        btn.setFixedSize(cfg["size"], cfg["size"])
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFlat(True)
        btn.setEnabled(enabled)
        btn.clicked.connect(callback)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: {cfg["radius"]}px;
            }}
            QPushButton:hover {{
                background: {cfg["hover_bg"]};
            }}
            QPushButton:disabled {{
                opacity: 0.4;
            }}
        """
        )
        return btn

    # ------------------------------------------------------------------
    #  Selection handling
    # ------------------------------------------------------------------
    def _on_current_item_changed(self, current, previous):
        if current:
            name = current.data(Qt.UserRole)
            self._edit_btn.setEnabled(name != "")
            self._delete_btn.setEnabled(name != "")
            self._up_btn.setEnabled(name != "" and self._list.row(current) > 1)
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
