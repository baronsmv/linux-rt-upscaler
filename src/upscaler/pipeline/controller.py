import logging
import os
import threading
from datetime import datetime
from queue import Empty, Queue
from typing import TYPE_CHECKING, Tuple

from PIL import Image
from PySide6.QtCore import Q_ARG, QMetaObject, Qt

from ..config import OUTPUT_GEOMETRIES, UPSCALING_MODELS

if TYPE_CHECKING:
    from .pipeline import Pipeline
    from ..vulkan import Texture2D

logger = logging.getLogger(__name__)

# Duration (in seconds) for on‑screen display messages.
OSD_DURATION = 1.5


class PipelineController:
    """
    Handles external commands for the Pipeline in a thread‑safe manner.

    Commands are queued and processed in the pipeline thread via
    `process_requests()`. This ensures that Vulkan operations and state
    changes occur on the correct thread.

    Attributes:
        _pipeline (Pipeline): Reference to the owning pipeline.
        _available_models (Tuple[str, ...]): List of upscaling model names.
        _available_geometries (Tuple[str, ...]): List of output geometry modes.
        _current_model_index (int): Index of the currently active model.
        _current_geometry_index (int): Index of the currently active geometry.
    """

    def __init__(
        self,
        pipeline: "Pipeline",
        available_models: Tuple[str, ...] = UPSCALING_MODELS,
        available_geometries: Tuple[str, ...] = OUTPUT_GEOMETRIES,
    ) -> None:
        """
        Initialize the controller.

        Args:
            pipeline: The Pipeline instance this controller manages.
            available_models: Tuple of model names supported for switching.
            available_geometries: Tuple of geometry mode names.
        """
        self._pipeline = pipeline
        self._available_models = available_models
        self._available_geometries = available_geometries

        # Thread‑safe request queues
        self._model_switch_queue: Queue[bool] = Queue()  # True = next, False = previous
        self._geometry_switch_queue: Queue[bool] = Queue()
        self._screenshot_requested = False
        self._screenshot_lock = threading.Lock()

        self._current_model_index = 0
        self._current_geometry_index = 0

    # ----------------------------------------------------------------------
    # Public API (safe to call from any thread)
    # ----------------------------------------------------------------------

    def toggle_overlay(self) -> None:
        """
        Show/hide the overlay window and pause/resume processing.

        When hidden, the pipeline stops capturing and upscaling to save resources.
        """
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
            next_model: If True, switch to the next model in the list.
                If False, switch to the previous model.
        """
        self._model_switch_queue.put(next_model)

    def switch_geometry(self) -> None:
        """Request a geometry mode cycle (next mode)."""
        self._geometry_switch_queue.put(True)

    def take_screenshot(self) -> None:
        """Request a screenshot of the current upscaled output."""
        with self._screenshot_lock:
            self._screenshot_requested = True

    # ----------------------------------------------------------------------
    # Request processing (called from pipeline thread)
    # ----------------------------------------------------------------------

    def process_requests(self) -> None:
        """
        Consume and apply any pending requests.

        This method must be called periodically from the pipeline thread.
        It processes one request of each type per invocation to avoid
        blocking the pipeline loop.
        """
        # Model switch (at most one per call)
        try:
            next_model = self._model_switch_queue.get_nowait()
            self._apply_model_switch(next_model)
        except Empty:
            pass

        # Screenshot (only if requested)
        with self._screenshot_lock:
            screenshot_requested = self._screenshot_requested
            self._screenshot_requested = False
        if screenshot_requested:
            self._save_screenshot()

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
        """
        Switch to the next or previous model.

        Args:
            next_model: Direction of switch (True = next, False = previous).
        """
        total = len(self._available_models)
        if total == 0:
            logger.warning("No models available for switching")
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

        # Recreate the upscaler with the new model
        self._pipeline.recreate_upscaler()

        # Update Lanczos source texture to the new upscaler output
        self._pipeline.presenter.set_source_texture(
            self._pipeline.upscaler_mgr.get_output_texture()
        )

        # Clear any stale frames (optional, but safe)
        self._pipeline.clear_frame_queue()

        # Show OSD message
        self._pipeline.osd_queue.put((f"Model: {new_model}", OSD_DURATION))

    def _apply_geometry_cycle(self) -> None:
        """Cycle to the next output geometry mode."""
        total = len(self._available_geometries)
        if total == 0:
            logger.warning("No geometry modes available for cycling")
            return

        new_idx = (self._current_geometry_index + 1) % total
        new_geometry = self._available_geometries[new_idx]

        old_geometry = self._pipeline.config.output_geometry
        logger.info(f"Switching output geometry from {old_geometry} to {new_geometry}")
        self._current_geometry_index = new_idx
        self._pipeline.config.output_geometry = new_geometry

        # Update overlay scale mode (must be done on main thread)
        QMetaObject.invokeMethod(
            self._pipeline.overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, new_geometry),
        )

        # Recalculate content dimensions and update overlay
        self._pipeline.update_content_dimensions()

        # Show OSD message
        self._pipeline.osd_queue.put((f"Geometry: {new_geometry}", OSD_DURATION))

    @staticmethod
    def _download_and_save(
        texture: "Texture2D", width: int, height: int, pipeline: "Pipeline"
    ) -> None:
        """
        Download texture data from GPU and save as PNG.

        This function runs in a background thread to avoid blocking the pipeline.
        It downloads the texture, converts from BGRA to RGB, and saves to the
        configured screenshot directory.

        Args:
            texture: Source texture to capture (usually the upscaled output).
            width: Texture width in pixels.
            height: Texture height in pixels.
            pipeline: Reference to the Pipeline instance (for config and OSD queue).
        """
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

    def _save_screenshot(self) -> None:
        """
        Capture the current upscaled texture and offload saving to a background thread.
        """
        try:
            src_tex = self._pipeline.upscaler_mgr.get_output_texture()
            if src_tex is None:
                logger.warning("No output texture available for screenshot")
                self._pipeline.osd_queue.put(("Screenshot failed", OSD_DURATION))
                return

            temp_tex = Texture2D(src_tex.width, src_tex.height)
            src_tex.copy_to(temp_tex)

            # Offload download and save to a background thread
            threading.Thread(
                target=self._download_and_save,
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
        """
        Set the current model index based on the config value.

        Args:
            model_name: The model name from the configuration.
        """
        if model_name in self._available_models:
            self._current_model_index = self._available_models.index(model_name)
        else:
            logger.warning(f"Model '{model_name}' not in available models list")

    def set_initial_geometry_index(self, geometry_name: str) -> None:
        """
        Set the current geometry index based on the config value.

        Args:
            geometry_name: The geometry mode from the configuration.
        """
        if geometry_name in self._available_geometries:
            self._current_geometry_index = self._available_geometries.index(
                geometry_name
            )
        else:
            logger.warning(
                f"Geometry '{geometry_name}' not in available geometries list"
            )
