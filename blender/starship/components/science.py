"""Science components: lab benches, microscopes, analyzers, specimens, instruments,
telescopes and particle-physics demonstrators (50 labels)."""
import math

from mathutils import Euler, Vector

from ..kit import family, register_material

register_material("sci_epoxy", "#28363a", 0.1, 0.3)
register_material("sci_white", "#eceff0", 0.15, 0.35)
register_material("sci_teal", "#2a7f86", 0.3, 0.4)
register_material("sci_liquid_g", "#59d86e", 0, 0.1, alpha=0.45)
register_material("sci_liquid_p", "#b06be0", 0, 0.1, alpha=0.45)
register_material("sci_liquid_o", "#f0a03a", 0, 0.1, alpha=0.45)
register_material("sci_liquid_b", "#5aa4e8", 0, 0.1, alpha=0.4)
register_material("sci_water", "#3d8fbf", 0, 0.1, alpha=0.4)
register_material("sci_frost", "#cfe6f2", 0.1, 0.6)
register_material("sci_crystal", "#8fe7ff", 0, 0.1, emission=2.2)
register_material("sci_crystal2", "#c07aff", 0, 0.1, emission=2.2)
register_material("sci_plasma", "#ff5fd8", 0, 0.1, emission=3.5)


def led(m, p, mat="em_green", s=0.014):
    m.box((s, s, 0.01), p, mat)


def leds(m, x0, y, z, n, dx, mats, s=0.014):
    for k in range(n):
        m.box((s, s, 0.01), (x0 + k * dx, y, z), mats[k % len(mats)])


def rp(p, rot, c):
    v = Euler(rot, "XYZ").to_matrix() @ Vector(p)
    return (v.x + c[0], v.y + c[1], v.z + c[2])


def cab(m, w, h, d, mat, y0=0.0, bevel=0.015, x=0.0, z=0.0):
    m.box((w, h, d), (x, y0 + h / 2, z), mat, bevel)


def handle(m, x, y, z, horiz=True, l=0.14):
    if horiz:
        m.box((l, 0.018, 0.022), (x, y, z), "chrome")
    else:
        m.box((0.018, l, 0.022), (x, y, z), "chrome")


def bottle(m, x, y, z, r, h, mat, cap="plastic_black"):
    m.cyl(r, h, (x, y + h / 2, z), mat, seg=8)
    m.cyl(r * 0.5, h * 0.18, (x, y + h * 1.09, z), cap, seg=8)


def star_base(m, y, r, mat="black_metal", n=5, caster=True):
    for k in range(n):
        a = 2 * math.pi * k / n
        px, pz = math.cos(a) * r, math.sin(a) * r
        m.link((0, y + 0.08, 0), (px, y + 0.03, pz), 0.018, mat, seg=6)
        if caster:
            m.sphere(0.03, (px, 0.03, pz), "rubber", seg=8, ring=6)


def dish(m, c, r, rot=(0, 0, 0), mat="paint_white", depth=0.08, feed=True):
    """Parabolic dish facing +Z (local) rotated by rot about centre c."""
    m.cyl(r, depth, c, mat, axis="z", seg=20, r2=r * 0.25, rot=rot)
    m.cyl(r * 0.28, depth * 0.6, rp((0, 0, -depth * 0.6), rot, c), "black_metal", axis="z", seg=10, rot=rot)
    m.torus(r, r * 0.02, rp((0, 0, depth * 0.5), rot, c), "brushed_alu", axis="z", seg=24, tseg=5, rot=rot)
    if feed:
        tip = rp((0, 0, r * 0.55), rot, c)
        for a in (0, 2.1, 4.2):
            m.link(rp((math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, depth * 0.5), rot, c), tip, 0.008, "steel", seg=5)
        m.cyl(r * 0.07, r * 0.12, tip, "chrome", axis="z", seg=8, r2=r * 0.04, rot=rot)


def hazard(m, x, y, z, w, h):
    m.box((w, h, 0.008), (x, y, z), "hazard_yellow")
    for k in range(int(w / 0.06)):
        m.box((0.02, h * 0.98, 0.004), (x - w / 2 + 0.05 + k * 0.06, y, z + 0.004), "black_metal", rot=(0, 0, 0.5))


def hood_arm(m):
    pass


TAG = ["science"]
_TABLES = []


def _reg(cat, table, **kw):
    def fn(m, i, label, rng):
        table[label](m, rng)
    fn.__name__ = "sci_" + cat + "_" + kw.get("mount", "floor")
    family(cat, list(table), **kw)(fn)


def _add(table, label):
    def deco(f):
        table[label] = f
        return f
    return deco


# ==========================================================================
# LAB BENCHES
# ==========================================================================
LB = {}


@_add(LB, "wet bench sink")
def _(m, rng):
    W, D = 2.0, 0.75
    m.box((W, 0.04, D + 0.04), (0, 0.88, 0), "sci_epoxy", 0.008)
    cab(m, W - 0.04, 0.72, D - 0.04, "sci_white", 0.08)
    m.box((W - 0.06, 0.08, D - 0.1), (0, 0.04, -0.01), "black_metal")
    for k in range(3):
        x = -0.66 + k * 0.66
        m.box((0.62, 0.66, 0.02), (x, 0.47, D / 2 - 0.015), "hull_light")
        handle(m, x + (0.24 if k < 2 else -0.24), 0.68, D / 2 + 0.005, False, 0.12)
    # sink
    m.box((0.62, 0.012, 0.42), (-0.45, 0.905, 0.04), "black_metal")
    for dx, dz, sx, sz in ((0, 0.23, 0.68, 0.04), (0, -0.15, 0.68, 0.04), (-0.33, 0.04, 0.04, 0.42), (0.33, 0.04, 0.04, 0.42)):
        m.box((sx, 0.02, sz), (-0.45 + dx, 0.905, 0.04 + dz * 0.9), "steel")
    m.box((0.06, 0.008, 0.28), (-0.45, 0.915, 0.04), "steel")
    m.tube([(-0.45, 0.9, -0.22), (-0.45, 1.18, -0.22), (-0.45, 1.27, -0.12), (-0.45, 1.2, -0.02)], 0.014, "chrome")
    m.cyl(0.02, 0.05, (-0.45, 1.16, -0.02), "chrome", seg=6)
    m.cyl(0.035, 0.03, (-0.62, 0.93, -0.22), "paint_red", seg=8)
    m.cyl(0.035, 0.03, (-0.28, 0.93, -0.22), "paint_blue", seg=8)
    # reagent shelf over the back
    for sx in (-0.95, 0.95):
        m.box((0.04, 0.8, 0.04), (sx, 1.3, -D / 2 + 0.05), "steel", 0.004)
    m.box((W - 0.04, 0.03, 0.22), (0, 1.55, -D / 2 + 0.1), "sci_white", 0.005)
    m.box((W - 0.04, 0.6, 0.02), (0, 1.25, -D / 2 + 0.02), "hull_light")
    for k in range(9):
        bottle(m, 0.05 + k * 0.1 - 0.9 + 0.05, 1.565, -D / 2 + 0.1, 0.035, 0.12, ["glass_amber", "glass_green", "glass", "glass_blue"][k % 4])
    # outlets
    for k in range(3):
        m.box((0.08, 0.08, 0.02), (0.3 + k * 0.2, 1.0, -D / 2 + 0.03), "hazard_yellow")
    # eyewash
    m.box((0.06, 0.06, 0.03), (0.85, 0.94, -0.2), "paint_green")


@_add(LB, "fume hood")
def _(m, rng):
    W, D = 1.6, 0.85
    cab(m, W, 0.85, D, "sci_white", 0.0, 0.015)
    for k in range(2):
        m.box((0.74, 0.7, 0.02), (-0.38 + k * 0.76, 0.42, D / 2 + 0.005), "hull_light", 0.006)
        handle(m, -0.38 + k * 0.76 + (0.3 if k == 0 else -0.3), 0.7, D / 2 + 0.03, False, 0.14)
    m.box((W + 0.04, 0.05, D + 0.04), (0, 0.875, 0), "sci_epoxy", 0.01)
    # hood shell
    m.box((0.08, 1.15, D - 0.1), (-W / 2 + 0.04, 1.47, -0.03), "sci_white", 0.01)
    m.box((0.08, 1.15, D - 0.1), (W / 2 - 0.04, 1.47, -0.03), "sci_white", 0.01)
    m.box((W, 1.15, 0.08), (0, 1.47, -D / 2 + 0.06), "hull_light", 0.01)
    m.box((W, 0.35, D - 0.02), (0, 2.22, -0.01), "sci_white", 0.02)
    m.box((W - 0.2, 0.12, 0.05), (0, 2.02, D / 2 - 0.05), "sci_teal", 0.01)
    m.screen((0.18, 0.1), (0.55, 2.03, D / 2 - 0.02), "diagnostic", bezel=0.008)
    led(m, (0.4, 2.03, D / 2 - 0.02), "em_green")
    m.cyl(0.16, 0.6, (0, 2.7, -0.15), "steel", seg=14)
    m.cyl(0.2, 0.05, (0, 2.42, -0.15), "steel", seg=14)
    # sash (glass, raised part-way)
    m.box((W - 0.16, 0.9, 0.02), (0, 1.55, D / 2 - 0.08), "glass_blue")
    m.box((W - 0.12, 0.04, 0.04), (0, 1.09, D / 2 - 0.08), "steel", 0.005)
    m.box((W - 0.12, 0.04, 0.03), (0, 2.02, D / 2 - 0.08), "steel", 0.005)
    m.box((0.04, 0.9, 0.03), (-W / 2 + 0.09, 1.55, D / 2 - 0.08), "steel")
    m.box((0.04, 0.9, 0.03), (W / 2 - 0.09, 1.55, D / 2 - 0.08), "steel")
    m.cyl(0.012, 0.3, (0, 1.09, D / 2 - 0.03), "chrome", axis="x", seg=6)
    # interior
    m.box((0.5, 0.12, 0.3), (-0.3, 0.98, -0.1), "steel", 0.01)
    for k in range(3):
        bottle(m, 0.1 + k * 0.16, 0.9, -0.1, 0.04, 0.12, ["sci_liquid_g", "sci_liquid_o", "sci_liquid_p"][k])
    m.box((1.2, 0.02, 0.05), (0, 2.03, -0.1), "em_white")


@_add(LB, "cleanroom glove box")
def _(m, rng):
    W, D = 1.5, 0.8
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.06, 0.72, 0.06), (sx * (W / 2 - 0.05), 0.36, sz * (D / 2 - 0.05)), "steel", 0.006)
    m.box((W - 0.05, 0.05, D - 0.05), (0, 0.72, 0), "steel", 0.008)
    m.box((W - 0.2, 0.2, 0.3), (0, 0.55, 0), "hull_dark", 0.01)
    # chamber
    m.box((W, 0.7, D), (0, 1.1, 0), "brushed_alu", 0.02)
    m.box((W - 0.16, 0.5, 0.02), (0, 1.15, D / 2 + 0.005), "glass_blue")
    m.box((W - 0.2, 0.44, D - 0.08), (0, 1.15, 0), "glass", 0.0)
    m.box((W - 0.05, 0.05, D - 0.05), (0, 1.5, 0), "black_metal", 0.008)
    m.box((W - 0.4, 0.04, D - 0.3), (0, 1.53, 0), "em_white")
    for sx in (-0.28, 0.28):
        m.cyl(0.1, 0.06, (sx, 1.12, D / 2 + 0.02), "chrome", axis="z", seg=14)
        m.cyl(0.07, 0.4, (sx, 1.12, D / 2 - 0.18), "rubber", axis="z", seg=10)
        m.sphere(0.06, (sx, 1.12, D / 2 - 0.4), "rubber", seg=8, ring=6)
    # antechamber
    m.cyl(0.18, 0.5, (W / 2 + 0.2, 1.1, 0), "steel", axis="x", seg=16)
    m.cyl(0.19, 0.03, (W / 2 + 0.47, 1.1, 0), "hull_dark", axis="x", seg=16)
    m.cyl(0.05, 0.05, (W / 2 + 0.5, 1.1, 0), "chrome", axis="x", seg=8)
    # control panel and gas bottle
    m.screen((0.2, 0.12), (-0.55, 1.5, D / 2 + 0.02), "diagnostic", bezel=0.01)
    leds(m, -0.7, 1.4, D / 2 + 0.01, 4, 0.05, ["em_green", "em_amber", "em_cyan"])
    m.cyl(0.07, 0.6, (-W / 2 - 0.15, 0.3, -0.2), "paint_green", seg=10)
    m.cyl(0.03, 0.1, (-W / 2 - 0.15, 0.65, -0.2), "brass", seg=6)
    m.link((-W / 2 - 0.15, 0.7, -0.2), (-W / 2, 1.2, -0.2), 0.012, "copper")


@_add(LB, "island reagent bench")
def _(m, rng):
    W, D = 2.4, 1.2
    m.box((W, 0.05, D), (0, 0.9, 0), "sci_epoxy", 0.01)
    cab(m, W - 0.06, 0.78, D - 0.06, "hull_light", 0.06)
    m.box((W - 0.1, 0.06, D - 0.1), (0, 0.03, 0), "black_metal")
    for s in (-1, 1):
        for k in range(4):
            x = -0.9 + k * 0.6
            m.box((0.54, 0.16, 0.02), (x, 0.7, s * (D / 2 - 0.02)), "paint_grey")
            m.box((0.54, 0.4, 0.02), (x, 0.36, s * (D / 2 - 0.02)), "sci_teal" if k % 2 else "paint_grey")
            handle(m, x, 0.73, s * (D / 2 + 0.005), True, 0.16)
    # central service spine & shelves
    for sx in (-1.1, 0, 1.1):
        m.box((0.05, 0.9, 0.05), (sx, 1.37, 0), "steel", 0.005)
    for yy in (1.3, 1.65):
        m.box((W - 0.1, 0.03, 0.3), (0, yy, 0), "sci_white", 0.005)
    for k in range(9):
        c = ["glass_amber", "glass_green", "glass", "glass_blue", "sci_liquid_p", "sci_liquid_o"][k % 6]
        bottle(m, -1.0 + k * 0.24, 1.315, 0.05 * ((-1) ** k), 0.036, 0.12 + 0.03 * (k % 3), c)
        bottle(m, -0.95 + k * 0.24, 1.665, 0.0, 0.03, 0.1 + 0.02 * (k % 2), ["glass_blue", "glass_amber"][k % 2])
    m.box((W - 0.1, 0.05, 0.05), (0, 1.86, 0), "hull_dark", 0.008)
    for k in range(5):
        m.box((0.1, 0.06, 0.03), (-0.9 + k * 0.45, 0.96, 0.4), "hazard_yellow")
    m.box((0.3, 0.02, 0.2), (0.7, 0.935, -0.3), "steel")
    m.cyl(0.07, 0.1, (0.7, 0.995, -0.3), "glass_blue", seg=10)


@_add(LB, "laminar flow bench")
def _(m, rng):
    W, D = 1.4, 0.8
    m.box((W, 0.05, D), (0, 0.85, 0), "steel", 0.008)
    cab(m, W - 0.04, 0.78, D - 0.04, "sci_white", 0.07)
    m.box((W - 0.1, 0.07, D - 0.1), (0, 0.035, 0), "black_metal")
    m.box((0.66, 0.4, 0.02), (-0.34, 0.45, D / 2 - 0.015), "hull_light", 0.006)
    m.box((0.66, 0.4, 0.02), (0.34, 0.45, D / 2 - 0.015), "hull_light", 0.006)
    handle(m, -0.1, 0.55, D / 2, False, 0.1)
    handle(m, 0.1, 0.55, D / 2, False, 0.1)
    # hood
    m.box((W, 0.9, 0.06), (0, 1.35, -D / 2 + 0.03), "sci_white", 0.008)
    for sx in (-1, 1):
        m.box((0.06, 0.9, D - 0.1), (sx * (W / 2 - 0.03), 1.35, -0.05), "sci_white", 0.008)
    m.box((W, 0.5, D), (0, 2.05, 0), "sci_white", 0.02)
    m.box((W - 0.2, 0.36, 0.02), (0, 2.05, D / 2 + 0.005), "black_metal")
    for k in range(8):
        m.box((W - 0.24, 0.012, 0.02), (0, 1.92 + k * 0.045, D / 2 + 0.015), "gunmetal")
    m.box((W - 0.1, 0.03, D - 0.1), (0, 1.79, 0), "em_blue")
    m.box((W - 0.1, 0.05, 0.06), (0, 1.77, D / 2 - 0.05), "black_metal")
    m.box((W - 0.1, 0.9, 0.02), (0, 1.35, D / 2 - 0.1), "glass_blue")
    m.cyl(0.02, W - 0.3, (0, 1.72, -0.1), "em_violet", axis="x", seg=6)
    m.screen((0.22, 0.12), (0.5, 0.9 + 0.15, D / 2 - 0.15), "systems", rot=(-0.6, 0, 0), bezel=0.008)
    led(m, (0.55, 2.3, D / 2 + 0.01), "em_green")


@_add(LB, "sample prep table")
def _(m, rng):
    W, D = 1.6, 0.8
    m.box((W, 0.04, D), (0, 0.86, 0), "steel", 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.03, 0.84, (sx * (W / 2 - 0.08), 0.42, sz * (D / 2 - 0.08)), "steel", seg=8)
        m.box((0.03, 0.03, D - 0.16), (sx * (W / 2 - 0.08), 0.25, 0), "steel")
    m.box((W - 0.16, 0.03, 0.03), (0, 0.25, -D / 2 + 0.08), "steel")
    m.box((W - 0.2, 0.02, 0.3), (0, 0.32, 0), "sci_white")
    # tray of sample tubes
    m.box((0.5, 0.03, 0.3), (-0.5, 0.895, 0.1), "plastic_grey", 0.005)
    for a in range(5):
        for b in range(3):
            m.cyl(0.02, 0.09, (-0.68 + a * 0.08, 0.955, 0.02 + b * 0.09), ["glass", "sci_liquid_g", "sci_liquid_o"][(a + b) % 3], seg=6)
    # balance with draft shield
    m.box((0.32, 0.06, 0.36), (0.15, 0.91, 0.1), "sci_white", 0.01)
    m.box((0.2, 0.22, 0.2), (0.15, 1.05, 0.05), "glass", 0.0)
    m.box((0.22, 0.02, 0.22), (0.15, 1.17, 0.05), "steel")
    m.screen((0.1, 0.05), (0.15, 0.925, 0.29), "bars", rot=(-0.3, 0, 0))
    # pipette carousel
    m.cyl(0.14, 0.02, (0.62, 0.89, -0.1), "plastic_grey", seg=14)
    m.cyl(0.02, 0.32, (0.62, 1.05, -0.1), "steel", seg=6)
    m.cyl(0.13, 0.02, (0.62, 1.12, -0.1), "plastic_grey", seg=14)
    for k in range(6):
        a = k * 1.047
        m.link((0.62 + math.cos(a) * 0.09, 1.2, -0.1 + math.sin(a) * 0.09), (0.62 + math.cos(a) * 0.09, 0.98, -0.1 + math.sin(a) * 0.09), 0.012, ["paint_blue", "paint_red", "paint_green"][k % 3], seg=6)
    # microscope-like monitor arm
    m.link((-0.65, 0.88, -0.32), (-0.65, 1.4, -0.32), 0.015, "steel", seg=6)
    m.screen((0.34, 0.22), (-0.65, 1.42, -0.28), "diagnostic", rot=(-0.1, 0, 0), bezel=0.015)
    m.box((0.1, 0.02, 0.1), (-0.65, 0.89, -0.32), "steel")


@_add(LB, "lab stool")
def _(m, rng):
    m.cyl(0.19, 0.07, (0, 0.7, 0), "plastic_black", seg=18, bevel=0.01)
    m.cyl(0.17, 0.03, (0, 0.65, 0), "steel", seg=14)
    m.cyl(0.03, 0.55, (0, 0.4, 0), "chrome", seg=8)
    m.cyl(0.05, 0.1, (0, 0.62, 0), "black_metal", seg=8)
    m.torus(0.22, 0.014, (0, 0.28, 0), "chrome", seg=16, tseg=4)
    for k in range(5):
        a = 2 * math.pi * k / 5
        m.link((0, 0.14, 0), (math.cos(a) * 0.26, 0.05, math.sin(a) * 0.26), 0.02, "steel", seg=5)
        m.link((0, 0.28, 0), (math.cos(a) * 0.22, 0.28, math.sin(a) * 0.22), 0.01, "chrome", seg=4)
        m.sphere(0.035, (math.cos(a) * 0.26, 0.035, math.sin(a) * 0.26), "rubber", seg=6, ring=4)
    m.cyl(0.05, 0.14, (0, 0.14, 0), "steel", seg=8)


@_add(LB, "lab chair")
def _(m, rng):
    m.box((0.46, 0.07, 0.44), (0, 0.5, 0.02), "fabric_teal", 0.03)
    m.box((0.42, 0.34, 0.06), (0, 0.78, -0.2), "fabric_teal", 0.03, rot=(-0.12, 0, 0))
    m.box((0.06, 0.2, 0.05), (0, 0.6, -0.2), "steel")
    m.cyl(0.04, 0.3, (0, 0.3, 0), "chrome", seg=8)
    m.cyl(0.055, 0.12, (0, 0.45, 0), "black_metal", seg=8)
    for sx in (-1, 1):
        m.box((0.04, 0.03, 0.3), (sx * 0.26, 0.68, 0.0), "plastic_black", 0.01)
        m.box((0.03, 0.18, 0.03), (sx * 0.26, 0.59, 0.1), "steel")
    star_base(m, 0.1, 0.3)
    m.cyl(0.05, 0.12, (0, 0.12, 0), "steel", seg=8)


_reg("labbench", {k: LB[k] for k in list(LB)[:6]}, mount="floor", tags=TAG + ["lab"], solid=True)
_reg("labbench", {k: LB[k] for k in list(LB)[6:]}, mount="floor", tags=TAG + ["lab", "seat"], solid=False)

# ==========================================================================
# MICROSCOPES
# ==========================================================================
MT = {}
MF = {}


@_add(MT, "optical microscope")
def _(m, rng):
    m.box((0.22, 0.04, 0.26), (0, 0.02, 0.0), "black_metal", 0.012)
    m.box((0.05, 0.36, 0.06), (0, 0.22, -0.09), "black_metal", 0.012)
    m.box((0.06, 0.05, 0.16), (0, 0.4, -0.02), "black_metal", 0.012)
    m.box((0.2, 0.014, 0.16), (0, 0.16, 0.03), "steel")
    m.box((0.08, 0.008, 0.06), (0, 0.172, 0.03), "glass")
    m.link((0, 0.42, 0.04), (0, 0.5, -0.02), 0.035, "black_metal", seg=8)
    m.link((0, 0.45, 0.04), (0, 0.56, -0.02), 0.03, "gunmetal", seg=8)
    m.cyl(0.03, 0.1, (0, 0.58, -0.04), "chrome", seg=8, rot=(0.4, 0, 0))
    m.cyl(0.055, 0.03, (0, 0.33, 0.04), "chrome", seg=12)
    for a in (-0.7, 0, 0.7):
        m.cyl(0.014, 0.06, (math.sin(a) * 0.04, 0.29, 0.04 + math.cos(a) * 0.04 - 0.03), "steel", seg=6)
    m.cyl(0.025, 0.06, (0, 0.11, 0.03), "hull_light", seg=8)
    for sx in (-1, 1):
        m.cyl(0.03, 0.03, (sx * 0.05, 0.22, -0.09), "rubber", axis="x", seg=10)
    m.cyl(0.035, 0.03, (0, 0.06, 0.12), "em_white", seg=8)
    led(m, (0.06, 0.03, 0.135), "em_green")


@_add(MT, "stereo microscope")
def _(m, rng):
    m.cyl(0.13, 0.03, (0, 0.015, 0), "black_metal", seg=16, bevel=0.008)
    m.cyl(0.11, 0.008, (0, 0.034, 0.02), "sci_white", seg=16)
    m.cyl(0.02, 0.5, (0, 0.28, -0.09), "steel", seg=8)
    m.box((0.05, 0.08, 0.05), (0, 0.4, -0.09), "black_metal", 0.01)
    m.box((0.04, 0.04, 0.24), (0, 0.42, 0.03), "black_metal", 0.01)
    m.box((0.14, 0.11, 0.1), (0, 0.42, 0.16), "gunmetal", 0.02)
    for sx in (-1, 1):
        m.cyl(0.022, 0.16, (sx * 0.035, 0.53, 0.09), "black_metal", seg=8, rot=(-0.6, 0, 0))
        m.cyl(0.026, 0.03, (sx * 0.035, 0.6, 0.02), "rubber", seg=8, rot=(-0.6, 0, 0))
    m.cyl(0.05, 0.08, (0, 0.34, 0.16), "steel", seg=10)
    m.torus(0.055, 0.012, (0, 0.29, 0.16), "em_white", seg=14, tseg=5)
    m.cyl(0.02, 0.03, (0.05, 0.42, -0.09), "rubber", axis="x", seg=8)
    m.sphere(0.02, (0.02, 0.05, 0.04), "food_green", seg=8, ring=6)


@_add(MT, "scanning probe microscope")
def _(m, rng):
    m.box((0.5, 0.05, 0.4), (0, 0.025, 0), "black_metal", 0.01)
    m.box((0.36, 0.03, 0.3), (0, 0.065, 0), "steel", 0.006)
    m.box((0.32, 0.26, 0.26), (0, 0.21, 0.0), "glass_dark", 0.01)
    for sx in (-0.17, 0.17):
        for sz in (-0.14, 0.14):
            m.box((0.02, 0.28, 0.02), (sx, 0.21, sz), "steel")
    m.box((0.36, 0.03, 0.3), (0, 0.365, 0), "hull_dark", 0.008)
    m.cyl(0.04, 0.08, (0, 0.42, 0), "gunmetal", seg=10)
    m.cyl(0.02, 0.12, (0, 0.2, 0), "chrome", seg=8)
    m.box((0.1, 0.02, 0.02), (0, 0.15, 0.03), "brass")
    m.box((0.12, 0.08, 0.06), (0.32, 0.055, 0.06), "hull_dark", 0.008)
    leds(m, 0.29, 0.06, 0.092, 3, 0.03, ["em_green", "em_amber"])
    m.screen((0.2, 0.13), (-0.02, 0.09, 0.26), "waveform", rot=(-0.9, 0, 0), bezel=0.012)
    m.box((0.22, 0.03, 0.14), (-0.02, 0.03, 0.26), "hull_dark", 0.006)


@_add(MF, "electron microscope")
def _(m, rng):
    m.box((0.7, 0.75, 0.7), (0, 0.375, 0), "sci_white", 0.03)
    m.box((0.5, 0.02, 0.02), (0, 0.6, 0.355), "sci_teal")
    m.box((0.6, 0.05, 0.6), (0, 0.775, 0), "brushed_alu", 0.01)
    m.cyl(0.16, 0.5, (0, 1.05, 0), "sci_white", seg=16, bevel=0.008)
    m.cyl(0.11, 0.35, (0, 1.48, 0), "brushed_alu", seg=16)
    for k in range(3):
        m.torus(0.13, 0.014, (0, 1.36 + k * 0.1, 0), "copper", seg=16, tseg=5)
    m.cyl(0.07, 0.2, (0, 1.78, 0), "hull_dark", seg=12)
    m.cyl(0.05, 0.1, (0, 1.93, 0), "black_metal", seg=10)
    m.box((0.16, 0.3, 0.22), (0.22, 0.95, 0.15), "hull_light", 0.01)
    m.cyl(0.05, 0.12, (0.31, 0.95, 0.32), "black_metal", axis="z", seg=10)
    # display desk
    m.box((0.5, 0.5, 0.5), (0.6, 0.25, 0.1), "hull_mid", 0.015)
    m.box((0.56, 0.04, 0.56), (0.6, 0.52, 0.1), "sci_epoxy", 0.008)
    m.screen((0.34, 0.24), (0.6, 0.9, 0.05), "diagnostic", rot=(-0.15, 0, 0), bezel=0.015)
    m.box((0.06, 0.34, 0.06), (0.6, 0.7, 0.0), "black_metal")
    m.screen((0.28, 0.2), (0.6, 0.78, 0.3), "waveform", rot=(-0.9, 0, 0), bezel=0.012)
    # pump
    m.cyl(0.14, 0.4, (-0.55, 0.2, 0), "paint_teal", seg=12)
    m.cyl(0.09, 0.15, (-0.55, 0.47, 0), "steel", seg=10)
    m.link((-0.55, 0.5, 0), (-0.1, 0.7, 0), 0.03, "steel", seg=8)
    led(m, (0.28, 0.5, 0.36), "em_green")
    leds(m, -0.2, 0.68, 0.356, 4, 0.05, ["em_cyan", "em_amber"])


@_add(MF, "confocal cabinet")
def _(m, rng):
    W, D = 1.0, 0.9
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.05, 0.6, (sx * 0.42, 0.3, sz * 0.36), "gunmetal", seg=10)
            m.cyl(0.07, 0.03, (sx * 0.42, 0.015, sz * 0.36), "rubber", seg=10)
    m.box((W, 0.1, D), (0, 0.65, 0), "steel", 0.008)
    for k in range(6):
        m.cyl(0.011, 0.09, (-0.4 + k * 0.16, 0.7, -0.35), "black_metal", seg=6)
    m.box((W - 0.1, 0.12, D - 0.1), (0, 0.5, 0), "black_metal", 0.01)
    # laser enclosure and scope box
    m.box((0.5, 0.75, 0.7), (-0.2, 1.1, 0), "sci_white", 0.02)
    m.box((0.2, 0.5, 0.5), (0.3, 1.05, 0.0), "hull_dark", 0.02)
    m.box((0.36, 0.05, 0.02), (-0.2, 1.3, 0.36), "em_violet")
    m.cyl(0.07, 0.4, (0.3, 1.5, 0.0), "gunmetal", seg=12)
    m.cyl(0.1, 0.12, (0.3, 1.72, 0.0), "steel", seg=12)
    m.link((0.05, 1.3, 0), (0.2, 1.3, 0), 0.03, "black_metal", seg=8)
    m.box((0.5, 0.02, 0.02), (-0.2, 1.4, 0.36), "hazard_yellow")
    m.box((0.4, 0.4, 0.02), (-0.2, 1.05, 0.36), "hull_light")
    m.cyl(0.04, 0.03, (0.3, 0.9, 0.3), "black_metal", axis="z", seg=8)
    # pc arm
    m.link((0.4, 0.7, -0.3), (0.4, 1.3, -0.3), 0.02, "steel", seg=6)
    m.screen((0.34, 0.24), (0.36, 1.4, -0.24), "medical", rot=(0, -0.3, 0), bezel=0.015)
    led(m, (0.45, 0.72, 0.45), "em_amber")


_reg("microscope", MT, mount="table", tags=TAG + ["lab"], solid=False)
_reg("microscope", MF, mount="floor", tags=TAG + ["lab"], solid=True)

# ==========================================================================
# ANALYZERS
# ==========================================================================
AT = {}
AF = {}


@_add(AF, "mass spectrometer")
def _(m, rng):
    m.box((1.4, 1.1, 0.7), (0, 0.55, 0), "sci_white", 0.03)
    m.box((1.36, 0.12, 0.66), (0, 1.16, 0), "hull_dark", 0.01)
    m.box((0.7, 0.35, 0.02), (-0.28, 0.75, 0.355), "black_metal")
    m.screen((0.6, 0.28), (-0.28, 0.75, 0.37), "graph", bezel=0.015)
    m.box((0.5, 0.5, 0.02), (0.45, 0.5, 0.355), "hull_light", 0.005)
    hazard(m, 0.45, 0.2, 0.362, 0.5, 0.1)
    leds(m, 0.25, 0.7, 0.36, 6, 0.06, ["em_green", "em_cyan", "em_amber"])
    # analyser tube along top
    m.cyl(0.11, 1.1, (-0.1, 1.38, 0), "brushed_alu", axis="x", seg=16)
    m.torus(0.13, 0.02, (0.45, 1.38, 0), "steel", axis="x", seg=14, tseg=5)
    m.torus(0.13, 0.02, (-0.65, 1.38, 0), "steel", axis="x", seg=14, tseg=5)
    m.cyl(0.14, 0.25, (0.65, 1.38, 0), "sci_teal", axis="x", seg=14)
    m.cyl(0.08, 0.3, (-0.75, 1.38, 0), "gunmetal", axis="x", seg=12)
    m.cyl(0.09, 0.3, (-0.3, 1.6, 0), "black_metal", seg=12)
    m.cyl(0.05, 0.14, (-0.3, 1.77, 0), "copper", seg=10)
    m.link((0.3, 1.5, 0), (0.3, 1.75, 0.0), 0.02, "copper", seg=6)
    # pumps rear
    for sx in (-0.45, 0.2):
        m.cyl(0.13, 0.5, (sx, 0.3, -0.5), "paint_teal", seg=12)
        m.cyl(0.05, 0.3, (sx, 0.65, -0.5), "steel", seg=8)
    m.box((1.2, 0.02, 0.02), (0, 0.01, 0.36), "black_metal")


@_add(AT, "gas chromatograph")
def _(m, rng):
    m.box((0.62, 0.42, 0.5), (0, 0.21, 0), "sci_white", 0.02)
    m.box((0.2, 0.32, 0.02), (-0.2, 0.22, 0.255), "black_metal")
    m.box((0.28, 0.3, 0.02), (0.13, 0.22, 0.255), "glass_dark")
    m.screen((0.14, 0.09), (-0.2, 0.3, 0.27), "graph", bezel=0.008)
    leds(m, -0.26, 0.16, 0.266, 4, 0.04, ["em_green", "em_amber"], 0.01)
    m.box((0.6, 0.02, 0.48), (0, 0.43, 0), "hull_dark", 0.005)
    # autosampler
    m.box((0.36, 0.05, 0.16), (-0.1, 0.475, 0.14), "steel", 0.006)
    for k in range(9):
        m.cyl(0.014, 0.05, (-0.25 + k * 0.038, 0.525, 0.14), "glass", seg=6)
    m.box((0.05, 0.18, 0.05), (0.14, 0.55, 0.02), "steel", 0.006)
    m.box((0.16, 0.03, 0.03), (0.06, 0.63, 0.02), "chrome")
    # solvent bottles + lines
    for k in range(4):
        x = -0.22 + k * 0.14
        bottle(m, x, 0.44, -0.16, 0.05, 0.22, ["sci_liquid_g", "sci_liquid_o", "glass_amber", "sci_liquid_b"][k])
        m.tube([(x, 0.7, -0.16), (x, 0.74, -0.12), (0.26, 0.6, -0.05), (0.26, 0.4, 0.1)], 0.005, "plastic_white", seg=5)
    m.cyl(0.03, 0.14, (0.28, 0.5, 0.15), "chrome", seg=8)


@_add(AT, "spectrometer")
def _(m, rng):
    m.box((0.72, 0.1, 0.32), (0, 0.05, 0), "black_metal", 0.01)
    m.box((0.5, 0.14, 0.24), (-0.08, 0.17, 0), "sci_white", 0.02)
    m.box((0.18, 0.1, 0.2), (0.28, 0.15, 0), "hull_dark", 0.01)
    m.box((0.12, 0.05, 0.12), (0.28, 0.225, 0), "glass_blue")
    m.cyl(0.03, 0.14, (0.42, 0.12, 0), "brushed_alu", axis="x", seg=10)
    m.tube([(0.5, 0.12, 0), (0.6, 0.1, 0.1), (0.65, 0.05, 0.05)], 0.006, "em_orange", seg=5)
    m.cyl(0.055, 0.1, (-0.25, 0.29, 0), "gunmetal", seg=12)
    m.cyl(0.03, 0.14, (-0.25, 0.4, 0), "chrome", seg=8)
    m.box((0.05, 0.03, 0.05), (-0.08, 0.255, 0), "black_metal")
    m.screen((0.24, 0.13), (-0.05, 0.13, 0.175), "waveform", rot=(-0.3, 0, 0), bezel=0.01)
    leds(m, -0.3, 0.06, 0.165, 3, 0.03, ["em_green", "em_cyan"], 0.01)
    m.box((0.05, 0.16, 0.06), (0.12, 0.28, 0), "hull_light")


@_add(AT, "centrifuge")
def _(m, rng):
    m.cyl(0.26, 0.28, (0, 0.14, 0), "sci_white", seg=20, bevel=0.01)
    m.cyl(0.22, 0.02, (0, 0.29, 0), "hull_dark", seg=20)
    m.cyl(0.23, 0.1, (0, 0.34, 0), "glass_blue", seg=20, r2=0.19, cap=True)
    m.cyl(0.24, 0.03, (0, 0.41, 0), "sci_white", seg=20)
    m.box((0.22, 0.12, 0.05), (0, 0.13, 0.245), "black_metal", 0.008)
    m.screen((0.14, 0.07), (0, 0.13, 0.275), "bars", bezel=0.006)
    led(m, (0.1, 0.19, 0.27), "em_green")
    m.cyl(0.02, 0.05, (0.12, 0.28, 0.2), "paint_red", seg=8)
    for k in range(6):
        a = k * 1.047
        m.box((0.03, 0.05, 0.04), (math.cos(a) * 0.1, 0.32, math.sin(a) * 0.1), "plastic_grey", rot=(0, -a, 0))
    m.cyl(0.02, 0.1, (0, 0.34, 0), "steel", seg=6)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.03, 0.015, (sx * 0.16, 0.0075, sz * 0.16), "rubber", seg=8)


@_add(AF, "co2 incubator")
def _(m, rng):
    m.box((0.8, 1.75, 0.8), (0, 0.9, 0), "sci_white", 0.03)
    m.box((0.6, 0.6, 0.02), (0, 1.15, 0.405), "glass_blue")
    m.box((0.64, 0.64, 0.02), (0, 1.15, 0.395), "steel")
    m.box((0.6, 0.6, 0.02), (0, 0.5, 0.405), "hull_light", 0.01)
    for k in range(4):
        m.box((0.5, 0.01, 0.3), (0, 0.95 + k * 0.15, 0.24), "steel")
    for k in range(3):
        m.cyl(0.05, 0.05, (-0.1 + k * 0.1, 1.06, 0.3), "sci_liquid_b", seg=8)
    handle(m, 0.32, 1.15, 0.425, False, 0.4)
    m.box((0.34, 0.14, 0.03), (0, 1.62, 0.405), "black_metal", 0.008)
    m.screen((0.28, 0.1), (0, 1.62, 0.425), "systems", bezel=0.006)
    leds(m, -0.3, 1.62, 0.42, 2, 0.02, ["em_green", "em_amber"], 0.01)
    handle(m, 0.32, 0.5, 0.425, False, 0.3)
    m.cyl(0.03, 0.12, (-0.32, 1.86, -0.2), "brass", seg=8)
    m.cyl(0.05, 0.02, (0.38, 0.02, 0.38), "rubber", seg=8)
    hazard(m, 0, 0.12, 0.41, 0.6, 0.08)
    for sx in (-1, 1):
        m.box((0.08, 0.08, 0.08), (sx * 0.34, 0.04, 0.32), "black_metal")


@_add(AT, "thermal cycler")
def _(m, rng):
    m.box((0.32, 0.14, 0.4), (0, 0.07, 0), "sci_white", 0.02)
    m.box((0.3, 0.05, 0.3), (0, 0.16, -0.03), "hull_dark", 0.012)
    m.box((0.24, 0.02, 0.2), (0, 0.19, -0.03), "steel", 0.004)
    for a in range(6):
        for b in range(4):
            m.cyl(0.009, 0.005, (-0.1 + a * 0.04, 0.205, -0.09 + b * 0.04), "black_metal", seg=6)
    m.box((0.32, 0.03, 0.36), (0, 0.1, 0.0), "sci_white", 0.01, )
    m.screen((0.16, 0.08), (0, 0.08, 0.207), "graph", bezel=0.008)
    leds(m, -0.12, 0.13, 0.205, 3, 0.03, ["em_green", "em_amber", "em_red"], 0.01)
    m.box((0.06, 0.03, 0.04), (0.11, 0.17, 0.19), "em_orange")
    m.box((0.28, 0.02, 0.02), (0, 0.24, -0.16), "steel")
    m.box((0.28, 0.008, 0.012), (0, 0.045, 0.207), "sci_teal")


@_add(AF, "3d fabricator")
def _(m, rng):
    W, D, H = 1.0, 0.9, 1.5
    m.box((W, 0.35, D), (0, 0.175, 0), "hull_dark", 0.02)
    m.box((0.6, 0.15, 0.02), (-0.1, 0.18, D / 2 + 0.005), "black_metal")
    m.screen((0.24, 0.14), (0.3, 0.18, D / 2 + 0.01), "systems", bezel=0.01)
    leds(m, -0.35, 0.18, D / 2 + 0.02, 5, 0.06, ["em_cyan"], 0.012)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.05, H - 0.35, 0.05), (sx * (W / 2 - 0.03), 0.35 + (H - 0.35) / 2, sz * (D / 2 - 0.03)), "gunmetal", 0.005)
    m.box((W, 0.05, D), (0, H + 0.025, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.02, H - 0.4, D - 0.06), (sx * (W / 2 - 0.02), 0.35 + (H - 0.35) / 2, 0), "glass_blue")
    m.box((W - 0.06, H - 0.4, 0.02), (0, 0.35 + (H - 0.35) / 2, -D / 2 + 0.03), "glass_blue")
    m.box((0.06, 0.06, D - 0.1), (-0.4, 1.3, 0), "chrome")
    m.box((0.06, 0.06, D - 0.1), (0.4, 1.3, 0), "chrome")
    m.box((W - 0.2, 0.05, 0.06), (0, 1.3, 0.15), "brushed_alu", 0.008)
    m.box((0.14, 0.14, 0.12), (0.1, 1.2, 0.15), "paint_orange", 0.015)
    m.cyl(0.02, 0.06, (0.1, 1.09, 0.15), "brass", seg=6, r2=0.005)
    m.box((0.8, 0.03, 0.7), (0, 0.5, 0), "black_metal", 0.005)
    m.box((0.7, 0.01, 0.6), (0, 0.52, 0), "glass_dark")
    # printed lattice object
    for k in range(7):
        m.box((0.3 - k * 0.02, 0.04, 0.3 - k * 0.02), (0.1, 0.56 + k * 0.05, 0.15), "paint_teal" if k % 2 else "plastic_white", 0.005)
    m.cyl(0.14, 0.05, (-0.25, H + 0.075, -0.1), "hull_light", axis="z", seg=14)
    m.torus(0.13, 0.05, (-0.25, H + 0.08, 0.0), "paint_orange", axis="z", seg=14, tseg=6)
    m.tube([(-0.25, H + 0.03, 0.05), (-0.2, 1.4, 0.2), (0.1, 1.28, 0.15)], 0.008, "plastic_white", seg=5)


@_add(AF, "materials tester")
def _(m, rng):
    W, D = 0.9, 0.6
    m.box((W, 0.7, D), (0, 0.35, 0), "paint_blue", 0.03)
    m.box((W - 0.05, 0.03, D - 0.05), (0, 0.715, 0), "steel", 0.006)
    for sx in (-1, 1):
        m.cyl(0.04, 1.3, (sx * 0.32, 1.38, -0.1), "chrome", seg=10)
        m.cyl(0.06, 0.04, (sx * 0.32, 0.745, -0.1), "steel", seg=10)
    m.box((W - 0.05, 0.14, 0.24), (0, 2.08, -0.1), "paint_blue", 0.02)
    m.box((W - 0.15, 0.12, 0.3), (0, 1.5, -0.1), "hull_dark", 0.015)
    m.cyl(0.03, 0.55, (0, 1.75, -0.1), "chrome", seg=8)
    m.cyl(0.05, 0.1, (0, 1.4, -0.1), "steel", seg=8)
    m.cyl(0.05, 0.1, (0, 0.86, -0.1), "steel", seg=8)
    m.cyl(0.03, 0.2, (0, 0.78, -0.1), "chrome", seg=8)
    m.cyl(0.012, 0.42, (0, 1.12, -0.1), "brushed_alu", seg=6)
    m.cyl(0.05, 0.03, (0, 1.12, -0.1), "hazard_yellow", seg=8, r2=0.02)
    m.box((0.22, 0.08, 0.02), (0, 1.12, D / 2 - 0.15), "hazard_yellow", rot=(0, 0, 0))
    # safety shield
    m.box((0.02, 1.0, 0.36), (-0.4, 1.15, 0.12), "glass_blue")
    m.box((0.02, 1.0, 0.36), (0.4, 1.15, 0.12), "glass_blue")
    m.box((0.8, 1.0, 0.02), (0, 1.15, 0.3), "glass_blue")
    m.box((0.8, 0.04, 0.4), (0, 0.68, 0.12), "steel")
    # control pod
    m.box((0.36, 0.28, 0.14), (0.0, 0.4, D / 2 + 0.03), "hull_dark", 0.015, rot=(-0.15, 0, 0))
    m.screen((0.28, 0.18), (0, 0.42, D / 2 + 0.105), "graph", rot=(-0.15, 0, 0), bezel=0.01)
    m.cyl(0.03, 0.04, (0.3, 0.3, D / 2 + 0.03), "paint_red", axis="z", seg=8)
    m.cyl(0.05, 0.3, (0.55, 0.15, 0.1), "hull_light", seg=10)
    led(m, (-0.3, 0.6, D / 2 + 0.005), "em_green")


_reg("analyzer", AT, mount="table", tags=TAG + ["lab"], solid=False)
_reg("analyzer", AF, mount="floor", tags=TAG + ["lab"], solid=True)

# ==========================================================================
# SPECIMENS
# ==========================================================================
ST = {}
SF = {}


@_add(ST, "specimen jar set")
def _(m, rng):
    m.box((0.6, 0.03, 0.26), (0, 0.015, 0), "wood_dark", 0.008)
    specs = [(-0.2, 0.07, 0.24, "sci_liquid_g"), (-0.04, 0.09, 0.3, "sci_liquid_o"), (0.14, 0.06, 0.2, "sci_liquid_p"), (0.24, 0.045, 0.14, "sci_liquid_b")]
    for x, r, h, liq in specs:
        m.cyl(r, h, (x, 0.03 + h / 2, 0.0), "glass", seg=14)
        m.cyl(r * 0.9, h * 0.8, (x, 0.03 + h * 0.42, 0.0), liq, seg=12)
        m.cyl(r * 1.05, 0.03, (x, 0.03 + h + 0.015, 0.0), "brass", seg=14)
        m.cyl(r * 0.8, 0.02, (x, 0.04, 0), "black_metal", seg=10)
        m.sphere(r * 0.45, (x, 0.03 + h * 0.4, 0.0), ["leaf", "food_brown", "paint_white", "paint_orange"][int(x * 10) % 4], seg=8, ring=6, scale=(1, 1.3, 1))
        m.box((r * 1.2, 0.05, 0.004), (x, 0.03 + h * 0.3, r + 0.002), "paint_white")


@_add(ST, "desktop terrarium")
def _(m, rng):
    m.box((0.6, 0.04, 0.4), (0, 0.02, 0), "black_metal", 0.008)
    m.box((0.56, 0.06, 0.36), (0, 0.07, 0), "soil", 0.01)
    for sx, sz in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        m.box((0.014, 0.4, 0.014), (sx * 0.28, 0.27, sz * 0.18), "steel")
    m.box((0.56, 0.36, 0.005), (0, 0.27, 0.18), "glass")
    m.box((0.56, 0.36, 0.005), (0, 0.27, -0.18), "glass")
    m.box((0.005, 0.36, 0.36), (0.28, 0.27, 0), "glass")
    m.box((0.005, 0.36, 0.36), (-0.28, 0.27, 0), "glass")
    m.box((0.6, 0.03, 0.4), (0, 0.475, 0), "black_metal", 0.008)
    m.box((0.44, 0.015, 0.06), (0, 0.455, 0), "em_warm")
    for k in range(7):
        a = k * 2.4
        x, z = math.cos(a) * 0.2, math.sin(a) * 0.1
        m.cyl(0.006, 0.12 + 0.03 * (k % 3), (x, 0.16, z), "leaf", seg=5)
        m.sphere(0.05, (x, 0.24 + 0.03 * (k % 3), z), "leaf", seg=8, ring=5, scale=(1, 0.5, 1))
    m.sphere(0.06, (-0.15, 0.12, 0.08), "concrete", seg=7, ring=5, scale=(1.3, 0.8, 1))
    m.sphere(0.04, (0.05, 0.11, 0.1), "concrete", seg=7, ring=5)
    m.cyl(0.008, 0.2, (0.2, 0.18, 0.05), "wood_dark", seg=5, rot=(0, 0, 0.4))


@_add(SF, "aquarium tank")
def _(m, rng):
    W, D = 1.3, 0.55
    cab(m, W, 0.7, D, "hull_dark", 0.0, 0.02)
    m.box((W - 0.1, 0.5, 0.02), (0, 0.38, D / 2 + 0.003), "hull_mid", 0.005)
    handle(m, 0, 0.6, D / 2 + 0.02, True, 0.3)
    m.box((W + 0.06, 0.05, D + 0.06), (0, 0.725, 0), "black_metal", 0.01)
    m.box((W, 0.6, D), (0, 1.05, 0), "glass", 0)
    m.box((W - 0.06, 0.52, D - 0.06), (0, 1.02, 0), "sci_water")
    m.box((W - 0.06, 0.06, D - 0.06), (0, 0.78, 0), "wood_light", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.03, 0.62, 0.03), (sx * (W / 2 - 0.01), 1.05, sz * (D / 2 - 0.01)), "black_metal")
    m.box((W + 0.04, 0.05, D + 0.04), (0, 1.375, 0), "black_metal", 0.01)
    m.box((W - 0.2, 0.03, 0.08), (0, 1.35, D / 2 - 0.1), "em_white")
    m.box((0.14, 0.05, 0.12), (0.5, 1.42, -0.05), "plastic_black", 0.01)
    for k in range(9):
        x = -0.5 + k * 0.12
        h = 0.2 + 0.1 * ((k * 7) % 4)
        m.cyl(0.012, h, (x, 0.8 + h / 2, -0.15 + 0.1 * (k % 3)), "leaf", seg=5, r2=0.004)
        m.sphere(0.04, (x + 0.02, 0.82 + h * 0.6, -0.15 + 0.1 * (k % 3)), "food_green", seg=6, ring=4, scale=(1, 2.2, 0.4))
    m.sphere(0.13, (-0.3, 0.86, 0.1), "concrete", seg=8, ring=6, scale=(1.4, 0.9, 1))
    m.sphere(0.09, (0.25, 0.84, 0.05), "concrete", seg=8, ring=6, scale=(1.2, 0.8, 1))
    m.cyl(0.02, 0.5, (0.55, 1.1, -0.2), "plastic_black", seg=6)
    m.cyl(0.02, 0.5, (0.35, 1.1, -0.2), "plastic_black", seg=6)
    m.box((0.28, 0.004, 0.006), (0.45, 0.73, D / 2 + 0.005), "em_cyan")


@_add(ST, "rock sample case")
def _(m, rng):
    m.box((0.5, 0.08, 0.36), (0, 0.04, 0), "plastic_black", 0.015)
    m.box((0.46, 0.05, 0.32), (0, 0.08, 0), "foam", 0.01)
    cols = ["concrete", "food_brown", "paint_grey", "copper", "hull_dark", "paint_red"]
    for a in range(3):
        for b in range(2):
            m.box((0.12, 0.04, 0.12), (-0.14 + a * 0.14, 0.09, -0.08 + b * 0.16), "black_metal")
            m.sphere(0.05, (-0.14 + a * 0.14, 0.13, -0.08 + b * 0.16), cols[(a * 2 + b) % 6], seg=7, ring=5, scale=(1, 0.8, 1.1))
    m.box((0.5, 0.05, 0.05), (0, 0.06, 0.185), "hull_dark")
    m.box((0.5, 0.36, 0.04), (0, 0.27, -0.2), "plastic_black", 0.012, rot=(-0.12, 0, 0))
    m.box((0.44, 0.3, 0.02), (0, 0.27, -0.17), "foam", rot=(-0.12, 0, 0))
    for k in range(6):
        m.box((0.05, 0.03, 0.006), (-0.15 + (k % 3) * 0.15, 0.32 - (k // 3) * 0.12, -0.16), "paint_white", rot=(-0.12, 0, 0))
    for sx in (-0.18, 0.18):
        m.box((0.05, 0.04, 0.02), (sx, 0.05, 0.185), "chrome")


@_add(ST, "vial rack")
def _(m, rng):
    m.box((0.36, 0.02, 0.2), (0, 0.06, 0), "plastic_grey", 0.005)
    m.box((0.36, 0.02, 0.2), (0, 0.15, 0), "plastic_grey", 0.005)
    for sx in (-1, 1):
        m.box((0.02, 0.15, 0.2), (sx * 0.17, 0.075, 0), "plastic_grey", 0.005)
    m.box((0.36, 0.005, 0.22), (0, 0.01, 0), "rubber")
    for a in range(8):
        for b in range(4):
            liq = ["sci_liquid_g", "glass", "sci_liquid_o", "sci_liquid_b", "sci_liquid_p"][(a * 3 + b * 2) % 5]
            m.cyl(0.0125, 0.11, (-0.14 + a * 0.04, 0.115, -0.06 + b * 0.04), liq, seg=5)
            m.cyl(0.013, 0.02, (-0.14 + a * 0.04, 0.18, -0.06 + b * 0.04), ["paint_red", "paint_blue", "paint_white"][(a + b) % 3], seg=5)


@_add(SF, "artifact plinth")
def _(m, rng):
    m.box((0.7, 0.08, 0.7), (0, 0.04, 0), "hull_dark", 0.012)
    m.box((0.5, 0.72, 0.5), (0, 0.44, 0), "hull_mid", 0.015, )
    m.box((0.54, 0.04, 0.54), (0, 0.82, 0), "gold_trim", 0.01)
    m.box((0.5, 0.04, 0.02), (0, 0.55, 0.255), "em_amber")
    m.screen((0.24, 0.1), (0, 0.4, 0.26), "text", bezel=0.008)
    m.cyl(0.26, 0.05, (0, 0.865, 0), "black_metal", seg=18)
    m.torus(0.24, 0.01, (0, 0.895, 0), "em_violet", seg=24, tseg=5)
    m.sphere(0.24, (0, 1.1, 0), "glass", seg=18, ring=10, scale=(1, 1.05, 1))
    m.cyl(0.03, 0.02, (0, 0.89, 0), "steel", seg=8)
    for k, (dx, dz, h, tilt) in enumerate(((0, 0, 0.3, 0), (0.06, 0.03, 0.2, 0.4), (-0.06, 0.02, 0.22, -0.45), (0.02, -0.06, 0.18, 0.25), (-0.03, -0.05, 0.16, -0.2))):
        m.link((dx * 0.3, 0.9, dz * 0.3), (dx * 0.3 + math.sin(tilt) * h, 0.9 + math.cos(tilt) * h, dz * 0.3 + (0.3 * tilt * h)), 0.026 - 0.003 * k, "sci_crystal" if k % 2 == 0 else "sci_crystal2", seg=5)
    m.sphere(0.06, (0, 0.93, 0), "sci_crystal", seg=6, ring=4)
    m.box((0.02, 0.02, 0.02), (0.29, 0.86, 0.29), "em_amber")


@_add(SF, "containment cylinder")
def _(m, rng):
    m.cyl(0.55, 0.12, (0, 0.06, 0), "hull_dark", seg=20, bevel=0.01)
    m.torus(0.5, 0.025, (0, 0.14, 0), "hazard_yellow", seg=24, tseg=5)
    m.cyl(0.42, 0.06, (0, 0.15, 0), "steel", seg=20)
    m.cyl(0.4, 1.6, (0, 0.98, 0), "glass_green", seg=20)
    m.cyl(0.36, 1.3, (0, 0.85, 0), "sci_liquid_g", seg=18)
    for k in range(6):
        a = k * 1.047
        m.box((0.03, 1.6, 0.03), (math.cos(a) * 0.41, 0.98, math.sin(a) * 0.41), "steel")
    m.cyl(0.44, 0.1, (0, 1.83, 0), "steel", seg=20, bevel=0.008)
    m.cyl(0.3, 0.2, (0, 1.98, 0), "hull_dark", seg=16, r2=0.2)
    m.cyl(0.08, 0.15, (0, 2.15, 0), "black_metal", seg=10)
    m.sphere(0.15, (0, 0.95, 0), "food_brown", seg=10, ring=7, scale=(1, 1.2, 1))
    m.sphere(0.06, (0.05, 1.1, 0.05), "sci_crystal", seg=6, ring=4)
    for sx in (-1, 1):
        m.link((sx * 0.2, 2.0, 0), (sx * 0.6, 1.9, 0.0), 0.03, "steel", seg=6)
        m.link((sx * 0.6, 1.9, 0), (sx * 0.6, 0.35, 0), 0.03, "steel", seg=6)
    m.box((0.4, 0.15, 0.1), (0, 0.2, 0.52), "hull_dark", 0.01, rot=(-0.4, 0, 0))
    m.screen((0.3, 0.09), (0, 0.21, 0.565), "lifesigns", rot=(-0.4, 0, 0), bezel=0.008)
    for k in range(6):
        m.cyl(0.02, 0.02, (math.cos(k + 0.5) * 0.45, 1.9, math.sin(k + 0.5) * 0.45), "em_amber", seg=6)


@_add(SF, "seed vault")
def _(m, rng):
    m.box((1.0, 1.85, 0.6), (0, 0.925, 0), "sci_frost", 0.03)
    m.box((0.9, 0.04, 0.02), (0, 0.06, 0.31), "black_metal")
    m.cyl(0.36, 0.08, (0, 1.05, 0.31), "steel", axis="z", seg=24)
    m.torus(0.34, 0.03, (0, 1.05, 0.36), "chrome", axis="z", seg=24, tseg=6)
    m.cyl(0.3, 0.05, (0, 1.05, 0.36), "hull_light", axis="z", seg=24)
    m.cyl(0.07, 0.08, (0, 1.05, 0.42), "chrome", axis="z", seg=10)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        m.link((0, 1.05, 0.44), (math.cos(a) * 0.22, 1.05 + math.sin(a) * 0.22, 0.44), 0.014, "chrome", seg=6)
        m.sphere(0.03, (math.cos(a) * 0.22, 1.05 + math.sin(a) * 0.22, 0.44), "black_metal", seg=8, ring=5)
    for k in range(8):
        a = k * math.pi / 4
        m.cyl(0.02, 0.05, (math.cos(a) * 0.33, 1.05 + math.sin(a) * 0.33, 0.35), "steel", axis="z", seg=6)
    m.box((0.8, 0.16, 0.02), (0, 1.68, 0.305), "em_cyan")
    m.screen((0.24, 0.1), (0.3, 0.55, 0.31), "power", bezel=0.008)
    m.box((0.5, 0.05, 0.02), (-0.15, 0.55, 0.305), "hazard_yellow")
    m.box((0.8, 0.14, 0.02), (0, 0.36, 0.305), "sci_white")
    for k in range(5):
        m.box((0.03, 0.06, 0.005), (-0.3 + k * 0.15, 0.36, 0.317), ["em_cyan", "black_metal"][k % 2])
    m.cyl(0.05, 0.1, (0.3, 1.92, -0.1), "steel", seg=8)


@_add(SF, "biocontainment cabinet")
def _(m, rng):
    W, D = 1.3, 0.85
    cab(m, W, 0.8, D, "sci_white", 0.0, 0.02)
    m.box((W - 0.1, 0.6, 0.02), (0, 0.4, D / 2 + 0.004), "paint_green", 0.006)
    hazard(m, 0, 0.22, D / 2 + 0.013, 0.4, 0.08)
    m.box((W + 0.02, 0.04, D + 0.02), (0, 0.82, 0), "steel", 0.008)
    m.box((W, 1.2, 0.08), (0, 1.44, -D / 2 + 0.06), "sci_white", 0.01)
    for sx in (-1, 1):
        m.box((0.08, 1.2, D - 0.06), (sx * (W / 2 - 0.04), 1.44, 0), "sci_white", 0.01)
    m.box((W, 0.3, D), (0, 2.19, 0), "sci_white", 0.02)
    m.box((0.5, 0.08, 0.5), (0, 2.38, -0.1), "hull_dark", 0.01)
    m.cyl(0.15, 0.2, (0, 2.5, -0.1), "steel", seg=12)
    m.box((W - 0.16, 0.9, 0.02), (0, 1.5, D / 2 - 0.05), "glass_green", 0, rot=(0.0, 0, 0))
    m.box((W - 0.1, 0.06, 0.05), (0, 1.02, D / 2 - 0.04), "steel", 0.006)
    m.box((W - 0.1, 0.06, 0.05), (0, 1.99, D / 2 - 0.04), "steel", 0.006)
    for sx in (-0.3, 0.3):
        m.cyl(0.1, 0.05, (sx, 1.48, D / 2 - 0.03), "chrome", axis="z", seg=14)
        m.cyl(0.075, 0.5, (sx, 1.48, D / 2 - 0.3), "rubber", axis="z", seg=10)
        m.sphere(0.07, (sx, 1.48, D / 2 - 0.55), "rubber", seg=8, ring=6)
    m.screen((0.2, 0.1), (0.5, 2.19, D / 2 + 0.01), "lifesigns", bezel=0.008)
    m.box((0.24, 0.24, 0.02), (-0.45, 2.19, D / 2 + 0.01), "hazard_yellow")
    m.box((0.5, 0.02, 0.02), (0, 1.02, D / 2 + 0.03), "em_green")
    m.box((0.3, 0.3, 0.3), (W / 2 + 0.15, 0.95, 0.0), "steel", 0.01)
    m.box((0.26, 0.26, 0.02), (W / 2 + 0.15, 0.95, 0.155), "glass_green")


_reg("specimen", {k: ST[k] for k in ST}, mount="table", tags=TAG + ["specimen"], solid=False)
_reg("specimen", SF, mount="floor", tags=TAG + ["specimen"], solid=True)

# ==========================================================================
# SCIENCE INSTRUMENTS
# ==========================================================================
IT = {}
IF = {}


@_add(IT, "sensor puck array")
def _(m, rng):
    m.box((0.5, 0.03, 0.3), (0, 0.015, 0), "plastic_black", 0.01)
    for k in range(3):
        x = -0.16 + k * 0.16
        m.cyl(0.055, 0.05, (x, 0.055, 0.02), ["paint_orange", "paint_teal", "paint_grey"][k], seg=14, bevel=0.005)
        m.cyl(0.03, 0.02, (x, 0.09, 0.02), "black_metal", seg=10)
        m.cyl(0.006, 0.09 + 0.03 * k, (x, 0.13, 0.02), "chrome", seg=5)
        led(m, (x, 0.058, 0.076), "em_green")
        m.tube([(x, 0.04, -0.03), (x, 0.03, -0.1), (0.2, 0.02, -0.12)], 0.006, "black_metal", seg=5)
    m.box((0.1, 0.04, 0.05), (0.2, 0.05, -0.1), "hull_dark", 0.008)
    m.screen((0.06, 0.03), (0.2, 0.06, -0.073), "bars")


@_add(IT, "probe kit")
def _(m, rng):
    m.box((0.46, 0.05, 0.28), (0, 0.025, 0), "hull_dark", 0.012)
    m.box((0.46, 0.005, 0.28), (0, 0.05, 0), "foam")
    for k, L in enumerate((0.36, 0.3, 0.24, 0.32)):
        z = -0.09 + k * 0.06
        m.cyl(0.012, L, (0, 0.062, z), "steel", axis="x", seg=6, r2=0.004)
        m.cyl(0.02, 0.1, (-0.18 + 0.0, 0.066, z), ["paint_orange", "paint_blue"][k % 2], axis="x", seg=8)
    m.box((0.1, 0.03, 0.08), (0.15, 0.065, 0.05), "black_metal", 0.006)
    led(m, (0.12, 0.084, 0.05), "em_green")
    m.screen((0.06, 0.03), (0.16, 0.082, 0.05), "vitals", rot=(-1.57, 0, 0))
    m.box((0.46, 0.14, 0.03), (0, 0.11, -0.16), "hull_dark", 0.01, rot=(-0.25, 0, 0))


@_add(IT, "geiger counter")
def _(m, rng):
    m.box((0.1, 0.04, 0.2), (0, 0.06, 0), "hull_dark", 0.01)   # stand
    m.box((0.1, 0.2, 0.06), (0, 0.16, 0), "hazard_yellow", 0.015, rot=(-0.15, 0, 0))
    m.box((0.08, 0.08, 0.01), (0, 0.19, 0.04), "black_metal")
    m.screen((0.07, 0.05), (0, 0.2, 0.055), "bars", rot=(-0.15, 0, 0), bezel=0.005)
    m.cyl(0.018, 0.02, (0.02, 0.13, 0.055), "paint_red", axis="z", seg=8)
    m.cyl(0.018, 0.02, (-0.02, 0.13, 0.055), "black_metal", axis="z", seg=8)
    m.cyl(0.03, 0.2, (0, 0.06, 0.16), "steel", axis="z", seg=10)
    m.cyl(0.025, 0.02, (0, 0.06, 0.27), "plastic_black", axis="z", seg=10)
    m.tube([(0, 0.25, -0.02), (0.05, 0.28, -0.05), (0.1, 0.12, -0.1)], 0.006, "black_metal", seg=5)
    m.sphere(0.03, (0.1, 0.03, -0.1), "hazard_yellow", seg=8, ring=6)
    m.cyl(0.03, 0.03, (0.0, 0.055, -0.06), "chrome", seg=8)


@_add(IT, "magnetometer")
def _(m, rng):
    m.box((0.3, 0.06, 0.24), (0, 0.03, 0), "sci_white", 0.012)
    m.box((0.2, 0.05, 0.04), (0, 0.085, 0.1), "black_metal")
    m.screen((0.14, 0.05), (0, 0.06, 0.122), "waveform")
    m.cyl(0.012, 0.36, (-0.06, 0.24, -0.06), "plastic_white", seg=6)
    m.sphere(0.055, (-0.06, 0.45, -0.06), "paint_orange", seg=12, ring=8)
    m.cyl(0.006, 0.4, (0, 0.06, -0.14), "carbon", axis="x", seg=5, rot=(0, 0, 0))
    m.torus(0.08, 0.008, (0.09, 0.12, -0.04), "copper", axis="x", seg=16, tseg=5)
    m.torus(0.08, 0.008, (0.12, 0.12, -0.04), "copper", axis="x", seg=16, tseg=5)
    m.cyl(0.01, 0.1, (0.105, 0.06, -0.04), "steel", seg=5)
    leds(m, -0.1, 0.07, 0.121, 3, 0.03, ["em_green", "em_cyan"], 0.01)


@_add(IT, "portable field lab")
def _(m, rng):
    m.box((0.6, 0.18, 0.4), (0, 0.09, 0), "hazard_yellow", 0.02)
    m.box((0.56, 0.02, 0.36), (0, 0.19, 0), "hull_dark")
    m.box((0.6, 0.4, 0.05), (0, 0.38, -0.2), "hazard_yellow", 0.02, rot=(-0.2, 0, 0))
    m.screen((0.42, 0.28), (0, 0.4, -0.16), "systems", rot=(-0.2, 0, 0), bezel=0.015)
    m.box((0.5, 0.025, 0.3), (0, 0.205, 0.0), "plastic_grey", 0.006)
    for k in range(4):
        m.cyl(0.02, 0.07, (-0.15 + k * 0.1, 0.25, 0.08), ["sci_liquid_g", "sci_liquid_o", "glass", "sci_liquid_b"][k], seg=6)
    m.box((0.14, 0.05, 0.12), (0.18, 0.23, -0.02), "hull_dark", 0.008)
    leds(m, 0.14, 0.26, 0.04, 3, 0.03, ["em_green", "em_amber"], 0.01)
    for sx in (-0.22, 0.22):
        m.box((0.06, 0.04, 0.02), (sx, 0.14, 0.205), "chrome")
    m.box((0.14, 0.03, 0.03), (0, 0.19, 0.19), "black_metal")


@_add(IF, "weather station")
def _(m, rng):
    m.box((0.3, 0.5, 0.2), (0, 0.25, 0), "sci_white", 0.015)
    m.screen((0.2, 0.14), (0, 0.32, 0.105), "bars", bezel=0.01)
    leds(m, -0.1, 0.16, 0.103, 4, 0.06, ["em_green", "em_amber", "em_cyan"])
    m.cyl(0.03, 1.5, (0, 1.24, -0.02), "steel", seg=10)
    m.cyl(0.05, 0.03, (0, 0.5, -0.02), "steel", seg=10)
    m.link((0, 1.0, -0.02), (-0.4, 1.0, -0.02), 0.015, "steel", seg=6)
    m.link((0, 1.5, -0.02), (0.4, 1.5, -0.02), 0.015, "steel", seg=6)
    for k in range(3):
        a = 2.1 * k
        m.link((-0.4, 1.0, -0.02), (-0.4 + math.cos(a) * 0.12, 1.0, -0.02 + math.sin(a) * 0.12), 0.008, "steel", seg=5)
        m.cyl(0.035, 0.03, (-0.4 + math.cos(a) * 0.12, 1.0, -0.02 + math.sin(a) * 0.12), "paint_orange", seg=8, r2=0.05)
    m.sphere(0.03, (-0.4, 1.02, -0.02), "steel", seg=8, ring=6)
    m.box((0.1, 0.02, 0.2), (0.4, 1.53, -0.02), "paint_blue", rot=(0, 0, 0.0))
    m.box((0.06, 0.12, 0.01), (0.52, 1.5, -0.02), "paint_blue")
    for k in range(6):
        m.box((0.16, 0.012, 0.16), (0, 0.85 + k * 0.025, -0.02), "paint_white", rot=(0, 0.3 * k, 0.0)) if k < 5 else None
    m.cyl(0.006, 0.3, (0, 2.1, -0.02), "chrome", seg=5)
    m.sphere(0.04, (0, 2.0, -0.02), "sci_white", seg=10, ring=8)
    m.box((0.32, 0.03, 0.34), (0, 0.015, 0), "black_metal", 0.008)
    for a in (0, 2.09, 4.19):
        m.link((0, 0.5, -0.02), (math.cos(a) * 0.3, 0.02, math.sin(a) * 0.3 - 0.02), 0.012, "steel", seg=5)


@_add(IF, "seismic monitor")
def _(m, rng):
    m.box((0.8, 0.5, 0.6), (0, 0.25, 0), "hull_dark", 0.02)
    m.box((0.76, 0.06, 0.56), (0, 0.53, 0), "steel", 0.006)
    m.box((0.5, 0.36, 0.03), (0, 0.28, 0.305), "black_metal")
    m.screen((0.46, 0.32), (0, 0.28, 0.32), "waveform", bezel=0.008)
    m.cyl(0.14, 0.22, (-0.2, 0.68, 0), "gunmetal", axis="z", seg=16)
    m.cyl(0.02, 0.26, (-0.2, 0.68, 0), "chrome", axis="z", seg=6)
    m.box((0.5, 0.02, 0.3), (0.12, 0.6, 0), "sci_white")
    m.box((0.34, 0.01, 0.005), (0.12, 0.612, 0.0), "paint_red")
    m.box((0.02, 0.08, 0.3), (0.3, 0.64, 0), "steel")
    m.link((-0.2, 0.7, 0.05), (0.22, 0.68, 0.05), 0.004, "brass", seg=4)
    m.link((0.1, 0.65, 0.05), (0.1, 0.9, -0.15), 0.01, "steel", seg=5)
    m.cyl(0.025, 0.1, (0.1, 0.92, -0.15), "paint_orange", seg=8)
    m.cyl(0.11, 0.02, (0.3, 0.55, 0.15), "paint_orange", seg=14)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.03, 0.04, (sx * 0.34, 0.02, sz * 0.24), "rubber", seg=8)
    leds(m, 0.25, 0.44, 0.31, 3, 0.04, ["em_green", "em_amber", "em_red"], 0.014)


@_add(IF, "sample drill rig")
def _(m, rng):
    m.box((0.9, 0.08, 0.8), (0, 0.04, 0), "hazard_yellow", 0.015)
    m.box((0.8, 0.02, 0.7), (0, 0.09, 0), "hull_dark")
    for sx in (-1, 1):
        m.cyl(0.03, 1.7, (sx * 0.2, 0.95, -0.2), "chrome", seg=8)
    m.box((0.5, 0.06, 0.16), (0, 1.85, -0.2), "hull_dark", 0.012)
    m.box((0.5, 0.06, 0.16), (0, 0.12, -0.2), "hull_dark", 0.012)
    m.cyl(0.02, 1.6, (0, 0.95, -0.2), "steel", seg=8)   # lead screw
    m.box((0.36, 0.28, 0.24), (0, 1.3, -0.15), "paint_orange", 0.02)
    m.cyl(0.07, 0.18, (0, 1.06, -0.05), "gunmetal", seg=12)
    m.cyl(0.03, 0.14, (0, 0.92, -0.05), "black_metal", seg=8)
    m.cyl(0.018, 0.95, (0, 0.42, -0.05), "steel", seg=6, r2=0.008)
    for k in range(5):
        m.torus(0.02, 0.005, (0, 0.6 + k * 0.1, -0.05), "brushed_alu", seg=8, tseg=4)
    m.cyl(0.14, 0.04, (0, 0.11, -0.05), "rubber", seg=14)
    m.sphere(0.1, (0.05, 0.16, -0.05), "concrete", seg=8, ring=6, scale=(1.2, 0.7, 1))
    m.box((0.3, 0.2, 0.06), (0.28, 0.35, 0.26), "hull_dark", 0.01, rot=(-0.3, 0, 0))
    m.screen((0.24, 0.14), (0.28, 0.36, 0.295), "diagnostic", rot=(-0.3, 0, 0), bezel=0.008)
    m.box((0.1, 0.25, 0.1), (0.28, 0.2, 0.26), "hull_dark", 0.008)
    leds(m, -0.2, 1.22, 0.06, 3, 0.05, ["em_green", "em_amber"], 0.014)


@_add(IF, "radiation monitor post")
def _(m, rng):
    m.cyl(0.25, 0.06, (0, 0.03, 0), "hazard_yellow", seg=20, bevel=0.008)
    m.cyl(0.08, 1.4, (0, 0.75, 0), "hull_mid", seg=12)
    m.cyl(0.12, 0.1, (0, 0.11, 0), "steel", seg=12, r2=0.08)
    m.box((0.36, 0.4, 0.2), (0, 1.5, 0), "hazard_yellow", 0.02)
    m.box((0.28, 0.1, 0.02), (0, 1.62, 0.105), "black_metal")
    m.screen((0.26, 0.08), (0, 1.62, 0.115), "bars", bezel=0.005)
    m.cyl(0.055, 0.02, (0, 1.42, 0.11), "black_metal", axis="z", seg=16)
    m.cyl(0.04, 0.005, (0, 1.42, 0.125), "sci_white", axis="z", seg=3)
    leds(m, -0.1, 1.33, 0.105, 5, 0.05, ["em_green", "em_green", "em_amber", "em_orange", "em_red"], 0.03)
    m.cyl(0.035, 0.2, (0.0, 1.8, 0), "steel", seg=8)
    m.sphere(0.07, (0, 1.95, 0), "em_red", seg=12, ring=8)
    m.cyl(0.02, 0.15, (0.25, 1.5, 0), "chrome", axis="x", seg=6)
    m.sphere(0.05, (0.35, 1.5, 0), "steel", seg=8, ring=6)
    for k in range(3):
        a = k * 2.09
        m.link((0, 0.15, 0), (math.cos(a) * 0.2, 0.06, math.sin(a) * 0.2), 0.012, "steel", seg=5)


@_add(IF, "field lab trunk")
def _(m, rng):
    m.box((0.9, 0.55, 0.55), (0, 0.32, 0), "gunmetal", 0.03)
    for sx in (-1, 1):
        m.cyl(0.06, 0.05, (sx * 0.35, 0.05, -0.2), "rubber", axis="x", seg=12)
        m.box((0.06, 0.12, 0.06), (sx * 0.35, 0.09, 0.22), "black_metal")
    for k in range(4):
        m.box((0.9, 0.025, 0.02), (0, 0.15 + k * 0.13, 0.28), "hull_dark")
    for sx in (-0.3, 0.3):
        m.box((0.08, 0.06, 0.03), (sx, 0.5, 0.28), "chrome")
    m.box((0.5, 0.3, 0.02), (0, 0.32, 0.285), "hazard_yellow")
    m.box((0.46, 0.06, 0.022), (0, 0.36, 0.296), "black_metal")
    m.box((0.06, 0.06, 0.04), (-0.35, 0.32, 0.28), "em_amber")
    m.box((0.22, 0.02, 0.06), (0, 0.63, 0), "chrome", 0.005)
    m.link((-0.2, 0.61, 0.1), (-0.2, 0.61, -0.1), 0.015, "steel", seg=5)
    m.link((-0.42, 0.62, 0), (-0.42, 0.9, 0), 0.015, "steel", seg=5)
    m.link((-0.42, 0.9, 0), (-0.42, 0.9, -0.3), 0.015, "steel", seg=5)
    m.cyl(0.04, 0.25, (-0.42, 0.95, -0.35), "steel", seg=8)
    m.screen((0.32, 0.2), (0.0, 0.66, 0.1), "diagnostic", rot=(-1.4, 0, 0), bezel=0.012)
    m.box((0.36, 0.02, 0.24), (0, 0.635, 0.1), "black_metal", 0.005)
    m.cyl(0.03, 0.14, (0.3, 0.7, 0.1), "sci_liquid_g", seg=8)
    m.cyl(0.03, 0.14, (0.35, 0.7, 0.05), "sci_liquid_o", seg=8)


_reg("sciinstrument", IT, mount="table", tags=TAG + ["instrument"], solid=False)
_reg("sciinstrument", IF, mount="floor", tags=TAG + ["instrument"], solid=True)

# ==========================================================================
# TELESCOPES
# ==========================================================================
TS = {}


def tripod(m, top_y, spread=0.5, r=0.018, mat="black_metal"):
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.5
        m.link((0, top_y, 0), (math.cos(a) * spread, 0.0, math.sin(a) * spread), r, mat, seg=6)
        m.cyl(0.03, 0.025, (math.cos(a) * spread, 0.0125, math.sin(a) * spread), "rubber", seg=8)
    m.cyl(0.05, 0.06, (0, top_y, 0), "steel", seg=8)


@_add(TS, "observation telescope")
def _(m, rng):
    tripod(m, 1.15, 0.6)
    m.box((0.1, 0.1, 0.18), (0, 1.22, 0), "hull_dark", 0.015)
    m.cyl(0.03, 0.14, (0, 1.32, 0), "steel", axis="x", seg=8)
    rot = (-0.55, 0, 0)
    c = (0, 1.5, 0)
    m.cyl(0.11, 0.9, rp((0, 0, 0.1), rot, c), "sci_white", axis="z", seg=18, rot=rot)
    m.cyl(0.115, 0.05, rp((0, 0, 0.55), rot, c), "black_metal", axis="z", seg=18, rot=rot)
    m.cyl(0.10, 0.02, rp((0, 0, 0.57), rot, c), "glass_blue", axis="z", seg=18, rot=rot)
    m.cyl(0.03, 0.2, rp((0, 0.1, -0.4), rot, c), "black_metal", axis="z", seg=10, rot=rot)
    m.cyl(0.04, 0.04, rp((0, 0.1, -0.52), rot, c), "rubber", axis="z", seg=10, rot=rot)
    m.cyl(0.03, 0.22, rp((0, 0.12, 0.3), rot, c), "black_metal", axis="z", seg=10, rot=rot)
    m.cyl(0.05, 0.03, rp((0, 0.0, 0.0), rot, c), "gold_trim", seg=8)
    m.box((0.04, 0.12, 0.04), rp((0, -0.13, 0.0), rot, c), "steel")
    m.sphere(0.04, (0, 1.45, 0), "steel", seg=8, ring=6)
    m.cyl(0.05, 0.12, rp((0, 0.0, 0.05), rot, c), "hull_dark", axis="x", seg=8, rot=rot)


@_add(TS, "star tracker scope")
def _(m, rng):
    m.cyl(0.25, 0.08, (0, 0.04, 0), "hull_dark", seg=18, bevel=0.008)
    m.cyl(0.12, 0.9, (0, 0.53, 0), "hull_mid", seg=14, r2=0.09)
    m.box((0.3, 0.06, 0.2), (0, 1.0, 0), "gunmetal", 0.01)
    for sx in (-1, 1):
        m.box((0.05, 0.26, 0.16), (sx * 0.17, 1.15, 0), "hull_dark", 0.01)
        m.cyl(0.035, 0.05, (sx * 0.21, 1.2, 0), "gold_trim", axis="x", seg=10)
    rot = (-0.7, 0, 0)
    c = (0, 1.2, 0)
    m.cyl(0.11, 0.55, rp((0, 0, 0.1), rot, c), "black_metal", axis="z", seg=16, rot=rot)
    m.cyl(0.16, 0.3, rp((0, 0, 0.4), rot, c), "black_metal", axis="z", seg=16, r2=0.16, rot=rot)
    m.cyl(0.13, 0.02, rp((0, 0, 0.56), rot, c), "glass_dark", axis="z", seg=16, rot=rot)
    m.torus(0.15, 0.012, rp((0, 0, 0.53), rot, c), "em_cyan", axis="z", seg=16, tseg=5, rot=rot)
    m.box((0.14, 0.1, 0.16), rp((0, 0, -0.25), rot, c), "hull_dark", 0.01, rot=rot)
    led(m, rp((0.08, 0.0, -0.25), rot, c), "em_green")
    m.tube([(0, 0.7, -0.09), (0.1, 0.8, -0.14), (0.15, 1.1, -0.1)], 0.01, "black_metal", seg=5)
    m.box((0.1, 0.08, 0.03), (0, 0.6, 0.11), "black_metal")
    m.screen((0.08, 0.05), (0, 0.6, 0.126), "starmap")


@_add(TS, "astrometric dish")
def _(m, rng):
    m.cyl(0.35, 0.1, (0, 0.05, 0), "hull_dark", seg=20, bevel=0.01)
    m.cyl(0.14, 0.9, (0, 0.55, 0), "hull_mid", seg=14)
    m.box((0.36, 0.16, 0.24), (0, 1.06, 0), "hull_dark", 0.015)
    for sx in (-1, 1):
        m.box((0.05, 0.4, 0.14), (sx * 0.26, 1.25, 0), "hull_mid", 0.01)
    m.cyl(0.03, 0.56, (0, 1.4, 0), "steel", axis="x", seg=8)
    dish(m, (0, 1.4, 0.05), 0.45, rot=(-0.6, 0, 0), mat="paint_white")
    m.cyl(0.04, 0.1, rp((0, 0, -0.1), (-0.6, 0, 0), (0, 1.4, 0.05)), "black_metal", axis="z", seg=8, rot=(-0.6, 0, 0))
    m.cyl(0.05, 0.04, (0, 0.11, 0.3), "paint_red", seg=8)
    leds(m, -0.1, 0.9, 0.147, 3, 0.05, ["em_green", "em_cyan"])


@_add(TS, "spectrograph tripod")
def _(m, rng):
    tripod(m, 1.0, 0.55)
    m.box((0.1, 0.06, 0.1), (0, 1.03, 0), "hull_dark", 0.01)
    m.box((0.36, 0.14, 0.16), (0, 1.13, 0), "sci_white", 0.02)
    m.cyl(0.05, 0.3, (-0.3, 1.18, 0), "black_metal", axis="x", seg=12)
    m.cyl(0.07, 0.05, (-0.48, 1.18, 0), "glass_blue", axis="x", seg=12)
    m.box((0.2, 0.1, 0.24), (0.25, 1.2, 0), "hull_dark", 0.015)
    m.box((0.2, 0.02, 0.24), (0.25, 1.25, 0), "glass_dark")
    m.cyl(0.04, 0.12, (0.4, 1.17, 0), "black_metal", axis="x", seg=10, r2=0.06)
    for k in range(4):
        m.box((0.02, 0.015, 0.3), (0.12, 1.26, 0), "em_violet", rot=(0, 0.0, 0.0)) if k == 0 else None
    m.tube([(0.25, 1.26, 0.1), (0.25, 1.45, 0.2), (0.4, 1.5, 0.3)], 0.008, "black_metal", seg=5)
    m.box((0.14, 0.09, 0.02), (0.4, 1.5, 0.32), "hull_dark")
    m.screen((0.1, 0.06), (0.4, 1.5, 0.332), "waveform")
    leds(m, -0.1, 1.08, 0.085, 3, 0.04, ["em_green", "em_amber"], 0.012)


_reg("telescope", TS, mount="floor", tags=TAG + ["astronomy"], solid=True)

# ==========================================================================
# PARTICLE
# ==========================================================================
PF = {}


@_add(PF, "detector ring segment")
def _(m, rng):
    R = 1.3
    m.box((0.5, 0.2, 1.2), (0, 0.1, 0), "hazard_yellow", 0.02)
    m.box((0.4, 0.15, 1.0), (0, 0.27, 0), "hull_dark", 0.02)
    for k in range(6):
        z = -0.5 + k * 0.2
        m.cyl(1.05, 0.14, (0, 1.4, z), "hull_mid" if k % 2 else "sci_teal", axis="z", seg=24, r2=1.05)
    for k in range(5):
        z = -0.4 + k * 0.2
        m.cyl(1.07, 0.06, (0, 1.4, z), "copper", axis="z", seg=24)
    m.cyl(0.42, 1.25, (0, 1.4, 0), "black_metal", axis="z", seg=20)
    m.cyl(0.3, 1.3, (0, 1.4, 0), "brushed_alu", axis="z", seg=16)
    m.cyl(0.14, 1.32, (0, 1.4, 0), "black_metal", axis="z", seg=12)
    for k in range(10):
        a = k * 0.62
        m.box((0.1, 0.16, 0.6), (math.cos(a) * 0.72, 1.4 + math.sin(a) * 0.72, 0), "em_cyan" if k % 3 == 0 else "gunmetal", rot=(0, 0, a))
    for k in range(3):
        m.box((0.06, 0.06, 0.02), (-0.5 + k * 0.1, 0.5, 0.63), ["em_green", "em_amber", "em_red"][k])
    m.tube([(1.0, 1.4, 0.3), (1.15, 1.0, 0.5), (0.4, 0.3, 0.55)], 0.03, "black_metal", seg=6)


@_add(PF, "mini collider ring")
def _(m, rng):
    m.box((2.6, 0.2, 2.6), (0, 0.1, 0), "hull_dark", 0.02)
    m.box((2.4, 0.04, 0.05), (0, 0.22, 0), "hazard_yellow")
    m.torus(1.0, 0.13, (0, 0.55, 0), "brushed_alu", seg=28, tseg=8)
    for k in range(12):
        a = k * math.pi / 6
        m.box((0.3, 0.32, 0.28), (math.cos(a) * 1.0, 0.55, math.sin(a) * 1.0), "paint_blue" if k % 3 else "paint_orange", 0, rot=(0, -a + math.pi / 2, 0))
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        m.cyl(0.24, 0.38, (math.cos(a) * 1.0, 0.55, math.sin(a) * 1.0), "gunmetal", seg=14)
        m.cyl(0.25, 0.05, (math.cos(a) * 1.0, 0.75, math.sin(a) * 1.0), "gold_trim", seg=14)
    m.torus(1.0, 0.02, (0, 0.55, 0), "em_cyan", seg=28, tseg=4)
    for k in range(6):
        a = k * math.pi / 3 + 0.2
        m.link((math.cos(a) * 1.0, 0.6, math.sin(a) * 1.0), (math.cos(a) * 0.55, 0.9, math.sin(a) * 0.55), 0.03, "copper", seg=6)
    m.cyl(0.4, 0.4, (0, 0.9, 0), "sci_white", seg=16, r2=0.3)
    m.sphere(0.2, (0, 1.2, 0), "sci_crystal", seg=12, ring=8)
    m.box((0.5, 0.3, 0.4), (1.0, 0.35, 1.05), "hull_mid", 0.02)
    m.screen((0.34, 0.2), (1.0, 0.36, 1.26), "waveform", bezel=0.01)


@_add(PF, "plasma chamber")
def _(m, rng):
    m.cyl(0.6, 0.15, (0, 0.075, 0), "hull_dark", seg=20, bevel=0.01)
    m.cyl(0.5, 0.35, (0, 0.33, 0), "gunmetal", seg=16, r2=0.42)
    m.sphere(0.5, (0, 1.05, 0), "glass", seg=18, ring=10)
    m.sphere(0.3, (0, 1.05, 0), "sci_plasma", seg=12, ring=8)
    m.sphere(0.2, (0, 1.05, 0), "em_white", seg=10, ring=7)
    for k in range(6):
        a = k * 1.047
        m.link((0, 1.05, 0), (math.cos(a) * 0.48, 1.05 + math.sin(a * 2) * 0.3, math.sin(a) * 0.48), 0.012, "em_violet", seg=4)
    m.torus(0.52, 0.03, (0, 1.05, 0), "copper", axis="x", seg=18, tseg=5)
    m.torus(0.52, 0.03, (0, 1.05, 0), "copper", axis="z", seg=18, tseg=5)
    m.cyl(0.4, 0.25, (0, 1.6, 0), "gunmetal", seg=20, r2=0.15)
    m.cyl(0.1, 0.3, (0, 1.85, 0), "steel", seg=12)
    for k in range(4):
        a = k * math.pi / 2 + 0.7
        m.cyl(0.06, 0.4, (math.cos(a) * 0.55, 0.55, math.sin(a) * 0.55), "brass", seg=8)
        m.link((math.cos(a) * 0.55, 0.75, math.sin(a) * 0.55), (math.cos(a) * 0.6, 1.4, math.sin(a) * 0.6), 0.025, "copper", seg=6)
    hazard(m, 0, 0.3, 0.475, 0.5, 0.1)
    m.screen((0.3, 0.14), (0.0, 0.14, 0.6), "power", rot=(-0.3, 0, 0), bezel=0.01)


@_add(PF, "tesla emitter")
def _(m, rng):
    m.cyl(0.4, 0.12, (0, 0.06, 0), "hull_dark", seg=20, bevel=0.008)
    m.cyl(0.3, 0.6, (0, 0.42, 0), "wood_dark", seg=16, r2=0.24)
    for k in range(3):
        m.torus(0.28 - k * 0.012, 0.012, (0, 0.2 + k * 0.18, 0), "brass", seg=14, tseg=4)
    m.cyl(0.2, 0.9, (0, 1.2, 0), "copper", seg=16, r2=0.16)
    for k in range(6):
        m.torus(0.19 - k * 0.006, 0.012, (0, 0.85 + k * 0.15, 0), "copper", seg=12, tseg=4)
    m.cyl(0.12, 0.1, (0, 1.7, 0), "brass", seg=12)
    m.sphere(0.24, (0, 1.95, 0), "chrome", seg=16, ring=10)
    m.torus(0.24, 0.03, (0, 1.75, 0), "chrome", seg=16, tseg=5)
    for k in range(5):
        a = k * 1.25
        h = 0.2 + 0.05 * (k % 3)
        m.link((math.cos(a) * 0.16, 2.05, math.sin(a) * 0.16), (math.cos(a) * 0.3, 2.05 + h, math.sin(a) * 0.3), 0.01, "em_violet", seg=4)
        m.link((math.cos(a) * 0.3, 2.05 + h, math.sin(a) * 0.3), (math.cos(a) * 0.36, 2.05 + h * 1.6, math.sin(a) * 0.36 + 0.05), 0.006, "em_white", seg=4)
    m.box((0.3, 0.16, 0.06), (0, 0.16, 0.36), "hull_dark", 0.01, rot=(-0.3, 0, 0))
    leds(m, -0.1, 0.16, 0.39, 3, 0.1, ["em_violet", "em_cyan"], 0.025)


@_add(PF, "tractor field emitter")
def _(m, rng):
    m.box((1.0, 0.1, 1.0), (0, 0.05, 0), "hull_dark", 0.02)
    hazard(m, 0, 0.05, 0.505, 0.8, 0.06)
    m.cyl(0.35, 0.3, (0, 0.25, 0), "hull_mid", seg=18, r2=0.25)
    m.cyl(0.26, 0.05, (0, 0.425, 0), "black_metal", seg=18)
    m.torus(0.26, 0.018, (0, 0.46, 0), "em_cyan", seg=24, tseg=5)
    for k in range(4):
        a = k * math.pi / 2 + 0.78
        m.link((math.cos(a) * 0.3, 0.45, math.sin(a) * 0.3), (math.cos(a) * 0.4, 1.4, math.sin(a) * 0.4), 0.03, "gunmetal", seg=6)
        m.sphere(0.05, (math.cos(a) * 0.4, 1.4, math.sin(a) * 0.4), "chrome", seg=8, ring=6)
    for k in range(4):
        m.torus(0.2 + 0.05 * k, 0.014, (0, 0.65 + k * 0.22, 0), "em_cyan" if k % 2 == 0 else "em_blue", seg=18, tseg=4)
    m.cyl(0.05, 1.0, (0, 1.0, 0), "glass_blue", seg=10, r2=0.05)
    m.cyl(0.02, 0.9, (0, 1.0, 0), "em_white", seg=6)
    m.box((0.3, 0.14, 0.1), (0.3, 0.16, 0.4), "hull_dark", 0.01, rot=(-0.3, 0, 0))
    m.screen((0.24, 0.09), (0.3, 0.17, 0.443), "nav", rot=(-0.3, 0, 0))


@_add(PF, "quantum chandelier")
def _(m, rng):
    # gantry frame that supports a gold, tiered quantum computer chandelier
    for sx in (-1, 1):
        m.box((0.08, 3.0, 0.08), (sx * 0.5, 1.5, -0.3), "gunmetal", 0.008)
    m.box((1.2, 0.1, 0.16), (0, 2.95, -0.3), "hull_dark", 0.01)
    m.box((1.2, 0.08, 0.6), (0, 0.04, -0.1), "hull_dark", 0.01)
    m.link((0, 2.9, -0.3), (0, 2.6, -0.3), 0.04, "gunmetal", seg=8)
    m.link((0, 2.6, -0.3), (0, 2.6, 0), 0.03, "gunmetal", seg=8)
    # plate stack
    tiers = [(2.55, 0.42, "gold_trim"), (2.15, 0.34, "copper"), (1.8, 0.26, "gold_trim"), (1.5, 0.18, "copper"), (1.25, 0.1, "gold_trim")]
    for y, r, mat in tiers:
        m.cyl(r, 0.03, (0, y, 0), mat, seg=16)
        m.torus(r, 0.008, (0, y, 0), "brushed_alu", seg=14, tseg=3)
        for k in range(6):
            a = k * 1.047
            m.link((math.cos(a) * r * 0.9, y, math.sin(a) * r * 0.9), (math.cos(a) * r * 0.9, y + 0.35, math.sin(a) * r * 0.9), 0.009, "brass", seg=4) if y > 1.3 else None
    for k in range(6):
        a = k * 1.047
        m.cyl(0.01, 1.3, (math.cos(a) * 0.3, 1.9, math.sin(a) * 0.3), "brass", seg=5)
    m.cyl(0.03, 1.4, (0, 1.9, 0), "copper", seg=8)
    for k in range(6):
        a = k * 1.047
        m.link((math.cos(a) * 0.4, 2.14, math.sin(a) * 0.4), (math.cos(a) * 0.15, 1.8, math.sin(a) * 0.15), 0.006, "chrome", seg=4)
    m.cyl(0.1, 0.16, (0, 1.14, 0), "black_metal", seg=12, r2=0.06)
    m.sphere(0.07, (0, 1.02, 0), "sci_crystal", seg=10, ring=7)
    for k in range(5):
        a = k * 1.25
        m.sphere(0.02, (math.cos(a) * 0.2, 1.6 - 0.05 * k, math.sin(a) * 0.2), "em_cyan", seg=5, ring=4)
    m.box((0.4, 0.5, 0.3), (0, 0.33, -0.15), "hull_dark", 0.015)
    m.screen((0.3, 0.16), (0, 0.4, 0.008), "systems", bezel=0.008)
    m.cyl(0.06, 0.4, (0.4, 0.28, -0.05), "sci_frost", seg=10)


_reg("particle", PF, mount="floor", tags=TAG + ["physics"], solid=True)
