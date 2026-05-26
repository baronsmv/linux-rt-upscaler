from __future__ import annotations

import logging
import math
import os
import struct
from typing import TYPE_CHECKING

from ..scaler import Scaler
from ....vulkan import Buffer, Sampler, SAMPLER_FILTER_POINT

if TYPE_CHECKING:
    from ....config import BackgroundColor

logger = logging.getLogger(__name__)

# Lanczos Fixed (fixed radius 2): no radiusX/radiusY fields
CB_FORMAT_FIXED = "ffffIIIIiiiif"
CB_SIZE_FIXED = struct.calcsize(CB_FORMAT_FIXED)

# Lanczos Adaptive (variable radius): includes radiusX/radiusY
CB_FORMAT_ADAPTIVE = "ffffIIIIiiiiIIffI"
CB_SIZE_ADAPTIVE = struct.calcsize(CB_FORMAT_ADAPTIVE)

# Maximum buffer size needed (we allocate once and reuse)
CB_SIZE_MAX = max(CB_SIZE_FIXED, CB_SIZE_ADAPTIVE)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH_FIXED = os.path.join(_SHADER_DIR, "lanczos_fixed.spv")
DEFAULT_SHADER_PATH_ADAPTIVE = os.path.join(_SHADER_DIR, "lanczos_adaptive.spv")


class LanczosScaler(Scaler):
    """
    Adaptive Lanczos resampler - single-pass 2D scaling via compute shader.

    Internally uses two Vulkan compute shaders:
        - `lanczos_fixed.spv` - highly optimized for radius 2 (upscaling).
        - `lanczos_adaptive.spv` - general variable-radius path for
          downscaling or non-uniform scaling.
    """

    def __init__(
        self,
        shader_path_l2: str = DEFAULT_SHADER_PATH_FIXED,
        shader_path_adapt: str = DEFAULT_SHADER_PATH_ADAPTIVE,
    ) -> None:
        # Pre-load both SPIR-V binaries into memory
        self._shader_l2 = None
        self._shader_adapt = None
        self._load_shader_variants(shader_path_l2, shader_path_adapt)

        # Let the base class handle persistent resources and pipeline creation
        super().__init__(shader_path_adapt)

        # Now set the initial shader to the adaptive variant (safe default)
        self._shader = self._shader_adapt
        self._current_variant = "adaptive"
        self._cb_format = CB_FORMAT_ADAPTIVE
        self._cb_size_current = CB_SIZE_ADAPTIVE

    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_MAX

    def _load_shader(self) -> None:
        pass

    def _load_shader_variants(self, path_lanczos: str, path_adapt: str) -> None:
        """Read both SPIR-V binaries into memory."""
        try:
            with open(path_lanczos, "rb") as f:
                self._shader_l2 = f.read()
            logger.debug("Lanczos shader loaded from '%s'", path_lanczos)
        except OSError as e:
            raise RuntimeError(f"Failed to load Lanczos shader: {e}") from e

        try:
            with open(path_adapt, "rb") as f:
                self._shader_adapt = f.read()
            logger.debug("Adaptive Lanczos shader loaded from '%s'", path_adapt)
        except OSError as e:
            raise RuntimeError(f"Failed to load Lanczos adaptive shader: {e}") from e

    def _create_persistent_resources(self):
        self._cb = Buffer(CB_SIZE_MAX)
        self._sampler = None
        self._point_sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT, filter_mag=SAMPLER_FILTER_POINT
        )

    def _get_bindings(self):
        if self._current_variant == "fixed":
            return [self.source_texture], [self.target_texture], [self._point_sampler]
        else:
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
        Pack and upload the constant buffer, automatically selecting the
        optimal shader based on the computed filter radii.
        """
        # Select the correct shader variant
        scale_x = dst_w / src_width
        scale_y = dst_h / src_height
        radius_x = 2 if scale_x >= 1.0 else math.ceil(2.0 / scale_x)
        radius_y = 2 if scale_y >= 1.0 else math.ceil(2.0 / scale_y)

        need_adaptive = not (radius_x == 2 and radius_y == 2)
        self._ensure_shader_variant(adaptive=need_adaptive)

        # Pack constants according to the current format
        if self._current_variant == "fixed":
            data = struct.pack(
                CB_FORMAT_FIXED,
                *background_color,
                src_width,
                src_height,
                dst_width,
                dst_height,
                dst_x,
                dst_y,
                dst_w,
                dst_h,
                self.blur,
            )
        else:  # adaptive
            data = struct.pack(
                CB_FORMAT_ADAPTIVE,
                *background_color,  # 4 floats
                src_width,
                src_height,  # 2 uint32
                dst_width,
                dst_height,  # 2 uint32
                dst_x,
                dst_y,
                dst_w,
                dst_h,  # 4 int32
                radius_x,
                radius_y,  # 2 uint32
                self.blur,  # float
                self.antiring_strength,  # float
                1 if self.tight_antiring else 0,  # uint32 (bool)
            )

        self._cb.upload(data)

    def _ensure_shader_variant(self, adaptive: bool) -> None:
        """
        Switch to the desired shader variant if not already active.
        Rebuilds the compute pipeline when a change is necessary.
        """
        variant = "adaptive" if adaptive else "fixed"
        if variant == self._current_variant:
            return

        logger.debug("LanczosScaler switching to '%s'", variant)

        self._shader = self._shader_adapt if adaptive else self._shader_l2
        self._current_variant = variant
        self._cb_format = CB_FORMAT_ADAPTIVE if adaptive else CB_FORMAT_FIXED
        self._cb_size_current = CB_SIZE_ADAPTIVE if adaptive else CB_SIZE_FIXED

        # Rebuild the Vulkan pipeline with the new shader bytes
        self._rebuild_compute()
