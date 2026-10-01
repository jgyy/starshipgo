"""Hull lines of the starship, drafted the way a naval architect would.

Two layers:

* **Deck outlines** (`outline(deck)`): one closed, convex polygon per deck built from a half-breadth curve (the
  "sheer plan" seen from above).  Rooms are clipped by it.

      bow     elliptical-sine ogive - pointed, streamlined, tangent to the parallel mid-body
      body    parallel mid-body, 26 m beam, identical on every deck so the stair towers stack
      stern   rounded counter that tapers to a narrow transom

  The five decks are terraced: Deck 1 (command) reaches furthest forward so the bridge overhangs the bow, Deck 3
  (engineering) reaches furthest aft so the hangar forms a stern platform, Deck 0 (the sky deck) is a lens-shaped
  dome on top and Deck 4 (the hold) a tapering keel below.

* **Outer skin** (`skin(volumes)`): the smooth, streamlined envelope that wraps all of it.  It is a loft of closed
  rings (one per height) that always encloses every room volume, flares outward with height (the hull sides lean
  about 9 degrees instead of standing vertical), rolls into a bilge and a keel blade underneath and a dome on top,
  and turns the stepped bow / stern terraces into long raked ramps.  The game draws it as the outside of the ship
  (see ship_builder.gd `_build_skin`).

Coordinates: +X starboard, -Z towards the bow, metres.  `outline(deck)` returns the closed polygon
(no repeated end point) in order bow -> starboard -> stern -> port.
"""
import math

BEAM_HALF = 13.0

#            deck: nose z, nose half-width, z where full beam is reached, z where stern taper starts, stern z, stern half-width
PARAMS = {
    0: dict(z_nose=-20.0, b_nose=4.0, z_full=-6.0, z_taper=8.0, z_stern=18.0, b_stern=8.0),
    1: dict(z_nose=-34.0, b_nose=2.0, z_full=-12.0, z_taper=6.0, z_stern=14.0, b_stern=8.0),
    2: dict(z_nose=-30.0, b_nose=2.0, z_full=-10.0, z_taper=10.0, z_stern=18.0, b_stern=9.0),
    3: dict(z_nose=-24.0, b_nose=2.5, z_full=-5.0, z_taper=14.0, z_stern=32.0, b_stern=8.0),
    4: dict(z_nose=-20.0, b_nose=3.0, z_full=-8.0, z_taper=12.0, z_stern=30.0, b_stern=8.0),
}
DECK_IDS = (0, 1, 2, 3, 4)
BOW_STEPS = 10
STERN_STEPS = 6


def half_breadth_points(deck):
    """Starboard side, bow -> stern, as (x, z) pairs."""
    p = PARAMS[deck]
    pts = []
    for i in range(BOW_STEPS + 1):
        t = i / BOW_STEPS
        z = p["z_nose"] + (p["z_full"] - p["z_nose"]) * t
        b = p["b_nose"] + (BEAM_HALF - p["b_nose"]) * math.sin(math.pi / 2 * t)
        pts.append((round(b, 3), round(z, 3)))
    for i in range(0, STERN_STEPS + 1):
        t = i / STERN_STEPS
        z = p["z_taper"] + (p["z_stern"] - p["z_taper"]) * t
        b = p["b_stern"] + (BEAM_HALF - p["b_stern"]) * math.cos(math.pi / 2 * t)
        pts.append((round(b, 3), round(z, 3)))
    # drop points that do not change the shape (keeps the polygon strictly convex and lean)
    out = [pts[0]]
    for q in pts[1:]:
        if abs(q[0] - out[-1][0]) < 1e-6 and abs(q[1] - out[-1][1]) < 1e-6:
            continue
        out.append(q)
    return out


def outline(deck):
    """Closed convex outline, clockwise when viewed from above with -Z up (bow at the top)."""
    sb = half_breadth_points(deck)
    poly = [(x, z) for x, z in sb]
    poly += [(-x, z) for x, z in reversed(sb)]
    # the bow / stern end points on the centreline are flat faces (nose and transom)
    return [(round(x, 3), round(z, 3)) for x, z in poly]


def is_convex(poly, eps=1e-6):
    n = len(poly)
    sign = 0
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        cx, cz = poly[(i + 2) % n]
        cross = (bx - ax) * (cz - bz) - (bz - az) * (cx - bx)
        if abs(cross) < eps:
            continue
        s = 1 if cross > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True


def area(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, z0 = poly[i]
        x1, z1 = poly[(i + 1) % len(poly)]
        a += x0 * z1 - x1 * z0
    return abs(a) / 2.0


def half_beam_at(deck, z):
    """Half-breadth of the deck outline at station z (None outside the hull)."""
    sb = half_breadth_points(deck)
    if z < sb[0][1] - 1e-9 or z > sb[-1][1] + 1e-9:
        return None
    for (x0, z0), (x1, z1) in zip(sb, sb[1:]):
        if z0 - 1e-9 <= z <= z1 + 1e-9:
            if z1 - z0 < 1e-9:
                return max(x0, x1)
            return x0 + (x1 - x0) * (z - z0) / (z1 - z0)
    return sb[-1][0]


def clip_convex(subject, clip):
    """Sutherland-Hodgman: clip polygon `subject` by the convex polygon `clip` (same winding)."""
    def inside(p, a, b, sgn):
        return sgn * ((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])) >= -1e-9

    def cut(p, q, a, b):
        x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
        x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(den) < 1e-12:
            return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    # orientation of the clip polygon
    s = 0.0
    for i in range(len(clip)):
        x0, z0 = clip[i]
        x1, z1 = clip[(i + 1) % len(clip)]
        s += x0 * z1 - x1 * z0
    sgn = 1 if s > 0 else -1
    out = list(subject)
    for i in range(len(clip)):
        a, b = clip[i], clip[(i + 1) % len(clip)]
        inp, out = out, []
        if not inp:
            break
        prev = inp[-1]
        for cur in inp:
            if inside(cur, a, b, sgn):
                if not inside(prev, a, b, sgn):
                    out.append(cut(prev, cur, a, b))
                out.append(cur)
            elif inside(prev, a, b, sgn):
                out.append(cut(prev, cur, a, b))
            prev = cur
    # remove duplicate consecutive points
    res = []
    for p in out:
        q = (round(p[0], 4), round(p[1], 4))
        if not res or abs(res[-1][0] - q[0]) > 1e-6 or abs(res[-1][1] - q[1]) > 1e-6:
            res.append(q)
    if len(res) > 1 and abs(res[0][0] - res[-1][0]) < 1e-6 and abs(res[0][1] - res[-1][1]) < 1e-6:
        res.pop()
    return res


if __name__ == "__main__":
    for d in DECK_IDS:
        o = outline(d)
        print(f"deck {d}: {len(o)} vertices, convex={is_convex(o)}, area={area(o):.0f} m2, "
              f"length={max(z for _, z in o) - min(z for _, z in o):.0f} m")


# =================================================================================================
# Outer skin
# =================================================================================================
SKIN_N = 256               # vertices per ring (equal steps of angle about the skin centre)
SKIN_DY = 0.5              # vertical ring spacing over the occupied height (m)
SKIN_WINDOW = 5.0          # a deck step is spread over about this much height: turns terraces into long raked ramps
SKIN_RELAX = 60            # blur-and-clamp passes that relax the skin over the room volumes
SKIN_MARGIN = 0.20         # the skin stands at least this far outside every room volume
SKIN_FLARE = 2.6           # extra radius gained between the lowest and the highest room: the sides lean outward ~9 deg
BILGE_DEPTH = 4.0          # rolls under the lowest deck into a keel blade
CROWN_HEIGHT = 3.0         # and over the top deck into a dome


def _far_radius(poly, cx, cz, phi):
    """Distance from (cx, cz) along direction `phi` to the far side of a convex polygon (0 if the ray misses it)."""
    dx, dz = math.cos(phi), math.sin(phi)
    best = 0.0
    n = len(poly)
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        ex, ez = bx - ax, bz - az
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - cx) * ez - (az - cz) * ex) / den
        u = ((ax - cx) * dz - (az - cz) * dx) / den
        if t >= 0.0 and -1e-9 <= u <= 1.0 + 1e-9 and t > best:
            best = t
    return best


def _blur(a, k, circular=True):
    """Gaussian-ish blur of a list (binomial weights, half width k samples)."""
    if k <= 0:
        return list(a)
    w = [math.exp(-0.5 * (j / (k / 2.0)) ** 2) for j in range(-k, k + 1)]
    n = len(a)
    out = []
    for i in range(n):
        s = tot = 0.0
        for j, wj in zip(range(-k, k + 1), w):
            idx = i + j
            if circular:
                idx %= n
            elif idx < 0 or idx >= n:
                continue
            s += a[idx] * wj
            tot += wj
        out.append(s / tot)
    return out


def _dilate(a, k, circular=True):
    n = len(a)
    out = []
    for i in range(n):
        m = 0.0
        for j in range(-k, k + 1):
            idx = i + j
            if circular:
                idx %= n
            elif idx < 0 or idx >= n:
                continue
            if a[idx] > m:
                m = a[idx]
        out.append(m)
    return out


def skin(volumes, center=(0.0, 2.0)):
    """Smooth enclosing skin.  `volumes` = [(polygon [(x, z)...], y_lo, y_hi), ...] of every room (convex polygons).

    Returns {"center": [x, z], "n": N, "rings": [{"y", "sx", "sz", "r": [N radii]}, ...]} ordered bottom -> top; ring
    vertex i is  (cx + sx * r[i] * cos(phi_i), cz + sz * r[i] * sin(phi_i)),  phi_i = 2 pi i / N.  Every room volume is
    inside the skin by at least SKIN_MARGIN (checked by `skin_contains`, tests/test_hull.py)."""
    cx, cz = center
    N = SKIN_N
    phis = [2.0 * math.pi * i / N for i in range(N)]
    vols = [(lo, hi, [_far_radius(p, cx, cz, ph) for ph in phis]) for (p, lo, hi) in volumes]
    ymin = min(v[0] for v in vols)
    ymax = max(v[1] for v in vols)
    nlev = int(math.ceil((ymax - ymin) / SKIN_DY)) + 1
    ys = [ymin + (ymax - ymin) * j / (nlev - 1) for j in range(nlev)]
    # required radius per level: every volume that spans that height
    req = []
    for y in ys:
        r = [0.0] * N
        for lo, hi, rr in vols:
            if lo - 1e-9 <= y <= hi + 1e-9:
                r = [max(a, b) for a, b in zip(r, rr)]
        req.append(r)
    # relax a membrane over the requirement: blur, then never go below it, repeated -> smooth ramps over the terraces
    cols = [[req[j][i] for j in range(nlev)] for i in range(N)]            # one vertical profile per angle
    kb = max(1, int(round(SKIN_WINDOW / (ys[1] - ys[0]) / 2)))
    smooth_cols = []
    for col in cols:
        cur = list(col)
        for _ in range(SKIN_RELAX):
            cur = [max(x, y) for x, y in zip(_blur(cur, kb, circular=False), col)]
        smooth_cols.append(cur)
    levels = [[smooth_cols[i][j] for i in range(N)] for j in range(nlev)]
    # round the plan corners the same way (outward only)
    rounded = []
    for r in levels:
        cur = list(r)
        for _ in range(SKIN_RELAX):
            cur = [max(x, y) for x, y in zip(_blur(cur, 4), r)]
        rounded.append(cur)
    # flare + margin: the sides lean outward with height
    rings = []
    span = max(ymax - ymin, 1e-6)
    for y, r in zip(ys, rounded):
        s = (y - ymin) / span
        flare = SKIN_FLARE * (s * 0.7 + 0.3 * s * s)
        rings.append({"y": y, "sx": 1.0, "sz": 1.0, "r": [x + SKIN_MARGIN + flare if x > 0 else 0.0 for x in r]})
    # directions with no room at all (r == 0 for the whole height) take the neighbours' average so the ring stays closed
    for ring in rings:
        r = ring["r"]
        for i in range(N):
            if r[i] <= 0:
                lo = next(r[(i - k) % N] for k in range(1, N) if r[(i - k) % N] > 0)
                hi = next(r[(i + k) % N] for k in range(1, N) if r[(i + k) % N] > 0)
                r[i] = (lo + hi) / 2
    # bilge (below the lowest deck) and crown (above the top deck): quarter ellipses that shrink the ring to a blade
    bottom, top = rings[0], rings[-1]
    caps_lo, caps_hi = [], []
    steps = 9
    for k in range(1, steps + 1):
        a = math.pi / 2 * k / steps
        caps_lo.append({"y": bottom["y"] - BILGE_DEPTH * math.sin(a), "sx": math.cos(a) ** 1.3, "sz": 1.0 - 0.32 * math.sin(a) ** 2,
                        "r": list(bottom["r"])})
        caps_hi.append({"y": top["y"] + CROWN_HEIGHT * math.sin(a), "sx": math.cos(a) ** 1.2, "sz": 1.0 - 0.5 * math.sin(a) ** 2,
                        "r": list(top["r"])})
    allr = list(reversed(caps_lo)) + rings + caps_hi
    for ring in allr:
        ring["y"] = round(ring["y"], 3)
        ring["sx"] = round(ring["sx"], 4)
        ring["sz"] = round(ring["sz"], 4)
        ring["r"] = [round(x, 2) for x in ring["r"]]
    return {"center": [cx, cz], "n": N, "rings": allr}


def ring_points(sk, ring):
    """(x, z) vertices of one ring."""
    cx, cz = sk["center"]
    n = sk["n"]
    return [(cx + ring["sx"] * ring["r"][i] * math.cos(2 * math.pi * i / n),
             cz + ring["sz"] * ring["r"][i] * math.sin(2 * math.pi * i / n)) for i in range(n)]


def skin_polygon(sk, y):
    """Skin cross-section (list of (x, z)) at height y, interpolated between the two surrounding rings (None outside)."""
    rings = sk["rings"]
    if y < rings[0]["y"] - 1e-9 or y > rings[-1]["y"] + 1e-9:
        return None
    for a, b in zip(rings, rings[1:]):
        if a["y"] - 1e-9 <= y <= b["y"] + 1e-9:
            t = 0.0 if b["y"] - a["y"] < 1e-9 else (y - a["y"]) / (b["y"] - a["y"])
            pa, pb = ring_points(sk, a), ring_points(sk, b)
            return [(p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t) for p, q in zip(pa, pb)]
    return None


def point_in_polygon(x, z, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def skin_contains(sk, x, y, z, margin=0.0):
    """True if (x, y, z) is inside the skin by at least `margin` metres (horizontal distance to the cross-section)."""
    poly = skin_polygon(sk, y)
    if poly is None or not point_in_polygon(x, z, poly):
        return False
    if margin <= 0:
        return True
    n = len(poly)
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        ex, ez = bx - ax, bz - az
        ln2 = ex * ex + ez * ez
        t = 0.0 if ln2 < 1e-12 else max(0.0, min(1.0, ((x - ax) * ex + (z - az) * ez) / ln2))
        if math.hypot(x - (ax + ex * t), z - (az + ez * t)) < margin:
            return False
    return True


def skin_hit(sk, px, py, pz, dx, dz):
    """Where a horizontal ray from (px, py, pz) along (dx, dz) leaves the skin: returns (x, z) or None."""
    poly = skin_polygon(sk, py)
    if poly is None:
        return None
    best = None
    n = len(poly)
    for i in range(n):
        ax, az = poly[i]
        bx, bz = poly[(i + 1) % n]
        ex, ez = bx - ax, bz - az
        den = dx * ez - dz * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - px) * ez - (az - pz) * ex) / den
        u = ((ax - px) * dz - (az - pz) * dx) / den
        if t > 0 and -1e-9 <= u <= 1 + 1e-9 and (best is None or t > best):
            best = t
    return None if best is None else (px + dx * best, pz + dz * best)
