import logging
import os
import struct
import threading
from queue import Queue, Empty
from typing import Optional, Any, Tuple

from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QCursor
from Xlib.display import Display
from Xlib.error import XError, BadWindow
from Xlib.xobject.drawable import Window as XlibWindow
from compushady import (
    Compute,
    Buffer,
    Texture2D,
    Sampler,
    HEAP_UPLOAD,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_FILTER_POINT,
)
from compushady.formats import R8G8B8A8_UNORM
from compushady.shaders import hlsl

from .capture.capture import FrameGrabber
from .shaders.srcnn import SRCNN
from .utils.parsers import color_string_to_float4

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
        model_name: str,
        double_upscale: bool,
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
        self.overlay = overlay
        self.swapchain = swapchain
        self.model_name = model_name
        self.double_upscale = double_upscale
        self.background_color = color_string_to_float4(overlay.background_color)

        logger.info(
            f"Initializing Pipeline: target={window_info.title} ({window_info.width}x{window_info.height}), "
            f"screen={screen_width}x{screen_height}, model={model_name}, "
            f"double_upscale={double_upscale}"
        )

        # Screen texture (output of the pipeline)
        logger.debug("Creating screen texture...")
        self.screen_tex = Texture2D(screen_width, screen_height, format=R8G8B8A8_UNORM)
        logger.debug("Screen texture created.")

        # Create upscaler (SRCNN)
        logger.debug(f"Creating upscaler with model '{model_name}'...")
        self.upscaler = SRCNN(
            width=window_info.width,
            height=window_info.height,
            model_name=model_name,
            double_upscale=double_upscale,
        )
        logger.debug("Upscaler created.")

        # Load Lanczos shader
        shader_dir = os.path.dirname(__file__)
        shader_path = os.path.join(shader_dir, "shaders", "lanczos2.hlsl")
        logger.debug(f"Loading Lanczos shader from {shader_path}")
        with open(shader_path, "r") as f:
            self.lanczos_shader = hlsl.compile(f.read())
        logger.debug("Lanczos shader compiled.")

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

        # X11 connection for geometry queries (used only if map_events is False)
        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        if not self.overlay.map_events:
            self._open_x_display()

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

        # Close X11 connection if open
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
        If the window is gone, set opacity to 1.0 and log a warning.
        """
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

    def _run(self) -> None:
        """Main pipeline loop – runs in a separate thread."""
        logger.info("Pipeline thread started.")

        # Create grabber inside thread to avoid sharing X connections across threads
        try:
            grabber = FrameGrabber(self.window_info)
            logger.debug(f"FrameGrabber created for window {self.window_info.handle}")
        except Exception as e:
            logger.error(f"Failed to create FrameGrabber: {e}", exc_info=True)
            return

        # Compute dispatch groups for Lanczos pass
        groups_x = (self.screen_width + 15) // 16
        groups_y = (self.screen_height + 15) // 16
        logger.debug(f"Compute dispatch groups: {groups_x}x{groups_y}")

        # Source dimensions depend on whether we double‑upscaled
        if self.double_upscale:
            src_w = self.window_info.width * 4
            src_h = self.window_info.height * 4
        else:
            src_w = self.window_info.width * 2
            src_h = self.window_info.height * 2
        logger.debug(f"Source dimensions after upscaling: {src_w}x{src_h}")

        while self.running:
            try:
                self._process_one_frame(grabber, src_w, src_h, groups_x, groups_y)
            except BadWindow:
                # Target window was destroyed – exit the loop cleanly
                logger.info("Target window destroyed, stopping pipeline loop.")
                break
            except XError as e:
                # Any other X error – log and exit
                logger.error(f"X error in pipeline loop: {e}")
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

    def _process_one_frame(
        self,
        grabber: FrameGrabber,
        src_w: int,
        src_h: int,
        groups_x: int,
        groups_y: int,
    ) -> None:
        """
        Grab a frame, upscale, scale, and present. May raise XError/BadWindow.
        """
        # Grab frame from target window
        frame = grabber.grab()
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
        logger.debug("Uploading frame to upscaler...")
        self.upscaler.upload(frame)
        logger.debug("Running SRCNN compute...")
        self.upscaler.compute()  # result in self.upscaler.output

        # Compute destination rectangle based on scale_mode
        dst_x, dst_y, dst_w, dst_h = _calculate_scaling_rect(
            src_w, src_h, self.screen_width, self.screen_height, self.overlay.scale_mode
        )

        # Store for mouse mapping
        self.overlay.scaling_rect[:] = [dst_x, dst_y, dst_w, dst_h]

        # Lanczos scaling (constant buffer)
        cb_data = struct.pack(
            CB_FORMAT,
            *self.background_color,  # 4 floats
            src_w,
            src_h,
            self.screen_width,
            self.screen_height,  # 4 uint
            dst_x,
            dst_y,
            dst_w,
            dst_h,  # 4 int
            1.0,  # blur (float)
        )
        logger.debug(f"CB data hex: {cb_data.hex()}")
        self.cb.upload(cb_data)
        logger.debug("Constant buffer updated for Lanczos scaling.")

        # Create compute pipeline
        scale_compute = Compute(
            self.lanczos_shader,
            srv=[self.upscaler.output],
            uav=[self.screen_tex],
            cbv=[self.cb],
            samplers=[self.lanczos_sampler],
        )
        scale_compute.dispatch(groups_x, groups_y, 1)
        logger.debug("Lanczos scaling dispatched.")

        # Opacity control
        self._update_opacity()

        # Present to swapchain
        self.swapchain.present(self.screen_tex)
        logger.debug("Presented to swapchain.")
