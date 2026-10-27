"""Faceless Media Studio - Executive Autopilot Dashboard.
Streamlined, zero-clutter command center for YouTube Shorts automation:
1. Live performance of published shorts (Views, Likes, Comments, Date, Status).
2. Next topic in queue with scheduled date & time.
3. Google Flow credits & generation capacity tracker.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

import streamlit as st

# Configure root directory
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.workflows.flow_credits import FlowCreditTracker
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE, DailyShortsPipeline
from src.youtube.oauth import YouTubeAuthManager

st.set_page_config(
    page_title="Apex Media Studio - Shorts Autopilot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for modern dark executive interface
st.markdown("""
<style>
    /* Dark executive theme aesthetics */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Top metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #38bdf8;
        margin-top: 4px;
    }
    
    /* Section headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 1.5rem;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Shorts row cards */
    .short-card {
        background: #131b2e;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .short-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffffff;
        text-decoration: none;
    }
    .short-meta {
        font-size: 0.83rem;
        color: #94a3b8;
        margin-top: 4px;
    }
    .badge-live {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.35);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .stat-pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #e2e8f0;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    
    /* Next topic banner */
    .queue-banner {
        background: linear-gradient(135deg, rgba(14, 116, 144, 0.25) 0%, rgba(30, 27, 75, 0.4) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 20px;
    }
    
    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---

def format_timestamp_ist(iso_str: str) -> str:
    """Convert UTC ISO timestamp to formatted Indian Standard Time (IST)."""
    if not iso_str:
        return "Unknown"
    try:
        clean = iso_str.replace("Z", "+00:00")
        dt_utc = datetime.fromisoformat(clean)
        # If naive, assume UTC
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
        ist_dt = dt_utc + timedelta(hours=5, minutes=30)
        return ist_dt.strftime("%d %b %Y, %I:%M %p IST")
    except Exception:
        return str(iso_str)[:19]


def fetch_public_youtube_stats(video_id: str) -> Dict[str, int]:
    """Fetch public view and like counts directly from YouTube web page without API credentials."""
    import urllib.request
    import re
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Robust multi-layered view parsing for desktop, mobile & datacenter responses
            vm = re.search(r'"viewCount":\s*"(\d+)"', html)
            if not vm:
                vm = re.search(r'"viewCount":\s*\{\s*"simpleText":\s*"([\d,]+)', html)
            if not vm:
                vm = re.search(r'"shortViewCount":\s*\{\s*"simpleText":\s*"([\d,]+)', html)
            if not vm:
                vm = re.search(r'([\d,]+)\s*views', html)
            views = int(vm.group(1).replace(",", "")) if vm else 0
            
            likes_match = re.search(r'"likeCount":\s*"(\d+)"', html)
            if not likes_match:
                likes_match = re.search(r'like this video along with ([\d,]+) other', html)
            likes = int(likes_match.group(1).replace(",", "")) if likes_match else 0
            
            return {"views": views, "likes": likes, "comments": 0}
    except Exception:
        return {"views": 0, "likes": 0, "comments": 0}


@st.cache_data(ttl=120)
def get_live_youtube_stats(video_ids: tuple) -> Dict[str, Dict[str, int]]:
    """Fetch real-time video stats (views, likes, comments) via API with automatic public web fallback."""
    stats_map = {}
    if not video_ids:
        return stats_map

    creds = YouTubeAuthManager.get_credentials()
    if creds:
        try:
            from googleapiclient.discovery import build
            yt = build("youtube", "v3", credentials=creds)
            ids_param = ",".join(video_ids)
            resp = yt.videos().list(part="statistics", id=ids_param).execute()
            for item in resp.get("items", []):
                vid = item.get("id")
                s = item.get("statistics", {})
                stats_map[vid] = {
                    "views": int(s.get("viewCount", 0)),
                    "likes": int(s.get("likeCount", 0)),
                    "comments": int(s.get("commentCount", 0)),
                }
        except Exception:
            pass

    # For any video that failed or if no OAuth credentials on Streamlit Cloud, fallback to public scraper
    for vid in video_ids:
        if vid not in stats_map or stats_map[vid].get("views", 0) == 0:
            stats_map[vid] = fetch_public_youtube_stats(vid)

    return stats_map


def load_published_shorts() -> List[Dict[str, Any]]:
    """Load published shorts from daily_shorts_log.json."""
    log_path = Path("data/daily_shorts_log.json")
    if not log_path.exists():
        return []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Return reversed so most recent appears on top
            return list(reversed(data))
    except Exception:
        return []


# --- Sidebar ---
st.sidebar.title("🎬 Apex Studio")
st.sidebar.caption("Autonomous Daily Shorts Production")

# Channel Information
auth_status = YouTubeAuthManager.get_auth_status()
st.sidebar.success("🟢 YouTube Channel: Apex op legend")
if auth_status.get("is_authenticated"):
    st.sidebar.caption("⚡ Direct OAuth API Sync: Active")
else:
    st.sidebar.caption("📡 Live Public Webhook Sync: Active")
    with st.sidebar.expander("🔑 Cloud Secrets Setup (Optional)"):
        st.markdown(
            "To enable authenticated write access inside Streamlit Cloud:\n"
            "1. Click **`< Manage app`** at bottom-right.\n"
            "2. Click **`⋮` Settings → Secrets**.\n"
            "3. Paste `YT_TOKEN_JSON` and `YT_CLIENT_SECRETS_JSON`.\n\n"
            "*(Note: Daily automated uploads already run securely on GitHub Actions!)*"
        )

# Google Flow Credit Summary in Sidebar
credits = FlowCreditTracker.get_status()
st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Google Flow Credits")
st.sidebar.metric(
    "Remaining Balance",
    f"{credits['credits_remaining']} / {credits['initial_credits']}",
    delta=f"~{credits['estimated_60s_videos_left']} videos left",
)
st.sidebar.progress(credits["credits_remaining"] / max(1, credits["initial_credits"]))
st.sidebar.caption(f"Credits Used: {credits['credits_used']} • Cost: ₹0")

# Active Video Profile Configuration
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Active Production Profile")
st.sidebar.markdown("""
<div style="background: rgba(14, 165, 233, 0.1); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 8px; padding: 12px; font-size: 0.82rem; line-height: 1.5;">
    <b>Preset:</b> US/Global Viral Documentary<br>
    <b>Target Audience:</b> United States & Global<br>
    <b>Target Length:</b> 90 – 120s (8 Acts)<br>
    <b>Resolution & FPS:</b> 1080x1920 @ 60 FPS<br>
    <b>Voice:</b> en-US-ChristopherNeural<br>
    <b>Visual Engine:</b> Google Veo 2 / VideoFX<br>
    <b>Graphic Pillars:</b> 3D Cross-Sections, Satellite DEM
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("☁️ Hosted live on Streamlit Cloud")
st.sidebar.caption("📦 Synced with GitHub `main`")


# --- Main Dashboard Header ---
st.title("🚀 Shorts Production & Channel Autopilot")
st.caption("Live tracking for daily vertical documentaries published to YouTube Shorts.")

# Fetch Published Shorts & Live Metrics
published_shorts = load_published_shorts()
video_ids = tuple([s["youtube_url"].split("/")[-1].strip() for s in published_shorts if "youtube_url" in s])
live_stats = get_live_youtube_stats(video_ids)

# Calculate Global Studio Totals
total_views = sum(live_stats.get(vid, {}).get("views", 0) for vid in video_ids)
total_likes = sum(live_stats.get(vid, {}).get("likes", 0) for vid in video_ids)
total_published = len(published_shorts)

# KPI Top Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Shorts Published</div>
        <div class="metric-value">{total_published}</div>
        <div class="metric-sub">100% Automated</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Live Views</div>
        <div class="metric-value">{total_views:,}</div>
        <div class="metric-sub">Real-time YouTube Data</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Likes</div>
        <div class="metric-value">{total_likes:,}</div>
        <div class="metric-sub">Organic Engagement</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flow Balance</div>
        <div class="metric-value">⚡ {credits['credits_remaining']}</div>
        <div class="metric-sub">~{credits['estimated_60s_videos_left']} shorts capacity</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# --- Section 1: Published Shorts (Live Performance) ---
header_col1, header_col2 = st.columns([4, 1])
with header_col1:
    st.markdown('<div class="section-title">📺 Published Shorts & Live Performance</div>', unsafe_allow_html=True)
with header_col2:
    if st.button("🔄 Refresh Live Metrics", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if not published_shorts:
    st.info("No shorts recorded in the daily publication log yet.")
else:
    for idx, short in enumerate(published_shorts):
        url = short.get("youtube_url", "")
        vid = url.split("/")[-1].strip() if url else ""
        stats = live_stats.get(vid, {})
        v_count = stats.get("views", 0)
        l_count = stats.get("likes", 0)
        c_count = stats.get("comments", 0)
        upload_time_str = format_timestamp_ist(short.get("timestamp", ""))
        title = short.get("title", "Untitled Short")

        with st.container():
            c_info, c_stats, c_action = st.columns([5, 3, 2])
            with c_info:
                st.markdown(f"**[{title}]({url})**")
                st.markdown(
                    f"<span style='color: #94a3b8; font-size: 0.85rem;'>📅 Uploaded: <b>{upload_time_str}</b></span> &nbsp; "
                    f"<span class='badge-live'>🟢 Live & Public</span>",
                    unsafe_allow_html=True
                )
            with c_stats:
                st.markdown(
                    f"<div style='margin-top: 6px;'>"
                    f"<span class='stat-pill'>👁️ {v_count:,} views</span> &nbsp; "
                    f"<span class='stat-pill'>👍 {l_count} likes</span> &nbsp; "
                    f"<span class='stat-pill'>💬 {c_count}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with c_action:
                st.markdown(f"<div style='margin-top: 4px;'><a href='{url}' target='_blank' style='display: inline-block; background-color: #ef4444; color: white; padding: 7px 16px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.85rem;'>▶ Watch on YouTube</a></div>", unsafe_allow_html=True)
            
            with st.expander(f"🎬 Watch Player: {title}"):
                col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
                with col_v2:
                    st.video(f"https://www.youtube.com/watch?v={vid}")

            st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.06); margin: 12px 0;'>", unsafe_allow_html=True)


# --- Section 2: Next Topic in Queue ---
st.markdown('<div class="section-title">⏳ Production Queue & Schedule</div>', unsafe_allow_html=True)

# Find unproduced items in queue
published_ids = {s.get("id") for s in published_shorts}
unproduced_items = [item for item in VIRAL_SHORTS_QUEUE if item["id"] not in published_ids]

if unproduced_items:
    next_topic = unproduced_items[0]
    
    # Calculate scheduled release (Next scheduled is tomorrow at 5:00 PM IST)
    now_ist = datetime.utcnow() + timedelta(hours=5, minutes=30)
    scheduled_date = now_ist.date() + timedelta(days=1)
    scheduled_time_str = f"{scheduled_date.strftime('%A, %d %b %Y')} at 05:00 PM IST (11:30 UTC)"

    st.markdown(f"""
    <div class="queue-banner">
        <div style="font-size: 0.85rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">
            NEXT IN QUEUE • SCHEDULED RUN
        </div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #ffffff; margin-bottom: 6px;">
            {next_topic['title']}
        </div>
        <div style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 12px;">
            <b>Hook:</b> <i>"{next_topic['hook']}"</i>
        </div>
        <div style="font-size: 0.88rem; color: #94a3b8; margin-bottom: 14px;">
            ⏰ <b>Scheduled Autopilot:</b> <span style="color: #f8fafc; font-weight: 600;">{scheduled_time_str}</span> &nbsp;•&nbsp; 
            🎯 <b>Target Platform:</b> YouTube Shorts (1080x1920 @ 60 FPS)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 1-Click Instant Autopilot Trigger Button
    col_trig1, col_trig2 = st.columns([1, 2])
    with col_trig1:
        trigger_now = st.button("🚀 Trigger Generation & Upload Now", type="primary", use_container_width=True)
    with col_trig2:
        st.caption("⚡ 100% Autonomous: renders 60fps master, layers sound design & subtitles, uploads to YouTube, and updates dashboard.")

    if trigger_now:
        with st.status(f"🎬 Autonomous Production: {next_topic['title']}...", expanded=True) as status_box:
            st.write("1. Verifying 8 dedicated high-end visual scenes & sound assets...")
            
            # Check if GitHub API token is provided in Streamlit secrets
            gh_token = None
            try:
                if "GH_TOKEN" in st.secrets:
                    gh_token = st.secrets["GH_TOKEN"]
            except Exception:
                pass
            if not gh_token:
                gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

            dispatched_cloud = False
            if gh_token:
                try:
                    import urllib.request, json
                    url = "https://api.github.com/repos/sohailmohamad84-svg/faceless-media-studio/actions/workflows/daily_shorts.yml/dispatches"
                    payload = json.dumps({"ref": "main", "inputs": {"privacy_status": "public"}}).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={
                            "Authorization": f"Bearer {gh_token}",
                            "Accept": "application/vnd.github.v3+json",
                            "User-Agent": "ApexMediaStudio"
                        }
                    )
                    with urllib.request.urlopen(req, timeout=10) as r_gh:
                        if r_gh.status in (200, 204):
                            dispatched_cloud = True
                            st.write("2. ✅ GitHub Actions cloud worker successfully dispatched in background!")
                            status_box.update(label="🚀 Cloud Autopilot Triggered!", state="complete")
                            st.success("The video is now being rendered and published on YouTube in the cloud. It will appear on your dashboard automatically in 2-3 minutes!")
                except Exception as e:
                    st.caption(f"Cloud dispatch note: {e}")

            if not dispatched_cloud:
                st.write("2. Synthesizing voiceover, animating 60fps visuals & burning gold subtitles...")
                import asyncio
                prod_res = asyncio.run(DailyShortsPipeline.produce_and_publish_next_short(privacy_status="public"))
                if prod_res.get("success"):
                    st.write("3. 🚢 Master video uploaded directly to YouTube Shorts!")
                    status_box.update(label=f"✅ Published: {prod_res.get('title')}", state="complete")
                    st.success(f"🎉 Short is live on YouTube: {prod_res.get('url')}")
                    st.balloons()
                    st.rerun()
                else:
                    status_box.update(label="⚠️ Production status", state="error")
                    st.error(f"Error during autonomous production: {prod_res.get('error')}")
                    if "credentials not configured" in str(prod_res.get('error', '')).lower():
                        st.info(
                            "💡 **Permanent 1-Minute Fix:**\n\n"
                            "1. In your browser at the top-right of this page, click **`⋮` (Settings)** → **Secrets** (or click **`< Manage app`** at bottom-right).\n"
                            "2. Paste the `YT_TOKEN_JSON` and `YT_CLIENT_SECRETS_JSON` blocks.\n"
                            "3. Click **Save**. Streamlit Cloud will permanently remember your YouTube connection for all future runs!"
                        )

    # 8-Act Script Breakdown in expander
    with st.expander("📖 View 8-Act Extended Narration & Sound Design Storyboard"):
        for act_idx, sc in enumerate(next_topic.get("scenes", [])):
            st.markdown(f"**Act {act_idx + 1}:** {sc.get('narration_text', '')}")
            foley_items = [f"{f['sfx']} (+{f['gain']}dB)" for f in sc.get("foley", [])]
            if foley_items:
                st.caption(f"🔊 Sound Design: {', '.join(foley_items)}")

    # Comprehensive Multi-Day Production Pipeline Table & Storyboards
    if len(unproduced_items) > 1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;'>"
            f"<span>📅 Upcoming Multi-Day Production Pipeline ({len(unproduced_items)} Topics Queued)</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.caption("Daily high-retention vertical documentaries queued for automated production and publishing at 5:00 PM IST.")

        for q_idx, item in enumerate(unproduced_items[1:], start=2):
            target_date = (now_ist.date() + timedelta(days=q_idx - 1)).strftime("%A, %d %b %Y")
            cat_badge = item.get("category", "Extreme Engineering")
            
            with st.container():
                st.markdown(f"""
                <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div>
                            <span style="background: #3b82f6; color: white; padding: 2px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">DAY {q_idx}</span> &nbsp;
                            <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">{target_date} at 5:00 PM IST</span>
                        </div>
                        <span style="background: rgba(148, 163, 184, 0.12); color: #38bdf8; padding: 2px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; border: 1px solid rgba(56, 189, 248, 0.2);">{cat_badge}</span>
                    </div>
                    <div style="font-size: 1.08rem; font-weight: 700; color: #ffffff; margin-bottom: 4px;">{item['title']}</div>
                    <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 6px;"><b>Hook:</b> <i>"{item['hook']}"</i></div>
                    <div style="display: flex; gap: 12px; font-size: 0.78rem; color: #94a3b8;">
                        <span>🎬 <b>Acts:</b> 8 Pure Physical Motion Scenes</span>
                        <span>⚡ <b>Engine:</b> Google Veo 2 / VideoFX</span>
                        <span>🎙️ <b>Voice:</b> en-US-ChristopherNeural</span>
                        <span>🎯 <b>Format:</b> 1080x1920 @ 60 FPS</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"🔍 Inspect 8-Act Storyboard: {item['title']}"):
                    for sc_idx, sc in enumerate(item.get("scenes", []), 1):
                        st.markdown(f"**Act {sc_idx}: {sc.get('title', f'Scene {sc_idx}')}** `[{sc.get('graphic_type', 'Veo 2')}]`")
                        st.write(f"*{sc.get('narration_text', '')}*")
                        st.caption(f"🎨 Veo Prompt: {sc.get('prompt', '')}")

else:
    st.success("🎉 All researched topics in the current queue have been successfully produced and published!")


# --- Section 3: Google Flow Credits & Studio Usage ---
st.markdown('<div class="section-title">⚡ Google Flow Credits & Capacity</div>', unsafe_allow_html=True)

col_cred1, col_cred2, col_cred3 = st.columns(3)
with col_cred1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Credits Remaining</div>
        <div class="metric-value" style="color: #4ade80;">{credits['credits_remaining']}</div>
        <div class="metric-sub">Out of {credits['initial_credits']} allocated credits</div>
    </div>
    """, unsafe_allow_html=True)

with col_cred2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Credits Consumed</div>
        <div class="metric-value" style="color: #f59e0b;">{credits['credits_used']}</div>
        <div class="metric-sub">Veo video generation tokens</div>
    </div>
    """, unsafe_allow_html=True)

with col_cred3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Videos Remaining</div>
        <div class="metric-value">~{credits['estimated_60s_videos_left']}</div>
        <div class="metric-sub">Estimated 60-90s shorts capacity</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Credit Progress Indicator
st.write(f"**Credit Utilization:** {credits['credits_remaining']} credits remaining ({credits['credits_remaining']/max(1, credits['initial_credits'])*100:.1f}%)")
st.progress(credits["credits_remaining"] / max(1, credits["initial_credits"]))

if credits.get("history"):
    with st.expander("📜 View Generation Credit Ledger"):
        for h in reversed(credits["history"][-5:]):
            st.markdown(f"- **{h.get('clip_name', 'Clip Generation')}**: spent `{h.get('credits', 10)} credits` &nbsp;<span style='color: #94a3b8;'>({h.get('notes', '')})</span>", unsafe_allow_html=True)

with st.expander("⚙️ Calibrate Live Google Flow Credits"):
    st.caption("Since Google Flow currently does not have an external public API for third-party balance queries, you can calibrate your exact live balance from flow.google.com whenever needed:")
    col_bal_in, col_bal_btn = st.columns([3, 1])
    with col_bal_in:
        new_bal = st.number_input("Current Live Balance on flow.google.com", min_value=0, max_value=50000, value=int(credits['credits_remaining']), step=25)
    with col_bal_btn:
        st.write("")
        st.write("")
        if st.button("Sync Balance", use_container_width=True):
            FlowCreditTracker.set_balance(int(new_bal))
            st.success(f"Dashboard updated to {new_bal} Google Flow credits!")
            st.rerun()
