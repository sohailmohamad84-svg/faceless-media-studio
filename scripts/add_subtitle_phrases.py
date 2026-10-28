import re
import sys

phrases_map = {
    1: [
        "Singapore is {\\c&H0020FFFF&}25% larger{\\c&H00FFFFFF&} today",
        "than when it gained independence in {\\c&H0020FFFF&}1965{\\c&H00FFFFFF&}."
    ],
    2: [
        "To construct modern skyscrapers and ports,",
        "Singapore imported over {\\c&H0020FFFF&}500 million tons{\\c&H00FFFFFF&} of sand,",
        "becoming the world's {\\c&H0020FFFF&}largest sand importer{\\c&H00FFFFFF&}."
    ],
    3: [
        "When regional bans halted legal supplies,",
        "an illicit dredging {\\c&H0020FFFF&}black market{\\c&H00FFFFFF&} devastated ecosystems,",
        "causing up to {\\c&H0020FFFF&}two dozen Indonesian islets{\\c&H00FFFFFF&}",
        "to submerge below the tides."
    ],
    4: [
        "To diversify beyond imported sand,",
        "Singapore pioneered massive {\\c&H0020FFFF&}Dutch-style polders{\\c&H00FFFFFF&},",
        "sealing ocean basins with {\\c&H0020FFFF&}reinforced dikes{\\c&H00FFFFFF&}",
        "to reclaim land below sea level."
    ],
    5: [
        "Miles of {\\c&H0020FFFF&}prefabricated vertical drains{\\c&H00FFFFFF&}",
        "accelerate water expulsion from deep marine clay",
        "under massive {\\c&H0020FFFF&}surcharge weight{\\c&H00FFFFFF&},",
        "consolidating unstable seabed silt",
        "into {\\c&H0020FFFF&}solid ground foundations{\\c&H00FFFFFF&}."
    ],
    6: [
        "The result is {\\c&H0020FFFF&}Tuas Mega Port{\\c&H00FFFFFF&}:",
        "planned to become the world's {\\c&H0020FFFF&}largest automated terminal{\\c&H00FFFFFF&}",
        "upon completion in the {\\c&H0020FFFF&}2040s{\\c&H00FFFFFF&},",
        "with Phase One already operational."
    ],
    7: [
        "With sea levels projected to rise,",
        "newly reclaimed land is mandated",
        "to sit at least {\\c&H0020FFFF&}4 to 5 meters above SHD{\\c&H00FFFFFF&},",
        "creating an {\\c&H0020FFFF&}existential coastal fortress{\\c&H00FFFFFF&} against the sea."
    ],
    8: [
        "Could other vulnerable coastal nations",
        "{\\c&H0020FFFF&}engineer their way out{\\c&H00FFFFFF&} of rising seas?",
        "Subscribe and leave your perspective in the comments."
    ]
}

with open("src/workflows/daily_shorts_pipeline.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
in_singapore = False
current_scene = None

for line in lines:
    if '"id": "singapore_sand_empire"' in line:
        in_singapore = True
    elif in_singapore and '"id": "' in line:
        in_singapore = False

    if in_singapore and '"scene_num":' in line:
        m = re.search(r'"scene_num":\s*(\d+)', line)
        if m:
            current_scene = int(m.group(1))

    new_lines.append(line)

    if in_singapore and '"narration_text":' in line and current_scene in phrases_map:
        phrases = phrases_map[current_scene]
        indent = " " * 16
        phrases_json = ",\n".join([f'{indent}    "{p}"' for p in phrases])
        new_lines.append(f'{indent}"subtitle_phrases": [\n{phrases_json}\n{indent}],\n')

with open("src/workflows/daily_shorts_pipeline.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Added subtitle_phrases to all 8 scenes in daily_shorts_pipeline.py successfully!")
