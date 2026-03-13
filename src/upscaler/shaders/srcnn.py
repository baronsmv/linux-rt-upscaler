import json
import os
import struct

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


def _pack_cb(in_w, in_h, out_w, out_h):
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


class SRCNN:
    def __init__(self, width, height, model_name):
        self._lanczos_pipeline = None
        self.width = width
        self.height = height
        self.model_name = model_name
        self._get_model_dir()
        self._load_config()
        self._load_shaders()
        self._create_resources()
        self._create_pipelines()

    def _get_model_dir(self):
        # Path: shaders/CuNNy/<model_name>/
        self.model_dir = os.path.join(
            os.path.dirname(__file__), "CuNNy", self.model_name
        )
        if not os.path.isdir(self.model_dir):
            raise FileNotFoundError(f"Model directory not found: {self.model_dir}")

    def _load_config(self):
        config_path = os.path.join(str(self.model_dir), "model.json")
        with open(config_path, "r") as f:
            self.cfg = json.load(f)
        # Validate required fields
        required = ["passes", "num_textures", "srv_uav", "samplers"]
        for key in required:
            if key not in self.cfg:
                raise ValueError(f"Missing required field '{key}' in model.json")

    def _load_shaders(self):
        self.shaders = []
        for i in range(self.cfg["passes"]):
            pass_file = os.path.join(self.model_dir, f"Pass{i + 1}.hlsl")
            with open(pass_file, "r") as f:
                self.shaders.append(hlsl.compile(f.read()))

    def _create_resources(self):
        w, h = self.width, self.height
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)

        self.textures = {}
        for i in range(self.cfg["num_textures"]):
            self.textures[f"t{i}"] = Texture2D(w, h, R8G8B8A8_UNORM)

        cb_size = struct.calcsize("IIIIffff")
        self.cbs = []
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

    def _create_pipelines(self):
        self.pipelines = []
        for i, (srv_names, uav_names) in enumerate(self.cfg["srv_uav"]):
            srv_list = []
            for name in srv_names:
                if name == "input":
                    srv_list.append(self.input)
                elif name == "output":
                    srv_list.append(self.output)
                else:
                    srv_list.append(self.textures[name])

            uav_list = []
            for name in uav_names:
                if name == "output":
                    uav_list.append(self.output)
                else:
                    uav_list.append(self.textures[name])

            sampler_list = []
            sampler_indices = self.cfg["samplers"][i]
            if "point" in sampler_indices:
                sampler_list.append(self.sampler_point)
            if "linear" in sampler_indices:
                sampler_list.append(self.sampler_linear)

            pipe = Compute(
                self.shaders[i],
                cbv=[self.cbs[i]],
                srv=srv_list,
                uav=uav_list,
                samplers=sampler_list,
            )
            self.pipelines.append(pipe)

    def upload(self, data):
        self.staging.upload2d(
            data,
            self.input.row_pitch,
            self.input.width,
            self.input.height,
            get_pixel_size(R8G8B8A8_UNORM),
        )
        self.staging.copy_to(self.input)

    def compute(self):
        w, h = self.width, self.height
        for i, pipe in enumerate(self.pipelines):
            if i < self.cfg["passes"] - 1:
                pipe.dispatch((w + 7) // 8, (h + 7) // 8, 1)
            else:
                pipe.dispatch((w * 2 + 15) // 16, (h * 2 + 15) // 16, 1)

    def _init_lanczos(self):
        if hasattr(self, "_lanczos_pipeline"):
            return
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
        self._lanczos_cb = Buffer(20, HEAP_UPLOAD)

    def scale_to(self, target_tex, target_width, target_height, blur=1.0):
        self._init_lanczos()
        cb_data = struct.pack(
            "IIIIf",
            self.width * 2,
            self.height * 2,
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
