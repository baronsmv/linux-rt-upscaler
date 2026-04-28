import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from .models import ModelConfig
from ..vulkan import (
    R8G8B8A8_UNORM,  # 28
    R16G16B16A16_FLOAT,  # 10
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Map model.json "depth" values to Vulkan format constants
# ---------------------------------------------------------------------------
_DEPTH_FORMAT_MAP: Dict[str, int] = {
    "rgba8": R8G8B8A8_UNORM,
    "rgba16": R16G16B16A16_FLOAT,
}

# ---------------------------------------------------------------------------
# Global cache - keyed by (model_path, variant)
# ---------------------------------------------------------------------------
_MODEL_CACHE: Dict[Tuple[str, str], ModelConfig] = {}


def load_model(
    model_name: str,
    variant: str = "",
    push_constant_size: int = 0,
) -> ModelConfig:
    """
    Load an upscaling model from a subdirectory of srcnn/.

    Parameters
    ----------
    model_name : str
        Path relative to the ``srcnn/`` directory, e.g. ``"fast"`` or
        ``"anime4k/upscale/x2"``.
    variant : str
        Shader variant suffix: ``""`` for full-frame, ``"_tile"`` for tile mode.
    push_constant_size : int
        Size of the push-constant block used by tile-mode shaders.

    Returns
    -------
    ModelConfig
        Configuration containing shader bytecode, binding layout, and
        the intermediate texture format.

    Raises
    ------
    FileNotFoundError
        If the model directory or required SPIR-V files are missing.
    ValueError
        If ``model.json`` is malformed.
    json.JSONDecodeError
        If the JSON is invalid.
    """
    cache_key = (model_name, variant)
    if cache_key in _MODEL_CACHE:
        logger.debug("Returning cached model config for %r (%r)", model_name, variant)
        return _MODEL_CACHE[cache_key]

    base_dir = Path(__file__).parent  # srcnn/
    model_dir = base_dir / model_name
    if not model_dir.is_dir():
        # Also try legacy CuNNy path (the name might just be "fast")
        legacy_dir = base_dir / "cunny" / model_name
        if legacy_dir.is_dir():
            model_dir = legacy_dir
        else:
            raise FileNotFoundError(
                f"Model directory not found: {model_dir} or {legacy_dir}"
            )

    config_path = model_dir / "model.json"
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)

    # ------------------------------------------------------------------
    # Basic validation
    # ------------------------------------------------------------------
    required_keys = ["passes", "num_textures", "srv_uav", "samplers"]
    missing = [k for k in required_keys if k not in cfg]
    if missing:
        raise ValueError(f"model.json missing required keys: {missing}")

    passes = cfg["passes"]
    num_textures = cfg["num_textures"]
    srv_uav_raw = cfg["srv_uav"]
    samplers_raw = cfg["samplers"]

    if not isinstance(srv_uav_raw, list) or len(srv_uav_raw) != passes:
        raise ValueError(f"srv_uav must be a list of length {passes}")
    if not isinstance(samplers_raw, list) or len(samplers_raw) != passes:
        raise ValueError(f"samplers must be a list of length {passes}")

    # ------------------------------------------------------------------
    # Intermediate texture format (default to rgba8)
    # ------------------------------------------------------------------
    depth_str = cfg.get("depth", "rgba8")
    if depth_str not in _DEPTH_FORMAT_MAP:
        raise ValueError(
            f"Unsupported depth format '{depth_str}'. "
            f"Must be one of {list(_DEPTH_FORMAT_MAP.keys())}"
        )
    intermediate_format = _DEPTH_FORMAT_MAP[depth_str]

    # ------------------------------------------------------------------
    # Load SPIR-V shaders
    # ------------------------------------------------------------------
    shaders: List[bytes] = []
    for pass_idx in range(1, passes + 1):
        spv_path = model_dir / f"Pass{pass_idx}{variant}.spv"
        if not spv_path.is_file():
            raise FileNotFoundError(f"Shader not found: {spv_path}")
        with spv_path.open("rb") as f:
            shaders.append(f.read())
        logger.debug("Loaded shader: %s", spv_path)

    srv_uav: List[Tuple[List[str], List[str]]] = [
        (entry[0], entry[1]) for entry in srv_uav_raw
    ]

    config = ModelConfig(
        passes=passes,
        num_textures=num_textures,
        srv_uav=srv_uav,
        samplers=samplers_raw,
        shaders=shaders,
        entry_point="main",
        push_constant_size=push_constant_size,
        output_names=["output"],
        intermediate_format=intermediate_format,
    )

    _MODEL_CACHE[cache_key] = config
    logger.info(
        "Loaded model %r (variant=%r, depth=%s) with %d passes",
        model_name,
        variant,
        depth_str,
        passes,
    )
    return config


def clear_model_cache() -> None:
    """Clear all cached model configurations."""
    _MODEL_CACHE.clear()
    logger.debug("Model cache cleared")
