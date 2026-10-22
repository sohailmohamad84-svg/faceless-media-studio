# Faceless Media Studio 🎬

> **Local-First, AI-Assisted YouTube Production Studio for Faceless Documentary Channels.**  
> Built for sustainable audience growth, verified investigative accuracy, procedural visuals, and zero recurring software fees.

---

## 1. Executive Summary & Business Objective

**Faceless Media Studio** is an end-to-end, local-first YouTube production application designed for a creator operating within a **1–2 hour daily window** and a **₹0 starting software budget** (with an absolute ceiling of ₹3,000/month after validation).

### Selected Channel Concept: **Apex Enterprise**
- **Niche:** Business Case Studies, Corporate Autopsies & "The Mechanics of Money"
- **Niche Score:** **92.5 / 100** (Highest ranking across Audience Demand, RPM, Repeatable Supply, and Copyright Safety)
- **Format:** 10–15 minute cinematic documentary case studies (16:9 1080p landscape).
- **Advertiser RPM Range:** **$10.00 – $25.00+ USD** per 1,000 views (Tier-1 global audience).
- **Long-Term Revenue Target:** **₹1,00,000 – ₹5,00,000 / month** (modeled across YouTube AdSense mid-rolls, financial affiliates, and B2B sponsorships).
- **Software Operating Cost Today:** **₹0.00** (100% Free Toolchain).

---

## 2. Key Capabilities & Technical Highlights

1. **Deterministic Pipeline State Machine:**  
   `RESEARCH` → `SCRIPT DRAFT` → `SCRIPT REVIEW` → `ASSET COLLECTION` → `VOICEOVER` → `RENDERING` → `AUTOMATED QA` → `HUMAN VIDEO REVIEW` → `APPROVED` → `UPLOAD / PACKAGE`.
2. **Mandatory Human Approval Gate:**  
   A video can **never** be published automatically. Explicit human sign-off is bound to the exact SHA-256 content hash of the video. Any script or visual edit immediately invalidates prior approvals.
3. **Free-First Audio Engine:**  
   High-definition neural speech powered by **Microsoft Edge-TTS** (`en-US-ChristopherNeural`, `en-US-GuyNeural`) with EBU R128 loudness normalization (-16 LUFS for YouTube) and an offline **pyttsx3 (Windows SAPI5)** failover.
4. **Procedural Financial Visuals:**  
   Generates 1920x1080 cinematic dark-mode financial charts (waterfalls, markup comparisons, trend lines) via Matplotlib, and clickable high-contrast thumbnails via Pillow.
5. **Zero-Quota YouTube Publishing:**  
   Supports both the official **YouTube Data API v3** (with OAuth 2.0 and Private/Unlisted safety defaults) and a **Manual Upload Package** (ZIP with `video.mp4`, `thumbnail.jpg`, and structured `metadata.txt`) that bypasses all API quota restrictions.
6. **Hard Budget Protection Circuit:**  
   Hardcoded ceiling of ₹3,000/month (default budget: ₹0). Every external call checks the budget and blocks actions that exceed it.

---

## 3. Architecture & Project Layout

```
faceless-media-studio/
├── app.py                      # 14-Page Streamlit Management Dashboard
├── run_pilot.py                # Autonomous end-to-end pilot production script
├── requirements.txt            # Pinned dependencies
├── .env.example                # Safe environment configuration template
├── config/
│   └── settings.py             # System paths, budget thresholds, dynamic FFmpeg resolver
├── src/
│   ├── database/               # SQLite ORM, connection manager, foreign keys
│   ├── research/               # 7-metric scoring, topic discovery, competitor analysis
│   ├── scripting/              # Documentary script generator, claim ledger extractor
│   ├── quality/                # 12-point editorial gate, YouTube compliance, media validator
│   ├── tts/                    # VoiceEngine (Edge-TTS + pyttsx3 fallback, loudness normalization)
│   ├── assets/                 # Procedural charts (Matplotlib), thumbnails (Pillow), license tracker
│   ├── editing/                # FFmpeg 9.0 timeline assembly, subtitle generation (.srt)
│   ├── youtube/                # YouTube Data API v3, OAuth 2.0, manual upload packaging
│   ├── analytics/              # Revenue modeling calculator, retention learning loop
│   └── workflows/              # Budget protection manager, daily automated runner
├── docs/                       # Comprehensive documentation
│   ├── architecture.md         # Full technical system architecture
│   ├── niche-research.md       # Evidence-backed niche report + 30 video ideas
│   ├── setup-guide.md          # Step-by-step Windows setup guide
│   ├── api-integrations.md     # Detailed API limits, costs, and licenses
│   ├── copyright-policy.md     # Fair use, YPP policies, and AI disclosure
│   ├── monetization-plan.md    # Financial projections to reach ₹1-5 Lakh/mo
│   └── troubleshooting.md      # Common errors, FFmpeg fixes, and failover
├── data/                       # Persistent SQLite database (`studio.db`)
├── projects/                   # Intermediate audio, charts, slides, thumbnails
├── exports/                    # Rendered 1080p MP4s and upload ZIP packages
├── tests/                      # Automated pytest test suite (12 passed tests)
└── logs/                       # FFmpeg logs, render traces, workflow runs
```

---

## 4. Windows Setup & Quickstart (5 Minutes)

### Prerequisites
- Windows 10 or 11 (64-bit)
- Python 3.11+
- FFmpeg 9.0 (installed via WinGet: `winget install Gyan.FFmpeg.Essentials`)

### Step 1: Clone or Navigate to Directory
```powershell
cd c:\Users\Sohail\Antigravity\faceless-media-studio
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Run Automated Test Suite
Verify that all 12 unit and integration tests pass:
```powershell
python -m pytest -v tests/test_studio.py
```

### Step 4: Launch the Studio Dashboard
```powershell
streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## 5. How to Produce and Publish Your First Video

1. **Step 1: Select Topic:**  
   Open **Page 3 (Topic Discovery)** and review the pre-researched topic backlog. Select *"How Costco's \$1.50 Hot Dog Protects a \$250 Billion Empire"*.
2. **Step 2: Generate Script & Quality Gate:**  
   Click **Generate Script**. Review the hook, context, case study evidence, and conclusion in **Page 4 (Script Editor)**. Review the 12-point editorial scorecard.
3. **Step 3: Generate Neural Voiceover:**  
   Go to **Page 7 (Voiceover Studio)**. Select `ChristopherNeural` and click **Generate Voiceover**. The audio will be synthesized and normalized to -16 LUFS.
4. **Step 4: Generate Procedural Visuals:**  
   Go to **Page 6 (Asset Library)** and click **Generate Costco Financial Charts**.
5. **Step 5: Render 1080p Video:**  
   Go to **Page 9 (Rendering Queue)** and click **Render 1080p Landscape Video**. FFmpeg compiles audio, images, transitions, subtitles, and ambient backing.
6. **Step 6: Review & Human Approval:**  
   Go to **Page 10 (Review & Approval)**. Preview the MP4 video, inspect the claim ledger, and click **Grant Official Human Approval**.
7. **Step 7: YouTube Publishing or Export:**  
   Go to **Page 11 (YouTube Publishing)**. Click **Generate Manual Upload Package** to download `Apex_Enterprise_Upload_Script_1.zip` containing `video.mp4`, `thumbnail.jpg`, and YouTube tags/description.

---

## 6. Free Toolchain vs. Paid Options

| Capability | Current Free Toolchain | Optional Paid Tier (Capped ≤ ₹3,000/mo) |
|---|---|---|
| **Voice Narration** | **Microsoft Edge-TTS** (Ultra-natural neural, 100% free) | ElevenLabs (Only if approved) |
| **Offline Audio** | **pyttsx3 / Windows SAPI5** (Local, zero internet) | Local Piper neural voice |
| **Rendering** | **Direct FFmpeg 9.0** (Open-source, local GPU/CPU) | Cloud render farm (Unnecessary) |
| **Data Visuals** | **Python Matplotlib & Seaborn** (1080p procedural charts) | Paid Figma templates |
| **Thumbnails** | **Pillow Graphic Engine** (High contrast, custom badges) | Adobe Photoshop subscription |
| **Stock Media** | **Procedural Charts + Pexels API + Wikimedia Commons** | Storyblocks ($30/mo - Not needed) |
| **YouTube Upload** | **YouTube Data API v3 + Manual ZIP Package** | Paid social scheduling tools |

---

## 7. Automated Test Suite Results

The project includes an automated test suite executed with `pytest`:

```
============================= test session starts =============================
tests/test_studio.py::test_database_initialization PASSED                [  8%]
tests/test_studio.py::test_topic_scoring_and_normalization PASSED        [ 16%]
tests/test_studio.py::test_topic_discovery_seeding PASSED                [ 25%]
tests/test_studio.py::test_script_generation_and_claim_ledger PASSED     [ 33%]
tests/test_studio.py::test_editorial_quality_gate PASSED                 [ 41%]
tests/test_studio.py::test_policy_and_ai_disclosure_checker PASSED       [ 50%]
tests/test_studio.py::test_budget_protection_circuit PASSED              [ 58%]
tests/test_studio.py::test_asset_generation_procedural_charts PASSED     [ 66%]
tests/test_studio.py::test_thumbnail_designer PASSED                     [ 75%]
tests/test_studio.py::test_human_approval_state_machine_and_invalidation PASSED [ 83%]
tests/test_studio.py::test_revenue_projection_calculator PASSED          [ 91%]
tests/test_studio.py::test_end_to_end_ffmpeg_assembly_and_validation PASSED [100%]
============================= 12 passed in 5.34s ==============================
```

---

## 8. 90-Day Channel Validation Roadmap

- **Month 1 (Videos 1–4):** Publish 4 foundational business autopsies (Costco Hot Dog, Toys 'R' Us Debt Trap, Airline Miles Secret Banks, Lego Turnaround). Validate APV > 40%.
- **Month 2 (Videos 5–8):** Publish 4 competitor duopoly cases (Boeing vs. Airbus, Netflix vs. Blockbuster). Test CTR variations across thumbnail badges.
- **Month 3 (Videos 9–12):** Apply for YouTube Partner Program (YPP). Launch financial and business book affiliate links. Review learning loop retention patterns.

---

## 9. Current Limitations & Honest Disclosure

1. **YouTube API Quota:** Default Google Cloud YouTube API quota is 10,000 units/day (~6 video uploads/day). If quota is exceeded, use the **Manual Upload Package ZIP** export.
2. **AI Voice Disclosure:** Per official YouTube policies, content using neural synthetic speech must check the **Altered or Synthetic Content** checkbox in YouTube Studio. The studio automates this recommendation.
3. **No Speculative Automation:** The studio intentionally does not auto-post without human review. This is by design to protect channel integrity and monetization standing.
