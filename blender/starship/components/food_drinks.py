"""Realistic drink models: coffee and tea, glasses, cans, bottles, cocktails (transparent glass / liquids + printed labels)."""
import math

from .food import slab, wobble
from .foodkit import Menu, blob, disc, dome, lathe, smooth_prof, spline, sprig, tube3, vessel

menu = Menu()
drink = menu.cat("drink", tags=("food", "drink"))
can = menu.cat("can", tags=("food", "drink", "can"))
bottle = menu.cat("bottle", tags=("food", "drink", "bottle"))
cocktail = menu.cat("cocktail", tags=("food", "drink", "glass"))


# ---------------------------------------------------------------- helpers
def cut_prof(outer, level):
    """Part of an outline (bottom-centre -> rim) below height `level`, ending exactly at `level`."""
    out = []
    for (r0, y0), (r1, y1) in zip(outer[:-1], outer[1:]):
        if not out:
            out.append((r0, y0))
        if y1 <= level:
            out.append((r1, y1))
        else:
            if y1 > y0:
                t = (level - y0) / (y1 - y0)
                out.append((r0 + (r1 - r0) * t, level))
            break
    return out


def fill(m, outer, t, level, mat, pos=(0, 0, 0), seg=24, top=None, inset=0.0004, uv_top="top", disp=None):
    """Liquid filling a vessel (outer profile, wall t) up to height `level`; `top` = optional opaque textured surface material."""
    prof = cut_prof(outer, level)
    body = [(0.0, prof[0][1] + t)] + [(max(r - t - inset, 0.0), max(y, prof[0][1] + t)) for r, y in prof[1:]]
    body.append((0.0, level))
    lathe(m, body, pos, mat, seg)
    if top:
        r = max(prof[-1][0] - t - inset, 0.001)
        lathe(m, [(0.0, 0.0), (r, 0.0), (r, 0.0006), (0.0, 0.0006)], (pos[0], pos[1] + level - 0.0004, pos[2]), top, seg, uv=uv_top, disp=disp)
    return max(prof[-1][0] - t - inset, 0.001)


def handle(m, pts, r=0.0035, mat="f_plate"):
    tube3(m, spline(pts, 5), r, mat, 7, caps=True)


def saucer(m, r=0.075, pos=(0, 0, 0), mat="f_plate"):
    lathe(m, [(0.0, 0.0), (r * 0.5, 0.0), (r * 0.58, 0.003), (r, 0.012), (r, 0.0138), (r * 0.9, 0.0138), (r * 0.55, 0.006), (0.0, 0.006)], pos, mat, 30)
    return pos[1] + 0.006


def ice_cubes(m, rng, n, rx, rz, y0, y1, size=0.019):
    for k in range(n):
        a = k * 2.399
        d = math.sqrt((k + 0.5) / n)
        m.box((size, size, size), (rx * d * math.cos(a), y0 + (y1 - y0) * ((k * 0.618) % 1.0), rz * d * math.sin(a)), "f_ice_cube", 0.002, rot=(0.4 * k, 0.7 * k, 0.3 * k))


def straw(m, base, top, mat="f_straw", r=0.0028):
    tube3(m, [base, ((base[0] + top[0]) / 2, (base[1] + top[1]) / 2, (base[2] + top[2]) / 2), top], r, mat, 6, caps=False)


# ================================================================ DRINKS: cups, mugs, glasses
CUP = [(0.0, 0.0), (0.026, 0.0), (0.03, 0.004), (0.04, 0.03), (0.048, 0.055), (0.05, 0.066)]


@drink("latte_art_cup")
def _(m, rng):
    y = saucer(m, 0.078)
    vessel(m, CUP, 0.0028, (0, y, 0), "f_plate", 30)
    fill(m, CUP, 0.0028, 0.056, "f_coffee_iced", (0, y, 0), 28, top="tex:latte_heart", inset=0.0)
    handle(m, [(0.048, y + 0.05, 0.0), (0.072, y + 0.052, 0.0), (0.076, y + 0.032, 0.0), (0.062, y + 0.016, 0.0), (0.04, y + 0.018, 0.0)])
    m.link((-0.025, y + 0.002, 0.058), (0.04, y + 0.002, 0.058), 0.0022, "f_steel", 5)


@drink("cappuccino_rosetta")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.034, 0.004), (0.05, 0.035), (0.058, 0.06), (0.06, 0.07)]
    y = saucer(m, 0.09, mat="f_plate_cream")
    vessel(m, outer, 0.003, (0, y, 0), "f_plate_cream", 32)
    fill(m, outer, 0.003, 0.062, "f_coffee_iced", (0, y, 0), 30, top="tex:latte_rosetta", inset=0.0)
    handle(m, [(0.056, y + 0.06, 0.0), (0.082, y + 0.062, 0.0), (0.087, y + 0.04, 0.0), (0.07, y + 0.02, 0.0), (0.045, y + 0.022, 0.0)], 0.004, "f_plate_cream")
    slab(m, 0.03, 0.007, 0.018, (0.0, y, 0.062), "tex:cookie", "box", 0.002, rot=(0, 0.3, 0))


@drink("latte_macchiato_glass")
def _(m, rng):
    outer = [(0.0, 0.0), (0.032, 0.0), (0.033, 0.004), (0.036, 0.1), (0.038, 0.15)]
    saucer(m, 0.075, (0, 0, 0), "f_steel")
    y = 0.006
    vessel(m, outer, 0.0025, (0, y, 0), "f_glass", 28)
    fill(m, outer, 0.0025, 0.07, "f_coffee_iced", (0, y, 0), 26)
    lathe(m, [(0, 0), (0.0338, 0), (0.0348, 0.045), (0.0, 0.045)], (0, y + 0.07, 0), "f_milk", 26)
    lathe(m, [(0.0, 0.0), (0.0352, 0.0), (0.0358, 0.018), (0.0, 0.022)], (0, y + 0.115, 0), "tex:milk_froth", 26, uv="cyl", disp=(0.0008, 90))
    m.link((0.012, y + 0.02, 0.012), (0.02, y + 0.17, 0.0), 0.0016, "f_steel", 5)
    blob(m, (0.012, 0.0025, 0.007), (0.0225, y + 0.172, 0.0), "f_steel", 10, 5, uv=None, rot=(0, 0, -0.05))


@drink("espresso_cup_sugar")
def _(m, rng):
    outer = [(0.0, 0.0), (0.019, 0.0), (0.022, 0.003), (0.03, 0.03), (0.032, 0.048)]
    y = saucer(m, 0.058)
    vessel(m, outer, 0.0028, (0, y, 0), "f_plate_dark", 26)
    fill(m, outer, 0.0028, 0.041, "f_coffee_iced", (0, y, 0), 24, top="tex:espresso", inset=0.0)
    handle(m, [(0.031, y + 0.04, 0.0), (0.047, y + 0.042, 0.0), (0.049, y + 0.026, 0.0), (0.04, y + 0.012, 0.0), (0.026, y + 0.014, 0.0)], 0.0028, "f_plate_dark")
    for k in range(2):
        m.box((0.011, 0.011, 0.011), (-0.02 + 0.012 * k, y + 0.0055, 0.045), "f_icing_white", 0.001, rot=(0, 0.3 * k, 0))
    m.link((-0.02, y + 0.002, -0.04), (0.02, y + 0.003, -0.034), 0.0018, "f_steel", 4)


@drink("tea_pot_and_cups")
def _(m, rng):
    body = smooth_prof([(0, 0.0), (0.05, 0.0), (0.082, 0.02), (0.09, 0.055), (0.08, 0.095), (0.055, 0.115), (0.04, 0.12)], 3)
    lathe(m, body, (0, 0.0, 0), "f_plate_blue", 32)
    lathe(m, [(0.04, 0.12), (0.045, 0.123), (0.04, 0.126), (0.0, 0.13)], (0, 0.0, 0), "f_plate_blue", 28)
    blob(m, (0.009, 0.009, 0.009), (0.0, 0.137, 0.0), "f_plate_blue", 10, 7, uv=None)
    \
    tube3(m, spline([(0.075, 0.03, 0.0), (0.11, 0.06, 0.0), (0.135, 0.095, 0.0), (0.145, 0.108, 0.0)], 5), 0.011, "f_plate_blue", 8, caps=True)
    handle(m, [(-0.082, 0.1, 0.0), (-0.125, 0.105, 0.0), (-0.135, 0.065, 0.0), (-0.1, 0.03, 0.0), (-0.07, 0.045, 0.0)], 0.007, "f_plate_blue")
    for (x, z, ang) in ((0.0, 0.17, 0.0), (0.15, 0.14, 0.4)):
        y = saucer(m, 0.065, (x, 0.0, z), "f_plate_blue")
        outer = [(0.0, 0.0), (0.022, 0.0), (0.026, 0.004), (0.036, 0.04), (0.038, 0.048)]
        vessel(m, outer, 0.0025, (x, y, z), "f_plate", 24)
        fill(m, outer, 0.0025, 0.041, "f_tea_hot", (x, y, z), 22, top="tex:tea", inset=0.0)
        handle(m, [(x + 0.037, y + 0.04, z), (x + 0.056, y + 0.042, z), (x + 0.058, y + 0.026, z), (x + 0.045, y + 0.014, z), (x + 0.03, y + 0.016, z)], 0.003)


@drink("hot_cocoa_mug")
def _(m, rng):
    outer = [(0.0, 0.0), (0.04, 0.0), (0.043, 0.004), (0.046, 0.04), (0.047, 0.09)]
    vessel(m, outer, 0.0035, (0, 0, 0), "f_plate_red", 28)
    fill(m, outer, 0.0035, 0.083, "f_cocoa_liquid", (0, 0, 0), 26, top="tex:cocoa", inset=0.0)
    handle(m, [(0.046, 0.075, 0.0), (0.075, 0.078, 0.0), (0.08, 0.05, 0.0), (0.062, 0.022, 0.0), (0.043, 0.026, 0.0)], 0.0055, "f_plate_red")
    for k in range(5):
        a = k * 1.3
        blob(m, (0.0085, 0.007, 0.0085), (0.022 * math.cos(a) * (k > 0), 0.088, 0.022 * math.sin(a) * (k > 0)), "f_icing_white", 8, 6, uv=None)


@drink("water_glass_ice_lemon")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.0335, 0.01), (0.036, 0.09)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.003, 0.08, "f_water", (0, 0, 0), 24)
    ice_cubes(m, rng, 4, 0.016, 0.016, 0.03, 0.074)
    lathe(m, [(0.0, 0.0), (0.021, 0.0), (0.021, 0.004), (0.0, 0.004)], (0.034, 0.088, 0.0), "f_lemon_flesh", 20, rot=(0.0, 0.0, 1.2))


@drink("orange_juice_glass")
def _(m, rng):
    outer = [(0.0, 0.0), (0.028, 0.0), (0.03, 0.01), (0.034, 0.13), (0.036, 0.15)]
    vessel(m, outer, 0.0028, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.0028, 0.128, "f_juice_orange", (0, 0, 0), 24)
    straw(m, (0.004, 0.005, 0.0), (0.02, 0.185, -0.006), "f_straw_green")
    lathe(m, [(0.0, 0.0), (0.03, 0.0), (0.03, 0.004), (0.0, 0.004)], (0.036, 0.148, 0.0), "f_juice_orange", 22, rot=(0.0, 0.0, 1.5708))
    lathe(m, [(0.0, 0.0), (0.0298, 0.0), (0.0298, 0.0006), (0.0, 0.0006)], (0.0382, 0.148, 0.0), "tex:orange_cut", 22, uv="top", rot=(0.0, 0.0, 1.5708))


@drink("milk_glass_cookies")
def _(m, rng):
    outer = [(0.0, 0.0), (0.029, 0.0), (0.0315, 0.01), (0.035, 0.1), (0.036, 0.11)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.003, 0.098, "f_milk", (0, 0, 0), 24, top="tex:milk_froth", inset=0.0)
    for k in range(3):
        disc(m, 0.03, 0.008, (0.09 + 0.0 * k, 0.0 + 0.0085 * k, 0.015 * (k - 1) * 0.3), "tex:cookie", 18, uv="top", edge=0.8, disp=(0.0012, 40), rot=(0, k, 0))
    disc(m, 0.03, 0.008, (0.13, 0.0, 0.035), "tex:cookie", 18, uv="top", edge=0.8, disp=(0.0012, 40), rot=(0.0, 0.0, 0.0))


@drink("smoothie_strawberry_tall")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.033, 0.01), (0.038, 0.17), (0.04, 0.19)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.003, 0.172, "f_pink_smoothie", (0, 0, 0), 24, top="tex:smoothie_pink", inset=0.0, disp=(0.0006, 60))
    straw(m, (0.004, 0.005, 0.0), (0.018, 0.235, 0.004), "f_straw")
    blob(m, (0.0135, 0.015, 0.0135), (0.034, 0.188, 0.0), "tex:strawberry", 12, 9, uv="sph")
    sprig(m, (0.034, 0.2, 0.0), "f_herb", 3, 0.008, rng)


@drink("bubble_tea_cup")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.0335, 0.01), (0.04, 0.17), (0.0415, 0.185)]
    vessel(m, outer, 0.0015, (0, 0, 0), "f_clear_plastic", 28)
    fill(m, outer, 0.0015, 0.162, "f_bubble_milk_tea", (0, 0, 0), 26)
    for k in range(34):
        a = k * 2.399
        d = math.sqrt((k + 0.5) / 34) * 0.027
        blob(m, (0.0058, 0.0058, 0.0058), (d * math.cos(a), 0.01 + 0.0 + 0.0075 * (k % 3), d * math.sin(a)), "tex:boba", 7, 5, uv="sph")
    dome(m, 0.0425, 0.02, (0, 0.185, 0), "f_clear_plastic", 26, 5, uv=None)
    straw(m, (0.01, 0.03, 0.0), (0.016, 0.255, 0.0), "f_straw_green", 0.0055)
    m.cyl(0.0425, 0.004, (0.0, 0.1855, 0.0), "f_clear_plastic", seg=26)


@drink("iced_coffee_glass")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.033, 0.01), (0.038, 0.15), (0.04, 0.17)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.003, 0.15, "f_coffee_iced", (0, 0, 0), 24)
    lathe(m, [(0.0, 0.0), (0.0345, 0.0), (0.0365, 0.05), (0.0, 0.05)], (0, 0.1, 0), "f_milk", 24, disp=(0.0006, 80))
    ice_cubes(m, rng, 5, 0.018, 0.018, 0.06, 0.145, 0.022)
    straw(m, (0.004, 0.005, 0.0), (0.016, 0.215, 0.004), "f_straw")


@drink("lemonade_pitcher_set")
def _(m, rng):
    outer = [(0.0, 0.0), (0.05, 0.0), (0.056, 0.012), (0.058, 0.2), (0.052, 0.225)]
    vessel(m, outer, 0.004, (0, 0, 0), "f_glass", 30)
    fill(m, outer, 0.004, 0.18, "f_lemonade", (0, 0, 0), 28)
    handle(m, [(-0.058, 0.19, 0.0), (-0.09, 0.19, 0.0), (-0.095, 0.1, 0.0), (-0.058, 0.04, 0.0)], 0.005, "f_glass")
    for k in range(3):
        lathe(m, [(0.0, 0.0), (0.026, 0.0), (0.026, 0.005), (0.0, 0.005)], (0.0 + 0.012 * k - 0.012, 0.15 + 0.012 * k, 0.015 * (k - 1)), "f_lemon_flesh", 20, rot=(1.2, 0.5 * k, 0.4))
    ice_cubes(m, rng, 5, 0.03, 0.03, 0.08, 0.17, 0.024)
    for k in range(2):
        gx = 0.12 + 0.0 * k
        gz = -0.06 + 0.1 * k
        g_out = [(0.0, 0.0), (0.028, 0.0), (0.032, 0.008), (0.036, 0.09)]
        vessel(m, g_out, 0.003, (gx, 0.0, gz), "f_glass", 24)
        fill(m, g_out, 0.003, 0.08, "f_lemonade", (gx, 0.0, gz), 22)
    sprig(m, (0.0, 0.226, 0.0), "tex:leaf_mint", 4, 0.016, rng)


@drink("coffee_pot_and_mugs")
def _(m, rng):
    body = smooth_prof([(0, 0.0), (0.06, 0.0), (0.068, 0.02), (0.06, 0.08), (0.05, 0.16), (0.05, 0.19)], 2)
    lathe(m, body, (0, 0.0, 0), "f_glass", 28)
    lathe(m, [(0, 0.004), (0.058, 0.004), (0.066, 0.02), (0.058, 0.08), (0.049, 0.14), (0.0, 0.14)], (0, 0.0, 0), "f_coffee_iced", 26)
    lathe(m, [(0.0, 0.0), (0.052, 0.0), (0.053, 0.012), (0.0, 0.014)], (0, 0.19, 0), "black_metal", 28)
    handle(m, [(-0.05, 0.18, 0.0), (-0.09, 0.18, 0.0), (-0.095, 0.1, 0.0), (-0.06, 0.03, 0.0)], 0.007, "black_metal")
    for k in range(2):
        mx = 0.14
        mz = -0.05 + 0.11 * k
        o = [(0.0, 0.0), (0.033, 0.0), (0.036, 0.004), (0.038, 0.085)]
        vessel(m, o, 0.003, (mx, 0.0, mz), "f_plate_dark" if k else "f_plate_sage", 24)
        fill(m, o, 0.003, 0.075, "f_coffee_iced", (mx, 0.0, mz), 22, top="tex:coffee_black", inset=0.0)
        handle(m, [(mx + 0.037, 0.075, mz), (mx + 0.058, 0.076, mz), (mx + 0.062, 0.05, mz), (mx + 0.047, 0.024, mz), (mx + 0.033, 0.026, mz)], 0.0045, "f_plate_dark" if k else "f_plate_sage")


@drink("mason_jar_green_smoothie")
def _(m, rng):
    outer = [(0.0, 0.0), (0.034, 0.0), (0.038, 0.01), (0.039, 0.11), (0.034, 0.125), (0.034, 0.138)]
    vessel(m, outer, 0.0028, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.0028, 0.105, "f_green_smoothie", (0, 0, 0), 24, top="tex:smoothie_green", inset=0.0)
    for k in range(4):
        m.torus(0.035, 0.0013, (0.0, 0.118 + 0.006 * k, 0.0), "f_glass", seg=22, tseg=4)
    straw(m, (0.0, 0.01, 0.0), (0.012, 0.19, 0.004), "f_straw_green")
    sprig(m, (0.0, 0.108, 0.0), "tex:spinach", 3, 0.012, rng)


@drink("tea_cup_with_bag")
def _(m, rng):
    outer = [(0.0, 0.0), (0.028, 0.0), (0.031, 0.004), (0.044, 0.05), (0.046, 0.062)]
    y = saucer(m, 0.072, (0, 0, 0), "f_plate_sage")
    vessel(m, outer, 0.003, (0, y, 0), "f_glass", 28)
    fill(m, outer, 0.003, 0.054, "f_tea_hot", (0, y, 0), 26)
    handle(m, [(0.045, y + 0.055, 0.0), (0.065, y + 0.056, 0.0), (0.067, y + 0.035, 0.0), (0.055, y + 0.02, 0.0), (0.038, y + 0.023, 0.0)], 0.0035, "f_glass")
    m.box((0.026, 0.0012, 0.03), (0.0, y + 0.05, 0.0), "f_paper", 0.0003, rot=(0.0, 0.0, 0.0))
    tube3(m, [(0.0, y + 0.05, 0.0), (0.02, y + 0.068, 0.0), (0.058, y + 0.07, 0.01)], 0.0004, "f_paper", 3, caps=False)
    m.box((0.022, 0.0012, 0.016), (0.06, y + 0.0072, 0.012), "f_paper", 0.0003, rot=(0, 0.3, 0))


@drink("milkshake_whipped")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.032, 0.01), (0.044, 0.15), (0.047, 0.18)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 28)
    fill(m, outer, 0.003, 0.17, "f_milk", (0, 0, 0), 26)
    lathe(m, [(0.0, 0.0), (0.0295, 0.0), (0.0345, 0.03), (0.0415, 0.12), (0.0, 0.12)], (0, 0.012, 0), "f_ice_cream_straw", 26, disp=(0.0007, 80))
    lathe(m, [(0, 0.0), (0.046, 0.0), (0.043, 0.012), (0.034, 0.026), (0.02, 0.042), (0.007, 0.056), (0.0, 0.06)], (0, 0.168, 0), "f_icing_white", 26, warp=wobble(8, 0.0, 0.05))
    blob(m, (0.0105, 0.0105, 0.0105), (0.0, 0.232, 0.0), "tex:cherry", 12, 9, uv="sph")
    straw(m, (0.01, 0.01, 0.0), (0.03, 0.27, 0.0), "f_straw")


# ================================================================ CANS
CANS = (
    ("cola", "tex:can_cola", 0.033, 0.122, 0.0),
    ("lime_fizz", "tex:can_lime", 0.033, 0.122, 0.0),
    ("orange_soda", "tex:can_orange", 0.033, 0.115, 0.002),
    ("blue_cooler_tall", "tex:can_blue", 0.033, 0.168, 0.0),
    ("grape_pop_mini", "tex:can_grape", 0.026, 0.09, 0.0),
    ("energy_slim", "tex:can_energy", 0.029, 0.135, 0.0),
    ("tonic_sleek", "tex:can_tonic", 0.027, 0.146, 0.0),
    ("cold_brew", "tex:can_coffee", 0.0325, 0.095, 0.0),
)


def make_can(m, tex, R, H, bulge, opened=False):
    hb = 0.012
    body = [(R * 0.82, hb), (R * 0.95, hb + 0.002), (R, hb + 0.006), (R + bulge, H * 0.5), (R, H - 0.016), (R * 0.9, H - 0.008)]
    lathe(m, body, (0, 0, 0), tex, 28, uv="cyl", tile=(1, 1))
    # aluminium base with domed bottom, shoulder, lid with recessed top, stay-tab
    lathe(m, [(0.0, 0.006), (R * 0.62, 0.003), (R * 0.82, 0.0), (R * 0.86, 0.004), (R * 0.82, hb), (0.0, hb)], (0, 0, 0), "f_foil", 26)
    lathe(m, [(R * 0.9, H - 0.008), (R * 0.84, H - 0.004), (R * 0.84, H), (R * 0.8, H + 0.001), (R * 0.78, H - 0.004), (0.0, H - 0.004)], (0, 0, 0), "f_foil", 26)
    m.torus(R * 0.82, 0.0014, (0, H, 0), "f_foil", seg=26, tseg=4)
    m.box((R * 0.55, 0.0012, R * 0.3), (R * 0.1, H - 0.0006, -R * 0.1), "f_steel", 0.0004)
    m.torus(R * 0.14, 0.0012, (R * 0.38, H - 0.0006, -R * 0.1), "f_steel", seg=10, tseg=4)
    blob(m, (R * 0.2, 0.0004, R * 0.14), (-R * 0.25, H - 0.0045, R * 0.18), "black_metal", 8, 3, uv=None)


def _can(label):
    row = next(c for c in CANS if c[0] == label)

    def f(m, rng):
        make_can(m, row[1], row[2], row[3], row[4])
    return f


for _row in CANS:
    can(_row[0])(_can(_row[0]))


@can("sixpack_cola")
def _(m, rng):
    for i in range(3):
        for j in range(2):
            x, z = (i - 1) * 0.067, (j - 0.5) * 0.067
            lathe(m, [(0.0, 0.0), (0.0325, 0.0), (0.0325, 0.12), (0.0, 0.12)], (x, 0.0, z), "tex:can_cola", 20, uv="cyl")
            lathe(m, [(0.0, 0.0), (0.0275, 0.0), (0.0275, 0.003), (0.0, 0.003)], (x, 0.12, z), "f_foil", 18)
            m.box((0.018, 0.0012, 0.01), (x, 0.1225, z), "f_steel", 0.0004)
    for (x0, z0, x1, z1) in ((-0.1, -0.034, 0.1, -0.034), (-0.1, 0.034, 0.1, 0.034)):
        m.box((0.2, 0.0012, 0.003), ((x0 + x1) / 2, 0.118, (z0 + z1) / 2), "f_clear_plastic", 0.0)


# ================================================================ BOTTLES
def bottle_body(m, ctrl, mat, pos=(0, 0, 0), seg=26, n=2):
    prof = smooth_prof(ctrl, n)
    lathe(m, prof, pos, mat, seg)
    return prof


def label_band(m, R, y0, y1, tex, pos=(0, 0, 0), seg=26, bulge=0.0006):
    lathe(m, [(R + bulge, y0), (R + bulge, y1)], pos, tex, seg, uv="cyl")


@bottle("water_bottle_500ml")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.034, 0.012), (0.034, 0.03), (0.0305, 0.045), (0.034, 0.06), (0.034, 0.12), (0.033, 0.15), (0.026, 0.17), (0.0145, 0.18), (0.0135, 0.192)]
    bottle_body(m, ctrl, "f_clear_plastic", seg=28, n=2)
    lathe(m, [(0.0, 0.004), (0.028, 0.004), (0.032, 0.03), (0.0285, 0.045), (0.032, 0.06), (0.032, 0.12), (0.0, 0.12)], (0, 0, 0), "f_water", 24)
    label_band(m, 0.034, 0.062, 0.115, "tex:label_water", seg=28)
    m.cyl(0.0155, 0.02, (0.0, 0.2, 0.0), "f_plastic_clear_cap", seg=20)
    m.torus(0.0145, 0.0012, (0.0, 0.191, 0.0), "f_clear_plastic", seg=18, tseg=4)


@bottle("sport_bottle_squeeze")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.027, 0.0), (0.03, 0.01), (0.031, 0.09), (0.029, 0.15), (0.024, 0.19), (0.021, 0.2)]
    bottle_body(m, ctrl, "f_cap_green", seg=24, n=2)
    label_band(m, 0.0307, 0.05, 0.12, "tex:label_flask", seg=24)
    m.cyl(0.022, 0.012, (0.0, 0.206, 0.0), "f_cap_black", seg=20)
    m.cyl(0.012, 0.03, (0.0, 0.227, 0.0), "f_cap_black", seg=14, r2=0.0095)
    m.cyl(0.0125, 0.008, (0.0, 0.246, 0.0), "f_cap_green", seg=14)


@bottle("wine_red_bordeaux")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.037, 0.006), (0.0375, 0.03), (0.0375, 0.18), (0.034, 0.205), (0.017, 0.24), (0.0125, 0.262), (0.0125, 0.31), (0.0145, 0.316), (0.0145, 0.325)]
    bottle_body(m, ctrl, "f_glass_dark", seg=28, n=2)
    label_band(m, 0.0375, 0.07, 0.15, "tex:label_wine", seg=28)
    m.cyl(0.0148, 0.07, (0.0, 0.29, 0.0), "f_wax_red", seg=20)


@bottle("wine_white_hock")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.035, 0.006), (0.0355, 0.03), (0.0355, 0.15), (0.032, 0.2), (0.0165, 0.255), (0.0125, 0.285), (0.0125, 0.32), (0.0145, 0.325), (0.0145, 0.335)]
    bottle_body(m, ctrl, "f_glass_green", seg=28, n=2)
    label_band(m, 0.0355, 0.06, 0.14, "tex:label_wine_white", seg=28)
    m.cyl(0.0148, 0.055, (0.0, 0.31, 0.0), "f_foil_gold", seg=20)


@bottle("champagne_foil")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.0385, 0.008), (0.039, 0.04), (0.039, 0.16), (0.034, 0.205), (0.018, 0.25), (0.0145, 0.275), (0.0145, 0.3)]
    bottle_body(m, ctrl, "f_glass_dark", seg=28, n=2)
    label_band(m, 0.039, 0.09, 0.15, "tex:label_champagne", seg=28)
    m.cyl(0.0155, 0.1, (0.0, 0.26, 0.0), "f_wrapper_gold", seg=24, r2=0.0225)
    m.cyl(0.0235, 0.012, (0.0, 0.318, 0.0), "f_wrapper_gold", seg=24)


@bottle("beer_brown_longneck")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.027, 0.0), (0.031, 0.006), (0.031, 0.13), (0.028, 0.16), (0.016, 0.2), (0.0125, 0.22), (0.0125, 0.24), (0.0145, 0.246)]
    bottle_body(m, ctrl, "f_glass_brown", seg=26, n=2)
    label_band(m, 0.031, 0.08, 0.145, "tex:label_beer", seg=26)
    m.cyl(0.0155, 0.007, (0.0, 0.247, 0.0), "f_cap_gold", seg=20)
    m.torus(0.0165, 0.0012, (0.0, 0.2505, 0.0), "f_cap_gold", seg=20, tseg=4)


@bottle("beer_lager_green")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.028, 0.0), (0.0325, 0.006), (0.0325, 0.12), (0.03, 0.15), (0.019, 0.185), (0.0135, 0.205), (0.0135, 0.215), (0.015, 0.22)]
    bottle_body(m, ctrl, "f_glass_green", seg=26, n=2)
    label_band(m, 0.0325, 0.07, 0.14, "tex:label_lager", seg=26)
    m.cyl(0.0165, 0.007, (0.0, 0.222, 0.0), "f_cap_red", seg=20)


@bottle("whisky_decanter_square")
def _(m, rng):
    m.box((0.095, 0.17, 0.095), (0, 0.085, 0), "f_glass", 0.01)
    m.box((0.087, 0.12, 0.087), (0, 0.065, 0), "f_whisky", 0.008)
    m.cyl(0.025, 0.03, (0, 0.185, 0), "f_glass", seg=16)
    m.cyl(0.03, 0.008, (0, 0.2, 0), "f_glass", seg=16)
    lathe(m, [(0.0, 0.0), (0.016, 0.0), (0.02, 0.012), (0.0, 0.03)], (0, 0.2, 0), "f_cork", 14)
    m.box((0.06, 0.05, 0.003), (0, 0.095, 0.0495), "f_label_cream", 0.0005)
    m.cyl(0.012, 0.0015, (0.0, 0.1, 0.0515), "f_wax_red", axis="z", seg=12)


@bottle("gin_blue_flask")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.034, 0.0), (0.04, 0.008), (0.04, 0.13), (0.033, 0.17), (0.016, 0.2), (0.013, 0.22), (0.013, 0.25), (0.0155, 0.256)]
    bottle_body(m, ctrl, "f_blue_lagoon", seg=26, n=2)
    label_band(m, 0.04, 0.05, 0.12, "tex:label_ration", seg=26)
    m.cyl(0.0165, 0.026, (0.0, 0.26, 0.0), "f_cork", seg=14, r2=0.0145)
    m.cyl(0.0185, 0.01, (0.0, 0.276, 0.0), "f_cap_black", seg=16)


@bottle("olive_oil_cruet")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.036, 0.01), (0.036, 0.1), (0.028, 0.14), (0.014, 0.17), (0.012, 0.19), (0.012, 0.23)]
    bottle_body(m, ctrl, "f_glass_green", seg=26, n=2)
    lathe(m, [(0.0, 0.003), (0.032, 0.004), (0.0345, 0.01), (0.0345, 0.095), (0.0, 0.095)], (0, 0, 0), "f_olive_oil", 24)
    m.cyl(0.0135, 0.034, (0.0, 0.245, 0.0), "f_steel", seg=14, r2=0.011)
    m.cyl(0.0035, 0.018, (0.0, 0.272, 0.0), "f_steel", seg=8)
    m.box((0.05, 0.065, 0.002), (0.0, 0.07, 0.036), "f_label_cream", 0.0005)


@bottle("milk_bottle_glass")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.03, 0.0), (0.034, 0.005), (0.034, 0.1), (0.03, 0.13), (0.022, 0.15), (0.0215, 0.16), (0.024, 0.17), (0.0235, 0.185)]
    bottle_body(m, ctrl, "f_glass", seg=26, n=2)
    lathe(m, [(0.0, 0.004), (0.03, 0.004), (0.0335, 0.01), (0.0335, 0.1), (0.029, 0.13), (0.021, 0.147), (0.0, 0.147)], (0, 0, 0), "f_milk", 24)
    label_band(m, 0.034, 0.03, 0.09, "tex:label_milk", seg=26)
    m.cyl(0.0245, 0.01, (0.0, 0.185, 0.0), "f_foil", seg=20)


@bottle("hip_flask_steel")
def _(m, rng):
    m.box((0.11, 0.15, 0.027), (0, 0.075, 0), "f_steel", 0.012)
    m.box((0.1, 0.05, 0.0285), (0, 0.06, 0), "leather_brown", 0.005)
    m.cyl(0.013, 0.02, (0, 0.16, 0), "f_steel", seg=14)
    m.cyl(0.016, 0.014, (0, 0.178, 0), "f_steel", seg=16)


@bottle("thermos_vacuum_flask")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.034, 0.0), (0.04, 0.008), (0.04, 0.22), (0.037, 0.236), (0.0, 0.236)], (0, 0, 0), "f_cap_green", 26)
    label_band(m, 0.04, 0.07, 0.16, "tex:label_flask", seg=26)
    m.cyl(0.0405, 0.055, (0.0, 0.2625, 0.0), "f_steel", seg=26, r2=0.0385)
    m.cyl(0.0395, 0.005, (0.0, 0.2925, 0.0), "f_cap_black", seg=26)
    handle(m, [(0.04, 0.2, 0.0), (0.065, 0.2, 0.0), (0.068, 0.12, 0.0), (0.04, 0.1, 0.0)], 0.006, "f_cap_black")


@bottle("hot_sauce_bottle")
def _(m, rng):
    ctrl = [(0.0, 0.0), (0.022, 0.0), (0.026, 0.006), (0.026, 0.09), (0.02, 0.11), (0.011, 0.125), (0.01, 0.145)]
    bottle_body(m, ctrl, "f_glass_green", seg=22, n=2)
    lathe(m, [(0.0, 0.003), (0.0235, 0.004), (0.0245, 0.01), (0.0245, 0.085), (0.0, 0.085)], (0, 0, 0), "f_wax_red", 20)
    label_band(m, 0.026, 0.035, 0.085, "tex:label_ration", seg=22)
    m.cyl(0.0115, 0.02, (0.0, 0.153, 0.0), "f_cap_red", seg=14)
    m.cyl(0.0035, 0.01, (0.0, 0.168, 0.0), "f_cap_red", seg=8, r2=0.0025)


# ================================================================ COCKTAILS AND GLASSWARE
@cocktail("martini_olive")
def _(m, rng):
    bowl = [(0.0, 0.092), (0.012, 0.094), (0.045, 0.16), (0.049, 0.17)]
    lathe(m, [(0.0, 0.0), (0.035, 0.0), (0.036, 0.003), (0.006, 0.01), (0.004, 0.09), (0.0, 0.09)], (0, 0, 0), "f_glass", 24)
    vessel(m, bowl, 0.0022, (0, 0.0, 0), "f_glass", 28)
    fill(m, bowl, 0.0022, 0.152, "f_martini", (0, 0.0, 0), 26)
    m.link((-0.02, 0.1, 0.0), (0.02, 0.178, 0.0), 0.0012, "f_wood_light", 4)
    blob(m, (0.0085, 0.0075, 0.0075), (-0.0185, 0.1075, 0.0), "f_olive", 10, 7, uv=None)
    blob(m, (0.0032, 0.0032, 0.0032), (-0.0205, 0.1075, 0.0), "f_gelatin", 6, 4, uv=None)


@cocktail("margarita_salt_rim")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.032, 0.0), (0.033, 0.003), (0.007, 0.01), (0.005, 0.08), (0.0, 0.08)], (0, 0, 0), "f_glass", 24)
    outer = [(0.0, 0.08), (0.015, 0.082), (0.036, 0.1), (0.055, 0.13), (0.06, 0.15)]
    vessel(m, outer, 0.0022, (0, 0.0, 0), "f_glass", 30)
    fill(m, outer, 0.0022, 0.138, "f_margarita", (0, 0.0, 0), 28)
    m.torus(0.0575, 0.0022, (0, 0.1495, 0), "f_white", seg=32, tseg=5)
    lathe(m, [(0.0, 0.0), (0.021, 0.0), (0.021, 0.004), (0.0, 0.004)], (0.058, 0.142, 0.0), "tex:lime_peel", 20, uv="sph", rot=(0.0, 0.0, 1.5708))
    lathe(m, [(0.0, 0.0), (0.0195, 0.0), (0.0195, 0.0006), (0.0, 0.0006)], (0.0602, 0.142, 0.0), "tex:lime_cut", 20, uv="top", rot=(0.0, 0.0, 1.5708))


@cocktail("mojito_mint_highball")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.033, 0.01), (0.037, 0.15), (0.0385, 0.165)]
    vessel(m, outer, 0.0028, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.0028, 0.148, "f_mojito", (0, 0, 0), 24)
    ice_cubes(m, rng, 8, 0.02, 0.02, 0.02, 0.14, 0.02)
    for k in range(5):
        a = k * 1.3
    for k in range(6):
        a = k * 1.1
        blob(m, (0.012, 0.0015, 0.007), (0.012 * math.cos(a), 0.13 + 0.006 * (k % 3), 0.012 * math.sin(a)), "tex:leaf_mint", 6, 4, uv="sph", rot=(0.3, a, 0.4))
    sprig(m, (0.0, 0.17, 0.0), "tex:leaf_mint", 5, 0.016, rng)
    straw(m, (0.008, 0.01, 0.0), (0.02, 0.215, 0.006), "f_straw_green")
    lathe(m, [(0.0, 0.0), (0.022, 0.0), (0.022, 0.004), (0.0, 0.004)], (0.0385, 0.16, 0.0), "tex:lime_peel", 20, uv="sph", rot=(0.0, 0.0, 1.5708))


@cocktail("beer_mug_foam")
def _(m, rng):
    outer = [(0.0, 0.0), (0.04, 0.0), (0.043, 0.008), (0.046, 0.12), (0.047, 0.14)]
    vessel(m, outer, 0.005, (0, 0, 0), "f_glass", 30)
    fill(m, outer, 0.005, 0.118, "f_beer", (0, 0, 0), 28)
    lathe(m, [(0.0, 0.0), (0.0405, 0.0), (0.0412, 0.024), (0.0, 0.03)], (0, 0.113, 0), "tex:beer_foam", 28, uv="cyl", disp=(0.0014, 90), tile=(2, 1))
    handle(m, [(0.046, 0.12, 0.0), (0.078, 0.122, 0.0), (0.084, 0.07, 0.0), (0.05, 0.025, 0.0)], 0.0075, "f_glass")
    handle(m, [(0.046, 0.108, 0.0), (0.066, 0.108, 0.0), (0.07, 0.07, 0.0), (0.048, 0.04, 0.0)], 0.0035, "f_glass")


@cocktail("pint_stout")
def _(m, rng):
    outer = [(0.0, 0.0), (0.0275, 0.0), (0.03, 0.008), (0.0385, 0.14), (0.0435, 0.155)]
    vessel(m, outer, 0.0028, (0, 0, 0), "f_glass", 28)
    fill(m, outer, 0.0028, 0.135, "f_stout", (0, 0, 0), 26)
    lathe(m, [(0.0, 0.0), (0.0405, 0.0), (0.0425, 0.02), (0.0, 0.021)], (0, 0.132, 0), "f_cream", 26, disp=(0.0005, 90))


@cocktail("wine_glass_red")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.04, 0.0), (0.042, 0.004), (0.006, 0.01), (0.004, 0.08)], (0, 0, 0), "f_glass", 28)
    outer = [(0.0, 0.078), (0.01, 0.08), (0.038, 0.11), (0.041, 0.14), (0.031, 0.185), (0.027, 0.195)]
    vessel(m, outer, 0.0016, (0, 0, 0), "f_glass", 32)
    fill(m, outer, 0.0016, 0.13, "f_wine_red", (0, 0, 0), 30)


@cocktail("champagne_flute")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.031, 0.0), (0.033, 0.003), (0.005, 0.01), (0.004, 0.08)], (0, 0, 0), "f_glass", 24)
    outer = [(0.0, 0.078), (0.008, 0.08), (0.022, 0.1), (0.026, 0.15), (0.024, 0.19), (0.023, 0.2)]
    vessel(m, outer, 0.0015, (0, 0, 0), "f_glass", 26)
    fill(m, outer, 0.0015, 0.178, "f_champagne", (0, 0, 0), 24)
    for k in range(10):
        blob(m, (0.0017, 0.0017, 0.0017), (0.006 * math.cos(k * 2.4), 0.09 + 0.0085 * k, 0.006 * math.sin(k * 2.4)), "f_champagne_bubble", 5, 3, uv=None)


@cocktail("old_fashioned_orange")
def _(m, rng):
    outer = [(0.0, 0.0), (0.033, 0.0), (0.036, 0.012), (0.04, 0.08)]
    vessel(m, outer, 0.004, (0, 0, 0), "f_glass", 28)
    fill(m, outer, 0.004, 0.06, "f_whisky", (0, 0, 0), 26)
    m.box((0.045, 0.045, 0.045), (0.0, 0.032, 0.0), "f_ice_cube", 0.006, rot=(0.1, 0.5, 0.05))
    pts = [(0.0165 * math.cos(t * 3.2), 0.05 + 0.04 * (t / 3.14) , 0.0165 * math.sin(t * 3.2)) for t in [i * 0.5 for i in range(7)]]
    tube3(m, [(p[0] * 1.2 + 0.0, p[1] + 0.02, p[2] * 1.2) for p in pts], 0.0025, "f_juice_orange", 5, caps=True, flat=0.5)
    blob(m, (0.0045, 0.0045, 0.0045), (0.0, 0.075, 0.0), "tex:cherry", 8, 6, uv="sph")


@cocktail("blue_lagoon_hurricane")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.035, 0.0), (0.036, 0.004), (0.006, 0.012), (0.005, 0.06)], (0, 0, 0), "f_glass", 24)
    outer = [(0.0, 0.055), (0.01, 0.058), (0.036, 0.08), (0.04, 0.12), (0.032, 0.165), (0.028, 0.175)]
    vessel(m, outer, 0.002, (0, 0, 0), "f_glass", 28)
    fill(m, outer, 0.002, 0.15, "f_blue_lagoon", (0, 0, 0), 26)
    ice_cubes(m, rng, 4, 0.016, 0.016, 0.08, 0.14, 0.018)
    m.link((0.004, 0.14, 0.0), (0.004, 0.215, 0.0), 0.0012, "f_wood_light", 4)
    lathe(m, [(0.0, 0.0), (0.031, 0.0), (0.0, 0.02)], (0.004, 0.185, 0.0), "f_cap_red", 14, warp=wobble(8, 0.0, 0.08))
    blob(m, (0.007, 0.007, 0.007), (0.03, 0.17, 0.0), "tex:cherry", 8, 6, uv="sph")
    straw(m, (-0.006, 0.01, 0.006), (-0.012, 0.215, 0.012), "f_straw")


@cocktail("whisky_rocks_tumbler")
def _(m, rng):
    outer = [(0.0, 0.0), (0.034, 0.0), (0.036, 0.01), (0.038, 0.085)]
    vessel(m, outer, 0.0055, (0, 0, 0), "f_glass", 28)
    fill(m, outer, 0.0055, 0.055, "f_whisky", (0, 0, 0), 26)
    for k in range(2):
        m.box((0.026, 0.026, 0.026), (-0.012 + 0.024 * k, 0.03 + 0.012 * k, 0.006 * k), "f_ice_cube", 0.004, rot=(0.2 * k, 0.5 + k, 0.1))


menu.register()
