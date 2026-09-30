"""Helpers for arranging the component library inside the starship.

Coordinates are Godot world coordinates: +X starboard, +Y up, -Z towards the bow.
A prop with yaw 0 faces +Z (glTF front); yaw 180 faces the bow, +90 faces +X, -90 faces -X.

Rooms are CONVEX POLYGONS: a nominal rectangle (the drafting grid) clipped by the deck's hull
outline (see hull.py).  Mid-ship rooms stay rectangular; rooms at the bow and stern get the
tapered, streamlined walls of the hull.  Every wall of a room is an *edge*:

    "N" "S" "E" "W"   axis-aligned edges (north = the -Z side); `c` of an opening is the absolute X (N/S) or Z (E/W)
    "D0" "D1" ...      diagonal edges (hull facets); `c` is the distance along the edge from its start point

Every placement can be attributed to a *bill-of-materials line* (``Room.line``) that records why the
item is in the room; docs/BOM.md and the drawings are generated from that information.
"""
import json
import math
import random
import zlib

import hull as hulllib

WALL_T = 0.15          # must match ship_builder.gd
DOOR_W = 2.36          # wall cut for a door (2.0 opening + frame)
DOOR_H = 2.76
SIDES = ("N", "S", "E", "W")
FACE_YAW = {"N": 0.0, "S": 180.0, "W": 90.0, "E": -90.0}   # yaw that makes a prop face into the room
EPS = 1e-6


def rot(x, z, yaw):
    """Rotate local (x, z) by yaw degrees about +Y (Godot convention)."""
    t = math.radians(yaw)
    c, s = math.cos(t), math.sin(t)
    return (c * x + s * z, -s * x + c * z)


def obb_corners(cx, cz, hx, hz, yaw):
    """Corners of a rectangle with half extents (hx, hz) in prop-local axes rotated by yaw."""
    return [(cx + rot(sx * hx, sz * hz, yaw)[0], cz + rot(sx * hx, sz * hz, yaw)[1])
            for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _axes(pts):
    out = []
    for i in range(len(pts)):
        ax, az = pts[i]
        bx, bz = pts[(i + 1) % len(pts)]
        ex, ez = bx - ax, bz - az
        n = math.hypot(ex, ez) or 1.0
        out.append((-ez / n, ex / n))
    return out


def polys_overlap(a, b, margin=0.0):
    """Separating-axis test for two convex polygons; `margin` demands that much clearance."""
    for axes in (_axes(a), _axes(b)):
        for (nx, nz) in axes:
            pa = [nx * p[0] + nz * p[1] for p in a]
            pb = [nx * p[0] + nz * p[1] for p in b]
            if max(pa) + margin <= min(pb) + 1e-9 or max(pb) + margin <= min(pa) + 1e-9:
                return False
    return True


# families whose flat top is a real work surface (table items may stand on these and nothing else)
SURFACE_HOSTS = {"table", "desk", "labbench", "galley", "console", "cabinet", "storagebin", "engtool", "medcabinet", "medbed",
                 "rack", "cell", "commsunit", "shelving", "surgical", "holo", "storage"}


def rect_poly(r):
    x0, z0, x1, z1 = r
    return [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]


def poly_area(poly):
    return hulllib.area(poly)


def poly_centroid(poly):
    a = cx = cz = 0.0
    for i in range(len(poly)):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % len(poly)]
        w = x0 * z1 - x1 * z0
        a += w
        cx += (x0 + x1) * w
        cz += (z0 + z1) * w
    if abs(a) < 1e-9:
        return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    return (cx / (3 * a), cz / (3 * a))


class Catalog:
    def __init__(self, path):
        with open(path) as f:
            d = json.load(f)
        self.models = {m["id"]: m for m in d["models"]}
        self.by_cat = {}
        for m in d["models"]:
            self.by_cat.setdefault(m["category"], []).append(m)
        self.use = {k: 0 for k in self.models}
        self.rng = random.Random(1701)
        self.missing_labels = set()     # (category, label) pairs that matched no model (pick fell back to the whole family)

    def pick(self, cat, pred=None, label=None, rng=None):
        """Least-used model of a category (random tie-break), optionally filtered.

        `label` narrows to models whose id contains the label (or any of a list of labels); if no
        model matches, the whole family is used and the miss is recorded in `missing_labels` (the generator
        reports it, the tests fail on it) instead of silently giving a random model."""
        rng = rng or self.rng
        cands = self.by_cat.get(cat, [])
        if label is not None:
            wanted = [label] if isinstance(label, str) else list(label)
            hit = [c for c in cands if any(l in c["id"] for l in wanted)]
            if not hit and cands:
                self.missing_labels.add((cat, ",".join(wanted)))
            cands = hit or cands
        if pred:
            cands = [c for c in cands if pred(c)]
        if not cands:
            return None
        cands = sorted(cands, key=lambda c: (self.use[c["id"]], rng.random()))
        return cands[0]

    def pick_any(self, cats, pred=None, rng=None):
        rng = rng or self.rng
        pool = []
        for c in cats:
            pool += self.by_cat.get(c, [])
        if pred:
            pool = [c for c in pool if pred(c)]
        if not pool:
            return None
        pool.sort(key=lambda c: (self.use[c["id"]], rng.random()))
        return pool[0]

    def unused(self):
        return [self.models[k] for k, v in self.use.items() if v == 0]


class Ship:
    def __init__(self, cat):
        self.cat = cat
        self.rooms = {}
        self.decks = []
        self.doors = []
        self.stairs = []
        self.cameras = []
        self.spawn = None
        self.hull = {}

    def deck_y(self, deck):
        for d in self.decks:
            if d["id"] == deck:
                return d["y"]
        raise KeyError(f"unknown deck {deck!r}; decks are {[d['id'] for d in self.decks]}")

    def add_room(self, room):
        self.rooms[room.id] = room
        return room

    # --------------------------------------------------------- links
    DOOR_LABELS = {
        "security": ["security", "blast"], "engineering": ["engineering", "blast", "maintenance", "hangar", "cargo"],
        "medical": ["medical", "cleanroom", "glass"], "science": ["science", "glass", "cleanroom"],
        "command": ["bulkhead", "officer"], "crew": ["cabin", "officer"], "life": ["engineering", "maintenance", "cargo"],
        "cargo": ["cargo", "hangar", "blast"], "transit": ["bulkhead"],
    }

    def link(self, a, b, kind="door", c=None, model=None, width=None, height=None):
        """Cut matching openings through the shared wall of rooms a and b and add a door.

        kind: "door" (sliding door model), "portal" (open doorway with a frame model) or "open" (wide opening)."""
        A, B = self.rooms[a], self.rooms[b]
        if abs(A.rx1 - B.rx0) < 1e-6:
            sa, sb, axis = "E", "W", "z"
        elif abs(A.rx0 - B.rx1) < 1e-6:
            sa, sb, axis = "W", "E", "z"
        elif abs(A.rz1 - B.rz0) < 1e-6:
            sa, sb, axis = "S", "N", "x"
        elif abs(A.rz0 - B.rz1) < 1e-6:
            sa, sb, axis = "N", "S", "x"
        else:
            raise ValueError(f"{a} and {b} do not touch")
        if axis == "z":
            lo, hi = max(A.rz0, B.rz0), min(A.rz1, B.rz1)
            bx = A.rx1 if sa == "E" else A.rx0
        else:
            lo, hi = max(A.rx0, B.rx0), min(A.rx1, B.rx1)
            bz = A.rz1 if sa == "S" else A.rz0
        if c is None:
            c = (lo + hi) / 2
        w = width or (DOOR_W if kind in ("door", "portal") else 4.0)
        h = height or (DOOR_H if kind in ("door", "portal") else 3.0)
        for room, side in ((A, sa), (B, sb)):
            span = room.wall_span(side)
            if span is None or c - w / 2 < span[0] - 1e-6 or c + w / 2 > span[1] + 1e-6:
                raise ValueError(f"opening {a}-{b} at {c} ({w} wide) is outside the {side} wall of {room.id} {span}")
            room.openings.append({"side": side, "c": round(c, 3), "w": w, "y0": 0.0, "y1": h, "kind": "door" if kind != "open" else "open"})
            room.block_door(side, c, w, 2.0 if kind in ("door", "portal") else 1.0)
            room.links.append({"to": b if room is A else a, "side": side, "c": round(c, 3), "kind": kind})
        y = A.y
        pos = [bx, y, c] if axis == "z" else [c, y, bz]
        yaw = 90.0 if axis == "z" else 0.0
        if kind == "door":
            if model is None:
                dept = B.dept if A.dept == "transit" else A.dept
                pick = self.cat.pick("door", label=self.DOOR_LABELS.get(dept, ["bulkhead"]))
                model = pick["id"]
            self.doors.append({"m": model, "pos": [round(v, 3) for v in pos], "yaw": yaw, "a": a, "b": b})
            self.cat.use[model] += 1
        elif kind == "portal":
            fr = self.cat.pick("doorframe")
            A.props.append({"m": fr["id"], "pos": [round(v, 3) for v in pos], "yaw": yaw, "_m": fr, "b": "ARCH"})
            self.cat.use[fr["id"]] += 1
        return c


class Room:
    """One convex room.  `rect` is the nominal drafting rectangle; `poly` = rect clipped by the hull."""

    def __init__(self, ship, rid, name, deck, rect, height=3.4, dept="transit", floor="deck_plate", tint="#dfe5ee",
                 floor_tint="#ffffff", accent="#3a6ea5", code=None, clip=True):
        self.ship, self.cat = ship, ship.cat
        self.id, self.name, self.deck = rid, name, deck
        self.rx0, self.rz0, self.rx1, self.rz1 = rect
        self.h = height
        self.dept, self.floor, self.tint, self.floor_tint, self.accent = dept, floor, tint, floor_tint, accent
        self.code = code or rid[:3].upper()
        self.y = ship.deck_y(deck)
        poly = rect_poly(rect)
        if clip and deck in ship.hull:
            poly = hulllib.clip_convex(poly, ship.hull[deck])
        self.poly = [tuple(p) for p in poly]
        xs, zs = [p[0] for p in self.poly], [p[1] for p in self.poly]
        self.x0, self.x1, self.z0, self.z1 = min(xs), max(xs), min(zs), max(zs)   # bounding box of the real shape
        self.cx, self.cz = poly_centroid(self.poly)
        self.area = poly_area(self.poly)
        self.props, self.openings, self.lights, self.forcefields = [], [], [], []
        self.links = []
        self.foot = []          # occupied / reserved floor polygons (list of point lists)
        self.cfoot = []         # occupied ceiling polygons
        self.zones = []         # documented clearance zones (for drawings)
        self.floor_holes, self.ceiling_holes = [], []
        self.edges = self._make_edges()
        self.wall_used = {e["side"]: [] for e in self.edges}
        self.rng = random.Random(zlib.crc32(rid.encode()))        # stable and collision-free per room id
        self.vboxes = []        # wall / ceiling items as (polygon, y0, y1) for clashes with tall floor props
        self.lines = []         # BOM lines
        self.cur = None         # current BOM line
        self.brief = {}

    # ------------------------------------------------------ geometry
    def _make_edges(self):
        pts = self.poly
        n = len(pts)
        zmin, xmin = min(p[1] for p in pts), min(p[0] for p in pts)
        ed = []
        k = 0
        outline = self.ship.hull.get(self.deck)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dz = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dz)
            if ln < 1e-4:
                continue
            if abs(dz) < 1e-6:
                side = "N" if abs(a[1] - zmin) < 1e-6 else "S"
            elif abs(dx) < 1e-6:
                side = "W" if abs(a[0] - xmin) < 1e-6 else "E"
            else:
                side = f"D{k}"
                k += 1
            ed.append({"side": side, "a": a, "b": b, "len": ln})
        for e in ed:
            ux, uz = (e["b"][0] - e["a"][0]) / e["len"], (e["b"][1] - e["a"][1]) / e["len"]
            nx, nz = -uz, ux
            mx, mz = (e["a"][0] + e["b"][0]) / 2, (e["a"][1] + e["b"][1]) / 2
            if nx * (self.cx - mx) + nz * (self.cz - mz) < 0:
                nx, nz = -nx, -nz
            e["n"] = (nx, nz)
            e["u"] = (ux, uz)
            e["yaw"] = math.degrees(math.atan2(nx, nz))
            e["hull"] = bool(outline) and self._on_outline(mx, mz, outline)
        return ed

    @staticmethod
    def _on_outline(x, z, outline):
        n = len(outline)
        for i in range(n):
            ax, az = outline[i]
            bx, bz = outline[(i + 1) % n]
            ex, ez = bx - ax, bz - az
            ln = math.hypot(ex, ez)
            if ln < 1e-9:
                continue
            d = abs((x - ax) * ez - (z - az) * ex) / ln
            t = ((x - ax) * ex + (z - az) * ez) / (ln * ln)
            if d < 0.02 and -0.01 <= t <= 1.01:
                return True
        return False

    def edge(self, side):
        for e in self.edges:
            if e["side"] == side:
                return e
        return None

    def wall_span(self, side):
        """(a, b) extent of an axis-aligned wall along its axis (absolute X or Z) or (0, len) for a diagonal."""
        e = self.edge(side)
        if e is None:
            return None
        if side in ("N", "S"):
            return (min(e["a"][0], e["b"][0]), max(e["a"][0], e["b"][0]))
        if side in ("E", "W"):
            return (min(e["a"][1], e["b"][1]), max(e["a"][1], e["b"][1]))
        return (0.0, e["len"])

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def d(self):
        return self.z1 - self.z0

    @property
    def volume(self):
        return self.area * self.h

    def inside(self, x, z, margin=0.0):
        """Point inside the room shell, `margin` metres clear of every wall."""
        for e in self.edges:
            if e["n"][0] * (x - e["a"][0]) + e["n"][1] * (z - e["a"][1]) < margin - 1e-9:
                return False
        return True

    def inner(self, m=0.0):
        """Bounding box of the room inset by the wall thickness (legacy helper)."""
        return (self.x0 + WALL_T + m, self.z0 + WALL_T + m, self.x1 - WALL_T - m, self.z1 - WALL_T - m)

    def occupancy(self):
        area = 0.0
        for p in self.props:
            fp = p.get("_fp")
            if fp and p["_m"]["mount"] == "floor":
                area += p["_area"]
        return area / max(self.area, 1.0)

    def describe(self, purpose, basis="", crew=0, adjacency="", notes=""):
        """Design brief printed at the head of the room's BOM chapter."""
        self.brief = {"purpose": purpose, "basis": basis, "crew": crew, "adjacency": adjacency, "notes": notes}

    def line(self, title, why, code=None):
        """Start a new bill-of-materials line: every placement until the next call belongs to it."""
        n = len(self.lines) + 1
        self.cur = {"code": code or f"{self.code}-{n:02d}", "title": title, "why": why}
        self.lines.append(self.cur)
        return self.cur

    def block_door(self, side, c, w, depth=2.0):
        e = self.edge(side)
        if e is None:
            return
        if side == "N":
            r = (c - w / 2 - 0.2, e["a"][1], c + w / 2 + 0.2, e["a"][1] + depth)
        elif side == "S":
            r = (c - w / 2 - 0.2, e["a"][1] - depth, c + w / 2 + 0.2, e["a"][1])
        elif side == "W":
            r = (e["a"][0], c - w / 2 - 0.2, e["a"][0] + depth, c + w / 2 + 0.2)
        else:
            r = (e["a"][0] - depth, c - w / 2 - 0.2, e["a"][0], c + w / 2 + 0.2)
        self.foot.append(rect_poly(r))
        self.zones.append({"kind": "door", "rect": [round(v, 3) for v in r], "why": "door swing / walkway clearance"})
        self.wall_used[side].append((c - w / 2 - 0.1, c + w / 2 + 0.1, 0.0, 99.0))

    def keep_clear(self, rect, why="circulation"):
        """Reserve a floor rectangle (x0, z0, x1, z1): nothing will be placed there."""
        self.foot.append(rect_poly(rect))
        self.zones.append({"kind": "clear", "rect": [round(v, 3) for v in rect], "why": why})

    def add_hole(self, rect, floor=False, ceiling=False):
        if floor:
            self.floor_holes.append(list(rect))
            self.foot.append(rect_poly(rect))
        if ceiling:
            self.ceiling_holes.append(list(rect))
            self.cfoot.append(rect_poly(rect))

    def add_window(self, side, c, w, y0=0.9, y1=2.6):
        """Window in the wall `side` (axis side or diagonal "D#"); `c` as described in the module doc."""
        e = self.edge(side)
        if e is None:
            raise ValueError(f"{self.id} has no wall {side}")
        self.openings.append({"side": side, "c": round(c, 3), "w": w, "y0": y0, "y1": y1, "kind": "window"})
        self.wall_used[side].append((c - w / 2 - 0.1, c + w / 2 + 0.1, 0.0, 99.0))

    def diag_sides(self):
        return [e["side"] for e in self.edges if e["side"].startswith("D")]

    # ------------------------------------------------------ placement
    def footprint(self, m, cx, cz, yaw, scale=1.0):
        """(origin px,pz, corner polygon, aabb) of model m whose footprint centre is (cx, cz)."""
        lo, hi = m["bounds_min"], m["bounds_max"]
        lx, lz = (lo[0] + hi[0]) / 2 * scale, (lo[2] + hi[2]) / 2 * scale
        ox, oz = rot(lx, lz, yaw)
        px, pz = cx - ox, cz - oz
        hx, hz = (hi[0] - lo[0]) / 2 * scale, (hi[2] - lo[2]) / 2 * scale
        corners = obb_corners(cx, cz, hx, hz, yaw)
        aabb = (min(p[0] for p in corners), min(p[1] for p in corners), max(p[0] for p in corners), max(p[1] for p in corners))
        return px, pz, corners, aabb, 4 * hx * hz

    def free(self, corners, margin=0.0, wall_margin=None):
        """True if the polygon lies inside the shell and clears every occupied / reserved area."""
        wm = WALL_T if wall_margin is None else wall_margin
        for (x, z) in corners:
            if not self.inside(x, z, wm - 1e-3):
                return False
        for a in self.foot:
            if polys_overlap(corners, a, max(margin, 0.0)):
                return False
        return True

    def _vclash(self, corners, y0, y1):
        """True if a column (footprint `corners`, heights y0..y1 above the floor) hits a wall / ceiling item."""
        for (poly, a0, a1) in self.vboxes:
            if y0 < a1 - 1e-3 and y1 > a0 + 1e-3 and polys_overlap(corners, poly, 0.0):
                return True
        return False

    def place(self, m, cx, cz, yaw=0.0, y=None, check=True, reserve=True, scale=1.0, solid=None, margin=0.0):
        """Place model `m` (catalog entry or id) with its footprint centre at (cx, cz).

        Floor models stand on the floor, ceiling models hang from the ceiling, table models sit at the height you pass
        (see on_top); wall models are refused here - hang them with wall_item().  Returns the prop or None."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        mount = m["mount"]
        if mount == "wall":
            return None
        ceil_y = self.y + self.h
        if mount == "floor" and y is not None and abs(y - self.y) > 0.02:
            return None
        if mount == "ceiling" and y is not None and abs(y - ceil_y) > 0.02:
            return None
        px, pz, corners, aabb, area = self.footprint(m, cx, cz, yaw, scale)
        floor_item = mount == "floor"
        ceil_item = mount == "ceiling"
        height = m["size"][1] * scale
        if floor_item and height > self.h - 0.05:
            return None                                       # would poke through the ceiling
        if check and floor_item:
            if not self.free(corners, margin):
                return None
            if self._vclash(corners, 0.0, height):
                return None
        if ceil_item:
            if check and not all(self.inside(x, z, WALL_T - 1e-3) for x, z in corners):
                return None
            if check and any(polys_overlap(corners, a) for a in self.cfoot):
                return None
            if check:
                lo_y = self.h + m["bounds_min"][1] * scale            # lowest point of the fixture above the floor
                for p in self.props:
                    pm = p["_m"]
                    if pm["mount"] == "floor" and p.get("_obb") and polys_overlap(corners, p["_obb"]) and \
                            pm["size"][1] * p.get("scale", 1.0) > lo_y - 1e-3:
                        return None
            self.cfoot.append(corners)
            self.vboxes.append((corners, self.h + m["bounds_min"][1] * scale, self.h + m["bounds_max"][1] * scale))
        if y is None:
            y = self.y if mount != "ceiling" else ceil_y
        p = {"m": m["id"], "pos": [round(px, 3), round(y, 3), round(pz, 3)], "yaw": round(yaw, 2)}
        if scale != 1.0: p["scale"] = scale
        if solid is not None: p["solid"] = solid
        if self.cur is not None: p["b"] = self.cur["code"]
        self.props.append(p)
        self.cat.use[m["id"]] += 1
        if reserve and floor_item:
            self.foot.append(corners)
        p["_fp"] = aabb
        p["_obb"] = corners
        p["_area"] = area
        p["_m"] = m
        return p

    def against_wall(self, side, m, along, gap=0.04, y=None, check=True, yaw_extra=0.0, reserve=True, scale=1.0, solid=None,
                     margin=0.0):
        """Place a floor/wall item with its back to wall `side`, centred at `along` (x for N/S, z for E/W,
        distance from the edge start for a diagonal wall)."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        e = self.edge(side)
        if e is None:
            return None
        lo, hi = m["bounds_min"], m["bounds_max"]
        hw = m["size"][0] * scale / 2
        if m["mount"] == "floor" and m["size"][1] > 0.6:
            for (ua, ub, uy0, uy1) in self.wall_used[side]:
                if uy1 >= 50 and along - hw < ub and along + hw > ua:
                    return None                       # would block a window / doorway
        cdist = WALL_T + gap + (hi[2] - lo[2]) * scale / 2      # wall face -> centre of the footprint
        a, b = self.wall_span(side)
        if along - hw < a - 1e-6 or along + hw > b + 1e-6:
            return None
        cx, cz = self._wall_point(e, side, along)
        cx, cz = cx + e["n"][0] * cdist, cz + e["n"][1] * cdist
        yaw = e["yaw"] + yaw_extra if side[0] == "D" else FACE_YAW[side] + yaw_extra
        p = self.place(m, cx, cz, yaw, y=y, check=check, reserve=reserve, scale=scale, solid=solid, margin=margin)
        if p is not None and m["mount"] == "floor":
            self.wall_used[side].append((along - hw, along + hw, 0.0, m["size"][1] * scale))
        return p

    def _wall_point(self, e, side, along):
        """World point on the wall face line (the wall's room-side surface without the thickness)."""
        if side in ("N", "S"):
            return (along, e["a"][1])
        if side in ("E", "W"):
            return (e["a"][0], along)
        return (e["a"][0] + e["u"][0] * along, e["a"][1] + e["u"][1] * along)

    def wall_span_free(self, side, a, b, y0=0.0, y1=99.0):
        for (ua, ub, uy0, uy1) in self.wall_used.get(side, []):
            if a < ub and b > ua and y0 < uy1 and y1 > uy0:
                return False
        return True

    def wall_item(self, side, m, along, y=None, gap=0.0, check=True):
        """Wall-mounted item (origin on the wall face). Returns placement or None if the span is taken
        or sticks out past the end of the wall."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        e = self.edge(side)
        if e is None:
            return None
        wd = m["size"][0]
        span = self.wall_span(side)
        if along - wd / 2 < span[0] + 0.05 or along + wd / 2 > span[1] - 0.05:
            return None
        yy = (m.get("mount_y") or 1.5) if y is None else y
        if yy + m["size"][1] / 2 > self.h - 0.02 or yy - m["size"][1] / 2 < 0.0:
            return None
        if check and not self.wall_span_free(side, along - wd / 2, along + wd / 2, yy - m["size"][1] / 2 - 0.02, yy + m["size"][1] / 2 + 0.02):
            return None
        yaw = e["yaw"] if side[0] == "D" else FACE_YAW[side]
        lo, hi = m["bounds_min"], m["bounds_max"]
        lx = (lo[0] + hi[0]) / 2
        wx, wz = self._wall_point(e, side, along)
        wx, wz = wx + e["n"][0] * (WALL_T + gap), wz + e["n"][1] * (WALL_T + gap)
        ox, oz = rot(lx, 0, yaw)
        # the item's volume must not intersect a tall floor prop standing against the same wall
        depth = max(hi[2], 0.02)
        bcx, bcz = wx + e["n"][0] * depth / 2, wz + e["n"][1] * depth / 2
        box = obb_corners(bcx, bcz, (hi[0] - lo[0]) / 2, depth / 2, yaw)
        wy0, wy1 = yy + lo[1], yy + hi[1]
        if check:
            for q in self.props:
                qm = q["_m"]
                if qm["mount"] == "floor" and q.get("_obb") and wy0 < qm["size"][1] * q.get("scale", 1.0) - 1e-3 and \
                        polys_overlap(box, q["_obb"], 0.0):
                    return None
        self.vboxes.append((box, wy0, wy1))
        p = {"m": m["id"], "pos": [round(wx - ox, 3), round(self.y + yy, 3), round(wz - oz, 3)], "yaw": round(yaw, 2), "_m": m}
        if self.cur is not None:
            p["b"] = self.cur["code"]
        self.props.append(p)
        self.cat.use[m["id"]] += 1
        self.wall_used[side].append((along - wd / 2, along + wd / 2, yy - m["size"][1] / 2, yy + m["size"][1] / 2))
        return p

    def ceiling_item(self, m, x, z, yaw=0.0):
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        return self.place(m, x, z, yaw, y=self.y + self.h, check=True)

    def on_top(self, host, m, dx=0.0, dz=0.0, yaw=None):
        """Stand a small item on the flat top of a placed host prop (must fit on the host's footprint)."""
        if host is None:
            return None
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        hm = host["_m"]
        ty = hm.get("top_y")
        if ty is None or hm["category"] not in SURFACE_HOSTS:
            return None
        hy = host["pos"][1]
        fp = host["_fp"]
        cx, cz = (fp[0] + fp[2]) / 2 + dx, (fp[1] + fp[3]) / 2 + dz
        yw = host["yaw"] if yaw is None else yaw
        _, _, corners, _, _ = self.footprint(m, cx, cz, yw)
        if not all(_point_in_poly(c, host["_obb"], -0.02) for c in corners):
            return None
        tops = host.setdefault("_tops", [])
        if any(polys_overlap(corners, t, 0.02) for t in tops):
            return None                                    # two items never share the same spot on a table
        p = self.place(m, cx, cz, yw, y=hy + ty, check=False)
        if p is not None:
            p["_on"] = host["m"]
            tops.append(corners)
        return p

    # ------------------------------------------------------ patterns
    def run(self, side, cats, start=None, end=None, gap=0.04, spacing=0.05, pred=None, limit=99, y=None,
            wall_mount=False, margin=0.0, max_w=None):
        """Fill a wall with a row of items picked (least-used first) from `cats`.

        wall_mount=True hangs wall-mount models only; otherwise floor models stand against the wall (wall-mount
        models among the candidates are hung)."""
        if isinstance(cats, str):
            cats = [cats]
        user_pred = pred
        if wall_mount:
            pred = (lambda c: c["mount"] == "wall" and (user_pred is None or user_pred(c)))
        else:
            pred = (lambda c: c["mount"] in ("floor", "wall") and (user_pred is None or user_pred(c)))
        span = self.wall_span(side)
        if span is None:
            return []
        a0, a1 = span[0] + WALL_T, span[1] - WALL_T
        if side[0] == "D":
            a0, a1 = span[0] + 0.3, span[1] - 0.3
        pos = (a0 if start is None else max(start, a0))
        end = a1 if end is None else min(end, a1)
        placed = []
        tries = 0
        while pos < end - 0.2 and len(placed) < limit and tries < 60:
            tries += 1
            m = self.cat.pick_any(cats, pred=pred, rng=self.rng)
            if m is None:
                break
            wd = m["size"][0]
            if max_w and wd > max_w:
                pos += 0.3
                continue
            if pos + wd > end + 1e-3:
                narrow = self.cat.pick_any(cats, pred=lambda c: c["size"][0] <= end - pos and pred(c), rng=self.rng)
                if narrow is None:
                    break
                m = narrow
                wd = m["size"][0]
            c = pos + wd / 2
            p = (self.wall_item(side, m, c, y=y) if m["mount"] == "wall"
                 else self.against_wall(side, m, c, gap=gap, margin=margin))
            if p is None:
                pos += 0.35
                continue
            placed.append(p)
            pos += wd + spacing
        return placed

    def grid(self, cats, x0, z0, x1, z1, nx, nz, yaw=0.0, pred=None, jitter=0.0, single=None):
        """Regular grid of floor items inside a rectangle."""
        out = []
        for i in range(nx):
            for j in range(nz):
                x = x0 + (x1 - x0) * (i + 0.5) / nx
                z = z0 + (z1 - z0) * (j + 0.5) / nz
                m = self.cat.models[single] if single else self.cat.pick_any(cats if isinstance(cats, list) else [cats], pred=pred, rng=self.rng)
                if m is None:
                    continue
                p = self.place(m, x + self.rng.uniform(-jitter, jitter), z + self.rng.uniform(-jitter, jitter), yaw)
                if p:
                    out.append(p)
        return out

    def light_grid(self, cats=("ceilinglight",), spacing=4.2, energy=1.6, color="#fff0dd", pred=None, shadow_every=3,
                   range_mul=1.5, angle=75.0, x_margin=1.0, label=None, cosmetic_only=False):
        """Regular grid of ceiling fixtures (+ one real light each) over the room's shape."""
        nx = max(1, int(round((self.w - 2 * x_margin) / spacing)))
        nz = max(1, int(round((self.d - 2 * x_margin) / spacing)))
        k = 0
        for i in range(nx):
            for j in range(nz):
                x = self.x0 + x_margin + (self.w - 2 * x_margin) * (i + 0.5) / nx
                z = self.z0 + x_margin + (self.d - 2 * x_margin) * (j + 0.5) / nz
                if not self.inside(x, z, 0.7):
                    continue
                m = self.cat.pick_any(list(cats), pred=lambda c: c["mount"] == "ceiling" and (pred is None or pred(c)), rng=self.rng)
                if m:
                    self.place(m, x, z, 0.0, y=self.y + self.h, check=True)
                if not cosmetic_only:
                    self.lights.append({"type": "spot", "pos": [round(x, 2), round(self.y + self.h - 0.25, 2), round(z, 2)],
                                        "energy": round(energy * 1.7, 2), "color": color, "range": round(self.h * range_mul + 2, 1),
                                        "angle": angle, "shadow": (k % shadow_every == 0)})
                k += 1

    def omni(self, x, y, z, color="#66ccff", energy=0.8, rng_=5.0, shadow=False):
        self.lights.append({"type": "omni", "pos": [round(x, 2), round(y, 2), round(z, 2)], "energy": energy,
                            "color": color, "range": rng_, "shadow": shadow})

    def to_json(self):
        props = []
        for p in self.props:
            props.append({k: v for k, v in p.items() if not k.startswith("_")})
        return {"id": self.id, "name": self.name, "deck": self.deck,
                "rect": [round(self.x0, 3), round(self.z0, 3), round(self.x1, 3), round(self.z1, 3)],
                "poly": [[round(x, 3), round(z, 3)] for x, z in self.poly],
                "edges": [{"side": e["side"], "a": [round(e["a"][0], 3), round(e["a"][1], 3)],
                           "b": [round(e["b"][0], 3), round(e["b"][1], 3)], "hull": e["hull"]} for e in self.edges],
                "height": self.h, "dept": self.dept, "code": self.code, "floor": self.floor, "tint": self.tint,
                "floor_tint": self.floor_tint, "accent": self.accent, "openings": self.openings,
                "lights": self.lights, "forcefields": self.forcefields, "floor_holes": self.floor_holes,
                "ceiling_holes": self.ceiling_holes, "zones": self.zones, "links": self.links,
                "brief": self.brief, "bom": self.lines, "area": round(self.area, 1), "props": props}


def _point_in_poly(pt, poly, margin=0.0):
    """Point inside convex polygon (any winding), `margin` > 0 requires it to be that far inside."""
    s = 0.0
    n = len(poly)
    for i in range(n):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % n]
        s += x0 * z1 - x1 * z0
    sgn = 1 if s > 0 else -1
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        ln = math.hypot(bx - ax, bz - az) or 1.0
        d = sgn * ((bx - ax) * (pt[1] - az) - (bz - az) * (pt[0] - ax)) / ln
        if d < margin - 1e-9:
            return False
    return True
