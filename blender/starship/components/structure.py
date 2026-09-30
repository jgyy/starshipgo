"""Structural components: doors, frames, hatches, panels, pipes, beams, railings.

(Exemplar module - other modules follow the same conventions.)
"""
import math

from ..kit import family, register_material

register_material("st_khaki", "#7a7a55", 0.35, 0.6)
register_material("st_sage", "#5f7a72", 0.3, 0.55)
register_material("st_cream", "#d9d2bd", 0.1, 0.7)
register_material("st_carpet", "#2a3350", 0.0, 1.0)

DOOR_LABELS = ["bulkhead", "security", "medical", "science", "cabin", "engineering"]


@family("door", DOOR_LABELS, mount="floor", tags=["door", "sliding"], solid=False)
def door_sliding(m, i, label, rng):
    """Two-leaf sliding door in a frame. Leaves are separate nodes ('leaf_l', 'leaf_r')
    that the game slides sideways; opening is 2.0 wide x 2.6 high."""
    paint = ["hull_light", "paint_red", "paint_white", "paint_green", "paint_grey", "paint_orange"][i]
    accent = ["em_cyan", "em_red", "em_green", "em_green", "em_amber", "em_orange"][i]
    W, H, T = 2.0, 2.6, 0.22
    # frame
    m.box((0.18, H + 0.16, T), (-W / 2 - 0.09, (H + 0.16) / 2, 0), "hull_dark", 0.015)
    m.box((0.18, H + 0.16, T), (W / 2 + 0.09, (H + 0.16) / 2, 0), "hull_dark", 0.015)
    m.box((W + 0.36, 0.2, T), (0, H + 0.1, 0), "hull_dark", 0.015)
    m.box((W + 0.36, 0.06, T + 0.04), (0, H + 0.23, 0), "black_metal", 0.01)
    m.box((W, 0.03, T * 0.8), (0, 0.015, 0), "steel", 0.005)
    m.box((0.06, H, 0.05), (-W / 2 - 0.16, H / 2, T / 2 + 0.02), accent, 0.01)
    m.box((0.06, H, 0.05), (W / 2 + 0.16, H / 2, T / 2 + 0.02), accent, 0.01)
    # status light + keypad
    m.box((0.28, 0.06, 0.03), (0, H + 0.1, T / 2 + 0.02), accent, 0.005)
    m.box((0.14, 0.2, 0.05), (W / 2 + 0.36, 1.25, 0.05), "black_metal", 0.01)
    m.box((0.09, 0.05, 0.02), (W / 2 + 0.36, 1.3, 0.09), accent)
    for k in range(3):
        m.box((0.09, 0.02, 0.02), (W / 2 + 0.36, 1.2 - k * 0.04, 0.09), "plastic_grey")
    # leaves
    for side, name in ((-1, "leaf_l"), (1, "leaf_r")):
        m.group(name, pivot=(side * W / 4, H / 2, 0))
        cx = side * W / 4
        m.box((W / 2 - 0.01, H, 0.1), (cx, H / 2 + 0.02, 0), paint, 0.012)
        m.box((W / 2 - 0.16, H - 0.3, 0.02), (cx, H / 2 + 0.02, 0.06), "hull_mid", 0.006)
        m.box((W / 2 - 0.16, H - 0.3, 0.02), (cx, H / 2 + 0.02, -0.06), "hull_mid", 0.006)
        m.box((0.04, H - 0.4, 0.03), (cx - side * (W / 4 - 0.02), H / 2, 0.075), "black_metal")
        if i == 1:  # security: hazard chevrons
            for k in range(5):
                m.box((W / 2 - 0.3, 0.05, 0.015), (cx, 0.5 + k * 0.4, 0.07), "hazard_yellow")
        if i == 2:  # medical cross
            m.box((0.34, 0.09, 0.015), (cx, 1.6, 0.07), "paint_red")
            m.box((0.09, 0.34, 0.015), (cx, 1.6, 0.07), "paint_red")
        if i == 3:  # science viewport
            m.box((0.5, 0.7, 0.02), (cx - side * 0.15, 1.6, 0.075), "glass_blue")
        if i == 5:  # engineering: heavy ribs
            for k in range(4):
                m.box((W / 2 - 0.1, 0.07, 0.03), (cx, 0.5 + k * 0.6, 0.075), "black_metal", 0.01)
    m.group("body")


# ==========================================================================
# shared helpers
PI = math.pi


def _dedupe(pts, eps=1e-4):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < eps and abs(out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


def _clip_x(poly, x0, x1):
    def clip(pts, keep, inter):
        out = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            ka, kb = keep(a), keep(b)
            if ka:
                out.append(a)
            if ka != kb:
                out.append(inter(a, b))
        return out

    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))
    p = clip(poly, lambda q: q[0] >= x0, ix(x0))
    if p:
        p = clip(p, lambda q: q[0] <= x1, ix(x1))
    return _dedupe(p)


def hazard(m, x0, y0, w, h, z, th=0.01, base="black_metal", mat="hazard_yellow", stripe=None):
    """Hazard-striped rectangle, lower-left (x0,y0), facing +Z, resting at depth z."""
    stripe = stripe or max(h, 0.22)
    m.box((w, h, th), (x0 + w / 2, y0 + h / 2, z + th / 2), base)
    a = -h
    while a < w:
        poly = _clip_x([(a, 0), (a + stripe * 0.5, 0), (a + stripe * 0.5 + h, h), (a + h, h)], 0, w)
        if len(poly) >= 3:
            m.prism(poly, th * 0.6, (x0, y0, z + th), mat, "xy")
        a += stripe


def _arc(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]


def _offset_path(pts, d):
    norms = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        norms.append((-dy / L, dx / L))
    res = []
    n = len(pts)
    for k, p in enumerate(pts):
        if k == 0:
            nx, ny = norms[0]
            s = 1
        elif k == n - 1:
            nx, ny = norms[-1]
            s = 1
        else:
            a, b = norms[k - 1], norms[k]
            nx, ny = a[0] + b[0], a[1] + b[1]
            l = math.hypot(nx, ny)
            nx /= l
            ny /= l
            s = 1 / max(0.3, nx * a[0] + ny * a[1])
        res.append((p[0] + nx * d * s, p[1] + ny * d * s))
    return res


def path_frame(m, pts, d, T, mat, z=0.0, bevel=0.0):
    """Thick band along an open path (outward = left of travel), depth T centred on z."""
    out = _offset_path(pts, d)
    for k in range(len(pts) - 1):
        q = _dedupe([pts[k], pts[k + 1], out[k + 1], out[k]])
        if len(q) >= 3:
            m.prism(q, T, (0, 0, z - T / 2), mat, "xy", bevel=bevel)


def bolt_row(m, p0, p1, n, mat="steel", r=0.014, h=0.012, axis="z", seg=6):
    for k in range(n):
        t = k / max(1, n - 1)
        m.cyl(r, h, tuple(p0[j] + (p1[j] - p0[j]) * t for j in range(3)), mat, axis, seg)


def wheel(m, pos, R, mat="paint_red", axis="z", spokes=3, r=0.02):
    """Hand wheel: rim torus, hub and spokes."""
    m.torus(R, r, pos, mat, axis, seg=12, tseg=4)
    m.cyl(R * 0.22, r * 3, pos, mat, axis, seg=10)
    for k in range(spokes):
        a = PI * k / spokes
        if axis == "z":
            ends = ((pos[0] + R * math.cos(a), pos[1] + R * math.sin(a), pos[2]), (pos[0] - R * math.cos(a), pos[1] - R * math.sin(a), pos[2]))
        else:
            ends = ((pos[0] + R * math.cos(a), pos[1], pos[2] + R * math.sin(a)), (pos[0] - R * math.cos(a), pos[1], pos[2] - R * math.sin(a)))
        m.link(ends[0], ends[1], r * 0.6, mat, 5)


DW, DH, DT = 2.0, 2.6, 0.22
RECT = [(-1.0, 0.0), (-1.0, DH), (1.0, DH), (1.0, 0.0)]


def _leaves(m, fn, thick=0.1, mat="hull_light", bevel=0.012):
    for side, name in ((-1, "leaf_l"), (1, "leaf_r")):
        cx = side * 0.5
        m.group(name, pivot=(cx, DH / 2, 0))
        if mat:
            m.box((0.99, DH, thick), (cx, DH / 2 + 0.02, 0), mat, bevel)
        fn(m, side, cx)
    m.group("body")


def _rect_frame(m, mat="hull_dark", d=0.18, T=DT, bevel=0.0):
    path_frame(m, RECT, d, T, mat, 0, bevel)
    m.box((DW, 0.03, T * 0.8), (0, 0.015, 0), "steel", 0.005)


# ==========================================================================
# doors (8 more)
DOOR_EXTRA = ["blast", "airlock", "glass lab", "officer wood", "hangar pressure", "cargo", "maintenance hatch", "cleanroom"]


@family("door", DOOR_EXTRA, mount="floor", tags=["door", "sliding"], solid=False)
def door_extra(m, i, label, rng):
    if i == 0:  # blast door: thick, hazard, locking bolts
        _rect_frame(m, "hull_dark", 0.26, DT)
        m.box((DW + 0.6, 0.08, DT + 0.06), (0, DH + 0.3, 0), "black_metal", 0.01)
        hazard(m, -1.0, DH + 0.06, 2.0, 0.1, DT / 2)
        for s in (-1, 1):
            hazard(m, s * 1.13 - 0.05, 0.05, 0.1, 1.0, DT / 2)
        m.box((0.06, 0.06, 0.03), (0, DH + 0.2, DT / 2 + 0.03), "em_red")

        def f(m, side, cx):
            for k in range(3):
                m.cyl(0.05, 0.36, (cx - side * 0.36, 0.55 + k * 0.75, 0), "chrome", "x", 8)
            hazard(m, cx - 0.44, 0.05, 0.88, 0.32, 0.09)
            m.box((0.8, 1.4, 0.03), (cx, 1.3, 0.1), "hull_mid")
            for a in (-0.3, 0.3):
                m.box((0.06, 1.3, 0.04), (cx + a, 1.3, 0.12), "black_metal")
            bolt_row(m, (cx - 0.4, 0.55, 0.115), (cx + 0.4, 0.55, 0.115), 3)
            bolt_row(m, (cx - 0.4, 2.05, 0.115), (cx + 0.4, 2.05, 0.115), 3)
            m.box((0.05, 0.05, 0.03), (cx - side * 0.42, 1.3, 0.13), "em_red")
        _leaves(m, f, 0.18, "gunmetal")
    elif i == 1:  # airlock: porthole, blue/white, gaskets, amber lamps
        _rect_frame(m, "paint_blue", 0.2, DT)
        for s in (-1, 1):
            m.cyl(0.07, 0.1, (s * 0.35, DH + 0.24, 0.02), "em_amber", "y", 10, r2=0.05)
            m.box((0.04, DH, 0.05), (s * 0.99, DH / 2, DT / 2 - 0.02), "rubber")
        m.box((0.7, 0.14, 0.04), (0, DH + 0.1, DT / 2 + 0.01), "black_metal", 0.006)

        def f(m, side, cx):
            m.cyl(0.24, 0.03, (cx - side * 0.16, 1.55, 0.06), "glass_blue", "z", 20)
            m.torus(0.25, 0.035, (cx - side * 0.16, 1.55, 0.065), "chrome", "z", 16, 5)
            for k in range(6):
                a = 2 * PI * k / 6
                m.cyl(0.015, 0.02, (cx - side * 0.16 + 0.31 * math.cos(a), 1.55 + 0.31 * math.sin(a), 0.065), "steel", "z", 6)
            m.box((0.86, 0.06, 0.02), (cx, 0.75, 0.065), "em_amber")
            m.box((0.86, 0.12, 0.02), (cx, 0.3, 0.065), "paint_blue")
            m.box((0.05, 0.9, 0.04), (cx - side * 0.45, 1.0, 0.07), "chrome", 0.005)
        _leaves(m, f, 0.1, "paint_white")
    elif i == 2:  # frameless glass lab door
        _rect_frame(m, "brushed_alu", 0.09, DT)
        m.box((DW + 0.2, 0.08, DT), (0, DH + 0.1, 0), "brushed_alu", 0.008)
        m.box((0.9, 0.05, 0.03), (0, DH + 0.1, DT / 2 + 0.01), "em_cyan")

        def f(m, side, cx):
            m.box((0.99, DH - 0.2, 0.03), (cx, DH / 2 + 0.02, 0), "glass_blue")
            m.box((0.99, 0.14, 0.06), (cx, 0.09, 0), "brushed_alu", 0.008)
            m.box((0.99, 0.1, 0.06), (cx, DH - 0.06, 0), "brushed_alu", 0.008)
            m.box((0.09, DH, 0.05), (cx + side * 0.45, DH / 2 + 0.02, 0), "brushed_alu", 0.006)
            m.box((0.5, 0.25, 0.034), (cx, 1.45, 0), "plastic_white")
            m.box((0.5, 0.02, 0.036), (cx, 1.58, 0), "em_cyan")
            m.cyl(0.015, 0.5, (cx - side * 0.44, 1.05, 0.06), "chrome", "y", 8)
        _leaves(m, f, 0.03, None)
    elif i == 3:  # wooden-trim officer door
        _rect_frame(m, "wood_dark", 0.2, DT)
        path_frame(m, RECT, 0.03, DT + 0.03, "gold_trim", 0)
        m.box((0.5, 0.08, 0.05), (0, DH + 0.24, 0.02), "gold_trim", 0.008)
        m.box((0.1, 0.08, 0.02), (0, DH + 0.24, 0.06), "em_warm")

        def f(m, side, cx):
            for yy, hh in ((0.55, 0.8), (1.6, 0.9), (2.3, 0.4)):
                for zz in (0.055, -0.055):
                    m.box((0.66, hh, 0.02), (cx, yy, zz), "wood_dark", 0.006)
                    m.box((0.6, hh - 0.06, 0.012), (cx, yy, zz * 1.2), "wood_light", 0.004)
            m.cyl(0.018, 0.5, (cx - side * 0.42, 1.1, 0.09), "brass", "y", 8)
            for yy in (0.85, 1.35):
                m.box((0.03, 0.03, 0.05), (cx - side * 0.42, yy, 0.075), "brass")
            m.box((0.16, 0.06, 0.012), (cx + side * 0.05, 1.98, 0.075), "gold_trim")
        _leaves(m, f, 0.09, "wood_light")
    elif i == 4:  # hangar pressure door
        _rect_frame(m, "hull_dark", 0.3, DT)
        m.box((DW + 0.7, 0.12, DT + 0.06), (0, DH + 0.36, 0), "black_metal", 0.01)
        m.cyl(0.11, 0.12, (0, DH + 0.5, 0.02), "em_red", "y", 12)
        m.cyl(0.13, 0.03, (0, DH + 0.44, 0.02), "black_metal", "y", 12)
        hazard(m, -1.0, DH + 0.02, 2.0, 0.09, DT / 2)
        for s in (-1, 1):
            hazard(m, s * 1.24 - 0.06, 0.0, 0.12, 0.6, DT / 2)

        def f(m, side, cx):
            for k in range(4):
                m.box((0.09, DH - 0.1, 0.06), (cx - 0.37 + k * 0.245, DH / 2, 0.1), "black_metal", 0.008)
            for yy in (0.45, 1.3, 2.15):
                m.box((0.99, 0.08, 0.07), (cx, yy, 0.09), "gunmetal", 0.008)
            m.box((0.99, 0.25, 0.02), (cx, 0.15, 0.145), "hazard_yellow")
            bolt_row(m, (cx - 0.45, 1.75, 0.13), (cx + 0.45, 1.75, 0.13), 3, "chrome", 0.02, 0.02)
            m.box((0.04, DH, 0.24), (cx - side * 0.49, DH / 2, 0), "rubber")
        _leaves(m, f, 0.2, "paint_orange")
    elif i == 5:  # cargo door: corrugated
        _rect_frame(m, "steel", 0.16, DT)
        for s in (-1, 1):
            for yy in (0.0, DH):
                m.box((0.2, 0.2, DT + 0.04), (s * 1.08, yy, 0), "hazard_yellow", 0.01)
        m.box((0.8, 0.16, 0.03), (0, DH + 0.12, DT / 2 + 0.01), "st_khaki")
        for k in range(3):
            m.box((0.14, 0.05, 0.03), (-0.25 + k * 0.25, DH + 0.12, DT / 2 + 0.03), "paint_white")

        def f(m, side, cx):
            for k in range(12):
                m.box((0.06, DH - 0.2, 0.05), (cx - 0.45 + k * 0.082, DH / 2 + 0.02, 0.05 if k % 2 else 0.0), "st_khaki")
            m.box((0.99, 0.12, 0.13), (cx, 0.08, 0), "steel", 0.008)
            m.box((0.99, 0.12, 0.13), (cx, DH - 0.02, 0), "steel", 0.008)
            m.cyl(0.03, 0.9, (cx - side * 0.42, 1.2, 0.1), "chrome", "y", 8)
            for yy in (0.8, 1.6):
                m.box((0.04, 0.04, 0.05), (cx - side * 0.42, yy, 0.08), "chrome")
            m.box((0.3, 0.05, 0.02), (cx + side * 0.1, 2.0, 0.09), "paint_white")
            m.box((0.05, 0.3, 0.02), (cx + side * 0.1, 2.0, 0.09), "paint_white")
        _leaves(m, f, 0.06, "hull_dark")
    elif i == 6:  # maintenance hatch-door with wheel and grille window
        _rect_frame(m, "hull_mid", 0.16, DT)
        for s in (-1, 1):
            hazard(m, s * 1.16 - 0.06, 0.0, 0.12, 0.5, DT / 2)
        m.box((0.5, 0.1, 0.03), (0, DH + 0.1, DT / 2 + 0.01), "hazard_yellow")

        def f(m, side, cx):
            for a in range(2):
                for b in range(4):
                    m.box((0.09, 0.09, 0.012), (cx - 0.2 + a * 0.4 + (0.2 if b % 2 else 0) - 0.1, 0.4 + b * 0.35, 0.054), "steel", 0, rot=(0, 0, PI / 4))
            m.box((0.34, 0.34, 0.03), (cx - side * 0.15, 1.75, 0.06), "black_metal", 0.006)
            m.box((0.26, 0.26, 0.03), (cx - side * 0.15, 1.75, 0.07), "glass_dark")
            for k in (-1, 0, 1):
                m.box((0.01, 0.26, 0.012), (cx - side * 0.15 + k * 0.08, 1.75, 0.09), "steel")
                m.box((0.26, 0.01, 0.012), (cx - side * 0.15, 1.75 + k * 0.08, 0.09), "steel")
            if side < 0:
                wheel(m, (cx + 0.3, 1.05, 0.11), 0.13, "paint_red", "z", 4)
            else:
                m.box((0.1, 0.16, 0.05), (cx - 0.3, 1.05, 0.08), "plastic_black", 0.005)
                m.box((0.05, 0.05, 0.02), (cx - 0.3, 1.1, 0.11), "em_green")
            bolt_row(m, (cx - 0.44, 0.1, 0.06), (cx + 0.44, 0.1, 0.06), 4)
            m.box((0.5, 0.06, 0.012), (cx + side * 0.1, 0.65, 0.06), "hazard_yellow")
        _leaves(m, f, 0.09, "steel")
    else:  # cleanroom
        _rect_frame(m, "paint_white", 0.14, DT)
        path_frame(m, RECT, -0.03, DT + 0.03, "paint_blue", 0)
        for s in (-1, 1):
            m.cyl(0.025, 0.08, (s * 0.7, DH - 0.04, 0.0), "steel", "y", 6, r2=0.012)
        m.box((1.2, 0.05, 0.03), (0, DH + 0.1, DT / 2 + 0.01), "em_blue")
        m.box((1.6, 0.03, 0.8), (0, 0.03, 0.55), "paint_blue", 0.008)
        m.box((1.4, 0.005, 0.6), (0, 0.05, 0.55), "plastic_white")

        def f(m, side, cx):
            m.box((0.5, 1.6, 0.03), (cx, 1.35, 0.05), "glass")
            m.box((0.54, 1.66, 0.02), (cx, 1.35, 0.045), "plastic_grey", 0.005)
            m.box((0.9, 0.05, 0.02), (cx, 0.45, 0.055), "em_blue")
            m.box((0.03, 0.4, 0.05), (cx - side * 0.42, 1.0, 0.08), "chrome", 0.004)
            m.box((0.99, 0.03, 0.02), (cx, 0.02, 0.055), "rubber")
        _leaves(m, f, 0.09, "plastic_white")


# ==========================================================================
# door frames (8)
DOORFRAME_LABELS = ["round arch", "hexagonal", "light strip square", "gothic arch", "ibeam portal", "twin ring", "deep bulkhead", "peaked gable"]


@family("doorframe", DOORFRAME_LABELS, mount="floor", tags=["door", "frame"], solid=False)
def doorframe_fam(m, i, label, rng):
    T = DT
    if i == 0:
        pts = [(-1, 0), (-1, 2.0)] + _arc(0, 2.0, 1.0, PI, 0, 16)[1:] + [(1, 0)]
        path_frame(m, pts, 0.24, T, "hull_mid", 0)
        path_frame(m, pts, -0.03, 0.05, "em_cyan", T / 2 - 0.02)
        path_frame(m, pts, 0.24, 0.03, "hull_dark", T / 2 + 0.005)
        m.box((0.3, 0.2, T + 0.06), (0, 3.1, 0), "gunmetal", 0.012)
        for s in (-1, 1):
            m.box((0.5, 0.12, 0.5), (s * 1.25, 0.06, 0), "hull_dark", 0.01)
        bolt_row(m, (-1.2, 0.5, T / 2 + 0.02), (-1.2, 1.9, T / 2 + 0.02), 4)
        bolt_row(m, (1.2, 0.5, T / 2 + 0.02), (1.2, 1.9, T / 2 + 0.02), 4)
    elif i == 1:
        pts = [(-1, 0), (-1, 1.9), (-0.55, 2.75), (0.55, 2.75), (1, 1.9), (1, 0)]
        path_frame(m, pts, 0.2, T, "hull_dark", 0, 0.01)
        path_frame(m, pts, -0.03, 0.04, "em_amber", T / 2 - 0.01)
        for p in pts[1:-1]:
            m.cyl(0.05, 0.03, (p[0] * 1.1, p[1] + (0.12 if p[1] > 2 else 0.05), T / 2 + 0.01), "steel", "z", 6)
        for s in (-1, 1):
            hazard(m, s * 1.2 - 0.06, 0.0, 0.12, 0.7, T / 2 + 0.0)
        m.box((2.1, 0.03, T), (0, 0.015, 0), "steel")
    elif i == 2:
        _rect_frame(m, "hull_light", 0.3, T)
        for s in (-1, 1):
            m.box((0.08, DH - 0.2, 0.03), (s * 1.15, 1.3, T / 2 + 0.005), "em_white")
            m.box((0.12, DH, 0.02), (s * 1.15, 1.3, T / 2 + 0.005), "black_metal")
        m.box((1.8, 0.08, 0.03), (0, DH + 0.15, T / 2 + 0.005), "em_white")
        m.box((1.9, 0.12, 0.02), (0, DH + 0.15, T / 2 + 0.005), "black_metal")
        m.box((0.1, 0.16, 0.05), (1.5, 1.2, 0.05), "plastic_black", 0.005)
        m.box((0.06, 0.06, 0.02), (1.5, 1.24, 0.08), "em_green")
    elif i == 3:
        a = math.acos(-0.6 / 1.6)
        left = [(-1, 0), (-1, 2.0)] + _arc(0.6, 2.0, 1.6, PI, a, 10)[1:]
        right = _arc(-0.6, 2.0, 1.6, PI - a, 0, 10) + [(1, 0)]
        pts = left + right
        path_frame(m, pts, 0.2, T, "concrete", 0)
        path_frame(m, pts, -0.025, 0.06, "gold_trim", T / 2 - 0.02)
        path_frame(m, pts, 0.2, 0.03, "hull_dark", T / 2 + 0.005)
        m.box((0.16, 0.5, T + 0.05), (0, 3.55, 0), "gold_trim", 0.01, rot=(0, 0, 0))
        for s in (-1, 1):
            m.box((0.4, 0.4, 0.4), (s * 1.2, 0.2, 0), "concrete", 0.02)
    elif i == 4:
        for s in (-1, 1):
            x = s * 1.12
            m.box((0.24, DH + 0.2, 0.04), (x, (DH + 0.2) / 2, 0), "steel", 0.004)
            for zz in (-0.09, 0.09):
                m.box((0.05, DH + 0.2, 0.2), (x + s * 0.095, (DH + 0.2) / 2, 0), "paint_orange", 0.006)
                m.box((0.05, DH + 0.2, 0.2), (x - s * 0.095, (DH + 0.2) / 2, 0), "paint_orange", 0.006)
        m.box((2.6, 0.05, 0.2), (0, DH + 0.3, 0), "paint_orange", 0.006)
        m.box((2.6, 0.05, 0.2), (0, DH + 0.1, 0), "paint_orange", 0.006)
        m.box((2.0, 0.2, 0.04), (0, DH + 0.2, 0), "steel", 0.004)
        for s in (-1, 1):
            m.prism([(0, 0), (0.35, 0), (0, 0.35)] if s < 0 else [(0, 0), (-0.35, 0), (0, 0.35)], 0.06, (s * 1.0, DH - 0.35, -0.03), "paint_orange", "xy")
            bolt_row(m, (s * 1.12, 0.3, 0.11), (s * 1.12, DH - 0.4, 0.11), 6, "chrome", 0.014, 0.012)
        m.box((0.24, 0.05, 0.3), (-1.12, 0.03, 0), "black_metal")
        m.box((0.24, 0.05, 0.3), (1.12, 0.03, 0), "black_metal")
    elif i == 5:
        r = 0.42
        pts = [(-1, 0), (-1, DH - r)] + _arc(-1 + r, DH - r, r, PI, PI / 2, 5)[1:] + _arc(1 - r, DH - r, r, PI / 2, 0, 5)[1:-1] + [(1, DH - r), (1, 0)]
        path_frame(m, pts, 0.12, 0.1, "hull_light", 0.0, 0.006)
        path_frame(m, pts, 0.0, T, "black_metal", 0.0)
        path_frame(m, pts, 0.12, 0.06, "hull_light", T / 2 - 0.03)
        path_frame(m, pts, 0.12, 0.06, "hull_light", -T / 2 + 0.03)
        path_frame(m, pts, 0.22, 0.06, "hull_mid", T / 2 - 0.03)
        path_frame(m, pts, 0.22, 0.06, "hull_mid", -T / 2 + 0.03)
        path_frame(m, pts, 0.13, 0.03, "em_blue", T / 2 + 0.005)
    elif i == 6:
        Tb = 0.5
        path_frame(m, RECT, 0.28, Tb, "hull_dark", 0)
        path_frame(m, RECT, 0.12, Tb + 0.08, "hull_mid", 0)
        path_frame(m, RECT, 0.45, 0.1, "black_metal", 0.0)
        m.box((2.0, 0.08, Tb), (0, 0.04, 0), "steel", 0.006)
        hazard(m, -1.0, 0.0, 2.0, 0.08, Tb / 2 + 0.0)
        for s in (-1, 1):
            bolt_row(m, (s * 1.2, 0.3, Tb / 2 + 0.05), (s * 1.2, DH - 0.2, Tb / 2 + 0.05), 6, "steel", 0.02, 0.02, "z", 8)
        bolt_row(m, (-0.9, DH + 0.2, Tb / 2 + 0.05), (0.9, DH + 0.2, Tb / 2 + 0.05), 7, "steel", 0.02, 0.02, "z", 8)
        for s in (-1, 1):
            m.cyl(0.06, 0.06, (s * 0.8, DH + 0.36, 0), "em_amber", "y", 8)
    else:
        pts = [(-1, 0), (-1, 2.4), (0, 2.95), (1, 2.4), (1, 0)]
        path_frame(m, pts, 0.22, T, "paint_grey", 0, 0.01)
        path_frame(m, pts, 0.22, 0.03, "hull_dark", T / 2 + 0.005)
        path_frame(m, pts, -0.03, 0.05, "em_amber", T / 2 - 0.02)
        m.box((0.4, 0.4, 0.4), (0, 3.4, 0), "hull_dark", 0.02, rot=(0, 0, PI / 4))
        m.box((0.16, 0.16, 0.04), (0, 3.4, T / 2 + 0.02), "em_amber", 0.01, rot=(0, 0, PI / 4))
        for s in (-1, 1):
            m.box((0.36, 0.14, T + 0.08), (s * 1.2, 0.07, 0), "hull_dark", 0.01)
            m.box((0.1, 1.0, 0.03), (s * 1.16, 0.6, T / 2 + 0.005), "hull_light")


# ==========================================================================
# hatches (10): 8 wall, 2 floor
HATCH_WALL = ["round wheel", "oval pressure", "jefferies square", "porthole round", "dogged rectangular", "iris", "emergency red", "hex access"]
HATCH_FLOOR = ["floor round wheel", "floor square recessed"]


def _ellipse(rx, ry, n=24):
    return [(rx * math.cos(2 * PI * k / n), ry * math.sin(2 * PI * k / n)) for k in range(n)]


def _dogs(m, n, R, z, mat="steel", size=0.07):
    for k in range(n):
        a = 2 * PI * k / n
        m.box((size, size * 0.5, 0.05), (R * math.cos(a), R * math.sin(a), z), mat, 0.004, rot=(0, 0, a))


@family("hatch", HATCH_WALL, mount="wall", tags=["hatch", "pressure"], solid=False, mount_y=1.2)
def hatch_wall(m, i, label, rng):
    if i == 0:
        m.box((0.95, 0.95, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
        m.cyl(0.42, 0.08, (0, 0, 0.06), "hull_mid", "z", 24)
        m.torus(0.4, 0.04, (0, 0, 0.1), "steel", "z", 24, 6)
        m.cyl(0.34, 0.06, (0, 0, 0.12), "steel", "z", 24)
        m.cyl(0.26, 0.02, (0, 0, 0.155), "hull_light", "z", 20)
        _dogs(m, 8, 0.4, 0.12)
        wheel(m, (0, 0, 0.19), 0.19, "paint_red", "z", 3, 0.022)
        for s in (-1, 1):
            m.box((0.08, 0.16, 0.08), (0.44, s * 0.25, 0.08), "black_metal", 0.006)
        bolt_row(m, (-0.42, -0.42, 0.04), (0.42, -0.42, 0.04), 2)
        bolt_row(m, (-0.42, 0.42, 0.04), (0.42, 0.42, 0.04), 2)
    elif i == 1:
        m.prism(_ellipse(0.42, 0.62), 0.05, (0, 0, 0), "hull_dark", "xy", bevel=0.008)
        m.prism(_ellipse(0.36, 0.55), 0.09, (0, 0, 0), "hull_mid", "xy", bevel=0.008)
        m.prism(_ellipse(0.3, 0.48), 0.11, (0, 0, 0), "paint_teal", "xy", bevel=0.006)
        for k in range(10):
            a = 2 * PI * k / 10
            m.cyl(0.016, 0.02, (0.39 * math.cos(a), 0.58 * math.sin(a), 0.06), "chrome", "z", 6)
        m.box((0.06, 0.4, 0.05), (-0.03, 0.0, 0.135), "chrome", 0.01)
        m.box((0.4, 0.06, 0.04), (0, 0.0, 0.135), "chrome", 0.01)
        m.box((0.12, 0.04, 0.02), (0, 0.4, 0.12), "em_amber")
        for s in (-1, 1):
            m.box((0.05, 0.14, 0.09), (-0.4, s * 0.3, 0.06), "black_metal", 0.005)
    elif i == 2:
        m.box((0.85, 0.85, 0.03), (0, 0, 0.015), "hull_dark", 0.01)
        hazard(m, -0.42, -0.42, 0.84, 0.08, 0.03)
        hazard(m, -0.42, 0.34, 0.84, 0.08, 0.03)
        m.box((0.7, 0.7, 0.03), (0, 0, 0.045), "hull_mid", 0.008)
        m.box((0.56, 0.56, 0.03), (0, 0, 0.07), "paint_grey", 0.008)
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.cyl(0.04, 0.05, (sx * 0.29, sy * 0.29, 0.1), "black_metal", "z", 8)
                m.box((0.09, 0.03, 0.02), (sx * 0.29, sy * 0.29, 0.13), "chrome", 0.004, rot=(0, 0, PI / 4 * sx * sy))
        m.box((0.24, 0.06, 0.03), (0, 0, 0.1), "em_green")
    elif i == 3:
        m.cyl(0.5, 0.05, (0, 0, 0.025), "paint_white", "z", 24)
        m.torus(0.42, 0.05, (0, 0, 0.07), "gunmetal", "z", 24, 6)
        m.cyl(0.38, 0.05, (0, 0, 0.09), "paint_white", "z", 24)
        m.torus(0.19, 0.04, (0, 0.05, 0.13), "chrome", "z", 20, 6)
        m.cyl(0.17, 0.03, (0, 0.05, 0.12), "glass_blue", "z", 20)
        m.box((0.36, 0.05, 0.04), (0, -0.2, 0.13), "paint_red", 0.008)
        m.box((0.05, 0.05, 0.06), (0.16, -0.2, 0.12), "black_metal")
        m.cyl(0.03, 0.08, (0.22, -0.2, 0.15), "black_metal", "x", 8, rot=(0, 0, 0))
        _dogs(m, 6, 0.44, 0.1, "black_metal", 0.09)
    elif i == 4:
        m.box((1.1, 0.8, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
        m.box((1.0, 0.7, 0.05), (0, 0, 0.065), "rubber", 0.01)
        m.box((0.92, 0.62, 0.06), (0, 0, 0.11), "hull_mid", 0.012)
        m.box((0.7, 0.4, 0.02), (0, 0, 0.15), "hull_light", 0.006)
        for x in (-0.36, 0, 0.36):
            for y in (-0.33, 0.33):
                m.box((0.12, 0.05, 0.05), (x, y, 0.14), "steel", 0.006)
                m.cyl(0.02, 0.06, (x, y, 0.13), "chrome", "z", 6)
        for y in (0,):
            for x in (-0.47, 0.47):
                m.box((0.05, 0.14, 0.05), (x, y, 0.14), "steel", 0.006)
        m.box((0.2, 0.06, 0.04), (0, 0, 0.16), "black_metal", 0.006)
        m.box((0.05, 0.05, 0.02), (0.15, 0, 0.18), "em_green")
        for s in (-1, 1):
            m.box((0.1, 0.05, 0.1), (s * 0.5, 0.25, 0.08), "black_metal", 0.005)
    elif i == 5:
        m.cyl(0.5, 0.05, (0, 0, 0.025), "hull_dark", "z", 24)
        m.torus(0.44, 0.045, (0, 0, 0.075), "steel", "z", 24, 6)
        for k in range(8):
            a = 2 * PI * k / 8
            m.prism([(0, 0), (0.44, -0.07), (0.44, 0.2)], 0.03, (0, 0, 0.05 + 0.008 * (k % 2)), "brushed_alu" if k % 2 else "hull_light", "xy", rot=(0, 0, a))
        m.cyl(0.05, 0.05, (0, 0, 0.09), "em_cyan", "z", 12)
        m.torus(0.09, 0.015, (0, 0, 0.09), "black_metal", "z", 12, 5)
        for k in range(6):
            a = 2 * PI * k / 6 + 0.26
            m.cyl(0.02, 0.03, (0.47 * math.cos(a), 0.47 * math.sin(a), 0.07), "chrome", "z", 6)
    elif i == 6:
        m.cyl(0.5, 0.05, (0, 0, 0.025), "paint_red", "z", 24)
        m.torus(0.42, 0.04, (0, 0, 0.07), "hazard_yellow", "z", 24, 6)
        m.cyl(0.38, 0.06, (0, 0, 0.09), "paint_red", "z", 24)
        m.box((0.5, 0.05, 0.04), (0, 0.0, 0.14), "black_metal", 0.008)
        m.box((0.05, 0.05, 0.08), (0.2, 0, 0.11), "black_metal")
        m.box((0.05, 0.05, 0.08), (-0.2, 0, 0.11), "black_metal")
        m.box((0.05, 0.3, 0.04), (0, -0.15, 0.14), "black_metal", 0.008)
        m.box((0.5, 0.12, 0.03), (0, 0.6, 0.015), "black_metal")
        m.box((0.42, 0.06, 0.02), (0, 0.6, 0.035), "em_green")
        m.cyl(0.05, 0.05, (-0.42, 0.42, 0.08), "em_red", "z", 10)
    else:
        hexp = [(0.5 * math.cos(PI / 3 * k), 0.5 * math.sin(PI / 3 * k)) for k in range(6)]
        hexq = [(0.4 * x / 0.5, 0.4 * y / 0.5) for x, y in hexp]
        hexr = [(0.3 * x / 0.5, 0.3 * y / 0.5) for x, y in hexp]
        m.prism(hexp, 0.04, (0, 0, 0), "hull_dark", "xy", bevel=0.008)
        m.prism(hexq, 0.08, (0, 0, 0), "hull_mid", "xy", bevel=0.008)
        m.prism(hexr, 0.1, (0, 0, 0), "paint_grey", "xy", bevel=0.006)
        for x, y in hexp:
            m.cyl(0.022, 0.06, (x * 0.92, y * 0.92, 0.05), "steel", "z", 6)
        m.cyl(0.07, 0.04, (0, 0, 0.12), "black_metal", "z", 10)
        m.box((0.02, 0.1, 0.02), (0, 0, 0.14), "steel")
        m.box((0.16, 0.1, 0.03), (0, 0.42, 0.11), "plastic_black", 0.005)
        m.box((0.1, 0.03, 0.02), (0, 0.42, 0.13), "em_amber")


@family("hatch", HATCH_FLOOR, mount="floor", tags=["hatch", "floor"], solid=False)
def hatch_floor(m, i, label, rng):
    if i == 0:
        m.cyl(0.62, 0.03, (0, 0.015, 0), "hull_dark", "y", 24)
        hazard_ring = m.torus(0.55, 0.02, (0, 0.03, 0), "hazard_yellow", "y", 24, 5)
        m.cyl(0.5, 0.06, (0, 0.03, 0), "steel", "y", 24)
        m.cyl(0.4, 0.02, (0, 0.065, 0), "hull_mid", "y", 20)
        for k in range(6):
            a = 2 * PI * k / 6
            m.cyl(0.02, 0.02, (0.46 * math.cos(a), 0.06, 0.46 * math.sin(a)), "chrome", "y", 6)
        wheel(m, (0, 0.085, 0), 0.22, "paint_red", "y", 3, 0.018)
    else:
        m.box((1.2, 0.03, 1.2), (0, 0.015, 0), "hull_dark", 0.006)
        m.box((1.04, 0.02, 1.04), (0, 0.035, 0), "hazard_yellow", 0.004)
        m.box((0.96, 0.03, 0.96), (0, 0.04, 0), "steel", 0.006)
        m.box((0.84, 0.02, 0.84), (0, 0.055, 0), "hull_mid", 0.004)
        m.box((0.3, 0.02, 0.1), (0, 0.065, 0.26), "black_metal", 0.004)
        m.box((0.24, 0.006, 0.05), (0, 0.075, 0.26), "hull_dark")
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.cyl(0.02, 0.02, (sx * 0.4, 0.07, sz * 0.4), "chrome", "y", 6)
        for sx in (-1, 1):
            m.box((0.1, 0.03, 0.03), (sx * 0.3, 0.03, -0.62), "black_metal")


# ==========================================================================
# wall panels (24): 16 short (1.2 tall, mount_y 1.5) + 8 tall (2.4 tall, mount_y 1.25)
WP_SHORT = ["plain smooth", "vent grille", "access panel", "conduit run", "ribbed", "screen inset", "hazard trim", "service bolted",
            "quilted insulation", "honeycomb", "riveted plate", "wood veneer", "light diffuser", "diamond plate", "fuse box", "lattice"]
WP_TALL = ["tall ribbed", "tall window slit", "tall conduit bundle", "tall lockers", "tall glow seam", "tall hazard stripe", "tall pipe niche", "tall wood panelled"]


def _wp_base(m, H, mat, D=0.05, bevel=0.008, W=1.0):
    m.box((W, H, D), (0, 0, D / 2), mat, bevel)


def _wp_border(m, H, D, mat="hull_dark", W=1.0, t=0.03):
    m.box((W - 0.06, t, 0.012), (0, H / 2 - 0.05, D + 0.004), mat)
    m.box((W - 0.06, t, 0.012), (0, -H / 2 + 0.05, D + 0.004), mat)
    m.box((t, H - 0.14, 0.012), (-W / 2 + 0.05, 0, D + 0.004), mat)
    m.box((t, H - 0.14, 0.012), (W / 2 - 0.05, 0, D + 0.004), mat)


@family("wallpanel", WP_SHORT, mount="wall", tags=["wall", "panel"], solid=False, mount_y=1.5)
def wallpanel_short(m, i, label, rng):
    H = 1.2
    if i == 0:
        _wp_base(m, H, "hull_light", 0.04)
        _wp_border(m, H, 0.04, "hull_mid")
        m.box((0.6, 0.02, 0.008), (0, 0.15, 0.044), "hull_mid")
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.cyl(0.014, 0.014, (sx * 0.44, sy * 0.54, 0.045), "steel", "z", 6)
        m.box((0.3, 0.08, 0.006), (0, -0.25, 0.043), "paint_grey")
    elif i == 1:
        _wp_base(m, H, "hull_dark", 0.06)
        m.box((0.8, 0.9, 0.03), (0, 0, 0.07), "black_metal", 0.006)
        m.box((0.7, 0.8, 0.02), (0, 0, 0.06), "gunmetal")
        for k in range(9):
            m.box((0.7, 0.045, 0.02), (0, -0.36 + k * 0.09, 0.09), "steel", 0.003, rot=(-0.6, 0, 0))
        for sx in (-1, 1):
            for sy in (-1, 1):
                m.cyl(0.016, 0.016, (sx * 0.43, sy * 0.48, 0.066), "chrome", "z", 6)
    elif i == 2:
        _wp_base(m, H, "hull_mid", 0.05)
        m.box((0.8, 0.9, 0.02), (0, 0, 0.06), "hull_light", 0.006)
        m.box((0.7, 0.8, 0.02), (0, 0, 0.078), "hull_mid", 0.005)
        for sy in (-1, 1):
            m.box((0.05, 0.14, 0.04), (-0.4, sy * 0.3, 0.07), "black_metal", 0.004)
            m.cyl(0.03, 0.03, (0.3, sy * 0.33, 0.1), "steel", "z", 8)
            m.box((0.05, 0.012, 0.012), (0.3, sy * 0.33, 0.118), "black_metal")
        m.box((0.1, 0.03, 0.03), (0.28, 0.0, 0.105), "black_metal", 0.004)
        m.box((0.06, 0.03, 0.01), (0.0, 0.38, 0.09), "em_amber")
        m.box((0.3, 0.05, 0.01), (0, -0.33, 0.09), "paint_white")
    elif i == 3:
        _wp_base(m, H, "hull_mid", 0.04)
        for k, yy in enumerate((-0.35, 0.0, 0.35)):
            r = (0.05, 0.035, 0.05)[k]
            m.cyl(r, 0.9, (0, yy, 0.04 + r), ("copper", "steel", "paint_orange")[k], "x", 10)
            for x in (-0.3, 0.3):
                m.box((0.05, r * 2 + 0.02, 0.03), (x, yy, 0.04 + r), "black_metal", 0.004)
        m.box((0.2, 0.28, 0.08), (0.3, 0.17, 0.08), "gunmetal", 0.006)
        m.cyl(0.02, 0.12, (-0.3, 0.17, 0.1), "steel", "y", 6)
        m.box((0.03, 0.03, 0.01), (0.3, 0.2, 0.125), "em_green")
    elif i == 4:
        _wp_base(m, H, "hull_dark", 0.04)
        for k in range(11):
            m.box((0.05, 1.1, 0.05 if k % 2 else 0.035), (-0.45 + k * 0.09, 0, 0.06), "hull_mid" if k % 2 else "steel", 0.006)
        m.box((1.0, 0.06, 0.1), (0, 0.55, 0.05), "black_metal", 0.006)
        m.box((1.0, 0.06, 0.1), (0, -0.55, 0.05), "black_metal", 0.006)
    elif i == 5:
        _wp_base(m, H, "hull_dark", 0.06)
        m.screen((0.6, 0.45), (0, 0.15, 0.062), rng.choice(["systems", "power", "nav", "diagnostic", "bars"]), bezel=0.03)
        for k in range(5):
            m.box((0.08, 0.05, 0.02), (-0.24 + k * 0.12, -0.22, 0.07), ("plastic_grey", "em_green", "plastic_grey", "em_amber", "plastic_grey")[k], 0.004)
        m.box((0.7, 0.03, 0.02), (0, -0.4, 0.07), "black_metal")
        m.box((0.05, 0.05, 0.01), (0.4, 0.48, 0.065), "em_cyan")
    elif i == 6:
        _wp_base(m, H, "paint_red", 0.05)
        hazard(m, -0.5, 0.42, 1.0, 0.16, 0.05, stripe=0.2)
        hazard(m, -0.5, -0.58, 1.0, 0.16, 0.05, stripe=0.2)
        m.box((0.7, 0.4, 0.01), (0, 0, 0.055), "paint_white")
        m.box((0.5, 0.06, 0.012), (0, 0.06, 0.062), "black_metal")
        m.box((0.36, 0.05, 0.012), (0, -0.08, 0.062), "black_metal")
    elif i == 7:
        _wp_base(m, H, "hull_mid", 0.06)
        for x in range(4):
            for y in range(6):
                m.cyl(0.018, 0.02, (-0.36 + x * 0.24, -0.5 + y * 0.2, 0.07), "steel", "z", 6)
        m.box((0.44, 0.5, 0.02), (0, 0.1, 0.07), "hull_dark", 0.005)
        m.box((0.34, 0.2, 0.012), (0, 0.22, 0.086), "paint_white")
        m.cyl(0.05, 0.05, (0, -0.05, 0.09), "brass", "z", 10)
        m.box((0.02, 0.09, 0.02), (0, -0.05, 0.12), "black_metal")
        m.box((0.36, 0.03, 0.01), (0, 0.13, 0.086), "hazard_yellow")
    elif i == 8:
        _wp_base(m, H, "hull_dark", 0.04)
        for x in range(2):
            for y in range(3):
                m.box((0.44, 0.34, 0.09), (-0.24 + x * 0.48, -0.38 + y * 0.38, 0.075), "st_cream", 0.03)
        for yy in (-0.19, 0.19):
            m.box((1.0, 0.03, 0.02), (0, yy, 0.128), "rubber")
        m.box((0.05, 0.05, 0.03), (0.44, 0.19, 0.13), "steel")
    elif i == 9:
        _wp_base(m, H, "hull_dark", 0.05)
        for r in range(5):
            for c in range(4 if r % 2 == 0 else 3):
                xx = (c - (3 if r % 2 == 0 else 2) / 2) * 0.25
                m.cyl(0.115, 0.05, (xx, (r - 2) * 0.216, 0.075), "brushed_alu" if (r + c) % 3 else "hull_light", "z", 6, bevel=0.005)
        m.cyl(0.04, 0.03, (0.0, 0.0, 0.115), "em_cyan", "z", 6)
    elif i == 10:
        _wp_base(m, H, "hull_dark", 0.04)
        for k, (x, y, w, h, mm) in enumerate(((-0.25, 0.28, 0.5, 0.56, "hull_mid"), (0.27, 0.1, 0.44, 0.9, "steel"), (-0.25, -0.34, 0.5, 0.4, "hull_light"))):
            m.box((w, h, 0.02), (x, y, 0.05 + 0.005 * k), mm, 0.004)
            for cx in (x - w / 2 + 0.03, x + w / 2 - 0.03):
                for cy in (y - h / 2 + 0.03, y + h / 2 - 0.03):
                    m.cyl(0.012, 0.012, (cx, cy, 0.066 + 0.005 * k), "black_metal", "z", 5)
        m.box((0.12, 0.03, 0.01), (-0.25, 0.3, 0.07), "hazard_yellow")
    elif i == 11:
        _wp_base(m, H, "wood_dark", 0.05)
        for k in range(6):
            m.box((0.96, 0.17, 0.02), (0, -0.5 + k * 0.2, 0.06), "wood_light" if k % 2 else "wood_dark", 0.004)
        m.box((1.0, 0.03, 0.07), (0, 0.585, 0.045), "gold_trim", 0.004)
        m.box((1.0, 0.03, 0.07), (0, -0.585, 0.045), "gold_trim", 0.004)
        m.box((0.03, 1.2, 0.07), (-0.485, 0, 0.045), "gold_trim", 0.004)
        m.box((0.03, 1.2, 0.07), (0.485, 0, 0.045), "gold_trim", 0.004)
    elif i == 12:
        _wp_base(m, H, "hull_dark", 0.06)
        m.box((0.86, 1.06, 0.02), (0, 0, 0.07), "plastic_grey", 0.006)
        m.box((0.76, 0.96, 0.02), (0, 0, 0.085), "em_white")
        for k in (-1, 0, 1):
            m.box((0.02, 0.96, 0.012), (k * 0.19, 0, 0.098), "plastic_grey")
        m.box((0.76, 0.02, 0.012), (0, 0, 0.098), "plastic_grey")
    elif i == 13:
        _wp_base(m, H, "steel", 0.03)
        for r in range(6):
            for c in range(4):
                m.box((0.13, 0.13, 0.01), (-0.3 + c * 0.2 + (0.1 if r % 2 else 0) - 0.05, -0.5 + r * 0.2, 0.035), "brushed_alu", 0, rot=(0, 0, PI / 4))
        for sx in (-1, 1):
            m.box((0.04, 1.2, 0.05), (sx * 0.48, 0, 0.025), "hull_dark", 0.004)
    elif i == 14:
        _wp_base(m, H, "hull_mid", 0.04)
        m.box((0.7, 0.9, 0.09), (0, 0.02, 0.085), "gunmetal", 0.008)
        m.box((0.6, 0.5, 0.02), (0, 0.12, 0.135), "hull_dark", 0.004)
        for k in range(6):
            m.box((0.06, 0.09, 0.03), (-0.25 + k * 0.1, 0.12, 0.155), "plastic_black", 0.004)
            m.box((0.03, 0.02, 0.01), (-0.25 + k * 0.1, 0.17, 0.175), ("em_green", "em_green", "em_amber", "em_green", "em_red", "em_green")[k])
        m.box((0.4, 0.14, 0.01), (0, -0.25, 0.135), "hazard_yellow")
        m.box((0.36, 0.08, 0.005), (0, -0.25, 0.14), "paint_white")
        m.box((0.03, 0.9, 0.05), (-0.36, 0.02, 0.07), "black_metal")
    else:
        _wp_base(m, H, "hull_dark", 0.04)
        for k in range(5):
            m.box((0.03, 1.1, 0.03), (-0.4 + k * 0.2, 0, 0.055), "steel", 0.003)
        for k in range(4):
            m.box((0.9, 0.03, 0.03), (0, -0.45 + k * 0.3, 0.075), "brushed_alu", 0.003)
        for a in range(5):
            for b in range(4):
                if (a + b) % 2 == 0:
                    m.box((0.05, 0.05, 0.01), (-0.4 + a * 0.2, -0.45 + b * 0.3, 0.095), "em_cyan")


@family("wallpanel", WP_TALL, mount="wall", tags=["wall", "panel", "tall"], solid=False, mount_y=1.25)
def wallpanel_tall(m, i, label, rng):
    H = 2.4
    if i == 0:
        _wp_base(m, H, "hull_mid", 0.05)
        for k in range(8):
            m.box((0.08, 2.3, 0.08 if k % 2 else 0.05), (-0.42 + k * 0.12, 0, 0.07), "hull_light" if k % 2 else "hull_dark", 0.008)
        for yy in (-1.15, 0, 1.15):
            m.box((1.0, 0.06, 0.12), (0, yy, 0.06), "black_metal", 0.006)
    elif i == 1:
        _wp_base(m, H, "hull_light", 0.07)
        m.box((0.36, 1.7, 0.03), (0, 0.1, 0.085), "black_metal", 0.008)
        m.box((0.26, 1.6, 0.03), (0, 0.1, 0.09), "glass_blue")
        m.box((0.7, 0.12, 0.02), (0, -1.0, 0.08), "hull_mid")
        for k in range(4):
            m.box((0.03, 0.1, 0.03), (0.0, 1.0 - k * 0.4, 0.11), "steel")
        for sy in (-1, 1):
            m.box((0.06, 2.2, 0.02), (sy * 0.36, 0, 0.08), "hull_mid")
        m.box((0.2, 0.05, 0.01), (0, 1.1, 0.1), "em_cyan")
    elif i == 2:
        _wp_base(m, H, "hull_dark", 0.05)
        cols = ["copper", "steel", "paint_orange", "paint_blue", "brass"]
        for k, mm in enumerate(cols):
            r = 0.06 + 0.012 * (k % 2)
            x = -0.36 + k * 0.18
            m.cyl(r, 2.2, (x, 0, 0.05 + r), mm, "y", 10)
        for yy in (-0.9, -0.1, 0.8):
            m.box((0.96, 0.05, 0.05), (0, yy, 0.115), "black_metal", 0.004)
        m.box((0.3, 0.3, 0.1), (0.2, 0.5, 0.1), "gunmetal", 0.006)
        m.box((0.05, 0.05, 0.01), (0.2, 0.52, 0.155), "em_amber")
    elif i == 3:
        _wp_base(m, H, "hull_dark", 0.08)
        for k in (-1, 1):
            m.box((0.46, 2.2, 0.03), (k * 0.245, 0, 0.095), "paint_grey", 0.008)
            for j in range(6):
                m.box((0.3, 0.02, 0.012), (k * 0.245, 0.55 + j * 0.05, 0.115), "black_metal")
            m.box((0.04, 0.24, 0.05), (k * 0.245 - k * 0.15, -0.1, 0.13), "chrome", 0.005)
            m.box((0.12, 0.06, 0.012), (k * 0.245, 0.2, 0.115), "paint_white")
            m.box((0.05, 0.03, 0.01), (k * 0.245, -0.9, 0.115), "em_green")
    elif i == 4:
        _wp_base(m, H, "hull_dark", 0.05)
        m.box((0.05, 2.4, 0.06), (0, 0, 0.06), "em_cyan")
        for s in (-1, 1):
            m.box((0.42, 2.3, 0.03), (s * 0.26, 0, 0.065), "hull_mid", 0.008)
            for k in range(5):
                m.box((0.3, 0.02, 0.012), (s * 0.26, -0.9 + k * 0.45, 0.086), "black_metal")
    elif i == 5:
        _wp_base(m, H, "paint_grey", 0.05)
        hazard(m, -0.5, -1.2, 1.0, 0.3, 0.05, stripe=0.25)
        hazard(m, -0.5, 0.9, 1.0, 0.3, 0.05, stripe=0.25)
        m.box((0.08, 1.7, 0.02), (-0.3, -0.0, 0.06), "hazard_yellow")
        m.box((0.08, 1.7, 0.02), (0.3, 0.0, 0.06), "hazard_yellow")
        m.box((0.4, 0.3, 0.012), (0, 0.2, 0.06), "paint_white")
        m.box((0.3, 0.05, 0.012), (0, 0.2, 0.068), "paint_red")
    elif i == 6:
        _wp_base(m, H, "hull_mid", 0.1)
        m.box((0.8, 2.1, 0.09), (0, 0, 0.055), "black_metal", 0.006)
        m.box((0.7, 2.0, 0.02), (0, 0, 0.1), "gunmetal")
        for x, mm in ((-0.2, "steel"), (0.2, "paint_teal")):
            m.cyl(0.07, 1.9, (x, 0, 0.09), mm, "y", 10)
            for yy in (-0.7, 0.0, 0.7):
                m.torus(0.075, 0.015, (x, yy, 0.09), "black_metal", "y", 10, 5)
        m.box((0.44, 0.06, 0.05), (0, 0.4, 0.12), "brass", 0.004)
        m.box((0.06, 0.06, 0.01), (0, -0.95, 0.105), "em_amber")
    else:
        _wp_base(m, H, "wood_dark", 0.06)
        for r, hh in ((0.62, 0.9), (-0.55, 0.9)):
            m.box((0.8, hh, 0.03), (0, r, 0.07), "wood_light", 0.008)
            m.box((0.64, hh - 0.16, 0.02), (0, r, 0.09), "wood_dark", 0.006)
        m.box((1.0, 0.06, 0.1), (0, -1.2 + 0.03, 0.05), "gold_trim", 0.005)
        m.box((1.0, 0.06, 0.1), (0, 1.2 - 0.03, 0.05), "gold_trim", 0.005)
        m.box((0.7, 0.05, 0.07), (0, 0.03, 0.06), "gold_trim", 0.005)


# ==========================================================================
# floor panels (12), origin bottom-centre, thin
FLOOR_LABELS = ["grating 1x1", "diamond plate 2x2", "hatch handle 1x1", "cable cover 1x1", "hazard edge 2x2", "arrow marking 2x2",
                "carpet tile 1x1", "rubber studs 1x1", "glow edge 2x2", "hex tile 1x1", "checker 2x2", "deck seam 2x2"]


@family("floorpanel", FLOOR_LABELS, mount="floor", tags=["floor", "panel"], solid=False)
def floorpanel_fam(m, i, label, rng):
    if i == 0:
        m.box((1.0, 0.02, 1.0), (0, 0.01, 0), "black_metal")
        m.box((1.0, 0.045, 0.04), (0, 0.0225, 0.48), "steel", 0.004)
        m.box((1.0, 0.045, 0.04), (0, 0.0225, -0.48), "steel", 0.004)
        for k in range(12):
            m.box((0.03, 0.04, 0.9), (-0.44 + k * 0.08, 0.025, 0), "steel")
        for k in range(3):
            m.box((1.0, 0.02, 0.02), (0, 0.035, -0.3 + k * 0.3), "gunmetal")
    elif i == 1:
        m.box((2.0, 0.03, 2.0), (0, 0.015, 0), "hull_dark", 0.006)
        for a in range(6):
            for b in range(6):
                m.box((0.22, 0.008, 0.06), (-0.83 + a * 0.33, 0.034, -0.83 + b * 0.33), "steel", 0, rot=(0, PI / 4 if (a + b) % 2 else -PI / 4, 0))
        m.box((2.0, 0.036, 0.04), (0, 0.018, 0.98), "gunmetal", 0.004)
        m.box((2.0, 0.036, 0.04), (0, 0.018, -0.98), "gunmetal", 0.004)
    elif i == 2:
        m.box((1.0, 0.03, 1.0), (0, 0.015, 0), "hull_dark", 0.005)
        m.box((0.86, 0.02, 0.86), (0, 0.04, 0), "steel", 0.005)
        m.box((0.3, 0.02, 0.1), (0, 0.045, 0.0), "black_metal", 0.004)
        m.box((0.22, 0.03, 0.03), (0, 0.045, 0.0), "chrome", 0.004)
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.cyl(0.018, 0.012, (sx * 0.4, 0.05, sz * 0.4), "black_metal", "y", 6)
        m.box((0.86, 0.006, 0.02), (0, 0.052, 0.3), "em_amber")
    elif i == 3:
        m.box((1.0, 0.015, 1.0), (0, 0.0075, 0), "hull_dark")
        m.prism([(-0.5, 0.0), (-0.36, 0.045), (0.36, 0.045), (0.5, 0.0)], 0.5, (-0.25, 0.0, 0.0), "gunmetal", "zy")
        m.box((0.5, 0.005, 0.02), (0, 0.048, 0.0), "hazard_yellow")
        for k in range(5):
            m.box((0.5, 0.008, 0.03), (0, 0.05, -0.28 + k * 0.14), "steel")
    elif i == 4:
        m.box((2.0, 0.025, 2.0), (0, 0.0125, 0), "hull_mid", 0.005)
        for z in (-0.9, 0.9):
            m.box((2.0, 0.03, 0.2), (0, 0.015, z), "black_metal")
        for x in (-0.9, 0.9):
            m.box((0.2, 0.03, 1.6), (x, 0.015, 0), "black_metal")
        for k in range(8):
            m.box((0.1, 0.034, 0.2), (-0.875 + k * 0.25, 0.017, 0.9), "hazard_yellow", 0) if k % 2 == 0 else None
            m.box((0.1, 0.034, 0.2), (-0.875 + k * 0.25, 0.017, -0.9), "hazard_yellow") if k % 2 == 0 else None
        for k in range(6):
            if k % 2 == 0:
                m.box((0.2, 0.034, 0.1), (0.9, 0.017, -0.7 + k * 0.28), "hazard_yellow")
                m.box((0.2, 0.034, 0.1), (-0.9, 0.017, -0.7 + k * 0.28), "hazard_yellow")
        m.box((1.4, 0.03, 1.4), (0, 0.02, 0), "hull_light", 0.005)
    elif i == 5:
        m.box((2.0, 0.025, 2.0), (0, 0.0125, 0), "gunmetal", 0.005)
        for zz in (-0.55, 0.15):
            m.prism([(-0.4, zz + 0.55), (0.4, zz + 0.55), (0.0, zz + 1.05 - 0.0)], 0.01, (0, 0.025, 0), "hazard_yellow", "xz")
            m.box((0.24, 0.01, 0.45), (0, 0.03, zz + 0.3), "hazard_yellow")
        m.box((0.05, 0.012, 1.9), (-0.75, 0.03, 0), "em_amber")
        m.box((0.05, 0.012, 1.9), (0.75, 0.03, 0), "em_amber")
    elif i == 6:
        m.box((1.0, 0.015, 1.0), (0, 0.0075, 0), "st_carpet", 0.003)
        m.box((0.9, 0.01, 0.9), (0, 0.018, 0), "fabric_navy")
        m.box((0.7, 0.01, 0.7), (0, 0.024, 0), "fabric_teal")
        m.box((0.5, 0.01, 0.5), (0, 0.03, 0), "fabric_navy")
        m.box((0.3, 0.01, 0.3), (0, 0.036, 0), "gold_trim", 0, rot=(0, PI / 4, 0))
    elif i == 7:
        m.box((1.0, 0.012, 1.0), (0, 0.006, 0), "rubber", 0.003)
        for a in range(5):
            for b in range(5):
                m.cyl(0.05, 0.02, (-0.4 + a * 0.2, 0.02, -0.4 + b * 0.2), "plastic_grey" if (a + b) % 2 else "rubber", "y", 8, r2=0.04)
        m.box((1.0, 0.02, 0.04), (0, 0.01, 0.48), "hazard_yellow")
    elif i == 8:
        m.box((2.0, 0.03, 2.0), (0, 0.015, 0), "hull_dark", 0.005)
        m.box((1.7, 0.036, 1.7), (0, 0.018, 0), "hull_mid", 0.005)
        for zz in (-0.9, 0.9):
            m.box((1.9, 0.02, 0.05), (0, 0.035, zz), "em_cyan")
        for xx in (-0.9, 0.9):
            m.box((0.05, 0.02, 1.9), (xx, 0.035, 0), "em_cyan")
        for a in (-0.5, 0.5):
            for b in (-0.5, 0.5):
                m.cyl(0.05, 0.01, (a, 0.04, b), "em_cyan", "y", 10)
    elif i == 9:
        m.box((1.0, 0.015, 1.0), (0, 0.0075, 0), "black_metal")
        for r in range(4):
            for c in range(3 if r % 2 == 0 else 2):
                xx = (c - (2 if r % 2 == 0 else 1) / 2) * 0.32
                m.cyl(0.17, 0.03, (xx, 0.03, -0.36 + r * 0.24), ["brushed_alu", "hull_light", "paint_teal", "hull_mid"][(r + c) % 4], "y", 6, bevel=0.004)
    elif i == 10:
        m.box((2.0, 0.02, 2.0), (0, 0.01, 0), "black_metal")
        for a in range(4):
            for b in range(4):
                if (a + b) % 2 == 0:
                    m.box((0.5, 0.012, 0.5), (-0.75 + a * 0.5, 0.026, -0.75 + b * 0.5), "ceramic", 0.003)
    else:
        m.box((2.0, 0.025, 2.0), (0, 0.0125, 0), "hull_light", 0.005)
        m.box((0.02, 0.03, 2.0), (0, 0.0125, 0), "black_metal")
        m.box((2.0, 0.03, 0.02), (0, 0.0125, 0), "black_metal")
        for a in (-0.5, 0.5):
            for b in (-0.5, 0.5):
                bolt_row(m, (a - 0.4, 0.03, b - 0.4), (a + 0.4, 0.03, b - 0.4), 2, "steel", 0.02, 0.01, "y", 6)
                bolt_row(m, (a - 0.4, 0.03, b + 0.4), (a + 0.4, 0.03, b + 0.4), 2, "steel", 0.02, 0.01, "y", 6)
        for k, w in enumerate((0.1, 0.2, 0.1, 0.3)):
            m.box((w, 0.008, 0.36), (-0.35 + k * 0.22, 0.03, 0.62), "paint_grey")


# ==========================================================================
# ceiling panels (14) - origin centre of top surface, extends -Y
CEIL_LABELS = ["perforated 1x1", "vent slats 1x1", "access 1x1", "light recess 2x2", "cable cover 1x1", "grid tile 1x1", "egg crate 2x2",
               "dome light 1x1", "hazard hatch 1x1", "coffer 2x2", "speaker grille 1x1", "sprinkler 1x1", "strip lights 2x2", "diffuser 2x2"]


@family("ceilingpanel", CEIL_LABELS, mount="ceiling", tags=["ceiling", "panel"], solid=False)
def ceilingpanel_fam(m, i, label, rng):
    y = lambda h: -h  # depth below ceiling plane
    if i == 0:
        m.box((1.0, 0.03, 1.0), (0, -0.015, 0), "hull_light", 0.004)
        for a in range(5):
            for b in range(5):
                m.cyl(0.03, 0.006, (-0.4 + a * 0.2, -0.032, -0.4 + b * 0.2), "black_metal", "y", 8)
        m.box((1.0, 0.04, 0.03), (0, -0.02, 0.485), "hull_mid")
        m.box((1.0, 0.04, 0.03), (0, -0.02, -0.485), "hull_mid")
    elif i == 1:
        m.box((1.0, 0.05, 1.0), (0, -0.025, 0), "hull_dark", 0.005)
        m.box((0.86, 0.02, 0.86), (0, -0.05, 0), "black_metal")
        for k in range(8):
            m.box((0.86, 0.012, 0.06), (0, -0.065, -0.375 + k * 0.107), "steel", 0.002, rot=(0.5, 0, 0))
    elif i == 2:
        m.box((1.0, 0.04, 1.0), (0, -0.02, 0), "hull_mid", 0.005)
        m.box((0.84, 0.02, 0.84), (0, -0.045, 0), "hull_light", 0.004)
        for x in (-1, 1):
            m.cyl(0.035, 0.03, (x * 0.36, -0.06, 0.36), "steel", "y", 8)
            m.box((0.05, 0.03, 0.14), (x * 0.4, -0.055, -0.3), "black_metal", 0.004)
        m.box((0.16, 0.03, 0.05), (0, -0.06, 0.34), "black_metal", 0.004)
        m.box((0.04, 0.008, 0.04), (0, -0.07, -0.34), "em_amber")
    elif i == 3:
        m.box((2.0, 0.06, 2.0), (0, -0.03, 0), "hull_light", 0.005)
        m.box((1.7, 0.04, 1.7), (0, -0.07, 0), "hull_mid", 0.005)
        m.box((1.55, 0.02, 1.55), (0, -0.09, 0), "em_white")
        m.box((0.05, 0.03, 1.55), (0, -0.1, 0), "plastic_grey")
        m.box((1.55, 0.03, 0.05), (0, -0.1, 0), "plastic_grey")
    elif i == 4:
        m.box((1.0, 0.03, 1.0), (0, -0.015, 0), "hull_dark", 0.004)
        m.box((0.5, 0.11, 1.0), (0, -0.055, 0), "gunmetal", 0.012)
        m.box((0.4, 0.02, 0.92), (0, -0.115, 0), "hull_mid", 0.004)
        for k in range(5):
            m.cyl(0.018, 0.012, (0, -0.126, -0.38 + k * 0.19), "steel", "y", 6)
        m.box((0.06, 0.02, 0.06), (0.18, -0.115, 0.36), "em_green")
    elif i == 5:
        m.box((1.0, 0.03, 1.0), (0, -0.015, 0), "st_cream", 0.004)
        m.box((0.92, 0.008, 0.92), (0, -0.033, 0), "foam")
        for xx in (-1, 1):
            m.box((0.03, 0.04, 1.0), (xx * 0.485, -0.02, 0), "steel")
            m.box((1.0, 0.04, 0.03), (0, -0.02, xx * 0.485), "steel")
    elif i == 6:
        m.box((2.0, 0.02, 2.0), (0, -0.01, 0), "black_metal")
        for k in range(9):
            m.box((0.02, 0.09, 1.96), (-0.8 + k * 0.2, -0.065, 0), "brushed_alu")
        for k in range(9):
            m.box((1.96, 0.09, 0.02), (0, -0.065, -0.8 + k * 0.2), "brushed_alu") if k % 1 == 0 else None
        m.box((2.0, 0.06, 0.05), (0, -0.03, 0.975), "hull_mid")
        m.box((2.0, 0.06, 0.05), (0, -0.03, -0.975), "hull_mid")
    elif i == 7:
        m.box((1.0, 0.03, 1.0), (0, -0.015, 0), "hull_light", 0.004)
        m.cyl(0.36, 0.05, (0, -0.055, 0), "steel", "y", 20)
        m.torus(0.33, 0.03, (0, -0.08, 0), "chrome", "y", 20, 6)
        m.sphere(0.3, (0, -0.075, 0), "em_warm", 16, 8, (1, 0.5, 1))
        for k in range(4):
            a = PI / 2 * k + PI / 4
            m.cyl(0.02, 0.01, (0.42 * math.cos(a), -0.035, 0.42 * math.sin(a)), "steel", "y", 6)
    elif i == 8:
        m.box((1.0, 0.04, 1.0), (0, -0.02, 0), "black_metal", 0.004)
        for s in (-1, 1):
            hazard_box = None
            m.box((1.0, 0.045, 0.1), (0, -0.0225, s * 0.45), "hazard_yellow")
            m.box((0.1, 0.045, 0.8), (s * 0.45, -0.0225, 0), "hazard_yellow")
        m.box((0.72, 0.03, 0.72), (0, -0.05, 0), "hull_mid", 0.005)
        m.box((0.5, 0.02, 0.5), (0, -0.07, 0), "hull_light", 0.004)
        m.box((0.2, 0.03, 0.05), (0, -0.09, 0), "black_metal", 0.004)
        m.box((0.4, 0.006, 0.03), (0, -0.082, 0.22), "paint_red")
    elif i == 9:
        m.box((2.0, 0.05, 2.0), (0, -0.025, 0), "hull_light", 0.005)
        for a in (-0.5, 0.5):
            for b in (-0.5, 0.5):
                m.box((0.85, 0.06, 0.85), (a, -0.07, b), "hull_mid", 0.005)
                m.box((0.7, 0.03, 0.7), (a, -0.1, b), "hull_dark")
                m.box((0.5, 0.01, 0.03), (a, -0.12, b), "em_blue")
        m.box((0.16, 0.14, 0.16), (0, -0.07, 0), "black_metal", 0.008)
    elif i == 10:
        m.box((1.0, 0.04, 1.0), (0, -0.02, 0), "hull_dark", 0.004)
        m.cyl(0.4, 0.04, (0, -0.06, 0), "black_metal", "y", 24)
        for r in (0.34, 0.26, 0.18, 0.1):
            m.torus(r, 0.012, (0, -0.082, 0), "steel", "y", 20, 5)
        m.cyl(0.05, 0.03, (0, -0.085, 0), "chrome", "y", 10, r2=0.04)
        for k in range(4):
            a = PI / 2 * k + PI / 4
            m.cyl(0.02, 0.01, (0.44 * math.cos(a), -0.045, 0.44 * math.sin(a)), "steel", "y", 6)
    elif i == 11:
        m.box((1.0, 0.03, 1.0), (0, -0.015, 0), "st_cream", 0.004)
        m.cyl(0.14, 0.02, (0, -0.04, 0), "chrome", "y", 16)
        m.cyl(0.03, 0.09, (0, -0.09, 0), "brass", "y", 8)
        m.sphere(0.03, (0, -0.15, 0), "paint_red", 8, 5)
        m.box((0.07, 0.008, 0.01), (0, -0.135, 0), "steel")
        m.box((0.01, 0.008, 0.07), (0, -0.135, 0), "steel")
        m.box((0.3, 0.005, 0.03), (0.0, -0.033, 0.4), "paint_red")
    elif i == 12:
        m.box((2.0, 0.05, 2.0), (0, -0.025, 0), "hull_mid", 0.005)
        for k in (-1, 0, 1):
            m.box((1.7, 0.03, 0.22), (0, -0.06, k * 0.6), "black_metal", 0.005)
            m.box((1.6, 0.012, 0.14), (0, -0.078, k * 0.6), "em_white")
        for sx in (-1, 1):
            m.box((0.05, 0.04, 1.8), (sx * 0.9, -0.07, 0), "hull_dark")
    else:
        m.box((2.0, 0.05, 2.0), (0, -0.025, 0), "hull_light", 0.005)
        for k, s in enumerate((1.7, 1.3, 0.9, 0.5)):
            m.box((s, 0.03 + 0.03 * k, s), (0, -0.05 - 0.015 * k, 0), ("hull_mid", "steel", "hull_dark", "brushed_alu")[k], 0.006)
        m.cyl(0.07, 0.06, (0, -0.16, 0), "black_metal", "y", 10, r2=0.05)
        for k in range(4):
            a = PI / 2 * k + PI / 4
            m.cyl(0.02, 0.012, (0.9 * math.cos(a) * 1.0, -0.055, 0.9 * math.sin(a)), "steel", "y", 6)


# ==========================================================================
# pillars (14): 11 floor columns + 3 ceiling beams
COL_LABELS = ["square plinth", "fluted round", "h beam", "bulkhead frame", "buttress", "twin rods", "hex light", "arch rib", "truss", "pipe wrapped", "tapered ring"]
BEAM_LABELS = ["h beam 4m", "box beam light", "truss beam 4m"]
CH = 3.4


@family("pillar", COL_LABELS, mount="floor", tags=["structure", "column"], solid=True)
def pillar_col(m, i, label, rng):
    if i == 0:
        m.box((0.6, 0.15, 0.6), (0, 0.075, 0), "hull_dark", 0.015)
        m.box((0.42, CH - 0.3, 0.42), (0, CH / 2, 0), "hull_mid", 0.02)
        m.box((0.6, 0.15, 0.6), (0, CH - 0.075, 0), "hull_dark", 0.015)
        for s in (-1, 1):
            m.box((0.03, CH - 0.7, 0.03), (s * 0.15, CH / 2, 0.22), "em_cyan")
        for yy in (0.9, 1.7, 2.5):
            m.box((0.44, 0.03, 0.44), (0, yy, 0), "black_metal", 0.004)
        m.box((0.2, 0.08, 0.02), (0, 1.3, 0.22), "paint_white")
    elif i == 1:
        m.cyl(0.32, 0.12, (0, 0.06, 0), "hull_dark", "y", 20, r2=0.28)
        m.cyl(0.25, CH - 0.24, (0, CH / 2, 0), "hull_light", "y", 20)
        for k in range(10):
            a = 2 * PI * k / 10
            m.cyl(0.025, CH - 0.5, (0.25 * math.cos(a), CH / 2, 0.25 * math.sin(a)), "steel", "y", 5)
        m.cyl(0.28, 0.12, (0, CH - 0.06, 0), "hull_dark", "y", 20, r2=0.32)
        for yy in (0.4, CH - 0.4):
            m.torus(0.26, 0.03, (0, yy, 0), "gold_trim", "y", 20, 5)
    elif i == 2:
        m.box((0.6, 0.05, 0.6), (0, 0.025, 0), "hull_dark", 0.01)
        m.box((0.6, 0.05, 0.6), (0, CH - 0.025, 0), "hull_dark", 0.01)
        m.box((0.06, CH - 0.1, 0.34), (0, CH / 2, 0), "steel", 0.005)
        for s in (-1, 1):
            m.box((0.34, CH - 0.1, 0.05), (0, CH / 2, s * 0.17), "paint_orange", 0.006)
        for yy in (0.5, 1.7, 2.9):
            m.box((0.36, 0.05, 0.36), (0, yy, 0), "black_metal", 0.004)
        bolt_row(m, (-0.25, 0.06, 0.25), (0.25, 0.06, 0.25), 3, "steel", 0.025, 0.03, "y", 6)
        bolt_row(m, (-0.25, 0.06, -0.25), (0.25, 0.06, -0.25), 3, "steel", 0.025, 0.03, "y", 6)
    elif i == 3:
        for s in (-1, 1):
            m.box((0.3, CH, 0.34), (s * 0.85, CH / 2, 0), "hull_mid", 0.015)
            m.box((0.5, 0.1, 0.5), (s * 0.85, 0.05, 0), "hull_dark", 0.01)
            m.box((0.04, CH - 0.6, 0.03), (s * 0.85, CH / 2, 0.18), "em_amber")
        m.box((2.0, 0.55, 0.34), (0, CH - 0.28, 0), "hull_dark", 0.015)
        m.box((1.4, 0.06, 0.36), (0, CH - 0.6, 0), "hazard_yellow")
        m.box((1.0, 0.1, 0.03), (0, CH - 0.28, 0.18), "em_amber")
        bolt_row(m, (-0.85, CH - 0.45, 0.18), (0.85, CH - 0.45, 0.18), 6)
    elif i == 4:
        m.prism([(-0.55, 0), (0.45, 0), (0.45, 0.25), (-0.15, CH), (-0.55, CH)], 0.5, (-0.25, 0, 0), "hull_mid", "zy", bevel=0.012)
        m.box((0.6, 0.12, 0.9), (0, 0.06, -0.05), "hull_dark", 0.01)
        for yy in (0.8, 1.6, 2.4):
            m.box((0.54, 0.05, 0.9 - yy * 0.28), (0, yy, -0.1 - yy * 0.06 + 0.17), "black_metal", 0.004)
    elif i == 5:
        for s in (-1, 1):
            m.cyl(0.09, CH, (s * 0.3, CH / 2, 0), "steel", "y", 12)
            m.cyl(0.16, 0.1, (s * 0.3, 0.05, 0), "hull_dark", "y", 12)
            m.cyl(0.16, 0.1, (s * 0.3, CH - 0.05, 0), "hull_dark", "y", 12)
        for yy in (0.6, 1.5, 2.4):
            m.box((0.5, 0.06, 0.1), (0, yy, 0), "gunmetal", 0.008)
        m.link((-0.3, 0.7, 0), (0.3, 1.5, 0), 0.02, "black_metal", 6)
        m.link((0.3, 0.7, 0), (-0.3, 1.5, 0), 0.02, "black_metal", 6)
        m.link((-0.3, 1.6, 0), (0.3, 2.4, 0), 0.02, "black_metal", 6)
        m.link((0.3, 1.6, 0), (-0.3, 2.4, 0), 0.02, "black_metal", 6)
        for s in (-1, 1):
            m.torus(0.1, 0.02, (s * 0.3, 1.9, 0), "em_amber", "y", 12, 5)
    elif i == 6:
        m.cyl(0.36, 0.1, (0, 0.05, 0), "hull_dark", "y", 6)
        m.cyl(0.3, CH - 0.2, (0, CH / 2, 0), "hull_light", "y", 6)
        m.cyl(0.36, 0.1, (0, CH - 0.05, 0), "hull_dark", "y", 6)
        for k in range(6):
            a = 2 * PI * k / 6 + PI / 6
            r = 0.3 * math.cos(PI / 6) + 0.008
            m.box((0.05, CH - 0.7, 0.02), (r * math.cos(a), CH / 2, r * math.sin(a)), "em_white" if k % 2 == 0 else "hull_dark", 0, rot=(0, -a + PI / 2, 0))
        for yy in (0.7, CH - 0.7):
            m.cyl(0.32, 0.06, (0, yy, 0), "black_metal", "y", 6)
    elif i == 7:
        r = 1.3
        pts = [(-1.3, 0), (-1.3, 2.1)] + _arc(0, 2.1, 1.3, PI, 0, 14)[1:] + [(1.3, 0)]
        path_frame(m, pts, 0.28, 0.4, "hull_mid", 0, 0.012)
        path_frame(m, pts, 0.0, 0.5, "hull_dark", 0)
        path_frame(m, pts, -0.03, 0.05, "em_cyan", 0.2)
        for s in (-1, 1):
            m.box((0.6, 0.12, 0.6), (s * 1.44, 0.06, 0), "hull_dark", 0.01)
        m.box((0.4, 0.25, 0.5), (0, 3.4 - 0.05, 0), "gunmetal", 0.01)
    elif i == 8:
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.cyl(0.035, CH, (sx * 0.2, CH / 2, sz * 0.2), "steel", "y", 6)
        for k in range(6):
            y0, y1 = 0.2 + k * 0.5, 0.2 + (k + 1) * 0.5
            for sz in (-1, 1):
                m.link((-0.2, y0 if k % 2 == 0 else y1, sz * 0.2), (0.2, y1 if k % 2 == 0 else y0, sz * 0.2), 0.017, "hull_mid", 5)
            for sx in (-1, 1):
                m.link((sx * 0.2, y0 if k % 2 == 0 else y1, -0.2), (sx * 0.2, y1 if k % 2 == 0 else y0, 0.2), 0.017, "hull_mid", 5)
        m.box((0.5, 0.08, 0.5), (0, 0.04, 0), "hull_dark", 0.008)
        m.box((0.5, 0.08, 0.5), (0, CH - 0.04, 0), "hull_dark", 0.008)
        for yy in (0.2, 1.7, 3.2):
            m.box((0.44, 0.04, 0.44), (0, yy, 0), "black_metal", 0.004)
        m.box((0.05, 0.05, 0.02), (0, 1.7, 0.21), "em_amber")
    elif i == 9:
        m.cyl(0.16, CH, (0, CH / 2, 0), "hull_mid", "y", 12)
        m.box((0.55, 0.08, 0.55), (0, 0.04, 0), "hull_dark", 0.008)
        m.box((0.55, 0.08, 0.55), (0, CH - 0.04, 0), "hull_dark", 0.008)
        for k, (a, r, mm) in enumerate(((0.9, 0.06, "copper"), (2.5, 0.05, "paint_blue"), (4.3, 0.045, "steel"))):
            x, z = 0.26 * math.cos(a), 0.26 * math.sin(a)
            m.cyl(r, CH - 0.2, (x, CH / 2, z), mm, "y", 10)
            for yy in (0.5, 1.7, 2.9):
                m.link((0.16 * math.cos(a), yy, 0.16 * math.sin(a)), (x, yy, z), 0.015, "black_metal", 5)
        m.cyl(0.09, 0.14, (0.26 * math.cos(0.9), 1.3, 0.26 * math.sin(0.9)), "black_metal", "y", 10)
        wheel(m, (0.26 * math.cos(0.9), 1.42, 0.26 * math.sin(0.9)), 0.1, "paint_red", "y", 3, 0.014)
    else:
        m.cyl(0.42, 0.14, (0, 0.07, 0), "hull_dark", "y", 16, r2=0.34)
        m.cyl(0.34, CH - 0.28, (0, CH / 2, 0), "hull_light", "y", 16, r2=0.2)
        m.cyl(0.24, 0.14, (0, CH - 0.07, 0), "hull_dark", "y", 16, r2=0.3)
        for k, yy in enumerate((0.6, 1.5, 2.4)):
            m.torus(0.31 - k * 0.045, 0.025, (0, yy, 0), "em_amber" if k == 1 else "black_metal", "y", 16, 5)


@family("pillar", BEAM_LABELS, mount="ceiling", tags=["structure", "beam"], solid=False)
def pillar_beam(m, i, label, rng):
    L = 4.0
    if i == 0:
        m.box((L, 0.04, 0.4), (0, -0.02, 0), "hull_dark", 0.008)
        m.box((L, 0.04, 0.4), (0, -0.38, 0), "hull_dark", 0.008)
        m.box((L, 0.32, 0.06), (0, -0.2, 0), "steel", 0.006)
        for k in range(5):
            m.box((0.04, 0.32, 0.18), (-1.6 + k * 0.8, -0.2, 0.12), "paint_orange", 0.004)
            m.box((0.04, 0.32, 0.18), (-1.6 + k * 0.8, -0.2, -0.12), "paint_orange", 0.004)
        for s in (-1, 1):
            m.box((0.05, 0.3, 0.42), (s * (L / 2 - 0.03), -0.2, 0), "black_metal", 0.004)
    elif i == 1:
        m.box((L, 0.36, 0.5), (0, -0.18, 0), "hull_mid", 0.02)
        m.box((L - 0.4, 0.03, 0.3), (0, -0.375, 0), "em_white")
        m.box((L, 0.06, 0.06), (0, -0.34, 0.24), "black_metal")
        m.box((L, 0.06, 0.06), (0, -0.34, -0.24), "black_metal")
        for k in range(5):
            m.box((0.05, 0.38, 0.52), (-1.8 + k * 0.9, -0.18, 0), "hull_dark", 0.005)
        for s in (-1, 1):
            m.box((0.06, 0.38, 0.54), (s * (L / 2 - 0.03), -0.18, 0), "black_metal", 0.004)
    else:
        for z in (-0.2, 0.2):
            m.box((L, 0.06, 0.06), (0, -0.04, z), "steel", 0.004)
            m.box((L, 0.06, 0.06), (0, -0.46, z), "steel", 0.004)
            for k in range(8):
                x0 = -L / 2 + k * L / 8
                m.link((x0, -0.04 if k % 2 == 0 else -0.46, z), (x0 + L / 8, -0.46 if k % 2 == 0 else -0.04, z), 0.02, "hull_mid", 5)
        for k in range(5):
            m.box((0.05, 0.46, 0.46), (-L / 2 + 0.03 + k * (L - 0.06) / 4, -0.25, 0), "hull_dark", 0.004)
        m.box((0.3, 0.05, 0.1), (0, -0.5, 0), "em_amber")


# ==========================================================================
# pipes (20): 14 wall runs (mount_y 2.2), 6 ceiling runs
class Surf:
    """Maps (x along, u away from mounting surface, v lateral) to game coords."""

    def __init__(self, wall):
        self.wall = wall
        self.nax = "z" if wall else "y"     # axis pointing away from surface
        self.lax = "y" if wall else "z"     # lateral axis

    def p(self, x, u, v):
        return (x, v, u) if self.wall else (x, -u, v)

    def box(self, m, sx, su, sv, x, u, v, mat, bevel=0.0):
        if self.wall:
            m.box((sx, sv, su), (x, v, u), mat, bevel)
        else:
            m.box((sx, su, sv), (x, -u, v), mat, bevel)

    def xcyl(self, m, r, L, x, u, v, mat, seg=12, r2=None):
        m.cyl(r, L, self.p(x, u, v), mat, "x", seg, r2=r2)

    def ncyl(self, m, r, L, x, u, v, mat, seg=10, r2=None):
        m.cyl(r, L, self.p(x, u, v), mat, self.nax, seg, r2=r2)

    def lcyl(self, m, r, L, x, u, v, mat, seg=10, r2=None):
        m.cyl(r, L, self.p(x, u, v), mat, self.lax, seg, r2=r2)


def _bracket(m, S, x, u, v, r, mat="black_metal"):
    S.box(m, 0.06, 0.012, 0.09, x, 0.006, v, mat)
    S.box(m, 0.03, max(0.01, u - r), 0.025, x, (u - r) / 2, v, mat)
    m.torus(r + 0.008, 0.011, S.p(x, u, v), mat, "x", 12, 5)


def _hpipe(m, S, x0, x1, u, v, r, mat, seg=12):
    S.xcyl(m, r, x1 - x0, (x0 + x1) / 2, u, v, mat, seg)


def _flange(m, S, x, u, v, r, mat="steel"):
    S.xcyl(m, r * 1.5, 0.035, x, u, v, mat, 14)
    for k in range(6):
        a = 2 * PI * k / 6
        yy, zz = v + r * 1.25 * math.cos(a), u + r * 1.25 * math.sin(a)
        S.xcyl(m, 0.011, 0.05, x, zz, yy, "chrome", 5)


WALL_PIPES = ["straight plain", "flanged joints", "elbow up", "elbow jog", "tee branch", "valve wheel", "valve lever", "insulated wrapped",
              "double run", "triple bundle", "corrugated hose", "gauge tap", "expansion loop", "coolant glow"]
CEIL_PIPES = ["ceiling hanger run", "ceiling turn", "ceiling tee", "ceiling insulated pair", "ceiling flanged twin", "ceiling pump"]


def _pipe(m, S, kind, rng):
    if kind == "straight plain":
        r, u = 0.07, 0.11
        _hpipe(m, S, -1, 1, u, 0, r, "steel")
        for x in (-0.8, 0, 0.8):
            _bracket(m, S, x, u, 0, r)
        for x in (-0.4, 0.4):
            S.xcyl(m, r + 0.008, 0.05, x, u, 0, "gunmetal", 12)
    elif kind == "flanged joints":
        r, u = 0.06, 0.1
        _hpipe(m, S, -1, 1, u, 0, r, "paint_blue")
        for x in (-0.55, 0.0, 0.55):
            _flange(m, S, x, u, 0, r)
        for x in (-0.8, 0.8):
            _bracket(m, S, x, u, 0, r)
        S.box(m, 0.16, 0.005, 0.05, 0.25, u + r + 0.003, 0, "paint_white")
    elif kind == "elbow up":
        r, u = 0.05, 0.09
        pts = [S.p(-1, u, 0), S.p(0.0, u, 0), S.p(0.0, u, 0.95)]
        m.tube(pts, r, "copper", 10)
        _flange(m, S, -0.6, u, 0, r, "brass")
        _bracket(m, S, -0.8, u, 0, r)
        for vv in (0.5, 0.85):
            m.torus(r + 0.008, 0.011, S.p(0, u, vv), "black_metal", S.lax, 10, 5)
            S.box(m, 0.03, u - r, 0.06, 0, (u - r) / 2, vv, "black_metal")
        m.cyl(r * 1.4, 0.04, S.p(0, u, 0.95), "brass", S.lax, 10)
    elif kind == "elbow jog":
        r, u = 0.06, 0.1
        pts = [S.p(-1, u, -0.15), S.p(-0.3, u, -0.15), S.p(0.3, u, 0.25), S.p(1, u, 0.25)]
        m.tube(pts, r, "paint_orange", 10)
        _flange(m, S, -0.85, u, -0.15, r)
        _flange(m, S, 0.85, u, 0.25, r)
        for x, v in ((-0.6, -0.15), (0.6, 0.25)):
            _bracket(m, S, x, u, v, r)
    elif kind == "tee branch":
        r, u = 0.06, 0.1
        _hpipe(m, S, -1, 1, u, 0, r, "paint_teal")
        m.link(S.p(0.0, u, 0), S.p(0.0, u, 0.8), 0.045, "paint_teal", 10)
        m.cyl(0.075, 0.05, S.p(0, u, 0.82), "steel", S.lax, 12)
        m.cyl(0.05, 0.05, S.p(0, u, 0.86), "black_metal", S.lax, 10)
        for x in (-0.75, 0.75):
            _bracket(m, S, x, u, 0, r)
        _flange(m, S, -0.9, u, 0, r)
        _flange(m, S, 0.9, u, 0, r)
    elif kind == "valve wheel":
        r, u = 0.06, 0.1
        _hpipe(m, S, -1, 1, u, 0, r, "steel")
        m.sphere(0.13, S.p(0, u, 0), "brass", 12, 8)
        _flange(m, S, -0.2, u, 0, r, "brass")
        _flange(m, S, 0.2, u, 0, r, "brass")
        m.cyl(0.035, 0.32, S.p(0, u, 0.22), "chrome", S.lax, 8)
        m.cyl(0.07, 0.05, S.p(0, u, 0.13), "brass", S.lax, 10)
        wheel(m, S.p(0, u, 0.38), 0.15, "paint_red", S.lax, 4, 0.016)
        for x in (-0.75, 0.75):
            _bracket(m, S, x, u, 0, r)
    elif kind == "valve lever":
        r, u = 0.05, 0.09
        _hpipe(m, S, -1, 1, u, 0, r, "paint_grey")
        m.sphere(0.09, S.p(0, u, 0), "steel", 12, 8)
        m.cyl(0.03, 0.1, S.p(0, u, 0.11), "chrome", S.lax, 8)
        m.box((0.32, 0.03, 0.03) if S.wall else (0.32, 0.03, 0.03), S.p(0.16, u, 0.17), "paint_red", 0.005)
        S.box(m, 0.05, 0.05, 0.05, 0.32, u, 0.17, "paint_red", 0.005)
        m.sphere(0.018, S.p(-0.15, u, 0.1), "em_green", 6, 4)
        for x in (-0.75, 0.75):
            _bracket(m, S, x, u, 0, r)
        _flange(m, S, -0.25, u, 0, r)
        _flange(m, S, 0.25, u, 0, r)
    elif kind == "insulated wrapped":
        r, u = 0.11, 0.17
        _hpipe(m, S, -1, 1, u, 0, r, "st_cream", 14)
        for k in range(7):
            S.xcyl(m, r + 0.008, 0.06, -0.85 + k * 0.28, u, 0, "brushed_alu", 14)
        S.xcyl(m, r + 0.02, 0.05, -1.0, u, 0, "steel", 14)
        S.xcyl(m, r + 0.02, 0.05, 1.0, u, 0, "steel", 14)
        for x in (-0.55, 0.55):
            _bracket(m, S, x, u, 0, r, "gunmetal")
    elif kind == "double run":
        u = 0.08
        for v, r, mm in ((0.065, 0.045, "steel"), (-0.065, 0.045, "copper")):
            _hpipe(m, S, -1, 1, u, v, r, mm, 10)
        for x in (-0.7, 0.0, 0.7):
            S.box(m, 0.05, 0.03, 0.26, x, u, 0.0, "black_metal", 0.004)
            for v in (0.065, -0.065):
                m.torus(0.052, 0.01, S.p(x, u, v), "steel", "x", 10, 4)
            S.box(m, 0.04, u - 0.03, 0.04, x, (u - 0.03) / 2, 0, "black_metal")
        _flange(m, S, 0.4, u, 0.065, 0.045)
        _flange(m, S, -0.4, u, -0.065, 0.045, "brass")
    elif kind == "triple bundle":
        u = 0.09
        for v, r, mm in ((0.12, 0.04, "paint_blue"), (0.0, 0.04, "paint_red"), (-0.12, 0.04, "paint_green")):
            _hpipe(m, S, -1, 1, u, v, r, mm, 10)
        for x in (-0.75, -0.1, 0.75):
            S.box(m, 0.06, 0.02, 0.36, x, u + 0.04, 0, "steel", 0.004)
            S.box(m, 0.05, u - 0.0, 0.05, x, u / 2, 0.0, "black_metal")
        for v, mm in ((0.12, "em_cyan"), (0.0, "em_red"), (-0.12, "em_green")):
            S.xcyl(m, 0.045, 0.04, 0.4, u, v, mm, 10)
    elif kind == "corrugated hose":
        r, u = 0.07, 0.11
        for k in range(9):
            m.torus(r, 0.028, S.p(-0.72 + k * 0.18, u, 0), "black_metal" if k % 2 else "gunmetal", "x", 10, 4)
        S.xcyl(m, r * 0.9, 1.6, 0.0, u, 0, "rubber", 10)
        for s in (-1, 1):
            S.xcyl(m, r * 1.3, 0.16, s * 0.9, u, 0, "brass", 12)
            _flange(m, S, s * 0.98, u, 0, r, "steel")
            _bracket(m, S, s * 0.6, u, 0, r)
    elif kind == "gauge tap":
        r, u = 0.055, 0.1
        _hpipe(m, S, -1, 1, u, 0, r, "steel")
        for x, mm in ((-0.3, "em_green"), (0.35, "em_amber")):
            m.link(S.p(x, u, 0), S.p(x, u, 0.14), 0.02, "brass", 6)
            S.ncyl(m, 0.09, 0.05, x, u + 0.0, 0.22, "chrome", 14)
            S.ncyl(m, 0.07, 0.02, x, u + 0.035, 0.22, "plastic_white", 14)
            S.box(m, 0.008, 0.012, 0.06, x, u + 0.05, 0.245, "black_metal")
            S.box(m, 0.02, 0.012, 0.012, x, u + 0.05, 0.18, mm)
        for x in (-0.8, 0.8, 0.0):
            _bracket(m, S, x, u, 0, r)
        _flange(m, S, -0.6, u, 0, r)
    elif kind == "expansion loop":
        r, u = 0.05, 0.09
        pts = [S.p(-1, u, 0), S.p(-0.45, u, 0), S.p(-0.45, u, 0.45), S.p(0.45, u, 0.45), S.p(0.45, u, 0), S.p(1, u, 0)]
        m.tube(pts, r, "paint_orange", 10)
        for x, v in ((-0.8, 0), (0.8, 0), (0, 0.45)):
            _bracket(m, S, x, u, v, r)
        _flange(m, S, -0.62, u, 0, r)
        _flange(m, S, 0.62, u, 0, r)
    elif kind == "coolant glow":
        r, u = 0.065, 0.1
        for k in range(5):
            seg = 0.4
            x = -0.8 + k * seg
            if k % 2 == 0:
                _hpipe(m, S, x - seg / 2, x + seg / 2, u, 0, r, "steel")
            else:
                _hpipe(m, S, x - seg / 2, x + seg / 2, u, 0, r * 0.85, "em_cyan", 10)
        for x in (-0.6, -0.2, 0.2, 0.6):
            S.xcyl(m, r + 0.015, 0.04, x + 0.2, u, 0, "black_metal", 12) if x < 0.6 else None
        for x in (-0.9, 0.9):
            _bracket(m, S, x, u, 0, r)
    # ---- ceiling
    elif kind == "ceiling hanger run":
        r, u = 0.09, 0.2
        _hpipe(m, S, -1, 1, u, 0, r, "hull_light", 14)
        for x in (-0.7, 0.0, 0.7):
            m.torus(r + 0.01, 0.014, S.p(x, u, 0), "gunmetal", "x", 14, 5)
            m.cyl(0.009, u, S.p(x, u / 2, 0), "steel", S.nax, 5)
            S.box(m, 0.09, 0.012, 0.09, x, 0.006, 0, "black_metal")
        S.xcyl(m, r + 0.02, 0.05, -0.35, u, 0, "hull_dark", 14)
        S.xcyl(m, r + 0.02, 0.05, 0.35, u, 0, "hull_dark", 14)
    elif kind == "ceiling turn":
        r, u = 0.07, 0.15
        pts = [S.p(-1, u, 0), S.p(0.15, u, 0), S.p(0.15, u, 0.9)]
        m.tube(pts, r, "paint_grey", 10)
        _flange(m, S, -0.5, u, 0, r)
        for x, v in ((-0.7, 0), (0.15, 0.6)):
            m.cyl(0.009, u, S.p(x, u / 2, v), "steel", S.nax, 5)
            S.box(m, 0.08, 0.012, 0.08, x, 0.006, v, "black_metal")
            m.torus(r + 0.01, 0.012, S.p(x, u, v), "black_metal", "x" if v == 0 else S.lax, 12, 5)
        m.cyl(r * 1.4, 0.04, S.p(0.15, u, 0.92), "steel", S.lax, 12)
    elif kind == "ceiling tee":
        r, u = 0.06, 0.14
        _hpipe(m, S, -1, 1, u, 0, r, "paint_teal")
        m.link(S.p(0, u, -0.8), S.p(0, u, 0.8), 0.05, "paint_teal", 10)
        for v in (-0.85, 0.85):
            m.cyl(0.07, 0.05, S.p(0, u, v), "steel", S.lax, 12)
        for x, v in ((-0.7, 0), (0.7, 0), (0, 0.5), (0, -0.5)):
            m.cyl(0.009, u, S.p(x, u / 2, v), "steel", S.nax, 5)
            S.box(m, 0.08, 0.012, 0.08, x, 0.006, v, "black_metal")
        m.sphere(0.09, S.p(0, u, 0), "paint_teal", 12, 8)
        _flange(m, S, -0.9, u, 0, r)
        _flange(m, S, 0.9, u, 0, r)
    elif kind == "ceiling insulated pair":
        u = 0.16
        for v, r, mm in ((0.11, 0.08, "st_cream"), (-0.11, 0.08, "st_cream")):
            _hpipe(m, S, -1, 1, u, v, r, mm, 12)
            for k in range(5):
                S.xcyl(m, r + 0.008, 0.05, -0.8 + k * 0.4, u, v, "brushed_alu", 12)
        S.box(m, 0.06, u, 0.06, -0.5, u / 2, 0, "black_metal")
        S.box(m, 0.06, u, 0.06, 0.5, u / 2, 0, "black_metal")
        for x in (-0.5, 0.5):
            S.box(m, 0.07, 0.02, 0.4, x, u, 0, "black_metal", 0.004)
        S.xcyl(m, 0.09, 0.03, 1.0, u, 0.11, "hazard_yellow", 12)
        S.xcyl(m, 0.09, 0.03, 1.0, u, -0.11, "paint_blue", 12)
    elif kind == "ceiling flanged twin":
        u = 0.15
        for v, r, mm in ((0.1, 0.06, "paint_red"), (-0.1, 0.06, "steel")):
            _hpipe(m, S, -1, 1, u, v, r, mm)
            for x in (-0.6, 0.0, 0.6):
                _flange(m, S, x, u, v, r)
        for x in (-0.3, 0.3):
            S.box(m, 0.05, u, 0.05, x, u / 2, 0, "black_metal")
            S.box(m, 0.06, 0.02, 0.32, x, u, 0, "black_metal", 0.004)
    else:  # ceiling pump
        r, u = 0.07, 0.3
        _hpipe(m, S, -1, 1, u, 0, r, "steel")
        S.xcyl(m, 0.17, 0.4, -0.05, u, 0, "paint_blue", 16)
        S.xcyl(m, 0.12, 0.3, 0.3, u, 0, "gunmetal", 12)
        S.xcyl(m, 0.19, 0.04, -0.27, u, 0, "steel", 16)
        S.xcyl(m, 0.19, 0.04, 0.17, u, 0, "steel", 16)
        S.box(m, 0.06, 0.015, 0.06, -0.05, u - 0.19, 0.0, "em_green")
        for x in (-0.25, 0.25):
            S.box(m, 0.08, u, 0.08, x, u / 2, 0.0, "black_metal", 0.004)
        for x in (-0.8, 0.8):
            _bracket(m, S, x, u, 0, r)


@family("pipe", WALL_PIPES, mount="wall", tags=["pipe", "wall"], solid=False, mount_y=2.2)
def pipe_wall(m, i, label, rng):
    _pipe(m, Surf(True), label, rng)


@family("pipe", CEIL_PIPES, mount="ceiling", tags=["pipe", "ceiling"], solid=False)
def pipe_ceiling(m, i, label, rng):
    _pipe(m, Surf(False), label, rng)


# ==========================================================================
# cable trays (8): 4 ceiling + 4 wall
TRAY_CEIL = ["ladder tray", "perforated trough", "covered led tray", "fibre glow tray"]
TRAY_WALL = ["wire basket", "conduit bundle", "two tier tray", "flex conduit"]


def _cables(m, S, u, vs, x0=-0.95, x1=0.95, r=0.02):
    cols = ["paint_red", "rubber", "paint_blue", "copper", "paint_green", "plastic_white", "paint_orange"]
    for k, v in enumerate(vs):
        _hpipe(m, S, x0, x1, u, v, r, cols[k % len(cols)], 6)


def _hangers(m, S, xs, u, w):
    for x in xs:
        m.cyl(0.008, u, S.p(x, u / 2, w), "steel", S.nax, 5)
        m.cyl(0.008, u, S.p(x, u / 2, -w), "steel", S.nax, 5)
        S.box(m, 0.05, 0.01, 0.06, x, 0.005, w, "black_metal")
        S.box(m, 0.05, 0.01, 0.06, x, 0.005, -w, "black_metal")


@family("cabletray", TRAY_CEIL, mount="ceiling", tags=["cable", "tray"], solid=False)
def cabletray_ceil(m, i, label, rng):
    _cabletray(m, Surf(False), i)


@family("cabletray", TRAY_WALL, mount="wall", tags=["cable", "tray"], solid=False, mount_y=2.4)
def cabletray_wall(m, i, label, rng):
    _cabletray(m, Surf(True), i + 4)


def _cabletray(m, S, k):
    if k == 0:  # ladder tray
        u, w = 0.14, 0.2
        for v in (-w, w):
            S.box(m, 2.0, 0.06, 0.02, 0, u, v, "hull_mid", 0.004)
        for j in range(11):
            S.box(m, 0.025, 0.02, 2 * w, -0.9 + j * 0.18, u - 0.02, 0, "steel")
        _cables(m, S, u + 0.0, (-0.12, -0.04, 0.05, 0.13), r=0.028)
        _hangers(m, S, (-0.8, 0.8), u, w)
    elif k == 1:  # perforated trough
        u, w = 0.14, 0.22
        S.box(m, 2.0, 0.02, 2 * w, 0, u - 0.05, 0, "hull_dark", 0.004)
        for v in (-w, w):
            S.box(m, 2.0, 0.1, 0.02, 0, u, v, "hull_dark", 0.004)
        for j in range(12):
            S.box(m, 0.08, 0.005, 0.24, -0.88 + j * 0.16, u - 0.04, 0, "black_metal")
        _cables(m, S, u - 0.02, (-0.1, 0.0, 0.1), r=0.03)
        _hangers(m, S, (-0.75, 0.75), u - 0.05, w)
    elif k == 2:  # covered LED tray
        u, w = 0.14, 0.2
        S.box(m, 2.0, 0.1, 2 * w, 0, u, 0, "hull_light", 0.02)
        S.box(m, 1.8, 0.012, 0.05, 0, u - 0.054, 0, "em_cyan")
        for x in (-0.9, -0.3, 0.3, 0.9):
            S.box(m, 0.05, 0.11, 2 * w + 0.03, x, u, 0, "black_metal", 0.004)
        for s in (-1, 1):
            S.box(m, 1.8, 0.008, 0.02, 0, u - 0.05, s * 0.13, "steel")
        _hangers(m, S, (-0.6, 0.6), u, w)
    elif k == 3:  # fibre glow tray
        u, w = 0.12, 0.15
        S.box(m, 2.0, 0.03, 2 * w, 0, u, 0, "black_metal", 0.004)
        for v in (-w, w):
            S.box(m, 2.0, 0.08, 0.015, 0, u - 0.02, v, "gunmetal", 0.003)
        for v, mm in ((-0.08, "em_violet"), (0.0, "em_cyan"), (0.08, "em_blue")):
            _hpipe(m, S, -0.95, 0.95, u - 0.03, v, 0.016, mm, 6)
        S.box(m, 0.16, 0.1, 2 * w + 0.03, -0.55, u - 0.02, 0, "hull_dark", 0.005)
        S.box(m, 0.16, 0.1, 2 * w + 0.03, 0.55, u - 0.02, 0, "hull_dark", 0.005)
        S.box(m, 0.05, 0.012, 0.04, 0.55, u - 0.08, 0, "em_green")
        _hangers(m, S, (-0.85, 0.85), u, w)
    elif k == 4:  # wire basket
        u, w = 0.1, 0.2
        for v in (-w, w):
            _hpipe(m, S, -1, 1, u + 0.0, v, 0.008, "chrome", 5)
            _hpipe(m, S, -1, 1, u - 0.05, v, 0.008, "chrome", 5)
        for j in range(14):
            x = -0.95 + j * 0.146
            m.link(S.p(x, u - 0.05, -w), S.p(x, u - 0.05, w), 0.006, "chrome", 4)
            m.link(S.p(x, u - 0.05, w), S.p(x, u, w), 0.006, "chrome", 4)
            m.link(S.p(x, u - 0.05, -w), S.p(x, u, -w), 0.006, "chrome", 4)
        _hpipe(m, S, -1, 1, u - 0.05, 0, 0.007, "chrome", 5)
        _cables(m, S, u - 0.02, (-0.1, 0.0, 0.1), r=0.03)
        for x in (-0.7, 0.7):
            S.box(m, 0.04, u - 0.05, 0.04, x, (u - 0.05) / 2, w + 0.02, "steel")
            S.box(m, 0.04, u - 0.05, 0.04, x, (u - 0.05) / 2, -w - 0.02, "steel")
    elif k == 5:  # conduit bundle
        u = 0.1
        for v, u2, r, mm in ((-0.04, 0.05, 0.03, "steel"), (0.04, 0.05, 0.03, "paint_orange"), (0.0, 0.105, 0.03, "paint_blue"), (0.09, 0.105, 0.025, "black_metal"), (-0.09, 0.105, 0.025, "rubber")):
            _hpipe(m, S, -1, 1, u2, v, r, mm, 10)
        for x in (-0.7, 0.0, 0.7):
            S.box(m, 0.05, 0.03, 0.26, x, 0.14, 0.0, "hull_dark", 0.004)
            S.box(m, 0.05, 0.05, 0.05, x, 0.025, 0.0, "hull_dark")
        S.box(m, 0.2, 0.12, 0.2, 0.35, 0.09, 0.0, "gunmetal", 0.01)
        S.box(m, 0.04, 0.012, 0.04, 0.35, 0.156, 0.0, "em_amber")
    elif k == 6:  # two tier
        w = 0.17
        for u in (0.09, 0.3):
            for v in (-w, w):
                S.box(m, 2.0, 0.05, 0.02, 0, u, v, "hull_mid", 0.004)
            for j in range(9):
                S.box(m, 0.03, 0.015, 2 * w, -0.9 + j * 0.225, u - 0.02, 0, "steel")
        _cables(m, S, 0.1, (-0.08, 0.0, 0.08), r=0.025)
        _cables(m, S, 0.32, (-0.1, -0.03, 0.05, 0.11), r=0.025)
        for x in (-0.75, 0.75):
            S.box(m, 0.05, 0.35, 0.03, x, 0.175, w + 0.025, "black_metal", 0.003)
            S.box(m, 0.05, 0.35, 0.03, x, 0.175, -w - 0.025, "black_metal", 0.003)
    else:  # flex conduit
        u = 0.09
        for j in range(12):
            m.torus(0.035, 0.02, S.p(-0.9 + j * 0.165, u + 0.03 * math.sin(j / 2.0), 0.0), "black_metal" if j % 2 else "gunmetal", "x", 8, 4)
        for x in (-1.0, 1.0):
            S.xcyl(m, 0.05, 0.1, x * 0.96, u, 0, "brass", 10)
        for x in (-0.6, 0.0, 0.6):
            S.box(m, 0.05, u, 0.05, x, u / 2, 0, "black_metal")
            m.torus(0.048, 0.01, S.p(x, u, 0), "steel", "x", 10, 4)


# ==========================================================================
# railings (6)
RAIL_LABELS = ["guard tube", "guard balusters", "guard glass", "guard mesh", "service stair 4 step"]


@family("railing", RAIL_LABELS, mount="floor", tags=["railing", "safety"], solid=True)
def railing_fam(m, i, label, rng):
    if i == 0:
        for x in (-0.95, 0.0, 0.95):
            m.cyl(0.03, 1.05, (x, 0.525, 0), "steel", "y", 8)
            m.box((0.14, 0.02, 0.14), (x, 0.01, 0), "hull_dark", 0.004)
        m.cyl(0.035, 2.0, (0, 1.05, 0), "hazard_yellow", "x", 10)
        m.cyl(0.02, 2.0, (0, 0.6, 0), "steel", "x", 8)
        m.cyl(0.02, 2.0, (0, 0.25, 0), "steel", "x", 8)
        for x in (-0.95, 0.95):
            m.sphere(0.04, (x, 1.05, 0), "hazard_yellow", 8, 5)
    elif i == 1:
        for x in (-0.97, 0.97):
            m.box((0.06, 1.0, 0.06), (x, 0.5, 0), "gunmetal", 0.004)
        m.box((2.0, 0.05, 0.1), (0, 1.03, 0), "brushed_alu", 0.008)
        m.box((2.0, 0.05, 0.05), (0, 0.06, 0), "gunmetal", 0.004)
        for k in range(13):
            m.cyl(0.011, 0.95, (-0.9 + k * 0.15, 0.53, 0), "steel", "y", 5)
        m.box((2.0, 0.03, 0.035), (0, 0.55, 0), "gunmetal", 0.003)
        for x in (-0.97, 0.97):
            m.box((0.16, 0.02, 0.16), (x, 0.01, 0), "hull_dark", 0.004)
    elif i == 2:
        for x in (-0.98, 0.98):
            m.box((0.07, 1.02, 0.07), (x, 0.51, 0), "brushed_alu", 0.006)
            m.box((0.16, 0.02, 0.16), (x, 0.01, 0), "hull_dark", 0.004)
        m.box((1.9, 0.86, 0.02), (0, 0.55, 0), "glass_blue")
        m.box((2.0, 0.06, 0.09), (0, 1.03, 0), "brushed_alu", 0.01)
        m.box((1.9, 0.05, 0.05), (0, 0.1, 0), "brushed_alu", 0.006)
        m.box((1.8, 0.012, 0.03), (0, 0.15, 0.03), "em_cyan")
    elif i == 3:
        for x in (-0.97, 0.97):
            m.box((0.06, 1.05, 0.06), (x, 0.525, 0), "paint_grey", 0.004)
            m.box((0.16, 0.02, 0.16), (x, 0.01, 0), "hull_dark", 0.004)
        m.box((1.9, 0.03, 0.04), (0, 1.05, 0), "paint_grey", 0.005)
        m.box((1.9, 0.03, 0.04), (0, 0.1, 0), "paint_grey", 0.005)
        for k in range(7):
            m.link((-0.92 + k * 0.26, 0.1, 0), (-0.92 + (k + 1) * 0.26, 1.05, 0), 0.008, "steel", 4)
            m.link((-0.92 + (k + 1) * 0.26, 0.1, 0), (-0.92 + k * 0.26, 1.05, 0), 0.008, "steel", 4)
        m.box((1.9, 0.12, 0.012), (0, 0.06, 0.02), "hazard_yellow")
    else:  # service stair: 4 steps, rise 0.2, run 0.28, width 1.0, climbing toward -Z
        rise, run = 0.2, 0.28
        for k in range(4):
            zc = 0.42 - k * run
            top = (k + 1) * rise
            m.box((0.94, top, run - 0.01), (0, top / 2, zc), "hull_dark", 0.004)
            m.box((0.96, 0.03, run + 0.02), (0, top - 0.015, zc), "steel", 0.004)
            for j in range(5):
                m.box((0.05, 0.006, run - 0.06), (-0.36 + j * 0.18, top + 0.002, zc), "black_metal")
            m.box((0.94, 0.03, 0.012), (0, top - 0.1, zc + run / 2 + 0.012), "hazard_yellow")
        for s in (-1, 1):
            x = s * 0.5
            m.link((x, 0.2, 0.42), (x, 1.1, 0.42), 0.025, "hazard_yellow", 6)
            m.link((x, 0.8, 0.42 - 3 * run), (x, 1.7, 0.42 - 3 * run), 0.025, "hazard_yellow", 6)
            m.link((x, 1.1, 0.42), (x, 1.7, 0.42 - 3 * run), 0.03, "hazard_yellow", 8)
            m.link((x, 0.65, 0.42 - 1.5 * run), (x, 1.4, 0.42 - 1.5 * run), 0.02, "hazard_yellow", 6)
            m.box((0.05, 0.05, 0.05), (x, 0.2, 0.42), "black_metal")
        m.box((0.3, 0.012, 0.03), (0, 0.04, 0.6), "em_amber")


@family("railing", ["maintenance ladder"], mount="wall", tags=["ladder"], solid=False, mount_y=1.7)
def railing_ladder(m, i, label, rng):
    for s in (-1, 1):
        m.box((0.05, 3.4, 0.03), (s * 0.2, 0, 0.16), "steel", 0.004)
        for y in (-1.6, -0.5, 0.6, 1.6):
            m.box((0.04, 0.05, 0.13), (s * 0.2, y, 0.085), "black_metal", 0.004)
            m.box((0.08, 0.1, 0.012), (s * 0.2, y, 0.006), "hull_dark")
    for k in range(11):
        m.cyl(0.014, 0.4, (0, -1.5 + k * 0.3, 0.16), "brushed_alu", "x", 6)
    m.box((0.5, 0.05, 0.02), (0, -1.67, 0.16), "hazard_yellow")
    m.box((0.03, 0.05, 0.03), (0.0, 1.62, 0.18), "em_green")
