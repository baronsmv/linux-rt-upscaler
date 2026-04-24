import logging
import threading
import time
from typing import Optional

import xcffib
from xcffib import ffi

from ..vulkan import Swapchain, Texture2D, get_current_device

logger = logging.getLogger(__name__)


class SwapchainManager:
    """
    Manages a Vulkan swapchain for presentation to an X11 window.

    Handles swapchain creation, recreation (e.g., on resize), and presentation.
    Uses a dedicated XCB connection for surface creation, independent of other
    X11 usage in the application.

    Thread-safe for use from the pipeline thread.
    """

    def __init__(
        self,
        xid: int,
        width: int,
        height: int,
        present_mode: str = "fifo",
        min_recreate_interval: float = 1.0,
    ) -> None:
        """
        Initialize the swapchain manager.

        Args:
            xid: X11 window ID to present to.
            width: Initial swapchain width in pixels.
            height: Initial swapchain height in pixels.
            present_mode: Vulkan present mode ("fifo", "mailbox", "immediate").
            min_recreate_interval: Minimum seconds between recreations (debounce).

        Raises:
            RuntimeError: If width or height is zero, or XCB connection fails.
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")

        self._xid = xid
        self._width = width
        self._height = height
        self._present_mode = present_mode
        self._min_recreate_interval = min_recreate_interval

        self._swapchain: Optional[Swapchain] = None
        self._last_recreate_time: float = 0.0
        self._lock = threading.Lock()

        # Open dedicated XCB connection for Vulkan surface
        try:
            self._xcb_conn = xcffib.connect()
        except Exception as e:
            raise RuntimeError(f"Failed to open XCB connection: {e}") from e

        # Extract raw pointer as integer for Vulkan surface creation
        self._xcb_conn_ptr = int(ffi.cast("uintptr_t", self._xcb_conn._conn))

        self._create_swapchain()
        logger.info(
            f"SwapchainManager initialized: {width}x{height}, mode={present_mode}"
        )

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def present(self, texture: Texture2D, wait_for_fence: bool = True) -> None:
        """
        Present a texture to the swapchain.

        Args:
            texture: The texture to present (must match swapchain dimensions).
            wait_for_fence: If True, block until presentation completes.

        Raises:
            RuntimeError: If the swapchain is not available.
        """
        with self._lock:
            if self._swapchain is None:
                raise RuntimeError("Swapchain not available")
            self._swapchain.present(texture, wait_for_fence=wait_for_fence)

    def recreate(self, new_width: int, new_height: int) -> None:
        """
        Recreate the swapchain with new dimensions.

        Debounced to at most once per `min_recreate_interval` seconds.

        Args:
            new_width: New width in pixels.
            new_height: New height in pixels.
        """
        if new_width <= 0 or new_height <= 0:
            logger.warning(f"Ignoring invalid swapchain size: {new_width}x{new_height}")
            return

        with self._lock:
            now = time.time()
            if now - self._last_recreate_time < self._min_recreate_interval:
                return
            self._last_recreate_time = now

            logger.info(
                f"Recreating swapchain: {self._width}x{self._height} -> {new_width}x{new_height}"
            )
            self._width = new_width
            self._height = new_height

            # Destroy old swapchain (Vulkan will handle pending frames)
            if self._swapchain is not None:
                # The Swapchain object's destructor will clean up Vulkan resources
                self._swapchain = None

            self._create_swapchain()

    def wait_for_last_present(self, timeout_ns: int = 1_000_000_000) -> bool:
        """
        Wait for the fence from the most recent present() call to be signalled.

        This must be called **before** the CPU starts writing to any GPU
        resource that is reused across frames (e.g., staging buffers,
        input textures).  It guarantees that the GPU has finished all work
        related to the previous frame, including the final image copy for
        presentation.

        Returns:
            True if the fence was signalled, False on timeout.
        """
        if self._swapchain is None:
            return True
        fence = self._swapchain.get_last_fence()
        if fence is None:
            return True  # first frame, nothing to wait for
        dev = get_current_device()
        return dev.wait_for_fences([fence], wait_all=True, timeout_ns=timeout_ns)

    def needs_recreation(self) -> bool:
        """Return True if the swapchain is invalid and needs recreation."""
        with self._lock:
            return self._swapchain is None or self._swapchain.needs_recreation()

    def is_out_of_date(self) -> bool:
        """Return True if the swapchain is out-of-date (e.g., surface resized)."""
        with self._lock:
            return self._swapchain is not None and self._swapchain.is_out_of_date()

    def is_suboptimal(self) -> bool:
        """Return True if the swapchain is suboptimal (e.g., different present mode)."""
        with self._lock:
            return self._swapchain is not None and self._swapchain.is_suboptimal()

    def close(self) -> None:
        """Close the XCB connection and release Vulkan resources."""
        with self._lock:
            self._swapchain = None
            if hasattr(self, "_xcb_conn") and self._xcb_conn:
                try:
                    self._xcb_conn.disconnect()
                except Exception as e:
                    logger.warning(f"Error closing XCB connection: {e}")
                self._xcb_conn = None
        logger.debug("SwapchainManager closed")

    # ----------------------------------------------------------------------
    # Internal
    # ----------------------------------------------------------------------
    def _create_swapchain(self) -> None:
        """Create a new swapchain with the current dimensions."""
        start = time.perf_counter()
        try:
            self._swapchain = Swapchain(
                (self._xcb_conn_ptr, self._xid),
                present_mode=self._present_mode,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create swapchain: {e}") from e

        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"Swapchain created in {elapsed:.2f} ms")
