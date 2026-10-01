"""Room recipes - Deck 4 (Hold Deck, y = -4 m, the keel deck: no windows, ceilings 3.4 m).

West side (port): antimatter containment, provisions hold, fabrication hall, main cargo hold.
East side (starboard): water reclamation, waste & recycling, auxiliary control, drone & probe bay.
Doors to the spine corridors are on the x = -/+1.5 walls, the hull is the outer wall of every room.
"""
from dressing import *   # noqa: F401,F403
from recipes_deck3_helpers import *   # noqa: F401,F403


def rail(R, B, kind, x0, z0, x1, z1, skip=()):
    """Guard rail around the rectangle (x0, z0)-(x1, z1) built of 2.1 m panels; `skip` lists sides left open ("N","S","E","W")."""
    n = max(1, round((x1 - x0) / 2.1))
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        if "N" not in skip:
            put(R, B, kind, x, z0, 0.0)
        if "S" not in skip:
            put(R, B, kind, x, z1, 180.0)
    n = max(1, round((z1 - z0) / 2.1))
    for i in range(n):
        z = z0 + (z1 - z0) * (i + 0.5) / n
        if "W" not in skip:
            put(R, B, kind, x0 - 0.25, z, 90.0)       # offset 0.25 m so the corner posts do not overlap the N / S panels
        if "E" not in skip:
            put(R, B, kind, x1 + 0.25, z, -90.0)


def sign_at(R, B, side, mid, along, y=2.6):
    return wall_y(R, B, side, mid, along, y, check=False)


def desk_station(R, B, side, desk, along, terminals=("terminal_desk_terminal", "terminal_keyboard"), chair="chair_swivel_office_chair"):
    d = aw(R, B, side, desk, along)
    seat_for(R, B, d, chair)
    if d:
        tops(R, B, d, list(terminals), [(0.0, -0.12), (0.0, 0.17)][:len(terminals)])
    return d


# ----------------------------------------------------------------------------------------------- ANTIMATTER CONTAINMENT
def f_antimatter(R, B):
    R.describe(
        "Antimatter Containment holds the ship's reserve of antihydrogen in magnetic bottles and feeds it, a few milligrams at a time, "
        "to the matter / antimatter injector that powers the warp core; it is the most dangerous room aboard and is staffed by a "
        "two-person containment watch.",
        basis="The trap (a plasma torus) stands alone inside a 4.2 m guard rail with a force-field gate facing the door; the bottle store, "
              "capacitor banks and field coils ring it on the hull facets so every cable is short; 1.4 m aisles all round, the 2 m door "
              "approach is kept clear. Reserve: 3 magnetic bottles x 0.5 mg antihydrogen = 1.5 mg, enough for about 90 days at 0.017 mg/day "
              "cruise load. Emergency coolant: a 4 m3 vertical tank (about 8 minutes of full boil-off cooling). Operators sit 5 m from the "
              "trap behind the rail; a radiation shelter panel and a decontamination station are by the door.",
        crew=2,
        adjacency="Forward spine corridor (east door); Provisions Hold is directly south across the bulkhead; Water Reclamation "
                  "is across the corridor; the injector feeds the warp-core plasma trunk that rises to Main Engineering.",
        notes="Tapered bow compartment: bottles and capacitors sit on the hull facets, the trap in the widest part of the room.")
    R.line("Ceiling lighting", "Violet-tinted high-output panels at 3.5 m pitch give 400 lux at the consoles and make the field-coil glow readable; "
           "they hang over the aisles, never over the trap.")
    lights(R, spacing=3.5, color="#e8e0ff", energy=1.6)

    TX, TZ = -5.9, -13.0
    R.line("Antimatter trap (plasma torus)",
           "The Penning-style trap that actually holds the antihydrogen is a plasma torus; it stands alone in the middle of the widest part "
           "of the room so the coils, bottles and injector are all about the same distance away and the hull is not in the radiation line "
           "of the crew corridor. It is 2.8 m tall and fits under the 3.4 m ceiling with the overhead trays.")
    put(R, B, "reactor_plasma_tokamak_torus", TX, TZ, 0.0)
    R.omni(TX, 1.5, TZ, "#c060ff", 2.2, 9.0, shadow=True)
    R.omni(TX, 0.4, TZ, "#7040ff", 1.0, 5.0)

    R.line("Guard rail and force-field gate",
           "A 4.2 m rail keeps people 0.7 m from the trap's shielding; its east side is a force-field gate that drops only for the maintenance "
           "party, so a visitor entering through the door is stopped by a visible barrier instead of a latch.")
    rail(R, B, "railing_guard_mesh", TX - 2.1, TZ - 2.1, TX + 2.1, TZ + 2.1, skip=("E",))
    put(R, B, "forcefield_emitter_pair", TX + 2.1, TZ, -90.0)

    R.line("Magnetic bottle store (west hull facets)",
           "The three reserve bottles stand in a row on the hull facets; each bottle is a separate 0.5 mg pocket, so a failure of one can only release "
           "one pocket and the hull behind them is the best shielded wall of the room. Fronts face the trap so a technician sees all dials.")
    aw(R, B, "D1", "coil_magnetic_bottle", 0.67)
    aw(R, B, "D3", "coil_magnetic_bottle", 0.78)
    wall_row(R, B, "S", ["coil_magnetic_bottle"], -10.3)

    R.line("Field coils (north hull facets)",
           "The dilithium chamber that regulate the containment field and the injector pulse stand at the narrow "
           "bow end, in the order of the plasma path; their long cable runs go overhead to the trap.")
    aw(R, B, "D7", "coil_dilithium_crystal_chamber", 0.97)

    R.line("Matter / antimatter injector (south wall)",
           "The injector is the 3.5 m throat between the trap and the warp-core plasma trunk, so it stands against the south wall that is shared with "
           "the trunk riser; it points to the trap with a 0.9 m aisle in front.")
    wall_row(R, B, "S", ["reactor_matter_antimatter_injector"], -9.0)
    wall_y(R, B, "S", "display_power_board", -3.4, bottom=2.15)
    wall_y(R, B, "S", "controlpanel_valve_control", -11.4, 1.5)

    R.line("Capacitor banks (south wall, east of the injector)",
           "Capacitor and Marx banks store the energy for the injection pulse and for a fast field re-seal; "
           "they stand next to the injector so the discharge cable is short and shielded.")
    wall_row(R, B, "S", ["capacitor_marx_bank", "capacitor_capacitor_bank_rack"], -5.4, gap=0.08)

    R.line("Emergency cooling (north-east corner)",
           "If the field fails the antihydrogen annihilates and heats the vessel; a vertical coolant tank floods the trap jacket "
           "within seconds (4 m3 of coolant). They stand in the north-east corner of the corridor wall, valved from the console, and are the "
           "first thing a duty engineer reaches in an emergency.")
    aw(R, B, "E", "tank_vertical_coolant_tank", -18.65)

    R.line("Operator console and seat (east wall, north of the door)",
           "The containment watch works from a console on the east wall about 4 m from the trap: from the chair the force-field gate, the trap "
           "and the bottle dials are in view at once, with the watch's back to the corridor wall and the door at their shoulder.")
    con = aw(R, B, "E", "console_engineering_status", -16.65)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.15)])
    wall_y(R, B, "E", "display_status_board", -16.65, bottom=2.0, check=False)

    R.line("Radiation and decontamination station (east wall, south of the door)",
           "Anyone leaving the room passes the glove / boot locker, an emergency shower and the hazmat cabinet before reaching the corridor; the "
           "radiation shelter panel and an eye wash are beside them, and the south wall holds the dose-monitoring display.")
    wall_row(R, B, "E", ["suitrack_glove_boot_locker", "safety_emergency_shower", "safety_hazmat_cabinet"], -12.5, dirn=1, gap=0.05)
    wall_y(R, B, "N", "safety_radiation_shelter_panel", -2.25, 1.5, check=False)
    wall_y(R, B, "D0", "safety_eye_wash_station", 0.62, 1.1)

    R.line("Maintenance cart, tool locker and spares",
           "A diagnostic cart stands in the south-west aisle for the weekly service; the cart and chest are on "
           "wheels, so they can be rolled to the trap only when a procedure calls for them.")
    put(R, B, "engtool_diagnostic_cart", -10.3, -11.3, 0.0)

    R.line("Overhead trays, pipes and ducts",
           "Cable trays carry the coil currents and sensor fibre from the banks to the trap; insulated coolant pipes follow them, and a duct "
           "removes any gas from the room. All overhead so the floor stays free of trip hazards.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 3, -9.0, -10.5, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 2, -7.5, -15.8, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 3, -9.4, -13.0, "x")

    R.line("Ceiling sensors, sprinklers and alert bars",
           "Dome cameras over the trap and the bottle store give the control room a view with no operator in the line of fire; sprinkler heads "
           "protect the capacitors, and a red alert bar over the gate flashes when the field drops below nominal.")
    for x, z in ((-7.5, -12.0), (-4.5, -12.0), (-10.0, -12.5)):
        R.place(mm(B, "camera_dome_ceiling"), x, z, 0.0, y=R.y + R.h)
    for x, z in ((-8.0, -9.9), (-4.4, -9.9), (-3.0, -16.5)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)
    R.place(mm(B, "beacon_red_alert_bar"), -4.4, -13.0, 90.0, y=R.y + R.h)

    R.line("Hazard warnings, beacons and fire safety",
           "Radiation, high-voltage and low-oxygen signs on the rail approach and the bottle store; a rotating beacon warns when the field "
           "is below nominal, the red-alert unit repeats the ship alert, and extinguishers stand by the door and the capacitors.")
    sign_at(R, B, "E", "sign_hazard_radiation", -18.65, 3.0)
    sign_at(R, B, "S", "sign_hazard_high_voltage", -9.0, 2.95)
    sign_at(R, B, "D2", "sign_hazard_low_oxygen", 0.7, 2.6)
    sign_at(R, B, "E", "sign_emergency_exit", -14.0, 2.9)
    wall_y(R, B, "E", "warnlight_red_alert_wall_unit", -15.7, bottom=2.7, check=False)
    wall_y(R, B, "S", "beacon_rotating_beacon", -2.3, 2.9)
    fe(R, B, "D2", 0.72)
    fe(R, B, "D2", 0.72)
