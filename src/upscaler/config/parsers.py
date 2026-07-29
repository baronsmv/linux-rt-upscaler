import logging
import re
from typing import Callable, Dict, Union

from .models import Config
from ..utils import color_string_to_float4, color_tuple_to_string

logger = logging.getLogger(__name__)


def parse_config(config: Config) -> None:
    config.background_color = color_string_to_float4(config.background_color)


def parse_profile_colors(profiles: Dict) -> Dict:
    """Return a copy of *profiles* with any color converted to a hex string."""
    cleaned = {}
    for name, profile in profiles.items():
        profile_copy = dict(profile)
        options = profile_copy.get("options", {})
        if "background_color" in options:
            bg = options["background_color"]
            if isinstance(bg, tuple):
                options["background_color"] = color_tuple_to_string(bg)
        cleaned[name] = profile_copy
    return cleaned


def parse_interval(interval: Union[str, int, float]) -> Callable:
    """
    Returns a function that checks if a number satisfies the interval string.

    Supported patterns:
        "480"         ->  n == 400
        "<480"        ->  n < 480
        ">480"        ->  n > 480
        "<=480"       ->  n <= 480
        ">=480"       ->  n >= 480
        "480<"        ->  480 < n  (same as n > 480)
        "480>"        ->  480 > n  (same as n < 480)
        "720-1080"    ->  720 <= n <= 1080
        "720..1080"   ->  720 <= n <= 1080
        "720,1080"    ->  720 <= n <= 1080
        "  < 480  "   ->  n < 480   (spaces ignored)
        "480 < = "    ->  ValueError (malformed)
    """
    # Already a number: treat as exact equality
    if isinstance(interval, (int, float)):
        return lambda n: n == interval
    try:
        num = float(interval)
        return lambda n: n == num
    except ValueError:
        pass

    # Normalize: remove all whitespace
    s = re.sub(r"\s+", "", interval)

    # Pattern for a range: number - number  (or .. or ,)
    range_match = re.fullmatch(r"([+-]?\d*\.?\d+)\s*[-.,]\s*([+-]?\d*\.?\d+)", s)
    if range_match:
        low = float(range_match.group(1))
        high = float(range_match.group(2))
        if low > high:
            low, high = high, low
        return lambda n: low <= n <= high

    # Pattern for an operator followed by a number (normal order: op num)
    op_num = re.fullmatch(r"(<=?|>=?)([+-]?\d*\.?\d+)", s)
    if op_num:
        op = op_num.group(1)
        num = float(op_num.group(2))
        if op == "<":
            return lambda n: n < num
        elif op == "<=":
            return lambda n: n <= num
        elif op == ">":
            return lambda n: n > num
        elif op == ">=":
            return lambda n: n >= num

    # Pattern for a number followed by an operator (reversed order: num op)
    num_op = re.fullmatch(r"([+-]?\d*\.?\d+)(<=?|>=?)", s)
    if num_op:
        num = float(num_op.group(1))
        op = num_op.group(2)
        # "480<" means 480 < n  =>  n > 480
        if op == "<":
            return lambda n: n > num
        elif op == "<=":
            return lambda n: n >= num
        elif op == ">":
            return lambda n: n < num
        elif op == ">=":
            return lambda n: n <= num

    raise ValueError(f"Unrecognised interval format: {interval}")
