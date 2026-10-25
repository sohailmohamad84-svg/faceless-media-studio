"""Procedural 2D Vector Graphic Designer for Panama Canal Animated Documentary.
Generates razor-sharp, 1080p vector plates, technical cross-sections, maps, and props using Pillow & Matplotlib.
"""
import math
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

anim_dir = Path("data/assets/panama_anim")
anim_dir.mkdir(parents=True, exist_ok=True)

width, height = 1920, 1080

def get_font(size, bold=True):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except:
        return ImageFont.load_default()

def create_panama_map():
    """1. 2D Vector Map of the Americas with Panama Isthmus & Shipping Routes."""
    im = Image.new("RGBA", (width, height), (22, 45, 68, 255)) # Deep oceanic blue
    draw = ImageDraw.Draw(im)
    
    # Ocean depth contours
    for r in range(120, 1400, 180):
        draw.ellipse((-200, -200, r * 2, r * 1.5), outline=(28, 55, 82, 160), width=2)
        
    # Continental Landmasses (Warm vector terrain tones)
    # North/Central America (top-left coming down)
    na_pts = [
        (0, 0), (680, 0), (620, 180), (520, 320), (560, 420), 
        (680, 500), (840, 540), (960, 560), # Isthmus narrow neck
        (920, 580), (780, 560), (640, 520), (460, 460), (320, 380),
        (180, 260), (0, 200)
    ]
    draw.polygon(na_pts, fill=(215, 180, 120, 255), outline=(170, 135, 85, 255))
    
    # South America (bottom-right coming up)
    sa_pts = [
        (960, 560), (1080, 580), (1220, 640), (1400, 720), (1550, 860),
        (1500, 1080), (1100, 1080), (980, 920), (920, 780), (920, 620), (960, 560)
    ]
    draw.polygon(sa_pts, fill=(205, 170, 110, 255), outline=(160, 125, 75, 255))
    
    # Internal Jungle Topography (Lush green mountain ranges)
    draw.polygon([(480, 280), (540, 380), (640, 460), (780, 520), (900, 550),
                  (860, 570), (720, 540), (580, 480), (440, 360)], fill=(120, 160, 85, 220))
    draw.polygon([(980, 600), (1120, 660), (1240, 760), (1180, 840), (1040, 720), (960, 630)],
                 fill=(115, 155, 80, 220))
                 
    # Ocean Labels (Stylized typography)
    draw.text((180, 750), "PACIFIC OCEAN", font=get_font(42, True), fill=(75, 125, 165, 200))
    draw.text((1220, 220), "ATLANTIC OCEAN\n(CARIBBEAN SEA)", font=get_font(38, True), fill=(75, 125, 165, 200))
    
    # Isthmus Target Ring (Panama)
    cx, cy = 940, 560
    draw.ellipse((cx - 45, cy - 45, cx + 45, cy + 45), outline=(255, 215, 0, 255), width=4)
    draw.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(255, 215, 0, 255))
    
    # Label Banner
    draw.rounded_rectangle([cx - 160, cy - 95, cx + 160, cy - 50], radius=8, fill=(15, 25, 35, 230), outline=(255, 215, 0, 255), width=2)
    draw.text((cx - 142, cy - 88), "ISTHMUS OF PANAMA (50 MILES)", font=get_font(18, True), fill=(255, 255, 255, 255))
    
    out_path = anim_dir / "bg_panama_map.png"
    im.save(out_path)
    print("Generated bg_panama_map.png")
    return out_path

def create_locks_cutaway():
    """2. 2D Vector Infographic Cutaway of the 85-ft Mountain Water Elevator."""
    im = Image.new("RGBA", (width, height), (242, 236, 220, 255)) # Warm blueprint cream background
    draw = ImageDraw.Draw(im)
    
    # Sky / Clouds gradient
    for y in range(400):
        alpha = int(255 * (1 - y / 400.0) * 0.15)
        draw.line([(0, y), (width, y)], fill=(135, 206, 250, alpha))
        
    # Continental Divide Mountain Profile
    # Mountain peak in center at y=280
    mountain_pts = [
        (0, 820), (320, 820), # Atlantic sea level approach
        (380, 740), (480, 660), (580, 580), # Gatun 3-step stairs
        (660, 580), (960, 580), (1260, 580), # Lake Gatun summit plateau (85 ft)
        (1340, 660), (1440, 740), (1540, 820), # Pacific stairs descending
        (width, 820), (width, height), (0, height) # Foundation
    ]
    draw.polygon(mountain_pts, fill=(185, 150, 105, 255), outline=(135, 100, 65, 255), width=4)
    
    # Subterranean Earth / Rock hatching
    for x in range(0, width, 40):
        draw.line([(x, 820), (x + 80, height)], fill=(160, 125, 85, 80), width=2)
        
    # Water Bodies (Glowing cyan water levels)
    # Atlantic Ocean (Left, 0 ft)
    draw.rectangle([0, 820, 320, 960], fill=(0, 175, 240, 220))
    draw.text((60, 860), "ATLANTIC OCEAN\n(SEA LEVEL: 0 FT)", font=get_font(22, True), fill=(255, 255, 255, 240))
    
    # Gatun Locks (3 Chambers stepping up)
    draw.rectangle([320, 740, 420, 820], fill=(0, 195, 245, 220), outline=(50, 50, 60, 255), width=3)
    draw.rectangle([420, 660, 520, 740], fill=(0, 205, 250, 220), outline=(50, 50, 60, 255), width=3)
    draw.rectangle([520, 580, 620, 660], fill=(0, 215, 255, 220), outline=(50, 50, 60, 255), width=3)
    
    # Lake Gatun (Center Summit Water, 85 ft)
    draw.rectangle([620, 580, 1280, 780], fill=(0, 210, 255, 230), outline=(40, 140, 190, 255), width=3)
    draw.text((780, 630), "LAKE GATUN SUMMIT RESERVOIR\n(+85 FEET ELEVATION)", font=get_font(28, True), fill=(10, 45, 80, 255))
    
    # Pacific Locks (3 Chambers stepping down)
    draw.rectangle([1280, 580, 1380, 660], fill=(0, 215, 255, 220), outline=(50, 50, 60, 255), width=3)
    draw.rectangle([1380, 660, 1480, 740], fill=(0, 205, 250, 220), outline=(50, 50, 60, 255), width=3)
    draw.rectangle([1480, 740, 1580, 820], fill=(0, 195, 245, 220), outline=(50, 50, 60, 255), width=3)
    
    # Pacific Ocean (Right, 0 ft)
    draw.rectangle([1580, 820, width, 960], fill=(0, 175, 240, 220))
    draw.text((1640, 860), "PACIFIC OCEAN\n(SEA LEVEL: 0 FT)", font=get_font(22, True), fill=(255, 255, 255, 240))
    
    # Elevation Dimension Line (Double arrow showing 85 ft)
    draw.line([(700, 820), (700, 580)], fill=(220, 50, 50, 255), width=4)
    draw.line([(680, 820), (720, 820)], fill=(220, 50, 50, 255), width=4)
    draw.line([(680, 580), (720, 580)], fill=(220, 50, 50, 255), width=4)
    
    # 85 FT Badge
    draw.rounded_rectangle([715, 680, 840, 725], radius=6, fill=(220, 50, 50, 255))
    draw.text((728, 688), "+85 FEET", font=get_font(22, True), fill=(255, 255, 255, 255))
    
    # Header Infographic Title
    draw.rounded_rectangle([420, 40, 1500, 115], radius=12, fill=(25, 35, 50, 240), outline=(255, 215, 0, 255), width=3)
    draw.text((455, 55), "PANAMA CANAL: THE 85-FOOT WATER ELEVATOR", font=get_font(34, True), fill=(255, 215, 0, 255))
    
    out_path = anim_dir / "bg_mountain_locks_cutaway.png"
    im.save(out_path)
    print("Generated bg_mountain_locks_cutaway.png")
    return out_path

def create_container_ship_prop():
    """3. 2D Cartoon Container Ship Prop (Transparent RGBA PNG)."""
    sw, sh = 880, 360
    im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    hull_y = 220
    hull_bottom_y = 310
    
    # Red anti-fouling keel bottom
    keel_pts = [(90, hull_bottom_y), (140, hull_bottom_y + 35), (780, hull_bottom_y + 35), (840, hull_bottom_y)]
    draw.polygon(keel_pts, fill=(195, 45, 40, 255), outline=(130, 25, 20, 255), width=3)
    
    # Dark Navy Hull
    hull_pts = [
        (40, hull_y), (840, hull_y), # Main deck
        (810, hull_bottom_y), (90, hull_bottom_y) # Lower hull
    ]
    draw.polygon(hull_pts, fill=(30, 45, 65, 255), outline=(15, 25, 35, 255), width=4)
    # White waterline boot-topping stripe
    draw.line([(85, hull_bottom_y - 12), (815, hull_bottom_y - 12)], fill=(255, 255, 255, 240), width=5)
    
    # Colorful Stacked Shipping Containers
    colors = [
        (220, 60, 50, 255),   # Red Maersk
        (40, 120, 215, 255),  # Blue CMA CGM
        (245, 185, 30, 255),  # Yellow MSC
        (40, 165, 95, 255),   # Green Evergreen
        (235, 110, 35, 255),  # Orange Hapag-Lloyd
        (130, 75, 175, 255)   # Purple ONE
    ]
    
    box_w = 58
    box_h = 28
    np.random.seed(101)
    
    # 4 Tiers of container stacks across deck (x: 140 to 680)
    for tier in range(4):
        ty = hull_y - (tier + 1) * (box_h + 2)
        for col in range(9):
            cx = 140 + col * (box_w + 3)
            c_idx = (tier * 9 + col) % len(colors)
            col_rgb = colors[c_idx]
            draw.rectangle([cx, ty, cx + box_w, ty + box_h], fill=col_rgb, outline=(25, 25, 25, 255), width=2)
            # Corrugated metal container lines
            for lx in range(cx + 8, cx + box_w - 4, 10):
                draw.line([(lx, ty + 2), (lx, ty + box_h - 2)], fill=(0, 0, 0, 70), width=1)
                
    # Bridge Superstructure (Rear, x: 710 to 800)
    b_x, b_y = 710, 80
    b_w, b_h = 95, hull_y - b_y
    # White cabin tower
    draw.rectangle([b_x, b_y, b_x + b_w, hull_y], fill=(240, 245, 250, 255), outline=(30, 40, 50, 255), width=3)
    # Tinted bridge navigation windows
    for wy in range(b_y + 14, b_y + 55, 18):
        draw.rectangle([b_x + 10, wy, b_x + b_w - 10, wy + 10], fill=(45, 115, 165, 255))
    # Radar Mast & Smokestack
    draw.rectangle([b_x + 55, b_y - 28, b_x + 85, b_y], fill=(210, 40, 35, 255), outline=(20, 20, 20, 255), width=2) # Red stack
    draw.line([(b_x + 25, b_y), (b_x + 25, b_y - 45)], fill=(80, 80, 90, 255), width=3) # Antenna
    draw.line([(b_x + 10, b_y - 30), (b_x + 40, b_y - 30)], fill=(80, 80, 90, 255), width=2)
    
    out_path = anim_dir / "prop_container_ship.png"
    im.save(out_path)
    print("Generated prop_container_ship.png")
    return out_path

def create_lock_canyon_background():
    """4. 2D Vector Lock Chamber Interior (Concrete walls & water channel)."""
    im = Image.new("RGBA", (width, height), (175, 185, 195, 255)) # Foggy overcast sky
    draw = ImageDraw.Draw(im)
    
    # Distant Horizon (Jungle hills beyond the lock)
    draw.polygon([(480, 360), (960, 280), (1440, 360), (1440, 480), (480, 480)], fill=(95, 135, 75, 255))
    
    # Massive Concrete Lock Walls (Perspective receding into center)
    # Left Wall
    left_wall = [(0, 0), (520, 360), (520, 820), (0, height), (0, 0)]
    draw.polygon(left_wall, fill=(160, 165, 172, 255), outline=(100, 105, 112, 255), width=4)
    # Concrete horizontal seam lines
    for sy in range(120, height, 110):
        draw.line([(0, sy), (520, int(360 + (sy/height)*460))], fill=(130, 135, 140, 180), width=2)
        
    # Right Wall
    right_wall = [(width, 0), (1400, 360), (1400, 820), (width, height), (width, 0)]
    draw.polygon(right_wall, fill=(155, 160, 168, 255), outline=(95, 100, 108, 255), width=4)
    for sy in range(120, height, 110):
        draw.line([(width, sy), (1400, int(360 + (sy/height)*460))], fill=(130, 135, 140, 180), width=2)
        
    # Electric Mule Tracks on Lock Coping (Walkways with cog rails)
    # Left track
    draw.line([(0, 680), (520, 520)], fill=(60, 60, 70, 255), width=6)
    # Right track
    draw.line([(width, 680), (1400, 520)], fill=(60, 60, 70, 255), width=6)
    
    # Water Channel (Deep turquoise water filling chamber)
    water_pts = [(520, 520), (1400, 520), (width, height), (0, height)]
    draw.polygon(water_pts, fill=(0, 165, 215, 255))
    
    # Water ripples & foam
    for wy in range(540, height, 40):
        draw.line([(int(520 - (wy-520)*0.8), wy), (int(1400 + (wy-520)*0.8), wy)], fill=(120, 220, 255, 120), width=3)
        
    # Massive Steel Miter Gates in distance (Closed V-shape)
    # Left gate leaf
    draw.polygon([(520, 340), (960, 380), (960, 540), (520, 520)], fill=(65, 75, 88, 255), outline=(30, 35, 45, 255), width=3)
    # Right gate leaf
    draw.polygon([(1400, 340), (960, 380), (960, 540), (1400, 520)], fill=(60, 70, 82, 255), outline=(30, 35, 45, 255), width=3)
    
    out_path = anim_dir / "bg_lock_canyon.png"
    im.save(out_path)
    print("Generated bg_lock_canyon.png")
    return out_path

def create_jungle_storm_background():
    """5. 2D Vector Jungle Deluge & Swollen River Background."""
    im = Image.new("RGBA", (width, height), (35, 45, 55, 255)) # Dark stormy sky
    draw = ImageDraw.Draw(im)
    
    # Lightning bolt flash in sky
    draw.line([(680, 0), (640, 110), (670, 120), (620, 240)], fill=(255, 255, 220, 230), width=4)
    draw.line([(640, 110), (610, 160)], fill=(255, 255, 220, 160), width=2)
    
    # Layered Jungle Mountains in storm fog
    draw.polygon([(0, 280), (420, 200), (980, 260), (1450, 180), (width, 240), (width, height), (0, height)], fill=(45, 75, 55, 255))
    draw.polygon([(0, 380), (360, 310), (840, 350), (1320, 290), (width, 360), (width, height), (0, height)], fill=(35, 65, 45, 255))
    
    # Raging Swollen Chagres River (Muddy brown rushing torrent)
    river_pts = [(0, 680), (480, 640), (1050, 690), (width, 620), (width, height), (0, height)]
    draw.polygon(river_pts, fill=(145, 105, 55, 255))
    # Torrential wave crests
    for ry in range(660, height, 45):
        draw.line([(0, ry), (width, ry)], fill=(195, 155, 95, 160), width=4)
        
    out_path = anim_dir / "bg_jungle_rainstorm.png"
    im.save(out_path)
    print("Generated bg_jungle_rainstorm.png")
    return out_path

def create_drought_lake_background():
    """6. 2D Vector Drought Lake Gatun with Cracked Earth & Sinking Water."""
    im = Image.new("RGBA", (width, height), (225, 215, 185, 255)) # Scorching hazy yellow sky
    draw = ImageDraw.Draw(im)
    
    # Blazing Hazy Sun
    draw.ellipse((960 - 80, 140 - 80, 960 + 80, 140 + 80), fill=(255, 240, 140, 255))
    for r in range(100, 240, 35):
        draw.ellipse((960 - r, 140 - r, 960 + r, 140 + r), outline=(255, 210, 80, 80), width=3)
        
    # Dried Parched Mud Flats (Foreground & Midground)
    mud_pts = [(0, 480), (620, 420), (1280, 460), (width, 410), (width, height), (0, height)]
    draw.polygon(mud_pts, fill=(175, 140, 95, 255), outline=(135, 100, 65, 255), width=3)
    
    # Mud crack grid
    for x in range(0, width, 140):
        for y in range(480, height, 90):
            draw.line([(x, y), (x + 40, y + 30), (x + 20, y + 70)], fill=(110, 80, 50, 180), width=2)
            
    # Sunken dead tree stumps sticking out of parched ground
    stump_positions = [(320, 640), (680, 560), (1140, 610), (1520, 540)]
    for sx, sy in stump_positions:
        draw.polygon([(sx - 18, sy), (sx - 8, sy - 85), (sx + 8, sy - 85), (sx + 18, sy)], fill=(65, 45, 30, 255))
        draw.line([(sx - 8, sy - 85), (sx - 35, sy - 125)], fill=(65, 45, 30, 255), width=5)
        draw.line([(sx + 8, sy - 85), (sx + 30, sy - 120)], fill=(65, 45, 30, 255), width=5)
        
    # Shrunken shallow water puddle
    draw.ellipse((640, 720, 1280, 940), fill=(80, 145, 160, 220), outline=(60, 110, 125, 255), width=3)
    
    out_path = anim_dir / "bg_drought_lake.png"
    im.save(out_path)
    print("Generated bg_drought_lake.png")
    return out_path

def create_electric_mule_prop():
    """7. 2D Cartoon Electric Mule Locomotive Prop (Transparent PNG)."""
    mw, mh = 420, 260
    im = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Heavy Silver Industrial Chassis
    base_y = 170
    draw.rounded_rectangle([40, 90, 380, base_y], radius=10, fill=(175, 182, 192, 255), outline=(40, 45, 55, 255), width=4)
    
    # Dual Operator Cabs (Left and Right ends)
    draw.rectangle([45, 60, 120, 90], fill=(210, 218, 228, 255), outline=(40, 45, 55, 255), width=3)
    draw.rectangle([55, 68, 110, 84], fill=(85, 155, 215, 255)) # Cab window
    
    draw.rectangle([300, 60, 375, 90], fill=(210, 218, 228, 255), outline=(40, 45, 55, 255), width=3)
    draw.rectangle([310, 68, 365, 84], fill=(85, 155, 215, 255))
    
    # Center Cable Winch Drum (with coiled steel wire)
    draw.ellipse((165, 50, 255, 140), fill=(80, 85, 95, 255), outline=(30, 35, 45, 255), width=4)
    for r in range(60, 95, 8):
        draw.ellipse((210 - r//2, 95 - r//2, 210 + r//2, 95 + r//2), outline=(220, 220, 220, 220), width=2)
        
    # Towing Cable leading up and to the right
    draw.line([(210, 75), (420, 20)], fill=(255, 215, 0, 255), width=4)
    
    # Heavy Cog Wheels (4 steel track wheels)
    wheel_y = base_y + 25
    for wx in [80, 150, 270, 340]:
        draw.ellipse((wx - 25, wheel_y - 25, wx + 25, wheel_y + 25), fill=(55, 60, 70, 255), outline=(20, 25, 30, 255), width=3)
        draw.ellipse((wx - 8, wheel_y - 8, wx + 8, wheel_y + 8), fill=(220, 180, 40, 255)) # Gold hubcap
        
    out_path = anim_dir / "prop_electric_mule.png"
    im.save(out_path)
    print("Generated prop_electric_mule.png")
    return out_path

def build_all_assets():
    print("Building procedural 2D vector graphic assets...")
    create_panama_map()
    create_locks_cutaway()
    create_container_ship_prop()
    create_lock_canyon_background()
    create_jungle_storm_background()
    create_drought_lake_background()
    create_electric_mule_prop()
    print("All procedural vector assets built successfully!")

if __name__ == '__main__':
    build_all_assets()
