import logging
import os
import struct
from typing import Dict, Optional

from ...vulkan import Buffer, Compute, Sampler, Texture2D, SAMPLER_FILTER_POINT

logger = logging.getLogger(__name__)

CB_SIZE = struct.calcsize("iiii")  # x, y, width, height

DEFAULT_SHADER_PATH = os.path.join(os.path.dirname(__file__), "overlay_blend.spv")


class OverlayBlender:
    """
    Blends an overlay texture onto a screen texture using premultiplied alpha.

    The shader reads the screen texture, blends the overlay on top, and writes
    back to the same screen texture. Compute pipelines are cached per overlay
    texture to avoid recreation on every frame.
    """

    def __init__(self, shader_path: str = DEFAULT_SHADER_PATH) -> None:
        """
        Initialize the overlay blender.

        Args:
            shader_path: Path to the compiled SPIR‑V shader.
        """
        self._shader_path = shader_path
        self._shader: Optional[bytes] = None
        self._sampler: Optional[Sampler] = None
        self._cb: Optional[Buffer] = None

        self._screen_tex: Optional[Texture2D] = None

        # Cache compute pipelines per overlay texture
        self._compute_cache: Dict[int, Compute] = {}

        self._load_shader()
        self._create_resources()

    # ----------------------------------------------------------------------
    # Initialisation
    # ----------------------------------------------------------------------
    def _load_shader(self) -> None:
        """Load SPIR‑V shader binary from disk."""
        with open(self._shader_path, "rb") as f:
            self._shader = f.read()
        logger.debug(f"Loaded overlay blend shader from {self._shader_path}")

    def _create_resources(self) -> None:
        """Create sampler and constant buffer (pipelines are cached on demand)."""
        self._sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )
        self._cb = Buffer(CB_SIZE)
        logger.debug("OverlayBlender resources created")

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def set_screen_texture(self, tex: Texture2D) -> None:
        """
        Set the screen texture to blend onto.

        The screen texture is used as both SRV (read) and UAV (write).
        Changing the screen texture invalidates the compute cache.
        """
        if tex is self._screen_tex:
            return
        self._screen_tex = tex
        self._compute_cache.clear()
        logger.debug(f"OverlayBlender screen texture set: {tex.width}x{tex.height}")

    def blend(
        self,
        overlay_tex: Texture2D,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        """
        Blend the overlay texture onto the screen texture.

        Args:
            overlay_tex: The overlay texture to blend (RGBA, premultiplied alpha).
            x, y: Top‑left position on the screen texture.
            width, height: Dimensions of the overlay texture.
        """
        if self._screen_tex is None:
            logger.warning("Cannot blend: screen texture not set")
            return

        # Get or create compute pipeline for this overlay texture
        compute = self._get_compute(overlay_tex)

        # Upload position and size constants
        cb_data = struct.pack("iiii", x, y, width, height)
        self._cb.upload(cb_data)

        # Dispatch compute groups (16x16 threads)
        groups_x = (width + 15) // 16
        groups_y = (height + 15) // 16
        compute.dispatch(groups_x, groups_y, 1)

    def clear_cache(self) -> None:
        """Clear the cached compute pipelines (e.g., on swapchain resize)."""
        self._compute_cache.clear()
        logger.debug("OverlayBlender compute cache cleared")

    # ----------------------------------------------------------------------
    # Internal
    # ----------------------------------------------------------------------
    def _get_compute(self, overlay_tex: Texture2D) -> Compute:
        """
        Return a cached compute pipeline for the given overlay texture.

        Pipelines are keyed by the overlay texture's ID to avoid recreation.
        """
        tex_id = id(overlay_tex)
        if tex_id not in self._compute_cache:
            compute = Compute(
                self._shader,
                srv=[self._screen_tex, overlay_tex],
                uav=[self._screen_tex],
                cbv=[self._cb],
                samplers=[self._sampler],
                push_size=0,
            )
            self._compute_cache[tex_id] = compute
            logger.debug(f"Created compute pipeline for overlay texture {tex_id}")
        return self._compute_cache[tex_id]
