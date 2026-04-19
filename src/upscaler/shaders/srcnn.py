import json
import logging
import os
import struct
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from ..vulkan import (
    Buffer,
    Compute,
    Sampler,
    Texture2D,
    SAMPLER_FILTER_LINEAR,
    SAMPLER_FILTER_POINT,
)

if TYPE_CHECKING:
    from ..pipeline.cache import TileAtlasManager

logger = logging.getLogger(__name__)


def _pack_cb(in_w: int, in_h: int, out_w: int, out_h: int) -> bytes:
    """Pack constant buffer data for SRCNN shaders."""
    return struct.pack(
        "IIIIffff",
        in_w,
        in_h,
        out_w,
        out_h,
        1.0 / in_w,
        1.0 / in_h,
        1.0 / out_w,
        1.0 / out_h,
    )


def dispatch_groups(
    width: int, height: int, last_pass: bool = False
) -> Tuple[int, int]:
    """
    Calculate compute dispatch groups for a given pass.

    Args:
        width: Input texture width (or output width for final pass).
        height: Input texture height.
        last_pass: True if this is the final pass of a stage (output is 2x).

    Returns:
        Tuple (groups_x, groups_y) for vkCmdDispatch.
    """
    if last_pass:
        return (width * 2 + 15) // 16, (height * 2 + 15) // 16
    return (width + 7) // 8, (height + 7) // 8


class SRCNN:
    """
    CuNNy‑based upscaler using Vulkan compute shaders.

    Supports:
      - Full‑frame upscaling (2x or 4x via double‑upscale).
      - Tile‑mode caching: processes individual tiles and writes to a texture atlas.

    The model is defined by a directory containing `model.json` and pre‑compiled
    SPIR‑V shaders (`PassN.spv` for full‑frame, `PassN_tile.spv` for tile mode).

    Attributes:
        output (Texture2D): Final upscaled texture (full‑frame mode only).
        staging (Buffer): Staging buffer for full‑frame uploads.
        outputs (List[str]): Names of intermediate output textures (e.g., ['t0','t1']).
        tile_mode (bool): Whether the instance is operating in tile mode.
    """

    output: Texture2D
    staging: Buffer

    def __init__(
        self,
        width: int,
        height: int,
        model_name: str,
        double_upscale: bool = False,
        tile_size: int = 64,
        tile_mode: bool = False,
        atlas_manager: Optional["TileAtlasManager"] = None,
        input_atlas: Optional[Texture2D] = None,
        output_atlases: Optional[List[Texture2D]] = None,
        output_atlas: Optional[Texture2D] = None,
    ) -> None:
        """
        Initialize the SRCNN upscaler.

        Args:
            width: Crop width in pixels.
            height: Crop height in pixels.
            model_name: Name of the CuNNy model subdirectory.
            double_upscale: If True, perform two 2x passes for 4x total upscale.
            tile_size: Input tile size in pixels (used only in tile_mode).
            tile_mode: If True, operate in tile‑cache mode.
            atlas_manager: Required in tile_mode; manages cache layers.
            input_atlas: Required in tile_mode; Texture2D array for input tiles.
            output_atlases: Required in tile_mode; list of Texture2D arrays for
                intermediate outputs (one per intermediate texture).
            output_atlas: Required in tile_mode; Texture2D array for final output tiles.

        Raises:
            FileNotFoundError: If the model directory or SPIR‑V shaders are missing.
            ValueError: If tile_mode is True but required atlas parameters are missing.
        """
        self.width = width
        self.height = height
        self.model_name = model_name
        self.double_upscale = double_upscale
        self.tile_size = tile_size
        self.tile_mode = tile_mode
        self.atlas_manager = atlas_manager
        self.input_atlas = input_atlas
        self.output_atlases = output_atlases
        self.output_atlas = output_atlas

        self._get_model_dir()
        self._load_config()

        if tile_mode:
            if not all([atlas_manager, input_atlas, output_atlases, output_atlas]):
                raise ValueError(
                    "Tile mode requires atlas_manager, input_atlas, output_atlases, and output_atlas"
                )
            self._init_tile_mode()
        else:
            self._init_full_mode()

    @property
    def outputs(self) -> List[str]:
        """
        Return the list of intermediate output texture names.

        Example: ['t0', 't1', 't2', 't3'].
        This is derived from the model's `srv_uav` configuration.
        """
        outputs = set()
        for _, uav_names in self.cfg["srv_uav"]:
            for name in uav_names:
                if name != "output":
                    outputs.add(name)
        return sorted(outputs)

    # --------------------------------------------------------------------------
    # Internal: model discovery and configuration
    # --------------------------------------------------------------------------
    def _get_model_dir(self) -> None:
        """Locate the model directory under `shaders/CuNNy/`."""
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "CuNNy", self.model_name
        )
        if not os.path.isdir(self.model_dir):
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")

    def _load_config(self) -> None:
        """Load model.json and validate required fields."""
        config_path = os.path.join(self.model_dir, "model.json")
        with open(config_path, "r") as f:
            self.cfg = json.load(f)
        required = ["passes", "num_textures", "srv_uav", "samplers"]
        for key in required:
            if key not in self.cfg:
                raise ValueError(f"Missing required field '{key}' in model.json")
        logger.info(
            f"Model config: passes={self.cfg['passes']}, textures={self.cfg['num_textures']}"
        )

    def _load_shaders(self, tile: bool = False) -> None:
        """
        Load precompiled SPIR‑V shaders for each pass.

        Args:
            tile: If True, load shaders with '_tile' suffix.
        """
        suffix = "_tile" if tile else ""
        self.shaders = []
        for i in range(self.cfg["passes"]):
            spv_path = os.path.join(self.model_dir, f"Pass{i + 1}{suffix}.spv")
            if not os.path.exists(spv_path):
                raise FileNotFoundError(f"Shader not found: {spv_path}")
            with open(spv_path, "rb") as f:
                self.shaders.append(f.read())
        logger.info(f"Loaded {len(self.shaders)} SPIR‑V shaders (tile={tile})")

    def _create_samplers(self) -> None:
        """Create point and linear samplers for texture access."""
        self.sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT, filter_mag=SAMPLER_FILTER_POINT
        )
        self.sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR, filter_mag=SAMPLER_FILTER_LINEAR
        )

    # --------------------------------------------------------------------------
    # Full‑frame mode
    # --------------------------------------------------------------------------
    def _init_full_mode(self) -> None:
        """Initialize resources and pipelines for full‑frame upscaling."""
        self._load_shaders(tile=False)
        self._create_full_resources()
        self._create_samplers()

        self.pipelines_first, self._first_in_w, self._first_in_h = (
            self._build_pipelines(
                target_input=self.input,
                target_output=(
                    self.output if not self.double_upscale else self.intermediate
                ),
                target_textures=self.textures,
                target_cbs=self.cbs,
                target_width=self.width,
                target_height=self.height,
            )
        )
        if self.double_upscale:
            self._create_pipelines_second()

    def _create_full_resources(self) -> None:
        """Allocate textures, staging buffer, and constant buffers for full‑frame mode."""
        w, h = self.width, self.height
        self.input = Texture2D(w, h)
        self.staging = Buffer(self.input.size)

        if self.double_upscale:
            self.intermediate = Texture2D(w * 2, h * 2)
            self.output = Texture2D(w * 4, h * 4)
        else:
            self.output = Texture2D(w * 2, h * 2)

        self.textures: Dict[str, Texture2D] = {}
        for i in range(self.cfg["num_textures"]):
            self.textures[f"t{i}"] = Texture2D(w, h)

        cb_size = struct.calcsize("IIIIffff")
        self.cbs: List[Buffer] = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size)
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(w, h, w, h))
            else:
                cb.upload(_pack_cb(w, h, w * 2, h * 2))
            self.cbs.append(cb)

    def _create_pipelines_second(self) -> None:
        """Create second‑stage pipelines for double‑upscale (4x total)."""
        new_w = self.width * 2
        new_h = self.height * 2
        second_textures = {
            f"t{i}": Texture2D(new_w, new_h) for i in range(self.cfg["num_textures"])
        }
        second_cbs = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(struct.calcsize("IIIIffff"))
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(new_w, new_h, new_w, new_h))
            else:
                cb.upload(_pack_cb(new_w, new_h, new_w * 2, new_h * 2))
            second_cbs.append(cb)

        self.pipelines_second, self._second_in_w, self._second_in_h = (
            self._build_pipelines(
                target_input=self.intermediate,
                target_output=self.output,
                target_textures=second_textures,
                target_cbs=second_cbs,
                target_width=new_w,
                target_height=new_h,
            )
        )

    def _build_pipelines(
        self,
        target_input: Texture2D,
        target_output: Texture2D,
        target_textures: Dict[str, Texture2D],
        target_cbs: List[Buffer],
        target_width: int,
        target_height: int,
    ) -> Tuple[List[Compute], int, int]:
        """
        Build compute pipelines for a stage (first or second).

        Returns:
            Tuple of (list of Compute pipelines, input width, input height).
        """
        pipelines = []
        for i, (srv_names, uav_names) in enumerate(self.cfg["srv_uav"]):
            srv_list = [
                (
                    target_input
                    if name == "input"
                    else target_output if name == "output" else target_textures[name]
                )
                for name in srv_names
            ]
            uav_list = [
                target_output if name == "output" else target_textures[name]
                for name in uav_names
            ]

            samplers = []
            if "point" in self.cfg["samplers"][i]:
                samplers.append(self.sampler_point)
            if "linear" in self.cfg["samplers"][i]:
                samplers.append(self.sampler_linear)

            pipe = Compute(
                self.shaders[i],
                cbv=[target_cbs[i]],
                srv=srv_list,
                uav=uav_list,
                samplers=samplers,
                push_size=8 if self.tile_mode else 0,
            )
            pipelines.append(pipe)
        return pipelines, target_width, target_height

    # --------------------------------------------------------------------------
    # Tile mode
    # --------------------------------------------------------------------------
    def _init_tile_mode(self) -> None:
        """Initialize resources and pipelines for tile‑mode (cache‑aware) upscaling."""
        self._tile_out_w = self.tile_size * (4 if self.double_upscale else 2)
        self._tile_out_h = self.tile_size * (4 if self.double_upscale else 2)

        self._load_shaders(tile=True)
        self._create_samplers()

        first_cbs = self._create_tile_constant_buffers(
            in_w=self.tile_size,
            in_h=self.tile_size,
            out_w=self._tile_out_w,
            out_h=self._tile_out_h,
        )
        self.pipelines_first = self._build_tile_pipelines(cbs=first_cbs, is_final=False)

        if self.double_upscale:
            second_in = self.tile_size * 2
            second_out = self._tile_out_w * 2
            second_cbs = self._create_tile_constant_buffers(
                in_w=second_in,
                in_h=second_in,
                out_w=second_out,
                out_h=second_out,
            )
            self.pipelines_second = self._build_tile_pipelines(
                cbs=second_cbs, is_final=True
            )

    def _create_tile_constant_buffers(
        self, in_w: int, in_h: int, out_w: int, out_h: int
    ) -> List[Buffer]:
        """Create and upload constant buffers for a tile pipeline stage."""
        cb_size = struct.calcsize("IIIIffff")
        cbs: List[Buffer] = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size)
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(in_w, in_h, in_w, in_h))
            else:
                cb.upload(_pack_cb(in_w, in_h, out_w, out_h))
            cbs.append(cb)
        return cbs

    def _build_tile_pipelines(self, cbs: List[Buffer], is_final: bool) -> List[Compute]:
        """
        Build compute pipelines for tile mode.

        Args:
            cbs: Constant buffers for this stage.
            is_final: True if this stage produces the final upscaled output.
        """
        pipelines = []
        for i, (srv_names, uav_names) in enumerate(self.cfg["srv_uav"]):
            srv_list = []
            for name in srv_names:
                if name == "input":
                    srv_list.append(self.input_atlas)
                else:
                    idx = int(name[1:])
                    srv_list.append(self.output_atlases[idx])

            uav_list = []
            for name in uav_names:
                if name == "output":
                    if not is_final:
                        raise ValueError("'output' UAV only allowed in final stage")
                    uav_list.append(self.output_atlas)
                else:
                    idx = int(name[1:])
                    uav_list.append(self.output_atlases[idx])

            samplers = []
            if "point" in self.cfg["samplers"][i]:
                samplers.append(self.sampler_point)
            if "linear" in self.cfg["samplers"][i]:
                samplers.append(self.sampler_linear)

            pipe = Compute(
                self.shaders[i],
                cbv=[cbs[i]],
                srv=srv_list,
                uav=uav_list,
                samplers=samplers,
                push_size=8,
            )
            pipelines.append(pipe)
        return pipelines

    # --------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------
    def upload(self, frame_data: bytes) -> None:
        """
        Upload full‑frame data to the staging buffer (full‑frame mode only).

        Args:
            frame_data: Raw BGRA pixel data of size width*height*4.

        Raises:
            RuntimeError: If called in tile mode.
        """
        if self.tile_mode:
            raise RuntimeError("upload() called in tile mode")
        self.staging.upload(frame_data)

    def process_tiles(self, dirty_tiles: List[Tuple[int, int, int, bytes]]) -> None:
        """
        Process a batch of dirty tiles (tile mode only).

        Args:
            dirty_tiles: List of (tile_x, tile_y, hash, data_bytes). Each tile's
                data must be exactly tile_size × tile_size × 4 bytes.

        Raises:
            RuntimeError: If called in full‑frame mode.
        """
        if not self.tile_mode:
            raise RuntimeError("process_tiles() called in full‑frame mode")

        # Allocate layers and prepare uploads
        upload_list = []  # (data, layer)
        tile_info = []  # (tile_x, tile_y, layer)
        for tx, ty, hash_val, data in dirty_tiles:
            layer, was_cached = self.atlas_manager.acquire_layer(tx, ty, hash_val)
            if was_cached:
                continue
            upload_list.append((data, layer))
            tile_info.append((tx, ty, layer))

        if not upload_list:
            return

        # Upload to input atlas
        subresources = [
            (data, 0, 0, self.tile_size, self.tile_size, layer)
            for data, layer in upload_list
        ]
        self.input_atlas.upload_subresources(subresources)

        # Dispatch pipelines for each tile
        groups_x, groups_y = dispatch_groups(
            self._tile_out_w, self._tile_out_h, last_pass=False
        )
        push_struct = struct.Struct("II")
        for tx, ty, layer in tile_info:
            push_data = push_struct.pack(layer, layer)
            for pipe in self.pipelines_first:
                pipe.dispatch(groups_x, groups_y, 1, push=push_data)
            if self.double_upscale:
                groups_x2, groups_y2 = dispatch_groups(
                    self._tile_out_w, self._tile_out_h, last_pass=True
                )
                for pipe in self.pipelines_second:
                    pipe.dispatch(groups_x2, groups_y2, 1, push=push_data)
