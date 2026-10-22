"""License tracking and stock asset retrieval manager."""
import os
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import PEXELS_API_KEY, PIXABAY_API_KEY
from src.database.models import MediaAsset
from src.database.repository import AssetRepository


class LicenseTracker:
    @staticmethod
    def register_asset(
        name: str,
        asset_type: str,
        file_path: str,
        source_url: str = "",
        license_type: str = "procedural_matplotlib",
        commercial_allowed: bool = True,
        attribution_required: bool = False,
        attribution_text: str = "",
        resolution: str = "1920x1080",
    ) -> MediaAsset:
        """Register a visual or audio asset in the persistent database with full license provenance."""
        path = Path(file_path)
        file_size = path.stat().st_size if path.exists() else 0

        asset = MediaAsset(
            name=name,
            asset_type=asset_type,
            file_path=str(path.resolve()),
            source_url=source_url,
            license_type=license_type,
            commercial_allowed=commercial_allowed,
            attribution_required=attribution_required,
            attribution_text=attribution_text,
            resolution=resolution,
            file_size_bytes=file_size,
        )
        asset_id = AssetRepository.add_asset(asset)
        asset.id = asset_id
        return asset

    @staticmethod
    def fetch_pexels_broll(query: str, output_path: str, api_key: str = None) -> Optional[str]:
        """Fetch free stock video or photo from Pexels API if API key is provided."""
        key = api_key or PEXELS_API_KEY
        if not key:
            return None

        headers = {"Authorization": key}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=landscape"

        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                data = res.json()
                videos = data.get("videos", [])
                if videos:
                    files = videos[0].get("video_files", [])
                    # Pick 1080p if available
                    chosen = next((f for f in files if f.get("width") == 1920), files[0])
                    video_url = chosen.get("link")
                    if video_url:
                        dl = requests.get(video_url, stream=True, timeout=20)
                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            for chunk in dl.iter_content(chunk_size=8192):
                                f.write(chunk)
                        LicenseTracker.register_asset(
                            name=f"Pexels - {query}",
                            asset_type="b_roll",
                            file_path=output_path,
                            source_url=videos[0].get("url", ""),
                            license_type="pexels",
                            commercial_allowed=True,
                            attribution_required=False,
                            attribution_text=f"Video by {videos[0].get('user', {}).get('name', 'Pexels creator')} on Pexels",
                        )
                        return output_path
        except Exception:
            pass
        return None
