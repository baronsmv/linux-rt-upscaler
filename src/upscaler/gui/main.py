from __future__ import annotations

import logging
import os
import re
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer, QStandardPaths, QSize
from PySide6.QtGui import QKeySequence, QImage, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QToolButton,
)

from .config import ConfigManager, GUIConfig, presets
from .dialogs import ProfileDialog
from .grid import FilterBar, WindowGridScene, WindowGridView
from .icons import load_icon
from .sidebars import ProfilesSidebar, SettingsSidebar
from .widgets import StyledSplitter
from ..config import find_matching_profile, get_version
from ..pipeline import create_pipeline_session
from ..utils import system_color_scheme
from ..window import WindowInfo, activate_window, list_windows

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    The primary GUI window for the upscaler.

    This class coordinates the three panes (profile list, window grid,
    settings sidebar) and delegates all configuration management to a
    :class:`ConfigManager`.  It no longer manipulates config objects
    directly – all layering, saving, and restoring is handled by the
    manager.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        profile_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._config_manager = config_manager

        # ---- GUI visual config (theme, dimensions) -----------------------
        scheme = system_color_scheme()
        self.gui_config = GUIConfig(
            palette=presets.DARK if scheme == "dark" else presets.LIGHT
        )

        # ---- Icons directory (for profile icons) -------------------------
        self._icons_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.ConfigLocation),
            "linux-rt-upscaler",
            "icons",
        )
        os.makedirs(self._icons_dir, exist_ok=True)

        # ---- UI setup ----------------------------------------------------
        self.setWindowTitle("Linux Real-Time Upscaler")
        self.setMinimumSize(1200, 600)

        # Central layout: splitter with three panels
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left sidebar – Profiles
        self.left_sidebar = ProfilesSidebar(
            self.gui_config,
            self._config_manager.profiles,
            self._config_manager.active_profile_name,
        )
        self.left_sidebar.profile_selected.connect(self._on_profile_selected)
        self.left_sidebar.add_profile_requested.connect(self._on_add_profile)
        self.left_sidebar.edit_profile_requested.connect(self._on_edit_profile)
        self.left_sidebar.delete_profile_requested.connect(self._on_delete_profile)
        self.left_sidebar.move_up_requested.connect(self._on_move_up)
        self.left_sidebar.move_down_requested.connect(self._on_move_down)

        # Central column – filter bar + window grid
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(
            0, self.gui_config.filter_vertical_margin, 0, 0
        )
        central_layout.setSpacing(0)

        # ---- Filter bar + About button in a horizontal row ----
        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(0, 0, 0, 0)
        filter_row.setSpacing(4)

        self.filter_bar = FilterBar(self.gui_config)
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.filter_bar.focus_grid_requested.connect(self._focus_grid)
        filter_row.addWidget(self.filter_bar, 1)

        # ---- About button ----
        self.about_btn = QToolButton()
        self.about_btn.setIcon(
            load_icon("actions/about", 20, 20, color=self.gui_config.palette.text_dim)
        )
        self.about_btn.setIconSize(QSize(20, 20))
        self.about_btn.setFixedSize(32, 32)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setToolTip("About Linux Real‑Time Upscaler")
        self.about_btn.setAutoRaise(True)
        self.about_btn.setStyleSheet(
            f"""
            QToolButton {{
                border-radius: 16px;
                border: none;
                background: transparent;
            }}
            QToolButton:hover {{
                background: {self.gui_config.palette.bg_surface_hover};
            }}
            """
        )
        self.about_btn.clicked.connect(self._show_about)
        filter_row.addWidget(self.about_btn)

        central_layout.addLayout(filter_row)

        self._scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self._scene, self.gui_config)
        self._scene.window_selected.connect(self._on_window_selected)
        self._scene.focus_filter_requested.connect(self.filter_bar.set_focus)
        self._view.focus_filter_requested.connect(self.filter_bar.set_focus)
        central_layout.addWidget(self._view, stretch=1)

        # Right sidebar – Settings
        self.right_sidebar = self._create_right_sidebar()
        self.right_sidebar.save_settings.connect(self._on_save_settings)
        self.right_sidebar.reset_settings.connect(self._on_reset_settings)
        self.right_sidebar.restore_defaults.connect(self._on_restore_defaults)

        # ---- Splitter ----------------------------------------------------
        self.splitter = StyledSplitter(Qt.Horizontal, self.gui_config)
        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(central_widget)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes(
            [self.gui_config.sidebar_width, 400, self.gui_config.sidebar_width]
        )
        main_layout.addWidget(self.splitter)

        # Ctrl+F shortcut
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # Connect to config changes to refresh the right sidebar
        self._config_manager.config_changed.connect(self._on_config_changed)

        # ---- Auto-refresh timer ------------------------------------------
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(self.gui_config.auto_refresh_ms)

        # ---- Pipeline state ----------------------------------------------
        self._selected_win_info: Optional[WindowInfo] = None
        self._session = None
        self._own_handle: Optional[int] = None

        # Activate a profile if one was provided at startup
        if profile_name and profile_name in self._config_manager.profiles:
            self._config_manager.set_active_profile(profile_name)
            self.left_sidebar.set_active_item(profile_name)

        self.showMaximized()
        QTimer.singleShot(0, self._initial_populate)

    # ------------------------------------------------------------------
    #  Window list helpers
    # ------------------------------------------------------------------
    def _initial_populate(self) -> None:
        self._own_handle = int(self.winId())
        self._populate_grid()

    def _populate_grid(self, filter_text: str = "") -> None:
        try:
            all_windows: List[WindowInfo] = list_windows()
        except Exception:
            logger.exception("Failed to enumerate windows")
            QMessageBox.warning(self, "Error", "Could not enumerate windows.")
            return

        own = self._own_handle
        filtered = []
        text_lower = filter_text.lower().strip()
        for win in all_windows:
            if own is not None and win.handle == own:
                continue
            if not win.title.strip():
                continue
            if text_lower and text_lower not in win.title.lower():
                continue
            filtered.append(win)

        self._scene.set_windows(filtered)

    def _auto_refresh(self) -> None:
        self._populate_grid(self.filter_bar.text())

    def _focus_grid(self) -> None:
        self._view.setFocus()
        self._scene.focus_first_tile()

    # ------------------------------------------------------------------
    #  Config helpers
    # ------------------------------------------------------------------
    def _create_right_sidebar(self) -> SettingsSidebar:
        """
        Build a new SettingsSidebar using the manager's current state.
        The sidebar is given the global baseline for highlighting and
        the persistent config for editing.
        """
        sidebar = SettingsSidebar(
            self.gui_config,
            self._config_manager.persistent_config,
            baseline_config=self._config_manager.saved_persistent_config,
            profile_active=self._config_manager.active_profile_name is not None,
            profile_has_options=self._active_profile_has_options(),
        )
        return sidebar

    def _active_profile_has_options(self) -> bool:
        """Return True if the active profile has at least one option override."""
        name = self._config_manager.active_profile_name
        if not name:
            return False
        profile_data = self._config_manager.profiles.get(name, {})
        return bool(profile_data.get("options", {}))

    def _on_config_changed(self) -> None:
        """Called whenever the manager's persistent config changes."""
        self._recreate_right_sidebar()

    def _recreate_right_sidebar(self) -> None:
        """Replace the right sidebar with a fresh one and restore the active tab."""
        old = self.right_sidebar
        tab_index = old.current_tab_index
        idx = self.splitter.indexOf(old)
        new_sidebar = self._create_right_sidebar()
        new_sidebar.save_settings.connect(self._on_save_settings)
        new_sidebar.reset_settings.connect(self._on_reset_settings)
        new_sidebar.restore_defaults.connect(self._on_restore_defaults)
        if idx != -1:
            self.splitter.replaceWidget(idx, new_sidebar)
            old.deleteLater()
        else:
            self.splitter.addWidget(new_sidebar)
        new_sidebar.current_tab_index = tab_index
        self.right_sidebar = new_sidebar

    # ------------------------------------------------------------------
    #  Profile slots
    # ------------------------------------------------------------------
    def _maybe_save_before_switch(self) -> bool:
        """Return False if user cancels."""
        if self._config_manager.is_dirty():
            reply = QMessageBox.question(
                self,
                "Unsaved changes",
                "Save changes before switching profile?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self._on_save_settings()
                return True
            elif reply == QMessageBox.Discard:
                return True
            else:
                return False
        return True

    def _on_profile_selected(self, name: str) -> None:
        # Already active?
        if name == (self._config_manager.active_profile_name or ""):
            return

        if not self._maybe_save_before_switch():
            return  # user canceled

        self._config_manager.set_active_profile(name)
        self.left_sidebar.set_active_item(name)
        # Sidebar is refreshed automatically by config_changed signal

    def _on_add_profile(self) -> None:
        try:
            dlg = ProfileDialog(
                self.gui_config, profiles=self._config_manager.profiles, parent=self
            )
            if dlg.exec() == QDialog.Accepted:
                name = dlg.profile_name()
                match = dlg.match_criteria()
                self._config_manager.add_profile(name, match)

                # Handle icon
                captured = dlg.get_captured_icon()
                if captured:
                    self._save_profile_icon(name, captured)

                # Activate the new profile immediately (avoids double signal)
                self._config_manager.set_active_profile(name)
                # Sync sidebar dict, then show
                self.left_sidebar.update_profiles(self._config_manager.profiles)
                self.left_sidebar.populate_list(active_name=name)

        except Exception:
            logger.exception("Failed to add profile")
            QMessageBox.critical(self, "Error", "Could not add profile.")

    def _on_edit_profile(self, name: str) -> None:
        try:
            current_match = self._config_manager.profiles[name].get("match", {})
            dlg = ProfileDialog(
                self.gui_config,
                profile_name=name,
                match=current_match,
                profiles=self._config_manager.profiles,
                parent=self,
            )
            if dlg.exec() == QDialog.Accepted:
                new_name = dlg.profile_name()
                new_match = dlg.match_criteria()

                # Rename if needed
                if new_name != name:
                    if new_name in self._config_manager.profiles:
                        QMessageBox.warning(
                            self,
                            "Duplicate name",
                            f"A profile named '{new_name}' already exists.",
                        )
                        return
                    self._config_manager.rename_profile(name, new_name)
                    self._rename_profile_icon_file(name, new_name)
                    self._config_manager.update_profile_match(new_name, new_match)
                else:
                    self._config_manager.update_profile_match(name, new_match)

                # Update icon if captured
                captured = dlg.get_captured_icon()
                if captured:
                    self._save_profile_icon(
                        new_name if new_name != name else name, captured
                    )

                # If the active profile was renamed, update the sidebar highlight
                if self._config_manager.active_profile_name == new_name:
                    self.left_sidebar.set_active_item(new_name)

                # Sync and refresh
                self.left_sidebar.update_profiles(self._config_manager.profiles)
                self.left_sidebar.populate_list(active_name=new_name)

        except Exception:
            logger.exception("Failed to edit profile")
            QMessageBox.critical(self, "Error", "Could not edit profile.")

    def _on_delete_profile(self, name: str) -> None:
        try:
            reply = QMessageBox.question(
                self,
                "Delete profile",
                f"Delete profile '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._remove_profile_icon_file(name)
                self._config_manager.delete_profile(name)
                self.left_sidebar.update_profiles(self._config_manager.profiles)
                self.left_sidebar.populate_list(active_name=None)
                if self._config_manager.active_profile_name == name:
                    self._config_manager.set_active_profile(None)
        except Exception:
            logger.exception("Failed to delete profile")
            QMessageBox.critical(self, "Error", "Could not delete profile.")

    def _on_move_up(self, name: str) -> None:
        try:
            self._config_manager.move_profile_up(name)
            self.left_sidebar.update_profiles(self._config_manager.profiles)
            self.left_sidebar.populate_list(active_name=name)
        except Exception:
            logger.exception("Failed to move profile up")
            QMessageBox.critical(self, "Error", "Could not reorder profiles.")

    def _on_move_down(self, name: str) -> None:
        try:
            self._config_manager.move_profile_down(name)
            self.left_sidebar.update_profiles(self._config_manager.profiles)
            self.left_sidebar.populate_list(active_name=name)
        except Exception:
            logger.exception("Failed to move profile down")
            QMessageBox.critical(self, "Error", "Could not reorder profiles.")

    # ------------------------------------------------------------------
    #  Save / Reset / Restore (delegated)
    # ------------------------------------------------------------------
    def _on_save_settings(self) -> None:
        """Save the current persistent config via the manager."""
        try:
            self._config_manager.save()
        except Exception as e:
            logger.exception("Save failed")
            QMessageBox.critical(self, "Save Error", f"Could not save:\n{e}")

    def _on_reset_settings(self) -> None:
        """Revert to the last saved state."""
        self._config_manager.reset_to_saved()

    def _on_restore_defaults(self) -> None:
        """Clear all overrides (profile or global)."""
        self._config_manager.restore_defaults()
        # Update left sidebar in case the active profile lost its options
        self.left_sidebar.set_active_item(self._config_manager.active_profile_name)

    # ------------------------------------------------------------------
    #  Icon file helpers (file I/O stays in MainWindow, manager tracks path)
    # ------------------------------------------------------------------
    @staticmethod
    def _sanitize_profile_name(name: str) -> str:
        return re.sub(r"[^\w\-_\. ]", "_", name).strip()

    def _profile_icon_path(self, name: str) -> str:
        return os.path.join(self._icons_dir, self._sanitize_profile_name(name) + ".png")

    def _save_profile_icon(self, profile_name: str, image: QImage) -> None:
        path = self._profile_icon_path(profile_name)
        image.save(path, "PNG")
        self._config_manager.set_profile_icon(profile_name, path)

    def _remove_profile_icon_file(self, profile_name: str) -> None:
        # Remove the icon file from disk
        try:
            path = self._profile_icon_path(profile_name)
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass
        self._config_manager.remove_profile_icon(profile_name)

    def _rename_profile_icon_file(self, old_name: str, new_name: str) -> None:
        """Rename the icon file on disk and update the profile entry."""
        old_path = self._profile_icon_path(old_name)
        new_path = self._profile_icon_path(new_name)
        if os.path.isfile(old_path):
            try:
                os.rename(old_path, new_path)
                self._config_manager.update_profile_icon_path(new_name, new_path)
            except OSError:
                # Fallback: remove old reference, let user re‑capture
                self._config_manager.remove_profile_icon(old_name)
                try:
                    os.remove(old_path)
                except OSError:
                    pass
        else:
            # No file to rename – ensure the entry is clean
            self._config_manager.remove_profile_icon(new_name)

    # ------------------------------------------------------------------
    #  Window selection -> pipeline launch
    # ------------------------------------------------------------------
    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text)

    def _on_window_selected(self, win_info: WindowInfo) -> None:
        self._selected_win_info = win_info

        profile_name, _ = find_matching_profile(
            self._config_manager.profiles, win_info.title
        )
        if profile_name and profile_name != self._config_manager.active_profile_name:
            if not self._maybe_save_before_switch():
                return
            self._config_manager.set_active_profile(profile_name)
            self.left_sidebar.set_active_item(profile_name)
            logger.info(
                "Auto‑applied profile '%s' for window '%s'",
                profile_name,
                win_info.title,
            )

        QTimer.singleShot(0, self._start_pipeline)

    def _start_pipeline(self) -> None:
        if self._selected_win_info is None:
            return

        logger.info("Starting upscale for: %s", self._selected_win_info.title)
        self._refresh_timer.stop()
        activate_window(self._selected_win_info.handle)
        self.hide()
        self._scene.clear_all()

        # The pipeline uses the effective config (includes CLI overrides)
        try:
            self._session = create_pipeline_session(
                self._config_manager.effective_config,
                self._selected_win_info,
            )
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    def _show_about(self) -> None:
        """Display the About dialog."""
        cfg = self.gui_config  # shorthand

        dlg = QDialog(self)
        dlg.setWindowTitle("About")
        dlg.setFixedSize(480, 400)

        # Overall dialog styling
        dlg.setStyleSheet(
            f"""
            QDialog {{
                background-color: {cfg.dialog_background};
                border: 1px solid {cfg.dialog_groupbox_border};
                border-radius: 12px;
            }}
            """
        )

        main_layout = QVBoxLayout(dlg)
        main_layout.setContentsMargins(32, 28, 32, 24)
        main_layout.setSpacing(0)

        # ---- App icon ----
        icon_label = QLabel()
        icon_pixmap = load_icon(
            "app/app", 96, 96, color=cfg.palette.accent_blue
        ).pixmap(96, 96)
        icon_label.setPixmap(icon_pixmap)
        icon_label.setFixedSize(96, 96)

        icon_container = QVBoxLayout()
        icon_container.addStretch()
        icon_container.addWidget(icon_label, alignment=Qt.AlignCenter)
        icon_container.addStretch()
        main_layout.addLayout(icon_container)

        # ---- App name (big, bold) ----
        name_label = QLabel("Linux Real‑Time Upscaler")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(
            f"color: {cfg.palette.text_primary}; "
            "font-size: 24px; "
            "font-weight: bold; "
            "margin-top: 16px;"
        )
        main_layout.addWidget(name_label)

        # ---- Version (subtle) ----
        version_label = QLabel(f"Version {get_version()}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(
            f"color: {cfg.palette.text_secondary}; "
            "font-size: 20px; "
            "margin-top: 4px;"
        )
        main_layout.addWidget(version_label)

        # ---- Tagline / description ----
        desc_label = QLabel(
            "A real‑time AI upscaler for any application window on GNU/Linux."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(
            f"color: {cfg.palette.text_dim}; "
            "font-size: 18px; "
            "margin-top: 18px; "
            "padding: 0 24px;"
        )
        main_layout.addWidget(desc_label)

        # ---- GitHub link ----
        link_label = QLabel()
        link_label.setText(
            "<a href='https://github.com/baronsmv/linux-rt-upscaler' "
            "style='color: #4a9eff; text-decoration: none;'>"
            "GitHub</a>"
        )
        link_label.setOpenExternalLinks(True)
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setCursor(Qt.PointingHandCursor)
        link_label.setStyleSheet("font-size: 18px; margin-top: 10px;")
        main_layout.addWidget(link_label)

        # Push remaining space above the button
        main_layout.addStretch()

        # ---- Close button ----
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(dlg.accept)
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {cfg.dialog_button_background};
                border: 1px solid {cfg.dialog_button_border};
                border-radius: 8px;
                padding: 6px 18px;
                color: {cfg.dialog_text_color};
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {cfg.dialog_button_hover_background};
                border-color: {cfg.dialog_button_hover_border_color};
            }}
            """
        )
        btn_container = QVBoxLayout()
        btn_container.addWidget(close_btn, alignment=Qt.AlignCenter)
        main_layout.addLayout(btn_container)

        dlg.exec()

    def closeEvent(self, event) -> None:
        self._refresh_timer.stop()
        self._scene.clear_all()
        super().closeEvent(event)
