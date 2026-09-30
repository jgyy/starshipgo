"""Cargo bay & hangar bay equipment: crates, barrels, pallets, shelving, loaders,
small craft, hangar tools and storage bins (130 components)."""
import math

from ..kit import family, register_material

for _n, _h, _mt, _ro in [
    ("olive", "#4d5a3a", 0.3, 0.55), ("tan", "#b39a6b", 0.2, 0.6), ("orange", "#c8501b", 0.35, 0.5),
    ("blue", "#1e4b8f", 0.35, 0.5), ("maroon", "#6b1f1a", 0.35, 0.5), ("ptl_blue", "#2a63b8", 0.0, 0.45),
    ("ptl_yellow", "#d9b31a", 0.0, 0.45), ("ptl_green", "#2f7a4a", 0.0, 0.45), ("ptl_red", "#b02a24", 0.0, 0.45),
    ("strap", "#e0a800", 0.0, 0.7), ("burlap", "#a68a5b", 0.0, 0.95), ("rust", "#7a4a2c", 0.5, 0.7),
    ("frost", "#cfe8f2", 0.0, 0.6), ("cream", "#d8d2bd", 0.2, 0.5), ("darkgreen", "#22392a", 0.35, 0.5),
    ("pale_wood", "#c9a878", 0.0, 0.7), ("navy", "#16233f", 0.4, 0.45), ("sand", "#c2b280", 0.3, 0.55),
]:
    register_material("cg_" + _n, _h, _mt, _ro)
register_material("cg_wrap", "#cfe6f0", alpha=0.2)
register_material("cg_tank", "#d9e6ee", alpha=0.35)

PI = math.pi


# ---------------------------------------------------------------- helpers
def fb(m, face, base, du, dv, off, su, sv, sd, mat, bevel=0.0, a=0.0):
    """Thin box on a face. face f(+z) b(-z) r(+x) l(-x). base=(x,y,z) plane centre,
    du/dv offsets along horizontal/vertical, off = distance from base along normal."""
    x, y, z = base
    if face == "f":
        m.box((su, sv, sd), (x + du, y + dv, z + off), mat, bevel, (0, 0, a))
    elif face == "b":
        m.box((su, sv, sd), (x - du, y + dv, z - off), mat, bevel, (0, 0, a))
    elif face == "r":
        m.box((sd, sv, su), (x + off, y + dv, z - du), mat, bevel, (a, 0, 0))
    else:
        m.box((sd, sv, su), (x - off, y + dv, z + du), mat, bevel, (a, 0, 0))


def hazard(m, face, base, du, dv, off, w, h, dark="black_metal"):
    fb(m, face, base, du, dv, off, w, h, 0.012, "hazard_yellow")
    n = max(2, int(w / (h * 1.3)))
    for k in range(n):
        u = -w / 2 + (k + 0.5) * w / n
        if abs(u) > w / 2 - h * 0.6:
            continue
        fb(m, face, base, du + u, dv, off + 0.001, h * 0.3, h * 1.414, 0.014, dark, 0, 0.785)


def stencil(m, face, base, du, dv, off, w, rng, n=4, mat="paint_white", h=0.03):
    tot = 0
    ws = [rng.uniform(0.3, 1.0) for _ in range(n)]
    s = w / (sum(ws) + 0.4 * n)
    x = -w / 2
    for q in ws:
        fb(m, face, base, du + x + q * s / 2, dv, off, q * s, h, 0.008, mat)
        x += q * s + 0.4 * s


def corners(m, cx, cy, cz, w, h, d, s=0.07, mat="steel"):
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                m.box((s, s, s), (cx + sx * (w / 2 - s / 2 + 0.006), cy + sy * (h / 2 - s / 2 + 0.006),
                                  cz + sz * (d / 2 - s / 2 + 0.006)), mat, 0.012)


def edges(m, cx, cy, cz, w, h, d, t, mat, bevel=0.0):
    for sy in (-1, 1):
        for sz in (-1, 1):
            m.box((w, t, t), (cx, cy + sy * (h / 2 - t / 2), cz + sz * (d / 2 - t / 2)), mat, bevel)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((t, h, t), (cx + sx * (w / 2 - t / 2), cy, cz + sz * (d / 2 - t / 2)), mat, bevel)
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.box((t, t, d), (cx + sx * (w / 2 - t / 2), cy + sy * (h / 2 - t / 2), cz), mat, bevel)


def latch(m, x, y, z, mat="steel", face="f"):
    fb(m, face, (x, y, z), 0, 0, 0.012, 0.07, 0.05, 0.03, mat, 0.005)
    fb(m, face, (x, y, z), 0, -0.04, 0.012, 0.03, 0.05, 0.04, "black_metal")


def handle(m, x, y, z, w=0.2, face="f", mat="black_metal"):
    fb(m, face, (x, y, z), 0, 0, 0.03, w, 0.025, 0.025, mat, 0.005)
    fb(m, face, (x, y, z), -w / 2 + 0.015, 0, 0.012, 0.025, 0.025, 0.025, mat)
    fb(m, face, (x, y, z), w / 2 - 0.015, 0, 0.012, 0.025, 0.025, 0.025, mat)


def strap_band(m, cx, cy, cz, w, h, d, x, sw=0.05, mat="cg_strap", over=0.012):
    """Strap around the crate in the YZ plane at x."""
    m.box((sw, h + 2 * over, d + 2 * over), (x, cy, cz), mat, 0.004)
    m.box((sw + 0.03, 0.09, 0.03), (x, cy + h / 2 + over, cz + d / 2 - 0.1), "steel", 0.005)


def feet(m, w, d, h=0.06, mat="black_metal", x0=0, z0=0):
    for sx in (-1, 1):
        m.box((0.08, h, d * 0.9), (x0 + sx * (w / 2 - 0.08), h / 2, z0), mat, 0.01)


def label_plate(m, face, base, du, dv, off, w, h, mat="paint_white", bar="black_metal"):
    fb(m, face, base, du, dv, off, w, h, 0.01, mat)
    fb(m, face, base, du, dv, off + 0.001, w * 0.7, h * 0.15, 0.01, bar)
    fb(m, face, base, du, dv - h * 0.25, off + 0.001, w * 0.5, h * 0.12, 0.01, bar)


def ribs_v(m, face, base, wid, hgt, n, off, mat, sw=0.05, sd=0.03, y0=0.0):
    for k in range(n):
        u = -wid / 2 + (k + 0.5) * wid / n
        fb(m, face, base, u, y0, off, sw, hgt, sd, mat, 0.004)


def cage_grid(m, cx, cy, cz, w, h, d, n, r, mat="steel", front=True):
    """Bar cage (vertical bars on all four sides)."""
    for k in range(n + 1):
        x = cx - w / 2 + k * w / n
        m.box((r, h, r), (x, cy, cz + d / 2 - r / 2), mat)
        m.box((r, h, r), (x, cy, cz - d / 2 + r / 2), mat)
    for k in range(1, max(2, int(n * d / w))):
        z = cz - d / 2 + k * d / max(2, int(n * d / w))
        m.box((r, h, r), (cx - w / 2 + r / 2, cy, z), mat)
        m.box((r, h, r), (cx + w / 2 - r / 2, cy, z), mat)


def pallet_wood(m, w, d, y0=0.0, mat="wood_light"):
    """Wooden pallet 0.144 tall centred on origin footprint (x w, z d)."""
    for sx in (-1, 0, 1):
        for sz in (-1, 0, 1):
            m.box((0.14, 0.09, 0.14), (sx * (w / 2 - 0.07), y0 + 0.055, sz * (d / 2 - 0.07)), mat)
    for sx in (-1, 0, 1):
        m.box((0.1, 0.02, d), (sx * (w / 2 - 0.05) * (1 if sx else 0), y0 + 0.11, 0), mat)
    for k in range(5):
        z = -d / 2 + 0.06 + k * (d - 0.12) / 4
        m.box((w, 0.022, 0.1), (0, y0 + 0.131, z), mat, 0.004)
    for sz in (-1, 1):
        m.box((w, 0.022, 0.1), (0, y0 + 0.011, sz * (d / 2 - 0.05)), mat, 0.004)
    return y0 + 0.144


def pallet_plastic(m, w, d, y0=0.0, mat="cg_ptl_blue"):
    m.box((w, 0.05, d), (0, y0 + 0.14, 0), mat, 0.012)
    for sx in (-1, 0, 1):
        for sz in (-1, 0, 1):
            m.box((0.16, 0.115, 0.16), (sx * (w / 2 - 0.08), y0 + 0.0575, sz * (d / 2 - 0.08)), mat, 0.012)
    for sz in (-1, 1):
        m.box((w - 0.04, 0.03, 0.08), (0, y0 + 0.015, sz * (d / 2 - 0.04)), mat, 0.008)
    for sx in (-1, 1):
        m.box((0.03, 0.03, d - 0.04), (sx * (w / 2 - 0.02), y0 + 0.165, 0), "black_metal")
    return y0 + 0.165


def box_crate(m, w, h, d, mat, cx=0.0, y0=0.0, cz=0.0, prot="steel", s=0.07, ribs=0, bevel=0.02):
    cy = y0 + h / 2
    m.box((w, h, d), (cx, cy, cz), mat, bevel)
    if prot:
        corners(m, cx, cy, cz, w, h, d, s, prot)
    if ribs:
        for fc, wid in (("f", w), ("b", w)):
            base = (cx, cy, cz + (d / 2 if fc == "f" else -d / 2))
            ribs_v(m, fc, base, wid - 2 * s, h - 2 * s, ribs, 0.01, prot or mat, 0.045, 0.024)
        for fc in ("r", "l"):
            base = (cx + (w / 2 if fc == "r" else -w / 2), cy, cz)
            ribs_v(m, fc, base, d - 2 * s, h - 2 * s, max(2, int(ribs * d / w)), 0.01, prot or mat, 0.045, 0.024)
    return cy


# ---------------------------------------------------------------- crates
def _c_steel1m(m, r):
    box_crate(m, 1.0, 1.0, 1.0, "hull_mid", ribs=0)
    B = (0, 0.5, 0.5)
    fb(m, "f", B, 0, 0, 0.01, 0.8, 0.06, 0.02, "steel", 0.005)
    fb(m, "f", B, 0, -0.3, 0.01, 0.8, 0.06, 0.02, "steel", 0.005)
    fb(m, "f", B, 0, 0.3, 0.01, 0.8, 0.06, 0.02, "steel", 0.005)
    stencil(m, "f", B, 0, 0.15, 0.012, 0.5, r, 5, "paint_white", 0.05)
    label_plate(m, "f", B, 0.3, -0.15, 0.012, 0.16, 0.1)
    latch(m, -0.15, 0.94, 0.5)
    latch(m, 0.15, 0.94, 0.5)
    for s in (-1, 1):
        handle(m, s * 0.5, 0.75, 0, 0.25, "r" if s > 0 else "l")
    feet(m, 1.0, 1.0)


def _c_wood06(m, r):
    w = 0.6
    m.box((w - 0.06, w - 0.06, w - 0.06), (0, w / 2, 0), "wood_dark")
    edges(m, 0, w / 2, 0, w, w, w, 0.05, "wood_light", 0.005)
    for fc in "fbrl":
        base = {"f": (0, w / 2, w / 2), "b": (0, w / 2, -w / 2), "r": (w / 2, w / 2, 0), "l": (-w / 2, w / 2, 0)}[fc]
        for k in range(4):
            fb(m, fc, base, 0, -0.2 + k * 0.133, 0.005, w - 0.1, 0.1, 0.02, "wood_light" if k % 2 else "cg_pale_wood", 0.004)
    fb(m, "f", (0, w / 2, w / 2), 0, 0, 0.03, 0.2, 0.08, 0.008, "paint_white")
    fb(m, "f", (0, w / 2, w / 2), 0, 0, 0.036, 0.15, 0.02, 0.006, "black_metal")


def _c_wood12(m, r):
    w, h, d = 1.2, 1.0, 1.2
    m.box((w - 0.06, h - 0.06, d - 0.06), (0, 0.55, 0), "wood_dark")
    m.box((w, 0.1, d), (0, 0.05, 0), "wood_dark", 0.01)
    edges(m, 0, 0.6, 0, w, h, d, 0.08, "wood_light", 0.008)
    for fc in "fb":
        base = (0, 0.6, d / 2 if fc == "f" else -d / 2)
        fb(m, fc, base, 0, 0, 0.03, 1.55, 0.06, 0.03, "wood_light", 0.004, 0.75)
        fb(m, fc, base, 0, 0, 0.034, 1.55, 0.06, 0.03, "wood_light", 0.004, -0.75)
        for k in range(3):
            fb(m, fc, base, 0, -0.3 + k * 0.3, 0.01, w - 0.1, 0.16, 0.03, "cg_pale_wood", 0.004)
    m.box((w + 0.04, 0.05, 0.05), (0, 1.07, 0), "steel")
    fb(m, "f", (0, 0.6, d / 2), 0.35, 0.3, 0.06, 0.25, 0.18, 0.006, "paint_orange")
    fb(m, "f", (0, 0.6, d / 2), -0.3, -0.25, 0.06, 0.25, 0.04, 0.006, "paint_white")


def _c_ribbed(m, r):
    w, h, d = 1.2, 1.2, 1.8
    m.box((w, h, d), (0, 0.65, 0), "paint_grey", 0.02)
    m.box((w + 0.04, 0.1, d + 0.04), (0, 0.05, 0), "black_metal", 0.01)
    for fc, base, wid in (("f", (0, 0.65, d / 2), w), ("b", (0, 0.65, -d / 2), w)):
        ribs_v(m, fc, base, wid - 0.1, h - 0.2, 8, 0.012, "steel", 0.06, 0.03)
    for fc, base in (("r", (w / 2, 0.65, 0)), ("l", (-w / 2, 0.65, 0))):
        ribs_v(m, fc, base, d - 0.1, h - 0.2, 12, 0.012, "steel", 0.06, 0.03)
    corners(m, 0, 0.65, 0, w, h, d, 0.09, "black_metal")
    for x in (-0.3, 0.3):
        latch(m, x, 1.05, d / 2)
    m.box((w - 0.1, 0.06, d - 0.1), (0, 1.27, 0), "steel", 0.008)
    hazard(m, "f", (0, 0.65, d / 2), 0, 0.5, 0.02, 0.9, 0.08)


def _c_tote(m, r, col="cg_ptl_blue", lid="plastic_grey", n=1, hz=False):
    w, h, d = 0.6, 0.4, 0.4
    for k in range(n):
        y = k * (h + 0.02)
        m.box((w, h, d), (0, y + h / 2, 0), col, 0.02)
        m.box((w + 0.03, 0.05, d + 0.03), (0, y + h - 0.02, 0), lid, 0.012)
        for s in (-1, 1):
            fb(m, "r" if s > 0 else "l", (s * w / 2, y + 0.3, 0), 0, 0, 0.012, 0.16, 0.05, 0.02, "black_metal", 0.01)
        fb(m, "f", (0, y + 0.2, d / 2), 0, 0, 0.01, 0.4, 0.14, 0.012, "paint_white", 0.004)
        for x in (-0.24, 0.24):
            latch(m, x, y + h - 0.02, d / 2 + 0.017, "paint_orange")
        for x in (-0.28, 0.28):
            m.box((0.03, h - 0.06, d - 0.06), (x, y + h / 2 - 0.01, 0), col, 0.006)


def _c_tote_stack(m, r):
    _c_tote(m, r, "cg_ptl_yellow", "black_metal", 3)


def _c_haz_yellow(m, r):
    box_crate(m, 0.9, 0.8, 0.9, "hazard_yellow", prot="black_metal", s=0.08, ribs=3)
    B = (0, 0.4, 0.45)
    fb(m, "f", B, 0, 0.12, 0.03, 0.22, 0.22, 0.012, "paint_red", 0, 0.785)
    fb(m, "f", B, 0, 0.12, 0.04, 0.09, 0.09, 0.012, "black_metal", 0, 0.785)
    stencil(m, "f", B, 0, -0.15, 0.03, 0.5, r, 4, "black_metal", 0.05)
    latch(m, 0, 0.72, 0.45, "black_metal")
    for s in (-1, 1):
        handle(m, s * 0.45, 0.55, 0, 0.3, "r" if s > 0 else "l")
    feet(m, 0.9, 0.9)


def _c_flammable(m, r):
    box_crate(m, 0.8, 0.9, 0.7, "paint_red", prot="black_metal", s=0.07)
    B = (0, 0.45, 0.35)
    fb(m, "f", B, 0, 0.0, 0.012, 0.8, 0.15, 0.012, "paint_white")
    m.prism([(-0.05, 0), (0.05, 0), (0.0, 0.14)], 0.01, (-0.12, 0.38, 0.375), "paint_orange", plane="xy")
    m.prism([(-0.05, 0), (0.05, 0), (0.0, 0.16)], 0.01, (0.0, 0.38, 0.375), "paint_orange", plane="xy")
    m.prism([(-0.05, 0), (0.05, 0), (0.0, 0.14)], 0.01, (0.12, 0.38, 0.375), "paint_orange", plane="xy")
    stencil(m, "f", B, 0, 0.25, 0.012, 0.5, r, 3, "paint_white", 0.05)
    hazard(m, "f", B, 0, -0.3, 0.012, 0.7, 0.07)
    for x in (-0.25, 0.25):
        latch(m, x, 0.84, 0.35)


def _c_medical(m, r):
    box_crate(m, 0.8, 0.5, 0.5, "plastic_white", prot="paint_red", s=0.06)
    B = (0, 0.25, 0.25)
    fb(m, "f", B, 0, 0.02, 0.012, 0.24, 0.08, 0.008, "paint_red")
    fb(m, "f", B, 0, 0.02, 0.012, 0.08, 0.24, 0.008, "paint_red")
    fb(m, "f", B, 0.28, -0.12, 0.012, 0.16, 0.06, 0.008, "em_green")
    fb(m, "f", B, -0.28, -0.12, 0.012, 0.16, 0.06, 0.008, "paint_grey")
    for x in (-0.15, 0.15):
        latch(m, x, 0.46, 0.25, "paint_red")
    handle(m, 0, 0.55, 0, 0.3, "f")
    m.box((0.3, 0.02, 0.2), (0, 0.51, 0.0), "paint_red", 0.005)


def _c_ammo(m, r):
    w, h, d = 0.55, 0.32, 0.28
    m.box((w, h, d), (0, h / 2, 0), "cg_olive", 0.02)
    m.box((w + 0.02, 0.04, d + 0.02), (0, h - 0.02, 0), "cg_olive", 0.012)
    for k in range(4):
        fb(m, "f", (0, h / 2, d / 2), -0.2 + k * 0.133, 0, 0.005, 0.02, h - 0.03, 0.015, "cg_olive", 0.004)
    for x in (-0.15, 0.15):
        latch(m, x, h - 0.06, d / 2 + 0.01, "steel")
    handle(m, 0, h + 0.03, 0, 0.22, "f", "steel")
    fb(m, "f", (0, h / 2, d / 2), 0, -0.03, 0.02, 0.3, 0.05, 0.006, "hazard_yellow")
    stencil(m, "f", (0, h / 2, d / 2), 0, 0.04, 0.02, 0.26, r, 3, "hazard_yellow", 0.02)
    for x in (-1, 1):
        m.box((0.02, h - 0.1, d - 0.1), (x * w / 2, h / 2, 0), "steel")


def _c_ammo_stack(m, r):
    for k, (dx, dz, a) in enumerate([(0, 0, 0), (0.02, 0, 0.06), (-0.02, 0.0, -0.05)]):
        w, h, d = 0.5, 0.26, 0.26
        y = k * (h + 0.005)
        m.box((w, h, d), (dx, y + h / 2, 0), "cg_olive" if k != 1 else "cg_tan", 0.02, (0, a, 0))
        m.box((0.07, 0.06, d + 0.02), (dx + 0.15, y + h - 0.05, 0), "steel", 0.006, (0, a, 0))
        m.box((0.07, 0.06, d + 0.02), (dx - 0.15, y + h - 0.05, 0), "steel", 0.006, (0, a, 0))
        m.box((0.2, 0.025, 0.03), (dx, y + h + 0.01, 0), "black_metal", 0.004, (0, a, 0))
    m.box((0.6, 0.02, 0.35), (0, 0.79, 0), "cg_tan")
    m.box((0.5, 0.02, 0.05), (0, 0.805, 0.1), "hazard_yellow")


def _c_fragile(m, r):
    w, h, d = 1.0, 0.9, 0.8
    m.box((w - 0.06, h - 0.06, d - 0.06), (0, h / 2, 0), "wood_dark")
    edges(m, 0, h / 2, 0, w, h, d, 0.07, "cg_pale_wood", 0.005)
    for fc, base in (("f", (0, h / 2, d / 2)), ("b", (0, h / 2, -d / 2))):
        for k in range(4):
            fb(m, fc, base, 0, -0.3 + k * 0.2, 0.01, w - 0.1, 0.16, 0.02, "cg_pale_wood", 0.004)
    B = (0, h / 2, d / 2)
    fb(m, "f", B, 0, 0.05, 0.03, 0.45, 0.35, 0.008, "paint_red", 0.004)
    fb(m, "f", B, 0, 0.05, 0.036, 0.4, 0.3, 0.006, "paint_white")
    m.cyl(0.05, 0.005, (0, 0.5, 0.43), "glass_blue", axis="z", seg=10, r2=0.05)
    m.box((0.014, 0.1, 0.008), (0, 0.42, 0.43), "paint_red")
    m.box((0.1, 0.014, 0.008), (0, 0.37, 0.43), "paint_red")
    m.cyl(0.05, 0.1, (0, 0.5, 0.437), "paint_red", axis="z", seg=8, r2=0.02)
    for s in (-1, 1):
        fb(m, "f", B, s * 0.35, -0.25, 0.03, 0.08, 0.16, 0.008, "paint_red")
        m.prism([(-0.06, 0), (0.06, 0), (0, 0.09)], 0.008, (s * 0.35, 0.68, 0.412), "paint_red", plane="xy")
    hazard(m, "f", B, 0, -0.38, 0.03, 0.5, 0.05)


def _c_open_parts(m, r):
    w, h, d = 1.0, 0.55, 0.8
    m.box((w, 0.05, d), (0, 0.025, 0), "wood_dark")
    for fc, base, wid in (("f", (0, h / 2, d / 2), w), ("b", (0, h / 2, -d / 2), w)):
        for k in range(3):
            fb(m, fc, base, 0, -0.2 + k * 0.2, -0.02, wid, 0.17, 0.03, "wood_light", 0.004)
    for fc, base in (("r", (w / 2, h / 2, 0)), ("l", (-w / 2, h / 2, 0))):
        for k in range(3):
            fb(m, fc, base, 0, -0.2 + k * 0.2, -0.02, d - 0.06, 0.17, 0.03, "wood_light", 0.004)
    for x in (-w / 2 + 0.03, w / 2 - 0.03):
        for z in (-d / 2 + 0.03, d / 2 - 0.03):
            m.box((0.06, h, 0.06), (x, h / 2, z), "wood_dark")
    m.box((w - 0.1, 0.03, d - 0.1), (0, 0.4, 0), "foam")
    m.cyl(0.1, 0.32, (-0.25, 0.55, 0.1), "brass", axis="x", seg=12)
    m.cyl(0.14, 0.07, (-0.25, 0.55, 0.1), "steel", axis="x", seg=12)
    m.box((0.35, 0.22, 0.25), (0.2, 0.52, -0.1), "hull_dark", 0.02)
    m.sphere(0.12, (0.28, 0.5, 0.2), "copper", 10, 8)
    m.cyl(0.03, 0.4, (0.0, 0.5, -0.28), "steel", axis="x", seg=8)
    m.box((0.2, 0.06, 0.2), (-0.3, 0.46, -0.2), "paint_red", 0.01)


def _c_open_cells(m, r):
    w, h, d = 1.0, 0.5, 0.7
    m.box((w, 0.05, d), (0, 0.025, 0), "hull_dark")
    edges(m, 0, h / 2, 0, w, h, d, 0.04, "hull_mid", 0.004)
    for fc, base, wid in (("f", (0, h / 2, d / 2), w), ("b", (0, h / 2, -d / 2), w)):
        fb(m, fc, base, 0, -0.05, -0.02, wid - 0.06, 0.28, 0.02, "cg_blue", 0.005)
    for fc, base in (("r", (w / 2, h / 2, 0)), ("l", (-w / 2, h / 2, 0))):
        fb(m, fc, base, 0, -0.05, -0.02, d - 0.06, 0.28, 0.02, "cg_blue", 0.005)
    for i in range(4):
        for j in range(3):
            x, z = -0.33 + i * 0.22, -0.25 + j * 0.25
            m.cyl(0.08, 0.3, (x, 0.33, z), "brushed_alu", seg=8)
            m.cyl(0.045, 0.02, (x, 0.49, z), "em_cyan" if (i + j) % 3 else "em_amber", seg=6)
    hazard(m, "f", (0, h / 2, d / 2), 0, 0.02, 0.005, 0.5, 0.06)


def _c_reefer(m, r):
    w, h, d = 1.2, 1.1, 0.9
    m.box((w, h, d), (0, 0.6, 0), "cg_cream", 0.03)
    m.box((w + 0.03, 0.1, d + 0.03), (0, 0.05, 0), "black_metal", 0.01)
    corners(m, 0, 0.6, 0, w, h, d, 0.08, "steel")
    # cooling unit on the front
    B = (0, 0.6, d / 2)
    fb(m, "f", B, 0, 0.1, 0.05, 0.7, 0.55, 0.1, "hull_light", 0.02)
    for k in range(7):
        fb(m, "f", B, 0, -0.06 + k * 0.05, 0.11, 0.55, 0.018, 0.012, "hull_dark")
    m.cyl(0.13, 0.03, (0.0, 0.85, 0.5), "hull_dark", axis="z", seg=16)
    for k in range(3):
        m.box((0.02, 0.24, 0.01), (0, 0.85, 0.52), "steel", rot=(0, 0, k * 1.047))
    fb(m, "f", B, 0.0, -0.28, 0.02, 0.4, 0.14, 0.02, "hull_dark", 0.01)
    fb(m, "f", B, 0.0, -0.28, 0.032, 0.32, 0.07, 0.008, "em_blue")
    m.box((1.0, 0.03, 0.03), (0, 1.16, 0.3), "paint_blue")
    fb(m, "f", B, -0.4, -0.4, 0.02, 0.1, 0.1, 0.01, "paint_blue", 0, 0.785)
    for s in (-1, 1):
        handle(m, s * 0.6, 0.9, 0, 0.3, "r" if s > 0 else "l", "steel")


def _c_stacked_pair(m, r):
    box_crate(m, 1.0, 0.7, 0.8, "cg_orange", prot="black_metal", s=0.07, ribs=3)
    box_crate(m, 0.7, 0.5, 0.6, "cg_blue", y0=0.7, cx=0.1, prot="steel", s=0.06)
    strap_band(m, 0.1, 0.95, 0, 0.7, 0.5, 0.6, -0.15)
    strap_band(m, 0.1, 0.95, 0, 0.7, 0.5, 0.6, 0.35)
    latch(m, 0.1, 1.15, 0.3)
    stencil(m, "f", (0, 0.35, 0.4), 0, 0.05, 0.025, 0.6, r, 4, "paint_white", 0.05)
    feet(m, 1.0, 0.8)


def _iso(m, r, col, doorcol, hz):
    w, h, d = 2.4, 2.6, 6.0
    cy = h / 2 + 0.02
    m.box((w - 0.06, h - 0.1, d - 0.2), (0, cy, 0), col)
    for sx in (-1, 1):
        for k in range(11):
            z = -d / 2 + 0.35 + k * (d - 0.7) / 21
            m.box((0.05, h - 0.3, 0.09), (sx * (w / 2 - 0.02), cy, z), col)
    for k in range(5):
        x = -w / 2 + 0.25 + k * (w - 0.5) / 4
        m.box((0.09, 0.05, d - 0.3), (x, h + 0.02, 0), col)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                m.box((0.16, 0.16, 0.18), (sx * (w / 2 - 0.08), cy + sy * (h / 2 - 0.08), sz * (d / 2 - 0.09)), "black_metal", 0.015)
    for sx in (-1, 1):
        m.box((0.09, 0.14, d - 0.2), (sx * (w / 2 - 0.05), 0.09, 0), "black_metal")
        m.box((0.09, 0.14, d - 0.2), (sx * (w / 2 - 0.05), h - 0.05, 0), "black_metal")
    for z in (-1.2, 1.2):
        m.box((w - 0.4, 0.08, 0.18), (0, 0.06, z), "hull_dark")
    # door end (front)
    B = (0, cy, d / 2)
    for sx in (-1, 1):
        fb(m, "f", B, sx * 0.55, 0, 0.005, 1.08, h - 0.2, 0.06, doorcol, 0.008)
        for q in range(4):
            fb(m, "f", B, sx * 0.55 + (q - 1.5) * 0.24, 0, 0.04, 0.05, h - 0.32, 0.03, doorcol, 0.004)
    for x in (-0.55, 0.55):
        m.cyl(0.018, 2.3, (x + 0.0, cy, d / 2 + 0.06), "steel", seg=8)
        m.box((0.12, 0.06, 0.05), (x, cy + 0.2, d / 2 + 0.08), "black_metal")
        m.box((0.12, 0.06, 0.05), (x, cy - 0.3, d / 2 + 0.08), "black_metal")
    m.box((0.07, 0.3, 0.05), (0, cy, d / 2 + 0.07), "steel")
    if hz:
        hazard(m, "r", (w / 2, cy, 0), 0, 0.55, 0.03, 3.2, 0.2)
        hazard(m, "l", (-w / 2, cy, 0), 0, 0.55, 0.03, 3.2, 0.2)
    stencil(m, "r", (w / 2, cy, 0), 1.4, 0.0, 0.03, 2.2, r, 6, "paint_white", 0.16)
    stencil(m, "l", (-w / 2, cy, 0), 1.4, 0.0, 0.03, 2.2, r, 6, "paint_white", 0.16)
    label_plate(m, "f", B, 0.9, -0.7, 0.07, 0.3, 0.2)


def _c_iso1(m, r):
    _iso(m, r, "cg_blue", "cg_blue", False)


def _c_iso2(m, r):
    _iso(m, r, "cg_orange", "cg_maroon", True)


def _c_pod_horiz(m, r):
    R, L = 0.6, 1.8
    y = 0.75
    m.cyl(R, L, (0, y, 0), "paint_white", axis="z", seg=20)
    for s in (-1, 1):
        m.sphere(R, (0, y, s * L / 2), "paint_white", 20, 10, (1, 1, 0.55))
    for z in (-0.6, 0.0, 0.6):
        m.torus(R + 0.01, 0.025, (0, y, z), "steel", axis="z", seg=20, tseg=6)
    m.cyl(0.2, 0.06, (0, y + R + 0.0, 0.0), "steel", seg=12, bevel=0.01)
    m.cyl(0.05, 0.1, (0.0, y + R + 0.07, 0.0), "paint_red", seg=8)
    m.cyl(0.16, 0.04, (R - 0.02, y, 0.4), "black_metal", axis="x", seg=14)
    m.cyl(0.11, 0.05, (R + 0.0, y, 0.4), "glass_blue", axis="x", seg=14)
    m.box((0.15, 0.06, 0.02), (0.0, y + 0.1, L / 2 + 0.28), "em_green")
    for z in (-0.6, 0.6):
        m.box((1.4, 0.06, 0.16), (0, 0.2, z), "hull_dark", 0.01)
        m.box((0.1, 0.35, 0.16), (-0.5, 0.35, z), "hull_dark", 0.01, (0, 0, 0.45))
        m.box((0.1, 0.35, 0.16), (0.5, 0.35, z), "hull_dark", 0.01, (0, 0, -0.45))
        m.box((1.2, 0.03, 0.3), (0, 0.03, z), "black_metal")
    m.box((0.5, 0.05, 0.02), (0, y - 0.2, L / 2 + 0.3), "hazard_yellow")


def _c_pod_vert(m, r):
    R, H = 0.5, 1.9
    m.cyl(0.7, 0.08, (0, 0.04, 0), "hull_dark", seg=8)
    m.cyl(R, H - 0.4, (0, 0.08 + (H - 0.4) / 2, 0), "cg_darkgreen", seg=20)
    m.sphere(R, (0, 0.08 + H - 0.4, 0), "cg_darkgreen", 20, 10, (1, 0.5, 1))
    m.sphere(R * 0.95, (0, 0.1663, 0), "cg_darkgreen", 20, 10, (1, 0.35, 1))
    for y in (0.45, 1.0, 1.55):
        m.torus(R + 0.005, 0.02, (0, y, 0), "steel", seg=20, tseg=6)
    m.box((0.5, 0.9, 0.06), (0, 0.85, R - 0.01), "hull_mid", 0.02)
    m.box((0.36, 0.7, 0.03), (0, 0.85, R + 0.03), "hull_dark", 0.01)
    m.cyl(0.05, 0.03, (0.1, 0.9, R + 0.06), "steel", axis="z", seg=10)
    m.box((0.08, 0.08, 0.02), (-0.12, 1.1, R + 0.05), "em_amber")
    m.cyl(0.04, 0.2, (0.3, 2.05, 0.0), "brass", seg=8)
    m.cyl(0.06, 0.03, (0.3, 2.17, 0.0), "paint_red", seg=8)
    for a in range(4):
        m.link((math.cos(a * 1.57) * 0.5, 0.15, math.sin(a * 1.57) * 0.5), (math.cos(a * 1.57) * 0.68, 0.06, math.sin(a * 1.57) * 0.68), 0.03, "steel", 6)
    hazard(m, "f", (0, 0.3, 0.0), 0, 0, R * 0.85, 0.5, 0.08)


def _c_strapped(m, r):
    box_crate(m, 0.9, 0.7, 0.9, "cg_tan", prot="black_metal", s=0.06)
    for x in (-0.25, 0.25):
        strap_band(m, 0, 0.35, 0, 0.9, 0.7, 0.9, x, 0.06)
    for x in (-0.25, 0.25):
        m.box((0.09, 0.12, 0.05), (x, 0.36, 0.475), "steel", 0.006)
        m.box((0.03, 0.05, 0.05), (x, 0.28, 0.48), "black_metal")
    stencil(m, "f", (0, 0.35, 0.45), 0, 0.15, 0.012, 0.2, r, 3, "paint_white", 0.04)
    fb(m, "f", (0, 0.35, 0.45), 0, -0.2, 0.012, 0.08, 0.08, 0.006, "paint_red", 0, 0.785)
    feet(m, 0.9, 0.9)


def _c_strapped_pair(m, r):
    box_crate(m, 0.8, 0.9, 0.8, "cg_olive", cx=-0.45, prot="steel", s=0.06)
    box_crate(m, 0.8, 0.6, 0.8, "cg_tan", cx=0.45, prot="black_metal", s=0.06)
    m.box((1.7, 0.05, 0.05), (0, 0.45, 0.42), "cg_strap")
    m.box((1.7, 0.05, 0.05), (0, 0.45, -0.42), "cg_strap")
    m.box((1.7, 0.05, 0.05), (0, 0.8, 0.42), "cg_strap")
    for z in (0.45, -0.45):
        m.box((0.14, 0.14, 0.05), (0.0, 0.62, z), "steel", 0.01)
        m.box((0.05, 0.12, 0.06), (0.0, 0.62, z * 1.05), "black_metal")
    for x in (-0.45, 0.45):
        m.box((0.05, 0.05, 0.85), (x, 0.9 if x < 0 else 0.6, 0), "cg_strap")
    stencil(m, "f", (-0.45, 0.45, 0.4), 0, 0.15, 0.012, 0.5, r, 3, "paint_white", 0.05)


def _c_cage_small(m, r):
    w, h, d = 0.9, 0.6, 0.6
    m.box((w, 0.05, d), (0, 0.1, 0), "black_metal")
    m.box((w - 0.05, 0.02, d - 0.05), (0, 0.13, 0), "steel")
    for x in (-0.38, 0.38):
        for z in (-0.25, 0.25):
            m.cyl(0.03, 0.06, (x, 0.03, z), "rubber", seg=8)
    cage_grid(m, 0, 0.4, 0, w, 0.5, d, 12, 0.012, "steel")
    edges(m, 0, 0.4, 0, w, 0.5, d, 0.03, "steel")
    m.box((w, 0.03, d), (0, 0.66, 0), "steel", 0.006)
    m.box((0.28, 0.02, 0.02), (0, 0.69, 0), "black_metal")
    latch(m, 0.3, 0.4, d / 2 + 0.01, "brass")
    m.cyl(0.02, 0.35, (-0.2, 0.6, 0.31), "steel", axis="x", seg=6)
    for s in (-1, 1):
        m.box((0.04, 0.05, 0.04), (s * 0.36, 0.7, 0), "steel")
    m.box((0.14, 0.05, 0.1), (0.22, 0.17, -0.2), "plastic_white", 0.01)


def _c_cage_large(m, r):
    w, h, d = 1.6, 1.2, 1.0
    m.box((w, 0.1, d), (0, 0.2, 0), "hull_dark", 0.01)
    for x in (-0.7, 0.7):
        for z in (-0.4, 0.4):
            m.cyl(0.07, 0.06, (x, 0.09, z), "rubber", axis="x", seg=10)
            m.box((0.06, 0.1, 0.06), (x, 0.13, z), "steel")
    cage_grid(m, 0, 0.85, 0, w, 1.1, d, 16, 0.014, "steel")
    edges(m, 0, 0.85, 0, w, 1.1, d, 0.04, "hull_mid", 0.004)
    m.box((w, 0.04, d), (0, 1.42, 0), "hull_mid", 0.008)
    for x in (-0.2, 0.2):
        m.box((0.03, 0.03, d), (x, 1.44, 0), "steel")
    m.box((0.7, 0.9, 0.03), (-0.35, 0.85, d / 2 + 0.005), "steel")
    for k in range(9):
        m.box((0.014, 0.85, 0.014), (-0.66 + k * 0.08, 0.85, d / 2 + 0.03), "steel")
    latch(m, 0.02, 0.85, d / 2 + 0.03, "gold_trim")
    m.box((0.3, 0.16, 0.02), (0.55, 1.1, d / 2 + 0.02), "paint_white")
    m.box((0.24, 0.02, 0.008), (0.55, 1.12, d / 2 + 0.03), "paint_red")


def _c_plank24(m, r):
    w, h, d = 2.4, 1.4, 1.4
    m.box((w, 0.16, d), (0, 0.08, 0), "wood_dark", 0.01)
    for x in (-0.9, 0, 0.9):
        m.box((0.2, 0.14, d + 0.2), (x, 0.07, 0), "wood_light", 0.01)
    m.box((w - 0.06, h - 0.2, d - 0.06), (0, 0.92, 0), "wood_dark")
    edges(m, 0, 0.92, 0, w, h - 0.15, d, 0.09, "wood_light", 0.008)
    for fc, base, wid in (("f", (0, 0.92, d / 2), w), ("b", (0, 0.92, -d / 2), w)):
        for k in range(6):
            fb(m, fc, base, 0, -0.5 + k * 0.2, 0.01, wid - 0.12, 0.17, 0.03, "cg_pale_wood" if k % 2 else "wood_light", 0.004)
        fb(m, fc, base, 0, 0, 0.045, 2.6, 0.08, 0.03, "wood_light", 0.004, 0.52)
    for fc, base in (("r", (w / 2, 0.92, 0)), ("l", (-w / 2, 0.92, 0))):
        for k in range(6):
            fb(m, fc, base, 0, -0.5 + k * 0.2, 0.01, d - 0.12, 0.17, 0.03, "wood_light", 0.004)
    for x in (-0.6, 0.6):
        m.box((0.03, 1.36, 1.46), (x, 0.92, 0), "steel")
        m.box((0.1, 0.06, 0.1), (x, 1.62, 0.4), "black_metal")
    label_plate(m, "f", (0, 0.92, d / 2), 0.7, 0.35, 0.07, 0.35, 0.22)
    hazard(m, "f", (0, 0.92, d / 2), -0.6, -0.4, 0.07, 0.6, 0.07)
    m.box((0.5, 0.2, 0.01), (-0.4, 1.3, d / 2 + 0.015), "paint_orange")


def _c_hardcase(m, r):
    w, h, d = 0.9, 0.3, 0.55
    m.box((w, h, d), (0, 0.11 + h / 2, 0), "plastic_black", 0.03)
    m.box((w + 0.02, 0.02, d + 0.02), (0, 0.11 + h / 2, 0), "hull_dark", 0.005)
    for x in (-0.28, -0.1, 0.1, 0.28):
        latch(m, x, 0.11 + h / 2 + 0.03, d / 2 + 0.01, "chrome")
    handle(m, 0, 0.11 + h, 0.0, 0.3, "f", "hull_dark")
    m.box((0.3, 0.03, 0.1), (0, 0.11 + h + 0.03, -0.0), "hull_dark", 0.01)
    corners(m, 0, 0.11 + h / 2, 0, w, h, d, 0.06, "hull_dark")
    for x in (-0.4, 0.4):
        m.cyl(0.055, 0.05, (x, 0.055, -0.22), "rubber", axis="x", seg=10)
    for x in (-0.38, 0.38):
        m.box((0.04, 0.05, 0.05), (x, 0.085, 0.22), "hull_dark")
    m.box((0.06, 0.24, 0.02), (0.0, 0.25, -d / 2 - 0.02), "hull_dark")
    fb(m, "f", (0, 0.26, d / 2), 0.28, 0.05, 0.012, 0.18, 0.06, 0.006, "paint_orange")


def _c_vault(m, r):
    w, h, d = 1.0, 1.0, 0.8
    box_crate(m, w, h, d, "gunmetal", prot="hull_dark", s=0.09, bevel=0.03)
    B = (0, 0.5, d / 2)
    fb(m, "f", B, 0, 0, 0.03, 0.8, 0.8, 0.05, "hull_dark", 0.02)
    m.cyl(0.13, 0.05, (0, 0.55, d / 2 + 0.08), "steel", axis="z", seg=16)
    m.cyl(0.03, 0.14, (0, 0.55, d / 2 + 0.12), "chrome", axis="z", seg=8)
    for a in range(3):
        m.box((0.02, 0.26, 0.02), (0, 0.55, d / 2 + 0.16), "chrome", rot=(0, 0, a * 1.047))
    m.box((0.18, 0.26, 0.03), (0.28, 0.35, d / 2 + 0.07), "black_metal", 0.005)
    m.quad((0.12, 0.08), (0.28, 0.42, d / 2 + 0.086), "screen:systems")
    for k in range(6):
        m.box((0.035, 0.03, 0.01), (0.23 + (k % 3) * 0.05, 0.33 - (k // 3) * 0.04, d / 2 + 0.086), "plastic_grey")
    m.box((0.05, 0.05, 0.02), (0.28, 0.48, d / 2 + 0.086), "em_red")
    for y in (0.2, 0.8):
        m.cyl(0.04, 0.16, (-0.44, y, d / 2 + 0.02), "steel", seg=8)
    hazard(m, "f", B, 0, -0.42, 0.06, 0.6, 0.06)


def _c_cold(m, r):
    w, h, d = 0.9, 0.7, 0.7
    m.box((w, h, d), (0, 0.4, 0), "cg_frost", 0.04)
    m.box((w + 0.05, 0.05, d + 0.05), (0, 0.72, 0), "foam", 0.02)
    m.box((w + 0.03, 0.1, d + 0.03), (0, 0.05, 0), "hull_dark", 0.01)
    corners(m, 0, 0.4, 0, w, h, d, 0.06, "paint_blue")
    B = (0, 0.4, d / 2)
    fb(m, "f", B, 0.0, 0.08, 0.03, 0.32, 0.18, 0.02, "black_metal", 0.006)
    m.quad((0.26, 0.11), (0, 0.48, d / 2 + 0.042), "screen:power")
    fb(m, "f", B, -0.25, -0.15, 0.02, 0.15, 0.15, 0.01, "paint_blue", 0, 0.785)
    fb(m, "f", B, 0.25, -0.15, 0.02, 0.15, 0.04, 0.01, "em_cyan")
    for x in (-0.3, 0.3):
        latch(m, x, 0.72, d / 2 + 0.02, "steel")
    m.cyl(0.05, 0.1, (0.3, 0.8, -0.2), "steel", seg=8)
    m.cyl(0.02, 0.1, (0.3, 0.88, -0.2), "paint_blue", seg=6)
    for s in (-1, 1):
        handle(m, s * 0.45, 0.5, 0, 0.3, "r" if s > 0 else "l", "steel")


def _c_locker_up(m, r):
    w, h, d = 0.6, 1.8, 0.5
    m.box((w, h, d), (0, h / 2 + 0.1, 0), "cg_olive", 0.02)
    m.box((w + 0.04, 0.1, d + 0.04), (0, 0.05, 0), "black_metal", 0.01)
    B = (0, 1.0, d / 2)
    fb(m, "f", B, 0, 0.0, 0.005, 0.5, 1.7, 0.02, "cg_olive", 0.01)
    fb(m, "f", B, -0.25, 0.0, 0.015, 0.02, 1.7, 0.01, "black_metal")
    fb(m, "f", B, 0.2, 0.0, 0.025, 0.04, 0.4, 0.03, "steel", 0.008)
    for y in (-0.7, 0.7):
        fb(m, "f", B, -0.23, y, 0.025, 0.05, 0.14, 0.03, "black_metal")
    for k in range(4):
        fb(m, "f", B, 0, 0.55 + k * 0.03, 0.02, 0.3, 0.012, 0.01, "black_metal")
    stencil(m, "f", B, 0, -0.35, 0.02, 0.35, r, 3, "hazard_yellow", 0.06)
    m.box((0.5, 0.06, 0.02), (0, 1.95, d / 2 + 0.005), "hazard_yellow")
    latch(m, 0.2, 0.7, d / 2 + 0.03, "brass")


def _c_biohaz(m, r):
    box_crate(m, 0.8, 0.7, 0.7, "cg_orange", prot="black_metal", s=0.07)
    B = (0, 0.35, 0.35)
    for a in range(3):
        ang = a * 2.094 + 1.57
        m.torus(0.05, 0.015, (0.09 * math.cos(ang), 0.42 + 0.09 * math.sin(ang), 0.36), "black_metal", axis="z", seg=10, tseg=5, arc=4.6)
    m.cyl(0.025, 0.012, (0, 0.42, 0.36), "black_metal", axis="z", seg=8)
    hazard(m, "f", B, 0, -0.22, 0.012, 0.65, 0.09)
    fb(m, "f", B, 0.28, 0.22, 0.012, 0.1, 0.05, 0.02, "em_amber")
    for x in (-0.22, 0.22):
        latch(m, x, 0.66, 0.35, "hull_dark")
    m.box((0.5, 0.04, 0.24), (0, 0.72, -0.05), "steel", 0.006)
    m.cyl(0.03, 0.1, (0, 0.77, -0.05), "paint_red", seg=8)
    feet(m, 0.8, 0.7)


CRATES = [
    ("steel_1m", _c_steel1m, ["cargo"]), ("wood_slat_06", _c_wood06, ["cargo"]), ("wood_slat_12", _c_wood12, ["cargo"]),
    ("ribbed_steel", _c_ribbed, ["cargo"]), ("tote_grey", lambda m, r: _c_tote(m, r, "plastic_grey", "black_metal"), ["cargo"]),
    ("tote_stack_yellow", _c_tote_stack, ["cargo"]), ("hazard_yellow", _c_haz_yellow, ["cargo"]),
    ("flammable_red", _c_flammable, ["cargo"]), ("medical_supply", _c_medical, ["cargo"]),
    ("ammo_box", _c_ammo, ["cargo"]), ("ammo_stack", _c_ammo_stack, ["cargo"]), ("fragile", _c_fragile, ["cargo"]),
    ("open_parts", _c_open_parts, ["cargo"]), ("open_power_cells", _c_open_cells, ["cargo"]),
    ("refrigerated", _c_reefer, ["cargo"]), ("stacked_pair", _c_stacked_pair, ["cargo"]),
    ("iso_container_blue", _c_iso1, ["cargo"]), ("iso_container_hazard", _c_iso2, ["cargo"]),
    ("pod_pressurised_long", _c_pod_horiz, ["cargo"]), ("pod_pressurised_tall", _c_pod_vert, ["cargo"]),
    ("strapped_single", _c_strapped, ["cargo"]), ("strapped_pair", _c_strapped_pair, ["cargo"]),
    ("cage_small", _c_cage_small, ["cargo"]), ("cage_large", _c_cage_large, ["cargo"]),
    ("plank_crate_24", _c_plank24, ["cargo"]), ("hard_case", _c_hardcase, ["cargo"]), ("vault_armoured", _c_vault, ["cargo"]),
    ("cold_chain", _c_cold, ["cargo"]), ("upright_locker", _c_locker_up, ["cargo"]), ("biohazard", _c_biohaz, ["cargo"]),
]


def _dispatch(table, budget=450):
    """Generator wrapper: drops box bevels once the triangle budget is spent (keeps GLBs small)."""
    def gen(m, i, label, rng):
        raw = m.box

        def box(size, pos=(0, 0, 0), mat="hull_mid", bevel=0.0, rot=(0, 0, 0)):
            if bevel and m.tris() > budget:
                bevel = 0.0
            return raw(size, pos, mat, bevel, rot)
        m.box = box
        table[i][1](m, rng)
    return gen


family("crate", [c[0] for c in CRATES], mount="floor", tags=["cargo"], solid=True)(_dispatch(CRATES))


# ---------------------------------------------------------------- barrels
def drum(m, x, z, y0=0.0, r=0.29, h=0.88, mat="cg_blue", rings=2, seg=12, lid="steel", hz=None):
    m.cyl(r, h, (x, y0 + h / 2, z), mat, seg=seg)
    m.cyl(r + 0.012, 0.03, (x, y0 + h - 0.015, z), lid, seg=seg)
    m.cyl(r + 0.012, 0.03, (x, y0 + 0.015, z), lid, seg=seg)
    for k in range(rings):
        yy = y0 + h * (k + 1) / (rings + 1)
        m.cyl(r + 0.006, 0.035, (x, yy, z), mat, seg=seg, cap=False)
    m.cyl(r * 0.9, 0.012, (x, y0 + h + 0.004, z), lid, seg=seg)
    m.cyl(0.035, 0.03, (x + r * 0.45, y0 + h + 0.02, z), "black_metal", seg=8)
    m.cyl(0.025, 0.03, (x - r * 0.35, y0 + h + 0.02, z + r * 0.3), "black_metal", seg=8)
    if hz:
        m.cyl(r + 0.006, 0.12, (x, y0 + h * 0.55, z), "hazard_yellow", seg=seg)
        m.cyl(r + 0.008, 0.02, (x, y0 + h * 0.55 + 0.06, z), "black_metal", seg=seg)
        m.cyl(r + 0.008, 0.02, (x, y0 + h * 0.55 - 0.06, z), "black_metal", seg=seg)


def _b_steel(m, r):
    drum(m, 0, 0, 0, 0.29, 0.88, "cg_blue", 2)
    m.box((0.14, 0.09, 0.005), (0, 0.5, 0.292), "paint_white")
    m.box((0.1, 0.012, 0.006), (0, 0.51, 0.295), "black_metal")


def _b_steel_pair(m, r):
    drum(m, -0.32, 0, 0, 0.29, 0.88, "paint_red", 2)
    # lying drum on chocks
    m.box((0.08, 0.15, 0.7), (0.5, 0.075, 0.0), "wood_dark", 0.005)
    m.box((0.08, 0.15, 0.7), (0.8, 0.075, 0.0), "wood_dark", 0.005)
    m.cyl(0.29, 0.88, (0.65, 0.42, 0.0), "paint_grey", axis="x", seg=16)
    for k in (-0.2, 0.0, 0.2):
        m.torus(0.294, 0.012, (0.65 + k * 1.2, 0.42, 0), "paint_grey", axis="x", seg=16, tseg=4)
    m.cyl(0.3, 0.03, (0.2, 0.42, 0), "steel", axis="x", seg=16)
    m.cyl(0.3, 0.03, (1.1, 0.42, 0), "steel", axis="x", seg=16)
    m.cyl(0.04, 0.03, (0.19, 0.55, 0.1), "black_metal", axis="x", seg=8)


def _b_plastic(m, r):
    R, H = 0.28, 0.9
    m.cyl(R, H, (0, H / 2, 0), "cg_ptl_blue", seg=18)
    m.cyl(R - 0.01, 0.02, (0, H - 0.01, 0), "cg_ptl_blue", seg=18)
    for y in (0.15, 0.4, 0.65):
        m.torus(R + 0.003, 0.012, (0, y, 0), "cg_ptl_blue", seg=18, tseg=4)
    m.cyl(R + 0.03, 0.06, (0, H + 0.02, 0), "cg_ptl_blue", seg=18)
    m.cyl(R + 0.04, 0.05, (0, H - 0.02, 0), "steel", seg=18)
    m.box((0.04, 0.05, 0.06), (R + 0.06, H - 0.01, 0), "black_metal", 0.005)
    m.cyl(0.045, 0.04, (0.12, H + 0.06, 0.1), "plastic_black", seg=8)
    m.cyl(0.05, 0.04, (-0.1, H + 0.06, -0.1), "paint_red", seg=8)
    m.box((0.2, 0.15, 0.006), (0, 0.5, R), "paint_white")


def _b_chem_haz(m, r):
    drum(m, 0, 0, 0, 0.29, 0.9, "cg_ptl_yellow", 2, hz=True)
    m.box((0.2, 0.2, 0.01), (0, 0.32, 0.29), "paint_red", rot=(0, 0, 0.785))
    m.box((0.06, 0.06, 0.012), (0, 0.32, 0.292), "black_metal", rot=(0, 0, 0.785))


def _b_toxic(m, r):
    m.box((1.0, 0.1, 0.9), (0, 0.05, 0), "hazard_yellow", 0.01)
    m.box((0.9, 0.02, 0.8), (0, 0.105, 0), "black_metal")
    for k in range(6):
        m.box((0.02, 0.02, 0.8), (-0.4 + k * 0.16, 0.12, 0), "steel")
    drum(m, -0.22, 0, 0.12, 0.27, 0.85, "cg_darkgreen", 2, hz=True)
    drum(m, 0.24, 0.05, 0.12, 0.27, 0.85, "cg_darkgreen", 2)
    m.box((0.12, 0.12, 0.01), (0.24, 0.55, 0.325), "hazard_yellow", rot=(0, 0, 0.785))
    m.cyl(0.03, 0.06, (0.46, 0.18, 0.4), "em_amber", seg=6)


def _jerry(m, x, y, z, col, rot=0.0):
    m.box((0.34, 0.5, 0.16), (x, y + 0.25, z), col, 0.03, (0, rot, 0))
    m.box((0.12, 0.04, 0.10), (x, y + 0.52, z), col, 0.01, (0, rot, 0))
    m.cyl(0.03, 0.05, (x + 0.1 * math.cos(rot), y + 0.545, z - 0.1 * math.sin(rot)), "black_metal", seg=8)
    m.box((0.1, 0.04, 0.02), (x, y + 0.5, z), "black_metal", 0.005, (0, rot, 0))
    m.box((0.34, 0.02, 0.005), (x, y + 0.25, z + 0.083), "hull_dark", 0, (0, rot, 0)) if rot == 0 else None
    for k in range(3):
        m.box((0.3, 0.012, 0.01), (x, y + 0.12 + k * 0.12, z), col, 0, (0, rot, 0))


def _b_jerry(m, r):
    _jerry(m, 0, 0, 0, "paint_red")
    m.box((0.12, 0.08, 0.01), (0, 0.25, 0.086), "paint_white")


def _b_jerry_rack(m, r):
    for sx in (-1, 1):
        m.box((0.05, 0.9, 0.5), (sx * 0.62, 0.45, 0), "hull_dark", 0.005)
        m.box((0.05, 0.05, 0.6), (sx * 0.62, 0.02, 0), "black_metal")
    for y in (0.08, 0.5):
        m.box((1.3, 0.04, 0.5), (0, y, 0), "steel", 0.005)
    m.box((1.3, 0.05, 0.05), (0, 0.85, -0.22), "hull_dark")
    cols = ["paint_red", "cg_olive", "cg_ptl_yellow", "paint_red", "cg_olive", "paint_orange"]
    for k in range(6):
        row, col = divmod(k, 3)
        _jerry(m, -0.4 + col * 0.4, 0.1 + row * 0.42, 0.0, cols[k])
    for row in (0, 1):
        m.box((1.2, 0.03, 0.02), (0, 0.4 + row * 0.42, 0.22), "cg_strap")


def _cyl_gas(m, x, z, y0, col, h=1.3, R=0.11):
    m.cyl(R, h - 0.2, (x, y0 + (h - 0.2) / 2, z), col, seg=10)
    m.sphere(R, (x, y0 + h - 0.2, z), col, 10, 5, (1, 0.7, 1))
    m.cyl(0.05, 0.1, (x, y0 + h - 0.05, z), "steel", seg=8)
    m.cyl(0.02, 0.08, (x + 0.05, y0 + h - 0.1, z), "brass", axis="x", seg=6)
    m.box((0.02, 0.02, 0.1), (x, y0 + h + 0.03, z), "black_metal")
    m.cyl(R + 0.005, 0.03, (x, y0 + 0.02, z), "black_metal", seg=12)


def _b_gas_rack(m, r):
    cols = ["paint_green", "paint_blue", "paint_red", "paint_white", "paint_orange", "cg_darkgreen"]
    m.box((0.9, 0.06, 0.6), (0, 0.03, 0), "hull_dark", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.05, 1.3, 0.05), (sx * 0.43, 0.65, sz * 0.27), "hazard_yellow", 0.006)
    m.box((0.9, 0.05, 0.05), (0, 1.0, 0.27), "hazard_yellow")
    m.box((0.9, 0.05, 0.05), (0, 1.0, -0.27), "hazard_yellow")
    m.box((0.05, 0.05, 0.54), (-0.43, 1.0, 0), "hazard_yellow")
    m.box((0.05, 0.05, 0.54), (0.43, 1.0, 0), "hazard_yellow")
    for k in range(6):
        row, col = divmod(k, 3)
        _cyl_gas(m, -0.27 + col * 0.27, -0.15 + row * 0.3, 0.06, cols[k], 1.25)
    m.box((0.9, 0.03, 0.02), (0, 0.85, 0.3), "black_metal")
    m.box((0.9, 0.03, 0.02), (0, 0.55, 0.3), "black_metal")
    m.box((0.2, 0.12, 0.01), (0.3, 1.25, 0.28), "paint_white")


def _b_gas_trolley(m, r):
    m.box((0.06, 1.2, 0.06), (0, 0.6, -0.15), "paint_orange", 0.008)
    m.box((0.5, 0.05, 0.4), (0, 0.12, 0.05), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.cyl(0.14, 0.05, (sx * 0.3, 0.14, -0.15), "rubber", axis="x", seg=14)
        m.cyl(0.05, 0.06, (sx * 0.3, 0.14, -0.15), "steel", axis="x", seg=8)
        m.box((0.03, 0.03, 0.03), (sx * 0.22, 0.14, -0.15), "steel")
        m.box((0.03, 1.15, 0.03), (sx * 0.2, 0.62, -0.17), "paint_orange")
    m.box((0.46, 0.05, 0.05), (0, 1.15, -0.17), "paint_orange")
    m.cyl(0.03, 0.4, (0, 1.2, -0.17), "black_metal", axis="x", seg=8)
    _cyl_gas(m, -0.12, 0.1, 0.14, "paint_teal", 1.2)
    _cyl_gas(m, 0.12, 0.1, 0.14, "paint_white", 1.2)
    m.box((0.46, 0.04, 0.02), (0, 0.7, 0.2), "cg_strap")
    m.cyl(0.04, 0.05, (0, 0.03, 0.27), "rubber", axis="x", seg=8)


def _b_canister_cluster(m, r):
    pts = [(0, 0)] + [(0.24 * math.cos(a * PI / 3), 0.24 * math.sin(a * PI / 3)) for a in range(6)]
    cols = ["paint_grey", "paint_orange", "paint_blue", "paint_grey", "paint_orange", "paint_teal", "paint_grey"]
    m.cyl(0.42, 0.06, (0, 0.03, 0), "hull_dark", seg=8, bevel=0.01)
    for (x, z), c in zip(pts, cols):
        m.cyl(0.11, 0.55, (x, 0.34, z), c, seg=10)
        m.cyl(0.08, 0.05, (x, 0.635, z), "steel", seg=8)
        m.cyl(0.03, 0.08, (x, 0.69, z), "brass", seg=6)
        m.torus(0.112, 0.008, (x, 0.5, z), "black_metal", seg=10, tseg=4)
    for y in (0.2, 0.5):
        m.torus(0.37, 0.012, (0, y, 0), "cg_strap", seg=16, tseg=4)


def _b_cryo(m, r):
    m.cyl(0.32, 0.07, (0, 0.2, 0), "hull_dark", seg=16)
    for a in range(3):
        m.link((0.25 * math.cos(a * 2.09), 0.24, 0.25 * math.sin(a * 2.09)), (0.3 * math.cos(a * 2.09), 0.02, 0.3 * math.sin(a * 2.09)), 0.025, "steel", 6)
    m.cyl(0.3, 0.8, (0, 0.65, 0), "brushed_alu", seg=20)
    m.sphere(0.3, (0, 1.05, 0), "brushed_alu", 20, 8, (1, 0.6, 1))
    m.cyl(0.08, 0.18, (0, 1.3, 0), "chrome", seg=10)
    m.cyl(0.11, 0.04, (0, 1.4, 0), "steel", seg=10)
    m.cyl(0.03, 0.12, (0.12, 1.32, 0), "brass", axis="x", seg=6)
    m.cyl(0.05, 0.03, (0.0, 1.06, 0.3), "black_metal", axis="z", seg=10)
    m.cyl(0.04, 0.01, (0.0, 1.06, 0.325), "em_cyan", axis="z", seg=10)
    m.torus(0.305, 0.02, (0, 0.4, 0), "cg_frost", seg=20, tseg=5)
    m.cyl(0.31, 0.25, (0, 0.33, 0), "cg_frost", seg=20)
    m.box((0.14, 0.1, 0.006), (0, 0.72, 0.3), "paint_blue")
    m.link((0.1, 1.42, 0), (0.28, 1.05, 0.15), 0.014, "black_metal", 6)


def _b_cryo_cart(m, r):
    m.box((1.1, 0.06, 0.6), (0, 0.24, 0), "hull_dark", 0.01)
    m.box((1.1, 0.03, 0.62), (0, 0.27, 0), "steel")
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.1, 0.05, (sx * 0.5, 0.1, sz * 0.24), "rubber", axis="x", seg=12)
            m.box((0.04, 0.12, 0.04), (sx * 0.5, 0.17, sz * 0.24), "steel")
    m.box((0.04, 0.95, 0.04), (-0.53, 0.75, -0.28), "hull_dark")
    m.box((0.04, 0.95, 0.04), (-0.53, 0.75, 0.28), "hull_dark")
    m.box((0.05, 0.05, 0.6), (-0.53, 1.22, 0), "black_metal")
    for k, x in enumerate((-0.25, 0.05, 0.35)):
        m.cyl(0.13, 0.5, (x, 0.55, 0), "brushed_alu", seg=14)
        m.sphere(0.13, (x, 0.8, 0), "brushed_alu", 14, 6, (1, 0.7, 1))
        m.cyl(0.04, 0.1, (x, 0.9, 0), "chrome", seg=8)
        m.cyl(0.035, 0.012, (x, 0.5, 0.13), "em_cyan", axis="z", seg=8)
        m.torus(0.13, 0.008, (x, 0.35, 0), "cg_frost", seg=14, tseg=4)
    m.box((1.0, 0.03, 0.02), (0, 0.55, 0.28), "cg_strap")
    m.box((0.6, 0.06, 0.02), (0.15, 0.31, 0.32), "hazard_yellow")


def _b_keg(m, r):
    for x in (-0.3, 0.3):
        m.box((0.08, 0.05, 0.8), (x, 0.03, 0), "wood_dark")
    for (x, y, z) in ((-0.3, 0.3, 0.2), (0.3, 0.3, 0.2), (0.0, 0.3, -0.2)):
        pass

    def keg(cx, cy, cz):
        m.cyl(0.24, 0.3, (cx, cy, cz - 0.0), "wood_dark", axis="z", seg=14)
        m.cyl(0.24, 0.1, (cx, cy, cz + 0.2), "wood_dark", axis="z", seg=14, r2=0.2)
        m.cyl(0.24, 0.1, (cx, cy, cz - 0.2), "wood_dark", axis="z", seg=14, r2=0.2)
        m.cyl(0.24, 0.1, (cx, cy, cz + 0.2), "wood_dark", axis="z", seg=14, r2=0.2)
        for zz in (-0.22, -0.1, 0.1, 0.22):
            m.cyl(0.24 if abs(zz) < 0.15 else 0.205, 0.03, (cx, cy, cz + zz), "gunmetal", axis="z", seg=12, cap=False)

    keg(0, 0.4, 0.0)
    # simple: three kegs in a cradle
    keg(0.56, 0.4, 0.0)
    keg(-0.56, 0.4, 0.0)
    keg(0.0, 0.85, 0.0)
    m.box((1.5, 0.04, 0.05), (0, 0.1, 0.32), "wood_dark")
    m.box((1.5, 0.04, 0.05), (0, 0.1, -0.32), "wood_dark")
    m.box((0.06, 0.1, 0.7), (-0.8, 0.1, 0), "wood_dark")
    m.box((0.06, 0.1, 0.7), (0.8, 0.1, 0), "wood_dark")
    m.box((0.14, 0.12, 0.006), (0.0, 0.85, 0.375), "paint_red")


def _b_coolant_pallet(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    for x in (-0.28, 0.28):
        for z in (-0.24, 0.24):
            drum(m, x, z, top, 0.26, 0.85, "cg_ptl_blue", 2)
            m.cyl(0.264, 0.08, (x, top + 0.4, z), "em_cyan", seg=16)
    m.box((1.1, 0.02, 0.02), (0, top + 0.6, 0.52), "cg_strap")
    m.box((1.1, 0.02, 0.02), (0, top + 0.6, -0.52), "cg_strap")
    m.box((0.02, 0.02, 0.98), (0.62, top + 0.6, 0), "cg_strap")
    m.box((0.02, 0.02, 0.98), (-0.62, top + 0.6, 0), "cg_strap")


def _ibc(m, tank, cage, comp=False):
    w, d, h = 1.0, 1.2, 1.15
    if comp:
        top = pallet_plastic(m, w, d, 0, "cg_ptl_green")
    else:
        m.box((w, 0.14, d), (0, 0.07, 0), "steel", 0.01)
        for x in (-0.35, 0, 0.35):
            m.box((0.12, 0.13, d - 0.02), (x, 0.065, 0), "hull_dark")
        top = 0.14
    m.box((w - 0.1, h - 0.1, d - 0.1), (0, top + h / 2, 0), tank, 0.03)
    if tank == "cg_tank":
        m.box((w - 0.16, (h - 0.1) * 0.6, d - 0.16), (0, top + 0.35, 0), "water", 0.02)
    m.cyl(0.15, 0.06, (0, top + h + 0.0, 0.25), "plastic_black", seg=12)
    m.cyl(0.05, 0.04, (0.3, top + h, -0.3), "paint_red", seg=8)
    edges(m, 0, top + h / 2, 0, w, h, d, 0.03, cage, 0.003)
    for k in range(1, 5):
        y = top + h * k / 5
        m.box((w + 0.005, 0.02, d + 0.005), (0, y, 0), cage)
    for k in range(1, 4):
        m.box((0.02, h, d + 0.005), (-w / 2 + k * w / 4, top + h / 2, 0), cage)
    for k in range(1, 4):
        m.box((0.02, h, 0.02), (-w / 2 + k * w / 4, top + h / 2, d / 2 + 0.004), cage)
    m.cyl(0.05, 0.14, (0.0, top + 0.1, d / 2 + 0.06), "brass", axis="z", seg=8)
    m.box((0.05, 0.12, 0.03), (0.0, top + 0.1, d / 2 + 0.14), "paint_red", 0.005)
    m.box((0.3, 0.2, 0.01), (-0.25, top + 0.75, d / 2 + 0.01), "paint_white")
    m.box((0.08, 0.2, 0.01), (0.4, top + 0.6, d / 2 + 0.01), "black_metal")
    m.box((0.05, 0.14, 0.012), (0.4, top + 0.65, d / 2 + 0.014), "em_amber")
    return top


def _b_ibc(m, r):
    _ibc(m, "cg_tank", "steel")


def _b_ibc_comp(m, r):
    top = _ibc(m, "plastic_white", "gunmetal", True)
    m.box((0.5, 0.08, 0.008), (0.1, top + 0.5, 0.606), "hazard_yellow")
    m.box((0.2, 0.2, 0.01), (-0.3, top + 0.55, 0.61), "paint_red", rot=(0, 0, 0.785))
    m.box((0.3, 0.2, 0.2), (0.7, top + 0.15, 0.3), "hull_mid", 0.02)
    m.cyl(0.05, 0.14, (0.7, top + 0.32, 0.3), "steel", seg=10)
    m.link((0.7, top + 0.15, 0.3), (0.5, top + 0.1, 0.55), 0.02, "black_metal", 6)


BARRELS = [
    ("steel_drum_blue", _b_steel), ("steel_drum_pair", _b_steel_pair), ("plastic_drum_lidded", _b_plastic),
    ("chemical_drum_hazard", _b_chem_haz), ("toxic_drums_sump", _b_toxic), ("jerrycan_single", _b_jerry),
    ("jerrycan_rack", _b_jerry_rack), ("gas_cylinder_rack", _b_gas_rack), ("gas_cylinder_trolley", _b_gas_trolley),
    ("canister_cluster", _b_canister_cluster), ("cryo_flask", _b_cryo), ("cryo_flask_cart", _b_cryo_cart),
    ("powder_keg_cradle", _b_keg), ("coolant_drums_pallet", _b_coolant_pallet), ("ibc_tote_steel", _b_ibc),
    ("ibc_tote_composite", _b_ibc_comp),
]
family("barrel", [c[0] for c in BARRELS], mount="floor", tags=["cargo"], solid=True)(_dispatch(BARRELS))


# ---------------------------------------------------------------- pallets
def cbox(m, x, y, z, w, h, d, mat="cardboard", tape=True, rot=0.0, lab=False):
    m.box((w, h, d), (x, y + h / 2, z), mat, 0.01, (0, rot, 0))
    if tape:
        m.box((w * 0.12, 0.004, d * 0.98), (x, y + h + 0.0, z), "cg_tan", 0, (0, rot, 0))
    if lab:
        m.box((w * 0.3, h * 0.25, 0.006), (x, y + h * 0.6, z + d / 2 + 0.002), "paint_white", 0, (0, rot, 0)) if rot == 0 else None


def _p_wood(m, r):
    pallet_wood(m, 1.2, 1.0)
    m.box((0.08, 0.005, 0.03), (0.5, 0.148, 0.47), "paint_white")


def _p_comp(m, r):
    top = pallet_plastic(m, 1.2, 1.0, 0, "cg_ptl_green")
    for x in (-0.4, 0, 0.4):
        for z in (-0.3, 0.3):
            m.box((0.2, 0.01, 0.16), (x, top + 0.003, z), "black_metal")
    m.box((0.1, 0.03, 0.05), (0.5, 0.09, 0.5), "em_green")


def _p_stack_empty(m, r):
    y = 0
    for k in range(5):
        if k % 3 == 2:
            y = pallet_plastic(m, 1.2, 1.0, y, "cg_ptl_blue") + 0.0
        else:
            y = pallet_wood(m, 1.2, 1.0, y, "wood_light" if k % 2 else "cg_pale_wood")
        y -= 0.008
    m.box((1.25, 0.03, 0.03), (0, 0.5, 0.52), "cg_strap")
    m.box((1.25, 0.03, 0.03), (0, 0.9, 0.52), "cg_strap")


def _p_boxes(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    y = top
    for L in range(3):
        for i in range(2):
            for j in range(2):
                cbox(m, -0.3 + i * 0.6, y, -0.245 + j * 0.49, 0.58, 0.32, 0.48, "cardboard" if (i + j + L) % 3 else "cg_tan", True, lab=(j == 1))
        y += 0.32
    for x in (-0.6, 0.6):
        pass
    m.box((1.22, 0.03, 0.02), (0, top + 0.5, 0.505), "plastic_black")
    m.box((0.02, 0.03, 1.02), (0.61, top + 0.5, 0), "plastic_black")
    m.box((0.02, 0.03, 1.02), (-0.61, top + 0.5, 0), "plastic_black")
    m.box((1.22, 0.03, 0.02), (0, top + 0.5, -0.505), "plastic_black")


def _wrap(m, w, h, d, y0, cx=0.0):
    m.box((w + 0.03, h + 0.02, d + 0.03), (cx, y0 + h / 2, 0), "cg_wrap", 0.02)
    for k in range(3):
        m.box((w + 0.04, 0.012, d + 0.04), (cx, y0 + h * (k + 1) / 4, 0), "cg_wrap")


def _p_wrap(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    y = top
    for L in range(3):
        for i in range(2):
            cbox(m, -0.3 + i * 0.6, y, 0, 0.58, 0.4, 0.9, ["cg_orange", "cardboard", "cg_blue"][L] if i == 0 else "cardboard", False)
        y += 0.4
    _wrap(m, 1.2, y - top + 0.03, 1.0, top - 0.02)
    m.box((0.3, 0.2, 0.01), (0.3, top + 0.7, 0.522), "paint_white")
    m.box((0.2, 0.03, 0.012), (0.3, top + 0.72, 0.526), "black_metal")


def _p_wrap_tall(m, r):
    top = pallet_plastic(m, 1.2, 1.0, 0, "cg_ptl_grey") if False else pallet_plastic(m, 1.2, 1.0, 0, "plastic_grey")
    y = top
    for L, (h, col) in enumerate([(0.5, "cg_olive"), (0.4, "hazard_yellow"), (0.6, "cg_blue"), (0.35, "cardboard")]):
        for i in range(2):
            m.box((0.55, h, 0.95), (-0.29 + i * 0.58, y + h / 2, 0), col if (L + i) % 2 == 0 else "cardboard", 0.015)
        y += h
    _wrap(m, 1.2, y - top, 1.0, top)
    m.box((1.26, 0.06, 0.03), (0, top + 0.9, 0.52), "cg_strap")
    m.box((0.6, 0.05, 0.03), (0, y + 0.02, 0.0), "cg_wrap")
    m.box((1.18, 0.1, 0.06), (0, y + 0.05, 0), "cg_wrap")


def _p_drums(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    cols = ["paint_grey", "cg_olive", "paint_grey", "cg_olive"]
    k = 0
    for x in (-0.28, 0.28):
        for z in (-0.24, 0.24):
            drum(m, x, z, top, 0.26, 0.85, cols[k], 2)
            k += 1
    m.box((1.2, 0.03, 0.03), (0, top + 0.7, 0.53), "black_metal")
    m.box((1.2, 0.03, 0.03), (0, top + 0.7, -0.53), "black_metal")
    m.box((0.03, 0.03, 1.06), (0.61, top + 0.7, 0), "black_metal")
    m.box((0.03, 0.03, 1.06), (-0.61, top + 0.7, 0), "black_metal")


def _cage_panel_mesh(m, x0, x1, y0, y1, z, n, mat="steel", axis="z"):
    pass


def _roll_cage(m, loaded=False):
    w, d, h = 0.8, 0.7, 1.7
    m.box((w, 0.05, d), (0, 0.16, 0), "hull_mid", 0.005)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.075, 0.04, (sx * 0.32, 0.075, sz * 0.27), "rubber", axis="z", seg=10)
            m.box((0.06, 0.08, 0.06), (sx * 0.32, 0.12, sz * 0.27), "steel")
    # frame
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.03, h - 0.2, 0.03), (sx * (w / 2 - 0.015), 0.19 + (h - 0.2) / 2, sz * (d / 2 - 0.015)), "steel")
    for y in (0.4, 1.0, 1.85 - 0.02):
        m.box((w, 0.03, 0.03), (0, y, d / 2 - 0.015), "steel")
        m.box((w, 0.03, 0.03), (0, y, -d / 2 + 0.015), "steel")
    for y in (0.4, 1.0, 1.83):
        m.box((0.03, 0.03, d), (-w / 2 + 0.015, y, 0), "steel")
        m.box((0.03, 0.03, d), (w / 2 - 0.015, y, 0), "steel")
    for k in range(1, 5):
        x = -w / 2 + k * w / 5
        m.box((0.012, h - 0.2, 0.012), (x, 0.19 + (h - 0.2) / 2, -d / 2 + 0.015), "steel")
    for k in range(1, 4):
        z = -d / 2 + k * d / 4
        m.box((0.012, h - 0.2, 0.012), (-w / 2 + 0.015, 0.19 + (h - 0.2) / 2, z), "steel")
        m.box((0.012, h - 0.2, 0.012), (w / 2 - 0.015, 0.19 + (h - 0.2) / 2, z), "steel")
    for k in range(1, 5):
        x = -w / 2 + k * w / 5
        m.box((0.012, 0.5, 0.012), (x, 0.44, d / 2 - 0.015), "steel")
    m.box((w, 0.03, 0.03), (0, 0.7, d / 2 - 0.015), "paint_orange")
    if loaded:
        for k, (yy, hh, col) in enumerate([(0.185, 0.4, "cardboard"), (0.585, 0.45, "cg_tan"), (1.035, 0.4, "cardboard")]):
            m.box((0.66, hh, 0.56), (0.0, yy + hh / 2, -0.02), col, 0.01)
            m.box((0.66, 0.02, 0.05), (0.0, yy + hh / 2, 0.265), "cg_strap")
        m.box((0.4, 0.3, 0.3), (0.0, 1.6, -0.05), "cg_blue", 0.01)


def _p_roll(m, r):
    _roll_cage(m, False)


def _p_roll_loaded(m, r):
    _roll_cage(m, True)
    m.box((0.6, 0.2, 0.01), (0, 0.64, 0.33), "paint_white")


def _p_mixed(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    cbox(m, -0.3, top, -0.2, 0.55, 0.4, 0.5, "cardboard")
    cbox(m, 0.3, top, -0.25, 0.5, 0.3, 0.45, "cg_tan")
    m.box((0.5, 0.35, 0.45), (0.3, top + 0.475, -0.25), "cg_olive", 0.015)
    drum(m, -0.3, 0.25, top, 0.22, 0.7, "paint_red", 1)
    m.box((0.5, 0.45, 0.4), (0.3, top + 0.225, 0.28), "hazard_yellow", 0.015)
    m.box((0.3, 0.14, 0.008), (0.3, top + 0.24, 0.482), "black_metal")
    m.box((0.5, 0.25, 0.3), (-0.3, top + 0.525, -0.2), "cg_orange", 0.015)
    m.sphere(0.13, (0.02, top + 0.16, 0.05), "cg_burlap", 10, 6, (1.4, 0.8, 1))


def _p_sacks(m, r):
    top = pallet_wood(m, 1.2, 1.0)
    for L in range(3):
        for i in range(2):
            for j in range(3):
                dx = (r.random() - 0.5) * 0.03
                x = -0.3 + i * 0.6 if L % 2 == 0 else -0.3 + j * 0 + i * 0.6
                z = -0.33 + j * 0.33 if L % 2 == 0 else -0.33 + j * 0.33 + 0.02
                m.sphere(0.3, (x + dx, top + 0.11 + L * 0.2, z), "cg_burlap" if (i + j + L) % 4 else "fabric_tan", 8, 5, (1.0, 0.42, 0.62))
    m.box((1.24, 0.02, 0.02), (0, top + 0.4, 0.53), "plastic_black")
    m.box((1.24, 0.02, 0.02), (0, top + 0.4, -0.53), "plastic_black")


def _rack_bay(m, levels, loaded):
    W, D = 2.7, 1.1
    H = levels * 1.5 + 0.2
    for sx in (-1, 1):
        for zz in (-1, 1):
            m.box((0.1, H, 0.06), (sx * (W / 2 - 0.05), H / 2, zz * (D / 2 - 0.03)), "cg_blue", 0.005)
            m.box((0.16, 0.4, 0.14), (sx * (W / 2 - 0.05), 0.2, zz * (D / 2 - 0.03)), "hazard_yellow", 0.008)
    for zz in (-1, 1):
        for k in range(levels):
            for hh in (0.2,) if False else ():
                pass
        for y in (0.9, 1.9, 2.9, 3.9)[:levels + (1 if levels > 2 else 0)] if False else []:
            pass
    # frames
    for sx in (-1, 1):
        m.box((0.05, 0.05, D), (sx * (W / 2 - 0.05), 0.15, 0), "cg_blue")
        for k in range(levels):
            pass
        y = 0.2
        while y < H - 0.1:
            m.link((sx * (W / 2 - 0.05), y, D / 2 - 0.03), (sx * (W / 2 - 0.05), y + 0.9, -D / 2 + 0.03), 0.012, "cg_blue", 6)
            y += 1.0
    tops = []
    for k in range(levels):
        y = 0.35 + k * 1.5 if levels == 3 else 0.35 + k * 1.5
        for zz in (-1, 1):
            m.box((W, 0.12, 0.06), (0, y, zz * (D / 2 - 0.03)), "paint_orange", 0.006)
        for x in (-0.6, 0.6):
            for zz in (-0.4, 0.4):
                pass
        m.box((W - 0.2, 0.012, D - 0.1), (0, y + 0.065, 0), "steel") if loaded == "wire" else None
        tops.append(y + 0.06)
    if loaded:
        for k, y in enumerate(tops):
            for i, x in enumerate((-0.65, 0.65)):
                if (k + i) % 4 == 3 and levels == 3:
                    continue
                m.box((1.2, 0.14, 1.0), (x, y + 0.07, 0), "wood_light", 0.005)
                hh = [0.9, 0.7, 1.1, 0.8][(k + i) % 4] if levels == 3 else [0.9, 1.1][(k + i) % 2]
                col = ["cardboard", "cg_olive", "cg_orange", "cg_blue", "cardboard"][(k * 2 + i) % 5]
                m.box((1.1, hh, 0.9), (x, y + 0.14 + hh / 2, 0), col, 0.02)
                m.box((1.12, 0.03, 0.03), (x, y + 0.14 + hh * 0.6, 0.46), "plastic_black")
                if (k + i) % 2:
                    m.box((1.14, hh + 0.02, 1.0), (x, y + 0.14 + hh / 2, 0), "cg_wrap")
    if levels > 2:
        pass


def _p_rack3(m, r):
    _rack_bay(m, 3, True)


def _p_rack2(m, r):
    _rack_bay(m, 2, "wire")


def _p_crates_banded(m, r):
    top = pallet_plastic(m, 1.2, 1.0, 0, "cg_ptl_yellow")
    for i, (h, col) in enumerate([(0.9, "cg_olive"), (0.9, "cg_maroon")]):
        x = -0.3 + i * 0.6
        m.box((0.56, h, 0.9), (x, top + h / 2, 0), col, 0.02)
        m.box((0.6, 0.06, 0.94), (x, top + h + 0.01, 0), "steel", 0.006)
    for y in (0.35, 0.8):
        for z in (-0.47, 0.47):
            m.box((1.2, 0.03, 0.02), (0, top + y, z), "plastic_black")
        for x in (-0.61, 0.61):
            m.box((0.02, 0.03, 0.94), (x, top + y, 0), "plastic_black")
    for x in (-0.6, 0.6):
        for z in (-0.5, 0.5):
            m.box((0.05, 0.9, 0.05), (x, top + 0.45, z), "cardboard")
    m.box((0.3, 0.2, 0.01), (-0.3, top + 0.55, 0.455), "paint_white")
    m.box((0.2, 0.1, 0.012), (0.3, top + 0.55, 0.455), "hazard_yellow")


PALLETS = [
    ("wooden_empty", _p_wood), ("composite_empty", _p_comp), ("empty_stack", _p_stack_empty),
    ("boxes_layered", _p_boxes), ("wrapped_stack", _p_wrap), ("wrapped_tall_mixed", _p_wrap_tall),
    ("drums_banded", _p_drums), ("roll_cage_empty", _p_roll), ("roll_cage_loaded", _p_roll_loaded),
    ("mixed_goods", _p_mixed), ("sacks_stacked", _p_sacks), ("rack_bay_loaded", _p_rack3),
    ("rack_bay_low_wire", _p_rack2), ("crates_banded", _p_crates_banded),
]
family("pallet", [c[0] for c in PALLETS], mount="floor", tags=["cargo"], solid=True)(_dispatch(PALLETS))


# ---------------------------------------------------------------- shelving
def shelf_frame(m, W, D, H, ys, up="cg_blue", beam="paint_orange", deck="steel", y0=0.0):
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.06, H, 0.06), (sx * (W / 2 - 0.03), y0 + H / 2, sz * (D / 2 - 0.03)), up, 0.004)
            m.box((0.1, 0.02, 0.1), (sx * (W / 2 - 0.03), y0 + 0.01, sz * (D / 2 - 0.03)), "black_metal")
    for y in ys:
        for sz in (-1, 1):
            m.box((W, 0.08, 0.04), (0, y0 + y, sz * (D / 2 - 0.05)), beam, 0.004)
        m.box((W - 0.1, 0.015, D - 0.08), (0, y0 + y + 0.045, 0), deck)


def _boxes_on(m, x0, x1, y, D, r, hmax=0.4, z=0.0):
    x = x0
    while x < x1 - 0.2:
        w = r.uniform(0.25, 0.5)
        w = min(w, x1 - x - 0.03)
        h = r.uniform(0.2, hmax)
        d = min(D - 0.14, r.uniform(0.3, 0.5))
        col = r.choice(["cardboard", "cg_tan", "cg_olive", "cg_ptl_blue", "cardboard", "plastic_grey", "cg_orange"])
        m.box((w, h, d), (x + w / 2, y + h / 2, z), col, 0.008)
        if r.random() < 0.6:
            m.box((w * 0.5, 0.008, d + 0.004), (x + w / 2, y + h, z), "cg_strap" if col != "cardboard" else "cg_tan")
        x += w + 0.03


def _s_heavy(m, r):
    W, D, H = 2.2, 0.65, 2.3
    ys = [0.3, 0.9, 1.5, 2.1]
    shelf_frame(m, W, D, H, ys)
    for y in ys[:-1]:
        _boxes_on(m, -W / 2 + 0.1, W / 2 - 0.1, y + 0.055, D, r, 0.5)
    for y in ys[:-1]:
        m.box((0.18, 0.06, 0.01), (0.6, y - 0.0, D / 2 - 0.0), "paint_white")
    for sx in (-1, 1):
        pass
    m.box((W, 0.03, 0.03), (0, 2.28, -D / 2 + 0.03), "hazard_yellow")


def _s_cage_locker(m, r):
    W, D, H = 2.1, 0.55, 2.0
    m.box((W, H, D - 0.05), (0, H / 2 + 0.08, -0.02), "hull_dark", 0.01)
    m.box((W + 0.04, 0.08, D), (0, 0.04, 0), "black_metal", 0.005)
    for c in range(3):
        for rr in range(3):
            x = -W / 3 + c * W / 3
            y = 0.06 + H / 6 + rr * H / 3 + 0.02
            m.box((W / 3 - 0.06, H / 3 - 0.06, 0.03), (x, y, D / 2 - 0.015), "steel", 0.004)
            for k in range(1, 4):
                m.box((0.008, H / 3 - 0.1, 0.012), (x - (W / 3 - 0.06) / 2 + k * (W / 3 - 0.06) / 4, y, D / 2 + 0.005), "black_metal")
            for k in range(1, 3):
                m.box((W / 3 - 0.1, 0.008, 0.012), (x, y - (H / 3 - 0.06) / 2 + k * (H / 3 - 0.06) / 3, D / 2 + 0.005), "black_metal")
            m.box((0.05, 0.08, 0.04), (x + 0.24, y, D / 2 + 0.03), "brass", 0.006)
            m.box((0.03, 0.05, 0.02), (x + 0.24, y - 0.09, D / 2 + 0.04), "steel")
            if (c + rr) % 2:
                m.box((0.12, 0.05, 0.01), (x - 0.1, y + 0.3, D / 2 + 0.02), "paint_white")
    m.box((W, 0.05, D), (0, H + 0.1, 0), "hull_mid", 0.008)


def _s_parts_rack(m, r):
    W, D, H = 1.6, 0.5, 2.0
    shelf_frame(m, W, D, H, [0.25, 0.7, 1.15, 1.6], "paint_grey", "hull_dark", "hull_mid")
    cols = ["cg_ptl_red", "cg_ptl_blue", "cg_ptl_yellow", "cg_ptl_green"]
    for row, y in enumerate([0.25, 0.7, 1.15, 1.6]):
        nb = 3 if row % 2 == 0 else 4
        bw = (W - 0.16) / nb
        for k in range(nb):
            x = -W / 2 + 0.08 + bw * (k + 0.5)
            col = cols[(k + row) % 4]
            h = 0.22
            m.box((bw - 0.03, h, 0.34), (x, y + 0.055 + h / 2, 0.0), col, 0.008)
            m.box((bw - 0.05, 0.08, 0.02), (x, y + 0.12, 0.18), "hull_dark")
            m.box((bw - 0.09, 0.06, 0.008), (x, y + 0.08, 0.191), "paint_white")
            for j in range(1):
                m.cyl(0.02, 0.12, (x - 0.03 + j * 0.05, y + 0.055 + h + 0.03, 0.02), "brass" if j else "copper", axis="z", seg=6)


def _s_pigeon(m, r):
    W, D, H = 1.6, 0.45, 1.9
    nx, ny = 4, 5
    m.box((W, H, 0.03), (0, H / 2 + 0.1, -D / 2 + 0.015), "hull_dark")
    for k in range(nx + 1):
        m.box((0.03, H, D), (-W / 2 + k * W / nx, H / 2 + 0.1, 0), "wood_dark" if False else "hull_mid", 0.004)
    for k in range(ny + 1):
        m.box((W, 0.03, D), (0, 0.1 + k * H / ny, 0), "hull_mid", 0.004)
    m.box((W + 0.1, 0.1, D + 0.05), (0, 0.05, 0), "black_metal", 0.006)
    for a in range(nx):
        for b in range(ny):
            x = -W / 2 + (a + 0.5) * W / nx
            y = 0.1 + b * H / ny + 0.03
            k = (a * 3 + b * 5) % 7
            if k == 0:
                m.cyl(0.05, 0.3, (x, y + 0.05, 0), "cg_tan", axis="z", seg=8)
            elif k == 1:
                m.box((0.25, 0.2, 0.3), (x, y + 0.1, 0), "cardboard", 0.005)
            elif k == 2:
                m.cyl(0.07, 0.3, (x, y + 0.07, 0.0), "paint_grey", axis="z", seg=10)
            elif k == 3:
                m.box((0.3, 0.06, 0.3), (x, y + 0.03, 0), "cg_olive")
            elif k == 4:
                m.sphere(0.09, (x, y + 0.09, 0.0), "cg_ptl_red", 8, 6)
            fb(m, "f", (x, y - 0.03, D / 2), 0, 0, 0.0, 0.14, 0.03, 0.01, "paint_white") if b % 2 == 0 else None


def _s_mobile(m, r):
    # two carriages on rails with a handwheel
    W, D, H = 1.8, 0.6, 2.0
    for z in (-0.42, 0.42):
        m.box((2.5, 0.05, 0.06), (0, 0.025, z), "black_metal")
    for z in (-0.42, 0.42):
        for x in (-1.2, 1.2):
            pass
    for uz, zz in ((0, -0.42 - 0.0), ):
        pass
    for k, x0 in enumerate((-0.55, 0.55)):
        pass
    for k, xc in enumerate((-0.6, 0.7)):
        m.box((0.55, 0.14, 1.2), (xc, 0.1, 0), "hull_dark", 0.008)
        for z in (-0.42, 0.42):
            m.cyl(0.05, 0.06, (xc - 0.15, 0.06, z), "steel", axis="z", seg=10)
            m.cyl(0.05, 0.06, (xc + 0.15, 0.06, z), "steel", axis="z", seg=10)
        for sx in (-1, 1):
            for sz in (-1, 1):
                m.box((0.05, 1.9, 0.05), (xc + sx * 0.25, 1.05, sz * 0.55), "cg_blue", 0.004)
        for y in (0.4, 0.95, 1.5, 2.0):
            m.box((0.55, 0.05, 1.15), (xc, y, 0), "paint_grey", 0.005)
        for y in (0.4, 0.95, 1.5):
            for j in range(2):
                z = -0.28 + j * 0.56
                cw = r.uniform(0.3, 0.42)
                ch = r.uniform(0.2, 0.42)
                m.box((0.4, ch, cw), (xc, y + 0.025 + ch / 2, z), r.choice(["cardboard", "cg_olive", "cg_ptl_blue", "cg_tan"]), 0.008)
        m.box((0.55, 0.05, 1.2), (xc, 2.05, 0), "cg_blue")
    # handwheel on the end of the left carriage
    m.box((0.08, 0.5, 0.05), (-0.6, 1.0, 0.66), "black_metal")
    m.cyl(0.14, 0.03, (-0.6, 1.0, 0.7), "chrome", axis="z", seg=16)
    m.torus(0.14, 0.014, (-0.6, 1.0, 0.71), "black_metal", axis="z", seg=14, tseg=5)
    for a in range(3):
        m.box((0.02, 0.28, 0.02), (-0.6, 1.0, 0.71), "black_metal", rot=(0, 0, a * 1.047))
    m.cyl(0.02, 0.1, (-0.6, 1.0, 0.65), "steel", axis="z", seg=8)
    m.box((0.25, 0.06, 0.01), (-0.6, 2.05, 0.61), "hazard_yellow")


def _s_tank_shelf(m, r):
    W, D, H = 2.0, 0.7, 2.0
    shelf_frame(m, W, D, H, [0.25, 1.05], "hazard_yellow", "black_metal", "steel")
    m.box((W, 0.06, D), (0, H, 0), "black_metal", 0.005)
    for k in range(4):
        x = -0.7 + k * 0.45
        _cyl_gas(m, x, 0.0, 0.3, ["paint_green", "paint_blue", "paint_white", "paint_red"][k], 0.7 if False else 0.65, 0.09)
    for k in range(4):
        _jerry(m, -0.65 + k * 0.42, 1.1, 0, ["paint_red", "cg_olive", "paint_red", "cg_ptl_yellow"][k])
    m.box((W - 0.1, 0.04, 0.02), (0, 0.6, D / 2 - 0.02), "cg_strap")
    m.box((W - 0.1, 0.04, 0.02), (0, 1.6, D / 2 - 0.02), "cg_strap")
    for sx in (-1, 1):
        pass
    m.box((W - 0.1, 0.5, 0.02), (0, 1.35, -D / 2 + 0.03), "black_metal")
    m.box((0.5, 0.15, 0.01), (0, 1.9, D / 2 + 0.005), "paint_red")


SHELV_FLOOR = [("heavy_boxes", _s_heavy), ("cage_lockers", _s_cage_locker), ("parts_bins_rack", _s_parts_rack),
               ("pigeonhole", _s_pigeon), ("mobile_carriages", _s_mobile), ("gas_and_fuel_shelf", _s_tank_shelf)]
family("shelving", [c[0] for c in SHELV_FLOOR], mount="floor", tags=["cargo"], solid=True)(_dispatch(SHELV_FLOOR))


# wall mounted (origin = centre of back plane, y is +-0.9)
def _w_storage(m, r):
    m.box((1.6, 1.4, 0.03), (0, 0, 0.015), "hull_dark")
    for y in (-0.5, 0.0, 0.5):
        m.box((1.6, 0.04, 0.4), (0, y, 0.22), "steel", 0.004)
        m.box((1.6, 0.06, 0.02), (0, y + 0.05, 0.415), "steel")
        for sx in (-0.75, 0.0, 0.75):
            m.box((0.04, 0.03, 0.36), (sx, y - 0.04, 0.22), "steel")
    _boxes_on(m, -0.75, 0.75, -0.48, 0.5, r, 0.35, 0.2)
    _boxes_on(m, -0.75, 0.75, 0.02, 0.5, r, 0.3, 0.2)
    for k in range(3):
        m.cyl(0.07, 0.3, (-0.55 + k * 0.2, 0.52 + 0.15, 0.2), "paint_grey" if k else "paint_red", seg=10)
    m.box((0.5, 0.25, 0.3), (0.35, 0.65, 0.2), "cg_olive", 0.01)


def _w_cable(m, r):
    m.box((1.4, 1.6, 0.04), (0, 0, 0.02), "hull_dark")
    for y in (-0.6, -0.2, 0.2, 0.6):
        m.box((1.36, 0.05, 0.05), (0, y, 0.065), "steel")
        for k in range(3):
            x = -0.45 + k * 0.45
            c = r.choice(["copper", "em_red", "cg_ptl_blue", "plastic_black", "cg_ptl_yellow", "paint_green"])
            if c == "em_red":
                c = "paint_red"
            m.torus(0.12, 0.05, (x, y - 0.11, 0.11), c, axis="z", seg=10, tseg=4)
            m.box((0.05, 0.14, 0.03), (x, y - 0.03, 0.09), "black_metal")
    m.box((1.36, 0.06, 0.02), (0, 0.85, 0.05), "hazard_yellow")
    for y in (-0.8,):
        m.box((1.2, 0.05, 0.3), (0, y, 0.16), "steel")
        m.cyl(0.14, 0.2, (-0.4, y + 0.14, 0.16), "paint_orange", axis="x", seg=14)
        m.cyl(0.14, 0.2, (0.1, y + 0.14, 0.16), "paint_green", axis="x", seg=14)
        m.cyl(0.14, 0.2, (0.5, y + 0.14, 0.16), "cg_ptl_blue", axis="x", seg=14)


def _w_bins(m, r):
    m.box((1.8, 1.5, 0.03), (0, 0, 0.015), "hull_dark")
    for k in range(6):
        m.box((1.8, 0.03, 0.08), (0, -0.7 + k * 0.28, 0.07), "steel")
    cols = ["cg_ptl_red", "cg_ptl_blue", "cg_ptl_yellow", "cg_ptl_green", "plastic_grey"]
    for row in range(5):
        y0 = -0.7 + row * 0.28
        n = 3 + (row % 3)
        bw = 1.7 / n
        for k in range(n):
            x = -0.85 + bw * (k + 0.5)
            m.box((bw - 0.03, 0.22, 0.22), (x, y0 + 0.13, 0.15), cols[(k + row) % 5], 0.006)
            m.box((bw - 0.1, 0.05, 0.01), (x, y0 + 0.2, 0.263), "paint_white")
            m.box((bw - 0.06, 0.02, 0.04), (x, y0 + 0.235, 0.24), "black_metal")


def _w_shelf_cans(m, r):
    m.box((1.0, 1.0, 0.03), (0, 0, 0.015), "hull_mid")
    for i, y in enumerate((-0.4, 0.0, 0.4)):
        m.box((1.0, 0.03, 0.25), (0, y, 0.15), "steel", 0.004)
        m.box((1.0, 0.07, 0.015), (0, y + 0.05, 0.27), "steel")
        for sx in (-0.4, 0.4):
            m.box((0.03, 0.14, 0.25), (sx, y - 0.075, 0.15), "steel")
        for k in range(5):
            x = -0.4 + k * 0.2
            if i == 0:
                m.cyl(0.07, 0.24, (x, y + 0.14, 0.14), r.choice(["paint_red", "paint_blue", "paint_grey"]), seg=10)
                m.cyl(0.05, 0.02, (x, y + 0.27, 0.14), "steel", seg=8)
            elif i == 1:
                m.box((0.13, 0.2, 0.14), (x, y + 0.12, 0.14), r.choice(["cg_ptl_yellow", "cardboard", "cg_olive"]), 0.006)
            else:
                m.cyl(0.05, 0.22, (x, y + 0.13, 0.14), r.choice(["plastic_white", "cg_ptl_green", "cg_ptl_yellow"]), seg=8)
                m.cyl(0.03, 0.03, (x, y + 0.255, 0.14), "plastic_black", seg=8)


SHELV_WALL = [("wall_storage_rack", _w_storage), ("hanging_cable_rack", _w_cable),
              ("parts_bin_wall", _w_bins), ("wall_shelf_cans", _w_shelf_cans)]
family("shelving", [c[0] for c in SHELV_WALL], mount="wall", tags=["cargo"], solid=False)(_dispatch(SHELV_WALL))


# ---------------------------------------------------------------- storage bins
def _sb_parts_bins(m, r):
    W, H = 1.2, 1.5
    for sx in (-1, 1):
        m.box((0.05, H, 0.7), (sx * (W / 2 - 0.025), H / 2, 0), "paint_grey", 0.004)
        m.box((0.05, 0.05, 0.75), (sx * (W / 2 - 0.025), 0.025, 0), "black_metal")
    m.box((W, 0.05, 0.06), (0, 0.15, -0.3), "hull_dark")
    cols = ["cg_ptl_red", "cg_ptl_blue", "cg_ptl_yellow", "cg_ptl_green"]
    for row in range(4):
        y = 0.3 + row * 0.3
        m.box((W - 0.1, 0.02, 0.45 - row * 0.05), (0, y - 0.01, -0.05 + row * 0.03), "steel")
        for k in range(4):
            x = -0.45 + k * 0.3
            dpt = 0.4 - row * 0.05
            m.box((0.26, 0.2, dpt), (x, y + 0.1, -0.05 + row * 0.03 - (0.45 - row * 0.05 - dpt) / 2 + 0.0), cols[(k + row) % 4], 0.008)
    m.box((W, 0.05, 0.75), (0, H + 0.02, 0), "hull_dark", 0.004)
    for k in range(4):
        pass


def _sb_tote_stack(m, r):
    m.box((0.68, 0.08, 0.48), (0, 0.13, 0), "hull_dark", 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.05, 0.05, (sx * 0.28, 0.05, sz * 0.18), "rubber", axis="x", seg=8)
    cols = ["cg_ptl_red", "cg_ptl_blue", "cg_ptl_yellow", "cg_ptl_green", "plastic_grey"]
    y = 0.17
    for k in range(5):
        h = 0.26
        m.box((0.6, h, 0.4), (0, y + h / 2, 0), cols[k], 0.015)
        m.box((0.62, 0.03, 0.42), (0, y + h - 0.015, 0), "plastic_black", 0.008)
        m.box((0.28, 0.08, 0.01), (0, y + 0.13, 0.205), "paint_white")
        for s in (-1, 1):
            m.box((0.16, 0.03, 0.03), (s * 0.31, y + 0.18, 0), "black_metal", 0.004)
        y += h + 0.005
    m.box((0.04, 1.2, 0.03), (-0.3, 0.75, -0.22), "hull_mid")
    m.box((0.04, 1.2, 0.03), (0.3, 0.75, -0.22), "hull_mid")
    m.box((0.64, 0.04, 0.05), (0, 1.36, -0.24), "hull_mid")


def _sb_toolbox(m, r):
    w, h, d = 0.5, 0.22, 0.22
    m.box((w, h * 0.6, d), (0, h * 0.3, 0), "paint_red", 0.012)
    m.box((w + 0.01, h * 0.45, d + 0.01), (0, h * 0.75, 0), "paint_red", 0.02)
    m.box((w - 0.05, 0.015, 0.02), (0, h * 0.55, d / 2 + 0.01), "black_metal")
    m.box((0.28, 0.025, 0.03), (0, h + 0.03, 0), "black_metal", 0.006)
    for x in (-0.12, 0.12):
        m.box((0.02, 0.03, 0.03), (x, h + 0.015, 0), "black_metal")
    for x in (-0.16, 0.16):
        latch(m, x, h * 0.55, d / 2 + 0.005, "chrome")
    for x in (-w / 2, w / 2):
        m.box((0.03, 0.1, d + 0.005), (x, h * 0.4, 0), "steel")
    m.box((0.14, 0.05, 0.005), (0, h * 0.35, d / 2 + 0.006), "paint_white")


def _sb_toolchest(m, r):
    W, D = 0.75, 0.5
    m.box((W, 0.9, D), (0, 0.6, 0), "paint_red", 0.012)
    m.box((W + 0.03, 0.04, D + 0.03), (0, 1.07, 0), "black_metal", 0.006)
    m.box((W + 0.03, 0.04, D + 0.03), (0, 0.16, 0), "black_metal", 0.006)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.05, 0.04, (sx * 0.3, 0.06, sz * 0.19), "rubber", axis="x", seg=10)
            m.box((0.03, 0.08, 0.05), (sx * 0.3 + sx * 0.03, 0.11, sz * 0.19), "steel")
    hs = [0.12, 0.12, 0.16, 0.2, 0.2]
    y = 0.2
    for k, h in enumerate(hs):
        m.box((W - 0.06, h - 0.02, 0.02), (0, y + h / 2, D / 2 + 0.005), "paint_red" if False else "hull_dark", 0.004)
        m.box((0.4, 0.025, 0.03), (0, y + h - 0.045, D / 2 + 0.03), "chrome", 0.004)
        y += h
    m.box((0.03, 0.05, 0.03), (-0.3, 1.0, D / 2 + 0.02), "brass")
    for sx in (-1, 1):
        pass
    m.box((0.05, 0.5, 0.05), (-W / 2 - 0.03, 0.75, -0.18), "black_metal")
    m.box((0.05, 0.5, 0.05), (W / 2 + 0.03, 0.75, -0.18), "black_metal")
    m.box((0.6, 0.02, 0.35), (0, 1.1, 0), "rubber")


def _sb_hopper(m, r):
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.08, 1.2, 0.08), (sx * 0.65, 0.6, sz * 0.65), "hull_dark", 0.006)
    for y in (0.4, 1.2):
        m.box((1.4, 0.06, 0.06), (0, y, 0.65), "hull_dark")
        m.box((1.4, 0.06, 0.06), (0, y, -0.65), "hull_dark")
        m.box((0.06, 0.06, 1.4), (0.65, y, 0), "hull_dark")
        m.box((0.06, 0.06, 1.4), (-0.65, y, 0), "hull_dark")
    m.cyl(0.2, 0.9, (0, 1.5, 0), "cg_orange", seg=4, r2=0.95, rot=(0, 0.785, 0))
    m.cyl(0.95, 0.35, (0, 2.12, 0), "cg_orange", seg=4, rot=(0, 0.785, 0))
    m.cyl(0.99, 0.06, (0, 2.32, 0), "steel", seg=4, rot=(0, 0.785, 0))
    for k in range(6):
        m.box((0.02, 0.03, 1.2), (-0.5 + k * 0.2, 2.31, 0), "black_metal")
    m.cyl(0.13, 0.35, (0, 0.62, 0), "steel", seg=12)
    m.cyl(0.16, 0.05, (0, 0.44, 0), "hull_dark", seg=12)
    m.box((0.06, 0.2, 0.06), (0.22, 0.6, 0.0), "paint_red")
    m.cyl(0.05, 0.06, (0.22, 0.72, 0), "black_metal", axis="x", seg=8)


def _sb_compactor(m, r):
    W, D, H = 0.9, 0.85, 1.7
    m.box((W, H, D), (0, H / 2 + 0.08, 0), "cg_darkgreen", 0.02)
    m.box((W + 0.04, 0.08, D + 0.04), (0, 0.04, 0), "black_metal", 0.006)
    B = (0, 0.9, D / 2)
    fb(m, "f", B, 0, -0.35, 0.005, 0.7, 0.75, 0.05, "hull_dark", 0.01)
    fb(m, "f", B, 0, -0.35, 0.03, 0.6, 0.65, 0.02, "cg_darkgreen", 0.008)
    m.box((0.08, 0.3, 0.03), (0.25, 0.55, D / 2 + 0.055), "steel", 0.006)
    m.box((0.5, 0.35, 0.06), (0, 1.45, D / 2 + 0.03), "black_metal", 0.008)
    m.quad((0.42, 0.2), (0, 1.5, D / 2 + 0.062), "screen:power")
    m.cyl(0.05, 0.04, (-0.1, 1.31, D / 2 + 0.05), "paint_red", axis="z", seg=10)
    m.cyl(0.05, 0.04, (0.1, 1.31, D / 2 + 0.05), "paint_green", axis="z", seg=10)
    m.box((0.6, 0.05, 0.6), (0, H + 0.11, 0), "hull_dark", 0.01)
    m.cyl(0.1, 0.5, (0, H + 0.38, 0), "steel", seg=10)
    hazard(m, "f", (0, 0.9, D / 2), 0, -0.65, 0.01, 0.8, 0.07)
    for sx in (-1, 1):
        pass


def _sb_drawer(m, r):
    W, D, H = 0.8, 0.55, 1.4
    m.box((W, H, D), (0, H / 2 + 0.06, 0), "paint_grey", 0.012)
    m.box((W + 0.02, 0.06, D + 0.02), (0, 0.03, 0), "black_metal")
    m.box((W + 0.02, 0.04, D + 0.02), (0, H + 0.08, 0), "hull_dark", 0.006)
    for k in range(8):
        y = 0.12 + k * 0.165
        m.box((W - 0.06, 0.145, 0.02), (0, y + 0.08, D / 2 + 0.005), "hull_mid" if k % 3 else "cg_blue", 0.005)
        m.box((0.3, 0.02, 0.03), (0, y + 0.13, D / 2 + 0.03), "chrome", 0.004)
        m.box((0.12, 0.04, 0.008), (0, y + 0.06, D / 2 + 0.017), "paint_white")


def _sb_ammo_cans(m, r):
    specs = [(-0.2, -0.1, 0.36, 0.18, 0.2, "cg_olive"), (0.15, -0.12, 0.28, 0.2, 0.15, "cg_tan"),
             (-0.05, 0.12, 0.22, 0.22, 0.2, "cg_olive"), (0.3, 0.14, 0.2, 0.13, 0.13, "paint_grey")]
    for x, z, w, h, d, col in specs:
        m.box((w, h, d), (x, h / 2, z), col, 0.01)
        m.box((w + 0.01, 0.03, d + 0.01), (x, h - 0.015, z), col, 0.006)
        m.box((w * 0.5, 0.025, 0.03), (x, h + 0.02, z), "steel", 0.004)
        m.box((0.05, 0.05, 0.02), (x - w * 0.3, h - 0.05, z + d / 2 + 0.008), "steel", 0.004)
        m.box((0.05, 0.05, 0.02), (x + w * 0.3, h - 0.05, z + d / 2 + 0.008), "steel", 0.004)
        m.box((w * 0.5, 0.025, 0.006), (x, h * 0.5, z + d / 2 + 0.004), "hazard_yellow")


def _sb_locker(m, r):
    W, D, H = 1.0, 0.6, 1.9
    m.box((W, H, D), (0, H / 2 + 0.08, 0), "hull_light", 0.02)
    m.box((W + 0.04, 0.08, D + 0.04), (0, 0.04, 0), "black_metal", 0.006)
    B = (0, 1.05, D / 2)
    fb(m, "f", B, 0, 0, 0.005, 0.86, 1.72, 0.05, "hull_mid", 0.02)
    fb(m, "f", B, 0, 0, 0.03, 0.72, 1.58, 0.02, "hull_light", 0.02)
    m.cyl(0.14, 0.05, (0.0, 1.05, D / 2 + 0.06), "steel", axis="z", seg=16)
    m.torus(0.13, 0.015, (0.0, 1.05, D / 2 + 0.09), "chrome", axis="z", seg=16, tseg=5)
    for a in range(4):
        m.box((0.014, 0.26, 0.014), (0, 1.05, D / 2 + 0.09), "chrome", rot=(0, 0, a * 0.785))
    m.cyl(0.04, 0.03, (0, 1.05, D / 2 + 0.1), "chrome", axis="z", seg=8)
    m.cyl(0.11, 0.02, (0.0, 1.65, D / 2 + 0.045), "black_metal", axis="z", seg=12)
    m.cyl(0.08, 0.02, (0.0, 1.65, D / 2 + 0.05), "glass_blue", axis="z", seg=12)
    m.box((0.06, 0.06, 0.02), (0.27, 1.9, D / 2 + 0.045), "em_green")
    for y in (0.35, 1.75):
        m.box((0.04, 0.12, 0.06), (-W / 2 + 0.03, y, D / 2 + 0.02), "steel")
    hazard(m, "f", B, 0, -0.55, 0.05, 0.6, 0.07)


def _sb_trolley(m, r):
    W, D = 0.9, 0.55
    m.box((W, 0.05, D), (0, 0.2, 0), "hull_dark", 0.008)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.075, 0.04, (sx * 0.38, 0.075, sz * 0.2), "rubber", axis="x", seg=12)
            m.box((0.05, 0.1, 0.06), (sx * 0.38, 0.14, sz * 0.2), "steel")
            m.box((0.04, 1.0, 0.04), (sx * 0.4, 0.7, sz * 0.24), "steel", 0.003)
    for y, h in ((0.225, 0.22), (0.7, 0.22)):
        pass
    for k, (y, col) in enumerate([(0.225, "cg_ptl_yellow"), (0.6, "cg_ptl_blue"), (0.98, "cg_ptl_red")]):
        m.box((W - 0.06, 0.03, D - 0.04), (0, y, 0), "steel", 0.004)
        for j in range(3):
            x = -0.27 + j * 0.27
            m.box((0.25, 0.22 if k < 2 else 0.18, 0.4), (x, y + 0.12, 0), col if (j + k) % 2 == 0 else "plastic_grey", 0.01)
            m.box((0.18, 0.06, 0.01), (x, y + 0.1, 0.205), "paint_white")
    m.box((W + 0.1, 0.04, 0.04), (0, 1.22, -D / 2 - 0.02), "steel")
    m.box((0.04, 0.24, 0.04), (-0.4, 1.12, -D / 2 - 0.02), "steel")
    m.box((0.04, 0.24, 0.04), (0.4, 1.12, -D / 2 - 0.02), "steel")


SB_FLOOR = [("parts_bins_stand", _sb_parts_bins), ("tote_stack_dolly", _sb_tote_stack), ("toolchest_wheels", _sb_toolchest),
            ("bulk_hopper", _sb_hopper), ("trash_compactor", _sb_compactor), ("drawer_cabinet", _sb_drawer),
            ("sealed_parts_locker", _sb_locker), ("bin_trolley_floor", _sb_trolley)]
SB_TABLE = [("toolbox_portable", _sb_toolbox), ("ammo_cans", _sb_ammo_cans)]
family("storagebin", [c[0] for c in SB_FLOOR], mount="floor", tags=["cargo"], solid=True)(_dispatch(SB_FLOOR))
family("storagebin", [c[0] for c in SB_TABLE], mount="table", tags=["cargo"], solid=False)(_dispatch(SB_TABLE))


# ---------------------------------------------------------------- loaders
def wheel(m, x, y, z, r=0.15, w=0.1, seg=12, hub="steel", tire="rubber"):
    m.cyl(r, w, (x, y, z), tire, axis="x", seg=seg)
    m.cyl(r * 0.55, w + 0.012, (x, y, z), hub, axis="x", seg=max(6, seg - 4))


def beacon(m, x, y, z, mat="em_amber"):
    m.cyl(0.05, 0.03, (x, y, z), "black_metal", seg=8)
    m.cyl(0.045, 0.08, (x, y + 0.055, z), mat, seg=8)


def _l_forklift(m, r):
    m.box((1.1, 0.5, 1.5), (0, 0.55, -0.15), "paint_orange", 0.03)
    m.box((1.1, 0.16, 1.5), (0, 0.3, -0.15), "black_metal", 0.02)
    m.box((1.0, 0.35, 0.5), (0, 0.9, -0.55), "paint_orange", 0.04)
    m.box((0.5, 0.06, 0.4), (0, 0.85, 0.15), "black_metal", 0.01)
    m.box((0.6, 0.35, 0.05), (0, 1.05, -0.05), "fabric_grey", 0.02)
    m.box((0.5, 0.08, 0.4), (0, 0.78, 0.15), "fabric_grey", 0.02)
    for sx in (-1, 1):
        m.box((0.06, 1.0, 0.06), (sx * 0.5, 1.45, 0.4), "black_metal", 0.004)
        m.box((0.06, 1.0, 0.06), (sx * 0.5, 1.4, -0.7), "black_metal", 0.004)
        m.box((0.06, 0.06, 1.2), (sx * 0.5, 1.95, -0.15), "black_metal", 0.004)
        wheel(m, sx * 0.5, 0.3, 0.45, 0.3, 0.2, 16)
        wheel(m, sx * 0.5, 0.25, -0.6, 0.25, 0.18, 14)
    for k in range(5):
        pass
    m.box((1.0, 0.03, 1.2), (0, 1.97, -0.15), "hull_dark", 0.005)
    beacon(m, 0.4, 2.0, -0.15)
    # mast
    for sx in (-1, 1):
        m.box((0.08, 1.9, 0.1), (sx * 0.3, 1.05, 0.72), "black_metal", 0.006)
        m.box((0.05, 1.7, 0.05), (sx * 0.3, 1.0, 0.78), "steel")
    m.box((0.68, 0.06, 0.1), (0, 1.9, 0.72), "black_metal")
    m.box((0.7, 0.25, 0.06), (0, 0.55, 0.82), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.12, 0.05, 1.1), (sx * 0.28, 0.08, 1.35), "steel", 0.006)
        m.box((0.12, 0.5, 0.05), (sx * 0.28, 0.32, 0.85), "steel", 0.006)
    m.link((0, 1.0, 0.7), (0, 0.75, 0.8), 0.03, "chrome", 6)
    hazard(m, "b", (0, 0.55, -0.9), 0, 0.0, 0.0, 0.9, 0.1)
    for sx in (-1, 1):
        m.box((0.1, 0.06, 0.02), (sx * 0.3, 0.45, 0.86), "em_white")


def _l_hover_jack(m, r):
    m.box((0.8, 0.14, 1.5), (0, 0.16, 0), "hull_mid", 0.03)
    m.box((0.74, 0.02, 1.4), (0, 0.24, 0), "rubber")
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.14, 0.05, (sx * 0.28, 0.06, sz * 0.55), "black_metal", seg=14)
            m.cyl(0.11, 0.01, (sx * 0.28, 0.032, sz * 0.55), "em_cyan", seg=14)
    m.box((0.82, 0.03, 0.03), (0, 0.16, 0.76), "em_cyan")
    m.box((0.82, 0.03, 0.03), (0, 0.16, -0.76), "em_cyan")
    m.box((0.22, 0.35, 0.3), (0, 0.4, -0.55), "hull_dark", 0.02)
    m.link((0, 0.5, -0.6), (0, 1.05, -0.85), 0.03, "hull_dark", 8)
    m.box((0.3, 0.05, 0.05), (0, 1.07, -0.87), "black_metal", 0.01)
    m.box((0.06, 0.04, 0.04), (0.12, 1.1, -0.87), "paint_green")
    m.box((0.06, 0.04, 0.04), (-0.12, 1.1, -0.87), "paint_red")
    hazard(m, "f", (0, 0.16, 0.75), 0, 0.0, 0.0, 0.7, 0.08)


def _l_hand_jack(m, r):
    for sx in (-1, 1):
        m.box((0.16, 0.05, 1.15), (sx * 0.28, 0.1, 0.1), "paint_red", 0.006)
        m.cyl(0.04, 0.1, (sx * 0.28, 0.05, 0.62), "rubber", axis="x", seg=10)
        m.cyl(0.05, 0.08, (sx * 0.28, 0.06, -0.4), "rubber", axis="x", seg=10)
    m.box((0.8, 0.18, 0.28), (0, 0.16, -0.4), "paint_red", 0.02)
    m.box((0.44, 0.12, 0.16), (0, 0.36, -0.43), "hull_dark", 0.01)
    m.box((0.06, 0.12, 0.06), (0, 0.5, -0.45), "steel")
    m.link((0, 0.5, -0.45), (0, 1.1, -0.72), 0.022, "hull_dark", 8)
    m.box((0.36, 0.045, 0.045), (0, 1.13, -0.74), "black_metal", 0.008)
    m.link((0.15, 1.12, -0.74), (0.14, 0.95, -0.66), 0.01, "steel", 6)
    m.box((0.05, 0.14, 0.03), (0.16, 0.98, -0.66), "paint_yellow" if False else "hazard_yellow", 0.005)
    for sx in (-1, 1):
        pass


def _l_tug(m, r):
    m.box((1.2, 0.35, 2.0), (0, 0.4, 0), "cg_blue", 0.04)
    m.box((1.0, 0.5, 0.9), (0, 0.85, -0.45), "cg_blue", 0.05)
    m.box((0.9, 0.05, 0.8), (0, 1.35, -0.45), "hull_dark", 0.01)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.05, 0.5, 0.05), (sx * 0.47, 1.1, -0.45 + sz * 0.37), "black_metal")
    m.box((0.8, 0.4, 0.03), (0, 0.95, -0.02), "glass_dark")
    m.box((0.5, 0.1, 0.4), (0, 0.78, -0.5), "fabric_grey", 0.02)
    m.box((0.5, 0.36, 0.08), (0, 1.0, -0.72), "fabric_grey", 0.02)
    m.box((0.6, 0.06, 0.06), (0, 0.9, 0.05), "black_metal", 0.01)
    for sx in (-1, 1):
        wheel(m, sx * 0.62, 0.3, 0.7, 0.3, 0.22, 16)
        wheel(m, sx * 0.62, 0.3, -0.7, 0.3, 0.22, 16)
        m.box((0.1, 0.06, 0.02), (sx * 0.4, 0.5, 1.01), "em_white")
    m.box((0.3, 0.2, 0.3), (0, 0.4, 1.1), "hull_dark", 0.02)
    m.cyl(0.05, 0.12, (0, 0.55, 1.15), "steel", seg=10)
    m.sphere(0.06, (0, 0.65, 1.15), "chrome", 10, 6)
    hazard(m, "f", (0, 0.35, 1.0), 0, 0.0, 0.0, 1.1, 0.1)
    beacon(m, 0, 1.4, -0.45)
    m.box((0.5, 0.05, 0.6), (0, 0.6, 0.55), "steel", 0.006)


def _l_drone_lifter(m, r):
    m.box((0.9, 0.22, 0.9), (0, 0.55, 0), "hull_light", 0.05)
    m.box((0.5, 0.12, 0.5), (0, 0.7, 0), "hull_dark", 0.03)
    m.sphere(0.1, (0, 0.5, 0.45), "glass_dark", 10, 6)
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 0.75, sz * 0.75
            m.link((sx * 0.35, 0.58, sz * 0.35), (x, 0.6, z), 0.04, "hull_mid", 8)
            m.torus(0.28, 0.035, (x, 0.68, z), "hull_dark", seg=12, tseg=4)
            m.cyl(0.05, 0.1, (x, 0.62, z), "black_metal", seg=8)
            for a in range(2):
                m.box((0.5, 0.012, 0.06), (x, 0.7, z), "carbon", 0, (0, a * 1.57 + 0.4, 0))
            m.torus(0.26, 0.012, (x, 0.58, z), "em_cyan", seg=12, tseg=3)
            m.link((sx * 0.35, 0.5, sz * 0.35), (sx * 0.45, 0.05, sz * 0.45), 0.02, "steel", 6)
    m.box((1.1, 0.04, 0.05), (0, 0.04, 0.45), "black_metal", 0.006)
    m.box((1.1, 0.04, 0.05), (0, 0.04, -0.45), "black_metal", 0.006)
    m.box((0.5, 0.05, 0.5), (0, 0.38, 0), "steel", 0.01)
    for sx in (-1, 1):
        m.link((sx * 0.22, 0.38, 0.22), (sx * 0.22, 0.22, 0.22), 0.015, "steel", 6)
        m.link((sx * 0.22, 0.38, -0.22), (sx * 0.22, 0.22, -0.22), 0.015, "steel", 6)
    m.box((0.5, 0.04, 0.5), (0, 0.19, 0), "black_metal", 0.008)
    hazard(m, "f", (0, 0.5, 0.45), 0, 0.0, 0.0, 0.5, 0.06)


def _l_gantry(m, r):
    W, H = 3.0, 3.6
    for sx in (-1, 1):
        x = sx * (W / 2 + 0.1)
        m.box((0.2, H, 0.2), (x, H / 2 + 0.1, 0), "paint_orange", 0.01)
        m.box((0.3, 0.1, 1.5), (x, 0.05, 0), "black_metal", 0.008)
        for sz in (-1, 1):
            wheel(m, x, 0.12, sz * 0.6, 0.12, 0.1, 10)
        m.link((x, 0.1, 0.7), (x, H * 0.6, 0.0), 0.05, "paint_orange", 6)
        m.link((x, 0.1, -0.7), (x, H * 0.6, 0.0), 0.05, "paint_orange", 6)
    m.box((W + 0.6, 0.3, 0.4), (0, H, 0), "paint_orange", 0.015)
    m.box((W + 0.6, 0.08, 0.5), (0, H - 0.17, 0), "black_metal", 0.006)
    hazard(m, "f", (0, H, 0.2), 0, 0.0, 0.0, W, 0.12)
    m.box((0.7, 0.3, 0.7), (0.4, H - 0.45, 0), "hull_dark", 0.02)
    m.box((0.9, 0.12, 0.7), (0.4, H - 0.26, 0), "black_metal", 0.01)
    for sx in (-1, 1):
        pass
    m.cyl(0.2, 0.3, (0.4, H - 0.65, 0), "hull_mid", axis="z", seg=14)
    m.cyl(0.02, 1.4, (0.4, H - 1.45, 0), "steel", seg=6)
    m.box((0.2, 0.25, 0.22), (0.4, H - 2.2, 0), "paint_red", 0.02)
    m.link((0.4, H - 2.3, 0), (0.4, H - 2.55, 0.0), 0.04, "steel", 8)
    m.torus(0.1, 0.03, (0.4, H - 2.72, 0), "steel", axis="z", seg=12, tseg=6, arc=4.7)
    beacon(m, -0.9, H + 0.15, 0)
    m.box((0.2, 0.3, 0.1), (-1.6, H - 0.5, 0.25), "black_metal", 0.01)
    m.box((0.06, 0.1, 0.02), (-1.6, H - 0.45, 0.31), "em_green")


def _l_elevator(m, r):
    W = 2.4
    m.box((W, 0.12, W), (0, 0.66, 0), "hull_dark", 0.01)
    m.box((W - 0.1, 0.03, W - 0.1), (0, 0.735, 0), "steel")
    for k in range(9):
        m.box((0.03, 0.02, W - 0.16), (-1.0 + k * 0.25, 0.755, 0), "black_metal")
    hazard(m, "f", (0, 0.66, W / 2), 0, 0.0, 0.0, W, 0.1)
    hazard(m, "r", (W / 2, 0.66, 0), 0, 0.0, 0.0, W, 0.1)
    hazard(m, "l", (-W / 2, 0.66, 0), 0, 0.0, 0.0, W, 0.1)
    # scissor lift
    for sx in (-1, 1):
        m.link((sx * 0.9, 0.08, -0.7), (sx * 0.9, 0.58, 0.7), 0.05, "paint_orange", 8)
        m.link((sx * 0.9, 0.08, 0.7), (sx * 0.9, 0.58, -0.7), 0.05, "paint_orange", 8)
        m.box((0.14, 0.1, 1.9), (sx * 0.9, 0.05, 0), "black_metal", 0.006)
    m.cyl(0.06, 0.9, (0.0, 0.32, 0.0), "chrome", axis="x", seg=8)
    # railings on 3 sides
    for (x, z) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        m.box((0.06, 1.1, 0.06), (x * (W / 2 - 0.05), 1.3, z * (W / 2 - 0.05)), "hazard_yellow", 0.006)
    for y in (1.35, 1.85):
        m.box((W - 0.05, 0.05, 0.05), (0, y, -W / 2 + 0.05), "hazard_yellow")
        m.box((0.05, 0.05, W - 0.05), (-W / 2 + 0.05, y, 0), "hazard_yellow")
        m.box((0.05, 0.05, W - 0.05), (W / 2 - 0.05, y, 0), "hazard_yellow")
    # control post
    m.box((0.14, 0.9, 0.14), (0.9, 1.2, 1.05), "hull_dark", 0.01)
    m.box((0.2, 0.22, 0.16), (0.9, 1.75, 1.05), "black_metal", 0.012)
    m.cyl(0.03, 0.03, (0.85, 1.78, 1.14), "paint_green", axis="z", seg=8)
    m.cyl(0.03, 0.03, (0.95, 1.78, 1.14), "paint_red", axis="z", seg=8)
    m.box((0.1, 0.05, 0.02), (0.9, 1.7, 1.14), "em_amber")
    beacon(m, -W / 2 + 0.05, 1.95, -W / 2 + 0.05)


def _l_crane_arm(m, r):
    m.box((1.3, 0.3, 2.0), (0, 0.35, 0), "black_metal", 0.02)
    for sx in (-1, 1):
        m.box((0.4, 0.35, 2.1), (sx * 0.7, 0.2, 0), "gunmetal", 0.05)
        for k in range(6):
            m.box((0.42, 0.04, 0.05), (sx * 0.7, 0.2, -0.85 + k * 0.34), "black_metal")
        m.cyl(0.18, 0.4, (sx * 0.7, 0.2, 0.95), "black_metal", axis="x", seg=12)
        m.cyl(0.18, 0.4, (sx * 0.7, 0.2, -0.95), "black_metal", axis="x", seg=12)
    m.box((1.1, 0.6, 1.5), (0, 0.8, 0), "paint_orange", 0.04)
    m.cyl(0.4, 0.15, (0, 1.15, -0.1), "hull_dark", seg=16)
    m.box((0.6, 0.6, 0.7), (0, 1.5, -0.35), "paint_orange", 0.04)
    m.box((0.4, 0.3, 0.02), (0, 1.55, -0.71), "glass_amber")
    beacon(m, 0.2, 1.85, -0.5)
    # boom
    ang = -0.6
    p0 = (0, 1.4, 0.15)
    m.cyl(0.14, 0.4, p0, "hull_dark", axis="x", seg=12)
    p1 = (0, 2.7, 1.5)
    p2 = (0, 3.7, 2.4)
    m.link(p0, p1, 0.15, "paint_orange", 8)
    m.link(p1, p2, 0.1, "brushed_alu", 8)
    for sx in (-1, 1):
        m.link((sx * 0.14, 1.4, 0.15), (sx * 0.14, 2.7, 1.5), 0.02, "hull_dark", 6)
    m.link((0.3, 0.9, 0.4), (0.0, 2.15, 0.85), 0.05, "chrome", 8)
    m.link((0.3, 0.9, 0.4), (0.3, 1.0, 0.5), 0.08, "hull_dark", 8)
    m.box((0.22, 0.22, 0.22), (0, 3.75, 2.45), "black_metal", 0.02)
    m.link((0, 3.7, 2.4), (0, 2.6, 2.4), 0.014, "black_metal", 6)
    m.box((0.16, 0.2, 0.16), (0, 2.5, 2.4), "paint_red", 0.02)
    m.torus(0.09, 0.025, (0, 2.32, 2.4), "steel", axis="x", seg=12, tseg=6, arc=4.7)
    for sx in (-1, 1):
        m.box((0.6, 0.06, 0.3), (sx * 1.15, 0.05, -0.6), "hazard_yellow", 0.008)
        m.link((sx * 0.9, 0.4, -0.6), (sx * 1.15, 0.1, -0.6), 0.04, "hull_dark", 6)
        m.box((0.6, 0.06, 0.3), (sx * 1.15, 0.05, 0.6), "hazard_yellow", 0.008)
        m.link((sx * 0.9, 0.4, 0.6), (sx * 1.15, 0.1, 0.6), 0.04, "hull_dark", 6)


def _l_robot(m, r):
    for sx in (-1, 1):
        x = sx * 0.42
        m.box((0.24, 0.3, 0.95), (x, 0.17, 0), "black_metal", 0.05)
        for z in (-0.38, 0.38):
            m.cyl(0.15, 0.24, (x, 0.17, z), "rubber", axis="x", seg=12)
            m.cyl(0.06, 0.26, (x, 0.17, z), "steel", axis="x", seg=8)
        for k in range(7):
            m.box((0.26, 0.02, 0.04), (x, 0.32, -0.42 + k * 0.14), "gunmetal")
            m.box((0.26, 0.02, 0.04), (x, 0.02, -0.42 + k * 0.14), "gunmetal")
    m.box((0.7, 0.45, 0.8), (0, 0.52, 0), "cg_tan" if False else "paint_grey", 0.04)
    m.box((0.72, 0.1, 0.82), (0, 0.32, 0), "hull_dark", 0.02)
    m.box((0.5, 0.4, 0.5), (0, 0.9, -0.05), "paint_orange", 0.05)
    m.box((0.36, 0.14, 0.32), (0, 1.22, 0.0), "hull_dark", 0.04)
    m.box((0.28, 0.05, 0.02), (0, 1.22, 0.17), "em_cyan")
    m.link((0.12, 1.29, -0.05), (0.12, 1.5, -0.05), 0.012, "steel", 6)
    m.sphere(0.03, (0.12, 1.52, -0.05), "em_red", 8, 5)
    for sx in (-1, 1):
        m.sphere(0.09, (sx * 0.34, 1.0, 0.0), "steel", 10, 6)
        m.box((0.1, 0.1, 0.45), (sx * 0.4, 0.85, 0.2), "hull_dark", 0.02)
        m.box((0.12, 0.12, 0.12), (sx * 0.4, 0.85, 0.46), "black_metal", 0.02)
        m.box((0.02, 0.1, 0.15), (sx * 0.34, 0.85, 0.55), "steel")
        m.box((0.02, 0.1, 0.15), (sx * 0.46, 0.85, 0.55), "steel")
    m.box((0.4, 0.04, 0.06), (0, 0.63, 0.42), "hazard_yellow")
    m.box((0.4, 0.3, 0.03), (0, 0.6, -0.42), "hull_dark", 0.005)
    m.box((0.2, 0.08, 0.01), (0, 0.65, -0.44), "em_green")


def _l_cargo_drone(m, r):
    m.box((1.6, 0.5, 2.2), (0, 0.78, 0), "hull_light", 0.06)
    m.box((1.62, 0.12, 2.22), (0, 0.58, 0), "hull_dark", 0.03)
    m.box((0.9, 0.16, 0.06), (0, 0.85, 1.12), "glass_dark", 0.02)
    m.box((0.5, 0.03, 0.02), (0, 0.85, 1.14), "em_cyan")
    for sx in (-1, 1):
        for sz in (-1, 1):
            x, z = sx * 1.1, sz * 0.9
            m.box((0.6, 0.06, 0.08), (sx * 0.8 - 0.0, 1.0, z), "hull_mid", 0.01)
            m.torus(0.3, 0.04, (x, 1.06, z), "hull_dark", seg=12, tseg=4)
            m.cyl(0.07, 0.12, (x, 1.02, z), "black_metal", seg=8)
            m.box((0.55, 0.012, 0.07), (x, 1.1, z), "carbon", 0, (0, 0.5, 0))
            m.box((0.55, 0.012, 0.07), (x, 1.1, z), "carbon", 0, (0, 2.07, 0))
            m.torus(0.27, 0.012, (x, 1.03, z), "em_cyan", seg=12, tseg=3)
    for sx in (-1, 1):
        m.box((0.07, 0.06, 2.0), (sx * 0.6, 0.04, 0), "black_metal", 0.008)
        for sz in (-0.8, 0.8):
            m.link((sx * 0.6, 0.04, sz), (sx * 0.65, 0.55, sz), 0.03, "steel", 6)
    hazard(m, "r", (0.8, 0.78, 0), 0, 0, 0.0, 1.6, 0.1)
    hazard(m, "l", (-0.8, 0.78, 0), 0, 0, 0.0, 1.6, 0.1)
    for k in range(3):
        m.box((0.4, 0.015, 0.03), (0, 1.045, -0.6 + k * 0.2), "hull_dark")
    m.box((0.14, 0.04, 0.02), (0.6, 0.78, 1.12), "em_green")


def _l_conveyor(m, r):
    L = 3.0
    m.box((0.05, 0.16, L), (-0.4, 0.75, 0), "hull_mid", 0.006)
    m.box((0.05, 0.16, L), (0.4, 0.75, 0), "hull_mid", 0.006)
    m.box((0.83, 0.03, L), (0, 0.7, 0), "hull_dark")
    for k in range(20):
        z = -L / 2 + 0.1 + k * (L - 0.2) / 19
        m.cyl(0.04, 0.76, (0, 0.795, z), "steel" if k % 2 else "brushed_alu", axis="x", seg=8)
    for sx in (-1, 1):
        m.box((0.03, 0.04, L), (sx * 0.44, 0.88, 0), "hazard_yellow")
    for sz in (-1, 1):
        for sx in (-1, 1):
            m.box((0.06, 0.66, 0.06), (sx * 0.4, 0.33, sz * (L / 2 - 0.2)), "hull_dark", 0.004)
            m.box((0.14, 0.03, 0.14), (sx * 0.4, 0.015, sz * (L / 2 - 0.2)), "black_metal")
        m.box((0.8, 0.04, 0.04), (0, 0.3, sz * (L / 2 - 0.2)), "hull_dark")
    m.box((0.3, 0.24, 0.35), (0.65, 0.5, 0.5), "hull_dark", 0.02)
    m.link((0.5, 0.5, 0.5), (0.4, 0.62, 0.5), 0.04, "steel", 6)
    m.box((0.04, 0.03, 0.1), (0.65, 0.63, 0.5), "em_green")
    for sz in (-1, 1):
        pass
    m.box((0.18, 0.18, 0.15), (-0.6, 0.6, -1.4), "black_metal", 0.02)
    m.box((0.06, 0.04, 0.02), (-0.6, 0.62, -1.32), "paint_red")


def _l_scanner(m, r):
    W, H = 3.2, 3.0
    m.box((W + 0.4, 0.12, 2.0), (0, 0.06, 0), "hull_dark", 0.01)
    m.box((1.0, 0.1, 3.2), (0, 0.17, 0), "rubber", 0.01)
    for k in range(7):
        m.box((0.9, 0.012, 0.05), (0, 0.226, -1.4 + k * 0.47), "steel")
    for sx in (-1, 1):
        x = sx * (W / 2 - 0.2)
        m.box((0.4, H, 1.4), (x, H / 2 + 0.12, 0), "hull_light", 0.03)
        m.box((0.03, 1.8, 1.1), (x - sx * 0.215, 1.35, 0), "glass_dark")
        m.box((0.03, 1.5, 0.05), (x - sx * 0.215, 1.35, 0.5), "em_cyan")
    m.box((W, 0.6, 1.4), (0, H + 0.0, 0), "hull_light", 0.03)
    m.box((W - 0.8, 0.05, 1.0), (0, H - 0.3, 0), "glass_dark")
    for k in range(6):
        m.box((0.3, 0.03, 0.03), (-1.0 + k * 0.4, H - 0.28, 0.5), "em_green" if k % 2 else "em_cyan")
    m.box((0.8, 0.28, 0.02), (0, H + 0.05, 0.71), "black_metal", 0.005)
    m.quad((0.7, 0.2), (0, H + 0.05, 0.722), "screen:diagnostic")
    for sx in (-1, 1):
        hazard(m, "f", (sx * (W / 2 - 0.2), 0.35, 0.7), 0, 0.0, 0.0, 0.4, 0.14)
    beacon(m, 1.3, H + 0.3, 0)
    beacon(m, -1.3, H + 0.3, 0, "em_green")
    m.box((0.2, 0.9, 0.2), (1.9, 0.6, 1.1), "hull_dark", 0.02)
    m.box((0.28, 0.2, 0.2), (1.9, 1.15, 1.1), "black_metal", 0.02)
    m.box((0.12, 0.08, 0.02), (1.9, 1.15, 1.21), "em_red")


LOADERS = [("platform_forklift", _l_forklift), ("hover_pallet_jack", _l_hover_jack), ("hand_pallet_jack", _l_hand_jack),
           ("cargo_tug", _l_tug), ("drone_lifter", _l_drone_lifter), ("crane_gantry_segment", _l_gantry),
           ("cargo_elevator_platform", _l_elevator), ("mobile_crane_arm", _l_crane_arm),
           ("maintenance_robot_treads", _l_robot), ("cargo_drone", _l_cargo_drone),
           ("conveyor_segment_3m", _l_conveyor), ("cargo_scanner_arch", _l_scanner)]
family("loader", [c[0] for c in LOADERS], mount="floor", tags=["cargo"], solid=True)(_dispatch(LOADERS))


# ---------------------------------------------------------------- small craft
def nozzle(m, x, y, z, r=0.3, L=0.5, mat="hull_dark", seg=14):
    m.cyl(r, L, (x, y, z - L / 2), mat, axis="z", seg=seg, r2=r * 0.7)
    m.cyl(r * 0.92, 0.02, (x, y, z - L - 0.005), "em_orange", axis="z", seg=seg)
    m.torus(r * 0.98, 0.02, (x, y, z - L + 0.03), "gunmetal", axis="z", seg=seg, tseg=4)


def gear(m, x, z, ytop, spread=0.12, pad=(0.4, 0.5), mat="steel"):
    m.link((x, ytop, z), (x + math.copysign(spread, x), 0.1, z), 0.05, mat, 8)
    m.box((pad[0], 0.08, pad[1]), (x + math.copysign(spread, x), 0.04, z), "black_metal", 0.015)
    m.cyl(0.07, 0.12, (x, ytop - 0.06, z), "chrome", seg=8)


def nav_lights(m, x, y, z):
    m.box((0.08, 0.08, 0.08), (-x, y, z), "em_red")
    m.box((0.08, 0.08, 0.08), (x, y, z), "em_green")


def plines(m, cx, y, z0, z1, w, n=4, mat="hull_dark"):
    for k in range(n):
        z = z0 + (z1 - z0) * (k + 0.5) / n
        m.box((w, 0.008, 0.02), (cx, y, z), mat)
    m.box((0.02, 0.008, z1 - z0), (cx - w * 0.25, y, (z0 + z1) / 2), mat)
    m.box((0.02, 0.008, z1 - z0), (cx + w * 0.25, y, (z0 + z1) / 2), mat)


def reg_marks(m, x, y, z, rng, face="r", n=4, mat="paint_white"):
    stencil(m, face, (x, y, z), 0, 0, 0.0, 0.7, rng, n, mat, 0.12)


def _cr_shuttle(m, r):
    m.prism([(-1.1, -2.8), (1.1, -2.8), (1.2, 0.5), (0.6, 2.4), (-0.6, 2.4), (-1.2, 0.5)], 1.3, (0, 0.7, 0), "hull_light", bevel=0.04)
    m.prism([(-0.95, -2.7), (0.95, -2.7), (1.05, 0.4), (0.5, 2.2), (-0.5, 2.2), (-1.05, 0.4)], 0.18, (0, 0.55, 0), "hull_dark")
    m.box((1.0, 0.55, 1.0), (0, 2.1, 1.35), "glass_blue", 0.05, (-0.35, 0, 0))
    m.box((1.1, 0.06, 0.15), (0, 1.99, 0.85), "hull_dark", 0.01)
    m.box((1.4, 0.1, 2.6), (0, 2.02, -1.0), "paint_white", 0.03)
    plines(m, 0, 2.08, -2.2, 0.1, 1.2, 5)
    for sx in (-1, 1):
        for k in range(4):
            m.box((0.02, 0.28, 0.4), (sx * 1.19 + sx * 0.02, 1.5, -1.6 + k * 0.85 if False else -1.6 + k * 0.7), "glass_blue")
        m.link((sx * 1.15, 1.3, -0.5), (sx * 1.7, 1.25, -1.0), 0.09, "hull_mid", 8)
        m.cyl(0.32, 2.4, (sx * 1.8, 1.25, -1.3), "paint_white", axis="z", seg=16)
        m.cyl(0.32, 0.5, (sx * 1.8, 1.25, 0.15), "hull_mid", axis="z", seg=16, r2=0.15)
        nozzle(m, sx * 1.8, 1.25, -2.5, 0.3, 0.5)
        m.torus(0.33, 0.02, (sx * 1.8, 1.25, -0.6), "paint_blue", axis="z", seg=16, tseg=4)
        m.box((0.06, 0.06, 0.4), (sx * 1.8, 1.58, -0.9), "hazard_yellow")
    m.box((0.1, 1.1, 1.4), (0, 2.75, -2.2), "paint_white", 0.02, (-0.4, 0, 0))
    m.box((0.12, 0.2, 0.5), (0, 3.3, -2.6), "paint_blue", 0.01, (-0.4, 0, 0))
    m.box((1.4, 0.7, 0.05), (0, 1.35, -2.83), "hull_mid", 0.01)
    for sx in (-1, 1):
        m.box((0.2, 0.08, 0.05), (sx * 0.3, 1.0, 2.35), "em_white")
        gear(m, sx * 0.9, 1.4, 0.7, 0.15)
        gear(m, sx * 0.9, -1.8, 0.7, 0.15)
    gear(m, 0.0, 1.9, 0.7, 0.0001, (0.3, 0.4))
    nav_lights(m, 2.15, 1.25, -0.2)
    reg_marks(m, 1.22, 1.25, -0.4, r, "r", 5)
    reg_marks(m, -1.22, 1.25, -0.4, r, "l", 5)
    hazard(m, "b", (0, 1.4, -2.85), 0, -0.55, 0.0, 1.0, 0.1)


def _cr_cargo(m, r):
    m.box((3.0, 2.2, 6.2), (0, 1.9, -0.3), "hull_mid", 0.06)
    m.prism([(-1.5, 2.8), (1.5, 2.8), (1.0, 4.0), (-1.0, 4.0)], 1.7, (0, 1.05, -0.0), "hull_light", bevel=0.05)
    m.box((2.2, 0.85, 1.3), (0, 2.8, 3.1), "glass_blue", 0.05, (-0.45, 0, 0))
    m.box((3.1, 0.3, 6.3), (0, 0.85, -0.3), "hull_dark", 0.03)
    m.box((3.1, 0.12, 6.3), (0, 3.05, -0.3), "paint_orange", 0.02)
    for k in range(5):
        pass
    plines(m, 0, 3.12, -3.2, 2.0, 2.8, 6)
    # rear ramp (open)
    m.box((2.2, 0.08, 1.9), (0, 0.6, -4.2), "steel", 0.01, (0.3, 0, 0))
    for k in range(6):
        pass
    m.box((2.4, 1.8, 0.06), (0, 1.75, -3.4), "black_metal", 0.02)
    m.box((0.06, 1.4, 0.03), (-0.8, 1.75, -3.38), "em_amber")
    m.box((0.06, 1.4, 0.03), (0.8, 1.75, -3.38), "em_amber")
    hazard(m, "b", (0, 0.95, -3.4), 0, 0.0, -0.03, 2.4, 0.16)
    for sx in (-1, 1):
        pass
    for x in (-1.1, -0.4, 0.4, 1.1):
        nozzle(m, x, 1.9 + (0.5 if abs(x) < 1 else -0.2) * 0, -3.6, 0.32, 0.45)
    for sx in (-1, 1):
        m.box((0.05, 0.9, 1.5), (sx * 1.53, 2.0, 0.8), "paint_orange")
        m.box((0.05, 0.4, 1.5), (sx * 1.53, 1.4, -1.0), "hazard_yellow")
        gear(m, sx * 1.25, 2.4, 0.9, 0.3, (0.6, 0.8))
        gear(m, sx * 1.25, -2.2, 0.9, 0.3, (0.6, 0.8))
    for sx in (-1, 1):
        pass
    for sx in (-1, 1):
        m.box((0.08, 1.3, 1.5), (sx * 1.2, 3.7, -3.2), "paint_orange", 0.02)
        m.box((0.1, 0.1, 1.5), (sx * 1.2, 4.35, -3.2), "hull_dark")
    m.box((2.4, 0.1, 0.5), (0, 4.3, -3.2), "paint_orange", 0.01)
    nav_lights(m, 1.62, 2.5, 2.9)
    reg_marks(m, 1.52, 2.4, -1.0, r, "r", 6)
    reg_marks(m, -1.52, 2.4, -1.0, r, "l", 6)
    for sx in (-1, 1):
        m.box((0.3, 0.1, 0.02), (sx * 0.8, 1.2, 3.95), "em_white")


def _cr_interceptor(m, r):
    m.prism([(-0.35, -2.2), (0.35, -2.2), (0.45, 0.5), (0.0, 2.6), (-0.45, 0.5)], 0.55, (0, 0.65, 0), "hull_mid", bevel=0.03)
    m.prism([(-0.3, -2.0), (-2.4, -2.0), (-2.1, -0.9), (-0.45, 0.6)], 0.09, (0, 0.85, 0), "hull_light", bevel=0.01)
    m.prism([(0.3, -2.0), (2.4, -2.0), (2.1, -0.9), (0.45, 0.6)], 0.09, (0, 0.85, 0), "hull_light", bevel=0.01)
    m.sphere(0.4, (0, 1.35, 0.55), "glass_blue", 14, 8, (0.85, 0.7, 1.9))
    m.box((0.9, 0.12, 0.6), (0, 1.22, -0.4), "hull_dark", 0.03)
    for sx in (-1, 1):
        m.cyl(0.27, 1.6, (sx * 0.55, 0.95, -1.5), "hull_dark", axis="z", seg=14)
        m.cyl(0.25, 0.5, (sx * 0.55, 0.95, -0.45), "hull_mid", axis="z", seg=14, r2=0.15)
        nozzle(m, sx * 0.55, 0.95, -2.3, 0.26, 0.4)
        m.link((sx * 2.3, 0.9, -1.3), (sx * 2.3, 0.9, 1.0), 0.05, "gunmetal", 8)
        m.cyl(0.06, 1.0, (sx * 2.3, 0.9, 1.3), "black_metal", axis="z", seg=8)
        m.box((0.06, 0.65, 0.7), (sx * 0.85, 1.4, -1.9), "paint_red", 0.01, (0, 0, sx * -0.35))
        m.box((0.5, 0.012, 0.5), (sx * 1.3, 0.905, -1.4), "paint_white")
        m.box((0.4, 0.014, 0.08), (sx * 1.7, 0.905, -1.2), "paint_red")
        m.box((0.08, 0.08, 0.08), (sx * 2.36, 0.9, -1.9), "em_red" if sx < 0 else "em_green")
        gear(m, sx * 0.55, -1.3, 0.65, 0.05, (0.2, 0.3))
    gear(m, 0, 1.4, 0.65, 0.0001, (0.25, 0.3))
    plines(m, 0, 0.93, -1.5, 1.5, 0.5, 5)
    m.box((0.18, 0.02, 0.5), (0, 0.935, 1.85), "paint_red")


def _cr_droppod(m, r):
    m.cyl(1.05, 1.8, (0, 1.8, 0), "hull_light", seg=16, r2=0.5)
    m.cyl(0.5, 0.5, (0, 3.0, 0), "hull_mid", seg=16, r2=0.3)
    m.sphere(0.3, (0, 3.22, 0), "steel", 12, 6, (1, 0.6, 1))
    m.cyl(1.05, 0.25, (0, 0.85, 0), "cg_rust" if False else "carbon", seg=16, r2=1.05)
    m.sphere(1.05, (0, 0.88, 0), "black_metal", 16, 6, (1, 0.4, 1))
    m.torus(1.05, 0.05, (0, 0.95, 0), "steel", seg=16, tseg=5)
    m.torus(0.78, 0.04, (0, 1.75, 0), "hazard_yellow", seg=16, tseg=5)
    m.box((0.6, 0.95, 0.06), (0, 1.55, 0.83), "hull_dark", 0.02, (-0.3, 0, 0))
    m.box((0.45, 0.8, 0.03), (0, 1.55, 0.87), "hull_light", 0.01, (-0.3, 0, 0))
    m.box((0.3, 0.12, 0.03), (0, 2.1, 0.7), "glass_blue", 0.01, (-0.5, 0, 0))
    for a in range(4):
        ang = a * PI / 2 + PI / 4
        cx, cz = math.cos(ang), math.sin(ang)
        m.link((cx * 0.9, 1.0, cz * 0.9), (cx * 1.5, 0.08, cz * 1.5), 0.06, "steel", 8)
        m.link((cx * 0.8, 1.7, cz * 0.8), (cx * 1.4, 0.5, cz * 1.4), 0.04, "hull_dark", 6)
        m.box((0.5, 0.08, 0.5), (cx * 1.55, 0.04, cz * 1.55), "black_metal", 0.015, (0, -ang, 0))
        m.box((0.3, 0.4, 0.3), (cx * 0.72, 2.45, cz * 0.72), "gunmetal", 0.03, (0, -ang, 0))
        m.cyl(0.07, 0.04, (cx * 0.75, 2.62, cz * 0.75), "em_orange", seg=8)
    m.cyl(0.03, 0.5, (0.0, 3.6, 0.0), "steel", seg=6)
    m.sphere(0.05, (0.0, 3.86, 0.0), "em_red", 8, 5)


def _cr_tug(m, r):
    m.box((2.2, 0.9, 3.4), (0, 1.0, 0), "paint_orange", 0.06)
    m.box((2.3, 0.3, 3.5), (0, 0.55, 0), "black_metal", 0.04)
    m.box((1.6, 0.9, 1.3), (0, 1.9, 0.6), "paint_orange", 0.08)
    m.box((1.4, 0.55, 0.06), (0, 1.95, 1.27), "glass_amber", 0.01, (-0.2, 0, 0))
    for sx in (-1, 1):
        m.box((0.05, 0.5, 0.9), (sx * 0.82, 1.95, 0.6), "glass_amber")
    m.box((1.7, 0.1, 1.3), (0, 2.4, 0.6), "hull_dark", 0.03)
    # big engine block rear
    m.cyl(0.65, 1.4, (0, 1.2, -1.8), "hull_dark", axis="z", seg=18)
    nozzle(m, 0, 1.2, -2.5, 0.6, 0.6)
    for sx in (-1, 1):
        m.cyl(0.18, 0.7, (sx * 1.0, 1.6, -1.5), "gunmetal", axis="z", seg=10)
        nozzle(m, sx * 1.0, 1.6, -1.85, 0.18, 0.25)
    # grapple arms
    for sx in (-1, 1):
        m.box((0.2, 0.2, 0.9), (sx * 0.6, 0.95, 2.0), "hull_dark", 0.03)
        m.link((sx * 0.6, 0.95, 2.4), (sx * 0.5, 0.6, 3.1), 0.09, "steel", 8)
        m.box((0.16, 0.25, 0.4), (sx * 0.5, 0.5, 3.2), "black_metal", 0.02)
        m.box((0.06, 0.4, 0.15), (sx * 0.4, 0.3, 3.3), "steel", 0.008)
        m.box((0.06, 0.4, 0.15), (sx * 0.6, 0.3, 3.3), "steel", 0.008)
        gear(m, sx * 0.9, 1.0, 0.55, 0.15, (0.5, 0.7))
        gear(m, sx * 0.9, -1.3, 0.55, 0.15, (0.5, 0.7))
        m.box((0.3, 0.14, 0.14), (sx * 0.5, 2.55, 1.0), "em_white")
    hazard(m, "f", (0, 0.95, 1.71), 0, 0.0, 0.0, 2.0, 0.16)
    hazard(m, "b", (0, 0.95, -1.7), 0, -0.25, 0.0, 2.0, 0.12)
    plines(m, 0, 1.47, -0.8, 1.3, 1.5, 4)
    m.box((0.2, 0.18, 0.18), (0.0, 2.55, 0.6), "em_amber", 0.02)
    reg_marks(m, 1.12, 1.1, 0.0, r, "r", 5)
    reg_marks(m, -1.12, 1.1, 0.0, r, "l", 5)


def _cr_eva(m, r):
    m.sphere(0.9, (0, 1.25, 0), "hull_light", 22, 14)
    m.sphere(0.55, (0, 1.4, 0.55), "glass_blue", 16, 10, (1, 0.85, 0.75))
    m.torus(0.9, 0.05, (0, 1.25, 0), "paint_orange", axis="x", seg=22, tseg=5)
    m.torus(0.9, 0.05, (0, 1.25, 0), "hull_mid", axis="y", seg=22, tseg=5)
    for a in range(4):
        ang = a * PI / 2 + PI / 4
        cx, cz = math.cos(ang), math.sin(ang)
        m.box((0.28, 0.28, 0.28), (cx * 0.85, 1.9 - 0.3 if False else 1.9, cz * 0.85), "gunmetal", 0.03, (0, -ang, 0))
    # thrusters under
    for a in range(3):
        ang = a * 2.094
        cx, cz = math.cos(ang), math.sin(ang)
        m.link((cx * 0.6, 0.6, cz * 0.6), (cx * 1.05, 0.08, cz * 1.05), 0.04, "steel", 6)
        m.box((0.34, 0.06, 0.34), (cx * 1.05, 0.03, cz * 1.05), "black_metal", 0.01)
    m.cyl(0.28, 0.2, (0, 0.5, 0), "hull_dark", seg=12, r2=0.2)
    m.cyl(0.18, 0.02, (0, 0.39, 0), "em_orange", seg=12)
    for sx in (-1, 1):
        m.sphere(0.12, (sx * 0.95, 1.0, 0.35), "steel", 10, 6)
        m.link((sx * 1.0, 1.0, 0.35), (sx * 1.15, 0.75, 0.85), 0.05, "hull_dark", 8)
        m.link((sx * 1.15, 0.75, 0.85), (sx * 0.9, 0.7, 1.35), 0.04, "hull_dark", 8)
        m.sphere(0.07, (sx * 1.15, 0.75, 0.85), "steel", 8, 5)
        m.box((0.05, 0.16, 0.12), (sx * 0.84, 0.7, 1.4), "black_metal", 0.008)
        m.box((0.05, 0.16, 0.12), (sx * 0.96, 0.7, 1.4), "black_metal", 0.008)
        m.box((0.16, 0.06, 0.06), (sx * 0.55, 1.75, 0.65), "em_white")
        for zz in (-0.9, ):
            pass
    m.box((0.5, 0.2, 0.2), (0, 1.25, -0.9), "hull_dark", 0.03)
    m.box((0.14, 0.04, 0.02), (0.0, 1.25, -1.0), "em_amber")
    m.cyl(0.03, 0.4, (0.0, 2.4, 0.0), "steel", seg=6)
    m.sphere(0.05, (0, 2.62, 0), "em_red", 8, 5)
    m.box((0.5, 0.08, 0.02), (0.0, 1.0, 0.86), "hazard_yellow", 0, (0, 0, 0))


def _cr_scout(m, r):
    m.prism([(0.0, 3.0), (0.32, 1.6), (0.5, -0.4), (0.4, -2.2), (-0.4, -2.2), (-0.5, -0.4), (-0.32, 1.6)], 0.5, (0, 0.6, 0), "hull_light", bevel=0.03)
    m.sphere(0.35, (0, 1.2, 1.1), "glass_blue", 14, 8, (0.9, 0.8, 1.7))
    m.prism([(0.4, -0.5), (2.6, -1.4), (2.7, -2.0), (0.4, -1.6)], 0.06, (0, 0.85, 0), "paint_white", bevel=0.01)
    m.prism([(-0.4, -0.5), (-2.6, -1.4), (-2.7, -2.0), (-0.4, -1.6)], 0.06, (0, 0.85, 0), "paint_white", bevel=0.01)
    # sensor dish
    m.cyl(0.05, 0.4, (0, 1.3, -0.6), "steel", seg=8)
    m.sphere(0.55, (0, 1.6, -0.6), "paint_white", 16, 8, (1, 0.28, 1))
    m.cyl(0.03, 0.3, (0, 1.85, -0.6), "steel", seg=6)
    m.sphere(0.05, (0, 2.03, -0.6), "em_cyan", 8, 5)
    for a in range(3):
        m.box((0.03, 0.03, 0.5), (0.0, 1.66, -0.6), "hull_dark", 0, (0, a * 1.047, 0))
    m.cyl(0.35, 1.2, (0, 0.95, -2.3), "hull_dark", axis="z", seg=16, r2=0.32)
    nozzle(m, 0, 0.95, -2.9, 0.34, 0.5)
    for sx in (-1, 1):
        m.box((0.1, 0.5, 0.5), (sx * 2.65, 1.1, -1.9), "paint_red", 0.01, (0, 0, 0))
        m.box((0.1, 0.1, 0.1), (sx * 2.72, 0.88, -1.4), "em_red" if sx < 0 else "em_green")
        m.cyl(0.14, 0.7, (sx * 1.1, 0.7, -0.8), "gunmetal", axis="z", seg=10)
        gear(m, sx * 0.55, 0.4, 0.62, 0.2, (0.3, 0.4))
    for sx in (-1, 1):
        m.link((sx * 0.55, 0.8, -1.5), (sx * 0.95, 0.1, -1.6), 0.045, "steel", 8)
        m.box((0.3, 0.07, 0.4), (sx * 0.95, 0.035, -1.6), "black_metal", 0.012)
    gear(m, 0, 2.2, 0.62, 0.0001, (0.22, 0.3))
    plines(m, 0, 1.12, -1.6, 0.4, 0.6, 4)
    m.box((0.12, 0.06, 0.02), (0, 0.85, 2.85), "em_white")


def _cr_medical(m, r):
    m.box((2.2, 1.6, 4.4), (0, 1.6, 0), "paint_white", 0.14)
    m.sphere(1.1, (0, 1.6, 2.2), "paint_white", 18, 10, (1, 0.75, 0.9))
    m.box((1.5, 0.6, 0.9), (0, 1.95, 2.55), "glass_blue", 0.06, (-0.4, 0, 0))
    m.box((2.25, 0.12, 4.5), (0, 0.85, 0), "hull_dark", 0.03)
    m.box((2.0, 0.1, 2.5), (0, 2.42, -0.6), "paint_red", 0.02)
    for sx in (-1, 1):
        m.box((0.04, 1.0, 1.4), (sx * 1.12, 1.6, -0.3), "hull_light", 0.02)
        m.box((0.03, 0.4, 0.5), (sx * 1.14, 1.85, -0.1), "glass_blue")
        m.box((0.03, 0.05, 1.4), (sx * 1.14, 1.55, -0.3), "hull_dark")
        # cross emblem
        m.box((0.03, 0.5, 0.14), (sx * 1.13, 1.5, 1.5), "paint_red")
        m.box((0.03, 0.14, 0.5), (sx * 1.13, 1.5, 1.5), "paint_red")
        m.cyl(0.4, 1.4, (sx * 1.6, 1.3, -1.5), "paint_white", axis="z", seg=14)
        m.link((sx * 1.05, 1.4, -1.5), (sx * 1.5, 1.35, -1.5), 0.1, "hull_mid", 8)
        m.cyl(0.4, 0.4, (sx * 1.6, 1.3, -0.5), "paint_white", axis="z", seg=14, r2=0.25)
        nozzle(m, sx * 1.6, 1.3, -2.2, 0.36, 0.5)
        m.torus(0.41, 0.03, (sx * 1.6, 1.3, -1.6), "paint_red", axis="z", seg=14, tseg=4)
        gear(m, sx * 0.8, 1.5, 0.8, 0.15, (0.4, 0.55))
        gear(m, sx * 0.8, -1.6, 0.8, 0.15, (0.4, 0.55))
        m.box((0.1, 0.1, 0.1), (sx * 2.0, 1.3, -0.5), "em_red" if sx < 0 else "em_green")
    m.cyl(0.1, 0.15, (0.0, 2.55, 1.0), "black_metal", seg=8)
    m.cyl(0.09, 0.14, (0.0, 2.68, 1.0), "em_red", seg=8)
    m.box((1.8, 0.4, 0.05), (0, 1.2, -2.22), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.18, 0.06, 0.06), (sx * 0.4, 1.2, 3.0), "em_white")
    reg_marks(m, 1.14, 0.85, 0.2, r, "r", 5, "black_metal")
    reg_marks(m, -1.14, 0.85, 0.2, r, "l", 5, "black_metal")


def _cr_repair(m, r):
    m.box((1.7, 0.9, 2.3), (0, 1.0, 0), "cg_tan" if False else "hazard_yellow", 0.07)
    m.box((1.75, 0.35, 2.35), (0, 0.65, 0), "black_metal", 0.04)
    m.box((1.2, 0.6, 0.9), (0, 1.75, 0.5), "hazard_yellow", 0.07)
    m.box((1.0, 0.4, 0.05), (0, 1.8, 0.96), "glass_amber", 0.01, (-0.2, 0, 0))
    m.box((1.3, 0.08, 1.0), (0, 2.1, 0.5), "hull_dark", 0.02)
    nozzle(m, 0, 1.0, -1.2, 0.3, 0.4)
    for sx in (-1, 1):
        nozzle(m, sx * 0.55, 1.35, -1.2, 0.15, 0.25)
        gear(m, sx * 0.7, 0.8, 0.55, 0.15, (0.5, 0.6))
        gear(m, sx * 0.7, -0.8, 0.55, 0.15, (0.5, 0.6))
    # articulated arm
    m.cyl(0.2, 0.25, (0.55, 2.2, -0.1), "hull_dark", seg=12)
    m.sphere(0.16, (0.55, 2.45, -0.1), "steel", 12, 8)
    m.link((0.55, 2.45, -0.1), (0.75, 3.0, 0.5), 0.08, "hull_mid", 8)
    m.sphere(0.11, (0.75, 3.0, 0.5), "steel", 10, 6)
    m.link((0.75, 3.0, 0.5), (0.7, 2.6, 1.5), 0.065, "hull_mid", 8)
    m.sphere(0.08, (0.7, 2.6, 1.5), "steel", 8, 6)
    m.box((0.1, 0.1, 0.35), (0.7, 2.45, 1.75), "black_metal", 0.015, (0.5, 0, 0))
    m.cyl(0.03, 0.2, (0.7, 2.3, 1.95), "steel", seg=6, rot=(0.5, 0, 0))
    m.sphere(0.06, (0.7, 2.24, 2.02), "em_cyan", 8, 5)
    # tool rack side
    m.box((0.06, 0.6, 1.2), (-0.88, 1.1, 0.0), "hull_dark", 0.01)
    for k in range(4):
        m.box((0.1, 0.4, 0.06), (-0.95, 1.1, -0.45 + k * 0.3), ["paint_red", "steel", "paint_blue", "brass"][k], 0.008)
    hazard(m, "f", (0, 0.8, 1.17), 0, 0.0, 0.0, 1.5, 0.12)
    hazard(m, "b", (0, 0.8, -1.17), 0, 0.0, 0.0, 1.5, 0.12)
    beacon(m, -0.5, 2.15, 0.3)
    reg_marks(m, 0.88, 1.1, 0.3, r, "r", 4)


def _cr_lander(m, r):
    m.cyl(1.35, 1.1, (0, 2.2, 0), "hull_light", seg=8, bevel=0.03)
    m.cyl(1.2, 0.5, (0, 3.0, 0), "hull_mid", seg=8, r2=0.7)
    m.cyl(0.35, 0.15, (0, 3.35, 0), "steel", seg=12)
    m.cyl(0.25, 0.1, (0, 3.48, 0), "glass_blue", seg=12)
    m.cyl(1.4, 0.15, (0, 1.55, 0), "black_metal", seg=8, bevel=0.01)
    m.cyl(0.55, 0.35, (0, 1.3, 0), "hull_dark", seg=14)
    m.cyl(0.6, 0.5, (0, 1.05, 0), "gunmetal", seg=16, r2=0.4)
    m.cyl(0.5, 0.02, (0, 0.795, 0), "em_orange", seg=16)
    # windows around
    for a in range(8):
        ang = a * PI / 4 + PI / 8
        cx, cz = math.cos(ang), math.sin(ang)
        if a in (1, 2, 5, 6) or True:
            pass
    m.box((0.5, 0.35, 0.05), (0, 2.5, 1.3), "glass_blue", 0.01)
    m.box((0.05, 0.35, 0.5), (-1.3, 2.5, 0), "glass_blue", 0.01)
    m.box((0.05, 0.35, 0.5), (1.3, 2.5, 0), "glass_blue", 0.01)
    m.box((0.6, 1.2, 0.1), (0, 2.1, -1.32), "hull_dark", 0.02)
    m.box((0.45, 1.0, 0.03), (0, 2.1, -1.39), "hazard_yellow")
    # legs
    for a in range(4):
        ang = a * PI / 2 + PI / 4
        cx, cz = math.cos(ang), math.sin(ang)
        m.link((cx * 1.1, 1.7, cz * 1.1), (cx * 2.4, 0.22, cz * 2.4), 0.09, "steel", 8)
        m.link((cx * 1.25, 2.6, cz * 1.25), (cx * 2.0, 0.9, cz * 2.0), 0.06, "hull_dark", 6)
        m.cyl(0.55, 0.14, (cx * 2.45, 0.09, cz * 2.45), "black_metal", seg=12, r2=0.5)
        m.cyl(0.07, 0.12, (cx * 2.4, 0.3, cz * 2.4), "chrome", seg=8)
    # ladder
    m.link((-0.2, 0.15, 2.0), (-0.2, 1.9, 1.3), 0.03, "steel", 6)
    m.link((0.2, 0.15, 2.0), (0.2, 1.9, 1.3), 0.03, "steel", 6)
    for k in range(6):
        t = 0.1 + k * 0.16
        m.box((0.4, 0.03, 0.04), (0, 0.15 + (1.75) * t, 2.0 - 0.7 * t), "steel")
    m.link((0.9, 3.55, -0.3), (0.9, 4.4, -0.3), 0.025, "steel", 6)
    m.sphere(0.07, (0.9, 4.45, -0.3), "em_red", 8, 5)
    m.box((0.5, 0.4, 0.4), (-0.7, 3.6, 0.3), "paint_white", 0.03)
    m.sphere(0.32, (-0.7, 3.85, 0.3), "paint_white", 12, 5, (1, 0.35, 1))
    for a in range(4):
        ang = a * PI / 2
        m.box((0.2, 0.2, 0.2), (math.cos(ang) * 1.35, 3.2, math.sin(ang) * 1.35), "gunmetal", 0.02)
    hazard(m, "f", (0, 1.6, 1.36), 0, 0.0, 0.0, 1.5, 0.1)


CRAFT = [("shuttlecraft", _cr_shuttle), ("cargo_shuttle", _cr_cargo), ("interceptor", _cr_interceptor),
         ("drop_pod", _cr_droppod), ("tug", _cr_tug), ("eva_pod", _cr_eva), ("scout", _cr_scout),
         ("medical_shuttle", _cr_medical), ("repair_pod", _cr_repair), ("lander", _cr_lander)]
family("craft", [c[0] for c in CRAFT], mount="floor", tags=["hangar"], solid=True)(_dispatch(CRAFT, 1000))


# ---------------------------------------------------------------- hangar tools
def caster(m, x, z, r=0.07, w=0.04, y=None):
    y = r if y is None else y
    m.cyl(r, w, (x, y, z), "rubber", axis="x", seg=10)
    m.box((0.05, 0.06, 0.07), (x, y + r + 0.02, z), "steel")


def _h_hose_reel(m, r):
    for sx in (-1, 1):
        m.box((0.06, 0.9, 0.7), (sx * 0.45, 0.55, 0), "paint_red", 0.02)
        m.box((0.16, 0.06, 0.8), (sx * 0.45, 0.05, 0), "black_metal", 0.008)
    m.box((0.96, 0.05, 0.05), (0, 0.98, -0.3), "hull_dark")
    m.box((0.96, 0.05, 0.05), (0, 0.15, -0.3), "hull_dark")
    m.cyl(0.34, 0.04, (-0.36, 0.7, 0), "steel", axis="x", seg=16)
    m.cyl(0.34, 0.04, (0.36, 0.7, 0), "steel", axis="x", seg=16)
    m.cyl(0.2, 0.72, (0, 0.7, 0), "hull_dark", axis="x", seg=14)
    for k in range(6):
        m.torus(0.28, 0.045, (-0.3 + k * 0.12, 0.7, 0), "hazard_yellow" if k % 2 == 0 else "cg_ptl_yellow", axis="x", seg=12, tseg=4)
    m.cyl(0.06, 0.14, (0.55, 0.7, 0), "steel", axis="x", seg=8)
    m.link((0.6, 0.7, 0), (0.62, 0.95, 0.15), 0.02, "chrome", 6)
    m.box((0.06, 0.06, 0.24), (0.62, 0.98, 0.25), "black_metal", 0.008)
    m.link((0, 0.42, 0.28), (0.1, 0.1, 0.8), 0.04, "hazard_yellow", 8)
    m.link((0.1, 0.1, 0.8), (0.5, 0.06, 1.2), 0.04, "hazard_yellow", 8)
    m.cyl(0.05, 0.25, (0.55, 0.06, 1.3), "brass", axis="z", seg=8)
    m.box((0.08, 0.14, 0.06), (0.55, 0.12, 1.45), "paint_green", 0.01)
    m.box((0.01, 0.14, 0.2), (-0.485, 0.65, 0.0), "paint_white")


def _h_toolcart(m, r):
    W, D = 0.9, 0.55
    m.box((W, 0.7, D), (0, 0.55, 0), "paint_blue", 0.015)
    m.box((W + 0.04, 0.04, D + 0.04), (0, 0.92, 0), "steel", 0.006)
    for k in range(3):
        m.box((W - 0.08, 0.18, 0.02), (0, 0.32 + k * 0.22, D / 2 + 0.008), "hull_dark", 0.005)
        m.box((0.4, 0.025, 0.03), (0, 0.38 + k * 0.22, D / 2 + 0.03), "chrome")
    for sx in (-1, 1):
        for sz in (-1, 1):
            caster(m, sx * 0.36, sz * 0.2, 0.08, 0.05)
    m.box((0.04, 0.5, 0.04), (-0.4, 1.15, -0.24), "steel")
    m.box((0.04, 0.5, 0.04), (0.4, 1.15, -0.24), "steel")
    m.box((W, 0.04, 0.04), (0, 1.4, -0.24), "steel")
    m.box((W - 0.1, 0.03, D - 0.1), (0, 0.95, 0.0), "rubber")
    for k, x in enumerate((-0.3, -0.1, 0.12, 0.3)):
        m.box((0.03, 0.03, 0.3), (x, 0.99, 0.0), ["paint_red", "steel", "paint_orange", "brass"][k], 0.004)
        m.box((0.05, 0.05, 0.08), (x, 0.99, 0.18), "black_metal", 0.006)
    m.box((0.2, 0.12, 0.14), (0.2, 1.03, -0.12), "hazard_yellow", 0.01)
    m.cyl(0.06, 0.16, (-0.25, 1.05, -0.05), "paint_grey", seg=8)


def _h_engine_hoist(m, r):
    for sx in (-1, 1):
        m.box((0.08, 0.1, 1.5), (sx * 0.45, 0.14, 0.2), "paint_blue", 0.008)
        caster(m, sx * 0.45, 0.85, 0.08, 0.05)
        caster(m, sx * 0.45, -0.5, 0.08, 0.05)
    m.box((1.0, 0.1, 0.1), (0, 0.14, -0.4), "paint_blue", 0.008)
    m.box((0.14, 1.9, 0.14), (0, 1.1, -0.4), "paint_blue", 0.012)
    m.link((0, 0.2, 0.2), (0, 1.0, -0.38), 0.05, "chrome", 8)
    m.link((0, 2.0, -0.4), (0, 2.25, 1.0), 0.07, "paint_blue", 8)
    m.link((0, 2.25, 1.0), (0, 2.15, 1.5), 0.055, "brushed_alu", 8)
    m.link((0, 0.5, -0.3), (0, 1.55, 0.3), 0.04, "steel", 8)
    m.cyl(0.06, 0.06, (0, 2.12, 1.5), "black_metal", axis="x", seg=8)
    m.link((0, 2.1, 1.5), (0, 1.35, 1.5), 0.012, "black_metal", 5)
    m.box((0.14, 0.1, 0.14), (0, 1.3, 1.5), "paint_red", 0.02)
    m.torus(0.08, 0.025, (0, 1.17, 1.5), "steel", axis="x", seg=12, tseg=6, arc=4.7)
    m.box((0.28, 0.4, 0.05), (0, 0.9, -0.5), "hazard_yellow", 0.008)
    m.box((0.05, 0.05, 0.3), (0.0, 0.6, -0.55), "black_metal")


def _h_jack(m, r):
    for a in range(3):
        ang = a * 2.094 + 1.57
        cx, cz = math.cos(ang), math.sin(ang)
        m.link((cx * 0.05, 0.9, cz * 0.05), (cx * 0.8, 0.08, cz * 0.8), 0.04, "paint_blue", 8)
        m.box((0.24, 0.06, 0.24), (cx * 0.82, 0.03, cz * 0.82), "black_metal", 0.01, (0, -ang, 0))
        m.cyl(0.05, 0.05, (cx * 0.82, 0.08, cz * 0.82), "steel", seg=8)
    m.cyl(0.12, 0.8, (0, 0.9, 0), "paint_blue", seg=14)
    m.cyl(0.08, 0.7, (0, 1.55, 0), "chrome", seg=12)
    m.cyl(0.14, 0.14, (0, 1.95, 0), "paint_red", seg=12, r2=0.2)
    m.cyl(0.25, 0.05, (0, 2.06, 0), "black_metal", seg=14)
    m.box((0.06, 0.2, 0.06), (0.16, 1.05, 0.0), "steel", 0.006)
    m.link((0.16, 1.1, 0), (0.55, 1.1, 0.0), 0.02, "black_metal", 6)
    m.sphere(0.04, (0.56, 1.1, 0), "paint_red", 8, 5)
    m.torus(0.125, 0.012, (0, 0.65, 0), "gunmetal", seg=14, tseg=4)
    m.box((0.14, 0.06, 0.01), (0.0, 1.0, 0.125), "paint_white")


def _h_chocks(m, r):
    for x in (-0.3, 0.3):
        m.prism([(-0.15, 0.0), (0.15, 0.0), (0.15, 0.06), (-0.05, 0.22), (-0.15, 0.22)], 0.2, (x - 0.1, 0, 0), "paint_orange", plane="zy", bevel=0.008)
        for k in range(5):
            pass
        m.box((0.2, 0.02, 0.28), (x, 0.005, 0.0), "rubber")
        m.box((0.2, 0.04, 0.05), (x, 0.2, -0.13), "hazard_yellow", 0.004)
        m.box((0.03, 0.09, 0.04), (x, 0.17, -0.155), "black_metal")
        for k in range(3):
            pass
    m.link((-0.3, 0.2, -0.16), (0.0, 0.05, -0.35), 0.012, "cg_strap", 5)
    m.link((0.3, 0.2, -0.16), (0.0, 0.05, -0.35), 0.012, "cg_strap", 5)
    m.box((0.14, 0.1, 0.05), (0.0, 0.05, -0.38), "cg_strap", 0.008)
    for x in (-0.85, 0.85):
        pass


def _h_tow_bar(m, r):
    m.link((0, 0.35, 1.8), (-0.35, 0.3, -1.3), 0.035, "hazard_yellow", 8)
    m.link((0, 0.35, 1.8), (0.35, 0.3, -1.3), 0.035, "hazard_yellow", 8)
    m.link((-0.3, 0.32, -0.6), (0.3, 0.32, -0.6), 0.03, "hull_dark", 8)
    m.box((0.9, 0.06, 0.2), (0, 0.28, -1.35), "black_metal", 0.01)
    for sx in (-1, 1):
        m.box((0.08, 0.16, 0.1), (sx * 0.4, 0.34, -1.3), "steel", 0.008)
    m.torus(0.1, 0.03, (0, 0.35, 1.93), "chrome", axis="x", seg=14, tseg=6)
    m.cyl(0.09, 0.1, (0, 0.35, 1.8), "black_metal", axis="z", seg=10)
    m.link((0, 0.35, 1.5), (0, 0.65, 1.3), 0.03, "steel", 6)
    m.link((0, 0.65, 1.3), (0, 0.7, 1.7), 0.02, "steel", 6)
    m.cyl(0.03, 0.4, (0, 0.72, 1.5), "black_metal", axis="x", seg=6)
    for sx in (-1, 1):
        wheel(m, sx * 0.5, 0.1, -1.2, 0.1, 0.06, 10)
        m.box((0.05, 0.1, 0.05), (sx * 0.5, 0.2, -1.2), "steel")
    for k in range(5):
        pass
    for k in range(4):
        z = 1.2 - k * 0.6
        t = (1.8 - z) / 3.1
        m.box((0.1, 0.05, 0.05), (-0.35 * t, 0.35 - 0.05 * t + 0.025, z), "black_metal")
        m.box((0.1, 0.05, 0.05), (0.35 * t, 0.35 - 0.05 * t + 0.025, z), "black_metal")


def _pad(m, r, variant):
    S = 6.0
    m.box((S, 0.06, S), (0, 0.03, 0), "hull_dark", 0.008)
    m.box((S - 0.3, 0.012, S - 0.3), (0, 0.066, 0), "gunmetal")
    for sx in (-1, 1):
        m.box((0.2, 0.02, S), (sx * (S / 2 - 0.1), 0.07, 0), "hazard_yellow")
        m.box((S - 0.4, 0.02, 0.2), (0, 0.07, sx * (S / 2 - 0.1)), "hazard_yellow")
    if variant == 0:
        m.torus(2.2, 0.03, (0, 0.078, 0), "paint_white", seg=32, tseg=4)
        m.torus(1.7, 0.02, (0, 0.078, 0), "paint_white", seg=32, tseg=4)
        # H
        m.box((0.25, 0.012, 1.8), (-0.6, 0.075, 0), "paint_white")
        m.box((0.25, 0.012, 1.8), (0.6, 0.075, 0), "paint_white")
        m.box((1.2, 0.012, 0.25), (0, 0.075, 0), "paint_white")
        for a in range(8):
            ang = a * PI / 4 + PI / 8
            m.box((0.25, 0.08, 0.25), (math.cos(ang) * 2.7, 0.07, math.sin(ang) * 2.7), "gunmetal", 0.01, (0, -ang, 0))
            m.cyl(0.07, 0.02, (math.cos(ang) * 2.7, 0.115, math.sin(ang) * 2.7), "em_amber", seg=10)
        m.torus(1.9, 0.015, (0, 0.077, 0), "em_cyan", seg=32, tseg=4)
    else:
        m.box((4.4, 0.012, 0.15), (0, 0.075, 2.2), "paint_white")
        m.box((4.4, 0.012, 0.15), (0, 0.075, -2.2), "paint_white")
        m.box((0.15, 0.012, 4.4), (2.2, 0.075, 0), "paint_white")
        m.box((0.15, 0.012, 4.4), (-2.2, 0.075, 0), "paint_white")
        for k in range(5):
            m.box((1.4, 0.012, 0.16), (0, 0.075, -1.6 + k * 0.4), "paint_orange" if k % 2 == 0 else "paint_white", 0, (0, 0, 0))
        # numerals as bars
        for k in range(4):
            pass
        for x in (-2.7, 2.7):
            for z in (-2.7, 2.7):
                m.cyl(0.18, 0.04, (x, 0.08, z), "steel", seg=10)
                m.cyl(0.1, 0.03, (x, 0.11, z), "em_green", seg=10)
        for k in range(5):
            for sx in (-1, 1):
                m.box((0.2, 0.03, 0.08), (sx * 2.7, 0.085, -1.6 + k * 0.8), "em_green")
                m.box((0.08, 0.03, 0.2), (-1.6 + k * 0.8, 0.085, sx * 2.7), "em_green")
        m.cyl(1.2, 0.012, (0, 0.073, 0), "hull_dark", seg=24)
        m.torus(1.2, 0.04, (0, 0.078, 0), "hazard_yellow", seg=24, tseg=4)
        m.box((1.4, 0.014, 0.2), (0, 0.078, 0), "paint_white")
        m.box((0.2, 0.014, 1.4), (0, 0.078, 0), "paint_white")
        # padding numerals
        for k in range(3):
            m.box((0.14, 0.014, 0.55), (-0.3 + k * 0.3, 0.076, 1.75), "paint_white")
        m.box((0.6, 0.014, 0.14), (0, 0.076, 1.95), "paint_white")


def _h_pad_a(m, r):
    _pad(m, r, 0)


def _h_pad_b(m, r):
    _pad(m, r, 1)


def _h_launch_rail(m, r):
    L = 4.0
    for k in range(9):
        m.box((1.3, 0.1, 0.18), (0, 0.06, -L / 2 + 0.2 + k * (L - 0.4) / 8), "concrete", 0.008)
    for sx in (-1, 1):
        m.box((0.16, 0.16, L), (sx * 0.5, 0.18, 0), "hull_dark", 0.015)
        m.box((0.1, 0.06, L), (sx * 0.5, 0.29, 0), "chrome", 0.006)
        m.box((0.02, 0.04, L - 0.2), (sx * 0.43, 0.2, 0), "em_blue")
    for k in range(4):
        z = -1.4 + k * 0.95
        m.torus(0.55, 0.07, (0, 0.3, z), "brass" if k % 2 else "copper", axis="z", seg=14, tseg=4)
        for sx in (-1, 1):
            m.box((0.1, 0.4, 0.14), (sx * 0.62, 0.3, z), "hull_mid", 0.01)
        m.box((1.3, 0.08, 0.14), (0, 0.85, z), "hull_mid", 0.01)
    m.box((0.5, 0.2, 0.2), (0, 0.4, -L / 2 - 0.1), "black_metal", 0.02)
    hazard(m, "f", (0, 0.14, L / 2 - 0.0), 0, 0.0, 0.0, 1.0, 0.1)
    m.box((0.12, 0.12, 0.05), (0.7, 0.2, L / 2 - 0.15), "em_amber")
    m.ground()  # the arch rings used to sink 0.3 m below the floor


def _h_dock_clamp(m, r):
    m.box((1.4, 0.2, 1.4), (0, 0.1, 0), "hull_dark", 0.02)
    m.box((1.2, 0.03, 1.2), (0, 0.215, 0), "gunmetal")
    hazard(m, "f", (0, 0.1, 0.7), 0, 0.0, 0.0, 1.2, 0.1)
    m.cyl(0.35, 0.5, (0, 0.45, 0), "hull_mid", seg=14)
    m.cyl(0.28, 0.06, (0, 0.73, 0), "black_metal", seg=14)
    for sx in (-1, 1):
        m.box((0.16, 0.16, 0.8), (sx * 0.5, 0.55, 0.1), "paint_orange", 0.015)
        m.link((sx * 0.45, 0.4, -0.5), (sx * 0.75, 1.2, -0.2), 0.06, "chrome", 8)
        m.box((0.2, 1.0, 0.24), (sx * 0.75, 0.9, 0.15), "paint_orange", 0.02, (0, 0, sx * -0.12))
        m.box((0.24, 0.5, 0.4), (sx * 0.65, 1.55, 0.6), "black_metal", 0.02)
        m.box((0.05, 0.4, 0.34), (sx * 0.51, 1.55, 0.6), "rubber")
        m.link((sx * 0.75, 1.3, 0.2), (sx * 0.68, 1.5, 0.5), 0.04, "paint_orange", 6)
        m.box((0.1, 0.1, 0.06), (sx * 0.68, 1.85, 0.6), "em_amber" if sx > 0 else "em_green")
    m.box((0.5, 0.3, 0.1), (0, 0.4, -0.75), "black_metal", 0.02)
    m.box((0.3, 0.06, 0.02), (0, 0.42, -0.69), "em_cyan")


def _h_light_tower(m, r):
    m.box((1.4, 0.25, 2.2), (0, 0.4, 0), "paint_orange", 0.03)
    m.box((1.5, 0.08, 2.3), (0, 0.24, 0), "black_metal", 0.01)
    for sx in (-1, 1):
        wheel(m, sx * 0.62, 0.18, -0.6, 0.18, 0.12, 12)
        m.box((0.08, 0.1, 0.5), (sx * 0.8, 0.25, 1.0), "hazard_yellow", 0.008)
        m.box((0.3, 0.05, 0.3), (sx * 0.8, 0.025, 1.15), "black_metal", 0.008)
    m.box((0.5, 0.4, 0.6), (0, 0.72, 0.6), "hull_dark", 0.02)
    m.cyl(0.08, 0.3, (0.5, 0.78, -0.7), "hull_dark", seg=8)
    m.box((0.14, 0.14, 0.1), (-0.5, 0.65, 1.12), "black_metal")
    m.cyl(0.1, 3.8, (0, 2.5, -0.4), "steel", seg=10)
    m.cyl(0.13, 0.4, (0, 0.8, -0.4), "hull_dark", seg=10)
    m.box((1.5, 0.08, 0.14), (0, 4.45, -0.4), "black_metal", 0.01)
    for sx in (-1, 1):
        for sy in (0, 1):
            m.box((0.6, 0.35, 0.2), (sx * 0.38, 4.7 + sy * 0.4 - 0.05, -0.3), "black_metal", 0.02)
            m.box((0.5, 0.26, 0.02), (sx * 0.38, 4.7 + sy * 0.4 - 0.05, -0.19), "em_white")
    hazard(m, "f", (0, 0.4, 1.1), 0, 0.0, 0.0, 1.3, 0.14)


def _h_fire_cannon(m, r):
    m.cyl(0.35, 0.1, (0, 0.05, 0), "hull_dark", seg=12)
    for a in range(4):
        m.cyl(0.03, 0.04, (math.cos(a * 1.57 + 0.785) * 0.28, 0.12, math.sin(a * 1.57 + 0.785) * 0.28), "steel", seg=6)
    m.cyl(0.14, 0.9, (0, 0.55, 0), "paint_red", seg=14)
    m.cyl(0.19, 0.06, (0, 0.13, 0), "steel", seg=14)
    m.sphere(0.2, (0, 1.05, 0), "paint_red", 14, 8)
    m.cyl(0.11, 0.5, (0, 1.05, 0.25), "paint_red", axis="z", seg=12, rot=(0, 0, 0))
    m.link((0, 1.05, 0.2), (0, 1.3, 0.85), 0.11, "paint_red", 12)
    m.cyl(0.14, 0.4, (0, 1.3, 1.05), "paint_red", axis="z", seg=14, r2=0.08)
    m.torus(0.12, 0.02, (0, 1.3, 0.85), "steel", axis="z", seg=12, tseg=4)
    m.cyl(0.075, 0.05, (0, 1.3, 1.27), "chrome", axis="z", seg=12)
    for sx in (-1, 1):
        m.box((0.08, 0.3, 0.12), (sx * 0.16, 1.15, 0.1), "black_metal", 0.01)
    m.cyl(0.05, 0.3, (0.24, 0.5, 0), "steel", axis="x", seg=8)
    m.torus(0.13, 0.015, (0.4, 0.5, 0), "paint_orange", axis="x", seg=14, tseg=4)
    for a in range(3):
        m.box((0.24, 0.015, 0.015), (0.4, 0.5, 0), "paint_orange", 0, (a * 1.047, 0, 0))
    m.box((0.2, 0.08, 0.01), (0, 0.55, 0.145), "paint_white")
    m.link((-0.18, 1.0, 0.0), (-0.45, 0.8, -0.1), 0.02, "black_metal", 5)
    m.box((0.14, 0.16, 0.14), (-0.5, 0.75, -0.1), "hazard_yellow", 0.01)


def _h_gpu(m, r):
    m.box((1.0, 0.9, 0.7), (0, 0.75, 0), "cg_navy", 0.04)
    m.box((1.1, 0.12, 0.8), (0, 0.24, 0), "black_metal", 0.02)
    for sx in (-1, 1):
        wheel(m, sx * 0.5, 0.15, -0.28, 0.15, 0.08, 12)
        m.box((0.05, 0.1, 0.05), (sx * 0.5, 0.25, 0.28), "steel")
    B = (0, 0.75, 0.35)
    fb(m, "f", B, -0.2, 0.1, 0.01, 0.45, 0.4, 0.02, "black_metal", 0.008)
    m.quad((0.36, 0.25), (-0.2, 0.9, 0.362), "screen:power")
    for k in range(3):
        m.cyl(0.03, 0.02, (-0.34 + k * 0.14, 0.7, 0.36), ["em_green", "em_amber", "em_red"][k] if False else "em_green" if k == 0 else "em_amber" if k == 1 else "em_red", axis="z", seg=8)
    for k in range(3):
        m.cyl(0.06, 0.12, (0.2 + k * 0.14 - 0.0, 0.5, 0.4), "black_metal", axis="z", seg=10)
        m.cyl(0.04, 0.03, (0.2 + k * 0.14, 0.5, 0.47), ["paint_red", "gold_trim", "chrome"][k], axis="z", seg=8)
    fb(m, "f", B, 0.28, 0.2, 0.02, 0.3, 0.2, 0.03, "hull_dark", 0.01)
    m.box((0.12, 0.05, 0.02), (0.28, 0.98, 0.38), "em_cyan")
    m.cyl(0.06, 0.3, (0.3, 1.35, -0.2), "steel", seg=8)
    m.cyl(0.09, 0.06, (0.3, 1.52, -0.2), "black_metal", seg=8)
    m.cyl(0.14, 0.12, (-0.5, 0.6, 0.0), "hull_dark", axis="x", seg=12)
    for k in range(3):
        pass
    m.torus(0.16, 0.03, (-0.57, 0.9, -0.1), "black_metal", axis="x", seg=12, tseg=5)
    m.torus(0.12, 0.03, (-0.57, 0.9, -0.1), "black_metal", axis="x", seg=12, tseg=5)
    hazard(m, "f", (0, 0.34, 0.4), 0, 0.0, 0.0, 0.9, 0.09)


def _h_refuel(m, r):
    m.box((0.8, 0.12, 0.7), (0, 0.06, 0), "concrete", 0.008)
    m.box((0.6, 1.5, 0.45), (0, 0.87, 0), "paint_red", 0.03)
    m.box((0.66, 0.25, 0.5), (0, 1.75, 0), "hull_dark", 0.03)
    B = (0, 1.0, 0.225)
    fb(m, "f", B, 0, 0.45, 0.01, 0.5, 0.2, 0.04, "black_metal", 0.01)
    m.quad((0.42, 0.14), (0, 1.45, 0.257), "screen:bars")
    fb(m, "f", B, 0, 0.2, 0.01, 0.4, 0.2, 0.02, "hull_dark", 0.005)
    for k in range(4):
        m.box((0.06, 0.06, 0.02), (-0.1 + (k % 2) * 0.07, 1.25 - (k // 2) * 0.07, 0.24), "plastic_grey")
    m.box((0.12, 0.05, 0.02), (0.15, 1.2, 0.24), "em_green")
    hazard(m, "f", B, 0, -0.55, 0.01, 0.55, 0.09)
    m.box((0.14, 0.32, 0.12), (0.4, 1.0, 0.1), "hull_dark", 0.02)
    m.link((0.4, 1.1, 0.16), (0.4, 0.95, 0.28), 0.035, "black_metal", 6)
    m.cyl(0.03, 0.3, (0.4, 0.9, 0.36), "brass", axis="z", seg=8)
    m.box((0.05, 0.1, 0.05), (0.4, 0.83, 0.42), "paint_green", 0.008)
    m.torus(0.28, 0.035, (-0.35, 0.8, 0.0), "black_metal", axis="x", seg=14, tseg=6)
    m.torus(0.28, 0.035, (-0.4, 0.8, 0.0), "black_metal", axis="x", seg=14, tseg=6)
    m.box((0.5, 0.06, 0.4), (0, 1.9, 0.0), "hazard_yellow", 0.01)
    m.cyl(0.06, 0.12, (-0.2, 2.0, 0.0), "paint_red", seg=8)
    for sx in (-1, 1):
        m.cyl(0.08, 0.7, (sx * 0.62, 0.35, 0.5), "hazard_yellow", seg=10)
        m.cyl(0.085, 0.1, (sx * 0.62, 0.62, 0.5), "paint_red", seg=10)


def _h_engine_stand(m, r):
    for sx in (-1, 1):
        m.box((0.1, 0.1, 1.8), (sx * 0.6, 0.2, 0), "paint_orange", 0.01)
        caster(m, sx * 0.6, 0.8, 0.08, 0.05)
        caster(m, sx * 0.6, -0.8, 0.08, 0.05)
        m.box((0.1, 0.9, 0.1), (sx * 0.6, 0.65, 0.5), "paint_orange", 0.008)
        m.box((0.1, 0.9, 0.1), (sx * 0.6, 0.65, -0.5), "paint_orange", 0.008)
        for z in (-0.5, 0.5):
            m.box((0.1, 0.1, 0.1), (sx * 0.6, 1.12, z), "hull_dark", 0.01)
    m.box((1.3, 0.06, 0.06), (0, 0.25, 0.5), "paint_orange")
    m.box((1.3, 0.06, 0.06), (0, 0.25, -0.5), "paint_orange")
    m.cyl(0.4, 1.5, (0, 1.45, 0), "hull_mid", axis="z", seg=20)
    m.cyl(0.4, 0.4, (0, 1.45, 0.95), "hull_mid", axis="z", seg=20, r2=0.24)
    m.cyl(0.42, 0.04, (0, 1.45, 0.5), "steel", axis="z", seg=20)
    m.cyl(0.42, 0.04, (0, 1.45, -0.5), "steel", axis="z", seg=20)
    for a in range(10):
        ang = a * 0.628
        m.box((0.05, 0.04, 0.5), (math.cos(ang) * 0.42, 1.45 + math.sin(ang) * 0.42, 0), "gunmetal", 0.004, (0, 0, ang))
    nozzle(m, 0, 1.45, -0.75, 0.34, 0.5, "gunmetal")
    m.link((0.35, 1.7, 0.2), (0.35, 2.0, 0.2), 0.03, "copper", 6)
    m.link((-0.3, 1.75, -0.2), (-0.3, 2.0, -0.2), 0.03, "brass", 6)
    m.torus(0.42, 0.015, (0, 1.45, 0.2), "hazard_yellow", axis="z", seg=20, tseg=4)


def _h_diag_cart(m, r):
    m.box((0.8, 0.06, 0.55), (0, 0.5, 0), "steel", 0.008)
    m.box((0.8, 0.06, 0.55), (0, 0.15, 0), "steel", 0.008)
    for sx in (-1, 1):
        m.box((0.05, 1.15, 0.05), (sx * 0.38, 0.6, -0.24), "paint_blue")
        m.box((0.05, 0.4, 0.05), (sx * 0.38, 0.33, 0.24), "paint_blue")
        caster(m, sx * 0.35, 0.22, 0.075, 0.04)
        caster(m, sx * 0.35, -0.22, 0.075, 0.04)
    m.box((0.75, 0.05, 0.05), (0, 1.15, -0.24), "paint_blue")
    m.box((0.6, 0.4, 0.05), (0, 1.0, -0.2), "black_metal", 0.012, (-0.15, 0, 0))
    m.quad((0.54, 0.34), (0, 1.0, -0.17), "screen:diagnostic", rot=(-0.15, 0, 0))
    m.box((0.6, 0.06, 0.25), (0, 0.55, 0.05), "plastic_black", 0.01)
    m.box((0.5, 0.01, 0.15), (0, 0.585, 0.05), "plastic_grey")
    m.box((0.4, 0.12, 0.3), (-0.1, 0.24, 0.0), "hull_dark", 0.015)
    m.box((0.25, 0.1, 0.2), (0.22, 0.22, 0.0), "cg_ptl_yellow", 0.012)
    for k in range(3):
        m.cyl(0.02, 0.2, (0.15 + k * 0.08, 0.35, 0.1), "black_metal", seg=6)
    m.torus(0.1, 0.02, (0.3, 0.32, 0.22), "cg_ptl_blue", axis="z", seg=10, tseg=5)
    m.torus(0.1, 0.02, (0.3, 0.35, 0.22), "paint_red", axis="z", seg=10, tseg=5)
    m.link((0.39, 0.95, -0.24), (0.55, 0.85, -0.1), 0.012, "black_metal", 5)
    m.box((0.05, 0.16, 0.04), (0.56, 0.75, -0.08), "black_metal", 0.008)
    m.box((0.03, 0.03, 0.03), (0.56, 0.66, -0.08), "em_cyan")


def _h_parts_washer(m, r):
    W, D = 1.2, 0.8
    m.box((W, 0.8, D), (0, 0.4, 0), "hull_mid", 0.02)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.06, 0.1, 0.06), (sx * 0.55, 0.05, sz * 0.35), "black_metal")
    m.box((W - 0.08, 0.04, D - 0.08), (0, 0.82, 0), "steel")
    m.box((W - 0.2, 0.03, D - 0.2), (0, 0.85, 0), "black_metal")
    for k in range(9):
        m.box((0.02, 0.02, D - 0.22), (-0.5 + k * 0.125, 0.87, 0), "steel")
    m.box((W, 0.6, 0.06), (0, 1.15, -D / 2 + 0.03), "hull_mid", 0.01)
    m.box((0.06, 0.6, D), (-W / 2 + 0.03, 1.15, 0), "hull_mid", 0.01)
    m.box((0.06, 0.6, D), (W / 2 - 0.03, 1.15, 0), "hull_mid", 0.01)
    # hinged lid open
    m.box((W, 0.05, 0.75), (0, 1.66, -0.62), "hull_light", 0.01, (-1.15, 0, 0))
    m.link((-0.4, 1.0, 0.1), (0.4, 1.0, 0.1), 0.03, "steel", 8)
    m.link((0.0, 1.0, 0.1), (0.0, 0.9, -0.2), 0.02, "steel", 6)
    m.link((0.0, 1.35, -0.3), (0.35, 1.25, 0.1), 0.02, "black_metal", 6)
    m.box((0.05, 0.05, 0.05), (0.35, 1.25, 0.1), "steel")
    m.cyl(0.05, 0.3, (0.3, 1.5, -0.3), "chrome", seg=8)
    m.link((0.3, 1.65, -0.3), (0.3, 1.7, 0.1), 0.05, "chrome", 8)
    m.box((0.22, 0.2, 0.06), (-0.38, 0.62, D / 2 + 0.02), "black_metal", 0.01)
    m.box((0.1, 0.05, 0.02), (-0.38, 0.65, D / 2 + 0.055), "em_green")
    m.cyl(0.025, 0.03, (-0.43, 0.58, D / 2 + 0.05), "paint_red", axis="z", seg=8)
    m.cyl(0.25, 0.7, (1.0, 0.35, -0.1), "cg_ptl_blue", seg=14)
    m.cyl(0.26, 0.04, (1.0, 0.7, -0.1), "steel", seg=14)
    m.cyl(0.04, 0.05, (1.1, 0.73, -0.1), "black_metal", seg=8)
    m.link((0.8, 0.5, -0.1), (0.6, 0.45, 0.0), 0.02, "black_metal", 5)
    m.box((0.5, 0.1, 0.006), (0.2, 0.3, D / 2 + 0.004), "hazard_yellow")


def _h_avionics_bench(m, r):
    m.box((2.0, 0.05, 0.8), (0, 0.9, 0), "wood_light", 0.008)
    m.box((2.02, 0.04, 0.82), (0, 0.88, 0), "steel", 0.006)
    for sx in (-1, 1):
        m.box((0.06, 0.88, 0.7), (sx * 0.93, 0.44, 0), "hull_dark", 0.008)
    m.box((1.8, 0.04, 0.7), (0, 0.22, 0), "hull_mid")
    m.box((1.8, 0.4, 0.04), (0, 0.5, -0.33), "hull_dark")
    for k in range(3):
        pass
    m.box((0.45, 0.28, 0.4), (-0.6, 0.38, 0.0), "cg_blue", 0.012)
    m.box((0.45, 0.28, 0.4), (0.0, 0.38, 0.0), "hull_light", 0.012)
    m.box((0.45, 0.28, 0.4), (0.6, 0.38, 0.0), "cg_olive", 0.012)
    # back panel
    m.box((2.0, 0.7, 0.05), (0, 1.5, -0.37), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.05, 0.75, 0.05), (sx * 0.98, 1.32, -0.34), "hull_dark")
    m.quad((0.5, 0.35), (-0.55, 1.5, -0.34), "screen:waveform")
    m.quad((0.4, 0.3), (0.05, 1.5, -0.34), "screen:diagnostic")
    m.quad((0.4, 0.3), (0.55, 1.5, -0.34), "screen:graph")
    for x, w, h in ((-0.55, 0.5, 0.35), (0.05, 0.4, 0.3), (0.55, 0.4, 0.3)):
        m.box((w + 0.04, h + 0.04, 0.02), (x, 1.5, -0.352), "black_metal", 0.006)
    # instruments
    m.box((0.6, 0.15, 0.32), (-0.5, 1.0, 0.0), "hull_light", 0.015)
    for k in range(5):
        m.cyl(0.03, 0.02, (-0.7 + k * 0.1, 1.03, 0.17), "chrome", axis="z", seg=8)
    m.box((0.4, 0.18, 0.3), (0.3, 1.02, 0.05), "black_metal", 0.015)
    m.quad((0.28, 0.1), (0.3, 1.04, 0.202), "screen:radar")
    m.box((0.14, 0.08, 0.14), (0.75, 0.97, 0.15), "hazard_yellow", 0.01)
    m.link((0.75, 1.0, 0.2), (0.6, 0.95, 0.35), 0.008, "copper", 4)
    m.box((0.06, 0.12, 0.06), (-0.85, 0.99, 0.2), "steel")
    m.cyl(0.05, 0.2, (0.85, 0.96, -0.2), "brass", seg=8)
    m.box((0.3, 0.04, 0.5), (0.5, 0.945, 0.15), "cg_ptl_green", 0.005)
    m.cyl(0.03, 0.1, (-0.9, 1.75, -0.34), "em_amber", seg=8)


def _h_barrier(m, r):
    L = 3.0
    for sx in (-1, 1):
        m.box((0.1, 0.9, 0.1), (sx * (L / 2 - 0.1), 0.55, 0), "black_metal", 0.008)
        m.box((0.1, 0.12, 0.6), (sx * (L / 2 - 0.1), 0.06, 0), "black_metal", 0.008)
        m.cyl(0.06, 0.12, (sx * (L / 2 - 0.1), 1.05, 0), "hazard_yellow", seg=8)
        m.cyl(0.05, 0.03, (sx * (L / 2 - 0.1), 1.13, 0), "em_amber", seg=8)
    for y in (0.5, 0.85):
        m.box((L, 0.24, 0.05), (0, y, 0), "paint_white", 0.006)
        n = 12
        for k in range(n):
            x = -L / 2 + 0.25 + k * (L - 0.5) / (n - 1)
        for k in range(10):
            x = -L / 2 + 0.3 + k * (L - 0.6) / 9
            m.box((0.1, 0.28, 0.056), (x, y, 0), "paint_red", 0, (0, 0, 0.6))
    m.box((0.1, 0.9, 0.1), (0, 0.55, 0), "black_metal", 0.008)
    m.box((0.1, 0.12, 0.6), (0, 0.06, 0), "black_metal", 0.008)


def _h_bollards(m, r):
    for k, x in enumerate((-0.8, 0.0, 0.8)):
        m.cyl(0.2, 0.05, (x, 0.025, 0), "steel", seg=12)
        m.cyl(0.12, 1.0, (x, 0.55, 0), "hazard_yellow", seg=14)
        m.cyl(0.125, 0.14, (x, 0.75, 0), "paint_red", seg=14)
        m.cyl(0.125, 0.16, (x, 0.35, 0), "black_metal", seg=14)
        m.cyl(0.125, 0.06, (x, 0.2, 0), "black_metal", seg=14)
        m.sphere(0.12, (x, 1.05, 0), "hazard_yellow", 14, 6, (1, 0.5, 1))
        m.cyl(0.13, 0.03, (x, 0.95, 0), "steel", seg=14)
        m.cyl(0.128, 0.05, (x, 0.9, 0), "em_amber" if k != 1 else "em_red", seg=14)
        for a in range(4):
            m.cyl(0.02, 0.03, (x + math.cos(a * 1.57) * 0.16, 0.06, math.sin(a * 1.57) * 0.16), "steel", seg=6)
    m.link((-0.8, 0.9, 0), (0.0, 0.8, 0), 0.012, "cg_strap", 5)
    m.link((0.0, 0.8, 0), (0.8, 0.9, 0), 0.012, "cg_strap", 5)


def _h_door_pillar(m, r):
    m.box((0.5, 0.1, 0.5), (0, 0.05, 0), "black_metal", 0.01)
    m.box((0.34, 2.4, 0.34), (0, 1.3, 0), "hull_light", 0.03)
    m.box((0.36, 0.3, 0.36), (0, 2.6, 0), "hull_dark", 0.03)
    B = (0, 1.4, 0.17)
    fb(m, "f", B, 0, 0.15, 0.005, 0.26, 0.4, 0.04, "black_metal", 0.01)
    m.quad((0.22, 0.32), (0, 1.55, 0.2), "screen:alert")
    for k, c in enumerate(("em_green", "em_amber", "em_red")):
        fb(m, "f", B, 0, -0.1 - k * 0.14, 0.03, 0.16, 0.1, 0.05, "hull_dark", 0.01)
        fb(m, "f", B, 0, -0.1 - k * 0.14, 0.055, 0.12, 0.07, 0.03, c, 0.01)
    m.cyl(0.05, 0.04, (0.0, 0.88, 0.19), "steel", axis="z", seg=10)
    m.box((0.02, 0.06, 0.02), (0.0, 0.9, 0.22), "black_metal")
    m.cyl(0.08, 0.06, (0.0, 1.2 + 0.0, 0.19) if False else (0.0, 0.7, 0.2), "paint_red", axis="z", seg=12)
    m.cyl(0.1, 0.03, (0.0, 0.7, 0.18), "hazard_yellow", axis="z", seg=12)
    m.cyl(0.13, 0.22, (0, 2.85, 0), "glass_amber", seg=12)
    m.cyl(0.14, 0.03, (0, 2.72, 0), "black_metal", seg=12)
    m.cyl(0.14, 0.03, (0, 2.97, 0), "black_metal", seg=12)
    hazard(m, "f", (0, 0.35, 0.17), 0, 0.0, 0.0, 0.3, 0.12)
    hazard(m, "r", (0.17, 0.35, 0), 0, 0.0, 0.0, 0.3, 0.12)
    hazard(m, "l", (-0.17, 0.35, 0), 0, 0.0, 0.0, 0.3, 0.12)
    for y in (2.1, 2.3):
        m.box((0.36, 0.05, 0.36), (0, y, 0), "hazard_yellow", 0.004)


def _h_wall_winch(m, r):
    m.box((0.9, 0.7, 0.05), (0, 0, 0.025), "hull_dark", 0.01)
    for sx in (-1, 1):
        m.box((0.06, 0.5, 0.35), (sx * 0.28, 0.05, 0.22), "paint_orange", 0.01)
    m.cyl(0.2, 0.5, (0, 0.05, 0.25), "hull_dark", axis="x", seg=16)
    for sx in (-1, 1):
        m.cyl(0.26, 0.04, (sx * 0.24, 0.05, 0.25), "steel", axis="x", seg=16)
    for k in range(5):
        m.torus(0.2, 0.02, (-0.16 + k * 0.08, 0.05, 0.25), "black_metal", axis="x", seg=16, tseg=4)
    m.box((0.3, 0.3, 0.3), (0.55, 0.05, 0.2), "hull_mid", 0.02)
    m.cyl(0.08, 0.1, (0.55, 0.05, 0.38), "black_metal", axis="z", seg=10)
    m.link((0.28, 0.05, 0.25), (0.4, 0.05, 0.25), 0.05, "steel", 8)
    m.link((0.0, -0.15, 0.25), (0.0, -0.9, 0.35), 0.015, "black_metal", 5)
    m.box((0.14, 0.12, 0.14), (0.0, -0.98, 0.35), "paint_red", 0.02)
    m.torus(0.07, 0.02, (0.0, -1.12, 0.35), "steel", axis="x", seg=12, tseg=5, arc=4.7)
    m.box((0.14, 0.2, 0.06), (-0.55, 0.15, 0.06), "black_metal", 0.01)
    m.box((0.05, 0.05, 0.02), (-0.55, 0.2, 0.1), "em_green")
    m.box((0.05, 0.05, 0.02), (-0.55, 0.1, 0.1), "em_red")
    hazard(m, "f", (0, -0.28, 0.05), 0, 0.0, 0.0, 0.8, 0.08)
    for x, y in ((-0.4, 0.28), (0.4, 0.28), (-0.4, -0.28), (0.4, -0.28)):
        m.cyl(0.03, 0.02, (x, y, 0.06), "steel", axis="z", seg=6)


def _h_compressor(m, r):
    m.cyl(0.3, 1.1, (0, 0.65, 0), "paint_red", axis="x", seg=18)
    m.sphere(0.3, (-0.55, 0.65, 0), "paint_red", 18, 8, (0.5, 1, 1))
    m.sphere(0.3, (0.55, 0.65, 0), "paint_red", 18, 8, (0.5, 1, 1))
    m.torus(0.305, 0.015, (-0.3, 0.65, 0), "steel", axis="x", seg=18, tseg=4)
    m.torus(0.305, 0.015, (0.3, 0.65, 0), "steel", axis="x", seg=18, tseg=4)
    m.box((1.4, 0.06, 0.5), (0, 0.24, 0), "black_metal", 0.01)
    for sx in (-1, 1):
        wheel(m, sx * 0.55, 0.14, -0.25, 0.14, 0.06, 10)
        m.box((0.06, 0.16, 0.06), (sx * 0.55, 0.16, 0.25), "black_metal")
    m.box((0.8, 0.3, 0.28), (0, 1.1, 0.0), "hull_dark", 0.02)
    m.cyl(0.12, 0.3, (0.0, 1.35, 0.0), "gunmetal", seg=10)
    for k in range(5):
        pass
    m.cyl(0.14, 0.1, (-0.2, 1.3, 0.0), "steel", seg=10)
    m.cyl(0.14, 0.1, (0.2, 1.3, 0.0), "steel", seg=10)
    m.link((-0.2, 1.2, 0.1), (0.2, 0.95, 0.3), 0.02, "copper", 5)
    m.cyl(0.08, 0.04, (0.35, 0.9, 0.3), "black_metal", axis="z", seg=12)
    m.cyl(0.065, 0.01, (0.35, 0.9, 0.32), "paint_white", axis="z", seg=12)
    m.cyl(0.08, 0.04, (0.0, 0.9, 0.3), "black_metal", axis="z", seg=12)
    m.cyl(0.065, 0.01, (0.0, 0.9, 0.32), "paint_white", axis="z", seg=12)
    m.torus(0.16, 0.03, (0.6, 0.62, 0.32), "cg_ptl_yellow", axis="x", seg=12, tseg=5)
    m.torus(0.16, 0.03, (0.66, 0.62, 0.32), "cg_ptl_yellow", axis="x", seg=12, tseg=5)
    m.cyl(0.03, 0.06, (0.0, 0.32 + 0.0, 0.32), "brass", axis="z", seg=8)
    m.box((0.1, 0.05, 0.02), (-0.3, 0.95, 0.15), "em_green")


def _h_paint_screen(m, r):
    for k in range(3):
        x = -0.95 + k * 0.95
        m.box((0.9, 2.0, 0.05), (x, 1.25, 0), "glass_dark" if False else "cg_wrap", 0.004)
        m.box((0.06, 2.2, 0.08), (x - 0.45, 1.2, 0), "hull_mid", 0.008)
        m.box((0.06, 2.2, 0.08), (x + 0.45, 1.2, 0), "hull_mid", 0.008)
        m.box((0.9, 0.08, 0.08), (x, 2.2, 0), "hull_mid", 0.008)
        m.box((0.9, 0.08, 0.08), (x, 0.3, 0), "hull_mid", 0.008)
        for j in range(4):
            m.box((0.8, 0.03, 0.02), (x, 0.7 + j * 0.42, 0.03), "paint_grey")
        m.box((0.6, 0.08, 0.5), (x, 0.06, 0.0), "black_metal", 0.008)
    for x in (-1.4, 1.4):
        m.box((0.08, 2.2, 0.08), (x + (0.0 if x < 0 else 0.0), 1.2, 0), "hull_mid")
    for k in range(3):
        x = -0.95 + k * 0.95
    m.box((0.6, 0.08, 0.02), (0, 2.05, 0.04), "hazard_yellow")
    m.box((0.16, 0.16, 0.01), (0, 1.2, 0.05), "paint_red", 0, (0, 0, 0.785))
    m.box((0.04, 0.1, 0.012), (0, 1.2, 0.058), "paint_white")
    m.box((0.3, 0.3, 0.14), (0, 2.42, 0.0), "hull_dark", 0.02)
    m.cyl(0.11, 0.03, (0, 2.42, 0.08), "em_white", axis="z", seg=12)


def _h_crash_cart(m, r):
    m.box((1.0, 0.1, 0.6), (0, 0.3, 0), "paint_red", 0.01)
    m.box((1.0, 0.9, 0.05), (0, 0.8, -0.28), "paint_red", 0.012)
    for sx in (-1, 1):
        m.box((0.05, 0.55, 0.55), (sx * 0.47, 0.6, 0), "paint_red", 0.01)
        caster(m, sx * 0.42, 0.22, 0.1, 0.05)
        caster(m, sx * 0.42, -0.22, 0.1, 0.05)
    m.box((1.0, 0.05, 0.05), (0, 1.3, -0.3), "black_metal", 0.008)
    # extinguisher
    m.cyl(0.09, 0.55, (-0.3, 0.65, 0.05), "paint_red", seg=12)
    m.sphere(0.09, (-0.3, 0.93, 0.05), "paint_red", 12, 6, (1, 0.6, 1))
    m.cyl(0.03, 0.08, (-0.3, 1.0, 0.05), "chrome", seg=8)
    m.box((0.14, 0.03, 0.03), (-0.26, 1.04, 0.05), "black_metal")
    m.link((-0.3, 0.6, 0.14), (-0.1, 0.5, 0.25), 0.012, "black_metal", 5)
    m.cyl(0.09, 0.55, (-0.1, 0.65, 0.05), "paint_white", seg=12)
    m.sphere(0.09, (-0.1, 0.93, 0.05), "paint_white", 12, 6, (1, 0.6, 1))
    m.cyl(0.03, 0.08, (-0.1, 1.0, 0.05), "chrome", seg=8)
    m.box((0.09, 0.03, 0.03), (-0.1, 1.04, 0.05), "paint_red")
    m.box((0.36, 0.2, 0.22), (0.25, 0.47, 0.05), "plastic_white", 0.02)
    m.box((0.05, 0.14, 0.02), (0.25, 0.5, 0.165), "paint_red")
    m.box((0.14, 0.05, 0.02), (0.25, 0.5, 0.165), "paint_red")
    m.box((0.36, 0.18, 0.2), (0.25, 0.66, 0.05), "cg_ptl_yellow", 0.015)
    m.cyl(0.03, 0.6, (0.0, 1.0, -0.2), "steel", axis="x", seg=6)
    m.link((0.35, 1.1, -0.24), (0.4, 0.85, -0.2), 0.02, "paint_orange", 5)
    m.box((0.08, 0.06, 0.06), (0.42, 0.8, -0.2), "paint_orange", 0.008)
    m.box((0.1, 0.3, 0.01), (0.0, 0.85, -0.25), "paint_white")
    m.box((0.3, 0.1, 0.01), (0.0, 0.85, -0.25), "paint_white")
    m.cyl(0.03, 0.04, (0.4, 1.36, -0.3), "em_red", seg=8)


def _h_nose_dolly(m, r):
    m.box((1.0, 0.1, 1.4), (0, 0.25, 0), "hazard_yellow", 0.015)
    m.prism([(-0.5, 0.7), (0.5, 0.7), (0.1, 1.6), (-0.1, 1.6)], 0.1, (0, 0.2, 0), "hazard_yellow", bevel=0.01)
    for sx in (-1, 1):
        wheel(m, sx * 0.55, 0.15, -0.5, 0.15, 0.1, 12)
        m.box((0.08, 0.16, 0.14), (sx * 0.5, 0.25, -0.5), "black_metal")
        m.box((0.12, 0.35, 0.5), (sx * 0.38, 0.5, -0.1), "paint_orange", 0.015)
        m.box((0.1, 0.1, 0.4), (sx * 0.38, 0.72, -0.1), "rubber", 0.02)
    m.box((0.8, 0.1, 0.1), (0, 0.55, -0.35), "paint_orange", 0.01)
    m.torus(0.1, 0.03, (0, 0.28, 1.72), "steel", axis="x", seg=12, tseg=5)
    m.link((0, 0.28, 1.6), (0, 0.28, 1.7), 0.03, "steel", 6)
    for sx in (-1, 1):
        m.cyl(0.08, 0.1, (sx * 0.3, 0.1, 1.1), "rubber", axis="x", seg=10)
    hazard(m, "f", (0, 0.25, 0.7), 0, 0.0, 0.0, 1.0, 0.09)
    for k in range(4):
        m.box((0.6, 0.012, 0.03), (0, 0.306, -0.3 + k * 0.12), "black_metal")
    m.box((0.08, 0.12, 0.08), (0.0, 0.36, 0.6), "paint_red", 0.01)


def _h_cones(m, r):
    def cone(x, z, h=0.7, R=0.17):
        m.box((0.42, 0.04, 0.42), (x, 0.02, z), "rubber", 0.01)
        m.cyl(R, h, (x, 0.04 + h / 2, z), "paint_orange", seg=12, r2=0.03)
        m.cyl(R * 0.62, 0.11, (x, 0.04 + h * 0.5, z), "paint_white", seg=12, r2=R * 0.5)
    cone(-0.9, 0.55)
    cone(-0.9, -0.1, 0.5, 0.14)
    cone(-0.4, 0.35, 0.36, 0.11)

    def barrier(x, z, ry):
        c, s = math.cos(ry), math.sin(ry)
        for sd in (-1, 1):
            px, pz = x + sd * 0.55 * c, z - sd * 0.55 * s
            m.box((0.06, 0.08, 0.5), (px, 0.04, pz), "black_metal", 0, (0, ry, 0))
            m.box((0.05, 0.9, 0.05), (px, 0.5, pz), "steel")
        for y in (0.6, 0.9):
            m.box((1.2, 0.2, 0.04), (x, y, z), "paint_white", 0.004, (0, ry, 0))
            for k in range(5):
                u = -0.5 + k * 0.25
                m.box((0.09, 0.21, 0.046), (x + u * c, y, z - u * s), "paint_red", 0, (0, ry, 0))
    barrier(0.4, -0.4, 0.0)
    barrier(0.9, 0.5, -0.5)
    m.torus(0.1, 0.03, (-0.3, 0.06, -0.5), "hazard_yellow", seg=12, tseg=5)
    m.torus(0.13, 0.03, (-0.3, 0.09, -0.5), "black_metal", seg=12, tseg=5)


def _h_mooring(m, r):
    m.box((1.0, 0.05, 1.0), (0, 0.025, 0), "hull_dark", 0.008)
    m.box((0.8, 0.02, 0.8), (0, 0.06, 0), "gunmetal", 0.005)
    m.cyl(0.32, 0.03, (0, 0.075, 0), "black_metal", seg=16)
    m.cyl(0.26, 0.03, (0, 0.06, 0), "carbon", seg=16)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.cyl(0.035, 0.02, (sx * 0.4, 0.075, sz * 0.4), "steel", seg=6)
            m.box((0.01, 0.012, 0.05), (sx * 0.4, 0.087, sz * 0.4), "black_metal")
    m.box((0.12, 0.05, 0.12), (0, 0.1, -0.08), "steel", 0.008)
    m.torus(0.14, 0.04, (0, 0.17, -0.08), "chrome", axis="z", seg=18, tseg=6)
    for sx in (-1, 1):
        m.box((0.4, 0.012, 0.06), (0, 0.072, sx * 0.44), "hazard_yellow")
    m.cyl(0.03, 0.012, (0.0, 0.07, 0.45), "em_amber", seg=8)


HT_FLOOR = [
    ("fuel_hose_reel", _h_hose_reel), ("tool_cart", _h_toolcart), ("engine_hoist", _h_engine_hoist),
    ("tripod_jack", _h_jack), ("wheel_chocks", _h_chocks), ("tow_bar", _h_tow_bar),
    ("launch_rail_segment", _h_launch_rail), ("docking_clamp", _h_dock_clamp), ("light_tower", _h_light_tower),
    ("fire_cannon", _h_fire_cannon), ("ground_power_unit", _h_gpu), ("refuelling_pump", _h_refuel),
    ("engine_stand", _h_engine_stand), ("diagnostics_cart", _h_diag_cart), ("parts_washer", _h_parts_washer),
    ("avionics_bench", _h_avionics_bench), ("safety_barrier", _h_barrier), ("bollard_set", _h_bollards),
    ("door_control_pillar", _h_door_pillar), ("air_compressor", _h_compressor), ("paint_booth_screen", _h_paint_screen),
    ("crash_cart", _h_crash_cart), ("nose_gear_dolly", _h_nose_dolly), ("cones_and_barriers", _h_cones),
]
HT_PAD = [("landing_pad_circle", _h_pad_a), ("landing_pad_square", _h_pad_b), ("mooring_ring", _h_mooring)]
HT_WALL = [("wall_winch", _h_wall_winch)]
family("hangartool", [c[0] for c in HT_FLOOR], mount="floor", tags=["hangar"], solid=True)(_dispatch(HT_FLOOR))
family("hangartool", [c[0] for c in HT_PAD], mount="floor", tags=["hangar"], solid=False)(_dispatch(HT_PAD))
family("hangartool", [c[0] for c in HT_WALL], mount="wall", tags=["hangar"], solid=False)(_dispatch(HT_WALL))
