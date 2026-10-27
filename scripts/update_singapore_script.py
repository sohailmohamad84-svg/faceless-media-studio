import sys
import os

with open("src/workflows/daily_shorts_pipeline.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace description
old_desc = 'Singapore has expanded its land area by over 130 square kilometers using 500 million tons of sand. How did an illicit ocean dredging black market alter the map of Southeast Asia?'
new_desc = 'Singapore has expanded its land area by over 25% since 1965, importing over 500 million tons of sand. How did environmental bans, disappearing sand cays in Indonesia, Dutch-style polders, and the engineering of Tuas Port reshape Southeast Asia?'
content = content.replace(old_desc, new_desc)

# Replace Scene 2
old_sc2 = '"To construct modern skyscrapers and mega container ports, the city-state devoured over five hundred million tons of ocean sand."'
new_sc2 = '"To construct modern skyscrapers and ports, Singapore imported over five hundred million tons of ocean sand, becoming the world\'s largest sand importer per capita."'
content = content.replace(old_sc2, new_sc2)

# Replace Scene 3
old_sc3 = '"When neighboring countries banned sand exports, an illicit multi-billion-dollar black market dredged entire Indonesian islands out of existence."'
new_sc3 = '"When regional bans halted legal supplies, an illicit dredging black market devastated ecosystems, causing up to two dozen small Indonesian islets and sand cays to submerge below the tides."'
content = content.replace(old_sc3, new_sc3)

# Replace Scene 4
old_sc4 = '"To survive the embargo, Singapore pioneered massive Dutch-style polders, sealing ocean basins with reinforced sea dikes to reclaim land without sand."'
new_sc4 = '"To diversify beyond imported sand, Singapore pioneered massive Dutch-style polders, sealing ocean basins with reinforced dikes to reclaim land below sea level."'
content = content.replace(old_sc4, new_sc4)

# Replace Scene 5
old_sc5 = '"Millions of prefabricated vertical drains compress waterlogged marine mud under immense pressure, turning treacherous ocean silt into rock-solid ground foundations."'
new_sc5 = '"Miles of prefabricated vertical drains accelerate water expulsion from deep marine clay under massive surcharge weight, consolidating unstable seabed silt into solid ground foundations."'
content = content.replace(old_sc5, new_sc5)

# Replace Scene 6
old_sc6 = '"The result is Tuas Port: the largest fully automated container terminal on the planet, built entirely on land that did not exist forty years ago."'
new_sc6 = '"The result is Tuas Mega Port: planned to become the world\'s largest automated container terminal upon completion in the 2040s, with Phase One already operational on reclaimed land."'
content = content.replace(old_sc6, new_sc6)

# Replace Scene 7
old_sc7 = '"With sea levels projected to rise, every single new square mile is built four meters above current tides as an existential fortress against the ocean."'
new_sc7 = '"With sea levels projected to rise, newly reclaimed land is mandated to sit at least four to five meters above Singapore Height Datum, creating an existential coastal fortress against the sea."'
content = content.replace(old_sc7, new_sc7)

# Replace Scene 8
old_sc8 = '"Could other coastal nations buy their own survival by manufacturing new land? Subscribe and leave your thoughts in the comments."'
new_sc8 = '"Could other vulnerable coastal nations engineer their way out of rising seas? Subscribe and leave your perspective in the comments."'
content = content.replace(old_sc8, new_sc8)

with open("src/workflows/daily_shorts_pipeline.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated daily_shorts_pipeline.py successfully!")
