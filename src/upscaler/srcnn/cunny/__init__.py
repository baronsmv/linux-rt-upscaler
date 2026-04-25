import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from ..models import ModelConfig

logger = logging.getLogger(__name__)

# Simple in-memory cache for loaded models to avoid repeated file reads
_MODEL_CACHE: Dict[Tuple[str, str], ModelConfig] = {}


def load_cunny_model(
    model_name: str, variant: str = "", push_constant_size: int = 0
) -> ModelConfig:
    """
    Load a CuNNy model configuration and SPIR-V shaders.

    CuNNy models are stored in subdirectories under `srcnn/cunny/`. Each
    directory contains:
        - `model.json` : Descriptor binding layout and number of passes/textures.
        - `PassN.spv`  : Full-frame shader binaries.
        - `PassN_tile.spv`   : Tile mode shader binaries.

    Args:
        model_name: Subdirectory name (e.g., "fast", "4x12").
        variant:    Shader variant suffix. Must be one of:
                        ""         for full-frame mode,
                        "_tile"    for tile mode.

    Returns:
        ModelConfig populated with shader bytecode and binding information.

    Raises:
        FileNotFoundError: If the model directory or a required SPIR-V file is missing.
        ValueError: If model.json is malformed or missing required fields.
        json.JSONDecodeError: If model.json is not valid JSON.
    """
    cache_key = (model_name, variant)
    if cache_key in _MODEL_CACHE:
        logger.debug(f"Returning cached model config for {model_name!r} ({variant!r})")
        return _MODEL_CACHE[cache_key]

    # Resolve model directory relative to this file
    base_dir = Path(__file__).parent
    model_dir = base_dir / model_name
    if not model_dir.is_dir():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    # Load model.json
    config_path = model_dir / "model.json"
    try:
        with config_path.open("r", encoding="utf-8") as f:
            cfg = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in {config_path}: {e.msg}", e.doc, e.pos
        ) from e

    # Validate required top-level keys
    required_keys = ["passes", "num_textures", "srv_uav", "samplers"]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise ValueError(f"model.json missing required keys: {missing}")

    passes = cfg["passes"]
    num_textures = cfg["num_textures"]
    srv_uav_raw = cfg["srv_uav"]
    samplers_raw = cfg["samplers"]

    # Basic validation of srv_uav structure
    if not isinstance(srv_uav_raw, list) or len(srv_uav_raw) != passes:
        raise ValueError(f"srv_uav must be a list of length {passes}")
    for i, entry in enumerate(srv_uav_raw):
        if not isinstance(entry, list) or len(entry) != 2:
            raise ValueError(f"srv_uav[{i}] must be a pair [srv_list, uav_list]")

    # Basic validation of samplers structure
    if not isinstance(samplers_raw, list) or len(samplers_raw) != passes:
        raise ValueError(f"samplers must be a list of length {passes}")

    # Load SPIR-V shader binaries
    shaders: List[bytes] = []
    for pass_idx in range(1, passes + 1):
        shader_path = model_dir / f"Pass{pass_idx}{variant}.spv"
        if not shader_path.is_file():
            raise FileNotFoundError(f"Shader not found: {shader_path}")
        with shader_path.open("rb") as f:
            shaders.append(f.read())
        logger.debug(f"Loaded shader: {shader_path}")

    # Convert srv_uav to the format expected by ModelConfig
    srv_uav: List[Tuple[List[str], List[str]]] = [
        (entry[0], entry[1]) for entry in srv_uav_raw
    ]

    # CuNNy convention: the final output is always named "output"
    output_names = ["output"]

    config = ModelConfig(
        passes=passes,
        num_textures=num_textures,
        srv_uav=srv_uav,
        samplers=samplers_raw,
        shaders=shaders,
        entry_point="main",
        push_constant_size=push_constant_size,
        output_names=output_names,
    )

    _MODEL_CACHE[cache_key] = config
    logger.info(
        f"Loaded model {model_name!r} (variant={variant!r}) with {passes} passes"
    )
    return config
