import logging
import os
import struct
from typing import Optional, Tuple

from ..shader import ShaderPass
from ...vulkan import Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout = match HLSL `cbuffer Constants`
# float4 bgColor;            // RGBA          (4x float)
# uint   srcWidth, srcHeight;                 (2x uint32)
# uint   dstTotalWidth, dstTotalHeight;       (2x uint32)
# int    dstX, dstY, dstW, dstH;              (4x int32)
# float  blur;                                (1x float)
# float  antiringStrength;                    (1x float)
# bool   linearLight;                         (1x uint32)
# bool   tightAntiring;                       (1x uint32)
# ---------------------------------------------------------------------------
CB_FORMAT = "ffffIIIIiiiiIIffII"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "lanczos.spv")


class LanczosScaler(ShaderPass):
    """
    Adaptive Lanczos 3.0 resampler - single-pass 2D scaling via compute shader.

    Maps an **upscaled** source texture (e.g. CuNNy output) onto a screen-sized
    destination texture using an adaptive-radius window-sinc (Lanczos) filter.

    The filter radius adapts automatically inside the shader:
        - upscaling   (scale ≥ 1.0)  -> radius 2 (Lanczos-2, sharp)
        - downscaling (scale < 1.0)  -> ceil(2.0 / min(scale)), capped at 6

    Features exposed via constant buffer:
        `blur` - kernel softness (1.0 = standard)
        `antiring_strength` - soft anti-ringing clamp (0-1)
        `linear_light` - sRGB ↔ linear conversion (recommended True)
        `tight_antiring` - use only central 2x2 for ringing bounds
            (True -> sharper text, False -> full-footprint clamp)

    Thread-group size: 16x16.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        self.source_texture: Optional[Texture2D] = None
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  Constant buffer size (static, overridden)
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    # ------------------------------------------------------------------
    #  Persistent resources (sampler)
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        """Create constant buffer and point sampler (required by Gather)."""
        super()._create_persistent_resources()  # creates self._cb
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )

    # ------------------------------------------------------------------
    #  Binding layout
    # ------------------------------------------------------------------
    def _get_bindings(self):
        """Return SRV=[source], UAV=[target], Sampler=[point]."""
        return [self.source_texture], [self.target_texture], [self._sampler]

    # ------------------------------------------------------------------
    #  Rebuild compute
    # ------------------------------------------------------------------
    def _rebuild_compute(self) -> None:
        """Only create the compute pipeline when both textures are set."""
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    # ------------------------------------------------------------------
    #  Set the input (upscaled) texture
    # ------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Bind the source (upscaled) texture.

        Args:
            tex: The fully upscaled image from the SRCNN / CuNNy stage.
        """
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Constant buffer update - all scaling parameters
    # ------------------------------------------------------------------
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
        radius_x: int,
        radius_y: int,
        blur: float = 1.0,
        antiring_strength: float = 1.0,
        linear_light: bool = True,
        tight_antiring: bool = True,
    ) -> None:
        """
        Pack and upload the constant buffer.

        Must be called every frame (or when layout changes).

        Args:
            background_color: RGBA colour for letterbox / pillarbox.
            src_width, src_height: Dimensions of the upscaled source.
            dst_total_width, dst_total_height: Full screen texture size.
            dst_x, dst_y: Top-left of content rectangle.
            dst_w, dst_h: Width and height of content rectangle.
            blur: Kernel softness (1.0 = standard).
            antiring_strength: 0.0 = off, 1.0 = full clamp.
            linear_light: Process in linear light if True.
            tight_antiring: Only use central 2x2 for ringing bounds.
        """
        data = struct.pack(
            CB_FORMAT,
            *background_color,  # 4 floats
            src_width,
            src_height,  # 2 uint32
            dst_total_width,
            dst_total_height,  # 2 uint32
            dst_x,
            dst_y,
            dst_w,
            dst_h,  # 4 int32
            radius_x,
            radius_y,
            blur,  # float
            antiring_strength,  # float
            1 if linear_light else 0,  # uint32 (bool)
            1 if tight_antiring else 0,  # uint32 (bool)
        )
        self._cb.upload(data)

    # ------------------------------------------------------------------
    #  Optional convenience accessors
    # ------------------------------------------------------------------
    @property
    def source_width(self) -> int:
        """Width of the source texture in pixels, or 0 if not set."""
        return self.source_texture.width if self.source_texture else 0

    @property
    def source_height(self) -> int:
        """Height of the source texture in pixels, or 0 if not set."""
        return self.source_texture.height if self.source_texture else 0
