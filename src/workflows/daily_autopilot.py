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
from src.assets.thumbnail_designer import ThumbnailDesigner
from src.editing.viral_engine import ViralEngine
from src.youtube.uploader import YouTubePublisher


class DailyAutopilot:
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
        ve.synthesize(p1_text, p1_vo_path)

        vo1 = Voiceover(script_id=p1_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p1_vo_path)
        VoiceoverRepository.add_voiceover(vo1)

        # 2. Visuals for Part 1 (Newspaper + Chart + SEC Document + Cliffhanger)
        p1_slide1 = str(p1_dir / "scene1_headline.png")
        p1_slide2 = str(p1_dir / "scene2_chart.png")
        p1_slide3 = str(p1_dir / "scene3_sec_doc.png")
        p1_slide4 = str(p1_dir / "scene4_cliffhanger.png")
        p1_thumb = str(p1_dir / "thumbnail_part1.jpg")

        ViralDesigner.create_headline_scene(
            title="THE LIE ABOUT AMAZON",
            news_outlet="THE WALL STREET INVESTIGATION",
            headline_text="HOW A $6.6B DEBT TRAP DESTROYED AN ICON",
            date_str="SPECIAL ARCHIVE REPORT",
            output_path=p1_slide1,
        )
        ChartGenerator.generate_costco_markup_chart(p1_slide2)
        ViralDesigner.create_document_highlight_scene(
            title="FORM 8-K: THE $5.3 BILLION DEBT SYNDICATE",
            doc_header="U.S. SECURITIES AND EXCHANGE COMMISSION",
            highlighted_claim="BORROWED DEBT: $5,300,000,000 AT 7.8% INTEREST",
            context_body="The transaction was funded primarily through debt financing, encumbering substantially all store assets and inventory as primary collateral.",
            output_path=p1_slide3,
            stamp_text="CONFIDENTIAL SEC RECORD",
        )
        ViralDesigner.create_cliffhanger_scene(
            part1_title="THE $6.6 BILLION PRIVATE EQUITY TRAP",
            part2_teaser="PART 2: THE 400M BLOOD-DRAIN & THE FINAL BANKRUPTCY",
            output_path=p1_slide4,
        )
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
            scene_images=[p1_slide1, p1_slide2, p1_slide3, p1_slide4],
            narration_audio_path=p1_vo_path,
            output_mp4_path=p1_mp4,
            thumbnail_path=p1_thumb,
        )

        # ======================================================================
        # BUILD PART 2: THE AUTOPSY & THE FINAL VERDICT
        # ======================================================================
        p2_dir = PROJECTS_DIR / f"series_{p2_script.id}_part2"
        p2_dir.mkdir(parents=True, exist_ok=True)

        # 1. Voiceover for Part 2
        p2_vo_path = str(p2_dir / "voiceover.mp3")
        p2_text = f"{p2_script.hook_text} {p2_script.promise_text} {p2_script.body_text} {p2_script.conclusion_text}"
        ve.synthesize(p2_text, p2_vo_path)

        vo2 = Voiceover(script_id=p2_script.id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=p2_vo_path)
        VoiceoverRepository.add_voiceover(vo2)

        # 2. Visuals for Part 2 (Recap + Waterfall + Liquidation Document + Verdict Headline)
        p2_slide1 = str(p2_dir / "scene1_recap.png")
        p2_slide2 = str(p2_dir / "scene2_waterfall.png")
        p2_slide3 = str(p2_dir / "scene3_court_doc.png")
        p2_slide4 = str(p2_dir / "scene4_verdict.png")
        p2_thumb = str(p2_dir / "thumbnail_part2.jpg")

        ThumbnailDesigner.create_scene_slide(
            "PART 2: THE FORENSIC AUTOPSY",
            "Where Did The Billions Actually Go?",
            output_path=p2_slide1,
        )
        ChartGenerator.generate_membership_profit_waterfall(p2_slide2)
        ViralDesigner.create_document_highlight_scene(
            title="CHAPTER 11 BANKRUPTCY SCHEDULE B",
            doc_header="UNITED STATES BANKRUPTCY COURT",
            highlighted_claim="$400,000,000 ANNUAL INTEREST OBLIGATION",
            context_body="Debtor cannot generate sufficient operating cash flows to service pre-petition secured senior notes while maintaining capital expenditures for store facilities.",
            output_path=p2_slide3,
            stamp_text="CHAPTER 11 FILING",
        )
        ViralDesigner.create_headline_scene(
            title="THE AUTOPSY VERDICT",
            news_outlet="APEX ENTERPRISE FORENSICS",
            headline_text="KILLED BY DEBT: THE 33,000 WORKER CASUALTY",
            date_str="FINAL AUDIT REPORT",
            output_path=p2_slide4,
            investigative_tag="AUTOPSY COMPLETE",
        )
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
            scene_images=[p2_slide1, p2_slide2, p2_slide3, p2_slide4],
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
