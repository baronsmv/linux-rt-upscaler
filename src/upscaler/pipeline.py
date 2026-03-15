import logging
import os
import struct
import threading
import time
from queue import Queue, Empty
from typing import Optional, Any

from PySide6.QtGui import QCursor
from Xlib.display import Display
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

# Module logger
logger = logging.getLogger(__name__)


def _calculate_scaling_rect(
    src_w: int, src_h: int, dst_w: int, dst_h: int
) -> tuple[int, int, int, int]:
    """
    Calculate the letterboxed destination rectangle that preserves aspect ratio.

    Returns (x, y, w, h) where (x,y) is the top‑left corner and (w,h) the size.
    """
    src_aspect = src_w / src_h
    screen_aspect = dst_w / dst_h
    if src_aspect > screen_aspect:
        # Source is wider than screen → fit to width
        out_w = dst_w
        out_h = int(dst_w / src_aspect)
        out_x = 0
        out_y = (dst_h - out_h) // 2
    else:
        # Source is taller or equal → fit to height
        out_h = dst_h
        out_w = int(dst_h * src_aspect)
        out_x = (dst_w - out_w) // 2
        out_y = 0
    logger.debug(
        f"Scaling rect: src={src_w}x{src_h}, dst={dst_w}x{dst_h} -> "
        f"rect=({out_x},{out_y},{out_w},{out_h})"
    )
    return out_x, out_y, out_w, out_h


class Pipeline:
    """
    Main processing pipeline: captures a window, upscales it via SRCNN,
    scales to screen size with Lanczos, and presents to a swapchain.
    Optionally maps clicks to the target window.
    """

    def __init__(
        self,
        window_info: Any,  # actually WindowInfo from the window module
        screen_width: int,
        screen_height: int,
        overlay: Any,  # OverlayWindow instance
        swapchain: Any,  # compushady Swapchain
        map_clicks: bool,
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
        :param map_clicks: If True, mouse events are forwarded to the target window.
        :param model_name: Name of the SRCNN model to load.
        :param double_upscale: If True, the upscaler performs a 4x upscale (two 2x passes),
                               otherwise only a single 2x upscale.
        """
        self.window_info = window_info
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.overlay = overlay
        self.swapchain = swapchain
        self.map_clicks = map_clicks
        self.model_name = model_name
        self.double_upscale = double_upscale

        logger.info(
            f"Initializing Pipeline: target={window_info.title} ({window_info.width}x{window_info.height}), "
            f"screen={screen_width}x{screen_height}, map_clicks={map_clicks}, model={model_name}, "
            f"double_upscale={double_upscale}"
        )

        # Create screen texture (output of the pipeline)
        logger.debug("Creating screen texture...")
        self.screen_tex = Texture2D(screen_width, screen_height, format=R8G8B8A8_UNORM)
        logger.debug("Screen texture created.")

        # Create upscaler (CuNNy / SRCNN)
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
        self.cb = Buffer(struct.calcsize("IIIIf"), heap_type=HEAP_UPLOAD)
        logger.debug("Constant buffer created.")

        # For click mapping rectangle (updated each frame)
        self.overlay.scaling_rect = [0, 0, 0, 0]  # x, y, w, h

        # Threading
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_queue: Queue[Optional[bytearray]] = Queue(maxsize=1)

        # X11 connection for geometry queries (only used if map_clicks is False)
        self._x_display: Optional[Display] = None
        self._x_window: Optional[XlibWindow] = None
        if not self.map_clicks:
            logger.debug(
                "Opening X display for window geometry queries (opacity control)."
            )
            self._x_display = Display()
            self._x_window = self._x_display.create_resource_object(
                "window", self.window_info.handle
            )

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
            self.thread.join()
            logger.debug("Pipeline thread joined.")

        # Close X11 connection if open
        if self._x_display is not None:
            self._x_display.close()
            logger.debug("Closed X display.")

    def _update_opacity(self) -> None:
        """Update overlay opacity based on mouse position relative to target window."""
        if self.map_clicks:
            self.overlay.setWindowOpacity(1.0)
            return

        if self._x_window is None or self._x_display is None:
            logger.warning("X11 resources not available for opacity check.")
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
        except Exception as e:
            logger.error(f"Error updating opacity: {e}", exc_info=True)
            self.overlay.setWindowOpacity(1.0)

    def _run(self) -> None:
        """Main pipeline loop – runs in a separate thread."""
        logger.info("Pipeline thread started.")
        grabber = FrameGrabber(self.window_info)
        logger.debug(f"FrameGrabber created for window {self.window_info.handle}")

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
            # Grab frame from target window
            try:
                frame = grabber.grab()
                logger.debug(f"Frame grabbed, size={len(frame)} bytes")
            except Exception as e:
                logger.error(f"Frame grab failed: {e}", exc_info=True)
                time.sleep(0.1)
                continue

            if not self.running:
                break

            # Put frame into queue (blocks if queue is full, but we set maxsize=1 so it replaces)
            self.frame_queue.put(frame)

            # Retrieve frame (the most recent) from queue
            try:
                frame = self.frame_queue.get_nowait()
            except Empty:
                logger.debug("Frame queue empty, skipping this cycle")
                continue

            # Upscale with SRCNN
            logger.debug("Uploading frame to upscaler...")
            self.upscaler.upload(frame)

            logger.debug("Running SRCNN compute...")
            self.upscaler.compute()  # result in self.upscaler.output

            # Calculate scaling rectangle for click mapping
            dst_x, dst_y, dst_w, dst_h = _calculate_scaling_rect(
                src_w, src_h, self.screen_width, self.screen_height
            )
            self.overlay.scaling_rect[:] = [dst_x, dst_y, dst_w, dst_h]

            # Lanczos scaling
            # Prepare constant buffer
            cb_data = struct.pack(
                "IIIIf",
                src_w,
                src_h,
                self.screen_width,
                self.screen_height,
                1.0,  # blur factor (1.0 = no extra blur)
            )
            self.cb.upload(cb_data)
            logger.debug("Constant buffer updated for Lanczos scaling.")

            # Create compute pipeline for this frame (recreated each frame; can be cached if needed)
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

        logger.info("Pipeline thread finished.")
