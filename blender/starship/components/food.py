"""Realistic food models, part 1: bakery and desserts (see also food_meals / food_produce / food_drinks / food_rations).

Everything is organic bmesh geometry (surfaces of revolution, noise displacement, tubes along curves; foodkit.py)
with procedural albedo maps from textures_food.py (`tex:<name>` materials).  Real-world scale; table mount origin =
bottom-centre of the item.
"""
import math

from .foodkit import PI, TAU, Menu, blob, disc, dome, lathe, seeds, slab, spline, sprig, torus_prof, tube3, vessel

menu = Menu()


# ---------------------------------------------------------------- shared props
def plate(m, r=0.13, mat="f_plate", pos=(0, 0, 0), well=0.008, seg=32, rim=None):
    """Dinner plate (default 0.26 m).  Returns the y of the food surface."""
    x, y, z = pos
    prof = [(0.0, 0.0), (r * 0.58, 0.0), (r * 0.64, 0.003), (r * 0.9, 0.012), (r, 0.017), (r, 0.0195),
            (r * 0.93, 0.0195), (r * 0.7, well + 0.004), (r * 0.62, well), (0.0, well)]
    lathe(m, prof, (x, y, z), mat, seg)
    if rim:
        lathe(m, [(r * 0.915, 0.0194), (r * 0.985, 0.0194), (r * 0.985, 0.0201), (r * 0.915, 0.0201)], (x, y, z), rim, seg)
    return y + well


def wobble(k, ph=0.0, amp=0.15):
    """Warp factory: lobed outline  r *= 1 + amp * sin(k a + ph)."""
    def w(x, y, z):
        a = math.atan2(z, x)
        f = 1 + amp * math.sin(k * a + ph)
        return x * f, y, z * f
    return w


def wavy_leaf(m, pos, r, mat="tex:lettuce", seg=26, amp=0.006, waves=7, ph=0.0, th=0.002):
    """Frilly leaf disc (lettuce, spinach, basil ...)."""
    def warp(x, y, z):
        a = math.atan2(z, x)
        k = math.hypot(x, z) / max(r, 1e-6)
        f = 1 + 0.06 * math.sin(a * 11 + ph)
        return x * f, y + amp * math.sin(a * waves + ph) * k ** 2 + 0.002 * k * k, z * f
    lathe(m, [(0.0, 0.0), (r, 0.0), (r, th), (0.0, th)], pos, mat, seg, uv="top", warp=warp)


def paper_cup(m, r0, r1, h, pos=(0, 0, 0), mat="f_cream", ridges=18):
    """Fluted baking case (r0 base radius, r1 top radius)."""
    prof = [(0.0, 0.0), (r0, 0.0), (r1, h), (r1 - 0.0015, h), (r0 - 0.0015, 0.001), (0.0, 0.001)]
    lathe(m, prof, pos, mat, ridges * 2, warp=wobble(ridges, 0.0, 0.05))


def frosting_swirl(m, r, h, pos, mat, tiers=3, turns=2.2):
    """Piped frosting swirl: stacked lobed discs spiralling up to a point."""
    prof = [(0.0, 0.0)]
    for k in range(0, 25):
        t = k / 24
        prof.append(((r * (1 - t) ** 0.9 * (1 + 0.16 * math.sin(t * PI * 2 * tiers))) + 0.0005, h * t))
    prof[-1] = (0.0, h)
    prof[1] = (prof[1][0], 0.0)

    def tw(x, y, z):
        a = math.atan2(z, x) + y / h * TAU * turns * 0.25
        rr = math.hypot(x, z) * (1 + 0.12 * math.cos(6 * a))
        return rr * math.cos(a - y / h * TAU * turns * 0.25), y, rr * math.sin(a - y / h * TAU * turns * 0.25)
    lathe(m, prof, pos, mat, 28, warp=tw, uv=None)


def strawberry_bit(m, pos, r=0.014):
    blob(m, (r, r * 1.2, r), pos, "tex:strawberry", 8, 6, uv="sph", disp=None)
    tube3(m, [(pos[0], pos[1] + r * 1.0, pos[2]), (pos[0], pos[1] + r * 1.4, pos[2])], 0.0016, "f_stem", 5, caps=False)


def wedge(m, r, h, deg, pos, mat, rot_y=0.0, n=8):
    """Pie / cake wedge prism with apex at pos (xz plane), base at pos.y, sector angle deg."""
    a0 = -math.radians(deg) / 2
    pts = [(0.0, 0.0)] + [(r * math.cos(a0 + math.radians(deg) * i / n), r * math.sin(a0 + math.radians(deg) * i / n)) for i in range(n + 1)]
    m.prism(pts, h, pos, mat, "xz", rot=(0, rot_y, 0))


# ================================================================ BAKERY
bakery = menu.cat("bakery", tags=("food", "bakery"))


@bakery("croissant")
def _(m, rng):
    L, Rc = 0.2, 0.085
    n = 36
    prof = [(0.0, -L / 2)]
    for k in range(1, n):
        t = k / n
        prof.append((0.034 * math.sin(PI * t) ** 0.7 * (1 + 0.15 * math.cos(TAU * 6 * t + 0.5)), -L / 2 + L * t))
    prof.append((0.0, L / 2))

    def bend(x, y, z):
        ph = y / Rc
        return Rc * math.sin(ph) + x * math.cos(ph), z, Rc * (1 - math.cos(ph)) + x * math.sin(ph)
    lathe(m, prof, (0, 0.024, 0), "tex:croissant", 18, scale=(1.0, 1.0, 0.8), uv="cyl", warp=bend, disp=(0.002, 30), tile=(2, 1))


@bakery("baguette")
def _(m, rng):
    L = 0.52
    prof = [(0.0, -L / 2)] + [(0.034 * math.sin(PI * (k / 22)) ** 0.25, -L / 2 + L * k / 22) for k in range(1, 22)] + [(0.0, L / 2)]
    lathe(m, prof, (0, 0.028, 0), "tex:bread_crust", 16, rot=(0, 0, PI / 2), scale=(1, 1, 0.82), uv="cyl", disp=(0.0016, 45), tile=(1, 2))
    for k in range(5):
        x = -0.17 + k * 0.085
        blob(m, (0.03, 0.0035, 0.0055), (x, 0.0535, 0.0), "tex:bread_crumb", 8, 4, uv="sph", rot=(0, 0.55, 0))


@bakery("sourdough_boule")
def _(m, rng):
    blob(m, (0.115, 0.075, 0.115), (0, 0.06, 0), "tex:bread_crust", 30, 14, disp=(0.003, 18), uv="sph", tile=(2, 1))
    for k in range(3):
        blob(m, (0.075, 0.0026, 0.006), (0, 0.133 - 0.0, 0), "tex:bread_crumb", 10, 4, uv="sph", rot=(0, k * PI / 3 + 0.3, 0),
             warp=lambda x, y, z: (x, y - 0.045 * (x / 0.075) ** 2, z))
    seeds(m, rng, 60, (0, 0, 0.08, 0.08), 0.0, "f_white", (0.004, 0.0012, 0.004),
          ground=lambda x, z: 0.06 + 0.075 * math.sqrt(max(0.0, 1 - (x * x + z * z) / 0.115 ** 2)) + 0.001)
    m.cyl(0.13, 0.006, (0, 0.003 - 0.02 + 0.0, 0), "f_wood_light", seg=28)


@bakery("bread_loaf")
def _(m, rng):
    L = 0.3
    prof = [(0.0, -L / 2), (0.05, -L / 2 + 0.004), (0.058, -L / 2 + 0.03), (0.06, -L / 2 + 0.07)] + [(0.062, y) for y in (-0.06, 0.0, 0.06)] + \
           [(0.06, L / 2 - 0.07), (0.058, L / 2 - 0.03), (0.05, L / 2 - 0.004), (0.0, L / 2)]

    def top(x, y, z):
        return x, y, z * (1.0 if z < 0 else 1.0 + 0.16 * (1 - (y / 0.15) ** 2))
    lathe(m, prof, (0, 0.047, 0), "tex:bread_crust", 18, rot=(0, 0, PI / 2), scale=(1, 1, 0.78), uv="cyl", disp=(0.0018, 25), warp=top, tile=(1, 2))
    for k in range(4):
        blob(m, (0.04, 0.004, 0.006), (-0.1 + k * 0.067, 0.1 - 0.005, 0.0), "tex:bread_crumb", 8, 4, uv="sph", rot=(0, 0.6, 0))


@bakery("bagel_poppy")
def _(m, rng):
    prof = torus_prof(0.034, 0.0175, 0.0175, 12)
    lathe(m, prof, (0, 0, 0), "tex:bread_crust", 28, uv="cyl", closed=True, disp=(0.0012, 50), tile=(2, 1))
    seeds(m, rng, 70, (0, 0, 0.034, 0.034), 0, "f_olive_black", (0.0014, 0.0009, 0.0014),
          ground=lambda x, z: 0.0175 + 0.0175 * math.sqrt(max(0.0, 1 - ((math.hypot(x, z) - 0.034) / 0.0175) ** 2)) * 0.97 + 0.0003)


@bakery("pancake_stack")
def _(m, rng):
    plate(m, 0.13)
    y = 0.009
    for k in range(5):
        disc(m, 0.095 - 0.002 * (k % 2), 0.014, (0.004 * math.sin(k * 2.3), y, 0.004 * math.cos(k * 1.7)), "tex:pancake", 32, uv="top", disp=(0.0012, 26), edge=0.7)
        y += 0.0122
    m.box((0.034, 0.014, 0.034), (0.0, y + 0.0055, 0.0), "f_butter", bevel=0.003, rot=(0, 0.5, 0))
    # syrup puddle on the top pancake and drips down the side
    lathe(m, [(0, 0.0), (0.07, 0.0), (0.076, 0.0006), (0.07, 0.0015), (0.0, 0.003)], (0, y + 0.0005, 0), "tex:syrup", 28, uv="top",
          warp=wobble(5, 0.4, 0.14))
    for k in range(5):
        a = k * 1.25 + 0.2
        c, s = math.cos(a), math.sin(a)
        tube3(m, [(0.074 * c, y + 0.002, 0.074 * s), (0.087 * c, y - 0.002, 0.087 * s), (0.092 * c, y - 0.02 - 0.006 * k % 3, 0.092 * s)], 0.0035, "tex:syrup", 6)
    strawberry_bit(m, (0.05, y + 0.012, -0.05))
    strawberry_bit(m, (-0.045, y + 0.012, -0.05))


@bakery("waffle_berries")
def _(m, rng):
    plate(m, 0.14, "f_plate_cream")
    y = 0.009
    slab(m, 0.15, 0.012, 0.15, (0, y, 0), "tex:waffle", "box", 0.004)
    for k in range(7):
        c = -0.0625 + k * 0.0208
    for k in range(6):
        c = -0.052 + k * 0.0208
        slab(m, 0.15, 0.004, 0.0055, (0, y + 0.0115, c), "tex:waffle", "box", 0.001)
        slab(m, 0.0055, 0.004, 0.15, (c, y + 0.0115, 0), "tex:waffle", "box", 0.001)
    m.box((0.035, 0.012, 0.035), (0.0, y + 0.02, 0.0), "f_butter", bevel=0.003, rot=(0, 0.3, 0))
    for (x, z) in ((-0.045, 0.04), (0.05, -0.035), (0.035, 0.05)):
        strawberry_bit(m, (x, y + 0.022, z), 0.014)
    for k in range(9):
        a = k * 0.97
        blob(m, (0.007, 0.007, 0.007), (0.045 * math.cos(a) * (0.5 + 0.5 * (k % 3) / 2), y + 0.0205, 0.045 * math.sin(a) * (0.6 + 0.2 * (k % 2))), "tex:blueberry", 8, 6, uv="sph")
    lathe(m, [(0, 0), (0.05, 0), (0.054, 0.0006), (0.05, 0.0012), (0, 0.0022)], (0.02, y + 0.0155, -0.02), "tex:honey", 22, uv="top", warp=wobble(5, 1.1, 0.2))


@bakery("donut_pink_sprinkles")
def _(m, rng):
    lathe(m, torus_prof(0.032, 0.0175, 0.0175, 14), (0, 0, 0), "tex:bread_crust", 32, uv="cyl", closed=True, disp=(0.0008, 60))
    lathe(m, torus_prof(0.032, 0.0196, 0.0175, 12, 150, 25), (0, 0, 0), "tex:sprinkles", 32, uv="cyl", disp=(0.0006, 50),
          warp=lambda x, y, z: (x, y - 0.0008 * math.sin(math.atan2(z, x) * 7) ** 2, z), tile=(3, 1))


@bakery("donut_chocolate")
def _(m, rng):
    lathe(m, torus_prof(0.034, 0.0165, 0.0165, 14), (0, 0, 0), "tex:bread_crust", 32, uv="cyl", closed=True, disp=(0.0008, 60))
    lathe(m, torus_prof(0.034, 0.0186, 0.0165, 12, 155, 22), (0, 0, 0), "f_icing_choc", 32, disp=(0.0005, 55),
          warp=lambda x, y, z: (x, y - 0.0009 * math.sin(math.atan2(z, x) * 5 + 1) ** 2, z))
    seeds(m, rng, 26, (0, 0, 0.034, 0.034), 0, "f_icing_white", (0.0025, 0.0006, 0.0006),
          ground=lambda x, z: 0.0165 + 0.0186 * math.sqrt(max(0.0, 1 - ((math.hypot(x, z) - 0.034) / 0.0186) ** 2)) * 0.97 + 0.0004)


@bakery("cupcake_swirl")
def _(m, rng):
    paper_cup(m, 0.0225, 0.0325, 0.04, (0, 0, 0), "f_icing_pink")
    dome(m, 0.034, 0.012, (0, 0.04, 0), "tex:sponge", 24, 4, uv="sph", disp=(0.0008, 60))
    frosting_swirl(m, 0.036, 0.048, (0, 0.046, 0), "f_icing_white")
    blob(m, (0.009, 0.009, 0.009), (0.0, 0.098, 0.0), "tex:cherry", 10, 8, uv="sph")
    tube3(m, [(0, 0.103, 0), (0.004, 0.115, 0.001)], 0.0007, "f_stem", 5, caps=False)


@bakery("muffin_choc_chip")
def _(m, rng):
    paper_cup(m, 0.026, 0.036, 0.042, (0, 0, 0), "f_cream")
    top = lambda x, y, z: (x * (1 + 0.1 * max(0.0, (y - 0.0) / 0.03)), y, z * (1 + 0.1 * max(0.0, (y - 0.0) / 0.03)))
    lathe(m, [(0.0, 0.0), (0.034, 0.0), (0.04, 0.012), (0.047, 0.024), (0.048, 0.03), (0.04, 0.04), (0.025, 0.048), (0.0, 0.05)], (0, 0.038, 0), "tex:cookie", 28,
          uv="sph", disp=(0.002, 28), warp=top)


@bakery("pie_apple_lattice")
def _(m, rng):
    R = 0.115
    lathe(m, [(0, 0), (R - 0.02, 0.0), (R, 0.025), (R + 0.006, 0.03), (R + 0.006, 0.033), (R - 0.005, 0.033), (R - 0.01, 0.009), (0, 0.009)], (0, 0, 0), "f_steel", 36)
    lathe(m, [(0, 0), (R - 0.005, 0), (R - 0.001, 0.024), (R + 0.002, 0.034), (R - 0.01, 0.038), (R - 0.02, 0.026), (0, 0.026)], (0, 0.003, 0), "tex:pie_crust", 36,
          uv="top", warp=wobble(30, 0.0, 0.025))
    lathe(m, [(0, 0), (R - 0.014, 0), (R - 0.014, 0.012), (0, 0.016)], (0, 0.027, 0), "tex:pie_filling", 30, uv="top", disp=(0.002, 40))
    for k in range(-3, 4):
        c = k * 0.026
        half = math.sqrt(max(R * R * 0.78 - c * c, 0.0)) * 0.98
        slab(m, 0.0145, 0.006, half * 2, (c, 0.042, 0), "tex:pie_crust", "box", 0.002, rot=(0, 0.0, 0), warp=lambda x, y, z: (x, y + 0.004 * (1 - (z / max(half, 1e-3)) ** 2), z))
        slab(m, half * 2, 0.0055, 0.0145, (0, 0.045, c), "tex:pie_crust", "box", 0.002, warp=lambda x, y, z: (x, y + 0.003 * (1 - (x / max(half, 1e-3)) ** 2), z))


@bakery("cookies_on_plate")
def _(m, rng):
    plate(m, 0.12)
    spots = [(-0.04, 0.03, 0.0), (0.035, 0.035, 0.8), (0.0, -0.045, 1.6), (-0.05, -0.04, 2.4), (0.055, -0.03, 3.1)]
    for (x, z, a) in spots:
        disc(m, 0.036, 0.009, (x, 0.0095, z), "tex:cookie", 20, uv="top", disp=(0.0015, 34), edge=0.8, rot=(0, a, 0))
    disc(m, 0.036, 0.009, (0.0, 0.0185, 0.0), "tex:cookie", 20, uv="top", disp=(0.0015, 34), edge=0.8, rot=(0.04, 0.4, 0.03))
    disc(m, 0.034, 0.009, (-0.01, 0.0275, 0.005), "tex:cookie", 20, uv="top", disp=(0.0015, 34), edge=0.8, rot=(0.05, 1.4, -0.04))


@bakery("cinnamon_roll")
def _(m, rng):
    plate(m, 0.09, "f_plate_blue", seg=26)
    n = 70
    pts, pts2 = [], []
    for k in range(n):
        t = k / (n - 1)
        a = t * TAU * 2.7
        pts.append(((0.012 + t * 0.036) * math.cos(a), 0.0215, (0.012 + t * 0.036) * math.sin(a)))
        pts2.append(((0.0145 + t * 0.036) * math.cos(a + 0.35), 0.0222, (0.0145 + t * 0.036) * math.sin(a + 0.35)))
    tube3(m, pts, [0.0075 + 0.0045 * (1 - i / (n - 1)) for i in range(n)], "tex:croissant", 10, uv=True, tile=(2, 8), flat=1.5, disp=(0.0007, 60))
    tube3(m, [(x, 0.0215 + 0.0022, z) for x, _, z in pts2], 0.0016, "f_caramel", 6)
    path = []
    for k in range(13):
        zz = -0.04 + k * 0.0067
        xx = 0.034 * math.sqrt(max(0.0, 1 - (zz / 0.044) ** 2)) * (1 if k % 2 else -1)
        path.append((xx, 0.0345, zz))
    tube3(m, path, 0.0026, "f_icing_white", 6, caps=True)


@bakery("pretzel_salted")
def _(m, rng):
    r = 0.0105
    bowl = [(0.078 * math.cos(math.radians(a)), 0.012 + 0.07 * math.sin(math.radians(a))) for a in range(180, -1, -15)]
    tube3(m, [(x, r, z) for x, _, z in spline([(x, 0, z) for x, z in bowl], 4)], r, "tex:pretzel", 10, uv=True, disp=(0.0008, 50), tile=(2, 6))
    armA = [(-0.078, 0.012), (-0.074, -0.03), (-0.045, -0.068), (0.0, -0.07), (0.035, -0.04), (0.02, -0.005), (-0.02, 0.02), (-0.05, 0.05), (-0.062, 0.062)]
    for sgn, yy in ((1, 0.0105), (-1, 0.0105)):
        pts = spline([(sgn * x, 0, z) for x, z in armA], 4)
        n = len(pts)
        tube3(m, [(x, yy + (0.0125 if (sgn > 0 and 0.4 < i / n < 0.75) else 0.0), z) for i, (x, _, z) in enumerate(pts)], r, "tex:pretzel", 10, uv=True, tile=(2, 6))
    seeds(m, rng, 50, (0, 0.0, 0.075, 0.06), 0, "f_white", (0.0024, 0.0013, 0.0016), ground=lambda x, z: 0.0225)


@bakery("toast_in_rack")
def _(m, rng):
    m.box((0.1, 0.005, 0.17), (0, 0.0025, 0), "f_steel", 0.001)
    for k in range(3):
        zc = -0.06 + k * 0.06
        for sx in (-0.047, 0.047):
            m.link((sx, 0.004, zc), (sx, 0.085, zc), 0.002, "f_steel", 6)
        m.link((-0.047, 0.085, zc), (0.047, 0.085, zc), 0.002, "f_steel", 6)
    for sx in (-0.047, 0.047):
        m.link((sx, 0.004, -0.085), (sx, 0.004, 0.085), 0.002, "f_steel", 6)
    for k in range(2):
        zc = -0.03 + k * 0.06
        slab(m, 0.09, 0.075, 0.012, (0, 0.006, zc), "tex:bread_crust", "box", 0.004)
        blob(m, (0.0455, 0.03, 0.0063), (0, 0.075, zc), "tex:bread_crust", 16, 8, uv="sph")
        slab(m, 0.07, 0.06, 0.0125, (0, 0.012, zc), "tex:bread_crumb", "box", 0.002)


@bakery("brioche_loaf")
def _(m, rng):
    L = 0.27
    prof = [(0.0, -L / 2), (0.04, -L / 2 + 0.003), (0.055, -L / 2 + 0.025), (0.06, -L / 2 + 0.06), (0.06, 0.0), (0.06, L / 2 - 0.06), (0.055, L / 2 - 0.025),
            (0.04, L / 2 - 0.003), (0.0, L / 2)]
    lathe(m, prof, (0, 0.042, 0), "tex:bread_crust", 20, rot=(0, 0, PI / 2), scale=(1, 1, 0.62), uv="cyl", disp=(0.0014, 30), tile=(2, 3))
    for k in range(4):
        x = -0.095 + k * 0.063
        blob(m, (0.037, 0.04, 0.052), (x, 0.05, 0.0), "tex:bread_crust", 14, 10, uv="sph", disp=(0.0016, 40), tile=(2, 1))
    m.box((0.3, 0.004, 0.13), (0, 0.002 - 0.0, 0), "f_wood_light", 0.0015)


@bakery("layer_cake_birthday")
def _(m, rng):
    lathe(m, [(0, 0), (0.1, 0), (0.1, 0.006), (0.013, 0.012), (0.013, 0.05), (0.03, 0.054), (0.12, 0.058), (0.12, 0.064), (0, 0.064)], (0, 0, 0), "f_plate_cream", 36)
    y = 0.064
    ytop = y + 3 * 0.036 + 2 * 0.007
    for k in range(3):
        lathe(m, [(0, 0), (0.095, 0), (0.095, 0.036), (0, 0.036)], (0, y, 0), "tex:sponge", 32, uv="cyl", disp=(0.0006, 30))
        y += 0.036
        if k < 2:
            lathe(m, [(0, 0), (0.0985, 0.0), (0.0985, 0.007), (0, 0.007)], (0, y, 0), "f_icing_pink", 32, warp=wobble(9, k, 0.012))
            y += 0.007
    lathe(m, [(0.0965, ytop - 0.1), (0.1005, ytop - 0.1), (0.1005, ytop - 0.003), (0.098, ytop + 0.003), (0.0, ytop + 0.003)], (0, 0, 0), "f_icing_choc", 40,
          warp=wobble(7, 0.3, 0.012))
    for k in range(9):
        a = k * TAU / 9 + 0.2
        ln = 0.02 + 0.014 * ((k * 5) % 3)
        tube3(m, [(0.0995 * math.cos(a), ytop - 0.002, 0.0995 * math.sin(a)), (0.1015 * math.cos(a), ytop - 0.012, 0.1015 * math.sin(a)),
                  (0.1015 * math.cos(a), ytop - 0.012 - ln, 0.1015 * math.sin(a))], 0.0045, "f_icing_white", 6)
    for k, a in enumerate((0.5, 1.5, 2.6, 3.7, 4.8, 5.8)):
        r = 0.08
        blob(m, (0.011, 0.011, 0.011), (r * math.cos(a), ytop + 0.011, r * math.sin(a)), "tex:strawberry" if k % 2 else "tex:cherry", 10, 8, uv="sph")
    for (cx, cz, col) in ((-0.02, 0.0, "f_cap_red"), (0.02, 0.02, "f_plastic_clear_cap"), (0.0, -0.025, "f_cap_green")):
        m.cyl(0.0028, 0.05, (cx, ytop + 0.028, cz), col, seg=6)
        blob(m, (0.0045, 0.009, 0.0045), (cx, ytop + 0.058, cz), "em_amber", 6, 5, uv=None)


@bakery("cake_slice_chocolate")
def _(m, rng):
    plate(m, 0.1, "f_plate_dark", seg=28)
    y = 0.008
    ys = y
    wedge(m, 0.1, 0.02, 40, (-0.05, ys, 0.0), "f_chocolate_milk")
    wedge(m, 0.1, 0.007, 40, (-0.05, ys + 0.02, 0.0), "f_cream")
    wedge(m, 0.1, 0.02, 40, (-0.05, ys + 0.027, 0.0), "f_chocolate_milk")
    wedge(m, 0.1, 0.006, 40, (-0.05, ys + 0.047, 0.0), "f_icing_choc")
    blob(m, (0.012, 0.012, 0.012), (0.01, ys + 0.058, 0.0), "tex:cherry", 10, 8, uv="sph")
    for k in range(5):
        tube3(m, [(0.046, ys + 0.045 - 0.0 * k, -0.017 + k * 0.0085), (0.05, ys + 0.041, -0.017 + k * 0.0085), (0.0515, ys + 0.03 - 0.004 * (k % 3), -0.017 + k * 0.0085)], 0.0025, "f_icing_choc", 5)


# ================================================================ DESSERT
dessert = menu.cat("dessert", tags=("food", "dessert"))


@dessert("ice_cream_cone_double")
def _(m, rng):
    lathe(m, [(0.0, 0.0), (0.0015, 0.0), (0.0345, 0.125), (0.0, 0.125)], (0, 0.03, 0), "tex:waffle_cone", 22, uv="cyl", tile=(3, 1))
    blob(m, (0.037, 0.036, 0.037), (0, 0.17, 0), "f_ice_cream_van", 20, 12, uv=None, disp=(0.003, 40))
    lathe(m, torus_prof(0.034, 0.006, 0.152, 8), (0, 0, 0), "f_ice_cream_van", 22, closed=True, warp=wobble(11, 0.0, 0.08))
    blob(m, (0.034, 0.033, 0.034), (0.002, 0.223, 0.001), "f_ice_cream_straw", 20, 12, uv=None, disp=(0.003, 40))
    lathe(m, torus_prof(0.031, 0.0055, 0.2, 8), (0, 0, 0), "f_ice_cream_straw", 22, closed=True, warp=wobble(9, 1.0, 0.08))
    for k in range(10):
        a = k * 2.4
        blob(m, (0.003, 0.0014, 0.0014), (0.026 * math.cos(a), 0.226 + 0.014 * math.sin(a * 1.7), 0.026 * math.sin(a)), "f_chocolate_dark", 5, 3, uv=None, rot=(0, a, 0))
    # four-prong holder so it can stand
    m.cyl(0.04, 0.012, (0, 0.006, 0), "f_steel", seg=18)
    for k in range(4):
        a = k * PI / 2 + PI / 4
        m.link((0.012 * math.cos(a), 0.012, 0.012 * math.sin(a)), (0.034 * math.cos(a), 0.095, 0.034 * math.sin(a)), 0.0018, "f_steel", 5)
    m.shift(dy=0.0)


@dessert("sundae_glass")
def _(m, rng):
    outer = [(0.0, 0.0), (0.028, 0.0), (0.006, 0.0), (0.006, 0.05), (0.03, 0.058), (0.048, 0.08), (0.056, 0.13), (0.059, 0.155)]
    outer = [(0.0, 0.0), (0.03, 0.0), (0.03, 0.004), (0.006, 0.012), (0.006, 0.05), (0.032, 0.062), (0.052, 0.088), (0.058, 0.125), (0.059, 0.15)]
    vessel(m, outer, 0.003, (0, 0, 0), "f_glass", 28)
    lathe(m, [(0, 0.062), (0.03, 0.065), (0.046, 0.09), (0.052, 0.112), (0.0, 0.112)], (0, 0, 0), "f_ice_cream_choc", 24, disp=(0.002, 40))
    lathe(m, [(0, 0.11), (0.052, 0.11), (0.054, 0.125), (0.0, 0.125)], (0, 0, 0), "f_ice_cream_van", 24, warp=wobble(6, 0.0, 0.1))
    blob(m, (0.04, 0.032, 0.04), (0.0, 0.158, 0.0), "f_ice_cream_van", 20, 12, uv=None, disp=(0.003, 40))
    blob(m, (0.032, 0.026, 0.032), (0.006, 0.185, 0.0), "f_ice_cream_straw", 18, 10, uv=None, disp=(0.003, 40))
    lathe(m, [(0, 0), (0.034, 0), (0.037, 0.003), (0.03, 0.012), (0, 0.016)], (0, 0.172, 0), "f_icing_choc", 22, warp=wobble(7, 0.2, 0.16))
    blob(m, (0.01, 0.01, 0.01), (0.0, 0.22, 0.0), "tex:cherry", 10, 8, uv="sph")
    slab(m, 0.012, 0.09, 0.003, (0.03, 0.19, 0.0), "tex:waffle_cone", "box", 0.001, rot=(0, 0, -0.35))
    slab(m, 0.012, 0.09, 0.003, (-0.03, 0.19, 0.0), "tex:waffle_cone", "box", 0.001, rot=(0, 0, 0.35))


@dessert("cheesecake_slice")
def _(m, rng):
    plate(m, 0.1, "f_plate_cream", seg=28)
    y = 0.008
    wedge(m, 0.105, 0.012, 38, (-0.05, y, 0.0), "tex:cookie")
    wedge(m, 0.105, 0.04, 38, (-0.05, y + 0.012, 0.0), "f_cream")
    wedge(m, 0.105, 0.0035, 38, (-0.05, y + 0.052, 0.0), "tex:pie_filling")
    for k in range(6):
        d = 0.045 + 0.012 * (k % 3) + 0.01 * (k // 3)
        zz = (-0.006 + 0.012 * (k % 2)) * (1 + k % 3) * 0.7
        blob(m, (0.0065, 0.0055, 0.0065), (-0.05 + d, y + 0.0635 + 0.003, zz), "tex:blueberry" if k % 2 else "tex:cherry", 8, 6, uv="sph")
    sprig(m, (-0.05 + 0.03, y + 0.0645, 0.0), "f_herb", 3, 0.011, rng)


@dessert("tiramisu_cup")
def _(m, rng):
    vessel(m, [(0.0, 0.0), (0.026, 0.0), (0.04, 0.06)], 0.0025, (0, 0, 0), "f_glass", 24)
    cols = ("f_cream", "f_chocolate_milk", "f_cream", "f_chocolate_milk")
    for k, c in enumerate(cols):
        h0 = 0.003 + k * 0.014
        r0 = 0.0262 + 0.014 * h0 / 0.06 - 0.003
        lathe(m, [(0, h0), (r0, h0), (r0 + 0.0008, h0 + 0.0135), (0, h0 + 0.0135)], (0, 0, 0), c, 24)
    lathe(m, [(0, 0), (0.0385, 0), (0.0385, 0.003), (0.0, 0.0038)], (0, 0.057, 0), "f_chocolate_milk", 24, disp=(0.0008, 80))
    m.link((0.032, 0.058, 0.0), (0.046, 0.095, 0.0), 0.0035, "f_steel", 6)
    blob(m, (0.012, 0.0035, 0.007), (0.05, 0.1, 0.0), "f_steel", 10, 6, uv=None, rot=(0, 0, -0.4))


@dessert("chocolate_bar_open")
def _(m, rng):
    slab(m, 0.16, 0.014, 0.074, (0, 0.0, 0), "f_wrapper_blue", "box", 0.002)
    for i in range(4):
        for j in range(2):
            slab(m, 0.0365, 0.012, 0.0345, (-0.065 + i * 0.0392, 0.012, -0.0188 + j * 0.0376), "tex:chocolate", "box", 0.0035)
    slab(m, 0.06, 0.002, 0.075, (0.095, 0.0, 0.0), "f_wrapper_gold", "box", 0.0005, rot=(0, 0, 0.35))


@dessert("macarons_plate")
def _(m, rng):
    plate(m, 0.1, "f_plate_blue", seg=28)
    cols = ("f_icing_pink", "f_wasabi", "f_butter", "f_chocolate_milk", "f_wrapper_blue", "f_icing_pink")
    for k in range(6):
        a = k * TAU / 6
        x, z = 0.055 * math.cos(a), 0.055 * math.sin(a)
        c = cols[k]
        disc(m, 0.019, 0.006, (x, 0.009, z), c, 18, uv=None, edge=0.9)
        lathe(m, [(0, 0), (0.0172, 0), (0.0176, 0.0025), (0, 0.0025)], (x, 0.015, z), "f_cream", 16, warp=wobble(9, 0, 0.06))
        disc(m, 0.019, 0.006, (x, 0.0175, z), c, 18, uv=None, edge=0.9)
    disc(m, 0.019, 0.006, (0, 0.009, 0), "f_icing_pink", 18, uv=None, edge=0.9)
    lathe(m, [(0, 0), (0.0172, 0), (0.0176, 0.0025), (0, 0.0025)], (0, 0.015, 0), "f_cream", 16, warp=wobble(9, 0, 0.06))
    disc(m, 0.019, 0.006, (0, 0.0175, 0), "f_wasabi", 18, uv=None, edge=0.9)


@dessert("brownie_stack")
def _(m, rng):
    plate(m, 0.1, "f_plate_cream", seg=28)
    for k in range(3):
        slab(m, 0.066, 0.026, 0.066, (0.006 * (1 - k), 0.008 + k * 0.026, 0.004 * k), "tex:brownie", "box", 0.003, rot=(0, 0.25 * (k - 1) + 0.1, 0), disp=(0.0008, 70))
    blob(m, (0.02, 0.012, 0.02), (0.0, 0.088, 0.0), "f_ice_cream_van", 14, 8, uv=None, disp=(0.002, 40))
    lathe(m, [(0, 0), (0.03, 0), (0.034, 0.002), (0.0, 0.005)], (0, 0.082, 0), "f_icing_choc", 20, warp=wobble(5, 0.5, 0.2))
    seeds(m, rng, 12, (0, 0, 0.02, 0.02), 0.099, "f_nut", (0.004, 0.0025, 0.0035))


@dessert("creme_caramel")
def _(m, rng):
    plate(m, 0.09, "f_plate", seg=26)
    lathe(m, [(0, 0), (0.033, 0), (0.0365, 0.02), (0.034, 0.044), (0.027, 0.05), (0.0, 0.052)], (0, 0.008, 0), "f_butter", 26, disp=(0.0007, 50))
    lathe(m, [(0, 0.0), (0.05, 0.0), (0.056, 0.0012), (0.05, 0.002), (0.0, 0.0025)], (0, 0.008, 0), "f_caramel", 26, warp=wobble(5, 0.2, 0.1))
    lathe(m, [(0, 0.0), (0.024, 0.0), (0.028, 0.004), (0.0, 0.006)], (0, 0.056, 0), "f_caramel", 22, warp=wobble(4, 0.8, 0.12))
    tube3(m, [(0.027, 0.058, 0.0), (0.0332, 0.04, 0.0), (0.0372, 0.02, 0.0), (0.04, 0.0095, 0.0)], 0.0022, "f_caramel", 5, caps=False)
    sprig(m, (0.0, 0.0595, 0.0), "f_herb", 3, 0.01, rng)


@dessert("fruit_tart")
def _(m, rng):
    R = 0.1
    lathe(m, [(0, 0), (R - 0.01, 0.0), (R, 0.012), (R + 0.003, 0.028), (R - 0.003, 0.028), (R - 0.01, 0.01), (0, 0.01)], (0, 0, 0), "tex:pie_crust", 36, uv="top", warp=wobble(36, 0, 0.02))
    lathe(m, [(0, 0), (R - 0.01, 0.0), (R - 0.01, 0.014), (0, 0.016)], (0, 0.012, 0), "f_butter", 32, disp=(0.001, 30))
    for k, (r, n, mt) in enumerate(((0.078, 12, "tex:strawberry"), (0.052, 8, "tex:blueberry"), (0.026, 5, "tex:strawberry"))):
        for i in range(n):
            a = TAU * i / n + k * 0.4
            rad = 0.0105 if mt == "tex:blueberry" else 0.0125
            blob(m, (rad, rad, rad), (r * math.cos(a), 0.034, r * math.sin(a)), mt, 8, 6, uv="sph")
    blob(m, (0.012, 0.012, 0.012), (0, 0.037, 0), "tex:blueberry", 8, 6, uv="sph")
    for k in range(5):
        a = k * 1.3
        sprig(m, (0.04 * math.cos(a), 0.046, 0.04 * math.sin(a)), "f_herb", 2, 0.008, rng, a)


@dessert("jelly_mould")
def _(m, rng):
    plate(m, 0.1, "f_plate", seg=26)
    prof = [(0, 0), (0.044, 0), (0.05, 0.01), (0.045, 0.03), (0.036, 0.055), (0.03, 0.068), (0.0, 0.07)]
    lathe(m, prof, (0, 0.008, 0), "f_jelly_clear", 24, warp=wobble(12, 0.0, 0.08))
    for k in range(5):
        a = k * 1.3
        blob(m, (0.007, 0.007, 0.007), (0.018 * math.cos(a), 0.03 + 0.008 * k, 0.018 * math.sin(a)), "tex:strawberry", 8, 6, uv="sph")
    blob(m, (0.011, 0.011, 0.011), (0, 0.082, 0), "tex:cherry", 10, 8, uv="sph")


menu.register()
