import json
import os
from typing import List, Tuple

from ..models import ModelConfig


def load_cunny_model(model_name: str, variant: str = "") -> ModelConfig:
    """
    Load a CuNNy model and return a ModelConfig.

    CuNNy models are stored in subdirectories under `srcnn/cunny/`. Each
    directory contains a `model.json` file and pre‑compiled SPIR‑V shaders
    named `PassN.spv` (or `PassN_tile.spv`, `PassN_offset.spv` for variants).

    Args:
        model_name: Name of the subdirectory (e.g., "fast", "4x12").
        variant: Shader variant suffix (e.g., "", "_tile", "_offset").

    Returns:
        ModelConfig populated with shaders and binding information.

    Raises:
        FileNotFoundError: If the model directory or required SPIR‑V files are missing.
        json.JSONDecodeError: If model.json is malformed.
    """
    # Locate the model directory
    model_dir = os.path.join(os.path.dirname(__file__), model_name)
    if not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    # Load model.json
    config_path = os.path.join(model_dir, "model.json")
    with open(config_path, "r") as f:
        cfg = json.load(f)

    # Validate required fields
    required = ["passes", "num_textures", "srv_uav", "samplers"]
    for key in required:
        if key not in cfg:
            raise ValueError(f"Missing required field '{key}' in model.json")

    # Load SPIR‑V shaders
    shaders = []
    for i in range(cfg["passes"]):
        spv_path = os.path.join(model_dir, f"Pass{i+1}{variant}.spv")
        if not os.path.exists(spv_path):
            raise FileNotFoundError(f"Shader not found: {spv_path}")
        with open(spv_path, "rb") as f:
            shaders.append(f.read())

    # Convert srv_uav from model.json format to our expected format.
    # model.json uses lists of strings, already matching our tuple.
    srv_uav: List[Tuple[List[str], List[str]]] = []
    for item in cfg["srv_uav"]:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError("srv_uav must be a list of [srv_list, uav_list] pairs")
        srv_uav.append((item[0], item[1]))

    # Determine output names. By default, any UAV named "output" is the final output.
    output_names = ["output"]  # CuNNy convention

    return ModelConfig(
        passes=cfg["passes"],
        num_textures=cfg["num_textures"],
        srv_uav=srv_uav,
        samplers=cfg["samplers"],
        shaders=shaders,
        entry_point="main",
        push_constant_size=0,  # Will be set by caller if needed
        output_names=output_names,
    )
