"""Communications / computing components: racks, storage, antennas, comms units, network gear (50 labels)."""
import math

from mathutils import Euler, Vector

from ..kit import family, register_material

register_material("cm_rack", "#23272d", 0.7, 0.4)
register_material("cm_cable_y", "#e2c21a", 0.0, 0.5)
register_material("cm_cable_b", "#2a6fd0", 0.0, 0.5)
register_material("cm_cable_r", "#c22a22", 0.0, 0.5)
register_material("cm_cable_g", "#2fa34a", 0.0, 0.5)
register_material("cm_ice", "#dcecf5", 0.1, 0.55)
register_material("cm_coolant", "#4bd0e8", 0.0, 0.1, alpha=0.5)
register_material("cm_orange", "#ff6a10", 0.2, 0.45)
register_material("cm_crystal", "#7fdfff", 0.0, 0.1, emission=2.2)
register_material("cm_crystal2", "#ff7ad9", 0.0, 0.1, emission=2.2)
register_material("cm_crystal3", "#8dff9c", 0.0, 0.1, emission=2.2)

TAGC = ["comms", "computing"]
LEDC = ["em_green", "em_green", "em_amber", "em_cyan", "em_green", "em_blue"]


def led(m, p, mat="em_green", s=0.012):
    m.box((s, s, 0.008), p, mat)


def leds(m, x0, y, z, n, dx, mats, s=0.012):
    for k in range(n):
        m.box((s, s, 0.008), (x0 + k * dx, y, z), mats[k % len(mats)])


def rp(p, rot, c):
    v = Euler(rot, "XYZ").to_matrix() @ Vector(p)
    return (v.x + c[0], v.y + c[1], v.z + c[2])


def dish(m, c, r, rot=(0, 0, 0), mat="paint_white", depth=0.08):
    m.cyl(r, depth, c, mat, axis="z", seg=18, r2=r * 0.25, rot=rot)
    m.cyl(r * 0.26, depth * 0.6, rp((0, 0, -depth * 0.6), rot, c), "black_metal", axis="z", seg=8, rot=rot)
    tip = rp((0, 0, r * 0.55), rot, c)
    for a in (0, 2.1, 4.2):
        m.link(rp((math.cos(a) * r * 0.9, math.sin(a) * r * 0.9, depth * 0.5), rot, c), tip, 0.007, "steel", seg=4)
    m.cyl(r * 0.07, r * 0.12, tip, "chrome", axis="z", seg=8, r2=r * 0.04, rot=rot)


def hazard(m, x, y, z, w, h):
    m.box((w, h, 0.008), (x, y, z), "hazard_yellow")
    for k in range(int(w / 0.07)):
        m.box((0.02, h * 0.98, 0.004), (x - w / 2 + 0.05 + k * 0.07, y, z + 0.004), "black_metal", rot=(0, 0, 0.5))


def handle(m, x, y, z, horiz=True, l=0.14):
    m.box((l, 0.016, 0.02) if horiz else (0.016, l, 0.02), (x, y, z), "chrome")


def bolts(m, pts, z, mat="steel", r=0.012):
    for x, y in pts:
        m.cyl(r, 0.01, (x, y, z), mat, axis="z", seg=5)


def _reg(cat, table, **kw):
    def fn(m, i, label, rng):
        table[label](m, rng)
    fn.__name__ = "comm_" + cat + "_" + kw.get("mount", "floor")
    family(cat, list(table), **kw)(fn)


def _add(table, label):
    def deco(f):
        table[label] = f
        return f
    return deco


UH = 0.0445


def rack_frame(m, w=0.6, d=1.0, h=2.0, closed=True, side="cm_rack", post="gunmetal"):
    """Standard rack shell; returns front face z of the equipment plane."""
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.05, h, 0.05), (sx * (w / 2 - 0.025), h / 2, sz * (d / 2 - 0.025)), post)
    m.box((w, 0.08, d), (0, 0.04, 0), "black_metal", 0.008)
    m.box((w, 0.06, d), (0, h - 0.03, 0), "black_metal", 0.008)
    if closed:
        for sx in (-1, 1):
            m.box((0.014, h - 0.14, d - 0.06), (sx * (w / 2 - 0.007), h / 2, 0), side)
        m.box((w - 0.06, h - 0.14, 0.014), (0, h / 2, -d / 2 + 0.007), side)
    for sx in (-1, 1):
        m.box((0.02, h - 0.2, 0.014), (sx * 0.245, h / 2, d / 2 - 0.045), "steel")
    return d / 2 - 0.05


def unit(m, u0, n, zf, mat="hull_dark", w=0.46, depth=0.5):
    hh = n * UH - 0.004
    y = 0.1 + u0 * UH + n * UH / 2
    m.box((w, hh, depth), (0, y, zf - depth / 2), mat)
    return y, hh


def vents(m, y, hh, zf, x0=-0.2, x1=-0.05, n=4, mat="black_metal"):
    for k in range(n):
        m.box(((x1 - x0) / n * 0.6, hh * 0.6, 0.004), (x0 + (x1 - x0) * (k + 0.5) / n, y, zf + 0.002), mat)


# ==========================================================================
# RACKS
# ==========================================================================
RK = {}


@_add(RK, "blade server rack")
def _(m, rng):
    zf = rack_frame(m)
    m.box((0.5, 1.84, 0.012), (0, 1.02, zf - 0.02), "black_metal")
    for c in range(5):
        y, hh = unit(m, 2 + c * 7, 5, zf, "hull_dark")
        for b in range(7):
            x = -0.2 + b * 0.067
            m.box((0.056, hh - 0.01, 0.014), (x, y, zf + 0.007), "hull_mid")
            led(m, (x, y + hh / 2 - 0.025, zf + 0.016), LEDC[(b + c) % 6], 0.014)
        m.box((0.46, 0.02, 0.014), (0, y - hh / 2 - 0.004, zf + 0.007), "steel")
        m.box((0.05, 0.02, 0.014), (0.21, y + hh / 2 - 0.03, zf + 0.007), "em_cyan")
    for k in range(3):
        m.box((0.46, UH - 0.004, 0.4), (0, 1.75 + k * UH + 0.03, zf - 0.2), "hull_dark")
        vents(m, 1.75 + k * UH + 0.03, UH, zf, -0.2, 0.2, 10)
    m.box((0.04, 1.6, 0.05), (0.27, 1.0, zf - 0.03), "cm_cable_y")


@_add(RK, "storage array")
def _(m, rng):
    zf = rack_frame(m)
    for c in range(6):
        y, hh = unit(m, 2 + c * 6, 5, zf, "hull_dark")
        m.box((0.44, hh - 0.014, 0.012), (0, y, zf + 0.006), "black_metal")
        for b in range(8):
            x = -0.19 + b * 0.054
            m.box((0.045, 0.1, 0.006), (x, y - 0.005, zf + 0.014), "gunmetal")
            led(m, (x, y + 0.04, zf + 0.018), LEDC[(b * 7 + c) % 6], 0.01)
        m.box((0.16, 0.014, 0.01), (0.14, y - hh / 2 + 0.01, zf + 0.008), "em_blue") if c % 2 else None
    y, hh = unit(m, 38, 3, zf, "steel")
    vents(m, y, hh, zf, -0.2, 0.2, 8)
    m.box((0.46, 0.04, 0.5), (0, 0.16, zf - 0.25), "steel")
    m.box((0.2, 0.06, 0.02), (0, 0.1 + 0.03, zf + 0.01), "paint_blue")


@_add(RK, "network switch rack")
def _(m, rng):
    zf = rack_frame(m, closed=False)
    cabs = ["cm_cable_y", "cm_cable_b", "cm_cable_r", "cm_cable_g"]
    for c in range(8):
        u0 = 3 + c * 4
        y, hh = unit(m, u0, 1, zf, "hull_mid", depth=0.3)
        m.box((0.36, hh - 0.012, 0.006), (-0.04, y, zf + 0.003), "black_metal")
        for k in range(8):
            led(m, (-0.19 + k * 0.03, y, zf + 0.008), LEDC[(k + c) % 6], 0.012)
        m.box((0.05, 0.02, 0.006), (0.19, y, zf + 0.004), "em_cyan")
        # patch panel below
        y2, hh2 = unit(m, u0 + 1, 1, zf, "steel", depth=0.1)
        m.box((0.4, 0.018, 0.008), (0, y2, zf + 0.004), "black_metal")
        m.link((-0.19 + (c % 4) * 0.1, y2, zf + 0.01), (-0.19 + (c % 4) * 0.1 + 0.05, y2 - 0.09, zf + 0.06), 0.006, cabs[c % 4], seg=4)
        m.link((-0.19 + (c % 4) * 0.1 + 0.05, y2 - 0.09, zf + 0.06), (-0.19 + (c % 4) * 0.1 + 0.1, y2 - 0.16, zf + 0.01), 0.006, cabs[c % 4], seg=4)
    m.box((0.08, 1.7, 0.08), (0.34, 1.0, zf - 0.05), "black_metal")
    for k in range(5):
        m.box((0.09, 0.008, 0.1), (0.34, 0.2 + k * 0.34, zf - 0.05), "steel")
    m.box((0.5, 0.05, 0.4), (0, 1.9, -0.1), "steel")
    m.box((0.5, 0.012, 0.4), (0, 1.86, -0.1), "gunmetal")


@_add(RK, "cryogenic quantum rack")
def _(m, rng):
    zf = rack_frame(m, closed=False, post="cm_ice")
    m.box((0.5, 0.9, 0.3), (0, 0.6, zf - 0.15), "cm_ice", 0.02)
    m.box((0.46, 0.7, 0.012), (0, 0.6, zf + 0.008), "glass_blue")
    for k in range(4):
        m.box((0.4, 0.008, 0.18), (0, 0.4 + k * 0.16, zf - 0.09), "copper")
    m.cyl(0.02, 0.6, (0, 0.6, zf - 0.09), "gold_trim", seg=6)
    m.box((0.3, 0.06, 0.01), (0, 1.16, zf + 0.008), "black_metal")
    m.screen((0.24, 0.05), (0, 1.16, zf + 0.014), "graph")
    # cryostat drum on top
    m.cyl(0.24, 0.5, (0, 1.42, 0.0), "brushed_alu", seg=16)
    m.torus(0.24, 0.02, (0, 1.68, 0), "steel", seg=16, tseg=4)
    m.torus(0.24, 0.02, (0, 1.17, 0), "steel", seg=16, tseg=4)
    m.cyl(0.2, 0.06, (0, 1.72, 0), "gold_trim", seg=16)
    for k in range(6):
        a = k * 1.047
        m.link((math.cos(a) * 0.1, 1.72, math.sin(a) * 0.1), (math.cos(a) * 0.1, 1.9, math.sin(a) * 0.1), 0.012, "copper", seg=4)
    m.cyl(0.12, 0.1, (0, 1.95, 0), "hull_dark", seg=12)
    m.tube([(0.2, 1.65, 0.2), (0.28, 1.4, 0.2), (0.28, 0.2, 0.2)], 0.025, "steel", seg=6)
    for k in range(4):
        led(m, (-0.18 + k * 0.05, 0.16, zf + 0.008), ["em_cyan", "em_blue"][k % 2], 0.014)
    m.box((0.5, 0.2, 0.3), (0, 0.19, zf - 0.15), "hull_dark")


@_add(RK, "open frame rack")
def _(m, rng):
    zf = rack_frame(m, w=0.56, closed=False, post="steel")
    shelves = [0.3, 0.75, 1.15, 1.55]
    for k, y in enumerate(shelves):
        m.box((0.5, 0.02, 0.85), (0, y, 0.0), "steel")
        for j in range(2):
            w = 0.2 + 0.06 * ((k + j) % 3)
            x = -0.13 + j * 0.24
            h = 0.12 + 0.06 * ((k * 2 + j) % 3)
            m.box((w, h, 0.4), (x, y + 0.01 + h / 2, 0.15 - 0.1 * j), ["hull_dark", "plastic_grey", "gunmetal"][(k + j) % 3], 0.01)
            led(m, (x + w / 2 - 0.03, y + 0.04, 0.35 - 0.1 * j + 0.005), LEDC[(k + j * 2) % 6])
            m.box((w - 0.05, 0.02, 0.005), (x, y + 0.03 + h * 0.5, 0.35 - 0.1 * j + 0.004), "black_metal")
    # cables draped
    cols = ["cm_cable_y", "cm_cable_b", "cm_cable_r", "cm_cable_g", "black_metal"]
    for k in range(8):
        x = -0.2 + k * 0.055
        m.tube([(x, 0.3, 0.0), (x + 0.04, 0.55, -0.35), (x - 0.03, 0.95, -0.38), (x, 1.15, -0.05)], 0.008, cols[k % 5], seg=4)
    m.box((0.5, 0.05, 0.05), (0, 1.9, zf - 0.02), "steel")
    m.box((0.5, 0.15, 0.2), (0, 1.75, 0.05), "hull_dark", 0.01)
    leds(m, -0.2, 1.75, 0.152, 6, 0.06, LEDC)


@_add(RK, "liquid cooled cabinet")
def _(m, rng):
    zf = rack_frame(m, side="hull_dark")
    m.box((0.5, 1.8, 0.012), (0, 1.02, zf - 0.02), "glass_blue")
    for c in range(7):
        y, hh = unit(m, 1 + c * 5, 4, zf - 0.03, "hull_dark", depth=0.35)
        m.box((0.44, 0.01, 0.4), (0, y - hh / 2, zf - 0.2), "copper")
        led(m, (-0.2, y, zf - 0.028), LEDC[c % 6], 0.014)
        m.box((0.1, 0.04, 0.005), (0.15, y, zf - 0.03), "em_cyan")
    # manifolds
    for sx, col in ((-1, "em_blue"), (1, "em_red")):
        m.cyl(0.03, 1.8, (sx * 0.24, 1.0, zf + 0.03), "cm_coolant", seg=8)
        m.cyl(0.012, 1.8, (sx * 0.24, 1.0, zf + 0.03), col, seg=5)
        for c in range(7):
            m.link((sx * 0.24, 0.3 + c * 0.22, zf + 0.03), (sx * 0.14, 0.3 + c * 0.22, zf - 0.03), 0.012, "brass", seg=5)
    for k in range(9):
        m.torus(0.032, 0.006, (-0.24, 0.2 + k * 0.2, zf + 0.03), "steel", seg=8, tseg=4)
    m.box((0.5, 0.2, 0.5), (0, 1.92 - 0.1, 0), "steel")
    for k in range(5):
        m.box((0.44, 0.012, 0.4), (0, 1.86 + k * 0.02, 0.0), "brushed_alu")
    m.box((0.2, 0.05, 0.01), (0, 0.13, zf + 0.008), "black_metal")
    m.screen((0.18, 0.04), (0, 0.13, zf + 0.013), "bars")


@_add(RK, "tape archive tower")
def _(m, rng):
    W, D, H = 0.7, 0.8, 2.1
    m.box((W, H, D), (0, H / 2, 0), "cm_rack", 0.015)
    m.box((W - 0.08, 1.6, 0.03), (0, 1.15, D / 2 + 0.01), "black_metal")
    for r in range(11):
        for c in range(4):
            col = ["paint_blue", "paint_red", "paint_grey", "paint_teal"][(r + c * 2) % 4]
            m.box((0.12, 0.11, 0.05), (-0.216 + c * 0.144, 0.42 + r * 0.135, D / 2 + 0.03), "black_metal")
            m.box((0.1, 0.03, 0.006), (-0.216 + c * 0.144, 0.44 + r * 0.135, D / 2 + 0.058), col)
    # robotic picker rail
    for sx in (-1, 1):
        m.box((0.03, 1.7, 0.03), (sx * 0.32, 1.15, D / 2 + 0.07), "steel")
    m.box((0.66, 0.06, 0.06), (0, 1.0, D / 2 + 0.09), "hull_mid", 0.008)
    m.box((0.14, 0.16, 0.1), (-0.05, 1.0, D / 2 + 0.1), "paint_orange", 0.01)
    m.box((0.1, 0.01, 0.06), (-0.05, 0.94, D / 2 + 0.16), "steel")
    led(m, (-0.05, 1.05, D / 2 + 0.152), "em_green")
    m.box((0.5, 0.14, 0.02), (0, 0.15, D / 2 + 0.01), "hull_dark")
    m.screen((0.24, 0.08), (0, 0.15, D / 2 + 0.03), "text", bezel=0.008)
    m.box((0.3, 0.06, 0.01), (0, 1.98, D / 2 + 0.01), "em_amber")


@_add(RK, "crystal archive tower")
def _(m, rng):
    W, D, H = 0.7, 0.7, 2.1
    m.cyl(0.4, 0.14, (0, 0.07, 0), "black_metal", seg=6, bevel=0.01)
    m.cyl(0.4, 0.1, (0, H - 0.05, 0), "black_metal", seg=6, bevel=0.01)
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        m.box((0.05, H - 0.2, 0.05), (math.cos(a) * 0.38, H / 2, math.sin(a) * 0.38), "gold_trim")
        # glass panel between posts
        a2 = a + math.pi / 6
        m.box((0.38, H - 0.3, 0.012), (math.cos(a2) * 0.34, H / 2, math.sin(a2) * 0.34), "glass", 0, rot=(0, -a2 + math.pi / 2, 0))
    m.cyl(0.05, H - 0.2, (0, H / 2, 0), "hull_dark", seg=8)
    for k in range(7):
        y = 0.3 + k * 0.25
        for j in range(3):
            a = j * 2.094 + k * 0.5
            cm = ["cm_crystal", "cm_crystal2", "cm_crystal3"][(k + j) % 3]
            m.box((0.06, 0.13, 0.22), (math.cos(a) * 0.2, y, math.sin(a) * 0.2), cm, 0, rot=(0, -a, 0))
        m.cyl(0.24, 0.012, (0, y - 0.08, 0), "steel", seg=12)
    m.cyl(0.14, 0.05, (0, H + 0.02, 0), "steel", seg=10)
    m.cyl(0.03, 0.14, (0, H + 0.1, 0), "gold_trim", seg=6)


@_add(RK, "ups battery rack")
def _(m, rng):
    zf = rack_frame(m, post="hazard_yellow", side="hull_dark")
    for c in range(6):
        y, hh = unit(m, 1 + c * 5, 4, zf, "paint_navy", w=0.48)
        m.box((0.4, hh - 0.04, 0.02), (0, y, zf + 0.01), "black_metal")
        m.box((0.36, 0.02, 0.02), (0, y + hh / 2 - 0.04, zf + 0.02), "em_green" if c != 3 else "em_amber")
        handle(m, 0, y - hh / 2 + 0.02, zf + 0.035, True, 0.2)
        for k in range(2):
            m.cyl(0.02, 0.02, (-0.15 + k * 0.3, y, zf + 0.025), "cm_cable_r" if k else "black_metal", axis="z", seg=8)
    y, hh = unit(m, 32, 4, zf, "hull_light")
    m.screen((0.3, 0.1), (0, y + 0.02, zf + 0.004), "power", bezel=0.008)
    leds(m, -0.15, y - 0.06, zf + 0.005, 5, 0.05, ["em_green", "em_green", "em_amber", "em_red", "em_green"], 0.016)
    m.box((0.02, 0.1, 0.006), (0.18, y + 0.02, zf + 0.004), "em_amber")
    m.box((0.06, 0.02, 0.006), (0.18, y + 0.02, zf + 0.004), "em_amber", rot=(0, 0, 0.7))
    hazard(m, 0, 1.92, zf, 0.4, 0.05)


@_add(RK, "kvm console rack")
def _(m, rng):
    zf = rack_frame(m)
    for c in range(6):
        y, hh = unit(m, 1 + c * 3, 2, zf, "hull_dark") if c < 4 else (0, 0)
        if c < 4:
            vents(m, y, hh, zf, -0.2, 0.05, 5)
            leds(m, 0.12, y, zf + 0.004, 3, 0.03, LEDC)
    # pull-out console drawer
    m.box((0.5, 0.05, 0.62), (0, 1.03, zf - 0.05), "steel", 0.006)
    m.box((0.46, 0.02, 0.24), (0, 1.07, zf + 0.12), "plastic_black", 0.005)
    for r in range(3):
        m.box((0.42, 0.01, 0.045), (0, 1.09, zf + 0.06 + r * 0.055), "plastic_grey")
    # lid + screen tilted up
    m.box((0.5, 0.42, 0.03), (0, 1.3, zf - 0.25), "steel", 0.008, rot=(-0.12, 0, 0))
    m.screen((0.44, 0.34), (0, 1.3, zf - 0.23), "systems", rot=(-0.12, 0, 0), bezel=0.012)
    m.box((0.5, 0.05, 0.05), (0, 1.53, zf - 0.28), "steel")
    for k in range(6):
        y, hh = unit(m, 24 + k * 2, 2, zf, "hull_dark") if k < 4 else (0, 0)
        if k < 4:
            vents(m, y, hh, zf, -0.2, 0.05, 5)
            led(m, (0.16, y, zf + 0.004), LEDC[k])


@_add(RK, "computer core cabinet")
def _(m, rng):
    W, D, H = 0.9, 1.0, 2.1
    m.box((W, H, D), (0, H / 2, 0), "hull_dark", 0.03)
    m.box((W - 0.08, 1.4, 0.03), (0, 1.15, D / 2 + 0.005), "black_metal")
    m.box((0.38, 1.3, 0.03), (0, 1.15, D / 2 + 0.03), "glass_dark")
    m.cyl(0.11, 1.28, (0, 1.15, D / 2 - 0.05), "em_cyan", seg=10)
    for k in range(6):
        m.torus(0.15, 0.015, (0, 0.6 + k * 0.2, D / 2 - 0.05), "steel", seg=10, tseg=4)
    for sx in (-1, 1):
        for k in range(8):
            m.box((0.18, 0.06, 0.02), (sx * 0.29, 0.55 + k * 0.15, D / 2 + 0.03), "hull_mid")
            led(m, (sx * 0.29 + 0.06, 0.55 + k * 0.15, D / 2 + 0.045), LEDC[(k + sx) % 6])
    m.screen((0.5, 0.14), (0, 1.94, D / 2 + 0.01), "diagnostic", bezel=0.01)
    m.box((W - 0.1, 0.08, 0.02), (0, 0.18, D / 2 + 0.01), "hazard_yellow")
    for k in range(4):
        m.box((0.16, 0.02, 0.2), (-0.25 + k * 0.17, H + 0.01, 0.1), "black_metal")
    m.box((0.02, H - 0.2, 0.02), (0, H / 2, D / 2 + 0.005), "black_metal")


@_add(RK, "gpu cluster rack")
def _(m, rng):
    zf = rack_frame(m)
    for c in range(7):
        y, hh = unit(m, 2 + c * 5, 4, zf, "hull_dark")
        m.box((0.44, hh - 0.01, 0.01), (0, y, zf + 0.005), "black_metal")
        for f in range(3):
            fx = -0.14 + f * 0.14
            m.cyl(0.055, 0.012, (fx, y, zf + 0.012), "gunmetal", axis="z", seg=8)
            m.cyl(0.02, 0.016, (fx, y, zf + 0.014), "em_green" if (c + f) % 3 else "em_cyan", axis="z", seg=4)
        led(m, (0.205, y + hh / 2 - 0.02, zf + 0.012), "em_green")
    y, hh = unit(m, 40, 2, zf, "steel")
    vents(m, y, hh, zf, -0.2, 0.2, 14)
    m.box((0.06, 0.03, 0.02), (0.22, 0.13, zf + 0.008), "em_orange")


@_add(RK, "armored data rack")
def _(m, rng):
    W, D, H = 0.7, 1.0, 2.0
    m.box((W, H, D), (0, H / 2, 0), "gunmetal", 0.02)
    m.box((W - 0.06, H - 0.16, 0.05), (0, H / 2, D / 2 + 0.02), "hull_dark", 0.015)
    for k in range(3):
        m.box((W - 0.06, 0.03, 0.03), (0, 0.4 + k * 0.6, D / 2 + 0.07), "steel", 0.006)
    for sx in (-1, 1):
        for k in range(4):
            m.box((0.05, 0.07, 0.04), (sx * (W / 2 - 0.02), 0.25 + k * 0.5, D / 2 + 0.05), "black_metal")
    m.cyl(0.16, 0.05, (0, 1.05, D / 2 + 0.07), "steel", axis="z", seg=16)
    m.cyl(0.05, 0.08, (0, 1.05, D / 2 + 0.12), "chrome", axis="z", seg=8)
    for a in (0, 2.09, 4.19):
        m.link((0, 1.05, D / 2 + 0.13), (math.cos(a + 0.5) * 0.14, 1.05 + math.sin(a + 0.5) * 0.14, D / 2 + 0.13), 0.01, "chrome", seg=5)
    m.box((0.12, 0.2, 0.02), (0.22, 1.05, D / 2 + 0.1), "black_metal")
    for r in range(4):
        for c in range(3):
            m.box((0.02, 0.02, 0.01), (0.19 + c * 0.03, 1.1 - r * 0.03, D / 2 + 0.115), "plastic_grey")
    led(m, (0.22, 1.18, D / 2 + 0.115), "em_red")
    hazard(m, 0, 0.18, D / 2 + 0.05, 0.5, 0.08)
    m.screen((0.24, 0.1), (-0.2, 1.5, D / 2 + 0.05), "alert", bezel=0.008)
    m.cyl(0.04, 0.05, (0, H + 0.02, 0), "em_red", seg=8)


@_add(RK, "photonic fiber rack")
def _(m, rng):
    zf = rack_frame(m, side="cm_rack")
    m.box((0.5, 1.75, 0.02), (0, 1.02, zf - 0.3), "black_metal")
    m.box((0.46, 1.6, 0.012), (0, 1.02, zf + 0.0), "glass_dark")
    # fibre bundles emerging from central spine
    m.cyl(0.03, 1.6, (0, 1.02, zf - 0.16), "brushed_alu", seg=8)
    for k in range(14):
        y = 0.35 + k * 0.11
        side = -1 if k % 2 else 1
        col = ["em_cyan", "em_violet", "em_blue", "em_white"][k % 4]
        m.tube([(0, y, zf - 0.16), (side * 0.12, y + 0.04, zf - 0.12), (side * 0.2, y - 0.02, zf - 0.14)], 0.006, col, seg=4)
        m.box((0.09, 0.05, 0.05), (side * 0.2, y - 0.02, zf - 0.14), "gunmetal")
        led(m, (side * 0.2, y - 0.02, zf - 0.105), LEDC[k % 6], 0.014)
    for k in range(4):
        m.torus(0.06, 0.008, (0, 0.5 + k * 0.4, zf - 0.16), "gold_trim", seg=10, tseg=4)
    m.box((0.3, 0.1, 0.01), (0, 0.16, zf + 0.008), "black_metal")
    m.screen((0.26, 0.07), (0, 0.16, zf + 0.014), "waveform")
    m.box((0.5, 0.04, 0.02), (0, 1.94, zf + 0.0), "em_violet")


_reg("rack", RK, mount="floor", tags=TAGC + ["rack"], solid=True)

# ==========================================================================
# STORAGE
# ==========================================================================
SG = {}
SGT = {}


@_add(SG, "data crystal vault")
def _(m, rng):
    m.cyl(0.6, 0.15, (0, 0.075, 0), "hull_dark", seg=8, bevel=0.01)
    m.cyl(0.5, 0.05, (0, 0.175, 0), "gold_trim", seg=8)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        m.box((0.05, 1.5, 0.05), (math.cos(a) * 0.5, 0.95, math.sin(a) * 0.5), "gold_trim", 0.006)
        a2 = a + math.pi / 8
        m.box((0.38, 1.4, 0.012), (math.cos(a2) * 0.46, 0.95, math.sin(a2) * 0.46), "glass_blue", 0, rot=(0, -a2 + math.pi / 2, 0))
    m.cyl(0.6, 0.1, (0, 1.75, 0), "hull_dark", seg=8, bevel=0.01)
    m.cyl(0.1, 1.5, (0, 0.95, 0), "hull_mid", seg=8)
    for k in range(7):
        y = 0.35 + k * 0.2
        m.cyl(0.3, 0.02, (0, y - 0.08, 0), "steel", seg=12)
        for j in range(4):
            a = j * 1.571 + k * 0.6
            m.box((0.05, 0.14, 0.12), (math.cos(a) * 0.2, y, math.sin(a) * 0.2), ["cm_crystal", "cm_crystal2", "cm_crystal3"][(k + j) % 3], rot=(0, -a, 0.15))
    m.cyl(0.12, 0.2, (0, 1.9, 0), "gold_trim", seg=8, r2=0.05)
    m.sphere(0.07, (0, 2.05, 0), "cm_crystal", seg=8, ring=6)


@_add(SG, "holo storage cylinder")
def _(m, rng):
    m.cyl(0.45, 0.2, (0, 0.1, 0), "hull_dark", seg=20, r2=0.4, bevel=0.01)
    m.torus(0.42, 0.02, (0, 0.21, 0), "em_blue", seg=20, tseg=4)
    m.cyl(0.38, 1.5, (0, 1.0, 0), "glass", seg=16)
    m.cyl(0.03, 1.5, (0, 1.0, 0), "chrome", seg=6)
    for k in range(5):
        y = 0.45 + k * 0.28
        m.torus(0.25, 0.014, (0, y, 0), ["em_cyan", "em_blue", "em_violet"][k % 3], seg=14, tseg=3)
        m.box((0.1, 0.03, 0.02), (math.cos(k) * 0.25, y, math.sin(k) * 0.25), "em_white", rot=(0, -k, 0))
    m.cyl(0.45, 0.14, (0, 1.82, 0), "hull_dark", seg=20, r2=0.35)
    m.cyl(0.2, 0.1, (0, 1.94, 0), "gunmetal", seg=12)
    for k in range(4):
        a = k * 1.571 + 0.785
        m.box((0.03, 1.5, 0.03), (math.cos(a) * 0.39, 1.0, math.sin(a) * 0.39), "steel")
    m.box((0.3, 0.12, 0.02), (0, 0.1, 0.44), "black_metal", rot=(-0.2, 0, 0))
    m.screen((0.24, 0.07), (0, 0.1, 0.455), "bars", rot=(-0.2, 0, 0))


@_add(SG, "archive robot")
def _(m, rng):
    W, D, H = 1.8, 0.9, 2.0
    for sz in (-1, 1):
        m.box((W, H, 0.3), (0, H / 2, sz * 0.3), "hull_dark", 0.01)
        for r in range(7):
            for c in range(6):
                col = ["paint_red", "paint_blue", "paint_grey", "paint_teal", "paint_white"][(r * 2 + c) % 5]
                m.box((0.22, 0.14, 0.02), (-0.7 + c * 0.28, 0.3 + r * 0.24, sz * 0.3 + sz * 0.145), col)
    # rail and mast
    m.box((W, 0.06, 0.12), (0, 0.08, 0), "steel")
    m.box((W, 0.06, 0.12), (0, H - 0.05, 0), "steel")
    m.box((0.14, H - 0.2, 0.1), (0.3, H / 2, 0), "paint_orange", 0.01)
    m.box((0.3, 0.3, 0.3), (0.3, 1.0, 0), "hull_light", 0.015)
    m.box((0.3, 0.04, 0.5), (0.3, 1.0, 0), "steel")
    m.box((0.26, 0.04, 0.12), (0.3, 1.0, 0.26), "chrome")
    m.box((0.26, 0.04, 0.12), (0.3, 1.0, -0.26), "chrome")
    led(m, (0.3, 1.08, 0.0), "em_green", 0.02)
    for sx in (-1, 1):
        m.box((0.08, H, 0.72), (sx * (W / 2 - 0.04), H / 2, 0), "black_metal", 0.008)
    m.box((0.5, 0.2, 0.02), (-0.4, 1.85, 0.46), "black_metal")
    m.screen((0.42, 0.12), (-0.4, 1.85, 0.47), "systems")


@_add(SG, "memory core column")
def _(m, rng):
    m.cyl(0.42, 0.15, (0, 0.075, 0), "hull_dark", seg=16, bevel=0.008)
    for k in range(7):
        y = 0.2 + k * 0.26
        m.cyl(0.3, 0.2, (0, y, 0), ["hull_mid", "hull_dark"][k % 2], seg=12)
        m.torus(0.3, 0.014, (0, y + 0.11, 0), ["em_cyan", "em_green", "em_blue"][k % 3], seg=12, tseg=3)
        for j in range(3):
            a = j * 1.571 + k * 0.4
            m.box((0.08, 0.1, 0.02), (math.cos(a) * 0.3, y, math.sin(a) * 0.3), "black_metal", rot=(0, -a + 1.5708, 0))
    m.cyl(0.36, 0.12, (0, 2.0, 0), "hull_dark", seg=12, r2=0.2)
    m.cyl(0.08, 0.3, (0, 2.2, 0), "steel", seg=8)
    m.sphere(0.1, (0, 2.42, 0), "cm_crystal", seg=10, ring=7)
    for k in range(3):
        a = k * 2.094
        m.link((math.cos(a) * 0.38, 0.14, math.sin(a) * 0.38), (math.cos(a) * 0.15, 0.6, math.sin(a) * 0.15), 0.02, "copper", seg=5)


@_add(SG, "cold storage locker")
def _(m, rng):
    W, D, H = 1.2, 0.6, 1.9
    m.box((W, H, D), (0, H / 2, 0), "cm_ice", 0.02)
    m.box((W - 0.04, 0.08, D - 0.04), (0, 0.04, 0), "black_metal")
    for r in range(4):
        for c in range(3):
            x = -0.38 + c * 0.38
            y = 0.35 + r * 0.42
            m.box((0.36, 0.38, 0.03), (x, y, D / 2 + 0.005), "hull_mid", 0.008)
            handle(m, x, y + 0.13, D / 2 + 0.03, True, 0.16)
            m.box((0.1, 0.04, 0.01), (x - 0.1, y - 0.1, D / 2 + 0.022), "black_metal")
            m.box((0.06, 0.02, 0.006), (x - 0.1, y - 0.1, D / 2 + 0.028), "em_cyan" if (r + c) % 3 else "em_amber")
            m.box((0.05, 0.02, 0.008), (x + 0.1, y - 0.1, D / 2 + 0.022), "glass_blue")
    m.box((W - 0.06, 0.04, 0.02), (0, 1.9 - 0.06, D / 2 + 0.01), "em_blue")
    m.cyl(0.05, 0.12, (0.4, H + 0.06, -0.15), "steel", seg=8)
    m.cyl(0.05, 0.12, (-0.4, H + 0.06, -0.15), "steel", seg=8)


@_add(SGT, "black box recorder")
def _(m, rng):
    m.box((0.32, 0.03, 0.22), (0, 0.015, 0), "steel", 0.006)
    m.box((0.26, 0.14, 0.16), (0, 0.1, 0), "cm_orange", 0.02)
    for sx in (-1, 1):
        m.box((0.02, 0.145, 0.165), (sx * 0.06, 0.1, 0), "paint_white")
    m.cyl(0.028, 0.06, (0.16, 0.06, 0), "steel", axis="x", seg=10)
    m.box((0.12, 0.05, 0.005), (0, 0.11, 0.082), "black_metal")
    m.cyl(0.03, 0.04, (-0.16, 0.05, 0.02), "black_metal", axis="x", seg=8)
    led(m, (0.06, 0.16, 0.08), "em_amber", 0.014)
    m.cyl(0.025, 0.02, (0, 0.18, 0), "em_amber", seg=8)
@_add(SG, "secure data safe")
def _(m, rng):
    W, D, H = 0.9, 0.7, 1.3
    m.box((W, H, D), (0, H / 2 + 0.05, 0), "gunmetal", 0.03)
    m.box((W + 0.02, 0.05, D + 0.02), (0, 0.025, 0), "black_metal")
    m.box((W - 0.16, H - 0.16, 0.05), (0, H / 2 + 0.05, D / 2 + 0.01), "hull_dark", 0.02)
    m.cyl(0.2, 0.06, (-0.08, 0.75, D / 2 + 0.05), "steel", axis="z", seg=16)
    m.cyl(0.05, 0.05, (-0.08, 0.75, D / 2 + 0.1), "chrome", axis="z", seg=8)
    for a in range(5):
        aa = a * 1.257
        m.link((-0.08, 0.75, D / 2 + 0.11), (-0.08 + math.cos(aa) * 0.16, 0.75 + math.sin(aa) * 0.16, D / 2 + 0.11), 0.01, "chrome", seg=5)
    m.box((0.14, 0.24, 0.02), (0.26, 0.9, D / 2 + 0.05), "black_metal")
    for r in range(4):
        for c in range(3):
            m.box((0.03, 0.03, 0.01), (0.21 + c * 0.05, 0.98 - r * 0.045, D / 2 + 0.065), "plastic_grey")
    led(m, (0.26, 1.03, D / 2 + 0.065), "em_red")
    m.screen((0.1, 0.03), (0.26, 0.77, D / 2 + 0.065), "text")
    for k in range(3):
        m.cyl(0.03, 0.06, (W / 2 - 0.02, 0.4 + k * 0.4, D / 2 - 0.06), "steel", axis="z", seg=8)
    hazard(m, 0, 0.25, D / 2 + 0.04, 0.5, 0.06)
    m.box((0.35, 0.015, 0.02), (0.0, 1.25, D / 2 + 0.03), "brass")


@_add(SG, "cartridge library shelves")
def _(m, rng):
    W, D, H = 1.2, 0.45, 1.9
    for sx in (-1, 1):
        m.box((0.04, H, D), (sx * (W / 2 - 0.02), H / 2, 0), "steel")
    m.box((W, H, 0.02), (0, H / 2, -D / 2 + 0.01), "hull_dark")
    for r in range(7):
        y = 0.1 + r * 0.27
        m.box((W - 0.06, 0.02, D), (0, y, 0), "steel")
        for c in range(7):
            col = ["paint_red", "paint_blue", "paint_teal", "paint_gold", "paint_grey", "paint_green"][(r + c * 2) % 6]
            m.box((0.11, 0.2, 0.3), (-0.42 + c * 0.14, y + 0.11, 0.06), "black_metal")
            m.box((0.1, 0.06, 0.005), (-0.42 + c * 0.14, y + 0.16, 0.213), col)
            if (c + r) % 4 == 0:
                led(m, (-0.42 + c * 0.14, y + 0.06, 0.213), "em_green", 0.014)
    m.box((W, 0.06, D), (0, H + 0.03, 0), "steel", 0.006)


_reg("storage", SG, mount="floor", tags=TAGC + ["storage"], solid=True)
_reg("storage", SGT, mount="table", tags=TAGC + ["storage"], solid=False)

# ==========================================================================
# ANTENNAS
# ==========================================================================
AF = {}
AW = {}
AC = {}


@_add(AF, "satellite dish pedestal")
def _(m, rng):
    m.cyl(0.5, 0.15, (0, 0.075, 0), "hull_dark", seg=16, bevel=0.01)
    m.cyl(0.2, 0.9, (0, 0.6, 0), "hull_mid", seg=12, r2=0.15)
    m.cyl(0.25, 0.14, (0, 1.12, 0), "gunmetal", seg=12)
    for sx in (-1, 1):
        m.box((0.06, 0.6, 0.2), (sx * 0.3, 1.45, -0.05), "hull_dark", 0.01)
    m.cyl(0.04, 0.7, (0, 1.65, -0.05), "steel", axis="x", seg=8)
    dish(m, (0, 1.75, 0.1), 0.85, rot=(-0.7, 0, 0), depth=0.14)
    m.box((0.3, 0.16, 0.2), (0.48, 0.2, 0.3), "hull_mid", 0.01)
    leds(m, 0.4, 0.22, 0.4, 3, 0.05, ["em_green", "em_amber"])
    m.cyl(0.03, 0.2, (-0.3, 0.2, 0.3), "brass", seg=8)


@_add(AF, "dish array demo")
def _(m, rng):
    m.box((2.0, 0.12, 1.2), (0, 0.06, 0), "hull_dark", 0.015)
    hazard(m, 0, 0.06, 0.61, 1.6, 0.06)
    cfg = [(-0.7, 0.9, 0.34, (-0.5, 0.4, 0)), (0.0, 1.3, 0.45, (-0.6, 0, 0)), (0.7, 0.9, 0.34, (-0.5, -0.4, 0))]
    for x, h, r, rot in cfg:
        m.cyl(0.06, h, (x, 0.12 + h / 2, -0.1), "steel", seg=8)
        m.cyl(0.14, 0.05, (x, 0.145, -0.1), "hull_mid", seg=10)
        m.box((0.16, 0.1, 0.14), (x, 0.12 + h + 0.02, -0.1), "gunmetal", 0.01)
        dish(m, (x, 0.12 + h + 0.12, -0.05), r, rot=rot)
    m.box((0.5, 0.2, 0.3), (0.0, 0.22, 0.35), "hull_mid", 0.01)
    m.screen((0.34, 0.1), (0, 0.24, 0.502), "comm", bezel=0.008)
    m.tube([(-0.7, 0.14, -0.1), (-0.5, 0.13, 0.3), (-0.25, 0.2, 0.35)], 0.012, "black_metal", seg=5)
    m.tube([(0.7, 0.14, -0.1), (0.5, 0.13, 0.3), (0.25, 0.2, 0.35)], 0.012, "black_metal", seg=5)


@_add(AF, "lattice mast")
def _(m, rng):
    H = 3.0
    m.box((0.9, 0.1, 0.9), (0, 0.05, 0), "concrete", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.link((sx * 0.35, 0.1, sz * 0.35), (sx * 0.08, H, sz * 0.08), 0.022, "steel", seg=5)
    levels = [0.1 + k * (H - 0.1) / 6 for k in range(7)]
    for a, b in zip(levels[:-1], levels[1:]):
        ra = 0.35 - (a - 0.1) / (H - 0.1) * 0.27
        rb = 0.35 - (b - 0.1) / (H - 0.1) * 0.27
        for s, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
            n = (1, 1), (-1, 1), (-1, -1), (1, -1)
            nx, nz = n[(s + 1) % 4]
            m.link((sx * ra, a, sz * ra), (nx * rb, b, nz * rb), 0.008, "steel", seg=4)
        for (sx, sz) in ((1, 1), (-1, -1)):
            pass
    for k, y in enumerate(levels[1:-1]):
        r = 0.35 - (y - 0.1) / (H - 0.1) * 0.27
        m.box((2 * r, 0.012, 0.012), (0, y, r), "steel")
        m.box((2 * r, 0.012, 0.012), (0, y, -r), "steel")
    m.box((0.4, 0.05, 0.4), (0, H + 0.02, 0), "steel")
    m.cyl(0.015, 0.7, (0, H + 0.4, 0), "chrome", seg=5)
    m.sphere(0.05, (0, H + 0.1, 0), "em_red", seg=8, ring=6)
    # yagi + cross dipoles
    for k, yy in enumerate((2.3, 2.6)):
        m.link((0, yy, 0.1), (0, yy, 0.7), 0.01, "brushed_alu", seg=4)
        for j in range(4):
            w = 0.34 - j * 0.05
            m.link((-w / 2, yy, 0.2 + j * 0.14), (w / 2, yy, 0.2 + j * 0.14), 0.006, "chrome", seg=4)
    m.link((0.1, 1.5, 0.1), (0.5, 1.7, 0.1), 0.01, "steel", seg=4)
    dish(m, (0.55, 1.75, 0.25), 0.22, rot=(0, 0.5, 0))
    m.box((0.2, 0.3, 0.14), (0.0, 0.25, 0.5), "hull_mid", 0.01)


@_add(AF, "whip antenna cluster")
def _(m, rng):
    m.box((0.6, 0.06, 0.5), (0, 0.03, 0), "hull_dark", 0.01)
    m.box((0.3, 0.12, 0.26), (0, 0.12, 0), "gunmetal", 0.012)
    heights = [1.9, 1.5, 1.2, 1.7, 0.9]
    pos = [(0, 0), (-0.18, 0.12), (0.18, 0.12), (-0.15, -0.14), (0.16, -0.14)]
    for k, (h, (x, z)) in enumerate(zip(heights, pos)):
        m.cyl(0.03, 0.1, (x, 0.13 + 0.05 + (0.06 if k == 0 else 0), z), "black_metal", seg=8)
        m.cyl(0.011, h, (x, 0.2 + h / 2, z), "carbon", seg=5, r2=0.004)
        m.cyl(0.02, 0.03, (x, 0.28, z), "steel", seg=6)
        m.sphere(0.015, (x, 0.2 + h, z), "chrome", seg=6, ring=4)
        if k % 2 == 0:
            m.cyl(0.018, 0.04, (x, 0.2 + h * 0.6, z), "hazard_yellow", seg=6)
    leds(m, -0.1, 0.12, 0.134, 3, 0.05, ["em_green", "em_amber"])


@_add(AF, "subspace relay coil")
def _(m, rng):
    m.cyl(0.4, 0.12, (0, 0.06, 0), "hull_dark", seg=16, bevel=0.008)
    m.torus(0.35, 0.02, (0, 0.14, 0), "em_violet", seg=18, tseg=4)
    m.cyl(0.14, 1.9, (0, 1.05, 0), "hull_mid", seg=10)
    for k in range(7):
        m.torus(0.22, 0.035, (0, 0.35 + k * 0.23, 0), "copper", seg=12, tseg=4)
    for k in range(3):
        a = k * 2.094
        m.cyl(0.03, 1.5, (math.cos(a) * 0.3, 0.9, math.sin(a) * 0.3), "gunmetal", seg=6)
        m.link((math.cos(a) * 0.3, 1.65, math.sin(a) * 0.3), (math.cos(a) * 0.18, 1.85, math.sin(a) * 0.18), 0.02, "gunmetal", seg=5)
    m.cyl(0.25, 0.06, (0, 2.03, 0), "gold_trim", seg=14)
    m.cyl(0.05, 0.14, (0, 2.13, 0), "steel", seg=8)
    m.sphere(0.13, (0, 2.3, 0), "cm_crystal2", seg=10, ring=6)
    m.torus(0.19, 0.012, (0, 2.3, 0), "em_violet", axis="x", seg=12, tseg=3)
    m.torus(0.19, 0.012, (0, 2.3, 0), "em_violet", axis="z", seg=12, tseg=3)
    m.box((0.3, 0.14, 0.06), (0, 0.15, 0.42), "hull_dark", 0.008, rot=(-0.3, 0, 0))
    m.screen((0.24, 0.08), (0, 0.155, 0.455), "waveform", rot=(-0.3, 0, 0))


@_add(AW, "phased array panel")
def _(m, rng):
    m.box((1.3, 1.3, 0.06), (0, 0, 0.03), "hull_dark")
    m.box((1.2, 1.2, 0.02), (0, 0, 0.07), "black_metal")
    for a in range(5):
        for b in range(5):
            x = -0.48 + a * 0.24
            y = -0.48 + b * 0.24
            m.box((0.18, 0.18, 0.03), (x, y, 0.095), "gunmetal")
            m.box((0.06, 0.06, 0.01), (x, y, 0.115), "em_cyan" if (a + b) % 4 == 0 else "gold_trim")
    bolts(m, [(-0.6, 0.6), (0.6, 0.6), (-0.6, -0.6), (0.6, -0.6)], 0.065)
    m.box((0.24, 0.18, 0.1), (0, -0.74, 0.05), "hull_mid", 0.01)
    leds(m, -0.06, -0.74, 0.102, 3, 0.06, ["em_green", "em_amber", "em_cyan"], 0.02)
    m.tube([(0, -0.82, 0.05), (0, -0.9, 0.1)], 0.02, "black_metal", seg=5)


@_add(AW, "feed horn panel")
def _(m, rng):
    m.box((1.0, 0.7, 0.1), (0, 0, 0.05), "hull_mid", 0.015)
    m.box((0.9, 0.6, 0.02), (0, 0, 0.11), "hull_dark", 0.01)
    for k in range(3):
        x = -0.3 + k * 0.3
        m.cyl(0.11, 0.24, (x, 0.05, 0.24), "brushed_alu", axis="z", seg=4, r2=0.06, rot=(0, 0, 0.785))
        m.cyl(0.07, 0.03, (x, 0.05, 0.135), "black_metal", axis="z", seg=8)
        m.box((0.08, 0.06, 0.05), (x, -0.18, 0.15), "gunmetal", 0.008)
        m.cyl(0.02, 0.05, (x, -0.24, 0.15), "brass", seg=6)
        led(m, (x, -0.18, 0.178), LEDC[k])
    m.box((1.0, 0.03, 0.03), (0, 0.33, 0.115), "hazard_yellow")
    bolts(m, [(-0.45, 0.28), (0.45, 0.28), (-0.45, -0.28), (0.45, -0.28)], 0.12)


@_add(AW, "relay box")
def _(m, rng):
    m.box((0.5, 0.4, 0.2), (0, 0, 0.1), "hull_mid", 0.02)
    m.box((0.46, 0.36, 0.02), (0, 0, 0.21), "hull_dark", 0.01)
    m.screen((0.2, 0.1), (-0.08, 0.08, 0.225), "comm", bezel=0.008)
    leds(m, -0.16, -0.06, 0.222, 5, 0.06, ["em_green", "em_amber", "em_cyan"], 0.02)
    for sx in (-1, 1):
        m.cyl(0.012, 0.5, (sx * 0.16, 0.45, 0.1), "black_metal", seg=6)
        m.cyl(0.03, 0.05, (sx * 0.16, 0.22, 0.1), "black_metal", seg=8)
    m.cyl(0.03, 0.14, (0.19, -0.27, 0.12), "steel", seg=8)
    m.cyl(0.03, 0.14, (-0.19, -0.27, 0.12), "steel", seg=8)
    m.cyl(0.03, 0.2, (0.0, 0.3, 0.05), "steel", seg=6, rot=(0, 0, 0))
    m.box((0.12, 0.08, 0.02), (0.14, 0.08, 0.225), "hazard_yellow")


_reg("antenna", AF, mount="floor", tags=TAGC + ["antenna"], solid=True)
_reg("antenna", AW, mount="wall", tags=TAGC + ["antenna"], solid=False)


@_add(AC, "ceiling antenna pod")
def _(m, rng):
    m.cyl(0.35, 0.05, (0, -0.025, 0), "hull_dark", seg=16, bevel=0.006)
    m.cyl(0.25, 0.14, (0, -0.12, 0), "hull_mid", seg=16, r2=0.3)
    m.sphere(0.24, (0, -0.19, 0), "paint_white", seg=16, ring=8, scale=(1, 0.7, 1))
    m.torus(0.26, 0.012, (0, -0.19, 0), "em_cyan", seg=16, tseg=4)
    m.cyl(0.02, 0.35, (0, -0.4, 0), "chrome", seg=6, r2=0.005)
    for k in range(3):
        a = k * 2.094 + 0.3
        m.cyl(0.02, 0.1, (math.cos(a) * 0.27, -0.12, math.sin(a) * 0.27), "gunmetal", seg=6)
        led(m, (math.cos(a) * 0.32, -0.12, math.sin(a) * 0.32), "em_green", 0.02)


@_add(AC, "ceiling log periodic")
def _(m, rng):
    m.box((0.3, 0.05, 0.3), (0, -0.025, 0), "hull_dark", 0.008)
    m.box((0.08, 0.2, 0.08), (0, -0.15, 0), "gunmetal", 0.008)
    m.box((0.05, 0.05, 1.3), (0, -0.28, 0.35), "brushed_alu", 0.006)
    for k in range(7):
        w = 0.9 - k * 0.11
        z = -0.25 + k * 0.2
        m.link((-w / 2, -0.28, z), (w / 2, -0.28, z), 0.01, "chrome", seg=5)
        m.sphere(0.014, (-w / 2, -0.28, z), "chrome", seg=5, ring=4)
        m.sphere(0.014, (w / 2, -0.28, z), "chrome", seg=5, ring=4)
    m.box((0.1, 0.06, 0.1), (0, -0.28, -0.35), "hull_mid", 0.008)
    led(m, (0, -0.31, -0.35), "em_green", 0.02)


_reg("antenna", AC, mount="ceiling", tags=TAGC + ["antenna"], solid=False)

# ==========================================================================
# COMMS UNITS
# ==========================================================================
CT = {}
CW = {}
CF = {}


@_add(CT, "handset cradle")
def _(m, rng):
    m.box((0.22, 0.06, 0.26), (0, 0.03, 0), "plastic_black", 0.012)
    m.box((0.2, 0.08, 0.04), (0, 0.1, -0.08), "plastic_black", 0.01, rot=(-0.3, 0, 0))
    for r in range(3):
        for c in range(3):
            m.box((0.025, 0.008, 0.02), (-0.05 + c * 0.05, 0.066, 0.07 + r * 0.045), "plastic_grey")
    m.screen((0.11, 0.05), (0, 0.062, 0.0), "text", rot=(-1.4, 0, 0), bezel=0.006)
    # cradle uprights + handset
    for sx in (-1, 1):
        m.box((0.03, 0.07, 0.06), (sx * 0.075, 0.13, -0.1), "plastic_black", 0.008)
    m.box((0.2, 0.04, 0.05), (0, 0.15, -0.1), "plastic_grey", 0.015)
    m.box((0.05, 0.05, 0.06), (-0.085, 0.15, -0.1), "plastic_grey", 0.015)
    m.box((0.05, 0.05, 0.06), (0.085, 0.15, -0.1), "plastic_grey", 0.015)
    led(m, (0.0, 0.176, -0.1), "em_green", 0.012)
    coil = [(0.1, 0.05, -0.1), (0.12, 0.04, -0.03), (0.13, 0.03, 0.03), (0.16, 0.02, 0.09)]
    for k in range(6):
        m.torus(0.012, 0.004, (0.13, 0.04, -0.08 + k * 0.03), "plastic_black", axis="x", seg=6, tseg=3)
    m.tube([(0.1, 0.06, -0.1), (0.13, 0.04, -0.08), (0.13, 0.04, 0.06)], 0.005, "plastic_black", seg=4)


@_add(CT, "radio transceiver")
def _(m, rng):
    m.box((0.42, 0.16, 0.26), (0, 0.08, 0), "hull_dark", 0.012)
    m.box((0.4, 0.14, 0.008), (0, 0.08, 0.13), "black_metal")
    m.screen((0.16, 0.05), (-0.09, 0.11, 0.136), "waveform", bezel=0.006)
    m.cyl(0.04, 0.03, (0.12, 0.09, 0.145), "chrome", axis="z", seg=12)
    m.cyl(0.015, 0.01, (0.12, 0.09, 0.165), "black_metal", axis="z", seg=6)
    for k in range(2):
        m.cyl(0.018, 0.02, (0.01 + k * 0.05, 0.04, 0.14), "black_metal", axis="z", seg=8)
    for k in range(4):
        m.box((0.02, 0.014, 0.006), (-0.17 + k * 0.04, 0.04, 0.137), ["paint_red", "paint_green", "paint_blue", "paint_orange"][k])
    m.cyl(0.006, 0.4, (-0.17, 0.3, -0.1), "chrome", seg=4, r2=0.004)
    m.cyl(0.02, 0.04, (-0.17, 0.18, -0.1), "black_metal", seg=6)
    # mic on stand
    m.cyl(0.05, 0.02, (0.3, 0.01, 0.05), "black_metal", seg=10)
    m.cyl(0.008, 0.16, (0.3, 0.1, 0.05), "chrome", seg=4)
    m.box((0.05, 0.05, 0.07), (0.3, 0.2, 0.05), "gunmetal", 0.012)
    m.box((0.04, 0.008, 0.02), (0.3, 0.2, 0.09), "em_red")
    led(m, (0.17, 0.14, 0.135), "em_green")
    leds(m, 0.15, 0.04, 0.136, 1, 0, ["em_amber"])


@_add(CT, "signal booster")
def _(m, rng):
    m.box((0.34, 0.1, 0.24), (0, 0.05, 0), "hull_dark", 0.012)
    for k in range(7):
        m.box((0.012, 0.06, 0.2), (-0.13 + k * 0.043, 0.13, -0.0), "brushed_alu")
    m.box((0.34, 0.012, 0.22), (0, 0.098, 0), "steel")
    for sx in (-0.12, 0.0, 0.12):
        m.cyl(0.014, 0.05, (sx, 0.125, -0.09), "chrome", seg=6)
        m.cyl(0.008, 0.28 - abs(sx), (sx, 0.29, -0.09), "black_metal", seg=5)
    m.box((0.3, 0.06, 0.008), (0, 0.06, 0.124), "black_metal")
    leds(m, -0.1, 0.07, 0.13, 5, 0.05, ["em_green", "em_green", "em_amber", "em_cyan", "em_green"], 0.014)
    m.cyl(0.018, 0.06, (0.19, 0.05, 0.05), "brass", axis="x", seg=8)
    m.cyl(0.018, 0.06, (-0.19, 0.05, 0.05), "brass", axis="x", seg=8)
    m.box((0.08, 0.02, 0.008), (0.1, 0.03, 0.124), "hazard_yellow")


@_add(CT, "encryption unit")
def _(m, rng):
    m.box((0.32, 0.14, 0.26), (0, 0.07, 0), "gunmetal", 0.015)
    m.box((0.3, 0.02, 0.24), (0, 0.15, 0), "hull_dark", 0.006)
    m.box((0.12, 0.09, 0.008), (0.08, 0.08, 0.134), "black_metal")
    for r in range(3):
        for c in range(3):
            m.box((0.02, 0.02, 0.008), (0.045 + c * 0.035, 0.105 - r * 0.028, 0.14), "plastic_grey")
    m.screen((0.13, 0.05), (-0.08, 0.1, 0.137), "text", bezel=0.005)
    m.cyl(0.02, 0.02, (-0.08, 0.04, 0.14), "brass", axis="z", seg=8)
    m.box((0.008, 0.03, 0.01), (-0.08, 0.04, 0.152), "black_metal")
    hazard(m, 0.0, 0.025, 0.134, 0.28, 0.03)
    led(m, (-0.13, 0.12, 0.134), "em_red")
    led(m, (-0.11, 0.12, 0.134), "em_green")
    m.cyl(0.03, 0.05, (0.0, 0.175, -0.06), "steel", seg=8)


_reg("commsunit", CT, mount="table", tags=TAGC + ["comms"], solid=False)


@_add(CW, "intercom panel")
def _(m, rng):
    m.box((0.22, 0.34, 0.04), (0, 0, 0.02), "hull_mid", 0.012)
    m.box((0.18, 0.11, 0.008), (0, 0.09, 0.044), "black_metal")
    for k in range(5):
        m.box((0.13, 0.006, 0.006), (0, 0.06 + k * 0.02, 0.05), "steel")
    m.screen((0.14, 0.05), (0, -0.01, 0.043), "comm", bezel=0.006)
    m.cyl(0.03, 0.02, (-0.05, -0.09, 0.05), "paint_green", axis="z", seg=10)
    m.cyl(0.03, 0.02, (0.05, -0.09, 0.05), "paint_red", axis="z", seg=10)
    m.cyl(0.008, 0.01, (0, -0.14, 0.045), "black_metal", axis="z", seg=6)
    led(m, (0.08, 0.14, 0.045), "em_green", 0.014)
    bolts(m, [(-0.09, 0.15), (0.09, 0.15), (-0.09, -0.15), (0.09, -0.15)], 0.04)


@_add(CW, "speaker grille")
def _(m, rng):
    m.box((0.6, 0.3, 0.08), (0, 0, 0.04), "hull_dark", 0.015)
    m.box((0.5, 0.2, 0.02), (0, 0, 0.085), "black_metal")
    for k in range(9):
        m.box((0.48, 0.012, 0.014), (0, -0.09 + k * 0.0225, 0.098), "steel")
    led(m, (0.26, 0.12, 0.09), "em_amber", 0.02)
    bolts(m, [(-0.27, 0.12), (0.27, 0.12), (-0.27, -0.12), (0.27, -0.12)], 0.082)


@_add(CW, "wall microphone")
def _(m, rng):
    m.box((0.16, 0.2, 0.03), (0, 0, 0.015), "hull_mid", 0.01)
    m.cyl(0.05, 0.02, (0, -0.02, 0.04), "plastic_black", axis="z", seg=10)
    m.cyl(0.03, 0.02, (0, -0.02, 0.055), "paint_red", axis="z", seg=10)
    m.tube([(0, 0.03, 0.04), (0, 0.06, 0.1), (0, 0.06, 0.2), (0, 0.03, 0.27)], 0.008, "chrome", seg=5)
    m.cyl(0.02, 0.09, (0, 0.03, 0.31), "gunmetal", axis="z", seg=8)
    m.sphere(0.024, (0, 0.03, 0.36), "black_metal", seg=8, ring=6)
    m.torus(0.024, 0.004, (0, 0.03, 0.335), "em_red", axis="z", seg=8, tseg=3)
    led(m, (0.05, 0.07, 0.032), "em_green")


@_add(CW, "translator panel")
def _(m, rng):
    m.box((0.5, 0.36, 0.05), (0, 0, 0.025), "hull_light", 0.015)
    m.screen((0.32, 0.2), (-0.05, 0.03, 0.052), "globe", bezel=0.01)
    m.screen((0.32, 0.06), (-0.05, -0.12, 0.052), "text", bezel=0.006)
    for k in range(5):
        m.box((0.05, 0.03, 0.012), (0.19, 0.12 - k * 0.055, 0.056), ["paint_teal", "paint_blue", "paint_green", "paint_orange", "paint_red"][k], 0.004)
        led(m, (0.19, 0.12 - k * 0.055 + 0.0, 0.064), "em_white", 0.008)
    for k in range(4):
        m.cyl(0.012, 0.01, (-0.2 + k * 0.05, 0.16, 0.055), "black_metal", axis="z", seg=6)
    m.box((0.5, 0.012, 0.012), (0, -0.19, 0.056), "em_cyan")


_reg("commsunit", CW, mount="wall", tags=TAGC + ["comms"], solid=False)


@_add(CF, "comms console")
def _(m, rng):
    m.box((1.6, 0.75, 0.6), (0, 0.375, 0.0), "hull_dark", 0.02)
    m.box((1.66, 0.05, 0.66), (0, 0.775, 0.02), "hull_mid", 0.01)
    m.box((1.6, 0.03, 0.02), (0, 0.15, 0.31), "em_cyan")
    for k, x in enumerate((-0.5, 0.0, 0.5)):
        m.box((0.44, 0.03, 0.2), (x, 0.815, 0.18), "hull_dark", 0.006, rot=(0.0, 0, 0))
        for j in range(6):
            m.box((0.03, 0.02, 0.09), (x - 0.16 + j * 0.065, 0.84, 0.18), ["plastic_grey", "plastic_white"][j % 2], 0.003)
            m.box((0.03, 0.012, 0.012), (x - 0.16 + j * 0.065, 0.85, 0.24), LEDC[(j + k) % 6])
    m.box((0.06, 0.4, 0.06), (0, 1.0, -0.22), "gunmetal")
    for k, (x, rot) in enumerate(((-0.55, (-0.1, 0.3, 0)), (0.0, (-0.1, 0, 0)), (0.55, (-0.1, -0.3, 0)))):
        m.screen((0.5, 0.32), (x, 1.2, -0.1 - 0.08 * abs(x)), ["comm", "starmap", "waveform"][k], rot=rot, bezel=0.02)
    m.cyl(0.02, 0.1, (0.7, 0.85, 0.15), "gunmetal", seg=6)
    m.sphere(0.03, (0.7, 0.92, 0.15), "black_metal", seg=6, ring=4)
    m.box((0.12, 0.05, 0.1), (-0.72, 0.83, 0.1), "plastic_black", 0.01)
    m.torus(0.07, 0.01, (-0.72, 0.88, 0.1), "plastic_black", axis="x", seg=8, tseg=3, arc=math.pi)
    m.box((0.5, 0.4, 0.02), (0, 0.4, 0.31), "black_metal")
    leds(m, -0.2, 0.45, 0.32, 8, 0.05, LEDC)


@_add(CF, "radio rack")
def _(m, rng):
    W, D, H = 0.6, 0.5, 1.5
    for sx in (-1, 1):
        m.box((0.04, H, D), (sx * (W / 2 - 0.02), H / 2, 0), "gunmetal", 0.006)
    m.box((W, 0.06, D), (0, 0.03, 0), "black_metal")
    m.box((W, 0.04, D), (0, H - 0.02, 0), "black_metal")
    m.box((W - 0.08, H - 0.1, 0.02), (0, H / 2, -D / 2 + 0.01), "hull_dark")
    ys = [0.15, 0.38, 0.6, 0.86, 1.1]
    hs = [0.2, 0.2, 0.22, 0.24, 0.18]
    for k, (y, h) in enumerate(zip(ys, hs)):
        m.box((W - 0.08, h, D - 0.06), (0, y + h / 2, 0), ["hull_dark", "hull_mid"][k % 2], 0.008)
        z = D / 2 - 0.02
        m.box((W - 0.1, h - 0.02, 0.008), (0, y + h / 2, z), "black_metal")
        if k in (0, 2):
            m.screen((0.18, 0.06), (-0.14, y + h * 0.6, z + 0.006), "waveform" if k else "comm")
            for j in range(3):
                m.cyl(0.03, 0.02, (0.02 + j * 0.075, y + h * 0.5, z + 0.012), "chrome", axis="z", seg=10)
                m.cyl(0.01, 0.01, (0.02 + j * 0.075, y + h * 0.5, z + 0.024), "black_metal", axis="z", seg=5)
        elif k in (1, 4):
            m.cyl(0.07, 0.02, (-0.15, y + h / 2, z + 0.012), "black_metal", axis="z", seg=14)
            m.cyl(0.05, 0.015, (-0.15, y + h / 2, z + 0.02), "steel", axis="z", seg=12)
            leds(m, 0.0, y + h / 2, z + 0.012, 5, 0.05, LEDC, 0.016)
        else:
            m.box((0.34, 0.1, 0.006), (-0.06, y + h / 2, z + 0.006), "gunmetal")
            for j in range(9):
                m.box((0.01, 0.06, 0.004), (-0.2 + j * 0.033, y + h / 2, z + 0.01), "steel")
            m.cyl(0.03, 0.02, (0.2, y + h / 2, z + 0.012), "paint_red", axis="z", seg=8)
    m.cyl(0.006, 0.6, (-0.2, H + 0.3, -0.1), "chrome", seg=4, r2=0.004)
    m.cyl(0.02, 0.04, (-0.2, H + 0.02, -0.1), "black_metal", seg=6)
    m.link((0.2, H, -0.1), (0.2, H + 0.5, -0.1), 0.006, "chrome", seg=4)
    m.link((0.2, H + 0.5, -0.1), (0.05, H + 0.5, -0.1), 0.006, "chrome", seg=4)


_reg("commsunit", CF, mount="floor", tags=TAGC + ["comms"], solid=True)

# ==========================================================================
# ROUTERS / NETWORK
# ==========================================================================
RT = {}
RW = {}
RF = {}


@_add(RT, "network hub")
def _(m, rng):
    m.box((0.42, 0.06, 0.24), (0, 0.03, 0), "hull_dark", 0.01)
    m.box((0.4, 0.02, 0.22), (0, 0.07, 0), "hull_mid", 0.005)
    for k in range(8):
        x = -0.17 + k * 0.048
        m.box((0.03, 0.03, 0.02), (x, 0.045, 0.12), "plastic_black")
        led(m, (x - 0.008, 0.062, 0.123), LEDC[(k * 3) % 6], 0.007)
        led(m, (x + 0.008, 0.062, 0.123), "em_amber" if k % 3 == 0 else "em_green", 0.007)
    cols = ["cm_cable_y", "cm_cable_b", "cm_cable_g", "cm_cable_r"]
    for k in range(4):
        x = -0.17 + k * 0.096
        m.tube([(x, 0.045, 0.13), (x, 0.03, 0.2), (x + 0.05 * (k - 1.5), 0.01, 0.32)], 0.007, cols[k], seg=4)
    m.cyl(0.015, 0.03, (0.18, 0.09, -0.08), "black_metal", seg=6)
    m.box((0.1, 0.008, 0.06), (-0.1, 0.084, -0.04), "hull_dark")


@_add(RT, "cable modem")
def _(m, rng):
    m.box((0.2, 0.04, 0.16), (0, 0.02, 0), "plastic_black", 0.012)
    m.box((0.18, 0.15, 0.08), (0, 0.115, -0.03), "plastic_white", 0.02)
    for sx in (-1, 1):
        m.cyl(0.01, 0.2, (sx * 0.08, 0.3, -0.06), "plastic_black", seg=6, rot=(0, 0, -sx * 0.12))
        m.cyl(0.018, 0.04, (sx * 0.08, 0.2, -0.06), "plastic_black", seg=6)
    leds(m, -0.06, 0.13, 0.012, 4, 0.035, ["em_green", "em_blue", "em_green", "em_amber"], 0.014)
    for k in range(4):
        m.box((0.024, 0.016, 0.02), (-0.06 + k * 0.04, 0.03, 0.082), "gunmetal")
    m.box((0.14, 0.006, 0.006), (0, 0.075, 0.01), "black_metal")


_reg("router", RT, mount="table", tags=TAGC + ["network"], solid=False)


@_add(RW, "patch panel")
def _(m, rng):
    m.box((0.9, 0.16, 0.05), (0, 0, 0.025), "steel", 0.01)
    m.box((0.86, 0.12, 0.01), (0, 0, 0.055), "hull_dark")
    cols = ["cm_cable_y", "cm_cable_b", "cm_cable_g", "cm_cable_r"]
    for k in range(12):
        x = -0.4 + k * 0.073
        for r in range(2):
            m.box((0.03, 0.028, 0.02), (x, 0.03 - r * 0.06, 0.066), "black_metal")
        led(m, (x, 0.055, 0.062), "em_green" if k % 3 else "em_amber", 0.008)
    for k in range(6):
        x = -0.4 + k * 0.146
        p0 = (x, 0.03, 0.08)
        m.tube([p0, (x, 0.02, 0.15), (x + 0.1, -0.15, 0.2), (x + 0.07, -0.4, 0.05)], 0.008, cols[k % 4], seg=4)
    bolts(m, [(-0.42, 0.06), (0.42, 0.06), (-0.42, -0.06), (0.42, -0.06)], 0.058)
    m.box((0.9, 0.05, 0.1), (0, -0.45, 0.05), "gunmetal", 0.008)
@_add(RW, "fiber junction box")
def _(m, rng):
    m.box((0.5, 0.6, 0.12), (0, 0, 0.06), "hull_mid", 0.02)
    m.box((0.42, 0.5, 0.01), (0, 0, 0.125), "glass_dark")
    m.box((0.38, 0.46, 0.008), (0, 0, 0.118), "black_metal")
    for k in range(3):
        m.torus(0.06 + 0.03 * k, 0.005, (0, 0.05, 0.11), "em_cyan" if k != 1 else "em_violet", axis="z", seg=14, tseg=3)
    for k in range(4):
        m.link((-0.19, -0.2 + k * 0.05, 0.11), (-0.05, -0.05 + k * 0.03, 0.11), 0.004, "em_white", seg=3)
    m.box((0.1, 0.06, 0.05), (0.14, -0.15, 0.12), "gunmetal", 0.006)
    leds(m, 0.12, -0.15, 0.148, 3, 0.03, ["em_green", "em_cyan"], 0.01)
    for k in range(4):
        m.cyl(0.018, 0.08, (-0.15 + k * 0.1, -0.34, 0.06), "black_metal", seg=6)
        m.cyl(0.006, 0.08, (-0.15 + k * 0.1, -0.4, 0.06), "em_white", seg=4)
    bolts(m, [(-0.22, 0.27), (0.22, 0.27), (-0.22, -0.27), (0.22, -0.27)], 0.13)


@_add(RW, "wall network cabinet")
def _(m, rng):
    m.box((0.7, 0.9, 0.24), (0, 0, 0.12), "cm_rack", 0.02)
    m.box((0.62, 0.82, 0.02), (0, 0, 0.25), "hull_mid", 0.008)
    m.box((0.5, 0.6, 0.012), (0, 0.04, 0.262), "glass_dark")
    for k in range(5):
        m.box((0.44, 0.06, 0.02), (0, 0.24 - k * 0.11, 0.235), "gunmetal")
        leds(m, -0.18, 0.24 - k * 0.11, 0.246, 6, 0.045, LEDC, 0.01)
    m.box((0.04, 0.8, 0.02), (-0.33, 0, 0.26), "steel")
    m.box((0.04, 0.05, 0.03), (0.28, 0.0, 0.27), "chrome")
    m.box((0.62, 0.05, 0.005), (0, -0.37, 0.262), "hazard_yellow")
    for k in range(3):
        m.cyl(0.02, 0.12, (-0.2 + k * 0.2, -0.5, 0.12), "black_metal", seg=6)


@_add(RW, "power conduit hub")
def _(m, rng):
    m.box((0.4, 0.4, 0.14), (0, 0, 0.07), "hazard_yellow", 0.02)
    m.box((0.32, 0.32, 0.02), (0, 0, 0.15), "hull_dark", 0.008)
    m.cyl(0.11, 0.05, (0, 0.0, 0.18), "gunmetal", axis="z", seg=12)
    m.cyl(0.06, 0.04, (0, 0, 0.21), "em_amber", axis="z", seg=10)
    for k in range(4):
        a = k * 1.571 + 0.785
        m.box((0.02, 0.02, 0.03), (math.cos(a) * 0.14, math.sin(a) * 0.14, 0.17), "brass")
    for sy in (-1, 1):
        m.cyl(0.05, 0.4, (0, sy * 0.4, 0.07), "steel", seg=10)
        m.cyl(0.065, 0.04, (0, sy * 0.22, 0.07), "black_metal", seg=10)
    m.cyl(0.05, 0.4, (0.4, 0.0, 0.07), "steel", axis="x", seg=10)
    m.cyl(0.065, 0.04, (0.22, 0, 0.07), "black_metal", axis="x", seg=10)
    m.cyl(0.03, 0.1, (-0.26, 0.0, 0.07), "black_metal", axis="x", seg=8)
    leds(m, -0.12, -0.16, 0.152, 4, 0.08, ["em_green", "em_cyan"], 0.02)
@_add(RF, "cable spool")
def _(m, rng):
    m.box((1.0, 0.06, 0.8), (0, 0.03, 0), "wood_dark", 0.008)
    for sx in (-1, 1):
        m.cyl(0.5, 0.05, (sx * 0.29, 0.6, 0), "wood_light", axis="x", seg=20)
        m.cyl(0.05, 0.06, (sx * 0.29, 0.6, 0), "steel", axis="x", seg=8)
    m.cyl(0.14, 0.53, (0, 0.6, 0), "wood_dark", axis="x", seg=12)
    m.cyl(0.4, 0.53, (0, 0.6, 0), "black_metal", axis="x", seg=20)
    m.cyl(0.405, 0.06, (-0.2, 0.6, 0), "cm_cable_y", axis="x", seg=18)
    m.cyl(0.405, 0.06, (0.05, 0.6, 0), "cm_cable_b", axis="x", seg=18)
    for sx in (-1, 1):
        m.box((0.06, 0.6, 0.06), (sx * 0.36, 0.3, -0.25), "steel", 0.006)
        m.box((0.06, 0.6, 0.06), (sx * 0.36, 0.3, 0.25), "steel", 0.006)
    m.tube([(0.0, 0.2, 0.4), (0.15, 0.06, 0.55), (0.3, 0.06, 0.38), (0.5, 0.06, 0.3)], 0.02, "cm_cable_y", seg=5)
    m.box((0.12, 0.06, 0.1), (0.5, 0.09, 0.3), "hazard_yellow", 0.008)


@_add(RF, "wireless tower")
def _(m, rng):
    H = 2.3
    m.cyl(0.35, 0.1, (0, 0.05, 0), "hull_dark", seg=12, bevel=0.008)
    m.cyl(0.08, H, (0, H / 2 + 0.05, 0), "hull_mid", seg=10, r2=0.05)
    m.cyl(0.14, 0.4, (0, 0.3, 0), "gunmetal", seg=10, r2=0.09)
    for k in range(3):
        a = k * 2.094 + 0.5
        m.link((math.cos(a) * 0.3, 0.1, math.sin(a) * 0.3), (0, 0.6, 0), 0.02, "steel", seg=5)
    for lvl, y in enumerate((1.7, 2.05)):
        for k in range(3):
            a = k * 2.094 + lvl * 0.5
            r = 0.15
            cx, cz = math.cos(a) * r, math.sin(a) * r
            m.box((0.16, 0.42, 0.05), (cx, y, cz), "paint_white", 0.01, rot=(0, -a + math.pi / 2, 0))
            m.link((cx * 0.3, y, cz * 0.3), (cx, y, cz), 0.015, "steel", seg=4)
    m.box((0.2, 0.28, 0.14), (0.0, 1.1, 0.16), "hull_dark", 0.01)
    leds(m, -0.06, 1.1, 0.232, 3, 0.06, ["em_green", "em_amber", "em_cyan"], 0.016)
    m.cyl(0.006, 0.4, (0, H + 0.25, 0), "chrome", seg=4)
    m.sphere(0.04, (0, H + 0.08, 0), "em_red", seg=8, ring=6)
    m.cyl(0.11, 0.02, (0, 1.4, 0), "steel", seg=10)


_reg("router", RW, mount="wall", tags=TAGC + ["network"], solid=False)
_reg("router", RF, mount="floor", tags=TAGC + ["network"], solid=True)
