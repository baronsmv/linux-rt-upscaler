"""Compute pipeline."""

from typing import List, Optional, Tuple, Union, Callable

from . import vulkan
from .resource import Buffer, Texture2D


class Compute:
    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_compute()")

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    def dispatch(self, x: int, y: int, z: int, push: bytes = b"") -> None:
        self._handle.dispatch(x, y, z, push)

    def dispatch_indirect(
        self, indirect_buffer: "Buffer", offset: int = 0, push: bytes = b""
    ) -> None:
        self._handle.dispatch_indirect(indirect_buffer._handle, offset, push)

    def dispatch_sequence(
        self,
        sequence: List[Tuple["Compute", int, int, int, bytes]],
        copy_src: Optional["Buffer"] = None,
        copy_dst: Optional["Texture2D"] = None,
        copy_slice: int = 0,
        present_image: Optional["Texture2D"] = None,
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
        tiles: List[Tuple[int, int]],
        tile_width: int,
        tile_height: int,
        push_data_cb: Optional[Callable] = None,
    ) -> None:
        import struct

        entries = []
        for tx, ty in tiles:
            if push_data_cb:
                data = push_data_cb(tx, ty)
            else:
                data = struct.pack("<II", tx, ty)
            entries.append((tx, ty, data))
        self._handle.dispatch_tiles(entries, tile_width, tile_height)

    def bind_cbv(self, index: int, resource: Union["Buffer", "Texture2D"]) -> None:
        self._handle.bind_cbv(index, resource._handle)

    def bind_srv(self, index: int, resource: Union["Buffer", "Texture2D"]) -> None:
        self._handle.bind_srv(index, resource._handle)

    def bind_uav(self, index: int, resource: Union["Buffer", "Texture2D"]) -> None:
        self._handle.bind_uav(index, resource._handle)

    def __repr__(self) -> str:
        return "<Compute>"
