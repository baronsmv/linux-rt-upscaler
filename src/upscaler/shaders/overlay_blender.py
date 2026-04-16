import logging
import os
import struct

from ..vulkan import (
    Buffer,
    Compute,
    Sampler,
    HEAP_UPLOAD,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_FILTER_POINT,
)

logger = logging.getLogger(__name__)

CB_SIZE = struct.calcsize("iiii")  # x, y, w, h

SHADERS_DIR = os.path.dirname(__file__)


class OverlayBlender:
    def __init__(
        self, shader_path: str = os.path.join(SHADERS_DIR, "overlay_blend.spv")
    ):
        self.shader_path = shader_path
        self.shader = None
        self.sampler = None
        self.cb = None
        self._screen_tex = None
        self._load_shader()
        self._create_resources()

    def _load_shader(self):
        with open(self.shader_path, "rb") as f:
            self.shader = f.read()

    def _create_resources(self):
        self.sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self.cb = Buffer(CB_SIZE, heap_type=HEAP_UPLOAD)
        logger.debug("OverlayBlender resources created.")

    def set_screen_texture(self, tex):
        self._screen_tex = tex

    def blend(self, overlay_tex, x: int, y: int, w: int, h: int):
        if self._screen_tex is None:
            return

        # Recreate compute pipeline with both textures (no bindless needed)
        compute = Compute(
            self.shader,
            srv=[self._screen_tex, overlay_tex],
            uav=[self._screen_tex],
            cbv=[self.cb],
            samplers=[self.sampler],
            push_size=0,
        )

        # Upload position/size constants
        cb_data = struct.pack("iiii", x, y, w, h)
        self.cb.upload(cb_data)

        groups_x = (w + 15) // 16
        groups_y = (h + 15) // 16
        compute.dispatch(groups_x, groups_y, 1)
