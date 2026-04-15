import logging
import os
import threading
from datetime import datetime
from queue import Queue, Empty
from typing import TYPE_CHECKING, Tuple

from PIL import Image
from PySide6.QtCore import QMetaObject, Qt, Q_ARG
from compushady import Texture2D
from compushady.formats import R8G8B8A8_UNORM

from ..config import OUTPUT_GEOMETRIES, UPSCALING_MODELS
from ..shaders import SRCNN

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
    """Handles external commands for the Pipeline in a thread‑safe manner."""

    def __init__(
        self,
        pipeline: "Pipeline",
        available_models: Tuple[str, ...] = UPSCALING_MODELS,
        available_geometries: Tuple[str, ...] = OUTPUT_GEOMETRIES,
    ) -> None:
        self._pipeline = pipeline
        self._available_models = available_models
        self._available_geometries = available_geometries

        # Thread‑safe queues (filled from main thread, consumed in pipeline thread)
        self._model_switch_queue: Queue[bool] = Queue()
        self._geometry_switch_queue: Queue[bool] = Queue()
        self._screenshot_requested = False

        # Current indices
        self._current_model_index = 0
        self._current_geometry_index = 0

    def toggle_overlay(self) -> None:
        """Show/hide the overlay window and pause/resume processing."""
        if self._pipeline.overlay.isVisible():
            self._pipeline.overlay.hide()
            self._pipeline.user_paused = True
        else:
            self._pipeline.overlay.show()
            self._pipeline.user_paused = False

    def switch_model(self, next_model: bool = True) -> None:
        """Request a model switch."""
        self._model_switch_queue.put(not next_model)  # Inverse order

    def take_screenshot(self) -> None:
        """Request a screenshot."""
        self._screenshot_requested = True

    def switch_geometry(self) -> None:
        """Request a geometry mode cycle."""
        self._geometry_switch_queue.put(True)

    def process_requests(self) -> None:
        """Consume any pending requests and apply them."""
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

    def _apply_model_switch(self, next_model: bool) -> None:
        total = len(self._available_models)
        if total == 0:
            return

        new_idx = (
            (self._current_model_index + 1) % total
            if next_model
            else (self._current_model_index - 1) % total
        )
        new_model = self._available_models[new_idx]

        logger.info(f"Switching model from {self._pipeline.model_name} to {new_model}")
        self._current_model_index = new_idx
        self._pipeline.model_name = new_model

        self._pipeline.upscaler = SRCNN(
            width=self._pipeline.crop_width,
            height=self._pipeline.crop_height,
            model_name=new_model,
            double_upscale=self._pipeline.double_upscale,
            tile_size=self._pipeline.tile_size,
        )
        self._pipeline.lanczos_scaler.set_source_texture(self._pipeline.upscaler.output)

        # Clear stale frames
        self._pipeline.clear_frame_queue()

        # Show OSD feedback
        self._pipeline.show_osd(f"Model: {new_model}", OSD_DURATION)

    def _apply_geometry_cycle(self) -> None:
        total = len(self._available_geometries)
        if total == 0:
            return

        new_idx = (self._current_geometry_index + 1) % total
        new_geometry = self._available_geometries[new_idx]

        logger.info(
            f"Switching output geometry from {self._pipeline.output_geometry} to {new_geometry}"
        )
        self._current_geometry_index = new_idx
        self._pipeline.output_geometry = new_geometry
        self._pipeline.scale_mode = new_geometry

        # Update overlay scale mode
        QMetaObject.invokeMethod(
            self._pipeline.overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, new_geometry),
        )
        self._pipeline.update_content_dimensions()

        # Show OSD feedback
        self._pipeline.show_osd(f"Geometry: {new_geometry}", OSD_DURATION)

    def _save_screenshot(self) -> None:
        """Capture the raw upscaled texture and offload saving to a background thread."""
        try:
            temp_tex = Texture2D(
                self._pipeline.src_w, self._pipeline.src_h, R8G8B8A8_UNORM
            )
            self._pipeline.upscaler.output.copy_to(temp_tex)

            threading.Thread(
                target=_download_and_save,
                args=(
                    temp_tex,
                    self._pipeline.src_w,
                    self._pipeline.src_h,
                    self._pipeline,
                ),
                daemon=True,
                name="ScreenshotSaver",
            ).start()
        except Exception as e:
            logger.error(f"Failed to initiate screenshot: {e}", exc_info=True)
            self._pipeline.osd_queue.put(("Screenshot failed", OSD_DURATION))

    def set_initial_model_index(self, model_name: str) -> None:
        if model_name in self._available_models:
            self._current_model_index = self._available_models.index(model_name)

    def set_initial_geometry_index(self, geometry_name: str) -> None:
        if geometry_name in self._available_geometries:
            self._current_geometry_index = self._available_geometries.index(
                geometry_name
            )
