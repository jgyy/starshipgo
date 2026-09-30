"""Room recipes - Deck 3 (Engineering deck, y = 0 m)."""
from dressing import *   # noqa: F401,F403
from recipes_deck3_helpers import *   # noqa: F401,F403


# ----------------------------------------------------------------------------------------------- LIFE SUPPORT
def f_life(R, B):
    R.describe(
        "Life Support keeps the ship breathable: it strips CO2 and trace contaminants from the cabin air, re-balances oxygen, "
        "and reclaims and polishes every litre of waste and condensate water.",
        basis="Processing units stand against the walls in trains that follow the process flow (air: scrubber, filter; "
              "water: recycler, osmosis, purifier, storage); 0.9 m service aisles behind the units and a clear working floor "
              "in the middle so filter cassettes can be rolled out and swapped; bottled gas is racked on the bow facets away from the door.",
        crew=2,
        adjacency="Forward spine corridor by the east door; shares the south bulkhead with the Computer Core; "
                  "hydroponics is one deck above.",
        notes="Wedge-shaped bow compartment: the hull facets carry gas racks, storage and the monitoring station.")
    R.line("Ceiling lighting", "Flush troffers give the 300 lux needed to read gauges and label plates; they sit over the service aisles, not over the units.")
    lights(R, spacing=3.6, color="#f4f8ff")

    R.line("CO2 scrubbers (east wall, north of the door)",
           "Cabin air returns down the forward trunk and is scrubbed first, so the amine scrubber and the CO2 tower stand on the east wall "
           "next to the corridor trunk. They use the north half of the wall, where the wedge still leaves a 1.4 m aisle in front.")
    wall_row(R, B, "E", ["scrubber_twin_amine_scrubber", "scrubber_co2_scrubber_tower"], -20.55, dirn=-1)

    R.line("Filter bank (east wall, south of the door)",
           "The particulate filter rack follows the scrubbers in the air path; its 1.9 m front faces the open floor so cassettes roll out "
           "straight onto a cart, and the wall beside the door stays free for the extinguisher and the exit sign.")
    wall_row(R, B, "E", ["scrubber_filter_bank_rack"], -14.55, dirn=-1)

    R.line("Water reclamation train (south wall)",
           "Recycler, condensate collector, reverse-osmosis skid, UV purifier and grey-water processor stand in process order along the "
           "south wall so piping between them is short and one operator can walk the whole train on a single service aisle.")
    wall_row(R, B, "S", ["watertank_water_recycler", "watertank_condensate_collector", "watertank_reverse_osmosis_skid",
                          "watertank_uv_water_purifier", "watertank_greywater_processor"], -2.0, dirn=-1)

    R.line("Monitoring station (south-west facet)",
           "The life-support engineer watches pressure, oxygen and water quality from a console on the south-west facet; from the chair the "
           "whole water train and the door are in view, and the console backs onto the hull where nobody needs to walk.")
    con = aw(R, B, "D0", "console_environmental", 1.2)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.12)])

    R.line("Potable storage and air processing (west facets)",
           "The potable tank is a tall heavy vessel, so it sits on a hull facet where the floor load is best; the atmosphere processor "
           "(Sabatier / O2 recovery) next to it closes the air loop. Fronts face the centre for a clear service circle.")
    wall_row(R, B, "D1", ["watertank_potable_water_tank"], 0.42)
    wall_row(R, B, "D2", ["scrubber_atmosphere_processor"], 0.35)

    R.line("Oxygen and cryogenic gas store (north facets)",
           "Oxygen cylinders feed the ship's O2 balance. They are racked together on the bow facets, furthest from the door, "
           "so a leak never blocks the escape route; cylinders stand in a rack, never free-standing.")
    aw(R, B, "D3", "cylinder_oxygen_cylinder_rack", 1.25)

    R.line("Filter staging cart",
           "Spent cassettes come out of the banks onto a service cart and go to the recycler; the cart stays in the open floor in front of the filter rack.")
    put(R, B, "engtool_diagnostic_cart", -3.9, -15.3, 90.0)
    put(R, B, "cylinder_cylinder_hand_cart", -4.6, -17.7, 0.0)

    R.line("Overhead ducts and pipework",
           "Return-air duct along the south wall and water lines overhead run parallel to the walls, dropping to each unit, so the floor stays free.")
    wall_run(R, B, "S", "duct_rectangular_duct_run", -9.8, -2.0, 3.05)
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 3, -9.0, -15.4, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 3, -7.2, -17.6, "x")

    R.line("Wall instrumentation",
           "A status board on the south-west facet repeats the console readings for anyone at the gas store; the return-air "
           "duct above the water train runs the length of the south wall.")
    wall_y(R, B, "D5", "display_status_board", 0.86, 2.35)

    R.line("Safety and signs",
           "Fire extinguisher at the north end, eye wash by the amine scrubber (amine is corrosive), "
           "low-oxygen sign at the gas store and exit sign over the door.")
    fe(R, B, "N", -2.0)
    wall_y(R, B, "D4", "safety_eye_wash_station", 0.4, 1.1)
    wall_y(R, B, "E", "sign_emergency_exit", -19.0, 2.9, check=False)
    wall_y(R, B, "D3", "sign_hazard_low_oxygen", 1.25, 2.6, check=False)


# ----------------------------------------------------------------------------------------------- COMPUTER CORE
def f_core(R, B):
    R.describe(
        "The Computer Core hosts the ship's main computer, data archives and network backbone; it is an unmanned machine hall "
        "visited by one systems administrator.",
        basis="Racks are 0.6 m units in straight rows on a hot/cold aisle plan: fronts face each other across 1.3-1.4 m cold aisles, "
              "backs face 1.2-1.5 m service aisles; a 2.8 m cross aisle follows the door axis. Liquid cooling, UPS banks and "
              "gas fire suppression are sized to the rack count. No ordinary furniture: one admin console and a tool cabinet.",
        crew=1,
        adjacency="Forward spine corridor (east door); Life Support north across the bulkhead; Bridge and comms decks above "
                  "connect by data trunk through the north-east riser.",
        notes="Cold aisles run east-west; the floor is hull panel with cable covers.")
    R.line("Ceiling lighting", "Cool-white panels over the aisles give 400 lux at the rack fronts; fixtures sit above the aisles so they never shadow a rack label.")
    lights(R, spacing=3.2, color="#e6eeff", energy=1.5)

    R.line("Compute pod, north rows (blade servers, GPU clusters, quantum racks)",
           "Two facing rows of 0.6 m racks form the main compute pod: fronts face each other across a 1.35 m cold aisle, backs face the "
           "north wall and the hot service aisle. A liquid-cooled cabinet every fifth position takes the densest GPU loads.")
    rowA = ["rack_network_switch_rack", "rack_blade_server_rack", "rack_blade_server_rack", "rack_blade_server_rack",
            "rack_liquid_cooled_cabinet", "rack_blade_server_rack", "rack_blade_server_rack", "rack_blade_server_rack",
            "rack_network_switch_rack"]
    rowB = ["rack_network_switch_rack", "rack_gpu_cluster_rack", "rack_gpu_cluster_rack", "rack_gpu_cluster_rack",
            "rack_liquid_cooled_cabinet", "rack_gpu_cluster_rack", "rack_gpu_cluster_rack", "rack_cryogenic_quantum_rack",
            "rack_cryogenic_quantum_rack", "rack_liquid_cooled_cabinet", "rack_network_switch_rack"]
    wall_row(R, B, "N", rowA, -10.4, gap=0.02, item_gap=0.02)
    line_x(R, B, rowB, -11.4, -9.9, 180.0, gap=0.02)
    R.keep_clear((-11.4, -11.68, -4.4, -10.42), "cold aisle 1.26 m between the facing compute rows")

    R.line("Storage pod, south rows (arrays and archive towers)",
           "Bulk storage arrays (row nearest the cross aisle) and the crystal / tape archive towers (against the south wall) face each other across "
           "a cold aisle; archive towers are the slowest-changing kit so they sit furthest from the door, where nobody walks past them.")
    rowD = ["rack_storage_array"] * 5 + ["rack_photonic_fiber_rack"] + ["rack_storage_array"] * 4 + ["rack_network_switch_rack"]
    rowC = ["rack_crystal_archive_tower"] * 4 + ["rack_tape_archive_tower"] * 3 + ["storage_memory_core_column",
            "rack_crystal_archive_tower", "rack_tape_archive_tower"]
    line_x(R, B, rowD, -10.9, -3.0, 0.0, gap=0.02)
    wall_row(R, B, "S", rowC, -10.9, gap=0.03, item_gap=0.02)

    R.line("Cooling plant (west wall)",
           "A shell-and-tube heat exchanger and circulation pump take the heat of the liquid-cooled cabinets to the ship's coolant loop; "
           "they stand on the west wall near the loop riser, away from the electronics and with the drain at floor level.")
    aw(R, B, "W", "tank_shell_and_tube_heat_exchanger", -2.65)
    aw(R, B, "S", "tank_circulation_pump", -12.1)

    R.line("UPS battery banks (east wall, north of the door)",
           "The core must ride through a power dip, so three battery racks stand on the east wall, near the power riser and out of the "
           "cold aisles; their 1.25 m fronts face the cross aisle.")
    wall_row(R, B, "E", ["capacitor_battery_rack", "capacitor_battery_rack", "capacitor_battery_rack"], -12.6)
    wall_y(R, B, "E", "sign_hazard_high_voltage", -9.0, 2.3)

    R.line("Administrator console (south-east corner)",
           "One engineering-status console and chair give the administrator a place to check load, temperature and alarms. It stands by the door "
           "end so the whole cross aisle and both cold aisles are in view.")
    con = aw(R, B, "E", "console_engineering_status", -2.6)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.12)])
    aw(R, B, "S", "cabinet_utility_cabinet", -2.3)

    R.line("Gas fire suppression",
           "Water would destroy the racks, so an inert-gas accumulator tank pair stands on the north wall with nozzles in the ceiling over "
           "each aisle; a pre-discharge beacon and abort switch hang by the door.")
    aw(R, B, "N", "tank_accumulator_tank", -3.8)
    aw(R, B, "N", "tank_accumulator_tank", -2.8)
    for x, z in ((-8.0, -11.0), (-5.6, -11.0), (-8.0, -2.0), (-5.6, -2.0), (-3.0, -6.5)):
        R.place(mm(B, "safety_suppression_nozzle"), x, z, 0.0, y=R.y + R.h)
    wall_y(R, B, "E", "warnlight_red_alert_wall_unit", -8.6, bottom=2.7)
    wall_y(R, B, "E", "controlpanel_emergency_stop", -7.3 if False else -8.15, 1.3, check=False)

    R.line("Network backbone and cable trays",
           "Patch panels over the north rack row and wall network cabinets on the west wall terminate the fibre trunks; ladder trays "
           "above every row carry power and data so nothing runs on the floor.")
    for x in (-9.0, -6.6):
        wall_y(R, B, "N", "router_patch_panel", x, bottom=2.3)
    wall_y(R, B, "W", "router_wall_network_cabinet", -4.6, 1.6)
    wall_y(R, B, "W", "router_fiber_junction_box", -2.6, 2.4)
    for z in (-11.05, -9.0, -1.9):
        ceil_run(R, B, ["cabletray_ladder_tray"] * 4, -11.0, z, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, -11.0, -6.5, "x")

    R.line("Safety and signs",
           "CO2 / halon discharge warning and an extinguisher at the door, exit sign above it, evacuation map beside it.")
    fe(R, B, "E", -4.95)
    wall_y(R, B, "E", "sign_emergency_exit", -6.5, 2.9, check=False)
    wall_y(R, B, "E", "safety_evac_route_map", -4.0, 2.3)


# ----------------------------------------------------------------------------------------------- MAIN ENGINEERING
def f_eng(R, B):
    R.describe(
        "Main Engineering is the ship's power house: the fusion reactor, its magnetic coils and capacitor banks, the turbine and "
        "generator sets and the control stations from which the duty engineers run them.",
        basis="The reactor stands inside a guard rail with 1.5 m service aisles on all four sides; the control stations face it from the "
              "west with the operator's back to the door side; coil and capacitor banks line the forward (north) and outboard (east) "
              "walls where the plasma conduits leave the reactor; rotating plant sits along the south wall; 1.2 m aisles behind every bank.",
        crew=3,
        adjacency="Forward spine corridor by the west door; Computer Core to the north-west; Power Distribution is aft across the "
                  "corridor; the plasma trunk rises through the north-east corner to the deflector and impulse systems.",
        notes="The door axis looks straight at the reactor: anyone entering sees the core and the status consoles at once.")
    R.line("Ceiling lighting", "High-output panels at 3.6 m pitch light the aisles evenly; the blue-white colour matches the reactor glow and keeps status lamps legible.")
    lights(R, spacing=3.6, color="#dfeaff", energy=1.7)

    RX, RZ = 8.0, -6.3
    R.line("Fusion reactor core",
           "The fusion core is the heart of the room and sits at its middle, so its magnetic coils, conduits and shielding are equidistant "
           "from every bank and the plant can be serviced from all four sides. It is 3.0 m tall and fits under the 3.4 m ceiling with "
           "room for the overhead trays.")
    put(R, B, "reactor_fusion_core_reactor", RX, RZ, 0.0)
    R.omni(RX, 1.4, RZ, "#66ccff", 1.8, 9.0)

    R.line("Reactor guard rail",
           "A 4.2 m square railing keeps people 0.85 m away from the shielded vessel and marks the exclusion zone; the only opening is a 2.1 m service "
           "gate on the west side, facing the entry approach and the consoles, which stays shut while the plant is live.")
    for x in (RX - 1.05, RX + 1.05):
        put(R, B, "railing_guard_balusters", x, RZ - 2.26, 0.0)
        put(R, B, "railing_guard_balusters", x, RZ + 2.26, 0.0)
    put(R, B, "railing_guard_balusters", RX - 2.1, RZ + 1.05, 90.0)      # west side: one panel, the other 2.1 m is the service gate
    for z in (RZ - 1.05, RZ + 1.05):
        put(R, B, "railing_guard_balusters", RX + 2.1, z, 90.0)
    R.keep_clear((3.55, RZ - 1.0, 5.75, RZ + 1.0), "entry approach: the door axis looks straight at the reactor, keep it open")

    R.line("Reactor control pillar",
           "The reactor's local control pillar (scram, coil current, containment readouts) stands just outside the rail at its south-west "
           "corner of the entry approach so an engineer can reach it from the consoles and still see the vessel.")
    put(R, B, "reactor_reactor_control_pillar", 5.0, -8.05, 0.0)

    R.line("Engineering status consoles",
           "Three consoles in two groups face west with operators' seats behind them, so the crew watch both their screens and the reactor "
           "beyond. The groups are split to leave the 3.5 m wide entry approach between them; consoles stand 1.5 m clear of the rail.")
    cx = RX - 2.1 - 1.5 - 0.43
    for mid, z in (("console_engineering_status", -10.35), ("console_damage_control", -8.45), ("console_engineering_status", -2.6)):
        con = put(R, B, mid, cx, z, -90.0)
        seat_for(R, B, con, "seat_ops_chair")
        if con and mid == "console_engineering_status":
            tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.15)])

    R.line("Plasma and warp coils (forward wall)",
           "The plasma leaves the reactor on the forward side, so the injector and warp coils stand on the north wall in the order of the "
           "plasma path, each with its discharge tower beside it; the row keeps a 1.2 m service aisle.")
    wall_row(R, B, "N", ["coil_warp_coil_stack", "coil_helical_plasma_coil", "coil_plasma_manifold", "coil_helical_plasma_coil",
                          "coil_warp_coil_stack"], 3.9, gap=0.08)

    R.line("Capacitor banks (outboard wall)",
           "Energy-storage banks stand on the east wall next to the plasma trunk so the discharge cables stay short; three racks give "
           "the buffer for one jump pulse and the aisle behind them is the maintenance walk.")
    wall_row(R, B, "E", ["capacitor_capacitor_bank_rack", "capacitor_marx_bank", "capacitor_capacitor_bank_rack"], -0.9, dirn=-1, gap=0.1)

    R.line("Coolant and heat rejection (north-east facets)",
           "Buffer and condenser tanks with the coolant pump take heat off the coils and the turbine loop; they stand on the outboard hull facets, "
           "closest to the radiator trunk.")
    aw(R, B, "D4", "generator_inverter_cabinet", 0.95)
    aw(R, B, "D3", "tank_buffer_tank_with_level_tube", 0.97)
    aw(R, B, "D2", "tank_condenser", 1.0)
    aw(R, B, "D1", "tank_circulation_pump", 1.05)

    R.line("Turbines and generators (south wall)",
           "The steam-loop turbine, motor-generator and flywheel convert and smooth the reactor output; rotating plant is kept on the quiet "
           "south wall, away from the control stations, with a 1.5 m aisle between it and the rail.")
    wall_row(R, B, "S", ["turbine_steam_turbine", "generator_motor_generator_set", "turbine_flywheel"], 5.3, gap=0.1)

    R.line("Tool locker and workstation (south-west)",
           "A tool locker and a rolling toolbox hold the engineers' own kit for quick repairs; they stand by the door end where "
           "tools are taken in and out.")
    aw(R, B, "S", "locker_double_locker_bank", 2.4)
    aw(R, B, "S", "engtool_rolling_toolbox", 3.6)

    R.line("Wall junctions, breakers and displays",
           "Breaker panels and bus-bar risers on the west wall distribute the reactor's auxiliary supply; a schematic board and power board "
           "let the watch see load and coil status at a glance from any seat.")
    wall_y(R, B, "W", "display_schematics_wall", -11.5, 1.9)
    wall_y(R, B, "W", "display_power_board", -9.4, 1.8)
    wall_y(R, B, "W", "junction_breaker_panel", -3.1, 1.5)
    wall_y(R, B, "W", "junction_bus_bar_riser", -2.5, 1.5)
    wall_y(R, B, "N", "junction_meter_panel", 2.9, 1.6)

    R.line("Overhead trays, pipes and ducts",
           "Cable trays leave the reactor head towards the banks, and coolant pipes and a ventilation duct run beside them; all are "
           "overhead so the floor is free for the aisles.")
    for z in (-11.1, -2.6):
        ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 4.0, z, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, 4.0, -12.3, "x")
    ceil_run(R, B, ["pipe_ceiling_flanged_twin"] * 4, 4.0, -1.5, "x")

    R.line("Radiation and fire safety",
           "A radiation shelter panel by the door, eye-wash beside the breaker panels, extinguishers at both ends of the room and radiation / high-voltage "
           "signs on the rail and the coil bank - the usual marks of a power plant.")
    wall_y(R, B, "W", "safety_radiation_shelter_panel", -4.4, 1.3)
    fe(R, B, "W", -0.6)
    fe(R, B, "N", 2.3)
    wall_y(R, B, "W", "safety_eye_wash_station", -1.6, 1.1)
    wall_y(R, B, "N", "sign_hazard_radiation", 7.0, 3.0)
    wall_y(R, B, "E", "sign_hazard_high_voltage", -2.5, 2.6)
    wall_y(R, B, "W", "sign_emergency_exit", -6.5, 2.9, check=False)


# ----------------------------------------------------------------------------------------------- AIRLOCK
def f_airlock(R, B):
    R.describe(
        "The airlock is where crew suit up for EVA and cycle through the hull hatch; it holds the suits, oxygen packs and "
        "decontamination equipment and the interlock controls for the hatch.",
        basis="Flow is one-way: corridor door, suit lockers and bench, decontamination arch, one-person airlock "
              "chamber, hull hatch. Lockers stand on the south wall with a 0.9 m dressing aisle; the approach to the chamber is kept "
              "clear; a console near the inner door cycles the lock. Suits are stored for four EVA crew.",
        crew=4,
        adjacency="Forward spine corridor (west door); Main Engineering is aft across the bulkhead; the outer hatch is in the "
                  "bow tip so EVA teams leave clear of the hangar traffic.",
        notes="Five viewports on the hull facets are left unobstructed so the supervisor can watch the outside; the airlock chamber "
              "is the narrow bow tip, the only part of the hull without a viewport wide enough for a hatch.")
    R.line("Ceiling lighting", "Bright neutral-white panels (500 lux) for suit checks, where a missed seal is a life-safety problem.")
    lights(R, spacing=3.6, color="#f6f6ff", energy=1.5)

    R.line("Outer airlock hatch (bow tip)",
           "The pressure hatch is cut in the bow tip, the only hull wall of the room without a viewport; the hatch wheel and the "
           "red/green state lights either side of it show at a glance whether the outside is safe to open.")
    R.wall_item("N", mm(B, "hatch_oval_pressure"), 2.0, y=1.3)
    wall_y(R, B, "W", "beacon_airlock_status_light", -23.55, bottom=1.2)
    wall_y(R, B, "W", "beacon_rotating_beacon", -23.55, bottom=2.4)
    wall_y(R, B, "D0", "controlpanel_airlock_control", 0.4, bottom=1.1)
    R.omni(2.3, 2.2, -23.0, "#ff5030", 0.8, 3.0)
    R.omni(3.0, 2.4, -19.0, "#40ff80", 0.5, 3.0)

    R.line("Decontamination arch",
           "Every returning EVA crew member walks through the arch to shed dust and radiation contamination before entering the ship; "
           "it stands at the mouth of the chamber so it cannot be bypassed; the red/green lights interlock the hatch with the inner door.")
    put(R, B, "suitrack_decontamination_arch", 2.65, -21.4, 0.0)
    R.keep_clear((1.65, -20.95, 4.2, -19.3), "approach to the decontamination arch and airlock chamber - kept open for suited crew")

    R.line("EVA suit lockers and oxygen packs (south wall)",
           "Wardrobe lockers hold the hard suits, glove/boot lockers the small items, and the oxygen-pack rack charges four packs. "
           "They stand on the south wall in suit-up order so a crew member walks along the row from suit to pack to boots, then north to the arch.")
    wall_row(R, B, "S", ["locker_wardrobe", "locker_wardrobe", "suitrack_glove_boot_locker", "suitrack_oxygen_pack_rack",
                          "suitrack_glove_boot_locker"], 2.3, gap=0.05)

    R.line("Suit-up bench",
           "A padded bench facing the lockers lets two crew sit to pull on boots and seal suits; A 0.9 m aisle is kept between "
           "it and the locker doors.")
    put(R, B, "suitrack_suit_up_bench", 5.0, -15.25, 0.0)

    R.line("Airlock control console and O2 reserve (west wall, south of the door)",
           "The cycle console sits beside the inner door so the EVA supervisor can open and close the pressure door and hatch and read the "
           "chamber pressure. Next to it the reserve oxygen rack has a helmet shelf above it, so a helmet and its air are together.")
    aw(R, B, "W", "console_compact_aux", -16.85)
    aw(R, B, "W", "cylinder_oxygen_cylinder_rack", -15.3)
    wall_y(R, B, "W", "suitrack_eva_helmet_rack", -15.3, 2.2)
    wall_y(R, B, "W", "warnlight_door_state_light", -17.45, 2.0)

    R.line("Tool belts (west wall, north of the door)",
           "Tool belts and tethers hang on the west wall beside the arch, where crew pass them on the way to the chamber.")
    wall_y(R, B, "W", "suitrack_tool_belt_board", -22.6, bottom=0.9)

    R.line("Decontamination shower and first aid (south-east corner)",
           "An emergency shower at the south-east facet serves both decontamination and chemical splashes; the first-aid cabinet and "
           "extinguisher are beside it, in view of the bench.")
    aw(R, B, "W", "safety_emergency_shower", -13.95)
    fe(R, B, "S", 2.0)

    R.line("Overhead services and signs",
           "Air-return duct and cable tray run overhead; an airlock department sign and an emergency-exit sign mark the door and the hatch.")
    wall_run(R, B, "S", "duct_rectangular_duct_run", 2.3, 9.4, 3.05)
    ceil_run(R, B, ["cabletray_ladder_tray"] * 3, 3.5, -18.6, "x")
    wall_y(R, B, "W", "sign_dept_airlock", -19.0, 3.05, check=False)
    wall_y(R, B, "S", "sign_hazard_low_oxygen", 5.0, 2.45, check=False)


# ----------------------------------------------------------------------------------------------- ENGINEERING WORKSHOP
def f_shop(R, B):
    R.describe(
        "The workshop is where engineers repair and fabricate parts for every system on the ship: bench work, welding, "
        "hoisting and parts storage, with a desk for work orders.",
        basis="Stations are grouped by noise and hazard: benches on the quiet north wall, a welding bay with its gas bottles at the "
              "hull end (west), heavy lifting in the open middle, parts storage on the south wall. 1.9 m clear aisles between the "
              "rows, a 2 m main route from the door, and gas is always racked, never loose.",
        crew=4,
        adjacency="Aft spine corridor by the east door; Cargo Bay immediately south (parts come through the corridor); "
                  "Main Engineering across the corridor to the north-east.",
        notes="The welding bay is at the hull wall so fumes go straight into the extraction duct overhead.")
    R.line("Ceiling lighting", "Warm-white panels at 3.3 m pitch give 500 lux for precision work; extra task light comes from the bench tool boards.")
    lights(R, spacing=3.3, color="#fff3e0", energy=1.7)

    R.line("Work benches with vises (north wall)",
           "Three fixed benches along the quiet north wall give one station per engineer; each has its own vise and a tool board above so "
           "a tool is never further than an arm's length. They stand against the wall so the 1.9 m floor in front is free for the work.")
    row = wall_row(R, B, "N", ["engtool_work_bench_with_vise", "engtool_work_bench_with_vise", "hangartool_avionics_bench"], -12.4, gap=0.1)
    for p in row:
        if p:
            tops(R, B, p, ["engtool_hand_tool_set", "toolbox_tabletop_toolbox"], [(-0.4, 0.0), (0.45, 0.0)])
    wall_y(R, B, "N", "engtool_tool_wall_board", -11.5, 1.85)
    wall_y(R, B, "N", "engtool_tool_wall_board", -9.6, 1.85)
    wall_y(R, B, "N", "engtool_tool_rack", -5.2, 1.6)

    R.line("Central work island and hoist",
           "A free-standing bench in the middle takes jobs too big for the wall stations; a chain-hoist gantry beside the south aisle lifts "
           "pumps and engine parts on to it. Both sit off the door axis so the 2 m main route stays open.")
    put(R, B, "engtool_work_bench_with_vise", -9.0, 7.0, 0.0)
    put(R, B, "engtool_rolling_toolbox", -7.5, 7.0, -90.0)
    put(R, B, "engtool_rolling_toolbox", -10.5, 7.0, 90.0)
    put(R, B, "engtool_chain_hoist_gantry", -5.6, 8.9, 0.0)
    put(R, B, "engtool_creeper_board", -11.8, 8.5, 0.0)

    R.line("Welding bay (west wall)",
           "Welding and cutting are at the hull end of the room with the extraction duct overhead; the rig, torch cart and gas racks are "
           "together so the gas hoses are short, and the racks stand against the wall secured, never loose on the floor.")
    wall_row(R, B, "W", ["engtool_welding_rig", "engtool_oxy_torch_cart", "barrel_gas_cylinder_rack",
                          "cylinder_nitrogen_cylinder_trio"], 5.4, gap=0.06)
    wall_y(R, B, "W", "safety_fire_blanket_box", 6.0, 1.8)
    wall_y(R, B, "W", "sign_hazard_high_voltage", 6.9, 2.6, check=False)

    R.line("Parts shelving (south wall)",
           "Bins, pigeonholes and heavy-duty racking hold fasteners, seals and small assemblies; they are on the south wall next to the cargo "
           "bay, and a PPE locker beside them holds gloves, goggles and aprons.")
    wall_row(R, B, "S", ["shelving_parts_bins_rack", "shelving_parts_bins_rack", "shelving_heavy_boxes",
                          "locker_double_locker_bank", "hangartool_air_compressor"], -12.4, gap=0.06)

    R.line("Work-order desk (east wall)",
           "Engineers book jobs and look up procedures at a desk and terminal by the door; the cork board above holds the job cards.")
    desk = aw(R, B, "E", "desk_workstation", 4.85)
    seat_for(R, B, desk, "chair_swivel_office_chair")
    if desk:
        tops(R, B, desk, ["terminal_desk_terminal", "terminal_keyboard"], [(0.0, -0.12), (0.0, 0.17)])
    wall_y(R, B, "E", "noticeboard_cork_bulletin_board", 4.85, 1.75)

    R.line("Safety equipment",
           "Eye wash and extinguishers by the door and at the benches: the two hazards are splashes (degreaser, coolant) and fire (welding).")
    wall_y(R, B, "E", "safety_eye_wash_station", 10.0, 1.1)
    fe(R, B, "E", 9.3)
    fe(R, B, "N", -3.0)
    wall_y(R, B, "S", "safety_first_aid_cabinet", -2.6, 1.3)
    wall_y(R, B, "E", "sign_emergency_exit", 7.3, 2.9, check=False)

    R.line("Overhead extraction, pipes and trays",
           "A fume extraction duct runs over the welding bay and along the benches; compressed-air pipe and a cable tray follow it so outlets can drop "
           "to each station.")
    wall_run(R, B, "N", "duct_rectangular_duct_run", -12.4, -3.6, 3.05)
    wall_run(R, B, "W", "duct_rectangular_duct_run", 5.4, 9.6, 3.05)
    ceil_run(R, B, ["pipe_ceiling_hanger_run"] * 5, -12.4, 9.6, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 5, -12.4, 7.3, "x")


# ----------------------------------------------------------------------------------------------- CARGO BAY
def f_cargo(R, B):
    R.describe(
        "The Cargo Bay receives, sorts and stores freight that arrives through the hangar opening and leaves through the aft corridor "
        "to the depot and the workshop.",
        basis="Freight moves on a cross-shaped forklift route: a 4 m wide N-S lane on the hangar-opening axis and a 2.5 m E-W lane from the "
              "corridor door, both kept clear. Marked pallet bays and racking stand between the lanes and the walls; hazardous goods "
              "are segregated in the hull corner with their own spill kit; bays are 1.25 x 1.05 m to match the pallets.",
        crew=3,
        adjacency="Hangar Bay to the south through a 4 m opening; aft corridor by the east door; Workshop to the north; Spares "
                  "Depot across the corridor.",
        notes="Overhead clearance 3.4 m: racks are the 3.2 m low bay type so the lights and sprinkler lines clear them.")
    R.line("Ceiling lighting", "Bright panels (300 lux) along the lanes so labels and hazard marks can be read at forklift speed.")
    lights(R, spacing=3.4, color="#f4f4ff", energy=1.6)

    R.line("Pallet racking (north wall)",
           "Low-bay racking on the north wall stores pallets three high-ish in the least-used wall space, out of the forklift lanes; "
           "the rack near the door holds the fast-moving items, the west rack the slow stock.")
    R.against_wall("N", mm(B, "pallet_rack_bay_low_wire"), -11.2)
    aw(R, B, "N", "shelving_heavy_boxes", -3.75)

    R.line("Marked pallet bays (west)",
           "Loaded pallets stand in marked 1.25 x 1.05 m bays north-west of the lane, with 0.9 m walking aisle in front of the racking; "
           "each bay has its floor stencil so the forklift driver can see at a glance whether a bay is free.")
    put(R, B, "pallet_crates_banded", -11.9, 13.8, 0.0)
    put(R, B, "pallet_drums_banded", -10.55, 13.8, 0.0)
    put(R, B, "sign_floor_marking", -11.2, 12.85, 0.0)
    wall_y(R, B, "W", "sign_dept_cargo", 12.6, 2.6, check=False)
    R.keep_clear((-9.0, 11.6, -5.0, 17.0), "hangar-opening axis: the 4 m N-S forklift lane must stay open from the hangar to the north wall")

    R.line("Pallet bays (south-west) and boxed stock",
           "A second pair of bays stands against the south wall beside the hangar opening so freight from the hangar is only a few metres "
           "from its first bay; the remaining 4 m of opening is the lane.")
    put(R, B, "pallet_boxes_layered", -11.9, 17.2, 180.0)
    put(R, B, "pallet_wrapped_stack", -10.55, 17.2, 180.0)

    R.line("Forklift and pallet jack (south-east)",
           "The platform forklift is parked next to the door so it is ready for the depot run, nose out; the hand jack covers short "
           "moves inside the bays. Both park clear of the lanes and the door.")
    put(R, B, "loader_platform_forklift", -4.15, 16.4, 180.0)
    put(R, B, "loader_hand_pallet_jack", -9.7, 15.5, 0.0)

    R.line("Cargo console and manifest desk (south-east corner)",
           "The cargo clerk logs every pallet in and out at a console beside the door, where the clerk sees the hangar lane, the door and "
           "the bays; a scanner terminal on the top reads pallet tags.")
    con = aw(R, B, "S", "console_transporter_control", -2.55)
    seat_for(R, B, con, "seat_ops_chair", gap=0.25)
    if con:
        tops(R, B, con, ["terminal_desk_terminal"], [(0.0, 0.0)])

    R.line("Cylinder rack and east-wall shelving",
           "Gas cylinders are chained in a rack by the door where the forklift and the fire party can reach them quickly; parts and "
           "packing materials are on the shelving beside the rack.")
    aw(R, B, "E", "cylinder_oxygen_cylinder_rack", 12.2)

    R.line("Hazardous goods storage (south-west hull)",
           "Chemicals, fuels and biological samples are segregated in the hull corner furthest from the door: hazmat cabinets on the hull wall, "
           "a drum and a spill kit in a taped bay, hazard signs on the walls.")
    aw(R, B, "D0", "safety_hazmat_cabinet", 0.8)
    aw(R, B, "D0", "safety_hazmat_cabinet", 2.1)
    put(R, B, "barrel_chemical_drum_hazard", -11.3, 15.1, 0.0)
    put(R, B, "barrel_chemical_drum_hazard", -10.6, 15.1, 0.0)
    put(R, B, "safety_spill_kit_bin", -11.0, 15.95, 0.0)
    wall_y(R, B, "D0", "sign_hazard_biohazard", 1.45, 2.5, check=False)

    R.line("Safety",
           "Extinguishers at the door and on the north wall, and an eye wash near the hazmat cabinets.")
    fe(R, B, "E", 16.3)
    fe(R, B, "N", -7.0)
    wall_y(R, B, "E", "sign_emergency_exit", 14.5, 2.9, check=False)

    R.line("Overhead services",
           "Sprinkler lines and cable tray run along the lanes overhead.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 5, -12.4, 12.9, "x")
    ceil_run(R, B, ["pipe_ceiling_hanger_run"] * 5, -12.4, 16.0, "x")


# ----------------------------------------------------------------------------------------------- POWER DISTRIBUTION
def f_aux(R, B):
    R.describe(
        "Power Distribution takes the reactor's output, transforms and conditions it, stores the surge in capacitor banks and feeds "
        "the ship's buses; one technician monitors it and does the switching.",
        basis="Equipment stands in parallel rows along the room's length: transformers on the north wall, back-to-back capacitor and "
              "switchgear rows in the middle, rotating generators on the south wall; 1.4 m aisles between rows (1.2 m minimum behind "
              "live equipment), a 1.7 m cross aisle by the door, and a 2.5 m main switching aisle in front of the console.",
        crew=2,
        adjacency="Aft spine corridor by the west door; Main Engineering across the corridor feeds it through the north wall trunk; "
                  "Spares Depot is directly south.",
        notes="Every cabinet is fronted by a painted 1 m safety line in practice; here the aisles are the safety zones.")
    R.line("Ceiling lighting", "Panels over the aisles light the cabinet fronts (300 lux) without reflecting in the meter glass.")
    lights(R, spacing=3.4, color="#f2f4ff", energy=1.6)

    R.line("Transformers and conditioning (north wall)",
           "Step-down transformers, rectifier and inverter cabinets stand on the north wall nearest the trunk from Engineering, in the "
           "order the power flows: distribution cabinet, two pad transformers, regulator, rectifier, inverter, then the discharge coil "
           "that protects the bus against surges. Fronts face the 1.4 m aisle.")
    wall_row(R, B, "N", ["generator_power_distribution_cabinet", "generator_pad_transformer", "generator_pad_transformer",
                          "generator_regulator_tower", "generator_rectifier_cabinet", "generator_inverter_cabinet",
                          "coil_discharge_coil_tower"], 3.8, gap=0.05)

    R.line("Capacitor banks (middle row, north face)",
           "Capacitor and Marx banks buffer the load swings of the ship's systems; they form the north half of the middle double row so a "
           "technician can reach their fronts from the aisle beside the transformers.")
    line_x(R, B, ["capacitor_capacitor_bank_rack", "capacitor_capacitor_bank_rack", "capacitor_capacitor_bank_rack",
                   "capacitor_marx_bank", "capacitor_marx_bank", "capacitor_power_cell_locker"], 5.4, 6.45, 180.0, gap=0.05)

    R.line("Switchgear (middle row, south face)",
           "Switchgear, marshalling and relay cabinets stand back-to-back with the capacitor banks, sharing their cable trench, and face "
           "the main switching aisle where the console is.")
    line_x(R, B, ["junction_switchgear", "junction_switchgear", "junction_marshalling_cabinet", "junction_switchgear",
                   "junction_control_cabinet_with_lights", "junction_relay_cabinet"], 5.4, 7.16, 0.0, gap=0.05)

    R.line("Generator sets (south wall)",
           "The gas turbine genset, diesel standby set, motor-generator and micro-fusion unit give independent supply if the reactor is "
           "down; they are on the south wall, furthest from the delicate controls, with exhaust and fuel service behind the wall.")
    wall_row(R, B, "S", ["generator_gas_turbine_genset", "generator_diesel_genset", "generator_motor_generator_set",
                          "generator_micro_fusion_generator"], 3.9, gap=0.06)

    R.line("Monitoring console (east wall)",
           "The technician watches bus voltages and breaker states from a console at the east end of the main switching aisle, facing the "
           "length of the room, with a chair so a long watch is bearable.")
    con = aw(R, B, "E", "console_engineering_status", 8.7)
    seat_for(R, B, con, "seat_ops_chair")
    if con:
        tops(R, B, con, ["terminal_keyboard"], [(0.0, 0.15)])
    wall_y(R, B, "E", "display_power_board", 6.0, 1.8)
    wall_y(R, B, "E", "coil_wall_coil_bank", 4.45, 1.7)
    wall_y(R, B, "E", "junction_distribution_board", 10.25, 1.6)

    R.line("Tool cabinet and spares (west wall, south of the door)",
           "A utility cabinet and a rolling toolbox hold the insulated tools and fuses needed for switching and repairs, by the door so "
           "tools are checked in and out.")
    aw(R, B, "W", "cabinet_utility_cabinet", 9.35)
    aw(R, B, "W", "engtool_rolling_toolbox", 10.35)

    R.line("Breaker panels and first aid (west wall, north of the door)",
           "Breaker banks and a fuse box sit next to the door for the local supply isolation; a first-aid cabinet is next to them, since electric shock is the room's main injury risk.")
    wall_y(R, B, "W", "controlpanel_breaker_bank", 4.4, 1.5)
    wall_y(R, B, "W", "controlpanel_fuse_box", 3.95, 1.5)

    R.line("Diagnostic cart and spares trolley (main aisle)",
           "A diagnostic cart and a battery trolley are parked in the main aisle, in front of the console, because every inspection and cell swap "
           "starts here; the aisle is 2.5 m so they never block the walk.")
    put(R, B, "engtool_diagnostic_cart", 6.3, 8.6, 0.0)
    put(R, B, "capacitor_battery_trolley", 8.6, 8.6, 0.0)
    R.line("Overhead cable trays and pipes",
           "Power and control cable trays run above the aisles to drop into each cabinet; coolant pipes follow the transformers.")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 4.0, 5.6, "x")
    ceil_run(R, B, ["cabletray_ladder_tray"] * 4, 4.0, 9.0, "x")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 4, 4.0, 4.0, "x")

    R.line("Danger signs and fire protection",
           "High-voltage signs above the transformer and generator rows, extinguishers at both ends of the main aisle and a first-aid "
           "cabinet by the door.")
    for x in (5.5, 9.0):
        wall_y(R, B, "N", "sign_hazard_high_voltage", x, 2.95, check=False)
    wall_y(R, B, "S", "sign_hazard_high_voltage", 7.0, 2.95, check=False)
    fe(R, B, "W", 5.0)
    fe(R, B, "N", 12.75)
    wall_y(R, B, "W", "safety_first_aid_cabinet", 5.55, 1.3)
    wall_y(R, B, "W", "sign_emergency_exit", 7.3, 2.9, check=False)


# ----------------------------------------------------------------------------------------------- SPARES DEPOT
def f_depot(R, B):
    R.describe(
        "The Spares Depot keeps the ship's replacement parts - thruster nozzles, turbines, coils, capacitor cells and "
        "small parts - so any failed unit can be swapped without waiting for a supply run.",
        basis="Everything is in a fixed place: small parts on shelving bays along the north wall, bulky spares on pallets against the "
              "south wall, racking in the middle; 1.2 m aisles between the shelving and the racks, a 1.7 m main aisle from the corridor "
              "door to the hangar door, and the two door swings left open. An inventory desk by the door records every issue and return.",
        crew=2,
        adjacency="Aft spine corridor (west door) and Hangar Bay (south door) - spares go straight to the craft; Power Distribution "
                  "to the north; Cargo Bay across the corridor.",
        notes="Heavy items (nozzles, coils) stand in marked bays with forklift access from the aisle; small spares are palletised.")
    R.line("Ceiling lighting", "Panels over the aisles at 400 lux so part numbers on the shelf labels can be read.")
    lights(R, spacing=3.4, color="#f7f7ff", energy=1.6)

    R.line("Inventory desk and terminal (north-west corner)",
           "Every part issued or returned is logged at the desk beside the door; the terminal holds the stock list and the wall board "
           "shows the critical spares and their minimum stock levels.")
    desk = aw(R, B, "W", "desk_workstation", 12.25)
    seat_for(R, B, desk, "chair_swivel_office_chair")
    if desk:
        tops(R, B, desk, ["terminal_desk_terminal", "terminal_keyboard"], [(0.0, -0.12), (0.0, 0.17)])
    wall_y(R, B, "W", "display_status_board", 12.25, 1.9)

    R.line("Small-parts shelving bays (north wall)",
           "Heavy-box shelving for bulky spares, parts-bin racks for fasteners and seals, pigeonholes for sensors and cage lockers for "
           "valuable parts: five bays in a row along the north wall, each labelled, so a part is always where the list says.")
    wall_row(R, B, "N", ["shelving_heavy_boxes", "shelving_parts_bins_rack", "shelving_pigeonhole", "shelving_cage_lockers"], 3.4, gap=0.05)
    wall_y(R, B, "N", "engtool_wall_parts_bins", 11.95, 1.7)

    R.line("Pallet racking (middle row)",
           "Two low-bay pallet racks stand in a row 1.2 m from the shelving, holding the mid-size spares that are issued every few weeks; "
           "both faces are reachable from the aisles.")
    line_x(R, B, ["pallet_rack_bay_low_wire", "pallet_rack_bay_low_wire"], 5.0, 13.75, 0.0, gap=0.1)

    R.line("Power-cell and sealed parts lockers (east wall)",
           "Charged energy cells and sealed electronic parts are kept in ventilated lockers on the east wall, away from the aisle "
           "traffic, with the hull behind them as the heat sink.")
    aw(R, B, "E", "capacitor_power_cell_locker", 12.5)
    aw(R, B, "E", "capacitor_power_cell_locker", 13.5)
    aw(R, B, "D0", "storagebin_sealed_parts_locker", 1.5)

    R.line("Spare nozzle, coil and palletised spares (south wall, east of the hangar door)",
           "Bulky spares for the thrusters and reactor - an ion-drive engine and a plasma coil - stand in marked bays against the south wall next "
           "to the hangar door, with a banded pallet of boxed spares beside them, so the loader can take them straight to a craft or down the corridor.")
    put(R, B, "nozzle_ion_drive_engine", 9.0, 17.2, 0.0)
    put(R, B, "coil_helical_plasma_coil", 10.3, 17.3, 0.0)
    put(R, B, "pallet_crates_banded", 11.65, 17.25, 0.0)

    R.line("Tool and parts bins, pallet jack (south wall, west of the hangar door)",
           "A parts-bin rack and a drawer cabinet take the everyday spares (fuses, gaskets, filters); beside them a hand pallet jack is parked for the 4 m move of pallets to the hangar door without starting the forklift.")
    wall_row(R, B, "S", ["shelving_parts_bins_rack", "storagebin_drawer_cabinet", "loader_hand_pallet_jack"], 2.1, gap=0.06)

    R.line("Safety, signs and services",
           "An extinguisher by each door, a first-aid cabinet by the desk, exit signs over both doors; cable tray and pipes overhead.")
    fe(R, B, "W", 16.6)
    wall_y(R, B, "N", "safety_first_aid_cabinet", 3.0, 1.3)
    wall_y(R, B, "W", "sign_emergency_exit", 14.5, 2.9, check=False)
    wall_y(R, B, "S", "sign_emergency_exit", 7.0, 3.0, check=False)
    ceil_run(R, B, ["cabletray_ladder_tray"] * 5, 3.0, 15.2, "x")
    ceil_run(R, B, ["pipe_ceiling_hanger_run"] * 5, 3.0, 12.6, "x")


# ----------------------------------------------------------------------------------------------- HANGAR BAY
def f_hangar(R, B):
    R.describe(
        "The Hangar Bay parks, services and launches the ship's small craft through the force-field opening in the stern.",
        basis="Three small craft stand nose-out on 6 m landing pads, 2.4-2.7 m apart and well clear of the walls; a 3 m strip in front of the "
              "stern force field and the lanes from the three north doors (corridor, cargo opening, depot) are kept open. Ground power, "
              "fuel and tools stand between the craft and along the walls; fire fighting equipment is by the stern opening.",
        crew=4,
        adjacency="Aft corridor (north door, c=0), Cargo Bay (4 m opening at x=-7) and Spares Depot (door at x=7) along the north wall; "
                  "open space through the 14 m force field to the stern.",
        notes="Ceiling is 8 m: high-bay fixtures and service gantries hang from it; the craft are the tall items.")
    R.line("High-bay lighting", "Industrial high-bay lights on a 5.5 m grid give even 300 lux across the pads without shadowing the craft.")
    lights(R, spacing=5.5, energy=2.2, color="#fff6e8", ids=("ceilinglight_industrial_high_bay",), x_margin=1.5)

    R.keep_clear((-7.0, 28.85, 7.0, 31.85), "3 m strip in front of the stern force field: launch path and emergency egress")
    R.keep_clear((-9.0, 18.0, -5.0, 21.2), "lane from the cargo opening into the hangar")
    R.keep_clear((-1.5, 18.0, 1.5, 21.2), "lane from the corridor door")

    R.line("Landing pads and craft",
           "Three small craft sit on marked 6 m pads, noses to the stern opening so each can launch straight out without turning; "
           "the interceptor is nearest the cargo lane, the shuttle in the middle and the repair pod on the depot side, where its spares are.")
    for x, craft in ((-6.5, "craft_interceptor"), (0.0, "craft_shuttlecraft"), (6.1, "craft_repair_pod")):
        R.place(mm(B, "hangartool_landing_pad_square"), x, 24.9, 0.0, reserve=False)
        put(R, B, craft, x - (0.4 if craft == "craft_interceptor" else 0.0), 24.9, 0.0)

    R.line("Ground power units",
           "A ground power unit between each pair of craft keeps systems live without running the engines; each reaches both neighbours on its cable.")
    put(R, B, "hangartool_ground_power_unit", -3.35, 24.9, 0.0)
    put(R, B, "hangartool_ground_power_unit", 3.6, 24.9, 0.0)

    R.line("Fuel and servicing",
           "A refuelling pump and fuel hose reel on the east facets serve all three pads; an engine stand and hoist stand next to them for "
           "beside them.")
    aw(R, B, "D6", "hangartool_refuelling_pump", 1.6)
    aw(R, B, "D5", "hangartool_fuel_hose_reel", 1.5)
    aw(R, B, "D3" if False else "D4", "hangartool_wheel_chocks", 1.0)

    R.line("Tow tug and tool carts (north wall, east of the depot door)",
           "The tow tug is parked beside the depot door to move craft; a tool chest and cart sit with it so a crew can start a job from one place.")
    wall_row(R, B, "N", ["storagebin_toolchest_wheels", "loader_cargo_tug", "hangartool_tool_cart"], 8.8, gap=0.15)

    R.line("Storage racks (north wall, west)",
           "Shelving and a drawer cabinet hold the hangar's consumables (seals, fluids, fasteners) next to the cargo opening.")
    wall_row(R, B, "N", ["shelving_heavy_boxes", "storagebin_drawer_cabinet"], -12.3, gap=0.1)
    wall_row(R, B, "N", ["shelving_parts_bins_rack", "locker_double_locker_bank"], -4.6, gap=0.1)

    R.line("Hangar control console",
           "The flight-deck controller works from a console at the forward wall, facing the pads, with the door and force-field controls in reach.")
    con = aw(R, B, "N", "console_flight_control", 3.6)
    seat_for(R, B, con, "seat_ops_chair")

    R.line("Fire fighting and crash equipment (stern)",
           "The fire cannon and crash cart stand either side of the stern opening, where a crash landing or launch fire is most likely; "
           "the door control pillars stand beside them at the field edges.")
    put(R, B, "hangartool_fire_cannon", -7.7, 29.8, 180.0)
    put(R, B, "hangartool_crash_cart", 7.7, 29.6, 180.0)
    put(R, B, "hangartool_door_control_pillar", -7.45, 31.3, 180.0)
    put(R, B, "hangartool_door_control_pillar", 7.45, 31.3, 180.0)

    R.line("Safety bollards and zone markings",
           "Bollards mark the edge of the force-field strip and floor stencils show the walking route from the doors to the pads.")
    for x in (-5.0, -1.7, 1.7, 5.0):
        put(R, B, "hangartool_bollard_set", x, 28.55, 0.0)
    put(R, B, "sign_floor_marking", 0.0, 21.6, 90.0)

    R.line("Overhead services and signs",
           "Air and fuel lines run along the ceiling gantry; hazard and exit signs mark the doors.")
    ceil_run(R, B, ["pipe_ceiling_insulated_pair"] * 10, -11.0, 20.4, "x")
    wall_y(R, B, "N", "sign_dept_hangar", 0.0, bottom=2.9, check=False)
    fe(R, B, "N", 2.4)
    fe(R, B, "N", -3.2)
