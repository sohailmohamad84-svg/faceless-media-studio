"""Packages the SR-71 Blackbird Short into a clean manual upload bundle:
- exports/sr71_manual_upload_bundle/sr71_blackbird_unstart_master_1080p.mp4
- exports/sr71_manual_upload_bundle/thumbnail.jpg
- exports/sr71_manual_upload_bundle/youtube_metadata.txt
"""
import shutil
from pathlib import Path

def main():
    bundle_dir = Path("exports/sr71_manual_upload_bundle")
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    vid_src = Path("exports/sr71_blackbird_unstart_master_1080p.mp4")
    thumb_src = Path("data/thumbnails/sr71_blackbird_unstart_thumb_main.jpg")
    
    shutil.copy2(vid_src, bundle_dir / "sr71_blackbird_unstart_master_1080p.mp4")
    shutil.copy2(thumb_src, bundle_dir / "thumbnail.jpg")
    
    metadata = """=== YOUTUBE SHORTS UPLOAD METADATA ===

TITLE:
The Jet That Choked at Mach 3.2: The SR-71 Unstart #shorts

DESCRIPTION:
At 2,200 MPH, the SR-71 Blackbird relied on moving spike cones to keep engines alive. What happens when supersonic air chokes a jet engine in fifty milliseconds?

✈️ Like & Subscribe for daily high-retention aviation & physics documentaries!

#shorts #sr71 #blackbird #aviation #planes #mach3 #engineering #supersonic #military

TAGS:
shorts, sr71, blackbird, aviation, planes, mach3, engineering, supersonic, military, documentary

CATEGORY:
Science & Technology / Education (Category ID: 27)

MADE FOR KIDS:
No (Not Made for Kids)

SYNTHETIC MEDIA DISCLOSURE:
Altered or synthetic content: Yes (Synthesized visual documentary reconstruction via Google DeepMind Veo)
"""
    (bundle_dir / "youtube_metadata.txt").write_text(metadata, encoding="utf-8")
    print(f"Manual upload bundle created at: {bundle_dir.resolve()}")

if __name__ == "__main__":
    main()
