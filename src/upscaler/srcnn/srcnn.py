import logging
import struct
from typing import Dict, List, Tuple

from .models import ModelConfig
from ..vulkan import (
    Buffer,
    Compute,
    Sampler,
    Texture2D,
    SAMPLER_FILTER_LINEAR,
    SAMPLER_FILTER_POINT,
)

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
    Low‑level compute pipeline executor for an upscaling model.

    This class does not perform any upload or orchestration; it only creates
    Vulkan resources and pipelines based on a ModelConfig and provides a
    `dispatch` method to run all passes.

    It can be configured for full‑frame, tile‑atlas, or offset‑write variants
    by passing appropriately created input/output textures and setting
    `push_constant_size`.
    """

    def __init__(
        self,
        config: ModelConfig,
        width: int,
        height: int,
        input_texture: Texture2D,
        output_textures: Dict[str, Texture2D],
        push_constant_size: int = 0,
        double_upscale: bool = False,
    ):
        """
        Initialize the SRCNN pipeline.

        Args:
            config: ModelConfig describing passes, shaders, and bindings.
            width: Logical width of the input (crop width).
            height: Logical height of the input (crop height).
            input_texture: Texture2D (or Texture2DArray) to use as INPUT.
            output_textures: Dict mapping texture name (e.g., "t0", "output")
                to pre‑created Texture2D objects. Must include all UAVs used
                by the model.
            push_constant_size: Size of push constant block (bytes).
            double_upscale: If True, the model performs two 2x stages (4x total).
                This affects constant buffer dimensions.
        """
        self.config = config
        self.width = width
        self.height = height
        self.input = input_texture
        self.outputs = output_textures
        self.push_constant_size = push_constant_size
        self.double_upscale = double_upscale

        # Create samplers (point and linear)
        self.sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT, filter_mag=SAMPLER_FILTER_POINT
        )
        self.sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR, filter_mag=SAMPLER_FILTER_LINEAR
        )

        # Create constant buffers for each pass
        self.cbs = self._create_constant_buffers()

        # Build compute pipelines
        self.pipelines = self._build_pipelines()

        logger.debug(
            f"SRCNN initialized: {width}x{height}, passes={len(self.pipelines)}"
        )

    def _create_constant_buffers(self) -> List[Buffer]:
        """Create and upload constant buffers for all passes."""
        cbs = []
        cb_size = struct.calcsize("IIIIffff")

        in_w, in_h = self.width, self.height
        out_w, out_h = self.width * 2, self.height * 2  # default 2x

        for i in range(self.config.passes):
            cb = Buffer(cb_size)
            if i < self.config.passes - 1:
                cb.upload(_pack_cb(in_w, in_h, in_w, in_h))
            else:
                cb.upload(_pack_cb(in_w, in_h, out_w, out_h))
            cbs.append(cb)

        return cbs

    def _build_pipelines(self) -> List[Compute]:
        """Create compute pipelines for all passes."""
        pipelines = []

        for pass_idx, (srv_names, uav_names) in enumerate(self.config.srv_uav):
            # Collect SRV resources
            srv_list = []
            for name in srv_names:
                if name == "input":
                    srv_list.append(self.input)
                else:
                    srv_list.append(self.outputs[name])

            # Collect UAV resources
            uav_list = [self.outputs[name] for name in uav_names]

            # Collect samplers for this pass
            sampler_list = []
            for sampler_type in self.config.samplers[pass_idx]:
                if sampler_type == "point":
                    sampler_list.append(self.sampler_point)
                elif sampler_type == "linear":
                    sampler_list.append(self.sampler_linear)

            # Create pipeline
            pipe = Compute(
                self.config.shaders[pass_idx],
                cbv=[self.cbs[pass_idx]],
                srv=srv_list,
                uav=uav_list,
                samplers=sampler_list,
                push_size=self.push_constant_size,
            )
            pipelines.append(pipe)

        return pipelines

    def dispatch(
        self,
        groups_x: int,
        groups_y: int,
        groups_z: int = 1,
        push_data: bytes = b"",
    ) -> None:
        """
        Execute all passes with the given dispatch dimensions and push constants.

        Args:
            groups_x, groups_y, groups_z: Number of workgroups.
            push_data: Push constant data (must match configured size).
        """
        for pipe in self.pipelines:
            pipe.dispatch(groups_x, groups_y, groups_z, push=push_data)

    def dispatch_sequence(
        self,
        sequence: List[Tuple[Compute, int, int, int, bytes]],
        **kwargs,
    ):
        """
        Execute a sequence of dispatches with optional pre/post operations.

        This is a convenience wrapper around the first pipeline's
        `dispatch_sequence` method.
        """
        if not self.pipelines:
            raise RuntimeError("No pipelines available")
        # All pipelines share the same device; use the first one to submit.
        return self.pipelines[0].dispatch_sequence(sequence=sequence, **kwargs)
