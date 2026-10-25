"""Comprehensive 8.5-minute narrative script for 'The Panama Canal Trap'.
Structured into 5 Acts, 18 scenes, with exact narration text, visual gags, animation cues, and Foley triggers.
Target duration: ~510 to 540 seconds (8.5 to 9.0 minutes).
"""

PANAMA_CANAL_SCRIPT = {
    "title": "The Panama Canal Trap: How an 85-Foot Mountain Traps Global Trade",
    "target_duration_sec": 520,
    "acts": [
        {
            "act_number": 1,
            "act_title": "The Mountain Elevator & The Water Paradox",
            "scenes": [
                {
                    "scene_id": "scene_01_hook_map",
                    "title": "The 8,000-Mile Illusion",
                    "duration": 30.0,
                    "narration": "Most people imagine the Panama Canal as a flat, tranquil ditch slicing through Central America—a simple blue ribbon connecting the Atlantic to the Pacific, just like the Suez Canal in Egypt. But that assumption is completely, dangerously wrong. If engineers had tried to dig a flat sea-level trench through Panama, the Pacific Ocean would literally pour into the Atlantic with lethal tidal waves, because the Pacific side is roughly eight inches higher, and its tides swing by more than twenty vertical feet every single day.",
                    "visual_type": "2D_MAP_PARADOX",
                    "visual_description": "2D animated map of the Americas showing the massive 8,000-mile detour around Cape Horn in red vs. the 50-mile shortcut in green. Split water level diagram showing Pacific tidal surge.",
                    "foley_cues": [("whoosh", 0.5), ("sonar_ping", 6.0), ("water_rush", 18.0)]
                },
                {
                    "scene_id": "scene_02_mountain_elevator",
                    "title": "The 85-Foot Mountain Elevator",
                    "duration": 32.0,
                    "narration": "Instead, the Panama Canal is something far more bizarre and terrifying: it is a massive liquid roller coaster. Every single day, eighty-thousand-ton mega-ships carrying billions of dollars in electronics, grain, and liquefied natural gas are not sailing across Panama. They are being physically hoisted eighty-five feet into the sky, driven over an active continental mountain range through dense tropical jungle, and then gingerly lowered back down into another ocean.",
                    "visual_type": "CROSS_SECTION_ELEVATOR",
                    "visual_description": "Animated side cutaway of the continental divide: A giant cartoon container ship rising step-by-step like a toy in an elevator, rolling across the mountain top, and descending.",
                    "foley_cues": [("ship_horn", 1.0), ("metal_clank", 10.0), ("water_surge", 18.0)]
                },
                {
                    "scene_id": "scene_03_flushing_paradox",
                    "title": "Flushing 52 Million Gallons",
                    "duration": 34.0,
                    "narration": "And here is the astonishing engineering catch that is threatening global trade today: the canal does not use ocean water to lift these steel leviathans. It uses fresh rainwater. Every single time a single container ship crosses the isthmus, fifty-two million gallons of pristine fresh drinking water are drained from an artificial jungle lake, flushed into the lock chambers, and dumped straight into the ocean—lost forever to human consumption.",
                    "visual_type": "FLUSHING_PARADOX_METAPHOR",
                    "visual_description": "Giant cartoon toilet handle flushing beside a lock chamber; massive water rush draining into ocean; cartoon water droplets weeping and waving goodbye.",
                    "foley_cues": [("toilet_flush", 2.0), ("water_torrent", 8.0), ("whistle_drop", 20.0), ("coin_clatter", 26.0)]
                }
            ]
        },
        {
            "act_number": 2,
            "act_title": "The French Graveyard: How Jungle & Bad Math Broke an Empire",
            "scenes": [
                {
                    "scene_id": "scene_04_french_arrogance",
                    "title": "De Lesseps Arrives in Panama",
                    "duration": 32.0,
                    "narration": "To understand how humanity trapped itself in this 85-foot mountain elevator, we have to travel back to 1880. A flamboyant French diplomat named Ferdinand de Lesseps had just conquered the sands of Egypt by opening the Suez Canal. He was celebrated across Europe as the undisputed master of geography. So when he turned his gaze to Central America, he made a fateful, arrogant declaration: if I dug a sea-level ditch through the deserts of Egypt, I will dig a sea-level ditch through the jungles of Panama.",
                    "visual_type": "CHARACTER_HISTORICAL_GAG",
                    "visual_description": "Cartoon Ferdinand de Lesseps in a top hat sipping champagne with a golden shovel, looking at a wall of menacing, living jungle mountains.",
                    "foley_cues": [("champagne_pop", 1.5), ("crowd_cheer", 7.0), ("jungle_rumble", 22.0)]
                },
                {
                    "scene_id": "scene_05_jungle_nightmare",
                    "title": "The Jungle Fights Back",
                    "duration": 34.0,
                    "narration": "He could not have been more catastrophically wrong. Egypt was flat desert sand; Panama was an impenetrable wall of volcanic basalt, jagged mountain ridges, and torrential tropical deluges. For eight months of every year, biblical rains battered the Isthmus. The unruly Chagres River would swell overnight by thirty-five vertical feet, triggering cataclysmic mudslides that swept away entire worker villages, hospital camps, and eighty-ton steam locomotives directly into the mud.",
                    "visual_type": "ENVIRONMENT_CHAOS",
                    "visual_description": "Tropical thunderstorm with jagged lightning; cartoon mudslides engulfing steam shovels; French engineers in top hats slipping into mud pits.",
                    "foley_cues": [("thunder_strike", 1.0), ("rain_loop", 3.0), ("mud_squish", 15.0), ("steam_whistle", 24.0)]
                },
                {
                    "scene_id": "scene_06_mosquito_graveyard",
                    "title": "The Mosquito Massacre & Financial Ruin",
                    "duration": 32.0,
                    "narration": "And then came the real killers: yellow fever and malaria. European doctors back then had no idea mosquitoes transmitted the diseases; they actually placed open water pans under hospital bed legs to stop ants from crawling up, unknowingly creating the perfect stagnant breeding ground for millions of infected mosquitoes right next to feverish patients. Over twenty-two thousand workers perished in agony. The French company collapsed in disgraceful bankruptcy, ruining eight-hundred thousand small French families in the biggest financial fraud of the nineteenth century.",
                    "visual_type": "COMIC_VFX_GRAVEYARD",
                    "visual_description": "Swarm of cartoon mosquitoes with tiny syringes and menacing smiles buzzing over hospital beds; falling stock certificates and bankruptcy stamp.",
                    "foley_cues": [("mosquito_buzz", 1.0), ("cough_wheeze", 8.0), ("stamp_thud", 20.0), ("glass_shatter", 26.0)]
                }
            ]
        },
        {
            "act_number": 3,
            "act_title": "The American Audacity: Creating a Lake on Top of a Mountain",
            "scenes": [
                {
                    "scene_id": "scene_07_teddy_roosevelt",
                    "title": "Teddy Roosevelt Takes the Isthmus",
                    "duration": 30.0,
                    "narration": "Enter the twenty-sixth President of the United States, Theodore Roosevelt. Teddy didn't just want a canal—he saw it as America's manifest destiny, believing whoever controlled the maritime gateway between the oceans would command global trade and naval supremacy for the entire twentieth century. When the government of Colombia hesitated to ratify the treaty, Washington covertly backed a lightning Panamanian revolution, dispatched gunboats to block Colombian troops from landing, and swiftly signed a treaty granting the United States sovereign control over a ten-mile wide Canal Zone in perpetuity.",
                    "visual_type": "GEOPOLITICS_CHARACTER",
                    "visual_description": "Cartoon Teddy Roosevelt with round spectacles and massive toothy grin holding a giant wrench and pointing warships toward the isthmus.",
                    "foley_cues": [("warship_horn", 2.0), ("gavel_strike", 12.0), ("eagle_screech", 22.0)]
                },
                {
                    "scene_id": "scene_08_mosquito_war",
                    "title": "Dr. Gorgas Wages War on Mosquitoes",
                    "duration": 32.0,
                    "narration": "Before turning a single cubic yard of soil, the Americans recognized they had to defeat the jungle's microscopic assassins. Chief sanitary officer Dr. William Gorgas launched an unprecedented military crusade against the Aedes aegypti mosquito: draining hundreds of thousands of stagnant jungle ponds, clearing millions of square yards of brush, pouring thousands of barrels of kerosene over swamps to suffocate mosquito larvae, and screening every doorway and window in the Republic of Panama. Within two years, yellow fever was wiped off the map.",
                    "visual_type": "VFX_OIL_SPRAY",
                    "visual_description": "Cartoon Dr. Gorgas with a fumigation cannon spraying clouds of kerosene; cartoon mosquitoes waving white surrender flags and dropping.",
                    "foley_cues": [("spray_hiss", 2.0), ("siren_slide", 12.0), ("comic_ding", 22.0)]
                },
                {
                    "scene_id": "scene_09_lake_gatun_masterstroke",
                    "title": "The Gatun Lake Masterstroke",
                    "duration": 34.0,
                    "narration": "Then came the radical stroke of engineering genius from Chief Engineer John Stevens. Stevens stared at the jagged continental divide and told President Roosevelt: stop trying to cut down to sea level. Instead, build a colossal earthen dam across the raging Chagres River, tame the floodwaters, and create the largest artificial lake in the world, sitting eighty-five feet above sea level in the mountain clouds. Then, build giant three-step concrete water staircases on both sides to hoist the world's ships straight up into the sky.",
                    "visual_type": "SCHEMATIC_CROSS_SECTION",
                    "visual_description": "Technical diagram: River valley flooding into a glowing cyan high-altitude lake; concrete staircases forming on Atlantic and Pacific flanks.",
                    "foley_cues": [("slide_whistle", 1.0), ("water_rush", 10.0), ("concrete_slam", 22.0)]
                }
            ]
        },
        {
            "act_number": 4,
            "act_title": "The Mechanical Marvel: How the Water Elevator Works",
            "scenes": [
                {
                    "scene_id": "scene_10_gravity_culverts",
                    "title": "Powered by Pure Gravity",
                    "duration": 32.0,
                    "narration": "The physical magnitude of this hydraulic marvel still defies belief. The lock walls are monoliths of solid concrete as thick as six-story office buildings at their base. But here is the crowning secret of the Panama Canal: to this day, not a single water pump is used to lift these gigantic vessels. The entire eight-hundred-foot system operates entirely by the silent, relentless force of natural gravity, letting water seek its own level through massive subterranean tunnels eighteen feet in diameter.",
                    "visual_type": "CUTAWAY_CULVERTS",
                    "visual_description": "Underground cutaway beneath the lock floor: Massive culverts (tunnels large enough for a train) opening cylindrical valves; water gushing upward under natural head pressure.",
                    "foley_cues": [("sub_bass_drone", 1.0), ("valve_creak", 10.0), ("water_geyser", 18.0)]
                },
                {
                    "scene_id": "scene_11_miter_gates",
                    "title": "The Seven-Story Steel Gates",
                    "duration": 30.0,
                    "narration": "Each chamber is sealed by titanic seven-story steel miter gates, weighing over seven hundred tons apiece. Yet they are engineered with such mathematical elegance—featuring hollow lower air chambers that float in water—that a modest forty-horsepower electric motor, no larger than an automobile engine, can glide these seven-story steel behemoths shut as smoothly as closing a kitchen pantry door.",
                    "visual_type": "MECHANICAL_GATES",
                    "visual_description": "Close-up of towering steel miter gates swinging shut; rubber seals locking together; pressure gauges ticking into the green zone.",
                    "foley_cues": [("gear_turning", 2.0), ("gate_clunk", 14.0), ("metal_latch", 24.0)]
                },
                {
                    "scene_id": "scene_12_electric_mules",
                    "title": "The Electric Mules of Panama",
                    "duration": 32.0,
                    "narration": "Once inside the concrete trench, a massive Panamax vessel has barely twenty-four inches of clearance between its steel hull and the abrasive concrete walls. Even the gentlest gust of tropical wind could grind the ship against the locks and rupture fuel tanks. That is why vessels are forbidden from using their own engines; instead, specialized fifty-ton electric locomotives, nicknamed mules, run along rack-and-pinion tracks on both sides of the canal, using steel winches to keep the floating mountain dead-center.",
                    "visual_type": "LOCOMOTIVE_ANIMATION",
                    "visual_description": "Cartoon electric locomotive running on cog railway tracks; tension cables tightening and flexing; captain sweating through binoculars.",
                    "foley_cues": [("locomotive_hum", 2.0), ("cable_strain", 12.0), ("whistle_tweet", 24.0)]
                },
                {
                    "scene_id": "scene_13_culebra_cut",
                    "title": "The Culebra Cut: Slicing the Mountain",
                    "duration": 32.0,
                    "narration": "Between the locks lay the nine-mile Culebra Cut—an artificial canyon gouged directly through the spine of the continental divide. Over sixty million pounds of high-grade dynamite were detonated, blasting away entire mountainsides. Fleets of steam shovels loaded spoil into hundreds of dirt trains running day and night, excavating enough earth to dig an eight-foot tunnel all the way through the center of the Earth. When water finally flooded the cut in 1914, human engineering had split the Western Hemisphere in two.",
                    "visual_type": "EXPLOSION_CANON_BLAST",
                    "visual_description": "Series of cartoon dynamite explosions rocketing rock chunks; steam shovels tossing boulders into rail cars; continents breaking apart.",
                    "foley_cues": [("dynamite_fuse", 1.0), ("boom_explosion", 6.0), ("rock_land", 14.0), ("orchestral_swell", 24.0)]
                }
            ]
        },
        {
            "act_number": 5,
            "act_title": "The Climate Trap: When a Mountain Lake Runs Out of Water",
            "scenes": [
                {
                    "scene_id": "scene_14_drought_crisis",
                    "title": "The 2023 Drought Emergency",
                    "duration": 34.0,
                    "narration": "For more than a century, the Panama Canal stood as an untouchable monument to American industrial supremacy. But in 2023, the critical vulnerability of relying on an elevated freshwater lake triggered a full-blown global supply chain crisis. A severe El Niño weather pattern brought unprecedented heat and the driest rainy season in the canal's hundred-and-ten-year history. Lake Gatun's water reserves plummeted by several feet every week, exposing ancient drowned trees on parched, cracked mud flats. For the first time in modern memory, the mountain elevator was running out of water.",
                    "visual_type": "ENVIRONMENT_DROUGHT",
                    "visual_description": "Lake Gatun water line dropping rapidly; cracked mud shoreline exposing sunken tree stumps; rain clouds dissipating under a scorching sun.",
                    "foley_cues": [("dry_wind", 1.0), ("warning_beep", 10.0), ("creaking_pipe", 20.0)]
                },
                {
                    "scene_id": "scene_15_traffic_jam",
                    "title": "The 150-Ship Maritime Gridlock",
                    "duration": 32.0,
                    "narration": "To prevent the lake from running completely dry, the Panama Canal Authority took the emergency measure of slashing daily vessel transits from thirty-eight ships down to barely twenty-two, while forcing ships to carry forty percent less cargo so they wouldn't scrape the shallow canal bottom. The result was pure maritime chaos: over one hundred and sixty massive container ships, gas carriers, and grain vessels were stranded at sea in an agonizing weeks-long traffic jam on both sides of the Isthmus, burning millions of dollars in bunker fuel while waiting for rain.",
                    "visual_type": "MAP_TRAFFIC_JAM",
                    "visual_description": "Map view of Pacific entrance jammed with dozens of cartoon container ships bumping into each other; ship horns honking in discord; calendar pages flipping.",
                    "foley_cues": [("discord_horns", 2.0), ("clock_ticking", 12.0), ("cash_register", 22.0)]
                },
                {
                    "scene_id": "scene_16_four_million_auction",
                    "title": "The $4 Million Line-Skipping Auction",
                    "duration": 32.0,
                    "narration": "Desperate multinational corporations began engaging in extraordinary blind bidding wars just to skip the queue. In late 2023, a Japanese liquefied natural gas exporter paid a historic four million dollars for a single priority transit slot at auction—on top of the standard four-hundred-thousand-dollar canal toll! Think about that: over four point four million dollars paid for the privilege of riding an 85-foot water elevator across fifty miles of jungle, simply because waiting in line would cost them even more in cancelled contracts.",
                    "visual_type": "COMIC_AUCTION_GAG",
                    "visual_description": "Auction gavel slamming down; dollar bills raining down; Sheikh and CEO characters sweating over auction paddles shouting bids.",
                    "foley_cues": [("auction_gavel", 2.0), ("crowd_gasp", 10.0), ("cash_drain", 20.0)]
                },
                {
                    "scene_id": "scene_17_competing_routes",
                    "title": "The Battle for Alternative Shortcuts",
                    "duration": 30.0,
                    "narration": "With climate change making rainfall over Lake Gatun increasingly erratic, the world is scrambling for alternatives to escape Panama's water bottleneck. Mexico has poured billions into its Interoceanic Rail Corridor, racing to build a high-speed freight rail shortcut between the Gulf of Mexico and the Pacific. Colombia and Nicaragua have pitched multi-billion dollar dry canals. And in the warming Arctic, melting polar ice is slowly unlocking the fabled Northwest Passage.",
                    "visual_type": "MAP_COMPETING_ROUTES",
                    "visual_description": "2D global map displaying dashed glowing trails: Mexican rail line, Arctic shipping route, and Cape Horn detour competing against Panama.",
                    "foley_cues": [("train_chug", 2.0), ("radar_ping", 10.0), ("ice_crack", 20.0)]
                },
                {
                    "scene_id": "scene_18_conclusion_verdict",
                    "title": "The Modern Choke Point Dilemma",
                    "duration": 32.0,
                    "narration": "Yet despite its growing climate trap, five percent of all global seaborne trade and forty percent of all container traffic bound for the United States still depends entirely on this 85-foot mountain elevator. The Panama Canal conquered disease, rock, and political revolution to unite two oceans—yet more than a century later, it remains trapped by its own ingenious design, entirely dependent on whether the skies above the jungle decide to rain.",
                    "visual_type": "EPIC_SUNSET_FINALE",
                    "visual_description": "Hero wide shot of container ship exiting Miraflores locks into the Pacific sunset; golden water reflections; dramatic cinematic title card fade.",
                    "foley_cues": [("cinematic_swell", 1.0), ("ship_horn_echo", 8.0), ("impact_boom", 22.0)]
                }
            ]
        }
    ]
}

def get_full_script_text():
    full_text = []
    for act in PANAMA_CANAL_SCRIPT["acts"]:
        for sc in act["scenes"]:
            full_text.append(sc["narration"])
    return " ".join(full_text)

if __name__ == '__main__':
    text = get_full_script_text()
    words = len(text.split())
    print(f"Total Words: {words}")
    print(f"Estimated Spoken Duration at 135 wpm: {words / 135 * 60:.1f} seconds ({words / 135:.2f} minutes)")
