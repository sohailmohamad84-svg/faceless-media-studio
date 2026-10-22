"""High-retention visual asset generator: document cutouts, newspaper clippings, and cliffhangers."""
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class ViralDesigner:
    DARK_BG = (10, 14, 20)
    PANEL_BG = (18, 24, 34)
    TEXT_WHITE = (248, 250, 252)
    TEXT_MUTED = (148, 163, 184)
    ACCENT_GOLD = (245, 158, 11)
    ACCENT_RED = (239, 68, 68)
    ACCENT_CYAN = (56, 189, 248)
    HIGHLIGHT_YELLOW = (250, 204, 21, 160)  # semi-transparent RGBA

    @classmethod
    def _get_fonts(cls):
        try:
            return {
                "headline": ImageFont.truetype("arialbd.ttf", 64),
                "title": ImageFont.truetype("arialbd.ttf", 48),
                "subtitle": ImageFont.truetype("arial.ttf", 32),
                "body": ImageFont.truetype("arial.ttf", 26),
                "badge": ImageFont.truetype("arialbd.ttf", 28),
                "stamp": ImageFont.truetype("arialbd.ttf", 42),
            }
        except Exception:
            try:
                return {
                    "headline": ImageFont.truetype("arial.ttf", 64),
                    "title": ImageFont.truetype("arial.ttf", 48),
                    "subtitle": ImageFont.truetype("arial.ttf", 32),
                    "body": ImageFont.truetype("arial.ttf", 26),
                    "badge": ImageFont.truetype("arial.ttf", 28),
                    "stamp": ImageFont.truetype("arial.ttf", 42),
                }
            except Exception:
                d = ImageFont.load_default()
                return {"headline": d, "title": d, "subtitle": d, "body": d, "badge": d, "stamp": d}

    @classmethod
    def create_cinematic_background(cls, size: Tuple[int, int] = (1920, 1080)) -> Image.Image:
        """Create dark textured cinematic background with subtle radial vignette."""
        w, h = size
        img = Image.new("RGB", size, cls.DARK_BG)
        draw = ImageDraw.Draw(img)

        # Gradient shading from center out
        cx, cy = w // 2, h // 2
        for r in range(0, max(cx, cy), 15):
            factor = (r / max(cx, cy))
            col = (
                int(cls.DARK_BG[0] * (1 - factor * 0.5)),
                int(cls.DARK_BG[1] * (1 - factor * 0.5)),
                int(cls.DARK_BG[2] * (1 - factor * 0.4)),
            )
            draw.ellipse([(cx - r * 1.6, cy - r), (cx + r * 1.6, cy + r)], outline=col, width=15)

        # Subtle dark border vignette
        draw.rectangle([(0, 0), (w, h)], outline=(5, 7, 10), width=35)
        return img

    @classmethod
    def create_document_highlight_scene(
        cls,
        title: str,
        doc_header: str,
        highlighted_claim: str,
        context_body: str,
        output_path: str,
        stamp_text: str = "OFFICIAL SEC FILING",
    ) -> str:
        """Generate high-retention SEC 10-K / corporate filing document with glowing yellow highlight."""
        w, h = 1920, 1080
        img = cls.create_cinematic_background((w, h))
        fonts = cls._get_fonts()

        # Document page panel (white/cream paper with drop shadow)
        doc_w, doc_h = 1350, 720
        doc_x, doc_y = (w - doc_w) // 2, (h - doc_h) // 2 + 30

        # Draw paper shadow
        shadow = Image.new("RGBA", (doc_w + 40, doc_h + 40), (0, 0, 0, 140))
        img.paste(shadow.filter(ImageFilter.GaussianBlur(15)), (doc_x - 10, doc_y - 5), shadow.filter(ImageFilter.GaussianBlur(15)))

        # Paper page
        paper = Image.new("RGBA", (doc_w, doc_h), (248, 246, 240, 255))
        p_draw = ImageDraw.Draw(paper)

        # Top document header rules
        p_draw.line([(50, 60), (doc_w - 50, 60)], fill=(180, 175, 165), width=2)
        p_draw.text((50, 25), doc_header.upper(), fill=(100, 95, 85), font=fonts["subtitle"])
        p_draw.line([(50, 65), (doc_w - 50, 65)], fill=(180, 175, 165), width=1)

        # Document Context lines
        p_draw.text((50, 95), "PART I - ITEM 1: FINANCIAL CONDITION & RISK FACTORS", fill=(60, 55, 45), font=fonts["body"])
        p_draw.text((50, 140), context_body[:180], fill=(70, 65, 55), font=fonts["body"])

        # Glowing Highlight Marker over the key claim!
        hl_box = [(45, 230), (doc_w - 45, 330)]
        p_draw.rounded_rectangle(hl_box, radius=8, fill=cls.HIGHLIGHT_YELLOW)
        p_draw.text((60, 245), f'"{highlighted_claim}"', fill=(15, 10, 5), font=fonts["title"])

        # Bottom filing legal notice
        p_draw.text((50, 480), "Filed pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934.", fill=(120, 115, 105), font=fonts["body"])
        p_draw.text((50, 530), "SOURCE VERIFICATION: UNITED STATES SECURITIES AND EXCHANGE COMMISSION", fill=(100, 95, 85), font=fonts["body"])

        # Red Stamp in corner
        stamp_box = [(doc_w - 380, doc_h - 120), (doc_w - 40, doc_h - 40)]
        p_draw.rounded_rectangle(stamp_box, radius=6, outline=cls.ACCENT_RED, width=3)
        p_draw.text((doc_w - 365, doc_h - 105), stamp_text, fill=cls.ACCENT_RED, font=fonts["badge"])

        # Paste paper onto dark background
        img.paste(paper, (doc_x, doc_y), paper)

        # Main Scene Title at top
        draw = ImageDraw.Draw(img)
        draw.text((doc_x, 40), title.upper(), fill=cls.ACCENT_GOLD, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_headline_scene(
        cls,
        title: str,
        news_outlet: str,
        headline_text: str,
        date_str: str,
        output_path: str,
        investigative_tag: str = "SPECIAL REPORT",
    ) -> str:
        """Generate high-retention press clipping / breaking investigation scene."""
        w, h = 1920, 1080
        img = cls.create_cinematic_background((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts()

        # Badge pill
        draw.rounded_rectangle([(140, 90), (460, 145)], radius=8, fill=cls.ACCENT_RED)
        draw.text((160, 102), investigative_tag.upper(), fill=(255, 255, 255), font=fonts["badge"])
        draw.text((490, 105), f"ARCHIVAL INTELLIGENCE • {date_str}", fill=cls.TEXT_MUTED, font=fonts["body"])

        # Big Cinematic Headline
        draw.text((140, 180), news_outlet.upper(), fill=cls.ACCENT_CYAN, font=fonts["title"])

        # Draw headline with drop shadow
        draw.text((144, 274), headline_text.upper(), fill=(0, 0, 0), font=fonts["headline"])
        draw.text((140, 270), headline_text.upper(), fill=cls.TEXT_WHITE, font=fonts["headline"])

        # Graphic Divider line
        draw.line([(140, 480), (w - 140, 480)], fill=(40, 50, 65), width=2)
        draw.rectangle([(140, 477), (320, 483)], fill=cls.ACCENT_GOLD)

        # Strategic take / subtext
        draw.text((140, 520), title, fill=cls.ACCENT_GOLD, font=fonts["title"])
        draw.text((140, 610), "CONFIDENTIAL CORPORATE RECORDS • ANALYZED BY APEX ENTERPRISE", fill=cls.TEXT_MUTED, font=fonts["subtitle"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_cliffhanger_scene(
        cls,
        part1_title: str,
        part2_teaser: str,
        output_path: str,
    ) -> str:
        """Generate an intense cliffhanger card to end Part 1 and demand the viewer watch Part 2."""
        w, h = 1920, 1080
        img = cls.create_cinematic_background((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts()

        # Warning banner
        draw.rounded_rectangle([(w // 2 - 250, 160), (w // 2 + 250, 225)], radius=10, fill=cls.ACCENT_RED)
        draw.text((w // 2 - 180, 175), "END OF PART 1", fill=(255, 255, 255), font=fonts["title"])

        # Big Cliffhanger Title
        draw.text((w // 2 - 450, 320), "WHAT HAPPENED NEXT?", fill=cls.TEXT_WHITE, font=fonts["headline"])
        draw.text((w // 2 - 450, 440), part2_teaser.upper(), fill=cls.ACCENT_GOLD, font=fonts["title"])

        # Call to Action Box
        cta_box = [(w // 2 - 500, 620), (w // 2 + 500, 740)]
        draw.rounded_rectangle(cta_box, radius=12, fill=cls.PANEL_BG, outline=cls.ACCENT_CYAN, width=3)
        draw.text((w // 2 - 460, 645), "CLICK THE LINK BELOW OR ON-SCREEN FOR PART 2", fill=cls.ACCENT_CYAN, font=fonts["subtitle"])
        draw.text((w // 2 - 460, 690), "Subscribe to Apex Enterprise so you never miss the final verdict.", fill=cls.TEXT_MUTED, font=fonts["body"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
