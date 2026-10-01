"""Shared building blocks for the extended texture generators (numpy, tileable by construction).

Everything here is deterministic (seeded) and *band-limited*: noise is generated in the frequency domain with a
hard-ish cut-off, pattern masks come from distance fields with a soft edge of >= 1.5 px, and `finish()` low-passes
height / roughness / albedo and bakes normal variance into roughness (Toksvig).  That removes the detail a
mip-mapped, anisotropic sampler could not resolve at ~1 m viewing distance, which is what makes textures shimmer.

bpy is used for what it is good at: image datablocks, colour management (sRGB vs Non-Color) and PNG encoding.
"""
import os
import re

import numpy as np

_K_CACHE = {}


def _freqs(n):
    f = np.fft.fftfreq(n)
    return f[None, :], f[:, None]


def hexc(h):
    """'#rrggbb' -> (r, g, b) floats in 0..1 (sRGB values, as stored in the albedo PNGs)."""
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _gauss_kernel(n, sx, sy):
    key = (n, round(sx, 3), round(sy, 3))
    if key not in _K_CACHE:
        fx, fy = _freqs(n)
        _K_CACHE[key] = np.exp(-2 * np.pi ** 2 * ((sx * fx) ** 2 + (sy * fy) ** 2)).astype(np.float32)
    return _K_CACHE[key]


def blur(a, sigma, sigma_y=None):
    """Tileable gaussian blur (sigma in pixels) of an (n, n) or (n, n, c) array."""
    if sigma <= 0 and (sigma_y is None or sigma_y <= 0):
        return a
    sy = sigma if sigma_y is None else sigma_y
    n = a.shape[0]
    k = _gauss_kernel(n, sigma, sy)
    if a.ndim == 3:
        k = k[..., None]
    return np.real(np.fft.ifft2(np.fft.fft2(a, axes=(0, 1)) * k, axes=(0, 1))).astype(np.float32)


def zscore(a):
    return ((a - a.mean()) / (a.std() + 1e-9)).astype(np.float32)


def noise(n, seed, beta=2.0, fmin=0.0, fmax=0.2):
    """Tileable 1/f^beta noise as z-score, spectrum limited to [fmin, fmax] cycles/pixel (smooth roll-off)."""
    rng = np.random.default_rng(seed)
    fx, fy = _freqs(n)
    r = np.sqrt(fx ** 2 + fy ** 2)
    r[0, 0] = 1
    spec = (rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))) / r ** beta
    spec *= np.exp(-(r / fmax) ** 4)
    if fmin > 0:
        spec *= 1 - np.exp(-(r / fmin) ** 2)
    spec[0, 0] = 0
    return zscore(np.real(np.fft.ifft2(spec)))


def streaks(n, seed, length=40.0, width=0.9, vertical=False):
    """Anisotropic noise (brushing / wood fibres): `length` px along the stroke, `width` px across it."""
    rng = np.random.default_rng(seed)
    w = rng.normal(size=(n, n)).astype(np.float32)
    a = blur(w, width, length) if vertical else blur(w, length, width)
    return zscore(a)


def coords(n):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32)
    return x + 0.5, y + 0.5


def soft(d, w=1.5):
    """Smooth 0..1 mask from a signed distance in pixels (positive = inside), edge width w px."""
    t = np.clip(d / w + 0.5, 0, 1)
    return (t * t * (3 - 2 * t)).astype(np.float32)


def periodic_dist(p, period):
    """Distance (same unit as p) to the nearest multiple of period."""
    m = np.mod(p, period)
    return np.minimum(m, period - m)


def voronoi(n, cells, seed, jitter=0.9):
    """Tileable worley noise.  Returns (f1, f2, cell_id) with distances in cell units, id in 0..cells^2-1."""
    rng = np.random.default_rng(seed)
    px = rng.uniform(0.5 - jitter / 2, 0.5 + jitter / 2, (cells, cells)).astype(np.float32)
    py = rng.uniform(0.5 - jitter / 2, 0.5 + jitter / 2, (cells, cells)).astype(np.float32)
    x, y = coords(n)
    u = x / n * cells
    v = y / n * cells
    ci = np.floor(u).astype(int)
    cj = np.floor(v).astype(int)
    f1 = np.full((n, n), 9.0, np.float32)
    f2 = np.full((n, n), 9.0, np.float32)
    cid = np.zeros((n, n), int)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            gi, gj = ci + di, cj + dj
            wi, wj = gi % cells, gj % cells
            d = np.hypot(u - (gi + px[wj, wi]), v - (gj + py[wj, wi]))
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, wj * cells + wi, cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def rand_by_id(cid, seed, lo=0.0, hi=1.0, count=None):
    rng = np.random.default_rng(seed)
    count = count or int(cid.max()) + 1
    return (lo + (hi - lo) * rng.random(count)).astype(np.float32)[cid]


def hex_cells(n, cols, seed=0):
    """Tileable hexagonal cells (`cols` across).  Returns (edge_px, cell_id, lu, lv): distance to the nearest cell
    edge in pixels, a per-cell integer id and the local coordinates (in cell units, centre = 0)."""
    sv = np.sqrt(3.0)
    rows = max(1, int(round(cols / sv)))          # lattice rows per tile (vertical period = rows * sqrt(3))
    x, y = coords(n)
    u = x / n * cols
    v = y / n * rows * sv
    cands = []
    for lat, (ox, oy) in enumerate(((0.0, 0.0), (0.5, sv / 2))):
        i0 = np.round(u - ox)
        j0 = np.round((v - oy) / sv)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                ii, jj = i0 + di, j0 + dj
                cu, cv = ii + ox, jj * sv + oy
                d = np.hypot(u - cu, v - cv)
                cid = (np.mod(ii, cols) * 131 + np.mod(jj, rows) * 7 + lat * 3).astype(int)
                cands.append((d, cid, u - cu, v - cv))
    ds = np.stack([c[0] for c in cands])
    order = np.argsort(ds, axis=0)
    d1 = np.take_along_axis(ds, order[:1], 0)[0]
    d2 = np.take_along_axis(ds, order[1:2], 0)[0]
    pick = lambda k: np.take_along_axis(np.stack([c[k] for c in cands]), order[:1], 0)[0]
    edge = (d2 - d1) * 0.5 * n / cols
    return edge.astype(np.float32), pick(1), pick(2).astype(np.float32), pick(3).astype(np.float32)


def slope_limit(g, gmax=1.2):
    return g / np.sqrt(1.0 + (g / gmax) ** 2)


def normal_map(h, strength=1.0, gmax=1.0):
    """OpenGL-style tangent-space normal from a height field (units: 1.0 height = `strength` px rise per px)."""
    gx = slope_limit((np.roll(h, -1, 1) - np.roll(h, 1, 1)) * 0.5 * strength, gmax)
    gy = slope_limit((np.roll(h, -1, 0) - np.roll(h, 1, 0)) * 0.5 * strength, gmax)
    ln = np.sqrt(gx ** 2 + gy ** 2 + 1.0)
    return np.stack([-gx / ln * 0.5 + 0.5, gy / ln * 0.5 + 0.5, 1.0 / ln * 0.5 + 0.5], axis=2).astype(np.float32), gx, gy


def finish(alb, h=None, rough=0.5, ao=None, metal=0.0, nstr=2.0, hblur=0.9, rblur=1.3, ablur=0.5, toksvig=1.0,
           gmax=0.8, rough_range=(0.06, 1.0)):
    """Band-limit and pack one surface: returns (albedo, normal, orm) float arrays in 0..1.

    h       height field (any scale; it is normalised so nstr is 'pixels of rise per pixel of travel' at +-1 sigma)
    nstr    normal strength; keep <= ~3 for tiles that are minified a lot
    toksvig bake local slope variance into roughness (specular anti-aliasing)
    """
    n = alb.shape[0]
    alb = blur(alb, ablur) if ablur > 0 else alb
    if h is None:
        h = np.zeros((n, n), np.float32)
    h = blur(h.astype(np.float32), hblur)
    h = h / (h.std() + 1e-6) * 0.5 if h.std() > 1e-6 else h
    nrm, gx, gy = normal_map(h, nstr, gmax)
    rough = np.broadcast_to(np.asarray(rough, np.float32), (n, n)).astype(np.float32)
    if toksvig > 0:
        var = blur(gx * gx + gy * gy, 2.5)
        rough = np.sqrt(rough ** 2 + toksvig * var * 0.5)
    rough = np.clip(blur(rough, rblur), *rough_range)
    ao = np.ones((n, n), np.float32) if ao is None else np.clip(blur(np.broadcast_to(ao, (n, n)).astype(np.float32), 0.8), 0, 1)
    metal = np.clip(blur(np.broadcast_to(np.asarray(metal, np.float32), (n, n)).astype(np.float32), 1.0), 0, 1)
    return np.clip(alb, 0, 1).astype(np.float32), nrm, np.stack([ao, rough, metal], axis=2).astype(np.float32)


def prefilter_existing(alb, nrm, orm):
    """Band-limit the older hand-written surface sets in place of regenerating them: low-pass albedo, soften and
    renormalise the normal map, bake the lost normal variance into roughness."""
    alb = np.clip(blur(alb.astype(np.float32), 0.6), 0, 1)
    v = nrm.astype(np.float32) * 2 - 1
    vb = blur(v, 0.8)
    var = np.clip(1 - np.linalg.norm(vb, axis=2) / np.maximum(np.linalg.norm(v, axis=2), 1e-3), 0, 1)
    vb = vb / np.maximum(np.linalg.norm(vb, axis=2, keepdims=True), 1e-4)
    vb[..., 2] = np.maximum(vb[..., 2], 0.05)
    vb = vb / np.linalg.norm(vb, axis=2, keepdims=True)
    nrm2 = vb * 0.5 + 0.5
    orm = orm.astype(np.float32).copy()
    orm[..., 1] = np.clip(blur(orm[..., 1], 1.2) + blur(np.abs(v[..., 0]) + np.abs(v[..., 1]), 2.0) * 0.15, 0.06, 1)
    orm[..., 0] = blur(orm[..., 0], 0.8)
    orm[..., 2] = blur(orm[..., 2], 1.0)
    del var
    return alb, nrm2.astype(np.float32), orm


# ------------------------------------------------------------------ png output through bpy
_SCENE = {}


def _scene():
    import bpy
    if "s" not in _SCENE:
        _SCENE["s"] = bpy.data.scenes.new("tex_out")
    return _SCENE["s"]


def write_png(path, arr, data=False, quant_bits=8):
    """Write an (h, w, 3) float image (0..1, top row first) as an 8-bit, maximum-compression PNG with bpy.
    data=True stores the image as Non-Color (normal / ORM) - the bytes are identical, only the metadata differs."""
    import bpy
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w = arr.shape[:2]
    a = np.clip(arr, 0, 1)
    if quant_bits < 8:
        q = 2 ** quant_bits - 1
        a = np.round(a * q) / q
    if a.shape[2] == 3:
        a = np.concatenate([a, np.ones((h, w, 1), a.dtype)], axis=2)
        mode = "RGB"
    else:
        mode = "RGBA"
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=(mode == "RGBA"), float_buffer=False)
    img.colorspace_settings.name = "Non-Color" if data else "sRGB"
    img.pixels.foreach_set(np.flipud(a).astype(np.float32).ravel())
    sc = _scene()
    s = sc.render.image_settings
    s.file_format = "PNG"
    s.color_mode = mode
    s.color_depth = "8"
    s.compression = 100
    sc.view_settings.view_transform = "Raw" if data else "Standard"
    sc.view_settings.look = "None"
    img.save_render(path, scene=sc)
    bpy.data.images.remove(img)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
