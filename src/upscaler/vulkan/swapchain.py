"""Swapchain for presentation."""

from . import vulkan
from .resource import Texture2D


class Swapchain:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_swapchain()")

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
        self, texture: Texture2D, x: int = 0, y: int = 0, wait: bool = True
    ) -> None:
        self._handle.present(texture._handle, x, y, wait)

    def is_suboptimal(self) -> bool:
        return self._handle.is_suboptimal()

    def is_out_of_date(self) -> bool:
        return self._handle.is_out_of_date()

    def needs_recreation(self) -> bool:
        return self._handle.needs_recreation()

    def __repr__(self) -> str:
        return f"<Swapchain {self.width}x{self.height}>"
