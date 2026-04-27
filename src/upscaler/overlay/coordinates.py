from typing import List, Tuple


class CoordinateMapper:
    """
    Maps overlay screen coordinates to target window coordinates.

    The mapper uses:
        - scaling_rect: rectangle (x, y, width, height) in overlay coordinates
          where the upscaled content is drawn.
        - content_width, content_height: logical size of the content before scaling.
        - crop_left, crop_top, crop_width, crop_height: region of the target window
          that corresponds to the content (after cropping).
        - client_width, client_height: actual dimensions of the target window.

    The mapping process:
        1. Check if the point falls inside scaling_rect.
        2. Compute normalized coordinates (0..1) within scaling_rect.
        3. Map normalized coordinates to content coordinates.
        4. Apply crop transformation to get target window coordinates.
        5. Clamp to client bounds.

    All dimensions are in pixels. The mapper is designed to be updated whenever
    the overlay geometry, content size, or target window changes.
    """

    def __init__(self) -> None:
        """Initialize with default (invalid) values. All dimensions must be set later."""
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
        """
        Update the rectangle where the content is drawn on the overlay.

        Args:
            rect: A list of four integers [x, y, width, height] in overlay coordinates.

        Raises:
            ValueError: If the list does not contain exactly four integers.
        """
        if len(rect) != 4:
            raise ValueError(f"Expected 4 integers, got {rect}")
        self.scaling_rect = rect

    def set_content_dimensions(self, width: int, height: int) -> None:
        """
        Update the logical content size (before any scaling).

        Args:
            width: Content width in pixels.
            height: Content height in pixels.
        """
        self.content_width = width
        self.content_height = height

    def set_crop(self, left: int, top: int, width: int, height: int) -> None:
        """
        Update the crop region of the target window that is shown.

        The crop region defines which part of the target window corresponds to
        the logical content. Typically, cropping removes window decorations or
        unwanted borders.

        Args:
            left: X offset from target window origin to start of content.
            top: Y offset from target window origin to start of content.
            width: Width of the cropped content region.
            height: Height of the cropped content region.
        """
        self.crop_left = left
        self.crop_top = top
        self.crop_width = width
        self.crop_height = height

    def set_target_size(self, width: int, height: int) -> None:
        """
        Update the actual target window dimensions (for clamping).

        Args:
            width: Full width of the target window in pixels.
            height: Full height of the target window in pixels.
        """
        self.client_width = width
        self.client_height = height

    def map(self, screen_x: int, screen_y: int) -> Tuple[int, int, bool]:
        """
        Transform overlay screen coordinates to target window coordinates.

        Args:
            screen_x, screen_y: Coordinates relative to the overlay window.

        Returns:
            A tuple (target_x, target_y, inside) where:
                - target_x, target_y are the corresponding coordinates in the target window
                  (clamped to the target window bounds).
                - inside is True if the point lies inside the scaling rectangle,
                  otherwise False (and target_x, target_y are set to 0).

        Notes:
            If any needed dimension (scaling_rect, content size, crop region) is zero,
            the method returns (0, 0, False) to avoid division by zero.
        """
        # Validate that we have meaningful dimensions
        rx, ry, rw, rh = self.scaling_rect
        if rw == 0 or rh == 0:
            return 0, 0, False

        if self.content_width == 0 or self.content_height == 0:
            return 0, 0, False

        if self.crop_width == 0 or self.crop_height == 0:
            return 0, 0, False

        # Check if the point is inside the scaling rectangle
        if not (rx <= screen_x < rx + rw and ry <= screen_y < ry + rh):
            return 0, 0, False

        # Normalize within scaling rect (0..1)
        norm_x = (screen_x - rx) / rw
        norm_y = (screen_y - ry) / rh

        # Map to content coordinates
        content_x = int(norm_x * self.content_width)
        content_y = int(norm_y * self.content_height)

        # Clamp to content bounds (should not be necessary, but safe)
        content_x = max(0, min(content_x, self.content_width - 1))
        content_y = max(0, min(content_y, self.content_height - 1))

        # Apply crop transformation to get target window coordinates
        target_x = self.crop_left + int(
            content_x * self.crop_width / self.content_width
        )
        target_y = self.crop_top + int(
            content_y * self.crop_height / self.content_height
        )

        # Clamp to target window bounds
        target_x = max(0, min(target_x, self.client_width - 1))
        target_y = max(0, min(target_y, self.client_height - 1))

        return target_x, target_y, True
