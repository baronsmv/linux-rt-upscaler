import logging
import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Tuple, List

from PIL import Image, ImageDraw, ImageFont

from ..shaders import OverlayBlender
from ..vulkan import Buffer, Compute, Texture2D

logger = logging.getLogger(__name__)


class TextRenderer:
    """
    Renders text to PIL images with a consistent style (white text, shadow, rounded background).
    Images are cached to avoid repeated rendering.
    """

    def __init__(
        self,
        texts: List[str],
        screen_height: int = 1080,
        font_path: Optional[str] = None,
    ) -> None:
        self.font_size = max(24, int(screen_height * 0.04))
        try:
            self.font = ImageFont.truetype(
                font_path or "DejaVuSans.ttf", self.font_size
            )
        except Exception:
            self.font = ImageFont.load_default()
        self._image_cache: Dict[str, Image.Image] = {}
        for text in texts:
            self._render_to_cache(text)

    def _render_to_cache(self, text: str) -> None:
        """Render a single text string to a PIL image and store in cache."""
        if text in self._image_cache:
            return

        # Colors and style
        text_color = (255, 255, 255, 255)
        shadow_color = (0, 0, 0, 180)
        bg_color = (0, 0, 0, 180)

        # Measure text
        dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(dummy_img)
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Add padding and shadow offset
        padding = int(self.font_size * 0.5)
        shadow_offset = max(2, int(self.font_size * 0.05))
        img_w = text_w + 2 * padding + shadow_offset
        img_h = text_h + 2 * padding + shadow_offset

        # Create image with background
        img = Image.new("RGBA", (int(img_w), int(img_h)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded rectangle background
        draw.rounded_rectangle((0, 0, img_w, img_h), radius=padding, fill=bg_color)

        # Draw shadow (offset)
        draw.text(
            (padding + shadow_offset, padding + shadow_offset),
            text,
            font=self.font,
            fill=shadow_color,
        )
        # Draw main text
        draw.text((padding, padding), text, font=self.font, fill=text_color)

        self._image_cache[text] = img

    def get_image(self, text: str) -> Optional[Image.Image]:
        """Return the cached PIL image for the given text, or None if not found."""
        return self._image_cache.get(text)


class OSDManager:
    """
    Manages on‑screen display messages.

    Texts are pre‑rendered on the CPU in a background thread, then uploaded to
    GPU textures on the pipeline thread. Active messages expire after a duration.
    Thread‑safe for showing messages from any thread.
    """

    def __init__(
        self,
        texts: Tuple[str, ...],
        screen_width: int,
        screen_height: int,
        blender: Optional[OverlayBlender] = None,
    ) -> None:
        """
        Initialize the OSD manager.

        Args:
            texts: All possible OSD message strings (pre‑rendered in background).
            screen_width, screen_height: Dimensions of the screen (for centering).
            blender: Optional OverlayBlender instance. If None, a default one is created.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height

        # CPU rendering in background
        self._images: Dict[str, Image.Image] = {}
        self._images_ready = threading.Event()
        self._render_executor = ThreadPoolExecutor(max_workers=1)
        self._render_future = self._render_executor.submit(self._render_all, texts)

        # GPU resources (populated on pipeline thread)
        self._texture_cache: Dict[str, Texture2D] = {}
        self._blender = blender or OverlayBlender()
        self._compute_cache: Dict[Texture2D, Compute] = {}

        # Active message state (protected by lock)
        self._lock = threading.Lock()
        self._active_text: Optional[str] = None
        self._active_texture: Optional[Texture2D] = None
        self._expiry_time: float = 0.0
        self._needs_redraw = False

    # ----------------------------------------------------------------------
    # Background CPU rendering
    # ----------------------------------------------------------------------
    def _render_all(self, texts: Tuple[str, ...]) -> None:
        """Render all texts to PIL images (runs in background thread)."""
        renderer = TextRenderer(list(texts), screen_height=self._screen_height)
        for text in texts:
            img = renderer.get_image(text)
            if img:
                self._images[text] = img
        self._images_ready.set()
        logger.debug(f"OSD CPU rendering complete: {len(self._images)} images")

    # ----------------------------------------------------------------------
    # GPU texture preparation (must be called from pipeline thread)
    # ----------------------------------------------------------------------
    def prepare_textures(self) -> None:
        """
        Upload all pre‑rendered images to GPU textures.

        Must be called from the pipeline thread after Vulkan device is ready.
        Blocks until background rendering is complete.
        """
        self._images_ready.wait()
        for text, img in self._images.items():
            if text not in self._texture_cache:
                logger.debug(f"Uploading OSD texture for '{text}'")
                try:
                    self._texture_cache[text] = self._upload_image_to_texture(img)
                except Exception as e:
                    logger.error(f"Failed to upload OSD texture '{text}': {e}")
        logger.debug("All OSD textures uploaded to GPU")

    @staticmethod
    def _upload_image_to_texture(image: Image.Image) -> Texture2D:
        """
        Upload a PIL image to a new GPU texture.

        Args:
            image: PIL Image in RGBA mode.

        Returns:
            A Texture2D containing the image data.
        """
        tex = Texture2D(image.width, image.height)
        buffer_size = image.width * image.height * 4
        upload_buffer = Buffer(buffer_size)
        upload_buffer.upload(image.tobytes())
        upload_buffer.copy_to(tex)
        return tex

    # ----------------------------------------------------------------------
    # State update (called each frame)
    # ----------------------------------------------------------------------
    def update(self) -> Tuple[Optional[Texture2D], bool]:
        """
        Update internal state (expiry) and return the texture to draw.

        Returns:
            A tuple (active_texture, needs_redraw).
            - active_texture: The texture to blend, or None if no active message.
            - needs_redraw: True if the OSD content changed this frame.
        """
        with self._lock:
            # Check expiry
            now = time.monotonic()
            if self._expiry_time > 0 and now >= self._expiry_time:
                self._active_text = None
                self._active_texture = None
                self._expiry_time = 0.0

            # Lazy texture resolution
            if self._active_text is not None and self._active_texture is None:
                self._active_texture = self._texture_cache.get(self._active_text)
                if self._active_texture is None:
                    # Should not happen if prepare_textures was called
                    logger.error(f"OSD texture not found for '{self._active_text}'")

            texture = self._active_texture
            needs_redraw = self._needs_redraw
            self._needs_redraw = False

        return texture, needs_redraw

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------
    def show(self, text: str, duration: float = 1.5) -> None:
        """
        Request an OSD message to be displayed (thread‑safe).

        Args:
            text: The message to show (must be one of the pre‑rendered strings).
            duration: How long to display the message in seconds.
        """
        with self._lock:
            self._active_text = text
            self._active_texture = None  # Resolved in update()
            self._expiry_time = time.monotonic() + duration
            self._needs_redraw = True

    def get_blend_params(self) -> Tuple[int, int, int, int]:
        """
        Calculate position and size for centering the active OSD texture.

        Returns:
            A tuple (x, y, width, height) for blending.
            If no active texture, returns zeros.
        """
        tex = self._active_texture
        if tex is None:
            return 0, 0, 0, 0
        w, h = tex.width, tex.height
        x = (self._screen_width - w) // 2
        y = (self._screen_height - h) // 2
        return x, y, w, h

    def blend_active(self, screen_tex: Texture2D) -> None:
        """
        Blend the active OSD texture onto the screen texture (if any).

        Args:
            screen_tex: The screen texture to blend onto.
        """
        tex = self._active_texture
        if tex is None:
            return
        x, y, w, h = self.get_blend_params()
        if w <= 0 or h <= 0:
            return

        # Update constants and blend
        cb_data = struct.pack("iiii", x, y, w, h)
        self._blender.cb.upload(cb_data)

        # Get or create compute pipeline
        if tex not in self._compute_cache:
            self._compute_cache[tex] = Compute(
                self._blender.shader,
                srv=[screen_tex, tex],
                uav=[screen_tex],
                cbv=[self._blender.cb],
                samplers=[self._blender.sampler],
                push_size=0,
            )
        compute = self._compute_cache[tex]

        groups_x = (w + 15) // 16
        groups_y = (h + 15) // 16
        compute.dispatch(groups_x, groups_y, 1)

    def clear_cache(self) -> None:
        """Clear cached compute pipelines (call on swapchain resize)."""
        self._compute_cache.clear()

    def shutdown(self) -> None:
        """Clean up background executor."""
        self._render_executor.shutdown(wait=False)
