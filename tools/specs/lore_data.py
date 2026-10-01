"""Authored lore of the starship (all original): ship, factions, star systems, lanes, mission plan, timeline, logs, datapads.

Pure data; tools/specs/gen_lore.py derives distances, ETAs and writes godot/data/lore.json and docs/LORE.md.
Dates: the Concord calendar counts years as in the timeline ("CY"); ship's logs use stardates where one unit is one ship day
(mission day = stardate - 41000.0).  Coordinates are light-years from the home system (x right, y up, z towards the galactic south).
"""

SHIP = {
    "name": "Vesper Lantern",
    "registry": "MCV-7741",
    "class": "Wayfinder-class deep survey cruiser",
    "builder": "Calder-Okonkwo Orbital Yards, Tessara Ring Dock 4",
    "commissioned": 2291,
    "motto": "Ad lucem ultra",
    "crew": 64,
    "cruise_warp": 5.0,
    "top_warp": 8.0,
    "ly_per_day_at_cruise": 1.1,
    "description": ("Vesper Lantern is a three-deck deep survey cruiser of the Meridian Concord's Survey Service, built to stay out for years: "
                    "a fusion core and warp coils amidships, a hangar for two survey shuttles on the stern platform, a hydroponics garden that "
                    "feeds most of the crew and a bridge that overhangs the bow like the lantern on an old river boat. Her Deep Survey Charter 7 "
                    "sends her four years out along the Concord frontier to chart the Veil region and to settle where a faint repeating signal comes from."),
    "charter": "Deep Survey Charter 7 (four years, CY 2294-2298): chart the frontier lanes, survey every system of the plan, keep the peace with neighbours and run down the Heartbeat signal.",
}

FACTIONS = [
    ("concord", "Meridian Concord", "#4aa8ff", "allied",
     "A union of eleven home systems around Tessara governed by a rotating Assembly. Funds the Survey Service, values open lanes and shared charts."),
    ("collegium", "Orrery Collegium", "#c08aff", "allied",
     "An academic league of observatories and archive worlds. Trades star charts and data for passage; neutral in every dispute."),
    ("commons", "Thessaly Commons", "#6be08a", "neutral",
     "Agrarian settlements who farm terraformed worlds and sell grain and seed stock; friendly but insular."),
    ("freeports", "Ashfall Free Ports", "#ffc247", "neutral",
     "A web of independent trade stations and salvage guilds that keep no flag but their ledgers; the cheapest repairs in the volume."),
    ("korvath", "Korvath Reach Compact", "#ff6a4a", "rival",
     "Mining houses and fleet families who claim the lanes beyond Ghalt and bristle at survey ships near their veins."),
    ("unclaimed", "Unclaimed and Uncharted", "#8a96a8", "unknown",
     "Systems nobody holds: dark stars, ruins, hazards and the unknown."),
]


def P(name, typ, g, atm, hab, moons, notes):
    return {"name": name, "type": typ, "gravity_g": g, "atmosphere": atm, "habitable": hab, "moons": moons, "notes": notes}


# id, name, pos, (class, temp_k, lum_solar), faction, kind, visited, summary, planets
SYSTEMS = [
    ("tessara", "Tessara", (0.0, 0.0, 0.0), ("G2V", 5780, 1.0), "concord", "home", True,
     "Home system of the Concord and the yard that built Vesper Lantern; the origin of every chart.",
     [P("Anchorage", "ocean-continental", 0.98, "N2-O2, 21% O2", True, 1, "Capital world, nine billion people, the Assembly sits at Lantern Hill."),
      P("Tessara II", "hot rock", 0.71, "thin CO2", False, 0, "Solar mirrors and ore smelters."),
      P("Gyre", "gas giant", 2.4, "H2-He", False, 14, "Fuel skimmers and the Ring Docks hang above it.")]),
    ("calloway", "Calloway", (4.2, 1.1, -2.0), ("K1V", 5100, 0.45), "concord", "waypoint", True,
     "First jump of the voyage; an orange dwarf with a busy survey relay.",
     [P("Calloway Prime", "cold desert", 0.82, "thin N2-CO2", False, 2, "Mining camps, relay station Bellwether in orbit."),
      P("Dorn", "ice dwarf", 0.12, "none", False, 0, "Water ice quarry used for reaction mass.")]),
    ("harrow", "Harrow", (-3.1, 2.8, 4.5), ("M0V", 3900, 0.12), "concord", "waypoint", True,
     "Dim red dwarf with a quiet Concord customs station.",
     [P("Harrow Station", "orbital", 0.0, "habitat air", True, 0, "Customs and fuel depot."),
      P("Harrow b", "tidally locked rock", 1.1, "thin N2", False, 0, "Terminator ridge colony proposals.")]),
    ("ostrava", "Ostrava", (-6.0, -1.5, -4.4), ("K5V", 4400, 0.2), "concord", "outpost", False,
     "Concord mining outpost on a cold, dark world.",
     [P("Ostrava III", "barren rock", 0.64, "none", False, 1, "Cobalt and titanium mining.")]),
    ("vellum", "Vellum", (6.8, -3.0, 5.1), ("F8V", 6150, 1.8), "collegium", "outpost", False,
     "Collegium archive world: the planet itself is a library.",
     [P("Vellum Stacks", "temperate rock", 1.02, "N2-O2, 19% O2", True, 2, "Stacks of data vaults under glass domes."),
      P("Vellum b", "ice giant", 1.3, "H2-He-CH4", False, 9, "Cold storage for deep archives.")]),
    ("lumen", "Lumen", (2.0, 7.5, -5.5), ("A2V", 9000, 22.0), "concord", "waypoint", False,
     "Bright white star with a thin debris ring used as a calibration source by astronomers.",
     [P("Lumen Ring", "debris belt", 0.0, "none", False, 0, "Dust sheet that scatters starlight perfectly for instrument tests."),
      P("Lumen b", "scorched rock", 0.9, "none", False, 0, "Too hot for anything.")]),
    ("brindle", "Brindle", (-8.5, 5.0, 0.5), ("G8V", 5400, 0.7), "commons", "outpost", False,
     "Thessaly farm world with wheat seas, and the seed vault our hydroponics stock came from.",
     [P("Brindle", "temperate rock", 0.93, "N2-O2, 20% O2", True, 1, "Wheat plains, terraced vineyards."),
      P("Bramble", "cold rock", 0.6, "thin N2", False, 0, "Seed vault in a lava tube.")]),
    ("sarrow", "Sarrow", (9.5, 3.5, -3.0), ("K3V", 4800, 0.32), "concord", "outpost", True,
     "Concord frontier outpost where the ship took on coolant and spares.",
     [P("Sarrow Reach", "cold desert", 0.7, "thin CO2", False, 2, "Outpost dome, fuel tanks and a landing field."),
      P("Sarrow b", "ice world", 0.4, "none", False, 0, "Source of the reaction ice.")]),
    ("kithara", "Kithara", (12.0, -6.0, 0.0), ("F2V", 6900, 3.6), "collegium", "waypoint", True,
     "Collegium observatory system; its astronomers triangulated the Heartbeat.",
     [P("Kithara Observatory", "orbital", 0.0, "habitat air", True, 0, "Twelve radio dishes on a ring."),
      P("Kithara II", "ocean world", 1.15, "N2-O2, 17% O2", True, 3, "Floating research rafts.")]),
    ("halcyon", "Halcyon Gate", (15.5, 2.0, -9.0), ("G5V", 5600, 0.85), "unclaimed", "waypoint", True,
     "A quiet yellow star with an old lane relay buoy at its gate; the ship's present anchorage.",
     [P("Halcyon I", "cold rock", 0.55, "none", False, 0, "Survey shuttle landing site; relay buoy in orbit."),
      P("Halcyon II", "ocean-ice", 0.88, "thin N2-O2", False, 4, "Frozen sea with warm vents."),
      P("Halcyon III", "gas giant", 1.9, "H2-He", False, 11, "Shuttle fuel skimming.")]),
    ("dunmere", "Dunmere", (-14.0, -4.0, 9.0), ("K0V", 5250, 0.5), "commons", "outpost", False,
     "Quiet agricultural system on the Commons side of the volume.",
     [P("Dunmere", "temperate rock", 1.0, "N2-O2, 21% O2", True, 2, "Orchards and pasture."),
      P("Dunmere b", "hot rock", 0.8, "CO2", False, 0, "Greenhouse trials.")]),
    ("cinder", "Cinder", (-18.0, 8.0, -6.0), ("M2V", 3500, 0.04), "freeports", "outpost", False,
     "Free port built inside a hollowed-out comet nucleus: cheap repairs, no questions.",
     [P("Cinder Hollow", "comet habitat", 0.2, "habitat air", True, 0, "Docks, markets and a hundred salvage guilds.")]),
    ("korvath_prime", "Korvath Prime", (22.0, -12.0, 7.0), ("K2V", 5000, 0.4), "korvath", "outpost", False,
     "Seat of the Compact's fleet families; heavily patrolled.",
     [P("Korvath", "hot desert", 1.2, "dense CO2-N2", False, 1, "Domed foundry cities."),
      P("Korvath b", "rock", 0.9, "none", False, 0, "Shipyards.")]),
    ("ghalt", "Ghalt", (25.0, -3.0, -14.0), ("K4V", 4600, 0.25), "korvath", "outpost", False,
     "Compact mining outpost that sells fuel and passage permits to survey ships.",
     [P("Ghalt Hollow", "cold rock", 0.7, "none", False, 0, "Ice and iron."), P("Ghalt b", "ice giant", 1.4, "H2-He-CH4", False, 6, "Gas mining rigs.")]),
    ("ironwake", "Ironwake", (19.0, -16.0, -4.0), ("G9V", 5300, 0.6), "korvath", "hazard", False,
     "Iron-rich debris field of a shattered world; mining houses fight over it.",
     [P("Ironwake Belt", "debris belt", 0.0, "none", False, 0, "Dense, fast-moving rubble; lane hazard.")]),
    ("veil", "The Veil", (24.0, 6.0, -18.0), ("B9V", 11000, 60.0), "unclaimed", "hazard", False,
     "A young blue star wrapped in a dust nebula that scrambles sensors and warp fields.",
     [P("Veil Anvil", "molten rock", 1.4, "none", False, 0, "Forming under the dust."),
      P("Veil b", "gas dwarf", 1.1, "H2-He", False, 3, "Ice-dust moons forming.")]),
    ("orrin", "Orrin", (-26.0, 12.0, 8.0), ("K7V", 4100, 0.1), "freeports", "outpost", False,
     "Salvage guild system around a dim orange star.",
     [P("Orrin Yard", "orbital", 0.0, "habitat air", True, 0, "Wreck breakers."), P("Orrin c", "ice dwarf", 0.2, "none", False, 0, "Cold storage.")]),
    ("wyndham", "Wyndham", (-22.0, -14.0, -18.0), ("M1V", 3700, 0.06), "unclaimed", "uncharted", False,
     "Never surveyed: a red dwarf seen only from a distance.",
     [P("Wyndham a", "unknown", 0.0, "unknown", False, 0, "Unsurveyed.")]),
    ("tamsin", "Tamsin", (30.0, 10.0, -22.0), ("F5V", 6500, 2.5), "unclaimed", "waypoint", False,
     "A yellow-white star at the edge of the Veil dust; the last quiet anchorage before the Lighthouse.",
     [P("Tamsin I", "barren rock", 0.45, "none", False, 1, "Planned survey camp."), P("Tamsin II", "ice giant", 1.2, "H2-He-CH4", False, 7, "Fuel source.")]),
    ("marrow", "Marrow", (34.0, -2.0, -22.0), ("K1V", 5100, 0.45), "korvath", "outpost", False,
     "Compact listening post on a bare moon, watching the Veil.",
     [P("Marrow Post", "airless moon", 0.15, "none", False, 0, "Dish arrays and barracks.")]),
    ("lighthouse", "The Lighthouse", (38.0, 4.0, -30.0), ("NS", 600000, 0.002), "unclaimed", "anomaly", False,
     "A neutron star with a ring of ancient machinery that sends the Heartbeat: a pulse every few minutes on a line no natural star would use.",
     [P("Lamp", "artificial ring", 0.0, "none", False, 0, "A ring of alloy 4 km across, spun by the star; the source of the signal."),
      P("Lighthouse b", "dead rock", 0.3, "none", False, 0, "Cinders swept up by the pulsar wind.")]),
    ("eventide", "Eventide", (45.0, 8.0, -24.0), ("M4V", 3200, 0.02), "unclaimed", "uncharted", False,
     "A dim red dwarf past the Lighthouse; nobody has charted it.",
     [P("Eventide a", "unknown", 0.0, "unknown", False, 0, "Seen only as a dot.")]),
    ("sable", "Sable Reach", (42.0, -18.0, 12.0), ("K0III", 4700, 60.0), "korvath", "outpost", False,
     "Compact frontier giant-star system and a fleet muster point.",
     [P("Sable a", "hot rock", 1.1, "none", False, 0, "Forts."), P("Sable b", "gas giant", 2.2, "H2-He", False, 13, "Fuel.")]),
    ("ember_deep", "Ember Deep", (-40.0, -10.0, -22.0), ("DA", 12000, 0.003), "unclaimed", "uncharted", False,
     "A white dwarf with a belt of ash; an unvisited graveyard system.",
     [P("Ember b", "dead rock", 0.2, "none", False, 0, "Scorched.")]),
    ("quill", "Quill", (-35.0, 22.0, 15.0), ("G1V", 5900, 1.15), "freeports", "outpost", False,
     "Free port ring around a gold-yellow star; a long-haul crossroads.",
     [P("Quill Station", "orbital", 0.0, "habitat air", True, 0, "Markets, docks and a notary."), P("Quill b", "ocean-ice", 0.8, "thin N2-O2", False, 2, "Water source.")]),
    ("nadir", "Nadir", (-12.0, -30.0, -24.0), ("NS", 700000, 0.003), "unclaimed", "hazard", False,
     "A pulsar with hard radiation; lanes avoid it by 5 light-years.",
     [P("Nadir a", "scorched rock", 0.5, "none", False, 0, "Lit by the pulsar beam twice a second.")]),
    ("lyra_ferry", "Lyra Ferry", (20.0, 30.0, 18.0), ("A5V", 8100, 11.0), "collegium", "outpost", False,
     "Collegium relay hub high above the plane; its signal towers keep the subspace network alive.",
     [P("Ferry Station", "orbital", 0.0, "habitat air", True, 0, "Relay hub."), P("Lyra b", "ice world", 0.5, "none", False, 0, "Cold, quiet.")]),
    ("pale_harbor", "Pale Harbor", (5.0, -20.0, 30.0), ("G3V", 5700, 0.95), "commons", "outpost", False,
     "Thessaly settlement system on a pale-sanded world.",
     [P("Pale Harbor", "temperate rock", 0.97, "N2-O2, 20% O2", True, 1, "Salt flats, fisheries."), P("Pale b", "gas giant", 1.7, "H2-He", False, 5, "Skimming.")]),
    ("oriel", "Oriel", (-2.0, 25.0, -30.0), ("K2V", 5000, 0.4), "unclaimed", "uncharted", False,
     "An orange star north of the Lighthouse axis; a single survey flyby, no landing.",
     [P("Oriel a", "unknown", 0.0, "unknown", False, 0, "One probe photograph.")]),
    ("fennick", "Fennick", (-28.0, -4.0, 22.0), ("M0V", 3900, 0.11), "commons", "outpost", False,
     "Small Commons cooperative around a dim star.",
     [P("Fennick", "cold rock", 0.8, "N2-CO2", False, 1, "Greenhouse domes.")]),
    ("kestrel", "Kestrel Ridge", (14.0, 18.0, 4.0), ("G0V", 6000, 1.3), "collegium", "outpost", False,
     "Collegium field station on a high-albedo rocky world.",
     [P("Kestrel Ridge", "cold desert", 0.85, "thin CO2", False, 0, "Geology school.")]),
    ("anvil", "Anvil", (-18.0, -22.0, 10.0), ("K6V", 4200, 0.15), "freeports", "waypoint", False,
     "Salvage lane junction with a shipbreaker's yard.",
     [P("Anvil Yard", "orbital", 0.0, "habitat air", True, 0, "Breaker's yard.")]),
    ("dray", "Dray", (8.0, -10.0, -16.0), ("M3V", 3400, 0.03), "concord", "outpost", False,
     "Concord listening post on a tiny dim star.",
     [P("Dray Post", "airless moon", 0.1, "none", False, 0, "Radio telescopes.")]),
]

# lanes: (a, b, hazard 0-5); ly is computed from the coordinates
ROUTES = [
    ("tessara", "calloway", 0), ("tessara", "harrow", 0), ("tessara", "ostrava", 1), ("tessara", "vellum", 0), ("tessara", "lumen", 1),
    ("tessara", "brindle", 0), ("calloway", "sarrow", 1), ("calloway", "lumen", 1), ("calloway", "vellum", 1), ("calloway", "dray", 2),
    ("harrow", "brindle", 0), ("harrow", "vellum", 1), ("harrow", "dunmere", 1), ("ostrava", "brindle", 1), ("ostrava", "dray", 2),
    ("sarrow", "kithara", 1), ("sarrow", "halcyon", 1), ("sarrow", "lumen", 2), ("vellum", "kithara", 1), ("kithara", "halcyon", 1),
    ("kithara", "korvath_prime", 2), ("kithara", "ironwake", 3), ("halcyon", "ghalt", 2), ("halcyon", "veil", 3), ("halcyon", "lumen", 2),
    ("ghalt", "veil", 3), ("ghalt", "korvath_prime", 2), ("ghalt", "marrow", 2), ("ghalt", "ironwake", 3), ("veil", "tamsin", 4),
    ("veil", "marrow", 3), ("tamsin", "lighthouse", 3), ("tamsin", "marrow", 2), ("marrow", "lighthouse", 3), ("lighthouse", "eventide", 3),
    ("eventide", "marrow", 3),("korvath_prime", "sable", 3), ("brindle", "dunmere", 0), ("brindle", "cinder", 1),
    ("cinder", "orrin", 2), ("cinder", "dunmere", 2), ("dunmere", "fennick", 1), ("orrin", "quill", 2), ("brindle", "quill", 3),
    ("dunmere", "pale_harbor", 3), ("tessara", "pale_harbor", 3), ("kestrel", "lumen", 1), ("kestrel", "kithara", 2), ("kestrel", "lyra_ferry", 2),
    ("lumen", "oriel", 3), ("anvil", "dunmere", 2), ("anvil", "ostrava", 2), ("ostrava", "wyndham", 3),
    ("wyndham", "nadir", 4), ("wyndham", "ember_deep", 3), ("dray", "ironwake", 3), ("orrin", "fennick", 2), 
    ("kestrel", "halcyon", 2),
]

# the mission plan: (system, objective, survey_days, status)
WAYPOINTS = [
    ("tessara", "Depart Ring Dock 4 and begin Charter 7.", 3, "done"),
    ("calloway", "Shake-down jump; calibrate warp coils against relay Bellwether.", 6, "done"),
    ("sarrow", "Take on coolant and spares; survey the reaction-ice moon.", 9, "done"),
    ("kithara", "Collegium observatory: exchange star charts and receive the Heartbeat bearing.", 21, "done"),
    ("halcyon", "Deploy shuttles to the old lane relay buoy; hold position for signal analysis.", 14, "active"),
    ("ghalt", "Buy fuel and a passage permit from the Compact; decide whether to enter the Veil.", 5, "planned"),
    ("veil", "Navigate the dust: sensors and warp fields degrade, a hazard lane.", 4, "planned"),
    ("tamsin", "Set up a survey camp and listen to the Heartbeat from 12 light-years.", 18, "planned"),
    ("lighthouse", "Approach the Lamp and identify the source of the signal.", 30, "planned"),
    ("eventide", "Chart the uncharted red dwarf past the Lighthouse.", 10, "planned"),
    ("marrow", "Report to the Compact listening post and trade survey data.", 5, "planned"),
    ("sarrow", "Homeward leg: restock and refit at the frontier outpost.", 10, "planned"),
]

CURRENT = {"system": "halcyon", "status": "In orbit at Halcyon I, shuttles deployed to the relay buoy, listening to the Heartbeat.",
           "toward": "veil"}

TIMELINE = [
    (2105, "The first jump", "A Tessara test craft makes the first faster-than-light hop to Calloway; the lane is named the First Road."),
    (2142, "Founding of the Meridian Concord", "Four home systems sign the Meridian Accord: open lanes, shared charts and a common Survey Service."),
    (2171, "The Quiet Years begin", "Subspace relays fail along the northern lanes for eleven years; expeditions turn back and the frontier freezes."),
    (2183, "Orrery Collegium chartered", "Observatory worlds federate and begin the Great Atlas, a star chart open to every flag."),
    (2203, "Ashfall Free Ports unite", "Salvage guilds sign the Free Port Articles, agreeing on neutral docking rights."),
    (2218, "The Ironwake Dispute", "Two mining houses destroy a freighter fleet over a shattered world; the Korvath Compact forms to end the fighting."),
    (2240, "Thessaly Commons joins the lanes", "Agrarian colonies open their worlds to trade and begin shipping seed stock."),
    (2261, "The Heartbeat is first logged", "The Kithara observatory records a periodic radio pulse from the far north-east; it is catalogued and forgotten."),
    (2283, "Wayfinder class approved", "The Assembly funds six deep survey cruisers designed to stay out for years."),
    (2291, "Vesper Lantern commissioned", "The fourth Wayfinder cruiser leaves the yard at Ring Dock 4 and is handed to the Survey Service."),
    (2294, "Charter 7 begins", "Vesper Lantern departs Tessara for the frontier with 64 crew and two shuttles."),
    (2295, "Heartbeat noticed in flight", "Astrometrics picks the pulse out of the noise at Sarrow and links it to the Kithara records."),
    (2296, "The Veil decision", "Command orders the ship to approach the Lighthouse through the dust; the Compact objects."),
]

# stardate, role, author, title, text, room
LOGS = [
    ("41000.0", "captain", "Capt. Imara Teague", "Departure",
     "Cast off from Ring Dock 4 at the turn of the shift. Sixty-four crew aboard, hold full, shuttles checked. Charter 7 gives us four years and a "
     "short list: chart the lanes, keep the peace, and see what the old Kithara pulse really is. The bridge looks fine at night; the observation "
     "lounge is full of faces at the windows. Let us be good guests out there.", "bridge"),
    ("41001.4", "chief engineer", "Ch. Eng. Dov Ashkenazi", "Core first light",
     "Fusion core reached 72 per cent output on the first try and held. Coolant loops A and B are balanced to within one kelvin. Main engineering is loud "
     "and warm as it should be. The warp coils want a long break-in; I have scheduled the first jump at cruise, not a rush.", "eng"),
    ("41012.0", "quartermaster", "Qm. Lio Marchetti", "Manifest",
     "Cargo bay at 62 per cent, spares depot at 80. Dry rations 400 units, coolant canisters 12, fabricator feedstock 71 per cent. I counted the crates twice "
     "and then a third time because the captain asked for a fourth. The depot is organised by function, not by size; this will matter.", "cargo"),
    ("41031.2", "helm", "Lt. Ngozi Adebayo", "Calloway jump",
     "First jump to Calloway, 4.8 light-years, in 4.4 days at cruise. No drift, the coil temperatures stayed under 420 kelvin. Relay Bellwether answered "
     "the hail on the first try. The ship feels light in the hand; I like her.", "bridge"),
    ("41040.7", "hydroponics", "Spec. Wren Takahashi", "First harvest",
     "The wheat bed is at day 41 of 90 and the lettuce is ready. Pump B is humming a little flat but flow is fine. I have asked the galley to put tomato "
     "on every Friday, the crew deserve something red.", "hydro"),
    ("41048.3", "medical officer", "Dr. Amara Lindqvist", "Routine physicals",
     "Sixty-four physicals done. Everyone is healthy; two sprains from the gym and one case of vending-machine heartburn. Bio-bed 2 needed a reboot but the "
     "vitals trace is clean again. I will start a sleep survey next month because spaceflight always brings sleep trouble.", "medbay"),
    ("41061.0", "science officer", "Lt. Cdr. Anselm Okoro", "A pulse in the noise",
     "Astrometrics found a periodic radio pulse hiding under the pulsar chatter: a sharp burst every 11 minutes 40 seconds from a bearing near the far "
     "north-east. It is too regular for a star and too slow for a pulsar. The Kithara records have the same pulse. I am calling it the Heartbeat, and "
     "the name is already on the whiteboard.", "astro"),
    ("41066.5", "communications", "Lt. Jun Park", "Not a natural signal",
     "I ran the pulse through every filter we have. It carries a faint second layer: a repeated string of twelve prime numbers. The Concord archive and "
     "the Collegium both say they have never seen it before. I did not tell the mess hall; I told the captain.", "comms"),
    ("41079.9", "security chief", "Cmdr. Tomas Reyes", "Armory and brig",
     "Armory inventoried and locked. The brig has been empty since departure and the cells hold spare mattresses. Doors to both are on the red alert list. "
     "I would like the crew to hold a drill in the first month at the stair towers so that nobody learns the way during an emergency.", "secoff"),
    ("41090.2", "captain", "Capt. Imara Teague", "Secondary objective",
     "Command signs off: the Heartbeat is added to the charter as a secondary objective. We keep to the survey plan, but every jump will bend a little "
     "toward the north-east. I told the crew in the mess over breakfast; they asked more questions than the Assembly did.", "mess"),
    ("41104.0", "chief engineer", "Ch. Eng. Dov Ashkenazi", "Sarrow coolant swap",
     "At Sarrow we swapped the coolant and took twenty tonnes of reaction ice. Coil C runs two kelvin warmer than the rest and I do not know why. "
     "The power distribution room is quiet; the battery bank passed its endurance test at 12.4 megawatt-hours.", "aux"),
    ("41117.3", "hydroponics", "Spec. Wren Takahashi", "Pump B and the lettuce",
     "Pump B failed overnight and the lettuce bolted. The garden is at 14 kilograms a day without it. Shop made a replacement impeller from spares, fabricator "
     "time two hours; the new part is whiter than the old one and looks smug about it.", "hydro"),
    ("41125.8", "medical officer", "Dr. Amara Lindqvist", "Sleep survey",
     "Eleven crew report the same restless sleep and a shared dream of a long dock with no ship in it. All eleven also work the astrometrics watch. Nothing "
     "is wrong with them. I am not saying the pulse can reach into a dream; I am saying I have the list.", "medbay"),
    ("41139.6", "helm", "Lt. Ngozi Adebayo", "Kithara",
     "Kithara is beautiful from orbit: twelve dishes on a ring and an ocean world below. The Collegium astronomers shared eleven years of the Heartbeat "
     "and a triangulation: the source lies 48 light-years out at the edge of the Veil. We copied everything into the ship's computer.", "bridge"),
    ("41150.0", "science officer", "Lt. Cdr. Anselm Okoro", "The pulse reacts",
     "The pulse changes shape when we change course. Not much, but it is real. At Kithara the burst was a clean square; at Halcyon the edges are "
     "rounded. It behaves like a lighthouse that is learning where the ship is. The spectrograph in the science lab agrees with astrometrics.", "sci"),
    ("41158.2", "security chief", "Cmdr. Tomas Reyes", "A shadow at the gate",
     "Cameras and sensors both show a dark ship holding a long way off while the shuttles worked the relay buoy. No hail, no transponder. The Compact flies "
     "no-transponder scouts; I would put money on them. The hangar force field is up and I want the second shuttle on standby.", "secoff"),
    ("41170.4", "quartermaster", "Qm. Lio Marchetti", "Rations",
     "We have 41 days of oxygen reserve and 120 days of fresh stores because the garden is pulling its weight. I have asked the galley to make soup on the "
     "cold days. Nobody has complained about the vending machines yet, which means they are not using them.", "galley"),
    ("41181.9", "captain", "Capt. Imara Teague", "Wardroom",
     "Held the officers' conference in the wardroom. Opinions: the engineers want to go home, the scientists want to go faster, the security chief wants "
     "the armory open. Nobody wants to be first through the Veil. I said we will decide at Halcyon, with the data.", "conf"),
    ("41190.3", "chief engineer", "Ch. Eng. Dov Ashkenazi", "The core breathes",
     "Core load oscillates with a period of 11 minutes 40 seconds. I checked it three times, then asked the computer core to check it. The fusion reactor "
     "is pulling the Heartbeat through its power electronics, a few parts per million, but it is there. Warp harmonics lock to it too.", "core"),
    ("41198.7", "flight deck chief", "Chief Petty Officer Mara Ilves", "Relay buoy",
     "Shuttle One reached the old relay buoy at Halcyon. It is dead, a century old, but its housing carries an engraved sequence of dots: the same twelve primes "
     "as the pulse. Somebody engraved it before the Concord existed. Both shuttles are back in the hangar, field on, bay door cycled.", "hangar"),
    ("41207.1", "communications", "Lt. Jun Park", "A schedule",
     "The prime string is not a message, it is a timetable: the pulse is a ferry schedule, with a column of sector coordinates under it. The coordinates "
     "all lie on one line through the Veil. A ferry for what, I do not know. The Kithara observatory sent confirmation and a lot of excitement.", "comms"),
    ("41213.5", "science officer", "Lt. Cdr. Anselm Okoro", "The countdown",
     "The period is getting shorter: 11:40, then 11:12, then 10:31. Extrapolated, the burst rate reaches continuous in about 280 days. I do not know if a "
     "continuous signal is a call, a warning or a door. Please do not tell anyone I said door.", "astro"),
    ("41221.0", "medical officer", "Dr. Amara Lindqvist", "The dream stops",
     "The eleven sleepers dream no more after the captain had the astrometrics watch change over; their sleep is normal and nobody is afraid. The dock in the "
     "dream was empty because the dock was waiting for us. That is a ridiculous sentence and I am leaving it in.", "medbay"),
    ("41226.8", "captain", "Capt. Imara Teague", "The Compact objects",
     "A formal message from the Korvath Compact asks us to stay out of the Veil. Concord Survey Command replies that the charter stands. I read both to the "
     "bridge crew and then asked for the course to Ghalt, where we can buy a permit and a few more days of thought.", "ready"),
    ("41230.0", "helm", "Lt. Ngozi Adebayo", "Plotting the Veil",
     "Plotted three routes through the dust. The Veil lane is hazard 3 on the charts; sensors lose range, warp coils run hot and the lane is thin "
     "and short on room. I prefer the Ghalt route even though it is longer. I would like the second shuttle to scout ahead.", "bridge"),
    ("41232.2", "hydroponics", "Spec. Wren Takahashi", "Spirals",
     "The new seed batch from Kithara grows in spirals instead of rows. The same pump, the same light. I measured it: the spiral turns once every 11 minutes "
     "40 seconds in the time-lapse. The lettuce is also delicious, which is the only normal thing here.", "hydro"),
    ("41233.6", "security chief", "Cmdr. Tomas Reyes", "Lockdown drill",
     "Ran a lockdown drill in all decks, the armory and brig sealed, stair towers open as designed. Doors responded in 2.1 seconds. The crew moved well; the "
     "dark ship has not been seen since Halcyon, which worries me more than seeing it.", "secoff"),
    ("41234.5", "science officer", "Lt. Cdr. Anselm Okoro", "Six minutes",
     "The Heartbeat now repeats every six minutes, down from eleven. It has also started to carry something new under the primes: a short phrase, again and "
     "again, that the computer says is a direction and a name. The name is ours. It says Vesper Lantern. I have asked the captain to come to astrometrics.", "astro"),
]

DATAPADS = [
    ("founding", "The Founding of the Concord",
     "In CY 2142 four home systems, tired of competing lane tolls, signed the Meridian Accord: open lanes, a shared chart office and a Survey Service "
     "whose ships answer to the Assembly and nobody else. The first Assembly met in a repurposed freight hangar at Lantern Hill and wrote the Accord on "
     "paper, so that nobody could say it had been overwritten."),
    ("lane_courtesy", "Lane Courtesy",
     "Lane law is short. Keep right. Hail at the gate. Do not sit in the lane's throat. Give way to anything that is slower or on fire. A ship that "
     "breaks lane courtesy at Ghalt pays the toll twice and apologises in public. The Free Ports add a fifth rule: tip the tugs."),
    ("lighthouse_rumours", "Lighthouse Rumours",
     "Crew rumours about the Lighthouse, in order of popularity: it is a navigation beacon; it is a trap; it is a tomb; it is a lighthouse. A cynical "
     "midshipman wrote that the real rumour is that nobody has ever gone there and come back with an opinion."),
    ("wayfinder", "The Wayfinder Class",
     "Six Wayfinder cruisers were built between 2288 and 2297 at Ring Dock 4. They have a 64-person crew, three decks, a stern hangar for two shuttles and "
     "an unusually large hydroponics garden. The bridge overhangs the bow so that the helm can see the lane ahead; engineers still say the view is wasted."),
    ("korvath_customs", "Korvath Reach Customs",
     "The Compact trades in iron, fuel and favours. A permit from Ghalt costs forty credits and a signed promise not to survey the veins. A visitor who asks "
     "about the veins anyway is invited to a long dinner. Eat the soup; it is excellent."),
    ("garden_notes", "Notes from the Garden",
     "Hydroponics runs on a 16-hour light cycle with a red-heavy spectrum for fruit and a blue-heavy one for leaf. Every bed has a name chosen by the "
     "last person to harvest it. Bed 3 is called Gerald. Nobody knows why."),
    ("quiet_years", "The Quiet Years",
     "For eleven years after CY 2171 the northern subspace relays went silent one by one. Expeditions turned back, the frontier froze, and the "
     "Collegium began to keep its own copy of every chart. The cause was never found; the relays woke up in 2182 with no explanation."),
    ("stardates", "A Short Guide to Stardates",
     "Ship stardates count one unit per ship day; the digits after the point are tenths of a day. Mission day equals stardate minus 41000. The chart office "
     "keeps its own calendar in Concord years; do not confuse them in a log or you will be asked, politely, to explain."),
    ("etiquette", "Shipboard Etiquette",
     "Eat in the mess. Sleep in your cabin. Ask before you open a hatch that is not yours. When a door is locked it is locked for a reason, and it will "
     "open again when someone with the right to open it says so. Nothing in the galley is secret, but the soup is."),
    ("orrery_charts", "The Orrery Charts",
     "The Collegium's Great Atlas has 41,000 pages and a single rule: no page is final. Every chart carries an uncertainty in light-years and the name of "
     "the person who last corrected it. Kithara's chart of the Heartbeat has seven names on it."),
    ("ferrymen", "The Ferrymen Fragment",
     "A dealer at Cinder once sold a metal tag engraved with twelve dots and a line of text nobody could read. The tag, he said, came from a ship that "
     "traded along a line of stars before the Concord existed. He called the ship's owners the Ferrymen, and when he was asked what they ferried, he said: the lost."),
]

GLOSSARY = [
    ("Meridian Concord", "The union of eleven systems around Tessara that fields the Survey Service."),
    ("Survey Service", "The Concord's exploration branch: charts lanes, makes first contact, keeps the peace on the frontier."),
    ("Charter", "A ship's mission order. Charter 7 covers four years of the Veil frontier."),
    ("Stardate", "Ship day count, one unit per day; mission day is stardate minus 41000."),
    ("Warp factor", "Dimensionless FTL speed setting; cruise is warp 5, top is warp 8."),
    ("ly", "Light-year, about 9.46 trillion kilometres."),
    ("Lane", "A charted jump route between two systems with a distance and a hazard rating."),
    ("Hazard rating", "0 (open road) to 5 (do not enter): dust, radiation, patrols and bad charts all count."),
    ("Heartbeat", "The repeating radio pulse that comes from the Lighthouse, first logged at Kithara in 2261."),
    ("The Lamp", "The ring of ancient machinery around the Lighthouse neutron star."),
    ("Ring Dock", "An orbital shipyard of Tessara; Dock 4 built Vesper Lantern."),
    ("Wayfinder class", "Concord deep survey cruiser class: 64 crew, three decks, stern hangar."),
    ("Orrery Collegium", "The academic league of observatory worlds that keeps the Great Atlas."),
    ("Free Ports", "Neutral trade stations of the Ashfall guilds."),
    ("Compact", "Short for the Korvath Reach Compact."),
    ("Veil", "The dust nebula around a young blue star; sensor and warp-field hazard."),
    ("Bio-bed", "Medical bed with built-in vitals monitoring and scanner."),
    ("Astrometrics", "The ship's astronomical measurement room on Deck 1."),
    ("Credits (cr)", "Concord money; one credit buys a cup of tea on Anchorage."),
]

ROOM_IDS_USED = sorted({l[5] for l in LOGS})
