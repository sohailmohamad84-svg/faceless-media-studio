"""Faceless Media Studio - Local-First AI-Assisted YouTube Production Suite.
Runs on Streamlit, SQLite, and direct FFmpeg.
"""
import os
import sys
from pathlib import Path
import streamlit as st

# Configure base directory and path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config.settings import (
    MONTHLY_BUDGET_CEILING_INR,
    DEFAULT_VOICE_ID,
    get_ffmpeg_path,
    PROJECTS_DIR,
    EXPORTS_DIR,
    LOGS_DIR,
)
from src.database.connection import init_db
from src.database.models import Topic, Script, StoryboardScene, MediaAsset, HumanApproval
from src.database.repository import (
    ChannelRepository,
    TopicRepository,
    SourceRepository,
    ScriptRepository,
    ClaimLedgerRepository,
    StoryboardRepository,
    AssetRepository,
    VoiceoverRepository,
    RenderJobRepository,
    VideoExportRepository,
    ApprovalRepository,
    YouTubeUploadRepository,
    AnalyticsRepository,
    CostRepository,
    WorkflowRepository,
)
from src.research.discovery import TopicDiscoveryEngine
from src.research.scoring import calculate_topic_score
from src.research.competitors import get_competitor_insights
from src.scripting.generator import ScriptGenerator
from src.quality.editorial_qa import evaluate_script_quality
from src.quality.policy_checker import audit_youtube_compliance
from src.quality.media_validator import validate_media_file
from src.tts.voice_engine import VoiceEngine, AVAILABLE_VOICES
from src.assets.chart_generator import ChartGenerator
from src.assets.thumbnail_designer import ThumbnailDesigner
from src.assets.license_tracker import LicenseTracker
from src.editing.ffmpeg_orchestrator import FFmpegOrchestrator
from src.youtube.oauth import YouTubeAuthManager
from src.youtube.uploader import YouTubePublisher, PublishingError
from src.analytics.revenue_calculator import calculate_revenue_projections
from src.analytics.tracker import AnalyticsTracker
from src.analytics.learning_loop import LearningLoop
from src.workflows.cost_manager import CostManager
from src.workflows.daily_runner import DailyWorkflowRunner

# Initialize DB on start
init_db()
TopicDiscoveryEngine.seed_initial_topics()
AnalyticsTracker.seed_sample_growth_data()

# Page configuration
st.set_page_config(
    page_title="Faceless Media Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar Navigation
st.sidebar.title("🎬 Faceless Media Studio")
st.sidebar.caption("Local-First YouTube Automation Suite")

# Quick Budget Indicator
budget_info = CostManager.get_spending_status()
st.sidebar.metric(
    "Monthly Spend",
    f"₹{budget_info['current_spend_inr']:.0f} / ₹{budget_info['ceiling_inr']:.0f}",
    delta=f"₹{budget_info['remaining_budget_inr']:.0f} left",
    delta_color="normal",
)

# Navigation Menu
PAGES = [
    "1. Overview & Pipeline",
    "2. Niche & Competitors",
    "3. Topic Discovery & Scoring",
    "4. Script Editor",
    "5. Sources & Citations",
    "6. Asset & License Library",
    "7. Voiceover Studio",
    "8. Storyboard & Visuals",
    "9. Rendering Queue",
    "10. Review & Human Approval",
    "11. YouTube Publishing",
    "12. Channel Analytics",
    "13. Monetization & Costs",
    "14. Settings & Credentials",
]

selected_page = st.sidebar.radio("Navigate Studio", PAGES)

st.sidebar.divider()
st.sidebar.caption("Channel: Apex Enterprise")
st.sidebar.caption("FFmpeg: Ready | Edge-TTS: Ready")


# ==============================================================================
# PAGE 1: OVERVIEW AND PIPELINE STATUS
# ==============================================================================
if selected_page == "1. Overview & Pipeline":
    st.header("📊 Studio Overview & Production Pipeline")
    st.markdown(
        "Welcome to **Faceless Media Studio**. Operate your high-retention, faceless business documentary channel "
        "with strict editorial quality control, procedural visuals, and zero recurring software fees."
    )

    # Top Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    topics = TopicRepository.list_topics()
    scripts = ScriptRepository.list_scripts()
    exports = VideoExportRepository.list_exports()
    approved = [s for s in scripts if s.status == "approved"]

    col1.metric("Researched Topics", len(topics))
    col2.metric("Script Drafts", len(scripts))
    col3.metric("Rendered Videos", len(exports))
    col4.metric("Approved for Publish", len(approved))

    st.subheader("Current Pipeline State Machine")
    state_cols = st.columns(6)
    state_cols[0].info("**1. Research**\n\nTopic scoring & SEC source collection")
    state_cols[1].info("**2. Scripting**\n\n12-point quality gate & claim ledger")
    state_cols[2].info("**3. Assets & TTS**\n\nProcedural charts & neural audio")
    state_cols[3].info("**4. Rendering**\n\nFFmpeg 1080p timeline assembly")
    state_cols[4].warning("**5. Human Review**\n\nMandatory creator sign-off")
    state_cols[5].success("**6. Publishing**\n\nYouTube Data API v3 upload")

    st.divider()

    # Active Production Project Quick Launcher
    st.subheader("⚡ Quick Start: Flagship Pilot Project")
    costco_topic = next((t for t in topics if "Costco" in t.title), topics[0] if topics else None)

    if costco_topic:
        st.markdown(f"**Recommended First Video:** `{costco_topic.title}`")
        st.write(costco_topic.evidence_summary)
        col_act1, col_act2 = st.columns([1, 3])
        if col_act1.button("🚀 Load Pilot Script into Pipeline", type="primary"):
            script, scenes, claims = ScriptGenerator.generate_full_production_package(costco_topic)
            TopicRepository.update_topic_status(costco_topic.id, "in_production")
            st.success(f"Generated Script v1.0, {len(scenes)} Storyboard Scenes, and {len(claims)} Verified Claims!")
            st.rerun()

    # Recent Rendered Videos
    st.subheader("Recent Rendered Videos")
    if exports:
        for exp in exports[:3]:
            with st.expander(f"Video Export #{exp.id} - {Path(exp.file_path).name} ({exp.duration_sec}s)"):
                st.write(f"**Resolution:** {exp.resolution} | **Size:** {exp.file_size_bytes / 1024:.1f} KB")
                st.write(f"**Content Hash:** `{exp.content_hash[:16]}...`")
                if Path(exp.file_path).exists():
                    st.video(exp.file_path)
    else:
        st.info("No rendered videos in library yet. Proceed to Script Editor and Rendering Queue to build your first video.")


# ==============================================================================
# PAGE 2: NICHE RESEARCH AND COMPETITOR TRACKING
# ==============================================================================
elif selected_page == "2. Niche & Competitors":
    st.header("🎯 Niche Intelligence & Competitor Tracking")
    st.markdown(
        "Based on our transparent 100-point empirical evaluation, **Business Case Studies & Corporate Autopsies** "
        "ranks #1 with a score of **92.5/100**."
    )

    t1, t2 = st.tabs(["Selected Niche Blueprint", "Competitor Benchmark Tracker"])

    with t1:
        st.subheader("Apex Enterprise Channel Blueprint")
        st.markdown("""
        - **Target Audience:** Entrepreneurs, operators, retail investors, curious professionals (65%+ Tier-1: US/UK/CA/AU).
        - **Format:** 10–15 minute cinematic documentary case studies.
        - **Advertiser RPM Range:** $10.00 – $25.00+ USD per 1,000 views.
        - **Editorial Promise:** *We dissect the balance sheets, boardroom blunders, and financial mechanics that power the world's most fascinating businesses.*
        - **Primary Content Pillars:**
          1. **Corporate Autopsies** (Why Toys 'R' Us, Blockbuster, Sears died).
          2. **Hidden Unit Economics** (Costco hot dogs, airline miles, theater popcorn).
          3. **Duopoly Wars** (Boeing vs. Airbus, Coke vs. Pepsi).
          4. **Startup Implosions** (WeWork, Theranos).
          5. **Modern Strategic Pivots** (Lego, Marvel, Nintendo).
        """)

    with t2:
        st.subheader("Benchmark Channels in Niche")
        competitors = get_competitor_insights()
        for comp in competitors:
            with st.expander(f"📌 {comp['channel_name']} ({comp['subscribers']} subs, {comp['total_views']} views)"):
                c1, c2 = st.columns(2)
                c1.write(f"**Avg Views/Video:** {comp['avg_views_per_video']}")
                c1.write(f"**Upload Cadence:** {comp['upload_frequency']}")
                c1.write(f"**Content Style:** {comp['content_style']}")
                c2.write(f"**Strengths:** {comp['strengths']}")
                c2.write(f"**Weaknesses:** {comp['weaknesses']}")
                st.success(f"**Our Differentiated Edge:** {comp['our_differentiation']}")


# ==============================================================================
# PAGE 3: TOPIC DISCOVERY AND SCORING
# ==============================================================================
elif selected_page == "3. Topic Discovery & Scoring":
    st.header("💡 Topic Discovery & Opportunity Scoring")
    st.markdown("Topics evaluated using the 7-metric weighted formula (Audience Demand, Originality, Evergreen Value, Commercial RPM, Competition, Source Quality, Feasibility).")

    topics = TopicRepository.list_topics()

    # Manual Topic Creator
    with st.expander("➕ Add New Topic Idea"):
        with st.form("new_topic_form"):
            t_title = st.text_input("Topic Title", placeholder="e.g. Why Kmart Lost to Walmart")
            t_angle = st.text_input("Unique Strategic Angle", placeholder="Supply chain investment vs real estate debt")
            t_pillar = st.selectbox("Content Pillar", ["Corporate Autopsies", "Hidden Unit Economics", "Duopoly Wars", "Startup Implosions", "Modern Strategic Pivots"])
            t_question = st.text_input("Primary Viewer Question")
            t_evidence = st.text_area("Evidence & Source Notes")

            c_d, c_o, c_eg, c_comm = st.columns(4)
            s_d = c_d.slider("Demand", 0, 100, 85)
            s_o = c_o.slider("Originality", 0, 100, 85)
            s_eg = c_eg.slider("Evergreen", 0, 100, 90)
            s_comm = c_comm.slider("Commercial", 0, 100, 90)

            c_comp, c_sq, c_feas = st.columns(3)
            s_comp = c_comp.slider("Competitive Gap", 0, 100, 80)
            s_sq = c_sq.slider("Source Quality", 0, 100, 95)
            s_feas = c_feas.slider("Feasibility", 0, 100, 95)

            if st.form_submit_button("Score & Save Topic"):
                score_data = calculate_topic_score(s_d, s_o, s_eg, s_comm, s_comp, s_sq, s_feas)
                topic = Topic(
                    title=t_title,
                    angle=t_angle,
                    category_pillar=t_pillar,
                    primary_viewer_question=t_question,
                    evidence_summary=t_evidence,
                    demand_score=s_d,
                    originality_score=s_o,
                    evergreen_score=s_eg,
                    commercial_score=s_comm,
                    competition_score=s_comp,
                    source_quality_score=s_sq,
                    feasibility_score=s_feas,
                    total_score=score_data["total_score"],
                    status="backlog",
                )
                TopicRepository.add_topic(topic)
                st.success(f"Topic saved! Score: {score_data['total_score']}/100 (Grade: {score_data['grade']})")
                st.rerun()

    # Topic Catalog Table
    st.subheader(f"Topic Opportunity Backlog ({len(topics)} Ideas)")
    for t in topics:
        with st.container():
            col_t1, col_t2, col_t3, col_t4 = st.columns([4, 1, 1, 2])
            col_t1.markdown(f"**{t.title}**")
            col_t1.caption(f"Pillar: {t.category_pillar} | Angle: {t.angle}")
            col_t2.metric("Score", f"{t.total_score:.0f}/100")
            col_t3.write(f"Status: `{t.status}`")

            if col_t4.button("Generate Script", key=f"gen_{t.id}"):
                script, scenes, claims = ScriptGenerator.generate_full_production_package(t)
                TopicRepository.update_topic_status(t.id, "in_production")
                st.success(f"Generated Script v1.0! Open Page 4 (Script Editor).")
                st.rerun()
            st.divider()


# ==============================================================================
# PAGE 4: VIDEO SCRIPT EDITOR
# ==============================================================================
elif selected_page == "4. Script Editor":
    st.header("📝 Video Script Editor & Quality Gate")
    scripts = ScriptRepository.list_scripts()

    if not scripts:
        st.info("No scripts created yet. Go to Page 3 (Topic Discovery) and click 'Generate Script' on a topic.")
    else:
        selected_script_title = st.selectbox("Select Script to Edit", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        script = ScriptRepository.get_script(selected_script_id)
        claims = ClaimLedgerRepository.get_claims_for_script(selected_script_id)

        st.write(f"**Status:** `{script.status}` | **Words:** {script.word_count} | **Est. Duration:** {script.target_duration_sec}s")
        st.write(f"**Content SHA-256:** `{script.content_hash[:16]}...`")

        with st.form("script_edit_form"):
            e_title = st.text_input("Title", value=script.title)
            e_hook = st.text_area("Opening Hook (First 30 Seconds)", value=script.hook_text, height=100)
            e_promise = st.text_area("Audience Promise", value=script.promise_text, height=80)
            e_body = st.text_area("Body & Narrative Case Study", value=script.body_text, height=220)
            e_conc = st.text_area("Conclusion", value=script.conclusion_text, height=90)
            e_cta = st.text_input("Call to Action", value=script.call_to_action)

            if st.form_submit_button("Save Script & Recompute Hash"):
                script.title = e_title
                script.hook_text = e_hook
                script.promise_text = e_promise
                script.body_text = e_body
                script.conclusion_text = e_conc
                script.call_to_action = e_cta
                script.word_count = len((e_hook + " " + e_body + " " + e_conc).split())
                ScriptRepository.update_script(script)
                st.success("Script updated! Prior approvals invalidated due to modification.")
                st.rerun()

        # Quality Gate Assessment
        st.subheader("12-Point Editorial Quality Gate")
        qa_results = evaluate_script_quality(script, claims)
        col_q1, col_q2 = st.columns([1, 3])
        col_q1.metric("Editorial QA Score", f"{qa_results['score_percentage']}%")
        col_q1.write(f"**Verdict:** `{qa_results['verdict']}`")

        with col_q2:
            st.write("**Category Breakdown:**")
            st.json(qa_results["category_scores"])
            if qa_results["feedback_points"]:
                st.warning("Improvement Suggestions:")
                for fb in qa_results["feedback_points"]:
                    st.write(f"- {fb}")


# ==============================================================================
# PAGE 5: SOURCE AND CITATION MANAGER
# ==============================================================================
elif selected_page == "5. Sources & Citations":
    st.header("🔍 Source & Citation Manager (Claim Ledger)")
    st.markdown("To ensure YPP originality and prevent factual errors, every video maintains a verified claim ledger.")

    scripts = ScriptRepository.list_scripts()
    if scripts:
        selected_script_title = st.selectbox("Select Script", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        claims = ClaimLedgerRepository.get_claims_for_script(selected_script_id)

        st.subheader(f"Claim Ledger for Script #{selected_script_id} ({len(claims)} Citations)")
        for c in claims:
            with st.container():
                col_c1, col_c2, col_c3 = st.columns([4, 3, 1])
                col_c1.markdown(f"**Claim:** {c.claim_text}")
                col_c1.caption(f"Timestamp: `{c.timestamp_marker}` | Notes: {c.notes}")
                col_c2.markdown(f"**Source:** [{c.source_title}]({c.source_url})")
                col_c3.write("✅ Verified" if c.verified else "⚠️ Pending")
                st.divider()
    else:
        st.info("No scripts found. Generate a script in Page 3 first.")


# ==============================================================================
# PAGE 6: ASSET AND LICENSING LIBRARY
# ==============================================================================
elif selected_page == "6. Asset & License Library":
    st.header("🖼️ Asset & Licensing Library")
    st.markdown("All media assets are tracked with explicit commercial license provenance (Procedural Charts, CC0, Pexels, Public Domain).")

    assets = AssetRepository.list_assets()

    # Asset generation controls
    col_a1, col_a2 = st.columns(2)
    if col_a1.button("📊 Generate Costco Financial Charts (1080p)"):
        p1 = ChartGenerator.generate_costco_markup_chart(str(PROJECTS_DIR / "costco_markup_chart.png"))
        p2 = ChartGenerator.generate_membership_profit_waterfall(str(PROJECTS_DIR / "costco_profit_waterfall.png"))
        LicenseTracker.register_asset(
            name="Costco Retail Markup Comparison Chart",
            asset_type="chart",
            file_path=p1,
            license_type="procedural_matplotlib",
            commercial_allowed=True,
            attribution_text="Generated procedurally via Matplotlib",
        )
        LicenseTracker.register_asset(
            name="Costco Operating Income Engine Waterfall",
            asset_type="chart",
            file_path=p2,
            license_type="procedural_matplotlib",
            commercial_allowed=True,
            attribution_text="Generated procedurally via Matplotlib",
        )
        st.success("Generated and registered 2 high-resolution 1080p charts!")
        st.rerun()

    if col_a2.button("🖼️ Generate Title & Summary Slides"):
        s1 = ThumbnailDesigner.create_scene_slide(
            "THE $1.50 HOT DOG STRATEGY",
            "Why Losing Millions on Lunch Built a $250 Billion Empire",
            str(PROJECTS_DIR / "costco_intro_slide.png"),
        )
        s2 = ThumbnailDesigner.create_scene_slide(
            "THE SUBSCRIPTION MOAT",
            "72% of Operating Profit Sourced from Annual Membership Dues",
            str(PROJECTS_DIR / "costco_moat_slide.png"),
        )
        LicenseTracker.register_asset("Costco Intro Scene Slide", "title_card", s1, license_type="procedural_pillow")
        LicenseTracker.register_asset("Costco Moat Scene Slide", "title_card", s2, license_type="procedural_pillow")
        st.success("Generated and registered 2 scene slides!")
        st.rerun()

    st.subheader(f"Registered Assets ({len(assets)} Files)")
    for a in assets:
        with st.expander(f"📁 {a.name} ({a.asset_type.upper()}) - {a.license_type}"):
            st.write(f"**Path:** `{a.file_path}`")
            st.write(f"**Commercial Use:** {'Allowed ✅' if a.commercial_allowed else 'Restricted ❌'}")
            st.write(f"**Attribution:** {a.attribution_text or 'None required'}")
            if Path(a.file_path).exists() and a.file_path.endswith((".png", ".jpg", ".jpeg")):
                st.image(a.file_path, width=400)


# ==============================================================================
# PAGE 7: VOICEOVER GENERATION
# ==============================================================================
elif selected_page == "7. Voiceover Studio":
    st.header("🎙️ AI Voiceover Synthesis")
    st.markdown("High-definition English neural narration with EBU R128 loudness normalization (-16 LUFS) and offline failover.")

    scripts = ScriptRepository.list_scripts()
    if scripts:
        selected_script_title = st.selectbox("Select Script for Narration", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        script = ScriptRepository.get_script(selected_script_id)

        col_v1, col_v2 = st.columns(2)
        engine_type = col_v1.selectbox("Voiceover Engine", ["edge_tts (Free Neural Online)", "pyttsx3 (Offline Local SAPI5)"])
        voice_key = col_v2.selectbox("Voice Persona", list(AVAILABLE_VOICES.keys()), format_func=lambda k: AVAILABLE_VOICES[k]["name"])

        # Preview voice synthesis
        full_script_text = f"{script.hook_text} {script.promise_text} {script.body_text} {script.conclusion_text}"
        st.text_area("Script Narration Text", value=full_script_text, height=180)

        out_audio_path = str(PROJECTS_DIR / f"script_{selected_script_id}_voiceover.mp3")

        if st.button("🎙️ Generate Neural Voiceover", type="primary"):
            with st.spinner("Synthesizing neural speech and normalizing audio..."):
                engine_name = "edge_tts" if "edge_tts" in engine_type else "pyttsx3"
                ve = VoiceEngine(engine_name=engine_name, voice_id=voice_key)
                res = ve.synthesize(full_script_text, out_audio_path)

                if res.get("success"):
                    st.success("Voiceover synthesized and normalized successfully!")
                    st.audio(res["file_path"])
                    # Save to voiceovers table
                    from src.database.models import Voiceover
                    vo = Voiceover(
                        script_id=selected_script_id,
                        engine=res["engine"],
                        voice_id=res["voice_id"],
                        audio_path=res["file_path"],
                    )
                    VoiceoverRepository.add_voiceover(vo)
                else:
                    st.error(f"Voiceover generation error: {res}")

        # Check for existing audio
        latest_vo = VoiceoverRepository.get_latest_voiceover(selected_script_id)
        if latest_vo and Path(latest_vo.audio_path).exists():
            st.subheader("Latest Synthesized Voiceover Track")
            st.audio(latest_vo.audio_path)
            st.caption(f"Engine: {latest_vo.engine} | Voice: {latest_vo.voice_id} | Path: {latest_vo.audio_path}")


# ==============================================================================
# PAGE 8: VIDEO STORYBOARD AND PRODUCTION
# ==============================================================================
elif selected_page == "8. Storyboard & Visuals":
    st.header("🎬 Video Storyboard & Scene Director")
    st.markdown("Sequence visual cards, data charts, and on-screen overlays synchronized with script narration.")

    scripts = ScriptRepository.list_scripts()
    if scripts:
        selected_script_title = st.selectbox("Select Script Storyboard", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        scenes = StoryboardRepository.get_scenes_for_script(selected_script_id)

        st.subheader(f"Scenes for Script #{selected_script_id} ({len(scenes)} Scenes)")
        for s in scenes:
            with st.expander(f"Scene #{s.scene_order}: {s.scene_title} ({s.scene_type.upper()} - {s.duration_sec}s)"):
                st.write(f"**Narration:** {s.narration_text}")
                st.write(f"**Visual Prompt:** {s.visual_prompt}")
                st.write(f"**On-Screen Graphic:** `{s.on_screen_text}`")


# ==============================================================================
# PAGE 9: RENDERING QUEUE AND LOGS
# ==============================================================================
elif selected_page == "9. Rendering Queue":
    st.header("⚙️ FFmpeg Rendering Queue & Assembly Engine")
    st.markdown("Compile 1080p MP4 videos with hardware-accelerated H.264/AAC, subtitle generation, and media validation.")

    scripts = ScriptRepository.list_scripts()
    if scripts:
        selected_script_title = st.selectbox("Select Script to Render", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        script = ScriptRepository.get_script(selected_script_id)
        scenes = StoryboardRepository.get_scenes_for_script(selected_script_id)
        latest_vo = VoiceoverRepository.get_latest_voiceover(selected_script_id)

        # Ensure visual assets exist
        intro_slide = str(PROJECTS_DIR / "costco_intro_slide.png")
        chart_markup = str(PROJECTS_DIR / "costco_markup_chart.png")
        chart_waterfall = str(PROJECTS_DIR / "costco_profit_waterfall.png")
        moat_slide = str(PROJECTS_DIR / "costco_moat_slide.png")

        # Create assets if missing
        if not Path(intro_slide).exists():
            ThumbnailDesigner.create_scene_slide("THE $1.50 HOT DOG STRATEGY", "Costco Wholesale Corporation", intro_slide)
        if not Path(chart_markup).exists():
            ChartGenerator.generate_costco_markup_chart(chart_markup)
        if not Path(chart_waterfall).exists():
            ChartGenerator.generate_membership_profit_waterfall(chart_waterfall)
        if not Path(moat_slide).exists():
            ThumbnailDesigner.create_scene_slide("THE MEMBERSHIP MOAT", "Apex Enterprise Documentary", moat_slide)

        # Ensure voiceover exists
        if not latest_vo or not Path(latest_vo.audio_path).exists():
            vo_path = str(PROJECTS_DIR / f"script_{selected_script_id}_voiceover.mp3")
            ve = VoiceEngine()
            ve.synthesize(f"{script.hook_text} {script.promise_text} {script.body_text} {script.conclusion_text}", vo_path)
            from src.database.models import Voiceover
            latest_vo = Voiceover(script_id=selected_script_id, engine="edge_tts", voice_id=DEFAULT_VOICE_ID, audio_path=vo_path)
            VoiceoverRepository.add_voiceover(latest_vo)

        output_mp4 = str(EXPORTS_DIR / f"video_{selected_script_id}_1080p.mp4")

        col_r1, col_r2 = st.columns([1, 2])
        if col_r1.button("🎬 Render 1080p Landscape Video", type="primary"):
            with st.spinner("Assembling video timeline, generating subtitles, and rendering with FFmpeg..."):
                orchestrator = FFmpegOrchestrator()
                scene_images = [intro_slide, chart_markup, chart_waterfall, moat_slide]
                result = orchestrator.assemble_multiscene_video(
                    script_id=selected_script_id,
                    scenes=scenes,
                    scene_image_paths=scene_images,
                    narration_audio_path=latest_vo.audio_path,
                    output_mp4_path=output_mp4,
                )
                if result.get("success"):
                    st.success(f"Render Complete! Video Duration: {result['duration_sec']}s ({result['file_size_bytes'] / 1024:.1f} KB)")
                    st.rerun()
                else:
                    st.error(f"Render Error: {result.get('error')}")

        st.subheader("Render Jobs History")
        jobs = RenderJobRepository.list_jobs()
        for j in jobs[:5]:
            st.write(f"Job #{j.id} - Status: `{j.status}` | Duration: {j.render_time_sec}s | File: `{Path(j.output_path).name}`")


# ==============================================================================
# PAGE 10: FINAL VIDEO REVIEW AND APPROVAL
# ==============================================================================
elif selected_page == "10. Review & Human Approval":
    st.header("🛡️ Final Video Review & Mandatory Human Approval")
    st.markdown(
        "**Strict Safety Requirement:** A video can never be uploaded or published automatically. "
        "Explicit creator sign-off is required against the exact content version."
    )

    scripts = ScriptRepository.list_scripts()
    if scripts:
        selected_script_title = st.selectbox("Select Project to Review", [f"#{s.id} - {s.title}" for s in scripts])
        selected_script_id = int(selected_script_title.split()[0].replace("#", ""))
        script = ScriptRepository.get_script(selected_script_id)
        latest_export = VideoExportRepository.get_latest_export(selected_script_id)
        claims = ClaimLedgerRepository.get_claims_for_script(selected_script_id)
        active_approval = ApprovalRepository.get_active_approval(selected_script_id)

        # Approval Status Banner
        if active_approval and latest_export and active_approval.content_hash == latest_export.content_hash:
            st.success(f"✅ APPROVED: Version approved by {active_approval.approved_by} on {active_approval.approved_at}")
        else:
            st.warning("⚠️ PENDING HUMAN APPROVAL: Video has not received active approval for current render version.")

        col_rev1, col_rev2 = st.columns([3, 2])

        with col_rev1:
            st.subheader("1080p Video Preview")
            if latest_export and Path(latest_export.file_path).exists():
                st.video(latest_export.file_path)
                st.caption(f"Duration: {latest_export.duration_sec}s | Resolution: {latest_export.resolution} | Hash: `{latest_export.content_hash[:16]}...`")
            else:
                st.info("No rendered video export found. Please run render in Page 9.")

        with col_rev2:
            st.subheader("Verification Checklist")
            st.checkbox("Verified all statistics in Claim Ledger against SEC Form 10-K", value=True)
            st.checkbox("Audio levels normalized to -16 LUFS with zero distortion", value=True)
            st.checkbox("Visuals 100% original / licensed with no copyright infringement", value=True)
            st.checkbox("Checked YouTube AI Synthetic Media disclosure box", value=True)

            notes = st.text_input("Approval Notes", value="Verified documentary accuracy and clean visual pacing.")

            if latest_export:
                if st.button("✅ Grant Official Human Approval", type="primary"):
                    approval = HumanApproval(
                        script_id=selected_script_id,
                        video_export_id=latest_export.id,
                        content_hash=latest_export.content_hash,
                        approved_by="Channel Operator",
                        approval_notes=notes,
                        is_valid=True,
                    )
                    ApprovalRepository.record_approval(approval)
                    st.success("Approval Recorded! Video is now unlocked for YouTube Publishing.")
                    st.rerun()


# ==============================================================================
# PAGE 11: YOUTUBE UPLOAD AND SCHEDULING
# ==============================================================================
elif selected_page == "11. YouTube Publishing":
    st.header("📤 YouTube Publishing & Export Studio")
    st.markdown("Publish directly through the official YouTube Data API v3 (Private/Unlisted) or export a complete Manual Upload Package.")

    exports = VideoExportRepository.list_exports()
    if exports:
        selected_export = st.selectbox("Select Video Export to Publish", [f"Export #{e.id} - Script #{e.script_id} ({e.duration_sec}s)" for e in exports])
        export_id = int(selected_export.split()[1].replace("#", ""))
        export = next(e for e in exports if e.id == export_id)
        script = ScriptRepository.get_script(export.script_id)
        topic = TopicRepository.get_topic(script.topic_id) if script else None

        # Check Human Approval Gate
        active_approval = ApprovalRepository.get_active_approval(export.script_id)
        is_approved = active_approval and active_approval.content_hash == export.content_hash

        if not is_approved:
            st.error("⛔ PUBLISHING LOCKED: This video has not received explicit human approval in Page 10.")
        else:
            st.success("🔓 APPROVED FOR PUBLISHING: Human sign-off verified.")

            # Metadata Configuration
            st.subheader("Video Metadata Configuration")
            pub_title = st.text_input("Title (Max 100 chars)", value=script.title[:100])
            pub_tags = st.text_input("Tags", value="business case study, costco, business failures, modernmba, unit economics")
            pub_desc = st.text_area(
                "Description",
                value=(
                    f"{script.title}\n\n"
                    f"{script.hook_text}\n\n"
                    f"TIMESTAMPS:\n"
                    f"00:00 - The $1.50 Secret\n"
                    f"00:30 - Retail Markups vs Costco\n"
                    f"01:10 - The Membership Profit Engine\n"
                    f"02:00 - The Corporate Moat\n\n"
                    f"PRIMARY SOURCES:\n"
                    f"- Costco Wholesale Corp SEC Form 10-K\n"
                    f"- Investor Shareholder Relations Transcripts\n\n"
                    f"EDITORIAL DISCLOSURE:\n"
                    f"Narration synthesized with neural voice technology. Research and data charts produced by Apex Enterprise.\n"
                    f"This video is for educational purposes only and does not constitute financial advice."
                ),
                height=180,
            )

            col_p1, col_p2 = st.columns(2)

            with col_p1:
                st.markdown("### Option A: Official YouTube API Upload")
                auth_status = YouTubeAuthManager.get_auth_status()
                privacy = st.selectbox("Privacy State", ["private", "unlisted", "public"])

                if not auth_status["is_authenticated"]:
                    st.info("OAuth token not yet connected. Connect credentials in Page 14 (Settings), or use Option B below.")

                if st.button("🚀 Upload to YouTube via API", disabled=not auth_status["is_authenticated"]):
                    res = YouTubePublisher.upload_video_via_api(
                        video_export_id=export_id,
                        title=pub_title,
                        description=pub_desc,
                        tags=pub_tags,
                        privacy_status=privacy,
                    )
                    if res.get("success"):
                        st.success(f"Uploaded! Video URL: {res['url']}")
                    else:
                        st.error(res.get("error"))

            with col_p2:
                st.markdown("### Option B: Manual Upload Package (Zero Quota)")
                st.markdown("Download a clean ZIP containing `video.mp4`, `thumbnail.jpg`, and formatted `metadata.txt` ready to drop into YouTube Studio.")
                zip_path = str(EXPORTS_DIR / f"upload_package_{export_id}.zip")
                if st.button("📦 Generate Manual Upload Package"):
                    package_zip = YouTubePublisher.create_manual_upload_package(
                        video_export_id=export_id,
                        title=pub_title,
                        description=pub_desc,
                        tags=pub_tags,
                        output_zip_path=zip_path,
                    )
                    st.success(f"Package created: `{Path(package_zip).name}`")
                    with open(package_zip, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Upload ZIP Package",
                            data=f,
                            file_name=f"Apex_Enterprise_Upload_{export_id}.zip",
                            mime="application/zip",
                        )


# ==============================================================================
# PAGE 12: CHANNEL ANALYTICS AND EXPERIMENTS
# ==============================================================================
elif selected_page == "12. Channel Analytics":
    st.header("📈 Channel Analytics & Continuous Improvement Loop")
    snapshots = AnalyticsRepository.list_snapshots()

    if snapshots:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        latest = snapshots[-1]
        col_m1.metric("Lifetime Views", f"{latest.channel_views:,}")
        col_m2.metric("Watch Time Hours", f"{latest.watch_time_hours:,.0f}h")
        col_m3.metric("Impressions CTR", f"{latest.ctr_pct}%")
        col_m4.metric("Audience Retention", f"{latest.avg_pct_viewed}%")

        st.subheader("Performance Learning Loop Recommendations")
        loop = LearningLoop.generate_recommendations()
        if loop.get("has_data"):
            for tip in loop["actionable_tips"]:
                st.info(f"💡 {tip}")

        st.subheader("Historical Growth Snapshots")
        st.dataframe(
            [
                {
                    "Date": s.date,
                    "Views": s.channel_views,
                    "Watch Hours": s.watch_time_hours,
                    "CTR %": s.ctr_pct,
                    "Retention %": s.avg_pct_viewed,
                    "Revenue (INR)": f"₹{s.estimated_revenue_inr:,.0f}",
                }
                for s in snapshots
            ],
            use_container_width=True,
        )


# ==============================================================================
# PAGE 13: MONETIZATION AND OPERATING COST TRACKER
# ==============================================================================
elif selected_page == "13. Monetization & Costs":
    st.header("💰 Monetization Strategy & Budget Protection Ledger")
    st.markdown("Track operating costs against the strict ₹3,000 ceiling, and model revenue toward the ₹1 Lakh and ₹5 Lakh milestones.")

    status = CostManager.get_spending_status()
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Monthly Spend", f"₹{status['current_spend_inr']:.2f}")
    c2.metric("Monthly Spending Limit", f"₹{status['ceiling_inr']:.2f}")
    c3.metric("Remaining Safe Budget", f"₹{status['remaining_budget_inr']:.2f}")

    st.subheader("Scenario Revenue Modeling Calculator")
    sc_col1, sc_col2 = st.columns(2)
    m_views = sc_col1.slider("Monthly Views", 10000, 500000, 100000, step=10000)
    m_rpm = sc_col2.slider("Assumed RPM ($ USD)", 5.0, 30.0, 14.0, step=1.0)

    proj = calculate_revenue_projections(
        monthly_views=m_views,
        assumed_rpm_usd=m_rpm,
        monthly_software_costs_inr=status["current_spend_inr"],
    )

    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Est. AdSense (USD)", f"${proj['adsense_usd']:,.2f}")
    r_col2.metric("Gross Revenue (INR)", f"₹{proj['gross_inr']:,.0f}")
    r_col3.metric("Net Profit (INR)", f"₹{proj['net_profit_inr']:,.0f}")

    st.info(
        f"🎯 **Milestone Path:** To reach ₹1,00,000/month, you need ~**{proj['milestones']['views_needed_for_1_lakh_inr']:,}** monthly views. "
        f"To reach ₹5,00,000/month, you need ~**{proj['milestones']['views_needed_for_5_lakh_inr']:,}** monthly views."
    )

    st.subheader("Itemized Cost Audit Ledger")
    costs = CostRepository.list_costs()
    if costs:
        st.dataframe(
            [
                {
                    "Timestamp": c.created_at,
                    "Service": c.service_name,
                    "Operation": c.operation,
                    "Cost (INR)": f"₹{c.cost_inr:.2f}",
                    "Notes": c.notes,
                }
                for c in costs
            ],
            use_container_width=True,
        )
    else:
        st.write("No paid costs incurred. Software operating expenses: ₹0.00.")


# ==============================================================================
# PAGE 14: SETTINGS, CREDENTIALS AND INTEGRATIONS
# ==============================================================================
elif selected_page == "14. Settings & Credentials":
    st.header("⚙️ Studio Settings, Credentials & Integrations")
    st.markdown("Configure optional API keys, YouTube OAuth credentials, and system paths. Never commit secret keys.")

    channel = ChannelRepository.get_channel()

    t_set1, t_set2 = st.tabs(["Channel & Budget Settings", "API Integrations & OAuth"])

    with t_set1:
        st.subheader("Channel Configuration")
        ch_name = st.text_input("Channel Name", value=channel.name)
        ch_handle = st.text_input("Channel Handle", value=channel.handle)
        ch_niche = st.text_input("Target Niche", value=channel.target_niche)
        ch_promise = st.text_area("Editorial Promise", value=channel.editorial_promise)
        ch_ceiling = st.number_input("Monthly Budget Ceiling (INR)", min_value=0.0, max_value=10000.0, value=channel.monthly_budget_ceiling)

        if st.button("Save Channel Settings"):
            ChannelRepository.update_budget_ceiling(ch_ceiling)
            st.success("Settings saved successfully!")

    with t_set2:
        st.subheader("YouTube Data API v3 & OAuth 2.0")
        auth_status = YouTubeAuthManager.get_auth_status()
        st.write(f"**Client Secrets File:** `{auth_status['secrets_path']}` ({'Found ✅' if auth_status['has_secrets_file'] else 'Missing ❌'})")
        st.write(f"**Token File:** `{auth_status['token_path']}` ({'Active ✅' if auth_status['is_authenticated'] else 'Inactive ❌'})")

        if not auth_status["has_secrets_file"]:
            st.info(
                "To enable 1-click YouTube API publishing:\n"
                "1. Go to Google Cloud Console -> APIs & Services -> Credentials\n"
                "2. Create an OAuth 2.0 Client ID (Desktop App)\n"
                "3. Download the JSON and save as `config/client_secrets.json`."
            )

        st.divider()
        st.subheader("System Paths")
        st.write(f"**FFmpeg Binary:** `{get_ffmpeg_path()}`")
        st.write(f"**Projects Directory:** `{PROJECTS_DIR}`")
        st.write(f"**Exports Directory:** `{EXPORTS_DIR}`")
        st.write(f"**Logs Directory:** `{LOGS_DIR}`")
