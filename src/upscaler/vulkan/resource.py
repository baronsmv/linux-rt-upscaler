"""Resource classes: Buffer, Texture1D, Texture2D, Texture3D."""

from typing import List, Optional, Tuple

from . import vulkan
from .heap import Heap


class Resource:
    """Base class for buffers and textures."""

    __slots__ = ("_handle",)

    def __init__(self):
        raise TypeError("Use Device.create_* methods")

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
        """Copy data to another resource."""
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
        """Bind a heap to a sparse tile."""
        self._handle.bind_tile(
            x, y, z, heap._handle if heap else None, heap_offset, slice
        )


class Buffer(Resource):
    __slots__ = ()

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


class Texture1D(Resource):
    __slots__ = ()

    @classmethod
    def _from_handle(cls, handle):
        self = cls.__new__(cls)
        self._handle = handle
        return self

    @property
    def width(self) -> int:
        return self._handle.width

    @property
    def slices(self) -> int:
        return self._handle.slices

    @property
    def row_pitch(self) -> int:
        return self._handle.row_pitch

    def __repr__(self) -> str:
        return f"<Texture1D width={self.width}>"


class Texture2D(Resource):
    __slots__ = ()

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


class Texture3D(Resource):
    __slots__ = ()

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
    def depth(self) -> int:
        return self._handle.depth

    @property
    def row_pitch(self) -> int:
        return self._handle.row_pitch

    def __repr__(self) -> str:
        return f"<Texture3D {self.width}x{self.height}x{self.depth}>"
