import logging
import struct
from typing import List, Tuple

from .abc import ABCTileProcessor
from ..srcnn import dispatch_groups, SRCNN
from ..vulkan import Texture2D, Buffer, HEAP_UPLOAD, Compute

logger = logging.getLogger(__name__)


class TileProcessor(ABCTileProcessor):
    """
    Tile processing without caching.

    Dirty tiles are expanded by a context margin, uploaded to an array
    texture with multiple layers (one per tile in the batch), and processed
    by the SRCNN stages. The final pass writes only the interior valid
    region directly into the full output texture.

    The number of concurrent tiles is limited by `max_layers`. If more
    tiles are dirty, the caller should fall back to full-frame mode.
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
        Initialize the tile processor.

        Args:
            crop_width, crop_height: Dimensions of the captured crop area.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform 4x upscaling (two 2x stages).
            tile_size: Nominal input tile size (without margin).
            tile_context_margin: Extra border pixels for convolution context.
            max_layers: Maximum number of concurrent tiles per batch.
        """
        super().__init__(
            crop_width=crop_width,
            crop_height=crop_height,
            model_name=model_name,
            double_upscale=double_upscale,
            tile_size=tile_size,
            tile_context_margin=tile_context_margin,
            max_layers=max_layers,
            push_constant_size=56,  # 14 uints * 4 bytes
        )

        # Texture holding the full captured frame (with damage regions uploaded)
        # Used by the final pass as the residual (INPUT) texture
        self.full_input_tex = Texture2D(
            crop_width, crop_height, slices=self.max_layers, force_array_view=True
        )
        full_size = crop_width * crop_height * 4
        self.full_staging = Buffer(full_size, heap_type=HEAP_UPLOAD)

        self._create_stages()

    # ----------------------------------------------------------------------
    #  Stage construction – creates all SRCNN stages and custom final pass
    # ----------------------------------------------------------------------
    def _create_stages(self) -> None:
        """
        Create the SRCNN stages and the custom final pass pipeline.

        This method sets up:
          - Input texture array for expanded tiles (max_layers slices).
          - Intermediate feature map arrays (one per texture in the model).
          - One or two SRCNN stages (depending on double_upscale).
          - A custom final pipeline that writes directly to the full output
            texture, using `full_input_tex` as the residual input.
        """
        # ------------------------------------------------------------------
        # Stage 1 input: texture array sized for the expanded tile
        # ------------------------------------------------------------------
        input_tex1 = Texture2D(
            self.expanded_tile_size,
            self.expanded_tile_size,
            slices=self.max_layers,
            force_array_view=True,
        )

        # ------------------------------------------------------------------
        # Stage 1 outputs (intermediate feature maps) – all arrays
        # ------------------------------------------------------------------
        inter_tex = Texture2D(
            self.expanded_tile_size,
            self.expanded_tile_size,
            slices=self.max_layers,
            force_array_view=True,
        )
        outputs_1 = {"output": inter_tex}
        for i in range(self.factory.config.num_textures):
            outputs_1[f"t{i}"] = Texture2D(
                self.expanded_tile_size,
                self.expanded_tile_size,
                slices=self.max_layers,
                force_array_view=True,
            )

        srcnn_1 = SRCNN(
            factory=self.factory,
            width=self.expanded_tile_size,
            height=self.expanded_tile_size,
            input_texture=input_tex1,
            output_textures=outputs_1,
            push_constant_size=self.factory.config.push_constant_size,
        )
        self.stages.append(srcnn_1)
        self.groups_per_stage.append(
            dispatch_groups(
                self.expanded_tile_size, self.expanded_tile_size, last_pass=False
            )
        )

        if self.double_upscale:
            # Stage 2 input = Stage 1 output array
            input_tex_2 = inter_tex
            # Stage 2 outputs (feature maps) also same size as input
            inter_tex2 = Texture2D(
                self.expanded_tile_size,
                self.expanded_tile_size,
                slices=self.max_layers,
                force_array_view=True,
            )
            outputs_2 = {"output": inter_tex2}
            for i in range(self.factory.config.num_textures):
                outputs_2[f"t{i}"] = Texture2D(
                    self.expanded_tile_size,
                    self.expanded_tile_size,
                    slices=self.max_layers,
                    force_array_view=True,
                )

            srcnn_2 = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=input_tex_2,
                output_textures=outputs_2,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.stages.append(srcnn_2)
            self.groups_per_stage.append(
                dispatch_groups(
                    self.expanded_tile_size, self.expanded_tile_size, last_pass=False
                )
            )

            # Final output array for the last stage (size = expanded_tile_size * 2)
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
            srcnn_final = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=inter_tex2,
                output_textures=outputs_final,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.stages.append(srcnn_final)
            self.groups_per_stage.append(
                dispatch_groups(
                    self.expanded_tile_size * 2,
                    self.expanded_tile_size * 2,
                    last_pass=True,
                )
            )
        else:
            # For 2x only, stage 1 writes to final output array
            final_out_array = Texture2D(
                self.expanded_tile_size * 2,
                self.expanded_tile_size * 2,
                slices=self.max_layers,
                force_array_view=True,
            )
            outputs_1["output"] = final_out_array
            self.stages[0] = SRCNN(
                factory=self.factory,
                width=self.expanded_tile_size,
                height=self.expanded_tile_size,
                input_texture=input_tex1,
                output_textures=outputs_1,
                push_constant_size=self.factory.config.push_constant_size,
            )
            self.groups_per_stage[0] = dispatch_groups(
                self.expanded_tile_size * 2, self.expanded_tile_size * 2, last_pass=True
            )

        # Keep a reference to the input texture for uploads
        self.input_tex = self.stages[0].input

        # ------------------------------------------------------------------
        #  Final pass pipeline (customised for offset writes)
        # ------------------------------------------------------------------
        final_pass_index = self.factory.config.passes - 1
        final_shader = self.factory.config.shaders[final_pass_index]

        scale = 4 if self.double_upscale else 2
        full_out_w = self.crop_width * scale
        full_out_h = self.crop_height * scale
        cb_data = struct.pack(
            "IIIIffff",
            self.expanded_tile_size,  # in_width  (feature map size)
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

        # SRV list: [full_input_tex] + intermediate textures from the last pre-final stage
        srv_list = [self.full_input_tex]
        pre_final_stage = self.stages[-2] if self.double_upscale else self.stages[0]
        for i in range(self.factory.config.num_textures):
            srv_list.append(pre_final_stage.outputs[f"t{i}"])

        # UAV list: final output texture (2D)
        uav_list = [self.output_texture]

        # Samplers for the final pass.
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

        # Replace the original final pass pipeline with our custom one
        if self.double_upscale:
            self.stages[-1].pipelines[-1] = self.final_pipeline
        else:
            self.stages[0].pipelines[-1] = self.final_pipeline

    def _get_pipelines_for_batch(self) -> List[Compute]:
        """
        Return the list of Compute pipelines for a tile batch.
        Overrides to include the custom final pass.
        """
        if self.double_upscale:
            return (
                self.stages[0].pipelines
                + self.stages[1].pipelines[:-1]
                + [self.final_pipeline]
            )
        else:
            return self.stages[0].pipelines[:-1] + [self.final_pipeline]

    # ----------------------------------------------------------------------
    #  Residual texture upload (damage regions expanded by margin)
    # ----------------------------------------------------------------------
    def upload_full_frame(
        self,
        frame: memoryview,
        rects: List[Tuple[int, int, int, int, int]],
    ) -> None:
        """
        Upload expanded damage regions to the residual texture.

        This texture provides the network with the surrounding context
        needed for the final pass. Only the damaged areas are updated.

        Args:
            frame: Raw BGRA pixel data for the entire crop area.
            rects: Damage rectangles from FrameGrabber.
        """
        if not rects:
            return

        expanded_rects = self.expand_damage_rects(
            rects, self.crop_width, self.crop_height, self.margin
        )
        uploads = []
        stride = self.crop_width * 4

        for ex, ey, ew, eh in expanded_rects:
            rect_data = bytearray(ew * eh * 4)
            for row in range(eh):
                src_start = (ey + row) * stride + ex * 4
                dst_start = row * ew * 4
                rect_data[dst_start : dst_start + ew * 4] = frame[
                    src_start : src_start + ew * 4
                ]
            # Upload to every layer (0 .. max_layers-1) so that all tiles see the same context
            for layer in range(self.max_layers):
                uploads.append((bytes(rect_data), ex, ey, ew, eh, layer))
        self.full_input_tex.upload_subresources(uploads)

    # ----------------------------------------------------------------------
    #  Main tile processing
    # ----------------------------------------------------------------------
    def process_tiles(
        self, dirty_tiles: List[Tuple[int, int, bytes, int, int]]
    ) -> None:
        """
        Process a batch of expanded dirty tiles using multi-layer array textures.

        The batch is limited to `self.max_layers`. Each tile is assigned a
        unique layer index, uploaded to the corresponding slice of the input
        array, and processed concurrently. The final pass writes the valid
        interior region directly to the full output texture.

        Args:
            dirty_tiles: List of (tile_x, tile_y, data_bytes, valid_x, valid_y)
                as returned by `extract_expanded_tiles`.
        """
        if not dirty_tiles:
            return

        # Limit batch size to maximum number of layers
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
        tile_batch = []  # (tx, ty, layer, push_data)

        for layer_idx, (tx, ty, data, valid_x, valid_y) in enumerate(batch):
            # Guarantee data length matches expected size
            if len(data) != expected_data_size:
                logger.warning(f"Tile ({tx},{ty}) size mismatch, adjusting.")
                if len(data) < expected_data_size:
                    data += b"\x00" * (expected_data_size - len(data))
                else:
                    data = data[:expected_data_size]

            # Upload tile data to layer `layer_idx` of the input array
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

            # Compute source and destination offsets
            src_x = tx * self.tile_size
            src_y = ty * self.tile_size
            dst_x = tx * self.tile_size * scale
            dst_y = ty * self.tile_size * scale

            # Scale the input-pixel offsets to output-pixel space
            valid_block_x = valid_x * scale
            valid_block_y = valid_y * scale

            actual_out_w = min(self.tile_size * scale, full_out_w - dst_x)
            actual_out_h = min(self.tile_size * scale, full_out_h - dst_y)

            push_data = struct.pack(
                "IIIIIIIIIIIIII",  # 14 uints = 56 bytes
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
            )
            tile_batch.append((tx, ty, layer_idx, push_data))

        # Upload all tiles to their respective layers
        self.input_tex.upload_subresources(uploads)

        # Build and execute dispatch sequence
        dispatches = self._build_dispatch_sequence(tile_batch)
        if dispatches:
            self.stages[0].pipelines[0].dispatch_sequence(sequence=dispatches)
