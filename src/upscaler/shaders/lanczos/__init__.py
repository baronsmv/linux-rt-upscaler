import logging
import os
import struct
from typing import Optional, Tuple

from ..shader import ShaderPass
from ...vulkan import Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layouts for the two Lanczos shaders
# ---------------------------------------------------------------------------

# Lanczos Fixed (fixed radius 2) - no radiusX/radiusY fields
CB_FORMAT_FIXED = "ffffIIIIiiiiffII"
CB_SIZE_FIXED = struct.calcsize(CB_FORMAT_FIXED)

# Lanczos Adaptive (variable radius) - includes radiusX/radiusY
CB_FORMAT_ADAPTIVE = "ffffIIIIiiiiIIffII"
CB_SIZE_ADAPTIVE = struct.calcsize(CB_FORMAT_ADAPTIVE)

# Maximum buffer size needed (we allocate once and reuse)
CB_SIZE_MAX = max(CB_SIZE_FIXED, CB_SIZE_ADAPTIVE)

_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH_FIXED = os.path.join(_SHADER_DIR, "lanczos_fixed.spv")
DEFAULT_SHADER_PATH_ADAPTIVE = os.path.join(_SHADER_DIR, "lanczos_adaptive.spv")


class LanczosScaler(ShaderPass):
    """
    Adaptive Lanczos resampler - single-pass 2D scaling via compute shader.

    Internally uses two Vulkan compute shaders:
        * `lanczos_fixed.spv` - highly optimised for radius 2 (upscaling).
        * `lanczos_adaptive.spv` - general variable-radius path for
          downscaling or non-uniform scaling.

    The appropriate shader is chosen automatically based on the pre-computed
    filter radii.  Switching between shaders happens only when the scaling
    setup changes (e.g. after a window resize) - never per frame.

    Public API identical to other :class:`ShaderPass` subclasses.
    """

    def __init__(
        self,
        shader_path_l2: str = DEFAULT_SHADER_PATH_FIXED,
        shader_path_adapt: str = DEFAULT_SHADER_PATH_ADAPTIVE,
    ) -> None:
        self.source_texture: Optional[Texture2D] = None

        # Pre-load both SPIR-V binaries into memory.
        self._shader_l2 = None
        self._shader_adapt = None
        self._load_shader_variants(shader_path_l2, shader_path_adapt)

        # Initially use the adaptive shader (safe default).
        self._shader = self._shader_adapt
        self._current_variant = "adaptive"
        self._cb_format = CB_FORMAT_ADAPTIVE
        self._cb_size_current = CB_SIZE_ADAPTIVE

        # Let the base class handle persistent resources and pipeline creation.
        super().__init__(
            shader_path_adapt
        )  # path is ignored after _load_shader override

    # ------------------------------------------------------------------
    #  Constant buffer size - returns the maximum we ever need.
    # ------------------------------------------------------------------
    @staticmethod
    def _cb_size() -> int:
        return CB_SIZE_MAX

    # ------------------------------------------------------------------
    #  Override _load_shader to avoid loading from disk (we pre-loaded).
    # ------------------------------------------------------------------
    def _load_shader(self) -> None:
        # Do nothing - we already have the shader bytes.
        pass

    def _load_shader_variants(self, path_lanczos: str, path_adapt: str) -> None:
        """Read both SPIR-V binaries into memory."""
        try:
            with open(path_lanczos, "rb") as f:
                self._shader_l2 = f.read()
            logger.debug("Lanczos shader loaded from %s", path_lanczos)
        except OSError as e:
            raise RuntimeError(f"Failed to load Lanczos shader: {e}") from e

        try:
            with open(path_adapt, "rb") as f:
                self._shader_adapt = f.read()
            logger.debug("Adaptive Lanczos shader loaded from %s", path_adapt)
        except OSError as e:
            raise RuntimeError(f"Failed to load Lanczos adaptive shader: {e}") from e

    # ------------------------------------------------------------------
    #  Persistent resources (sampler + constant buffer)
    # ------------------------------------------------------------------
    def _create_persistent_resources(self) -> None:
        """Create constant buffer and point sampler."""
        # Base class would normally create a constant buffer of _cb_size().
        # We need to override to use our max size.
        super()._create_persistent_resources()  # creates self._cb with size CB_SIZE_MAX
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )

    # ------------------------------------------------------------------
    #  Binding layout - common to both shaders.
    # ------------------------------------------------------------------
    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], [self._sampler]

    # ------------------------------------------------------------------
    #  Rebuild compute (called by base when textures change)
    # ------------------------------------------------------------------
    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    # ------------------------------------------------------------------
    #  Set the input (upscaled) texture
    # ------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Constant buffer update - this is where we decide which shader to use
    # ------------------------------------------------------------------
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
        radius_x: int,
        radius_y: int,
        blur: float = 1.0,
        antiring_strength: float = 1.0,
        linear_light: bool = True,
        tight_antiring: bool = True,
    ) -> None:
        """
        Pack and upload the constant buffer, automatically selecting the
        optimal shader based on the computed filter radii.
        """
        # ---- 1. Select the correct shader variant ---------------------------
        need_adaptive = not (radius_x == 2 and radius_y == 2)
        self._ensure_shader_variant(adaptive=need_adaptive)

        # ---- 2. Pack constants according to the current format ---------------
        if self._current_variant == "fixed":
            data = struct.pack(
                CB_FORMAT_FIXED,
                *background_color,  # 4 floats
                src_width,
                src_height,  # 2 uint32
                dst_total_width,
                dst_total_height,  # 2 uint32
                dst_x,
                dst_y,
                dst_w,
                dst_h,  # 4 int32
                blur,  # float
                antiring_strength,  # float
                1 if linear_light else 0,  # uint32 (bool)
                1 if tight_antiring else 0,  # uint32 (bool)
            )
        else:  # adaptive
            data = struct.pack(
                CB_FORMAT_ADAPTIVE,
                *background_color,  # 4 floats
                src_width,
                src_height,  # 2 uint32
                dst_total_width,
                dst_total_height,  # 2 uint32
                dst_x,
                dst_y,
                dst_w,
                dst_h,  # 4 int32
                radius_x,
                radius_y,  # 2 uint32
                blur,  # float
                antiring_strength,  # float
                1 if linear_light else 0,  # uint32 (bool)
                1 if tight_antiring else 0,  # uint32 (bool)
            )

        # ---- 3. Upload -------------------------------------------------------
        self._cb.upload(data)

    # ------------------------------------------------------------------
    #  Shader switching logic
    # ------------------------------------------------------------------
    def _ensure_shader_variant(self, adaptive: bool) -> None:
        """
        Switch to the desired shader variant if not already active.
        Rebuilds the compute pipeline when a change is necessary.
        """
        variant = "adaptive" if adaptive else "fixed"
        if variant == self._current_variant:
            return

        logger.debug("LanczosScaler switching to %s", variant)

        self._shader = self._shader_adapt if adaptive else self._shader_l2
        self._current_variant = variant
        self._cb_format = CB_FORMAT_ADAPTIVE if adaptive else CB_FORMAT_FIXED
        self._cb_size_current = CB_SIZE_ADAPTIVE if adaptive else CB_SIZE_FIXED

        # Rebuild the Vulkan pipeline with the new shader bytes.
        self._rebuild_compute()

    # ------------------------------------------------------------------
    #  Convenience accessors
    # ------------------------------------------------------------------
    @property
    def source_width(self) -> int:
        return self.source_texture.width if self.source_texture else 0

    @property
    def source_height(self) -> int:
        return self.source_texture.height if self.source_texture else 0
