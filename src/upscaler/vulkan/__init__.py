"""
Vulkan backend for GPU compute and presentation (single-file version).

This module provides a Pythonic interface to the native Vulkan C extension.
All classes and context are defined here to avoid circular imports.
"""

import atexit
import os
from typing import List, Optional, Tuple, Union

from . import vulkan  # type: ignore

# ----------------------------------------------------------------------
# Constants (matching the C format table and original compushady)
# ----------------------------------------------------------------------
HEAP_DEFAULT = 0
HEAP_UPLOAD = 1
HEAP_READBACK = 2

SHADER_BINARY_TYPE_SPIRV = 1

SAMPLER_FILTER_POINT = 0
SAMPLER_FILTER_LINEAR = 1

SAMPLER_ADDRESS_MODE_WRAP = 0
SAMPLER_ADDRESS_MODE_MIRROR = 1
SAMPLER_ADDRESS_MODE_CLAMP = 2

# Pixel formats (indices must match C table)
R32G32B32A32_FLOAT = 2
R32G32B32A32_UINT = 3
R32G32B32A32_SINT = 4
R32G32B32_FLOAT = 6
R32G32B32_UINT = 7
R32G32B32_SINT = 8
R16G16B16A16_FLOAT = 10
R16G16B16A16_UNORM = 11
R16G16B16A16_UINT = 12
R16G16B16A16_SNORM = 13
R16G16B16A16_SINT = 14
R32G32_FLOAT = 16
R32G32_UINT = 17
R32G32_SINT = 18
R10G10B10A2_UNORM = 24
R10G10B10A2_UINT = 25
R8G8B8A8_UNORM = 28
R8G8B8A8_UNORM_SRGB = 29
R8G8B8A8_UINT = 30
R8G8B8A8_SNORM = 31
R8G8B8A8_SINT = 32
R16G16_FLOAT = 34
R16G16_UNORM = 35
R16G16_UINT = 36
R16G16_SNORM = 37
R16G16_SINT = 38
R32_FLOAT = 41
R32_UINT = 42
R32_SINT = 43
R8G8_UNORM = 49
R8G8_UINT = 50
R8G8_SNORM = 51
R8G8_SINT = 52
R16_FLOAT = 54
R16_UNORM = 55
R16_UINT = 57
R16_SNORM = 58
R16_SINT = 59
R8_UNORM = 61
R8_UINT = 62
R8_SNORM = 63
R8_SINT = 64
B8G8R8A8_UNORM = 87
B8G8R8A8_UNORM_SRGB = 91

_PIXEL_SIZE = {
    R32G32B32A32_FLOAT: 16,
    R32G32B32A32_UINT: 16,
    R32G32B32A32_SINT: 16,
    R32G32B32_FLOAT: 12,
    R32G32B32_UINT: 12,
    R32G32B32_SINT: 12,
    R16G16B16A16_FLOAT: 8,
    R16G16B16A16_UNORM: 8,
    R16G16B16A16_UINT: 8,
    R16G16B16A16_SNORM: 8,
    R16G16B16A16_SINT: 8,
    R32G32_FLOAT: 8,
    R32G32_UINT: 8,
    R32G32_SINT: 8,
    R10G10B10A2_UNORM: 4,
    R10G10B10A2_UINT: 4,
    R8G8B8A8_UNORM: 4,
    R8G8B8A8_UNORM_SRGB: 4,
    R8G8B8A8_UINT: 4,
    R8G8B8A8_SNORM: 4,
    R8G8B8A8_SINT: 4,
    R16G16_FLOAT: 4,
    R16G16_UNORM: 4,
    R16G16_UINT: 4,
    R16G16_SNORM: 4,
    R16G16_SINT: 4,
    R32_FLOAT: 4,
    R32_UINT: 4,
    R32_SINT: 4,
    R8G8_UNORM: 2,
    R8G8_UINT: 2,
    R8G8_SNORM: 2,
    R8G8_SINT: 2,
    R16_FLOAT: 2,
    R16_UNORM: 2,
    R16_UINT: 2,
    R16_SNORM: 2,
    R16_SINT: 2,
    R8_UNORM: 1,
    R8_UINT: 1,
    R8_SNORM: 1,
    R8_SINT: 1,
    B8G8R8A8_UNORM: 4,
    B8G8R8A8_UNORM_SRGB: 4,
}


def get_pixel_size(fmt: int) -> int:
    return _PIXEL_SIZE[fmt]


# ----------------------------------------------------------------------
# VulkanContext (holds device selection and debug state)
# ----------------------------------------------------------------------
class VulkanContext:
    __slots__ = (
        "_discovered_devices",
        "_current_device",
        "_debug_enabled",
        "_cleanup_registered",
    )

    def __init__(self) -> None:
        self._discovered_devices: Optional[List["Device"]] = None
        self._current_device: Optional["Device"] = None
        self._debug_enabled: bool = False
        self._cleanup_registered: bool = False

    def _cleanup(self) -> None:
        if self._current_device is not None:
            self._current_device.wait_idle()

    def enable_debug(self) -> None:
        if not self._debug_enabled:
            vulkan.enable_debug()
            self._debug_enabled = True
            if not self._cleanup_registered:
                atexit.register(self._cleanup)
                self._cleanup_registered = True

    def get_shader_binary_type(self) -> int:
        return vulkan.get_shader_binary_type()

    def get_discovered_devices(self) -> List["Device"]:
        if self._discovered_devices is None:
            raw_list = vulkan.get_discovered_devices()
            self._discovered_devices = [Device._from_handle(d) for d in raw_list]
        return self._discovered_devices

    def set_current_device(self, index: int) -> None:
        devices = self.get_discovered_devices()
        if index < 0 or index >= len(devices):
            raise IndexError(f"Device index {index} out of range (0..{len(devices)-1})")
        self._current_device = devices[index]

    def get_current_device(self) -> "Device":
        if self._current_device is None:
            self._current_device = self.get_best_device()
        return self._current_device

    def get_best_device(self) -> "Device":
        devices = self.get_discovered_devices()
        if not devices:
            raise RuntimeError("No Vulkan devices found")
        env = os.environ.get("VULKAN_DEVICE")
        if env is not None:
            try:
                return devices[int(env)]
            except (ValueError, IndexError):
                pass

        def key(d: "Device") -> tuple:
            return (d.is_hardware, d.is_discrete, d.dedicated_video_memory)

        return sorted(devices, key=key)[-1]


# Global default context
_default_context = VulkanContext()


# ----------------------------------------------------------------------
# Module-level convenience functions (delegate to default context)
# ----------------------------------------------------------------------
def enable_debug() -> None:
    _default_context.enable_debug()


def get_shader_binary_type() -> int:
    return _default_context.get_shader_binary_type()


def get_discovered_devices() -> List["Device"]:
    return _default_context.get_discovered_devices()


def set_current_device(index: int) -> None:
    _default_context.set_current_device(index)


def get_current_device() -> "Device":
    return _default_context.get_current_device()


def get_best_device() -> "Device":
    return _default_context.get_best_device()


def configure_device(buffer_pool_size: int = 0) -> None:
    """Set performance options on the current Vulkan device."""
    dev = get_current_device()
    if buffer_pool_size:
        dev.set_buffer_pool_size(buffer_pool_size)


# ----------------------------------------------------------------------
# Device wrapper
# ----------------------------------------------------------------------
class Device:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use get_discovered_devices() to obtain Device instances")

    @classmethod
    def _from_handle(cls, handle):
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
        self._handle.set_buffer_pool_size(size)

    def wait_idle(self) -> None:
        self._handle.wait_idle()

    def get_debug_messages(self) -> List[str]:
        return self._handle.get_debug_messages()

    def create_heap(self, heap_type: int, size: int) -> "Heap":
        return Heap._from_handle(self._handle.create_heap(heap_type, size))

    def create_buffer(
        self,
        heap_type: int,
        size: int,
        stride: int,
        format: int,
        heap_handle,
        heap_offset: int,
        sparse: bool,
    ):
        # Internal method used by Buffer.__init__
        return self._handle.create_buffer(
            heap_type, size, stride, format, heap_handle, heap_offset, sparse
        )

    def create_texture2d(
        self,
        width: int,
        height: int,
        format: int,
        heap_handle,
        heap_offset: int,
        slices: int,
        sparse: bool,
    ):
        # Internal method used by Texture2D.__init__
        return self._handle.create_texture2d(
            width, height, format, heap_handle, heap_offset, slices, sparse
        )

    def create_sampler(
        self,
        address_u: int,
        address_v: int,
        address_w: int,
        filter_min: int,
        filter_mag: int,
    ):
        return self._handle.create_sampler(
            address_u, address_v, address_w, filter_min, filter_mag
        )

    def create_compute(
        self,
        shader: bytes,
        cbv_handles: List,
        srv_handles: List,
        uav_handles: List,
        sampler_handles: List,
        push_size: int,
        bindless_max: int,
    ):
        return self._handle.create_compute(
            shader,
            cbv_handles,
            srv_handles,
            uav_handles,
            sampler_handles,
            push_size,
            bindless_max,
        )

    def create_swapchain(
        self,
        window_handle: tuple,
        format: int,
        num_buffers: int,
        width: int,
        height: int,
        present_mode: str,
    ):
        return self._handle.create_swapchain(
            window_handle, format, num_buffers, width, height, present_mode
        )

    def __repr__(self) -> str:
        return f"<Device '{self.name}' vendor=0x{self.vendor_id:04x}>"


# ----------------------------------------------------------------------
# Heap
# ----------------------------------------------------------------------
class Heap:
    __slots__ = ("_handle",)

    def __init__(self, heap_type: int, size: int, device: Optional[Device] = None):
        dev = device or get_current_device()
        self._handle = dev.create_heap(heap_type, size)

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def size(self) -> int:
        return self._handle.size

    @property
    def heap_type(self) -> int:
        return self._handle.heap_type

    def __repr__(self) -> str:
        return f"<Heap type={self.heap_type} size={self.size}>"


# ----------------------------------------------------------------------
# Resource base
# ----------------------------------------------------------------------
class Resource:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_* methods or subclass constructors")

    @property
    def size(self) -> int:
        return self._handle.size

    @property
    def heap_size(self) -> int:
        return self._handle.heap_size

    @property
    def tiles_x(self) -> int:
        return self._handle.tiles_x

    @property
    def tiles_y(self) -> int:
        return self._handle.tiles_y

    @property
    def tiles_z(self) -> int:
        return self._handle.tiles_z

    @property
    def tile_width(self) -> int:
        return self._handle.tile_width

    @property
    def tile_height(self) -> int:
        return self._handle.tile_height

    @property
    def tile_depth(self) -> int:
        return self._handle.tile_depth

    def copy_to(
        self,
        destination: "Resource",
        size: int = 0,
        src_offset: int = 0,
        dst_offset: int = 0,
        width: int = 0,
        height: int = 0,
        depth: int = 0,
        src_x: int = 0,
        src_y: int = 0,
        src_z: int = 0,
        dst_x: int = 0,
        dst_y: int = 0,
        dst_z: int = 0,
        src_slice: int = 0,
        dst_slice: int = 0,
    ) -> None:
        self._handle.copy_to(
            destination._handle,
            size,
            src_offset,
            dst_offset,
            width,
            height,
            depth,
            src_x,
            src_y,
            src_z,
            dst_x,
            dst_y,
            dst_z,
            src_slice,
            dst_slice,
        )

    def bind_tile(
        self,
        x: int,
        y: int,
        z: int,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        slice: int = 0,
    ) -> None:
        self._handle.bind_tile(
            x, y, z, heap._handle if heap else None, heap_offset, slice
        )


# ----------------------------------------------------------------------
# Buffer
# ----------------------------------------------------------------------
class Buffer(Resource):
    __slots__ = ()

    def __init__(
        self,
        size: int,
        heap_type: int = HEAP_DEFAULT,
        stride: int = 0,
        format: int = 0,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        sparse: bool = False,
        device: Optional[Device] = None,
    ):
        dev = device or get_current_device()
        handle = dev.create_buffer(
            heap_type,
            size,
            stride,
            format,
            heap._handle if heap else None,
            heap_offset,
            sparse,
        )
        self._handle = handle

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def upload(self, data: bytes, offset: int = 0) -> None:
        self._handle.upload(data, offset)

    def upload2d(
        self, data: bytes, pitch: int, width: int, height: int, bpp: int
    ) -> None:
        self._handle.upload2d(data, pitch, width, height, bpp)

    def readback(self, size: int = 0, offset: int = 0) -> bytes:
        return self._handle.readback(size, offset)

    def __repr__(self) -> str:
        return f"<Buffer size={self.size}>"


# ----------------------------------------------------------------------
# Texture1D (placeholder, not fully implemented in C)
# ----------------------------------------------------------------------
class Texture1D(Resource):
    __slots__ = ()

    def __init__(
        self,
        width: int,
        format: int,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        slices: int = 1,
        sparse: bool = False,
        device: Optional[Device] = None,
    ):
        # The C backend does not yet support Texture1D, but we stub it for compatibility.
        # In practice, you can fallback to a 2D texture with height=1 if needed.
        raise NotImplementedError("Texture1D not yet implemented in Vulkan C backend")

    @property
    def width(self) -> int:
        return self._handle.width

    @property
    def slices(self) -> int:
        return self._handle.slices

    @property
    def row_pitch(self) -> int:
        return self._handle.row_pitch


# ----------------------------------------------------------------------
# Texture2D
# ----------------------------------------------------------------------
class Texture2D(Resource):
    __slots__ = ()

    def __init__(
        self,
        width: int,
        height: int,
        format: int,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        slices: int = 1,
        sparse: bool = False,
        device: Optional[Device] = None,
    ):
        dev = device or get_current_device()
        handle = dev.create_texture2d(
            width,
            height,
            format,
            heap._handle if heap else None,
            heap_offset,
            slices,
            sparse,
        )
        self._handle = handle

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def width(self) -> int:
        return self._handle.width

    @property
    def height(self) -> int:
        return self._handle.height

    @property
    def slices(self) -> int:
        return self._handle.slices

    @property
    def row_pitch(self) -> int:
        return self._handle.row_pitch

    def download(self) -> bytes:
        return self._handle.download()

    def download_regions(self, regions: List[Tuple[int, int, int, int]]) -> List[bytes]:
        return self._handle.download_regions(regions)

    def upload_subresource(
        self, data: bytes, x: int, y: int, width: int, height: int
    ) -> None:
        self._handle.upload_subresource(data, x, y, width, height)

    def upload_subresources(
        self, rects: List[Tuple[bytes, int, int, int, int]]
    ) -> None:
        self._handle.upload_subresources(rects)

    def __repr__(self) -> str:
        return f"<Texture2D {self.width}x{self.height}>"


# ----------------------------------------------------------------------
# Texture3D (placeholder)
# ----------------------------------------------------------------------
class Texture3D(Resource):
    __slots__ = ()

    def __init__(
        self,
        width: int,
        height: int,
        depth: int,
        format: int,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        sparse: bool = False,
        device: Optional[Device] = None,
    ):
        raise NotImplementedError("Texture3D not yet implemented in Vulkan C backend")

    @property
    def width(self) -> int:
        return self._handle.width

    @property
    def height(self) -> int:
        return self._handle.height

    @property
    def depth(self) -> int:
        return self._handle.depth

    @property
    def row_pitch(self) -> int:
        return self._handle.row_pitch


# ----------------------------------------------------------------------
# Sampler
# ----------------------------------------------------------------------
class Sampler:
    __slots__ = ("_handle",)

    def __init__(
        self,
        address_mode_u: int = SAMPLER_ADDRESS_MODE_WRAP,
        address_mode_v: int = SAMPLER_ADDRESS_MODE_WRAP,
        address_mode_w: int = SAMPLER_ADDRESS_MODE_WRAP,
        filter_min: int = SAMPLER_FILTER_POINT,
        filter_mag: int = SAMPLER_FILTER_POINT,
        device: Optional[Device] = None,
    ):
        dev = device or get_current_device()
        self._handle = dev.create_sampler(
            address_mode_u, address_mode_v, address_mode_w, filter_min, filter_mag
        )

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def __repr__(self) -> str:
        return "<Sampler>"


# ----------------------------------------------------------------------
# Compute
# ----------------------------------------------------------------------
class Compute:
    __slots__ = ("_handle",)

    def __init__(
        self,
        shader: bytes,
        cbv: Optional[List[Union[Buffer, Texture2D]]] = None,
        srv: Optional[List[Union[Buffer, Texture2D]]] = None,
        uav: Optional[List[Union[Buffer, Texture2D]]] = None,
        samplers: Optional[List[Sampler]] = None,
        push_size: int = 0,
        bindless: bool = False,
        max_bindless: int = 64,
        device: Optional[Device] = None,
    ):
        dev = device or get_current_device()
        cbv_handles = [r._handle for r in (cbv or [])]
        srv_handles = [r._handle for r in (srv or [])]
        uav_handles = [r._handle for r in (uav or [])]
        sampler_handles = [s._handle for s in (samplers or [])]
        self._handle = dev.create_compute(
            shader,
            cbv_handles,
            srv_handles,
            uav_handles,
            sampler_handles,
            push_size,
            max_bindless if bindless else 0,
        )

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def dispatch(self, x: int, y: int, z: int, push: bytes = b"") -> None:
        self._handle.dispatch(x, y, z, push)

    def dispatch_indirect(
        self, indirect_buffer: Buffer, offset: int = 0, push: bytes = b""
    ) -> None:
        self._handle.dispatch_indirect(indirect_buffer._handle, offset, push)

    def dispatch_sequence(
        self,
        sequence: List[Tuple["Compute", int, int, int, bytes]],
        copy_src: Optional[Buffer] = None,
        copy_dst: Optional[Texture2D] = None,
        copy_slice: int = 0,
        present_image: Optional[Texture2D] = None,
        timestamps: bool = False,
    ) -> Optional[Tuple[None, List[float]]]:
        seq = [(c._handle, x, y, z, p) for c, x, y, z, p in sequence]
        src = copy_src._handle if copy_src else None
        dst = copy_dst._handle if copy_dst else None
        pres = present_image._handle if present_image else None
        return self._handle.dispatch_sequence(
            sequence=seq,
            copy_src=src,
            copy_dst=dst,
            copy_slice=copy_slice,
            present_image=pres,
            timestamps=timestamps,
        )

    def dispatch_tiles(
        self,
        tiles: List[Tuple[int, int, bytes]],
        tile_width: int,
        tile_height: int,
    ) -> None:
        self._handle.dispatch_tiles(tiles, tile_width, tile_height)

    def bind_cbv(self, index: int, resource: Union[Buffer, Texture2D]) -> None:
        self._handle.bind_cbv(index, resource._handle)

    def bind_srv(self, index: int, resource: Union[Buffer, Texture2D]) -> None:
        self._handle.bind_srv(index, resource._handle)

    def bind_uav(self, index: int, resource: Union[Buffer, Texture2D]) -> None:
        self._handle.bind_uav(index, resource._handle)

    def __repr__(self) -> str:
        return "<Compute>"


# ----------------------------------------------------------------------
# Swapchain
# ----------------------------------------------------------------------
class Swapchain:
    __slots__ = ("_handle",)

    def __init__(
        self,
        window_handle: tuple,
        format: int,
        num_buffers: int = 3,
        device: Optional[Device] = None,
        width: int = 0,
        height: int = 0,
        present_mode: str = "fifo",
    ):
        dev = device or get_current_device()
        self._handle = dev.create_swapchain(
            window_handle, format, num_buffers, width, height, present_mode
        )

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def width(self) -> int:
        return self._handle.width

    @property
    def height(self) -> int:
        return self._handle.height

    def present(
        self, texture: Texture2D, x: int = 0, y: int = 0, wait_for_fence: bool = True
    ) -> None:
        self._handle.present(texture._handle, x, y, wait_for_fence)

    def is_suboptimal(self) -> bool:
        return self._handle.is_suboptimal()

    def is_out_of_date(self) -> bool:
        return self._handle.is_out_of_date()

    def needs_recreation(self) -> bool:
        return self._handle.needs_recreation()

    def __repr__(self) -> str:
        return f"<Swapchain {self.width}x{self.height}>"
