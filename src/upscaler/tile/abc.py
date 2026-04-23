import logging
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

from ..srcnn import PipelineFactory, SRCNN, load_cunny_model
from ..vulkan import Buffer, Compute, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class ABCTileProcessor(ABC):
    """
    Abstract base for tile-based upscaling strategies.

    Subclasses must implement `process_tiles` to handle dirty tiles and
    populate `self.output_texture`. The base class provides common
    initialization, tile extraction utilities, and dispatch sequence building.

    Attributes:
        crop_width, crop_height: Dimensions of the captured crop area.
        tile_size: Nominal tile size (input to the network) in pixels.
        margin: Extra border pixels added around each tile for context.
        double_upscale: If True, perform 4x upscaling (two 2x stages).
        max_layers: Maximum number of concurrent tile layers (batch size).
        expanded_tile_size: Tile size including margin.
        tile_out_w_first, tile_out_h_first: Output size of first upscale stage.
        tile_out_w_final, tile_out_h_final: Final output size per tile.
        output_texture: Full-frame final upscaled image (2D).
        factory: Shared pipeline factory for all SRCNN stages.
        staging: Reusable upload buffer for tile data.
        stages: List of SRCNN instances (one per upscale stage).
        groups_per_stage: Dispatch group counts for each stage.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        tile_context_margin: int,
        max_layers: int,
        push_constant_size: int,
        variant: str = "_tile",
    ) -> None:
        """
        Common initialisation for tile processors.

        Args:
            crop_width, crop_height: Dimensions of the captured crop area.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal tile size (input to the network) in pixels.
            tile_context_margin: Extra border pixels added around each tile
                to provide context for convolution layers.
            max_layers: Maximum number of tiles processed in one batch.
            push_constant_size: Size of push constant block (bytes).
            variant: Shader variant suffix (e.g., "_tile").
        """
        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.margin = tile_context_margin
        self.double_upscale = double_upscale
        self.max_layers = max_layers

        # The actual input tile size after adding the margin.
        self.expanded_tile_size = tile_size + 2 * self.margin

        # Output dimensions for each stage (after upscaling).
        self.tile_out_w_first = self.expanded_tile_size * 2
        self.tile_out_h_first = self.expanded_tile_size * 2
        scale = 4 if double_upscale else 2
        self.tile_out_w_final = self.expanded_tile_size * scale
        self.tile_out_h_final = self.expanded_tile_size * scale

        # Final output texture (full frame, upscaled).
        out_w = crop_width * scale
        out_h = crop_height * scale
        self.output_texture = Texture2D(out_w, out_h)

        # Shared pipeline factory for all SRCNN stages.
        config = load_cunny_model(model_name, variant=variant)
        config.push_constant_size = push_constant_size
        self.factory = PipelineFactory(config)

        # Staging buffer for uploading tile data (reused).
        self.staging = Buffer(
            self.expanded_tile_size * self.expanded_tile_size * 4,
            heap_type=HEAP_UPLOAD,
        )

        # Subclasses populate these.
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []

    @abstractmethod
    def process_tiles(self, dirty_tiles) -> None:
        """Process a batch of dirty tiles and update the output texture."""
        pass

    def _build_dispatch_sequence(
        self, tile_batch: List[Tuple[int, int, int, Optional[bytes]]]
    ) -> List[Tuple[Compute, int, int, int, bytes]]:
        """
        Build a list of dispatches for a batch of tiles.

        Args:
            tile_batch: List of (tile_x, tile_y, layer, push_data) tuples.

        Returns:
            List of (Compute, groups_x, groups_y, groups_z, push_data) ready
            for `dispatch_sequence`.
        """
        dispatches = []
        for _, _, _, push_data in tile_batch:
            for stage_idx, srnn in enumerate(self.stages):
                groups_x, groups_y = self.groups_per_stage[stage_idx]
                for pipe in srnn.pipelines:
                    dispatches.append((pipe, groups_x, groups_y, 1, push_data))
        return dispatches

    # ----------------------------------------------------------------------
    #  Static utility: expand damage rectangles by margin
    # ----------------------------------------------------------------------
    @staticmethod
    def expand_damage_rects(
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        margin: int,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Expand damage rectangles by a given margin, clamped to crop bounds.

        Args:
            rects: Damage rectangles as (x, y, w, h, hash).
            crop_width, crop_height: Dimensions of the full crop area.
            margin: Pixels to add on each side.

        Returns:
            List of expanded rectangles as (x, y, w, h).
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

    # ----------------------------------------------------------------------
    #  Static utility: extract expanded tiles from damage rects
    # ----------------------------------------------------------------------
    @staticmethod
    def extract_expanded_tiles(
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        tile_size: int,
        margin: int,
    ) -> List[Tuple[int, int, bytes, int, int]]:
        """
        Extract expanded tiles for all dirty tile positions.

        For each tile in the grid that overlaps any damage rectangle,
        extract a region of size `(tile_size + 2*margin)²` (clamped to
        crop bounds). Return the raw pixel data together with the valid
        output offset (valid_x, valid_y) indicating where the interior
        `tile_size x tile_size` region begins within the expanded tile.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber.
            crop_width, crop_height: Dimensions of the crop area.
            tile_size: Nominal tile size (interior region).
            margin: Context margin to add on each side.

        Returns:
            List of tuples:
                (tile_x, tile_y, data_bytes, valid_x, valid_y)
            where valid_x and valid_y are the offset inside the expanded tile
            where the valid output region starts (usually margin, except at
            image boundaries where the expansion was clamped).
        """
        stride = crop_width * 4
        tiles_x = (crop_width + tile_size - 1) // tile_size
        tiles_y = (crop_height + tile_size - 1) // tile_size

        # Find dirty tile grid cells.
        dirty_tiles = set()
        for rx, ry, rw, rh, _ in rects:
            tx0 = rx // tile_size
            ty0 = ry // tile_size
            tx1 = (rx + rw + tile_size - 1) // tile_size
            ty1 = (ry + rh + tile_size - 1) // tile_size
            for ty in range(ty0, min(ty1, tiles_y)):
                for tx in range(tx0, min(tx1, tiles_x)):
                    dirty_tiles.add((tx, ty))

        expanded_size = tile_size + 2 * margin
        expanded_bytes = expanded_size * expanded_size * 4
        result = []

        for tx, ty in dirty_tiles:
            # Nominal tile top-left in crop coordinates
            tile_x0 = tx * tile_size
            tile_y0 = ty * tile_size

            # Expanded region (before clamping)
            exp_x0 = tile_x0 - margin
            exp_y0 = tile_y0 - margin

            # Clamp source region to crop bounds
            src_x0 = max(0, exp_x0)
            src_y0 = max(0, exp_y0)
            src_x1 = min(crop_width, exp_x0 + expanded_size)
            src_y1 = min(crop_height, exp_y0 + expanded_size)

            # Destination offsets within the expanded tile buffer
            dst_x0 = src_x0 - exp_x0
            dst_y0 = src_y0 - exp_y0
            copy_w = src_x1 - src_x0
            copy_h = src_y1 - src_y0

            data = bytearray(expanded_bytes)

            # Copy valid region
            for row in range(copy_h):
                src_start = (src_y0 + row) * stride + src_x0 * 4
                dst_start = ((dst_y0 + row) * expanded_size + dst_x0) * 4
                data[dst_start : dst_start + copy_w * 4] = frame[
                    src_start : src_start + copy_w * 4
                ]

            # Edge clamping for out-of-bounds areas
            # Top padding
            if exp_y0 < 0:
                first_valid_row = dst_y0
                for y in range(first_valid_row):
                    src_y = 0
                    src_start = src_y * stride + src_x0 * 4
                    dst_start = y * expanded_size * 4 + dst_x0 * 4
                    data[dst_start : dst_start + copy_w * 4] = frame[
                        src_start : src_start + copy_w * 4
                    ]
            # Bottom padding
            if exp_y0 + expanded_size > crop_height:
                last_valid_y = crop_height - 1
                last_valid_row = dst_y0 + copy_h - 1
                for y in range(last_valid_row + 1, expanded_size):
                    src_start = last_valid_y * stride + src_x0 * 4
                    dst_start = y * expanded_size * 4 + dst_x0 * 4
                    data[dst_start : dst_start + copy_w * 4] = frame[
                        src_start : src_start + copy_w * 4
                    ]
            # Left padding
            if exp_x0 < 0:
                for y in range(expanded_size):
                    dst_start = y * expanded_size * 4 + 0
                    src_col = src_x0
                    src_y = min(max(exp_y0 + y, 0), crop_height - 1)
                    src_start = src_y * stride + src_col * 4
                    for x in range(dst_x0):
                        data[dst_start + x * 4 : dst_start + x * 4 + 4] = frame[
                            src_start : src_start + 4
                        ]
            # Right padding
            if exp_x0 + expanded_size > crop_width:
                for y in range(expanded_size):
                    dst_start = y * expanded_size * 4 + (dst_x0 + copy_w) * 4
                    src_col = crop_width - 1
                    src_y = min(max(exp_y0 + y, 0), crop_height - 1)
                    src_start = src_y * stride + src_col * 4
                    for x in range(expanded_size - (dst_x0 + copy_w)):
                        data[dst_start + x * 4 : dst_start + x * 4 + 4] = frame[
                            src_start : src_start + 4
                        ]

            result.append((tx, ty, bytes(data), dst_x0, dst_y0))

        return result
