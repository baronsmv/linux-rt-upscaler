"""
CuNNy‑veryfast 2× upscaler using Compushady.
Loads four HLSL shaders from files and manages GPU resources.
"""

import os
import struct

from compushady import (
    Compute,
    Buffer,
    Texture2D,
    HEAP_UPLOAD,
    Sampler,
    SAMPLER_FILTER_POINT,
    SAMPLER_FILTER_LINEAR,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_ADDRESS_MODE_WRAP,
)
from compushady.formats import R8G8B8A8_UNORM, get_pixel_size
from compushady.shaders import hlsl


class SRCNN:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._load_shaders()
        self._create_resources()
        self._create_pipelines()

    def _load_shaders(self):
        """Load HLSL shader source from files."""
        shader_dir = os.path.dirname(__file__)
        with open(os.path.join(shader_dir, "CuNNy-veryfast-NVL_Pass1.hlsl"), "r") as f:
            self.shader1 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "CuNNy-veryfast-NVL_Pass2.hlsl"), "r") as f:
            self.shader2 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "CuNNy-veryfast-NVL_Pass3.hlsl"), "r") as f:
            self.shader3 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "CuNNy-veryfast-NVL_Pass4.hlsl"), "r") as f:
            self.shader4 = hlsl.compile(f.read())

    def _create_resources(self):
        w, h = self.width, self.height
        # Input and output textures
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)  # 2× upscaled

        # Staging buffer for uploading pixel data from CPU
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)

        # Intermediate textures (used by the network)
        self.t0 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t1 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t2 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t3 = Texture2D(w, h, R8G8B8A8_UNORM)

        # Constant buffers (contain dimensions and scale factors)
        def cb_data(w, h, out_w, out_h):
            return struct.pack(
                "iiii ffffff",
                w,
                h,
                out_w,
                out_h,
                1.0 / w,
                1.0 / h,
                1.0 / out_w,
                1.0 / out_h,
                1.0,
                1.0,
            )

        self.cb1 = Buffer(40, HEAP_UPLOAD)
        self.cb1.upload(cb_data(w, h, w, h))

        self.cb2 = Buffer(40, HEAP_UPLOAD)
        self.cb2.upload(cb_data(w, h, w, h))

        self.cb3 = Buffer(40, HEAP_UPLOAD)
        self.cb3.upload(cb_data(w, h, w, h))

        self.cb4 = Buffer(40, HEAP_UPLOAD)
        self.cb4.upload(cb_data(w, h, w * 2, h * 2))

        # Samplers (point and linear)
        self.sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_WRAP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self.sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
            address_mode_u=SAMPLER_ADDRESS_MODE_WRAP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )

    def _create_pipelines(self):
        """Create compute pipelines for the four passes (reusable)."""
        self.pass1 = Compute(
            self.shader1,
            cbv=[self.cb1],
            srv=[self.input],
            uav=[self.t0, self.t1],
            samplers=[self.sampler_point, self.sampler_linear],
        )
        self.pass2 = Compute(
            self.shader2,
            cbv=[self.cb2],
            srv=[self.t0, self.t1],
            uav=[self.t2, self.t3],
            samplers=[self.sampler_point, self.sampler_linear],
        )
        self.pass3 = Compute(
            self.shader3,
            cbv=[self.cb3],
            srv=[self.t2, self.t3],
            uav=[self.t0],
            samplers=[self.sampler_point, self.sampler_linear],
        )
        self.pass4 = Compute(
            self.shader4,
            cbv=[self.cb4],
            srv=[self.input, self.t0],
            uav=[self.output],
            samplers=[self.sampler_point, self.sampler_linear],
        )

    def upload(self, data):
        """
        Copy raw RGBX data (as bytes or memoryview) into the input texture.
        data: must be a contiguous buffer of size width*height*4.
        """
        self.staging.upload2d(
            data,
            self.input.row_pitch,
            self.input.width,
            self.input.height,
            get_pixel_size(R8G8B8A8_UNORM),
        )
        self.staging.copy_to(self.input)

    def compute(self):
        """Execute the four CuNNy passes."""
        w, h = self.width, self.height
        self.pass1.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        self.pass2.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        self.pass3.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        self.pass4.dispatch((w * 2 + 15) // 16, (h * 2 + 15) // 16, 1)

    def _init_lanczos(self):
        """Lazy initialisation of Lanczos scaling resources."""
        if hasattr(self, "_lanczos_pipeline"):
            return
        shader_dir = os.path.dirname(__file__)
        with open(os.path.join(shader_dir, "lanczos2.hlsl"), "r") as f:
            self._lanczos_shader = hlsl.compile(f.read())

        self._lanczos_sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        # Constant buffer will be updated per call, so we just create a placeholder.
        self._lanczos_cb = Buffer(20, HEAP_UPLOAD)  # 5 * 4 bytes (4 uint + 1 float)

    def scale_to(self, target_tex, target_width, target_height, blur=1.0):
        """
        Scale the internal 2× upscaled texture (self.output) to `target_tex`
        using Lanczos2+antiring, preserving aspect ratio and centering.
        `target_tex` must be a Texture2D of size (target_width, target_height).
        """
        self._init_lanczos()

        # Update constant buffer with current dimensions and blur
        cb_data = struct.pack(
            "IIIIf",
            self.width * 2,  # input width  (upscaled)
            self.height * 2,  # input height (upscaled)
            target_width,
            target_height,
            blur,
        )
        self._lanczos_cb.upload(cb_data)

        # Create or recreate the compute pipeline if the target size changed
        groups_x = (target_width + 15) // 16
        groups_y = (target_height + 15) // 16

        # The pipeline uses self.output as SRV, target_tex as UAV
        self._lanczos_pipeline = Compute(
            self._lanczos_shader,
            srv=[self.output],
            uav=[target_tex],
            cbv=[self._lanczos_cb],
            samplers=[self._lanczos_sampler],
        )

        self._lanczos_pipeline.dispatch(groups_x, groups_y, 1)
