import logging
from typing import List, Tuple, Set

import xxhash

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
#  Damage Region Expansion
# ------------------------------------------------------------------------------
def expand_damage_rects(
    rects: List[Tuple[int, int, int, int, int]],
    crop_width: int,
    crop_height: int,
    margin: int,
) -> List[Tuple[int, int, int, int]]:
    """
    Expand each damage rectangle by a given margin, clamped to crop bounds.

    Damage rectangles are reported by the frame grabber as (x, y, w, h, hash).
    To provide sufficient context for convolution layers, we expand each
    rectangle outward by `margin` pixels. The expanded rectangles are merged
    if they overlap, but this function does **not** perform merging - it simply
    returns the clamped, expanded rectangles. Merging is left to the caller if
    desired.

    Args:
        rects: List of damage rectangles, each as (x, y, width, height, hash).
        crop_width: Width of the captured crop area in pixels.
        crop_height: Height of the captured crop area in pixels.
        margin: Number of pixels to expand on all four sides.

    Returns:
        List of expanded rectangles as (x, y, width, height). The hash field
        is discarded. Rectangles that would become empty after clamping are
        omitted.

    Raises:
        ValueError: If crop_width or crop_height is non-positive.
    """
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")

    expanded: List[Tuple[int, int, int, int]] = []

    for rx, ry, rw, rh, _ in rects:
        # Skip invalid rectangles
        if rw <= 0 or rh <= 0:
            continue

        # Compute expanded bounds
        ex0 = rx - margin
        ey0 = ry - margin
        ex1 = rx + rw + margin
        ey1 = ry + rh + margin

        # Clamp to crop area
        ex0 = max(0, ex0)
        ey0 = max(0, ey0)
        ex1 = min(crop_width, ex1)
        ey1 = min(crop_height, ey1)

        # Only include if the clamped region is non-empty
        if ex1 > ex0 and ey1 > ey0:
            expanded.append((ex0, ey0, ex1 - ex0, ey1 - ey0))

    return expanded


# ------------------------------------------------------------------------------
#  Tile Extraction (Expanded with Edge Clamping)
# ------------------------------------------------------------------------------
def extract_expanded_tiles(
    frame: memoryview,
    rects: List[Tuple[int, int, int, int, int]],
    crop_width: int,
    crop_height: int,
    tile_size: int,
    margin: int,
) -> List[Tuple[int, int, bytes, int, int]]:
    """
    Extract expanded tiles for all tile grid cells that overlap any damage rectangle.

    The frame is divided into a grid of tiles of size `tile_size`. For each tile
    that intersects at least one damage rectangle, an expanded region of size
    `(tile_size + 2*margin)²` is extracted. If the expanded region extends
    beyond the crop area, the missing pixels are filled by replicating the
    nearest valid edge pixel (edge clamping).

    The function returns the raw pixel data for each expanded tile, together
    with the valid offset (`valid_x`, `valid_y`) that indicates where the
    interior `tile_size x tile_size` region begins within the expanded tile.
    This offset is usually equal to `margin`, but may be smaller at image
    boundaries where the expansion was clamped.

    Args:
        frame: Raw BGRA pixel data for the entire crop area. Must be
               `crop_width * crop_height * 4` bytes.
        rects: Damage rectangles as (x, y, w, h, hash).
        crop_width: Width of the crop area in pixels.
        crop_height: Height of the crop area in pixels.
        tile_size: Nominal tile size (interior region) in pixels.
        margin: Context margin to add on each side.

    Returns:
        List of tuples:
            (tile_x, tile_y, data_bytes, valid_x, valid_y)
        - `tile_x`, `tile_y`: Tile grid coordinates (0-based).
        - `data_bytes`: Raw BGRA data of the expanded tile.
        - `valid_x`, `valid_y`: Offset within the expanded tile where the
          interior region begins. For non-edge tiles, this equals `margin`.

    Raises:
        ValueError: If frame size does not match crop dimensions.
    """
    expected_frame_bytes = crop_width * crop_height * 4
    if len(frame) != expected_frame_bytes:
        raise ValueError(
            f"Frame size mismatch: expected {expected_frame_bytes} bytes, got {len(frame)}"
        )

    stride = crop_width * 4
    tiles_x = (crop_width + tile_size - 1) // tile_size
    tiles_y = (crop_height + tile_size - 1) // tile_size

    # Collect dirty tile grid cells (any overlap with a damage rectangle)
    dirty_tiles: Set[Tuple[int, int]] = set()
    for rx, ry, rw, rh, _ in rects:
        if rw <= 0 or rh <= 0:
            continue
        tx0 = rx // tile_size
        ty0 = ry // tile_size
        tx1 = (rx + rw + tile_size - 1) // tile_size
        ty1 = (ry + rh + tile_size - 1) // tile_size
        for ty in range(ty0, min(ty1, tiles_y)):
            for tx in range(tx0, min(tx1, tiles_x)):
                dirty_tiles.add((tx, ty))

    expanded_size = tile_size + 2 * margin
    expanded_bytes = expanded_size * expanded_size * 4
    result: List[Tuple[int, int, bytes, int, int]] = []

    for tx, ty in dirty_tiles:
        # Top-left of the nominal tile in crop coordinates
        tile_x0 = tx * tile_size
        tile_y0 = ty * tile_size

        # Expanded region before clamping
        exp_x0 = tile_x0 - margin
        exp_y0 = tile_y0 - margin
        exp_x1 = exp_x0 + expanded_size
        exp_y1 = exp_y0 + expanded_size

        # Clamp source region to crop bounds
        src_x0 = max(0, exp_x0)
        src_y0 = max(0, exp_y0)
        src_x1 = min(crop_width, exp_x1)
        src_y1 = min(crop_height, exp_y1)

        # Destination offsets within the expanded tile buffer
        dst_x0 = src_x0 - exp_x0
        dst_y0 = src_y0 - exp_y0
        copy_w = src_x1 - src_x0
        copy_h = src_y1 - src_y0

        data = bytearray(expanded_bytes)

        # Copy valid interior region
        _copy_region(
            data,
            frame,
            stride,
            src_x0,
            src_y0,
            copy_w,
            copy_h,
            dst_x0,
            dst_y0,
            expanded_size,
        )

        # Edge clamping for out-of-bounds areas
        # Top padding (exp_y0 < 0)
        if exp_y0 < 0:
            _pad_top(
                data, frame, stride, dst_x0, dst_y0, copy_w, expanded_size, src_x0, 0
            )  # src_y = 0 (top edge)

        # Bottom padding (exp_y1 > crop_height)
        if exp_y1 > crop_height:
            _pad_bottom(
                data,
                frame,
                stride,
                dst_x0,
                dst_y0,
                copy_w,
                copy_h,
                expanded_size,
                src_x0,
                crop_height - 1,
            )  # src_y = last row

        # Left padding (exp_x0 < 0)
        if exp_x0 < 0:
            _pad_left(
                data,
                frame,
                stride,
                dst_x0,
                expanded_size,
                exp_y0,
                crop_height,
                src_x0,
            )

        # Right padding (exp_x1 > crop_width)
        if exp_x1 > crop_width:
            _pad_right(
                data,
                frame,
                stride,
                dst_x0,
                copy_w,
                expanded_size,
                exp_y0,
                crop_height,
                crop_width - 1,
            )

        result.append((tx, ty, bytes(data), dst_x0, dst_y0))

    return result


# ----------------------------------------------------------------------
#  Extract tiles with content hash
# ----------------------------------------------------------------------
def extract_dirty_tiles_with_hash(
    frame: memoryview,
    rects: List[Tuple[int, int, int, int, int]],
    crop_width: int,
    crop_height: int,
    tile_size: int,
    margin: int,
) -> List[Tuple[int, int, int, bytes, int, int]]:
    expanded_tiles = extract_expanded_tiles(
        frame, rects, crop_width, crop_height, tile_size, margin
    )
    result = []
    for tx, ty, data, valid_x, valid_y in expanded_tiles:
        h = xxhash.xxh64(data).intdigest()
        result.append((tx, ty, h, data, valid_x, valid_y))
    return result


# ------------------------------------------------------------------------------
#  Internal Helper Functions for Tile Extraction
# ------------------------------------------------------------------------------
def _copy_region(
    dst: bytearray,
    src: memoryview,
    src_stride: int,
    src_x: int,
    src_y: int,
    copy_w: int,
    copy_h: int,
    dst_x: int,
    dst_y: int,
    dst_stride: int,
) -> None:
    """Copy a rectangular region from src to dst (row by row)."""
    for row in range(copy_h):
        src_start = (src_y + row) * src_stride + src_x * 4
        dst_start = ((dst_y + row) * dst_stride + dst_x) * 4
        dst[dst_start : dst_start + copy_w * 4] = src[
            src_start : src_start + copy_w * 4
        ]


def _pad_top(
    dst: bytearray,
    src: memoryview,
    src_stride: int,
    dst_x: int,
    first_valid_row: int,
    copy_w: int,
    dst_stride: int,
    src_x: int,
    src_y: int,
) -> None:
    """Replicate the top valid row into the top padding area."""
    for y in range(first_valid_row):
        src_start = src_y * src_stride + src_x * 4
        dst_start = y * dst_stride * 4 + dst_x * 4
        dst[dst_start : dst_start + copy_w * 4] = src[
            src_start : src_start + copy_w * 4
        ]


def _pad_bottom(
    dst: bytearray,
    src: memoryview,
    src_stride: int,
    dst_x: int,
    first_valid_row: int,
    copy_w: int,
    copy_h: int,
    dst_stride: int,
    src_x: int,
    src_y: int,
) -> None:
    """Replicate the bottom valid row into the bottom padding area."""
    last_valid_row = first_valid_row + copy_h - 1
    for y in range(last_valid_row + 1, dst_stride):
        src_start = src_y * src_stride + src_x * 4
        dst_start = y * dst_stride * 4 + dst_x * 4
        dst[dst_start : dst_start + copy_w * 4] = src[
            src_start : src_start + copy_w * 4
        ]


def _pad_left(
    dst: bytearray,
    src: memoryview,
    src_stride: int,
    dst_x: int,
    dst_stride: int,
    exp_y0: int,
    crop_height: int,
    src_x: int,
) -> None:
    """Replicate the leftmost valid column into the left padding area."""
    for y in range(dst_stride):
        src_y = min(max(exp_y0 + y, 0), crop_height - 1)
        src_start = src_y * src_stride + src_x * 4
        dst_start = y * dst_stride * 4
        for x in range(dst_x):
            dst[dst_start + x * 4 : dst_start + x * 4 + 4] = src[
                src_start : src_start + 4
            ]


def _pad_right(
    dst: bytearray,
    src: memoryview,
    src_stride: int,
    dst_x: int,
    copy_w: int,
    dst_stride: int,
    exp_y0: int,
    crop_height: int,
    src_x: int,
) -> None:
    """Replicate the rightmost valid column into the right padding area."""
    for y in range(dst_stride):
        src_y = min(max(exp_y0 + y, 0), crop_height - 1)
        src_start = src_y * src_stride + src_x * 4
        dst_start = y * dst_stride * 4 + (dst_x + copy_w) * 4
        for x in range(dst_stride - (dst_x + copy_w)):
            dst[dst_start + x * 4 : dst_start + x * 4 + 4] = src[
                src_start : src_start + 4
            ]
