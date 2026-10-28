"""Thumbnail Generator for Faceless Media Studio.
Generates purpose-built, high-contrast, typography-mastered thumbnails for YouTube Shorts (9:16)
and promotional landscape (16:9) featuring Main, Alternative A, and Alternative B variants.
"""
import os
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


class ThumbnailGenerator:
    """Creates cinematic, high-retention engineering documentary thumbnails."""

    BRAND_GOLD = (255, 224, 32)      # #FFE020
    BRAND_BLUE = (56, 189, 248)      # #38BDF8
    DARK_BG = (11, 15, 25)           # #0B0F19
    WHITE = (248, 250, 252)

    @classmethod
    def _get_font(cls, size: int) -> ImageFont.ImageFont:
        font_names = [
            "arialbd.ttf", "ariblk.ttf", "impact.ttf", "segoeui.ttf", "helvetica.ttf", "DejaVuSans-Bold.ttf"
        ]
        for fn in font_names:
            try:
                return ImageFont.truetype(fn, size)
            except Exception:
                continue
        return ImageFont.load_default()

    @classmethod
    def generate_short_cover(
        cls,
        topic_id: str,
        headline_text: str,
        subtitle_text: str,
        out_path: Path,
        variant_name: str = "main",
        bg_image_path: Optional[Path] = None,
        accent_color: tuple = BRAND_GOLD,
        dimensions: tuple = (1080, 1920)
    ) -> Path:
        """
        Generates a 1080x1920 vertical Shorts thumbnail with forensic engineering typography.
        """
        w, h = dimensions
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Base image
        if bg_image_path and bg_image_path.exists():
            base = Image.open(bg_image_path).convert("RGBA")
            base = base.resize((w, h), Image.Resampling.LANCZOS)
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(base)
            base = enhancer.enhance(1.15)
        else:
            base = Image.new("RGBA", (w, h), cls.DARK_BG)
            draw_bg = ImageDraw.Draw(base)
            # Draw technical grid lines
            for y_line in range(0, h, 80):
                draw_bg.line([(0, y_line), (w, y_line)], fill=(255, 255, 255, 12), width=1)
            for x_line in range(0, w, 80):
                draw_bg.line([(x_line, 0), (x_line, h)], fill=(255, 255, 255, 12), width=1)

        # Dark overlay gradient for maximum text contrast
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)

        # Top vignette
        for y in range(350):
            alpha = int(180 * (1.0 - y / 350))
            draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

        # Bottom safe-area vignette
        for y in range(h - 500, h):
            frac = (y - (h - 500)) / 500
            alpha = int(220 * frac)
            draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

        # Mid-band gradient for typography placement (y=400 to y=1000)
        for y in range(350, 1050):
            # parabolic alpha peaking at center
            dist = abs(y - 700) / 350
            alpha = int(170 * (1.0 - (dist ** 2)))
            draw_ov.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

        combined = Image.alpha_composite(base, overlay)
        draw = ImageDraw.Draw(combined)

        # Brand pill at top
        pill_font = cls._get_font(34)
        brand_pill = "DOCUMENTARY FORENSICS • 4K 60FPS"
        draw.rectangle([(w // 2 - 340, 140), (w // 2 + 340, 200)], fill=(0, 0, 0, 180), outline=accent_color, width=2)
        draw.text((w // 2, 170), brand_pill, font=pill_font, fill=accent_color, anchor="mm")

        # Main Headline Typography (2-4 words, large impact)
        head_font = cls._get_font(98)
        words = headline_text.upper().split()
        lines = []
        if len(words) <= 3:
            lines = [" ".join(words)]
        else:
            mid = math.ceil(len(words) / 2)
            lines = [" ".join(words[:mid]), " ".join(words[mid:])]

        y_text = 620
        for line in lines:
            # Draw heavy black outline for legibility
            for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5), (-4, -4), (4, 4), (-4, 4), (4, -4)]:
                draw.text((w // 2 + dx, y_text + dy), line, font=head_font, fill=(0, 0, 0, 255), anchor="mm")
            # Text shadow
            draw.text((w // 2 + 6, y_text + 8), line, font=head_font, fill=(0, 0, 0, 180), anchor="mm")
            # Text fill
            draw.text((w // 2, y_text), line, font=head_font, fill=accent_color, anchor="mm")
            y_text += 125

        # Subtitle badge / mystery prompt
        if subtitle_text:
            sub_font = cls._get_font(42)
            draw.text((w // 2, y_text + 30), subtitle_text, font=sub_font, fill=cls.WHITE, anchor="mm")

        # Save output
        final_rgb = combined.convert("RGB")
        final_rgb.save(out_path, "JPEG", quality=95)
        return out_path

    @classmethod
    def generate_promotional_16x9(
        cls,
        topic_id: str,
        headline_text: str,
        subtitle_text: str,
        out_path: Path,
        bg_image_path: Optional[Path] = None,
        accent_color: tuple = BRAND_GOLD
    ) -> Path:
        """Generates 1280x720 landscape promotional thumbnail."""
        return cls.generate_short_cover(
            topic_id=topic_id,
            headline_text=headline_text,
            subtitle_text=subtitle_text,
            out_path=out_path,
            dimensions=(1280, 720),
            bg_image_path=bg_image_path,
            accent_color=accent_color
        )

    @classmethod
    def generate_full_package(
        cls,
        topic_id: str,
        main_headline: str,
        main_subtitle: str,
        alt_a_headline: str,
        alt_b_headline: str,
        bg_frame_path: Optional[Path] = None,
        output_dir: Path = Path("data/thumbnails")
    ) -> Dict[str, Any]:
        """
        Produces the complete thumbnail package required by Part 9:
        1. Main thumbnail (9:16)
        2. Alternative A (9:16)
        3. Alternative B (9:16)
        4. Promotional landscape (16:9)
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        main_path = output_dir / f"{topic_id}_thumb_main.jpg"
        alt_a_path = output_dir / f"{topic_id}_thumb_alt_a.jpg"
        alt_b_path = output_dir / f"{topic_id}_thumb_alt_b.jpg"
        promo_path = output_dir / f"{topic_id}_thumb_promo_16x9.jpg"

        # Generate Main
        cls.generate_short_cover(
            topic_id=topic_id,
            headline_text=main_headline,
            subtitle_text=main_subtitle,
            out_path=main_path,
            variant_name="main",
            bg_image_path=bg_frame_path,
            accent_color=cls.BRAND_GOLD
        )

        # Generate Alt A (Cyan/Blue emphasis)
        cls.generate_short_cover(
            topic_id=topic_id,
            headline_text=alt_a_headline,
            subtitle_text=main_subtitle,
            out_path=alt_a_path,
            variant_name="alt_a",
            bg_image_path=bg_frame_path,
            accent_color=cls.BRAND_BLUE
        )

        # Generate Alt B (High-Contrast White with Gold outline)
        cls.generate_short_cover(
            topic_id=topic_id,
            headline_text=alt_b_headline,
            subtitle_text=main_subtitle,
            out_path=alt_b_path,
            variant_name="alt_b",
            bg_image_path=bg_frame_path,
            accent_color=cls.WHITE
        )

        # Generate Promo 16:9
        cls.generate_promotional_16x9(
            topic_id=topic_id,
            headline_text=main_headline,
            subtitle_text=main_subtitle,
            out_path=promo_path,
            bg_image_path=bg_frame_path,
            accent_color=cls.BRAND_GOLD
        )

        return {
            "topic_id": topic_id,
            "main_thumbnail": str(main_path),
            "alt_a_thumbnail": str(alt_a_path),
            "alt_b_thumbnail": str(alt_b_path),
            "promo_16x9": str(promo_path),
            "generated_count": 4
        }
