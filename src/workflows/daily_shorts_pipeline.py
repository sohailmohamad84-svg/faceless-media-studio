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
        "description": "How did one single rudder angle trap 400 cargo ships and freeze $10 billion in world trade daily? Discover the terrifying physics of the Suez Canal megajams.\n\n\ud83d\udea2 Like & Subscribe for daily high-retention engineering & business documentaries!\n\n#shorts #suezcanal #engineering #megaprojects #maritime #history #logistics #facts",
        "tags": [
            "shorts",
            "suezcanal",
            "evergiven",
            "engineering",
            "megaprojects",
            "shipping",
            "documentary"
        ],
        "scenes": [
            {
                "input_video": "data/suez_assets/suez_clip_1.mp4",
                "is_clean": True,
                "narration_text": "Four hundred cargo ships were trapped in the desert. Not by pirates. By an invisible wall of sand.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.3
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_2.mp4",
                "is_clean": True,
                "narration_text": "A forty-knot wind struck the world's longest container ship, jamming its twenty-thousand-ton bow into solid clay.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_3.mp4",
                "is_clean": True,
                "narration_text": "Every single hour it remained stuck cost the global economy four hundred million dollars in frozen cargo.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_4.mp4",
                "is_clean": True,
                "narration_text": "Fourteen massive tugboats and thirty thousand tons of dredged silt fought against the Mediterranean tide.",
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.5,
                        "gain": 0.35
                    }
                ]
            },
            {
                "input_video": "data/suez_assets/suez_clip_5.mp4",
                "is_clean": True,
                "narration_text": "Six days later, a full moon super-tide lifted the monster free, proving the fragility of modern civilization.",
                "foley": [
                    {
                        "sfx": "ship_horn.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            }
        ]
    },
    {
        "id": "dubai_sinking_islands",
        "title": "The $100 Billion Sinking Islands of Dubai",
        "hook": "The artificial world archipelago that the ocean is slowly reclaiming.",
        "description": "Three hundred artificial islands built with 320 million cubic meters of sand. Why is Dubai's most ambitious megaproject slowly being swallowed back into the Persian Gulf?\n\n\ud83c\udfdd\ufe0f Like & Subscribe for daily high-retention engineering & business documentaries!\n\n#shorts #dubai #engineering #megaprojects #architecture #theworld #history #geopolitics",
        "tags": [
            "shorts",
            "dubai",
            "theworld",
            "megaprojects",
            "engineering",
            "architecture",
            "documentary"
        ],
        "scenes": [
            {
                "input_video": "data/dubai_assets/dubai_clip_1.mp4",
                "is_clean": True,
                "narration_text": "Three hundred artificial islands were carved into the ocean to look like the planet Earth.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_2.mp4",
                "is_clean": True,
                "narration_text": "Over three hundred million cubic meters of sand were dredged from the seabed to build paradise.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    },
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 1.0,
                        "gain": 0.35
                    }
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_3.mp4",
                "is_clean": True,
                "narration_text": "Then the financial crash hit. Construction froze, and the ocean currents began reclaiming the coastlines.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.5,
                        "gain": 0.35
                    },
                    {
                        "sfx": "dust_puff.wav",
                        "time_offset": 1.5,
                        "gain": 0.3
                    }
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_4.mp4",
                "is_clean": True,
                "narration_text": "Satellite tracking showed the islands slowly sinking and eroding back into the Persian Gulf.",
                "foley": [
                    {
                        "sfx": "radar_ping.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    },
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 1.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "input_video": "data/dubai_assets/dubai_clip_5.mp4",
                "is_clean": True,
                "narration_text": "Now, luxury developers are racing to fortify the sea walls before this hundred-billion-dollar wonder disappears.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    },
                    {
                        "sfx": "desert_wind.wav",
                        "time_offset": 1.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "japan_maglev_speed",
        "title": "The 375 MPH Train That Levitates on Superconductors",
        "hook": "Why Japan mastered 375 MPH levitating trains while Hyperloop collapsed.",
        "description": "Floating four inches above the track, Japan's L0 Series Maglev travels at half the speed of sound without wheels. How did Japanese engineers conquer gravity using liquid helium cryogenics while Silicon Valley burned billions on failed vacuum tubes?\n\n\ud83d\ude84 Like & Subscribe for daily high-retention engineering & megaproject documentaries!\n\n#shorts #maglev #bullettrain #engineering #japan #hyperloop #technology #speed #physics #megaprojects",
        "tags": [
            "shorts",
            "maglev",
            "bullettrain",
            "engineering",
            "japan",
            "hyperloop",
            "technology",
            "documentary",
            "physics",
            "trains"
        ],
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
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
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
                    {
                        "sfx": "desert_wind.wav",
                        "time_offset": 0.2,
                        "gain": 0.25
                    }
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
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
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
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
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
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
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
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
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
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
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
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.45
                    }
                ]
            }
        ]
    },
    {
        "id": "concorde_sonic_tragedy",
        "title": "Why You Can't Fly Supersonic Anymore",
        "hook": "How a single piece of runway titanium destroyed the world's fastest passenger airliner.",
        "description": "Concorde flew from New York to London in under three hours at Mach 2. Why did commercial aviation become 40% slower after 2003?\n\n\u2708\ufe0f Like & Subscribe for daily high-retention engineering & business documentaries!\n\n#shorts #concorde #aviation #engineering #planes #history #supersonic #travel #speed",
        "tags": [
            "shorts",
            "concorde",
            "aviation",
            "engineering",
            "planes",
            "history",
            "supersonic",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Mach 2 Ground Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Cinematic low-angle ground tracking shot of Concorde supersonic airliner thundering down runway at sunset, four Rolls-Royce Olympus 593 turbojets blasting blazing orange afterburner shock diamonds, tarmac rippling with atmospheric heat distortion, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_1.mp4",
                "is_clean": True,
                "narration_text": "In nineteen-ninety-six, you could board a plane in London and land in New York before the local time you took off. Today, commercial aviation is forty percent slower than it was fifty years ago.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "3D Satellite Atlantic Flyover",
                "graphic_type": "3D_SATELLITE_CARTOGRAPHY",
                "prompt": "Cinematic 3D satellite digital elevation model flyover over the deep blue North Atlantic Ocean, glowing neon cyan supersonic flight corridor cutting from London Heathrow to New York JFK through atmospheric cloud layers, dramatic orbital push-in, photorealistic 8k vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_2.mp4",
                "is_clean": True,
                "narration_text": "Cruising at sixty thousand feet on the edge of space, passengers could see the curvature of the Earth while crossing the Atlantic at thirteen hundred miles an hour. London to Manhattan in just two hours and fifty-two minutes.",
                "foley": [
                    {
                        "sfx": "desert_wind.wav",
                        "time_offset": 0.2,
                        "gain": 0.25
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "3D Architectural Engine Cutaway",
                "graphic_type": "ARCHITECTURAL_CUTAWAY_CROSS_SECTION",
                "prompt": "Architectural 3D cutaway cross-section of Concorde delta wing and Olympus afterburner engine nacelle, transparent titanium skin revealing internal fuel trim transfer tanks and roaring white-hot afterburner combustion, technical engineering diagram with glowing heat flux lines, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_3.mp4",
                "is_clean": True,
                "narration_text": "The engineering was insane. Atmospheric friction heated the titanium nose to over two hundred and sixty degrees, stretching the airplane eight inches in flight. Engineers had to pump fuel through the wings just to cool the airframe.",
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "The Runway Debris Catalyst",
                "graphic_type": "MACRO_FORENSIC_TRACKING",
                "prompt": "Macro dramatic slow-motion tracking shot along the cracked asphalt of Paris Charles de Gaulle runway, a sharp 16-inch titanium wear strip resting on tarmac, intense atmospheric summer heat waves, cinematic documentary lighting, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_4.mp4",
                "is_clean": True,
                "narration_text": "Then on July twenty-fifth, two thousand, a tiny strip of titanium fell from a preceding DC-ten onto the runway at Paris. Minutes later, Concorde hit it at two hundred miles an hour.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "Hydrodynamic Shockwave Explosion",
                "graphic_type": "3D_TECHNICAL_SCHEMATIC",
                "prompt": "3D scientific forensic animation of high-speed aircraft tire violently disintegrating on runway, dense rubber chunk blasting against the underside of an aluminum delta wing fuel tank, sending a massive internal hydrodynamic pressure wave rupturing the fuel cell from within, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_5.mp4",
                "is_clean": True,
                "narration_text": "The debris did not puncture the tank. The sheer shockwave forced the fuel inside to burst the tank outward from within. Leaking kerosene ignited on the afterburners, engulfing the left wing in a fifty-foot plume of fire.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Cockpit Telemetry at Critical Altitude",
                "graphic_type": "FIRST_PERSON_TELEMETRY",
                "prompt": "High-tension cinematic cockpit point-of-view looking out Concorde visor windshield over Paris outskirts, pilots hands gripping flight controls, glowing red master warning alarms flashing, digital flight deck telemetry showing speed decay and flameout warnings, photorealistic documentary, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_6.mp4",
                "is_clean": True,
                "narration_text": "With two engines destroyed and the landing gear jammed, Captain Christian Marty fought for control. Two minutes after takeoff, Flight forty-five-ninety stalled and crashed into a hotel, killing one hundred and thirteen people.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Sonic Boom Shockwave & Economic Reality",
                "graphic_type": "AERODYNAMIC_PHYSICS_VISUALIZATION",
                "prompt": "Cinematic aerial shot of Concorde piercing the sound barrier over open ocean, visible physical conical vapor shockwave cone wrapping around the supersonic delta wings, sonic boom pressure waves rippling across the water, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_7.mp4",
                "is_clean": True,
                "narration_text": "Yet the tragedy was not why Concorde died. Flying supersonic created sonic booms that rattled windows on the ground, triggering bans across ninety percent of the world. It burned one ton of fuel per passenger, making tickets cost twelve thousand dollars.",
                "foley": [
                    {
                        "sfx": "thunder_strike.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Aviation Museum Finish & Call to Action",
                "graphic_type": "EPIC_CINEMATIC_FINISH",
                "prompt": "Cinematic wide shot of Concorde parked inside a modern aviation museum hangar, shafts of golden morning volumetric sunlight illuminating the pristine white delta wings and drooping nose, visitors admiring from below, epic cinematic documentary finish, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/concorde_scene_8.mp4",
                "is_clean": True,
                "narration_text": "In two thousand and three, Concorde flew its final flight. For the first time in modern history, civilization abandoned a faster technology. Would you pay twelve thousand dollars to fly supersonic today? Subscribe for daily engineering megaprojects, and tell us in the comments.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.45
                    }
                ]
            }
        ]
    },
    {
        "id": "singapore_sand_empire",
        "title": "The Secret Ocean War for Singapore's Sand #shorts",
        "category": "Geopolitics & Megaprojects",
        "hook": "How a tiny island nation grew twenty-five percent bigger using smuggled seabed sand.",
        "description": "Singapore has expanded its land area by over 25% since 1965, importing over 500 million tons of sand. How did environmental bans, disappearing sand cays in Indonesia, Dutch-style polders, and the engineering of Tuas Port reshape Southeast Asia?\n\n\ud83c\udfdd\ufe0f Like & Subscribe for daily high-retention engineering & geopolitical documentaries!\n\n#shorts #singapore #megaprojects #geopolitics #engineering #landreclamation #facts #ocean",
        "tags": [
            "shorts",
            "singapore",
            "megaprojects",
            "geopolitics",
            "engineering",
            "landreclamation",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The High-Altitude Expansion Hook",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "Cinematic high-altitude 3D satellite timelapse zooming into Singapore island, shoreline visibly glowing and pushing outward into the ocean in pulsing neon blue, hyperrealistic cartography, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_1.mp4",
                "narration_text": "Singapore is twenty-five percent larger today than when it gained independence in nineteen-sixty-five.",
                "subtitle_phrases": [
                    "Singapore is {\c&H0020FFFF&}25% larger{\c&H00FFFFFF&} today",
                    "than when it gained independence in {\c&H0020FFFF&}1965{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Mega Dredger Suction",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Massive cutter-suction dredging ship in choppy turquoise ocean waters pumping hundreds of tons of seabed sand through roaring steel pipes onto artificial shoreline, dramatic low angle, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_2.mp4",
                "narration_text": "To construct modern skyscrapers and ports, Singapore imported over five hundred million tons of ocean sand, becoming the world's largest sand importer per capita.",
                "subtitle_phrases": [
                    "To construct modern skyscrapers and ports,",
                    "Singapore imported over {\c&H0020FFFF&}500 million tons{\c&H00FFFFFF&} of sand,",
                    "becoming the world's {\c&H0020FFFF&}largest sand importer{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "Regional Black Market Cartography",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D satellite radar map tracking illicit marine cargo vessels moving secretly between Indonesia, Malaysia, and Singapore at night, glowing AIS transponder paths, photorealistic military cartography, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_3.mp4",
                "narration_text": "When regional bans halted legal supplies, an illicit dredging black market devastated ecosystems, causing up to two dozen small Indonesian islets and sand cays to submerge below the tides.",
                "subtitle_phrases": [
                    "When regional bans halted legal supplies,",
                    "an illicit dredging {\c&H0020FFFF&}black market{\c&H00FFFFFF&} devastated ecosystems,",
                    "causing up to {\c&H0020FFFF&}two dozen Indonesian islets{\c&H00FFFFFF&}",
                    "to submerge below the tides."
                ],
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Architectural Polder Dike Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "Forensic 3D cross-section cutaway animation of a concrete polder sea wall holding back deep ocean water, drainage pumps flushing sea water below sea level, blueprint lines, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_4.mp4",
                "narration_text": "To diversify beyond imported sand, Singapore pioneered massive Dutch-style polders, sealing ocean basins with reinforced dikes to reclaim land below sea level.",
                "subtitle_phrases": [
                    "To diversify beyond imported sand,",
                    "Singapore pioneered massive {\c&H0020FFFF&}Dutch-style polders{\c&H00FFFFFF&},",
                    "sealing ocean basins with {\c&H0020FFFF&}reinforced dikes{\c&H00FFFFFF&}",
                    "to reclaim land below sea level."
                ],
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "Soil Settlement Physics Simulation",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "3D geological soil cutaway simulation showing underwater vertical prefab drains driving hundreds of feet into marine clay, compressing saturated seabed into solid rock foundations, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_5.mp4",
                "narration_text": "Miles of prefabricated vertical drains accelerate water expulsion from deep marine clay under massive surcharge weight, consolidating unstable seabed silt into solid ground foundations.",
                "subtitle_phrases": [
                    "Miles of {\c&H0020FFFF&}prefabricated vertical drains{\c&H00FFFFFF&}",
                    "accelerate water expulsion from deep marine clay",
                    "under massive {\c&H0020FFFF&}surcharge weight{\c&H00FFFFFF&},",
                    "consolidating unstable seabed silt",
                    "into {\c&H0020FFFF&}solid ground foundations{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.2,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Tuas Mega Port Drone Push",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Dramatic sunset drone hyperlapse over Tuas Mega Port, automated automated cranes lifting thousands of containers onto newly reclaimed tarmac stretching into horizon, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_6.mp4",
                "narration_text": "The result is Tuas Mega Port: planned to become the world's largest automated container terminal upon completion in the 2040s, with Phase One already operational on reclaimed land.",
                "subtitle_phrases": [
                    "The result is {\c&H0020FFFF&}Tuas Mega Port{\c&H00FFFFFF&}:",
                    "planned to become the world's {\c&H0020FFFF&}largest automated terminal{\c&H00FFFFFF&}",
                    "upon completion in the {\c&H0020FFFF&}2040s{\c&H00FFFFFF&},",
                    "with Phase One already operational."
                ],
                "foley": [
                    {
                        "sfx": "ship_horn.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Rising Sea Levels Defense Matrix",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Futuristic seawall fortress bracing against surging ocean storm waves with glowing telemetry meters indicating four-meter height buffers, photorealistic, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_7.mp4",
                "narration_text": "With sea levels projected to rise, newly reclaimed land is mandated to sit at least four to five meters above Singapore Height Datum, creating an existential coastal fortress against the sea.",
                "subtitle_phrases": [
                    "With sea levels projected to rise,",
                    "newly reclaimed land is mandated",
                    "to sit at least {\c&H0020FFFF&}4 to 5 meters above SHD{\c&H00FFFFFF&},",
                    "creating an {\c&H0020FFFF&}existential coastal fortress{\c&H00FFFFFF&} against the sea."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Golden Marina Bay Finish & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Breathtaking twilight pan over Singapore Marina Bay skyline with glowing supertrees and financial towers reflecting on calm bay water, cinematic golden volumetric lighting, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/singapore_scene_8.mp4",
                "narration_text": "Could other vulnerable coastal nations engineer their way out of rising seas? Subscribe and leave your perspective in the comments.",
                "subtitle_phrases": [
                    "Could other vulnerable coastal nations",
                    "{\c&H0020FFFF&}engineer their way out{\c&H00FFFFFF&} of rising seas?",
                    "Subscribe and leave your perspective in the comments."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "three_gorges_rotation",
        "title": "The Monster Dam That Slowed Earth's Rotation #shorts",
        "category": "Extreme Megastructures",
        "hook": "Holding 39 trillion kilograms of water, this dam altered the physical rotation of planet Earth.",
        "description": "China's Three Gorges Dam holds 39 trillion kilograms of water 175 meters above sea level. NASA confirmed it literally lengthened the 24-hour day. How does concrete conquer planetary physics?\n\n\u26a1 Like & Subscribe for daily high-retention engineering & physics documentaries!\n\n#shorts #threegorgesdam #engineering #physics #earth #megastructures #nasa #science",
        "tags": [
            "shorts",
            "threegorgesdam",
            "engineering",
            "physics",
            "earth",
            "megastructures",
            "nasa",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Massive Spillway Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Low-angle cinematic drone shot facing the colossal concrete wall of Three Gorges Dam with massive floodgates blasting violent roaring white water into the gorge, heavy mist and rainbow distortion, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_1.mp4",
                "narration_text": "Sitting across the Yangtze River is a concrete monster so heavy that it physically changed the rotation of planet Earth.",
                "subtitle_phrases": [
                    "Sitting across the {\c&H0020FFFF&}Yangtze River{\c&H00FFFFFF&}",
                    "is a {\c&H0020FFFF&}concrete monster{\c&H00FFFFFF&} so heavy",
                    "that it physically changed the {\c&H0020FFFF&}rotation of planet Earth{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Planetary Physics & Moment of Inertia",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D holographic view of planet Earth spinning in deep space, glowing vector lines showing Earth's rotational axis shifting slightly as a glowing red mass concentrates in central China, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_2.mp4",
                "narration_text": "NASA geophysicists calculated that raising thirty-nine trillion kilograms of water one hundred and seventy-five meters increased Earth's moment of inertia.",
                "subtitle_phrases": [
                    "NASA geophysicists calculated that raising",
                    "{\c&H0020FFFF&}39 trillion kilograms{\c&H00FFFFFF&} of water",
                    "{\c&H0020FFFF&}175 meters{\c&H00FFFFFF&} above sea level",
                    "increased Earth's {\c&H0020FFFF&}moment of inertia{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "Spinning Figure Skater Analogy",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Visual split simulation comparing a spinning figure skater extending arms to a spinning globe elevating billions of tons of water away from its core, motion vectors, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_3.mp4",
                "narration_text": "Just like a spinning ice skater slowing down when they stretch out their arms, raising water against gravity slowed Earth's daily spin by zero point zero six microseconds.",
                "subtitle_phrases": [
                    "Just like a spinning ice skater slowing down",
                    "when they {\c&H0020FFFF&}stretch out their arms{\c&H00FFFFFF&},",
                    "raising water against gravity",
                    "slowed Earth's daily spin by {\c&H0020FFFF&}0.06 microseconds{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "3D Internal Turbine Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D architectural cross-section cutaway deep inside the dam wall revealing thirty-two colossal Francis hydro-turbines spinning in roaring high-pressure water, glowing copper magnetic coils, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_4.mp4",
                "narration_text": "Beneath the reservoir, thirty-two colossal hydro-turbines produce twenty-two thousand five hundred megawatts: enough electricity to power entire nations.",
                "subtitle_phrases": [
                    "Beneath the reservoir,",
                    "{\c&H0020FFFF&}32 colossal hydro-turbines{\c&H00FFFFFF&}",
                    "produce {\c&H0020FFFF&}22,500 megawatts{\c&H00FFFFFF&}:",
                    "enough electricity to {\c&H0020FFFF&}power entire nations{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "Ship Elevator Engineering Marvel",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Macro tracking shot of the world's largest vertical ship lift, raising a 3,000-ton container barge 370 feet straight up inside a steel elevator shaft on massive counterweight cables, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_5.mp4",
                "narration_text": "To bypass the four-hundred-foot wall, engineers built a three-thousand-ton vertical ship elevator that hoists entire cargo freighters in forty minutes.",
                "subtitle_phrases": [
                    "To bypass the 400-foot wall,",
                    "engineers built a {\c&H0020FFFF&}3,000-ton ship elevator{\c&H00FFFFFF&}",
                    "that hoists entire cargo freighters",
                    "in just {\c&H0020FFFF&}40 minutes{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Seismic Stress & Crustal Fault Lines",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "3D geological fault line simulation showing immense tectonic pressure underneath the reservoir bed with micro-fractures glowing red in continental crust rock, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_6.mp4",
                "narration_text": "The weight is so immense that geologists monitor tectonic fault lines beneath the reservoir, where reservoir-induced seismicity triggers thousands of micro-tremors.",
                "subtitle_phrases": [
                    "The weight is so immense that geologists monitor",
                    "{\c&H0020FFFF&}tectonic fault lines{\c&H00FFFFFF&} beneath the reservoir,",
                    "where {\c&H0020FFFF&}reservoir-induced seismicity{\c&H00FFFFFF&}",
                    "triggers thousands of {\c&H0020FFFF&}micro-tremors{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Flood Defense Shockwave",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "High-speed tracking shot of rushing monsoon flood currents crashing into reinforced concrete dissipation baffles, water exploding into towering spray, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_7.mp4",
                "narration_text": "Built to tame floods that previously killed three hundred thousand people, it absorbs the full force of five-hundred-year Pacific superstorms.",
                "subtitle_phrases": [
                    "Built to tame floods that historically",
                    "killed over {\c&H0020FFFF&}300,000 people{\c&H00FFFFFF&},",
                    "it absorbs the full force",
                    "of {\c&H0020FFFF&}500-year Pacific superstorms{\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.3,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Golden Dam Crest Panorama & CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Stunning golden hour panoramic drone shot rising over the crest of the dam, calm mountain reservoir stretching hundreds of miles into misty limestone peaks, warm sunlight, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/threegorges_scene_8.mp4",
                "narration_text": "Is altering planetary mechanics worth clean energy? Hit subscribe and let us know your verdict below.",
                "subtitle_phrases": [
                    "Is {\c&H0020FFFF&}altering planetary mechanics{\c&H00FFFFFF&}",
                    "worth clean energy?",
                    "Hit {\c&H0020FFFF&}Subscribe{\c&H00FFFFFF&} and share your verdict below."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "sr71_blackbird_unstart",
        "title": "The Jet That Choked at Mach 3.2: The SR-71 Unstart #shorts",
        "category": "Aviation & Speed",
        "hook": "A one-millimeter shockwave misplacement slammed this Mach 3 spy plane sideways in mid-air.",
        "description": "At 2,200 MPH, the SR-71 Blackbird relied on moving spike cones to keep engines alive. What happens when supersonic air chokes a jet engine in fifty milliseconds?\n\n\u2708\ufe0f Like & Subscribe for daily high-retention aviation & physics documentaries!\n\n#shorts #sr71 #blackbird #aviation #planes #mach3 #engineering #supersonic #military",
        "tags": [
            "shorts",
            "sr71",
            "blackbird",
            "aviation",
            "planes",
            "mach3",
            "engineering",
            "supersonic",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Stratospheric Cruise Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Cinematic low tracking shot of SR-71 Blackbird cruising at 85,000 feet in upper stratosphere against black sky and curved blue Earth horizon, twin canted vertical fins, Pratt and Whitney J58 engines roaring with blue-orange afterburner shock diamonds, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_1.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "ALT: 85,000 FT // SPD: MACH 3.20 // REGIME: STRATOSPHERE // AIR TEMP: -60°C",
                "narration_text": "Cruising at eighty-five thousand feet at Mach three point two, the airframe faces extreme stress. Here, a shockwave shifting one millimeter can choke the engines in milliseconds.",
                "subtitle_phrases": [
                    "Cruising at {\\c&H00D7FF&}85,000 feet{\\c&HFFFFFF&}",
                    "at {\\c&H00D7FF&}Mach 3.2{\\c&HFFFFFF&}, the airframe",
                    "faces {\\c&H00D7FF&}extreme stress{\\c&HFFFFFF&}.",
                    "A shockwave shifting {\\c&H00D7FF&}1 millimeter{\\c&HFFFFFF&}",
                    "chokes the engines {\\c&H00D7FF&}in milliseconds{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "desert_wind.wav",
                        "time_offset": 0.0,
                        "gain": 0.15
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "3D Moveable Spike Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D cross-section animation of the SR-71 inlet cone spike moving back twenty-six inches inside nacelle, trapping conical shockwaves at supersonic speeds, slowing airflow to subsonic Mach 0.5, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_2.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "INLET GEOMETRY // SPIKE TRANSLATION: -26 INCHES // SUBSONIC DIFFUSION",
                "narration_text": "At Mach three, fuel cannot burn in supersonic air. The intake spike retracts twenty-six inches inside the cowl, slowing twenty-two hundred mile-per-hour air to subsonic speeds.",
                "subtitle_phrases": [
                    "At {\\c&H00D7FF&}Mach 3{\\c&HFFFFFF&}, fuel cannot",
                    "burn in {\\c&H00D7FF&}supersonic air{\\c&HFFFFFF&}.",
                    "The intake spike {\\c&H00D7FF&}retracts 26 inches{\\c&HFFFFFF&},",
                    "slowing {\\c&H00D7FF&}2,200 mph air{\\c&HFFFFFF&}",
                    "down to {\\c&H00D7FF&}subsonic speeds{\\c&HFFFFFF&}."
                ],
                "foley": []
            },
            {
                "scene_num": 3,
                "title": "Forensic Shockwave Expulsion",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Forensic aerodynamic simulation of a terminal normal shockwave expelled forward out of the intake cowl in violent condensation collar and shock vortices, zero fireball explosion, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_3.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "WARNING: NORMAL SHOCK EXPULSION // INLET UNSTART // DELTA-T: 50MS",
                "narration_text": "If internal shockwave balance fails, the engine chokes. In fifty milliseconds, the terminal normal shock is violently expelled forward out the cowl in an aerodynamic unstart.",
                "subtitle_phrases": [
                    "If shockwave balance fails,",
                    "the engine {\\c&H00D7FF&}instantly chokes{\\c&HFFFFFF&}.",
                    "In {\\c&H00D7FF&}50 milliseconds{\\c&HFFFFFF&}, the terminal shock",
                    "is {\\c&H00D7FF&}expelled forward{\\c&HFFFFFF&} out the cowl",
                    "in an {\\c&H00D7FF&}aerodynamic unstart{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "shockwave_unstart_blast.wav",
                        "time_offset": 3.0,
                        "gain": 0.40
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Cockpit Violent Yaw Telemetry",
                "graphic_type": "COCKPIT_TELEMETRY",
                "prompt": "Visor POV inside SR-71 cockpit during severe violent yaw jerk, pilot in white David Clark pressure suit and gold visor slamming toward canopy, analog dials vibrating with red warning lights, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_4.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "ASYMMETRIC THRUST // YAW ACCELERATION: +3.8G // HELMET CANOPY IMPACT",
                "narration_text": "Losing all thrust on one side, the aircraft whips violently sideways, slamming the pilot against the canopy with enough yaw force to crack flight helmets.",
                "subtitle_phrases": [
                    "Losing all thrust {\\c&H00D7FF&}on one side{\\c&HFFFFFF&},",
                    "the aircraft {\\c&H00D7FF&}whips violently sideways{\\c&HFFFFFF&},",
                    "slamming the pilot {\\c&H00D7FF&}against the canopy{\\c&HFFFFFF&}",
                    "with enough {\\c&H00D7FF&}yaw acceleration{\\c&HFFFFFF&}",
                    "to {\\c&H00D7FF&}crack flight helmets{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.5,
                        "gain": 0.20
                    },
                    {
                        "sfx": "metal_stress_creak.wav",
                        "time_offset": 1.5,
                        "gain": 0.30
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "J58 Turbo-Ramjet Transition Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D mechanical cutaway of the Pratt and Whitney J58 engine showing bypass bleed pipes redirecting compressor air straight into the afterburner like a pure ramjet, glowing orange heat, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_5.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "J58 TURBO-RAMJET // BYPASS BLEED: ACTIVE // INLET DIFFUSER: 80% THRUST",
                "narration_text": "The J-fifty-eight was a hybrid turbo-ramjet. At Mach three, bypass bleed pipes converted it to a ramjet, with the inlet diffuser producing eighty percent of total thrust.",
                "subtitle_phrases": [
                    "The {\\c&H00D7FF&}J58{\\c&HFFFFFF&} was a hybrid turbo-ramjet.",
                    "At {\\c&H00D7FF&}Mach 3{\\c&HFFFFFF&}, bypass bleed pipes",
                    "converted it {\\c&H00D7FF&}into a ramjet{\\c&HFFFFFF&},",
                    "with the intake diffuser {\\c&H00D7FF&}producing 80%{\\c&HFFFFFF&}",
                    "of its {\\c&H00D7FF&}total forward thrust{\\c&HFFFFFF&}."
                ],
                "foley": []
            },
            {
                "scene_num": 6,
                "title": "Titanium Skin Heat Expansion",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Macro tracking shot of the Blackbird's titanium fuselage skin at 600 degrees Fahrenheit, corrugated panels expanding to seal loose fuel joints, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_6.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "AERODYNAMIC HEATING // TITANIUM EXPANSION // SKIN TEMP: 620°F",
                "narration_text": "Atmospheric friction heated the titanium skin past six hundred degrees. The airframe expanded several inches in flight, sealing fuel joints that leaked on the ground.",
                "subtitle_phrases": [
                    "Atmospheric friction heated",
                    "the titanium skin {\\c&H00D7FF&}past 600°F{\\c&HFFFFFF&}.",
                    "The airframe {\\c&H00D7FF&}expanded several inches{\\c&HFFFFFF&},",
                    "sealing fuel joints",
                    "that {\\c&H00D7FF&}leaked on the ground{\\c&HFFFFFF&}."
                ],
                "foley": []
            },
            {
                "scene_num": 7,
                "title": "Missile Evading Speed Climb",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "SR-71 pitching up into an aggressive supersonic climb leaving twin Mach diamonds across the upper stratosphere as surface-to-air missiles detonate miles below in harmless clouds, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_7.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "SAM RADAR LOCK DETECTED // DEFENSE: ACCELERATING // LOSSES: ZERO",
                "narration_text": "Over four thousand anti-aircraft missiles were fired at the Blackbird. Not a single SR-seventy-one was ever hit: its standard defense was simply accelerating away.",
                "subtitle_phrases": [
                    "Over {\\c&H00D7FF&}4,000 missiles{\\c&HFFFFFF&} were fired",
                    "at the Blackbird {\\c&H00D7FF&}during its service{\\c&HFFFFFF&}.",
                    "Not a single {\\c&H00D7FF&}SR-71 was ever hit{\\c&HFFFFFF&}:",
                    "its standard defense",
                    "was {\\c&H00D7FF&}simply accelerating away{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "thunder_strike.wav",
                        "time_offset": 2.0,
                        "gain": 0.25
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Hangar Golden Finish & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Pristine aviation museum display with SR-71 Blackbird under dramatic golden spotlighting, sleek black stealth curves reflecting volumetric sunbeams, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/sr71_flow_scene_8.mp4",
                "duration": 11.50,
                "voice_rate": "+16%",
                "hud_telemetry": "SKUNK WORKS ARCHIVE // LOCKHEED SR-71 // HYPERSONIC LEGACY",
                "narration_text": "Could modern hypersonic drones ever match the physical genius of the SR-seventy-one Blackbird? Subscribe and leave your thoughts below.",
                "subtitle_phrases": [
                    "Could modern {\\c&H00D7FF&}hypersonic drones{\\c&HFFFFFF&}",
                    "ever match the {\\c&H00D7FF&}physical genius{\\c&HFFFFFF&}",
                    "of the {\\c&H00D7FF&}SR-71 Blackbird{\\c&HFFFFFF&}?",
                    "Subscribe and {\\c&H00D7FF&}leave your thoughts below{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "chime.wav",
                        "time_offset": 8.0,
                        "gain": 0.20
                    }
                ]
            }
        ]
    },
    {
        "id": "taipei_101_damper",
        "title": "The 660-Ton Steel Sphere That Stabilizes Taipei 101 #shorts",
        "category": "Extreme Engineering",
        "hook": "Suspended on the 92nd floor, this giant golden pendulum slashes skyscraper sway by 40% and absorbs violent harmonic resonance.",
        "description": "During Category 5 typhoons and magnitude 7.4 earthquakes, Taipei 101 sways violently. How does a 660-tonne suspended steel sphere slash building sway by 40% while 380 bedrock megacolumns prevent structural collapse? Discover the genius physics of tuned mass dampers.\n\n🏙️ Like & Subscribe for daily high-retention engineering & architecture documentaries!\n\n#shorts #taipei101 #engineering #architecture #physics #skyscrapers #earthquake #taiwan",
        "tags": [
            "shorts",
            "taipei101",
            "engineering",
            "architecture",
            "physics",
            "skyscrapers",
            "earthquake",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Typhoon Sway Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Low-angle dramatic shot of Taipei 101 skyscraper standing in a raging night typhoon with blinding rain sheets and swaying slightly against howling 150 MPH wind gusts, neon skyscraper lighting, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_1.mp4",
                "narration_text": "Standing sixteen hundred feet over an active subduction zone, this skyscraper faces violent typhoon winds and catastrophic earthquakes.",
                "subtitle_phrases": [
                    "Standing 1,600 feet over an active fault line,",
                    "this skyscraper faces {\\c&H0020FFFF&}violent typhoon winds{\\c&H00FFFFFF&}",
                    "and {\\c&H0020FFFF&}catastrophic earthquakes{\\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Golden Pendulum Reveal",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "Camera sweeping around a colossal 18-foot golden steel sphere suspended by eight massive woven steel cables inside the 92nd floor atrium of Taipei 101, dramatic museum lighting, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_2.mp4",
                "narration_text": "Suspended between the eighty-seventh and ninety-second floors is a six-hundred-and-sixty-ton golden steel tuned mass damper.",
                "subtitle_phrases": [
                    "Suspended between the {\\c&H0020FFFF&}87th and 92nd floors{\\c&H00FFFFFF&}",
                    "is a {\\c&H0020FFFF&}660-ton golden steel{\\c&H00FFFFFF&}",
                    "tuned mass damper."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "Counter-Oscillation Physics Simulation",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Forensic architectural 3D simulation showing Taipei 101 swaying to the left while the golden pendulum sways forcefully to the right, glowing force vector arrows canceling harmonic resonance, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_3.mp4",
                "narration_text": "When fierce typhoon winds push the top of the tower left, inertia keeps the sphere moving right: canceling out forty percent of the building's sway.",
                "subtitle_phrases": [
                    "When typhoon winds push the tower left,",
                    "inertia forces the sphere {\\c&H0020FFFF&}to swing right{\\c&H00FFFFFF&}:",
                    "canceling out {\\c&H0020FFFF&}40% of sway{\\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Hydraulic Shock Absorbers Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D cutaway of eight massive high-pressure hydraulic shock cylinders connected to the bottom of the steel sphere compressing glowing red fluid, dampening kinetic energy, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_4.mp4",
                "narration_text": "Underneath the sphere, eight high-pressure hydraulic dampers absorb millions of foot-pounds of kinetic energy, converting violent motion into heat.",
                "subtitle_phrases": [
                    "Beneath the sphere, {\\c&H0020FFFF&}8 hydraulic dampers{\\c&H00FFFFFF&}",
                    "absorb millions of foot-pounds of energy,",
                    "converting violent motion {\\c&H0020FFFF&}into heat{\\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "Deep Bedrock Foundation Piles",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D cross-section traveling 260 feet beneath city streets showing 380 reinforced concrete foundation piles anchored directly into solid bedrock, steel rebar framework glowing, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_5.mp4",
                "narration_text": "Deep beneath the street, three hundred and eighty steel-reinforced concrete columns sink two hundred and sixty feet into solid bedrock, anchoring the spine.",
                "subtitle_phrases": [
                    "Deep beneath the city street,",
                    "{\\c&H0020FFFF&}380 concrete columns{\\c&H00FFFFFF&} sink 260 feet into bedrock,",
                    "anchoring the {\\c&H0020FFFF&}structural spine{\\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "7.4 Magnitude Earthquake Test",
                "graphic_type": "COCKPIT_TELEMETRY",
                "prompt": "Real-time engineering telemetry overlay showing seismic P-waves shaking building columns during an earthquake while the pendulum swings in a controlled 100cm arc, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_6.mp4",
                "narration_text": "During Taiwan's magnitude seven point four earthquake, the damper swung nearly three feet, absorbing destructive harmonic waves and controlling sway.",
                "subtitle_phrases": [
                    "During Taiwan's {\\c&H0020FFFF&}magnitude 7.4 earthquake{\\c&H00FFFFFF&},",
                    "the damper swung {\\c&H0020FFFF&}nearly 3 feet{\\c&H00FFFFFF&},",
                    "absorbing destructive harmonic waves."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Bamboo Aerodynamic Stepped Facade",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Wind tunnel aerodynamic airflow visualization around Taipei 101's stepped pagoda bamboo modules, vortex shedding spiraling harmlessly off corner notches, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_7.mp4",
                "narration_text": "Inspired by native bamboo stalks, the building's eight tiered modules break up vortex shedding, slicing through typhoon winds instead of blocking them.",
                "subtitle_phrases": [
                    "Inspired by native {\\c&H0020FFFF&}bamboo stalks{\\c&H00FFFFFF&},",
                    "eight tiered modules break vortex shedding,",
                    "slicing through {\\c&H0020FFFF&}typhoon winds{\\c&H00FFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Golden Sunset Skyline & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Golden hour drone shot flying past the spire of Taipei 101 illuminated against a purple and orange sunset over Taipei basin, warm sunlight, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/taipei_scene_8.mp4",
                "narration_text": "Would you feel safe inside a skyscraper stabilized by a swinging sphere? Subscribe and share your thoughts below.",
                "subtitle_phrases": [
                    "Would you feel safe inside a skyscraper",
                    "stabilized by a {\\c&H0020FFFF&}swinging sphere{\\c&H00FFFFFF&}?",
                    "Hit {\\c&H0020FFFF&}Subscribe{\\c&H00FFFFFF&} and tell us below."
                ],
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "gotthard_base_tunnel",
        "title": "The 35-Mile Granite Furnace Under the Alps #shorts",
        "category": "Underground Megaprojects",
        "hook": "Engineers drilled 57 kilometers under 7,500 feet of crushing granite where rock temperatures hit 115 degrees.",
        "description": "The Gotthard Base Tunnel is the longest and deepest rail tunnel ever built. How did 2,500 miners carve 28 million tons of rock under boiling geothermal heat?\n\n\ud83d\ude86 Like & Subscribe for daily high-retention engineering & mega-tunnel documentaries!\n\n#shorts #gotthard #tunnels #switzerland #alps #trains #engineering #megaprojects",
        "tags": [
            "shorts",
            "gotthard",
            "tunnels",
            "switzerland",
            "alps",
            "trains",
            "engineering",
            "megaprojects",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Deep Alpine Portal Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Cinematic low tracking shot of high-speed Swiss electric train shooting into massive concrete tunnel portal carved into sheer snowcapped Swiss Alps rockface at 155 MPH, motion blur, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_1.mp4",
                "duration": 9.40,
                "voice_rate": "+16%",
                "hud_telemetry": "PORTAL ERSTFELD // DEPTH: 7,500 FT // SPEED: 155 MPH // STATUS: ENTERING",
                "narration_text": "Buried beneath seven thousand five hundred feet of crushing alpine granite is the longest and deepest railway tunnel on Earth: Switzerland's thirty-five mile Gotthard Base Tunnel.",
                "subtitle_phrases": [
                    "Buried beneath {\\c&H00D7FF&}7,500 feet{\\c&HFFFFFF&}",
                    "of {\\c&H00D7FF&}crushing alpine granite{\\c&HFFFFFF&}",
                    "is the {\\c&H00D7FF&}longest and deepest{\\c&HFFFFFF&} railway tunnel on Earth:",
                    "Switzerland's {\\c&H00D7FF&}35-mile Gotthard Base Tunnel{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.30
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "3D Mountain Cross-Section DEM",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D geological cross-section cutting through the Swiss Alps showing the 57-kilometer Gotthard tunnel running flat through the base beneath massive peaks, glowing red depth indicators, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_2.mp4",
                "duration": 9.75,
                "voice_rate": "+16%",
                "hud_telemetry": "GEOLOGY // LENGTH: 57 KM (35 MI) // FORMATIONS: 80 ROCK TYPES // 17 YEARS",
                "narration_text": "Drilling thirty-five miles flat under the Alps required cutting through eighty distinct rock formations, battling pressurized subterranean water pockets for seventeen relentless years.",
                "subtitle_phrases": [
                    "Drilling {\\c&H00D7FF&}35 miles flat under the Alps{\\c&HFFFFFF&}",
                    "required cutting through {\\c&H00D7FF&}80 distinct rock formations{\\c&HFFFFFF&},",
                    "battling {\\c&H00D7FF&}pressurized water pockets{\\c&HFFFFFF&}",
                    "for {\\c&H00D7FF&}17 relentless years{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "radar_ping.wav",
                        "time_offset": 0.3,
                        "gain": 0.20
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "Colossal Tunnel Boring Machine",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Massive 400-meter-long Tunnel Boring Machine cutterhead grinding through solid granite rock under high pressure water jets, steel disc cutters throwing stone chips, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_3.mp4",
                "duration": 9.20,
                "voice_rate": "+16%",
                "hud_telemetry": "TBM HERRENKNECHT // HEAD: 9.5M // EXCAVATION: 28M TONS // 5X GIZA PYRAMIDS",
                "narration_text": "Four colossal four-hundred-meter tunnel boring machines chewed through twenty-eight million tons of rock, enough granite to rebuild the Great Pyramid of Giza five times over.",
                "subtitle_phrases": [
                    "Four colossal {\\c&H00D7FF&}400-meter TBMs{\\c&HFFFFFF&}",
                    "chewed through {\\c&H00D7FF&}28 million tons of rock{\\c&HFFFFFF&},",
                    "enough granite to rebuild the {\\c&H00D7FF&}Great Pyramid of Giza{\\c&HFFFFFF&}",
                    "{\\c&H00D7FF&}five times over{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.2,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "115 Degree Geothermal Furnace Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D cutaway showing the geothermal heat transfer from crushing mountain pressure heating tunnel rock walls to 115 degrees Fahrenheit, industrial ventilation pipes pumping ice water, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_4.mp4",
                "duration": 9.95,
                "voice_rate": "+16%",
                "hud_telemetry": "GEOTHERMAL HEAT // ROCK TEMP: 115°F (46°C) // VENTILATION: ICE REFRIGERATION",
                "narration_text": "Deep in the mountain core, geothermal heat pushed rock temperatures to a blistering one hundred and fifteen degrees Fahrenheit, requiring massive refrigeration plants to keep miners alive.",
                "subtitle_phrases": [
                    "Deep in the mountain core,",
                    "geothermal heat pushed rock temps to {\\c&H00D7FF&}115°F{\\c&HFFFFFF&},",
                    "requiring {\\c&H00D7FF&}massive refrigeration plants{\\c&HFFFFFF&}",
                    "just to keep miners alive."
                ],
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.3,
                        "gain": 0.30
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "Mountain Squeezing Pressure Simulation",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Forensic engineering animation of heavy hydraulic steel yielding rings deforming under millions of pounds of crushing rock pressure without collapsing, glowing stress vectors, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_5.mp4",
                "duration": 10.00,
                "voice_rate": "+16%",
                "hud_telemetry": "OVERBURDEN PRESSURE // ROCK SQUEEZE: 2.3 FT // STEEL YIELD RINGS: ABSORBING",
                "narration_text": "Under millions of pounds of overburden pressure, soft sedimentary rock squeezed inward by over two feet, forcing engineers to invent sliding steel rings that yield without collapsing.",
                "subtitle_phrases": [
                    "Under {\\c&H00D7FF&}millions of pounds of pressure{\\c&HFFFFFF&},",
                    "soft rock {\\c&H00D7FF&}squeezed inward by over 2 feet{\\c&HFFFFFF&},",
                    "forcing engineers to invent {\\c&H00D7FF&}sliding steel rings{\\c&HFFFFFF&}",
                    "that {\\c&H00D7FF&}yield without collapsing{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "metal_stress_creak.wav",
                        "time_offset": 0.3,
                        "gain": 0.30
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Laser Guided Precision Breakthrough",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Dramatic final breakthrough shot of the TBM cutterhead chewing through the last wall of rock, miners cheering as dust clears with laser alignment beam hitting exact center target, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_6.mp4",
                "duration": 8.70,
                "voice_rate": "+16%",
                "hud_telemetry": "HISTORIC BREAKTHROUGH // DISTANCE: 28 MILES // LASER DEVIATION: < 1.0 CM",
                "narration_text": "When cutterheads met from opposite sides of the Alps after drilling twenty-eight miles in pitch-black darkness, the laser alignment error was less than a single centimeter.",
                "subtitle_phrases": [
                    "When cutterheads met from {\\c&H00D7FF&}opposite sides of the Alps{\\c&HFFFFFF&}",
                    "after drilling {\\c&H00D7FF&}28 miles in pitch-black darkness{\\c&HFFFFFF&},",
                    "the laser alignment error was {\\c&H00D7FF&}less than a single centimeter{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Piston Effect Aerodynamic Shockwave",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Aerodynamic simulation of a 155 MPH passenger train shooting through the tunnel tube pushing a massive air piston shockwave into side ventilation pressure relief shafts, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_7.mp4",
                "duration": 9.10,
                "voice_rate": "+16%",
                "hud_telemetry": "AERODYNAMICS // TUBE SPEED: 155 MPH // AIR PISTON EFFECT // RELIEF DUCTS: OPEN",
                "narration_text": "Today, high-speed passenger trains blast through the twin tubes at one hundred and fifty-five miles per hour, compressing air ahead of them like a giant pneumatic piston.",
                "subtitle_phrases": [
                    "Today, high-speed trains blast through at {\\c&H00D7FF&}155 mph{\\c&HFFFFFF&},",
                    "compressing air ahead of them",
                    "like a {\\c&H00D7FF&}giant pneumatic piston{\\c&HFFFFFF&}."
                ],
                "foley": [
                    {
                        "sfx": "jet_engine_rumble.wav",
                        "time_offset": 0.2,
                        "gain": 0.25
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Emerging Into Alpine Sunlight & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Golden hour drone shot following high-speed train emerging from Gotthard south portal into lush sunlit Swiss valley with snow-capped peaks in background, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/gotthard_scene_8.mp4",
                "duration": 9.60,
                "voice_rate": "+16%",
                "hud_telemetry": "TRANS-ALPINE CORRIDOR // GOTTHARD BASE // DEPTH: 2,300M // WORLD RECORD",
                "narration_text": "Would you board a high-speed train traveling thirty-five miles through the burning core of the Alps? Subscribe for more extreme engineering, and let us know in the comments.",
                "subtitle_phrases": [
                    "Would you board a train traveling {\\c&H00D7FF&}35 miles{\\c&HFFFFFF&}",
                    "through the {\\c&H00D7FF&}burning core of the Alps{\\c&HFFFFFF&}?",
                    "{\\c&H00D7FF&}Subscribe{\\c&HFFFFFF&} for more extreme engineering,",
                    "and let us know in the comments."
                ],
                "foley": [
                    {
                        "sfx": "chime.wav",
                        "time_offset": 0.3,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "jakarta_sinking_seawall",
        "title": "The $40 Billion Wall to Save a Sinking City #shorts",
        "category": "Sinking Megacities",
        "hook": "Sinking ten inches every year, Jakarta is building an eagle-shaped sea wall in the open ocean.",
        "description": "Over forty percent of Jakarta is now below sea level. How does a developing mega-city spend $40 billion on the 'Great Garuda' offshore dike to prevent total drowning?\n\n\ud83c\udf0a Like & Subscribe for daily high-retention engineering & megaproject documentaries!\n\n#shorts #jakarta #indonesia #engineering #megaprojects #climate #seawall #cities",
        "tags": [
            "shorts",
            "jakarta",
            "indonesia",
            "engineering",
            "megaprojects",
            "climate",
            "seawall",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Submerged Street Hook",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Cinematic low tracking shot through a flooded Jakarta street where murky ocean water laps against second-story shop signs, concrete flood walls holding back dark sea, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_1.mp4",
                "narration_text": "Sinking ten inches every single year, this mega-city of ten million people is literally collapsing into the ocean.",
                "foley": []
            },
            {
                "scene_num": 2,
                "title": "3D Groundwater Subsidence Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D geological cross-section beneath Jakarta streets showing illegal deep water wells draining underground aquifers, porous soil layers collapsing like an empty sponge, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_2.mp4",
                "narration_text": "Because piped municipal water is scarce, millions of illegal deep wells suck water out of underground aquifers, causing the clay soil beneath the city to deflate like an empty sponge.",
                "foley": []
            },
            {
                "scene_num": 3,
                "title": "3D Satellite Elevation DEM",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D satellite elevation map over northern Jakarta showing dark blue contour lines sinking below zero-meter sea level, Java Sea towering behind reinforced dikes, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_3.mp4",
                "narration_text": "Today, over forty percent of north Jakarta lies below sea level, kept dry only by aging concrete sea walls that crack under monsoon storm surges.",
                "foley": []
            },
            {
                "scene_num": 4,
                "title": "The Great Garuda Sea Wall Blueprint",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "Holographic 3D blueprint animation of the 25-mile offshore 'Great Garuda' sea wall shaped like a mythical eagle spanning across Jakarta Bay, artificial barrier islands glowing in gold, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_4.mp4",
                "narration_text": "To stop the catastrophe, Indonesia launched the Great Garuda: a forty-billion-dollar, twenty-five-mile sea dike shaped like a mythical eagle spanning across the bay.",
                "foley": []
            },
            {
                "scene_num": 5,
                "title": "Heavy Rock Revetment Engineering",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Giant marine crane barges dumping multi-ton interlocking concrete tetrapods into roaring ocean waters along the perimeter of the offshore seawall, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_5.mp4",
                "narration_text": "Thousands of interlocking concrete tetrapods and rock armor are lowered into forty feet of open ocean to create a breakwater capable of withstanding category-four typhoons.",
                "foley": []
            },
            {
                "scene_num": 6,
                "title": "Moving the Capital into the Jungle",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D satellite push from sinking Jakarta over 800 miles across the Java Sea into the dense green rainforests of East Kalimantan where Nusantara smart city is being built, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_6.mp4",
                "narration_text": "Realizing engineering might only buy twenty years, the government made a historic decision: completely abandoning Jakarta and carving an entirely new capital city inside the Borneo jungle.",
                "foley": []
            },
            {
                "scene_num": 7,
                "title": "Sea Barrier Pumping Station",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Colossal high-volume Archimedes screw pumps discharging millions of gallons of trapped river water over the sea wall back into the open Java Sea, heavy spray, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_7.mp4",
                "narration_text": "Giant drainage pumping stations must continuously lift river floodwaters over the high dikes, burning massive electrical grids just to keep streets above water.",
                "foley": []
            },
            {
                "scene_num": 8,
                "title": "Golden Bay Sunset & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Sweeping golden hour drone shot looking out from the sea wall towards the Jakarta skyline reflecting on the glowing ocean, warm cinematic sunset, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/jakarta_scene_8.mp4",
                "narration_text": "Can megaprojects save coastal cities, or is moving inland the only real answer? Subscribe and share your thoughts below.",
                "foley": []
            }
        ]
    },
    {
        "id": "boeing_747_hump_secret",
        "title": "The Military Secret Behind the Boeing 747 Hump #shorts",
        "category": "Aviation History & Design",
        "hook": "Why does the Queen of the Skies have a second-story bump? It was never meant for luxury passenger lounges.",
        "description": "The iconic Boeing 747 cockpit hump changed commercial aviation forever. Why did Boeing engineers design it for military nose-loading cargo tanks?\n\n\u2708\ufe0f Like & Subscribe for daily high-retention aviation & engineering documentaries!\n\n#shorts #boeing747 #aviation #planes #history #engineering #boeing #cargo",
        "tags": [
            "shorts",
            "boeing747",
            "aviation",
            "planes",
            "history",
            "engineering",
            "boeing",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Iconic Silhouette Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Dramatic low-angle tracking shot of a Boeing 747-400 rotating off runway at sunset, four giant turbofan engines roaring with golden exhaust haze, distinctive upper deck hump catching warm light, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_1.mp4",
                "narration_text": "The Boeing seven-forty-seven is the most recognizable passenger airliner in human history. But its iconic cockpit hump was designed for a secret military reason.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Supersonic Obsolescence Fear",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Split screen comparing a sleek Concorde supersonic airliner slicing through Mach clouds to a widebody 747 subsonic airliner, glowing Mach numbers, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_2.mp4",
                "narration_text": "In the nineteen-sixties, Boeing engineers were convinced that supersonic jets like Concorde would make all subsonic passenger planes completely obsolete within ten years.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "3D Swing-Up Nose Cargo Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D architectural cutaway of the 747 nose swinging completely upward on massive hinges, allowing two semi-truck shipping containers to drive straight down the main cargo deck, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_3.mp4",
                "narration_text": "To keep the plane profitable once passengers abandoned it, they designed it as a freighter: placing the flight deck on the second floor so the entire nose could swing open on hinges.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Area Rule Aerodynamics",
                "graphic_type": "AERODYNAMIC_SHOCKWAVE",
                "prompt": "Wind tunnel aerodynamic visualization showing Whitcomb area-rule airflow smoothing around the 747 cockpit hump, air pressure streamlines curving without drag penalties, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_4.mp4",
                "narration_text": "Aerodynamicist Richard Whitcomb discovered that fairing the hump smoothly into the fuselage actually reduced transonic drag, making the massive jet faster and more fuel-efficient.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "The Incredible Boeing Everett Factory",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Colossal indoor drone tracking shot inside Boeing's Everett Factory, the largest building by volume in the world, with three 747 fuselages under construction under massive yellow bridge cranes, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_5.mp4",
                "narration_text": "Boeing staked the entire company's existence on the project, building the largest building by volume on Earth in Everett, Washington, just to assemble it.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Supersonic Failure & The 747 Triumph",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D global cartography showing sonic boom ban flight restrictions over land, forcing supersonic airliners off lucrative continental routes while 747s conquer global skies, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_6.mp4",
                "narration_text": "When sonic boom bans killed continental supersonic travel, the Queen of the Skies didn't become obsolete: it revolutionized affordable global travel for over five decades.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Main Deck Military Cargo Ingestion",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Time-lapse of heavy mechanized military pallets and jet engines sliding effortlessly into the gaping open nose of a 747 freighter under airport floodlights, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_7.mp4",
                "narration_text": "Today, while passenger 747s have retired, hundreds of 747 freighters still fly the world's most critical supply chains thanks to that exact second-story cockpit.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Queen of the Skies Sunset & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Majestic golden hour shot of a Boeing 747 soaring into pink clouds at sunset, sun glinting off the upper deck windows, cinematic warm lighting, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/boeing747_scene_8.mp4",
                "narration_text": "Have you ever flown on the upper deck of a 747? Subscribe and leave your memories in the comments below.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "project_azorian_salvage",
        "title": "The CIA's $4 Billion Mechanical Ocean Claw #shorts",
        "category": "Cold War Deep-Sea Engineering",
        "hook": "The CIA built a six-hundred-foot ship with a secret moon pool to steal a Soviet nuclear sub from three miles deep.",
        "description": "Project Azorian was the most daring covert salvage in naval history. How did Howard Hughes help the CIA secretly lift a 2,700-ton Soviet submarine off the ocean floor?\n\n\ud83d\udea2 Like & Subscribe for daily high-retention history & engineering documentaries!\n\n#shorts #cia #coldwar #submarines #engineering #navy #history #salvage",
        "tags": [
            "shorts",
            "cia",
            "coldwar",
            "submarines",
            "engineering",
            "navy",
            "history",
            "salvage",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Sunken Submarine Hook",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Underwater cinematic shot in pitch black ocean depth where deep-sea submersible spotlights reveal the crushed black hull of Soviet nuclear missile submarine K-129 resting on the abyssal plain, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_1.mp4",
                "narration_text": "Three miles beneath the Pacific Ocean, a sunken Soviet nuclear submarine held nuclear missiles and top-secret cryptographic codebooks.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Howard Hughes Cover Story",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D architectural cutaway of the 618-foot Hughes Glomar Explorer ship, exterior showing deep-sea manganese nodule mining gear, interior cutaway revealing a gigantic secret submarine moon pool inside the hull, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_2.mp4",
                "narration_text": "To recover it without starting World War Three, the CIA enlisted eccentric billionaire Howard Hughes to build a six-hundred-foot ship under the cover of mining ocean minerals.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "The Clementine Mechanical Capture Claw",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Massive 200-foot articulated steel capture claw named Clementine with colossal hydraulic mechanical fingers descending through a bottom well into dark ocean water, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_3.mp4",
                "narration_text": "Inside the ship was a hidden moon pool housing Clementine: a multi-million-pound mechanical steel claw designed to grip the entire submarine hull.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Three-Mile Pipe String Physics",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "3D forensic simulation of three miles of threaded 30-foot heavy drill pipes lowering the heavy claw through abyssal ocean currents, tension and bending stresses glowing on the steel pipe string, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_4.mp4",
                "narration_text": "Lowering the claw required connecting three miles of heavy steel pipe sections one by one, supporting over sixteen million pounds of dead weight in violent ocean currents.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "The Critical Claw Failure",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Forensic underwater simulation of two steel claw fingers snapping under catastrophic shear load at 9,000 feet depth, sending two-thirds of the submarine hull tumbling back down into the abyss, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_5.mp4",
                "narration_text": "As the claw hoisted the submarine off the seabed, two claw fingers suffered catastrophic structural failure: snapping under immense tension and dropping two-thirds of the sub back to the bottom.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.3,
                        "gain": 0.45
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Recovered Bow & Formal Nuclear Burial",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Inside the secret moon pool under sterile floodlights, naval engineers inspect the recovered 38-foot bow section containing nuclear torpedoes and lost crew members, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_6.mp4",
                "narration_text": "The recovered bow section contained two nuclear-tipped torpedoes and the bodies of six Soviet submariners, who were given a formal military burial at sea with full naval honors.",
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Glomar Response Legal Precedent",
                "graphic_type": "COCKPIT_TELEMETRY",
                "prompt": "Declassified vintage CIA file stamps slamming onto confidential memos with glowing text: 'NEITHER CONFIRM NOR DENY', vintage film grain, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_7.mp4",
                "narration_text": "When journalists uncovered the mission, the CIA created the famous legal response still used today: stating they could 'neither confirm nor deny' the existence of the project.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "Open Ocean Horizon & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Cinematic golden hour drone shot flying over open Pacific Ocean waters with the sun setting on calm deep blue waves, warm reflective light, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/azorian_scene_8.mp4",
                "narration_text": "Was spending four billion dollars for a piece of a submarine worth the risk? Subscribe and tell us what you think below.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "chunnel_drilling_secret",
        "title": "The 250-Foot Underwater Meeting That Shocked Engineers #shorts",
        "category": "Megastructures & Tunnels",
        "hook": "Drilling thirty miles from opposite coasts under the English Channel, their laser guidance met with only 14 inches of error.",
        "description": "The Channel Tunnel linked Britain to mainland Europe for the first time since the Ice Age. How did British and French engineers drill from opposite sides through chalk marl and meet in the exact center?\n\n\ud83d\ude86 Like & Subscribe for daily high-retention engineering & tunnel megaproject documentaries!\n\n#shorts #chunnel #channeltunnel #engineering #trains #uk #france #megaprojects",
        "tags": [
            "shorts",
            "chunnel",
            "channeltunnel",
            "engineering",
            "trains",
            "uk",
            "france",
            "megaprojects",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The Channel Eurostar Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Eurostar high-speed train roaring through the white-tiled Channel Tunnel at 100 MPH, aerodynamic nose slicing through bright tube lights, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_1.mp4",
                "narration_text": "Linking Britain to continental Europe for the first time since the Ice Age is a thirty-one-mile engineering marvel carved two hundred and fifty feet beneath the sea.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "3D Seabed Chalk Marl Layer Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D geological cross-section of the English Channel showing three parallel tunnels routed strictly through an impermeable grey chalk marl stratum beneath ocean waves, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_2.mp4",
                "narration_text": "Engineers could not drill through hard rock or permeable sand: they had to weave the tunnel through a single narrow layer of water-impermeable chalk marl.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "Giant Opposing TBMs",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Massive 1,000-ton English and French Tunnel Boring Machines boring from opposite coasts towards each other, giant hydraulic rams pushing against curved concrete liner rings, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_3.mp4",
                "narration_text": "Eleven giant tunnel boring machines weighing over a thousand tons chewed through chalk from both coasts, simultaneously bolting interlocking precast concrete rings behind them.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Laser Guidance Across Thirty Miles",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "3D simulation of laser alignment beams and satellite GPS survey benchmarks guiding the drill path around geological fissures across 30 miles under choppy ocean swells, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_4.mp4",
                "narration_text": "Because compasses were distorted by iron deposits and GPS could not penetrate two hundred feet of seawater, engineers used surface satellite triangulation to project lasers.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "The Historic Center Punch Breakthrough",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Dramatic hand-held camera perspective as a worker breaks through the final chalk rock with a pneumatic hammer, British and French miners shaking hands through the breakthrough hole, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_5.mp4",
                "narration_text": "On December first nineteen-ninety, a pilot probe broke through in the exact center: the laser alignment was off by just fourteen inches.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "Burying the TBM Monster Forever",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "3D animation of the British TBM steering downward and drilling its own grave into the bedrock below the main tunnel, buried in concrete while French TBM is dismantled, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_6.mp4",
                "narration_text": "Too colossal to turn around and reverse out, the British drilling machine was simply steered down into the bedrock and sealed forever in concrete beneath the tracks.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Underwater Cross-Over Cavern",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "Sweeping 3D interior of the underwater crossover cavern, large enough to fit an entire cathedral beneath the seabed, enabling trains to switch tracks underwater, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_7.mp4",
                "narration_text": "Beneath the English Channel lies a cathedral-sized crossover cavern carved underwater, allowing trains to switch tunnels during emergencies without surfacing.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.2,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "White Cliffs of Dover Golden Finish & CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Breathtaking sunset drone shot over the White Cliffs of Dover with calm ocean waters stretching towards France, golden volumetric sunlight, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/chunnel_scene_8.mp4",
                "narration_text": "Would you feel comfortable traveling under thirty miles of open ocean? Subscribe and leave your verdict below.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
                ]
            }
        ]
    },
    {
        "id": "north_sea_gas_rig_troll",
        "title": "The 1-Million-Ton Concrete Monster Standing on Ocean Mud #shorts",
        "category": "Extreme Offshore Engineering",
        "hook": "Taller than the Eiffel Tower, the heaviest structure ever moved by humanity sits in 1,000 feet of freezing North Sea waves.",
        "description": "The Troll A Platform weighs 1.2 million tons and stands 1,548 feet tall. How did engineers tow a concrete skyscraper across Norwegian fjords and sink it into seabed mud?\n\n\ud83c\udf0a Like & Subscribe for daily high-retention extreme engineering documentaries!\n\n#shorts #trolla #engineering #megaprojects #northsea #offshore #norway #ocean",
        "tags": [
            "shorts",
            "trolla",
            "engineering",
            "megaprojects",
            "northsea",
            "offshore",
            "norway",
            "documentary"
        ],
        "scenes": [
            {
                "scene_num": 1,
                "title": "The North Sea Behemoth Hook",
                "graphic_type": "DYNAMIC_SPEED_TRACKING",
                "prompt": "Low-angle dramatic drone shot rising along the massive concrete legs of the Troll A offshore platform in violent gray North Sea swells, platform standing 1,500 feet tall against gale winds, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_1.mp4",
                "narration_text": "Standing over fifteen hundred feet tall in the freezing North Sea is the heaviest object ever moved by human beings.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.35
                    },
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.5,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 2,
                "title": "Taller than the Eiffel Tower Cutaway",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D scale comparison graphic showing the Eiffel Tower placed next to Troll A, with 1,000 feet of Troll A submerged under deep ocean water resting on four hollow concrete legs, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_2.mp4",
                "narration_text": "Taller than the Eiffel Tower, Troll A weighs one point two million tons: a gravity-based structure constructed with six hundred and eighty-eight thousand tons of reinforced concrete.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 3,
                "title": "The Historic 120-Mile Ocean Tow",
                "graphic_type": "DYNAMIC_ACTION_TRACKING",
                "prompt": "Aerial view of ten massive deep-sea tugboats towing the colossal floating concrete skyscraper through a narrow Norwegian fjord at one knot speed, calm fjord reflections, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_3.mp4",
                "narration_text": "In nineteen-ninety-five, ten tugboats spent seven days towing the giant one hundred and twenty miles across Norwegian fjords at a crawl of one single knot.",
                "foley": [
                    {
                        "sfx": "water_rush.wav",
                        "time_offset": 0.4,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 4,
                "title": "Vacuum Suction Skirts Seabed Penetration",
                "graphic_type": "3D_ARCHITECTURAL_CUTAWAY",
                "prompt": "3D cross-section showing nineteen circular steel suction buckets penetrating 118 feet into soft ocean clay, water being pumped out to create massive vacuum holding force, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_4.mp4",
                "narration_text": "To anchor it in soft seabed mud, nineteen concrete vacuum skirts drove one hundred and eighteen feet into the seafloor, suctioning it securely into place without driving a single pile.",
                "foley": [
                    {
                        "sfx": "drill_rumble.wav",
                        "time_offset": 0.3,
                        "gain": 0.35
                    }
                ]
            },
            {
                "scene_num": 5,
                "title": "100-Year Wave Resonance Simulation",
                "graphic_type": "FORENSIC_SIMULATION",
                "prompt": "Forensic simulation of a hundred-year North Sea wave cresting 100 feet tall against the cylindrical concrete legs, natural frequency engineered to avoid destructive resonance oscillations, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_5.mp4",
                "narration_text": "Engineered to withstand one-hundred-foot monster waves, its natural oscillation period was tuned to avoid resonance with North Sea swells that would snap concrete columns.",
                "foley": [
                    {
                        "sfx": "impact_boom.wav",
                        "time_offset": 0.4,
                        "gain": 0.4
                    }
                ]
            },
            {
                "scene_num": 6,
                "title": "The 1,000-Foot Elevator Shaft",
                "graphic_type": "COCKPIT_TELEMETRY",
                "prompt": "Perspective looking straight down a dizzying 1,000-foot hollow concrete leg interior, elevator cage descending inside with telemetry showing minus 300 meters below sea level, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_6.mp4",
                "narration_text": "Inside one of the hollow concrete legs is an elevator that takes nine minutes to descend one thousand feet beneath the ocean surface to the seabed pump rooms.",
                "foley": [
                    {
                        "sfx": "gate_clank.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 7,
                "title": "Supplying Europe's Energy Veins",
                "graphic_type": "3D_SATELLITE_DEM",
                "prompt": "3D glowing map of high-pressure subsea pipelines radiating out from Troll A across the North Sea floor into Germany, the UK, and France, delivering 10% of Europe's gas, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_7.mp4",
                "narration_text": "Supplying ten percent of Europe's total natural gas, it was designed with a service lifespan of seventy years in the world's most unforgiving offshore waters.",
                "foley": [
                    {
                        "sfx": "warning_beep.wav",
                        "time_offset": 0.3,
                        "gain": 0.3
                    }
                ]
            },
            {
                "scene_num": 8,
                "title": "North Sea Midnight Sun & Organic CTA",
                "graphic_type": "GOLDEN_FINISH_CTA",
                "prompt": "Breathtaking twilight drone shot of the Troll A platform under the midnight sun in the North Sea, flare boom burning gently against pink and purple skies, 4k 60fps vertical 9:16",
                "input_video": "data/flow_clips/troll_scene_8.mp4",
                "narration_text": "Could humans build entire offshore cities with this concrete technology? Hit subscribe and share your thoughts below.",
                "foley": [
                    {
                        "sfx": "tension_drone.wav",
                        "time_offset": 0.0,
                        "gain": 0.25
                    }
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

        # Step 0: Ensure all physical Google Veo 2 video clips exist via Google Flow
        from src.workflows.autonomous_flow_pipeline import ensure_scene_clips
        try:
            await ensure_scene_clips(next_item)
        except Exception as e:
            print(f"Warning during Google Flow scene generation: {e}")

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
        qa_result = AIVideoInspector.evaluate_video(str(master_video_path), is_veo_flow_source=True, topic_metadata=next_item)
        print(f"AI Quality Score: {qa_result.get('score')}/100 | Verdict: {qa_result.get('verdict')}")
        if qa_result.get("flags"):
            print("AI Inspector Flags:", qa_result.get("flags"))

        # Hard Gate: Halt immediately if quality inspection fails
        if qa_result.get("verdict") == "REJECT":
            return {
                "success": False,
                "error": f"Quality Gate REJECTED video: {qa_result.get('flags')}",
                "qa_result": qa_result
            }

        # Safety Gate: Default to private for creator preview if quality score is below 90
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
