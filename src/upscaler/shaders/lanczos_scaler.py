import logging
import os
import struct
from typing import Optional, Tuple

from ..vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# Constant buffer layout: 4 floats (bgColor), 4 uint, 4 int, 1 float (blur)
CB_FORMAT = "ffffIIIIiiiif"
CB_SIZE = struct.calcsize(CB_FORMAT)

SHADERS_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(SHADERS_DIR, "lanczos2.spv")


class LanczosScaler:
    """
    Lanczos2 scaling via compute shader.

    Scales a source texture into a destination texture using the Lanczos2
    algorithm with optional anti‑ringing. The shader expects a constant buffer
    containing background color, source/destination dimensions, and rectangle.

    Attributes:
        source_texture (Texture2D | None): The input texture to scale.
        target_texture (Texture2D | None): The output texture to write to.
        source_width (int): Width of the source texture (0 if not set).
        source_height (int): Height of the source texture (0 if not set).
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        """
        Initialize the Lanczos scaler.

        Args:
            shader_path: Path to the compiled SPIR‑V shader.
        """
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None
        self._compute: Optional[Compute] = None

        self._src_tex: Optional[Texture2D] = None
        self._dst_tex: Optional[Texture2D] = None

        self._push_data: bytes = b""

        self._load_shader()
        self._create_resources()

    # ----------------------------------------------------------------------
    # Public properties
    # ----------------------------------------------------------------------
    @property
    def source_texture(self) -> Optional[Texture2D]:
        """The input texture to be scaled."""
        return self._src_tex

    @property
    def target_texture(self) -> Optional[Texture2D]:
        """The output texture to write scaled result to."""
        return self._dst_tex

    @property
    def source_width(self) -> int:
        """Width of the source texture, or 0 if not set."""
        return self._src_tex.width if self._src_tex else 0

    @property
    def source_height(self) -> int:
        """Height of the source texture, or 0 if not set."""
        return self._src_tex.height if self._src_tex else 0

    @property
    def compute(self) -> Optional[Compute]:
        """The compute pipeline (created when both textures are set)."""
        return self._compute

    # ----------------------------------------------------------------------
    # Initialisation
    # ----------------------------------------------------------------------
    def _load_shader(self) -> None:
        """Load SPIR‑V shader binary from disk."""
        with open(self._shader_path, "rb") as f:
            self._shader = f.read()
        logger.debug(f"Loaded Lanczos shader from {self._shader_path}")

    def _create_resources(self) -> None:
        """Create sampler and constant buffer (pipeline created later)."""
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )
        self._cb = Buffer(CB_SIZE)
        logger.debug("Lanczos scaler resources created")

    # ----------------------------------------------------------------------
    # Texture binding
    # ----------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Set the input texture to scale.

        If the texture changes, the compute pipeline is rebuilt.
        """
        if tex is self._src_tex:
            return
        self._src_tex = tex
        self._rebuild_compute()
        logger.debug(f"Lanczos source texture set: {tex.width}x{tex.height}")

    def set_target_texture(self, tex: Texture2D) -> None:
        """
        Set the output texture to write to.

        If the texture changes, the compute pipeline is rebuilt.
        """
        if tex is self._dst_tex:
            return
        self._dst_tex = tex
        self._rebuild_compute()
        logger.debug(f"Lanczos target texture set: {tex.width}x{tex.height}")

    def resize_target(self, width: int, height: int) -> None:
        """
        Resize the target texture (creates a new one and rebuilds pipeline).

        Args:
            width: New width in pixels.
            height: New height in pixels.
        """
        if (
            self._dst_tex
            and self._dst_tex.width == width
            and self._dst_tex.height == height
        ):
            return
        self._dst_tex = Texture2D(width, height)
        self._rebuild_compute()
        logger.debug(f"Lanczos target texture resized to {width}x{height}")

    # ----------------------------------------------------------------------
    # Constant buffer updates
    # ----------------------------------------------------------------------
    def update_constants(
        self,
        background_color: Tuple[float, float, float, float],
        src_width: int,
        src_height: int,
        dst_total_width: int,
        dst_total_height: int,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
        blur: float = 1.0,
    ) -> None:
        """
        Update the constant buffer with scaling parameters.

        Args:
            background_color: RGBA color used outside the scaled rectangle.
            src_width, src_height: Dimensions of the source texture.
            dst_total_width, dst_total_height: Dimensions of the target texture.
            dst_x, dst_y: Top‑left corner of the destination rectangle.
            dst_w, dst_h: Size of the destination rectangle.
            blur: Blur factor (1.0 = standard Lanczos2).
        """
        self._push_data = struct.pack(
            CB_FORMAT,
            *background_color,
            src_width,
            src_height,
            dst_total_width,
            dst_total_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
            blur,
        )
        self._cb.upload(self._push_data)
        logger.debug(
            f"Lanczos constants updated: dst={dst_w}x{dst_h} at ({dst_x},{dst_y})"
        )

    # ----------------------------------------------------------------------
    # Pipeline management
    # ----------------------------------------------------------------------
    def _rebuild_compute(self) -> None:
        """Rebuild the compute pipeline (called when source or target changes)."""
        if self._src_tex is None or self._dst_tex is None:
            return
        self._compute = Compute(
            self._shader,
            srv=[self._src_tex],
            uav=[self._dst_tex],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        logger.debug("Lanczos compute pipeline rebuilt")
