import logging
import os
import threading
import time
from datetime import datetime
from queue import Queue, Empty
from typing import Optional

from PIL import Image
from PySide6.QtCore import QMetaObject, Qt, Q_ARG
from compushady import Texture2D
from compushady.formats import R8G8B8A8_UNORM

from .swapchain import SwapchainManager
from ..capture import FrameGrabber
from ..config import Config, OUTPUT_GEOMETRIES, UPSCALING_MODELS
from ..overlay import OverlayWindow
from ..shaders import LanczosScaler, SRCNN
from ..utils import parse_output_geometry, calculate_scaling_rect
from ..window import WindowInfo, WindowTracker, get_display

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Main processing pipeline: captures a window, upscales it via SRCNN,
    scales to screen size with Lanczos, and presents to a swapchain.
    Accepts a Config, WindowInfo, and OverlayWindow.
    """

    def __init__(
        self, config: Config, win_info: WindowInfo, overlay: OverlayWindow
    ) -> None:
        """
        Initialize the pipeline.

        Args:
            config: Full configuration (model, double_upscale, output_geometry, crop, etc.)
            win_info: Information about the target window.
            overlay: The overlay window (already shown and ready).
        """
        self._config = config
        self._win_info = win_info
        self._overlay = overlay

        # Relevant config values
        self._crop_left = config.crop_left
        self._crop_top = config.crop_top
        self._crop_right = config.crop_right
        self._crop_bottom = config.crop_bottom
        self._double_upscale = config.double_upscale
        self._model_name = config.model
        self._output_geometry = config.output_geometry
        self._scale_factor = config.scale_factor
        self._background_color = config.background_color

        # Screen dimensions from overlay
        self._screen_width = overlay.width()
        self._screen_height = overlay.height()
        self._content_width = overlay.content_width
        self._content_height = overlay.content_height
        self._scale_mode = overlay.scale_mode

        # Crop dimensions
        self._crop_width = win_info.width - config.crop_left - config.crop_right
        self._crop_height = win_info.height - config.crop_top - config.crop_bottom

        # Source dimensions after upscaling
        self._src_w = self._crop_width * (4 if self._double_upscale else 2)
        self._src_h = self._crop_height * (4 if self._double_upscale else 2)

        # Swapchain manager
        display_id = get_display()
        self._swapchain_manager = SwapchainManager(
            display_id, overlay.xid, self._screen_width, self._screen_height
        )

        # Screen texture
        self._screen_tex = Texture2D(
            self._screen_width, self._screen_height, format=R8G8B8A8_UNORM
        )

        # Upscaler
        self._upscaler = SRCNN(
            width=self._crop_width,
            height=self._crop_height,
            model_name=self._model_name,
            double_upscale=self._double_upscale,
        )

        # Lanczos scaler
        self._lanczos_scaler = LanczosScaler()
        self._lanczos_scaler.set_source_texture(self._upscaler.output)
        self._lanczos_scaler.set_target_texture(self._screen_tex)

        # Compute groups for Lanczos
        self._groups_x = (self._screen_width + 15) // 16
        self._groups_y = (self._screen_height + 15) // 16

        # Window tracker (for detecting size/handle changes)
        self._window_tracker = WindowTracker(
            win_info.handle, win_info.width, win_info.height
        )

        # Mouse mapping rect (initially empty)
        overlay.scaling_rect = [0, 0, 0, 0]

        # Threading control
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._stopped_event = threading.Event()

        self._frame_queue: Queue[Optional[bytearray]] = Queue(maxsize=1)
        self._switch_queue: Queue[Optional[WindowInfo]] = Queue()
        self._model_switch_queue: Queue[bool] = Queue()
        self._geometry_switch_queue: Queue[bool] = Queue()

        self._screenshot_requested = False
        self._current_model_index = (
            UPSCALING_MODELS.index(self._model_name)
            if self._model_name in UPSCALING_MODELS
            else 0
        )
        self._current_geometry_index = (
            OUTPUT_GEOMETRIES.index(self._output_geometry)
            if self._output_geometry in OUTPUT_GEOMETRIES
            else 0
        )

        # Performance
        self._frame_count = 0
        self._last_fps_log = 0.0
        self._last_frame_time = 0.0
        self._grabber = None
        self._consecutive_failures = 0

    def start(self) -> None:
        """Start the pipeline thread."""
        logger.info("Starting pipeline thread.")
        self._running = True
        self._thread = threading.Thread(target=self._run, name="PipelineThread")
        self._thread.start()

    def stop(self) -> None:
        """Stop the pipeline thread and clean up resources."""
        logger.info("Stopping pipeline thread.")
        self._running = False

        # Unblock queue by pushing a dummy frame
        dummy = bytearray(self._win_info.width * self._win_info.height * 4)
        self._frame_queue.put(dummy)

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                logger.warning("Pipeline thread did not stop gracefully.")
            else:
                logger.debug("Pipeline thread joined.")

        # Clean up components
        self._swapchain_manager = None
        self._screen_tex = None
        self._upscaler = None
        self._lanczos_scaler = None
        self._window_tracker.close()

    def _pause(self):
        """Pause processing (no frame capture or display)."""
        self._paused = True

    def _resume(self):
        """Resume processing."""
        self._paused = False

    def toggle_overlay(self):
        if self._overlay.isVisible():
            self._overlay.hide()
            self._pause()
        else:
            self._overlay.show()
            self._resume()

    def switch_model(self, next_model: bool = True):
        """Switch to the next or previous model."""
        self._model_switch_queue.put(next_model)

    def _clear_frame_queue(self) -> None:
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break

    def _apply_model_switch(self, next_model: bool) -> None:
        """Called in pipeline thread to change the upscaling model."""
        new_idx = (
            (self._current_model_index + 1) % len(UPSCALING_MODELS)
            if next_model
            else (self._current_model_index - 1) % len(UPSCALING_MODELS)
        )
        new_model = UPSCALING_MODELS[new_idx]

        logger.info(f"Switching model from {self._model_name} to {new_model}")
        self._current_model_index = new_idx
        self._model_name = new_model

        # Recreate upscaler with new model
        self._upscaler = SRCNN(
            width=self._crop_width,
            height=self._crop_height,
            model_name=self._model_name,
            double_upscale=self._double_upscale,
        )
        self._lanczos_scaler.set_source_texture(self._upscaler.output)

        # Clear stale frames
        self._clear_frame_queue()

    def take_screenshot(self) -> None:
        """Request a screenshot (main thread)."""
        self._screenshot_requested = True

    def _save_screenshot(self) -> None:
        """Capture the raw upscaled texture (lossless, pre‑Lanczos) and save to PNG."""
        try:
            # Download raw SRCNN output
            data = self._upscaler.output.download()
            img = Image.frombytes(
                "RGBA", (self._src_w, self._src_h), data, "raw", "BGRA"
            )
            img = img.convert("RGB")

            save_dir = os.path.expanduser(
                "~/.local/share/linux-rt-upscaler/screenshots"
            )
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(save_dir, f"screenshot_{timestamp}.png")
            img.save(filename)
            logger.info(f"Screenshot saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}", exc_info=True)

    def cycle_output_geometry(self) -> None:
        """Cycle to the next output geometry."""
        self._geometry_switch_queue.put(True)

    def _apply_geometry_cycle(self, next_geometry: bool) -> None:
        """Cycle through output geometries."""
        new_idx = (self._current_geometry_index + 1) % len(OUTPUT_GEOMETRIES)
        new_geometry = OUTPUT_GEOMETRIES[new_idx]

        logger.info(
            f"Switching output geometry from {self._output_geometry} to {new_geometry}"
        )
        self._current_geometry_index = new_idx
        self._output_geometry = new_geometry

        # Update overlay's scale_mode
        QMetaObject.invokeMethod(
            self._overlay,
            "set_scale_mode",
            Qt.QueuedConnection,
            Q_ARG(str, new_geometry),
        )

        # Update content dimensions to reflect new geometry mode
        self._update_content_dimensions()

    def _create_grabber(self):
        try:
            start = time.perf_counter()
            self._grabber = FrameGrabber(
                self._win_info,
                crop_left=self._crop_left,
                crop_top=self._crop_top,
                crop_right=self._crop_right,
                crop_bottom=self._crop_bottom,
            )
            logger.debug(
                f"FrameGrabber created for window {self._win_info.handle} in "
                f"{(time.perf_counter() - start)*1000:.2f} ms"
            )
        except Exception as e:
            logger.error(f"Failed to create FrameGrabber: {e}", exc_info=True)
            raise

    def _run(self) -> None:
        """Main pipeline loop."""
        logger.info("Pipeline thread started.")
        self._create_grabber()

        while self._running:
            try:
                # If paused, check every 100 ms
                if self._paused:
                    time.sleep(0.1)
                    continue

                # Check for target window changes
                if self._window_tracker.update():
                    self._handle_window_change()

                self._process_one_frame()
                self._frame_count += 1

                # Check if a switch request arrived
                try:
                    new_win = self._switch_queue.get_nowait()
                    if new_win is not None:
                        self._switch_target(new_win)
                except Empty:
                    pass

                # Check for model switch requests
                try:
                    next_model = self._model_switch_queue.get_nowait()
                    self._apply_model_switch(next_model)
                except Empty:
                    pass

                # Screenshot (flag set in main thread)
                if self._screenshot_requested:
                    self._save_screenshot()
                    self._screenshot_requested = False

                # Check for geometry cycle requests
                try:
                    next_geometry = self._geometry_switch_queue.get_nowait()
                    self._apply_geometry_cycle(next_geometry)
                except Empty:
                    pass

                # FPS logging every 2 seconds
                now = time.time()
                if now - self._last_fps_log >= 2.0:
                    elapsed = now - self._last_frame_time
                    if elapsed > 0:
                        fps = self._frame_count / elapsed
                        logger.info(f"FPS: {fps:.1f} (frames: {self._frame_count})")
                    self._last_frame_time = now
                    self._frame_count = 0
                    self._last_fps_log = now

            except Exception as e:
                logger.debug(f"Fatal error in pipeline loop: {e}")
                break

        self._stopped_event.set()
        logger.info("Pipeline stopped event set.")
        QMetaObject.invokeMethod(
            self._overlay, "on_pipeline_stopped", Qt.QueuedConnection
        )

    def _process_one_frame(self) -> None:
        """Grab, upscale, scale, and present one frame."""
        # Grab frame
        try:
            frame = self._grabber.grab()
            self._consecutive_failures = 0
        except RuntimeError as e:
            if "window probably gone" in str(e):
                self._consecutive_failures += 1
                if self._consecutive_failures > 30:  # ~0.5 seconds
                    logger.info("Target window gone for too long, stopping pipeline.")
                    raise RuntimeError("Target window gone timeout")
                logger.info("Target window disappeared, attempting to recover...")

                # Force a fresh window size check
                self._window_tracker.update(force=True)

                # Force a full pipeline update
                self._handle_window_change(force=True)

                # Clear the frame queue to discard the stale frame
                while not self._frame_queue.empty():
                    try:
                        self._frame_queue.get_nowait()
                    except Empty:
                        break
                return

            else:
                raise

        if not self._running:
            return

        # Keep only the most recent frame
        self._frame_queue.put(frame)
        frame = self._frame_queue.get_nowait()

        # Upscale
        self._upscaler.upload(frame)
        self._upscaler.compute()

        # Calculate destination rectangle
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            self._src_w,
            self._src_h,
            self._content_width,
            self._content_height,
            self._scale_mode,
        )

        canvas_x = (self._screen_width - self._content_width) // 2
        canvas_y = (self._screen_height - self._content_height) // 2

        dst_x = canvas_x + r_x + self._config.offset_x
        dst_y = canvas_y + r_y + self._config.offset_y
        dst_w = r_w
        dst_h = r_h

        # Update mouse mapping rect (scaled)
        self._overlay.scaling_rect = [
            dst_x / self._scale_factor,
            dst_y / self._scale_factor,
            dst_w / self._scale_factor,
            dst_h / self._scale_factor,
        ]
        logger.debug(
            f"Scaling rect: dst={self._overlay.scaling_rect}, "
            f"content={self._content_width}x{self._content_height}, "
            f"screen={self._screen_width}x{self._screen_height}"
        )

        # Update Lanczos constants
        self._lanczos_scaler.update_constants(
            self._background_color,
            self._src_w,
            self._src_h,
            self._screen_width,
            self._screen_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
        )

        # Dispatch Lanczos
        self._lanczos_scaler.dispatch(self._groups_x, self._groups_y)

        # Opacity control
        self._overlay.update_opacity()

        # Present
        self._swapchain_manager.present(self._screen_tex)

        # Check swapchain
        if self._swapchain_manager.needs_recreation():
            if self._swapchain_manager.is_out_of_date():
                logger.info("Swapchain out-of-date, recreating.")
                self._recreate_swapchain()
            elif self._swapchain_manager.is_suboptimal():
                logger.debug("Swapchain suboptimal, ignoring")

    def _handle_window_change(self, force: bool = False) -> None:
        """Update internal state when target window changes."""
        logger.info(f"Handling window change (force={force})")

        # Update local window info from tracker's current state
        self._win_info.handle = self._window_tracker.handle
        self._win_info.width = self._window_tracker.width
        self._win_info.height = self._window_tracker.height

        self._overlay.set_target_handle(self._win_info.handle)
        self._overlay.set_target_size(self._win_info.width, self._win_info.height)

        # Recompute crop dimensions
        self._crop_width = self._win_info.width - self._crop_left - self._crop_right
        self._crop_height = self._win_info.height - self._crop_top - self._crop_bottom
        self._overlay.set_crop(
            self._crop_left, self._crop_top, self._crop_width, self._crop_height
        )

        # Update content dimensions (depends on crop and overlay size)
        self._update_content_dimensions()

        # Update source dimensions after upscaling
        self._src_w = self._crop_width * (4 if self._double_upscale else 2)
        self._src_h = self._crop_height * (4 if self._double_upscale else 2)
        logger.debug(f"New src dimensions: {self._src_w}x{self._src_h}")

        # Recreate upscaler with new crop size
        self._upscaler = SRCNN(
            width=self._crop_width,
            height=self._crop_height,
            model_name=self._model_name,
            double_upscale=self._double_upscale,
        )
        self._lanczos_scaler.set_source_texture(self._upscaler.output)

        # Recreate grabber with new window handle and crop
        self._create_grabber()

        # Clear the frame queue to avoid using old frames
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break

        logger.info("Window change handled successfully")

    def _recreate_swapchain(self) -> None:
        """Recreate swapchain and related resources."""
        new_width = self._overlay.width()
        new_height = self._overlay.height()

        if new_width != self._screen_width or new_height != self._screen_height:
            self._screen_width = new_width
            self._screen_height = new_height
            self._screen_tex = Texture2D(new_width, new_height, format=R8G8B8A8_UNORM)
            self._groups_x = (new_width + 15) // 16
            self._groups_y = (new_height + 15) // 16
            self._lanczos_scaler.set_target_texture(self._screen_tex)
            self._update_content_dimensions()

        logger.debug(
            f"Recreating swapchain: "
            f"old size {self._screen_width}x{self._screen_height} "
            f"-> new size {new_width}x{new_height}"
        )
        self._swapchain_manager.recreate(self._screen_width, self._screen_height)

    def _update_content_dimensions(self) -> None:
        """Recalculate content dimensions based on current overlay size and crop."""
        overlay_w = self._overlay.width()
        overlay_h = self._overlay.height()
        new_content_w, new_content_h, _, _, _ = parse_output_geometry(
            self._output_geometry,
            self._crop_width,
            self._crop_height,
            overlay_w,
            overlay_h,
        )
        logger.debug(
            f"Content dimensions updated: "
            f"{self._content_width}x{self._content_height} "
            f"-> {new_content_w}x{new_content_h}, "
            f"mode={self._scale_mode}"
        )
        if (
            new_content_w != self._content_width
            or new_content_h != self._content_height
        ):
            self._content_width = new_content_w
            self._content_height = new_content_h
            self._overlay.set_content_dimensions(new_content_w, new_content_h)

    def _switch_target(self, new_win_info: WindowInfo) -> None:
        """Switch the pipeline to a new target window."""
        logger.info(
            f"Switching pipeline to new window: {new_win_info.title} ({new_win_info.width}x{new_win_info.height})"
        )

        # Update window_info and tracker
        self._win_info = new_win_info
        self._window_tracker = WindowTracker(
            new_win_info.handle, new_win_info.width, new_win_info.height
        )

        # Force a full update of all resources
        self._handle_window_change(force=True)

        # Update overlay with new target info
        self._overlay.set_target_handle(new_win_info.handle)
        self._overlay.set_target_size(new_win_info.width, new_win_info.height)

    def request_switch(self, new_win_info: WindowInfo) -> None:
        self._switch_queue.put(new_win_info)
