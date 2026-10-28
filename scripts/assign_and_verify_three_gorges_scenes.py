import hashlib
import os
import shutil
import subprocess

TILE_TO_SCENE = {
    1: 7, # Tile 7 -> Scene 1: Three Gorges Dam releasing water
    2: 6, # Tile 6 -> Scene 2: Earth spinning in deep space
    3: 5, # Tile 5 -> Scene 3: Spinning figure skater
    4: 4, # Tile 4 -> Scene 4: Francis hydro-turbines
    5: 3, # Tile 3 -> Scene 5: Ship lift raising barge
    6: 2, # Tile 2 -> Scene 6: Geological fault line simulation
    7: 1, # Tile 1 -> Scene 7: Flood currents striking concrete
    8: 0, # Tile 0 -> Scene 8: Drone rising over dam reservoir
}

SCENE_NAMES = {
    1: "The Massive Spillway Hook",
    2: "Planetary Physics & Moment of Inertia",
    3: "Spinning Figure Skater Analogy",
    4: "3D Internal Turbine Cutaway",
    5: "Ship Elevator Engineering Marvel",
    6: "Seismic Stress & Crustal Fault Lines",
    7: "Flood Defense Shockwave",
    8: "Golden Dam Crest Panorama & CTA"
}

print("=======================================================")
print("ASSIGNING & VERIFYING ALL 8 THREE GORGES SCENES")
print("=======================================================")

seen_hashes = set()

for sc_num in range(1, 9):
    tile_idx = TILE_TO_SCENE[sc_num]
    src_tile = f"data/flow_clips/tile_{tile_idx}.mp4"
    dst1 = f"data/flow_clips/three_gorges_scene_{sc_num}.mp4"
    dst2 = f"data/flow_clips/threegorges_scene_{sc_num}.mp4"
    
    assert os.path.exists(src_tile), f"Missing {src_tile}!"
    shutil.copyfile(src_tile, dst1)
    shutil.copyfile(src_tile, dst2)
    
    data = open(dst1, "rb").read()
    h = hashlib.sha256(data).hexdigest()
    seen_hashes.add(h)
    
    # ffprobe check
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,duration", "-of", "csv=p=0", dst1]
    probe_out = subprocess.check_output(cmd).decode().strip()
    
    print(f"Scene {sc_num} [Tile {tile_idx}] ({SCENE_NAMES[sc_num]}):")
    print(f"  File size: {len(data):,} bytes")
    print(f"  Probe: {probe_out}")
    print(f"  SHA256: {h[:20]}...")

print("\n-------------------------------------------------------")
print(f"Total verified scenes: 8")
print(f"Unique SHA-256 hashes: {len(seen_hashes)}/8")
assert len(seen_hashes) == 8, "ERROR: Some scenes share identical hashes!"
print("ALL 8 SCENES VERIFIED 100% UNIQUE & VALID!")
print("=======================================================")
