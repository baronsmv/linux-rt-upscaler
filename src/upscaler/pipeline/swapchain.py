import gc
import logging
import threading
import time
import xcffib
from typing import Optional
from xcffib import ffi

from ..vulkan import Swapchain, Texture2D

logger = logging.getLogger(__name__)


class SwapchainManager:
    """
    Manages a swapchain for presentation, handling recreation when needed.
    Uses a dedicated XCB connection for Vulkan surface creation.
    """

    def __init__(
        self,
        xid: int,
        width: int,
        height: int,
        present_mode: str,
    ):
        self.xid = xid
        self.screen_width = width
        self.screen_height = height
        self.present_mode = present_mode
        self.swapchain: Optional[Swapchain] = None
        self.last_recreate_time = 0.0
        self._lock = threading.Lock()

        # Open dedicated XCB connection for Vulkan
        self._xcb_conn = xcffib.connect()
        # Extract raw xcb_connection_t* as integer using CFFI cast
        self._xcb_conn_ptr = int(ffi.cast("uintptr_t", self._xcb_conn._conn))

        self._create_swapchain()

    def _create_swapchain(self) -> None:
        if self.screen_width == 0 or self.screen_height == 0:
            raise RuntimeError("Cannot create swapchain without screen dimensions")
        start = time.perf_counter()
        self.swapchain = Swapchain(
            (self._xcb_conn_ptr, self.xid),
            num_buffers=4,
            present_mode=self.present_mode,
        )
        logger.debug(
            f"Swapchain created in {(time.perf_counter() - start)*1000:.2f} ms"
        )

    def recreate(self, new_width: int, new_height: int) -> None:
        with self._lock:
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

    def present(self, texture: Texture2D, wait_for_fence: bool = True) -> None:
        if self.swapchain is None:
            raise RuntimeError("Swapchain not available")
        with self._lock:
            self.swapchain.present(texture, wait_for_fence=wait_for_fence)

    def needs_recreation(self) -> bool:
        return self.swapchain is None or self.swapchain.needs_recreation()

    def is_out_of_date(self) -> bool:
        return self.swapchain is not None and self.swapchain.is_out_of_date()

    def is_suboptimal(self) -> bool:
        return self.swapchain is not None and self.swapchain.is_suboptimal()

    def close(self) -> None:
        """Close the XCB connection and cleanup."""
        self.swapchain = None
        if hasattr(self, "_xcb_conn") and self._xcb_conn:
            self._xcb_conn.disconnect()
            self._xcb_conn = None
