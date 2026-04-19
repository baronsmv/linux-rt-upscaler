import logging
import os
import threading
from datetime import datetime
from queue import Empty, Queue
from typing import TYPE_CHECKING, Tuple

from PIL import Image
from PySide6.QtCore import Q_ARG, QMetaObject, Qt

from ..config import OUTPUT_GEOMETRIES, UPSCALING_MODELS
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .pipeline import Pipeline

logger = logging.getLogger(__name__)

OSD_DURATION = 1.5


def _download_and_save(
    texture: Texture2D, width: int, height: int, pipeline: "Pipeline"
) -> None:
    """Download texture data and save as PNG. Runs in a background thread."""
    success = False
    try:
        data = texture.download()
        img = Image.frombytes("RGBA", (width, height), data, "raw", "BGRA")
        img = img.convert("RGB")

        save_dir = os.path.expanduser(pipeline.config.screenshot_dir)
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"Screenshot_{timestamp}.png")
        img.save(filename)
        logger.info(f"Screenshot saved to {filename}")
        success = True
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}", exc_info=True)

    message = "Screenshot saved" if success else "Screenshot failed"
    pipeline.osd_queue.put((message, OSD_DURATION))


class PipelineController:
    """
    Handles external commands for the Pipeline in a thread‑safe manner.

    Commands include:
        - Toggling overlay visibility.
        - Switching upscaling models.
        - Cycling output geometry modes.
        - Taking screenshots.
    """

    def __init__(
        self,
        pipeline: "Pipeline",
        available_models: Tuple[str, ...] = UPSCALING_MODELS,
        available_geometries: Tuple[str, ...] = OUTPUT_GEOMETRIES,
    ) -> None:
        self._pipeline = pipeline
        self._available_models = available_models
        self._available_geometries = available_geometries

        # Thread‑safe request queues
        self._model_switch_queue: Queue[bool] = Queue()  # True = next, False = previous
        self._geometry_switch_queue: Queue[bool] = Queue()
        self._screenshot_requested = False

        self._current_model_index = 0
        self._current_geometry_index = 0

    # ----------------------------------------------------------------------
    # Public API (called from main thread)
    # ----------------------------------------------------------------------
    def toggle_overlay(self) -> None:
        """Show/hide the overlay window and pause/resume processing."""
        if self._pipeline.overlay.isVisible():
            self._pipeline.overlay.hide()
            self._pipeline.user_paused = True
        else:
            self._pipeline.overlay.show()
            self._pipeline.user_paused = False

    def switch_model(self, next_model: bool = True) -> None:
        """
        Request a model switch.

        Args:
            next_model: If True, switch to next model; if False, switch to previous.
        """
        self._model_switch_queue.put(next_model)

    def switch_geometry(self) -> None:
        """Request a geometry mode cycle (next mode)."""
        self._geometry_switch_queue.put(True)

    def take_screenshot(self) -> None:
        """Request a screenshot."""
        self._screenshot_requested = True

    # ----------------------------------------------------------------------
    # Request processing (called from pipeline thread)
    # ----------------------------------------------------------------------
    def process_requests(self) -> None:
        """Consume and apply any pending requests."""
        # Model switch
        try:
            next_model = self._model_switch_queue.get_nowait()
            self._apply_model_switch(next_model)
        except Empty:
            pass

        # Screenshot
        if self._screenshot_requested:
            self._save_screenshot()
            self._screenshot_requested = False

        # Geometry cycle
        try:
            self._geometry_switch_queue.get_nowait()
            self._apply_geometry_cycle()
        except Empty:
            pass

    # ----------------------------------------------------------------------
    # Internal implementation
    # ----------------------------------------------------------------------
    def _apply_model_switch(self, next_model: bool) -> None:
        """Switch to the next or previous model."""
        total = len(self._available_models)
        if total == 0:
            return

        new_idx = (
            (self._current_model_index + 1) % total
            if next_model
            else (self._current_model_index - 1) % total
        )
        new_model = self._available_models[new_idx]

        old_model = self._pipeline.config.model
        logger.info(f"Switching model from {old_model} to {new_model}")
        self._current_model_index = new_idx
        self._pipeline.config.model = new_model

        # Delegate the actual upscaler recreation to the pipeline
        self._pipeline.recreate_upscaler()

        # Update Lanczos source texture
        self._pipeline.presenter.set_source_texture(
            self._pipeline.upscaler_mgr.full_upscaler.output
        )

        self._pipeline.clear_frame_queue()
        self._pipeline.osd.show(f"Model: {new_model}", OSD_DURATION)

    def _apply_geometry_cycle(self) -> None:
        """Cycle to the next output geometry mode."""
        total = len(self._available_geometries)
        if total == 0:
            return

        new_idx = (self._current_geometry_index + 1) % total
        new_geometry = self._available_geometries[new_idx]

        old_geometry = self._pipeline.config.output_geometry
        logger.info(f"Switching output geometry from {old_geometry} to {new_geometry}")
        self._current_geometry_index = new_idx
        self._pipeline.config.output_geometry = new_geometry
        self._pipeline.scale_mode = new_geometry

        # Update overlay scale mode via queued connection
        QMetaObject.invokeMethod(
            self._pipeline.overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, new_geometry),
        )

        self._pipeline.update_content_dimensions()
        self._pipeline.osd.show(f"Geometry: {new_geometry}", OSD_DURATION)

    def _save_screenshot(self) -> None:
        """Capture the current upscaled texture and offload saving to a background thread."""
        try:
            # Get the source texture from the presenter (the fully upscaled image)
            src_tex = self._pipeline.presenter.lanczos.source_texture
            if src_tex is None:
                logger.warning("No source texture available for screenshot")
                self._pipeline.osd_queue.put(("Screenshot failed", OSD_DURATION))
                return

            temp_tex = Texture2D(src_tex.width, src_tex.height)
            src_tex.copy_to(temp_tex)

            threading.Thread(
                target=_download_and_save,
                args=(
                    temp_tex,
                    src_tex.width,
                    src_tex.height,
                    self._pipeline,
                ),
                daemon=True,
                name="ScreenshotSaver",
            ).start()
        except Exception as e:
            logger.error(f"Failed to initiate screenshot: {e}", exc_info=True)
            self._pipeline.osd_queue.put(("Screenshot failed", OSD_DURATION))

    # ----------------------------------------------------------------------
    # Initialisation helpers
    # ----------------------------------------------------------------------
    def set_initial_model_index(self, model_name: str) -> None:
        """Set the current model index based on the config value."""
        if model_name in self._available_models:
            self._current_model_index = self._available_models.index(model_name)

    def set_initial_geometry_index(self, geometry_name: str) -> None:
        """Set the current geometry index based on the config value."""
        if geometry_name in self._available_geometries:
            self._current_geometry_index = self._available_geometries.index(
                geometry_name
            )
