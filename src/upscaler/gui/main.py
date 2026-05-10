from __future__ import annotations

import collections
import copy
import logging
from typing import List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QWidget,
    QMessageBox,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
)

from .config import GUIConfig
from .dialogs import ProfileDialog
from .grid import WindowGridScene, WindowGridView, FilterBar
from .sidebars import ProfilesSidebar, SettingsSidebar
from .widgets import StyledSplitter
from ..config import (
    Config,
    find_profile,
    load_yaml_config,
    move_profile_down,
    move_profile_up,
    parse_config,
    save_yaml_config,
)
from ..pipeline import create_pipeline_session
from ..window import WindowInfo, activate_window, list_windows

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        config: Config,
        config_path: str,
        profile_name: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        self.config = config
        self.config_path = config_path

        self._profile_name = profile_name
        self._active_profile = profile_name if profile_name else None
        self._general_opts, profiles = load_yaml_config(self.config_path)
        self.profiles = collections.OrderedDict(profiles)
        self._profile_order = list(self.profiles.keys())

        self._profile_has_options = (
            bool(self.profiles[profile_name].get("options"))
            if profile_name and profile_name in self.profiles
            else False
        )

        self._baseline_config = self._compute_yaml_baseline()
        self.gui_config = GUIConfig()

        self.setWindowTitle("Linux Real-Time Upscaler")
        self.setMinimumSize(1200, 600)

        # ---- Central widget with horizontal splitter ----
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---- Left sidebar (Profiles) ----
        self.left_sidebar = ProfilesSidebar(
            self.gui_config, self.profiles, self._active_profile
        )
        self.left_sidebar.profile_selected.connect(self._on_profile_selected)
        self.left_sidebar.add_profile_requested.connect(self._on_add_profile)
        self.left_sidebar.edit_profile_requested.connect(self._on_edit_profile)
        self.left_sidebar.delete_profile_requested.connect(self._on_delete_profile)
        self.left_sidebar.move_up_requested.connect(self._on_move_up)
        self.left_sidebar.move_down_requested.connect(self._on_move_down)

        # ---- Central column: filter bar + grid ----
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(
            0, self.gui_config.filter_vertical_margin, 0, 0
        )
        central_layout.setSpacing(0)

        self.filter_bar = FilterBar(self.gui_config)
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.filter_bar.focus_grid_requested.connect(self._focus_grid)
        central_layout.addWidget(self.filter_bar)

        self._scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self._scene, self.gui_config)
        self._scene.window_selected.connect(self._on_window_selected)
        self._scene.focus_filter_requested.connect(self.filter_bar.set_focus)
        self._view.focus_filter_requested.connect(self.filter_bar.set_focus)
        central_layout.addWidget(self._view, stretch=1)

        # ---- Right sidebar (Settings) ----
        self.right_sidebar = SettingsSidebar(
            self.gui_config,
            self.config,
            self._baseline_config,
            profile_active=bool(self._active_profile),
            profile_has_options=self._profile_has_options,
        )
        self.right_sidebar.save_settings.connect(self._on_save_settings)
        self.right_sidebar.reset_settings.connect(self._on_reset_settings)
        self.right_sidebar.restore_defaults.connect(self._on_restore_defaults)

        # ---- Assemble splitter ----
        self.splitter = StyledSplitter(Qt.Horizontal, self.gui_config)
        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(central_widget)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes(
            [
                self.gui_config.sidebar_width,
                400,
                self.gui_config.sidebar_width,
            ]
        )

        main_layout.addWidget(self.splitter)

        # Ctrl+F shortcut
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # Auto-refresh timer
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start(self.gui_config.auto_refresh_ms)

        # State
        self._selected_win_info: Optional[WindowInfo] = None
        self._session = None
        self._own_handle: Optional[int] = None

        self.showMaximized()
        QTimer.singleShot(0, self._initial_populate)

    # ------------------------------------------------------------------
    #  Window list management
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

    # ------------------------------------------------------------------
    #  Config helpers
    # ------------------------------------------------------------------
    def _compute_yaml_baseline(self) -> Config:
        """Build baseline Config from cached YAML options + active profile."""
        baseline = Config()

        # Apply cached general options
        for k, v in self._general_opts.items():
            if hasattr(baseline, k) and k not in ("log_level", "log_file"):
                setattr(baseline, k, v)

        # If a profile is active, its saved options take precedence
        if self._active_profile and self._active_profile in self.profiles:
            profile_data = self.profiles[self._active_profile]
            if profile_data:
                opts = profile_data.get("options", {})
                for k, v in opts.items():
                    if hasattr(baseline, k) and k not in ("log_level", "log_file"):
                        setattr(baseline, k, v)

        # CLI profile (not yet active), only needed at startup
        elif self._profile_name:
            profile_data = find_profile(self.profiles, self._profile_name)
            if profile_data:
                opts = profile_data.get("options", {})
                for k, v in opts.items():
                    if hasattr(baseline, k) and k not in ("log_level", "log_file"):
                        setattr(baseline, k, v)

        parse_config(baseline)
        return baseline

    # ------------------------------------------------------------------
    #  Profile helpers
    # ------------------------------------------------------------------
    def _apply_profile(self, name: Optional[str]) -> None:
        """
        Replace the live config with the chosen profile's options, inheriting
        any missing fields from the top-level YAML (general) options.
        """
        self._active_profile = name

        # Base = general (top-level) YAML options, not system defaults
        self.config = Config()
        for k, v in self._general_opts.items():
            if hasattr(self.config, k) and k not in ("log_level", "log_file"):
                setattr(self.config, k, v)

        if name:
            # Layer the profile's explicit options on top
            opts = self.profiles[name].get("options", {})
            for k, v in opts.items():
                if hasattr(self.config, k):
                    setattr(self.config, k, v)

        parse_config(self.config)

        if name:
            opts = self.profiles[name].get("options", {})
            self._profile_has_options = bool(opts)
        else:
            self._profile_has_options = False

        self._baseline_config = self._compute_yaml_baseline()
        self._recreate_right_sidebar()
        self.left_sidebar.set_active_item(name)

    def _save_profiles_to_disk(self):
        """Write the current profile list to YAML, leaving general options untouched."""
        try:
            general_opts, _ = load_yaml_config(self.config_path)
            save_yaml_config(general_opts, dict(self.profiles), self.config_path)
        except Exception:
            logger.exception("Failed to auto-save profiles")

    def _maybe_save_before_switch(self) -> bool:
        """Return False if user cancels."""
        if self.right_sidebar.is_dirty():
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

    def _safe_apply_profile(self, name: str):
        try:
            self._apply_profile(name if name != "" else None)
        except Exception:
            logger.exception("Failed to apply profile")
            QMessageBox.critical(
                self,
                "Error",
                "An unexpected error occurred while switching profiles.",
            )

    def _on_profile_selected(self, name: str):
        # Skip if the profile is already active
        active = self._active_profile if self._active_profile else ""
        if active == name:
            return

        if not self._maybe_save_before_switch():
            return

        QTimer.singleShot(0, lambda: self._safe_apply_profile(name))

    def _on_add_profile(self):
        try:
            dlg = ProfileDialog(parent=self)
            if dlg.exec() == QDialog.Accepted:
                name = dlg.profile_name()
                match = dlg.match_criteria()
                self.profiles[name] = {"match": match, "options": {}}
                self._profile_order.append(name)
                self.left_sidebar.populate_list(active_name=name)
                self._save_profiles_to_disk()
                QTimer.singleShot(0, lambda n=name: self._safe_apply_profile(n))
        except Exception:
            logger.exception("Failed to add profile")
            QMessageBox.critical(self, "Error", "Could not add profile.")

    def _on_edit_profile(self, name: str):
        try:
            current_match = self.profiles[name].get("match", {})
            dlg = ProfileDialog(profile_name=name, match=current_match, parent=self)
            if dlg.exec() == QDialog.Accepted:
                new_name = dlg.profile_name()
                new_match = dlg.match_criteria()
                if new_name != name:
                    data = self.profiles.pop(name)
                    self.profiles[new_name] = data
                    self._profile_order[self._profile_order.index(name)] = new_name
                self.profiles[new_name]["match"] = new_match
                self.left_sidebar.populate_list(active_name=new_name)
                self._save_profiles_to_disk()
        except Exception:
            logger.exception("Failed to edit profile")
            QMessageBox.critical(self, "Error", "Could not edit profile.")

    def _on_delete_profile(self, name: str):
        try:
            reply = QMessageBox.question(
                self,
                "Delete profile",
                f"Delete profile '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                del self.profiles[name]
                self._profile_order.remove(name)
                self.left_sidebar.populate_list(active_name=None)
                self._save_profiles_to_disk()
                if self._active_profile == name:
                    QTimer.singleShot(0, lambda: self._safe_apply_profile(""))
        except Exception:
            logger.exception("Failed to delete profile")
            QMessageBox.critical(self, "Error", "Could not delete profile.")

    def _on_move_up(self, name: str):
        try:
            self.profiles = move_profile_up(self.profiles, name)
            self._profile_order = list(self.profiles.keys())
            self.left_sidebar.update_profiles(self.profiles)
            self.left_sidebar.populate_list(active_name=name)
            self._save_profiles_to_disk()
        except Exception:
            logger.exception("Failed to move profile up")
            QMessageBox.critical(self, "Error", "Could not reorder profiles.")

    def _on_move_down(self, name: str):
        try:
            self.profiles = move_profile_down(self.profiles, name)
            self._profile_order = list(self.profiles.keys())
            self.left_sidebar.update_profiles(self.profiles)
            self.left_sidebar.populate_list(active_name=name)
            self._save_profiles_to_disk()
        except Exception:
            logger.exception("Failed to move profile down")
            QMessageBox.critical(self, "Error", "Could not reorder profiles.")

    # ------------------------------------------------------------------
    #  Focus helpers
    # ------------------------------------------------------------------
    def _focus_grid(self) -> None:
        self._view.setFocus()
        self._scene.focus_first_tile()

    # ------------------------------------------------------------------
    #  Sidebar helpers
    # ------------------------------------------------------------------
    def _recreate_right_sidebar(self) -> None:
        old = self.right_sidebar
        tab_index = old.current_tab_index
        new = SettingsSidebar(
            self.gui_config,
            self.config,
            self._baseline_config,
            profile_active=bool(self._active_profile),
            profile_has_options=self._profile_has_options,
        )
        new.save_settings.connect(self._on_save_settings)
        new.reset_settings.connect(self._on_reset_settings)
        new.restore_defaults.connect(self._on_restore_defaults)

        idx = self.splitter.indexOf(old)
        if idx != -1:
            self.splitter.replaceWidget(idx, new)
            old.deleteLater()
        else:
            self.splitter.addWidget(new)
        self.right_sidebar = new

        new.current_tab_index = tab_index

    # ------------------------------------------------------------------
    #  Slots
    # ------------------------------------------------------------------
    def _on_filter_changed(self, text: str) -> None:
        self._populate_grid(text)

    def _on_window_selected(self, win_info: WindowInfo) -> None:
        self._selected_win_info = win_info
        QTimer.singleShot(0, self._start_pipeline)

    def _on_save_settings(self):
        """Save the current config to the YAML file."""
        config_dict = self.config.to_dict(diff_only=True)
        try:
            if self._active_profile:
                # Merge options into the active profile
                self.profiles[self._active_profile]["options"] = config_dict
                # Keep general options as they are on disk
                general_opts, _ = load_yaml_config(self.config_path)
                save_yaml_config(general_opts, dict(self.profiles), self.config_path)
                self._profile_has_options = bool(
                    self.profiles[self._active_profile].get("options")
                )
            else:
                save_yaml_config(config_dict, dict(self.profiles), self.config_path)
                self._profile_has_options = False

            self._baseline_config = copy.deepcopy(self.config)
            QTimer.singleShot(0, self._recreate_right_sidebar)
        except Exception as e:
            logger.exception("Failed to save configuration")
            QMessageBox.critical(self, "Save Error", f"Could not save:\n{e}")

    def _on_reset_settings(self):
        """Revert all settings back to what was loaded from the file."""
        logger.info("Resetting settings to saved state.")
        self.config = copy.deepcopy(self._baseline_config)
        self._recreate_right_sidebar()

    def _on_restore_defaults(self):
        if self._active_profile:
            # Capture the current baseline *before* clearing options
            old_baseline = copy.deepcopy(self._baseline_config)

            # Clear the profile’s explicit options (in memory only)
            self.profiles[self._active_profile]["options"] = {}

            # Build the live config from top‑level YAML only (no profile overrides)
            self.config = Config()
            for k, v in self._general_opts.items():
                if hasattr(self.config, k) and k not in ("log_level", "log_file"):
                    setattr(self.config, k, v)
            parse_config(self.config)

            # Use the old baseline so the sidebar sees a difference
            self._baseline_config = old_baseline
            self._profile_has_options = False

            self._recreate_right_sidebar()
            self.left_sidebar.set_active_item(self._active_profile)
            logger.info("Profile overrides cleared.")
        else:
            # Global config: true system defaults
            self.config = Config()
            parse_config(self.config)
            self._recreate_right_sidebar()
            logger.info("Restoring system defaults.")

    # ------------------------------------------------------------------
    #  Pipeline launch
    # ------------------------------------------------------------------
    def _start_pipeline(self) -> None:
        if self._selected_win_info is None:
            return

        win_info = self._selected_win_info
        logger.info("Starting upscale for: %s", win_info.title)

        self._refresh_timer.stop()
        activate_window(win_info.handle)
        self.hide()
        self._scene.clear_all()

        try:
            self._session = create_pipeline_session(self.config, win_info)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    def closeEvent(self, event) -> None:
        self._refresh_timer.stop()
        self._scene.clear_all()
        super().closeEvent(event)
