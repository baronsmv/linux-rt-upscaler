from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QSize


def is_relative_output_geometry(spec: str) -> bool:
    """Return True if the spec is relative to the screen."""
    if spec in ("fit", "stretch", "cover"):
        return True
    return spec.endswith("%") or spec.endswith("%!")


def is_valid_overlay_size(size: QSize) -> bool:
    """Min-max checks before trusting a saved size."""
    if size.width() < 320 or size.height() < 240:
        return False
    if size.width() > 16384 or size.height() > 16384:
        return False
    return True
