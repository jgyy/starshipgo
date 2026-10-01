"""Realistic food models, part 4: space rations, serving trays, buffet and display furniture."""
import math

from .food import plate, wobble
from .food_drinks import handle
from .foodkit import PI, TAU, Menu, blob, bowl_outer, dome, heap, lathe, scaled, slab, smooth_prof, spline, sprig, tube3, vessel

menu = Menu()
ration = menu.cat("ration", tags=("food", "ration"))
tray = menu.cat("tray", tags=("food", "tray"))
buffet = menu.cat("buffet", mount="floor", tags=("food", "buffet", "display"))


# ---------------------------------------------------------------- helpers
def pouch(m, w, h, d, tex, pos=(0, 0, 0), rot=(0, 0, 0)):
    """Stand-up retort pouch: pillow body pinched towards a flat top seal, printed on both faces."""
    def pinch(x, y, z):
        t = y / h
        return x * (1 - 0.04 * t * t), y, z * (0.2 + 0.8 * (1 - t ** 3)) * (1 + 0.1 * math.sin(PI * min(1.0, t * 1.4)) * 0.0)
    slab(m, w, h, d, pos, tex, "box", 0.004, rot=rot, warp=pinch)
    slab(m, w * 0.98, 0.012, d * 0.2, (pos[0], pos[1] + h - 0.012 if rot == (0, 0, 0) else pos[1], pos[2]), "f_pouch_edge", "box", 0.0008, rot=rot) if rot == (0, 0, 0) else None


def tray_frame(m, w, d, h, t, mat, xs=(), zs=(), pos=(0, 0, 0)):
    """Compartment tray: floor, rim walls and divider walls at local x = xs / z = zs.  Returns the height of the cell floor."""
    x, y, z = pos
    m.box((w, t, d), (x, y + t / 2, z), mat, 0.002)
    for sz in (-1, 1):
        m.box((w, h, t), (x, y + h / 2, z + sz * (d / 2 - t / 2)), mat, 0.002)
    for sx in (-1, 1):
        m.box((t, h, d - 2 * t), (x + sx * (w / 2 - t / 2), y + h / 2, z), mat, 0.002)
    for dx in xs:
        m.box((t, h * 0.9, d - 2 * t), (x + dx, y + h * 0.45, z), mat, 0.001)
    for dz in zs:
        m.box((w - 2 * t, h * 0.9, t), (x, y + h * 0.45, z + dz), mat, 0.001)
    return y + t


def spork(m, pos, ang=0.0, L=0.15, mat="f_cap_black"):
    c, s = math.cos(ang), math.sin(ang)
    m.link((pos[0] - c * L / 2, pos[1] + 0.002, pos[2] - s * L / 2), (pos[0] + c * L * 0.3, pos[1] + 0.002, pos[2] + s * L * 0.3), 0.0035, mat, 5)
    blob(m, (0.02, 0.0025, 0.014), (pos[0] + c * L * 0.42, pos[1] + 0.003, pos[2] + s * L * 0.42), mat, 8, 4, uv=None, rot=(0, -ang, 0))


# ================================================================ SPACE RATIONS
@ration("pouch_beef_stew")
def _(m, rng):
    pouch(m, 0.13, 0.185, 0.034, "tex:pouch_stew")
    pouch(m, 0.13, 0.185, 0.034, "tex:pouch_pasta", (0.17, 0.0, 0.03), (0.0, 0.5, 0.0))


@ration("pouch_vegetable_flat")
def _(m, rng):
    slab(m, 0.2, 0.014, 0.14, (0, 0, 0), "tex:pouch_veg", "box", 0.003, warp=lambda x, y, z: (x, y * (1 + 1.8 * (1 - (x / 0.1) ** 2) * (1 - (z / 0.07) ** 2)), z))
    slab(m, 0.2, 0.002, 0.012, (0.0, 0.0, 0.07), "f_pouch_edge", "box", 0.0005)
    slab(m, 0.2, 0.002, 0.012, (0.0, 0.0, -0.07), "f_pouch_edge", "box", 0.0005)
    slab(m, 0.2, 0.014, 0.14, (0.0, 0.03, 0.0), "tex:pouch_oats", "box", 0.003, rot=(0, 0.35, 0), warp=lambda x, y, z: (x, y * (1 + 1.8 * (1 - (x / 0.1) ** 2) * (1 - (z / 0.07) ** 2)), z))


@ration("pouch_fruit_puree_spout")
def _(m, rng):
    pouch(m, 0.09, 0.14, 0.025, "tex:pouch_fruit")
    m.cyl(0.0105, 0.012, (0.0, 0.146, 0.0), "f_pouch_edge", seg=14)
    m.cyl(0.0125, 0.014, (0.0, 0.158, 0.0), "f_cap_red", seg=14)
    pouch(m, 0.09, 0.14, 0.025, "tex:pouch_fruit", (0.1, 0.0, 0.0), (0.0, 0.3, 0.0))
    m.cyl(0.0125, 0.014, (0.1, 0.158, 0.0), "f_cap_gold", seg=14)


@ration("nutrient_tubes_set")
def _(m, rng):
    flat = lambda x, y, zz: (x * (1 + 1.8 * max(0.0, (y - 0.1) / 0.03) ** 2), y, zz * (1 - 0.82 * max(0.0, (y - 0.1) / 0.03) ** 2))
    for k, (tex, cap) in enumerate((("tex:label_tube", "f_cap_red"), ("tex:label_tube_green", "f_cap_green"), ("tex:label_tube", "f_plastic_clear_cap"))):
        z = (k - 1) * 0.045
        lathe(m, [(0.0, 0.0), (0.0105, 0.0), (0.0175, 0.012), (0.0175, 0.12), (0.0175, 0.132), (0.0, 0.132)], (-0.07, 0.0175, z), tex, 22, uv="cyl",
              rot=(0, 0, -PI / 2), warp=flat)
        m.cyl(0.0125, 0.02, (0.075, 0.0175, z), cap, axis="x", seg=14, r2=0.0105)


@ration("protein_bars_stack")
def _(m, rng):
    texs = ("tex:label_bar_choco", "tex:label_bar_oat", "tex:label_bar_berry", "tex:label_bar_choco")
    for k, t in enumerate(texs):
        a = 0.06 * (k - 1.5)
        slab(m, 0.15, 0.013, 0.05, (0.004 * k, 0.014 * k, 0.0), t, "box", 0.003, rot=(0, a, 0))
        for sgn in (-1, 1):
            slab(m, 0.012, 0.005, 0.05, (0.004 * k + sgn * 0.081 * math.cos(a), 0.014 * k + 0.004, -sgn * 0.081 * math.sin(a)), "f_pouch_edge", "box", 0.0005, rot=(0, a, 0))
    # an unwrapped bar and a peeled wrapper
    slab(m, 0.1, 0.014, 0.036, (0.0, 0.0, 0.09), "tex:cookie", "box", 0.003, disp=(0.0008, 90))
    for k in range(4):
        slab(m, 0.0018, 0.0142, 0.036, (-0.03 + 0.02 * k, 0.0, 0.09), "f_chocolate_milk", "box", 0.0003)
    slab(m, 0.06, 0.0015, 0.045, (0.075, 0.0, 0.09), "tex:label_bar_oat", "box", 0.0005, rot=(0.0, 0.2, 0.0))


@ration("freeze_dried_tray")
def _(m, rng):
    y = tray_frame(m, 0.24, 0.16, 0.035, 0.003, "f_tray_blue", xs=(-0.04, 0.045), zs=(), pos=(0, 0, 0))
    blob(m, (0.032, 0.012, 0.062), (-0.08, y + 0.006, 0.0), "tex:pasta", 12, 6, uv="sph", disp=(0.004, 120))
    blob(m, (0.037, 0.012, 0.062), (0.003, y + 0.006, 0.0), "tex:rice_fried", 12, 6, uv="sph", disp=(0.004, 120))
    blob(m, (0.037, 0.013, 0.062), (0.085, y + 0.006, 0.0), "tex:beans", 12, 6, uv="sph", disp=(0.004, 120))
    # sealing film: still stuck down over the right half, peeled and curling up over the left
    slab(m, 0.12, 0.0012, 0.16, (0.06, 0.0345, 0.0), "f_clear_plastic", "box", 0.0003)
    slab(m, 0.1, 0.0012, 0.16, (-0.07, 0.0345, 0.0), "f_clear_plastic", "box", 0.0003, warp=lambda x, yy, z: (x, yy + 0.05 * max(0.0, -x) ** 1.5 * 3, z))


@ration("mre_tray_pasta")
def _(m, rng):
    y = tray_frame(m, 0.2, 0.135, 0.036, 0.0025, "f_foil", pos=(0, 0, 0))
    blob(m, (0.085, 0.022, 0.052), (0.0, y + 0.012, 0.0), "tex:pasta", 20, 8, uv="sph", disp=(0.006, 60))
    blob(m, (0.06, 0.016, 0.034), (0.0, y + 0.02, 0.0), "tex:bolognese", 16, 6, uv="sph", disp=(0.004, 70))
    m.box((0.2, 0.0016, 0.0045), (0.0, 0.038, -0.067), "f_foil", 0.0004)
    spork(m, (0.0, 0.0, 0.095), 0.1)
    slab(m, 0.07, 0.01, 0.1, (0.17, 0.0, 0.0), "tex:label_ration", "box", 0.003, rot=(0, 0.2, 0))
    slab(m, 0.1, 0.012, 0.034, (0.0, 0.0, -0.1), "f_pouch_edge", "box", 0.003)


@ration("ration_brick_pack")
def _(m, rng):
    slab(m, 0.15, 0.04, 0.095, (0, 0, 0), "tex:label_ration", "box", 0.004)
    slab(m, 0.152, 0.0016, 0.096, (0, 0.0215, 0), "f_pouch_edge", "box", 0.0003)
    for k in range(3):
        slab(m, 0.1, 0.018, 0.04, (0.0, 0.019 * k, 0.12), "tex:hash", "box", 0.003, rot=(0, 0.04 * (k - 1), 0.0), disp=(0.0007, 100))
    slab(m, 0.1, 0.0018, 0.012, (0.0, 0.0, 0.098), "f_pouch_edge", "box", 0.0003)


@ration("cup_noodle_instant")
def _(m, rng):
    lathe(m, [(0.031, 0.0), (0.0425, 0.095)], (0, 0.0, 0), "tex:label_cup_noodle", 28, uv="cyl")
    lathe(m, [(0.0, 0.0), (0.031, 0.0)], (0, 0.0, 0), "f_white", 20)
    m.torus(0.0432, 0.0024, (0, 0.0955, 0), "f_white", seg=28, tseg=5)
    lathe(m, [(0.0, 0.0), (0.043, 0.0), (0.0436, 0.0012), (0.0, 0.0012)], (0, 0.0955, 0), "tex:label_cup_noodle", 28, uv="top", arc=TAU * 0.8, a0=0.7)
    slab(m, 0.03, 0.0012, 0.034, (0.036, 0.1, 0.0), "tex:label_cup_noodle", "box", 0.0003, rot=(0.0, 0.0, 0.45))
    spork(m, (0.0, 0.1, 0.0), 0.3, 0.14, "f_white")


@ration("canned_beans_open")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.0365, 0.0), (0.0375, 0.004), (0.0375, 0.0075)], (0, 0.0, 0), "f_steel", 28)
    lathe(m, [(0.0372, 0.0075), (0.0372, 0.105)], (0, 0.0, 0), "tex:label_ration", 28, uv="cyl")
    m.torus(0.0372, 0.0016, (0, 0.1065, 0), "f_steel", seg=28, tseg=4)
    lathe(m, [(0.0, 0.0), (0.0345, 0.0), (0.0345, 0.0008), (0.0, 0.0008)], (0, 0.1, 0.0), "tex:beans", 26, uv="top", disp=(0.0025, 90))
    # lid bent back over its hinge
    lathe(m, [(0.0, 0.0), (0.034, 0.0), (0.034, 0.001), (0.0, 0.001)], (0.0, 0.1065, -0.034), "f_steel", 24, rot=(-1.35, 0.0, 0.0))
    spork(m, (0.12, 0.0, 0.03), 0.4, 0.14, "f_steel")


@ration("ration_boxes_stacked")
def _(m, rng):
    for k in range(3):
        a = 0.06 * (k - 1)
        slab(m, 0.34 - 0.01 * k, 0.1, 0.22, (0.0, 0.1 * k, 0.0), "tex:cardboard_print", "box", 0.004, rot=(0, a, 0))
        slab(m, 0.2, 0.058, 0.002, (0.11 * math.sin(a), 0.1 * k + 0.02, 0.11 * math.cos(a)), "tex:label_ration", "box", 0.0003, rot=(0, a, 0))
        slab(m, 0.34, 0.0016, 0.03, (0.0, 0.1 * k + 0.0995, 0.0), "f_cardboard", "box", 0.0003, rot=(0, a, 0))


@ration("water_pouches_stack")
def _(m, rng):
    for k in range(6):
        a = (0.0 if k % 2 == 0 else PI / 2) + 0.05 * k
        slab(m, 0.11, 0.03, 0.17, (0.0, 0.03 * k, 0.0), "tex:label_water", "box", 0.006, rot=(0, a, 0),
             warp=lambda x, y, z: (x, y * (1 - 0.35 * (x / 0.055) ** 2) * (1 - 0.35 * (z / 0.085) ** 2), z))
    m.cyl(0.009, 0.014, (0.0, 0.03 * 5 + 0.034, 0.0), "f_plastic_clear_cap", seg=10)


@ration("bento_ration_box")
def _(m, rng):
    y = tray_frame(m, 0.24, 0.16, 0.04, 0.003, "f_tray_grey", xs=(0.0,), zs=(0.0,), pos=(0, 0, 0))
    blob(m, (0.044, 0.02, 0.032), (-0.06, y + 0.006, -0.038), "tex:rice", 16, 8, uv="sph", disp=(0.003, 100))
    for k in range(5):
        a = k * 1.3
        blob(m, (0.012, 0.012, 0.012), (-0.06 + 0.02 * math.cos(a), y + 0.012, 0.04 + 0.02 * math.sin(a)), "tex:broccoli", 8, 5, uv="sph")
    slab(m, 0.07, 0.014, 0.05, (0.06, y, -0.036), "tex:steak", "box", 0.004, disp=(0.0012, 60))
    for k in range(4):
        blob(m, (0.02, 0.008, 0.012), (0.045 + 0.016 * (k % 2), y + 0.008, 0.032 + 0.018 * (k // 2)), "f_juice_orange", 10, 5, uv=None, rot=(0, k, 0))
    slab(m, 0.24, 0.006, 0.16, (0.0, 0.0, 0.18), "f_tray_blue", "box", 0.003)
    spork(m, (0.0, 0.0, -0.1), 0.0, 0.18, "f_cap_black")


# ================================================================ SERVING TRAYS
@tray("meal_tray_steel")
def _(m, rng):
    y = tray_frame(m, 0.42, 0.3, 0.03, 0.003, "f_tray", xs=(-0.045, 0.09), zs=(0.0,), pos=(0, 0, 0))
    # compartments: mash, peas, meat on the left half; roll, fruit on the right; milk carton in the corner
    blob(m, (0.05, 0.02, 0.05), (-0.15, y + 0.01, -0.07), "f_cream", 14, 8, uv=None, disp=(0.003, 70))
    for k in range(14):
        a = k * 2.399
        blob(m, (0.006, 0.006, 0.006), (-0.15 + 0.02 * math.sqrt(k / 14) * math.cos(a) * 1.4, y + 0.008, 0.07 + 0.02 * math.sqrt(k / 14) * math.sin(a) * 1.4), "f_pea", 6, 4, uv=None)
    slab(m, 0.075, 0.016, 0.052, (0.0, y, -0.07), "tex:steak", "box", 0.004, disp=(0.0012, 60), rot=(0, 0.15, 0))
    blob(m, (0.032, 0.022, 0.026), (0.0, y + 0.012, 0.075), "tex:bread_crust", 14, 8, uv="sph", disp=(0.002, 60))
    vessel(m, bowl_outer(0.04, 0.03, 0.4, 5), 0.002, (0.15, y, 0.065), "f_plate_blue", 18)
    for k in range(6):
        blob(m, (0.008, 0.008, 0.008), (0.15 + 0.014 * math.cos(k * 1.1), y + 0.026, 0.065 + 0.014 * math.sin(k * 1.1)), "tex:blueberry" if k % 2 else "tex:cherry", 6, 4, uv="sph")
    slab(m, 0.06, 0.1, 0.06, (0.145, y, -0.08), "tex:label_milk", "box", 0.003)
    spork(m, (-0.18, y + 0.0, 0.13), 0.2, 0.15, "f_steel")


@tray("meal_tray_brig")
def _(m, rng):
    y = tray_frame(m, 0.38, 0.27, 0.025, 0.003, "f_tray_grey", xs=(0.04,), zs=(0.0,), pos=(0, 0, 0))
    blob(m, (0.075, 0.014, 0.05), (-0.09, y + 0.006, -0.06), "tex:porridge", 14, 6, uv="sph", disp=(0.004, 80))
    blob(m, (0.075, 0.012, 0.05), (-0.09, y + 0.006, 0.07), "tex:beans", 14, 6, uv="sph", disp=(0.004, 80))
    blob(m, (0.05, 0.014, 0.05), (0.12, y + 0.007, -0.06), "tex:rice", 12, 6, uv="sph", disp=(0.004, 80))
    blob(m, (0.026, 0.026, 0.026), (0.12, y + 0.02, 0.07), "tex:apple_green", 14, 10, uv="sph", disp=(0.001, 60))
    spork(m, (0.0, y, 0.14), 0.0, 0.14, "f_tray_grey")


@tray("breakfast_tray_wood")
def _(m, rng):
    slab(m, 0.5, 0.015, 0.34, (0, 0, 0), "tex:wood_board", "box", 0.004)
    for sx in (-1, 1):
        slab(m, 0.02, 0.025, 0.34, (sx * 0.24, 0.015, 0.0), "tex:wood_board", "box", 0.004)
    y = 0.015
    plate(m, 0.1, "f_plate", (-0.1, y, 0.0), seg=26)
    lathe(m, [(0, 0), (0.036, 0), (0.04, 0.001), (0.037, 0.003), (0, 0.0035)], (-0.12, y + 0.008, -0.01), "tex:egg_white", 22, uv="top", warp=wobble(5, 0.3, 0.12))
    dome(m, 0.0125, 0.01, (-0.118, y + 0.0115, -0.012), "f_yolk", 14, 5, uv=None)
    slab(m, 0.05, 0.011, 0.05, (-0.07, y + 0.008, 0.03), "tex:bread_crust", "box", 0.004, rot=(0, 0.3, 0))
    outer = [(0.0, 0.0), (0.028, 0.0), (0.03, 0.008), (0.034, 0.1), (0.036, 0.12)]
    vessel(m, outer, 0.003, (0.08, y, -0.08), "f_glass", 24)
    lathe(m, [(0, 0.003), (0.028, 0.004), (0.0315, 0.01), (0.0345, 0.1), (0.0, 0.1)], (0.08, y, -0.08), "f_juice_orange", 22)
    cup = [(0.0, 0.0), (0.026, 0.0), (0.03, 0.004), (0.04, 0.03), (0.048, 0.055), (0.05, 0.066)]
    sy = y + 0.006
    lathe(m, [(0.0, 0.0), (0.04, 0.0), (0.045, 0.003), (0.075, 0.012), (0.075, 0.0138), (0.06, 0.0138), (0.04, 0.006), (0.0, 0.006)], (0.1, y, 0.06), "f_plate_sage", 28)
    vessel(m, cup, 0.0028, (0.1, sy + y - y, 0.06), "f_plate_sage", 26)
    lathe(m, [(0.0, 0.0), (0.0455, 0.0), (0.0455, 0.0006), (0.0, 0.0006)], (0.1, sy + 0.056, 0.06), "tex:latte_swirl", 24, uv="top")
    for k in range(3):
        blob(m, (0.012, 0.012, 0.012), (0.17, y + 0.012, -0.09 + 0.026 * k), "tex:strawberry", 8, 6, uv="sph")
    sprig(m, (0.17, y + 0.026, -0.0), "tex:leaf_mint", 3, 0.012, rng)


@tray("drinks_tray_round")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.15, 0.0), (0.162, 0.006), (0.164, 0.018), (0.158, 0.018), (0.15, 0.01), (0.0, 0.008)], (0, 0, 0), "f_steel", 40)
    y = 0.008
    spots = ((0.065, 0.0), (-0.065, 0.0), (0.0, 0.07), (0.0, -0.07))
    specs = (("f_water", 0.0), ("f_juice_orange", 0.0), ("f_soda_dark", 0.0), ("f_wine_red", 1.0))
    for k, ((x, z), (mat, wine)) in enumerate(zip(spots, specs)):
        if wine:
            lathe(m, [(0.0, 0.0), (0.03, 0.0), (0.031, 0.002), (0.004, 0.008), (0.004, 0.07)], (x, y, z), "f_glass", 22)
            outer = [(0.0, 0.07), (0.008, 0.072), (0.03, 0.095), (0.032, 0.12), (0.025, 0.15), (0.022, 0.158)]
            vessel(m, outer, 0.0015, (x, y, z), "f_glass", 24)
            lathe(m, [(0.0, 0.076), (0.027, 0.098), (0.0295, 0.118), (0.0, 0.118)], (x, y, z), mat, 22)
        else:
            outer = [(0.0, 0.0), (0.028, 0.0), (0.03, 0.01), (0.034, 0.12), (0.035, 0.13)]
            vessel(m, outer, 0.003, (x, y, z), "f_glass", 22)
            lathe(m, [(0, 0.004), (0.026, 0.004), (0.029, 0.01), (0.032, 0.105), (0.0, 0.105)], (x, y, z), mat, 20)
            if k == 2:
                m.box((0.017, 0.017, 0.017), (x + 0.004, y + 0.09, z), "f_ice_cube", 0.002, rot=(0.3, 0.4, 0.2))
                m.box((0.017, 0.017, 0.017), (x - 0.008, y + 0.08, z + 0.01), "f_ice_cube", 0.002, rot=(0.1, 0.9, 0.2))


@tray("cloche_hot_dish")
def _(m, rng):
    plate(m, 0.15, "f_plate", seg=34, rim="f_cap_gold")
    y = 0.008
    blob(m, (0.06, 0.016, 0.044), (-0.04, y + 0.013, 0.0), "tex:steak", 18, 8, uv="box", disp=(0.002, 40), rot=(0, 0.4, 0))
    blob(m, (0.025, 0.02, 0.025), (0.06, y + 0.015, 0.03), "f_cream", 14, 8, uv=None, disp=(0.002, 70))
    for k in range(5):
        tube3(m, [(0.02 + 0.0 * k, y + 0.006, -0.06 + 0.012 * k), (0.045, y + 0.009, -0.058 + 0.012 * k), (0.07, y + 0.006, -0.06 + 0.012 * k)], 0.0035, "f_bean_green", 5)
    # lifted cloche leaning on its rim beside the plate
    lathe(m, [(0.14, 0.0), (0.145, 0.012), (0.138, 0.06), (0.1, 0.11), (0.05, 0.14), (0.0, 0.146)], (0.0, y + 0.0, 0.0), "f_steel", 40)
    m.torus(0.1425, 0.003, (0.0, y + 0.002, 0.0), "f_steel", seg=40, tseg=5)
    blob(m, (0.018, 0.014, 0.018), (0.0, y + 0.153, 0.0), "f_steel", 14, 9, uv=None)
    m.cyl(0.006, 0.01, (0.0, y + 0.146, 0.0), "f_steel", seg=10)


@tray("bread_basket_wicker")
def _(m, rng):
    outer = [(0.0, 0.0), (0.09, 0.0), (0.12, 0.03), (0.145, 0.07), (0.15, 0.085)]
    lathe(m, [(0.0, 0.0), (0.09, 0.0), (0.12, 0.03), (0.145, 0.07), (0.15, 0.085), (0.146, 0.085), (0.116, 0.036), (0.086, 0.006), (0.0, 0.006)], (0, 0, 0), "tex:wicker", 32, uv="cyl", tile=(3, 1))
    m.torus(0.148, 0.005, (0, 0.085, 0), "f_wood_dark", seg=32, tseg=6)
    lathe(m, [(0.0, 0.0), (0.13, 0.0), (0.138, 0.004), (0.0, 0.004)], (0, 0.012, 0), "f_napkin", 28, warp=wobble(9, 0.0, 0.05))
    for k, (x, z) in enumerate(((-0.05, -0.03), (0.04, -0.05), (0.06, 0.04), (-0.04, 0.05))):
        blob(m, (0.042, 0.03, 0.034), (x, 0.032, z), "tex:bread_crust", 16, 10, uv="sph", disp=(0.002, 50), rot=(0, k, 0))
    blob(m, (0.04, 0.026, 0.03), (0.0, 0.058, 0.0), "tex:bread_crust", 16, 10, uv="sph", disp=(0.002, 50), rot=(0, 0.5, 0))


@tray("fruit_bowl_mixed")
def _(m, rng):
    R = 0.17
    vessel(m, bowl_outer(R, 0.09, 0.4, 8), 0.005, (0, 0, 0), "f_plate_cream", 34)
    apple = smooth_prof([(0, 0.1), (0.4, 0.0), (0.8, 0.12), (0.99, 0.42), (0.98, 0.68), (0.82, 0.9), (0.5, 0.99), (0.2, 0.93), (0, 0.8)], 1)
    for k, (x, z, mat) in enumerate(((-0.06, -0.04, "tex:apple_red"), (0.05, -0.06, "tex:apple_green"), (0.07, 0.05, "tex:apple_red"))):
        lathe(m, scaled(apple, 0.04, 0.075), (x, 0.045, z), mat, 14, uv="sph", rot=(0.0, k, 0.0))
    for k, (x, z) in enumerate(((-0.07, 0.06), (0.0, 0.02))):
        blob(m, (0.036, 0.034, 0.036), (x, 0.08 + 0.0 * k, z), "tex:orange_peel", 16, 10, uv="sph")
    for k in range(3):
        lathe(m, [(0.0, 0.0)] + [(0.0095 + 0.0105 * math.sin(PI * (0.08 + 0.84 * i / 8)) ** 0.7, 0.18 * i / 8) for i in range(1, 8)] + [(0.0, 0.18)], (-0.12 + 0.0, 0.07 + 0.012 * k, -0.02 + 0.03 * k), "tex:banana_skin", 5, uv="cyl", rot=(0.0, 0.0, -1.3 + 0.05 * k), warp=lambda x, y, z: (x + 0.03 * (y / 0.18) ** 2, y, z))
    for (x, y, z) in heap(rng, 14, 0.05, 0.02, 0.4):
        blob(m, (0.01, 0.01, 0.01), (0.04 + x, 0.115 + y, 0.0 + z), "tex:grape_skin", 6, 4, uv="sph")
    blob(m, (0.032, 0.05, 0.032), (0.0, 0.1, -0.1), "tex:pear_skin", 12, 8, uv="sph")


@tray("hotel_pan_mash_gravy")
def _(m, rng):
    y = tray_frame(m, 0.53, 0.325, 0.065, 0.003, "f_steel", pos=(0, 0, 0))
    for sx in (-1, 1):
        m.box((0.02, 0.003, 0.325), (sx * 0.2715, 0.0625, 0.0), "f_steel", 0.001)
    for sz in (-1, 1):
        m.box((0.55, 0.003, 0.02), (0.0, 0.0625, sz * 0.1725), "f_steel", 0.001)
    lathe(m, [(0.0, 0.0), (0.12, 0.0), (0.13, 0.02), (0.1, 0.05), (0.0, 0.058)], (-0.07, y, 0.0), "f_cream", 30, scale=(1.5, 1.0, 1.0), disp=(0.004, 40))
    lathe(m, [(0.0, 0.0), (0.06, 0.0), (0.06, 0.0008), (0.0, 0.0008)], (-0.07, y + 0.057, 0.0), "f_caramel", 24, scale=(1.4, 1.0, 1.0), warp=wobble(5, 0.4, 0.15))
    for k in range(6):
        blob(m, (0.026, 0.016, 0.022), (0.16 + 0.02 * (k % 2), y + 0.012 + 0.012 * (k // 3), -0.08 + 0.055 * (k % 3)), "tex:potato_skin", 10, 6, uv="sph", disp=(0.003, 40))
    m.link((-0.02, y + 0.07, 0.0), (0.2, y + 0.07, 0.17), 0.0035, "f_steel", 5)


@tray("hotel_pan_roast_veg")
def _(m, rng):
    y = tray_frame(m, 0.53, 0.325, 0.065, 0.003, "f_steel", pos=(0, 0, 0))
    for sx in (-1, 1):
        m.box((0.02, 0.003, 0.325), (sx * 0.2715, 0.0625, 0.0), "f_steel", 0.001)
    for sz in (-1, 1):
        m.box((0.55, 0.003, 0.02), (0.0, 0.0625, sz * 0.1725), "f_steel", 0.001)
    for k in range(44):
        a = k * 2.399
        x = 0.22 * math.sqrt((k + 0.5) / 44) * math.cos(a) * 1.15
        z = 0.12 * math.sqrt((k + 0.5) / 44) * math.sin(a) * 1.2
        mat = ("tex:carrot", "tex:potato_skin", "tex:broccoli", "tex:pepper_red", "tex:pepper_yellow", "tex:onion_red")[k % 6]
        s = 0.016 + 0.004 * (k % 3)
        blob(m, (s * 1.4, s, s), (x, y + 0.012 + 0.014 * (1 - (x / 0.25) ** 2) * (k % 3) * 0.5, z), mat, 7, 5, uv="sph", rot=(0, k, 0), disp=(0.002, 60))
    tube3(m, spline([(0.0, y + 0.06, 0.15), (0.1, y + 0.08, 0.2), (0.24, y + 0.07, 0.19)], 3), 0.003, "f_steel", 5)


@tray("soup_tureen_ladle")
def _(m, rng):
    body = smooth_prof([(0.0, 0.0), (0.06, 0.0), (0.11, 0.03), (0.13, 0.08), (0.12, 0.13), (0.1, 0.145)], 3)
    lathe(m, body, (0, 0.0, 0), "f_plate_cream", 32, scale=(1.2, 1.0, 0.85))
    lathe(m, [(0.0, 0.0), (0.09, 0.0), (0.09, 0.001), (0.0, 0.001)], (0.0, 0.132, 0.0), "tex:soup_green", 26, uv="top", scale=(1.2, 1.0, 0.85))
    lathe(m, [(0.0, 0.0), (0.096, 0.0), (0.098, 0.01), (0.075, 0.042), (0.0, 0.052)], (0.0, 0.146, -0.0), "f_plate_cream", 28, scale=(1.2, 1.0, 0.85), warp=lambda x, yy, z: (x, yy, z))
    blob(m, (0.012, 0.012, 0.012), (0.0, 0.2, 0.0), "f_plate_cream", 10, 8, uv=None)
    for sgn in (-1, 1):
        tube3(m, spline([(sgn * 0.146, 0.1, 0.0), (sgn * 0.175, 0.112, 0.0), (sgn * 0.172, 0.082, 0.0), (sgn * 0.142, 0.07, 0.0)], 4), 0.006, "f_plate_cream", 7)
    m.link((0.04, 0.16, 0.02), (0.24, 0.2, 0.18), 0.004, "f_steel", 5)
    vessel(m, [(0.0, 0.0), (0.025, 0.0), (0.03, 0.02)], 0.002, (0.24, 0.185, 0.18), "f_steel", 18)


@tray("cake_stand_afternoon_tea")
def _(m, rng):
    for k, (r, y) in enumerate(((0.15, 0.0), (0.115, 0.14), (0.085, 0.27))):
        lathe(m, [(0.0, 0.0), (r, 0.0), (r + 0.004, 0.003), (r, 0.006), (0.0, 0.006)], (0, y, 0), "f_plate_cream", 34)
        m.torus(r + 0.001, 0.003, (0, y + 0.003, 0), "f_cap_gold", seg=34, tseg=5)
    m.cyl(0.005, 0.4, (0, 0.2, 0), "f_cap_gold", seg=10)
    blob(m, (0.012, 0.012, 0.012), (0.0, 0.41, 0.0), "f_cap_gold", 10, 8, uv=None)
    # bottom tier: scones and jam; middle: sandwiches; top: cakes
    for k in range(4):
        a = k * TAU / 4 + 0.4
        blob(m, (0.032, 0.022, 0.032), (0.085 * math.cos(a), 0.0285, 0.085 * math.sin(a)), "tex:bread_crust", 14, 8, uv="sph", disp=(0.002, 60))
    for k in range(5):
        a = k * TAU / 5 + 0.2
        m.prism([(-0.03, -0.03), (0.03, -0.03), (-0.03, 0.03)], 0.012, (0.07 * math.cos(a) - 0.0, 0.146, 0.07 * math.sin(a)), "f_dough", "xz", rot=(0, a, 0))
        m.prism([(-0.03, -0.03), (0.03, -0.03), (-0.03, 0.03)], 0.004, (0.07 * math.cos(a), 0.158, 0.07 * math.sin(a)), "f_herb", "xz", rot=(0, a, 0))
    for k in range(5):
        a = k * TAU / 5
        lathe(m, [(0.0, 0.0), (0.016, 0.0), (0.0185, 0.03), (0.0, 0.03)], (0.05 * math.cos(a), 0.276, 0.05 * math.sin(a)), "f_icing_pink" if k % 2 else "f_icing_choc", 12)
        blob(m, (0.007, 0.007, 0.007), (0.05 * math.cos(a), 0.309, 0.05 * math.sin(a)), "tex:cherry", 8, 6, uv="sph")


@tray("coffee_set_tray")
def _(m, rng):
    slab(m, 0.46, 0.012, 0.32, (0, 0, 0), "tex:wood_walnut", "box", 0.004)
    y = 0.012
    body = smooth_prof([(0.0, 0.0), (0.045, 0.0), (0.065, 0.04), (0.06, 0.11), (0.04, 0.17), (0.034, 0.185)], 3)
    lathe(m, body, (-0.12, y, 0.0), "f_steel", 26)
    lathe(m, [(0.034, 0.185), (0.036, 0.19), (0.0, 0.205)], (-0.12, y, 0.0), "f_steel", 22)
    tube3(m, spline([(-0.065, y + 0.06, 0.0), (-0.04, y + 0.11, 0.0), (-0.066, y + 0.165, 0.0)], 4), 0.006, "f_cap_black", 7)
    tube3(m, spline([(-0.17, y + 0.07, 0.0), (-0.19, y + 0.14, 0.0), (-0.172, y + 0.185, 0.0)], 3), 0.009, "f_steel", 8)
    cup = [(0.0, 0.0), (0.026, 0.0), (0.03, 0.004), (0.04, 0.03), (0.046, 0.05), (0.047, 0.055)]
    for k, (cx, cz) in enumerate(((0.06, -0.07), (0.06, 0.07))):
        lathe(m, [(0.0, 0.0), (0.04, 0.0), (0.045, 0.003), (0.07, 0.011), (0.07, 0.0128), (0.058, 0.0128), (0.04, 0.006), (0.0, 0.006)], (cx, y, cz), "f_plate", 26)
        vessel(m, cup, 0.0026, (cx, y + 0.006, cz), "f_plate", 24)
        lathe(m, [(0.0, 0.0), (0.0425, 0.0), (0.0425, 0.0006), (0.0, 0.0006)], (cx, y + 0.006 + 0.046, cz), "tex:latte_rosetta" if k else "tex:coffee_black", 22, uv="top")
        handle(m, [(cx + 0.046, y + 0.052, cz), (cx + 0.064, y + 0.054, cz), (cx + 0.066, y + 0.036, cz), (cx + 0.054, y + 0.02, cz), (cx + 0.04, y + 0.022, cz)], 0.003)
    vessel(m, [(0.0, 0.0), (0.022, 0.0), (0.03, 0.05), (0.032, 0.07)], 0.003, (0.19, y, -0.06), "f_plate", 20)
    vessel(m, bowl_outer(0.034, 0.045, 0.4, 5), 0.003, (0.18, y, 0.08), "f_plate", 20)
    for k in range(6):
        m.box((0.011, 0.011, 0.011), (0.18 + 0.01 * (k % 3) - 0.01, y + 0.03 + 0.011 * (k // 3), 0.08 + 0.008 * (k % 2)), "f_icing_white", 0.001, rot=(0, k, 0))


# ================================================================ BUFFET AND DISPLAY FURNITURE (floor)
@buffet("bakery_display_stand")
def _(m, rng):
    W, D, H = 0.9, 0.5, 1.45
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.04, H, 0.04), (sx * (W / 2 - 0.02), H / 2, sz * (D / 2 - 0.02)), "f_wood_dark", 0.004)
    for k, y in enumerate((0.25, 0.65, 1.05)):
        m.box((W, 0.025, D), (0, y, 0), "f_wood_light", 0.004)
        m.box((W, 0.06, 0.02), (0, y + 0.04, D / 2 - 0.01), "f_wood_light", 0.003)
    m.box((W + 0.04, 0.03, D + 0.04), (0, 1.465, 0), "f_wood_dark", 0.005)
    # shelf 1: baguettes in a bucket + loaves; shelf 2: boules and rolls; shelf 3: croissants and pastries on trays
    for k in range(5):
        lathe(m, [(0.0, 0.0)] + [(0.034 * math.sin(PI * i / 12) ** 0.3, 0.55 * i / 12) for i in range(1, 12)] + [(0.0, 0.55)], (-0.3 + 0.045 * k, 0.77 + 0.0, -0.1), "tex:bread_crust", 12,
              uv="cyl", rot=(0.12 * (k - 2), 0.0, 0.1 * (k - 2)), disp=(0.002, 30))
    for k in range(3):
        blob(m, (0.14, 0.055, 0.075), (0.2, 0.31, -0.1 + 0.1 * k), "tex:bread_crust", 16, 8, uv="sph", disp=(0.003, 14))
    for k in range(6):
        blob(m, (0.085, 0.07, 0.085), (-0.3 + 0.18 * (k % 3), 0.74, -0.12 + 0.2 * (k // 3) + 0.0), "tex:bread_crust", 16, 10, uv="sph", disp=(0.003, 22))
    for k in range(8):
        blob(m, (0.035, 0.028, 0.035), (-0.38 + 0.11 * (k % 4) * 1.0 + 0.0, 1.1 + 0.0, -0.1 + 0.2 * (k // 4)), "tex:croissant", 10, 6, uv="sph", disp=(0.002, 40))
    for k in range(5):
        blob(m, (0.065, 0.02, 0.065), (0.2, 1.088, -0.1 + 0.1 * k if k < 3 else 0.0), "tex:pie_crust", 14, 6, uv="sph") if k < 3 else None


@buffet("fruit_market_stand")
def _(m, rng):
    W, D = 1.2, 0.9
    for sx in (-1, 1):
        m.box((0.05, 0.7, 0.8), (sx * (W / 2 - 0.025), 0.35, 0.0), "f_wood_dark", 0.005)
    for k, (y, tilt, zc) in enumerate(((0.28, 0.2, -0.25), (0.5, 0.2, 0.05))):
        m.box((W - 0.05, 0.03, 0.44), (0.0, y, zc), "f_wood_light", 0.004, rot=(-tilt, 0, 0))
        m.box((W - 0.05, 0.06, 0.03), (0.0, y - 0.01, zc + 0.2), "f_wood_light", 0.004)
    m.box((W - 0.05, 0.03, 0.44), (0.0, 0.06, 0.25), "f_wood_light", 0.004)
    mats = ("tex:apple_red", "tex:orange_peel", "tex:apple_green", "tex:lemon_peel", "tex:tomato_skin")
    for tier, (y, zc) in enumerate(((0.33, -0.25), (0.55, 0.05), (0.12, 0.27))):
        for k in range(9):
            for q in range(3 if tier < 2 else 2):
                x = -0.5 + k * 0.125
                z = zc - 0.15 + q * 0.11 + 0.0
                blob(m, (0.05, 0.05, 0.05), (x, y + 0.045 + 0.0 + (0.03 if (k + q) % 2 else 0.0), z), mats[(k // 2 + q + tier) % 5], 9, 6, uv="sph")
    m.box((W, 0.06, 0.02), (0.0, 0.9, -0.38), "f_wood_dark", 0.003)
    m.box((0.04, 0.9, 0.04), (-W / 2 + 0.02, 0.45, -0.38), "f_wood_dark", 0.003)
    m.box((0.04, 0.9, 0.04), (W / 2 - 0.02, 0.45, -0.38), "f_wood_dark", 0.003)


@buffet("dessert_display_case")
def _(m, rng):
    W, D, H = 1.2, 0.6, 1.1
    m.box((W, 0.5, D), (0, 0.25, 0), "f_steel_dark", 0.01)
    m.box((W - 0.04, 0.03, D - 0.04), (0, 0.515, 0), "f_white", 0.004)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((0.02, 0.58, 0.02), (sx * (W / 2 - 0.01), 0.8, sz * (D / 2 - 0.01)), "f_steel", 0.002)
    m.box((W, 0.025, D), (0, 1.1, 0), "f_steel", 0.004)
    m.box((W - 0.04, 0.58, 0.004), (0, 0.8, D / 2 - 0.002), "f_glass", 0.0)
    m.box((W - 0.04, 0.58, 0.004), (0, 0.8, -D / 2 + 0.002), "f_glass", 0.0)
    m.box((0.004, 0.58, D - 0.04), (W / 2 - 0.002, 0.8, 0.0), "f_glass", 0.0)
    m.box((0.004, 0.58, D - 0.04), (-W / 2 + 0.002, 0.8, 0.0), "f_glass", 0.0)
    m.box((W - 0.04, 0.012, D - 0.06), (0, 0.8, 0.0), "f_glass", 0.0)
    for k, (x, y) in enumerate(((-0.4, 0.53), (0.0, 0.53), (0.4, 0.53), (-0.3, 0.82), (0.3, 0.82))):
        lathe(m, [(0.0, 0.0), (0.1, 0.0), (0.1, 0.004), (0.0, 0.004)], (x, y, 0.0), "f_plate", 24)
        if k % 3 == 0:
            lathe(m, [(0.0, 0.0), (0.085, 0.0), (0.085, 0.03), (0.0, 0.03)], (x, y + 0.004, 0.0), "tex:sponge", 24, uv="cyl")
            lathe(m, [(0.0, 0.0), (0.09, 0.0), (0.09, 0.012), (0.0, 0.014)], (x, y + 0.034, 0.0), "f_icing_pink", 24, warp=wobble(8, 0.0, 0.03))
            blob(m, (0.012, 0.012, 0.012), (x, y + 0.054, 0.0), "tex:cherry", 8, 6, uv="sph")
        elif k % 3 == 1:
            lathe(m, [(0.0, 0.0), (0.085, 0.0), (0.087, 0.03), (0.0, 0.03)], (x, y + 0.004, 0.0), "tex:pie_crust", 24, uv="top", warp=wobble(24, 0.0, 0.02))
            for q in range(10):
                a = q * 2.399
                blob(m, (0.012, 0.012, 0.012), (0.06 * math.sqrt(q / 10) * math.cos(a), y + 0.04, 0.06 * math.sqrt(q / 10) * math.sin(a)), "tex:strawberry", 7, 5, uv="sph")
        else:
            for q in range(6):
                a = q * TAU / 6
            for q in range(7):
                a = q * TAU / 7
                lathe(m, [(0.0, 0.0), (0.02, 0.0), (0.022, 0.03), (0.0, 0.03)], (x + 0.055 * math.cos(a), y + 0.004, 0.055 * math.sin(a)), "f_icing_choc" if q % 2 else "f_icing_white", 12)


@buffet("chafing_buffet_line")
def _(m, rng):
    W, D = 1.9, 0.7
    m.box((W, 0.82, D), (0, 0.41, 0), "f_steel_dark", 0.008)
    m.box((W + 0.06, 0.04, D + 0.06), (0, 0.84, 0), "f_steel", 0.006)
    # four hot pans in warmers, each with a different dish
    dishes = ("tex:curry", "tex:rice", "tex:soup_tomato", "tex:cheese_sauce")
    for k in range(4):
        x = -0.69 + 0.46 * k
        m.box((0.43, 0.06, 0.3), (x, 0.88, 0.0), "f_steel", 0.006)
        slab(m, 0.38, 0.03, 0.25, (x, 0.88, 0.0), dishes[k], "box", 0.01, disp=(0.004, 30))
        m.link((x + 0.1, 0.99, 0.0), (x + 0.2, 1.01, 0.12), 0.004, "f_steel", 5)
    # sneeze guard
    for sx in (-1, 1):
        m.box((0.03, 0.4, 0.03), (sx * (W / 2 - 0.05), 1.07, D / 2 - 0.08), "f_steel", 0.003)
    m.box((W - 0.1, 0.32, 0.01), (0.0, 1.15, D / 2 - 0.08), "f_glass", 0.0, rot=(0.25, 0, 0))
    m.box((W - 0.06, 0.03, 0.05), (0.0, 1.27, D / 2 - 0.08), "f_steel", 0.003)
    for k in range(10):
        a = k * 0.8
    for k in range(4):
        lathe(m, [(0.0, 0.0), (0.1, 0.0), (0.11, 0.012), (0.0, 0.012)], (0.8 + 0.0, 0.84 + 0.0 + 0.012 * k, 0.1), "f_plate", 24) if k == 3 and False else None
    for k in range(5):
        lathe(m, [(0.0, 0.0), (0.09, 0.0), (0.1, 0.012), (0.0, 0.012)], (-0.82, 0.86 + 0.014 * k, -0.28), "f_plate", 20)


menu.register()
