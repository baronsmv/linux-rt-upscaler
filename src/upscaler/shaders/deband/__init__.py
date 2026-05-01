import logging
import os
import struct
from typing import Optional

from ..shader import ShaderPass
from ...vulkan import Texture2D

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout - must match HLSL `cbuffer Constants`
#   float debandStrength;    // 0.0 - 1.0
#   uint  dstWidth;
#   uint  dstHeight;
#   uint  frameIndex;        // increasing frame counter for dither variation
# ---------------------------------------------------------------------------
CB_FORMAT = "fIII"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "deband.spv")


class DebandPass(ShaderPass):
    """
    Anisotropic stochastic debanding post-effect.

    Uses four pseudo-random samples per pixel, comparing them with an
    edge-preserving threshold, and blends only band-like differences.
    A small temporally varying dither is injected to prevent the
    output pipeline from re-banding.

    Requires separate source and target textures (cannot safely operate
    in-place). The `frame_index` parameter should be incremented
    each frame to avoid static noise patterns.

    Strength:
        0.0 = passthrough
        0.3 = subtle (recommended for most content)
        0.6 = strong
        1.0 = maximum
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
    #  Persistent resources - only the constant buffer is needed
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()

    # ------------------------------------------------------------------
    #  Binding layout - input texture as SRV, output as UAV, no sampler
    # ------------------------------------------------------------------
    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], []

    # ------------------------------------------------------------------
    #  Source texture (the AI-upscaled image to be debanded)
    # ------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Set the texture to be debanded (usually the upscaler output).

        Args:
            tex: The RGBA8 texture containing the upscaled frame.
        """
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Constant buffer update
    # ------------------------------------------------------------------
    def update_constants(self, strength: float = 0.3, frame_index: int = 0) -> None:
        """
        Pack and upload debanding parameters.

        Args:
            strength: 0.0 (off) to 1.0 (maximum). Default 0.3.
            frame_index: An increasing frame counter (0, 1, 2, ...).
                Provides unique dither per frame; the caller must
                increment it on each call.
        """
        strength = max(0.0, min(strength, 1.0))
        w = self.target_texture.width if self.target_texture else 0
        h = self.target_texture.height if self.target_texture else 0
        data = struct.pack(CB_FORMAT, strength, w, h, frame_index)
        self._cb.upload(data)
