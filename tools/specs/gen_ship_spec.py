#!/usr/bin/env python3
"""Ship-level design specification -> docs/SHIP_SPEC.md

    python tools/specs/gen_ship_spec.py [--root DIR] [--out FILE]

Aggregates godot/data/ship.json (decks, rooms, props, doors, stairs, hull outlines) with the machine datasheets of godot/data/specs.json
and the ship description of the lore.  Generic over the number of decks and rooms.  Standard library only, deterministic.
"""
import argparse
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_lore  # noqa: E402
import specagg as A  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

DEPT_NAMES = {"command": "Command", "transit": "Circulation", "crew": "Crew and habitat", "security": "Security", "engineering": "Engineering",
              "cargo": "Cargo and hangar", "science": "Science", "life": "Life support and garden", "medical": "Medical"}
ESSENTIAL = ("life", "medical", "command")
# design assumptions (documented in the generated file)
ASSUME = [
    ("Pressure hull skin incl. ablative layer", "300 kg/m2 of wetted skin (perimeter x deck height)"),
    ("Deck slabs and roof", "140 kg/m2 of hull area per deck plus one roof"),
    ("Internal bulkheads", "45 kg/m2 on half the room perimeters (walls are shared)"),
    ("Secondary structure and frames", "12 % of skin, slabs and bulkheads"),
    ("Stair flights", "1.1 t per flight (two flights per run)"),
    ("Radiators", "4.0 kW/m2 rejection, 11 kg/m2, design margin 25 %"),
    ("Tank and cylinder contents", "35 % of installed tank / cylinder / water-tank bounding volume at 900 kg/m3"),
    ("Stores", "180 days of food (1.8 kg per person-day as served), 5 days of potable water buffer (30 L per person-day), 30 days of oxygen"),
    ("Cargo", "net cargo volume = 55 % of the cargo room volume; payload 280 kg/m3; loaded to 60 % at departure"),
    ("Power diversity", "maximum demand = typical + 35 % of the gap to the connected peak"),
    ("Essential load", "typical load of command, medical and life-support rooms plus 10 % of everything else"),
    ("Battery", "90 % usable"),
    ("Build cost", "equipment + 85,000 cr per tonne of structure; integration 22 %; yard overhead and margin 18 %; design and trials 6 %"),
    ("Running cost", "crew 4,200 cr/month each, provisions 11 cr/kg, maintenance 0.25 % and spares 0.1 % of equipment value per month, fuel 0.012 cr/kWh"),
]
CERT_NOTES = {
    "CSA-E24": "Electrical safety", "CSA-EMC4": "Electromagnetic compatibility", "CSA-B7": "Bridge systems", "CSA-M5": "Machinery safety",
    "CSA-R3": "Radiation protection (fusion)", "CSA-LS1": "Life support equipment", "CSA-P4": "Pressure equipment", "CSA-MD5": "Medical device class 5",
    "CSA-LAB2": "Laboratory equipment", "CSA-F1": "Fire and smoke", "CSA-F2": "Food contact", "CSA-F9": "Flight certificate", "CSA-S2": "Structural",
    "CSA-S3": "Safety equipment", "CSA-SEC2": "Security systems", "CSA-C1": "Cargo handling", "CSA-H2": "Flight deck", "CSA-L3": "Photobiological safety",
    "CSA-BIO1": "Biosafety"}


def poly_area(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2.0


def poly_perim(p):
    return sum(math.dist(p[i], p[(i + 1) % len(p)]) for i in range(len(p)))


def md_table(w, head, rows):
    w("| " + " | ".join(head) + " |")
    w("|" + "---|" * len(head))
    for r in rows:
        w("| " + " | ".join(str(c) for c in r) + " |")
    w("")


def generate(ship, specs, lore):
    out = []
    w = out.append
    decks = sorted(ship["decks"], key=lambda d: d["id"])
    rooms = ship["rooms"]
    sp = lore["ship"]
    crew = sp["crew"]
    # ---- per-room and aggregate totals
    rt = {r["id"]: A.room_totals(r, ship, specs) for r in rooms}
    deck_t = {d["id"]: A.blank() for d in decks}
    dept_t = collections.defaultdict(A.blank)
    total = A.blank()
    for r in rooms:
        A.merge(deck_t.setdefault(r["deck"], A.blank()), rt[r["id"]])
        A.merge(dept_t[r["dept"]], rt[r["id"]])
        A.merge(total, rt[r["id"]])
    # ---- geometry
    hulls = {int(k): v for k, v in ship.get("hull", {}).items()}
    allpts = [p for poly in hulls.values() for p in poly]
    if allpts:
        length = max(p[1] for p in allpts) - min(p[1] for p in allpts)
        beam = max(p[0] for p in allpts) - min(p[0] for p in allpts)
    else:
        length = beam = 0.0
    rh = {d["id"]: max([r["height"] for r in rooms if r["deck"] == d["id"]] or [3.4]) for d in decks}
    by_y = sorted(decks, key=lambda d: -d["y"])
    height = (by_y[0]["y"] + rh[by_y[0]["id"]]) if by_y else 0.0
    deck_h = {d["id"]: (by_y[i - 1]["y"] - d["y"] if i > 0 else rh[d["id"]] + 0.6) for i, d in enumerate(by_y)}
    hull_area = {k: poly_area(v) for k, v in hulls.items()}
    hull_perim = {k: poly_perim(v) for k, v in hulls.items()}
    room_vol = {r["id"]: r["area"] * r["height"] for r in rooms}
    total_vol = sum(room_vol.values())
    n_items = sum(len(r["props"]) for r in rooms) + len(ship.get("doors", []))
    stairs = ship.get("stairs", [])
    flights = sum(len(run["flights"]) for s in stairs for run in s["runs"])
    # ---- mass budget
    skin = sum(hull_perim.get(d["id"], 0) * deck_h.get(d["id"], 4.0) * 300 for d in decks)
    slabs = (sum(hull_area.get(d["id"], 0) for d in decks) + (hull_area.get(decks[0]["id"], 0) if decks else 0)) * 140
    bulkheads = sum(poly_perim(r["poly"]) * r["height"] * 45 / 2.0 for r in rooms)
    frames = 0.12 * (skin + slabs + bulkheads)
    stair_kg = flights * 1100
    # thermal
    crew_heat = crew * 120.0
    heat_total = total["heat"] + crew_heat
    rad_area = heat_total * 1.25 / 4000.0
    rad_kg = rad_area * 11
    tank_vol = sum(specs[m]["dim"][0] * specs[m]["dim"][1] * specs[m]["dim"][2] / 1e9 for r in rooms for m in A.room_items(r, ship)
                   if m in specs and specs[m]["cat"] in ("tank", "cylinder", "watertank"))
    tank_kg = tank_vol * 0.35 * 900
    food_kg = crew * 180 * 1.8
    water_kg = crew * 5 * 30
    o2_kg = crew * 30 * 0.84
    air_kg = total_vol * 1.2
    cargo_rooms = [r for r in rooms if r["dept"] == "cargo"]
    cargo_gross = sum(room_vol[r["id"]] for r in cargo_rooms)
    cargo_net = cargo_gross * 0.55
    cargo_cap_kg = cargo_net * 280
    payload_kg = cargo_cap_kg * 0.6
    structure = skin + slabs + bulkheads + frames + stair_kg + rad_kg
    lightship = structure + total["kg"]
    consumables = tank_kg + food_kg + water_kg + o2_kg + air_kg + payload_kg
    displacement = lightship + consumables
    # ---- electrical
    gen_items = collections.Counter()
    sto_items = collections.Counter()
    for r in rooms:
        for m in A.room_items(r, ship):
            s = specs.get(m)
            if s and s["r"] == "g":
                gen_items[(m, r["id"])] += 1
            if s and s["r"] == "s":
                sto_items[(m, r["id"])] += 1
    gen_kw = total["gen_kw"]
    typ_kw = total["typ"] / 1000.0
    peak_kw = total["peak"] / 1000.0
    max_demand = typ_kw + 0.35 * (peak_kw - typ_kw)
    unit_max = max([specs[m]["gen"] for (m, _r) in gen_items] or [0])
    ess = 0.0
    for r in rooms:
        ess += rt[r["id"]]["typ"] * (1.0 if r["dept"] in ESSENTIAL else 0.1)
    ess_kw = ess / 1000.0
    batt_kwh = total["cap_kwh"]
    endurance_h = (batt_kwh * 0.9 / ess_kw) if ess_kw else 0.0
    margin = (gen_kw - max_demand) / gen_kw * 100 if gen_kw else 0.0
    # ---- life support
    scr_cap = 0.0
    scr_n = 0
    for r in rooms:
        for m in A.room_items(r, ship):
            s = specs.get(m)
            if s and s["cat"] == "scrubber" and any(k in m for k in ("scrubber", "sabatier", "amine", "processor")):
                scr_cap += s["dim"][0] * s["dim"][1] * s["dim"][2] / 1e9 * 30.0
                scr_n += 1
    co2_day = crew * 1.04
    planter_vol = sum(specs[m]["dim"][0] * specs[m]["dim"][1] * specs[m]["dim"][2] / 1e9 for r in rooms for m in A.room_items(r, ship)
                      if m in specs and specs[m]["cat"] == "planter")
    garden_kg_day = planter_vol * 0.30
    water_tank_l = sum(specs[m]["dim"][0] * specs[m]["dim"][1] * specs[m]["dim"][2] / 1e6 * 0.5 for r in rooms for m in A.room_items(r, ship)
                       if m in specs and specs[m]["cat"] == "watertank")
    berths = sum(1 for r in rooms for m in A.room_items(r, ship) if m in specs and specs[m]["cat"] == "bed")
    # ---- costs
    equip_cr = total["cr"]
    struct_cr = structure / 1000.0 * 85000
    integ = 0.22 * equip_cr
    sub = equip_cr + struct_cr + integ
    yard = 0.18 * sub
    design = 0.06 * (sub + yard)
    build_cr = sub + yard + design
    month_kwh = typ_kw * 730
    run = [("Crew pay (%d x 4,200 cr)" % crew, crew * 4200), ("Provisions (%d people, 30 days)" % crew, crew * 30 * 1.8 * 11),
           ("Maintenance (0.25 % of equipment)", equip_cr * 0.0025), ("Spares (0.1 % of equipment)", equip_cr * 0.001),
           ("Fuel and reaction mass (%.0f MWh)" % (month_kwh / 1000), month_kwh * 0.012)]
    run_total = sum(v for _k, v in run)

    # =========================================================== document
    w("# StarshipGo - Ship Design Specification: %s" % sp["name"])
    w("")
    w("*Generated by `python tools/specs/gen_ship_spec.py` from `godot/data/ship.json`, `godot/data/specs.json` and the lore; do not edit by hand. "
      "Machine datasheets: [MACHINE_SPECS.md](MACHINE_SPECS.md). Bill of materials with mass, power and price per line: [BOM.md](BOM.md).*")
    w("")
    w("**%s** (%s), %s, built by %s, commissioned %d. Motto *%s*. Crew complement %d." % (sp["name"], sp["registry"], sp["class"], sp["builder"], sp["commissioned"], sp["motto"], crew))
    w("")
    w("## 1. Summary")
    w("")
    md_table(w, ["Parameter", "Value"], [
        ["Length overall", "%.1f m" % length], ["Beam", "%.1f m" % beam], ["Height (keel to top of the highest deck)", "%.1f m" % height],
        ["Decks", len(decks)], ["Rooms (incl. circulation)", len(rooms)], ["Doors / stair flights", "%d / %d" % (len(ship.get("doors", [])), flights)],
        ["Pressurised volume", "%s m3" % "{:,.0f}".format(total_vol)], ["Installed equipment (items / distinct models)", "%d / %d" % (n_items, len({m for r in rooms for m in A.room_items(r, ship)}))],
        ["Equipment mass", A.fmt_kg(total["kg"])], ["Lightship displacement (structure + equipment)", A.fmt_kg(lightship)],
        ["Full-load displacement", A.fmt_kg(displacement)], ["Installed generation", "%.1f MW" % (gen_kw / 1000)],
        ["Typical electrical load", "%.2f MW" % (typ_kw / 1000)], ["Maximum demand", "%.2f MW" % (max_demand / 1000)],
        ["Battery storage", "%.0f kWh" % batt_kwh], ["Equipment value", "%s cr" % A.fmt_cr(equip_cr)], ["Estimated build cost", "%s cr" % A.fmt_cr(build_cr)],
        ["Cruise / top speed", "warp %g / warp %g (%.2f / %.1f ly per day)" % (sp["cruise_warp"], sp["top_warp"], sp["ly_per_day_at_cruise"],
                                                                                  sp["ly_per_day_at_cruise"] * (sp["top_warp"] / sp["cruise_warp"]) ** (10.0 / 3))]])
    w("## 2. Dimensions and decks")
    w("")
    w("Hull outlines are one closed convex polygon per deck (`ship.json` `hull`). The ship is %.1f m long and %.1f m wide at the widest deck." % (length, beam))
    w("")
    rows = []
    for d in decks:
        rs = [r for r in rooms if r["deck"] == d["id"]]
        t = deck_t[d["id"]]
        rows.append([d["id"], d["name"], "%+.1f m" % d["y"], "%.0f m2" % hull_area.get(d["id"], 0), len(rs), "%.0f m2" % sum(r["area"] for r in rs),
                     "%.0f m3" % sum(room_vol[r["id"]] for r in rs), t["n"], A.fmt_kg(t["kg"]), A.fmt_w(t["typ"]), A.fmt_cr(t["cr"])])
    md_table(w, ["Deck", "Name", "Floor", "Hull area", "Rooms", "Room area", "Volume", "Items", "Equip. mass", "Typ. load", "Value cr"], rows)
    w("### Rooms")
    w("")
    rows = []
    for d in decks:
        for r in [r for r in rooms if r["deck"] == d["id"]]:
            t = rt[r["id"]]
            rows.append([d["id"], "%s (`%s`)" % (r["name"], r["code"] if "code" in r else r["id"]), DEPT_NAMES.get(r["dept"], r["dept"]), "%.0f" % r["area"], "%.1f" % r["height"],
                         t["n"], A.fmt_kg(t["kg"]), A.fmt_w(t["idle"]), A.fmt_w(t["typ"]), A.fmt_w(t["peak"]), A.fmt_cr(t["cr"])])
    md_table(w, ["Deck", "Room", "Department", "m2", "H m", "Items", "Mass", "Idle", "Typical", "Peak", "Value cr"], rows)
    w("## 3. Crew complement")
    w("")
    occ = sum((r.get("brief", {}) or {}).get("crew", 0) or 0 for r in rooms)
    md_table(w, ["Item", "Value"], [["Crew complement (lore)", crew], ["Sum of room design occupancies", occ], ["Berths installed (bed models)", berths],
                                    ["Berth coverage", "%.0f %%" % (100.0 * berths / crew if crew else 0)],
                                    ["Metabolic heat (120 W each)", A.fmt_w(crew_heat)]])
    w("Departments: " + ", ".join("%s %d rooms" % (DEPT_NAMES.get(k, k), sum(1 for r in rooms if r["dept"] == k)) for k in sorted({r["dept"] for r in rooms})) + ".")
    w("")
    w("## 4. Mass budget")
    w("")
    md_table(w, ["Group", "Mass", "Share"], [[n, A.fmt_kg(v), "%.1f %%" % (100.0 * v / displacement)] for n, v in [
        ("Pressure hull skin and ablative layer", skin), ("Deck slabs and roof", slabs), ("Internal bulkheads", bulkheads), ("Secondary structure", frames),
        ("Stair flights", stair_kg), ("Radiators (external)", rad_kg), ("Installed equipment (%d items)" % n_items, total["kg"]), ("**Lightship**", lightship),
        ("Tank, cylinder and water-tank contents", tank_kg), ("Food stores (180 days)", food_kg), ("Potable water buffer", water_kg), ("Oxygen reserve (30 days)", o2_kg),
        ("Atmosphere inventory", air_kg), ("Cargo payload at departure", payload_kg), ("**Full-load displacement**", displacement)]])
    w("### Installed equipment mass by department")
    w("")
    md_table(w, ["Department", "Items", "Mass", "Share of equipment"], [[DEPT_NAMES.get(k, k), v["n"], A.fmt_kg(v["kg"]), "%.1f %%" % (100.0 * v["kg"] / total["kg"] if total["kg"] else 0)]
                                                                       for k, v in sorted(dept_t.items())])
    cat_mass = collections.Counter()
    for r in rooms:
        for m in A.room_items(r, ship):
            if m in specs:
                cat_mass[specs[m]["cat"]] += specs[m]["kg"]
    w("### Heaviest equipment families")
    w("")
    md_table(w, ["Family", "Mass", "Share"], [[c, A.fmt_kg(v), "%.1f %%" % (100.0 * v / total["kg"])] for c, v in sorted(cat_mass.items(), key=lambda kv: (-kv[1], kv[0]))[:10]])
    w("## 5. Electrical power budget")
    w("")
    w("Loads are the *typical* figures of the machine datasheets; connected peak is the sum of the peak figures. Assumptions: %s." % "; ".join(
        "%s (%s)" % (a, b) for a, b in ASSUME if a in ("Power diversity", "Essential load", "Battery")))
    w("")
    md_table(w, ["Quantity", "Value"], [
        ["Installed generation", "%.2f MW" % (gen_kw / 1000)], ["Largest single unit", "%.2f MW" % (unit_max / 1000)],
        ["Generation with the largest unit lost (N-1)", "%.2f MW" % ((gen_kw - unit_max) / 1000)], ["Hotel (idle) load", A.fmt_w(total["idle"])],
        ["Typical load", A.fmt_w(total["typ"])], ["Connected peak", A.fmt_w(total["peak"])], ["Maximum demand", "%.2f MW" % (max_demand / 1000)],
        ["Margin (generation - maximum demand)", "%.0f %%" % margin], ["Essential load (emergency)", "%.0f kW" % ess_kw], ["Battery capacity", "%.0f kWh" % batt_kwh],
        ["Battery discharge rating", "%.1f MW" % (total["store_kw"] / 1000)], ["Emergency endurance on batteries", "%.1f h" % endurance_h]])
    w("### Producers")
    w("")
    rows = []
    for (m, rid), n in sorted(gen_items.items()):
        s = specs[m]
        rows.append(["`%s`" % m, s["d"], rid, n, "%.0f kW" % s["gen"], "%.0f kW" % (s["gen"] * n), s["v"]])
    md_table(w, ["Model", "Designation", "Room", "Qty", "Output each", "Output total", "Bus"], rows or [["-", "-", "-", 0, "-", "-", "-"]])
    w("### Energy storage")
    w("")
    rows = []
    for (m, rid), n in sorted(sto_items.items()):
        s = specs[m]
        rows.append(["`%s`" % m, rid, n, "%.1f kWh" % (s["cap"] * n), "%.0f kW" % (s["gen"] * n)])
    md_table(w, ["Model", "Room", "Qty", "Capacity", "Discharge"], rows or [["-", 0, "-", "-", "-"]])
    w("### Single-line diagram")
    w("")
    w("```mermaid")
    w("flowchart LR")
    w("    subgraph SRC[Sources]")
    gens = sorted({m for (m, _r) in gen_items})
    for i, m in enumerate(gens):
        n = sum(c for (mm, _r), c in gen_items.items() if mm == m)
        w('        G%d["%s x%d<br/>%.0f kW"]' % (i, specs[m]["d"].split(" - ")[-1], n, specs[m]["gen"] * n))
    w('        B0["Batteries<br/>%.0f kWh"]' % batt_kwh)
    w("    end")
    w('    BUS{{"Main bus<br/>%.1f MW gen, %.2f MW max demand"}}' % (gen_kw / 1000, max_demand / 1000))
    for i in range(len(gens)):
        w("    G%d --> BUS" % i)
    w("    B0 <--> BUS")
    for d in decks:
        t = deck_t[d["id"]]
        w('    BUS --> D%d["Deck %d feeder<br/>%s typ"]' % (d["id"], d["id"], A.fmt_w(t["typ"])))
        for k in sorted({r["dept"] for r in rooms if r["deck"] == d["id"]}):
            tt = A.blank()
            for r in rooms:
                if r["deck"] == d["id"] and r["dept"] == k:
                    A.merge(tt, rt[r["id"]])
            if tt["typ"] > 0:
                w('    D%d --> D%d_%s["%s<br/>%s"]' % (d["id"], d["id"], k, DEPT_NAMES.get(k, k), A.fmt_w(tt["typ"])))
    w("```")
    w("")
    w("### Load by deck and department")
    w("")
    md_table(w, ["Deck", "Idle", "Typical", "Connected peak", "Share of typical"], [[d["id"], A.fmt_w(deck_t[d["id"]]["idle"]), A.fmt_w(deck_t[d["id"]]["typ"]), A.fmt_w(deck_t[d["id"]]["peak"]),
                                                                                   "%.1f %%" % (100.0 * deck_t[d["id"]]["typ"] / total["typ"] if total["typ"] else 0)] for d in decks])
    md_table(w, ["Department", "Idle", "Typical", "Connected peak", "Share of typical"], [[DEPT_NAMES.get(k, k), A.fmt_w(v["idle"]), A.fmt_w(v["typ"]), A.fmt_w(v["peak"]),
                                                                                         "%.1f %%" % (100.0 * v["typ"] / total["typ"] if total["typ"] else 0)] for k, v in sorted(dept_t.items())])
    w("### Biggest electrical consumers by family")
    w("")
    cat_w = collections.Counter()
    for r in rooms:
        for m in A.room_items(r, ship):
            if m in specs and specs[m]["r"] == "c":
                cat_w[specs[m]["cat"]] += specs[m]["w"][1]
    md_table(w, ["Family", "Typical load", "Share"], [[c, A.fmt_w(v), "%.1f %%" % (100.0 * v / total["typ"])] for c, v in sorted(cat_w.items(), key=lambda kv: (-kv[1], kv[0]))[:10]])
    w("## 6. Thermal budget")
    w("")
    md_table(w, ["Quantity", "Value"], [["Equipment heat (datasheets, typical)", A.fmt_w(total["heat"])], ["Crew metabolic heat", A.fmt_w(crew_heat)],
                                        ["Total heat to reject", A.fmt_w(heat_total)], ["Radiator area (4 kW/m2, +25 % margin)", "%.0f m2" % rad_area],
                                        ["Radiator mass", A.fmt_kg(rad_kg)],
                                        ["Coolant flow (water-glycol, 35 K rise)", "%.0f kg/s" % (heat_total / (3600.0 * 35))]])
    md_table(w, ["Deck", "Equipment heat"], [[d["id"], A.fmt_w(deck_t[d["id"]]["heat"])] for d in decks])
    w("## 7. Life-support budget")
    w("")
    days_o2 = (o2_kg + air_kg * 0.21) / (crew * 0.84) if crew else 0
    md_table(w, ["Flow (per person-day)", "Per person", "Crew of %d" % crew], [
        ["Oxygen consumed", "0.84 kg", "%.0f kg" % (crew * 0.84)], ["CO2 produced", "1.04 kg", "%.0f kg" % co2_day], ["Potable water and food water", "3.5 L", "%.0f L" % (crew * 3.5)],
        ["Hygiene and lab water", "26.5 L", "%.0f L" % (crew * 26.5)], ["Food as served", "1.8 kg", "%.0f kg" % (crew * 1.8)],
        ["Water recycled (96 %)", "28.8 L", "%.0f L" % (crew * 28.8)], ["Water makeup", "1.2 L", "%.0f L" % (crew * 1.2)]])
    md_table(w, ["Installed capability", "Value"], [
        ["CO2 scrubbing (%d units, 30 kg/day per m3)" % scr_n, "%.0f kg/day (%.1fx the crew)" % (scr_cap, scr_cap / co2_day if co2_day else 0)],
        ["Pressurised volume / air inventory", "%s m3 / %s" % ("{:,.0f}".format(total_vol), A.fmt_kg(air_kg))],
        ["Oxygen autonomy (reserve + air)", "%.0f days" % days_o2], ["Water-tank storage (50 % fill)", "%.0f L (%.1f days of crew use)" % (water_tank_l, water_tank_l / (crew * 30.0) if crew else 0)],
        ["Hydroponics planter volume / yield (0.30 kg/m3/day)", "%.1f m3 / %.1f kg/day" % (planter_vol, garden_kg_day)],
        ["Fresh produce need (0.55 kg per person-day)", "%.1f kg/day (%.0f %% covered)" % (crew * 0.55, 100.0 * garden_kg_day / (crew * 0.55) if crew else 0)],
        ["Food stores (180 days)", A.fmt_kg(food_kg)]])
    w("## 8. Propulsion, FTL, sensors, defence")
    w("")
    groups = [("Warp field and plasma", ("coil",)), ("Power generation and conversion", ("reactor", "generator", "turbine")), ("Impulse and manoeuvring", ("nozzle",)),
              ("Sensors and astronomy", ("instrument", "telescope", "antenna", "sciinstrument")), ("Defence and security", ("forcefield", "weaponrack", "camera", "cell")),
              ("Computing and communications", ("rack", "storage", "router", "commsunit")), ("Craft", ("craft",)), ("Life support machinery", ("scrubber", "tank", "watertank", "cylinder"))]
    rows = []
    for name, cats in groups:
        t = A.blank()
        for r in rooms:
            for m in A.room_items(r, ship):
                if m in specs and specs[m]["cat"] in cats:
                    A.add(t, m, specs)
        rows.append([name, ", ".join(cats), t["n"], A.fmt_kg(t["kg"]), A.fmt_w(t["typ"]), A.fmt_w(t["peak"]), A.fmt_cr(t["cr"])])
    md_table(w, ["System", "Families", "Units", "Mass", "Typical", "Peak", "Value cr"], rows)
    craft = collections.Counter(m for r in rooms for m in A.room_items(r, ship) if m in specs and specs[m]["cat"] == "craft")
    if craft:
        w("Craft carried: " + ", ".join("%s x%d (%s)" % (m, n, A.fmt_kg(specs[m]["kg"])) for m, n in sorted(craft.items())) + ".")
        w("")
    reactor_kw = sum(specs[m]["gen"] * n for (m, _r), n in gen_items.items() if specs[m]["cat"] == "reactor")
    coil_typ = sum(specs[m]["w"][1] for r in rooms for m in A.room_items(r, ship) if m in specs and specs[m]["cat"] == "coil")
    w("The ship's main power is its fusion core(s) (%.1f MW); fusion fuel burn at typical load is about %.1f g of deuterium per day (3.4e14 J/kg), so the "
      "endurance limit is the garden, the filters and the crew, not fuel. The warp coils draw %s typically." % (
          reactor_kw / 1000, (typ_kw * 1000 * 86400 / 3.4e14) * 1000, A.fmt_w(coil_typ)))
    w("")
    w("### Warp performance")
    w("")
    cw, c_day = sp["cruise_warp"], sp["ly_per_day_at_cruise"]
    cur = next((s for s in lore["systems"] if s["id"] == lore["current"]["system"]), None)
    target = next((s for s in lore["systems"] if s["kind"] == "anomaly"), None)
    dist = math.dist(cur["pos"], target["pos"]) if cur and target else 0.0
    rows = []
    k = 1.0
    while k <= sp["top_warp"] + 1e-9:
        v = c_day * (k / cw) ** (10.0 / 3)
        rows.append(["%.1f" % k, "%.3f" % v, "%.1f" % (v * 30), ("%.1f d" % (dist / v)) if dist else "-"])
        k += 1.0
    md_table(w, ["Warp factor", "ly per day", "ly per 30 days", "Days to %s (%.1f ly straight)" % (target["name"] if target else "-", dist)], rows)
    w("Speed model: `ly/day = %.2f x (warp / %g)^(10/3)`. Cruise is warp %g, top speed warp %g; above cruise the coils run hot and the maximum duration is limited by coil temperature." % (c_day, cw, cw, sp["top_warp"]))
    w("")
    w("## 9. Costs")
    w("")
    w("### Equipment value by department and deck")
    w("")
    md_table(w, ["Department", "Items", "Value cr", "Share"], [[DEPT_NAMES.get(k, k), v["n"], A.fmt_cr(v["cr"]), "%.1f %%" % (100.0 * v["cr"] / equip_cr if equip_cr else 0)] for k, v in sorted(dept_t.items())])
    md_table(w, ["Deck", "Items", "Value cr", "Share"], [[d["id"], deck_t[d["id"]]["n"], A.fmt_cr(deck_t[d["id"]]["cr"]), "%.1f %%" % (100.0 * deck_t[d["id"]]["cr"] / equip_cr if equip_cr else 0)] for d in decks])
    w("### Most valuable rooms")
    w("")
    top_rooms = sorted(rooms, key=lambda r: (-rt[r["id"]]["cr"], r["id"]))[:10]
    md_table(w, ["Room", "Deck", "Value cr", "Mass"], [[r["name"], r["deck"], A.fmt_cr(rt[r["id"]]["cr"]), A.fmt_kg(rt[r["id"]]["kg"])] for r in top_rooms])
    w("### Build cost estimate")
    w("")
    md_table(w, ["Item", "Cost cr"], [["Installed equipment", A.fmt_cr(equip_cr)], ["Hull and structure (%s)" % A.fmt_kg(structure), A.fmt_cr(struct_cr)], ["Integration (22 %)", A.fmt_cr(integ)],
                                      ["Yard overhead and margin (18 %)", A.fmt_cr(yard)], ["Design and trials (6 %)", A.fmt_cr(design)], ["**Total**", A.fmt_cr(build_cr)]])
    w("### Running cost per month")
    w("")
    md_table(w, ["Item", "Cost cr"], [[k, A.fmt_cr(v)] for k, v in run] + [["**Total per month**", A.fmt_cr(run_total)], ["**Per year**", A.fmt_cr(run_total * 12)]])
    w("## 10. Maintenance schedule")
    w("")
    buckets = collections.defaultdict(lambda: [0, 0.0])
    cat_hours = collections.Counter()
    for r in rooms:
        for m in A.room_items(r, ship):
            s = specs.get(m)
            if not s or not s["svc"]:
                continue
            per = 0.25 + 0.12 * (s["kg"] ** 0.35)
            hrs = per * 8760.0 / s["svc"]
            buckets[s["svc"]][0] += 1
            buckets[s["svc"]][1] += hrs
            cat_hours[s["cat"]] += hrs
    def label(h):
        return {168: "weekly", 1000: "every 1,000 h", 2000: "every 2,000 h", 2190: "quarterly", 3000: "every 3,000 h", 4000: "every 4,000 h", 4380: "six-monthly",
                8760: "yearly", 17520: "two-yearly"}.get(h, "every %d h" % h)
    md_table(w, ["Interval", "Hours", "Units", "Crew-hours per year"], [[label(k), "{:,}".format(k), v[0], "%.0f" % v[1]] for k, v in sorted(buckets.items())])
    tot_h = sum(v[1] for v in buckets.values())
    w("Total scheduled maintenance: %.0f crew-hours per year (%.0f per month) - about %.1f full-time technicians (1,800 h each)." % (tot_h, tot_h / 12, tot_h / 1800.0))
    w("")
    md_table(w, ["Family", "Crew-hours per year"], [[c, "%.0f" % v] for c, v in sorted(cat_hours.items(), key=lambda kv: (-kv[1], kv[0]))[:12]])
    w("## 11. Cargo capacity")
    w("")
    rows = [[r["name"], "%.0f" % room_vol[r["id"]], "%.0f" % (room_vol[r["id"]] * 0.55), A.fmt_kg(room_vol[r["id"]] * 0.55 * 280)] for r in cargo_rooms]
    md_table(w, ["Cargo room", "Volume m3", "Net m3", "Payload capacity"], rows or [["-", "-", "-", "-"]])
    w("Total net cargo volume %.0f m3, payload capacity %s (departure load %s). Craft: %s." % (cargo_net, A.fmt_kg(cargo_cap_kg), A.fmt_kg(payload_kg), ", ".join("%d x %s" % (n, m) for m, n in sorted(craft.items())) or "none"))
    w("")
    w("## 12. Performance")
    w("")
    autonomy = min(days_o2, 180)
    md_table(w, ["Figure", "Value"], [["Cruise speed", "warp %g = %.2f ly/day" % (cw, c_day)], ["Top speed", "warp %g = %.1f ly/day" % (sp["top_warp"], c_day * (sp["top_warp"] / cw) ** (10.0 / 3))],
                                      ["Autonomy (limited by oxygen and food stores)", "%.0f days" % autonomy], ["Range at cruise without resupply", "%.0f ly" % (autonomy * c_day)],
                                      ["Charter length", "four years with resupply at frontier outposts"], ["Reactor fuel burn", "about %.1f g/day" % ((typ_kw * 1000 * 86400 / 3.4e14) * 1000)]])
    w("## 13. Compliance")
    w("")
    w("Invented Concord Standards Agency (CSA) codes claimed by the installed machine datasheets:")
    w("")
    cert_n = collections.Counter()
    for r in rooms:
        for m in A.room_items(r, ship):
            if m in specs:
                for c in specs[m]["cert"]:
                    cert_n[c.split(" ")[0]] += 1
    md_table(w, ["Standard", "Scope", "Installed units claiming it"], [[c, CERT_NOTES.get(c, ""), n] for c, n in sorted(cert_n.items())])
    w("### Ship-level checks")
    w("")
    checks = [
        ("Generation margin over maximum demand >= 20 %", margin >= 20, "%.0f %%" % margin),
        ("N-1: generation without the largest unit covers the typical (cruise) load", gen_kw - unit_max >= typ_kw, "%.2f MW vs %.2f MW" % ((gen_kw - unit_max) / 1000, typ_kw / 1000)),
        ("Battery endurance on essential load >= 1 h", endurance_h >= 1.0, "%.1f h" % endurance_h),
        ("CO2 scrubbing >= 1.25 x crew production", scr_cap >= 1.25 * co2_day, "%.0f vs %.0f kg/day" % (scr_cap, co2_day)),
        ("At least two stair towers (two means of escape)", len(stairs) >= 2, "%d" % len(stairs)),
        ("Berths cover crew (or hot-bunking <= 2:1)", berths * 2 >= crew, "%d berths for %d crew" % (berths, crew)),
        ("All models have datasheets", total["missing"] == 0, "%d missing" % total["missing"]),
        ("Cargo payload >= 20 t", cargo_cap_kg >= 20000, A.fmt_kg(cargo_cap_kg))]
    md_table(w, ["Check", "Result", "Value"], [[c, "PASS" if ok else "REVIEW", v] for c, ok, v in checks])
    w("## 14. Assumptions")
    w("")
    md_table(w, ["Item", "Assumption"], [list(a) for a in ASSUME])
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ship = json.load(open(os.path.join(a.root, "godot", "data", "ship.json")))
    specs = A.load_specs(a.root)
    md = generate(ship, specs, gen_lore.build())
    out = a.out or os.path.join(a.root, "docs", "SHIP_SPEC.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(md)
    print("wrote %s (%d lines)" % (out, md.count("\n")))


if __name__ == "__main__":
    main()
