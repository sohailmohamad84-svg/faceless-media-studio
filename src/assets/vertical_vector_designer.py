"""Generate 1080x1920 Vertical Vector Backgrounds for Panama Canal YouTube Short."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

v_dir = Path("data/assets/panama_shorts")
v_dir.mkdir(parents=True, exist_ok=True)

vw, vh = 1080, 1920

def get_font(size, bold=True):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except:
        return ImageFont.load_default()

def create_vertical_elevator():
    """Scene 1: Vertical Mountain Elevator Cutaway (1080x1920)."""
    im = Image.new("RGBA", (vw, vh), (245, 240, 228, 255))
    draw = ImageDraw.Draw(im)
    
    # Sky gradient at top
    for y in range(600):
        alpha = int(255 * (1 - y / 600.0) * 0.2)
        draw.line([(0, y), (vw, y)], fill=(120, 195, 245, alpha))
        
    # Continental Mountain Silhouette in background
    draw.polygon([(0, 950), (320, 680), (540, 520), (760, 690), (vw, 920), (vw, vh), (0, vh)], fill=(165, 135, 95, 255))
    
    # Terraced Lock Steps (Gatun Locks Climbing 85 ft)
    # Step 0: Sea Level (y: 1550)
    draw.rectangle([0, 1550, vw, vh], fill=(130, 95, 60, 255))
    draw.rectangle([0, 1550, 420, 1750], fill=(0, 175, 235, 230)) # Atlantic sea level water
    draw.text((40, 1620), "SEA LEVEL (0 FT)", font=get_font(28, True), fill=(255, 255, 255, 255))
    
    # Concrete Lock Steps climbing up
    # Step 1 (+28 ft)
    draw.rectangle([280, 1320, 520, 1550], fill=(170, 175, 185, 255), outline=(60, 65, 75, 255), width=4)
    draw.rectangle([280, 1320, 520, 1460], fill=(0, 190, 245, 220))
    draw.text((310, 1480), "STEP 1\n+28 FT", font=get_font(24, True), fill=(20, 30, 40, 255))
    
    # Step 2 (+56 ft)
    draw.rectangle([500, 1100, 740, 1320], fill=(170, 175, 185, 255), outline=(60, 65, 75, 255), width=4)
    draw.rectangle([500, 1100, 740, 1240], fill=(0, 205, 250, 220))
    draw.text((530, 1260), "STEP 2\n+56 FT", font=get_font(24, True), fill=(20, 30, 40, 255))
    
    # Summit Reservoir: Lake Gatun (+85 ft, y: 860 to 1100)
    draw.rectangle([720, 860, vw, 1100], fill=(170, 175, 185, 255), outline=(60, 65, 75, 255), width=4)
    draw.rectangle([720, 860, vw, 1020], fill=(0, 220, 255, 240)) # Summit water
    
    # Giant Callout Banner at top
    draw.rounded_rectangle([60, 180, vw - 60, 320], radius=16, fill=(20, 30, 45, 240), outline=(255, 215, 0, 255), width=4)
    draw.text((105, 205), "THE 85-FOOT MOUNTAIN TRAP", font=get_font(46, True), fill=(255, 215, 0, 255))
    draw.text((135, 265), "Ships Lifted Over a Mountain by Rainwater", font=get_font(28, False), fill=(220, 240, 255, 240))
    
    # +85 FT Floating Indicator Badge
    draw.rounded_rectangle([750, 760, 1010, 830], radius=10, fill=(220, 50, 50, 255), outline=(255, 255, 255, 255), width=3)
    draw.text((775, 775), "SUMMIT: +85 FT", font=get_font(30, True), fill=(255, 255, 255, 255))
    
    out_path = v_dir / "bg_vertical_elevator.png"
    im.save(out_path)
    print("Generated bg_vertical_elevator.png")
    return out_path

def create_vertical_map():
    """Scene 2: Vertical Map Split (Tidal Paradox)."""
    im = Image.new("RGBA", (vw, vh), (20, 40, 65, 255))
    draw = ImageDraw.Draw(im)
    
    # Continents
    draw.polygon([(0, 0), (vw, 0), (vw, 480), (680, 720), (520, 860), (380, 940), (140, 920), (0, 780)], fill=(205, 175, 120, 255))
    draw.polygon([(420, 960), (680, 1040), (880, 1220), (960, 1500), (820, vh), (0, vh)], fill=(195, 165, 110, 255))
    
    # Tidal Wave Gauge Box in Lower Half
    draw.rounded_rectangle([60, 1180, vw - 60, 1680], radius=20, fill=(15, 25, 40, 240), outline=(0, 220, 255, 255), width=4)
    draw.text((120, 1220), "THE SEA-LEVEL TIDAL DISASTER", font=get_font(38, True), fill=(255, 215, 0, 255))
    
    # Comparison Columns: Pacific vs Atlantic
    # Pacific (Left): 20 FT Tides
    draw.rectangle([120, 1340, 480, 1580], fill=(220, 60, 50, 200), outline=(255, 80, 80, 255), width=3)
    draw.text((150, 1360), "PACIFIC OCEAN", font=get_font(26, True), fill=(255, 255, 255, 255))
    draw.text((150, 1420), "+20 FT TIDES", font=get_font(42, True), fill=(255, 255, 255, 255))
    draw.text((150, 1500), "8 inches higher\nDangerous tidal surge", font=get_font(22, False), fill=(255, 220, 220, 255))
    
    # Atlantic (Right): 2 FT Tides
    draw.rectangle([580, 1340, 940, 1580], fill=(40, 130, 215, 200), outline=(80, 180, 255, 255), width=3)
    draw.text((610, 1360), "ATLANTIC OCEAN", font=get_font(26, True), fill=(255, 255, 255, 255))
    draw.text((610, 1420), "+2 FT TIDES", font=get_font(42, True), fill=(255, 255, 255, 255))
    draw.text((610, 1500), "Calm & Stable\nNo tidal lock", font=get_font(22, False), fill=(220, 240, 255, 255))
    
    out_path = v_dir / "bg_vertical_map.png"
    im.save(out_path)
    print("Generated bg_vertical_map.png")
    return out_path

def create_vertical_lock():
    """Scene 3: Vertical Lock Chamber Interior (1080x1920)."""
    im = Image.new("RGBA", (vw, vh), (180, 190, 200, 255))
    draw = ImageDraw.Draw(im)
    
    # Concrete Lock Walls (Deep perspective)
    # Left Wall
    draw.polygon([(0, 0), (320, 500), (320, 1300), (0, vh), (0, 0)], fill=(155, 160, 168, 255), outline=(95, 100, 108, 255), width=4)
    # Right Wall
    draw.polygon([(vw, 0), (760, 500), (760, 1300), (vw, vh), (vw, 0)], fill=(150, 155, 162, 255), outline=(90, 95, 102, 255), width=4)
    
    # Electric Mule Tracks on both walls
    draw.line([(0, 1100), (320, 780)], fill=(50, 50, 60, 255), width=8)
    draw.line([(vw, 1100), (760, 780)], fill=(50, 50, 60, 255), width=8)
    
    # Water in lower half
    water_pts = [(320, 780), (760, 780), (vw, vh), (0, vh)]
    draw.polygon(water_pts, fill=(0, 185, 235, 255))
    
    # Steel Miter Gates in distance
    draw.polygon([(320, 480), (540, 530), (540, 800), (320, 760)], fill=(60, 70, 85, 255), outline=(25, 30, 40, 255), width=3)
    draw.polygon([(760, 480), (540, 530), (540, 800), (760, 760)], fill=(55, 65, 80, 255), outline=(25, 30, 40, 255), width=3)
    
    # HUD: Hydraulic Specs Banner at top
    draw.rounded_rectangle([60, 140, vw - 60, 280], radius=14, fill=(20, 25, 35, 230), outline=(0, 220, 255, 255), width=3)
    draw.text((110, 165), "HYDRAULIC WATER ELEVATOR", font=get_font(42, True), fill=(0, 230, 255, 255))
    draw.text((110, 225), "Zero Water Pumps | 100% Gravity Powered", font=get_font(26, False), fill=(255, 255, 255, 240))
    
    out_path = v_dir / "bg_vertical_lock.png"
    im.save(out_path)
    print("Generated bg_vertical_lock.png")
    return out_path

def create_vertical_drought():
    """Scene 5: Vertical Drought Lake & Auction (1080x1920)."""
    im = Image.new("RGBA", (vw, vh), (235, 220, 190, 255)) # Hazy desert heat
    draw = ImageDraw.Draw(im)
    
    # Scorching sun at top
    draw.ellipse((540 - 90, 320 - 90, 540 + 90, 320 + 90), fill=(255, 235, 120, 255))
    for r in range(110, 260, 40):
        draw.ellipse((540 - r, 320 - r, 540 + r, 320 + r), outline=(255, 200, 70, 80), width=3)
        
    # Cracked Mud Flats (Lower half)
    mud_pts = [(0, 720), (380, 680), (740, 740), (vw, 700), (vw, vh), (0, vh)]
    draw.polygon(mud_pts, fill=(165, 130, 85, 255), outline=(125, 90, 55, 255), width=4)
    # Mud cracks
    for x in range(0, vw, 120):
        for y in range(750, vh, 110):
            draw.line([(x, y), (x + 35, y + 25), (x + 15, y + 60)], fill=(100, 70, 40, 160), width=2)
            
    # Sunken dead tree stumps
    for sx, sy in [(220, 920), (520, 840), (840, 880)]:
        draw.polygon([(sx - 15, sy), (sx - 6, sy - 90), (sx + 6, sy - 90), (sx + 15, sy)], fill=(55, 40, 25, 255))
        draw.line([(sx - 6, sy - 90), (sx - 30, sy - 130)], fill=(55, 40, 25, 255), width=5)
        draw.line([(sx + 6, sy - 90), (sx + 25, sy - 125)], fill=(55, 40, 25, 255), width=5)
        
    # Giant Red Auction Alert Card
    draw.rounded_rectangle([60, 1150, vw - 60, 1650], radius=20, fill=(25, 20, 25, 240), outline=(255, 60, 50, 255), width=4)
    draw.text((120, 1190), "2023 CLIMATE EMERGENCY", font=get_font(38, True), fill=(255, 70, 60, 255))
    
    # Auction price box
    draw.rounded_rectangle([120, 1270, 960, 1440], radius=12, fill=(180, 30, 30, 255))
    draw.text((180, 1300), "$4,000,000", font=get_font(72, True), fill=(255, 255, 255, 255))
    draw.text((220, 1390), "PAID FOR 1 PRIORITY TRANSIT SLOT", font=get_font(26, True), fill=(255, 235, 120, 255))
    
    draw.text((120, 1480), "160+ Ships Stranded at Sea\nDaily transits slashed from 38 down to 22", font=get_font(28, False), fill=(230, 230, 240, 240))
    
    out_path = v_dir / "bg_vertical_drought.png"
    im.save(out_path)
    print("Generated bg_vertical_drought.png")
    return out_path

def build_all_vertical():
    print("Building 1080x1920 vertical vector assets...")
    create_vertical_elevator()
    create_vertical_map()
    create_vertical_lock()
    create_vertical_drought()
    print("All vertical assets built successfully!")

if __name__ == '__main__':
    build_all_vertical()
