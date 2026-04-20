import json
import os

from ..models import ModelConfig


def load_cunny_model(model_name: str, variant: str = "") -> ModelConfig:
    """
    Load a CuNNy model and return a ModelConfig.

    Args:
        model_name: Name of the subdirectory under `shaders/CuNNy/`.
        variant: Shader variant suffix (e.g., "", "_tile", "_offset").

    Returns:
        ModelConfig populated with shaders and binding information.
    """
    model_dir = os.path.join(os.path.dirname(__file__), model_name)
    if not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    # Load model.json
    config_path = os.path.join(model_dir, "model.json")
    with open(config_path, "r") as f:
        cfg = json.load(f)

    # Load SPIR‑V shaders
    shaders = []
    for i in range(cfg["passes"]):
        spv_path = os.path.join(model_dir, f"Pass{i+1}{variant}.spv")
        if not os.path.exists(spv_path):
            raise FileNotFoundError(f"Shader not found: {spv_path}")
        with open(spv_path, "rb") as f:
            shaders.append(f.read())

    # Convert srv_uav from model.json format to our expected format
    srv_uav = []
    for srv_list, uav_list in cfg["srv_uav"]:
        srv_uav.append((srv_list, uav_list))

    return ModelConfig(
        passes=cfg["passes"],
        num_textures=cfg["num_textures"],
        srv_uav=srv_uav,
        samplers=cfg["samplers"],
        shaders=shaders,
        entry_point="main",
        push_constant_size=0,  # will be overridden by caller if needed
        output_names=["output"],  # default
    )
