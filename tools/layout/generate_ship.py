#!/usr/bin/env python3
"""Arrange the Blender components inside the starship (BOM driven, no random fill).

    python tools/layout/generate_ship.py            # writes godot/data/ship.json

Deterministic: same catalog -> same ship.  The ship is drafted on a 3-deck grid (see docs/drafts):

    Deck 0  Sky          y = 12 m  star cartography, wardroom, library, observatory, arboretum (lens-shaped dome)
    Deck 1  Command      y = 8 m   bridge in the bow, officers' country aft
    Deck 2  Habitat      y = 4 m   mess, medical, science, security, crew
    Deck 3  Engineering  y = 0 m   engines, life support, cargo, hangar on the stern platform
    Deck 4  Hold         y = -4 m  antimatter, provisions, water, fabrication, main hold (tapering keel)

Every deck has a central spine corridor (3 m), a mid-ship cross passage ("lobby") and TWO stair
towers (port / starboard) that stack on top of each other - there are no lifts.  Rooms are the drafting
rectangles clipped by the tapered hull outline of their deck (hull.py).  The outer skin that wraps the five decks
(smooth, flared, raked) is lofted from the room volumes by hull.skin().
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hull as hulllib  # noqa: E402
from shiplib import Catalog, Room, Ship
from dressing import look  # noqa: E402
import themes  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
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

DECKS = [{"id": 0, "name": "Sky Deck", "y": 12.0}, {"id": 1, "name": "Command Deck", "y": 8.0},
         {"id": 2, "name": "Habitat Deck", "y": 4.0}, {"id": 3, "name": "Engineering Deck", "y": 0.0},
         {"id": 4, "name": "Hold Deck", "y": -4.0}]
PITCH = 4.0

# ------------------------------------------------------------------ drafting grid
CORR = 1.5                  # half width of the spine corridor
XH = hulllib.BEAM_HALF      # half beam of the parallel mid-body
LOBBY = (-6.4, 0.0, 6.4, 3.6)
TOWER_W = (-XH, 0.0, -6.4, 3.6)
TOWER_E = (6.4, 0.0, XH, 3.6)

# stair geometry (must match blender/starship/arch.py: arch_stair_flight)
RISER = PITCH / 22.0
TREAD = 0.28
FLIGHT_W = 1.4
FLIGHT_RUN = 11 * TREAD     # 3.08 m plan length of one flight
STRIP = 1.8                 # deck-level strip between the lobby opening and the first riser
PRE = 0.15                  # wall thickness


class Builder:
    def __init__(self, cat):
        self.cat = cat
        self.ship = Ship(cat)
        self.ship.decks = [dict(d) for d in DECKS]
        self.ship.hull = {d["id"]: hulllib.outline(d["id"]) for d in DECKS}

    def room(self, rid, name, deck, rect, dept="transit", height=3.4, code=None, **kw):
        opts = dict(DEPT[dept])
        opts.update(kw)
        return self.ship.add_room(Room(self.ship, rid, name, deck, rect, height=height, dept=dept, code=code, **opts))

    def m(self, cat, label=None, **kw):
        return self.cat.pick(cat, label=label, **kw)


# ================================================================== the ship
def build(cat):
    B = Builder(cat)
    S = B.ship
    rm = B.room
    R = {}

    def circulation(deck):
        d = deck
        z_fore = {0: -8.0, 1: -21.0, 2: -30.0, 3: -24.0, 4: -20.0}[d]
        z_aft = {0: 18.0, 1: 14.0, 2: 18.0, 3: 18.0, 4: 30.0}[d]
        R[f"corF{d}"] = rm(f"corF{d}", "Forward Spine Corridor", d, (-CORR, z_fore, CORR, 0.0), "transit", code=f"CF{d}")
        R[f"corA{d}"] = rm(f"corA{d}", "Aft Spine Corridor", d, (-CORR, 3.6, CORR, z_aft), "transit", code=f"CA{d}")
        R[f"lobby{d}"] = rm(f"lobby{d}", "Mid-ship Stair Lobby", d, LOBBY, "transit", code=f"LB{d}")
        R[f"towerA{d}"] = rm(f"towerA{d}", "Port Stair Tower", d, TOWER_W, "transit", code=f"SP{d}", height=3.4)
        R[f"towerB{d}"] = rm(f"towerB{d}", "Starboard Stair Tower", d, TOWER_E, "transit", code=f"SS{d}", height=3.4)

    # ---------------------------------------------------------------- DECK 0  (sky deck)
    circulation(0)
    R["starcart"] = rm("starcart", "Star Cartography", 0, (-XH, -20.0, XH, -8.0), "science", height=4.2, floor="carpet",
                       floor_tint="#52607a", accent="#6a8cff", code="SC")
    R["theatre"] = rm("theatre", "Briefing Theatre", 0, (-XH, -8.0, -CORR, 0.0), "command", code="BT")
    R["wardroom"] = rm("wardroom", "Officers' Wardroom & Bar", 0, (CORR, -8.0, XH, 0.0), "crew", floor="carpet",
                       floor_tint="#7a5a4a", accent="#d08a40", code="WR")
    R["library"] = rm("library", "Library & Archive", 0, (-XH, 3.6, -CORR, 11.0), "crew", floor="carpet", floor_tint="#6a5a4a",
                      accent="#b08a50", code="LI")
    R["arbor"] = rm("arbor", "Arboretum", 0, (-XH, 11.0, -CORR, 18.0), "life", height=3.6, floor="hull_panel", floor_tint="#9ab8a0",
                    code="AB")
    R["observ"] = rm("observ", "Observatory", 0, (CORR, 3.6, XH, 11.0), "science", floor="carpet", floor_tint="#4a566a", code="OB")
    R["flag"] = rm("flag", "Flag Officer's Suite", 0, (CORR, 11.0, XH, 18.0), "crew", floor_tint="#8a7a68", code="FS")

    # ---------------------------------------------------------------- DECK 1  (command)
    circulation(1)
    R["bridge"] = rm("bridge", "Bridge", 1, (-XH, -34.0, XH, -21.0), "command", height=4.2, code="BR")
    R["ready"] = rm("ready", "Captain's Ready Room", 1, (-XH, -21.0, -CORR, -13.0), "command", code="RR")
    R["lounge"] = rm("lounge", "Observation Lounge", 1, (-XH, -13.0, -CORR, 0.0), "crew", height=3.6, code="OL")
    R["conf"] = rm("conf", "Conference Room", 1, (CORR, -21.0, XH, -13.0), "command", code="CR")
    R["astro"] = rm("astro", "Astrometrics", 1, (CORR, -13.0, XH, 0.0), "science", floor="carpet", floor_tint="#6a7f96", code="AM")
    R["cabinA"] = rm("cabinA", "Officers' Cabins A", 1, (-XH, 3.6, -CORR, 8.8), "crew", code="OA")
    R["cabinB"] = rm("cabinB", "Officers' Cabins B", 1, (-XH, 8.8, -CORR, 14.0), "crew", code="OB")
    R["capt"] = rm("capt", "Captain's Quarters", 1, (CORR, 3.6, XH, 9.0), "crew", floor_tint="#a08870", code="CQ")
    R["comms"] = rm("comms", "Communications Centre", 1, (CORR, 9.0, XH, 14.0), "command", code="CC")

    # ---------------------------------------------------------------- DECK 2  (habitat)
    circulation(2)
    R["armory"] = rm("armory", "Armory", 2, (-XH, -30.0, -CORR, -22.0), "security", code="AR")
    R["galley"] = rm("galley", "Galley", 2, (-XH, -22.0, -CORR, -13.0), "crew", floor="hull_panel", floor_tint="#d8d8d4", code="GA")
    R["mess"] = rm("mess", "Mess Hall", 2, (-XH, -13.0, -CORR, 0.0), "crew", height=3.6, code="MH")
    R["brig"] = rm("brig", "Brig", 2, (CORR, -30.0, XH, -22.0), "security", code="BG")
    R["secoff"] = rm("secoff", "Security Office", 2, (CORR, -22.0, XH, -13.0), "security", floor="carpet", floor_tint="#6a6a72", code="SO")
    R["medbay"] = rm("medbay", "Medical Bay", 2, (CORR, -13.0, XH, 0.0), "medical", height=3.6, code="MB")
    R["rec"] = rm("rec", "Recreation & Gym", 2, (-XH, 3.6, -CORR, 11.0), "crew", floor="deck_plate", floor_tint="#7a7f8a", code="RG")
    R["dorm"] = rm("dorm", "Crew Quarters", 2, (-XH, 11.0, -CORR, 18.0), "crew", code="CW")
    R["sci"] = rm("sci", "Science Laboratory", 2, (CORR, 3.6, XH, 11.0), "science", code="SL")
    R["hydro"] = rm("hydro", "Hydroponics Garden", 2, (CORR, 11.0, XH, 18.0), "life", height=3.6, code="HY")

    # ---------------------------------------------------------------- DECK 3  (engineering)
    circulation(3)
    R["life"] = rm("life", "Life Support", 3, (-XH, -24.0, -CORR, -13.0), "life", floor="deck_plate", code="LS")
    R["core"] = rm("core", "Computer Core", 3, (-XH, -13.0, -CORR, 0.0), "command", floor="hull_panel", floor_tint="#b8c4d8",
                   accent="#33aaff", code="CO")
    R["airlock"] = rm("airlock", "Airlock & EVA Prep", 3, (CORR, -24.0, XH, -13.0), "security", floor="deck_plate",
                      floor_tint="#a8b0b8", accent="#e0c020", code="AL")
    R["eng"] = rm("eng", "Main Engineering", 3, (CORR, -13.0, XH, 0.0), "engineering", code="ME")
    R["shop"] = rm("shop", "Engineering Workshop", 3, (-XH, 3.6, -CORR, 11.0), "engineering", code="WS")
    R["cargo"] = rm("cargo", "Cargo Bay", 3, (-XH, 11.0, -CORR, 18.0), "cargo", code="CB")
    R["aux"] = rm("aux", "Power Distribution", 3, (CORR, 3.6, XH, 11.0), "engineering", floor="grating", floor_tint="#ffffff", code="PD")
    R["depot"] = rm("depot", "Spares Depot", 3, (CORR, 11.0, XH, 18.0), "cargo", code="SD")
    R["hangar"] = rm("hangar", "Hangar Bay", 3, (-XH, 18.0, XH, 32.0), "cargo", height=8.0, floor="deck_plate",
                     floor_tint="#a8acb4", code="HB")

    # ---------------------------------------------------------------- DECK 4  (hold)
    circulation(4)
    R["antimatter"] = rm("antimatter", "Antimatter Containment", 4, (-XH, -20.0, -CORR, -9.0), "engineering", height=3.4,
                         accent="#d06aff", code="AC")
    R["provisions"] = rm("provisions", "Provisions Hold & Cold Store", 4, (-XH, -9.0, -CORR, 0.0), "cargo", floor="hull_panel",
                         floor_tint="#cfd8dc", accent="#40a8d8", code="PH")
    R["water"] = rm("water", "Water Reclamation Plant", 4, (CORR, -20.0, XH, -9.0), "life", code="WP")
    R["waste"] = rm("waste", "Waste & Recycling Plant", 4, (CORR, -9.0, XH, 0.0), "life", floor="grating", floor_tint="#ffffff",
                    code="WW")
    R["fab"] = rm("fab", "Fabrication Hall", 4, (-XH, 3.6, -CORR, 14.0), "engineering", code="FH")
    R["auxctl"] = rm("auxctl", "Auxiliary Control", 4, (CORR, 3.6, XH, 14.0), "command", code="AX")
    R["hold"] = rm("hold", "Main Cargo Hold", 4, (-XH, 14.0, -CORR, 30.0), "cargo", code="MC")
    R["drone"] = rm("drone", "Drone & Probe Bay", 4, (CORR, 14.0, XH, 30.0), "cargo", floor="deck_plate", floor_tint="#a8acb4", code="DP")

    # ---------------------------------------------------------------- links (doors / arches)
    L = S.link
    for d in hulllib.DECK_IDS:
        L(f"corF{d}", f"lobby{d}", kind="open", c=0, width=3.0, height=3.2)
        L(f"corA{d}", f"lobby{d}", kind="open", c=0, width=3.0, height=3.2)
        # the stair towers open onto the cross passage over the deck-level strip
        L(f"towerA{d}", f"lobby{d}", kind="open", c=1.8, width=3.2, height=3.2)
        L(f"towerB{d}", f"lobby{d}", kind="open", c=1.8, width=3.2, height=3.2)

    # deck 0
    L("starcart", "corF0", c=0, kind="open", width=3.0, height=3.2)
    L("theatre", "corF0", c=-4.0, kind="portal")
    L("wardroom", "corF0", c=-4.0, kind="portal")
    L("library", "corA0", c=7.3, kind="portal")
    L("arbor", "corA0", c=14.5, kind="portal")
    L("observ", "corA0", c=7.3)
    L("flag", "corA0", c=14.5)
    # deck 4
    L("antimatter", "corF4", c=-14.0)
    L("provisions", "corF4", c=-4.5)
    L("water", "corF4", c=-14.0)
    L("waste", "corF4", c=-4.5)
    L("fab", "corA4", c=7.3)
    L("auxctl", "corA4", c=7.3)
    L("hold", "corA4", c=22.0, kind="open", width=3.2, height=3.2)
    L("drone", "corA4", c=22.0, kind="open", width=3.2, height=3.2)
    # deck 1
    L("bridge", "corF1", c=0)
    L("bridge", "ready", kind="door", c=-6.0)
    L("bridge", "conf", kind="door", c=6.0)
    L("ready", "corF1", c=-17.0)
    L("conf", "corF1", c=-17.0)
    L("lounge", "corF1", c=-6.5, kind="portal")
    L("astro", "corF1", c=-6.5)
    L("cabinA", "corA1", c=6.2)
    L("cabinB", "corA1", c=11.4)
    L("capt", "corA1", c=6.3)
    L("comms", "corA1", c=11.5)
    # deck 2
    L("armory", "corF2", c=-26.0)
    L("galley", "corF2", c=-17.5, kind="portal")
    L("galley", "mess", c=-7.0, kind="portal", width=3.0)
    L("mess", "corF2", c=-6.5, kind="portal")
    L("brig", "corF2", c=-26.0)
    L("brig", "secoff", c=6.0)
    L("secoff", "corF2", c=-17.5)
    L("medbay", "corF2", c=-6.5)
    L("rec", "corA2", c=7.3, kind="portal")
    L("dorm", "corA2", c=14.5, kind="portal")
    L("sci", "corA2", c=7.3)
    L("hydro", "corA2", c=14.5, kind="portal")
    # deck 3
    L("life", "corF3", c=-19.0)
    L("core", "corF3", c=-6.5)
    L("airlock", "corF3", c=-19.0)
    L("eng", "corF3", c=-6.5)
    L("shop", "corA3", c=7.3)
    L("cargo", "corA3", c=14.5)
    L("aux", "corA3", c=7.3)
    L("depot", "corA3", c=14.5)
    L("corA3", "hangar", c=0.0)
    L("cargo", "hangar", kind="open", c=-7.0, width=4.0, height=3.2)
    L("depot", "hangar", kind="door", c=7.0, model=None)

    # ---------------------------------------------------------------- windows (hull walls only)
    hull_windows(R["starcart"], width=3.6, y0=0.6, y1=3.6, margin=0.3, gap=0.3)
    hull_windows(R["theatre"], width=1.4, y0=1.0, y1=2.4)
    hull_windows(R["wardroom"], width=2.6, y0=0.8, y1=2.7)
    hull_windows(R["library"], width=1.6, y0=1.0, y1=2.6)
    hull_windows(R["arbor"], width=3.0, y0=0.6, y1=3.0)
    hull_windows(R["observ"], width=2.8, y0=0.6, y1=3.2)
    hull_windows(R["flag"], width=2.2, y0=0.8, y1=2.7)
    hull_windows(R["bridge"], width=3.4, y0=0.5, y1=3.6, margin=0.2, gap=0.25)
    hull_windows(R["lounge"], width=3.2, y0=0.7, y1=2.8)
    hull_windows(R["ready"], width=1.6, y0=0.9, y1=2.6)
    hull_windows(R["conf"], width=1.6, y0=0.9, y1=2.6)
    hull_windows(R["astro"], width=2.4, y0=0.9, y1=2.7)
    hull_windows(R["cabinA"], width=1.4, y0=1.0, y1=2.4)
    hull_windows(R["cabinB"], width=1.4, y0=1.0, y1=2.4)
    hull_windows(R["capt"], width=2.0, y0=0.8, y1=2.7)
    hull_windows(R["mess"], width=2.8, y0=0.8, y1=2.7)
    hull_windows(R["rec"], width=2.0, y0=1.0, y1=2.6)
    hull_windows(R["hydro"], width=2.6, y0=0.9, y1=2.8)
    hull_windows(R["sci"], width=2.0, y0=1.0, y1=2.6)
    hull_windows(R["medbay"], width=2.4, y0=1.0, y1=2.6)
    hull_windows(R["dorm"], width=1.2, y0=1.3, y1=2.3)
    hull_windows(R["airlock"], width=1.0, y0=1.2, y1=2.2, min_w=1.0)
    # the hangar mouth: a 14 m opening in the stern transom closed by a force field
    hang = R["hangar"]
    hang.openings.append({"side": "S", "c": 0.0, "w": 14.0, "y0": 0.0, "y1": 7.0, "kind": "open"})
    hang.wall_used["S"].append((-7.2, 7.2, 0.0, 99.0))
    hang.forcefields.append({"pos": [0.0, 3.5, 31.85], "size": [14.0, 7.0], "yaw": 0.0})

    # ---------------------------------------------------------------- stairs (replace the old lifts)
    add_stairs(S, R)

    # ---------------------------------------------------------------- furnishing
    furnish_all(B)
    lob = R["lobby2"]
    S.spawn = {"pos": [0.0, S.deck_y(2) + 0.1, lob.cz], "yaw": 0.0}
    cameras(S)
    return B


SLAB = 0.3


# structure that only exists outside the rooms: the sensor prow ahead of the bridge and the engine boom under the hangar.
# They are solid fairing (the skin must enclose them) and give the hull its pointed bow and raked stern.
FAIRINGS = [
    ([(-10.5, -33.0), (10.5, -33.0), (2.5, -51.0), (-2.5, -51.0)], -3.0, 10.5),
    ([(-6.0, -41.0), (6.0, -41.0), (2.0, -57.0), (-2.0, -57.0)], -0.5, 8.0),
    ([(-3.0, -50.0), (3.0, -50.0), (1.6, -60.0), (-1.6, -60.0)], 1.5, 6.0),
    ([(-8.0, 29.0), (8.0, 29.0), (5.5, 41.0), (-5.5, 41.0)], -5.6, -0.3),
    ([(-4.5, 38.0), (4.5, 38.0), (3.0, 46.0), (-3.0, 46.0)], -5.0, -1.5),
]


def room_volumes(S):
    """(polygon, y_lo, y_hi) of every room including its floor / ceiling slabs plus the fairings: what the outer skin
    must enclose."""
    vols = [(r.poly, r.y - SLAB, r.y + r.h + SLAB) for r in S.rooms.values()]
    return vols + [(list(p), lo, hi) for p, lo, hi in FAIRINGS]


def exterior(S):
    """Outer skin (hull.skin) and the window panels that show the rooms' hull windows on it."""
    import math
    sk = hulllib.skin(room_volumes(S))
    wins = []
    for r in S.rooms.values():
        for o in r.openings:
            if o["kind"] != "window":
                continue
            e = r.edge(o["side"])
            if e is None or not e["hull"]:
                continue
            wx, wz = r._wall_point(e, o["side"], o["c"])
            ux, uz = e["u"]
            dx, dz = -e["n"][0], -e["n"][1]                    # outward
            yc = r.y + (o["y0"] + o["y1"]) / 2
            hit = hulllib.skin_hit(sk, wx, yc, wz, dx, dz)
            hu = hulllib.skin_hit(sk, wx, yc + 0.5, wz, dx, dz)
            hd = hulllib.skin_hit(sk, wx, yc - 0.5, wz, dx, dz)
            if hit is None or hu is None or hd is None:
                continue
            v = (hu[0] - hd[0], 1.0, hu[1] - hd[1])             # slope direction: one metre of height along the skin
            dot = v[0] * ux + v[2] * uz
            v = (v[0] - dot * ux, v[1], v[2] - dot * uz)
            ln = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
            v = tuple(c / ln for c in v)
            wins.append({"room": r.id, "c": [round(hit[0], 3), round(yc, 3), round(hit[1], 3)],
                         "u": [round(ux, 4), 0.0, round(uz, 4)], "v": [round(c, 4) for c in v],
                         "w": o["w"], "h": round((o["y1"] - o["y0"]) / v[1], 3), "kind": "window"})
    # the hangar mouth: a lit, force-field-blue panel on the stern skin
    hit = hulllib.skin_hit(sk, 0.0, S.deck_y(3) + 3.5, 20.0, 0.0, 1.0)
    if hit is not None:
        hu = hulllib.skin_hit(sk, 0.0, S.deck_y(3) + 4.0, 20.0, 0.0, 1.0)
        hd = hulllib.skin_hit(sk, 0.0, S.deck_y(3) + 3.0, 20.0, 0.0, 1.0)
        vz = (hu[1] - hd[1]) / 1.0
        ln = math.sqrt(1.0 + vz * vz)
        wins.append({"room": "hangar", "c": [0.0, round(S.deck_y(3) + 3.5, 3), round(hit[1], 3)], "u": [1.0, 0.0, 0.0],
                     "v": [0.0, round(1.0 / ln, 4), round(vz / ln, 4)], "w": 14.0, "h": round(7.0 * ln, 3), "kind": "mouth"})
    belts = []
    for y, col in ((-0.3, "#33e0ff"), (3.7, "#ffab1f"), (7.7, "#cfe2ff"), (11.7, "#33e0ff")):
        poly = hulllib.skin_polygon(sk, y)
        cx, cz = sk["center"]
        pts = []
        for i, (x, z) in enumerate(poly):
            if i % 2:
                continue
            dx, dz = x - cx, z - cz
            ln = math.hypot(dx, dz) or 1.0
            pts.append([round(x + dx / ln * 0.07, 2), round(z + dz / ln * 0.07, 2)])
        belts.append({"y": y, "color": col, "pts": pts})
    return {"skin": sk, "ext_windows": wins, "exterior": exterior_fittings(sk, S), "belts": belts}


def skin_top(sk, x, z, y_from=40.0):
    y = y_from
    while y > -30.0:
        if hulllib.skin_contains(sk, x, y, z):
            return y
        y -= 0.05
    return None


def skin_bottom(sk, x, z):
    y = -30.0
    while y < 40.0:
        if hulllib.skin_contains(sk, x, y, z):
            return y
        y += 0.05
    return None


def exterior_fittings(sk, S):
    """Nacelles, deflector, masts, engines and keel fin placed on the skin: [{"m", "pos", "yaw", "pitch"}]."""
    out = []
    z0 = 4.0
    for side, mid in ((1, "arch_nacelle_starboard"), (-1, "arch_nacelle_port")):
        hit = hulllib.skin_hit(sk, 0.0, 2.5, z0, float(side), 0.0)
        out.append({"m": mid, "pos": [round(hit[0] - side * 0.9, 3), 2.5, z0], "yaw": 0.0})
    hit = hulllib.skin_hit(sk, 0.0, 4.0, 0.0, 0.0, -1.0)
    out.append({"m": "arch_deflector", "pos": [0.0, 4.0, round(hit[1] + 0.7, 3)], "yaw": 0.0, "pitch": 0.0})
    for z, scale in ((-6.0, 1.0), (7.0, 0.7)):
        yt = skin_top(sk, 0.0, z)
        out.append({"m": "arch_mast", "pos": [0.0, round(yt - 0.4, 3), z], "yaw": 0.0, "scale": scale})
    hit = hulllib.skin_hit(sk, 0.0, -2.6, 20.0, 0.0, 1.0)
    out.append({"m": "arch_engine_cluster", "pos": [0.0, -2.6, round(hit[1] - 2.2, 3)], "yaw": 0.0})
    yb = skin_bottom(sk, 0.0, 4.0)
    out.append({"m": "arch_keel_fin", "pos": [0.0, round(yb + 0.35, 3), 4.0], "yaw": 0.0})
    return out


def hull_windows(room, width=2.0, y0=0.9, y1=2.6, pitch=None, margin=0.25, min_w=0.8, gap=0.3):
    """Windows evenly spaced along every hull-exposed wall of the room (axis-aligned walls and hull facets)."""
    pitch = pitch or width + 1.2
    for e in room.edges:
        if not e["hull"]:
            continue
        usable = e["len"] - 2 * margin
        if usable < min_w:
            continue
        n = max(1, int(usable // pitch))
        w = min(width, usable / n - gap)
        if w < min_w and n > 1:
            n -= 1
            w = min(width, usable / n - gap)
        if w < min_w:
            continue
        for k in range(n):
            mid = margin + usable * (k + 0.5) / n          # distance along the edge from its start
            if e["side"] in ("N", "S"):
                c = min(e["a"][0], e["b"][0]) + mid
            elif e["side"] in ("E", "W"):
                c = min(e["a"][1], e["b"][1]) + mid
            else:
                c = mid
            room.add_window(e["side"], c, w, y0, y1)


# ================================================================== stairs
def stair_rects(side):
    """Plan rectangles of one stair tower (inner faces): strip, flight lanes, landing and the slab holes."""
    xa, za, xb, zb = TOWER_W if side == "A" else TOWER_E
    z0, z1 = za + PRE, zb - PRE
    sgn = 1 if side == "A" else -1            # +1: the strip is at the east end (port tower)
    x_inner_far = xa + PRE if side == "A" else xb - PRE           # outer wall face (hull side)
    x_strip_end = xb - PRE if side == "A" else xa + PRE           # inner wall face (lobby side)
    x_foot = x_strip_end - sgn * STRIP                            # where the flights start
    x_land = x_foot - sgn * FLIGHT_RUN                            # where the mid-landing starts
    lane_a = (z0, z0 + FLIGHT_W + 0.05)
    lane_b = (z1 - FLIGHT_W - 0.05, z1)
    return dict(z0=z0, z1=z1, sgn=sgn, x_far=x_inner_far, x_end=x_strip_end, x_foot=x_foot, x_land=x_land,
                lane_a=lane_a, lane_b=lane_b, yaw_up=(90.0 if side == "A" else -90.0))


def add_stairs(S, R):
    """Two dog-leg stair towers, one flight pair per deck pair.  Flight A leaves the deck-level strip,
    climbs to the mid-landing, flight B climbs back to the strip of the deck above."""
    for side in ("A", "B"):
        g = stair_rects(side)
        za, zb = g["lane_a"], g["lane_b"]
        x0h, x1h = sorted((g["x_far"], g["x_foot"]))            # hole extent along x for the flight lanes
        land0, land1 = sorted((g["x_far"], g["x_land"]))
        holes = [[x0h, za[0], x1h, za[1]], [x0h, zb[0], x1h, zb[1]], [land0, g["z0"], land1, g["z1"]]]
        runs = []
        for lo, hi in ((4, 3), (3, 2), (2, 1), (1, 0)):
            y0 = S.deck_y(lo)
            za_c = g["z0"] + FLIGHT_W / 2
            zb_c = g["z1"] - FLIGHT_W / 2
            # flight A: starts at the strip edge, climbs away from the lobby
            fa = {"pos": [round(g["x_foot"], 3), round(y0, 3), round(za_c, 3)], "yaw": g["yaw_up"], "rise": PITCH / 2, "run": 10 * TREAD}
            # flight B: starts at the landing, climbs back towards the lobby
            fb = {"pos": [round(g["x_land"], 3), round(y0 + PITCH / 2, 3), round(zb_c, 3)], "yaw": -g["yaw_up"], "rise": PITCH / 2, "run": 10 * TREAD}
            runs.append({"deck_lo": lo, "deck_hi": hi, "flights": [fa, fb],
                         "landing": {"rect": [round(v, 3) for v in (land0, g["z0"], land1, g["z1"])], "y": round(y0 + PITCH / 2, 3)}})
        S.stairs.append({"id": f"S{side}", "name": "Port stair" if side == "A" else "Starboard stair", "runs": runs,
                         "width": FLIGHT_W, "strip": [round(v, 3) for v in (min(g["x_foot"], g["x_end"]), g["z0"], max(g["x_foot"], g["x_end"]), g["z1"])]})
        for d in hulllib.DECK_IDS:
            room = R[f"tower{side}{d}"]
            if d < max(hulllib.DECK_IDS):     # the flights from the deck below arrive through this floor
                room.add_hole(holes[0], floor=True); room.add_hole(holes[1], floor=True); room.add_hole(holes[2], floor=True)
            if d > min(hulllib.DECK_IDS):     # and the flights to the deck above leave through this ceiling
                room.add_hole(holes[0], ceiling=True); room.add_hole(holes[1], ceiling=True); room.add_hole(holes[2], ceiling=True)


# ================================================================== furnishing
import importlib  # noqa: E402

ONLY_DECKS = None      # set by --decks: furnish only these decks (others stay empty) so authors can iterate independently


def furnish_all(B):
    recipes = {}
    mods = ["recipes_common"] + ["recipes_deck%d" % d for d in hulllib.DECK_IDS
                                 if (ONLY_DECKS is None or d in ONLY_DECKS) and os.path.exists(os.path.join(HERE, "recipes_deck%d.py" % d))]
    for name in mods:
        mod = importlib.import_module(name)
        for k, v in vars(mod).items():
            if k.startswith("f_"):
                recipes[k[2:]] = v
    for rid, room in B.ship.rooms.items():
        if ONLY_DECKS is not None and room.deck not in ONLY_DECKS:
            continue
        fn = recipes.get(rid)
        if fn is None:
            fn = recipes.get(rid.rstrip("0123456789")) if rid[-1].isdigit() else None
        if fn is None:
            print("warning: no recipe for", rid)
            continue
        fn(room, B)


def cameras(S):
    """Tour cameras for the rooms listed in `order` (25 of the ship's rooms): stand just inside the first door looking at the
    far side of the room; the four exterior cameras follow."""
    S.cameras = []
    order = ["bridge", "corF1", "lounge", "conf", "astro", "capt", "corF2", "mess", "galley", "medbay", "sci", "hydro", "brig", "armory",
             "rec", "lobby2", "eng", "core", "life", "cargo", "airlock", "hangar", "towerA2", "shop", "aux",
             "starcart", "theatre", "wardroom", "library", "arbor", "observ", "flag",
             "antimatter", "provisions", "water", "waste", "fab", "auxctl", "hold", "drone"]
    n = 0
    for rid in order:
        room = S.rooms.get(rid)
        if room is None:
            continue
        n += 1
        eye, tgt = _camera_for(room)
        yaw, pitch = look(eye, tgt)
        S.cameras.append({"name": "%02d_%s" % (n, rid), "room": rid, "title": room.name,
                          "subtitle": "DECK %d - %s" % (room.deck, next(d["name"] for d in S.decks if d["id"] == room.deck)),
                          "pos": [round(v, 3) for v in eye], "yaw": yaw, "pitch": pitch})
    exterior_cameras(S)


def exterior_cameras(S):
    """Outside views of the tapered hull (used for documentation screenshots)."""
    views = [("X1_bow_quarter", (-50.0, 30.0, -92.0), (0.0, 3.0, -8.0), "Exterior - bow quarter view"),
             ("X2_starboard_profile", (118.0, 5.0, 0.0), (0.0, 4.0, 0.0), "Exterior - starboard profile"),
             ("X3_stern_quarter", (52.0, 26.0, 88.0), (0.0, 2.0, 12.0), "Exterior - stern quarter, hangar mouth"),
             ("X4_plan_view", (0.0, 135.0, -1.0), (0.0, 0.0, -1.0), "Exterior - plan view")]
    for name, eye, tgt, title in views:
        yaw, pitch = look(eye, tgt)
        if name == "X4_plan_view":
            yaw, pitch = 0.0, -90.0
        S.cameras.append({"name": name, "room": "", "title": title, "subtitle": "STARSHIPGO", "exterior": True, "fov": 50.0,
                          "pos": list(eye), "yaw": yaw, "pitch": pitch})


def _camera_for(room):
    """Eye position 1 m inside the room next to its first wall opening, aimed at the far side."""
    op = next((o for o in room.openings if o["kind"] in ("door", "open")), None)
    cx, cz = room.cx, room.cz
    if op is not None:
        e = room.edge(op["side"])
        if op["side"] in ("N", "S"):
            px, pz = op["c"], e["a"][1]
        else:
            px, pz = e["a"][0], op["c"]
        nx, nz = e["n"]
        ex, ez = px + nx * 1.4, pz + nz * 1.4
        if not room.inside(ex, ez, 0.4):
            ex, ez = cx, cz
    else:
        ex, ez = room.cx, room.cz
    # aim at the point of the room farthest from the eye
    far = max(room.poly, key=lambda p: (p[0] - ex) ** 2 + (p[1] - ez) ** 2)
    tx = ex + (far[0] - ex) * 0.85
    tz = ez + (far[1] - ez) * 0.85
    return (ex, room.y + 1.62, ez), (tx, room.y + min(1.5, room.h * 0.45), tz)


def main(argv=None):
    global ONLY_DECKS
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--decks", default="", help="comma separated decks to furnish (default all); needs an explicit --out")
    ap.add_argument("--out", default=None, help="default godot/data/ship.json")
    a = ap.parse_args(argv)
    if a.decks:
        if a.out is None:
            ap.error("--decks leaves the other decks empty, so it must not overwrite godot/data/ship.json: pass --out PATH")
        try:
            ONLY_DECKS = {int(x) for x in a.decks.split(",")}
        except ValueError:
            ap.error("--decks takes comma separated deck numbers, e.g. 1,3")
    a.out = a.out or os.path.join(GODOT, "data", "ship.json")
    cat = Catalog(os.path.join(GODOT, "data", "catalog.json"))
    B = build(cat)
    S = B.ship
    rooms = [r.to_json() for r in S.rooms.values()]
    for r in rooms:
        r["mats"] = themes.theme_for(r["id"], r["dept"])
    total = sum(len(r["props"]) for r in rooms) + len(S.doors)
    bom_lines = sum(len(r["bom"]) for r in rooms)
    out = {"version": 2, "decks": S.decks, "hull": {str(k): [[x, z] for x, z in v] for k, v in S.hull.items()},
           "rooms": rooms, "doors": S.doors, "stairs": S.stairs,
           "cameras": S.cameras, "spawn": S.spawn, **exterior(S),
           "stats": {"rooms": len(rooms), "props": total, "bom_lines": bom_lines,
                     "distinct_models": sum(1 for v in cat.use.values() if v > 0), "catalog": len(cat.models)}}
    path = os.path.abspath(a.out)
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"{len(rooms)} rooms, {total} placements, {bom_lines} BOM lines, {out['stats']['distinct_models']}/{len(cat.models)} "
          f"models used -> {path} ({os.path.getsize(path) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
