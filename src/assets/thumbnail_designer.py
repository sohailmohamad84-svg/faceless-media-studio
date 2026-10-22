"""YouTube thumbnail generator and scene title card builder using Pillow."""
from pathlib import Path
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont


class ThumbnailDesigner:
    BG_DARK = (13, 17, 23)
    BG_SECONDARY = (22, 27, 34)
    TEXT_WHITE = (240, 246, 252)
    ACCENT_GOLD = (245, 158, 11)
    ACCENT_RED = (239, 68, 68)
    ACCENT_CYAN = (56, 189, 248)

    @classmethod
    def create_thumbnail(
        cls,
        title_top: str,
        title_bottom: str,
        badge_text: str,
        output_path: str,
        size: Tuple[int, int] = (1280, 720),
        accent_color: Tuple[int, int, int] = (245, 158, 11),
    ) -> str:
        """Create a high-contrast, clickable YouTube thumbnail (1280x720)."""
        img = Image.new("RGB", size, color=cls.BG_DARK)
        draw = ImageDraw.Draw(img)

        width, height = size

        # 1. Subtle gradient / background panel effect
        for y in range(height):
            ratio = y / height
            r = int(cls.BG_DARK[0] * (1 - ratio * 0.4))
            g = int(cls.BG_DARK[1] * (1 - ratio * 0.4))
            b = int(cls.BG_DARK[2] + ratio * 20)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 2. Side accent pillar
        draw.rectangle([(0, 0), (24, height)], fill=accent_color)

        # 3. Typography (use default Pillow font with scale fallback)
        try:
            font_title = ImageFont.truetype("arial.ttf", 68)
            font_badge = ImageFont.truetype("arial.ttf", 36)
            font_brand = ImageFont.truetype("arial.ttf", 26)
        except Exception:
            font_title = ImageFont.load_default()
            font_badge = ImageFont.load_default()
            font_brand = ImageFont.load_default()

        # 4. Draw Badges
        if badge_text:
            badge_x = 70
            badge_y = 90
            badge_w = 420
            badge_h = 65
            draw.rounded_rectangle(
                [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
                radius=10,
                fill=accent_color,
            )
            draw.text(
                (badge_x + 20, badge_y + 12),
                badge_text.upper(),
                fill=(10, 10, 10),
                font=font_badge,
                stroke_width=1,
                stroke_fill=(0, 0, 0),
            )

        # 5. Main Headline Texts with Drop Shadow
        top_y = 230
        bottom_y = 340
        x_pos = 70

        # Drop shadow for top text
        draw.text((x_pos + 4, top_y + 4), title_top.upper(), fill=(0, 0, 0), font=font_title)
        draw.text((x_pos, top_y), title_top.upper(), fill=cls.TEXT_WHITE, font=font_title)

        # Bottom Text with Accent Color
        draw.text((x_pos + 4, bottom_y + 4), title_bottom.upper(), fill=(0, 0, 0), font=font_title)
        draw.text((x_pos, bottom_y), title_bottom.upper(), fill=accent_color, font=font_title)

        # 6. Brand stamp
        draw.text((width - 260, height - 60), "APEX ENTERPRISE", fill=(130, 140, 155), font=font_brand)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "JPEG", quality=95)
        return output_path

    @classmethod
    def create_scene_slide(
        cls,
        title: str,
        subtitle: str,
        output_path: str,
        size: Tuple[int, int] = (1920, 1080),
        accent_color: Tuple[int, int, int] = (56, 189, 248),
    ) -> str:
        """Create a full 1080p slide card for video scenes."""
        img = Image.new("RGB", size, color=cls.BG_DARK)
        draw = ImageDraw.Draw(img)
        w, h = size

        # Background gradient
        for y in range(h):
            ratio = y / h
            r = int(cls.BG_DARK[0] + ratio * 8)
            g = int(cls.BG_DARK[1] + ratio * 12)
            b = int(cls.BG_DARK[2] + ratio * 24)
            draw.line([(0, y), (w, y)], fill=(r, g, b))

        # Border styling
        draw.rectangle([(40, 40), (w - 40, h - 40)], outline=(48, 54, 61), width=3)
        draw.rectangle([(40, 40), (60, h - 40)], fill=accent_color)

        try:
            font_title = ImageFont.truetype("arial.ttf", 64)
            font_sub = ImageFont.truetype("arial.ttf", 36)
            font_brand = ImageFont.truetype("arial.ttf", 28)
        except Exception:
            font_title = ImageFont.load_default()
            font_sub = ImageFont.load_default()
            font_brand = ImageFont.load_default()

        # Headline
        draw.text((120, 360), title.upper(), fill=cls.TEXT_WHITE, font=font_title)
        # Subtitle
        draw.text((120, 460), subtitle, fill=accent_color, font=font_sub)
        # Branding
        draw.text((120, h - 120), "APEX ENTERPRISE  •  BUSINESS FORENSICS", fill=(100, 116, 139), font=font_brand)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
