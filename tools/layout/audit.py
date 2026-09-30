#!/usr/bin/env python3
"""Layout AUDIT for the starship interior (godot/data/ship.json, version 2; version 1 files are supported too).

    python tools/layout/audit.py [--ship PATH] [--catalog PATH] [--room ID] [--json] [--summary] [--max N]

Exit code 1 when any violation has severity "error".  Importable::

    from audit import audit, audit_stats
    violations = audit(ship, catalog, only_room=None)       # catalog: {model id: model dict}

A violation is ``{severity, rule, room, model, bom, msg, pos:[x, z]}`` (``other`` = second model of a pair).

Conventions: coordinates are Godot world metres (+X starboard, -Z bow); a prop's footprint is the catalog
bounds_min/bounds_max (xz) times ``scale`` rotated by ``yaw`` about Y (shiplib.rot / obb_corners); ``pos`` is the
model origin.  A wall item's *contact point* is its origin shifted along the wall by the model's local x centre; it lies on
the wall face (0.15 m inside the room polygon edge).  Version 1 files (``rect`` only) are audited with the rect as the
polygon, N/S/E/W edges derived from it, door/clear zones derived from the door/open openings (like Room.block_door), and
without the BOM / brief rules and the hull / stair rules (those data do not exist in v1).

RULES (error unless noted)
  footprint-overlap    floor props' oriented footprints overlap (> 1 cm2 and > 5 mm deep); a prop standing on another
                       (y == host y + top_y) and table-mount props are ignored.  Door/arch frames (b == "ARCH" or category door/doorframe) are ignored, and so are "flat" floor
                       props (<= 15 cm tall: rugs, floor markings, hatch plates) against non-flat ones (they also do not count
                       for density or door-clearance).
  outside-shell        floor-prop footprint corner outside the room polygon inset by the wall thickness 0.15 (tol 2 cm); wall
                       item contact point / table item origin / ceiling item origin or footprint corner outside the polygon.
  door-clearance       floor prop intersects a zone of kind door / clear.
  window-blocked       floor prop taller than 0.6 m whose footprint is within 0.5 m of a window span on the same wall.
  wall-item-overlap    two wall items overlap in (along, height) on the same wall, or a wall item overlaps a door/open/window
                       opening span (+/- 0.05 along the wall).
  wall-item-span       wall item extends beyond the ends of its wall edge (2 cm tol), is above the ceiling / below the floor.
  mount-mismatch       ceiling item not hanging at floor y + height (2 cm); wall item whose origin is > 0.6 m from any wall edge.
                       (floor models at the wrong y: see floating-floor)
  wall-floor-clash     wall item volume (bounds footprint extending 0..depth into the room) overlaps (> 1 cm2) the footprint of a
                       non-flat floor prop that is taller than the wall item's lowest point.
  ceiling-floor-clash  ceiling item footprint overlaps a non-flat floor prop whose top is above the ceiling item's lowest point.
  too-tall             floor prop higher than room height - 0.05 m.
  tabletop-host        table-mount prop stands on a host whose family is not in shiplib.SURFACE_HOSTS.
  wall-facing          wall-mount prop yaw not within 6 degrees of facing into the room from its wall edge.
  ceiling-overlap      two ceiling items overlap; ceiling item over a ceiling_hole; ceiling item y != floor y + height (2 cm).
  floating-floor       floor prop whose y != deck floor y (2 cm) and that does not stand on a host prop.
  table-support        table-mount prop must rest on a floor/table host with top_y whose top == the item's y (3 cm) and whose
                       footprint contains the item footprint (2 cm); otherwise floating / buried.
  hole-clash           floor prop footprint intersects a floor_hole.
  policy-category      prop family not allowed for the room by policy.allowed(room id) (ARCH frames skipped).
  unknown-room-policy  (warn, once per audit) room ids policy.py does not know; the policy rule is skipped for them.
  unknown-model        prop model id not in the catalog.
  walkable             capsule (r 0.32 = the player capsule, cell 0.2) flood fill from the deck's lobby: a room that is not reachable, has no free
                       floor, or a door/open mouth that is blocked.
  unreachable-pocket   (warn) >= 8 free cells of a room that cannot be reached from the lobby (pockets < 8 cells ignored).
  aisle-width          (warn) a passage inside a room narrower than 0.8 m between solid props / walls (grid approximation:
                       regions connected for a 0.32 m capsule but separated for a 0.40 m capsule).
  density              floor occupancy (footprint area / polygon area) > 0.60 error, > 0.45 warn (0.55 for depot, cargo, hangar,
                       armory); (warn) < 0.03 for rooms > 40 m2 (corridors, lobbies and stair towers excluded).
  duplicates           (warn) same model used > 6 times in one room (universal service families excluded).
  bom-line             (v2) every prop except doors/ARCH has ``b`` naming a bom line of its room; every bom line has >= 1
                       prop (or "empty": true; only an error when the room has other props), a title, and ``why`` >= 40 chars (warn when short); room has brief.purpose.
  lights               every room (not stair towers) has >= 1 light entry and >= 1 ceiling-mount ceilinglight prop.
  stair-consistency    ceiling_holes of a deck == floor_holes of the deck above it (same rects); flights lie inside their
                       tower room; flight A top y == landing y == flight B foot y (and run tops meet the next run).
  hull-containment     room polygon vertices inside the deck hull (3 cm tol); rooms of one deck overlap < 0.05 m2.
  opening-validity     door/open/window inside its wall span; door/open has a matching opening in the neighbour room
                       (openings on hull edges, or on side S of a room with forcefields, need no neighbour).
"""
import argparse
import collections
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hull as hulllib  # noqa: E402
import policy  # noqa: E402
from shiplib import WALL_T, rot, obb_corners, rect_poly, _point_in_poly, SURFACE_HOSTS  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CELL = 0.2
RADIUS = 0.32
AISLE_RADIUS = 0.40
MIN_OVERLAP_AREA = 1e-4          # 1 cm2
MIN_OVERLAP_DEPTH = 0.005        # 5 mm (positions are rounded to 1 mm in ship.json)
FLAT_H = 0.15                    # floor props this low are flat decals: furniture may stand on / across them
DEPOT_LIKE = ("depot", "cargo", "hangar", "armory")
CIRCULATION = ("cor", "lobby", "tower", "lift")


# ====================================================================== geometry helpers
def signed_area(poly):
    s = 0.0
    for i in range(len(poly)):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % len(poly)]
        s += x0 * z1 - x1 * z0
    return s / 2.0


def poly_area(poly):
    return abs(signed_area(poly)) if len(poly) >= 3 else 0.0


def centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def aabb_of(pts):
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def aabb_hit(a, b, m=0.0):
    return a[0] < b[2] + m and b[0] < a[2] + m and a[1] < b[3] + m and b[1] < a[3] + m


def sat_depth(a, b):
    """Minimum penetration depth of two convex polygons over all edge normals (<= 0 when they do not overlap)."""
    best = 1e9
    for poly in (a, b):
        n = len(poly)
        for i in range(n):
            ex, ez = poly[(i + 1) % n][0] - poly[i][0], poly[(i + 1) % n][1] - poly[i][1]
            ln = math.hypot(ex, ez)
            if ln < 1e-12:
                continue
            nx, nz = -ez / ln, ex / ln
            pa = [nx * p[0] + nz * p[1] for p in a]
            pb = [nx * p[0] + nz * p[1] for p in b]
            d = min(max(pa), max(pb)) - max(min(pa), min(pb))
            if d <= 0:
                return d
            best = min(best, d)
    return best


def overlap_area(a, b):
    c = hulllib.clip_convex(list(a), list(b))
    return poly_area(c) if len(c) >= 3 else 0.0


def polys_intersect(a, b):
    """(intersects?, area, depth) using the 1 cm2 / 5 mm thresholds."""
    if sat_depth(a, b) <= MIN_OVERLAP_DEPTH:
        return False, 0.0, 0.0
    ar = overlap_area(a, b)
    return ar > MIN_OVERLAP_AREA, ar, sat_depth(a, b)


def point_seg_dist(p, a, b):
    ex, ez = b[0] - a[0], b[1] - a[1]
    l2 = ex * ex + ez * ez
    t = 0.0 if l2 < 1e-12 else max(0.0, min(1.0, ((p[0] - a[0]) * ex + (p[1] - a[1]) * ez) / l2))
    return math.hypot(p[0] - (a[0] + t * ex), p[1] - (a[1] + t * ez))


def _seg_cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


def seg_poly_dist(a, b, poly):
    """Distance between segment ab and convex polygon (0 when they touch / overlap)."""
    if _point_in_poly(a, poly) or _point_in_poly(b, poly):
        return 0.0
    n = len(poly)
    best = 1e9
    for i in range(n):
        c, d = poly[i], poly[(i + 1) % n]
        if _seg_cross(a, b, c, d):
            return 0.0
        best = min(best, point_seg_dist(a, c, d), point_seg_dist(b, c, d), point_seg_dist(c, a, b), point_seg_dist(d, a, b))
    return best


def rect_dist_poly_overlap(rect, poly):
    return polys_intersect(poly, rect_poly(rect))


def r2(v):
    return round(float(v), 2)


# ====================================================================== model of a room / prop
class Prop:
    __slots__ = ("raw", "m", "mod", "mount", "cat", "x", "y", "z", "yaw", "sx", "sy", "sz", "b", "arch", "corners", "center",
                 "area", "aabb", "hy", "flat")

    def __init__(self, raw, mod):
        self.raw, self.mod = raw, mod
        self.m = raw["m"]
        self.mount = mod["mount"]
        self.cat = mod["category"]
        self.x, self.y, self.z = raw["pos"]
        self.yaw = raw.get("yaw", 0.0)
        s = raw.get("scale", 1.0)
        if isinstance(s, (list, tuple)):
            self.sx, self.sy, self.sz = (float(v) for v in (list(s) + [s[-1]] * 3)[:3])
        else:
            self.sx = self.sy = self.sz = float(s)
        self.b = raw.get("b")
        self.arch = self.b == "ARCH" or self.cat in ("door", "doorframe")
        lo, hi = mod["bounds_min"], mod["bounds_max"]
        lx, lz = (lo[0] + hi[0]) / 2 * self.sx, (lo[2] + hi[2]) / 2 * self.sz
        ox, oz = rot(lx, lz, self.yaw)
        self.center = (self.x + ox, self.z + oz)
        hx, hz = (hi[0] - lo[0]) / 2 * self.sx, (hi[2] - lo[2]) / 2 * self.sz
        self.corners = obb_corners(self.center[0], self.center[1], hx, hz, self.yaw)
        self.area = 4 * hx * hz
        self.aabb = aabb_of(self.corners)
        self.hy = mod["size"][1] * self.sy
        self.flat = self.mount == "floor" and self.hy <= FLAT_H      # rugs, floor markings, hatch plates

    @property
    def top(self):
        t = self.mod.get("top_y")
        return None if t is None else self.y + t * self.sy

    def pos2(self):
        return [r2(self.center[0]), r2(self.center[1])]


class Edge:
    def __init__(self, side, a, b, inward, hull=False):
        self.hull = bool(hull)
        self.side, self.a, self.b = side, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))
        ex, ez = self.b[0] - self.a[0], self.b[1] - self.a[1]
        self.len = math.hypot(ex, ez)
        self.u = (ex / self.len, ez / self.len) if self.len > 1e-9 else (1.0, 0.0)
        self.n = inward(self.a, self.b)
        self.yaw = math.degrees(math.atan2(self.n[0], self.n[1]))

    def along(self, pt):
        if self.side in ("N", "S"):
            return pt[0]
        if self.side in ("E", "W"):
            return pt[1]
        return (pt[0] - self.a[0]) * self.u[0] + (pt[1] - self.a[1]) * self.u[1]

    def span(self):
        if self.side in ("N", "S"):
            return (min(self.a[0], self.b[0]), max(self.a[0], self.b[0]))
        if self.side in ("E", "W"):
            return (min(self.a[1], self.b[1]), max(self.a[1], self.b[1]))
        return (0.0, self.len)

    def point(self, c):
        """World point on the wall line at opening coordinate c."""
        if self.side in ("N", "S"):
            return (c, self.a[1])
        if self.side in ("E", "W"):
            return (self.a[0], c)
        return (self.a[0] + self.u[0] * c, self.a[1] + self.u[1] * c)

    def seg(self, c, w):
        return self.point(c - w / 2), self.point(c + w / 2)


class Room:
    def __init__(self, raw, ctx):
        self.raw = raw
        self.id = raw["id"]
        self.deck = raw["deck"]
        self.h = raw.get("height", 3.4)
        self.y = ctx.deck_y.get(self.deck, 0.0)
        poly = raw.get("poly")
        if not poly:
            poly = rect_poly(raw["rect"])
        self.poly = [(float(p[0]), float(p[1])) for p in poly]
        self.area = poly_area(self.poly)
        ccw = signed_area(self.poly) > 0

        def inward(a, b):
            dx, dz = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dz) or 1.0
            return (-dz / ln, dx / ln) if ccw else (dz / ln, -dx / ln)
        self.edges = []
        if raw.get("edges"):
            for e in raw["edges"]:
                self.edges.append(Edge(e["side"], e["a"], e["b"], inward, e.get("hull", False)))
        else:
            r = raw["rect"]
            x0, z0, x1, z1 = r
            for side, a, b in (("N", (x0, z0), (x1, z0)), ("E", (x1, z0), (x1, z1)), ("S", (x1, z1), (x0, z1)), ("W", (x0, z1), (x0, z0))):
                self.edges.append(Edge(side, a, b, inward))
        self.edge_by = {e.side: e for e in self.edges}
        self.openings = raw.get("openings", [])
        self.props = []
        self.bbox = aabb_of(self.poly)
        self.key = policy.room_key(self.id)

    def is_circulation(self):
        return self.id.startswith(CIRCULATION)

    def inset_dist(self, pt):
        """Smallest distance of pt to the room's wall lines (positive inside)."""
        return min(e.n[0] * (pt[0] - e.a[0]) + e.n[1] * (pt[1] - e.a[1]) for e in self.edges)

    def zones(self):
        z = self.raw.get("zones")
        if z is not None:
            return [(zz["kind"], zz["rect"], zz.get("why", "")) for zz in z]
        out = []     # v1: derive from the openings like Room.block_door
        for o in self.openings:
            if o["kind"] not in ("door", "open"):
                continue
            e = self.edge_by.get(o["side"])
            if e is None or o["side"].startswith("D"):
                continue
            c, w = o["c"], o["w"]
            depth = 2.0 if o["kind"] == "door" else 1.0
            if o["side"] == "N":
                r = (c - w / 2 - 0.2, e.a[1], c + w / 2 + 0.2, e.a[1] + depth)
            elif o["side"] == "S":
                r = (c - w / 2 - 0.2, e.a[1] - depth, c + w / 2 + 0.2, e.a[1])
            elif o["side"] == "W":
                r = (e.a[0], c - w / 2 - 0.2, e.a[0] + depth, c + w / 2 + 0.2)
            else:
                r = (e.a[0] - depth, c - w / 2 - 0.2, e.a[0], c + w / 2 + 0.2)
            out.append(("door", list(r), "door clearance (derived from the opening)"))
        return out


class Ctx:
    def __init__(self, ship, catalog):
        self.ship, self.cat = ship, catalog
        self.deck_y = {d["id"]: d["y"] for d in ship.get("decks", [])}
        self.v2 = ship.get("version", 1) >= 2
        self.rooms = [Room(r, self) for r in ship["rooms"]]
        self.by_id = {r.id: r for r in self.rooms}
        self.out = []
        self.unknown_models = set()
        for room in self.rooms:
            for raw in room.raw.get("props", []):
                mod = catalog.get(raw["m"])
                if mod is None:
                    self.viol("error", "unknown-model", room, raw["m"], raw.get("b"), f"model '{raw['m']}' is not in the catalog",
                              [raw["pos"][0], raw["pos"][2]])
                    continue
                room.props.append(Prop(raw, mod))

    def viol(self, sev, rule, room, model, bom, msg, pos, other=None):
        v = {"severity": sev, "rule": rule, "room": room.id if hasattr(room, "id") else room, "model": model, "bom": bom,
             "msg": msg, "pos": [r2(pos[0]), r2(pos[1])]}
        if other:
            v["other"] = other
        self.out.append(v)


# ====================================================================== per-room rules
def stands_on(up, low):
    t = low.top
    return t is not None and up.y > low.y + 0.05 and abs(up.y - t) <= 0.03


def find_hosts(p, room):
    """Floor / table props whose footprint contains the footprint centre of p (excluding p)."""
    hosts = []
    for h in room.props:
        if h is p or h.arch or h.mount not in ("floor", "table") or h.mod.get("top_y") is None:
            continue
        if aabb_hit(h.aabb, p.aabb) and _point_in_poly(p.center, h.corners, -0.02):
            hosts.append(h)
    return hosts


def wall_geometry(p):
    """(contact point, along-half-width, y0 rel to world, y1) of a wall item."""
    lo, hi = p.mod["bounds_min"], p.mod["bounds_max"]
    lx = (lo[0] + hi[0]) / 2 * p.sx
    ox, oz = rot(lx, 0.0, p.yaw)
    contact = (p.x + ox, p.z + oz)
    hw = (hi[0] - lo[0]) / 2 * p.sx
    return contact, hw, p.y + lo[1] * p.sy, p.y + hi[1] * p.sy


def wall_edge_of(p, room):
    """Wall edge a wall item belongs to: (edge, distance, contact, facing_ok, yaw diff)."""
    contact, _, _, _ = wall_geometry(p)
    cand = sorted(((point_seg_dist(contact, e.a, e.b), e) for e in room.edges), key=lambda t: t[0])
    if not cand:
        return None, 1e9, contact, True, 0.0
    chosen = None
    for d, e in cand:
        if d > 0.6:
            break
        diff = (p.yaw - e.yaw + 180.0) % 360.0 - 180.0
        if abs(diff) <= 6.0:
            chosen = (e, d, diff)
            break
    if chosen is None:
        d, e = cand[0]
        chosen = (e, d, (p.yaw - e.yaw + 180.0) % 360.0 - 180.0)
    e, d, diff = chosen
    return e, d, contact, abs(diff) <= 6.0, diff


def check_room(ctx, room, allowed_keys):
    V = ctx.viol
    floor_props = [p for p in room.props if p.mount == "floor" and not p.arch]
    table_props = [p for p in room.props if p.mount == "table" and not p.arch]
    wall_props = [p for p in room.props if p.mount == "wall" and not p.arch]
    ceil_props = [p for p in room.props if p.mount == "ceiling" and not p.arch]
    zones = room.zones()
    holes = [h for h in room.raw.get("floor_holes", [])]
    choles = [h for h in room.raw.get("ceiling_holes", [])]

    # ---- footprint-overlap
    for i, a in enumerate(floor_props):
        for b in floor_props[i + 1:]:
            if not aabb_hit(a.aabb, b.aabb):
                continue
            if stands_on(a, b) or stands_on(b, a) or a.flat != b.flat:
                continue
            hit, ar, dp = polys_intersect(a.corners, b.corners)
            if hit:
                cx, cz = (a.center[0] + b.center[0]) / 2, (a.center[1] + b.center[1]) / 2
                V("error", "footprint-overlap", room, a.m, a.b,
                  f"{a.m} @({a.center[0]:.2f},{a.center[1]:.2f}) overlaps {b.m} @({b.center[0]:.2f},{b.center[1]:.2f}) "
                  f"by {ar:.3f} m2 (penetration {dp:.2f} m)", (cx, cz), other=b.m)

    # ---- outside-shell
    for p in floor_props:
        worst = None
        for c in p.corners:
            d = room.inset_dist(c)
            if d < WALL_T - 0.02 and (worst is None or d < worst[0]):
                worst = (d, c)
        if worst:
            V("error", "outside-shell", room, p.m, p.b,
              f"{p.m} footprint corner ({worst[1][0]:.2f},{worst[1][1]:.2f}) is {worst[0]:.2f} m from the wall line "
              f"(needs >= {WALL_T - 0.02:.2f}, inside the room)", p.center)
    for p in table_props:
        if room.inset_dist((p.x, p.z)) < -0.0:
            V("error", "outside-shell", room, p.m, p.b, f"table item {p.m} origin ({p.x:.2f},{p.z:.2f}) is outside the room polygon",
              (p.x, p.z))
    for p in ceil_props:
        bad = None
        if room.inset_dist((p.x, p.z)) < 0.0:
            bad = (p.x, p.z)
        else:
            for c in p.corners:
                if room.inset_dist(c) < -0.02:
                    bad = c
                    break
        if bad:
            V("error", "outside-shell", room, p.m, p.b,
              f"ceiling item {p.m} at ({bad[0]:.2f},{bad[1]:.2f}) is outside the room polygon", (p.x, p.z))

    # ---- door-clearance / hole-clash
    for p in floor_props:
        for kind, rect, why in ([] if p.flat else zones):
            rp = rect_poly(rect)
            if aabb_hit(p.aabb, aabb_of(rp)):
                hit, ar, dp = polys_intersect(p.corners, rp)
                if hit:
                    V("error", "door-clearance", room, p.m, p.b,
                      f"{p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) stands in {kind} zone {[round(v, 2) for v in rect]} ({why})", p.center)
        for h in holes:
            rp = rect_poly(h)
            if aabb_hit(p.aabb, aabb_of(rp)):
                hit, ar, dp = polys_intersect(p.corners, rp)
                if hit:
                    V("error", "hole-clash", room, p.m, p.b,
                      f"{p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) stands over floor hole {[round(v, 2) for v in h]}", p.center)

    # ---- window-blocked
    for o in room.openings:
        if o["kind"] != "window":
            continue
        e = room.edge_by.get(o["side"])
        if e is None:
            continue
        s0, s1 = e.seg(o["c"], o["w"])
        for p in floor_props:
            if p.hy <= 0.6:
                continue
            d = seg_poly_dist(s0, s1, p.corners)
            if d <= 0.5:
                V("error", "window-blocked", room, p.m, p.b,
                  f"{p.m} ({p.hy:.2f} m tall) @({p.center[0]:.2f},{p.center[1]:.2f}) is {d:.2f} m from the window on wall "
                  f"{o['side']} at c={o['c']:.2f} w={o['w']:.2f}", p.center)

    # ---- wall items
    items = []
    for p in wall_props:
        e, d, contact, face_ok, diff = wall_edge_of(p, room)
        _, hw, y0, y1 = wall_geometry(p)
        rel0, rel1 = y0 - room.y, y1 - room.y
        if room.inset_dist(contact) < -0.02:
            V("error", "outside-shell", room, p.m, p.b,
              f"wall item {p.m} contact point ({contact[0]:.2f},{contact[1]:.2f}) is outside the room polygon", contact)
        if e is None or d > 0.6:
            V("error", "mount-mismatch", room, p.m, p.b,
              f"wall item {p.m} @({contact[0]:.2f},{contact[1]:.2f}) is not on a wall (nearest wall {d:.2f} m away)", contact)
            continue
        if not face_ok:
            V("error", "wall-facing", room, p.m, p.b,
              f"wall item {p.m} yaw {p.yaw:.0f} but wall {e.side} faces into the room with yaw {e.yaw:.0f} (off by {diff:.0f} deg)", contact)
        al = e.along(contact)
        a0, a1 = al - hw, al + hw
        s0, s1 = e.span()
        if a0 < s0 - 0.02 or a1 > s1 + 0.02:
            V("error", "wall-item-span", room, p.m, p.b,
              f"wall item {p.m} spans {a0:.2f}..{a1:.2f} along wall {e.side} but the wall only runs {s0:.2f}..{s1:.2f}", contact)
        if rel1 > room.h + 0.02:
            V("error", "wall-item-span", room, p.m, p.b,
              f"wall item {p.m} top at {rel1:.2f} m is above the ceiling ({room.h:.2f} m) on wall {e.side}", contact)
        if rel0 < -0.02:
            V("error", "wall-item-span", room, p.m, p.b,
              f"wall item {p.m} bottom at {rel0:.2f} m is below the floor on wall {e.side}", contact)
        items.append((p, e, a0, a1, rel0, rel1, contact))
    for i, (p, e, a0, a1, h0, h1, ct) in enumerate(items):
        for (q, e2, b0, b1, g0, g1, ct2) in items[i + 1:]:
            if e2 is not e:
                continue
            if min(a1, b1) - max(a0, b0) > 0.01 and min(h1, g1) - max(h0, g0) > 0.01:
                V("error", "wall-item-overlap", room, p.m, p.b,
                  f"wall items {p.m} and {q.m} overlap on wall {e.side} (along {a0:.2f}..{a1:.2f} vs {b0:.2f}..{b1:.2f}, "
                  f"height {h0:.2f}..{h1:.2f} vs {g0:.2f}..{g1:.2f})", ct, other=q.m)
        for o in room.openings:
            if o["side"] != e.side:
                continue
            c0, c1 = o["c"] - o["w"] / 2 - 0.05, o["c"] + o["w"] / 2 + 0.05
            if min(a1, c1) - max(a0, c0) > 0.0 and min(h1, o["y1"]) - max(h0, o["y0"]) > 0.0:
                V("error", "wall-item-overlap", room, p.m, p.b,
                  f"wall item {p.m} (along {a0:.2f}..{a1:.2f}, height {h0:.2f}..{h1:.2f}) overlaps the {o['kind']} on wall "
                  f"{e.side} at c={o['c']:.2f} w={o['w']:.2f} (y {o['y0']:.2f}..{o['y1']:.2f})", ct)

    # ---- ceiling items
    for i, a in enumerate(ceil_props):
        for b in ceil_props[i + 1:]:
            if aabb_hit(a.aabb, b.aabb):
                hit, ar, dp = polys_intersect(a.corners, b.corners)
                if hit:
                    V("error", "ceiling-overlap", room, a.m, a.b,
                      f"ceiling items {a.m} @({a.center[0]:.2f},{a.center[1]:.2f}) and {b.m} @({b.center[0]:.2f},{b.center[1]:.2f}) "
                      f"overlap by {ar:.3f} m2", a.center, other=b.m)
        for h in choles:
            rp = rect_poly(h)
            if aabb_hit(a.aabb, aabb_of(rp)):
                hit, ar, dp = polys_intersect(a.corners, rp)
                if hit:
                    V("error", "ceiling-overlap", room, a.m, a.b,
                      f"ceiling item {a.m} @({a.center[0]:.2f},{a.center[1]:.2f}) is over ceiling hole {[round(v, 2) for v in h]}", a.center)
        want = room.y + room.h
        if abs(a.y - want) > 0.02:
            V("error", "mount-mismatch", room, a.m, a.b,
              f"ceiling item {a.m} hangs at y={a.y:.2f} but the ceiling is at {want:.2f}", a.center)

    # ---- floating-floor
    for p in floor_props:
        if abs(p.y - room.y) <= 0.02:
            continue
        ok = False
        for h in find_hosts(p, room):
            if abs(p.y - h.top) <= 0.03:
                ok = True
                break
        if not ok:
            V("error", "floating-floor", room, p.m, p.b,
              f"floor prop {p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) has y={p.y:.2f} but the deck floor is {room.y:.2f} and no prop supports it",
              p.center)

    # ---- table-support
    for p in table_props:
        hosts = find_hosts(p, room)
        good = False
        good_host = None
        best = None
        for h in hosts:
            dy = p.y - h.top
            inside = all(_point_in_poly(c, h.corners, -0.02) for c in p.corners)
            if abs(dy) <= 0.03 and inside:
                good = True
                good_host = h
                break
            if best is None or abs(dy) < abs(best[1]):
                best = (h, dy, inside)
        if good:
            if good_host is not None and good_host.cat not in SURFACE_HOSTS:
                V("error", "tabletop-host", room, p.m, p.b,
                  f"table item {p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) stands on {good_host.m} (family '{good_host.cat}') "
                  f"which is not a surface host (shiplib.SURFACE_HOSTS)", p.center, other=good_host.m)
            continue
        if best is None:
            V("error", "table-support", room, p.m, p.b,
              f"table item {p.m} @({p.center[0]:.2f},{p.center[1]:.2f}, y={p.y:.2f}) has no host prop with a flat top under it "
              f"(floating/buried)", p.center)
        else:
            h, dy, inside = best
            why = []
            if abs(dy) > 0.03:
                why.append(f"{'floating' if dy > 0 else 'buried'} {abs(dy):.2f} m (y={p.y:.2f}, host top {h.top:.2f})")
            if not inside:
                why.append("footprint overhangs the host")
            V("error", "table-support", room, p.m, p.b,
              f"table item {p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) on {h.m}: " + "; ".join(why), p.center, other=h.m)

    # ---- wall-floor-clash / ceiling-floor-clash / too-tall
    tall = [q for q in floor_props if not q.flat]
    for p in wall_props:
        lo, hi = p.mod["bounds_min"], p.mod["bounds_max"]
        pts = [(p.x + rot(x * p.sx, z * p.sz, p.yaw)[0], p.z + rot(x * p.sx, z * p.sz, p.yaw)[1])
               for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
        pts = [pts[0], pts[1], pts[3], pts[2]]
        box = aabb_of(pts)
        y_low = p.y + lo[1] * p.sy
        for q in tall:
            if not aabb_hit(box, q.aabb) or q.y + q.hy <= y_low:
                continue
            ar = overlap_area(pts, q.corners)
            if ar > MIN_OVERLAP_AREA:
                V("error", "wall-floor-clash", room, p.m, p.b,
                  f"wall item {p.m} (lowest point {y_low - room.y:.2f} m) collides with floor prop {q.m} ({q.hy:.2f} m tall) "
                  f"@({q.center[0]:.2f},{q.center[1]:.2f}); footprints overlap {ar:.3f} m2", q.center, other=q.m)
    for a in ceil_props:
        lowest = a.y + a.mod["bounds_min"][1] * a.sy
        for q in tall:
            if aabb_hit(a.aabb, q.aabb) and q.y + q.hy > lowest + 1e-6:
                ar = overlap_area(a.corners, q.corners)
                if ar > MIN_OVERLAP_AREA:
                    V("error", "ceiling-floor-clash", room, a.m, a.b,
                      f"ceiling item {a.m} (lowest point {lowest:.2f}) is hit by floor prop {q.m} whose top is {q.y + q.hy:.2f} "
                      f"@({q.center[0]:.2f},{q.center[1]:.2f})", q.center, other=q.m)
    for q in floor_props:
        if q.hy > room.h - 0.05:
            V("error", "too-tall", room, q.m, q.b,
              f"floor prop {q.m} is {q.hy:.2f} m tall but the room height is {room.h:.2f} m (max {room.h - 0.05:.2f})", q.center)

    # ---- policy-category
    if allowed_keys is not None:
        for p in room.props:
            if p.arch or p.cat in allowed_keys:
                continue
            V("error", "policy-category", room, p.m, p.b,
              f"family '{p.cat}' ({p.m}) is not allowed in {room.id} by policy.py", p.center)

    # ---- density
    foot = sum(p.area for p in floor_props if not p.flat)
    occ = foot / max(room.area, 1.0)
    thr = 0.55 if room.key in DEPOT_LIKE else 0.45
    if occ > 0.60:
        V("error", "density", room, None, None, f"floor occupancy {occ:.0%} exceeds 60% ({foot:.1f} of {room.area:.1f} m2)", room.poly[0])
    elif occ > thr:
        V("warn", "density", room, None, None, f"floor occupancy {occ:.0%} exceeds {thr:.0%} ({foot:.1f} of {room.area:.1f} m2)",
          centroid(room.poly))
    elif occ < 0.03 and room.area > 40 and not room.is_circulation():
        V("warn", "density", room, None, None, f"floor occupancy {occ:.1%} is very low for a {room.area:.0f} m2 room", centroid(room.poly))

    # ---- duplicates
    cnt = collections.Counter(p.m for p in room.props if not p.arch and p.cat not in policy.UNIVERSAL)
    for m, n in cnt.items():
        if n > 6:
            V("warn", "duplicates", room, m, None, f"{m} is used {n} times in {room.id}", centroid(room.poly))

    # ---- lights
    if not room.id.startswith(("tower", "lift")):
        if not room.raw.get("lights"):
            V("error", "lights", room, None, None, f"room {room.id} has no light entries", centroid(room.poly))
        if not any(p.mount == "ceiling" and p.cat == "ceilinglight" for p in room.props):
            V("error", "lights", room, None, None, f"room {room.id} has no ceiling-mounted light fixture (category ceilinglight)",
              centroid(room.poly))

    # ---- bom-line
    if ctx.v2:
        codes = {}
        for ln in room.raw.get("bom", []) or []:
            codes[ln.get("code")] = ln
        used = collections.Counter()
        for p in room.props:
            if p.arch or p.cat == "door":
                continue
            if not p.b:
                V("error", "bom-line", room, p.m, None, f"{p.m} @({p.center[0]:.2f},{p.center[1]:.2f}) has no BOM line (b)", p.center)
            elif p.b not in codes:
                V("error", "bom-line", room, p.m, p.b, f"{p.m} refers to unknown BOM line '{p.b}'", p.center)
            else:
                used[p.b] += 1
        for code, ln in codes.items():
            if not (ln.get("title") or "").strip():
                V("error", "bom-line", room, None, code, f"BOM line {code} has an empty title", centroid(room.poly))
            why = (ln.get("why") or "").strip()
            if len(why) < 40:
                V("warn", "bom-line", room, None, code, f"BOM line {code} '{ln.get('title')}': why is only {len(why)} chars (< 40)",
                  centroid(room.poly))
            if not used[code] and not ln.get("empty") and any(used.values()):
                V("error", "bom-line", room, None, code, f"BOM line {code} '{ln.get('title')}' has no props (mark it \"empty\": true if intended)",
                  centroid(room.poly))
        if not (room.raw.get("brief") or {}).get("purpose"):
            V("error", "bom-line", room, None, None, f"room {room.id} has no brief.purpose", centroid(room.poly))

    # ---- opening-validity (span)
    for o in room.openings:
        e = room.edge_by.get(o["side"])
        if e is None:
            V("error", "opening-validity", room, None, None, f"{o['kind']} on side {o['side']} but {room.id} has no such wall", centroid(room.poly))
            continue
        s0, s1 = e.span()
        if o["c"] - o["w"] / 2 < s0 - 0.01 or o["c"] + o["w"] / 2 > s1 + 0.01:
            V("error", "opening-validity", room, None, None,
              f"{o['kind']} on wall {o['side']} at c={o['c']:.2f} w={o['w']:.2f} exceeds the wall span {s0:.2f}..{s1:.2f}", e.point(o["c"]))


# ====================================================================== walkability
class Grid:
    def __init__(self, rooms, radius):
        xs = [p[0] for r in rooms for p in r.poly]
        zs = [p[1] for r in rooms for p in r.poly]
        self.x0, self.z0 = min(xs) - 1.0, min(zs) - 1.0
        self.nx = int((max(xs) + 1.0 - self.x0) / CELL) + 2
        self.nz = int((max(zs) + 1.0 - self.z0) / CELL) + 2
        self.free = bytearray(self.nx * self.nz)
        self.owner = [0] * (self.nx * self.nz)
        self.radius = radius

    def cell_range(self, x0, z0, x1, z1):
        i0 = max(int(math.floor((x0 - self.x0) / CELL)), 0)
        i1 = min(int(math.ceil((x1 - self.x0) / CELL)), self.nx - 1)
        j0 = max(int(math.floor((z0 - self.z0) / CELL)), 0)
        j1 = min(int(math.ceil((z1 - self.z0) / CELL)), self.nz - 1)
        return i0, i1, j0, j1

    def idx(self, x, z):
        return int(round((x - self.x0) / CELL)), int(round((z - self.z0) / CELL))

    def xy(self, i, j):
        return self.x0 + i * CELL, self.z0 + j * CELL


def build_grid(ctx, rooms, radius):
    g = Grid(rooms, radius)
    inset = WALL_T + radius
    for ri, room in enumerate(rooms, 1):
        i0, i1, j0, j1 = g.cell_range(*room.bbox)
        for i in range(i0, i1 + 1):
            x = g.x0 + i * CELL
            for j in range(j0, j1 + 1):
                z = g.z0 + j * CELL
                if room.inset_dist((x, z)) >= inset - 1e-9:
                    k = i * g.nz + j
                    g.free[k] = 1
                    g.owner[k] = ri
    for room in rooms:          # doors / openings are passages through the wall
        for o in room.openings:
            if o["kind"] == "window":
                continue
            e = room.edge_by.get(o["side"])
            if e is None:
                continue
            hw = o["w"] / 2 - 0.2
            P = e.point(o["c"])
            n = e.n
            u = (-n[1], n[0])
            th = WALL_T + radius
            xs = [P[0] + su * u[0] * hw + sn * n[0] * th for su in (-1, 1) for sn in (-1, 1)]
            zs = [P[1] + su * u[1] * hw + sn * n[1] * th for su in (-1, 1) for sn in (-1, 1)]
            i0, i1, j0, j1 = g.cell_range(min(xs), min(zs), max(xs), max(zs))
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    x, z = g.xy(i, j)
                    dx, dz = x - P[0], z - P[1]
                    if abs(dx * u[0] + dz * u[1]) <= hw + 1e-9 and abs(dx * n[0] + dz * n[1]) <= th + 1e-9:
                        g.free[i * g.nz + j] = 1
    for room in rooms:          # stair wells / floor holes
        for h in room.raw.get("floor_holes", []):
            i0, i1, j0, j1 = g.cell_range(*h)
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    x, z = g.xy(i, j)
                    if h[0] < x < h[2] and h[1] < z < h[3]:
                        g.free[i * g.nz + j] = 0
    for room in rooms:          # solid props
        for p in room.props:
            m = p.mod
            if p.arch or m["mount"] != "floor" or abs(p.y - room.y) > 0.3:
                continue
            if not (p.raw.get("solid", m["solid"]) and m["size"][1] > 0.35 and (m["size"][0] > 0.25 or m["size"][2] > 0.25)):
                continue
            lo, hi = m["bounds_min"], m["bounds_max"]
            hx, hz = (hi[0] - lo[0]) / 2 * p.sx * 0.95, (hi[2] - lo[2]) / 2 * p.sz * 0.95
            cx, cz = p.center
            i0, i1, j0, j1 = g.cell_range(p.aabb[0] - radius, p.aabb[1] - radius, p.aabb[2] + radius, p.aabb[3] + radius)
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    x, z = g.xy(i, j)
                    lx, lz = rot(x - cx, z - cz, -p.yaw)
                    if math.hypot(max(abs(lx) - hx, 0.0), max(abs(lz) - hz, 0.0)) <= radius + 1e-9:
                        g.free[i * g.nz + j] = 0
    return g


def components(g, cells):
    """Connected components (4-neighbourhood) of the set `cells` (indices) -> list of lists."""
    cells = set(cells)
    comps = []
    nz = g.nz
    while cells:
        s = cells.pop()
        comp = [s]
        stack = [s]
        while stack:
            k = stack.pop()
            for d in (nz, -nz, 1, -1):
                q = k + d
                if q in cells:
                    cells.discard(q)
                    comp.append(q)
                    stack.append(q)
        comps.append(comp)
    return comps


def flood(g, start):
    seen = {start}
    stack = [start]
    free, nz, total = g.free, g.nz, g.nx * g.nz
    while stack:
        k = stack.pop()
        for d in (nz, -nz, 1, -1):
            q = k + d
            if 0 <= q < total and free[q] and q not in seen:
                seen.add(q)
                stack.append(q)
    return seen


def check_walkable(ctx, decks=None):
    V = ctx.viol
    for deck in sorted({r.deck for r in ctx.rooms}):
        if decks is not None and deck not in decks:
            continue
        rooms = [r for r in ctx.rooms if r.deck == deck]
        g = build_grid(ctx, rooms, RADIUS)
        lobby = next((r for r in rooms if r.id.startswith("lobby")), rooms[0])
        li = rooms.index(lobby) + 1
        cx, cz = centroid(lobby.poly)
        ci, cj = g.idx(cx, cz)
        cand = [(((k // g.nz) - ci) ** 2 + ((k % g.nz) - cj) ** 2, k) for k in range(len(g.owner)) if g.owner[k] == li and g.free[k]]
        if not cand:
            V("error", "walkable", lobby, None, None, f"no free floor in the lobby {lobby.id} of deck {deck}: nothing is reachable", centroid(lobby.poly))
            continue
        start = min(cand)[1]
        seen = flood(g, start)
        by_room = collections.defaultdict(list)
        for k, o in enumerate(g.owner):
            if o and g.free[k]:
                by_room[o].append(k)
        for ri, room in enumerate(rooms, 1):
            cells = by_room.get(ri, [])
            reach = [k for k in cells if k in seen]
            if not cells:
                V("error", "walkable", room, None, None, f"room {room.id} has no free walkable floor (capsule r={RADIUS})", centroid(room.poly))
                continue
            if len(reach) <= 12:
                V("error", "walkable", room, None, None,
                  f"room {room.id} is not reachable on foot from {lobby.id} ({len(reach)} of {len(cells)} free cells reachable)",
                  g.xy(cells[0] // g.nz, cells[0] % g.nz))
            else:
                for comp in components(g, [k for k in cells if k not in seen]):
                    if len(comp) >= 8:
                        k = comp[0]
                        V("warn", "unreachable-pocket", room, None, None,
                          f"{len(comp)} free cells ({len(comp) * CELL * CELL:.1f} m2) of {room.id} near ({g.xy(k // g.nz, k % g.nz)[0]:.1f},"
                          f"{g.xy(k // g.nz, k % g.nz)[1]:.1f}) cannot be reached from the door", g.xy(k // g.nz, k % g.nz))
            for o in room.openings:
                if o["kind"] == "window":
                    continue
                e = room.edge_by.get(o["side"])
                if e is None:
                    continue
                P = e.point(o["c"])
                u = (-e.n[1], e.n[0])
                hw = o["w"] / 2 - 0.2
                ok = False
                t = -hw
                while t <= hw + 1e-9:
                    x = P[0] + e.n[0] * (WALL_T + RADIUS + 0.15) + u[0] * t
                    z = P[1] + e.n[1] * (WALL_T + RADIUS + 0.15) + u[1] * t
                    i, j = g.idx(x, z)
                    if 0 <= i < g.nx and 0 <= j < g.nz and g.free[i * g.nz + j]:
                        ok = True
                        break
                    t += CELL
                if not ok:
                    V("error", "walkable", room, None, None,
                      f"the {o['kind']} on wall {o['side']} at c={o['c']:.2f} of {room.id} is blocked on the room side (props within the capsule clearance)",
                      P)
        # ---- aisle-width: connected for the player capsule but split for r=0.40
        g4 = build_grid(ctx, rooms, AISLE_RADIUS)
        for ri, room in enumerate(rooms, 1):
            c3 = [k for k in by_room.get(ri, [])]
            c4 = [k for k, o in enumerate(g4.owner) if o == ri and g4.free[k]] if c3 else []
            if not c4:
                continue
            comps4 = [c for c in components(g4, c4) if len(c) >= 8]
            if len(comps4) < 2:
                continue
            label = {}
            for ci_, comp in enumerate(comps4):
                for k in comp:
                    label[k] = ci_
            for comp3 in components(g, c3):
                ids = {label[k] for k in comp3 if k in label}
                if len(ids) < 2:
                    continue
                spot = None
                for k in comp3:
                    if k in label:
                        continue
                    nb = {label.get(k + d) for d in (g.nz, -g.nz, 1, -1, 2 * g.nz, -2 * g.nz, 2, -2)} - {None}
                    if len(nb) >= 2:
                        spot = g.xy(k // g.nz, k % g.nz)
                        break
                if spot is None:
                    k = comp3[0]
                    spot = g.xy(k // g.nz, k % g.nz)
                V("warn", "aisle-width", room, None, None,
                  f"passage narrower than {2 * AISLE_RADIUS:.1f} m between solid props near ({spot[0]:.1f},{spot[1]:.1f}) in {room.id}", spot)
                break


# ====================================================================== ship level rules
def rect_match(r, rects, tol=0.02):
    return any(all(abs(a - b) <= tol for a, b in zip(r, q)) for q in rects)


def check_ship(ctx):
    V = ctx.viol
    ship = ctx.ship
    decks = sorted(ship.get("decks", []), key=lambda d: -d["y"])
    # ---- stair-consistency: holes
    def holes(deck_id, key):
        out = []
        for r in ctx.rooms:
            if r.deck == deck_id:
                out += [(r, h) for h in r.raw.get(key, [])]
        return out
    for i, d in enumerate(decks):
        floor_h = holes(d["id"], "floor_holes")
        ceil_h = holes(d["id"], "ceiling_holes")
        above = decks[i - 1] if i > 0 else None
        below = decks[i + 1] if i + 1 < len(decks) else None
        up_floor = [h for _, h in holes(above["id"], "floor_holes")] if above else []
        for r, h in ceil_h:
            if not rect_match(h, up_floor):
                V("error", "stair-consistency", r, None, None,
                  f"ceiling hole {[round(v, 2) for v in h]} of deck {d['id']} has no equal floor hole on the deck above"
                  f"{'' if above else ' (there is none)'}", ((h[0] + h[2]) / 2, (h[1] + h[3]) / 2))
        for r, h in floor_h:
            target = [hh for _, hh in holes(below["id"], "ceiling_holes")] if below else []
            if not rect_match(h, target):
                V("error", "stair-consistency", r, None, None,
                  f"floor hole {[round(v, 2) for v in h]} of deck {d['id']} has no equal ceiling hole on the deck below"
                  f"{'' if below else ' (there is none)'}", ((h[0] + h[2]) / 2, (h[1] + h[3]) / 2))
    # ---- stair-consistency: flights
    for st in ship.get("stairs", []) or []:
        runs = st.get("runs", [])
        for ri, run in enumerate(runs):
            fl = run.get("flights", [])
            land = run.get("landing") or {}
            lo = run.get("deck_lo")
            tower = None
            if fl:
                fx, fz = fl[0]["pos"][0], fl[0]["pos"][2]
                for r in ctx.rooms:
                    if r.deck == lo and _point_in_poly((fx, fz), r.poly, -0.3):
                        tower = r
                        break
            for f in fl:
                ux, uz = -math.sin(math.radians(f["yaw"])), -math.cos(math.radians(f["yaw"]))
                hw = st.get("width", 1.4) / 2
                x0, z0 = f["pos"][0], f["pos"][2]
                x1, z1 = x0 + ux * f["run"], z0 + uz * f["run"]
                pts = [(x0 - uz * hw, z0 + ux * hw), (x0 + uz * hw, z0 - ux * hw), (x1 + uz * hw, z1 - ux * hw), (x1 - uz * hw, z1 + ux * hw)]
                if tower is None:
                    V("error", "stair-consistency", None, None, None,
                      f"flight of {st.get('id')} at ({x0:.2f},{z0:.2f}) is not inside any room of deck {lo}", (x0, z0))
                    break
                bad = [c for c in pts if not _point_in_poly(c, tower.poly, -0.02)]
                if bad:
                    V("error", "stair-consistency", tower, None, None,
                      f"flight of {st.get('id')} ({x0:.2f},{z0:.2f})->({x1:.2f},{z1:.2f}) sticks out of {tower.id}'s polygon at "
                      f"({bad[0][0]:.2f},{bad[0][1]:.2f})", (x0, z0))
            if len(fl) >= 2 and land:
                a, b = fl[0], fl[1]
                top = a["pos"][1] + a["rise"]
                if abs(top - land["y"]) > 0.01 or abs(b["pos"][1] - land["y"]) > 0.01:
                    V("error", "stair-consistency", tower, None, None,
                      f"{st.get('id')} run {lo}->{run.get('deck_hi')}: flight A top y {top:.3f}, landing y {land['y']:.3f}, "
                      f"flight B foot y {b['pos'][1]:.3f} do not agree", (a["pos"][0], a["pos"][2]))
                lr = land.get("rect")
                if lr:
                    ux, uz = -math.sin(math.radians(a["yaw"])), -math.cos(math.radians(a["yaw"]))
                    tx, tz = a["pos"][0] + ux * a["run"], a["pos"][2] + uz * a["run"]
                    dxl = max(lr[0] - tx, 0, tx - lr[2])
                    dzl = max(lr[1] - tz, 0, tz - lr[3])
                    if math.hypot(dxl, dzl) > 0.35:
                        V("error", "stair-consistency", tower, None, None,
                          f"{st.get('id')}: flight A ends at ({tx:.2f},{tz:.2f}), {math.hypot(dxl, dzl):.2f} m from the landing {lr}", (tx, tz))
                    bx, bz = b["pos"][0], b["pos"][2]
                    if bx < lr[0] - 0.02 or bx > lr[2] + 0.02 or bz < lr[1] - 0.02 or bz > lr[3] + 0.02:
                        V("error", "stair-consistency", tower, None, None,
                          f"{st.get('id')}: flight B starts at ({bx:.2f},{bz:.2f}) outside the landing {lr}", (bx, bz))
            if fl and ri + 1 < len(runs) and runs[ri + 1].get("flights"):
                btop = fl[-1]["pos"][1] + fl[-1]["rise"]
                nxt = runs[ri + 1]["flights"][0]["pos"][1]
                if abs(btop - nxt) > 0.01:
                    V("error", "stair-consistency", tower, None, None,
                      f"{st.get('id')}: run {lo}->{run.get('deck_hi')} ends at y {btop:.3f} but the next run starts at y {nxt:.3f}",
                      (fl[-1]["pos"][0], fl[-1]["pos"][2]))
            if fl:
                want_lo, want_hi = ctx.deck_y.get(lo), ctx.deck_y.get(run.get("deck_hi"))
                if want_lo is not None and abs(fl[0]["pos"][1] - want_lo) > 0.01:
                    V("error", "stair-consistency", tower, None, None,
                      f"{st.get('id')}: first flight starts at y {fl[0]['pos'][1]:.3f}, deck {lo} floor is {want_lo:.3f}", (fl[0]["pos"][0], fl[0]["pos"][2]))
                if want_hi is not None and abs(fl[-1]["pos"][1] + fl[-1]["rise"] - want_hi) > 0.01:
                    V("error", "stair-consistency", tower, None, None,
                      f"{st.get('id')}: last flight ends at y {fl[-1]['pos'][1] + fl[-1]['rise']:.3f}, deck {run.get('deck_hi')} floor is {want_hi:.3f}",
                      (fl[-1]["pos"][0], fl[-1]["pos"][2]))

    # ---- hull-containment
    hulls = ship.get("hull") or {}
    for room in ctx.rooms:
        hpoly = hulls.get(str(room.deck))
        if not hpoly:
            continue
        hp = [tuple(p) for p in hpoly]
        for v in room.poly:
            if not _point_in_poly(v, hp, -0.03):
                V("error", "hull-containment", room, None, None, f"room {room.id} vertex ({v[0]:.2f},{v[1]:.2f}) lies outside the deck {room.deck} hull",
                  v)
                break
    for deck in {r.deck for r in ctx.rooms}:
        rs = [r for r in ctx.rooms if r.deck == deck]
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                if not aabb_hit(a.bbox, b.bbox):
                    continue
                ar = overlap_area(a.poly, b.poly) if len(a.poly) >= 3 and len(b.poly) >= 3 else 0.0
                if ar > 0.05:
                    V("error", "hull-containment", a, None, None, f"rooms {a.id} and {b.id} overlap by {ar:.2f} m2", centroid(a.poly), other=b.id)

    # ---- opening-validity: neighbour match
    per_deck = collections.defaultdict(list)
    for room in ctx.rooms:
        for o in room.openings:
            if o["kind"] in ("door", "open"):
                e = room.edge_by.get(o["side"])
                if e is not None:
                    per_deck[room.deck].append((room, o, e.point(o["c"]), e))
    for deck, lst in per_deck.items():
        for room, o, P, e in lst:
            if e.hull or (e.side == "S" and room.raw.get("forcefields")):
                continue          # opening to space (hangar stern): no neighbour room
            if not any(r2_ is not room and abs(P2[0] - P[0]) <= 0.05 and abs(P2[1] - P[1]) <= 0.05 for r2_, o2, P2, _e in lst):
                V("error", "opening-validity", room, None, None,
                  f"{o['kind']} on wall {o['side']} at c={o['c']:.2f} ({P[0]:.2f},{P[1]:.2f}) has no matching opening in a neighbouring room", P)


# ====================================================================== public API
RULES = ["footprint-overlap", "outside-shell", "door-clearance", "window-blocked", "wall-item-overlap", "wall-item-span", "wall-facing",
         "ceiling-overlap", "floating-floor", "table-support", "hole-clash", "policy-category", "unknown-room-policy", "unknown-model",
         "walkable", "unreachable-pocket", "aisle-width", "density", "duplicates", "bom-line", "lights", "stair-consistency",
         "hull-containment", "opening-validity", "wall-floor-clash", "ceiling-floor-clash", "too-tall", "tabletop-host", "mount-mismatch"]


def audit(ship, catalog, only_room=None, rules=None):
    """All violations (optionally only room `only_room`, only rule ids in `rules`)."""
    ctx = Ctx(ship, catalog)
    unknown = sorted({r.id for r in ctx.rooms if r.key not in policy.ROOM})
    for room in ctx.rooms:
        if only_room and room.id != only_room:
            continue
        allowed_keys = policy.allowed(room.id) if room.key in policy.ROOM else None
        check_room(ctx, room, allowed_keys)
    check_ship(ctx)
    decks = None
    if only_room:
        r = ctx.by_id.get(only_room)
        decks = {r.deck} if r else set()
    check_walkable(ctx, decks)
    if unknown:
        ctx.out.append({"severity": "warn", "rule": "unknown-room-policy", "room": None, "model": None, "bom": None,
                        "msg": "policy.py has no entry for room id(s) " + ", ".join(unknown) + "; the policy-category rule was skipped for them",
                        "pos": [0.0, 0.0]})
    out = ctx.out
    if only_room:
        out = [v for v in out if v["room"] == only_room]
    if rules is not None:
        rules = set(rules)
        out = [v for v in out if v["rule"] in rules]
    out.sort(key=lambda v: (v["severity"] != "error", v["rule"], str(v["room"]), v["pos"]))
    return out


def audit_stats(ship, catalog):
    """Per-room statistics: props, occupancy, area, distinct models (for docs)."""
    ctx = Ctx(ship, catalog)
    rows = []
    for room in ctx.rooms:
        fl = [p for p in room.props if p.mount == "floor" and not p.arch]
        rows.append({
            "room": room.id, "deck": room.deck, "area": round(room.area, 1),
            "props": sum(1 for p in room.props if not p.arch), "floor_props": len(fl),
            "wall_props": sum(1 for p in room.props if p.mount == "wall"),
            "ceiling_props": sum(1 for p in room.props if p.mount == "ceiling"),
            "table_props": sum(1 for p in room.props if p.mount == "table"),
            "occupancy": round(sum(p.area for p in fl) / max(room.area, 1.0), 3),
            "distinct_models": len({p.m for p in room.props if not p.arch}),
            "bom_lines": len(room.raw.get("bom", []) or []),
        })
    return rows


# ====================================================================== CLI
def load_catalog(path):
    with open(path) as f:
        d = json.load(f)
    return {m["id"]: m for m in (d["models"] if isinstance(d, dict) else d)}


def summary_table(viol):
    rules = collections.OrderedDict()
    for v in viol:
        r = rules.setdefault(v["rule"], {"error": 0, "warn": 0, "rooms": collections.Counter()})
        r[v["severity"]] += 1
        r["rooms"][v["room"] or "-"] += 1
    lines = [f"{'rule':<22}{'err':>5}{'warn':>6}  rooms (count)"]
    for rule, r in sorted(rules.items()):
        rooms = ", ".join(f"{k}:{n}" for k, n in r["rooms"].most_common())
        lines.append(f"{rule:<22}{r['error']:>5}{r['warn']:>6}  {rooms}")
    e = sum(1 for v in viol if v["severity"] == "error")
    lines.append(f"{'TOTAL':<22}{e:>5}{len(viol) - e:>6}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ship", default=os.path.join(ROOT, "godot", "data", "ship.json"))
    ap.add_argument("--catalog", default=os.path.join(ROOT, "godot", "data", "catalog.json"))
    ap.add_argument("--room", default=None)
    ap.add_argument("--json", action="store_true", help="print the violations as JSON")
    ap.add_argument("--summary", action="store_true", help="print a rule x room table instead of every violation")
    ap.add_argument("--max", type=int, default=200, help="print at most N violations (0 = all)")
    a = ap.parse_args(argv)
    with open(a.ship) as f:
        ship = json.load(f)
    viol = audit(ship, load_catalog(a.catalog), a.room)
    errors = sum(1 for v in viol if v["severity"] == "error")
    if a.json:
        print(json.dumps(viol if not a.max else viol[:a.max], indent=1))
    elif a.summary:
        print(summary_table(viol))
    else:
        shown = viol if not a.max else viol[:a.max]
        for v in shown:
            print(f"{v['severity'].upper():5} {v['rule']:<18} [{v['room']}] {('model=' + v['model'] + ' ') if v['model'] else ''}"
                  f"{('bom=' + v['bom'] + ' ') if v['bom'] else ''}@({v['pos'][0]},{v['pos'][1]}): {v['msg']}")
        if len(viol) > len(shown):
            print(f"... {len(viol) - len(shown)} more (use --max 0, --room ID or --summary)")
        print(f"{errors} errors, {len(viol) - errors} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
