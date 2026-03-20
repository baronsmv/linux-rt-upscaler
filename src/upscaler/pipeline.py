import logging
import os
import struct
import threading
import time
from queue import Empty, Queue
from typing import Any, Optional, Tuple

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QCursor
from Xlib.display import Display
from Xlib.error import XError, BadWindow
from Xlib.xobject.drawable import Window as XlibWindow
from compushady import (
    Buffer,
    Compute,
    Texture2D,
    Sampler,
    Swapchain,
    HEAP_UPLOAD,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_FILTER_POINT,
)
from compushady.formats import R8G8B8A8_UNORM
from compushady.shaders import hlsl

from .capture.capture import FrameGrabber
from .shaders.srcnn import SRCNN
from .utils.parsers import color_string_to_float4, parse_output_geometry

logger = logging.getLogger(__name__)

# Constant buffer layout: 4 floats (bgColor), 4 uint, 4 int, 1 float (blur)
CB_FORMAT = "ffffIIIIiiiif"
CB_SIZE = struct.calcsize(CB_FORMAT)


def _calculate_scaling_rect(
    src_w: int, src_h: int, dst_w: int, dst_h: int, mode: str
) -> Tuple[int, int, int, int]:
    """
    Returns (x, y, w, h) where (x, y) is the top‑left corner of the
    destination rectangle within the output texture of size dst_w x dst_h.
    """
    if mode == "stretch":
        return 0, 0, dst_w, dst_h

    if mode == "cover":
        scale = max(dst_w / src_w, dst_h / src_h)
    else:  # "fit" or any unknown mode (fallback to fit)
        scale = min(dst_w / src_w, dst_h / src_h)

    out_w = int(src_w * scale)
    out_h = int(src_h * scale)
    out_x = (dst_w - out_w) // 2
    out_y = (dst_h - out_h) // 2
    return out_x, out_y, out_w, out_h


class Pipeline:
    """
    Main processing pipeline: captures a window, upscales it via SRCNN,
    scales to screen size with Lanczos, and presents to a swapchain.
    Optionally maps clicks to the target window.
    """

    def __init__(
        self,
        window_info: Any,  # WindowInfo instance
        screen_width: int,
        screen_height: int,
        overlay: Any,  # Overlay instance
        swapchain: Any,
        display_id: int,
        xid: int,
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
    ) -> None:
        """
        Initialize the pipeline.

        :param window_info: WindowInfo object describing the target window.
        :param screen_width: Full screen width (for presentation).
        :param screen_height: Full screen height.
        :param overlay: OverlayWindow instance (used for opacity and click mapping).
        :param swapchain: compushady Swapchain for presenting the final image.
        :param model_name: Name of the SRCNN model to load.
        :param double_upscale: If True, the upscaler performs a 4x upscale (two 2x passes),
                               otherwise only a single 2x upscale.
        """
        self.window_info = window_info
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.content_width = overlay.content_width
        self.content_height = overlay.content_height

        self.crop_left = crop_left
        self.crop_top = crop_top
        self.crop_right = crop_right
        self.crop_bottom = crop_bottom
        self.crop_width = window_info.width - crop_left - crop_right
        self.crop_height = window_info.height - crop_top - crop_bottom

        # Compute source dimensions after upscaling
        self.double_upscale = double_upscale
        self.src_w = self.crop_width * (4 if double_upscale else 2)
        self.src_h = self.crop_height * (4 if double_upscale else 2)

        self.output_geometry = output_geometry
        self.base_width = base_width
        self.base_height = base_height
        self.overlay_mode = overlay_mode

        self.overlay = overlay
        self.swapchain = swapchain
        self.model_name = model_name
        self.background_color = color_string_to_float4(overlay.background_color)

        self.display_id = display_id
        self.xid = xid
        self.last_recreate_time = 0
        self.consecutive_failures = 0

        logger.info(
            f"Initializing Pipeline: target={window_info.title} ({window_info.width}x{window_info.height}), "
            f"screen={screen_width}x{screen_height}, model={model_name}, "
            f"double_upscale={double_upscale}"
        )

        # Screen texture (output of the pipeline)
        logger.debug("Creating screen texture...")
        start = time.perf_counter()
        self.screen_tex = Texture2D(screen_width, screen_height, format=R8G8B8A8_UNORM)
        logger.debug(
            f"Screen texture created in {(time.perf_counter() - start)*1000:.2f} ms"
        )

        # Create upscaler (SRCNN)
        logger.debug(f"Creating upscaler with model '{model_name}'...")
        start = time.perf_counter()
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
        )
        logger.debug(f"Upscaler created in {(time.perf_counter() - start)*1000:.2f} ms")

        # Load Lanczos shader
        shader_dir = os.path.dirname(__file__)
        shader_path = os.path.join(shader_dir, "shaders", "lanczos2.hlsl")
        logger.debug(f"Loading Lanczos shader from {shader_path}")
        start = time.perf_counter()
        with open(shader_path, "r") as f:
            self.lanczos_shader = hlsl.compile(f.read())
        logger.debug(
            f"Lanczos shader compiled in {(time.perf_counter() - start)*1000:.2f} ms"
        )

        # Create sampler for Lanczos scaling (point sampling, clamp addressing)
        self.lanczos_sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        logger.debug("Lanczos sampler created.")

        # Constant buffer (will be updated per frame with scaling parameters)
        self.cb = Buffer(CB_SIZE, heap_type=HEAP_UPLOAD)
        logger.debug("Constant buffer created.")

        # For click mapping rectangle (updated each frame)
        self.overlay.scaling_rect = [0, 0, 0, 0]  # x, y, w, h

        # Threading control
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_queue: Queue[Optional[bytearray]] = Queue(maxsize=1)
        self.stopped_event = threading.Event()

        # Performance tracking
        self.frame_count = 0
        self.last_fps_log = 0.0

        # X11 connection for geometry queries (used only if map_events is False)
        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        self._open_x_display()
        self._last_opacity_update = 0.0

    def _open_x_display(self) -> None:
        """Open a connection to the X server for opacity control."""
        try:
            self._x_display = Display()
            self._x_window = self._x_display.create_resource_object(
                "window", self.window_info.handle
            )
            logger.debug("Opened X display for opacity control.")
        except XError as e:
            logger.error(f"Failed to open X display for opacity: {e}")
            self._x_display = None
            self._x_window = None

    def start(self) -> None:
        """Start the pipeline thread."""
        logger.info("Starting pipeline thread.")
        self.running = True
        self.thread = threading.Thread(target=self._run, name="PipelineThread")
        self.thread.start()

    def stop(self) -> None:
        logger.info("Stopping pipeline thread.")
        self.running = False

        # Unblock queue by pushing a dummy frame
        dummy = bytearray(self.window_info.width * self.window_info.height * 4)
        self.frame_queue.put(dummy)

        # Daemon thread will be killed on exit
        if self.thread is not None:
            self.thread.join(timeout=2.0)
            if self.thread.is_alive():
                logger.warning("Pipeline thread did not stop gracefully.")
            else:
                logger.debug("Pipeline thread joined.")

        self.swapchain = None
        self.screen_tex = None
        self.upscaler = None
        self.lanczos_compute = None

        self._close_x_display()

    def _close_x_display(self) -> None:
        if self._x_display is not None:
            try:
                self._x_display.close()
                logger.debug("Closed X display.")
            except Exception as e:
                logger.warning(f"Error closing X display: {e}")
            finally:
                self._x_display = None
                self._x_window = None

    def _update_opacity(self) -> None:
        """
        Update overlay opacity based on mouse position relative to target window.
        Throttled to once per 100 ms to reduce X11 overhead.
        """
        now = time.time()
        if now - self._last_opacity_update < 0.1:
            return
        self._last_opacity_update = now

        if self.overlay.map_events:
            self.overlay.setWindowOpacity(1.0)
            return

        if self._x_window is None or self._x_display is None:
            # No valid X connection – keep overlay visible
            self.overlay.setWindowOpacity(1.0)
            return

        try:
            mouse = QCursor.pos()
            geom = self._x_window.get_geometry()
            trans = geom.root.translate_coords(self._x_window, 0, 0)
            win_x, win_y = trans.x, trans.y

            inside = (
                win_x <= mouse.x() < win_x + self.window_info.width
                and win_y <= mouse.y() < win_y + self.window_info.height
            )
            opacity = 1.0 if inside else 0.2
            self.overlay.setWindowOpacity(opacity)
            logger.debug(
                f"Opacity set to {opacity:.2f} (mouse at ({mouse.x()},{mouse.y()}), "
                f"window at ({win_x},{win_y})"
            )
        except (BadWindow, XError) as e:
            # Target window no longer exists – treat as gone and keep overlay visible
            logger.warning(f"Target window disappeared during opacity update: {e}")
            self.overlay.setWindowOpacity(1.0)
            self._close_x_display()  # release stale resources
        except Exception as e:
            logger.error(f"Unexpected error in opacity update: {e}", exc_info=True)
            self.overlay.setWindowOpacity(1.0)

    def _create_grabber(self):
        """Create grabber inside thread to avoid sharing X connections across threads"""
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
        """Main pipeline loop – runs in a separate thread."""
        logger.info("Pipeline thread started.")
        self._create_grabber()

        # Compute dispatch groups for Lanczos pass
        self.groups_x = (self.screen_width + 15) // 16
        self.groups_y = (self.screen_height + 15) // 16
        logger.debug(f"Compute dispatch groups: {self.groups_x}x{self.groups_y}")

        # Log source dimensions
        logger.debug(f"Source dimensions after upscaling: {self.src_w}x{self.src_h}")

        # Create the Lanczos compute object (will be reused)
        start = time.perf_counter()
        self.lanczos_compute = Compute(
            self.lanczos_shader,
            srv=[self.upscaler.output],
            uav=[self.screen_tex],
            cbv=[self.cb],
            samplers=[self.lanczos_sampler],
        )
        logger.debug(
            f"Lanczos compute object created in {(time.perf_counter() - start)*1000:.2f} ms"
        )

        # Frame timing
        last_frame_time = time.time()
        frame_times = []

        while self.running:
            try:
                # Check if target window size changed
                self._update_target_window_size()
                self._process_one_frame()
                self.frame_count += 1

                # FPS logging every 2 seconds
                now = time.time()
                if now - self.last_fps_log >= 2.0:
                    avg_interval = (
                        (now - last_frame_time) / self.frame_count
                        if self.frame_count
                        else 0
                    )
                    fps = 1.0 / avg_interval if avg_interval else 0
                    logger.info(
                        f"FPS: {fps:.1f} (frames: {self.frame_count}, avg interval: {avg_interval*1000:.2f} ms)"
                    )
                    last_frame_time = now
                    self.frame_count = 0
                    self.last_fps_log = now

            except BadWindow:
                # Target window was destroyed – exit the loop cleanly
                logger.info("Target window destroyed, stopping pipeline loop.")
                break
            except XError as e:
                # Any other X error – log and exit
                logger.error(f"X error in pipeline loop: {e}")
                break
            except RuntimeError as e:
                if "Target window gone timeout" in str(e):
                    logger.info("Target window gone, stopping pipeline.")
                    break
                else:
                    logger.debug(f"Fatal error in pipeline loop: {e}")
                    break
            except Exception as e:
                logger.debug(f"Fatal error in pipeline loop: {e}")
                break

        self.stopped_event.set()
        logger.info("Pipeline stopped event set.")

        # Tell the main thread to quit via Qt's queued connection
        QMetaObject.invokeMethod(
            self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
        )

    def _process_one_frame(self) -> None:
        """
        Grab a frame, upscale, scale, and present. May raise XError/BadWindow.
        """
        frame_start = time.perf_counter()

        # Grab frame from target window
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
                self._update_target_window_size(force=True)
                return
            else:
                raise

        logger.debug(f"Frame grabbed, size={len(frame)} bytes")

        if not self.running:
            return

        # Put frame into queue (maxsize=1 ensures we only keep the most recent)
        self.frame_queue.put(frame)

        # Retrieve the latest frame (if any)
        try:
            frame = self.frame_queue.get_nowait()
        except Empty:
            logger.debug("Frame queue empty, skipping this cycle")
            return

        # Upscale with SRCNN
        upscale_start = time.perf_counter()
        self.upscaler.upload(frame)
        self.upscaler.compute()
        upscale_time = (time.perf_counter() - upscale_start) * 1000
        logger.debug(f"Upscaling took {upscale_time:.2f} ms")

        # Compute rectangle within the content canvas
        r_x, r_y, r_w, r_h = _calculate_scaling_rect(
            self.src_w,
            self.src_h,
            self.content_width,
            self.content_height,
            self.overlay.scale_mode,
        )

        # Position the content canvas on the screen (centered by default)
        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2

        # Apply user offsets and rectangle offset
        dst_x = canvas_x + r_x + self.overlay.offset_x
        dst_y = canvas_y + r_y + self.overlay.offset_y
        dst_w = r_w
        dst_h = r_h

        # Store for mouse mapping
        self.overlay.scaling_rect = [dst_x, dst_y, dst_w, dst_h]

        # Lanczos scaling (constant buffer)
        cb_data = struct.pack(
            CB_FORMAT,
            *self.background_color,  # 4 floats
            self.src_w,
            self.src_h,
            self.screen_width,
            self.screen_height,  # 4 uint
            dst_x,
            dst_y,
            dst_w,
            dst_h,  # 4 int
            1.0,  # blur (float)
        )
        self.cb.upload(cb_data)

        # Dispatch compute
        dispatch_start = time.perf_counter()
        self.lanczos_compute.dispatch(self.groups_x, self.groups_y, 1)
        dispatch_time = (time.perf_counter() - dispatch_start) * 1000
        logger.debug(f"Lanczos dispatch took {dispatch_time:.2f} ms")

        # Opacity control
        self._update_opacity()

        # Present to swapchain
        present_start = time.perf_counter()
        self.swapchain.present(self.screen_tex)
        present_time = (time.perf_counter() - present_start) * 1000
        logger.debug(f"Present took {present_time:.2f} ms")

        # Check if swapchain needs recreation
        if self.swapchain.needs_recreation():
            if self.swapchain.is_out_of_date():
                logger.info("Swapchain out-of-date, full pipeline rebuild in progress")
                self._update_target_window_size()  # ensure target size is current
                self.recreate_swapchain()
            elif self.swapchain.is_suboptimal():
                logger.debug("Swapchain suboptimal, recreating")
                self.recreate_swapchain()

        total_frame_time = (time.perf_counter() - frame_start) * 1000
        logger.debug(f"Total frame processing time: {total_frame_time:.2f} ms")

    def recreate_swapchain(self):
        """Create a new swapchain when the current one becomes suboptimal."""
        now = time.time()
        if now - self.last_recreate_time < 1.0:  # at most once per second
            return

        self.last_recreate_time = now
        logger.info("Recreating swapchain")

        new_width = self.overlay.width()
        new_height = self.overlay.height()

        # If the overlay was resized, update screen texture and compute groups
        if new_width != self.screen_width or new_height != self.screen_height:
            logger.info(
                f"Overlay resized from {self.screen_width}x{self.screen_height} to {new_width}x{new_height}"
            )
            self.screen_width = new_width
            self.screen_height = new_height
            start = time.perf_counter()
            self.screen_tex = Texture2D(new_width, new_height, format=R8G8B8A8_UNORM)
            logger.debug(
                f"Screen texture recreated in {(time.perf_counter() - start)*1000:.2f} ms"
            )
            self.groups_x = (new_width + 15) // 16
            self.groups_y = (new_height + 15) // 16
            self._update_content_dimensions()

        # Create a new swapchain (the old one will be garbage‑collected later)
        start = time.perf_counter()
        new_swap = Swapchain((self.display_id, self.xid), R8G8B8A8_UNORM, 3)
        logger.debug(
            f"Swapchain recreated in {(time.perf_counter() - start)*1000:.2f} ms"
        )
        self.swapchain = new_swap
        self._rebuild_lanczos_compute()

        logger.info("Swapchain recreated")

    def _rebuild_lanczos_compute(self):
        """Rebuild the Lanczos compute object when resources change."""
        start = time.perf_counter()
        self.lanczos_compute = Compute(
            self.lanczos_shader,
            srv=[self.upscaler.output],
            uav=[self.screen_tex],
            cbv=[self.cb],
            samplers=[self.lanczos_sampler],
        )
        logger.debug(
            f"Lanczos compute rebuilt in {(time.perf_counter() - start)*1000:.2f} ms"
        )

    def _update_target_window_size(self, force: bool = False, depth: int = 0) -> bool:
        """
        Check if the target window has been resized or recreated.
        If so, recreate the frame grabber, upscaler, and refresh X resources.
        If force is True, always attempt to refresh even if size/handle unchanged.
        Returns True if a change occurred or if recovery succeeded.
        """
        if depth > 2:
            return False

        if self._x_window is None:
            # Attempt to open X display if not already
            if depth == 0:
                self._open_x_display()
            return False

        try:
            geom = self._x_window.get_geometry()
            new_handle = self._x_window.id
            new_width = geom.width
            new_height = geom.height
        except (BadWindow, XError) as e:
            # Window is gone or inaccessible – treat as change and try to refresh
            logger.debug(f"X error when querying window: {e}")
            if force:
                return False
            self._close_x_display()
            self._open_x_display()
            if self._x_window is None:
                return False
            return self._update_target_window_size(force=True, depth=depth + 1)

        handle_changed = new_handle != self.window_info.handle
        size_changed = (
            new_width != self.window_info.width or new_height != self.window_info.height
        )

        if handle_changed or size_changed or force:
            logger.info(
                f"Target window changed: handle {self.window_info.handle} -> {new_handle}, "
                f"size {self.window_info.width}x{self.window_info.height} -> {new_width}x{new_height}"
            )

            self.window_info.handle = new_handle
            self.window_info.width = new_width
            self.window_info.height = new_height
            self.overlay.set_target_handle(self.window_info.handle)
            self.overlay.set_target_size(new_width, new_height)

            # Recompute crop dimensions
            self.crop_width = self.window_info.width - self.crop_left - self.crop_right
            self.crop_height = (
                self.window_info.height - self.crop_top - self.crop_bottom
            )
            self.overlay.set_crop(
                self.crop_left, self.crop_top, self.crop_width, self.crop_height
            )

            self._update_content_dimensions()
            self.src_w = self.crop_width * (4 if self.double_upscale else 2)
            self.src_h = self.crop_height * (4 if self.double_upscale else 2)

            if self.crop_width <= 0 or self.crop_height <= 0:
                logger.warning(
                    "Crop dimensions became invalid after resize; disabling crop."
                )
                self.crop_width = self.window_info.width
                self.crop_height = self.window_info.height
                self.crop_left = self.crop_top = self.crop_right = self.crop_bottom = 0
                self.src_w = self.crop_width * (4 if self.double_upscale else 2)
                self.src_h = self.crop_height * (4 if self.double_upscale else 2)

            # Recreate upscaler with new size
            start = time.perf_counter()
            self.upscaler = SRCNN(
                width=self.crop_width,
                height=self.crop_height,
                model_name=self.model_name,
                double_upscale=self.double_upscale,
            )
            logger.debug(
                f"Upscaler recreated in {(time.perf_counter() - start)*1000:.2f} ms"
            )

            # Recreate frame grabber with the new handle and dimensions
            self._create_grabber()

            # Rebuild Lanczos compute object (depends on upscaler output)
            self._rebuild_lanczos_compute()

            return True

        return False

    def _update_content_dimensions(self):
        """Recalculate content_width/content_height based on current overlay size."""
        overlay_w = self.overlay.width()
        overlay_h = self.overlay.height()

        # Re‑parse the output geometry using the current overlay size as the reference
        new_content_w, new_content_h, _, _, _ = parse_output_geometry(
            self.output_geometry,
            self.crop_width,
            self.crop_height,
            overlay_w,
            overlay_h,
        )

        if new_content_w != self.content_width or new_content_h != self.content_height:
            logger.debug(
                f"Content dimensions updated: {self.content_width}x{self.content_height} -> {new_content_w}x{new_content_h}"
            )
            self.content_width = new_content_w
            self.content_height = new_content_h
            self.overlay.set_content_dimensions(new_content_w, new_content_h)
