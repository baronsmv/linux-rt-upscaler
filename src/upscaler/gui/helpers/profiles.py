from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QMessageBox, QDialog

from ..dialogs import ProfileDialog

if TYPE_CHECKING:
    from ..config import ConfigManager
    from ..main import MainWindow
    from ..sidebars import ProfilesSidebar

logger = logging.getLogger(__name__)


class ProfileActions:
    """
    Encapsulates every action that modifies the profile list:
    add, edit, delete, move up/down, rename, icon management.

    Parameters
    ----------
    main_window: MainWindow
        Parent for dialogs.
    config_manager: ConfigManager
        The manager holding profiles and persistent config.
    left_sidebar: ProfilesSidebar
        The sidebar that displays the profile list.
    icons_dir: str
        Directory where profile icon PNGs are stored.
    """

    def __init__(
        self,
        main_window: MainWindow,
        config_manager: ConfigManager,
        left_sidebar: ProfilesSidebar,
        icons_dir: str,
    ) -> None:
        self._main_window = main_window
        self._config_manager = config_manager
        self._sidebar = left_sidebar
        self._icons_dir = icons_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def maybe_save_before_switch(self) -> bool:
        """Return False if the user cancels an unsaved‑changes dialog."""
        if self._config_manager.is_dirty():
            reply = QMessageBox.question(
                self._main_window,
                "Unsaved changes",
                "Save changes before switching profile?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            )
            if reply == QMessageBox.Save:
                self._config_manager.save()
                return True
            elif reply == QMessageBox.Discard:
                return True
            else:
                return False
        return True

    def select_profile(self, name: str) -> None:
        """Activate a different profile (from sidebar click)."""
        if name == (self._config_manager.active_profile_name or ""):
            return
        if not self.maybe_save_before_switch():
            return
        self._config_manager.set_active_profile(name)
        self._sidebar.set_active_item(name)

    def add_profile(self) -> None:
        """Open the Add Profile dialog and process the result."""
        try:
            dlg = ProfileDialog(
                self._main_window.gui_config,
                profiles=self._config_manager.profiles,
                parent=self._main_window,
            )
            if dlg.exec() == QDialog.Accepted:
                name = dlg.profile_name()
                match = dlg.match_criteria()
                self._config_manager.add_profile(name, match)

                icon = dlg.get_captured_icon()
                if icon:
                    self._save_icon(name, icon)

                self._config_manager.set_active_profile(name)
                self._sidebar.update_profiles(self._config_manager.profiles)
                self._sidebar.populate_list(active_name=name)
        except Exception:
            logger.exception("Failed to add profile")
            QMessageBox.critical(self._main_window, "Error", "Could not add profile.")

    def edit_profile(self, name: str) -> None:
        """Open the Edit Profile dialog for an existing profile."""
        try:
            current_match = self._config_manager.profiles[name].get("match", {})
            dlg = ProfileDialog(
                self._main_window.gui_config,
                profile_name=name,
                match=current_match,
                profiles=self._config_manager.profiles,
                parent=self._main_window,
            )
            if dlg.exec() == QDialog.Accepted:
                new_name = dlg.profile_name()
                new_match = dlg.match_criteria()

                if new_name != name:
                    if new_name in self._config_manager.profiles:
                        QMessageBox.warning(
                            self._main_window,
                            "Duplicate name",
                            f"A profile named '{new_name}' already exists.",
                        )
                        return
                    self._config_manager.rename_profile(name, new_name)
                    self._rename_icon_file(name, new_name)
                    self._config_manager.update_profile_match(new_name, new_match)
                else:
                    self._config_manager.update_profile_match(name, new_match)

                icon = dlg.get_captured_icon()
                if icon:
                    self._save_icon(new_name if new_name != name else name, icon)

                if self._config_manager.active_profile_name == new_name:
                    self._sidebar.set_active_item(new_name)

                self._sidebar.update_profiles(self._config_manager.profiles)
                self._sidebar.populate_list(active_name=new_name)
        except Exception:
            logger.exception("Failed to edit profile")
            QMessageBox.critical(self._main_window, "Error", "Could not edit profile.")

    def delete_profile(self, name: str) -> None:
        """Delete a profile after confirmation."""
        try:
            reply = QMessageBox.question(
                self._main_window,
                "Delete profile",
                f"Delete profile '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._remove_icon_file(name)
                self._config_manager.delete_profile(name)
                self._sidebar.update_profiles(self._config_manager.profiles)
                self._sidebar.populate_list(active_name=None)
                if self._config_manager.active_profile_name == name:
                    self._config_manager.set_active_profile(None)
        except Exception:
            logger.exception("Failed to delete profile")
            QMessageBox.critical(
                self._main_window, "Error", "Could not delete profile."
            )

    def move_up(self, name: str) -> None:
        try:
            self._config_manager.move_profile_up(name)
            self._sidebar.update_profiles(self._config_manager.profiles)
            self._sidebar.populate_list(active_name=name)
        except Exception:
            logger.exception("Failed to move profile up")
            QMessageBox.critical(
                self._main_window, "Error", "Could not reorder profiles."
            )

    def move_down(self, name: str) -> None:
        try:
            self._config_manager.move_profile_down(name)
            self._sidebar.update_profiles(self._config_manager.profiles)
            self._sidebar.populate_list(active_name=name)
        except Exception:
            logger.exception("Failed to move profile down")
            QMessageBox.critical(
                self._main_window, "Error", "Could not reorder profiles."
            )

    # ------------------------------------------------------------------
    # Icon file helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _sanitize(name: str) -> str:
        return re.sub(r"[^\w\-_\. ]", "_", name).strip()

    def _icon_path(self, name: str) -> str:
        return os.path.join(self._icons_dir, self._sanitize(name) + ".png")

    def _save_icon(self, profile_name: str, image: QImage) -> None:
        path = self._icon_path(profile_name)
        image.save(path, "PNG")
        self._config_manager.set_profile_icon(profile_name, path)

    def _remove_icon_file(self, profile_name: str) -> None:
        path = self._icon_path(profile_name)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass
        self._config_manager.remove_profile_icon(profile_name)

    def _rename_icon_file(self, old_name: str, new_name: str) -> None:
        old_path = self._icon_path(old_name)
        new_path = self._icon_path(new_name)
        if os.path.isfile(old_path):
            try:
                os.rename(old_path, new_path)
                self._config_manager.update_profile_icon_path(new_name, new_path)
            except OSError:
                self._config_manager.remove_profile_icon(old_name)
                try:
                    os.remove(old_path)
                except OSError:
                    pass
        else:
            self._config_manager.remove_profile_icon(new_name)
