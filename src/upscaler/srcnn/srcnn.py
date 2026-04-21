import logging
from typing import Dict, List, Tuple

from .factory import PipelineFactory
from ..vulkan import Compute, Texture2D

logger = logging.getLogger(__name__)


def dispatch_groups(
    width: int, height: int, last_pass: bool = False
) -> Tuple[int, int]:
    """Calculate compute dispatch groups for a given pass."""
    if last_pass:
        # 16 output pixels per workgroup (8×8 threads × 2×2 pixels each)
        return (width + 15) // 16, (height + 15) // 16
    else:
        # 8 output pixels per workgroup (8×8 threads × 1×1 pixel each)
        return (width + 7) // 8, (height + 7) // 8


class SRCNN:
    """
    Low-level compute pipeline executor for a single upscaling stage (2x).

    This class uses a shared `PipelineFactory` to obtain Vulkan pipelines
    and constant buffers. It provides a simple `dispatch` interface.

    For multi-stage upscaling (e.g., 4x), create multiple SRCNN instances
    with the same factory, chaining their output textures.
    """

    def __init__(
        self,
        factory: PipelineFactory,
        width: int,
        height: int,
        input_texture: Texture2D,
        output_textures: Dict[str, Texture2D],
        push_constant_size: int = 0,
    ):
        """
        Initialize a single upscaling stage.

        Args:
            factory: PipelineFactory that provides cached pipelines.
            width: Logical width of the input.
            height: Logical height of the input.
            input_texture: Texture2D (or array) to use as INPUT.
            output_textures: Dict mapping texture name to pre-created Texture2D.
            push_constant_size: Size of push constant block (bytes).
        """
        self.factory = factory
        self.width = width
        self.height = height
        self.input = input_texture
        self.outputs = output_textures
        self.push_constant_size = push_constant_size

        # Obtain pipelines and constant buffers from factory
        self.pipelines, self.cbs = factory.create_stage(
            width, height, input_texture, output_textures, push_constant_size
        )

        logger.debug(
            f"SRCNN stage created: {width}x{height}, passes={len(self.pipelines)}"
        )

    def dispatch(
        self,
        groups_x: int,
        groups_y: int,
        groups_z: int = 1,
        push_data: bytes = b"",
    ) -> None:
        """Execute all passes with the given workgroup counts."""
        if not self.pipelines:
            raise RuntimeError("No pipelines available")

        for pipe in self.pipelines:
            pipe.dispatch(groups_x, groups_y, groups_z, push=push_data)

    def dispatch_sequence(
        self,
        sequence: List[Tuple[Compute, int, int, int, bytes]],
        **kwargs,
    ):
        """Execute a sequence of dispatches using the first pipeline."""
        if not self.pipelines:
            raise RuntimeError("No pipelines available")
        return self.pipelines[0].dispatch_sequence(sequence=sequence, **kwargs)
