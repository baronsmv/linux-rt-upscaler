import logging
import struct
import threading
import time
from queue import Empty, Queue
from typing import Optional, Tuple

from PySide6.QtCore import QMetaObject, Qt
from compushady import Texture2D, configure_device, Compute
from compushady.formats import R8G8B8A8_UNORM

from .controller import PipelineController
from .swapchain import SwapchainManager
from .text_renderer import TextRenderer
from ..capture import FrameGrabber
from ..config import Config, OverlayMode, OUTPUT_GEOMETRIES, UPSCALING_MODELS
from ..overlay import OverlayWindow
from ..shaders import LanczosScaler, OverlayBlender, SRCNN, dispatch_groups
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
        self.config = config
        self._win_info = win_info
        self.overlay = overlay

        # Relevant config values
        self._crop_left = config.crop_left
        self._crop_top = config.crop_top
        self._crop_right = config.crop_right
        self._crop_bottom = config.crop_bottom
        self.double_upscale = config.double_upscale
        self.model_name = config.model
        self.output_geometry = config.output_geometry
        self._scale_factor = config.scale_factor
        self._background_color = config.background_color

        # Screen dimensions from overlay
        self._screen_width = overlay.width()
        self._screen_height = overlay.height()
        self._content_width = overlay.content_width
        self._content_height = overlay.content_height
        self.scale_mode = overlay.scale_mode

        # Crop dimensions
        self.crop_width = win_info.width - config.crop_left - config.crop_right
        self.crop_height = win_info.height - config.crop_top - config.crop_bottom

        # Source dimensions after upscaling
        self.src_w = self.crop_width * (4 if self.double_upscale else 2)
        self.src_h = self.crop_height * (4 if self.double_upscale else 2)

        # Pipeline controller
        self.controller = PipelineController(self)
        self.controller.set_initial_model_index(self.model_name)
        self.controller.set_initial_geometry_index(self.output_geometry)

        # Swapchain manager
        display_id = get_display()
        configure_device(self.config.vulkan_buffer_pool_size)
        self._swapchain_manager = SwapchainManager(
            display_id,
            overlay.xid,
            self._screen_width,
            self._screen_height,
            present_mode=self.config.vulkan_present_mode,
        )

        # Screen texture
        self._screen_tex = Texture2D(
            self._screen_width, self._screen_height, format=R8G8B8A8_UNORM
        )

        # Upscaler
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=self.model_name,
            double_upscale=self.double_upscale,
        )

        # Lanczos scaler
        self.lanczos_scaler = LanczosScaler()
        self.lanczos_scaler.set_source_texture(self.upscaler.output)
        self.lanczos_scaler.set_target_texture(self._screen_tex)

        # Compute groups for Lanczos
        self._groups_x = (self._screen_width + 15) // 16
        self._groups_y = (self._screen_height + 15) // 16

        # Window tracker (for detecting size/handle changes)
        self._window_tracker = WindowTracker(
            win_info.handle, win_info.width, win_info.height
        )

        # Mouse mapping rect (initially empty)
        overlay.scaling_rect = [0, 0, 0, 0]

        # Threading variables and control
        self._running = False
        self.user_paused = False
        self.minimized_paused = False
        self.focus_paused = False
        self._thread: Optional[threading.Thread] = None
        self._stopped_event = threading.Event()
        self._frame_queue: Queue[Optional[bytearray]] = Queue(maxsize=1)
        self._switch_queue: Queue[Optional[WindowInfo]] = Queue()
        self.osd_queue: Queue[Tuple[str, float]] = Queue()

        # Performance
        self._frame_count = 0
        self._last_fps_log = 0.0
        self._last_frame_time = 0.0
        self._grabber = None
        self._consecutive_failures = 0

        # OSD
        self._osd_texture: Optional[Texture2D] = None
        self._needs_osd_redraw = False
        self._osd_expiry_time: Optional[float] = None
        osd_texts = (
            [f"Model: {m}" for m in UPSCALING_MODELS]
            + [f"Geometry: {g}" for g in OUTPUT_GEOMETRIES]
            + ["Screenshot saved", "Screenshot failed"]
        )
        self._text_renderer = TextRenderer(osd_texts, screen_height=self._screen_height)
        self._overlay_blender = OverlayBlender()
        self._overlay_blender.set_screen_texture(self._screen_tex)

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
        try:
            self._frame_queue.put_nowait(dummy)
        except Queue.Full:
            pass

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                logger.warning("Pipeline thread did not stop gracefully.")
            else:
                logger.debug("Pipeline thread joined.")

        if self._grabber:
            self._grabber.close()
            self._grabber = None

        # Clean up components
        self._swapchain_manager = None
        self._screen_tex = None
        self.upscaler = None
        self.lanczos_scaler = None
        self._window_tracker.close()

    def clear_frame_queue(self) -> None:
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break

    def _create_grabber(self):
        try:
            if self._grabber is not None:
                self._grabber.close()
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
                # Process switch requests
                try:
                    new_win = None
                    while True:
                        new_win = self._switch_queue.get_nowait()
                except Empty:
                    pass
                if new_win is not None:
                    self._switch_target(new_win)

                # Window alive check (only when follow_focus is off)
                if not self.config.follow_focus:
                    self._window_tracker.check_alive()
                    if not self._window_tracker.alive:
                        logger.info("Target window closed – exiting.")
                        break

                # Update window state
                changed = self._window_tracker.update()

                # Handle minimization pause
                if self._window_tracker.minimized:
                    if not self.minimized_paused:
                        logger.info(
                            "Target window minimized, pausing frame processing."
                        )
                        self.minimized_paused = True
                        self.overlay.hide()
                    time.sleep(0.1)
                    continue
                else:
                    if self.minimized_paused:
                        logger.info(
                            "Target window restored, resuming frame processing."
                        )
                        self.minimized_paused = False
                        if not self.user_paused:
                            self.overlay.show()

                # Handle focus and manual pause
                bypass_wm = self.config.overlay_mode in (
                    OverlayMode.ALWAYS_ON_TOP.value,
                    OverlayMode.ALWAYS_ON_TOP_TRANSPARENT.value,
                )

                if (
                    bypass_wm
                    and self.config.pause_on_focus_loss
                    and not self._window_tracker.active
                ):
                    if not self.focus_paused:
                        logger.info(
                            "Target window lost focus, pausing and hiding overlay."
                        )
                        self.focus_paused = True
                        QMetaObject.invokeMethod(
                            self.overlay, "hide", Qt.QueuedConnection
                        )
                    time.sleep(0.1)
                    continue
                else:
                    if self.focus_paused:
                        logger.info(
                            "Target window regained focus, resuming and showing overlay."
                        )
                        self.focus_paused = False
                        if not self.user_paused:
                            QMetaObject.invokeMethod(
                                self.overlay, "show", Qt.QueuedConnection
                            )

                # Only handle changes if not minimized
                if changed:
                    self._handle_window_change()

                # If paused via hotkey, skip frame processing
                if self.user_paused:
                    time.sleep(0.1)
                    continue

                # Frame processing
                self._process_one_frame()
                self._frame_count += 1

                # Check controller requests
                self.controller.process_requests()

                # Process OSD requests from other threads
                try:
                    text, duration = self.osd_queue.get_nowait()
                    self.show_osd(text, duration)
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
            self.overlay, "on_pipeline_stopped", Qt.QueuedConnection
        )

    def show_osd(self, text: str, duration: float = 1.5):
        """Request an OSD message to be displayed."""
        tex = self._text_renderer.get_texture(text)
        if tex is not None:
            self._osd_texture = tex
            self._osd_expiry_time = time.monotonic() + duration
            self._needs_osd_redraw = True

    def _draw_osd(self) -> None:
        if self._osd_texture is not None:
            w, h = self._osd_texture.width, self._osd_texture.height
            x = (self._screen_width - w) // 2
            y = (self._screen_height - h) // 2
            self._overlay_blender.blend(self._osd_texture, x, y, w, h)

    def _update_osd_timer(self) -> None:
        if self._osd_texture is not None and self._osd_expiry_time is not None:
            if time.monotonic() >= self._osd_expiry_time:
                self._osd_texture = None
                self._osd_expiry_time = None

    def _process_one_frame(self) -> None:
        """
        Process a single frame:
          1. Grab frame from the target window.
          2. Upload to staging buffer.
          3. Calculate Lanczos destination rectangle and constants.
          4. Build a list of GPU dispatches:
             - All upscale passes (SRCNN).
             - Lanczos scaling pass.
             - (Optional) OSD blend pass if an OSD message is active.
          5. Submit everything in ONE Vulkan command buffer, including:
             - Copy from staging to input texture.
             - All compute dispatches.
             - Layout transition of screen texture to PRESENT_SRC_KHR.
          6. Present the screen texture without waiting for an additional fence.
          7. Update mouse mapping for overlay interaction.
          8. Check if swapchain needs recreation.
        """

        # -------------------------------------------------------------------------
        # 1. Grab frame from X11 (raw BGRA bytes)
        # -------------------------------------------------------------------------
        try:
            frame, is_dirty, rects = self._grabber.grab()
        except RuntimeError as e:
            logger.warning(f"Frame grab failed: {e}")
            return

        if rects:
            logger.debug(f"Damage rects ({len(rects)}): {rects}")

        if not self._running:
            return

        # -------------------------------------------------------------------------
        # 2. Handle OSD expiry (auto‑hide after duration)
        # -------------------------------------------------------------------------
        self._update_osd_timer()

        # Force a redraw if the OSD just expired (to clear it from screen)
        if self._needs_osd_redraw:
            is_dirty = True
            self._needs_osd_redraw = False

        # Always update overlay window opacity (may change due to focus)
        self.overlay.update_opacity()

        # -------------------------------------------------------------------------
        # 3. If frame hasn't changed and no OSD update, skip GPU work
        # -------------------------------------------------------------------------
        if not is_dirty and self._osd_texture is None:
            # Just present the existing screen texture
            self._swapchain_manager.present(self._screen_tex)
            return

        # -------------------------------------------------------------------------
        # 4. Upload captured frame to staging buffer (CPU -> GPU)
        # -------------------------------------------------------------------------
        if self.config.use_damage_tracking and rects:
            upload_list = []
            stride = self.crop_width * 4
            for rx, ry, rw, rh in rects:
                # Extract sub-rectangle data from the full frame buffer
                sub_data = bytearray()
                for row in range(ry, ry + rh):
                    start = row * stride + rx * 4
                    sub_data.extend(frame[start : start + rw * 4])
                upload_list.append((bytes(sub_data), rx, ry, rw, rh))
            self.upscaler.input.upload_subresources(upload_list)
        else:
            self.upscaler.staging.upload(frame)

        # -------------------------------------------------------------------------
        # 5. Calculate Lanczos destination rectangle and update constants
        # -------------------------------------------------------------------------
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            self.src_w,
            self.src_h,
            self._content_width,
            self._content_height,
            self.scale_mode,
        )
        canvas_x = (self._screen_width - self._content_width) // 2
        canvas_y = (self._screen_height - self._content_height) // 2
        dst_x = canvas_x + r_x + self.config.offset_x
        dst_y = canvas_y + r_y + self.config.offset_y
        dst_w, dst_h = r_w, r_h

        if dst_w <= 0 or dst_h <= 0:
            logger.debug(f"Skipping Lanczos dispatch – invalid rect: {dst_w}x{dst_h}")
            self._swapchain_manager.present(self._screen_tex)
            return

        self.lanczos_scaler.update_constants(
            self._background_color,
            self.upscaler.output.width,
            self.upscaler.output.height,
            self._screen_width,
            self._screen_height,
            dst_x,
            dst_y,
            r_w,
            r_h,
            1.0,  # blur factor
        )

        # -------------------------------------------------------------------------
        # 6. Build the list of compute dispatches for this frame
        # -------------------------------------------------------------------------
        dispatches = []

        # ---- SRCNN upscale passes (first stage) ----
        w, h = self.upscaler._first_in_w, self.upscaler._first_in_h
        for i, pipe in enumerate(self.upscaler.pipelines_first):
            last = i == self.upscaler.cfg["passes"] - 1
            gx, gy = dispatch_groups(w, h, last)
            dispatches.append((pipe, gx, gy, 1, None))

        # ---- SRCNN second stage (if double upscale enabled) ----
        if self.double_upscale:
            w2, h2 = self.upscaler._second_in_w, self.upscaler._second_in_h
            for i, pipe in enumerate(self.upscaler.pipelines_second):
                last = i == self.upscaler.cfg["passes"] - 1
                gx, gy = dispatch_groups(w2, h2, last)
                dispatches.append((pipe, gx, gy, 1, None))

        # ---- Lanczos scaling pass ----
        dispatches.append(
            (self.lanczos_scaler.compute, self._groups_x, self._groups_y, 1, None)
        )

        # ---- OSD blend pass (if OSD is active) ----
        if self._osd_texture is not None:
            # Update OSD constant buffer with position and size
            osd_w = self._osd_texture.width
            osd_h = self._osd_texture.height
            osd_x = (self._screen_width - osd_w) // 2
            osd_y = (self._screen_height - osd_h) // 2

            # The OverlayBlender uses a CBV with four ints: x, y, w, h
            cb_data = struct.pack("iiii", osd_x, osd_y, osd_w, osd_h)
            self._overlay_blender.cb.upload(cb_data)

            # Create (or reuse) the compute pipeline for this specific OSD texture.
            # Since the OSD texture changes rarely, we can recreate the pipeline
            # each time; it's lightweight and only happens when OSD is shown.
            osd_compute = Compute(
                self._overlay_blender.shader,
                srv=[self._screen_tex, self._osd_texture],
                uav=[self._screen_tex],
                cbv=[self._overlay_blender.cb],
                samplers=[self._overlay_blender.sampler],
            )

            # Dispatch enough groups to cover the OSD rectangle (16x16 threads)
            groups_x = (osd_w + 15) // 16
            groups_y = (osd_h + 15) // 16
            dispatches.append((osd_compute, groups_x, groups_y, 1, None))

        # -------------------------------------------------------------------------
        # 7. Submit EVERYTHING in one Vulkan command buffer
        # -------------------------------------------------------------------------
        if self.config.use_damage_tracking and rects:
            # Damage upload was done directly; skip the copy stage
            copy_src = None
        else:
            copy_src = self.upscaler.staging

        self.upscaler.pipelines_first[0].dispatch_sequence(
            sequence=dispatches,
            copy_src=copy_src,
            copy_dst=self.upscaler.input,
            present_image=self._screen_tex,
        )

        # -------------------------------------------------------------------------
        # 8. Present the screen texture (no extra GPU work, layout already correct)
        # -------------------------------------------------------------------------
        self._swapchain_manager.present(self._screen_tex, wait_for_fence=False)

        # -------------------------------------------------------------------------
        # 9. Update mouse mapping rectangle for overlay interaction
        # -------------------------------------------------------------------------
        self.overlay.scaling_rect = [
            dst_x / self._scale_factor,
            dst_y / self._scale_factor,
            dst_w / self._scale_factor,
            dst_h / self._scale_factor,
        ]

        # -------------------------------------------------------------------------
        # 10. Check if swapchain needs recreation (e.g., window resized)
        # -------------------------------------------------------------------------
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

        self.overlay.set_target_handle(self._win_info.handle)
        self.overlay.set_target_size(self._win_info.width, self._win_info.height)

        # Recompute crop dimensions
        self.crop_width = self._win_info.width - self._crop_left - self._crop_right
        self.crop_height = self._win_info.height - self._crop_top - self._crop_bottom
        self.overlay.set_crop(
            self._crop_left, self._crop_top, self.crop_width, self.crop_height
        )

        # Update content dimensions (depends on crop and overlay size)
        self.update_content_dimensions()

        # Update source dimensions after upscaling
        self.src_w = self.crop_width * (4 if self.double_upscale else 2)
        self.src_h = self.crop_height * (4 if self.double_upscale else 2)
        logger.debug(f"New src dimensions: {self.src_w}x{self.src_h}")

        # Recreate upscaler with new crop size
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=self.model_name,
            double_upscale=self.double_upscale,
        )
        self.lanczos_scaler.set_source_texture(self.upscaler.output)

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
        new_width = self.overlay.width()
        new_height = self.overlay.height()

        if new_width != self._screen_width or new_height != self._screen_height:
            self._screen_width = new_width
            self._screen_height = new_height
            self._screen_tex = Texture2D(new_width, new_height, format=R8G8B8A8_UNORM)
            self._groups_x = (new_width + 15) // 16
            self._groups_y = (new_height + 15) // 16
            self.lanczos_scaler.set_target_texture(self._screen_tex)
            self.update_content_dimensions()

        logger.debug(
            f"Recreating swapchain: "
            f"old size {self._screen_width}x{self._screen_height} "
            f"-> new size {new_width}x{new_height}"
        )
        self._swapchain_manager.recreate(self._screen_width, self._screen_height)

    def update_content_dimensions(self) -> None:
        """Recalculate content dimensions based on current overlay size and crop."""
        overlay_w = self.overlay.width()
        overlay_h = self.overlay.height()
        new_content_w, new_content_h, _, _, _ = parse_output_geometry(
            self.output_geometry,
            self.crop_width,
            self.crop_height,
            overlay_w,
            overlay_h,
        )
        logger.debug(
            f"Content dimensions updated: "
            f"{self._content_width}x{self._content_height} "
            f"-> {new_content_w}x{new_content_h}, "
            f"mode={self.scale_mode}"
        )
        if (
            new_content_w != self._content_width
            or new_content_h != self._content_height
        ):
            self._content_width = new_content_w
            self._content_height = new_content_h
            self.overlay.set_content_dimensions(new_content_w, new_content_h)

    def _switch_target(self, new_win_info: WindowInfo) -> None:
        """Switch the pipeline to a new target window."""
        logger.info(
            f"Switching pipeline to new window: {new_win_info.title} ({new_win_info.width}x{new_win_info.height})"
        )

        # Test if the window is alive
        test_tracker = WindowTracker(
            new_win_info.handle, new_win_info.width, new_win_info.height
        )
        test_tracker.update(force=True)
        if not test_tracker.alive:
            logger.warning(
                f"New window {new_win_info.handle} is not alive, ignoring switch"
            )
            test_tracker.close()
            return

        # Close old tracker and replace
        self._window_tracker.close()
        self._window_tracker = test_tracker
        self._win_info = new_win_info

        # Force a full update of all resources
        self._handle_window_change(force=True)

        # Update overlay with new target info
        self.overlay.set_target_handle(new_win_info.handle)
        self.overlay.set_target_size(new_win_info.width, new_win_info.height)

        logger.info(f"Successfully switched to window {new_win_info.handle}")

    def request_switch(self, new_win_info: WindowInfo) -> None:
        self._switch_queue.put(new_win_info)
