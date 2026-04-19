import logging
import threading
import time
from queue import Empty, Queue, Full
from typing import Optional, Tuple

from PySide6.QtCore import QMetaObject, Qt

from .controller import PipelineController
from .osd import OSDManager
from .swapchain import SwapchainManager
from ..capture import FrameGrabber
from ..config import Config, OverlayMode, OUTPUT_GEOMETRIES, UPSCALING_MODELS
from ..overlay import OverlayWindow
from ..shaders import LanczosScaler, SRCNN, dispatch_groups
from ..utils import parse_output_geometry, calculate_scaling_rect
from ..vulkan import Texture2D, configure_device, create_fence, device_wait_idle
from ..window import WindowInfo, WindowTracker

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
        self.tile_size = config.tile_size
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
        configure_device(self.config.vulkan_buffer_pool_size)
        self._swapchain_manager = SwapchainManager(
            overlay.xid,
            self._screen_width,
            self._screen_height,
            present_mode=self.config.vulkan_present_mode,
        )

        # Upscaler
        self.upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=self.model_name,
            double_upscale=self.double_upscale,
            tile_size=self.tile_size,
        )

        # Async
        self._async_enabled = config.async_pipeline
        self._async_buffer_count = config.async_buffer_count
        self._idle_frame_counter = 0

        if self._async_enabled:
            self._screen_textures = []
            self._texture_fences = []
            for _ in range(self._async_buffer_count):
                tex = Texture2D(self._screen_width, self._screen_height)
                self._screen_textures.append(tex)
                # Create fence in signaled state
                fence = create_fence(signaled=True)
                self._texture_fences.append(fence)
            self._current_tex_idx = 0
            self._present_tex_idx = None
            self._lanczos_target = self._screen_textures[0]
        else:
            self._screen_tex = Texture2D(self._screen_width, self._screen_height)
            self._lanczos_target = self._screen_tex

        # Lanczos scaler
        self.lanczos_scaler = LanczosScaler()
        self.lanczos_scaler.set_source_texture(self.upscaler.output)
        self.lanczos_scaler.set_target_texture(self._lanczos_target)

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
        osd_texts = tuple(
            [f"Model: {m}" for m in UPSCALING_MODELS]
            + [f"Geometry: {g}" for g in OUTPUT_GEOMETRIES]
            + ["Screenshot saved", "Screenshot failed"]
        )
        self.osd = OSDManager(osd_texts, self._screen_width, self._screen_height)
        device_wait_idle()
        self.osd.prepare_textures()

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
        except Full:
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

    def create_grabber(self):
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
                tile_size=self.tile_size,
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
        self.create_grabber()

        while self._running:
            try:
                # Process switch requests
                new_win = None
                try:
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
                    self.osd.show(text, duration)
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

    def _expand_damage_rects(self, rects):
        margin = self.config.tile_context_margin
        expanded = []
        for rx, ry, rw, rh, _ in rects:
            ex0 = max(0, rx - margin)
            ey0 = max(0, ry - margin)
            ex1 = min(self.crop_width, rx + rw + margin)
            ey1 = min(self.crop_height, ry + rh + margin)
            if ex1 > ex0 and ey1 > ey0:
                expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))
        return expanded

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
            logger.error(f"grab() exception: {e}", exc_info=True)
            return

        if not self._running:
            return

        # -------------------------------------------------------------------------
        # 2. Update OSD state and get active texture
        # -------------------------------------------------------------------------
        osd_texture, needs_redraw = self.osd.update()
        if needs_redraw:
            is_dirty = True

        # Always update overlay window opacity (may change due to focus)
        self.overlay.update_opacity()

        # -------------------------------------------------------------------------
        # 3. If frame hasn't changed and no OSD update, decide whether to render
        # -------------------------------------------------------------------------
        if not is_dirty and osd_texture is None:
            if self._async_enabled:
                self._idle_frame_counter += 1
                if self._idle_frame_counter >= self._async_buffer_count:
                    # Render this frame (dispatches only, no upload)
                    self._idle_frame_counter = 0
                    is_dirty = False  # will skip upload later
                    # fall through to rendering
                else:
                    # Present the last frame and return
                    present_tex = self._screen_textures[self._present_tex_idx or 0]
                    self._swapchain_manager.present(present_tex, wait_for_fence=False)
                    return
            else:
                # Synchronous mode: nothing to do
                self._swapchain_manager.present(self._screen_tex, wait_for_fence=False)
                return
        else:
            # Frame is dirty or OSD active → reset counter
            self._idle_frame_counter = 0

        # -------------------------------------------------------------------------
        # 4. Upload captured frame (only if actually dirty)
        # -------------------------------------------------------------------------
        upload_performed = False
        if is_dirty:
            try:
                if self.config.use_damage_tracking and rects:
                    upload_list = []
                    stride = self.crop_width * 4
                    for ex, ey, ew, eh in self._expand_damage_rects(rects):
                        sub_data = bytearray()
                        for row in range(ey, ey + eh):
                            start = row * stride + ex * 4
                            sub_data.extend(frame[start : start + ew * 4])
                        upload_list.append((bytes(sub_data), ex, ey, ew, eh))
                    self.upscaler.input.upload_subresources(upload_list)
                    upload_performed = (
                        True  # subresource upload, no staging buffer needed later
                    )
                else:
                    self.upscaler.staging.upload(frame)
                    upload_performed = True  # staging buffer contains the full frame
            except Exception as e:
                logger.error(f"Frame upload failed: {e}", exc_info=True)
                return

        # -------------------------------------------------------------------------
        # 5. Choose target screen texture for this frame
        # -------------------------------------------------------------------------
        if self._async_enabled:
            logger.debug(
                f"Writing to tex idx={self._current_tex_idx}, presenting idx={self._present_tex_idx}"
            )
            next_idx = (self._current_tex_idx + 1) % self._async_buffer_count
            target_tex = self._screen_textures[next_idx]
            target_fence = self._texture_fences[next_idx]

            # Wait until GPU has finished with this texture
            target_fence.wait()
            target_fence.reset()

            # Update Lanczos target
            self.lanczos_scaler.set_target_texture(target_tex)
            self._current_tex_idx = next_idx
        else:
            target_tex = self._screen_tex

        # -------------------------------------------------------------------------
        # 6. Calculate Lanczos destination rectangle and update constants
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
            if self._async_enabled:
                present_tex = self._screen_textures[self._present_tex_idx or 0]
            else:
                present_tex = target_tex
            self._swapchain_manager.present(present_tex, wait_for_fence=False)
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
            1.0,
        )

        # -------------------------------------------------------------------------
        # 7. Build the list of compute dispatches for this frame
        # -------------------------------------------------------------------------
        dispatches = []

        # SRCNN first stage
        w, h = self.upscaler._first_in_w, self.upscaler._first_in_h
        for i, pipe in enumerate(self.upscaler.pipelines_first):
            last = i == self.upscaler.cfg["passes"] - 1
            gx, gy = dispatch_groups(w, h, last)
            dispatches.append((pipe, gx, gy, 1, b""))

        # SRCNN second stage
        if self.double_upscale:
            w2, h2 = self.upscaler._second_in_w, self.upscaler._second_in_h
            for i, pipe in enumerate(self.upscaler.pipelines_second):
                last = i == self.upscaler.cfg["passes"] - 1
                gx, gy = dispatch_groups(w2, h2, last)
                dispatches.append((pipe, gx, gy, 1, b""))

        # Lanczos scaling pass
        dispatches.append(
            (self.lanczos_scaler.compute, self._groups_x, self._groups_y, 1, b"")
        )

        # OSD blend pass (if OSD is active)
        if osd_texture is not None:
            osd_w = osd_texture.width
            osd_h = osd_texture.height
            osd_x = (self._screen_width - osd_w) // 2
            osd_y = (self._screen_height - osd_h) // 2

            self.osd.update_constants(osd_x, osd_y, osd_w, osd_h)
            osd_compute = self.osd.get_compute_pipeline(osd_texture, target_tex)

            groups_x = (osd_w + 15) // 16
            groups_y = (osd_h + 15) // 16
            dispatches.append((osd_compute, groups_x, groups_y, 1, b""))

        # -------------------------------------------------------------------------
        # 8. Submit all GPU work with proper synchronization
        # -------------------------------------------------------------------------
        if upload_performed and self.config.use_damage_tracking and rects:
            # Subresource upload was used → no staging buffer copy needed
            copy_src = None
        elif upload_performed:
            # Full frame uploaded via staging → copy from staging buffer
            copy_src = self.upscaler.staging
        else:
            # Forced render (idle) → no upload, skip copy
            copy_src = None

        if self._async_enabled:
            # Use a fence to signal
            logger.debug(f"Fence for tex {next_idx}: handle = {target_fence.handle}")
            try:
                self.upscaler.pipelines_first[0].dispatch_sequence(
                    sequence=dispatches,
                    copy_src=copy_src,
                    copy_dst=self.upscaler.input,
                    present_image=None,  # we handle presentation separately
                    fence=target_fence,
                    wait_for_fence=False,  # don't wait inside
                )
                # Optional: wait a tiny bit for the GPU to start
                time.sleep(0.001)
                if target_fence.is_signaled():
                    logger.debug(f"Fence for tex {next_idx} signaled quickly")
            except Exception as e:
                logger.error(f"dispatch_sequence failed: {e}", exc_info=True)
                return
        else:
            # Synchronous path: present_image = target_tex, wait inside
            try:
                self.upscaler.pipelines_first[0].dispatch_sequence(
                    sequence=dispatches,
                    copy_src=copy_src,
                    copy_dst=self.upscaler.input,
                )
            except Exception as e:
                logger.error(f"dispatch_sequence failed: {e}", exc_info=True)
                return

        if self._frame_count % 60 == 0:  # every ~1 second at 60fps
            with open(f"/home/mau/frame_{self._frame_count}.raw", "wb") as f:
                f.write(frame.tobytes())

        # -------------------------------------------------------------------------
        # 9. Present the appropriate texture
        # -------------------------------------------------------------------------
        if self._async_enabled:
            # On first frame, we haven't rendered anything yet; present the first texture (empty)
            if self._present_tex_idx is None:
                self._present_tex_idx = 0
            else:
                # Present the texture that is at least one frame old (guaranteed to be idle)
                self._present_tex_idx = (
                    self._current_tex_idx - 1
                ) % self._async_buffer_count
            present_tex = self._screen_textures[self._present_tex_idx]
        else:
            present_tex = target_tex

        self._swapchain_manager.present(present_tex, wait_for_fence=False)

        # -------------------------------------------------------------------------
        # 10. Update mouse mapping and check swapchain
        # -------------------------------------------------------------------------
        self.overlay.scaling_rect = [
            dst_x / self._scale_factor,
            dst_y / self._scale_factor,
            dst_w / self._scale_factor,
            dst_h / self._scale_factor,
        ]

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
            tile_size=self.tile_size,
        )
        self.lanczos_scaler.set_source_texture(self.upscaler.output)

        # Recreate grabber with new window handle and crop
        self.create_grabber()

        # Clear the frame queue to avoid using old frames
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except Empty:
                break

        logger.info("Window change handled successfully")

    def _recreate_swapchain(self):
        new_width = self.overlay.width()
        new_height = self.overlay.height()
        if new_width != self._screen_width or new_height != self._screen_height:
            self._screen_width = new_width
            self._screen_height = new_height
            self._groups_x = (new_width + 15) // 16
            self._groups_y = (new_height + 15) // 16

            if self._async_enabled:
                for i in range(self._async_buffer_count):
                    self._screen_textures[i] = Texture2D(new_width, new_height)
                    # Recreate fence (old one will be garbage‑collected)
                    self._texture_fences[i] = create_fence(signaled=True)
                self._lanczos_target = self._screen_textures[self._current_tex_idx]
                self._present_tex_idx = None  # reset on resize
            else:
                self._screen_tex = Texture2D(new_width, new_height)
                self._lanczos_target = self._screen_tex

            self.lanczos_scaler.set_target_texture(self._lanczos_target)
            self.update_content_dimensions()

        self._swapchain_manager.recreate(self._screen_width, self._screen_height)
        self.osd.clear_compute_cache()

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
