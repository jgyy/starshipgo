"""Room recipes - Deck 4 (Hold Deck, y = -4 m, the keel deck: no windows, ceilings 3.4 m).

West side (port): antimatter containment, provisions hold, fabrication hall, main cargo hold.
East side (starboard): water reclamation, waste & recycling, auxiliary control, drone & probe bay.
Doors to the spine corridors are on the x = -/+1.5 walls, the hull is the outer wall of every room.
"""
from dressing import *   # noqa: F401,F403
from recipes_deck3_helpers import *   # noqa: F401,F403
from recipes_deck3_helpers import _log


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


def aw_try(R, B, side, mid, alongs, **kw):
    """Like aw() but tries several positions along the wall and keeps the first that fits (silent miss only if none fits)."""
    m = mm(B, mid)
    for a in alongs:
        p = R.against_wall(side, m, a, gap=kw.get("gap", 0.04))
        if p is None and os.environ.get("DBG4"):
            e = R.edge(side)
            print("DBG", mid, side, a, e and e.get("len"), R.wall_span(side), m["size"], file=sys.stderr)
        if p is not None:
            return p
    _log(R, mid, (side, alongs))
    return None


def mark(R, B, x, z, yaw=0.0, mid="sign_floor_marking"):
    """Flat floor stencil (lane / bay marking): ignored by the overlap and clearance rules, may lie inside a keep-clear lane."""
    return R.place(mm(B, mid), x, z, yaw, check=False, reserve=False)


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
    fe(R, B, "D5", 0.9)


# ----------------------------------------------------------------------------------------------- PROVISIONS HOLD & COLD STORE
def f_provisions(R, B):
    R.describe(
        "The Provisions Hold is the ship's larder: frozen and chilled food in a cold store on the hull side, dry goods, oils and "
        "staples on pallets and shelving, and an inventory desk that tells the galley what is left.",
        basis="Planned for 120 crew on a 180-day voyage: 120 x 0.65 kg/day of food = 78 kg/day = 14 t, of which about 40 % is frozen "
              "or chilled. 5 cryo storage tanks (about 1 t each) and 5 freezer / refrigerator units hold the cold share; about 15 "
              "pallets of staples (sacks, boxed rations, drums of oil) stand in two rows either side of a 2.8 m forklift lane from "
              "the door; hydroponics on Deck 2 supplies fresh produce, so the hold carries 150 days of fully balanced rations plus "
              "30 days of emergency ration packs in sealed lockers. Aisles are 1.2 m at the shelving and 2.8 m on the forklift lane.",
        crew=2,
        adjacency="Forward spine corridor (east door); Antimatter Containment is directly north (the north wall is a radiation "
                  "bulkhead), Waste & Recycling across the corridor; the galley two decks up is served by the stair towers.",
        notes="Food added later (produce, packaged meals, drink crates) goes to the pallet rows and the cold-store bays.")
    R.line("Ceiling lighting", "Cool white panels (300 lux) light the aisles and read the pallet labels; the cold store gets the same lights, "
           "which stay on while the door field is open.")
    lights(R, spacing=3.5, color="#eaf4ff", energy=1.5)

    R.keep_clear((-8.8, -5.8, -1.5, -3.2), "2.8 m forklift lane from the corridor door into the hold")
    R.line("Cold store: cryo storage tanks (west hull wall)",
           "Frozen meat, fish and bread dough are held in liquid-nitrogen cooled storage tanks on the hull wall, the coldest and best insulated wall "
           "of the room; the control pillar at the end shows temperature and nitrogen level of every tank.")
    wall_row(R, B, "W", ["cryo_cryo_storage_tank"] * 5 + ["cryo_cryo_control_pillar"], -7.8, gap=0.05)

    R.line("Cold store: freezers and refrigerators (inner row)",
           "Chest freezers hold the daily-use frozen stock, upright refrigerators the dairy, eggs and fresh produce; the units stand with "
           "their backs to the cold-zone boundary so their compressors vent to the warm side, and open to the cold-store aisle.")
    line_z(R, B, ["galley_chest_freezer", "galley_refrigerator"], -10.1, -7.85, -90.0, gap=0.05, dirn=1)
    line_z(R, B, ["galley_chest_freezer", "galley_refrigerator"], -10.1, -2.6, -90.0, gap=0.05, dirn=1)

    R.line("Cold store boundary (force-field curtain)",
           "The cold-store door is a force-field curtain, not a hinged door: pallets and people pass the 3 m opening without losing the cold "
           "(the field holds the air in), and the field projectors flank the opening on the lane axis.")
    put(R, B, "forcefield_emitter_pair", -9.0, -7.35, 90.0)
    put(R, B, "forcefield_emitter_pair", -9.0, -1.65, 90.0)
    sign_at(R, B, "N", "sign_hazard_low_oxygen", -9.7, 2.8)

    R.line("Nitrogen supply and liquid-nitrogen dewars (north-west corner)",
           "The cryo tanks are topped up from liquid-nitrogen dewars and an inert-gas trio stands beside them; nitrogen is heavier than "
           "air in the cold store, so the low-oxygen sign is at the entrance and the dewars are on the wall, never free-standing.")
    wall_row(R, B, "N", ["cylinder_cryo_dewar", "cylinder_nitrogen_cylinder_trio"], -12.4, gap=0.1)

    R.line("Dry goods shelving and water buffer (north wall)",
           "Packaged rations, spices, tea and coffee, tinned goods and baking supplies stand on heavy-duty shelves along the north wall, "
           "grouped by use so the cook finds them; the galley's own potable water tank ends the row, so a failure of the reclamation plant "
           "does not stop the kitchen in its first days.")
    wall_row(R, B, "N", ["shelving_heavy_boxes", "shelving_heavy_boxes", "watertank_potable_water_tank"], -8.4, gap=0.06)

    R.line("Staple pallets (north row)",
           "Rice and flour sacks, boxed rations and a mixed pallet of pasta and cereal stand in a row 1.2 m from the shelving, "
           "labelled on the lane side; a pallet is 1.2 x 1.0 m so the forklift lifts it straight out into the lane.")
    line_x(R, B, ["pallet_sacks_stacked", "pallet_boxes_layered", "pallet_mixed_goods"], -8.4, -6.45, 0.0, gap=0.08)

    R.line("Oils, drinks and tinned stock (south pallet row)",
           "Drums of cooking oil and vinegar, a wrapped pallet of bottled drinks and a roll cage of fast-moving items stand in the south row, "
           "nearest the galley dispatch; the bung of each drum is turned towards the lane.")
    line_x(R, B, ["pallet_drums_banded", "pallet_wrapped_stack", "pallet_roll_cage_loaded"], -8.4, -2.35, 0.0, gap=0.08)

    R.line("South wall: small stores and ration lockers",
           "Emergency ration lockers (30 days of sealed packs, ready to grab in an evacuation) and shelves for small items stand on the south wall; "
           "ration lockers are locked and sealed so the emergency stock cannot be eaten by accident.")
    wall_row(R, B, "S", ["shelving_pigeonhole", "shelving_parts_bins_rack", "safety_ration_locker", "safety_ration_locker"], -8.5, gap=0.06)

    R.line("Forklift and pallet jack (east wall, south of the door)",
           "The platform forklift is parked against the east wall south of the door, nose to the lane, and the hand pallet jack beside it handles "
           "the daily galley pick; 2.8 m of lane is kept between the vehicles and the north pallet row.")
    put(R, B, "loader_platform_forklift", -2.3, -1.6, 180.0)
    put(R, B, "loader_hand_pallet_jack", -3.9, -1.7, 180.0)

    R.line("Inventory desk and terminal (east wall, north of the door)",
           "The storekeeper counts every pallet in and out at a desk beside the door; the terminal keeps the stock list and shows days of supply "
           "left per item to the galley and the quartermaster.")
    desk_station(R, B, "E", "desk_workstation", -6.75)
    wall_y(R, B, "E", "display_status_board", -6.75, bottom=2.0)

    R.line("Safety and signs",
           "Extinguishers at the door and the cold store, exit sign, first-aid cabinet by the desk and a fire blanket, as for any store of food "
           "packaging and oil.")
    fe(R, B, "N", -1.9)
    fe(R, B, "W", -0.3)
    sign_at(R, B, "E", "sign_emergency_exit", -4.5, 2.9)
    sign_at(R, B, "E", "sign_dept_cargo", -8.4, 2.9)
    wall_y(R, B, "E", "safety_first_aid_cabinet", -8.4, 1.3)

    R.line("Overhead pipes and trays",
           "Refrigerant lines run overhead from the cold store compressors to the tanks, with cable trays beside them; all overhead.")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, -12.0, -8.2, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, -12.0, -0.8, "x")

    R.line("Lane markings, sprinklers and cameras",
           "Floor stencils mark the 2.8 m forklift lane so pallets are never left in it; sprinkler heads protect the oil drums and packaging, "
           "and a camera covers the door and the cold-store curtain for the inventory audit.")
    for x in (-7.8, -5.4, -3.6):
        mark(R, B, x, -4.5, 90.0)
    for x, z in ((-7.0, -4.5), (-5.0, -7.9), (-5.0, -0.6)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)
    R.place(mm(B, "camera_dome_ceiling"), -6.0, -4.5, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- WATER RECLAMATION PLANT
def f_water(R, B):
    R.describe(
        "The Water Reclamation Plant recovers drinking-quality water from every source on the ship (showers, sinks, galley, laundry, "
        "humidity condensate and the waste plant's liquor): grey water goes in at the sump, passes the filters and membranes, "
        "is sterilised, tested and ends in the potable tank that feeds the ship's mains.",
        basis="Sized for 120 crew at 100 l/person/day = 12 m3/day of grey water at a 96 % recovery (11.5 m3/day returned), so the "
              "RO skid is rated 0.5 m3/h (24 h a day). The potable tank holds 24 h of supply (12 m3 incl. the Deck-3 buffer). "
              "Process order along the south wall follows the flow: sump, grey-water processor, filtration, reverse osmosis, "
              "distillation / UV sterilising, potable storage; 1.2 m aisle in front of the train, the entry lane from the door is kept "
              "2.6 m wide, pumps stand on their own row so noisy machines are on the other side of the aisle from the control desk.",
        crew=2,
        adjacency="Forward spine corridor (west door); Antimatter Containment across the corridor; Waste & Recycling is directly "
                  "south; Life Support (Deck 3) above feeds the grey-water riser and takes the potable return.",
        notes="Tapered bow compartment: the bulky vessels sit on the hull facets, the process train on the straight south wall.")
    R.line("Ceiling lighting", "Cool-white panels at 3.5 m pitch (350 lux) over the aisles, with the lamps on the process train at gauge level.")
    lights(R, spacing=3.5, color="#e6fbff", energy=1.5)

    R.line("Grey-water sump and pump row",
           "Grey water arrives in a sump and is lifted by a piston pump and a circulation pump (duty / standby) into the process train; the pump row stands "
           "in front of the entry lane, back to the north, fronts facing the train so a technician sees the gauges and the sight glasses.")
    line_x(R, B, ["tank_sump_tank", "tank_piston_pump_skid", "tank_circulation_pump"], 4.7, -11.95, 0.0, gap=0.2)

    R.line("Process train (south wall)",
           "Left to right along the wall in flow order: grey-water processor (settles solids), filtration unit (sand and carbon), reverse-osmosis "
           "skid (removes salts, 96 % recovery), distillation column (polishing), UV purifier (final sterilising), and the 12 m3 potable tank. "
           "Putting them in a row keeps each pipe joint short and lets one operator walk the whole process.")
    wall_row(R, B, "S", ["watertank_greywater_processor", "tank_filtration_unit", "watertank_reverse_osmosis_skid",
                          "watertank_uv_water_purifier", "watertank_potable_water_tank"], 2.6, gap=0.12)
    R.line("Process pipework, valves and gauges (south wall, above the train)",
           "Pipes carrying the water between stages run along the wall above the vessels, with a flow meter, pressure gauges and isolating valves "
           "at gauge height so every stage can be isolated and read without climbing.")
    wall_run(R, B, "S", "pipe_insulated_wrapped", 2.6, 11.0, 3.2)
    for x, mid in ((3.6, "valve_flow_meter"), (5.4, "valve_pressure_regulator"), (6.9, "valve_dial_gauge"), (8.3, "valve_gauge_cluster"),
                   (9.6, "valve_sight_glass"), (10.7, "valve_gate_valve_wheel")):
        wall_y(R, B, "S", mid, x, bottom=2.25)

    R.line("Hull-facet vessels (north-east facets)",
           "The tall vessels - distillation of the condensate stream, the condensate collector and the water recycler - stand on "
           "the hull facets, one per facet so the pipes reach them from the north wall trunk and the floor load is carried by the hull frames; "
           "fronts face the entry lane.")
    aw(R, B, "D1", "watertank_distillation_column", 0.97)
    aw(R, B, "D3", "watertank_condensate_collector", 0.9)
    aw(R, B, "D5", "watertank_water_recycler", 0.78)

    R.line("Water quality laboratory bench (west wall, north of the door)",
           "A wet bench with a sink and a mass spectrometer test every batch before it enters the potable tank (conductivity, pH, TOC, "
           "bacteria); the lab corner is next to the door so the technician can reach the sample port without crossing the plant.")
    bench = aw(R, B, "W", "labbench_wet_bench_sink", -16.45)
    aw(R, B, "W", "analyzer_mass_spectrometer", -18.45)
    if bench:
        tops(R, B, bench, ["analyzer_gas_chromatograph", "analyzer_centrifuge"], [(-0.45, 0.0), (0.45, 0.0)])
    put(R, B, "labbench_lab_stool", 3.1, -16.45, 90.0)
    wall_y(R, B, "W", "display_vitals_monitor", -16.45, bottom=2.0, check=False)

    R.line("Plant control console and seat (west wall, south of the door)",
           "The operator monitors flow, pressure and water quality from a console near the door, with the whole process train and the pump row in view "
           "and an alarm display above; a keyboard terminal on the desk lets the operator set the duty pump and the dosing.")
    con = aw(R, B, "W", "console_environmental", -11.45)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.15)])
    wall_y(R, B, "W", "display_power_board", -11.45, bottom=2.1, check=False)
    aw(R, B, "W", "cabinet_utility_cabinet", -9.7)

    R.line("Dosing chemicals and spill containment (north-east)",
           "Chlorine-free polishing still needs anti-scalant and cleaning chemicals: two drums stand on a spill sump in the north corner, away from the lab and the door, with an eye wash and a spill kit so a leak is contained and treated at once.")
    put(R, B, "barrel_chemical_drum_hazard", 5.8, -16.4, 0.0)
    put(R, B, "barrel_plastic_drum_lidded", 6.6, -16.0, 0.0)
    put(R, B, "safety_spill_kit_bin", 4.7, -16.4, 0.0)
    wall_y(R, B, "D2", "safety_eye_wash_station", 0.9, 1.1)

    R.line("Spare membranes and filter cartridges",
           "RO membranes and carbon cartridges last about six months; spares for one change stand in a parts-bin stand by the lab so the "
           "technician can change a stage without fetching them from the depot.")
    put(R, B, "storagebin_parts_bins_stand", 3.5, -18.5, 0.0)

    R.line("Service cart",
           "A diagnostic cart is kept by the lab for the weekly inspection; it stands in the north-west corner clear of the entry lane.")
    put(R, B, "engtool_diagnostic_cart", 3.6, -17.3, 90.0)

    R.line("Overhead pipes and trays",
           "Insulated feed and return lines and cable trays run overhead from the grey-water riser by the door to the process train and out to "
           "the potable mains; the floor stays clear.")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, 3.0, -10.4, "x")
    ceil_run(R, B, ["pipe_ceiling_flanged_twin"] * 3, 3.0, -12.9, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 2, 3.6, -15.8, "x")

    R.line("Safety and signs",
           "Biohazard sign (grey water carries pathogens), wet-floor stands on the aisle, exit sign above the door, extinguishers at both ends of the "
           "train and sprinkler / dome camera in the ceiling.")
    sign_at(R, B, "S", "sign_hazard_biohazard", 12.0, 2.9)
    sign_at(R, B, "W", "sign_emergency_exit", -14.0, 2.9)
    sign_at(R, B, "W", "sign_dept_engineering", -17.0, 2.9)
    fe(R, B, "N", 2.25, y=1.9)
    fe(R, B, "S", 12.3)
    put(R, B, "sign_wet_floor_stand", 7.5, -10.7, 0.0)
    for x, z in ((6.0, -10.7), (10.0, -10.7)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)
    R.place(mm(B, "camera_dome_ceiling"), 6.5, -13.0, 0.0, y=R.y + R.h)
    wall_y(R, B, "W", "warnlight_red_alert_wall_unit", -13.0, bottom=2.9, check=False)


# ----------------------------------------------------------------------------------------------- WASTE & RECYCLING PLANT
def f_waste(R, B):
    R.describe(
        "The Waste & Recycling Plant takes everything the crew throw away - paper, plastics, metal, food scraps, medical and "
        "chemical waste - sorts it, shreds and bales what can be re-made in the Fabrication Hall, digests the wet waste into compost "
        "and gas, and burns only the residue.",
        basis="Sized for 120 crew at 0.8 kg of solid waste per person per day = 96 kg/day (about 17 t over a 180-day voyage before "
              "recycling; 85 % is recovered). Material flow runs west to east along the north wall: intake hopper and chutes, "
              "two sorting conveyors, a shredder / compactor; baled output goes onto pallets on the south wall for the forklift "
              "(2.8 m lane from the door); wet waste goes to the digester in the south-east corner and the exhaust is scrubbed "
              "before it rejoins the ship's air. The grating floor lets spills drain to the sump.",
        crew=2,
        adjacency="Forward spine corridor (west door); Water Reclamation directly north (liquor from the digester goes there), "
                  "Provisions Hold across the corridor; the Fabrication Hall aft receives the baled metal and plastic.",
        notes="Negative air pressure: the room draws air towards its own scrubbers so odour never reaches the corridor.")
    R.line("Ceiling lighting", "Sealed industrial panels (350 lux) over the line and the lane; washable, with the lamps clear of the conveyors.")
    lights(R, spacing=3.5, color="#f2f2e8", energy=1.5)
    R.keep_clear((3.4, -5.8, 11.9, -3.2), "2.8 m forklift lane from the corridor door to the bale pallets and the digester")

    R.line("Operator station (west wall, north of the door)",
           "One operator runs the whole line from a console at the intake end: the seat faces east along the conveyors, so the operator sees the "
           "hopper, the belts and the compactor at once and is close to the door for a quick exit.")
    con = aw(R, B, "W", "console_ops", -7.7)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.15)])
    wall_y(R, B, "W", "display_status_board", -7.7, bottom=2.0, check=False)

    R.line("Intake hopper, chutes and sorting conveyors (north wall)",
           "Waste from the ship's chutes falls onto the first belt; the bulk hopper takes large items and crates; the two 3 m belts give 6 m of sorting "
           "length so two people can pick glass, metal and plastics before the shredder. Chute doors are over the belt so nothing drops on the floor.")
    put(R, B, "storagebin_bulk_hopper", 4.6, -8.15, 0.0)
    put(R, B, "loader_conveyor_segment_3m", 6.9, -8.06, 90.0)
    put(R, B, "loader_conveyor_segment_3m", 9.96, -8.06, 90.0)
    put(R, B, "storagebin_trash_compactor", 12.0, -8.3, 0.0)
    for x in (6.1, 7.3):
        wall_y(R, B, "N", "bin_waste_chute_door", x, 2.0)
    wall_y(R, B, "N", "bin_incinerator_hatch", 9.4, 2.2)

    R.line("Shredder / blower and off-gas scrubbing (east wall, north)",
           "The shredder housing and blower reduce the sorted waste to flake for baling; its exhaust runs through a HEPA unit and a catalytic "
           "converter that remove dust and odour before the air returns to the ship, so they stand together on the east wall.")
    aw(R, B, "E", "scrubber_hepa_particulate_unit", -6.6)
    wall_y(R, B, "E", "controlpanel_power_isolator", -5.6, 1.4, check=False)

    R.line("Digester and sump (east wall, south of the lane)",
           "Food scraps and sewage solids go into a closed pressure vessel (anaerobic digester, 4 m3, about 3 weeks retention) which makes compost and "
           "biogas; the sump tank takes the liquor to the water plant. They stand in the south-east corner away from the door and the operator.")
    aw(R, B, "E", "tank_spherical_pressure_vessel", -2.2)
    wall_y(R, B, "E", "valve_dial_gauge", -2.2, bottom=2.5)

    R.line("Sorting bins and hazardous waste (south wall, west)",
           "Crew drop sorted waste into triple recycling bins; medical and chemical waste have their own sealed hazmat cabinets and a drum bay "
           "with a spill kit beside the bins, so hazardous waste is never mixed into the general stream.")
    wall_row(R, B, "S", ["bin_recycling_bin_triple", "bin_recycling_bin_triple", "bin_trash_bin", "bin_trash_bin",
                          "safety_hazmat_cabinet", "safety_hazmat_cabinet", "barrel_chemical_drum_hazard"], 2.6, gap=0.06)

    R.line("Baled output pallets (south wall, east)",
           "Baled metal, plastic flake, cartons and finished compost are stacked on pallets on the south wall, nearest the digester and the lane; the "
           "forklift takes them to the Fabrication Hall and the hold.")
    wall_row(R, B, "S", ["pallet_wrapped_stack", "pallet_sacks_stacked"], 9.0, gap=0.08)

    R.line("Forklift, pallet jack and crates",
           "The hand pallet jack for the baled pallets is parked on the south side of the lane near the door, so the "
           "operator can fetch a pallet without leaving the line; the forklift comes from the depot for the heavy loads.")
    put(R, B, "loader_hand_pallet_jack", 4.0, -1.8, 0.0)

    R.line("Decontamination and PPE (west wall, south of the door)",
           "Anyone handling waste dresses at the glove / boot locker beside the door and washes in the emergency shower on the way out; "
           "the corridor is never entered in work clothes.")
    wall_row(R, B, "W", ["safety_emergency_shower", "suitrack_glove_boot_locker"], -3.0, gap=0.04)

    R.line("Cleaning drone",
           "A floor-scrubbing drone cleans the grating between the line and the lane overnight and returns to its dock.")
    put(R, B, "cleaningbot_floor_scrubber_disc", 5.5, -2.0, 0.0)

    R.line("Overhead ducts, trays and ventilation",
           "Exhaust vents in the ceiling draw air towards the scrubbers (negative pressure) and cable trays carry the conveyor and compactor "
           "power; all overhead.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 3.9, -4.5, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, 3.9, -0.9, "x")
    for x, z in ((5.5, -7.0), (8.5, -7.0), (11.0, -7.0), (5.5, -1.8)):
        R.place(mm(B, "duct_ceiling_round_vent"), x, z, 0.0, y=R.y + R.h)

    R.line("Safety and signs",
           "Biohazard and no-entry signs, extinguishers at the door and by the digester (biogas) and an exit sign over the door; the emergency shower "
           "by the door doubles as the eye wash.")
    sign_at(R, B, "E", "sign_hazard_biohazard", -4.5, 2.7)
    sign_at(R, B, "W", "sign_emergency_exit", -4.5, 2.9)
    sign_at(R, B, "N", "sign_dept_engineering", 2.7, 2.9)
    fe(R, B, "E", -3.4)
    fe(R, B, "N", 3.3)
    R.place(mm(B, "safety_sprinkler_head"), 7.0, -5.2, 0.0, y=R.y + R.h)
    R.place(mm(B, "camera_dome_ceiling"), 8.0, -3.9, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- FABRICATION HALL
def f_fab(R, B):
    R.describe(
        "The Fabrication Hall is the ship's own factory: it makes spare parts, tools and fittings from stock material and from the "
        "baled metal and plastic of the recycling plant, so a failed part can be replaced in hours instead of weeks.",
        basis="Work flows from raw stock (pallet racking on the north wall) to machine (3D fabricators and the materials tester on the hull wall), "
              "to finishing and assembly (two bench islands in the middle), to dirty trades (washing, welding, painting on the south wall) and "
              "out to the depot through the corridor door; designs are drawn at the design corner by the door. A 1.5 m aisle runs along the racks "
              "(hand pallet jack route), 1.8 m between hull-wall machines and the islands, 2.6 m clear in front of the door. "
              "Crew of 4 on a normal shift (2 machinists, 1 welder / finisher, 1 designer); 4 fabricators can print about 40 kg of parts per day.",
        crew=4,
        adjacency="Aft spine corridor (east door); Auxiliary Control is across the corridor; Main Cargo Hold is directly south and "
                  "Workshop and Spares Depot are on Deck 3 above, reached by the stair towers.",
        notes="Welding, painting and washing are all on the south wall with the ducted extraction above, away from the clean printers.")
    R.line("Ceiling lighting", "Bright neutral-white panels (500 lux) for precision work; on top of that every bench has a task lamp on the "
           "tool board above.")
    lights(R, spacing=3.4, color="#fff6e8", energy=1.7)

    R.line("Stock material racking (north wall)",
           "Aluminium and steel bar, plate, plastic feedstock and spools of filament are stored on low-bay pallet racking along the north wall, "
           "furthest from the door, with heavy boxes of fasteners beside it; the forklift or pallet jack serves them from the 1.5 m aisle in front.")
    wall_row(R, B, "N", ["pallet_rack_bay_low_wire", "pallet_rack_bay_low_wire", "shelving_heavy_boxes"], -12.5, gap=0.08)
    wall_row(R, B, "N", ["locker_double_locker_bank"], -4.4)

    R.line("3D fabricator line (west hull wall)",
           "Four metal / polymer 3D fabricators and the materials tester stand in a row on the hull wall so power and the cooling lines run on one "
           "trunk, and every printed part goes straight to the tester beside it; fronts face the middle of the room for loading and part removal.")
    wall_row(R, B, "W", ["analyzer_3d_fabricator"] * 4 + ["analyzer_materials_tester"], 5.1, gap=0.08)
    con = aw(R, B, "W", "console_compact_aux", 11.35)
    seat_for(R, B, con, "seat_ops_chair")
    wall_y(R, B, "W", "display_status_board", 9.9, bottom=2.2, check=False)

    R.line("Assembly and inspection islands (middle)",
           "Two bench islands take the finished parts: one with vises for fitting and filing, one reagent-style bench with a spectrometer for "
           "surface and composition checks. Island benches stand back to back so one power pedestal feeds both; 1.8 m aisles all round.")
    bench1 = put(R, B, "engtool_work_bench_with_vise", -8.4, 7.45, 0.0)
    bench2 = put(R, B, "engtool_work_bench_with_vise", -8.4, 8.6, 180.0)
    for b in (bench1, bench2):
        if b:
            tops(R, B, b, ["engtool_hand_tool_set", "toolbox_tabletop_toolbox"], [(-0.45, 0.0), (0.45, 0.0)])
    isl = put(R, B, "labbench_island_reagent_bench", -7.2, 11.0, 0.0)
    if isl:
        tops(R, B, isl, ["analyzer_spectrometer", "analyzer_centrifuge"], [(-0.5, 0.0), (0.5, 0.0)])
    put(R, B, "seat_science_stool", -8.2, 12.2, 180.0)
    put(R, B, "seat_science_stool", -6.2, 12.2, 180.0)
    put(R, B, "engtool_chain_hoist_gantry", -11.0, 9.9, 0.0)

    R.line("Dirty trades (south wall)",
           "Parts washer, welding rig with its gas rack and the paint-booth screen are on the south wall together, under one extraction duct, "
           "so fumes, solvent and sparks are away from the 3D printers and the paper-and-screen design corner.")
    wall_row(R, B, "S", ["hangartool_parts_washer", "engtool_welding_rig", "barrel_gas_cylinder_rack", "hangartool_paint_booth_screen"],
             -11.9, gap=0.08)
    wall_y(R, B, "S", "safety_fire_blanket_box", -3.0, 1.4)
    wall_run(R, B, "S", "duct_rectangular_duct_run", -12.0, -3.2, 3.0)

    R.line("Design corner (east wall, south of the door)",
           "The designer works at a computer desk and a drafting table in the south-east corner, with a holographic projector to review a part in "
           "3D before it is printed and a schematics wall to pin the drawings; it is beside the door so engineers from other decks can drop in.")
    desk_station(R, B, "E", "desk_computer_desk", 13.1)
    dt = aw(R, B, "E", "desk_drafting_table", 11.6)
    seat_for(R, B, dt, "seat_science_stool")
    put(R, B, "holo_ship_schematic_projector", -2.4, 9.85, -90.0)
    wall_y(R, B, "E", "display_schematics_wall", 12.4, bottom=1.75, check=False)

    R.line("Tool chests and parts wall (east wall, north of the door)",
           "Roll-around tool chests hold the hand tools; the parts wall above them holds the small parts and fixings that are used every day, "
           "so a machinist does not walk to the depot for a screw.")
    aw(R, B, "E", "storagebin_toolchest_wheels", 4.4)
    wall_y(R, B, "E", "shelving_parts_bin_wall", 4.9, 2.2)
    wall_y(R, B, "N", "engtool_tool_rack", -2.4, 1.9)

    R.line("Pallet jack and tool cart",
           "The hand pallet jack stands at the end of the rack aisle and a tool cart by the islands, so a machinist reaches tools "
           "and stock without crossing the hall.")
    put(R, B, "loader_hand_pallet_jack", -5.0, 6.3, 0.0)
    put(R, B, "hangartool_tool_cart", -5.4, 9.5, 0.0)

    R.line("Overhead extraction, services and trays",
           "Cable trays and compressed-air pipes run overhead from the south-wall trunk to each machine; the extraction duct above the dirty "
           "trades leaves through the hull riser.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, -12.0, 5.4, "x")
    ceil_run(R, B, ["pipe_ceiling_hanger_run"] * 4, -12.0, 8.8, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, -12.0, 12.6, "x")

    R.line("Safety and signs",
           "Eye wash by the dirty trades, extinguishers by the door and the welder, a first-aid cabinet, floor stencils for the aisles and an "
           "exit sign over the door.")
    sign_at(R, B, "E", "sign_emergency_exit", 7.3, 2.9)
    sign_at(R, B, "E", "sign_dept_engineering", 9.8, 2.9)
    wall_y(R, B, "D0", "safety_eye_wash_station", 1.0, 1.1)
    fe(R, B, "E", 8.95)
    fe(R, B, "S", -12.4)
    wall_y(R, B, "E", "safety_first_aid_cabinet", 9.5, 1.3)
    for x in (-10.0, -7.0):
        mark(R, B, x, 5.8, 0.0)
    for x, z in ((-9.0, 6.4), (-5.5, 6.4), (-9.0, 12.0), (-5.0, 10.0)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)
    R.place(mm(B, "camera_dome_ceiling"), -6.0, 8.0, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- AUXILIARY CONTROL
def f_auxctl(R, B):
    R.describe(
        "Auxiliary Control is the backup bridge and damage-control centre: if the main bridge is lost, the ship can be flown, fought and "
        "repaired from here, and in any damage emergency the damage-control officer coordinates repair parties from this room.",
        basis="Eight stations in two staggered rows face a 5.6 m status display wall on the hull side (viewing distance 3 to 6 m, which is the "
              "comfortable range for a 5.6 m display): helm, operations, tactical and damage control in the front row, sensors, communications, "
              "shields and engineering in the back row; 0.9 m between the rows, the duty officer's chair and podium behind them on the "
              "door axis, a holographic table for damage-control planning, and a 2.4 m clear approach from the door. The room runs "
              "4 hours on its own battery racks; the lockers hold breach kits and emergency suits for 8 people (the full watch).",
        crew=8,
        adjacency="Aft spine corridor (west door); Fabrication Hall across the corridor; Drone & Probe Bay directly south; "
                  "the bridge is three decks above, joined by the stair towers and a hardened data trunk.",
        notes="Sparse and military: no decoration, everything the watch needs within reach of the chairs, red-alert lighting on a separate circuit.")
    R.line("Ceiling lighting", "Dimmable cool-white panels at 3.4 m pitch (200 lux, so the screens stay readable); a separate red-alert circuit "
           "overrides them.")
    lights(R, spacing=3.4, color="#dbe6ff", energy=1.3)
    R.omni(12.0, 1.7, 7.8, "#40c8ff", 1.8, 8.0)

    R.line("Status display wall (east hull wall)",
           "A 5.6 m main viewscreen shows the ship's status, tactical picture and damage plan; flanking screens carry the power board and the "
           "engineering summary. They are on the hull wall so every station faces them and no console has its back to the screen.")
    wall_y(R, B, "E", "display_main_viewscreen", 8.1, 1.7, check=False)
    wall_y(R, B, "E", "display_status_board", 4.45, 1.6, check=False)
    wall_y(R, B, "E", "display_tall_readout", 11.5, 1.7, check=False)

    TOPS = ["terminal_keyboard", "terminal_laptop_console", "terminal_desk_terminal", "terminal_headset_dock"] * 2
    R.line("Front row stations: helm, operations, tactical, damage control",
           "The front row is the 'flying and fighting' row: helm and operations steer and run the ship, tactical handles defence, and damage control "
           "tracks every breach and fire. They sit 3.5 m from the screen wall; consoles face west so operators sit with the screen ahead of them.")
    for mid, z in (("console_helm", 5.35), ("console_ops", 7.5), ("console_tactical", 9.7), ("console_damage_control", 11.6)):
        con = put(R, B, mid, 11.3, z, -90.0)
        seat_for(R, B, con, "seat_tactical_chair" if "tactical" in mid else "seat_ops_chair")
        if con:
            tops(R, B, con, [TOPS.pop(0)], [(0.0, 0.15)])

    R.line("Back row stations: sensors, communications, shields, engineering",
           "The back row supports the front row: sensors build the picture, communications keeps the link to the fleet and the main bridge, "
           "shield control balances the defences and engineering shows the power state; each seat sees the screen over the front row.")
    for mid, z in (("console_sensor", 5.35), ("console_communications", 7.2), ("console_shield_control", 9.2), ("console_engineering_status", 11.1)):
        con = put(R, B, mid, 8.6, z, -90.0)
        seat_for(R, B, con, "seat_comms_chair" if "communications" in mid else "seat_ops_chair")
        if con:
            tops(R, B, con, [TOPS.pop(0)], [(0.0, 0.15)])

    R.line("Duty officer's chair and podium (door axis)",
           "The duty officer sits on the door axis, behind the back row and one step higher in view: from the command chair every station and the "
           "screen wall are in sight, and the podium in front holds the command authentication key and the ship-wide intercom.")
    put(R, B, "console_captain_podium", 7.05, 8.1, -90.0)
    put(R, B, "seat_captain_command_chair", 6.1, 8.1, 90.0)

    R.line("Damage-control holographic table",
           "A holographic table shows the ship's decks in 3D with every breach, fire and repair team marked; the damage-control officer and the "
           "duty officer plan repairs around it standing, as on a military command post.")
    put(R, B, "holo_briefing_table", 4.6, 10.4, 0.0)

    R.line("Emergency gear lockers (north wall)",
           "Damage-control lockers hold breach-repair kits, patches and torches; gear lockers and suit racks hold emergency suits, oxygen packs and "
           "gloves for the whole watch of 8, so in a decompression everyone can suit up without leaving their post.")
    wall_row(R, B, "N", ["safety_damage_control_locker", "locker_gear_locker_keypad", "safety_damage_control_locker",
                          "suitrack_glove_boot_locker", "suitrack_oxygen_pack_rack"], 4.2, gap=0.06)
    wall_y(R, B, "N", "suitrack_eva_helmet_rack", 9.2, 2.65)
    wall_y(R, B, "N", "safety_breach_repair_kit", 5.0, 2.4)
    wall_y(R, B, "W", "safety_defibrillator_station", 12.6, 1.4)
    wall_y(R, B, "N", "display_deck_plan_board", 11.9, 1.9)

    R.line("Communications and data cabinets (west wall, south of the door)",
           "Radio, network and armoured data racks give the room its own link to the fleet and a copy of the ship's critical data, independent of "
           "the main bridge and the computer core; they stand together on the west wall so one cable trunk serves them.")
    wall_row(R, B, "W", ["commsunit_radio_rack", "rack_armored_data_rack", "rack_network_switch_rack", "rack_ups_battery_rack"], 9.3, gap=0.06)
    wall_y(R, B, "W", "commsunit_intercom_panel", 8.9, 1.5, check=False)

    R.line("Backup power and command safe (south wall)",
           "Two battery racks keep the room alive for 4 hours without ship power; the secure data safe holds the command authentication keys "
           "and the ship's log of record, opened only by two officers.")
    wall_row(R, B, "S", ["capacitor_battery_rack", "capacitor_battery_rack", "storage_secure_data_safe", "cabinet_utility_cabinet"], 6.5, gap=0.08)

    R.line("Watch refreshment (south wall, west)",
           "A water cooler and coffee machine are for the long watches: crew who must stay alert for 8 hours need water and coffee at hand, "
           "so nobody leaves their post; a refrigerator holds rations.")
    wall_row(R, B, "S", ["galley_water_cooler", "galley_coffee_machine", "galley_refrigerator"], 2.4, gap=0.06)

    R.line("Alert lights, signs and overhead services",
           "A rotating beacon and the red-alert unit change the room to red alert, signs mark the exits and the lockers, and cable trays "
           "carry the console data from the floor trunk to the racks.")
    wall_y(R, B, "W", "warnlight_red_alert_wall_unit", 6.4, bottom=2.9, check=False)
    wall_y(R, B, "N", "beacon_rotating_beacon", 3.5, 2.7)
    sign_at(R, B, "W", "sign_emergency_exit", 7.3, 2.9)
    sign_at(R, B, "W", "sign_dept_bridge", 9.9, 2.9)
    fe(R, B, "W", 5.1)
    fe(R, B, "S", 12.0)
    wall_y(R, B, "W", "safety_first_aid_cabinet", 4.1, 1.3)
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 4.0, 4.7, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 4.0, 13.0, "x")
    for x, z in ((6.0, 6.0), (6.0, 11.0), (10.0, 8.2)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)
    R.place(mm(B, "camera_dome_ceiling"), 6.5, 8.2, 0.0, y=R.y + R.h)


# ----------------------------------------------------------------------------------------------- MAIN CARGO HOLD
def f_hold(R, B):
    R.describe(
        "The Main Cargo Hold is the keel-deck freight space: pallets, crates and containers of everything the ship carries that is not "
        "food (provisions have their own hold), spare equipment, trade goods and mission cargo, stored in marked bays and moved by forklift "
        "and cargo loader between the corridor opening and the bays.",
        basis="One 3.2 m wide main lane runs from the corridor opening along the axis of the hold; two storage zones lie either side of it. "
              "North zone: low-bay pallet racking on the north wall, a 1.5 m forklift aisle, then a double row of pallets (1.2 x 1.0 m "
              "bays); south zone: a row of crates, a 1.5 m aisle and a hazardous-goods bay on the hull side, and a 20 ft container "
              "on the starboard wall. Capacity: about 25 pallet positions plus the racking and a 20 ft container (about 25 t), roughly one year of "
              "consumables for the deck crew. The loading console sits at the opening so the cargo clerk sees every movement.",
        crew=3,
        adjacency="Aft spine corridor through a 3.2 m opening (east side, forklift width); Fabrication Hall directly north; "
                  "the stern is the keel hull - there is no hull opening on this deck, freight goes up by the stair towers' freight lift trunk.",
        notes="Ceiling 3.4 m: racking is the 3.2 m low-bay type; the tallest pallet stands 2.1 m, so lights and sprinklers clear every load.")
    R.line("Ceiling lighting", "Bright panels (300 lux) on a 3.6 m grid light the lanes and bay labels; fixtures sit over the lanes so no load shadows a label.")
    lights(R, spacing=3.6, color="#f4f4ff", energy=1.6)
    R.keep_clear((-8.6, 20.4, -2.5, 23.6), "3.2 m main forklift lane from the corridor opening into the hold")

    R.line("Low-bay pallet racking (north wall)",
           "The slow-moving stock stands on three low-bay racks on the north wall, out of the traffic lanes and furthest from the door; the "
           "fast-moving stock is on the floor bays nearer the lane. The racks are 1.2 m deep with a 1.5 m forklift aisle in front.")
    wall_row(R, B, "N", ["pallet_rack_bay_low_wire"] * 3, -12.3, gap=0.1)

    R.line("Pallet bays: row A (north zone)",
           "Five different unit loads stand in marked 1.3 m bays: boxes, banded crates, drums, mixed goods and sacks; each "
           "pallet is turned so its label faces the 1.5 m forklift aisle on the racking side.")
    line_x(R, B, ["pallet_boxes_layered", "pallet_crates_banded", "pallet_drums_banded", "pallet_mixed_goods", "pallet_sacks_stacked"],
           -11.3, 17.45, 0.0, gap=0.1)

    R.line("Pallet bays: row B (north zone, lane side)",
           "A second row of tall wrapped loads, a roll cage, a caged crate and a wooden crate is next to the main lane, for the loads that are moved "
           "most often; it touches row A (they are handled as one double row from the lane side).")
    line_x(R, B, ["pallet_wrapped_tall_mixed", "crate_wood_slat_12", "pallet_roll_cage_loaded", "crate_cage_large", "pallet_wrapped_stack"],
           -11.3, 18.75, 0.0, gap=0.2)

    R.line("Hazardous goods bay (south zone, hull side)",
           "Flammable, toxic and biohazard crates and drums stand together in a row on the hull side of the lane, furthest from the door and the "
           "console, behind a safety barrier, with a spill kit and signs so a leak is contained and nobody enters by mistake.")
    line_x(R, B, ["crate_flammable_red", "crate_biohazard", "crate_hazard_yellow", "barrel_chemical_drum_hazard", "barrel_toxic_drums_sump"],
           -9.4, 24.55, 0.0, gap=0.12)
    put(R, B, "safety_spill_kit_bin", -8.9, 26.2, 0.0)
    put(R, B, "hangartool_safety_barrier", -6.8, 25.7, 0.0)
    wall_y(R, B, "D2", "sign_hazard_biohazard", 1.5, 2.6, check=False)
    wall_y(R, B, "D1", "sign_no_entry", 1.5, 2.4, check=False)

    R.line("20 ft container (stern wall)",
           "A standard blue 20 ft container is parked along the stern wall as a bulk store for mixed ship's stores; it is the last-in, "
           "first-out space and its doors face the aisle so it can be unloaded by the forklift.")
    put(R, B, "crate_iso_container_blue", -4.85, 28.55, 90.0)

    R.line("Shelving cage and fuel shelf",
           "Caged lockers hold the valuable and pilferable items (electronics, medicine stock, tools), the gas and fuel shelf holds small gas "
           "and fuel containers away from the floor; the cage stands on the hull side of the pallet rows and the shelf on the starboard wall, both out of the lane.")
    put(R, B, "shelving_cage_lockers", -11.8, 16.9, 90.0)
    aw(R, B, "E", "shelving_gas_and_fuel_shelf", 25.4)

    R.line("Loaders: forklift and pallet jacks (east wall, north of the opening)",
           "The platform forklift and a hover pallet jack park nose-out along the east wall north of the opening, where they can "
           "turn straight into the lane; they stand clear of the 3.2 m opening.")
    put(R, B, "loader_platform_forklift", -2.4, 18.55, 180.0)
    put(R, B, "loader_hover_pallet_jack", -10.6, 20.35, 0.0)

    R.line("Cargo tug (west end of the lane)",
           "A cargo tug docks at the west end of the lane: it shuttles loads between the bays and the lift trunk, so the forklift is free for the heavy pallets.")
    put(R, B, "loader_cargo_tug", -9.5, 22.4, 0.0)

    R.line("Loading console and manifest desk (east wall, north)",
           "The cargo clerk logs every load and assigns bays at a console beside the opening: from the seat the lane, the pallet rows and "
           "the corridor are in view; the display above the console shows the bay plan with free positions.")
    con = aw(R, B, "E", "console_compact_aux", 15.3)
    seat_for(R, B, con, "seat_ops_chair")
    wall_y(R, B, "E", "display_status_board", 15.3, bottom=2.0, check=False)

    R.line("Lane markings and barriers",
           "Floor stencils mark the main lane and a barrier marks the pedestrian crossing to the console: "
           "the rule is that no cargo stands in the lane, ever.")
    for x in (-8.0, -5.5, -3.5):
        mark(R, B, x, 22.0, 0.0)

    R.line("Cable trays, pipes and ceiling sprinklers",
           "Sprinkler lines and cable trays run along the lanes overhead; sprinkler heads protect each bay.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 3, -9.0, 19.9, "x")
    ceil_run(R, B, ["pipe_ceiling_hanger_run"] * 3, -9.0, 25.8, "x")
    for x, z in ((-10.0, 16.0), (-6.0, 16.0), (-10.0, 24.0), (-6.0, 26.5), (-3.5, 17.0)):
        R.place(mm(B, "safety_sprinkler_head"), x, z, 0.0, y=R.y + R.h)

    R.line("Safety and signs",
           "Extinguishers at the opening and the racks, a first-aid cabinet by the console, exit sign beside the opening and the department sign: "
           "the usual marks of a freight space.")
    fe(R, B, "E", 27.0, y=1.5)
    fe(R, B, "N", -3.3, y=1.5)
    wall_y(R, B, "N", "safety_first_aid_cabinet", -2.4, 1.5)
    sign_at(R, B, "E", "sign_emergency_exit", 19.7, 2.9)
    sign_at(R, B, "E", "sign_dept_cargo", 25.2, 2.9)
