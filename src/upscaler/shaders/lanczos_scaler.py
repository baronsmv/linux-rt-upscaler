import logging
import os
import struct
from typing import Dict, Optional

from ..vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

CB_FORMAT = "ffffIIIIiiiif"
CB_SIZE = struct.calcsize(CB_FORMAT)
SHADERS_DIR = os.path.dirname(__file__)


class LanczosScaler:
    def __init__(self, shader_path: str = os.path.join(SHADERS_DIR, "lanczos2.spv")):
        self.shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._push_data: bytes = b""
        self.compute: Optional[Compute] = None
        self._compute_cache: Dict[int, Compute] = {}
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None

        self._src_tex: Optional[Texture2D] = None
        self._src_width: int = 0
        self._src_height: int = 0

        self._dst_tex: Optional[Texture2D] = None
        self._dst_width: int = 0
        self._dst_height: int = 0

        self._load_shader()
        self._create_resources()

    def _load_shader(self) -> None:
        try:
            with open(self.shader_path, "rb") as f:
                self._shader = f.read()
            logger.debug(f"Loaded Lanczos shader: {len(self._shader)} bytes")
        except Exception as e:
            logger.critical(
                f"Failed to load Lanczos shader from {self.shader_path}: {e}"
            )
            raise

    def _create_resources(self) -> None:
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )
        self._cb = Buffer(CB_SIZE)
        logger.debug("Lanczos scaler resources created.")

    def set_source_texture(self, tex: Texture2D) -> None:
        """Update the input texture. Invalidates all cached pipelines."""
        if (
            tex is self._src_tex
            and tex.width == self._src_width
            and tex.height == self._src_height
        ):
            return
        self._src_tex = tex
        self._src_width = tex.width
        self._src_height = tex.height
        self._compute_cache.clear()
        self.compute = None
        logger.debug(
            f"Lanczos source texture updated to {tex.width}x{tex.height}, cache cleared"
        )

    def set_target_texture(self, tex: Texture2D) -> None:
        # Ignore texture changes – always use the first pipeline created
        self.count = 0
        if self.count > 2:
            return

        self.count += 1
        # Create once and never rebuild
        self.compute = Compute(
            self._shader,
            srv=[self._src_tex],
            uav=[tex],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        self._dst_tex = tex

    def update_constants(self, background_color, *args) -> None:
        self._push_data = struct.pack(CB_FORMAT, *background_color, *args)
        self._cb.upload(self._push_data)
