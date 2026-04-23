import logging
import struct
from typing import List, Optional, Tuple

from .utils import expand_damage_rects, extract_expanded_tiles
from ..srcnn import PipelineFactory, SRCNN, dispatch_groups, load_cunny_model
from ..vulkan import Buffer, Compute, Texture2D, HEAP_UPLOAD

logger = logging.getLogger(__name__)


class TileProcessor:
    """
    Direct tile-based upscaling processor.

    The processor divides the captured crop area into a grid of tiles of size
    `tile_size`. Each dirty tile (overlapping a damage rectangle) is expanded
    by a context margin, uploaded to a dedicated layer of an array texture,
    and processed by the SRCNN pipeline. The final pass writes the interior
    region directly to the full output texture (a 2D array with 1 slice).

    Attributes:
        crop_width (int): Width of the captured crop area in pixels.
        crop_height (int): Height of the captured crop area in pixels.
        tile_size (int): Nominal tile size (interior region) in pixels.
        margin (int): Context margin added around each tile.
        double_upscale (bool): If True, perform 4x upscaling (two 2x stages).
        max_layers (int): Maximum concurrent tiles per batch.
        expanded_tile_size (int): tile_size + (2 * margin).
        tile_out_w_final (int): Width of final upscaled tile.
        tile_out_h_final (int): Height of final upscaled tile.
        output_texture (Texture2D): Final full-frame upscaled texture (1 slice).
        factory (PipelineFactory): Shared factory for SRCNN pipelines.
        stages (List[SRCNN]): SRCNN stage instances.
        groups_per_stage (List[Tuple[int, int]]): Dispatch groups per stage.
        input_tex (Texture2D): Input array texture for tile data.
        full_input_tex (Texture2D): Residual texture (full frame, updated per damage).
        staging (Buffer): Staging buffer for tile uploads.
    """

    def __init__(
        self,
        crop_width: int,
        crop_height: int,
        model_name: str,
        double_upscale: bool,
        tile_size: int,
        tile_context_margin: int = 0,
        max_layers: int = 16,
    ) -> None:
        """
        Initialize the direct tile processor.

        Args:
            crop_width: Width of the captured crop area in pixels.
            crop_height: Height of the captured crop area in pixels.
            model_name: Name of the CuNNy model subdirectory (e.g., "fast").
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal input tile size (without margin).
            tile_context_margin: Extra border pixels for convolution context.
            max_layers: Maximum number of concurrent tiles per batch.

        Raises:
            ValueError: If crop dimensions are non-positive.
            FileNotFoundError: If model files are missing.
        """
        if crop_width <= 0 or crop_height <= 0:
            raise ValueError(f"Invalid crop dimensions: {crop_width}x{crop_height}")
        if tile_size <= 0:
            raise ValueError(f"Invalid tile size: {tile_size}")
        if max_layers <= 0:
            raise ValueError(f"Invalid max_layers: {max_layers}")

        self.crop_width = crop_width
        self.crop_height = crop_height
        self.tile_size = tile_size
        self.margin = tile_context_margin
        self.double_upscale = double_upscale
        self.max_layers = max_layers

        self.expanded_tile_size = tile_size + 2 * self.margin

        scale = 4 if double_upscale else 2
        self.tile_out_w_final = self.expanded_tile_size * scale
        self.tile_out_h_final = self.expanded_tile_size * scale

        out_w = crop_width * scale
        out_h = crop_height * scale
        # Output texture is a 2D array of 1 slice (compatible with unified shader)
        self.output_texture = Texture2D(out_w, out_h, slices=1, force_array_view=True)

        # Load model configuration and create pipeline factory
        config = load_cunny_model(model_name, variant="_tile")
        config.push_constant_size = self._get_push_constant_size()
        self.factory = PipelineFactory(config)

        # Staging buffer for uploading tile data (reused across frames)
        self.staging = Buffer(
            self.expanded_tile_size * self.expanded_tile_size * 4,
            heap_type=HEAP_UPLOAD,
        )

        # Residual texture: holds the full captured frame (damage regions updated)
        self.full_input_tex = Texture2D(
            crop_width, crop_height, slices=self.max_layers, force_array_view=True
        )
        # Staging buffer for uploading to residual texture (rarely used, small)
        self.full_staging = Buffer(crop_width * crop_height * 4, heap_type=HEAP_UPLOAD)

        # SRCNN stages and dispatch groups (populated by _create_stages)
        self.stages: List[SRCNN] = []
        self.groups_per_stage: List[Tuple[int, int]] = []
        self._create_stages()

        # Custom final pipeline (overrides the last pass to write directly to output)
        self.final_pipeline: Optional[Compute] = None
        self._finalize_pipeline()

        # Reference to the input texture for tile uploads
        self.input_tex = self.stages[0].input

        logger.info(
            f"TileProcessor initialized: crop={crop_width}x{crop_height}, "
            f"tile={tile_size}, margin={self.margin}, max_layers={max_layers}"
        )

    # --------------------------------------------------------------------------
    #  Template Methods (hooks for subclasses)
    # --------------------------------------------------------------------------
    def _get_push_constant_size(self) -> int:
        """Return the size of the push constant block in bytes."""
        return 60  # 15 uints x 4 bytes

    def _make_push_data(
        self,
        tx: int,
        ty: int,
        layer_idx: int,
        valid_x: int,
        valid_y: int,
        full_out_w: int,
        full_out_h: int,
        actual_out_w: int,
        actual_out_h: int,
    ) -> bytes:
        """
        Build the push constant block for a single tile.

        The default implementation sets `outputLayer = 0` (direct mode).
        Subclasses may override this to provide a different output layer
        (e.g., cache mode).

        Returns:
            Packed bytes (60 bytes) ready for upload.
        """
        src_x = tx * self.tile_size
        src_y = ty * self.tile_size
        scale = 4 if self.double_upscale else 2
        dst_x = tx * self.tile_size * scale
        dst_y = ty * self.tile_size * scale

        valid_block_x = valid_x * scale
        valid_block_y = valid_y * scale

        return struct.pack(
            "IIIIIIIIIIIIIII",  # 15 uints
            layer_idx,  # inputLayer
            src_x,
            src_y,  # srcOffset
            dst_x,
            dst_y,  # dstOffset
            self.margin,  # margin
            self.crop_width,
            self.crop_height,  # cropWidth, cropHeight
            full_out_w,
            full_out_h,  # fullOutWidth, fullOutHeight
            valid_block_x,
            valid_block_y,  # validOffset
            actual_out_w,
            actual_out_h,  # tileOutExtent
            0,  # outputLayer (always 0 for direct)
        )

    def _finalize_pipeline(self) -> None:
        """
        Replace the final pass pipeline with a custom one that writes directly
        to the full output texture.

        This method is called once during initialization. It creates a new
        compute pipeline for the last pass, binding `full_input_tex` as an SRV
        and `output_texture` as the UAV. Subclasses may override this to bind
        a different output target (e.g., an atlas).
        """
        final_pass_index = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_index]

        scale = 4 if self.double_upscale else 2
        full_out_w = self.crop_width * scale
        full_out_h = self.crop_height * scale
        cb_data = struct.pack(
            "IIIIffff",
            self.expanded_tile_size,  # in_width
            self.expanded_tile_size,  # in_height
            full_out_w,  # out_width
            full_out_h,  # out_height
            1.0 / self.expanded_tile_size,  # in_dx
            1.0 / self.expanded_tile_size,  # in_dy
            1.0 / full_out_w,  # out_dx
            1.0 / full_out_h,  # out_dy
        )
        final_cb = Buffer(len(cb_data))
        final_cb.upload(cb_data)

        # SRVs: residual texture + intermediate textures from the previous stage
        srv_list = [self.full_input_tex]
        pre_final_stage = self.stages[-2] if self.double_upscale else self.stages[0]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final_stage.outputs[f"t{i}"])

        uav_list = [self.output_texture]
        sampler_list = [
            self.factory._get_sampler(t)
            for t in self.factory.config.samplers[final_pass_index]
        ]

        self.final_pipeline = Compute(
            final_shader,
            cbv=[final_cb],
            srv=srv_list,
            uav=uav_list,
            samplers=sampler_list,
            push_size=self.factory.config.push_constant_size,
        )

        # Replace the original final pass in the stage's pipeline list
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = self.final_pipeline
        else:
            self.stages[0].pipelines[-1] = self.final_pipeline

    # --------------------------------------------------------------------------
    #  Stage Construction (internal)
    # --------------------------------------------------------------------------
    def _create_stages(self) -> None:
        """
        Create SRCNN stages with array textures sized for expanded tiles.

        This method builds the input texture array, intermediate feature map
        arrays, and the SRCNN instances. The stages are stored in `self.stages`.
        """
        # Input array: expanded tile size, `max_layers` slices
        input_tex = Texture2D(
            self.expanded_tile_size,
            self.expanded_tile_size,
            slices=self.max_layers,
            force_array_view=True,
        )

        # First stage outputs (intermediate feature maps)
        inter_tex = Texture2D(
            self.expanded_tile_size,
            self.expanded_tile_size,
            slices=self.max_layers,
            force_array_view=True,
        )
        outputs1 = {"output": inter_tex}
        for i in range(self.factory.config.num_textures):
            outputs1[f"t{i}"] = Texture2D(
                self.expanded_tile_size,
                self.expanded_tile_size,
                slices=self.max_layers,
                force_array_view=True,
            )

        srnn1 = SRCNN(
            factory=self.factory,
            width=self.expanded_tile_size,
            height=self.expanded_tile_size,
            input_texture=input_tex,
            output_textures=outputs1,
            push_constant_size=self.factory.config.push_constant_size,
        )
        self.stages.append(srnn1)
        self.groups_per_stage.append(
            dispatch_groups(
                self.expanded_tile_size, self.expanded_tile_size, last_pass=False
            )
        )

        if self.double_upscale:
            # Second stage (feature maps, same size)
            inter_tex2 = Texture2D(
                self.expanded_tile_size,
                self.expanded_tile_size,
                slices=self.max_layers,
                force_array_view=True,
            )
            outputs2 = {"output": inter_tex2}
            for i in range(self.factory.config.num_textures):
                outputs2[f"t{i}"] = Texture2D(
                    self.expanded_tile_size,
                    self.expanded_tile_size,
                    slices=self.max_layers,
                    force_array_view=True,
                )

            srnn2 = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=inter_tex,
                output_textures=outputs2,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.stages.append(srnn2)
            self.groups_per_stage.append(
                dispatch_groups(
                    self.expanded_tile_size, self.expanded_tile_size, last_pass=False
                )
            )

            # Final stage output (2x upscaled)
            final_out_array = Texture2D(
                self.expanded_tile_size * 2,
                self.expanded_tile_size * 2,
                slices=self.max_layers,
                force_array_view=True,
            )
            outputs_final = {"output": final_out_array}
            for i in range(self.factory.config.num_textures):
                outputs_final[f"t{i}"] = Texture2D(
                    self.expanded_tile_size * 2,
                    self.expanded_tile_size * 2,
                    slices=self.max_layers,
                    force_array_view=True,
                )

            srnn_final = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=inter_tex2,
                output_textures=outputs_final,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.stages.append(srnn_final)
            self.groups_per_stage.append(
                dispatch_groups(
                    self.expanded_tile_size * 2,
                    self.expanded_tile_size * 2,
                    last_pass=True,
                )
            )
        else:
            # Single stage (2x upscaling): output is final array
            final_out_array = Texture2D(
                self.expanded_tile_size * 2,
                self.expanded_tile_size * 2,
                slices=self.max_layers,
                force_array_view=True,
            )
            outputs1["output"] = final_out_array
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=input_tex,
                output_textures=outputs1,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.groups_per_stage[0] = dispatch_groups(
                self.expanded_tile_size * 2,
                self.expanded_tile_size * 2,
                last_pass=True,
            )

    # --------------------------------------------------------------------------
    #  Public methods
    # --------------------------------------------------------------------------
    def upload_full_frame(
        self, frame: memoryview, rects: List[Tuple[int, int, int, int, int]]
    ) -> None:
        """
        Upload expanded damage regions to the residual texture.

        The residual texture (`full_input_tex`) provides the surrounding context
        for the final pass. Only the areas that intersect expanded damage
        rectangles are updated; this is sufficient because the final pass only
        reads these regions.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from the frame grabber (x, y, w, h, hash).
        """
        if not rects:
            return

        expanded = expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.margin
        )
        if not expanded:
            return

        uploads = []
        stride = self.crop_width * 4

        for ex, ey, ew, eh in expanded:
            rect_data = bytearray(ew * eh * 4)
            for row in range(eh):
                src_start = (ey + row) * stride + ex * 4
                dst_start = row * ew * 4
                rect_data[dst_start : dst_start + ew * 4] = frame[
                    src_start : src_start + ew * 4
                ]
            # Upload to every layer so all tiles see the same context
            for layer in range(self.max_layers):
                uploads.append((bytes(rect_data), ex, ey, ew, eh, layer))

        self.full_input_tex.upload_subresources(uploads)

    def process_tiles(
        self, dirty_tiles: List[Tuple[int, int, bytes, int, int]]
    ) -> None:
        """
        Process a batch of expanded dirty tiles.

        The batch size is limited to `self.max_layers`. Each tile is assigned a
        unique layer index, uploaded to the input array, and processed by the
        SRCNN pipeline. The final pass writes the interior region directly to
        the full output texture.

        Args:
            dirty_tiles: List of tuples as returned by `extract_expanded_tiles`:
                (tile_x, tile_y, data_bytes, valid_x, valid_y)
        """
        if not dirty_tiles:
            return

        # Limit batch size
        batch = dirty_tiles[: self.max_layers]
        num_tiles = len(batch)

        expected_data_size = self.expanded_tile_size * self.expanded_tile_size * 4
        total_staging = num_tiles * expected_data_size

        # Ensure staging buffer is large enough
        if self.staging.size < total_staging:
            self.staging = Buffer(total_staging, heap_type=HEAP_UPLOAD)

        scale = 4 if self.double_upscale else 2
        full_out_w = self.crop_width * scale
        full_out_h = self.crop_height * scale

        uploads = []
        tile_batch: List[Tuple[int, int, int, bytes]] = []  # (tx, ty, layer, push_data)

        for layer_idx, (tx, ty, data, valid_x, valid_y) in enumerate(batch):
            # Sanitize data size
            if len(data) != expected_data_size:
                logger.warning(f"Tile ({tx},{ty}) size mismatch, adjusting.")
                if len(data) < expected_data_size:
                    data += b"\x00" * (expected_data_size - len(data))
                else:
                    data = data[:expected_data_size]

            # Upload tile to the input array layer
            uploads.append(
                (
                    data,
                    0,
                    0,
                    self.expanded_tile_size,
                    self.expanded_tile_size,
                    layer_idx,
                )
            )

            # Compute actual output extent (may be smaller at image edges)
            actual_out_w = min(
                self.tile_size * scale, full_out_w - tx * self.tile_size * scale
            )
            actual_out_h = min(
                self.tile_size * scale, full_out_h - ty * self.tile_size * scale
            )

            push_data = self._make_push_data(
                tx,
                ty,
                layer_idx,
                valid_x,
                valid_y,
                full_out_w,
                full_out_h,
                actual_out_w,
                actual_out_h,
            )
            tile_batch.append((tx, ty, layer_idx, push_data))

        # Perform all uploads
        self.input_tex.upload_subresources(uploads)

        # Build and execute dispatch sequence
        dispatches = self._build_dispatch_sequence(tile_batch)
        if dispatches:
            # Use the first pipeline's dispatch_sequence (any pipeline works)
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)

    def _build_dispatch_sequence(
        self, tile_batch: List[Tuple[int, int, int, bytes]]
    ) -> List[Tuple[Compute, int, int, int, bytes]]:
        """
        Build a flat list of dispatches for a batch of tiles.

        For each tile, we append all passes (stages) in order.
        The resulting sequence can be submitted in one call.

        Returns:
            List of (Compute, groups_x, groups_y, groups_z, push_data).
        """
        dispatches = []
        for _, _, _, push_data in tile_batch:
            for stage_idx, srnn in enumerate(self.stages):
                gx, gy = self.groups_per_stage[stage_idx]
                for pipe in srnn.pipelines:
                    dispatches.append((pipe, gx, gy, 1, push_data))
        return dispatches

    # --------------------------------------------------------------------------
    #  Static convenience wrappers (delegate to tile_utils)
    # --------------------------------------------------------------------------
    @staticmethod
    def expand_damage_rects(
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        margin: int,
    ) -> List[Tuple[int, int, int, int]]:
        """Delegate to `tile_utils.expand_damage_rects`."""
        return expand_damage_rects(rects, crop_width, crop_height, margin)

    @staticmethod
    def extract_expanded_tiles(
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
        crop_width: int,
        crop_height: int,
        tile_size: int,
        margin: int,
    ) -> List[Tuple[int, int, bytes, int, int]]:
        """Delegate to `tile_utils.extract_expanded_tiles`."""
        return extract_expanded_tiles(
            frame, rects, crop_width, crop_height, tile_size, margin
        )
