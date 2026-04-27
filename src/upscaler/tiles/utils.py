from typing import List, Tuple, Set, Optional


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
    Expand each damage rectangle by `margin` pixels, clamped to the crop area.

    Damage rectangles are reported as (x, y, width, height, hash). This
    iterator discards the hash and returns only the (x, y, width, height)
    of the expanded, clamped region. Rectangles that collapse to zero area
    after clamping are omitted.

    Args:
        rects: List of damage rectangles (x, y, w, h, hash).
        crop_width, crop_height: Dimensions of the captured crop in pixels.
        margin: Number of pixels to add on all four sides.

    Returns:
        List of (x, y, width, height) of expanded rectangles.

    Raises:
        ValueError: If crop dimensions are non-positive.
    """
    if crop_width <= 0 or crop_height <= 0:
        raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")

    expanded: List[Tuple[int, int, int, int]] = []

    for rx, ry, rw, rh, _ in rects:
        # Skip invalid rectangles
        if rw <= 0 or rh <= 0:
            continue

        # Compute expanded bounds and clamp to crop area
        ex0 = max(0, rx - margin)
        ey0 = max(0, ry - margin)
        ex1 = min(crop_width, rx + rw + margin)
        ey1 = min(crop_height, ry + rh + margin)

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
    skip_interior: bool = False,
) -> List[Tuple[int, int, Optional[bytes], int, int]]:
    """
    Extract expanded pixel data for every tile cell that touches a damage rectangle.

    The frame is divided into a grid of `tile_size x tile_size` cells.
    For each cell that overlaps at least one damage rectangle, an expanded
    region of size `(tile_size + 2xmargin)²` is copied out of the full-frame
    buffer. If that region extends beyond the crop bounds, the missing
    pixels are filled by replicating the nearest valid edge pixel (edge
    clamping).

    When `skip_interior` is True and a tile lies entirely inside the crop
    (no clamping required), no CPU extraction is performed and the tile’s
    pixel data is returned as ``None``. In that case the caller must
    supply the tile data by another means (e.g. a GPU copy).

    Args:
        frame: Raw BGRA pixel data for the entire crop area. Must be
               `crop_width * crop_height * 4` bytes.
        rects: Damage rectangles as (x, y, width, height, hash).
        crop_width, crop_height: Crop dimensions in pixels.
        tile_size: Nominal interior size of a tile in pixels.
        margin: Context margin to add on all sides.
        skip_interior: If True, interior tiles are not extracted - their
            returned pixel data will be ``None``.

    Returns:
        List of (tx, ty, data, valid_x, valid_y) tuples.
        - tx, ty: Tile grid indices (0-based).
        - data: Raw BGRA bytes of the expanded tile, or ``None`` if
                `skip_interior` was True and the tile is interior.
        - valid_x, valid_y: Offset within the expanded buffer where the
          interior `tile_size x tile_size` region begins. Equals `margin`
          for non-edge tiles, smaller at borders.

    Raises:
        ValueError: If `frame` size does not match crop dimensions.
    """
    expected = crop_width * crop_height * 4
    if len(frame) != expected:
        raise ValueError(
            f"Frame size mismatch: expected {expected} bytes, got {len(frame)}"
        )

    stride = crop_width * 4
    tiles_x = (crop_width + tile_size - 1) // tile_size
    tiles_y = (crop_height + tile_size - 1) // tile_size

    # Gather all tile coordinates that intersect at least one damage rectangle.
    dirty: Set[Tuple[int, int]] = set()
    for rx, ry, rw, rh, _ in rects:
        if rw <= 0 or rh <= 0:
            continue
        tx0 = rx // tile_size
        ty0 = ry // tile_size
        tx1 = (rx + rw + tile_size - 1) // tile_size
        ty1 = (ry + rh + tile_size - 1) // tile_size
        for ty in range(ty0, min(ty1, tiles_y)):
            for tx in range(tx0, min(tx1, tiles_x)):
                dirty.add((tx, ty))

    expanded_side = tile_size + 2 * margin
    expanded_bytes = expanded_side * expanded_side * 4
    result: List[Tuple[int, int, Optional[bytes], int, int]] = []

    for tx, ty in dirty:
        tile_x0 = tx * tile_size
        tile_y0 = ty * tile_size

        # Expanded bounds before clamping
        exp_x0 = tile_x0 - margin
        exp_y0 = tile_y0 - margin
        exp_x1 = exp_x0 + expanded_side
        exp_y1 = exp_y0 + expanded_side

        # If requested, skip interior tiles (return None) - caller handles them.
        if skip_interior and (
            0 <= exp_x0
            and 0 <= exp_y0
            and exp_x1 <= crop_width
            and exp_y1 <= crop_height
        ):
            result.append((tx, ty, None, margin, margin))
            continue

        # Clamp source rectangle to the crop area.
        src_x0 = max(0, exp_x0)
        src_y0 = max(0, exp_y0)
        src_x1 = min(crop_width, exp_x1)
        src_y1 = min(crop_height, exp_y1)

        # Destination offset inside the expanded tile buffer.
        dst_x0 = src_x0 - exp_x0
        dst_y0 = src_y0 - exp_y0
        copy_w = src_x1 - src_x0
        copy_h = src_y1 - src_y0

        data = bytearray(expanded_bytes)

        # Copy the valid interior region.
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
            expanded_side,
        )

        # Replicate edge pixels for any out-of-bounds areas.
        if exp_y0 < 0:
            _pad_top(
                data, frame, stride, dst_x0, dst_y0, copy_w, expanded_side, src_x0, 0
            )
        if exp_y1 > crop_height:
            _pad_bottom(
                data,
                frame,
                stride,
                dst_x0,
                dst_y0,
                copy_w,
                copy_h,
                expanded_side,
                src_x0,
                crop_height - 1,
            )
        if exp_x0 < 0:
            _pad_left(
                data, frame, stride, dst_x0, expanded_side, exp_y0, crop_height, src_x0
            )
        if exp_x1 > crop_width:
            _pad_right(
                data,
                frame,
                stride,
                dst_x0,
                copy_w,
                expanded_side,
                exp_y0,
                crop_height,
                crop_width - 1,
            )

        result.append((tx, ty, bytes(data), dst_x0, dst_y0))

    return result


# ------------------------------------------------------------------------------
#  Internal helpers - fast row/column copies with memoryview slicing
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
    """Copy a rectangular region from src to dst, row by row."""
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
    """Fill top padding rows with the first valid row of the source."""
    src_start = src_y * src_stride + src_x * 4
    row_data = src[src_start : src_start + copy_w * 4]
    for y in range(first_valid_row):
        dst_start = y * dst_stride * 4 + dst_x * 4
        dst[dst_start : dst_start + copy_w * 4] = row_data


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
    """Fill bottom padding rows with the last valid row of the source."""
    last_valid_y = first_valid_row + copy_h - 1
    src_start = src_y * src_stride + src_x * 4
    row_data = src[src_start : src_start + copy_w * 4]
    for y in range(last_valid_y + 1, dst_stride):
        dst_start = y * dst_stride * 4 + dst_x * 4
        dst[dst_start : dst_start + copy_w * 4] = row_data


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
    """Fill left padding columns with the leftmost valid column of each row."""
    for y in range(dst_stride):
        src_y = min(max(exp_y0 + y, 0), crop_height - 1)
        pixel = src[src_y * src_stride + src_x * 4 : src_y * src_stride + src_x * 4 + 4]
        dst_row = y * dst_stride * 4
        for x in range(dst_x):
            dst[dst_row + x * 4 : dst_row + x * 4 + 4] = pixel


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
    """Fill right padding columns with the rightmost valid column of each row."""
    for y in range(dst_stride):
        src_y = min(max(exp_y0 + y, 0), crop_height - 1)
        pixel = src[src_y * src_stride + src_x * 4 : src_y * src_stride + src_x * 4 + 4]
        dst_row = y * dst_stride * 4 + (dst_x + copy_w) * 4
        for x in range(dst_stride - (dst_x + copy_w)):
            dst[dst_row + x * 4 : dst_row + x * 4 + 4] = pixel
