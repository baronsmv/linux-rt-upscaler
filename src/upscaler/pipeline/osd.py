import logging
import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from ..shaders import OverlayBlender
from ..vulkan import Buffer, Compute, Texture2D

logger = logging.getLogger(__name__)


def upload_image_to_texture(image: Image.Image) -> Texture2D:
    tex = Texture2D(image.width, image.height)
    buffer_size = image.width * image.height * 4
    upload_buffer = Buffer(buffer_size)
    upload_buffer.upload(image.tobytes())
    upload_buffer.copy_to(tex)
    return tex


class TextRenderer:
    """Renders text to PIL images; GPU upload is done separately."""

    def __init__(
        self,
        texts: list[str],
        screen_height: int = 1080,
        font_path: Optional[str] = None,
    ):
        # Font size scales with screen height (approx 4%)
        self.font_size = max(24, int(screen_height * 0.04))

        try:
            self.font = ImageFont.truetype(
                font_path or "DejaVuSans.ttf", self.font_size
            )
        except Exception:
            self.font = ImageFont.load_default()
        self._image_cache: Dict[str, Image.Image] = {}

        # Pre‑render all required texts (CPU only)
        for text in texts:
            self._render_to_cache(text)

    def _render_to_cache(self, text: str) -> None:
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
        return self._image_cache.get(text)


class OSDManager:
    """Manages OSD messages: CPU rendering, GPU texture caching, and display state."""

    def __init__(self, texts: Tuple[str, ...], screen_width: int, screen_height: int):
        self._screen_width = screen_width
        self._screen_height = screen_height

        # CPU image cache (rendered in background)
        self.images_ready = threading.Event()
        self._images: Dict[str, Image.Image] = {}
        self._render_executor = ThreadPoolExecutor(max_workers=1)
        self._render_future: Future = self._render_executor.submit(
            self._render_all, texts
        )

        # GPU texture cache (populated on pipeline thread)
        self._texture_cache: Dict[str, Texture2D] = {}
        self._compute_cache: Dict[Texture2D, Compute] = {}

        # Active OSD state (protected by lock)
        self._lock = threading.Lock()
        self._active_text: Optional[str] = None
        self._active_texture: Optional[Texture2D] = None
        self._expiry_time: Optional[float] = None
        self._needs_redraw = False

        self._blender = OverlayBlender()

    def _render_all(self, texts: Tuple[str, ...]) -> None:
        """Render all OSD texts to PIL images (runs in background thread)."""
        renderer = TextRenderer(list(texts), screen_height=self._screen_height)
        for text in texts:
            img = renderer.get_image(text)
            if img:
                self._images[text] = img
        self.images_ready.set()
        logger.debug(f"OSD CPU rendering complete: {len(self._images)} images")

    def prepare_textures(self) -> None:
        """
        Upload all rendered images to GPU textures.
        Must be called from the pipeline thread before use.
        """
        self.images_ready.wait()
        for text, img in self._images.items():
            if text not in self._texture_cache:
                logger.debug(f"Uploading OSD texture for '{text}'")
                try:
                    self._texture_cache[text] = upload_image_to_texture(img)
                except Exception as e:
                    logger.error(f"Failed to upload OSD texture '{text}': {e}")
        logger.debug("All OSD textures uploaded to GPU")

    def update(self) -> Tuple[Optional[Texture2D], bool]:
        """
        Update internal state (expiry) and return the texture to draw,
        along with a flag indicating whether a redraw is needed.

        If the active text has no GPU texture yet, upload it now (on pipeline thread).
        """
        with self._lock:
            # Handle expiry
            if self._expiry_time is not None and time.monotonic() >= self._expiry_time:
                self._active_text = None
                self._active_texture = None
                self._expiry_time = None

            # Lazy upload: if we have an active text but no texture, create it now
            if self._active_text is not None and self._active_texture is None:
                texture = self._texture_cache.get(self._active_text)
                if texture is None:
                    img = self._images.get(self._active_text)
                    if img is not None:
                        logger.debug(f"Uploading OSD texture for '{self._active_text}'")
                        try:
                            texture = upload_image_to_texture(img)
                            self._texture_cache[self._active_text] = texture
                        except Exception as e:
                            logger.error(
                                f"Failed to upload OSD texture '{self._active_text}': {e}"
                            )
                            texture = None
                self._active_texture = texture

            texture = self._active_texture
            needs_redraw = self._needs_redraw
            self._needs_redraw = False

        return texture, needs_redraw

    def show(self, text: str, duration: float = 1.5) -> None:
        """Request an OSD message to be displayed (thread‑safe)."""
        with self._lock:
            self._active_text = text
            self._active_texture = None  # Will be resolved when drawn
            self._expiry_time = time.monotonic() + duration
            self._needs_redraw = True

    def get_compute_pipeline(
        self, texture: Texture2D, screen_tex: Texture2D
    ) -> Compute:
        """Return a cached compute pipeline for the given OSD texture."""
        if texture not in self._compute_cache:
            self._compute_cache[texture] = Compute(
                self._blender.shader,
                srv=[screen_tex, texture],
                uav=[screen_tex],
                cbv=[self._blender.cb],
                samplers=[self._blender.sampler],
                push_size=0,
            )
        return self._compute_cache[texture]

    def update_constants(self, x: int, y: int, w: int, h: int) -> None:
        """Update the constant buffer with OSD position and size."""
        cb_data = struct.pack("iiii", x, y, w, h)
        self._blender.cb.upload(cb_data)

    def clear_compute_cache(self) -> None:
        """Clear cached compute pipelines (e.g., on swapchain resize)."""
        self._compute_cache.clear()

    def shutdown(self) -> None:
        """Clean up resources."""
        self._render_executor.shutdown(wait=False)
        # Textures and compute pipelines are owned by Vulkan and will be
        # destroyed when the device is torn down.
