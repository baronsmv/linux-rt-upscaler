import gc
import logging
import time
from typing import Optional

from compushady import Swapchain, Texture2D
from compushady.formats import R8G8B8A8_UNORM

logger = logging.getLogger(__name__)


class SwapchainManager:
    """
    Manages a swapchain for presentation, handling recreation when needed.
    """

    def __init__(
        self,
        display_id: int,
        xid: int,
        width: int,
        height: int,
        present_mode: str,
    ):
        self.display_id = display_id
        self.xid = xid
        self.screen_width = width
        self.screen_height = height
        self.present_mode = present_mode
        self.swapchain: Optional[Swapchain] = None
        self.last_recreate_time = 0.0
        self._create_swapchain()

    def _create_swapchain(self) -> None:
        if self.screen_width == 0 or self.screen_height == 0:
            raise RuntimeError("Cannot create swapchain without screen dimensions")
        start = time.perf_counter()
        self.swapchain = Swapchain(
            (self.display_id, self.xid),
            R8G8B8A8_UNORM,
            4,
            present_mode=self.present_mode,
        )
        logger.debug(
            f"Swapchain created in {(time.perf_counter() - start)*1000:.2f} ms"
        )

    def recreate(self, new_width: int, new_height: int) -> None:
        now = time.time()
        if now - self.last_recreate_time < 1.0:  # at most once per second
            return
        self.last_recreate_time = now

        logger.info(f"Recreating swapchain with size {new_width}x{new_height}")
        self.screen_width = new_width
        self.screen_height = new_height

        # Explicitly destroy the old swapchain
        old = self.swapchain
        self.swapchain = None
        if old is not None:
            del old
            gc.collect()
            time.sleep(0.05)

        self._create_swapchain()

    def present(self, texture: Texture2D) -> None:
        if self.swapchain is None:
            raise RuntimeError("Swapchain not available")
        self.swapchain.present(texture)

    def needs_recreation(self) -> bool:
        return self.swapchain is None or self.swapchain.needs_recreation()

    def is_out_of_date(self) -> bool:
        return self.swapchain is not None and self.swapchain.is_out_of_date()

    def is_suboptimal(self) -> bool:
        return self.swapchain is not None and self.swapchain.is_suboptimal()
