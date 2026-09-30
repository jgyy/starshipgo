"""Bridge / command-deck furniture and electronics (100 labels).

Categories: console(20) seat(8) display(22) controlpanel(20) holo(8) terminal(12) instrument(10).
"""
import math

from ..kit import family
try:  # bpy is optional so `build_all.py --check` runs on a bare Python
    from mathutils import Euler, Vector  # noqa: E402 (after kit imports bpy)
except ImportError:
    Euler = Vector = None

PI = math.pi
BTN = ["em_red", "em_green", "em_amber", "em_cyan", "plastic_grey", "em_white", "plastic_black", "em_blue"]


# ---------------------------------------------------------------- helpers
def _n(rot):
    return Euler(rot, "XYZ").to_matrix() @ Vector((0, 0, 1))


def mon(m, w, h, pos, tex, rot=(0, 0, 0), b=0.02, depth=0.04, frame="black_metal", bev=0.006):
    """Monitor: bezel box behind an emissive screen quad. pos = screen centre."""
    n = _n(rot)
    c = Vector(pos) - n * (depth / 2 + 0.001)
    m.box((w + 2 * b, h + 2 * b, depth), tuple(c), frame, min(bev, depth * 0.4), rot)
    m.quad((w, h), pos, "screen:" + tex, rot)


def yaw(pt, ry):
    x, y, z = pt
    return (x * math.cos(ry) + z * math.sin(ry), y, -x * math.sin(ry) + z * math.cos(ry))


def hazard(m, x0, x1, y, z, hgt=0.04, dz=0.006, n=None, mat="hazard_yellow"):
    """Hazard stripe band along X on a front (+Z facing) surface."""
    m.box((x1 - x0, hgt, dz), ((x0 + x1) / 2, y, z), mat)
    n = n or max(3, int((x1 - x0) / 0.06))
    step = (x1 - x0) / n
    for k in range(n):
        if k % 2 == 0:
            m.box((step * 0.6, hgt * 1.02, dz * 1.4), (x0 + step * (k + 0.5), y, z), "black_metal", 0, (0, 0, 0.6))


def bolts(m, pts, r=0.008, mat="steel", axis="z", h=0.008):
    for p in pts:
        m.cyl(r, h, p, mat, axis=axis, seg=6)


def joystick(m, pos, base="black_metal", knob="plastic_grey"):
    x, y, z = pos
    m.cyl(0.05, 0.035, (x, y + 0.012, z), base, seg=14, bevel=0.005)
    m.cyl(0.032, 0.05, (x, y + 0.05, z), "rubber", seg=10, r2=0.018)
    m.cyl(0.013, 0.11, (x, y + 0.12, z), "gunmetal", seg=8)
    m.sphere(0.03, (x, y + 0.2, z), knob, seg=10, ring=6, scale=(1, 1.15, 1))
    m.box((0.014, 0.014, 0.014), (x, y + 0.222, z + 0.02), "em_red")


def lever(m, pos, tilt=-0.5, length=0.16, knob="paint_red", base="black_metal", axis_len=0.1):
    x, y, z = pos
    m.box((0.05, 0.03, 0.05 + axis_len), (x, y + 0.015, z), base, 0.004)
    p0 = (x, y + 0.03, z)
    p1 = (x, y + 0.03 + length * math.cos(tilt), z + length * math.sin(tilt))
    m.link(p0, p1, 0.009, "steel", 8)
    m.sphere(0.024, p1, knob, seg=10, ring=6)


class Desk:
    """Floor console body: side-profile prism with a sloped working panel."""

    def __init__(s, m, w=1.6, d=0.9, yf=0.9, yb=1.02, bk=0.25, body="hull_mid", trim="em_cyan",
                 plate="gunmetal", x=0.0):
        s.m, s.w, s.d, s.x, s.yb, s.yf = m, w, d, x, yb, yf
        zb, zf = -d / 2 + bk, d / 2
        s.zb, s.zf = zb, zf
        s.a = math.atan2(yb - yf, zf - zb)
        s.cy, s.cz = (yb + yf) / 2, (zb + zf) / 2
        s.L = math.hypot(zf - zb, yb - yf)
        pts = [(-d / 2, 0), (d / 2 - 0.12, 0), (d / 2 - 0.12, 0.1), (d / 2, 0.1), (d / 2, yf), (zb, yb), (-d / 2, yb)]
        m.prism(pts, w, (x - w / 2, 0, 0), body, plane="zy", bevel=0.01)
        m.box((w - 0.02, 0.1, 0.02), (x, 0.05, d / 2 - 0.11), "black_metal")
        if trim:
            m.box((w - 0.12, 0.012, 0.012), (x, 0.065, d / 2 - 0.118), trim)
            m.box((w - 0.12, 0.014, 0.014), s.p(0, s.L / 2 - 0.012, 0.007), trim, 0, (s.a, 0, 0))
        m.box((w - 0.14, 0.012, s.L - 0.1), s.p(0, -0.01, 0.006), plate, 0.003, (s.a, 0, 0))
        n = max(1, int(w / 0.55))
        for k in range(1, n):
            xx = x - w / 2 + w * k / n
            m.box((0.008, yf - 0.26, 0.006), (xx, 0.1 + (yf - 0.1) / 2 - 0.02, d / 2 + 0.001), "black_metal")
        # side kick plates
        for sx in (-1, 1):
            m.box((0.012, yb - 0.2, d - 0.3), (x + sx * (w / 2 + 0.002), yb / 2 + 0.05, -0.03), "hull_dark", 0.004)

    def p(s, u, sl, off=0.0):
        a = s.a
        return (s.x + u, s.cy - sl * math.sin(a) + off * math.cos(a), s.cz + sl * math.cos(a) + off * math.sin(a))

    def btn(s, u, sl, mat="em_green", sz=(0.03, 0.03), h=0.012):
        s.m.box((sz[0], h, sz[1]), s.p(u, sl, 0.006 + h / 2), mat, 0, (s.a, 0, 0))

    def grid(s, u0, s0, nu, ns, pu=0.045, ps=0.045, rng=None, mats=BTN, sz=0.03):
        k = 0
        for i in range(nu):
            for j in range(ns):
                mm = mats[(k + (rng.randrange(len(mats)) if rng else 0)) % len(mats)]
                s.btn(u0 + i * pu, s0 + j * ps, mm, (sz, sz))
                k += 1

    def dial(s, u, sl, r=0.035, mat="chrome", dot="em_white"):
        s.m.cyl(r, 0.02, s.p(u, sl, 0.016), "black_metal", seg=14, rot=(s.a, 0, 0))
        s.m.cyl(r * 0.8, 0.01, s.p(u, sl, 0.026), mat, seg=14, rot=(s.a, 0, 0))
        s.m.box((0.006, 0.006, r * 0.7), s.p(u, sl + r * 0.35, 0.033), dot, 0, (s.a, 0, 0))

    def slider(s, u, sl, ln=0.16, k=0.5, mat="em_amber", horiz=False):
        if horiz:
            s.m.box((ln, 0.006, 0.012), s.p(u, sl, 0.009), "black_metal", 0, (s.a, 0, 0))
            s.m.box((0.022, 0.016, 0.03), s.p(u - ln / 2 + ln * k, sl, 0.014), mat, 0.002, (s.a, 0, 0))
        else:
            s.m.box((0.012, 0.006, ln), s.p(u, sl, 0.009), "black_metal", 0, (s.a, 0, 0))
            s.m.box((0.03, 0.016, 0.022), s.p(u, sl - ln / 2 + ln * k, 0.014), mat, 0.002, (s.a, 0, 0))

    def scr(s, u, sl, w, h, tex):
        a = s.a
        s.m.box((w + 0.03, 0.02, h + 0.03), s.p(u, sl, 0.012), "black_metal", 0.004, (a, 0, 0))
        s.m.quad((w, h), s.p(u, sl, 0.0225), "screen:" + tex, (a - PI / 2, 0, 0))

    def up(s, u, w, h, tex, tilt=0.28, y=None, z=None, ry=0.0):
        y0 = (s.yb if y is None else y) + 0.06
        zz = (-s.d / 2 + 0.12) if z is None else z
        s.m.box((0.07, 0.1, 0.05), (s.x + u, y0 - 0.01, zz - 0.02), "hull_dark", 0.005)
        mon(s.m, w, h, (s.x + u, y0 + h / 2 + 0.02, zz + 0.02), tex, (-tilt, ry, 0))

    def riser(s, w):  # rear gantry behind the working surface
        s.m.box((w, 0.03, 0.08), (s.x, s.yb + 0.015, -s.d / 2 + 0.06), "hull_dark", 0.005)


# ---------------------------------------------------------------- consoles
def c_helm(m, rng):
    d = Desk(m, 1.7, 0.9, 0.9, 1.0, 0.25, "hull_mid", "em_cyan")
    d.scr(-0.52, 0.02, 0.34, 0.24, "nav")
    d.scr(0.52, 0.02, 0.34, 0.24, "radar")
    joystick(m, d.p(0.0, 0.1, 0.0))
    lever(m, d.p(-0.18, 0.12), -0.6, 0.15, "paint_orange")
    lever(m, d.p(0.18, 0.12), -0.6, 0.15, "paint_orange")
    d.grid(-0.75, -0.2, 3, 2, rng=rng)
    d.grid(0.6, -0.2, 3, 2, rng=rng)
    d.up(0, 0.9, 0.34, "nav", 0.25)


def c_navigation(m, rng):
    d = Desk(m, 1.9, 0.9, 0.88, 0.98, 0.2, "hull_light", "em_blue", "hull_dark")
    d.scr(0.0, 0.0, 0.7, 0.4, "starmap")
    d.scr(-0.72, 0.05, 0.3, 0.22, "nav")
    d.scr(0.72, 0.05, 0.3, 0.22, "text")
    for k in range(4):
        d.dial(-0.35 + k * 0.23, 0.26, 0.032)
    m.sphere(0.04, d.p(0.5, 0.26, 0.03), "chrome", seg=10, ring=6)
    m.torus(0.048, 0.008, d.p(0.5, 0.26, 0.012), "black_metal", "y", 14, 6, rot=(d.a, 0, 0))
    d.up(-0.45, 0.55, 0.32, "starmap", 0.3)
    d.up(0.45, 0.55, 0.32, "nav", 0.3)


def c_ops(m, rng):
    d = Desk(m, 2.1, 0.85, 0.9, 1.0, 0.22, "hull_mid", "em_amber")
    for k, tex in enumerate(["systems", "power", "diagnostic"]):
        d.scr(-0.65 + k * 0.65, 0.0, 0.5, 0.3, tex)
    d.grid(-0.9, 0.22, 8, 2, 0.06, 0.05, rng)
    # overhead arch frame carrying two screens
    for sx in (-1, 1):
        m.box((0.05, 0.5, 0.05), (sx * 1.0, 1.25, -0.32), "hull_dark", 0.005)
    m.box((2.05, 0.05, 0.06), (0, 1.5, -0.32), "hull_dark", 0.008)
    mon(m, 0.7, 0.32, (-0.5, 1.3, -0.28), "systems", (-0.15, 0.25, 0))
    mon(m, 0.7, 0.32, (0.5, 1.3, -0.28), "bars", (-0.15, -0.25, 0))


def c_tactical(m, rng):
    d = Desk(m, 1.8, 0.95, 0.92, 1.02, 0.25, "hull_dark", "em_red", "black_metal")
    d.scr(0.0, -0.02, 0.62, 0.36, "tactical")
    d.scr(-0.68, 0.03, 0.28, 0.2, "alert")
    for k in range(3):
        m.box((0.05, 0.03, 0.05), d.p(0.6 + k * 0.1, 0.18, 0.02), "hazard_yellow", 0.004, (d.a, 0, 0))
        m.box((0.038, 0.014, 0.038), d.p(0.6 + k * 0.1, 0.18, 0.04), "paint_red", 0.003, (d.a, 0, 0))
    d.grid(-0.5, 0.24, 6, 1, 0.055, 0.05, rng, ["em_red", "em_amber", "plastic_black"])
    d.up(0, 1.0, 0.36, "tactical", 0.3)
    m.sphere(0.03, (0.85, 1.08, -0.4), "em_red", seg=10, ring=6)
    m.cyl(0.04, 0.05, (0.85, 1.03, -0.4), "black_metal", seg=10)


def c_science(m, rng):
    d = Desk(m, 1.5, 0.9, 0.9, 1.0, 0.22, "hull_light", "em_cyan", "plastic_grey")
    # sensor hood
    m.box((0.5, 0.04, 0.4), (-0.35, 1.02, -0.05), "hull_dark", 0.006)
    m.box((0.02, 0.28, 0.4), (-0.6, 1.16, -0.05), "hull_dark", 0.005)
    m.box((0.02, 0.28, 0.4), (-0.1, 1.16, -0.05), "hull_dark", 0.005)
    m.box((0.5, 0.28, 0.02), (-0.35, 1.16, -0.25), "hull_dark", 0.005)
    m.box((0.5, 0.03, 0.4), (-0.35, 1.32, -0.05), "hull_mid", 0.006)
    m.quad((0.44, 0.24), (-0.35, 1.16, -0.238), "screen:waveform")
    d.scr(0.3, 0.02, 0.45, 0.28, "graph")
    d.scr(-0.05, 0.22, 0.2, 0.12, "text")
    for k in range(3):
        d.dial(0.1 + k * 0.1, 0.24, 0.028)
    m.cyl(0.04, 0.03, d.p(0.6, 0.12, 0.02), "ceramic", seg=12)  # sample dish
    m.cyl(0.03, 0.01, d.p(0.6, 0.12, 0.04), "glass", seg=12)
    d.up(0.5, 0.42, 0.26, "periodic", 0.3)


def c_engineering(m, rng):
    d = Desk(m, 1.8, 0.85, 0.9, 1.0, 0.2, "hull_mid", "em_orange", "gunmetal")
    hazard(m, -0.85, 0.85, 0.12, d.d / 2 + 0.003, 0.05)
    for k in range(6):
        d.slider(-0.7 + k * 0.13, 0.0, 0.34, rng.random(), rng.choice(["em_green", "em_amber", "em_orange"]))
    d.scr(0.42, -0.04, 0.4, 0.28, "power")
    d.grid(0.15, 0.2, 3, 1, 0.05, 0.05, rng)
    d.up(-0.5, 0.36, 0.5, "bars", 0.15)
    d.up(0.0, 0.36, 0.5, "power", 0.15)
    d.up(0.5, 0.36, 0.5, "systems", 0.15)


def c_comms(m, rng):
    d = Desk(m, 1.4, 0.8, 0.88, 0.98, 0.2, "hull_light", "em_green", "hull_dark")
    d.scr(-0.25, 0.0, 0.5, 0.3, "comm")
    d.scr(0.42, 0.05, 0.3, 0.2, "waveform")
    for k in range(3):
        d.dial(-0.6 + k * 0.1, 0.24, 0.03)
    d.grid(0.3, 0.22, 4, 1, 0.055, 0.05, rng)
    # gooseneck mic
    m.cyl(0.03, 0.03, d.p(0.6, 0.25, 0.015), "black_metal", seg=10)
    m.tube([d.p(0.6, 0.25, 0.03), (d.x + 0.6, 1.15, 0.08), (d.x + 0.55, 1.28, 0.15)], 0.007, "black_metal", 6)
    m.sphere(0.02, (d.x + 0.55, 1.28, 0.16), "plastic_black", seg=8, ring=6)
    # headset hooks on the side
    m.box((0.05, 0.03, 0.05), (0.72, 0.85, 0.0), "black_metal", 0.004)
    m.torus(0.05, 0.008, (0.77, 0.8, 0.0), "plastic_black", "x", 14, 6, arc=PI)
    d.up(0.0, 0.7, 0.3, "comm", 0.28)


def c_flightcontrol(m, rng):
    d = Desk(m, 1.6, 0.95, 0.88, 0.98, 0.3, "hull_dark", "em_blue", "black_metal")
    # central yoke column
    m.cyl(0.06, 0.25, (0, 1.05, 0.05), "hull_mid", seg=12, r2=0.045)
    m.box((0.6, 0.05, 0.05), (0, 1.2, 0.1), "black_metal", 0.008)
    for sx in (-1, 1):
        m.link((sx * 0.3, 1.2, 0.1), (sx * 0.3, 1.36, 0.06), 0.02, "rubber", 8)
        m.box((0.03, 0.03, 0.03), (sx * 0.3, 1.38, 0.05), "em_red")
    m.torus(0.08, 0.012, (0, 1.2, 0.1), "chrome", "z", 16, 6)
    d.scr(-0.6, 0.0, 0.36, 0.25, "nav")
    d.scr(0.6, 0.0, 0.36, 0.25, "diagnostic")
    lever(m, d.p(-0.28, 0.25), -0.7, 0.16, "paint_navy")
    lever(m, d.p(-0.20, 0.25), -0.7, 0.16, "paint_navy")
    lever(m, d.p(0.24, 0.25), -0.7, 0.16, "paint_red")
    d.up(0, 0.6, 0.3, "systems", 0.35, y=1.0)


def c_sensor(m, rng):
    d = Desk(m, 1.6, 0.85, 0.9, 1.0, 0.2, "hull_mid", "em_violet", "gunmetal")
    d.scr(-0.35, 0.0, 0.5, 0.3, "radar")
    d.scr(0.35, 0.0, 0.5, 0.3, "waveform")
    d.grid(-0.7, 0.24, 6, 1, 0.05, 0.05, rng, ["em_violet", "em_cyan", "plastic_grey"])
    # miniature dish on the deck top
    m.cyl(0.03, 0.15, (0.65, 1.08, -0.3), "steel", seg=8)
    m.cyl(0.05, 0.05, (0.65, 1.19, -0.3), "hull_light", seg=16, r2=0.16, rot=(-0.6, 0, 0))
    m.cyl(0.006, 0.12, (0.65, 1.24, -0.27), "brass", seg=6, rot=(-0.6, 0, 0))
    d.up(-0.3, 0.7, 0.3, "waveform", 0.3)
    d.dial(0.7, 0.2, 0.04)


def c_environmental(m, rng):
    d = Desk(m, 1.6, 0.85, 0.9, 1.0, 0.2, "hull_light", "em_green", "hull_mid")
    d.scr(0.0, 0.0, 0.6, 0.34, "schematic")
    for k in range(5):
        d.dial(-0.7 + k * 0.1, 0.22, 0.035, "brass")
    d.slider(0.62, 0.05, 0.3, 0.6, "em_cyan")
    d.slider(0.7, 0.05, 0.3, 0.3, "em_green")
    # side pipes with valve wheels
    for k, x in enumerate((-0.86, 0.86)):
        m.cyl(0.03, 0.9, (x, 0.5, -0.3), "copper", seg=8)
        m.torus(0.04, 0.006, (x, 0.8 - 0.2 * k, -0.3 + 0.0), "paint_red", "z", 14, 6)
        m.cyl(0.012, 0.09, (x, 0.8 - 0.2 * k, -0.3), "steel", axis="z", seg=6)
    d.up(0, 0.9, 0.3, "lifesigns", 0.3)


def c_damage(m, rng):
    d = Desk(m, 1.7, 0.9, 0.9, 1.0, 0.22, "paint_grey", "em_amber", "black_metal")
    hazard(m, -0.8, 0.8, 0.13, d.d / 2 + 0.003, 0.06)
    d.scr(0.0, 0.0, 0.8, 0.36, "schematic")
    for k in range(4):
        x = -0.75 + k * 0.1
        m.box((0.06, 0.03, 0.07), d.p(x, 0.24, 0.02), "hazard_yellow", 0.004, (d.a, 0, 0))
        m.box((0.045, 0.02, 0.05), d.p(x, 0.24, 0.04), "paint_red", 0.003, (d.a - 0.5, 0, 0))
    d.grid(0.4, 0.22, 4, 1, 0.055, 0.05, rng, ["em_red", "em_amber", "em_green"])
    # rotating beacon
    m.cyl(0.05, 0.03, (0.75, 1.03, -0.3), "black_metal", seg=12)
    m.sphere(0.05, (0.75, 1.08, -0.3), "em_red", seg=12, ring=8, scale=(1, 1.1, 1))
    d.up(-0.5, 0.5, 0.3, "alert", 0.3)
    d.up(0.15, 0.5, 0.3, "systems", 0.3)


def c_weapons(m, rng):
    d = Desk(m, 1.6, 0.95, 0.92, 1.02, 0.25, "hull_dark", "em_red", "gunmetal")
    d.scr(0.0, 0.03, 0.55, 0.32, "tactical")
    # twin gooseneck triggers
    for sx in (-1, 1):
        x = sx * 0.6
        m.cyl(0.045, 0.03, d.p(x, 0.1, 0.015), "black_metal", seg=10)
        m.link(d.p(x, 0.1, 0.03), (d.x + x, 1.22, 0.12), 0.018, "gunmetal", 8)
        m.box((0.05, 0.05, 0.11), (d.x + x, 1.25, 0.14), "rubber", 0.01)
        m.box((0.015, 0.03, 0.02), (d.x + x, 1.21, 0.2), "em_red")
    # key switch + arming cover
    m.box((0.12, 0.03, 0.09), d.p(-0.3, 0.24, 0.02), "hazard_yellow", 0.004, (d.a, 0, 0))
    m.cyl(0.02, 0.03, d.p(-0.3, 0.24, 0.04), "brass", seg=8, rot=(d.a, 0, 0))
    m.box((0.12, 0.05, 0.09), d.p(0.3, 0.24, 0.05), "glass_dark", 0.004, (d.a - 0.3, 0, 0))
    d.grid(-0.18, 0.24, 4, 1, 0.055, 0.05, rng, ["em_red", "em_amber"])
    d.up(0, 1.3, 0.34, "tactical", 0.3)
    d.up(-0.5, 0.4, 0.25, "alert", 0.3, y=1.02)


def c_shield(m, rng):
    d = Desk(m, 1.7, 0.9, 0.9, 1.0, 0.22, "hull_light", "em_blue", "paint_navy")
    # hex shield-power emblem panel
    m.cyl(0.24, 0.02, d.p(0, 0.0, 0.012), "black_metal", seg=6, rot=(d.a, 0, 0))
    m.cyl(0.19, 0.01, d.p(0, 0.0, 0.024), "em_blue", seg=6, rot=(d.a, 0, 0))
    m.cyl(0.15, 0.01, d.p(0, 0.0, 0.03), "glass_dark", seg=6, rot=(d.a, 0, 0))
    d.dial(0, 0.0, 0.05, "chrome", "em_cyan")
    d.scr(-0.62, 0.0, 0.36, 0.25, "power")
    d.scr(0.62, 0.0, 0.36, 0.25, "bars")
    for k in range(5):
        d.slider(-0.4 + k * 0.05 + (0 if k < 3 else 0.6), 0.25, 0.12, 0.3 + 0.1 * k, "em_cyan", horiz=True)
    d.up(0, 0.8, 0.3, "systems", 0.3)


def c_transporter(m, rng):
    d = Desk(m, 1.5, 0.95, 0.9, 1.0, 0.2, "hull_mid", "em_amber", "black_metal")
    d.scr(0.0, 0.0, 0.3, 0.28, "vitals")
    # three long slide-levers on a recessed slot
    for k in range(3):
        x = -0.55 + k * 0.1
        m.box((0.05, 0.008, 0.5), d.p(x, 0.0, 0.01), "black_metal", 0, (d.a, 0, 0))
        d.btn(x, -0.15 + 0.15 * k, "gold_trim", (0.05, 0.08), 0.03)
    d.grid(0.3, -0.2, 3, 4, 0.06, 0.06, rng)
    m.cyl(0.06, 0.02, d.p(0.0, 0.26, 0.012), "black_metal", seg=14, rot=(d.a, 0, 0))
    m.cyl(0.045, 0.01, d.p(0.0, 0.26, 0.024), "em_cyan", seg=14, rot=(d.a, 0, 0))
    d.up(0, 0.6, 0.32, "lifesigns", 0.3)
    m.box((0.4, 0.02, 0.04), (0, 1.5, -0.35), "em_amber")


def c_podium(m, rng):
    m.box((0.6, 0.06, 0.55), (0, 0.03, 0), "wood_dark", 0.01)
    m.prism([(-0.22, -0.2), (0.22, -0.2), (0.28, 0.15), (-0.28, 0.15)], 0.98, (0, 0.06, 0), "wood_dark", bevel=0.01)
    m.box((0.5, 0.04, 0.44), (0, 1.04, -0.02), "gold_trim", 0.008)
    m.box((0.5, 0.03, 0.4), (0, 1.09, -0.06), "wood_dark", 0.01, (0.4, 0, 0))
    m.quad((0.28, 0.18), (0, 1.115, -0.058), "screen:text", (0.4 - PI / 2, 0, 0))
    m.box((0.5, 0.05, 0.04), (0, 1.02, 0.21), "gold_trim", 0.006)
    m.box((0.02, 0.6, 0.006), (0, 0.55, 0.156), "gold_trim")
    for sx in (-1, 1):
        m.box((0.02, 0.8, 0.02), (sx * 0.22, 0.55, 0.15), "brass", 0.004, (0, 0, sx * -0.06))
    m.box((0.22, 0.14, 0.006), (0, 0.8, 0.158), "brass")
    m.box((0.18, 0.1, 0.004), (0, 0.8, 0.162), "em_warm")
    m.cyl(0.02, 0.08, (0.26, 1.1, -0.12), "black_metal", seg=8)
    m.sphere(0.016, (0.26, 1.16, -0.12), "em_green", seg=8, ring=6)
    m.box((0.26, 0.015, 0.05), (0, 0.96, 0.05), "black_metal")
    for k in range(4):
        m.box((0.03, 0.012, 0.03), (-0.09 + k * 0.06, 0.99, 0.05), rng.choice(BTN), 0.002)


def c_curved(m, rng):
    n, R, span = 7, 1.9, 1.15
    chord = 2 * R * math.sin(span / (n - 1) / 2) * 1.02
    a = 0.22
    for k in range(n):
        th = -span / 2 + span * k / (n - 1)
        ry = -th
        cx, cz = R * math.sin(th), R * (1 - math.cos(th))
        m.box((chord, 0.86, 0.6), (cx, 0.43, cz - 0.02), "hull_dark" if k % 2 else "hull_mid", 0.008, (0, ry, 0))
        m.box((chord * 1.02, 0.03, 0.62), (cx, 0.96, cz), "gunmetal", 0.006, (a, ry, 0))
        f = yaw((0, 0.09, 0.32), ry)
        m.box((chord * 0.9, 0.012, 0.012), (cx + f[0], 0.86, cz + f[2] + 0.015), "em_cyan", 0, (0, ry, 0))
        if k in (1, 3, 5):
            p = yaw((0, 0.025, 0.02), ry)
            mon(m, chord * 0.75, 0.3, (cx + p[0], 0.995, cz + p[2]), ["nav", "systems", "tactical"][k // 2], (a - PI / 2, ry, 0), 0.015, 0.03)
        else:
            for j in range(3):
                p = yaw(((j - 1) * 0.11, 0.0, 0.05), ry)
                m.box((0.05, 0.012, 0.05), (cx + p[0], 0.985, cz + p[2]), rng.choice(BTN), 0.002, (a, ry, 0))
    m.box((0.4, 0.08, 0.06), (0, 1.02, -0.32), "gold_trim", 0.008)


def c_wallflush(m, rng):
    d = Desk(m, 2.2, 0.4, 0.95, 1.02, 0.02, "hull_light", "em_cyan", "gunmetal")
    # shallow sloped surface, screens set flush
    L = d.L
    for k, tex in enumerate(["systems", "nav", "radar", "graph"]):
        d.scr(-0.78 + k * 0.52, -0.03, 0.44, min(0.22, L - 0.12), tex)
    m.box((2.2, 0.5, 0.05), (0, 1.3, -0.16), "hull_dark", 0.006)
    m.box((2.0, 0.04, 0.02), (0, 1.56, -0.13), "em_cyan")
    for k in range(4):
        m.box((0.4, 0.3, 0.03), (-0.78 + k * 0.52, 1.28, -0.13), "hull_mid", 0.005)
        m.box((0.3, 0.02, 0.006), (-0.78 + k * 0.52, 1.28, -0.113), "em_cyan")
    bolts(m, [(-1.05, 1.5, -0.13), (1.05, 1.5, -0.13), (-1.05, 1.1, -0.13), (1.05, 1.1, -0.13)])


def c_aux(m, rng):
    d = Desk(m, 1.0, 0.6, 0.88, 0.96, 0.15, "hull_mid", "em_amber", "gunmetal")
    d.scr(0.0, -0.02, 0.4, 0.2, "text")
    d.grid(-0.2, 0.15, 5, 1, 0.09, 0.05, rng)
    d.up(0, 0.4, 0.26, "diagnostic", 0.3)
    # foot pedal + stool ring
    m.box((0.2, 0.04, 0.12), (0.2, 0.02, 0.4), "black_metal", 0.008, (0, 0.2, 0))
    m.box((0.14, 0.03, 0.05), (0.2, 0.05, 0.42), "rubber", 0.005, (0, 0.2, 0))


def c_corner(m, rng):
    pts = [(0, -0.62), (0.95, 0.3), (0.6, 0.7), (-0.6, 0.7), (-0.95, 0.3)]
    m.prism(pts, 0.92, (0, 0, 0), "hull_mid", bevel=0.012)
    # recess/toe
    m.prism([(0, -0.55), (0.9, 0.3), (0.56, 0.64), (-0.56, 0.64), (-0.9, 0.3)], 0.06, (0, 0.92, 0), "gunmetal", bevel=0.004)
    m.box((1.0, 0.012, 0.012), (0, 0.06, 0.71), "em_cyan")
    for sx in (-1, 1):
        rot = sx * PI / 4
        mon(m, 0.5, 0.3, (sx * 0.55, 1.28, -0.02 - 0.0), "systems" if sx < 0 else "nav", (-0.2, -rot * 1.0, 0), 0.02, 0.04)
        m.box((0.06, 0.4, 0.05), (sx * 0.55, 1.1, -0.1), "hull_dark", 0.005)
        for j in range(3):
            m.box((0.05, 0.014, 0.05), (sx * (0.35 + j * 0.09), 0.987, 0.45 - j * 0.02), rng.choice(BTN), 0.002)
    mon(m, 0.5, 0.3, (0, 1.15, -0.4), "radar", (-0.25, 0, 0), 0.02, 0.05)
    m.box((0.08, 0.3, 0.05), (0, 1.05, -0.44), "hull_dark", 0.005)
    m.cyl(0.05, 0.02, (0, 0.995, 0.5), "black_metal", seg=12)
    m.cyl(0.035, 0.012, (0, 1.008, 0.5), "em_amber", seg=12)


def c_triple(m, rng):
    d = Desk(m, 2.0, 0.9, 0.88, 1.0, 0.2, "hull_dark", "em_cyan", "black_metal")
    d.scr(0.0, -0.02, 0.8, 0.3, "nav")
    d.grid(-0.8, 0.2, 5, 1, 0.055, 0.05, rng)
    d.grid(0.5, 0.2, 5, 1, 0.055, 0.05, rng)
    # triptych of upright screens
    m.box((1.9, 0.04, 0.08), (0, 1.07, -0.34), "hull_mid", 0.006)
    mon(m, 0.72, 0.42, (0, 1.4, -0.34), "starmap", (-0.22, 0, 0), 0.02, 0.05)
    for sx in (-1, 1):
        mon(m, 0.55, 0.42, (sx * 0.68, 1.4, -0.28), "systems" if sx < 0 else "tactical", (-0.22, -sx * 0.45, 0), 0.02, 0.05)
        m.box((0.06, 0.34, 0.05), (sx * 0.7, 1.22, -0.38), "hull_dark", 0.005)
    m.box((0.06, 0.34, 0.05), (0, 1.22, -0.4), "hull_dark", 0.005)


CONSOLES = [("helm", c_helm), ("navigation", c_navigation), ("ops", c_ops), ("tactical", c_tactical),
            ("science", c_science), ("engineering status", c_engineering), ("communications", c_comms),
            ("flight control", c_flightcontrol), ("sensor", c_sensor), ("environmental", c_environmental),
            ("damage control", c_damage), ("weapons", c_weapons), ("shield control", c_shield),
            ("transporter control", c_transporter), ("captain podium", c_podium),
            ("curved command desk", c_curved), ("wall flush", c_wallflush), ("compact aux", c_aux),
            ("corner", c_corner), ("sloped triple screen", c_triple)]


@family("console", [n for n, _ in CONSOLES], mount="floor", tags=["bridge", "console"], solid=True)
def bridge_console(m, i, label, rng):
    CONSOLES[i][1](m, rng)


# ---------------------------------------------------------------- seats
def _pedestal(m, r=0.3, col=0.05, top=0.4, mat="steel", base="hull_dark"):
    m.cyl(r, 0.04, (0, 0.02, 0), base, seg=20, bevel=0.008)
    m.cyl(r * 0.6, 0.03, (0, 0.055, 0), "black_metal", seg=16, r2=r * 0.35)
    m.cyl(col, top - 0.07, (0, 0.07 + (top - 0.07) / 2, 0), mat, seg=12)
    m.cyl(col * 1.5, 0.05, (0, top - 0.03, 0), "black_metal", seg=12)


def _cushion(m, w, d, y, mat, t=0.09, z=0.0, bev=0.025):
    m.box((w, t, d), (0, y, z), mat, bev)


def s_captain(m, rng):
    _pedestal(m, 0.36, 0.06, 0.4, "chrome")
    m.cyl(0.36, 0.01, (0, 0.045, 0), "gold_trim", seg=20)
    _cushion(m, 0.62, 0.58, 0.44, "leather_black", 0.11, 0.0, 0.035)
    m.box((0.6, 0.06, 0.55), (0, 0.395, 0), "hull_dark", 0.01)
    # high back
    m.box((0.58, 0.72, 0.13), (0, 0.9, -0.3), "leather_black", 0.04, (-0.12, 0, 0))
    m.box((0.36, 0.5, 0.02), (0, 0.9, -0.235), "leather_brown", 0.01, (-0.12, 0, 0))
    m.box((0.4, 0.2, 0.12), (0, 1.36, -0.34), "leather_black", 0.04, (-0.12, 0, 0))
    m.box((0.66, 0.03, 0.05), (0, 0.6, -0.27), "gold_trim", 0.008, (-0.12, 0, 0))
    for sx in (-1, 1):
        x = sx * 0.37
        m.box((0.08, 0.5, 0.06), (sx * 0.33, 0.75, -0.3), "hull_dark", 0.01)
        m.box((0.1, 0.05, 0.5), (x, 0.66, -0.03), "hull_dark", 0.012)     # arm
        m.box((0.07, 0.35, 0.06), (x, 0.5, -0.27), "hull_dark", 0.01)
        m.box((0.13, 0.05, 0.2), (x, 0.7, 0.06), "black_metal", 0.01)      # control pad
        m.box((0.12, 0.012, 0.13), (x, 0.727, 0.08), "gunmetal", 0.003, (0.15, 0, 0))
        m.quad((0.09, 0.07), (x, 0.735, 0.07), "screen:systems", (0.15 - PI / 2, 0, 0))
        for j in range(3):
            m.box((0.022, 0.012, 0.022), (x - 0.03 + j * 0.03, 0.732, 0.16), rng.choice(BTN), 0.002)
    m.box((0.5, 0.012, 0.012), (0, 0.44 - 0.055, 0.29), "em_cyan")


def s_helm(m, rng):
    _pedestal(m, 0.3, 0.05, 0.42, "steel")
    m.torus(0.26, 0.012, (0, 0.13, 0), "chrome", "y", 20, 6)
    for k in range(4):
        a = k * PI / 2 + 0.4
        m.link((0, 0.13, 0), (0.26 * math.cos(a), 0.13, 0.26 * math.sin(a)), 0.008, "steel", 6)
    _cushion(m, 0.5, 0.5, 0.46, "fabric_navy", 0.1, 0.0, 0.03)
    for sx in (-1, 1):   # bolsters
        m.box((0.08, 0.16, 0.44), (sx * 0.27, 0.53, -0.02), "fabric_navy", 0.03)
    m.box((0.5, 0.5, 0.1), (0, 0.78, -0.25), "fabric_navy", 0.035, (-0.14, 0, 0))
    m.box((0.36, 0.3, 0.03), (0, 0.8, -0.195), "fabric_grey", 0.01, (-0.14, 0, 0))
    m.box((0.5, 0.02, 0.02), (0, 0.56, -0.2), "em_blue")
    m.box((0.3, 0.08, 0.1), (0, 0.42, -0.3), "hull_dark", 0.01)


def s_ops(m, rng):
    m.cyl(0.05, 0.28, (0, 0.24, 0), "steel", seg=10)
    for k in range(5):
        a = k * 2 * PI / 5
        c, s_ = math.cos(a), math.sin(a)
        m.link((0, 0.1, 0), (0.3 * c, 0.07, 0.3 * s_), 0.017, "black_metal", 6)
        m.sphere(0.03, (0.3 * c, 0.035, 0.3 * s_), "rubber", seg=8, ring=6)
    m.cyl(0.07, 0.06, (0, 0.1, 0), "black_metal", seg=10)
    m.cyl(0.08, 0.06, (0, 0.39, 0), "black_metal", seg=10)
    _cushion(m, 0.5, 0.48, 0.44, "fabric_grey", 0.09, 0.0, 0.03)
    m.box((0.46, 0.5, 0.08), (0, 0.78, -0.24), "fabric_grey", 0.03, (-0.1, 0, 0))
    m.box((0.05, 0.4, 0.05), (0, 0.6, -0.24), "steel", 0.005, (-0.1, 0, 0))
    for sx in (-1, 1):
        m.box((0.03, 0.22, 0.03), (sx * 0.27, 0.56, -0.15), "black_metal", 0.004)
        m.box((0.07, 0.035, 0.28), (sx * 0.27, 0.66, -0.05), "fabric_grey", 0.012)
    m.box((0.36, 0.025, 0.025), (0, 0.9, -0.28), "em_amber")


def s_tactical(m, rng):
    _pedestal(m, 0.32, 0.055, 0.4, "gunmetal")
    _cushion(m, 0.54, 0.52, 0.44, "fabric_red", 0.1, 0.0, 0.03)
    m.box((0.54, 0.8, 0.11), (0, 0.9, -0.27), "fabric_red", 0.035, (-0.1, 0, 0))
    m.box((0.34, 0.16, 0.1), (0, 1.36, -0.31), "fabric_red", 0.035, (-0.1, 0, 0))
    for sx in (-1, 1):   # harness straps and buckles
        m.box((0.05, 0.62, 0.012), (sx * 0.12, 0.86, -0.2), "black_metal", 0.002, (-0.1, 0, 0))
        m.box((0.04, 0.05, 0.02), (sx * 0.1, 0.62, -0.19), "chrome", 0.004)
        m.box((0.05, 0.03, 0.4), (sx * 0.31, 0.66, -0.03), "black_metal", 0.01)
        m.box((0.03, 0.2, 0.03), (sx * 0.31, 0.55, -0.2), "black_metal")
        m.cyl(0.02, 0.1, (sx * 0.31, 0.7, 0.16), "rubber", axis="z", seg=8)
    m.box((0.6, 0.02, 0.02), (0, 0.44, 0.28), "em_red")
    m.cyl(0.04, 0.02, (0, 1.02, -0.3), "hazard_yellow", seg=10, axis="z")


def s_stool(m, rng):
    m.cyl(0.28, 0.04, (0, 0.02, 0), "hull_dark", seg=20, bevel=0.008)
    m.cyl(0.04, 0.5, (0, 0.3, 0), "chrome", seg=10)
    m.torus(0.2, 0.014, (0, 0.28, 0), "chrome", "y", 20, 6)
    for k in range(3):
        a = k * 2 * PI / 3
        m.link((0, 0.28, 0), (0.2 * math.cos(a), 0.28, 0.2 * math.sin(a)), 0.01, "steel", 6)
    m.cyl(0.19, 0.08, (0, 0.6, 0), "fabric_teal", seg=20, r2=0.2, bevel=0.02)
    m.cyl(0.2, 0.02, (0, 0.55, 0), "black_metal", seg=20)
    m.torus(0.19, 0.006, (0, 0.64, 0), "em_cyan", "y", 20, 4)
    m.cyl(0.06, 0.03, (0, 0.53, 0), "black_metal", seg=10)


def s_comms(m, rng):
    _pedestal(m, 0.3, 0.05, 0.42, "brushed_alu")
    _cushion(m, 0.5, 0.48, 0.46, "fabric_teal", 0.1, 0.0, 0.03)
    m.box((0.48, 0.62, 0.1), (0, 0.85, -0.25), "fabric_teal", 0.035, (-0.16, 0, 0))
    m.box((0.3, 0.18, 0.1), (0, 1.25, -0.29), "fabric_grey", 0.04, (-0.16, 0, 0))
    for sx in (-1, 1):
        m.box((0.06, 0.03, 0.34), (sx * 0.28, 0.67, -0.06), "hull_dark", 0.01)
        m.box((0.03, 0.2, 0.03), (sx * 0.28, 0.56, -0.2), "hull_dark")
        m.cyl(0.055, 0.035, (sx * 0.19, 1.22, -0.3), "plastic_black", axis="x", seg=12, bevel=0.005)  # ear cups
    m.tube([(0.33, 0.7, -0.06), (0.4, 0.95, -0.02), (0.3, 1.08, 0.05)], 0.008, "black_metal", 6)
    m.sphere(0.02, (0.3, 1.09, 0.06), "plastic_black", seg=8, ring=6)
    m.box((0.02, 0.02, 0.3), (0, 0.5, 0.26), "em_green")


def s_bench(m, rng):
    # two-seat observer bench
    m.box((1.3, 0.06, 0.5), (0, 0.03, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.06, 0.35, 0.44), (sx * 0.62, 0.22, 0), "hull_mid", 0.012)
        m.box((0.06, 0.32, 0.4), (sx * 0.2, 0.22, 0), "hull_mid", 0.012)
    m.box((1.24, 0.03, 0.02), (0, 0.06, 0.26), "em_blue")
    for sx in (-1, 1):
        x = sx * 0.4
        m.box((0.56, 0.09, 0.5), (x, 0.42, 0), "fabric_grey", 0.03)
        m.box((0.56, 0.4, 0.08), (x, 0.7, -0.24), "fabric_grey", 0.03, (-0.15, 0, 0))
    m.box((1.36, 0.06, 0.1), (0, 0.88, -0.29), "hull_dark", 0.01, (-0.15, 0, 0))
    m.box((0.05, 0.6, 0.06), (-0.66, 0.58, -0.25), "hull_dark", 0.008)
    m.box((0.05, 0.6, 0.06), (0.66, 0.58, -0.25), "hull_dark", 0.008)
    m.box((0.05, 0.62, 0.06), (0, 0.6, -0.27), "hull_dark", 0.008)
    for sx in (-1, 1):
        m.box((0.05, 0.03, 0.05), (sx * 0.62, 0.42 + 0.1, 0.05), "steel", 0.004)


def s_jump(m, rng):
    # swivel jump seat on a single column, small round back
    m.cyl(0.24, 0.03, (0, 0.015, 0), "hull_dark", seg=20, bevel=0.006)
    m.cyl(0.05, 0.34, (0, 0.2, 0), "hull_mid", seg=10)
    m.box((0.3, 0.05, 0.16), (0, 0.38, -0.03), "black_metal", 0.008)
    m.cyl(0.24, 0.07, (0, 0.44, 0), "fabric_tan", seg=20, r2=0.23, bevel=0.015)
    m.torus(0.23, 0.02, (0, 0.475, 0), "fabric_tan", "y", 20, 6)
    # curved backrest
    m.torus(0.25, 0.02, (0, 0.72, 0), "fabric_tan", "y", 12, 6, arc=1.6, rot=(0, 2.4, 0))
    m.torus(0.25, 0.02, (0, 0.62, 0), "fabric_tan", "y", 12, 6, arc=1.6, rot=(0, 2.4, 0))
    m.torus(0.25, 0.02, (0, 0.82, 0), "fabric_tan", "y", 12, 6, arc=1.6, rot=(0, 2.4, 0))
    for sx in (-1, 1):
        m.box((0.03, 0.4, 0.03), (sx * 0.19, 0.66, -0.17), "steel", 0.004)
    m.box((0.05, 0.06, 0.02), (0.22, 0.5, 0.06), "em_amber")


SEATS = [("captain command chair", s_captain), ("helm chair", s_helm), ("ops chair", s_ops),
         ("tactical chair", s_tactical), ("science stool", s_stool), ("comms chair", s_comms),
         ("observer bench", s_bench), ("swivel jump seat", s_jump)]


@family("seat", [n for n, _ in SEATS], mount="floor", tags=["bridge", "seat"], solid=True)
def bridge_seat(m, i, label, rng):
    SEATS[i][1](m, rng)


# ---------------------------------------------------------------- displays (wall, origin = centre of back plane)
def wframe(m, w, h, tex, depth=0.07, frame="hull_dark", trim="em_cyan", bz=0.05, z0=0.0):
    """Framed wall display centred on the origin."""
    m.box((w, h, depth), (0, 0, z0 + depth / 2), frame, 0.012)
    iw, ih = w - 2 * bz, h - 2 * bz
    m.box((iw + 0.02, ih + 0.02, 0.01), (0, 0, z0 + depth + 0.002), "black_metal", 0.003)
    m.quad((iw, ih), (0, 0, z0 + depth + 0.008), "screen:" + tex)
    if trim:
        m.box((iw, 0.012, 0.01), (0, -ih / 2 - 0.02 if bz > 0.04 else -ih / 2, z0 + depth + 0.004), trim)
    return iw, ih


def d_viewscreen(m, rng):
    W, H = 5.0, 2.6
    m.box((W + 0.5, 0.3, 0.3), (0, H / 2 + 0.1, 0.15), "hull_dark", 0.02)
    m.box((W + 0.5, 0.3, 0.3), (0, -H / 2 - 0.1, 0.15), "hull_dark", 0.02)
    for sx in (-1, 1):
        m.box((0.3, H + 0.5, 0.3), (sx * (W / 2 + 0.1), 0, 0.15), "hull_dark", 0.02)
        m.box((0.08, H - 0.1, 0.05), (sx * (W / 2 - 0.1), 0, 0.3), "gold_trim", 0.008)
        m.box((0.4, 0.4, 0.34), (sx * (W / 2 + 0.1), H / 2 + 0.1, 0.17), "hull_mid", 0.03)
        m.box((0.4, 0.4, 0.34), (sx * (W / 2 + 0.1), -H / 2 - 0.1, 0.17), "hull_mid", 0.03)
        for k in range(4):
            m.box((0.05, 0.05, 0.02), (sx * (W / 2 + 0.1), -0.8 + k * 0.5, 0.31), rng.choice(["em_cyan", "em_amber", "em_green"]))
    m.box((W, H, 0.04), (0, 0, 0.02), "black_metal")
    m.quad((W - 0.1, H - 0.1), (0, 0, 0.045), "screen:starmap")
    m.box((W - 0.05, 0.03, 0.03), (0, H / 2 - 0.04, 0.05), "em_cyan")
    m.box((W - 0.05, 0.03, 0.03), (0, -H / 2 + 0.04, 0.05), "em_cyan")
    m.box((1.6, 0.12, 0.05), (0, H / 2 + 0.28, 0.1), "gold_trim", 0.01)
    m.box((1.2, 0.08, 0.02), (0, H / 2 + 0.28, 0.14), "em_amber")
    bolts(m, [(x, y, 0.31) for x in (-2.6, 2.6) for y in (-1.5, 1.5)], 0.02, "steel", h=0.02)


def d_status(m, rng):
    wframe(m, 1.5, 1.0, "systems", trim=None)
    m.box((1.2, 0.02, 0.01), (0, 0.32, 0.08), "black_metal")
    m.box((1.5, 0.05, 0.05), (0, -0.53, 0.05), "hull_mid", 0.008)
    for k in range(6):
        m.box((0.03, 0.03, 0.02), (-0.5 + k * 0.2, -0.53, 0.085), BTN[k])


def d_tactical_wall(m, rng):
    m.box((1.9, 1.3, 0.1), (0, 0, 0.05), "hull_dark", 0.015)
    m.box((1.7, 1.1, 0.02), (0, 0, 0.11), "black_metal", 0.004)
    m.quad((1.64, 1.04), (0, 0, 0.122), "screen:tactical")
    m.box((1.9, 0.06, 0.16), (0, -0.66, 0.1), "hazard_yellow", 0.008)
    m.box((0.05, 1.3, 0.14), (-0.97, 0, 0.09), "paint_red", 0.006)
    m.box((0.05, 1.3, 0.14), (0.97, 0, 0.09), "paint_red", 0.006)
    for k in range(5):
        m.cyl(0.02, 0.03, (-0.7 + k * 0.35, 0.69, 0.08), "em_red", axis="y", seg=8)


def d_arm(m, rng):
    m.box((0.2, 0.3, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    m.cyl(0.035, 0.5, (0, 0, 0.25), "steel", axis="z", seg=10)
    m.sphere(0.05, (0, 0, 0.5), "black_metal", seg=10, ring=6)
    m.box((0.1, 0.12, 0.1), (0, -0.05, 0.56), "hull_mid", 0.01)
    mon(m, 0.7, 0.42, (0, -0.15, 0.64), "systems", (0.5, 0, 0), 0.03, 0.05)
    m.box((0.7, 0.02, 0.02), (0, -0.4, 0.62), "em_amber")


def d_tall(m, rng):
    wframe(m, 0.42, 1.8, "bars", 0.08, "hull_mid", "em_green", 0.04)
    for k in range(6):
        m.box((0.3, 0.008, 0.01), (0, -0.7 + k * 0.28, 0.095), "steel")
    m.cyl(0.02, 0.03, (0, 0.86, 0.09), "em_red", axis="z", seg=8)
    m.box((0.5, 0.06, 0.1), (0, 0.93, 0.05), "black_metal", 0.01)


def d_dual(m, rng):
    m.box((0.14, 0.14, 0.04), (0, 0, 0.02), "hull_dark", 0.008)
    m.cyl(0.03, 0.22, (0, 0, 0.13), "steel", axis="z", seg=8)
    m.box((1.3, 0.05, 0.05), (0, 0, 0.26), "hull_dark", 0.008)
    for sx in (-1, 1):
        mon(m, 0.55, 0.36, (sx * 0.34, 0, 0.32), ["nav", "radar"][sx > 0], (0, -sx * 0.4, 0), 0.025, 0.05)
        m.box((0.04, 0.1, 0.05), (sx * 0.34, 0, 0.27), "steel", 0.004)


def d_round(m, rng):
    m.cyl(0.5, 0.08, (0, 0, 0.04), "hull_dark", axis="z", seg=24, bevel=0.01)
    m.torus(0.47, 0.025, (0, 0, 0.09), "chrome", "z", 24, 8)
    m.cyl(0.43, 0.02, (0, 0, 0.09), "black_metal", axis="z", seg=24)
    m.quad((0.62, 0.62), (0, 0, 0.102), "screen:radar")
    for k in range(12):
        a = k * PI / 6
        m.box((0.02, 0.05, 0.015), (0.4 * math.cos(a), 0.4 * math.sin(a), 0.105), "em_cyan", 0, (0, 0, a - PI / 2))
    m.torus(0.5, 0.008, (0, 0, 0.05), "em_cyan", "z", 24, 4)


def d_schematics(m, rng):
    m.box((2.5, 1.5, 0.06), (0, 0, 0.03), "wood_dark", 0.02)
    m.box((2.34, 1.34, 0.02), (0, 0, 0.07), "black_metal", 0.004)
    m.quad((2.3, 1.3), (0, 0, 0.082), "screen:schematic")
    for k in range(4):
        m.box((0.03, 0.03, 0.03), ((-1.15, 1.15)[k % 2], (-0.65, 0.65)[k // 2], 0.09), "brass")
    m.box((2.5, 0.08, 0.14), (0, 0.79, 0.07), "wood_dark", 0.01)
    m.box((1.0, 0.05, 0.02), (0, 0.79, 0.15), "em_amber")
    m.box((2.5, 0.05, 0.06), (0, -0.78, 0.08), "steel", 0.005)


def d_alert(m, rng):
    wframe(m, 1.0, 0.7, "alert", 0.08, "hull_dark", None, 0.05)
    for k, mm in enumerate(["em_red", "em_amber", "em_green"]):
        m.cyl(0.07, 0.06, (-0.24 + k * 0.24, 0.5, 0.05), "black_metal", axis="z", seg=16)
        m.cyl(0.055, 0.05, (-0.24 + k * 0.24, 0.5, 0.07), mm, axis="z", seg=16)
    m.box((1.0, 0.1, 0.03), (0, -0.4, 0.09), "paint_red", 0.005)


def d_clock(m, rng):
    m.cyl(0.32, 0.06, (0, 0, 0.03), "black_metal", axis="z", seg=28, bevel=0.006)
    m.torus(0.3, 0.025, (0, 0, 0.06), "brass", "z", 28, 8)
    m.cyl(0.28, 0.01, (0, 0, 0.062), "plastic_white", axis="z", seg=28)
    for k in range(12):
        a = k * PI / 6
        L = 0.05 if k % 3 == 0 else 0.03
        m.box((0.015, L, 0.006), (0.24 * math.sin(a), 0.24 * math.cos(a), 0.07), "black_metal", 0, (0, 0, -a))
    m.box((0.02, 0.15, 0.008), (0.05, 0.07, 0.078), "black_metal", 0, (0, 0, -0.9))
    m.box((0.012, 0.22, 0.008), (-0.04, 0.09, 0.086), "black_metal", 0, (0, 0, 0.4))
    m.box((0.006, 0.24, 0.006), (0, 0.0, 0.092), "em_red", 0, (0, 0, -2.4))
    m.cyl(0.02, 0.02, (0, 0, 0.09), "brass", axis="z", seg=8)


def d_deckplan(m, rng):
    m.box((1.1, 1.5, 0.06), (0, 0, 0.03), "brass", 0.015)
    m.box((1.0, 1.4, 0.02), (0, 0, 0.07), "black_metal", 0.004)
    m.quad((0.96, 1.36), (0, 0, 0.082), "screen:schematic")
    m.box((1.0, 1.4, 0.008), (0, 0, 0.1), "glass", 0.0)
    m.box((0.6, 0.1, 0.02), (0, 0.8, 0.03), "gold_trim", 0.006)
    for k in range(3):
        m.box((0.08, 0.05, 0.02), (-0.35 + k * 0.35, -0.8, 0.03), BTN[k])


def d_ticker(m, rng):
    m.box((2.2, 0.28, 0.07), (0, 0, 0.035), "hull_dark", 0.01)
    m.box((2.1, 0.2, 0.01), (0, 0, 0.075), "black_metal", 0.003)
    m.quad((2.06, 0.18), (0, 0, 0.082), "screen:text")
    for sx in (-1, 1):
        m.box((0.1, 0.24, 0.09), (sx * 1.12, 0, 0.045), "hull_mid", 0.01)
        m.cyl(0.03, 0.03, (sx * 1.12, 0, 0.1), "em_amber", axis="z", seg=8)


def d_vitals(m, rng):
    m.box((0.5, 0.3, 0.05), (0, 0.0, 0.025), "hull_dark", 0.008)
    m.box((0.06, 0.06, 0.2), (0, 0, 0.14), "steel", 0.006)
    m.box((0.06, 0.06, 0.06), (0, 0, 0.26), "hull_mid", 0.01)
    mon(m, 0.5, 0.32, (0, 0, 0.33), "vitals", (0, 0, 0), 0.03, 0.06, "plastic_white", 0.01)
    m.box((0.5, 0.03, 0.07), (0, -0.2, 0.33), "plastic_white", 0.006)
    m.cyl(0.02, 0.02, (0.2, -0.2, 0.37), "em_green", axis="z", seg=8)


def d_stack3(m, rng):
    m.box((0.85, 1.55, 0.06), (0, 0, 0.03), "hull_mid", 0.012)
    for k, t in enumerate(["waveform", "graph", "bars"]):
        m.box((0.7, 0.42, 0.02), (0, 0.5 - k * 0.5, 0.07), "black_metal", 0.004)
        m.quad((0.66, 0.38), (0, 0.5 - k * 0.5, 0.082), "screen:" + t)
        m.box((0.7, 0.02, 0.015), (0, 0.5 - k * 0.5 - 0.235, 0.075), ["em_cyan", "em_amber", "em_green"][k])


def d_hex(m, rng):
    m.cyl(0.55, 0.08, (0, 0, 0.04), "hull_dark", axis="z", seg=6, bevel=0.01, rot=(0, 0, PI / 6))
    m.cyl(0.47, 0.02, (0, 0, 0.09), "black_metal", axis="z", seg=6, rot=(0, 0, PI / 6))
    m.quad((0.66, 0.66), (0, 0, 0.102), "screen:globe")
    for k in range(6):
        a = k * PI / 3
        m.box((0.05, 0.05, 0.03), (0.52 * math.cos(a), 0.52 * math.sin(a), 0.09), "em_violet")


def d_wings(m, rng):
    m.box((1.0, 0.7, 0.07), (0, 0, 0.035), "hull_dark", 0.012)
    m.box((0.94, 0.64, 0.01), (0, 0, 0.075), "black_metal")
    m.quad((0.9, 0.6), (0, 0, 0.082), "screen:nav")
    for sx in (-1, 1):
        m.box((0.4, 0.6, 0.06), (sx * 0.62, 0, 0.14), "hull_mid", 0.01, (0, -sx * 0.7, 0))
        mon(m, 0.32, 0.5, (sx * 0.6, 0, 0.19), "text" if sx < 0 else "graph", (0, -sx * 0.7, 0), 0.02, 0.03)
        m.box((0.05, 0.05, 0.1), (sx * 0.5, 0, 0.06), "steel", 0.004)
    m.box((1.0, 0.03, 0.02), (0, 0.38, 0.06), "em_cyan")


def d_scope_rack(m, rng):
    m.box((1.2, 0.8, 0.1), (0, 0, 0.05), "hull_mid", 0.012)
    m.box((0.6, 0.6, 0.02), (-0.25, 0, 0.11), "black_metal", 0.004)
    m.quad((0.56, 0.56), (-0.25, 0, 0.122), "screen:waveform")
    m.box((0.35, 0.28, 0.02), (0.35, 0.22, 0.11), "black_metal", 0.004)
    m.quad((0.31, 0.24), (0.35, 0.22, 0.122), "screen:radar")
    for k in range(3):
        m.cyl(0.04, 0.04, (0.2 + k * 0.15, -0.15, 0.12), "chrome", axis="z", seg=12)
        m.box((0.006, 0.05, 0.01), (0.2 + k * 0.15, -0.15, 0.145), "em_white", 0, (0, 0, k))


def d_heading(m, rng):
    wframe(m, 0.9, 0.6, "nav", 0.07, "hull_light", "em_blue", 0.05)
    m.torus(0.13, 0.012, (0, -0.42, 0.06), "brass", "z", 20, 6)
    m.cyl(0.12, 0.03, (0, -0.42, 0.045), "black_metal", axis="z", seg=20)
    m.box((0.01, 0.2, 0.01), (0, -0.42, 0.075), "em_red")


def d_comm_log(m, rng):
    wframe(m, 1.2, 0.8, "comm", 0.09, "hull_dark", "em_green", 0.05)
    m.cyl(0.11, 0.03, (0, -0.55, 0.045), "black_metal", axis="z", seg=16)
    for r in (0.02, 0.05, 0.08):
        m.torus(r + 0.01, 0.004, (0, -0.55, 0.062), "steel", "z", 14, 4)
    m.box((1.2, 0.28, 0.06), (0, -0.55, 0.03), "hull_dark", 0.008)
    for k in range(4):
        m.box((0.05, 0.03, 0.02), (-0.5 + k * 0.08, -0.55, 0.07), BTN[k])
        m.box((0.05, 0.03, 0.02), (0.3 + k * 0.08, -0.55, 0.07), BTN[k + 3])


def d_diag_rack(m, rng):
    m.box((1.0, 1.2, 0.1), (0, 0, 0.05), "gunmetal", 0.012)
    for k in range(4):
        y = 0.4 - k * 0.27
        m.box((0.9, 0.2, 0.02), (0, y, 0.11), "black_metal", 0.003)
        m.quad((0.5, 0.16), (-0.18, y, 0.122), "screen:diagnostic")
        for j in range(5):
            m.box((0.012, 0.16, 0.008), (0.16 + j * 0.03, y, 0.118), "black_metal")
        m.cyl(0.015, 0.02, (0.38, y, 0.125), "em_green" if k % 2 else "em_amber", axis="z", seg=8)
    hazard(m, -0.45, 0.45, -0.58, 0.105, 0.04)


def d_holoframe(m, rng):
    m.box((1.4, 0.06, 0.06), (0, -0.4, 0.03), "hull_dark", 0.008)
    m.box((1.4, 0.06, 0.06), (0, 0.4, 0.03), "hull_dark", 0.008)
    m.box((1.2, 0.7, 0.01), (0, 0, 0.06), "glass_blue")
    for sx in (-1, 1):
        m.box((0.05, 0.86, 0.08), (sx * 0.72, 0, 0.04), "hull_dark", 0.008)
        m.box((0.02, 0.7, 0.02), (sx * 0.62, 0, 0.07), "em_cyan")
    m.quad((0.9, 0.5), (0, 0, 0.07), "screen:globe")
    m.box((1.2, 0.02, 0.03), (0, -0.36, 0.07), "em_cyan")


def d_power_board(m, rng):
    m.box((1.4, 0.9, 0.08), (0, 0, 0.04), "hull_mid", 0.012)
    m.box((0.7, 0.5, 0.02), (-0.28, 0.1, 0.09), "black_metal", 0.004)
    m.quad((0.66, 0.46), (-0.28, 0.1, 0.102), "screen:power")
    for j in range(2):
        for k in range(8):
            m.box((0.05, 0.07, 0.03), (-0.55 + k * 0.155, -0.28 - j * 0.1, 0.09), "black_metal", 0.004)
            m.box((0.02, 0.02, 0.012), (-0.55 + k * 0.155, -0.28 - j * 0.1 + 0.02, 0.11), "em_green" if (k + j) % 3 else "em_red")
    for k in range(3):
        m.box((0.02, 0.4, 0.01), (0.3 + k * 0.12, 0.1, 0.09), "black_metal")
        m.box((0.05, 0.03, 0.02), (0.3 + k * 0.12, 0.05 + 0.1 * k, 0.1), "em_amber")
    hazard(m, -0.7, 0.7, 0.41, 0.085, 0.05)


DISPLAYS = [("main viewscreen", d_viewscreen, 3.0), ("status board", d_status, None), ("tactical wall screen", d_tactical_wall, None),
            ("swing arm monitor", d_arm, None), ("tall readout", d_tall, None), ("dual screen mount", d_dual, None),
            ("circular display", d_round, None), ("schematics wall", d_schematics, None), ("alert board", d_alert, None),
            ("chronometer clock", d_clock, None), ("deck plan board", d_deckplan, None), ("ticker banner", d_ticker, None),
            ("vitals monitor", d_vitals, None), ("triple stack", d_stack3, None), ("hex display", d_hex, None),
            ("wing display", d_wings, None), ("scope rack", d_scope_rack, None), ("heading display", d_heading, None),
            ("comms log board", d_comm_log, None), ("diagnostic rack", d_diag_rack, None),
            ("holo frame panel", d_holoframe, None), ("power board", d_power_board, None)]


@family("display", ["main viewscreen"], mount="wall", tags=["bridge", "display"], solid=False, mount_y=3.0)
def bridge_viewscreen(m, i, label, rng):
    d_viewscreen(m, rng)


@family("display", [x[0] for x in DISPLAYS[1:]], mount="wall", tags=["bridge", "display"], solid=False, mount_y=1.6)
def bridge_display(m, i, label, rng):
    DISPLAYS[i + 1][1](m, rng)


# ---------------------------------------------------------------- control panels (wall, centred on origin)
def plate(m, w, h, mat="hull_mid", depth=0.04, trim=None):
    m.box((w, h, depth), (0, 0, depth / 2), mat, 0.008)
    m.box((w - 0.03, h - 0.03, 0.006), (0, 0, depth + 0.002), "hull_dark", 0.002)
    bolts(m, [(sx * (w / 2 - 0.02), sy * (h / 2 - 0.02), depth + 0.004) for sx in (-1, 1) for sy in (-1, 1)], 0.006, h=0.008)
    if trim:
        m.box((w - 0.04, 0.008, 0.008), (0, -h / 2 + 0.012, depth + 0.006), trim)


def toggle(m, x, y, z=0.045, mat="chrome", up=True):
    m.cyl(0.015, 0.012, (x, y, z), "steel", axis="z", seg=8)
    a = -0.5 if up else 0.5
    m.link((x, y, z), (x, y + 0.03 * (1 if up else -1), z + 0.03), 0.005, mat, 6)
    m.sphere(0.008, (x, y + 0.03 * (1 if up else -1), z + 0.03), mat, seg=6, ring=4)


def pbtn(m, x, y, mat="em_green", s=0.03, z=0.045):
    m.box((s + 0.008, s + 0.008, 0.008), (x, y, z), "black_metal", 0.002)
    m.box((s, s, 0.012), (x, y, z + 0.007), mat, 0.003)


def knob(m, x, y, r=0.025, z=0.045, mat="black_metal"):
    m.cyl(r, 0.02, (x, y, z + 0.01), mat, axis="z", seg=14, bevel=0.003)
    m.box((0.005, r * 0.8, 0.004), (x, y + r * 0.4, z + 0.022), "em_white")


def cp_switch(m, rng):
    plate(m, 0.45, 0.35, "hull_mid", trim="em_amber")
    for r in range(2):
        for c in range(6):
            toggle(m, -0.17 + c * 0.068, 0.07 - r * 0.13, mat=rng.choice(["em_amber", "em_red", "chrome", "em_cyan"]), up=rng.random() > 0.4)


def cp_breaker(m, rng):
    plate(m, 0.5, 0.9, "hull_dark")
    for c in range(2):
        for r in range(10):
            x, y = -0.1 + c * 0.2, 0.38 - r * 0.075
            m.box((0.12, 0.05, 0.03), (x, y, 0.055), "black_metal", 0.004)
            m.box((0.05, 0.03, 0.016), (x, y + (0.008 if rng.random() > 0.3 else -0.008), 0.075), "paint_red" if r % 4 == 0 else "plastic_grey", 0.003)
    m.box((0.5, 0.04, 0.02), (0, 0.43, 0.05), "hazard_yellow")


def cp_intercom(m, rng):
    plate(m, 0.22, 0.34, "hull_light", trim="em_green")
    for k in range(6):
        m.box((0.13, 0.008, 0.006), (0, 0.11 + k * 0.016, 0.046), "black_metal")
    m.torus(0.058, 0.006, (0, 0.13, 0.05), "steel", "z", 16, 5)
    pbtn(m, 0, -0.02, "em_green", 0.05)
    m.cyl(0.012, 0.01, (0, -0.1, 0.048), "black_metal", axis="z", seg=8)
    pbtn(m, -0.06, -0.12, "em_red", 0.022)
    pbtn(m, 0.06, -0.12, "em_amber", 0.022)


def cp_lift(m, rng):
    plate(m, 0.16, 0.36, "brushed_alu")
    m.box((0.1, 0.06, 0.008), (0, 0.12, 0.047), "black_metal")
    m.quad((0.09, 0.05), (0, 0.12, 0.052), "screen:text")
    for sy, rot in ((0.02, 0), (-0.09, PI)):
        m.box((0.075, 0.075, 0.012), (0, sy, 0.048), "black_metal", 0.004)
        m.cyl(0.024, 0.01, (0, sy, 0.056), "em_amber", axis="z", seg=3, rot=(0, 0, 0 if rot == 0 else PI))
    m.cyl(0.008, 0.004, (0, -0.16, 0.048), "em_white", axis="z", seg=8)


def cp_env(m, rng):
    plate(m, 0.6, 0.4, "hull_light", trim="em_green")
    m.box((0.22, 0.14, 0.01), (-0.16, 0.08, 0.05), "black_metal", 0.003)
    m.quad((0.2, 0.12), (-0.16, 0.08, 0.056), "screen:lifesigns")
    for k in range(2):
        knob(m, 0.1 + k * 0.1, 0.09, 0.03)
    for k in range(3):
        pbtn(m, -0.24 + k * 0.08, -0.08, BTN[k], 0.035)
    m.box((0.2, 0.012, 0.008), (0.16, -0.03, 0.048), "black_metal")
    m.box((0.03, 0.03, 0.02), (0.13, -0.03, 0.05), "em_cyan")
    m.box((0.2, 0.012, 0.008), (0.16, -0.09, 0.048), "black_metal")
    m.box((0.03, 0.03, 0.02), (0.2, -0.09, 0.05), "em_amber")


def cp_dials(m, rng):
    plate(m, 0.7, 0.3, "hull_dark", trim="em_cyan")
    for k in range(4):
        x = -0.26 + k * 0.17
        m.cyl(0.045, 0.02, (x, 0.04, 0.05), "chrome", axis="z", seg=16)
        m.cyl(0.038, 0.005, (x, 0.04, 0.062), "plastic_white", axis="z", seg=16)
        m.box((0.004, 0.032, 0.004), (x - 0.01, 0.055, 0.066), "paint_red", 0, (0, 0, 0.5 + k))
    for k in range(4):
        x = -0.26 + k * 0.17
        m.box((0.012, 0.09, 0.006), (x, -0.08, 0.046), "black_metal")
        m.box((0.03, 0.015, 0.014), (x, -0.08 + (k - 1.5) * 0.02, 0.052), "plastic_grey", 0.002)


def cp_estop(m, rng):
    plate(m, 0.24, 0.28, "hazard_yellow")
    m.cyl(0.085, 0.02, (0, 0, 0.05), "black_metal", axis="z", seg=20)
    m.cyl(0.07, 0.04, (0, 0, 0.07), "paint_red", axis="z", seg=20, r2=0.06, bevel=0.005)
    m.torus(0.08, 0.006, (0, 0, 0.062), "hazard_yellow", "z", 20, 4)
    m.box((0.16, 0.03, 0.006), (0, -0.11, 0.046), "black_metal")
    hazard(m, -0.1, 0.1, 0.115, 0.046, 0.03)


def cp_keypad(m, rng):
    plate(m, 0.2, 0.3, "gunmetal", trim="em_red")
    m.box((0.12, 0.05, 0.01), (0, 0.1, 0.048), "black_metal")
    m.quad((0.11, 0.04), (0, 0.1, 0.054), "screen:text")
    for r in range(4):
        for c in range(3):
            pbtn(m, -0.05 + c * 0.05, 0.03 - r * 0.048, "plastic_grey", 0.033)
    m.box((0.1, 0.008, 0.01), (0, -0.14, 0.05), "em_red")


def cp_alertlevel(m, rng):
    plate(m, 0.5, 0.22, "hull_dark")
    for k, mm in enumerate(["em_green", "em_cyan", "em_amber", "em_orange", "em_red"]):
        x = -0.19 + k * 0.095
        m.box((0.075, 0.12, 0.015), (x, 0, 0.048), "black_metal", 0.004)
        m.box((0.06, 0.09, 0.012), (x, 0, 0.058), mm, 0.004)
    m.box((0.45, 0.02, 0.008), (0, 0.085, 0.046), "hazard_yellow")


def cp_fusebox(m, rng):
    plate(m, 0.4, 0.55, "hull_mid")
    m.box((0.32, 0.22, 0.02), (0, 0.15, 0.05), "black_metal", 0.004)
    for k in range(6):
        for j in range(2):
            m.cyl(0.014, 0.05, (-0.12 + k * 0.048, 0.19 - j * 0.09 + 0.0, 0.075), "glass_amber" if (k + j) % 3 else "paint_red", axis="z", seg=8)
    m.box((0.34, 0.24, 0.01), (0, -0.14, 0.05), "hull_dark", 0.004)
    m.box((0.06, 0.06, 0.03), (0.12, -0.14, 0.07), "paint_red", 0.005)
    hazard(m, -0.15, 0.15, -0.26, 0.046, 0.03)


def cp_firepull(m, rng):
    plate(m, 0.16, 0.24, "paint_red")
    m.box((0.1, 0.13, 0.03), (0, 0.02, 0.055), "paint_red", 0.006)
    m.box((0.075, 0.03, 0.006), (0, 0.04, 0.072), "plastic_white")
    m.box((0.02, 0.08, 0.016), (0, -0.01, 0.076), "plastic_white", 0.003)
    m.cyl(0.006, 0.004, (0, -0.095, 0.048), "em_red", axis="z", seg=6)
    m.box((0.12, 0.03, 0.008), (0, 0.095, 0.046), "plastic_white")


def cp_lightsw(m, rng):
    m.box((0.12, 0.2, 0.025), (0, 0, 0.0125), "plastic_white", 0.006)
    m.box((0.09, 0.16, 0.012), (0, 0, 0.03), "plastic_grey", 0.004)
    for k in range(2):
        m.box((0.05, 0.05, 0.015), (0, 0.04 - k * 0.08, 0.04), "plastic_white", 0.004, (0.25 * (1 - 2 * k), 0, 0))
        m.box((0.012, 0.012, 0.004), (0.03, 0.04 - k * 0.08 + 0.02, 0.048), "em_amber" if k == 0 else "plastic_black")


def cp_valve(m, rng):
    plate(m, 0.4, 0.4, "hull_dark")
    m.cyl(0.1, 0.03, (0, 0, 0.055), "black_metal", axis="z", seg=16, r2=0.06)
    m.torus(0.085, 0.012, (0, 0, 0.1), "paint_red", "z", 20, 6)
    for k in range(3):
        m.box((0.17, 0.014, 0.014), (0, 0, 0.1), "paint_red", 0.003, (0, 0, k * PI / 3))
    m.cyl(0.015, 0.06, (0, 0, 0.08), "steel", axis="z", seg=8)
    m.box((0.06, 0.03, 0.01), (0, -0.16, 0.046), "hazard_yellow")


def cp_jacks(m, rng):
    plate(m, 0.5, 0.2, "hull_mid")
    for k in range(6):
        x = -0.2 + k * 0.08
        m.cyl(0.02, 0.02, (x, 0.02, 0.05), "steel", axis="z", seg=10)
        m.cyl(0.008, 0.024, (x, 0.02, 0.057), "black_metal", axis="z", seg=8)
        m.box((0.03, 0.012, 0.005), (x, -0.06, 0.046), BTN[k])


def cp_dataport(m, rng):
    plate(m, 0.3, 0.25, "hull_light", trim="em_blue")
    m.box((0.2, 0.05, 0.03), (0, 0.04, 0.055), "black_metal", 0.004)
    m.box((0.15, 0.02, 0.03), (0, 0.04, 0.062), "glass_dark")
    for k in range(3):
        m.box((0.04, 0.012, 0.02), (-0.08 + k * 0.08, -0.05, 0.052), "black_metal")
        m.box((0.01, 0.006, 0.006), (-0.08 + k * 0.08, -0.05, 0.064), "em_cyan")
    m.cyl(0.012, 0.012, (0.11, 0.09, 0.05), "em_green", axis="z", seg=8)


def cp_statuslights(m, rng):
    plate(m, 0.14, 0.62, "hull_dark")
    for k, mm in enumerate(["em_red", "em_orange", "em_amber", "em_green", "em_cyan", "em_blue"]):
        y = 0.24 - k * 0.095
        m.cyl(0.03, 0.02, (0, y, 0.05), "black_metal", axis="z", seg=14)
        m.cyl(0.024, 0.02, (0, y, 0.058), mm if k in (0, 3) else "glass_dark", axis="z", seg=14)


def cp_isolator(m, rng):
    plate(m, 0.3, 0.42, "hazard_yellow")
    m.box((0.22, 0.34, 0.02), (0, 0, 0.05), "black_metal", 0.005)
    m.box((0.05, 0.22, 0.01), (0, 0, 0.065), "steel")
    m.cyl(0.03, 0.03, (0, 0.08, 0.08), "steel", axis="z", seg=12)
    m.link((0, 0.08, 0.08), (0, -0.08, 0.16), 0.014, "black_metal", 8)
    m.box((0.04, 0.1, 0.05), (0, -0.09, 0.165), "paint_red", 0.01, (-0.5, 0, 0))
    m.box((0.05, 0.02, 0.008), (0, 0.16, 0.062), "em_green")
    m.box((0.05, 0.02, 0.008), (0, -0.16, 0.062), "em_red")


def cp_cardreader(m, rng):
    plate(m, 0.16, 0.26, "black_metal", trim="em_cyan")
    m.box((0.1, 0.02, 0.02), (0, 0.04, 0.054), "gunmetal", 0.003)
    m.box((0.085, 0.004, 0.02), (0, 0.04, 0.058), "black_metal")
    m.box((0.1, 0.08, 0.01), (0, 0.1, 0.05), "glass_dark")
    m.quad((0.09, 0.06), (0, 0.1, 0.0555), "screen:text")
    m.cyl(0.015, 0.006, (0, -0.06, 0.05), "em_green", axis="z", seg=10)
    m.cyl(0.015, 0.006, (0, -0.1, 0.05), "em_red", axis="z", seg=10)


def cp_biometric(m, rng):
    plate(m, 0.24, 0.3, "hull_dark", trim="em_violet")
    m.box((0.14, 0.18, 0.012), (0, 0.02, 0.048), "glass_dark", 0.004)
    m.cyl(0.05, 0.01, (0, 0.03, 0.058), "em_violet", axis="z", seg=16)
    m.cyl(0.04, 0.012, (0, 0.03, 0.06), "glass_dark", axis="z", seg=16)
    m.box((0.14, 0.006, 0.006), (0, -0.09, 0.05), "em_violet")
    m.torus(0.06, 0.005, (0, 0.03, 0.062), "chrome", "z", 16, 4)


def cp_airlock(m, rng):
    plate(m, 0.36, 0.5, "hull_light", trim="em_amber")
    m.box((0.24, 0.1, 0.01), (0, 0.17, 0.05), "black_metal", 0.003)
    m.quad((0.22, 0.08), (0, 0.17, 0.056), "screen:hazard")
    pbtn(m, -0.08, 0.04, "em_green", 0.06)
    pbtn(m, 0.08, 0.04, "em_red", 0.06)
    m.box((0.24, 0.04, 0.008), (0, -0.04, 0.046), "black_metal")
    for k in range(4):
        m.cyl(0.012, 0.012, (-0.09 + k * 0.06, -0.04, 0.052), BTN[k], axis="z", seg=8)
    knob(m, 0, -0.14, 0.04, mat="paint_red")
    hazard(m, -0.15, 0.15, -0.22, 0.046, 0.03)


CPANELS = [("switch bank", cp_switch), ("breaker bank", cp_breaker), ("intercom station", cp_intercom),
           ("lift call", cp_lift), ("environment control", cp_env), ("dials and sliders", cp_dials),
           ("emergency stop", cp_estop), ("keypad lock", cp_keypad), ("alert level", cp_alertlevel),
           ("fuse box", cp_fusebox), ("fire pull station", cp_firepull), ("light switch", cp_lightsw),
           ("valve control", cp_valve), ("comm jack panel", cp_jacks), ("data port", cp_dataport),
           ("status light strip", cp_statuslights), ("power isolator", cp_isolator),
           ("card reader", cp_cardreader), ("biometric scanner", cp_biometric), ("airlock control", cp_airlock)]


@family("controlpanel", [n for n, _ in CPANELS], mount="wall", tags=["bridge", "panel"], solid=False, mount_y=1.5)
def bridge_controlpanel(m, i, label, rng):
    CPANELS[i][1](m, rng)


# ---------------------------------------------------------------- holo (floor)
def _holo_base(m, r=0.4, h=0.9, mat="hull_dark", trim="em_cyan"):
    m.cyl(r, h, (0, h / 2, 0), mat, seg=24, r2=r * 0.85, bevel=0.01)
    m.torus(r * 0.93, 0.012, (0, h * 0.35, 0), trim, "y", 24, 4)
    m.cyl(r * 0.8, 0.03, (0, h + 0.015, 0), "black_metal", seg=24, bevel=0.005)
    m.cyl(r * 0.5, 0.012, (0, h + 0.036, 0), trim, seg=24)


def h_table(m, rng):
    _holo_base(m, 0.8, 0.85, "hull_mid")
    m.cyl(0.55, 0.9, (0, 1.34, 0), "glass_blue", seg=24, r2=0.15)
    for k in range(3):
        m.torus(0.15 + 0.13 * k, 0.006, (0, 0.92 + 0.0, 0), "em_cyan", "y", 20, 4)
    m.sphere(0.06, (0, 1.15, 0), "glass_blue", seg=12, ring=8)
    for k in range(6):
        a = k * PI / 3
        m.box((0.05, 0.03, 0.05), (0.7 * math.cos(a), 0.9, 0.7 * math.sin(a)), rng.choice(BTN), 0.003)


def h_globe(m, rng):
    _holo_base(m, 0.35, 1.0, "gunmetal", "em_blue")
    m.sphere(0.32, (0, 1.42, 0), "glass_blue", seg=24, ring=16)
    m.sphere(0.16, (0, 1.42, 0), "em_cyan", seg=16, ring=10)
    m.torus(0.34, 0.008, (0, 1.42, 0), "em_blue", "y", 24, 4, rot=(0.4, 0, 0))
    m.torus(0.34, 0.008, (0, 1.42, 0), "brass", "z", 24, 4, rot=(0.4, 0.6, 0))
    m.cyl(0.02, 0.1, (0, 1.06, 0), "em_cyan", seg=8)
    m.cyl(0.08, 0.06, (0, 1.04, 0), "black_metal", seg=12, r2=0.05)


def h_tactical(m, rng):
    m.box((0.9, 0.7, 0.9), (0, 0.35, 0), "hull_dark", 0.02)
    hazard(m, -0.4, 0.4, 0.1, 0.451, 0.05)
    m.box((1.0, 0.06, 1.0), (0, 0.73, 0), "hull_mid", 0.015)
    m.box((0.8, 0.02, 0.8), (0, 0.77, 0), "black_metal")
    for i in range(4):
        for j in range(4):
            m.box((0.19, 0.005, 0.19), (-0.3 + i * 0.2, 0.782, -0.3 + j * 0.2), "em_red" if (i + j) % 2 else "gunmetal")
    m.box((0.4, 0.35, 0.4), (0, 1.0, 0), "glass_blue", 0.0)
    m.prism([(-0.16, -0.16), (0.16, -0.16), (0.16, 0.16), (-0.16, 0.16)], 0.22, (0, 0.79, 0), "em_red")
    m.prism([(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)], 0.5, (0.2, 0.79, -0.2), "em_amber")
    for k in range(4):
        a = k * PI / 2 + PI / 4
        m.box((0.05, 0.03, 0.05), (0.42 * math.cos(a), 0.79, 0.42 * math.sin(a)), "em_cyan")


def h_schematic(m, rng):
    _holo_base(m, 0.45, 0.8, "hull_mid", "em_cyan")
    m.prism([(0, 0.4), (0.06, 0.15), (0.16, -0.1), (0.1, -0.3), (0.0, -0.36), (-0.1, -0.3), (-0.16, -0.1), (-0.06, 0.15)],
            0.02, (0, 1.4, 0), "glass_blue")
    m.prism([(0, 0.4), (0.06, 0.15), (-0.06, 0.15)], 0.05, (0, 1.4, 0), "em_cyan")
    m.prism([(0.16, -0.1), (0.4, -0.25), (0.4, -0.3), (0.1, -0.3)], 0.02, (0, 1.4, 0), "glass_blue")
    m.prism([(-0.16, -0.1), (-0.4, -0.25), (-0.4, -0.3), (-0.1, -0.3)], 0.02, (0, 1.4, 0), "glass_blue")
    m.box((0.8, 0.005, 0.005), (0, 1.41, 0), "em_cyan")
    m.box((0.005, 0.005, 0.8), (0, 1.41, 0), "em_cyan")
    m.cyl(0.25, 0.65, (0, 1.12, 0), "glass_blue", seg=20, r2=0.02)
    for sx in (-1, 1):
        m.link((sx * 0.3, 0.9, 0), (sx * 0.4, 1.4, 0), 0.008, "em_cyan", 6)


def h_briefing(m, rng):
    m.cyl(0.3, 0.05, (0, 0.025, 0), "hull_dark", seg=20, bevel=0.008)
    m.cyl(0.06, 1.0, (0, 0.55, 0), "steel", seg=10)
    m.box((0.36, 0.22, 0.4), (0, 1.15, 0), "hull_light", 0.03)
    m.cyl(0.11, 0.14, (0, 1.15, 0.28), "black_metal", axis="z", seg=16, r2=0.14)
    m.cyl(0.09, 0.02, (0, 1.15, 0.36), "glass_blue", axis="z", seg=16)
    m.box((0.5, 0.36, 0.01), (0, 1.15, 0.9), "glass_blue")
    m.link((0, 1.15, 0.36), (0.25, 1.32, 0.9), 0.005, "em_cyan", 5)
    m.link((0, 1.15, 0.36), (-0.25, 1.32, 0.9), 0.005, "em_cyan", 5)
    m.link((0, 1.15, 0.36), (0.25, 0.98, 0.9), 0.005, "em_cyan", 5)
    m.link((0, 1.15, 0.36), (-0.25, 0.98, 0.9), 0.005, "em_cyan", 5)
    m.box((0.26, 0.04, 0.3), (0, 1.28, -0.05), "hull_mid", 0.008)
    for k in range(3):
        m.box((0.03, 0.01, 0.03), (-0.06 + k * 0.06, 1.305, -0.05), BTN[k])


def h_pillar(m, rng):
    m.cyl(0.32, 0.3, (0, 0.15, 0), "hull_dark", seg=8, r2=0.24, bevel=0.01)
    m.cyl(0.14, 0.9, (0, 0.75, 0), "hull_mid", seg=8)
    for k in range(5):
        m.torus(0.145, 0.01, (0, 0.4 + k * 0.16, 0), "em_violet", "y", 16, 4)
    m.cyl(0.2, 0.05, (0, 1.22, 0), "black_metal", seg=8, r2=0.14)
    m.box((0.5, 0.5, 0.5), (0, 1.62, 0), "glass_blue", 0.0, (0.6, 0.8, 0))
    m.box((0.28, 0.28, 0.28), (0, 1.62, 0), "em_violet", 0.0, (0.6, 0.8, 0))


def h_terrace(m, rng):
    m.cyl(0.55, 0.12, (0, 0.06, 0), "hull_dark", seg=28, bevel=0.01)
    m.cyl(0.5, 0.5, (0, 0.37, 0), "hull_mid", seg=28, r2=0.4, bevel=0.008)
    for k in range(4):
        r = 0.45 - k * 0.09
        m.torus(r, 0.014, (0, 0.65 + k * 0.17, 0), ["em_cyan", "em_blue", "em_cyan", "em_white"][k], "y", 24, 5)
        m.cyl(r, 0.012, (0, 0.65 + k * 0.17, 0), "glass_blue", seg=24)
        m.link((r * 0.7, 0.62 + k * 0.17, 0), (r * 0.7, 0.66 + k * 0.17, 0), 0.006, "em_white", 4)
    m.cyl(0.02, 0.6, (0, 0.95, 0), "em_cyan", seg=6)
    m.torus(0.49, 0.008, (0, 0.5, 0), "em_cyan", "y", 28, 4)


def h_bust(m, rng):
    m.cyl(0.28, 0.75, (0, 0.375, 0), "hull_dark", seg=16, r2=0.22, bevel=0.01)
    m.torus(0.26, 0.012, (0, 0.6, 0), "em_amber", "y", 20, 4)
    m.cyl(0.21, 0.03, (0, 0.765, 0), "black_metal", seg=16)
    m.cyl(0.18, 0.7, (0, 1.13, 0), "glass_amber", seg=16, r2=0.06)
    m.sphere(0.09, (0, 1.2, 0), "em_amber", seg=12, ring=8)
    m.sphere(0.05, (0, 1.37, 0), "em_amber", seg=10, ring=6)
    m.cyl(0.04, 0.06, (0, 1.29, 0), "em_amber", seg=8)
    for k in range(3):
        m.box((0.05, 0.03, 0.02), (-0.08 + k * 0.08, 0.35, 0.235), BTN[k + 3], 0.003, (0, 0, 0))


HOLOS = [("briefing table", h_table), ("star map globe", h_globe), ("tactical plinth", h_tactical),
         ("ship schematic projector", h_schematic), ("briefing projector", h_briefing),
         ("holo emitter pillar", h_pillar), ("terrain terrace", h_terrace), ("comm bust projector", h_bust)]


@family("holo", [n for n, _ in HOLOS], mount="floor", tags=["bridge", "holo"], solid=True)
def bridge_holo(m, i, label, rng):
    HOLOS[i][1](m, rng)


# ---------------------------------------------------------------- terminals
def t_desk(m, rng):
    m.box((0.36, 0.03, 0.26), (0, 0.015, 0), "hull_dark", 0.008)
    m.box((0.1, 0.16, 0.06), (0, 0.11, -0.06), "hull_mid", 0.01)
    mon(m, 0.34, 0.22, (0, 0.28, -0.06), "systems", (-0.15, 0, 0), 0.015, 0.04, "hull_dark")
    m.box((0.3, 0.015, 0.1), (0, 0.037, 0.08), "plastic_black", 0.004)
    for k in range(8):
        m.box((0.028, 0.008, 0.028), (-0.105 + k * 0.03, 0.048, 0.08), "plastic_grey", 0.002)
    m.box((0.36, 0.01, 0.01), (0, 0.035, 0.13), "em_cyan")


def t_datapad(m, rng):
    m.box((0.2, 0.012, 0.14), (0, 0.006, 0), "plastic_black", 0.004)
    m.box((0.19, 0.003, 0.13), (0, 0.0135, 0), "hull_dark")
    m.quad((0.17, 0.11), (0, 0.0155, 0.0), "screen:text", (-PI / 2, 0, 0))
    m.box((0.02, 0.004, 0.008), (0.07, 0.014, 0.062), "em_green")
    m.box((0.2, 0.012, 0.006), (0, 0.006, 0.073), "steel", 0.002)


def t_padstack(m, rng):
    for k in range(3):
        m.box((0.2 - 0.01 * k, 0.012, 0.14), (0.01 * (k - 1), 0.006 + k * 0.014, 0.01 * (k - 1)), ["plastic_grey", "hull_dark", "plastic_white"][k], 0.004, (0, 0.15 * k, 0))
    m.quad((0.16, 0.1), (0.0, 0.0425, 0.0), "screen:medical", (-PI / 2, 0.3, 0))


def t_reader(m, rng):
    m.box((0.12, 0.03, 0.2), (0, 0.015, 0), "hull_light", 0.01)
    m.box((0.1, 0.004, 0.11), (0, 0.032, -0.03), "black_metal")
    m.quad((0.09, 0.09), (0, 0.035, -0.03), "screen:diagnostic", (-PI / 2, 0, 0))
    for k in range(3):
        m.cyl(0.011, 0.006, (-0.03 + k * 0.03, 0.033, 0.07), "chrome", seg=8)
    m.box((0.02, 0.008, 0.05), (0.0, 0.034, 0.1), "em_cyan")


def t_keyboard(m, rng):
    m.box((0.42, 0.02, 0.15), (0, 0.01, 0), "plastic_black", 0.005)
    for r in range(4):
        for c in range(12):
            m.box((0.027, 0.008, 0.024), (-0.15 + c * 0.0275, 0.024, -0.05 + r * 0.03), "plastic_grey" if (r + c) % 5 else "em_amber", 0.001)


def t_handset(m, rng):
    m.box((0.12, 0.05, 0.1), (0, 0.025, 0), "hull_dark", 0.01)
    m.box((0.05, 0.02, 0.085), (0.0, 0.058, 0), "black_metal", 0.004)
    m.link((-0.09, 0.09, 0.0), (0.09, 0.09, 0.0), 0.017, "plastic_black", 8)
    m.cyl(0.03, 0.04, (-0.1, 0.075, 0), "plastic_black", axis="y", seg=10, bevel=0.004)
    m.cyl(0.026, 0.04, (0.1, 0.075, 0), "plastic_black", axis="y", seg=10, bevel=0.004)
    m.box((0.02, 0.02, 0.02), (0, 0.06, 0.04), "em_green")
    m.box((0.1, 0.005, 0.005), (0, 0.07, 0.048), "steel")


def t_headset(m, rng):
    m.cyl(0.08, 0.02, (0, 0.01, 0), "hull_dark", seg=16, bevel=0.004)
    m.cyl(0.015, 0.2, (0, 0.11, -0.02), "steel", seg=8)
    m.box((0.04, 0.05, 0.05), (0, 0.22, -0.02), "hull_dark", 0.006)
    m.torus(0.085, 0.01, (0, 0.27, -0.0), "plastic_black", "z", 16, 6, arc=PI, rot=(0, 0, 0))
    for sx in (-1, 1):
        m.cyl(0.03, 0.03, (sx * 0.085, 0.235, 0), "plastic_black", axis="x", seg=10)
    m.tube([(0.09, 0.24, 0.0), (0.1, 0.2, 0.05), (0.06, 0.17, 0.08)], 0.004, "black_metal", 5)
    m.box((0.05, 0.01, 0.05), (0, 0.022, 0.05), "em_cyan")


def t_intercom(m, rng):
    m.box((0.2, 0.05, 0.16), (0, 0.025, 0), "hull_light", 0.01)
    m.box((0.18, 0.06, 0.08), (0, 0.075, -0.04), "hull_light", 0.01, (0.4, 0, 0))
    for k in range(4):
        m.cyl(0.018, 0.012, (-0.06 + k * 0.04, 0.056, 0.04), BTN[k], seg=8)
    m.box((0.1, 0.012, 0.005), (0, 0.07, -0.058), "black_metal", 0, (0.4, 0, 0))
    for k in range(3):
        m.box((0.09, 0.003, 0.005), (0, 0.078 + k * 0.006, -0.04 - 0.0), "black_metal", 0, (0.4, 0, 0))


def t_laptop(m, rng):
    m.box((0.34, 0.02, 0.24), (0, 0.01, 0.03), "hull_mid", 0.006)
    m.box((0.3, 0.004, 0.12), (0, 0.022, 0.06), "plastic_black")
    m.box((0.1, 0.004, 0.06), (0, 0.022, -0.03), "plastic_grey")
    mon(m, 0.3, 0.2, (0, 0.13, -0.085), "text", (-0.2, 0, 0), 0.012, 0.015, "hull_mid")
    m.box((0.34, 0.012, 0.012), (0, 0.02, -0.09), "steel")


def t_kiosk(m, rng):
    m.box((0.5, 0.05, 0.4), (0, 0.025, 0), "hull_dark", 0.01)
    m.prism([(-0.15, -0.14), (0.15, -0.14), (0.15, 0.12), (-0.15, 0.12)], 0.9, (0, 0.05, 0), "hull_light", bevel=0.01)
    m.box((0.32, 0.5, 0.05), (0, 1.15, -0.02), "hull_light", 0.02, (-0.15, 0, 0))
    mon(m, 0.28, 0.42, (0, 1.16, 0.016), "systems", (-0.15, 0, 0), 0.015, 0.02)
    m.box((0.3, 0.05, 0.12), (0, 0.98, 0.1), "hull_mid", 0.01)
    for k in range(4):
        m.box((0.05, 0.012, 0.05), (-0.09 + k * 0.06, 1.01, 0.1), BTN[k], 0.002)
    m.box((0.12, 0.02, 0.02), (0, 0.7, 0.125), "black_metal")
    m.box((0.3, 0.012, 0.01), (0, 0.06, 0.15), "em_cyan")


def t_pedestal(m, rng):
    m.cyl(0.22, 0.05, (0, 0.025, 0), "hull_dark", seg=20, bevel=0.008)
    m.cyl(0.08, 1.0, (0, 0.55, 0), "steel", seg=12, r2=0.06)
    m.box((0.36, 0.28, 0.06), (0, 1.15, 0), "hull_mid", 0.015, (-0.5, 0, 0))
    mon(m, 0.32, 0.24, (0, 1.17, 0.03), "nav", (-0.5, 0, 0), 0.012, 0.02)
    m.torus(0.085, 0.008, (0, 0.5, 0), "em_amber", "y", 14, 4)


def t_ticket(m, rng):
    m.box((0.6, 1.5, 0.35), (0, 0.75, 0), "paint_blue", 0.02)
    m.box((0.6, 0.06, 0.37), (0, 0.03, 0.0), "hull_dark", 0.008)
    mon(m, 0.4, 0.3, (0, 1.2, 0.18), "text", (0, 0, 0), 0.015, 0.02)
    m.box((0.36, 0.05, 0.05), (0, 0.9, 0.18), "black_metal", 0.006)
    m.box((0.3, 0.008, 0.03), (0, 0.9, 0.206), "em_green")
    m.box((0.25, 0.18, 0.05), (0, 0.62, 0.18), "black_metal", 0.006)
    m.box((0.2, 0.03, 0.02), (0, 0.55, 0.21), "hull_mid")
    for k in range(3):
        m.box((0.05, 0.05, 0.02), (-0.1 + k * 0.1, 0.72, 0.19), BTN[k + 1], 0.003)
    m.box((0.6, 0.1, 0.4), (0, 1.55, 0), "paint_blue", 0.02)


TERM_TABLE = [("desk terminal", t_desk), ("datapad", t_datapad), ("datapad stack", t_padstack),
              ("portable reader", t_reader), ("keyboard", t_keyboard), ("comm handset", t_handset),
              ("headset dock", t_headset), ("desk intercom", t_intercom), ("laptop console", t_laptop)]
TERM_FLOOR = [("info kiosk", t_kiosk), ("pedestal terminal", t_pedestal), ("ticket kiosk", t_ticket)]


@family("terminal", [n for n, _ in TERM_TABLE], mount="table", tags=["bridge", "terminal"], solid=False)
def bridge_terminal_small(m, i, label, rng):
    TERM_TABLE[i][1](m, rng)


@family("terminal", [n for n, _ in TERM_FLOOR], mount="floor", tags=["bridge", "terminal", "kiosk"], solid=True)
def bridge_terminal_floor(m, i, label, rng):
    TERM_FLOOR[i][1](m, rng)


# ---------------------------------------------------------------- instruments
def _dial_face(m, x, y, z, r, tex=None, rim="chrome", face="plastic_white", axis="z"):
    m.cyl(r, 0.03, (x, y, z), "black_metal", axis="z", seg=20, bevel=0.003)
    m.torus(r * 0.93, r * 0.09, (x, y, z + 0.015), rim, "z", 20, 6)
    m.cyl(r * 0.85, 0.004, (x, y, z + 0.016), face, axis="z", seg=20)
    if tex:
        m.quad((r * 1.5, r * 1.5), (x, y, z + 0.0185), "screen:" + tex)


def i_table_astrolabe(m, rng):
    m.cyl(0.11, 0.03, (0, 0.015, 0), "wood_dark", seg=20, bevel=0.005)
    m.cyl(0.02, 0.1, (0, 0.08, 0), "brass", seg=8)
    m.torus(0.09, 0.006, (0, 0.17, 0), "brass", "z", 24, 6)
    m.torus(0.09, 0.006, (0, 0.17, 0), "brass", "x", 24, 6)
    m.torus(0.065, 0.005, (0, 0.17, 0), "gold_trim", "y", 20, 5)
    m.sphere(0.02, (0, 0.17, 0), "brass", seg=10, ring=6)
    m.link((0, 0.17, 0), (0.08, 0.24, 0.0), 0.004, "brass", 5)


def i_table_sextant(m, rng):
    m.box((0.2, 0.02, 0.14), (0, 0.01, 0), "wood_dark", 0.005)
    m.prism([(0, 0.0), (0.15, 0.08), (0.15, -0.07)], 0.015, (-0.07, 0.02, 0), "brass", plane="xz", bevel=0.002)
    m.torus(0.15, 0.005, (-0.07, 0.03, 0), "gold_trim", "y", 12, 5, arc=0.85, rot=(0, -0.42, 0))
    m.link((-0.07, 0.04, 0), (0.06, 0.04, 0.06), 0.004, "brass", 5)
    m.cyl(0.02, 0.03, (0.06, 0.05, -0.05), "chrome", axis="z", seg=10)
    m.cyl(0.006, 0.05, (0.1, 0.05, 0.05), "black_metal", axis="x", seg=6)
    m.box((0.02, 0.02, 0.02), (-0.06, 0.04, -0.02), "glass")


def i_table_compass(m, rng):
    m.box((0.2, 0.06, 0.2), (0, 0.03, 0), "wood_dark", 0.008)
    m.cyl(0.085, 0.04, (0, 0.07, 0), "brass", seg=24, bevel=0.004)
    m.cyl(0.075, 0.005, (0, 0.092, 0), "plastic_white", seg=24)
    m.cyl(0.075, 0.008, (0, 0.099, 0), "glass", seg=24)
    m.box((0.01, 0.004, 0.13), (0, 0.096, 0), "paint_red", 0, (0, 0.7, 0))
    m.box((0.01, 0.004, 0.13), (0, 0.095, 0), "steel", 0, (0, 0.7 + PI / 2, 0))
    for k in range(4):
        a = k * PI / 2
        m.box((0.008, 0.003, 0.02), (0.06 * math.sin(a), 0.095, 0.06 * math.cos(a)), "black_metal", 0, (0, a, 0))
    m.torus(0.1, 0.006, (0, 0.11, 0), "gold_trim", "y", 24, 5)


def i_table_chrono(m, rng):
    m.box((0.24, 0.1, 0.18), (0, 0.05, 0), "wood_dark", 0.01)
    m.box((0.22, 0.008, 0.16), (0, 0.101, 0), "brass", 0.002)
    m.cyl(0.06, 0.02, (0, 0.11, 0.0), "brass", seg=20, bevel=0.003)
    m.cyl(0.05, 0.004, (0, 0.122, 0), "plastic_white", seg=20)
    m.box((0.004, 0.003, 0.035), (0, 0.126, 0.015), "black_metal", 0, (0, 0.6, 0))
    m.box((0.004, 0.003, 0.045), (0, 0.128, -0.02), "paint_red", 0, (0, 2.4, 0))
    m.box((0.01, 0.014, 0.01), (0.09, 0.11, 0.06), "gold_trim")
    m.box((0.01, 0.014, 0.01), (-0.09, 0.11, 0.06), "gold_trim")


def i_table_sensor(m, rng):
    m.cyl(0.1, 0.03, (0, 0.015, 0), "hull_dark", seg=16, bevel=0.005)
    m.cyl(0.03, 0.12, (0, 0.09, 0), "steel", seg=8)
    m.cyl(0.02, 0.1, (0, 0.2, 0), "hull_mid", seg=8)
    for k in range(4):
        a = k * PI / 2 + PI / 4
        m.link((0, 0.2, 0), (0.09 * math.cos(a), 0.26, 0.09 * math.sin(a)), 0.004, "brushed_alu", 5)
        m.sphere(0.014, (0.09 * math.cos(a), 0.26, 0.09 * math.sin(a)), "em_cyan" if k % 2 else "em_amber", seg=8, ring=5)
    m.sphere(0.03, (0, 0.27, 0), "chrome", seg=10, ring=8)
    m.cyl(0.04, 0.01, (0, 0.14, 0), "black_metal", seg=10)


def i_wall_gauges(m, rng):
    m.box((0.6, 0.24, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
    for k in range(3):
        _dial_face(m, -0.2 + k * 0.2, 0.0, 0.04, 0.085, None)
        m.box((0.004, 0.06, 0.004), (-0.2 + k * 0.2, 0.03, 0.06), "paint_red", 0, (0, 0, 0.9 * k - 0.7))
    m.box((0.6, 0.01, 0.01), (0, -0.11, 0.045), "em_amber")


def i_wall_radar(m, rng):
    m.cyl(0.24, 0.1, (0, 0, 0.05), "hull_dark", axis="z", seg=24, bevel=0.008)
    m.torus(0.2, 0.02, (0, 0, 0.1), "chrome", "z", 24, 6)
    m.cyl(0.19, 0.01, (0, 0, 0.1), "black_metal", axis="z", seg=24)
    m.quad((0.28, 0.28), (0, 0, 0.106), "screen:radar")
    m.box((0.04, 0.06, 0.08), (0, -0.27, 0.04), "hull_mid", 0.006)
    for sx in (-1, 1):
        m.cyl(0.02, 0.03, (sx * 0.27, 0, 0.04), "chrome", axis="x", seg=8)


def i_wall_attitude(m, rng):
    m.box((0.3, 0.3, 0.06), (0, 0, 0.03), "black_metal", 0.012)
    m.torus(0.12, 0.014, (0, 0, 0.065), "chrome", "z", 24, 6)
    m.cyl(0.115, 0.02, (0, 0, 0.055), "black_metal", axis="z", seg=24)
    m.sphere(0.1, (0, 0, 0.055), "paint_blue", seg=20, ring=12, scale=(1, 1, 0.3))
    m.box((0.2, 0.01, 0.02), (0, 0.0, 0.08), "paint_orange")
    m.box((0.2, 0.005, 0.01), (0, 0.0, 0.09), "em_white")
    m.box((0.04, 0.008, 0.012), (0, 0.06, 0.09), "em_amber", 0, (0, 0, 0))
    m.box((0.1, 0.008, 0.012), (0.0, 0.03, 0.09), "em_white")
    m.cyl(0.006, 0.02, (0.13, -0.13, 0.07), "brass", axis="z", seg=6)


def i_wall_depth(m, rng):
    m.box((0.28, 0.4, 0.06), (0, 0, 0.03), "brass", 0.012)
    m.box((0.22, 0.34, 0.01), (0, 0, 0.065), "black_metal", 0.003)
    m.quad((0.2, 0.32), (0, 0, 0.0705), "screen:bars")
    for k in range(9):
        m.box((0.03 if k % 2 == 0 else 0.018, 0.004, 0.004), (0.09, -0.14 + k * 0.035, 0.075), "em_white")
    m.cyl(0.02, 0.02, (0, -0.24, 0.03), "steel", axis="y", seg=8)
    bolts(m, [(-0.115, 0.17, 0.062), (0.115, 0.17, 0.062), (-0.115, -0.17, 0.062), (0.115, -0.17, 0.062)], 0.008, "gold_trim")


def i_wall_pressure(m, rng):
    m.cyl(0.14, 0.07, (0, 0, 0.035), "copper", axis="z", seg=24, bevel=0.005)
    m.torus(0.12, 0.014, (0, 0, 0.075), "brass", "z", 24, 6)
    m.cyl(0.11, 0.008, (0, 0, 0.07), "plastic_white", axis="z", seg=24)
    for k in range(11):
        a = -2.3 + k * 0.46
        m.box((0.006, 0.02, 0.004), (0.09 * math.sin(a), 0.09 * math.cos(a), 0.076), "black_metal", 0, (0, 0, -a))
    m.box((0.006, 0.09, 0.004), (0.02, 0.03, 0.08), "paint_red", 0, (0, 0, -0.6))
    m.cyl(0.012, 0.014, (0, 0, 0.082), "brass", axis="z", seg=8)
    m.cyl(0.015, 0.05, (0, -0.17, 0.035), "copper", seg=8)
    m.cyl(0.11, 0.008, (0, 0, 0.082), "glass", axis="z", seg=24)


INST_TABLE = [("astrolabe", i_table_astrolabe), ("sextant", i_table_sextant), ("nav compass", i_table_compass),
              ("brass chronometer", i_table_chrono), ("sensor array", i_table_sensor)]
INST_WALL = [("gauge cluster", i_wall_gauges), ("radar scope", i_wall_radar), ("attitude indicator", i_wall_attitude),
             ("depth meter", i_wall_depth), ("pressure meter", i_wall_pressure)]


@family("instrument", [n for n, _ in INST_TABLE], mount="table", tags=["bridge", "instrument"], solid=False)
def bridge_instrument_table(m, i, label, rng):
    INST_TABLE[i][1](m, rng)


@family("instrument", [n for n, _ in INST_WALL], mount="wall", tags=["bridge", "instrument"], solid=False, mount_y=1.5)
def bridge_instrument_wall(m, i, label, rng):
    INST_WALL[i][1](m, rng)
