import json
import re

phrases_map = {
    1: [
        "Sitting across the {\\c&H0020FFFF&}Yangtze River{\\c&H00FFFFFF&}",
        "is a {\\c&H0020FFFF&}concrete monster{\\c&H00FFFFFF&} so heavy",
        "that it physically changed the {\\c&H0020FFFF&}rotation of planet Earth{\\c&H00FFFFFF&}."
    ],
    2: [
        "NASA geophysicists calculated that raising",
        "{\\c&H0020FFFF&}39 trillion kilograms{\\c&H00FFFFFF&} of water",
        "{\\c&H0020FFFF&}175 meters{\\c&H00FFFFFF&} above sea level",
        "increased Earth's {\\c&H0020FFFF&}moment of inertia{\\c&H00FFFFFF&}."
    ],
    3: [
        "Just like a spinning ice skater slowing down",
        "when they {\\c&H0020FFFF&}stretch out their arms{\\c&H00FFFFFF&},",
        "raising water against gravity",
        "slowed Earth's daily spin by {\\c&H0020FFFF&}0.06 microseconds{\\c&H00FFFFFF&}."
    ],
    4: [
        "Beneath the reservoir,",
        "{\\c&H0020FFFF&}32 colossal hydro-turbines{\\c&H00FFFFFF&}",
        "produce {\\c&H0020FFFF&}22,500 megawatts{\\c&H00FFFFFF&}:",
        "enough electricity to {\\c&H0020FFFF&}power entire nations{\\c&H00FFFFFF&}."
    ],
    5: [
        "To bypass the 400-foot wall,",
        "engineers built a {\\c&H0020FFFF&}3,000-ton ship elevator{\\c&H00FFFFFF&}",
        "that hoists entire cargo freighters",
        "in just {\\c&H0020FFFF&}40 minutes{\\c&H00FFFFFF&}."
    ],
    6: [
        "The weight is so immense that geologists monitor",
        "{\\c&H0020FFFF&}tectonic fault lines{\\c&H00FFFFFF&} beneath the reservoir,",
        "where {\\c&H0020FFFF&}reservoir-induced seismicity{\\c&H00FFFFFF&}",
        "triggers thousands of {\\c&H0020FFFF&}micro-tremors{\\c&H00FFFFFF&}."
    ],
    7: [
        "Built to tame floods that historically",
        "killed over {\\c&H0020FFFF&}300,000 people{\\c&H00FFFFFF&},",
        "it absorbs the full force",
        "of {\\c&H0020FFFF&}500-year Pacific superstorms{\\c&H00FFFFFF&}."
    ],
    8: [
        "Is {\\c&H0020FFFF&}altering planetary mechanics{\\c&H00FFFFFF&}",
        "worth clean energy?",
        "Hit {\\c&H0020FFFF&}Subscribe{\\c&H00FFFFFF&} and share your verdict below."
    ]
}

def update_pipeline():
    with open("src/workflows/daily_shorts_pipeline.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    in_three_gorges = False
    current_scene = None

    for line in lines:
        if '"id": "three_gorges_rotation"' in line:
            in_three_gorges = True
        elif in_three_gorges and '"id": "' in line:
            in_three_gorges = False

        if in_three_gorges and '"scene_num":' in line:
            m = re.search(r'"scene_num":\s*(\d+)', line)
            if m:
                current_scene = int(m.group(1))

        if in_three_gorges and '"subtitle_phrases":' in line:
            # Skip existing phrase line to avoid duplicates
            continue

        new_lines.append(line)

        if in_three_gorges and '"narration_text":' in line and current_scene in phrases_map:
            phrases = phrases_map[current_scene]
            indent = " " * 16
            phrases_json = ",\n".join([f'{indent}    "{p}"' for p in phrases])
            new_lines.append(f'{indent}"subtitle_phrases": [\n{phrases_json}\n{indent}],\n')

    with open("src/workflows/daily_shorts_pipeline.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print("Added/updated subtitle_phrases for three_gorges_rotation successfully!")

if __name__ == "__main__":
    update_pipeline()
