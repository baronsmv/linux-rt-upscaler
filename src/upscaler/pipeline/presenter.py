import logging
from typing import List, TYPE_CHECKING

from ..config import Config
from ..shaders import LanczosScaler
from ..utils import calculate_scaling_rect
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .osd import OSDManager

logger = logging.getLogger(__name__)


class Presenter:
    """
    Handles final scaling (Lanczos), OSD overlay, and swapchain presentation.

    The presenter maintains a screen-sized texture that serves as the render
    target. It uses a LanczosScaler to scale the upscaled source into the
    appropriate destination rectangle, then optionally blends an OSD message
    on top.

    Attributes:
        screen_width (int): Physical overlay width in pixels.
        screen_height (int): Physical overlay height in pixels.
        content_width (int): Logical content width (before scaling).
        content_height (int): Logical content height (before scaling).
        scale_mode (str): Scaling mode ("fit", "fill", "stretch").
        background_color (BackgroundColor): RGBA clear color for unused areas.
        offset_x (int): Horizontal offset for the content rectangle.
        offset_y (int): Vertical offset for the content rectangle.
        osd (OSDManager): OSD manager for status messages.
        swapchain (SwapchainManager): Presentation swapchain.
        screen_tex (Texture2D): Render target texture.
        lanczos (LanczosScaler): Lanczos2 scaling pipeline.
        groups_x, groups_y (int): Dispatch groups for Lanczos.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        content_width: int,
        content_height: int,
        scale_mode: str,
        config: Config,
        osd_manager: "OSDManager",
        swapchain_manager,
    ) -> None:
        """
        Initialize the presenter.

        Args:
            screen_width, screen_height: Overlay window dimensions.
            content_width, content_height: Logical content dimensions.
            scale_mode: One of "fit", "fill", "stretch".
            background_color: RGBA tuple for background areas.
            offset_x, offset_y: Additional offset for the content rectangle.
            osd_manager: OSD manager instance.
            swapchain_manager: Swapchain manager for presentation.
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.content_width = content_width
        self.content_height = content_height
        self.scale_mode = scale_mode
        self.background_color = config.background_color
        self.offset_x = config.offset_x
        self.offset_y = config.offset_y
        self.lanczos_blur = config.lanczos_blur
        self.osd = osd_manager
        self.swapchain = swapchain_manager

        # Screen texture (render target)
        self.screen_tex = Texture2D(screen_width, screen_height)

        # Lanczos scaler
        self.lanczos = LanczosScaler()
        self.lanczos.set_target_texture(self.screen_tex)

        # Dispatch groups for Lanczos (16x16 threads per group)
        self.groups_x = (screen_width + 15) // 16
        self.groups_y = (screen_height + 15) // 16

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def set_source_texture(self, texture: Texture2D) -> None:
        """
        Set the upscaled source texture for Lanczos scaling.

        Args:
            texture: The fully upscaled texture (output of UpscalerManager).
        """
        self.lanczos.set_source_texture(texture)

    def update_lanczos_constants(self, src_width: int, src_height: int) -> None:
        """
        Calculate destination rectangle and update Lanczos constants.

        This must be called whenever the source texture dimensions change
        (e.g., after crop resize or model switch).

        Args:
            src_width: Width of the source texture.
            src_height: Height of the source texture.
        """
        # Calculate the rectangle within content area where the scaled image will go
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            src_width,
            src_height,
            self.content_width,
            self.content_height,
            self.scale_mode,
        )

        # Center the content area on screen
        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2
        dst_x = canvas_x + r_x + self.offset_x
        dst_y = canvas_y + r_y + self.offset_y

        if r_w <= 0 or r_h <= 0:
            logger.warning(f"Invalid Lanczos rect: {r_w}x{r_h}, skipping update")
            return

        self.lanczos.update_constants(
            self.background_color,
            src_width,
            src_height,
            self.screen_width,
            self.screen_height,
            dst_x,
            dst_y,
            r_w,
            r_h,
            blur=self.lanczos_blur,  # blur factor (1.0 = standard Lanczos2)
        )

    def present(self, wait_for_fence: bool = False) -> None:
        """
        Execute Lanczos scaling, blend OSD, and present to swapchain.

        Args:
            wait_for_fence: If True, block until presentation completes.
        """
        # 1. Dispatch Lanczos (writes to self.screen_tex)
        self.lanczos.compute.dispatch(self.groups_x, self.groups_y, 1)

        # 2. Blend OSD (if active) - modifies self.screen_tex in place
        self.osd.blend_active(self.screen_tex)

        # 3. Present to swapchain
        self.swapchain.present(self.screen_tex, wait_for_fence=wait_for_fence)

    def get_scaling_rect(self, scale_factor: float) -> List[float]:
        """
        Return the rectangle (in overlay coordinates) where content is drawn.

        Used by the overlay window to map mouse events.

        Args:
            scale_factor: Scale factor from logical to physical pixels.

        Returns:
            List [x, y, width, height] in overlay widget coordinates.
        """
        src_tex = self.lanczos.source_texture
        if src_tex is None:
            return [0, 0, 0, 0]

        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            src_tex.width,
            src_tex.height,
            self.content_width,
            self.content_height,
            self.scale_mode,
        )

        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2
        dst_x = canvas_x + r_x + self.offset_x
        dst_y = canvas_y + r_y + self.offset_y

        return [
            dst_x / scale_factor,
            dst_y / scale_factor,
            r_w / scale_factor,
            r_h / scale_factor,
        ]

    def resize(self, new_width: int, new_height: int) -> None:
        """
        Handle overlay window resize.

        Args:
            new_width: New overlay width in pixels.
            new_height: New overlay height in pixels.
        """
        self.screen_width = new_width
        self.screen_height = new_height
        self.screen_tex = Texture2D(new_width, new_height)
        self.lanczos.set_target_texture(self.screen_tex)
        self.groups_x = (new_width + 15) // 16
        self.groups_y = (new_height + 15) // 16

        # Clear OSD compute cache since screen texture changed
        self.osd.clear_compute_cache()
