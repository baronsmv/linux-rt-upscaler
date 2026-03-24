import logging
import threading
import time
from queue import Queue
from typing import Any, Optional

from PySide6.QtCore import QMetaObject, Qt
from compushady import Texture2D
from compushady.formats import R8G8B8A8_UNORM

from .capture import FrameGrabber
from .opacity_controller import OpacityController
from .shaders import LanczosScaler, SRCNN
from .swapchain_manager import SwapchainManager
from .utils import calculate_scaling_rect
from .window_tracker import WindowTracker
from ..overlay.window import OverlayWindow
from ..utils.parsers import color_string_to_float4, parse_output_geometry
from ..utils.x11 import get_display

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Main processing pipeline: captures a window, upscales it via SRCNN,
    scales to screen size with Lanczos, and presents to a swapchain.
    """

    def __init__(
        self,
        window_info: Any,  # WindowInfo instance
        overlay: OverlayWindow,
        model_name: str,
        double_upscale: bool,
        output_geometry: str,
        base_width: int,
        base_height: int,
        overlay_mode: int,
        crop_left: int = 0,
        crop_top: int = 0,
        crop_right: int = 0,
        crop_bottom: int = 0,
        scale_factor: float = 1.0,
    ) -> None:
        self.window_info = window_info
        self.overlay = overlay
        self.model_name = model_name
        self.double_upscale = double_upscale
        self.output_geometry = output_geometry
        self.base_width = base_width
        self.base_height = base_height
        self.overlay_mode = overlay_mode
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.scale_factor = scale_factor

        self.screen_width = overlay.width()
        self.screen_height = overlay.height()
        self.content_width = overlay.content_width
        self.content_height = overlay.content_height

        self.crop_width = window_info.width - crop_left - crop_right
        self.crop_height = window_info.height - crop_top - crop_bottom

        self.src_w = self.crop_width * (4 if double_upscale else 2)
        self.src_h = self.crop_height * (4 if double_upscale else 2)

        self.background_color = color_string_to_float4(overlay.background_color)

        # Swapchain manager
        display_id = get_display()
        self.swapchain_manager = SwapchainManager(
            display_id, overlay.xid, self.screen_width, self.screen_height
        )

        # Screen texture
        self.screen_tex = Texture2D(
            self.screen_width, self.screen_height, format=R8G8B8A8_UNORM
        )

        # Upscaler
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
        )

        # Lanczos scaler
        self.lanczos_scaler = LanczosScaler()
        self.lanczos_scaler.set_source_texture(self.upscaler.output)
        self.lanczos_scaler.set_target_texture(self.screen_tex)

        # Compute groups
        self.groups_x = (self.screen_width + 15) // 16
        self.groups_y = (self.screen_height + 15) // 16

        # Window tracker
        self.window_tracker = WindowTracker(
            window_info.handle, window_info.width, window_info.height
        )

        # Opacity controller
        self.opacity_controller = OpacityController(
            overlay, window_info.handle, window_info.width, window_info.height
        )

        # Click mapping rect
        overlay.scaling_rect = [0, 0, 0, 0]

        # Threading
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_queue: Queue[Optional[bytearray]] = Queue(maxsize=1)
        self.stopped_event = threading.Event()

        # Performance
        self.frame_count = 0
        self.last_fps_log = 0.0
        self._last_frame_time = 0.0
        self.grabber = None
        self.consecutive_failures = 0

    def start(self) -> None:
        """Start the pipeline thread."""
        logger.info("Starting pipeline thread.")
        self.running = True
        self.thread = threading.Thread(target=self._run, name="PipelineThread")
        self.thread.start()

    def stop(self) -> None:
        """Stop the pipeline thread and clean up resources."""
        logger.info("Stopping pipeline thread.")
        self.running = False

        # Unblock queue by pushing a dummy frame
        dummy = bytearray(self.window_info.width * self.window_info.height * 4)
        self.frame_queue.put(dummy)

        if self.thread is not None:
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                logger.warning("Pipeline thread did not stop gracefully.")
            else:
                logger.debug("Pipeline thread joined.")

        # Clean up components
        self.swapchain_manager = None
        self.screen_tex = None
        self.upscaler = None
        self.lanczos_scaler = None
        self.window_tracker.close()
        self.opacity_controller.close()

    def _create_grabber(self):
        try:
            start = time.perf_counter()
            self.grabber = FrameGrabber(
                self.window_info,
                crop_left=self.crop_left,
                crop_top=self.crop_top,
                crop_right=self.crop_right,
                crop_bottom=self.crop_bottom,
            )
            logger.debug(
                f"FrameGrabber created for window {self.window_info.handle} in "
                f"{(time.perf_counter() - start)*1000:.2f} ms"
            )
        except Exception as e:
            logger.error(f"Failed to create FrameGrabber: {e}", exc_info=True)
            raise

    def _run(self) -> None:
        """Main pipeline loop."""
        logger.info("Pipeline thread started.")
        self._create_grabber()

        while self.running:
            try:
                # Check for target window changes
                if self.window_tracker.update():
                    self._handle_window_change()

                self._process_one_frame()
                self.frame_count += 1

                # FPS logging every 2 seconds
                now = time.time()
                if now - self.last_fps_log >= 2.0:
                    elapsed = now - self._last_frame_time
                    if elapsed > 0:
                        fps = self.frame_count / elapsed
                        logger.info(f"FPS: {fps:.1f} (frames: {self.frame_count})")
                    self._last_frame_time = now
                    self.frame_count = 0
                    self.last_fps_log = now

            except Exception as e:
                logger.debug(f"Fatal error in pipeline loop: {e}")
                break

        self.stopped_event.set()
        logger.info("Pipeline stopped event set.")
        QMetaObject.invokeMethod(
            self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
        )

    def _process_one_frame(self) -> None:
        """Grab, upscale, scale, and present one frame."""
        # Grab frame
        try:
            frame = self.grabber.grab()
            self.consecutive_failures = 0
        except RuntimeError as e:
            if "window probably gone" in str(e):
                self.consecutive_failures += 1
                if self.consecutive_failures > 30:  # ~0.5 seconds
                    logger.info("Target window gone for too long, stopping pipeline.")
                    raise RuntimeError("Target window gone timeout")
                logger.info("Target window disappeared, attempting to recover...")
                self.window_tracker.update(force=True)
                return
            else:
                raise

        if not self.running:
            return

        # Keep only the most recent frame
        self.frame_queue.put(frame)
        frame = self.frame_queue.get_nowait()

        # Upscale
        self.upscaler.upload(frame)
        self.upscaler.compute()

        # Calculate destination rectangle
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            self.src_w,
            self.src_h,
            self.content_width,
            self.content_height,
            self.overlay.scale_mode,
        )

        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2

        dst_x = canvas_x + r_x + self.overlay.offset_x
        dst_y = canvas_y + r_y + self.overlay.offset_y
        dst_w = r_w
        dst_h = r_h

        # Update mouse mapping rect
        self.overlay.scaling_rect = [
            dst_x / self.scale_factor,
            dst_y / self.scale_factor,
            dst_w / self.scale_factor,
            dst_h / self.scale_factor,
        ]

        # Update Lanczos constants
        self.lanczos_scaler.update_constants(
            self.background_color,
            self.src_w,
            self.src_h,
            self.screen_width,
            self.screen_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
        )

        # Dispatch Lanczos
        self.lanczos_scaler.dispatch(self.groups_x, self.groups_y)

        # Opacity control
        self.opacity_controller.update()

        # Present
        self.swapchain_manager.present(self.screen_tex)

        # Check swapchain
        if self.swapchain_manager.needs_recreation():
            if self.swapchain_manager.is_out_of_date():
                logger.info("Swapchain out-of-date, recreating.")
                self._recreate_swapchain()
            elif self.swapchain_manager.is_suboptimal():
                logger.debug("Swapchain suboptimal, ignoring")

    def _handle_window_change(self) -> None:
        """Update internal state when target window changes."""
        logger.info("Target window changed, updating pipeline.")

        self.window_info.handle = self.window_tracker.handle
        self.window_info.width = self.window_tracker.width
        self.window_info.height = self.window_tracker.height

        self.overlay.set_target_handle(self.window_info.handle)
        self.overlay.set_target_size(self.window_info.width, self.window_info.height)

        # Recompute crop
        self.crop_width = self.window_info.width - self.crop_left - self.crop_right
        self.crop_height = self.window_info.height - self.crop_top - self.crop_bottom
        self.overlay.set_crop(
            self.crop_left, self.crop_top, self.crop_width, self.crop_height
        )

        self.src_w = self.crop_width * (4 if self.double_upscale else 2)
        self.src_h = self.crop_height * (4 if self.double_upscale else 2)

        # Recreate upscaler
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=self.model_name,
            double_upscale=self.double_upscale,
        )
        self.lanczos_scaler.set_source_texture(self.upscaler.output)

        # Recreate grabber
        self._create_grabber()

        # Update opacity controller
        self.opacity_controller.update_target_info(
            self.window_info.handle, self.window_info.width, self.window_info.height
        )

    def _recreate_swapchain(self) -> None:
        """Recreate the swapchain and related resources."""
        new_width = self.overlay.width()
        new_height = self.overlay.height()
        if new_width != self.screen_width or new_height != self.screen_height:
            self.screen_width = new_width
            self.screen_height = new_height
            self.screen_tex = Texture2D(new_width, new_height, format=R8G8B8A8_UNORM)
            self.groups_x = (new_width + 15) // 16
            self.groups_y = (new_height + 15) // 16
            self.lanczos_scaler.set_target_texture(self.screen_tex)
            self._update_content_dimensions()

        self.swapchain_manager.recreate(self.screen_width, self.screen_height)

    def _update_content_dimensions(self) -> None:
        """Recalculate content dimensions based on new overlay size."""
        overlay_w = self.overlay.width()
        overlay_h = self.overlay.height()
        new_content_w, new_content_h, _, _, _ = parse_output_geometry(
            self.output_geometry,
            self.crop_width,
            self.crop_height,
            overlay_w,
            overlay_h,
        )
        if new_content_w != self.content_width or new_content_h != self.content_height:
            self.content_width = new_content_w
            self.content_height = new_content_h
            self.overlay.set_content_dimensions(new_content_w, new_content_h)
