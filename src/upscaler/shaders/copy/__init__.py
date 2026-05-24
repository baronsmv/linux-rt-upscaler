from __future__ import annotations

import logging
import os
import struct
from typing import TYPE_CHECKING

from ..shader import ShaderPass
from ...vulkan import Texture2D

if TYPE_CHECKING:
    from ...config import BackgroundColor

logger = logging.getLogger(__name__)

# Constant buffer: float4 bgColor, 4 uints, 4 ints
CB_FORMAT = "ffffIIIIiiii"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "copy.spv")


class CopyPass(ShaderPass):
    """
    Point‑sample copy from source to destination rectangle.

    Bypasses Lanczos when no resampling is needed (1:1 mapping).
    The source texture is placed exactly at (dstX, dstY) with
    dimensions (dstW, dstH) and the surrounding area is filled
    with `bgColor`.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        self.source_texture: Texture2D | None = None
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    # ------------------------------------------------------------------
    #  Binding layout
    # ------------------------------------------------------------------
    def _get_bindings(self):
        # SRV = source texture, UAV = target texture, no sampler
        return [self.source_texture], [self.target_texture], []

    # ------------------------------------------------------------------
    #  Rebuild compute (called by base when textures change)
    # ------------------------------------------------------------------
    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    # ------------------------------------------------------------------
    #  Set the input texture
    # ------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Set the texture to be copied. Must be set before dispatch.
        Rebuilds the compute pipeline if the texture object changes.
        """
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Constant buffer update
    # ------------------------------------------------------------------
    def update_constants(
        self,
        background_color: BackgroundColor,
        src_width: int,
        src_height: int,
        dst_total_width: int,
        dst_total_height: int,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
    ) -> None:
        """
        Pack and upload copy parameters.

        Args:
            background_color: RGBA colour for areas outside the content rect.
            src_width: Width of the source texture.
            src_height: Height of the source texture.
            dst_total_width: Width of the target (screen) texture.
            dst_total_height: Height of the target (screen) texture.
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
            dst_total_width,
            dst_total_height,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
        )
        self._cb.upload(data)
