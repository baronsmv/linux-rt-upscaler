import logging
import os
import struct
from typing import Optional, Tuple

from ...vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout for the adaptive Lanczos compute shader.
#
# The buffer must exactly match the `cbuffer Constants` declaration in the
# HLSL shader.  It contains (in order):
#   - 4 floats: background colour (RGBA)
#   - 4 uint32: srcWidth, srcHeight, dstTotalWidth, dstTotalHeight
#   - 4 int32:  dstX, dstY, dstW, dstH
#   - 1 float:  blur (kernel softness, 1.0 = standard Lanczos2)
#   - 1 float:  antiringStrength (0 = off, 1 = full hard clamp)
#   - 1 uint32: linearLight (1 = true, 0 = false)
#
# Any mismatch will cause undefined behaviour or visual corruption.
# ---------------------------------------------------------------------------
CB_FORMAT = "ffffIIIIiiiiffI"
CB_SIZE = struct.calcsize(CB_FORMAT)

# Default location of the compiled SPIR-V shader binary.
_SHADER_DIR = os.path.dirname(__file__)
DEFAULT_SHADER_PATH = os.path.join(_SHADER_DIR, "lanczos2.spv")


class LanczosScaler:
    """
    Adaptive Lanczos resampler - single-pass, high-quality 2D convolution.

    Maps an upscaled source texture onto a screen-sized destination texture
    using a window-sinc (Lanczos) filter.  The filter radius automatically
    adapts to the scaling factor:

    * **Upscaling** (scale ≥ 1.0) - radius 2, sharp Lanczos2.
    * **Downscaling** (scale < 1.0) - radius = ceil(2.0 / min(scale)),
      capped at 6, providing proper anti-aliasing.

    Quality controls are exposed via constant buffer parameters:

    * ``blur`` - kernel softness (1.0 = standard).
    * ``antiringStrength`` - soft clamping (0 = off, 1 = full hard clamp).
    * ``linearLight`` - enable linear-light resampling (sRGB -> linear -> sRGB).

    **Lifecycle**::

        1. Create a ``LanczosScaler`` instance.
        2. Set source and target textures via ``set_source_texture`` /
           ``set_target_texture`` (or ``resize_target``).
        3. Every frame, call ``update_constants`` with the destination
           rectangle and quality parameters.
        4. Call ``dispatch_auto()`` (or ``dispatch(gx, gy)``).

    .. note::

        The shader uses a 16x16 thread-group shared-memory cache for
        radius-2 upscaling, and a direct per-pixel convolution for
        larger downscaling radii.  This balances quality and speed.

    Attributes:
        source_texture (Texture2D | None): The input texture to scale
            (the fully upscaled SRCNN output).
        target_texture (Texture2D | None): The output texture that will
            receive the final scaled image.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        """
        Initialise the Lanczos scaler.

        Loads the SPIR-V shader from disk and creates shared Vulkan
        resources (point sampler, constant buffer).  The compute pipeline
        is built lazily when both source and target textures are set.

        Args:
            shader_path: Path to the compiled ``lanczos2.spv`` file.
                Defaults to the one next to this module.
        """
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None
        self._compute: Optional[Compute] = None

        self.source_texture: Optional[Texture2D] = None
        self.target_texture: Optional[Texture2D] = None

        # Serialised constant data - updated once per frame and uploaded
        # to the GPU buffer before dispatch.
        self._push_data: bytes = b""

        self._load_shader()
        self._create_resources()

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def source_width(self) -> int:
        """Width of the source texture in pixels, or 0 if not set."""
        return self.source_texture.width if self.source_texture else 0

    @property
    def source_height(self) -> int:
        """Height of the source texture in pixels, or 0 if not set."""
        return self.source_texture.height if self.source_texture else 0

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _load_shader(self) -> None:
        """Load the SPIR-V binary from disk into memory."""
        with open(self._shader_path, "rb") as f:
            self._shader = f.read()
        logger.debug("Lanczos shader loaded from %s", self._shader_path)

    def _create_resources(self) -> None:
        """
        Create long-lived Vulkan resources that are independent of
        the source or target textures.

        * A point-filtering sampler (used for hardware Gather calls
          in the shader).
        * A constant buffer large enough to hold the ``Constants``
          block.
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
        Set or replace the source (upscaled) texture.

        If the texture object changes, the compute pipeline is rebuilt
        so that the descriptor set points to the new image.

        Args:
            tex: The fully upscaled output from the SRCNN stage.
        """
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()
        logger.debug("Lanczos source texture set to %dx%d", tex.width, tex.height)

    def set_target_texture(self, tex: Texture2D) -> None:
        """
        Set or replace the target (screen) texture.

        If the texture object changes, the compute pipeline is rebuilt.

        Args:
            tex: The render texture (must be ``rgba8`` and match the
                overlay dimensions).
        """
        if tex is self.target_texture:
            return
        self.target_texture = tex
        self._rebuild_compute()
        logger.debug("Lanczos target texture set to %dx%d", tex.width, tex.height)

    def resize_target(self, width: int, height: int) -> None:
        """
        Resize the target texture, creating a new one.

        This convenience method replaces ``set_target_texture`` when
        you only need a plain ``rgba8`` texture of the given size.
        The compute pipeline is automatically rebuilt.

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
    ) -> None:
        """
        Serialise scaling parameters into the constant buffer.

        This must be called once per frame (or whenever the layout
        changes) before dispatching the compute shader.

        Args:
            background_color: RGBA colour for areas outside the
                destination rectangle (letterbox / pillarbox).
            src_width, src_height: Dimensions of the upscaled source.
            dst_total_width, dst_total_height: Full output (screen)
                texture dimensions.
            dst_x, dst_y: Top-left corner of the destination rectangle
                inside the screen texture.
            dst_w, dst_h: Width and height of the destination rectangle.
            blur: Kernel softness (1.0 = standard Lanczos2).
            antiring_strength: 0.0 disables anti-ringing;
                1.0 (default) applies the full hard clamp.
            linear_light: If ``True`` (default), the shader processes
                in linear light (sRGB -> linear -> sRGB).  Disabling
                this can improve text clarity on some content.
        """
        self._push_data = struct.pack(
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
            blur,
            antiring_strength,
            1 if linear_light else 0,
        )
        self._cb.upload(self._push_data)

    # ------------------------------------------------------------------
    # Pipeline management
    # ------------------------------------------------------------------

    def _rebuild_compute(self) -> None:
        """
        (Re)create the compute pipeline.

        Called automatically whenever the source or target texture changes.
        The pipeline binds:

        * ``InputTex``  (SRV / t0) - the source texture
        * ``OutputTex`` (UAV / u0) - the target texture
        * ``Constants`` (CBV / b0) - the constant buffer
        * ``PointSampler`` (sampler / s0) - a point filter
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
    # Public dispatch interface
    # ------------------------------------------------------------------

    def dispatch_auto(self) -> None:
        """
        Convenience dispatch that automatically computes the required
        workgroup counts from the target texture dimensions.

        Equivalent to::

            scaler.dispatch(
                (target.width  + 15) // 16,
                (target.height + 15) // 16,
            )
        """
        if self.target_texture is None:
            raise RuntimeError("No target texture set")
        w, h = self.target_texture.width, self.target_texture.height
        self.dispatch((w + 15) // 16, (h + 15) // 16)

    def dispatch(self, groups_x: int, groups_y: int, groups_z: int = 1) -> None:
        """
        Execute the Lanczos compute pass.

        The shader uses a 16x16 thread group.  The caller must provide
        enough groups to cover the full target texture (e.g., those
        computed by ``dispatch_auto``).

        Args:
            groups_x: Number of workgroups in X.
            groups_y: Number of workgroups in Y.
            groups_z: Number of workgroups in Z (always 1).
        """
        if self._compute is None:
            raise RuntimeError("Compute pipeline not ready")
        self._compute.dispatch(groups_x, groups_y, groups_z)
