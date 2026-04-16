import logging
import os
import struct

from ..vulkan import (
    Buffer,
    Compute,
    Sampler,
    Texture2D,
    HEAP_UPLOAD,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_FILTER_POINT,
)

logger = logging.getLogger(__name__)

# Constant buffer layout: 4 floats (bgColor), 4 uint, 4 int, 1 float (blur)
CB_FORMAT = "ffffIIIIiiiif"
CB_SIZE = struct.calcsize(CB_FORMAT)

# Shaders directory
SHADERS_DIR = os.path.dirname(__file__)


class LanczosScaler:
    """
    Handles the Lanczos scaling pass: dispatches compute shader to scale
    the upscaled texture to the screen texture.
    """

    def __init__(self, shader_path: str = os.path.join(SHADERS_DIR, "lanczos2.spv")):
        self.shader_path = shader_path
        self._shader = None
        self._push_data = b""
        self.compute = None
        self._sampler = None
        self._cb = None

        self._src_tex = None
        self._src_width = 0
        self._src_height = 0
        self._src_format = None
        self._dst_tex = None
        self._dst_width = 0
        self._dst_height = 0
        self._dst_format = None

        self._load_shader()
        self._create_resources()

    def _load_shader(self):
        with open(self.shader_path, "rb") as f:
            self._shader = f.read()

    def _create_resources(self):
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self._cb = Buffer(CB_SIZE, heap_type=HEAP_UPLOAD)
        logger.debug("Lanczos scaler resources created.")

    def set_source_texture(self, tex: Texture2D) -> None:
        if (
            tex is self._src_tex
            and tex.width == self._src_width
            and tex.height == self._src_height
        ):
            return
        self._src_tex = tex
        self._src_width = tex.width
        self._src_height = tex.height
        self._rebuild_compute()

    def set_target_texture(self, tex: Texture2D) -> None:
        if (
            tex is self._dst_tex
            and tex.width == self._dst_width
            and tex.height == self._dst_height
        ):
            return
        self._dst_tex = tex
        self._dst_width = tex.width
        self._dst_height = tex.height
        self._rebuild_compute()

    def update_constants(self, background_color, *args) -> None:
        self._push_data = struct.pack(CB_FORMAT, *background_color, *args)
        self._cb.upload(self._push_data)

    def _rebuild_compute(self):
        if self._src_tex is None or self._dst_tex is None:
            return
        self.compute = Compute(
            self._shader,
            srv=[self._src_tex],
            uav=[self._dst_tex],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        logger.debug("Lanczos compute object rebuilt.")
