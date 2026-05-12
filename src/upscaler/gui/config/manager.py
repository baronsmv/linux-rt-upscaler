from __future__ import annotations

import copy
import logging
from collections import OrderedDict
from dataclasses import fields
from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

from ...config import (
    Config,
    apply_overrides,
    load_yaml_config,
    move_profile_down,
    move_profile_up,
    parse_config,
    save_yaml_config,
)

logger = logging.getLogger(__name__)


class ConfigManager(QObject):
    """
    Manages the entire configuration lifecycle for the GUI.

    Signals
    -------
    config_changed ()
        Emitted whenever `persistent_config` is modified (by loading a profile,
        restoring defaults, etc.).  The sidebars can connect to this signal to
        refresh their displayed values and dirty‑state highlighting.

    profile_list_changed ()
        Emitted when profiles are added, removed, renamed, or reordered, or
        when a profile’s icon path is changed.
    """

    config_changed = Signal()
    profile_list_changed = Signal()

    # ------------------------------------------------------------------
    #  Initialisation
    # ------------------------------------------------------------------
    def __init__(
        self,
        config_path: str,
        cli_overrides: Optional[Dict[str, Any]] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        """
        Parameters
        ----------
        config_path : str
            Path to the YAML configuration file (may not exist yet).
        cli_overrides : dict or None
            Command‑line overrides as returned by :func:`config.args.parse_args`.
            These are **never** saved to disk; they are applied on top of
            everything else to form the effective runtime configuration.
        """
        super().__init__(parent)
        self._config_path = config_path
        self._cli_overrides: Dict[str, Any] = dict(cli_overrides or {})

        # ---- Load frozen data from disk -----------------------------------
        self._general_opts: Dict[str, Any] = {}
        self._profiles: OrderedDict[str, Dict] = OrderedDict()
        self._load_from_disk()

        # ---- Compute the immutable layering bases ------------------------
        self._system_defaults = Config()  # all fields at their Dataclass defaults
        parse_config(self._system_defaults)

        # Global baseline: system defaults + top‑level YAML (NO profile, NO CLI)
        self._global_baseline = self._build_global_baseline()

        # ---- Live state --------------------------------------------------
        self._active_profile_name: Optional[str] = None

        # The *persistent* config is what the user edits in the sidebar.
        # It contains system defaults + YAML general + active profile options.
        # CLI overrides are intentionally excluded.
        self._persistent_config = copy.deepcopy(self._global_baseline)

        # The *effective* config is what the pipeline actually uses.
        # It adds CLI overrides on top of the persistent one.
        self._effective_config = self._compute_effective()

        # Snapshot of the persistent config at the last successful save.
        # Used for dirty‑state detection and "Reset" functionality.
        self._saved_persistent_config = copy.deepcopy(self._persistent_config)

    # ------------------------------------------------------------------
    #  Public properties
    # ------------------------------------------------------------------
    @property
    def persistent_config(self) -> Config:
        """
        The configuration that the user can modify through the GUI sidebars.
        It **does not** contain CLI overrides, so saving it back to disk
        will never leak transient CLI options.
        """
        return self._persistent_config

    @property
    def effective_config(self) -> Config:
        """
        The configuration that should be used by the upscaling pipeline.
        It is built as: ``persistent_config + CLI overrides``.
        """
        return self._effective_config

    @property
    def profiles(self) -> OrderedDict[str, Dict]:
        """Read‑only view of the current profiles (name -> {match, options, icon})."""
        return OrderedDict(self._profiles)

    @property
    def active_profile_name(self) -> Optional[str]:
        """Name of the currently active profile, or None for the global settings."""
        return self._active_profile_name

    @property
    def global_baseline(self) -> Config:
        """
        Baseline for highlighting: system defaults + top‑level YAML only.
        This is useful for the sidebar to show which options are overridden
        by the active profile.
        """
        return self._global_baseline

    # ------------------------------------------------------------------
    #  Profile management
    # ------------------------------------------------------------------
    def set_active_profile(self, name: Optional[str]) -> None:
        """
        Switch to the given profile (or to global settings when *name* is None).

        The persistent config is rebuilt: start from `_global_baseline`,
        then apply the profile's saved options (if any).  CLI overrides
        are kept separate and applied to the effective config only.
        """
        self._active_profile_name = name

        if name is not None:
            profile_data = self._profiles.get(name, {})
            opts = profile_data.get("options", {})
            self._persistent_config = copy.deepcopy(self._global_baseline)
            apply_overrides(self._persistent_config, opts)
            parse_config(self._persistent_config)

        else:
            self._persistent_config = copy.deepcopy(self._global_baseline)

        self._effective_config = self._compute_effective()
        self.config_changed.emit()

    def add_profile(self, name: str, match: Dict[str, Any]) -> None:
        """
        Add a new profile with the given match criteria and empty options.

        Raises `ValueError` if a profile with *name* already exists.
        """
        if name in self._profiles:
            raise ValueError(f"Profile '{name}' already exists")

        self._profiles[name] = {"match": match, "options": {}}
        self.profile_list_changed.emit()
        logger.debug(f"Added profile '{name}'")

    def delete_profile(self, name: str) -> None:
        """Remove the profile *name*.  Does nothing if the profile doesn't exist."""
        if name in self._profiles:
            del self._profiles[name]
            self.profile_list_changed.emit()
            logger.debug(f"Deleted profile '{name}'")

    def rename_profile(self, old_name: str, new_name: str) -> None:
        """
        Rename a profile, preserving its position in the order.

        Raises `ValueError` if *new_name* already exists.
        """
        if new_name in self._profiles:
            raise ValueError(f"Profile '{new_name}' already exists")
        if old_name not in self._profiles:
            raise ValueError(f"Profile '{old_name}' not found")

        # Rebuild OrderedDict to keep order
        new_profiles = OrderedDict()
        for key, val in self._profiles.items():
            if key == old_name:
                new_profiles[new_name] = val
            else:
                new_profiles[key] = val

        self._profiles = new_profiles
        self.profile_list_changed.emit()
        logger.debug(f"Renamed profile '{old_name}' -> '{new_name}'")

    def move_profile_up(self, name: str) -> None:
        """Reorder the profile one position up (does nothing if already first)."""
        self._profiles = move_profile_up(self._profiles, name)
        self.profile_list_changed.emit()

    def move_profile_down(self, name: str) -> None:
        """Reorder the profile one position down."""
        self._profiles = move_profile_down(self._profiles, name)
        self.profile_list_changed.emit()

    def update_profile_match(self, name: str, match: Dict[str, Any]) -> None:
        """
        Update the match criteria of an existing profile.
        The profile's options are left unchanged.
        """
        if name not in self._profiles:
            raise ValueError(f"Profile '{name}' not found")
        self._profiles[name]["match"] = match
        self.profile_list_changed.emit()

    # ------------------------------------------------------------------
    #  Profile icon management (file I/O is handled by the caller)
    # ------------------------------------------------------------------
    def set_profile_icon(self, name: str, icon_path: str) -> None:
        """
        Store an icon path for *name* and immediately save to disk.

        The caller is responsible for having already saved the image file
        at *icon_path*.
        """
        if name not in self._profiles:
            raise ValueError(f"Profile '{name}' not found")
        self._profiles[name]["icon"] = icon_path
        save_yaml_config(self._general_opts, dict(self._profiles), self._config_path)
        self.profile_list_changed.emit()

    def remove_profile_icon(self, name: str) -> None:
        """Remove the icon entry for *name* (does not delete the file)."""
        if name in self._profiles and "icon" in self._profiles[name]:
            del self._profiles[name]["icon"]
            save_yaml_config(
                self._general_opts, dict(self._profiles), self._config_path
            )
            self.profile_list_changed.emit()

    def update_profile_icon_path(self, new_name: str, new_path: str) -> None:
        """Update the icon path after a profile rename."""
        if new_name not in self._profiles:
            raise ValueError(f"Profile '{new_name}' not found")
        if "icon" in self._profiles[new_name]:
            self._profiles[new_name]["icon"] = new_path
            save_yaml_config(
                self._general_opts, dict(self._profiles), self._config_path
            )
            self.profile_list_changed.emit()

    # ------------------------------------------------------------------
    #  Saving, resetting, restoring
    # ------------------------------------------------------------------
    def save(self) -> None:
        """
        Write the current persistent configuration to the YAML file.

        - If a profile is active, only the options that differ from the
          global baseline are saved inside the profile dictionary.
        - If no profile is active, the top‑level YAML section is updated
          with the diff from system defaults.
        """
        if self._active_profile_name is not None:
            # Save only profile‑specific overrides (diff from global baseline)
            new_options = self._profile_options_diff()
            self._profiles[self._active_profile_name]["options"] = new_options

            # Always write the full file: general opts unchanged + updated profiles
            save_yaml_config(
                self._general_opts, dict(self._profiles), self._config_path
            )
            logger.debug(
                "Saved profile '%s' with %d options",
                self._active_profile_name,
                len(new_options),
            )

        else:
            # Global settings – top‑level YAML
            cfg_dict = self._persistent_config.to_dict(diff_only=True)
            save_yaml_config(cfg_dict, dict(self._profiles), self._config_path)

            # Reload the general opts from what we just wrote to keep them in sync
            self._general_opts, _ = load_yaml_config(self._config_path)

            # Rebuild the global baseline because general opts may have changed
            self._global_baseline = self._build_global_baseline()
            logger.debug("Saved global settings")

        # Update the saved snapshot so dirty‑state is cleared
        self._saved_persistent_config = copy.deepcopy(self._persistent_config)
        self.config_changed.emit()

    def reset_to_saved(self) -> None:
        """
        Discard any unsaved changes and revert the persistent config to the
        last saved state.
        """
        self._persistent_config = copy.deepcopy(self._saved_persistent_config)
        self._effective_config = self._compute_effective()
        self.config_changed.emit()

    def restore_defaults(self) -> None:
        """
        Clear all overrides:

        - For the active profile: remove all its options.  The persistent
          config falls back to the global baseline (system + top‑level YAML).
        - For global settings: restore the true system defaults (a fresh
          ``Config()``), ignoring YAML overrides.

        CLI overrides are **not** affected; they remain in the effective config.
        """
        if self._active_profile_name is not None:
            # Clear profile options – profile goes to "no overrides" state
            self._profiles[self._active_profile_name]["options"] = {}
            self._persistent_config = copy.deepcopy(self._global_baseline)

        else:
            # Restore system defaults (completely fresh Config)
            self._persistent_config = copy.deepcopy(self._system_defaults)

        parse_config(self._persistent_config)
        self._effective_config = self._compute_effective()
        self.config_changed.emit()

    def is_dirty(self) -> bool:
        """
        Return `True` if the persistent config has unsaved changes compared
        to the last saved state.
        """
        return self._configs_differ(
            self._persistent_config, self._saved_persistent_config
        )

    # ------------------------------------------------------------------
    #  Private helpers
    # ------------------------------------------------------------------
    def _load_from_disk(self) -> None:
        """Load general options and profiles from the YAML file, handling errors."""
        try:
            self._general_opts, raw_profiles = load_yaml_config(self._config_path)
            # Preserve insertion order (YAML already provides OrderedDict via safe_load)
            self._profiles = OrderedDict(raw_profiles)

        except Exception:
            logger.exception("Failed to load config from %s", self._config_path)
            self._general_opts = {}
            self._profiles = OrderedDict()

    def _build_global_baseline(self) -> Config:
        """
        System defaults + top‑level YAML only.

        This is the starting point for any profile: it includes everything
        from the “general” section of the config file.  Profile options and
        CLI overrides are **not** included.
        """
        base = copy.deepcopy(self._system_defaults)
        apply_overrides(base, self._general_opts)
        parse_config(base)
        return base

    def _compute_effective(self) -> Config:
        """Build the runtime config: persistent + CLI overrides."""
        cfg = copy.deepcopy(self._persistent_config)
        apply_overrides(cfg, self._cli_overrides)
        parse_config(cfg)
        return cfg

    def _profile_options_diff(self) -> Dict[str, Any]:
        """
        Return only the options that the active profile overrides compared
        to the global baseline.
        """
        diff = {}
        for field in fields(self._persistent_config):
            name = field.name
            if name in ("log_level", "log_file", "program", "config_file"):
                continue
            value = getattr(self._persistent_config, name)
            baseline = getattr(self._global_baseline, name)
            if value != baseline:
                diff[name] = value
        return diff

    @staticmethod
    def _configs_differ(a: Config, b: Config) -> bool:
        """Compare two Config objects field by field, ignoring internal fields."""
        for field in fields(a):
            name = field.name
            if name in ("log_level", "log_file", "program", "config_file"):
                continue
            if getattr(a, name) != getattr(b, name):
                return True

        return False
