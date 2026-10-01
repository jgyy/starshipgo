"""Procedural food textures (numpy, written as JPEG through Blender's image API).

Every texture is a 256x256 tileable albedo map in godot/textures/food/<name>.jpg. Models use them through the
kit material prefix ``tex:<name>`` (see kit.mat); SURFACE gives the roughness / metallic the kit uses with the map.
No text is drawn anywhere: packaging uses brand-less stripes, pictograms and bars.
"""
import math
import os

import numpy as np

S = 256
TEX = {}        # name -> generator(rng_seed) -> float array (S, S, 3) in 0..1
SURFACE = {}    # name -> (roughness, metallic)


def tex(name, rough=0.6, metal=0.0):
    def deco(fn):
        TEX[name] = fn
        SURFACE[name] = (rough, metal)
        return fn
    return deco


def surface(name):
    return SURFACE.get(name, (0.6, 0.0))


# ---------------------------------------------------------------- numeric helpers
def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def noise(beta, seed, n=S, sx=1.0, sy=1.0):
    """Tileable 1/f^beta noise in 0..1; sx/sy stretch the frequency axes (anisotropic grain)."""
    fx, fy = np.meshgrid(np.fft.fftfreq(n) * sx, np.fft.fftfreq(n) * sy)
    r = np.sqrt(fx ** 2 + fy ** 2)
    r[0, 0] = 1
    g = np.random.default_rng(seed)
    spec = (g.normal(size=(n, n)) + 1j * g.normal(size=(n, n))) / r ** beta
    spec[0, 0] = 0
    a = np.real(np.fft.ifft2(spec))
    return (a - a.min()) / (a.max() - a.min() + 1e-9)


def cells(k, seed, n=S, jitter=0.9):
    """Tileable Voronoi: returns (f1, f2, cell id 0..1), distances in cell units."""
    g = np.random.default_rng(seed)
    jx, jy = g.random((k, k)) * jitter + (1 - jitter) / 2, g.random((k, k)) * jitter + (1 - jitter) / 2
    ids = g.random((k, k))
    yy, xx = np.mgrid[0:n, 0:n] / n * k
    cy, cx = np.floor(yy).astype(int), np.floor(xx).astype(int)
    f1 = np.full((n, n), 9.0)
    f2 = np.full((n, n), 9.0)
    cid = np.zeros((n, n))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            iy, ix = (cy + dy) % k, (cx + dx) % k
            d = np.hypot(cx + dx + jx[iy, ix] - xx, cy + dy + jy[iy, ix] - yy)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, ids[iy, ix], cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def grid():
    yy, xx = np.mgrid[0:S, 0:S] / S
    return xx, yy


def ramp(t, stops):
    """Colour ramp: stops = [(pos, '#hex'), ...]; t array 0..1 -> (.., 3)."""
    pos = [p for p, _ in stops]
    cols = np.array([hexc(c) for _, c in stops])
    t = np.clip(t, 0, 1)
    return np.stack([np.interp(t, pos, cols[:, i]) for i in range(3)], axis=-1)


def mix(a, b, t):
    t = np.asarray(t)[..., None] if np.ndim(t) == 2 else t
    return a * (1 - t) + b * t


def smooth(x, a, b):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


def solid(c, n=S):
    return np.ones((n, n, 3)) * hexc(c)


def speckle(img, seed, density, color, size=1, strength=1.0):
    g = np.random.default_rng(seed)
    m = (g.random((S, S)) < density).astype(float)
    if size > 1:
        m = np.clip(sum(np.roll(np.roll(m, i, 0), j, 1) for i in range(size) for j in range(size)), 0, 1)
    return mix(img, hexc(color), m * strength)


def disc(xx, yy, cx, cy, r, soft=0.01):
    """Soft disc mask with wrap-around."""
    dx = np.minimum(abs(xx - cx), 1 - abs(xx - cx))
    dy = np.minimum(abs(yy - cy), 1 - abs(yy - cy))
    return 1 - smooth(np.hypot(dx, dy), r - soft, r + soft)


def shade(img, f, amount=0.25, bias=0.0):
    """Multiply by (1 + amount*(f-0.5)*2) for a noise-driven darkening / lightening."""
    return np.clip(img * (1 + amount * (f[..., None] - 0.5) * 2 + bias), 0, 1)


# ---------------------------------------------------------------- bakery
@tex("bread_crust", 0.7)
def _(s):
    f = noise(2.0, s)
    img = ramp(f, [(0, "#7a3f16"), (0.45, "#b8742c"), (0.8, "#d99a45"), (1, "#e7b868")])
    img = speckle(img, s, 0.01, "#f2deb0", 2, 0.7)
    return shade(img, noise(3.0, s + 5), 0.12)


@tex("bread_crumb", 0.9)
def _(s):
    f1, f2, _c = cells(22, s)
    pores = smooth(0.34 - f1, 0, 0.3) * (noise(1.5, s + 1) > 0.42)
    img = mix(ramp(noise(2.5, s + 2), [(0, "#e8cf98"), (1, "#f6e6bb")]), hexc("#c49c58"), pores * 0.7)
    return shade(img, noise(3.0, s + 3), 0.05)


@tex("pizza_crust", 0.8)
def _(s):
    f = noise(2.2, s)
    img = ramp(f, [(0, "#d9a95e"), (0.6, "#e6bf78"), (1, "#f0d69a")])
    spots = smooth(noise(1.2, s + 1, sx=2, sy=2), 0.62, 0.78)
    img = mix(img, hexc("#8d4a1d"), spots * 0.85)
    return shade(img, noise(3.0, s + 3), 0.08)


@tex("pizza_top", 0.45)
def _(s):
    xx, yy = grid()
    r = np.hypot(xx - 0.5, yy - 0.5) * 2
    sauce = shade(ramp(noise(2.5, s), [(0, "#9e1f14"), (1, "#c8381f")]), noise(3, s + 1), 0.15)
    f = noise(1.4, s + 2, sx=2.2, sy=2.2)
    cheese_m = smooth(f, 0.3, 0.42) * (1 - smooth(r, 0.84, 0.9))
    cheese = ramp(noise(2.0, s + 3), [(0, "#f2d684"), (0.6, "#f8e6a8"), (1, "#fff2c4")])
    brown = smooth(noise(1.2, s + 4, sx=3, sy=3), 0.66, 0.8)
    cheese = mix(cheese, hexc("#c78a2e"), brown * 0.75)
    img = mix(sauce, cheese, cheese_m)
    oil = smooth(noise(0.8, s + 6, sx=4, sy=4), 0.74, 0.8) * cheese_m
    return np.clip(img + oil[..., None] * 0.12, 0, 1)


@tex("cookie", 0.85)
def _(s):
    f1, _f2, cid = cells(9, s)
    chip = (f1 < 0.2) & (cid > 0.35)
    img = ramp(noise(2.2, s + 1), [(0, "#a8702e"), (0.6, "#c48d45"), (1, "#d9a65e")])
    img = mix(img, hexc("#3a2014"), chip.astype(float) * 0.95)
    crack = smooth(noise(1.0, s + 2, sx=3, sy=3), 0.52, 0.55) * 0.18
    return np.clip(img - crack[..., None], 0, 1)


@tex("sponge", 0.9)
def _(s):
    f1, _f2, _c = cells(26, s)
    img = ramp(noise(2.4, s), [(0, "#e8c874"), (1, "#f6dd96")])
    return mix(img, hexc("#b88a3c"), smooth(0.3 - f1, 0, 0.25) * 0.35 * (noise(1.5, s + 2) > 0.45))


@tex("croissant", 0.5)
def _(s):
    xx, yy = grid()
    layers = 0.5 + 0.5 * np.sin(yy * math.pi * 2 * 9 + noise(2.5, s) * 4)
    f = noise(2.0, s + 1)
    img = ramp(0.6 * f + 0.4 * layers, [(0, "#8a4a1a"), (0.5, "#c0762a"), (1, "#e2a24a")])
    img = speckle(img, s, 0.004, "#fff0c8", 2, 0.6)
    return shade(img, noise(3, s + 3), 0.1)


@tex("pancake", 0.7)
def _(s):
    xx, yy = grid()
    r = np.hypot(xx - 0.5, yy - 0.5) * 2
    f = noise(2.0, s)
    img = ramp(f * 0.7 + smooth(0.7 - r, 0, 0.5) * 0.3, [(0, "#d9a257"), (0.5, "#c8863a"), (1, "#a96a26")])
    ring = smooth(r, 0.85, 0.97)
    img = mix(img, hexc("#e8c27c"), ring * 0.8)
    bubbles = smooth(cells(10, s + 1)[0], 0.3, 0.25) * 0
    return np.clip(img + bubbles[..., None], 0, 1)


@tex("waffle", 0.7)
def _(s):
    xx, yy = grid()
    gx = np.abs(np.sin(xx * math.pi * 6)) ** 0.5
    gy = np.abs(np.sin(yy * math.pi * 6)) ** 0.5
    pocket = np.minimum(gx, gy)
    img = ramp(0.55 * pocket + 0.45 * noise(2.0, s), [(0, "#a8651f"), (0.5, "#d19a47"), (1, "#eec078")])
    return img


@tex("waffle_cone", 0.75)
def _(s):
    xx, yy = grid()
    d1 = np.abs(np.sin((xx + yy) * math.pi * 8))
    d2 = np.abs(np.sin((xx - yy) * math.pi * 8))
    pocket = np.minimum(d1, d2) ** 0.6
    return ramp(0.6 * pocket + 0.4 * noise(2.2, s), [(0, "#a0652a"), (0.5, "#cf9a52"), (1, "#e9c283")])


@tex("pretzel", 0.5)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#5a2a12"), (0.6, "#7a3a18"), (1, "#9a5324")])
    return speckle(img, s, 0.012, "#f4efe4", 2, 0.95)


@tex("sprinkles", 0.5)
def _(s):
    img = solid("#f4a6c0")
    g = np.random.default_rng(s)
    xx, yy = grid()
    for _ in range(90):
        cx, cy = g.random(2)
        col = ["#ffffff", "#ffd23a", "#3aa0ff", "#41c26b", "#e8302a"][g.integers(0, 5)]
        a = g.random() * math.pi
        t = np.abs((xx - cx) * math.sin(a) - (yy - cy) * math.cos(a))
        l = np.abs((xx - cx) * math.cos(a) + (yy - cy) * math.sin(a))
        m = (t < 0.006) & (l < 0.025)
        img[m] = hexc(col)
    return shade(img, noise(3, s), 0.05)


@tex("chocolate", 0.35)
def _(s):
    return shade(ramp(noise(2.5, s), [(0, "#2a150c"), (1, "#4a2816")]), noise(3, s + 1), 0.05)


@tex("brownie", 0.7)
def _(s):
    cr = smooth(noise(1.0, s, sx=3, sy=3), 0.5, 0.56)
    img = ramp(noise(2.2, s + 1), [(0, "#2e1810"), (1, "#5a3220")])
    return mix(img, hexc("#8a5a3c"), cr * 0.5)


@tex("pie_crust", 0.7)
def _(s):
    f = noise(1.8, s, sy=1.5)
    img = ramp(f, [(0, "#a8651f"), (0.5, "#cf9348"), (1, "#ebc074")])
    return speckle(img, s, 0.006, "#fff2cc", 2, 0.5)


@tex("pie_filling", 0.35)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#6a1a2c"), (1, "#a82a44")])
    return speckle(img, s, 0.01, "#d65a74", 2, 0.6)


@tex("cream", 0.5)
def _(s):
    return shade(ramp(noise(2.5, s), [(0, "#f2ead4"), (1, "#fffaee")]), noise(3, s + 1), 0.03)


# ---------------------------------------------------------------- meat / fish / egg / dairy
@tex("steak", 0.55)
def _(s):
    xx, yy = grid()
    f = noise(2.0, s)
    img = ramp(f, [(0, "#5a2c18"), (0.6, "#7e4426"), (1, "#a05f38")])
    d = ((xx * 1.0 + yy * 0.8) * 6) % 1.0
    mark = smooth(0.2 - np.abs(d - 0.5) * 0.5, 0.0, 0.07)
    mark *= smooth(noise(1.5, s + 1), 0.15, 0.4)
    img = mix(img, hexc("#1c0e08"), mark * 0.9)
    fat = smooth(noise(1.2, s + 2, sx=3, sy=3), 0.7, 0.78)
    return mix(img, hexc("#e8d2b0"), fat * 0.6)


@tex("patty", 0.75)
def _(s):
    f1, _f2, cid = cells(40, s)
    img = ramp(noise(2.0, s + 1), [(0, "#3a1c10"), (0.6, "#5c3220"), (1, "#7a4a30")])
    return mix(img, hexc("#2a140c"), (cid > 0.7) * 0.4)


@tex("chicken_skin", 0.45)
def _(s):
    f = noise(2.2, s)
    img = ramp(f, [(0, "#8d4a1a"), (0.5, "#bd7530"), (1, "#dba04c")])
    f1, _f2, _c = cells(30, s + 1)
    img = mix(img, hexc("#6a3414"), smooth(0.22 - f1, 0, 0.15) * 0.5)
    sheen = smooth(noise(1.2, s + 2, sx=3, sy=3), 0.68, 0.8)
    return np.clip(img + sheen[..., None] * 0.12, 0, 1)


@tex("ham", 0.5)
def _(s):
    f = noise(2.0, s, sx=1, sy=3)
    img = ramp(f, [(0, "#d0707c"), (0.6, "#e29aa0"), (1, "#f0c4c0")])
    return shade(img, noise(3, s + 1), 0.05)


@tex("salami", 0.55)
def _(s):
    f1, _f2, cid = cells(26, s)
    img = ramp(noise(2.2, s + 1), [(0, "#7e2a26"), (1, "#a8443c")])
    return mix(img, hexc("#efd5c8"), (smooth(0.28 - f1, 0, 0.1) * (cid > 0.4)) * 0.9)


@tex("pepperoni", 0.5)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#7a1a12"), (0.6, "#a8261c"), (1, "#c23a28")])
    f1, _f2, cid = cells(18, s + 1)
    img = mix(img, hexc("#e8b8a0"), smooth(0.2 - f1, 0, 0.1) * (cid > 0.55) * 0.7)
    return img


@tex("bacon", 0.55)
def _(s):
    xx, yy = grid()
    w = 0.5 + 0.5 * np.sin(yy * math.pi * 2 * 5 + noise(2.5, s) * 3)
    return mix(solid("#9e3a30"), solid("#f0d8c8"), smooth(w, 0.35, 0.65))


@tex("sausage", 0.5)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#7a3418"), (0.6, "#a85030"), (1, "#c56a40")])
    return shade(img, noise(3, s + 1), 0.08)


@tex("fish_fillet", 0.5)
def _(s):
    f = noise(2.0, s, sx=3, sy=1)
    return ramp(f, [(0, "#d2602e"), (0.5, "#e88650"), (1, "#f2b088")])


@tex("batter", 0.7)
def _(s):
    f = noise(1.8, s)
    img = ramp(f, [(0, "#b8761f"), (0.5, "#d9a042"), (1, "#eec468")])
    return speckle(img, s, 0.01, "#8a5a1a", 2, 0.5)


@tex("cheese_swiss", 0.5)
def _(s):
    img = ramp(noise(2.5, s), [(0, "#eccf62"), (1, "#f6e089")])
    f1, _f2, cid = cells(7, s + 1)
    hole = smooth(0.2 + cid * 0.15 - f1, 0, 0.04) * (cid > 0.5)
    return mix(img, hexc("#bf9a2a"), hole * 0.9)


@tex("cheese_cheddar", 0.5)
def _(s):
    return shade(ramp(noise(2.5, s), [(0, "#e49a20"), (1, "#f0b640")]), noise(3, s + 1), 0.04)


@tex("cheese_brie", 0.8)
def _(s):
    return ramp(noise(2.0, s), [(0, "#f2ecda"), (1, "#fff9ea")])


@tex("butter", 0.4)
def _(s):
    return solid("#f4dc78")


@tex("egg_white", 0.25)
def _(s):
    xx, yy = grid()
    r = np.hypot(xx - 0.5, yy - 0.5) * 2
    img = mix(solid("#f8f6ee"), solid("#fbfaf5"), smooth(r, 0.3, 0.7))
    brown = smooth(r, 0.86, 0.99) * smooth(noise(1.5, s), 0.45, 0.7)
    return mix(img, hexc("#c89a48"), brown * 0.8)


@tex("eggshell_brown", 0.5)
def _(s):
    return speckle(shade(solid("#b98456"), noise(2.5, s), 0.07), s, 0.01, "#8a5a36", 1, 0.5)


@tex("eggshell_white", 0.5)
def _(s):
    return speckle(shade(solid("#f0e8d8"), noise(2.5, s), 0.04), s, 0.006, "#c9bda4", 1, 0.5)


# ---------------------------------------------------------------- fruit and vegetables
def _skin(s, stops, grain=2.5, specks=0.0, speck_col="#ffffff"):
    img = ramp(noise(grain, s), stops)
    if specks:
        img = speckle(img, s + 9, specks, speck_col, 1, 0.55)
    return shade(img, noise(3.2, s + 4), 0.05)


@tex("tomato_skin", 0.3)
def _(s):
    return _skin(s, [(0, "#a8180f"), (0.5, "#c8281a"), (1, "#e04a2a")], 2.5, 0.004, "#f08a6a")


@tex("apple_red", 0.3)
def _(s):
    n = noise(1.8, s, sx=1, sy=5)
    img = ramp(n, [(0, "#a0141a"), (0.5, "#bd2a20"), (0.75, "#d8742a"), (1, "#d9b13a")])
    return speckle(img, s, 0.006, "#f2dca0", 1, 0.7)


@tex("apple_green", 0.3)
def _(s):
    n = noise(1.8, s, sx=1, sy=5)
    img = ramp(n, [(0, "#6a9a2a"), (0.6, "#98c23a"), (1, "#c8d65a")])
    return speckle(img, s, 0.006, "#e8f0b0", 1, 0.6)


@tex("pear_skin", 0.45)
def _(s):
    img = _skin(s, [(0, "#9aa83a"), (0.5, "#bcc24a"), (1, "#d8d068")], 2.2)
    return speckle(img, s, 0.012, "#7a6a2a", 1, 0.6)


@tex("peach_skin", 0.8)
def _(s):
    xx, yy = grid()
    g = noise(1.6, s, sx=1, sy=2)
    return ramp(0.6 * xx + 0.4 * g, [(0, "#e86a3a"), (0.5, "#f2a050"), (1, "#f6c068")])


@tex("orange_peel", 0.5)
def _(s):
    f1, _f2, _c = cells(48, s)
    bump = smooth(f1, 0.0, 0.7)
    img = ramp(noise(2.5, s + 1), [(0, "#e8780f"), (1, "#f59a22")])
    return np.clip(img * (0.82 + 0.25 * bump[..., None]), 0, 1)


@tex("lemon_peel", 0.5)
def _(s):
    f1, _f2, _c = cells(44, s)
    bump = smooth(f1, 0.0, 0.7)
    img = ramp(noise(2.5, s + 1), [(0, "#e8c814"), (1, "#f6e23a")])
    return np.clip(img * (0.85 + 0.2 * bump[..., None]), 0, 1)


@tex("lime_peel", 0.5)
def _(s):
    f1, _f2, _c = cells(48, s)
    bump = smooth(f1, 0.0, 0.7)
    img = ramp(noise(2.5, s + 1), [(0, "#4a8a1a"), (1, "#7ab32a")])
    return np.clip(img * (0.82 + 0.25 * bump[..., None]), 0, 1)


def _citrus_cut(s, rind, pulp, pith, seg):
    xx, yy = grid()
    dx, dy = xx - 0.5, yy - 0.5
    r = np.hypot(dx, dy) * 2
    a = np.arctan2(dy, dx)
    wedge = np.abs(np.sin(a * seg / 2))
    f1, f2, _c = cells(20, s)
    juice = 0.5 + 0.5 * smooth(f2 - f1, 0.0, 0.3)
    img = solid(pulp) * juice[..., None]
    img = mix(img, solid(pith), smooth(0.07 - wedge * r * 0.5, 0.0, 0.05) * (r > 0.1))
    img = mix(img, solid(pith), 1 - smooth(r, 0.0, 0.1))
    img = mix(img, solid(pith), smooth(r, 0.86, 0.9))
    return mix(img, solid(rind), smooth(r, 0.93, 0.97))


@tex("orange_cut", 0.25)
def _(s):
    return _citrus_cut(s, "#e8780f", "#f8a020", "#f9e6b0", 10)


@tex("lemon_cut", 0.25)
def _(s):
    return _citrus_cut(s, "#e8c814", "#f6e060", "#fdf5c8", 9)


@tex("lime_cut", 0.25)
def _(s):
    return _citrus_cut(s, "#3c7a18", "#a8d050", "#e8f0b8", 9)


@tex("banana_skin", 0.55)
def _(s):
    xx, yy = grid()
    g = noise(2.0, s, sx=1, sy=4)
    img = ramp(g, [(0, "#d8b420"), (0.6, "#ecc830"), (1, "#f4dc50")])
    ridge = smooth(np.abs(np.sin(xx * math.pi * 10)), 0.9, 1.0)
    img = mix(img, hexc("#a88418"), ridge * 0.35)
    img = speckle(img, s, 0.004, "#6a4a14", 2, 0.8)
    tip = smooth(np.abs(yy - 0.5) * 2, 0.9, 1.0)
    return mix(img, hexc("#4a3a1a"), tip)


@tex("strawberry", 0.4)
def _(s):
    xx, yy = grid()
    img = ramp(noise(2.2, s) * 0.6 + (1 - yy) * 0.4, [(0, "#a8101a"), (0.6, "#d02030"), (1, "#e8503c")])
    f1, _f2, _c = cells(14, s + 1)
    seed = smooth(0.12 - f1, 0, 0.05)
    img = mix(img, hexc("#8a1018"), smooth(0.22 - f1, 0, 0.1) * 0.5)
    return mix(img, hexc("#f2d878"), seed)


@tex("watermelon_rind", 0.45)
def _(s):
    xx, yy = grid()
    w = np.sin((xx + noise(2.0, s) * 0.18) * math.pi * 2 * 5)
    return mix(solid("#1a4a22"), solid("#6aa84a"), smooth(w, -0.2, 0.5)) * (0.9 + 0.2 * noise(3, s + 1)[..., None])


@tex("watermelon_flesh", 0.3)
def _(s):
    xx, yy = grid()
    g = noise(2.5, s)
    img = ramp(g, [(0, "#e03048"), (1, "#f0586a")])
    gg = np.random.default_rng(s)
    for _ in range(14):
        cx, cy = gg.random(2)
        m = disc(xx, yy, cx, cy, 0.02, 0.006)
        img = mix(img, hexc("#14100e"), m * 0.95)
    return img


@tex("pineapple", 0.55)
def _(s):
    xx, yy = grid()
    d1 = np.abs(((xx + yy) * 6) % 1 - 0.5) * 2
    d2 = np.abs(((xx - yy) * 6) % 1 - 0.5) * 2
    cell = np.minimum(d1, d2)
    img = ramp(noise(2.2, s) * 0.5 + cell * 0.5, [(0, "#8a5a14"), (0.5, "#c9962a"), (1, "#e6c050")])
    return mix(img, hexc("#4a3010"), smooth(0.14 - cell, 0, 0.08) * 0.6)


@tex("kiwi_cut", 0.3)
def _(s):
    xx, yy = grid()
    dx, dy = xx - 0.5, yy - 0.5
    r = np.hypot(dx, dy) * 2
    a = np.arctan2(dy, dx)
    streak = 0.5 + 0.5 * np.sin(a * 36)
    img = mix(solid("#7ab82a"), solid("#a8d44a"), streak * smooth(r, 0.2, 0.8))
    img = mix(img, solid("#eef0c0"), 1 - smooth(r, 0.12, 0.3))
    for k in range(26):
        ang = k / 26 * math.pi * 2 + (k % 2) * 0.1
        rr = 0.17 + (k % 3) * 0.03
        img = mix(img, hexc("#14100e"), disc(xx, yy, 0.5 + math.cos(ang) * rr, 0.5 + math.sin(ang) * rr, 0.014, 0.005) * 0.95)
    return mix(img, solid("#6a5030"), smooth(r, 0.93, 0.98))


@tex("grape_skin", 0.35)
def _(s):
    img = ramp(noise(2.2, s), [(0, "#2a1048"), (0.6, "#4a2068"), (1, "#6a3a88")])
    return mix(img, hexc("#8a7aa8"), smooth(noise(1.5, s + 1), 0.6, 0.9) * 0.35)


@tex("grape_green", 0.35)
def _(s):
    return ramp(noise(2.2, s), [(0, "#8aa83a"), (0.6, "#b0c64a"), (1, "#d2d878")])


@tex("cherry", 0.2)
def _(s):
    return ramp(noise(2.5, s), [(0, "#5a0814"), (0.6, "#8a0f1e"), (1, "#b01a2a")])


@tex("blueberry", 0.5)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#1e2a5a"), (0.6, "#343e7a"), (1, "#5a64a0")])
    return mix(img, hexc("#8a96c2"), smooth(noise(1.4, s + 1), 0.55, 0.85) * 0.4)


@tex("pomegranate_skin", 0.45)
def _(s):
    return ramp(noise(1.8, s, sx=1, sy=2), [(0, "#7a0f18"), (0.6, "#a82230"), (1, "#d2603a")])


@tex("mango_skin", 0.5)
def _(s):
    xx, yy = grid()
    g = noise(1.8, s)
    return ramp(0.5 * g + 0.5 * xx, [(0, "#c8282a"), (0.5, "#e8902a"), (1, "#d8c030")])


@tex("coconut", 0.9)
def _(s):
    img = ramp(noise(1.2, s, sx=2, sy=2), [(0, "#3a2414"), (0.5, "#5c3a1e"), (1, "#8a5e34")])
    return speckle(img, s, 0.1, "#2a180c", 1, 0.5)


@tex("pumpkin", 0.55)
def _(s):
    xx, yy = grid()
    rib = 0.5 + 0.5 * np.cos(xx * math.pi * 2 * 10)
    img = ramp(noise(2.2, s) * 0.5 + rib * 0.5, [(0, "#c85a0a"), (0.5, "#e07a1a"), (1, "#f09a32")])
    return img


@tex("carrot", 0.5)
def _(s):
    xx, yy = grid()
    g = noise(1.8, s, sx=1, sy=5)
    img = ramp(g, [(0, "#d8600f"), (0.6, "#ec7e1a"), (1, "#f59a36")])
    ring = smooth(np.abs(np.sin(yy * math.pi * 2 * 9 + g * 6)), 0.93, 1.0)
    return mix(img, hexc("#b84a0a"), ring * 0.45)


@tex("corn", 0.4)
def _(s):
    f1, f2, _c = cells(16, s, jitter=0.2)
    edge = smooth(f2 - f1, 0.0, 0.25)
    img = solid("#d8a014") * (0.55 + 0.45 * edge[..., None]) + hexc("#ffe27a") * 0.18 * (edge ** 2)[..., None]
    return np.clip(img * (0.95 + 0.1 * noise(2.5, s + 1)[..., None]), 0, 1)


@tex("corn_husk", 0.8)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=6), [(0, "#6a9a30"), (0.6, "#8cb83e"), (1, "#b4d060")])


@tex("pepper_red", 0.25)
def _(s):
    return _skin(s, [(0, "#a8100f"), (0.5, "#cc1c14"), (1, "#e43a22")], 2.2)


@tex("pepper_green", 0.25)
def _(s):
    return _skin(s, [(0, "#2a6a14"), (0.5, "#3e8a1c"), (1, "#5aa82e")], 2.2)


@tex("pepper_yellow", 0.25)
def _(s):
    return _skin(s, [(0, "#d8a014"), (0.5, "#eec21e"), (1, "#f8dc4a")], 2.2)


@tex("chili_red", 0.25)
def _(s):
    return _skin(s, [(0, "#8a0a0a"), (0.5, "#bd1410"), (1, "#e0302a")], 1.8)


@tex("eggplant", 0.2)
def _(s):
    xx, yy = grid()
    img = ramp(noise(2.2, s, sx=1, sy=3), [(0, "#1e0a2e"), (0.6, "#341446"), (1, "#54246a")])
    return np.clip(img + smooth(noise(1.4, s + 1, sx=4, sy=1), 0.7, 0.85)[..., None] * 0.1, 0, 1)


@tex("onion_skin", 0.45)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=6), [(0, "#a86a2a"), (0.6, "#c8883a"), (1, "#e0a85a")])


@tex("onion_red", 0.4)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=6), [(0, "#6a1a3a"), (0.6, "#8a2a52"), (1, "#b04a76")])


@tex("garlic", 0.5)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=6), [(0, "#d8cfc0"), (0.6, "#ece6da"), (1, "#faf8f0")])


@tex("potato_skin", 0.7)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#a07c48"), (0.6, "#bd9a62"), (1, "#d2b480")])
    return speckle(img, s, 0.014, "#6a4a28", 2, 0.8)


@tex("radish", 0.3)
def _(s):
    xx, yy = grid()
    return ramp(noise(2.2, s) * 0.5 + yy * 0.6, [(0, "#d02060"), (0.55, "#e0386a"), (0.8, "#f4c8d0"), (1, "#faf4f0")])


@tex("cucumber", 0.35)
def _(s):
    img = ramp(noise(1.8, s, sx=1, sy=4), [(0, "#1e5a1a"), (0.6, "#2e7a24"), (1, "#5aa040")])
    return speckle(img, s, 0.01, "#a8d078", 1, 0.5)


@tex("broccoli", 0.7)
def _(s):
    f1, _f2, _c = cells(40, s)
    img = ramp(noise(2.0, s + 1), [(0, "#1a4a14"), (0.6, "#2e6a20"), (1, "#4a8a30")])
    return np.clip(img * (0.7 + 0.5 * smooth(f1, 0.0, 0.7)[..., None]), 0, 1)


@tex("mushroom_cap", 0.6)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#a87a52"), (0.6, "#c09870"), (1, "#d8b890")])
    return mix(img, hexc("#f0e2cc"), smooth(noise(1.2, s + 1, sx=3, sy=3), 0.65, 0.85) * 0.6)


@tex("mushroom_white", 0.55)
def _(s):
    return ramp(noise(2.0, s), [(0, "#ddd2c0"), (0.6, "#ece4d4"), (1, "#f8f4ea")])


@tex("mushroom_stem", 0.7)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=6), [(0, "#d8cdb8"), (1, "#f2eadc")])


def _leaf(s, dark, light, vein, mid_w=0.012):
    xx, yy = grid()
    f = noise(2.2, s)
    img = ramp(f, [(0, dark), (1, light)])
    c = np.abs(xx - 0.5)
    midrib = smooth(mid_w - c, 0, mid_w * 0.5)
    side = np.abs(((yy * 7 + c * 5) % 1.0) - 0.5)
    sv = smooth(0.04 - side, 0, 0.03) * (c > 0.015)
    img = mix(img, hexc(vein), np.clip(midrib * 0.9 + sv * 0.55, 0, 1))
    return img


@tex("leaf", 0.55)
def _(s):
    return _leaf(s, "#1c4a18", "#3a7a2a", "#8abf5a")


@tex("leaf_basil", 0.4)
def _(s):
    return _leaf(s, "#1a5a1a", "#2f8a30", "#6abf5a", 0.01)


@tex("leaf_mint", 0.6)
def _(s):
    return _leaf(s, "#2a6a2a", "#4aa044", "#a0d68a")


@tex("lettuce", 0.5)
def _(s):
    xx, yy = grid()
    f1, f2, _c = cells(7, s, jitter=0.8)
    veins = smooth(0.18 - (f2 - f1), 0, 0.15)
    img = ramp(noise(2.0, s + 1) * 0.6 + (1 - yy) * 0.4, [(0, "#6aa832"), (0.6, "#9bd048"), (1, "#d4eb8a")])
    return mix(img, hexc("#e8f5b0"), veins * 0.5)


@tex("cabbage", 0.45)
def _(s):
    f1, f2, _c = cells(6, s, jitter=0.8)
    veins = smooth(0.2 - (f2 - f1), 0, 0.12)
    img = ramp(noise(2.0, s + 1), [(0, "#7aa84a"), (0.6, "#a6cc70"), (1, "#d4ecac")])
    return mix(img, hexc("#f0f6dc"), veins * 0.6)


@tex("cabbage_red", 0.45)
def _(s):
    f1, f2, _c = cells(6, s, jitter=0.8)
    veins = smooth(0.2 - (f2 - f1), 0, 0.12)
    img = ramp(noise(2.0, s + 1), [(0, "#5a1a50"), (0.6, "#8a3a7a"), (1, "#b070a0")])
    return mix(img, hexc("#e8d0e0"), veins * 0.5)


@tex("spinach", 0.5)
def _(s):
    return _leaf(s, "#14400f", "#2a6a1c", "#7ab050")


@tex("wheat", 0.6)
def _(s):
    return ramp(noise(1.6, s, sx=1, sy=5), [(0, "#b8902a"), (0.6, "#d8b24a"), (1, "#eed078")])


@tex("herb_dill", 0.6)
def _(s):
    return ramp(noise(1.3, s, sx=1, sy=5), [(0, "#4a7a2a"), (1, "#8ab44a")])


# ---------------------------------------------------------------- cooked staples
@tex("pasta", 0.55)
def _(s):
    return shade(ramp(noise(2.2, s), [(0, "#e0c070"), (1, "#f2dc96")]), noise(3, s + 1), 0.06)


@tex("noodle", 0.5)
def _(s):
    xx, yy = grid()
    f = noise(2.0, s, sx=6, sy=1)
    img = ramp(f, [(0, "#d8b45a"), (0.6, "#ecd079"), (1, "#f6e6a4")])
    ln = smooth(np.abs(np.sin(yy * math.pi * 2 * 14 + f * 4)), 0.8, 1.0)
    return mix(img, hexc("#b88f3a"), ln * 0.3)


@tex("rice", 0.55)
def _(s):
    f1, f2, cid = cells(36, s, jitter=0.9)
    sh = smooth(f2 - f1, 0.0, 0.2)
    return solid("#f6f3e8") * (0.78 + 0.22 * sh[..., None]) * (0.95 + 0.05 * cid[..., None])


@tex("rice_fried", 0.55)
def _(s):
    f1, f2, cid = cells(36, s, jitter=0.9)
    sh = smooth(f2 - f1, 0.0, 0.2)
    img = mix(solid("#e8c878"), solid("#9a6a2a"), (cid > 0.7) * 0.5) * (0.8 + 0.2 * sh[..., None])
    img = mix(img, hexc("#4a8a28"), (cells(14, s + 5)[2] > 0.88) * smooth(0.1 - cells(14, s + 5)[0], 0, 0.1) * 0.9)
    return img


@tex("porridge", 0.7)
def _(s):
    return shade(ramp(noise(2.0, s), [(0, "#c8b08a"), (1, "#e2d0ac")]), noise(3, s + 1), 0.06)


@tex("curry", 0.35)
def _(s):
    img = ramp(noise(1.8, s), [(0, "#b4600f"), (0.6, "#d68a22"), (1, "#e8a83a")])
    f1, _f2, cid = cells(12, s + 1)
    img = mix(img, hexc("#f0c060"), smooth(0.2 - f1, 0, 0.1) * (cid > 0.5) * 0.6)
    return mix(img, hexc("#7a3a0a"), smooth(noise(1.2, s + 2, sx=2, sy=2), 0.6, 0.8) * 0.5)


@tex("broth", 0.2)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#a8601a"), (0.6, "#c8842a"), (1, "#dca04a")])
    f1, _f2, cid = cells(10, s + 1)
    return mix(img, hexc("#f0d28a"), smooth(0.2 - f1, 0, 0.06) * (cid > 0.45) * 0.8)


@tex("soup_tomato", 0.2)
def _(s):
    img = ramp(noise(2.2, s), [(0, "#b02a14"), (1, "#d4482a")])
    f1, _f2, cid = cells(9, s + 1)
    return mix(img, hexc("#f2b090"), smooth(0.18 - f1, 0, 0.06) * (cid > 0.6) * 0.7)


@tex("soup_cream", 0.25)
def _(s):
    return ramp(noise(2.2, s), [(0, "#d8c490"), (1, "#eadcb0")])


@tex("soup_green", 0.25)
def _(s):
    return ramp(noise(2.2, s), [(0, "#5a8a28"), (1, "#86b042")])


@tex("bolognese", 0.4)
def _(s):
    f1, _f2, cid = cells(30, s)
    img = ramp(noise(2.0, s + 1), [(0, "#7a1e10"), (0.6, "#a6341c"), (1, "#c84a28")])
    return mix(img, hexc("#5a2a18"), (cid > 0.6) * smooth(0.3 - f1, 0, 0.2) * 0.8)


@tex("cheese_sauce", 0.35)
def _(s):
    img = ramp(noise(2.0, s), [(0, "#e8a820"), (1, "#f6c84a")])
    f = smooth(noise(1.2, s + 2, sx=2, sy=2), 0.7, 0.8)
    return mix(img, hexc("#a85a14"), f * 0.4)


@tex("salad_mix", 0.5)
def _(s):
    g = noise(1.5, s, sx=2, sy=2)
    img = ramp(g, [(0, "#2e6a20"), (0.4, "#6aa832"), (0.7, "#9bd048"), (1, "#d4eb8a")])
    f1, _f2, cid = cells(10, s + 1)
    img = mix(img, hexc("#d02820"), (cid > 0.88) * smooth(0.28 - f1, 0, 0.1))
    return img


@tex("hash", 0.6)
def _(s):
    return ramp(noise(1.8, s), [(0, "#a07838"), (0.6, "#c8a050"), (1, "#e8c878")])


@tex("beans", 0.4)
def _(s):
    f1, _f2, cid = cells(22, s)
    img = ramp(noise(2.0, s + 1), [(0, "#6a2a12"), (1, "#a44a22")])
    return mix(img, hexc("#8a3418"), smooth(0.35 - f1, 0, 0.2) * 0.6)


@tex("jam", 0.2)
def _(s):
    return ramp(noise(2.0, s), [(0, "#6a0f24"), (1, "#a01a36")])


@tex("honey", 0.15)
def _(s):
    return ramp(noise(2.0, s), [(0, "#c8800f"), (1, "#e8a82a")])


@tex("syrup", 0.1)
def _(s):
    return ramp(noise(2.0, s), [(0, "#6a3208"), (1, "#8a4a12")])


@tex("peanut_butter", 0.55)
def _(s):
    return shade(ramp(noise(2.2, s), [(0, "#a87430"), (1, "#c8924a")]), noise(3, s + 1), 0.05)


# ---------------------------------------------------------------- surfaces / wood / weave / drinks
def _wood(s, dark, light, rings=14):
    xx, yy = grid()
    w = noise(2.4, s, sx=1, sy=5)
    g = 0.5 + 0.5 * np.sin((xx * rings + w * 2.2) * math.pi * 2)
    img = ramp(0.5 * g + 0.5 * w, [(0, dark), (1, light)])
    return shade(img, noise(3, s + 2, sx=1, sy=6), 0.06)


@tex("wood_board", 0.55)
def _(s):
    return _wood(s, "#b88a52", "#dcb67c", 10)


@tex("wood_walnut", 0.5)
def _(s):
    return _wood(s, "#3e2414", "#6a4228", 12)


@tex("bamboo", 0.6)
def _(s):
    xx, yy = grid()
    weave = 0.5 + 0.5 * np.sin(xx * math.pi * 2 * 14) * np.sin(yy * math.pi * 2 * 14)
    return ramp(0.6 * weave + 0.4 * noise(2.0, s), [(0, "#a07c40"), (0.6, "#c8a462"), (1, "#e4c888")])


@tex("wicker", 0.7)
def _(s):
    xx, yy = grid()
    a = np.sin(xx * math.pi * 2 * 8 + (np.floor(yy * 8) % 2) * math.pi)
    b = np.sin(yy * math.pi * 2 * 8)
    img = ramp(0.5 + 0.25 * a + 0.25 * b, [(0, "#7a4e22"), (0.5, "#a87438"), (1, "#c89a58")])
    return shade(img, noise(2.5, s), 0.08)


@tex("marble", 0.2)
def _(s):
    xx, yy = grid()
    v = np.abs(np.sin((xx + yy) * 6 + noise(2.5, s) * 9))
    return mix(solid("#f4f2ee"), solid("#9a9ca4"), smooth(0.08 - v, 0, 0.08) * 0.6)


@tex("latte_heart", 0.15)
def _(s):
    xx, yy = grid()
    x, y = (xx - 0.5) * 2, (yy - 0.5) * 2
    base = ramp(noise(2.0, s) * 0.5 + np.hypot(x, y) * 0.5, [(0, "#c8924e"), (0.6, "#8a5a2c"), (1, "#5a3418")])
    ox, oy = x * 1.45, -y * 1.45 + 0.25
    heart = (ox ** 2 + oy ** 2 - 1) ** 3 - ox ** 2 * oy ** 3
    foam = 1 - smooth(heart, -0.02, 0.02)
    foam = np.clip(foam, 0, 1) * (1 - smooth(np.hypot(x, y), 0.8, 0.9))
    return mix(base, hexc("#f4e8d0"), foam)


@tex("latte_rosetta", 0.15)
def _(s):
    xx, yy = grid()
    x, y = (xx - 0.5) * 2, (yy - 0.5) * 2
    base = ramp(noise(2.0, s) * 0.5 + np.hypot(x, y) * 0.5, [(0, "#c8924e"), (0.6, "#8a5a2c"), (1, "#5a3418")])
    wig = np.sin(y * 18) * 0.28 * (1 - np.abs(y)) ** 0.7
    leaf = np.abs(x - wig * 0.0) < (0.62 * np.sqrt(np.clip(1 - np.abs(y * 1.1), 0, 1))) * (0.5 + 0.5 * np.sin(y * 20 + 1.5 * np.abs(x) * 8)) + 0.04
    stem = np.abs(x) < 0.03
    foam = ((leaf & (np.abs(y) < 0.85)) | stem).astype(float)
    foam = np.clip(foam * (1 - smooth(np.hypot(x, y), 0.82, 0.88)), 0, 1)
    return mix(base, hexc("#f2e6cc"), foam * 0.95)


@tex("latte_swirl", 0.15)
def _(s):
    xx, yy = grid()
    x, y = (xx - 0.5) * 2, (yy - 0.5) * 2
    r, a = np.hypot(x, y), np.arctan2(y, x)
    base = ramp(noise(2.0, s) * 0.4 + r * 0.6, [(0, "#d8a868"), (0.6, "#9a6a34"), (1, "#5a3418")])
    spiral = 0.5 + 0.5 * np.sin(a * 2 + r * 14)
    foam = smooth(spiral, 0.55, 0.7) * (1 - smooth(r, 0.78, 0.86))
    return mix(base, hexc("#f2e6cc"), foam * 0.9)


@tex("espresso", 0.12)
def _(s):
    xx, yy = grid()
    r = np.hypot(xx - 0.5, yy - 0.5) * 2
    img = ramp(noise(2.0, s) * 0.5 + (1 - r) * 0.5, [(0, "#3a1c0c"), (0.5, "#6a3a1a"), (1, "#a8742e")])
    return mix(img, hexc("#e8c898"), smooth(noise(1.2, s + 2, sx=3, sy=3), 0.7, 0.85) * 0.3)


@tex("coffee_black", 0.08)
def _(s):
    return ramp(noise(2.0, s), [(0, "#120804"), (1, "#2a1408")])


@tex("cocoa", 0.25)
def _(s):
    xx, yy = grid()
    r = np.hypot(xx - 0.5, yy - 0.5) * 2
    img = ramp(noise(2.0, s), [(0, "#4a2614"), (1, "#6a3a20")])
    marsh = np.zeros((S, S))
    g = np.random.default_rng(s)
    for _ in range(9):
        cx, cy = 0.5 + (g.random() - 0.5) * 0.6, 0.5 + (g.random() - 0.5) * 0.6
        marsh = np.maximum(marsh, disc(xx, yy, cx, cy, 0.07, 0.01))
    img = mix(img, hexc("#f6efe2"), marsh * 0.95)
    return mix(img, hexc("#c8b8a0"), smooth(r, 0.9, 0.98) * 0.5)


@tex("tea", 0.08)
def _(s):
    return ramp(noise(2.0, s), [(0, "#8a4a14"), (1, "#b8741f")])


@tex("beer_foam", 0.5)
def _(s):
    f1, _f2, _c = cells(26, s)
    return solid("#f8f4e8") * (0.85 + 0.15 * smooth(f1, 0, 0.6)[..., None])


@tex("milk_froth", 0.5)
def _(s):
    return shade(ramp(noise(2.5, s), [(0, "#f0e8d8"), (1, "#fcf8ee")]), noise(3, s + 1), 0.03)


@tex("smoothie_pink", 0.3)
def _(s):
    return shade(ramp(noise(2.2, s), [(0, "#d8508a"), (1, "#f08ab0")]), noise(3, s + 1), 0.04)


@tex("smoothie_green", 0.3)
def _(s):
    return shade(ramp(noise(2.2, s), [(0, "#6aa832"), (1, "#9bcf56")]), noise(3, s + 1), 0.04)


@tex("boba", 0.2)
def _(s):
    return ramp(noise(2.0, s), [(0, "#120a08"), (1, "#2a1810")])


@tex("ice", 0.15)
def _(s):
    return ramp(noise(2.0, s), [(0, "#dcecf4"), (1, "#f6fbff")])


# ---------------------------------------------------------------- packaging (brand-less)
def _bands(s, cols, n=None, vertical=False):
    xx, yy = grid()
    t = xx if vertical else yy
    n = n or len(cols)
    img = np.zeros((S, S, 3))
    for i, c in enumerate(cols):
        m = (t >= i / n) & (t < (i + 1) / n)
        img[m] = hexc(c)
    return img


def _label(s, bg, fg, accent, kind):
    xx, yy = grid()
    img = solid(bg)
    if kind == 0:     # horizontal stripes + circle
        img = mix(img, solid(fg), smooth(np.abs(yy - 0.3), 0.07, 0.06) * 0 + (np.abs(yy - 0.28) < 0.05))
        img = mix(img, solid(accent), (np.abs(yy - 0.7) < 0.03))
        img = mix(img, solid(fg), disc(xx % 0.5 + 0.0, yy, 0.25, 0.5, 0.12, 0.005) * (np.abs(yy - 0.5) < 0.13))
    elif kind == 1:   # chevrons
        v = np.abs((xx % 0.25) - 0.125) * 2 + yy * 0.6
        img = mix(img, solid(fg), (np.floor(v * 4) % 2 == 0) * (yy > 0.2) * (yy < 0.8))
        img = mix(img, solid(accent), (np.abs(yy - 0.12) < 0.04))
    elif kind == 2:   # sun / wave
        w = yy - 0.55 - 0.06 * np.sin(xx * math.pi * 8)
        img = mix(img, solid(fg), (w > 0) * (w < 0.12))
        img = mix(img, solid(accent), (w >= 0.12) * (w < 0.2))
        img = mix(img, solid(accent), disc(xx % 0.5, yy, 0.25, 0.3, 0.1, 0.005))
    elif kind == 3:   # big diagonal band
        d = (xx * 2 + yy) % 1.0
        img = mix(img, solid(fg), d < 0.35)
        img = mix(img, solid(accent), (d >= 0.35) & (d < 0.43))
    elif kind == 4:   # dots
        f1, _f2, _c = cells(8, s, jitter=0.1)
        img = mix(img, solid(fg), (f1 < 0.28).astype(float))
        img = mix(img, solid(accent), (np.abs(yy - 0.5) < 0.04))
    else:             # lines of "text" bars
        for k in range(5):
            y0 = 0.3 + k * 0.09
            img = mix(img, solid(fg), (np.abs(yy - y0) < 0.02) & (xx % 0.5 < 0.4 - 0.04 * k))
        img = mix(img, solid(accent), (yy < 0.18))
    return np.clip(img * (0.97 + 0.04 * noise(3, s)[..., None]), 0, 1)


CAN_DESIGNS = [("can_cola", "#8a1018", "#f2f2f2", "#1c1c1c", 0), ("can_lime", "#3a9a2a", "#f4f8d8", "#14501a", 1),
               ("can_orange", "#e8741a", "#fff1dc", "#a83a0a", 2), ("can_blue", "#1c4aa8", "#e8f2ff", "#9ad0f0", 3),
               ("can_grape", "#5a2a8a", "#f0e6ff", "#d8b0f0", 4), ("can_energy", "#101418", "#e8e61a", "#3ad8f0", 5),
               ("can_tonic", "#d8dee2", "#1c5a7a", "#3a9ab8", 1), ("can_coffee", "#3a2418", "#f0d8b0", "#c8883a", 3)]
for _n, _bg, _fg, _ac, _k in CAN_DESIGNS:
    def _mk(bg=_bg, fg=_fg, ac=_ac, k=_k):
        return lambda s: _label(s, bg, fg, ac, k)
    tex(_n, 0.3, 0.6)(_mk())

POUCH_DESIGNS = [("pouch_stew", "#c8b890", "#8a3a22", "#e8e0c8", 0), ("pouch_veg", "#d8dcc8", "#3a7a2a", "#e8c83a", 2),
                 ("pouch_fruit", "#e8d8d0", "#c8283a", "#f0a02a", 4), ("pouch_oats", "#e8dcc0", "#9a6a2a", "#4a6a8a", 1),
                 ("pouch_pasta", "#dcc890", "#c84a1a", "#3a6a2a", 3), ("pouch_coffee", "#2a2420", "#d8a860", "#f0e0c0", 5)]
for _n, _bg, _fg, _ac, _k in POUCH_DESIGNS:
    def _mk2(bg=_bg, fg=_fg, ac=_ac, k=_k):
        return lambda s: _label(s, bg, fg, ac, k)
    tex(_n, 0.35, 0.55)(_mk2())

LABELS = [("label_wine", "#e8e0c8", "#6a1a2a", "#b8902a", 0), ("label_wine_white", "#f0ecd8", "#3a6a3a", "#c8a838", 2),
          ("label_beer", "#c8902a", "#f4e8c0", "#6a2a10", 3), ("label_lager", "#2a6a3a", "#f0e8c8", "#c8a838", 1),
          ("label_whisky", "#f0e4c8", "#3a2414", "#a87a2a", 5), ("label_champagne", "#1a1a1e", "#d4b04a", "#f0e8c8", 4),
          ("label_water", "#d8ecf4", "#2a78c8", "#ffffff", 2), ("label_juice", "#f0a028", "#fff4d8", "#3a8a2a", 4),
          ("label_milk", "#f8f8f4", "#3a78c8", "#d8e8f8", 3), ("label_ration", "#9aa87a", "#2a3a1a", "#e8e0b0", 5),
          ("label_bar_choco", "#5a2a18", "#f0c870", "#e8e0d0", 1), ("label_bar_oat", "#c89a52", "#4a2a14", "#f4ecd8", 3),
          ("label_bar_berry", "#6a2a5a", "#f4d8e8", "#f0b83a", 0), ("label_tube", "#d8d8dc", "#c82a2a", "#2a2a2e", 0),
          ("label_tube_green", "#d8dcd4", "#2a8a3a", "#2a2a2e", 1), ("label_tray", "#2e3a4a", "#e8c83a", "#d8dce0", 5),
          ("label_cup_noodle", "#d82a1a", "#f8e8a0", "#f4f4f4", 2), ("label_flask", "#2a3e4a", "#c8d0d6", "#e8a02a", 0)]
for _n, _bg, _fg, _ac, _k in LABELS:
    def _mk3(bg=_bg, fg=_fg, ac=_ac, k=_k):
        return lambda s: _label(s, bg, fg, ac, k)
    tex(_n, 0.45, 0.0)(_mk3())


@tex("cardboard_print", 0.85)
def _(s):
    return shade(ramp(noise(2.0, s, sx=4, sy=1), [(0, "#a07d4f"), (1, "#c09c68")]), noise(3, s + 1), 0.05)


# ---------------------------------------------------------------- output
def _to_uint8(arr):
    return (np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)


def save_jpg(path, arr, quality=82):
    """Write an (h, w, 3) float array in 0..1 as JPEG through Blender (no extra dependencies)."""
    import bpy
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w = arr.shape[:2]
    rgba = np.concatenate([arr, np.ones((h, w, 1))], axis=2)
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(np.clip(np.flipud(rgba), 0, 1).astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "JPEG"
    bpy.context.scene.render.image_settings.quality = quality
    img.save()
    bpy.data.images.remove(img)


def tex_path(tex_dir, name):
    return os.path.join(tex_dir, "food", name + ".jpg")


def missing(tex_dir):
    return [n for n in TEX if not os.path.exists(tex_path(tex_dir, n))]


def make_all(tex_dir, only=None):
    """Generate every food texture (deterministic: seed = crc of the name)."""
    import zlib
    for name, fn in TEX.items():
        if only and name not in only:
            continue
        save_jpg(tex_path(tex_dir, name), fn(zlib.crc32(name.encode()) % 10000))
