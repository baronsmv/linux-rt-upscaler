import os
import struct
import threading
import time
from queue import Queue, Empty

from PySide6.QtGui import QCursor
from Xlib.display import Display
from compushady import (
    Compute,
    Buffer,
    Texture2D,
    Sampler,
    HEAP_UPLOAD,
    SAMPLER_FILTER_POINT,
    SAMPLER_ADDRESS_MODE_CLAMP,
)
from compushady.formats import R8G8B8A8_UNORM
from compushady.shaders import hlsl

from .capture.capture import FrameGrabber
from .shaders.srcnn import SRCNN


class Pipeline:
    def __init__(
        self, window_info, screen_width, screen_height, overlay, swapchain, map_clicks
    ):
        self.window_info = window_info
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.overlay = overlay
        self.swapchain = swapchain
        self.map_clicks = map_clicks

        # Create screen texture
        self.screen_tex = Texture2D(screen_width, screen_height, R8G8B8A8_UNORM)

        # Create upscaler (CuNNy)
        self.upscaler = SRCNN(window_info.width, window_info.height)

        # Load Lanczos shader
        shader_dir = os.path.dirname(__file__)
        with open(os.path.join(shader_dir, "shaders", "lanczos2.hlsl"), "r") as f:
            self.lanczos_shader = hlsl.compile(f.read())
        self.lanczos_sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        # Constant buffer (will be updated per frame)
        self.cb = Buffer(struct.calcsize("IIIIf"), HEAP_UPLOAD)

        # For click mapping rectangle
        self.overlay.scaling_rect = [0, 0, 0, 0]

        # Threading
        self.running = False
        self.thread = None
        self.frame_queue = Queue(maxsize=1)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.running = False
        # Unblock queue
        self.frame_queue.put(
            bytearray(self.window_info.width * self.window_info.height * 4)
        )
        if self.thread:
            self.thread.join()

    def _run(self):
        grabber = FrameGrabber(self.window_info)
        groups_x = (self.screen_width + 15) // 16
        groups_y = (self.screen_height + 15) // 16

        src_w = self.window_info.width * 2
        src_h = self.window_info.height * 2

        # For opacity control (if not mapping clicks)
        if not self.map_clicks:
            disp = Display()
            window = disp.create_resource_object("window", self.window_info.handle)

        while self.running:
            frame = grabber.grab()
            if not self.running:
                break
            self.frame_queue.put(frame)

            try:
                frame = self.frame_queue.get_nowait()
            except Empty:
                continue

            start_time = time.perf_counter()

            # CuNNy upscale
            self.upscaler.upload(frame)
            self.upscaler.compute()  # result in self.upscaler.output

            # Compute destination rectangle (for click mapping)
            src_aspect = src_w / src_h
            screen_aspect = self.screen_width / self.screen_height
            if src_aspect > screen_aspect:
                dst_w = self.screen_width
                dst_h = int(self.screen_width / src_aspect)
                dst_x = 0
                dst_y = (self.screen_height - dst_h) // 2
            else:
                dst_h = self.screen_height
                dst_w = int(self.screen_height * src_aspect)
                dst_x = (self.screen_width - dst_w) // 2
                dst_y = 0
            self.overlay.scaling_rect[:] = [dst_x, dst_y, dst_w, dst_h]

            # Lanczos scaling
            cb_data = struct.pack(
                "IIIIf",
                src_w,
                src_h,
                self.screen_width,
                self.screen_height,
                1.0,  # blur
            )
            self.cb.upload(cb_data)

            # Create or reuse compute pipeline
            scale_compute = Compute(
                self.lanczos_shader,
                srv=[self.upscaler.output],
                uav=[self.screen_tex],
                cbv=[self.cb],
                samplers=[self.lanczos_sampler],
            )
            scale_compute.dispatch(groups_x, groups_y, 1)

            compute_time = time.perf_counter() - start_time

            # Opacity control
            if self.map_clicks:
                self.overlay.setWindowOpacity(1.0)
            else:

                mouse = QCursor.pos()
                geom = window.get_geometry()
                trans = geom.root.translate_coords(window, 0, 0)
                win_x, win_y = trans.x, trans.y
                inside = (
                    win_x <= mouse.x() < win_x + self.window_info.width
                    and win_y <= mouse.y() < win_y + self.window_info.height
                )
                opacity = 1.0 if inside else 0.2
                self.overlay.setWindowOpacity(opacity)

            # Present
            self.swapchain.present(self.screen_tex)

        # Cleanup
        if not self.map_clicks:
            disp.close()
