"""Interactive YouTube OAuth Re-authentication Helper.
Saves the active authorization URL to data/auth_url.txt and launches the browser.
"""
import sys
import webbrowser
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow
from src.youtube.oauth import YOUTUBE_SCOPES
from config.settings import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE

class LoggingFlow(InstalledAppFlow):
    def authorization_url(self, **kwargs):
        url, state = super().authorization_url(**kwargs)
        auth_file = Path("data/auth_url.txt")
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        auth_file.write_text(url, encoding="utf-8")
        print(f"\nAUTH_URL_READY: {url}\n", flush=True)
        return url, state

def main():
    secrets_file = Path(YOUTUBE_CLIENT_SECRETS_FILE)
    token_file = Path(YOUTUBE_TOKEN_FILE)

    if not secrets_file.exists():
        print(f"ERROR: Client secrets file not found at: {secrets_file}", flush=True)
        sys.exit(1)

    print("Initiating YouTube OAuth authentication...", flush=True)
    flow = LoggingFlow.from_client_secrets_file(
        str(secrets_file), YOUTUBE_SCOPES
    )

    print("Launching browser and starting local authentication listener...", flush=True)
    creds = flow.run_local_server(port=0, prompt="consent")

    with open(token_file, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"\nAUTHENTICATION_SUCCESS: Valid credentials saved to {token_file}", flush=True)

if __name__ == "__main__":
    main()
