import logging
import os
import struct

from ..shader import ShaderPass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout - must match HLSL `cbuffer Constants`
#   float vignetteStrength;   // 0.0 - 1.0
#   uint  dstWidth;
#   uint  dstHeight;
#   float vignetteRadius;     // where darkening starts (0.0 - 1.5)
#   float vignetteFalloff;    // edge softness (1.0 - 4.0)
# ---------------------------------------------------------------------------
CB_FORMAT = "fII f f"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "vignette.spv")


class VignettePass(ShaderPass):
    """
    Radial vignette - soft darkening at screen edges.

    Works in-place on the screen texture. Zero-cost when `strength` is 0.0.

    Tuning:
        strength = 0.0 (off)   to   1.0 (fully black corners)
        radius   = 0.0 - 1.5   (default 0.8 - keeps centre bright)
        falloff  = 1.0 - 4.0   (default 2.0 - higher = sharper transition)
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()

    def _get_bindings(self):
        # In-place: read and write the same texture
        return [self.target_texture], [self.target_texture], []

    def update_constants(
        self,
        strength: float = 0.0,
        radius: float = 0.8,
        falloff: float = 2.0,
    ) -> None:
        """
        Pack and upload vignette parameters.

        Args:
            strength: 0.0 (off) to 1.0 (fully black). Default 0.0.
            radius: 0.0 to 1.5. 0.0 = centre, 0.8 = moderate crop.
            falloff: 1.0 (gentle) to 4.0 (sharp).
        """
        strength = max(0.0, min(strength, 1.0))
        radius = max(0.0, min(radius, 2.0))
        falloff = max(0.1, min(falloff, 10.0))
        w = self.target_texture.width if self.target_texture else 0
        h = self.target_texture.height if self.target_texture else 0

        data = struct.pack(CB_FORMAT, strength, w, h, radius, falloff)
        self._cb.upload(data)
