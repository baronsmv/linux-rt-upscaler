from __future__ import annotations

import logging
import os
import struct
from typing import Optional

from ..blue_noise import BLUE_NOISE_DATA
from ...shader import Shader
from ....vulkan import Sampler, Texture2D

logger = logging.getLogger(__name__)

CB_FORMAT = "IIf"
CB_SIZE = struct.calcsize(CB_FORMAT)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "dither.spv")


class DitherCopy(Shader):
    """Adds blue-noise dither to an sRGB image and writes it to an 8-bit target."""

    def __init__(self, shader_path: Optional[str] = None) -> None:
        self.source_texture: Optional[Texture2D] = None
        self._noise_tex: Optional[Texture2D] = None
        self._sampler: Optional[Sampler] = None
        super().__init__(shader_path or DEFAULT_SHADER_PATH)

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE

    def _create_persistent_resources(self) -> None:
        super()._create_persistent_resources()
        self._sampler = Sampler()

    def _get_bindings(self):
        return (
            [self.source_texture, self._noise_tex],
            [self.target_texture],
            [self._sampler],
        )

    def _rebuild_compute(self) -> None:
        if (
            self.target_texture is None
            or self.source_texture is None
            or self._noise_tex is None
        ):
            return
        super()._rebuild_compute()

    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    def set_noise_texture(self, tex: Optional[Texture2D] = None) -> None:
        if tex is None:
            if self._noise_tex is None:
                tex = Texture2D(64, 64)
                tex.upload_subresources([(bytes(BLUE_NOISE_DATA), 0, 0, 64, 64)])
            else:
                return
        if tex is self._noise_tex:
            return
        self._noise_tex = tex
        self._rebuild_compute()

    def update_constants(self, dither_strength: float = 1.0 / 255.0) -> None:
        if self.target_texture is None:
            raise RuntimeError("Target texture not set")
        w = self.target_texture.width
        h = self.target_texture.height
        data = struct.pack(CB_FORMAT, w, h, dither_strength)
        self._cb.upload(data)
