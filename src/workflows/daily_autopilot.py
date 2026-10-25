"""Autonomous Daily Production Autopilot: Generates 2 Viral Videos (Part 1 & Part 2) in 1 Click."""
import time
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from config.settings import PROJECTS_DIR, EXPORTS_DIR, DEFAULT_VOICE_ID
from src.database.models import Topic, Script, VideoExport
from src.database.repository import (
    TopicRepository,
    ScriptRepository,
    VideoExportRepository,
    VoiceoverRepository,
    WorkflowRepository,
)
from src.database.models import WorkflowRun, Voiceover
from src.scripting.two_part_generator import TwoPartGenerator
from src.tts.voice_engine import VoiceEngine
from src.assets.chart_generator import ChartGenerator
from src.assets.viral_designer import ViralDesigner
from src.assets.documentary_designer import DocumentaryDesigner
from src.assets.thumbnail_designer import ThumbnailDesigner
from src.editing.viral_engine import ViralEngine
from src.youtube.uploader import YouTubePublisher


class DailyAutopilot:
    @classmethod
    def produce_daily_shorts_batch(cls, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """Produce 2 vertical YouTube Shorts (<60s) in the authentic MagnatesMedia documentary aesthetic:
        - 1080x1920 vertical framing
        - Rapid-fire 4-6s scene cuts
        - Real archival imagery, court exhibits, and aged newspapers with glowing highlights
        - 35mm temporal film grain, optical vignette, and contrast color grading
        - Kinetic gold-and-black subtitle popups in the mobile center sweet spot
        - Exact multi-track Foley sound design (sub-bass boom, shutter clicks, paper rustles, stamp thuds)
        """
        start_time = time.time()
        topics = TopicRepository.list_topics()

        if topic_id:
            topic = TopicRepository.get_topic(topic_id)
        else:
            topic = next((t for t in topics if "Toys" in t.title), None)
            if not topic:
                topic = topics[0] if topics else None

        if not topic:
            return {"success": False, "error": "No topics found in library."}

        # Step 1: Generate Two-Part Shorts Scripts (<60s each)
        (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims) = (
            TwoPartGenerator.generate_two_part_series(topic, is_shorts=True)
        )

        ve = VoiceEngine(voice_id=DEFAULT_VOICE_ID)
        engine = ViralEngine()

        # ======================================================================
        # BUILD SHORTS PART 1: THE TRAP & CLIFFHANGER (~49s, 1080x1920)
        # ======================================================================
        p1_dir = PROJECTS_DIR / f"shorts_{p1_script.id}_part1"
        p1_dir.mkdir(parents=True, exist_ok=True)

        p1_vo_path = str(p1_dir / "voiceover.mp3")
        p1_text = f"{p1_script.hook_text} {p1_script.promise_text} {p1_script.body_text} {p1_script.conclusion_text}"
        ve.synthesize(p1_text, p1_vo_path, rate="+20%")

        vo1 = Voiceover(script_id=p1_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p1_vo_path)
        VoiceoverRepository.add_voiceover(vo1)

        p1_images = []
        p1_thumb = str(p1_dir / "thumbnail_shorts_part1.jpg")

        # 9 Vertical Scenes for Part 1
        s1 = str(p1_dir / "scene01_monopoly.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/store_exterior.jpg",
            title="THE 20% MONOPOLY",
            caption="1,600 STORES & 20% OF TOY INDUSTRY",
            badge_text="PEAK MONOPOLY",
            stamp_text="ORIGINAL TITAN",
            output_path=s1,
            is_vertical=True,
        )
        p1_images.append(s1)

        s2 = str(p1_dir / "scene02_bulldozed.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/abandoned_empty_store.jpg",
            title="BULLDOZED & CLOSED",
            caption="18 YEARS LATER: EVERY STORE GONE",
            badge_text="CRIME SCENE",
            stamp_text="LIQUIDATED & CLOSED",
            output_path=s2,
            is_vertical=True,
        )
        p1_images.append(s2)

        s3 = str(p1_dir / "scene03_amazon_lie.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="THE WALL STREET CHRONICLE",
            headline="THE LIE ABOUT AMAZON",
            subhead="How Wall Street Fabricated A Scapegoat",
            highlighted_claim="AMAZON DID NOT KILL TOYS 'R' US",
            date_str="SPECIAL REPORT",
            output_path=s3,
            investigative_tag="DEBUNKED",
            is_vertical=True,
        )
        p1_images.append(s3)

        s4 = str(p1_dir / "scene04_heist_docket.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="U.S. SECURITIES & EXCHANGE COMMISSION",
            case_no="SEC-LBO-2005",
            docket_title="THE $6.6 BILLION TAKEOVER",
            highlighted_finding="CONFIDENTIAL MERGER DOCKET: $6.6B HEIST",
            output_path=s4,
            stamp_text="WALL STREET HEIST",
            is_vertical=True,
        )
        p1_images.append(s4)

        s5 = str(p1_dir / "scene05_syndicate.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/bain_capital_logo.png",
            title="THE BUYOUT SYNDICATE",
            caption="BAIN CAPITAL, KKR & VORNADO",
            badge_text="THE SYNDICATE",
            stamp_text="$6.6B TAKEOVER",
            output_path=s5,
            is_vertical=True,
        )
        p1_images.append(s5)

        s6 = str(p1_dir / "scene06_borrowed_debt.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="BORROWED DEBT TRAP",
            metric_1_label="BORROWED ON TOYS R US",
            metric_1_val="$5,300,000,000",
            metric_2_label="CASH BUYERS PUT DOWN",
            metric_2_val="ONLY 20% CASH",
            subtext="BUYERS USED TOYS 'R' US'S OWN STORES AS COLLATERAL",
            output_path=s6,
            is_vertical=True,
        )
        p1_images.append(s6)

        s7 = str(p1_dir / "scene07_bleed.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="THE $400M ANNUAL BLEED",
            metric_1_label="ANNUAL INTEREST PAID",
            metric_1_val="$400,000,000/YR",
            metric_2_label="OPERATING PROFITS",
            metric_2_val="97% WIPED OUT",
            subtext="EVERY DOLLAR SENT DIRECTLY TO WALL STREET BANKS",
            output_path=s7,
            is_vertical=True,
        )
        p1_images.append(s7)

        s8 = str(p1_dir / "scene08_zero_capital.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/airport_store.jpg",
            title="ZERO CAPITAL FOR STORES",
            caption="NO FUNDS TO FIX ROOFS, AIR CONDITIONING OR SITES",
            badge_text="DECAYING STORES",
            stamp_text="CAPITAL STARVED",
            output_path=s8,
            is_vertical=True,
        )
        p1_images.append(s8)

        s9 = str(p1_dir / "scene09_cliffhanger.png")
        DocumentaryDesigner.create_cliffhanger_card(
            part1_title="THE $6.6B DEBT TRAP",
            part2_teaser="WHERE THE $470M ACTUALLY WENT",
            cliffhanger_hook="WATCH PART 2: THE AUTOPSY",
            output_path=s9,
            is_vertical=True,
        )
        p1_images.append(s9)

        ThumbnailDesigner.create_thumbnail(
            title_top="WHY TOYS R US DIED",
            title_bottom="IT WASN'T AMAZON",
            badge_text="PART 1 #Shorts",
            output_path=p1_thumb,
        )

        p1_mp4 = str(EXPORTS_DIR / f"Viral_Shorts_{topic.id}_Part1.mp4")
        p1_res = engine.assemble_viral_video(
            script_id=p1_script.id,
            scenes=p1_scenes,
            scene_images=p1_images,
            narration_audio_path=p1_vo_path,
            output_mp4_path=p1_mp4,
            thumbnail_path=p1_thumb,
            is_shorts=True,
        )

        # ======================================================================
        # BUILD SHORTS PART 2: THE AUTOPSY & THE FINAL VERDICT (~47s, 1080x1920)
        # ======================================================================
        p2_dir = PROJECTS_DIR / f"shorts_{p2_script.id}_part2"
        p2_dir.mkdir(parents=True, exist_ok=True)

        p2_vo_path = str(p2_dir / "voiceover.mp3")
        p2_text = f"{p2_script.hook_text} {p2_script.promise_text} {p2_script.body_text} {p2_script.conclusion_text}"
        ve.synthesize(p2_text, p2_vo_path, rate="+20%")

        vo2 = Voiceover(script_id=p2_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p2_vo_path)
        VoiceoverRepository.add_voiceover(vo2)

        p2_images = []
        p2_thumb = str(p2_dir / "thumbnail_shorts_part2.jpg")

        # 8 Vertical Scenes for Part 2
        p2_s1 = str(p2_dir / "scene01_ch11_docket.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="UNITED STATES BANKRUPTCY COURT",
            case_no="CASE NO. 17-34665",
            docket_title="CHAPTER 11 BANKRUPTCY PETITION",
            highlighted_finding="PETITION DATE: SEPT 2017 — $7.9B TOTAL DEBT",
            output_path=p2_s1,
            stamp_text="CHAPTER 11",
            is_vertical=True,
        )
        p2_images.append(p2_s1)

        p2_s2 = str(p2_dir / "scene02_workers_vs_wallst.png")
        DocumentaryDesigner.create_split_verdict_scene(
            title="THE BRUTAL REALITY",
            left_header="33,000 WORKERS",
            left_stat="$0 SEVERANCE",
            left_sub="TERMINATED WITHOUT A DIME",
            right_header="PRIVATE EQUITY FIRMS",
            right_stat="$470,000,000",
            right_sub="EXTRACTED IN ADVISORY FEES",
            verdict_summary="WALL STREET WALKED AWAY WITH CASH WHILE WORKERS CARRIED THE FALL",
            output_path=p2_s2,
            is_vertical=True,
        )
        p2_images.append(p2_s2)

        p2_s3 = str(p2_dir / "scene03_where_cash_went.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="THE 12-YEAR BLEED",
            metric_1_label="ANNUAL INTEREST EXPENSE",
            metric_1_val="$400,000,000/YR",
            metric_2_label="INNOVATION CAPITAL",
            metric_2_val="$0 FOR TECH",
            subtext="97% OF OPERATING CASH DRAINED BY LBO DEBT",
            output_path=p2_s3,
            is_vertical=True,
        )
        p2_images.append(p2_s3)

        p2_s4 = str(p2_dir / "scene04_amazon_pact.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="THE WALL STREET JOURNAL",
            headline="THE FATAL AMAZON PACT",
            subhead="Toys 'R' Us Signed 10-Year Exclusive Deal in 2000",
            highlighted_claim="OUTSOURCING DIGITAL FUTURE TO AMAZON",
            date_str="YEAR 2000 PACT",
            output_path=p2_s4,
            investigative_tag="DIGITAL SUICIDE",
            is_vertical=True,
        )
        p2_images.append(p2_s4)

        p2_s5 = str(p2_dir / "scene05_trojan_horse.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="RETAIL TECH INVESTIGATION",
            headline="AMAZON'S TROJAN HORSE",
            subhead="Amazon Used Customer Buying Data To Undercut Toys 'R' Us",
            highlighted_claim="THIRD-PARTY SELLERS UNDERMINED TOYS 'R' US",
            date_str="DATA EXPLOITATION",
            output_path=p2_s5,
            investigative_tag="TROJAN HORSE",
            is_vertical=True,
        )
        p2_images.append(p2_s5)

        p2_s6 = str(p2_dir / "scene06_supplier_panic.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/store_exterior.jpg",
            title="SUPPLIERS PULL CREDIT",
            caption="MANUFACTURERS REFUSED TO SHIP CHRISTMAS TOYS",
            badge_text="SEPTEMBER 2017",
            stamp_text="CREDIT FREEZE",
            output_path=p2_s6,
            is_vertical=True,
        )
        p2_images.append(p2_s6)

        p2_s7 = str(p2_dir / "scene07_liquidation.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/abandoned_empty_store.jpg",
            title="TOTAL LIQUIDATION",
            caption="STORES STRIPPED TO THE BARE METAL",
            badge_text="BANKRUPTCY AUCTION",
            stamp_text="STORE CLOSING",
            output_path=p2_s7,
            is_vertical=True,
        )
        p2_images.append(p2_s7)

        p2_s8 = str(p2_dir / "scene08_verdict.png")
        DocumentaryDesigner.create_split_verdict_scene(
            title="THE FINAL AUTOPSY VERDICT",
            left_header="KILLED BY DEBT",
            left_stat="NOT AMAZON",
            left_sub="FINANCIAL ENGINEERING AUTOPSY",
            right_header="APEX ENTERPRISE",
            right_stat="SUBSCRIBE",
            right_sub="FOR FORENSIC AUTOPSIES",
            verdict_summary="SUBSCRIBE TO APEX ENTERPRISE FOR UNCOMPROMISING INVESTIGATIONS",
            output_path=p2_s8,
            is_vertical=True,
        )
        p2_images.append(p2_s8)

        ThumbnailDesigner.create_thumbnail(
            title_top="THE FINAL AUTOPSY",
            title_bottom="WHERE THE MONEY WENT",
            badge_text="PART 2 #Shorts",
            output_path=p2_thumb,
        )

        p2_mp4 = str(EXPORTS_DIR / f"Viral_Shorts_{topic.id}_Part2.mp4")
        p2_res = engine.assemble_viral_video(
            script_id=p2_script.id,
            scenes=p2_scenes,
            scene_images=p2_images,
            narration_audio_path=p2_vo_path,
            output_mp4_path=p2_mp4,
            thumbnail_path=p2_thumb,
            is_shorts=True,
        )

        total_duration = round(time.time() - start_time, 2)

        # Log Workflow Run
        summary_msg = f"Produced 2-Part MagnatesMedia YouTube Shorts for '{topic.title}' in {total_duration}s."
        WorkflowRepository.log_run(
            WorkflowRun(
                workflow_name="Daily YouTube Shorts Autopilot",
                status="success",
                summary=summary_msg,
                duration_sec=total_duration,
            )
        )

        return {
            "success": True,
            "topic": topic,
            "is_shorts": True,
            "total_render_time_sec": total_duration,
            "part1": {
                "script_id": p1_script.id,
                "video_export_id": p1_res.get("video_export_id"),
                "mp4_path": p1_mp4,
                "thumbnail_path": p1_thumb,
                "duration_sec": p1_res.get("duration_sec"),
                "content_hash": p1_res.get("content_hash"),
                "title": p1_script.title,
            },
            "part2": {
                "script_id": p2_script.id,
                "video_export_id": p2_res.get("video_export_id"),
                "mp4_path": p2_mp4,
                "thumbnail_path": p2_thumb,
                "duration_sec": p2_res.get("duration_sec"),
                "content_hash": p2_res.get("content_hash"),
                "title": p2_script.title,
            },
        }

    @classmethod
    def produce_daily_two_part_batch(cls, topic_id: Optional[int] = None) -> Dict[str, Any]:
        """Produce 2 complete, high-retention viral videos (Part 1 & Part 2) with zero manual hassle.
        - Part 1: The Setup & The Fatal Trap (ends on a cliffhanger)
        - Part 2: The Autopsy & The Shocking Resolution
        """
        start_time = time.time()
        topics = TopicRepository.list_topics()

        # Select topic
        if topic_id:
            topic = TopicRepository.get_topic(topic_id)
        else:
            # Pick highest scored backlog topic, prioritizing Toys 'R' Us or Costco
            topic = next((t for t in topics if "Toys" in t.title), None)
            if not topic:
                topic = next((t for t in topics if "Costco" in t.title), topics[0] if topics else None)

        if not topic:
            return {"success": False, "error": "No topics found in library."}

        # Step 1: Generate Two-Part Linked Script Series
        (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims) = (
            TwoPartGenerator.generate_two_part_series(topic)
        )

        ve = VoiceEngine(voice_id=DEFAULT_VOICE_ID)
        engine = ViralEngine()

        # ======================================================================
        # BUILD PART 1: THE TRAP & CLIFFHANGER
        # ======================================================================
        p1_dir = PROJECTS_DIR / f"series_{p1_script.id}_part1"
        p1_dir.mkdir(parents=True, exist_ok=True)

        # 1. Voiceover for Part 1
        p1_vo_path = str(p1_dir / "voiceover.mp3")
        p1_text = f"{p1_script.hook_text} {p1_script.promise_text} {p1_script.body_text} {p1_script.conclusion_text}"
        ve.synthesize(p1_text, p1_vo_path, rate="+20%")

        vo1 = Voiceover(script_id=p1_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p1_vo_path)
        VoiceoverRepository.add_voiceover(vo1)

        # 2. Visuals for Part 1 (14 High-Density Documentary Scenes)
        p1_images = []
        p1_thumb = str(p1_dir / "thumbnail_part1.jpg")

        # Slide 1: Peak Monopoly Hero Archival Photo
        s1 = str(p1_dir / "scene01_monopoly.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/store_exterior.jpg",
            title="THE UNTOUCHABLE MONOPOLY",
            caption="1,600 STORES & 20% OF US TOY INDUSTRY (CIRCA 2000)",
            badge_text="20% MONOPOLY",
            stamp_text="ORIGINAL TITAN",
            output_path=s1,
        )
        p1_images.append(s1)

        # Slide 2: Bulldozed Empire Archival Photo
        s2 = str(p1_dir / "scene02_bulldozed.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/abandoned_empty_store.jpg",
            title="THE BULLDOZED EMPIRE",
            caption="TOTAL LIQUIDATION: 18 YEARS LATER",
            badge_text="CRIME SCENE",
            stamp_text="LIQUIDATED & CLOSED",
            output_path=s2,
        )
        p1_images.append(s2)

        # Slide 3: The Amazon Lie Newspaper
        s3 = str(p1_dir / "scene03_amazon_lie.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="THE WALL STREET CHRONICLE",
            headline="THE COVER STORY DEBUNKED",
            subhead="How Wall Street Fabricated A Scapegoat",
            highlighted_claim="AMAZON DID NOT KILL TOYS 'R' US",
            date_str="SPECIAL INVESTIGATION",
            output_path=s3,
            investigative_tag="DEBUNKED",
        )
        p1_images.append(s3)

        # Slide 4: $6.6B Heist Evidence Docket
        s4 = str(p1_dir / "scene04_heist_docket.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="U.S. SECURITIES & EXCHANGE COMMISSION",
            case_no="SEC-LBO-2005",
            docket_title="THE $6.6 BILLION TAKEOVER AGREEMENT",
            highlighted_finding="CONFIDENTIAL MERGER FILING: $6.6B BUYOUT AGREEMENT",
            output_path=s4,
            stamp_text="CONFIDENTIAL EVIDENCE",
        )
        p1_images.append(s4)

        # Slide 5: Category Killer Origin Archival Photo
        s5 = str(p1_dir / "scene05_origin.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/airport_store.jpg",
            title="PIONEER OF THE CATEGORY KILLER",
            caption="FOUNDED 1948 BY CHARLES LAZARUS — 25% LOWER PRICES",
            badge_text="1948 ORIGIN",
            stamp_text="CATEGORY KILLER",
            output_path=s5,
        )
        p1_images.append(s5)

        # Slide 6: Cash Printing Engine Financial Autopsy
        s6 = str(p1_dir / "scene06_cash_engine.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="THE CASH PRINTING ENGINE (PEAK)",
            metric_1_label="PEAK GLOBAL REVENUE",
            metric_1_val="$11.2 BILLION",
            metric_2_label="ANNUAL NET PROFIT",
            metric_2_val="$500,000,000",
            subtext="TOY SUPPLIERS BOWED TO TOYS 'R' US FOR CHRISTMAS DISTRIBUTION",
            output_path=s6,
        )
        p1_images.append(s6)

        # Slide 7: Walmart Price War Newspaper
        s7 = str(p1_dir / "scene07_walmart_ambush.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="RETAIL PRICE WAR ARCHIVE",
            headline="WALMART LAUNCHES PREDATORY AMBUSH",
            subhead="Top 20 Bestselling Toys Sold At A Cash Loss",
            highlighted_claim="SELLING TOYS AT A LOSS TO DESTROY COMPETITORS",
            date_str="DECEMBER 2004",
            output_path=s7,
            investigative_tag="PRICE WAR",
        )
        p1_images.append(s7)

        # Slide 8: Stock Market Panic Archival Photo
        s8 = str(p1_dir / "scene08_stock_panic.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/wall_street_nyse.jpg",
            title="THE STOCK MARKET PANIC",
            caption="NEW YORK STOCK EXCHANGE — EQUITY PLUMMETS 50%",
            badge_text="WALL STREET CIRCLING",
            stamp_text="-50% CRASH",
            output_path=s8,
        )
        p1_images.append(s8)

        # Slide 9: Private Equity Syndicate Archival Photo
        s9 = str(p1_dir / "scene09_syndicate.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/bain_capital_logo.png",
            title="THE PRIVATE EQUITY SYNDICATE",
            caption="BAIN CAPITAL, KKR & VORNADO TEAM UP FOR $6.6B TAKEOVER",
            badge_text="THE SYNDICATE",
            stamp_text="$6.6B TAKEOVER",
            output_path=s9,
        )
        p1_images.append(s9)

        # Slide 10: LBO Mechanism Financial Autopsy
        s10 = str(p1_dir / "scene10_lbo_trap.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="THE LEVERAGED BUYOUT MECHANISM",
            metric_1_label="BUYERS PUT DOWN (20%)",
            metric_1_val="$1.3 BILLION CASH",
            metric_2_label="BORROWED DEBT (80%)",
            metric_2_val="$5.3 BILLION DEBT",
            subtext="BUYERS FORCED TOYS 'R' US'S OWN STORES TO SERVE AS COLLATERAL",
            output_path=s10,
        )
        p1_images.append(s10)

        # Slide 11: Borrowed Against Own Stores Docket
        s11 = str(p1_dir / "scene11_borrowed_debt.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="U.S. SECURITIES & EXCHANGE COMMISSION",
            case_no="FORM-8K-MERGER",
            docket_title="CREDIT SYNDICATION AGREEMENT",
            highlighted_finding="DEBT ENCUMBERING ALL STORES & INVENTORY: $5,300,000,000",
            output_path=s11,
            stamp_text="ENCUMBERED DEBT",
        )
        p1_images.append(s11)

        # Slide 12: $400M Annual Bleed Financial Autopsy
        s12 = str(p1_dir / "scene12_bleed.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="THE $400M ANNUAL BLEED",
            metric_1_label="ANNUAL INTEREST PAYMENT",
            metric_1_val="$400,000,000/YR",
            metric_2_label="OPERATING PROFIT WIPED",
            metric_2_val="97% OF PROFITS",
            subtext="EVERY DOLLAR EARNED SENT DIRECTLY TO WALL STREET BANKS",
            output_path=s12,
        )
        p1_images.append(s12)

        # Slide 13: Winter 2017 Collapse Archival Photo
        s13 = str(p1_dir / "scene13_winter2017.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/corporate_hq.jpg",
            title="DECEMBER 2017: THE TRAP SNAPS",
            caption="HEADQUARTERS PARALYZED AS SUPPLIERS HALT CREDIT",
            badge_text="DECEMBER 2017",
            stamp_text="THE TRAP SNAPS",
            output_path=s13,
        )
        p1_images.append(s13)

        # Slide 14: Cliffhanger Card
        s14 = str(p1_dir / "scene14_cliffhanger.png")
        DocumentaryDesigner.create_cliffhanger_card(
            part1_title="THE $6.6 BILLION WALL STREET HEIST",
            part2_teaser="THE $470M LOOTING & CHAPTER 11 AUTOPSY",
            cliffhanger_hook="WHERE DID THE BILLIONS ACTUALLY GO?",
            output_path=s14,
        )
        p1_images.append(s14)

        ThumbnailDesigner.create_thumbnail(
            title_top="WHY TOYS R US DIED",
            title_bottom="IT WASN'T AMAZON",
            badge_text="PART 1: THE TRAP",
            output_path=p1_thumb,
        )

        p1_mp4 = str(EXPORTS_DIR / f"Viral_Daily_{topic.id}_Part1.mp4")
        p1_res = engine.assemble_viral_video(
            script_id=p1_script.id,
            scenes=p1_scenes,
            scene_images=p1_images,
            narration_audio_path=p1_vo_path,
            output_mp4_path=p1_mp4,
            thumbnail_path=p1_thumb,
        )

        # ======================================================================
        # BUILD PART 2: THE AUTOPSY & THE FINAL VERDICT (14 High-Density Scenes)
        # ======================================================================
        p2_dir = PROJECTS_DIR / f"series_{p2_script.id}_part2"
        p2_dir.mkdir(parents=True, exist_ok=True)

        # 1. Voiceover for Part 2
        p2_vo_path = str(p2_dir / "voiceover.mp3")
        p2_text = f"{p2_script.hook_text} {p2_script.promise_text} {p2_script.body_text} {p2_script.conclusion_text}"
        ve.synthesize(p2_text, p2_vo_path, rate="+20%")

        vo2 = Voiceover(script_id=p2_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p2_vo_path)
        VoiceoverRepository.add_voiceover(vo2)

        # 2. Visuals for Part 2 (14 High-Density Documentary Scenes)
        p2_images = []
        p2_thumb = str(p2_dir / "thumbnail_part2.jpg")

        # Slide 1: Chapter 11 Court Docket
        p2_s1 = str(p2_dir / "scene01_ch11_docket.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="UNITED STATES BANKRUPTCY COURT",
            case_no="CASE NO. 17-34665",
            docket_title="CHAPTER 11 BANKRUPTCY PETITION",
            highlighted_finding="PETITION DATE: SEPTEMBER 18, 2017 — TOTAL DEBT: $7.9 BILLION",
            output_path=p2_s1,
            stamp_text="CHAPTER 11 PETITION",
        )
        p2_images.append(p2_s1)

        # Slide 2: Workers vs Wall Street Split Verdict
        p2_s2 = str(p2_dir / "scene02_workers_vs_wallst.png")
        DocumentaryDesigner.create_split_verdict_scene(
            title="THE BRUTAL REALITY",
            left_header="33,000 WORKERS",
            left_stat="$0 SEVERANCE",
            left_sub="TERMINATED WITHOUT A DIME",
            right_header="WALL STREET SPONSORS",
            right_stat="$470,000,000",
            right_sub="EXTRACTED IN ADVISORY FEES",
            verdict_summary="WALL STREET WALKED AWAY WITH CASH WHILE WORKERS WERE LEFT EMPTY-HANDED",
            output_path=p2_s2,
        )
        p2_images.append(p2_s2)

        # Slide 3: Where Did Cash Go Financial Autopsy
        p2_s3 = str(p2_dir / "scene03_where_cash_went.png")
        DocumentaryDesigner.create_financial_autopsy_graphic(
            title="WHERE DID $5 BILLION GO?",
            metric_1_label="ANNUAL INTEREST PAID",
            metric_1_val="$400,000,000/YR",
            metric_2_label="CAPITAL LEFT FOR STORES",
            metric_2_val="$0 FOR UPGRADES",
            subtext="97% OF OPERATING CASH SACRIFICED TO SERVICE SENIOR LBO DEBT",
            output_path=p2_s3,
        )
        p2_images.append(p2_s3)

        # Slide 4: Modern Retail Arms Race Archival Photo
        p2_s4 = str(p2_dir / "scene04_arms_race.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/store_exterior.jpg",
            title="THE MODERN RETAIL ARMS RACE",
            caption="AMAZON & TARGET SPENT BILLIONS ON AUTOMATION & SAME-DAY DELIVERY",
            badge_text="RETAIL EVOLUTION",
            stamp_text="E-COMMERCE BOOM",
            output_path=p2_s4,
        )
        p2_images.append(p2_s4)

        # Slide 5: Decaying Stores Archival Photo
        p2_s5 = str(p2_dir / "scene05_decaying_stores.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/abandoned_empty_store.jpg",
            title="DECAYING STORE INFRASTRUCTURE",
            caption="ZERO CAPITAL LEFT TO FIX AIR CONDITIONING, CEILINGS OR CASH REGISTERS",
            badge_text="CAPITAL STARVATION",
            stamp_text="DECAYING STORES",
            output_path=p2_s5,
        )
        p2_images.append(p2_s5)

        # Slide 6: Fatal Amazon Deal Newspaper
        p2_s6 = str(p2_dir / "scene06_amazon_pact.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="THE WALL STREET JOURNAL",
            headline="THE FATAL 10-YEAR AMAZON PACT",
            subhead="Toys 'R' Us Signed Exclusive E-Commerce Contract in 2000",
            highlighted_claim="OUTSOURCING ENTIRE DIGITAL FUTURE TO DIRECT COMPETITOR",
            date_str="AUGUST 2000 ARCHIVE",
            output_path=p2_s6,
            investigative_tag="DIGITAL SUICIDE",
        )
        p2_images.append(p2_s6)

        # Slide 7: Amazon Trojan Horse Newspaper
        p2_s7 = str(p2_dir / "scene07_trojan_horse.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="RETAIL TECH INVESTIGATION",
            headline="AMAZON'S DIGITAL TROJAN HORSE",
            subhead="Amazon Leveraged Toy Buying Data To Allow 3rd-Party Merchants",
            highlighted_claim="THIRD-PARTY SELLERS UNDERMINED TOYS 'R' US ON AMAZON",
            date_str="SPECIAL REPORT",
            output_path=p2_s7,
            investigative_tag="TROJAN HORSE",
        )
        p2_images.append(p2_s7)

        # Slide 8: Court Lawsuit Victory Docket
        p2_s8 = str(p2_dir / "scene08_lawsuit_docket.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="SUPERIOR COURT OF NEW JERSEY",
            case_no="DOCKET NO. C-00055-04",
            docket_title="TOYS 'R' US v. AMAZON.COM",
            highlighted_finding="COURT ORDERS AMAZON TO PAY $51 MILLION FOR BREACH OF CONTRACT",
            output_path=p2_s8,
            stamp_text="$51M LAWSUIT WON",
        )
        p2_images.append(p2_s8)

        # Slide 9: Supplier Credit Panic Newspaper
        p2_s9 = str(p2_dir / "scene09_supplier_panic.png")
        DocumentaryDesigner.create_newspaper_investigation_scene(
            publication="BLOOMBERG MARKETS",
            headline="SUPPLIERS PULL HOLIDAY CREDIT",
            subhead="Toy Manufacturers Demand Upfront Cash Before Shipping Christmas Toys",
            highlighted_claim="CREDIT INSURERS CANCEL TOYS 'R' US COVERAGE IN SEPTEMBER 2017",
            date_str="SEPTEMBER 2017",
            output_path=p2_s9,
            investigative_tag="CREDIT CRASH",
        )
        p2_images.append(p2_s9)

        # Slide 10: Total Liquidation Archival Photo
        p2_s10 = str(p2_dir / "scene10_liquidation.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/airport_store.jpg",
            title="CHAPTER 11: TOTAL LIQUIDATION",
            caption="EVERY STORE ORDERED CLOSED — FIXTURES AND INVENTORY STRIPPED",
            badge_text="TOTAL LIQUIDATION",
            stamp_text="GOING OUT OF BUSINESS",
            output_path=p2_s10,
        )
        p2_images.append(p2_s10)

        # Slide 11: Human Cost vs Wall Street Split Verdict
        p2_s11 = str(p2_dir / "scene11_human_cost.png")
        DocumentaryDesigner.create_split_verdict_scene(
            title="THE SYSTEMIC SACRIFICE",
            left_header="33,000 EMPLOYEES",
            left_stat="$0 SEVERANCE",
            left_sub="PENSIONS & LIVELIHOODS WIPED OUT",
            right_header="SPONSOR DIVIDENDS",
            right_stat="$470,000,000",
            right_sub="TOTAL MANAGEMENT FEES EXTRACTED",
            verdict_summary="FINANCIAL ENGINEERING PROTECTED INVESTORS WHILE EMPLOYEES CARRIED THE FALL",
            output_path=p2_s11,
        )
        p2_images.append(p2_s11)

        # Slide 12: Final Forensic Truth Archival Photo
        p2_s12 = str(p2_dir / "scene12_final_truth.png")
        DocumentaryDesigner.create_archival_photo_scene(
            photo_path="data/assets/toys_r_us/corporate_hq.jpg",
            title="THE FORENSIC AUTOPSY TRUTH",
            caption="KILLED BY DEBT ENGINEERING, NOT BY CHANGING CONSUMER DEMAND",
            badge_text="AUTOPSY VERDICT",
            stamp_text="KILLED BY DEBT",
            output_path=p2_s12,
        )
        p2_images.append(p2_s12)

        # Slide 13: Case Closed Court Decree
        p2_s13 = str(p2_dir / "scene13_case_closed.png")
        DocumentaryDesigner.create_court_docket_scene(
            court_name="UNITED STATES BANKRUPTCY COURT",
            case_no="CASE CLOSURE DOCKET",
            docket_title="FINAL DECREE & POST-MORTEM VERDICT",
            highlighted_finding="THE COLLAPSE WAS DRIVEN PRIMARILY BY INSUPPORTABLE LBO DEBT LEVERAGE",
            output_path=p2_s13,
            stamp_text="CASE CLOSED",
        )
        p2_images.append(p2_s13)

        # Slide 14: Subscribe & Engagement Card
        p2_s14 = str(p2_dir / "scene14_subscribe.png")
        DocumentaryDesigner.create_split_verdict_scene(
            title="APEX ENTERPRISE FORENSICS",
            left_header="SUBSCRIBE FOR MORE",
            left_stat="WEEKLY",
            left_sub="DEEP CORPORATE AUTOPSIES",
            right_header="JOIN THE DEBATE",
            right_stat="COMMENT",
            right_sub="WHAT COMPANY IS NEXT?",
            verdict_summary="SUBSCRIBE TO APEX ENTERPRISE FOR UNCOMPROMISING BUSINESS INVESTIGATIONS",
            output_path=p2_s14,
        )
        p2_images.append(p2_s14)

        ThumbnailDesigner.create_thumbnail(
            title_top="THE FINAL AUTOPSY",
            title_bottom="WHERE THE MONEY WENT",
            badge_text="PART 2: THE VERDICT",
            output_path=p2_thumb,
        )

        p2_mp4 = str(EXPORTS_DIR / f"Viral_Daily_{topic.id}_Part2.mp4")
        p2_res = engine.assemble_viral_video(
            script_id=p2_script.id,
            scenes=p2_scenes,
            scene_images=p2_images,
            narration_audio_path=p2_vo_path,
            output_mp4_path=p2_mp4,
            thumbnail_path=p2_thumb,
        )

        total_duration = round(time.time() - start_time, 2)

        # Log Workflow Run
        summary_msg = f"Produced 2-Part Viral Series for '{topic.title}' in {total_duration}s."
        WorkflowRepository.log_run(
            WorkflowRun(
                workflow_name="Daily 2-Video Viral Autopilot",
                status="success",
                summary=summary_msg,
                duration_sec=total_duration,
            )
        )

        return {
            "success": True,
            "topic": topic,
            "total_render_time_sec": total_duration,
            "part1": {
                "script_id": p1_script.id,
                "video_export_id": p1_res.get("video_export_id"),
                "mp4_path": p1_mp4,
                "thumbnail_path": p1_thumb,
                "duration_sec": p1_res.get("duration_sec"),
                "content_hash": p1_res.get("content_hash"),
                "title": p1_script.title,
            },
            "part2": {
                "script_id": p2_script.id,
                "video_export_id": p2_res.get("video_export_id"),
                "mp4_path": p2_mp4,
                "thumbnail_path": p2_thumb,
                "duration_sec": p2_res.get("duration_sec"),
                "content_hash": p2_res.get("content_hash"),
                "title": p2_script.title,
            },
        }
