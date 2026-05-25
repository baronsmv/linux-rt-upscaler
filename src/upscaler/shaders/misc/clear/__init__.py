import logging
import os
import struct

from ...shader import Shader

logger = logging.getLogger(__name__)


class Clear(Shader):
    def __init__(self, shader_path=None):
        if shader_path is None:
            shader_path = os.path.join(os.path.dirname(__file__), "clear.spv")
        super().__init__(shader_path)

    @staticmethod
    def _cb_size() -> int:
        return 24

    def _get_bindings(self):
        return [], [self.target_texture], []

    def update_constants(self, color):
        w = self.target_texture.width
        h = self.target_texture.height
        data = struct.pack("<4f2I", *color, w, h)
        self._cb.upload(data)
