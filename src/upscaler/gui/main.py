from __future__ import annotations

import logging
import os
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QSettings, QSize, QStandardPaths
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .config import ConfigManager, GUIConfig, presets
from .dialogs import AboutDialog
from .grid import FilterBar, WindowGridScene, WindowGridView
from .helpers import DaemonController, ProfileActions, WindowGridManager
from .icons import load_icon
from .sidebars import ProfilesSidebar, SettingsSidebar
from .styles import about_button_style, tooltip_style
from .widgets import StyledSplitter
from ..config import find_matching_profile, parse_config
from ..pipeline import create_pipeline_session
from ..utils import system_color_scheme
from ..window import WindowInfo, activate_window

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Primary GUI window. Coordinates three major components:

    * **Profile sidebar**  - list and management of profiles.
    * **Window grid**      - live previews of X11 application windows.
    * **Settings sidebar** - editing of global and per-profile options.
    """

    def __init__(
        self,
        config_manager: ConfigManager,
        profile_name: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._config_manager = config_manager
        self._manual_session = None  # used for non-daemon launches

        # Visual configuration
        scheme = system_color_scheme()
        self.gui_config = GUIConfig(
            palette=presets.DARK if scheme == "dark" else presets.LIGHT
        )
        QApplication.instance().setStyleSheet(tooltip_style(self.gui_config))

        # Icon directory
        self._icons_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.ConfigLocation),
            "linux-rt-upscaler",
            "icons",
        )
        os.makedirs(self._icons_dir, exist_ok=True)

        # Window properties
        self.setWindowTitle("Real-Time Upscaler")
        self.setMinimumSize(1200, 600)

        # ------------------------------------------------------------------
        # Central layout
        # ------------------------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ------------------------------------------------------------------
        # Left sidebar: Profiles
        # ------------------------------------------------------------------
        self.left_sidebar = ProfilesSidebar(
            self.gui_config,
            self._config_manager.profiles,
            self._config_manager.active_profile_name,
        )

        # ------------------------------------------------------------------
        # Central column
        # ------------------------------------------------------------------
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(
            0, self.gui_config.filter_vertical_margin, 0, 0
        )
        central_layout.setSpacing(0)

        # Filter bar
        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(0, 0, 0, 0)
        filter_row.setSpacing(4)

        self.filter_bar = FilterBar(self.gui_config)
        filter_row.addWidget(self.filter_bar, 1)

        # About button
        self.about_btn = QToolButton()
        self.about_btn.setIcon(
            load_icon("actions/about", 20, 20, color=self.gui_config.palette.text_dim)
        )
        self.about_btn.setIconSize(QSize(20, 20))
        self.about_btn.setFixedSize(32, 32)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setToolTip("About Real-Time Upscaler")
        self.about_btn.setAutoRaise(True)
        self.about_btn.setStyleSheet(about_button_style(self.gui_config))
        self.about_btn.clicked.connect(self._show_about_dialog)
        filter_row.addWidget(self.about_btn)
        filter_row.addSpacing(self.gui_config.filter_horizontal_margin)

        # Add filter row
        central_layout.addLayout(filter_row)

        # Add grid
        self._scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self._scene, self.gui_config)
        central_layout.addWidget(self._view, stretch=1)

        # ------------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------------
        self.grid_mgr = WindowGridManager(
            self, self.gui_config, self._scene, self._view, self.filter_bar
        )
        self.profile_act = ProfileActions(
            self, self._config_manager, self.left_sidebar, self._icons_dir
        )
        self.daemon_ctrl = DaemonController(self, self._config_manager, self.grid_mgr)

        # ------------------------------------------------------------------
        # Right sidebar: Settings
        # ------------------------------------------------------------------
        self.right_sidebar = self._create_right_sidebar()
        self.right_sidebar.save_settings.connect(self._on_save_settings)
        self.right_sidebar.reset_settings.connect(self._on_reset_settings)
        self.right_sidebar.restore_defaults.connect(self._on_restore_defaults)

        # Splitter
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

        # ------------------------------------------------------------------
        # Signals
        # ------------------------------------------------------------------
        # Grid and filter
        self.filter_bar.filter_changed.connect(self.grid_mgr.populate)
        self.filter_bar.focus_grid_requested.connect(self.grid_mgr.focus_grid)
        self._scene.window_selected.connect(self._on_window_selected)
        self._scene.focus_filter_requested.connect(self.filter_bar.set_focus)
        self._view.focus_filter_requested.connect(self.filter_bar.set_focus)

        # Profile
        self.left_sidebar.profile_selected.connect(self.profile_act.select_profile)
        self.left_sidebar.add_profile_requested.connect(self.profile_act.add_profile)
        self.left_sidebar.edit_profile_requested.connect(self.profile_act.edit_profile)
        self.left_sidebar.delete_profile_requested.connect(
            self.profile_act.delete_profile
        )
        self.left_sidebar.move_up_requested.connect(self.profile_act.move_up)
        self.left_sidebar.move_down_requested.connect(self.profile_act.move_down)

        # Daemon
        self.right_sidebar.daemon_toggled.connect(self.daemon_ctrl.toggle)
        self._config_manager.config_changed.connect(self._on_config_changed)

        # ------------------------------------------------------------------
        # Background tasks
        # ------------------------------------------------------------------
        self.grid_mgr.start()
        self._settings = QSettings("linux-rt-upscaler")
        geometry = self._settings.value("mainwindow/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.showMaximized()

        # Activate initial profile if given on command line
        if profile_name and profile_name in self._config_manager.profiles:
            self._config_manager.set_active_profile(profile_name)
            self.left_sidebar.set_active_item(profile_name)

        # If daemon is enabled in saved config, start it after the event loop runs
        if self._config_manager.effective_config.daemon:
            QTimer.singleShot(0, self.daemon_ctrl.start)

    # ------------------------------------------------------------------
    # Pipeline launch
    # ------------------------------------------------------------------
    def _on_window_selected(self, win_info: WindowInfo) -> None:
        """Auto-apply a matching profile, then start a one-shot pipeline."""
        profile_name, _ = find_matching_profile(
            self._config_manager.profiles, win_info.title
        )
        if profile_name and profile_name != self._config_manager.active_profile_name:
            if not self.profile_act.maybe_save_before_switch():
                return
            self._config_manager.set_active_profile(profile_name)
            self.left_sidebar.set_active_item(profile_name)
            logger.info("Auto-applied profile '%s'.", profile_name)

        QTimer.singleShot(0, lambda: self._start_pipeline(win_info))

    def _on_manual_overlay_closed(self) -> None:
        if self._manual_session:
            self._manual_session.pipeline.stop()
            self._manual_session = None
        QApplication.instance().quit()

    def _start_pipeline(self, win_info: WindowInfo) -> None:
        """Create a temporary pipeline session for the given window."""
        logger.info("Starting upscale for: '%s'", win_info.title)
        self.grid_mgr.stop()
        activate_window(win_info.handle)
        self.hide()
        parse_config(self._config_manager.effective_config)

        try:
            self._manual_session = create_pipeline_session(
                self._config_manager.effective_config,
                win_info,
            )
            self._manual_session.overlay.closed.connect(self._on_manual_overlay_closed)
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(None, "Error", f"Could not start pipeline:\n{e}")
            QApplication.instance().quit()

    # ------------------------------------------------------------------
    # Right sidebar
    # ------------------------------------------------------------------
    def _create_right_sidebar(self) -> SettingsSidebar:
        """Build a SettingsSidebar reflecting the current config state."""
        sidebar = SettingsSidebar(
            self.gui_config,
            self._config_manager.persistent_config,
            baseline_config=self._config_manager.saved_persistent_config,
            profile_active=self._config_manager.active_profile_name is not None,
            profile_has_options=self._active_profile_has_options(),
        )
        # Daemon checkbox is inside the sidebar
        sidebar.daemon_toggled.connect(self.daemon_ctrl.toggle)
        return sidebar

    def _active_profile_has_options(self) -> bool:
        """Return True if the active profile contains any option overrides."""
        name = self._config_manager.active_profile_name
        if not name:
            return False
        profile_data = self._config_manager.profiles.get(name, {})
        return bool(profile_data.get("options", {}))

    def _on_config_changed(self) -> None:
        """
        Called whenever the persistent config (global or profile) is modified.
        Recreates the right sidebar to show current values and pushes the
        latest effective config to the running daemon pipeline, if any.
        """
        # Rebuild the sidebar in place
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

        # Update daemon base config so next match uses current GUI settings
        if self.daemon_ctrl.active:
            self.daemon_ctrl.update_base_config(self._config_manager.effective_config)

    # ------------------------------------------------------------------
    # Save / Reset / Restore
    # ------------------------------------------------------------------
    def _on_save_settings(self) -> None:
        """Persist current configuration to YAML."""
        try:
            self._config_manager.save()
        except Exception as e:
            logger.exception("Save failed")
            QMessageBox.critical(self, "Save Error", f"Could not save:\n{e}")

    def _on_reset_settings(self) -> None:
        """Revert unsaved changes to the last saved state."""
        self._config_manager.reset_to_saved()

    def _on_restore_defaults(self) -> None:
        """Clear all overrides (global and profile) back to application defaults."""
        self._config_manager.restore_defaults()
        self.left_sidebar.set_active_item(self._config_manager.active_profile_name)

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------
    def _show_about_dialog(self) -> None:
        dlg = AboutDialog(self.gui_config, self)
        dlg.exec()

    # ------------------------------------------------------------------
    # Window close
    # ------------------------------------------------------------------
    def closeEvent(self, event) -> None:
        """Stop all background activity before closing."""
        self.grid_mgr.stop()
        self.daemon_ctrl.stop()
        self._settings.setValue("mainwindow/geometry", self.saveGeometry())
        super().closeEvent(event)
