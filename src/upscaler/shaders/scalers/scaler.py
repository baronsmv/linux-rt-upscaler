from __future__ import annotations

from abc import abstractmethod
from typing import Optional, TYPE_CHECKING

from ..shader import Shader

if TYPE_CHECKING:
    from ...vulkan import Texture2D


class Scaler(Shader):
    """Common ground for all scaling passes."""

    requires_linear_input: bool = True
    linear_output: bool = True

    # Used by downsamplers
    blur: float = 1.0
    antiring_strength: float = 1.0
    tight_antiring: bool = True

    def __init__(self, shader_path: str) -> None:
        self.source_texture: Optional[Texture2D] = None
        super().__init__(shader_path)

    @staticmethod
    @abstractmethod
    def _cb_size() -> int:
        """Size of the constant buffer in bytes (0 if none)."""
        ...

    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    def configure(
        self,
        blur: float = 1.0,
        antiring_strength: float = 1.0,
        tight_antiring: bool = True,
        *_,
    ):
        """Set custom parameters."""
        self.blur = blur
        self.antiring_strength = antiring_strength
        self.tight_antiring = tight_antiring
