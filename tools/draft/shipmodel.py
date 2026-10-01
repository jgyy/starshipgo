"""Ship data wrapper + small geometry helpers for the drafting tool (pure standard library)."""
import colorsys
import json
import math

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
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
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
        with open(ship_path, encoding="utf-8") as f:
            d = json.load(f)
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
