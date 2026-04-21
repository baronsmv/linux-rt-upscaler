import logging
import struct
from typing import Dict, List, Tuple, Any

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


class PipelineFactory:
    """
    Factory that creates and caches Vulkan compute pipelines for SRCNN stages.

    The factory maintains shared resources (samplers, descriptor set layouts,
    and pipelines) based on a `ModelConfig`. This avoids duplicating Vulkan
    objects when multiple SRCNN instances use the same model configuration.

    Usage:
        factory = PipelineFactory(config)
        pipelines, cbs = factory.create_stage(
            width, height, input_texture, output_textures, push_size
        )
        # Use pipelines and cbs in SRCNN wrapper.

    TODO: Re-evaluate pipeline caching if performance becomes an issue:

    Previously, a `_pipeline_cache` was used to cache `Compute` objects keyed by
    (width, height, pass_idx, push_size). This caused stale descriptor sets when
    the underlying textures (e.g., output atlases or intermediate textures) were
    recreated (e.g., after crop resize, model switch, or tile cache resize).
    The cached `Compute` held descriptor sets referencing destroyed Vulkan images,
    resulting in silent write failures (black screen in tile modes).

    Removing the cache fixes the issue because `create_stage` is called only:
      - At upscaler initialization.
      - When the upscaler is recreated due to crop/window changes or model switch.

    These events are infrequent (user-initiated or window resizes), so the cost
    of pipeline creation (a few milliseconds) is acceptable. The `Compute` objects
    returned by `create_stage` are reused for all per‑frame dispatches.

    If in the future the architecture changes such that `create_stage` is called
    per frame or per tile, a proper caching mechanism with invalidation should be
    implemented. That would involve:
      - Storing the cache here.
      - Providing a `clear_pipeline_cache()` method.
      - Calling it whenever any texture bound to the pipelines is recreated.
    """

    def __init__(self, config: ModelConfig):
        """
        Initialize the factory with a model configuration.

        Args:
            config: ModelConfig containing shaders and binding information.
        """
        self.config = config

        # Shared samplers (created once)
        self._sampler_point = Sampler(
            filter_min=SAMPLER_FILTER_POINT,
            filter_mag=SAMPLER_FILTER_POINT,
        )
        self._sampler_linear = Sampler(
            filter_min=SAMPLER_FILTER_LINEAR,
            filter_mag=SAMPLER_FILTER_LINEAR,
        )

        # Cache for descriptor set layouts.
        # Key: (push_constant_size, bindless_flag, texture_type_tuple)
        self._dsl_cache: Dict[Tuple, Any] = {}

        # Cache for constant buffers (per pass and dimensions).
        # Key: (width, height, pass_index)
        self._cb_cache: Dict[Tuple, Buffer] = {}

    def _get_sampler(self, sampler_type: str) -> Sampler:
        """Return the appropriate shared sampler."""
        if sampler_type == "point":
            return self._sampler_point
        elif sampler_type == "linear":
            return self._sampler_linear
        else:
            raise ValueError(f"Unknown sampler type: {sampler_type}")

    def _create_or_get_constant_buffer(
        self, width: int, height: int, pass_index: int
    ) -> Buffer:
        """Return a constant buffer for a given pass and dimensions."""
        key = (width, height, pass_index)
        if key in self._cb_cache:
            return self._cb_cache[key]

        cb_size = struct.calcsize("IIIIffff")
        cb = Buffer(cb_size)

        # For intermediate passes, output dimensions equal input; final pass outputs 2x.
        if pass_index < self.config.passes - 1:
            out_w, out_h = width, height
        else:
            out_w, out_h = width * 2, height * 2

        cb.upload(_pack_cb(width, height, out_w, out_h))
        self._cb_cache[key] = cb
        return cb

    def create_stage(
        self,
        width: int,
        height: int,
        input_texture: Texture2D,
        output_textures: Dict[str, Texture2D],
        push_constant_size: int = 0,
    ) -> Tuple[List[Compute], List[Buffer]]:
        """
        Create pipelines and constant buffers for a single upscaling stage.

        Args:
            width: Logical width of the input.
            height: Logical height of the input.
            input_texture: Texture2D (or array) used as INPUT.
            output_textures: Dict mapping texture name to pre-created Texture2D.
            push_constant_size: Size of push constant block (bytes).

        Returns:
            Tuple (pipelines, constant_buffers) where pipelines is a list of
            Compute objects (one per pass) and constant_buffers is the list of
            corresponding constant buffers.
        """
        pipelines = []
        cbs = []

        for pass_idx in range(self.config.passes):
            # Get constant buffer (cached)
            cb = self._create_or_get_constant_buffer(width, height, pass_idx)
            cbs.append(cb)

            # Resolve SRV/UAV lists
            srv_names, uav_names = self.config.srv_uav[pass_idx]

            srv_list = []
            for name in srv_names:
                if name == "input":
                    srv_list.append(input_texture)
                else:
                    if name not in output_textures:
                        raise KeyError(f"SRV '{name}' not found in output_textures")
                    srv_list.append(output_textures[name])

            uav_list = []
            for name in uav_names:
                if name not in output_textures:
                    raise KeyError(f"UAV '{name}' not found in output_textures")
                uav_list.append(output_textures[name])

            # Samplers for this pass
            sampler_list = []
            for sampler_type in self.config.samplers[pass_idx]:
                sampler_list.append(self._get_sampler(sampler_type))

            # Create compute pipeline
            pipe = Compute(
                self.config.shaders[pass_idx],
                cbv=[cb],
                srv=srv_list,
                uav=uav_list,
                samplers=sampler_list,
                push_size=push_constant_size,
            )
            pipelines.append(pipe)

        return pipelines, cbs
