import logging
import os
import struct

from ..shader import Shader

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout = must match `cbuffer Constants` in cas.hlsl
#   float sharpeningStrength;   // 0.0 - 1.0
#   uint  dstWidth;
#   uint  dstHeight;
#   uint  _pad0;                // alignment padding
# ---------------------------------------------------------------------------
CB_FORMAT = "fIII"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "cas.spv")


class CAS(Shader):
    """
    Contrast Adaptive Sharpening - single-pass screen-space sharpening.

    Operates directly on the screen texture (read and write). The
    sharpening strength is adjustable via `update_constants(strength)`.

    Thread-group size: 16x16.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        # CAS does not have a separate source texture; input = target
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  Constant buffer size
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    # ------------------------------------------------------------------
    #  Persistent resources - nothing beyond the constant buffer
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()  # creates self._cb

    # ------------------------------------------------------------------
    #  Bindings - target texture is both SRV and UAV
    # ------------------------------------------------------------------
    def _get_bindings(self):
        return [self.target_texture], [self.target_texture], []

    # ------------------------------------------------------------------
    #  Constant buffer update
    # ------------------------------------------------------------------
    def update_constants(self, strength: float = 0.4) -> None:
        """
        Pack and upload CAS parameters.

        Args:
            strength: Sharpening amount (0.0 = passthrough, 1.0 = maximum).
                Recommended range for VN content: 0.2 - 0.5.
        """
        strength = max(0.0, min(strength, 1.0))
        w = self.target_texture.width
        h = self.target_texture.height
        data = struct.pack(CB_FORMAT, strength, w, h, 0)
        self._cb.upload(data)
