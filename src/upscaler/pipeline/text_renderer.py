from PIL import Image, ImageDraw, ImageFont

import vulkan
from vulkan.constants import R8G8B8A8_UNORM


class TextRenderer:
    def __init__(
        self, texts: list[str], screen_height: int = 1080, font_path: str = None
    ):
        # Font size scales with screen height (approx 4%)
        self.font_size = max(24, int(screen_height * 0.04))
        try:
            self.font = ImageFont.truetype(
                font_path or "DejaVuSans.ttf", self.font_size
            )
        except:
            self.font = ImageFont.load_default()
        self.cache = {}
        for text in texts:
            self._render_to_cache(text)

    def _render_to_cache(self, text: str):
        if text in self.cache:
            return

        # Colors: white text, black shadow, dark translucent background
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

        # Upload to GPU
        tex = vulkan.Texture2D(img_w, img_h, R8G8B8A8_UNORM)
        buffer_size = img_w * img_h * 4
        upload_buffer = vulkan.Buffer(buffer_size, heap_type=vulkan.HEAP_UPLOAD)
        upload_buffer.upload(img.tobytes())
        upload_buffer.copy_to(tex)

        self.cache[text] = tex

    def get_texture(self, text: str) -> vulkan.Texture2D | None:
        return self.cache.get(text)
