"""Render Hollywood-grade cinematic 60fps vertical clips for SR-71 Blackbird Unstart.
Features:
- Act 1: Stratosphere tracking push-in with aerodynamic float
- Act 2: Moveable spike technical macro push-in
- Act 3: Forensic shockwave unstart with VIOLENT CAMERA SHAKE / BUFFER at t=2.5s (frame 150)
- Act 4: Cockpit yaw jerk with SHARP VIOLENT LATERAL SLAM / WOBBLE at t=1.0s (frame 60)
- Act 5: J58 turbo-ramjet bypass duct scan
- Act 6: Corrugated titanium thermal expansion macro glide
- Act 7: Aggressive supersonic missile evasion climb
- Act 8: Museum golden spotlight crane pull-back
- Filmic vignette + unsharp detail enhancement + broadcast yuv420p
"""
import subprocess
from pathlib import Path

def main():
    assets_dir = Path("data/assets/sr71")
    flow_dir = Path("data/flow_clips")
    flow_dir.mkdir(parents=True, exist_ok=True)
    
    scene_dur = 11.50
    fps = 60
    total_frames = int(scene_dur * fps)  # 690 frames
    
    # Filmic post-processing filter chain (soft vignette, crisp 4K unsharp mask, film contrast)
    film_grade = "vignette=PI/4.5:eval=init,unsharp=5:5:0.7:5:5:0.0,eq=contrast=1.08:brightness=-0.01:saturation=1.10"
    
    for i in range(1, 9):
        img_path = assets_dir / f"sr71_scene_{i}.jpg"
        out_mp4 = flow_dir / f"sr71_scene_{i}.mp4"
        
        if not img_path.exists():
            raise FileNotFoundError(f"Missing asset: {img_path}")
            
        print(f"Rendering cinematic Scene {i} clip ({scene_dur}s, 60fps)...")
        
        rate = 0.12 / float(total_frames)
        
        if i == 1:
            # Act 1: Stratosphere Tracking Push-in with subtle high-altitude atmospheric float
            zoom_expr = f"zoompan=z='min(zoom+{rate:.6f},1.12)':x='(iw-iw/zoom)/2 + 8*sin(on*0.03)':y='(ih-ih/zoom)/2 + 6*cos(on*0.025)':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 2:
            # Act 2: Technical CAD Push-in towards inlet cone
            zoom_expr = f"zoompan=z='min(zoom+{rate*1.2:.6f},1.14)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 3:
            # Act 3: Forensic Shockwave Unstart - Starts steady, then VIOLENT SHOCKWAVE CAMERA BUFFET at t=2.5s (frame 150)
            # Shake amplitude: 35px high-frequency jitter decaying over 120 frames (~2.0s)
            shake_x = "if(between(on,150,300), 32*sin(on*1.9)*exp(-(on-150)/45), 0)"
            shake_y = "if(between(on,150,300), 24*cos(on*2.4)*exp(-(on-150)/45), 0)"
            zoom_expr = f"zoompan=z='min(zoom+{rate*1.1:.6f},1.14)':x='(iw-iw/zoom)/2 + {shake_x}':y='(ih-ih/zoom)/2 + {shake_y}':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 4:
            # Act 4: Cockpit Violent Yaw Jerk - At t=1.0s (frame 60): SHARP LATERAL SLAM & REBOUND
            # Lateral impulse: 45px slam to the left with damped elastic rebound
            slam_x = "if(between(on,60,240), -45*sin((on-60)*0.18)*exp(-(on-60)/40), 0)"
            slam_y = "if(between(on,60,240), 18*cos((on-60)*0.22)*exp(-(on-60)/40), 0)"
            zoom_expr = f"zoompan=z='if(lte(zoom,1.0),1.12,max(1.0,zoom-{rate*0.8:.6f}))':x='(iw-iw/zoom)/2 + {slam_x}':y='(ih-ih/zoom)/2 + {slam_y}':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 5:
            # Act 5: J58 Turbo-Ramjet Bypass Duct Pan
            zoom_expr = f"zoompan=z='min(zoom+{rate:.6f},1.12)':x='(iw-iw/zoom)/2 + 25*(on/{total_frames})':y='(ih-ih/zoom)/2':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 6:
            # Act 6: Titanium Skin Macro Glide with subtle thermal drift
            zoom_expr = f"zoompan=z='min(zoom+{rate:.6f},1.12)':x='(iw-iw/zoom)/2 - 20*(on/{total_frames})':y='(ih-ih/zoom)/2 + 5*sin(on*0.04)':d={total_frames}:s=1080x1920:fps={fps}"
            
        elif i == 7:
            # Act 7: Aggressive Mach 3.2 Supersonic Missile Evasion Climb
            zoom_expr = f"zoompan=z='min(zoom+{rate*1.4:.6f},1.16)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2 + 30*(1 - on/{total_frames})':d={total_frames}:s=1080x1920:fps={fps}"
            
        else:
            # Act 8: Museum Golden Spotlight Crane Pull-out
            zoom_expr = f"zoompan=z='if(lte(zoom,1.0),1.14,max(1.0,zoom-{rate*1.1:.6f}))':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d={total_frames}:s=1080x1920:fps={fps}"

        cmd = [
            "ffmpeg", "-y", "-threads", "2",
            "-loop", "1",
            "-i", str(img_path),
            "-t", f"{scene_dur:.2f}",
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,{zoom_expr},{film_grade},format=yuv420p",
            "-r", str(fps),
            "-c:v", "libx264",
            "-preset", "fast",
            "-b:v", "8500k", "-minrate", "8200k", "-maxrate", "9000k", "-bufsize", "9000k",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out_mp4)
        ]
        subprocess.run(cmd, check=True)
        print(f"  Scene {i} rendered: {out_mp4.stat().st_size:,} bytes")
        
    print("\nAll 8 scenes rendered with Hollywood camera dynamics to data/flow_clips!")

if __name__ == "__main__":
    main()
