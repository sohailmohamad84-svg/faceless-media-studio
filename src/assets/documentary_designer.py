"""Cinematic Documentary Visual Engine: 2.5D photo collages, aged newspapers, court dockets, and financial autopsies.
Supports both 16:9 Landscape (1920x1080) and 9:16 Vertical YouTube Shorts (1080x1920).
"""
import math
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps


class DocumentaryDesigner:
    DARK_BG = (12, 16, 24)
    SLATE_BG = (18, 24, 36)
    CREAM_PAPER = (244, 240, 230)
    TEXT_WHITE = (248, 250, 252)
    TEXT_MUTED = (148, 163, 184)
    ACCENT_GOLD = (245, 158, 11)
    ACCENT_RED = (220, 38, 38)
    ACCENT_CYAN = (56, 189, 248)
    HIGHLIGHT_YELLOW = (253, 224, 71, 180)  # Semi-transparent RGBA

    @classmethod
    def _get_fonts(cls, is_vertical: bool = False):
        """Load crisp system fonts with graceful cross-platform fallbacks."""
        scale = 1.0 if not is_vertical else 0.95
        try:
            return {
                "headline": ImageFont.truetype("arialbd.ttf", int(60 * scale)),
                "title": ImageFont.truetype("arialbd.ttf", int(44 * scale)),
                "subtitle": ImageFont.truetype("arial.ttf", int(28 * scale)),
                "body": ImageFont.truetype("arial.ttf", int(22 * scale)),
                "badge": ImageFont.truetype("arialbd.ttf", int(24 * scale)),
                "stamp": ImageFont.truetype("arialbd.ttf", int(42 * scale)),
                "big_num": ImageFont.truetype("arialbd.ttf", int(72 * scale)),
                "mono": ImageFont.truetype("courbd.ttf", int(26 * scale)),
            }
        except Exception:
            try:
                return {
                    "headline": ImageFont.truetype("arial.ttf", int(60 * scale)),
                    "title": ImageFont.truetype("arial.ttf", int(44 * scale)),
                    "subtitle": ImageFont.truetype("arial.ttf", int(28 * scale)),
                    "body": ImageFont.truetype("arial.ttf", int(22 * scale)),
                    "badge": ImageFont.truetype("arial.ttf", int(24 * scale)),
                    "stamp": ImageFont.truetype("arial.ttf", int(42 * scale)),
                    "big_num": ImageFont.truetype("arial.ttf", int(72 * scale)),
                    "mono": ImageFont.truetype("cour.ttf", int(26 * scale)),
                }
            except Exception:
                d = ImageFont.load_default()
                return {k: d for k in ["headline", "title", "subtitle", "body", "badge", "stamp", "big_num", "mono"]}

    @classmethod
    def create_cinematic_backdrop(cls, size: Tuple[int, int] = (1920, 1080)) -> Image.Image:
        """Create a deep, moody cinematic background with subtle radial vignette and slate tone."""
        w, h = size
        base = Image.new("RGB", size, cls.DARK_BG)
        draw = ImageDraw.Draw(base)

        cx, cy = w // 2, h // 2
        max_r = int(math.hypot(cx, cy))
        step = 20 if max_r < 1500 else 25
        for r in range(0, max_r, step):
            factor = r / max_r
            col = (
                int(cls.DARK_BG[0] * (1.0 - factor * 0.6)),
                int(cls.DARK_BG[1] * (1.0 - factor * 0.6)),
                int(cls.DARK_BG[2] * (1.0 - factor * 0.5)),
            )
            draw.ellipse([(cx - r * 1.5, cy - r), (cx + r * 1.5, cy + r)], outline=col, width=step)

        # Subtle dark border vignette
        border_w = 40 if w > 1200 else 30
        draw.rectangle([(0, 0), (w, h)], outline=(5, 7, 10), width=border_w)
        return base

    @classmethod
    def create_archival_photo_scene(
        cls,
        photo_path: str,
        title: str,
        caption: str,
        badge_text: str = "HISTORICAL ARCHIVE",
        stamp_text: Optional[str] = None,
        output_path: str = "scene.png",
        is_vertical: bool = False,
    ) -> str:
        """Generate a 2.5D archival photo slide with realistic blurred background, drop shadow, and badges."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        fonts = cls._get_fonts(is_vertical=is_vertical)

        photo_file = Path(photo_path)
        if photo_file.exists():
            raw_photo = Image.open(photo_file).convert("RGB")
        else:
            raw_photo = Image.new("RGB", (800, 600), (40, 50, 65))
            d = ImageDraw.Draw(raw_photo)
            d.text((250, 280), "[ARCHIVAL PHOTOGRAPH]", fill=(180, 190, 205), font=fonts["title"])

        if is_vertical:
            # MagnatesMedia Blur Backdrop: Scale photo to fill canvas, blur, and darken
            bg_photo = ImageOps.fit(raw_photo, (w, h), method=Image.Resampling.LANCZOS)
            bg_photo = bg_photo.filter(ImageFilter.GaussianBlur(32))
            dark_overlay = Image.new("RGBA", (w, h), (10, 14, 22, 185))
            img = Image.new("RGB", (w, h))
            img.paste(bg_photo, (0, 0))
            img.paste(dark_overlay, (0, 0), dark_overlay)

            target_w, target_h = 960, 960
            pos_x = (w - (target_w + 30)) // 2
            pos_y = 300
        else:
            img = cls.create_cinematic_backdrop((w, h))
            target_w, target_h = 1300, 720
            pos_x = (w - (target_w + 40)) // 2
            pos_y = (h - (target_h + 70)) // 2 + 25

        cropped_photo = ImageOps.fit(raw_photo, (target_w, target_h), method=Image.Resampling.LANCZOS)

        frame_pad = 20
        frame_bottom_pad = 55
        frame_w = target_w + frame_pad * 2
        frame_h = target_h + frame_pad + frame_bottom_pad

        frame = Image.new("RGBA", (frame_w, frame_h), (245, 243, 237, 255))
        frame.paste(cropped_photo, (frame_pad, frame_pad))

        f_draw = ImageDraw.Draw(frame)
        f_draw.text((frame_pad + 12, frame_h - 44), caption[:65].upper(), fill=(45, 50, 60), font=fonts["body"])

        shadow = Image.new("RGBA", (frame_w + 40, frame_h + 40), (0, 0, 0, 190))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        img.paste(shadow, (pos_x - 10, pos_y - 8), shadow)
        img.paste(frame, (pos_x, pos_y), frame)

        draw = ImageDraw.Draw(img)

        # Title & Badges
        if is_vertical:
            badge_box = [(60, 140), (460, 200)]
            draw.rounded_rectangle(badge_box, radius=8, fill=cls.ACCENT_RED)
            draw.text((badge_box[0][0] + 18, badge_box[0][1] + 12), badge_text.upper()[:24], fill=cls.TEXT_WHITE, font=fonts["badge"])
            draw.text((60, 215), title.upper()[:35], fill=cls.ACCENT_GOLD, font=fonts["headline"])
        else:
            draw.text((pos_x, 40), title.upper(), fill=cls.ACCENT_GOLD, font=fonts["title"])
            badge_box = [(pos_x + frame_w - 320, pos_y - 18), (pos_x + frame_w - 10, pos_y + 26)]
            draw.rounded_rectangle(badge_box, radius=6, fill=cls.ACCENT_RED)
            draw.text((badge_box[0][0] + 18, badge_box[0][1] + 6), badge_text.upper(), fill=cls.TEXT_WHITE, font=fonts["badge"])

        if stamp_text:
            if is_vertical:
                stamp_box = [(pos_x + frame_w - 470, pos_y + 35), (pos_x + frame_w - 20, pos_y + 98)]
            else:
                sy = pos_y + frame_h - 110
                stamp_box = [(pos_x + 40, sy), (pos_x + 480, sy + 65)]
            draw.rounded_rectangle(stamp_box, radius=8, outline=cls.ACCENT_RED, width=4)
            draw.text((stamp_box[0][0] + 18, stamp_box[0][1] + 10), stamp_text.upper()[:25], fill=cls.ACCENT_RED, font=fonts["stamp"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_newspaper_investigation_scene(
        cls,
        publication: str,
        headline: str,
        subhead: str,
        highlighted_claim: str,
        date_str: str,
        output_path: str,
        investigative_tag: str = "EXCLUSIVELY UNCOVERED",
        is_vertical: bool = False,
    ) -> str:
        """Generate high-contrast aged newspaper investigation with glowing yellow highlight."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        img = cls.create_cinematic_backdrop((w, h))
        fonts = cls._get_fonts(is_vertical=is_vertical)

        paper_w = 980 if is_vertical else 1420
        paper_h = 1260 if is_vertical else 780
        px = (w - paper_w) // 2
        py = 220 if is_vertical else (h - paper_h) // 2 + 30

        shadow = Image.new("RGBA", (paper_w + 40, paper_h + 40), (0, 0, 0, 190))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        img.paste(shadow, (px - 10, py - 8), shadow)

        paper = Image.new("RGBA", (paper_w, paper_h), (248, 244, 234, 255))
        p_draw = ImageDraw.Draw(paper)

        # Masthead
        p_draw.line([(30, 35), (paper_w - 30, 35)], fill=(80, 75, 65), width=3)
        p_draw.text((40, 48), publication.upper()[:30], fill=(25, 20, 15), font=fonts["headline"])
        p_draw.text((40, 115), date_str.upper(), fill=(100, 95, 85), font=fonts["body"])
        p_draw.text((paper_w - 280, 115), "SPECIAL INVESTIGATION", fill=(100, 95, 85), font=fonts["body"])
        p_draw.line([(30, 145), (paper_w - 30, 145)], fill=(80, 75, 65), width=2)

        # Headline
        p_draw.text((35, 175), headline.upper()[:40], fill=(15, 10, 5), font=fonts["title"])
        p_draw.text((35, 245), subhead[:55], fill=(75, 70, 60), font=fonts["subtitle"])
        p_draw.line([(30, 295), (paper_w - 30, 295)], fill=(180, 175, 165), width=1)

        # Glowing yellow marker box
        hl_y = 330
        hl_h = 170 if is_vertical else 130
        p_draw.rounded_rectangle([(30, hl_y), (paper_w - 30, hl_y + hl_h)], radius=10, fill=cls.HIGHLIGHT_YELLOW)
        p_draw.text((45, hl_y + 35), f'"{highlighted_claim[:45]}"', fill=(10, 8, 4), font=fonts["title"])

        # Context body
        p_draw.text(
            (35, hl_y + hl_h + 40),
            "Confidential filings verify that predatory debt obligations stripped the company\n"
            "of capital, while Wall Street extracted over $470 million in advisory fees.\n\n"
            "By locking Toys 'R' Us into unsustainable high-yield bonds, sponsors ensured\n"
            "steady fee streams regardless of store-level operational performance.",
            fill=(50, 45, 38),
            font=fonts["body"],
        )

        # Stamp
        if is_vertical:
            stamp_box = [(paper_w - 380, 50), (paper_w - 30, 115)]
        else:
            stamp_box = [(paper_w - 380, paper_h - 100), (paper_w - 30, paper_h - 35)]
        p_draw.rounded_rectangle(stamp_box, radius=8, outline=cls.ACCENT_RED, width=4)
        p_draw.text((stamp_box[0][0] + 16, stamp_box[0][1] + 10), investigative_tag.upper()[:22], fill=cls.ACCENT_RED, font=fonts["badge"])

        img.paste(paper, (px, py), paper)

        draw = ImageDraw.Draw(img)
        if is_vertical:
            badge_box = [(60, 140), (500, 195)]
            draw.rounded_rectangle(badge_box, radius=8, fill=cls.ACCENT_RED)
            draw.text((badge_box[0][0] + 16, badge_box[0][1] + 10), "INVESTIGATIVE PRESS DOSSIER", fill=cls.TEXT_WHITE, font=fonts["badge"])
        else:
            draw.text((px, 45), "INVESTIGATIVE PRESS DOSSIER", fill=cls.ACCENT_GOLD, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_court_docket_scene(
        cls,
        court_name: str,
        case_no: str,
        docket_title: str,
        highlighted_finding: str,
        output_path: str,
        stamp_text: str = "FILED UNDER CHAPTER 11",
        is_vertical: bool = False,
    ) -> str:
        """Generate realistic federal bankruptcy court docket / exhibit scene."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        img = cls.create_cinematic_backdrop((w, h))
        fonts = cls._get_fonts(is_vertical=is_vertical)

        doc_w = 980 if is_vertical else 1360
        doc_h = 1260 if is_vertical else 760
        dx = (w - doc_w) // 2
        dy = 220 if is_vertical else (h - doc_h) // 2 + 30

        shadow = Image.new("RGBA", (doc_w + 40, doc_h + 40), (0, 0, 0, 190))
        shadow = shadow.filter(ImageFilter.GaussianBlur(20))
        img.paste(shadow, (dx - 10, dy - 8), shadow)

        paper = Image.new("RGBA", (doc_w, doc_h), (250, 248, 242, 255))
        p_draw = ImageDraw.Draw(paper)

        # Header
        p_draw.text((40, 40), court_name.upper()[:38], fill=(20, 20, 20), font=fonts["title"])
        p_draw.line([(30, 95), (doc_w - 30, 95)], fill=(150, 145, 135), width=2)

        p_draw.text((40, 115), "IN RE: TOYS 'R' US, INC., ET AL.", fill=(40, 40, 40), font=fonts["subtitle"])
        p_draw.text((40, 155), f"CASE: {case_no}", fill=(80, 80, 80), font=fonts["body"])
        p_draw.text((40, 195), f"EXHIBIT: {docket_title.upper()[:40]}", fill=(20, 20, 20), font=fonts["subtitle"])
        p_draw.line([(30, 245), (doc_w - 30, 245)], fill=(150, 145, 135), width=1)

        # Highlighted court evidence
        hl_y = 285
        hl_h = 170 if is_vertical else 140
        p_draw.rounded_rectangle([(30, hl_y), (doc_w - 30, hl_y + hl_h)], radius=10, fill=cls.HIGHLIGHT_YELLOW)
        p_draw.text((45, hl_y + 35), f'"{highlighted_finding[:45]}"', fill=(10, 10, 10), font=fonts["title"])

        p_draw.text((40, hl_y + hl_h + 35), "COURT AUDIT EVIDENCE:", fill=(30, 30, 30), font=fonts["subtitle"])
        p_draw.text((40, hl_y + hl_h + 80), "- 33,000 store workers fired with zero severance.", fill=(50, 50, 50), font=fonts["body"])
        p_draw.text((40, hl_y + hl_h + 125), "- Wall Street collected $470M+ in management fees.", fill=(50, 50, 50), font=fonts["body"])
        p_draw.text((40, hl_y + hl_h + 170), "- Debt payments consumed 97% of operating cash flow.", fill=(50, 50, 50), font=fonts["body"])

        # Rubber Stamp
        if is_vertical:
            stamp_box = [(doc_w - 440, 45), (doc_w - 30, 105)]
        else:
            stamp_box = [(doc_w - 440, doc_h - 100), (doc_w - 30, doc_h - 35)]
        p_draw.rounded_rectangle(stamp_box, radius=8, outline=cls.ACCENT_RED, width=4)
        p_draw.text((stamp_box[0][0] + 16, stamp_box[0][1] + 10), stamp_text.upper()[:24], fill=cls.ACCENT_RED, font=fonts["badge"])

        img.paste(paper, (dx, dy), paper)

        draw = ImageDraw.Draw(img)
        if is_vertical:
            badge_box = [(60, 140), (500, 195)]
            draw.rounded_rectangle(badge_box, radius=8, fill=cls.ACCENT_RED)
            draw.text((badge_box[0][0] + 16, badge_box[0][1] + 10), "LEGAL COURT DOCKET EXHIBIT", fill=cls.TEXT_WHITE, font=fonts["badge"])
        else:
            draw.text((dx, 45), "LEGAL COURT DOCKET EXHIBIT", fill=cls.ACCENT_GOLD, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_financial_autopsy_graphic(
        cls,
        title: str,
        metric_1_label: str,
        metric_1_val: str,
        metric_2_label: str,
        metric_2_val: str,
        subtext: str,
        output_path: str,
        is_vertical: bool = False,
    ) -> str:
        """Generate high-contrast Wall Street financial autopsy graphic."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts(is_vertical=is_vertical)

        panel_w = 980 if is_vertical else 1440
        panel_h = 1260 if is_vertical else 760
        px = (w - panel_w) // 2
        py = 220 if is_vertical else (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=(50, 65, 95), width=3)

        draw.text((px + 40, py + 40), title.upper()[:35], fill=cls.ACCENT_GOLD, font=fonts["headline"])
        draw.line([(px + 40, py + 120), (px + panel_w - 40, py + 120)], fill=(50, 65, 95), width=2)

        if is_vertical:
            # Stacked vertical boxes for mobile
            m_w = panel_w - 80
            # Metric 1
            m1_y = py + 150
            draw.rounded_rectangle([(px + 40, m1_y), (px + 40 + m_w, m1_y + 240)], radius=14, fill=(40, 22, 28), outline=cls.ACCENT_RED, width=3)
            draw.text((px + 65, m1_y + 30), metric_1_label.upper()[:30], fill=cls.TEXT_MUTED, font=fonts["subtitle"])
            draw.text((px + 65, m1_y + 95), metric_1_val, fill=cls.ACCENT_RED, font=fonts["big_num"])
            draw.text((px + 65, m1_y + 185), "DRAINED OPERATING CASH FLOW", fill=(240, 150, 150), font=fonts["body"])

            # Metric 2
            m2_y = m1_y + 270
            draw.rounded_rectangle([(px + 40, m2_y), (px + 40 + m_w, m2_y + 240)], radius=14, fill=(22, 35, 52), outline=cls.ACCENT_CYAN, width=3)
            draw.text((px + 65, m2_y + 30), metric_2_label.upper()[:30], fill=cls.TEXT_MUTED, font=fonts["subtitle"])
            draw.text((px + 65, m2_y + 95), metric_2_val, fill=cls.ACCENT_CYAN, font=fonts["big_num"])
            draw.text((px + 65, m2_y + 185), "ZERO CAPITAL ALLOCATED TO REINVESTMENT", fill=(140, 210, 250), font=fonts["body"])

            # Subtext
            sub_y = m2_y + 280
            draw.rounded_rectangle([(px + 40, sub_y), (px + 40 + m_w, sub_y + 160)], radius=12, fill=(14, 18, 28), outline=cls.ACCENT_GOLD, width=2)
            draw.text((px + 60, sub_y + 30), "FORENSIC ACCOUNTING VERDICT:", fill=cls.ACCENT_GOLD, font=fonts["subtitle"])
            draw.text((px + 60, sub_y + 80), subtext[:60], fill=cls.TEXT_WHITE, font=fonts["subtitle"])
        else:
            m1_w = (panel_w - 140) // 2
            m1_x = px + 50
            m1_y = py + 160
            draw.rounded_rectangle([(m1_x, m1_y), (m1_x + m1_w, m1_y + 240)], radius=12, fill=(35, 20, 25), outline=cls.ACCENT_RED, width=3)
            draw.text((m1_x + 30, m1_y + 30), metric_1_label.upper(), fill=cls.TEXT_MUTED, font=fonts["subtitle"])
            draw.text((m1_x + 30, m1_y + 90), metric_1_val, fill=cls.ACCENT_RED, font=fonts["big_num"])

            m2_x = m1_x + m1_w + 40
            draw.rounded_rectangle([(m2_x, m1_y), (m2_x + m1_w, m1_y + 240)], radius=12, fill=(20, 30, 45), outline=cls.ACCENT_CYAN, width=3)
            draw.text((m2_x + 30, m1_y + 30), metric_2_label.upper(), fill=cls.TEXT_MUTED, font=fonts["subtitle"])
            draw.text((m2_x + 30, m1_y + 90), metric_2_val, fill=cls.ACCENT_CYAN, font=fonts["big_num"])

            bar_y = py + 450
            draw.rounded_rectangle([(px + 50, bar_y), (px + panel_w - 50, bar_y + 180)], radius=10, fill=(14, 18, 28), outline=(35, 45, 65), width=2)
            draw.text((px + 80, bar_y + 35), "FORENSIC ACCOUNTING VERDICT:", fill=cls.ACCENT_GOLD, font=fonts["subtitle"])
            draw.text((px + 80, bar_y + 85), subtext, fill=cls.TEXT_WHITE, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_split_verdict_scene(
        cls,
        title: str,
        left_header: str,
        left_stat: str,
        left_sub: str,
        right_header: str,
        right_stat: str,
        right_sub: str,
        verdict_summary: str,
        output_path: str,
        is_vertical: bool = False,
    ) -> str:
        """Generate high-impact comparison verdict (Workers vs Wall Street)."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts(is_vertical=is_vertical)

        panel_w = 980 if is_vertical else 1500
        panel_h = 1260 if is_vertical else 780
        px = (w - panel_w) // 2
        py = 220 if is_vertical else (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=(50, 65, 95), width=3)
        draw.text((px + 40, py + 35), title.upper()[:35], fill=cls.ACCENT_GOLD, font=fonts["headline"])
        draw.line([(px + 40, py + 115), (px + panel_w - 40, py + 115)], fill=(50, 65, 95), width=2)

        if is_vertical:
            col_w = panel_w - 80
            # Top card: Workers
            c1_y = py + 145
            draw.rounded_rectangle([(px + 40, c1_y), (px + 40 + col_w, c1_y + 260)], radius=14, fill=(40, 18, 24), outline=cls.ACCENT_RED, width=3)
            draw.text((px + 65, c1_y + 25), left_header.upper()[:28], fill=cls.ACCENT_RED, font=fonts["title"])
            draw.text((px + 65, c1_y + 85), left_stat, fill=cls.TEXT_WHITE, font=fonts["big_num"])
            draw.text((px + 65, c1_y + 195), left_sub[:45], fill=(220, 180, 180), font=fonts["body"])

            # Bottom card: Wall St
            c2_y = c1_y + 290
            draw.rounded_rectangle([(px + 40, c2_y), (px + 40 + col_w, c2_y + 260)], radius=14, fill=(18, 35, 54), outline=cls.ACCENT_CYAN, width=3)
            draw.text((px + 65, c2_y + 25), right_header.upper()[:28], fill=cls.ACCENT_CYAN, font=fonts["title"])
            draw.text((px + 65, c2_y + 85), right_stat, fill=cls.ACCENT_GOLD, font=fonts["big_num"])
            draw.text((px + 65, c2_y + 195), right_sub[:45], fill=(160, 220, 255), font=fonts["body"])

            # Verdict strip
            vy = c2_y + 290
            draw.rounded_rectangle([(px + 40, vy), (px + 40 + col_w, vy + 130)], radius=12, fill=(12, 16, 24), outline=cls.ACCENT_GOLD, width=3)
            draw.text((px + 60, vy + 22), "THE SYSTEMIC REALITY:", fill=cls.ACCENT_GOLD, font=fonts["badge"])
            draw.text((px + 60, vy + 65), verdict_summary[:52], fill=cls.TEXT_WHITE, font=fonts["subtitle"])
        else:
            col_w = (panel_w - 140) // 2
            lx = px + 50
            ly = py + 150
            draw.rounded_rectangle([(lx, ly), (lx + col_w, ly + 360)], radius=12, fill=(30, 15, 20), outline=cls.ACCENT_RED, width=2)
            draw.text((lx + 30, ly + 30), left_header.upper(), fill=cls.ACCENT_RED, font=fonts["title"])
            draw.text((lx + 30, ly + 110), left_stat, fill=cls.TEXT_WHITE, font=fonts["big_num"])
            draw.text((lx + 30, ly + 230), left_sub, fill=cls.TEXT_MUTED, font=fonts["subtitle"])

            rx = lx + col_w + 40
            draw.rounded_rectangle([(rx, ly), (rx + col_w, ly + 360)], radius=12, fill=(15, 28, 42), outline=cls.ACCENT_CYAN, width=2)
            draw.text((rx + 30, ly + 30), right_header.upper(), fill=cls.ACCENT_CYAN, font=fonts["title"])
            draw.text((rx + 30, ly + 110), right_stat, fill=cls.ACCENT_GOLD, font=fonts["big_num"])
            draw.text((rx + 30, ly + 230), right_sub, fill=cls.TEXT_MUTED, font=fonts["subtitle"])

            vy = py + 550
            draw.rounded_rectangle([(px + 50, vy), (px + panel_w - 50, vy + 160)], radius=10, fill=(12, 16, 24), outline=cls.ACCENT_GOLD, width=2)
            draw.text((px + 80, vy + 30), "THE SYSTEMIC REALITY:", fill=cls.ACCENT_GOLD, font=fonts["subtitle"])
            draw.text((px + 80, vy + 75), verdict_summary, fill=cls.TEXT_WHITE, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path

    @classmethod
    def create_cliffhanger_card(
        cls,
        part1_title: str,
        part2_teaser: str,
        cliffhanger_hook: str,
        output_path: str,
        is_vertical: bool = False,
    ) -> str:
        """Generate high-retention Part 1 cliffhanger card that compels watching Part 2."""
        w, h = (1080, 1920) if is_vertical else (1920, 1080)
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts(is_vertical=is_vertical)

        panel_w = 980 if is_vertical else 1440
        panel_h = 1260 if is_vertical else 780
        px = (w - panel_w) // 2
        py = 220 if is_vertical else (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=cls.ACCENT_RED, width=3)

        badge_box = [(px + 40, py + 40), (px + 460, py + 95)]
        draw.rounded_rectangle(badge_box, radius=6, fill=cls.ACCENT_RED)
        draw.text((badge_box[0][0] + 20, badge_box[0][1] + 12), "INVESTIGATION IN PROGRESS", fill=cls.TEXT_WHITE, font=fonts["badge"])

        draw.text((px + 40, py + 125), "END OF PART 1: THE TRAP", fill=cls.TEXT_WHITE, font=fonts["headline"])
        draw.text((px + 40, py + 215), f'"{cliffhanger_hook[:42]}"', fill=cls.ACCENT_GOLD, font=fonts["title"])

        # Teaser Card for Part 2
        t_y = py + 340 if not is_vertical else py + 320
        t_h = 360 if not is_vertical else 540
        draw.rounded_rectangle([(px + 40, t_y), (px + panel_w - 40, t_y + t_h)], radius=14, fill=(12, 16, 26), outline=cls.ACCENT_GOLD, width=3)
        draw.text((px + 70, t_y + 40), "NEXT EPISODE: PART 2", fill=cls.ACCENT_GOLD, font=fonts["title"])
        draw.text((px + 70, t_y + 130), part2_teaser.upper()[:36], fill=cls.TEXT_WHITE, font=fonts["headline"])
        draw.text((px + 70, t_y + 260), "WHERE DID THE $470,000,000 GO?", fill=cls.ACCENT_RED, font=fonts["title"])
        draw.text((px + 70, t_y + 360), "TAP CHANNEL OR WATCH PART 2 NOW", fill=cls.ACCENT_CYAN, font=fonts["subtitle"])
        draw.text((px + 70, t_y + 110), part2_teaser.upper()[:36], fill=cls.TEXT_WHITE, font=fonts["title"])
        draw.text((px + 70, t_y + 220), "SWIPE OR CLICK LINK NOW TO WATCH", fill=cls.ACCENT_CYAN, font=fonts["subtitle"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
