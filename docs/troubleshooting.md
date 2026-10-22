# Troubleshooting & Diagnostic Guide

This guide covers common operational edge cases, FFmpeg errors, TTS issues, and recovery procedures for **Faceless Media Studio**.

---

## 1. FFmpeg Issues

### Error: `FFmpeg executable not found`
- **Cause:** FFmpeg is not installed or not present in your system PATH.
- **Solution:**
  1. The studio automatically scans standard WinGet installation paths (`%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials*`).
  2. If missing, install Gyan FFmpeg:
     ```powershell
     winget install Gyan.FFmpeg.Essentials --accept-source-agreements --accept-package-agreements
     ```
  3. You can also specify the manual path in `.env`:
     ```
     FFMPEG_BINARY_PATH=C:\path\to\ffmpeg.exe
     ```

### Error: `Audio/Video Desynchronization or Blank Video`
- **Cause:** Mismatched framerates or corrupted intermediate clips.
- **Solution:**
  1. The studio uses direct `-pix_fmt yuv420p` and fixed 30fps CFR (Constant Frame Rate) to avoid variable framerate drift.
  2. The automated media validator runs `ffprobe` after every render to verify duration, non-zero audio streams, and valid video dimensions.
  3. If a clip fails, inspect `logs/ffmpeg_render.log` for the exact filtergraph trace.

---

## 2. Text-to-Speech (TTS) Issues

### Error: `Edge-TTS Connection Timeout / Network Error`
- **Cause:** Network firewall, DNS failure, or temporary ISP routing glitch to Microsoft Edge speech endpoint.
- **Solution:**
  1. The studio includes an automatic fallback mechanism: if Edge-TTS fails after 2 retries, it switches to **pyttsx3 (offline Windows SAPI5)**.
  2. In the dashboard (Page 7 or Page 14), toggle Voice Engine to **Local Offline (pyttsx3)** for 100% offline synthesis.

### Issue: `Mispronounced Names or Financial Acronyms`
- **Cause:** TTS reads "EBITDA" as letters or mispronounces foreign founder names.
- **Solution:**
  1. The studio has a built-in **Pronunciation Dictionary** (`data/pronunciation_rules.json`).
  2. Add regex or exact replacements (e.g. `{"EBITDA": "ee-bit-dah", "SEC": "S-E-C"}`).
  3. Pre-processing cleans the script automatically before feeding it to the TTS synthesizer.

---

## 3. YouTube API & OAuth Issues

### Error: `403 Quota Exceeded`
- **Cause:** Google Cloud YouTube Data API v3 daily quota limit reached (10,000 units).
- **Solution:**
  1. Daily quota resets at midnight Pacific Time (PT).
  2. The studio catches this error cleanly and offers the **"Manual Upload Package"** button. Download the ZIP file containing `video.mp4`, `thumbnail.jpg`, and `metadata.txt` and upload directly via [studio.youtube.com](https://studio.youtube.com) in 30 seconds.

### Error: `Invalid Grant / Token Expired`
- **Cause:** Refresh token revoked or expired during testing.
- **Solution:**
  1. Delete `config/token.json`.
  2. Return to **Page 14 (Settings)** and click **Re-authenticate YouTube Channel**.

---

## 4. Human Approval & Safety Invalidation

### Why did my video revert from `APPROVED` to `SCRIPT_REVIEW`?
- **Cause:** The system enforces strict content integrity. If any user edits the script text, changes a storyboard visual, or replaces the narration audio *after* approving the video, the cryptographic hash of the content changes.
- **Resolution:** This is an intentional security safeguard to prevent unreviewed modifications from reaching YouTube. Go to **Page 10 (Review & Approval)**, review the new version, and click **Approve Version** again.

---

## 5. Budget Protection Triggered

### Why is my API call blocked with `BudgetExceededError`?
- **Cause:** The monthly spending tracker detected that the planned action would exceed your configured ceiling (default: ₹0, ceiling: ₹3,000).
- **Resolution:**
  1. Check **Page 13 (Monetization & Costs)** to view the itemized spending ledger.
  2. If you intentionally want to permit a paid service (e.g., ElevenLabs or stock assets), update your monthly ceiling in Page 14 or `.env`.
