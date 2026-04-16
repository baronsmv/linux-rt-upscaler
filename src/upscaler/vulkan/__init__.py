"""
Vulkan backend for GPU compute and presentation.

This module provides a Pythonic interface to the native Vulkan C extension.

Basic usage:
    import vulkan

    # Create a context (holds device selection and debug state)
    ctx = vulkan.VulkanContext()
    ctx.enable_debug()

    # Discover and select a device
    devices = ctx.get_discovered_devices()
    ctx.set_current_device(0)  # or use ctx.get_best_device()

    device = ctx.get_current_device()
    buffer = device.create_buffer(1024)
    buffer.upload(b"hello world")
"""

import atexit
import os
from typing import List, Optional

# Import the C extension under a clear, distinct name
from . import _vulkan as _backend
from .compute import Compute
from .constants import *
from .device import Device
from .heap import Heap
from .resource import Buffer, Texture1D, Texture2D, Texture3D
from .sampler import Sampler
from .swapchain import Swapchain

__all__ = [
    "VulkanContext",
    "Device",
    "Heap",
    "Buffer",
    "Texture1D",
    "Texture2D",
    "Texture3D",
    "Sampler",
    "Compute",
    "Swapchain",
]


class VulkanContext:
    """
    Holds Vulkan state for a specific execution context.

    Encapsulates discovered devices, the currently selected device,
    and debug settings. Multiple contexts can coexist independently.
    """

    __slots__ = (
        "_discovered_devices",
        "_current_device",
        "_debug_enabled",
        "_cleanup_registered",
    )

    def __init__(self) -> None:
        self._discovered_devices: Optional[List[Device]] = None
        self._current_device: Optional[Device] = None
        self._debug_enabled: bool = False
        self._cleanup_registered: bool = False

    def _cleanup(self) -> None:
        """Wait for the current device to idle (called at process exit)."""
        if self._current_device is not None:
            self._current_device.wait_idle()

    def enable_debug(self) -> None:
        """Enable Vulkan validation layers and debug output."""
        if not self._debug_enabled:
            _backend.enable_debug()
            self._debug_enabled = True
            if not self._cleanup_registered:
                atexit.register(self._cleanup)
                self._cleanup_registered = True

    def get_shader_binary_type(self) -> int:
        """Return the shader binary type supported by this backend (SPIR‑V = 1)."""
        return _backend.get_shader_binary_type()

    def get_discovered_devices(self) -> List[Device]:
        """Return a list of all available Vulkan devices (cached)."""
        if self._discovered_devices is None:
            raw_list = _backend.get_discovered_devices()
            self._discovered_devices = [Device._from_handle(d) for d in raw_list]
        return self._discovered_devices

    def set_current_device(self, index: int) -> None:
        """Set the currently active device by index from `get_discovered_devices()`."""
        devices = self.get_discovered_devices()
        if index < 0 or index >= len(devices):
            raise IndexError(f"Device index {index} out of range (0..{len(devices)-1})")
        self._current_device = devices[index]

    def get_current_device(self) -> Device:
        """Return the currently active device (auto‑selects best if none set)."""
        if self._current_device is None:
            self._current_device = self.get_best_device()
        return self._current_device

    def get_best_device(self) -> Device:
        """
        Select the best available device.

        Selection order:
        1. Device specified by `VULKAN_DEVICE` environment variable (index).
        2. Discrete GPU with the most dedicated video memory.
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

        # Prefer hardware‑accelerated, discrete GPUs with more VRAM
        def key(d: Device) -> tuple:
            return (d.is_hardware, d.is_discrete, d.dedicated_video_memory)

        return sorted(devices, key=key)[-1]


# Optional: create a default context for simple scripts
_default_context = VulkanContext()

# Expose module-level convenience functions that delegate to the default context.
# These are purely for brevity in single‑context applications.


def enable_debug() -> None:
    """Enable Vulkan validation layers (uses default context)."""
    _default_context.enable_debug()


def get_shader_binary_type() -> int:
    """Return the shader binary type (uses default context)."""
    return _default_context.get_shader_binary_type()


def get_discovered_devices() -> List[Device]:
    """Return a list of all available Vulkan devices (uses default context)."""
    return _default_context.get_discovered_devices()


def set_current_device(index: int) -> None:
    """Set the current device for the default context."""
    _default_context.set_current_device(index)


def get_current_device() -> Device:
    """Return the current device from the default context."""
    return _default_context.get_current_device()


def get_best_device() -> Device:
    """Select the best device (uses default context)."""
    return _default_context.get_best_device()
