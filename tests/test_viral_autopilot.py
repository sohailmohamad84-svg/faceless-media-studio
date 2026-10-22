"""Automated test suite for Viral Video Engine, Sound Design, and Two-Part Cliffhanger Autopilot."""
import pytest
from pathlib import Path
from src.database.connection import init_db, reset_db_connection
from src.database.repository import TopicRepository
from src.research.discovery import TopicDiscoveryEngine
from src.assets.sound_designer import SoundDesigner
from src.assets.viral_designer import ViralDesigner
from src.scripting.two_part_generator import TwoPartGenerator
from src.editing.viral_engine import ViralEngine
from src.quality.media_validator import validate_media_file


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    reset_db_connection()
    db_file = tmp_path / "test_viral.db"
    monkeypatch.setattr("config.settings.DATABASE_PATH", db_file)
    init_db(db_file)
    TopicDiscoveryEngine.seed_initial_topics()
    yield
    reset_db_connection()


def test_sound_designer_procedural_fx():
    """Verify procedural synthesis of cinematic sound effects."""
    sfx = SoundDesigner.ensure_sfx_library()
    assert Path(sfx["impact_boom"]).exists()
    assert Path(sfx["whoosh"]).exists()
    assert Path(sfx["tension_drone"]).exists()
    assert Path(sfx["impact_boom"]).stat().st_size > 1000


def test_viral_designer_assets(tmp_path):
    """Verify document highlight and headline scenes."""
    doc_path = str(tmp_path / "test_doc.png")
    ViralDesigner.create_document_highlight_scene(
        title="FORM 10-K FILING",
        doc_header="SECURITIES AND EXCHANGE COMMISSION",
        highlighted_claim="$400,000,000 ANNUAL INTEREST OBLIGATION",
        context_body="Debtor cannot generate sufficient operating cash flows to service pre-petition secured notes.",
        output_path=doc_path,
    )
    assert Path(doc_path).exists()
    assert Path(doc_path).stat().st_size > 10000

    head_path = str(tmp_path / "test_headline.png")
    ViralDesigner.create_headline_scene(
        title="THE 33,000 WORKER CASUALTY",
        news_outlet="WALL STREET JOURNAL",
        headline_text="KILLED BY DEBT: THE INVESTIGATION",
        date_str="2026",
        output_path=head_path,
    )
    assert Path(head_path).exists()
    assert Path(head_path).stat().st_size > 10000

    cliff_path = str(tmp_path / "test_cliff.png")
    ViralDesigner.create_cliffhanger_scene(
        part1_title="THE $6.6B TRAP",
        part2_teaser="PART 2: THE FINAL VERDICT",
        output_path=cliff_path,
    )
    assert Path(cliff_path).exists()


def test_two_part_cliffhanger_generation():
    """Verify coordinated generation of Part 1 and Part 2 with cliffhanger."""
    topics = TopicRepository.list_topics()
    topic = next((t for t in topics if "Toys" in t.title), topics[0])

    (p1_script, p1_scenes, p1_claims), (p2_script, p2_scenes, p2_claims) = (
        TwoPartGenerator.generate_two_part_series(topic)
    )

    # Check Part 1 has cliffhanger ending
    assert "Part 1" in p1_script.title
    assert "Part 2" in p1_script.conclusion_text
    assert len(p1_scenes) >= 4
    assert any(s.scene_type == "cliffhanger" for s in p1_scenes)

    # Check Part 2 has recap and verdict
    assert "Part 2" in p2_script.title
    assert "Part 1" in p2_script.hook_text
    assert len(p2_scenes) >= 3


def test_viral_engine_assembly(tmp_path):
    """Verify viral engine assembles video with Ken Burns and subtitles."""
    slide1 = str(tmp_path / "s1.png")
    slide2 = str(tmp_path / "s2.png")
    ViralDesigner.create_headline_scene("TEST HOOK", "FINANCIAL REPORT", "EMPIRE IN CRISIS", "2026", slide1)
    ViralDesigner.create_cliffhanger_scene("PART 1", "WATCH PART 2", slide2)

    # Audio synthesis
    from src.tts.voice_engine import VoiceEngine
    audio_path = str(tmp_path / "audio.mp3")
    ve = VoiceEngine()
    ve.synthesize("In 2005, the board signed a deal that sealed their fate. Watch Part 2 right now.", audio_path)

    from src.database.models import StoryboardScene, Script
    from src.database.repository import ScriptRepository
    topic = TopicRepository.list_topics()[0]
    script = Script(topic_id=topic.id, title="Test Viral Video")
    script_id = ScriptRepository.add_script(script)

    scenes = [
        StoryboardScene(scene_order=1, scene_title="S1", duration_sec=3.0, narration_text="In 2005, the board signed a deal."),
        StoryboardScene(scene_order=2, scene_title="S2", duration_sec=3.0, narration_text="Watch Part 2 right now."),
    ]

    engine = ViralEngine()
    out_mp4 = str(tmp_path / "viral_out.mp4")
    res = engine.assemble_viral_video(
        script_id=script_id,
        scenes=scenes,
        scene_images=[slide1, slide2],
        narration_audio_path=audio_path,
        output_mp4_path=out_mp4,
    )

    assert res["success"] is True
    assert Path(out_mp4).exists()
    val = validate_media_file(out_mp4)
    assert val["valid"] is True
    assert val["has_video"] is True
    assert val["has_audio"] is True
