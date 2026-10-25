"""Google OAuth 2.0 authentication manager for YouTube Data API v3."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from config.settings import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


class YouTubeAuthManager:
    @staticmethod
    def _restore_from_cloud_secrets():
        """Restore tokens from Streamlit secrets or environment if running in the cloud."""
        secrets_file = Path(YOUTUBE_CLIENT_SECRETS_FILE)
        token_file = Path(YOUTUBE_TOKEN_FILE)
        secrets_file.parent.mkdir(parents=True, exist_ok=True)

        # Check Streamlit secrets
        try:
            import streamlit as st
            if "YT_TOKEN_JSON" in st.secrets and not token_file.exists():
                token_file.write_text(st.secrets["YT_TOKEN_JSON"], encoding="utf-8")
            if "YT_CLIENT_SECRETS_JSON" in st.secrets and not secrets_file.exists():
                secrets_file.write_text(st.secrets["YT_CLIENT_SECRETS_JSON"], encoding="utf-8")
        except Exception:
            pass

        # Check Environment variables
        if os.getenv("YT_TOKEN_JSON") and not token_file.exists():
            token_file.write_text(os.getenv("YT_TOKEN_JSON"), encoding="utf-8")
        if os.getenv("YT_CLIENT_SECRETS_JSON") and not secrets_file.exists():
            secrets_file.write_text(os.getenv("YT_CLIENT_SECRETS_JSON"), encoding="utf-8")

    @staticmethod
    def get_auth_status() -> Dict[str, Any]:
        """Check if OAuth client secrets exist and if valid tokens are present."""
        YouTubeAuthManager._restore_from_cloud_secrets()
        secrets_file = Path(YOUTUBE_CLIENT_SECRETS_FILE)
        token_file = Path(YOUTUBE_TOKEN_FILE)

        has_secrets = secrets_file.exists() and secrets_file.stat().st_size > 20
        has_token = token_file.exists() and token_file.stat().st_size > 20

        is_authenticated = False

        if has_token and GOOGLE_AUTH_AVAILABLE:
            try:
                creds = Credentials.from_authorized_user_file(str(token_file), YOUTUBE_SCOPES)
                if creds and creds.valid:
                    is_authenticated = True
                elif creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(token_file, "w") as f:
                        f.write(creds.to_json())
                    is_authenticated = True
            except Exception:
                is_authenticated = False

        return {
            "has_secrets_file": has_secrets,
            "has_token_file": has_token,
            "is_authenticated": is_authenticated,
            "secrets_path": str(secrets_file),
            "token_path": str(token_file),
        }

    @staticmethod
    def get_credentials() -> Optional[Any]:
        """Return valid Google credentials or None."""
        if not GOOGLE_AUTH_AVAILABLE:
            return None

        status = YouTubeAuthManager.get_auth_status()
        if not status["is_authenticated"]:
            return None

        return Credentials.from_authorized_user_file(
            str(YOUTUBE_TOKEN_FILE), YOUTUBE_SCOPES
        )

    @staticmethod
    def authenticate_channel() -> Dict[str, Any]:
        """Launch interactive browser window to authorize YouTube channel access."""
        if not GOOGLE_AUTH_AVAILABLE:
            return {"success": False, "error": "Google OAuth libraries not available."}

        secrets_file = Path(YOUTUBE_CLIENT_SECRETS_FILE)
        token_file = Path(YOUTUBE_TOKEN_FILE)

        if not secrets_file.exists():
            return {"success": False, "error": f"Client secrets file not found: {secrets_file}"}

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(secrets_file), YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0, prompt="consent")
            with open(token_file, "w") as f:
                f.write(creds.to_json())
            return {"success": True, "token_path": str(token_file)}
        except Exception as e:
            return {"success": False, "error": str(e)}
