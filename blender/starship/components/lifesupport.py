"""Life-support components: scrubbers, ducts, water tanks, planters, gas cylinders."""
import math

from ..kit import family, register_material

register_material("ls_wheat", "#c9a850", 0.0, 0.7)
register_material("ls_tomato", "#c8321f", 0.0, 0.45)
register_material("ls_pink", "#e05a9a", 0.0, 0.6)
register_material("ls_yellow", "#e8c81c", 0.0, 0.6)
register_material("ls_purple", "#7a45b8", 0.0, 0.6)
register_material("ls_orange", "#e07a1c", 0.0, 0.5)
register_material("ls_mush", "#c9b08a", 0.0, 0.7)
register_material("ls_dleaf", "#1f4d1f", 0.0, 0.7)
register_material("ls_tub", "#5a4a3a", 0.0, 0.8)
register_material("ls_o2", "#2c6fb3", 0.4, 0.4)
register_material("ls_n2", "#1c1c20", 0.4, 0.4)
register_material("ls_air", "#c9cfd6", 0.4, 0.35)
register_material("ls_filter", "#d8d2bd", 0.0, 0.95)


# ---------------------------------------------------------------- helpers
def lean(m, minsize=0.07):
    """Drop bevels on thin boxes (invisible, but they triple the triangle count)."""
    orig = m.box

    def box(size, pos=(0, 0, 0), mat="hull_mid", bevel=0.0, rot=(0, 0, 0)):
        if min(size) < minsize:
            bevel = 0.0
        return orig(size, pos, mat, bevel, rot)
    m.box = box


def gauge(m, x, y, z, r=0.05, col="em_green"):
    m.cyl(r * 1.2, 0.02, (x, y, z), "black_metal", axis="z", seg=12)
    m.cyl(r, 0.01, (x, y, z + 0.008), col, axis="z", seg=12)


def led(m, x, y, z, col="em_green", s=0.025):
    m.box((s, s, 0.012), (x, y, z), col)


def door(m, cx, cy, z, w, h, mat="hull_light", handle_side=1):
    m.box((w, h, 0.02), (cx, cy, z + 0.01), mat, 0.005)
    m.box((w - 0.04, h - 0.04, 0.008), (cx, cy, z + 0.022), "hull_mid", 0.002)
    m.box((0.03, min(0.16, h * 0.4), 0.035), (cx + handle_side * (w / 2 - 0.05), cy, z + 0.04), "black_metal", 0.005)
    for s in (-1, 1):
        m.cyl(0.012, 0.03, (cx - handle_side * (w / 2 - 0.01), cy + s * h * 0.35, z + 0.02), "steel", seg=6)


def slats(m, cx, cy, z, w, h, n, mat="black_metal", tilt=0.5):
    for k in range(n):
        y = cy - h / 2 + h * (k + 0.5) / n
        m.box((w, h / n * 0.5, 0.012), (cx, y, z), mat, rot=(-tilt, 0, 0))


def cabinet(m, w, h, d, mat="hull_light", plinth=0.08, y0=0.0):
    m.box((w - 0.04, plinth, d - 0.04), (0, y0 + plinth / 2, 0), "black_metal")
    m.box((w, h - plinth, d), (0, y0 + plinth + (h - plinth) / 2, 0), mat, 0.015)
    m.box((w + 0.02, 0.03, d + 0.02), (0, y0 + h - 0.015, 0), "hull_dark", 0.008)


def bolts(m, xs, ys, z, r=0.012):
    for x in xs:
        for y in ys:
            m.cyl(r, 0.01, (x, y, z), "steel", axis="z", seg=6)


def label_plate(m, x, y, z, w=0.16, col="em_cyan"):
    m.box((w, 0.05, 0.012), (x, y, z), "black_metal", 0.002)
    m.box((w - 0.03, 0.012, 0.014), (x, y, z), col)


def hazard(m, cx, cy, z, w, h=0.05):
    m.box((w, h, 0.008), (cx, cy, z), "hazard_yellow")
    n = int(w / 0.06)
    for k in range(n):
        m.box((0.02, h, 0.01), (cx - w / 2 + 0.04 + k * 0.06, cy, z + 0.002), "black_metal")


def pipe_h(m, y, z, x0, x1, r=0.035, mat="copper"):
    m.cyl(r, abs(x1 - x0), ((x0 + x1) / 2, y, z), mat, axis="x", seg=10)
    for x in (x0 + 0.06, x1 - 0.06):
        m.cyl(r * 1.35, 0.03, (x, y, z), "steel", axis="x", seg=10)


def flange_ring(m, pos, r, axis="x", mat="steel"):
    m.cyl(r * 1.25, 0.03, pos, mat, axis=axis, seg=12)
    ang = 6
    for k in range(ang):
        a = 2 * math.pi * k / ang
        if axis == "x":
            p = (pos[0], pos[1] + math.sin(a) * r * 1.12, pos[2] + math.cos(a) * r * 1.12)
            m.cyl(0.008, 0.04, p, "black_metal", axis="x", seg=5)
        elif axis == "z":
            p = (pos[0] + math.cos(a) * r * 1.12, pos[1] + math.sin(a) * r * 1.12, pos[2])
            m.cyl(0.008, 0.04, p, "black_metal", axis="z", seg=5)


# ================================================================ SCRUBBERS
SCRUB = ["CO2 Scrubber Tower", "Air Handler Unit", "Atmosphere Processor", "Humidity Control Unit",
         "Filter Bank Rack", "Twin Amine Scrubber", "UV Air Sterilizer", "Catalytic Converter",
         "HEPA Particulate Unit", "Sabatier Reactor"]


@family("scrubber", SCRUB, mount="floor", tags=["lifesupport", "atmosphere"], solid=True)
def scrubber(m, i, label, rng):
    lean(m)
    B[i](m, rng)


def s_tower(m, rng):
    cabinet(m, 0.8, 2.2, 0.7, "hull_light")
    m.box((0.6, 0.5, 0.02), (0, 1.75, 0.36), "hull_dark", 0.004)
    m.screen((0.5, 0.2), (0, 1.75, 0.375), "diagnostic", bezel=0.015)
    for s in (-1, 1):
        m.cyl(0.14, 1.0, (s * 0.2, 0.9, 0.36), "steel", seg=14)
        m.cyl(0.16, 0.05, (s * 0.2, 1.4, 0.36), "hull_dark", seg=14)
        m.cyl(0.16, 0.05, (s * 0.2, 0.42, 0.36), "hull_dark", seg=14)
        m.box((0.04, 0.6, 0.012), (s * 0.2, 0.9, 0.5), "glass_blue")
    gauge(m, -0.25, 1.55, 0.36, 0.05, "em_cyan")
    gauge(m, 0.25, 1.55, 0.36, 0.05, "em_amber")
    m.cyl(0.09, 0.3, (0, 2.35, 0), "steel", seg=12)
    flange_ring(m, (0, 2.24, 0), 0.09, "y") if False else m.cyl(0.11, 0.03, (0, 2.22, 0), "steel", seg=12)
    hazard(m, 0, 0.16, 0.355, 0.7)
    led(m, -0.32, 2.0, 0.36, "em_green")
    led(m, 0.32, 2.0, 0.36, "em_amber")
    bolts(m, (-0.36, 0.36), (0.3, 2.0), 0.355)


def s_air_handler(m, rng):
    m.box((2.0, 0.9, 0.8), (0, 0.55, 0), "hull_mid", 0.02)
    for x in (-0.9, 0.9):
        m.box((0.12, 0.1, 0.7), (x, 0.05, 0), "black_metal")
    m.box((1.9, 0.06, 0.7), (0, 1.03, 0), "hull_dark", 0.01)
    # fan grille
    m.cyl(0.32, 0.03, (-0.5, 0.6, 0.41), "black_metal", axis="z", seg=20)
    for r in (0.08, 0.16, 0.24):
        m.torus(r, 0.008, (-0.5, 0.6, 0.43), "steel", axis="z", seg=16, tseg=4)
    for k in range(4):
        m.box((0.6, 0.012, 0.012), (-0.5, 0.6, 0.435), "steel", rot=(0, 0, k * math.pi / 4))
    m.cyl(0.05, 0.03, (-0.5, 0.6, 0.44), "hull_dark", axis="z", seg=8)
    door(m, 0.4, 0.55, 0.4, 0.9, 0.7, "hull_light")
    gauge(m, 0.75, 0.85, 0.42, 0.04, "em_cyan")
    led(m, 0.15, 0.85, 0.42, "em_green")
    # ducts on top
    m.box((0.5, 0.35, 0.5), (-0.5, 1.26, 0), "steel", 0.01)
    m.cyl(0.2, 0.5, (0.55, 1.25, 0), "brushed_alu", axis="y", seg=16)
    m.box((0.5, 0.3, 0.3), (0.55, 1.65, 0), "steel", 0.01)
    flange_ring(m, (1.0, 0.55, 0), 0.17, "x")
    m.cyl(0.17, 0.2, (1.1, 0.55, 0), "brushed_alu", axis="x", seg=14)


def s_atmo(m, rng):
    m.box((1.4, 0.15, 1.0), (0, 0.075, 0), "hull_dark", 0.01)
    for x in (-0.6, 0.6):
        m.box((0.1, 1.8, 0.1), (x, 1.05, -0.35), "hull_mid", 0.01)
        m.box((0.1, 1.8, 0.1), (x, 1.05, 0.35), "hull_mid", 0.01)
    m.box((1.3, 0.1, 0.9), (0, 1.95, 0), "hull_mid", 0.01)
    m.cyl(0.4, 1.5, (0, 1.05, 0), "glass", seg=20, cap=False)
    m.cyl(0.42, 0.06, (0, 0.3, 0), "steel", seg=20)
    m.cyl(0.42, 0.06, (0, 1.8, 0), "steel", seg=20)
    m.cyl(0.18, 1.5, (0, 1.05, 0), "em_cyan", seg=12)
    for k in range(5):
        m.torus(0.28, 0.02, (0, 0.5 + k * 0.28, 0), "chrome", seg=16, tseg=5)
    m.cyl(0.08, 0.2, (0, 2.1, 0), "steel", seg=10)
    pipe_h(m, 0.5, 0.0, 0.42, 0.85, 0.05, "copper")
    pipe_h(m, 1.6, 0.0, -0.85, -0.42, 0.05, "steel")
    m.box((0.5, 0.35, 0.3), (0.0, 0.35, 0.3), "hull_light", 0.01)
    m.screen((0.38, 0.2), (0.0, 0.36, 0.455), "diagnostic", bezel=0.01)
    gauge(m, 0.65, 1.3, 0.4, 0.06, "em_amber")


def s_humidity(m, rng):
    cabinet(m, 0.9, 1.5, 0.6, "hull_light")
    m.box((0.7, 0.5, 0.02), (0, 1.0, 0.31), "hull_dark", 0.004)
    m.box((0.6, 0.4, 0.012), (0, 1.0, 0.325), "glass_blue")
    m.box((0.5, 0.14, 0.01), (0, 0.9, 0.33), "water")  # water window
    m.box((0.36, 0.1, 0.4), (0, 0.16, 0.3), "steel", 0.008)  # drip tray
    m.box((0.32, 0.03, 0.36), (0, 0.19, 0.3), "water")
    slats(m, 0, 1.4, 0.31, 0.7, 0.08, 4, tilt=0.6)
    m.screen((0.22, 0.1), (0.28, 0.65, 0.31), "bars", bezel=0.008)
    m.cyl(0.06, 0.1, (-0.28, 0.65, 0.34), "steel", axis="z", seg=10)  # knob
    m.cyl(0.03, 0.03, (-0.28, 0.65, 0.4), "plastic_black", axis="z", seg=8)
    led(m, 0.35, 0.45, 0.31, "em_cyan")
    m.tube([(0.4, 1.3, -0.2), (0.6, 1.3, -0.2), (0.6, 0.3, -0.2)], 0.025, "copper")


def s_filter_bank(m, rng):
    m.box((1.9, 0.1, 0.7), (0, 0.05, 0), "hull_dark", 0.01)
    for x in (-0.92, 0.92):
        m.box((0.08, 1.7, 0.7), (x, 0.95, 0), "hull_mid", 0.01)
    m.box((1.9, 0.08, 0.7), (0, 1.84, 0), "hull_mid", 0.01)
    m.box((1.76, 1.7, 0.5), (0, 0.95, -0.05), "black_metal")
    for r in range(3):
        for c in range(4):
            x = -0.66 + c * 0.44
            y = 0.35 + r * 0.55
            m.box((0.4, 0.5, 0.16), (x, y, 0.2), "ls_filter", 0.006)
            for k in range(3):
                m.box((0.02, 0.44, 0.04), (x - 0.1 + k * 0.1, y, 0.3), "foam")
            m.box((0.3, 0.03, 0.03), (x, y + 0.27, 0.3), "steel")
            led(m, x + 0.17, y - 0.24, 0.29, "em_green" if (r + c) % 3 else "em_amber", 0.02)
    m.box((0.6, 0.12, 0.02), (0, 1.75, 0.36), "hull_dark")
    m.screen((0.5, 0.08), (0, 1.75, 0.375), "bars")


def s_twin_amine(m, rng):
    m.box((1.8, 0.12, 0.9), (0, 0.06, 0), "hull_dark", 0.01)
    for s in (-1, 1):
        x = s * 0.55
        m.cyl(0.3, 1.9, (x, 1.07, 0), "paint_teal" if s < 0 else "paint_blue", seg=20)
        m.cyl(0.3, 0.02, (x, 1.75, 0.0), "black_metal", seg=20)
        m.cyl(0.24, 0.16, (x, 2.1, 0), "steel", seg=16, r2=0.12)
        m.torus(0.3, 0.02, (x, 0.5, 0), "steel", seg=20, tseg=5)
        m.torus(0.3, 0.02, (x, 1.4, 0), "steel", seg=20, tseg=5)
        m.box((0.05, 0.9, 0.012), (x, 1.05, 0.3), "glass_green")
        gauge(m, x, 1.65, 0.3, 0.05, "em_cyan")
    m.tube([(-0.55, 2.2, 0), (-0.55, 2.4, 0), (0.55, 2.4, 0), (0.55, 2.2, 0)], 0.045, "steel")
    m.tube([(-0.3, 0.3, 0.2), (0, 0.3, 0.45), (0.3, 0.3, 0.2)], 0.04, "copper")
    m.box((0.36, 0.4, 0.2), (0, 0.32, -0.2), "hull_mid", 0.01)
    label_plate(m, 0, 0.65, 0.31, 0.2, "em_amber")
    hazard(m, 0, 0.16, 0.455, 1.6)


def s_uv(m, rng):
    cabinet(m, 0.7, 1.7, 0.6, "hull_mid")
    m.box((0.5, 1.1, 0.02), (0, 1.0, 0.31), "black_metal", 0.004)
    m.box((0.46, 1.06, 0.014), (0, 1.0, 0.325), "glass_dark")
    for k in range(4):
        m.cyl(0.02, 1.0, (-0.15 + k * 0.1, 1.0, 0.3), "em_violet", seg=6)
    m.box((0.5, 0.1, 0.04), (0, 1.58, 0.31), "hull_dark", 0.004)
    m.box((0.5, 0.1, 0.04), (0, 0.44, 0.31), "hull_dark", 0.004)
    m.box((0.6, 0.06, 0.02), (0, 0.3, 0.31), "hazard_yellow")
    m.cyl(0.07, 0.2, (0, 1.8, 0), "steel", seg=12)
    m.cyl(0.07, 0.3, (0.0, 0.25, -0.45), "steel", axis="z", seg=12)
    led(m, 0.28, 1.6, 0.31, "em_violet")
    m.cyl(0.03, 0.03, (-0.28, 1.6, 0.32), "paint_red", axis="z", seg=8)


def s_catalytic(m, rng):
    for x in (-0.6, 0.6):
        m.box((0.12, 0.7, 0.7), (x, 0.35, 0), "hull_dark", 0.01)
        m.box((0.3, 0.06, 0.5), (x, 0.03, 0), "black_metal")
    m.cyl(0.42, 1.6, (0, 0.8, 0), "gunmetal", axis="x", seg=20)
    for x in (-0.5, 0, 0.5):
        m.torus(0.42, 0.025, (x, 0.8, 0), "steel", axis="x", seg=20, tseg=5)
    m.cyl(0.42, 0.06, (0.85, 0.8, 0), "steel", axis="x", seg=20, r2=0.3)
    m.cyl(0.42, 0.06, (-0.85, 0.8, 0), "steel", axis="x", seg=20, r2=0.3)
    hz = 0.0
    m.cyl(0.43, 0.2, (0.3, 0.8, 0), "hazard_yellow", axis="x", seg=20)
    m.cyl(0.14, 0.2, (0, 1.32, 0), "steel", seg=12)
    m.cyl(0.05, 0.2, (0.0, 1.55, 0), "black_metal", seg=8)
    m.box((0.36, 0.22, 0.03), (-0.4, 0.8, 0.43), "hull_light", 0.005, rot=(0.4, 0, 0))
    m.box((0.24, 0.12, 0.012), (-0.4, 0.8, 0.455), "em_orange", rot=(0.4, 0, 0))
    gauge(m, 0.0, 1.05, 0.33, 0.05, "em_amber")
    pipe_h(m, 0.8, 0, 0.9, 1.2, 0.07, "steel")
    pipe_h(m, 0.8, 0, -1.2, -0.9, 0.07, "steel")


def s_hepa(m, rng):
    m.box((1.5, 0.12, 0.7), (0, 0.06, 0), "black_metal", 0.008)
    m.box((1.5, 0.7, 0.7), (0, 0.47, 0), "hull_light", 0.02)
    m.box((1.3, 0.5, 0.05), (0, 0.47, 0.34), "hull_dark", 0.005)
    for k in range(28):
        m.box((0.02, 0.44, 0.06), (-0.63 + k * 0.0467, 0.47, 0.36), "ls_filter", rot=(0, 0, 0))
    m.box((1.5, 0.08, 0.74), (0, 0.86, 0), "hull_dark", 0.01)
    m.cyl(0.14, 0.15, (-0.5, 0.97, 0), "steel", seg=14)
    m.cyl(0.14, 0.15, (0.5, 0.97, 0), "steel", seg=14)
    for x in (-0.5, 0.5):
        m.cyl(0.12, 0.03, (x, 1.06, 0), "black_metal", seg=14)
        for k in range(3):
            m.box((0.22, 0.01, 0.02), (x, 1.07, 0), "steel", rot=(0, k * 1.05, 0))
    led(m, 0.68, 0.7, 0.36, "em_cyan")
    led(m, 0.68, 0.64, 0.36, "em_green")
    m.screen((0.18, 0.08), (0.62, 0.22, 0.36), "bars", bezel=0.008)
    m.cyl(0.035, 0.03, (-0.68, 0.2, 0.37), "steel", axis="z", seg=8)


def s_sabatier(m, rng):
    m.box((1.2, 0.14, 1.0), (0, 0.07, 0), "hull_dark", 0.01)
    m.cyl(0.32, 1.7, (0, 1.0, -0.1), "gunmetal", seg=20)
    m.sphere(0.32, (0, 1.85, -0.1), "gunmetal", seg=20, ring=6, scale=(1, 0.5, 1))
    for k in range(9):
        m.cyl(0.4, 0.018, (0, 0.4 + k * 0.14, -0.1), "copper", seg=20)
    m.tube([(0.32, 0.5, -0.1), (0.5, 0.5, -0.1), (0.5, 1.2, 0.2), (0.5, 1.2, 0.4)], 0.035, "steel")
    m.tube([(-0.32, 1.6, -0.1), (-0.5, 1.6, -0.1), (-0.5, 0.35, 0.3)], 0.035, "copper")
    m.box((0.4, 0.55, 0.3), (0.3, 0.42, 0.35), "hull_mid", 0.01)
    m.screen((0.3, 0.16), (0.3, 0.5, 0.505), "power", bezel=0.01)
    gauge(m, 0.2, 0.28, 0.51, 0.04, "em_amber")
    gauge(m, 0.4, 0.28, 0.51, 0.04, "em_green")
    m.cyl(0.05, 0.2, (0, 2.05, -0.1), "steel", seg=10)
    m.box((0.06, 0.06, 0.06), (0.32, 1.1, 0.15), "paint_red")  # relief valve
    m.box((0.05, 0.9, 0.012), (0, 1.0, 0.22), "em_orange")


B = [s_tower, s_air_handler, s_atmo, s_humidity, s_filter_bank, s_twin_amine, s_uv, s_catalytic, s_hepa, s_sabatier]


# ================================================================ DUCTS
def duct_flanges(m, xs, y, z, w, h):
    for x in xs:
        m.box((0.05, h + 0.08, w + 0.08), (x, y, z), "steel", 0.006)


def bracket(m, x, y, z, h=0.3):
    m.box((0.05, 0.05, z), (x, y, z / 2), "black_metal")


WALL_DUCT = ["Rectangular Duct Run", "Round Duct Run", "Flex Duct Hose", "Rectangular Elbow",
             "Round Elbow Duct", "Tee Junction Duct", "Plenum Damper Box", "Louvered Wall Grille",
             "Return Air Grille", "Emergency Shutter Vent"]


@family("duct", WALL_DUCT, mount="wall", tags=["lifesupport", "hvac"], solid=False, mount_y=2.3)
def duct_wall(m, i, label, rng):
    lean(m)
    D[i](m, rng)


def d_rect(m, rng):
    W, H, Z = 2.0, 0.4, 0.3
    m.box((W, H, Z), (0, 0, 0.05 + Z / 2), "brushed_alu", 0.012)
    for x in (-0.99, -0.33, 0.33, 0.99):
        m.box((0.05, H + 0.08, Z + 0.08), (x, 0, 0.05 + Z / 2), "steel", 0.006)
    for x in (-0.66, 0.66):
        m.box((0.06, 0.04, 0.05), (x, 0, 0.025), "black_metal")
    m.box((0.5, 0.3, 0.02), (0, 0, 0.37), "hull_mid", 0.004)
    m.box((0.4, 0.08, 0.012), (0, 0.06, 0.385), "hazard_yellow")
    label_plate(m, -0.66, -0.05, 0.365, 0.16, "em_cyan")


def d_round(m, rng):
    m.cyl(0.2, 2.0, (0, 0, 0.25), "brushed_alu", axis="x", seg=18)
    for x in (-0.95, -0.5, 0.0, 0.5, 0.95):
        m.cyl(0.215, 0.05, (x, 0, 0.25), "steel", axis="x", seg=18)
    for x in (-0.25, 0.75):
        m.box((0.05, 0.04, 0.06), (x, 0, 0.03), "black_metal")
        m.box((0.05, 0.14, 0.04), (x, -0.0, 0.05), "black_metal")
        m.box((0.04, 0.04, 0.2), (x, 0, 0.1), "black_metal")
    m.cyl(0.05, 0.05, (0.5, 0.2, 0.25), "black_metal", seg=8)  # damper spindle
    m.box((0.14, 0.02, 0.02), (0.5, 0.235, 0.25), "paint_orange")


def d_flex(m, rng):
    pts = [(-1.0, 0, 0.3), (-0.6, 0.0, 0.3), (-0.3, -0.25, 0.3), (0.2, -0.3, 0.3), (0.55, 0.0, 0.3), (1.0, 0.0, 0.3)]
    for a, b in zip(pts[:-1], pts[1:]):
        m.link(a, b, 0.14, "plastic_grey", seg=12)
        L = math.dist(a, b)
        n = int(L / 0.06)
        for k in range(n):
            t = (k + 0.5) / n
            p = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
    for p in pts[1:-1]:
        m.sphere(0.145, p, "plastic_grey", seg=10, ring=6)
    for x in (-1.0, 1.0):
        m.cyl(0.19, 0.12, (x, 0, 0.3), "steel", axis="x", seg=14)
        m.cyl(0.155, 0.05, (x, 0, 0.3), "black_metal", axis="x", seg=14)
        m.cyl(0.195, 0.02, (x * 0.94, 0, 0.3), "paint_orange", axis="x", seg=14)
    for x in (-0.9, -0.45, 0.0, 0.4, 0.75):
        y = -0.3 if 0 < x < 0.5 else 0
    m.box((0.03, 0.03, 0.3), (0.2, 0.3, 0.15), "steel")


def d_elbow_rect(m, rng):
    Z = 0.3
    m.box((1.0, 0.4, Z), (-0.5 + 0.2, 0, 0.2 + Z / 2), "brushed_alu", 0.012)
    m.box((0.4, 1.3, Z), (0.5, -0.45, 0.2 + Z / 2), "brushed_alu", 0.012)
    m.box((0.05, 0.48, Z + 0.08), (-0.3, 0, 0.35), "steel", 0.006)
    m.box((0.48, 0.05, Z + 0.08), (0.5, -1.1, 0.35), "steel", 0.006)
    m.box((0.5, 0.46, Z + 0.02), (0.5, 0.0, 0.35), "brushed_alu", 0.02)
    # turning vanes hint
    m.box((0.02, 0.44, 0.02), (0.5, 0, 0.51), "steel", rot=(0, 0, 0.78))
    m.box((0.05, 0.05, 0.2), (-0.3, 0.0, 0.1), "black_metal")
    m.box((0.05, 0.05, 0.2), (0.5, -0.8, 0.1), "black_metal")
    m.box((0.14, 0.03, 0.012), (0.5, -0.6, 0.52), "em_cyan")


def d_elbow_round(m, rng):
    m.torus(0.5, 0.18, (-0.5, -0.5, 0.35), "brushed_alu", axis="z", seg=12, tseg=12, arc=math.pi / 2, rot=(0, 0, 0))
    m.cyl(0.18, 0.7, (-0.85, 0.0, 0.35), "brushed_alu", axis="x", seg=14)
    m.cyl(0.18, 0.7, (0.0, -0.85, 0.35), "brushed_alu", axis="y", seg=14)
    for p, ax in (((-1.1, 0, 0.35), "x"), ((0, -1.1, 0.35), "y"), ((-0.5, 0.0, 0.35), "x")):
        m.cyl(0.2, 0.05, p, "steel", axis=ax, seg=14)
    for p in ((-0.85, 0, 0), (0, -0.85, 0)):
        m.box((0.05, 0.05, 0.16), (p[0], p[1], 0.09), "black_metal")
    led(m, -0.8, 0.0, 0.54, "em_green", 0.03)


def d_tee(m, rng):
    m.box((2.0, 0.36, 0.3), (0, 0, 0.35), "brushed_alu", 0.012)
    m.box((0.36, 0.9, 0.3), (0, -0.63, 0.35), "brushed_alu", 0.012)
    for x in (-0.95, 0.95):
        m.box((0.05, 0.44, 0.38), (x, 0, 0.35), "steel", 0.006)
    m.box((0.44, 0.05, 0.38), (0, -1.05, 0.35), "steel", 0.006)
    m.box((0.48, 0.04, 0.34), (0, -0.2, 0.35), "steel", 0.006)
    m.box((0.06, 0.04, 0.2), (0, 0, 0.1), "black_metal")
    for x in (-0.6, 0.6):
        m.box((0.05, 0.05, 0.2), (x, 0.0, 0.1), "black_metal")
    m.box((0.05, 0.05, 0.2), (0, -0.9, 0.1), "black_metal")
    m.box((0.12, 0.12, 0.05), (0, 0.0, 0.52), "paint_orange", 0.005)  # damper actuator
    m.cyl(0.03, 0.08, (0, 0.0, 0.48), "steel", axis="z", seg=8)
    m.box((0.14, 0.03, 0.012), (0, -0.7, 0.51), "em_cyan")
    m.box((0.14, 0.03, 0.012), (0.6, 0.0, 0.51), "em_green")


def d_plenum(m, rng):
    m.box((1.2, 0.8, 0.6), (0, 0, 0.3 + 0.05), "hull_mid", 0.02)
    m.box((1.3, 0.05, 0.7), (0, 0.42, 0.4), "hull_dark", 0.01)
    m.box((1.3, 0.05, 0.7), (0, -0.42, 0.4), "hull_dark", 0.01)
    for k in range(3):
        x = -0.35 + k * 0.35
        m.box((0.28, 0.5, 0.03), (x, 0.0, 0.67), "black_metal", 0.004)
        for j in range(5):
            m.box((0.26, 0.03, 0.02), (x, -0.2 + j * 0.1, 0.685), "steel", rot=(0.5, 0, 0))
        m.box((0.08, 0.06, 0.06), (x, 0.32, 0.7), "paint_orange", 0.004)  # actuator
    m.cyl(0.18, 0.4, (-0.8, 0, 0.35), "brushed_alu", axis="x", seg=14)
    m.cyl(0.18, 0.4, (0.8, 0, 0.35), "brushed_alu", axis="x", seg=14)
    for x in (-0.62, 0.62):
        m.cyl(0.2, 0.04, (x, 0, 0.35), "steel", axis="x", seg=14)
    for x in (-0.4, 0.4):
        m.box((0.05, 0.05, 0.3), (x, 0.0, 0.1), "black_metal")


def d_wall_grille(m, rng):
    m.box((0.9, 0.6, 0.06), (0, 0, 0.03), "plastic_white", 0.012)
    m.box((0.8, 0.5, 0.02), (0, 0, 0.07), "black_metal", 0.004)
    for k in range(9):
        m.box((0.78, 0.035, 0.03), (0, -0.22 + k * 0.055, 0.08), "hull_light", rot=(-0.6, 0, 0))
    bolts(m, (-0.4, 0.4), (-0.26, 0.26), 0.063)


def d_return(m, rng):
    m.box((0.5, 1.0, 0.05), (0, 0, 0.025), "hull_light", 0.01)
    m.box((0.4, 0.9, 0.02), (0, 0, 0.055), "black_metal", 0.004)
    for k in range(3):
        for j in range(12):
            m.box((0.08, 0.05, 0.02), (-0.13 + k * 0.13, -0.42 + j * 0.077, 0.075), "steel")
    bolts(m, (-0.21, 0.21), (-0.45, 0.45), 0.052, 0.01)


def d_shutter(m, rng):
    m.box((0.8, 0.8, 0.14), (0, 0, 0.07), "hull_dark", 0.015)
    m.box((0.62, 0.62, 0.05), (0, 0, 0.14), "black_metal", 0.005)
    m.box((0.56, 0.56, 0.02), (0, 0, 0.17), "hull_mid", 0.004)
    for k in range(4):
        m.box((0.54, 0.09, 0.02), (0, -0.21 + k * 0.14, 0.19), "steel", 0.003, rot=(-0.15, 0, 0))
    hazard(m, 0, 0.36, 0.145, 0.7, 0.05)
    hazard(m, 0, -0.36, 0.145, 0.7, 0.05)
    m.box((0.14, 0.14, 0.06), (0.5, 0.0, 0.1), "paint_red", 0.006)
    m.box((0.1, 0.03, 0.03), (0.5, 0.0, 0.14), "em_red")
    m.cyl(0.05, 0.08, (-0.5, 0.0, 0.1), "paint_red", axis="z", seg=8)
    led(m, -0.5, -0.2, 0.15, "em_red")


D = [d_rect, d_round, d_flex, d_elbow_rect, d_elbow_round, d_tee, d_plenum, d_wall_grille, d_return, d_shutter]

CEIL_DUCT = ["Ceiling Square Diffuser", "Ceiling Round Vent"]


@family("duct", CEIL_DUCT, mount="ceiling", tags=["lifesupport", "hvac"], solid=False)
def duct_ceiling(m, i, label, rng):
    lean(m)
    if i == 0:
        m.box((0.7, 0.03, 0.7), (0, -0.015, 0), "plastic_white", 0.006)
        for s in range(4):
            r = 0.06 + s * 0.07
        for k in range(4):
            sz = 0.62 - k * 0.15
            m.box((sz, 0.05, 0.03), (0, -0.05 - k * 0.012, sz / 2), "hull_light", 0.003)
            m.box((sz, 0.05, 0.03), (0, -0.05 - k * 0.012, -sz / 2), "hull_light", 0.003)
            m.box((0.03, 0.05, sz), (sz / 2, -0.05 - k * 0.012, 0), "hull_light", 0.003)
            m.box((0.03, 0.05, sz), (-sz / 2, -0.05 - k * 0.012, 0), "hull_light", 0.003)
        m.box((0.14, 0.09, 0.14), (0, -0.075, 0), "hull_mid", 0.004)
        m.box((0.4, 0.008, 0.02), (0, -0.032, 0.34), "em_white")
    else:
        m.cyl(0.27, 0.04, (0, -0.02, 0), "plastic_white", seg=20)
        m.cyl(0.2, 0.06, (0, -0.06, 0), "hull_light", seg=20, r2=0.14)
        m.cyl(0.13, 0.08, (0, -0.1, 0), "hull_mid", seg=20, r2=0.07)
        m.torus(0.28, 0.012, (0, -0.045, 0), "steel", seg=20, tseg=5)
        for k in range(8):
            a = k * math.pi / 4
            m.box((0.012, 0.012, 0.13), (math.cos(a) * 0.14, -0.05, math.sin(a) * 0.14), "black_metal", rot=(0, -a + math.pi / 2, 0))
        m.cyl(0.03, 0.02, (0, -0.15, 0), "em_cyan", seg=8)


# ================================================================ WATER TANKS
WATER = ["Water Recycler", "Potable Water Tank", "Greywater Processor", "Condensate Collector",
         "Water Heater", "UV Water Purifier", "Reverse Osmosis Skid", "Distillation Column"]


@family("watertank", WATER, mount="floor", tags=["lifesupport", "water"], solid=True)
def watertank(m, i, label, rng):
    lean(m)
    W[i](m, rng)


def w_recycler(m, rng):
    cabinet(m, 1.2, 2.0, 0.8, "hull_light")
    m.box((0.5, 0.9, 0.02), (-0.28, 1.0, 0.41), "black_metal", 0.004)
    m.box((0.46, 0.86, 0.012), (-0.28, 1.0, 0.425), "glass_blue")
    m.box((0.4, 0.3, 0.01), (-0.28, 0.75, 0.43), "water")
    m.box((0.4, 0.3, 0.01), (-0.28, 1.15, 0.43), "glass_green")
    m.screen((0.42, 0.4), (0.3, 1.35, 0.41), "diagnostic", bezel=0.015)
    gauge(m, 0.15, 0.7, 0.41, 0.05, "em_cyan")
    gauge(m, 0.4, 0.7, 0.41, 0.05, "em_green")
    m.cyl(0.05, 0.4, (0.4, 0.3, 0.41), "chrome", axis="z", seg=8)  # spigot
    m.box((0.3, 0.05, 0.22), (0.4, 0.15, 0.5), "steel", 0.005)
    m.tube([(-0.5, 2.0, -0.2), (-0.5, 2.3, -0.2), (0.3, 2.3, -0.2)], 0.04, "steel")
    hazard(m, 0, 0.16, 0.405, 1.1)


def w_potable(m, rng):
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        m.box((0.08, 0.5, 0.08), (math.cos(a) * 0.42, 0.25, math.sin(a) * 0.42), "hull_dark", 0.006)
    m.cyl(0.55, 1.5, (0, 1.05, 0), "brushed_alu", seg=24)
    m.sphere(0.55, (0, 1.8, 0), "brushed_alu", seg=24, ring=6, scale=(1, 0.35, 1))
    for y in (0.6, 1.05, 1.5):
        m.torus(0.55, 0.018, (0, y, 0), "steel", seg=24, tseg=5)
    m.box((0.08, 1.1, 0.02), (0, 1.05, 0.55), "glass_blue")
    m.box((0.05, 0.6, 0.02), (0, 0.85, 0.56), "water")
    for y in (0.55, 1.05, 1.55):
        m.box((0.14, 0.02, 0.03), (0.09, y, 0.56), "steel")
    m.cyl(0.14, 0.06, (0, 2.0, 0), "steel", seg=12)
    pipe_h(m, 0.5, 0.0, 0.5, 0.95, 0.045, "steel")
    m.cyl(0.07, 0.05, (0.8, 0.62, 0.0), "paint_blue", seg=8)  # valve wheel
    m.box((0.22, 0.1, 0.02), (-0.25, 0.55, 0.53), "paint_blue")
    m.box((0.2, 0.05, 0.012), (-0.25, 0.55, 0.545), "em_cyan")


def w_greywater(m, rng):
    m.box((1.6, 0.1, 0.9), (0, 0.05, 0), "hull_dark", 0.01)
    for k in range(3):
        x = -0.5 + k * 0.5
        m.box((0.42, 1.1, 0.42), (x, 0.65, -0.1), ["paint_grey", "hull_mid", "paint_teal"][k], 0.02)
        m.box((0.44, 0.06, 0.44), (x, 1.22, -0.1), "hull_dark", 0.01)
        m.box((0.1, 0.5, 0.012), (x, 0.7, 0.115), "glass_amber" if k == 0 else "glass_blue")
        m.cyl(0.05, 0.1, (x, 1.32, -0.1), "steel", seg=8)
    m.tube([(-0.5, 1.38, -0.1), (-0.5, 1.5, -0.1), (0.5, 1.5, -0.1), (0.5, 1.38, -0.1)], 0.03, "steel")
    m.box((1.4, 0.3, 0.2), (0, 0.28, 0.3), "hull_light", 0.01)
    m.screen((0.5, 0.16), (-0.3, 0.28, 0.405), "vitals", bezel=0.01)
    led(m, 0.1, 0.3, 0.405, "em_green")
    led(m, 0.2, 0.3, 0.405, "em_amber")
    hazard(m, 0.5, 0.28, 0.405, 0.4, 0.06)
    m.cyl(0.06, 0.4, (0.75, 0.55, 0.25), "steel", axis="y", seg=8)


def w_condensate(m, rng):
    m.box((0.9, 0.75, 0.7), (0, 0.42, 0), "hull_mid", 0.02)
    m.box((0.9, 0.1, 0.7), (0, 0.85, 0), "hull_dark", 0.01)
    m.box((0.5, 0.35, 0.02), (0, 0.5, 0.36), "black_metal", 0.004)
    m.box((0.46, 0.3, 0.014), (0, 0.5, 0.372), "glass_blue")
    m.box((0.42, 0.18, 0.01), (0, 0.44, 0.38), "water")
    for x in (-0.38, 0.38):
        m.box((0.06, 0.06, 0.06), (x, 0.04, 0.28), "black_metal")
        m.box((0.06, 0.06, 0.06), (x, 0.04, -0.28), "black_metal")
    # intake funnel + pipe
    m.cyl(0.36, 0.25, (0, 1.05, 0), "brushed_alu", seg=16, r2=0.12)
    m.cyl(0.12, 0.3, (0, 1.32, 0), "steel", seg=12)
    m.tube([(0, 1.45, 0), (0, 1.7, 0), (0.6, 1.7, 0), (0.6, 1.9, 0)], 0.045, "steel")
    m.cyl(0.05, 0.14, (0.0, 0.2, 0.42), "chrome", axis="z", seg=8)
    gauge(m, -0.25, 0.7, 0.36, 0.04, "em_cyan")
    led(m, 0.28, 0.7, 0.36, "em_cyan")


def w_heater(m, rng):
    m.cyl(0.35, 0.05, (0, 0.03, 0), "black_metal", seg=20)
    m.cyl(0.33, 1.4, (0, 0.78, 0), "paint_white", seg=20)
    m.sphere(0.33, (0, 1.48, 0), "paint_white", seg=20, ring=6, scale=(1, 0.3, 1))
    m.torus(0.33, 0.012, (0, 0.5, 0), "steel", seg=20, tseg=4)
    m.torus(0.33, 0.012, (0, 1.2, 0), "steel", seg=20, tseg=4)
    m.box((0.3, 0.32, 0.12), (0, 1.0, 0.33), "hull_dark", 0.01)
    m.screen((0.22, 0.14), (0, 1.03, 0.395), "power", bezel=0.008)
    m.cyl(0.04, 0.03, (-0.08, 0.9, 0.4), "steel", axis="z", seg=8)
    m.cyl(0.04, 0.03, (0.08, 0.9, 0.4), "paint_red", axis="z", seg=8)
    m.cyl(0.04, 0.5, (-0.15, 1.75, 0), "copper", seg=8)
    m.cyl(0.04, 0.5, (0.15, 1.75, 0), "steel", seg=8)
    m.tube([(-0.15, 2.0, 0), (-0.15, 2.1, 0), (-0.6, 2.1, 0)], 0.04, "copper")
    m.tube([(0.15, 2.0, 0), (0.15, 2.2, 0), (0.6, 2.2, 0)], 0.04, "steel")
    m.box((0.1, 0.1, 0.16), (0.3, 0.3, 0.2), "paint_red", 0.006)
    m.cyl(0.03, 0.2, (0.3, 0.2, 0.36), "steel", axis="y", seg=6)
    m.box((0.06, 0.06, 0.06), (-0.26, 1.3, 0.22), "em_orange", rot=(0, 0.8, 0))


def w_uv(m, rng):
    m.box((0.5, 1.5, 0.4), (0, 0.85, 0), "hull_dark", 0.015)
    for y in (0.15, 0.4):
        pass
    m.box((0.44, 0.06, 0.34), (0, 0.13, 0), "black_metal")
    m.cyl(0.13, 1.3, (0, 0.9, 0.22), "glass", axis="y", seg=14)
    m.cyl(0.04, 1.3, (0, 0.9, 0.22), "em_violet", axis="y", seg=8)
    for y in (0.24, 1.56):
        m.cyl(0.15, 0.06, (0, y, 0.22), "steel", seg=14)
    m.cyl(0.05, 0.3, (-0.3, 0.4, 0.0), "steel", axis="x", seg=8)
    m.cyl(0.05, 0.3, (0.3, 1.5, 0.0), "steel", axis="x", seg=8)
    m.box((0.06, 0.06, 0.03), (0.15, 1.7, 0.2), "em_violet")
    m.box((0.06, 0.06, 0.03), (-0.15, 1.7, 0.2), "em_green")
    m.cyl(0.14, 0.06, (0, 0.03, 0.22), "black_metal", seg=14)


def w_ro(m, rng):
    m.box((0.06, 1.5, 0.06), (-0.85, 0.75, 0), "hull_mid")
    m.box((0.06, 1.5, 0.06), (0.85, 0.75, 0), "hull_mid")
    m.box((1.8, 0.06, 0.6), (0, 0.06, 0), "hull_dark", 0.008)
    m.box((1.8, 0.06, 0.6), (0, 1.0, 0), "hull_dark", 0.008)
    m.box((1.8, 0.06, 0.6), (0, 1.5, 0), "hull_mid", 0.008)
    for k in range(4):
        y = 0.25 + k * 0.2
        m.cyl(0.08, 1.4, (0.0, 0.25 + k * 0.2, 0.0), "paint_white", axis="x", seg=12)
        for x in (-0.68, 0.68):
            m.cyl(0.09, 0.08, (x, y, 0), "steel", axis="x", seg=12)
    m.box((0.5, 0.3, 0.3), (-0.5, 1.25, 0), "paint_blue", 0.02)
    m.cyl(0.13, 0.36, (0.4, 1.25, 0), "chrome", axis="x", seg=14)
    gauge(m, -0.5, 1.25, 0.16, 0.06, "em_cyan")
    m.box((0.2, 0.05, 0.012), (0.4, 1.0, 0.31), "em_cyan")


def w_distill(m, rng):
    m.box((1.0, 0.12, 1.0), (0, 0.06, 0), "hull_dark", 0.01)
    m.cyl(0.3, 0.7, (0, 0.47, 0), "copper", seg=18, r2=0.24)
    m.cyl(0.22, 1.5, (0, 1.55, 0), "brushed_alu", seg=18)
    for k in range(6):
        m.torus(0.22, 0.015, (0, 1.0 + k * 0.25, 0), "steel", seg=18, tseg=5)
    m.sphere(0.24, (0, 2.32, 0), "copper", seg=16, ring=6, scale=(1, 0.7, 1))
    m.tube([(0, 2.45, 0), (0, 2.6, 0), (0.5, 2.6, 0), (0.5, 0.55, 0)], 0.045, "copper")
    m.cyl(0.14, 0.7, (0.5, 1.0, 0.0), "steel", seg=12)
    m.box((0.08, 0.5, 0.012), (0, 1.55, 0.225), "glass_blue")
    m.box((0.36, 0.25, 0.04), (0, 0.4, 0.33), "hull_mid", 0.006)
    m.screen((0.28, 0.16), (0, 0.4, 0.355), "text", bezel=0.008)
    gauge(m, -0.3, 0.9, 0.29, 0.05, "em_amber")
    m.box((0.1, 0.1, 0.1), (0.5, 0.2, 0.3), "paint_blue")
    m.cyl(0.03, 0.1, (0.5, 0.1, 0.3), "chrome", seg=6)


W = [w_recycler, w_potable, w_greywater, w_condensate, w_heater, w_uv, w_ro, w_distill]


# ================================================================ PLANTS
def lettuce(m, x, y, z, s=1.0, mat="food_green"):
    m.sphere(0.09 * s, (x, y + 0.05 * s, z), mat, seg=7, ring=3, scale=(1, 0.65, 1))
    m.sphere(0.06 * s, (x, y + 0.09 * s, z), "leaf", seg=5, ring=3, scale=(1, 0.7, 1))


def tomato_vine(m, x, y, z, h=1.0, rng=None):
    m.cyl(0.01, h, (x, y + h / 2, z), "wood_light", seg=5)
    for k in range(5):
        yy = y + 0.2 + k * h * 0.17
        s = -1 if k % 2 else 1
        m.sphere(0.06, (x + s * 0.06, yy, z), "leaf", seg=6, ring=4, scale=(1.4, 0.4, 1))
        if k > 0:
            m.sphere(0.03, (x - s * 0.04, yy - 0.05, z + 0.02), "ls_tomato", seg=6, ring=4)
    m.sphere(0.06, (x, y + h, z), "leaf", seg=6, ring=4, scale=(1, 0.6, 1))


def wheat(m, x, y, z, h=0.6):
    for dx, dz in ((0, 0), (0.035, 0.02), (-0.03, 0.03)):
        m.cyl(0.005, h, (x + dx, y + h / 2, z + dz), "food_green", seg=3)
        m.cyl(0.014, 0.08, (x + dx, y + h + 0.03, z + dz), "ls_wheat", seg=4, r2=0.004)


def herb(m, x, y, z, s=1.0, mat="leaf"):
    for dx, dz in ((0, 0), (0.04, 0.02), (-0.04, 0.01), (0.0, -0.04)):
        m.cyl(0.035 * s, 0.14 * s, (x + dx, y + 0.07 * s, z + dz), mat, seg=5, r2=0.0)


def flower(m, x, y, z, mat="ls_pink", h=0.3):
    m.cyl(0.006, h, (x, y + h / 2, z), "food_green", seg=4)
    m.sphere(0.04, (x, y + h + 0.01, z), mat, seg=7, ring=4, scale=(1, 0.45, 1))
    m.sphere(0.015, (x, y + h + 0.03, z), "ls_yellow", seg=5, ring=3)


def mushroom(m, x, y, z, s=1.0, mat="ls_mush"):
    m.cyl(0.02 * s, 0.09 * s, (x, y + 0.045 * s, z), "foam", seg=4)
    m.sphere(0.05 * s, (x, y + 0.09 * s, z), mat, seg=6, ring=3, scale=(1, 0.6, 1))


def trough(m, cx, cy, cz, w, d, h, soil=True, frame="steel"):
    m.box((w, h, d), (cx, cy + h / 2, cz), "plastic_white", 0.015)
    m.box((w - 0.06, 0.02, d - 0.06), (cx, cy + h - 0.01, cz), "soil" if soil else "water")


# ================================================================ PLANTERS
PLANTER = ["Lettuce Trough", "Tomato Vine Rack", "Wheat Tray Bed", "Herb Shelf Rack", "Flower Bed Planter",
           "Dwarf Tree Tub", "Vertical Grow Tower", "Mushroom Shelf", "Strawberry Tiered Planter",
           "Microgreen Rack"]


@family("planter", PLANTER, mount="floor", tags=["lifesupport", "hydroponics", "plants"], solid=True)
def planter(m, i, label, rng):
    lean(m)
    P[i](m, rng)


def p_lettuce(m, rng):
    for x in (-0.5, 0.5):
        for z in (-0.28, 0.28):
            m.box((0.06, 0.6, 0.06), (x, 0.3, z), "hull_dark", 0.005)
    m.box((1.2, 0.05, 0.7), (0, 0.1, 0), "hull_dark", 0.005)
    trough(m, 0, 0.62, 0, 1.25, 0.65, 0.12, False)
    m.box((1.1, 0.03, 0.5), (0, 0.7, 0), "foam")
    for r in range(2):
        for c in range(5):
            lettuce(m, -0.45 + c * 0.225, 0.72, -0.14 + r * 0.28, 1.0 + 0.1 * ((r + c) % 2), "food_green" if (r + c) % 2 else "leaf")
    m.box((0.2, 0.2, 0.15), (0.0, 0.3, 0.0), "hull_mid", 0.01)
    m.tube([(0.1, 0.35, 0.0), (0.5, 0.35, 0.0), (0.5, 0.62, 0.2)], 0.02, "plastic_black")
    led(m, 0.0, 0.32, 0.08, "em_cyan")


def p_tomato(m, rng):
    m.box((1.4, 0.1, 0.5), (0, 0.05, 0), "hull_dark", 0.008)
    trough(m, 0, 0.1, 0, 1.3, 0.42, 0.28)
    for x in (-0.55, 0.55):
        m.box((0.05, 2.0, 0.05), (x, 1.05, -0.24), "black_metal", 0.004)
    m.box((1.3, 0.05, 0.05), (0, 2.02, -0.24), "black_metal", 0.004)
    for k in range(4):
        x = -0.48 + k * 0.32
        tomato_vine(m, x, 0.38, 0.0, 1.5 + 0.1 * (k % 2), rng)
        m.link((x, 2.02, -0.24), (x, 1.85, 0.0), 0.004, "plastic_white", 4)
    m.box((1.2, 0.03, 0.03), (0, 2.0, -0.2), "em_violet")
    m.box((0.2, 0.15, 0.05), (0.55, 0.22, 0.24), "hull_mid", 0.006)
    led(m, 0.55, 0.22, 0.27, "em_green")


def p_wheat(m, rng):
    for t in range(3):
        y = 0.1 + t * 0.62
        trough(m, 0, y, 0, 1.5, 0.6, 0.1)
        for r in range(2):
            for c in range(4):
                wheat(m, -0.55 + c * 0.37 + 0.12 * r, y + 0.1, -0.15 + r * 0.3, 0.38 + 0.05 * ((c * 3 + r) % 3))
        m.box((1.5, 0.03, 0.03), (0, y + 0.52, 0.28), "em_white")
    for x in (-0.78, 0.78):
        m.box((0.05, 2.0, 0.65), (x, 1.0, 0), "hull_dark", 0.005)
    m.box((1.6, 0.05, 0.7), (0, 2.02, 0), "hull_dark", 0.005)
    m.box((1.5, 0.08, 0.6), (0, 0.04, 0), "hull_dark", 0.005)


def p_herb(m, rng):
    m.box((0.06, 1.6, 0.4), (-0.6, 0.8, 0), "hull_mid", 0.005)
    m.box((0.06, 1.6, 0.4), (0.6, 0.8, 0), "hull_mid", 0.005)
    m.box((1.26, 0.06, 0.4), (0, 0.03, 0), "hull_dark")
    mats = ["leaf", "food_green", "ls_dleaf", "leaf"]
    for t in range(4):
        y = 0.3 + t * 0.4
        m.box((1.2, 0.03, 0.36), (0, y, 0), "hull_light", 0.004)
        m.box((1.2, 0.02, 0.02), (0, y + 0.02, 0.18), "hull_light")
        for c in range(4):
            x = -0.45 + c * 0.3
            m.cyl(0.09, 0.1, (x, y + 0.065, 0), "ls_tub" if (c + t) % 2 else "paint_white", seg=8, r2=0.075)
            herb(m, x, y + 0.11, 0, 1.0 + 0.2 * ((c + t) % 3), mats[(c + t) % 4])
        m.box((1.2, 0.02, 0.03), (0, y + 0.36, 0.14), "em_white") if t < 3 else None
    m.box((1.2, 0.03, 0.4), (0, 1.62, 0), "hull_mid", 0.004)


def p_flower(m, rng):
    m.box((1.5, 0.35, 0.7), (0, 0.175, 0), "concrete", 0.02)
    m.box((1.4, 0.05, 0.6), (0, 0.375, 0), "soil")
    cols = ["ls_pink", "ls_yellow", "ls_purple", "ls_orange", "paint_white"]
    n = 0
    for r in range(3):
        for c in range(6):
            x = -0.6 + c * 0.24 + (0.06 if r % 2 else 0)
            flower(m, x, 0.4, -0.2 + r * 0.2, cols[(r * 2 + c) % 5], 0.16 + 0.07 * ((c + r * 2) % 3))
            n += 1
    for x in (-0.3, 0.4):
        m.sphere(0.1, (x, 0.42, 0.28), "leaf", seg=7, ring=4, scale=(1.2, 0.7, 1))
    m.box((0.3, 0.04, 0.01), (0, 0.15, 0.355), "em_warm")
    m.box((1.55, 0.04, 0.75), (0, 0.36, 0), "hull_mid", 0.008)


def p_tree(m, rng):
    m.cyl(0.35, 0.06, (0, 0.03, 0), "black_metal", seg=16)
    m.cyl(0.32, 0.45, (0, 0.28, 0), "ls_tub", seg=16, r2=0.36)
    m.cyl(0.36, 0.05, (0, 0.52, 0), "hull_dark", seg=16)
    m.cyl(0.32, 0.03, (0, 0.5, 0), "soil", seg=16)
    m.cyl(0.04, 1.1, (0, 1.05, 0), "wood_dark", seg=7, r2=0.025)
    m.link((0, 1.0, 0), (0.25, 1.4, 0.05), 0.02, "wood_dark", 6)
    m.link((0, 1.15, 0), (-0.25, 1.5, -0.05), 0.02, "wood_dark", 6)
    for p, s in (((0, 1.75, 0), 0.34), ((0.3, 1.5, 0.08), 0.24), ((-0.3, 1.58, -0.06), 0.25), ((0.05, 1.5, 0.25), 0.2)):
        m.sphere(s, p, "leaf", seg=10, ring=6, scale=(1, 0.85, 1))
    for p in ((0.2, 1.7, 0.25), (-0.15, 1.9, 0.2), (0.35, 1.45, -0.1)):
        m.sphere(0.045, p, "ls_orange", seg=6, ring=4)
    led(m, 0.0, 0.3, 0.37, "em_green", 0.04)


def p_tower(m, rng):
    m.cyl(0.35, 0.08, (0, 0.04, 0), "hull_dark", seg=16)
    m.cyl(0.2, 2.2, (0, 1.15, 0), "plastic_white", seg=12)
    for k in range(6):
        y = 0.35 + k * 0.32
        m.cyl(0.24, 0.04, (0, y, 0), "hull_light", seg=12)
        for j in range(3):
            a = j * 2.094 + k * 0.6
            px, pz = math.cos(a) * 0.24, math.sin(a) * 0.24
            m.box((0.1, 0.07, 0.07), (px, y + 0.04, pz), "ls_tub", 0.005, rot=(0, -a, 0))
            m.sphere(0.06, (math.cos(a) * 0.29, y + 0.11, math.sin(a) * 0.29), "food_green" if (j + k) % 2 else "leaf", seg=6, ring=4, scale=(1, 0.8, 1))
    for a in (math.pi / 4, 3 * math.pi / 4 + math.pi, 5 * math.pi / 4 - math.pi):
        pass
    for a in (0.8, 3.94):
        m.box((0.03, 2.1, 0.012), (math.cos(a) * 0.205, 1.15, math.sin(a) * 0.205), "em_violet", rot=(0, -a, 0))
    m.cyl(0.24, 0.1, (0, 2.3, 0), "hull_dark", seg=12)
    m.sphere(0.2, (0, 2.36, 0), "hull_mid", seg=12, ring=4, scale=(1, 0.5, 1))
    m.box((0.14, 0.1, 0.02), (0, 0.15, 0.21), "black_metal")
    m.box((0.1, 0.03, 0.02), (0, 0.15, 0.22), "em_cyan")


def p_mush(m, rng):
    m.box((1.4, 1.8, 0.05), (0, 0.95, -0.35), "hull_dark", 0.005)
    for x in (-0.7, 0.7):
        m.box((0.05, 1.8, 0.7), (x, 0.9, 0), "hull_mid", 0.005)
    for t in range(4):
        y = 0.2 + t * 0.45
        m.box((1.35, 0.04, 0.7), (0, y, 0), "hull_light", 0.004)
        m.box((1.25, 0.1, 0.6), (0, y + 0.07, 0), "wood_dark", 0.01)
        m.box((1.2, 0.03, 0.55), (0, y + 0.125, 0), "soil")
        for c in range(4):
            for r in range(2):
                mushroom(m, -0.5 + c * 0.32 + 0.08 * r, y + 0.13, -0.12 + r * 0.25, 0.9 + 0.6 * ((c * 5 + r * 3 + t) % 3) / 2,
                         ["ls_mush", "fabric_tan", "foam", "food_brown"][(c + t) % 4])
        m.box((1.2, 0.02, 0.03), (0, y + 0.35, 0.3), "em_blue")
    m.box((1.4, 0.05, 0.75), (0, 1.85, 0), "hull_dark", 0.005)
    m.box((0.14, 0.14, 0.03), (0.55, 1.6, -0.32), "black_metal")
    m.box((0.12, 0.03, 0.02), (0.55, 1.6, -0.3), "em_cyan")


def p_strawberry(m, rng):
    m.box((0.9, 0.08, 0.9), (0, 0.04, 0), "hull_dark", 0.008)
    for t, (sz, y) in enumerate(((0.8, 0.25), (0.6, 0.6), (0.4, 0.9))):
        m.box((sz, 0.3, sz), (0, y, 0), "plastic_white", 0.02)
        m.box((sz - 0.06, 0.02, sz - 0.06), (0, y + 0.15, 0), "soil")
        n = 6 + t * 0
        for k in range(8 - t * 2):
            a = 2 * math.pi * k / (8 - t * 2)
            rr = sz / 2 - 0.09
            px, pz = math.cos(a) * rr, math.sin(a) * rr
            m.sphere(0.07, (px, y + 0.2, pz), "leaf", seg=7, ring=4, scale=(1.2, 0.6, 1.2))
            m.sphere(0.03, (px * 1.15, y + 0.17, pz * 1.15), "ls_tomato", seg=6, ring=4, scale=(1, 1.2, 1))
    m.box((0.06, 0.06, 0.06), (0.3, 0.25, 0.41), "hull_mid")
    m.sphere(0.06, (0, 1.1, 0), "food_green", seg=7, ring=4)
    m.sphere(0.03, (0.05, 1.08, 0.04), "ls_tomato", seg=6, ring=4)
    led(m, 0.0, 0.25, 0.41, "em_green", 0.03)
    m.box((0.5, 0.03, 0.03), (0, 0.42, 0.41), "em_violet")
    m.box((0.35, 0.03, 0.03), (0, 0.76, 0.31), "em_violet")


def p_micro(m, rng):
    for x in (-0.65, 0.65):
        m.box((0.06, 1.8, 0.06), (x, 0.9, -0.3), "steel")
        m.box((0.06, 1.8, 0.06), (x, 0.9, 0.3), "steel")
    for t in range(5):
        y = 0.15 + t * 0.4
        m.box((1.4, 0.03, 0.7), (0, y, 0), "steel", 0.003)
        m.box((1.3, 0.07, 0.6), (0, y + 0.05, 0), "paint_white", 0.008)
        mat = ["food_green", "ls_purple", "leaf", "food_red", "food_green"][t]
        m.box((1.24, 0.05, 0.52), (0, y + 0.1, 0), mat, 0.006)
        for k in range(10):
            m.box((0.02, 0.05, 0.5), (-0.55 + k * 0.12, y + 0.13, 0), "leaf" if t != 3 else "food_red")
        m.box((1.3, 0.025, 0.05), (0, y + 0.3, 0.2), "em_violet" if t % 2 == 0 else "em_white")
    m.box((1.4, 0.04, 0.7), (0, 2.02, 0), "steel", 0.003)
    m.box((0.2, 0.15, 0.1), (0.4, 2.1, 0), "hull_dark", 0.008)
    m.tube([(0.4, 2.05, 0), (0.4, 1.9, 0.33), (0.66, 1.9, 0.33), (0.66, 0.2, 0.33)], 0.018, "plastic_black")


P = [p_lettuce, p_tomato, p_wheat, p_herb, p_flower, p_tree, p_tower, p_mush, p_strawberry, p_micro]

LIGHTS = ["Grow Light Bar Panel", "Hanging Grow Light Array"]


@family("planter", LIGHTS, mount="ceiling", tags=["lifesupport", "hydroponics", "light"], solid=False)
def growlight(m, i, label, rng):
    lean(m)
    if i == 0:
        m.box((1.6, 0.08, 0.5), (0, -0.04, 0), "hull_dark", 0.01)
        m.box((1.5, 0.04, 0.4), (0, -0.1, 0), "hull_mid", 0.006)
        for k in range(5):
            m.box((1.4, 0.02, 0.05), (0, -0.13, -0.16 + k * 0.08), "em_violet" if k % 2 == 0 else "em_white")
        m.box((0.12, 0.05, 0.12), (-0.7, -0.1, 0.0), "black_metal")
        m.box((0.12, 0.05, 0.12), (0.7, -0.1, 0.0), "black_metal")
        m.cyl(0.02, 0.06, (0.6, 0.0, 0.0), "steel", seg=6)
        led(m, 0.7, -0.09, 0.27, "em_green", 0.03)
    else:
        m.cyl(0.15, 0.04, (0, -0.02, 0), "hull_dark", seg=12)
        for s in (-0.5, 0.5):
            m.link((s * 0.3, -0.03, 0), (s * 0.6, -0.5, 0), 0.006, "steel", 5)
        for k in range(3):
            x = -0.7 + k * 0.7
        m.box((1.8, 0.05, 0.4), (0, -0.55, 0), "hull_dark", 0.01)
        for k in range(3):
            m.box((0.5, 0.02, 0.32), (-0.6 + k * 0.6, -0.59, 0), "em_violet" if k != 1 else "em_white")
            m.box((0.52, 0.03, 0.02), (-0.6 + k * 0.6, -0.58, 0.17), "black_metal")
            m.box((0.52, 0.03, 0.02), (-0.6 + k * 0.6, -0.58, -0.17), "black_metal")
        m.box((1.8, 0.04, 0.04), (0, -0.52, 0.21), "steel")
        for x in (-0.9, 0.9):
            m.link((x * 0.9, -0.55, 0), (x * 0.5, -0.03, 0), 0.008, "steel", 5)


# ================================================================ CYLINDERS
CYL = ["Oxygen Cylinder Rack", "Nitrogen Cylinder Trio", "Cryo Dewar", "Emergency Air Bottle",
       "Portable O2 Unit", "Cylinder Hand Cart", "Bulk LOX Tank"]


def bottle(m, x, z, h, r, mat, cap="steel", y0=0.0):
    m.cyl(r, h * 0.85, (x, y0 + h * 0.425, z), mat, seg=12)
    m.sphere(r, (x, y0 + h * 0.85, z), mat, seg=12, ring=4, scale=(1, 0.55, 1))
    m.cyl(r * 0.28, 0.1, (x, y0 + h * 0.85 + r * 0.55 + 0.03, z), cap, seg=8)
    m.cyl(r * 0.16, 0.1, (x + 0.0, y0 + h * 0.85 + r * 0.55 + 0.1, z), "brass", axis="x", seg=6)


@family("cylinder", CYL, mount="floor", tags=["lifesupport", "gas"], solid=True)
def cylinders(m, i, label, rng):
    lean(m)
    C[i](m, rng)


def c_o2_rack(m, rng):
    m.box((1.5, 0.08, 0.5), (0, 0.04, 0), "hull_dark", 0.008)
    for x in (-0.75, 0.75):
        m.box((0.05, 1.5, 0.5), (x, 0.8, 0), "hull_mid", 0.005)
    for y in (0.6, 1.3):
        m.box((1.5, 0.05, 0.05), (0, y, 0.22), "black_metal")
    for k in range(4):
        x = -0.55 + k * 0.37
        bottle(m, x, 0.0, 1.5, 0.13, "ls_o2")
        m.cyl(0.131, 0.16, (x, 1.0, 0), "paint_white", seg=12)
        m.cyl(0.132, 0.03, (x, 1.32, 0), "paint_white", seg=12)
    m.box((0.25, 0.08, 0.02), (0.0, 0.3, 0.26), "paint_blue")
    m.box((0.2, 0.03, 0.012), (0.0, 0.3, 0.275), "em_cyan")
    m.box((1.5, 0.04, 0.02), (0, 0.82, 0.26), "hazard_yellow")


def c_n2(m, rng):
    m.box((1.0, 0.06, 0.6), (0, 0.03, 0.1), "hull_dark", 0.008)
    for k, x in enumerate((-0.3, 0.0, 0.3)):
        bottle(m, x, 0.0 if k != 1 else 0.2, 1.6, 0.11, "ls_n2")
        m.cyl(0.112, 0.12, (x, 1.0, 0.0 if k != 1 else 0.2), "paint_white", seg=12)
    m.box((1.0, 0.06, 0.04), (0, 0.6, 0.2), "steel")
    m.box((1.0, 1.0, 0.04), (0, 0.55, -0.24), "hull_mid", 0.005)
    m.box((0.3, 0.08, 0.02), (0.0, 0.3, 0.42), "black_metal")
    m.box((0.2, 0.03, 0.02), (0.0, 0.3, 0.43), "em_amber")
    m.tube([(-0.3, 1.66, 0), (-0.3, 1.8, 0), (0.3, 1.8, 0), (0.3, 1.66, 0.0)], 0.02, "brass")
    m.tube([(0.0, 1.8, 0), (0.0, 1.95, 0)], 0.02, "brass")


def c_dewar(m, rng):
    m.cyl(0.4, 0.05, (0, 0.04, 0), "black_metal", seg=20)
    for k in range(3):
        a = k * 2.094
        m.box((0.05, 0.3, 0.05), (math.cos(a) * 0.3, 0.2, math.sin(a) * 0.3), "hull_dark", 0.004)
    m.cyl(0.36, 1.1, (0, 0.85, 0), "brushed_alu", seg=22)
    m.sphere(0.36, (0, 1.4, 0), "brushed_alu", seg=22, ring=6, scale=(1, 0.5, 1))
    m.torus(0.36, 0.02, (0, 0.4, 0), "steel", seg=22, tseg=5)
    m.cyl(0.11, 0.1, (0, 1.6, 0), "steel", seg=10)
    m.cyl(0.13, 0.05, (0, 1.68, 0), "hazard_yellow", seg=10)
    m.cyl(0.06, 0.12, (0.0, 1.76, 0), "black_metal", seg=8)
    m.tube([(0.2, 1.5, 0), (0.42, 1.5, 0), (0.42, 1.0, 0)], 0.02, "copper")
    m.cyl(0.05, 0.05, (0.42, 0.95, 0), "paint_red", axis="y", seg=8)
    m.box((0.22, 0.3, 0.02), (0, 0.8, 0.36), "paint_white", 0.004, rot=(0, 0, 0))
    m.box((0.14, 0.05, 0.012), (0, 0.9, 0.375), "em_cyan")
    m.box((0.14, 0.05, 0.012), (0, 0.75, 0.375), "paint_red")


def c_air_bottle(m, rng):
    m.box((0.5, 0.06, 0.5), (0, 0.03, 0), "hull_dark", 0.008)
    m.box((0.06, 1.15, 0.06), (0, 0.6, -0.2), "hull_mid")
    m.cyl(0.11, 0.7, (0, 0.6, 0), "carbon", seg=14)
    m.sphere(0.11, (0, 0.95, 0), "carbon", seg=14, ring=4, scale=(1, 0.6, 1))
    m.sphere(0.11, (0, 0.25, 0), "carbon", seg=14, ring=4, scale=(1, 0.5, 1))
    m.cyl(0.115, 0.1, (0, 0.45, 0), "paint_green", seg=14)
    m.cyl(0.115, 0.04, (0, 0.75, 0), "hazard_yellow", seg=14)
    m.box((0.3, 0.05, 0.16), (0, 0.4, -0.12), "black_metal", 0.004)
    m.box((0.3, 0.05, 0.16), (0, 0.8, -0.12), "black_metal", 0.004)
    m.cyl(0.04, 0.12, (0, 1.06, 0), "brass", seg=8)
    m.cyl(0.04, 0.03, (0.09, 1.12, 0.05), "black_metal", axis="z", seg=10)
    m.cyl(0.03, 0.01, (0.09, 1.12, 0.07), "em_green", axis="z", seg=10)
    m.tube([(0.0, 1.1, 0.05), (0.0, 1.2, 0.2), (-0.2, 1.2, 0.3)], 0.015, "rubber")
    m.box((0.14, 0.12, 0.03), (-0.2, 1.2, 0.34), "paint_orange", 0.006)


def c_portable(m, rng):
    m.box((0.36, 0.55, 0.22), (0, 0.32, 0), "paint_white", 0.03)
    m.box((0.38, 0.05, 0.24), (0, 0.06, 0), "rubber", 0.01)
    m.box((0.28, 0.04, 0.05), (0, 0.72, 0), "black_metal", 0.006)
    m.box((0.04, 0.08, 0.05), (-0.13, 0.66, 0), "black_metal")
    m.box((0.04, 0.08, 0.05), (0.13, 0.66, 0), "black_metal")
    m.box((0.28, 0.2, 0.02), (0, 0.4, 0.115), "hull_dark", 0.004)
    m.screen((0.22, 0.12), (0, 0.42, 0.127), "vitals", bezel=0.006)
    gauge(m, 0.0, 0.26, 0.13, 0.03, "em_cyan")
    m.cyl(0.03, 0.06, (0.18, 0.4, 0.0), "steel", axis="x", seg=8)
    m.tube([(0.2, 0.4, 0.0), (0.3, 0.3, 0.15), (0.25, 0.1, 0.3)], 0.012, "rubber")
    m.box((0.2, 0.06, 0.02), (0, 0.55, 0.115), "paint_red")
    led(m, 0.1, 0.16, 0.12, "em_green", 0.03)


def c_cart(m, rng):
    m.box((0.7, 0.05, 0.5), (0, 0.15, 0), "steel", 0.005)
    for x in (-0.3, 0.3):
        for z in (-0.2, 0.2):
            m.cyl(0.06, 0.04, (x, 0.06, z), "rubber", axis="x", seg=10)
            m.box((0.03, 0.08, 0.03), (x, 0.11, z), "steel")
    m.box((0.05, 0.9, 0.05), (-0.32, 0.65, -0.22), "steel")
    m.box((0.05, 0.9, 0.05), (0.32, 0.65, -0.22), "steel")
    m.box((0.7, 0.05, 0.05), (0, 1.1, -0.22), "steel")
    m.link((-0.32, 1.1, -0.22), (-0.32, 1.1, -0.34), 0.02, "black_metal")
    m.link((0.32, 1.1, -0.22), (0.32, 1.1, -0.34), 0.02, "black_metal")
    m.link((-0.32, 1.1, -0.34), (0.32, 1.1, -0.34), 0.02, "black_metal")
    m.cyl(0.12, 0.9, (-0.14, 0.65, -0.05), "ls_o2", seg=14)
    m.cyl(0.12, 0.9, (0.14, 0.65, -0.05), "ls_air", seg=14)
    for x in (-0.14, 0.14):
        m.sphere(0.12, (x, 1.1, -0.05), "ls_o2" if x < 0 else "ls_air", seg=12, ring=4, scale=(1, 0.5, 1))
        m.cyl(0.03, 0.1, (x, 1.2, -0.05), "brass", seg=8)
    m.box((0.5, 0.05, 0.05), (0, 0.5, 0.06), "black_metal")
    m.box((0.5, 0.05, 0.05), (0, 0.9, 0.06), "black_metal")


def c_lox(m, rng):
    for x in (-0.5, 0.5):
        m.box((0.12, 0.5, 0.9), (x, 0.25, 0), "hull_dark", 0.01)
    m.cyl(0.55, 1.5, (0, 0.85, 0), "brushed_alu", axis="x", seg=24)
    m.sphere(0.55, (0.75, 0.85, 0), "brushed_alu", seg=24, ring=8, scale=(0.5, 1, 1))
    m.sphere(0.55, (-0.75, 0.85, 0), "brushed_alu", seg=24, ring=8, scale=(0.5, 1, 1))
    for x in (-0.4, 0.4):
        m.torus(0.55, 0.025, (x, 0.85, 0), "steel", axis="x", seg=24, tseg=5)
    m.cyl(0.56, 0.3, (0, 0.85, 0), "paint_blue", axis="x", seg=24)
    m.cyl(0.14, 0.14, (0, 1.42, 0), "steel", seg=12)
    m.cyl(0.05, 0.2, (0, 1.56, 0), "black_metal", seg=8)
    m.tube([(0.3, 1.4, 0.0), (0.3, 1.65, 0.0), (-0.3, 1.65, 0.0), (-0.3, 1.4, 0.0)], 0.03, "steel")
    m.box((0.5, 0.36, 0.05), (0, 0.3, 0.48), "hull_dark", 0.008)
    gauge(m, -0.12, 0.3, 0.51, 0.06, "em_cyan")
    gauge(m, 0.12, 0.3, 0.51, 0.06, "em_amber")
    hazard(m, 0, 0.1, 0.46, 0.5, 0.05)


C = [c_o2_rack, c_n2, c_dewar, c_air_bottle, c_portable, c_cart, c_lox]


@family("cylinder", ["Gas Manifold Panel"], mount="wall", tags=["lifesupport", "gas"], solid=False, mount_y=1.4)
def manifold(m, i, label, rng):
    lean(m)
    m.box((1.0, 0.8, 0.08), (0, 0, 0.04), "hull_dark", 0.01)
    m.box((0.94, 0.74, 0.02), (0, 0, 0.09), "hull_mid", 0.005)
    cols = ["ls_o2", "ls_n2", "paint_green", "paint_red"]
    names = ["em_cyan", "em_white", "em_green", "em_red"]
    for k in range(4):
        x = -0.33 + k * 0.22
        m.cyl(0.04, 0.6, (x, -0.02, 0.15), cols[k], seg=8)
        m.cyl(0.05, 0.03, (x, 0.2, 0.15), "brass", seg=8)
        gauge(m, x, 0.24, 0.12, 0.05, names[k])
        m.cyl(0.05, 0.05, (x, -0.24, 0.16), "paint_red" if k == 3 else "steel", axis="z", seg=8)
        m.cyl(0.03, 0.05, (x, -0.34, 0.15), "brass", seg=6)
    m.box((0.92, 0.04, 0.06), (0, -0.33, 0.13), "black_metal")
    label_plate(m, 0, 0.36, 0.1, 0.4, "em_amber")
    bolts(m, (-0.45, 0.45), (-0.35, 0.35), 0.09)
