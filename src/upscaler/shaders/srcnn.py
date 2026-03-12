"""
CuNNy upscaler using Compushady.
Supports multiple models (veryfast, fast). Loads four HLSL shaders from files.
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
)
from compushady.formats import R8G8B8A8_UNORM, get_pixel_size
from compushady.shaders import hlsl


class SRCNN:
    def __init__(self, width, height, model="fast"):
        self.width = width
        self.height = height
        self.model = model
        self._load_shaders()
        self._create_resources()
        self._create_pipelines()

    def _load_shaders(self):
        """Load HLSL shader source from files."""
        # Directory structure: shaders/CuNNy/<model>/Pass*.hlsl
        shader_dir = os.path.join(os.path.dirname(__file__), "CuNNy", self.model)

        with open(os.path.join(shader_dir, "Pass1.hlsl"), "r") as f:
            self.shader1 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "Pass2.hlsl"), "r") as f:
            self.shader2 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "Pass3.hlsl"), "r") as f:
            self.shader3 = hlsl.compile(f.read())
        with open(os.path.join(shader_dir, "Pass4.hlsl"), "r") as f:
            self.shader4 = hlsl.compile(f.read())

    def _pack_cb(self, in_w, in_h, out_w, out_h):
        """Pack constant buffer data for the shaders."""
        return struct.pack(
            "IIIIffff",
            in_w,
            in_h,
            out_w,
            out_h,
            1.0 / in_w,
            1.0 / in_h,  # inputPt
            1.0 / out_w,
            1.0 / out_h,  # outputPt (only used in pass4)
        )

    def _create_resources(self):
        w, h = self.width, self.height

        # Input and output textures
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)  # 2× upscaled

        # Staging buffer for CPU uploads
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)

        # Intermediate textures – the fast model needs 6 of them
        self.t0 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t1 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t2 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t3 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t4 = Texture2D(w, h, R8G8B8A8_UNORM)
        self.t5 = Texture2D(w, h, R8G8B8A8_UNORM)

        # Constant buffers – one per pass
        cb_size = struct.calcsize("IIIIffff")  # 32 bytes
        self.cb1 = Buffer(cb_size, HEAP_UPLOAD)
        self.cb1.upload(self._pack_cb(w, h, w, h))  # pass1: output size = input size

        self.cb2 = Buffer(cb_size, HEAP_UPLOAD)
        self.cb2.upload(self._pack_cb(w, h, w, h))  # pass2: same

        self.cb3 = Buffer(cb_size, HEAP_UPLOAD)
        self.cb3.upload(self._pack_cb(w, h, w, h))  # pass3: same

        self.cb4 = Buffer(cb_size, HEAP_UPLOAD)
        self.cb4.upload(self._pack_cb(w, h, w * 2, h * 2))  # pass4: output 2x

        # Samplers
        self.sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,  # clamp for safe sampling
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self.sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )

    def _create_pipelines(self):
        """Create compute pipelines for the four passes."""
        # Pass1: input -> t0, t1, t2
        self.pass1 = Compute(
            self.shader1,
            cbv=[self.cb1],
            srv=[self.input],
            uav=[self.t0, self.t1, self.t2],
            samplers=[self.sampler_point],  # only point sampler needed
        )

        # Pass2: t0, t1, t2 -> t3, t4, t5
        self.pass2 = Compute(
            self.shader2,
            cbv=[self.cb2],
            srv=[self.t0, self.t1, self.t2],
            uav=[self.t3, self.t4, self.t5],
            samplers=[self.sampler_point],
        )

        # Pass3: t3, t4, t5 -> t0, t1
        self.pass3 = Compute(
            self.shader3,
            cbv=[self.cb3],
            srv=[self.t3, self.t4, self.t5],
            uav=[self.t0, self.t1],
            samplers=[self.sampler_point],
        )

        # Pass4: input + t0, t1 -> output
        # This pass uses both samplers: point for t0/t1, linear for original input
        self.pass4 = Compute(
            self.shader4,
            cbv=[self.cb4],
            srv=[self.input, self.t0, self.t1],
            uav=[self.output],
            samplers=[self.sampler_point, self.sampler_linear],
        )

    def upload(self, data):
        """
        Copy raw RGBX data into the input texture.
        data: contiguous buffer of size width*height*4.
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
        # Passes 1‑3: input-sized dispatch (8×8 threads per group)
        self.pass1.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        self.pass2.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        self.pass3.dispatch((w + 7) // 8, (h + 7) // 8, 1)
        # Pass4: output-sized dispatch, each group covers 16×16 output pixels
        self.pass4.dispatch((w * 2 + 15) // 16, (h * 2 + 15) // 16, 1)

    def _init_lanczos(self):
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
        self._lanczos_cb = Buffer(20, HEAP_UPLOAD)  # 5 * 4 bytes

    def scale_to(self, target_tex, target_width, target_height, blur=1.0):
        self._init_lanczos()
        cb_data = struct.pack(
            "IIIIf",
            self.width * 2,
            self.height * 2,
            target_width,
            target_height,
            blur,
        )
        self._lanczos_cb.upload(cb_data)
        groups_x = (target_width + 15) // 16
        groups_y = (target_height + 15) // 16
        self._lanczos_pipeline = Compute(
            self._lanczos_shader,
            srv=[self.output],
            uav=[target_tex],
            cbv=[self._lanczos_cb],
            samplers=[self._lanczos_sampler],
        )
        self._lanczos_pipeline.dispatch(groups_x, groups_y, 1)
