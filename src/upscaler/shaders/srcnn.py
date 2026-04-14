import json
import logging
import os
import struct
from typing import Dict, List, Optional, Tuple

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
from compushady.formats import R8G8B8A8_UNORM
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
    return data


def dispatch_groups(
    width: int, height: int, last_pass: bool = False
) -> Tuple[int, int]:
    """
    Calculate dispatch groups for a given pass.
    - Intermediate passes: 8x8 thread groups
    - Final pass: 16x16 thread groups (output is 2x)
    """
    if last_pass:
        groups_x = (width * 2 + 15) // 16
        groups_y = (height * 2 + 15) // 16
    else:
        groups_x = (width + 7) // 8
        groups_y = (height + 7) // 8
    return groups_x, groups_y


class SRCNN:
    """
    CuNNy‑based upscaler. Supports single 2x or double 2x passes (4x total).
    """

    def __init__(
        self,
        width: int,
        height: int,
        model_name: str,
        double_upscale: bool,
    ) -> None:
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
        self._create_pipelines_first()
        if self.double_upscale:
            self.pipelines_first, self._first_in_w, self._first_in_h = (
                self._build_pipelines(
                    target_input=self.input,
                    target_output=self.intermediate,
                    target_textures=self.textures,
                    target_cbs=self.cbs,
                    target_width=self.width,
                    target_height=self.height,
                )
            )
            self._create_pipelines_second()
        else:
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

    def _get_model_dir(self) -> None:
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "CuNNy", self.model_name
        )
        if not os.path.isdir(self.model_dir):
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")

    def _load_config(self) -> None:
        with open(os.path.join(self.model_dir, "model.json"), "r") as f:
            self.cfg = json.load(f)
        required = ["passes", "num_textures", "srv_uav", "samplers"]
        for key in required:
            if key not in self.cfg:
                raise ValueError(f"Missing required field '{key}' in model.json")
        logger.info(
            f"Model config: passes={self.cfg['passes']}, textures={self.cfg['num_textures']}"
        )

    def _load_shaders(self) -> None:
        self.shaders = []
        for i in range(self.cfg["passes"]):
            with open(os.path.join(self.model_dir, f"Pass{i + 1}.hlsl"), "r") as f:
                self.shaders.append(hlsl.compile(f.read()))
        logger.info(f"Compiled {len(self.shaders)} shaders")

    def _create_resources(self) -> None:
        w, h = self.width, self.height
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)

        if self.double_upscale:
            self.intermediate = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)
            self.output = Texture2D(w * 4, h * 4, R8G8B8A8_UNORM)
        else:
            self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)

        self.textures: Dict[str, Texture2D] = {}
        for i in range(self.cfg["num_textures"]):
            self.textures[f"t{i}"] = Texture2D(w, h, R8G8B8A8_UNORM)

        cb_size = struct.calcsize("IIIIffff")
        self.cbs: List[Buffer] = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size, HEAP_UPLOAD)
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(w, h, w, h))
            else:
                cb.upload(_pack_cb(w, h, w * 2, h * 2))
            self.cbs.append(cb)

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

        self.pipelines_first: Optional[List[Compute]] = None
        self.pipelines_second: Optional[List[Compute]] = None

    def _create_pipelines_first(self) -> None:
        # Already done in __init__
        pass

    def _create_pipelines_second(self) -> None:
        new_w = self.width * 2
        new_h = self.height * 2
        second_textures = {
            f"t{i}": Texture2D(new_w, new_h, R8G8B8A8_UNORM)
            for i in range(self.cfg["num_textures"])
        }
        second_cbs = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(struct.calcsize("IIIIffff"), HEAP_UPLOAD)
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
            )
            pipelines.append(pipe)

        return pipelines, target_width, target_height

    def upload(self, frame_data: bytes) -> None:
        """Copy frame data into the staging buffer."""
        self.staging.upload(frame_data)
