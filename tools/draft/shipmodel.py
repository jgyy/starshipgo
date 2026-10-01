"""Ship data wrapper + small geometry helpers for the drafting tool (pure standard library)."""
import colorsys
import json
import math
import os

WALL_T = 0.15
SLAB_T = 0.3
PITCH = 4.0
FLAT_H = 0.15


def rot(x, z, yaw):
    t = math.radians(yaw)
    c, s = math.cos(t), math.sin(t)
    return (c * x + s * z, -s * x + c * z)


def poly_area(p):
    a = 0.0
    for i in range(len(p)):
        x0, z0 = p[i]
        x1, z1 = p[(i + 1) % len(p)]
        a += x0 * z1 - x1 * z0
    return a / 2


def clip_half(poly, nx, nz, c):
    """Keep the part of a polygon with nx*x + nz*z >= c (Sutherland-Hodgman)."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = nx * a[0] + nz * a[1] - c
        db = nx * b[0] + nz * b[1] - c
        if da >= 0:
            out.append(a)
        if (da > 0 > db) or (da < 0 < db):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def centroid(poly):
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


def inset(poly, d):
    """Inward offset of a convex polygon by d."""
    out = list(poly)
    cx, cz = centroid(poly)
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        dx, dz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dz)
        if ln < 1e-9:
            continue
        nx, nz = -dz / ln, dx / ln
        if nx * (cx - a[0]) + nz * (cz - a[1]) < 0:
            nx, nz = -nx, -nz
        out = clip_half(out, nx, nz, nx * a[0] + nz * a[1] + d)
        if not out:
            return []
    return out


def line_interval(poly, axis, val):
    """Interval of the other coordinate where the line coord[axis]==val crosses a convex polygon, or None."""
    o = 1 - axis
    hits = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da, db = a[axis] - val, b[axis] - val
        if da == 0:
            hits.append(a[o])
        if (da < 0 < db) or (db < 0 < da):
            t = da / (da - db)
            hits.append(a[o] + (b[o] - a[o]) * t)
    if len(hits) < 2:
        return None
    return (min(hits), max(hits))


def rect_poly(r):
    return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]


class Catalog:
    def __init__(self, path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        self.models = {m["id"]: m for m in d["models"]}
        cats = sorted({m["category"] for m in d["models"]})
        self.cats = cats
        self.color = {}
        for i, c in enumerate(cats):
            h = (i * 0.61803398875) % 1.0
            s = 0.38 + 0.12 * ((i * 7) % 3) / 2
            v = 0.97 - 0.06 * ((i * 5) % 3) / 2
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            self.color[c] = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

    def fill(self, m):
        return self.color.get(m["category"], "#dddddd")


class Prop:
    def __init__(self, d, cat):
        self.d = d
        self.m = cat.models[d["m"]]
        m = self.m
        self.id = d["m"]
        self.code = d.get("b")
        self.mount = m["mount"]
        self.cat = m["category"]
        self.label = m.get("label") or m["id"]
        sc = d.get("scale", 1.0)
        px, py, pz = d["pos"]
        self.yaw = d.get("yaw", 0.0)
        lo, hi = m["bounds_min"], m["bounds_max"]
        self.y0, self.y1 = py + lo[1] * sc, py + hi[1] * sc
        self.pos = (px, py, pz)
        pts = []
        for lx, lz in ((lo[0], lo[2]), (hi[0], lo[2]), (hi[0], hi[2]), (lo[0], hi[2])):
            ox, oz = rot(lx * sc, lz * sc, self.yaw)
            pts.append((px + ox, pz + oz))
        self.corners = pts
        self.bbox = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
        self.cx = sum(p[0] for p in pts) / 4
        self.cz = sum(p[1] for p in pts) / 4
        fx, fz = rot(0, 1, self.yaw)
        self.front = (fx, fz)
        self.size = (m["size"][0] * sc, m["size"][1] * sc, m["size"][2] * sc)
        self.on = d.get("_on")


class Room:
    def __init__(self, d, ship):
        self.d = d
        self.ship = ship
        self.id, self.name, self.deck = d["id"], d["name"], d["deck"]
        self.code, self.dept = d["code"], d["dept"]
        self.h = d["height"]
        self.y = ship.deck_y[self.deck]
        self.poly = [tuple(p) for p in d["poly"]]
        self.cx, self.cz = centroid(self.poly)
        self.area = d["area"]
        xs, zs = [p[0] for p in self.poly], [p[1] for p in self.poly]
        self.x0, self.x1, self.z0, self.z1 = min(xs), max(xs), min(zs), max(zs)
        self.tint = d.get("tint", "#dddddd")
        self.openings = d.get("openings", [])
        self.zones = d.get("zones", [])
        self.floor_holes = d.get("floor_holes", [])
        self.ceiling_holes = d.get("ceiling_holes", [])
        self.forcefields = d.get("forcefields", [])
        self.links = d.get("links", [])
        self.bom = d.get("bom", [])
        self.brief = d.get("brief", {})
        self.props = [Prop(p, ship.cat) for p in d.get("props", [])]
        self.inner = inset(self.poly, WALL_T)
        self.edges = []
        for e in d["edges"]:
            a, b = tuple(e["a"]), tuple(e["b"])
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            if ln < 1e-6:
                continue
            u = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
            n = (-u[1], u[0])
            mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            if n[0] * (self.cx - mx) + n[1] * (self.cz - mz) < 0:
                n = (-n[0], -n[1])
            self.edges.append({"side": e["side"], "a": a, "b": b, "len": ln, "u": u, "n": n, "hull": e.get("hull", False)})
        self.doors = []          # filled by Ship

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def dd(self):
        return self.z1 - self.z0

    @property
    def top(self):
        return self.y + self.h

    def edge(self, side):
        for e in self.edges:
            if e["side"] == side:
                return e
        return None

    def opening_seg(self, o):
        """World segment ((x0,z0),(x1,z1)) of an opening on its wall edge line, plus the edge."""
        e = self.edge(o["side"])
        if e is None:
            return None
        c, w = o["c"], o["w"]
        s = o["side"]
        if s in ("N", "S"):
            z = e["a"][1]
            return ((c - w / 2, z), (c + w / 2, z)), e
        if s in ("E", "W"):
            x = e["a"][0]
            return ((x, c - w / 2), (x, c + w / 2)), e
        a, u = e["a"], e["u"]
        return ((a[0] + u[0] * (c - w / 2), a[1] + u[1] * (c - w / 2)),
                (a[0] + u[0] * (c + w / 2), a[1] + u[1] * (c + w / 2))), e

    def occupancy(self):
        a = 0.0
        for p in self.props:
            if p.mount == "floor" and p.size[1] > FLAT_H and p.code != "ARCH" and p.cat not in ("door", "doorframe"):
                # rugs, floor markings and door frames do not occupy floor (same definition as audit rule `density`)
                a += (p.size[0] * p.size[2])
        return a / max(self.area, 1.0)

    def crew(self):
        return self.brief.get("crew", 0) or 0


class Ship:
    def __init__(self, ship_path, cat_path):
        with open(ship_path, encoding="utf-8") as fh:
            d = json.load(fh)
        self.cat = Catalog(cat_path)
        self.raw = d
        self.decks = d["decks"]
        self.deck_y = {k["id"]: k["y"] for k in d["decks"]}
        self.deck_name = {k["id"]: k["name"] for k in d["decks"]}
        self.hull = {int(k): [tuple(p) for p in v] for k, v in d["hull"].items()}
        self.rooms = [Room(r, self) for r in d["rooms"]]
        self.by_id = {r.id: r for r in self.rooms}
        self.doors = d.get("doors", [])
        self.stairs = d.get("stairs", [])
        for dr in self.doors:
            for k in ("a", "b"):
                r = self.by_id.get(dr[k])
                if r:
                    r.doors.append(dr)
        self.spawn = d.get("spawn")
        self.deck_ids = sorted(self.deck_y)                    # top (Sky) deck first
        self.skin = Skin(d["skin"]) if d.get("skin") else None
        self.ext_windows = d.get("ext_windows", [])
        arch = os.path.join(os.path.dirname(os.path.abspath(ship_path)), "arch.json")
        models = {}
        if os.path.exists(arch):
            with open(arch, encoding="utf-8") as fh:
                models = {m["id"]: m for m in json.load(fh)["models"]}
        self.fittings = [Fitting(f, models) for f in d.get("exterior", []) if f["m"] in models]
        self.fp_z = self._forward_perpendicular()
        self._build_schedules()

    def _build_schedules(self):
        """Door list (marks D01..), window list, lookup of mark by (room, side, c)."""
        order = {r.id: i for i, r in enumerate(self.rooms)}
        doors, seen = [], set()
        for r in self.rooms:
            for lk in r.links:
                o = lk["to"]
                pair = tuple(sorted((r.id, o))) + (round(lk["c"], 2),)
                if pair in seen:
                    continue
                seen.add(pair)
                op = next((x for x in r.openings if x["side"] == lk["side"] and abs(x["c"] - lk["c"]) < 1e-3
                           and x["kind"] != "window"), None)
                model, locked = "-", False
                ci = 2 if lk["side"] in ("E", "W") else 0
                for dr in self.doors:
                    if {dr["a"], dr["b"]} == {r.id, o} and abs(dr["pos"][ci] - lk["c"]) < 1e-2:
                        model, locked = dr["m"], dr.get("locked", False)
                        break
                else:
                    if lk["kind"] == "portal":
                        model = "doorframe (arch)"
                    elif lk["kind"] == "open":
                        model = "open arch"
                doors.append({"a": r.id, "b": o, "side": lk["side"], "c": lk["c"], "kind": lk["kind"], "deck": r.deck,
                              "w": op["w"] if op else 0, "h": op["y1"] if op else 0, "model": model, "locked": locked,
                              "order": (r.deck, order[r.id], lk["c"])})
        doors.sort(key=lambda d: d["order"])
        self.door_list = doors
        self.door_mark = {}
        for i, d in enumerate(doors):
            d["mark"] = "D%02d" % (i + 1)
            self.door_mark[(d["a"], d["side"], round(d["c"], 2))] = d
            lk2 = next((l for l in self.by_id[d["b"]].links if l["to"] == d["a"] and abs(l["c"] - d["c"]) < 1e-3), None)
            if lk2:
                self.door_mark[(d["b"], lk2["side"], round(d["c"], 2))] = d
        wins = []
        for r in self.rooms:
            k = 0
            for o in sorted([x for x in r.openings if x["kind"] == "window"], key=lambda x: (x["side"], x["c"])):
                k += 1
                wins.append({"room": r.id, "deck": r.deck, "side": o["side"], "c": o["c"], "w": o["w"], "sill": o["y0"],
                             "head": o["y1"], "mark": "W-%s-%d" % (r.code, k)})
        self.win_list = wins
        self.win_mark = {(w["room"], w["side"], round(w["c"], 2)): w for w in wins}

    def _forward_perpendicular(self):
        """Station 0: the foremost point of the ship (skin and fittings), rounded outward to a whole metre."""
        zs = [self.bounds(None)[1]]
        if self.skin:
            zs.append(self.skin.z0)
        zs += [f.bmin[2] for f in self.fittings]
        return float(math.floor(min(zs) + 1e-9))

    def overall(self):
        """(xmin, ymin, zmin, xmax, ymax, zmax) of the skin and every exterior fitting."""
        lo = [1e9] * 3
        hi = [-1e9] * 3
        if self.skin:
            lo = [self.skin.x0, self.skin.y0, self.skin.z0]
            hi = [self.skin.x1, self.skin.y1, self.skin.z1]
        else:
            b = self.bounds(None)
            lo = [b[0], min(self.deck_y.values()), b[1]]
            hi = [b[2], max(self.deck_y.values()) + 4.0, b[3]]
        for f in self.fittings:
            lo = [min(a, b) for a, b in zip(lo, f.bmin)]
            hi = [max(a, b) for a, b in zip(hi, f.bmax)]
        return (lo[0], lo[1], lo[2], hi[0], hi[1], hi[2])

    def station_zs(self, zmin=None, zmax=None):
        """(index, z) of every station (every STATION_M from the forward perpendicular) inside [zmin, zmax]."""
        zmin = self.fp_z if zmin is None else zmin
        zmax = self.overall()[5] if zmax is None else zmax
        out, k = [], 0
        while self.fp_z + STATION_M * k <= zmax + 1e-6:
            z = self.fp_z + STATION_M * k
            if z >= zmin - 1e-6:
                out.append((k, z))
            k += 1
        return out

    def tower(self, sid, deck):
        """Stair tower room of stair `sid` (e.g. 'SA') on `deck`."""
        return self.by_id.get("tower%s%d" % (sid[1], deck))

    def top_y(self, deck):
        return max((r.top for r in self.deck_rooms(deck)), default=self.deck_y[deck] + 3.4)

    def deck_rooms(self, deck):
        return [r for r in self.rooms if r.deck == deck]

    def bounds(self, deck=None):
        pts = []
        for k, v in self.hull.items():
            if deck is None or k == deck:
                pts += v
        xs, zs = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(zs), max(xs), max(zs)

    def stair_geom(self, sid):
        """Normalised stair data: for each run, flights as dicts with start x, z centre, direction, y0, risers, going."""
        out = []
        for st in self.stairs:
            if st["id"] != sid:
                continue
            for run in st["runs"]:
                lr = run["landing"]["rect"]
                lcx = (lr[0] + lr[2]) / 2
                fl = []
                f0, f1 = run["flights"]
                d0 = 1 if lcx > f0["pos"][0] else -1
                for k, f in enumerate(run["flights"]):
                    dirx = d0 if k == 0 else -d0
                    nris = int(round(f["rise"] / (PITCH / 22.0)))
                    fl.append({"x": f["pos"][0], "y": f["pos"][1], "z": f["pos"][2], "dir": dirx, "rise": f["rise"],
                               "n": nris, "tread": f["run"] / max(nris - 1, 1), "w": st["width"], "up": k == 0})
                out.append({"lo": run["deck_lo"], "hi": run["deck_hi"], "flights": fl, "landing": lr, "landing_y": run["landing"]["y"]})
            return out, st
        return [], None


# ================================================================== outer skin and exterior fittings
STATION_M = 6.0           # frame / station spacing along the ship (m)


def convex_hull(pts):
    """Andrew's monotone chain; returns the hull counter-clockwise (no repeated end point)."""
    p = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    if len(p) <= 2:
        return p

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in p:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


class Skin:
    """The smooth outer skin: a loft of closed star-shaped rings (see tools/layout/hull.py)."""

    def __init__(self, d):
        self.cx, self.cz = d["center"]
        self.n = d["n"]
        self.rings = d["rings"]
        self.ys = [r["y"] for r in self.rings]
        self.y0, self.y1 = self.ys[0], self.ys[-1]
        n = self.n
        cs = [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.pts = [[(self.cx + r["sx"] * r["r"][i] * cs[i][0], self.cz + r["sz"] * r["r"][i] * cs[i][1]) for i in range(n)]
                    for r in self.rings]
        allp = [p for ring in self.pts for p in ring]
        self.x0, self.x1 = min(p[0] for p in allp), max(p[0] for p in allp)
        self.z0, self.z1 = min(p[1] for p in allp), max(p[1] for p in allp)

    def plan(self, y):
        """Cross-section polygon (x, z) at height y, interpolated between the two surrounding rings (None outside)."""
        if y < self.y0 - 1e-9 or y > self.y1 + 1e-9:
            return None
        for i in range(len(self.ys) - 1):
            ya, yb = self.ys[i], self.ys[i + 1]
            if ya - 1e-9 <= y <= yb + 1e-9:
                t = 0.0 if yb - ya < 1e-9 else (y - ya) / (yb - ya)
                return [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for p, q in zip(self.pts[i], self.pts[i + 1])]
        return None

    def silhouette(self):
        """Side silhouette: (fore, aft) lists of (z, y) per ring, bow (min z) and stern (max z)."""
        fore = [(min(p[1] for p in ring), y) for ring, y in zip(self.pts, self.ys)]
        aft = [(max(p[1] for p in ring), y) for ring, y in zip(self.pts, self.ys)]
        return fore, aft

    def volume(self):
        """Enclosed volume (m3) by integrating the ring areas over height."""
        ar = [abs(poly_area(r)) for r in self.pts]
        return sum((ar[i] + ar[i + 1]) / 2 * (self.ys[i + 1] - self.ys[i]) for i in range(len(ar) - 1))


class Fitting:
    """An exterior fitting (nacelle, deflector, mast, ...) as an oriented bounding box (Godot Euler order YXZ)."""

    def __init__(self, d, models):
        self.d = d
        self.id = d["m"]
        m = models[self.id]
        self.label = self.id[5:] if self.id.startswith("arch_") else self.id
        self.label = self.label.replace("_", " ")
        self.pos = tuple(d["pos"])
        self.yaw, self.pitch, self.scale = d.get("yaw", 0.0), d.get("pitch", 0.0), d.get("scale", 1.0)
        lo, hi = m["bounds_min"], m["bounds_max"]
        self.size = tuple((hi[i] - lo[i]) * self.scale for i in range(3))
        cp, sp = math.cos(math.radians(self.pitch)), math.sin(math.radians(self.pitch))
        self.corners = []
        for k in range(8):
            x = (hi if k & 1 else lo)[0] * self.scale
            y = (hi if k & 2 else lo)[1] * self.scale
            z = (hi if k & 4 else lo)[2] * self.scale
            y, z = y * cp - z * sp, y * sp + z * cp                  # pitch about X
            x, z = rot(x, z, self.yaw)                                # yaw about Y
            self.corners.append((self.pos[0] + x, self.pos[1] + y, self.pos[2] + z))
        self.bmin = tuple(min(c[i] for c in self.corners) for i in range(3))
        self.bmax = tuple(max(c[i] for c in self.corners) for i in range(3))

    EDGES = [(a, a | b) for a in range(8) for b in (1, 2, 4) if not a & b]

    def hull2(self, i, j):
        """Convex hull of the box projected on coordinates (i, j) of (x, y, z)."""
        return convex_hull([(c[i], c[j]) for c in self.corners])

    def cut_poly(self, T):
        """Intersection of the box with the vertical plane d = 0 where T(x, z) -> (h, d); polygon of (h, y) or None."""
        q = []
        for c in self.corners:
            h, d = T(c[0], c[2])
            q.append((h, c[1], d))
        pts = []
        for a, b in self.EDGES:
            da, db = q[a][2], q[b][2]
            if abs(da) < 1e-9:
                pts.append((q[a][0], q[a][1]))
            if (da < -1e-9 and db > 1e-9) or (da > 1e-9 and db < -1e-9):
                t = da / (da - db)
                pts.append((q[a][0] + (q[b][0] - q[a][0]) * t, q[a][1] + (q[b][1] - q[a][1]) * t))
        if len(pts) < 3:
            return None
        hp = convex_hull(pts)
        return hp if len(hp) >= 3 else None

    def depth_range(self, T):
        ds = [T(c[0], c[2])[1] for c in self.corners]
        return min(ds), max(ds)

    def beyond_poly(self, T):
        """Projection (h, y) of the part of the box behind the plane (d > 0)."""
        q = [(T(c[0], c[2]), c[1]) for c in self.corners]
        pts = [(h, y) for (h, d), y in q if d >= -1e-9]
        for a, b in self.EDGES:
            (ha, da), ya = q[a]
            (hb, db), yb = q[b]
            if (da < -1e-9 and db > 1e-9) or (da > 1e-9 and db < -1e-9):
                t = da / (da - db)
                pts.append((ha + (hb - ha) * t, ya + (yb - ya) * t))
        if len(pts) < 3:
            return None
        hp = convex_hull(pts)
        return hp if len(hp) >= 3 else None
