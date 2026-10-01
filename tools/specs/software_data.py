"""Content of the software specification: one record per screen application (see docs/SOFTWARE_SPEC.md).

Pure data.  tools/specs/gen_software.py renders it to docs/SOFTWARE_SPEC.md and godot/data/software.json.
"""

# existing screen textures (godot/textures/screens/*.png) -> application
TEXTURE_MAP = {
    "radar": "sensors", "waveform": "science", "graph": "atmosphere", "text": "computer", "starmap": "starmap",
    "schematic": "deckplan", "bars": "diagnostics", "warp": "warp", "vitals": "medical", "power": "power", "nav": "nav",
    "alert": "alert", "tactical": "tactical", "systems": "engineering", "lifesigns": "medical", "comm": "comms",
    "medical": "medical", "periodic": "science", "hazard": "lifesupport", "diagnostic": "diagnostics", "globe": "holo",
}

# future textures: a texture name starting with the prefix opens the app (longest prefix wins).  The "scr_" prefix is
# optional: "scr_reactor_core" and "reactor_core" both match "reactor".
TEXTURE_PREFIX_MAP = {
    "scr_starmap": "starmap", "scr_map": "starmap", "scr_chart": "starmap", "scr_nav": "nav", "scr_helm": "nav",
    "scr_radar": "sensors", "scr_sensor": "sensors", "scr_scan": "sensors", "scr_tactical": "tactical",
    "scr_shield": "tactical", "scr_weapon": "tactical", "scr_warp": "warp", "scr_ftl": "warp", "scr_reactor": "reactor",
    "scr_fusion": "reactor", "scr_core": "reactor", "scr_power": "power", "scr_grid": "power", "scr_breaker": "power",
    "scr_systems": "engineering", "scr_damage": "engineering", "scr_eng": "engineering", "scr_life": "lifesupport",
    "scr_o2": "lifesupport", "scr_scrub": "lifesupport", "scr_hydro": "hydroponics", "scr_crop": "hydroponics",
    "scr_plant": "hydroponics", "scr_med": "medical", "scr_vital": "medical", "scr_bio": "medical", "scr_sci": "science",
    "scr_spectro": "science", "scr_lab": "science", "scr_periodic": "science", "scr_comm": "comms", "scr_radio": "comms",
    "scr_sec": "security", "scr_door": "security", "scr_cctv": "security", "scr_cam": "security", "scr_cargo": "cargo",
    "scr_inventory": "cargo", "scr_manifest": "cargo", "scr_fab": "fabricator", "scr_print": "fabricator",
    "scr_galley": "galley", "scr_menu": "galley", "scr_food": "galley", "scr_drink": "galley", "scr_replicator": "galley",
    "scr_vend": "vending", "scr_shop": "vending", "scr_alert": "alert", "scr_term": "computer", "scr_text": "computer",
    "scr_console": "computer", "scr_deck": "deckplan", "scr_plan": "deckplan", "scr_locator": "deckplan",
    "scr_log": "logbook", "scr_journal": "logbook", "scr_roster": "roster", "scr_duty": "roster", "scr_notice": "roster",
    "scr_clock": "clock", "scr_time": "clock", "scr_atmo": "atmosphere", "scr_env": "atmosphere", "scr_hangar": "docking",
    "scr_dock": "docking", "scr_bay": "docking", "scr_diag": "diagnostics", "scr_bars": "diagnostics",
    "scr_datapad": "datapad", "scr_library": "datapad", "scr_book": "datapad", "scr_holo": "holo", "scr_globe": "holo",
    "scr_hologram": "holo",
}

# model category -> application used when the model has a screen whose texture is unknown (or no GLB to scan)
CATEGORY_APP = {
    "console": "nav", "display": "diagnostics", "terminal": "computer", "controlpanel": "engineering", "holo": "holo",
    "vending": "vending", "medscanner": "medical", "medbed": "medical", "analyzer": "science", "sciinstrument": "science",
    "instrument": "sensors", "commsunit": "comms", "clock": "clock", "noticeboard": "roster", "camera": "security",
    "forcefield": "docking", "scrubber": "lifesupport", "reactor": "reactor", "generator": "power", "capacitor": "power",
    "cell": "power", "junction": "power", "router": "comms", "antenna": "comms", "planter": "hydroponics",
    "microscope": "science", "telescope": "starmap", "gym": "roster", "cryo": "medical", "surgical": "medical",
    "weaponrack": "tactical", "loader": "cargo", "pallet": "cargo", "crate": "cargo", "craft": "docking",
    "watertank": "lifesupport", "tank": "lifesupport", "galley": "galley", "cleaningbot": "diagnostics",
    "turbine": "engineering", "particle": "science", "coil": "warp", "sign": "deckplan", "specimen": "science",
}

THEME = {
    "bg": "#070b12", "panel": "#0d1522", "panel_hi": "#14213a", "line": "#2a4266", "text": "#d6e4f5", "dim": "#7d93b2",
    "accent": "#42c8ff", "accent2": "#7affc6", "ok": "#4be08a", "warn": "#ffc247", "crit": "#ff4d5e", "info": "#6aa8ff",
    "alert_green": "#2fd37a", "alert_yellow": "#ffc247", "alert_red": "#ff3b4a",
}

CATEGORIES = [
    ("navigation", "Navigation and cartography"), ("engineering", "Engineering and power"),
    ("operations", "Operations and defence"), ("life", "Life support, medical and hydroponics"),
    ("science", "Science and information"), ("services", "Crew services"), ("systems", "Ship systems and administration"),
]


def app(id, title, category, purpose, users, rooms, hosts, textures, wireframe, widgets, data, interactions, alarms, rate,
        effects, perf, accept, extra=None):
    return {"id": id, "title": title, "category": category, "purpose": purpose, "users": users, "rooms": rooms,
            "hosts": hosts, "textures": textures, "wireframe": wireframe.strip("\n"), "widgets": widgets, "data": data,
            "interactions": interactions, "alarms": alarms, "rate": rate, "effects": effects, "perf": perf,
            "accept": accept, "extra": extra or []}


APPS = [
    app("starmap", "Star Cartography", "navigation",
        "A rotatable 3D chart of every system in lore.json: faction colours, jump lanes, the ship's position and the mission plan. "
        "The crew can inspect a system, plot a route along lanes and commit a destination to the helm.",
        "Navigator, helm, captain, science officer, anyone curious.",
        ["bridge", "astro", "ready", "conf", "lounge"], ["console", "display", "holo", "telescope", "terminal"], ["starmap"],
        """
+--------------------------------------------------------------+
| STAR CARTOGRAPHY      stardate 41234.5      [ALERT: GREEN]   |
+------------------------------------+-------------------------+
|                                    | SYSTEM  Kestrel's Rest  |
|        .  *   .                    | class G2V  5772 K  1.0 L|
|    *     [ship]---*                 | faction: Concord        |
|        .      \\    *   .            | planets (3) ...         |
|   *    .       *  <hover label>     | [ PLOT ROUTE ] [ JUMP ] |
|                                    | route: 3 hops 21.4 ly   |
+------------------------------------+ ETA 18.6 d  hazard 2    |
| [Filter: faction v] [Labels] [Lanes] [Reset view] [Search __] |
+--------------------------------------------------------------+
""",
        ["3D chart viewport (SubViewport, orbit camera, one sprite per system sized by luminosity, coloured by faction, ring per kind)",
         "Jump lanes drawn as lines, colour by hazard 0-5", "Ship marker with heading arrow (current.heading)",
         "Detail panel (star data, planet list with gravity / atmosphere / habitable flags, discovery notes)",
         "Route planner: shortest hazard-weighted path along routes, total ly, ETA days, maximum hazard",
         "Filter bar: faction, kind, visited only; search box", "Mission plan strip: waypoints with done/active/planned status"],
        ["lore.json: systems, routes, factions, waypoints, current, ship.ly_per_day_at_cruise", "ShipState.destination, ShipState.position_system",
         "ShipState.warp (to disable JUMP while already in transit)"],
        ["Left drag orbit; wheel zoom; middle drag pan; click a star selects; double click centres", "Arrow keys orbit, +/- zoom, Space recentre on ship",
         "P plot route to the selected system, Enter / J commit the jump (opens a confirm dialog), L toggle labels, F cycle faction filter",
         "Hover shows a tooltip with name and distance from the ship"],
        ["System unreachable (no lane path): PLOT shows 'NO LANE' in warn colour", "Hazard >= 4 on a leg: route text turns crit and the commit dialog requires a second confirmation",
         "Warp field offline (ShipState.warp.online false): JUMP disabled with the reason on the button"],
        "Chart redraws on input only; ship marker and clock 1 Hz; lore data loaded once.",
        ["Setting a destination writes ShipState.destination (system id) and ShipState.route (list of system ids); the nav app shows the new course",
         "Committing the jump starts the in-world transit simulation (ShipState.warp.engaged = true)"],
        "<= 128 sprites + 150 lines; one SubViewport; no per-frame allocation.",
        ["Opening the app with the default lore shows >= 28 stars and the ship marker at current.system",
         "Selecting any system shows its planets; PLOT to a connected system gives ly equal to the summed lane distances (1%)",
         "COMMIT sets ShipState.destination and nav shows it"],
        ),
    app("nav", "Helm and Navigation", "navigation",
        "The pilot's view: current course, speed, heading, the ETA to the next waypoint and the destination selector. It is the control "
        "surface for ShipState.destination and for the throttle (impulse / cruise / top warp).",
        "Helm officer, captain.", ["bridge", "hangar"], ["console", "display", "controlpanel"], ["nav"],
        """
+--------------------------------------------------------------+
| HELM & NAVIGATION                                  IN ORBIT   |
+----------------------+---------------------+-----------------+
|   HEADING            |   SPEED             |  NEXT WAYPOINT  |
|     ( N ^ )  127.4   |   [=====>   ] 6.0  |  Halcyon Gate   |
|   compass rose       |   warp 6.0 / 9.2    |  dist 7.3 ly    |
|                      |   0.82 ly/day       |  ETA 8.9 days   |
+----------------------+---------------------+-----------------+
| DESTINATION [Halcyon Gate v]  [SET COURSE] [ALL STOP] [ORBIT] |
| plan: 1 Kestrel > 2 Halcyon > 3 Veil   throttle [-][+]        |
+--------------------------------------------------------------+
""",
        ["Compass rose with heading numerals (from current.heading)", "Speed gauge with warp factor and ly/day", "Next waypoint card (system, distance, ETA)",
         "Destination dropdown (systems with a lane path), SET COURSE / ALL STOP / ORBIT buttons", "Throttle slider 0..top_warp",
         "Mission plan list with status chips"],
        ["lore.json: ship.cruise_warp, top_warp, ly_per_day_at_cruise, waypoints, routes", "ShipState.destination, ShipState.warp.factor, ShipState.alert"],
        ["Dropdown + Enter selects destination; Space toggles ALL STOP; Up/Down or W/S change throttle in 0.5 steps; Tab cycles widgets"],
        ["Throttle above top_warp: clamped with a beep", "Reactor output below 40 %: warp is capped (see reactor)", "No destination: ETA shows '--'"],
        "1 Hz (ETA, distance); gauges animate at 30 Hz from interpolated values.",
        ["Writes ShipState.destination and ShipState.throttle; ETA uses the warp speed model of the cross-cutting section"],
        "< 0.5 ms per frame.",
        ["ETA equals the lore ETA when the throttle is at cruise", "ALL STOP sets the throttle to 0 and the ETA shows '--'", "A destination chosen in starmap is preselected"],
        ),
    app("sensors", "Long-Range Sensors", "operations",
        "A radar-style sweep of the neighbourhood: contacts (ships, anomalies, debris) with bearing, range and classification; the crew can lock a contact and request a deep scan.",
        "Science officer, tactical officer, helm.", ["bridge", "astro", "comms"], ["console", "display", "instrument", "antenna"], ["radar"],
        """
+--------------------------------------------------------------+
| LONG-RANGE SENSORS   range [ 10 ly v ]   mode [PASSIVE|ACTIVE]|
+----------------------------+---------------------------------+
|          N                 | CONTACTS                        |
|      .-""-.    o C-04      | id    class     brg   rng  stat |
|     /   +   \\   [ship]     | C-01  anomaly   041   3.1  ?    |
|    | o C-01   |            | C-02  freighter 212   0.4  FRND |
|     \\    .   /  sweep ->   | C-04  unknown   300   5.9  ??   |
|      '-....-'              | [LOCK] [DEEP SCAN] [HAIL]       |
+----------------------------+---------------------------------+
""",
        ["Radar scope: rotating sweep line (1 revolution per 4 s), fading blips", "Range selector (1, 10, 50 ly)", "Contact table sorted by range",
         "Contact detail with classification confidence bar", "LOCK / DEEP SCAN / HAIL buttons"],
        ["Contacts generated deterministically from lore.json systems within the range of the current system plus a seeded set of local contacts", "ShipState.power (sensors share; reduces range when under-powered)"],
        ["Mouse click a blip or table row; Tab cycles contacts; R changes range; L lock; D deep scan (5 s progress bar); H hail (opens comms with the contact)"],
        ["Sensors unpowered: static noise and 'SENSORS OFFLINE'", "Hostile contact with shields down: row turns crit"],
        "Sweep 30 Hz; contact positions 2 Hz.",
        ["LOCK sets ShipState.target; DEEP SCAN may reveal text appended to the contact (lore anomaly notes); HAIL pre-selects the contact in comms"],
        "<= 64 blips; drawn with canvas items, no textures.",
        ["Range change rescales blips", "Unpowered sensors show the offline state", "Deep scan completes in 5 s and updates the classification"],
        ),
    app("tactical", "Tactical and Shields", "operations",
        "Shield and weapon management with a ship silhouette showing four shield quadrants and hull integrity. Under the exploration charter the ship is lightly armed; the app is used for debris shielding and defence drills.",
        "Tactical officer, security chief, captain.", ["bridge", "secoff", "armory"], ["console", "display", "weaponrack", "controlpanel"], ["tactical"],
        """
+--------------------------------------------------------------+
| TACTICAL & SHIELDS                      ALERT [ YELLOW ]      |
+-----------------------------+--------------------------------+
|      FWD 82%                | SHIELDS  [ON]  power 40%       |
|    .-------.                | quadrant  fwd  port stbd aft   |
| P  | ship  |  S             | strength  82   64   71   90    |
| 64 | top   | 71             | [REDISTRIBUTE] [RAISE][LOWER]  |
|    '-------'                | POINT DEFENCE  2/2 ready       |
|      AFT 90%                | HULL 100%   [RED ALERT]        |
+-----------------------------+--------------------------------+
""",
        ["Ship silhouette with four shield arcs", "Shield toggle and power slider", "Quadrant strength bars", "Point defence status", "Hull integrity bar", "Alert button (raises alert)"],
        ["ShipState.shields, ShipState.hull, ShipState.alert", "specs.json of installed weaponrack / forcefield models for numbers"],
        ["S toggles shields; 1-4 select quadrant; +/- move power into quadrant; R redistributes evenly; A cycles alert level (red needs a confirm)"],
        ["Shields below 25 %: bar crit and the console beeps once", "No power: all bars grey"],
        "10 Hz.",
        ["Raising shields draws power (see power); alert red changes the ship lighting"],
        "< 0.5 ms per frame.",
        ["Toggling shields flips ShipState.shields.on and the bar colours", "Selecting alert red sets ShipState.alert = red"],
        ),
    app("warp", "Warp Field Control", "engineering",
        "Controls the warp field generator (the coil, particle and turbine machines): field strength, nacelle alignment, coil temperatures and the pre-jump checklist.",
        "Chief engineer, helm.", ["eng", "bridge"], ["coil", "particle", "console", "display", "turbine"], ["warp"],
        """
+--------------------------------------------------------------+
| WARP FIELD CONTROL                          FIELD: STANDBY    |
+----------------------+---------------------------------------+
| COIL TEMPS           | FIELD STRENGTH  [==========    ] 62 % |
| A 412K  B 409K       | ALIGNMENT       +0.012 mrad  OK        |
| C 418K  D 420K       | PLASMA FLOW     [=======       ]      |
|                      | CHECKLIST  [x]core [x]coils [ ]nav     |
| [ENGAGE] [STANDBY]   | warp factor target 6.0  [-] [+]        |
+----------------------+---------------------------------------+
""",
        ["4 coil temperature gauges", "Field strength bar and warp factor target", "Alignment readout", "Plasma flow bar", "Pre-jump checklist with live pass/fail", "ENGAGE / STANDBY buttons"],
        ["ShipState.warp (online, factor, field), ShipState.reactor.output_pct, ShipState.power.warp", "specs.json warp coil power figures"],
        ["Enter or the ENGAGE button when the checklist is green; +/- warp factor; S standby; Tab through widgets"],
        ["A red checklist item blocks ENGAGE and shows the cause", "Coil temperature > 480 K: warn; > 520 K: crit and automatic standby"],
        "5 Hz.", ["ENGAGE needs reactor output >= 40 %; sets ShipState.warp.online and enables the starmap JUMP; draws warp power from the power bus"],
        "< 0.3 ms per frame.",
        ["ENGAGE fails with the reactor offline and states why", "STANDBY returns the field to 0"],
        ),
    app("reactor", "Fusion Core Control", "engineering",
        "Operates the main fusion core: output, fuel (deuterium / helium-3), containment, coolant loops and SCRAM.",
        "Chief engineer, engineering technicians.", ["eng", "aux"], ["reactor", "generator", "capacitor", "console", "controlpanel"], [],
        """
+--------------------------------------------------------------+
| FUSION CORE CONTROL       CORE STATE: RUNNING   ONLINE 41d   |
+--------------------+-----------------------------------------+
| OUTPUT 72 %        | CONTAINMENT  99.97 %   plasma 1.4e8 K   |
|  ( arc gauge )     | FUEL D2 81 %  He3 76 %                  |
|  96 MW / 134 MW    | COOLANT A 311K  B 309K  flow ok         |
| [THROTTLE -][+]    | [SCRAM]  [RESTART]  [BYPASS SAFETIES]   |
+--------------------+-----------------------------------------+
""",
        ["Arc output gauge in % and MW", "Containment, plasma temperature, fuel and coolant readouts", "Throttle buttons", "SCRAM (guarded button: click twice)", "Event log of the last 20 core events"],
        ["ShipState.reactor (running, output_pct, fuel, containment)", "specs.json: output of the reactor models installed in ship.json (sum = rated MW)"],
        ["Up/Down arrows throttle in 5 % steps; X (twice within 2 s) SCRAM; R restart (10 s spool-up bar)"],
        ["Containment < 98 %: warn; < 95 %: crit and automatic SCRAM", "SCRAM: lights flicker to emergency power; the battery endurance countdown shows on the power app"],
        "10 Hz.", ["Output sets the generation figure in ShipState.power.supply; SCRAM sets reactor.running false, which drops ship power to batteries (emergency lights)"],
        "< 0.5 ms per frame.",
        ["Throttle changes the generation visible in the power app", "SCRAM puts the ship on battery"],
        ),
    app("power", "Power Distribution", "engineering",
        "Single-line view of the ship's electrical network: generation, buses, per-deck and per-department breakers, loads and battery state, from the machine datasheets.",
        "Chief engineer, damage control teams.", ["aux", "eng", "bridge"], ["junction", "capacitor", "cell", "controlpanel", "console", "display"], ["power"],
        """
+--------------------------------------------------------------+
| POWER DISTRIBUTION      supply 96.0 MW  load 61.2 MW  +35 MW  |
+-----------------------+--------------------------------------+
| [CORE]--[MAIN BUS A]  | DECK 1 command   [x] 6.2 MW  ----    |
|         |-[D1] [D2]   | DECK 2 habitat   [x] 14.8 MW ======  |
|         |-[D3] [HAN]  | DECK 3 engineer. [x] 22.5 MW ======= |
| [BATT 12.4 MWh 92%]   | warp coils       [ ] off              |
+-----------------------+  [SHED NON-ESSENTIAL] [RESET ALL]    |
+--------------------------------------------------------------+
""",
        ["Single-line diagram (core, buses, breakers)", "Per-deck and per-department load bars with typical and peak markers", "Breaker toggles", "Battery gauge with endurance time", "Shed non-essential button"],
        ["specs.json (power per model) aggregated per room by ship.json", "docs/SHIP_SPEC.md budget numbers (same aggregation)", "ShipState.power"],
        ["Click or Enter toggles a breaker; S sheds non-essential loads (lighting 50 %, galley, recreation, vending off); R resets"],
        ["Load > supply: bus bars red and a brown-out timer starts; load > 90 % of supply: warn", "Opening the life support breaker: confirm dialog"],
        "2 Hz.", ["A tripped deck breaker turns off that deck's real lights (ShipState.deck_power[deck] = false); shed mode dims lights to 50 %"],
        "< 0.5 ms per frame.",
        ["Opening the deck 2 breaker darkens deck 2", "Totals equal the SHIP_SPEC power budget (1%)"],
        ),
    app("engineering", "Damage Control and Systems Status", "engineering",
        "Status board of every ship system with health bars, active faults and repair tasking; shows which rooms are affected.",
        "Chief engineer, damage control, captain.", ["eng", "bridge", "shop"], ["console", "display", "controlpanel", "terminal"], ["systems"],
        """
+--------------------------------------------------------------+
| SYSTEMS STATUS                            3 FAULTS  0 CRIT    |
+---------------------------+----------------------------------+
| Propulsion   [========] 98| FAULTS                           |
| Power        [=======-] 91| F-12 Hydroponics pump B  WARN    |
| Life support [========]100| F-14 Cargo door slow     INFO    |
| Sensors      [======--] 78| [ASSIGN TEAM] [REPAIR] [IGNORE]  |
| Comms        [========] 99| rooms affected: hydro            |
+---------------------------+----------------------------------+
""",
        ["System health list with bars", "Fault list with severity chips", "Repair tasking buttons", "Affected rooms summary"],
        ["ShipState.systems (health 0..100), faults generated deterministically from the ship seed and the ship.json room list", "lore.json logs for flavour"],
        ["Up/Down selects, Enter opens fault details, R starts a repair (10 s progress bar)"],
        ["Health < 60 warn, < 30 crit", "Crit faults raise alert yellow automatically"],
        "1 Hz.", ["Repair completion raises the system health and may clear the fault of the affected room"],
        "< 0.3 ms per frame.",
        ["The fault list is never empty at start (2-4 minor faults)", "A repair completes and the health bar rises"],
        ),
    app("lifesupport", "Life Support", "life",
        "Per-deck atmosphere (O2, CO2, temperature, pressure), scrubber and water-recycler status and the consumables budget.",
        "Chief engineer, environmental technician.", ["life", "eng"], ["scrubber", "watertank", "tank", "console", "display", "controlpanel"], ["hazard"],
        """
+--------------------------------------------------------------+
| LIFE SUPPORT                              O2 reserve 41 d     |
+-------------+-------------+-------------+--------------------+
| DECK 1      | DECK 2      | DECK 3      | SCRUBBERS 9/10 ok   |
| O2 20.9%    | O2 20.8%    | O2 20.7%    | water recycle 96%   |
| CO2 0.04%   | CO2 0.06%   | CO2 0.05%   | [BOOST][FLUSH]      |
| 21.5C 101kPa| 22.0C 101kPa| 23.1C 101kPa| humidity 48%        |
+-------------+-------------+-------------+--------------------+
""",
        ["Per-deck tile (iterate decks[] of ship.json) with four readouts and trend arrows", "Scrubber list with status", "Water recycler gauge", "Reserves countdown (O2, water, food days)", "BOOST / FLUSH buttons"],
        ["docs/SHIP_SPEC.md life support budget; specs.json scrubber / tank models", "ShipState.atmosphere[deck]", "ShipState.crew_count"],
        ["Tab between tiles, B boosts scrubbers (+30 % power), F flushes a deck (vents for 10 s)"],
        ["CO2 > 0.5 %: warn; > 1 %: crit and alert yellow", "Pressure < 90 kPa: crit; hatch seal advice"],
        "1 Hz.", ["Boost draws power; atmosphere values feed the atmosphere app; crit values raise the alert level"],
        "< 0.3 ms per frame.",
        ["Boost lowers CO2 over time", "Every deck of ship.json is shown"],
        ),
    app("hydroponics", "Hydroponics Control", "life",
        "Garden control: crop beds, light spectrum and schedule, water, nutrients and harvest forecast; the food source for the galley.",
        "Hydroponics specialist, galley crew.", ["hydro"], ["planter", "plant", "terminal", "controlpanel", "display"], [],
        """
+--------------------------------------------------------------+
| HYDROPONICS GARDEN                    yield today 14.2 kg     |
+---------------------+----------------------------------------+
| BEDS                | BED 3  Wheat  day 41/90                |
| 1 Lettuce  [====  ] | light 16h  spectrum [R:B 3:1]          |
| 2 Tomato   [======] | water 4.2 L/h  pH 6.1  EC 1.8          |
| 3 Wheat    [===   ] | nutrient [A][B][C]  [HARVEST]          |
| 4 Potato   [=     ] | [LIGHTS +][LIGHTS -] [SCHEDULE]        |
+---------------------+----------------------------------------+
""",
        ["Bed list with growth progress", "Detail panel with sliders for light hours and spectrum", "Water / pH / EC readouts", "Nutrient dosing buttons", "Harvest button and forecast chart"],
        ["ShipState.crops (from the docs/FOOD.md crop list when present, else a built-in set)", "ShipState.power"],
        ["Up/Down bed select, Left/Right adjust the selected slider, H harvest when ripe"],
        ["pH outside 5.5-6.5: warn", "Pump fault: bed row turns warn and engineering shows the fault"],
        "1 Hz.", ["Harvest adds produce to the cargo manifest (fresh food) and to galley availability"],
        "< 0.3 ms per frame.",
        ["Harvesting a ripe bed increments cargo fresh food", "The light slider changes the growth rate"],
        ),
    app("medical", "Medical Diagnostics", "life",
        "Bio-bed vitals, scanner results and a patient list. Bio-bed models host the vitals trace; the medical scanner hosts the body scan.",
        "Medical officer, nurse.", ["medbay", "cabinA", "capt"], ["medbed", "medscanner", "cryo", "surgical", "display", "console"], ["medical", "vitals", "lifesigns"],
        """
+--------------------------------------------------------------+
| MEDICAL DIAGNOSTICS       patients 2  beds free 4             |
+------------------------+-------------------------------------+
| BED 2  J. Okafor       |  ECG ~~/\\~~~/\\~~~   HR 72  SpO2 98   |
| status STABLE          |  BP 118/76  temp 36.8  resp 14      |
| [SCAN] [SEDATE] [DISCH]|  body scan: [HEAD][CHEST][LIMBS]    |
| BED 4  (empty)         |  note: mild fatigue, sleep rec.     |
+------------------------+-------------------------------------+
""",
        ["Patient list tied to bio-beds", "Animated ECG / respiration trace", "Vitals grid", "Body scan selector", "Treatment buttons"],
        ["ShipState.patients (seeded from the roster names, 0-3 patients)", "specs.json medbed / medscanner power"],
        ["Up/Down patient; S scan (3 s); D discharge; Tab to buttons"],
        ["HR outside 50-110 or SpO2 < 92: row turns crit and a beep sounds"],
        "ECG 30 Hz, vitals 1 Hz.", ["Discharging a patient frees the bed; medical events appear on the roster and logbook"],
        "< 0.5 ms per frame (the ECG is a polyline of 256 points).",
        ["The ECG animates", "A scan shows a result text after 3 s"],
        ),
    app("science", "Science Analysis", "science",
        "Spectrograph, periodic table lookup and sample catalogue for the lab analysers and the astrometrics instruments.",
        "Science officer, lab technicians.", ["sci", "astro"], ["analyzer", "sciinstrument", "microscope", "particle", "specimen", "console", "display"], ["waveform", "periodic"],
        """
+--------------------------------------------------------------+
| SCIENCE ANALYSIS      [SPECTRUM] [ELEMENTS] [SAMPLES]         |
+--------------------------------------------------------------+
|  intensity ^   /\\      /\\                                    |
|            |  /  \\ /\\ /  \\    peaks: H 656nm  Fe 438nm      |
|            | /    v  v    \\___  match: G2V star (92%)         |
|            +----------------------> wavelength nm            |
| [LOAD SAMPLE] [COMPARE TO CATALOGUE] [EXPORT TO LOG]          |
+--------------------------------------------------------------+
""",
        ["Spectrograph graph with labelled peaks", "Periodic table grid (118 cells, click for properties)", "Sample list (from lore planets / anomaly notes)", "Match result"],
        ["lore.json star class, temp_k and planets atmosphere", "built-in element table (118 entries)"],
        ["Tab switches views; click an element; Enter loads a sample; E exports a log line into ShipState.log"],
        ["Unknown spectrum: 'NO CATALOGUE MATCH' in warn", "Sample contaminated: crit"],
        "Graph 30 Hz while a sample is loaded.", ["Exported entries appear in the logbook as the science officer"],
        "< 0.5 ms; the periodic table is a static layout.",
        ["The periodic table has 118 cells", "Loading a lore star class shows a plausible spectrum"],
        ),
    app("comms", "Communications", "operations",
        "Channels (ship-wide, department, external subspace), message inbox and hailing.",
        "Comms officer, captain, anyone sending a ship-wide message.", ["comms", "bridge", "ready"], ["commsunit", "router", "antenna", "console", "display", "terminal"], ["comm"],
        """
+--------------------------------------------------------------+
| COMMUNICATIONS    subspace link: STRONG  lag 3.4 s            |
+--------------------+-----------------------------------------+
| CHANNELS           | #ship-wide                              |
| > ship-wide        | 41234.1 Helm: Waypoint in 3 h           |
|   command          | 41234.3 Eng: Scheduled coolant swap     |
|   security         | [type a message____________] [SEND]     |
|   subspace (rx 2)  | [HAIL CONTACT] [OPEN CHANNEL] [MUTE]    |
+--------------------+-----------------------------------------+
""",
        ["Channel list with unread counts", "Message list and composer", "Link status with lag from the distance to the nearest friendly system", "Hail / mute buttons"],
        ["lore.json factions and logs (as incoming subspace traffic)", "ShipState.messages"],
        ["Up/Down channel; type then Enter sends; H hails the locked contact (sensors)"],
        ["Link lost beyond 40 ly of any allied system: 'DELAYED' mode, messages queue", "Anomaly signal (lore): inbound message with garbled text"],
        "1 Hz.", ["Sent messages are appended to ShipState.messages and may be read on any comms screen"],
        "< 0.3 ms.",
        ["A sent message appears in the list", "The link status text changes with the ship position"],
        ),
    app("security", "Security and Access", "systems",
        "Door lock management that really locks and unlocks doors in the game, a camera grid and intruder alerts.",
        "Security chief, bridge, captain.", ["secoff", "brig", "bridge", "armory"], ["camera", "console", "display", "controlpanel", "terminal"], [],
        """
+--------------------------------------------------------------+
| SECURITY & ACCESS     doors 26  locked 3   cams 14  alert G   |
+-------------------------+------------------------------------+
| DOORS            [lock] | CAMERAS                            |
| bridge-corF1      [ ]   | [cam01][cam02][cam03]              |
| armory-corF2      [x]   | [cam04][cam05][cam06]  (live tiles) |
| brig-corF2        [x]   | selected: cam02 Bridge             |
| [LOCK ALL] [UNLOCK ALL] | [FULL SCREEN]                      |
+-------------------------+------------------------------------+
""",
        ["Door list with lock toggles (all doors from ship.json doors[])", "Camera grid of static views per room (pre-rendered or 160x90 SubViewports, max 4 live)", "Lockdown buttons", "Access log"],
        ["ship.json doors and rooms", "ShipState.door_locks {door_index: bool}"],
        ["Up/Down selects a door, Space toggles the lock; L lock all (except stair towers), U unlock all; Tab to cameras, Enter enlarges"],
        ["Lockdown while crew stand in the doorway: the door stays open for 3 s", "Red alert auto-locks the armory and brig"],
        "1 Hz list; camera tiles 5 Hz.", ["Locked doors do not open when the player approaches and show a red light; the starting set locks the armory and the brig"],
        "<= 4 live camera viewports at 160x90.",
        ["Locking the bridge door makes it refuse to open", "Stair tower doors can never be locked (escape)"],
        ),
    app("cargo", "Cargo and Inventory Manifest", "services",
        "Inventory of the cargo bay and spares depot: containers, mass, volume and a tally of the ship's stores.",
        "Quartermaster, cargo handlers.", ["cargo", "depot", "hangar"], ["terminal", "console", "loader", "pallet", "crate", "display"], [],
        """
+--------------------------------------------------------------+
| CARGO MANIFEST       hold 62 % full   mass 18.4 t of 30 t     |
+----------------------+---------------------------------------+
| CATEGORY   QTY  MASS | search [______]                       |
| Fresh food  120  0.9t| item            qty  location   mass  |
| Dry stores   84  2.1t| Rations, dry    400  CB-02      0.8 t |
| Spares      212  3.3t| Coolant canister 12  SD-04      0.3 t |
| Fabric. feed 40  1.2t| [TRANSFER] [AUDIT] [EXPORT CSV]       |
+----------------------+---------------------------------------+
""",
        ["Category summary", "Item table with search", "Fill gauge", "Transfer and audit buttons"],
        ["docs/SHIP_SPEC.md cargo capacity (volume of cargo rooms times a packing factor)", "specs.json mass of the cargo crates in ship.json", "ShipState.cargo"],
        ["Type to search, Up/Down select, T transfer to the fabricator or galley, A audit"],
        ["Mass over capacity: crit; item below minimum stock: warn chip"],
        "On change.", ["Transfers change galley / fabricator availability"], "< 0.3 ms.",
        ["Totals equal the SHIP_SPEC cargo capacity", "Search filters the list"],
        ),
    app("fabricator", "Fabricator Queue", "services",
        "3D printer / fabricator job queue: parts, progress, material feed and power draw.",
        "Engineering workshop crew, quartermaster.", ["shop", "sci", "cargo"], ["analyzer", "terminal", "console", "display"], [],
        """
+--------------------------------------------------------------+
| FABRICATOR QUEUE       printers 2   feedstock 71 %            |
+---------------------------+----------------------------------+
| JOB            ETA  STATE | CATALOGUE                        |
| Valve, 40 mm   0:12 RUN   | [Valve] [Bracket] [Filter] [Tool]|
| Bracket x4     0:40 WAIT  | selected: Bracket   mass 0.2 kg  |
| Filter         1:15 WAIT  | time 8 min  material 120 g       |
+---------------------------+ [QUEUE] [CANCEL] [PRIORITY]      |
+--------------------------------------------------------------+
""",
        ["Job queue with progress bars", "Catalogue of printable parts (valve / engtool / medtool categories from specs.json)", "Feedstock gauge", "Queue / cancel / priority buttons"],
        ["specs.json (mass, price of the part model)", "ShipState.fab_queue, ShipState.cargo.feedstock"],
        ["Click a part then Enter to queue, Delete cancels, P priority"],
        ["Feedstock < 10 %: warn; a job fails when the feedstock is empty"],
        "1 Hz.", ["Finished jobs add spares to the cargo manifest"], "< 0.3 ms.",
        ["A queued job progresses and completes", "Feedstock decreases"],
        ),
    app("galley", "Galley Replicator and Menu", "services",
        "Food and drink catalogue with calories and ingredients; orders from the replicator or galley. Ties to docs/FOOD.md and the food models in the catalogue.",
        "Crew, galley staff.", ["galley", "mess"], ["galley", "vending", "terminal", "display", "tableware"], [],
        """
+--------------------------------------------------------------+
| GALLEY & MENU          credits 120    daily kcal 1,840/2,600  |
+-------------------+------------------------------------------+
| [Meals][Drinks]   | Ratatouille bowl             420 kcal    |
| [Snacks][Special] | ingredients: courgette, tomato, aubergine |
| > Ratatouille     | allergens: none      vegan   [ORDER]     |
|   Rice bowl       | stock: 14 portions                       |
|   Miso soup       | [-] qty 1 [+]       cost 8 cr             |
+-------------------+------------------------------------------+
""",
        ["Category tabs", "Item list with filter (vegan, allergen)", "Detail panel: calories, macros, ingredients, allergens, price", "Order widget with quantity", "Daily intake bar"],
        ["docs/FOOD.md and the food / drink models of catalog.json (calories from godot/data/food.json if the food worker provides it, else a built-in fallback list)", "ShipState.credits, ShipState.cargo.fresh_food"],
        ["Left/Right tab, Up/Down item, +/- quantity, Enter order (consumes stock and credits)"],
        ["Out of stock: row grey", "Insufficient credits: ORDER disabled"],
        "On change.", ["An order decrements the cargo food stock; the calorie counter of the HUD (if present) increases"], "< 0.3 ms.",
        ["Ordering reduces credits and stock", "The allergen filter hides matching items"],
        ),
    app("vending", "Vending Terminal", "services",
        "Self-service vending machine: a short list of snacks and drinks, prices in credits, dispense status line.",
        "Anyone.", ["mess", "rec", "lounge", "dorm"], ["vending"], [],
        """
+------------------------------------------+
| VENDING     credits 120                  |
+------------------------------------------+
| A1 Protein bar  3cr   B1 Water      1cr  |
| A2 Fruit chew   2cr   B2 Tea        2cr  |
| A3 Nut mix      3cr   B3 Cola       2cr  |
|     select code [A_]   [DISPENSE]        |
+------------------------------------------+
""",
        ["Grid of 6-12 slots", "Code entry pad", "Credit display", "Dispense status line"],
        ["ShipState.credits", "item list shared with the galley app (snacks and drinks)"],
        ["Number/letter keys enter the code; Enter dispenses; Esc closes"],
        ["Insufficient credits: the line turns warn", "Sold out"], "On change.",
        ["A dispense deducts credits and adds a snack to the player's inventory text"], "< 0.2 ms.",
        ["Credits decrease after a purchase"],
        ),
    app("alert", "Alert Status Panel", "operations",
        "The ship-wide alert level (green, yellow, red) panel. Changing the level changes the lighting of every room.",
        "Captain, bridge officers, security.", ["bridge", "secoff", "eng", "corF1"], ["display", "controlpanel", "warnlight", "beacon", "sign"], ["alert"],
        """
+------------------------------------------+
| ALERT STATUS                             |
|                                          |
|        [ GREEN ]  YELLOW   RED           |
|     condition: normal operations         |
|  [SET GREEN] [SET YELLOW] [SET RED]      |
|  reason: ______________________          |
+------------------------------------------+
""",
        ["Large level indicator", "Three set buttons (red needs a confirm tap)", "Reason text field", "Last 5 changes list"],
        ["ShipState.alert", "lore.json glossary for the text of the condition names"],
        ["1 / 2 / 3 set green / yellow / red; Enter confirm"],
        ["Red: siren audio hook and warning strobe lights"],
        "On change.",
        ["Writes ShipState.alert; the game tints room lights (green: normal; yellow: amber at 80 % intensity; red: red pulse at 1 Hz on ceiling lights); red alert locks the brig and armory doors"],
        "< 0.1 ms.",
        ["Changing the level emits ShipState.alert_changed", "Lights change within one frame"],
        ),
    app("computer", "Ship's Computer", "systems",
        "A text terminal: type commands and the ship's computer answers. It is the fallback app for any unknown screen texture.",
        "Anyone.", ["bridge", "core", "conf", "ready", "comms"], ["terminal", "console", "display"], ["text"],
        """
+--------------------------------------------------------------+
| SHIP'S COMPUTER  v1.0                                         |
+--------------------------------------------------------------+
| > help                                                       |
| commands: help status map locate <room> specs <model> lore   |
|           log [n] time alert [g|y|r] doors lock <door> ...   |
| > locate astro                                               |
| Astrometrics - deck 1, 28 m from here                        |
| > _                                                          |
+--------------------------------------------------------------+
""",
        ["Scrolling output (500-line ring buffer)", "Input line with history (Up/Down)", "Tab completion for commands, room ids and model ids"],
        ["lore.json, specs.json, ship.json, catalog.json, ShipState"],
        ["Type + Enter; Up/Down history; Tab completes; Ctrl+L clears; Esc closes"],
        ["Unknown command: 'unknown command, try help'"],
        "On input.", ["The commands alert, lock, unlock and dest change ShipState exactly like the dedicated apps"], "< 0.3 ms.",
        ["Every command of the command table runs without an error", "locate <room> answers for every room id"],
        extra=[("Command table", [
            "`help` list commands", "`status` ship summary (alert, power, position)", "`time` ship time and stardate", "`map` current system and neighbours with distances",
            "`dest [system]` show or set the destination", "`locate <room>` where a room is relative to the player (deck, direction, metres)",
            "`specs <model>` datasheet card from specs.json", "`lore` a random datapad", "`log [n]` the latest n log entries", "`alert [g|y|r]` read or set the alert",
            "`doors` list locked doors", "`lock <room>` / `unlock <room>` toggle the door locks of a room", "`power` supply / load summary", "`crew` roster summary",
            "`menu` top items of the food catalogue", "`clear` clear the screen"])]),
    app("deckplan", "Deck Plan and Locator", "navigation",
        "A you-are-here deck map: choose a deck, see every room, find a room by name and show the route from the player's position.",
        "Anyone.", ["corF1", "lobby1", "lobby2", "lobby3", "towerA1", "bridge"], ["sign", "noticeboard", "display", "terminal"], ["schematic"],
        """
+--------------------------------------------------------------+
| DECK PLAN       [ D1 ] [ D2 ] [ D3 ]    find [______]         |
+--------------------------------------------------------------+
|   .---------------.                                          |
|   |BR |  corridor | RR|                                      |
|   |   +-----------+---|   * you are here (corF1)             |
|   '---------------'                      -> Astrometrics     |
|  legend: room dept colours   [SHOW ROUTE]                    |
+--------------------------------------------------------------+
""",
        ["Deck tabs (one per entry of decks[])", "Plan drawing from ship.json polygons coloured by department", "You-are-here marker with heading", "Search box and route line", "Room card (area, purpose from the BOM brief)"],
        ["ship.json rooms[].poly, decks, doors, stairs", "player position from the game"],
        ["Number keys select a deck, click a room for its card, Enter on a search result draws the route"],
        ["Room not found: 'no such room'"], "Marker 10 Hz.", ["None (read-only)"], "Polygons built once per deck.",
        ["The marker moves with the player", "Every room can be found by name"],
        ),
    app("logbook", "Captain's and Crew Logs", "science",
        "Browse the ship's log entries from lore.json by stardate, role or room; read the story of the voyage.",
        "Anyone.", ["ready", "capt", "bridge", "lounge"], ["terminal", "display", "console"], [],
        """
+--------------------------------------------------------------+
| SHIP'S LOGS     role [all v]  [search______]  entries 26      |
+---------------------+----------------------------------------+
| 41200.2 Captain     | 41234.5 Science officer                |
| 41207.9 Eng         | "Signal repeating again, 11 minute..." |
| 41234.5 Science  <  | room: astro                            |
| 41240.1 Helm        | [PREV] [NEXT] [LOCATE ROOM]            |
+---------------------+----------------------------------------+
""",
        ["Entry list sorted by stardate", "Entry reader", "Role filter and search", "Locate room button (opens deckplan)"],
        ["lore.json logs; ShipState.log (entries added in play by science and comms)"],
        ["Up/Down, PageUp/PageDown, Left/Right prev/next, F filter"],
        ["Entries about the signal are highlighted in the accent2 colour"], "On change.", ["None (read-only); optionally entries after the current stardate stay hidden"], "< 0.3 ms.",
        ["All visible logs are listed", "Filtering by role works"],
        ),
    app("roster", "Duty Roster and Notice Board", "services",
        "Duty roster by department and shift, plus a notice board with ship announcements.",
        "Crew.", ["mess", "corF2", "dorm", "lounge", "rec"], ["noticeboard", "display", "terminal"], [],
        """
+--------------------------------------------------------------+
| DUTY ROSTER             shift: BETA (0800-1600)              |
+----------------------+---------------------------------------+
| BRIDGE   Captain ... | NOTICES                               |
| ENG      Chief ...   | * Coolant swap deck 3, 1300           |
| MEDICAL  Dr. ...     | * Movie night, lounge, 2000           |
| GARDEN   ...         | * Signal watch volunteers wanted      |
+----------------------+---------------------------------------+
""",
        ["Roster grid by department and shift", "Notice list", "Shift selector"],
        ["lore.json (crew roles from the logs) and a roster generated from the ship.json departments", "ShipState.clock"],
        ["Left/Right shift, Up/Down notice"], ["None"], "On change.", ["None"], "< 0.2 ms.",
        ["The roster lists every department of ship.json"],
        ),
    app("clock", "Ship's Chronometer", "systems",
        "Ship time, stardate, mission elapsed time and the time to the next waypoint.",
        "Anyone.", ["bridge", "mess", "corF2", "ready"], ["clock", "display"], [],
        """
+------------------------------------------+
|            SHIP TIME 14:32:07            |
|         STARDATE 41234.6                 |
|  mission day 412   next waypoint 8.9 d   |
|  [24h] [12h]                             |
+------------------------------------------+
""",
        ["Large time display", "Stardate and mission day", "Format toggle"],
        ["ShipState.clock (1 game minute per 10 real seconds by default)", "lore.json current and waypoints"],
        ["T toggles 12/24 h"], ["None"], "1 Hz.", ["None (the clock is the source of ShipState.stardate)"], "< 0.1 ms.",
        ["The stardate increases over time"],
        ),
    app("atmosphere", "Environmental Monitor", "life",
        "Room-by-room environment: temperature, humidity, lighting level and noise. Complements the life support deck summary.",
        "Environmental technician, crew.", ["life", "hydro", "bridge", "corF3"], ["display", "controlpanel", "terminal", "sign"], ["graph"],
        """
+--------------------------------------------------------------+
| ENVIRONMENT        room [Hydroponics v]                       |
+--------------------------------------------------------------+
|  temp 24.1 C  [graph 6h ~~~~/\\~~]   humidity 68 %            |
|  light 3200 lx            noise 38 dB(A)    CO2 0.05 %       |
|  setpoint temp [ 24 ] [-][+]                                 |
+--------------------------------------------------------------+
""",
        ["Room dropdown", "Trend graphs (temperature, humidity)", "Readouts", "Setpoint steppers"],
        ["ship.json rooms; docs/SHIP_SPEC.md thermal budget", "ShipState.atmosphere"],
        ["Left/Right changes room, Up/Down adjusts the setpoint"], ["Temperature outside 15-30 C: warn"], "1 Hz.", ["Setpoints affect nothing visual (reserved)"], "< 0.3 ms.",
        ["Every room can be selected"],
        ),
    app("docking", "Hangar and Docking Control", "operations",
        "Hangar bay: force-field on/off, shuttle status, bay door cycle and pressure.",
        "Flight deck officer, helm.", ["hangar", "airlock"], ["forcefield", "craft", "controlpanel", "console", "display"], [],
        """
+--------------------------------------------------------------+
| HANGAR & DOCKING                  bay pressure 101 kPa        |
+------------------+-------------------------------------------+
| FORCE FIELD [ON] | CRAFT      STATE    FUEL   READY          |
| BAY DOOR  CLOSED | Shuttle 1  docked   92 %   yes            |
| [CYCLE DOOR]     | Shuttle 2  docked   88 %   yes            |
| [FIELD TOGGLE]   | [LAUNCH CHECKLIST]  [CLEAR TO LAUNCH]     |
+------------------+-------------------------------------------+
""",
        ["Force-field toggle", "Bay door cycle button with progress", "Craft list", "Pressure gauge", "Launch checklist"],
        ["ShipState.hangar (field_on, door_state)", "specs.json of the craft models in the hangar"],
        ["F toggles the field, C cycles the door, Enter on a craft opens its checklist"],
        ["Door open with the field off: crit and automatic alarm"], "2 Hz.",
        ["F toggles the force-field in the hangar mouth (ShipState.hangar.field_on); C opens/closes the bay door visual if implemented"], "< 0.3 ms.",
        ["The field toggle changes the force-field node"],
        ),
    app("diagnostics", "System Diagnostics", "systems",
        "Self-test of the screen network and machines: runs a test pattern, displays bars and a pass/fail list.",
        "Technicians.", ["eng", "core", "shop"], ["display", "terminal", "console", "controlpanel"], ["diagnostic", "bars"],
        """
+--------------------------------------------------------------+
| SYSTEM DIAGNOSTICS         [RUN ALL TESTS]                    |
+---------------------------+----------------------------------+
| core CPU    [========] OK | colour bars  ||||||||             |
| storage     [========] OK | pixel test   [ ]  [ ]            |
| network     [======- ] 84 | screens 191 online / 0 fault     |
| displays    [========] OK | [EXPORT REPORT TO LOG]           |
+---------------------------+----------------------------------+
""",
        ["Test list with progress bars", "Test pattern panel", "Network summary", "Export button"],
        ["ShipState.systems; the screen-model count from specs.json (software field)"],
        ["R run, Up/Down select, E export"], ["Failed items are crit"], "On run.", ["None"], "< 0.3 ms.",
        ["Run all finishes in 10 s and shows pass"],
        ),
    app("datapad", "Library and Datapad Reader", "science",
        "Reader for the short lore datapads (library and wardroom) and the glossary.",
        "Anyone.", ["lounge", "conf", "ready", "rec", "dorm"], ["terminal", "display", "console"], [],
        """
+--------------------------------------------------------------+
| LIBRARY            [DATAPADS] [GLOSSARY]     search [_____]   |
+---------------------+----------------------------------------+
| 1 The Founding      | THE FOUNDING OF THE CONCORD            |
| 2 Lane Courtesy     | text ... (scrolls)                     |
| 3 The Lighthouse    |                                        |
+---------------------+----------------------------------------+
""",
        ["List of datapads", "Scrollable text reader", "Glossary tab with search"],
        ["lore.json datapads and glossary"], ["Up/Down list, PageUp/PageDown scroll, Tab switches tab"], ["None"], "On change.", ["Reading marks a datapad as read (ShipState.read_pads)"], "< 0.2 ms.",
        ["All datapads are readable", "Glossary search finds terms"],
        ),
    app("holo", "Holo-Projection Viewer", "navigation",
        "Rotating 3D schematic of the ship (and optionally of a selected machine model) on the holo tables.",
        "Anyone, engineers.", ["conf", "bridge", "eng", "astro"], ["holo", "display"], ["globe"],
        """
+--------------------------------------------------------------+
| HOLO VIEWER      [SHIP] [DECK] [MODEL]    spin [ON]           |
+--------------------------------------------------------------+
|               .-----.                                         |
|          ___/ ship   \\___    wireframe hull rotating         |
|          \\_____________/     deck cut lines                  |
|  drag to rotate   wheel zoom   labels [ON]                    |
+--------------------------------------------------------------+
""",
        ["3D wireframe viewport (hull outlines from ship.json.hull extruded per deck)", "Mode tabs (ship, deck, model)", "Spin toggle and labels"],
        ["ship.json hull, decks, rooms", "catalog.json model files (MODEL mode loads the selected GLB)", "specs.json for the data card"],
        ["Drag rotates, wheel zooms, Space toggles spin, Tab changes mode"], ["None"], "30 Hz while open.", ["None"], "<= 1 SubViewport; <= 20k triangles.",
        ["Ship mode shows every deck", "Model mode shows the data card"],
        ),
]


def resolve_app(texture, category=""):
    """Application opened by a screen texture name (the game applies the same four rules, see docs/SOFTWARE_SPEC.md 3.2)."""
    t = texture
    if t.startswith("screen_"):
        t = t[len("screen_"):]
    if t.startswith("scr_"):
        t = t[len("scr_"):]
    if t in TEXTURE_MAP:
        return TEXTURE_MAP[t]
    best = ""
    for k in TEXTURE_PREFIX_MAP:
        key = k[len("scr_"):]
        if t.startswith(key) and len(key) > len(best):
            best = key
    if best:
        return TEXTURE_PREFIX_MAP["scr_" + best]
    return CATEGORY_APP.get(category, "computer")
