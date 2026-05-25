from __future__ import annotations

import logging
import os
import struct
from typing import TYPE_CHECKING

from ..scaler import Scaler

if TYPE_CHECKING:
    from ....config import BackgroundColor

logger = logging.getLogger(__name__)

CB_FORMAT = "ffffIIIIiiii"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "copy.spv")


class CopyScaler(Scaler):
    """
    Point‑sample copy from source to destination rectangle.

    Bypasses Lanczos when no resampling is needed (1:1 mapping).
    The source texture is placed exactly at (dstX, dstY) with
    dimensions (dstW, dstH) and the surrounding area is filled
    with `bgColor`.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], []

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
        """
        Pack and upload copy parameters.

        Args:
            background_color: RGBA color for areas outside the content rect.
            src_width: Width of the source texture.
            src_height: Height of the source texture.
            dst_width: Width of the target (screen) texture.
            dst_height: Height of the target (screen) texture.
            dst_x: Left edge of the destination rectangle.
            dst_y: Top edge of the destination rectangle.
            dst_w: Width of the destination rectangle.
            dst_h: Height of the destination rectangle.
        """
        data = struct.pack(
            CB_FORMAT,
            *background_color,
            src_width,
            src_height,
            dst_width,
            dst_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
        )
        self._cb.upload(data)
