"""Tile Processors and Atlas public module."""

from .tile import TileProcessor
from .utils import (
    DamageRects,
    DirtyTiles,
    DirtyTilesCoords,
    DirtyTilesRects,
    collect_dirty_tile_coords,
    expand_damage_rects,
    extract_expanded_tiles,
)

__all__ = [
    "DamageRects",
    "DirtyTiles",
    "DirtyTilesCoords",
    "DirtyTilesRects",
    "TileProcessor",
    "collect_dirty_tile_coords",
    "expand_damage_rects",
    "extract_expanded_tiles",
]
