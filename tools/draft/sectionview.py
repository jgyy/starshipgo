"""Section-view drawing routines.

A Cut is a vertical plane x = c (looking +X, bow to the left, h = z) or z = c (looking aft, h = -x, port to the right).
Everything is first transformed to (h, d) where d > 0 is the distance behind the cut plane."""
import math

from shipmodel import SLAB_T, clip_half, line_interval, rect_poly
from planview import blend, OUTLINE_ONLY


class SV:
    """Section view: (h metres, y metres) -> paper mm (y up)."""

    def __init__(self, s, ox, oy, h0, y0):
        self.s, self.ox, self.oy, self.h0, self.y0 = s, ox, oy, h0, y0

    def xy(self, h, y):
        return (self.ox + (h - self.h0) * self.s, self.oy - (y - self.y0) * self.s)

    def box(self, h0, h1, y0, y1):
        a, b = self.xy(h0, y1), self.xy(h1, y0)
        return [a, (b[0], a[1]), b, (a[0], b[1])]


class Cut:
    def __init__(self, axis, c):
        self.axis, self.c = axis, c
        self.v = (1.0, 0.0) if axis == "x" else (0.0, 1.0)

    def T(self, x, z):
        if self.axis == "x":
            return (z, x - self.c)
        return (-x, z - self.c)

    def inv(self, h, d):
        if self.axis == "x":
            return (self.c + d, h)
        return (-h, self.c + d)

    def poly(self, pts):
        return [self.T(x, z) for x, z in pts]

    def iv(self, pts):
        return line_interval(self.poly(pts), 1, 0.0)

    @property
    def label(self):
        return "LOOKING STARBOARD (+X)" if self.axis == "x" else "LOOKING AFT (+Z)"

    def hmin_label(self):
        return "BOW" if self.axis == "x" else "STBD"

    def hmax_label(self):
        return "STERN" if self.axis == "x" else "PORT"


def subtract(iv, holes):
    """Interval iv=(a,b) minus a list of (a,b) holes -> list of intervals."""
    segs = [iv]
    for h0, h1 in holes:
        nxt = []
        for a, b in segs:
            if h1 <= a or h0 >= b:
                nxt.append((a, b))
                continue
            if h0 > a:
                nxt.append((a, h0))
            if h1 < b:
                nxt.append((h1, b))
        segs = nxt
    return segs


def shade(d, dmax, lo=(243, 245, 248), hi=(212, 218, 226)):
    t = 0.0 if dmax <= 0 else max(0.0, min(1.0, d / dmax))
    return "#%02x%02x%02x" % tuple(int(lo[i] + (hi[i] - lo[i]) * t) for i in range(3))


def _edges_h(cut, room):
    """Edges in (h,d) space."""
    out = []
    for e in room.edges:
        ha, da = cut.T(*e["a"])
        hb, db = cut.T(*e["b"])
        out.append((e, (ha, da), (hb, db)))
    return out


def crossing_edges(cut, room):
    res = []
    for e, (ha, da), (hb, db) in _edges_h(cut, room):
        if da == db:
            continue
        if min(da, db) <= 1e-9 and max(da, db) >= -1e-9 and not (abs(da) < 1e-9 and abs(db) < 1e-9):
            if (da < -1e-9 and db < -1e-9) or (da > 1e-9 and db > 1e-9):
                continue
            t = da / (da - db)
            res.append((ha + (hb - ha) * t, e, t * e["len"] if True else 0))
    res.sort(key=lambda r: r[0])
    return res


def draw_room_section(sh, sv, cut, room, ship, cat, phase, depth_max=14.0, labels=False, info=None, detail=True):
    """phase 'beyond': visible wall faces, openings and props behind the plane.  phase 'cut': slabs, cut walls, cut props."""
    iv = cut.iv(room.poly)
    if iv is None or iv[1] - iv[0] < 1e-3:
        return None
    y, h = room.y, room.h
    if phase == "beyond":
        _beyond_walls(sh, sv, cut, room, y, h, depth_max, info)
        _props(sh, sv, cut, room, cat, y, h, False, depth_max, labels, info)
        return iv
    # ---- cut phase
    iiv = cut.iv(room.inner) if room.inner else None
    # slabs
    fh = []
    for r in room.floor_holes:
        q = cut.iv(rect_poly(r))
        if q:
            fh.append(q)
    ch = []
    for r in room.ceiling_holes:
        q = cut.iv(rect_poly(r))
        if q:
            ch.append(q)
    for a, b in subtract(iv, fh):
        sh.poly(sv.box(a, b, y - SLAB_T, y), "n", "url(#hSlab)")
    for a, b in subtract(iv, ch):
        sh.poly(sv.box(a, b, y + h, y + h + SLAB_T), "n", "url(#hSlab)")
    # walls
    cr = crossing_edges(cut, room)
    if iiv is None:
        segs = [(iv[0], iv[1], cr[0][1] if cr else None, cr[0][0] if cr else 0)]
    else:
        segs = []
        if cr:
            segs.append((iv[0], iiv[0], cr[0][1], cr[0][2]))
            segs.append((iiv[1], iv[1], cr[-1][1], cr[-1][2]))
    for a, b, e, t in segs:
        if b - a < 1e-4:
            continue
        _cut_wall(sh, sv, room, e, t, a, b, y, h)
    _props(sh, sv, cut, room, cat, y, h, True, depth_max, labels, info)
    _forcefields(sh, sv, cut, room)
    return iv


def _forcefields(sh, sv, cut, room):
    for f in room.forcefields:
        fx, fy, fz = f["pos"]
        half = f["size"][0] / 2
        yaw = math.radians(f.get("yaw", 0.0))
        dx, dz = math.cos(yaw) * half, -math.sin(yaw) * half
        ha, da = cut.T(fx - dx, fz - dz)
        hb, db = cut.T(fx + dx, fz + dz)
        y0, y1 = fy - f["size"][1] / 2, fy + f["size"][1] / 2
        if (da <= 0 <= db) or (db <= 0 <= da):
            t = 0.5 if da == db else da / (da - db)
            hh = ha + (hb - ha) * t
            sh.line(*sv.xy(hh, y0), *sv.xy(hh, y1), "cl")
            sh.text(sv.xy(hh, 0)[0] + 1.2, sv.xy(0, y1)[1] + 3, "FORCE FIELD", 1.5, fill="#2060a0")
        elif da > 0 and db > 0:
            sh.poly(sv.box(min(ha, hb), max(ha, hb), y0, y1), "cl", "#9fd8f0", op=0.25)

def _opening_t(room, o, e):
    (p0, p1), _ = room.opening_seg(o)
    ax, az = e["a"]
    ux, uz = e["u"]
    t0 = (p0[0] - ax) * ux + (p0[1] - az) * uz
    t1 = (p1[0] - ax) * ux + (p1[1] - az) * uz
    return min(t0, t1), max(t0, t1)


def _cut_wall(sh, sv, room, e, t, a, b, y, h):
    fill = "url(#hHull)" if (e and e["hull"]) else "#1c1c1c"
    op = None
    if e is not None:
        for o in room.openings:
            if o["side"] != e["side"]:
                continue
            t0, t1 = _opening_t(room, o, e)
            if t0 - 1e-6 <= t <= t1 + 1e-6:
                op = o
                break
    if op is None:
        sh.poly(sv.box(a, b, y, y + h), "n", fill)
        return
    if op["kind"] == "window":
        if op["y0"] > 0.01:
            sh.poly(sv.box(a, b, y, y + op["y0"]), "n", fill)
        if op["y1"] < h - 0.01:
            sh.poly(sv.box(a, b, y + op["y1"], y + h), "n", fill)
        m = (a + b) / 2
        sh.poly(sv.box(m - 0.03, m + 0.03, y + op["y0"], y + op["y1"]), "f", "#bfe3f5")
        sh.poly(sv.box(a - 0.02, b + 0.02, y + op["y0"] - 0.06, y + op["y0"]), "f", "#777")
        sh.poly(sv.box(a - 0.02, b + 0.02, y + op["y1"], y + op["y1"] + 0.06), "f", "#777")
    else:
        if op["y1"] < h - 0.01:
            sh.poly(sv.box(a, b, y + op["y1"], y + h), "n", fill)


def _beyond_walls(sh, sv, cut, room, y, h, dmax, info):
    vis = []
    for e, (ha, da), (hb, db) in _edges_h(cut, room):
        if e["n"][0] * cut.v[0] + e["n"][1] * cut.v[1] > -0.02:
            continue
        if da <= 1e-9 and db <= 1e-9:
            continue
        # clip to d >= 0
        u0, u1 = 0.0, 1.0
        if da < 0:
            u0 = da / (da - db)
        if db < 0:
            u1 = da / (da - db)
        ta, tb = u0 * e["len"], u1 * e["len"]
        dm = max(0.0, (max(da, 0) + max(db, 0)) / 2)
        vis.append((dm, e, ta, tb, ha + (hb - ha) * u0, ha + (hb - ha) * u1))
    vis.sort(key=lambda v: -v[0])
    for dm, e, ta, tb, h0, h1 in vis:
        sh.poly(sv.box(min(h0, h1), max(h0, h1), y, y + h), "x", shade(dm, dmax))
        for o in room.openings:
            if o["side"] != e["side"]:
                continue
            t0, t1 = _opening_t(room, o, e)
            t0, t1 = max(t0, ta), min(t1, tb)
            if t1 - t0 < 0.05:
                continue
            f0 = (t0 - ta) / max(tb - ta, 1e-9)
            f1 = (t1 - ta) / max(tb - ta, 1e-9)
            o0, o1 = h0 + (h1 - h0) * f0, h0 + (h1 - h0) * f1
            lo, hi = min(o0, o1), max(o0, o1)
            if o["kind"] == "window":
                sh.poly(sv.box(lo, hi, y + o["y0"], y + o["y1"]), "n", "url(#hGlass)")
                sh.line(*sv.xy((lo + hi) / 2, y + o["y0"]), *sv.xy((lo + hi) / 2, y + o["y1"]), "f")
            else:
                lk = None
                for l in room.links:
                    if l["side"] == o["side"] and abs(l["c"] - o["c"]) < 1e-3:
                        lk = l
                fl = "#fbfbfb" if (lk and lk["kind"] == "open") else "#c3cad6"
                sh.poly(sv.box(lo, hi, y, y + o["y1"]), "n", fl)
                if not (lk and lk["kind"] == "open"):
                    sh.line(*sv.xy((lo + hi) / 2, y), *sv.xy((lo + hi) / 2, y + o["y1"]), "f")
            if info is not None:
                info.setdefault("openings", []).append((lo, hi, o, dm))


def _silhouette(cut, p):
    tp = cut.poly(p.corners)
    if min(q[1] for q in tp) >= -1e-9:
        return tp, None, (min(q[0] for q in tp), max(q[0] for q in tp), min(q[1] for q in tp))
    if max(q[1] for q in tp) <= 1e-9:
        return None, None, None
    iv = line_interval(tp, 1, 0.0)
    back = clip_half(tp, 0, 1, 0.0)
    bs = (min(q[0] for q in back), max(q[0] for q in back), 0.0) if back else None
    return None, iv, bs


def _props(sh, sv, cut, room, cat, y, h, cut_phase, dmax, labels, info):
    beyond, cuts = [], []
    for p in room.props:
        tp, iv, bs = _silhouette(cut, p)
        if tp is None and iv is None:
            continue
        if iv is None:
            beyond.append((bs[2], p, bs))
        else:
            cuts.append((p, iv, bs))
            if bs:
                beyond.append((0.0, p, bs))
    if not cut_phase:
        beyond.sort(key=lambda b: -b[0])
        for dmin, p, bs in beyond:
            fill = blend(cat.fill(p.m), min(0.75, 0.35 + dmin / dmax * 0.4))
            if p.mount == "ceiling":
                sh.poly(sv.box(bs[0], bs[1], p.y0, p.y1), "dot", "none")
            elif p.cat in OUTLINE_ONLY:
                sh.poly(sv.box(bs[0], bs[1], p.y0, p.y1), "f", "none")
            else:
                sh.poly(sv.box(bs[0], bs[1], p.y0, p.y1), "f", fill)
            if labels and p.mount == "wall" and info is not None:
                info.setdefault("wall_items", []).append((bs[0], bs[1], p))
    else:
        for p, iv, bs in sorted(cuts, key=lambda c: c[0].y0):
            fill = "none" if p.cat in OUTLINE_ONLY else blend(cat.fill(p.m), 0.05)
            sh.poly(sv.box(iv[0], iv[1], p.y0, p.y1), "m", fill)
            if labels and p.mount == "wall" and info is not None:
                info.setdefault("wall_items", []).append((iv[0], iv[1], p))


# ------------------------------------------------------------------ stairs
def flight_profile(f):
    """Sawtooth outline of a flight in (x, y): list of points along the nosing, plus underside."""
    x0, y0, d, n, t = f["x"], f["y"], f["dir"], f["n"], f["tread"]
    r = f["rise"] / n
    top = [(x0, y0)]
    for k in range(n):
        xk = x0 + d * t * k
        top.append((xk, y0 + (k + 1) * r))
        if k < n - 1:
            top.append((x0 + d * t * (k + 1), y0 + (k + 1) * r))
    xe = x0 + d * t * (n - 1)
    under = [(xe, y0 + n * r - 0.24), (x0, y0)]
    return top + under


def draw_stairs_section(sh, sv, cut, ship, phase, region=None, handrail=False, only=None):
    """region: room polygon (plan) - only flights inside it are drawn.  Flights: cut / beyond / behind."""
    items = []
    for st in ship.stairs:
        if only and st["id"] not in only:
            continue
        runs, _ = ship.stair_geom(st["id"])
        for run in runs:
            for f in run["flights"]:
                if region is not None and not (_inside(region, f["x"], f["z"]) or _inside(region, f["x"] + f["dir"] * 1.0, f["z"])):
                    continue
                items.append(("f", f, run))
            items.append(("l", run, run))
    for kind, o, run in items:
        if kind == "f":
            _flight_section(sh, sv, cut, o, phase, handrail)
        else:
            if region is not None:
                lr = o["landing"]
                if not _inside(region, (lr[0] + lr[2]) / 2, (lr[1] + lr[3]) / 2):
                    continue
            _landing_section(sh, sv, cut, o, phase)


def _inside(poly, x, z):
    n = len(poly)
    s = 0
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if abs(c) < 1e-9:
            continue
        sg = 1 if c > 0 else -1
        if s == 0:
            s = sg
        elif s != sg:
            return False
    return True


def _flight_section(sh, sv, cut, f, phase, handrail):
    w = f["w"]
    z0, z1 = f["z"] - w / 2, f["z"] + w / 2
    xe = f["x"] + f["dir"] * f["tread"] * (f["n"] - 1)
    xa, xb = min(f["x"], xe), max(f["x"], xe)
    r = f["rise"] / f["n"]
    if cut.axis == "z":
        prof = flight_profile(f)
        pts = [sv.xy(-x, yy) for x, yy in prof]
        if z0 - 1e-9 <= cut.c <= z1 + 1e-9:
            if phase == "cut":
                sh.poly(pts, "m", "url(#hSlab)")
                if handrail:
                    _handrail(sh, sv, f, lambda x: -x)
        elif z0 > cut.c:
            if phase == "beyond":
                sh.poly(pts, "f", "#e3e7ee")
                if handrail:
                    _handrail(sh, sv, f, lambda x: -x)
        else:
            if phase == "beyond":
                sh.poly(pts, "hid")
    else:
        if xa - 1e-9 <= cut.c <= xb + 1e-9 or (cut.c >= xa and cut.c <= xb):
            if phase == "cut":
                k = int((cut.c - f["x"]) * f["dir"] / f["tread"] + 1e-9)
                k = max(0, min(k, f["n"] - 1))
                yt = f["y"] + (k + 1) * r
                sh.poly(sv.box(z0, z1, yt - 0.24, yt), "m", "url(#hSlab)")
        elif xa > cut.c:
            if phase == "beyond":
                sh.poly(sv.box(z0, z1, f["y"], f["y"] + f["rise"]), "f", "#e3e7ee")


def _handrail(sh, sv, f, hmap):
    r = f["rise"] / f["n"]
    x0, y0, d, t, n = f["x"], f["y"], f["dir"], f["tread"], f["n"]
    xe = x0 + d * t * (n - 1)
    p0 = sv.xy(hmap(x0), y0 + r + 0.9)
    p1 = sv.xy(hmap(xe), y0 + n * r + 0.9)
    sh.line(*p0, *p1, "n")
    for k in (0, n - 1):
        x = x0 + d * t * k
        a = sv.xy(hmap(x), y0 + (k + 1) * r)
        b = sv.xy(hmap(x), y0 + (k + 1) * r + 0.9)
        sh.line(*a, *b, "f")


def _landing_section(sh, sv, cut, run, phase):
    lr = run["landing"]
    ly = run["landing_y"]
    if cut.axis == "z":
        if lr[1] - 1e-9 <= cut.c <= lr[3] + 1e-9 and phase == "cut":
            sh.poly(sv.box(-lr[2], -lr[0], ly - 0.24, ly), "m", "url(#hSlab)")
        elif lr[1] > cut.c and phase == "beyond":
            sh.poly(sv.box(-lr[2], -lr[0], ly - 0.24, ly), "f", "#e3e7ee")
    else:
        if lr[0] - 1e-9 <= cut.c <= lr[2] + 1e-9:
            if phase == "cut":
                sh.poly(sv.box(lr[1], lr[3], ly - 0.24, ly), "m", "url(#hSlab)")
        elif lr[0] > cut.c and phase == "beyond":
            sh.poly(sv.box(lr[1], lr[3], ly - 0.24, ly), "f", "#e3e7ee")


# ------------------------------------------------------------------ annotations
def level_marks(sh, sv, x, levels, right=True):
    for y, lab in levels:
        px, py = sv.xy(0, y)
        sh.level_mark(x, py, lab, 1.6, right)


def lv(y):
    return "%+.3f" % y


def room_section_dims(sh, sv, cut, room, iv, info, ship):
    """Vertical and horizontal dimensions around a single room section."""
    y, h = room.y, room.h
    a, b = iv
    xl, _ = sv.xy(a, 0)
    xr, _ = sv.xy(b, 0)
    # right chain (heights)
    xd = xr + 6.0
    ys = [sv.xy(0, v)[1] for v in (y + h + SLAB_T, y + h, y, y - SLAB_T)]
    sh.chain_v(list(reversed(ys)), xd, ["300", str(int(round(h * 1000))), "300"][::-1], ext_x=xr + 1.0)
    # floor-to-floor
    y_ff = y + 4.0
    xd2 = xr + 13.0
    sh.dim_v(sv.xy(0, y + 0)[1], sv.xy(0, y_ff)[1], xd2, "4000 F-F" if room.deck > 1 or True else "", ext_x=xr + 1.0)
    # overall height slab to slab
    # levels on the left
    xlm = xl - 16.0
    sh.level_mark(xlm, sv.xy(0, y)[1], lv(y) + " FFL", 1.6, True)
    sh.level_mark(xlm, sv.xy(0, y + h)[1], lv(y + h) + " CEIL", 1.6, True)
    sh.level_mark(xlm, sv.xy(0, y + h + SLAB_T)[1], lv(y + h + SLAB_T) + " SLAB", 1.4, True)
    # bottom chain: walls and visible openings
    yb = sv.xy(0, y - SLAB_T)[1] + 6.0
    pts = [a, b]
    ops = []
    for lo, hi, o, dm in info.get("openings", []):
        if a - 1e-6 <= lo and hi <= b + 1e-6 and o["kind"] != "window":
            ops.append((lo, hi))
    ops.sort()
    # merge touching duplicates
    merged = []
    for lo, hi in ops:
        if merged and lo < merged[-1][1] + 0.02:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    for lo, hi in merged:
        pts += [lo, hi]
    pts = sorted(set(round(p, 3) for p in pts))
    xs = [sv.xy(p, 0)[0] for p in pts]
    labels = [str(int(round((pts[i + 1] - pts[i]) * 1000))) for i in range(len(pts) - 1)]
    if len(pts) > 2:
        sh.chain_h(xs, yb, labels, ext_y=sv.xy(0, y - SLAB_T)[1] + 1.0)
    if len(pts) > 2:
        sh.dim_h(xl, xr, yb + 6.0, str(int(round((b - a) * 1000))), ext_y=yb + 0.6)
    else:
        sh.dim_h(xl, xr, yb, str(int(round((b - a) * 1000))), ext_y=sv.xy(0, y - SLAB_T)[1] + 1.0)
    return yb + 6.0


def wall_item_labels(sh, sv, info, room, maxn=10):
    items = info.get("wall_items", [])
    items = sorted(items, key=lambda t: -(t[1] - t[0]) * (t[2].y1 - t[2].y0))[:maxn]
    for lo, hi, p in items:
        ymid = p.pos[1]
        x, yy = sv.xy((lo + hi) / 2, ymid)
        lab = "%d" % int(round((ymid - room.y) * 1000))
        sh.label(x, yy + 0.5, lab, 1.2, "middle", fill="#444")
