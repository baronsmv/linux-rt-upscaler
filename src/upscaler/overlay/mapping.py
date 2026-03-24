from typing import List, Tuple


class CoordinateMapper:
    """
    Maps overlay screen coordinates to target window coordinates.

    The mapper uses:
        - scaling_rect: rectangle (x, y, width, height) in overlay coordinates
          where the upscaled content is drawn.
        - content_width, content_height: logical size of the content before scaling.
        - crop_*: region of the target window that corresponds to the content.
        - client_width, client_height: actual dimensions of the target window.

    The mapping process:
        1. Check if the point falls inside scaling_rect.
        2. Compute normalized coordinates (0..1) within scaling_rect.
        3. Map normalized coordinates to content coordinates.
        4. Apply crop transformation to get target window coordinates.
        5. Clamp to client bounds.
    """

    def __init__(self) -> None:
        """Initialize with default (invalid) values."""
        # Scaling rectangle (x, y, width, height) in overlay screen coordinates
        self.scaling_rect: List[int] = [0, 0, 0, 0]

        # Logical content dimensions (before scaling)
        self.content_width: int = 0
        self.content_height: int = 0

        # Crop region within the target window (left, top, width, height)
        self.crop_left: int = 0
        self.crop_top: int = 0
        self.crop_width: int = 0
        self.crop_height: int = 0

        # Actual target window size (for clamping)
        self.client_width: int = 0
        self.client_height: int = 0

    def set_scaling_rect(self, rect: List[int]) -> None:
        """Update the rectangle where the content is drawn on the overlay."""
        if len(rect) != 4:
            raise ValueError(f"Expected 4 integers, got {rect}")
        self.scaling_rect = rect

    def set_content_dimensions(self, width: int, height: int) -> None:
        """Update the logical content size."""
        self.content_width = width
        self.content_height = height

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """Update the crop region (the part of the target window that is shown)."""
        self.crop_left = left
        self.crop_top = top
        self.crop_width = width
        self.crop_height = height

    def set_target_size(self, width: int, height: int) -> None:
        """Update the actual target window size (for clamping)."""
        self.client_width = width
        self.client_height = height

    def map(self, screen_x: int, screen_y: int) -> Tuple[int, int, bool]:
        """
        Transform overlay screen coordinates to target window coordinates.

        Args:
            screen_x, screen_y: Coordinates relative to the overlay window.

        Returns:
            A tuple (target_x, target_y, inside) where `inside` is True if the
            point lies inside the scaling rectangle, otherwise False.
        """
        # 1. Check if inside scaling rect
        rx, ry, rw, rh = self.scaling_rect
        if rw == 0 or rh == 0:
            # No valid scaling rect – cannot map
            return 0, 0, False

        if not (rx <= screen_x < rx + rw and ry <= screen_y < ry + rh):
            return 0, 0, False

        # 2. Normalize within scaling rect
        norm_x = (screen_x - rx) / rw
        norm_y = (screen_y - ry) / rh

        # 3. Map to content coordinates
        content_x = int(norm_x * self.content_width)
        content_y = int(norm_y * self.content_height)

        # Clamp to content bounds
        content_x = max(0, min(content_x, self.content_width - 1))
        content_y = max(0, min(content_y, self.content_height - 1))

        # 4. Apply crop transformation to get target coordinates
        target_x = self.crop_left + int(
            content_x * self.crop_width / self.content_width
        )
        target_y = self.crop_top + int(
            content_y * self.crop_height / self.content_height
        )

        # 5. Clamp to target window bounds
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))

        return target_x, target_y, True
