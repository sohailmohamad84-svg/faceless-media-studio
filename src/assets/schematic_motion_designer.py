"""Technical Motion Schematics Engine:
Generates broadcast-quality, 1:1 correlated animated engineering schematics:
1. Mountain Elevation Cross-Section (85-ft summit profile + ship elevation bracket)
2. Tidal Paradox Comparison (Pacific 20-ft surge vs Atlantic calm)
3. Gravity Hydraulic Elevator (underground culverts + rising chamber water + floating ship)
4. Reservoir Drought Diagnostic (lake water meter dropping to critical + 52M gallon flush)
5. Maritime Gridlock Radar & $4M Auction Terminal
"""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

w, h = 1920, 1080
fps = 30
work_dir = Path("scratch/schematic_work")
work_dir.mkdir(parents=True, exist_ok=True)
anim_assets = Path("data/assets/panama_anim")

# Load container ship prop
ship_prop_p = anim_assets / "prop_container_ship.png"
if ship_prop_p.exists():
    raw_ship = Image.open(ship_prop_p).convert("RGBA")
else:
    raw_ship = Image.new("RGBA", (400, 160), (30, 45, 70, 255))

def get_font(size, bold=True):
    try:
        f = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(f, size)
    except:
        return ImageFont.load_default()

def draw_tech_grid(draw, width=w, height=h):
    """Draw a dark engineering blueprint grid background."""
    draw.rectangle([(0, 0), (width, height)], fill=(11, 16, 26))
    # Grid lines every 80px
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(20, 30, 48), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(20, 30, 48), width=1)
    # Outer vignette border
    draw.rectangle([(0, 0), (width, height)], outline=(5, 8, 14), width=24)

# ==============================================================================
# SCENE 1: MOUNTAIN ELEVATION CROSS-SECTION
# ==============================================================================
def render_scene1_elevation_schematic(duration):
    out_mp4 = work_dir / "scene1_elevation_schematic.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ship_w = 260
    ship_h = int(raw_ship.height * (ship_w / raw_ship.width))
    scaled_ship = raw_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
    
    for f in range(total_frames):
        t = f / fps
        im = Image.new("RGB", (w, h), (11, 16, 26))
        draw = ImageDraw.Draw(im)
        draw_tech_grid(draw)
        
        # Header banner
        draw.rounded_rectangle([80, 50, 800, 115], radius=8, fill=(18, 26, 42), outline=(0, 200, 255), width=2)
        draw.text((105, 68), "PANAMA CANAL // TOPOGRAPHIC CROSS-SECTION", fill=(0, 220, 255), font=get_font(24, True))
        
        # Ground Mountain profile (Cutaway through the Continental Divide)
        mountain_points = [
            (80, 850), (280, 850), # Atlantic sea level
            (420, 750), (520, 750), # Step 1: Gatun (+28 ft)
            (620, 650), (720, 650), # Step 2 (+56 ft)
            (820, 550), (1380, 550), # Summit Lake Gatun (+85 ft)
            (1480, 650), (1560, 650), # Pedro Miguel
            (1640, 750), (1720, 750), # Miraflores
            (1840, 850), # Pacific sea level
            (1840, 960), (80, 960)
        ]
        draw.polygon(mountain_points, fill=(28, 38, 56), outline=(0, 200, 255), width=3)
        
        # Water bodies
        # Atlantic
        draw.rectangle([80, 850, 280, 960], fill=(0, 140, 220))
        draw.text((95, 870), "ATLANTIC (0 FT)", fill=(255, 255, 255), font=get_font(18, True))
        # Pacific
        draw.rectangle([1720, 850, 1840, 960], fill=(0, 140, 220))
        draw.text((1725, 870), "PACIFIC", fill=(255, 255, 255), font=get_font(18, True))
        
        # Summit Lake Gatun (+85 ft water)
        draw.rectangle([820, 550, 1380, 620], fill=(0, 180, 240))
        draw.text((980, 570), "LAKE GATUN SUMMIT WATER RESERVOIR (+85 FT)", fill=(10, 25, 45), font=get_font(18, True))
        
        # Place container ship on the summit water with realistic bobbing
        bob = int(math.sin(t * 3.0) * 3)
        ship_x, ship_y = 1000, 480 + bob
        im.paste(scaled_ship, (ship_x, ship_y), scaled_ship)
        
        # Animated elevation bracket climbing from 0 FT up to 85 FT
        progress = min(1.0, t / 3.0)
        current_ft = int(progress * 85)
        bracket_y = int(850 - progress * (850 - 550))
        
        # Elevation line
        draw.line([(760, 850), (760, bracket_y)], fill=(255, 200, 40), width=4)
        draw.line([(740, 850), (780, 850)], fill=(255, 200, 40), width=4)
        draw.line([(740, bracket_y), (780, bracket_y)], fill=(255, 200, 40), width=4)
        
        # Pulsing elevation indicator card
        card_box = [420, bracket_y - 45, 730, bracket_y + 35]
        draw.rounded_rectangle(card_box, radius=8, fill=(35, 25, 10), outline=(255, 200, 40), width=3)
        draw.text((440, bracket_y - 30), f"ELEVATION: +{current_ft} FEET", fill=(255, 215, 0), font=get_font(28, True))
        draw.text((440, bracket_y + 5), "ABOVE SEA LEVEL", fill=(220, 200, 160), font=get_font(18, False))
        
        # Big Warning Banner in Upper Right
        warn_box = [1120, 150, 1840, 280]
        pulse = (math.sin(t * 5.0) + 1) / 2
        border_col = (int(255 * pulse), 40, 40)
        draw.rounded_rectangle(warn_box, radius=12, fill=(28, 16, 18), outline=border_col, width=3)
        draw.text((1150, 175), "CRITICAL ENGINEERING PARADOX:", fill=(255, 80, 80), font=get_font(22, True))
        draw.text((1150, 215), "80,000-TON SHIP TRAPPED ON A MOUNTAIN", fill=(255, 255, 255), font=get_font(26, True))
        
        proc.stdin.write(im.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Scene 1 Schematic:", out_mp4)
    return out_mp4

# ==============================================================================
# SCENE 2: TIDAL WAVE PARADOX (PACIFIC VS ATLANTIC)
# ==============================================================================
def render_scene2_tidal_schematic(duration):
    out_mp4 = work_dir / "scene2_tidal_schematic.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for f in range(total_frames):
        t = f / fps
        im = Image.new("RGB", (w, h), (11, 16, 26))
        draw = ImageDraw.Draw(im)
        draw_tech_grid(draw)
        
        # Header banner
        draw.rounded_rectangle([80, 50, 950, 115], radius=8, fill=(18, 26, 42), outline=(255, 80, 80), width=2)
        draw.text((105, 68), "THE TIDAL DISASTER // WHY A SEA-LEVEL CANAL IS FATAL", fill=(255, 100, 100), font=get_font(24, True))
        
        # Split comparison boxes: Atlantic (Left) vs Pacific (Right)
        # Left: Atlantic
        draw.rounded_rectangle([100, 160, 920, 940], radius=16, fill=(14, 22, 35), outline=(0, 200, 255), width=3)
        draw.text((140, 200), "ATLANTIC OCEAN (CARIBBEAN)", fill=(0, 220, 255), font=get_font(30, True))
        draw.text((140, 245), "STABLE TIDAL ENVIRONMENT", fill=(160, 200, 240), font=get_font(20, False))
        
        # Atlantic Gauge (Gentle 2-ft tide)
        draw.rectangle([140, 320, 880, 780], fill=(18, 28, 45), outline=(40, 60, 90), width=2)
        atl_wave = math.sin(t * 1.5) * 12 # Very small 2-ft ripple
        draw.rectangle([140, int(540 + atl_wave), 880, 780], fill=(0, 130, 200))
        draw.text((160, 340), "TIDAL VARIATION: ONLY 2 FEET", fill=(255, 255, 255), font=get_font(26, True))
        draw.text((160, 390), "Water level remains calm & predictable\nNo dangerous tidal currents generated", fill=(180, 210, 240), font=get_font(20, False))
        
        # Right: Pacific
        draw.rounded_rectangle([1000, 160, 1820, 940], radius=16, fill=(28, 16, 20), outline=(255, 60, 60), width=3)
        draw.text((1040, 200), "PACIFIC OCEAN (GULF OF PANAMA)", fill=(255, 80, 80), font=get_font(30, True))
        draw.text((1040, 245), "VIOLENT TIDAL SURGE ZONE", fill=(240, 180, 180), font=get_font(20, False))
        
        # Pacific Gauge (Violent 20-ft tide!)
        draw.rectangle([1040, 320, 1780, 780], fill=(35, 18, 22), outline=(90, 40, 40), width=2)
        pac_wave = math.sin(t * 3.5) * 110 # Giant 20-ft surge!
        draw.rectangle([1040, int(550 + pac_wave), 1780, 780], fill=(220, 50, 50))
        draw.text((1060, 340), "EXTREME TIDE: 20 FEET (6 METERS)!", fill=(255, 255, 80), font=get_font(28, True))
        draw.text((1060, 390), "Lethal 20-foot tidal wave wall\nWould cause catastrophic inland flooding", fill=(255, 200, 200), font=get_font(20, False))
        
        # Flashing Warning Bar at Bottom
        draw.rounded_rectangle([140, 820, 1780, 910], radius=10, fill=(40, 15, 15), outline=(255, 50, 50), width=3)
        draw.text((220, 845), "A FLAT DITCH WOULD CREATE A DESTRUCTIVE 20-FT TSUNAMI RIVER THROUGH CENTRAL AMERICA", fill=(255, 220, 50), font=get_font(24, True))
        
        proc.stdin.write(im.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Scene 2 Schematic:", out_mp4)
    return out_mp4

# ==============================================================================
# SCENE 3: HYDRAULIC ELEVATOR & GRAVITY INFLOW
# ==============================================================================
def render_scene3_hydraulic_schematic(duration):
    out_mp4 = work_dir / "scene3_hydraulic_schematic.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ship_w = 420
    ship_h = int(raw_ship.height * (ship_w / raw_ship.width))
    scaled_ship = raw_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
    
    for f in range(total_frames):
        t = f / fps
        im = Image.new("RGB", (w, h), (11, 16, 26))
        draw = ImageDraw.Draw(im)
        draw_tech_grid(draw)
        
        # Header banner
        draw.rounded_rectangle([80, 50, 900, 115], radius=8, fill=(18, 26, 42), outline=(0, 200, 255), width=2)
        draw.text((105, 68), "GRAVITY HYDRAULIC ELEVATOR // ZERO ELECTRIC PUMPS", fill=(0, 220, 255), font=get_font(24, True))
        
        # Massive Concrete Lock Chamber Cutaway
        chamber_left = 500
        chamber_right = 1450
        floor_y = 860
        wall_top_y = 350
        
        # Concrete walls
        draw.rectangle([chamber_left - 120, wall_top_y, chamber_left, floor_y + 80], fill=(55, 65, 80), outline=(0, 180, 255), width=3)
        draw.rectangle([chamber_right, wall_top_y, chamber_right + 120, floor_y + 80], fill=(55, 65, 80), outline=(0, 180, 255), width=3)
        draw.rectangle([chamber_left - 120, floor_y, chamber_right + 120, floor_y + 80], fill=(55, 65, 80), outline=(0, 180, 255), width=3)
        
        # Water level rises smoothly in real-time from bottom (820) to top (520) = 300px climb!
        rise_progress = min(1.0, t / (duration * 0.75))
        water_y = int(820 - rise_progress * 280)
        
        # Churning Lock Water
        draw.rectangle([chamber_left, water_y, chamber_right, floor_y], fill=(0, 160, 235))
        
        # Container ship floating and rising on top of water!
        ship_y = water_y - ship_h + 35
        im.paste(scaled_ship, (chamber_left + 180, ship_y), scaled_ship)
        
        # Underground culverts / gravity pipes under the floor
        draw.rectangle([chamber_left - 180, floor_y + 20, chamber_right + 180, floor_y + 60], fill=(20, 30, 45), outline=(0, 220, 255), width=2)
        
        # Animated water arrows flowing into culverts
        for px in range(chamber_left, chamber_right, 140):
            arrow_phase = (t * 4.0 + px * 0.05) % 1.0
            ay = int(floor_y + 20 - arrow_phase * 40)
            draw.polygon([(px, ay), (px - 12, ay + 18), (px + 12, ay + 18)], fill=(0, 240, 255))
            
        # Left Info Panel: Natural Gravity Principle
        draw.rounded_rectangle([80, 160, 450, 480], radius=12, fill=(15, 22, 35), outline=(0, 200, 255), width=2)
        draw.text((105, 185), "NATURAL HYDRODYNAMICS", fill=(0, 220, 255), font=get_font(20, True))
        draw.text((105, 230), "• Water flows downhill from\n  Lake Gatun summit (85 ft)\n• Pure hydrostatic pressure\n• ZERO water pumps used\n• 100% gravity powered", fill=(210, 230, 250), font=get_font(18, False))
        
        # Right Info Panel: Live Telemetry
        gallons = int(rise_progress * 26000000)
        feet_lift = int(rise_progress * 28)
        draw.rounded_rectangle([1500, 160, 1860, 480], radius=12, fill=(15, 22, 35), outline=(255, 200, 40), width=2)
        draw.text((1525, 185), "REAL-TIME TELEMETRY", fill=(255, 200, 40), font=get_font(20, True))
        draw.text((1525, 235), "WATER INFLOW:", fill=(160, 180, 200), font=get_font(16, True))
        draw.text((1525, 260), f"{gallons:,} GAL", fill=(0, 240, 255), font=get_font(24, True))
        draw.text((1525, 320), "VERTICAL LIFT:", fill=(160, 180, 200), font=get_font(16, True))
        draw.text((1525, 345), f"+{feet_lift} FEET", fill=(255, 215, 0), font=get_font(34, True))
        draw.text((1525, 410), "CHAMBER STATUS: SEALED", fill=(100, 240, 120), font=get_font(16, True))
        
        proc.stdin.write(im.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Scene 3 Schematic:", out_mp4)
    return out_mp4

# ==============================================================================
# SCENE 4: 2023 DROUGHT & WATER DRAINAGE CRISIS
# ==============================================================================
def render_scene4_drought_schematic(duration):
    out_mp4 = work_dir / "scene4_drought_schematic.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for f in range(total_frames):
        t = f / fps
        im = Image.new("RGB", (w, h), (11, 16, 26))
        draw = ImageDraw.Draw(im)
        draw_tech_grid(draw)
        
        # Header banner
        draw.rounded_rectangle([80, 50, 950, 115], radius=8, fill=(35, 18, 20), outline=(255, 60, 60), width=2)
        draw.text((105, 68), "2023 CLIMATE CRISIS // THE DRINKING WATER DILEMMA", fill=(255, 80, 80), font=get_font(24, True))
        
        # Drainage Formula Card (Center Left)
        draw.rounded_rectangle([100, 160, 920, 520], radius=16, fill=(24, 16, 20), outline=(255, 120, 60), width=3)
        draw.text((140, 200), "THE FRESHWATER DRAINAGE TRAP:", fill=(255, 140, 60), font=get_font(26, True))
        draw.text((140, 255), "Every single ship crossing flushes:\n", fill=(220, 220, 220), font=get_font(20, False))
        draw.text((140, 290), "52,000,000 GALLONS", fill=(255, 60, 60), font=get_font(42, True))
        draw.text((140, 360), "of pure mountain freshwater straight into the ocean,\nlost forever. The canal drinks the same water that\nsupplies 50% of Panama's human population.", fill=(200, 200, 210), font=get_font(20, False))
        
        # Reservoir Level Meter (Right Half)
        draw.rounded_rectangle([1000, 160, 1820, 880], radius=16, fill=(15, 20, 30), outline=(0, 200, 255), width=2)
        draw.text((1050, 200), "LAKE GATUN WATER LEVEL DEPLETION", fill=(0, 220, 255), font=get_font(28, True))
        
        # Gauge Bar
        # Normal is 89.0 ft, drops to 79.0 ft
        drop_progress = min(1.0, t / (duration * 0.75))
        current_level = 89.0 - drop_progress * 10.0
        
        gauge_top = 280
        gauge_bot = 760
        gauge_h = gauge_bot - gauge_top
        
        # Fill bar
        bar_fill_y = int(gauge_top + drop_progress * gauge_h * 0.7)
        draw.rectangle([1100, gauge_top, 1220, gauge_bot], fill=(20, 30, 45), outline=(50, 70, 100), width=3)
        # Gradient alert fill
        fill_color = (0, 180, 240) if current_level > 84 else (255, 60, 60)
        draw.rectangle([1100, bar_fill_y, 1220, gauge_bot], fill=fill_color)
        
        # Level Indicators
        draw.line([(1080, gauge_top), (1240, gauge_top)], fill=(0, 240, 100), width=3)
        draw.text((1260, gauge_top - 12), "89.0 FT — NORMAL FULL CAPACITY", fill=(0, 240, 100), font=get_font(20, True))
        
        draw.line([(1080, gauge_top + int(gauge_h * 0.7)), (1240, gauge_top + int(gauge_h * 0.7))], fill=(255, 60, 60), width=3)
        draw.text((1260, gauge_top + int(gauge_h * 0.7) - 12), "79.0 FT — CRITICAL SHUTDOWN THRESHOLD", fill=(255, 60, 60), font=get_font(20, True))
        
        # Live Digital Readout Card
        readout_box = [1260, 480, 1760, 640]
        draw.rounded_rectangle(readout_box, radius=12, fill=(35, 15, 18), outline=(255, 60, 60), width=3)
        draw.text((1290, 510), "CURRENT RESERVOIR LEVEL:", fill=(255, 200, 200), font=get_font(18, True))
        draw.text((1290, 545), f"{current_level:.1f} FEET", fill=(255, 60, 60), font=get_font(48, True))
        
        # Lower Crisis summary
        draw.rounded_rectangle([100, 560, 920, 880], radius=16, fill=(22, 28, 38), outline=(255, 200, 40), width=2)
        draw.text((140, 595), "2023 OPERATIONAL RESTRICTIONS:", fill=(255, 200, 40), font=get_font(22, True))
        draw.text((140, 645), "• Daily vessel transits slashed from 38 to 22\n• Cargo weight limits cut by 40%\n• Over 160 ships trapped waiting in ocean\n• Global supply chain shipping bottleneck", fill=(220, 230, 245), font=get_font(20, False))
        
        proc.stdin.write(im.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Scene 4 Schematic:", out_mp4)
    return out_mp4

# ==============================================================================
# SCENE 5: MARITIME RADAR GRIDLOCK & $4M AUCTION DOCKET
# ==============================================================================
def render_scene5_auction_schematic(duration):
    out_mp4 = work_dir / "scene5_auction_schematic.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Generate 160 ship coordinates for radar map
    np.random.seed(42)
    radar_cx, radar_cy = 500, 550
    radar_r = 340
    ship_coords = []
    for _ in range(160):
        ang = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(30, radar_r - 20)
        sx = int(radar_cx + dist * np.cos(ang))
        sy = int(radar_cy + dist * np.sin(ang))
        ship_coords.append((sx, sy))
        
    for f in range(total_frames):
        t = f / fps
        im = Image.new("RGB", (w, h), (11, 16, 26))
        draw = ImageDraw.Draw(im)
        draw_tech_grid(draw)
        
        # Header banner
        draw.rounded_rectangle([80, 50, 950, 115], radius=8, fill=(18, 26, 42), outline=(255, 215, 0), width=2)
        draw.text((105, 68), "PACIFIC MARITIME GRIDLOCK // THE $4M LINE-SKIP AUCTION", fill=(255, 215, 0), font=get_font(24, True))
        
        # Left Half: Pacific Radar Screen
        draw.ellipse([radar_cx - radar_r, radar_cy - radar_r, radar_cx + radar_r, radar_cy + radar_r], fill=(10, 22, 28), outline=(0, 220, 255), width=3)
        draw.ellipse([radar_cx - int(radar_r*0.66), radar_cy - int(radar_r*0.66), radar_cx + int(radar_r*0.66), radar_cy + int(radar_r*0.66)], outline=(0, 100, 140), width=1)
        draw.ellipse([radar_cx - int(radar_r*0.33), radar_cy - int(radar_r*0.33), radar_cx + int(radar_r*0.33), radar_cy + int(radar_r*0.33)], outline=(0, 100, 140), width=1)
        draw.line([(radar_cx - radar_r, radar_cy), (radar_cx + radar_r, radar_cy)], fill=(0, 100, 140), width=1)
        draw.line([(radar_cx, radar_cy - radar_r), (radar_cx, radar_cy + radar_r)], fill=(0, 100, 140), width=1)
        
        # Rotating Radar Sweep line
        sweep_angle = t * 2.5
        sw_x = int(radar_cx + radar_r * math.cos(sweep_angle))
        sw_y = int(radar_cy + radar_r * math.sin(sweep_angle))
        draw.line([(radar_cx, radar_cy), (sw_x, sw_y)], fill=(0, 255, 200), width=3)
        
        # Draw 160 blips
        for sx, sy in ship_coords:
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 80, 80))
            
        draw.rounded_rectangle([radar_cx - 160, radar_cy + radar_r + 20, radar_cx + 160, radar_cy + radar_r + 75], radius=8, fill=(28, 15, 15), outline=(255, 80, 80), width=2)
        draw.text((radar_cx - 135, radar_cy + radar_r + 35), "163 SHIPS STRANDED AT SEA", fill=(255, 80, 80), font=get_font(18, True))
        
        # Right Half: Wall Street / Maritime Auction Docket Card
        docket_box = [1000, 160, 1840, 940]
        draw.rounded_rectangle(docket_box, radius=16, fill=(245, 242, 235), outline=(215, 180, 50), width=4)
        d_draw = ImageDraw.Draw(im)
        
        # Docket Header
        d_draw.rectangle([1000, 160, 1840, 260], fill=(22, 28, 40))
        d_draw.text((1050, 185), "PANAMA CANAL TRANSIT AUCTION", fill=(255, 215, 0), font=get_font(28, True))
        d_draw.text((1050, 225), "EMERGENCY LINE-SKIPPING SLOT ALLOCATION", fill=(180, 200, 225), font=get_font(18, False))
        
        # Auction Bidding Ticker
        d_draw.text((1050, 300), "BASE STARTING BID: $500,000", fill=(70, 75, 85), font=get_font(20, True))
        
        # Ticker climbs from $500k to $4,000,000
        bid_prog = min(1.0, t / (duration * 0.6))
        current_bid = int(500000 + bid_prog * 3500000)
        
        bid_box = [1050, 350, 1790, 480]
        d_draw.rounded_rectangle(bid_box, radius=12, fill=(230, 245, 230), outline=(40, 160, 60), width=3)
        d_draw.text((1080, 375), "RECORD WINNING BID:", fill=(40, 120, 50), font=get_font(22, True))
        d_draw.text((1080, 410), f"${current_bid:,}", fill=(20, 140, 40), font=get_font(52, True))
        
        # Docket Details
        d_draw.text((1050, 520), "WINNING ENTITY: PRIVATE PETROCHEMICAL CARRIER", fill=(40, 45, 55), font=get_font(20, True))
        d_draw.text((1050, 565), "NORMAL TOLL FEE: $400,000", fill=(70, 75, 85), font=get_font(20, False))
        d_draw.text((1050, 605), "LINE-SKIP SURCHARGE: +$4,000,000 (10X PREMIUM)", fill=(180, 30, 30), font=get_font(22, True))
        d_draw.text((1050, 650), "DAYS SAVED: 21 DAYS WAITING TIME AT SEA", fill=(30, 90, 160), font=get_font(20, True))
        
        # Slam Red Stamp if bid reached $4M
        if bid_prog >= 0.95:
            stamp_box = [1180, 720, 1660, 810]
            d_draw.rounded_rectangle(stamp_box, radius=10, outline=(200, 30, 30), width=5)
            d_draw.text((1220, 740), "AUCTION CLOSED: SOLD", fill=(200, 30, 30), font=get_font(34, True))
            
        proc.stdin.write(im.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Scene 5 Schematic:", out_mp4)
    return out_mp4
