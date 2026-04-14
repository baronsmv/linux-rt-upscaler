"""Utility modules."""

from .environment import setup_environment
from .geometry import parse_output_geometry, calculate_scaling_rect
from .screen import get_base_geometry
from .tiling import TILE_SIZE, compute_dirty_tiles, tile_dispatch_groups

__all__ = [
    "TILE_SIZE",
    "calculate_scaling_rect",
    "compute_dirty_tiles",
    "get_base_geometry",
    "parse_output_geometry",
    "setup_environment",
    "tile_dispatch_groups",
]
