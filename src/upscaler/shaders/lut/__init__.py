import logging
import os
import struct
from typing import Optional

from .presets import BUILT_IN_PRESETS, LUT_SIZE
from ..shader import Shader
from ...vulkan import Sampler, Texture2D, SAMPLER_FILTER_LINEAR

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Constant buffer layout - must match HLSL `cbuffer Constants`
#   float intensity;      // 0.0 - 1.0
#   uint  lutSize;        // e.g., 32
#   uint  dstWidth;
#   uint  dstHeight;
# ------------------------------------------------------------------
CB_FORMAT = "fIII"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "lut.spv")


class LUT(Shader):
    """
    Color grading via 3D LUT.

    Applies a pre-computed lookup table to the screen image. The LUT
    is stored as a 2D-array texture (slices = LUT size). Trilinear
    interpolation ensures smooth color transitions.

    Strength:
        0.0 = original image (passthrough)
        0.5 = half blend
        1.0 = fully graded image
    """

    def __init__(
        self, shader_path: str = DEFAULT_SHADER_PATH, preset: str = "identity"
    ) -> None:
        # LUT texture is a persistent resource - built in _create_persistent_resources
        self._lut_tex: Optional[Texture2D] = None
        self._lut_sampler: Optional[Sampler] = None
        self._preset_name = preset
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  Constant buffer size
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    # ------------------------------------------------------------------
    #  Persistent resources - texture + sampler, then load the preset
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        # Constant buffer (base class)
        super()._create_persistent_resources()

        # LUT texture: 2D array of size LUTSIZE x LUTSIZE x LUTSIZE
        self._lut_tex = Texture2D(
            width=LUT_SIZE,
            height=LUT_SIZE,
            slices=LUT_SIZE,
        )
        self._lut_sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
        )

        # Load the initial preset (defaults to identity)
        self._apply_preset(self._preset_name)

    # ------------------------------------------------------------------
    #  Preset management
    # ------------------------------------------------------------------
    def _apply_preset(self, preset_name: str) -> None:
        """Upload a built-in preset to the LUT texture."""
        if preset_name not in BUILT_IN_PRESETS:
            logger.warning(
                "Preset '%s' not found, falling back to identity", preset_name
            )
            preset_name = "identity"
        lut_data = BUILT_IN_PRESETS[preset_name]()
        self._upload_lut_data(lut_data)
        self._preset_name = preset_name
        logger.debug("LUT preset set to '%s'", preset_name)

    def set_preset(self, preset_name: str) -> None:
        """Change the active preset (can be called at runtime)."""
        self._apply_preset(preset_name)

    def _upload_lut_data(self, data: bytes) -> None:
        """Upload raw RGBA8 LUT data (size must be 32³ -x 4 bytes)."""
        uploads = []
        slice_size = LUT_SIZE * LUT_SIZE * 4
        for z in range(LUT_SIZE):
            slice_data = data[z * slice_size : (z + 1) * slice_size]
            uploads.append((bytes(slice_data), 0, 0, LUT_SIZE, LUT_SIZE, z))
        self._lut_tex.upload_subresources(uploads)
        logger.debug("LUT data uploaded (%d³)", LUT_SIZE)

    # ------------------------------------------------------------------
    #  Custom LUT from external file
    # ------------------------------------------------------------------
    def set_lut_data(self, lut_data: bytes, lut_size: int = LUT_SIZE) -> None:
        """Upload a custom LUT (same format as presets)."""
        if lut_size != LUT_SIZE:
            logger.warning(
                "LUT size mismatch: texture is %d, provided %d",
                LUT_SIZE,
                lut_size,
            )
            return
        self._upload_lut_data(lut_data)

    # ------------------------------------------------------------------
    #  Bindings: screen (SRV/UAV) + LUT texture + LUT sampler
    # ------------------------------------------------------------------
    def _get_bindings(self):
        srv = [self.target_texture, self._lut_tex]
        uav = [self.target_texture]
        samplers = [self._lut_sampler]
        return srv, uav, samplers

    # ------------------------------------------------------------------
    #  Constant buffer update
    # ------------------------------------------------------------------
    def update_constants(self, intensity: float = 0.0) -> None:
        """
        Pack and upload color grading parameters.

        Args:
            intensity: 0.0 (original) to 1.0 (fully graded). Default 0.0.
        """
        intensity = max(0.0, min(intensity, 1.0))
        w = self.target_texture.width if self.target_texture else 0
        h = self.target_texture.height if self.target_texture else 0
        data = struct.pack(CB_FORMAT, intensity, LUT_SIZE, w, h)
        self._cb.upload(data)
