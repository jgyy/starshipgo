"""Reusable room-dressing helpers for the ship layout.

All helpers work on the polygon rooms of shiplib.Room and attribute every placement to the room's current
BOM line (``R.line(title, why)``).  Nothing here places items at random: positions are either explicit or come
from regular patterns (runs along a wall, grids, arcs, chairs around a table).
"""
import math

from shiplib import rot


# ------------------------------------------------------------------ geometry helpers
def yaw_to(x0, z0, x1, z1):
    """Prop yaw so its front (+Z) faces the target point."""
    return math.degrees(math.atan2(x1 - x0, z1 - z0))


def look(eye, target):
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return round(yaw, 1), round(pitch, 1)


def by_size(maxw=None, minw=None, maxd=None, maxh=None, minh=None, mind=None):
    """Catalog predicate on the model size (width x, height y, depth z)."""
    def f(c):
        s = c["size"]
        return ((maxw is None or s[0] <= maxw) and (minw is None or s[0] >= minw) and
                (maxd is None or s[2] <= maxd) and (mind is None or s[2] >= mind) and
                (maxh is None or s[1] <= maxh) and (minh is None or s[1] >= minh))
    return f


def floor_only(c):
    return c["mount"] == "floor"


def wall_only(c):
    return c["mount"] == "wall"


def ceiling_only(c):
    return c["mount"] == "ceiling"


def both(*preds):
    return lambda c: all(p(c) for p in preds)


# ------------------------------------------------------------------ dressing helpers
def light_room(R, spacing=4.2, cats=("ceilinglight",), color="#fff0dd", energy=1.5, **kw):
    """Ceiling light fixtures on a regular grid over the room's shape (each carries a real light)."""
    R.light_grid(cats=cats, spacing=spacing, color=color, energy=energy, **kw)


def dress_walls(R, cats=("wallpanel",), sides="NSEW", pred=None, y=None):
    for s in sides:
        if R.edge(s):
            R.run(s, list(cats), wall_mount=True, spacing=0.02, pred=pred, y=y)


def ceiling_runs(R, cat="duct", along="x", n=2, off=1.2, pred=None):
    """Ducts / trays running along the ceiling in n parallel runs (only where they fit inside the room)."""
    ix0, iz0, ix1, iz1 = R.inner()
    base = pred or (lambda c: True)
    for k in range(n):
        if along == "x":
            z = iz0 + off + (iz1 - iz0 - 2 * off) * (k + 0.5) / n
            x = ix0 + 0.6
            while x < ix1 - 0.6:
                m = R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling" and c["size"][0] > c["size"][2] and base(c), rng=R.rng) or \
                    R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling" and base(c), rng=R.rng)
                if not m:
                    return
                w = max(m["size"][0], 0.5)
                if R.place(m, x + w / 2, z, 0.0, y=R.y + R.h, check=True):
                    x += w + 0.05
                else:
                    x += 0.5
        else:
            x = ix0 + off + (ix1 - ix0 - 2 * off) * (k + 0.5) / n
            z = iz0 + 0.6
            while z < iz1 - 0.6:
                m = R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling" and base(c), rng=R.rng)
                if not m:
                    return
                w = max(m["size"][0], 0.5)
                if R.place(m, x, z + w / 2, 90.0, y=R.y + R.h, check=True):
                    z += w + 0.05
                else:
                    z += 0.5


def signs(R, side, c, dept_label=None, y=3.05):
    m = R.cat.pick("sign", label=dept_label, pred=lambda s: s["mount"] == "wall" and s["size"][0] < 1.6 and s["size"][1] < 0.7)
    if m:
        return R.wall_item(side, m, c, y=y)
    return None


def safety(R, side, c, label=None):
    m = R.cat.pick("safety", label=label, pred=lambda s: s["mount"] == "wall")
    if m:
        return R.wall_item(side, m, c)
    return None


def tabletop(R, host, cats, n=3, prefer=None):
    """Put small table-mount items on top of a host prop.  Items are spread over the top so they do not overlap."""
    if host is None:
        return []
    fp = host["_fp"]
    w, d = fp[2] - fp[0], fp[3] - fp[1]
    out = []
    slots = [(-0.3, -0.25), (0.3, 0.25), (0.3, -0.25), (-0.3, 0.25), (0.0, 0.0), (0.0, -0.3), (0.0, 0.3)]
    0
    for (sx, sz) in slots:
        if len(out) >= n:
            break
        m = None
        if prefer:
            m = R.cat.pick(prefer[0], label=prefer[1] if len(prefer) > 1 else None,
                           pred=lambda c: c["mount"] == "table" and c["size"][0] < min(w, 0.9) * 0.6 and c["size"][2] < min(d, 0.9) * 0.6)
        if m is None:
            m = R.cat.pick_any(list(cats), pred=lambda c: c["mount"] == "table" and c["size"][0] < min(w, 0.9) * 0.6 and c["size"][2] < min(d, 0.9) * 0.6, rng=R.rng)
        if m:
            p = R.on_top(host, m, dx=sx * w * 0.6, dz=sz * d * 0.6, yaw=host["yaw"])
            if p:
                out.append(p)
    return out


def chairs_around(R, cx, cz, hw, hd, cats=("chair",), step=1.0, pred=None, ends=False):
    """Chairs on both long sides of a table centred at (cx, cz) with half extents hw (x) and hd (z), facing it."""
    n = 0
    k = max(1, int(2 * hw // step))
    xs = [cx - hw + (2 * hw) * (i + 0.5) / k for i in range(k)]
    for x in xs:
        for sign in (-1, 1):
            z = cz + sign * (hd + 0.4)
            yaw = 0.0 if sign < 0 else 180.0
            m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
            if m and R.place(m, x, z, yaw):
                n += 1
    if ends:
        for sign in (-1, 1):
            m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
            if m and R.place(m, cx + sign * (hw + 0.4), cz, -90.0 if sign < 0 else 90.0):
                n += 1
    return n


def central_table(R, cat="table", pred=None, cx=None, cz=None, yaw=0.0, label=None):
    m = R.cat.pick(cat, pred=pred, label=label)
    if not m:
        return None
    return R.place(m, R.cx if cx is None else cx, R.cz if cz is None else cz, yaw)


def seat_behind(R, con, cats=("seat",), yaw=None, gap=0.55, pred=None):
    """Put a chair behind a console that stands with its back to the N wall (chair on the +Z side)."""
    if con is None:
        return None
    fp = con["_fp"]
    m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
    if m is None:
        return None
    x = (fp[0] + fp[2]) / 2
    return R.place(m, x, fp[3] + gap + m["size"][2] / 2, 180.0 if yaw is None else yaw)


def seat_facing(R, host, cats=("chair",), gap=0.45, pred=None, label=None):
    """Chair in front of a prop `host` (on the side its front (+Z) faces), turned to face it."""
    if host is None:
        return None
    m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng) if label is None else R.cat.pick(cats[0], label=label, pred=pred)
    if m is None:
        return None
    hm = host["_m"]
    lo, hi = hm["bounds_min"], hm["bounds_max"]
    fx, fz = (lo[0] + hi[0]) / 2, hi[2] + gap + m["size"][2] / 2      # in host-local space, in front of the host
    ox, oz = rot(fx, fz, host["yaw"])
    return R.place(m, host["pos"][0] + ox, host["pos"][2] + oz, host["yaw"] + 180.0)


def arc(R, cx, cz, radius, a0, a1, n, pred=None, cats=None, face="centre", single=None, margin=0.0):
    """n items on an arc around (cx, cz) between angles a0..a1 (degrees, 0 = +X axis, 90 = +Z).  `face`: "centre" turns
    them toward the centre, "out" away from it."""
    out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i / max(1, n - 1)))
        x, z = cx + radius * math.cos(a), cz + radius * math.sin(a)
        yaw = yaw_to(x, z, cx, cz) if face == "centre" else yaw_to(cx, cz, x, z)
        m = R.cat.models[single] if single else R.cat.pick_any(cats, pred=pred, rng=R.rng)
        if m is None:
            continue
        p = R.place(m, x, z, yaw, margin=margin)
        if p:
            out.append(p)
    return out


def row(R, cats, x0, z0, x1, z1, n, yaw=0.0, pred=None, single=None, margin=0.0):
    """n items evenly spread from (x0, z0) to (x1, z1) (centres)."""
    out = []
    for i in range(n):
        t = i / max(1, n - 1) if n > 1 else 0.5
        x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
        m = R.cat.models[single] if single else R.cat.pick_any(list(cats) if not isinstance(cats, str) else [cats], pred=pred, rng=R.rng)
        if m is None:
            continue
        p = R.place(m, x, z, yaw, margin=margin)
        if p:
            out.append(p)
    return out
