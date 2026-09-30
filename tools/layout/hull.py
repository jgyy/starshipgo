"""Hull lines of the starship, drafted the way a naval architect would: one closed, convex
outline per deck, built from a half-breadth curve (the "sheer plan" seen from above).

    bow     elliptical-sine ogive - pointed, streamlined, tangent to the parallel mid-body
    body    parallel mid-body, 26 m beam, identical on all three decks so the stair towers stack
    stern   rounded counter that tapers to a narrow transom

The decks are terraced like a cruise ship: Deck 1 (command) reaches furthest forward so the bridge
overhangs the bow, Deck 3 (engineering) reaches furthest aft so the hangar forms a stern platform.

Coordinates: +X starboard, -Z towards the bow, metres.  `outline(deck)` returns the closed polygon
(no repeated end point) in order bow -> starboard -> stern -> port.
"""
import math

BEAM_HALF = 13.0

#            deck: nose z, nose half-width, z where full beam is reached, z where stern taper starts, stern z, stern half-width
PARAMS = {
    1: dict(z_nose=-34.0, b_nose=2.0, z_full=-12.0, z_taper=6.0, z_stern=14.0, b_stern=8.0),
    2: dict(z_nose=-30.0, b_nose=2.0, z_full=-10.0, z_taper=10.0, z_stern=18.0, b_stern=9.0),
    3: dict(z_nose=-24.0, b_nose=2.5, z_full=-5.0, z_taper=14.0, z_stern=32.0, b_stern=8.0),
}
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
    for d in (1, 2, 3):
        o = outline(d)
        print(f"deck {d}: {len(o)} vertices, convex={is_convex(o)}, area={area(o):.0f} m2, "
              f"length={max(z for _, z in o) - min(z for _, z in o):.0f} m")
