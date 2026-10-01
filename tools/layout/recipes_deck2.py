"""Room recipes - Deck 2 (Habitat Deck)."""
from recipes_deck2_helpers import *   # noqa: F401,F403
from recipes_food import (food_brig, food_dorm, food_galley, food_hydro, food_medbay, food_mess, food_rec, food_secoff,   # noqa: F401
                          mess_tables)


# ----------------------------------------------------------------------------------------------- MESS
def f_mess(R, B):
    R.describe(
        "Dining hall where the whole off-watch crew eats in shifts.  It takes food through the wide portal from the galley and "
        "doubles as the ship's social centre (notice board, clocks, vending, plants).",
        basis="About 40 diners per sitting at 2.0 m2 of hall per seat plus the serving line; three columns of long tables with 1.2 m aisles "
              "between columns, a 1.8 m cross aisle in line with the corridor door, 1.4 m kept free along the window wall and the "
              "galley portal and door swing zones left clear.  Serving side north against the galley, vending and waste at the door end.",
        crew=40, adjacency="Galley directly north (3 m portal in the shared wall); corridor door on the east wall; hull windows on the port side.")
    # --- tables first so seats line up on a regular grid
    cols = (-10.6, -7.7, -4.8)
    tables = []
    R.line("Long dining tables",
           "Six 3.0 m tables (two per column) are the core of the hall: long rows give the regular, easily cleaned layout a mess deck needs "
           "and let a watch sit together.  The columns run fore-aft so every seat has a view of the port windows and the serving line.")
    for cx in cols:
        for zc in (-9.0, -4.2):
            tables.append(put(R, B, "table_long_mess_table", cx, zc, 90.0))
    R.line("Short tables for small groups",
           "A 1.5 m bolted table at the aft end of each column seats four and lets pairs or small work teams eat apart from a full row.")
    shorts = [put(R, B, "table_bolted_table", cx, -1.5, 90.0) for cx in cols]
    R.line("Seating along the window column",
           "The port-most column has mess benches on both sides of each table: benches pack more people per metre, stay low in front of the "
           "glass and leave the view open.  One bench of 2.0 m per side gives three seats.")
    for ti, t in enumerate(tables[0:2] + shorts[0:1]):
        if t is None:
            continue
        x0, z0, x1, z1 = t["_fp"]
        zc = (z0 + z1) / 2
        for xs, yaw in ((x0 - 0.30, 90.0), (x1 + 0.30, -90.0)):
            put(R, B, "bench_mess_bench" if ti == 0 else "bench_locker_room_bench", xs, zc, yaw)
    R.line("Chairs at the inner columns",
           "Chairs on both long sides of the two inner columns (three per side at 1.0 m pitch) suit people who like a back rest; "
           "each is tucked against the table edge and faces it.")
    for t in tables[2:] + shorts[1:]:
        if t is None:
            continue
        x0, z0, x1, z1 = t["_fp"]
        zc = (z0 + z1) / 2
        n = 3 if (z1 - z0) > 2.5 else 2
        step = 1.0 if n == 3 else 0.75
        for i in range(n):
            z = zc + (i - (n - 1) / 2.0) * step
            cm = "chair_mess_chair" if x0 < -6.5 else "chair_folding_chair"
            put(R, B, cm, x0 - 0.26, z, 90.0)
            put(R, B, cm, x1 + 0.26, z, -90.0)
    mess_tables(R, B, tables, shorts)
    # --- serving line, north wall both sides of the portal
    R.line("Serving line",
           "Food replicator, salad bar and a coffee machine stand against the galley wall either side of the portal, so trays are filled "
           "where the galley passes food out and the queue forms across the free strip in front of them.")
    wall(R, B, "N", "galley_food_replicator", -11.75)
    wall(R, B, "N", "galley_salad_bar", -9.8)
    wall(R, B, "N", "galley_salad_bar", -4.15)
    wall(R, B, "N", "galley_coffee_machine", -2.55)
    wi(R, B, "N", "display_status_board", -10.8, y=2.6)
    wi(R, B, "N", "display_ticker_banner", -3.6, y=2.6)
    dsign(R, B, "N", -7.0, "dept_mess", y=3.0)
    R.line("Vending and drinking water",
           "Drink and snack machines and a water cooler sit at the door end of the east wall where crew pass as they leave, "
           "clear of the queue at the serving line.")
    wall(R, B, "E", "vending_drink_machine", -11.35)
    wall(R, B, "E", "vending_snack_machine", -10.4)
    wall(R, B, "E", "fountain_water_cooler_tower", -9.65)
    R.line("Waste and recycling", "Tray return and recycling bins by the exit keep diners from carrying rubbish across the hall.")
    wall(R, B, "E", "bin_recycling_bin_triple", -8.7)
    wall(R, B, "E", "bin_trash_bin", -3.4)
    R.line("Window benches",
           "A low bench under each hull window (0.47 m, below the sill) lets people sit with a coffee and look out without blocking the glass.")
    for z in (-7.38, -2.62):
        wall(R, B, "W", "bench_mess_bench", z)
    R.line("Planting and greenery",
           "Planter boxes and ficus trees in the corners and along the south wall soften the steel hall and improve the air; the window wall itself is left free.")
    wall(R, B, "S", "plant_planter_box", -6.0, quiet=True)
    wall(R, B, "E", "plant_ficus_tree", -1.0, quiet=True)
    wall(R, B, "S", "plant_planter_box", -11.6, quiet=True)
    wall(R, B, "S", "plant_ficus_tree", -2.6, quiet=True)
    R.line("Notice board, clocks and displays",
           "Cork board, duty roster and message display on the south wall are read while people wait for a seat; two ship's clocks "
           "give the watch times everyone eats by.")
    wi(R, B, "S", "noticeboard_cork_bulletin_board", -10.2, y=1.5)
    wi(R, B, "S", "noticeboard_duty_roster_display", -8.3, y=1.5)
    wi(R, B, "S", "noticeboard_digital_message_board", -6.4, y=1.6)
    wi(R, B, "S", "clock_dual_time_ship_clock", -4.5, y=2.4)
    wi(R, B, "E", "clock_analogue_chronometer", -3.0, y=2.4, quiet=True)
    wi(R, B, "S", "display_holo_frame_panel", -3.3, y=1.7, quiet=True)
    R.line("Safety equipment and cleaning",
           "Extinguishers at the galley wall and the exit, a first-aid cabinet and a cleaning drone that works between meals.")
    extinguisher(R, B, "N", -11.05)
    extinguisher(R, B, "S", -1.9)
    wi(R, B, "S", "safety_first_aid_cabinet", -12.2, y=1.3, quiet=True)
    wall(R, B, "S", "cleaningbot_floor_scrubber_disc", -8.0, quiet=True)
    R.line("Ceiling lighting and air",
           "Panel lights on a 4 m grid for 300 lux over the tables; square diffusers and sprinklers over the aisles.")
    ext_lights(R, B, spacing=4.0)
    for x, z in ((-9.15, -6.6), (-6.25, -6.6), (-6.25, -1.0), (-9.15, -1.0)):
        R.place(M(B, "duct_ceiling_square_diffuser"), x, z, 0.0, y=R.y + R.h)
    R.place(M(B, "safety_sprinkler_head"), -7.5, -10.5, 0.0, y=R.y + R.h)
    R.place(M(B, "safety_sprinkler_head"), -7.5, -2.8, 0.0, y=R.y + R.h)
    R.omni(-12.3, R.y + 1.6, -5.0, color="#bfe0ff", energy=0.6, rng_=5.0)
    food_mess(R, B)


# ----------------------------------------------------------------------------------------------- GALLEY
def f_galley(R, B):
    R.describe(
        "Crew kitchen that cooks and plates meals for about 40 people and passes them through the wide portal into the mess hall.",
        basis="Linear flow north to south: cold and dry stores on the north wall, prep island in the middle, cooking line on the "
              "port hull facets, dish-wash by the corridor door, hot and cold serving line on the mess wall.  Work triangle "
              "refrigerator - sink - range kept under 6 m; 1.2 m working aisles; hood over the range; easy-clean floor.",
        crew=6, adjacency="Mess hall through the 3 m portal in the south wall; service door to the corridor on the east wall.")
    R.line("Cold storage",
           "Two upright refrigerators and a chest freezer on the north wall hold a week of fresh and frozen food for 40; they sit farthest from "
           "the heat of the range and next to the goods-in door so deliveries cross the room once.")
    seq(R, B, "N", ["galley_refrigerator", "galley_refrigerator", "galley_chest_freezer"], -8.05, gap=0.05, direction=1)
    R.line("Dry stores and shelving",
           "Floor-to-ceiling storage shelving for tins, flour and dry goods next to the cold line, and a second bay by the door for crockery; "
           "both are within one step of the prep island.")
    wall(R, B, "N", "galley_storage_shelving", -3.3)
    wall(R, B, "E", "galley_storage_shelving", -21.0)
    R.line("Prep island and counters",
           "A kitchen island and a prep counter form the central work area: the cook turns from the fridges on the north wall to the island "
           "and on to the range in three steps.  Aisles of 1.2 m or more surround them so two cooks can pass.")
    isl = put(R, B, "galley_kitchen_island", -7.8, -17.7, 0.0)
    cnt = put(R, B, "galley_prep_counter", -5.4, -19.2, 0.0)
    top(R, B, isl, ["galley_toaster"], dx=0.5)
    top(R, B, cnt, ["galley_microwave"], dx=0.3)
    R.line("Cooking line",
           "Range with extraction hood, commercial oven and steamer stand side by side against the port hull facets, so heat, steam and "
           "grease are drawn out at one place and away from the serving line.")
    wall(R, B, "D3", "galley_range_with_hood", 1.2)
    wall(R, B, "D2", "galley_commercial_oven", 1.15)
    wall(R, B, "D1", "galley_steamer", 1.1)
    wall(R, B, "D0", "galley_soup_kettle", 1.05)
    R.line("Sinks and dish-wash",
           "Sink unit and dishwasher on the east wall between the door and the serving line; dirty dishes arrive from the mess hall by the "
           "short path and leave the kitchen without crossing the cook's area.")
    wall(R, B, "E", "galley_sink_unit", -15.3)
    wall(R, B, "E", "galley_dishwasher", -14.0)
    R.line("Serving line",
           "Two counters flank the portal on the mess side: hot food on the port side, salads and cold on the starboard side, so plates move "
           "straight through the opening without the cooks entering the hall.")
    wall(R, B, "S", "galley_prep_counter", -9.7)
    wall(R, B, "S", "galley_food_replicator", -11.6, quiet=True)
    wall(R, B, "S", "galley_prep_counter", -4.25)
    wall(R, B, "S", "galley_water_cooler", -2.5, quiet=True)
    R.line("Hanging pots and ceiling rail",
           "Pans and ladles hang above the island within arm's reach, freeing drawer space and keeping the floor clear.")
    if isl:
        x0, z0, x1, z1 = isl["_fp"]
        R.place(M(B, "galley_hanging_pots_rack"), (x0 + x1) / 2, (z0 + z1) / 2, 0.0, y=R.y + R.h)
    R.line("Water and waste",
           "A potable-water tank and a filtration unit supply cooking water from a dedicated source so the kitchen does not draw from the "
           "drinking loop; a wall trash chute and waste bins keep scraps out of the way.")
    wall(R, B, "E", "watertank_uv_water_purifier", -19.9, quiet=True)
    wi(R, B, "E", "galley_trash_chute", -18.3, y=1.0, quiet=True)
    wall(R, B, "E", "bin_trash_bin", -15.4, quiet=True)
    R.line("Fire and first aid",
           "A kitchen fire is the most likely fire on board: extinguisher by the range, fire blanket by the door, first-aid kit for burns.")
    extinguisher(R, B, "N", -4.4)
    wi(R, B, "E", "safety_fire_blanket_box", -19.4, y=1.3, quiet=True)
    wi(R, B, "E", "safety_first_aid_cabinet", -15.2, y=1.3, quiet=True)
    R.line("Ceiling lighting and ventilation",
           "Sealed light panels over the work areas (300 lux), grilles over the cooking line to feed the hood, and sprinklers for fire suppression.")
    ext_lights(R, B, spacing=3.6)
    R.place(M(B, "duct_ceiling_round_vent"), -10.4, -17.4, 0.0, y=R.y + R.h)
    R.place(M(B, "safety_sprinkler_head"), -7.0, -20.2, 0.0, y=R.y + R.h)
    food_galley(R, B)


# ----------------------------------------------------------------------------------------------- ARMORY
def f_armory(R, B):
    R.describe(
        "Secure weapons store of the security department: long arms, sidearms, armour and riot gear are kept locked, charged, inspected "
        "and issued to the duty watch here.",
        basis="Triangular wedge of 31 m2 under the port bow hull.  Lockers stand against the straight south wall, racks use the slanting "
              "hull facets, the middle stays free for the inspection bench (1.0 m clear each side); a dead-end issue pocket beside the "
              "door lets one person be served while the store stays closed and a force-field shutter seals the store when unattended.  "
              "Sized for a watch of about 12.",
        crew=2, adjacency="Corridor door on the east wall; the brig and security office lie across the corridor on the starboard side.")
    R.line("Rifle and pistol lockers",
           "Locked upright cabinets hold the long arms and sidearms of the watch; they are bolted to the long south wall, which is the only "
           "straight run long enough and is out of the way of the door and the inspection area.")
    seq(R, B, "S", ["weaponrack_rifle_locker", "weaponrack_rifle_locker", "weaponrack_pistol_locker"], -7.25)
    R.line("Armour locker",
           "The armour-plate locker holds body armour and helmets for the watch; it stands on the east wall north of the door, where the "
           "armorer can see it from the counter.")
    wall(R, B, "E", "weaponrack_armour_plate_locker", -28.0)
    R.line("Wall racks on the hull facets",
           "Racks for heavy rifles, pistols, cell packs and riot shields hang on the slanting hull facets - awkward shapes for floor furniture - "
           "high on the wall (centre 1.75-1.85 m) above the level of the floor furniture below, each rack within sight of the armorer.")
    wi(R, B, "D0", "weaponrack_riot_shield_rack", 1.6, y=1.8)
    wi(R, B, "D2", "weaponrack_heavy_rifle_rack", 0.9, y=1.85)
    wi(R, B, "D3", "weaponrack_pistol_rack_wall", 0.75, y=1.75)
    R.line("Cell charging and ammunition",
           "A power-cell charger rack keeps energy weapons topped up; ammunition boxes stay in cans on the bench, never loose.")
    wi(R, B, "D3", "weaponrack_cell_charger_rack", 1.9, y=1.75)
    R.line("Inspection bench",
           "Weapons are cleared, checked and cleaned on the inspection bench on the second hull facet, with the armorer standing at its open side; "
           "the open middle of the store lets a weapon be handled muzzle-down without sweeping anyone.")
    bench = wall_first(R, B, "D1", "weaponrack_weapons_inspection_bench", (1.3, 1.2, 1.4, 1.1))
    if bench:
        top(R, B, bench, ["storagebin_ammo_cans"], quiet=True)
    R.line("Issue counter and armorer's terminal",
           "Weapons are handed out over a counter so nobody enters the store uninvited; the armorer sits behind it and logs every issue and "
           "return on the terminal.")
    cnt = put(R, B, "table_bar_counter", -3.4, -23.2, 90.0)
    top(R, B, cnt, ["terminal_desk_terminal"], quiet=True)
    put(R, B, "chair_swivel_office_chair", -4.25, -23.25, 90.0, quiet=True)
    R.line("Force-field shutter and access control",
           "A force-field shield doorway just inside the door closes the store when the armorer leaves; a retina scanner on the wall beside "
           "the door and a dome camera over it record everybody who enters.")
    first(R, B, "forcefield_shield_doorway", [(-3.69, -26.0, -90.0)])
    wi(R, B, "E", "camera_retina_scanner", -24.0, y=1.5, quiet=True)
    R.place(M(B, "camera_dome_ceiling"), -3.0, -26.0, 0.0, y=R.y + R.h)
    R.place(M(B, "camera_pan_tilt_ceiling"), -5.5, -23.6, 0.0, y=R.y + R.h)
    R.line("Safety and signs",
           "An extinguisher and a first-aid cabinet by the armorer, a no-entry sign and the security department sign at the door.")
    extinguisher(R, B, "S", -3.1, y=1.6)
    wi(R, B, "E", "safety_first_aid_cabinet", -23.0, y=1.3, quiet=True)
    wi(R, B, "E", "sign_no_entry", -28.0, y=2.6, quiet=True, check=False)
    dsign(R, B, "E", -26.0, "dept_security", y=3.05)
    R.line("Ceiling lighting",
           "Bright, even light (400 lux) for inspecting weapons, with a cooling vent over the charger racks.")
    ext_lights(R, B, spacing=3.0, x_margin=0.6)
    R.place(M(B, "duct_ceiling_round_vent"), -6.0, -23.0, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- BRIG
def f_brig(R, B):
    R.describe(
        "Detention block of the ship: a holding cell for offenders awaiting the captain's judgement, a guard post that watches the cell and both "
        "doors, and the equipment for searching, restraining and interviewing a detainee.",
        basis="Triangular starboard-bow wedge of 31 m2.  One full-height cell module (about 6 m2) is the most the wedge takes; the cell "
              "front faces the guard post, which sees the cell, the corridor door and the door to the security office from one seat.  "
              "Detainees are searched and held on the bench beside the corridor door before they enter the cell.",
        crew=2, adjacency="Security office directly south (door at its north wall); corridor door on the west wall; armoury across the corridor.")
    R.line("Detention cell",
           "A cell module with wall cot and toilet is the secure room; it stands in the south-west corner with its back to two walls "
           "so the only way out is through its front, which faces the guard post.")
    cell = first(R, B, "cell_wall_cot_toilet", [(3.12, -23.15, 180.0)], scale=0.97)
    R.line("Cell door and observation",
           "A force-field door closes the cell front; the guard opens it from the desk, and cameras let him watch the cell while seated.")
    if cell:
        x0, z0, x1, z1 = cell["_fp"]
        first(R, B, "cell_door_forcefield", [((x0 + x1) / 2, z0 - 0.3, 180.0)], quiet=True)
    R.line("Guard post",
           "The guard's desk stands against the west wall beside the corridor door, so every visitor is seen on entry; the terminal and "
           "the camera monitor stack above it control the cell field and door locks and show the cell and the security office.")
    desk = wall_first(R, B, "W", "desk_computer_desk", (-28.05, -28.1, -28.15))
    if desk:
        top(R, B, desk, ["terminal_desk_terminal"], quiet=True)
        put(R, B, "chair_swivel_office_chair", desk["_fp"][2] + 0.5, (desk["_fp"][1] + desk["_fp"][3]) / 2, -90.0, quiet=True)
        wi(R, B, "W", "display_triple_stack", (desk["_fp"][1] + desk["_fp"][3]) / 2, y=2.25, quiet=True)
    R.line("Holding bench and restraint chair",
           "New detainees wait cuffed to the holding bench on the south-east facet, beside the door to the security office, before they are "
           "searched and booked; the restraint chair next to it is for violent or intoxicated persons.")
    wall_first(R, B, "D2", "bench_locker_room_bench", (1.0, 1.1, 0.95, 1.2))
    R.line("Property and guard lockers",
           "A detainee's belongings are locked away before he enters the cell, and the guard's sidearm is kept in a pistol locker that "
           "detainees cannot reach; all three cabinets stand on the north-east facet within reach of the guard desk.")
    wall_first(R, B, "D1", "cell_property_locker", (0.65, 0.75, 0.85), quiet=True)
    wall_first(R, B, "D1", "cell_property_locker", (1.65, 1.75, 1.55), quiet=True)
    wall_first(R, B, "D1", "weaponrack_pistol_locker", (2.3, 2.2), quiet=True)
    first(R, B, "cell_restraint_chair", [(4.9, -25.4, 135.0), (5.0, -25.6, 135.0), (4.8, -25.2, 135.0)], quiet=True)
    wi(R, B, "D0", "safety_first_aid_cabinet", 1.0, y=1.3, quiet=True)
    R.line("Cameras and control",
           "Ceiling domes cover the cell and the door; a motion sensor at the cell alerts the guard if a detainee approaches the field.")
    R.place(M(B, "camera_dome_ceiling"), 3.0, -24.6, 0.0, y=R.y + R.h)
    R.place(M(B, "camera_pan_tilt_ceiling"), 5.5, -23.0, 0.0, y=R.y + R.h)
    wi(R, B, "W", "camera_card_reader", -24.5, y=1.5, quiet=True)
    wi(R, B, "S", "camera_card_reader", 7.6, y=1.5, quiet=True)
    R.line("Safety and signs",
           "Extinguisher by the guard post, security sign at the corridor door, status board with the detention register.")
    wi(R, B, "W", "safety_fire_extinguisher", -24.0, y=1.1, quiet=True)
    dsign(R, B, "W", -26.0, "dept_security", y=3.05)
    wi(R, B, "D1", "display_status_board", 1.3, y=2.0, quiet=True)
    R.line("Ceiling lighting",
           "Sealed, vandal-resistant light panels; one directly over the cell front.")
    ext_lights(R, B, spacing=3.0, x_margin=0.6)
    food_brig(R, B)


# ----------------------------------------------------------------------------------------------- SECURITY OFFICE
def f_secoff(R, B):
    R.describe(
        "Headquarters of the ship's security department: duty desks, the monitor wall that shows every camera on the ship, a tactical "
        "table for briefing the watch, and the evidence and weapon stores.",
        basis="About 85 m2 for a watch of six to eight.  Monitor wall and duty consoles on the long south wall; briefing table with "
              "seating in the open middle, 1.2 m clear all round; duty desks on the east hull facets, where the room narrows; stores on the "
              "west and north walls next to the brig door so prisoners and evidence move the shortest way.",
        crew=8, adjacency="Brig directly north (door in the north wall); corridor door on the west wall; armoury across the corridor.")
    R.line("Monitor wall",
           "Tactical wall screens, a schematics wall and status boards fill the long south wall above the duty consoles, at a 1.9 m centre "
           "height so every seat in the room can read them; they show camera feeds, the ship plan and alert status.")
    wi(R, B, "S", "display_tactical_wall_screen", 4.0, y=2.55)
    wi(R, B, "S", "display_schematics_wall", 6.6, y=2.55)
    wi(R, B, "S", "display_tactical_wall_screen", 9.2, y=2.55)
    wi(R, B, "S", "display_status_board", 11.2, y=2.55, quiet=True)
    wi(R, B, "S", "display_alert_board", 2.5, y=2.55, quiet=True)
    R.line("Duty consoles",
           "Three consoles against the south wall - tactical, sensor and a triple-screen station - are the watch-standers' working "
           "positions; each operator sits facing the monitor wall and each console has its chair tucked in front.")
    cons = []
    for mid, x in (("console_tactical", 3.6), ("console_sloped_triple_screen", 6.6), ("console_sensor", 9.6)):
        c = wall(R, B, "S", mid, x)
        cons.append(c)
        if c:
            seat = seat_facing(R, c, cats=("seat",), gap=0.3, label="tactical_chair")
            if seat is None:
                _miss(R, "seat for " + mid, "")
    R.line("Briefing table and seating",
           "A holographic briefing table in the middle of the floor lets the watch commander brief six to eight people standing or seated; "
           "benches and chairs form an arc on the north side so everyone can see the projection and the monitor wall.")
    hol = put(R, B, "holo_briefing_table", 6.6, -17.6, 0.0)
    if hol:
        x0, z0, x1, z1 = hol["_fp"]
        for i, dx in enumerate((-1.0, 0.0, 1.0)):
            put(R, B, "chair_swivel_office_chair", (x0 + x1) / 2 + dx, z0 - 0.55, 0.0, quiet=True)
        for dz in (-0.45, 0.45):
            put(R, B, "chair_folding_chair", x0 - 0.6, (z0 + z1) / 2 + dz, 90.0, quiet=True)
            put(R, B, "chair_folding_chair", x1 + 0.6, (z0 + z1) / 2 + dz, -90.0, quiet=True)
    R.line("Duty desks on the hull facets",
           "Three officers' desks with terminals and swivel chairs use the slanted east hull, which leaves awkward corners for other "
           "furniture; the desk occupants see the whole room and the door.")
    ds = []
    for side, along in (("D1", 1.15), ("D2", 1.1), ("D3", 1.05)):
        d = wall_first(R, B, side, "desk_officer_desk", (along, along + 0.1, along - 0.1), quiet=True)
        if d:
            ds.append(d)
            top(R, B, d, ["terminal_desk_terminal"], dx=-0.4, quiet=True)
            seat_facing(R, d, cats=("chair",), gap=0.3, label="swivel_office")
        else:
            _miss(R, "desk_officer_desk", "on " + side)
    R.line("Evidence store",
           "Cage lockers and a drawer cabinet hold evidence and seized items; they stand beside the brig door so prisoners' property "
           "and evidence are logged and locked away next to where they enter.")
    wall_first(R, B, "N", "shelving_cage_lockers", (3.0, 2.9, 3.1))
    wall_first(R, B, "N", "crate_vault_armoured", (1.4, 1.5), quiet=True) if False else None
    wall_first(R, B, "W", "storagebin_drawer_cabinet", (-14.2, -14.1, -14.4), quiet=True)
    R.line("Weapon locker",
           "A rifle locker and a pistol locker for the duty shift's sidearms, locked and close to the corridor door.")
    wall_first(R, B, "W", "weaponrack_rifle_locker", (-21.0, -20.6, -20.2))
    wall_first(R, B, "W", "weaponrack_pistol_locker", (-19.7, -19.6, -19.5), quiet=True)
    R.line("Coffee point",
           "A coffee machine and water cooler at the north-east corner give the watch a place to stand and talk without leaving the room.")
    wall_first(R, B, "N", "galley_coffee_machine", (7.95, 8.0, 7.9), quiet=True)
    wall_first(R, B, "D0", "fountain_water_cooler_tower", (0.9, 1.0, 1.1), quiet=True)
    R.line("Cameras and access control",
           "Dome cameras at the two doors and a card reader beside each door record who enters; the corridor door is the only way in for visitors.")
    R.place(M(B, "camera_dome_ceiling"), 3.0, -17.5, 0.0, y=R.y + R.h)
    R.place(M(B, "camera_pan_tilt_ceiling"), 6.0, -20.9, 0.0, y=R.y + R.h)
    wi(R, B, "W", "camera_card_reader", -19.3, y=1.5, quiet=True)
    wi(R, B, "N", "camera_card_reader", 8.2, y=1.5, quiet=True)
    R.line("Greenery and comfort",
           "A bonsai and a succulent on the duty desks soften a room where people work long watches.")
    if ds:
        top_try(R, B, ds[0], "plant_bonsai", [(0.5, 0), (-0.5, 0), (0, 0.3), (0, -0.3), (0.4, 0.2), (-0.4, -0.2), (0.3, -0.25), (-0.3, 0.25), (0.7, 0), (-0.7, 0)])
    if len(ds) > 2:
        top_try(R, B, ds[2], "plant_succulent_set", [(0.5, 0), (-0.5, 0), (0, 0.3), (0, -0.3), (0.4, 0.2), (-0.4, -0.2), (0.3, -0.25), (-0.3, 0.25), (0.7, 0), (-0.7, 0)])
    wall_first(R, B, "N", "plant_planter_box", (2.0, 2.2), quiet=True) if False else None
    R.line("Safety, signs and notices",
           "Extinguishers and a first-aid cabinet, a wall clock for the log, and the department sign over the corridor door.")
    wi(R, B, "W", "safety_fire_extinguisher", -15.6, y=1.1, quiet=True)
    wi(R, B, "S", "safety_fire_extinguisher", 1.9, y=1.1, quiet=True)
    wi(R, B, "S", "safety_first_aid_cabinet", 12.0, y=1.3, quiet=True)
    wi(R, B, "W", "clock_digital_clock", -16.0, y=2.35, quiet=True)
    wi(R, B, "N", "noticeboard_duty_roster_display", 2.4, y=1.5, quiet=True)
    dsign(R, B, "W", -17.5, "dept_security", y=3.05)
    R.line("Ceiling lighting",
           "Bright lighting (350 lux) on a 3.5 m grid with the brig door and the briefing table lit separately.")
    ext_lights(R, B, spacing=3.6)
    food_secoff(R, B)


# ----------------------------------------------------------------------------------------------- MEDICAL BAY
def f_medbay(R, B):
    R.describe(
        "Sickbay for the whole crew: a ward of treatment beds, a surgical corner, diagnostic scanners, stasis units, an isolation bed "
        "and the drug and supply stores, with the doctor's desk by the door.",
        basis="About 150 m2 (3.7 m2 per crew member).  A 1.8 m stretcher aisle runs from the corridor door into the middle of the room and "
              "divides the ward (north) from the diagnostic and surgical zone (south); beds at 1.9 m pitch leave 0.58 m for curtains; "
              "scrub sink beside the operating table; the starboard windows stay clear.  Ceiling 3.6 m for surgical light and ceiling rails.",
        crew=6, adjacency="Corridor door on the west wall; science laboratory lies south across the corridor side; windows on the starboard hull.")
    R.keep_clear((1.65, -7.45, 7.0, -5.55), "1.8 m stretcher aisle from the door into the middle of the bay")
    R.line("Treatment beds",
           "Four diagnostic biobeds with heads to the north wall give a ward for routine treatment; each has a vitals monitor above it "
           "and 0.58 m between beds for a privacy curtain.  The beds are the first thing a stretcher reaches from the door.")
    beds = []
    for x in (4.3, 6.1, 7.9, 9.7):
        b = wall(R, B, "N", "medbed_diagnostic_biobed", x)
        beds.append(b)
        wi(R, B, "N", "medsupply_wall_patient_monitor", x, y=2.3, quiet=True)
    R.line("Isolation bed",
           "A sealed isolation bed in the north-east corner, far from the door, for contagious patients; its distance from the ward and "
           "the window to the hull make it the natural place for quarantine.")
    wall_first(R, B, "N", "medbed_isolation_bed", (11.5, 11.45, 11.4))
    R.line("Bedside equipment",
           "IV stands stand next to the bed heads so a drip can follow the patient when a bed is moved.")
    for i, b in enumerate(beds):
        if b:
            x0, z0, x1, z1 = b["_fp"]
            put(R, B, "medsupply_iv_stand" if i % 2 == 0 else "cylinder_portable_o2_unit", (x0 + x1) / 2, z1 + 0.45, 0.0, quiet=True)
    R.line("Drug and instrument stores",
           "Drug dispensing, medicine, sample fridge and instrument cabinets line the north end of the west wall, next to the door and "
           "the doctor, locked, cold where needed and within one step of the beds.")
    seq(R, B, "W", ["medcabinet_drug_dispensing_cabinet", "medcabinet_medicine_cabinet", "medcabinet_sample_fridge"], -12.85, gap=0.05, quiet=True)
    wall_first(R, B, "N", "medcabinet_instrument_tray_cabinet", (3.05, 3.0, 3.1), quiet=True)
    R.line("Doctor's desk",
           "The doctor's desk with terminal stands against the west wall south of the door: the doctor sees everyone entering, reaches "
           "the stores and keeps the records.")
    desk = wall_first(R, B, "W", "desk_officer_desk", (-4.15, -4.2, -4.3))
    if desk:
        top(R, B, desk, ["terminal_desk_terminal"], quiet=True)
        seat_facing(R, desk, cats=("chair",), gap=0.3, label="swivel_office")
    R.line("Diagnostic scanners",
           "A whole-body scanner arch and an MRI ring stand side by side on the south wall, each with clear floor in front so a bed can be "
           "rolled in from the aisle; the heavy, shielded equipment sits away from the windows and near the power trunks.")
    wall(R, B, "S", "medscanner_whole_body_scanner_arch", 3.25)
    wall(R, B, "S", "medscanner_mri_ring_scanner", 5.75)
    R.line("Stasis and cryo",
           "Two stasis pods and a control pillar hold patients in emergency stasis and shield them while a surgeon is found; they stand "
           "against the south wall next to the scanners that identify who needs them.")
    wall(R, B, "S", "cryo_cryo_stasis_pod", 7.5)
    wall(R, B, "S", "cryo_cryo_stasis_pod", 8.6)
    R.line("Surgical table and equipment",
           "The operating table in the south-east corner has an overhead surgical light, an anesthesia machine at the head, "
           "a robotic arm beyond the head and a defibrillator cart at the side; it stays 1.0 m from the scrub sink and away from the stretcher aisle.")
    tbl = put(R, B, "medbed_surgical_table", 10.75, -3.2, 0.0)
    if tbl:
        cx = (tbl["_fp"][0] + tbl["_fp"][2]) / 2
        cz = (tbl["_fp"][1] + tbl["_fp"][3]) / 2
        R.place(M(B, "surgical_overhead_surgical_light_boom"), cx, cz, 0.0, y=R.y + R.h)
        first(R, B, "surgical_anesthesia_machine", [(cx - 1.0, tbl["_fp"][1] + 0.4, 0.0)], quiet=True)
        first(R, B, "surgical_surgical_robotic_arm_unit", [(cx + 0.3, tbl["_fp"][1] - 0.9, 180.0), (cx + 0.3, tbl["_fp"][1] - 1.0, 180.0)])
        first(R, B, "surgical_defibrillator_cart", [(cx - 1.0, tbl["_fp"][3] - 0.3, 90.0)], quiet=True)
        top(R, B, tbl, ["medtool_surgical_instrument_tray"], quiet=True)
    wall_first(R, B, "S", "labbench_wet_bench_sink", (11.6, 11.7, 11.5), quiet=True)
    R.line("Sharps, biohazard and first aid",
           "Sharps container and biohazard bin at the scrub sink, a wall first-aid station by the door and a defibrillator station in the "
           "ward, so contaminated waste never crosses the clean area.")
    wi(R, B, "S", "medsupply_sharps_container", 9.9, y=1.3, quiet=True)
    wall_first(R, B, "S", "crate_biohazard", (12.3, 12.4), quiet=True)
    wi(R, B, "W", "medcabinet_wall_first_aid_station", -8.1, y=1.4, quiet=True)
    wi(R, B, "N", "safety_defibrillator_station", 3.4, y=1.1, quiet=True)
    wi(R, B, "W", "medcabinet_glove_and_mask_dispenser", -4.3, y=1.4, quiet=True)
    R.line("Oxygen and gases",
           "Two emergency air bottles and a portable oxygen unit stand on the west wall by the door, ready to go with a stretcher; "
           "they are chained to the wall as required.")
    wall_first(R, B, "W", "cylinder_emergency_air_bottle", (-8.6, -8.7, -8.5))
    wall_first(R, B, "W", "cylinder_emergency_air_bottle", (-9.35, -9.4, -9.3), quiet=True)
    wall_first(R, B, "W", "cylinder_portable_o2_unit", (-9.95, -10.0), quiet=True)
    wi(R, B, "E", "cylinder_gas_manifold_panel", -5.0, y=1.6, quiet=True) if False else None
    R.line("Window benches",
           "A low bench (0.47 m, below the sill) under the north starboard window give recovering patients and visitors a place to sit "
           "and look out; nothing tall stands in front of the glass.")
    wall(R, B, "E", "bench_mess_bench", -7.38)
    R.line("Safety, signs and cleaning",
           "Extinguisher by the door, department sign over it, and a cleaning drone to keep the floor sterile between shifts.")
    wi(R, B, "W", "safety_fire_extinguisher", -7.9, y=1.1, quiet=True) if False else None
    wi(R, B, "W", "safety_fire_extinguisher", -4.6, y=1.1, quiet=True)
    dsign(R, B, "W", -6.5, "dept_medical", y=3.05)
    wi(R, B, "S", "clock_digital_clock", 7.3, y=2.4, quiet=True)
    wall_first(R, B, "S", "cleaningbot_floor_scrubber_disc", (1.7, 1.75), quiet=True)
    R.line("Ceiling lighting",
           "Shadow-free panels (500 lux) over the ward and surgical corner, dimmer panels over the recovery area.")
    ext_lights(R, B, spacing=3.6)
    food_medbay(R, B)


# ----------------------------------------------------------------------------------------------- RECREATION
def f_rec(R, B):
    R.describe(
        "Off-duty space of the crew: a small gym on the starboard half for cardio and strength work, and a lounge around the port hull window "
        "with sofas, a games table and vending.",
        basis="About 85 m2 for up to 20 people at a time.  Cardio machines stand against the north wall facing the wall display, "
              "free weights and the punching bag in the south-east where floor loads are lowest, 1.2 m circulation between them; the lounge "
              "seating faces the window and nothing tall stands within 0.5 m of the glass.",
        crew=20, adjacency="Corridor door on the east wall; crew quarters directly aft-south; mess hall to the north.")
    R.line("Treadmills and exercise bikes",
           "Three treadmills and two bikes stand in a row against the north wall, backs to the room and faces toward the wall, so the "
           "runner looks at a wall display and the rest of the room stays in view of the gym attendant; the row is far from the lounge to keep noise down.")
    for x in (-7.6, -6.5, -5.4):
        first(R, B, "gym_treadmill", [(x, 4.85, 180.0)])
    for x in (-4.4, -3.6):
        first(R, B, "gym_exercise_bike", [(x, 4.35, 180.0)], quiet=True)
    wi(R, B, "N", "display_status_board", -6.5, y=2.4, quiet=True)
    R.line("Rowing machines",
           "Two rowing machines need 2.1 m of length, so they run north-south beside the bikes, clear of the main route from the door to the lounge.")
    for x in (-7.3, -6.5):
        first(R, B, "gym_rowing_machine", [(x, 7.05, 0.0)])
    R.line("Free weights and punching bag",
           "Weight bench with rack and the dumbbell rack sit on the south wall, the punching bag in the south-east corner where swing space "
           "is free; heavy, noisy equipment stays far from the quarters' wall.")
    wall_first(R, B, "S", "gym_weight_bench_and_rack", (-6.0, -6.2, -5.8))
    wall_first(R, B, "S", "gym_dumbbell_rack", (-8.4, -8.2, -8.6), quiet=True)
    wall_first(R, B, "S", "gym_punching_bag", (-2.6, -2.5, -2.4), quiet=True)
    R.line("Yoga mats and benches",
           "A yoga mat rack on the south wall gives a stretching area with clear floor in front of it.")
    wall_first(R, B, "S", "gym_yoga_mat_rack", (-3.9, -4.1, -3.7), quiet=True)
    R.line("Lounge seating facing the window",
           "A three-seater sofa faces the port window with a coffee table between, and two armchairs close the conversation group; the "
           "view of space is the main attraction of the room.")
    first(R, B, "couch_three_seater_sofa", [(-9.5, 6.8, -90.0), (-9.6, 6.8, -90.0)])
    tbl = first(R, B, "table_coffee_table", [(-11.5, 6.8, 90.0), (-11.4, 6.8, 90.0)], quiet=True)
    first(R, B, "couch_lounge_armchair", [(-11.4, 5.7, 0.0), (-11.0, 5.7, 0.0)], quiet=True)
    first(R, B, "couch_lounge_armchair", [(-11.4, 7.95, 180.0), (-11.0, 7.95, 180.0)], quiet=True)
    if tbl:
        top(R, B, tbl, ["tableware_cups_and_mugs"], quiet=True)
    R.line("Games table",
           "A bolted table with four chairs in the south-west corner for cards and board games, near the vending machines.")
    g = first(R, B, "table_bolted_table", [(-9.6, 9.1, 0.0), (-9.6, 8.9, 0.0), (-10.4, 8.4, 0.0), (-8.4, 8.4, 0.0)], quiet=True)
    if g:
        x0, z0, x1, z1 = g["_fp"]
        for dx in (-0.4, 0.4):
            put(R, B, "chair_folding_chair", (x0 + x1) / 2 + dx, z0 - 0.3, 0.0, quiet=True)
            put(R, B, "chair_folding_chair", (x0 + x1) / 2 + dx, z1 + 0.3, 180.0, quiet=True)
        top(R, B, g, ["tableware_bottle_and_glasses"], quiet=True)
    R.line("Vending, water and display",
           "Drink and snack machines and a water fountain on the south wall serve both zones; a wall display over them shows the ship's news "
           "and the day's exercise schedule.")
    wall_first(R, B, "S", "vending_drink_machine", (-12.1, -12.0), quiet=True)
    wall_first(R, B, "S", "vending_snack_machine", (-11.1, -11.0), quiet=True)
    wi(R, B, "N", "fountain_drinking_fountain_wall_unit", -9.0, y=0.9, quiet=True)
    wi(R, B, "S", "display_holo_frame_panel", -9.7, y=1.8, quiet=True)
    R.line("Lockers and bench",
           "A bank of double lockers with a bench along the north wall west of the gym lets people stow kit before they train; a wall mirror "
           "cabinet sits at the end.")
    seq(R, B, "N", ["locker_double_locker_bank", "locker_double_locker_bank", "locker_double_locker_bank"], -12.75, quiet=True)
    wall_first(R, B, "N", "bench_locker_room_bench", (-9.4, -9.3), quiet=True)
    R.line("Plants and notices",
           "A ficus by the lounge and a notice board with the activity roster bring life to the room and tell people what is on.")
    wall_first(R, B, "S", "plant_ficus_tree", (-7.8, -7.6), quiet=True)
    wi(R, B, "E", "noticeboard_cork_bulletin_board", 10.0, y=1.5, quiet=True)
    R.line("Safety and signs",
           "Extinguisher, first-aid cabinet and a sign over the corridor door; a wall clock shows the session time.")
    wi(R, B, "E", "safety_fire_extinguisher", 4.6, y=1.1, quiet=True)
    wi(R, B, "E", "safety_first_aid_cabinet", 9.5, y=1.3, quiet=True)
    wi(R, B, "E", "clock_dual_time_ship_clock", 4.6, y=2.4, quiet=True)
    dsign(R, B, "E", 7.3, "dept_quarters", y=3.0)
    R.line("Ceiling lighting", "Bright light over the gym (400 lux) and warm light over the lounge.")
    ext_lights(R, B, spacing=3.6)
    food_rec(R, B)


# ----------------------------------------------------------------------------------------------- CREW QUARTERS
def f_dorm(R, B):
    R.describe(
        "Shared sleeping quarters for enlisted crew off watch: bunk beds with a personal locker each, a common table for meals and cards, "
        "and a desk nook for letters and study.",
        basis="About 4.6 m2 per berth for 15 berths (the ship's hot-bunking ratio is 2 crew per berth).  Bunks stand head-to-wall in a row "
              "along the north wall with a tall locker between each, leaving a 1.1 m cross aisle to the common table; "
              "single bunks use the tapering stern facets; nothing tall within 0.5 m of the small stern portholes; 0.9 m minimum aisles.",
        crew=28, adjacency="Corridor door on the east wall; recreation room directly forward (north); hydroponics across the corridor.")
    R.line("Bunk row on the north wall",
           "Five double bunks stand with their heads to the north wall - the quietest, darkest wall, furthest from the corridor door - "
           "giving ten berths.  Each bunk has its own tall vented locker beside it.")
    xs = []
    pos = -11.75
    for i in range(5):
        b = wall_first(R, B, "N", "bed_bunk_bed", (pos + 0.54,))
        if b is None:
            continue
        xs.append(pos)
        wall_first(R, B, "N", "locker_tall_vented_locker", (pos + 1.08 + 0.05 + 0.26,))
        pos += 1.08 + 0.05 + 0.52 + 0.05
    R.line("Bunks on the east and south walls",
           "Two more double bunks - one on the east wall south of the door and one in the gap between the two south portholes - raise the total "
           "to fourteen berths before the single.")
    wall_first(R, B, "E", "bed_bunk_bed", (16.6, 16.65))
    wall_first(R, B, "S", "bed_bunk_bed", (-5.25, -5.3, -5.2))
    R.line("Single bunk on the port side",
           "The tapering port side is too narrow for a double bunk; a single bunk with its head to the hull uses the space, "
           "gives the fifteenth berth and is away from the corridor noise.")
    first(R, B, "bed_single_bunk", [(-9.7, 14.45, 90.0), (-9.6, 14.45, 90.0), (-9.5, 14.4, 90.0)])
    R.line("Under-bed drawers and shoe rack",
           "Under-bed drawers take folded clothing, a shoe rack and wall cabinet keep boots out of the aisle and the bunks tidy.")
    wall_first(R, B, "S", "locker_shoe_rack", (-2.5, -2.4), quiet=True)
    wall_first(R, B, "D5", "locker_wardrobe", (0.85, 0.9), quiet=True)
    wi(R, B, "E", "locker_wall_cabinet", 12.2, y=1.6, quiet=True)
    R.line("Common table",
           "A bolted table with four chairs in the middle of the room is where crew eat off-watch snacks, play cards and write; "
           "its position leaves more than 1.0 m on all sides.")
    t = first(R, B, "table_bolted_table", [(-7.4, 15.3, 0.0), (-7.4, 15.5, 0.0)])
    if t:
        x0, z0, x1, z1 = t["_fp"]
        for dx in (-0.4, 0.4):
            put(R, B, "chair_mess_chair", (x0 + x1) / 2 + dx, z0 - 0.26, 0.0, quiet=True)
            put(R, B, "chair_mess_chair", (x0 + x1) / 2 + dx, z1 + 0.26, 180.0, quiet=True)
        top(R, B, t, ["tableware_cups_and_mugs", "tableware_cutlery_set"], step=0.5, quiet=True)
    R.line("Desk nook",
           "A writing desk with terminal and chair in the north-east corner by the corridor for letters, study and the duty roster; "
           "a table lamp lets the reader work without waking sleepers.")
    d = wall_first(R, B, "E", "desk_writing_desk", (12.0, 12.1, 11.9), quiet=True)
    if d:
        top(R, B, d, ["terminal_desk_terminal", "lamp_table_lamp"], step=0.4, quiet=True)
        seat_facing(R, d, cats=("chair",), gap=0.3, label="swivel_office")
    R.line("Lamps and greenery",
           "A floor lamp and a small ficus by the table make the room feel like home and give a low night light.")
    put(R, B, "lamp_floor_lamp", -4.2, 14.2, 0.0, quiet=True)
    wall_first(R, B, "D5", "plant_planter_box", (0.85, 0.9, 0.8), quiet=True)
    wi(R, B, "N", "lamp_reading_light", -8.3, y=1.4, quiet=True)
    R.line("Safety, signs and notices",
           "Extinguisher and fire blanket near the door, an evacuation map, and the quarters department sign over the corridor door.")
    wi(R, B, "E", "safety_fire_extinguisher", 13.0, y=1.1, quiet=True)
    wi(R, B, "E", "safety_evac_route_map", 16.6, y=1.4, quiet=True)
    wi(R, B, "N", "noticeboard_duty_roster_display", -2.6, y=1.5, quiet=True)
    dsign(R, B, "E", 14.5, "dept_quarters", y=3.0)
    R.line("Ceiling lighting",
           "Dim warm lights (150 lux) on a grid for night watch, with a brighter one over the common table.")
    ext_lights(R, B, spacing=3.6, energy=1.0)
    food_dorm(R, B)


# ----------------------------------------------------------------------------------------------- SCIENCE LAB
def f_sci(R, B):
    R.describe(
        "General laboratory for the science department: wet chemistry and biology at the north benches, instruments and specimen storage on "
        "the south wall, an island bench for shared work, and data desks in the south-east corner by the starboard window.",
        basis="About 85 m2 for four to six researchers (14 m2 each incl. equipment).  Fume hood, sink and clean bench sit on one wall so "
              "one fixed extract/water service serves them; 1.2 m clear work aisles either side of the island; safety shower and eye wash "
              "within 3 m of the hood and never behind a bench; the corridor door end stays clear; window end kept free of tall items.",
        crew=6, adjacency="Corridor door on the west wall; medical bay is forward (north) across the same corridor; hydroponics is aft.")
    R.line("Fume hood, wet bench and clean bench",
           "Fume hood, sink bench, laminar-flow bench and sample-prep table run along the north wall where ducts and water lines come "
           "from above; the order follows the workflow - prepare, wash, handle cleanly.")
    row = seq(R, B, "N", ["labbench_fume_hood", "labbench_wet_bench_sink", "labbench_laminar_flow_bench", "labbench_sample_prep_table",
                          "labbench_cleanroom_glove_box"], 1.8, gap=0.06)
    prep = row[3] if len(row) > 3 else None
    R.line("Benchtop instruments",
           "A microscope, centrifuge and thermal cycler stand on the sample-prep table, so a sample can be examined and spun down without "
           "moving it across the room.")
    if prep:
        top(R, B, prep, ["microscope_optical_microscope", "analyzer_centrifuge", "analyzer_thermal_cycler"], step=0.45, quiet=True)
    R.line("Island reagent bench and stools",
           "The island bench in the middle of the room is the shared working surface for assembling experiments, with stools on both "
           "long sides and 1.2 m of clear floor all round.")
    isl = put(R, B, "labbench_island_reagent_bench", 7.0, 7.4, 0.0)
    if isl:
        x0, z0, x1, z1 = isl["_fp"]
        for dx in (-0.6, 0.6):
            put(R, B, "labbench_lab_stool", (x0 + x1) / 2 + dx, z0 - 0.45, 0.0, quiet=True)
            put(R, B, "labbench_lab_stool", (x0 + x1) / 2 + dx, z1 + 0.45, 180.0, quiet=True)
    R.line("Analysers and incubator",
           "Mass spectrometer, CO2 incubator and a materials analyser stand against the south wall, where the cabling can drop from the ceiling "
           "trays and heat is exhausted away from the wet benches.")
    seq(R, B, "S", ["analyzer_mass_spectrometer", "analyzer_co2_incubator", "microscope_electron_microscope"], 1.8, gap=0.08, quiet=True)
    R.line("Specimens and biocontainment",
           "A biocontainment cabinet holds hazardous samples, a seed vault the reference collection, both in the far corner from the "
           "door and out of the traffic route, with a hazard sign on the cabinet wall.")
    wall_first(R, B, "S", "specimen_biocontainment_cabinet", (6.95, 7.0, 6.9))
    wall_first(R, B, "S", "specimen_seed_vault", (8.3, 8.35, 8.4), quiet=True)
    wi(R, B, "S", "sign_hazard_biohazard", 6.95, y=2.75, quiet=True)
    R.line("Instrument cabinets",
           "Cabinets beside the door keep glassware, probe kits and instruments near where they are used; locked as a rule.")
    wall_first(R, B, "W", "cabinet_utility_cabinet", (4.4, 4.5, 4.3), quiet=True)
    wall_first(R, B, "W", "storagebin_drawer_cabinet", (5.4, 5.3), quiet=True)
    wall_first(R, B, "W", "cabinet_janitor_closet", (9.3, 9.4), quiet=True)
    R.line("Gas cylinder rack",
           "Nitrogen and breathing-air cylinders in a chained rack between the desks and the incubator supply the analysers; kept "
           "together so a leak can be isolated at one valve.")
    wall_first(R, B, "S", "cylinder_nitrogen_cylinder_trio", (9.6, 9.7), quiet=True)
    wi(R, B, "S", "cylinder_gas_manifold_panel", 9.6, y=1.5, quiet=True)
    R.line("Emergency shower and eye wash",
           "A drench shower and eye-wash station stand at the north-east end of the benches, within 3 m of the fume hood and with a clear "
           "approach, as regulations require.")
    wall_first(R, B, "N", "safety_emergency_shower", (12.3, 12.2, 12.1))
    wi(R, B, "N", "safety_eye_wash_station", 11.5, y=1.1, quiet=True)
    wi(R, B, "N", "sign_hazard_high_voltage", 12.3, y=2.6, quiet=True) if False else None
    R.line("Data desks",
           "A workstation with terminal on the south wall by the window lets researchers enter results without leaving the room; "
           "it sits away from wet work and keeps the window view.")
    for x in (11.9,):
        d = wall_first(R, B, "S", "desk_workstation", (x, x + 0.1, x - 0.1), quiet=True)
        if d:
            top(R, B, d, ["terminal_desk_terminal"], quiet=True)
            seat_facing(R, d, cats=("chair",), gap=0.3, label="swivel_office")
    R.line("Display and plants",
           "A wall display shows the experiment schedule; a bonsai on the desk keeps the room livable.")
    wi(R, B, "W", "display_status_board", 10.3, y=1.8, quiet=True)
    if d:
        top(R, B, d, ["plant_bonsai"], dx=0.5, quiet=True)
    R.line("Safety, signs and cleaning",
           "Extinguisher and first-aid cabinet by the door, a department sign over it, and a spill kit near the fume hood.")
    wi(R, B, "W", "safety_fire_extinguisher", 8.9, y=1.1, quiet=True)
    wi(R, B, "W", "safety_first_aid_cabinet", 5.0, y=1.3, quiet=True)
    wall_first(R, B, "E", "safety_spill_kit_bin", (4.6, 4.5), quiet=True) if False else None
    dsign(R, B, "W", 7.3, "dept_science", y=3.0)
    R.line("Ceiling lighting and extract",
           "Daylight-colour panels (500 lux) over benches; an extract diffuser over the fume hood, sprinklers for fire suppression.")
    ext_lights(R, B, spacing=3.6, color="#f4f8ff") if False else ext_lights(R, B, spacing=3.6)
    R.place(M(B, "duct_ceiling_round_vent"), 3.5, 5.0, 0.0, y=R.y + R.h)
    R.place(M(B, "safety_sprinkler_head"), 7.0, 5.3, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- HYDROPONICS
def f_hydro(R, B):
    R.describe(
        "Hydroponic garden that grows fresh vegetables and herbs for the galley and keeps the air fresh; also the quietest place on the deck "
        "to sit, with a small seating nook by the big stern window.",
        basis="About 69 m2 with a 3.6 m ceiling for grow lights and hanging arrays.  Two growing rows of trays and racks run east-west with "
              "1.2 m service aisles; vertical towers on the west wall; water, pumps and nutrient dosing along the north wall so pipes stay short "
              "and dry and spills run to one drain; seating nook by the window; tall racks kept 0.5 m off all windows.",
        crew=3, adjacency="Corridor door on the west wall; science lab forward (north); crew quarters across the corridor; galley gets produce via the corridor.")
    R.line("Water tank and pumps",
           "Potable water tank, filtration unit and circulation pump stand along the north wall in one line; the garden's water loop is "
           "kept together so a leak is found quickly and the tank's weight sits on the deck's main frame.")
    seq(R, B, "N", ["watertank_potable_water_tank", "tank_filtration_unit", "tank_circulation_pump"], 4.0, gap=0.08)
    R.line("Nutrient dosing",
           "A nutrient tote tank and two dosing drums feed the pumps through metered lines; they stand at the end of the water line so "
           "concentrate never travels across the garden.")
    seq(R, B, "N", ["tank_tote_tank", "barrel_plastic_drum_lidded", "barrel_plastic_drum_lidded"], 8.2, gap=0.08, quiet=True)
    R.line("Growing row one",
           "Wheat trays, a lettuce trough, a herb shelf and a microgreen rack in the first row, at 1.2 m from the water line so workers "
           "can walk to the tanks; staple crops sit nearest the door.")
    row1 = []
    x = 4.3
    for mid in ("planter_wheat_tray_bed", "planter_lettuce_trough", "planter_herb_shelf_rack", "planter_microgreen_rack"):
        p = put(R, B, mid, x + M(B, mid)["size"][0] / 2, 13.55, 0.0, quiet=True)
        if p:
            row1.append(p)
            x += M(B, mid)["size"][0] + 0.1
    R.line("Growing row two",
           "Tomato vine rack, strawberry tiers and a mushroom shelf form the second row, leaving a 1.2 m aisle between rows; "
           "row two stays 2 m from the window so nothing tall shades the nook.")
    row2 = []
    x = 4.3
    for mid in ("planter_tomato_vine_rack", "planter_strawberry_tiered_planter", "planter_mushroom_shelf"):
        p = put(R, B, mid, x + M(B, mid)["size"][0] / 2, 15.35, 0.0, quiet=True)
        if p:
            row2.append(p)
            x += M(B, mid)["size"][0] + 0.1
    R.line("Vertical grow towers",
           "Vertical towers along the west wall use height instead of floor for leafy crops, doubling yield per square metre; "
           "their pumps are fed from the north-wall water line.")
    for z in (11.75, 12.55, 16.6, 17.4):
        wall_first(R, B, "W", "planter_vertical_grow_tower", (z,), quiet=True)
    R.line("Grow lights",
           "Hanging grow-light arrays above the rows give the full spectrum the crops need on a 12 h cycle; fixtures hang over each planter "
           "run at 0.6 m above the crop.")
    for p in row1 + row2:
        x0, z0, x1, z1 = p["_fp"]
        if p["_m"]["size"][0] < 1.3:
            continue
        R.place(M(B, "planter_hanging_grow_light_array"), (x0 + x1) / 2, (z0 + z1) / 2, 0.0, y=R.y + R.h)
    R.place(M(B, "planter_grow_light_bar_panel"), 8.7, 13.55, 0.0, y=R.y + R.h)
    R.place(M(B, "planter_grow_light_bar_panel"), 8.7, 15.35, 0.0, y=R.y + R.h)
    R.line("Seating nook by the window",
           "A low bench under the stern window, a round table and two armchairs form a quiet corner where crew sit among the plants and look "
           "out; the bench stays below the sill and nothing tall blocks the glass.")
    wall(R, B, "S", "bench_mess_bench", 5.25)
    tb = first(R, B, "table_round_mess_table", [(5.25, 16.45, 0.0), (5.25, 16.3, 0.0)], quiet=True)
    if tb:
        x0, z0, x1, z1 = tb["_fp"]
        put(R, B, "chair_armchair", x0 - 0.55, (z0 + z1) / 2, 90.0, quiet=True)
        put(R, B, "chair_armchair", x1 + 0.55, (z0 + z1) / 2, -90.0, quiet=True)
        top(R, B, tb, ["tableware_teapot", "tableware_cups_and_mugs"], step=0.4, quiet=True)
    R.line("Tool storage and cleaning",
           "Tool cabinets and a cleaning drone by the door keep trimming, pruning and cleaning gear where the work starts; a wet bin for "
           "trimmings goes to the recycler.")
    wall_first(R, B, "N", "cabinet_utility_cabinet", (2.4, 2.5), quiet=True)
    wall_first(R, B, "N", "cabinet_janitor_closet", (3.3, 3.25), quiet=True)
    wall_first(R, B, "S", "cleaningbot_floor_scrubber_disc", (2.5, 2.6), quiet=True)
    wall_first(R, B, "S", "bin_trash_bin", (8.2, 8.3), quiet=True)
    wi(R, B, "W", "engtool_tool_rack", 14.5, y=1.6, quiet=True) if False else None
    R.line("Pipes and air",
           "Insulated water pipes run overhead above the tanks, and the air handler supplies humidity-controlled air to the crops; "
           "a humidity unit on the north wall keeps the garden at 70 % RH.")
    wall_first(R, B, "N", "scrubber_humidity_control_unit", (11.3, 11.5), quiet=True)
    for xx in (5.0, 7.0, 9.0):
        wi(R, B, "N", "pipe_insulated_wrapped", xx, y=2.85, quiet=True)
    R.place(M(B, "pipe_ceiling_insulated_pair"), 7.2, 11.6, 0.0, y=R.y + R.h)
    R.place(M(B, "duct_ceiling_square_diffuser"), 11.0, 13.9, 0.0, y=R.y + R.h)
    R.line("Plants and notices",
           "A ficus, a hanging plant and a notice board with the harvest roster make the garden a pleasant place to pass through.")
    wall_first(R, B, "S", "plant_ficus_tree", (2.6, 2.7), quiet=True)
    R.place(M(B, "plant_hanging_plant"), 3.8, 16.8, 0.0, y=R.y + R.h)
    wi(R, B, "W", "noticeboard_duty_roster_display", 12.3, y=1.5, quiet=True)
    R.line("Safety and signs",
           "Extinguisher and first-aid cabinet by the door, a department sign over it, and a sprinkler over the rows.")
    wi(R, B, "W", "safety_fire_extinguisher", 16.8, y=1.1, quiet=True)
    wi(R, B, "W", "safety_first_aid_cabinet", 12.9, y=1.3, quiet=True)
    dsign(R, B, "W", 14.5, "dept_science", y=3.05)
    R.place(M(B, "safety_sprinkler_head"), 7.0, 14.45, 0.0, y=R.y + R.h)
    R.line("Ceiling lighting",
           "Warm general lights on a wide grid (200 lux) for people; growth is lit by the grow arrays.")
    ext_lights(R, B, spacing=4.0, energy=1.0)
    food_hydro(R, B)
