"""Sampler object."""

from . import vulkan


class Sampler:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_sampler()")

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def __repr__(self) -> str:
        return "<Sampler>"
