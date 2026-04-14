TILE_SIZE = 64  # Must be multiple of 8 and 16


def compute_dirty_tiles(rects, width, height, tile_size=TILE_SIZE):
    """Return a set of (tx, ty) tile indices that intersect any dirty rect."""
    if not rects:
        return set()
    tiles = set()
    tiles_x = (width + tile_size - 1) // tile_size
    tiles_y = (height + tile_size - 1) // tile_size
    for rx, ry, rw, rh in rects:
        # Clamp to frame boundaries
        rx = max(0, rx)
        ry = max(0, ry)
        rw = min(rw, width - rx)
        rh = min(rh, height - ry)
        if rw <= 0 or rh <= 0:
            continue
        tx_start = rx // tile_size
        ty_start = ry // tile_size
        tx_end = (rx + rw + tile_size - 1) // tile_size
        ty_end = (ry + rh + tile_size - 1) // tile_size
        for ty in range(ty_start, min(ty_end, tiles_y)):
            for tx in range(tx_start, min(tx_end, tiles_x)):
                tiles.add((tx, ty))
    return tiles


def tile_dispatch_groups(tx, ty, groups_per_tile_x, groups_per_tile_y):
    """Return (gx, gy, 1) dispatch arguments for a single tile."""
    return (tx * groups_per_tile_x, ty * groups_per_tile_y, 1)
