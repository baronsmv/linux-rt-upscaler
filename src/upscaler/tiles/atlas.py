import threading
from collections import OrderedDict
from typing import Dict, List, Optional, Tuple


class TileAtlasManager:
    """
    Thread-safe manager for a fixed-capacity tile cache.

    Each tile is identified by (tile_x, tile_y, content_hash). The manager maps
    this key to a layer index in a set of parallel texture arrays (one per
    intermediate output). LRU eviction ensures the most relevant tiles stay cached.

    Attributes:
        capacity (int): Maximum number of tiles that can be stored.
        tile_width (int): Width of a tile in pixels (output size).
        tile_height (int): Height of a tile in pixels.
    """

    def __init__(self, capacity: int, tile_width: int, tile_height: int) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.tile_width = tile_width
        self.tile_height = tile_height

        # Mapping: (tx, ty, hash) -> layer_index
        self._key_to_layer: Dict[Tuple[int, int, int], int] = {}

        # LRU tracking: OrderedDict where keys are layer indices,
        # values are the corresponding (tx, ty, hash) key.
        # Items are ordered from least recently used to most recently used.
        self._lru: OrderedDict[int, Tuple[int, int, int]] = OrderedDict()

        # Free layers that are not currently assigned to any tile
        self._free_layers: List[int] = list(range(capacity))

        # Lock for thread safety (pipeline runs in its own thread)
        self._lock = threading.Lock()

        # Statistics for debugging / performance monitoring
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get_all_entries(self) -> List[Tuple[int, int, int]]:
        """Return list of (tile_x, tile_y, layer) for all cached tiles."""
        with self._lock:
            return [(tx, ty, layer) for layer, (tx, ty, _) in self._lru.items()]

    def acquire_layer(self, tx: int, ty: int, tile_hash: int) -> Tuple[int, bool]:
        """
        Get the layer index for a tile.

        Args:
            tx, ty: Tile coordinates in the source image grid.
            tile_hash: xxHash64 of the tile's pixel data.

        Returns:
            A tuple (layer_index, was_cached).
            - If the tile is already cached, `was_cached` is True and the LRU order is updated.
            - Otherwise, a layer is allocated (possibly evicting the LRU tile) and `was_cached` is False.
        """
        key = (tx, ty, tile_hash)
        with self._lock:
            # Cache hit
            if key in self._key_to_layer:
                layer = self._key_to_layer[key]
                # Move to end (most recently used)
                self._lru.move_to_end(layer)
                self.hits += 1
                return layer, True

            # Cache miss, need to allocate a layer
            self.misses += 1

            # If no free layers, evict the least recently used one
            if not self._free_layers:
                evicted_layer, evicted_key = self._lru.popitem(last=False)
                del self._key_to_layer[evicted_key]
                self._free_layers.append(evicted_layer)
                self.evictions += 1

            # Allocate a free layer
            layer = self._free_layers.pop()
            self._key_to_layer[key] = layer
            self._lru[layer] = key
            return layer, False

    def mark_used(self, layer: int) -> None:
        """
        Update LRU order for a layer (e.g., when the tile is accessed again).

        Raises ValueError if the layer is not currently in use.
        """
        with self._lock:
            if layer not in self._lru:
                raise ValueError(f"Layer {layer} is not currently allocated")
            self._lru.move_to_end(layer)

    def get_key_for_layer(self, layer: int) -> Optional[Tuple[int, int, int]]:
        """Return the (tx, ty, hash) key for a given layer, or None if unused."""
        with self._lock:
            return self._lru.get(layer)

    def invalidate_layer(self, layer: int) -> None:
        """
        Forcefully remove a layer from the cache (e.g., if the tile data is known stale).
        """
        with self._lock:
            if layer not in self._lru:
                return
            key = self._lru.pop(layer)
            del self._key_to_layer[key]
            self._free_layers.append(layer)

    def clear(self) -> None:
        """Reset the cache to empty state."""
        with self._lock:
            self._key_to_layer.clear()
            self._lru.clear()
            self._free_layers = list(range(self.capacity))
            self.hits = 0
            self.misses = 0
            self.evictions = 0

    @property
    def used_layers(self) -> int:
        """Number of currently occupied layers."""
        with self._lock:
            return self.capacity - len(self._free_layers)

    def get_stats(self) -> Dict[str, int]:
        """Return a dictionary of cache statistics."""
        with self._lock:
            return {
                "capacity": self.capacity,
                "used": self.used_layers,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
            }
