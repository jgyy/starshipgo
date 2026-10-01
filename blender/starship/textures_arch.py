"""Textures for the architectural assets (stairs, exterior hull plating).

Same conventions as textures.py: <name>_{albedo,normal,orm}.png, ORM = (ao, roughness, metallic),
tileable, fully deterministic (fixed numpy seeds).

    hull_plate          1024  exterior armour, meant for 4 m world-space tiling (256 px / m)
    stair_tread         512   diamond anti-slip plate, 0.5 m tile, worn
    stair_riser         512   painted steel riser, tile = 0.7 m wide x 0.18 m (one riser) tall,
                              hazard band along the top edge
    hull_window_frame   512   dark anodised frame section
"""
import math
import os

import numpy as np

from .textures import fnoise, normal_from_height, _pack_orm, save, save_data


def _blur(a, k):
    """Tileable separable box blur, radius k (px)."""
    if k <= 0:
        return a
    out = a.copy()
    for ax in (0, 1):
        acc = np.zeros_like(out)
        for s in range(-k, k + 1):
            acc += np.roll(out, s, ax)
        out = acc / (2 * k + 1)
    return out


def _streaks(n, seed, freq=10):
    """Vertical dirt streaks (tileable): 1D noise per column, stretched in y, modulated."""
    np.random.default_rng(seed)
    cols = fnoise(n, 1.4, seed)[0]          # (n,) tileable along x
    cols = (cols - cols.min()) / (cols.max() - cols.min() + 1e-9)
    drip = fnoise(n, 2.4, seed + 7)
    # stretch: only low frequencies along y
    f = np.fft.fft(drip, axis=0)
    f[n // 40:-n // 40 or None, :] = 0
    drip = np.real(np.fft.ifft(f, axis=0))
    drip = (drip - drip.min()) / (drip.max() - drip.min() + 1e-9)
    return np.clip(cols[None, :] * 1.2 * drip, 0, 1)


# 5x7 pixel stencil font (digits and a few letters) -> grooves
_FONT = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
}


def _stencil(mask, text, x0, y0, scale):
    """Stamp `text` into bool `mask` at (x0, y0) px, glyph pixel = scale px."""
    n = mask.shape[0]
    cx = x0
    for ch in text:
        g = _FONT.get(ch)
        if g is None:
            cx += 4 * scale
            continue
        for gy, row in enumerate(g):
            for gx, c in enumerate(row):
                if c == "1":
                    ys = (y0 + gy * scale) % n
                    xs = (cx + gx * scale) % n
                    mask[ys:ys + scale, xs:xs + scale] = True
        cx += 6 * scale
    return mask


def surf_hull_plate(n=1024):
    Y, X = np.mgrid[0:n, 0:n]
    pw = n // 2                      # panel = 2 m x 2 m  (512 px)
    row = Y // pw
    Xs = (X + row * (pw // 2)) % n   # brick offset, still tileable (2 rows)
    col = Xs // pw
    u = Xs % pw
    v = Y % pw
    pid = row * 2 + col
    d = np.minimum(np.minimum(u, pw - 1 - u), np.minimum(v, pw - 1 - v)).astype(float)

    rng = np.random.default_rng(11)
    tone = (rng.random(4) - 0.5) * 0.16
    warm = (rng.random(4) - 0.5) * 0.06
    t = tone[pid]
    w = warm[pid]

    nz_f = fnoise(n, 2.2, 21)
    nz_m = fnoise(n, 1.3, 23)
    grain = fnoise(n, 0.6, 29)

    # ---- height map --------------------------------------------------------
    h = 0.0 * d
    # raised plate field with bevelled lip, groove at the seam
    h += np.clip(d / 6.0, 0, 1) * 0.55
    h -= (d < 3) * 0.35
    h += nz_m * 0.05 + grain * 0.012
    # rivet rows 14 px inside each edge, every 32 px
    def rivets(a, b):  # a along edge, b distance from edge
        da = ((a - 16) % 32) - 16
        return np.exp(-((da ** 2 + (b - 15) ** 2) / 26.0))
    riv = (rivets(u, v) + rivets(u, pw - 1 - v) + rivets(v, u) + rivets(v, pw - 1 - u))
    riv = np.clip(riv, 0, 1)
    h += riv * 0.6
    # weld seams on alternate edges: rippled bead centred on the seam (only the horizontal seam)
    weld_mask = (np.abs(v - 0) < 9) | (np.abs(v - (pw - 1)) < 9)
    weld_mask = weld_mask & ((pid % 2) == 0)
    dv = np.minimum(v, pw - 1 - v)
    bead = np.exp(-(dv / 5.0) ** 2) * (0.5 + 0.5 * np.sin(u * 0.9 + (v * 0.2)))
    h += np.where(weld_mask, bead * 0.45, 0)
    # stencil grooves (panel id + hazard-ish marks)
    st = np.zeros((n, n), bool)
    labels = ["A-01", "A-02", "C-14", "H-07"]
    for i, (r0, c0) in enumerate(((0, 0), (0, 1), (1, 0), (1, 1))):
        ox = (c0 * pw - r0 * (pw // 2)) % n
        oy = r0 * pw
        _stencil(st, labels[i], ox + 70, oy + 380, 5)
        _stencil(st, "D" + str(i + 1) + "-" + str(3 + i * 2), ox + 300, oy + 70, 3)
    # soften
    stf = _blur(st.astype(float), 1)
    h -= stf * 0.45
    # dents / scratches
    sc = fnoise(n, 0.9, 41)
    h += (sc > 0.93) * (sc - 0.93) * 1.5

    # ---- weathering --------------------------------------------------------
    streak = _streaks(n, 51)
    scorch_src = _blur(fnoise(n, 2.0, 61), 3)
    scorch = np.clip((scorch_src - 0.70) * 4.0, 0, 1) * 0.6
    edge_dirt = np.clip(1 - d / 26.0, 0, 1) * (0.4 + nz_f)
    dirt = np.clip(streak * 0.55 + edge_dirt * 0.35 + (nz_f - 0.5) * 0.3, 0, 1)
    rust = np.clip((fnoise(n, 2.0, 71) - 0.72) * 4.0, 0, 1) * np.clip(edge_dirt * 1.5, 0, 1)

    base = 0.50 + t + (nz_m - 0.5) * 0.08 + (grain - .5) * 0.04
    R = base * 0.78 + w * 0.5
    G = base * 0.82
    B = base * 0.90 - w * 0.5
    alb = np.stack([R, G, B], axis=2)
    # paint stencil (pale)
    alb = np.where(stf[..., None] > 0.3, alb * 0.3 + np.array([0.62, 0.62, 0.56]) * 0.7, alb)
    alb *= (1 - dirt[..., None] * 0.45)
    alb = alb * (1 - scorch[..., None] * 0.65) + np.array([0.05, 0.035, 0.03]) * scorch[..., None] * 0.65
    alb = alb * (1 - rust[..., None] * 0.6) + np.array([0.36, 0.17, 0.07]) * rust[..., None] * 0.6
    alb = np.where((d < 3)[..., None], alb * 0.5, alb)
    alb = np.where((riv > 0.35)[..., None], alb * 1.45 + 0.05, alb)

    rough = 0.42 + dirt * 0.3 + scorch * 0.2 + grain * 0.1 + rust * 0.2
    metal = np.clip(0.85 - dirt * 0.25 - rust * 0.5 - scorch * 0.2, 0.1, 1)
    ao = np.clip(1 - (d < 5) * 0.5 - riv * 0.0 - dirt * 0.15, 0, 1)
    return np.clip(alb, 0, 1), normal_from_height(h, 9.0), _pack_orm(ao, np.clip(rough, 0, 1), metal)


def surf_stair_tread(n=512):
    Y, X = np.mgrid[0:n, 0:n]
    x = X / n
    y = Y / n
    k = 10   # 10 diamonds per 0.5 m tile -> 5 cm pitch
    # alternating-orientation lozenges (classic tread plate): elongated diamonds at +-45 deg
    u = (x * k) % 1
    v = (y * k) % 1
    cellx = np.floor(x * k).astype(int)
    celly = np.floor(y * k).astype(int)
    flip = ((cellx + celly) % 2) == 0
    uu = np.where(flip, u, 1 - u)
    # bar along the diagonal u==v: distance across and along
    a = (uu - v) / math.sqrt(2)
    b = (uu + v - 1) / math.sqrt(2)
    bar = (np.abs(a) < 0.11) & (np.abs(b) < 0.46)
    prof = np.clip(1 - np.abs(a) / 0.11, 0, 1) ** 0.5 * np.clip(1 - np.abs(b) / 0.46, 0, 1) ** 0.4
    h = np.where(bar, 0.45 + prof * 0.35, 0.0)
    h = _blur(h, 1)
    wear = _blur(fnoise(n, 2.4, 81), 3)
    wear = np.clip((wear - 0.45) * 2.5, 0, 1)
    scr = fnoise(n, 0.9, 83)
    h -= wear * 0.25 * (h > 0.3)
    base = 0.52 + fnoise(n, 1.5, 85) * 0.08
    tip = np.clip(h, 0, 1)
    shade = base * (0.75 + 0.45 * tip) + wear * 0.12
    # grime in the valleys
    shade = shade * (1 - (h < 0.1) * 0.25)
    alb = np.stack([shade * 0.93, shade * 0.95, shade * 1.0], axis=2)
    rough = 0.48 - wear * 0.22 + (scr > 0.9) * 0.1 + (h < 0.1) * 0.3
    metal = np.clip(0.8 + wear * 0.15 - (h < 0.1) * 0.3, 0, 1)
    ao = np.clip(0.55 + 0.45 * tip, 0, 1)
    return np.clip(alb, 0, 1), normal_from_height(h, 4.0), _pack_orm(ao, np.clip(rough, 0, 1), metal)


def surf_stair_riser(n=512):
    """Riser: 0.7 m wide x 0.18 m tall in the U/V tile (non-square texel, see module docstring)."""
    Y, X = np.mgrid[0:n, 0:n]
    u = X / n            # 0..1 -> 0.7 m
    v = 1 - Y / n        # 0 bottom .. 1 top of the riser -> 0.18 m   (image row 0 is the top)
    mx = u * 0.70
    my = v * 0.18
    paint = np.array([0.16, 0.22, 0.30])            # blue-grey starship paint
    nz = fnoise(n, 1.7, 91)
    wear = np.clip((_blur(fnoise(n, 2.2, 93), 4) - 0.55) * 3.0, 0, 1)
    # hazard band along the top edge
    band = (v > 0.74) & (v < 0.94)
    stripe = (((mx + my) / 0.03) % 2) < 1.0
    haz = np.where(stripe, 0.88, 0.04)
    col = np.tile(paint, (n, n, 1)) * (0.85 + nz[..., None] * 0.3)
    hazc = np.stack([haz, haz * 0.78, haz * 0.05 + 0.01], axis=2)
    col = np.where(band[..., None], hazc, col)
    # thin white-ish edge lines
    line = (np.abs(v - 0.72) < 0.012) | (np.abs(v - 0.96) < 0.012)
    col = np.where(line[..., None], np.array([0.6, 0.62, 0.64]), col)
    # vertical panel seam at tile edges + two bolts
    seam = (np.minimum(u, 1 - u) < 0.004)
    col = np.where(seam[..., None], col * 0.45, col)
    # worn metal showing through on the bottom (kicks)
    wearb = wear * (1 - np.clip(v * 1.5, 0, 1)) * 1.4
    col = col * (1 - wearb[..., None] * 0.7) + np.array([0.45, 0.46, 0.48]) * wearb[..., None] * 0.7
    h = nz * 0.04 - seam * 0.3 + band * 0.05
    for bx in (0.08, 0.92):
        dd = np.hypot((u - bx) * 0.70, (v - 0.35) * 0.18)
        h += np.exp(-(dd / 0.006) ** 2) * 0.5
    rough = 0.5 + nz * 0.2 - wearb * 0.25
    metal = np.clip(0.25 + wearb * 0.6, 0, 1)
    ao = np.clip(1 - seam * 0.5, 0, 1)
    return np.clip(col, 0, 1), normal_from_height(h, 5.0), _pack_orm(ao, np.clip(rough, 0, 1), metal)


def surf_hull_window_frame(n=512):
    Y, X = np.mgrid[0:n, 0:n]
    x = X / n
    y = Y / n
    nz = fnoise(n, 1.8, 101)
    # brushed along x
    br = fnoise(n, 0.5, 103)
    br = _blur(np.tile(br[:1, :], (n, 1)) * 0.5 + br * 0.5, 1)
    base = 0.13 + nz * 0.05 + (br - 0.5) * 0.03
    alb = np.stack([base * 0.95, base, base * 1.12], axis=2)
    bolt = np.zeros((n, n))
    for bx in np.arange(0.0625, 1, 0.125):
        for by in (0.2, 0.8):
            dd = np.hypot(((x - bx + .5) % 1) - .5, ((y - by + .5) % 1) - .5)
            bolt += np.exp(-(dd / 0.018) ** 2)
    seam = (np.abs(y - 0.5) < 0.004)
    h = nz * 0.05 + bolt * 0.5 - seam * 0.3
    alb = np.where((bolt > 0.5)[..., None], alb * 1.6, alb)
    alb = np.where(seam[..., None], alb * 0.5, alb)
    rough = 0.36 + nz * 0.15
    return np.clip(alb, 0, 1), normal_from_height(h, 5.0), _pack_orm(np.clip(1 - seam * 0.5, 0, 1), rough, np.full((n, n), 0.85))


ARCH_SURFACES = {
    "hull_plate": (surf_hull_plate, 1024),
    "stair_tread": (surf_stair_tread, 512),
    "stair_riser": (surf_stair_riser, 512),
    "hull_window_frame": (surf_hull_window_frame, 512),
}


def make_arch_textures(outdir):
    """Write godot/textures/surfaces/<name>_{albedo,normal,orm}.png (outdir = textures dir)."""
    from .textures_lib import prefilter_existing
    for name, (fn, n) in ARCH_SURFACES.items():
        alb, nrm, orm = prefilter_existing(*fn(n))     # band-limit (see docs/TEXTURES.md)
        save(os.path.join(outdir, "surfaces", name + "_albedo.png"), np.clip(alb, 0, 1))
        save_data(os.path.join(outdir, "surfaces", name + "_normal.png"), nrm)
        save_data(os.path.join(outdir, "surfaces", name + "_orm.png"), orm)
