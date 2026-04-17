from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Dict

from ..vulkan import Buffer


def _upload_image_to_texture(image: Image.Image) -> Texture2D:
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
        img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
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
