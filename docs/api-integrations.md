# API Integrations & Service Registry

This document records the exact specifications, limits, commercial licenses, costs, and failover behaviors for every external service integrated or supported by **Faceless Media Studio**.

---

## 1. Text-to-Speech (TTS) Integrations

### A. Microsoft Edge-TTS (Primary Free Neural Engine)
- **What it does:** Generates natural-sounding neural speech in English (US/UK) with custom speaking rates, pitch, volume, and sentence-level boundary timestamps.
- **Account Required:** No.
- **API Key Required:** No.
- **Free-Tier Limits:** Free for standard educational and media creation; subject to standard network fair usage.
- **Commercial Use:** Microsoft Edge Voices are distributed for content creation via the Edge speech platform. No attribution token is injected.
- **Expected Cost:** ₹0 / month.
- **Failure Behavior:** If network disconnects or times out, system automatically falls back to **pyttsx3 / Windows SAPI5**.

### B. pyttsx3 / Windows SAPI5 (Offline Fallback Engine)
- **What it does:** Generates speech 100% locally on the host machine using native Windows speech synthesizers (David, Zira, Mark).
- **Account Required:** No.
- **API Key Required:** No.
- **Free-Tier Limits:** Unlimited, completely offline.
- **Commercial Use:** Native Windows voices are licensed as part of the Windows OS license for local audio generation.
- **Expected Cost:** ₹0 / month.
- **Failure Behavior:** Returns descriptive system error if audio device is locked.

### C. ElevenLabs (Optional Paid Tier - Strictly Budget Capped)
- **What it does:** Cloud-based voice cloning and emotional delivery.
- **Account Required:** Yes (user must provide their own API key).
- **Free-Tier Limits:** 10,000 characters per month on free tier (requires attribution).
- **Paid Tier:** \$5/month (~₹415/month) for 30,000 characters.
- **System Policy:** Disabled by default. Can only be enabled if user provides a valid key AND total monthly spending is ≤ ₹3,000 ceiling. System blocks calls if credits exceed ceiling.

---

## 2. YouTube Integrations

### A. YouTube Data API v3 (Uploads, Metadata, Playlists)
- **What it does:** Programmatically uploads rendered videos, sets titles/descriptions/tags, uploads custom thumbnails, and sets scheduled release timestamps.
- **Account Required:** Yes (Google Cloud Console project linked to YouTube Channel).
- **Authorization:** Google OAuth 2.0 (client secrets JSON). Requires `youtube.upload` and `youtube` scopes.
- **Free-Tier Limits:** Default quota is **10,000 units per day**. A video upload costs 1,600 units. A thumbnail set costs 50 units. Free quota permits up to 6 video uploads per day, far exceeding the 1-video/day target.
- **Commercial Use:** Permitted under YouTube API Terms of Service.
- **Expected Cost:** ₹0 / month (Standard Google Cloud free tier).
- **Failure Behavior:** 
  1. Quota exceeded: Application catches HTTP 403 quotaExceeded and generates an exportable "Manual Upload Package" (MP4 + JPG thumbnail + text metadata file) for one-click manual upload via YouTube Studio.
  2. Unauthenticated: Upload button remains locked with visual setup instructions until OAuth consent is completed.

### B. YouTube Analytics API (Performance & Retention)
- **What it does:** Fetches channel-level and video-level views, watch time, impressions, CTR, average view duration (AVD), and traffic sources.
- **Account Required:** Same Google Cloud OAuth credentials.
- **Free-Tier Limits:** Standard project quota (sufficient for periodic automated refreshes).
- **Expected Cost:** ₹0 / month.
- **Failure Behavior:** If token expired or API unavailable, dashboard falls back to cached SQLite historical data or manual CSV import from YouTube Studio.

---

## 3. Stock Media & Visual Asset Integrations

### A. Pexels API (Stock Footage & Photographs)
- **What it does:** Searches and downloads high-definition 1080p B-roll and photography for documentary scene illustration.
- **Account Required:** Yes (Free developer account on Pexels.com).
- **API Key Required:** Yes (Optional free API key).
- **Free-Tier Limits:** 200 requests per hour, 20,000 requests per month (100% free).
- **Commercial Use:** Permitted under Pexels License (Commercial use allowed, no attribution required, but attribution is tracked in our ledger as best practice).
- **Expected Cost:** ₹0 / month.
- **Failure Behavior:** Falls back to procedural charts, local asset cache, or Pixabay/Wikimedia.

### B. Pixabay API (Stock Footage & Illustrations)
- **What it does:** Secondary stock footage, vector graphics, and sound effects library.
- **Account Required:** Yes (Free Pixabay account).
- **Free-Tier Limits:** 5,000 requests per hour.
- **Commercial Use:** Pixabay Content License permits commercial use without copyright attribution.
- **Expected Cost:** ₹0 / month.
- **Failure Behavior:** Skips and utilizes local procedural visuals.

### C. Wikimedia Commons API
- **What it does:** Retrieves historical corporate photos, patents, public SEC exhibits, and founder portraits.
- **Account Required:** No.
- **API Key Required:** No (User-Agent header required).
- **Commercial Use:** Content is Public Domain (CC0) or Creative Commons (CC-BY / CC-BY-SA). Application automatically copies author attribution and license URL into video descriptions.
- **Expected Cost:** ₹0 / month.

---

## 4. Procedural & Local Asset Generation (Zero-API Dependencies)

### A. Matplotlib & Seaborn Financial Chart Engine
- **What it does:** Generates custom 1920x1080 high-contrast financial charts (stock price histories, revenue waterfalls, market share comparisons, unit economic breakdowns).
- **Dependencies:** 100% local Python code.
- **Commercial Use:** Fully open source (BSD-compatible license). All generated output belongs exclusively to the user.
- **Expected Cost:** ₹0 / month.

### B. PIL / Pillow Motion Graphic & Title Card Engine
- **What it does:** Builds 1080p scene title cards, lower-third graphic overlays, quotation cards, and YouTube thumbnails.
- **Dependencies:** 100% local Python code.
- **Commercial Use:** Standard open-source license.
- **Expected Cost:** ₹0 / month.

---

## 5. Summary Matrix & Cost Audit

| Service | Category | Auth Type | Monthly Free Limit | Monthly Cost | Required for Local Testing? |
|---|---|---|---|---|---|
| Edge-TTS | Audio | None | Unlimited fair use | ₹0 | No (Included) |
| pyttsx3 | Audio | None | Unlimited offline | ₹0 | No (Included) |
| FFmpeg 9.0 | Media Engine | Local Binary | Unlimited | ₹0 | No (Installed) |
| Matplotlib | Visuals | Local Python | Unlimited | ₹0 | No (Included) |
| Pexels API | Visuals | Free Key | 20,000 req/mo | ₹0 | Optional |
| YouTube Data API | Publishing | OAuth 2.0 | 10,000 units/day | ₹0 | Optional (Manual package fallback) |
| YouTube Analytics API| Reporting | OAuth 2.0 | Standard free | ₹0 | Optional (CSV fallback) |
