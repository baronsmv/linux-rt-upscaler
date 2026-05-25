import logging
import os
import struct

from ...shader import Shader

logger = logging.getLogger(__name__)

CB_FORMAT = "fIIfI"  # bloomStrength, width, height, bloomThreshold, radius
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "bloom.spv")


class Bloom(Shader):
    """
    Soft bloom effect for bright regions of the screen.

    Uses a wide 4-tap blur, threshold, and screen blend to create a dreamy
    glow without blurring line art or text.

    Tuning:
        strength  = 0.0 (off)  - 0.15 (strong)   [default 0.0]
        threshold = 0.7 - 0.95                    [default 0.85]
        radius    = 2 - 8 pixels                  [default 4]
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()

    def _get_bindings(self):
        return [self.target_texture], [self.target_texture], []

    def update_constants(
        self,
        strength: float = 0.0,
        threshold: float = 0.85,
        radius: int = 4,
    ) -> None:
        """
        Pack and upload bloom parameters.

        Args:
            strength: 0.0 - 0.15. 0 = off.
            threshold: Only pixels brighter than this contribute (0.85 - 0.95).
            radius: Blur radius in pixels (2 - 8).
        """
        strength = max(0.0, min(strength, 1.0))
        threshold = max(0.0, min(threshold, 1.0))
        radius = max(1, min(radius, 16))
        w = self.target_texture.width if self.target_texture else 0
        h = self.target_texture.height if self.target_texture else 0
        data = struct.pack(CB_FORMAT, strength, w, h, threshold, radius)
        self._cb.upload(data)
