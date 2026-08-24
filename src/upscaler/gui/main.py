from __future__ import annotations

import copy
import logging
import os
from dataclasses import fields
from typing import Optional, TYPE_CHECKING

from PySide6.QtCore import QEvent, Qt, QTimer, QSettings, QSize, QStandardPaths
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

from .config import (
    ConfigManager,
    GUIConfig,
    GUIPalette,
    PRESETS,
    load_gui_style,
    save_gui_style,
)
from .dialogs import AboutDialog
from .grid import FilterBar, WindowGridScene, WindowGridView
from .helpers import DaemonController, ProfileActions, TrayController, WindowGridManager
from .icons import load_icon
from .sidebars import ProfilesSidebar, SettingsSidebar
from .styles import circular_button_style, tooltip_style
from .utils import find_matching_preset
from .widgets import StyledSplitter
from ..config import apply_overrides, find_matching_profile, parse_config
from ..pipeline import create_pipeline_session
from ..window import activate_window

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..pipeline import PipelineSession
    from ..window import WindowInfo


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
        self._settings = QSettings("linux-rt-upscaler")
        self._config_manager = config_manager
        self._profile_name = profile_name
        self._tray_controller: Optional[TrayController] = None
        self.manual_session: Optional[PipelineSession] = None

        # GUI Palette
        palette = load_gui_style() or PRESETS["Auto"]
        self.gui_config = GUIConfig(palette=palette)
        QApplication.instance().setStyleSheet(tooltip_style(self.gui_config))

        # Icon directory
        self._icons_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.ConfigLocation),
            "linux-rt-upscaler",
            "icons",
        )
        os.makedirs(self._icons_dir, exist_ok=True)

        # Window properties
        self.setWindowTitle(
            self.tr("Real-Time Upscaler", "Localized name of the application")
        )
        self.setMinimumSize(1200, 600)

        # Setup UI
        self._setup_ui()
        self._config_manager.config_changed.connect(self._on_config_changed)
        QApplication.instance().aboutToQuit.connect(self._cleanup_before_quit)

    def _setup_ui(self):
        """Create the entire UI from scratch, using self.gui_config."""
        # ------------------------------------------------------------------
        # Central layout
        # ------------------------------------------------------------------
        central = QWidget()
        central.setStyleSheet(
            f"background-color: {self.gui_config.palette.background};"
        )
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
            0, self.gui_config.filter.vertical_margin, 0, 0
        )
        central_layout.setSpacing(0)

        # Filter bar
        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(0, 0, 0, 0)
        filter_row.setSpacing(4)

        self.filter_bar = FilterBar(self.gui_config)
        filter_row.addWidget(self.filter_bar, 1)

        # System tray toggle
        self.tray_toggle_btn = QToolButton()
        self.tray_toggle_btn.setCheckable(True)
        self.tray_toggle_btn.setChecked(
            self._settings.value("tray/enabled", False, type=bool)
        )
        self.tray_toggle_btn.setIconSize(QSize(36, 36))
        self.tray_toggle_btn.setFixedSize(36, 36)
        self.tray_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.tray_toggle_btn.setToolTip(
            self.tr("Enable/Disable System Tray", "Tray toggle button")
        )
        self.tray_toggle_btn.setAutoRaise(True)
        self.tray_toggle_btn.setStyleSheet(
            circular_button_style(self.gui_config, icon_size=36)
        )
        self.tray_toggle_btn.toggled.connect(self._on_tray_toggled)
        self._update_tray_toggle_icon()
        filter_row.addWidget(self.tray_toggle_btn)
        filter_row.addSpacing(round(self.gui_config.filter.horizontal_margin / 2))

        # About button
        self.about_btn = QToolButton()
        self.about_btn.setIcon(
            load_icon("actions/about", 24, 24, color=self.gui_config.palette.icon)
        )
        self.about_btn.setIconSize(QSize(36, 36))
        self.about_btn.setFixedSize(36, 36)
        self.about_btn.setCursor(Qt.PointingHandCursor)
        self.about_btn.setToolTip(
            self.tr("About Real-Time Upscaler.", "About dialog button")
        )
        self.about_btn.setAutoRaise(True)
        self.about_btn.setStyleSheet(
            circular_button_style(self.gui_config, icon_size=36)
        )
        self.about_btn.clicked.connect(self._show_about_dialog)
        filter_row.addWidget(self.about_btn)
        filter_row.addSpacing(self.gui_config.filter.horizontal_margin)

        # Add filter row
        central_layout.addLayout(filter_row)

        # Add grid
        self.scene = WindowGridScene(self.gui_config)
        self._view = WindowGridView(self.scene, self.gui_config)
        central_layout.addWidget(self._view, stretch=1)

        # ------------------------------------------------------------------
        # Helpers
        # ------------------------------------------------------------------
        self.grid_mgr = WindowGridManager(
            self, self.gui_config, self.scene, self._view, self.filter_bar
        )
        self.profile_act = ProfileActions(
            self, self._config_manager, self.left_sidebar, self._icons_dir
        )
        self.daemon_ctrl = DaemonController(self, self._config_manager, self.grid_mgr)

        # Restore tray state if enabled
        if self.tray_toggle_btn.isChecked():
            QTimer.singleShot(0, lambda: self._on_tray_toggled(True))

        # ------------------------------------------------------------------
        # Right sidebar: Settings
        # ------------------------------------------------------------------
        self.right_sidebar = self._create_right_sidebar()
        self.right_sidebar.save_settings.connect(self._on_save_settings)
        self.right_sidebar.reset_settings.connect(self._on_reset_settings)
        self.right_sidebar.restore_defaults.connect(self._on_restore_defaults)
        self.right_sidebar.style_applied.connect(self._on_style_applied)

        # Splitter
        self.splitter = StyledSplitter(Qt.Horizontal, self.gui_config)
        self.splitter.addWidget(self.left_sidebar)
        self.splitter.addWidget(central_widget)
        self.splitter.addWidget(self.right_sidebar)
        self.splitter.setSizes(
            [self.gui_config.sidebar.width, 400, self.gui_config.sidebar.width]
        )
        self.splitter.setCollapsible(0, True)  # left sidebar can collapse
        self.splitter.setCollapsible(2, True)  # right sidebar can collapse
        self.splitter.splitterMoved.connect(self._on_splitter_moved)
        main_layout.addWidget(self.splitter)

        # Ctrl+F shortcut
        QShortcut(QKeySequence("Ctrl+F"), self, self.filter_bar.set_focus)

        # ------------------------------------------------------------------
        # Signals
        # ------------------------------------------------------------------
        # Grid and filter
        self.filter_bar.filter_changed.connect(self.grid_mgr.populate)
        self.filter_bar.focus_grid_requested.connect(self.grid_mgr.focus_grid)
        self.scene.window_selected.connect(self._on_window_selected)
        self.scene.focus_filter_requested.connect(self.filter_bar.set_focus)
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

        # ------------------------------------------------------------------
        # Background tasks
        # ------------------------------------------------------------------
        QTimer.singleShot(0, self.grid_mgr.start)
        geometry = self._settings.value("mainwindow/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        else:
            self.showMaximized()

        # Activate initial profile if given on command line
        if self._profile_name and self._profile_name in self._config_manager.profiles:
            self._config_manager.set_active_profile(self._profile_name)
            self.left_sidebar.set_active_item(self._profile_name)

        # If daemon is enabled in saved config, start it after the event loop runs
        if self._config_manager.effective_config.daemon:
            QTimer.singleShot(0, self.daemon_ctrl.start)

        # Restore sidebar visibility from previous session
        left_hidden = self._settings.value("gui/left_sidebar_hidden", False)
        right_hidden = self._settings.value("gui/right_sidebar_hidden", False)
        if isinstance(left_hidden, str):
            left_hidden = left_hidden.lower() == "true"
        if isinstance(right_hidden, str):
            right_hidden = right_hidden.lower() == "true"
        if left_hidden or right_hidden:
            sizes = self.splitter.sizes()
            if left_hidden:
                sizes[0] = 0
            if right_hidden:
                sizes[2] = 0
            self.splitter.setSizes(sizes)

    # ------------------------------------------------------------------
    # Pipeline launch
    # ------------------------------------------------------------------
    def _on_window_selected(self, win_info: WindowInfo) -> None:
        """Auto-apply a matching profile, then start a one-shot pipeline."""
        # Daemon mode: always auto-matches
        if self.daemon_ctrl.active:
            self.grid_mgr.stop()
            self.hide()
            activate_window(win_info.handle)
            self.daemon_ctrl.request_switch(win_info)
            return

        # No daemon mode: auto-match only while Global is selected
        if not self._config_manager.active_profile_name:  # Auto-match
            profile_name, _ = find_matching_profile(
                self._config_manager.profiles, win_info
            )
            if profile_name:
                if not self.profile_act.maybe_save_before_switch():
                    return
                self._config_manager.set_active_profile(profile_name)
                self.left_sidebar.set_active_item(profile_name)
                logger.info("Auto-applied profile '%s'.", profile_name)
        else:  # Manual profile
            logger.info(
                "Manual profile applied: '%s'.",
                self._config_manager.active_profile_name,
            )

        QTimer.singleShot(0, lambda: self._start_pipeline(win_info))

    def _on_splitter_moved(self, pos: int, index: int) -> None:
        """Save sidebar visibility based on current splitter sizes."""
        sizes = self.splitter.sizes()
        # If a sidebar's width is less than 10 pixels, consider it hidden.
        left_hidden = sizes[0] < 10
        right_hidden = sizes[2] < 10
        self._settings.setValue("gui/left_sidebar_hidden", left_hidden)
        self._settings.setValue("gui/right_sidebar_hidden", right_hidden)

    def _on_manual_overlay_closed(self) -> None:
        """Called when the overlay of a manual session is closed."""
        if self._settings.value("tray/enabled", False, type=bool):
            self.stop_manual_session()
        else:
            if self.manual_session:
                self.manual_session.shutdown()
                self.manual_session = None
            QApplication.instance().quit()

    def _start_pipeline(self, win_info: WindowInfo) -> None:
        """Create a temporary pipeline session for the given window."""
        logger.info("Starting upscale for: '%s'", win_info.title)
        self.grid_mgr.stop()
        activate_window(win_info.handle)
        self.hide()

        # Copy configuration
        eff_gui_config = copy.deepcopy(self._config_manager.effective_config)
        eff_gui_config.daemon = False
        parse_config(eff_gui_config)

        # Build a clean base config for future follow-focus window matches
        clean_base = copy.deepcopy(self._config_manager.global_baseline)
        apply_overrides(clean_base, self._config_manager.cli_overrides)
        parse_config(clean_base)
        active_profile = self._config_manager.active_profile_name

        # Only pass profiles for auto-matching if Global is selected
        if not active_profile:
            profiles = self._config_manager.profiles
            profile_name_arg = None
        else:
            profiles = {}
            profile_name_arg = active_profile

        # Create pipeline session
        try:
            self.manual_session = create_pipeline_session(
                eff_gui_config,
                win_info,
                base_config=clean_base,
                profiles=profiles,
                profile_name=profile_name_arg,
            )
            self.manual_session.overlay.closed.connect(self._on_manual_overlay_closed)
            self.manual_session.pipeline.finished.connect(
                self._on_manual_pipeline_finished
            )
        except Exception as e:
            logger.exception("Failed to start pipeline")
            QMessageBox.critical(
                None,
                self.tr("Error", "Error starting pipeline"),
                self.tr(
                    "Could not start pipeline:\n{0}", "Error starting pipeline"
                ).format(e),
            )
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
        new_sidebar.style_applied.connect(self._on_style_applied)
        if idx != -1:
            self.splitter.replaceWidget(idx, new_sidebar)
            old.deleteLater()
        else:
            self.splitter.addWidget(new_sidebar)
        new_sidebar.current_tab_index = tab_index
        new_sidebar.on_tab_changed(tab_index)
        self.right_sidebar = new_sidebar

        # Update daemon base config so next match uses current GUI settings
        if self.daemon_ctrl.active:
            merged_base = copy.deepcopy(self._config_manager.global_baseline)
            apply_overrides(merged_base, self._config_manager.cli_overrides)
            parse_config(merged_base)
            self.daemon_ctrl.update_base_config(merged_base)

    def _rebuild_ui(self) -> None:
        # Save state
        tab_index = self.right_sidebar.current_tab_index
        active_profile = self._config_manager.active_profile_name
        filter_text = self.filter_bar.text()
        daemon_was_active = self.daemon_ctrl.active

        # Stop background tasks
        self.grid_mgr.stop()
        self.daemon_ctrl.stop()

        # Remove old central widget
        old_central = self.centralWidget()
        if old_central:
            old_central.deleteLater()

        # Re-initialize the whole UI
        self._setup_ui()

        # Restore state
        self.right_sidebar.current_tab_index = tab_index
        self.right_sidebar.on_tab_changed(tab_index)
        self.filter_bar.set_text(filter_text)
        if active_profile:
            self._config_manager.set_active_profile(active_profile)
            self.left_sidebar.set_active_item(active_profile)
        if daemon_was_active:
            QTimer.singleShot(0, self.daemon_ctrl.start)

    def _on_style_applied(self, new_palette: GUIPalette) -> None:
        """Save the new palette to disk and rebuild the GUI with it."""
        palette_dict = {
            field.name: getattr(new_palette, field.name) for field in fields(GUIPalette)
        }
        preset_name = find_matching_preset(new_palette)
        if preset_name:
            save_gui_style(palette_dict, preset=preset_name)
        else:
            save_gui_style(palette_dict)

        # Build a completely new GUIConfig (same layout constants, new palette)
        new_gui_config = GUIConfig(palette=new_palette)
        self.gui_config = new_gui_config
        QApplication.instance().setStyleSheet(tooltip_style(new_gui_config))

        # Rebuild the entire central area, keeping the active profile / daemon state
        self._rebuild_ui()

    # ------------------------------------------------------------------
    # Save / Reset / Restore
    # ------------------------------------------------------------------
    def _on_save_settings(self) -> None:
        """Persist current configuration to YAML."""
        try:
            self._config_manager.save()
        except Exception as e:
            logger.exception("Save failed")
            QMessageBox.critical(
                self,
                self.tr("Save Error", "Error while saving configuration"),
                self.tr(
                    "Could not save:\n{0}", "Error while saving configuration"
                ).format(e),
            )

    def _on_reset_settings(self) -> None:
        """Revert unsaved changes to the last saved state."""
        self._config_manager.reset_to_saved()

    def _on_restore_defaults(self) -> None:
        """Clear all overrides (global and profile) back to application defaults."""
        self._config_manager.restore_defaults()
        self.left_sidebar.set_active_item(self._config_manager.active_profile_name)

    # ------------------------------------------------------------------
    # Tray
    # ------------------------------------------------------------------
    def _update_tray_toggle_icon(self) -> None:
        """Update the tray toggle button icon based on current state."""
        if self.tray_toggle_btn.isChecked():
            icon_name = "actions/tray_enabled"
        else:
            icon_name = "actions/tray_disabled"
        self.tray_toggle_btn.setIcon(
            load_icon(icon_name, 24, 24, color=self.gui_config.palette.icon)
        )

    def _on_tray_toggled(self, enabled: bool) -> None:
        """Enable or disable the system tray."""
        self._settings.setValue("tray/enabled", enabled)
        self._update_tray_toggle_icon()

        if enabled:
            if not hasattr(self, "_tray_controller") or self._tray_controller is None:
                self._tray_controller = TrayController(self, self.daemon_ctrl, self)
                self._tray_controller.show()
        else:
            if hasattr(self, "_tray_controller") and self._tray_controller is not None:
                self._tray_controller.hide()
                self._tray_controller.deleteLater()
                self._tray_controller = None

    def _on_manual_pipeline_finished(self) -> None:
        if self._settings.value("tray/enabled", False, type=bool):
            self.stop_manual_session()
        else:
            QApplication.instance().quit()

    def stop_manual_session(self) -> None:
        """Stop the active manual session and return to the main window."""
        session = self.manual_session
        self.manual_session = None
        if session:
            session.shutdown()

        self.show()
        self.raise_()
        self.activateWindow()
        QTimer.singleShot(0, self.scene.schedule_relayout)

        self.grid_mgr.start()

    # ------------------------------------------------------------------
    # About dialog
    # ------------------------------------------------------------------
    def _show_about_dialog(self) -> None:
        dlg = AboutDialog(self.gui_config, self)
        dlg.exec()

    # ------------------------------------------------------------------
    # Window close
    # ------------------------------------------------------------------
    def _cleanup_before_quit(self) -> None:
        if self.manual_session is not None:
            self.manual_session.shutdown()
            self.manual_session = None

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            if self._settings.value(
                "tray/enabled", False, type=bool
            ) and self._settings.value("tray/minimize_to_tray", False, type=bool):
                QTimer.singleShot(0, self.hide)
        super().changeEvent(event)

    def closeEvent(self, event) -> None:
        if (
            self._settings.value("tray/enabled", False, type=bool)
            and self._settings.value("tray/close_to_tray", False, type=bool)
            and hasattr(self, "_tray_controller")
            and self._tray_controller is not None
        ):
            self.hide()
            event.ignore()
            return

        self.grid_mgr.stop()
        self.daemon_ctrl.stop()
        self._cleanup_before_quit()
        self._settings.setValue("mainwindow/geometry", self.saveGeometry())
        super().closeEvent(event)
