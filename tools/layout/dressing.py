"""Reusable room-dressing helpers for the ship layout."""
import math

from shiplib import FACE_YAW, WALL_T


# ------------------------------------------------------------------ dressing helpers
def light_room(R, spacing=4.2, cats=("ceilinglight",), color="#fff0dd", energy=1.5, **kw):
    R.light_grid(cats=cats, spacing=spacing, color=color, energy=energy, **kw)


def dress_walls(R, cats=("wallpanel",), sides="NSEW", every=1, pred=None, y=None):
    for s in sides:
        R.run(s, list(cats), wall_mount=True, spacing=0.02, pred=pred, y=y)


def dress_ceiling(R, n=8, cats=("ceilingpanel",), pred=None):
    ix0, iz0, ix1, iz1 = R.inner(0.6)
    for _ in range(n * 4):
        if n <= 0:
            break
        x = R.rng.uniform(ix0, ix1)
        z = R.rng.uniform(iz0, iz1)
        m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
        if m and R.place(m, x, z, R.rng.choice([0, 90]), y=R.y + R.h, check=True):
            n -= 1


def ceiling_runs(R, cat="duct", along="x", n=2, off=1.2):
    """Ducts / trays running along the ceiling."""
    ix0, iz0, ix1, iz1 = R.inner()
    for k in range(n):
        if along == "x":
            z = iz0 + off + (iz1 - iz0 - 2 * off) * (k + 0.5) / n
            x = ix0 + 0.6
            while x < ix1 - 0.6:
                m = R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling" and c["size"][0] > c["size"][2], rng=R.rng) or \
                    R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling", rng=R.rng)
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
                m = R.cat.pick_any([cat], pred=lambda c: c["mount"] == "ceiling", rng=R.rng)
                if not m:
                    return
                w = max(m["size"][0], 0.5)
                if R.place(m, x, z + w / 2, 90.0, y=R.y + R.h, check=True):
                    z += w + 0.05
                else:
                    z += 0.5


def signs(R, side, c, dept_label=None, y=3.05):
    m = R.cat.pick("sign", label=dept_label, pred=lambda s: s["mount"] in ("wall", "ceiling") and s["size"][0] < 1.6 and s["size"][1] < 0.7)
    if m and m["mount"] == "wall":
        R.wall_item(side, m, c, y=y, check=False)


def safety(R, side, c):
    m = R.cat.pick("safety", pred=lambda s: s["mount"] == "wall")
    if m:
        R.wall_item(side, m, c)


def tabletop(R, host, cats, n=3):
    """Put small items on top of a host prop."""
    if host is None:
        return
    fp = host["_fp"]
    w, d = fp[2] - fp[0], fp[3] - fp[1]
    for _ in range(n):
        m = R.cat.pick_any(list(cats), pred=lambda c: c["mount"] == "table" and c["size"][0] < min(w, 0.9) and c["size"][2] < min(d, 0.9), rng=R.rng)
        if m:
            R.on_top(host, m, dx=R.rng.uniform(-w * 0.3, w * 0.3), dz=R.rng.uniform(-d * 0.3, d * 0.3), yaw=R.rng.uniform(0, 360))


def by_size(maxw=None, minw=None, maxd=None, maxh=None, minh=None):
    def f(c):
        s = c["size"]
        return ((maxw is None or s[0] <= maxw) and (minw is None or s[0] >= minw) and
                (maxd is None or s[2] <= maxd) and (maxh is None or s[1] <= maxh) and (minh is None or s[1] >= minh))
    return f


def chairs_around(R, cx, cz, hw, hd, cats=("chair",), step=1.0, yaw_in=True, pred=None):
    """Chairs facing a rectangle centred at (cx,cz) with half extents hw,hd."""
    n = 0
    xs = [cx - hw + step * (i + 0.5) for i in range(int(2 * hw / step))]
    for x in xs:
        for sign in (-1, 1):
            z = cz + sign * (hd + 0.45)
            yaw = 0.0 if sign < 0 else 180.0
            m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
            if m and R.place(m, x, z, yaw):
                n += 1
    return n


def central_table(R, cat="table", pred=None, cx=None, cz=None, yaw=0.0):
    m = R.cat.pick(cat, pred=pred)
    if not m:
        return None
    return R.place(m, R.cx if cx is None else cx, R.cz if cz is None else cz, yaw)




def yaw_to(x0, z0, x1, z1):
    return math.degrees(math.atan2(x1 - x0, z1 - z0))     # prop yaw so its front (+Z) faces the target


def look(eye, target):
    dx, dy, dz = target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]
    yaw = math.degrees(math.atan2(-dx, -dz))
    pitch = math.degrees(math.atan2(dy, math.hypot(dx, dz)))
    return round(yaw, 1), round(pitch, 1)


