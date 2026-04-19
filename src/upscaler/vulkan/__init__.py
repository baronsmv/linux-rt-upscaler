import atexit
import os
from typing import List, Optional, Tuple, Union

from . import vulkan as _vk  # type: ignore

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
# Heap types
HEAP_DEFAULT = 0
HEAP_UPLOAD = 1
HEAP_READBACK = 2

# Shader binary type (only SPIR‑V is supported)
SHADER_BINARY_TYPE_SPIRV = 1

# Sampler filters
SAMPLER_FILTER_POINT = 0
SAMPLER_FILTER_LINEAR = 1

# Sampler address modes
SAMPLER_ADDRESS_MODE_WRAP = 0
SAMPLER_ADDRESS_MODE_MIRROR = 1
SAMPLER_ADDRESS_MODE_CLAMP = 2

# Pixel formats (indices must match the C++ format table)
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


# ----------------------------------------------------------------------
# Vulkan Context (device selection and debug)
# ----------------------------------------------------------------------
class VulkanContext:
    """
    Holds Vulkan state for a specific execution context.

    Manages device discovery, selection, and debug settings.
    Multiple contexts can coexist independently.

    Attributes:
        discovered_devices (List[Device]): Cached list of available devices.
        current_device (Device): Currently active logical device.
        debug_enabled (bool): Whether validation layers are active.
    """

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
        """Wait for the current device to idle (called at process exit)."""
        if self._current_device is not None:
            self._current_device.wait_idle()

    def enable_debug(self) -> None:
        """
        Enable Vulkan validation layers and debug output.

        This must be called before any device creation to take effect.
        """
        if not self._debug_enabled:
            _vk.enable_debug()
            self._debug_enabled = True
            if not self._cleanup_registered:
                atexit.register(self._cleanup)
                self._cleanup_registered = True

    def get_shader_binary_type(self) -> int:
        """Return the shader binary type supported (SPIR‑V = 1)."""
        return _vk.get_shader_binary_type()

    def get_discovered_devices(self) -> List["Device"]:
        """
        Return a list of all available Vulkan devices.

        The list is cached after the first call.
        """
        if self._discovered_devices is None:
            raw_list = _vk.get_discovered_devices()
            self._discovered_devices = [Device.from_handle(d) for d in raw_list]
        return self._discovered_devices

    def set_current_device(self, index: int) -> None:
        """
        Set the currently active device by index.

        Args:
            index: Index into the list returned by `get_discovered_devices()`.

        Raises:
            IndexError: If the index is out of range.
        """
        devices = self.get_discovered_devices()
        if index < 0 or index >= len(devices):
            raise IndexError(f"Device index {index} out of range (0..{len(devices)-1})")
        self._current_device = devices[index]

    def get_current_device(self) -> "Device":
        """
        Return the currently active device.

        If no device has been set, automatically selects the best available.
        """
        if self._current_device is None:
            self._current_device = self.get_best_device()
        return self._current_device

    def get_best_device(self) -> "Device":
        """
        Select the best available device.

        Preference order:
            1. Device specified by the `VULKAN_DEVICE` environment variable (index).
            2. Discrete GPU with the most dedicated video memory.
            3. Any hardware‑accelerated device.

        Raises:
            RuntimeError: If no Vulkan devices are found.
        """
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


# Global default context for simple scripts
_default_context = VulkanContext()


# ----------------------------------------------------------------------
# Module‑level convenience functions (delegate to default context)
# ----------------------------------------------------------------------
def enable_debug() -> None:
    """Enable Vulkan validation layers (uses default context)."""
    _default_context.enable_debug()


def get_shader_binary_type() -> int:
    """Return the shader binary type (uses default context)."""
    return _default_context.get_shader_binary_type()


def get_discovered_devices() -> List["Device"]:
    """Return a list of available devices (uses default context)."""
    return _default_context.get_discovered_devices()


def set_current_device(index: int) -> None:
    """Set the current device for the default context."""
    _default_context.set_current_device(index)


def get_current_device() -> "Device":
    """Return the current device from the default context."""
    return _default_context.get_current_device()


def get_best_device() -> "Device":
    """Select the best device (uses default context)."""
    return _default_context.get_best_device()


def configure_device(buffer_pool_size: int = 0) -> None:
    """
    Set the staging buffer pool size on the current device.

    Args:
        buffer_pool_size: Number of reusable staging buffers.
    """
    dev = get_current_device()
    if buffer_pool_size:
        dev.set_buffer_pool_size(buffer_pool_size)


def device_wait_idle() -> None:
    """Wait for the Vulkan device to finish all queued work."""
    dev = get_current_device()
    dev.wait_idle()


# ----------------------------------------------------------------------
# Device
# ----------------------------------------------------------------------
class Device:
    """
    Vulkan physical/logical device.

    Provides methods to create resources (buffers, textures, etc.).
    Instances are obtained via `get_discovered_devices()`.

    Attributes:
        name (str): Device name (e.g., 'NVIDIA GeForce RTX 3060').
        dedicated_video_memory (int): Dedicated video memory in bytes.
        dedicated_system_memory (int): Dedicated system memory in bytes.
        shared_system_memory (int): Shared system memory in bytes.
        vendor_id (int): PCI vendor ID.
        device_id (int): PCI device ID.
        is_hardware (bool): True if hardware‑accelerated.
        is_discrete (bool): True if discrete GPU.
    """

    __slots__ = ("_handle",)

    def __init__(self) -> None:
        raise TypeError("Use get_discovered_devices() to obtain Device instances")

    @classmethod
    def from_handle(cls, handle):
        """Internal: create Device from C++ handle."""
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

    def create_heap(self, heap_type: int, size: int) -> "Heap":
        """
        Create a memory heap.

        Args:
            heap_type: One of HEAP_DEFAULT, HEAP_UPLOAD, HEAP_READBACK.
            size: Size in bytes.

        Returns:
            A new Heap object.
        """
        return Heap.from_handle(self._handle.create_heap(heap_type, size))

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
        """Internal method used by Buffer.__init__."""
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
        """Internal method used by Texture2D.__init__."""
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
        """Internal method used by Sampler.__init__."""
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
        """Internal method used by Compute.__init__."""
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
        """Internal method used by Swapchain.__init__."""
        return self._handle.create_swapchain(
            window_handle, format, num_buffers, width, height, present_mode
        )

    def __repr__(self) -> str:
        return f"<Device '{self.name}' vendor=0x{self.vendor_id:04x}>"


# ----------------------------------------------------------------------
# Heap
# ----------------------------------------------------------------------
class Heap:
    """
    A contiguous block of GPU memory.

    Attributes:
        size (int): Size of the heap in bytes.
        heap_type (int): Heap type (0=DEFAULT, 1=UPLOAD, 2=READBACK).
    """

    __slots__ = ("_handle",)

    def __init__(self, heap_type: int, size: int, device: Optional[Device] = None):
        """
        Create a new heap.

        Args:
            heap_type: HEAP_DEFAULT, HEAP_UPLOAD, or HEAP_READBACK.
            size: Size in bytes.
            device: Optional device (uses current if None).
        """
        dev = device or get_current_device()
        self._handle = dev.create_heap(heap_type, size)

    @classmethod
    def from_handle(cls, handle):
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
        type_names = ["DEFAULT", "UPLOAD", "READBACK"]
        type_str = type_names[self.heap_type] if self.heap_type < 3 else "UNKNOWN"
        return f"<Heap type={type_str} size={self.size}>"


# ----------------------------------------------------------------------
# Resource (base class)
# ----------------------------------------------------------------------
class Resource:
    """
    Base class for buffers and textures.

    This class should not be instantiated directly.
    """

    __slots__ = ("_handle",)

    def __init__(self) -> None:
        pass

    @property
    def size(self) -> int:
        """Size of the resource in bytes."""
        return self._handle.size

    @property
    def heap_size(self) -> int:
        """Actual memory size allocated."""
        return self._handle.heap_size

    @property
    def tiles_x(self) -> int:
        """Number of sparse tiles in X direction."""
        return self._handle.tiles_x

    @property
    def tiles_y(self) -> int:
        """Number of sparse tiles in Y direction."""
        return self._handle.tiles_y

    @property
    def tiles_z(self) -> int:
        """Number of sparse tiles in Z direction."""
        return self._handle.tiles_z

    @property
    def tile_width(self) -> int:
        """Tile width in pixels (sparse)."""
        return self._handle.tile_width

    @property
    def tile_height(self) -> int:
        """Tile height in pixels (sparse)."""
        return self._handle.tile_height

    @property
    def tile_depth(self) -> int:
        """Tile depth in pixels (sparse)."""
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
        """
        Copy data to another resource.

        The exact meaning of parameters depends on the source and destination types.
        """
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


# ----------------------------------------------------------------------
# Buffer
# ----------------------------------------------------------------------
class Buffer(Resource):
    """
    A linear GPU buffer.

    Supports upload, readback, and use as constant buffer, storage buffer,
    or indirect argument buffer.

    Example:
        buf = Buffer(1024, heap_type=HEAP_UPLOAD)
        buf.upload(b"Hello")
        data = buf.readback()
    """

    __slots__ = ()

    def __init__(
        self,
        size: int,
        heap_type: int = HEAP_UPLOAD,
        stride: int = 0,
        format: int = R8G8B8A8_UNORM,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        sparse: bool = False,
        device: Optional[Device] = None,
    ) -> None:
        """
        Create a buffer.

        Args:
            size: Size in bytes.
            heap_type: Memory type (DEFAULT, UPLOAD, READBACK).
            stride: For structured buffers.
            format: Pixel format for formatted buffers (0 = none).
            heap: Optional heap to sub‑allocate from.
            heap_offset: Offset within the heap.
            sparse: Create as a sparse resource.
            device: Optional device (uses current if None).
        """
        dev = device or get_current_device()
        self._handle = dev.create_buffer(
            heap_type,
            size,
            stride,
            format,
            heap._handle if heap else None,
            heap_offset,
            sparse,
        )

    @classmethod
    def from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def upload(self, data: bytes, offset: int = 0) -> None:
        """Upload data to the buffer at the given offset."""
        self._handle.upload(data, offset)

    def __repr__(self) -> str:
        return f"<Buffer size={self.size}>"


# ----------------------------------------------------------------------
# Texture2D
# ----------------------------------------------------------------------
class Texture2D(Resource):
    """
    A 2D texture resource.

    Can be used as shader resource (SRV) or unordered access (UAV).
    Supports sub‑region uploads and downloads.

    Example:
        tex = Texture2D(1920, 1080, B8G8R8A8_UNORM)
        tex.upload_subresource(pixel_data, 0, 0, 1920, 1080)
    """

    __slots__ = ()

    def __init__(
        self,
        width: int,
        height: int,
        format: int = R8G8B8A8_UNORM,
        heap: Optional[Heap] = None,
        heap_offset: int = 0,
        slices: int = 1,
        sparse: bool = False,
        device: Optional[Device] = None,
    ) -> None:
        """
        Create a 2D texture.

        Args:
            width: Width in pixels.
            height: Height in pixels.
            format: Pixel format constant (e.g., R8G8B8A8_UNORM).
            heap: Optional heap to sub‑allocate from.
            heap_offset: Offset within the heap.
            slices: Number of array slices.
            sparse: Create as a sparse resource.
            device: Optional device (uses current if None).
        """
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
    def from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def width(self) -> int:
        """Width in pixels."""
        return self._handle.width

    @property
    def height(self) -> int:
        """Height in pixels."""
        return self._handle.height

    @property
    def slices(self) -> int:
        """Number of array slices."""
        return self._handle.slices

    @property
    def row_pitch(self) -> int:
        """Row pitch in bytes."""
        return self._handle.row_pitch

    def download(self) -> bytes:
        """Download entire texture contents as RGBA8 bytes."""
        return self._handle.download()

    def upload_subresources(self, rects: List[Tuple]) -> None:
        """
        Batch upload rectangles to a texture (optionally to a specific array slice).

        Args:
            rects: List of tuples. Each tuple can be:
                - (data, x, y, width, height)           # slice 0
                - (data, x, y, width, height, slice)    # specific slice
        """
        normalized = []
        for t in rects:
            if len(t) == 5:
                normalized.append(t + (0,))
            elif len(t) == 6:
                normalized.append(t)
            else:
                raise ValueError(
                    "Each rect must be a 5‑ or 6‑tuple (data, x, y, width, height[, slice])"
                )
        self._handle.upload_subresources(normalized)

    def clear_color(self, r: float, g: float, b: float, a: float) -> None:
        self._handle.clear_color(r, g, b, a)

    def __repr__(self) -> str:
        return f"<Texture2D {self.width}x{self.height}>"


# ----------------------------------------------------------------------
# Sampler
# ----------------------------------------------------------------------
class Sampler:
    """
    Texture sampler configuration.

    Controls how textures are sampled in shaders (filtering, addressing).
    """

    __slots__ = ("_handle",)

    def __init__(
        self,
        address_mode_u: int = SAMPLER_ADDRESS_MODE_CLAMP,
        address_mode_v: int = SAMPLER_ADDRESS_MODE_CLAMP,
        address_mode_w: int = SAMPLER_ADDRESS_MODE_CLAMP,
        filter_min: int = SAMPLER_FILTER_POINT,
        filter_mag: int = SAMPLER_FILTER_POINT,
        device: Optional[Device] = None,
    ) -> None:
        """
        Create a sampler.

        Args:
            address_mode_u/v/w: WRAP, MIRROR, or CLAMP.
            filter_min/mag: POINT or LINEAR.
            device: Optional device (uses current if None).
        """
        dev = device or get_current_device()
        self._handle = dev.create_sampler(
            address_mode_u, address_mode_v, address_mode_w, filter_min, filter_mag
        )

    @classmethod
    def from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def __repr__(self) -> str:
        return "<Sampler>"


# ----------------------------------------------------------------------
# Compute Pipeline
# ----------------------------------------------------------------------
class Compute:
    """
    Compute pipeline.

    Executes SPIR‑V compute shaders with bound resources.

    Example:
        shader = open("shader.spv", "rb").read()
        comp = Compute(shader, cbv=[buf1], srv=[tex1], uav=[tex2])
        comp.dispatch(8, 8, 1)
    """

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
    ) -> None:
        """
        Create a compute pipeline.

        Args:
            shader: SPIR‑V bytecode.
            cbv: List of constant buffer views.
            srv: List of shader resource views.
            uav: List of unordered access views.
            samplers: List of samplers.
            push_size: Size of push constant block (bytes).
            bindless: Enable bindless resource indexing.
            max_bindless: Maximum number of bindless slots.
            device: Optional device (uses current if None).
        """
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
    def from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def dispatch(self, x: int, y: int, z: int, push: bytes = b"") -> None:
        """
        Dispatch compute workgroups.

        Args:
            x, y, z: Number of workgroups in each dimension.
            push: Optional push constant data.
        """
        self._handle.dispatch(x, y, z, push)

    def dispatch_sequence(
        self,
        sequence: List[Tuple["Compute", int, int, int, bytes]],
        copy_src: Optional[Buffer] = None,
        copy_dst: Optional[Texture2D] = None,
        copy_slice: int = 0,
        present_image: Optional[Texture2D] = None,
        timestamps: bool = False,
    ) -> Optional[Tuple[None, List[float]]]:
        """
        Submit a sequence of dispatches with optional pre/post copies.

        Args:
            sequence: List of (compute, x, y, z, push_data) tuples.
            copy_src: Buffer to copy from before dispatches.
            copy_dst: Texture to copy to.
            copy_slice: Destination texture slice.
            present_image: Texture to transition for presentation.
            timestamps: If True, return GPU timings.

        Returns:
            None, or (None, timestamps_list) if timestamps=True.
        """
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

    def __repr__(self) -> str:
        return "<Compute>"


# ----------------------------------------------------------------------
# Swapchain
# ----------------------------------------------------------------------
class Swapchain:
    """
    Presentation swapchain.

    Manages a queue of presentable images for displaying on screen.

    Example:
        # On X11: window_handle = (display, window)
        sc = Swapchain((display, window), B8G8R8A8_UNORM, num_buffers=3)
        sc.present(texture)
    """

    __slots__ = ("_handle",)

    def __init__(
        self,
        window_handle: Tuple,
        num_buffers: int = 3,
        format: int = R8G8B8A8_UNORM,
        device: Optional[Device] = None,
        width: int = 0,
        height: int = 0,
        present_mode: str = "fifo",
    ) -> None:
        """
        Create a swapchain.

        Args:
            window_handle: Platform‑specific tuple:
                X11: (display_ptr, window_id)
                Wayland: (wl_display_ptr, wl_surface_ptr)
            format: Pixel format (e.g., B8G8R8A8_UNORM).
            num_buffers: Number of swapchain images (default 3).
            device: Optional device (uses current if None).
            width, height: Desired dimensions (0 = use surface's).
            present_mode: "fifo", "mailbox", "immediate", "fifo_relaxed".
        """
        dev = device or get_current_device()
        handle = dev.create_swapchain(
            window_handle, format, num_buffers, width, height, present_mode
        )
        if handle is None:
            # The C++ layer has set a Python exception; re-raise it
            raise RuntimeError("Failed to create swapchain") from None
        self._handle = handle

    @classmethod
    def from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def width(self) -> int:
        """Swapchain width in pixels."""
        return self._handle.width

    @property
    def height(self) -> int:
        """Swapchain height in pixels."""
        return self._handle.height

    def present(
        self, texture: Texture2D, x: int = 0, y: int = 0, wait_for_fence: bool = True
    ) -> None:
        """
        Present a texture to the swapchain.

        Args:
            texture: Texture2D to present.
            x, y: Offset within the swapchain (top‑left).
            wait_for_fence: If True, block until presentation completes.
        """
        self._handle.present(texture._handle, x, y, wait_for_fence)

    def is_suboptimal(self) -> bool:
        """Return True if the swapchain is suboptimal."""
        return self._handle.is_suboptimal()

    def is_out_of_date(self) -> bool:
        """Return True if the swapchain is out of date."""
        return self._handle.is_out_of_date()

    def needs_recreation(self) -> bool:
        """Return True if the swapchain needs recreation."""
        return self._handle.needs_recreation()

    def __repr__(self) -> str:
        return f"<Swapchain {self.width}x{self.height}>"
