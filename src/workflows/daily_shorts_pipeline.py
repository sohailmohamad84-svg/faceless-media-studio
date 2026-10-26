"""Automated Daily YouTube Shorts Production & Publishing Engine.
Runs autonomously in the cloud:
1. Picks the highest-ranked unproduced deep-researched topic.
2. Generates the 5-act high-retention vertical script.
3. Assembles 1080x1920 Full HD visuals, ChristopherNeural voiceover, and organic Foley.
4. Burns in gold kinetic mobile subtitles.
5. Uploads the finished short directly to YouTube Shorts with SEO tags and descriptions.
6. Returns the live YouTube Shorts URL.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Ensure project root is always in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database.connection import init_db
from src.research.discovery import TopicDiscoveryEngine
from src.database.repository import TopicRepository
from src.assets.sound_designer import SoundDesigner
from src.youtube.oauth import YouTubeAuthManager
from src.youtube.uploader import YouTubePublisher
from src.editing.flow_master_engine import FlowMasterEngine

# Pre-researched viral topics queue with complete 5-act vertical storyboards
VIRAL_SHORTS_QUEUE = [
    {
        "id": "suez_canal_ghost_fleet",
        "title": "The 24-Hour Ghost Fleet of the Suez Canal",
        "hook": "How one single rudder angle froze twelve percent of world trade in seconds.",
        "description": (
            "How did one single rudder angle trap 400 cargo ships and freeze $10 billion in world trade daily? "
            "Discover the terrifying physics of the Suez Canal megajams.\n\n"
            "🚢 Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
            "#shorts #suezcanal #engineering #megaprojects #maritime #history #logistics #facts"
        ),
        "tags": ["shorts", "suezcanal", "evergiven", "engineering", "megaprojects", "shipping", "documentary"],
        "scenes": [
            {
                "input_video": "data/suez_assets/suez_clip_1.mp4",
                "is_clean": True,
                "narration_text": "Four hundred cargo ships were trapped in the desert. Not by pirates. By an invisible wall of sand.",
                "foley": [
                    {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.3},
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_2.mp4",
                "is_clean": True,
                "narration_text": "A forty-knot wind struck the world's longest container ship, jamming its twenty-thousand-ton bow into solid clay.",
                "foley": [
                    {"sfx": "gate_clank.wav", "time_offset": 0.4, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_3.mp4",
                "is_clean": True,
                "narration_text": "Every single hour it remained stuck cost the global economy four hundred million dollars in frozen cargo.",
                "foley": [
                    {"sfx": "warning_beep.wav", "time_offset": 0.2, "gain": 0.3}
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_4.mp4",
                "is_clean": True,
                "narration_text": "Fourteen massive tugboats and thirty thousand tons of dredged silt fought against the Mediterranean tide.",
                "foley": [
                    {"sfx": "water_rush.wav", "time_offset": 0.5, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_5.mp4",
                "is_clean": True,
                "narration_text": "Six days later, a full moon super-tide lifted the monster free, proving the fragility of modern civilization.",
                "foley": [
                    {"sfx": "ship_horn.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            }
        ]
    },
    {
        "id": "dubai_sinking_islands",
        "title": "The $100 Billion Sinking Islands of Dubai",
        "hook": "The artificial world archipelago that the ocean is slowly reclaiming.",
        "description": (
            "Three hundred artificial islands built with 320 million cubic meters of sand. "
            "Why is Dubai's most ambitious megaproject slowly being swallowed back into the Persian Gulf?\n\n"
            "🏝️ Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
            "#shorts #dubai #engineering #megaprojects #architecture #theworld #history #geopolitics"
        ),
        "tags": ["shorts", "dubai", "theworld", "megaprojects", "engineering", "architecture", "documentary"],
        "scenes": [
            {
                "input_video": "data/dubai_assets/dubai_clip_1.mp4",
                "is_clean": True,
                "narration_text": "Three hundred artificial islands were carved into the ocean to look like the planet Earth.",
                "foley": [
                    {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_2.mp4",
                "is_clean": True,
                "narration_text": "Over three hundred million cubic meters of sand were dredged from the seabed to build paradise.",
                "foley": [
                    {"sfx": "drill_rumble.wav", "time_offset": 0.4, "gain": 0.35},
                    {"sfx": "water_rush.wav", "time_offset": 1.0, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_3.mp4",
                "is_clean": True,
                "narration_text": "Then the financial crash hit. Construction froze, and the ocean currents began reclaiming the coastlines.",
                "foley": [
                    {"sfx": "gate_clank.wav", "time_offset": 0.5, "gain": 0.35},
                    {"sfx": "dust_puff.wav", "time_offset": 1.5, "gain": 0.3}
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_4.mp4",
                "is_clean": True,
                "narration_text": "Satellite tracking showed the islands slowly sinking and eroding back into the Persian Gulf.",
                "foley": [
                    {"sfx": "radar_ping.wav", "time_offset": 0.4, "gain": 0.35},
                    {"sfx": "warning_beep.wav", "time_offset": 1.2, "gain": 0.3}
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_5.mp4",
                "is_clean": True,
                "narration_text": "Now, luxury developers are racing to fortify the sea walls before this hundred-billion-dollar wonder disappears.",
                "foley": [
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4},
                    {"sfx": "desert_wind.wav", "time_offset": 1.0, "gain": 0.25}
                ]
            }
        ]
    },
    {
        "id": "japan_maglev_speed",
        "title": "The 375 MPH Train That Levitates on Superconductors",
        "hook": "Why Japan mastered 375 MPH levitating trains while Hyperloop collapsed.",
        "description": (
            "Floating four inches above the track, Japan's L0 Series Maglev travels at half the speed of sound without wheels. "
            "How did Japanese engineers conquer gravity using liquid helium cryogenics while Silicon Valley burned billions on failed vacuum tubes?\n\n"
            "🚄 Like & Subscribe for daily high-retention engineering & megaproject documentaries!\n\n"
            "#shorts #maglev #bullettrain #engineering #japan #hyperloop #technology #speed #physics #megaprojects"
        ),
        "tags": ["shorts", "maglev", "bullettrain", "engineering", "japan", "hyperloop", "technology", "documentary", "physics", "trains"],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Supersonic Ground Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Cinematic low-angle ground tracking shot of the Japanese L0 Series Maglev bullet train rushing past the camera at 375 MPH through a concrete U-shaped guideway, vapor trails peeling off the aerodynamic nose, ultra-smooth motion, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_1.mp4",
                "is_clean": True,
                "narration_text": "Floating four inches above the ground, this train travels at half the speed of sound without ever touching the track. It is not science fiction. It is Japan's L0 Series Maglev.",
                "foley": [
                    {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "scene_num": 2,
                "title": "Topographic Barrier / Map Flyover",
                "graphic_type": "3D_SATELLITE_CARTOGRAPHY",
                "prompt": "Cinematic 3D satellite digital elevation model flyover over the jagged snowcapped mountains of the Japanese Southern Alps, glowing neon cyan route line tunneling straight through granite peaks from Tokyo to Osaka, photorealistic cartography, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_2.mp4",
                "is_clean": True,
                "narration_text": "Japan is covered in jagged granite mountains. Connecting Tokyo to Osaka through the Southern Alps by traditional rail was physically impossible at supersonic speeds. Engineers had to literally conquer gravity.",
                "foley": [
                    {"sfx": "desert_wind.wav", "time_offset": 0.2, "gain": 0.25}
                ]
            },
            {
                "scene_num": 3,
                "title": "Silicon Valley Hype vs Engineering Reality",
                "graphic_type": "HISTORICAL_CONTRAST",
                "prompt": "Cinematic split-screen documentary style: left side showing an experimental vacuum hyperloop steel tube buckling under atmospheric pressure, right side showing a high-tech Japanese cryogenic laboratory testing superconducting coils glowing with cold blue light, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_3.mp4",
                "is_clean": True,
                "narration_text": "While Silicon Valley burned billions trying to build vacuum tubes that buckled under atmospheric pressure, Japanese engineers focused on pure physics: superconducting magnets cooled to minus four hundred and fifty degrees.",
                "foley": [
                    {"sfx": "gate_clank.wav", "time_offset": 0.3, "gain": 0.35}
                ]
            },
            {
                "scene_num": 4,
                "title": "3D Architectural Cutaway / Cross-Section",
                "graphic_type": "ARCHITECTURAL_CUTAWAY_CROSS_SECTION",
                "prompt": "Architectural 3D cutaway cross-section of a Maglev train bogie and concrete guideway sidewall, transparent metal chassis revealing niobium-titanium superconducting coils inside liquid helium tanks, glowing magnetic flux lines repelling the track and lifting the train four inches high, technical engineering visualization, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_4.mp4",
                "is_clean": True,
                "narration_text": "Here is the secret. Inside the bogies are superconducting coils cooled by liquid helium. As the train accelerates, these coils induce a massive magnetic field in the concrete guideway walls, creating pure repulsive levitation.",
                "foley": [
                    {"sfx": "water_rush.wav", "time_offset": 0.4, "gain": 0.35}
                ]
            },
            {
                "scene_num": 5,
                "title": "Linear Synchronous Motor Propulsion",
                "graphic_type": "3D_TECHNICAL_SCHEMATIC",
                "prompt": "3D animated technical schematic inside the concrete guideway walls, alternating electromagnetic coils pulsing in synchronized blue and orange light wave packets pulling the train forward at high velocity, cinematic motion graphic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_5.mp4",
                "is_clean": True,
                "narration_text": "There is no engine on board. Electric power is fed directly into the track walls, pulling the front of each car forward while pushing from behind. The entire guideway acts as a giant electric motor.",
                "foley": [
                    {"sfx": "drill_rumble.wav", "time_offset": 0.3, "gain": 0.3}
                ]
            },
            {
                "scene_num": 6,
                "title": "Carving 50 Miles of Granite Tunnels",
                "graphic_type": "SUBTERRANEAN_ENGINEERING",
                "prompt": "Heavy industrial underground construction shot inside a deep Alpine mountain tunnel, massive tunnel boring machine cutterhead spinning against solid granite rock with high pressure water mist, industrial floodlights, muddy bedrock, cinematic documentary, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_6.mp4",
                "is_clean": True,
                "narration_text": "To keep the line completely straight at six hundred kilometers per hour, Japan is spending sixty billion dollars drilling fifty miles of continuous deep mountain tunnels through tectonic fault lines.",
                "foley": [
                    {"sfx": "drill_rumble.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "scene_num": 7,
                "title": "Cockpit Telemetry & Passenger Sensation",
                "graphic_type": "FIRST_PERSON_TELEMETRY",
                "prompt": "Futuristic high-tech train driver console view looking through the cockpit window down an illuminated guideway, digital HUD telemetry overlay showing 603 km/h 375 MPH with zero vibration, lush Japanese landscape blurring by, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_7.mp4",
                "is_clean": True,
                "narration_text": "Inside the cockpit, there is no vibration. The digital speedometer climbs past three hundred and seventy-five miles per hour. Passengers feel like they are cruising in a private jet at ground level.",
                "foley": [
                    {"sfx": "warning_beep.wav", "time_offset": 0.4, "gain": 0.35}
                ]
            },
            {
                "scene_num": 8,
                "title": "The Civil Engineering Triumph & Call to Action",
                "graphic_type": "EPIC_DRONE_FLYOVER",
                "prompt": "Cinematic wide aerial drone shot of the gleaming silver aerodynamic Maglev bullet train bursting out of an Alpine mountain portal onto a soaring viaduct over a crystal clear river gorge, morning sun reflecting off the fuselage, epic documentary finish, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/maglev_scene_8.mp4",
                "is_clean": True,
                "narration_text": "In twenty-twenty-seven, the journey from Tokyo to Nagoya will take just forty minutes. Proving that true civil engineering always beats tech hype. Would you ride a train with no wheels? Let us know in the comments.",
                "foley": [
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.45}
                ]
            }
        ]
    },
    {
        "id": "concorde_sonic_tragedy",
        "title": "Why You Can't Fly Supersonic Anymore",
        "hook": "How a single piece of runway titanium destroyed the world's fastest passenger airliner.",
        "description": (
            "Concorde flew from New York to London in under three hours at Mach 2. "
            "Why did commercial aviation become 40% slower after 2003?\n\n"
            "✈️ Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
            "#shorts #concorde #aviation #engineering #planes #history #supersonic #travel #speed"
        ),
        "tags": ["shorts", "concorde", "aviation", "engineering", "planes", "history", "supersonic", "documentary"],
        "scenes": [
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "In nineteen-ninety-six, you could fly from London to New York faster than the Earth's rotation.",
                "foley": [
                    {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Cruising at sixty thousand feet, Concorde's titanium nose stretched eight inches from atmospheric heat.",
                "foley": [
                    {"sfx": "radar_ping.wav", "time_offset": 0.4, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Then in Paris, a sixteen-inch titanium strip dropped on the runway shredded a tire at two hundred miles an hour.",
                "foley": [
                    {"sfx": "gate_clank.wav", "time_offset": 0.5, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "The supersonic boom was banned over land, passenger demand collapsed, and airline speeds dropped forty percent.",
                "foley": [
                    {"sfx": "warning_beep.wav", "time_offset": 0.3, "gain": 0.3}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Twenty-three years later, we still fly slower than passengers did in nineteen-seventy-six.",
                "foley": [
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.45}
                ]
            }
        ]
    },
    {
        "id": "singapore_sand_empire",
        "title": "The Secret Ocean War for Singapore's Sand",
        "hook": "How a tiny island nation grew twenty-five percent bigger using smuggled seabed sand.",
        "description": (
            "Singapore has expanded its land area by over 130 square kilometers. "
            "Where did hundreds of millions of tons of ocean sand come from?\n\n"
            "🏝️ Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
            "#shorts #singapore #megaprojects #geopolitics #engineering #landreclamation #facts #ocean"
        ),
        "tags": ["shorts", "singapore", "megaprojects", "geopolitics", "engineering", "landreclamation", "documentary"],
        "scenes": [
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Singapore is twenty-five percent larger today than when it gained independence in nineteen-sixty-five.",
                "foley": [
                    {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "To build skyscrapers and mega-ports, the city devoured over five hundred million tons of foreign sand.",
                "foley": [
                    {"sfx": "drill_rumble.wav", "time_offset": 0.4, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "When neighboring nations banned sand exports, an illicit billion-dollar black market dredged entire Indonesian islands out of existence.",
                "foley": [
                    {"sfx": "water_rush.wav", "time_offset": 0.5, "gain": 0.35}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Today, massive polder dikes and recycled clay are replacing sand to push the coastline even further into the sea.",
                "foley": [
                    {"sfx": "gate_clank.wav", "time_offset": 0.4, "gain": 0.3}
                ]
            },
            {
                "input_video": "data/showcase/Dubai_Islands_34s_Viral_Master_1080p.mp4",
                "narration_text": "Proving that when you run out of territory on Earth, money can build you a new country.",
                "foley": [
                    {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.45}
                ]
            }
        ]
    }
]


class DailyShortsPipeline:
    LOG_FILE = Path("data/daily_shorts_log.json")

    @classmethod
    def get_published_ids(cls) -> list:
        if not cls.LOG_FILE.exists():
            return []
        try:
            import json
            with open(cls.LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def record_published_id(cls, item_id: str, youtube_url: str):
        import json
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        records = cls.get_published_ids()
        records.append({
            "id": item_id,
            "youtube_url": youtube_url,
            "timestamp": datetime.utcnow().isoformat()
        })
        with open(cls.LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    @classmethod
    async def produce_and_publish_next_short(cls, privacy_status: str = "public") -> Dict[str, Any]:
        """Produce the next scheduled short and publish directly to YouTube Shorts."""
        # Ensure database and sounds
        init_db()
        SoundDesigner.ensure_sfx_library()

        published = [r["id"] for r in cls.get_published_ids()]
        next_item = None
        for item in VIRAL_SHORTS_QUEUE:
            if item["id"] not in published:
                next_item = item
                break

        if not next_item:
            return {
                "success": False,
                "error": "All scheduled shorts in queue have already been produced and published!"
            }

        # Step 1: Render Master Short Video
        output_name = f"{next_item['id']}_master_1080p.mp4"
        print(f"Producing master vertical short: {next_item['title']}...")
        master_video_path = await FlowMasterEngine.build_master_video(
            scenes=next_item["scenes"],
            output_filename=output_name,
            ambient_sfx="tension_drone.wav"
        )

        if not master_video_path.exists():
            return {"success": False, "error": f"Failed to render master video at {master_video_path}"}

        # Step 1.5: Automated AI Video Quality Inspection Gate
        from src.quality.ai_video_inspector import AIVideoInspector
        qa_result = AIVideoInspector.evaluate_video(str(master_video_path))
        print(f"AI Quality Score: {qa_result.get('score')}/100 | Verdict: {qa_result.get('verdict')}")
        if qa_result.get("flags"):
            print("AI Inspector Flags:", qa_result.get("flags"))

        # Safety Gate: Default to private for creator preview if quality score is below threshold
        upload_privacy = "private" if qa_result.get("score", 0) < 90 else privacy_status

        # Step 2: Upload to YouTube Shorts
        print(f"Uploading to YouTube Shorts ({upload_privacy})...")
        upload_res = YouTubePublisher.upload_short_file(
            file_path=str(master_video_path),
            title=next_item["title"],
            description=next_item["description"],
            tags=next_item["tags"],
            privacy_status=upload_privacy
        )

        if upload_res.get("success"):
            cls.record_published_id(next_item["id"], upload_res["url"])
            return {
                "success": True,
                "title": next_item["title"],
                "video_id": upload_res.get("youtube_video_id"),
                "url": upload_res.get("url"),
                "file_path": str(master_video_path)
            }
        else:
            return {
                "success": False,
                "error": upload_res.get("error", "Unknown YouTube upload failure")
            }


if __name__ == "__main__":
    privacy = "public"
    if len(sys.argv) > 1 and sys.argv[1]:
        privacy = sys.argv[1]
    res = asyncio.run(DailyShortsPipeline.produce_and_publish_next_short(privacy_status=privacy))
    print("Daily Pipeline Result:", res)
    if not res.get("success"):
        sys.exit(1)
