from __future__ import annotations

from typing import TYPE_CHECKING

from ..common import SettingsTab

if TYPE_CHECKING:
    from ...config import GUIConfig
    from ....config import Config


class GeneralTab(SettingsTab):
    def __init__(self, gui_config: GUIConfig, config: Config, parent=None) -> None:
        self._config = config
        super().__init__(gui_config, "General", parent)

    def _build_content(self) -> None:
        # ---- Model & double upscale ----
        self._add_section("Upscaling Model")
        self._model_combo = self._add_combo(
            "Model",
            [
                "fast",
                "faster",
                "veryfast",
                "4x32",
                "4x24",
                "4x16",
                "4x12",
                "3x12",
                "8x32",
            ],
            self._config.model,
            self._on_model_changed,
        )
        self._double_cb = self._add_cb(
            "Double Upscale (4x)",
            self._config.double_upscale,
            self._on_double_changed,
        )

        # ---- Output Geometry ----
        self._add_section("Output Geometry")
        self._geom_combo = self._add_combo(
            "Scaling mode",
            ["fit", "stretch", "cover"],
            self._config.output_geometry,
            self._on_geometry_changed,
        )

        # ---- Focus Tracking ----
        self._add_section("Focus Tracking")
        self._follow_focus_cb = self._add_cb(
            "Follow Focus", self._config.follow_focus, self._on_follow_focus
        )
        self._pause_focus_loss_cb = self._add_cb(
            "Pause on Focus Loss",
            self._config.pause_on_focus_loss,
            self._on_pause_focus_loss,
        )

    def _on_model_changed(self, text: str) -> None:
        self._config.model = text
        self.config_changed.emit()

    def _on_double_changed(self, state: int) -> None:
        self._config.double_upscale = bool(state)
        self.config_changed.emit()

    def _on_geometry_changed(self, text: str) -> None:
        self._config.output_geometry = text
        self.config_changed.emit()

    def _on_follow_focus(self, state):
        self._config.follow_focus = bool(state)
        self.config_changed.emit()

    def _on_pause_focus_loss(self, state):
        self._config.pause_on_focus_loss = bool(state)
        self.config_changed.emit()
