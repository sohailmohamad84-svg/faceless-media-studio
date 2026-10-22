"""Cinematic Documentary Visual Engine: 2.5D photo collages, aged newspapers, court dockets, and financial autopsies."""
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
    def _get_fonts(cls):
        """Load crisp system fonts with graceful cross-platform fallbacks."""
        try:
            return {
                "headline": ImageFont.truetype("arialbd.ttf", 60),
                "title": ImageFont.truetype("arialbd.ttf", 46),
                "subtitle": ImageFont.truetype("arial.ttf", 30),
                "body": ImageFont.truetype("arial.ttf", 24),
                "badge": ImageFont.truetype("arialbd.ttf", 26),
                "stamp": ImageFont.truetype("arialbd.ttf", 44),
                "big_num": ImageFont.truetype("arialbd.ttf", 76),
                "mono": ImageFont.truetype("courbd.ttf", 28),
            }
        except Exception:
            try:
                return {
                    "headline": ImageFont.truetype("arial.ttf", 60),
                    "title": ImageFont.truetype("arial.ttf", 46),
                    "subtitle": ImageFont.truetype("arial.ttf", 30),
                    "body": ImageFont.truetype("arial.ttf", 24),
                    "badge": ImageFont.truetype("arial.ttf", 26),
                    "stamp": ImageFont.truetype("arial.ttf", 44),
                    "big_num": ImageFont.truetype("arial.ttf", 76),
                    "mono": ImageFont.truetype("cour.ttf", 28),
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
        for r in range(0, max_r, 20):
            factor = r / max_r
            col = (
                int(cls.DARK_BG[0] * (1.0 - factor * 0.6)),
                int(cls.DARK_BG[1] * (1.0 - factor * 0.6)),
                int(cls.DARK_BG[2] * (1.0 - factor * 0.5)),
            )
            draw.ellipse([(cx - r * 1.5, cy - r), (cx + r * 1.5, cy + r)], outline=col, width=20)

        # Subtle dark border vignette
        draw.rectangle([(0, 0), (w, h)], outline=(5, 7, 10), width=40)
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
    ) -> str:
        """Generate a 2.5D archival photo slide with realistic drop shadow, photo borders, and badges."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        fonts = cls._get_fonts()

        # Load and resize archival photo
        photo_file = Path(photo_path)
        if photo_file.exists():
            raw_photo = Image.open(photo_file).convert("RGB")
        else:
            raw_photo = Image.new("RGB", (1200, 750), (40, 50, 65))
            d = ImageDraw.Draw(raw_photo)
            d.text((400, 350), "[ARCHIVAL EVIDENCE PHOTOGRAPH]", fill=(180, 190, 205), font=fonts["title"])

        # Scale photo nicely to fit in center frame
        target_w, target_h = 1300, 720
        raw_photo = ImageOps.fit(raw_photo, (target_w, target_h), method=Image.Resampling.LANCZOS)

        # Create polaroid / museum matte frame with drop shadow
        frame_pad = 20
        frame_bottom_pad = 50
        frame_w = target_w + frame_pad * 2
        frame_h = target_h + frame_pad + frame_bottom_pad

        frame = Image.new("RGBA", (frame_w, frame_h), (242, 240, 234, 255))
        frame.paste(raw_photo, (frame_pad, frame_pad))

        f_draw = ImageDraw.Draw(frame)
        f_draw.text((frame_pad + 10, frame_h - 40), caption.upper(), fill=(60, 65, 75), font=fonts["body"])

        # Add drop shadow
        pos_x = (w - frame_w) // 2
        pos_y = (h - frame_h) // 2 + 25

        shadow = Image.new("RGBA", (frame_w + 50, frame_h + 50), (0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        img.paste(shadow, (pos_x - 15, pos_y - 10), shadow)
        img.paste(frame, (pos_x, pos_y), frame)

        draw = ImageDraw.Draw(img)

        # Scene Title Banner at top
        draw.text((pos_x, 40), title.upper(), fill=cls.ACCENT_GOLD, font=fonts["title"])

        # Investigative Badge in top right of photo
        badge_box = [(pos_x + frame_w - 320, pos_y - 18), (pos_x + frame_w - 10, pos_y + 26)]
        draw.rounded_rectangle(badge_box, radius=6, fill=cls.ACCENT_RED)
        draw.text((badge_box[0][0] + 18, badge_box[0][1] + 6), badge_text.upper(), fill=cls.TEXT_WHITE, font=fonts["badge"])

        # Red rubber stamp if requested
        if stamp_text:
            stamp_box = [(pos_x + 50, pos_y + frame_h - 130), (pos_x + 460, pos_y + frame_h - 55)]
            draw.rounded_rectangle(stamp_box, radius=8, outline=cls.ACCENT_RED, width=4)
            draw.text((stamp_box[0][0] + 20, stamp_box[0][1] + 10), stamp_text.upper(), fill=cls.ACCENT_RED, font=fonts["stamp"])

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
    ) -> str:
        """Generate high-contrast aged newspaper investigation with glowing yellow highlight."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        fonts = cls._get_fonts()

        paper_w, paper_h = 1420, 780
        px, py = (w - paper_w) // 2, (h - paper_h) // 2 + 30

        # Drop shadow
        shadow = Image.new("RGBA", (paper_w + 50, paper_h + 50), (0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))
        img.paste(shadow, (px - 15, py - 10), shadow)

        # Aged Newsprint Paper
        paper = Image.new("RGBA", (paper_w, paper_h), (245, 241, 230, 255))
        p_draw = ImageDraw.Draw(paper)

        # Masthead
        p_draw.line([(50, 40), (paper_w - 50, 40)], fill=(80, 75, 65), width=3)
        p_draw.text((paper_w // 2 - 250, 50), publication.upper(), fill=(25, 20, 15), font=fonts["headline"])
        p_draw.text((50, 125), date_str.upper(), fill=(100, 95, 85), font=fonts["body"])
        p_draw.text((paper_w - 320, 125), "SPECIAL INVESTIGATION", fill=(100, 95, 85), font=fonts["body"])
        p_draw.line([(50, 155), (paper_w - 50, 155)], fill=(80, 75, 65), width=2)

        # Headline
        p_draw.text((50, 185), headline.upper(), fill=(15, 10, 5), font=fonts["title"])
        p_draw.text((50, 255), subhead, fill=(75, 70, 60), font=fonts["subtitle"])
        p_draw.line([(50, 310), (paper_w - 50, 310)], fill=(180, 175, 165), width=1)

        # Glowing yellow marker box over the investigative punchline
        hl_y = 360
        hl_h = 130
        p_draw.rounded_rectangle([(45, hl_y), (paper_w - 45, hl_y + hl_h)], radius=10, fill=cls.HIGHLIGHT_YELLOW)
        p_draw.text((65, hl_y + 35), f'"{highlighted_claim}"', fill=(10, 8, 4), font=fonts["title"])

        # Context body snippet
        p_draw.text(
            (50, 530),
            "Confidential financial records verify that massive debt obligations stripped the retailer of capital,\n"
            "preventing essential store modernization while tens of millions in advisory fees were extracted annually.",
            fill=(60, 55, 45),
            font=fonts["body"],
        )

        # Red Stamp
        stamp_box = [(paper_w - 380, paper_h - 110), (paper_w - 50, paper_h - 40)]
        p_draw.rounded_rectangle(stamp_box, radius=6, outline=cls.ACCENT_RED, width=3)
        p_draw.text((paper_w - 365, paper_h - 98), investigative_tag.upper(), fill=cls.ACCENT_RED, font=fonts["badge"])

        img.paste(paper, (px, py), paper)

        # Top Title
        draw = ImageDraw.Draw(img)
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
    ) -> str:
        """Generate realistic federal bankruptcy court docket / exhibit scene."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        fonts = cls._get_fonts()

        doc_w, doc_h = 1360, 760
        dx, dy = (w - doc_w) // 2, (h - doc_h) // 2 + 30

        shadow = Image.new("RGBA", (doc_w + 50, doc_h + 50), (0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(16))
        img.paste(shadow, (dx - 15, dy - 10), shadow)

        paper = Image.new("RGBA", (doc_w, doc_h), (250, 248, 242, 255))
        p_draw = ImageDraw.Draw(paper)

        # Federal Court Header
        p_draw.text((doc_w // 2 - 280, 40), court_name.upper(), fill=(20, 20, 20), font=fonts["title"])
        p_draw.line([(50, 105), (doc_w - 50, 105)], fill=(150, 145, 135), width=2)

        # Case No and Docket details
        p_draw.text((60, 125), f"IN RE: TOYS 'R' US, INC., ET AL.", fill=(40, 40, 40), font=fonts["subtitle"])
        p_draw.text((60, 165), f"CASE NO: {case_no} (CHAPTER 11 PROCEEDING)", fill=(80, 80, 80), font=fonts["body"])
        p_draw.text((60, 205), f"DOCKET EXHIBIT: {docket_title.upper()}", fill=(20, 20, 20), font=fonts["subtitle"])
        p_draw.line([(50, 255), (doc_w - 50, 255)], fill=(150, 145, 135), width=1)

        # Highlighted court evidence finding
        hl_y = 295
        hl_h = 140
        p_draw.rounded_rectangle([(50, hl_y), (doc_w - 50, hl_y + hl_h)], radius=8, fill=cls.HIGHLIGHT_YELLOW)
        p_draw.text((70, hl_y + 40), f'"{highlighted_finding}"', fill=(10, 10, 10), font=fonts["title"])

        p_draw.text((60, 480), "EVIDENTIARY AUDIT FINDINGS:", fill=(30, 30, 30), font=fonts["subtitle"])
        p_draw.text((60, 525), "- 33,000 retail store employees terminated without contractual severance pay.", fill=(60, 60, 60), font=fonts["body"])
        p_draw.text((60, 565), "- Wall Street sponsors collected over $470,000,000 in advisory fees and structured dividends.", fill=(60, 60, 60), font=fonts["body"])
        p_draw.text((60, 605), "- Debt servicing absorbed 97% of cumulative operating income prior to petition date.", fill=(60, 60, 60), font=fonts["body"])

        # Rubber Stamp
        stamp_box = [(doc_w - 480, doc_h - 110), (doc_w - 50, doc_h - 40)]
        p_draw.rounded_rectangle(stamp_box, radius=6, outline=cls.ACCENT_RED, width=3)
        p_draw.text((doc_w - 460, doc_h - 96), stamp_text.upper(), fill=cls.ACCENT_RED, font=fonts["badge"])

        img.paste(paper, (dx, dy), paper)

        draw = ImageDraw.Draw(img)
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
    ) -> str:
        """Generate high-contrast Wall Street financial autopsy graphic."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts()

        # Center Slate Panel
        panel_w, panel_h = 1440, 760
        px, py = (w - panel_w) // 2, (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=(40, 52, 75), width=2)

        # Title
        draw.text((px + 50, py + 45), title.upper(), fill=cls.ACCENT_GOLD, font=fonts["headline"])
        draw.line([(px + 50, py + 125), (px + panel_w - 50, py + 125)], fill=(50, 65, 95), width=2)

        # Metric 1 Box (Red / Debt / Blood)
        m1_w = (panel_w - 140) // 2
        m1_x = px + 50
        m1_y = py + 160
        draw.rounded_rectangle([(m1_x, m1_y), (m1_x + m1_w, m1_y + 240)], radius=12, fill=(35, 20, 25), outline=cls.ACCENT_RED, width=3)
        draw.text((m1_x + 30, m1_y + 30), metric_1_label.upper(), fill=cls.TEXT_MUTED, font=fonts["subtitle"])
        draw.text((m1_x + 30, m1_y + 90), metric_1_val, fill=cls.ACCENT_RED, font=fonts["big_num"])

        # Metric 2 Box (Gold / Cash / Contrast)
        m2_x = m1_x + m1_w + 40
        draw.rounded_rectangle([(m2_x, m1_y), (m2_x + m1_w, m1_y + 240)], radius=12, fill=(20, 30, 45), outline=cls.ACCENT_CYAN, width=3)
        draw.text((m2_x + 30, m1_y + 30), metric_2_label.upper(), fill=cls.TEXT_MUTED, font=fonts["subtitle"])
        draw.text((m2_x + 30, m1_y + 90), metric_2_val, fill=cls.ACCENT_CYAN, font=fonts["big_num"])

        # Subtext Bar
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
    ) -> str:
        """Generate high-impact comparison verdict (Workers vs Wall Street)."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts()

        panel_w, panel_h = 1500, 780
        px, py = (w - panel_w) // 2, (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=(45, 58, 80), width=2)
        draw.text((px + 50, py + 40), title.upper(), fill=cls.ACCENT_GOLD, font=fonts["headline"])
        draw.line([(px + 50, py + 120), (px + panel_w - 50, py + 120)], fill=(50, 65, 95), width=2)

        # Left Column: Workers (Red)
        col_w = (panel_w - 140) // 2
        lx = px + 50
        ly = py + 150
        draw.rounded_rectangle([(lx, ly), (lx + col_w, ly + 360)], radius=12, fill=(30, 15, 20), outline=cls.ACCENT_RED, width=2)
        draw.text((lx + 30, ly + 30), left_header.upper(), fill=cls.ACCENT_RED, font=fonts["title"])
        draw.text((lx + 30, ly + 110), left_stat, fill=cls.TEXT_WHITE, font=fonts["big_num"])
        draw.text((lx + 30, ly + 230), left_sub, fill=cls.TEXT_MUTED, font=fonts["subtitle"])

        # Right Column: Wall Street (Cyan / Gold)
        rx = lx + col_w + 40
        draw.rounded_rectangle([(rx, ly), (rx + col_w, ly + 360)], radius=12, fill=(15, 28, 42), outline=cls.ACCENT_CYAN, width=2)
        draw.text((rx + 30, ly + 30), right_header.upper(), fill=cls.ACCENT_CYAN, font=fonts["title"])
        draw.text((rx + 30, ly + 110), right_stat, fill=cls.ACCENT_GOLD, font=fonts["big_num"])
        draw.text((rx + 30, ly + 230), right_sub, fill=cls.TEXT_MUTED, font=fonts["subtitle"])

        # Bottom verdict
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
    ) -> str:
        """Generate high-retention Part 1 cliffhanger card that compels watching Part 2."""
        w, h = 1920, 1080
        img = cls.create_cinematic_backdrop((w, h))
        draw = ImageDraw.Draw(img)
        fonts = cls._get_fonts()

        panel_w, panel_h = 1440, 780
        px, py = (w - panel_w) // 2, (h - panel_h) // 2 + 25

        draw.rounded_rectangle([(px, py), (px + panel_w, py + panel_h)], radius=16, fill=cls.SLATE_BG, outline=cls.ACCENT_RED, width=3)

        # Warning Badge
        badge_box = [(px + 50, py + 45), (px + 420, py + 95)]
        draw.rounded_rectangle(badge_box, radius=6, fill=cls.ACCENT_RED)
        draw.text((px + 65, py + 55), "INVESTIGATION IN PROGRESS", fill=cls.TEXT_WHITE, font=fonts["badge"])

        draw.text((px + 50, py + 120), "END OF PART 1: THE TRAP", fill=cls.TEXT_WHITE, font=fonts["headline"])
        draw.text((px + 50, py + 200), f'"{cliffhanger_hook}"', fill=cls.ACCENT_GOLD, font=fonts["title"])

        # Teaser Card for Part 2
        t_y = py + 340
        draw.rounded_rectangle([(px + 50, t_y), (px + panel_w - 50, t_y + 260)], radius=12, fill=(12, 16, 26), outline=cls.ACCENT_GOLD, width=3)
        draw.text((px + 90, t_y + 35), "NEXT EPISODE: PART 2", fill=cls.ACCENT_GOLD, font=fonts["subtitle"])
        draw.text((px + 90, t_y + 85), part2_teaser.upper(), fill=cls.TEXT_WHITE, font=fonts["headline"])
        draw.text((px + 90, t_y + 175), "CLICK THE ON-SCREEN CARD OR PINNED LINK NOW TO WATCH", fill=cls.ACCENT_CYAN, font=fonts["title"])

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
