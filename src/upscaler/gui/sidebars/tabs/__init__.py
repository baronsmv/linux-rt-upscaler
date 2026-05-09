"""Sidebar tabs public module."""

from .capture import CaptureTab
from .display import DisplayTab
from .effects import EffectsTab
from .general import GeneralTab
from .osd import OSDTab
from .performance import PerformanceTab
from .scaler import ScalerTab
from .screenshots import ScreenshotsTab
from .tiles import TilesTab

__all__ = [
    "CaptureTab",
    "DisplayTab",
    "EffectsTab",
    "GeneralTab",
    "OSDTab",
    "PerformanceTab",
    "ScalerTab",
    "ScreenshotsTab",
    "TilesTab",
]
