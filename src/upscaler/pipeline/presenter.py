import logging
from typing import List, TYPE_CHECKING

from ..shaders import LanczosScaler
from ..utils import calculate_scaling_rect
from ..vulkan import Texture2D

if TYPE_CHECKING:
    from .osd import OSDManager
    from ..config import BackgroundColor

logger = logging.getLogger(__name__)


class Presenter:
    """
    Handles final scaling (Lanczos), OSD overlay, and swapchain presentation.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        content_width: int,
        content_height: int,
        scale_mode: str,
        background_color: "BackgroundColor",
        offset_x: int,
        offset_y: int,
        osd_manager: "OSDManager",
        swapchain_manager,
    ) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.content_width = content_width
        self.content_height = content_height
        self.scale_mode = scale_mode
        self.background_color = background_color
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.osd = osd_manager
        self.swapchain = swapchain_manager

        # Screen texture (render target)
        self.screen_tex = Texture2D(screen_width, screen_height)

        # Lanczos scaler
        self.lanczos = LanczosScaler()
        self.lanczos.set_target_texture(self.screen_tex)

        # Dispatch groups for Lanczos
        self.groups_x = (screen_width + 15) // 16
        self.groups_y = (screen_height + 15) // 16

    def set_source_texture(self, texture: Texture2D) -> None:
        """Set the upscaled source texture for Lanczos scaling."""
        self.lanczos.set_source_texture(texture)

    def update_lanczos_constants(self, src_width: int, src_height: int) -> None:
        """Calculate destination rectangle and update Lanczos constants."""
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            src_width,
            src_height,
            self.content_width,
            self.content_height,
            self.scale_mode,
        )
        canvas_x = (self.screen_width - self.content_width) // 2
        canvas_y = (self.screen_height - self.content_height) // 2
        dst_x = canvas_x + r_x + self.offset_x
        dst_y = canvas_y + r_y + self.offset_y

        if r_w <= 0 or r_h <= 0:
            logger.warning(f"Invalid Lanczos rect: {r_w}x{r_h}, skipping")
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
            1.0,  # blur
        )

    def present(self, wait_for_fence: bool = False) -> None:
        """
        Execute Lanczos (+ optional OSD) and present to swapchain.
        Assumes source texture and constants are already set.
        """
        # Build dispatches: Lanczos + optional OSD
        dispatches = [(self.lanczos.compute, self.groups_x, self.groups_y, 1, b"")]

        osd_tex, needs_redraw = self.osd.update()
        if osd_tex is not None:
            osd_w = osd_tex.width
            osd_h = osd_tex.height
            osd_x = (self.screen_width - osd_w) // 2
            osd_y = (self.screen_height - osd_h) // 2
            self.osd.update_constants(osd_x, osd_y, osd_w, osd_h)
            osd_compute = self.osd.get_compute_pipeline(osd_tex, self.screen_tex)
            groups_x = (osd_w + 15) // 16
            groups_y = (osd_h + 15) // 16
            dispatches.append((osd_compute, groups_x, groups_y, 1, b""))

        # Submit all in one command buffer
        self.lanczos.compute.dispatch_sequence(
            sequence=dispatches,
            present_image=self.screen_tex,
        )

        # Swapchain present
        self.swapchain.present(self.screen_tex, wait_for_fence=wait_for_fence)

    def get_scaling_rect(self, scale_factor: float) -> List[float]:
        """Return the rectangle (in overlay coordinates) where content is drawn."""
        r_x, r_y, r_w, r_h = calculate_scaling_rect(
            self.lanczos.source_width,
            self.lanczos.source_height,
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
        """Handle overlay window resize."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.screen_tex = Texture2D(new_width, new_height)
        self.lanczos.set_target_texture(self.screen_tex)
        self.groups_x = (new_width + 15) // 16
        self.groups_y = (new_height + 15) // 16
