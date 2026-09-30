#!/usr/bin/env python3
"""Arrange the 1000 Blender components inside the starship.

    python tools/layout/generate_ship.py            # writes godot/data/ship.json

Deterministic: same catalog -> same ship. Every model of the catalogue is placed at least once
(leftovers go to the spares stores on Deck 3).
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import Catalog, Room, Ship, FACE_YAW, WALL_T  # noqa: E402
from dressing import *  # noqa: E402,F401,F403

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GODOT = os.path.join(ROOT, "godot")

DEPT = {
    "command": dict(tint="#cfd8ec", floor="carpet", floor_tint="#8090b8", accent="#3a6ea5"),
    "crew": dict(tint="#e6dccd", floor="carpet", floor_tint="#9a8676", accent="#c09048"),
    "medical": dict(tint="#eaf3f3", floor="hull_panel", floor_tint="#dfeceb", accent="#2fa8a0"),
    "science": dict(tint="#e0eee3", floor="hull_panel", floor_tint="#cfe0d2", accent="#3aa55a"),
    "security": dict(tint="#d8d0d0", floor="deck_plate", floor_tint="#b0a0a0", accent="#c04040"),
    "engineering": dict(tint="#d8d0c4", floor="deck_plate", floor_tint="#ffffff", accent="#e08a2a"),
    "cargo": dict(tint="#cfcfc6", floor="deck_plate", floor_tint="#d8d4c4", accent="#d8b030"),
    "transit": dict(tint="#d4dae2", floor="deck_plate", floor_tint="#e8ecf2", accent="#4a78b0"),
    "life": dict(tint="#d3e5dc", floor="hull_panel", floor_tint="#c8dcd2", accent="#30a58a"),
}


class Builder:
    def __init__(self, cat):
        self.cat = cat
        self.ship = Ship(cat)
        self.ship.decks = [{"id": 1, "name": "Command Deck", "y": 8.0}, {"id": 2, "name": "Habitat Deck", "y": 4.0},
                           {"id": 3, "name": "Engineering Deck", "y": 0.0}]

    def room(self, rid, name, deck, rect, dept="transit", height=3.4, **kw):
        opts = dict(DEPT[dept])
        opts.update(kw)
        return self.ship.add_room(Room(self.ship, rid, name, deck, rect, height=height, dept=dept, **opts))

    def m(self, cat, label=None, **kw):
        return self.cat.pick(cat, label=label, **kw)


# ================================================================== the ship
def build(cat):
    B = Builder(cat)
    S = B.ship
    rm = B.room

    # ---------------------------------------------------------------- DECK 1
    bridge = rm("bridge", "Bridge", 1, (-10, -40, 10, -24), "command", height=4.2)
    cor1 = rm("cor1", "Command Corridor", 1, (-2, -24, 2, 28), "transit")
    ready = rm("ready", "Captain's Ready Room", 1, (-14, -24, -2, -12), "command")
    conf = rm("conf", "Conference Room", 1, (2, -24, 14, -12), "command")
    lounge = rm("lounge", "Observation Lounge", 1, (-14, -12, -2, 6), "crew", height=3.6)
    comms = rm("comms", "Communications Centre", 1, (2, -12, 14, 0), "command")
    astro = rm("astro", "Astrometrics", 1, (2, 0, 14, 14), "science", floor="carpet", floor_tint="#6a7f96")
    cabin1 = rm("cabin1", "Officers' Cabins A", 1, (-14, 6, -2, 16), "crew")
    cabin2 = rm("cabin2", "Officers' Cabins B", 1, (-14, 16, -2, 28), "crew")
    capt = rm("capt", "Captain's Quarters", 1, (2, 14, 14, 28), "crew", floor_tint="#a08870")
    lobby1 = rm("lobby1", "Turbolift Lobby", 1, (-6, 28, 6, 36), "transit")
    liftA1 = rm("liftA1", "Turbolift A", 1, (-10, 29, -6, 33), "transit", floor_tint="#9098a8")
    liftB1 = rm("liftB1", "Turbolift B", 1, (6, 29, 10, 33), "transit", floor_tint="#9098a8")

    # ---------------------------------------------------------------- DECK 2
    cor2 = rm("cor2", "Main Corridor", 2, (-2, -32, 2, 28), "transit")
    armory = rm("armory", "Armory", 2, (-18, -32, -2, -22), "security")
    galley = rm("galley", "Galley", 2, (-18, -22, -2, -12), "crew", floor="hull_panel", floor_tint="#d8d8d4")
    mess = rm("mess", "Mess Hall", 2, (-18, -12, -2, 6), "crew", height=3.6)
    rec = rm("rec", "Recreation & Gym", 2, (-18, 6, -2, 18), "crew", floor="deck_plate", floor_tint="#7a7f8a")
    dorm = rm("dorm", "Crew Quarters", 2, (-18, 18, -2, 28), "crew")
    brig = rm("brig", "Brig", 2, (2, -32, 18, -22), "security")
    secoff = rm("secoff", "Security Office", 2, (2, -22, 18, -14), "security", floor="carpet", floor_tint="#6a6a72")
    medbay = rm("medbay", "Medical Bay", 2, (2, -14, 18, 4), "medical", height=3.6)
    sci = rm("sci", "Science Laboratory", 2, (2, 4, 18, 16), "science")
    hydro = rm("hydro", "Hydroponics Garden", 2, (2, 16, 18, 28), "life", height=3.6)
    lobby2 = rm("lobby2", "Turbolift Lobby", 2, (-6, 28, 6, 36), "transit")
    liftA2 = rm("liftA2", "Turbolift A", 2, (-10, 29, -6, 33), "transit", floor_tint="#9098a8")
    liftB2 = rm("liftB2", "Turbolift B", 2, (6, 29, 10, 33), "transit", floor_tint="#9098a8")

    # ---------------------------------------------------------------- DECK 3
    cor3 = rm("cor3", "Engineering Corridor", 3, (-2, -32, 2, 28), "transit")
    life = rm("life", "Life Support", 3, (-18, -32, -2, -18), "life", floor="deck_plate")
    core = rm("core", "Computer Core", 3, (-18, -18, -2, -6), "command", floor="hull_panel", floor_tint="#b8c4d8", accent="#33aaff")
    shop = rm("shop", "Engineering Workshop", 3, (-18, -6, -2, 6), "engineering")
    cargoA = rm("cargoA", "Cargo Bay 1", 3, (-18, 6, -2, 28), "cargo", height=3.4)
    airlock = rm("airlock", "Airlock & EVA Prep", 3, (2, -32, 18, -24), "security", floor="deck_plate", floor_tint="#a8b0b8", accent="#e0c020")
    eng = rm("eng", "Main Engineering", 3, (2, -24, 18, 0), "engineering", height=3.4)
    aux = rm("aux", "Power Distribution", 3, (2, 0, 18, 14), "engineering")
    cargoB = rm("cargoB", "Spares Depot", 3, (2, 14, 18, 28), "cargo")
    lobby3 = rm("lobby3", "Turbolift Lobby", 3, (-6, 28, 6, 36), "transit")
    liftA3 = rm("liftA3", "Turbolift A", 3, (-10, 29, -6, 33), "transit", floor_tint="#9098a8")
    liftB3 = rm("liftB3", "Turbolift B", 3, (6, 29, 10, 33), "transit", floor_tint="#9098a8")
    hangar = rm("hangar", "Hangar Bay", 3, (-18, 36, 18, 62), "cargo", height=8.0, floor="deck_plate", floor_tint="#a8acb4")

    # ---------------------------------------------------------------- links (doors / arches)
    L = S.link
    L("bridge", "cor1", c=0)
    L("ready", "cor1", c=-18)
    L("conf", "cor1", c=-18)
    L("lounge", "cor1", c=-3, kind="portal")
    L("comms", "cor1", c=-6)
    L("astro", "cor1", c=7, kind="portal")
    L("cabin1", "cor1", c=11)
    L("cabin2", "cor1", c=22)
    L("capt", "cor1", c=21, kind="portal")
    L("cor1", "lobby1", kind="open", c=0, width=4.0, height=3.2)
    L("lobby1", "liftA1", c=31)
    L("lobby1", "liftB1", c=31)

    L("armory", "cor2", c=-27)
    L("galley", "cor2", c=-17, kind="portal")
    L("mess", "cor2", c=-3, kind="portal")
    L("rec", "cor2", c=12, kind="portal")
    L("dorm", "cor2", c=23, kind="portal")
    L("brig", "cor2", c=-27)
    L("secoff", "cor2", c=-18)
    L("medbay", "cor2", c=-9)
    L("sci", "cor2", c=10)
    L("hydro", "cor2", c=22, kind="portal")
    L("cor2", "lobby2", kind="open", c=0, width=4.0, height=3.2)
    L("lobby2", "liftA2", c=31)
    L("lobby2", "liftB2", c=31)

    L("life", "cor3", c=-25)
    L("core", "cor3", c=-12)
    L("shop", "cor3", c=0)
    L("cargoA", "cor3", c=17)
    L("airlock", "cor3", c=-28)
    L("eng", "cor3", c=-12)
    L("aux", "cor3", c=7)
    L("cargoB", "cor3", c=21)
    L("cor3", "lobby3", kind="open", c=0, width=4.0, height=3.2)
    L("lobby3", "liftA3", c=31)
    L("lobby3", "liftB3", c=31)
    L("lobby3", "hangar", kind="open", c=0, width=6.0, height=3.4)

    # windows
    bridge.add_window("N", 0, 15.0, 0.8, 3.7)
    lounge.add_window("W", -3.0, 4.0, 0.8, 2.8); lounge.add_window("W", -8.0, 4.0, 0.8, 2.8)
    capt.add_window("E", 21, 5.0, 0.9, 2.7)
    astro.add_window("E", 7, 5.0, 0.9, 2.7)
    hydro.add_window("E", 22, 6.0, 0.9, 2.8)
    hangar.forcefields.append({"pos": [0, 8.0 * 0 + 3.2, 61.9], "size": [16.0, 6.4], "yaw": 0.0})

    # lifts (trigger volumes)
    for dk in (1, 2, 3):
        y = S.deck_y(dk)
        S.lifts.append({"name": f"A{dk}", "pos": [-8, y + 1.2, 31], "size": [3.4, 2.4, 3.4]})
        S.lifts.append({"name": f"B{dk}", "pos": [8, y + 1.2, 31], "size": [3.4, 2.4, 3.4]})

    furnish_all(B)
    S.spawn = {"pos": [0.0, 4.1, 24.0], "yaw": 0.0}
    cameras(S)
    return B


# ================================================================== furnishing
import recipes_deck1, recipes_deck2, recipes_deck3  # noqa: E402

TOUR = [
    # name, room, eye, target
    ("01_bridge", "bridge", (0, 9.62, -25.4), (0, 9.4, -39)),
    ("02_bridge_window", "bridge", (-2.0, 9.62, -31.5), (-9.5, 9.0, -40)),
    ("03_command_corridor", "cor1", (0, 9.62, 26.0), (0, 9.4, -20)),
    ("04_observation_lounge", "lounge", (-3.4, 9.62, 4.6), (-12.5, 9.2, -4.5)),
    ("05_conference_room", "conf", (3.4, 9.62, -13.2), (10, 9.2, -21)),
    ("06_astrometrics", "astro", (3.4, 9.62, 1.5), (9, 9.0, 8.5)),
    ("07_captains_quarters", "capt", (3.4, 9.62, 26.5), (10, 9.0, 18)),
    ("08_main_corridor", "cor2", (0, 5.62, 25.0), (0, 5.4, -25)),
    ("09_mess_hall", "mess", (-3.4, 5.62, 4.6), (-12, 5.0, -6)),
    ("10_galley", "galley", (-3.4, 5.62, -13.2), (-12, 5.0, -20.5)),
    ("11_medical_bay", "medbay", (3.4, 5.62, 2.6), (12, 4.9, -8)),
    ("12_science_lab", "sci", (3.4, 5.62, 5.4), (12, 5.0, 12)),
    ("13_hydroponics", "hydro", (3.4, 5.62, 17.4), (12, 5.2, 24)),
    ("14_brig", "brig", (3.4, 5.62, -23.4), (10, 5.0, -30)),
    ("15_armory", "armory", (-3.4, 5.62, -23.4), (-10, 5.0, -30)),
    ("16_recreation", "rec", (-3.4, 5.62, 7.4), (-12, 5.0, 15)),
    ("17_turbolift_lobby", "lobby2", (0, 5.62, 29.6), (0, 5.4, 35)),
    ("18_main_engineering", "eng", (3.6, 1.62, -1.4), (11, 1.6, -12)),
    ("19_engineering_reactor", "eng", (9.5, 1.62, -20.5), (10, 1.6, -12)),
    ("20_computer_core", "core", (-3.4, 1.62, -7.4), (-11, 1.4, -13)),
    ("21_life_support", "life", (-3.4, 1.62, -19.4), (-11, 1.4, -26)),
    ("22_cargo_bay", "cargoA", (-3.4, 1.62, 7.4), (-11, 1.2, 20)),
    ("23_airlock", "airlock", (3.4, 1.62, -25.4), (10, 1.5, -30)),
    ("24_hangar_bay", "hangar", (0, 1.62, 37.4), (0, 2.5, 56)),
    ("25_hangar_forcefield", "hangar", (-8, 1.62, 40), (6, 2.2, 61)),
]


def furnish_all(B):
    recipes = {}
    for mod in (recipes_deck1, recipes_deck2, recipes_deck3):
        for k, v in vars(mod).items():
            if k.startswith("f_"):
                recipes[k[2:]] = v
    for rid, room in B.ship.rooms.items():
        fn = recipes.get(rid)
        if fn is None:
            print("warning: no recipe for", rid)
            continue
        fn(room, B)
    for rid, room in B.ship.rooms.items():
        if rid.startswith("lift"):
            continue
        if rid not in ("cargoB",):
            garnish(room, max_new=70 if room.w * room.d > 150 else 35)
        tabletop_pass(room)
    store_leftovers(B)


def cameras(S):
    S.cameras = []
    for name, rid, eye, tgt in TOUR:
        yaw, pitch = look(eye, tgt)
        S.cameras.append({"name": name, "title": S.rooms[rid].name,
                          "subtitle": "DECK %d - %s" % (S.rooms[rid].deck, next(d["name"] for d in S.decks if d["id"] == S.rooms[rid].deck)),
                          "pos": list(eye), "yaw": yaw, "pitch": pitch})


def store_leftovers(B):
    """Every catalogue model must exist in the ship: put anything not yet used on the shelves
    and floors of the spares stores (cargo bays, workshop, hangar)."""
    cat = B.cat
    pack_depot(B)
    stores = [B.ship.rooms[r] for r in ("hangar", "cargoA", "cargoB", "shop", "aux")]
    left = sorted(cat.unused(), key=lambda m: -(m["size"][0] * m["size"][2]))
    placed = 0
    for m in left:
        ok = False
        big = m["size"][0] * m["size"][2] > 5.0
        for R in stores:
            if R.id == "hangar" and not big and m["mount"] == "floor":
                continue
            ix0, iz0, ix1, iz1 = R.inner(0.3)
            if m["mount"] == "floor":
                step = 0.5
                spots = [(x, z) for x in frange(ix0 + 0.4, ix1 - 0.4, step) for z in frange(iz0 + 0.4, iz1 - 0.4, step)]
                R.rng.shuffle(spots)
                for (x, z) in spots:
                    if R.place(m, x, z, R.rng.choice([0, 90, 180, 270]), margin=0.15):
                        ok = True
                        break
            elif m["mount"] == "ceiling":
                spots = [(x, z) for x in frange(ix0 + 0.5, ix1 - 0.5, 0.5) for z in frange(iz0 + 0.5, iz1 - 0.5, 0.5)]
                R.rng.shuffle(spots)
                for (x, z) in spots[:300]:
                    if R.place(m, x, z, 0.0, y=R.y + R.h, check=True):
                        ok = True
                        break
            elif m["mount"] == "wall":
                for side in R.rng.sample(["N", "S", "E", "W"], 4):
                    a0, a1 = (ix0, ix1) if side in "NS" else (iz0, iz1)
                    for a in frange(a0 + m["size"][0] / 2 + 0.1, a1 - m["size"][0] / 2 - 0.1, 0.3):
                        for yy in (1.4, 2.2, 0.9):
                            if R.wall_item(side, m, a, y=yy):
                                ok = True
                                break
                        if ok:
                            break
                    if ok:
                        break
            else:   # table items: stand on any flat host prop in a store room
                hosts = [p for p in R.props if "_fp" in p and (p["_m"].get("top_y") or 0) >= 0.45 and p["_m"]["mount"] == "floor"]
                R.rng.shuffle(hosts)
                for h in hosts:
                    fp = h["_fp"]
                    dx = R.rng.uniform(-0.3, 0.3) * (fp[2] - fp[0])
                    dz = R.rng.uniform(-0.3, 0.3) * (fp[3] - fp[1])
                    if R.on_top(h, m, dx, dz):
                        ok = True
                        break
            if ok:
                placed += 1
                break
        if not ok:
            print("warning: could not place leftover", m["id"])
    print(f"leftovers stored: {placed}/{len(left)}")


def pack_depot(B):
    """Tidy storage rows in the Spares Depot: floor-standing leftovers sorted by category, one aisle per row."""
    R = B.ship.rooms["cargoB"]
    items = [m for m in B.cat.unused() if m["mount"] == "floor" and m["size"][0] * m["size"][2] < 6.0 and max(m["size"][0], m["size"][2]) < 3.0]
    items.sort(key=lambda m: (m["category"], m["id"]))
    ix0, iz0, ix1, iz1 = R.inner(0.5)
    x, z, row_d = ix0 + 0.4, iz0 + 0.4, 0.0
    for m in items:
        w, d = m["size"][0], m["size"][2]
        if x + w > ix1 - 0.4:
            x, z, row_d = ix0 + 0.4, z + row_d + 1.1, 0.0
        if z + d > iz1 - 0.4:
            break
        if R.place(m, x + w / 2, z + d / 2, 180.0 if False else 0.0, margin=0.05):
            x += w + 0.25
            row_d = max(row_d, d)


def frange(a, b, s):
    x = a
    while x <= b:
        yield x
        x += s


def main():
    cat = Catalog(os.path.join(GODOT, "data", "catalog.json"))
    B = build(cat)
    S = B.ship
    rooms = [r.to_json() for r in S.rooms.values()]
    total = sum(len(r["props"]) for r in rooms) + len(S.doors)
    out = {"version": 1, "decks": S.decks, "rooms": rooms, "doors": S.doors, "lifts": S.lifts,
           "cameras": S.cameras, "spawn": S.spawn,
           "stats": {"rooms": len(rooms), "props": total,
                     "distinct_models": sum(1 for v in cat.use.values() if v > 0), "catalog": len(cat.models)}}
    path = os.path.join(GODOT, "data", "ship.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    unused = cat.unused()
    print(f"{len(rooms)} rooms, {total} placements, {out['stats']['distinct_models']}/{len(cat.models)} models used "
          f"({len(unused)} unused) -> {os.path.relpath(path, ROOT)} ({os.path.getsize(path) / 1024:.0f} KB)")
    if unused:
        print("unused:", ", ".join(m["id"] for m in unused[:20]))
        sys.exit(1)


if __name__ == "__main__":
    main()
