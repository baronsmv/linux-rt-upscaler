import logging
import os
import struct
from typing import Optional

from ..shader import ShaderPass
from ...vulkan import Sampler, Texture2D, SAMPLER_FILTER_LINEAR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout - must match HLSL `cbuffer Constants`
#   float intensity;      // 0.0 - 1.0
#   uint  lutSize;        // e.g., 32
#   uint  dstWidth;
#   uint  dstHeight;
# ---------------------------------------------------------------------------
CB_FORMAT = "fIII"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "lut.spv")

# Default LUT resolution (32x32x32)
DEFAULT_LUT_SIZE = 32


class LUTPass(ShaderPass):
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

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        # LUT texture is a persistent resource - built in _create_persistent_resources
        self._lut_tex: Optional[Texture2D] = None
        self._lut_sampler: Optional[Sampler] = None
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  Constant buffer size
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    # ------------------------------------------------------------------
    #  Create the LUT texture and sampler (persistent)
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        # Constant buffer (base class)
        super()._create_persistent_resources()

        # LUT texture: 2D array of size LUTSIZE x LUTSIZE x LUTSIZE
        self._lut_tex = Texture2D(
            width=DEFAULT_LUT_SIZE,
            height=DEFAULT_LUT_SIZE,
            slices=DEFAULT_LUT_SIZE,
        )
        self._lut_sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
        )

        # Initialise with identity LUT
        self._upload_identity_lut()

    # ------------------------------------------------------------------
    #  Upload identity LUT (R,G,B -> R,G,B)
    # ------------------------------------------------------------------
    def _upload_identity_lut(self) -> None:
        """Populate the LUT texture with an identity mapping."""
        lut_size = DEFAULT_LUT_SIZE
        data = bytearray(lut_size * lut_size * lut_size * 4)

        off = 0
        for z in range(lut_size):
            for y in range(lut_size):
                for x in range(lut_size):
                    r = x / (lut_size - 1) * 255
                    g = y / (lut_size - 1) * 255
                    b = z / (lut_size - 1) * 255
                    data[off : off + 4] = struct.pack(
                        "BBBB", int(r), int(g), int(b), 255
                    )
                    off += 4

        # Upload as sub-resources (one slice at a time)
        uploads = []
        slice_size = lut_size * lut_size * 4
        for z in range(lut_size):
            slice_data = data[z * slice_size : (z + 1) * slice_size]
            uploads.append((bytes(slice_data), 0, 0, lut_size, lut_size, z))
        self._lut_tex.upload_subresources(uploads)

    # ------------------------------------------------------------------
    #  Bindings: screen (SRV/UAV) + LUT texture + LUT sampler
    # ------------------------------------------------------------------
    def _get_bindings(self):
        srv = [self.target_texture, self._lut_tex]  # screen + LUT
        uav = [self.target_texture]
        samplers = [self._lut_sampler]
        return srv, uav, samplers

    # ------------------------------------------------------------------
    #  Set a custom LUT (optional, e.g., loaded from file)
    # ------------------------------------------------------------------
    def set_lut_data(self, lut_data: bytes, lut_size: int = DEFAULT_LUT_SIZE) -> None:
        """
        Upload a custom LUT. Expects raw RGBA8 data (4 bytes per pixel)
        in row-major order: [blue_slices][rows][columns].

        Args:
            lut_data: The flat pixel data (size = lut_size³ * 4).
            lut_size: LUT dimension (must match texture creation size).
        """
        if lut_size != DEFAULT_LUT_SIZE:
            logger.warning(
                "LUT size mismatch: texture is %d, provided %d",
                DEFAULT_LUT_SIZE,
                lut_size,
            )
            return

        uploads = []
        slice_size = lut_size * lut_size * 4
        for z in range(lut_size):
            slice_data = lut_data[z * slice_size : (z + 1) * slice_size]
            uploads.append((bytes(slice_data), 0, 0, lut_size, lut_size, z))
        self._lut_tex.upload_subresources(uploads)
        logger.debug("Custom LUT uploaded (%d³)", lut_size)

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
        data = struct.pack(CB_FORMAT, intensity, DEFAULT_LUT_SIZE, w, h)
        self._cb.upload(data)
