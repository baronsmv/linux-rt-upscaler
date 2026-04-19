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
        logger.debug(
            f"set_target_texture called: tex={id(tex)} {tex.width}x{tex.height}"
        )
        if tex is self._dst_tex and self.compute is not None:
            logger.debug("Texture unchanged and compute exists, skipping")
            return

        if self._src_tex is None:
            logger.error("Source texture is None – cannot create Lanczos pipeline")
            self.compute = None
            return

        if self._shader is None:
            logger.critical("Shader not loaded")
            self.compute = None
            return

        logger.debug(f"Source texture: {self._src_tex.width}x{self._src_tex.height}")

        tex_id = id(tex)
        if tex_id in self._compute_cache:
            self.compute = self._compute_cache[tex_id]
            self._dst_tex = tex
            logger.debug(f"Using cached compute for tex id={tex_id}")
            return

        logger.info(
            f"Creating new Lanczos compute pipeline for tex {tex.width}x{tex.height}"
        )
        # Temporarily remove try/except to let the exception propagate
        self.compute = Compute(
            self._shader,
            srv=[self._src_tex],
            uav=[tex],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        self._compute_cache[tex_id] = self.compute
        self._dst_tex = tex
        self._dst_width = tex.width
        self._dst_height = tex.height
        logger.info("Lanczos compute pipeline created successfully")

    def update_constants(self, background_color, *args) -> None:
        self._push_data = struct.pack(CB_FORMAT, *background_color, *args)
        self._cb.upload(self._push_data)
