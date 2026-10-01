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


def _table_chairs(R, B, table, mid, per_side=3, pitch=0.9, ends=None, sides=(-1, 1), gap=0.06):
    """Chairs along the two long sides of a table, facing it; `ends` = model for the two end seats.  Works for a table whose long
    axis runs along x (yaw 0 / 180) or along z (yaw 90 / -90)."""
    out = []
    if table is None:
        return out
    x0, z0, x1, z1 = table["_fp"]
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    d = M(B, mid)["size"][2]
    vertical = abs(round(table["yaw"]) % 180) == 90
    for i in range(per_side):
        t = (i - (per_side - 1) / 2.0) * pitch
        if vertical:
            if -1 in sides:
                out.append(put(R, B, mid, x0 - gap - d / 2, zm + t, 90.0, quiet=True))
            if 1 in sides:
                out.append(put(R, B, mid, x1 + gap + d / 2, zm + t, -90.0, quiet=True))
        else:
            if -1 in sides:
                out.append(put(R, B, mid, xm + t, z0 - gap - d / 2, 0.0, quiet=True))
            if 1 in sides:
                out.append(put(R, B, mid, xm + t, z1 + gap + d / 2, 180.0, quiet=True))
    if ends:
        de = M(B, ends)["size"][2]
        if vertical:
            out.append(put(R, B, ends, xm, z0 - gap - de / 2, 0.0, quiet=True))
            out.append(put(R, B, ends, xm, z1 + gap + de / 2, 180.0, quiet=True))
        else:
            out.append(put(R, B, ends, x0 - gap - de / 2, zm, 90.0, quiet=True))
            out.append(put(R, B, ends, x1 + gap + de / 2, zm, -90.0, quiet=True))
    return out


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


# ----------------------------------------------------------------------------------------------- LIBRARY
def f_library(R, B):
    R.describe(
        "The ship's library and data archive: bookshelves and cartridge stacks for the printed and recorded record, reading tables for "
        "study, a quiet armchair corner by the port window, and the librarian's issue desk by the door.",
        basis="11.5 m x 7.4 m.  Shelving runs along the north and south walls (about 18 m of shelf), two reading tables in the open middle "
              "with 1.2 m aisles, the archive machines (robot librarian, data vault, memory core) along the south wall, an armchair "
              "nook in the south-west corner with a window seat on the port wall.  Door on the east wall with its 2 m zone clear.",
        crew=14, adjacency="Aft spine corridor through the east door; hull windows on the port wall; the observatory and flag suite "
                           "are across the corridor.")
    R.line("Shelving along the north wall",
           "Pigeonhole book cases, cartridge shelves and archive boxes take the whole north wall: the ship's reference works and logs "
           "stand shoulder to shoulder with the shelf faces turned to the room, within reach of the tables.")
    seq(R, B, "N", ["shelving_pigeonhole", "shelving_pigeonhole", "storage_cartridge_library_shelves", "shelving_heavy_boxes",
                    "shelving_pigeonhole"], -12.5, gap=0.03)
    R.line("Data archive machines",
           "The ship's recorded knowledge: a robot librarian that fetches cartridges, a data crystal vault, a memory core column, a "
           "secure safe for restricted logs and a holographic storage cylinder; all on the south wall where power and data conduits run.")
    seq(R, B, "S", ["storage_archive_robot", "storage_data_crystal_vault", "storage_memory_core_column", "storage_holo_storage_cylinder",
                    "storage_secure_data_safe"], -9.5, gap=0.05)
    R.line("Notice board",
           "The notice board above the librarian's issue desk announces new acquisitions, opening hours and the quiet-zone rules.")
    wi(R, B, "E", "noticeboard_cork_bulletin_board", 4.6, y=2.4, quiet=True)
    R.line("Reading tables",
           "Two long tables, standing north-south in the middle of the room so that readers face the stacks and the door stays in view, give "
           "the reading room its centre; with lamps and datapads people can study on their own or in a group.")
    t1 = put(R, B, "table_conference_table", -8.0, 6.5, 90.0)
    t2 = put(R, B, "table_long_mess_table", -5.4, 6.5, 90.0)
    _table_chairs(R, B, t1, "chair_mess_chair", pitch=0.95)
    _table_chairs(R, B, t2, "chair_folding_chair", pitch=0.95, sides=(1,))
    top(R, B, t1, ["lamp_architect_desk_lamp", "terminal_datapad_stack", "terminal_laptop_console"], step=0.9, quiet=True)
    top(R, B, t2, ["lamp_table_lamp", "terminal_datapad", "terminal_portable_reader", "tableware_cups_and_mugs"], step=0.65, quiet=True)
    R.line("Librarian's issue desk and catalogue kiosks",
           "The librarian's tall issue desk stands beside the door so every borrower is seen on entering; catalogue kiosks next to it "
           "let readers search the archive without disturbing the librarian.")
    d = wall(R, B, "E", "desk_secretary_desk", 4.65)
    if d:
        put(R, B, "chair_swivel_office_chair", d["_fp"][0] - 0.5, (d["_fp"][1] + d["_fp"][3]) / 2, 90.0, quiet=True)
    wall(R, B, "E", "terminal_info_kiosk", 9.2, quiet=True)
    R.line("Reading nook",
           "A sofa with an armchair and coffee table in the south-west corner, a metre or more back from the port windows so the glass "
           "stays clear, are the quiet place for reading for pleasure; a floor lamp and a wall reading light give a warm light.")
    sofa = first(R, B, "couch_two_seater_sofa", [(-11.3, 10.1, 180.0), (-11.0, 10.1, 180.0)], quiet=True)
    first(R, B, "couch_lounge_armchair", [(-11.9, 7.8, 90.0), (-11.7, 7.8, 90.0)], quiet=True)
    ct = first(R, B, "table_coffee_table", [(-10.6, 8.3, 0.0), (-10.6, 8.5, 0.0)], quiet=True)
    top(R, B, ct, ["tableware_cups_and_mugs"], quiet=True)
    first(R, B, "lamp_floor_lamp", [(-9.1, 8.4, 0.0), (-9.2, 8.6, 0.0)])
    wi(R, B, "W", "lamp_reading_light", 7.0, y=1.5, quiet=True)
    R.line("Rug",
           "A soft carpet-tile rug under the nook's furniture marks it out as the 'quiet corner' and deadens footsteps.")
    for x in (-11.8, -10.8, -9.8):
        for z in (7.9, 8.9):
            R.place(M(B, "floorpanel_carpet_tile_1x1"), x, z, 0.0, check=False)
    R.line("Plants and globe",
           "A ficus by the door and hanging plants over the reading tables make the room friendlier; a reading globe of the nearest star systems stands in the corner by the stacks.")
    first(R, B, "plant_ficus_tree", [(-2.4, 10.3, 0.0), (-2.5, 10.4, 0.0)])
    for x in (-8.0, -5.4):
        _ceil(R, B, "plant_hanging_plant", x, 8.3)
    first(R, B, "holo_star_map_globe", [(-12.0, 4.9, 0.0)], quiet=True)
    R.line("Lighting",
           "Pendant lights hang over each reading table and downlights elsewhere give about 300 lux, with extra warm lights at the "
           "nook; screens and shelves have no reflected glare.")
    _lights(R, B, spacing=3.6, energy=1.1, color="#fff0d8", x_margin=1.0)
    _ceil(R, B, "ceilinglight_pendant_globe", -8.0, 6.5)
    _ceil(R, B, "ceilinglight_pendant_globe", -5.4, 6.5)
    R.omni(-10.4, R.y + 2.0, 8.6, color="#ffcf90", energy=0.8, rng_=4.5)
    R.omni(-6.7, R.y + 2.3, 6.5, color="#fff1d6", energy=0.8, rng_=5.0)
    R.line("Safety and signs",
           "An extinguisher by the door and the quarters department sign; a quiet-zone panel on the east wall reminds visitors of the rules.")
    wi(R, B, "E", "safety_fire_extinguisher", 10.4, y=1.1, quiet=True)
    wi(R, B, "E", "panellight_illuminated_logo_plate", 3.9, y=1.6, quiet=True)
    dsign(R, B, "E", 7.3, "dept_quarters", y=3.1)


# ----------------------------------------------------------------------------------------------- ARBORETUM
def f_arbor(R, B):
    R.describe(
        "The ship's garden under the stern dome: food herbs, ornamental beds and a koi tank in a green, humid room where the crew "
        "come to sit and drink tea; botanists tend the beds and examine specimens at a small microscope bench.",
        basis="62 m2, 3.6 m high, curved hull walls with five windows.  Production racks (tomato, herbs, microgreens, grow tower, mushrooms, "
              "wheat) along the north wall; three raised flower beds and the garden path in the middle; tea terrace at the west end; "
              "koi tank and benches under the windows; UV water purifier and microscope bench against the east wall.  The 1.6 m path from "
              "the door to the tea terrace is kept clear; nothing taller than 0.6 m stands within 0.5 m of a window.",
        crew=8, adjacency="Aft spine corridor through the east portal; hull windows to the stern and port; the hydroponics bay "
                          "(sci/hydro) one deck below feeds its water and nutrients.")
    R.keep_clear((-6.3, 13.95, -3.5, 15.75), "garden path from the door to the tea terrace")
    R.line("Production racks along the north wall",
           "Herb shelves, a microgreen rack, a vertical grow tower, a tomato vine rack and a mushroom shelf along the "
           "north wall feed the galley with fresh produce; the wall carries the water and nutrient lines and lets the racks share them.")
    seq(R, B, "N", ["planter_herb_shelf_rack", "planter_microgreen_rack", "planter_vertical_grow_tower",
                    "planter_tomato_vine_rack", "planter_mushroom_shelf"], -10.7, gap=0.04)
    R.line("Grow lights over the racks",
           "Full-spectrum bar panels hang over each rack position: plants need roughly 12 hours a day of 200 umol of light that the dim "
           "ship lighting cannot give; each panel also gives the pink glow that characterises the room.")
    for x in (-9.9, -8.2, -5.9, -3.8, -2.7):
        _ceil(R, B, "planter_grow_light_bar_panel", x, 11.9)
    R.line("Raised flower beds",
           "Three flower beds give colour and fragrance and take the sun from the windows; they stand between the racks and the "
           "path, 0.9 m clear of both, so a gardener can weed from the path side.")
    beds = [put(R, B, "planter_flower_bed_planter", x, 13.15, 0.0, quiet=True) for x in (-9.2, -7.4, -5.6)]
    for x in (-8.3, -6.5):
        _ceil(R, B, "planter_hanging_grow_light_array", x, 13.1)
    R.line("Dwarf trees and ornamentals",
           "A dwarf tree in a tub and a strawberry planter on the south side of the path form the 'orchard' and give height; they stand "
           "away from the hull windows so that the glass stays clear.")
    first(R, B, "planter_dwarf_tree_tub", [(-5.3, 16.7, 0.0), (-5.0, 16.7, 0.0)])
    first(R, B, "planter_strawberry_tiered_planter", [(-3.7, 16.4, 0.0), (-3.8, 16.2, 0.0)], quiet=True)
    R.line("Koi tank and water purifier",
           "The water feature: a koi aquarium at the stern end of the path makes the sound and sparkle of water, its fish clean the "
           "irrigation water, and the UV water purifier on the east wall sterilises it and returns it to the beds.")
    first(R, B, "specimen_aquarium_tank", [(-7.0, 16.7, 0.0), (-7.2, 16.6, 0.0), (-7.4, 16.4, 0.0)])
    wall(R, B, "E", "watertank_uv_water_purifier", 11.52, quiet=True)
    R.line("Tea terrace",
           "A round table with an armchair at the west end of the path is the garden's tea place: the table is set with a teapot "
           "and cups and has a bonsai in the middle; the path leads straight to it.")
    tt = first(R, B, "table_round_mess_table", [(-7.3, 14.85, 0.0), (-7.4, 14.85, 0.0)])
    if tt:
        x0, z0, x1, z1 = tt["_fp"]
        xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
        put(R, B, "chair_armchair", x0 - 0.55, zm, 90.0, quiet=True)
        top(R, B, tt, ["tableware_teapot", "plant_bonsai", "tableware_cups_and_mugs"], step=0.3, quiet=True)
    R.line("Benches under the windows",
           "Low benches (under 0.5 m, so they do not block the glass) sit below the hull windows: the view of the stars and the stern "
           "wake is the best thing in the room.")
    for side, mid, a in (("D1", "bench_locker_room_bench", 0.98), ("D2", "bench_locker_room_bench", 0.92),
                         ("S", "bench_mess_bench", -4.75), ("D4", "bench_locker_room_bench", 1.05)):
        wall(R, B, side, mid, a, quiet=True)
    R.line("Microscope bench",
           "Botanists check leaf, root and water samples at a bench against the east wall with a microscope, a stereo scope and sample jars; "
           "it is next to the water purifier and the beds so that samples do not travel.")
    lb = wall(R, B, "E", "labbench_sample_prep_table", 17.0, quiet=True)
    top(R, B, lb, ["microscope_optical_microscope", "microscope_stereo_microscope", "specimen_specimen_jar_set"], step=0.45, quiet=True)
    if lb:
        put(R, B, "labbench_lab_stool", lb["_fp"][0] - 0.5, (lb["_fp"][1] + lb["_fp"][3]) / 2, 90.0, quiet=True)
    R.line("Greenery",
           "Ficus trees and ferns fill the corners and a moss wall panel above the benches gives a green wall.")
    first(R, B, "plant_ficus_tree", [(-12.0, 12.9, 0.0), (-11.6, 12.9, 0.0)], quiet=True)
    first(R, B, "plant_fern", [(-12.0, 11.8, 0.0)], quiet=True)
    wi(R, B, "E", "plant_moss_wall_panel", 15.0 + 2.45, y=1.7, quiet=True)
    for x, z in ((-6.5, 15.0), (-4.5, 15.0)):
        _ceil(R, B, "plant_hanging_plant", x, z)
    R.line("Wall lights between the windows",
           "Small frosted wall lights on the piers between the windows make the garden glow at night without lighting up the glass.")
    _sconces_between_windows(R, B, ["D0", "D1", "D2", "D4"], mid="sconce_frosted_glass_shell", y=2.0)
    R.line("Daylight and grow lighting",
           "Bright daylight-white downlights give the plants a full spectrum; extra pink grow-light omni lights over the beds and the cool "
           "water light above the koi tank give the room its characteristic glow.")
    _lights(R, B, spacing=3.2, energy=1.1, color="#f2ffe6", x_margin=1.0)
    R.omni(-7.4, R.y + 2.8, 12.8, color="#ff7ad0", energy=1.0, rng_=5.0)
    R.omni(-4.5, R.y + 2.8, 12.4, color="#ff7ad0", energy=0.8, rng_=4.5)
    R.omni(-7.2, R.y + 1.8, 16.7, color="#59d0ff", energy=0.6, rng_=3.5)
    R.omni(-8.0, R.y + 2.6, 14.8, color="#fff2cf", energy=0.7, rng_=4.0)
    R.line("Safety and signs",
           "Extinguisher by the door, a hose-down panel note and the science sign; a wet-floor stand by the koi tank.")
    wi(R, B, "E", "safety_fire_extinguisher", 11.3, y=1.1, quiet=True)
    dsign(R, B, "E", 14.5, "dept_science", y=3.1)


# ----------------------------------------------------------------------------------------------- OBSERVATORY
def f_observ(R, B):
    R.describe(
        "The ship's stargazing and astronomy room on the starboard stern: real telescopes at the big window, a spectrograph and a small "
        "instrument lab, a console cluster to run them, and chaises for the crew to watch the stars at night.",
        basis="11.5 m x 7.4 m.  The window wall (east) is kept completely free except for the main telescope 1.8 m inside it; consoles in "
              "a row on the north wall, instruments on the south wall, two chaises facing the window across the room centre, lights low "
              "and red-tinted so eyes stay dark-adapted.  Door zone (2 m deep) and the walkway to the window kept clear.",
        crew=8, adjacency="Aft spine corridor through the west door; the library and arboretum are across the corridor; hull window "
                           "on the starboard wall plus a small port at the stern corner.")
    R.line("Main telescope",
           "The observation telescope on its mount stands on the centre line of the big window, 1.8 m back from the glass so its "
           "tube can swing without touching it; the seats look past it at the stars.")
    first(R, B, "telescope_observation_telescope", [(10.4, 5.8, 90.0), (10.2, 5.8, 90.0)])
    R.line("Star trackers and spectrograph",
           "A star tracker on its tripod, a spectrograph tripod and an astrometric dish stand round the window and take images, spectra "
           "and fixes of the sky at once; they sit at the sides of the window, not in front of it.")
    first(R, B, "telescope_star_tracker_scope", [(10.7, 9.4, 120.0), (10.2, 9.6, 120.0)], quiet=True)
    first(R, B, "telescope_spectrograph_tripod", [(10.5, 4.3, 60.0), (9.8, 4.6, 60.0)], quiet=True)
    first(R, B, "telescope_astrometric_dish", [(11.7, 9.9, -150.0), (11.3, 9.9, -150.0)], quiet=True)
    R.line("Control console row",
           "Science, sensor and navigation consoles run side by side on the north wall: the observers steer the telescopes, read the "
           "detectors and log targets while their seats face the displays above the consoles.")
    for mid, x, seat in (("console_science", 5.2, "science_stool"), ("console_sensor", 7.0, "ops_chair"),
                         ("console_navigation", 8.9, "tactical_chair")):
        c = wall(R, B, "N", mid, x, quiet=True)
        if c is not None:
            seat_facing(R, c, cats=("seat",), gap=0.3, label=seat)
    for x, mid in ((5.2, "display_triple_stack"), (7.0, "display_wing_display"), (8.9, "display_triple_stack")):
        wi(R, B, "N", mid, x, y=2.3, quiet=True)
    R.line("Data racks",
           "Two racks by the door record the nightly sky images and hold the telescopes' observation catalogue, near the console row and "
           "the door.")
    seq(R, B, "N", ["rack_storage_array", "rack_photonic_fiber_rack"], 1.75, gap=0.04)
    R.line("Instrument bench",
           "Spectra and samples are measured at a bench on the south wall: a spectrometer, a field lab and a magnetometer on the bench, "
           "a mass spectrometer, weather station and a satellite-dish demonstrator next to it.")
    lb = wall(R, B, "S", "labbench_sample_prep_table", 3.6, quiet=True)
    top(R, B, lb, ["analyzer_spectrometer", "sciinstrument_portable_field_lab", "sciinstrument_magnetometer"], step=0.5, quiet=True)
    if lb:
        put(R, B, "labbench_lab_stool", (lb["_fp"][0] + lb["_fp"][2]) / 2, lb["_fp"][1] - 0.45, 180.0, quiet=True)
    wall(R, B, "S", "analyzer_mass_spectrometer", 5.9, quiet=True)
    wall(R, B, "S", "sciinstrument_weather_station", 7.4, quiet=True)
    wall(R, B, "S", "antenna_dish_array_demo", 9.1, quiet=True)
    wall(R, B, "S", "sciinstrument_sample_drill_rig", 10.7, quiet=True)
    R.line("Stargazing seating",
           "Two chaises recline toward the window across the room centre for long meteor and aurora watches; an ottoman and a "
           "side table with a lamp complete the group.")
    first(R, B, "couch_chaise", [(7.4, 7.1, 90.0), (7.0, 7.1, 90.0)])
    first(R, B, "couch_chaise", [(7.4, 8.8, 90.0), (7.0, 8.8, 90.0)])
    st = first(R, B, "table_side_table", [(8.8, 8.0, 0.0), (8.9, 7.9, 0.0)], quiet=True)
    top(R, B, st, ["lamp_table_lamp"], quiet=True)
    R.line("Holographic sky globe",
           "A holographic star-map globe on a pedestal in the corner shows the whole sky with the targets of the night marked, the "
           "observers' planning sheet.")
    first(R, B, "holo_star_map_globe", [(4.4, 9.8, 0.0), (4.4, 9.6, 0.0)], quiet=True)
    R.line("Observer's log desk",
           "A small desk against the west wall holds the observing log and a lamp; each night's observer writes up targets and "
           "weather there, away from the console glare.")
    d = wall(R, B, "W", "desk_writing_desk", 9.6, quiet=True)
    top(R, B, d, ["lamp_architect_desk_lamp", "terminal_datapad"], step=0.5, quiet=True)
    if d:
        put(R, B, "chair_ergonomic_chair", d["_fp"][2] + 0.5, (d["_fp"][1] + d["_fp"][3]) / 2, 90.0, quiet=True)
    R.line("Plants and notices",
           "A ficus by the door, the night-roster notice board and the observatory chronometer keep the room tidy and on schedule.")
    first(R, B, "plant_ficus_tree", [(2.3, 4.0, 0.0)], quiet=True)
    wi(R, B, "W", "noticeboard_duty_roster_display", 4.4, y=1.7, quiet=True)
    wi(R, B, "W", "clock_dual_time_ship_clock", 10.2, y=2.3, quiet=True)
    for x in (4.0, 10.9, 11.9):
        wi(R, B, "N", "sconce_chrome_uplight", x, y=1.9, quiet=True)
    wi(R, B, "S", "instrument_radar_scope", 2.6, y=1.8, quiet=True)
    wi(R, B, "D1", "sconce_chrome_uplight", 0.7, y=1.9, quiet=True)
    R.line("Low red lighting",
           "Dim downlights and red omni lights keep the room around 20 lux so the eye stays dark-adapted; the consoles' own displays "
           "and a cool blue accent at the telescope are the main light sources.")
    _lights(R, B, spacing=3.6, energy=0.6, color="#ffb09a", x_margin=1.0)
    R.omni(7.0, R.y + 2.6, 5.0, color="#ff6a50", energy=0.5, rng_=5.0)
    R.omni(5.5, R.y + 2.4, 9.5, color="#ff6a50", energy=0.4, rng_=4.5)
    R.omni(10.4, R.y + 2.0, 5.8, color="#6aa8ff", energy=0.5, rng_=4.0)
    R.line("Safety and signs",
           "An extinguisher by the door, the science sign and an exit sign mark the room as a working lab.")
    wi(R, B, "W", "safety_fire_extinguisher", 10.0, y=1.1, quiet=True)
    dsign(R, B, "W", 7.3, "dept_science", y=3.1)


# ----------------------------------------------------------------------------------------------- FLAG OFFICER'S SUITE
def f_flag(R, B):
    R.describe(
        "The admiral's quarters on the starboard stern: a sleeping alcove, a working corner with desk, display and private holo-comm, a "
        "small lounge with a sofa, armchairs and a stargazing telescope at the stern window, and a table for two for private dinners.",
        basis="62 m2, tapering to the stern.  Bed head on the north wall in the widest corner, desk, wardrobe and bookcase along the "
              "north and west walls, lounge in the middle, dining table and telescope at the stern window; the 2 m door zone and a 1.2 m "
              "route from the door to the lounge are kept clear; nothing taller than 0.6 m stands within 0.5 m of a window.  Richer than "
              "the officers' cabins: a captain's bed, a real desk and lounge, art and lamps.",
        crew=1, adjacency="Aft spine corridor through the west door; the observatory is across the corridor to the north; "
                          "hull windows to the stern and starboard.")
    R.line("Admiral's bed",
           "A captain's bed with a canopy stands head to the north wall in the widest, quietest corner, away from the door and "
           "with a hull window beside it; the bedside table carries the reading lamp.")
    bed = wall(R, B, "N", "bed_captain_bed", 8.5, quiet=True)
    if bed is None:
        bed = first(R, B, "bed_captain_bed", [(8.5, 12.6, 0.0)])
    for x in (6.95,):
        t = first(R, B, "table_side_table", [(x, 11.5, 0.0), (x - 0.1, 11.6, 0.0)], quiet=True)
        top(R, B, t, ["lamp_bedside_light"] if x < 9 else ["lamp_table_lamp"], quiet=True)
    R.line("Wardrobe and bookcase",
           "A tall wardrobe for uniforms stands next to the desk and a pigeonhole bookcase against the west wall holds the admiral's "
           "own books; both are within reach of the door and out of the lounge.")
    wall(R, B, "N", "locker_wardrobe", 3.95, quiet=True)
    wall(R, B, "W", "shelving_pigeonhole", 12.0, quiet=True)
    R.line("Admiral's desk",
           "A large officer's desk on the north wall is the working corner: the admiral sits facing the wall display with the whole "
           "room behind; the desk is fitted with a lamp, terminal, chronometer and datapads.")
    desk = wall(R, B, "N", "desk_officer_desk", 5.65, quiet=True)
    top(R, B, desk, ["lamp_architect_desk_lamp", "terminal_desk_terminal", "terminal_datapad_stack", "instrument_brass_chronometer"],
        step=0.4, quiet=True)
    if desk:
        seat = M(B, "chair_ergonomic_chair")
        put(R, B, "chair_ergonomic_chair", (desk["_fp"][0] + desk["_fp"][2]) / 2, desk["_fp"][3] + 0.1 + seat["size"][2] / 2, 180.0, quiet=True)
        wi(R, B, "N", "display_status_board", 5.65, y=2.35, quiet=True)
    R.line("Lounge group",
           "A sofa against the south wall, a coffee table and two ottomans form a conversation group where the admiral receives "
           "visitors; the group sits on a soft rug and is laid out round a clear 1.2 m route from the door.")
    first(R, B, "couch_two_seater_sofa", [(7.1, 16.8, 180.0), (7.0, 16.8, 180.0)])
    ct = first(R, B, "table_coffee_table", [(7.1, 15.6, 0.0), (7.1, 15.5, 0.0)], quiet=True)
    top(R, B, ct, ["tableware_teapot", "tableware_cups_and_mugs"], step=0.35, quiet=True)
    first(R, B, "couch_ottoman", [(8.4, 15.7, -90.0), (8.3, 15.7, -90.0)], quiet=True)
    for x in (6.1, 7.1, 8.1):
        R.place(M(B, "floorpanel_carpet_tile_1x1"), x, 15.4, 0.0, check=False)
        R.place(M(B, "floorpanel_carpet_tile_1x1"), x, 16.4, 0.0, check=False)
    R.line("Stargazing telescope",
           "An observation telescope at the stern window is the admiral's private hobby: it stands a metre back from the glass at the "
           "side of the lounge so the view of the stars stays open.")
    first(R, B, "telescope_observation_telescope", [(5.0, 16.4, 180.0), (5.0, 16.3, 180.0), (5.1, 16.3, 180.0)])
    R.line("Dinner table for two",
           "A small round table with two chairs by the window for private dinners with a guest; set with plates, glasses and a candle "
           "lantern, it is the one formal corner of the suite.")
    dt = first(R, B, "table_round_mess_table", [(2.85, 16.6, 0.0), (2.85, 16.7, 0.0)], quiet=True)
    if dt:
        x0, z0, x1, z1 = dt["_fp"]
        zm = (z0 + z1) / 2
        put(R, B, "chair_mess_chair", (x0 + x1) / 2, z1 + 0.3, 180.0, quiet=True)
        put(R, B, "chair_folding_chair", x1 + 0.3, zm, -90.0, quiet=True)
        top(R, B, dt, ["tableware_plate_stack", "tableware_bottle_and_glasses", "lamp_decorative_lantern"], step=0.3, quiet=True)
    R.line("Art, plants and display",
           "A holographic art frame on the west wall, a ficus tree and a fern, a bonsai on the dining table and a floor lamp make "
           "the suite feel like a home rather than a cabin.")
    wi(R, B, "W", "display_holo_frame_panel", 17.2, y=1.7, quiet=True)
    first(R, B, "plant_ficus_tree", [(4.1, 14.55, 0.0), (4.2, 14.5, 0.0)], quiet=True)
    first(R, B, "plant_fern", [(11.2, 12.6, 0.0)], quiet=True)
    first(R, B, "lamp_floor_lamp", [(6.1, 13.5, 0.0), (6.2, 13.6, 0.0)], quiet=True)
    first(R, B, "lamp_uplight", [(2.1, 17.5, 0.0), (2.0, 17.5, 0.0)], quiet=True)
    wi(R, B, "W", "locker_mirror_cabinet", 11.4, y=1.7, quiet=True)
    R.line("Bed rug and chest",
           "A rug under the bed foot and a sea chest at the bed's foot hold the admiral's winter blankets and make the sleeping alcove "
           "feel like a separate part of the room.")
    for x in (7.6, 8.6, 9.6):
        R.place(M(B, "floorpanel_carpet_tile_1x1"), x, 14.4, 0.0, check=False)
    first(R, B, "locker_sea_chest", [(8.6, 14.75, 0.0), (8.5, 14.8, 0.0)], quiet=True)
    for x, z in ((3.0, 13.0), (6.6, 14.4)):
        _ceil(R, B, "plant_hanging_plant", x, z)
    R.line("Wall lights between the windows",
           "Small wall lights on the piers between the hull windows are the soft evening light of the suite.")
    _sconces_between_windows(R, B, ["D1", "D2", "D3"], mid="sconce_brass_candle_sconce", y=1.9)
    R.line("Warm lighting",
           "A chandelier over the lounge, downlights elsewhere at 150 lux and warm omni accents by the bed, the desk and the "
           "telescope give the suite a warm, residential light.")
    _lights(R, B, spacing=3.6, energy=0.9, color="#ffdcb0", x_margin=1.0)
    _ceil(R, B, "ceilinglight_lounge_chandelier_ring", 7.0, 15.7)
    R.omni(8.9, R.y + 2.2, 12.5, color="#ffb870", energy=0.7, rng_=4.5)
    R.omni(5.6, R.y + 2.2, 12.4, color="#ffe3b8", energy=0.6, rng_=4.0)
    R.omni(3.8, R.y + 2.0, 16.4, color="#ffd2a0", energy=0.5, rng_=4.0)
    R.line("Safety and signs",
           "An extinguisher by the door and the quarters sign; the suite has its own alarm panel next to the bed.")
    wi(R, B, "W", "safety_fire_extinguisher", 17.0, y=1.1, quiet=True)
    dsign(R, B, "W", 14.5, "dept_quarters", y=3.0)
