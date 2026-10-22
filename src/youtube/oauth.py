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
    def get_auth_status() -> Dict[str, Any]:
        """Check if OAuth client secrets exist and if valid tokens are present."""
        secrets_file = Path(YOUTUBE_CLIENT_SECRETS_FILE)
        token_file = Path(YOUTUBE_TOKEN_FILE)

        has_secrets = secrets_file.exists() and secrets_file.stat().st_size > 20
        has_token = token_file.exists() and token_file.stat().st_size > 20

        is_authenticated = False
        user_info = None

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
