import logging
from typing import List, Optional, Tuple

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

        if use_cache:
            self._init_cache_mode(model_name, double_upscale, cache_capacity)

    def _init_cache_mode(
        self, model_name: str, double_upscale: bool, capacity: int
    ) -> None:
        """Create atlases and tile‑mode SRCNN instance."""
        tile_out = self.tile_size * (4 if double_upscale else 2)
        self.tile_out_w = tile_out
        self.tile_out_h = tile_out

        self.atlas_manager = TileAtlasManager(
            capacity=capacity,
            tile_width=tile_out,
            tile_height=tile_out,
        )

        # Create texture arrays for intermediate outputs (T0, T1, ...) and final output
        num_intermediate = len(self.full_upscaler.outputs)  # e.g., 4
        self.intermediate_atlases: List[Texture2D] = []
        for _ in range(num_intermediate):
            self.intermediate_atlases.append(
                Texture2D(tile_out, tile_out, slices=capacity)
            )
        self.final_atlas = Texture2D(tile_out, tile_out, slices=capacity)
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
            output_atlases=self.intermediate_atlases,
            output_atlas=self.final_atlas,
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
        tiles = []
        stride = self.crop_width * 4
        for rx, ry, rw, rh, hash_val in rects:
            tx = rx // self.tile_size
            ty = ry // self.tile_size
            data = bytearray()
            for row in range(ry, ry + rh):
                start = row * stride + rx * 4
                data.extend(frame[start : start + rw * 4])
            tiles.append((tx, ty, hash_val, bytes(data)))
        return tiles

    def process_tile_frame(
        self, dirty_tiles: List[Tuple[int, int, int, bytes]]
    ) -> None:
        """
        Execute tile‑mode SRCNN and assemble the upscaled output.
        After this, `self.upscaled_output` contains the full upscaled image.
        """
        if not self.tile_upscaler:
            raise RuntimeError("Tile mode not enabled")

        # 1. Process tiles (uploads + dispatches)
        self.tile_upscaler.process_tiles(dirty_tiles)

        # 2. Copy all cached tiles from final atlas to upscaled_output
        for tx, ty, layer in self.atlas_manager.get_all_entries():
            dst_x = tx * self.tile_out_w
            dst_y = ty * self.tile_out_h
            self.final_atlas.copy_to(
                self.upscaled_output,
                src_slice=layer,
                dst_x=dst_x,
                dst_y=dst_y,
                width=self.tile_out_w,
                height=self.tile_out_h,
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

    # Inside UpscalerManager class

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
