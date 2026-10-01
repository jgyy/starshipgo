"""Realistic food models, part 3: fruit, vegetables, deli, hydroponic harvest crates and hanging produce."""
import math

from .food import wavy_leaf
from .foodkit import PI, TAU, Menu, blob, bowl_outer, bend_flat, crate, disc, extrude, heap, lathe, scaled, slab, smooth_prof, spline, sprig, tube3, vessel

menu = Menu()
fruit = menu.cat("fruit", tags=("food", "fruit"))
veg = menu.cat("veg", tags=("food", "vegetable"))
deli = menu.cat("deli", tags=("food", "deli"))
harvest = menu.cat("harvest", mount="floor", tags=("food", "hydroponics", "crate"))
hanging = menu.cat("hanging", mount="wall", tags=("food", "hanging"), mount_y=1.7)

APPLE = smooth_prof([(0, 0.1), (0.4, 0.0), (0.8, 0.12), (0.99, 0.42), (0.98, 0.68), (0.82, 0.9), (0.5, 0.99), (0.2, 0.93), (0, 0.8)], 3)
PEAR = smooth_prof([(0, 0.02), (0.45, 0.0), (0.8, 0.1), (0.93, 0.25), (0.78, 0.42), (0.56, 0.58), (0.42, 0.75), (0.28, 0.92), (0.1, 1.0), (0, 0.98)], 3)
BERRY = smooth_prof([(0, 0.0), (0.3, 0.05), (0.68, 0.22), (0.97, 0.5), (0.93, 0.74), (0.66, 0.92), (0.25, 0.99), (0, 0.95)], 3)
TOMATO = smooth_prof([(0, 0.05), (0.5, 0.0), (0.9, 0.2), (1.0, 0.55), (0.85, 0.85), (0.5, 0.97), (0.2, 0.9), (0, 0.8)], 3)
ONION = smooth_prof([(0, 0.0), (0.35, 0.02), (0.8, 0.22), (1.0, 0.45), (0.85, 0.7), (0.5, 0.88), (0.2, 0.96), (0.08, 1.0), (0, 1.0)], 3)


def stem(m, pos, h=0.012, r=0.0022, mat="f_stem", bend=0.004):
    tube3(m, spline([pos, (pos[0] + bend * 0.4, pos[1] + h * 0.5, pos[2]), (pos[0] + bend, pos[1] + h, pos[2] + bend * 0.5)], 3), r, mat, 5)


def calyx(m, pos, r, n=6, mat="f_herb", lift=0.0):
    for k in range(n):
        a = k * TAU / n
        blob(m, (r, r * 0.12, r * 0.32), (pos[0] + math.cos(a) * r * 0.7, pos[1] + lift, pos[2] + math.sin(a) * r * 0.7), mat, 6, 4, uv=None,
             rot=(0, -a, -0.35))


def fruit_body(m, prof, R, H, pos, mat, seg=20, disp=0.0012, uv="sph", lo=False, **kw):
    """Fruit from a unit outline scaled to radius R / height H; lo=True keeps every third outline point (crates, heaps)."""
    if lo:
        prof = prof[::3] + [prof[-1]]
        seg = min(seg, 9)
    lathe(m, scaled(prof, R, H), pos, mat, seg, uv=uv, disp=(disp, 55) if disp else None, **kw)


# ================================================================ FRUIT
@fruit("apple_red_and_slice")
def _(m, rng):
    fruit_body(m, APPLE, 0.04, 0.075, (0, 0, 0), "tex:apple_red", 22, 0.0015)
    stem(m, (0, 0.062, 0), 0.016, 0.0018, "f_stem_brown", 0.003)
    blob(m, (0.019, 0.0025, 0.009), (0.015, 0.07, 0.0), "tex:leaf", 8, 5, uv="sph", rot=(0, 0, 0.35))
    # three crescent-shaped wedges lying on their sides (skin outside, cut face up)
    arc = [(0.036 * math.cos(t), 0.036 * math.sin(t)) for t in [-0.9 + 1.8 * k / 8 for k in range(9)]]
    arc += [(0.012 * math.cos(t), 0.012 * math.sin(t)) for t in [0.9 - 1.8 * k / 4 for k in range(5)]]
    for k in range(3):
        extrude(m, arc, 0.011, (0.045 + 0.02 * k, 0.0 + 0.0 * k, 0.07 - 0.0 * k), "f_cream", "tex:apple_red", None, (0.0, 1.9 + 0.5 * k, 0.0), 12.0)


@fruit("apple_green_pair")
def _(m, rng):
    fruit_body(m, APPLE, 0.036, 0.07, (0, 0, 0), "tex:apple_green", 22, 0.0015)
    stem(m, (0, 0.058, 0), 0.015, 0.0018, "f_stem_brown", 0.004)
    fruit_body(m, APPLE, 0.033, 0.064, (0.075, 0, 0.02), "tex:apple_green", 22, 0.0015, rot=(0.9, 0.5, 0.0))
    blob(m, (0.02, 0.0025, 0.009), (0.015, 0.067, 0.004), "tex:leaf", 8, 5, uv="sph", rot=(0, 0.4, 0.3))


@fruit("orange_and_half")
def _(m, rng):
    blob(m, (0.037, 0.034, 0.037), (0, 0.034, 0), "tex:orange_peel", 22, 14, uv="sph", disp=(0.0008, 60))
    blob(m, (0.006, 0.002, 0.006), (0, 0.0675, 0), "f_stem", 6, 4, uv=None)
    # a halved orange, cut face up, with a wedge beside it
    lathe(m, [(0.0, 0.0), (0.012, 0.0), (0.03, 0.006), (0.0365, 0.018), (0.0372, 0.034)], (0.09, 0.0, 0.01), "tex:orange_peel", 22, uv="sph", disp=(0.0006, 60))
    lathe(m, [(0.0, 0.0), (0.0368, 0.0), (0.0368, 0.0008), (0.0, 0.0008)], (0.09, 0.034, 0.01), "tex:orange_cut", 26, uv="top")
    extrude(m, [(0.0, 0.0), (0.03, -0.012), (0.03, 0.012)], 0.016, (0.05, 0.0, 0.065), "f_juice_apple", "tex:orange_peel", None, (0.0, 0.5, 0.0), 8.0)


@fruit("banana_bunch")
def _(m, rng):
    L = 0.19
    ys = [L * k / 18 for k in range(19)]
    prof = [(0.0, 0.0)] + [(0.0095 + 0.0105 * math.sin(PI * (0.08 + 0.84 * k / 18)) ** 0.7 * (1.0 if k < 15 else 1 - (k - 14) * 0.18), ys[k]) for k in range(1, 18)] + [(0.0, L)]
    for k in range(4):
        lathe(m, prof, (0.02 * k * 0.0, 0.019 + 0.002 * k, 0.034 * (k - 1.5)), "tex:banana_skin", 5, scale=(1.0, 1.0, 1.0), uv="cyl", warp=bend_flat(0.17),
              rot=(0, -1.57 + 0.09 * (k - 1.5), 0), tile=(2, 1))
    m.box((0.026, 0.018, 0.14), (-0.0, 0.03, 0.0), "f_stem_brown", 0.004)


@fruit("grapes_purple")
def _(m, rng):
    rows = [(0.0, 1), (0.014, 4), (0.026, 6), (0.04, 7), (0.054, 6), (0.066, 4), (0.076, 2), (0.084, 1)]
    for x, n in rows:
        rad = 0.028 * math.sin(PI * (x + 0.02) / 0.11) ** 0.8
        for q in range(n):
            a = TAU * q / n + x * 20
            r = rad * (1 if n > 1 else 0)
            blob(m, (0.0105, 0.0105, 0.0105), (-0.04 + x, 0.03 + r * math.sin(a), r * math.cos(a)), "tex:grape_skin", 8, 6, uv="sph")
    tube3(m, spline([(-0.043, 0.032, 0.0), (-0.06, 0.04, 0.0), (-0.075, 0.034, 0.004)], 3), 0.0028, "f_stem_brown", 6)
    blob(m, (0.035, 0.003, 0.03), (-0.0, 0.058, 0.0), "tex:leaf", 10, 5, uv="sph", rot=(0.1, 0.5, 0.15))


@fruit("grapes_green_vine")
def _(m, rng):
    for k, (x, _y, z) in enumerate(heap(rng, 38, 0.036, 0.0, 0.2)):
        blob(m, (0.0095, 0.0105, 0.0095), (x * 1.3, 0.011 + 0.035 * (1 - (k / 38)) * 0.8, z * 1.3), "tex:grape_green", 8, 6, uv="sph")
    tube3(m, spline([(0.0, 0.05, 0.0), (0.01, 0.066, 0.01), (0.03, 0.074, 0.02)], 3), 0.0028, "f_stem_brown", 6)
    wavy_leaf(m, (0.04, 0.0, 0.0), 0.035, "tex:leaf", 14, 0.004, 3, 0.4, 0.002)


@fruit("strawberries_bowl")
def _(m, rng):
    R = 0.07
    vessel(m, bowl_outer(R, 0.05, 0.4, 7), 0.003, (0, 0, 0), "f_plate_cream", 26)
    for k, (x, y, z) in enumerate(heap(rng, 11, 0.045, 0.045, 0.6)):
        a = k * 1.9
        fruit_body(m, BERRY, 0.015, 0.034, (x, 0.014 + y, z), "tex:strawberry", 12, 0.0, rot=(0.5 * math.sin(a), a, 0.6 * math.cos(a)))
        calyx(m, (x, 0.014 + y + 0.03, z), 0.009, 5, "f_herb")


@fruit("watermelon_wedge")
def _(m, rng):
    R, T = 0.11, 0.05
    arc = [(R * math.cos(t), R * 0.85 * math.sin(t)) for t in [PI * k / 18 for k in range(19)]]
    extrude(m, arc, T, (0, 0.0, 0), "tex:watermelon_flesh", "tex:watermelon_rind", None, (PI / 2, 0, 0), 4.0)
    for k in range(4):
        pass
    for k in range(7):
        blob(m, (0.004, 0.0006, 0.0025), (-0.07 + 0.024 * k, -0.02 - 0.012 * (k % 2) - 0.03 * (1 - abs(k - 3) / 3) * 0.0, T + 0.0003), "f_nori", 5, 3, uv=None, rot=(0, 0, 0.8))


@fruit("pineapple_whole")
def _(m, rng):
    lathe(m, smooth_prof([(0, 0.0), (0.5, 0.02), (0.9, 0.2), (1.0, 0.5), (0.88, 0.82), (0.5, 0.98), (0, 1.0)], 3) and scaled(smooth_prof([(0, 0.0), (0.5, 0.02), (0.9, 0.2), (1.0, 0.5), (0.88, 0.82), (0.5, 0.98), (0, 1.0)], 3), 0.052, 0.16),
          (0, 0.0, 0), "tex:pineapple", 22, uv="cyl", tile=(2, 2), disp=(0.0015, 50))
    for ring, (n, ln, tilt, y0) in enumerate(((9, 0.085, 0.55, 0.15), (8, 0.095, 0.25, 0.158), (6, 0.08, 0.1, 0.162))):
        for k in range(n):
            a = k * TAU / n + ring * 0.5
            c, s = math.cos(a), math.sin(a)
            blob(m, (0.012, ln / 2, 0.003), (c * (0.018 + ln / 2 * math.sin(tilt)), y0 + ln / 2 * math.cos(tilt), s * (0.018 + ln / 2 * math.sin(tilt))),
                 "tex:leaf" if ring % 2 else "tex:leaf_mint", 6, 6, uv="sph", rot=(0, -a, -tilt * 1.0))


@fruit("lemons_cut")
def _(m, rng):
    for (x, z, rot) in ((0.0, 0.0, 0.3), (0.06, -0.04, 1.8)):
        blob(m, (0.035, 0.026, 0.026), (x, 0.026, z), "tex:lemon_peel", 18, 12, uv="sph", disp=(0.0007, 60), rot=(0, rot, 0))
        blob(m, (0.005, 0.004, 0.005), (x + 0.036 * math.cos(rot), 0.026, z - 0.036 * math.sin(rot)), "f_stem", 6, 4, uv=None)
    # a halved lemon, cut face up, and a wedge
    lathe(m, [(0, 0), (0.026, 0.0), (0.0275, 0.01), (0.022, 0.021), (0.0, 0.026)], (-0.06, 0.0, 0.03), "tex:lemon_peel", 20, uv="sph", scale=(1.0, 1.0, 1.0))


@fruit("pear_ripe")
def _(m, rng):
    fruit_body(m, PEAR, 0.036, 0.105, (0, 0, 0), "tex:pear_skin", 22, 0.0015, warp=lambda x, y, z: (x + 0.0006 * y / 0.1 * 30 * 0.01, y, z))
    stem(m, (0.001, 0.1, 0), 0.02, 0.002, "f_stem_brown", 0.008)
    blob(m, (0.02, 0.0025, 0.009), (0.015, 0.108, 0.0), "tex:leaf", 8, 5, uv="sph", rot=(0, 0, 0.5))
    fruit_body(m, PEAR, 0.03, 0.09, (0.08, 0.0, 0.025), "tex:pear_skin", 20, 0.0015, rot=(1.45, 0.4, 0.0))


@fruit("peaches_halved")
def _(m, rng):
    for (x, z) in ((0.0, 0.0), (0.075, 0.02)):
        blob(m, (0.037, 0.035, 0.036), (x, 0.035, z), "tex:peach_skin", 20, 14, uv="sph", disp=(0.0007, 50), warp=lambda a, b, c: (a + 0.0, b, c * (1 - 0.0)))
    lathe(m, [(0, 0), (0.035, 0.0), (0.034, 0.012), (0.026, 0.022), (0.0, 0.028)], (-0.075, 0.0, 0.01), "tex:peach_skin", 20, uv="sph")
    lathe(m, [(0, 0), (0.032, 0), (0.0, 0.0006)], (-0.075, 0.0, 0.01), "f_butter", 20)
    blob(m, (0.012, 0.009, 0.01), (-0.075, 0.003, 0.01), "f_wood_dark", 10, 8, uv=None, disp=(0.001, 100))


@fruit("cherries_stems")
def _(m, rng):
    for k in range(6):
        a = k * 1.05
        x, z = 0.03 * math.cos(a), 0.03 * math.sin(a) * 0.7
        blob(m, (0.0115, 0.0105, 0.011), (x, 0.0105, z), "tex:cherry", 12, 9, uv="sph")
        tube3(m, spline([(x, 0.02, z), (x * 0.5 + 0.01, 0.04, z * 0.5), (0.0, 0.065 + 0.004 * (k % 2), 0.0)], 4), 0.0009, "f_stem", 4)
    blob(m, (0.02, 0.0025, 0.01), (0.0, 0.07, 0.0), "tex:leaf", 8, 5, uv="sph", rot=(0, 0.3, 0.2))


@fruit("kiwi_halves")
def _(m, rng):
    blob(m, (0.032, 0.025, 0.027), (0.0, 0.026, 0.0), "tex:coconut", 18, 12, uv="sph", disp=(0.001, 80))
    for (x, z, r) in ((0.075, -0.01, 0.3), (0.075, 0.045, 1.2)):
        lathe(m, [(0, 0), (0.026, 0), (0.026, 0.001), (0.0, 0.001)], (x, 0.0, z), "tex:kiwi_cut", 24, uv="top", scale=(1.15, 1.0, 1.0), rot=(0, r, 0))
    for (x, z, r) in ((0.075, -0.01, 0.3), (0.075, 0.045, 1.2)):
        lathe(m, [(0, 0), (0.0285, 0.0), (0.03, 0.01), (0.027, 0.02), (0.0, 0.024)], (x, 0.0, z), "tex:coconut", 22, uv="sph", scale=(1.15, 1.0, 1.0), rot=(0, r, 0))
        lathe(m, [(0, 0), (0.0262, 0), (0.0262, 0.0006), (0.0, 0.0006)], (x, 0.0246, z), "tex:kiwi_cut", 24, uv="top", scale=(1.15, 1.0, 1.0), rot=(0, r, 0))


@fruit("pomegranate_open")
def _(m, rng):
    fruit_body(m, TOMATO, 0.04, 0.075, (0, 0, 0), "tex:pomegranate_skin", 22, 0.0012)
    calyx(m, (0, 0.074, 0), 0.01, 5, "tex:pomegranate_skin", 0.0)
    lathe(m, [(0, 0), (0.038, 0.0), (0.039, 0.012), (0.034, 0.028), (0.0, 0.036)], (0.1, 0.0, 0.0), "tex:pomegranate_skin", 22, uv="sph", disp=(0.001, 50))
    lathe(m, [(0.0, 0.0), (0.0345, 0.0), (0.0345, 0.0008), (0.0, 0.0008)], (0.1, 0.0345, 0.0), "f_cream", 22)
    for (x, y, z) in heap(rng, 38, 0.032, 0.0, 0.0):
        blob(m, (0.0045, 0.004, 0.0045), (0.1 + x, 0.0365, z), "f_pomegranate_seed", 6, 4, uv=None)
    for k in range(5):
        blob(m, (0.0045, 0.004, 0.0045), (0.04 - 0.01 * k, 0.004, 0.06 - 0.003 * k), "f_pomegranate_seed", 6, 4, uv=None)


@fruit("mango_hedgehog")
def _(m, rng):
    mango = smooth_prof([(0, 0.05), (0.5, 0.0), (0.9, 0.2), (1.0, 0.5), (0.8, 0.85), (0.4, 1.0), (0, 0.96)], 3)
    fruit_body(m, mango, 0.04, 0.095, (0, 0, 0), "tex:mango_skin", 22, 0.001, scale=(1.15, 1.0, 0.85))
    # a scored 'hedgehog' cheek: skin shell, flesh face and the cut cubes pushed out
    lathe(m, [(0.0, 0.0), (0.05, 0.0), (0.054, 0.012), (0.046, 0.024)], (0.115, 0.0, 0.0), "tex:mango_skin", 24, uv="sph", scale=(1.25, 1.0, 0.95))
    lathe(m, [(0.0, 0.0), (0.046, 0.0), (0.046, 0.0008), (0.0, 0.0008)], (0.115, 0.0235, 0.0), "f_corn_yellow", 24, scale=(1.25, 1.0, 0.95))
    for i in range(5):
        for j in range(4):
            x, z = (i - 2) * 0.0195, (j - 1.5) * 0.0185
            if (x / 0.0575) ** 2 + (z / 0.0455) ** 2 < 0.8:
                blob(m, (0.0092, 0.0078, 0.0088), (0.115 + x, 0.0255, z), "f_corn_yellow", 8, 6, uv=None, rot=(0, 0.0, 0.0))


@fruit("coconut_cracked")
def _(m, rng):
    blob(m, (0.055, 0.05, 0.055), (0, 0.05, 0), "tex:coconut", 20, 12, uv="sph", disp=(0.0015, 60))
    vessel(m, [(0, 0), (0.026, 0.0), (0.042, 0.022), (0.052, 0.045)], 0.003, (0.13, 0.0, 0.03), "tex:coconut", 22, uv="sph")
    lathe(m, [(0, 0.004), (0.028, 0.004), (0.045, 0.026), (0.049, 0.042), (0.0, 0.042)], (0.13, 0.0, 0.03), "f_white", 22)


@fruit("blueberries_bowl")
def _(m, rng):
    vessel(m, bowl_outer(0.062, 0.045, 0.4, 7), 0.003, (0, 0, 0), "f_plate_blue", 26)
    for (x, y, z) in heap(rng, 52, 0.052, 0.034, 0.5):
        blob(m, (0.0085, 0.0085, 0.0085), (x, 0.022 + y, z), "tex:blueberry", 7, 5, uv="sph")
    for k in range(5):
        a = k * 1.7
    sprig(m, (0.0, 0.057, 0.0), "tex:leaf_mint", 4, 0.014, rng)


# ================================================================ VEGETABLES
@veg("tomatoes_on_vine")
def _(m, rng):
    pts = [(-0.1, 0.012, 0.0), (-0.05, 0.03, 0.01), (0.0, 0.05, -0.005), (0.05, 0.05, 0.0), (0.1, 0.035, 0.01)]
    tube3(m, spline(pts, 5), 0.0028, "f_stem", 6)
    for k, (x, z) in enumerate(((-0.07, 0.025), (-0.02, -0.03), (0.035, 0.03), (0.09, -0.02))):
        R = 0.032 - 0.002 * (k % 2)
        fruit_body(m, TOMATO, R, R * 1.7, (x, 0.0, z), "tex:tomato_skin", 20, 0.0012)
        calyx(m, (x, R * 1.62, z), 0.012, 6, "f_herb", 0.0)
        tube3(m, spline([(x, R * 1.66, z), (x * 0.9, 0.055, z * 0.5), pts[min(k + 1, 4)]], 3), 0.0016, "f_stem", 5)
    for k in range(3):
        wavy_leaf(m, (-0.09 + 0.09 * k, 0.034 + 0.01 * k, -0.04 + 0.01 * k), 0.026, "tex:leaf", 10, 0.004, 3, k, 0.0016)


@veg("carrots_bunch")
def _(m, rng):
    L = 0.19
    for k in range(5):
        prof = [(0.0, 0.0)] + [(0.0165 * (1 - t) ** 0.8 * (1 + 0.03 * math.sin(t * 17 + k)), L * t) for t in [i / 14 for i in range(1, 14)]] + [(0.0004, L)]
        lathe(m, prof, (0.0, 0.0165 + 0.0, 0.034 * (k - 2)), "tex:carrot", 10, uv="cyl", rot=(0, (k - 2) * 0.1, -PI / 2), disp=(0.0006, 70), tile=(2, 1))
        for q in range(3):
            tube3(m, spline([(-0.01, 0.019, 0.034 * (k - 2)), (-0.05, 0.03 + 0.004 * q, 0.034 * (k - 2) + (q - 1) * 0.012), (-0.09, 0.028, 0.034 * (k - 2) + (q - 1) * 0.03)], 3),
                  0.0013, "f_stem", 4)
            blob(m, (0.028, 0.0015, 0.008), (-0.09, 0.028, 0.034 * (k - 2) + (q - 1) * 0.03), "tex:leaf_mint", 6, 4, uv="sph", rot=(0, (q - 1) * 0.5, 0))
    m.link((0.0, 0.0165, -0.075), (0.0, 0.0165, 0.075), 0.0025, "f_hay", 5)


@veg("corn_cobs")
def _(m, rng):
    cob = smooth_prof([(0, 0.0), (0.5, 0.01), (0.88, 0.1), (1.0, 0.4), (0.92, 0.75), (0.7, 0.93), (0.35, 0.99), (0, 1.0)], 3)
    lathe(m, scaled(cob, 0.0275, 0.2), (0, 0.0275, 0.0), "tex:corn", 16, uv="cyl", rot=(0, 0, PI / 2), tile=(1, 1), disp=(0.0007, 60))
    m.cyl(0.011, 0.04, (-0.11, 0.0275, 0.0), "f_hay", axis="x", seg=8)
    # second cob wrapped in husk leaves
    lathe(m, scaled(cob, 0.0275, 0.19), (0.0, 0.0275, 0.075), "tex:corn", 16, uv="cyl", rot=(0, 0.2, PI / 2), tile=(1, 1), disp=(0.0007, 60))
    for k in range(4):
        a = -0.55 + 0.37 * k
        pts = spline([(-0.07, 0.03, 0.075), (0.0, 0.05 + 0.005 * k, 0.075 + 0.045 * math.sin(a)), (0.085, 0.02, 0.075 + 0.07 * math.sin(a))], 4)
        tube3(m, pts, [0.0045 + 0.015 * math.sin(PI * i / (len(pts) - 1)) ** 0.6 for i in range(len(pts))], "tex:corn_husk", 8, uv=True, flat=0.18, caps=True, tile=(1, 4))
    for k in range(18):
        tube3(m, [(-0.1, 0.03, 0.075 + (k - 9) * 0.0016), (-0.14, 0.028 + 0.003 * math.sin(k), 0.075 + (k - 9) * 0.004)], 0.0005, "f_hay", 3, caps=False)


@veg("bell_peppers_trio")
def _(m, rng):
    cols = ("tex:pepper_red", "tex:pepper_yellow", "tex:pepper_green")
    prof = smooth_prof([(0, 0.06), (0.5, 0.0), (0.9, 0.2), (1.0, 0.55), (0.92, 0.88), (0.5, 0.98), (0.25, 1.0), (0.0, 0.86)], 3)
    for k, (x, z) in enumerate(((-0.07, 0.0), (0.04, -0.04), (0.06, 0.05))):
        lobes = lambda a, b, c: (a * (1 + 0.07 * math.cos(3 * math.atan2(c, a) + 0.4 * k)), b, c * (1 + 0.07 * math.cos(3 * math.atan2(c, a) + 0.4 * k)))
        fruit_body(m, prof, 0.048, 0.1, (x, 0.0, z), cols[k], 24, 0.0012, warp=lobes, rot=(0.0, k, 0.0))
        tube3(m, spline([(x, 0.092, z), (x + 0.004, 0.105, z), (x + 0.011, 0.113, z + 0.004)], 3), 0.005 - 0.0008 * k, "f_stem", 7)
        m.torus(0.011, 0.0035, (x, 0.099, z), "f_stem", seg=8, tseg=4)


@veg("aubergine_pair")
def _(m, rng):
    prof = smooth_prof([(0, 0.0), (0.4, 0.02), (0.85, 0.15), (1.0, 0.35), (0.85, 0.62), (0.55, 0.82), (0.3, 0.95), (0.0, 1.0)], 3)
    fruit_body(m, prof, 0.046, 0.2, (0, 0.0, 0.0), "tex:eggplant", 22, 0.0012, rot=(0.0, 0.0, 0.0))
    calyx(m, (0, 0.196, 0), 0.025, 6, "f_herb", 0.0)
    tube3(m, spline([(0, 0.196, 0), (0.004, 0.214, 0), (0.014, 0.226, 0.0)], 3), 0.008, "f_stem", 8)
    fruit_body(m, prof, 0.042, 0.18, (0.09, 0.0, 0.0), "tex:eggplant", 22, 0.0012, rot=(0.0, 0.4, 1.35))


@veg("cabbage_green")
def _(m, rng):
    blob(m, (0.085, 0.08, 0.085), (0, 0.08, 0), "tex:cabbage", 28, 16, uv="sph", disp=(0.004, 22), tile=(2, 2))
    for k in range(6):
        a = k * TAU / 6 + 0.3
        c, s = math.cos(a), math.sin(a)
        wavy_leaf(m, (c * 0.06, 0.03 + 0.012 * (k % 2), s * 0.06), 0.07, "tex:cabbage", 22, 0.012, 5, a, 0.003)
    blob(m, (0.007, 0.012, 0.007), (0.0, 0.01, 0.0), "f_hay", 6, 4, uv=None)


@veg("cabbage_red_halved")
def _(m, rng):
    blob(m, (0.085, 0.08, 0.085), (-0.1, 0.08, 0), "tex:cabbage_red", 26, 14, uv="sph", disp=(0.003, 22), tile=(2, 2))
    # half head with the cut face up, showing the layered leaves
    lathe(m, [(0.0, 0.0), (0.04, 0.008), (0.068, 0.035), (0.077, 0.065), (0.076, 0.08)], (0.1, 0.0, 0.0), "tex:cabbage_red", 28, uv="sph", disp=(0.002, 30))
    for k in range(7):
        r = 0.076 - 0.0105 * k
        lathe(m, [(0.0, 0.0), (r, 0.0), (r, 0.0008), (0.0, 0.0008)], (0.1, 0.08 + 0.0004 * k, 0.0), "f_cream" if k % 2 else "tex:cabbage_red", 28, uv="top")


@veg("potatoes_pile")
def _(m, rng):
    spots = ((0.0, 0.0), (0.075, 0.015), (0.035, -0.07), (-0.06, -0.05), (-0.065, 0.05), (0.03, 0.075))
    for k, (x, z) in enumerate(spots):
        blob(m, (0.05 + 0.006 * (k % 3), 0.034, 0.038 + 0.004 * (k % 2)), (x, 0.034, z), "tex:potato_skin", 16, 10, uv="sph", disp=(0.006, 24), rot=(0, k * 1.1, 0))
    blob(m, (0.05, 0.034, 0.038), (0.01, 0.075, 0.0), "tex:potato_skin", 16, 10, uv="sph", disp=(0.006, 24), rot=(0, 0.7, 0.1))
    blob(m, (0.05, 0.034, 0.038), (0.15, 0.034, 0.02), "tex:potato_skin", 16, 10, uv="sph", disp=(0.006, 24), rot=(0, 1.5, 0.0))


@veg("mushrooms_brown_white")
def _(m, rng):
    for k, (x, z, s, mat) in enumerate(((0.0, 0.0, 1.0, "tex:mushroom_white"), (0.055, 0.02, 0.8, "tex:mushroom_cap"), (-0.045, 0.035, 0.9, "tex:mushroom_white"),
                                         (0.02, -0.055, 0.75, "tex:mushroom_cap"), (-0.05, -0.04, 0.65, "tex:mushroom_white"))):
        cap = scaled(smooth_prof([(0, 0.5), (0.5, 0.45), (0.9, 0.55), (1.0, 0.7), (0.8, 0.92), (0.4, 1.0), (0, 1.0)], 3), 0.034 * s, 0.05 * s)
        lathe(m, [(0.0, 0.0), (0.011 * s, 0.0), (0.0125 * s, 0.025 * s), (0.015 * s, 0.03 * s)], (x, 0.0, z), "tex:mushroom_stem", 12, uv="cyl")
        lathe(m, cap, (x, 0.0, z), mat, 18, uv="sph", disp=(0.001, 60))


@veg("broccoli_cauliflower")
def _(m, rng):
    for (x, z, mat, col) in ((-0.05, 0.0, "tex:broccoli", "f_stem"), (0.065, 0.02, "f_cream", "f_herb")):
        lathe(m, [(0, 0), (0.013, 0.0), (0.011, 0.04), (0.0, 0.05)], (x, 0.0, z), "f_stem", 10)
        for (hx, hy, hz) in heap(rng, 22, 0.042, 0.04, 0.4):
            blob(m, (0.017, 0.015, 0.017), (x + hx, 0.052 + hy, z + hz), mat, 9, 6, uv="sph" if mat.startswith("tex") else None, disp=(0.003, 80))
        blob(m, (0.044, 0.03, 0.044), (x, 0.062, z), mat, 14, 8, uv="sph" if mat.startswith("tex") else None, disp=(0.004, 60))


@veg("onions_assorted")
def _(m, rng):
    for k, (x, z, mat) in enumerate(((0.0, 0.0, "tex:onion_skin"), (0.075, 0.015, "tex:onion_red"), (0.03, -0.065, "tex:onion_skin"))):
        fruit_body(m, ONION, 0.04, 0.08, (x, 0.0, z), mat, 18, 0.001, rot=(0, k, 0))
        tube3(m, spline([(x, 0.078, z), (x + 0.004, 0.09, z), (x - 0.002, 0.098, z + 0.003)], 3), 0.0022, "f_hay", 5)
    for k in range(4):
        m.torus(0.03 - 0.007 * k, 0.0022, (-0.08, 0.0035, 0.04), "f_onion" if k % 2 == 0 else "f_icing_pink", seg=18, tseg=5)


@veg("garlic_bulbs")
def _(m, rng):
    for (x, z) in ((0.0, 0.0), (0.07, 0.02)):
        fruit_body(m, ONION, 0.033, 0.05, (x, 0.0, z), "tex:garlic", 18, 0.0008)
        tube3(m, spline([(x, 0.05, z), (x, 0.062, z), (x + 0.004, 0.072, z)], 3), 0.003, "f_hay", 5)
        for q in range(8):
            a = q * TAU / 8
    for k in range(4):
        a = k * 1.3
        cl = scaled(smooth_prof([(0, 0.0), (0.7, 0.05), (1.0, 0.35), (0.7, 0.8), (0.3, 0.97), (0, 1.0)], 3), 0.012, 0.03)
        lathe(m, cl, (-0.07 + 0.015 * k, 0.012, 0.03 + 0.01 * (k % 2)), "tex:garlic", 10, uv="sph", rot=(1.45, a, 0.0))


@veg("cucumbers_sliced")
def _(m, rng):
    cu = [(0.0, 0.0)] + [(0.0215 * (0.9 + 0.1 * math.sin(PI * i / 14)), 0.22 * i / 14) for i in range(1, 14)] + [(0.0, 0.22)]
    lathe(m, cu, (0.0, 0.0215, 0.0), "tex:cucumber", 14, uv="cyl", rot=(0, 0.2, PI / 2), disp=(0.0007, 40), tile=(1, 1))
    for k in range(6):
        x = 0.07 + 0.0 * k
    for k in range(6):
        disc(m, 0.0215, 0.005, (-0.08 + 0.011 * k, 0.0215, 0.07), "tex:cucumber", 16, uv="top", edge=0.4, rot=(0, 0, PI / 2 - 0.15 * (k % 2)))
        disc(m, 0.0185, 0.0052, (-0.08 + 0.011 * k + 0.0003, 0.0215, 0.07), "f_pea", 16, uv=None, edge=0.2, rot=(0, 0, PI / 2 - 0.15 * (k % 2)))


@veg("lettuce_heads")
def _(m, rng):
    for (x, z, mat) in ((-0.07, 0.0, "tex:lettuce"), (0.08, 0.02, "tex:leaf_mint")):
        blob(m, (0.05, 0.045, 0.05), (x, 0.045, z), mat, 18, 10, uv="sph", disp=(0.004, 40))
        for k in range(10):
            a = k * TAU / 10 + 0.4 * (x > 0)
            wavy_leaf(m, (x + math.cos(a) * 0.05, 0.02 + 0.025 * (k % 3), z + math.sin(a) * 0.05), 0.058, mat, 18, 0.014, 6, a, 0.002)


@veg("pumpkin_ribbed")
def _(m, rng):
    prof = smooth_prof([(0, 0.06), (0.5, 0.0), (0.9, 0.15), (1.0, 0.5), (0.9, 0.85), (0.5, 1.0), (0.15, 0.9), (0, 0.8)], 3)
    rib = lambda x, y, z: (x * (1 + 0.1 * math.cos(10 * math.atan2(z, x))), y, z * (1 + 0.1 * math.cos(10 * math.atan2(z, x))))
    fruit_body(m, prof, 0.13, 0.19, (0, 0.0, 0.0), "tex:pumpkin", 40, 0.0, warp=rib, tile=(1, 1))
    tube3(m, spline([(0, 0.17, 0), (0.005, 0.2, 0.0), (0.02, 0.225, 0.01), (0.04, 0.23, 0.01)], 4), 0.012, "f_stem_brown", 8, disp=(0.001, 60))


@veg("chili_peppers_pile")
def _(m, rng):
    for k in range(9):
        a = k * 0.9
        L = 0.085 + 0.01 * (k % 3)
        prof = [(0.0, 0.0)] + [(0.0065 * (1 - (t * 0.92)) ** 0.8 * (1.0 if t > 0.03 else 0.7), L * t) for t in [i / 8 for i in range(1, 8)]] + [(0.0004, L)]
        lathe(m, prof, (0.0, 0.007 + 0.006 * (k // 3), 0.0), "tex:chili_red" if k % 3 else "tex:pepper_green", 7, uv="cyl", rot=(0, a, -PI / 2 + 0.1 * (k % 4)),
              warp=lambda x, y, z: (x + 0.01 * (y / 0.09) ** 2, y, z))
    for k in range(9):
        a = k * 0.9
        blob(m, (0.007, 0.004, 0.007), (0.0, 0.007 + 0.006 * (k // 3), 0.0), "f_stem", 6, 4, uv=None)


@veg("radish_bunch")
def _(m, rng):
    for k in range(6):
        x = -0.05 + 0.02 * k
        fruit_body(m, ONION, 0.015, 0.03, (x, 0.0, 0.0), "tex:radish", 12, 0.0006, rot=(0, 0, 0))
        tube3(m, [(x, 0.028, 0.0), (x + 0.005 * (k - 2.5) * 0.3, 0.036, 0.0)], 0.0025, "f_stem", 5)
        for q in range(3):
            wavy_leaf(m, (x + 0.012 * (q - 1) * 1.5, 0.045 + 0.01 * q, 0.0 + 0.01 * (q - 1)), 0.024, "tex:leaf_mint", 10, 0.004, 3, k + q, 0.0015)
    m.link((-0.05, 0.03, 0.0), (0.05, 0.03, 0.0), 0.0018, "f_hay", 4)


@veg("pea_pods_open")
def _(m, rng):
    for k in range(4):
        pod = [(0.0, 0.0)] + [(0.0095 * math.sin(PI * i / 12) ** 0.6, 0.085 * i / 12) for i in range(1, 12)] + [(0.0, 0.085)]
        lathe(m, pod, (-0.04, 0.0095, -0.045 + 0.02 * k), "tex:leaf", 8, uv="cyl", rot=(0, 0.1 * k, PI / 2), scale=(1.0, 1.0, 0.8),
              warp=lambda x, y, z: (x + 0.006 * (y / 0.085 - 0.5) ** 2, y, z))
    # an opened pod showing its peas
    lathe(m, [(0.0, 0.0), (0.0095, 0.0), (0.0095, 0.085), (0.0, 0.085)], (-0.04, 0.0, 0.05), "tex:leaf", 4, uv="cyl", rot=(0, 0.0, PI / 2), scale=(1.0, 0.3, 1.0))
    for k in range(7):
        blob(m, (0.0072, 0.0072, 0.0072), (-0.03 + 0.0115 * k, 0.0085, 0.05), "f_pea", 8, 6, uv=None)


@veg("asparagus_bundle")
def _(m, rng):
    for k in range(9):
        z = (k - 4) * 0.0105
        L = 0.24 + 0.012 * (k % 3)
        prof = [(0.0, 0.0)] + [(0.0048 * (1 - 0.0 * i / 8), L * i / 8) for i in range(1, 8)] + [(0.0058, L * 0.96), (0.0045, L * 0.985), (0.0, L)]
        lathe(m, prof, (-L / 2 + 0.0, 0.005 + 0.0 * k, z), "tex:leaf_mint" if k % 2 else "tex:spinach", 7, uv="cyl", rot=(0, 0, -PI / 2), tile=(1, 1))
    for xs in (-0.03, 0.04):
        m.box((0.004, 0.012, 0.1), (xs, 0.0072, 0.0), "f_hay", 0.0015)


# ================================================================ DELI
@deli("cheese_board")
def _(m, rng):
    slab(m, 0.4, 0.02, 0.26, (0, 0, 0), "tex:wood_board", "box", 0.006)
    # brie round with a cut wedge, cheddar block, swiss wedge
    lathe(m, [(0, 0), (0.055, 0.0), (0.056, 0.03), (0.0, 0.03)], (-0.12, 0.02, -0.04), "tex:cheese_brie", 24, uv="cyl", disp=(0.0006, 60))
    slab(m, 0.07, 0.04, 0.045, (0.08, 0.02, -0.07), "tex:cheese_cheddar", "box", 0.002, rot=(0, 0.2, 0))
    extrude(m, [(-0.04, -0.03), (0.04, -0.02), (0.04, 0.03), (-0.04, 0.025)], 0.035, (0.075, 0.02, 0.05), "tex:cheese_swiss", "tex:cheese_swiss", None, (0, 0.3, 0), 6.0)
    for k in range(4):
            slab(m, 0.045, 0.004, 0.045, (-0.13 + 0.012 * k, 0.02 + 0.0042 * k, 0.08), "tex:waffle", "box", 0.0015, rot=(0, 0.2 + 0.5 * k, 0))
    for k in range(9):
        a = k * 2.4
    for k in range(8):
        a = k * 2.4
        blob(m, (0.009, 0.009, 0.009), (-0.02 + 0.016 * (k % 4) + 0.008 * (k // 4), 0.029 + 0.009 * (k // 4) * 0.8, 0.045 + 0.014 * (k // 4) - 0.002 * (k % 2)), "tex:grape_skin", 8, 6, uv="sph")
    for k in range(6):
            blob(m, (0.011, 0.009, 0.008), (0.17 - 0.0, 0.0285, -0.08 + 0.018 * k), "f_nut", 8, 5, uv=None, rot=(0, k, 0))
    m.box((0.1, 0.002, 0.014), (0.0, 0.021, -0.1), "f_steel", 0.0005, rot=(0, 0.1, 0))


@deli("charcuterie_board")
def _(m, rng):
    slab(m, 0.42, 0.018, 0.28, (0, 0, 0), "tex:wood_walnut", "box", 0.006)
    for k in range(8):
        disc(m, 0.03, 0.0026, (-0.14 + 0.03 * (k % 4) + 0.015 * (k // 4), 0.018 + 0.0027 * (k % 3), -0.085 + 0.045 * (k // 4)), "tex:salami", 18, uv="top", edge=0.5)
    for k in range(5):
        a = k * 0.5
        blob(m, (0.026, 0.012, 0.02), (0.07 + 0.018 * k - 0.0, 0.026 + 0.0 * k, -0.065 + 0.012 * (k % 2)), "tex:ham", 14, 8, uv="sph", rot=(0, a, 0.0), disp=(0.003, 60))
    vessel(m, bowl_outer(0.04, 0.03, 0.4, 6), 0.002, (-0.11, 0.018, 0.07), "f_plate", 20)
    for (x, y, z) in heap(rng, 12, 0.024, 0.014, 0.4):
        blob(m, (0.0075, 0.0065, 0.0075), (-0.11 + x, 0.026 + y, 0.07 + z), "f_olive", 7, 5, uv=None)
    for k in range(5):
        slab(m, 0.05, 0.005, 0.05, (0.0 + 0.01 * k, 0.018 + 0.0052 * k, 0.07), "tex:bread_crust", "box", 0.002, rot=(0, 0.25 * k, 0))
    for k in range(5):
        blob(m, (0.012, 0.01, 0.007), (0.12 + 0.012 * (k % 3), 0.024, 0.05 + 0.014 * k * 0.5), "f_nut", 8, 5, uv=None, rot=(0, k, 0))
    for k in range(4):
        slab(m, 0.016, 0.014, 0.016, (0.14 - 0.0, 0.018, 0.1 - 0.017 * k), "f_pea", "box", 0.003, rot=(0, k, 0))
    for k in range(6):
        blob(m, (0.012, 0.009, 0.009), (-0.04 + 0.02 * k, 0.025, 0.105), "f_pepper_flake", 8, 5, uv=None, rot=(0, 0.2 * k, 0.0)) if k < 4 else None


@deli("parmesan_wheel_wedge")
def _(m, rng):
    R, H = 0.18, 0.12
    lathe(m, [(0.0, 0.0), (R, 0.0), (R + 0.006, H * 0.12), (R + 0.006, H * 0.88), (R, H), (0.0, H)], (0, 0.0, 0.0), "tex:cheese_cheddar", 40, uv="cyl", disp=(0.0008, 40), tile=(2, 1))
    # cut wedge removed: stack a lighter wedge next to the wheel
    extrude(m, [(0.0, 0.0), (0.16, -0.04), (0.16, 0.04)], 0.1, (0.22, 0.0, 0.0), "tex:cheese_swiss", "tex:cheese_cheddar", None, (0, 0.0, 0.0), 5.0)
    for k in range(10):
        a = k * 2.0
        blob(m, (0.008, 0.002, 0.005), (0.3 - 0.0 * k + 0.01 * math.cos(a), 0.101, 0.02 * math.sin(a * 1.3)), "f_cheese_white", 5, 3, uv=None, rot=(0, a, 0))


@deli("ham_leg_stand")
def _(m, rng):
    m.box((0.5, 0.05, 0.2), (0, 0.025, 0), "f_wood_dark", 0.008)
    m.box((0.46, 0.012, 0.16), (0, 0.056, 0), "f_wood_light", 0.003)
    leg = smooth_prof([(0, 0.0), (0.18, 0.02), (0.55, 0.15), (0.9, 0.28), (1.0, 0.5), (0.9, 0.75), (0.6, 0.92), (0.35, 0.98), (0, 1.0)], 3)
    lathe(m, scaled(leg, 0.075, 0.45), (-0.22, 0.14, 0.0), "tex:salami", 22, uv="cyl", rot=(0, 0, -PI / 2), disp=(0.004, 22), scale=(1.0, 1.0, 0.9))
    blob(m, (0.02, 0.018, 0.02), (0.235, 0.14, 0.0), "f_cream", 10, 8, uv=None)
    for k in range(5):
        m.box((0.06, 0.0015, 0.04), (0.12 + 0.006 * k, 0.0665 + 0.0017 * k, 0.045), "f_ginger", 0.0005, rot=(0, 0.3 * k, 0.0))


@deli("sausage_plate")
def _(m, rng):
    from .food import plate
    plate(m, 0.15, "f_plate_cream")
    y = 0.008
    for k in range(3):
        z = -0.05 + 0.04 * k
        pts = spline([(-0.1, y + 0.016, z), (-0.03, y + 0.019, z + 0.006 * (k - 1)), (0.04, y + 0.019, z), (0.1, y + 0.016, z - 0.004 * (k - 1))], 4)
        tube3(m, pts, 0.0165, "tex:sausage", 10, uv=True, tile=(1, 4), disp=(0.0007, 60))
    blob(m, (0.05, 0.014, 0.03), (-0.04, y + 0.014, 0.075), "f_cream", 16, 8, uv=None, disp=(0.004, 60))
    tube3(m, [(0.02 + 0.0095 * k, y + 0.0, 0.07 + 0.008 * (-1) ** k) for k in range(9)], 0.0032, "f_butter", 5)


@deli("egg_carton_dozen")
def _(m, rng):
    m.box((0.31, 0.012, 0.155), (0, 0.006, 0), "f_cardboard", 0.003)
    for i in range(6):
        for j in range(2):
            x, z = -0.1275 + i * 0.051, -0.039 + j * 0.078
            lathe(m, [(0.0, 0.0), (0.0185, 0.0), (0.0225, 0.022), (0.0, 0.022)], (x, 0.012, z), "f_cardboard", 10)
            blob(m, (0.0215, 0.0295, 0.0215), (x, 0.031, z), "tex:eggshell_brown" if (i + j) % 3 else "tex:eggshell_white", 14, 10, uv="sph")
    # lid, open and leaning back
    m.box((0.31, 0.003, 0.15), (0.0, 0.085, -0.1), "f_cardboard", 0.002, rot=(-1.1, 0.0, 0.0))


@deli("butter_dish_and_knife")
def _(m, rng):
    m.box((0.17, 0.012, 0.11), (0, 0.006, 0), "f_plate", 0.004)
    slab(m, 0.12, 0.034, 0.055, (0, 0.012, 0), "f_butter", "box", 0.004, rot=(0, 0.0, 0), disp=(0.0006, 60))
    m.box((0.1, 0.0015, 0.016), (0.0, 0.0125, 0.075), "f_steel", 0.0005, rot=(0, 0.1, 0))


@deli("jam_jars_trio")
def _(m, rng):
    cols = ("tex:jam", "tex:honey", "tex:peanut_butter")
    caps = ("f_cap_red", "f_cap_gold", "f_cap_green")
    for k in range(3):
        x = (k - 1) * 0.085
        R, H = 0.0325 + 0.002 * (k % 2), 0.085 + 0.012 * k
        vessel(m, [(0, 0), (R * 0.9, 0.0), (R, 0.004), (R, H * 0.8), (R * 0.82, H)], 0.002, (x, 0.0, 0.0), "f_glass", 22)
        lathe(m, [(0, 0.003), (R - 0.002, 0.003), (R - 0.002, H * 0.78), (0.0, H * 0.78)], (x, 0.0, 0.0), cols[k], 20, uv="cyl")
        m.cyl(R * 0.85, 0.016, (x, H + 0.006, 0.0), caps[k], seg=20, bevel=0.0)
        m.box((R * 1.3, H * 0.36, 0.0012), (x, H * 0.42, R * 0.97), "f_label_cream", 0.0003)


@deli("honey_pot_dipper")
def _(m, rng):
    outer = [(0.0, 0.0), (0.03, 0.0), (0.05, 0.03), (0.057, 0.065), (0.045, 0.09), (0.036, 0.098)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 26)
    lathe(m, [(0, 0.003), (0.0285, 0.003), (0.0475, 0.03), (0.0545, 0.065), (0.0425, 0.085), (0.0, 0.085)], (0, 0, 0), "tex:honey", 24, uv="cyl")
    # dipper with honey drizzle
    m.link((0.0, 0.03, 0.0), (0.0, 0.14, 0.0), 0.004, "f_wood_light", 6)
    for k in range(9):
        m.cyl(0.0075 + 0.0015 * math.sin(PI * k / 8), 0.0042, (0.0, 0.1 + 0.0042 * k, 0.0), "f_wood_light", seg=10)
    tube3(m, [(0.0, 0.1, 0.0), (0.003, 0.088, 0.004), (0.005, 0.086, 0.01)], 0.0022, "tex:honey", 5)


# ================================================================ HYDROPONIC HARVEST CRATES (floor)
@harvest("crate_lettuce")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.2, "f_tray_grey")
    for k in range(9):
        a = k * 2.399
        r = 0.2 * math.sqrt((k + 0.5) / 9)
        x, z = r * 0.95 * math.cos(a) * 1.3, r * math.sin(a) * 0.95
        z = max(-0.15, min(0.15, z))
        x = max(-0.24, min(0.24, x))
        blob(m, (0.085, 0.07, 0.085), (x, y + 0.075, z), "tex:lettuce", 12, 7, uv="sph", disp=(0.006, 22))
        for q in range(3):
            wavy_leaf(m, (x + 0.05 * math.cos(q * 2.1 + k), y + 0.12 + 0.01 * (k % 2), z + 0.05 * math.sin(q * 2.1 + k)), 0.05, "tex:lettuce", 10, 0.01, 5, q + k, 0.0018)


@harvest("crate_tomatoes")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.2, "f_tray_blue")
    for (x, h, z) in heap(rng, 32, 0.22, 0.09, 0.4):
        x = max(-0.25, min(0.25, x * 1.22))
        z = max(-0.15, min(0.15, z * 0.78))
        fruit_body(m, TOMATO, 0.037, 0.06, (x, y + 0.02 + h * 1.0, z), "tex:tomato_skin", 9, 0.0, lo=True, rot=(0, x * 40, 0))
    for k in range(4):
        calyx(m, (-0.15 + 0.1 * k, y + 0.115 + 0.01 * (k % 3), 0.01 * k), 0.012, 4, "f_herb")


@harvest("crate_herbs")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.14, "f_tray_grey", slots=2)
    mats = ("tex:leaf_basil", "tex:leaf_mint", "tex:herb_dill")
    for b in range(9):
        x = -0.24 + 0.06 * (b % 5) * 1.0 if b < 5 else -0.18 + 0.12 * (b - 5)
        z = -0.1 if b < 5 else 0.09
        mt = mats[b % 3]
        for q in range(9):
            a = q * 0.7 + b
            sp = (q - 4) * 0.012
            blob(m, (0.026, 0.004, 0.017), (x + 0.025 * math.cos(a) * 0.8, y + 0.04 + 0.012 * (q % 3), z + 0.03 * math.sin(a) * 0.8), mt, 6, 3, uv="sph", rot=(0.3, a, 0.2))
            del sp
        tube3(m, [(x, y + 0.006, z - 0.03), (x, y + 0.04, z)], 0.0028, "f_stem", 5)
    for b in range(3):
        m.link((-0.2 + 0.2 * b, y + 0.06, -0.0), (-0.2 + 0.2 * b + 0.03, y + 0.06, 0.0), 0.0018, "f_hay", 4)


@harvest("crate_strawberries")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.14, "f_cardboard", slots=2)
    for k, (x, h, z) in enumerate(heap(rng, 42, 0.22, 0.07, 0.4)):
        x = max(-0.26, min(0.26, x * 1.25))
        z = max(-0.16, min(0.16, z * 0.8))
        a = k * 1.9
        fruit_body(m, BERRY, 0.019, 0.04, (x, y + 0.01 + h, z), "tex:strawberry", 8, 0.0, lo=True, rot=(0.6 * math.sin(a), a, 0.7 * math.cos(a)))
        blob(m, (0.011, 0.004, 0.011), (x, y + 0.01 + h + 0.034, z), "f_herb", 6, 3, uv=None)


@harvest("crate_peppers")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.22, "f_tray_grey")
    prof = smooth_prof([(0, 0.06), (0.5, 0.0), (0.9, 0.2), (1.0, 0.55), (0.92, 0.88), (0.5, 0.98), (0.25, 1.0), (0.0, 0.86)], 1)
    cols = ("tex:pepper_red", "tex:pepper_yellow", "tex:pepper_green", "tex:pepper_red")
    for k, (x, h, z) in enumerate(heap(rng, 22, 0.2, 0.07, 0.4)):
        x = max(-0.23, min(0.23, x * 1.15))
        z = max(-0.14, min(0.14, z * 0.7))
        fruit_body(m, prof, 0.042, 0.085, (x, y + 0.02 + h, z), cols[k % 4], 9, 0.0, lo=True, rot=(0.3 * math.sin(k), k, 0.3 * math.cos(k)))
        m.cyl(0.006, 0.014, (x, y + 0.02 + h + 0.088, z), "f_stem", seg=6)


@harvest("crate_potatoes")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.24, "f_cardboard", slots=3)
    for k, (x, h, z) in enumerate(heap(rng, 20, 0.2, 0.08, 0.4)):
        x = max(-0.23, min(0.23, x * 1.2))
        z = max(-0.14, min(0.14, z * 0.75))
        blob(m, (0.05, 0.035, 0.04), (x, y + 0.04 + h, z), "tex:potato_skin", 10, 7, uv="sph", disp=(0.006, 22), rot=(0, k * 1.3, 0))


@harvest("tray_mushrooms")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.09, "f_cardboard", slots=1)
    m.box((0.54, 0.03, 0.34), (0, y + 0.015, 0), "soil", 0.004)
    for k in range(18):
        a = k * 2.399
        r = math.sqrt((k + 0.5) / 18)
        x, z = 0.25 * r * math.cos(a), 0.15 * r * math.sin(a)
        s = 0.7 + 0.5 * ((k * 7) % 5) / 5
        lathe(m, [(0.0, 0.0), (0.008 * s, 0.0), (0.009 * s, 0.03 * s)], (x, y + 0.03, z), "tex:mushroom_stem", 8, uv="cyl")
        lathe(m, scaled(smooth_prof([(0, 0.35), (0.6, 0.3), (1.0, 0.5), (0.8, 0.85), (0.4, 1.0), (0, 1.0)], 2), 0.02 * s, 0.03 * s), (x, y + 0.03 + 0.02 * s, z),
              "tex:mushroom_cap" if k % 3 else "tex:mushroom_white", 10, uv="sph")


@harvest("crate_cabbages")
def _(m, rng):
    y = crate(m, 0.6, 0.4, 0.2, "f_wood_dark", slots=2)
    for k, (x, z, mat) in enumerate(((-0.14, -0.06, "tex:cabbage"), (0.1, -0.07, "tex:cabbage"), (-0.02, 0.07, "tex:cabbage_red"), (0.17, 0.08, "tex:cabbage"))):
        blob(m, (0.095, 0.09, 0.095), (x, y + 0.09, z), mat, 18, 12, uv="sph", disp=(0.005, 20), tile=(2, 2))
        for q in range(4):
            a = q * 1.6 + k
            wavy_leaf(m, (x + 0.07 * math.cos(a), y + 0.04, z + 0.07 * math.sin(a)), 0.065, mat, 14, 0.012, 5, a, 0.003)


# ================================================================ HANGING PRODUCE (wall, hung from a hook board)
@hanging("garlic_braid")
def _(m, rng):
    m.box((0.12, 0.05, 0.016), (0, 0.0, 0.008), "f_wood_dark", 0.003)
    m.link((0.0, -0.01, 0.014), (0.0, -0.45, 0.04), 0.0045, "f_hay", 6)
    for k in range(11):
        y = -0.07 - 0.036 * k
        side = -1 if k % 2 else 1
        x = side * (0.028 - 0.0012 * k)
        fruit_body(m, ONION, 0.03 - 0.0007 * k, 0.045 - 0.001 * k, (x, y - 0.03, 0.04 + 0.0), "tex:garlic", 12, 0.0006)
        tube3(m, [(0.0, y + 0.012, 0.04), (x, y - 0.0, 0.04)], 0.0026, "f_hay", 4, caps=False)


@hanging("chili_ristra")
def _(m, rng):
    m.box((0.1, 0.04, 0.016), (0, 0.0, 0.008), "f_wood_light", 0.003)
    m.link((0.0, -0.005, 0.012), (0.0, -0.62, 0.03), 0.0026, "f_hay", 5)
    for k in range(16):
        y = -0.05 - 0.036 * k
        for side in (-1, 1):
            if k > 12 and side == 1:
                continue
            L = 0.1 - 0.0015 * k
            prof = [(0.0, 0.0)] + [(0.011 * (1 - t) ** 0.7 * (0.5 if t < 0.04 else 1.0), L * t) for t in [i / 8 for i in range(1, 8)]] + [(0.0004, L)]
            lathe(m, prof, (side * 0.012, y, 0.03 + 0.003 * side), "tex:chili_red", 7, uv="cyl", rot=(0, 0, side * (0.25 + 0.04 * (k % 3)) + PI), warp=lambda x, yy, z: (x, yy, z + 0.004 * (yy / 0.1) ** 2))


@hanging("herb_bundles")
def _(m, rng):
    m.box((0.5, 0.03, 0.02), (0, 0.0, 0.01), "f_wood_dark", 0.004)
    for k, mat in enumerate(("tex:leaf_basil", "tex:herb_dill", "tex:leaf_mint", "tex:spinach")):
        x = -0.18 + 0.12 * k
        m.link((x, -0.01, 0.02), (x, -0.07, 0.03), 0.002, "f_hay", 4)
        for q in range(14):
            a = q * 0.9 + k
            tube3(m, [(x, -0.07, 0.03), (x + 0.02 * math.cos(a), -0.15 - 0.012 * (q % 3), 0.035 + 0.02 * math.sin(a)), (x + 0.035 * math.cos(a), -0.24 - 0.02 * (q % 4), 0.04 + 0.03 * math.sin(a))],
                  0.0012, "f_stem", 3, caps=False)
            blob(m, (0.02, 0.01, 0.005), (x + 0.03 * math.cos(a), -0.2 - 0.02 * (q % 3), 0.04 + 0.027 * math.sin(a)), mat, 6, 4, uv="sph", rot=(0.4, a, 0.3))
        m.torus(0.011, 0.002, (x, -0.085, 0.03), "f_hay", axis="y", seg=8, tseg=4)


@hanging("sausage_links_hanging")
def _(m, rng):
    m.box((0.3, 0.03, 0.02), (0, 0.0, 0.01), "f_steel_dark", 0.003)
    for k in range(4):
        x = -0.1 + 0.067 * k
        m.link((x, -0.01, 0.02), (x, -0.06, 0.03), 0.0012, "f_hay", 4)
        for q in range(3 if k != 1 else 4):
            y = -0.1 - 0.075 * q
            blob(m, (0.0165, 0.04, 0.0165), (x, y, 0.03), "tex:salami" if k % 2 == 0 else "tex:sausage", 12, 8, uv="sph", disp=(0.0008, 60))
            m.cyl(0.0075, 0.006, (x, y + 0.04, 0.03), "f_hay", seg=6)


menu.register()
