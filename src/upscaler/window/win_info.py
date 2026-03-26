from dataclasses import dataclass
from typing import Tuple


@dataclass
class WindowInfo:
    """Immutable information about an X11 window."""

    handle: int
    width: int
    height: int
    title: str

    @property
    def size(self) -> Tuple[int, int]:
        return self.width, self.height
