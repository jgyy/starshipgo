"""Engineering components: reactors, coils, capacitors, generators, tanks, turbines, valves,
junctions, nozzles and engineering tools (135 labels)."""
import math

from .. import kit

PI = math.pi
PARTS = {}
ORDER = []


def part(cat, label, mount="floor", solid=None, mount_y=None):
    def deco(fn):
        PARTS[(cat, label)] = (fn, mount, mount == "floor" if solid is None else solid, mount_y)
        ORDER.append((cat, label))
        return fn
    return deco


# ---------------------------------------------------------------- helpers
def bolts(m, pts, r=0.018, h=0.015, mat="steel", axis="y", seg=6):
    for p in pts:
        m.cyl(r, h, p, mat, axis=axis, seg=5)


def bolt_circle(m, cx, y, cz, R, n, r=0.018, mat="steel", axis="y", h=0.015):
    for k in range(n):
        a = 2 * PI * k / n
        if axis == "y":
            p = (cx + R * math.cos(a), y, cz + R * math.sin(a))
        elif axis == "z":
            p = (cx + R * math.cos(a), y + R * math.sin(a), cz)
        else:
            p = (cx, y + R * math.cos(a), cz + R * math.sin(a))
        m.cyl(r, h, p, mat, axis=axis, seg=5)


def hazard(m, x0, x1, y0, y1, z, depth=0.012, n=6, mat="hazard_yellow", bg="black_metal"):
    """Hazard-striped band on a +Z facing surface at depth z."""
    m.box((x1 - x0, y1 - y0, depth), ((x0 + x1) / 2, (y0 + y1) / 2, z), bg)
    w = (x1 - x0) / (n * 2 + 1)
    s = (y1 - y0) * 0.6
    for k in range(n):
        xa = x0 + w * (1 + 2 * k) - s * 0.0
        m.prism([(xa, y0), (xa + w, y0), (xa + w + s * 0.5, y1), (xa + s * 0.5, y1)][:4] if xa + w + s * 0.5 <= x1 else
                [(xa, y0), (xa + w, y0), (xa + w, y1), (xa, y1)], depth * 1.3, (0, 0, z - depth * 0.15), mat, plane="xy")


def hazard_ring(m, cx, y, cz, R, h, n=12, mat="hazard_yellow"):
    for k in range(0, n, 2):
        a0 = 2 * PI * k / n
        a1 = 2 * PI * (k + 1) / n
        pts = [(cx + R * math.cos(a0), cz + R * math.sin(a0)), (cx + R * math.cos(a1), cz + R * math.sin(a1)),
               (cx + (R + 0.012) * math.cos(a1), cz + (R + 0.012) * math.sin(a1)),
               (cx + (R + 0.012) * math.cos(a0), cz + (R + 0.012) * math.sin(a0))]
        m.prism(pts, h, (0, y, 0), mat, plane="xz")


def leds(m, x0, x1, y, z, mats, s=0.022):
    n = len(mats)
    for k, mt in enumerate(mats):
        x = x0 + (x1 - x0) * (k / max(1, n - 1))
        m.box((s, s, 0.012), (x, y, z), mt)


def led_pat(rng, n, on=("em_green", "em_amber", "em_red"), off="plastic_black"):
    return [rng.choice(on) if rng.random() < 0.6 else off for _ in range(n)]


def gauge(m, pos, r=0.06, face="plastic_white", tick="em_red"):
    x, y, z = pos
    m.cyl(r, 0.03, (x, y, z + 0.015), "chrome", axis="z", seg=16)
    m.cyl(r * 0.84, 0.006, (x, y, z + 0.032), face, axis="z", seg=16)
    m.box((r * 0.7, 0.008, 0.004), (x + r * 0.15, y + r * 0.2, z + 0.037), "black_metal", rot=(0, 0, 0.7))
    m.box((r * 0.25, 0.012, 0.004), (x - r * 0.5, y - r * 0.4, z + 0.036), tick)


def wheel(m, pos, R=0.12, spokes=3, mat="paint_red", stem=0.0):
    x, y, z = pos
    m.torus(R, 0.014, (x, y, z), mat, axis="z", seg=12, tseg=4)
    m.cyl(0.03, 0.05, (x, y, z), mat, axis="z", seg=8)
    for k in range(spokes):
        m.box((R * 2, 0.018, 0.018), (x, y, z), mat, rot=(0, 0, PI * k / spokes + 0.3))
    if stem:
        m.cyl(0.012, stem, (x, y, z - stem / 2), "chrome", axis="z", seg=6)


def flange(m, pos, r, axis="x", t=0.03, mat="steel", nb=6):
    m.cyl(r * 1.35, t, pos, mat, axis=axis, seg=14)
    x, y, z = pos
    for k in range(nb):
        a = 2 * PI * k / nb
        if axis == "x":
            p = (x, y + r * 1.15 * math.cos(a), z + r * 1.15 * math.sin(a))
        elif axis == "y":
            p = (x + r * 1.15 * math.cos(a), y, z + r * 1.15 * math.sin(a))
        else:
            p = (x + r * 1.15 * math.cos(a), y + r * 1.15 * math.sin(a), z)
        m.cyl(r * 0.13, t * 1.4, p, "black_metal", axis=axis, seg=4)


def pipe(m, a, b, r=0.04, mat="steel", fl=False):
    m.link(a, b, r, mat, seg=8)
    if fl:
        for p in (a, b):
            m.sphere(r * 1.25, p, mat, seg=8, ring=5)


def base_plate(m, sx, sz, h=0.06, mat="hull_dark", y=0.0):
    m.box((sx, h, sz), (0, y + h / 2, 0), mat, 0.01)
    bolts(m, [(sx / 2 - 0.05, y + h, sz / 2 - 0.05), (-sx / 2 + 0.05, y + h, sz / 2 - 0.05),
              (sx / 2 - 0.05, y + h, -sz / 2 + 0.05), (-sx / 2 + 0.05, y + h, -sz / 2 + 0.05)])


def ladder(m, x, z, y0, y1, w=0.4, face="z", mat="steel"):
    if face == "z":
        m.box((0.03, y1 - y0, 0.03), (x - w / 2, (y0 + y1) / 2, z), mat)
        m.box((0.03, y1 - y0, 0.03), (x + w / 2, (y0 + y1) / 2, z), mat)
        n = int((y1 - y0) / 0.28)
        for k in range(n):
            m.cyl(0.011, w, (x, y0 + 0.2 + k * 0.28, z), mat, axis="x", seg=5)
    else:
        m.box((0.03, y1 - y0, 0.03), (x, (y0 + y1) / 2, z - w / 2), mat)
        m.box((0.03, y1 - y0, 0.03), (x, (y0 + y1) / 2, z + w / 2), mat)
        n = int((y1 - y0) / 0.28)
        for k in range(n):
            m.cyl(0.011, w, (x, y0 + 0.2 + k * 0.28, z), mat, axis="z", seg=5)


def cabinet(m, w, h, d, body="hull_mid", bevel=0.015, plinth=0.08, y0=0.0):
    m.box((w, plinth, d - 0.02), (0, y0 + plinth / 2, 0), "black_metal")
    m.box((w, h - plinth, d), (0, y0 + plinth + (h - plinth) / 2, 0), body, bevel)
    m.box((w + 0.02, 0.02, d + 0.02), (0, y0 + h, 0), "hull_dark", 0.005)


def vents(m, x, y, z, w, n, h=0.012, gap=0.03, mat="black_metal"):
    for k in range(n):
        m.box((w, h, 0.01), (x, y + k * gap, z), mat)


def gauge_glass_tube(m, x, y0, y1, z, level=0.6, liquid="em_cyan"):
    m.cyl(0.014, y1 - y0, (x, (y0 + y1) / 2, z), "glass", seg=8)
    m.cyl(0.008, (y1 - y0) * level, (x, y0 + (y1 - y0) * level / 2, z), liquid, seg=6)
    m.cyl(0.02, 0.03, (x, y0, z), "steel", seg=8)
    m.cyl(0.02, 0.03, (x, y1, z), "steel", seg=8)


def helix(m, cx, cy0, cz, R, h, turns, r, mat, seg_per=10, wire=6):
    n = int(turns * seg_per)
    pts = []
    for k in range(n + 1):
        a = 2 * PI * k / seg_per
        pts.append((cx + R * math.cos(a), cy0 + h * k / n, cz + R * math.sin(a)))
    for a, b in zip(pts[:-1], pts[1:]):
        m.link(a, b, r, mat, seg=wire)


def em_band(m, cx, y, cz, r, h, mat="em_cyan", seg=20):
    m.cyl(r + 0.004, h, (cx, y, cz), mat, seg=seg)


# ================================================================ REACTOR (6)
@part("reactor", "Fusion Core Reactor")
def _(m, rng):
    m.cyl(1.25, 0.14, (0, 0.07, 0), "hull_dark", seg=28, bevel=0.01)
    hazard_ring(m, 0, 0.0, 0, 1.25, 0.14, n=20)
    m.cyl(1.0, 0.7, (0, 0.49, 0), "hull_mid", seg=28)
    bolt_circle(m, 0, 0.84, 0, 0.93, 6)
    m.cyl(0.9, 1.4, (0, 1.54, 0), "glass_blue", seg=28)
    m.cyl(0.5, 2.2, (0, 1.5, 0), "glass", seg=20)
    m.cyl(0.26, 2.3, (0, 1.5, 0), "em_cyan", seg=14)
    for k in range(4):
        a = PI / 2 * k + 0.4
        m.cyl(0.05, 1.5, (0.9 * math.cos(a), 1.54, 0.9 * math.sin(a)), "steel", seg=8)
    for y in (0.85, 1.55, 2.25):
        m.torus(0.92, 0.07, (0, y, 0), "steel", seg=20, tseg=5)
    m.cyl(1.0, 0.16, (0, 2.34, 0), "hull_dark", seg=28, r2=0.85)
    m.cyl(0.85, 0.5, (0, 2.67, 0), "hull_mid", seg=28, r2=0.55)
    m.cyl(0.5, 0.12, (0, 2.98, 0), "black_metal", seg=20)
    for k in range(4):
        a = PI / 2 * k + PI / 4
        pipe(m, (0.6 * math.cos(a), 2.7, 0.6 * math.sin(a)), (1.1 * math.cos(a), 2.3, 1.1 * math.sin(a)), 0.05, "copper")
        pipe(m, (1.1 * math.cos(a), 2.3, 1.1 * math.sin(a)), (1.15 * math.cos(a), 0.3, 1.15 * math.sin(a)), 0.05, "copper")
    m.box((0.5, 0.25, 0.06), (0, 0.5, 1.01), "black_metal", 0.01)
    leds(m, -0.18, 0.18, 0.5, 1.05, ["em_green", "em_green", "em_amber", "em_red"])
    m.screen((0.3, 0.16), (0, 0.32, 1.02), "power", bezel=0.01)


@part("reactor", "Plasma Tokamak Torus")
def _(m, rng):
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.14, 0.9, 0.14), (sx * 0.8, 0.45, sz * 0.8), "hull_dark", 0.01)
            m.box((0.24, 0.05, 0.24), (sx * 0.8, 0.025, sz * 0.8), "steel")
    m.box((2.0, 0.08, 2.0), (0, 0.92, 0), "hull_dark", 0.01)
    m.cyl(0.55, 0.9, (0, 0.45, 0), "hull_mid", seg=20)
    m.torus(0.85, 0.36, (0, 1.4, 0), "steel", seg=24, tseg=8)
    m.torus(0.85, 0.11, (0, 1.4, 0), "em_violet", seg=24, tseg=5)
    m.torus(0.85, 0.37, (0, 1.4, 0), "glass_blue", seg=24, tseg=8, arc=PI * 0.5)
    for k in range(8):
        a = 2 * PI * k / 8 + 0.2
        m.torus(0.5, 0.05, (0.85 * math.cos(a), 1.4, 0.85 * math.sin(a)), "copper", axis="x",
                seg=10, tseg=4, rot=(0, -a - PI / 2, 0))
    m.cyl(0.32, 0.8, (0, 1.9, 0), "hull_mid", seg=16)
    m.cyl(0.4, 0.15, (0, 2.35, 0), "steel", seg=16)
    m.cyl(0.15, 0.4, (0, 2.6, 0), "gunmetal", seg=12)
    for a in (0.4, 2.0, 3.6, 5.2):
        m.cyl(0.09, 0.3, (1.28 * math.cos(a), 1.4, 1.28 * math.sin(a)), "steel", axis="y", seg=10, rot=(0, 0, 0))
        flange(m, (1.28 * math.cos(a), 1.55, 1.28 * math.sin(a)), 0.07, "y")
    hazard_ring(m, 0, 0.88, 0, 1.0, 0.05, n=16)


@part("reactor", "Matter Antimatter Injector")
def _(m, rng):
    for x in (-0.9, 0.9):
        m.box((0.16, 1.0, 0.7), (x, 0.5, 0), "hull_dark", 0.015)
        m.box((0.3, 0.06, 0.9), (x, 0.03, 0), "steel")
    m.cyl(0.32, 1.2, (-0.85, 1.25, 0), "paint_red", axis="x", seg=20)
    m.cyl(0.32, 1.2, (0.85, 1.25, 0), "paint_blue", axis="x", seg=20)
    for x in (-1.3, -1.0, -0.7, 0.7, 1.0, 1.3):
        m.torus(0.34, 0.035, (x, 1.25, 0), "chrome", axis="x", seg=16, tseg=5)
    m.cyl(0.22, 0.9, (-0.2, 1.25, 0), "hull_light", axis="x", seg=16, r2=0.12)
    m.cyl(0.22, 0.9, (0.2, 1.25, 0), "hull_light", axis="x", seg=16, r2=0.22)
    m.sphere(0.36, (0, 1.25, 0), "glass_dark", seg=20, ring=12)
    m.sphere(0.2, (0, 1.25, 0), "em_violet", seg=14, ring=8)
    m.torus(0.42, 0.04, (0, 1.25, 0), "gold_trim", axis="x", seg=20, tseg=6)
    m.torus(0.42, 0.04, (0, 1.25, 0), "gold_trim", axis="z", seg=20, tseg=6)
    m.box((0.6, 0.5, 0.5), (0, 0.85, 0), "hull_mid", 0.02)
    m.cyl(0.14, 0.5, (0, 1.85, 0), "steel", seg=12)
    m.cyl(0.05, 0.5, (0, 2.3, 0), "chrome", seg=8)
    hazard(m, -0.28, 0.28, 0.78, 0.9, 0.26)
    for x in (-1.55, 1.55):
        m.cyl(0.12, 0.2, (x, 1.25, 0), "steel", axis="x", seg=12)
        m.sphere(0.13, (x * 1.06, 1.25, 0), "em_red" if x < 0 else "em_cyan", seg=10, ring=6)


@part("reactor", "Auxiliary Reactor")
def _(m, rng):
    base_plate(m, 1.5, 1.3, 0.12)
    m.box((1.2, 1.6, 1.0), (0, 0.92, 0), "paint_grey", 0.03)
    m.box((1.24, 0.08, 1.04), (0, 1.76, 0), "hull_dark", 0.01)
    m.box((0.7, 0.55, 0.05), (0, 1.15, 0.5), "black_metal", 0.02)
    m.box((0.55, 0.4, 0.03), (0, 1.15, 0.53), "glass_amber")
    m.box((0.4, 0.25, 0.02), (0, 1.15, 0.54), "em_orange")
    for sx in (-1, 1):
        for k in range(9):
            m.box((0.05, 1.3, 0.85), (sx * (0.65 + k * 0.045), 0.95, 0), "steel")
        m.box((0.03, 1.3, 0.05), (sx * 1.03, 0.95, 0.45), "black_metal")
    hazard(m, -0.55, 0.55, 0.2, 0.32, 0.51)
    leds(m, -0.4, 0.4, 0.6, 0.51, ["em_green", "em_green", "em_green", "em_amber", "em_red"])
    gauge(m, (-0.4, 1.55, 0.5), 0.07)
    gauge(m, (0.4, 1.55, 0.5), 0.07)
    m.cyl(0.14, 0.4, (0.3, 1.98, -0.1), "hull_dark", seg=12)
    m.cyl(0.18, 0.05, (0.3, 2.2, -0.1), "steel", seg=12)
    pipe(m, (-0.3, 1.8, -0.3), (-0.3, 2.3, -0.3), 0.05, "copper")
    pipe(m, (-0.3, 2.3, -0.3), (-0.05, 2.3, -0.3), 0.05, "copper")


@part("reactor", "Reactor Control Pillar")
def _(m, rng):
    m.cyl(0.55, 0.12, (0, 0.06, 0), "hull_dark", seg=6, bevel=0.01)
    pts = [(0.4 * math.cos(PI / 3 * k), 0.4 * math.sin(PI / 3 * k)) for k in range(6)]
    m.prism(pts, 1.75, (0, 0.12, 0), "hull_mid")
    m.prism([(0.43 * math.cos(PI / 3 * k), 0.43 * math.sin(PI / 3 * k)) for k in range(6)], 0.08, (0, 1.87, 0), "hull_dark")
    m.cyl(0.32, 0.1, (0, 2.0, 0), "black_metal", seg=6)
    m.cyl(0.28, 0.35, (0, 2.2, 0), "glass_blue", seg=12)
    m.cyl(0.1, 0.35, (0, 2.2, 0), "em_cyan", seg=8)
    m.cyl(0.3, 0.06, (0, 2.4, 0), "hull_dark", seg=12)
    m.screen((0.3, 0.36), (0, 1.45, 0.352), "power", bezel=0.015)
    for sx in (-1, 1):
        m.box((0.05, 0.6, 0.02), (sx * 0.28, 1.45, 0.34), "em_cyan" if sx < 0 else "em_amber")
    m.box((0.36, 0.14, 0.06), (0, 0.98, 0.42), "black_metal", 0.01)
    for k in range(5):
        m.box((0.03, 0.05, 0.05), (-0.13 + k * 0.065, 0.98, 0.46), "em_green" if k % 2 else "em_amber")
    m.cyl(0.05, 0.03, (0.13, 0.75, 0.42), "chrome", axis="z", seg=10)
    m.cyl(0.07, 0.03, (-0.05, 0.75, 0.42), "black_metal", axis="z", seg=10)
    m.cyl(0.07, 0.06, (0.13, 0.62, 0.44), "paint_red", axis="z", seg=12)
    hazard(m, -0.25, 0.25, 0.3, 0.4, 0.41, n=5)


@part("reactor", "Emergency Reactor")
def _(m, rng):
    m.box((1.5, 0.1, 1.2), (0, 0.05, 0), "hazard_yellow", 0.01)
    m.box((1.4, 0.06, 1.1), (0, 0.13, 0), "black_metal", 0.01)
    m.cyl(0.42, 1.2, (0, 0.85, 0), "paint_red", axis="x", seg=22, bevel=0.01)
    for x in (-0.6, -0.2, 0.2, 0.6):
        m.torus(0.43, 0.025, (x, 0.85, 0), "steel", axis="x", seg=20, tseg=5)
    m.cyl(0.43, 0.06, (-0.62, 0.85, 0), "hull_dark", axis="x", seg=22)
    m.sphere(0.4, (0.62, 0.85, 0), "paint_red", seg=16, ring=8, scale=(0.35, 1, 1))
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.link((sx * 0.7, 0.15, sz * 0.5), (sx * 0.7, 1.6, sz * 0.5), 0.025, "steel")
        m.link((sx * 0.7, 1.6, -0.5), (sx * 0.7, 1.6, 0.5), 0.025, "steel")
    m.link((-0.7, 1.6, 0.5), (0.7, 1.6, 0.5), 0.025, "steel")
    m.link((-0.7, 1.6, -0.5), (0.7, 1.6, -0.5), 0.025, "steel")
    m.box((0.5, 0.3, 0.06), (-0.1, 0.9, 0.44), "black_metal", 0.01)
    m.cyl(0.06, 0.03, (-0.2, 0.9, 0.49), "paint_red", axis="z", seg=10)
    leds(m, -0.05, 0.1, 0.9, 0.48, ["em_amber", "em_red", "em_green"])
    m.cyl(0.12, 0.7, (-0.3, 1.5, -0.2), "gunmetal", seg=10)
    m.cyl(0.16, 0.05, (-0.3, 1.87, -0.2), "steel", seg=10)
    m.box((0.36, 0.25, 0.04), (0.35, 1.25, 0.42), "paint_red")
    hazard(m, 0.1, 0.6, 0.5, 0.6, 0.44, n=4)
    m.cyl(0.05, 0.3, (0.75, 0.3, 0.6), "chrome", seg=8, axis="x")


# ================================================================ COIL (12)
@part("coil", "Warp Coil Stack")
def _(m, rng):
    base_plate(m, 1.0, 1.0, 0.1)
    m.cyl(0.12, 2.3, (0, 1.25, 0), "em_blue", seg=12)
    for k in range(7):
        y = 0.3 + k * 0.3
        R = 0.42 - 0.02 * abs(k - 3)
        m.torus(R, 0.08, (0, y, 0), "copper", seg=20, tseg=8)
        m.cyl(0.14, 0.05, (0, y - 0.15, 0), "gunmetal", seg=10)
    for a in (0.8, 2.4, 3.9, 5.5):
        m.link((0.48 * math.cos(a), 0.3, 0.48 * math.sin(a)), (0.48 * math.cos(a), 2.1, 0.48 * math.sin(a)), 0.02, "steel")
    m.cyl(0.25, 0.1, (0, 2.42, 0), "hull_dark", seg=12)
    m.sphere(0.13, (0, 2.55, 0), "em_cyan", seg=10, ring=6)


@part("coil", "Plasma Manifold")
def _(m, rng):
    base_plate(m, 1.6, 0.7, 0.08)
    m.cyl(0.13, 1.7, (0, 1.2, 0), "gunmetal", axis="x", seg=16)
    for x in (-0.75, 0.75):
        flange(m, (x, 1.2, 0), 0.13, "x")
        m.box((0.1, 1.1, 0.1), (x * 0.9, 0.62, 0), "hull_dark")
    for k, x in enumerate((-0.5, -0.17, 0.17, 0.5)):
        up = k % 2 == 0
        y1 = 1.85 if up else 0.5
        m.cyl(0.07, 0.65, (x, 1.2 + (0.33 if up else -0.33), 0), "steel", seg=12)
        flange(m, (x, y1, 0), 0.07, "y")
        m.cyl(0.05, 0.12, (x, 1.2, 0.16), "black_metal", axis="z", seg=8)
        wheel(m, (x, 1.2, 0.26), 0.09, 2, "paint_orange")
    m.torus(0.135, 0.03, (0, 1.2, 0), "em_violet", axis="x", seg=14, tseg=5)
    em_band(m, 0, 1.2, 0, 0.13, 0.05, "em_violet")
    m.cyl(0.135, 0.06, (0, 1.2, 0), "em_violet", axis="x", seg=14)


@part("coil", "Field Coil Ring", "wall")
def _(m, rng):
    m.box((1.9, 1.9, 0.05), (0, 0, 0.025), "hull_dark", 0.02)
    m.torus(0.7, 0.13, (0, 0, 0.2), "copper", axis="z", seg=30, tseg=10)
    for k in range(12):
        a = 2 * PI * k / 12
        m.cyl(0.15, 0.035, (0.7 * math.cos(a), 0.7 * math.sin(a), 0.2), "gold_trim", axis="x", seg=8,
              rot=(0, 0, a + PI / 2))
    m.torus(0.45, 0.03, (0, 0, 0.15), "em_cyan", axis="z", seg=28, tseg=6)
    for k in range(4):
        a = PI / 4 + PI / 2 * k
        m.link((0.6 * math.cos(a), 0.6 * math.sin(a), 0.2), (0.8 * math.cos(a), 0.8 * math.sin(a), 0.03), 0.04, "steel")
        m.box((0.16, 0.16, 0.06), (0.8 * math.cos(a), 0.8 * math.sin(a), 0.06), "steel", 0.01)
    m.box((0.2, 0.14, 0.1), (0, -0.7, 0.32), "black_metal", 0.01)
    leds(m, -0.06, 0.06, -0.7, 0.38, ["em_green", "em_amber"])


@part("coil", "Magnetic Bottle")
def _(m, rng):
    m.cyl(0.5, 0.2, (0, 0.1, 0), "hull_dark", seg=20, r2=0.42, bevel=0.01)
    m.cyl(0.18, 0.5, (0, 0.45, 0), "gunmetal", seg=12)
    m.sphere(0.6, (0, 1.4, 0), "glass_blue", seg=24, ring=14, scale=(0.85, 1.05, 0.85))
    m.sphere(0.25, (0, 1.4, 0), "em_violet", seg=14, ring=8, scale=(0.8, 1.4, 0.8))
    for y in (0.85, 1.95):
        m.torus(0.42, 0.06, (0, y, 0), "copper", seg=22, tseg=8)
    for y in (1.15, 1.65):
        m.torus(0.56, 0.05, (0, y, 0), "brass", seg=22, tseg=8)
    m.cyl(0.14, 0.2, (0, 2.12, 0), "steel", seg=10)
    m.cyl(0.05, 0.3, (0, 2.35, 0), "chrome", seg=8)
    for a in (0.5, 2.6, 4.7):
        pipe(m, (0.42 * math.cos(a), 0.9, 0.42 * math.sin(a)), (0.3 * math.cos(a), 0.4, 0.3 * math.sin(a)), 0.02, "copper", False)


@part("coil", "EPS Conduit Trunk", "wall")
def _(m, rng):
    for k in range(3):
        x = -0.15 + k * 0.15
        m.cyl(0.055, 2.4, (x, 0, 0.09), ["copper", "gunmetal", "copper"][k], seg=10)
        m.cyl(0.058, 2.3, (x, 0, 0.09), ["em_amber", "em_cyan", "em_amber"][k], seg=10, r2=0.058)
        m.cyl(0.057, 2.25, (x, 0, 0.09), ["copper", "gunmetal", "copper"][k], seg=10)
    for y in (-1.0, -0.2, 0.6, 1.2):
        m.box((0.55, 0.08, 0.1), (0, y, 0.05), "hull_dark", 0.01)
        bolts(m, [(-0.24, y, 0.11), (0.24, y, 0.11)])
    m.box((0.55, 0.3, 0.16), (0, 0.2, 0.1), "black_metal", 0.02)
    leds(m, -0.18, 0.18, 0.2, 0.19, ["em_cyan", "em_amber", "em_cyan"])
    hazard(m, -0.25, 0.25, -1.12, -1.02, 0.12, n=5)
    flange(m, (0, 1.2, 0.09), 0.14, "y")


@part("coil", "Dilithium Crystal Chamber")
def _(m, rng):
    m.cyl(0.6, 0.35, (0, 0.175, 0), "hull_dark", seg=16, r2=0.5, bevel=0.01)
    m.cyl(0.42, 1.0, (0, 0.85, 0), "glass_blue", seg=20)
    for k in range(7):
        a = 2 * PI * k / 7 if k else 0
        rr = 0.22 if k else 0.0
        hgt = 0.5 + 0.25 * rng.random() if k else 0.9
        m.cyl(0.07, hgt, (rr * math.cos(a), 0.35 + hgt / 2, rr * math.sin(a)), "em_violet" if k % 2 else "em_blue",
              seg=6, r2=0.005, rot=(0.15 * math.sin(a), 0, -0.15 * math.cos(a)))
    m.cyl(0.46, 0.08, (0, 1.39, 0), "steel", seg=20)
    m.cyl(0.4, 0.15, (0, 1.5, 0), "hull_mid", seg=20, r2=0.25)
    m.cyl(0.08, 0.3, (0, 1.72, 0), "brass", seg=10)
    for k in range(4):
        a = PI / 2 * k + PI / 4
        m.link((0.5 * math.cos(a), 0.35, 0.5 * math.sin(a)), (0.5 * math.cos(a), 1.4, 0.5 * math.sin(a)), 0.03, "steel")
    m.torus(0.44, 0.03, (0, 0.5, 0), "gold_trim", seg=20, tseg=5)


@part("coil", "Injector Tower")
def _(m, rng):
    base_plate(m, 0.9, 0.9, 0.1)
    for k, (w, h) in enumerate([(0.6, 0.6), (0.5, 0.6), (0.42, 0.6), (0.34, 0.6), (0.26, 0.5)]):
        y = 0.1 + sum(hh for _, hh in [(0.6, 0.6), (0.5, 0.6), (0.42, 0.6), (0.34, 0.6), (0.26, 0.5)][:k])
        m.box((w, h, w), (0, y + h / 2, 0), "hull_mid" if k % 2 == 0 else "hull_dark", 0.015)
        m.torus(w * 0.75, 0.03, (0, y + h, 0), "brass", seg=14, tseg=5)
        m.box((w * 0.5, 0.06, 0.02), (0, y + h * 0.5, w / 2 + 0.005), "em_cyan" if k % 2 else "em_amber")
    m.cyl(0.08, 0.6, (0, 3.0, 0), "chrome", seg=8, r2=0.03)
    m.sphere(0.1, (0, 2.68, 0), "em_cyan", seg=10, ring=6)
    for a in (0.7, 2.3, 3.9, 5.5):
        pipe(m, (0.2 * math.cos(a), 2.2, 0.2 * math.sin(a)), (0.55 * math.cos(a), 0.4, 0.55 * math.sin(a)), 0.03, "copper", False)


@part("coil", "Helical Plasma Coil")
def _(m, rng):
    m.cyl(0.55, 0.15, (0, 0.075, 0), "hull_dark", seg=16, bevel=0.01)
    m.cyl(0.2, 1.9, (0, 1.05, 0), "glass_dark", seg=14)
    m.cyl(0.09, 1.9, (0, 1.05, 0), "em_orange", seg=8)
    helix(m, 0, 0.25, 0, 0.3, 1.6, 4, 0.045, "copper", seg_per=8)
    for a in (0.6, 3.7):
        m.link((0.36 * math.cos(a), 0.25, 0.36 * math.sin(a)), (0.36 * math.cos(a), 1.85, 0.36 * math.sin(a)), 0.02, "brass")
    m.cyl(0.42, 0.1, (0, 2.05, 0), "hull_dark", seg=16, r2=0.3)
    m.cyl(0.1, 0.25, (0, 2.22, 0), "steel", seg=10)
    for a in (0, PI):
        m.link((0.3 * math.cos(a), 0.25, 0.3 * math.sin(a)), (0.55 * math.cos(a), 0.25, 0.55 * math.sin(a)), 0.03, "copper")


@part("coil", "Wall Coil Bank", "wall")
def _(m, rng):
    m.box((1.3, 1.6, 0.05), (0, 0, 0.025), "hull_dark", 0.02)
    for k in range(4):
        y = -0.6 + k * 0.4
        m.cyl(0.14, 1.0, (0, y, 0.19), "gunmetal", axis="x", seg=14)
        for j in range(7):
            m.cyl(0.165, 0.05, (-0.35 + j * 0.115, y, 0.19), "copper", axis="x", seg=10)
        m.cyl(0.1, 0.06, (-0.53, y, 0.19), "em_cyan" if k % 2 else "em_amber", axis="x", seg=10)
        m.cyl(0.1, 0.06, (0.53, y, 0.19), "em_cyan" if k % 2 else "em_amber", axis="x", seg=10)
        m.box((0.08, 0.2, 0.14), (-0.55, y, 0.1), "steel")
        m.box((0.08, 0.2, 0.14), (0.55, y, 0.1), "steel")


@part("coil", "Discharge Coil Tower")
def _(m, rng):
    m.cyl(0.5, 0.12, (0, 0.06, 0), "hull_dark", seg=16)
    m.cyl(0.33, 1.3, (0, 0.77, 0), "black_metal", seg=18, r2=0.2)
    helix(m, 0, 0.2, 0, 0.3, 0.3, 1, 0.01, "copper", wire=4)
    for k in range(9):
        r = 0.34 - 0.017 * k
        m.torus(r, 0.022, (0, 0.2 + k * 0.14, 0), "copper", seg=18, tseg=5)
    m.torus(0.35, 0.09, (0, 1.6, 0), "chrome", seg=24, tseg=8)
    m.sphere(0.14, (0, 1.8, 0), "chrome", seg=12, ring=8)
    for a in (0.3, 2.4, 4.5):
        m.link((0.35 * math.cos(a), 1.6, 0.35 * math.sin(a)), (0.6 * math.cos(a), 1.75, 0.6 * math.sin(a)), 0.01, "em_violet", seg=4)
        m.sphere(0.03, (0.6 * math.cos(a), 1.75, 0.6 * math.sin(a)), "em_white", seg=6, ring=4)


@part("coil", "Coil Gantry")
def _(m, rng):
    for sx in (-1, 1):
        m.box((0.16, 2.3, 0.5), (sx * 1.05, 1.15, 0), "hull_dark", 0.015)
        m.box((0.3, 0.06, 0.7), (sx * 1.05, 0.03, 0), "steel")
        m.box((0.12, 0.6, 0.08), (sx * 0.98, 1.2, 0.2), "black_metal")
    m.box((2.4, 0.16, 0.5), (0, 2.3, 0), "hull_dark", 0.015)
    for k, z in enumerate((-0.15, 0.0, 0.15)):
        m.torus(0.85, 0.07 - 0.005 * k, (0, 1.2, z), "copper", axis="z", seg=28, tseg=8)
    m.torus(0.7, 0.03, (0, 1.2, 0), "em_blue", axis="z", seg=28, tseg=5)
    for a in range(0, 360, 60):
        r = math.radians(a)
        m.link((0.85 * math.cos(r), 1.2 + 0.85 * math.sin(r), -0.15), (0.85 * math.cos(r), 1.2 + 0.85 * math.sin(r), 0.15), 0.025, "steel", 5)
    leds(m, -0.3, 0.3, 2.3, 0.26, ["em_green", "em_green", "em_amber", "em_green"])


@part("coil", "Plasma Conduit Elbow", "wall")
def _(m, rng):
    pts = [(-0.7, -0.7, 0.3), (-0.7, 0.3, 0.3), (0.7, 0.3, 0.3)]
    m.tube(pts, 0.14, "gunmetal", seg=14)
    m.torus(0.145, 0.03, (-0.7, 0.0, 0.3), "em_orange", axis="y", seg=14, tseg=5)
    m.torus(0.145, 0.03, (0.2, 0.3, 0.3), "em_orange", axis="x", seg=14, tseg=5)
    flange(m, (-0.7, -0.7, 0.3), 0.14, "y")
    flange(m, (0.7, 0.3, 0.3), 0.14, "x")
    for p in ((-0.7, -0.3), (-0.4, 0.3), (0.4, 0.3)):
        m.box((0.24, 0.24, 0.02), (p[0], p[1], 0.01), "steel")
        m.box((0.06, 0.06, 0.2), (p[0], p[1], 0.11), "steel")


# ================================================================ CAPACITOR (18)
@part("capacitor", "Capacitor Bank Rack")
def _(m, rng):
    m.box((1.1, 0.08, 0.6), (0, 0.04, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.06, 1.9, 0.06), (sx * 0.52, 0.99, sz * 0.27), "steel")
    for k in range(4):
        y = 0.08 + k * 0.5
        m.box((1.1, 0.04, 0.6), (0, y + 0.02 if k else 0.1, 0), "hull_mid")
        if k == 3:
            continue
        for j in range(4):
            m.cyl(0.11, 0.38, (-0.36 + j * 0.24, y + 0.25, 0.0), "paint_blue" if k % 2 else "paint_teal", seg=10)
            m.cyl(0.08, 0.04, (-0.36 + j * 0.24, y + 0.46, 0.0), "chrome", seg=8)
            m.cyl(0.03, 0.05, (-0.36 + j * 0.24, y + 0.49, 0.0), "copper", seg=6)
        m.box((1.0, 0.02, 0.02), (0, y + 0.45, -0.2), "copper")
    m.box((1.1, 0.24, 0.6), (0, 1.84, 0), "hull_dark", 0.01)
    leds(m, -0.4, 0.4, 1.84, 0.31, ["em_green"] * 4 + ["em_amber"] * 2)


@part("capacitor", "Fuel Cell Stack")
def _(m, rng):
    m.box((1.5, 0.12, 0.7), (0, 0.06, 0), "hull_dark", 0.01)
    for k in range(14):
        m.box((0.05, 0.6, 0.5), (-0.5 + k * 0.077, 0.5, 0), "plastic_white" if k % 2 else "paint_teal")
    for sx in (-1, 1):
        m.box((0.14, 0.7, 0.6), (sx * 0.62, 0.5, 0), "steel", 0.015)
    for sz in (-1, 1):
        for y in (0.28, 0.72):
            m.cyl(0.015, 1.4, (0, y, sz * 0.27), "chrome", axis="x", seg=5)
    m.cyl(0.05, 0.25, (-0.62, 0.95, 0), "copper", seg=6)
    m.cyl(0.05, 0.25, (0.62, 0.95, 0), "copper", seg=6)
    m.box((0.5, 0.3, 0.05), (0, 0.5, 0.29), "black_metal")
    m.box((0.4, 0.1, 0.03), (0, 0.5, 0.32), "em_green")
    pipe(m, (0.62, 0.15, 0.2), (0.9, 0.15, 0.2), 0.04, "gunmetal")


@part("capacitor", "Battery Rack")
def _(m, rng):
    for sx in (-1, 1):
        m.box((0.05, 1.7, 0.6), (sx * 0.6, 0.85, 0), "paint_grey")
    for k in range(4):
        y = 0.1 + k * 0.5
        m.box((1.2, 0.04, 0.6), (0, y, 0), "hull_mid")
        for j in range(3):
            m.box((0.34, 0.3, 0.5), (-0.38 + j * 0.38, y + 0.19, 0), "paint_navy", 0.01)
            m.box((0.3, 0.02, 0.15), (-0.38 + j * 0.38, y + 0.35, 0.1), "plastic_grey")
            m.cyl(0.02, 0.05, (-0.48 + j * 0.38, y + 0.36, -0.15), "copper", seg=5)
            m.cyl(0.02, 0.05, (-0.28 + j * 0.38, y + 0.36, -0.15), "chrome", seg=5)
            m.box((0.05, 0.03, 0.02), (-0.38 + j * 0.38, y + 0.12, 0.26), "em_green" if (j + k) % 3 else "em_amber")
    m.box((1.2, 0.05, 0.6), (0, 1.75, 0), "hull_dark", 0.01)
    hazard(m, -0.5, 0.5, 1.6, 1.68, 0.31, n=8)


@part("capacitor", "Energy Cell", "table")
def _(m, rng):
    m.cyl(0.07, 0.03, (0, 0.015, 0), "black_metal", seg=10)
    m.cyl(0.06, 0.24, (0, 0.15, 0), "glass_blue", seg=10)
    m.cyl(0.035, 0.24, (0, 0.15, 0), "em_cyan", seg=8)
    m.cyl(0.07, 0.04, (0, 0.29, 0), "chrome", seg=10)
    m.cyl(0.02, 0.03, (0, 0.325, 0), "copper", seg=6)
    for y in (0.06, 0.24):
        m.torus(0.062, 0.006, (0, y, 0), "steel", seg=10, tseg=4)


@part("capacitor", "Power Cell Pack", "table")
def _(m, rng):
    m.box((0.3, 0.16, 0.12), (0, 0.08, 0), "paint_orange", 0.01)
    m.box((0.32, 0.03, 0.14), (0, 0.17, 0), "black_metal", 0.005)
    m.box((0.16, 0.03, 0.03), (0, 0.205, 0), "rubber", 0.005)
    for x in (-0.09, 0.09):
        m.box((0.02, 0.05, 0.02), (x, 0.18, 0), "rubber")
    leds(m, -0.09, 0.09, 0.12, 0.062, ["em_green", "em_green", "em_green", "em_amber"], 0.018)
    hazard(m, -0.12, 0.12, 0.03, 0.06, 0.062, n=4)
    m.box((0.05, 0.05, 0.03), (0.16, 0.08, 0), "steel")


@part("capacitor", "Power Core")
def _(m, rng):
    m.cyl(0.5, 0.2, (0, 0.1, 0), "hull_dark", seg=16, r2=0.4, bevel=0.01)
    m.cyl(0.14, 0.25, (0, 0.3, 0), "gunmetal", seg=10)
    m.sphere(0.36, (0, 0.82, 0), "glass_blue", seg=16, ring=10)
    m.sphere(0.2, (0, 0.82, 0), "em_cyan", seg=10, ring=6)
    for k in range(3):
        a = 2 * PI * k / 3
        for t in (0, 1):
            m.torus(0.4, 0.02, (0, 0.82, 0), "chrome", axis="x", seg=14, tseg=4, rot=(0, a + t * PI / 2, PI * t * 0.25))
    m.cyl(0.3, 0.06, (0, 1.24, 0), "hull_dark", seg=12)
    m.cyl(0.12, 0.12, (0, 1.33, 0), "steel", seg=8)
    bolt_circle(m, 0, 0.2, 0, 0.36, 6)


@part("capacitor", "Supercapacitor Cluster")
def _(m, rng):
    m.cyl(0.62, 0.1, (0, 0.05, 0), "hull_dark", seg=12)
    m.cyl(0.62, 0.08, (0, 1.72, 0), "hull_dark", seg=12)
    pos = [(0, 0)] + [(0.36 * math.cos(2 * PI * k / 6), 0.36 * math.sin(2 * PI * k / 6)) for k in range(6)]
    for k, (x, z) in enumerate(pos):
        m.cyl(0.15, 1.55, (x, 0.9, z), "paint_teal" if k else "paint_navy", seg=10)
        m.cyl(0.155, 0.06, (x, 0.5, z), "hazard_yellow", seg=10)
        m.cyl(0.05, 0.08, (x, 1.8, z), "copper", seg=6)
    for k in range(6):
        a0, a1 = 2 * PI * k / 6, 2 * PI * (k + 1) / 6
        m.link((0.36 * math.cos(a0), 1.85, 0.36 * math.sin(a0)), (0.36 * math.cos(a1), 1.85, 0.36 * math.sin(a1)), 0.015, "copper")
    m.box((0.2, 0.3, 0.08), (0, 0.3, 0.7), "black_metal")
    m.box((0.14, 0.03, 0.02), (0, 0.36, 0.75), "em_green")


@part("capacitor", "Charging Cradle", "table")
def _(m, rng):
    m.box((0.5, 0.05, 0.32), (0, 0.025, 0), "hull_dark", 0.01)
    m.box((0.5, 0.14, 0.06), (0, 0.12, -0.13), "hull_mid", 0.01)
    for x in (-0.13, 0.13):
        m.box((0.04, 0.12, 0.2), (x - 0.09 * (1 if x > 0 else -1), 0.11, 0.02), "hull_mid")
    m.cyl(0.07, 0.34, (0, 0.24, 0.02), "glass_blue", seg=10, rot=(0.0, 0, 0))
    m.cyl(0.04, 0.34, (0, 0.24, 0.02), "em_cyan", seg=8)
    m.cyl(0.075, 0.03, (0, 0.42, 0.02), "chrome", seg=10)
    m.box((0.36, 0.03, 0.05), (0, 0.06, 0.13), "black_metal")
    leds(m, -0.12, 0.12, 0.06, 0.16, ["em_green", "em_amber", "em_green"], 0.03)
    m.cyl(0.015, 0.4, (0.15, 0.02, -0.22), "rubber", axis="x", seg=5)


@part("capacitor", "Wall Battery Cabinet", "wall")
def _(m, rng):
    m.box((0.9, 1.4, 0.3), (0, 0, 0.15), "paint_grey", 0.02)
    m.box((0.8, 1.3, 0.03), (0, 0, 0.31), "hull_mid", 0.005)
    m.screen((0.5, 0.25), (0, 0.4, 0.33), "power", bezel=0.012)
    for k in range(4):
        m.box((0.6, 0.04, 0.015), (0, 0.05 - k * 0.12, 0.33), "black_metal")
        m.box((0.05, 0.02, 0.02), (0.2, 0.05 - k * 0.12, 0.34), "em_green" if k != 2 else "em_amber")
    m.box((0.18, 0.05, 0.05), (0.25, -0.5, 0.34), "hazard_yellow")
    m.box((0.04, 0.2, 0.05), (0.36, 0.0, 0.34), "steel")
    bolts(m, [(-0.4, 0.65, 0.3), (0.4, 0.65, 0.3), (-0.4, -0.65, 0.3), (0.4, -0.65, 0.3)])


@part("capacitor", "Cell Charging Dock", "wall")
def _(m, rng):
    m.box((1.0, 0.7, 0.12), (0, 0, 0.06), "hull_dark", 0.015)
    for k in range(4):
        x = -0.36 + k * 0.24
        m.box((0.18, 0.5, 0.12), (x, 0.0, 0.16), "black_metal", 0.01)
        if k != 2:
            m.cyl(0.06, 0.4, (x, 0.02, 0.17), "glass_blue", seg=8)
            m.cyl(0.03, 0.4 * (0.4 + 0.2 * k), (x, -0.18 + 0.2 * (0.4 + 0.2 * k), 0.17), "em_cyan", seg=6)
        m.box((0.05, 0.03, 0.02), (x, -0.3, 0.23), "em_green" if k != 2 else "em_red")
    hazard(m, -0.45, 0.45, 0.28, 0.33, 0.13, n=8)


@part("capacitor", "High Voltage Capacitor")
def _(m, rng):
    m.box((0.8, 0.12, 0.8), (0, 0.06, 0), "hull_dark", 0.01)
    m.cyl(0.2, 0.4, (0, 0.32, 0), "paint_green", seg=12)
    for k in range(7):
        r = 0.2 - 0.008 * k
        m.cyl(r + 0.05, 0.06, (0, 0.6 + k * 0.1, 0), "ceramic", seg=12)
        m.cyl(0.1, 0.06, (0, 0.65 + k * 0.1, 0), "ceramic", seg=8)
    m.torus(0.22, 0.03, (0, 1.4, 0), "chrome", seg=14, tseg=5)
    m.sphere(0.1, (0, 1.5, 0), "chrome", seg=10, ring=6)
    m.link((0.14, 0.4, 0), (0.5, 0.15, 0), 0.02, "copper")
    m.box((0.14, 0.14, 0.06), (0, 0.32, 0.4), "black_metal")
    hazard(m, -0.35, 0.35, 0.16, 0.24, 0.41, n=6)


@part("capacitor", "Marx Bank")
def _(m, rng):
    m.box((0.9, 0.1, 0.5), (0, 0.05, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.cyl(0.03, 1.7, (sx * 0.38, 0.95, 0), "ceramic", seg=6)
    for k in range(6):
        y = 0.28 + k * 0.26
        m.box((0.6, 0.07, 0.3), (0, y, 0), "paint_navy" if k % 2 else "paint_blue", 0.01)
        m.cyl(0.045, 0.16, (-0.12 if k % 2 else 0.12, y + 0.11, 0), "chrome", seg=6)
        m.sphere(0.04, (-0.12 if k % 2 else 0.12, y + 0.2, 0), "chrome", seg=6, ring=4)
    m.torus(0.28, 0.03, (0, 1.85, 0), "chrome", seg=14, tseg=5)
    m.link((0, 1.75, 0), (0, 1.85, 0), 0.02, "chrome")
    pass


@part("capacitor", "Energy Cell Crate")
def _(m, rng):
    m.box((0.9, 0.5, 0.6), (0, 0.25, 0), "paint_orange", 0.02)
    m.box((0.94, 0.06, 0.64), (0, 0.5, 0), "hull_dark", 0.01)
    for j in range(3):
        for i in range(2):
            m.cyl(0.09, 0.02, (-0.27 + j * 0.27, 0.53, -0.12 + i * 0.24), "chrome", seg=8)
            m.cyl(0.05, 0.28, (-0.27 + j * 0.27, 0.66, -0.12 + i * 0.24), "em_cyan" if (i + j) % 2 else "em_blue", seg=8)
    for sx in (-1, 1):
        m.box((0.05, 0.16, 0.24), (sx * 0.47, 0.32, 0), "steel", 0.01)
    hazard(m, -0.3, 0.3, 0.1, 0.22, 0.31, n=6)
    m.box((0.2, 0.12, 0.02), (0, 0.38, 0.305), "plastic_white")
    m.cyl(0.03, 0.02, (0.2, 0.38, 0.31), "em_red", axis="z", seg=6)


@part("capacitor", "Battery Trolley")
def _(m, rng):
    m.box((1.1, 0.06, 0.6), (0, 0.22, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.09, 0.06, (sx * 0.45, 0.09, sz * 0.32), "rubber", axis="z", seg=10)
    for k in range(4):
        m.box((0.24, 0.45, 0.42), (-0.36 + k * 0.24, 0.49, 0), "paint_navy", 0.01)
        m.cyl(0.025, 0.05, (-0.36 + k * 0.24, 0.74, -0.1), "copper", seg=5)
        m.cyl(0.025, 0.05, (-0.36 + k * 0.24, 0.74, 0.1), "chrome", seg=5)
        m.box((0.05, 0.03, 0.02), (-0.36 + k * 0.24, 0.6, 0.215), "em_green")
    m.link((0.58, 0.26, -0.28), (0.72, 1.05, -0.28), 0.02, "steel")
    m.link((0.58, 0.26, 0.28), (0.72, 1.05, 0.28), 0.02, "steel")
    m.link((0.72, 1.05, -0.28), (0.72, 1.05, 0.28), 0.025, "rubber")
    pass


@part("capacitor", "Cell Tray", "table")
def _(m, rng):
    m.box((0.5, 0.03, 0.2), (0, 0.015, 0), "plastic_grey", 0.005)
    m.box((0.5, 0.05, 0.02), (0, 0.055, 0.09), "plastic_grey")
    m.box((0.5, 0.05, 0.02), (0, 0.055, -0.09), "plastic_grey")
    for k in range(6):
        x = -0.2 + k * 0.08
        m.cyl(0.028, 0.1, (x, 0.08, 0), "glass_blue" if k % 3 else "glass_green", seg=8)
        m.cyl(0.015, 0.09, (x, 0.08, 0), "em_cyan" if k % 3 else "em_green", seg=6)
        m.cyl(0.03, 0.015, (x, 0.135, 0), "chrome", seg=8)
    m.box((0.06, 0.06, 0.16), (0.27, 0.06, 0), "black_metal")


@part("capacitor", "Capacitor Wall Array", "wall")
def _(m, rng):
    m.box((1.2, 1.2, 0.05), (0, 0, 0.025), "hull_dark", 0.015)
    for j in range(3):
        for i in range(3):
            x, y = -0.38 + i * 0.38, -0.38 + j * 0.38
            m.cyl(0.13, 0.22, (x, y, 0.16), "gunmetal", axis="z", seg=10)
            m.cyl(0.1, 0.03, (x, y, 0.28), "em_cyan" if (i + j) % 2 else "em_amber", axis="z", seg=10)
            m.torus(0.13, 0.015, (x, y, 0.1), "copper", axis="z", seg=10, tseg=4)
    for j in range(3):
        m.link((-0.55, -0.38 + j * 0.38 - 0.2, 0.06), (0.55, -0.38 + j * 0.38 - 0.2, 0.06), 0.015, "copper")


@part("capacitor", "Fuel Cell Tower")
def _(m, rng):
    m.cyl(0.5, 0.15, (0, 0.075, 0), "hull_dark", seg=12, bevel=0.01)
    m.cyl(0.4, 2.1, (0, 1.2, 0), "paint_white", seg=14)
    for y in (0.35, 0.9, 1.55, 2.1):
        m.torus(0.41, 0.03, (0, y, 0), "steel", seg=14, tseg=4)
    m.box((0.14, 1.2, 0.03), (0, 1.25, 0.4), "glass_green")
    m.box((0.06, 0.9, 0.02), (0, 1.1, 0.41), "em_green")
    m.cyl(0.4, 0.15, (0, 2.32, 0), "hull_mid", seg=14, r2=0.15)
    m.cyl(0.12, 0.2, (0, 2.5, 0), "steel", seg=8)
    hazard(m, -0.3, 0.3, 0.2, 0.3, 0.385, n=6)
    pipe(m, (0.12, 2.6, 0), (0.4, 2.6, 0), 0.04, "copper")
    pipe(m, (0.4, 2.6, 0), (0.55, 0.4, 0), 0.04, "copper")


@part("capacitor", "Power Cell Locker")
def _(m, rng):
    cabinet(m, 0.9, 1.9, 0.5, "paint_green")
    m.box((0.02, 1.7, 0.02), (0, 0.95, 0.26), "black_metal")
    for sx in (-1, 1):
        m.box((0.42, 1.7, 0.02), (sx * 0.22, 0.95, 0.255), "hull_mid", 0.006)
        vents(m, sx * 0.22, 1.4, 0.27, 0.3, 5, 0.014, 0.035)
        m.box((0.03, 0.14, 0.03), (sx * 0.06, 0.95, 0.28), "chrome")
    hazard(m, -0.4, 0.4, 1.6, 1.72, 0.27, n=8)
    m.box((0.28, 0.14, 0.01), (0, 1.15, 0.27), "plastic_white")
    leds(m, -0.1, 0.1, 0.5, 0.27, ["em_green", "em_amber", "em_green"], 0.03)


# ================================================================ GENERATOR (12)
@part("generator", "Diesel Genset")
def _(m, rng):
    m.box((1.9, 0.14, 0.8), (0, 0.07, 0), "hazard_yellow", 0.01)
    m.box((1.0, 0.7, 0.6), (-0.3, 0.55, 0), "paint_orange", 0.03)
    for k in range(3):
        m.cyl(0.09, 0.14, (-0.55 + k * 0.25, 0.95, 0), "gunmetal", seg=8)
    m.cyl(0.28, 0.6, (0.6, 0.5, 0), "paint_grey", axis="x", seg=14)
    m.cyl(0.29, 0.06, (0.3, 0.5, 0), "steel", axis="x", seg=14)
    m.cyl(0.33, 0.35, (0.75, 0.5, 0), "hull_dark", axis="x", seg=12, r2=0.28)
    pass
    m.box((0.2, 0.6, 0.5), (-0.9, 0.55, 0), "hull_dark", 0.01)
    for k in range(6):
        pass
    m.cyl(0.05, 0.9, (-0.05, 1.3, -0.2), "gunmetal", seg=8)
    m.cyl(0.08, 0.08, (-0.05, 1.79, -0.2), "black_metal", seg=8, r2=0.06)
    m.link((-0.05, 1.0, -0.2), (-0.05, 1.3, -0.2), 0.05, "gunmetal")
    m.box((0.35, 0.45, 0.1), (0.6, 0.55, 0.42), "black_metal", 0.01)
    leds(m, 0.5, 0.7, 0.72, 0.48, ["em_green", "em_amber", "em_red"])
    gauge(m, (0.6, 0.5, 0.47), 0.06)
    m.torus(0.28, 0.012, (0.6, 0.5, 0), "chrome", axis="x", seg=12, tseg=4)


@part("generator", "Pad Transformer")
def _(m, rng):
    m.box((1.3, 0.12, 0.9), (0, 0.06, 0), "concrete", 0.01)
    m.box((1.0, 0.9, 0.6), (0, 0.57, 0), "paint_grey", 0.03)
    for sx in (-1, 1):
        for k in range(7):
            m.box((0.05, 0.75, 0.5), (sx * (0.52 + k * 0.05), 0.55, 0), "steel")
    for k in range(3):
        x = -0.28 + k * 0.28
        m.cyl(0.05, 0.1, (x, 1.07, 0), "black_metal", seg=8)
        for j in range(3):
            m.cyl(0.07 - 0.005 * j, 0.05, (x, 1.15 + j * 0.06, 0), "ceramic", seg=8)
        m.sphere(0.03, (x, 1.36, 0), "chrome", seg=6, ring=4)
    m.box((1.02, 0.06, 0.62), (0, 1.03, 0), "hull_dark", 0.01)
    hazard(m, -0.4, 0.4, 0.15, 0.27, 0.31, n=8)
    m.box((0.25, 0.18, 0.02), (0.25, 0.7, 0.31), "plastic_white")
    gauge(m, (-0.25, 0.7, 0.31), 0.07)


@part("generator", "Inverter Cabinet")
def _(m, rng):
    cabinet(m, 0.8, 1.9, 0.6, "paint_white")
    m.screen((0.45, 0.28), (0, 1.55, 0.31), "power", bezel=0.015)
    for k in range(2):
        m.cyl(0.14, 0.025, (0, 1.05 - k * 0.38, 0.3), "black_metal", axis="z", seg=12)
        m.torus(0.13, 0.008, (0, 1.05 - k * 0.38, 0.312), "chrome", axis="z", seg=10, tseg=3)
        for j in range(3):
            pass
        m.box((0.02, 0.26, 0.01), (0, 1.05 - k * 0.38, 0.32), "steel")
        m.box((0.26, 0.02, 0.01), (0, 1.05 - k * 0.38, 0.32), "steel")
    leds(m, -0.25, 0.25, 1.78, 0.31, led_pat(rng, 6), 0.03)
    vents(m, 0, 0.2, 0.305, 0.5, 5, 0.02, 0.04)
    m.box((0.1, 0.06, 0.04), (0.3, 0.7, 0.32), "paint_red")
    hazard(m, -0.35, -0.1, 0.1, 0.18, 0.305, n=3)


@part("generator", "Power Distribution Cabinet")
def _(m, rng):
    cabinet(m, 1.1, 2.0, 0.5, "paint_grey")
    for sx in (-1, 1):
        m.box((0.52, 1.8, 0.02), (sx * 0.27, 1.02, 0.26), "hull_light", 0.006)
        m.box((0.04, 0.24, 0.04), (sx * 0.06, 1.0, 0.29), "black_metal")
        m.box((0.24, 0.1, 0.005), (sx * 0.27, 1.6, 0.275), "plastic_white")
    for k in range(6):
        m.box((0.05, 0.05, 0.02), (-0.4 + k * 0.16, 1.85, 0.275), rng.choice(["em_green", "em_green", "em_amber", "em_red"]))
    hazard(m, -0.5, 0.5, 0.18, 0.3, 0.27, n=8)
    m.box((0.14, 0.14, 0.015), (-0.27, 1.25, 0.275), "hazard_yellow")
    m.box((0.14, 0.14, 0.015), (0.27, 1.25, 0.275), "hazard_yellow")
    m.box((0.06, 0.09, 0.016), (-0.27, 1.25, 0.285), "black_metal")
    m.box((0.06, 0.09, 0.016), (0.27, 1.25, 0.285), "black_metal")


@part("generator", "Gas Turbine Genset")
def _(m, rng):
    m.box((2.3, 0.16, 0.9), (0, 0.08, 0), "hull_dark", 0.01)
    for x in (-0.9, -0.3, 0.3, 0.9):
        m.box((0.1, 0.55, 0.7), (x, 0.44, 0), "gunmetal")
    m.cyl(0.34, 0.9, (-0.85, 0.85, 0), "steel", axis="x", seg=14, r2=0.42)
    m.cyl(0.42, 0.7, (-0.05, 0.85, 0), "paint_orange", axis="x", seg=14)
    m.cyl(0.36, 0.9, (0.65, 0.85, 0), "paint_grey", axis="x", seg=14, r2=0.3)
    m.cyl(0.2, 0.3, (1.25, 0.85, 0), "gunmetal", axis="x", seg=12, r2=0.28)
    m.cyl(0.22, 0.02, (-1.3, 0.85, 0), "black_metal", axis="x", seg=12)
    for k in range(5):
        pass
    for x in (-0.3, 0.1):
        m.torus(0.43, 0.02, (x, 0.85, 0), "chrome", axis="x", seg=14, tseg=4)
    m.box((0.6, 0.4, 0.25), (0.1, 1.28, -0.0), "hull_mid", 0.02)
    hazard(m, -0.6, 0.6, 0.18, 0.28, 0.46, n=10)
    leds(m, -0.05, 0.25, 1.28, 0.13, ["em_green", "em_green", "em_amber"])
    pipe(m, (1.1, 0.9, 0), (1.5, 1.6, 0), 0.06, "steel")
    m.cyl(0.1, 0.1, (1.5, 1.65, 0), "steel", seg=8)


@part("generator", "Fuel Processor")
def _(m, rng):
    base_plate(m, 1.4, 0.9, 0.1)
    m.cyl(0.38, 1.7, (-0.3, 0.98, 0), "steel", seg=14)
    m.sphere(0.38, (-0.3, 1.83, 0), "steel", seg=14, ring=6, scale=(1, 0.5, 1))
    for y in (0.5, 1.0, 1.5):
        m.torus(0.385, 0.02, (-0.3, y, 0), "black_metal", seg=14, tseg=4)
    m.cyl(0.2, 0.8, (0.4, 0.5, 0.15), "paint_green", axis="y", seg=10)
    m.cyl(0.2, 0.8, (0.4, 0.5, -0.2), "paint_teal", seg=10)
    m.box((0.2, 0.5, 0.3), (0.6, 1.1, 0), "hull_mid", 0.01)
    pipe(m, (-0.3, 2.0, 0), (-0.3, 2.3, 0), 0.05)
    pipe(m, (-0.3, 2.3, 0), (0.6, 2.3, 0), 0.05)
    pipe(m, (0.6, 2.3, 0), (0.6, 1.35, 0), 0.05)
    pipe(m, (0.08, 0.5, 0.15), (-0.3, 0.5, 0.15), 0.035)
    gauge(m, (-0.3, 1.2, 0.38), 0.07)
    wheel(m, (0.15, 2.3, 0.08), 0.08, 2, "paint_red")
    m.cyl(0.14, 0.06, (-0.3, 2.08, 0), "hull_dark", seg=10)


@part("generator", "Rectifier Cabinet")
def _(m, rng):
    cabinet(m, 0.9, 1.8, 0.55, "hull_mid")
    for k in range(3):
        m.box((0.7, 0.32, 0.1), (0, 1.35 - k * 0.42, 0.32), "black_metal", 0.01)
        for j in range(10):
            m.box((0.012, 0.28, 0.08), (-0.32 + j * 0.07, 1.35 - k * 0.42, 0.38), "brushed_alu")
    pass
    for x in (-0.25, 0.25):
        gauge(m, (x, 1.7, 0.28), 0.07)
    leds(m, -0.3, 0.3, 0.2, 0.28, ["em_green", "em_red", "em_amber", "em_green"], 0.03)
    m.cyl(0.04, 0.3, (0.0, 1.96, 0), "copper", seg=6)
    pass


@part("generator", "Wall Transformer", "wall")
def _(m, rng):
    m.box((0.9, 1.0, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    m.box((0.6, 0.6, 0.3), (0, -0.08, 0.2), "paint_grey", 0.02)
    for k in range(9):
        m.box((0.02, 0.5, 0.2), (-0.33 - k * 0.0 + (k - 4) * 0.07, -0.08, 0.36), "steel")
    for k in range(3):
        m.cyl(0.035, 0.12, (-0.18 + k * 0.18, 0.28, 0.2), "ceramic", seg=8)
        m.sphere(0.03, (-0.18 + k * 0.18, 0.36, 0.2), "copper", seg=6, ring=4)
    m.box((0.2, 0.1, 0.02), (0, -0.42, 0.36), "hazard_yellow")
    pass
    m.box((0.05, 0.05, 0.02), (0.28, -0.42, 0.36), "em_green")


@part("generator", "Micro Fusion Generator")
def _(m, rng):
    base_plate(m, 1.1, 1.1, 0.1)
    m.box((0.9, 0.9, 0.9), (0, 0.55, 0), "paint_teal", 0.03)
    m.box((0.5, 0.5, 0.05), (0, 0.6, 0.45), "black_metal", 0.01)
    m.box((0.42, 0.42, 0.02), (0, 0.6, 0.47), "glass_dark")
    m.sphere(0.13, (0, 0.6, 0.4), "em_orange", seg=10, ring=6)
    for a in (0.0, PI / 2):
        m.torus(0.18, 0.02, (0, 0.6, 0.42), "copper", axis="z", seg=10, tseg=4, rot=(a * 0.5, a, 0))
    m.torus(0.19, 0.02, (0, 0.6, 0.47), "brass", axis="z", seg=12, tseg=4)
    m.cyl(0.25, 0.15, (0, 1.08, 0), "hull_dark", seg=12)
    m.cyl(0.15, 0.22, (0, 1.25, 0), "steel", seg=10)
    hazard(m, -0.4, 0.4, 0.12, 0.22, 0.46, n=8)
    leds(m, -0.3, 0.3, 0.95, 0.46, ["em_green", "em_green", "em_amber"], 0.03)
    for sx in (-1, 1):
        pass


@part("generator", "Motor Generator Set")
def _(m, rng):
    m.box((2.0, 0.12, 0.8), (0, 0.06, 0), "hull_dark", 0.01)
    m.cyl(0.32, 0.7, (-0.65, 0.5, 0), "paint_blue", axis="x", seg=14)
    m.cyl(0.32, 0.7, (0.65, 0.5, 0), "paint_orange", axis="x", seg=14)
    for x in (-0.65, 0.65):
        for k in range(5):
            pass
        m.box((0.7, 0.05, 0.3), (x, 0.84, 0), "hull_mid")
        m.box((0.3, 0.14, 0.26), (x, 0.9, 0), "black_metal", 0.01)
        m.box((0.6, 0.12, 0.6), (x, 0.18, 0), "gunmetal")
    m.cyl(0.05, 0.6, (0, 0.5, 0), "chrome", axis="x", seg=8)
    m.cyl(0.13, 0.22, (0, 0.5, 0), "hazard_yellow", axis="x", seg=10)
    pass
    m.cyl(0.32, 0.05, (-0.3, 0.5, 0), "steel", axis="x", seg=14)
    m.cyl(0.32, 0.05, (0.3, 0.5, 0), "steel", axis="x", seg=14)
    pass
    pass
    pass
    gauge(m, (-0.65, 0.5, 0.32), 0.06)
    gauge(m, (0.65, 0.5, 0.32), 0.06)


@part("generator", "Regulator Tower")
def _(m, rng):
    m.cyl(0.4, 0.14, (0, 0.07, 0), "hull_dark", seg=12)
    m.cyl(0.22, 2.0, (0, 1.14, 0), "gunmetal", seg=10)
    for k in range(9):
        m.cyl(0.42 - 0.02 * abs(k - 4), 0.03, (0, 0.4 + k * 0.2, 0), "brushed_alu", seg=12)
    m.cyl(0.3, 0.14, (0, 2.24, 0), "hull_mid", seg=12)
    m.sphere(0.14, (0, 2.38, 0), "em_amber", seg=8, ring=5)
    m.box((0.2, 0.3, 0.08), (0, 0.28, 0.34), "black_metal")
    m.box((0.14, 0.03, 0.02), (0, 0.32, 0.39), "em_green")
    hazard_ring(m, 0, 0.14, 0, 0.4, 0.1, n=12)


@part("generator", "Wall Substation", "wall")
def _(m, rng):
    m.box((1.6, 1.3, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    for k in range(3):
        x = -0.5 + k * 0.5
        m.box((0.36, 0.5, 0.2), (x, -0.25, 0.15), "paint_grey", 0.015)
        for s in (-1, 0, 1):
            m.cyl(0.025, 0.14, (x + s * 0.11, 0.06, 0.15), "ceramic", seg=6)
            m.link((x + s * 0.11, 0.13, 0.15), (x + s * 0.11, 0.5, 0.08), 0.014, "copper")
        m.box((0.04, 0.05, 0.02), (x, -0.45, 0.26), "em_green" if k != 1 else "em_amber")
    for s in (-1, 0, 1):
        pass
    for j, y in enumerate((0.5, 0.56, 0.62)):
        m.box((1.5, 0.03, 0.03), (0, y, 0.08), ["copper", "brass", "copper"][j])
    hazard(m, -0.75, 0.75, -0.62, -0.54, 0.06, n=12)


# ================================================================ TANK (18)
def _saddles(m, xs, r, y0=0.0, w=0.5):
    for x in xs:
        m.box((0.1, r * 0.9, w), (x, y0 + r * 0.45, 0), "hull_dark", 0.01)
    m.box((abs(xs[-1] - xs[0]) + 0.3, 0.06, w + 0.1), ((xs[0] + xs[-1]) / 2, y0 + 0.03, 0), "black_metal")


@part("tank", "Vertical Coolant Tank")
def _(m, rng):
    m.cyl(0.8, 0.1, (0, 0.05, 0), "hull_dark", seg=14)
    m.cyl(0.72, 1.9, (0, 1.05, 0), "paint_teal", seg=16)
    m.sphere(0.72, (0, 2.0, 0), "paint_teal", seg=16, ring=6, scale=(1, 0.3, 1))
    for y in (0.5, 1.05, 1.6):
        m.torus(0.73, 0.02, (0, y, 0), "steel", seg=16, tseg=4)
    ladder(m, -0.3, 0.75, 0.1, 2.1, 0.4)
    gauge_glass_tube(m, 0.5, 0.4, 1.7, 0.55, 0.6, "em_cyan")
    m.cyl(0.12, 0.15, (0.3, 2.2, 0.2), "steel", seg=8)
    flange(m, (0, 0.3, 0.72), 0.08, "z")
    hazard(m, 0.1, 0.5, 0.15, 0.25, 0.72, n=4)
    pipe(m, (0.3, 2.3, 0.2), (0.3, 2.5, 0.2), 0.04)


@part("tank", "Horizontal Fuel Tank")
def _(m, rng):
    _saddles(m, (-0.7, 0.7), 0.7, 0, 0.6)
    m.cyl(0.5, 1.9, (0, 0.85, 0), "paint_orange", axis="x", seg=16)
    m.sphere(0.5, (-0.95, 0.85, 0), "paint_orange", seg=14, ring=7, scale=(0.4, 1, 1))
    m.sphere(0.5, (0.95, 0.85, 0), "paint_orange", seg=14, ring=7, scale=(0.4, 1, 1))
    for x in (-0.3, 0.3):
        m.torus(0.51, 0.02, (x, 0.85, 0), "steel", axis="x", seg=16, tseg=4)
    m.cyl(0.15, 0.1, (0, 1.4, 0), "steel", seg=10)
    m.cyl(0.19, 0.03, (0, 1.46, 0), "hull_dark", seg=10)
    pass
    m.cyl(0.05, 0.12, (-0.5, 1.38, 0), "brass", seg=6)
    gauge(m, (0.0, 0.85, 0.5), 0.07)
    pass
    m.box((0.5, 0.14, 0.02), (0.55, 0.85, 0.5), "hazard_yellow")


@part("tank", "Shell and Tube Heat Exchanger")
def _(m, rng):
    _saddles(m, (-0.8, 0.8), 0.5, 0, 0.5)
    m.cyl(0.32, 2.0, (0, 0.72, 0), "steel", axis="x", seg=14)
    m.cyl(0.4, 0.5, (-1.25, 0.72, 0), "paint_blue", axis="x", seg=14)
    m.cyl(0.4, 0.4, (1.2, 0.72, 0), "paint_blue", axis="x", seg=14)
    flange(m, (-1.0, 0.72, 0), 0.28, "x", 0.05)
    flange(m, (1.0, 0.72, 0), 0.28, "x", 0.05)
    m.sphere(0.4, (-1.5, 0.72, 0), "paint_blue", seg=12, ring=6, scale=(0.3, 1, 1))
    m.sphere(0.4, (1.4, 0.72, 0), "paint_blue", seg=12, ring=6, scale=(0.3, 1, 1))
    for x, mt in ((-0.5, "copper"), (0.5, "gunmetal")):
        m.cyl(0.07, 0.4, (x, 1.2, 0), "steel", seg=8)
        flange(m, (x, 1.42, 0), 0.07, "y")
    for x in (-1.25, 1.2):
        m.cyl(0.06, 0.3, (x, 1.15, 0.0), "gunmetal", seg=8)
        m.cyl(0.09, 0.03, (x, 1.32, 0), "steel", seg=8)
    gauge(m, (0.0, 0.85, 0.32), 0.05)
    m.box((0.3, 0.1, 0.02), (0.5, 0.6, 0.32), "hazard_yellow")


@part("tank", "Circulation Pump")
def _(m, rng):
    base_plate(m, 1.3, 0.6, 0.1)
    m.cyl(0.22, 0.6, (-0.25, 0.4, 0), "paint_blue", axis="x", seg=12)
    for k in range(5):
        m.box((0.02, 0.42, 0.42), (-0.45 + k * 0.08, 0.4, 0), "steel")
    m.cyl(0.1, 0.1, (-0.6, 0.4, 0), "hull_dark", axis="x", seg=10)
    m.cyl(0.24, 0.2, (0.08, 0.4, 0), "gunmetal", axis="x", seg=12)
    m.cyl(0.34, 0.24, (0.35, 0.4, 0), "hull_mid", axis="x", seg=16)
    m.cyl(0.26, 0.05, (0.48, 0.4, 0), "steel", axis="x", seg=12)
    flange(m, (0.35, 0.95, 0), 0.09, "y")
    m.cyl(0.09, 0.4, (0.35, 0.75, 0), "hull_mid", seg=10)
    pass
    m.cyl(0.09, 0.4, (0.6, 0.4, 0), "hull_mid", axis="x", seg=10)
    flange(m, (0.8, 0.4, 0.0), 0.09, "x")
    m.box((0.14, 0.1, 0.12), (-0.25, 0.7, 0.0), "black_metal", 0.01)
    pass
    m.box((0.05, 0.03, 0.02), (-0.25, 0.7, 0.07), "em_green")


@part("tank", "Spherical Pressure Vessel")
def _(m, rng):
    m.sphere(0.85, (0, 1.35, 0), "paint_white", seg=18, ring=10)
    for k in range(4):
        a = PI / 2 * k + PI / 4
        m.link((0.55 * math.cos(a), 0.2, 0.55 * math.sin(a)), (0.6 * math.cos(a), 1.05, 0.6 * math.sin(a)), 0.05, "steel")
        m.box((0.2, 0.05, 0.2), (0.6 * math.cos(a), 0.025, 0.6 * math.sin(a)), "hull_dark")
    m.torus(0.86, 0.02, (0, 1.35, 0), "black_metal", seg=18, tseg=4)
    m.cyl(0.14, 0.2, (0, 2.25, 0), "steel", seg=10)
    flange(m, (0, 2.35, 0), 0.14, "y")
    pass
    ladder(m, 0.0, 0.88, 0.1, 1.9, 0.36)
    pass
    gauge(m, (0.4, 1.0, 0.76), 0.06)


@part("tank", "Radiator Panel", "wall")
def _(m, rng):
    m.box((1.2, 0.1, 0.08), (0, 0.9, 0.06), "steel")
    m.box((1.2, 0.1, 0.08), (0, -0.9, 0.06), "steel")
    for k in range(9):
        m.box((0.06, 1.7, 0.05), (-0.5 + k * 0.125, 0, 0.08), "paint_white")
        m.box((0.16, 1.6, 0.012), (-0.5 + k * 0.125, 0, 0.1), "brushed_alu")
    m.cyl(0.04, 0.3, (0.7, 0.9, 0.06), "copper", axis="x", seg=6)
    m.cyl(0.04, 0.3, (0.7, -0.9, 0.06), "copper", axis="x", seg=6)
    m.box((0.06, 2.0, 0.03), (-0.68, 0, 0.02), "hull_dark")
    m.box((0.06, 2.0, 0.03), (0.68, 0, 0.02), "hull_dark")
    m.box((0.1, 0.1, 0.12), (0.0, 1.0, 0.06), "black_metal")
    m.box((0.05, 0.03, 0.02), (0.0, 1.0, 0.13), "em_amber")


@part("tank", "Filtration Unit")
def _(m, rng):
    m.box((1.4, 0.12, 0.7), (0, 0.06, 0), "hull_dark", 0.01)
    for k in range(3):
        x = -0.45 + k * 0.45
        m.cyl(0.17, 1.1, (x, 0.7, 0), "paint_grey" if k != 1 else "paint_teal", seg=12)
        m.cyl(0.19, 0.06, (x, 1.28, 0), "steel", seg=12)
        m.cyl(0.19, 0.06, (x, 0.18, 0), "steel", seg=12)
        m.box((0.16, 0.5, 0.02), (x, 0.75, 0.17), "glass_blue")
    m.cyl(0.06, 1.45, (0, 1.55, -0.2), "gunmetal", axis="x", seg=8)
    for k in range(3):
        x = -0.45 + k * 0.45
        m.link((x, 1.31, 0), (x, 1.55, -0.2), 0.035, "gunmetal")
    pass
    m.box((0.28, 0.2, 0.08), (0.5, 0.3, 0.36), "black_metal", 0.01)
    pass
    leds(m, 0.4, 0.6, 0.3, 0.41, ["em_green", "em_amber"], 0.03)
    flange(m, (-0.78, 1.55, -0.2), 0.06, "x")


@part("tank", "Condenser")
def _(m, rng):
    base_plate(m, 1.0, 1.0, 0.1)
    m.cyl(0.4, 1.8, (0, 1.0, 0), "steel", seg=14)
    m.sphere(0.4, (0, 1.9, 0), "steel", seg=14, ring=6, scale=(1, 0.5, 1))
    pass
    pass
    for y in (0.3, 1.0, 1.7):
        flange(m, (0, y, 0), 0.31, "y", 0.05)
    tube_pts = [(0.4, 0.5, 0.1), (0.7, 0.5, 0.1), (0.7, 0.9, 0.1), (0.4, 0.9, 0.1)]
    m.tube(tube_pts, 0.04, "copper", seg=6)
    tube_pts = [(0.4, 1.3, -0.1), (0.7, 1.3, -0.1), (0.7, 1.7, -0.1), (0.4, 1.7, -0.1)]
    m.tube(tube_pts, 0.04, "copper", seg=6)
    m.cyl(0.08, 0.3, (0, 2.25, 0), "gunmetal", seg=8)
    m.cyl(0.1, 0.04, (0, 2.42, 0), "steel", seg=8)
    gauge(m, (-0.2, 1.0, 0.38), 0.07)
    m.cyl(0.07, 0.3, (-0.5, 0.25, 0), "gunmetal", axis="x", seg=8)
    em_band(m, 0, 1.4, 0, 0.4, 0.08, "em_cyan", 14)


@part("tank", "Deuterium Bottle Rack")
def _(m, rng):
    m.box((1.5, 0.08, 0.55), (0, 0.04, 0), "hull_dark", 0.01)
    for k in range(4):
        x = -0.55 + k * 0.37
        m.cyl(0.13, 1.35, (x, 0.78, 0), "paint_white", seg=10)
        m.sphere(0.13, (x, 1.46, 0), "paint_white", seg=10, ring=5, scale=(1, 0.7, 1))
        pass
        m.cyl(0.14, 0.12, (x, 0.9, 0), "hazard_yellow", seg=10)
        m.cyl(0.03, 0.12, (x, 1.62, 0), "brass", seg=6)
        pass
        m.box((0.1, 0.02, 0.05), (x, 1.7, 0), "paint_red")
    m.box((1.5, 0.06, 0.05), (0, 0.5, 0.2), "steel")
    m.box((1.5, 0.06, 0.05), (0, 1.15, 0.2), "steel")
    for sx in (-1, 1):
        m.box((0.05, 1.3, 0.05), (sx * 0.72, 0.7, 0.2), "steel")
        m.box((0.05, 1.3, 0.05), (sx * 0.72, 0.7, -0.2), "steel")
    m.box((1.5, 0.06, 0.05), (0, 1.15, -0.2), "steel")
    m.box((0.3, 0.12, 0.01), (0, 0.3, 0.28), "plastic_white")


@part("tank", "Accumulator Tank")
def _(m, rng):
    m.cyl(0.4, 0.08, (0, 0.04, 0), "hull_dark", seg=12)
    for k in range(3):
        a = 2 * PI * k / 3
        m.link((0.3 * math.cos(a), 0.08, 0.3 * math.sin(a)), (0.3 * math.cos(a), 0.4, 0.3 * math.sin(a)), 0.03, "steel")
    m.cyl(0.32, 1.0, (0, 0.9, 0), "paint_red", seg=14)
    m.sphere(0.32, (0, 1.4, 0), "paint_red", seg=14, ring=6, scale=(1, 0.5, 1))
    m.sphere(0.32, (0, 0.4, 0), "paint_red", seg=14, ring=6, scale=(1, 0.5, 1))
    m.cyl(0.06, 0.16, (0, 1.65, 0), "steel", seg=8)
    gauge(m, (0, 1.0, 0.31), 0.07)
    m.cyl(0.05, 0.3, (0.32, 0.6, 0), "gunmetal", axis="x", seg=8)
    flange(m, (0.48, 0.6, 0), 0.05, "x")
    m.torus(0.325, 0.02, (0, 0.9, 0), "steel", seg=14, tseg=4)


@part("tank", "Deuterium Bottle")
def _(m, rng):
    m.cyl(0.16, 0.05, (0, 0.025, 0), "black_metal", seg=10)
    m.cyl(0.14, 1.35, (0, 0.72, 0), "paint_teal", seg=12)
    m.sphere(0.14, (0, 1.4, 0), "paint_teal", seg=12, ring=6, scale=(1, 0.75, 1))
    m.cyl(0.145, 0.16, (0, 1.0, 0), "hazard_yellow", seg=12)
    m.cyl(0.145, 0.04, (0, 0.5, 0), "paint_white", seg=12)
    m.cyl(0.05, 0.14, (0, 1.6, 0), "brass", seg=8)
    m.torus(0.1, 0.012, (0, 1.65, 0), "steel", seg=10, tseg=4)
    m.box((0.14, 0.03, 0.03), (0, 1.68, 0), "paint_red")
    m.cyl(0.03, 0.1, (0.07, 1.62, 0), "chrome", axis="x", seg=6)
    pass
    m.box((0.1, 0.16, 0.005), (0, 0.75, 0.145), "plastic_white")


@part("tank", "Expansion Tank", "wall")
def _(m, rng):
    for y in (-0.22, 0.22):
        pass
    for x in (-0.42, 0.42):
        m.box((0.1, 0.62, 0.05), (x, 0, 0.025), "hull_dark")
        m.box((0.1, 0.06, 0.26), (x, -0.16, 0.13), "steel")
        m.box((0.1, 0.06, 0.26), (x, 0.16, 0.13), "steel")
    m.cyl(0.24, 1.1, (0, 0, 0.28), "paint_blue", axis="x", seg=14)
    m.sphere(0.24, (-0.55, 0, 0.28), "paint_blue", seg=12, ring=6, scale=(0.4, 1, 1))
    m.sphere(0.24, (0.55, 0, 0.28), "paint_blue", seg=12, ring=6, scale=(0.4, 1, 1))
    m.cyl(0.05, 0.14, (0, 0.28, 0.28), "steel", seg=8)
    gauge(m, (0.0, 0.0, 0.52), 0.06)
    m.cyl(0.04, 0.2, (-0.3, -0.26, 0.28), "gunmetal", seg=6)
    m.torus(0.245, 0.015, (0.2, 0, 0.28), "steel", axis="x", seg=14, tseg=4)


@part("tank", "Sump Tank")
def _(m, rng):
    m.box((1.4, 0.7, 0.8), (0, 0.45, 0), "paint_grey", 0.03)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.08, 0.1, 0.08), (sx * 0.6, 0.05, sz * 0.32), "black_metal")
    pass
    m.box((0.6, 0.06, 0.4), (-0.25, 0.83, 0), "hull_mid", 0.01)
    m.cyl(0.06, 0.03, (-0.25, 0.88, 0.0), "steel", seg=8)
    pass
    m.box((0.24, 0.3, 0.02), (0.4, 0.55, 0.41), "glass_blue")
    m.box((0.16, 0.2, 0.01), (0.4, 0.5, 0.42), "em_cyan")
    m.box((0.5, 0.14, 0.02), (-0.3, 0.5, 0.41), "hazard_yellow")
    pass
    m.cyl(0.05, 0.25, (0.8, 0.5, 0.0), "gunmetal", axis="x", seg=8)
    flange(m, (0.94, 0.5, 0.0), 0.05, "x")
    for k in range(3):
        m.box((0.04, 0.6, 0.01), (-0.6 + k * 0.6, 0.45, 0.405), "steel")


@part("tank", "Buffer Tank with Level Tube")
def _(m, rng):
    m.cyl(0.5, 0.06, (0, 0.03, 0), "black_metal", seg=12)
    m.cyl(0.42, 1.5, (0, 0.81, 0), "paint_navy", seg=14, r2=0.42)
    m.sphere(0.42, (0, 1.56, 0), "paint_navy", seg=14, ring=6, scale=(1, 0.4, 1))
    m.box((0.12, 0.1, 0.06), (0.46, 0.35, 0), "steel")
    m.box((0.12, 0.1, 0.06), (0.46, 1.25, 0), "steel")
    gauge_glass_tube(m, 0.55, 0.35, 1.25, 0.0, 0.55, "em_blue")
    m.link((0.42, 0.35, 0), (0.55, 0.35, 0), 0.025, "steel")
    m.link((0.42, 1.25, 0), (0.55, 1.25, 0), 0.025, "steel")
    m.cyl(0.12, 0.1, (0, 1.85, 0), "steel", seg=10)
    pass
    for y in (0.5, 1.1):
        m.torus(0.425, 0.02, (0, y, 0), "steel", seg=14, tseg=4)
    hazard(m, -0.2, 0.2, 0.15, 0.25, 0.42, n=4)


@part("tank", "Cryo Dewar")
def _(m, rng):
    m.cyl(0.5, 0.08, (0, 0.04, 0), "hull_dark", seg=12)
    m.cyl(0.42, 1.3, (0, 0.73, 0), "paint_white", seg=14, bevel=0.0)
    m.sphere(0.42, (0, 1.38, 0), "paint_white", seg=14, ring=7, scale=(1, 0.7, 1))
    m.cyl(0.43, 0.08, (0, 0.3, 0), "steel", seg=14)
    m.cyl(0.1, 0.12, (0, 1.72, 0), "steel", seg=8)
    m.sphere(0.13, (0, 1.85, 0), "chrome", seg=8, ring=5)
    m.cyl(0.05, 0.3, (0.3, 1.5, 0), "chrome", seg=6, rot=(0, 0, -0.9))
    for a in (0.7, 2.6, 4.5):
        pass
    m.box((0.2, 0.28, 0.02), (0, 0.8, 0.42), "glass_blue")
    m.box((0.14, 0.2, 0.01), (0, 0.8, 0.43), "em_cyan")
    m.box((0.3, 0.06, 0.02), (0, 0.5, 0.42), "paint_blue")
    for a in (0.5, 2.6, 4.7):
        pass


@part("tank", "Piston Pump Skid")
def _(m, rng):
    m.box((1.1, 0.1, 0.6), (0, 0.05, 0), "hazard_yellow", 0.01)
    m.box((0.6, 0.35, 0.4), (0.0, 0.3, 0), "paint_orange", 0.02)
    for k in range(3):
        x = -0.2 + k * 0.2
        m.cyl(0.07, 0.35, (x, 0.65, 0), "steel", seg=8)
        m.cyl(0.09, 0.04, (x, 0.83, 0), "hull_dark", seg=8)
        m.cyl(0.02, 0.2, (x, 0.95, 0), "chrome", seg=5)
    m.cyl(0.22, 0.25, (-0.6, 0.3, 0), "paint_blue", axis="x", seg=12)
    m.cyl(0.05, 0.1, (-0.35, 0.3, 0), "chrome", axis="x", seg=8)
    pipe(m, (0.3, 0.55, 0.0), (0.55, 0.55, 0.0), 0.04, "gunmetal")
    pipe(m, (0.55, 0.55, 0.0), (0.55, 0.25, 0.0), 0.04, "gunmetal")
    m.box((0.15, 0.1, 0.04), (0.4, 0.3, 0.22), "black_metal")
    m.box((0.04, 0.03, 0.02), (0.4, 0.3, 0.25), "em_green")
    gauge(m, (-0.05, 0.4, 0.21), 0.05)


@part("tank", "Radiator Coil", "wall")
def _(m, rng):
    m.box((1.2, 1.4, 0.03), (0, 0, 0.015), "hull_dark")
    ys = [-0.5 + k * 0.2 for k in range(6)]
    pts = []
    for k, y in enumerate(ys):
        xs = (-0.45, 0.45) if k % 2 == 0 else (0.45, -0.45)
        pts += [(xs[0], y, 0.12), (xs[1], y, 0.12)]
    m.tube(pts, 0.04, "copper", seg=6)
    for p in ys:
        for x in (-0.3, 0.0, 0.3):
            pass
    for k in range(7):
        m.box((0.03, 1.0, 0.16), (-0.36 + k * 0.12, -0.0, 0.1), "brushed_alu")
    pass
    for x in (-0.55, 0.55):
        m.box((0.06, 1.2, 0.06), (x, 0.0, 0.06), "steel")
    pass
    m.box((0.1, 0.06, 0.06), (0.0, 0.62, 0.1), "black_metal")
    m.box((0.05, 0.03, 0.02), (0.0, 0.62, 0.14), "em_amber")


@part("tank", "Tote Tank")
def _(m, rng):
    m.box((1.0, 0.12, 1.0), (0, 0.06, 0), "black_metal", 0.01)
    m.box((0.9, 0.9, 0.9), (0, 0.6, 0), "plastic_white", 0.03)
    m.box((0.8, 0.7, 0.8), (0, 0.6, 0), "glass_green", 0.0)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.05, 1.0, 0.05), (sx * 0.47, 0.6, sz * 0.47), "steel")
    for y in (0.15, 0.6, 1.08):
        for sx in (-1, 1):
            m.box((0.05, 0.04, 0.94), (sx * 0.47, y, 0), "steel")
            m.box((0.94, 0.04, 0.05), (0, y, sx * 0.47), "steel")
    m.cyl(0.1, 0.05, (0.0, 1.13, 0.0), "paint_orange", seg=8)
    m.cyl(0.06, 0.15, (0.2, 0.2, 0.55), "brass", axis="z", seg=8)
    m.box((0.1, 0.03, 0.03), (0.2, 0.3, 0.6), "paint_red")
    pass
    pass
    m.box((0.3, 0.2, 0.01), (-0.15, 0.55, 0.46), "hazard_yellow")


# ================================================================ TURBINE (6)
@part("turbine", "Steam Turbine")
def _(m, rng):
    m.box((2.4, 0.12, 0.9), (0, 0.06, 0), "hull_dark", 0.01)
    for x in (-0.9, 0.0, 0.9):
        m.box((0.16, 0.55, 0.7), (x, 0.4, 0), "gunmetal")
    for k, (x, r) in enumerate([(-0.85, 0.28), (-0.4, 0.4), (0.05, 0.5), (0.55, 0.42), (0.95, 0.3)]):
        m.cyl(r, 0.42, (x, 0.85, 0), "paint_grey" if k % 2 else "hull_mid", axis="x", seg=14)
        m.torus(r, 0.02, (x + 0.22, 0.85, 0), "steel", axis="x", seg=14, tseg=4)
    m.cyl(0.08, 0.5, (-1.3, 0.85, 0), "chrome", axis="x", seg=8)
    m.cyl(0.14, 0.08, (-1.06, 0.85, 0), "steel", axis="x", seg=10)
    pass
    pipe(m, (0.05, 1.35, 0), (0.05, 1.8, 0), 0.1, "steel")
    flange(m, (0.05, 1.8, 0), 0.1, "y")
    pipe(m, (1.1, 0.7, 0), (1.35, 0.5, 0), 0.1, "steel")
    gauge(m, (-0.4, 0.85, 0.4), 0.06)
    m.box((0.5, 0.14, 0.02), (0.05, 0.85, 0.5), "hazard_yellow")


@part("turbine", "Axial Compressor")
def _(m, rng):
    m.box((2.0, 0.1, 0.8), (0, 0.05, 0), "hull_dark", 0.01)
    for x in (-0.6, 0.6):
        m.box((0.12, 0.5, 0.6), (x, 0.35, 0), "gunmetal")
    m.cyl(0.55, 1.5, (0, 0.85, 0), "steel", axis="x", seg=16, r2=0.32)
    for k in range(5):
        x = -0.7 + k * 0.3
        m.torus(0.55 - 0.045 * k, 0.03, (x, 0.85, 0), "brushed_alu", axis="x", seg=14, tseg=4)
    m.cyl(0.4, 0.4, (-0.95, 0.85, 0), "black_metal", axis="x", seg=12, r2=0.55)
    m.cyl(0.14, 0.14, (-1.2, 0.85, 0), "chrome", axis="x", seg=8)
    pass
    m.cyl(0.36, 0.3, (0.9, 0.85, 0), "hull_mid", axis="x", seg=12, r2=0.28)
    pipe(m, (0.7, 0.85, 0.25), (0.7, 1.4, 0.3), 0.06)
    pipe(m, (0.7, 1.4, 0.3), (0.2, 1.4, 0.3), 0.06)
    pass
    hazard(m, -0.3, 0.3, 0.15, 0.25, 0.41, n=6)
    leds(m, -0.1, 0.1, 0.4, 0.41, ["em_green", "em_amber"], 0.03)


@part("turbine", "Flywheel")
def _(m, rng):
    m.box((1.5, 0.12, 0.6), (0, 0.06, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        pass
        m.box((0.1, 1.5, 0.35), (sx * 0.55, 0.85, 0), "hull_dark", 0.01)
    m.cyl(0.65, 0.22, (0, 1.0, 0), "steel", axis="z", seg=20, bevel=0.01)
    m.torus(0.6, 0.06, (0, 1.0, 0), "gunmetal", axis="z", seg=20, tseg=5)
    m.cyl(0.2, 0.3, (0, 1.0, 0), "chrome", axis="z", seg=10)
    for k in range(4):
        m.box((0.9, 0.05, 0.23), (0, 1.0, 0), "hull_mid", rot=(0, 0, PI * k / 4))
    for k in range(8):
        a = 2 * PI * k / 8
        m.box((0.08, 0.08, 0.05), (0.62 * math.cos(a), 1.0 + 0.62 * math.sin(a), 0.13), "hazard_yellow" if k % 2 else "black_metal")
    m.cyl(0.06, 1.1, (0, 1.0, 0), "chrome", axis="x", seg=8)
    m.box((0.2, 0.14, 0.04), (0, 0.24, 0.3), "black_metal")
    m.box((0.14, 0.03, 0.02), (0, 0.24, 0.33), "em_amber")


@part("turbine", "Impeller Housing")
def _(m, rng):
    m.box((1.2, 0.1, 1.1), (0, 0.05, 0), "hull_dark", 0.01)
    m.cyl(0.6, 0.45, (0, 0.85, 0), "paint_blue", axis="z", seg=20)
    m.torus(0.6, 0.05, (0, 0.85, 0.22), "steel", axis="z", seg=20, tseg=4)
    m.cyl(0.45, 0.05, (0, 0.85, 0.25), "glass_blue", axis="z", seg=16)
    for k in range(6):
        m.box((0.5, 0.05, 0.04), (0, 0.85, 0.24), "chrome", rot=(0, 0, PI * k / 6))
    m.cyl(0.09, 0.08, (0, 0.85, 0.3), "chrome", axis="z", seg=8)
    pass
    m.cyl(0.13, 0.7, (0.5, 1.3, 0), "paint_blue", seg=10, rot=(0, 0, 0))
    flange(m, (0.5, 1.65, 0), 0.13, "y")
    m.cyl(0.14, 0.5, (0, 0.85, -0.45), "gunmetal", axis="z", seg=12)
    m.cyl(0.24, 0.3, (0, 0.85, -0.75), "hull_dark", axis="z", seg=12)
    for sx in (-1, 1):
        m.box((0.12, 0.6, 0.35), (sx * 0.4, 0.4, 0.0), "hull_dark", 0.01)


@part("turbine", "Vertical Turbopump")
def _(m, rng):
    m.cyl(0.55, 0.1, (0, 0.05, 0), "hull_dark", seg=14)
    m.cyl(0.4, 0.6, (0, 0.4, 0), "steel", seg=14, r2=0.3)
    m.sphere(0.4, (0, 0.4, 0), "paint_orange", seg=14, ring=8, scale=(1.0, 0.8, 1.0))
    m.cyl(0.12, 0.6, (0, 1.0, 0), "gunmetal", seg=10)
    m.cyl(0.3, 0.7, (0, 1.6, 0), "paint_orange", seg=14, r2=0.3)
    for y in (1.35, 1.6, 1.85):
        m.torus(0.3, 0.02, (0, y, 0), "steel", seg=14, tseg=4)
    m.cyl(0.18, 0.15, (0, 2.03, 0), "hull_dark", seg=10)
    pipe(m, (0.35, 0.4, 0.1), (0.75, 0.4, 0.1), 0.09, "steel")
    flange(m, (0.78, 0.4, 0.1), 0.09, "x")
    pipe(m, (0.3, 1.6, 0.0), (0.6, 1.6, 0.0), 0.06, "copper")
    pipe(m, (0.6, 1.6, 0.0), (0.6, 0.6, 0.1), 0.06, "copper")
    m.box((0.2, 0.15, 0.06), (0, 1.0, 0.16), "black_metal")
    m.box((0.14, 0.03, 0.02), (0, 1.0, 0.2), "em_green")


@part("turbine", "Gyroscope")
def _(m, rng):
    m.cyl(0.5, 0.1, (0, 0.05, 0), "hull_dark", seg=14)
    m.cyl(0.14, 0.7, (0, 0.45, 0), "chrome", seg=10, r2=0.09)
    m.torus(0.75, 0.05, (0, 1.4, 0), "brass", axis="z", seg=22, tseg=5)
    m.torus(0.6, 0.045, (0, 1.4, 0), "steel", axis="x", seg=20, tseg=5)
    m.torus(0.45, 0.04, (0, 1.4, 0), "gold_trim", axis="y", seg=18, tseg=5)
    m.sphere(0.2, (0, 1.4, 0), "em_cyan", seg=10, ring=6)
    pass
    m.cyl(0.06, 0.4, (0, 0.82, 0), "steel", seg=6)
    m.cyl(0.08, 0.15, (0.75, 1.4, 0), "black_metal", axis="x", seg=8)
    m.cyl(0.08, 0.15, (-0.75, 1.4, 0), "black_metal", axis="x", seg=8)
    m.cyl(0.07, 0.15, (0, 1.4, 0.6), "black_metal", axis="z", seg=8)
    m.cyl(0.07, 0.15, (0, 1.4, -0.6), "black_metal", axis="z", seg=8)
    pass
    pass


# ================================================================ VALVE (18)
def _backplate(m, w, h, mat="hull_dark", t=0.03):
    m.box((w, h, t), (0, 0, t / 2), mat, 0.008)


@part("valve", "Gate Valve Wheel", "wall")
def _(m, rng):
    _backplate(m, 0.7, 0.7)
    m.cyl(0.07, 0.8, (0, 0, 0.16), "gunmetal", axis="x", seg=10)
    flange(m, (-0.3, 0, 0.16), 0.07, "x")
    flange(m, (0.3, 0, 0.16), 0.07, "x")
    m.box((0.2, 0.26, 0.2), (0, 0, 0.16), "paint_green", 0.02)
    m.cyl(0.05, 0.14, (0, 0.0, 0.3), "steel", axis="z", seg=8)
    wheel(m, (0, 0, 0.4), 0.16, 3, "paint_red", 0.0)
    m.cyl(0.015, 0.14, (0, 0, 0.34), "chrome", axis="z", seg=5)
    for x in (-0.15, 0.15):
        m.box((0.06, 0.06, 0.13), (x, 0, 0.065), "steel")


@part("valve", "Gauge Cluster", "wall")
def _(m, rng):
    _backplate(m, 0.8, 0.34, "black_metal")
    for k, x in enumerate((-0.25, 0.0, 0.25)):
        gauge(m, (x, 0.0, 0.03), 0.1 if k == 1 else 0.075)
        pass
    leds(m, -0.3, 0.3, -0.14, 0.04, ["em_green", "em_green", "em_amber", "em_red"], 0.025)
    m.box((0.8, 0.03, 0.03), (0, 0.17, 0.04), "hazard_yellow")
    bolts(m, [(-0.37, 0.14, 0.03), (0.37, 0.14, 0.03), (-0.37, -0.14, 0.03), (0.37, -0.14, 0.03)])


@part("valve", "Manifold Valve Block", "wall")
def _(m, rng):
    _backplate(m, 0.8, 0.6)
    m.box((0.6, 0.16, 0.14), (0, 0.0, 0.11), "brass", 0.015)
    for k in range(4):
        x = -0.22 + k * 0.146
        m.cyl(0.03, 0.2, (x, 0.1, 0.11), "brass", seg=6)
        m.cyl(0.03, 0.18, (x, -0.1, 0.11), "brass", seg=6)
        m.cyl(0.025, 0.12, (x, 0.0, 0.2), "chrome", axis="z", seg=6)
        m.box((0.1, 0.03, 0.03), (x, 0.0, 0.27), "paint_red" if k % 2 else "paint_blue")
    m.cyl(0.05, 0.1, (-0.33, 0.0, 0.11), "steel", axis="x", seg=8)
    m.cyl(0.05, 0.1, (0.33, 0.0, 0.11), "steel", axis="x", seg=8)
    gauge(m, (0.0, 0.22, 0.03), 0.06)


@part("valve", "Pressure Regulator", "wall")
def _(m, rng):
    _backplate(m, 0.5, 0.6)
    m.cyl(0.04, 0.6, (0, 0.0, 0.12), "steel", axis="x", seg=8)
    m.cyl(0.11, 0.2, (0, 0.05, 0.12), "gunmetal", seg=12)
    m.cyl(0.13, 0.05, (0, 0.17, 0.12), "steel", seg=12)
    m.cyl(0.04, 0.1, (0, 0.24, 0.12), "chrome", seg=8)
    m.cyl(0.08, 0.05, (0, 0.3, 0.12), "paint_orange", seg=10)
    gauge(m, (0.0, 0.05, 0.25), 0.06)
    m.cyl(0.1, 0.07, (0, -0.09, 0.12), "hull_mid", seg=10)
    flange(m, (-0.22, 0, 0.12), 0.04, "x")
    flange(m, (0.22, 0, 0.12), 0.04, "x")


@part("valve", "Flow Meter", "wall")
def _(m, rng):
    _backplate(m, 0.9, 0.5)
    m.cyl(0.06, 0.85, (0, -0.1, 0.14), "steel", axis="x", seg=10)
    m.box((0.28, 0.12, 0.14), (0, -0.1, 0.14), "hull_mid", 0.015)
    flange(m, (-0.3, -0.1, 0.14), 0.06, "x")
    flange(m, (0.3, -0.1, 0.14), 0.06, "x")
    m.box((0.36, 0.2, 0.1), (0, 0.06, 0.17), "black_metal", 0.015)
    m.box((0.3, 0.13, 0.01), (0, 0.06, 0.225), "em_cyan")
    m.box((0.1, 0.05, 0.012), (0, 0.06, 0.23), "black_metal")
    m.cyl(0.03, 0.08, (0, -0.02, 0.16), "steel", seg=6)
    pass


@part("valve", "Valve Tree", "floor")
def _(m, rng):
    m.box((0.5, 0.08, 0.5), (0, 0.04, 0), "hull_dark", 0.01)
    m.cyl(0.09, 1.4, (0, 0.78, 0), "steel", seg=10)
    flange(m, (0, 0.12, 0), 0.09, "y")
    for k, (y, side) in enumerate(((0.45, 1), (0.85, -1), (1.25, 1))):
        m.cyl(0.05, 0.4, (side * 0.22, y, 0), "gunmetal", axis="x", seg=8)
        flange(m, (side * 0.4, y, 0), 0.05, "x")
        m.box((0.12, 0.16, 0.12), (0, y, 0), "paint_blue", 0.01)
        wheel(m, (0, y, 0.11), 0.08, 3, "paint_red" if k != 1 else "paint_orange")
    m.cyl(0.11, 0.1, (0, 1.53, 0), "hull_mid", seg=10)
    pass
    m.cyl(0.03, 0.15, (0, 1.65, 0), "chrome", seg=6)
    gauge(m, (0.0, 1.0, 0.1), 0.05)


@part("valve", "Quick Couplings", "table")
def _(m, rng):
    m.box((0.36, 0.03, 0.14), (0, 0.015, 0), "plastic_grey", 0.005)
    pass
    for sx, mt in ((-1, "brass"), (1, "chrome")):
        m.cyl(0.035, 0.14, (sx * 0.1, 0.08, 0), mt, axis="x", seg=10)
        m.cyl(0.045, 0.05, (sx * 0.03, 0.08, 0), "steel", axis="x", seg=10)
        pass
        for s in (-1, 1):
            pass
        m.box((0.02, 0.02, 0.09), (sx * 0.05, 0.08, 0), "paint_red" if sx < 0 else "paint_blue")
    m.cyl(0.03, 0.06, (-0.19, 0.08, 0), "rubber", axis="x", seg=8)
    m.cyl(0.03, 0.06, (0.19, 0.08, 0), "rubber", axis="x", seg=8)


@part("valve", "Pressure Relief Valve", "floor")
def _(m, rng):
    m.box((0.4, 0.06, 0.4), (0, 0.03, 0), "hull_dark", 0.01)
    m.cyl(0.06, 0.5, (0, 0.31, 0), "steel", seg=8)
    flange(m, (0, 0.08, 0), 0.06, "y")
    m.cyl(0.1, 0.3, (0, 0.65, 0), "paint_red", seg=10)
    m.cyl(0.13, 0.05, (0, 0.82, 0), "steel", seg=10)
    m.cyl(0.07, 0.2, (0, 0.95, 0), "steel", seg=10, r2=0.05)
    m.cyl(0.04, 0.08, (0, 1.08, 0), "brass", seg=6)
    m.sphere(0.05, (0, 1.14, 0), "brass", seg=6, ring=4)
    m.link((0.08, 0.62, 0), (0.25, 0.62, 0), 0.045, "steel")
    m.link((0.25, 0.62, 0), (0.25, 1.2, 0), 0.045, "steel")
    m.cyl(0.07, 0.03, (0.25, 1.22, 0), "steel", seg=8)
    pass
    m.torus(0.105, 0.012, (0, 0.55, 0), "hazard_yellow", seg=10, tseg=4)


@part("valve", "Sight Glass", "wall")
def _(m, rng):
    _backplate(m, 0.5, 0.5)
    m.cyl(0.05, 0.5, (0, 0, 0.12), "steel", axis="x", seg=8)
    pass
    pass
    m.cyl(0.17, 0.1, (0, 0, 0.14), "gunmetal", axis="z", seg=14)
    m.cyl(0.13, 0.03, (0, 0, 0.2), "glass_blue", axis="z", seg=14)
    m.cyl(0.08, 0.02, (0, 0, 0.19), "em_cyan", axis="z", seg=10)
    bolt_circle(m, 0, 0, 0.2, 0.15, 8, 0.012, "steel", "z", 0.02)
    flange(m, (-0.22, 0, 0.12), 0.05, "x")
    flange(m, (0.22, 0, 0.12), 0.05, "x")


@part("valve", "Butterfly Valve", "wall")
def _(m, rng):
    _backplate(m, 0.7, 0.6)
    m.cyl(0.12, 0.1, (0, 0, 0.16), "steel", axis="x", seg=14)
    m.cyl(0.11, 0.6, (0, 0, 0.16), "gunmetal", axis="x", seg=12)
    m.cyl(0.14, 0.12, (0, 0, 0.16), "paint_blue", axis="x", seg=14)
    flange(m, (-0.28, 0, 0.16), 0.11, "x")
    flange(m, (0.28, 0, 0.16), 0.11, "x")
    m.cyl(0.03, 0.2, (0, 0.17, 0.16), "chrome", seg=6)
    m.box((0.1, 0.06, 0.08), (0, 0.27, 0.16), "hull_mid", 0.01)
    pass
    m.link((0, 0.3, 0.16), (0.24, 0.34, 0.16 + 0.12), 0.015, "paint_orange")
    m.sphere(0.03, (0.24, 0.34, 0.28), "paint_orange", seg=6, ring=4)


@part("valve", "Ball Valve", "table")
def _(m, rng):
    m.cyl(0.03, 0.34, (0, 0.09, 0), "brass", axis="x", seg=8)
    m.sphere(0.07, (0, 0.09, 0), "brass", seg=10, ring=6)
    m.cyl(0.02, 0.09, (0, 0.17, 0), "chrome", seg=6)
    m.box((0.18, 0.02, 0.03), (0.06, 0.22, 0), "paint_green", 0.005)
    m.box((0.03, 0.03, 0.03), (-0.03, 0.22, 0), "paint_green")
    for sx in (-1, 1):
        m.cyl(0.05, 0.03, (sx * 0.14, 0.09, 0), "steel", axis="x", seg=8)
    m.box((0.36, 0.03, 0.14), (0, 0.015, 0), "plastic_grey", 0.005)
    m.box((0.05, 0.08, 0.05), (0, 0.06, 0), "steel")


@part("valve", "Dial Gauge", "wall")
def _(m, rng):
    m.cyl(0.24, 0.05, (0, 0, 0.025), "hull_dark", axis="z", seg=16)
    m.cyl(0.22, 0.06, (0, 0, 0.07), "chrome", axis="z", seg=16)
    m.cyl(0.19, 0.01, (0, 0, 0.105), "plastic_white", axis="z", seg=16)
    for k in range(11):
        a = -PI * 0.75 + PI * 1.5 * k / 10
        m.box((0.02 if k % 5 == 0 else 0.012, 0.045, 0.006), (0.15 * math.sin(a), 0.15 * math.cos(a), 0.113), "black_metal" if k < 8 else "paint_red", rot=(0, 0, -a))
    m.box((0.015, 0.16, 0.008), (0.03, 0.05, 0.12), "black_metal", rot=(0, 0, -0.5))
    m.cyl(0.02, 0.012, (0, 0, 0.125), "chrome", axis="z", seg=8)
    m.cyl(0.19, 0.008, (0, 0, 0.115), "glass", axis="z", seg=16)
    m.cyl(0.04, 0.15, (0, -0.25, 0.06), "brass", seg=8)
    pass


@part("valve", "Twin Isolation Station", "wall")
def _(m, rng):
    _backplate(m, 0.9, 0.9)
    for y, mt in ((0.25, "paint_red"), (-0.25, "paint_blue")):
        m.cyl(0.05, 0.85, (0, y, 0.12), "steel", axis="x", seg=8)
        m.box((0.16, 0.16, 0.14), (0, y, 0.13), mt, 0.015)
        m.cyl(0.02, 0.15, (0, y, 0.24), "chrome", axis="z", seg=6)
        wheel(m, (0, y, 0.32), 0.11, 4, mt)
    m.cyl(0.04, 0.6, (0.3, 0.0, 0.12), "gunmetal", seg=8)
    m.cyl(0.04, 0.6, (-0.3, 0.0, 0.12), "gunmetal", seg=8)
    pass
    gauge(m, (0.0, 0.0, 0.13), 0.055)
    hazard(m, -0.4, 0.4, -0.44, -0.38, 0.04, n=8)


@part("valve", "Test Manifold", "table")
def _(m, rng):
    m.box((0.5, 0.04, 0.3), (0, 0.02, 0), "hull_dark", 0.005)
    m.box((0.4, 0.06, 0.06), (0, 0.09, 0), "brass", 0.01)
    for k in range(4):
        x = -0.15 + k * 0.1
        m.cyl(0.015, 0.1, (x, 0.13, 0), "brass", seg=6)
        m.box((0.05, 0.015, 0.015), (x, 0.19, 0), "paint_red" if k % 2 else "paint_blue")
        m.link((x, 0.09, 0.03), (x, 0.09, 0.12), 0.012, "copper")
    m.cyl(0.04, 0.03, (-0.22, 0.09, 0), "steel", axis="x", seg=8)
    pass
    m.cyl(0.05, 0.04, (0.0, 0.14, 0.14), "chrome", axis="z", seg=10)
    m.cyl(0.04, 0.005, (0.0, 0.14, 0.165), "plastic_white", axis="z", seg=10)


@part("valve", "Emergency Shutoff", "wall")
def _(m, rng):
    _backplate(m, 0.45, 0.55, "hazard_yellow")
    m.box((0.35, 0.45, 0.02), (0, 0, 0.04), "black_metal", 0.005)
    m.cyl(0.09, 0.05, (0, 0.03, 0.07), "chrome", axis="z", seg=14)
    m.cyl(0.075, 0.05, (0, 0.03, 0.11), "paint_red", axis="z", seg=14, r2=0.065)
    for a in (0, PI / 2):
        m.box((0.24, 0.02, 0.15), (0, 0.03, 0.14), "glass", 0.0, rot=(0, 0, a))
    pass
    m.box((0.3, 0.08, 0.01), (0, -0.16, 0.055), "plastic_white")
    m.box((0.2, 0.02, 0.012), (0, -0.16, 0.062), "paint_red")
    m.box((0.05, 0.02, 0.02), (0, 0.2, 0.06), "em_red")


@part("valve", "Pneumatic Actuator Valve", "floor")
def _(m, rng):
    m.box((0.5, 0.06, 0.4), (0, 0.03, 0), "hull_dark", 0.01)
    pass
    m.cyl(0.07, 0.7, (0, 0.4, 0), "steel", axis="x", seg=10)
    flange(m, (-0.3, 0.4, 0), 0.07, "x")
    flange(m, (0.3, 0.4, 0), 0.07, "x")
    m.box((0.2, 0.2, 0.2), (0, 0.42, 0), "paint_teal", 0.02)
    m.cyl(0.05, 0.2, (0, 0.62, 0), "chrome", seg=8)
    m.cyl(0.16, 0.5, (0, 0.95, 0), "paint_orange", seg=12)
    m.cyl(0.17, 0.05, (0, 0.7, 0), "steel", seg=12)
    m.cyl(0.17, 0.05, (0, 1.2, 0), "steel", seg=12)
    m.cyl(0.03, 0.12, (0, 1.29, 0), "chrome", seg=6)
    pass
    m.box((0.12, 0.16, 0.06), (0.22, 0.65, 0), "black_metal", 0.01)
    m.box((0.05, 0.02, 0.02), (0.22, 0.7, 0.04), "em_green")
    pipe(m, (0.16, 0.95, 0), (0.22, 0.95, 0), 0.015, "copper")
    pipe(m, (0.22, 0.95, 0), (0.22, 0.73, 0), 0.015, "copper")


@part("valve", "Chain Wheel Valve", "wall")
def _(m, rng):
    _backplate(m, 0.7, 1.4)
    m.cyl(0.06, 0.8, (0, 0.4, 0.14), "steel", axis="x", seg=10)
    m.box((0.18, 0.2, 0.18), (0, 0.4, 0.14), "paint_navy", 0.015)
    m.cyl(0.04, 0.16, (0, 0.4, 0.28), "chrome", axis="z", seg=6)
    m.cyl(0.22, 0.03, (0, 0.4, 0.36), "paint_red", axis="z", seg=12)
    m.torus(0.22, 0.012, (0, 0.4, 0.36), "steel", axis="z", seg=12, tseg=4)
    for k in range(6):
        a = 2 * PI * k / 6
        m.box((0.03, 0.05, 0.03), (0.22 * math.cos(a), 0.4 + 0.22 * math.sin(a), 0.36), "paint_red", rot=(0, 0, a))
    m.link((0.23, 0.4, 0.37), (0.23, -0.55, 0.37), 0.01, "chrome", 4)
    m.link((-0.23, 0.4, 0.37), (-0.23, -0.55, 0.37), 0.01, "chrome", 4)
    pass
    pass
    pass


@part("valve", "Check Valve", "table")
def _(m, rng):
    m.cyl(0.03, 0.32, (0, 0.07, 0), "steel", axis="x", seg=8)
    m.sphere(0.06, (0, 0.07, 0), "paint_orange", seg=10, ring=6, scale=(1.4, 1, 1))
    pass
    m.cyl(0.05, 0.04, (0, 0.14, 0), "steel", seg=8)
    pass
    for sx in (-1, 1):
        flange(m, (sx * 0.14, 0.07, 0), 0.03, "x", 0.02)
    m.box((0.05, 0.005, 0.03), (0, 0.07, 0.062), "plastic_white")
    m.box((0.02, 0.005, 0.005), (0.01, 0.07, 0.066), "paint_red")
    m.box((0.36, 0.02, 0.12), (0, 0.01, 0), "plastic_grey", 0.004)
    m.box((0.05, 0.05, 0.05), (0, 0.045, 0), "steel")


# ================================================================ JUNCTION (22)
def _door_box(m, w, h, d, body="hull_mid", y=0.0, wall=True):
    """Wall-mounted enclosure centred on origin, extends to +z."""
    m.box((w, h, d), (0, y, d / 2), body, 0.012)
    m.box((w - 0.06, h - 0.06, 0.01), (0, y, d + 0.004), "hull_light", 0.004)
    bolts(m, [(w / 2 - 0.03, y + h / 2 - 0.03, d + 0.01), (-w / 2 + 0.03, y + h / 2 - 0.03, d + 0.01),
              (w / 2 - 0.03, y - h / 2 + 0.03, d + 0.01), (-w / 2 + 0.03, y - h / 2 + 0.03, d + 0.01)], 0.012, 0.012, "steel", "z")


@part("junction", "Junction Box", "wall")
def _(m, rng):
    _door_box(m, 0.4, 0.5, 0.15, "paint_grey")
    m.box((0.03, 0.12, 0.03), (0.15, 0.0, 0.18), "black_metal")
    m.box((0.12, 0.05, 0.01), (-0.06, 0.15, 0.17), "hazard_yellow")
    m.cyl(0.03, 0.12, (-0.1, -0.3, 0.075), "black_metal", seg=6)
    m.cyl(0.03, 0.12, (0.1, -0.3, 0.075), "black_metal", seg=6)
    m.cyl(0.02, 0.14, (0, 0.32, 0.075), "black_metal", seg=6)
    m.box((0.04, 0.03, 0.012), (0.0, -0.1, 0.17), "em_green")


@part("junction", "Breaker Panel", "wall")
def _(m, rng):
    _door_box(m, 0.6, 0.9, 0.12, "hull_dark")
    m.box((0.5, 0.05, 0.02), (0, 0.38, 0.14), "plastic_white")
    for r in range(8):
        for c in (-1, 1):
            m.box((0.1, 0.04, 0.03), (c * 0.13, 0.28 - r * 0.075, 0.15), "black_metal")
            m.box((0.03, 0.02, 0.035), (c * 0.13 + (0.03 if rng.random() < 0.5 else -0.03), 0.28 - r * 0.075, 0.165), "paint_red" if r == 0 else "plastic_white")
    m.box((0.02, 0.68, 0.02), (0, -0.02, 0.145), "steel")
    leds(m, -0.2, 0.2, -0.4, 0.14, ["em_green", "em_green", "em_amber"], 0.025)


@part("junction", "Fuse Box", "wall")
def _(m, rng):
    _door_box(m, 0.55, 0.32, 0.1, "paint_orange")
    m.box((0.46, 0.14, 0.04), (0, 0.0, 0.13), "glass_dark")
    for k in range(6):
        x = -0.19 + k * 0.076
        m.cyl(0.014, 0.1, (x, 0.0, 0.13), "ceramic", axis="y", seg=6)
        m.box((0.012, 0.06, 0.012), (x, 0.0, 0.13), "em_amber" if k != 3 else "em_red")
    hazard(m, -0.24, 0.24, -0.14, -0.1, 0.11, n=8)


@part("junction", "Bus Bar Riser", "wall")
def _(m, rng):
    m.box((0.5, 2.0, 0.04), (0, 0, 0.02), "hull_dark", 0.008)
    for k in range(3):
        x = -0.15 + k * 0.15
        m.box((0.06, 1.9, 0.02), (x, 0, 0.13), ["copper", "brass", "copper"][k])
        pass
    for y in (-0.8, -0.3, 0.3, 0.8):
        m.box((0.46, 0.06, 0.09), (0, y, 0.085), "ceramic", 0.008)
        for x in (-0.15, 0.0, 0.15):
            m.cyl(0.02, 0.02, (x, y, 0.14), "steel", axis="z", seg=6)
    m.box((0.46, 0.2, 0.12), (0, 0.55, 0.06), "black_metal", 0.01)
    hazard(m, -0.2, 0.2, -1.0, -0.94, 0.05, n=6)


@part("junction", "Relay Cabinet", "floor")
def _(m, rng):
    cabinet(m, 0.7, 1.7, 0.4, "hull_dark")
    m.box((0.6, 1.3, 0.02), (0, 0.95, 0.2), "glass_dark")
    for r in range(5):
        for c in range(4):
            m.box((0.1, 0.15, 0.08), (-0.21 + c * 0.14, 0.45 + r * 0.24, 0.17), "plastic_grey" if (r + c) % 3 else "paint_orange", 0.008)
            m.box((0.03, 0.02, 0.01), (-0.21 + c * 0.14, 0.5 + r * 0.24, 0.22), "em_green" if rng.random() < 0.7 else "em_amber")
    m.box((0.6, 0.02, 0.03), (0, 1.62, 0.21), "hazard_yellow")
    m.box((0.05, 0.14, 0.04), (0.3, 0.95, 0.22), "chrome")


@part("junction", "Cable Termination Cabinet", "floor")
def _(m, rng):
    cabinet(m, 0.9, 1.9, 0.5, "paint_navy")
    m.box((0.8, 0.14, 0.02), (0, 0.3, 0.26), "hull_mid")
    for sx in (-1, 1):
        m.box((0.4, 1.5, 0.02), (sx * 0.21, 1.1, 0.255), "hull_mid", 0.006)
        m.box((0.03, 0.2, 0.03), (sx * 0.04, 1.1, 0.28), "chrome")
    for k in range(7):
        x = -0.32 + k * 0.107
        m.cyl(0.03, 0.15, (x, 0.08, 0.0), "black_metal", seg=6)
        pass
    for k in range(7):
        x = -0.32 + k * 0.107
        pass
    for k in range(6):
        x = -0.3 + k * 0.12
        pass
    m.box((0.5, 0.12, 0.01), (0, 1.7, 0.265), "plastic_white")
    leds(m, -0.3, 0.3, 1.56, 0.265, ["em_green", "em_green", "em_red"], 0.03)
    hazard(m, -0.4, 0.4, 0.16, 0.24, 0.27, n=8)


@part("junction", "Patch Panel", "wall")
def _(m, rng):
    m.box((0.9, 0.5, 0.06), (0, 0, 0.03), "black_metal", 0.01)
    cols = ["cable_r", "cable_b", "cable_g"]
    for r in range(3):
        for c in range(8):
            x = -0.36 + c * 0.1
            y = 0.14 - r * 0.14
            m.box((0.06, 0.06, 0.02), (x, y, 0.07), "gunmetal")
            m.box((0.04, 0.04, 0.012), (x, y, 0.075), "plastic_black")
            m.box((0.02, 0.012, 0.012), (x + 0.03, y + 0.045, 0.075), "em_green" if rng.random() < 0.6 else "plastic_black")
    for k in range(3):
        x0 = -0.36 + rng.randrange(8) * 0.1
        x1 = -0.36 + rng.randrange(8) * 0.1
        mt = ["paint_red", "paint_blue", "paint_green"][k]
        m.tube([(x0, 0.14 - k * 0.14, 0.085), (x0, 0.14 - k * 0.14, 0.2), (x1, 0.14 - ((k + 1) % 3) * 0.14, 0.2),
                (x1, 0.14 - ((k + 1) % 3) * 0.14, 0.085)], 0.009, mt, seg=4)


@part("junction", "Diagnostic Port Panel", "wall")
def _(m, rng):
    _door_box(m, 0.5, 0.42, 0.06, "hull_dark")
    m.screen((0.3, 0.16), (-0.05, 0.08, 0.075), "diagnostic", bezel=0.01)
    for k in range(3):
        m.box((0.05, 0.05, 0.02), (0.17, 0.12 - k * 0.07, 0.075), "black_metal")
        m.box((0.03, 0.03, 0.01), (0.17, 0.12 - k * 0.07, 0.086), "em_cyan")
    for k in range(4):
        m.cyl(0.02, 0.02, (-0.17 + k * 0.08, -0.12, 0.075), "gunmetal", axis="z", seg=8)
        m.cyl(0.012, 0.022, (-0.17 + k * 0.08, -0.12, 0.078), "brass", axis="z", seg=6)
    m.box((0.1, 0.03, 0.01), (0.15, -0.14, 0.07), "hazard_yellow")


@part("junction", "Terminal Block", "wall")
def _(m, rng):
    m.box((0.9, 0.24, 0.04), (0, 0, 0.02), "hull_dark", 0.006)
    m.box((0.85, 0.03, 0.03), (0, 0.0, 0.055), "brushed_alu")
    for k in range(14):
        x = -0.4 + k * 0.062
        m.box((0.055, 0.14, 0.05), (x, 0.0, 0.09), ["paint_grey", "paint_grey", "hazard_yellow", "paint_green"][k % 4], 0.004)
        m.cyl(0.011, 0.012, (x, 0.05, 0.12), "steel", axis="z", seg=5)
        m.cyl(0.011, 0.012, (x, -0.05, 0.12), "steel", axis="z", seg=5)
        pass
    m.box((0.85, 0.02, 0.015), (0, -0.1, 0.09), "plastic_white")


@part("junction", "Control Cabinet with Lights", "floor")
def _(m, rng):
    cabinet(m, 0.8, 1.8, 0.45, "hull_light")
    m.box((0.7, 0.9, 0.02), (0, 0.95, 0.235), "hull_mid", 0.006)
    for r in range(4):
        for c in range(5):
            mt = rng.choice(["em_green", "em_green", "em_amber", "em_red", "em_cyan"])
            m.cyl(0.024, 0.015, (-0.24 + c * 0.12, 1.25 - r * 0.15, 0.25), mt, axis="z", seg=6)
    for c in range(3):
        m.cyl(0.035, 0.03, (-0.2 + c * 0.2, 0.7, 0.25), "black_metal", axis="z", seg=8)
        m.box((0.01, 0.05, 0.01), (-0.2 + c * 0.2, 0.7, 0.27), "plastic_white")
    m.cyl(0.05, 0.05, (0.25, 0.7, 0.25), "paint_red", axis="z", seg=10)
    m.box((0.6, 0.08, 0.01), (0, 1.62, 0.235), "plastic_white")
    hazard(m, -0.35, 0.35, 0.12, 0.2, 0.235, n=8)


@part("junction", "Switchgear", "floor")
def _(m, rng):
    cabinet(m, 1.0, 2.0, 0.6, "paint_green")
    m.box((0.9, 0.5, 0.02), (0, 1.45, 0.31), "hull_light", 0.005)
    m.screen((0.4, 0.22), (0.15, 1.45, 0.325), "power", bezel=0.012)
    for k in range(3):
        m.cyl(0.035, 0.02, (-0.32, 1.6 - k * 0.15, 0.32), "chrome", axis="z", seg=8)
    m.box((0.85, 0.7, 0.02), (0, 0.75, 0.31), "hull_mid", 0.005)
    m.box((0.1, 0.4, 0.04), (0, 0.8, 0.33), "black_metal", 0.008)
    m.link((0.0, 0.68, 0.36), (0.0, 0.92, 0.36), 0.03, "paint_red")
    m.sphere(0.045, (0.0, 0.94, 0.36), "paint_red", seg=8, ring=5)
    m.box((0.14, 0.05, 0.015), (-0.3, 0.75, 0.32), "em_green")
    m.box((0.14, 0.05, 0.015), (0.3, 0.75, 0.32), "em_red")
    hazard(m, -0.45, 0.45, 0.15, 0.25, 0.31, n=8)


@part("junction", "Conduit Cluster", "wall")
def _(m, rng):
    _door_box(m, 0.36, 0.36, 0.14, "paint_grey")
    for a in (0, PI / 2, PI, 1.5 * PI):
        d = (math.cos(a), math.sin(a))
        m.link((d[0] * 0.18, d[1] * 0.18, 0.07), (d[0] * 0.7, d[1] * 0.7, 0.07), 0.04, "steel")
        m.cyl(0.055, 0.04, (d[0] * 0.22, d[1] * 0.22, 0.07), "gunmetal", axis="x" if d[0] else "y", seg=8)
        m.box((0.1, 0.1, 0.02), (d[0] * 0.45, d[1] * 0.45, 0.02), "steel")
    m.box((0.1, 0.05, 0.01), (0, 0, 0.15), "hazard_yellow")


@part("junction", "Cable Tray Segment", "wall")
def _(m, rng):
    m.box((1.6, 0.36, 0.03), (0, 0, 0.14), "hull_mid", 0.005)
    m.box((1.6, 0.03, 0.06), (0, 0.18, 0.14), "hull_mid")
    m.box((1.6, 0.03, 0.06), (0, -0.18, 0.14), "hull_mid")
    for x in (-0.6, 0.0, 0.6):
        m.box((0.05, 0.4, 0.14), (x, 0, 0.07), "black_metal")
    for k, (mt, y) in enumerate((("rubber", -0.09), ("paint_red", 0.0), ("paint_blue", 0.09))):
        m.cyl(0.03, 1.5, (0, y, 0.19), mt, axis="x", seg=6)
    m.cyl(0.045, 1.5, (0, 0.0, 0.25), "copper", axis="x", seg=6)
    for x in (-0.3, 0.3):
        m.box((0.05, 0.3, 0.01), (x, 0.0, 0.29), "plastic_black")


@part("junction", "Disconnect Switch", "wall")
def _(m, rng):
    _door_box(m, 0.36, 0.52, 0.16, "paint_orange")
    m.box((0.16, 0.34, 0.06), (0, 0.0, 0.2), "black_metal", 0.01)
    m.link((0, 0.1, 0.23), (0, -0.02, 0.36), 0.02, "paint_red")
    m.sphere(0.04, (0, -0.02, 0.37), "paint_red", seg=8, ring=5)
    m.box((0.04, 0.03, 0.01), (0, 0.13, 0.235), "em_green")
    m.box((0.04, 0.03, 0.01), (0, -0.13, 0.235), "em_red")
    hazard(m, -0.15, 0.15, -0.23, -0.19, 0.175, n=5)
    m.box((0.06, 0.03, 0.03), (0.15, 0.0, 0.18), "steel")


@part("junction", "Meter Panel", "wall")
def _(m, rng):
    _door_box(m, 0.9, 0.55, 0.08, "hull_dark")
    for r in range(2):
        for c in range(3):
            gauge(m, (-0.28 + c * 0.28, 0.1 - r * 0.2, 0.09), 0.06 if r else 0.08)
    pass
    leds(m, -0.36, 0.36, -0.24, 0.095, ["em_green"] * 4 + ["em_amber"] * 2, 0.025)


@part("junction", "Data Interface Rack", "floor")
def _(m, rng):
    m.box((0.62, 1.8, 0.7), (0, 0.9, 0), "black_metal", 0.01)
    for k in range(8):
        y = 0.25 + k * 0.19
        m.box((0.54, 0.16, 0.03), (0, y, 0.36), "hull_mid" if k % 2 else "hull_dark", 0.004)
        leds(m, -0.2, 0.2, y, 0.38, led_pat(rng, 6, ("em_green", "em_cyan", "em_amber")), 0.02)
        pass
    pass
    m.box((0.62, 0.05, 0.75), (0, 0.03, 0), "hull_dark")
    vents(m, 0, 1.7, 0.36, 0.4, 3, 0.015, 0.04)


@part("junction", "Service Pedestal", "floor")
def _(m, rng):
    m.cyl(0.25, 0.06, (0, 0.03, 0), "hull_dark", seg=8)
    m.box((0.3, 0.9, 0.24), (0, 0.5, 0), "paint_teal", 0.02)
    m.box((0.34, 0.06, 0.28), (0, 0.98, 0), "hull_dark", 0.01)
    for k in range(3):
        m.box((0.08, 0.08, 0.02), (-0.09 + k * 0.09, 0.75, 0.125), "black_metal")
        m.cyl(0.018, 0.02, (-0.09 + k * 0.09, 0.75, 0.135), "chrome", axis="z", seg=6)
    m.box((0.22, 0.12, 0.01), (0, 0.55, 0.125), "plastic_white")
    leds(m, -0.08, 0.08, 0.4, 0.125, ["em_green", "em_amber"], 0.03)
    m.cyl(0.04, 0.16, (0, 1.09, 0), "paint_orange", seg=8)
    m.cyl(0.05, 0.03, (0, 1.19, 0), "em_amber", seg=8)


@part("junction", "Outlet Strip Panel", "wall")
def _(m, rng):
    m.box((1.0, 0.16, 0.05), (0, 0, 0.025), "black_metal", 0.008)
    for k in range(6):
        x = -0.4 + k * 0.16
        m.box((0.1, 0.1, 0.02), (x, 0, 0.06), "plastic_grey", 0.005)
        m.box((0.02, 0.04, 0.012), (x - 0.02, 0, 0.075), "plastic_black")
        m.box((0.02, 0.04, 0.012), (x + 0.02, 0, 0.075), "plastic_black")
        m.box((0.03, 0.01, 0.01), (x, 0.06, 0.06), "em_green" if k != 4 else "em_red")
    pass
    pass


@part("junction", "Marshalling Cabinet", "floor")
def _(m, rng):
    cabinet(m, 1.0, 1.9, 0.5, "hull_mid")
    m.box((0.9, 1.7, 0.03), (0, 1.0, 0.0), "black_metal")
    for k in range(7):
        y = 0.4 + k * 0.2
        m.box((0.85, 0.04, 0.05), (0, y, 0.24), "paint_grey")
        for c in range(7):
            m.box((0.03, 0.05, 0.02), (-0.33 + c * 0.11, y, 0.265), rng.choice(["hazard_yellow", "paint_green", "paint_grey", "paint_red"]))
    m.box((0.5, 1.8, 0.02), (0.52, 1.0, 0.23), "hull_light", 0.006, rot=(0, -0.9, 0))
    pass
    hazard(m, -0.4, 0.4, 0.1, 0.2, 0.245, n=8)


@part("junction", "Surge Protector Box", "wall")
def _(m, rng):
    _door_box(m, 0.3, 0.26, 0.1, "plastic_grey")
    m.box((0.2, 0.08, 0.02), (0, 0.04, 0.115), "glass_dark")
    for k in range(3):
        m.box((0.04, 0.03, 0.012), (-0.06 + k * 0.06, 0.04, 0.128), ["em_green", "em_green", "em_amber"][k])
    m.box((0.1, 0.05, 0.012), (0, -0.06, 0.112), "plastic_white")
    m.cyl(0.02, 0.1, (-0.08, -0.18, 0.05), "black_metal", seg=6)
    m.cyl(0.02, 0.1, (0.08, -0.18, 0.05), "black_metal", seg=6)
    m.cyl(0.015, 0.1, (0.0, 0.17, 0.05), "rubber", seg=6)


@part("junction", "Ground Bus", "wall")
def _(m, rng):
    m.box((0.8, 0.14, 0.04), (0, 0, 0.02), "hull_dark")
    for x in (-0.3, 0.3):
        m.cyl(0.02, 0.05, (x, 0, 0.065), "ceramic", axis="z", seg=6)
    m.box((0.8, 0.06, 0.02), (0, 0, 0.1), "copper")
    for k in range(7):
        x = -0.33 + k * 0.11
        m.cyl(0.02, 0.01, (x, 0, 0.115), "brass", axis="z", seg=6)
        m.box((0.04, 0.09, 0.008), (x, -0.07 if k % 2 else 0.07, 0.11), "copper")
        m.link((x, -0.1 if k % 2 else 0.1, 0.11), (x, -0.4 if k % 2 else 0.4, 0.08), 0.012, "paint_green", 4)
    pass


@part("junction", "Distribution Board", "wall")
def _(m, rng):
    _door_box(m, 1.2, 1.4, 0.16, "paint_grey")
    for c in (-1, 1):
        m.box((0.5, 1.2, 0.02), (c * 0.28, 0.0, 0.18), "hull_dark", 0.005)
        for r in range(9):
            m.box((0.34, 0.06, 0.03), (c * 0.28, 0.5 - r * 0.115, 0.2), "black_metal", 0.004)
            m.box((0.05, 0.04, 0.03), (c * 0.28 + 0.1, 0.5 - r * 0.115, 0.22), "em_green" if (r + c) % 3 else "em_amber")
            m.box((0.03, 0.03, 0.03), (c * 0.28 - 0.1, 0.5 - r * 0.115, 0.22), "paint_red" if r == 0 else "plastic_white")
    m.box((0.06, 1.2, 0.03), (0, 0.0, 0.19), "copper")
    pass
    hazard(m, -0.5, 0.5, -0.66, -0.6, 0.175, n=10)


# ================================================================ NOZZLE (8)
@part("nozzle", "Main Thruster Bell")
def _(m, rng):
    m.box((1.4, 0.12, 1.4), (0, 0.06, 0), "hull_dark", 0.01)
    bolt_circle(m, 0, 0.12, 0, 0.6, 8)
    m.cyl(0.55, 0.5, (0, 0.37, 0), "hull_mid", seg=16)
    m.cyl(0.4, 0.3, (0, 0.75, 0), "gunmetal", seg=16, r2=0.25)
    m.cyl(0.25, 1.3, (0, 1.55, 0), "gunmetal", seg=16, r2=0.62)
    pass
    m.cyl(0.23, 1.3, (0, 1.55, 0), "em_orange", seg=14, r2=0.6)
    m.torus(0.62, 0.05, (0, 2.2, 0), "steel", seg=16, tseg=4)
    for y, r in ((1.0, 0.31), (1.4, 0.42), (1.8, 0.53)):
        m.torus(r + 0.03, 0.025, (0, y, 0), "copper", seg=14, tseg=4)
    for a in (0.8, 2.4, 3.9, 5.5):
        m.link((0.5 * math.cos(a), 0.6, 0.5 * math.sin(a)), (0.4 * math.cos(a), 1.5, 0.4 * math.sin(a)), 0.03, "copper")
    pass
    hazard_ring(m, 0, 0.12, 0, 0.55, 0.12, n=12)


@part("nozzle", "RCS Thruster Cluster", "wall")
def _(m, rng):
    m.box((1.0, 1.0, 0.06), (0, 0, 0.03), "hull_dark", 0.015)
    bolts(m, [(-0.45, 0.45, 0.07), (0.45, 0.45, 0.07), (-0.45, -0.45, 0.07), (0.45, -0.45, 0.07)])
    for k, (x, y) in enumerate(((0, 0.28), (0, -0.28), (0.28, 0), (-0.28, 0))):
        m.cyl(0.08, 0.14, (x, y, 0.13), "gunmetal", axis="z", seg=10)
        m.cyl(0.05, 0.16, (x, y, 0.29), "black_metal", axis="z", seg=10, r2=0.1)
        m.cyl(0.035, 0.02, (x, y, 0.25), "em_orange" if k % 2 else "em_amber", axis="z", seg=8)
        pass
    m.cyl(0.1, 0.1, (0, 0, 0.1), "steel", axis="z", seg=10)
    m.box((0.24, 0.06, 0.02), (0, 0.0, 0.16), "hazard_yellow")
    for a in (0.785, 2.356, 3.927, 5.498):
        m.link((0.0, 0.0, 0.08), (0.25 * math.cos(a) + 0.0, 0.25 * math.sin(a), 0.08), 0.015, "copper")


@part("nozzle", "Exhaust Bell with Cooling Ribs")
def _(m, rng):
    m.cyl(0.6, 0.15, (0, 0.075, 0), "hull_dark", seg=16)
    m.cyl(0.18, 0.7, (0, 0.5, 0), "steel", seg=12, r2=0.14)
    m.cyl(0.14, 1.6, (0, 1.65, 0), "gunmetal", seg=16, r2=0.66)
    for k in range(10):
        a = 2 * PI * k / 10
        m.link((0.16 * math.cos(a), 1.0, 0.16 * math.sin(a)), (0.7 * math.cos(a), 2.42, 0.7 * math.sin(a)), 0.02, "steel", 4)
    for y, r in ((1.3, 0.3), (1.7, 0.4), (2.1, 0.55), (2.4, 0.65)):
        m.torus(r + 0.02, 0.03, (0, y, 0), "steel", seg=16, tseg=4)
    pass
    m.torus(0.66, 0.04, (0, 2.45, 0), "brass", seg=16, tseg=4)
    pass
    pipe(m, (0.18, 0.5, 0), (0.5, 0.25, 0.0), 0.05, "copper")


@part("nozzle", "Ion Drive Engine")
def _(m, rng):
    m.box((1.2, 0.1, 1.2), (0, 0.05, 0), "hull_dark", 0.01)
    m.cyl(0.4, 0.9, (0, 0.55, 0), "paint_white", seg=16)
    for y in (0.3, 0.5, 0.7, 0.9):
        m.torus(0.41, 0.02, (0, y, 0), "steel", seg=16, tseg=4)
    m.cyl(0.44, 0.5, (0, 1.25, 0), "hull_mid", seg=16, r2=0.5)
    m.cyl(0.5, 0.06, (0, 1.53, 0), "steel", seg=16)
    m.cyl(0.46, 0.02, (0, 1.57, 0), "black_metal", seg=16)
    for k in range(3):
        m.torus(0.15 + 0.13 * k, 0.012, (0, 1.6 + 0.015 * k, 0), "em_cyan" if k != 1 else "chrome", seg=14, tseg=4)
    m.cyl(0.05, 0.03, (0, 1.6, 0), "em_blue", seg=8)
    for k in range(4):
        a = PI / 2 * k + PI / 4
        m.cyl(0.05, 0.6, (0.5 * math.cos(a) * 0.9, 0.5, 0.5 * math.sin(a) * 0.9), "paint_navy", seg=8)
    pass
    m.box((0.3, 0.16, 0.02), (0, 0.25, 0.42), "plastic_white")


@part("nozzle", "Vectoring Nozzle")
def _(m, rng):
    m.box((1.5, 0.14, 1.2), (0, 0.07, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.14, 1.3, 0.3), (sx * 0.65, 0.75, 0), "hull_mid", 0.015)
        m.cyl(0.09, 0.14, (sx * 0.56, 1.2, 0), "chrome", axis="x", seg=10)
    pass
    m.cyl(0.4, 0.5, (0, 1.2, 0), "brushed_alu", axis="z", seg=14, r2=0.4, rot=(-0.35, 0, 0))
    pass
    m.cyl(0.42, 0.9, (0, 1.0, 0.55), "hull_mid", axis="z", seg=14, r2=0.6, rot=(-0.35, 0, 0))
    m.torus(0.6, 0.04, (0, 0.82, 0.95), "copper", axis="z", seg=14, tseg=4, rot=(-0.35, 0, 0))
    pass
    for sx in (-1, 1):
        m.link((sx * 0.4, 0.2, 0.35), (sx * 0.3, 1.0, 0.35), 0.035, "chrome")
        m.cyl(0.05, 0.5, (sx * 0.4, 0.45, 0.35), "steel", seg=8)
    pass
    m.box((0.2, 0.14, 0.04), (0, 0.24, 0.6), "black_metal")
    leds(m, -0.06, 0.06, 0.24, 0.63, ["em_green", "em_amber"], 0.03)


@part("nozzle", "Plasma Injector Nozzle", "wall")
def _(m, rng):
    m.box((0.8, 0.8, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    m.cyl(0.2, 0.4, (0, 0, 0.25), "hull_mid", axis="z", seg=14)
    for k in range(4):
        m.torus(0.21, 0.02, (0, 0, 0.12 + k * 0.1), "copper", axis="z", seg=14, tseg=4)
    m.cyl(0.1, 0.4, (0, 0, 0.62), "gunmetal", axis="z", seg=12, r2=0.06)
    m.cyl(0.05, 0.03, (0, 0, 0.83), "em_violet", axis="z", seg=8)
    m.torus(0.13, 0.015, (0, 0, 0.45), "em_violet", axis="z", seg=12, tseg=4)
    for a in (0.785, 2.356, 3.927, 5.498):
        m.link((0.3 * math.cos(a), 0.3 * math.sin(a), 0.05), (0.14 * math.cos(a), 0.14 * math.sin(a), 0.4), 0.025, "steel")
    bolts(m, [(-0.35, 0.35, 0.05), (0.35, 0.35, 0.05), (-0.35, -0.35, 0.05), (0.35, -0.35, 0.05)], mat="steel", axis="z")


@part("nozzle", "Gimbal Mount")
def _(m, rng):
    m.box((1.2, 0.14, 1.0), (0, 0.07, 0), "hull_dark", 0.01)
    m.cyl(0.1, 0.5, (0, 0.4, 0), "steel", seg=10, r2=0.14)
    for sx in (-1, 1):
        m.box((0.08, 0.7, 0.5), (sx * 0.5, 0.5, 0), "hull_mid", 0.01)
    m.torus(0.42, 0.05, (0, 0.95, 0), "brass", axis="x", seg=16, tseg=5)
    m.cyl(0.05, 1.0, (0, 0.95, 0), "chrome", axis="x", seg=6)
    m.torus(0.32, 0.045, (0, 0.95, 0), "gold_trim", axis="z", seg=14, tseg=5)
    m.cyl(0.22, 0.5, (0, 0.95, 0.0), "gunmetal", seg=12, r2=0.3)
    m.cyl(0.1, 0.3, (0, 1.3, 0), "gunmetal", seg=10, r2=0.06)
    m.link((0.35, 0.16, 0.3), (0.1, 0.85, 0.15), 0.03, "chrome")
    m.cyl(0.05, 0.4, (0.35, 0.3, 0.3), "steel", seg=8)
    m.link((-0.35, 0.16, 0.3), (-0.1, 0.85, 0.15), 0.03, "chrome")
    m.cyl(0.05, 0.4, (-0.35, 0.3, 0.3), "steel", seg=8)
    m.box((0.18, 0.05, 0.02), (0, 0.15, 0.51), "hazard_yellow")


@part("nozzle", "Quad RCS Block")
def _(m, rng):
    m.box((1.1, 0.1, 1.1), (0, 0.05, 0), "hull_dark", 0.01)
    m.box((0.5, 0.6, 0.5), (0, 0.4, 0), "paint_orange", 0.02)
    m.cyl(0.14, 0.2, (0, 0.8, 0), "steel", seg=10)
    m.sphere(0.14, (0, 0.9, 0), "steel", seg=10, ring=6)
    for sx, sz in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        a = math.atan2(sz, sx)
        m.link((sx * 0.25, 0.55, sz * 0.25), (sx * 0.45, 0.85, sz * 0.45), 0.05, "gunmetal")
        pass
        m.cyl(0.11, 0.1, (sx * 0.48, 0.9, sz * 0.48), "gunmetal", seg=10)
        m.cyl(0.05, 0.14, (sx * 0.48, 1.0, sz * 0.48), "black_metal", seg=10, r2=0.1)
        m.cyl(0.04, 0.02, (sx * 0.48, 0.96, sz * 0.48), "em_orange", seg=8)
    m.box((0.3, 0.06, 0.02), (0, 0.25, 0.26), "hazard_yellow")


# ================================================================ ENGTOOL (15)
@part("engtool", "Tool Rack", "wall")
def _(m, rng):
    m.box((1.4, 1.0, 0.03), (0, 0, 0.015), "hull_dark", 0.008)
    for y in (-0.3, 0.05, 0.4):
        m.box((1.3, 0.03, 0.06), (0, y, 0.06), "steel")
    tools = ["steel", "paint_red", "paint_blue", "paint_orange", "steel", "paint_red"]
    for k in range(9):
        x = -0.55 + k * 0.14
        h = 0.3 + 0.1 * (k % 3)
        m.box((0.03, h, 0.03), (x, 0.4 - h / 2 + 0.02, 0.1), "steel")
        m.box((0.05, 0.12, 0.035), (x, 0.4 - h + 0.05, 0.1), tools[k % 6], 0.004)
    for k in range(6):
        x = -0.5 + k * 0.2
        m.box((0.06, 0.28, 0.04), (x, -0.06, 0.1), "black_metal", 0.004)
        m.box((0.045, 0.14, 0.05), (x, 0.05, 0.1), tools[(k + 2) % 6], 0.004)
    for k in range(4):
        m.cyl(0.05, 0.05, (-0.45 + k * 0.3, -0.42, 0.11), "steel", axis="z", seg=8)
        m.cyl(0.03, 0.055, (-0.45 + k * 0.3, -0.42, 0.11), "black_metal", axis="z", seg=6)
    m.box((1.4, 0.05, 0.14), (0, -0.52, 0.09), "paint_red", 0.006)


@part("engtool", "Rolling Toolbox")
def _(m, rng):
    m.box((0.8, 0.9, 0.5), (0, 0.6, 0), "paint_red", 0.02)
    m.box((0.82, 0.08, 0.52), (0, 1.09, 0), "hull_dark", 0.01)
    for k in range(4):
        y = 0.27 + k * 0.19
        m.box((0.7, 0.16, 0.02), (0, y + 0.1, 0.255), "paint_red" if k % 2 else "hull_dark", 0.006)
        m.box((0.3, 0.03, 0.03), (0, y + 0.14, 0.275), "chrome")
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.07, 0.05, (sx * 0.33, 0.07, sz * 0.2), "rubber", axis="z", seg=8)
            m.box((0.04, 0.06, 0.04), (sx * 0.33, 0.13, sz * 0.2), "steel")
    m.box((0.78, 0.06, 0.48), (0, 0.16, 0), "black_metal")
    m.box((0.1, 0.07, 0.02), (0.3, 1.0, 0.26), "hazard_yellow")


@part("engtool", "Cable Reel")
def _(m, rng):
    m.box((0.8, 0.06, 0.7), (0, 0.03, 0), "hull_dark", 0.008)
    for sz in (-1, 1):
        m.box((0.06, 0.9, 0.06), (0.0, 0.5, sz * 0.32), "steel")
        m.cyl(0.4, 0.05, (0, 0.6, sz * 0.2), "paint_orange", axis="z", seg=16)
    m.cyl(0.36, 0.3, (0, 0.6, 0.0), "rubber", axis="z", seg=16)
    pass
    m.torus(0.3, 0.05, (0, 0.6, 0), "paint_orange", axis="z", seg=14, tseg=4)
    m.cyl(0.08, 0.5, (0, 0.6, 0.0), "chrome", axis="z", seg=8)
    pass
    m.tube([(0.34, 0.5, 0.0), (0.5, 0.2, 0.2), (0.7, 0.05, 0.3)], 0.025, "rubber", seg=5)
    m.box((0.1, 0.1, 0.06), (0.73, 0.05, 0.3), "paint_red", 0.01)
    pass
    pass


@part("engtool", "Welding Rig")
def _(m, rng):
    m.box((0.9, 0.08, 0.6), (0, 0.24, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.cyl(0.12, 0.07, (sx * 0.4, 0.13, 0.3), "rubber", axis="z", seg=10)
    pass
    m.box((0.5, 0.5, 0.35), (0.15, 0.53, 0), "paint_orange", 0.02)
    m.box((0.5, 0.06, 0.37), (0.15, 0.8, 0), "hull_dark", 0.01)
    for k in range(3):
        m.cyl(0.03, 0.03, (0.0 + k * 0.15, 0.55, 0.19), "chrome", axis="z", seg=8)
    leds(m, 0.05, 0.3, 0.7, 0.18, ["em_green", "em_amber"], 0.03)
    m.cyl(0.12, 1.0, (-0.28, 0.78, 0.0), "paint_green", seg=10)
    m.sphere(0.12, (-0.28, 1.28, 0), "paint_green", seg=10, ring=5, scale=(1, 0.7, 1))
    m.cyl(0.13, 0.1, (-0.28, 1.0, 0), "paint_white", seg=10)
    m.cyl(0.03, 0.1, (-0.28, 1.4, 0), "brass", seg=6)
    pass
    m.tube([(0.4, 0.5, 0.0), (0.55, 0.3, 0.15), (0.7, 0.2, 0.25)], 0.02, "rubber", seg=5)
    m.link((0.7, 0.2, 0.25), (0.78, 0.35, 0.3), 0.025, "copper")
    pass


@part("engtool", "Spare Parts Bin")
def _(m, rng):
    pass
    for sx in (-1, 1):
        m.box((0.05, 0.85, 0.5), (sx * 0.4, 0.42, 0), "steel")
    m.box((0.85, 0.05, 0.5), (0, 0.03, 0), "hull_dark")
    for y in (0.3, 0.62):
        m.box((0.85, 0.03, 0.5), (0, y, 0), "hull_mid")
    for row, y in enumerate((0.08, 0.35, 0.67)):
        for k in range(3):
            x = -0.27 + k * 0.27
            m.box((0.22, 0.17, 0.4), (x, y + 0.09, 0.03), ["paint_blue", "paint_red", "paint_green", "paint_orange"][(row + k) % 4], 0.008)
            m.box((0.14, 0.05, 0.005), (x, y + 0.12, 0.235), "plastic_white")
            pass
    m.box((0.85, 0.05, 0.5), (0, 0.9, 0), "hull_dark", 0.005)


@part("engtool", "Work Bench with Vise")
def _(m, rng):
    m.box((1.8, 0.06, 0.8), (0, 0.9, 0), "wood_dark", 0.006)
    pass
    for sx in (-1, 1):
        m.box((0.06, 0.88, 0.7), (sx * 0.85, 0.44, 0), "hull_dark")
    m.box((1.7, 0.05, 0.05), (0, 0.15, 0.3), "hull_dark")
    m.box((1.7, 0.05, 0.05), (0, 0.15, -0.3), "hull_dark")
    m.box((1.7, 0.04, 0.7), (0, 0.24, 0), "hull_mid")
    # vise
    m.box((0.24, 0.14, 0.2), (0.55, 1.03, 0.3), "paint_blue", 0.01)
    m.box((0.2, 0.1, 0.06), (0.55, 1.13, 0.2), "steel")
    m.box((0.2, 0.1, 0.06), (0.55, 1.12, 0.38), "steel")
    m.cyl(0.015, 0.25, (0.55, 1.08, 0.5), "chrome", axis="z", seg=5)
    m.link((0.42, 1.08, 0.62), (0.68, 1.08, 0.62), 0.012, "chrome", 4)
    # back rail + tools
    pass
    m.box((0.3, 0.06, 0.2), (-0.5, 0.96, 0.0), "paint_red", 0.005)
    m.cyl(0.05, 0.03, (-0.2, 0.975, 0.1), "steel", seg=8)
    m.box((0.2, 0.03, 0.12), (0.0, 0.945, -0.1), "hazard_yellow")
    m.box((1.8, 0.08, 0.05), (0, 0.98, -0.4), "hull_dark")


@part("engtool", "Diagnostic Cart")
def _(m, rng):
    m.box((0.7, 0.05, 0.5), (0, 0.22, 0), "hull_dark", 0.008)
    m.box((0.7, 0.05, 0.5), (0, 0.65, 0), "hull_mid", 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.02, 0.62, (sx * 0.32, 0.5, sz * 0.22), "steel", seg=5)
            m.cyl(0.06, 0.04, (sx * 0.32, 0.06, sz * 0.22), "rubber", axis="x", seg=8)
    pass
    m.cyl(0.03, 0.8, (0.0, 1.05, -0.2), "steel", seg=6)
    m.box((0.6, 0.4, 0.05), (0, 1.5, -0.2), "black_metal", 0.01, rot=(-0.25, 0, 0))
    m.screen((0.5, 0.3), (0, 1.5, -0.17), "diagnostic", rot=(-0.25, 0, 0), bezel=0.01)
    pass
    m.box((0.4, 0.12, 0.3), (0.0, 0.73, 0.05), "paint_orange", 0.012)
    leds(m, -0.12, 0.12, 0.76, 0.21, ["em_green", "em_amber", "em_cyan"], 0.03)
    m.tube([(0.2, 0.7, 0.2), (0.3, 0.45, 0.28), (0.1, 0.35, 0.28)], 0.012, "rubber", seg=4)
    m.box((0.5, 0.1, 0.3), (0, 0.32, 0.0), "paint_grey", 0.01)
    pass


@part("engtool", "Chain Hoist Gantry")
def _(m, rng):
    for sx in (-1, 1):
        m.box((0.1, 0.06, 0.9), (sx * 0.8, 0.03, 0), "hull_dark")
        m.box((0.08, 2.2, 0.08), (sx * 0.8, 1.13, 0.3), "hazard_yellow", 0.006)
        m.box((0.08, 2.2, 0.08), (sx * 0.8, 1.13, -0.3), "hazard_yellow", 0.006)
        m.link((sx * 0.8, 0.5, 0.3), (sx * 0.8, 1.6, -0.3), 0.02, "steel", 4)
    m.box((1.8, 0.16, 0.14), (0, 2.28, 0), "steel", 0.01)
    m.box((0.22, 0.2, 0.24), (0.1, 2.12, 0), "paint_red", 0.015)
    m.cyl(0.08, 0.28, (0.1, 2.0, 0), "gunmetal", axis="z", seg=10)
    for k in range(6):
        m.box((0.03, 0.025, 0.012), (0.1, 1.95 - k * 0.09, 0.0), "steel")
        m.box((0.012, 0.025, 0.03), (0.1, 1.9 - k * 0.09, 0.0), "steel")
    m.link((0.1, 1.9, 0.0), (0.1, 1.35, 0.0), 0.015, "chrome", 4)
    m.torus(0.06, 0.015, (0.1, 1.28, 0), "steel", axis="z", seg=10, tseg=4)
    m.box((0.06, 0.05, 0.05), (0.1, 1.2, 0), "hazard_yellow")
    pass
    m.box((1.8, 0.04, 0.02), (0, 2.28, 0.08), "hazard_yellow")


@part("engtool", "Oxy Torch Cart")
def _(m, rng):
    m.box((0.6, 0.06, 0.5), (0, 0.16, 0), "hull_dark", 0.008)
    for sx in (-1, 1):
        m.cyl(0.14, 0.05, (sx * 0.25, 0.14, 0.27), "rubber", axis="z", seg=10)
        m.cyl(0.14, 0.05, (sx * 0.25, 0.14, -0.27), "rubber", axis="z", seg=10)
    for x, mt in ((-0.14, "paint_green"), (0.14, "paint_red")):
        m.cyl(0.1, 1.05, (x, 0.72, -0.05), mt, seg=10)
        m.sphere(0.1, (x, 1.25, -0.05), mt, seg=10, ring=5, scale=(1, 0.8, 1))
        m.cyl(0.03, 0.08, (x, 1.32, -0.05), "brass", seg=6)
        pass
    m.box((0.35, 0.05, 0.05), (0, 1.0, 0.1), "steel")
    m.box((0.05, 0.9, 0.05), (0, 0.6, 0.22), "steel")
    m.link((0.3, 0.19, -0.27), (0.5, 1.0, -0.27), 0.015, "steel", 4)
    m.link((0.3, 0.19, 0.27), (0.5, 1.0, 0.27), 0.015, "steel", 4)
    m.link((0.5, 1.0, -0.27), (0.5, 1.0, 0.27), 0.02, "rubber", 5)
    m.tube([(0.1, 1.3, 0.05), (0.2, 1.1, 0.3), (0.42, 0.9, 0.2)], 0.012, "rubber", seg=4)
    pass
    hazard(m, -0.28, 0.28, 0.06, 0.14, 0.26, n=6)


@part("engtool", "Tool Wall Board", "wall")
def _(m, rng):
    m.box((1.6, 1.0, 0.03), (0, 0, 0.015), "wood_light", 0.008)
    m.box((1.66, 0.05, 0.05), (0, 0.5, 0.03), "hull_dark")
    m.box((1.66, 0.05, 0.05), (0, -0.5, 0.03), "hull_dark")
    for sx in (-1, 1):
        m.box((0.05, 1.06, 0.05), (sx * 0.83, 0, 0.03), "hull_dark")
    outline = ["paint_red", "steel", "paint_blue", "paint_orange", "paint_green", "steel", "paint_red", "paint_blue"]
    for k in range(8):
        x = -0.62 + k * 0.18
        m.box((0.13, 0.36 if k % 2 else 0.5, 0.008), (x, 0.15 if k % 2 else 0.08, 0.034), "plastic_white")
        m.box((0.04, 0.3 if k % 2 else 0.44, 0.03), (x, 0.15 if k % 2 else 0.08, 0.05), outline[k], 0.004)
        pass
    for k in range(6):
        m.cyl(0.03, 0.06, (-0.5 + k * 0.2, -0.32, 0.07), "steel", axis="z", seg=8)
    m.box((1.4, 0.04, 0.09), (0, -0.4, 0.075), "paint_red", 0.006)


@part("engtool", "Jack Stands")
def _(m, rng):
    for j, x in enumerate((-0.35, 0.35)):
        h = 0.45 + 0.1 * j
        pass
        m.box((0.5, 0.04, 0.05), (x, 0.02, 0.2), "paint_red")
        m.box((0.5, 0.04, 0.05), (x, 0.02, -0.2), "paint_red")
        m.box((0.05, 0.04, 0.4), (x + 0.22, 0.02, 0), "paint_red")
        m.box((0.05, 0.04, 0.4), (x - 0.22, 0.02, 0), "paint_red")
        m.link((x - 0.2, 0.04, 0.18), (x, h, 0), 0.02, "paint_red", 4)
        m.link((x + 0.2, 0.04, 0.18), (x, h, 0), 0.02, "paint_red", 4)
        m.link((x - 0.2, 0.04, -0.18), (x, h, 0), 0.02, "paint_red", 4)
        m.link((x + 0.2, 0.04, -0.18), (x, h, 0), 0.02, "paint_red", 4)
        pass
        m.cyl(0.04, 0.35, (x, h, 0), "chrome", seg=6)
        m.cyl(0.1, 0.03, (x, h + 0.18, 0), "steel", seg=8)
        m.box((0.04, 0.06, 0.03), (x, h + 0.02, 0.06), "black_metal")
    pass


@part("engtool", "Portable Work Light")
def _(m, rng):
    for a in (0.5, 2.6, 4.7):
        m.link((0, 0.85, 0), (0.4 * math.cos(a), 0.02, 0.4 * math.sin(a)), 0.015, "steel", 5)
        m.cyl(0.03, 0.03, (0.4 * math.cos(a), 0.015, 0.4 * math.sin(a)), "rubber", seg=6)
    m.cyl(0.03, 0.7, (0, 1.2, 0), "chrome", seg=8)
    m.cyl(0.05, 0.1, (0, 0.85, 0), "black_metal", seg=8)
    m.cyl(0.045, 0.06, (0, 1.53, 0), "hazard_yellow", seg=8)
    m.box((0.5, 0.35, 0.1), (0, 1.75, 0), "hazard_yellow", 0.015, rot=(-0.15, 0, 0))
    m.box((0.44, 0.29, 0.02), (0, 1.75, 0.06), "em_white", rot=(-0.15, 0, 0))
    m.box((0.5, 0.03, 0.06), (0, 1.94, 0.02), "black_metal", rot=(-0.15, 0, 0))
    pass
    pass


@part("engtool", "Creeper Board")
def _(m, rng):
    m.box((0.5, 0.05, 1.0), (0, 0.13, 0), "paint_orange", 0.015)
    m.box((0.46, 0.06, 0.6), (0, 0.18, 0.15), "leather_black", 0.02)
    m.box((0.36, 0.08, 0.2), (0, 0.18, -0.35), "leather_black", 0.02)
    for sx in (-1, 1):
        for z in (-0.4, 0.0, 0.4):
            m.cyl(0.045, 0.03, (sx * 0.2, 0.05, z), "rubber", axis="x", seg=8)
            m.box((0.04, 0.05, 0.05), (sx * 0.2, 0.09, z), "steel")
    pass
    m.box((0.46, 0.04, 0.05), (0, 0.16, -0.5), "hazard_yellow")
    m.box((0.46, 0.04, 0.05), (0, 0.16, 0.5), "hazard_yellow")


@part("engtool", "Hand Tool Set", "table")
def _(m, rng):
    m.box((0.5, 0.03, 0.3), (0, 0.015, 0), "wood_dark", 0.004)
    m.box((0.3, 0.02, 0.03), (-0.05, 0.04, -0.09), "steel")
    m.box((0.08, 0.025, 0.045), (0.12, 0.04, -0.09), "paint_red", 0.004)
    m.link((-0.2, 0.04, 0.0), (0.2, 0.04, 0.0), 0.012, "paint_orange", 5)
    m.box((0.1, 0.03, 0.05), (0.22, 0.04, 0.0), "steel", 0.004)
    m.cyl(0.05, 0.05, (-0.15, 0.055, 0.09), "chrome", seg=8)
    m.cyl(0.03, 0.06, (-0.15, 0.055, 0.09), "black_metal", seg=6)
    for k in range(4):
        m.link((0.0 + k * 0.04, 0.035, 0.1), (0.05 + k * 0.04, 0.035, 0.2), 0.008, ["paint_blue", "paint_green", "paint_red", "paint_orange"][k], 4)
    m.box((0.14, 0.06, 0.06), (0.0, 0.06, 0.06), "paint_orange", 0.008)


@part("engtool", "Wall Parts Bins", "wall")
def _(m, rng):
    m.box((1.3, 0.9, 0.03), (0, 0, 0.015), "hull_dark", 0.008)
    m.box((1.3, 0.05, 0.12), (0, 0.42, 0.07), "steel")
    cols = ["paint_blue", "paint_red", "paint_green", "paint_orange", "paint_teal"]
    for r in range(3):
        m.box((1.3, 0.03, 0.15), (0, -0.4 + r * 0.3 - 0.0, 0.1), "steel")
        for k in range(5):
            x = -0.5 + k * 0.25
            m.box((0.2, 0.2, 0.16), (x, -0.27 + r * 0.3, 0.11), cols[(r + k) % 5], 0.008)
            m.box((0.16, 0.05, 0.01), (x, -0.23 + r * 0.3, 0.195), "plastic_white")
            m.box((0.1, 0.02, 0.02), (x, -0.31 + r * 0.3, 0.2), "black_metal")


# ================================================================ registration
def _lod(m, cyl=12, tor=14, tt=5, sph=10, link=5):
    o_cyl, o_tor, o_sph, o_link = m.cyl, m.torus, m.sphere, m.link

    def cy(r, h, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=16, **k):
        return o_cyl(r, h, pos, mat, axis=axis, seg=min(seg, cyl), **k)

    def to(R, r, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=24, tseg=8, **k):
        return o_tor(R, r, pos, mat, axis=axis, seg=min(seg, tor), tseg=min(tseg, tt), **k)

    def sp(r, pos=(0, 0, 0), mat="hull_mid", seg=16, ring=10, scale=(1, 1, 1)):
        return o_sph(r, pos, mat, min(seg, sph), min(ring, max(4, sph // 2)), scale)

    def li(a, b, r, mat="steel", seg=8):
        return o_link(a, b, r, mat, min(seg, link))
    m.cyl, m.torus, m.sphere, m.link = cy, to, sp, li


HERO = {"Fusion Core Reactor": (16, 16, 5, 8), "Plasma Tokamak Torus": (16, 24, 6, 10)}


def _register():
    groups = {}
    for key in ORDER:
        fn, mount, solid, my = PARTS[key]
        groups.setdefault((key[0], mount, solid, my), []).append(key[1])
    for (cat, mount, solid, my), labels in groups.items():
        def gen(m, i, label, rng, _cat=cat):
            c = HERO.get(label)
            _lod(m, c[0], c[1], c[2], c[3]) if c else _lod(m)
            PARTS[(_cat, label)][0](m, rng)
        gen.__module__ = __name__
        kit.family(cat, labels, mount=mount, tags=["engineering"], solid=solid, mount_y=my)(gen)


_register()
