"""Helpers for arranging the component library inside the ship.

Coordinates are Godot world coordinates: +X starboard, +Y up, -Z towards the bow.
A prop with yaw 0 faces +Z (glTF front); yaw 180 faces the bow, +90 faces +X, -90 faces -X.
"""
import json
import math
import random

WALL_T = 0.15          # must match ship_builder.gd
DOOR_W = 2.36          # wall cut for a door (2.0 opening + frame)
DOOR_H = 2.76
SIDES = ("N", "S", "E", "W")
FACE_YAW = {"N": 0.0, "S": 180.0, "W": 90.0, "E": -90.0}   # yaw that makes a prop face into the room


def rot(x, z, yaw):
    """Rotate local (x, z) by yaw degrees about +Y (Godot convention)."""
    t = math.radians(yaw)
    c, s = math.cos(t), math.sin(t)
    return (c * x + s * z, -s * x + c * z)


class Catalog:
    def __init__(self, path):
        d = json.load(open(path))
        self.models = {m["id"]: m for m in d["models"]}
        self.by_cat = {}
        for m in d["models"]:
            self.by_cat.setdefault(m["category"], []).append(m)
        self.use = {k: 0 for k in self.models}
        self.pen = {}             # soft penalty for models that recently failed to fit
        self.rng = random.Random(1701)

    def pick(self, cat, pred=None, label=None, rng=None):
        """Least-used model of a category (random tie-break), optionally filtered."""
        rng = rng or self.rng
        cands = self.by_cat.get(cat, [])
        if label is not None:
            cands = [c for c in cands if any(l in c["id"] for l in ([label] if isinstance(label, str) else label))] or cands
        if pred:
            cands = [c for c in cands if pred(c)]
        if not cands:
            return None
        cands = sorted(cands, key=lambda c: (self.use[c["id"]] + self.pen.get(c["id"], 0.0), rng.random()))
        return cands[0]

    def pick_any(self, cats, pred=None, rng=None):
        best = None
        rng = rng or self.rng
        pool = []
        for c in cats:
            pool += self.by_cat.get(c, [])
        if pred:
            pool = [c for c in pool if pred(c)]
        if not pool:
            return None
        pool.sort(key=lambda c: (self.use[c["id"]] + self.pen.get(c["id"], 0.0), rng.random()))
        return pool[0]

    def unused(self):
        return [self.models[k] for k, v in self.use.items() if v == 0]


class Ship:
    def __init__(self, cat):
        self.cat = cat
        self.rooms = {}
        self.decks = []
        self.doors = []
        self.lifts = []
        self.cameras = []
        self.spawn = None

    def deck_y(self, deck):
        return next(d["y"] for d in self.decks if d["id"] == deck)

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

    def link(self, a, b, kind="door", c=None, model=None, width=None, height=None, locked=False):
        """Cut matching openings through the shared wall of rooms a and b and add a door."""
        A, B = self.rooms[a], self.rooms[b]
        if abs(A.x1 - B.x0) < 1e-6:
            sa, sb, axis = "E", "W", "z"
        elif abs(A.x0 - B.x1) < 1e-6:
            sa, sb, axis = "W", "E", "z"
        elif abs(A.z1 - B.z0) < 1e-6:
            sa, sb, axis = "S", "N", "x"
        elif abs(A.z0 - B.z1) < 1e-6:
            sa, sb, axis = "N", "S", "x"
        else:
            raise ValueError(f"{a} and {b} do not touch")
        if axis == "z":
            lo, hi = max(A.z0, B.z0), min(A.z1, B.z1)
            bx = A.x1 if sa == "E" else A.x0
        else:
            lo, hi = max(A.x0, B.x0), min(A.x1, B.x1)
            bz = A.z1 if sa == "S" else A.z0
        if c is None:
            c = (lo + hi) / 2
        w = width or (DOOR_W if kind in ("door", "portal") else 4.0)
        h = height or (DOOR_H if kind in ("door", "portal") else 3.0)
        for room, side in ((A, sa), (B, sb)):
            room.openings.append({"side": side, "c": c, "w": w, "y0": 0.0, "y1": h, "kind": "door" if kind != "open" else "open"})
            room.block_door(side, c, w)
        y = A.y
        pos = [bx, y, c] if axis == "z" else [c, y, bz]
        yaw = 90.0 if axis == "z" else 0.0
        if kind == "door":
            if model is None:
                dept = B.dept if A.dept == "transit" else A.dept
                pick = self.cat.pick("door", label=self.DOOR_LABELS.get(dept, ["bulkhead"]))
                model = pick["id"]
            self.doors.append({"m": model, "pos": [round(v, 3) for v in pos], "yaw": yaw,
                               "locked": locked, "a": a, "b": b})
            self.cat.use[model] += 1
        elif kind == "portal":
            fr = self.cat.pick("doorframe")
            A.props.append({"m": fr["id"], "pos": [round(v, 3) for v in pos], "yaw": yaw, "_m": fr})
            self.cat.use[fr["id"]] += 1
        return c


class Room:
    def __init__(self, ship, rid, name, deck, rect, height=3.4, dept="transit", floor="deck_plate", tint="#dfe5ee",
                 floor_tint="#ffffff", accent="#3a6ea5"):
        self.ship, self.cat = ship, ship.cat
        self.id, self.name, self.deck = rid, name, deck
        self.x0, self.z0, self.x1, self.z1 = rect
        self.h = height
        self.dept, self.floor, self.tint, self.floor_tint, self.accent = dept, floor, tint, floor_tint, accent
        self.y = ship.deck_y(deck)
        self.props, self.openings, self.lights, self.forcefields = [], [], [], []
        self.foot = []          # occupied floor rects (x0,z0,x1,z1)
        self.cfoot = []         # occupied ceiling rects
        self.wall_used = {s: [] for s in SIDES}   # (a, b, y0, y1)
        self.rng = random.Random(sum(ord(ch) * (i + 1) for i, ch in enumerate(rid)))

    # ------------------------------------------------------ geometry
    @property
    def w(self): return self.x1 - self.x0
    @property
    def d(self): return self.z1 - self.z0
    @property
    def cx(self): return (self.x0 + self.x1) / 2
    @property
    def cz(self): return (self.z0 + self.z1) / 2

    def inner(self, m=0.0):
        return (self.x0 + WALL_T + m, self.z0 + WALL_T + m, self.x1 - WALL_T - m, self.z1 - WALL_T - m)

    def occupancy(self):
        area = 0.0
        for p in self.props:
            fp = p.get("_fp")
            if fp and p["_m"]["mount"] == "floor":
                area += (fp[2] - fp[0]) * (fp[3] - fp[1])
        return area / max(self.w * self.d, 1.0)

    def block_door(self, side, c, w):
        depth = 2.4
        if side == "N": r = (c - w / 2 - 0.2, self.z0, c + w / 2 + 0.2, self.z0 + depth)
        elif side == "S": r = (c - w / 2 - 0.2, self.z1 - depth, c + w / 2 + 0.2, self.z1)
        elif side == "W": r = (self.x0, c - w / 2 - 0.2, self.x0 + depth, c + w / 2 + 0.2)
        else: r = (self.x1 - depth, c - w / 2 - 0.2, self.x1, c + w / 2 + 0.2)
        self.foot.append(r)
        self.wall_used[side].append((c - w / 2 - 0.1, c + w / 2 + 0.1, 0.0, 99.0))

    def add_window(self, side, c, w, y0=0.9, y1=2.6):
        self.openings.append({"side": side, "c": c, "w": w, "y0": y0, "y1": y1, "kind": "window"})
        self.wall_used[side].append((c - w / 2 - 0.1, c + w / 2 + 0.1, 0.0, 99.0))

    # ------------------------------------------------------ placement
    def free(self, r, margin=0.0, ignore_blocked=False):
        x0, z0, x1, z1 = r
        ix0, iz0, ix1, iz1 = self.inner()
        if x0 < ix0 - 1e-3 or z0 < iz0 - 1e-3 or x1 > ix1 + 1e-3 or z1 > iz1 + 1e-3:
            return False
        for a in self.foot:
            if x0 < a[2] - margin and x1 > a[0] + margin and z0 < a[3] - margin and z1 > a[1] + margin:
                return False
        return True

    def place(self, m, cx, cz, yaw=0.0, y=None, check=True, reserve=True, scale=1.0, solid=None, light=None, margin=0.0):
        """Place model `m` (catalog entry or id) with its footprint centre at (cx, cz)."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        lo, hi = m["bounds_min"], m["bounds_max"]
        lx, lz = (lo[0] + hi[0]) / 2 * scale, (lo[2] + hi[2]) / 2 * scale
        ox, oz = rot(lx, lz, yaw)
        px, pz = cx - ox, cz - oz
        pts = [rot(x * scale, z * scale, yaw) for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
        fp = (px + min(p[0] for p in pts), pz + min(p[1] for p in pts), px + max(p[0] for p in pts), pz + max(p[1] for p in pts))
        floor_item = m["mount"] in ("floor",)
        ceil_item = m["mount"] == "ceiling"
        if check and floor_item:
            if not self.free(fp, margin):
                return None
        if ceil_item:
            ix0, iz0, ix1, iz1 = self.inner()
            if check and (fp[0] < ix0 or fp[2] > ix1 or fp[1] < iz0 or fp[3] > iz1):
                return None
            if check and any(fp[0] < a[2] and fp[2] > a[0] and fp[1] < a[3] and fp[3] > a[1] for a in self.cfoot):
                return None
            self.cfoot.append(fp)
        if y is None:
            if m["mount"] == "floor": y = self.y
            elif m["mount"] == "ceiling": y = self.y + self.h
            elif m["mount"] == "wall": y = self.y + (m.get("mount_y") or 1.5)
            else: y = self.y
        p = {"m": m["id"], "pos": [round(px, 3), round(y, 3), round(pz, 3)], "yaw": round(yaw, 2)}
        if scale != 1.0: p["scale"] = scale
        if solid is not None: p["solid"] = solid
        self.props.append(p)
        self.cat.use[m["id"]] += 1
        if reserve and floor_item:
            self.foot.append(fp)
        p["_fp"] = fp
        p["_m"] = m
        return p

    def against_wall(self, side, m, along, gap=0.04, y=None, check=True, yaw_extra=0.0, reserve=True, scale=1.0, solid=None):
        """Place a floor/wall item with its back to `side` wall, centred at `along` (x for N/S, z for E/W)."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        lo, hi = m["bounds_min"], m["bounds_max"]
        yaw = FACE_YAW[side] + yaw_extra
        ix0, iz0, ix1, iz1 = self.inner()
        hw = m["size"][0] * scale / 2
        if m["mount"] == "floor" and m["size"][1] > 0.6:
            for (ua, ub, uy0, uy1) in self.wall_used[side]:
                if uy1 >= 50 and along - hw < ub and along + hw > ua:
                    return None                       # would block a window / doorway
        cdist = gap + (hi[2] - lo[2]) * scale / 2      # wall -> centre of the footprint
        if side == "N": cx, cz = along, iz0 + cdist
        elif side == "S": cx, cz = along, iz1 - cdist
        elif side == "W": cx, cz = ix0 + cdist, along
        else: cx, cz = ix1 - cdist, along
        p = self.place(m, cx, cz, yaw, y=y, check=check, reserve=reserve, scale=scale, solid=solid)
        if p is not None and m["mount"] == "floor":
            hw = m["size"][0] * scale / 2
            self.wall_used[side].append((along - hw, along + hw, 0.0, m["size"][1] * scale))
        return p

    def wall_span_free(self, side, a, b, y0=0.0, y1=99.0):
        for (ua, ub, uy0, uy1) in self.wall_used[side]:
            if a < ub and b > ua and y0 < uy1 and y1 > uy0:
                return False
        return True

    def wall_item(self, side, m, along, y=None, gap=0.0, check=True):
        """Wall-mounted item (origin on the wall face). Returns placement or None if the span is taken."""
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        wd = m["size"][0]
        yy = (m.get("mount_y") or 1.5) if y is None else y
        if check and not self.wall_span_free(side, along - wd / 2, along + wd / 2, yy - m["size"][1] / 2 - 0.02, yy + m["size"][1] / 2 + 0.02):
            return None
        ix0, iz0, ix1, iz1 = self.inner()
        yaw = FACE_YAW[side]
        lo, hi = m["bounds_min"], m["bounds_max"]
        lx = (lo[0] + hi[0]) / 2
        if side == "N": x, z = along, self.z0 + WALL_T + gap
        elif side == "S": x, z = along, self.z1 - WALL_T - gap
        elif side == "W": x, z = self.x0 + WALL_T + gap, along
        else: x, z = self.x1 - WALL_T - gap, along
        ox, oz = rot(lx, 0, yaw)
        p = {"m": m["id"], "pos": [round(x - ox, 3), round(self.y + yy, 3), round(z - oz, 3)], "yaw": yaw, "_m": m}
        self.props.append(p)
        self.cat.use[m["id"]] += 1
        self.wall_used[side].append((along - wd / 2, along + wd / 2, yy - m["size"][1] / 2, yy + m["size"][1] / 2))
        return p

    def ceiling_item(self, m, x, z, yaw=0.0, light=None):
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        p = self.place(m, x, z, yaw, y=self.y + self.h, check=False)
        return p

    def on_top(self, host, m, dx=0.0, dz=0.0, yaw=None):
        """Stand a small item on the flat top of a placed host prop."""
        if host is None:
            return None
        if isinstance(m, str):
            m = self.cat.models[m]
        if m is None:
            return None
        hm = host["_m"]
        ty = hm.get("top_y")
        if ty is None:
            return None
        hy = host["pos"][1]
        fp = host["_fp"]
        cx, cz = (fp[0] + fp[2]) / 2 + dx, (fp[1] + fp[3]) / 2 + dz
        if not (fp[0] + 0.05 < cx < fp[2] - 0.05 and fp[1] + 0.05 < cz < fp[3] - 0.05):
            return None
        return self.place(m, cx, cz, host["yaw"] if yaw is None else yaw, y=hy + ty, check=False)

    # ------------------------------------------------------ patterns
    def run(self, side, cats, start=None, end=None, gap=0.04, spacing=0.05, pred=None, limit=99, y=None,
            wall_mount=False, pick_label=None, margin=0.0, max_w=None):
        """Fill a wall side with a row of items picked (least-used first) from `cats`."""
        if isinstance(cats, str):
            cats = [cats]
        ix0, iz0, ix1, iz1 = self.inner()
        if side in ("N", "S"):
            a0, a1 = ix0, ix1
        else:
            a0, a1 = iz0, iz1
        pos = (a0 if start is None else start)
        end = a1 if end is None else end
        placed = []
        tries = 0
        while pos < end - 0.2 and len(placed) < limit and tries < 60:
            tries += 1
            m = self.cat.pick_any(cats, pred=pred, rng=self.rng)
            if m is None:
                break
            wd = m["size"][0] if side in ("N", "S") else m["size"][0]
            if max_w and wd > max_w:
                pos += 0.3
                continue
            if pos + wd > end + 1e-3:
                # try a narrower item once, else stop
                narrow = self.cat.pick_any(cats, pred=lambda c: c["size"][0] <= end - pos and (pred is None or pred(c)), rng=self.rng)
                if narrow is None:
                    break
                m = narrow
                wd = m["size"][0]
            c = pos + wd / 2
            p = (self.wall_item(side, m, c, y=y) if (wall_mount or m["mount"] == "wall")
                 else self.against_wall(side, m, c, gap=gap))
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
        nx = max(1, int(round((self.w - 2 * x_margin) / spacing)))
        nz = max(1, int(round((self.d - 2 * x_margin) / spacing)))
        k = 0
        for i in range(nx):
            for j in range(nz):
                x = self.x0 + x_margin + (self.w - 2 * x_margin) * (i + 0.5) / nx
                z = self.z0 + x_margin + (self.d - 2 * x_margin) * (j + 0.5) / nz
                m = self.cat.pick_any(list(cats), pred=pred, rng=self.rng)
                if m:
                    self.place(m, x, z, 0.0, y=self.y + self.h, check=False)
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
            q = {k: v for k, v in p.items() if not k.startswith("_")}
            props.append(q)
        return {"id": self.id, "name": self.name, "deck": self.deck, "rect": [self.x0, self.z0, self.x1, self.z1],
                "height": self.h, "dept": self.dept, "floor": self.floor, "tint": self.tint,
                "floor_tint": self.floor_tint, "accent": self.accent, "openings": self.openings,
                "lights": self.lights, "forcefields": self.forcefields, "props": props}
