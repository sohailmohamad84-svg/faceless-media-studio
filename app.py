"""Faceless Media Studio - Local-First AI-Assisted YouTube Production Suite.
Features 1-Click Daily Batch Production (2 Viral Videos/Day with Part 1 & Part 2 Cliffhangers),
Kinetic Subtitles, Multi-Track Sound Design, and Auto-Publishing on Approval.
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
from src.scripting.two_part_generator import TwoPartGenerator
from src.quality.editorial_qa import evaluate_script_quality
from src.quality.policy_checker import audit_youtube_compliance
from src.quality.media_validator import validate_media_file
from src.tts.voice_engine import VoiceEngine, AVAILABLE_VOICES
from src.assets.chart_generator import ChartGenerator
from src.assets.viral_designer import ViralDesigner
from src.assets.thumbnail_designer import ThumbnailDesigner
from src.assets.sound_designer import SoundDesigner
from src.assets.license_tracker import LicenseTracker
from src.editing.viral_engine import ViralEngine
from src.workflows.daily_autopilot import DailyAutopilot
from src.youtube.oauth import YouTubeAuthManager
from src.youtube.uploader import YouTubePublisher, PublishingError
from src.analytics.revenue_calculator import calculate_revenue_projections
from src.analytics.tracker import AnalyticsTracker
from src.analytics.learning_loop import LearningLoop
from src.workflows.cost_manager import CostManager
from src.workflows.daily_runner import DailyWorkflowRunner

# Initialize DB and seed initial topics
init_db()
TopicDiscoveryEngine.seed_initial_topics()
AnalyticsTracker.seed_sample_growth_data()
SoundDesigner.ensure_sfx_library()

st.set_page_config(
    page_title="Apex Enterprise - Viral Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("🎬 Faceless Media Studio")
st.sidebar.caption("High-Retention Business Documentaries (2 Videos/Day)")

# Budget Indicator
budget_info = CostManager.get_spending_status()
st.sidebar.metric(
    "Monthly Spend",
    f"₹{budget_info['current_spend_inr']:.0f} / ₹{budget_info['ceiling_inr']:.0f}",
    delta=f"₹{budget_info['remaining_budget_inr']:.0f} left",
)

# Navigation Menu - Primary View is 1-Click Daily Autopilot!
PAGES = [
    "⚡ 1-Click Daily Viral Hub (2 Videos/Day)",
    "1. Overview & Pipeline Status",
    "2. Niche & Competitors",
    "3. Topic Discovery & Scoring",
    "4. Script Editor & Claim Ledger",
    "5. Asset & License Library",
    "6. Voiceover & Sound Design",
    "7. Final Video Review & Approval",
    "8. YouTube Auto-Publishing",
    "9. Channel Analytics & Learning",
    "10. Monetization & Cost Calculator",
    "11. Settings & Channel Credentials",
]

selected_page = st.sidebar.radio("Navigate Studio", PAGES)
st.sidebar.divider()
st.sidebar.caption("Pacing: 3s Ken Burns Cuts")
st.sidebar.caption("Sound Design: Drone + Boom + Whoosh")
st.sidebar.caption("Captions: Kinetic Gold Subtitles")


# ==============================================================================
# PRIMARY VIEW: 1-CLICK DAILY VIRAL HUB (2 VIDEOS / DAY WITH CLIFFHANGER)
# ==============================================================================
if selected_page == "⚡ 1-Click Daily Viral Hub (2 Videos/Day)":
    st.header("⚡ 1-Click Daily Viral Production Hub")
    st.markdown(
        "**Zero Hassle Production:** Generates **2 linked viral videos per day** (Part 1 + Part 2) with "
        "dynamic Ken Burns camera push zooms, multi-track sound design (sub-bass drone + impact hits + whooshes), "
        "burned-in kinetic gold subtitles, and a heart-stopping cliffhanger open loop."
    )

    topics = TopicRepository.list_topics()
    col_ctrl1, col_ctrl2 = st.columns([3, 1])

    with col_ctrl1:
        selected_topic_idx = st.selectbox(
            "Select Today's Topic Story Arc (or let Autopilot pick the top-ranked idea):",
            range(len(topics)),
            format_func=lambda i: f"#{topics[i].id} - {topics[i].title} ({topics[i].category_pillar}) - Score: {topics[i].total_score:.0f}/100",
        )
        selected_topic = topics[selected_topic_idx]

    with col_ctrl2:
        st.write("")
        st.write("")
        run_daily = st.button("🚀 Produce Today's 2 Viral Videos", type="primary", use_container_width=True)

    if run_daily:
        with st.status("🎬 Producing 2 Viral Videos (Part 1 & Part 2)...", expanded=True) as status:
            st.write("1. Generating linked 2-part cliffhanger script & claim ledger...")
            time_start = st.empty()
            res = DailyAutopilot.produce_daily_two_part_batch(topic_id=selected_topic.id)
            if res.get("success"):
                status.update(label="✅ Both Videos Rendered & Ready for Approval!", state="complete", expanded=False)
                st.success(f"Produced 2 Videos in {res['total_render_time_sec']}s! Preview and approve below.")
                st.rerun()
            else:
                status.update(label="❌ Production Error", state="error")
                st.error(res.get("error"))

    st.divider()

    auth_status = YouTubeAuthManager.get_auth_status()
    if auth_status["is_authenticated"]:
        st.success("🟢 **YouTube Channel Connected:** `Apex op legend` — Ready for 1-click automated publishing!")
    else:
        st.warning("⚠️ YouTube Channel Not Connected. Connect in Settings or use the instant ZIP package.")

    if "last_upload_url" in st.session_state:
        st.success(f"🚀 **Successfully Uploaded Video!** Watch in YouTube Studio: [{st.session_state['last_upload_url']}]({st.session_state['last_upload_url']})")

    # Look for the latest Part 1 and Part 2 exports in exports directory
    exports = VideoExportRepository.list_exports()
    part1_export = next((e for e in exports if "Part1" in e.file_path and Path(e.file_path).exists()), None)
    part2_export = next((e for e in exports if "Part2" in e.file_path and Path(e.file_path).exists()), None)

    if part1_export and part2_export:
        col_hdr1, col_hdr2 = st.columns([3, 1])
        col_hdr1.subheader("📺 Today's 2 Viral Videos (Ready for 1-Click Approval & Auto-Publishing)")
        upload_privacy = col_hdr2.selectbox("Upload Visibility", ["private", "unlisted", "public"], index=0, help="Default is Private for safe review in YouTube Studio before going Public.")

        p1_script = ScriptRepository.get_script(part1_export.script_id)
        p2_script = ScriptRepository.get_script(part2_export.script_id)

        c_v1, c_v2 = st.columns(2)

        # ----------------------------- PART 1 CARD -----------------------------
        with c_v1:
            st.markdown("### 🔴 Video 1 — Part 1: The Setup & The Trap")
            st.caption(f"**Duration:** {part1_export.duration_sec:.1f}s | **Resolution:** 1080p 16:9 | **Size:** {part1_export.file_size_bytes / 1024 / 1024:.1f} MB")
            st.video(part1_export.file_path)

            st.markdown(f"**Title:** `{p1_script.title if p1_script else 'Part 1'}`")
            st.info("🔥 **Retention Engine:** Ends with high-tension unresolved cliffhanger forcing viewers to click Part 2!")

            # Approval Status
            p1_approval = ApprovalRepository.get_active_approval(part1_export.script_id)
            is_p1_approved = p1_approval and p1_approval.content_hash == part1_export.content_hash

            if is_p1_approved:
                st.success(f"✅ Approved by {p1_approval.approved_by}")
            else:
                if st.button("🚀 Approve & Auto-Publish Part 1", key="btn_app_p1", type="primary", use_container_width=True):
                    with st.spinner("Recording approval and uploading to your YouTube channel..."):
                        approval = HumanApproval(
                            script_id=part1_export.script_id,
                            video_export_id=part1_export.id,
                            content_hash=part1_export.content_hash,
                            approved_by="Channel Lead",
                            approval_notes="Approved Part 1 viral cut.",
                            is_valid=True,
                        )
                        ApprovalRepository.record_approval(approval)

                        # Trigger auto-upload
                        if auth_status["is_authenticated"]:
                            up_res = YouTubePublisher.upload_video_via_api(
                                video_export_id=part1_export.id,
                                title=p1_script.title if p1_script else "Part 1",
                                description=(
                                    f"{p1_script.hook_text}\n\n"
                                    f"TIMESTAMPS:\n"
                                    f"00:00 - The Unseen Trap\n"
                                    f"00:30 - The Monopoly Era\n"
                                    f"01:10 - The Hidden Wall Street Deal\n"
                                    f"01:45 - The Fatal Flaw\n\n"
                                    f"Watch Part 2 for the final verdict!\n\n"
                                    f"Educational and analytical documentary. Narration generated with neural voice technology."
                                ),
                                tags="business case study, corporate autopsy, economics, modernmba",
                                privacy_status=upload_privacy,
                            )
                            if up_res.get("success"):
                                st.session_state["last_upload_url"] = up_res["url"]
                            else:
                                st.error(up_res.get("error"))
                        else:
                            pkg = YouTubePublisher.create_manual_upload_package(
                                video_export_id=part1_export.id,
                                title=p1_script.title if p1_script else "Part 1",
                                description="Watch Part 2 for the final verdict.",
                                tags="business, case study, economics",
                                output_zip_path=str(EXPORTS_DIR / f"Upload_Part1_{part1_export.id}.zip"),
                            )
                        st.rerun()

        # ----------------------------- PART 2 CARD -----------------------------
        with c_v2:
            st.markdown("### 🟢 Video 2 — Part 2: The Autopsy & Final Verdict")
            st.caption(f"**Duration:** {part2_export.duration_sec:.1f}s | **Resolution:** 1080p 16:9 | **Size:** {part2_export.file_size_bytes / 1024 / 1024:.1f} MB")
            st.video(part2_export.file_path)

            st.markdown(f"**Title:** `{p2_script.title if p2_script else 'Part 2'}`")
            st.info("🧠 **Retention Engine:** Opens with recap hook, reveals the smoking-gun SEC filing, and delivers the permanent lesson!")

            # Approval Status
            p2_approval = ApprovalRepository.get_active_approval(part2_export.script_id)
            is_p2_approved = p2_approval and p2_approval.content_hash == part2_export.content_hash

            if is_p2_approved:
                st.success(f"✅ Approved by {p2_approval.approved_by}")
            else:
                if st.button("🚀 Approve & Auto-Publish Part 2", key="btn_app_p2", type="primary", use_container_width=True):
                    with st.spinner("Recording approval and uploading to your YouTube channel..."):
                        approval = HumanApproval(
                            script_id=part2_export.script_id,
                            video_export_id=part2_export.id,
                            content_hash=part2_export.content_hash,
                            approved_by="Channel Lead",
                            approval_notes="Approved Part 2 viral cut.",
                            is_valid=True,
                        )
                        ApprovalRepository.record_approval(approval)

                        if auth_status["is_authenticated"]:
                            up_res = YouTubePublisher.upload_video_via_api(
                                video_export_id=part2_export.id,
                                title=p2_script.title if p2_script else "Part 2",
                                description=(
                                    f"{p2_script.hook_text}\n\n"
                                    f"TIMESTAMPS:\n"
                                    f"00:00 - Recap & The Panic\n"
                                    f"00:25 - The $400M Interest Bloodbath\n"
                                    f"01:00 - The Paralyzed Balance Sheet\n"
                                    f"01:30 - The Chapter 11 Liquidation\n\n"
                                    f"Subscribe to Apex Enterprise for more forensic corporate dissections.\n\n"
                                    f"Educational and analytical documentary. Narration generated with neural voice technology."
                                ),
                                tags="business case study, corporate autopsy, economics, modernmba",
                                privacy_status=upload_privacy,
                            )
                            if up_res.get("success"):
                                st.session_state["last_upload_url"] = up_res["url"]
                            else:
                                st.error(up_res.get("error"))
                        else:
                            pkg = YouTubePublisher.create_manual_upload_package(
                                video_export_id=part2_export.id,
                                title=p2_script.title if p2_script else "Part 2",
                                description="Dissecting the balance sheets and boardroom blunders.",
                                tags="business, case study, economics, modernmba",
                                output_zip_path=str(EXPORTS_DIR / f"Upload_Part2_{part2_export.id}.zip"),
                            )
                        st.rerun()

        st.divider()

        # YouTube Channel Credentials Callout if not connected
        auth = YouTubeAuthManager.get_auth_status()
        if not auth["is_authenticated"]:
            with st.expander("🔑 Connect Your YouTube Channel for 100% Direct Auto-Uploading"):
                st.markdown(
                    """
                    **How to Connect Your YouTube Channel:**
                    1. Go to [Google Cloud Console](https://console.cloud.google.com/) -> **APIs & Services > Credentials**.
                    2. Click **Create Credentials > OAuth client ID** (Application type: **Desktop app**).
                    3. Download the JSON file and save it as **`config/client_secrets.json`**.
                    4. Once saved, click **Authenticate Channel** in **Page 11 (Settings)**.
                    
                    *Once connected, clicking "Approve & Auto-Publish" will automatically push the video directly to your YouTube channel as Private or Unlisted without any manual steps!*
                    """
                )
    else:
        st.info("No 2-part daily series generated yet. Click **'🚀 Produce Today's 2 Viral Videos'** above to generate today's batch in 80 seconds!")


# ==============================================================================
# PAGE 1: OVERVIEW AND PIPELINE STATUS
# ==============================================================================
elif selected_page == "1. Overview & Pipeline Status":
    st.header("📊 Studio Overview & Pipeline Status")
    col1, col2, col3, col4 = st.columns(4)
    topics = TopicRepository.list_topics()
    scripts = ScriptRepository.list_scripts()
    exports = VideoExportRepository.list_exports()
    approved = [s for s in scripts if s.status == "approved"]

    col1.metric("Researched Topics", len(topics))
    col2.metric("Script Drafts", len(scripts))
    col3.metric("Rendered 1080p Videos", len(exports))
    col4.metric("Approved for Publishing", len(approved))

    st.subheader("Recent Video Library")
    for exp in exports[:4]:
        with st.expander(f"🎬 {Path(exp.file_path).name} ({exp.duration_sec:.1f}s - {exp.resolution})"):
            st.write(f"**File Size:** {exp.file_size_bytes / 1024 / 1024:.2f} MB | **Hash:** `{exp.content_hash[:16]}...`")
            if Path(exp.file_path).exists():
                st.video(exp.file_path)


# ==============================================================================
# PAGE 2: NICHE RESEARCH AND COMPETITOR TRACKING
# ==============================================================================
elif selected_page == "2. Niche & Competitors":
    st.header("🎯 Niche Intelligence & Competitor Tracking")
    st.markdown("Category: **Business Case Studies & Corporate Autopsies** (Score: 92.5/100, Tier-1 RPM: $10 - $25+).")

    competitors = get_competitor_insights()
    for comp in competitors:
        with st.expander(f"📌 {comp['channel_name']} ({comp['subscribers']} subs, {comp['total_views']} views)"):
            c1, c2 = st.columns(2)
            c1.write(f"**Avg Views/Video:** {comp['avg_views_per_video']}")
            c1.write(f"**Upload Cadence:** {comp['upload_frequency']}")
            c2.write(f"**Pacing Style:** {comp['content_style']}")
            st.success(f"**Our Differentiated Edge:** {comp['our_differentiation']}")


# ==============================================================================
# PAGE 3: TOPIC DISCOVERY AND SCORING
# ==============================================================================
elif selected_page == "3. Topic Discovery & Scoring":
    st.header("💡 Topic Opportunity Catalog")
    topics = TopicRepository.list_topics()

    for t in topics:
        with st.container():
            c1, c2, c3 = st.columns([5, 1, 2])
            c1.markdown(f"**{t.title}**")
            c1.caption(f"Pillar: {t.category_pillar} | Angle: {t.angle}")
            c2.metric("Score", f"{t.total_score:.0f}/100")
            if c3.button("Produce 2-Part Series", key=f"top_{t.id}"):
                with st.spinner("Generating Part 1 & Part 2..."):
                    res = DailyAutopilot.produce_daily_two_part_batch(topic_id=t.id)
                    st.success("Produced 2 Viral Videos! Open the 1-Click Viral Hub.")
                    st.rerun()
            st.divider()


# ==============================================================================
# PAGE 4: SCRIPT EDITOR & CLAIM LEDGER
# ==============================================================================
elif selected_page == "4. Script Editor & Claim Ledger":
    st.header("📝 Script Editor & Claim Ledger")
    scripts = ScriptRepository.list_scripts()
    if scripts:
        s_title = st.selectbox("Select Script", [f"#{s.id} - {s.title}" for s in scripts])
        s_id = int(s_title.split()[0].replace("#", ""))
        script = ScriptRepository.get_script(s_id)
        claims = ClaimLedgerRepository.get_claims_for_script(s_id)

        st.write(f"**Word Count:** {script.word_count} | **Est. Duration:** {script.target_duration_sec}s | **Status:** `{script.status}`")
        st.text_area("Opening Hook", value=script.hook_text, height=80)
        st.text_area("Audience Promise", value=script.promise_text, height=60)
        st.text_area("Body & Case Study Evidence", value=script.body_text, height=180)
        st.text_area("Conclusion / Cliffhanger", value=script.conclusion_text, height=80)

        st.subheader("Verified Claims in Ledger")
        for c in claims:
            st.write(f"- **{c.claim_text}** (Source: [{c.source_title}]({c.source_url}))")


# ==============================================================================
# PAGE 5: ASSET AND LICENSING LIBRARY
# ==============================================================================
elif selected_page == "5. Asset & License Library":
    st.header("🖼️ Asset & Licensing Library")
    assets = AssetRepository.list_assets()
    st.write(f"Tracking **{len(assets)}** registered media assets with commercial license provenance.")

    for a in assets[:6]:
        with st.expander(f"📁 {a.name} ({a.asset_type.upper()})"):
            st.write(f"**License:** `{a.license_type}` | **Commercial Use:** {'Allowed ✅' if a.commercial_allowed else 'Restricted ❌'}")
            if Path(a.file_path).exists() and a.file_path.endswith((".png", ".jpg")):
                st.image(a.file_path, width=450)


# ==============================================================================
# PAGE 6: VOICEOVER & SOUND DESIGN
# ==============================================================================
elif selected_page == "6. Voiceover & Sound Design":
    st.header("🎙️ Voiceover & Sound Design Studio")
    st.markdown("Multi-track sound design: Neural Voiceover + Sub-Bass Tension Drone + Impact Booms + Whoosh sweeps.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Voiceover Engine")
        st.write("Engine: **Microsoft Edge-TTS** (Ultra-natural neural, 100% free)")
        st.selectbox("Voice Persona", list(AVAILABLE_VOICES.keys()), format_func=lambda k: AVAILABLE_VOICES[k]["name"])

    with col2:
        st.subheader("Cinematic Sound Design FX")
        sfx = SoundDesigner.ensure_sfx_library()
        for name, path in sfx.items():
            st.write(f"**{name.replace('_', ' ').title()}:**")
            if Path(path).exists():
                st.audio(path)


# ==============================================================================
# PAGE 7: FINAL VIDEO REVIEW & APPROVAL
# ==============================================================================
elif selected_page == "7. Final Video Review & Approval":
    st.header("🛡️ Final Video Review & Human Sign-off")
    exports = VideoExportRepository.list_exports()
    if exports:
        sel_exp = st.selectbox("Select Video Export", [f"Export #{e.id} - {Path(e.file_path).name} ({e.duration_sec:.1f}s)" for e in exports])
        exp_id = int(sel_exp.split()[1].replace("#", ""))
        export = next(e for e in exports if e.id == exp_id)

        st.video(export.file_path)
        st.caption(f"Content SHA-256: `{export.content_hash}`")

        approval = ApprovalRepository.get_active_approval(export.script_id)
        if approval and approval.content_hash == export.content_hash:
            st.success(f"✅ Approved by {approval.approved_by} on {approval.approved_at}")
        else:
            if st.button("✅ Grant Official Human Approval", type="primary"):
                app = HumanApproval(script_id=export.script_id, video_export_id=export.id, content_hash=export.content_hash, approved_by="Channel Lead")
                ApprovalRepository.record_approval(app)
                st.success("Approval recorded successfully!")
                st.rerun()


# ==============================================================================
# PAGE 8: YOUTUBE AUTO-PUBLISHING
# ==============================================================================
elif selected_page == "8. YouTube Auto-Publishing":
    st.header("📤 YouTube Auto-Publishing & Direct Uploads")
    auth_status = YouTubeAuthManager.get_auth_status()
    st.write(f"OAuth Authentication Status: {'Connected ✅' if auth_status['is_authenticated'] else 'Not Authenticated ❌'}")

    exports = VideoExportRepository.list_exports()
    if exports:
        sel_exp = st.selectbox("Select Video to Upload", [f"Export #{e.id} - {Path(e.file_path).name}" for e in exports], key="pub_sel")
        exp_id = int(sel_exp.split()[1].replace("#", ""))
        export = next(e for e in exports if e.id == exp_id)
        script = ScriptRepository.get_script(export.script_id)

        col_u1, col_u2 = st.columns(2)
        with col_u1:
            st.markdown("### Direct YouTube API Upload")
            privacy = st.selectbox("Privacy State", ["private", "unlisted", "public"])
            if st.button("🚀 Push to YouTube Channel", disabled=not auth_status["is_authenticated"]):
                res = YouTubePublisher.upload_video_via_api(
                    video_export_id=exp_id,
                    title=script.title if script else "Documentary",
                    description=script.body_text if script else "",
                    tags="business, case study, economics",
                    privacy_status=privacy,
                )
                if res.get("success"):
                    st.success(f"Uploaded! Video URL: {res['url']}")
                else:
                    st.error(res.get("error"))

        with col_u2:
            st.markdown("### Manual Upload Package ZIP (Zero Quota)")
            zip_out = str(EXPORTS_DIR / f"Manual_Package_{exp_id}.zip")
            if st.button("📦 Generate Upload ZIP Package"):
                pkg = YouTubePublisher.create_manual_upload_package(
                    video_export_id=exp_id,
                    title=script.title if script else "Documentary",
                    description=script.body_text if script else "",
                    tags="business, case study, economics",
                    output_zip_path=zip_out,
                )
                with open(pkg, "rb") as f:
                    st.download_button("⬇️ Download ZIP Package", data=f, file_name=f"Upload_{exp_id}.zip", mime="application/zip")


# ==============================================================================
# PAGE 9: CHANNEL ANALYTICS & LEARNING
# ==============================================================================
elif selected_page == "9. Channel Analytics & Learning":
    st.header("📈 Channel Analytics & Retention Learning Loop")
    snapshots = AnalyticsRepository.list_snapshots()
    if snapshots:
        latest = snapshots[-1]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lifetime Views", f"{latest.channel_views:,}")
        c2.metric("Watch Hours", f"{latest.watch_time_hours:,.0f}h")
        c3.metric("CTR %", f"{latest.ctr_pct}%")
        c4.metric("Audience Retention", f"{latest.avg_pct_viewed}%")

        loop = LearningLoop.generate_recommendations()
        if loop.get("has_data"):
            st.subheader("Algorithm Optimization Insights")
            for tip in loop["actionable_tips"]:
                st.info(f"💡 {tip}")


# ==============================================================================
# PAGE 10: MONETIZATION & COST CALCULATOR
# ==============================================================================
elif selected_page == "10. Monetization & Cost Calculator":
    st.header("💰 Monetization Strategy & Budget Protection")
    status = CostManager.get_spending_status()
    st.metric("Operating Spend", f"₹{status['current_spend_inr']:.0f} / ₹{status['ceiling_inr']:.0f}")

    st.subheader("Revenue Milestone Calculator")
    m_views = st.slider("Monthly Views", 20000, 500000, 150000, step=10000)
    m_rpm = st.slider("Assumed RPM ($ USD)", 8.0, 30.0, 15.0, step=1.0)
    proj = calculate_revenue_projections(m_views, m_rpm)

    c1, c2, c3 = st.columns(3)
    c1.metric("Gross Revenue (USD)", f"${proj['gross_usd']:,.2f}")
    c2.metric("Gross Revenue (INR)", f"₹{proj['gross_inr']:,.0f}")
    c3.metric("Net Profit (INR)", f"₹{proj['net_profit_inr']:,.0f}")

    st.info(
        f"🎯 Views needed for **₹1,00,000/mo**: ~**{proj['milestones']['views_needed_for_1_lakh_inr']:,}** views. "
        f"Views needed for **₹5,00,000/mo**: ~**{proj['milestones']['views_needed_for_5_lakh_inr']:,}** views."
    )


# ==============================================================================
# PAGE 11: SETTINGS & CHANNEL CREDENTIALS
# ==============================================================================
elif selected_page == "11. Settings & Channel Credentials":
    st.header("⚙️ Channel Credentials & YouTube Authorization")
    auth_status = YouTubeAuthManager.get_auth_status()

    st.subheader("YouTube Channel OAuth Connection")
    st.write(f"**Client Secrets File:** `{auth_status['secrets_path']}` ({'Found ✅' if auth_status['has_secrets_file'] else 'Missing ❌'})")
    st.write(f"**Token File:** `{auth_status['token_path']}` ({'Active ✅' if auth_status['is_authenticated'] else 'Inactive ❌'})")

    if auth_status["has_secrets_file"] and not auth_status["is_authenticated"]:
        if st.button("🔗 Authorize YouTube Channel in Browser", type="primary"):
            with st.spinner("Opening Google login in your browser..."):
                res = YouTubeAuthManager.authenticate_channel()
                if res.get("success"):
                    st.success("YouTube Channel successfully authorized!")
                    st.rerun()
                else:
                    st.error(f"Authorization error: {res.get('error')}")

    if auth_status["is_authenticated"]:
        st.success("🎉 YouTube Channel is Connected! When you click 'Approve & Auto-Publish' in the 1-Click Viral Hub, videos will automatically upload to your channel.")

    with st.expander("📝 How to Connect Your YouTube Channel for Auto-Uploading", expanded=not auth_status["is_authenticated"]):
        st.markdown(
            """
            1. Open [Google Cloud Console](https://console.cloud.google.com/).
            2. Enable **YouTube Data API v3**.
            3. Go to **Credentials > Create Credentials > OAuth client ID** (Application type: **Desktop app**).
            4. Download the JSON file and place it at:
               `c:\\Users\\Sohail\\Antigravity\\faceless-media-studio\\config\\client_secrets.json`
            5. Once placed, any video you approve in the **1-Click Viral Hub** will automatically push to your channel!
            """
        )

    st.divider()
    st.subheader("System Paths")
    st.write(f"**FFmpeg:** `{get_ffmpeg_path()}`")
    st.write(f"**Exports:** `{EXPORTS_DIR}`")
    st.write(f"**Projects:** `{PROJECTS_DIR}`")
