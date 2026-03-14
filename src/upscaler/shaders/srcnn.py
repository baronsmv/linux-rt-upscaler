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
    def __init__(self, width, height, model_name, double_upscale):
        self._lanczos_pipeline = None
        self.width = width
        self.height = height
        self.model_name = model_name
        self.double_upscale = double_upscale
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

        # Input texture (original size)
        self.input = Texture2D(w, h, R8G8B8A8_UNORM)
        self.staging = Buffer(self.input.size, HEAP_UPLOAD)

        if self.double_upscale:
            # Intermediate texture (2x) and final output (4x)
            self.intermediate = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)
            self.output = Texture2D(w * 4, h * 4, R8G8B8A8_UNORM)
        else:
            # Normal output (2x)
            self.output = Texture2D(w * 2, h * 2, R8G8B8A8_UNORM)

        self.textures = {}
        for i in range(self.cfg["num_textures"]):
            self.textures[f"t{i}"] = Texture2D(w, h, R8G8B8A8_UNORM)

        # Constant buffers for each pass (first run)
        cb_size = struct.calcsize("IIIIffff")
        self.cbs = []
        for i in range(self.cfg["passes"]):
            cb = Buffer(cb_size, HEAP_UPLOAD)
            if i < self.cfg["passes"] - 1:
                cb.upload(_pack_cb(w, h, w, h))
            else:
                cb.upload(_pack_cb(w, h, w * 2, h * 2))
            self.cbs.append(cb)

        # Samplers (same for both runs)
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

        # For double upscale, we'll need additional pipelines for the second run.
        self.pipelines_first = None  # will hold pipelines for first run
        self.pipelines_second = None  # for second run (if double)

    def _create_pipelines(
        self,
        target_input=None,
        target_output=None,
        target_textures=None,
        target_cbs=None,
        target_width=None,
        target_height=None,
    ):
        """
        Helper to create pipelines with specific resource bindings.
        If not provided, uses default self.input, self.output, self.textures, self.cbs.
        """
        if target_input is None:
            target_input = self.input
        if target_output is None:
            target_output = self.output
        if target_textures is None:
            target_textures = self.textures
        if target_cbs is None:
            target_cbs = self.cbs
        # For dispatch group calculation we need the current input dimensions
        in_w = target_width if target_width is not None else self.width
        in_h = target_height if target_height is not None else self.height

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
        return pipelines, in_w, in_h

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
        if not self.double_upscale:
            # Single 2x upscale
            pipelines, in_w, in_h = self._create_pipelines()  # uses defaults
            w, h = in_w, in_h
            for i, pipe in enumerate(pipelines):
                if i < self.cfg["passes"] - 1:
                    pipe.dispatch((w + 7) // 8, (h + 7) // 8, 1)
                else:
                    pipe.dispatch((w * 2 + 15) // 16, (h * 2 + 15) // 16, 1)
        else:
            # First run: input (w, h) -> intermediate (2w, 2h)
            # Create pipelines for first run with intermediate as output
            # We need a temporary output texture (intermediate) and constant buffers for first run
            # Also need temporary textures (at w,h) for the model's internal passes
            first_textures = {}
            for i in range(self.cfg["num_textures"]):
                first_textures[f"t{i}"] = Texture2D(
                    self.width, self.height, R8G8B8A8_UNORM
                )

            first_cbs = []
            for i in range(self.cfg["passes"]):
                cb = Buffer(struct.calcsize("IIIIffff"), HEAP_UPLOAD)
                if i < self.cfg["passes"] - 1:
                    cb.upload(
                        _pack_cb(self.width, self.height, self.width, self.height)
                    )
                else:
                    cb.upload(
                        _pack_cb(
                            self.width, self.height, self.width * 2, self.height * 2
                        )
                    )
                first_cbs.append(cb)

            pipelines_first, in_w, in_h = self._create_pipelines(
                target_input=self.input,
                target_output=self.intermediate,
                target_textures=first_textures,
                target_cbs=first_cbs,
                target_width=self.width,
                target_height=self.height,
            )

            w, h = in_w, in_h
            for i, pipe in enumerate(pipelines_first):
                if i < self.cfg["passes"] - 1:
                    pipe.dispatch((w + 7) // 8, (h + 7) // 8, 1)
                else:
                    pipe.dispatch((w * 2 + 15) // 16, (h * 2 + 15) // 16, 1)

            # Second run: intermediate (2w,2h) -> final output (4w,4h)
            # Now create pipelines for second run with intermediate as input, final as output
            # Textures for internal passes need to be at 2w,2h size
            second_textures = {}
            for i in range(self.cfg["num_textures"]):
                second_textures[f"t{i}"] = Texture2D(
                    self.width * 2, self.height * 2, R8G8B8A8_UNORM
                )

            second_cbs = []
            new_w = self.width * 2
            new_h = self.height * 2
            for i in range(self.cfg["passes"]):
                cb = Buffer(struct.calcsize("IIIIffff"), HEAP_UPLOAD)
                if i < self.cfg["passes"] - 1:
                    cb.upload(_pack_cb(new_w, new_h, new_w, new_h))
                else:
                    cb.upload(_pack_cb(new_w, new_h, new_w * 2, new_h * 2))
                second_cbs.append(cb)

            pipelines_second, in_w2, in_h2 = self._create_pipelines(
                target_input=self.intermediate,
                target_output=self.output,
                target_textures=second_textures,
                target_cbs=second_cbs,
                target_width=new_w,
                target_height=new_h,
            )

            w2, h2 = in_w2, in_h2
            for i, pipe in enumerate(pipelines_second):
                if i < self.cfg["passes"] - 1:
                    pipe.dispatch((w2 + 7) // 8, (h2 + 7) // 8, 1)
                else:
                    pipe.dispatch((w2 * 2 + 15) // 16, (h2 * 2 + 15) // 16, 1)

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
        # Source is self.output, which after compute will be either 2x or 4x depending on double_upscale
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
