from __future__ import annotations

import os
from typing import Dict, Optional

from PySide6.QtCore import QEvent, Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..config import GUIConfig
from ..icons import load_icon, load_pixmap
from ..styles import scrollbar_style, sidebar_container_style


class ProfilesSidebar(QWidget):
    """
    Left sidebar panel for managing named profiles.

    Displays a title, a styled list of profiles (plus a default entry),
    and a toolbar for adding, editing, deleting, and reordering.

    Signals
    -------
    profile_selected(str)
        Emitted when the user clicks a profile in the list.
        The payload is the profile name (or "" for the default entry).
    add_profile_requested()
        Emitted when the user clicks the Add button.
    edit_profile_requested(str)
        Emitted after a profile is selected, either by clicking the Edit
        button or by double-clicking the profile entry.
    delete_profile_requested(str)
    move_up_requested(str)
    move_down_requested(str)
    """

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

        # ---- Visual identity ----
        self.setObjectName("sidebar_container")
        self.setStyleSheet(sidebar_container_style(gui_config))
        self.setFixedWidth(gui_config.sidebar_width)

        # ---- Layout ----
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        # Title
        title = QLabel("Profiles")
        title.setStyleSheet(
            f"color: {gui_config.sidebar_section_title_color}; "
            f"font-size: {gui_config.sidebar_section_title_size}px; "
            f"font-weight: bold;"
            f"padding-left: {gui_config.profile_title_left_padding}px;"
        )
        layout.addWidget(title)

        # Header separator line
        layout.addSpacing(8)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {gui_config.profile_header_bottom_border};")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Profile list
        self._list = QListWidget()
        self._list.setMouseTracking(True)
        self._list.viewport().installEventFilter(self)
        self._list.installEventFilter(self)
        self._list.setStyleSheet(self._list_stylesheet())
        self._list.setIconSize(
            QSize(
                gui_config.profile_item_icon_size,
                gui_config.profile_item_icon_size,
            )
        )
        self._list.setSpacing(gui_config.profile_item_spacing)
        self._list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._list.verticalScrollBar().setStyleSheet(scrollbar_style(gui_config))
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._list, stretch=1)

        # Toolbar separator
        toolbar_sep = QFrame()
        toolbar_sep.setFrameShape(QFrame.HLine)
        toolbar_sep.setStyleSheet(f"color: {gui_config.profile_toolbar_top_border};")
        toolbar_sep.setFixedHeight(1)
        layout.addWidget(toolbar_sep)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)

        btn_cfg = {
            "size": gui_config.profile_toolbar_button_size,
            "icon_size": gui_config.profile_toolbar_button_icon_size,
            "hover_bg": gui_config.profile_toolbar_button_background_hover,
            "radius": gui_config.profile_toolbar_button_border_radius,
        }

        btn_cfg = {
            "size": gui_config.profile_toolbar_button_size,
            "icon_size": gui_config.profile_toolbar_button_icon_size,
            "hover_bg": gui_config.profile_toolbar_button_background_hover,
            "radius": gui_config.profile_toolbar_button_border_radius,
        }

        self._add_btn = self._make_tool_button(
            "actions/add",
            "Add profile (Ctrl+N)",
            self.add_profile_requested.emit,
            btn_cfg,
        )
        self._edit_btn = self._make_tool_button(
            "actions/edit",
            "Edit match criteria (Enter/F2)",
            self._emit_edit,
            btn_cfg,
            enabled=False,
        )
        self._delete_btn = self._make_tool_button(
            "actions/delete",
            "Delete profile (Del)",
            self._emit_delete,
            btn_cfg,
            enabled=False,
        )

        self._up_btn = self._make_tool_button(
            "actions/up",
            "Move up (Ctrl+Shift+Up)",
            self._emit_move_up,
            btn_cfg,
            enabled=False,
        )
        self._down_btn = self._make_tool_button(
            "actions/down",
            "Move down (Ctrl+Shift+Down)",
            self._emit_move_down,
            btn_cfg,
            enabled=False,
        )

        toolbar.addWidget(self._add_btn)
        toolbar.addWidget(self._edit_btn)
        toolbar.addWidget(self._delete_btn)
        toolbar.addStretch()
        toolbar.addWidget(self._up_btn)
        toolbar.addWidget(self._down_btn)

        layout.addLayout(toolbar)

        # Populate with the initial data
        self.populate_list(active_name)

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------
    def eventFilter(self, obj, event) -> bool:
        """Handle mouse-hover cursor and keyboard shortcuts."""
        # --- Mouse cursor over list items ---
        if obj is self._list.viewport() and event.type() == QEvent.MouseMove:
            pos = event.position().toPoint()
            item = self._list.itemAt(pos)
            if item is not None:
                self._list.viewport().setCursor(Qt.PointingHandCursor)
            else:
                self._list.viewport().setCursor(Qt.ArrowCursor)
            return False  # don't consume the event

        # --- Keyboard shortcuts when the list widget has focus ---
        if obj is self._list and event.type() == QEvent.KeyPress:
            key = event.key()
            mods = event.modifiers() & Qt.KeyboardModifierMask

            # Current item (may be None)
            item = self._list.currentItem()
            has_profile = item and item.data(Qt.UserRole) != ""

            # Delete, triggers the existing confirmation dialog
            if key == Qt.Key_Delete and has_profile:
                self.delete_profile_requested.emit(item.data(Qt.UserRole))
                return True

            # Edit: Enter / Return or F2 (standard for rename)
            if (
                key == Qt.Key_Return or key == Qt.Key_Enter or key == Qt.Key_F2
            ) and has_profile:
                self.edit_profile_requested.emit(item.data(Qt.UserRole))
                return True

            # Add new profile: Ctrl+N (common shortcut)
            if key == Qt.Key_N and mods == Qt.ControlModifier:
                self.add_profile_requested.emit()
                return True

            # Move up: Ctrl+Shift+Up  (using Shift to avoid conflict with text navigation)
            if (
                key == Qt.Key_Up
                and mods == (Qt.ControlModifier | Qt.ShiftModifier)
                and has_profile
            ):
                self.move_up_requested.emit(item.data(Qt.UserRole))
                return True

            # Move down: Ctrl+Shift+Down
            if (
                key == Qt.Key_Down
                and mods == (Qt.ControlModifier | Qt.ShiftModifier)
                and has_profile
            ):
                self.move_down_requested.emit(item.data(Qt.UserRole))
                return True

        return super().eventFilter(obj, event)

    def populate_list(self, active_name: Optional[str] = None) -> None:
        """
        Clear and rebuild the list from *self._profiles*.

        Use this after adding, deleting, or reordering profiles.
        """
        self._list.blockSignals(True)
        self._list.clear()

        # Default entry (global settings)
        default_icon = QIcon(
            load_pixmap(
                "actions/profile_global",
                self._cfg.profile_item_icon_size,
                self._cfg.profile_item_icon_size,
                color=self._cfg.icon_color,
            )
        )
        default_item = QListWidgetItem(default_icon, "  Global")
        default_item.setData(Qt.UserRole, "")
        default_item.setSizeHint(QSize(0, self._cfg.profile_item_height))
        default_item.setToolTip(
            "When selected, the settings panel on the right edits the global configuration."
        )
        self._list.addItem(default_item)

        # Profile entries
        for name in self._profiles.keys():
            profile_data = self._profiles[name]
            icon_path = profile_data.get("icon", "")
            if icon_path and os.path.isfile(icon_path):
                pix = QPixmap(icon_path).scaled(
                    self._cfg.profile_item_icon_size,
                    self._cfg.profile_item_icon_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                icon = QIcon(pix)
            else:
                icon = QIcon(
                    load_pixmap(
                        "actions/profile",
                        self._cfg.profile_item_icon_size,
                        self._cfg.profile_item_icon_size,
                        color=self._cfg.icon_color,
                    )
                )
            item = QListWidgetItem(icon, f"  {name}")
            item.setData(Qt.UserRole, name)
            item.setSizeHint(QSize(0, self._cfg.profile_item_height))
            if name:
                item.setToolTip(
                    "When selected, the settings panel on the right edits the "
                    f"'{name}' profile overrides."
                )
            self._list.addItem(item)

        # Re-enable signals before selecting the active item
        self._list.blockSignals(False)

        # Now select the correct item - the signal will fire and update toolbar buttons
        if active_name is None or active_name == "":
            self._list.setCurrentRow(0)
        else:
            for i in range(self._list.count()):
                item = self._list.item(i)
                if item is not None and item.data(Qt.UserRole) == active_name:
                    self._list.setCurrentRow(i)
                    break

    def set_active_item(self, name: Optional[str]) -> None:
        """
        Highlight the given profile without rebuilding the list.

        Use this when the list content hasn't changed, it prevents
        unnecessary flicker and preserves the double-click window.
        """
        target = name or ""
        self._list.blockSignals(True)

        for i in range(self._list.count()):
            item = self._list.item(i)
            if item is not None and item.data(Qt.UserRole) == target:
                self._list.setCurrentRow(i)
                break

        self._list.blockSignals(False)

    def update_profiles(self, profiles: dict) -> None:
        """Replace the internal profiles dict (used after reordering)."""
        self._profiles = profiles

    # ------------------------------------------------------------------
    #  Private helpers
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
                border-left: {c.profile_item_indicator_width}px solid transparent;
            }}
            QListWidget::item:hover {{
                background: {c.profile_item_background_hover};
                color: {c.profile_item_text_color_active};
            }}
            QListWidget::item:selected {{
                background: {c.profile_item_background_active};
                color: {c.profile_item_text_color_active};
                border-left: {c.profile_item_indicator_width}px solid {c.profile_item_indicator_color};
            }}
        """

    def _make_tool_button(
        self,
        icon_name: str,
        tooltip: str,
        callback,
        cfg: dict,
        enabled: bool = True,
    ) -> QPushButton:
        """Create a flat, icon-only toolbar button with configurable size."""
        btn = QPushButton()
        btn.setIcon(
            load_icon(
                icon_name,
                cfg["icon_size"],
                cfg["icon_size"],
                color=self._cfg.icon_color,
            )
        )
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
                border-radius: {cfg['radius']}px;
            }}
            QPushButton:hover {{
                background: {cfg['hover_bg']};
            }}
            QPushButton:disabled {{
                opacity: 0.4;
            }}
            """
        )
        return btn

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------

    def _on_current_item_changed(
        self, current: QListWidgetItem | None, previous: QListWidgetItem | None
    ) -> None:
        """
        Update toolbar button states and emit ``profile_selected``.

        The profile is applied immediately; the list is not rebuilt.
        """
        if current is None:
            self._edit_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
            self._up_btn.setEnabled(False)
            self._down_btn.setEnabled(False)
            return

        name = current.data(Qt.UserRole)

        self._edit_btn.setEnabled(name != "")
        self._delete_btn.setEnabled(name != "")
        self._up_btn.setEnabled(name != "" and self._list.row(current) > 1)
        self._down_btn.setEnabled(
            name != "" and self._list.row(current) < self._list.count() - 1
        )

        self.profile_selected.emit(name)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """
        Open the edit dialog for a double-clicked profile.

        The profile was already applied by the initial single click,
        so this only requests editing.
        """
        if item is None:
            return
        name = item.data(Qt.UserRole)
        if not name:  # ignore default
            return
        self.edit_profile_requested.emit(name)

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
