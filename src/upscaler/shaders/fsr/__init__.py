import logging
import os
import struct

from ..shader import ShaderPass
from ...vulkan import (
    Sampler,
    Texture2D,
    SAMPLER_ADDRESS_MODE_CLAMP,
    SAMPLER_FILTER_LINEAR,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FSR EASU constant buffer layout
#   cbuffer cb : register(b0) {
#       uint4 Const0;   // floats
#       uint4 Const1;
#       uint4 Const2;
#       uint4 Const3;
#       uint4 Sample;   // debug only, set to 0
#   }
# ---------------------------------------------------------------------------
CB_SIZE_FSR = 80  # 5 uint4 = 20 floats
CB_FORMAT_FSR = "<" + "f" * 20  # 20 floats little-endian

SHADER_DIR = os.path.dirname(__file__)
DEFAULT_FSR_SHADER = os.path.join(SHADER_DIR, "fsr.spv")


class FSRUpscaler(ShaderPass):
    """FidelityFX Super Resolution 1.0, EASU pass. Used for upscaling."""

    def __init__(self, shader_path: str = DEFAULT_FSR_SHADER) -> None:
        self.source_texture: Texture2D | None = None
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  ShaderPass required overrides
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_FSR

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
        )

    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], [self._sampler]

    # ------------------------------------------------------------------
    #  Pipeline rebuild guard
    # ------------------------------------------------------------------
    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Constant buffer update
    # ------------------------------------------------------------------
    def update_constants(
        self,
        src_width: int,
        src_height: int,
        dst_width: int,
        dst_height: int,
        dst_x: int = 0,
        dst_y: int = 0,
    ) -> None:
        """
        Pack and upload the EASU constants.

        The constants are computed from the source/destination dimensions
        and the pixel-size of the source texture.

        Args:
            src_width, src_height: Dimensions of the **source** texture.
            dst_width, dst_height:  Dimensions of the **output** texture.
            dst_x, dst_y:          Offset in the output where the scaled
                                   region starts (usually 0).
        """
        data = self._compute_easu_constants(
            src_width, src_height, dst_width, dst_height
        )
        self._cb.upload(data)

    # ------------------------------------------------------------------
    #  EASU constant computation (replicates FsrEasuCon from ffx_fsr1.h)
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_easu_constants(
        src_w: int,
        src_h: int,
        dst_w: int,
        dst_h: int,
    ) -> bytes:
        """
        Return the packed 80-byte constant buffer for FSR EASU.

        The original algorithm uses the following mapping:
          * Const0 = (scaleX, scaleY, 0.5*scaleX-0.5, 0.5*scaleY-0.5)
          * Const1 = (1/src_w, 1/src_h,  1/src_w, -1/src_h)
          * Const2 = (-1/src_w, 2/src_h, 1/src_w, 2/src_h)
          * Const3 = (0,        4/src_h)
        """
        # Scale factor from input to output
        scale_x = float(src_w) / float(dst_w)
        scale_y = float(src_h) / float(dst_h)

        # Pixel size in the source texture
        in_pt_x = 1.0 / float(src_w)
        in_pt_y = 1.0 / float(src_h)

        # Pack the 20 floats (order must match the HLSL cbuffer)
        floats = (
            scale_x,
            scale_y,
            0.5 * scale_x - 0.5,
            0.5 * scale_y - 0.5,
            in_pt_x,
            in_pt_y,
            in_pt_x,
            -in_pt_y,
            -in_pt_x,
            2.0 * in_pt_y,
            in_pt_x,
            2.0 * in_pt_y,
            0.0,
            4.0 * in_pt_y,
            # Pad
            0.0,
            0.0,
            # Sample (debug)
            0.0,
            0.0,
            0.0,
            0.0,
        )
        return struct.pack(CB_FORMAT_FSR, *floats)
