import logging
import os

from ..shader import ShaderPass
from ...vulkan import Texture2D

logger = logging.getLogger(__name__)


class DelinearizePass(ShaderPass):
    """Converts a linear-light texture back to sRGB space."""

    def __init__(self, shader_path: str = None) -> None:
        if shader_path is None:
            shader_path = os.path.join(os.path.dirname(__file__), "delinearize.spv")
        self.source_texture: Texture2D | None = None
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return 0

    def _create_persistent_resources(self) -> None:
        self._cb = None
        self._sampler = None

    def _get_bindings(self):
        return [self.source_texture], [self.target_texture], []

    def _rebuild_compute(self) -> None:
        if self.target_texture is None or self.source_texture is None:
            return
        super()._rebuild_compute()

    def set_source_texture(self, tex: Texture2D) -> None:
        if tex is self.source_texture:
            return
        self.source_texture = tex
        self._rebuild_compute()

    def update_constants(self, **kwargs) -> None:
        pass
