"""Application configuration and environment settings for Faceless Media Studio."""
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = BASE_DIR / "projects"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for directory in [CONFIG_DIR, DATA_DIR, PROJECTS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Load environment variables
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# SQLite Database
DATABASE_PATH = DATA_DIR / "studio.db"

# Budget Protection Controls
MONTHLY_BUDGET_CEILING_INR = float(os.getenv("MONTHLY_BUDGET_CEILING_INR", "3000.0"))
DEFAULT_BUDGET_INR = float(os.getenv("DEFAULT_BUDGET_INR", "0.0"))

# Voice Engine Settings
DEFAULT_TTS_ENGINE = os.getenv("DEFAULT_TTS_ENGINE", "edge_tts")
DEFAULT_VOICE_ID = os.getenv("DEFAULT_VOICE_ID", "en-US-ChristopherNeural")

# Stock Media API Keys (Optional)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# YouTube Data API & OAuth Paths
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv(
    "YOUTUBE_CLIENT_SECRETS_FILE", str(CONFIG_DIR / "client_secrets.json")
)
YOUTUBE_TOKEN_FILE = os.getenv(
    "YOUTUBE_TOKEN_FILE", str(CONFIG_DIR / "token.json")
)
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "")

# AI Text Generation (Optional)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")


def get_ffmpeg_path() -> str:
    """Resolve the FFmpeg executable path dynamically.
    Checks environment override, system PATH, and standard WinGet install locations.
    """
    env_path = os.getenv("FFMPEG_BINARY_PATH")
    if env_path and Path(env_path).is_file():
        return env_path

    which_path = shutil.which("ffmpeg")
    if which_path:
        return which_path

    # Check local appdata winget package path on Windows
    local_appdata = os.getenv("LOCALAPPDATA", "")
    if local_appdata:
        winget_pattern = Path(local_appdata) / "Microsoft" / "WinGet" / "Packages"
        if winget_pattern.exists():
            for p in winget_pattern.glob("**/ffmpeg.exe"):
                if p.is_file():
                    return str(p)

    return "ffmpeg"


def get_ffprobe_path() -> str:
    """Resolve the ffprobe executable path dynamically."""
    ffmpeg = get_ffmpeg_path()
    if ffmpeg != "ffmpeg":
        probe = Path(ffmpeg).parent / "ffprobe.exe"
        if probe.is_file():
            return str(probe)
    which_probe = shutil.which("ffprobe")
    if which_probe:
        return which_probe
    return "ffprobe"
