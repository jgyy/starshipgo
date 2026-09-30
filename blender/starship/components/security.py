"""Security, safety, signage: armory, brig, surveillance, forcefields, safety gear, signs, beacons, suit racks."""
import math

from ..kit import family as _family, register_material

register_material("sec_blaster", "#3b424c", 0.8, 0.35)
register_material("sec_sign_green", "#0f7a3f", 0.1, 0.5)
register_material("sec_sign_blue", "#1a4f9c", 0.1, 0.5)
register_material("sec_sign_black", "#101215", 0.1, 0.5)
register_material("sec_sign_red", "#b5211a", 0.1, 0.5)
register_material("sec_sign_purple", "#5a2a86", 0.1, 0.5)
register_material("sec_mat", "#2a2d31", 0.0, 0.9)
register_material("sec_field", "#4d95ff", 0.0, 0.05, alpha=0.28)

PI = math.pi


def _lean(fn):
    """Wrap a generator so tiny boxes get no bevel and small cylinders fewer segments (keeps GLBs small)."""
    import functools

    @functools.wraps(fn)
    def wrapper(m, i, label, rng):
        ob, oc = m.box, m.cyl

        def box(size, pos=(0, 0, 0), mat="hull_mid", bevel=0.0, rot=(0, 0, 0)):
            if min(size) < 0.08:
                bevel = 0.0
            return ob(size, pos, mat, bevel, rot)

        def cyl(r, h, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=16, r2=None, cap=True, rot=(0, 0, 0), bevel=0.0):
            if r < 0.06:
                seg = min(seg, 8)
            elif r < 0.15:
                seg = min(seg, 12)
            return oc(r, h, pos, mat, axis, seg, r2, cap, rot, 0.0 if r < 0.1 else bevel)

        m.box, m.cyl = box, cyl
        return fn(m, i, label, rng)
    return wrapper


def family(*a, **k):
    deco = _family(*a, **k)
    return lambda fn: deco(_lean(fn))


# ---------------------------------------------------------------- helpers
def bolts(m, pts, z, mat="steel", r=0.011):
    for x, y in pts:
        m.cyl(r, 0.008, (x, y, z), mat, axis="z", seg=6)


def field(m, w, h, pos, mat="sec_field", lines=True):
    """Double-sided translucent energy plane facing +Z/-Z with emissive scan lines."""
    x, y, z = pos
    m.quad((w, h), (x, y, z), mat)
    m.quad((w, h), (x, y, z), mat, rot=(0, PI, 0))
    if lines:
        for k in range(3):
            yy = y - h / 2 + h * (k + 1) / 4
            m.box((w, 0.012, 0.006), (x, yy, z), "em_blue")


def blaster(m, o, kind="rifle", vert=False, col="sec_blaster", cell="em_cyan", flip=1):
    """Generic sci-fi blaster. o = rear-bottom of stock. Length axis is X (or Y if vert);
    'up' of the weapon is Y (or Z if vert); side is Z (or X)."""
    ox, oy, oz = o

    def P(a, u, s):
        a *= flip
        return (ox + a, oy + u, oz + s) if not vert else (ox + s, oy + a, oz + u)

    def S(a, u, s):
        return (a, u, s) if not vert else (s, a, u)

    ax = "x" if not vert else "y"

    def C(r, L, a, u, s, mat, seg=8):
        m.cyl(r, L, P(a, u, s), mat, axis=ax, seg=seg)

    if kind == "pistol":
        m.box(S(0.17, 0.05, 0.03), P(0.09, 0.075, 0), col, 0.006)
        m.box(S(0.04, 0.09, 0.028), P(0.04, 0.0, 0), "plastic_black", 0.005)
        C(0.011, 0.09, 0.2, 0.085, 0, "gunmetal")
        m.box(S(0.05, 0.012, 0.012), P(0.13, 0.112, 0), cell)
    elif kind == "heavy":
        m.box(S(0.3, 0.09, 0.06), P(0.15, 0.09, 0), "plastic_black", 0.008)
        m.box(S(0.5, 0.16, 0.09), P(0.53, 0.115, 0), col, 0.01)
        C(0.028, 0.5, 1.03, 0.13, 0, "gunmetal", 10)
        C(0.036, 0.1, 0.83, 0.13, 0, "black_metal", 10)
        m.box(S(0.2, 0.05, 0.1), P(0.55, 0.22, 0), "gunmetal", 0.005)
        m.box(S(0.14, 0.05, 0.02), P(0.5, 0.115, 0.05), cell)
        m.box(S(0.05, 0.13, 0.04), P(0.6, 0.0, 0), "plastic_black", 0.005)
    elif kind == "carbine":
        m.box(S(0.2, 0.07, 0.04), P(0.1, 0.1, 0), "plastic_black", 0.006)
        m.box(S(0.32, 0.09, 0.05), P(0.36, 0.09, 0), col, 0.008)
        C(0.014, 0.25, 0.64, 0.1, 0, "gunmetal")
        m.box(S(0.045, 0.1, 0.035), P(0.32, 0.0, 0), "plastic_black", 0.004)
        m.box(S(0.12, 0.025, 0.02), P(0.36, 0.09, 0.03), cell)
    else:  # rifle
        m.box(S(0.24, 0.09, 0.05), P(0.12, 0.1, 0), "plastic_black", 0.008)
        m.box(S(0.4, 0.11, 0.06), P(0.44, 0.1, 0), col, 0.008)
        C(0.016, 0.34, 0.81, 0.11, 0, "gunmetal")
        C(0.024, 0.06, 0.96, 0.11, 0, "black_metal")
        m.box(S(0.05, 0.11, 0.035), P(0.42, 0.0, 0), "plastic_black", 0.004)
        m.box(S(0.14, 0.03, 0.02), P(0.5, 0.1, 0.032), cell)
        C(0.02, 0.16, 0.42, 0.185, 0, "black_metal")
        m.box(S(0.06, 0.05, 0.05), P(0.18, 0.0, 0), "plastic_black", 0.004)


def locker_shell(m, w, h, d, body="hull_mid", inner="hull_dark", glass="glass", front=True, base=0.1, z0=0.0):
    """Cabinet carcass, open at the front, with an optional glass front pane. Returns inner bounds."""
    t = 0.03
    cz = z0
    m.box((w, h - base, t), (0, base + (h - base) / 2, cz - d / 2 + t / 2), inner)
    for s in (-1, 1):
        m.box((t, h - base, d), (s * (w / 2 - t / 2), base + (h - base) / 2, cz), body, 0.005)
    m.box((w, t, d), (0, h - t / 2, cz), body, 0.005)
    m.box((w, t, d), (0, base + t / 2, cz), body, 0.005)
    m.box((w - 0.04, base, d - 0.06), (0, base / 2, cz), "black_metal")
    if front:
        m.box((w - 0.02, h - base - 0.02, 0.01), (0, base + (h - base) / 2, cz + d / 2 - 0.005), glass)
        m.box((0.03, h - base - 0.1, 0.03), (w / 2 - 0.1, base + (h - base) / 2, cz + d / 2 + 0.01), "chrome", 0.005)
    return (-w / 2 + t, w / 2 - t, base + t, h - t, cz - d / 2 + t, cz + d / 2 - t)


# ---- tiny 3x5 pixel font for sign text
_F = {
    "A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110",
    "E": "111100110100111", "F": "111100110100100", "G": "011100101101011", "H": "101101111101101",
    "I": "111010010010111", "K": "101101110101101", "L": "100100100100111", "M": "101111111101101",
    "N": "110101101101101", "O": "010101101101010", "Q": "010101101111011", "R": "110101110101101",
    "S": "011100010001110", "T": "111010010010010", "U": "101101101101111", "Y": "101101010010010", "X": "101101010101101",
    "1": "010110010010111", "2": "110001010100111", "3": "110001010001110", "-": "000000111000000",
    " ": "000000000000000", "!": "010010010000010",
}


def text(m, s, cx, cy, z, px, mat="paint_white", ):
    """Flat pixel text made of single-sided quads facing +Z. px = pixel size."""
    n = len(s)
    total = n * 4 - 1
    x0 = cx - total * px / 2
    for ci, ch in enumerate(s):
        g = _F.get(ch, _F[" "])
        for row in range(5):
            col = 0
            while col < 3:
                if g[row * 3 + col] == "1":
                    e = col
                    while e + 1 < 3 and g[row * 3 + e + 1] == "1":
                        e += 1
                    w = (e - col + 1) * px
                    x = x0 + (ci * 4 + col) * px + w / 2
                    y = cy + (2 - row) * px
                    m.quad((w, px), (x, y, z), mat)
                    col = e + 1
                else:
                    col += 1


# ================================================================= WEAPON RACKS
@family("weaponrack", ["rifle_rack_wall", "pistol_rack_wall", "riot_shield_rack", "target_range_panel",
                       "cell_charger_rack", "heavy_rifle_rack"],
        mount="wall", tags=["security"], solid=False, mount_y=1.3)
def weaponrack_wall(m, i, label, rng):
    if i == 0:  # three rifles on a backing board
        m.box((1.3, 1.0, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
        m.box((1.34, 0.06, 0.06), (0, 0.5, 0.03), "hazard_yellow", 0.005)
        m.box((0.4, 0.05, 0.02), (0.4, 0.5, 0.07), "em_green")
        for k in range(3):
            y = -0.36 + k * 0.3
            for x in (-0.4, 0.4):
                m.box((0.06, 0.05, 0.06), (x, y - 0.02, 0.07), "steel", 0.005)
                m.box((0.06, 0.03, 0.03), (x, y + 0.01, 0.09), "steel", 0.005)
            blaster(m, (-0.45, y, 0.1), "rifle", cell=["em_cyan", "em_green", "em_orange"][k])
        bolts(m, [(-0.6, 0.4), (0.6, 0.4), (-0.6, -0.45), (0.6, -0.45)], 0.043)
    elif i == 1:  # pistol pegboard
        m.box((0.95, 0.65, 0.03), (0, 0, 0.015), "hull_mid", 0.01)
        for r in range(2):
            y = 0.12 - r * 0.28
            m.box((0.9, 0.04, 0.05), (0, y - 0.09, 0.05), "black_metal", 0.005)
            for c in range(3):
                x = -0.3 + c * 0.3
                for dx in (-0.06, 0.08):
                    m.cyl(0.012, 0.05, (x + dx, y, 0.055), "steel", axis="z", seg=6)
                blaster(m, (x - 0.12, y - 0.07, 0.07), "pistol", cell=["em_cyan", "em_amber", "em_red"][c])
        m.box((0.95, 0.08, 0.04), (0, 0.36, 0.04), "paint_red", 0.005)
    elif i == 2:  # riot shields
        m.box((1.5, 0.1, 0.05), (0, 0.5, 0.025), "steel", 0.005)
        m.box((1.5, 0.1, 0.05), (0, -0.5, 0.025), "steel", 0.005)
        for k in range(3):
            x = -0.5 + k * 0.5
            z = 0.1 + (k % 2) * 0.03
            m.box((0.42, 0.95, 0.03), (x, 0, z), "paint_navy", 0.01)
            m.box((0.34, 0.6, 0.015), (x, 0.1, z + 0.02), "glass_blue")
            m.box((0.34, 0.06, 0.02), (x, -0.32, z + 0.02), "hazard_yellow")
            m.box((0.05, 0.16, 0.05), (x, -0.1, z - 0.04), "black_metal", 0.005)
            m.box((0.03, 0.04, z), (x, 0.42, z / 2), "steel")
            m.box((0.03, 0.04, z), (x, -0.42, z / 2), "steel")
    elif i == 3:  # target panel
        m.box((1.3, 1.1, 0.05), (0, 0, 0.025), "hull_dark", 0.012)
        for k, x in enumerate((-0.3, 0.3)):
            for r, mat in enumerate(("paint_white", "paint_red", "paint_white", "em_red")):
                m.cyl(0.26 - r * 0.06, 0.006, (x, 0.12, 0.052 + r * 0.004), mat, axis="z", seg=14)
            for _ in range(3):
                m.cyl(0.012, 0.004, (x + rng.uniform(-0.12, 0.12), 0.12 + rng.uniform(-0.12, 0.12), 0.075), "plastic_black", axis="z", seg=6)
        m.box((1.1, 0.1, 0.02), (0, -0.4, 0.06), "black_metal")
        m.screen((0.5, 0.08), (0.2, -0.4, 0.072), "bars")
        for x in (-0.55, 0.55):
            m.box((0.05, 1.1, 0.07), (x, 0, 0.04), "hazard_yellow", 0.005)
        m.box((0.16, 0.16, 0.06), (-0.4, -0.4, 0.07), "paint_orange", 0.005)
    elif i == 4:  # energy cell charging rack
        m.box((1.2, 0.8, 0.12), (0, 0, 0.06), "hull_dark", 0.015)
        for r in range(2):
            for c in range(6):
                x = -0.5 + c * 0.2
                y = 0.15 - r * 0.32
                m.box((0.13, 0.24, 0.05), (x, y, 0.13), "black_metal", 0.005)
                lv = rng.choice([0.5, 0.8, 1.0])
                m.cyl(0.04, 0.2 * lv, (x, y - 0.1 * (1 - lv), 0.17), rng.choice(["em_cyan", "em_green"]), axis="y", seg=10)
                m.box((0.11, 0.02, 0.01), (x, y + 0.125, 0.16), rng.choice(["em_green", "em_amber"]))
        m.box((1.2, 0.05, 0.14), (0, -0.42, 0.07), "hazard_yellow")
        m.box((0.3, 0.05, 0.02), (0, 0.42, 0.13), "em_cyan")
    else:  # heavy rifle rack vertical
        m.box((1.2, 1.2, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
        m.box((1.16, 0.12, 0.1), (0, 0.58, 0.07), "steel", 0.008)
        m.box((1.16, 0.12, 0.1), (0, -0.4, 0.07), "steel", 0.008)
        for k in range(4):
            x = -0.42 + k * 0.28
            m.box((0.1, 0.03, 0.04), (x, 0.58, 0.14), "black_metal")
            blaster(m, (x, -0.55, 0.12), "heavy", vert=True, cell=["em_orange", "em_red", "em_amber", "em_cyan"][k])
        m.box((0.8, 0.05, 0.03), (0, 0.63, 0.06), "em_red")


@family("weaponrack", ["rifle_locker", "pistol_locker", "gun_safe", "weapons_inspection_bench",
                       "armour_plate_locker", "canister_cabinet", "gun_cleaning_station", "energy_charger_tower"],
        mount="floor", tags=["security"], solid=True)
def weaponrack_floor(m, i, label, rng):
    if i == 0:
        w, h, d = 1.0, 2.0, 0.5
        locker_shell(m, w, h, d, "paint_grey", "hull_dark", "glass_dark")
        for k in range(4):
            x = -0.33 + k * 0.22
            blaster(m, (x, 0.2, -0.1), "rifle", vert=True, cell=["em_cyan", "em_green"][k % 2])
        m.box((w, 0.06, 0.02), (0, h - 0.03, d / 2 + 0.02), "paint_red")
        m.box((0.16, 0.05, 0.03), (0.3, 1.0, d / 2 + 0.03), "em_red")
        m.box((0.16, 0.12, 0.03), (-0.3, 1.0, d / 2 + 0.03), "black_metal")
    elif i == 1:
        w, h, d = 0.8, 1.4, 0.36
        locker_shell(m, w, h, d, "hull_mid", "hull_dark", "glass")
        for k in range(3):
            y = 0.35 + k * 0.38
            m.box((w - 0.08, 0.02, d - 0.08), (0, y, 0), "steel")
            for c in range(3):
                blaster(m, (-0.3 + c * 0.2, y + 0.01, 0), "pistol", cell=["em_cyan", "em_amber", "em_red"][c])
        m.box((0.1, 0.1, 0.03), (0.28, 0.75, d / 2 + 0.03), "black_metal")
        m.box((0.05, 0.05, 0.01), (0.28, 0.78, d / 2 + 0.05), "em_green")
    elif i == 2:  # gun safe
        w, h, d = 0.8, 1.5, 0.65
        m.box((w, h - 0.06, d), (0, 0.06 + (h - 0.06) / 2, 0), "gunmetal", 0.02)
        for x in (-0.3, 0.3):
            m.box((0.12, 0.06, 0.12), (x, 0.03, 0.2), "black_metal")
            m.box((0.12, 0.06, 0.12), (x, 0.03, -0.2), "black_metal")
        m.box((w - 0.1, h - 0.2, 0.03), (0, 0.8, d / 2 + 0.01), "steel", 0.01)
        m.box((0.03, 0.06, 0.06), (-w / 2 + 0.03, 1.4, d / 2 + 0.01), "black_metal")
        m.box((0.03, 0.06, 0.06), (-w / 2 + 0.03, 0.2, d / 2 + 0.01), "black_metal")
        m.cyl(0.09, 0.04, (0.05, 0.85, d / 2 + 0.03), "chrome", axis="z", seg=20)
        m.torus(0.12, 0.014, (0.05, 0.85, d / 2 + 0.035), "black_metal", axis="z", seg=20, tseg=6)
        for k in range(3):
            m.link((0.05, 0.85, d / 2 + 0.05), (0.05 + 0.17 * math.cos(k * 2.09), 0.85 + 0.17 * math.sin(k * 2.09), d / 2 + 0.05), 0.012, "chrome", 6)
        m.box((0.16, 0.22, 0.03), (0.25, 1.2, d / 2 + 0.03), "black_metal", 0.004)
        m.screen((0.1, 0.05), (0.25, 1.26, d / 2 + 0.048), "power")
        for r in range(3):
            for c in range(3):
                m.box((0.03, 0.03, 0.01), (0.2 + c * 0.05, 1.17 - r * 0.04, d / 2 + 0.048), "plastic_grey")
    elif i == 3:  # inspection bench
        m.box((1.9, 0.06, 0.8), (0, 0.9, 0), "steel", 0.008)
        m.box((1.9, 0.02, 0.8), (0, 0.94, 0), "sec_mat")
        for x in (-0.85, 0.85):
            for z in (-0.33, 0.33):
                m.box((0.06, 0.87, 0.06), (x, 0.435, z), "hull_dark")
        m.box((1.8, 0.05, 0.7), (0, 0.25, 0), "hull_dark")
        m.box((0.5, 0.5, 0.6), (0.6, 0.5, 0), "hull_mid", 0.01)
        blaster(m, (-0.8, 0.95, 0.15), "rifle", cell="em_amber")
        m.box((0.2, 0.05, 0.05), (-0.1, 0.975, -0.15), "chrome", 0.005)
        m.box((0.12, 0.05, 0.08), (-0.35, 0.975, -0.15), "black_metal")
        m.box((0.4, 0.3, 0.04), (0.6, 1.05, -0.36), "hull_dark", 0.005)
        m.screen((0.34, 0.24), (0.6, 1.07, -0.335), "diagnostic")
        m.link((-0.7, 0.95, -0.35), (-0.7, 1.55, -0.35), 0.02, "steel", 6)
        m.link((-0.7, 1.55, -0.35), (-0.3, 1.7, -0.1), 0.018, "steel", 6)
        m.cyl(0.08, 0.06, (-0.3, 1.66, -0.1), "hull_dark", seg=12, r2=0.11)
        m.cyl(0.07, 0.01, (-0.3, 1.63, -0.1), "em_white", seg=12)
        m.box((0.1, 0.12, 0.14), (0.9, 0.98, 0.2), "steel", 0.01)
    elif i == 4:  # armour plate locker (open front)
        w, h, d = 1.0, 2.0, 0.6
        locker_shell(m, w, h, d, "paint_navy", "hull_dark", "glass_dark", front=False)
        for k in range(4):
            y = 0.35 + k * 0.4
            m.box((w - 0.08, 0.02, d - 0.06), (0, y, 0.0), "steel")
            m.box((0.5, 0.3, 0.06), (0, y + 0.16, -0.05), "hull_mid", 0.02)
            m.box((0.5, 0.05, 0.062), (0, y + 0.22, -0.05), "hazard_yellow")
            m.box((0.3, 0.02, 0.2), (-0.32 + (k % 2) * 0.64, y + 0.02, 0.1), "carbon", 0.006)
        m.box((w, 0.06, 0.02), (0, h - 0.09, d / 2), "paint_gold")
    elif i == 5:  # canister cabinet
        w, h, d = 1.0, 1.4, 0.5
        locker_shell(m, w, h, d, "paint_orange", "hull_dark", "glass", front=True)
        for k in range(3):
            y = 0.35 + k * 0.38
            m.box((w - 0.08, 0.02, d - 0.08), (0, y, 0), "steel")
            for c in range(5):
                x = -0.36 + c * 0.18
                m.cyl(0.055, 0.22, (x, y + 0.12, 0), rng.choice(["paint_green", "paint_red", "hazard_yellow"]), seg=10)
                m.cyl(0.02, 0.05, (x, y + 0.245, 0), "chrome", seg=6)
        m.box((w, 0.08, 0.02), (0, h - 0.06, d / 2 + 0.02), "hazard_yellow")
        m.box((0.1, 0.1, 0.02), (0, h - 0.06, d / 2 + 0.035), "black_metal")
    elif i == 6:  # cleaning station
        m.box((1.6, 0.06, 0.7), (0, 0.9, 0), "steel", 0.008)
        m.box((1.5, 0.86, 0.66), (0, 0.43, 0), "hull_mid", 0.01)
        m.box((0.5, 0.1, 0.45), (-0.4, 0.92, 0.02), "hull_dark")
        m.box((0.44, 0.01, 0.39), (-0.4, 0.98, 0.02), "water")
        m.box((1.5, 0.9, 0.08), (0, 1.35, -0.31), "hull_dark", 0.01)
        for k in range(5):
            m.cyl(0.03, 0.4, (0.05 + k * 0.1, 1.3, -0.24), "plastic_grey", seg=8)
            m.cyl(0.012, 0.15, (0.05 + k * 0.1, 1.55, -0.24), "brass", seg=6)
        m.box((0.6, 0.35, 0.3), (-0.4, 1.7, -0.2), "hull_mid", 0.02)
        m.box((0.5, 0.02, 0.2), (-0.4, 1.52, -0.18), "em_white")
        blaster(m, (0.1, 0.93, 0.15), "carbine", cell="em_green")
        for x in (0.45, 0.6):
            m.cyl(0.04, 0.1, (x, 0.98, 0.2), "paint_blue", seg=8)
        m.screen((0.3, 0.2), (0.6, 1.4, -0.265), "diagnostic")
    else:  # energy charger tower
        m.cyl(0.32, 0.12, (0, 0.06, 0), "black_metal", seg=6)
        m.cyl(0.22, 1.6, (0, 0.92, 0), "hull_mid", seg=6)
        for k in range(3):
            y = 0.4 + k * 0.45
            m.cyl(0.235, 0.06, (0, y, 0), "hull_dark", seg=6)
            for c in range(6):
                a = c * PI / 3 + PI / 6
                x, z = 0.2 * math.cos(a), 0.2 * math.sin(a)
                m.cyl(0.04, 0.2, (x * 1.15, y + 0.13, z * 1.15), rng.choice(["em_cyan", "em_green", "em_amber"]), seg=8)
        m.cyl(0.24, 0.1, (0, 1.78, 0), "steel", seg=6, r2=0.16)
        m.cyl(0.05, 0.04, (0, 1.85, 0), "em_cyan", seg=8)
        m.box((0.3, 0.12, 0.03), (0, 0.24, 0.2), "hazard_yellow")


# ================================================================= BRIG CELLS
@family("cell", ["door_bars", "door_forcefield", "wall_cot_toilet", "observation_window", "interrogation_table",
                 "holding_bench", "control_desk", "restraint_chair", "property_locker", "contraband_xray_table"],
        mount="floor", tags=["security"], solid=True)
def cell_module(m, i, label, rng):
    if i == 0:  # barred door
        W, H = 1.2, 2.3
        for x in (-W / 2 - 0.06, W / 2 + 0.06):
            m.box((0.12, H + 0.1, 0.2), (x, (H + 0.1) / 2, 0), "hull_dark", 0.01)
        m.box((W + 0.24, 0.12, 0.2), (0, H + 0.06, 0), "hull_dark", 0.01)
        m.box((W, 0.1, 0.1), (0, 0.05, 0), "steel")
        for k in range(11):
            m.cyl(0.014, H - 0.1, (-W / 2 + 0.06 + k * (W - 0.12) / 10, H / 2 + 0.04, 0.02), "steel", seg=6)
        for y in (0.15, 1.1, H - 0.1):
            m.box((W, 0.05, 0.06), (0, y, 0.04), "gunmetal", 0.005)
        m.box((0.16, 0.3, 0.1), (W / 2 - 0.12, 1.05, 0.08), "black_metal", 0.01)
        m.box((0.04, 0.04, 0.02), (W / 2 - 0.12, 1.15, 0.14), "em_red")
        m.box((0.4, 0.06, 0.06), (0, H + 0.03, 0.12), "em_red")
        for y in (0.4, 1.8):
            m.cyl(0.03, 0.14, (-W / 2, y, 0.03), "black_metal", seg=8)
    elif i == 1:  # forcefield door
        W, H = 1.3, 2.3
        for x in (-W / 2 - 0.1, W / 2 + 0.1):
            m.box((0.2, H + 0.2, 0.24), (x, (H + 0.2) / 2, 0), "hull_dark", 0.015)
            m.box((0.06, H - 0.4, 0.05), (x, H / 2, 0.14), "em_blue")
            m.box((0.1, 0.24, 0.3), (x, H - 0.1, 0), "gunmetal", 0.01)
            m.box((0.1, 0.24, 0.3), (x, 0.15, 0), "gunmetal", 0.01)
        m.box((W + 0.4, 0.2, 0.24), (0, H + 0.2, 0), "hull_dark", 0.015)
        m.box((W, 0.06, 0.16), (0, 0.03, 0), "steel")
        m.box((W, 0.05, 0.08), (0, H, 0), "black_metal")
        field(m, W, H - 0.05, (0, H / 2, 0))
        m.box((0.16, 0.2, 0.06), (W / 2 + 0.3, 1.2, 0.05), "black_metal", 0.01)
        m.screen((0.1, 0.1), (W / 2 + 0.3, 1.22, 0.085), "alert")
    elif i == 2:  # cell wall with cot + toilet
        m.box((3.0, 2.6, 0.15), (0, 1.3, -0.5), "hull_light", 0.01)
        m.box((3.0, 0.2, 0.17), (0, 0.1, -0.5), "hull_dark")
        for x in (-1.0, 1.0):
            m.box((0.02, 2.4, 0.01), (x, 1.3, -0.415), "hull_dark")
        m.box((0.85, 0.05, 1.9), (-0.7, 0.55, 0.4), "steel", 0.01)
        m.box((0.8, 0.09, 1.85), (-0.7, 0.62, 0.4), "fabric_grey", 0.03)
        m.box((0.3, 0.06, 0.4), (-0.7, 0.7, -0.3), "foam", 0.02)
        for x in (-1.08, -0.32):
            m.link((x, 1.3, -0.42), (x, 0.57, 1.3), 0.012, "steel", 6)
            m.link((x, 1.3, -0.42), (x, 0.57, -0.4), 0.012, "steel", 6)
        m.box((0.4, 0.3, 0.2), (0.9, 0.5, -0.28), "brushed_alu", 0.02)
        m.cyl(0.19, 0.18, (0.9, 0.35, -0.05), "brushed_alu", seg=14, r2=0.22)
        m.cyl(0.17, 0.02, (0.9, 0.45, -0.05), "water", seg=14)
        m.box((0.36, 0.06, 0.28), (0.9, 0.9, -0.34), "brushed_alu", 0.01)
        m.box((0.3, 0.1, 0.22), (0.9, 0.8, -0.32), "brushed_alu", 0.02)
        m.cyl(0.02, 0.05, (0.9, 0.98, -0.34), "chrome", seg=6)
        m.box((0.3, 0.22, 0.02), (0.9, 1.5, -0.41), "chrome")
        m.box((0.2, 0.05, 0.02), (0.0, 2.3, -0.41), "em_white")
    elif i == 3:  # observation window wall
        m.box((2.4, 0.9, 0.2), (0, 0.45, 0), "hull_light", 0.01)
        m.box((2.4, 0.7, 0.2), (0, 2.25, 0), "hull_light", 0.01)
        for x in (-1.1, 1.1):
            m.box((0.2, 1.1, 0.2), (x, 1.45, 0), "hull_light", 0.01)
        m.box((2.0, 1.0, 0.04), (0, 1.45, 0), "glass_blue")
        for x, w in ((-1.0, 0.06), (1.0, 0.06), (0, 0.04)):
            m.box((w, 1.06, 0.1), (x, 1.45, 0.0), "steel", 0.005)
        m.box((2.06, 0.06, 0.1), (0, 1.97, 0), "steel", 0.005)
        m.box((2.06, 0.06, 0.1), (0, 0.93, 0), "steel", 0.005)
        m.box((2.4, 0.1, 0.24), (0, 0.05, 0), "hull_dark")
        m.box((0.18, 0.18, 0.05), (-1.0, 0.7, 0.12), "black_metal", 0.005)
        for k in range(3):
            m.box((0.12, 0.01, 0.01), (-1.0, 0.66 + k * 0.04, 0.15), "steel")
        m.screen((0.3, 0.14), (0, 2.3, 0.105), "text", bezel=0.015)
        m.box((0.36, 0.06, 0.03), (1.0, 2.3, 0.11), "em_red")
        m.box((2.0, 0.04, 0.22), (0, 0.98, 0.1), "steel", 0.005)
    elif i == 4:  # interrogation table
        m.box((1.6, 0.06, 0.8), (0, 0.76, 0), "steel", 0.01)
        m.box((1.5, 0.02, 0.7), (0, 0.8, 0), "hull_dark")
        m.box((0.5, 0.7, 0.5), (0, 0.38, 0), "hull_dark", 0.01)
        m.box((0.8, 0.04, 0.7), (0, 0.02, 0), "steel")
        m.torus(0.05, 0.01, (0.4, 0.84, 0.0), "steel", axis="x", seg=12, tseg=6)
        m.box((0.06, 0.06, 0.06), (0.4, 0.82, 0), "steel")
        for z in (-1, 1):
            zz = z * 0.85
            m.cyl(0.2, 0.05, (0, 0.03, zz), "steel", seg=12)
            m.cyl(0.05, 0.42, (0, 0.24, zz), "hull_dark", seg=8)
            m.box((0.44, 0.06, 0.42), (0, 0.48, zz), "leather_black", 0.02)
            m.box((0.44, 0.5, 0.06), (0, 0.76, zz + z * 0.2), "leather_black", 0.02)
        m.box((0.3, 0.04, 0.3), (0.3, 0.83, -0.2), "plastic_black", 0.005)
        m.box((0.05, 0.03, 0.05), (0.3, 0.86, -0.2), "em_red")
    elif i == 5:  # holding bench
        m.box((2.0, 0.08, 0.5), (0, 0.46, 0), "steel", 0.015)
        m.box((2.0, 0.6, 0.06), (0, 0.9, -0.28), "hull_mid", 0.01)
        for x in (-0.9, 0.9):
            m.box((0.1, 0.42, 0.44), (x, 0.21, 0), "hull_dark", 0.01)
        m.box((1.8, 0.05, 0.05), (0, 0.32, 0.15), "hull_dark")
        for x in (-0.7, 0.0, 0.7):
            m.torus(0.05, 0.01, (x, 0.85, -0.24), "steel", axis="z", seg=12, tseg=6)
            m.box((0.05, 0.03, 0.04), (x, 0.79, -0.25), "steel")
        m.box((2.0, 0.06, 0.08), (0, 1.22, -0.27), "hazard_yellow")
    elif i == 6:  # cell control desk
        m.box((1.9, 0.06, 0.8), (0, 0.76, 0), "hull_dark", 0.01)
        m.box((1.8, 0.72, 0.5), (0, 0.36, -0.1), "hull_mid", 0.01)
        m.box((1.8, 0.5, 0.06), (0, 1.12, -0.35), "hull_dark", 0.01)
        for k, x in enumerate((-0.6, 0.0, 0.6)):
            m.screen((0.5, 0.36), (x, 1.14, -0.315), "text", bezel=0.02)
        m.box((1.0, 0.03, 0.3), (-0.3, 0.8, 0.22), "black_metal", 0.005, rot=(-0.15, 0, 0))
        for r in range(2):
            for c in range(8):
                m.box((0.06, 0.02, 0.05), (-0.65 + c * 0.1, 0.83 + r * 0.01, 0.16 + r * 0.09), rng.choice(["em_green", "em_red", "em_amber", "plastic_grey"]))
        for k in range(4):
            m.box((0.05, 0.05, 0.05), (0.5 + k * 0.09, 0.82, 0.22), "black_metal")
            m.link((0.5 + k * 0.09, 0.84, 0.22), (0.5 + k * 0.09, 0.93, 0.25), 0.01, "chrome", 6)
        m.box((0.1, 0.12, 0.1), (0.85, 0.85, 0.1), "paint_red", 0.01)
        m.cyl(0.04, 0.03, (0.85, 0.93, 0.1), "paint_red", seg=10)
        m.box((1.85, 0.1, 0.72), (0, 0.05, 0), "black_metal")
    elif i == 7:  # restraint chair (empty)
        m.cyl(0.25, 0.05, (0, 0.025, 0), "steel", seg=14)
        m.cyl(0.07, 0.4, (0, 0.24, 0), "hull_dark", seg=10)
        m.box((0.5, 0.08, 0.5), (0, 0.48, 0.05), "black_metal", 0.02)
        m.box((0.44, 0.06, 0.44), (0, 0.54, 0.05), "leather_black", 0.02)
        m.box((0.5, 0.9, 0.08), (0, 1.0, -0.22), "black_metal", 0.02)
        m.box((0.44, 0.8, 0.05), (0, 1.0, -0.17), "leather_black", 0.02)
        m.box((0.3, 0.2, 0.1), (0, 1.55, -0.2), "black_metal", 0.02)
        for s in (-1, 1):
            m.box((0.08, 0.06, 0.5), (s * 0.31, 0.78, 0.0), "black_metal", 0.01)
            m.box((0.1, 0.08, 0.14), (s * 0.31, 0.83, 0.1), "steel", 0.01)
            m.torus(0.06, 0.012, (s * 0.31, 0.86, 0.1), "steel", axis="x", seg=12, tseg=6)
            m.box((0.1, 0.06, 0.14), (s * 0.2, 0.3, 0.3), "steel", 0.01)
            m.torus(0.06, 0.012, (s * 0.2, 0.36, 0.3), "steel", axis="z", seg=12, tseg=6)
            m.box((0.04, 0.7, 0.03), (s * 0.15, 0.95, -0.17), "fabric_grey")
            m.box((0.04, 0.03, 0.4), (s * 0.15, 0.6, 0.0), "fabric_grey")
    elif i == 8:  # property locker
        w, h, d = 0.9, 1.9, 0.5
        m.box((w, h, d), (0, h / 2, 0), "paint_grey", 0.012)
        m.box((w + 0.02, 0.06, d + 0.02), (0, 0.03, 0), "black_metal")
        m.box((w - 0.1, 0.9, 0.02), (0, 1.35, d / 2 + 0.005), "hull_mid", 0.005)
        for k in range(6):
            m.box((0.5, 0.012, 0.01), (0, 1.5 + k * 0.05, d / 2 + 0.02), "black_metal")
        m.box((w - 0.1, 0.4, 0.18), (0, 0.5, d / 2 + 0.02), "hull_mid", 0.01)
        m.box((0.4, 0.05, 0.05), (0, 0.6, d / 2 + 0.13), "steel", 0.008)
        m.box((0.1, 0.06, 0.02), (0.2, 0.42, d / 2 + 0.115), "paint_white")
        m.box((0.16, 0.1, 0.03), (0.25, 1.0, d / 2 + 0.02), "black_metal")
        m.box((0.05, 0.05, 0.01), (0.25, 1.02, d / 2 + 0.04), "em_red")
        m.box((0.2, 0.1, 0.01), (-0.2, 1.85, d / 2 + 0.006), "paint_white")
    else:  # contraband x-ray table
        m.box((1.8, 0.1, 0.8), (0, 0.5, 0), "hull_dark", 0.01)
        m.box((1.7, 0.4, 0.7), (0, 0.25, 0), "hull_mid", 0.01)
        m.box((1.9, 0.03, 0.5), (0, 0.57, 0.0), "rubber")
        m.box((0.9, 0.7, 0.9), (0.0, 0.94, 0), "hull_mid", 0.03)
        for z in (0.45, -0.45):
            m.box((0.7, 0.5, 0.02), (0, 0.9, z), "black_metal")
        m.box((0.92, 0.06, 0.92), (0, 1.3, 0), "hazard_yellow", 0.01)
        m.box((0.2, 0.06, 0.06), (0.3, 1.36, 0.38), "em_amber")
        m.link((0.7, 0.6, -0.3), (0.7, 1.25, -0.3), 0.02, "steel", 6)
        m.box((0.5, 0.4, 0.05), (0.75, 1.4, -0.3), "hull_dark", 0.01, rot=(0.2, 0, 0))
        m.screen((0.44, 0.32), (0.75, 1.4, -0.27), "diagnostic", rot=(0.2, 0, 0))
        for x in (-0.9, 0.9):
            m.box((0.06, 0.1, 0.4), (x, 0.62, 0), "steel", 0.005)


# ================================================================= SURVEILLANCE
@family("camera", ["wall_bracket", "motion_sensor", "retina_scanner", "palm_scanner", "card_reader"],
        mount="wall", tags=["security"], solid=False, mount_y=1.5)
def camera_wall(m, i, label, rng):
    if i == 0:  # bracket camera, mounted high
        m.box((0.14, 0.18, 0.02), (0, 0, 0.01), "hull_dark", 0.004)
        m.box((0.05, 0.05, 0.16), (0, 0, 0.09), "steel", 0.005)
        m.sphere(0.04, (0, 0, 0.18), "black_metal", 10, 6)
        m.box((0.13, 0.11, 0.34), (0, -0.04, 0.32), "plastic_white", 0.02, rot=(0.25, 0, 0))
        m.box((0.15, 0.02, 0.36), (0, 0.03, 0.34), "plastic_white", 0.005, rot=(0.25, 0, 0))
        m.cyl(0.048, 0.06, (0, -0.1, 0.5), "black_metal", axis="z", seg=12, r2=0.055)
        m.cyl(0.036, 0.01, (0, -0.1, 0.535), "glass_dark", axis="z", seg=12)
        m.box((0.02, 0.02, 0.01), (0.04, -0.03, 0.5), "em_red")
        m.link((0, 0.05, 0.1), (0, 0.1, 0.02), 0.008, "rubber", 5)
    elif i == 1:  # PIR motion sensor
        m.box((0.16, 0.16, 0.03), (0, 0, 0.015), "plastic_white", 0.006)
        m.box((0.13, 0.13, 0.04), (0, 0, 0.05), "plastic_white", 0.01)
        m.sphere(0.055, (0, -0.01, 0.075), "glass_amber", 12, 6, scale=(1, 1, 0.7))
        for k in range(6):
            a = k * PI / 3
        m.box((0.02, 0.012, 0.008), (0.05, 0.06, 0.075), "em_green")
        m.box((0.04, 0.012, 0.008), (-0.05, 0.06, 0.075), "plastic_black")
    elif i == 2:  # retina scanner
        m.box((0.24, 0.38, 0.05), (0, 0, 0.025), "hull_dark", 0.012)
        m.box((0.2, 0.3, 0.02), (0, 0, 0.06), "black_metal", 0.008)
        m.cyl(0.075, 0.015, (0, 0.05, 0.075), "gunmetal", axis="z", seg=20)
        m.torus(0.065, 0.007, (0, 0.05, 0.085), "em_cyan", axis="z", seg=20, tseg=6)
        m.cyl(0.035, 0.012, (0, 0.05, 0.088), "glass_dark", axis="z", seg=14)
        m.cyl(0.012, 0.014, (0, 0.05, 0.092), "em_cyan", axis="z", seg=8)
        m.screen((0.14, 0.08), (0, -0.08, 0.072), "vitals")
        m.box((0.14, 0.02, 0.01), (0, -0.16, 0.07), "em_green")
    elif i == 3:  # palm scanner
        m.box((0.3, 0.4, 0.04), (0, 0, 0.02), "hull_mid", 0.01)
        m.box((0.26, 0.26, 0.08), (0, -0.04, 0.06), "black_metal", 0.01, rot=(-0.35, 0, 0))
        m.box((0.22, 0.22, 0.02), (0, -0.04, 0.11), "glass_blue", rot=(-0.35, 0, 0))
        m.box((0.13, 0.11, 0.008), (0, -0.07, 0.118), "em_green", rot=(-0.35, 0, 0))
        for k in range(4):
            m.box((0.022, 0.09, 0.008), (-0.06 + k * 0.04, 0.03, 0.115), "em_green", rot=(-0.35, 0, 0))
        m.box((0.05, 0.1, 0.008), (0.085, -0.07, 0.118), "em_green", rot=(-0.35, 0, 0.6))
        m.box((0.26, 0.04, 0.02), (0, 0.16, 0.05), "plastic_black")
        m.box((0.08, 0.02, 0.008), (0, 0.16, 0.062), "em_cyan")
    else:  # card reader
        m.box((0.11, 0.2, 0.035), (0, 0, 0.0175), "plastic_black", 0.008)
        m.box((0.09, 0.05, 0.02), (0, 0.06, 0.04), "plastic_grey", 0.004)
        m.box((0.06, 0.008, 0.012), (0, 0.06, 0.052), "black_metal")
        m.box((0.05, 0.012, 0.008), (0, 0.095, 0.042), "em_red")
        for r in range(3):
            for c in range(3):
                m.box((0.016, 0.012, 0.008), (-0.024 + c * 0.024, 0.0 - r * 0.02, 0.04), "plastic_grey")
        m.box((0.05, 0.02, 0.008), (0, -0.075, 0.04), "em_green")


@family("camera", ["dome_ceiling", "pan_tilt_ceiling", "cluster_ceiling", "sentry_sensor_pod"],
        mount="ceiling", tags=["security"], solid=False)
def camera_ceiling(m, i, label, rng):
    if i == 0:  # dome
        m.cyl(0.16, 0.03, (0, -0.015, 0), "plastic_white", seg=20, bevel=0.004)
        m.sphere(0.13, (0, -0.04, 0), "glass_dark", 20, 10, scale=(1, 0.85, 1))
        m.box((0.05, 0.05, 0.08), (0, -0.09, 0.02), "black_metal", 0.005)
        m.cyl(0.02, 0.03, (0, -0.1, 0.07), "black_metal", axis="z", seg=8)
        m.cyl(0.012, 0.01, (0, -0.1, 0.09), "glass", axis="z", seg=8)
        m.box((0.012, 0.012, 0.01), (0.05, -0.02, 0.15), "em_red")
    elif i == 1:  # pan-tilt
        m.cyl(0.11, 0.03, (0, -0.015, 0), "hull_dark", seg=16)
        m.cyl(0.05, 0.12, (0, -0.09, 0), "steel", seg=12)
        m.cyl(0.09, 0.06, (0, -0.18, 0), "black_metal", seg=14)
        for s in (-1, 1):
            m.box((0.03, 0.2, 0.1), (s * 0.11, -0.28, 0), "plastic_grey", 0.008)
        m.cyl(0.12, 0.2, (0, -0.32, 0.02), "plastic_white", axis="z", seg=14, bevel=0.008)
        m.cyl(0.13, 0.03, (0, -0.32, 0.16), "black_metal", axis="z", seg=14)
        m.cyl(0.075, 0.03, (0, -0.32, 0.175), "glass_dark", axis="z", seg=14)
        m.cyl(0.02, 0.01, (0, -0.32, 0.195), "em_cyan", axis="z", seg=8)
        m.box((0.02, 0.02, 0.02), (0, -0.22, 0.13), "em_red")
    elif i == 2:  # four-way cluster
        m.cyl(0.12, 0.03, (0, -0.015, 0), "hull_dark", seg=16)
        m.cyl(0.06, 0.1, (0, -0.08, 0), "steel", seg=10)
        m.box((0.18, 0.1, 0.18), (0, -0.15, 0), "plastic_grey", 0.015)
        for k in range(4):
            a = k * PI / 2
            dx, dz = math.sin(a), math.cos(a)
            m.cyl(0.055, 0.14, (dx * 0.16, -0.19, dz * 0.16), "plastic_white", axis="z" if dz else "x", seg=10)
            m.cyl(0.058, 0.02, (dx * 0.235, -0.19, dz * 0.235), "black_metal", axis="z" if dz else "x", seg=10)
            m.cyl(0.035, 0.014, (dx * 0.245, -0.19, dz * 0.245), "glass_dark", axis="z" if dz else "x", seg=10)
            m.box((0.02, 0.02, 0.02) if dz else (0.02, 0.02, 0.02), (dx * 0.15, -0.135, dz * 0.15), "em_red" if k == 0 else "em_green")
        m.cyl(0.03, 0.05, (0, -0.24, 0), "black_metal", seg=8)
    else:  # sentry sensor pod (no turret)
        m.cyl(0.05, 0.6, (0, -0.3, 0), "steel", seg=8)
        m.cyl(0.14, 0.03, (0, -0.015, 0), "hull_dark", seg=12)
        m.sphere(0.22, (0, -0.72, 0), "hull_light", 18, 10)
        m.torus(0.22, 0.02, (0, -0.72, 0), "black_metal", axis="y", seg=20, tseg=6)
        for k in range(4):
            a = k * PI / 2 + PI / 4
            m.sphere(0.055, (0.19 * math.cos(a), -0.72, 0.19 * math.sin(a)), "glass_dark", 8, 5)
            m.sphere(0.02, (0.24 * math.cos(a), -0.72, 0.24 * math.sin(a)), "em_cyan", 6, 4)
        m.cyl(0.07, 0.05, (0, -0.95, 0), "black_metal", seg=10, r2=0.04)
        m.sphere(0.03, (0, -0.98, 0), "em_amber", 8, 5)
        m.torus(0.23, 0.008, (0, -0.72, 0), "em_amber", axis="y", seg=16, tseg=4, rot=(0.5, 0, 0))


@family("camera", ["metal_detector_arch"], mount="floor", tags=["security"], solid=False)
def camera_arch(m, i, label, rng):
    for s in (-1, 1):
        m.box((0.2, 1.92, 0.5), (s * 0.5, 0.96 + 0.04, 0), "hull_light", 0.02)
        m.box((0.04, 1.6, 0.4), (s * 0.4, 1.0, 0), "hull_dark")
        for k in range(6):
            m.box((0.03, 0.06, 0.3), (s * 0.39, 0.3 + k * 0.27, 0), rng.choice(["em_green", "em_green", "em_amber"]))
        m.box((0.24, 0.06, 0.56), (s * 0.5, 0.03, 0), "black_metal", 0.01)
    m.box((1.2, 0.16, 0.5), (0, 1.92, 0), "hull_light", 0.02)
    m.box((0.5, 0.1, 0.02), (0, 1.92, 0.26), "black_metal")
    m.screen((0.4, 0.08), (0, 1.92, 0.27), "alert")
    m.box((0.5, 0.04, 0.4), (0, 0.02, 0), "rubber")
    m.cyl(0.05, 0.06, (0.35, 2.03, 0), "em_amber", seg=10)


# ================================================================= FORCEFIELDS
@family("forcefield", ["emitter_pair", "containment_projector", "shield_doorway", "blast_shutter",
                       "barrier_bollards", "hangar_field_arch"],
        mount="floor", tags=["security"], solid=False)
def forcefield_floor(m, i, label, rng):
    if i == 0:
        for s in (-1, 1):
            x = s * 1.2
            m.box((0.34, 0.08, 0.34), (x, 0.04, 0), "black_metal", 0.01)
            m.box((0.2, 2.1, 0.2), (x, 1.13, 0), "hull_dark", 0.02)
            m.box((0.24, 0.3, 0.24), (x, 0.25, 0), "gunmetal", 0.015)
            m.box((0.24, 0.3, 0.24), (x, 2.05, 0), "gunmetal", 0.015)
            m.box((0.05, 1.5, 0.05), (x - s * 0.02, 1.15, 0.12), "em_cyan")
            for k in range(5):
                m.box((0.1, 0.04, 0.05), (x - s * 0.13, 0.5 + k * 0.35, 0), "em_blue")
        field(m, 2.2, 1.9, (0, 1.15, 0))
    elif i == 1:  # cylindrical containment
        m.cyl(0.75, 0.12, (0, 0.06, 0), "hull_dark", seg=16, bevel=0.01)
        m.cyl(0.6, 0.06, (0, 0.15, 0), "gunmetal", seg=16)
        m.torus(0.62, 0.03, (0, 0.2, 0), "em_cyan", axis="y", seg=16, tseg=6)
        m.cyl(0.75, 0.12, (0, 2.34, 0), "hull_dark", seg=16, bevel=0.01)
        m.cyl(0.6, 0.06, (0, 2.25, 0), "gunmetal", seg=16)
        m.torus(0.62, 0.03, (0, 2.2, 0), "em_cyan", axis="y", seg=16, tseg=6)
        for k in range(4):
            a = k * PI / 2 + PI / 4
            m.cyl(0.05, 2.28, (0.7 * math.cos(a), 1.2, 0.7 * math.sin(a)), "steel", seg=8)
        m.cyl(0.6, 2.0, (0, 1.2, 0), "sec_field", seg=16, cap=False)
        m.cyl(0.05, 1.9, (0, 1.2, 0), "em_cyan", seg=8)
        m.box((0.26, 0.2, 0.1), (0, 0.16, 0.85), "hull_mid", 0.01)
        m.box((0.16, 0.08, 0.01), (0, 0.17, 0.905), "em_cyan")
    elif i == 2:  # doorway 2.0 x 2.6 opening
        W, H = 2.0, 2.6
        for s in (-1, 1):
            m.box((0.24, H + 0.2, 0.3), (s * (W / 2 + 0.12), (H + 0.2) / 2, 0), "hull_dark", 0.015)
            m.box((0.05, H - 0.2, 0.03), (s * (W / 2 - 0.01), H / 2, 0.14), "em_cyan")
            m.box((0.05, H - 0.2, 0.03), (s * (W / 2 - 0.01), H / 2, -0.14), "em_cyan")
            m.box((0.03, H - 0.3, 0.08), (s * (W / 2 + 0.11), H / 2, 0.16), "hazard_yellow")
        m.box((W + 0.48, 0.2, 0.3), (0, H + 0.1, 0), "hull_dark", 0.015)
        m.box((W, 0.05, 0.03), (0, H - 0.05, 0.14), "em_cyan")
        m.box((W, 0.05, 0.03), (0, H - 0.05, -0.14), "em_cyan")
        m.box((W, 0.04, 0.3), (0, 0.02, 0), "steel")
        field(m, W, H - 0.1, (0, H / 2 + 0.02, 0))
        m.box((0.4, 0.08, 0.04), (0, H + 0.1, 0.17), "black_metal")
        m.box((0.3, 0.04, 0.02), (0, H + 0.1, 0.2), "em_green")
    elif i == 3:  # blast shutter (static, closed)
        W, H = 2.2, 2.8
        for s in (-1, 1):
            m.box((0.3, H, 0.4), (s * (W / 2 + 0.15), H / 2, 0), "hull_dark", 0.02)
            m.box((0.06, H - 0.4, 0.06), (s * (W / 2 + 0.05), H / 2, 0.22), "hazard_yellow")
        m.box((W + 0.6, 0.5, 0.45), (0, H + 0.05, 0), "gunmetal", 0.02)
        m.cyl(0.14, W, (0, H + 0.05, 0.25), "steel", axis="x", seg=14)
        for k in range(14):
            y = 0.12 + k * 0.19
            m.box((W, 0.17, 0.12), (0, y, 0), "hull_mid" if k % 2 else "hull_light", 0.012)
        for k in range(4):
            m.box((0.5, 0.17, 0.125), (-0.9 + k * 0.6, 0.12 + 6 * 0.19, 0.0), "hazard_yellow") if k % 2 == 0 else None
        m.box((W, 0.08, 0.2), (0, 0.04, 0), "black_metal")
        m.box((0.3, 0.08, 0.02), (0, H - 0.1, 0.07), "em_red")
    elif i == 4:  # energy bollards
        for s in (-1, 1):
            x = s * 0.8
            m.cyl(0.13, 0.05, (x, 0.025, 0), "black_metal", seg=12)
            m.cyl(0.09, 0.95, (x, 0.5, 0), "hull_mid", seg=12)
            m.cyl(0.11, 0.06, (x, 1.0, 0), "gunmetal", seg=12, r2=0.09)
            m.sphere(0.07, (x, 1.06, 0), "em_blue", 10, 6)
            m.torus(0.095, 0.012, (x, 0.3, 0), "em_cyan", axis="y", seg=12, tseg=4)
        for y in (0.4, 0.7, 0.98):
            m.box((1.5, 0.03, 0.03), (0, y, 0), "em_blue")
            m.box((1.5, 0.08, 0.005), (0, y, 0), "sec_field")
    else:  # hangar field arch
        R, W = 1.4, 2.8
        for s in (-1, 1):
            m.box((0.3, 2.3, 0.4), (s * (R + 0.15), 1.15, 0), "hull_dark", 0.02)
            m.box((0.06, 2.1, 0.03), (s * (R - 0.02), 1.15, 0.2), "em_cyan")
        m.torus(R + 0.15, 0.15, (0, 2.3, 0), "hull_dark", axis="z", seg=20, tseg=6, arc=PI)
        m.torus(R - 0.02, 0.02, (0, 2.3, 0.2), "em_cyan", axis="z", seg=20, tseg=4, arc=PI)
        m.box((W, 0.05, 0.4), (0, 0.025, 0), "steel")
        field(m, W - 0.1, 2.3, (0, 1.16, 0), lines=False)
        pts = [(-R + 0.02, 2.3)] + [(-R * math.cos(t * PI / 10) + 0.0, 2.3 + R * math.sin(t * PI / 10)) for t in range(1, 10)] + [(R - 0.02, 2.3)]
        m.prism(pts, 0.006, (0, 0, 0), "sec_field", plane="xy")


@family("forcefield", ["deflector_grid", "laser_grid_emitter"], mount="wall", tags=["security"], solid=False, mount_y=1.3)
def forcefield_wall(m, i, label, rng):
    if i == 0:
        m.box((1.6, 1.6, 0.06), (0, 0, 0.03), "hull_dark", 0.015)
        for r in range(5):
            for c in range(5 if r % 2 == 0 else 4):
                x = -0.5 + c * 0.248 + (0.124 if r % 2 else 0)
                y = 0.46 - r * 0.232
                m.cyl(0.085, 0.01, (x, y, 0.07), rng.choice(["em_cyan", "em_blue", "em_blue"]), axis="z", seg=6, rot=(0, 0, PI / 6))
        m.box((1.7, 0.06, 0.1), (0, 0.83, 0.05), "hazard_yellow", 0.005)
        m.box((1.7, 0.06, 0.1), (0, -0.83, 0.05), "hazard_yellow", 0.005)
    else:
        m.box((0.24, 1.7, 0.16), (-1.2, 0, 0.08), "hull_dark", 0.015)
        m.box((0.24, 1.7, 0.16), (1.2, 0, 0.08), "hull_dark", 0.015)
        for k in range(7):
            y = -0.72 + k * 0.24
            m.cyl(0.025, 0.05, (-1.08, y, 0.12), "chrome", axis="x", seg=8)
            m.box((0.05, 0.05, 0.04), (1.1, y, 0.12), "black_metal")
            m.box((0.02, 0.02, 0.02), (1.09, y, 0.14), "em_green")
            m.box((2.16, 0.008, 0.008), (0, y, 0.12), "em_red")
        m.box((0.16, 0.06, 0.02), (-1.2, 0.8, 0.17), "em_red")
        m.box((0.16, 0.06, 0.02), (1.2, 0.8, 0.17), "em_green")


# ================================================================= SAFETY
def trefoil(m, cx, cy, z, r, fg="sec_sign_black", h=0.006):
    """Radiation trefoil made from three annular sector prisms + hub."""
    for k in range(3):
        a0 = math.radians(90 + k * 120 - 30)
        pts = [(cx + 0.28 * r * math.cos(a0 + t * math.radians(60) / 5), cy + 0.28 * r * math.sin(a0 + t * math.radians(60) / 5)) for t in range(6)]
        pts += [(cx + r * math.cos(a0 + math.radians(60) - t * math.radians(60) / 5), cy + r * math.sin(a0 + math.radians(60) - t * math.radians(60) / 5)) for t in range(6)]
        m.prism(pts, h, (0, 0, z), fg, plane="xy")
    m.cyl(0.16 * r, h, (cx, cy, z + h / 2), fg, axis="z", seg=10)


@family("safety", ["fire_extinguisher", "first_aid_cabinet", "oxygen_mask_box", "defibrillator_station",
                   "eye_wash_station", "breach_repair_kit", "fire_blanket_box", "evac_route_map",
                   "radiation_shelter_panel"],
        mount="wall", tags=["safety"], solid=False, mount_y=1.1)
def safety_wall(m, i, label, rng):
    if i == 0:  # extinguisher on bracket with sign
        m.box((0.3, 0.3, 0.02), (0, 0.32, 0.01), "sec_sign_red", 0.004)
        m.box((0.16, 0.16, 0.008), (0, 0.32, 0.024), "paint_white")
        m.box((0.03, 0.12, 0.008), (0, 0.32, 0.03), "sec_sign_red")
        m.box((0.12, 0.03, 0.008), (0, 0.32, 0.03), "sec_sign_red")
        m.cyl(0.075, 0.46, (0, 0.0, 0.11), "paint_red", seg=16, bevel=0.003)
        m.sphere(0.075, (0, 0.23, 0.11), "paint_red", 16, 6, scale=(1, 0.5, 1))
        m.cyl(0.05, 0.08, (0, 0.28, 0.11), "black_metal", seg=10)
        m.box((0.13, 0.03, 0.1), (0.03, 0.34, 0.11), "black_metal", 0.005)
        m.tube([(0.05, 0.25, 0.14), (0.1, 0.1, 0.19), (0.09, -0.08, 0.18), (0.075, -0.15, 0.14)], 0.01, "rubber", 5)
        m.cyl(0.02, 0.005, (-0.04, 0.24, 0.185), "chrome", axis="z", seg=10)
        for y in (0.12, -0.1):
            m.box((0.19, 0.03, 0.03), (0, y, 0.11), "steel", 0.004)
        m.box((0.16, 0.05, 0.035), (0, -0.24, 0.05), "steel", 0.005)
    elif i == 1:  # first aid cabinet
        m.box((0.42, 0.52, 0.16), (0, 0, 0.08), "plastic_white", 0.015)
        m.box((0.38, 0.48, 0.02), (0, 0, 0.17), "plastic_white", 0.008)
        m.box((0.24, 0.07, 0.01), (0, 0.02, 0.185), "sec_sign_green")
        m.box((0.07, 0.24, 0.01), (0, 0.02, 0.185), "sec_sign_green")
        m.box((0.04, 0.08, 0.03), (0.15, -0.16, 0.19), "steel", 0.005)
        m.box((0.1, 0.03, 0.01), (0, -0.2, 0.185), "em_green")
    elif i == 2:  # oxygen mask box
        m.box((0.5, 0.36, 0.14), (0, 0, 0.07), "hazard_yellow", 0.015)
        m.box((0.42, 0.28, 0.02), (0, 0, 0.15), "glass")
        for k in range(2):
            x = -0.1 + k * 0.2
            m.sphere(0.06, (x, 0.02, 0.11), "plastic_grey", 10, 6, scale=(1, 1.2, 0.6))
            m.tube([(x, -0.03, 0.1), (x + 0.05, -0.1, 0.09), (x - 0.02, -0.14, 0.08)], 0.008, "rubber", 5)
        m.box((0.5, 0.05, 0.02), (0, 0.21, 0.05), "sec_sign_black")
        text(m, "O2", 0, 0.21, 0.062, 0.008, "paint_white")
    elif i == 3:  # defibrillator
        m.box((0.4, 0.46, 0.2), (0, 0, 0.1), "paint_white", 0.02)
        m.box((0.4, 0.1, 0.205), (0, 0.18, 0.1), "sec_sign_red", 0.01)
        m.prism([(0.02, 0.1), (0.09, 0.1), (0.03, 0.0), (0.08, 0.0), (-0.06, -0.14), (-0.01, -0.03), (-0.06, -0.03)], 0.01, (0, -0.03, 0.2), "sec_sign_red", plane="xy")
        m.box((0.14, 0.09, 0.02), (0.0, -0.16, 0.21), "black_metal", 0.004)
        m.screen((0.12, 0.05), (0, -0.16, 0.222), "vitals")
        m.box((0.05, 0.03, 0.01), (0.14, 0.18, 0.21), "em_green")
        m.cyl(0.04, 0.015, (-0.13, -0.05, 0.21), "plastic_black", axis="z", seg=10)
        m.cyl(0.04, 0.015, (0.13, -0.05, 0.21), "plastic_black", axis="z", seg=10)
    elif i == 4:  # eye wash
        m.box((0.7, 0.6, 0.02), (0, 0.05, 0.01), "sec_sign_green", 0.004)
        m.cyl(0.19, 0.1, (0, -0.15, 0.22), "plastic_white", seg=16, r2=0.24)
        m.cyl(0.17, 0.02, (0, -0.1, 0.22), "water", seg=16)
        m.cyl(0.02, 0.14, (0, -0.28, 0.22), "steel", seg=8)
        for x in (-0.09, 0.09):
            m.link((x, -0.05, 0.05), (x, -0.06, 0.2), 0.014, "chrome", 6)
            m.cyl(0.03, 0.03, (x, -0.04, 0.22), "sec_sign_green", seg=8)
        m.box((0.02, 0.2, 0.02), (0.26, -0.15, 0.06), "steel")
        m.box((0.16, 0.05, 0.04), (0.26, -0.03, 0.1), "sec_sign_green", 0.005)
        m.box((0.14, 0.14, 0.008), (0, 0.25, 0.024), "paint_white")
        m.sphere(0.035, (0, 0.25, 0.03), "sec_sign_green", 10, 6, scale=(1.5, 1, 0.3))
        m.sphere(0.016, (0, 0.25, 0.034), "sec_sign_black", 8, 5, scale=(1, 1, 0.3))
    elif i == 5:  # breach repair kit
        m.box((0.55, 0.38, 0.16), (0, 0, 0.08), "paint_orange", 0.02)
        for k in range(4):
            m.box((0.07, 0.38, 0.005), (-0.19 + k * 0.125, 0, 0.165), "hazard_yellow", rot=(0, 0, 0)) if k % 2 == 0 else None
        m.box((0.5, 0.08, 0.04), (0, 0.0, 0.18), "black_metal", 0.005)
        m.box((0.1, 0.03, 0.02), (0, 0.0, 0.21), "steel")
        m.box((0.1, 0.06, 0.005), (-0.15, -0.14, 0.17), "sec_sign_red")
        m.box((0.2, 0.05, 0.005), (0.1, -0.14, 0.17), "paint_white")
        m.box((0.6, 0.03, 0.03), (0, 0.19, 0.03), "hull_dark")
    elif i == 6:  # fire blanket box
        m.box((0.28, 0.3, 0.1), (0, 0, 0.05), "paint_red", 0.012)
        m.box((0.24, 0.1, 0.008), (0, 0.06, 0.104), "paint_white")
        text(m, "FIRE", 0, 0.06, 0.11, 0.015, "sec_sign_red")
        m.box((0.05, 0.1, 0.03), (0, -0.19, 0.06), "paint_orange", 0.006)
        m.box((0.28, 0.04, 0.02), (0, -0.1, 0.11), "hazard_yellow")
        m.cyl(0.015, 0.03, (0, -0.15, 0.06), "paint_orange", seg=8, axis="y")
    elif i == 7:  # evac map
        m.box((1.0, 0.7, 0.03), (0, 0, 0.015), "hull_dark", 0.01)
        m.box((0.94, 0.5, 0.02), (0, -0.05, 0.035), "sec_sign_blue")
        m.screen((0.9, 0.44), (0, -0.05, 0.046), "schematic")
        m.box((0.94, 0.1, 0.02), (0, 0.29, 0.035), "sec_sign_green")
        m.cyl(0.03, 0.01, (0.15, -0.02, 0.055), "em_red", axis="z", seg=10)
        for k in range(3):
            m.box((0.12, 0.02, 0.008), (-0.3 + k * 0.1, -0.24, 0.052), "em_green")
    else:  # radiation shelter panel
        m.box((1.3, 1.0, 0.05), (0, 0, 0.025), "hazard_yellow", 0.01)
        m.box((1.16, 0.86, 0.06), (0, 0, 0.03), "hull_dark", 0.01)
        trefoil(m, -0.3, 0.05, 0.062, 0.24, "hazard_yellow")
        m.box((0.45, 0.6, 0.02), (0.35, 0.05, 0.065), "steel", 0.005)
        m.box((0.4, 0.05, 0.02), (0.35, 0.05, 0.08), "hazard_yellow")
        m.box((0.4, 0.14, 0.02), (0.35, -0.3, 0.07), "black_metal")
        m.box((0.3, 0.05, 0.01), (0.35, -0.3, 0.085), "em_amber")
        m.cyl(0.05, 0.03, (-0.3, -0.33, 0.08), "hull_light", axis="z", seg=12)
        m.box((0.05, 0.05, 0.01), (0.5, 0.36, 0.08), "em_red")


@family("safety", ["sprinkler_head", "suppression_nozzle"], mount="ceiling", tags=["safety"], solid=False)
def safety_ceiling(m, i, label, rng):
    if i == 0:
        m.cyl(0.07, 0.01, (0, -0.005, 0), "chrome", seg=14)
        m.cyl(0.02, 0.05, (0, -0.035, 0), "brass", seg=8)
        m.cyl(0.03, 0.03, (0, -0.075, 0), "brass", seg=8, r2=0.02)
        for a in (0, PI):
            m.box((0.006, 0.05, 0.006), (0.025 * math.cos(a), -0.11, 0), "brass")
        m.cyl(0.008, 0.035, (0, -0.115, 0), "paint_red", seg=6)
        m.cyl(0.05, 0.006, (0, -0.145, 0), "brass", seg=12)
    else:
        m.cyl(0.05, 0.3, (0, -0.15, 0), "paint_red", seg=10)
        m.box((0.18, 0.02, 0.18), (0, -0.01, 0), "hull_dark")
        m.cyl(0.065, 0.03, (0, -0.31, 0), "hazard_yellow", seg=12)
        m.cyl(0.09, 0.14, (0, -0.4, 0), "steel", seg=14, r2=0.15)
        m.cyl(0.14, 0.01, (0, -0.475, 0), "black_metal", seg=14)
        for k in range(8):
            a = k * PI / 4
            m.box((0.02, 0.008, 0.035), (0.085 * math.cos(a), -0.48, 0.085 * math.sin(a)), "chrome", rot=(0, -a, 0))
        m.sphere(0.02, (0, -0.48, 0), "em_red", 8, 5)


@family("safety", ["emergency_shower", "hazmat_cabinet", "ration_locker", "spill_kit_bin", "damage_control_locker"],
        mount="floor", tags=["safety"], solid=True)
def safety_floor(m, i, label, rng):
    if i == 0:  # emergency shower + eyewash
        m.cyl(0.4, 0.05, (0, 0.025, 0), "steel", seg=16)
        m.cyl(0.36, 0.01, (0, 0.055, 0), "black_metal", seg=16)
        for a in range(4):
            m.box((0.5, 0.012, 0.03), (0, 0.062, 0), "steel", rot=(0, a * PI / 4, 0))
        m.cyl(0.03, 2.3, (-0.3, 1.15, -0.3), "sec_sign_green", seg=8)
        m.link((-0.3, 2.3, -0.3), (0, 2.3, 0), 0.03, "sec_sign_green", 8)
        m.cyl(0.14, 0.05, (0, 2.27, 0), "chrome", seg=14, r2=0.2)
        for k in range(6):
            a = k * PI / 3
            m.cyl(0.01, 0.006, (0.09 * math.cos(a), 2.24, 0.09 * math.sin(a)), "black_metal", seg=5)
        m.link((0, 2.3, 0.02), (0, 1.75, 0.12), 0.006, "steel", 4)
        m.torus(0.06, 0.008, (0, 1.72, 0.14), "steel", axis="x", seg=12, tseg=4)
        m.box((0.04, 0.04, 0.3), (-0.3, 0.98, -0.15), "sec_sign_green")
        m.cyl(0.19, 0.09, (-0.3, 0.98, 0.1), "plastic_white", seg=14, r2=0.24)
        m.box((0.4, 0.4, 0.02), (-0.3, 1.7, -0.29), "sec_sign_green")
        m.box((0.3, 0.3, 0.005), (-0.3, 1.7, -0.278), "paint_white")
        m.sphere(0.06, (-0.3, 1.7, -0.27), "sec_sign_green", 10, 6, scale=(1, 1.3, 0.25))
    elif i == 1:  # hazmat cabinet, empty
        w, h, d = 0.9, 2.0, 0.5
        locker_shell(m, w, h, d, "hazard_yellow", "hull_dark", "glass_dark", front=False)
        m.box((w - 0.06, 0.03, d - 0.08), (0, 0.35, 0), "steel")
        m.box((w - 0.06, 0.03, d - 0.08), (0, 1.85, 0), "steel")
        m.box((w - 0.06, 0.04, 0.05), (0, 1.75, -0.2), "steel")
        for k in range(3):
            m.cyl(0.012, 0.06, (-0.28 + k * 0.28, 1.65, -0.2 + 0.03), "steel", axis="z", seg=6)
            m.link((-0.28 + k * 0.28, 1.65, -0.17), (-0.28 + k * 0.28, 1.5, -0.15), 0.008, "steel", 5)
        m.box((0.44, 1.7, 0.03), (-w / 2 + 0.22, 1.1, d / 2 + 0.03), "hazard_yellow", 0.006, rot=(0, 0.0, 0))
        m.box((0.36, 0.3, 0.008), (-w / 2 + 0.22, 1.5, d / 2 + 0.05), "sec_sign_black")
        trefoil(m, -w / 2 + 0.22, 1.5, d / 2 + 0.05, 0.12, "hazard_yellow")
        m.box((0.03, 0.15, 0.03), (-w / 2 + 0.4, 1.0, d / 2 + 0.06), "black_metal")
        m.box((w - 0.04, 0.05, 0.02), (0, 0.15, d / 2 - 0.02), "sec_sign_black")
    elif i == 2:  # ration locker
        w, h, d = 1.0, 1.8, 0.5
        locker_shell(m, w, h, d, "paint_green", "hull_dark", "glass", front=False)
        for k in range(4):
            y = 0.35 + k * 0.36
            m.box((w - 0.06, 0.02, d - 0.06), (0, y, 0), "steel")
            for c in range(3):
                m.box((0.26, 0.24, 0.36), (-0.3 + c * 0.3, y + 0.13, 0), rng.choice(["cardboard", "paint_white", "fabric_tan"]), 0.01)
                m.box((0.1, 0.05, 0.01), (-0.3 + c * 0.3, y + 0.15, 0.185), "paint_green")
        m.box((w, 0.08, 0.02), (0, h - 0.06, d / 2 + 0.02), "paint_white")
        text(m, "MESS", 0, h - 0.06, d / 2 + 0.032, 0.012, "paint_green")
    elif i == 3:  # spill kit bin
        m.box((0.6, 0.62, 0.42), (0, 0.43, 0), "hazard_yellow", 0.03)
        m.box((0.64, 0.06, 0.46), (0, 0.76, 0), "hazard_yellow", 0.015)
        m.box((0.4, 0.14, 0.02), (0, 0.5, 0.215), "paint_white")
        m.box((0.36, 0.04, 0.01), (0, 0.5, 0.228), "sec_sign_black")
        m.box((0.3, 0.05, 0.05), (0, 0.72, 0.24), "black_metal", 0.008)
        for s in (-1, 1):
            m.cyl(0.07, 0.04, (s * 0.26, 0.07, -0.1), "rubber", axis="x", seg=12)
            m.cyl(0.03, 0.05, (s * 0.27, 0.05, 0.15), "black_metal", seg=8)
        m.link((-0.28, 0.76, -0.2), (-0.28, 1.1, -0.35), 0.015, "steel", 6)
        m.link((0.28, 0.76, -0.2), (0.28, 1.1, -0.35), 0.015, "steel", 6)
        m.link((-0.28, 1.1, -0.35), (0.28, 1.1, -0.35), 0.015, "steel", 6)
    else:  # damage-control locker
        w, h, d = 1.0, 2.0, 0.55
        m.box((w, h - 0.1, d), (0, 0.1 + (h - 0.1) / 2, 0), "paint_red", 0.015)
        m.box((w - 0.04, 0.1, d - 0.06), (0, 0.05, 0), "black_metal")
        for s in (-1, 1):
            m.box((w / 2 - 0.05, h - 0.3, 0.03), (s * (w / 4), 1.05, d / 2 + 0.015), "paint_red", 0.008)
        m.box((0.02, h - 0.3, 0.05), (0, 1.05, d / 2 + 0.03), "black_metal")
        m.box((0.7, 0.16, 0.01), (0, 1.75, d / 2 + 0.035), "paint_white")
        text(m, "DC", 0, 1.75, d / 2 + 0.043, 0.024, "sec_sign_red")
        m.box((0.9, 0.06, 0.01), (0, 0.3, d / 2 + 0.035), "hazard_yellow")
        m.box((0.1, 0.06, 0.03), (0.14, 1.05, d / 2 + 0.06), "steel", 0.005)
        m.box((0.1, 0.06, 0.03), (-0.14, 1.05, d / 2 + 0.06), "steel", 0.005)


# ================================================================= SIGNS
def plate(m, w, h, bg, frame=None, t=0.03):
    if frame:
        m.box((w, h, t), (0, 0, t / 2), frame, 0.008)
        m.box((w - 0.05, h - 0.05, 0.006), (0, 0, t + 0.002), bg)
    else:
        m.box((w, h, t), (0, 0, t / 2), bg, 0.008)
    return t + 0.005


def tri_pts(cx, cy, r, up=True):
    s = 1 if up else -1
    return [(cx - r * 0.866, cy - s * r * 0.5), (cx + r * 0.866, cy - s * r * 0.5), (cx, cy + s * r)]


def hazard_tri(m, z=0.0):
    m.prism(tri_pts(0, -0.03, 0.36), 0.02, (0, 0, z), "sec_sign_black", plane="xy", bevel=0.004)
    m.prism(tri_pts(0, -0.05, 0.3), 0.008, (0, 0, z + 0.02), "hazard_yellow", plane="xy")
    return z + 0.03


def icon(m, kind, cx, cy, z, s=1.0):
    """Department pictogram built from simple shapes, centred at (cx,cy) on surface z."""
    f, d = "paint_white", 0.008
    if kind == "bridge":  # helm wheel
        m.torus(0.1 * s, 0.014 * s, (cx, cy, z + 0.01), f, axis="z", seg=16, tseg=6)
        for k in range(4):
            a = k * PI / 4
            m.link((cx + 0.1 * s * math.cos(a), cy + 0.1 * s * math.sin(a), z + 0.01), (cx - 0.1 * s * math.cos(a), cy - 0.1 * s * math.sin(a), z + 0.01), 0.008 * s, f, 5)
        m.cyl(0.03 * s, d, (cx, cy, z + 0.01), f, axis="z", seg=10)
    elif kind == "engineering":  # gear
        m.cyl(0.09 * s, d, (cx, cy, z + 0.004), f, axis="z", seg=12)
        for k in range(8):
            a = k * PI / 4
            m.box((0.05 * s, 0.05 * s, d), (cx + 0.105 * s * math.cos(a), cy + 0.105 * s * math.sin(a), z + 0.004), f, rot=(0, 0, a))
        m.cyl(0.04 * s, d, (cx, cy, z + 0.008), "sec_sign_black", axis="z", seg=10)
    elif kind == "medical":
        m.box((0.24 * s, 0.075 * s, d), (cx, cy, z + 0.004), "sec_sign_red")
        m.box((0.075 * s, 0.24 * s, d), (cx, cy, z + 0.004), "sec_sign_red")
    elif kind == "science":  # flask
        m.prism([(-0.03 * s, 0.12 * s), (0.03 * s, 0.12 * s), (0.03 * s, 0.04 * s), (0.11 * s, -0.11 * s), (-0.11 * s, -0.11 * s), (-0.03 * s, 0.04 * s)], d, (cx, cy, z), f, plane="xy")
        m.prism([(-0.075 * s, -0.06 * s), (0.075 * s, -0.06 * s), (0.1 * s, -0.1 * s), (-0.1 * s, -0.1 * s)], d, (cx, cy, z + d), "em_cyan", plane="xy")
        m.box((0.09 * s, 0.02 * s, d), (cx, cy + 0.125 * s, z + 0.004), f)
    elif kind == "security":  # shield
        m.prism([(-0.1 * s, 0.12 * s), (0.1 * s, 0.12 * s), (0.1 * s, -0.02 * s), (0, -0.14 * s), (-0.1 * s, -0.02 * s)], d, (cx, cy, z), f, plane="xy")
        m.prism([(-0.065 * s, 0.085 * s), (0.065 * s, 0.085 * s), (0.065 * s, -0.005 * s), (0, -0.09 * s), (-0.065 * s, -0.005 * s)], d, (cx, cy, z + d), "paint_navy", plane="xy")
        m.cyl(0.03 * s, d, (cx, cy + 0.01 * s, z + 2 * d), "gold_trim", axis="z", seg=5)
    elif kind == "cargo":
        m.box((0.22 * s, 0.18 * s, d), (cx, cy, z + 0.004), f)
        m.box((0.03 * s, 0.18 * s, d), (cx, cy, z + 0.008), "sec_sign_black")
        m.box((0.22 * s, 0.03 * s, d), (cx, cy, z + 0.008), "sec_sign_black")
    elif kind == "hangar":  # ship silhouette
        m.prism([(0, 0.13 * s), (0.05 * s, 0.03 * s), (0.14 * s, -0.08 * s), (0.14 * s, -0.11 * s), (0.04 * s, -0.07 * s), (0.03 * s, -0.12 * s),
                 (-0.03 * s, -0.12 * s), (-0.04 * s, -0.07 * s), (-0.14 * s, -0.11 * s), (-0.14 * s, -0.08 * s), (-0.05 * s, 0.03 * s)], d, (cx, cy, z), f, plane="xy")
    elif kind == "quarters":  # bed
        m.box((0.26 * s, 0.05 * s, d), (cx, cy - 0.03 * s, z + 0.004), f)
        m.box((0.05 * s, 0.14 * s, d), (cx - 0.13 * s, cy, z + 0.004), f)
        m.box((0.08 * s, 0.05 * s, d), (cx - 0.08 * s, cy, z + 0.008), f)
        m.box((0.05 * s, 0.05 * s, d), (cx + 0.13 * s, cy - 0.07 * s, z + 0.004), f)
        m.box((0.2 * s, 0.04 * s, d), (cx + 0.03 * s, cy + 0.0, z + 0.008), "sec_sign_red")
    elif kind == "mess":  # plate + fork + knife
        m.torus(0.06 * s, 0.01 * s, (cx, cy, z + 0.01), f, axis="z", seg=14, tseg=5)
        m.cyl(0.04 * s, d, (cx, cy, z + 0.006), f, axis="z", seg=12)
        m.box((0.015 * s, 0.22 * s, d), (cx - 0.11 * s, cy, z + 0.004), f)
        m.box((0.05 * s, 0.05 * s, d), (cx - 0.11 * s, cy + 0.09 * s, z + 0.004), f)
        m.box((0.02 * s, 0.22 * s, d), (cx + 0.11 * s, cy, z + 0.004), f)
    else:  # airlock: ring door with wheel
        m.torus(0.11 * s, 0.018 * s, (cx, cy, z + 0.01), f, axis="z", seg=18, tseg=6)
        m.cyl(0.075 * s, d, (cx, cy, z + 0.004), "sec_sign_black", axis="z", seg=16)
        for k in range(3):
            a = k * PI / 3
            m.box((0.15 * s, 0.014 * s, d), (cx, cy, z + 0.01), f, rot=(0, 0, a))


def dept_plate(m, i, name, kind, bg, fg="paint_white"):
    plate(m, 1.0, 0.4, bg, "steel")
    m.box((0.32, 0.32, 0.006), (-0.34, 0, 0.037), "sec_sign_black")
    icon(m, kind, -0.34, 0, 0.04)
    n = len(name)
    px = min(0.03, 0.56 / (4 * n - 1))
    text(m, name, 0.17, 0.0, 0.038, px, fg)
    bolts(m, [(-0.46, 0.17), (0.46, 0.17), (-0.46, -0.17), (0.46, -0.17)], 0.03)


DEPTS = [("bridge", "BRIDGE", "sec_sign_blue"), ("engineering", "ENGINEERING", "paint_orange"),
         ("medical", "MEDICAL", "sec_sign_green"), ("science", "SCIENCE", "paint_teal"),
         ("security", "SECURITY", "sec_sign_red"), ("cargo", "CARGO", "paint_gold"),
         ("hangar", "HANGAR", "paint_grey"), ("quarters", "QUARTERS", "sec_sign_purple"),
         ("mess", "MESS", "food_brown"), ("airlock", "AIRLOCK", "paint_navy")]

SIGN_WALL = (["deck_1", "deck_2", "deck_3", "exit_arrow", "hazard_radiation", "hazard_biohazard", "hazard_high_voltage",
              "hazard_laser", "hazard_low_oxygen"] + ["dept_" + d[0] for d in DEPTS] +
             ["emergency_exit", "no_entry", "blade_sign"])


@family("sign", SIGN_WALL, mount="wall", tags=["safety"], solid=False, mount_y=2.0)
def sign_wall(m, i, label, rng):
    if i < 3:  # deck numbers
        n = i + 1
        col = ["sec_sign_blue", "sec_sign_green", "paint_orange"][i]
        plate(m, 0.8, 0.95, "sec_sign_black", "steel")
        m.box((0.7, 0.16, 0.006), (0, 0.33, 0.038), col)
        text(m, "DECK", 0, 0.33, 0.045, 0.036, "paint_white")
        text(m, str(n), 0, -0.1, 0.04, 0.09, "paint_white")
        for k in range(n):
            m.box((0.1, 0.03, 0.006), (-0.15 * (n - 1) + k * 0.3, -0.38, 0.038), col)
    elif i == 3:  # exit arrow
        plate(m, 0.7, 0.24, "sec_sign_green", "paint_white")
        m.prism([(0.08, 0.03), (0.22, 0.03), (0.22, 0.075), (0.31, 0), (0.22, -0.075), (0.22, -0.03), (0.08, -0.03)], 0.006, (0, 0, 0.036), "paint_white", plane="xy")
        text(m, "EXIT", -0.15, 0, 0.038, 0.022, "paint_white")
    elif i == 4:  # radiation
        m.cyl(0.32, 0.03, (0, 0, 0.015), "sec_sign_black", axis="z", seg=24, bevel=0.005)
        m.cyl(0.29, 0.008, (0, 0, 0.033), "hazard_yellow", axis="z", seg=24)
        trefoil(m, 0, 0, 0.037, 0.24, "sec_sign_black")
    elif i == 5:  # biohazard
        plate(m, 0.6, 0.6, "paint_orange", "sec_sign_black")
        for k in range(3):
            a = math.radians(90 + k * 120)
            m.torus(0.085, 0.022, (0.1 * math.cos(a), 0.1 * math.sin(a) - 0.0, 0.04), "sec_sign_black", axis="z", seg=14, tseg=5)
            m.link((0, 0, 0.038), (0.22 * math.cos(a + 0.5), 0.22 * math.sin(a + 0.5), 0.038), 0.018, "sec_sign_black", 5)
        m.torus(0.06, 0.012, (0, 0, 0.04), "sec_sign_black", axis="z", seg=12, tseg=5)
        m.cyl(0.02, 0.01, (0, 0, 0.04), "sec_sign_black", axis="z", seg=6)
    elif i == 6:  # high voltage
        z = hazard_tri(m)
        m.prism([(0.04, 0.16), (0.11, 0.16), (0.03, 0.01), (0.09, 0.01), (-0.06, -0.2), (-0.02, -0.03), (-0.09, -0.03)], 0.008, (0, -0.06, z), "sec_sign_black", plane="xy")
    elif i == 7:  # laser (diamond)
        m.box((0.5, 0.5, 0.03), (0, 0, 0.015), "sec_sign_red", 0.008, rot=(0, 0, PI / 4))
        m.box((0.4, 0.4, 0.006), (0, 0, 0.033), "hazard_yellow", rot=(0, 0, PI / 4))
        m.cyl(0.05, 0.008, (0, 0, 0.04), "sec_sign_black", axis="z", seg=10)
        for k in range(8):
            a = k * PI / 4
            m.box((0.08, 0.016, 0.008), (0.11 * math.cos(a), 0.11 * math.sin(a), 0.04), "sec_sign_black", rot=(0, 0, a))
    elif i == 8:  # low oxygen
        plate(m, 0.6, 0.4, "sec_sign_blue", "paint_white")
        text(m, "O2", -0.12, 0.02, 0.038, 0.04, "paint_white")
        m.prism([(0.2, 0.15), (0.28, 0.15), (0.28, 0.0), (0.33, 0.0), (0.24, -0.12), (0.15, 0.0), (0.2, 0.0)], 0.006, (0, 0, 0.036), "hazard_yellow", plane="xy")
    elif 9 <= i < 19:
        k, name, bg = DEPTS[i - 9]
        dept_plate(m, i, name, k, bg)
    elif i == 19:  # emergency exit (emissive)
        m.box((0.56, 0.24, 0.06), (0, 0, 0.03), "hull_dark", 0.012)
        m.box((0.5, 0.18, 0.02), (0, 0, 0.06), "em_green")
        text(m, "EXIT", 0.06, 0.0, 0.072, 0.02, "sec_sign_black")
        m.box((0.1, 0.14, 0.008), (-0.19, 0, 0.072), "sec_sign_black")
        m.box((0.05, 0.1, 0.008), (-0.19, 0, 0.08), "em_green")
    elif i == 20:  # no entry
        m.cyl(0.24, 0.03, (0, 0, 0.015), "paint_white", axis="z", seg=24, bevel=0.004)
        m.torus(0.21, 0.03, (0, 0, 0.035), "sec_sign_red", axis="z", seg=24, tseg=6)
        m.box((0.36, 0.09, 0.012), (0, 0, 0.038), "sec_sign_red")
    else:  # projecting blade sign (perpendicular to wall)
        m.box((0.16, 0.3, 0.03), (0, 0, 0.015), "hull_dark", 0.005)
        m.link((0, 0.12, 0.03), (0, 0.12, 0.85), 0.018, "steel", 6)
        m.link((0, -0.12, 0.03), (0, -0.12, 0.85), 0.018, "steel", 6)
        m.link((0, -0.12, 0.03), (0, 0.12, 0.85), 0.012, "steel", 6)
        m.box((0.04, 0.5, 0.8), (0, 0.0, 0.5), "sec_sign_blue", 0.008)
        for s in (-1, 1):
            m.box((0.01, 0.42, 0.72), (s * 0.024, 0, 0.5), "paint_white", 0.003)
            m.prism([(0.2, 0.03), (0.6, 0.03), (0.6, 0.12), (0.75, 0), (0.6, -0.12), (0.6, -0.03), (0.2, -0.03)], 0.004, (s * 0.03 - 0.002, 0, 0), "sec_sign_blue", plane="zy")


@family("sign", ["hanging_ceiling_sign"], mount="ceiling", tags=["safety"], solid=False)
def sign_ceiling(m, i, label, rng):
    for x in (-0.45, 0.45):
        m.link((x, 0, 0), (x, -0.45, 0), 0.01, "steel", 6)
        m.box((0.05, 0.02, 0.05), (x, -0.005, 0), "steel")
    m.box((1.3, 0.44, 0.05), (0, -0.66, 0), "hull_dark", 0.01)
    for z, s in ((0.03, 1), (-0.03, -1)):
        m.box((1.2, 0.36, 0.008), (0, -0.66, z), "sec_sign_green")
    text(m, "EXIT", -0.15, -0.66, 0.036, 0.024, "paint_white")
    m.prism([(0.2, 0.04), (0.4, 0.04), (0.4, 0.1), (0.52, 0), (0.4, -0.1), (0.4, -0.04), (0.2, -0.04)], 0.006, (0, -0.66, 0.03), "paint_white", plane="xy")


@family("sign", ["floor_marking", "wet_floor_stand", "barrier_tape_frame"], mount="floor", tags=["safety"], solid=False)
def sign_floor(m, i, label, rng):
    if i == 0:  # hazard-stripe floor panel with arrow
        m.box((1.6, 0.012, 0.5), (0, 0.006, 0), "sec_sign_black", 0.003)
        for k in range(8):
            x = -0.75 + k * 0.2
        for k in range(7):
            x = -0.68 + k * 0.23
            m.prism([(x, -0.22), (x + 0.1, -0.22), (x + 0.2, 0.22), (x + 0.1, 0.22)], 0.004, (0, 0.012, 0), "hazard_yellow", plane="xz")
    elif i == 1:  # wet floor A-frame
        for s in (-1, 1):
            m.box((0.34, 0.6, 0.02), (0, 0.32, s * 0.13), "hazard_yellow", 0.006, rot=(-s * 0.24, 0, 0))
            m.prism(tri_pts(0, 0, 0.13), 0.004, (0, 0.34, s * 0.14 + s * 0.012), "sec_sign_black", plane="xy", rot=(-s * 0.24, PI if s < 0 else 0, 0))
        m.box((0.36, 0.03, 0.34), (0, 0.015, 0), "hazard_yellow", 0.005)
        m.box((0.3, 0.03, 0.04), (0, 0.63, 0), "black_metal", 0.005)
        m.cyl(0.025, 0.03, (0, 0.62, 0), "steel", axis="x", seg=8)
    else:  # stanchions with hazard tape
        for s in (-1, 1):
            x = s * 0.85
            m.cyl(0.18, 0.03, (x, 0.015, 0), "black_metal", seg=14)
            m.cyl(0.025, 0.95, (x, 0.5, 0), "chrome", seg=8)
            m.sphere(0.04, (x, 1.0, 0), "chrome", 10, 6)
            m.cyl(0.05, 0.1, (x, 0.9, 0), "black_metal", seg=10)
        for k in range(17):
            m.box((0.1, 0.06, 0.006), (-0.8 + k * 0.1, 0.9, 0.0), "hazard_yellow" if k % 2 == 0 else "sec_sign_black")
        m.box((0.4, 0.2, 0.006), (0, 0.6, 0.003), "sec_sign_red")


# ================================================================= BEACONS
@family("beacon", ["rotating_beacon", "emergency_flood", "strobe_light", "siren_horn", "airlock_status_light",
                   "emergency_lighting_unit", "intercom_speaker", "evac_light_strip"],
        mount="wall", tags=["safety"], solid=False, mount_y=2.2)
def beacon_wall(m, i, label, rng):
    if i == 0:  # rotating beacon
        m.cyl(0.09, 0.03, (0, 0, 0.015), "hull_dark", axis="z", seg=14)
        m.cyl(0.07, 0.05, (0, 0, 0.055), "black_metal", axis="z", seg=14)
        m.cyl(0.075, 0.12, (0, 0, 0.14), "glass_amber", axis="z", seg=16, r2=0.06)
        m.cyl(0.03, 0.09, (0, 0, 0.13), "em_amber", axis="z", seg=8)
        m.box((0.07, 0.006, 0.05), (0, 0.0, 0.16), "chrome")
    elif i == 1:  # twin flood lamps
        m.box((0.3, 0.12, 0.04), (0, 0, 0.02), "black_metal", 0.006)
        m.box((0.05, 0.1, 0.1), (0, 0, 0.09), "gunmetal", 0.006)
        for s in (-1, 1):
            m.box((0.22, 0.2, 0.12), (s * 0.15, 0.04, 0.16), "hull_dark", 0.02, rot=(0, -s * 0.5, 0))
            m.box((0.16, 0.15, 0.012), (s * 0.15 + s * 0.03, 0.04, 0.2), "em_white", rot=(0, -s * 0.5, 0))
        m.cyl(0.015, 0.05, (0, 0, 0.03), "steel", seg=6)
    elif i == 2:  # xenon strobe
        m.box((0.14, 0.1, 0.03), (0, 0, 0.015), "plastic_white", 0.006)
        m.box((0.12, 0.08, 0.05), (0, 0, 0.055), "paint_red", 0.012)
        m.box((0.09, 0.055, 0.02), (0, 0, 0.09), "em_white")
        m.box((0.09, 0.055, 0.008), (0, 0, 0.1), "glass")
    elif i == 3:  # siren horns
        m.box((0.2, 0.3, 0.03), (0, 0, 0.015), "hull_dark", 0.006)
        for k, y in enumerate((-0.07, 0.07)):
            m.cyl(0.04, 0.08, (0, y, 0.07), "steel", axis="z", seg=10)
            m.cyl(0.045, 0.22, (0, y, 0.22), "paint_red", axis="z", seg=14, r2=0.1)
            m.cyl(0.09, 0.005, (0, y, 0.33), "black_metal", axis="z", seg=14)
        m.box((0.03, 0.03, 0.02), (0.08, 0.13, 0.04), "em_red")
    elif i == 4:  # airlock status light: 3 stacked lamps with labelled plate
        m.box((0.16, 0.5, 0.04), (0, 0, 0.02), "black_metal", 0.01)
        for k, (mat, off) in enumerate((("em_red", 0.15), ("em_amber", 0.0), ("em_green", -0.15))):
            m.cyl(0.055, 0.02, (0, off, 0.05), "hull_dark", axis="z", seg=14)
            m.cyl(0.045, 0.02, (0, off, 0.066), mat if k in (0, 2) else mat, axis="z", seg=14)
        m.box((0.16, 0.05, 0.02), (0, -0.28, 0.01), "hazard_yellow")
    elif i == 5:  # emergency lighting unit
        m.box((0.42, 0.16, 0.08), (0, 0, 0.04), "plastic_white", 0.012)
        for s in (-1, 1):
            m.sphere(0.06, (s * 0.15, 0, 0.11), "hull_dark", 10, 6, scale=(1, 1, 0.8))
            m.box((0.07, 0.07, 0.01), (s * 0.15 + s * 0.03, 0.0, 0.15), "em_white", rot=(0, -s * 0.5, 0))
            m.link((s * 0.15, 0, 0.06), (s * 0.15, 0, 0.11), 0.012, "steel", 5)
        m.cyl(0.015, 0.01, (0, 0.0, 0.085), "em_green", axis="z", seg=8)
        m.box((0.05, 0.02, 0.008), (0, -0.05, 0.082), "plastic_grey")
    elif i == 6:  # intercom speaker
        m.box((0.3, 0.42, 0.05), (0, 0, 0.025), "hull_dark", 0.012)
        m.cyl(0.11, 0.02, (0, 0.06, 0.06), "black_metal", axis="z", seg=18)
        for k in range(5):
            m.torus(0.02 + k * 0.02, 0.004, (0, 0.06, 0.072), "steel", axis="z", seg=16, tseg=4)
        m.cyl(0.02, 0.01, (0, 0.06, 0.072), "steel", axis="z", seg=8)
        m.cyl(0.03, 0.02, (0, -0.12, 0.06), "plastic_black", axis="z", seg=10)
        m.box((0.05, 0.03, 0.012), (0.09, -0.12, 0.055), "em_red")
        m.box((0.05, 0.03, 0.012), (-0.09, -0.12, 0.055), "em_green")
    else:  # evac light strip
        m.box((1.6, 0.1, 0.03), (0, 0, 0.015), "hull_dark", 0.006)
        for k in range(7):
            x = -0.66 + k * 0.22
            m.prism([(x - 0.06, 0.035), (x, 0.035), (x + 0.06, 0), (x, -0.035), (x - 0.06, -0.035), (x, 0)], 0.012, (0, 0, 0.03), "em_green", plane="xy")
        m.box((0.05, 0.1, 0.04), (-0.82, 0, 0.02), "black_metal")
        m.box((0.05, 0.1, 0.04), (0.82, 0, 0.02), "black_metal")


@family("beacon", ["red_alert_bar", "yellow_alert_bar"], mount="ceiling", tags=["safety"], solid=False)
def beacon_ceiling(m, i, label, rng):
    if i == 0:
        m.box((1.3, 0.05, 0.16), (0, -0.025, 0), "hull_dark", 0.008)
        m.box((1.2, 0.08, 0.12), (0, -0.09, 0), "em_red", 0.025)
        for k in range(6):
            m.box((0.012, 0.085, 0.125), (-0.5 + k * 0.2, -0.09, 0), "black_metal")
        for s in (-1, 1):
            m.box((0.06, 0.12, 0.16), (s * 0.63, -0.08, 0), "black_metal", 0.01)
    else:
        m.box((0.9, 0.04, 0.2), (0, -0.02, 0), "black_metal", 0.006)
        for k in range(4):
            x = -0.33 + k * 0.22
            m.cyl(0.085, 0.05, (x, -0.065, 0), "hull_dark", seg=14)
            m.cyl(0.075, 0.06, (x, -0.11, 0), "em_amber" if k % 2 == 0 else "glass_amber", seg=14, r2=0.06)
        m.box((0.92, 0.02, 0.02), (0, -0.045, 0.11), "hazard_yellow")


# ================================================================= SUIT RACKS (no figures)
@family("suitrack", ["eva_helmet_rack", "tool_belt_board"], mount="wall", tags=["safety"], solid=False, mount_y=1.5)
def suitrack_wall(m, i, label, rng):
    if i == 0:
        m.box((1.5, 0.9, 0.04), (0, 0, 0.02), "hull_dark", 0.01)
        for y in (-0.05, -0.42):
            m.box((1.5, 0.04, 0.34), (0, y, 0.19), "steel", 0.006)
        for c in range(4):
            x = -0.55 + c * 0.37
            for row, y in enumerate((0.08, -0.29)):
                if row == 1 and c == 3:
                    continue
                m.sphere(0.13, (x, y + 0.14, 0.2), "paint_white", 10, 6)
                m.sphere(0.1, (x, y + 0.15, 0.27), "glass_amber", 8, 4, scale=(1.1, 0.75, 0.5))
                m.torus(0.12, 0.014, (x, y + 0.06, 0.2), "steel", axis="y", seg=10, tseg=4)
                m.cyl(0.025, 0.05, (x + 0.11, y + 0.14, 0.2), "steel", axis="x", seg=8)
        m.box((1.5, 0.05, 0.05), (0, 0.44, 0.04), "hazard_yellow", 0.006)
    else:
        m.box((1.2, 0.9, 0.03), (0, 0, 0.015), "wood_light", 0.008)
        for gx in range(8):
            for gy in range(5):
                m.cyl(0.005, 0.005, (-0.5 + gx * 0.14, -0.3 + gy * 0.15, 0.033), "black_metal", axis="z", seg=4)
        for k in range(2):  # belts hung on hooks
            x = -0.35 + k * 0.5
            m.link((x, 0.35, 0.05), (x, 0.35, 0.08), 0.015, "steel", 6)
            m.torus(0.15, 0.02, (x, 0.2, 0.08), "leather_brown", axis="z", seg=16, tseg=5)
            for a in range(3):
                m.box((0.06, 0.08, 0.05), (x + 0.15 * math.cos(a * 2.1 + 0.6), 0.2 + 0.15 * math.sin(a * 2.1 + 0.6), 0.1), "gunmetal", 0.008)
        for k in range(3):  # wrenches, cutter, torch
            x = 0.3 + k * 0.14
            m.box((0.03, 0.4, 0.012), (x, -0.05, 0.05), "chrome", 0.005)
            m.cyl(0.03, 0.03, (x, 0.16, 0.055), "chrome", axis="z", seg=6) if k == 0 else None
            m.cyl(0.02, 0.15, (x, -0.24, 0.06), "paint_orange", seg=8) if k == 1 else None
        m.cyl(0.05, 0.16, (-0.2, -0.28, 0.07), "paint_red", axis="x", seg=10)
        m.box((0.15, 0.1, 0.04), (-0.4, -0.3, 0.05), "paint_orange", 0.008)
        m.box((1.2, 0.05, 0.05), (0, 0.46, 0.04), "hazard_yellow", 0.006)


@family("suitrack", ["oxygen_pack_rack", "glove_boot_locker", "suit_up_bench", "decontamination_arch"],
        mount="floor", tags=["safety"], solid=True)
def suitrack_floor(m, i, label, rng):
    if i == 0:  # oxygen backpacks on a frame
        for x in (-0.8, 0.8):
            m.box((0.06, 1.7, 0.5), (x, 0.85, 0), "steel", 0.006)
            m.box((0.2, 0.04, 0.6), (x, 0.02, 0), "black_metal")
        m.box((1.66, 0.06, 0.06), (0, 1.5, -0.2), "steel")
        m.box((1.66, 0.06, 0.06), (0, 0.6, -0.2), "steel")
        m.box((1.6, 0.05, 0.5), (0, 0.15, 0), "hull_dark")
        for c in range(4):
            x = -0.55 + c * 0.37
            m.box((0.3, 0.5, 0.18), (x, 0.95, -0.05), "paint_white", 0.02)
            for s in (-1, 1):
                m.cyl(0.05, 0.42, (x + s * 0.07, 0.95, 0.09), "paint_teal" if c % 2 else "paint_blue", seg=10)
                m.sphere(0.05, (x + s * 0.07, 1.16, 0.09), "paint_teal" if c % 2 else "paint_blue", 10, 5, scale=(1, 0.5, 1))
            m.box((0.1, 0.05, 0.02), (x, 1.12, 0.05), "em_green")
            m.tube([(x + 0.14, 1.0, 0.0), (x + 0.2, 0.7, 0.08), (x + 0.12, 0.35, 0.1)], 0.012, "rubber", 5)
    elif i == 1:  # glove & boot locker (open)
        w, h, d = 1.1, 1.9, 0.5
        locker_shell(m, w, h, d, "paint_grey", "hull_dark", "glass_dark", front=False)
        m.box((0.02, h - 0.2, d - 0.06), (0, 1.0, 0.0), "hull_dark")
        for s in (-1, 1):
            xc = s * 0.27
            m.box((0.46, 0.02, d - 0.06), (xc, 1.2, 0), "steel")
            m.box((0.46, 0.02, d - 0.06), (xc, 0.6, 0), "steel")
            for gx in (-0.1, 0.1):  # gloves
                m.box((0.11, 0.2, 0.05), (xc + gx, 1.32, 0.05), "fabric_grey", 0.02)
                m.box((0.11, 0.05, 0.04), (xc + gx, 1.44, 0.05), "steel")
            for bx in (-0.1, 0.1):  # boots
                m.box((0.12, 0.3, 0.16), (xc + bx, 0.77, 0.0), "rubber", 0.02)
                m.box((0.12, 0.1, 0.26), (xc + bx, 0.67, 0.08), "rubber", 0.02)
            m.box((0.4, 0.08, 0.01), (xc, 1.8, d / 2), "hazard_yellow")
            m.box((0.44, 0.3, 0.2), (xc, 0.28, 0.0), "hull_mid", 0.01)
        m.box((w, 0.04, 0.03), (0, h - 0.02, d / 2), "paint_gold")
    elif i == 2:  # suit-up bench with helmet cubbies + hooks
        m.box((2.2, 0.08, 0.5), (0, 0.46, 0.15), "fabric_grey", 0.02)
        m.box((2.2, 0.03, 0.5), (0, 0.4, 0.15), "steel")
        for x in (-1.0, 0.0, 1.0):
            m.box((0.08, 0.4, 0.44), (x, 0.2, 0.15), "hull_dark", 0.008)
        m.box((2.2, 0.04, 0.4), (0, 0.15, 0.15), "hull_mid")
        for c in range(4):
            m.sphere(0.11, (-0.8 + c * 0.55, 0.3, 0.15), "paint_white", 10, 6, scale=(1, 0.9, 1))
        m.box((2.2, 1.2, 0.05), (0, 1.2, -0.12), "hull_dark", 0.01)
        for c in range(7):
            x = -0.9 + c * 0.3
            m.cyl(0.012, 0.1, (x, 1.5, -0.06), "steel", axis="z", seg=6)
            m.sphere(0.015, (x, 1.5, -0.0), "steel", 6, 4)
        m.box((2.2, 0.06, 0.07), (0, 1.8, -0.1), "hazard_yellow", 0.005)
        m.box((0.5, 0.1, 0.01), (0, 1.2, -0.09), "paint_white")
    else:  # decon arch 2.0 m
        for s in (-1, 1):
            m.box((0.24, 2.0, 0.8), (s * 0.65, 1.0, 0), "hull_light", 0.02)
            m.box((0.28, 0.06, 0.84), (s * 0.65, 0.03, 0), "black_metal")
            for k in range(5):
                m.cyl(0.02, 0.05, (s * 0.52, 0.4 + k * 0.32, 0), "chrome", axis="x", seg=8)
            m.box((0.03, 0.06, 0.7), (s * 0.535, 0.2, 0), "paint_teal")
        m.box((1.54, 0.24, 0.8), (0, 1.88, 0), "hull_light", 0.02)
        for k in range(5):
            m.cyl(0.025, 0.06, (-0.5 + k * 0.25, 1.73, 0), "chrome", seg=8)
        m.box((0.6, 0.06, 0.02), (0, 1.9, 0.41), "em_cyan")
        m.box((1.0, 0.03, 0.7), (0, 0.02, 0), "steel")
        for k in range(6):
            m.box((0.9, 0.006, 0.02), (0, 0.04, -0.3 + k * 0.12), "black_metal")
        m.box((0.16, 0.2, 0.06), (1.0, 1.3, 0.3), "black_metal", 0.01)
        m.box((0.08, 0.08, 0.01), (1.0, 1.32, 0.335), "em_amber")
