"""Procedural texture generation (numpy) written out through Blender's image API.

Produces
  * screens/*.png      - 256x256 emissive UI screens used by display models
  * surfaces/*_{albedo,normal,orm}.png - tileable PBR sets for the ship shell
  * sky/stars.png      - equirectangular starfield + nebula for the environment
  * sky/planet.png     - planet surface for the window view
"""
import math
import os

import numpy as np

S = 256


def save(path, arr):
    """Save float array (h, w, 3|4) in 0..1 as PNG using bpy."""
    import bpy
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w = arr.shape[:2]
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1), arr.dtype)], axis=2)
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=True, float_buffer=False)
    img.colorspace_settings.name = "sRGB"
    img.pixels.foreach_set(np.clip(np.flipud(arr), 0, 1).astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def save_data(path, arr):
    """Same as save but flags the image as Non-Color data (normal / ORM maps)."""
    import bpy
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w = arr.shape[:2]
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=False)
    img.colorspace_settings.name = "Non-Color"
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.ones((h, w, 1), arr.dtype)], axis=2)
    img.pixels.foreach_set(np.clip(np.flipud(arr), 0, 1).astype(np.float32).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


# ---------------------------------------------------------------- helpers
def fnoise(n, beta, rng, w=None):
    """Tileable 1/f^beta noise in 0..1 (n rows x w columns, w defaults to n)."""
    w = n if w is None else w
    fx, fy = np.meshgrid(np.fft.fftfreq(w), np.fft.fftfreq(n))
    r = np.sqrt(fx ** 2 + fy ** 2)
    r[0, 0] = 1
    spec = (np.random.default_rng(rng).normal(size=(n, w)) + 1j * np.random.default_rng(rng + 1).normal(size=(n, w))) / r ** beta
    spec[0, 0] = 0
    a = np.real(np.fft.ifft2(spec))
    a = (a - a.min()) / (a.max() - a.min() + 1e-9)
    return a


def normal_from_height(h, strength=2.0):
    gx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * strength
    gy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * strength
    nz = np.ones_like(h)
    ln = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    return np.stack([(-gx / ln) * .5 + .5, (gy / ln) * .5 + .5, nz / ln * .5 + .5], axis=2)


def _grid(n):
    y, x = np.mgrid[0:n, 0:n]
    return x / n, y / n


def _pack_orm(ao, rough, metal):
    return np.stack([ao, rough, metal], axis=2)


def _line(img, x0, y0, x1, y1, col, w=1):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for t in np.linspace(0, 1, n * 2):
        x = int(x0 + (x1 - x0) * t)
        y = int(y0 + (y1 - y0) * t)
        ya, yb = max(0, y - w // 2), min(S, y + w // 2 + 1)
        xa, xb = max(0, x - w // 2), min(S, x + w // 2 + 1)
        if ya < yb and xa < xb:
            img[ya:yb, xa:xb] = col


# ------------------------------------------------------------ surface maps
def _panels(n, cols, rows, seam=0.012):
    x, y = _grid(n)
    u = (x * cols) % 1
    v = (y * rows) % 1
    np.minimum(np.minimum(u, 1 - u) / (1.0 / cols), np.minimum(v, 1 - v) / (1.0 / rows))
    d = np.minimum(np.minimum(u, 1 - u) * cols, np.minimum(v, 1 - v) * rows)
    seam_mask = d < seam * 8
    idx = (np.floor(x * cols) + np.floor(y * rows) * cols).astype(int)
    return u, v, d, seam_mask, idx


def surf_hull_panel(n=512):
    u, v, d, seam, idx = _panels(n, 4, 4, 0.006)
    rng = np.random.default_rng(3)
    tone = rng.random(16)[idx % 16] * 0.12
    nz = fnoise(n, 1.8, 5)
    base = 0.62 + tone + (nz - .5) * 0.10
    h = np.where(seam, 0.0, 1.0) * 0.5 + nz * 0.03
    # rivets
    for cx in (0.1, 0.9):
        for cy in (0.1, 0.9):
            dd = np.hypot(((u - cx + .5) % 1) - .5, ((v - cy + .5) % 1) - .5) * 4
            h += np.exp(-(dd / 0.025) ** 2) * 0.35
    alb = np.stack([base * 0.86, base * 0.89, base * 0.94], axis=2)
    alb = np.where(seam[..., None], alb * 0.45, alb)
    orm = _pack_orm(np.where(seam, 0.55, 1.0), 0.42 + nz * 0.25, np.full_like(nz, 0.8))
    return alb, normal_from_height(h, 5.0), orm


def surf_deck_plate(n=512):
    x, y = _grid(n)
    # diamond tread plate
    u = (x * 16) % 1
    v = (y * 16) % 1
    diam = (np.abs(u - .5) + np.abs(v - .5)) < 0.28
    diam2 = (np.abs(((x * 16 + .5) % 1) - .5) + np.abs(((y * 16 + .5) % 1) - .5)) < 0.16
    h = diam * 0.5 + diam2 * 0.15
    _, _, d, seam, _ = _panels(n, 2, 2, 0.004)
    h = np.where(seam, -0.2, h)
    nz = fnoise(n, 1.6, 9)
    base = 0.46 + nz * 0.08
    alb = np.stack([base * .97, base * .98, base * 1.0], axis=2)
    alb = np.where(seam[..., None], alb * .5, alb)
    orm = _pack_orm(np.ones((n, n)), 0.5 + nz * 0.25, np.full((n, n), .85))
    return alb, normal_from_height(h, 3.0), orm


def surf_grating(n=512):
    x, y = _grid(n)
    u = (x * 12) % 1
    v = (y * 12) % 1
    bar = (u < .22) | (v < .22)
    h = bar * 1.0
    nz = fnoise(n, 1.5, 11)
    alb = np.stack([0.24 + nz * .05] * 3, axis=2) * np.array([.95, .97, 1.0])
    alb = np.where(bar[..., None], alb, alb * .25)
    orm = _pack_orm(np.where(bar, 1.0, .2), 0.5 + nz * .2, np.where(bar, .9, .3))
    return alb, normal_from_height(h.astype(float), 3.5), orm


def surf_ceiling(n=512):
    u, v, d, seam, idx = _panels(n, 2, 2, 0.004)
    nz = fnoise(n, 2.0, 13)
    perf = ((u * 24) % 1 - .5) ** 2 + ((v * 24) % 1 - .5) ** 2 < 0.03
    base = 0.6 + nz * 0.05
    alb = np.stack([base * .95, base * .97, base], axis=2)
    alb = np.where(perf[..., None], alb * .55, alb)
    alb = np.where(seam[..., None], alb * .5, alb)
    h = np.where(seam, 0, 0.6) - perf * 0.3
    orm = _pack_orm(np.where(perf | seam, .5, 1.0), 0.6 + nz * .2, np.full((n, n), .15))
    return alb, normal_from_height(h.astype(float), 3.0), orm


def surf_carpet(n=512):
    rng = np.random.default_rng(21)
    fine = rng.random((n, n))
    nz = fnoise(n, 1.0, 23)
    x, y = _grid(n)
    weave = (np.sin(x * 2 * math.pi * 64) * np.sin(y * 2 * math.pi * 64)) * .5 + .5
    base = 0.42 + fine * .10 + nz * .05 + weave * .04
    alb = np.stack([base * .95, base * .97, base * 1.03], axis=2)
    base = base * 1.0
    orm = _pack_orm(np.ones((n, n)) * .9, np.full((n, n), .97), np.zeros((n, n)))
    return alb, normal_from_height(fine * .4 + weave * .3, 1.5), orm


def surf_hull_dark(n=512):
    nz = fnoise(n, 1.7, 31)
    u, v, d, seam, idx = _panels(n, 8, 4, 0.005)
    base = 0.14 + nz * .08 + (np.random.default_rng(1).random(32)[idx % 32]) * .05
    alb = np.stack([base] * 3, axis=2) * np.array([.95, 1.0, 1.08])
    alb = np.where(seam[..., None], alb * .4, alb)
    h = np.where(seam, 0, .5) + nz * .05
    orm = _pack_orm(np.where(seam, .5, 1.0), 0.35 + nz * .3, np.full((n, n), .9))
    return alb, normal_from_height(h, 4.0), orm


def surf_wall_trim(n=512):
    """Wall with dado rail: lower half darker, upper half light; vertical panel seams."""
    x, y = _grid(n)
    nz = fnoise(n, 1.9, 41)
    u = (x * 4) % 1
    seam = np.minimum(u, 1 - u) < 0.006
    dado = (y > 0.5)
    band = (np.abs(y - .5) < 0.012) | (np.abs(y - .02) < .01)
    base = np.where(dado, 0.62, 0.86) + nz * .05
    alb = np.stack([base * .93, base * .96, base], axis=2)
    alb = np.where(seam[..., None], alb * .55, alb)
    alb = np.where(band[..., None], np.array([.85, .7, .25]), alb)
    h = np.where(seam, -.2, 0.) + band * .8 + nz * .04
    orm = _pack_orm(np.where(seam, .5, 1.0), 0.5 + nz * .2, np.where(band, .8, .1) * np.ones((n, n)))
    return alb, normal_from_height(h.astype(float), 3.0), orm


SURFACES = {
    "hull_panel": surf_hull_panel, "deck_plate": surf_deck_plate, "grating": surf_grating,
    "ceiling": surf_ceiling, "carpet": surf_carpet, "hull_dark": surf_hull_dark, "wall_trim": surf_wall_trim,
}


def make_surfaces(outdir, n=512):
    for name, fn in SURFACES.items():
        alb, nrm, orm = fn(n)
        save(os.path.join(outdir, "surfaces", name + "_albedo.png"), np.clip(alb, 0, 1))
        save_data(os.path.join(outdir, "surfaces", name + "_normal.png"), nrm)
        save_data(os.path.join(outdir, "surfaces", name + "_orm.png"), orm)


# ------------------------------------------------------------------- sky
def make_sky(outdir, w=2048, h=1024):
    rng = np.random.default_rng(7)
    img = np.zeros((h, w, 3), np.float32)
    # nebula
    a = fnoise(h, 2.4, 71, w)
    b = fnoise(h, 2.0, 73, w)
    neb = np.clip((a - .5) * 2.2, 0, 1) ** 1.5
    img += neb[..., None] * np.array([.10, .05, .22]) * (0.5 + b[..., None])
    img += np.clip((b - .55) * 2.5, 0, 1)[..., None] ** 2 * np.array([.20, .06, .10]) * 0.5
    # stars - denser near the galactic band
    yy = np.arange(h)[:, None] / h
    band = np.exp(-((yy - .5) / .12) ** 2)
    for cnt, mag in ((9000, .35), (2600, .7), (500, 1.0), (60, 1.6)):
        xs = rng.integers(0, w, cnt)
        # uniform on the sphere: sin(latitude) is uniform; row = (0.5 - lat/pi) * h
        lat = np.arcsin(rng.uniform(-1, 1, cnt))
        ys = np.clip(((.5 - lat / np.pi) * h).astype(int), 0, h - 1)
        col = rng.choice([0, 1, 2], cnt, p=[.5, .35, .15])
        tint = np.array([[1, .95, .9], [.85, .92, 1], [1, .8, .6]])[col]
        for x0, y0, t in zip(xs, ys, tint):
            img[y0, x0] += t * mag * rng.uniform(.4, 1.0)
            if mag >= 1.0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    img[(y0 + dy) % h, (x0 + dx) % w] += t * mag * .25
    img += band[..., None] * 0.02
    save(os.path.join(outdir, "sky", "stars.png"), np.clip(img ** 0.8, 0, 1))
    # planet
    n = 512
    p = fnoise(n, 2.2, 91)
    q = fnoise(n, 1.4, 93)
    y, x = np.mgrid[0:n, 0:n] / n
    lat = np.abs(y - .5) * 2
    ocean = (p < .52)
    land = np.stack([.25 + q * .25, .35 + q * .2, np.full_like(q, .12)], axis=2)
    sea = np.stack([np.full_like(p, .03), .18 + p * .2, .42 + p * .2], axis=2)
    surf = np.where(ocean[..., None], sea, land)
    surf = np.where((lat > .82)[..., None], np.array([.9, .93, .97]), surf)
    cl = np.clip((fnoise(n, 2.6, 95) - .5) * 3, 0, 1)
    surf = surf * (1 - cl[..., None] * .8) + cl[..., None] * .8
    save(os.path.join(outdir, "sky", "planet.png"), np.clip(surf, 0, 1))


# --------------------------------------------------------------- screens
def _canvas(bg=(.02, .05, .08)):
    return np.ones((S, S, 3), np.float32) * np.array(bg, np.float32)


def _grid_lines(img, col, step=32, a=.25):
    img[::step, :] = img[::step, :] * (1 - a) + np.array(col) * a
    img[:, ::step] = img[:, ::step] * (1 - a) + np.array(col) * a


def _circle(img, cx, cy, r, col, w=2):
    y, x = np.mgrid[0:S, 0:S]
    d = np.hypot(x - cx, y - cy)
    m = np.abs(d - r) < w / 2 + .5
    img[m] = col


def _fill_circle(img, cx, cy, r, col):
    y, x = np.mgrid[0:S, 0:S]
    img[np.hypot(x - cx, y - cy) < r] = col


def _rect(img, x0, y0, x1, y1, col):
    img[int(y0):int(y1), int(x0):int(x1)] = col


def _text_lines(img, x0, y0, rows, width, col, rng, lh=9):
    for r in range(rows):
        w = int(width * rng.uniform(.3, 1.0))
        _rect(img, x0, y0 + r * lh, x0 + w, y0 + r * lh + 3, col)


def _header(img, col, txt_w=90):
    _rect(img, 0, 0, S, 16, np.array(col) * .35)
    _rect(img, 6, 5, 6 + txt_w, 10, col)
    _rect(img, S - 30, 5, S - 8, 10, col)


def scr_radar(rng):
    img = _canvas((.01, .05, .03)); c = (.2, 1., .45)
    for r in (30, 60, 90, 118):
        _circle(img, 128, 132, r, np.array(c) * .5)
    _line(img, 10, 132, 246, 132, np.array(c) * .4); _line(img, 128, 14, 128, 250, np.array(c) * .4)
    a = 0.9
    for t in np.linspace(0, 1, 60):
        aa = a - t * .9
        _line(img, 128, 132, 128 + 118 * math.cos(aa), 132 - 118 * math.sin(aa), np.array(c) * (1 - t) * .8)
    for _ in range(7):
        r = rng.uniform(15, 105); th = rng.uniform(0, 6.28)
        _fill_circle(img, 128 + r * math.cos(th), 132 - r * math.sin(th), 3, (1, 1, .6))
    _header(img, c); return img


def scr_waveform(rng):
    img = _canvas((.02, .03, .06)); c = (.3, .9, 1.)
    _grid_lines(img, c, 32, .18)
    for k, col in enumerate((c, (1, .5, .2))):
        ph = rng.uniform(0, 6); fr = rng.uniform(2, 5) + k
        xs = np.arange(S)
        ys = (128 + math.sin(0) + np.sin(xs / S * fr * 6.28 + ph) * (50 - 12 * k) * (0.6 + 0.4 * np.sin(xs / 37.))).astype(int)
        for x, y in zip(xs, ys):
            img[max(0, y - 1):y + 2, x] = col
    _header(img, c); return img


def scr_graph(rng):
    img = _canvas((.03, .03, .05)); c = (1., .75, .2)
    _grid_lines(img, c, 32, .15)
    for i in range(12):
        hgt = rng.uniform(20, 170)
        col = c if hgt < 130 else (1, .3, .2)
        _rect(img, 20 + i * 18, 230 - hgt, 32 + i * 18, 230, col)
    _header(img, c); return img


def scr_text(rng):
    img = _canvas((.01, .03, .05)); c = (.4, .85, 1.)
    _header(img, c)
    for blk in range(3):
        _text_lines(img, 12, 28 + blk * 76, 6, 200, np.array(c) * .8, rng)
    return img


def scr_starmap(rng):
    img = _canvas((.01, .01, .04)); c = (.6, .7, 1.)
    pts = []
    for _ in range(40):
        p = (rng.uniform(10, 246), rng.uniform(24, 246)); pts.append(p)
        _fill_circle(img, p[0], p[1], rng.choice([1.5, 2, 3]), (1, .95, .8))
    for i in range(0, 38, 2):
        _line(img, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], np.array(c) * .5)
    _circle(img, *pts[0], 9, (1, .4, .2)); _header(img, c); return img


def scr_schematic(rng):
    img = _canvas((.01, .04, .08)); c = (.3, .8, 1.)
    _grid_lines(img, c, 16, .1)
    _rect(img, 40, 100, 216, 150, np.array(c) * .25)
    for x in (40, 216):
        _line(img, x, 100, x, 150, c, 2)
    _line(img, 40, 100, 216, 100, c, 2); _line(img, 40, 150, 216, 150, c, 2)
    for i in range(5):
        _rect(img, 60 + i * 32, 70, 80 + i * 32, 100, np.array(c) * .6)
        _rect(img, 60 + i * 32, 150, 80 + i * 32, 180, np.array(c) * .6)
    _line(img, 216, 125, 245, 110, c, 2); _line(img, 216, 125, 245, 140, c, 2)
    _header(img, c); return img


def scr_bars(rng):
    img = _canvas((.02, .04, .03)); c = (.3, 1., .5)
    for i in range(7):
        _rect(img, 20, 30 + i * 30, 236, 44 + i * 30, np.array(c) * .15)
        _rect(img, 20, 30 + i * 30, 20 + rng.uniform(.2, 1) * 216, 44 + i * 30, c if i % 3 else (1, .6, .2))
    _header(img, c); return img


def scr_warp(rng):
    img = _canvas((.02, .01, .06)); c = (.7, .4, 1.)
    for r in range(8, 122, 10):
        _circle(img, 128, 132, r, np.array(c) * (1 - r / 140), 2)
    for k in range(24):
        th = k / 24 * 6.28
        _line(img, 128 + 10 * math.cos(th), 132 + 10 * math.sin(th), 128 + 118 * math.cos(th), 132 + 118 * math.sin(th), np.array(c) * .3)
    _fill_circle(img, 128, 132, 8, (1, .9, 1)); _header(img, c); return img


def scr_vitals(rng):
    img = _canvas((.01, .04, .04)); c = (.3, 1., .9)
    _grid_lines(img, c, 32, .12)
    for row in range(3):
        y0 = 40 + row * 70
        xs = np.arange(20, 236)
        beat = np.where((xs % 54) < 6, -28 * np.sin((xs % 54) / 6 * 3.14), 0) + np.sin(xs / 8.) * 2
        for x, b in zip(xs, beat):
            img[int(y0 + 25 + b) - 1:int(y0 + 25 + b) + 1, x] = c if row != 1 else (1, .4, .4)
    _header(img, c); return img


def scr_power(rng):
    img = _canvas((.04, .02, .01)); c = (1., .55, .15)
    for i in range(4):
        cx = 60 + (i % 2) * 130; cy = 80 + (i // 2) * 100
        _circle(img, cx, cy, 36, np.array(c) * .6, 3)
        a = rng.uniform(.5, 2.6)
        _line(img, cx, cy, cx - 30 * math.cos(a), cy - 30 * math.sin(a), c, 2)
    _header(img, c); return img


def scr_nav(rng):
    img = _canvas((.01, .02, .05)); c = (.4, .9, 1.)
    _grid_lines(img, c, 32, .2)
    pts = [(30, 220), (80, 170), (120, 180), (170, 110), (225, 60)]
    for a, b in zip(pts[:-1], pts[1:]):
        _line(img, *a, *b, c, 2)
    for p in pts:
        _fill_circle(img, *p, 5, (1, 1, 1))
    _circle(img, 225, 60, 14, (1, .5, .2)); _header(img, c); return img


def scr_alert(rng):
    img = _canvas((.15, .01, .01)); c = (1., .2, .15)
    for i in range(0, S, 32):
        _line(img, i, 0, i + 90, S, np.array(c) * .35, 10)
    _rect(img, 40, 90, 216, 170, (.05, 0, 0))
    _rect(img, 40, 90, 216, 96, c); _rect(img, 40, 164, 216, 170, c)
    _text_lines(img, 56, 108, 4, 140, c, rng, 13); return img


def scr_tactical(rng):
    img = _canvas((.03, .01, .01)); c = (1., .35, .25)
    _grid_lines(img, c, 32, .16)
    _fill_circle(img, 128, 132, 9, (.3, .8, 1))
    for _ in range(5):
        th = rng.uniform(0, 6.28); r = rng.uniform(35, 105)
        x, y = 128 + r * math.cos(th), 132 + r * math.sin(th)
        _line(img, x - 6, y - 6, x + 6, y + 6, c, 2); _line(img, x - 6, y + 6, x + 6, y - 6, c, 2)
    _circle(img, 128, 132, 100, np.array(c) * .5); _header(img, c); return img


def scr_systems(rng):
    img = _canvas((.02, .03, .04)); c = (.6, .85, 1.)
    for r in range(6):
        for cl in range(4):
            on = rng.random() > .25
            _rect(img, 14 + cl * 60, 26 + r * 36, 68 + cl * 60, 54 + r * 36, (.15, .7, .3) if on else (.8, .2, .2))
            _rect(img, 18 + cl * 60, 34 + r * 36, 18 + cl * 60 + rng.uniform(10, 40), 38 + r * 36, (0, 0, 0))
    _header(img, c); return img


def scr_lifesigns(rng):
    img = _canvas((.01, .04, .03)); c = (.4, 1., .7)
    for i in range(6):
        cx = 45 + (i % 3) * 82; cy = 80 + (i // 3) * 100
        _circle(img, cx, cy, 26, c, 2)
        _rect(img, cx - 20, cy + 32, cx + 20, cy + 36, np.array(c) * .4)
        _rect(img, cx - 20, cy + 32, cx - 20 + rng.uniform(10, 40), cy + 36, c)
    _header(img, c); return img


def scr_comm(rng):
    img = _canvas((.02, .02, .05)); c = (.5, .8, 1.)
    _fill_circle(img, 128, 100, 45, np.array(c) * .15); _circle(img, 128, 100, 45, c, 2)
    _rect(img, 100, 150, 156, 190, np.array(c) * .25)
    for i in range(24):
        h = rng.uniform(4, 30); _rect(img, 20 + i * 9, 236 - h, 26 + i * 9, 236, c)
    _header(img, c); return img


def scr_medical(rng):
    img = _canvas((.02, .04, .05)); c = (.5, 1., 1.)
    _header(img, c)
    _rect(img, 100, 40, 156, 200, np.array(c) * .12)
    _fill_circle(img, 128, 60, 14, np.array(c) * .5)
    _rect(img, 118, 76, 138, 150, np.array(c) * .5)
    for y in (90, 120, 150):
        _line(img, 60, y, 100, y, c); _line(img, 156, y, 196, y, c)
    _text_lines(img, 14, 210, 3, 100, c, rng); return img


def scr_periodic(rng):
    img = _canvas((.02, .02, .03)); c = (1., .8, .3)
    for r in range(6):
        for cl in range(9):
            if rng.random() > .12:
                _rect(img, 8 + cl * 27, 24 + r * 36, 32 + cl * 27, 54 + r * 36, np.array(c) * rng.uniform(.25, .9))
    _header(img, c); return img


def scr_hazard(rng):
    img = _canvas((.06, .05, 0)); c = (1., .85, .1)
    for i in range(-S, S * 2, 40):
        _line(img, i, 0, i + S, S, c, 16)
    _rect(img, 30, 96, 226, 160, (.02, .02, .0))
    _text_lines(img, 44, 108, 3, 160, c, rng, 16); return img


def scr_diagnostic(rng):
    img = _canvas((.02, .03, .03)); c = (.5, 1., .6)
    _text_lines(img, 10, 26, 22, 230, np.array(c) * .8, rng, 10)
    _rect(img, 8, 246, 8 + rng.uniform(60, 240), 250, c); _header(img, c); return img


def scr_globe(rng):
    img = _canvas((.01, .02, .05)); c = (.3, .8, 1.)
    _circle(img, 128, 128, 100, c, 2)
    for k in range(-3, 4):
        _circle(img, 128, 128, 100 - abs(k) * 4, np.array(c) * .3)
        _line(img, 28, 128 + k * 26, 228, 128 + k * 26, np.array(c) * .3)
    _header(img, c); return img


SCREENS = {
    "radar": scr_radar, "waveform": scr_waveform, "graph": scr_graph, "text": scr_text,
    "starmap": scr_starmap, "schematic": scr_schematic, "bars": scr_bars, "warp": scr_warp,
    "vitals": scr_vitals, "power": scr_power, "nav": scr_nav, "alert": scr_alert,
    "tactical": scr_tactical, "systems": scr_systems, "lifesigns": scr_lifesigns, "comm": scr_comm,
    "medical": scr_medical, "periodic": scr_periodic, "hazard": scr_hazard, "diagnostic": scr_diagnostic,
    "globe": scr_globe,
}


def make_screens(outdir):
    for i, (name, fn) in enumerate(SCREENS.items()):
        rng = np.random.default_rng(100 + i)
        img = fn(rng)
        # cheap CRT look: alternating scanline dimming, then posterise so the PNGs stay small
        img = img * (0.9 + 0.1 * (np.arange(S)[:, None, None] % 2))
        img = np.round(np.clip(img, 0, 1) * 15) / 15
        save(os.path.join(outdir, "screens", name + ".png"), img)
