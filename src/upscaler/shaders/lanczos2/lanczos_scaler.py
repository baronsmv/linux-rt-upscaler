import logging
import os
import struct
from typing import Optional, Tuple

from ...vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constant buffer layout for the Lanczos compute shader.
#
# The buffer contains the following fields, in order:
#   - 4 floats: background colour (RGBA)
#   - 4 uint32: srcWidth, srcHeight, dstTotalWidth, dstTotalHeight
#   - 4 int32:  dstX, dstY, dstW, dstH
#   - 1 float:  blur (kernel width, 1.0 = standard Lanczos2)
#   - 1 float:  antiringStrength (0 = off, 1 = full hard clamp)
#   - 1 uint32: linearLight (1 = true, 0 = false)
#
# This layout must exactly match the `cbuffer Constants` declaration in
# the HLSL shader (`lanczos2.hlsl`). Any mismatch will cause undefined
# behaviour or visual corruption.
# ---------------------------------------------------------------------------
CB_FORMAT = "ffffIIIIiiiiffI"
CB_SIZE = struct.calcsize(CB_FORMAT)

# Default location of the compiled SPIR-V shader binary.
DEFAULT_SHADER_PATH = os.path.join(os.path.dirname(__file__), "lanczos2.spv")


class LanczosScaler:
    """
    Lanczos2 scaling via an optimized compute shader.

    Translates an upscaled source texture onto a screen-sized destination
    texture with a high-quality Lanczos2 filter. The destination rectangle
    can be arbitrarily placed and sized within the output, allowing
    “fit” / “fill” / “stretch” layout modes. Areas outside the destination
    are filled with a solid background color.

    The shader used by this class is an improved version of the original
    Magpie Lanczos2 effect. It includes:

    * **Thread-group shared memory** - drastically reduces texture
      bandwidth by loading each source texel only once per workgroup.
    * **Adaptive kernel** - automatically switches to Catmull-Rom when
      the scale factor is below 1.6x, reducing overshoot for near-1:1
      scaling.
    * **Soft anti-ringing** - controlled via `antiring_strength` (0 = no
      clamp, 1 = hard clamp like the original).
    * **Linear-light toggle** - the sRGB-linear-sRGB processing can be
      disabled via `linear_light = False`, which can improve the look of
      UI text.

    **Lifecycle**::
        1. Create a `LanczosScaler` instance.
        2. Call `set_source_texture` / `set_target_texture` (or `resize_target`).
        3. Every frame, call `update_constants` to set the destination
           rectangle and quality parameters.
        4. Dispatch the compute pipeline via `self.compute.dispatch(x, y, z)`.

    Attributes:
        source_texture (Texture2D | None): The input texture to scale
            (the fully upscaled SRCNN output).
        target_texture (Texture2D | None): The output texture that will be
            written to (usually the screen-sized render target).
        compute (Compute | None): The Vulkan compute pipeline, created
            automatically when both textures are set.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        """
        Initialise the Lanczos scaler.

        Loads the SPIR-V shader from disk and creates shared resources
        (sampler, constant buffer). The actual compute pipeline is built
        lazily when both source and target textures are available.

        Args:
            shader_path: Path to a compiled SPIR-V binary for the
                Lanczos2 compute shader. Defaults to lanczos2.spv
                in the same directory as this module.
        """
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None

        self.compute: Optional[Compute] = None
        self.source_texture: Optional[Texture2D] = None
        self.target_texture: Optional[Texture2D] = None

        # Cached serialized constant data - updated once per frame and
        # uploaded to the GPU buffer just before dispatch.
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
        Create long-lived Vulkan resources that do not depend on the
        source / target textures.

        * A point-filtering sampler (required for the `Gather` calls).
        * A constant buffer sized to hold the full `Constants` block.
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
        so that the new descriptor set points to the correct image.

        Args:
            tex: The upscaled output from the SRCNN stage.
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
            tex: The render texture (must be rgba8 and match the
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

        This is a convenience method that replaces set_target_texture
        when you only need a plain rgba8 texture of the given size.
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
        Serialize scaling parameters into the constant buffer.

        This must be called once per frame (or whenever the layout
        changes) before dispatching the compute shader.

        Args:
            background_color: RGBA color used for areas outside the
                destination rectangle (e.g., letterboxing).
            src_width, src_height: Dimensions of the upscaled source.
            dst_total_width, dst_total_height: Full output (screen)
                texture dimensions.
            dst_x, dst_y: Top-left corner of the destination rectangle
                within the screen texture.
            dst_w, dst_h: Width and height of the destination rectangle.
            blur: Kernel width (1.0 = standard Lanczos2). Larger values
                produce softer results.
            antiring_strength: 0.0 disables anti-ringing entirely;
                1.0 (default) applies the full hard clamp.
            linear_light: If True (default), the shader squares the
                source samples before convolution and takes the square
                root of the result, preserving luminance energy.
                Disabling this can improve text clarity on some content.
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
        - InputTex (SRV): source texture
        - OutputTex (UAV): target texture
        - Constants (CBV): constant buffer
        - PointSampler (sampler): point-sampler
        """
        if self.source_texture is None or self.target_texture is None:
            return
        self.compute = Compute(
            self._shader,
            srv=[self.source_texture],
            uav=[self.target_texture],
            cbv=[self._cb],
            samplers=[self._sampler],
            push_size=0,
        )
        logger.debug("Lanczos compute pipeline rebuilt")
