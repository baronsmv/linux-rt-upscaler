import logging
import os
import struct
from typing import Optional, Tuple

from ...vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout - MUST match the HLSL `cbuffer Constants` block.
#
# Order in the HLSL shader:
#   float4 bgColor;                 // RGBA, 4x float
#   uint   srcWidth;                // source texture width
#   uint   srcHeight;               // source texture height
#   uint   dstTotalWidth;           // full output (screen) width
#   uint   dstTotalHeight;          // full output height
#   int    dstX, dstY, dstW, dstH;  // dest rectangle (int32)
#   float  blur;                    // kernel softness (1.0 = standard)
#   float  antiringStrength;        // 0.0 - 1.0
#   bool   linearLight;             // 4 bytes on GPU
#   bool   tightAntiring;           // 4 bytes on GPU
#
# Packed with Python struct:   'f' = float, 'I' = uint32, 'i' = int32
# ---------------------------------------------------------------------------
CB_FORMAT = "ffffIIIIiiiiffII"
CB_SIZE = struct.calcsize(CB_FORMAT)

# Default location of the compiled SPIR-V binary.
_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "lanczos.spv")


class LanczosScaler:
    """
    Adaptive Lanczos resampler - single-pass 2D scaling via compute shader.

    Maps an **upscaled** source texture (e.g. CuNNy or SRCNN output) onto a
    screen-sized destination texture using a Lanczos (window-sinc) filter.

    The filter radius adapts automatically inside the shader:
        - upscaling (scale ≥ 1.0)  -> radius 2 (Lanczos-2, sharp)
        - downscaling (scale < 1.0) -> ceil(2.0 / min(scale)), capped at 6

    Features exposed via the constant buffer:
        - `blur` - kernel softness (1.0 = standard Lanczos)
        - `antiring_strength` - soft anti-ringing clamp (0-1)
        - `linear_light` - sRGB ↔ linear conversion (recommended)
        - `tight_antiring` - use only central 2x2 for ringing bounds
          (True -> sharper text, False -> full-footprint clamp)

    Thread-group size: 16x16 The dispatch must cover the entire target texture.

    Attributes:
        source_texture (Texture2D | None): Input (upscaled) image.
        target_texture (Texture2D | None): Output (screen) texture.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        """Load the SPIR-V shader and create persistent Vulkan objects."""
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None  # constant buffer
        self._compute: Optional[Compute] = None  # compute pipeline

        self.source_texture: Optional[Texture2D] = None
        self.target_texture: Optional[Texture2D] = None

        # Serialised constant data - updated once per frame
        self._push_data: bytes = b""

        self._load_shader()
        self._create_persistent_resources()

    # ------------------------------------------------------------------
    # Public read-only helpers
    # ------------------------------------------------------------------

    @property
    def source_width(self) -> int:
        """Width of the source texture, or 0 if not set."""
        return self.source_texture.width if self.source_texture else 0

    @property
    def source_height(self) -> int:
        """Height of the source texture, or 0 if not set."""
        return self.source_texture.height if self.source_texture else 0

    # ------------------------------------------------------------------
    # Initialisation helpers (private)
    # ------------------------------------------------------------------

    def _load_shader(self) -> None:
        """Read the SPIR-V binary into memory."""
        try:
            with open(self._shader_path, "rb") as f:
                self._shader = f.read()
            logger.debug("Lanczos shader loaded from %s", self._shader_path)
        except OSError as e:
            raise RuntimeError(
                f"Failed to load Lanczos shader at {self._shader_path}: {e}"
            ) from e

    def _create_persistent_resources(self) -> None:
        """
        Create Vulkan resources that do not depend on the source or target textures:

        - A point-filtering sampler (required by hardware Gather instructions).
        - A constant buffer large enough to hold the `Constants` block.
        """
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )
        self._cb = Buffer(CB_SIZE)
        logger.debug("Lanczos sampler and constant buffer created")

    # ------------------------------------------------------------------
    # Texture binding
    # ------------------------------------------------------------------

    def set_source_texture(self, tex: Texture2D) -> None:
        """
        Bind a new upscaled source texture.

        If the object reference changes, the compute pipeline is rebuilt
        so that the descriptor set points to the new image.

        Args:
            tex: Fully upscaled image (output from the CuNNy/SRCNN stage).
        """
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()
        logger.debug("Lanczos source texture set to %dx%d", tex.width, tex.height)

    def set_target_texture(self, tex: Texture2D) -> None:
        """
        Bind a new target (screen) texture.

        Args:
            tex: Render target texture Must be `rgba8` and match the
                overlay dimensions.
        """
        if tex is self.target_texture:
            return
        self.target_texture = tex
        self._rebuild_compute()
        logger.debug("Lanczos target texture set to %dx%d", tex.width, tex.height)

    def resize_target(self, width: int, height: int) -> None:
        """
        Convenience method: create a new `rgba8` target texture of the given size.

        This replaces both `set_target_texture` and the on-the-fly texture creation
        for the common case of an opaque screen buffer.

        Args:
            width:  Desired width in pixels.
            height: Desired height in pixels.
        """
        if (
            self.target_texture
            and self.target_texture.width == width
            and self.target_texture.height == height
        ):
            return
        self.target_texture = Texture2D(width, height)
        self._rebuild_compute()
        logger.debug("Lanczos target texture resized to %dx%d", width, height)

    # ------------------------------------------------------------------
    # Constant buffer update
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
        blur: float = 1.0,
        antiring_strength: float = 1.0,
        linear_light: bool = True,
        tight_antiring: bool = True,
    ) -> None:
        """
        Pack scaling parameters into the constant buffer and upload to GPU.

        Must be called every frame (or whenever the layout changes) before
        dispatching the compute shader.

        Args:
            background_color: RGBA color used for letterbox / pillarbox.
            src_width, src_height: Dimensions of the upscaled source texture.
            dst_total_width, dst_total_height: Full screen texture size.
            dst_x, dst_y: Top-left corner of the actual content rectangle inside
                the screen texture.
            dst_w, dst_h: Width and height of that rectangle.
            blur: Kernel softness (1.0 = standard Lanczos, >1.0 = softer).
            antiring_strength: 0.0 = no anti-ringing, 1.0 = full hard clamp.
            linear_light: If True, process in linear light (sRGB-linear-sRGB).
                Recommended for correct luminance scaling.
            tight_antiring: If True, ringing bounds are taken only from the
                central 2x2 neighborhood - this preserves thin text details.
                Set to `False` for a more conservative full-footprint clamp.
        """
        self._push_data = struct.pack(
            CB_FORMAT,
            *background_color,  # 4 floats
            src_width,
            src_height,  # 2x uint32
            dst_total_width,
            dst_total_height,  # 2x uint32
            dst_x,
            dst_y,
            dst_w,
            dst_h,  # 4x int32
            blur,  # float
            antiring_strength,  # float
            1 if linear_light else 0,  # uint32 (bool)
            1 if tight_antiring else 0,  # uint32 (bool)
        )
        self._cb.upload(self._push_data)

    # ------------------------------------------------------------------
    # Pipeline management
    # ------------------------------------------------------------------

    def _rebuild_compute(self) -> None:
        """
        (Re)create the compute pipeline when source or target textures change.

        The pipeline binds:
            - `InputTex`  (t0) - source texture (SRV)
            - `OutputTex` (u0) - target texture (UAV)
            - `Constants` (b0) - constant buffer (CBV)
            - `PointSampler` (s0) - point sampler
        """
        if self.source_texture is None or self.target_texture is None:
            return
        self._compute = Compute(
            self._shader,
            srv=[self.source_texture],
            uav=[self.target_texture],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        logger.debug("Lanczos compute pipeline rebuilt")

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def dispatch_auto(self) -> None:
        """
        Dispatch the compute shader using the default workgroup grid.

        The grid is automatically computed from the current target texture:
            groups_x = ceil(width  / 16)
            groups_y = ceil(height / 16)

        Raises:
            RuntimeError: if source or target texture is not set.
        """
        self._check_ready()
        w, h = self.target_texture.width, self.target_texture.height
        self.dispatch((w + 15) // 16, (h + 15) // 16)

    def dispatch(self, groups_x: int, groups_y: int, groups_z: int = 1) -> None:
        """
        Execute the Lanczos compute pass.

        Args:
            groups_x: Number of 16-thread workgroups in X.
            groups_y: Number of 16-thread workgroups in Y.
            groups_z: Must be 1.

        Raises:
            RuntimeError: if the compute pipeline is not ready.
        """
        self._check_ready()
        self._compute.dispatch(groups_x, groups_y, groups_z)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_ready(self) -> None:
        """Verify that the compute pipeline is ready to dispatch."""
        if self._compute is None:
            raise RuntimeError(
                "Lanczos compute pipeline is not ready - "
                "call set_source_texture() and set_target_texture() first."
            )
