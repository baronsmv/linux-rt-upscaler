import logging
from typing import List, Optional, Tuple

import xxhash

from .cache import TileAtlasManager
from ..shaders import SRCNN
from ..vulkan import Texture2D

logger = logging.getLogger(__name__)


class UpscalerManager:
    """
    Manages SRCNN upscaling in both full‑frame and tile‑cache modes.

    Attributes:
        full_upscaler (SRCNN): Always available full‑frame upscaler.
        tile_upscaler (SRCNN | None): Tile‑mode upscaler (if cache enabled).
        atlas_manager (TileAtlasManager | None): Cache slot manager.
        upscaled_output (Texture2D | None): Assembled full upscaled texture for tile mode.
        tile_out_w, tile_out_h (int): Dimensions of an upscaled tile.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        use_cache: bool,
        cache_capacity: int,
        cache_threshold: float,
    ) -> None:
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.use_cache = use_cache
        self.cache_threshold = cache_threshold

        # Full‑frame upscaler (always available)
        self.full_upscaler = SRCNN(
            width=crop_width,
            height=crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
            tile_size=tile_size,
        )

        self.tile_upscaler: Optional[SRCNN] = None
        self.atlas_manager: Optional[TileAtlasManager] = None
        self.upscaled_output: Optional[Texture2D] = None
        self.tile_out_w: int = 0
        self.tile_out_h: int = 0
        self.output_names: List[str] = []
        self.output_atlases: List[Texture2D] = []

        if use_cache:
            self._init_cache_mode(model_name, double_upscale, cache_capacity)

    def _init_cache_mode(
        self, model_name: str, double_upscale: bool, capacity: int
    ) -> None:
        """Create atlases and tile‑mode SRCNN instance."""
        self.tile_out_w = self.tile_size * (4 if double_upscale else 2)
        self.tile_out_h = self.tile_size * (4 if double_upscale else 2)

        self.atlas_manager = TileAtlasManager(
            capacity=capacity,
            tile_width=self.tile_out_w,
            tile_height=self.tile_out_h,
        )

        # Get the ordered list of UAV names from the full upscaler
        self.output_names = self.full_upscaler.output_names

        # Create one atlas per UAV output
        for _ in self.output_names:
            atlas = Texture2D(self.tile_out_w, self.tile_out_h, slices=capacity)
            self.output_atlases.append(atlas)

        # Input atlas
        self.input_atlas = Texture2D(self.tile_size, self.tile_size, slices=capacity)

        # Full assembled upscaled texture (2D)
        src_w = self.crop_width * (4 if double_upscale else 2)
        src_h = self.crop_height * (4 if double_upscale else 2)
        self.upscaled_output = Texture2D(src_w, src_h)

        # Tile‑mode SRCNN instance
        self.tile_upscaler = SRCNN(
            width=self.crop_width,
            height=self.crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
            tile_size=self.tile_size,
            tile_mode=True,
            atlas_manager=self.atlas_manager,
            input_atlas=self.input_atlas,
            output_atlases=self.output_atlases,
        )

    @property
    def active_upscaler(self) -> SRCNN:
        """
        Return the default upscaler for compatibility with code that expects
        a single instance (e.g., for full‑frame path).
        """
        return self.full_upscaler

    def total_tiles(self) -> int:
        """Number of tiles covering the crop area."""
        tiles_x = (self.crop_width + self.tile_size - 1) // self.tile_size
        tiles_y = (self.crop_height + self.tile_size - 1) // self.tile_size
        return tiles_x * tiles_y

    def should_use_tile_mode(self, num_dirty: int) -> bool:
        """Return True if tile mode should be used for this frame."""
        if not self.use_cache:
            return False
        threshold = int(self.total_tiles() * self.cache_threshold)
        return num_dirty <= threshold

    def extract_dirty_tiles(
        self, rects: List[Tuple[int, int, int, int, int]], frame: bytes
    ) -> List[Tuple[int, int, int, bytes]]:
        """
        Convert damage rectangles to tile data.

        Args:
            rects: List of (x, y, width, height, hash) from FrameGrabber.
            frame: Raw BGRA frame bytes (full crop region).

        Returns:
            List of (tile_x, tile_y, hash, tile_data_bytes).
        """
        stride = self.crop_width * 4
        tile_w = self.tile_size
        tile_h = self.tile_size
        tiles_x = (self.crop_width + tile_w - 1) // tile_w
        tiles_y = (self.crop_height + tile_h - 1) // tile_h

        dirty_tile_coords = set()
        for rx, ry, rw, rh, _ in rects:
            start_tx = rx // tile_w
            start_ty = ry // tile_h
            end_tx = (rx + rw + tile_w - 1) // tile_w
            end_ty = (ry + rh + tile_h - 1) // tile_h
            for ty in range(start_ty, min(end_ty, tiles_y)):
                for tx in range(start_tx, min(end_tx, tiles_x)):
                    dirty_tile_coords.add((tx, ty))

        result = []
        full_tile_bytes = tile_w * tile_h * 4
        for tx, ty in dirty_tile_coords:
            x = tx * tile_w
            y = ty * tile_h
            w = min(tile_w, self.crop_width - x)
            h = min(tile_h, self.crop_height - y)

            # Start with zero‑filled full tile
            data = bytearray(full_tile_bytes)
            # Copy available rows
            for row in range(h):
                src_start = (y + row) * stride + x * 4
                dst_start = row * tile_w * 4
                data[dst_start : dst_start + w * 4] = frame[
                    src_start : src_start + w * 4
                ]

            valid_data = data[: w * h * 4]  # only the real pixel data, without pads
            tile_hash = xxhash.xxh64(valid_data).intdigest()
            result.append((tx, ty, tile_hash, bytes(data)))

        return result

    def process_tile_frame(
        self, dirty_tiles: List[Tuple[int, int, int, bytes]]
    ) -> None:
        """
        Execute tile‑mode SRCNN and assemble the upscaled output.
        After this, `self.upscaled_output` contains the full upscaled image.
        """
        if not self.tile_upscaler:
            raise RuntimeError("Tile mode not enabled")

        # Process tiles (uploads + dispatches)
        self.tile_upscaler.process_tiles(dirty_tiles)

        # Copy all cached tiles from the final output atlas to upscaled_output
        final_atlas = self.output_atlases[self.output_names.index("output")]
        output_w = self.upscaled_output.width
        output_h = self.upscaled_output.height

        for tx, ty, layer in self.atlas_manager.get_all_entries():
            dst_x = tx * self.tile_out_w
            dst_y = ty * self.tile_out_h

            # Clamp copy dimensions to output texture bounds
            copy_w = min(self.tile_out_w, output_w - dst_x)
            copy_h = min(self.tile_out_h, output_h - dst_y)

            if copy_w <= 0 or copy_h <= 0:
                continue  # tile completely outside (should not happen)

            final_atlas.copy_to(
                self.upscaled_output,
                src_slice=layer,
                dst_x=dst_x,
                dst_y=dst_y,
                width=copy_w,
                height=copy_h,
            )

    def get_output_texture(self) -> Texture2D:
        """
        Return the texture that holds the fully upscaled image.

        For full‑frame mode, this is `full_upscaler.output`.
        For tile mode, this is `self.upscaled_output` (must be called after processing).
        """
        if self.use_cache and self.upscaled_output:
            return self.upscaled_output
        return self.full_upscaler.output

    def upload_full_frame(
        self,
        frame: bytes,
        rects: List[Tuple[int, int, int, int, int]],
        use_damage_tracking: bool,
        crop_width: int,
        crop_height: int,
        margin: int,
    ) -> None:
        """
        Upload a full frame (or damage regions) to the full‑frame upscaler.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber (x, y, w, h, hash).
            use_damage_tracking: If True, upload only damaged subregions.
            crop_width, crop_height: Dimensions of the crop area.
            margin: Number of pixels to expand each damage rectangle (context).
        """
        upscaler = self.full_upscaler

        if use_damage_tracking and rects:
            upload_list = []
            stride = crop_width * 4
            for ex, ey, ew, eh in self._expand_damage_rects(
                rects, crop_width, crop_height, margin
            ):
                sub_data = bytearray()
                for row in range(ey, ey + eh):
                    start = row * stride + ex * 4
                    sub_data.extend(frame[start : start + ew * 4])
                upload_list.append((bytes(sub_data), ex, ey, ew, eh))
            upscaler.input.upload_subresources(upload_list)
        else:
            upscaler.staging.upload(frame)

        upscaler.process_full_frame()

    @staticmethod
    def _expand_damage_rects(
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        margin: int,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Expand damage rectangles by margin, clamped to crop bounds.

        Returns:
            List of (x, y, width, height) for each expanded rectangle.
        """
        expanded = []
        for rx, ry, rw, rh, _ in rects:
            ex0 = max(0, rx - margin)
            ey0 = max(0, ry - margin)
            ex1 = min(crop_width, rx + rw + margin)
            ey1 = min(crop_height, ry + rh + margin)
            if ex1 > ex0 and ey1 > ey0:
                expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))
        return expanded
