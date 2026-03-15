import json
import logging
import os
import struct
from typing import Any, Dict, List, Optional, Tuple

from compushady import (
    Compute,
    Buffer,
    Texture2D,
    HEAP_UPLOAD,
    Sampler,
    SAMPLER_FILTER_POINT,
    SAMPLER_FILTER_LINEAR,
    SAMPLER_ADDRESS_MODE_CLAMP,
)
from compushady.formats import R8G8B8A8_UNORM, get_pixel_size
from compushady.shaders import hlsl

logger = logging.getLogger(__name__)


def _pack_cb(in_w: int, in_h: int, out_w: int, out_h: int) -> bytes:
    """Pack constant buffer data for shaders."""
    data = struct.pack(
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
    logger.debug(f"Packed CB: {in_w}x{in_h} -> {out_w}x{out_h}")
    return data


def _dispatch_groups(
    width: int, height: int, last_pass: bool = False
) -> Tuple[int, int]:
    """
    Calculate dispatch groups for a given pass.
    - For intermediate passes (not last), thread group size is 8x8 (from shader).
    - For the last pass, group size is 16x16 (because output is double width/height?).
    The shaders in CuNNy typically use 8x8 for internal passes and 16x16 for the final upscaling pass.
    This matches the original code: (w+7)//8 for non‑last, (w*2+15)//16 for last.
    """
    if last_pass:
        # Last pass: output is 2x, shader likely uses 16x16 groups
        groups_x = (width * 2 + 15) // 16
        groups_y = (height * 2 + 15) // 16
        logger.debug(f"Last pass dispatch groups: {groups_x}x{groups_y}")
    else:
        groups_x = (width + 7) // 8
        groups_y = (height + 7) // 8
        logger.debug(f"Intermediate pass dispatch groups: {groups_x}x{groups_y}")
    return groups_x, groups_y


class SRCNN:
    """
    CuNNy‑based upscaler. Supports single 2x upscale or double 2x passes (4x total).
    """

    def __init__(
        self,
        width: int,
        height: int,
        model_name: str,
        double_upscale: bool,
    ) -> None:
        """
        :param width: Original window width (source).
        :param height: Original window height.
        :param model_name: Name of the model (subdirectory in CuNNy/).
        :param double_upscale: If True, performs two 2x passes (total 4x).
        """
        self.width = width
        self.height = height
        self.model_name = model_name
        self.double_upscale = double_upscale

        logger.info(
            f"Initializing SRCNN: {width}x{height}, model='{model_name}', double={double_upscale}"
        )

        self._get_model_dir()
        self._load_config()
        self._load_shaders()
        self._create_resources()
        self._create_pipelines_first()  # pipelines for normal (or first pass)
        if self.double_upscale:
            self._create_pipelines_second()

        # Lanczos resources (lazy initialised)
        self._lanczos_shader: Optional[Any] = None
        self._lanczos_sampler: Optional[Sampler] = None
        self._lanczos_cb: Optional[Buffer] = None
        self._lanczos_pipeline: Optional[Compute] = None

    # ----------------------------------------------------------------------
    # Initialisation helpers
    # ----------------------------------------------------------------------

    def _get_model_dir(self) -> None:
        """Locate and verify the model directory."""
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "CuNNy", self.model_name
        )
        if not os.path.isdir(self.model_dir):
            logger.error(f"Model directory not found: {self.model_dir}")
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")
        logger.debug(f"Model directory: {self.model_dir}")

    def _load_config(self) -> None:
        """Load and validate model.json."""
        config_path = os.path.join(self.model_dir, "model.json")
        logger.debug(f"Loading config from {config_path}")
        with open(config_path, "r") as f:
            self.cfg = json.load(f)
        # Validate required fields
        required = ["passes", "num_textures", "srv_uav", "samplers"]
        for key in required:
            if key not in self.cfg:
                logger.error(f"Missing required field '{key}' in model.json")
                raise ValueError(f"Missing required field '{key}' in model.json")
        logger.info(
            f"Model config loaded: passes={self.cfg['passes']}, num_textures={self.cfg['num_textures']}"
        )

    def _load_shaders(self) -> None:
        """Compile HLSL shaders for each pass."""
        self.shaders = []
        for i in range(self.cfg["passes"]):
            pass_file = os.path.join(self.model_dir, f"Pass{i + 1}.hlsl")
            logger.debug(f"Compiling shader: {pass_file}")
            with open(pass_file, "r") as f:
                shader_src = f.read()
            self.shaders.append(hlsl.compile(shader_src))
        logger.info(f"Compiled {len(self.shaders)} shaders")

    def _create_resources(self) -> None:
        """Create all GPU resources (textures, buffers, samplers)."""
        w, h = self.width, self.height

        # Input texture (original size)
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        logger.debug(f"Created input texture: {w}x{h}")

        # Staging buffer for upload
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)
        logger.debug(f"Created staging buffer: size={self.input.size}")

        if self.double_upscale:
            # Intermediate texture (2x) and final output (4x)
            self.intermediate = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)
            self.output = Texture2D(w * 4, h * 4, R8G8B8A8_UNORM)
            logger.debug(f"Created intermediate: {w*2}x{h*2}, output: {w*4}x{h*4}")
        else:
            # Normal output (2x)
            self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)
            logger.debug(f"Created output texture: {w*2}x{h*2}")

        # Textures for internal passes (size depends on current stage)
        self.textures: Dict[str, Texture2D] = {}
        for i in range(self.cfg["num_textures"]):
            self.textures[f"t{i}"] = Texture2D(w, h, R8G8B8A8_UNORM)
        logger.debug(
            f"Created {self.cfg['num_textures']} internal textures at original size"
        )

        # Constant buffers for each pass (first run)
        cb_size = struct.calcsize("IIIIffff")
        self.cbs: List[Buffer] = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size, HEAP_UPLOAD)
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(w, h, w, h))
            else:
                cb.upload(_pack_cb(w, h, w * 2, h * 2))
            self.cbs.append(cb)
        logger.debug(f"Created {len(self.cbs)} constant buffers for first run")

        # Samplers (shared)
        self.sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self.sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        logger.debug("Samplers created")

        # For double upscale, we'll create additional pipelines later.
        self.pipelines_first: Optional[List[Compute]] = None
        self.pipelines_second: Optional[List[Compute]] = None

    def _create_pipelines_first(self) -> None:
        """
        Create pipelines for the first (or only) upscaling run.
        This uses the original input and output textures.
        """
        logger.debug("Creating pipelines for first/only upscale run")
        self.pipelines_first, self._first_in_w, self._first_in_h = (
            self._build_pipelines(
                target_input=self.input,
                target_output=self.output,
                target_textures=self.textures,
                target_cbs=self.cbs,
                target_width=self.width,
                target_height=self.height,
            )
        )
        logger.info(f"Created {len(self.pipelines_first)} pipelines for first run")

    def _create_pipelines_second(self) -> None:
        """
        Create pipelines for the second upscaling run (when double_upscale=True).
        This uses intermediate textures (2x) as input and final output.
        """
        logger.debug("Creating pipelines for second upscale run")
        new_w = self.width * 2
        new_h = self.height * 2

        # Textures for internal passes at 2x size
        second_textures: Dict[str, Texture2D] = {}
        for i in range(self.cfg["num_textures"]):
            second_textures[f"t{i}"] = Texture2D(new_w, new_h, R8G8B8A8_UNORM)
        logger.debug(
            f"Created {self.cfg['num_textures']} internal textures at {new_w}x{new_h}"
        )

        # Constant buffers for second run
        second_cbs: List[Buffer] = []
        cb_size = struct.calcsize("IIIIffff")
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size, HEAP_UPLOAD)
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
        logger.info(f"Created {len(self.pipelines_second)} pipelines for second run")

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
        Helper to build a list of compute pipelines for a given set of resources.
        Returns (pipelines, input_width, input_height).
        """
        pipelines = []
        for i, (srv_names, uav_names) in enumerate(self.cfg["srv_uav"]):
            srv_list = []
            for name in srv_names:
                if name == "input":
                    srv_list.append(target_input)
                elif name == "output":
                    srv_list.append(target_output)
                else:
                    srv_list.append(target_textures[name])

            uav_list = []
            for name in uav_names:
                if name == "output":
                    uav_list.append(target_output)
                else:
                    uav_list.append(target_textures[name])

            sampler_list = []
            sampler_indices = self.cfg["samplers"][i]
            if "point" in sampler_indices:
                sampler_list.append(self.sampler_point)
            if "linear" in sampler_indices:
                sampler_list.append(self.sampler_linear)

            pipe = Compute(
                self.shaders[i],
                cbv=[target_cbs[i]],
                srv=srv_list,
                uav=uav_list,
                samplers=sampler_list,
            )
            pipelines.append(pipe)
            logger.debug(
                f"Built pipeline for pass {i}: SRV={srv_names}, UAV={uav_names}"
            )

        return pipelines, target_width, target_height

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def upload(self, data: Any) -> None:
        """Upload raw frame data to the input texture."""
        logger.debug(f"Uploading data (size {len(data)}) to input texture")
        self.staging.upload2d(
            data,
            self.input.row_pitch,
            self.input.width,
            self.input.height,
            get_pixel_size(R8G8B8A8_UNORM),
        )
        self.staging.copy_to(self.input)
        logger.debug("Upload complete")

    def compute(self) -> None:
        """Run the upscaling compute shaders."""
        if not self.double_upscale:
            self._compute_single()
        else:
            self._compute_double()

    def _compute_single(self) -> None:
        """Single 2x upscale."""
        logger.info("Starting single 2x upscale")
        if self.pipelines_first is None:
            logger.error("Pipelines for first run not created")
            return

        pipelines = self.pipelines_first
        w, h = self._first_in_w, self._first_in_h

        for i, pipe in enumerate(pipelines):
            last_pass = i == self.cfg["passes"] - 1
            gx, gy = _dispatch_groups(w, h, last_pass)
            logger.debug(f"Dispatching pass {i}: groups={gx}x{gy}")
            pipe.dispatch(gx, gy, 1)
        logger.info("Single upscale complete")

    def _compute_double(self) -> None:
        """Two 2x upscale passes (total 4x)."""
        logger.info("Starting double upscale (4x)")

        # First run: input -> intermediate
        if self.pipelines_first is None:
            logger.error("Pipelines for first run not created")
            return
        w1, h1 = self._first_in_w, self._first_in_h
        for i, pipe in enumerate(self.pipelines_first):
            last_pass = i == self.cfg["passes"] - 1
            gx, gy = _dispatch_groups(w1, h1, last_pass)
            logger.debug(f"First run pass {i}: groups={gx}x{gy}")
            pipe.dispatch(gx, gy, 1)

        # Second run: intermediate -> output
        if self.pipelines_second is None:
            logger.error("Pipelines for second run not created")
            return
        w2, h2 = self._second_in_w, self._second_in_h
        for i, pipe in enumerate(self.pipelines_second):
            last_pass = i == self.cfg["passes"] - 1
            gx, gy = _dispatch_groups(w2, h2, last_pass)
            logger.debug(f"Second run pass {i}: groups={gx}x{gy}")
            pipe.dispatch(gx, gy, 1)

        logger.info("Double upscale complete")

    def _init_lanczos(self) -> None:
        """Lazy initialisation of Lanczos scaling resources."""
        if self._lanczos_shader is not None:
            return
        logger.debug("Initialising Lanczos resources")
        shader_dir = os.path.dirname(__file__)
        with open(os.path.join(shader_dir, "lanczos2.hlsl"), "r") as f:
            self._lanczos_shader = hlsl.compile(f.read())
        self._lanczos_sampler = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
            address_mode_u=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_v=SAMPLER_ADDRESS_MODE_CLAMP,
            address_mode_w=SAMPLER_ADDRESS_MODE_CLAMP,
        )
        self._lanczos_cb = Buffer(20, HEAP_UPLOAD)  # 5 ints? Actually 5 * 4 = 20 bytes
        logger.debug("Lanczos resources ready")

    def scale_to(
        self,
        target_tex: Texture2D,
        target_width: int,
        target_height: int,
        blur: float = 1.0,
    ) -> None:
        """
        Scale the current output texture to a target texture using Lanczos.
        Typically called after compute().
        """
        logger.info(
            f"Scaling output to {target_width}x{target_height} with blur={blur}"
        )
        self._init_lanczos()

        src_w = self.output.width
        src_h = self.output.height
        cb_data = struct.pack(
            "IIIIf",
            src_w,
            src_h,
            target_width,
            target_height,
            blur,
        )
        self._lanczos_cb.upload(cb_data)

        groups_x = (target_width + 15) // 16
        groups_y = (target_height + 15) // 16
        self._lanczos_pipeline = Compute(
            self._lanczos_shader,
            srv=[self.output],
            uav=[target_tex],
            cbv=[self._lanczos_cb],
            samplers=[self._lanczos_sampler],
        )
        self._lanczos_pipeline.dispatch(groups_x, groups_y, 1)
        logger.debug("Lanczos scaling dispatched")
