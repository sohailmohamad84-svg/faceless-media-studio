# Setup Guide: Faceless Media Studio (Windows)

This guide walks you through setting up and running **Faceless Media Studio** locally on your Windows machine from scratch.

---

## 1. System Prerequisites

1. **Operating System:** Windows 10 or Windows 11 (64-bit).
2. **Python:** Python 3.11+ installed. Verify in PowerShell:
   ```powershell
   python --version
   ```
3. **FFmpeg:** Installed and available in PATH (or WinGet).
   - If not installed, run:
     ```powershell
     winget install Gyan.FFmpeg.Essentials --accept-source-agreements --accept-package-agreements
     ```
   - Verify FFmpeg:
     ```powershell
     ffmpeg -version
     ```
   *(Note: The studio automatically detects FFmpeg from system PATH or standard WinGet install locations).*

---

## 2. Quickstart Installation (5 Minutes)

### Step 1: Open PowerShell in the project directory
```powershell
cd c:\Users\Sohail\Antigravity\faceless-media-studio
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If PowerShell displays an ExecutionPolicy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
By default, the studio runs in **100% Free Mode**:
- `DEFAULT_TTS_ENGINE=edge_tts` (Free neural voiceover; no API key needed).
- Procedural charts (Matplotlib) require no external accounts.
- YouTube OAuth is optional until you choose to upload directly.

---

## 3. Running the Application

Launch the studio dashboard:
```powershell
.\.venv\Scripts\streamlit run app.py
```
Your default web browser will automatically open:
```
http://localhost:8501
```

---

## 4. Optional Integrations Setup

### A. YouTube Data API v3 & OAuth 2.0 (For 1-Click Publishing)
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named `Faceless Media Studio`.
3. Navigate to **APIs & Services > Library**, search for **YouTube Data API v3**, and click **Enable**.
4. Navigate to **APIs & Services > Credentials**:
   - Click **Create Credentials > OAuth client ID**.
   - Application Type: **Desktop app**.
   - Download the JSON credentials and save as `config/client_secrets.json`.
5. In the studio dashboard, navigate to **Page 14: Settings & Credentials**, click **Authenticate YouTube Channel**, and complete the one-time Google login in your browser.
6. The token is saved securely in `config/token.json` (ignored by Git).

### B. Free Stock Footage (Pexels / Pixabay)
1. Register for a free account at [Pexels Developers](https://www.pexels.com/api/).
2. Copy your free API key.
3. Paste it in `.env` under `PEXELS_API_KEY=` or enter it on **Page 14 (Settings)**.
4. (Optional) Repeat for [Pixabay API](https://pixabay.com/api/docs/).

---

## 5. Daily Production Workflow (1–2 Hours)

1. **Step 1: Discover & Select Topic (10 mins)**
   - Go to **Page 3 (Topic Discovery)**. Review the top-scored ideas (e.g. *"How Costco's \$1.50 Hot Dog Protects a \$250B Empire"*).
   - Click **Select for Production**.
2. **Step 2: Generate & Edit Script (20 mins)**
   - Go to **Page 4 (Script Editor)**. Review the generated hook, claims ledger, and storyboard scenes.
   - Edit or refine scenes to your liking. Run the **Editorial Quality Gate**.
3. **Step 3: Generate Voiceover & Assets (15 mins)**
   - Go to **Page 7 (Voiceover)**. Select a neural voice (`ChristopherNeural` or `GuyNeural`) and click **Generate Voiceover**.
   - Go to **Page 6 & 8 (Assets & Storyboard)**. Generate custom financial charts and select scene visuals.
4. **Step 4: Render Video (15 mins)**
   - Go to **Page 9 (Rendering Queue)**. Click **Render 1080p Video**. FFmpeg compiles audio, video, transitions, subtitles, and background music.
5. **Step 5: Review & Human Approval (15 mins)**
   - Go to **Page 10 (Review & Approval)**. Watch the complete preview, verify the claim ledger, and click **Approve Version 1.0**.
6. **Step 6: YouTube Upload / Export (5 mins)**
   - Go to **Page 11 (YouTube Publishing)**. Choose **Upload via API (Private/Unlisted)** or click **Download Manual Upload Package**.
