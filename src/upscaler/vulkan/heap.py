"""Heap – a contiguous block of GPU memory."""

from . import vulkan


class Heap:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_heap() to obtain Heap instances")

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
