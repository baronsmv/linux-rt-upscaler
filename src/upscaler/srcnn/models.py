from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ModelConfig:
    """
    Configuration for a compute‑shader based upscaling model.

    This contains all information needed to create pipelines and bind resources,
    independent of the model's origin (CuNNy, FSRS, etc.).

    Attributes:
        passes: Number of compute passes.
        num_textures: Number of intermediate textures (T0, T1, ...) needed.
        srv_uav: For each pass, a tuple (srv_names, uav_names).
        samplers: For each pass, list of sampler types used (e.g., ["point", "linear"]).
        shaders: SPIR‑V bytecode for each pass (in order).
        entry_point: Entry point name for all shaders (usually "main").
        push_constant_size: Size of push constant block in bytes (0 if not used).
        output_names: Names of textures that should be treated as final output.
    """

    passes: int
    num_textures: int
    srv_uav: List[Tuple[List[str], List[str]]]
    samplers: List[List[str]]
    shaders: List[bytes]
    entry_point: str = "main"
    push_constant_size: int = 0
    output_names: Optional[List[str]] = None
