"""Render repaired 60fps vertical clips for SR-71 Blackbird Unstart.
Renders 8 scenes at exactly 11.50s each (Total: 92.00s) with continuous dynamic Ken Burns motion,
Lanczos scaling to 1080x1920, and broadcast standard yuv420p pixel format.
"""
import subprocess
from pathlib import Path

def main():
    assets_dir = Path("data/assets/sr71")
    flow_dir = Path("data/flow_clips")
    flow_dir.mkdir(parents=True, exist_ok=True)
    
    scene_dur = 11.50  # 8 * 11.50 = 92.00 seconds
    fps = 60
    total_frames = int(scene_dur * fps)  # 690 frames
    
    for i in range(1, 9):
        img_path = assets_dir / f"sr71_scene_{i}.jpg"
        out_mp4 = flow_dir / f"sr71_scene_{i}.mp4"
        
        if not img_path.exists():
            raise FileNotFoundError(f"Missing asset: {img_path}")
            
        print(f"Rendering repaired Scene {i} clip ({scene_dur}s, 60fps)...")
        
        # Continuous smooth Ken Burns motion across all 690 frames without capping early
        rate = 0.10 / float(total_frames)  # ~0.000145 per frame
        if i % 2 == 1:
            zoom_expr = f"zoompan=z='min(zoom+{rate:.6f},1.10)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={total_frames}:s=1080x1920:fps={fps}"
        else:
            zoom_expr = f"zoompan=z='if(lte(zoom,1.0),1.10,max(1.0,zoom-{rate:.6f}))':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={total_frames}:s=1080x1920:fps={fps}"
            
        cmd = [
            "ffmpeg", "-y", "-threads", "2",
            "-loop", "1",
            "-i", str(img_path),
            "-t", f"{scene_dur:.2f}",
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,{zoom_expr},format=yuv420p",
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "fast",
            "-b:v", "8400k", "-minrate", "8100k", "-maxrate", "8800k", "-bufsize", "8800k",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out_mp4)
        ]
        subprocess.run(cmd, check=True)
        print(f"  Scene {i} rendered successfully: {out_mp4.stat().st_size:,} bytes")
        
    print("\nAll 8 scenes rendered successfully to data/flow_clips at 60 FPS, 11.50s each!")

if __name__ == "__main__":
    main()
