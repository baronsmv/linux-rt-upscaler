import logging
import os
import threading
from datetime import datetime
from queue import Empty, Queue
from typing import TYPE_CHECKING, Tuple

from PIL import Image
from PySide6.QtCore import Q_ARG, QMetaObject, Qt
from PySide6.QtWidgets import QApplication

from ..config import OUTPUT_GEOMETRIES, UPSCALING_MODELS, ZOOM_LEVELS
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .pipeline import Pipeline

logger = logging.getLogger(__name__)


class PipelineController:
    """
    Handles external commands for the Pipeline in a thread-safe manner.

    Commands are queued and processed in the pipeline thread via
    `process_requests()`. This ensures that Vulkan operations and state
    changes occur on the correct thread.

    Attributes:
        _pipeline (Pipeline): Reference to the owning pipeline.
        available_models (Tuple[str, ...]): List of upscaling model names.
        available_geometries (Tuple[str, ...]): List of output geometry modes.
        _osd_duration (float): Duration (in seconds) for on-screen display messages.
        _current_model_index (int): Index of the currently active model.
        _current_geometry_index (int): Index of the currently active geometry.
    """

    def __init__(
        self,
        pipeline: "Pipeline",
        available_models: Tuple[str, ...] = UPSCALING_MODELS,
        available_geometries: Tuple[str, ...] = OUTPUT_GEOMETRIES,
        available_zoom_levels: Tuple[str, ...] = ZOOM_LEVELS,
    ) -> None:
        """
        Initialize the controller.

        Args:
            pipeline: The Pipeline instance this controller manages.
            available_models: Tuple of model names supported for switching.
            available_geometries: Tuple of geometry mode names.
        """
        self._pipeline = pipeline
        self.available_models = available_models
        self.available_geometries = available_geometries
        self.available_zoom_levels = available_zoom_levels

        # OSD
        self._osd_duration = self._pipeline.config.osd_duration

        # Thread-safe request queues
        self._model_switch_queue: Queue[bool] = Queue()
        self._geometry_switch_queue: Queue[bool] = Queue()
        self._zoom_switch_queue: Queue[bool] = Queue()
        self._screenshot_requested = False
        self._screenshot_lock = threading.Lock()

        self._current_model_index = 0
        self._current_geometry_index = 0
        self._current_zoom_index = 0

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
        self._model_switch_queue.put(not next_model)  # Models are inverted

    def switch_geometry(self) -> None:
        """Request a geometry mode cycle (next mode)."""
        self._geometry_switch_queue.put(True)

    def take_screenshot(self) -> None:
        """Request a screenshot of the current upscaled output."""
        with self._screenshot_lock:
            self._screenshot_requested = True

    def zoom_in(self) -> None:
        """Zoom in: cycle to the next (larger) geometry mode."""
        self._zoom_switch_queue.put(True)

    def zoom_out(self) -> None:
        """Zoom out: cycle to the previous (smaller) geometry mode."""
        self._zoom_switch_queue.put(False)

    def offset_left(self, step: int = 25):
        self._pipeline.config.offset_x -= step
        self._sync_presenter_offset()

    def offset_right(self, step: int = 25):
        self._pipeline.config.offset_x += step
        self._sync_presenter_offset()

    def offset_up(self, step: int = 25):
        self._pipeline.config.offset_y -= step
        self._sync_presenter_offset()

    def offset_down(self, step: int = 25):
        self._pipeline.config.offset_y += step
        self._sync_presenter_offset()

    def exit_app(self):
        QApplication.instance().quit()

    # ----------------------------------------------------------------------
    # Request processing (called from pipeline thread)
    # ----------------------------------------------------------------------

    def cycle_geometry(self, forward: bool = True) -> None:
        """
        Cycle to the next or previous output geometry mode.

        Updates the configuration, syncs the presenter's scale mode, notifies
        the overlay on the main thread, recalculates content dimensions, and
        immediately updates the Lanczos scaling rectangle so the change is
        visible on the next frame - even if the pipeline is temporarily paused.

        Args:
            forward: If True (default), cycle forward; if False, cycle backward.
        """
        total = len(self.available_geometries)
        if total == 0:
            logger.warning("No geometry modes available for cycling")
            return

        delta = 1 if forward else -1
        new_idx = (self._current_geometry_index + delta) % total
        new_geometry = self.available_geometries[new_idx]

        old_geometry = self._pipeline.config.output_geometry
        logger.info(f"Switching output geometry from {old_geometry} to {new_geometry}")
        self._current_geometry_index = new_idx
        self._pipeline.config.output_geometry = new_geometry

        # 1. Update the presenter's scale mode so it applies on the next frame
        self._pipeline.presenter.scale_mode = new_geometry

        # 2. Notify the overlay window on the main thread (for UI consistency)
        QMetaObject.invokeMethod(
            self._pipeline.overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, new_geometry),
        )

        # 3. Recalculate content dimensions based on new geometry and overlay size
        self._pipeline.update_content_dimensions()

        # 4. Immediately recalculate Lanczos scaling rectangle so the change is
        #    visible even before the next frame capture (e.g., when paused).
        src_tex = self._pipeline.upscaler_mgr.get_output_texture()
        if src_tex:
            self._pipeline.presenter.update_lanczos_constants(
                src_tex.width, src_tex.height
            )

        # 5. Show OSD message with the new geometry name
        self._pipeline.osd_queue.put(
            (f"Geometry: {new_geometry}", self._pipeline.config.osd_duration)
        )

    def process_requests(self) -> None:
        """
        Consume and apply any pending requests.

        This method must be called periodically from the pipeline thread.
        It processes one request of each type per invocation to avoid
        blocking the pipeline loop.
        """
        # Model switch
        try:
            next_model = self._model_switch_queue.get_nowait()
            self._apply_model_switch(next_model)
        except Empty:
            pass

        # Screenshot
        with self._screenshot_lock:
            screenshot_requested = self._screenshot_requested
            self._screenshot_requested = False
        if screenshot_requested:
            self._save_screenshot()

        # Geometry cycle
        try:
            forward = self._geometry_switch_queue.get_nowait()
            self.cycle_geometry(forward)
        except Empty:
            pass

        # Zoom level change
        try:
            forward = self._zoom_switch_queue.get_nowait()
            self._apply_zoom_change(forward)
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
        total = len(self.available_models)
        if total == 0:
            logger.warning("No models available for switching")
            return

        new_idx = (
            (self._current_model_index + 1) % total
            if next_model
            else (self._current_model_index - 1) % total
        )
        new_model = self.available_models[new_idx]

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
        self._pipeline.osd_queue.put((f"Model: {new_model}", self._osd_duration))

    def _apply_zoom_change(self, forward: bool) -> None:
        total = len(self.available_zoom_levels)
        if total == 0:
            logger.warning("No zoom levels available")
            return

        delta = 1 if forward else -1
        new_idx = (self._current_zoom_index + delta) % total
        new_zoom = self.available_zoom_levels[new_idx]

        logger.info(f"Zooming to {new_zoom}")
        self._current_zoom_index = new_idx
        self._pipeline.config.output_geometry = new_zoom

        # Percentage zoom always works in "fit" mode
        self._pipeline.presenter.scale_mode = "fit"

        # Notify the overlay (optional but keeps UI consistent)
        QMetaObject.invokeMethod(
            self._pipeline.overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, "fit"),
        )

        self._pipeline.update_content_dimensions()

        src_tex = self._pipeline.upscaler_mgr.get_output_texture()
        if src_tex:
            self._pipeline.presenter.update_lanczos_constants(
                src_tex.width, src_tex.height
            )

        self._pipeline.osd_queue.put(
            (f"Zoom: {new_zoom}", self._pipeline.config.osd_duration)
        )

    def _download_and_save(
        self, texture: Texture2D, width: int, height: int, pipeline: "Pipeline"
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

            # Build format variables for the filename template
            now = datetime.now()
            fmt_vars = {
                "timestamp": now,  # datetime object to supports {timestamp:%Y-%m-%d …}
                "model": pipeline.config.model,
                "width": width,
                "height": height,
            }

            try:
                filename = pipeline.config.screenshot_filename.format(**fmt_vars)
            except (KeyError, ValueError) as e:
                logger.error(
                    "Screenshot filename format error: %s - falling back to default", e
                )
                filename = f"Screenshot_{now:%Y%m%d_%H%M%S}.png"

            save_dir = os.path.expanduser(pipeline.config.screenshot_dir)
            full_path = os.path.join(save_dir, filename)

            # Create subdirectories if the template contains path separators (e.g., {model}/...)
            dir_part = os.path.dirname(full_path)
            if dir_part and not os.path.exists(dir_part):
                os.makedirs(dir_part, exist_ok=True)

            # Ensure filename has a recognized image extension
            if not os.path.splitext(full_path)[1].lower() in (
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
            ):
                full_path += ".png"

            img.save(full_path)
            logger.info("Screenshot saved to %s", full_path)
            success = True
        except Exception as e:
            logger.error("Failed to save screenshot: %s", e, exc_info=True)

        message = "Screenshot saved" if success else "Screenshot failed"
        pipeline.osd_queue.put((message, self._osd_duration))

    def _save_screenshot(self) -> None:
        """
        Capture the current upscaled texture and offload saving to a background thread.
        """
        try:
            src_tex = self._pipeline.upscaler_mgr.get_output_texture()
            if src_tex is None:
                logger.warning("No output texture available for screenshot")
                self._pipeline.osd_queue.put(("Screenshot failed", self._osd_duration))
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
            self._pipeline.osd_queue.put(("Screenshot failed", self._osd_duration))

    def _sync_presenter_offset(self):
        # Presenter will update Lanczos constants on next frame using the new values
        self._pipeline.presenter.offset_x = self._pipeline.config.offset_x
        self._pipeline.presenter.offset_y = self._pipeline.config.offset_y

    # ----------------------------------------------------------------------
    # Initialisation helpers
    # ----------------------------------------------------------------------

    def set_initial_model_index(self, model_name: str) -> None:
        """
        Set the current model index based on the config value.

        Args:
            model_name: The model name from the configuration.
        """
        if model_name in self.available_models:
            self._current_model_index = self.available_models.index(model_name)
        else:
            logger.warning(f"Model '{model_name}' not in available models list")

    def set_initial_geometry_index(self, geometry_name: str) -> None:
        """
        Set the current geometry index based on the config value.

        Args:
            geometry_name: The geometry mode from the configuration.
        """
        if geometry_name in self.available_geometries:
            self._current_geometry_index = self.available_geometries.index(
                geometry_name
            )
        else:
            logger.warning(
                f"Geometry '{geometry_name}' not in available geometries list"
            )

    def set_initial_zoom_index(self) -> None:
        """Set the current zoom index based on the initial output geometry."""
        current = self._pipeline.config.output_geometry
        if current in self.available_zoom_levels:
            self._current_zoom_index = self.available_zoom_levels.index(current)
        else:
            # Default to "100%"
            self._current_zoom_index = self.available_zoom_levels.index("100%")
