"""Realistic food models, part 2: plated meals and dishes (burgers, pizza, noodles, steak, sushi, salads, pasta ...)."""
import math

from .food import plate, wavy_leaf, wedge, wobble
from .foodkit import PI, TAU, Menu, blob, disc, dome, lathe, seeds, slab, spline, sprig, tube3, vessel, bowl_outer

menu = Menu()
meal = menu.cat("meal", tags=("food", "meal"))


# ---------------------------------------------------------------- helpers
def bowl(m, R, h, mat="f_plate", pos=(0, 0, 0), t=0.004, seg=30, foot=0.4):
    """Round bowl; returns the inner rim radius."""
    vessel(m, bowl_outer(R, h, foot), t, pos, mat, seg)
    return R - t


def noodles(m, rng, cx, cz, y, rad, n, mat="tex:noodle", r=0.0016, wig=0.012, length=1.8):
    """Wavy noodle strands lying in a disc of radius `rad` at height y."""
    for k in range(n):
        a = rng.random() * TAU
        off = (rng.random() - 0.5) * rad * 1.4
        pts = []
        ph = rng.random() * TAU
        for i in range(14):
            t = (i / 13 - 0.5) * rad * 2 * length * 0.5
            x = t
            z = off + wig * math.sin(i * 1.1 + ph)
            if math.hypot(x, z) > rad:
                continue
            pts.append((cx + x * math.cos(a) - z * math.sin(a), y + 0.003 * math.sin(i * 0.9 + ph) + 0.002 * (k % 3), cz + x * math.sin(a) + z * math.cos(a)))
        if len(pts) >= 3:
            tube3(m, pts, r, mat, 5, uv=True, tile=(1, 8))


def pepper_ring(m, pos, r=0.012, mat="f_pepper_flake"):
    m.torus(r, r * 0.3, pos, mat, seg=10, tseg=5)


def lemon_wedge(m, pos, rot=0.0, s=1.0):
    wedge(m, 0.024 * s, 0.014 * s, 60, pos, "f_lemon_flesh", rot_y=rot)


def chopsticks(m, pos, ang=0.0, L=0.21, y=0.0):
    for k in (-1, 1):
        a = ang
        dx, dz = math.cos(a), math.sin(a)
        ox, oz = -dz * 0.007 * k, dx * 0.007 * k
        m.link((pos[0] + ox - dx * L / 2, pos[1], pos[2] + oz - dz * L / 2), (pos[0] + ox + dx * L / 2, pos[1] + y, pos[2] + oz + dz * L / 2), 0.0026, "f_wood_dark", 6)


# ================================================================ MEALS
@meal("burger_with_fries")
def _(m, rng):
    plate(m, 0.14, "f_plate_blue")
    y = 0.009
    cx = -0.025
    # bottom bun, patty, cheese, tomato, lettuce, top bun
    disc(m, 0.052, 0.018, (cx, y, 0), "tex:bread_crust", 24, uv="auto", disp=(0.0012, 40), edge=0.9)
    y1 = y + 0.016
    wavy_leaf(m, (cx, y1, 0), 0.062, "tex:lettuce", 28, 0.006, 7, 0.3)
    y2 = y1 + 0.004
    for (dx, dz) in ((-0.014, 0.01), (0.016, -0.012)):
        disc(m, 0.026, 0.007, (cx + dx, y2, dz), "f_tomato", 16, uv=None, edge=0.5)
    disc(m, 0.054, 0.02, (cx, y2 + 0.004, 0), "tex:patty", 28, uv="auto", disp=(0.0016, 50), edge=0.9)
    slab(m, 0.098, 0.003, 0.098, (cx, y2 + 0.022, 0), "f_cheese_yellow", "box", 0.0008, rot=(0, 0.78, 0),
         warp=lambda x, yy, z: (x, yy - 0.012 * max(0.0, (abs(x) + abs(z) - 0.06)) * 6, z))
    dome(m, 0.056, 0.045, (cx, y2 + 0.024, 0), "tex:bread_crust", 26, 8, disp=(0.0015, 35), uv="sph", tile=(2, 1))
    for k in range(16):
        a = k * 2.399
        rr = 0.036 * math.sqrt((k + 0.5) / 16)
        xx, zz = rr * math.cos(a), rr * math.sin(a)
        hh = 0.045 * math.sqrt(max(0.0, 1 - (rr / 0.056) ** 2))
        blob(m, (0.0036, 0.0017, 0.0022), (cx + xx, y2 + 0.024 + hh * 0.98, zz), "f_sesame", 5, 3, uv=None, rot=(0, a, 0))
    for k in range(18):
        a = k * 0.35
        m.box((0.075, 0.009, 0.009), (0.065 + 0.0 * k, 0.0095 + 0.0045 + 0.007 * (k % 3), -0.045 + 0.007 * k), "f_fry", 0.0015, rot=(0, 0.3 + 0.1 * math.sin(k * 2.1), 0.05 * math.cos(k)))


@meal("double_cheeseburger")
def _(m, rng):
    m.box((0.2, 0.004, 0.2), (0, 0.002, 0), "f_napkin", 0.001, rot=(0, 0.2, 0))
    m.box((0.16, 0.0045, 0.16), (0, 0.0045, 0), "f_paper", 0.001, rot=(0, 0.2, 0))
    y = 0.007
    disc(m, 0.05, 0.018, (0, y, 0), "tex:bread_crust", 24, uv="auto", disp=(0.0012, 40), edge=0.9)
    y += 0.017
    disc(m, 0.05, 0.007, (0.0, y, 0.0), "f_onion", 20, uv=None, edge=0.4)
    for k in range(2):
        y += 0.006 if k == 0 else 0.0
        disc(m, 0.052, 0.018, (0, y + 0.004, 0), "tex:patty", 26, uv="auto", disp=(0.0015, 50), edge=0.9)
        slab(m, 0.095, 0.0028, 0.095, (0, y + 0.0215, 0), "f_cheese_yellow", "box", 0.0008, rot=(0, 0.78 + k * 0.4, 0),
             warp=lambda x, yy, z: (x, yy - 0.012 * max(0.0, (abs(x) + abs(z) - 0.055)) * 6, z))
        y += 0.025
    for k in range(3):
        disc(m, 0.017, 0.003, (0.03 * math.cos(k * 2.1), y + 0.0005, 0.03 * math.sin(k * 2.1)), "f_olive", 10, uv=None)
    wavy_leaf(m, (0, y + 0.002, 0), 0.058, "tex:lettuce", 26, 0.006, 6, 1.2)
    disc(m, 0.03, 0.007, (0.01, y + 0.008, 0.01), "f_tomato", 16, uv=None, edge=0.5)
    dome(m, 0.056, 0.042, (0, y + 0.01, 0), "tex:bread_crust", 26, 8, disp=(0.0015, 35), uv="sph", tile=(2, 1))
    m.link((0.0, y + 0.02, 0.0), (0.0, y + 0.07, 0.0), 0.0016, "f_wood_light", 5)
    blob(m, (0.007, 0.007, 0.007), (0.0, y + 0.072, 0.0), "f_olive", 8, 6, uv=None)


@meal("club_sandwich")
def _(m, rng):
    plate(m, 0.14, "f_plate_dark")
    y0 = 0.009
    tri = [(-0.045, -0.045), (0.045, -0.045), (-0.045, 0.045)]
    for q, (px, pz, rot) in enumerate(((-0.045, 0.02, 0.3), (0.055, -0.02, 3.5))):
        y = y0
        for mat, h in (("f_dough", 0.011), ("f_herb", 0.003), ("f_ginger", 0.006), ("f_dough", 0.011), ("f_tomato", 0.005),
                       ("f_wasabi", 0.003), ("f_cheese_white", 0.003), ("f_dough", 0.011)):
            m.prism(tri, h, (px, y, pz), mat, "xz", rot=(0, rot, 0))
            y += h
        m.link((px, y - 0.04, pz), (px, y + 0.03, pz), 0.0013, "f_wood_light", 5)
        blob(m, (0.005, 0.005, 0.005), (px, y + 0.031, pz), "f_olive", 6, 4, uv=None)
    for k in range(14):
        a = k * 0.8
    for k in range(10):
        a = k * 0.9
        blob(m, (0.02, 0.0035, 0.015), (-0.03 + 0.05 * (k % 5) * 0.5, 0.0115 + 0.003 * (k // 3), -0.09 + 0.01 * (k % 3)), "f_chip", 8, 4, uv=None, rot=(0.15, a, 0.1))


@meal("hot_dog_mustard")
def _(m, rng):
    m.prism([(-0.1, -0.075), (0.1, -0.075), (0.1, 0.075), (-0.1, 0.075)], 0.003, (0, 0, 0), "f_paper", "xz")
    bun = [(0.0, -0.095), (0.026, -0.09), (0.036, -0.05), (0.038, 0.0), (0.036, 0.05), (0.026, 0.09), (0.0, 0.095)]
    lathe(m, bun, (0, 0.03, 0), "tex:bread_crust", 18, rot=(0, 0, PI / 2), scale=(1, 1, 0.8), uv="cyl", disp=(0.001, 40), tile=(1, 2))
    # split: darker crumb slot on top
    slab(m, 0.17, 0.004, 0.03, (0, 0.0555, 0), "tex:bread_crumb", "box", 0.001)
    pts = spline([(-0.1, 0.06, 0.0), (-0.05, 0.062, 0.002), (0.05, 0.062, -0.002), (0.1, 0.06, 0.0)], 5)
    tube3(m, pts, [0.0145] * len(pts), "tex:sausage", 10, uv=True, flat=1.0, tile=(1, 4), disp=(0.0007, 60))
    zig = [(-0.07 + 0.0094 * k, 0.0775 + 0.0, 0.007 * (1 if k % 2 else -1)) for k in range(16)]
    tube3(m, zig, 0.0018, "f_butter", 5)
    zig2 = [(-0.066 + 0.0094 * k, 0.0775 + 0.0, 0.007 * (-1 if k % 2 else 1)) for k in range(15)]
    tube3(m, zig2, 0.0018, "f_tomato", 5)
    seeds(m, rng, 14, (0, 0, 0.07, 0.01), 0.0, "f_onion", (0.003, 0.0018, 0.003), ground=lambda x, z: 0.078)


@meal("pizza_margherita")
def _(m, rng):
    m.cyl(0.165, 0.004, (0, 0.002, 0), "f_steel", seg=40)
    m.torus(0.165, 0.003, (0, 0.0045, 0), "f_steel", seg=40, tseg=6)
    prof = [(0.0, 0.0), (0.145, 0.0), (0.15, 0.004), (0.152, 0.012), (0.147, 0.017), (0.133, 0.014), (0.0, 0.006)]
    lathe(m, prof, (0, 0.004, 0), "tex:pizza_crust", 44, uv="cyl", disp=(0.0015, 30), warp=wobble(5, 0.5, 0.012), tile=(3, 1))
    lathe(m, [(0.0, 0.0), (0.138, 0.0), (0.138, 0.004), (0.0, 0.004)], (0, 0.0105, 0), "tex:pizza_top", 44, uv="top", disp=(0.001, 40))
    for k in range(9):
        a = k * 2.399 + 0.4
        rr = 0.105 * math.sqrt((k + 0.4) / 9)
        blob(m, (0.024, 0.0075, 0.024), (rr * math.cos(a), 0.0165, rr * math.sin(a)), "f_cheese_white", 12, 6, uv=None, disp=(0.002, 50))
    for k in range(7):
        a = k * 2.5 + 1.0
        rr = 0.09 * math.sqrt((k + 0.7) / 7)
        wavy_leaf(m, (rr * math.cos(a), 0.0195, rr * math.sin(a)), 0.016, "tex:leaf_basil", 10, 0.004, 3, a, 0.0015)
    for k in range(6):
        a = k * PI / 3 * 0.5 + 0.2


@meal("pizza_pepperoni")
def _(m, rng):
    m.cyl(0.165, 0.004, (0, 0.002, 0), "f_steel", seg=40)
    prof = [(0.0, 0.0), (0.145, 0.0), (0.15, 0.004), (0.152, 0.012), (0.147, 0.017), (0.133, 0.014), (0.0, 0.006)]
    lathe(m, prof, (0, 0.004, 0), "tex:pizza_crust", 44, uv="cyl", disp=(0.0015, 30), warp=wobble(7, 0.9, 0.012), tile=(3, 1))
    lathe(m, [(0.0, 0.0), (0.138, 0.0), (0.138, 0.004), (0.0, 0.004)], (0, 0.0105, 0), "tex:pizza_top", 44, uv="top", disp=(0.001, 40))
    for k in range(17):
        a = k * 2.399
        rr = 0.118 * math.sqrt((k + 0.5) / 17)
        disc(m, 0.0165, 0.0035, (rr * math.cos(a), 0.0145, rr * math.sin(a)), "tex:pepperoni", 14, uv="top", disp=(0.0005, 80), edge=0.9)
    for k in range(9):
        a = k * 2.399 + 1.3
        rr = 0.12 * math.sqrt((k + 0.5) / 9)
        m.torus(0.005, 0.0018, (rr * math.cos(a), 0.0178, rr * math.sin(a)), "f_olive_black", seg=10, tseg=5)
    for k in range(5):
        a = k * 1.7
        blob(m, (0.012, 0.0018, 0.004), (0.07 * math.cos(a), 0.0172, 0.07 * math.sin(a)), "f_herb", 6, 4, uv=None, rot=(0, a, 0))


@meal("ramen_bowl")
def _(m, rng):
    R = 0.105
    vessel(m, bowl_outer(R, 0.085, 0.38, 8), 0.0045, (0, 0, 0), "f_plate_dark", 32)
    lathe(m, [(0, 0), (R - 0.006, 0), (R - 0.006, 0.001), (0, 0.001)], (0, 0.07, 0), "tex:broth", 32, uv="top")
    noodles(m, rng, 0.0, 0.0, 0.0715, 0.088, 22, "tex:noodle", 0.0019, 0.014, 1.9)
    # toppings: chashu, egg halves, nori, scallions, naruto
    for k in range(2):
        disc(m, 0.03, 0.005, (-0.04, 0.076 + k * 0.0035, -0.02 + k * 0.012), "tex:ham", 18, uv="top", edge=0.7, rot=(0.1, k * 0.9, 0.05))
    for (ex, ez) in ((0.035, 0.045), (0.05, 0.02)):
        blob(m, (0.0215, 0.015, 0.027), (ex, 0.0775, ez), "f_egg_white", 16, 10, uv=None, rot=(0, 0.5, 0))
        blob(m, (0.0125, 0.0075, 0.015), (ex, 0.088, ez), "f_yolk", 12, 8, uv=None, rot=(0, 0.5, 0))
    slab(m, 0.05, 0.075, 0.002, (0.0, 0.0735, -0.062), "f_nori", "box", 0.0005, rot=(-0.3, 0.1, 0.0))
    for k in range(14):
        a = k * 2.4
        rr = 0.015 + 0.02 * (k % 4) / 3
        m.torus(0.0035, 0.0012, (0.0 + rr * math.cos(a), 0.0745 + 0.002 * (k % 3), 0.01 + rr * math.sin(a)), "f_scallion", seg=8, tseg=4)
    disc(m, 0.012, 0.004, (0.0, 0.08, 0.04), "f_white", 12, uv=None)
    m.torus(0.006, 0.0018, (0.0, 0.0825, 0.04), "f_tuna", seg=12, tseg=4)
    chopsticks(m, (0.02, 0.098, 0.0), 0.25, 0.23, 0.0)


@meal("steak_dinner")
def _(m, rng):
    plate(m, 0.15, "f_plate_dark", rim="f_cap_gold")
    y = 0.008
    blob(m, (0.066, 0.017, 0.052), (-0.025, y + 0.012, -0.012), "tex:steak", 24, 12, uv="box", disp=(0.0022, 36), rot=(0, 0.35, 0), tile=(1, 1))
    blob(m, (0.032, 0.025, 0.032), (0.065, y + 0.018, 0.035), "f_cream", 18, 10, uv=None, disp=(0.003, 40))
    sprig(m, (0.065, y + 0.043, 0.035), "f_herb", 3, 0.014, rng)
    for k in range(9):
        tube3(m, [(-0.065 + 0.0 * k, y + 0.004 + 0.0045 * (k % 3), 0.055 + 0.0035 * k), (-0.045, y + 0.007 + 0.0045 * (k % 3), 0.0555 + 0.0035 * k), (-0.022, y + 0.004 + 0.0045 * (k % 3), 0.05 + 0.0035 * k)],
              0.0035, "f_bean_green", 6)
    blob(m, (0.016, 0.014, 0.016), (-0.07, y + 0.014, -0.07), "tex:tomato_skin", 12, 8, uv="sph")
    lathe(m, [(0, 0), (0.026, 0), (0.032, 0.0008), (0.026, 0.0018), (0, 0.0022)], (0.04, y, -0.06), "f_chocolate_dark", 20, warp=wobble(4, 0.5, 0.2))


@meal("roast_chicken")
def _(m, rng):
    lathe(m, [(0, 0), (0.17, 0), (0.19, 0.012), (0.2, 0.026), (0.185, 0.03), (0.17, 0.014), (0, 0.012)], (0, 0, 0), "f_plate", 40, scale=(1.0, 1.0, 0.68))
    y = 0.016
    # the bird lies on its back: carcass along z (neck end -z), breast ridge on top, thighs and drumsticks at the +z end
    blob(m, (0.075, 0.058, 0.105), (0.0, y + 0.05, -0.0), "tex:chicken_skin", 26, 16, uv="sph", disp=(0.003, 22), tile=(2, 1))
    for sgn in (-1, 1):
        blob(m, (0.042, 0.034, 0.075), (sgn * 0.034, y + 0.088, -0.012), "tex:chicken_skin", 18, 12, uv="sph", disp=(0.002, 30))
        blob(m, (0.026, 0.03, 0.05), (sgn * 0.068, y + 0.062, -0.045), "tex:chicken_skin", 12, 8, uv="sph", disp=(0.002, 30))
        thigh = [(sgn * 0.048, y + 0.05, 0.062), (sgn * 0.085, y + 0.045, 0.09), (sgn * 0.1, y + 0.03, 0.135), (sgn * 0.09, y + 0.02, 0.17)]
        pts = spline(thigh, 4)
        tube3(m, pts, [0.034 - 0.022 * i / (len(pts) - 1) for i in range(len(pts))], "tex:chicken_skin", 12, uv=True, tile=(2, 2), disp=(0.0012, 40))
        blob(m, (0.007, 0.007, 0.011), (sgn * 0.089, y + 0.02, 0.182), "f_cream", 8, 6, uv=None)
        tube3(m, [(sgn * 0.09, y + 0.02, 0.17), (sgn * 0.088, y + 0.02, 0.185)], 0.0045, "f_cream", 6)
    for k in range(7):
        a = k * 0.9 + 0.4
        px, pz = 0.145 * math.cos(a) * 1.15, 0.1 * math.sin(a) * 1.0
        if abs(px) > 0.1 or pz < -0.04:
            blob(m, (0.026, 0.02, 0.026), (px, y + 0.02, pz), "tex:potato_skin", 12, 8, uv="sph", disp=(0.003, 40))
    for (sx, sz, a) in ((-0.12, -0.08, 0.4), (0.13, -0.07, 2.0), (0.0, 0.1, 1.2)):
        sprig(m, (sx, y + 0.012, sz), "f_herb", 4, 0.022, rng, a)
    for (lx, lz) in ((-0.15, 0.06), (0.15, -0.0)):
        blob(m, (0.027, 0.02, 0.022), (lx, y + 0.018, lz), "tex:lemon_peel", 14, 10, uv="sph")


@meal("sushi_nigiri_set")
def _(m, rng):
    m.box((0.3, 0.012, 0.13), (0, 0.016, 0), "f_wood_light", 0.003)
    for sx in (-0.11, 0.11):
        m.box((0.03, 0.016, 0.12), (sx, 0.008, 0), "f_wood_light", 0.002)
    toppings = ("f_salmon", "f_tuna", "f_shrimp", "f_butter", "f_salmon", "f_tuna")
    for k in range(6):
        x = -0.115 + k * 0.046
        z = -0.022 if k % 2 == 0 else 0.026
        z = 0.03 * (-1) ** k * 0.5
        blob(m, (0.0185, 0.0125, 0.0095), (x, 0.0345, z), "tex:rice", 14, 8, uv="sph", disp=(0.0012, 80), rot=(0, 0.1 * k, 0))
        t = toppings[k]
        slab(m, 0.044, 0.007, 0.021, (x, 0.0435, z), t, "box", 0.0025, rot=(0, 0.1 * k, 0), warp=lambda a, b, c: (a, b - 0.004 * (a / 0.022) ** 2, c))
        if k == 3:
            m.box((0.006, 0.014, 0.026), (x, 0.0415, z), "f_nori", 0.0005, rot=(0, 0.3, 0))
        if k == 2:
            for q in range(4):
                m.box((0.0035, 0.0024, 0.021), (x - 0.012 + 0.008 * q, 0.0512, z), "f_white", 0.0004, rot=(0, 0.1 * k, 0))
    blob(m, (0.012, 0.007, 0.009), (0.12, 0.028, 0.045), "f_wasabi", 10, 6, uv=None, disp=(0.0015, 60))
    for k in range(4):
        blob(m, (0.015, 0.0025, 0.009), (-0.12 + 0.012 * k, 0.027 + 0.003 * k, 0.045), "f_ginger", 10, 4, uv=None, rot=(0.2, 0.4 * k, 0.1))


@meal("maki_platter")
def _(m, rng):
    slab(m, 0.34, 0.012, 0.14, (0, 0, 0), "f_plate_dark", "box", 0.004)
    fills = ("f_tuna", "f_salmon", "f_cheese_yellow", "f_bean_green")
    for row in range(2):
        for k in range(4):
            x = -0.12 + k * 0.056
            z = -0.032 + row * 0.064
            cyl_y = 0.012
            lathe(m, [(0.0, 0.0), (0.021, 0.0), (0.021, 0.033), (0.0, 0.033)], (x, cyl_y, z), "f_nori", 20, disp=(0.0006, 60))
            lathe(m, [(0.0, 0.0), (0.0185, 0.0), (0.0185, 0.0006), (0.0, 0.0006)], (x, cyl_y + 0.0334, z), "tex:rice", 18, uv="top")
            blob(m, (0.0085, 0.0006, 0.0085), (x, cyl_y + 0.0338, z), fills[(k + row) % 4], 8, 4, uv=None)
            blob(m, (0.0035, 0.0007, 0.0035), (x + 0.007, cyl_y + 0.0338, z - 0.006), "f_wasabi", 6, 4, uv=None)
    vessel(m, [(0, 0), (0.025, 0), (0.035, 0.018)], 0.002, (0.0, 0.0, 0.105), "f_plate_blue", 20)
    lathe(m, [(0, 0), (0.03, 0), (0.03, 0.0008), (0, 0.0008)], (0.0, 0.0125, 0.105), "f_soy", 18)
    chopsticks(m, (0.12, 0.02, 0.1), 0.15, 0.21)


@meal("salad_bowl_wood")
def _(m, rng):
    R = 0.15
    vessel(m, bowl_outer(R, 0.09, 0.4, 8), 0.007, (0, 0, 0), "f_wood_dark", 32)
    lathe(m, [(0, 0), (R - 0.01, 0.0), (R - 0.02, 0.025), (R - 0.05, 0.05), (0.0, 0.065)], (0, 0.05, 0), "tex:salad_mix", 30, uv="top", disp=(0.006, 28))
    for k in range(18):
        a = k * 2.399
        rr = 0.105 * math.sqrt((k + 0.3) / 18)
        wavy_leaf(m, (rr * math.cos(a), 0.108 - 0.0003 * k - 0.015 * (rr / 0.11) ** 2, rr * math.sin(a)), 0.03 + 0.005 * (k % 3), "tex:leaf" if k % 2 else "tex:lettuce", 12, 0.008, 5, a, 0.002)
    for k in range(7):
        a = k * 2.1 + 0.3
        rr = 0.08 * math.sqrt((k + 0.5) / 7)
        blob(m, (0.0125, 0.0125, 0.0125), (rr * math.cos(a), 0.112 - 0.012 * (rr / 0.11) ** 2, rr * math.sin(a)), "tex:tomato_skin", 10, 8, uv="sph")
    for k in range(6):
        a = k * 1.5
        rr = 0.07 * (k + 1) / 7
        disc(m, 0.017, 0.004, (rr * math.cos(a), 0.118 - 0.012 * (rr / 0.11) ** 2, rr * math.sin(a)), "tex:cucumber", 12, uv="top", rot=(0.4, a, 0.3))
    for k in range(6):
        a = k * 2.6
        rr = 0.07 * (k + 0.5) / 7
        m.torus(0.011, 0.0022, (rr * math.cos(a), 0.114 - 0.012 * (rr / 0.11) ** 2, rr * math.sin(a)), "f_onion", seg=10, tseg=4, rot=(0.5, a, 0))
    for k in range(5):
        slab(m, 0.011, 0.01, 0.011, (0.04 * math.cos(k * 2.0), 0.112, 0.04 * math.sin(k * 2.0)), "f_chip", "box", 0.002, rot=(0, k, 0))
    for k in range(5):
        blob(m, (0.007, 0.004, 0.004), (0.06 * math.cos(k * 1.7), 0.113, 0.06 * math.sin(k * 1.7)), "f_olive_black", 8, 5, uv=None)


@meal("caesar_salad")
def _(m, rng):
    plate(m, 0.145, "f_plate_cream", rim="f_plate_sage")
    y = 0.008
    for k in range(5):
        a = -0.6 + k * 0.3
        pts = spline([(-0.08 + 0.0 * k, y + 0.003, -0.06 + 0.03 * k), (-0.02, y + 0.012 + 0.003 * k, -0.065 + 0.03 * k + 0.01), (0.06, y + 0.006, -0.05 + 0.03 * k)], 4)
        tube3(m, pts, [0.012 + 0.006 * math.sin(i / len(pts) * PI) for i in range(len(pts))], "tex:lettuce", 6, uv=True, caps=True, flat=0.35, tile=(1, 1))
    for k in range(8):
        a = k * 2.0
        slab(m, 0.016, 0.014, 0.016, (-0.04 + 0.025 * math.cos(a), y + 0.02, 0.0 + 0.04 * math.sin(a)), "f_chip", "box", 0.003, rot=(0.3 * k, a, 0.2))
    for k in range(5):
        slab(m, 0.02, 0.003, 0.036, (0.07 - 0.01 * k, y + 0.014 + 0.003 * k, 0.025 - 0.0 * k), "tex:ham", "box", 0.001, rot=(0, 0.2, -0.25))
    for k in range(7):
        a = k * 1.6
        blob(m, (0.018, 0.002, 0.006), (0.03 * math.cos(a), y + 0.036 + 0.0007 * k, 0.03 * math.sin(a)), "f_cheese_white", 8, 4, uv=None, rot=(0.2, a, 0.1))
    lathe(m, [(0, 0), (0.02, 0), (0.022, 0.0008), (0, 0.0012)], (0.0, y + 0.0, 0.1), "f_cream", 12)
    for k in range(4):
        tube3(m, [(-0.07 + 0.045 * k, y + 0.032, -0.03), (-0.06 + 0.045 * k, y + 0.036, 0.0), (-0.055 + 0.045 * k, y + 0.03, 0.03)], 0.0016, "f_cream", 5, caps=False)


@meal("curry_and_rice")
def _(m, rng):
    plate(m, 0.16, "f_plate_cream", well=0.01)
    y = 0.01
    blob(m, (0.05, 0.03, 0.05), (-0.05, y + 0.015, 0.0), "tex:rice", 20, 12, uv="sph", disp=(0.004, 30))
    vessel(m, bowl_outer(0.052, 0.04, 0.5, 6), 0.003, (0.05, y, -0.015), "f_steel", 22)
    lathe(m, [(0, 0), (0.049, 0), (0.049, 0.001), (0, 0.001)], (0.05, y + 0.0345, -0.015), "tex:curry", 22, uv="top")
    for k in range(6):
        a = k * 1.1
        slab(m, 0.014, 0.012, 0.014, (0.05 + 0.025 * math.cos(a), y + 0.0345, -0.015 + 0.025 * math.sin(a)), "f_chip" if k % 2 else "f_carrot_cut", "box", 0.003, rot=(0, a, 0.2))
    blob(m, (0.075, 0.006, 0.05), (-0.02, y + 0.004, 0.085), "tex:bread_crust", 22, 8, uv="box", disp=(0.0025, 30), rot=(0, 0.25, 0), warp=lambda x, yy, z: (x * (1 - 0.35 * (z / 0.05) + 0.0), yy, z))
    for k in range(6):
        sprig(m, (-0.05 + 0.012 * k, y + 0.0585 - 0.003 * k, 0.0 + 0.008 * (k % 3)), "f_herb", 2, 0.01, rng, k)


@meal("spaghetti_bolognese")
def _(m, rng):
    plate(m, 0.145, "f_plate", well=0.012)
    y = 0.012
    for k in range(26):
        a = rng.random() * TAU
        rr = 0.045 + 0.018 * (k % 3)
        h = y + 0.006 + 0.004 * (k // 7)
        pts = [(rr * math.cos(a + t * 0.55) * (1 - 0.06 * t), h + 0.004 * math.sin(t * 3.0 + k), rr * math.sin(a + t * 0.55) * (1 - 0.06 * t)) for t in (0, 1, 2, 3, 4, 5, 6)]
        tube3(m, pts, 0.0023, "tex:pasta", 5, uv=True, tile=(1, 6))
    blob(m, (0.06, 0.012, 0.06), (0.0, y + 0.02, 0.0), "tex:pasta", 20, 8, uv="sph", disp=(0.004, 50), tile=(2, 2))
    blob(m, (0.042, 0.015, 0.042), (0.0, y + 0.03, 0.0), "tex:bolognese", 18, 8, uv="sph", disp=(0.004, 55))
    for k in range(10):
        a = k * 2.4
        blob(m, (0.006, 0.004, 0.006), (0.024 * math.cos(a), y + 0.042 - 0.002 * (k % 3), 0.024 * math.sin(a)), "tex:bolognese", 6, 4, uv="sph")
    for k in range(9):
        a = k * 1.9
        blob(m, (0.004, 0.0015, 0.0025), (0.03 * math.cos(a), y + 0.037 - 0.003 * (k % 2), 0.03 * math.sin(a)), "f_cheese_white", 5, 3, uv=None, rot=(0, a, 0))
    sprig(m, (0.0, y + 0.047, 0.0), "f_herb", 3, 0.013, rng)


@meal("mac_and_cheese")
def _(m, rng):
    vessel(m, [(0.0, 0.0), (0.07, 0.0), (0.082, 0.012), (0.095, 0.055)], 0.004, (0, 0, 0), "f_plate_red", 30)
    lathe(m, [(0, 0), (0.088, 0), (0.088, 0.001), (0, 0.001)], (0, 0.047, 0), "tex:cheese_sauce", 30, uv="top", disp=(0.0025, 40))
    for k in range(70):
        a = k * 2.399
        rr = 0.085 * math.sqrt((k + 0.5) / 70)
        yy = 0.0468 + 0.0
        pts = [(rr * math.cos(a) + 0.006 * math.cos(a + 1.0 + t * 1.2), yy + 0.0035 * t * 0 + 0.0023, rr * math.sin(a) + 0.006 * math.sin(a + 1.0 + t * 1.2)) for t in (-1, 0, 1)]
    for k in range(55):
        a = k * 2.399
        rr = 0.083 * math.sqrt((k + 0.5) / 55)
        pa = rng.random() * TAU
        c = (rr * math.cos(a), 0.0505, rr * math.sin(a))
        pts = [(c[0] + 0.008 * math.cos(pa + t * 0.9), c[1] + 0.002 * t * 0, c[2] + 0.008 * math.sin(pa + t * 0.9)) for t in (-1, 0, 1, 2)]
        tube3(m, pts, 0.0035, "f_cheese_yellow" if k % 3 else "f_caramel", 5, caps=True)
    for k in range(6):
        a = k * 1.1
        sprig(m, (0.03 * math.cos(a), 0.056, 0.03 * math.sin(a)), "f_herb", 2, 0.01, rng, a)


@meal("tacos_trio")
def _(m, rng):
    m.box((0.31, 0.012, 0.13), (0, 0.006, 0), "f_wood_dark", 0.003)
    for k in range(3):
        x = -0.095 + k * 0.095
        # taco shell: half-pipe (arc of a cylinder along Z) with filling heaped inside
        lathe(m, [(0.034, -0.055), (0.0362, -0.055), (0.0362, 0.055), (0.034, 0.055)], (x, 0.0095, 0.0), "f_tortilla", 14, rot=(PI / 2, 0, 0),
              arc=PI * 1.1, a0=-PI * 0.05, scale=(1.0, 1.0, 1.15))
        blob(m, (0.026, 0.012, 0.05), (x, 0.03, 0.0), "f_herb", 10, 6, uv=None, disp=(0.004, 60)) if k != 1 else \
            blob(m, (0.026, 0.014, 0.05), (x, 0.032, 0.0), "tex:bolognese", 10, 6, uv="sph", disp=(0.003, 60))
        blob(m, (0.012, 0.008, 0.022), (x, 0.045, 0.0), "tex:tomato_skin", 8, 6, uv="sph", disp=(0.003, 60))
        blob(m, (0.012, 0.006, 0.03), (x, 0.044, 0.0), "f_cheese_yellow", 8, 5, uv=None, disp=(0.003, 60), rot=(0, 0, 0.2))
    lemon_wedge(m, (0.14, 0.012, 0.04), 0.3, 1.2)


@meal("dumplings_steamer")
def _(m, rng):
    R = 0.115
    lathe(m, [(0.0, 0.0), (R, 0.0), (R, 0.018), (R - 0.004, 0.018), (R - 0.004, 0.003), (0.0, 0.003)], (0, 0, 0), "tex:bamboo", 36, uv="cyl", tile=(3, 1))
    lathe(m, [(R - 0.004, 0.0), (R + 0.003, 0.0), (R + 0.003, 0.028), (R - 0.003, 0.028)], (0, 0.018, 0), "tex:bamboo", 36, uv="cyl", tile=(3, 1))
    for k in range(6):
        a = k * TAU / 6 + 0.2
        x, z = 0.058 * math.cos(a), 0.058 * math.sin(a)
        if k == 5:
            x, z = 0, 0
        dome(m, 0.032, 0.026, (x, 0.0185, z), "f_dough", 18, 6, uv=None, warp=lambda xx, yy, zz: (xx * (1.1 - 0.5 * yy / 0.026), yy, zz * (1.0 - 0.45 * yy / 0.026)), rot=(0, a, 0))
    for k in range(5):
        a = k * TAU / 6 + 0.2
        x, z = 0.058 * math.cos(a), 0.058 * math.sin(a)
        pts = spline([(x - 0.026 * math.sin(a), 0.0405, z + 0.026 * math.cos(a)), (x, 0.0455, z), (x + 0.026 * math.sin(a), 0.0405, z - 0.026 * math.cos(a))], 3)
        tube3(m, pts, 0.0026, "f_dough", 6, caps=True, flat=0.8)
    vessel(m, [(0, 0), (0.025, 0), (0.035, 0.018)], 0.002, (0.0, 0.0, 0.155), "f_plate_blue", 20)
    lathe(m, [(0, 0), (0.026, 0), (0.026, 0.0008), (0, 0.0008)], (0.0, 0.0105, 0.155), "f_soy", 18)
    chopsticks(m, (0.07, 0.048, 0.0), 0.0, 0.22, 0.0)


@meal("fried_egg_breakfast")
def _(m, rng):
    plate(m, 0.15, "f_plate")
    y = 0.008
    for (ex, ez, ph) in ((-0.045, -0.02, 0.3), (0.0, 0.04, 1.7)):
        lathe(m, [(0, 0), (0.044, 0), (0.05, 0.001), (0.047, 0.0035), (0.0, 0.004)], (ex, y, ez), "tex:egg_white", 28, uv="top", warp=wobble(5, ph, 0.12), disp=(0.0012, 40))
        dome(m, 0.0165, 0.0125, (ex + 0.003, y + 0.0035, ez - 0.002), "f_yolk", 16, 6, uv=None)
    for k in range(2):
        slab(m, 0.1, 0.0035, 0.024, (0.045, y + 0.006 * k, -0.05 + 0.03 * k + 0.0 * k), "tex:bacon", "box", 0.001, rot=(0, 0.2 - 0.3 * k, 0),
             warp=lambda x, yy, z: (x, yy + 0.003 * math.sin(x * 130), z))
    for k in range(2):
        pts = spline([(-0.07, y + 0.01, 0.06 + 0.02 * k), (-0.02, y + 0.012, 0.062 + 0.02 * k), (0.03, y + 0.01, 0.058 + 0.02 * k)], 4)
        tube3(m, pts, 0.0095, "tex:sausage", 8, uv=True, tile=(1, 4)) if k == 0 else None
    slab(m, 0.07, 0.012, 0.07, (-0.065, y, -0.055), "tex:bread_crust", "box", 0.004, rot=(0, 0.3, 0), warp=lambda x, yy, z: (x, yy + 0.0 * x, z))
    disc(m, 0.02, 0.012, (0.085, y, 0.055), "tex:tomato_skin", 14, uv=None, edge=0.8)
    blob(m, (0.018, 0.006, 0.018), (0.085, y + 0.0135, 0.055), "f_gelatin", 10, 6, uv=None)


@meal("porridge_bowl")
def _(m, rng):
    R = 0.085
    vessel(m, bowl_outer(R, 0.06, 0.4, 8), 0.0035, (0, 0, 0), "f_plate_sage", 28)
    lathe(m, [(0, 0), (R - 0.006, 0.0), (R - 0.018, 0.0), (R - 0.03, 0.006), (0.0, 0.012)], (0, 0.048, 0), "tex:porridge", 28, uv="top", disp=(0.003, 60))
    for k in range(7):
        a = k * 0.8
        disc(m, 0.016, 0.0045, (0.025 * math.cos(a * 1.3), 0.06 + 0.004 * (k % 2), -0.02 + 0.013 * k * 0.5 + 0.0), "f_butter", 12, uv=None, edge=0.9, rot=(0.25, a, 0.15))
    for k in range(9):
        a = k * 2.0
        blob(m, (0.008, 0.008, 0.008), (0.04 * math.cos(a) * 0.9, 0.062, 0.04 * math.sin(a) * 0.9 + 0.01), "tex:blueberry", 8, 6, uv="sph") if k % 2 else strawberry_slice(m, (0.04 * math.cos(a), 0.0605, 0.04 * math.sin(a)))
    lathe(m, [(0, 0), (0.03, 0), (0.034, 0.001), (0.028, 0.002), (0, 0.003)], (0.0, 0.0605, 0.0), "f_honey", 20, warp=wobble(5, 0.3, 0.25))
    m.link((0.105, 0.078, -0.015), (0.045, 0.071, -0.005), 0.0016, "f_steel", 5)


def strawberry_slice(m, pos):
    disc(m, 0.01, 0.003, pos, "f_tomato", 10, uv=None, edge=0.5)
    disc(m, 0.007, 0.0032, (pos[0], pos[1] + 0.0002, pos[2]), "f_icing_pink", 10, uv=None, edge=0.5)


@meal("tomato_soup_bowl")
def _(m, rng):
    plate(m, 0.105, "f_plate", well=0.006, seg=30)
    R = 0.075
    vessel(m, bowl_outer(R, 0.055, 0.45, 8), 0.0035, (0, 0.006, 0), "f_plate", 30)
    lathe(m, [(0, 0), (R - 0.006, 0), (R - 0.006, 0.001), (0, 0.001)], (0, 0.052, 0), "tex:soup_tomato", 28, uv="top")
    tube3(m, spline([(-0.03, 0.0555, 0.0), (-0.015, 0.0558, 0.015), (0.01, 0.0555, 0.01), (0.02, 0.0558, -0.01), (0.0, 0.0555, -0.02)], 4), 0.0045, "f_cream", 6)
    for k in range(5):
        slab(m, 0.014, 0.012, 0.014, (0.03 * math.cos(k * 1.9), 0.0565, 0.03 * math.sin(k * 1.9) - 0.005), "f_chip", "box", 0.003, rot=(0.2, k, 0.1))
    sprig(m, (0.0, 0.0575, 0.0), "f_herb", 3, 0.014, rng)
    m.link((0.1, 0.012, 0.0), (0.04, 0.056, -0.012), 0.0016, "f_steel", 5)


@meal("fish_and_chips")
def _(m, rng):
    plate(m, 0.16, "f_plate_blue", rim="f_white")
    y = 0.008
    for k, (fx, fz, ang) in enumerate(((-0.03, -0.035, 0.3), (-0.01, 0.015, -0.2))):
        blob(m, (0.085, 0.02, 0.032), (fx, y + 0.02 + 0.016 * k, fz), "tex:batter", 22, 10, uv="sph", disp=(0.003, 38), rot=(0, ang, 0), warp=lambda x, yy, z: (x, yy, z * (1 - 0.25 * (x / 0.085))))
    for k in range(20):
        a = k * 0.55
        ln = 0.07 + 0.01 * ((k * 7) % 3)
        m.box((0.012, 0.012, ln), (0.045 + 0.011 * (k % 6), y + 0.006 + 0.011 * (k // 8), 0.0 - 0.0 + 0.01 * ((k * 3) % 3) - 0.02), "f_fry", 0.0015, rot=(0.03 * (k % 3), 0.2 * math.sin(k), 0.1 * math.cos(k * 2)))
    vessel(m, [(0, 0), (0.025, 0), (0.032, 0.025)], 0.002, (-0.08, y, 0.075), "f_plate", 18)
    lathe(m, [(0, 0), (0.026, 0), (0.026, 0.001), (0, 0.001)], (-0.08, y + 0.019, 0.075), "f_pea", 18, uv=None, disp=(0.0018, 60))
    lemon_wedge(m, (-0.01, y, 0.08), 0.5, 1.3)
    blob(m, (0.012, 0.004, 0.012), (0.08, y + 0.002, 0.075), "f_cream", 8, 4, uv=None, disp=(0.001, 60))


@meal("burrito_plate")
def _(m, rng):
    plate(m, 0.15, "f_plate_dark")
    y = 0.008
    pts = spline([(-0.065, y + 0.03, 0.0), (0.0, y + 0.032, 0.0), (0.065, y + 0.03, 0.0)], 4)
    tube3(m, pts, 0.03, "f_tortilla", 14, uv=None, caps=False, disp=(0.0015, 50))
    lathe(m, [(0.0, 0.0), (0.0295, 0.0), (0.0295, 0.0008), (0.0, 0.0008)], (0.0695, y + 0.03, 0.0), "tex:rice_fried", 20, rot=(0, 0, PI / 2), uv="top")
    blob(m, (0.004, 0.012, 0.012), (0.0705, y + 0.0385, -0.006), "tex:beans", 8, 6, uv="sph")
    blob(m, (0.004, 0.009, 0.01), (0.0705, y + 0.024, 0.008), "f_cheese_yellow", 8, 6, uv=None)
    blob(m, (0.004, 0.007, 0.007), (0.0705, y + 0.03, -0.012), "f_tomato", 8, 6, uv=None)
    m.cyl(0.032, 0.062, (-0.04, y + 0.03, 0.0), "f_foil", axis="x", seg=18)
    vessel(m, [(0, 0), (0.03, 0), (0.04, 0.03)], 0.0025, (-0.055, y, 0.085), "f_plate_red", 20)
    lathe(m, [(0, 0), (0.034, 0), (0.0345, 0.001), (0, 0.001)], (-0.055, y + 0.022, 0.085), "f_tomato", 20, disp=(0.002, 60))
    vessel(m, [(0, 0), (0.026, 0), (0.034, 0.026)], 0.0025, (0.04, y, 0.09), "f_plate_sage", 20)
    blob(m, (0.026, 0.012, 0.026), (0.04, y + 0.022, 0.09), "f_wasabi", 12, 8, uv=None, disp=(0.003, 60))
    for k in range(6):
        m.prism([(0.0, 0.0), (0.03, 0.0), (0.015, 0.026)], 0.003, (0.065 + 0.0 * k, y + 0.0 + 0.003 * k, -0.07 + 0.012 * k), "f_chip", "xz", rot=(0, 0.6 * k, 0))


@meal("lasagna_slice")
def _(m, rng):
    plate(m, 0.14, "f_plate_cream")
    y = 0.008
    layers = (("f_dough", 0.006), ("tex:bolognese", 0.011), ("f_cream", 0.006), ("f_dough", 0.006), ("tex:bolognese", 0.011), ("f_cream", 0.006), ("f_dough", 0.005))
    for mat, h in layers:
        if mat.startswith("tex"):
            slab(m, 0.1, h, 0.075, (0, y, 0), mat, "box", 0.0015, rot=(0, 0.12, 0), disp=(0.0014, 80))
        else:
            slab(m, 0.102, h, 0.077, (0, y, 0), mat, "box", 0.0012, rot=(0, 0.12, 0), disp=(0.001, 80))
        y += h
    slab(m, 0.104, 0.006, 0.079, (0, y, 0), "tex:cheese_sauce", "box", 0.002, rot=(0, 0.12, 0), disp=(0.0015, 60))
    y += 0.006
    for k in range(4):
        sprig(m, (-0.03 + 0.02 * k, y + 0.001, 0.0 + 0.01 * (k % 2)), "f_herb", 2, 0.012, rng, k)
    blob(m, (0.05, 0.004, 0.02), (-0.0, y + 0.0, 0.0), "tex:cheese_sauce", 14, 6, uv="sph", rot=(0, 0.12, 0), disp=(0.002, 70))


@meal("fried_rice_bowl")
def _(m, rng):
    R = 0.088
    vessel(m, bowl_outer(R, 0.065, 0.4, 8), 0.0035, (0, 0, 0), "f_plate_red", 28)
    blob(m, (0.078, 0.052, 0.078), (0.0, 0.05, 0.0), "tex:rice_fried", 28, 12, uv="sph", disp=(0.004, 36), tile=(2, 1))
    for k in range(10):
        a = k * 2.399
        rr = 0.055 * math.sqrt((k + 0.5) / 10)
        slab(m, 0.008, 0.007, 0.008, (rr * math.cos(a), 0.092 - 0.02 * (rr / 0.08) ** 2, rr * math.sin(a)), "f_carrot_cut" if k % 3 == 0 else "f_pea", "box", 0.002, rot=(0.3, a, 0.2))
    for k in range(5):
        a = k * 1.7 + 0.5
        blob(m, (0.012, 0.005, 0.008), (0.03 * math.cos(a), 0.095, 0.03 * math.sin(a)), "f_butter", 8, 5, uv=None, rot=(0, a, 0))
    for k in range(3):
        a = k * 2.2
        tube3(m, spline([(0.035 * math.cos(a), 0.088, 0.035 * math.sin(a)), (0.045 * math.cos(a), 0.093, 0.045 * math.sin(a)), (0.052 * math.cos(a + 0.3), 0.087, 0.052 * math.sin(a + 0.3))], 3),
              [0.008, 0.007, 0.005, 0.004, 0.003, 0.002][:0] or 0.0065, "f_shrimp", 7)
    for k in range(7):
        a = k * 0.9
        m.torus(0.0035, 0.0012, (0.0 + 0.02 * math.cos(a), 0.099 - 0.006 * (k % 2), 0.02 * math.sin(a)), "f_scallion", seg=8, tseg=4)
    chopsticks(m, (0.015, 0.1, 0.0), 0.5, 0.23, 0.0)


@meal("omelette_plate")
def _(m, rng):
    plate(m, 0.15, "f_plate_sage")
    y = 0.008
    blob(m, (0.1, 0.022, 0.05), (-0.01, y + 0.014, -0.01), "f_butter", 26, 12, uv=None, disp=(0.002, 40), rot=(0, 0.15, 0),
         warp=lambda x, yy, z: (x, yy, z * (1 - 0.5 * (x / 0.1) ** 2) * 1.0))
    for k in range(9):
        a = k * 1.1
        sprig(m, (-0.07 + 0.017 * k, y + 0.034 - 0.003 * abs(k - 4) * 0.4, -0.004 - 0.003 * k * 0.5), "f_herb", 2, 0.011, rng, a)
    for k in range(3):
        blob(m, (0.012, 0.011, 0.012), (0.03 + 0.016 * k, y + 0.011, 0.075 + 0.0), "tex:tomato_skin", 10, 8, uv="sph")
    for k in range(4):
        wavy_leaf(m, (-0.06 + 0.02 * k, y + 0.0, 0.07 - 0.0), 0.017, "tex:spinach", 10, 0.003, 4, k, 0.0015)


@meal("pho_bowl")
def _(m, rng):
    R = 0.115
    vessel(m, bowl_outer(R, 0.085, 0.36, 8), 0.0045, (0, 0, 0), "f_white", 34)
    lathe(m, [(0, 0), (R - 0.006, 0), (R - 0.006, 0.001), (0, 0.001)], (0, 0.072, 0), "f_olive_oil", 30)
    lathe(m, [(0, 0), (R - 0.01, 0), (R - 0.01, 0.0006), (0, 0.0006)], (0, 0.0725, 0), "tex:broth", 30, uv="top")
    noodles(m, rng, 0.0, 0.0, 0.0725, 0.095, 18, "f_dough", 0.0022, 0.014, 1.8)
    for k in range(6):
        slab(m, 0.05, 0.003, 0.03, (-0.02 + 0.015 * (k % 3), 0.0745 + 0.003 * (k // 3), -0.04 + 0.03 * (k // 3) + 0.01 * (k % 2)), "tex:steak", "box", 0.001, rot=(0, 0.5 * k, 0.05))
    for k in range(7):
        a = k * 2.6
        m.torus(0.0035, 0.0012, (0.02 * math.cos(a) + 0.03, 0.0775, 0.02 * math.sin(a) + 0.04), "f_scallion", seg=8, tseg=4)
    for k in range(5):
        tube3(m, [(-0.05 + 0.01 * k, 0.076, 0.045), (-0.045 + 0.01 * k, 0.082, 0.05), (-0.04 + 0.01 * k, 0.078, 0.055)], 0.0012, "f_cream", 4)
    lemon_wedge(m, (0.085, 0.07, 0.035), 0.4, 1.0)
    chopsticks(m, (0.02, 0.11, -0.06), 0.1, 0.24, 0.0)


@meal("beef_stew_pot")
def _(m, rng):
    R = 0.115
    vessel(m, [(0.0, 0.0), (R * 0.9, 0.0), (R, 0.012), (R, 0.1)], 0.005, (0, 0, 0), "f_steel_dark", 32)
    lathe(m, [(0, 0), (R - 0.012, 0), (R - 0.012, 0.001), (0, 0.001)], (0, 0.078, 0), "tex:bolognese", 30, uv="top", disp=(0.002, 50))
    for k in range(10):
        a = k * 2.399
        rr = 0.085 * math.sqrt((k + 0.5) / 10)
        blob(m, (0.014, 0.011, 0.014), (rr * math.cos(a), 0.084, rr * math.sin(a)), ("tex:potato_skin", "tex:carrot", "tex:steak")[k % 3], 10, 8, uv="sph", disp=(0.002, 70))
    for k in range(4):
        a = k * 1.6 + 0.8
        sprig(m, (0.04 * math.cos(a), 0.088, 0.04 * math.sin(a)), "f_herb", 3, 0.012, rng, a)
    m.torus(0.117, 0.004, (0, 0.1, 0), "f_steel_dark", seg=36, tseg=6)
    for sgn in (-1, 1):
        m.box((0.03, 0.012, 0.03), (sgn * (R + 0.015), 0.085, 0), "black_metal", 0.003)
    arcp = [(-R - 0.01 * math.cos(t), 0.096 + 0.05 * math.sin(t), 0.0) for t in (0, 0.5, 1.0, 1.57)] + [(0.0, 0.147, 0.0)] + [(R + 0.01 * math.cos(t), 0.096 + 0.05 * math.sin(t), 0.0) for t in (1.57, 1.0, 0.5, 0.0)]
    tube3(m, spline(arcp, 4), 0.0028, "black_metal", 6, caps=True)
    # ladle resting


@meal("paella_pan")
def _(m, rng):
    R = 0.18
    vessel(m, [(0.0, 0.0), (R * 0.92, 0.0), (R, 0.012), (R, 0.035)], 0.003, (0, 0, 0), "f_steel_dark", 40)
    lathe(m, [(0, 0), (R - 0.005, 0), (R - 0.005, 0.001), (0, 0.001)], (0, 0.026, 0), "tex:rice_fried", 36, uv="top", disp=(0.002, 50))
    for k in range(7):
        a = k * TAU / 7 + 0.2
        for q, (rr, mt) in enumerate(((0.12, "f_shrimp"),)):
            tube3(m, spline([(rr * math.cos(a) - 0.02 * math.sin(a), 0.032, rr * math.sin(a) + 0.02 * math.cos(a)), (rr * math.cos(a), 0.044, rr * math.sin(a)), (rr * math.cos(a) + 0.02 * math.sin(a), 0.034, rr * math.sin(a) - 0.02 * math.cos(a))], 3),
                  0.009, mt, 8, caps=True)
    for k in range(8):
        a = k * TAU / 8 + 0.6
        rr = 0.06
        blob(m, (0.022, 0.009, 0.014), (rr * math.cos(a), 0.034, rr * math.sin(a)), "f_glass_dark", 10, 6, uv=None, rot=(0, -a, 0.25))
    for k in range(18):
        a = k * 2.399
        rr = 0.14 * math.sqrt((k + 0.5) / 18)
        blob(m, (0.004, 0.004, 0.004), (rr * math.cos(a), 0.0285, rr * math.sin(a)), "f_pea", 6, 4, uv=None)
    for k in range(6):
        a = k * 1.1
        m.box((0.03, 0.003, 0.007), (0.1 * math.cos(a), 0.029, 0.1 * math.sin(a)), "f_tomato", 0.001, rot=(0, -a, 0))
    for sgn in (-1, 1):
        m.link((sgn * R, 0.03, 0.0), (sgn * (R + 0.05), 0.04, 0.0), 0.007, "black_metal", 6)
    lemon_wedge(m, (0.0, 0.03, 0.0), 0.0, 1.0)


@meal("shepherds_pie_dish")
def _(m, rng):
    vessel(m, [(0.0, 0.0), (0.07, 0.0), (0.09, 0.012), (0.1, 0.05)], 0.004, (0, 0, 0), "f_plate_sage", 30, scale=(1.0, 1.0, 0.75))
    lathe(m, [(0, 0), (0.093, 0.0), (0.095, 0.01), (0.08, 0.018), (0.0, 0.024)], (0, 0.036, 0), "f_cream", 30, scale=(1.0, 1.0, 0.76), disp=(0.0025, 60))
    for r in range(5):
        z = (r - 2) * 0.026
        half = 0.088 * math.sqrt(max(0.0, 1 - (z / 0.073) ** 2))
        tube3(m, [(-half * 0.85, 0.058, z), (0.0, 0.0625, z), (half * 0.85, 0.058, z)], 0.0036, "f_butter", 6, caps=True, disp=(0.0006, 90))
    for k in range(4):
        sprig(m, (-0.03 + 0.02 * k, 0.065, 0.0), "f_herb", 2, 0.011, rng, k)


menu.register()
