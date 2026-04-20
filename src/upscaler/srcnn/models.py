from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class ModelConfig:
    """
    Configuration for a compute‑shader based upscaling model.

    This contains all information needed to create pipelines and bind resources,
    independent of the model's origin (CuNNy, FSRS, etc.).
    """

    # Number of compute passes
    passes: int

    # Number of intermediate textures (T0, T1, ...) needed
    num_textures: int

    # For each pass: a tuple (srv_names, uav_names)
    # Example: (["input", "t0"], ["t1", "t2"])
    srv_uav: List[Tuple[List[str], List[str]]]

    # For each pass: list of sampler types used (e.g., ["point", "linear"])
    samplers: List[List[str]]

    # SPIR‑V bytecode for each pass (in order)
    shaders: List[bytes]

    # Entry point name for all shaders (usually "main")
    entry_point: str = "main"

    # Push constant size in bytes (0 if not used)
    push_constant_size: int = 0

    # Optional: names of textures that should be treated as output (for final stage)
    output_names: Optional[List[str]] = None
