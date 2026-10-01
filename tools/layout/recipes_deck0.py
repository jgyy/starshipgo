"""Room recipes - Deck 0 (Sky Deck): the lens-shaped dome on top of the ship.

Star Cartography at the bow, the Briefing Theatre and Officers' Wardroom on the forward cross passage and the
library, observatory, arboretum and flag officer's suite aft.  Every placement belongs to a BOM line that says why it is there.
"""
import math

from recipes_deck2_helpers import *   # noqa: F401,F403


# ----------------------------------------------------------------------------------------------- helpers
def _lights(R, B, spacing=4.2, energy=1.2, color="#fff0dd", wide=False, **kw):
    """Ceiling fixtures (each with a real spot light) on a regular grid: small downlights unless `wide`."""
    if wide:
        pred = lambda m: m["mount"] == "ceiling" and m["size"][1] < 0.3 and m["size"][0] < 1.7 and m["size"][2] < 1.7
    else:
        pred = lambda m: m["mount"] == "ceiling" and m["size"][1] < 0.3 and m["size"][0] < 1.1 and m["size"][2] < 1.1
    R.light_grid(cats=("ceilinglight",), spacing=spacing, energy=energy, color=color, pred=pred, **kw)


def _ceil(R, B, mid, x, z, yaw=0.0):
    return R.place(M(B, mid), x, z, yaw, y=R.y + R.h)


def _polar(cx, cz, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cz + r * math.sin(a)


def _face(x, z, tx, tz):
    return yaw_to(x, z, tx, tz)


def _sconces_between_windows(R, B, sides, mid="sconce_frosted_glass_shell", y=1.9):
    """One wall light on the short pier between two neighbouring hull windows."""
    for s in sides:
        e = R.edge(s)
        if e is not None:
            wi(R, B, s, mid, e["len"] - 0.16, y=y, quiet=True)


def _chairs(R, B, mid, pts, centre, **kw):
    """Chairs at (x, z) points all turned toward `centre`."""
    out = []
    for (x, z) in pts:
        out.append(put(R, B, mid, x, z, _face(x, z, centre[0], centre[1]), **kw))
    return out


# ----------------------------------------------------------------------------------------------- STAR CARTOGRAPHY
def f_starcart(R, B):
    R.describe(
        "The ship's exploration heart: a darkened, domed chart room at the bow where the navigators, astrometrists and the captain "
        "build the picture of where the ship is and where it is going.  A holographic star-map table stands in the middle, ringed by "
        "operator stations, with the great wall of star charts on the curved bow walls and the bow windows left free for the real stars.",
        basis="26 m x 12 m, 4.2 m high.  The star-map table sits on the ship's centre line 6 m behind the bow glass so everybody looking "
              "at it also sees the stars; navigation and sensor stations form two wings (one per side) with their backs to the chart "
              "walls; data racks flank the entry; 1.2 m or wider aisles everywhere and a straight 3 m route from the entry to the table.  "
              "Light is dim and blue over the table, warmer at the stations so screens stay readable.",
        crew=12, adjacency="Forward spine corridor through the 3 m opening in the aft wall; hull windows all round the bow; "
                           "the bridge is one deck below through the stair towers.")
    C = (0.0, -14.0)           # centre of the star-map table
    R.keep_clear((-1.5, -12.6, 1.5, -9.0), "straight 3 m route from the entry to the star-map table")

    R.line("Star-map table",
           "The briefing table is the room's centre: a holographic star map is projected over it, so the whole crew can plan jumps and "
           "survey routes round the same 3-D chart.  It stands on the centre line, in line with the entry and the bow window.")
    table = put(R, B, "holo_briefing_table", C[0], C[1], 0.0)
    R.line("Table crew stools",
           "Six science stools ring the table at arm's length so navigators can lean in and reach into the projection; the south side "
           "stays open so people walking in from the corridor see the map first.")
    for i in range(6):
        x, z = _polar(C[0], C[1], 1.65, 150 + i * 48)
        put(R, B, "seat_science_stool", x, z, _face(x, z, *C), quiet=True)
    R.line("Captain's podium",
           "The captain briefs the room from a podium at the head of the table with the bow glass behind; it is a low console so "
           "the stars stay visible over it.")
    pod = put(R, B, "console_captain_podium", 0.0, -17.7, 0.0)
    R.line("Wing consoles around the table",
           "Navigation, sensor, science and ops stations stand in a loose arc on each side of the table facing it, so each operator feeds the "
           "map while watching it; consoles are 1.2 m or more apart for a seated operator to pass behind.")
    wing = [("console_navigation", 163), ("console_sensor", 197), ("console_science", 17), ("console_ops", -17)]
    for mid, a in wing:
        x, z = _polar(C[0], C[1], 5.3, a)
        c = put(R, B, mid, x, z, _face(x, z, *C), quiet=True)
        if c is None:
            c = first(R, B, mid, [(x + dx, z + dz, _face(x + dx, z + dz, *C)) for dx, dz in ((0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3))])
        sx, sz = _polar(C[0], C[1], 4.15, a)
        put(R, B, "seat_ops_chair" if a in (163, 17) else "seat_tactical_chair", sx, sz, _face(sx, sz, x, z), quiet=True)
    R.line("Visitors' gallery",
           "Two curved benches on the entry side let guests, trainees and off-watch officers follow a briefing without standing in the "
           "operators' way; they face the table across the open route from the door.")
    put(R, B, "bench_curved_lounge_bench", -3.6, -10.1, 180.0)
    put(R, B, "bench_curved_lounge_bench", 3.6, -10.1, 180.0)

    R.line("Aft wall navigation bays",
           "Along the aft wall west of the entry three more stations - navigation, ops and communications - serve the crew who work "
           "on stellar position fixes and probe telemetry; each operator sits facing the aft wall displays above the console.")
    w_cons = []
    for mid, x in (("console_environmental", -6.6), ("console_flight_control", -8.6), ("console_damage_control", -10.4)):
        c = wall(R, B, "S", mid, x, quiet=True)
        w_cons.append(c)
        if c is not None:
            seat_facing(R, c, cats=("seat",), gap=0.3, label="ops_chair")
    for mid, x in (("console_communications", 6.6), ("console_helm", 8.5), ("console_transporter_control", 10.3)):
        c = wall(R, B, "S", mid, x, quiet=True)
        if c is not None:
            seat_facing(R, c, cats=("seat",), gap=0.3, label="comms_chair" if "comm" in mid else "helm_chair")
    R.line("Aft wall display banks",
           "Screens above the aft consoles repeat what the table shows and carry telemetry from probes and buoys, high enough (centre 2.3 m) "
           "to be read from the whole room.")
    for x, mid in ((-6.6, "display_tactical_wall_screen"), (-9.2, "display_triple_stack"), (-10.6, "display_triple_stack"),
                   (6.8, "display_tactical_wall_screen"), (9.2, "display_triple_stack"), (10.6, "display_triple_stack")):
        wi(R, B, "S", mid, x, y=2.45, quiet=True)
    wi(R, B, "S", "display_ticker_banner", -4.0, y=3.35, quiet=True)
    wi(R, B, "S", "display_ticker_banner", 4.0, y=3.35, quiet=True)

    R.line("Data racks",
           "The star catalogue, sensor logs and the table's rendering cluster live in racks beside the entry, close to the consoles that "
           "use them and short cable runs from the cable trays overhead; a different rack type in each slot (crystal archive, GPU, "
           "quantum, storage array).")
    seq(R, B, "S", ["rack_crystal_archive_tower", "rack_gpu_cluster_rack", "rack_cryogenic_quantum_rack"], -2.0, gap=0.04, direction=-1)
    seq(R, B, "S", ["rack_storage_array", "rack_photonic_fiber_rack", "rack_blade_server_rack"], 2.0, gap=0.04, direction=1)

    R.line("The great wall of star charts",
           "The slanting bow walls carry the ship's chart library as framed holographic panels and circular sector displays: constellations, "
           "surveyed systems, nebula and the current route; each panel is lit by its own glow so it reads as a window onto space.")
    for s, mids in (("D0", ["display_hex_display"]), ("D1", ["display_circular_display"]), ("D2", ["display_hex_display"]),
                    ("D13", ["display_circular_display"]), ("D14", ["display_hex_display"]), ("D15", ["display_circular_display"]),
                    ("D17", []), ("D16", [])):
        e = R.edge(s)
        if e is None:
            continue
        for mid in mids:
            wi(R, B, s, mid, e["len"] / 2, y=1.9, quiet=True)
    for s, c in (("N", -3.0), ("N", 3.0)):
        wi(R, B, s, "display_tactical_wall_screen", c, y=2.3, quiet=True)
    for s in ("D0", "D2", "D13", "D15"):
        e = R.edge(s)
        if e:
            wi(R, B, s, "panellight_backlit_rectangle", e["len"] / 2, y=0.9, quiet=True)
    R.line("Wall lights between the bow windows",
           "Each short pier between two bow windows carries a frosted wall light, so the curve of the bow glass is outlined softly "
           "without glare on the screens.")
    _sconces_between_windows(R, B, ["D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11"])

    R.line("Telescopes and star trackers",
           "A star-tracker scope and an astrometric dish stand near the bow glass so the navigators can calibrate the chart against "
           "the real sky; they are kept a metre back from the windows so the glass stays clear.")
    first(R, B, "telescope_star_tracker_scope", [(-5.5, -16.6, 150.0), (-6.0, -16.0, 150.0), (-5.0, -16.0, 150.0)])
    first(R, B, "telescope_astrometric_dish", [(5.5, -16.4, -150.0), (6.0, -16.0, -150.0), (5.0, -16.0, -150.0)])
    first(R, B, "telescope_spectrograph_tripod", [(-3.2, -17.2, 160.0), (-3.0, -16.6, 160.0)])
    first(R, B, "telescope_observation_telescope", [(3.2, -17.2, -160.0), (3.0, -16.8, -160.0)])

    R.line("Sector globes and plinths",
           "Smaller holographic projectors on both wings show a single sector in detail or the ship's own position: the map globe at "
           "the west and the ship schematic projector at the east.")
    first(R, B, "holo_star_map_globe", [(-8.0, -12.6, 0.0), (-8.4, -12.4, 0.0), (-7.6, -12.0, 0.0)])
    first(R, B, "holo_ship_schematic_projector", [(8.0, -12.6, 0.0), (8.4, -12.4, 0.0), (7.6, -12.0, 0.0)])

    R.line("Paper-style chart tables",
           "Two chart tables with a clear top, one per wing, carry the navigators' astrolabe, sextant and chronometers - the "
           "traditional instruments they use to cross-check the computer; the tops are otherwise left empty for spreading charts.")
    for side, x in ((-1, -9.6), (1, 9.6)):
        t = first(R, B, "table_briefing_table", [(x, -12.0, 0.0), (x * 0.97, -11.8, 0.0)])
        if t:
            top(R, B, t, ["instrument_astrolabe", "instrument_sextant"] if side < 0 else ["instrument_brass_chronometer", "instrument_nav_compass"],
                step=0.5, quiet=True)

    R.line("Green corners",
           "Plants soften the dome: a ficus tree by each chart wall and low planter boxes in front of the bow glass (under the sill, so the "
           "view stays free) keep the long hours in the dark room humane.")
    first(R, B, "plant_ficus_tree", [(-11.4, -9.4, 0.0), (-11.2, -9.6, 0.0)], quiet=True)
    first(R, B, "plant_ficus_tree", [(11.4, -9.4, 0.0), (11.2, -9.6, 0.0)], quiet=True)
    first(R, B, "plant_planter_box", [(-3.2, -19.0, 0.0), (-2.9, -18.9, 0.0)], quiet=True)
    first(R, B, "plant_planter_box", [(3.2, -19.0, 0.0), (2.9, -18.9, 0.0)], quiet=True)
    first(R, B, "plant_fern", [(-7.0, -10.3, 0.0)], quiet=True)

    R.line("Ceiling lighting and star-map halo",
           "Soft cool downlights give only 100 lux so the hologram stays vivid, with a ring light directly above the star-map table; the "
           "light over the podium is a warmer stage spot so the speaker is visible.")
    _lights(R, B, spacing=4.4, energy=0.8, color="#bcd4ff", x_margin=1.4)
    _ceil(R, B, "ceilinglight_ring_light", C[0], C[1])
    _ceil(R, B, "spotlight_stage_truss_lights", 0.0, -17.6)
    R.omni(C[0], R.y + 3.2, C[1], color="#4a9bff", energy=1.6, rng_=7.0)
    R.omni(-8.0, R.y + 2.2, -12.4, color="#6aa8ff", energy=0.8, rng_=4.5)
    R.omni(8.0, R.y + 2.2, -12.4, color="#6aa8ff", energy=0.8, rng_=4.5)
    R.omni(0.0, R.y + 2.5, -18.0, color="#ffe2b0", energy=0.7, rng_=4.0)
    R.omni(-8.5, R.y + 2.8, -9.0, color="#ffd9a8", energy=0.6, rng_=5.0)
    R.omni(8.5, R.y + 2.8, -9.0, color="#ffd9a8", energy=0.6, rng_=5.0)
    R.line("Safety and signs",
           "An extinguisher beside each aft wall bay, the science department sign over the entry and the exit sign keep the room "
           "compliant even though it is kept dark.")
    wi(R, B, "S", "safety_fire_extinguisher", -1.9, y=1.1, quiet=True)
    wi(R, B, "S", "safety_fire_extinguisher", 1.9, y=1.1, quiet=True)
    dsign(R, B, "S", 0.0, "dept_science", y=3.75)
    wi(R, B, "S", "clock_dual_time_ship_clock", -12.0, y=3.2, quiet=True)


# ----------------------------------------------------------------------------------------------- BRIEFING THEATRE
def f_theatre(R, B):
    R.describe(
        "Tiered-seating briefing room for the whole officer corps: mission briefings, science lectures and film nights are given here "
        "to up to 24 people facing a wall-size display, with a lectern and a holographic projector for the speaker.",
        basis="11.5 m x 8 m.  The display wall is the north wall; 4 rows of 6 seats at 1.1 m pitch with a 1.0 m centre aisle (seat "
              "heights rise from the front row to the back row so every head sees the screen); the speaker's zone in front of the screen "
              "is 2.3 m deep; the 2 m door zone and its walkway stay clear; the projection console is at the back.",
        crew=24, adjacency="Forward spine corridor through the 2.4 m door in the east wall; hull windows on the west wall are "
                           "screened by the audience-side wall lights.")
    R.line("Display wall",
           "A wall-size viewscreen on the north wall is the point of the room; two tactical screens beside it show the agenda or a second "
           "image.  The audience looks along the room's long axis so nobody sits at a bad angle.")
    wi(R, B, "N", "display_main_viewscreen", -7.5, y=1.75)
    wi(R, B, "N", "display_tactical_wall_screen", -11.6, y=2.0, quiet=True)
    wi(R, B, "N", "display_tactical_wall_screen", -3.4, y=2.0, quiet=True)
    R.line("Lectern and projector",
           "The speaker stands at the captain's podium beside the screen's centre; a briefing projector next to it throws 3-D plots "
           "(courses, formations) into the space in front of the first row.")
    put(R, B, "console_captain_podium", -7.5, -6.6, 0.0)
    put(R, B, "holo_briefing_projector", -10.2, -6.5, 0.0)
    put(R, B, "holo_comm_bust_projector", -4.8, -6.6, 0.0)
    R.line("Speaker's table",
           "A small table by the lectern holds a water jug and cups for long briefings and the speaker's datapads.")
    t = put(R, B, "table_side_table", -5.7, -6.9, 0.0)
    top(R, B, t, ["tableware_pitcher"], quiet=True)
    R.line("Audience seating, rows 1 and 2",
           "The two front rows use ordinary stackable chairs (mess and folding chairs) that can be removed for a standing briefing; "
           "each row is split by a 1.0 m centre aisle that gives access to the seats without climbing over anybody.")
    xs = (-11.4, -10.4, -9.4, -6.9, -5.9, -4.9)
    for x in xs:
        put(R, B, "chair_mess_chair", x, -4.4, 180.0, quiet=True)
        put(R, B, "chair_folding_chair", x, -3.3, 180.0, quiet=True)
    R.line("Audience seating, rows 3 and 4",
           "The back rows use taller seats - swivel chairs and then bar stools - which lifts the heads of the back row above the front "
           "rows exactly as a stepped floor would, so the screen stays visible from every seat.")
    for x in xs:
        put(R, B, "chair_swivel_office_chair", x, -2.2, 180.0, quiet=True)
        put(R, B, "couch_bar_stool", x, -1.1, 180.0, quiet=True)
    R.line("Projection and sound console",
           "A control console at the back of the room, facing the screen, runs the display wall, the speakers and the room lights; the "
           "operator can see the whole audience.")
    c = wall(R, B, "S", "console_ops", -2.9)
    if c:
        seat_facing(R, c, cats=("seat",), gap=0.3, label="ops_chair")
    wi(R, B, "S", "commsunit_speaker_grille", -6.0, y=2.6, quiet=True)
    wi(R, B, "S", "commsunit_speaker_grille", -9.0, y=2.6, quiet=True)
    R.line("Refreshment point",
           "Coffee and a water cooler by the door let people take a drink into the theatre without queueing in the corridor.")
    wall(R, B, "E", "galley_coffee_machine", -6.7, quiet=True)
    wall(R, B, "E", "fountain_water_cooler_tower", -7.6, quiet=True)
    R.line("Side storage",
           "A wall cabinet for the projector's spare lamps, remotes and cables hangs at the back of the room, out of the speaker's sight and "
           "above the back-row seats.")
    wi(R, B, "S", "cabinet_wall_storage_lockers", -10.4, y=1.5, quiet=True)
    R.line("Plants and wall lights",
           "A ficus at the speaker's end and sconces along the walls give the room a warmer, more finished look than a bare bulkhead and "
           "keep the aisles lit when the screen is dark.")
    first(R, B, "plant_ficus_tree", [(-12.3, -7.2, 0.0), (-12.1, -7.0, 0.0)], quiet=True)
    first(R, B, "plant_ficus_tree", [(-2.6, -7.2, 0.0), (-2.8, -7.0, 0.0)], quiet=True)
    for x in (-11.9, -8.6, -6.0, -4.3):
        wi(R, B, "S", "sconce_art_deco_fan", x, y=1.9, quiet=True)
    for z in (-6.9, -0.8):
        wi(R, B, "E", "sconce_art_deco_fan", z, y=1.9, quiet=True)
    wi(R, B, "W", "sconce_lantern_sconce", -6.5, y=1.9, quiet=True)
    wi(R, B, "W", "sconce_lantern_sconce", -0.7, y=1.9, quiet=True)
    wi(R, B, "W", "sconce_lantern_sconce", -3.0, y=1.9, quiet=True)
    R.line("Stage and house lighting",
           "A stage truss with spots over the lectern lights the speaker; dimmable downlights over the audience are low so the screen "
           "is not washed out; a cool omni glows from the display wall onto the front rows.")
    _lights(R, B, spacing=3.4, energy=0.9, color="#ffe8cc", x_margin=1.0)
    _ceil(R, B, "spotlight_stage_truss_lights", -7.5, -6.4)
    R.omni(-7.5, R.y + 2.4, -6.0, color="#79b4ff", energy=1.1, rng_=6.0)
    R.omni(-8.0, R.y + 2.8, -2.2, color="#ffd9a8", energy=0.6, rng_=5.5)
    R.line("Safety and signs",
           "Extinguisher by the door, an exit sign above it and the bridge-department sign mark the theatre as a command space.")
    wi(R, B, "E", "safety_fire_extinguisher", -1.0, y=1.1, quiet=True)
    wi(R, B, "E", "sign_exit_arrow", -2.1, y=2.45, quiet=True, check=False)
    dsign(R, B, "E", -4.0, "dept_bridge", y=3.1)


# ----------------------------------------------------------------------------------------------- WARDROOM
def f_wardroom(R, B):
    R.describe(
        "The officers' club of the ship: a formal dining table for the captain's dinners, a bar with a small galley behind it, and a "
        "lounge by the starboard window where off-duty officers talk, read and watch the stars.",
        basis="11.5 m x 8 m, 3.4 m high.  Bar and back-bar along the north wall (about 4 m of counter, 1.0 m service gap behind it), "
              "dining table for 8 in the open south-west half with 1.3 m chair aisles, lounge group in front of the 2.6 m window, "
              "fireplace nook in the north-east corner, drinks and snack machines beside the door.  The door zone and the straight route "
              "from the door to the window stay clear.",
        crew=20, adjacency="Forward spine corridor through the west door; hull window on the starboard wall; the galley is a deck below, so "
                           "the bar keeps its own refrigerator, dishwasher and coffee machine.")
    R.line("Back bar equipment",
           "A refrigerator, dishwasher, sink and coffee machine stand against the north wall behind the counter, so the steward never "
           "leaves the bar to wash glasses or fetch ice.")
    seq(R, B, "N", ["galley_refrigerator", "galley_coffee_machine", "galley_sink_unit", "galley_dishwasher"], 4.2, gap=0.03)
    R.line("Bar counter",
           "Three counter modules form the bar: customers sit on the south side, the steward works on the north side; the 1.1 m gap "
           "between the counter and the back-bar units is a comfortable working aisle.")
    bars = [put(R, B, "table_bar_counter", x, -5.5, 0.0) for x in (5.1, 6.9, 8.7)]
    for b, mids in zip(bars, (["tableware_bottle_and_glasses", "tableware_cups_and_mugs"], ["tableware_bread_basket", "tableware_condiments"],
                              ["tableware_bottle_and_glasses", "tableware_fruit_bowl"])):
        top(R, B, b, mids, step=0.55, quiet=True)
    R.line("Bar stools",
           "Four stools along the customer side of the bar (one per 1.3 m of counter, so a person can slip between two of them) give a place to perch with a drink.")
    for x in (4.7, 6.0, 7.3, 8.6):
        put(R, B, "couch_bar_stool", x, -4.7, 180.0, quiet=True)
    R.line("Drinks and snack machines",
           "Machines beside the door sell soft drinks and snacks around the clock, when the steward is off duty, and keep the queue "
           "out of the bar.")
    wall(R, B, "W", "vending_drink_machine", -7.2, quiet=True)
    wall(R, B, "W", "vending_snack_machine", -6.15, quiet=True)
    wall(R, B, "W", "fountain_water_cooler_tower", -0.7, quiet=True)

    R.line("Dining table",
           "A 3 m table seats eight for the captain's dinner and for working lunches; it stands in the middle of the south-west half "
           "so servers and guests can walk all round it.")
    dt = put(R, B, "table_conference_table", 5.6, -1.7, 0.0)
    R.line("Dining chairs",
           "Six mess chairs on the long sides and an armchair at each end (host and guest of honour); every chair faces the table "
           "and is tucked in 0.1 m from it.")
    if dt:
        x0, z0, x1, z1 = dt["_fp"]
        xm = (x0 + x1) / 2
        for dx in (-0.9, 0.0, 0.9):
            put(R, B, "chair_mess_chair", xm + dx, z0 - 0.35, 0.0, quiet=True)
            put(R, B, "chair_mess_chair", xm + dx, z1 + 0.35, 180.0, quiet=True)
        put(R, B, "chair_armchair", x0 - 0.55, (z0 + z1) / 2, 90.0, quiet=True)
        put(R, B, "chair_armchair", x1 + 0.55, (z0 + z1) / 2, -90.0, quiet=True)
    R.line("Table setting",
           "The table is laid for dinner: plates, cutlery, glasses, a teapot and a fruit bowl and bread basket in the middle.")
    top(R, B, dt, ["tableware_plate_stack", "tableware_bottle_and_glasses", "tableware_fruit_bowl", "tableware_bread_basket",
                   "tableware_pitcher"], step=0.5, quiet=True)
    top(R, B, dt, ["tableware_cutlery_set", "tableware_cups_and_mugs", "tableware_teapot", "tableware_salad"], dz=0.28, step=0.65, quiet=True)
    R.line("Sideboard",
           "Wall cabinets along the south wall hold the good glassware and the ship's silver and a display case shows the mission trophies; a ficus fills the corner.")
    first(R, B, "plant_ficus_tree", [(2.4, -0.9, 0.0)], quiet=True)
    wi(R, B, "S", "locker_display_cabinet", 4.3, y=1.7, quiet=True)
    wi(R, B, "S", "locker_display_cabinet", 5.5, y=1.7, quiet=True)
    wi(R, B, "S", "locker_mirror_cabinet", 7.0, y=1.8, quiet=True)

    R.line("Window lounge",
           "A three-seater sofa faces the starboard window across a low coffee table; two lounge armchairs make the group conversational.  "
           "Seating is kept 1.7 m from the glass so the window stays clear.")
    sofa = put(R, B, "couch_three_seater_sofa", 9.9, -2.3, 90.0)
    ct = put(R, B, "table_coffee_table", 11.4, -3.0, 90.0)
    top(R, B, ct, ["tableware_teapot", "tableware_cups_and_mugs"], step=0.35, quiet=True)
    put(R, B, "couch_lounge_armchair", 11.6, -0.9, -150.0, quiet=True)
    top(R, B, ct, ["instrument_astrolabe"], dz=0.0, dx=0.0, step=0.0, quiet=True)
    first(R, B, "couch_lounge_armchair", [(11.7, -5.2, -30.0)], quiet=True)
    first(R, B, "couch_ottoman", [(11.0, -1.2, 90.0)], quiet=True)
    R.line("Fireplace nook",
           "Holographic fire in a wall frame in the north-east corner is the ship's 'hearth': an armchair and a side table face it, "
           "with a lamp - warm light and a corner for quiet talk.")
    wi(R, B, "N", "display_holo_frame_panel", 11.4, y=1.3, quiet=True)
    first(R, B, "chair_lounge_chair", [(11.4, -6.0, 180.0)], quiet=True)
    first(R, B, "plant_ficus_tree", [(12.2, -7.2, 0.0)], quiet=True)
    sd = first(R, B, "table_side_table", [(12.3, -5.9, 0.0)], quiet=True)
    top(R, B, sd, ["lamp_table_lamp"], quiet=True)
    R.line("Plants and decoration",
           "A ficus tree and a fern soften the corners, a bonsai sits on the bar and a floor lamp "
           "marks the corner beside the hearth; a bulletin board and a ship's chronometer hang by the door.")
    first(R, B, "plant_ficus_tree", [(2.5, -7.2, 0.0), (2.6, -7.0, 0.0)], quiet=True)
    first(R, B, "plant_fern", [(12.1, -0.8, 0.0)], quiet=True)
    top(R, B, bars[1], ["plant_bonsai"], dz=-0.15, quiet=True)
    first(R, B, "lamp_floor_lamp", [(10.1, -7.45, 0.0)], quiet=True)
    wi(R, B, "W", "noticeboard_cork_bulletin_board", -1.2, y=1.7, quiet=True)
    wi(R, B, "W", "clock_analogue_chronometer", -2.0, y=2.5, quiet=True)
    R.line("Lighting",
           "Warm pendant fixtures over the bar and dining table, soft downlights elsewhere, and warm omni lamps over the lounge and the "
           "fireplace nook create evening light, brighter at the bar so labels can be read.")
    _lights(R, B, spacing=3.6, energy=1.0, color="#ffe3c0", x_margin=1.0)
    _ceil(R, B, "ceilinglight_lounge_chandelier_ring", 5.6, -1.7)
    for x in (5.1, 8.7):
        _ceil(R, B, "ceilinglight_pendant_globe", x, -5.0)
    R.omni(11.2, R.y + 2.2, -2.5, color="#ffc98a", energy=0.8, rng_=5.0)
    R.omni(11.4, R.y + 1.8, -6.6, color="#ff9b5a", energy=0.9, rng_=4.0)
    R.omni(6.9, R.y + 2.3, -6.5, color="#ffe6c4", energy=0.7, rng_=4.5)
    R.line("Safety and signs",
           "An extinguisher by the door, the mess department sign and the exit marker; the bar's emergency light uses the beacon.")
    wi(R, B, "W", "safety_fire_extinguisher", -0.8, y=1.1, quiet=True)
    dsign(R, B, "W", -4.0, "dept_mess", y=3.1)
