from __future__ import annotations

import logging
import os
import struct
from typing import Optional, Tuple

from ..scaler import Scaler
from ....vulkan import (
    Buffer,
    Sampler,
    SAMPLER_FILTER_LINEAR,
)

logger = logging.getLogger(__name__)

CB_FORMAT_CATMULL = "ffffIIIIiiiif"
CB_SIZE_CATMULL = struct.calcsize(CB_FORMAT_CATMULL)

SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(SHADER_DIR, "catmull_rom.spv")


class CatmullRomScaler(Scaler):
    """
    Catmull-Rom bicubic resampler.

    Parameters
    ----------
    shader_path : str
        Path to the compiled SPIR-V file.
    blur : float
        Default kernel stretch (1.0 = standard, >1.0 = softer).
    """

    def __init__(
        self, shader_path: str = DEFAULT_SHADER_PATH, blur: float = 1.0
    ) -> None:
        super().__init__(shader_path)
        self._blur = blur

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_CATMULL

    def _create_persistent_resources(self) -> None:
        self._cb = Buffer(CB_SIZE_CATMULL)
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR, filter_mag=SAMPLER_FILTER_LINEAR
        )

    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], [self._sampler]

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
        blur: Optional[float] = None,
    ) -> None:
        """
        Pack and upload the constant buffer.

        Args:
            background_color: RGBA color for areas outside the content rect.
            src_width, src_height: Dimensions of the source texture.
            dst_total_width, dst_total_height: Size of the output (screen) texture.
            dst_x, dst_y: Top-left corner of the destination rectangle.
            dst_w, dst_h: Dimensions of the destination rectangle.
            blur: Kernel stretch (1.0 = standard Catmull-Rom). If None, the
                  value given to the constructor is used.
        """
        blur = blur or self._blur
        blur = max(blur, 0.001)

        data = struct.pack(
            CB_FORMAT_CATMULL,
            *background_color,
            src_width,
            src_height,
            dst_total_width,
            dst_total_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
            blur,
        )
        self._cb.upload(data)
