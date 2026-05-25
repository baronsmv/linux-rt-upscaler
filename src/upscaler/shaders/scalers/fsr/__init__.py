from __future__ import annotations

import logging
import os
import struct
from typing import TYPE_CHECKING

from ..scaler import Scaler
from ....vulkan import Sampler, SAMPLER_FILTER_LINEAR

if TYPE_CHECKING:
    from ....config import BackgroundColor

logger = logging.getLogger(__name__)

CB_SIZE_FSR = 112
CB_FORMAT_FSR = "<" + "f" * 20 + "i" * 4 + "f" * 4

SHADER_DIR = os.path.dirname(__file__)
DEFAULT_FSR_SHADER = os.path.join(SHADER_DIR, "fsr.spv")


class FSRScaler(Scaler):
    """FidelityFX Super Resolution 1.0, EASU pass. Used for upscaling."""

    def __init__(self, shader_path: str = DEFAULT_FSR_SHADER) -> None:
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_FSR

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
        )

    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], [self._sampler]

    def update_constants(
        self,
        background_color: BackgroundColor,
        src_width: int,
        src_height: int,
        dst_width: int,
        dst_height: int,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """Pack and upload the EASU constants."""
        data = self._compute_easu_constants(
            src_width,
            src_height,
            dst_w,
            dst_h,
            dst_x,
            dst_y,
            dst_w if dst_w is not None else dst_width,
            dst_h if dst_h is not None else dst_height,
            background_color,
        )
        self._cb.upload(data)

    @staticmethod
    def _compute_easu_constants(
        src_w: int,
        src_h: int,
        dst_w: int,
        dst_h: int,
        dst_x: int,
        dst_y: int,
        fill_w: int,
        fill_h: int,
        background_color: BackgroundColor,
    ) -> bytes:
        """
        Return the packed constant buffer for FSR EASU:
          - Const0 = (scaleX, scaleY, 0.5*scaleX-0.5, 0.5*scaleY-0.5)
          - Const1 = (1/src_w, 1/src_h,  1/src_w, -1/src_h)
          - Const2 = (-1/src_w, 2/src_h, 1/src_w, 2/src_h)
          - Const3 = (0, 4/src_h)
        """
        # Scale factor from input to output
        scale_x = float(src_w) / float(dst_w)
        scale_y = float(src_h) / float(dst_h)

        # Pixel size in the source texture
        in_pt_x = 1.0 / float(src_w)
        in_pt_y = 1.0 / float(src_h)

        # Original EASU constants (20 floats)
        easu = (
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
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        return struct.pack(
            CB_FORMAT_FSR, *easu, dst_x, dst_y, fill_w, fill_h, *background_color
        )
