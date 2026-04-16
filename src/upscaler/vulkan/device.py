"""Device class – represents a Vulkan physical/logical device."""

from typing import List, Optional, Union

from . import vulkan
from .compute import Compute
from .constants import HEAP_DEFAULT
from .heap import Heap
from .resource import Buffer, Texture2D
from .sampler import Sampler
from .swapchain import Swapchain


class Device:
    """Vulkan device handle."""

    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use get_discovered_devices() to obtain Device instances")

    @classmethod
    def _from_handle(cls, handle):
        """Internal: create Device from C handle."""
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def name(self) -> str:
        return self._handle.name

    @property
    def dedicated_video_memory(self) -> int:
        return self._handle.dedicated_video_memory

    @property
    def dedicated_system_memory(self) -> int:
        return self._handle.dedicated_system_memory

    @property
    def shared_system_memory(self) -> int:
        return self._handle.shared_system_memory

    @property
    def vendor_id(self) -> int:
        return self._handle.vendor_id

    @property
    def device_id(self) -> int:
        return self._handle.device_id

    @property
    def is_hardware(self) -> bool:
        return bool(self._handle.is_hardware)

    @property
    def is_discrete(self) -> bool:
        return bool(self._handle.is_discrete)

    def set_buffer_pool_size(self, size: int) -> None:
        """Set the number of reusable staging buffers."""
        self._handle.set_buffer_pool_size(size)

    def wait_idle(self) -> None:
        """Block until all GPU work finishes."""
        self._handle.wait_idle()

    def get_debug_messages(self) -> List[str]:
        """Retrieve and clear Vulkan validation messages."""
        return self._handle.get_debug_messages()

    def create_heap(self, heap_type: int, size: int) -> Heap:
        """Create a memory heap."""
        return Heap._from_handle(self._handle.create_heap(heap_type, size))

    def create_buffer(
        self,
        size: int,
        heap_type: int = HEAP_DEFAULT,
        stride: int = 0,
        format: int = 0,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        sparse: bool = False,
    ) -> Buffer:
        """Create a buffer resource."""
        return Buffer._from_handle(
            self._handle.create_buffer(
                heap_type,
                size,
                stride,
                format,
                heap._handle if heap else None,
                heap_offset,
                sparse,
            )
        )

    def create_texture2d(
        self,
        width: int,
        height: int,
        format: int,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        slices: int = 1,
        sparse: bool = False,
    ) -> Texture2D:
        """Create a 2D texture resource."""
        return Texture2D._from_handle(
            self._handle.create_texture2d(
                width,
                height,
                format,
                heap._handle if heap else None,
                heap_offset,
                slices,
                sparse,
            )
        )

    def create_sampler(
        self,
        address_mode_u: int = 0,
        address_mode_v: int = 0,
        address_mode_w: int = 0,
        filter_min: int = 0,
        filter_mag: int = 0,
    ) -> Sampler:
        """Create a sampler object."""
        return Sampler._from_handle(
            self._handle.create_sampler(
                address_mode_u, address_mode_v, address_mode_w, filter_min, filter_mag
            )
        )

    def create_compute(
        self,
        shader: bytes,
        cbv: Optional[List[Union[Buffer, Texture2D]]] = None,
        srv: Optional[List[Union[Buffer, Texture2D]]] = None,
        uav: Optional[List[Union[Buffer, Texture2D]]] = None,
        samplers: Optional[List[Sampler]] = None,
        push_size: int = 0,
        bindless: bool = False,
        max_bindless: int = 64,
    ) -> Compute:
        """Create a compute pipeline from SPIR‑V."""
        cbv_handles = [r._handle for r in (cbv or [])]
        srv_handles = [r._handle for r in (srv or [])]
        uav_handles = [r._handle for r in (uav or [])]
        sampler_handles = [s._handle for s in (samplers or [])]
        return Compute._from_handle(
            self._handle.create_compute(
                shader,
                cbv_handles,
                srv_handles,
                uav_handles,
                sampler_handles,
                push_size,
                max_bindless if bindless else 0,
            )
        )

    def create_swapchain(
        self,
        window_handle: tuple,
        format: int,
        num_buffers: int = 3,
        width: int = 0,
        height: int = 0,
        present_mode: str = "fifo",
    ) -> Swapchain:
        """Create a swapchain for presentation."""
        return Swapchain._from_handle(
            self._handle.create_swapchain(
                window_handle, format, num_buffers, width, height, present_mode
            )
        )

    def __repr__(self) -> str:
        return f"<Device '{self.name}' vendor=0x{self.vendor_id:04x}>"
