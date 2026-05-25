import logging
import os
import struct

from ...shader import Shader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout - must match HLSL `cbuffer Constants`
#   float grainStrength;    // 0.0 - 0.10
#   uint  dstWidth;
#   uint  dstHeight;
#   uint  frameIndex;
#   float grainSize;        // 1.0 = fine, >1.0 = coarser
# ---------------------------------------------------------------------------
CB_FORMAT = "fIII f"  # note: float after uint preserves alignment
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "grain.spv")


class FilmGrain(Shader):
    """
    Film-emulation grain overlay.

    Adds an organic, isotropic noise texture with sub-pixel temporal
    movement, blended via soft-light to mimic real photographic grain.
    Operates in-place on the screen texture.

    Tuning:
        strength  = 0.0  (off)   to  0.10 (gritty)     [default 0.0]
        grainSize = 1.0  (fine)  to  2.0+  (coarse)    [default 1.0]
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()

    def _get_bindings(self):
        # Read and write the same texture (in-place)
        return [self.target_texture], [self.target_texture], []

    def update_constants(
        self,
        strength: float = 0.0,
        grain_size: float = 1.0,
        frame_index: int = 0,
    ) -> None:
        """
        Pack and upload grain parameters.

        Args:
            strength: Grain intensity (0.0 - 0.10). 0 = off.
            grain_size: 1.0 (fine) to 2.0+ (coarse).
            frame_index: An increasing frame counter (0, 1, 2, ...).
                Must be incremented each frame for temporal variation.
        """
        strength = max(0.0, min(strength, 1.0))
        grain_size = max(1.0, grain_size)
        w = self.target_texture.width if self.target_texture else 0
        h = self.target_texture.height if self.target_texture else 0

        data = struct.pack(CB_FORMAT, strength, w, h, frame_index, grain_size)
        self._cb.upload(data)
