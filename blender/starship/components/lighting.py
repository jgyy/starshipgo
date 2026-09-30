"""Lighting fixtures and utility props: ceiling/wall/strip lights, sconces, spots, warning lights,
vending machines, fountains, bins, notice boards, cleaning bots, cabinets, toolboxes, clocks."""
import math

from ..kit import family

PI = math.pi
B = {}


def b(label):
    def deco(fn):
        B[label] = fn
        return fn
    return deco


def _run(m, i, label, rng):
    B[label](m, rng)


def bolts(m, pts, r=0.008, mat="steel", axis="y", h=0.008):
    for p in pts:
        m.cyl(r, h, p, mat, axis=axis, seg=6)


def bolts4(m, w, d, y, r=0.008, mat="steel", axis="y", h=0.008, z0=0.0):
    bolts(m, [(sx * w, y, z0 + sz * d) for sx in (-1, 1) for sz in (-1, 1)], r, mat, axis, h)


def wbolts4(m, w, h, y0, z, r=0.008, mat="steel"):
    bolts(m, [(sx * w, y0 + sy * h, z) for sx in (-1, 1) for sy in (-1, 1)], r, mat, "z", 0.008)


# ==========================================================================
# CEILING LIGHTS (origin = centre of top surface, extends down)
CEIL = ["round downlight", "square panel 1x1", "panel troffer 0.6x1.2", "linear fixture 1.2", "twin linear 2.4",
        "pendant globe", "industrial high bay", "cage light", "ring light", "triple spot rail",
        "lounge chandelier ring", "emergency fixture", "recessed hex cells", "cove tray", "flush dome",
        "drum pendant"]


@family("ceilinglight", CEIL, mount="ceiling", tags=["light", "ceiling"], solid=False)
def ceilinglight(m, i, label, rng):
    B["c_" + str(i)](m, rng)


@b("c_0")
def _(m, rng):
    m.cyl(0.17, 0.02, (0, -0.01, 0), "hull_light", seg=24, bevel=0.004)
    m.cyl(0.13, 0.08, (0, -0.06, 0), "hull_mid", seg=20, r2=0.15)
    m.cyl(0.105, 0.012, (0, -0.104, 0), "em_white", seg=20)
    m.torus(0.112, 0.01, (0, -0.1, 0), "chrome", seg=24, tseg=6)
    bolts4(m, 0.13, 0.13, -0.02, 0.007, h=0.006)


@b("c_1")
def _(m, rng):
    m.box((1.0, 0.06, 1.0), (0, -0.03, 0), "hull_light", 0.01)
    m.box((0.9, 0.012, 0.9), (0, -0.066, 0), "em_white")
    for k in (-1, 1):
        m.box((0.9, 0.018, 0.012), (0, -0.068, k * 0.15), "hull_light")
        m.box((0.012, 0.018, 0.9), (k * 0.15, -0.068, 0), "hull_light")
    m.box((0.96, 0.016, 0.96), (0, -0.06, 0), "hull_mid", 0.004)
    bolts4(m, 0.47, 0.47, -0.074, 0.01, h=0.01)


@b("c_2")
def _(m, rng):
    m.box((0.6, 0.07, 1.2), (0, -0.035, 0), "hull_mid", 0.012)
    m.box((0.54, 0.012, 1.14), (0, -0.075, 0), "em_warm")
    for k in range(5):
        m.box((0.52, 0.016, 0.012), (0, -0.078, -0.44 + k * 0.22), "plastic_white")
    m.box((0.62, 0.02, 0.06), (0, -0.01, 0.6), "hull_dark", 0.004)
    m.box((0.62, 0.02, 0.06), (0, -0.01, -0.6), "hull_dark", 0.004)
    m.box((0.05, 0.025, 0.04), (0.2, -0.085, 0.53), "black_metal")


@b("c_3")
def _(m, rng):
    m.box((1.2, 0.05, 0.14), (0, -0.025, 0), "hull_dark", 0.01)
    m.box((1.12, 0.012, 0.09), (0, -0.056, 0), "em_white", 0.003)
    m.box((0.05, 0.06, 0.15), (0.6, -0.03, 0), "black_metal", 0.006)
    m.box((0.05, 0.06, 0.15), (-0.6, -0.03, 0), "black_metal", 0.006)
    for x in (-0.4, 0, 0.4):
        m.box((0.03, 0.015, 0.16), (x, -0.052, 0), "steel")


@b("c_4")
def _(m, rng):
    m.box((2.4, 0.08, 0.26), (0, -0.04, 0), "gunmetal", 0.012)
    for z in (-0.06, 0.06):
        m.box((2.3, 0.014, 0.08), (0, -0.087, z), "em_cyan", 0.004)
    m.box((2.3, 0.02, 0.02), (0, -0.09, 0), "black_metal")
    for x in (-1.1, 0, 1.1):
        m.box((0.08, 0.12, 0.28), (x, -0.06, 0), "hull_dark", 0.008)
    for s in (-1, 1):
        m.box((0.06, 0.09, 0.27), (s * 1.2, -0.045, 0), "black_metal", 0.006)


@b("c_5")
def _(m, rng):
    m.cyl(0.09, 0.03, (0, -0.015, 0), "brass", seg=16, bevel=0.004)
    m.link((0, -0.03, 0), (0, -0.62, 0), 0.008, "black_metal", 6)
    m.cyl(0.05, 0.07, (0, -0.66, 0), "brass", seg=14, r2=0.035)
    m.sphere(0.19, (0, -0.83, 0), "em_warm", 20, 12)
    m.torus(0.05, 0.008, (0, -0.695, 0), "brass", seg=14, tseg=6)
    m.cyl(0.025, 0.03, (0, -1.005, 0), "brass", seg=10)


@b("c_6")
def _(m, rng):
    m.box((0.2, 0.03, 0.2), (0, -0.015, 0), "black_metal", 0.005)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.link((sx * 0.07, -0.03, sz * 0.07), (sx * 0.1, -0.35, sz * 0.1), 0.006, "steel", 5)
    m.cyl(0.11, 0.05, (0, -0.37, 0), "black_metal", seg=16)
    m.cyl(0.42, 0.28, (0, -0.52, 0), "hazard_yellow", seg=24, r2=0.13, bevel=0.005)
    m.torus(0.42, 0.014, (0, -0.66, 0), "steel", seg=24, tseg=6)
    m.cyl(0.24, 0.02, (0, -0.665, 0), "em_white", seg=20)
    m.cyl(0.05, 0.05, (0, -0.68, 0), "black_metal", seg=10)
    for a in range(0, 360, 60):
        r = math.radians(a)
        bolts(m, [(0.32 * math.cos(r), -0.44, 0.32 * math.sin(r))], 0.01, "steel", "y", 0.01)


@b("c_7")
def _(m, rng):
    m.cyl(0.11, 0.03, (0, -0.015, 0), "black_metal", seg=14)
    m.cyl(0.05, 0.05, (0, -0.055, 0), "brass", seg=10)
    m.sphere(0.065, (0, -0.15, 0), "em_warm", 12, 8)
    for h in (-0.08, -0.15, -0.22):
        m.torus(0.09 if h != -0.22 else 0.06, 0.006, (0, h, 0), "steel", seg=14, tseg=5)
    for a in range(0, 360, 45):
        r = math.radians(a)
        m.link((0.05 * math.cos(r), -0.08, 0.05 * math.sin(r)), (0.09 * math.cos(r), -0.08, 0.09 * math.sin(r)), 0.005, "steel", 5) if False else None
        m.link((0.085 * math.cos(r), -0.08, 0.085 * math.sin(r)), (0.09 * math.cos(r), -0.15, 0.09 * math.sin(r)), 0.004, "steel", 4)
        m.link((0.09 * math.cos(r), -0.15, 0.09 * math.sin(r)), (0.06 * math.cos(r), -0.22, 0.06 * math.sin(r)), 0.004, "steel", 4)
    m.cyl(0.06, 0.012, (0, -0.226, 0), "steel", seg=12)


@b("c_8")
def _(m, rng):
    m.torus(0.42, 0.06, (0, -0.07, 0), "hull_light", seg=24, tseg=8)
    m.torus(0.42, 0.03, (0, -0.11, 0), "em_white", seg=24, tseg=6)
    for a in range(0, 360, 90):
        r = math.radians(a)
        m.link((0, -0.03, 0), (0.42 * math.cos(r), -0.06, 0.42 * math.sin(r)), 0.012, "hull_mid", 6)
    m.cyl(0.08, 0.06, (0, -0.03, 0), "hull_dark", seg=14, bevel=0.004)
    m.cyl(0.3, 0.012, (0, -0.01, 0), "hull_dark", seg=20) if False else None


@b("c_9")
def _(m, rng):
    m.box((1.1, 0.04, 0.07), (0, -0.02, 0), "black_metal", 0.006)
    m.box((1.0, 0.012, 0.03), (0, -0.046, 0), "steel")
    for k, x in enumerate((-0.38, 0, 0.38)):
        tilt = (-0.35, 0.0, 0.35)[k]
        m.cyl(0.03, 0.05, (x, -0.06, 0), "steel", seg=8)
        m.cyl(0.05, 0.13, (x, -0.135, 0.02 * k), "gunmetal", seg=12, r2=0.04, rot=(tilt, 0, 0), bevel=0.003)
        m.cyl(0.042, 0.012, (x, -0.2, 0.02 * k + tilt * -0.05), "em_white", seg=12, rot=(tilt, 0, 0))


@b("c_10")
def _(m, rng):
    m.cyl(0.08, 0.03, (0, -0.015, 0), "brass", seg=14)
    m.cyl(0.03, 0.09, (0, -0.075, 0), "brass", seg=10)
    m.torus(0.5, 0.02, (0, -0.72, 0), "brass", seg=24, tseg=5)
    m.torus(0.28, 0.014, (0, -0.68, 0), "gold_trim", seg=24, tseg=6)
    for a in range(0, 360, 120):
        r = math.radians(a + 30)
        m.link((0.03 * math.cos(r), -0.1, 0.03 * math.sin(r)), (0.5 * math.cos(r), -0.72, 0.5 * math.sin(r)), 0.006, "brass", 5)
        m.link((0.28 * math.cos(r + 1.05), -0.68, 0.28 * math.sin(r + 1.05)), (0.5 * math.cos(r), -0.72, 0.5 * math.sin(r)), 0.005, "brass", 5) if False else None
    for a in range(0, 360, 45):
        r = math.radians(a)
        x, z = 0.5 * math.cos(r), 0.5 * math.sin(r)
        m.cyl(0.018, 0.08, (x, -0.78, z), "ceramic", seg=6)
        m.sphere(0.035, (x, -0.85, z), "em_warm", 6, 4, (1, 1.4, 1))
        m.cyl(0.03, 0.01, (x, -0.74, z), "brass", seg=6)
    m.sphere(0.07, (0, -0.72, 0), "em_warm", 12, 8)
    m.link((0, -0.1, 0), (0, -0.66, 0), 0.007, "brass", 6)


@b("c_11")
def _(m, rng):
    m.box((0.56, 0.09, 0.16), (0, -0.045, 0), "paint_white", 0.012)
    for s in (-1, 1):
        m.box((0.1, 0.08, 0.1), (s * 0.2, -0.13, 0), "hull_dark", 0.006, rot=(0, 0, s * 0.35))
        m.cyl(0.055, 0.03, (s * 0.2, -0.17, 0), "em_red" if s < 0 else "em_amber", seg=12)
    m.box((0.14, 0.02, 0.05), (0, -0.098, 0.045), "em_green")
    m.box((0.1, 0.012, 0.04), (0, -0.1, -0.035), "plastic_black")
    m.box((0.5, 0.03, 0.012), (0, -0.02, 0.085), "hazard_yellow")
    bolts(m, [(-0.26, -0.045, 0.081), (0.26, -0.045, 0.081)], 0.008, "steel", "z")


def _hex(r):
    return [(r * math.cos(PI / 3 * k), r * math.sin(PI / 3 * k)) for k in range(6)]


@b("c_12")
def _(m, rng):
    m.prism(_hex(0.5), 0.06, (0, -0.06, 0), "hull_dark", bevel=0.006)
    cells = [(0, 0)] + [(0.26 * math.cos(PI / 3 * k + PI / 6), 0.26 * math.sin(PI / 3 * k + PI / 6)) for k in range(6)]
    for cx, cz in cells:
        m.prism([(cx + x, cz + z) for x, z in _hex(0.115)], 0.012, (0, -0.073, 0), "em_white" if (cx, cz) != (0, 0) else "em_cyan")
        m.prism([(cx + x, cz + z) for x, z in _hex(0.132)], 0.008, (0, -0.066, 0), "hull_light")


@b("c_13")
def _(m, rng):
    m.box((1.6, 0.02, 0.5), (0, -0.01, 0), "hull_mid", 0.004)
    for s in (-1, 1):
        m.box((1.6, 0.14, 0.03), (0, -0.09, s * 0.235), "hull_light", 0.006)
        m.box((1.5, 0.02, 0.05), (0, -0.08, s * 0.2), "em_warm")
    for s in (-1, 1):
        m.box((0.03, 0.14, 0.5), (s * 0.785, -0.09, 0), "hull_light", 0.006)
    m.box((1.5, 0.014, 0.28), (0, -0.16, 0), "em_warm", 0.003)
    m.box((1.5, 0.02, 0.32), (0, -0.155, 0), "plastic_white", 0.003) if False else None
    for x in (-0.55, 0.55):
        m.box((0.05, 0.03, 0.44), (x, -0.155, 0), "hull_dark", 0.004)


@b("c_14")
def _(m, rng):
    m.cyl(0.32, 0.03, (0, -0.015, 0), "chrome", seg=28, bevel=0.005)
    m.sphere(0.29, (0, -0.03, 0), "em_white", 24, 8, (1, 0.5, 1))
    m.torus(0.3, 0.012, (0, -0.032, 0), "chrome", seg=28, tseg=6)
    bolts(m, [(0.3 * math.cos(a), -0.005, 0.3 * math.sin(a)) for a in (0.5, 2.6, 4.7)], 0.012, "brushed_alu", "y", 0.012)


@b("c_15")
def _(m, rng):
    m.cyl(0.07, 0.03, (0, -0.015, 0), "black_metal", seg=12)
    for a in (0, 2.1, 4.2):
        m.link((0.05 * math.cos(a), -0.03, 0.05 * math.sin(a)), (0.25 * math.cos(a), -0.45, 0.25 * math.sin(a)), 0.004, "steel", 4)
    m.cyl(0.3, 0.25, (0, -0.58, 0), "fabric_grey", seg=28)
    m.torus(0.3, 0.012, (0, -0.455, 0), "brass", seg=28, tseg=6)
    m.torus(0.3, 0.012, (0, -0.705, 0), "brass", seg=28, tseg=6)
    m.cyl(0.285, 0.012, (0, -0.706, 0), "em_warm", seg=28)
    m.cyl(0.02, 0.02, (0, -0.45, 0), "brass", seg=8)


# ==========================================================================
# PANEL LIGHTS (wall)
PANEL = ["backlit rectangle", "glowing wall strip", "illuminated logo plate", "wall grazer", "window light box",
         "door side light", "hex glow panel", "triple bar panel", "porthole glow", "tile matrix panel"]


@family("panellight", PANEL, mount="wall", tags=["light", "wall"], solid=False, mount_y=1.6)
def panellight(m, i, label, rng):
    B["p_" + str(i)](m, rng)


@b("p_0")
def _(m, rng):
    m.box((0.66, 0.96, 0.05), (0, 0, 0.025), "hull_dark", 0.012)
    m.box((0.56, 0.86, 0.012), (0, 0, 0.056), "em_white", 0.004)
    m.box((0.6, 0.02, 0.02), (0, 0.4, 0.05), "steel")
    wbolts4(m, 0.3, 0.45, 0, 0.052)


@b("p_1")
def _(m, rng):
    m.box((0.1, 1.3, 0.04), (0, 0, 0.02), "brushed_alu", 0.008)
    m.box((0.05, 1.22, 0.02), (0, 0, 0.045), "em_cyan", 0.004)
    for y in (-0.62, 0.62):
        m.box((0.12, 0.05, 0.06), (0, y, 0.03), "black_metal", 0.005)


@b("p_2")
def _(m, rng):
    m.box((0.6, 0.36, 0.03), (0, 0, 0.015), "hull_dark", 0.01)
    m.box((0.56, 0.32, 0.01), (0, 0, 0.035), "black_metal")
    m.prism([(0, 0.12), (0.1, -0.02), (0.06, -0.02), (0, 0.06), (-0.06, -0.02), (-0.1, -0.02)], 0.012, (-0.18, 0, 0.04), "em_cyan", plane="xy") if False else None
    m.prism([(-0.22, -0.1), (-0.12, 0.1), (-0.06, 0.1), (-0.16, -0.1)], 0.012, (0, 0, 0.04), "em_cyan", plane="xy")
    m.prism([(-0.06, -0.1), (0.04, 0.1), (0.1, 0.1), (0, -0.1)], 0.012, (0, 0, 0.04), "em_cyan", plane="xy")
    m.prism([(0.1, -0.1), (0.2, 0.1), (0.26, 0.1), (0.16, -0.1)], 0.012, (0, 0, 0.04), "em_white", plane="xy")
    m.box((0.5, 0.012, 0.012), (0, -0.14, 0.043), "em_amber")
    wbolts4(m, 0.27, 0.15, 0, 0.037, 0.007)


@b("p_3")
def _(m, rng):
    m.box((0.6, 0.14, 0.12), (0, 0.07, 0.06), "hull_mid", 0.015, rot=(0, 0, 0))
    m.box((0.54, 0.02, 0.08), (0, 0.005, 0.07), "em_warm")
    m.box((0.62, 0.05, 0.14), (0, 0.16, 0.07), "hull_dark", 0.01)
    m.box((0.05, 0.16, 0.13), (0.3, 0.08, 0.065), "black_metal", 0.006)
    m.box((0.05, 0.16, 0.13), (-0.3, 0.08, 0.065), "black_metal", 0.006)


@b("p_4")
def _(m, rng):
    m.box((0.9, 0.9, 0.08), (0, 0, 0.04), "hull_light", 0.015)
    m.box((0.76, 0.76, 0.02), (0, 0, 0.085), "em_white")
    for x in (-0.19, 0.19, 0):
        pass
    m.box((0.78, 0.03, 0.03), (0, 0, 0.1), "brushed_alu")
    m.box((0.03, 0.78, 0.03), (0, 0, 0.1), "brushed_alu")
    m.box((0.98, 0.05, 0.15), (0, -0.475, 0.075), "brushed_alu", 0.01)
    m.box((0.8, 0.8, 0.012), (0, 0, 0.096), "glass_blue")


@b("p_5")
def _(m, rng):
    m.box((0.16, 0.56, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
    m.box((0.1, 0.1, 0.014), (0, 0.18, 0.045), "em_green", 0.003)
    m.box((0.1, 0.1, 0.014), (0, 0.04, 0.045), "em_red", 0.003)
    m.prism([(0, 0.05), (0.035, 0), (0.012, 0), (0.012, -0.05), (-0.012, -0.05), (-0.012, 0), (-0.035, 0)], 0.012, (0, -0.16, 0.04), "em_cyan", plane="xy")
    wbolts4(m, 0.06, 0.25, 0, 0.041, 0.007)


@b("p_6")
def _(m, rng):
    m.prism(_hex(0.3), 0.05, (0, 0, 0), "hull_dark", plane="xy", bevel=0.008)
    m.prism(_hex(0.24), 0.012, (0, 0, 0.05), "em_amber", plane="xy")
    m.prism(_hex(0.12), 0.012, (0, 0, 0.06), "em_white", plane="xy")
    m.torus(0.27, 0.01, (0, 0, 0.052), "brass", axis="z", seg=6, tseg=5) if False else None


@b("p_7")
def _(m, rng):
    m.box((0.8, 0.5, 0.04), (0, 0, 0.02), "gunmetal", 0.01)
    for k, y in enumerate((-0.15, 0, 0.15)):
        m.box((0.7, 0.07, 0.03), (0, y, 0.05), "em_blue" if k != 1 else "em_cyan", 0.005)
    for s in (-1, 1):
        m.box((0.03, 0.44, 0.02), (s * 0.38, 0, 0.05), "steel")


@b("p_8")
def _(m, rng):
    m.cyl(0.32, 0.06, (0, 0, 0.03), "hull_dark", axis="z", seg=28, bevel=0.006)
    m.torus(0.28, 0.025, (0, 0, 0.07), "brushed_alu", axis="z", seg=28, tseg=8)
    m.cyl(0.26, 0.02, (0, 0, 0.065), "em_white", axis="z", seg=28)
    for a in range(0, 360, 45):
        r = math.radians(a)
        m.cyl(0.012, 0.014, (0.28 * math.cos(r), 0.28 * math.sin(r), 0.1), "steel", axis="z", seg=6)


@b("p_9")
def _(m, rng):
    m.box((0.84, 0.84, 0.04), (0, 0, 0.02), "black_metal", 0.008)
    tex = ["em_white", "em_cyan", "em_blue", "em_white"]
    for a in range(2):
        for c in range(2):
            m.box((0.38, 0.38, 0.02), (-0.2 + c * 0.4, -0.2 + a * 0.4, 0.05), tex[a * 2 + c], 0.006)


# ==========================================================================
# STRIP LIGHTS
def _strip_ends(m, L, y, z, h):
    for s in (-1, 1):
        m.box((0.02, h, 0.04 if h < 0.05 else 0.06), (s * L / 2, y, z), "black_metal", 0.003)


@family("striplight", ["floor edge runner", "stair edge light", "floor dash guide"], mount="floor", tags=["light", "strip"], solid=False)
def strip_floor(m, i, label, rng):
    B["sf_" + str(i)](m, rng)


@b("sf_0")
def _(m, rng):
    m.box((2.0, 0.02, 0.06), (0, 0.01, 0), "brushed_alu", 0.004)
    m.box((1.94, 0.008, 0.03), (0, 0.022, 0.005), "em_cyan")
    for s in (-1, 1):
        m.box((0.03, 0.03, 0.06), (s * 1.0, 0.015, 0), "black_metal", 0.004)
    for x in (-0.6, 0, 0.6):
        m.box((0.03, 0.006, 0.06), (x, 0.023, 0), "steel")


@b("sf_1")
def _(m, rng):
    m.box((1.2, 0.025, 0.08), (0, 0.0125, 0), "hazard_yellow", 0.004)
    m.box((1.15, 0.01, 0.025), (0, 0.028, 0.02), "em_amber")
    m.box((1.2, 0.015, 0.02), (0, 0.0075, -0.05), "rubber")
    for k in range(6):
        m.box((0.03, 0.006, 0.08), (-0.55 + k * 0.22, 0.026, 0), "black_metal")


@b("sf_2")
def _(m, rng):
    m.box((1.6, 0.01, 0.12), (0, 0.005, 0), "black_metal", 0.003)
    for k in range(8):
        col = "em_green" if k % 2 == 0 else "em_white"
        m.box((0.12, 0.012, 0.05), (-0.7 + k * 0.2, 0.014, 0), col, 0.003)
    for s in (-1, 1):
        m.prism([(0, 0.05), (0.06, 0), (0, -0.05)], 0.008, (s * 0.83, 0.01, 0), "em_green") if False else None


@family("striplight", ["cove strip warm", "recessed ceiling channel", "hanging linear bar"], mount="ceiling", tags=["light", "strip"], solid=False)
def strip_ceil(m, i, label, rng):
    B["sc_" + str(i)](m, rng)


@b("sc_0")
def _(m, rng):
    m.box((2.0, 0.05, 0.08), (0, -0.025, 0), "hull_light", 0.006)
    m.box((1.9, 0.012, 0.03), (0, -0.056, 0), "em_warm")
    m.box((2.0, 0.06, 0.012), (0, -0.03, -0.045), "hull_mid")
    for x in (-0.9, 0, 0.9):
        m.box((0.04, 0.03, 0.09), (x, -0.015, 0), "steel", 0.004)


@b("sc_1")
def _(m, rng):
    m.box((1.5, 0.03, 0.14), (0, -0.015, 0), "black_metal", 0.004)
    m.box((1.5, 0.008, 0.1), (0, -0.034, 0), "brushed_alu")
    m.box((1.44, 0.008, 0.05), (0, -0.04, 0), "em_white")
    for s in (-1, 1):
        m.box((0.02, 0.05, 0.14), (s * 0.75, -0.025, 0), "gunmetal", 0.004)


@b("sc_2")
def _(m, rng):
    m.box((1.5, 0.05, 0.05), (0, -0.4, 0), "gunmetal", 0.008)
    m.box((1.4, 0.012, 0.03), (0, -0.428, 0), "em_cyan")
    for x in (-0.6, 0.6):
        m.link((x, 0, 0), (x, -0.375, 0), 0.004, "steel", 5)
        m.cyl(0.03, 0.01, (x, -0.005, 0), "steel", seg=8)
    m.box((1.4, 0.012, 0.03), (0, -0.372, 0), "em_white") if False else None


@family("striplight", ["handrail light", "under console glow", "baseboard glow", "dot matrix strip"], mount="wall", tags=["light", "strip"], solid=False, mount_y=1.0)
def strip_wall(m, i, label, rng):
    B["sw_" + str(i)](m, rng)


@b("sw_0")
def _(m, rng):
    m.link((-1.0, 0, 0.07), (1.0, 0, 0.07), 0.022, "brushed_alu", 10)
    m.box((1.9, 0.01, 0.014), (0, -0.017, 0.07), "em_warm")
    for x in (-0.9, 0, 0.9):
        m.box((0.03, 0.035, 0.05), (x, 0, 0.025), "steel", 0.004)
        m.cyl(0.015, 0.05, (x, 0, 0.055), "steel", axis="z", seg=8) if False else None


@b("sw_1")
def _(m, rng):
    m.box((1.8, 0.03, 0.05), (0, 0, 0.025), "black_metal", 0.004)
    m.box((1.74, 0.012, 0.03), (0, -0.017, 0.03), "em_blue")
    for x in (-0.85, 0.85):
        m.box((0.03, 0.05, 0.05), (x, 0, 0.025), "steel", 0.004)


@b("sw_2")
def _(m, rng):
    m.box((1.2, 0.08, 0.02), (0, 0, 0.01), "hull_dark", 0.004)
    m.box((1.2, 0.03, 0.03), (0, -0.02, 0.03), "hull_mid", 0.004)
    m.box((1.16, 0.014, 0.014), (0, 0.02, 0.026), "em_amber")
    for x in (-0.55, 0.55):
        bolts(m, [(x, 0, 0.022)], 0.008, "steel", "z", 0.006)


@b("sw_3")
def _(m, rng):
    m.box((1.0, 0.05, 0.02), (0, 0, 0.01), "black_metal", 0.003)
    for k in range(20):
        m.box((0.02, 0.02, 0.012), (-0.475 + k * 0.05, 0, 0.026), "em_green" if k % 5 else "em_white", 0.002)
    for s in (-1, 1):
        m.box((0.03, 0.055, 0.03), (s * 0.5, 0, 0.015), "steel", 0.004)


# ==========================================================================
# SCONCES (wall)
SCONCE = ["brass candle sconce", "chrome uplight", "frosted glass shell", "lantern sconce", "downlight cone",
          "energy torch", "corridor pill light", "art deco fan"]


@family("sconce", SCONCE, mount="wall", tags=["light", "decor"], solid=False, mount_y=1.7)
def sconce(m, i, label, rng):
    B["s_" + str(i)](m, rng)


@b("s_0")
def _(m, rng):
    m.cyl(0.07, 0.02, (0, 0, 0.01), "brass", axis="z", seg=16, bevel=0.003)
    m.cyl(0.02, 0.1, (0, 0, 0.07), "brass", axis="z", seg=8)
    m.torus(0.09, 0.012, (0, -0.02, 0.11), "brass", axis="x", seg=14, tseg=5, arc=PI) if False else None
    m.link((0, 0, 0.07), (0, -0.1, 0.16), 0.012, "brass", 6)
    m.cyl(0.05, 0.02, (0, -0.1, 0.16), "brass", seg=12)
    m.cyl(0.022, 0.12, (0, -0.03, 0.16), "ceramic", seg=10)
    m.sphere(0.03, (0, 0.06, 0.16), "em_warm", 10, 7, (1, 1.5, 1))
    m.torus(0.05, 0.008, (0, -0.1, 0.16), "gold_trim", seg=12, tseg=5)


@b("s_1")
def _(m, rng):
    m.box((0.1, 0.4, 0.02), (0, 0, 0.01), "chrome", 0.005)
    m.cyl(0.09, 0.3, (0, 0.06, 0.09), "chrome", seg=16, r2=0.06)
    m.cyl(0.08, 0.01, (0, 0.212, 0.09), "em_white", seg=16)
    m.link((0, -0.1, 0.02), (0, -0.05, 0.09), 0.014, "chrome", 8)


@b("s_2")
def _(m, rng):
    m.box((0.2, 0.06, 0.02), (0, 0.11, 0.01), "brushed_alu", 0.004)
    m.sphere(0.13, (0, 0, 0.13), "em_white", 18, 10, (0.75, 1.15, 0.7))
    m.cyl(0.09, 0.03, (0, 0.11, 0.05), "brushed_alu", axis="z", seg=12)
    m.torus(0.09, 0.014, (0, -0.09, 0.13), "brushed_alu", seg=14, tseg=5) if False else None
    m.cyl(0.07, 0.03, (0, -0.13, 0.13), "brushed_alu", seg=12, r2=0.05)


@b("s_3")
def _(m, rng):
    m.box((0.14, 0.34, 0.02), (0, 0.02, 0.01), "black_metal", 0.004)
    m.link((0, 0.12, 0.02), (0, 0.12, 0.16), 0.012, "black_metal", 6)
    m.box((0.16, 0.03, 0.16), (0, 0.16, 0.13), "black_metal", 0.004) if False else None
    m.box((0.16, 0.02, 0.16), (0, 0.26, 0.15), "black_metal", 0.004, rot=(0, 0, 0))
    m.box((0.16, 0.02, 0.16), (0, -0.06, 0.15), "black_metal", 0.004)
    m.box((0.12, 0.28, 0.12), (0, 0.1, 0.15), "em_amber", 0.004)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.link((sx * 0.075, -0.05, 0.15 + sz * 0.075), (sx * 0.075, 0.25, 0.15 + sz * 0.075), 0.007, "black_metal", 5)
    m.cyl(0.03, 0.05, (0, 0.3, 0.15), "black_metal", seg=8)


@b("s_4")
def _(m, rng):
    m.box((0.14, 0.14, 0.03), (0, 0.1, 0.015), "hull_dark", 0.006)
    m.box((0.06, 0.05, 0.1), (0, 0.1, 0.07), "hull_dark", 0.004)
    m.cyl(0.07, 0.1, (0, 0.06, 0.14), "hull_mid", seg=14, r2=0.03)
    m.box((0.07, 0.05, 0.08), (0, 0.07, 0.09), "hull_mid") if False else None
    m.cyl(0.07, 0.012, (0, 0.006, 0.14), "em_white", seg=14)


@b("s_5")
def _(m, rng):
    m.box((0.12, 0.12, 0.03), (0, -0.1, 0.015), "gunmetal", 0.005)
    m.link((0, -0.1, 0.03), (0, 0.02, 0.12), 0.02, "gunmetal", 8)
    m.cyl(0.055, 0.16, (0, 0.14, 0.14), "copper", seg=10, r2=0.09)
    m.sphere(0.075, (0, 0.24, 0.14), "em_orange", 12, 8, (1, 1.3, 1))
    m.torus(0.075, 0.012, (0, 0.2, 0.14), "gunmetal", seg=12, tseg=5)
    m.sphere(0.04, (0, 0.28, 0.14), "em_amber", 8, 6)


@b("s_6")
def _(m, rng):
    m.box((0.12, 0.34, 0.03), (0, 0, 0.015), "hull_dark", 0.01)
    m.cyl(0.04, 0.24, (0, 0, 0.06), "em_white", axis="y", seg=10, cap=True)
    m.box((0.1, 0.28, 0.03), (0, 0, 0.035), "hull_light", 0.012)
    m.box((0.06, 0.24, 0.02), (0, 0, 0.055), "em_white", 0.008)
    for y in (-0.15, 0.15):
        bolts(m, [(0, y, 0.031)], 0.008, "steel", "z")


@b("s_7")
def _(m, rng):
    m.box((0.1, 0.06, 0.03), (0, -0.1, 0.015), "gold_trim", 0.005)
    m.prism([(0, 0), (-0.22, 0.24), (-0.1, 0.28), (0, 0.2), (0.1, 0.28), (0.22, 0.24)], 0.04, (0, -0.12, 0.09), "gold_trim", plane="zy", rot=(0, 0, 0)) if False else None
    for k, a in enumerate((-0.9, -0.45, 0, 0.45, 0.9)):
        m.box((0.05, 0.3, 0.03), (0.16 * math.sin(a), -0.02 + 0.0 * a, 0.045), "em_warm", 0.005, rot=(0, 0, -a * 0.9)) if False else None
        m.box((0.05, 0.3, 0.025), (0.14 * math.sin(a), -0.02 + 0.06 * (1 - math.cos(a)) * -1, 0.05), "em_warm", 0.004, rot=(0, 0, -a))
    m.cyl(0.05, 0.02, (0, -0.1, 0.03), "gold_trim", axis="z", seg=12)
    m.torus(0.2, 0.01, (0, -0.1, 0.03), "brass", axis="z", seg=16, tseg=5, arc=PI) if False else None


# ==========================================================================
# SPOTLIGHTS
@family("spotlight", ["recessed spot can", "track light pair", "gimbal spot", "stage truss lights"], mount="ceiling", tags=["light", "spot"], solid=False)
def spot_ceil(m, i, label, rng):
    B["sp_" + str(i)](m, rng)


@b("sp_0")
def _(m, rng):
    m.cyl(0.11, 0.015, (0, -0.0075, 0), "black_metal", seg=18)
    m.cyl(0.08, 0.14, (0, -0.085, 0), "hull_dark", seg=16, r2=0.06, bevel=0.003)
    for k in range(4):
        m.torus(0.078 - 0.004 * k, 0.005, (0, -0.06 - 0.03 * k, 0), "steel", seg=16, tseg=4)
    m.cyl(0.06, 0.012, (0, -0.16, 0), "em_white", seg=16)


@b("sp_1")
def _(m, rng):
    m.box((0.9, 0.04, 0.05), (0, -0.02, 0), "black_metal", 0.005)
    for k, x in enumerate((-0.25, 0.25)):
        t = 0.5 - k * 1.0
        m.box((0.05, 0.05, 0.05), (x, -0.06, 0), "gunmetal", 0.005)
        m.cyl(0.06, 0.2, (x, -0.17, 0.05 * -t), "gunmetal", seg=14, r2=0.045, rot=(t * 0.7, 0, 0), bevel=0.004)
        m.cyl(0.055, 0.012, (x, -0.26, 0.05 * -t + t * -0.07), "em_warm", seg=14, rot=(t * 0.7, 0, 0))
        m.cyl(0.02, 0.06, (x, -0.06, 0), "steel", seg=8, rot=(0, 0, PI / 2))
    m.box((0.06, 0.05, 0.06), (0.45, -0.025, 0), "steel", 0.004)


@b("sp_2")
def _(m, rng):
    m.cyl(0.1, 0.02, (0, -0.01, 0), "hull_mid", seg=16)
    m.torus(0.13, 0.014, (0, -0.15, 0), "brushed_alu", axis="z", seg=20, tseg=6, rot=(0, 0, 0)) if False else None
    m.torus(0.12, 0.014, (0, -0.16, 0), "brushed_alu", axis="z", seg=20, tseg=6)
    m.box((0.05, 0.13, 0.05), (0, -0.075, 0), "hull_dark", 0.005)
    m.sphere(0.09, (0, -0.16, 0), "gunmetal", 14, 10)
    m.cyl(0.075, 0.1, (0, -0.16, 0.06), "black_metal", axis="z", seg=14, r2=0.08)
    m.cyl(0.07, 0.012, (0, -0.16, 0.115), "em_white", axis="z", seg=14)
    for s in (-1, 1):
        m.cyl(0.02, 0.02, (s * 0.12, -0.16, 0), "steel", axis="x", seg=8)


@b("sp_3")
def _(m, rng):
    for z in (-0.3, 0.3):
        m.cyl(0.03, 1.4, (0, -0.03, z), "steel", axis="x", seg=10)
    for x in (-0.6, 0.6, 0):
        m.box((0.04, 0.03, 0.66), (x, -0.03, 0), "steel", 0.003)
    m.box((1.5, 0.05, 0.05), (0, -0.01, 0.3), "black_metal") if False else None
    for k, (x, z) in enumerate(((-0.45, -0.3), (0.0, 0.3), (0.45, -0.3))):
        m.box((0.16, 0.03, 0.03), (x, -0.075, z), "black_metal")
        m.link((x, -0.03, z), (x, -0.1, z), 0.012, "steel", 6)
        m.box((0.18, 0.18, 0.2), (x, -0.22, z), "black_metal", 0.01, rot=(0.4 * (1 if z < 0 else -1), 0, 0))
        m.box((0.15, 0.15, 0.012), (x, -0.29, z + (0.06 if z < 0 else -0.06)), "em_white", rot=(0.4 * (1 if z < 0 else -1), 0, 0))


@family("spotlight", ["hangar flood wall", "inspection lamp flex arm"], mount="wall", tags=["light", "spot"], solid=False, mount_y=2.4)
def spot_wall(m, i, label, rng):
    B["sw2_" + str(i)](m, rng)


@b("sw2_0")
def _(m, rng):
    m.box((0.3, 0.3, 0.03), (0, 0, 0.015), "hull_dark", 0.006)
    m.link((0, 0, 0.03), (0, 0.06, 0.28), 0.03, "gunmetal", 8)
    m.box((0.5, 0.36, 0.14), (0, 0.06, 0.36), "hull_mid", 0.02, rot=(0.35, 0, 0))
    m.box((0.44, 0.3, 0.02), (0, 0.02, 0.43), "em_white", rot=(0.35, 0, 0))
    for k in range(4):
        m.box((0.5, 0.012, 0.16), (0, 0.15 - k * 0.07, 0.4), "black_metal", rot=(0.35, 0, 0)) if False else None
    m.box((0.54, 0.03, 0.12), (0, 0.235, 0.32), "black_metal", 0.004, rot=(0.35, 0, 0))
    m.cyl(0.02, 0.06, (0.26, 0.06, 0.34), "steel", axis="x", seg=8)
    bolts4(m, 0.11, 0.11, 0, 0.012, "steel", "z", 0.01, 0) if False else None


@b("sw2_1")
def _(m, rng):
    m.box((0.12, 0.16, 0.05), (0, 0, 0.025), "hull_dark", 0.008)
    m.cyl(0.03, 0.05, (0, 0, 0.075), "black_metal", axis="z", seg=10)
    pts = [(0, 0, 0.09), (0.0, 0.12, 0.24), (0.05, 0.28, 0.38), (0.0, 0.34, 0.52)]
    m.tube(pts, 0.012, "black_metal", seg=6)
    for p in pts[:-1]:
        m.torus(0.014, 0.004, p, "steel", axis="z", seg=8, tseg=4) if False else None
    m.cyl(0.05, 0.13, (0.0, 0.29, 0.6), "paint_orange", axis="z", seg=12, r2=0.075, bevel=0.003)
    m.cyl(0.062, 0.012, (0.0, 0.29, 0.67), "em_white", axis="z", seg=12)
    m.box((0.03, 0.05, 0.07), (0, 0.375, 0.54), "black_metal", 0.004)
    m.sphere(0.02, (0.0, 0.34, 0.52), "steel", 8, 6)


@family("spotlight", ["tripod floodlight", "search light pedestal"], mount="floor", tags=["light", "spot"], solid=True)
def spot_floor(m, i, label, rng):
    B["sfl_" + str(i)](m, rng)


@b("sfl_0")
def _(m, rng):
    for a in (0, 2.09, 4.19):
        ca, sa = math.cos(a), math.sin(a)
        m.link((0.45 * ca, 0.0, 0.45 * sa), (0.03 * ca, 1.4, 0.03 * sa), 0.013, "steel", 6)
        m.sphere(0.02, (0.45 * ca, 0.02, 0.45 * sa), "rubber", 6, 4)
        m.link((0.25 * ca, 0.55, 0.25 * sa), (0.02, 0.3, 0.02), 0.006, "steel", 4) if False else None
    m.cyl(0.05, 0.35, (0, 1.3, 0), "black_metal", seg=10)
    m.cyl(0.045, 0.2, (0, 1.5, 0), "steel", seg=10)
    m.torus(0.05, 0.012, (0, 1.4, 0), "paint_orange", seg=10, tseg=5)
    m.box((0.48, 0.34, 0.16), (0, 1.75, 0.04), "paint_orange", 0.02)
    m.box((0.42, 0.28, 0.02), (0, 1.75, 0.13), "em_white", 0.004)
    m.box((0.54, 0.03, 0.06), (0, 1.9, 0.02), "black_metal", 0.004)
    for s in (-1, 1):
        m.box((0.03, 0.4, 0.05), (s * 0.27, 1.65, 0.0), "black_metal", 0.004)
    m.box((0.36, 0.04, 0.04), (0, 1.58, 0.0), "black_metal", 0.004) if False else None


@b("sfl_1")
def _(m, rng):
    m.cyl(0.32, 0.08, (0, 0.04, 0), "hazard_yellow", seg=24, bevel=0.008)
    m.cyl(0.24, 0.08, (0, 0.12, 0), "hull_dark", seg=20, r2=0.18)
    m.cyl(0.09, 1.0, (0, 0.7, 0), "hull_mid", seg=14, r2=0.07)
    m.cyl(0.14, 0.05, (0, 1.22, 0), "black_metal", seg=16)
    for s in (-1, 1):
        m.box((0.04, 0.3, 0.12), (s * 0.24, 1.36, 0), "hull_dark", 0.006)
    m.cyl(0.22, 0.5, (0, 1.4, 0.22), "hull_light", axis="z", seg=24, r2=0.25, bevel=0.004)
    m.cyl(0.2, 0.02, (0, 1.4, 0.485), "em_white", axis="z", seg=24)
    m.torus(0.24, 0.02, (0, 1.4, 0.49), "chrome", axis="z", seg=24, tseg=6)
    m.box((0.1, 0.06, 0.16), (0, 1.66, 0.1), "black_metal", 0.006)
    m.cyl(0.02, 0.1, (0.24, 1.4, 0), "steel", axis="x", seg=8)


# ==========================================================================
# WARNING LIGHTS
WARN = ["signal tower", "rotating beacon", "pressure status light", "door state light", "rail marker light",
        "red alert wall unit", "floor guide disc", "docking guide bar"]


@family("warnlight", ["signal tower", "rotating beacon", "rail marker light", "floor guide disc", "docking guide bar"],
        mount="floor", tags=["light", "warning"], solid=False)
def warn_floor(m, i, label, rng):
    B["wf_" + str(i)](m, rng)


@b("wf_0")
def _(m, rng):
    m.cyl(0.12, 0.05, (0, 0.025, 0), "black_metal", seg=14, bevel=0.005)
    m.cyl(0.03, 0.55, (0, 0.32, 0), "steel", seg=10)
    for k, c in enumerate(("em_green", "em_amber", "em_red")):
        m.cyl(0.07, 0.11, (0, 0.35 + k * 0.12, 0), c, seg=16)
        m.cyl(0.078, 0.012, (0, 0.295 + k * 0.12, 0), "black_metal", seg=16)
    m.cyl(0.07, 0.02, (0, 0.72, 0), "black_metal", seg=16, r2=0.05)
    m.cyl(0.02, 0.05, (0, 0.75, 0), "steel", seg=8)
    bolts(m, [(0.09 * math.cos(a), 0.052, 0.09 * math.sin(a)) for a in (0.5, 2.6, 4.7)], 0.01, "steel")


@b("wf_1")
def _(m, rng):
    m.cyl(0.14, 0.05, (0, 0.025, 0), "hazard_yellow", seg=16, bevel=0.005)
    m.cyl(0.1, 0.06, (0, 0.08, 0), "black_metal", seg=14)
    m.cyl(0.085, 0.16, (0, 0.19, 0), "em_amber", seg=16, r2=0.075)
    m.sphere(0.075, (0, 0.27, 0), "em_amber", 14, 6, (1, 0.6, 1))
    m.box((0.02, 0.09, 0.08), (0, 0.19, 0), "black_metal") if False else None
    m.box((0.012, 0.1, 0.14), (0, 0.19, 0), "black_metal")
    for a in (0.8, 2.4, 3.9, 5.5):
        m.box((0.03, 0.02, 0.03), (0.13 * math.cos(a), 0.06, 0.13 * math.sin(a)), "steel")


@b("wf_2")
def _(m, rng):
    m.cyl(0.05, 0.04, (0, 0.02, 0), "black_metal", seg=10)
    m.cyl(0.032, 0.5, (0, 0.29, 0), "paint_white", seg=10, r2=0.028)
    m.cyl(0.035, 0.08, (0, 0.335, 0), "hazard_yellow", seg=10) if False else None
    for y in (0.16, 0.24):
        m.cyl(0.034, 0.03, (0, y, 0), "paint_red", seg=10)
    m.sphere(0.045, (0, 0.55, 0), "em_red", 12, 8)
    m.cyl(0.05, 0.015, (0, 0.525, 0), "black_metal", seg=12)
    m.cyl(0.04, 0.03, (0, 0.585, 0), "black_metal", seg=10, r2=0.01) if False else None


@b("wf_3")
def _(m, rng):
    m.cyl(0.11, 0.015, (0, 0.0075, 0), "black_metal", seg=20)
    m.cyl(0.085, 0.02, (0, 0.02, 0), "em_green", seg=20)
    m.torus(0.1, 0.008, (0, 0.022, 0), "steel", seg=20, tseg=5)
    m.prism([(0, 0.05), (0.04, -0.03), (0, -0.01), (-0.04, -0.03)], 0.006, (0, 0.03, 0), "black_metal")
    for a in range(0, 360, 90):
        r = math.radians(a + 45)
        m.cyl(0.008, 0.008, (0.1 * math.cos(r) * 1.1, 0.012, 0.1 * math.sin(r) * 1.1), "steel", seg=6)


@b("wf_4")
def _(m, rng):
    m.box((1.8, 0.06, 0.2), (0, 0.03, 0), "hull_dark", 0.01)
    m.box((1.7, 0.02, 0.12), (0, 0.065, 0), "black_metal", 0.004)
    cols = ["em_red", "em_amber", "em_green", "em_green", "em_amber", "em_red"]
    for k, c in enumerate(cols):
        m.box((0.2, 0.03, 0.1), (-0.72 + k * 0.288, 0.08, 0), c, 0.006)
    for s in (-1, 1):
        m.box((0.1, 0.09, 0.22), (s * 0.9, 0.045, 0), "hazard_yellow", 0.006)
    m.box((0.1, 0.02, 0.05), (0, 0.075, 0.13), "steel")


@family("warnlight", ["pressure status light", "door state light", "red alert wall unit"], mount="wall", tags=["light", "warning"], solid=False, mount_y=2.0)
def warn_wall(m, i, label, rng):
    B["ww_" + str(i)](m, rng)


@b("ww_0")
def _(m, rng):
    m.box((0.2, 0.44, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    for k, c in enumerate(("em_red", "em_amber", "em_green")):
        m.cyl(0.05, 0.03, (0, 0.13 - k * 0.13, 0.065), c, axis="z", seg=14)
        m.torus(0.055, 0.008, (0, 0.13 - k * 0.13, 0.055), "steel", axis="z", seg=14, tseg=5)
    m.box((0.14, 0.04, 0.01), (0, -0.2, 0.054), "plastic_white") if False else None
    m.box((0.14, 0.03, 0.01), (0, 0.2, 0.054), "hazard_yellow")


@b("ww_1")
def _(m, rng):
    m.box((0.34, 0.12, 0.05), (0, 0, 0.025), "gunmetal", 0.01)
    m.box((0.1, 0.07, 0.015), (-0.09, 0, 0.055), "em_green", 0.004)
    m.box((0.1, 0.07, 0.015), (0.09, 0, 0.055), "screen_off", 0.004) if False else None
    m.box((0.1, 0.07, 0.015), (0.09, 0, 0.055), "em_red", 0.004)
    m.box((0.02, 0.09, 0.02), (0, 0, 0.055), "steel")
    m.prism([(0, 0.02), (0.02, 0), (0, -0.02), (-0.02, 0)], 0.01, (-0.09, 0, 0.065), "black_metal", plane="xy")


@b("ww_2")
def _(m, rng):
    m.box((0.36, 0.36, 0.08), (0, 0, 0.04), "paint_red", 0.012)
    m.cyl(0.14, 0.05, (0, 0, 0.1), "em_red", axis="z", seg=20, r2=0.13)
    m.sphere(0.13, (0, 0, 0.115), "glass", 18, 8, (1, 1, 0.3))
    m.box((0.02, 0.2, 0.05), (0, 0, 0.11), "black_metal")
    m.box((0.34, 0.03, 0.03), (0, 0.17, 0.09), "hazard_yellow", 0.003)
    m.box((0.34, 0.03, 0.03), (0, -0.17, 0.09), "hazard_yellow", 0.003)
    wbolts4(m, 0.15, 0.15, 0, 0.082, 0.01)


# ==========================================================================
# VENDING (floor, solid)
def _vend_base(m, body, front_w=0.9, D=0.8, H=1.9):
    m.box((front_w, H, D), (0, H / 2, 0), body, 0.02)
    m.box((front_w - 0.06, 0.06, D - 0.04), (0, 0.03, 0), "black_metal", 0.005)


def _coin_card(m, x, y, z, card=True):
    m.box((0.16, 0.22, 0.03), (x, y, z), "black_metal", 0.006)
    m.box((0.1, 0.012, 0.012), (x, y + 0.08, z + 0.02), "em_green")
    m.box((0.05, 0.02, 0.012), (x - 0.035, y + 0.03, z + 0.02), "steel")
    if card:
        m.box((0.09, 0.008, 0.012), (x, y - 0.02, z + 0.02), "em_cyan")
    m.box((0.1, 0.014, 0.014), (x, y - 0.075, z + 0.02), "steel")


@family("vending", ["snack machine", "drink machine", "tech parts machine", "ticket kiosk"], mount="floor", tags=["vending", "prop"], solid=True)
def vending(m, i, label, rng):
    B["v_" + str(i)](m, rng)


@b("v_0")
def _(m, rng):
    _vend_base(m, "paint_red")
    m.box((0.6, 1.3, 0.04), (-0.1, 1.0, 0.4), "glass_dark")
    m.box((0.66, 1.36, 0.02), (-0.1, 1.0, 0.395), "black_metal", 0.004)
    for r in range(5):
        m.box((0.56, 0.02, 0.3), (-0.1, 0.55 + r * 0.25, 0.28), "steel")
        for c in range(4):
            col = ("food_red", "food_green", "hazard_yellow", "paint_orange", "food_brown")[(r + c) % 5]
            m.box((0.1, 0.16, 0.06), (-0.24 + c * 0.13, 0.66 + r * 0.25, 0.3), col)
            m.cyl(0.01, 0.12, (-0.24 + c * 0.13, 0.63 + r * 0.25, 0.27), "steel", axis="z", seg=6) if False else None
    m.box((0.7, 0.14, 0.02), (-0.03, 1.82, 0.41), "em_warm") if False else None
    m.box((0.82, 0.12, 0.03), (0, 1.8, 0.4), "em_warm", 0.005)
    m.box((0.2, 1.3, 0.03), (0.34, 1.0, 0.4), "black_metal", 0.005)
    _coin_card(m, 0.34, 1.25, 0.42)
    for k in range(6):
        m.box((0.05, 0.03, 0.012), (0.3 + (k % 3) * 0.05 - 0.05, 1.05 - (k // 3) * 0.05, 0.42), "steel")
    m.box((0.6, 0.18, 0.06), (-0.1, 0.26, 0.4), "black_metal", 0.008)
    m.box((0.5, 0.1, 0.02), (-0.1, 0.26, 0.43), "glass_dark")


@b("v_1")
def _(m, rng):
    _vend_base(m, "paint_blue", front_w=0.95, D=0.85)
    m.box((0.62, 1.4, 0.03), (-0.13, 1.03, 0.43), "em_cyan", 0.004)
    for r in range(6):
        for c in range(6):
            col = ("paint_red", "paint_white", "paint_orange", "paint_green", "paint_blue", "hazard_yellow")[(r * 2 + c) % 6]
            m.cyl(0.032, 0.12, (-0.32 + c * 0.1, 0.5 + r * 0.22, 0.42), col, axis="x", seg=8, rot=(0, 0, 0)) if False else None
            m.cyl(0.032, 0.14, (-0.32 + c * 0.104, 0.55 + r * 0.22, 0.44), col, seg=6)
    m.box((0.2, 1.4, 0.03), (0.34, 1.03, 0.43), "hull_dark", 0.006)
    _coin_card(m, 0.34, 1.35, 0.455)
    m.box((0.5, 0.2, 0.05), (-0.13, 0.22, 0.44), "black_metal", 0.008)
    m.box((0.95, 0.09, 0.04), (0, 1.83, 0.41), "paint_white", 0.006)
    m.box((0.9, 0.05, 0.02), (0, 1.83, 0.435), "em_white")
    m.box((0.16, 0.12, 0.03), (0.34, 0.6, 0.45), "black_metal", 0.005)
    m.box((0.1, 0.06, 0.02), (0.34, 0.6, 0.47), "steel") if False else None


@b("v_2")
def _(m, rng):
    _vend_base(m, "gunmetal")
    m.box((0.64, 1.3, 0.03), (-0.1, 1.0, 0.4), "glass_blue")
    m.box((0.68, 1.34, 0.02), (-0.1, 1.0, 0.39), "black_metal", 0.004)
    for r in range(6):
        m.box((0.6, 0.015, 0.25), (-0.1, 0.5 + r * 0.2, 0.3), "steel")
        for c in range(3):
            w = 0.14 + 0.02 * ((r + c) % 3)
            m.box((w, 0.12, 0.06), (-0.27 + c * 0.18, 0.565 + r * 0.2, 0.3), ("paint_green", "paint_orange", "hull_light")[(r + c) % 3])
            m.box((0.05, 0.015, 0.012), (-0.27 + c * 0.18, 0.565 + r * 0.2, 0.335), "em_cyan")
    m.box((0.2, 1.3, 0.03), (0.34, 1.0, 0.4), "hull_dark", 0.006)
    m.box((0.15, 0.21, 0.012), (0.34, 1.45, 0.415), "black_metal", 0.003)
    m.box((0.12, 0.05, 0.01), (0.34, 1.5, 0.425), "em_cyan")
    m.box((0.12, 0.03, 0.01), (0.34, 1.43, 0.425), "em_green")
    m.box((0.12, 0.03, 0.01), (0.34, 1.38, 0.425), "em_amber")
    _coin_card(m, 0.34, 1.15, 0.42)
    m.box((0.82, 0.1, 0.03), (0, 1.82, 0.4), "em_cyan", 0.005)
    m.box((0.6, 0.18, 0.07), (-0.1, 0.24, 0.4), "black_metal", 0.008)
    m.box((0.9, 0.05, 0.02), (0, 1.0, 0.405), "hazard_yellow") if False else None
    for y in (0.72, 1.6):
        m.box((0.04, 0.04, 0.02), (0.44, y, 0.405), "hazard_yellow")


@b("v_3")
def _(m, rng):
    m.box((0.9, 1.9, 0.6), (0, 0.95, 0), "paint_navy", 0.02)
    m.box((0.84, 0.06, 0.56), (0, 0.03, 0), "black_metal", 0.005)
    m.box((0.9, 0.16, 0.7), (0, 1.86, 0.05), "paint_navy", 0.02)
    m.box((0.8, 0.09, 0.02), (0, 1.86, 0.4), "em_amber", 0.004)
    m.screen((0.6, 0.45), (0, 1.5, 0.305), "starmap", bezel=0.02)
    m.box((0.62, 0.22, 0.08), (0, 1.07, 0.34), "black_metal", 0.01, rot=(-0.3, 0, 0))
    for r in range(3):
        for c in range(4):
            m.box((0.1, 0.02, 0.03), (-0.19 + c * 0.126, 1.04 + r * 0.055, 0.365 - r * 0.005), "plastic_grey", rot=(-0.3, 0, 0))
    _coin_card(m, -0.25, 0.7, 0.32)
    m.box((0.2, 0.16, 0.02), (0.15, 0.7, 0.31), "black_metal")
    m.box((0.16, 0.012, 0.03), (0.15, 0.7, 0.325), "em_cyan") if False else None
    m.box((0.22, 0.03, 0.03), (0.15, 0.7, 0.325), "em_white")
    m.box((0.6, 0.16, 0.05), (0, 0.32, 0.32), "black_metal", 0.008)
    m.box((0.5, 0.05, 0.02), (0, 0.32, 0.35), "em_green")


# ==========================================================================
# FOUNTAINS
@family("fountain", ["drinking fountain wall unit"], mount="wall", tags=["prop"], solid=False, mount_y=0.9)
def fountain_wall(m, i, label, rng):
    m.box((0.5, 0.3, 0.3), (0, 0.05, 0.15), "brushed_alu", 0.02)
    m.box((0.44, 0.02, 0.28), (0, 0.205, 0.16), "steel")
    m.box((0.34, 0.02, 0.22), (0, 0.19, 0.17), "chrome", 0.006)
    m.box((0.5, 0.5, 0.03), (0, 0.1, 0.015), "hull_dark", 0.006)
    m.link((0, 0.2, 0.06), (0, 0.32, 0.12), 0.014, "chrome", 8)
    m.sphere(0.02, (0, 0.33, 0.13), "chrome", 8, 6)
    m.cyl(0.03, 0.03, (0.18, 0.31, 0.1), "paint_blue", seg=10)
    m.cyl(0.028, 0.02, (0.18, 0.33, 0.1), "chrome", seg=10)
    m.box((0.1, 0.03, 0.012), (0, 0.0, 0.306), "em_cyan")
    m.box((0.5, 0.1, 0.05), (0, -0.14, 0.03), "steel", 0.005)
    m.cyl(0.03, 0.1, (0, -0.08, 0.14), "steel", seg=8)


@family("fountain", ["water cooler tower"], mount="floor", tags=["prop"], solid=True)
def fountain_floor(m, i, label, rng):
    m.box((0.36, 0.95, 0.36), (0, 0.475, 0), "paint_white", 0.015)
    m.box((0.32, 0.03, 0.32), (0, 0.015, 0), "black_metal")
    m.cyl(0.14, 0.3, (0, 1.1, 0), "glass_blue", seg=20, r2=0.13)
    m.cyl(0.15, 0.03, (0, 0.96, 0), "hull_mid", seg=20)
    m.cyl(0.05, 0.04, (0, 1.27, 0), "hull_mid", seg=12, r2=0.03)
    m.sphere(0.13, (0, 1.36, 0), "glass_blue", 16, 8, (1, 0.7, 1)) if False else None
    for k, (c, x) in enumerate((("paint_blue", -0.07), ("paint_red", 0.07))):
        m.box((0.1, 0.1, 0.03), (x, 0.8, 0.185), "black_metal", 0.005)
        m.box((0.05, 0.05, 0.02), (x, 0.8, 0.205), c)
        m.cyl(0.02, 0.04, (x, 0.7, 0.2), "chrome", axis="z", seg=8)
    m.box((0.3, 0.02, 0.1), (0, 0.63, 0.19), "black_metal") if False else None
    m.box((0.28, 0.03, 0.09), (0, 0.6, 0.2), "steel", 0.004)
    m.box((0.22, 0.06, 0.02), (0, 0.55, 0.19), "black_metal")
    m.box((0.2, 0.006, 0.006), (0, 0.51, 0.2), "em_cyan") if False else None
    m.box((0.06, 0.02, 0.01), (0, 0.9, 0.185), "em_cyan")


# ==========================================================================
# BINS
@family("bin", ["trash bin", "recycling bin triple"], mount="floor", tags=["prop", "bin"], solid=True)
def bin_floor(m, i, label, rng):
    B["b_" + str(i)](m, rng)


@b("b_0")
def _(m, rng):
    m.cyl(0.22, 0.7, (0, 0.35, 0), "steel", seg=20, r2=0.26, bevel=0.004)
    m.cyl(0.27, 0.06, (0, 0.73, 0), "hull_dark", seg=20, bevel=0.005)
    m.cyl(0.2, 0.02, (0, 0.765, 0), "black_metal", seg=20)
    m.box((0.28, 0.05, 0.05), (0, 0.75, 0.21), "steel") if False else None
    m.box((0.2, 0.09, 0.02), (0, 0.72, 0.27), "black_metal", 0.004)
    m.cyl(0.06, 0.0, (0, 0, 0), "steel") if False else None
    m.torus(0.235, 0.012, (0, 0.3, 0), "hull_dark", seg=20, tseg=5)
    m.box((0.12, 0.12, 0.012), (0, 0.45, 0.245), "hazard_yellow", rot=(-0.14, 0, 0))
    m.cyl(0.24, 0.03, (0, 0.015, 0), "rubber", seg=20)


@b("b_1")
def _(m, rng):
    m.box((1.2, 0.85, 0.45), (0, 0.475, 0), "hull_dark", 0.015)
    m.box((1.24, 0.04, 0.5), (0, 0.92, 0), "black_metal", 0.008)
    m.box((1.1, 0.05, 0.4), (0, 0.04, 0), "rubber")
    for k, (c, em) in enumerate((("paint_blue", "em_blue"), ("paint_green", "em_green"), ("paint_orange", "em_amber"))):
        x = -0.4 + k * 0.4
        m.box((0.34, 0.06, 0.02), (x, 0.9, 0.245), "black_metal") if False else None
        m.box((0.3, 0.12, 0.03), (x, 0.7, 0.235), c, 0.005)
        m.box((0.26, 0.02, 0.012), (x, 0.755, 0.253), em)
        m.box((0.25, 0.04, 0.03), (x, 0.96, 0.05), "black_metal", 0.006)
        m.box((0.2, 0.012, 0.2), (x, 0.945, 0.0), "black_metal") if False else None
        m.box((0.2, 0.02, 0.1), (x, 0.945, 0.12), "steel")
        m.box((0.03, 0.4, 0.012), (x + 0.11, 0.4, 0.235), c)
    m.box((0.02, 0.85, 0.46), (-0.2, 0.475, 0), "black_metal") if False else None
    for x in (-0.2, 0.2):
        m.box((0.015, 0.7, 0.46), (x, 0.44, 0), "black_metal")


@family("bin", ["waste chute door", "incinerator hatch"], mount="wall", tags=["prop", "bin"], solid=False, mount_y=1.0)
def bin_wall(m, i, label, rng):
    B["bw_" + str(i)](m, rng)


@b("bw_0")
def _(m, rng):
    m.box((0.6, 0.7, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
    m.group("flap", pivot=(0, 0.28, 0.06))
    m.box((0.46, 0.5, 0.04), (0, 0.02, 0.06), "steel", 0.01)
    m.box((0.3, 0.06, 0.03), (0, -0.16, 0.095), "black_metal", 0.008)
    m.box((0.1, 0.1, 0.012), (0, 0.1, 0.085), "hazard_yellow")
    m.group("body")
    m.box((0.52, 0.56, 0.02), (0, 0.02, 0.05), "black_metal", 0.004)
    m.box((0.5, 0.04, 0.02), (0, -0.28, 0.06), "hazard_yellow") if False else None
    m.box((0.16, 0.05, 0.012), (0, 0.3, 0.045), "em_green")
    wbolts4(m, 0.26, 0.3, 0, 0.042, 0.01)


@b("bw_1")
def _(m, rng):
    m.box((0.8, 0.8, 0.06), (0, 0, 0.03), "hull_dark", 0.012)
    m.cyl(0.32, 0.03, (0, 0, 0.075), "black_metal", axis="z", seg=24)
    m.group("hatch", pivot=(-0.34, 0, 0.1))
    m.cyl(0.29, 0.05, (0, 0, 0.11), "gunmetal", axis="z", seg=24, bevel=0.005)
    m.torus(0.2, 0.014, (0, 0, 0.14), "paint_orange", axis="z", seg=20, tseg=5)
    m.box((0.05, 0.16, 0.05), (0.15, 0, 0.16), "steel", 0.008)
    m.group("body")
    m.box((0.5, 0.06, 0.015), (0, 0.34, 0.065), "hazard_yellow")
    m.box((0.5, 0.06, 0.015), (0, -0.34, 0.065), "hazard_yellow")
    m.box((0.1, 0.05, 0.02), (0.3, 0.3, 0.07), "em_red")
    for a in range(0, 360, 60):
        r = math.radians(a)
        m.cyl(0.015, 0.02, (0.32 * math.cos(r), 0.32 * math.sin(r), 0.09), "steel", axis="z", seg=6)


# ==========================================================================
# NOTICE BOARDS (wall)
@family("noticeboard", ["cork bulletin board", "digital message board", "duty roster display"], mount="wall", tags=["prop", "sign"], solid=False, mount_y=1.5)
def noticeboard(m, i, label, rng):
    B["n_" + str(i)](m, rng)


@b("n_0")
def _(m, rng):
    m.box((1.2, 0.8, 0.04), (0, 0, 0.02), "wood_dark", 0.01)
    m.box((1.1, 0.7, 0.012), (0, 0, 0.046), "cardboard")
    cols = ["paint_white", "hazard_yellow", "paint_white", "paint_green", "paint_white", "food_red"]
    for k in range(9):
        w, h = 0.16 + 0.03 * (k % 3), 0.2 + 0.03 * (k % 2)
        x = -0.4 + (k % 4) * 0.28 + rng.uniform(-0.02, 0.02)
        y = 0.16 - (k // 4) * 0.28 + rng.uniform(-0.02, 0.02)
        m.box((w, h, 0.004), (x, y, 0.055 + 0.002 * (k % 2)), cols[k % 6], rot=(0, 0, rng.uniform(-0.08, 0.08)))
        m.sphere(0.01, (x, y + h / 2 - 0.02, 0.06), "paint_red", 6, 4)
    m.box((1.2, 0.03, 0.06), (0, -0.4, 0.05), "wood_dark", 0.004)


@b("n_1")
def _(m, rng):
    m.box((1.4, 0.5, 0.06), (0, 0, 0.03), "black_metal", 0.012)
    m.screen((1.3, 0.4), (0, 0, 0.062), "text", bezel=0.0)
    m.box((1.4, 0.02, 0.07), (0, 0.26, 0.035), "brushed_alu", 0.004) if False else None
    m.box((0.2, 0.012, 0.01), (0.55, -0.23, 0.066), "em_cyan")
    for s in (-1, 1):
        m.box((0.03, 0.06, 0.05), (s * 0.5, 0.3, 0.025), "steel", 0.004)
    m.box((0.04, 0.02, 0.01), (-0.65, -0.225, 0.066), "em_green")


@b("n_2")
def _(m, rng):
    m.box((1.0, 1.3, 0.05), (0, 0, 0.025), "hull_dark", 0.012)
    m.box((0.94, 0.14, 0.02), (0, 0.55, 0.06), "hull_mid", 0.004)
    m.box((0.5, 0.05, 0.012), (0, 0.55, 0.072), "em_amber")
    m.screen((0.86, 1.0), (0, -0.05, 0.056), "bars", bezel=0.015)
    for k in range(5):
        m.box((0.08, 0.05, 0.012), (-0.42 + k * 0.05, -0.6, 0.06), ("em_green", "em_amber", "em_red", "em_cyan", "em_white")[k]) if False else None
    m.box((0.9, 0.06, 0.02), (0, -0.6, 0.06), "black_metal", 0.004)
    for k in range(5):
        m.box((0.08, 0.03, 0.01), (-0.32 + k * 0.16, -0.6, 0.07), ("em_green", "em_amber", "em_red", "em_cyan", "em_white")[k])


# ==========================================================================
# CLEANING BOTS (floor, solid)
@family("cleaningbot", ["floor scrubber disc", "wall window crawler", "service drone with arm"], mount="floor", tags=["bot", "prop"], solid=True)
def cleaningbot(m, i, label, rng):
    B["cb_" + str(i)](m, rng)


@b("cb_0")
def _(m, rng):
    m.cyl(0.36, 0.05, (0, 0.05, 0), "rubber", seg=28)
    m.torus(0.35, 0.03, (0, 0.05, 0), "black_metal", seg=28, tseg=6) if False else None
    m.cyl(0.34, 0.16, (0, 0.14, 0), "paint_white", seg=28, r2=0.3, bevel=0.005)
    m.cyl(0.29, 0.06, (0, 0.24, 0), "paint_teal", seg=28, r2=0.26)
    m.cyl(0.1, 0.05, (0, 0.29, 0), "hull_dark", seg=16, r2=0.08)
    m.sphere(0.045, (0, 0.33, 0), "em_cyan", 10, 6)
    m.torus(0.33, 0.012, (0, 0.13, 0), "em_green", seg=28, tseg=5) if False else None
    m.torus(0.315, 0.008, (0, 0.135, 0), "em_green", seg=28, tseg=5)
    m.box((0.2, 0.06, 0.02), (0, 0.16, 0.335), "black_metal", 0.005, rot=(-0.1, 0, 0))
    m.box((0.1, 0.02, 0.02), (0, 0.16, 0.345), "em_amber")
    for s in (-1, 1):
        m.cyl(0.03, 0.03, (s * 0.2, 0.015, 0.2), "steel", seg=8)


@b("cb_1")
def _(m, rng):
    m.box((0.5, 0.14, 0.5), (0, 0.5, 0), "paint_white", 0.03)
    m.box((0.44, 0.06, 0.44), (0, 0.58, 0), "paint_blue", 0.02)
    m.cyl(0.16, 0.03, (0, 0.44, 0.0), "black_metal", seg=18) if False else None
    for sx in (-1, 1):
        m.box((0.12, 0.22, 0.46), (sx * 0.3, 0.5, 0), "black_metal", 0.02) if False else None
        m.box((0.12, 0.2, 0.7), (sx * 0.31, 0.5, 0), "black_metal", 0.04)
        m.cyl(0.065, 0.14, (sx * 0.31, 0.5, 0.3), "rubber", axis="x", seg=12) if False else None
        for z in (-0.28, 0.28):
            m.cyl(0.08, 0.13, (sx * 0.31, 0.5, z), "rubber", axis="x", seg=12)
            m.cyl(0.04, 0.14, (sx * 0.31, 0.5, z), "steel", axis="x", seg=8)
    m.cyl(0.12, 0.05, (0, 0.44, 0), "hull_dark", seg=18)
    m.box((0.2, 0.05, 0.02), (0, 0.5, 0.26), "em_cyan")
    m.box((0.5, 0.05, 0.04), (0, 0.42, 0.27), "hazard_yellow") if False else None
    m.box((0.36, 0.05, 0.09), (0, 0.33, 0.0), "brushed_alu", 0.01) if False else None
    m.box((0.4, 0.06, 0.06), (0, 0.4, 0.0), "steel", 0.008)
    m.box((0.1, 0.1, 0.04), (0, 0.6, 0.0), "black_metal", 0.006) if False else None
    m.cyl(0.03, 0.08, (0.15, 0.65, 0.1), "steel", seg=8)
    m.link((0.15, 0.68, 0.1), (0.15, 0.78, 0.0), 0.008, "steel", 5)
    m.sphere(0.03, (0.15, 0.8, 0.0), "em_amber", 8, 6)


@b("cb_2")
def _(m, rng):
    m.sphere(0.22, (0, 1.1, 0), "paint_white", 14, 8, (1, 0.75, 1))
    m.torus(0.22, 0.03, (0, 1.1, 0), "paint_orange", seg=16, tseg=5)
    m.sphere(0.07, (0, 1.1, 0.19), "em_cyan", 12, 8, (1, 1, 0.5))
    m.torus(0.08, 0.012, (0, 1.1, 0.19), "black_metal", axis="z", seg=12, tseg=5) if False else None
    m.cyl(0.1, 0.06, (0, 1.29, 0), "hull_dark", seg=14, r2=0.06)
    m.cyl(0.02, 0.1, (0, 1.4, 0), "steel", seg=6)
    m.sphere(0.02, (0, 1.46, 0), "em_red", 8, 6)
    for a in range(4):
        r = a * PI / 2 + PI / 4
        x, z = 0.38 * math.cos(r), 0.38 * math.sin(r)
        m.link((0.16 * math.cos(r), 1.1, 0.16 * math.sin(r)), (x, 1.14, z), 0.02, "hull_dark", 6)
        m.cyl(0.11, 0.015, (x, 1.16, z), "hull_mid", seg=10)
        m.cyl(0.09, 0.02, (x, 1.185, z), "black_metal", seg=10)
    m.link((0.12, 0.98, 0.1), (0.2, 0.82, 0.28), 0.018, "hull_mid", 6)
    m.sphere(0.03, (0.2, 0.82, 0.28), "steel", 8, 6)
    m.link((0.2, 0.82, 0.28), (0.12, 0.68, 0.46), 0.014, "hull_mid", 6)
    m.box((0.14, 0.03, 0.06), (0.12, 0.65, 0.5), "paint_orange", 0.005)
    m.cyl(0.04, 0.06, (0.12, 0.6, 0.52), "rubber", seg=8, r2=0.06) if False else None
    m.box((0.02, 0.06, 0.03), (0.06, 0.62, 0.52), "steel")
    m.box((0.02, 0.06, 0.03), (0.18, 0.62, 0.52), "steel")
    m.cyl(0.1, 0.04, (0, 0.96, 0), "hull_dark", seg=14, r2=0.05)
    m.cyl(0.15, 0.02, (0, 0.98, 0), "em_cyan", seg=14)
    for a in (0.3, 2.4, 4.5):
        ca, sa = math.cos(a), math.sin(a)
        m.link((0.14 * ca, 1.02, 0.14 * sa), (0.3 * ca, 0.03, 0.3 * sa), 0.014, "hull_dark", 5)
        m.cyl(0.04, 0.03, (0.3 * ca, 0.015, 0.3 * sa), "rubber", seg=8)


# ==========================================================================
# CABINETS
@family("cabinet", ["utility cabinet", "janitor closet"], mount="floor", tags=["prop", "storage"], solid=True)
def cabinet_floor(m, i, label, rng):
    B["cab_" + str(i)](m, rng)


@b("cab_0")
def _(m, rng):
    m.box((0.9, 1.8, 0.5), (0, 0.9, 0), "hull_mid", 0.015)
    for s in (-1, 1):
        m.box((0.43, 1.7, 0.03), (s * 0.22, 0.9, 0.255), "hull_light", 0.008)
        for k in range(7):
            m.box((0.3, 0.012, 0.012), (s * 0.22, 1.45 + k * 0.03, 0.275), "hull_dark") if False else None
        for k in range(6):
            m.box((0.3, 0.012, 0.012), (s * 0.22, 1.5 + k * 0.035, 0.275), "hull_dark")
        m.box((0.03, 0.2, 0.03), (s * 0.04, 0.95, 0.285), "black_metal", 0.005)
    m.box((0.05, 0.05, 0.02), (-0.22, 1.2, 0.27), "hazard_yellow") if False else None
    m.box((0.2, 0.12, 0.02), (-0.22, 1.2, 0.27), "hazard_yellow")
    m.box((0.06, 0.06, 0.012), (0.22, 1.2, 0.27), "em_green")
    m.box((0.96, 0.05, 0.56), (0, 0.025, 0), "black_metal", 0.005)
    m.box((0.96, 0.03, 0.56), (0, 1.815, 0), "black_metal", 0.005)


@b("cab_1")
def _(m, rng):
    m.box((0.8, 1.9, 0.6), (0, 0.95, 0), "paint_green", 0.02)
    m.box((0.7, 1.8, 0.03), (0, 0.95, 0.305), "paint_green", 0.008)
    m.box((0.7, 0.03, 0.03), (0, 0.5, 0.325), "hull_dark")
    for k in range(8):
        m.box((0.5, 0.02, 0.012), (0, 1.5 + k * 0.035, 0.325), "hull_dark")
    m.box((0.06, 0.06, 0.03), (0.25, 0.95, 0.335), "steel", 0.008)
    m.box((0.3, 0.14, 0.012), (-0.05, 1.3, 0.323), "paint_white")
    m.box((0.2, 0.03, 0.012), (-0.05, 1.3, 0.33), "paint_blue")
    m.box((0.14, 0.14, 0.012), (-0.2, 0.7, 0.323), "hazard_yellow")
    m.box((0.6, 0.03, 0.12), (0, 1.94, 0.02), "hull_dark", 0.005)
    m.box((0.85, 0.06, 0.65), (0, 0.03, 0), "black_metal", 0.005)
    m.cyl(0.11, 0.2, (0.22, 1.98, -0.05), "paint_blue", seg=8) if False else None


@family("cabinet", ["wall storage lockers"], mount="wall", tags=["prop", "storage"], solid=False, mount_y=1.3)
def cabinet_wall(m, i, label, rng):
    m.box((1.2, 0.8, 0.35), (0, 0, 0.175), "hull_dark", 0.012)
    for k in range(3):
        x = -0.4 + k * 0.4
        m.box((0.37, 0.74, 0.02), (x, 0, 0.36), ("paint_grey", "paint_grey", "paint_teal")[k], 0.006)
        for j in range(4):
            m.box((0.24, 0.012, 0.01), (x, 0.22 + j * 0.03, 0.375), "black_metal")
        m.box((0.03, 0.12, 0.03), (x + 0.13, -0.05, 0.385), "steel", 0.005)
        m.box((0.06, 0.03, 0.01), (x, -0.25, 0.372), "plastic_white")
    m.box((0.04, 0.04, 0.012), (0.4, 0.28, 0.372), "em_green") if False else None
    m.box((0.06, 0.03, 0.01), (0.4, 0.3, 0.375), "em_green")


# ==========================================================================
# TOOLBOX (table)
@family("toolbox", ["tabletop toolbox", "tool bag", "cleaning caddy"], mount="table", tags=["prop", "tool"], solid=False)
def toolbox(m, i, label, rng):
    B["t_" + str(i)](m, rng)


@b("t_0")
def _(m, rng):
    m.box((0.46, 0.2, 0.22), (0, 0.1, 0), "paint_red", 0.012)
    m.box((0.48, 0.03, 0.24), (0, 0.205, 0), "paint_red", 0.008)
    m.box((0.48, 0.02, 0.02), (0, 0.13, 0.115), "black_metal") if False else None
    m.box((0.1, 0.05, 0.03), (0, 0.16, 0.125), "steel", 0.006)
    for s in (-1, 1):
        m.box((0.04, 0.05, 0.02), (s * 0.19, 0.2, 0.125), "steel", 0.004)
        m.box((0.03, 0.05, 0.05), (s * 0.23, 0.24, 0), "black_metal", 0.004) if False else None
        m.box((0.03, 0.07, 0.03), (s * 0.15, 0.245, 0), "steel", 0.004)
    m.box((0.32, 0.03, 0.03), (0, 0.285, 0), "rubber", 0.008)
    m.box((0.14, 0.05, 0.005), (0, 0.11, 0.111), "hazard_yellow")
    m.cyl(0.02, 0.012, (0.15, 0.1, 0.11), "steel", axis="z", seg=8)


@b("t_1")
def _(m, rng):
    m.box((0.5, 0.2, 0.22), (0, 0.1, 0), "fabric_tan", 0.04)
    m.box((0.46, 0.06, 0.2), (0, 0.22, 0), "leather_brown", 0.03)
    for s in (-1, 1):
        m.link((s * 0.14, 0.24, 0), (s * 0.08, 0.36, 0), 0.014, "leather_brown", 6)
    m.box((0.2, 0.03, 0.03), (0, 0.375, 0), "leather_brown", 0.01)
    m.box((0.48, 0.03, 0.12), (0, 0.15, 0.09), "leather_brown", 0.01)
    m.box((0.05, 0.05, 0.01), (0, 0.15, 0.155), "brass")
    for x in (-0.15, -0.05, 0.05, 0.15):
        m.box((0.03, 0.08, 0.02), (x, 0.25, 0.08), ("steel", "paint_orange", "steel", "hazard_yellow")[int((x + 0.15) * 10) % 4])


@b("t_2")
def _(m, rng):
    m.box((0.36, 0.03, 0.22), (0, 0.015, 0), "plastic_grey", 0.006)
    m.box((0.36, 0.14, 0.012), (0, 0.1, 0.1), "paint_blue", 0.004)
    m.box((0.36, 0.14, 0.012), (0, 0.1, -0.1), "paint_blue", 0.004)
    for s in (-1, 1):
        m.box((0.012, 0.14, 0.2), (s * 0.174, 0.1, 0), "paint_blue", 0.004)
    m.box((0.35, 0.16, 0.02), (0, 0.1, 0), "paint_blue")
    m.box((0.02, 0.28, 0.02), (0, 0.22, 0), "steel")
    for k, (c, x) in enumerate((("paint_green", -0.1), ("paint_orange", 0.0), ("glass_blue", 0.1))):
        m.cyl(0.028, 0.14, (x, 0.12, 0.055), c, seg=8)
        m.cyl(0.012, 0.03, (x, 0.205, 0.055), "paint_white", seg=6)
        m.cyl(0.006, 0.03, (x, 0.23, 0.055), "paint_red", seg=6)
    m.cyl(0.05, 0.1, (0.12, 0.09, -0.05), "foam", seg=8) if False else None
    m.box((0.1, 0.06, 0.06), (0.1, 0.06, -0.05), "food_green", 0.01)
    m.box((0.08, 0.02, 0.04), (-0.1, 0.045, -0.06), "food_red", 0.005)


# ==========================================================================
# CLOCKS (wall)
@family("clock", ["analogue chronometer", "digital clock", "dual time ship clock"], mount="wall", tags=["prop", "clock"], solid=False, mount_y=2.2)
def clock(m, i, label, rng):
    B["k_" + str(i)](m, rng)


@b("k_0")
def _(m, rng):
    m.cyl(0.24, 0.05, (0, 0, 0.025), "brass", axis="z", seg=28, bevel=0.005)
    m.cyl(0.2, 0.02, (0, 0, 0.055), "paint_white", axis="z", seg=28)
    m.torus(0.22, 0.02, (0, 0, 0.05), "gold_trim", axis="z", seg=28, tseg=6)
    for k in range(12):
        a = k * PI / 6
        L = 0.03 if k % 3 == 0 else 0.015
        m.box((0.008 if k % 3 else 0.014, L, 0.008), (0.17 * math.sin(a), 0.17 * math.cos(a), 0.068), "black_metal", rot=(0, 0, -a))
    m.box((0.014, 0.11, 0.008), (0.04 * math.sin(0.9) * 0 - 0.03, 0.045, 0.076), "black_metal", rot=(0, 0, 0.5))
    m.box((0.01, 0.16, 0.008), (0.06, -0.01, 0.084), "black_metal", rot=(0, 0, -1.9))
    m.box((0.004, 0.17, 0.006), (0, 0.02, 0.09), "em_red", rot=(0, 0, 0.2)) if False else None
    m.cyl(0.015, 0.02, (0, 0, 0.09), "gold_trim", axis="z", seg=8)
    m.sphere(0.2, (0, 0, 0.068), "glass", 20, 6, (1, 1, 0.08))


@b("k_1")
def _(m, rng):
    m.box((0.5, 0.2, 0.06), (0, 0, 0.03), "black_metal", 0.012)
    m.box((0.44, 0.14, 0.01), (0, 0, 0.065), "screen_off")
    digs = {0: "1110111", 1: "0010010", 2: "1011101", 3: "1011011", 4: "0111010", 5: "1101011", 6: "1101111", 7: "1010010", 8: "1111111", 9: "1111011"}
    show = [1, 4, 2, 7]
    xs = [-0.17, -0.09, 0.05, 0.13]
    for d, x in zip(show, xs):
        seg = digs[d]
        segs = [((0, 0.05), 0.05, 0.012), ((-0.03, 0.025), 0.012, 0.05), ((0.03, 0.025), 0.012, 0.05),
                ((0, 0), 0.05, 0.012), ((-0.03, -0.025), 0.012, 0.05), ((0.03, -0.025), 0.012, 0.05), ((0, -0.05), 0.05, 0.012)]
        for on, (p, w, h) in zip(seg, segs):
            if on == "1":
                m.box((w, h, 0.006), (x + p[0], p[1], 0.072), "em_red")
    for y in (0.02, -0.02):
        m.box((0.014, 0.014, 0.006), (-0.02, y, 0.072), "em_red")
    m.box((0.52, 0.02, 0.07), (0, 0.11, 0.035), "gunmetal", 0.004) if False else None
    m.box((0.06, 0.012, 0.012), (0.2, -0.085, 0.07), "em_green")


@b("k_2")
def _(m, rng):
    m.box((0.9, 0.06, 0.05), (0, 0.25, 0.025), "hull_dark", 0.008) if False else None
    m.box((0.9, 0.42, 0.05), (0, 0, 0.025), "hull_dark", 0.015)
    m.box((0.9, 0.06, 0.05), (0, 0.24, 0.05), "brushed_alu", 0.006) if False else None
    for s in (-1, 1):
        x = s * 0.2
        m.cyl(0.16, 0.03, (x, -0.02, 0.06), "paint_white", axis="z", seg=24)
        m.torus(0.165, 0.014, (x, -0.02, 0.06), "chrome", axis="z", seg=24, tseg=6)
        for k in range(12):
            a = k * PI / 6
            m.box((0.008, 0.02, 0.006), (x + 0.13 * math.sin(a), -0.02 + 0.13 * math.cos(a), 0.078), "black_metal", rot=(0, 0, -a))
        ha, ma = (0.6, 2.6) if s < 0 else (3.6, 1.2)
        m.box((0.012, 0.09, 0.006), (x + 0.04 * math.sin(ha), -0.02 + 0.04 * math.cos(ha), 0.084), "black_metal", rot=(0, 0, -ha))
        m.box((0.008, 0.13, 0.006), (x + 0.06 * math.sin(ma), -0.02 + 0.06 * math.cos(ma), 0.09), "black_metal", rot=(0, 0, -ma))
        m.cyl(0.012, 0.012, (x, -0.02, 0.092), "gold_trim", axis="z", seg=8)
    m.box((0.2, 0.05, 0.01), (-0.2, 0.17, 0.052), "em_cyan")
    m.box((0.2, 0.05, 0.01), (0.2, 0.17, 0.052), "em_amber")
    m.box((0.04, 0.03, 0.01), (0, -0.02, 0.055), "em_green")


# --------------------------------------------------------------------------
# verify the 85 label total at import (cheap sanity, no output)
