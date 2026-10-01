"""Room recipes - Deck 1 (Command Deck, y = 8 m)."""
import math
from dressing import *   # noqa: F401,F403
from recipes_deck1_helpers import need, M, put, wall, floor_wall, tops
from recipes_food import food_bridge, food_cabin, food_capt, food_conf, food_lounge, food_ready   # noqa: F401


# ====================================================================================== BRIDGE
def f_bridge(R, B):
    R.describe(
        "The ship's command centre: the captain, the forward flight crew (helm, ops, navigation, flight control) and the aft "
        "systems stations (tactical, engineering, science, communications) work here.  The panoramic nose windows replace a "
        "projected viewscreen.",
        basis="175 m2 and a 4.2 m volume for 9-10 watchstanders (about 17 m2 each). Forward row 1.0 m clear between "
              "stations so the captain sees past the helm; 1.2 m main aisle behind the command chair; nothing taller than a "
              "console within 1.5 m of the bow glazing; aft wall reserved for the four systems stations and their displays; "
              "escape to the corridor, ready room and conference room through three 2 m doors on the aft wall.",
        crew=10,
        adjacency="Corridor door at centre aft; captain's ready room to port and conference room to starboard on the same bulkhead, "
                  "so the captain can reach both without leaving the command area.")
    cx, cz0 = 0.0, -25.3          # command chair position
    (cx, cz0)

    R.line("Ceiling lighting",
           "Low-glare recessed fixtures on a 4 m grid give about 250 lux on the stations, deliberately dimmer than other rooms "
           "so the displays and the star field stay readable.")
    light_room(R, spacing=4.4, energy=1.25, color="#f3e9d8", x_margin=1.4,
               pred=lambda m: m["mount"] == "ceiling" and m["size"][0] < 1.3 and m["size"][2] < 1.3 and m["size"][1] < 0.3)

    R.line("Command chair and podium",
           "The captain's chair sits on the centreline one third back from the nose, where the whole glazing arc and every station "
           "are in view, with the captain's podium console at its right arm for ship-wide orders.  No console stands between "
           "the chair and the bow except the two flight stations.")
    put(R, "seat", "captain_command", cx, cz0, yaw=180, what="captain's chair")
    put(R, "console", "captain_podium", cx + 1.0, cz0 + 0.05, yaw=180, what="captain podium")

    R.line("Helm and operations (forward row)",
           "Helm and ops are the two stations that steer and run the ship, so they sit forward on the centreline facing the "
           "main glazing.  The 1.0 m gap between them keeps the captain's line of sight to the nose window; each pilot sits "
           "behind the console with his back to the captain.")
    put(R, "console", "helm", -1.6, -30.3, face=(0, -25.0), what="helm console")
    put(R, "console", "console_ops", 1.75, -30.3, face=(0, -25.0), what="ops console")
    put(R, "seat", "helm_chair", -1.6, -28.8, yaw=180, what="helm chair")
    put(R, "seat", "ops_chair", 1.75, -28.8, yaw=180, what="ops chair")

    R.line("Navigation and flight control (forward wings)",
           "Navigation plots the course and flight control handles the craft and docking traffic; both are angled 25 degrees "
           "toward the captain on the forward wings so every screen can be read from the command chair.")
    put(R, "console", "navigation", -4.0, -28.3, face=(0, -25.0), what="navigation console")
    put(R, "console", "flight_control", 4.0, -28.3, face=(0, -25.0), what="flight control console")
    put(R, "seat", "ops_chair", -3.4, -26.85, yaw=yaw_to(-3.4, -26.85, -4.0, -28.3), what="nav chair")
    put(R, "seat", "helm_chair", 3.4, -26.85, yaw=yaw_to(3.4, -26.85, 4.0, -28.3), what="flight chair")

    R.line("Tactical table",
           "A holographic tactical table on the starboard side, within two steps of the command chair, lets the captain and "
           "the tactical officer review a threat picture together; the plinth on the port side shows the ship's own damage "
           "and systems schematic.")
    put(R, "holo", "briefing_table", 6.0, -24.9, yaw=0, what="tactical holo table")
    put(R, "holo", "ship_schematic", -6.2, -24.9, yaw=0, what="ship schematic projector")

    R.line("Aft systems stations",
           "Tactical, engineering, science and communications stand against the solid aft bulkhead between the doors, facing "
           "forward, so these watchstanders work with the whole bridge in front of them and out of the flight crew's way.  "
           "Each has its own chair and a wall display above it carrying that station's repeater.")
    eng = floor_wall(R, "S", "console", "engineering_status", -8.5, what="engineering console")
    sci = floor_wall(R, "S", "console", "console_science", -3.0, what="science console")
    tac = floor_wall(R, "S", "console", "console_tactical", 3.65, what="tactical console")
    com = floor_wall(R, "S", "console", "console_communications", 8.6, what="comms console")
    for con, lab in ((eng, "ops_chair"), (sci, "science_stool"), (tac, "tactical_chair"), (com, "comms_chair")):
        seat_facing(R, con, cats=("seat",), label=lab, gap=0.3)

    R.line("Station repeater displays",
           "A display above each aft station repeats its data at head height for the captain and for anyone standing behind "
           "the operator; the aft wall is solid so no glazing is covered.")
    for x, lab, yy in ((-8.5, "status_board", 2.55), (-3.0, "wing_display", 2.55), (3.45, "tactical_wall_screen", 2.8), (8.6, "status_board", 2.55)):
        wall(R, "S", "display", lab, x, y=yy, what="repeater %s" % lab)

    R.line("Door signs and wall clock",
           "Each door on the aft wall is labelled on the bridge side; one ship's clock keeps the watch.")
    wall(R, "S", "sign", "emergency_exit", 1.95, y=3.4, what="exit sign")
    wall(R, "S", "clock", "dual_time", -4.0, y=3.3, what="clock")

    R.line("Emergency and fire protection",
           "A damage-control locker beside the centre door and an extinguisher at the west end stand on the aft wall, where crew can reach them "
           "from any station within ten paces; suppression nozzles are over the forward stations.")
    floor_wall(R, "S", "safety", "damage_control_locker", 2.05, what="damage control locker")
    wall(R, "S", "safety", "fire_extinguisher", -10.1, y=1.1, what="extinguisher")
    for (x, z) in ((-3.0, -29.0), (3.0, -29.0), (0.0, -25.0)):
        R.place(M(R, "safety", "suppression_nozzle"), x, z, 0.0, y=R.y + R.h)
    food_bridge(R, B)


def lights(R, spacing=4.0, energy=1.5, color="#fff0dd", x_margin=1.0, why=None):
    R.line("Ceiling lighting", why or "Recessed ceiling fixtures on a regular grid give even general light sized to the room.")
    light_room(R, spacing=spacing, energy=energy, color=color, x_margin=x_margin,
               pred=lambda m: m["mount"] == "ceiling" and m["size"][0] < 1.3 and m["size"][2] < 1.3 and m["size"][1] < 0.35)


def extinguisher(R, side, along, y=1.1):
    return wall(R, side, "safety", "fire_extinguisher", along, y=y, what="fire extinguisher")


# ====================================================================================== READY ROOM
def f_ready(R, B):
    R.describe(
        "The captain's private office next to the bridge: paperwork, confidential talks with officers, and a quiet place to "
        "think between watches.",
        basis="85 m2 for one occupant plus two to four visitors.  Desk island in the west half with the captain facing the door; "
              "two visitor chairs opposite (1.0 m knee clearance); a separate informal sofa group in the south (coffee table 0.5 m "
              "from the sofa front); 1.2 m clear from the corridor door to the desk; shelving and display on the walls.",
        crew=1,
        adjacency="Door to the bridge (north) so the captain reaches the command chair in ten steps; door to the corridor "
                  "on the east wall for officers who are called in.")
    lights(R, spacing=3.6, energy=1.3, color="#fff1de", x_margin=1.3,
           why="Warm, dimmable downlights (about 300 lux) suit desk work and conversation; the fixtures sit over the desk and the sofa group.")

    R.line("Captain's desk",
           "A large officer desk is the centre of the office; the captain sits on its west side with the door in view, the "
           "hull at his back, and the visitors' side open to the room.  Desk terminal, lamp and a datapad are on the top.")
    desk = put(R, "desk", "officer_desk", -9.3, -17.0, yaw=-90, what="captain's desk")
    if desk:
        cap = R.place(M(R, "chair", "swivel_office"), -10.75, -17.0, 90.0)
        need(cap, "captain's chair", R)
        tops(R, desk, None, [("terminal", "desk_terminal", 0.0, 0.0), ("lamp", "architect", 0.55, 0.0),
                             ("terminal", "datapad_stack", -0.55, 0.0)])

    R.line("Visitors' chairs",
           "Two armchairs face the desk across its front edge for briefings; two is the number of officers the captain normally "
           "receives at once, and the pair leaves the route from the door to the desk open.")
    for z in (-17.8, -16.2):
        need(R.place(M(R, "chair", "armchair"), -7.6, z, -90.0), "visitor chair", R)

    R.line("Sofa group",
           "A three-seater sofa, coffee table and two lounge chairs form an informal corner where the captain can talk with a "
           "guest without the desk between them; it is placed on the south wall away from the traffic line door-to-desk.")
    floor_wall(R, "S", "couch", "three_seater", -5.3, what="sofa")
    tbl = put(R, "table", "coffee_table", -5.3, -14.75, yaw=0, what="coffee table")
    put(R, "couch", "lounge_armchair", -8.3, -14.6, face=(-5.3, -14.75), what="armchair")
    tops(R, tbl, None, [("tableware", "teapot", -0.25, 0.0), ("tableware", "cups_and_mugs", 0.2, 0.0)])

    R.line("Coffee point",
           "A coffee machine and a side table with cups so the captain can offer a drink without calling the galley; beside the "
           "bridge door so it is on the way in.")
    floor_wall(R, "N", "galley", "coffee_machine", -2.35, what="coffee machine")
    st = put(R, "table", "side_table", -3.4, -20.55, yaw=180, what="side table")
    tops(R, st, None, [("tableware", "cups_and_mugs", 0.0, 0.0)])

    R.line("Bookshelves and trophy case",
           "Bookcases on the north and east walls hold the ship's library and logs; a wall display case shows mission "
           "mementos.  Wall-standing units leave the middle of the room open.")
    floor_wall(R, "N", "shelving", "pigeonhole", -9.6, what="bookcase")
    floor_wall(R, "E", "shelving", "pigeonhole", -14.35, what="bookcase")
    wall(R, "E", "locker", "display_cabinet", -19.6, y=1.5, what="display case")

    R.line("Displays",
           "A status board on the east wall and a holo frame over the desk show the ship's state and the day's schedule "
           "without the captain having to walk to the bridge.")
    wall(R, "S", "display", "status_board", -5.3, y=2.05, what="status board")
    wall(R, "S", "display", "holo_frame", -9.0, y=1.7, what="holo frame display")
    wall(R, "N", "display", "chronometer", -9.6, y=2.75, what="clock display")

    R.line("Plants and lamps",
           "A ficus in the south-west corner and a floor lamp beside the sofa give the room a domestic feel.")
    put(R, "plant", "ficus", -11.6, -14.2, yaw=0, what="ficus")
    put(R, "lamp", "floor_lamp", -3.35, -14.0, yaw=0, what="floor lamp")

    R.line("Safety and signs",
           "Extinguisher by the corridor door, exit sign over it.")
    extinguisher(R, "E", -20.4)
    wall(R, "N", "sign", "emergency_exit", -8.3, y=2.6, what="exit sign")
    food_ready(R, B)


def _chairpred(m):
    return m["id"].endswith("swivel_office_chair")


# ====================================================================================== LOUNGE
def f_lounge(R, B):
    R.describe(
        "The ship's observation lounge: off-duty officers watch the stars through the port windows, read, talk and have a "
        "drink.  It doubles as the venue for receptions and small ceremonies.",
        basis="149 m2 for up to 20 people (7 m2 each, standing reception 40).  Seating groups turned to the two 3.2 m windows; "
              "low furniture only (< 0.6 m) within 2 m of the glazing; 1.2 m aisle from the door to the windows and to the "
              "bar; bar counter and kitchen modules along the south wall; library on the north wall.",
        crew=20,
        adjacency="Door to the corridor on the east wall, midway along it; port hull windows give the view; the ready room is "
                  "next door to the north for receptions hosted by the captain.")
    lights(R, spacing=3.8, energy=1.35, color="#ffe9cf", x_margin=1.3,
           why="Warm, dimmable light (about 150 lux) with the windows unobstructed for star viewing; one fixture over each seating group.")

    R.line("Window seating groups",
           "Each 3.2 m window is paired with one group: a long observation sofa faces the glass across a low coffee table. The sofa stays "
           "3 m back so nobody's view is blocked and nothing tall stands in front of the glazing.")
    groups = []
    for zc in (-8.88, -3.12):
        s = put(R, "couch", "observation_sofa", -7.6, zc, yaw=-90, what="observation sofa")
        t = put(R, "table", "coffee_table", -10.3, zc, yaw=90, what="coffee table")
        if t:
            tops(R, t, None, [("tableware", "bottle_and_glasses", 0.0, 0.0)] if zc < -5 else [("plant", "succulent", 0.0, 0.0)])
        groups.append((s, t))

    R.line("Lounge chairs on the window flanks",
           "One armchair at the north end of the first sofa and one at the south end of the second close the groups into conversation "
           "circles and turn toward the windows; the 2.3 m gap between the sofas stays open as the route to the telescope.")
    for x, z, yw in ((-7.6, -11.3, -60), (-8.6, -1.0, -120)):
        put(R, "chair", "lounge_chair", x, z, yaw=yw, what="lounge chair")

    R.line("Telescope and star globe",
           "A visitor telescope stands on the solid wall piece between the two windows so it can be turned to either; the star-map "
           "globe by the north window is where people find the constellation they just saw.")
    floor_wall(R, "W", "telescope", "observation_telescope", -6.0, what="telescope")
    floor_wall(R, "W", "holo", "star_map_globe", -11.5, what="star map globe")

    R.line("Bar",
           "A bar counter with stools along the south wall and a refrigerator, coffee machine and water cooler behind it handle "
           "drinks for receptions without bringing a steward; it sits at the far end from the door so queues do not block the entrance.")
    cnt = []
    for x in (-5.2, -7.0):
        cnt.append(floor_wall(R, "S", "table", "bar_counter", x, what="bar counter"))
    for c in cnt:
        tops(R, c, None, [("tableware", "bottle_and_glasses", -0.3, 0.0), ("tableware", "cups_and_mugs", 0.3, 0.0)])
    for x in (-5.6, -6.4, -7.2):
        put(R, "couch", "bar_stool", x + 0.6, -1.45, yaw=180, what="bar stool")
    floor_wall(R, "S", "galley", "refrigerator", -2.4, what="refrigerator")
    floor_wall(R, "S", "galley", "coffee_machine", -3.4, what="coffee machine")
    floor_wall(R, "S", "galley", "water_cooler", -9.6, what="water cooler")

    R.line("Reading corner and library",
           "Two bookcases on the north wall form a small library; two armchairs and a side table with a reading lamp under it "
           "give a quiet place to read away from the bar.")
    floor_wall(R, "N", "shelving", "pigeonhole", -10.2, what="bookcase")
    floor_wall(R, "N", "shelving", "pigeonhole", -8.4, what="bookcase")
    put(R, "chair", "armchair", -6.3, -11.3, yaw=180 + 20, what="reading armchair")
    put(R, "chair", "armchair", -4.0, -11.3, yaw=180 - 20, what="reading armchair")
    st = put(R, "table", "side_table", -5.15, -11.3, yaw=0, what="side table")
    tops(R, st, None, [("lamp", "table_lamp", 0.0, 0.0)])

    R.line("Plants",
           "A ficus and a fern soften the room's corners; they are kept against solid wall, never in front of glass.")
    put(R, "plant", "fern", -11.6, -0.9, yaw=0, what="fern")
    put(R, "plant", "ficus", -2.5, -12.0, yaw=0, what="ficus")

    R.line("Displays and lamps",
           "A wall display by the entrance shows the ship's position chart and a wall clock keeps the watch; an uplight by the door gives soft indirect light.")
    wall(R, "E", "display", "hex_display", -10.0, y=1.7, what="position display")
    wall(R, "E", "display", "chronometer", -2.5, y=2.2, what="wall clock")
    put(R, "lamp", "uplight", -2.3, -9.6, yaw=0, what="uplight")

    R.line("Safety and signs",
           "Extinguisher and first-aid signage by the door and at the bar.")
    extinguisher(R, "E", -12.0)
    wall(R, "E", "sign", "dept_quarters", -9.0, y=2.6, what="lounge sign")
    extinguisher(R, "S", -8.9)
    food_lounge(R, B)


# ====================================================================================== CONFERENCE ROOM
def f_conf(R, B):
    R.describe(
        "Senior-staff conference room: daily command briefings, planning sessions and video links with other ships.",
        basis="85 m2 for 12 seated plus observers.  Table 6.0 x 1.2 m (two 3 m sections) on the long axis; 0.75 m per seat; 1.2 m "
              "clear behind chairs on the north side (service route) and 1.4 m on the south (credenza); displays and holo "
              "projector at the head of the table (east end is the captain's seat); doors on the west (corridor) and north "
              "(bridge) walls.",
        crew=12,
        adjacency="Direct door to the bridge on the north wall, door to the corridor on the west; close to the ready room.")
    lights(R, spacing=3.8, energy=1.4, color="#f4f6ff", x_margin=1.3,
           why="Even 400 lux over the table (two fixtures in line with it), cooler colour temperature to keep the meeting alert.")

    R.line("Conference table",
           "Two 3 m conference tables joined end to end make a 6 m boardroom table, long enough for 12 seats and short enough "
           "to keep 1.4 m of aisle to the walls.  Datapads and a water pitcher wait on top.")
    t1 = put(R, "table", "conference_table", 5.5, -17.0, yaw=0, what="conference table A")
    t2 = put(R, "table", "conference_table", 8.52, -17.0, yaw=0, what="conference table B")
    tops(R, t1, None, [("terminal", "datapad_stack", -0.6, 0.0), ("tableware", "pitcher", 0.0, 0.0), ("terminal", "datapad", 0.6, 0.0)])
    tops(R, t2, None, [("terminal", "datapad_stack", -0.6, 0.0), ("tableware", "bottle_and_glasses", 0.0, 0.0), ("tableware", "cups_and_mugs", 0.6, 0.0)])

    R.line("Chairs around the table",
           "Twelve swivel chairs, six on each side at 1.0 m pitch, all facing the table; the head seat at the east end is an armchair "
           "for the captain so the chair of the meeting sees the displays and the door.")
    for i in range(6):
        x = 4.52 + i * 1.0
        for z, yw in ((-18.05, 0.0), (-15.95, 180.0)):
            need(R.place(M(R, "chair", None, _chairpred), x, z, yw), "conference chair", R)
    put(R, "chair", "armchair", 10.5, -17.0, yaw=90 + 180, what="captain's armchair")

    R.line("Head-of-table displays and holo projector",
           "A large tactical screen, a status board and a holo plinth on the north wall east of the bridge door give everyone at "
           "the table a shared picture; the wall is solid so no glazing is lost.")
    wall(R, "N", "display", "tactical_wall_screen", 9.3, y=1.9, what="tactical screen")
    wall(R, "N", "display", "schematics_wall", 3.1, y=1.9, what="schematics display")
    put(R, "holo", "tactical_plinth", 9.9, -19.7, yaw=0, what="holo plinth")

    R.line("Credenza and refreshments",
           "Drawer consoles along the south wall serve as credenza for documents; a coffee machine and water cooler at the west "
           "end serve refreshments without anyone crossing the room during a meeting.")
    cr = []
    for x in (6.6, 8.6):
        cr.append(floor_wall(R, "S", "desk", "drawer_console", x, what="credenza"))
    for c, labs in zip(cr, ([("tableware", "teapot", -0.2, 0.0), ("tableware", "cups_and_mugs", 0.3, 0.0)],
                            [("tableware", "fruit_bowl", 0.0, 0.0)], [("lamp", "table_lamp", 0.0, 0.0)])):
        tops(R, c, None, labs)
    floor_wall(R, "S", "galley", "coffee_machine", 4.6, what="coffee machine")
    floor_wall(R, "S", "galley", "water_cooler", 3.5, what="water cooler")

    R.line("Conference audio and cabinet",
           "Ceiling-wall speaker grille and microphone serve the video links; a utility cabinet holds spare datapads and cables.")
    wall(R, "S", "commsunit", "speaker_grille", 8.6, y=2.4, what="speaker grille")
    floor_wall(R, "W", "cabinet", "utility_cabinet", -19.8, what="utility cabinet")

    R.line("Plants",
           "Two ficus trees against the solid south wall soften the room; none stands near the door or the aisle.")
    put(R, "plant", "ficus", 2.6, -13.9, yaw=0, what="ficus")
    put(R, "plant", "ficus", 10.95, -13.95, yaw=0, what="ficus")

    R.line("Safety and signs", "Extinguisher by the bridge door and a wall clock so meetings keep to time.")
    extinguisher(R, "W", -20.75)
    wall(R, "W", "clock", "digital_clock", -14.3, y=2.4, what="wall clock")
    food_conf(R, B)


# ====================================================================================== ASTROMETRICS
def f_astro(R, B):
    R.describe(
        "Stellar cartography and long-range sensor analysis: the science watch builds the ship's star chart, tracks "
        "objects and plans routes from sensor data.",
        basis="149 m2, 5 operators in a horseshoe of consoles around a 3D star-map globe (operators stand/sit 1.1 m outside the ring "
              "facing in, open end to the door so visitors see the globe); 3 m to the starboard windows with only low items there; "
              "rack wall for the sensor processors on the north wall, analysis desks on the south wall.",
        crew=6,
        adjacency="Door to the corridor on the west wall; starboard hull windows give the view for the optical instruments; "
                  "near the bridge for quick data hand-off.")
    lights(R, spacing=3.8, energy=1.2, color="#dce8ff", x_margin=1.3,
           why="Cool, dimmable light (about 200 lux) so the holographic chart stays visible; fixtures are on a grid clear of the globe.")
    gx, gz = 7.4, -6.5

    R.line("Star-map globe",
           "The holographic star-map globe is the room's purpose; placed in the middle of the room so the operators' ring and the visitors "
           "entering from the door all see it from every side.")
    need(R.place(M(R, "holo", "star_map_globe"), gx, gz, 0.0), "star map globe", R)

    R.line("Sensor horseshoe",
           "Five consoles (sensor, science, navigation, environmental, auxiliary) stand on a 2.4 m radius ring open to the west; each "
           "faces outward to its operator, who sits 1.1 m outside the ring and sees the globe over the console.")
    labs = ["environmental", "console_science", "console_sensor", "navigation", "compact_aux"]
    seats = ["science_stool", "ops_chair", "science_stool", "ops_chair", "swivel_jump"]
    for lab, sl, ang in zip(labs, seats, (-100, -50, 0, 50, 100)):
        a = math.radians(ang)
        x, z = gx + 2.4 * math.cos(a), gz + 2.4 * math.sin(a)
        put(R, "console", lab, x, z, face=(x + math.cos(a), z + math.sin(a)), what="astro console " + lab)
        xs, zs = gx + 3.55 * math.cos(a), gz + 3.55 * math.sin(a)
        put(R, "seat", sl, xs, zs, face=(gx, gz), what="astro seat")

    R.line("Optical and receiver instruments",
           "A spectrograph tripod and a star tracker stand 1.6 m inside the starboard windows, where they see the sky without blocking "
           "the glazing, and the astrometric dish at the north-east corner is the pulsar-navigation receiver feeding the racks.")
    need(R.place(M(R, "telescope", "spectrograph"), 11.3, -9.9, -90.0), "spectrograph", R)
    need(R.place(M(R, "telescope", "star_tracker"), 11.6, -3.2, -90.0), "star tracker", R)
    need(R.place(M(R, "telescope", "astrometric_dish"), 11.8, -12.15, 180.0), "astrometric dish", R)

    R.line("Sensor processing racks",
           "Four processing racks (network switch, blade server, storage array, photonic fibre), a receiver rack and two archive towers "
           "along the north wall turn raw sensor data into the chart and store it; one row keeps cable runs short and gives the "
           "technician one aisle.")
    x = 2.6
    for lab in ("network_switch", "blade_server", "storage_array", "photonic_fiber"):
        floor_wall(R, "N", "rack", lab, x + 0.35, what="rack " + lab)
        x += 0.75
    floor_wall(R, "N", "commsunit", "radio_rack", 6.0, what="receiver rack")
    floor_wall(R, "N", "rack", "crystal_archive", 7.0, what="chart archive tower")
    floor_wall(R, "N", "rack", "tape_archive", 7.85, what="tape archive tower")
    wall(R, "W", "router", "patch_panel", -12.2, y=1.3, what="patch panel")

    R.line("Analysis desks",
           "Two workstations on the south wall are where operators review and annotate the charts away from the noise of the horseshoe; "
           "each has an instrument on it and its own chair.")
    for x in (4.0, 9.4):
        d = floor_wall(R, "S", "desk", "workstation", x, what="analysis desk")
        seat_facing(R, d, cats=("chair",), label="swivel_office", gap=0.3)
        tops(R, d, None, [("analyzer", "spectrometer", -0.3, 0.0), ("terminal", "keyboard", 0.3, 0.1)])
    floor_wall(R, "S", "storage", "cartridge_library", 11.9, what="chart archive")

    R.line("Wall displays",
           "Displays on the west wall repeat the globe picture for people entering; the heading display and scope rack above the racks "
           "are the raw sensor feeds.")
    wall(R, "W", "display", "tactical_wall_screen", -10.5, y=1.9, what="chart display")
    wall(R, "W", "display", "circular_display", -2.5, y=1.8, what="sensor display")
    wall(R, "N", "display", "scope_rack", 10.0, y=1.7, what="scope rack")
    wall(R, "N", "display", "heading_display", 11.5, y=1.7, what="heading display")

    R.line("Plants and lamps", "A ficus brightens the north-west corner; it is away from the windows and the operator ring.")
    put(R, "plant", "ficus", 2.4, -1.0, yaw=0, what="ficus")

    R.line("Safety and signs", "Extinguisher next to the door and department sign.")
    extinguisher(R, "W", -1.5)
    wall(R, "W", "sign", "dept_science", -4.2, y=2.6, what="science sign")
    wall(R, "W", "clock", "analogue", -12.0, y=2.2, what="clock")


# ====================================================================================== OFFICERS' CABINS
def _cabin_units(R, xs, tag, last_desk_south=False):
    """Berths along the N wall: [bed | wardrobe stub | desk+chair] per unit."""
    z_n = R.edge("N")["a"][1]
    for k, x0 in enumerate(xs):
        floor_wall(R, "N", "bed", "single_bunk", x0 + 0.6, what="berth %d" % (k + 1))
        wall(R, "N", "lamp", "reading_light", x0 + 0.6, y=1.3, what="reading light")
        # wardrobe stub: two lockers end to end, perpendicular to the wall, doors toward the bed
        put(R, "locker", "wardrobe", x0 + 1.5, z_n + 0.15 + 0.58 + 0.03, yaw=-90, what="wardrobe")
        if k < len(xs) - 1:
            put(R, "locker", "tall_vented", x0 + 1.5, z_n + 0.15 + 1.16 + 0.03 + 0.26 + 0.02, yaw=-90, what="locker")
        south = last_desk_south and k == len(xs) - 1
        d = floor_wall(R, "S" if south else "N", "desk", "writing_desk", x0 + 2.55, what="desk %d" % (k + 1))
        seat_facing(R, d, cats=("chair",), label="swivel_office", gap=0.3)
        if d:
            tops(R, d, None, [("lamp", "architect", -0.35, 0.0), ("terminal", "laptop", 0.3, 0.0)])


def f_cabinA(R, B):
    R.describe(
        "Three single-occupancy officers' cabins in one block with a shared sitting area: each officer has a berth, a wardrobe and a "
        "desk; the sitting area in the south half is for off-duty conversation.",
        basis="59 m2 for 3 officers (about 20 m2 each incl. share of the sitting area).  Bed 0.92 x 2.08 with its head to the north wall; "
              "wardrobe stubs as 1.7 m privacy dividers between berths (no partitions available); desk 1.2 m wide beside each berth "
              "with 0.6 m clear behind; 1.2 m aisle in front of the berths; sofa group 1.0 m from the berth ends.",
        crew=3,
        adjacency="Door to the corridor on the east wall; cabins B next door to the south; the lounge is across the corridor.")
    lights(R, spacing=3.6, energy=1.0, color="#ffe8cc", x_margin=1.2,
           why="Warm dimmable light (150 lux) for a residential feel; one fixture over the berths, one over the sitting area.")
    R.line("Berths with wardrobe and desk",
           "Three units: bed with its head to the north wall and a reading light above, a wardrobe (and tall locker between neighbours) "
           "standing out from the wall as a privacy divider, and a writing desk with its own chair.  The first two desks are on the north "
           "wall beside the berths; the third is on the south wall so its chair does not crowd the door.  Laptop and desk lamp on each desk.")
    _cabin_units(R, (-12.6, -9.5, -6.4), "A", last_desk_south=True)

    R.line("Shared sitting area",
           "A three-seater sofa with a small side table and an armchair on the south wall give the three officers somewhere to meet without "
           "entering each other's berths; it is 1.2 m from the berth desks so the aisle stays clear.")
    floor_wall(R, "S", "couch", "three_seater", -6.8, what="sofa")
    t = put(R, "table", "side_table", -6.8, 7.3, yaw=0, what="side table")
    tops(R, t, None, [("tableware", "cups_and_mugs", 0.0, 0.0)])
    put(R, "couch", "lounge_armchair", -8.8, 7.3, face=(-6.8, 7.3), what="armchair")

    R.line("Shelves, display and plant",
           "A bookcase, a display and a floor lamp on the south wall make the sitting area feel like a room.")
    floor_wall(R, "S", "shelving", "pigeonhole", -11.0, what="bookcase")
    wall(R, "S", "display", "holo_frame", -6.8, y=1.9, what="display")
    put(R, "lamp", "floor_lamp", -2.6, 8.4, yaw=0, what="floor lamp")

    R.line("Safety and signs", "Extinguisher near the door, cabin-block sign, ship's clock.")
    extinguisher(R, "E", 4.2)
    wall(R, "E", "sign", "dept_quarters", 8.0, y=2.6, what="quarters sign")
    wall(R, "N", "clock", "digital_clock", -2.6, y=2.2, what="clock")
    food_cabin(R, B)


def f_cabinB(R, B):
    R.describe(
        "Two officers' cabins forming the aft half of the officers' block, arranged like block A (berth, wardrobe divider, desk) "
        "with a small sitting corner for the pair.",
        basis="46 m2 for 2 officers (23 m2 each, more than block A because the five hull windows on the taper keep the south and west "
              "walls free of tall furniture); beds 0.5 m or more from the glazing; 1.2 m aisle in front of the berths; armchair pair 1.0 m "
              "from the berth ends.",
        crew=2,
        adjacency="Door to the corridor on the east wall; cabins A to the north share the dividing bulkhead.")
    lights(R, spacing=3.4, energy=1.0, color="#ffe8cc", x_margin=1.0,
           why="Warm dimmable light, one fixture per berth group.")
    R.line("Berths with wardrobe and desk (north wall)",
           "Two units identical to block A along the north bulkhead: head to the wall, wardrobe stub divider, desk and chair; "
           "the north wall is the only one without windows so the beds stand there.")
    _cabin_units(R, (-9.4, -6.3), "B")

    R.line("Sitting corner",
           "Two armchairs facing each other across a side table with a lamp, in the wide middle of the room, give the pair a place to "
           "talk; they are kept 0.5 m or more from the windows on the south wall and the taper.")
    put(R, "couch", "lounge_armchair", -7.6, 12.6, yaw=-90, what="armchair")
    put(R, "couch", "lounge_armchair", -5.6, 12.6, yaw=90, what="armchair")
    st = put(R, "table", "side_table", -6.6, 12.6, yaw=0, what="side table")
    tops(R, st, None, [("lamp", "table_lamp", 0.0, 0.0)])

    R.line("Safety and signs", "Extinguisher near the door and quarters sign.")
    extinguisher(R, "E", 13.1)
    wall(R, "E", "sign", "dept_quarters", 9.45, y=2.6, what="quarters sign")
    wall(R, "N", "display", "chronometer", -3.4, y=2.0, what="clock display")
    food_cabin(R, B)


# ====================================================================================== CAPTAIN'S QUARTERS
def f_capt(R, B):
    R.describe(
        "The captain's private residence: sleeping alcove, dressing, a study corner, a sitting group and a small dining and galley "
        "corner so the captain can live and host two or three guests without leaving the suite.",
        basis="61 m2 for one person (generous by command-deck standards).  Night zone (bed, wardrobes) in the north-east, "
              "day zone (desk, bookcase, sofa group) in the west, dining and galley in the south-east; 1.2 m circulation between "
              "zones; bed 2.05 x 2.9 m with 0.9 m either side; dining table with 0.8 m per seat.",
        crew=1,
        adjacency="Door to the corridor on the west wall; aft of the command deck, close to the lounge and ready room by corridor.")
    lights(R, spacing=3.6, energy=1.1, color="#ffe6c8", x_margin=1.2,
           why="Warm, dimmable light (150-300 lux) with separate fixtures over the bed, study and dining areas.")

    R.line("Captain's bed",
           "The large captain's bed has its head against the north wall in the north-east corner, away from the door and the noise of "
           "the corridor; a bedside light sits on either side.")
    floor_wall(R, "N", "bed", "captain_bed", 10.6, what="captain's bed")
    wall(R, "N", "lamp", "reading_light", 9.8, y=1.75, what="reading light")
    wall(R, "N", "lamp", "reading_light", 11.4, y=1.75, what="reading light")

    R.line("Wardrobes",
           "Two wardrobes between the desk and the bed and a footlocker beside the bed hold uniforms and personal gear, all within "
           "three steps of the bed.")
    floor_wall(R, "N", "locker", "wardrobe", 7.9, what="wardrobe")
    floor_wall(R, "N", "locker", "wardrobe", 6.6, what="wardrobe")
    floor_wall(R, "N", "locker", "footlocker", 12.3, what="footlocker")

    R.line("Study corner",
           "An officer's desk on the north wall with a swivel chair, desk lamp and terminal is where the captain does private "
           "paperwork; a bookcase beside it holds paper books.")
    d = floor_wall(R, "N", "desk", "officer_desk", 5.0, what="captain's desk")
    seat_facing(R, d, cats=("chair",), label="swivel_office", gap=0.3)
    if d:
        tops(R, d, None, [("lamp", "architect", -0.55, 0.0), ("terminal", "desk_terminal", 0.1, 0.0), ("terminal", "datapad", 0.6, 0.0)])
    floor_wall(R, "N", "shelving", "pigeonhole", 2.9, what="bookcase")

    R.line("Sitting group",
           "A sofa and coffee table form the conversation group in the west half, with the display above the sofa.")
    floor_wall(R, "S", "couch", "three_seater", 5.0, what="sofa")
    t = put(R, "table", "coffee_table", 5.0, 6.95, yaw=0, what="coffee table")
    tops(R, t, None, [("tableware", "teapot", -0.2, 0.0), ("plant", "flower_vase", 0.25, 0.0)])
    wall(R, "S", "display", "holo_frame", 5.0, y=2.0, what="display")

    R.line("Dining table for four",
           "A round table with four chairs lets the captain host a small dinner; it stands between the sitting group and the galley "
           "corner so serving is short.")
    dt = put(R, "table", "round_mess_table", 8.0, 6.7, yaw=0, what="dining table")
    if dt:
        for ang in (0, 90, 180, 270):
            a = math.radians(ang)
            x, z = 8.0 + 1.0 * math.cos(a), 6.7 + 1.0 * math.sin(a)
            need(R.place(M(R, "chair", "mess_chair"), x, z, yaw_to(x, z, 8.0, 6.7)), "dining chair", R)
        tops(R, dt, None, [("tableware", "fruit_bowl", 0.0, 0.0)])

    R.line("Galley corner",
           "A refrigerator and sink unit against the south wall east of the dining table, and a coffee machine by the door, let the captain "
           "make coffee and light meals without the galley.")
    floor_wall(R, "S", "galley", "refrigerator", 11.6, what="refrigerator")
    floor_wall(R, "S", "galley", "sink_unit", 10.3, what="sink")
    floor_wall(R, "S", "galley", "coffee_machine", 2.3, what="coffee machine")

    R.line("Plants, lamps and display case",
           "A floor lamp beside the sofa and a display above it give the suite a personal character.")
    put(R, "lamp", "floor_lamp", 3.4, 8.4, yaw=0, what="floor lamp")

    R.line("Safety and signs", "Extinguisher by the door, quarters sign, ship's clock.")
    extinguisher(R, "W", 4.4)
    wall(R, "W", "sign", "dept_quarters", 8.2, y=2.6, what="sign")
    wall(R, "S", "clock", "digital_clock", 7.4, y=2.3, what="clock")
    food_capt(R, B)


# ====================================================================================== COMMUNICATIONS CENTRE
def f_comms(R, B):
    R.describe(
        "Ship's communications centre: subspace and radio traffic with Starfleet-style command, other ships and planets, "
        "encryption and the ship's internal network backbone.",
        basis="44 m2, 3 operator stations on the north wall facing a holo bust projector; 6 racks on the south wall in one row with "
              "1.0 m clear maintenance aisle in front; overhead cable trays; indoor antenna panels on the hull facet and a ceiling "
              "log-periodic for local links.",
        crew=3,
        adjacency="Door to the corridor on the west wall; below the bridge communications station by cable tray; "
                  "on the starboard stern hull for clear antenna paths.")
    lights(R, spacing=3.4, energy=1.2, color="#e7efff", x_margin=1.0,
           why="Neutral, flicker-free light (300 lux) over the operator desks and the rack aisle.")

    R.line("Operator stations",
           "Three communications consoles along the north wall, each with a communications chair, let three operators work in parallel "
           "(voice, data and encrypted traffic); they face the bust projector in the centre, so they see the caller in the room.")
    for lab, x in (("console_communications", 4.0), ("comms_console", 6.3), ("console_communications", 8.6)):
        cat = "console" if lab.startswith("console") else "commsunit"
        con = floor_wall(R, "N", cat, lab, x, what="comms console")
        seat_facing(R, con, cats=("seat",), label="comms_chair", gap=0.3)
        if con and cat == "commsunit":
            tops(R, con, None, [("commsunit", "handset", 0.0, 0.0)])

    R.line("Holo bust projector",
           "A holographic bust projector in the centre shows the person on the other end of a call at life size; it is on the "
           "operators' line of sight and 1.5 m from every console.")
    put(R, "holo", "comm_bust", 6.3, 11.4, yaw=0, what="holo bust projector")

    R.line("Radio and encryption racks",
           "A row of racks along the south wall: radio rack, network switch rack, encryption/KVM rack, photonic fibre rack and an UPS "
           "battery rack so traffic survives a power dip.  The 1.0 m aisle in front gives maintenance access.")
    x = 3.6
    for cat, lab in (("commsunit", "radio_rack"), ("rack", "network_switch"), ("rack", "kvm_console"),
                     ("rack", "photonic_fiber"), ("rack", "ups_battery")):
        p = floor_wall(R, "S", cat, lab, x + 0.36, what="rack " + lab)
        if p:
            x = p["_fp"][2] + 0.04

    R.line("Antennas, patch panel and key safe",
           "A patch panel above the rack row and a secure data safe on the north wall holds the encryption key material; a phased-array panel and a feed-horn panel on the north wall and angled hull wall receive/transmit through the hull "
           "skin; a ceiling log-periodic and antenna pod cover short-range links.  Cabinet for patch panels next to the door.")
    wall(R, "D1", "antenna", "phased_array", 0.8, y=1.6, what="phased array panel")
    wall(R, "D2", "antenna", "feed_horn", 0.9, y=1.4, what="feed horn panel")
    R.place(M(R, "antenna", "ceiling_log_periodic"), 6.3, 11.4, 0.0, y=R.y + R.h)
    R.place(M(R, "antenna", "antenna_pod"), 9.0, 10.4, 0.0, y=R.y + R.h)
    wall(R, "W", "router", "wall_network_cabinet", 9.6, y=1.4, what="network cabinet")
    wall(R, "S", "router", "patch_panel", 5.2, y=2.7, what="patch panel")
    floor_wall(R, "N", "storage", "secure_data_safe", 10.6, what="encryption key safe")

    R.line("Cabling overhead",
           "Cable trays run across the ceiling from the rack row to the consoles and out through the door to the bridge, so no cables "
           "cross the floor.")
    for x in (3.0, 5.0, 7.0):
        R.place(M(R, "cabletray", "cabletray_ladder_tray"), x + 1.0, 13.2, 0.0, y=R.y + R.h)
    for x in (3.0, 5.0, 7.0, 9.0):
        pass

    R.line("Displays",
           "A comms log board and a signal status display above the consoles show traffic and link quality.")
    wall(R, "N", "display", "comms_log_board", 4.0, y=2.3, what="comms log board")
    wall(R, "N", "display", "status_board", 8.6, y=2.3, what="status board")

    R.line("Safety and signs", "Extinguisher beside the door and a department sign.")
    extinguisher(R, "W", 13.5)
    wall(R, "N", "sign", "dept_bridge", 2.4, y=2.6, what="sign")
