from abc import abstractmethod
from typing import Optional

from ..shader import Shader
from ...vulkan import Texture2D


class Scaler(Shader):
    """Common ground for all scaling passes."""

    def __init__(self, shader_path: str) -> None:
        self.source_texture: Optional[Texture2D] = None
        super().__init__(shader_path)

    # ------------------------------------------------------------------
    #  Mandatory implementations
    # ------------------------------------------------------------------
    @staticmethod
    @abstractmethod
    def _cb_size() -> int:
        """Size of the constant buffer in bytes (0 if none)."""
        ...

    # ------------------------------------------------------------------
    #  Source texture management (DRY)
    # ------------------------------------------------------------------
    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()
