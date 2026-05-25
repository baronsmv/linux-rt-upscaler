from __future__ import annotations

import logging
import os
import struct
from typing import Tuple

from ..scaler import Scaler
from ....vulkan import Buffer, Sampler, Texture2D, SAMPLER_FILTER_LINEAR

logger = logging.getLogger(__name__)

NIS_THREAD_GROUP_SIZE = 64
CB_SIZE_NIS = 28 * 4 + 4 * 4 + 4 * 4
CB_FORMAT_NIS = "<" + "f" * 28 + "I" * 4 + "f" * 4

_COEF_SCALER_SIZE = (8, 32)
_COEF_USM_SIZE = (8, 32)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_NIS_SHADER = os.path.join(_SHADER_DIR, "nis.spv")


class NISScaler(Scaler):
    """
    NVIDIA Image Scaling.

    Parameters
    ----------
    shader_path : str
        Path to the compiled SPIR‑V file.
    sharpness : float
        Default sharpness [0.0 – 1.0].  Used when :meth:`update_constants` is
        called without an explicit sharpness.
    """

    requires_linear_input = False  # NIS works in sRGB, not linear

    def __init__(
        self, shader_path: str = DEFAULT_NIS_SHADER, sharpness: float = 0.5
    ) -> None:
        super().__init__(shader_path)
        self._sharpness = sharpness
        self._coef_scaler = self._load_coefficient_texture("coef_scaler")
        self._coef_usm = self._load_coefficient_texture("coef_usm")

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_NIS

    def _create_persistent_resources(self) -> None:
        self._cb = Buffer(CB_SIZE_NIS)
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
        )

    def _get_bindings(self):
        return (
            [self.source_texture, self._coef_scaler, self._coef_usm],
            [self.target_texture],
            [self._sampler],
        )

    def dispatch_auto(self) -> None:
        self._check_ready()
        w, h = self.target_texture.width, self.target_texture.height
        groups_x = (w + NIS_THREAD_GROUP_SIZE - 1) // NIS_THREAD_GROUP_SIZE
        groups_y = h
        self.dispatch(groups_x, groups_y, 1)

    def update_constants(
        self,
        background_color: Tuple[float, float, float, float],
        src_width: int,
        src_height: int,
        dst_width: int,
        dst_height: int,
        dst_x: int,
        dst_y: int,
        dst_w: int,
        dst_h: int,
        sharpness: float = None,
    ) -> None:
        if sharpness is None:
            sharpness = self._sharpness

        consts = self._compute_nis_constants(
            src_width, src_height, dst_w, dst_h, sharpness
        )
        data = struct.pack(
            CB_FORMAT_NIS,
            *consts,
            dst_x,
            dst_y,
            dst_w,
            dst_h,
            *background_color,
        )
        self._cb.upload(data)

    @staticmethod
    def _compute_nis_constants(
        src_w: int,
        src_h: int,
        out_w: int,
        out_h: int,
        sharpness: float,
    ) -> Tuple[float, ...]:
        sharpness = max(0.0, min(sharpness, 1.0))

        # Scale factors
        kScaleX = float(src_w) / float(out_w)
        kScaleY = float(src_h) / float(out_h)

        # Normalisation factors
        kDstNormX = 1.0 / float(out_w)
        kDstNormY = 1.0 / float(out_h)
        kSrcNormX = 1.0 / float(src_w)
        kSrcNormY = 1.0 / float(src_h)

        # Viewport (full image)
        kInputViewportOriginX = 0
        kInputViewportOriginY = 0
        kInputViewportWidth = src_w
        kInputViewportHeight = src_h
        kOutputViewportOriginX = 0
        kOutputViewportOriginY = 0
        kOutputViewportWidth = out_w
        kOutputViewportHeight = out_h

        # Sharpness / filter coefficients
        kDetectRatio = 0.5 + 0.5 * sharpness
        kDetectThres = 0.015
        kMinContrastRatio = 0.125
        kRatioNorm = 1.0 / (1.0 - kMinContrastRatio)

        kContrastBoost = 0.1
        kEps = 1e-5
        kSharpStartY = 0.015
        kSharpScaleY = 1.0 / (1.0 - kSharpStartY)

        kSharpStrengthMin = 0.2
        kSharpStrengthScale = 0.8
        kSharpLimitMin = 0.1
        kSharpLimitScale = 0.9

        reserved0 = 0.0
        reserved1 = 0.0

        return (
            kDetectRatio,
            kDetectThres,
            kMinContrastRatio,
            kRatioNorm,
            kContrastBoost,
            kEps,
            kSharpStartY,
            kSharpScaleY,
            kSharpStrengthMin,
            kSharpStrengthScale,
            kSharpLimitMin,
            kSharpLimitScale,
            kScaleX,
            kScaleY,
            kDstNormX,
            kDstNormY,
            kSrcNormX,
            kSrcNormY,
            kInputViewportOriginX,
            kInputViewportOriginY,
            kInputViewportWidth,
            kInputViewportHeight,
            kOutputViewportOriginX,
            kOutputViewportOriginY,
            kOutputViewportWidth,
            kOutputViewportHeight,
            reserved0,
            reserved1,
        )

    @staticmethod
    def _load_coefficient_texture(name: str) -> Texture2D:
        """
        Load a small RGBA8 coefficient texture.

        The texture data is expected to reside in a file next to the shader,
        e.g. ``coef_scaler.bin``.  If the file is missing, a black stub is
        returned so that the pipeline does not crash (visual quality will
        degrade).
        """
        filename = os.path.join(_SHADER_DIR, f"{name}.bin")
        try:
            with open(filename, "rb") as f:
                raw = f.read()
        except FileNotFoundError:
            logger.warning("NIS coefficient texture '%s' not found, using stub", name)
            raw = b"\x00" * (_COEF_SCALER_SIZE[0] * _COEF_SCALER_SIZE[1] * 4)

        # Determine size from the expected dimensions
        size = _COEF_SCALER_SIZE if name == "coef_scaler" else _COEF_USM_SIZE
        tex = Texture2D(size[0], size[1])
        tex.upload_subresources([(raw, 0, 0, size[0], size[1])])
        return tex
