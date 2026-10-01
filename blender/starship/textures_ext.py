"""Extended tileable PBR surface library (~110 sets) for the ship shell and for the props.

Each recipe returns (albedo, normal, orm) float arrays; `build_one(name)` runs it and `make_ext_surfaces(outdir)`
fans the recipes out over processes and writes
    surfaces/<name>_albedo.png   sRGB
    surfaces/<name>_normal.png   OpenGL tangent space, Non-Color
    surfaces/<name>_orm.png      R occlusion, G roughness, B metallic, Non-Color
    surfaces/index.json          {name: {size, tile_m, group, neutral}}  (read by godot/scripts/materials.gd)

"neutral" sets (prefix `p_`) are tint-friendly (near-white albedo, ORM roughness is a relative modulation around
0.9) and are used by godot/scripts/prop_materials.gd on top of the flat colours baked into the GLBs.

Texture sizes are 512 (1024 for hero surfaces, 256 for fine, uniform ones); `tile_m` is the real-world size of
one repeat in metres.  See docs/TEXTURES.md.
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from . import textures_lib as L
from .textures_lib import blur, coords, finish, hexc, noise, soft, streaks, voronoi

REG = {}


def reg(name, size=512, tile=1.0, group="misc", neutral=False):
    def deco(fn):
        REG[name] = {"fn": fn, "size": size, "tile_m": tile, "group": group, "neutral": neutral}
        return fn
    return deco


def add(name, fn, **kw):
    reg(name, **kw)(fn)


def _col(c):
    return hexc(c)[None, None, :]


def _tone(base, v):
    """base colour (3,) times a scalar field -> (n, n, 3)."""
    return base[None, None, :] * v[..., None]


def _mix(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


# ============================================================ metals (brushed, anodised)
def brushed(color, rough=0.32, metal=1.0, seed=1, length=55, scratch=0.35, mottle=0.04, tint_var=0.0):
    def fn(n):
        s1 = streaks(n, seed, length, 0.8)
        s2 = streaks(n, seed + 1, length / 4, 0.7)
        sc = streaks(n, seed + 2, length * 1.8, 0.6)
        m = noise(n, seed + 3, 2.5, fmax=0.01)
        v = 1 + 0.045 * s1 + 0.03 * s2 + mottle * m
        v -= scratch * 0.12 * np.clip(sc - 1.7, 0, 3)
        alb = _tone(hexc(color), v)
        if tint_var:
            alb = alb * (1 + tint_var * np.stack([m, m * 0.5, -m * 0.4], 2))
        h = 0.5 * s1 + 0.3 * s2 - scratch * np.clip(sc - 1.7, 0, 3)
        return finish(alb, h, rough * (1 + 0.1 * s2) + 0.04 * np.clip(sc - 1.7, 0, 3), metal=metal, nstr=0.5, hblur=0.7)
    return fn


for _nm, _c, _r, _sd in (("alu_silver", "#c9ced4", 0.30, 11), ("alu_graphite", "#5d6269", 0.34, 12),
                         ("alu_anodised_blue", "#4a74b8", 0.28, 13), ("alu_anodised_red", "#b23a34", 0.28, 14),
                         ("alu_anodised_gold", "#c9a24a", 0.28, 15), ("alu_anodised_teal", "#2f9a9a", 0.28, 16),
                         ("steel_brushed", "#a9aeb5", 0.36, 17), ("brass_brushed", "#c4a257", 0.32, 18),
                         ("copper_brushed", "#c06f46", 0.34, 19), ("titanium_brushed", "#8a8d92", 0.38, 20)):
    add(_nm, brushed(_c, _r, seed=_sd), tile=1.0, group="metal")


def _chrome(n):
    m = noise(n, 31, 2.5, fmax=0.02)
    return finish(_tone(hexc("#dfe3e8"), 1 + 0.02 * m), 0.1 * m, 0.1 + 0.02 * m, metal=1.0, nstr=0.2)


add("chrome_polished", _chrome, size=256, tile=1.0, group="metal")


def _gunmetal(n):
    s = streaks(n, 33, 20, 0.9)
    m = noise(n, 34, 2.0, fmax=0.05)
    sp = np.clip(noise(n, 35, 0.5, fmax=0.2) - 1.5, 0, 3)
    return finish(_tone(hexc("#3b4048"), 1 + 0.05 * m + 0.03 * s + 0.06 * sp), 0.2 * s, 0.38 + 0.06 * m, metal=0.9, nstr=0.4)


add("gunmetal_blasted", _gunmetal, tile=1.0, group="metal")


# ============================================================ plates / patterns
def diamond_plate(color, rough, seed, lugs=10, dark=False):
    def fn(n):
        x, y = coords(n)
        u = x / n * lugs
        v = y / n * lugs
        iu, iv = np.floor(u), np.floor(v)
        pu, pv = u - iu - 0.5, v - iv - 0.5
        even = ((iu + iv) % 2 == 0)
        a = np.where(even, pu + pv, pu - pv) / np.sqrt(2)
        b = np.where(even, pu - pv, pu + pv) / np.sqrt(2)
        r = np.sqrt((a / 0.40) ** 2 + (b / 0.14) ** 2)
        px = n / lugs
        lug = soft((1 - r) * px * 0.14, 2.2)
        nz = noise(n, seed, 2.0, fmax=0.06)
        wear = np.clip(noise(n, seed + 1, 1.5, fmax=0.1) - 1.2, 0, 3)
        v_ = 1 + 0.04 * nz + lug * 0.08 - wear * 0.03
        alb = _tone(hexc(color), v_)
        return finish(alb, lug + 0.05 * nz, rough + 0.12 * wear - 0.06 * lug + 0.04 * nz, ao=1 - 0.25 * (1 - lug) * 0.4,
                      metal=0.85 - 0.2 * wear, nstr=2.2, hblur=1.1)
    return fn


add("diamond_plate_steel", diamond_plate("#8a9098", 0.42, 41), tile=1.0, group="plate")
add("diamond_plate_dark", diamond_plate("#40454d", 0.46, 42), tile=1.0, group="plate")
add("diamond_plate_alu", diamond_plate("#b9bec6", 0.36, 43, lugs=12), tile=1.0, group="plate")


def riveted(color, plates=2, seed=1, rough=0.45, metal=0.8, stripe=None, rivet_n=4, wear=0.5):
    def fn(n):
        x, y = coords(n)
        pw = n / plates
        dx = L.periodic_dist(x, pw)
        dy = L.periodic_dist(y, pw)
        edge = np.minimum(dx, dy)
        seam = soft(2.5 - edge, 2.0)                      # groove
        bevel = soft(edge - 2.5, 4.0) - soft(edge - 9.0, 6.0)
        pid = (np.floor(x / pw) + np.floor(y / pw) * plates).astype(int)
        tone = L.rand_by_id(pid, seed, -0.04, 0.04, plates * plates)
        nz = noise(n, seed + 2, 2.2, fmax=0.05)
        # rivets on a lattice inset 20 px from each plate edge
        rp = pw / rivet_n
        rx = L.periodic_dist(x - pw * 0.0 - rp * 0.5, rp)
        ry = L.periodic_dist(y - rp * 0.5, rp)
        on_edge = (edge < 18)
        rr = np.hypot(rx, ry)
        rivet = soft(5.5 - rr, 2.0) * on_edge * (rp > 12)
        rivet = np.where(np.minimum(dx, dy) < 22, rivet, 0)
        w = np.clip(noise(n, seed + 3, 1.6, fmax=0.12) - 0.8, 0, 3) * wear
        v = 1 + tone + 0.04 * nz - 0.35 * seam - 0.04 * w + 0.07 * rivet
        alb = _tone(hexc(color), v)
        if stripe:
            band = soft(10 - np.abs(((y / n * plates) % 1) - 0.82) * pw, 2.0)
            alb = _mix(alb, _col(stripe)[0] * np.ones_like(alb), band * 0.85)
        h = 1.0 * rivet + 0.6 * bevel - 1.6 * seam + 0.05 * nz
        return finish(alb, h, rough + 0.25 * w + 0.2 * seam, ao=1 - 0.55 * seam, metal=metal - 0.3 * w, nstr=2.0)
    return fn


add("riveted_plate_steel", riveted("#8a9199", 2, 51), tile=2.0, group="plate")
add("riveted_plate_grey", riveted("#6c737d", 2, 52, 0.5, 0.6), tile=2.0, group="plate")
add("riveted_plate_blue", riveted("#3f5f93", 2, 53, 0.45, 0.55, stripe="#d8dde4"), tile=2.0, group="plate")
add("riveted_plate_big", riveted("#9aa0a8", 1, 54, 0.42, 0.8, rivet_n=6), tile=2.0, group="plate")


def perforated(color, holes=10, r=0.27, seed=1, backing="#15181c", hex_=False):
    def fn(n):
        x, y = coords(n)
        p = n / holes
        if hex_:
            ex, cid, lu, lv = L.hex_cells(n, holes)
            d = np.hypot(lu, lv) * p
        else:
            d = np.hypot(L.periodic_dist(x - p / 2, p), L.periodic_dist(y - p / 2, p))
        hole = soft(p * r - d, 2.2)
        nz = noise(n, seed, 2.0, fmax=0.05)
        rim = soft(p * r + 2.5 - d, 3.0) * (1 - hole)
        alb = _mix(_tone(hexc(color), 1 + 0.04 * nz), _col(backing)[0] * np.ones((n, n, 3), np.float32), hole)
        ao = 1 - 0.7 * hole
        return finish(alb, rim * 0.6 - hole * 0.6, 0.45 + 0.2 * hole + 0.05 * nz, ao=ao, metal=0.85 * (1 - 0.7 * hole),
                      nstr=1.6, hblur=1.2)
    return fn


add("perforated_mesh", perforated("#9ea3aa", 10, 0.27, 61), tile=1.0, group="plate")
add("perforated_dark", perforated("#3a3f46", 12, 0.25, 62), tile=1.0, group="plate")
add("perforated_hex", perforated("#8e949c", 8, 0.34, 63, hex_=True), tile=1.0, group="plate")


def _vent(n):
    x, y = coords(n)
    slats = 12
    p = n / slats
    t = np.mod(y, p) / p
    slat = np.clip(np.sin(np.pi * t), 0, 1) ** 0.6
    gap = soft(0.17 - np.abs(t - 0.5) * 1.0 - 0.0, 0.05) * 0 + (1 - soft((np.abs(t - 0.5) - 0.34) * p, 2.0))
    nz = noise(n, 71, 2.0, fmax=0.05)
    alb = _tone(hexc("#7d838b"), (0.55 + 0.45 * slat) * (1 + 0.04 * nz))
    alb = _mix(alb, _col("#0e1013")[0] * np.ones_like(alb), (1 - gap) * 0.9)
    return finish(alb, slat * 0.8 + gap * 0.3, 0.42 + 0.1 * (1 - gap), ao=0.35 + 0.65 * gap, metal=0.7, nstr=1.8, hblur=1.3)


add("vent_grille", _vent, tile=1.0, group="plate")


def carbon(twill=True, seed=1, n_th=48, color="#1a1c20", gloss=0.22):
    def fn(n):
        x, y = coords(n)
        i = np.floor(x / n * n_th)
        j = np.floor(y / n * n_th)
        fu = (x / n * n_th) % 1
        fv = (y / n * n_th) % 1
        over = (((i - j) % 4) < 2) if twill else (((i + j) % 2) == 0)
        prof_x = np.sin(np.pi * fu) ** 0.7
        prof_y = np.sin(np.pi * fv) ** 0.7
        th = np.where(over, prof_x, prof_y)
        rnd = L.rand_by_id((i * n_th + j).astype(int) % 4096, seed, -0.2, 0.2, 4096)
        sheen = np.where(over, 1.0, 0.55) * (0.5 + 0.5 * th)
        alb = _tone(hexc(color), (0.55 + 0.9 * sheen) * (1 + rnd))
        return finish(alb, th * 0.8, gloss + 0.12 * (1 - th), ao=0.55 + 0.45 * th, metal=0.15, nstr=1.4, hblur=1.1)
    return fn


add("carbon_fibre_twill", carbon(True, 81), tile=0.6, group="composite")
add("carbon_fibre_plain", carbon(False, 82, 40), tile=0.6, group="composite")
add("kevlar_weave", carbon(False, 83, 40, "#b99a2b", 0.4), tile=0.6, group="composite")


def hex_plate(color, cols=8, seed=1, rough=0.4, metal=0.8, gap=3.0, bevel=True):
    def fn(n):
        edge, cid, lu, lv = L.hex_cells(n, cols)
        tone = L.rand_by_id(cid % 4096, seed, -0.05, 0.05, 4096)
        nz = noise(n, seed, 2.0, fmax=0.05)
        groove = soft(gap - edge, 2.0)
        bev = soft(edge - gap, 5.0) - soft(edge - gap - 10, 6.0) if bevel else 0
        alb = _tone(hexc(color), 1 + tone + 0.04 * nz - 0.5 * groove)
        return finish(alb, 0.8 * bev - 1.5 * groove, rough + 0.2 * groove, ao=1 - 0.6 * groove, metal=metal, nstr=1.8)
    return fn


add("hex_plate_steel", hex_plate("#8d939b", 8, 91), tile=1.0, group="plate")
add("hex_plate_dark", hex_plate("#3b4048", 10, 92), tile=1.0, group="plate")
add("hex_tile_white", hex_plate("#e4e7e9", 8, 93, 0.22, 0.0, 2.5), tile=1.0, group="tile")
add("hex_tile_teal", hex_plate("#2b8f95", 8, 94, 0.22, 0.0, 2.5), tile=1.0, group="tile")


# ============================================================ tiles / stone / concrete
def tiles(color, cols=4, rows=None, grout="#a9a9a2", seed=1, rough=0.18, gap=3.5, tone=0.035, staggered=False, speck=0.0):
    rows = rows or cols

    def fn(n):
        x, y = coords(n)
        pw, ph = n / cols, n / rows
        xs = x + (np.floor(y / ph) % 2) * pw / 2 if staggered else x
        dx = L.periodic_dist(xs, pw)
        dy = L.periodic_dist(y, ph)
        edge = np.minimum(dx, dy)
        g = soft(gap / 2 - edge, 1.8)
        iu = np.floor(xs / pw) % cols
        iv = np.floor(y / ph)
        tid = (iu + iv * cols).astype(int)
        t = L.rand_by_id(tid, seed, -tone, tone, cols * rows)
        nz = noise(n, seed + 1, 2.2, fmax=0.04)
        sp = np.clip(noise(n, seed + 2, 0.8, fmax=0.2) - 1.3, 0, 3) * speck
        alb = _mix(_tone(hexc(color), 1 + t + 0.03 * nz - 0.25 * sp), _col(grout)[0] * np.ones((n, n, 3), np.float32) * (1 + 0.04 * nz)[..., None], g)
        h = soft(edge - gap / 2, 6.0) * 0.6 - g * 1.0 + 0.03 * nz
        return finish(alb, h, np.where(g > 0.5, 0.85, rough + 0.05 * nz), ao=1 - 0.5 * g, metal=0.0, nstr=1.5)
    return fn


add("ceramic_tile_white", tiles("#e9ebeb", 4, grout="#b9b9b2", seed=101), tile=2.0, group="tile")
add("ceramic_tile_blue", tiles("#3f78b5", 4, grout="#bcc3c9", seed=102), tile=2.0, group="tile")
add("ceramic_tile_green", tiles("#3f8f6a", 4, grout="#bcc3c0", seed=103), tile=2.0, group="tile")
add("ceramic_tile_black", tiles("#1d2024", 4, grout="#4a4d52", seed=104, rough=0.12), tile=2.0, group="tile")
add("ceramic_tile_sand", tiles("#cdbb98", 4, grout="#a39b88", seed=105, speck=0.4, rough=0.35), tile=2.0, group="tile")
add("ceramic_subway_white", tiles("#eef0ee", 4, 8, grout="#b0b0aa", seed=106, staggered=True, gap=3.0), tile=2.0, group="tile")
add("mosaic_tile_blue", tiles("#3a86b8", 16, grout="#c9d0d4", seed=107, gap=3.0, tone=0.12), tile=1.0, group="tile")
add("mosaic_tile_grey", tiles("#8d949b", 16, grout="#c9cbcc", seed=108, gap=3.0, tone=0.1), tile=1.0, group="tile")


def marble(base, vein, seed, vein_n=3.0, warp=1.2, sharp=14, rough=0.12, vein2=None):
    def fn(n):
        x, y = coords(n)
        w = noise(n, seed, 2.4, fmax=0.015) * warp
        t = (x / n * vein_n + y / n * vein_n * 0.6 + w * 0.3)
        v1 = (1 - np.abs(np.sin(np.pi * t))) ** sharp
        w2 = noise(n, seed + 1, 2.0, fmax=0.03) * 0.6
        t2 = (x / n * vein_n * 2 - y / n * 3 + w2)
        v2 = (1 - np.abs(np.sin(np.pi * np.round(t2 * 1.0) * 0 + np.pi * t2))) ** (sharp * 2)
        cloud = noise(n, seed + 2, 2.6, fmax=0.02)
        b = _tone(hexc(base), 1 + 0.05 * cloud)
        vc = _col(vein)[0] * np.ones_like(b)
        alb = _mix(b, vc, np.clip(v1 * 0.8 + v2 * 0.3, 0, 1))
        return finish(alb, 0.05 * cloud, rough + 0.03 * cloud, nstr=0.3)
    return fn


add("marble_white", marble("#ecebe8", "#8b8f98", 111), tile=2.0, group="stone")
add("marble_black", marble("#1c1d20", "#c7c2b5", 112, 2.5, 1.4, 16), tile=2.0, group="stone")
add("marble_green", marble("#2c5a46", "#d6e0d2", 113, 3.5, 1.3, 12), tile=2.0, group="stone")


def terrazzo(base, chips, seed, cells=26, density=0.5):
    def fn(n):
        f1, f2, cid = voronoi(n, cells, seed, 1.0)
        pick = L.rand_by_id(cid, seed + 1, 0, 1, cells * cells)
        size = L.rand_by_id(cid, seed + 2, 0.18, 0.4, cells * cells)
        chip = (pick < density).astype(np.float32) * soft((size - f1) * (n / cells), 2.0)
        cidx = (L.rand_by_id(cid, seed + 3, 0, len(chips) - 1e-3, cells * cells)).astype(int)
        cols = np.stack([hexc(c) for c in chips])[cidx]
        nz = noise(n, seed + 4, 2.0, fmax=0.1)
        b = _tone(hexc(base), 1 + 0.05 * nz)
        alb = _mix(b, cols * (1 + 0.1 * nz)[..., None], chip)
        return finish(alb, chip * 0.3 + 0.1 * nz, 0.22 + 0.1 * (1 - chip) + 0.03 * nz, nstr=0.8)
    return fn


add("terrazzo_light", terrazzo("#d8d4c8", ["#7e8a96", "#b4573f", "#2f3a44", "#e6e1d6", "#8fa07d"], 121), tile=2.0, group="stone")
add("terrazzo_dark", terrazzo("#3a3d42", ["#c9c3b4", "#7a8da3", "#a55a3e", "#e0dccf"], 122, 30, 0.55), tile=2.0, group="stone")


def concrete(color, seed, pores=1.0, form=False, rough=0.88, big=0.06):
    def fn(n):
        a = noise(n, seed, 1.8, fmax=0.08)
        b = noise(n, seed + 1, 2.8, fmax=0.01)
        pore = np.clip(noise(n, seed + 2, 0.6, fmax=0.18) - 1.9, 0, 3) * pores
        v = 1 + 0.05 * a + big * b - 0.18 * pore
        x, y = coords(n)
        h = 0.3 * a - pore
        if form:
            seam = soft(2.2 - L.periodic_dist(y, n / 2), 1.8) + soft(2.2 - L.periodic_dist(x, n / 2), 1.8)
            tie = soft(6 - np.hypot(L.periodic_dist(x - n / 4, n / 2), L.periodic_dist(y - n / 4, n / 2)), 2.0)
            v = v - 0.2 * seam - 0.25 * tie
            h = h - seam * 1.5 - tie
        return finish(_tone(hexc(color), v), h, rough - 0.1 * pore, ao=1 - 0.6 * pore, nstr=1.2)
    return fn


add("concrete_smooth", concrete("#8a8a86", 131, 0.4, rough=0.7), tile=2.0, group="stone")
add("concrete_poured", concrete("#7b7b78", 132, 1.0, form=True), tile=2.0, group="stone")
add("concrete_rough", concrete("#6f6f6c", 133, 1.6, big=0.09), tile=2.0, group="stone")


def _epoxy(n):
    nz = noise(n, 141, 2.0, fmax=0.05)
    chips = np.clip(noise(n, 142, 0.5, fmax=0.2) - 1.4, 0, 3)
    alb = _tone(hexc("#6b7078"), 1 + 0.04 * nz + 0.1 * chips)
    return finish(alb, 0.2 * nz + 0.6 * chips, 0.4 + 0.1 * chips, nstr=0.8)


add("epoxy_floor_grey", _epoxy, size=256, tile=1.0, group="floor")


def rubber_studs(color, seed, pitch_cells=20, ribbed=False, rough=0.82):
    def fn(n):
        x, y = coords(n)
        p = n / pitch_cells
        if ribbed:
            d = L.periodic_dist(x, p) - p * 0.5
            h = soft(-d - 0.5, p * 0.5) * 0 + (0.5 + 0.5 * np.cos(2 * np.pi * x / p))
        else:
            d = np.hypot(L.periodic_dist(x - p / 2, p), L.periodic_dist(y - p / 2, p))
            h = soft(p * 0.32 - d, 4.0)
        nz = noise(n, seed, 2.0, fmax=0.1)
        alb = _tone(hexc(color), 1 + 0.08 * nz - 0.15 * h * 0 + 0.06 * h)
        return finish(alb, h * 1.2 + 0.05 * nz, rough - 0.08 * h, ao=1 - 0.3 * (1 - h), nstr=1.6, hblur=1.4)
    return fn


add("rubber_floor_black", rubber_studs("#1d1d1f", 151), tile=1.0, group="floor")
add("rubber_floor_grey", rubber_studs("#5b5f66", 152), tile=1.0, group="floor")
add("rubber_floor_ribbed", rubber_studs("#26282b", 153, 24, True), tile=1.0, group="floor")


def _cork(n):
    f1, f2, cid = voronoi(n, 70, 161, 1.0)
    g = L.rand_by_id(cid, 162, -0.18, 0.18, 70 * 70)
    nz = noise(n, 163, 1.5, fmax=0.2)
    dark = np.clip(noise(n, 164, 0.5, fmax=0.2) - 1.5, 0, 3)
    alb = _tone(hexc("#b98c58"), 1 + g + 0.08 * nz - 0.25 * dark)
    return finish(alb, (f2 - f1) * 0.8 + 0.1 * nz, 0.8, ao=0.8 + 0.2 * np.clip(f2 - f1, 0, 1), nstr=1.2)


add("cork", _cork, size=256, tile=1.0, group="floor")


# ============================================================ woods
def wood(light, dark, seed, rings=9, warp=2.2, pore=0.5, planks=0, gap=0.0, rough=0.5, vertical_grain=True, nstr=0.8):
    def fn(n):
        x, y = coords(n)
        wp = noise(n, seed, 2.2, fmax=0.012)
        fib = streaks(n, seed + 1, 60, 0.8, vertical=True)
        fib2 = streaks(n, seed + 2, 16, 0.6, vertical=True)
        if planks:
            pw = n / planks
            pid = np.floor(x / pw).astype(int) % planks
            off = L.rand_by_id(pid, seed + 3, 0, 1, planks)
            xl = L.periodic_dist(x, pw)
        else:
            pid = np.zeros((n, n), int)
            off = np.zeros((n, n), np.float32)
            xl = np.full((n, n), 99.0)
        t = (x / n * rings + wp * warp * 0.15 + off * 7.3)
        ring = 0.5 + 0.5 * np.sin(2 * np.pi * np.floor(t * 0 + t) + 0) * 0
        r = (t * 2) % 1
        ring = np.clip(np.abs(r - 0.5) * 2, 0, 1) ** 1.5
        late = soft(ring - 0.55, 0.5) * 0.5 + ring * 0.5
        v = np.clip(0.35 + 0.5 * late + 0.06 * fib + 0.04 * fib2 + 0.05 * wp, 0, 1)
        alb = _mix(_col(light)[0] * np.ones((n, n, 3), np.float32), _col(dark)[0] * np.ones((n, n, 3), np.float32), v)
        tone = L.rand_by_id(pid, seed + 4, -0.06, 0.06, max(planks, 1))
        alb = alb * (1 + tone)[..., None]
        grooves = soft(gap / 2 - xl, 1.8) if planks and gap else np.zeros((n, n), np.float32)
        alb = alb * (1 - 0.55 * grooves)[..., None]
        h = -0.6 * fib2 * pore - 0.4 * ring - 1.4 * grooves
        return finish(alb, h, rough + 0.12 * (1 - late) + 0.05 * fib2 + 0.3 * grooves, ao=1 - 0.5 * grooves, nstr=nstr, hblur=0.9)
    return fn


add("wood_oak", wood("#c9a06a", "#8e6a3a", 171, 8), tile=1.0, group="wood")
add("wood_walnut", wood("#6b4630", "#2e1c11", 172, 10), tile=1.0, group="wood")
add("wood_teak", wood("#b0763a", "#6f4219", 173, 7, 1.8), tile=1.0, group="wood")
add("wood_mahogany", wood("#8b3f26", "#3e1710", 174, 9), tile=1.0, group="wood")
add("wood_planks_dark", wood("#5a3a24", "#2b1a10", 175, 6, planks=4, gap=5), tile=2.0, group="wood")
add("wood_planks_light", wood("#d2ae78", "#a07a48", 176, 6, planks=4, gap=5), tile=2.0, group="wood")
add("wood_planks_grey", wood("#a9a59d", "#6e6a62", 177, 5, planks=6, gap=4, rough=0.6), tile=2.0, group="wood")


def _bamboo(n):
    x, y = coords(n)
    strips = 16
    pw = n / strips
    xl = L.periodic_dist(x, pw)
    sid = (np.floor(x / pw)).astype(int) % strips
    node_y = (L.rand_by_id(sid, 181, 0, 1, strips) * n)
    nd = L.periodic_dist(y - node_y, n / 3)
    node = soft(5 - nd, 4.0)
    fib = streaks(n, 182, 70, 0.8, vertical=True)
    tone = L.rand_by_id(sid, 183, -0.05, 0.05, strips)
    v = 1 + tone + 0.04 * fib - 0.12 * node
    alb = _tone(hexc("#d9c27e"), v)
    g = soft(2.2 - xl, 1.8)
    alb = alb * (1 - 0.35 * g)[..., None]
    return finish(alb, -g * 1.2 - node * 0.4 + 0.2 * fib, 0.42 + 0.08 * node + 0.2 * g, nstr=1.0)


add("wood_bamboo", _bamboo, tile=1.0, group="wood")


def _plywood(n):
    f = streaks(n, 191, 80, 1.0, vertical=True)
    nz = noise(n, 192, 2.0, fmax=0.03)
    alb = _tone(hexc("#c8a875"), 1 + 0.06 * f + 0.05 * nz)
    return finish(alb, 0.3 * f, 0.6, nstr=0.6)


add("plywood", _plywood, size=256, tile=1.0, group="wood")


def _parquet(n):
    x, y = coords(n)
    cells = 8
    p = n / cells
    iu, iv = np.floor(x / p), np.floor(y / p)
    horiz = ((iu + iv) % 2 == 0)
    fu = (x % p) / p
    fv = (y % p) / p
    # four boards per block, grain along the block orientation
    board = np.where(horiz, np.floor(fv * 4), np.floor(fu * 4))
    bl = np.where(horiz, (fv * 4) % 1, (fu * 4) % 1)
    edge = np.minimum(bl, 1 - bl) * p / 4
    g = soft(1.8 - edge, 1.6)
    ft = streaks(n, 201, 50, 0.7)
    ft2 = streaks(n, 202, 50, 0.7, vertical=True)
    fib = np.where(horiz, ft, ft2)
    tone = L.rand_by_id(((iu * cells + iv) * 4 + board).astype(int) % 4096, 203, -0.1, 0.1, 4096)
    alb = _tone(hexc("#b78a55"), 1 + tone + 0.05 * fib) * (1 - 0.5 * g)[..., None]
    return finish(alb, 0.3 * fib - 1.3 * g, 0.42 + 0.3 * g, ao=1 - 0.4 * g, nstr=1.0)


add("wood_parquet", _parquet, tile=2.0, group="wood")


# ============================================================ leather / fabric / carpet
def leather(color, seed, cells=30, rough=0.5, sheen=0.0):
    def fn(n):
        f1, f2, cid = voronoi(n, cells, seed, 1.0)
        crease = np.clip(1 - (f2 - f1) * 4.0, 0, 1)
        nz = noise(n, seed + 1, 2.2, fmax=0.05)
        puff = soft((f2 - f1) * (n / cells) - 1.5, 5.0)
        tone = L.rand_by_id(cid, seed + 2, -0.04, 0.04, cells * cells)
        alb = _tone(hexc(color), 1 + tone + 0.05 * nz - 0.22 * crease)
        return finish(alb, puff + 0.1 * nz, rough + 0.12 * crease - sheen * puff, ao=1 - 0.35 * crease, nstr=1.4, hblur=1.2)
    return fn


add("leather_black", leather("#262322", 211), size=256, tile=1.0, group="leather")
add("leather_brown", leather("#6a432b", 212), size=256, tile=1.0, group="leather")
add("leather_red", leather("#8e2a28", 213), size=256, tile=1.0, group="leather")
add("leather_tan", leather("#b08a5e", 214, 26), size=256, tile=1.0, group="leather")
add("leather_white", leather("#d9d4ca", 215, 34, 0.42), size=256, tile=1.0, group="leather")


def weave(color, color2=None, seed=1, n_th=64, rough=0.92, thick=0.35, plain=True):
    def fn(n):
        x, y = coords(n)
        i = np.floor(x / n * n_th)
        j = np.floor(y / n * n_th)
        fu = (x / n * n_th) % 1
        fv = (y / n * n_th) % 1
        over = ((i + j) % 2 == 0) if plain else (((i - j) % 4) < 2)
        th = np.where(over, np.sin(np.pi * fu) ** 0.6, np.sin(np.pi * fv) ** 0.6)
        rx = L.rand_by_id(i.astype(int) % 512, seed, -0.12, 0.12, 512)
        ry = L.rand_by_id(j.astype(int) % 512, seed + 1, -0.12, 0.12, 512)
        tone = np.where(over, rx, ry)
        fuzz = noise(n, seed + 2, 1.0, fmax=0.2) * 0.04
        base = _col(color)[0] * np.ones((n, n, 3), np.float32)
        if color2:
            base = _mix(base, _col(color2)[0] * np.ones((n, n, 3), np.float32), np.where(over, 0.0, 1.0))
        alb = base * (0.7 + 0.3 * th + tone + fuzz)[..., None]
        return finish(alb, th, rough, ao=0.5 + 0.5 * th, nstr=thick * 4, hblur=1.0)
    return fn


add("fabric_navy", weave("#2c3d68", seed=221), tile=0.5, group="fabric")
add("fabric_grey", weave("#707680", seed=222), tile=0.5, group="fabric")
add("fabric_teal", weave("#2a7a82", seed=223), tile=0.5, group="fabric")
add("fabric_red", weave("#8f2b2d", seed=224), tile=0.5, group="fabric")
add("fabric_tan", weave("#b49d78", seed=225), tile=0.5, group="fabric")
add("fabric_heather", weave("#6f7d93", "#8d97a8", seed=226, plain=False), tile=0.5, group="fabric")


def carpet_tweed(c1, c2, seed, loop=False):
    def fn(n):
        a = noise(n, seed, 1.0, fmax=0.2)
        b = noise(n, seed + 1, 1.0, fmax=0.2)
        m = soft(a, 0.9)
        if loop:
            f1, f2, cid = voronoi(n, 56, seed + 2, 1.0)
            lp = soft(1 - f1 * 2.0, 0.9)
            m = np.clip(m * 0.4 + 0.6 * lp, 0, 1)
        base = _mix(_col(c1)[0] * np.ones((n, n, 3), np.float32), _col(c2)[0] * np.ones((n, n, 3), np.float32), m)
        blot = noise(n, seed + 3, 2.4, fmax=0.015)
        alb = base * (1 + 0.04 * b + 0.04 * blot)[..., None]
        return finish(alb, a * 0.4 + 0.3 * b, 0.95, ao=0.7 + 0.3 * soft(a + 1, 2.0), nstr=1.0, hblur=1.2, ablur=0.7)
    return fn


add("carpet_tweed_grey", carpet_tweed("#4a4e55", "#7b808a", 231), size=256, tile=1.0, group="carpet")
add("carpet_tweed_red", carpet_tweed("#4d1c1f", "#8a3a3c", 232), size=256, tile=1.0, group="carpet")
add("carpet_tweed_navy", carpet_tweed("#1d2a4a", "#44577e", 233), size=256, tile=1.0, group="carpet")
add("carpet_loop_beige", carpet_tweed("#8a7c64", "#b5a68a", 234, True), size=256, tile=1.0, group="carpet")


def carpet_pattern(c1, c2, kind, seed, cells=8):
    def fn(n):
        x, y = coords(n)
        if kind == "diamond":
            u = (x / n * cells) % 1
            v = (y / n * cells) % 1
            d = np.abs(u - 0.5) + np.abs(v - 0.5)
            m = soft((0.32 - d) * (n / cells), 2.0)
            ring = soft(2.5 - np.abs(d - 0.42) * (n / cells), 1.8)
            m = np.clip(m + ring, 0, 1)
        elif kind == "hex":
            edge, cid, lu, lv = L.hex_cells(n, cells)
            m = soft(edge - 4, 2.0) * 0.0 + (1 - soft(edge - 3, 2.0)) * 0.0
            m = soft(np.hypot(lu, lv) * (n / cells) - n / cells * 0.38, 2.0) * 0 + (1 - soft(edge - 5.0, 2.0))
        else:                                              # stripes
            m = soft(L.periodic_dist(x, n / cells) - n / cells * 0.28, 2.0) * 0 + soft(n / cells * 0.18 - L.periodic_dist(x, n / cells), 2.0)
        pile = noise(n, seed, 1.0, fmax=0.2)
        m = m * 0.55                                   # soft contrast: big high-contrast checks shimmer and look harsh
        base = _mix(_col(c1)[0] * np.ones((n, n, 3), np.float32), _col(c2)[0] * np.ones((n, n, 3), np.float32), m)
        alb = base * (1 + 0.05 * pile)[..., None]
        return finish(alb, m * 0.3 + 0.35 * pile, 0.94, ao=0.75 + 0.25 * (1 - m * 0.5), nstr=1.0, hblur=1.2, ablur=0.7)
    return fn


add("carpet_geo_blue", carpet_pattern("#1f3358", "#6f86b3", "diamond", 241), size=256, tile=1.5, group="carpet")
add("carpet_geo_burgundy", carpet_pattern("#4a1b26", "#b08a5a", "diamond", 242, 6), size=256, tile=1.5, group="carpet")
add("carpet_hex_teal", carpet_pattern("#1b4a50", "#3f8f94", "hex", 243), size=256, tile=1.5, group="carpet")
add("carpet_stripe_navy", carpet_pattern("#1e2638", "#5d6f94", "stripe", 244, 8), size=256, tile=1.5, group="carpet")


def quilt(color, seed, cells=6, button="#222222", rough=0.55):
    def fn(n):
        x, y = coords(n)
        a = (x + y) / n * cells
        b = (x - y) / n * cells
        da, db = np.abs((a % 1) - 0.5), np.abs((b % 1) - 0.5)
        pill = np.clip(1 - np.maximum(da, db) * 2, 0, 1)
        h = np.sqrt(pill) * 1.0
        crease = 1 - soft(np.minimum(0.5 - da, 0.5 - db) * (n / cells) * 0.7 - 1.5, 3.0)
        # buttons at lattice nodes
        bu = np.hypot(L.periodic_dist(a, 1.0), L.periodic_dist(b, 1.0)) * (n / cells) * 0.7
        btn = soft(5 - bu, 2.0)
        nz = noise(n, seed, 2.0, fmax=0.06)
        alb = _tone(hexc(color), 1 + 0.05 * nz - 0.4 * crease)
        alb = _mix(alb, _col(button)[0] * np.ones_like(alb), btn * 0.8)
        return finish(alb, h * 1.4 - crease * 0.6 + btn * 0.6, rough + 0.2 * crease - 0.1 * btn, ao=1 - 0.5 * crease,
                      nstr=1.6, hblur=1.3)
    return fn


add("quilted_black", quilt("#25262a", 251), tile=1.0, group="padded")
add("quilted_blue", quilt("#2a4a7c", 252), tile=1.0, group="padded")
add("quilted_cream", quilt("#cfc6b1", 253, 5), tile=1.0, group="padded")


def _foam(n):
    x, y = coords(n)
    cells = 8
    p = n / cells
    u = (x % p) / p
    v = (y % p) / p
    pyr = (1 - np.maximum(np.abs(u - 0.5), np.abs(v - 0.5)) * 2)
    pyr = np.clip(pyr, 0, 1)
    nz = noise(n, 261, 1.5, fmax=0.15)
    alb = _tone(hexc("#2a2c31"), 0.6 + 0.6 * pyr + 0.06 * nz)
    return finish(alb, pyr * 1.8 + 0.1 * nz, 0.95, ao=0.3 + 0.7 * pyr, nstr=2.0, hblur=1.5)


add("acoustic_foam", _foam, tile=1.0, group="padded")


def _foam_panel(n):
    f1, f2, cid = voronoi(n, 40, 262, 1.0)
    nz = noise(n, 263, 1.2, fmax=0.2)
    pit = soft(0.18 - f1, 0.1) * 0.0 + np.clip(1 - f1 * 3, 0, 1)
    alb = _tone(hexc("#9aa2a8"), 1 + 0.05 * nz - 0.2 * pit)
    return finish(alb, -pit * 1.2 + 0.1 * nz, 0.95, ao=1 - 0.3 * pit, nstr=1.2, hblur=1.4)


add("acoustic_panel_grey", _foam_panel, size=256, tile=1.0, group="padded")


# ============================================================ tech surfaces
def _glass_ceramic(n):
    nz = noise(n, 271, 2.5, fmax=0.03)
    sp = np.clip(noise(n, 272, 0.6, fmax=0.2) - 2.0, 0, 3)
    alb = _tone(hexc("#14171c"), 1 + 0.15 * nz + 0.8 * sp)
    return finish(alb, 0.05 * nz, 0.08 + 0.02 * nz, metal=0.1, nstr=0.2)


add("glass_ceramic", _glass_ceramic, size=256, tile=1.0, group="tech")


def _solar(n):
    x, y = coords(n)
    cells = 4
    p = n / cells
    dx = L.periodic_dist(x, p)
    dy = L.periodic_dist(y, p)
    gap = soft(3 - np.minimum(dx, dy), 1.8)
    f1, f2, cid = voronoi(n, 12, 281, 1.0)
    crystal = L.rand_by_id(cid, 282, -0.08, 0.08, 144)
    bus = soft(2.2 - np.abs(((x / p) % 1 - 0.5) - 0.16) * p, 1.6) + soft(2.2 - np.abs(((x / p) % 1 - 0.5) + 0.16) * p, 1.6)
    fing = 0.5 + 0.5 * np.cos(2 * np.pi * y / (n / 48))
    cellcol = _tone(hexc("#1f3d78"), 1 + crystal + 0.05 * fing)
    alb = _mix(cellcol, _col("#b8bcc4")[0] * np.ones_like(cellcol), np.clip(bus, 0, 1) * 0.7)
    alb = _mix(alb, _col("#9aa0aa")[0] * np.ones_like(alb), gap)
    return finish(alb, -gap * 0.6 + bus * 0.2, 0.25 + 0.3 * gap, metal=0.3 + 0.4 * bus, nstr=1.2, hblur=1.2)


add("solar_cell", _solar, tile=1.0, group="tech")


def _pcb(n):
    rng = np.random.default_rng(291)
    g = 32
    cell = n // g
    trace = np.zeros((n, n), np.float32)
    pad = np.zeros((n, n), np.float32)
    y, x = np.mgrid[0:n, 0:n]
    for _ in range(90):
        gx, gy = rng.integers(0, g, 2)
        length = int(rng.integers(2, 7))
        horiz = rng.random() < 0.5
        for k in range(length):
            cx = int(((gx + (k if horiz else 0)) % g) * cell + cell // 2)
            cy = int(((gy + (0 if horiz else k)) % g) * cell + cell // 2)
            if horiz:
                ys_ = np.arange(cy - 2, cy + 3) % n
                xs_ = np.arange(cx - cell // 2, cx + cell // 2 + 1) % n
            else:
                ys_ = np.arange(cy - cell // 2, cy + cell // 2 + 1) % n
                xs_ = np.arange(cx - 2, cx + 3) % n
            trace[np.ix_(ys_, xs_)] = 1
        if rng.random() < 0.8:
            ex = int(((gx + (length if horiz else 0)) % g) * cell + cell // 2)
            ey = int(((gy + (0 if horiz else length)) % g) * cell + cell // 2)
            pad = np.maximum(pad, (np.hypot(((x - ex + n / 2) % n) - n / 2, ((y - ey + n / 2) % n) - n / 2) < 6).astype(np.float32))
    chips = np.zeros((n, n), np.float32)
    for _ in range(10):
        cx, cy = rng.integers(0, n, 2)
        w, h = rng.integers(24, 64, 2)
        m = (np.abs(((x - cx + n / 2) % n) - n / 2) < w / 2) & (np.abs(((y - cy + n / 2) % n) - n / 2) < h / 2)
        chips = np.maximum(chips, m.astype(np.float32))
    trace = blur(trace, 0.9)
    pad = blur(pad, 0.9)
    chips = blur(chips, 0.9)
    nz = noise(n, 292, 2.0, fmax=0.05)
    base = _tone(hexc("#1f5a3a"), 1 + 0.06 * nz)
    alb = _mix(base, _col("#2f7a4f")[0] * np.ones_like(base), np.clip(trace, 0, 1) * 0.8)
    alb = _mix(alb, _col("#c9a43a")[0] * np.ones_like(alb), np.clip(pad, 0, 1))
    alb = _mix(alb, _col("#17181b")[0] * np.ones_like(alb), np.clip(chips, 0, 1))
    return finish(alb, trace * 0.4 + pad * 0.6 + chips * 1.4, 0.4 - 0.15 * pad + 0.1 * chips, metal=0.9 * np.clip(pad, 0, 1), nstr=1.2)


add("circuit_board", _pcb, tile=1.0, group="tech")


def hazard(seed=301, c1="#e2b514", c2="#1c1c1e", stripes=8, worn=True):
    def fn(n):
        x, y = coords(n)
        t = ((x + y) / n * stripes) % 1
        m = soft((0.5 - np.abs(t - 0.5)) * 0 + (np.abs(t - 0.5) - 0.25) * (n / stripes) * 0.7, 2.0)
        wear = np.clip(noise(n, seed, 1.5, fmax=0.08) - 0.9, 0, 3) * (1.0 if worn else 0)
        nz = noise(n, seed + 1, 2.0, fmax=0.05)
        base = _mix(_col(c1)[0] * np.ones((n, n, 3), np.float32), _col(c2)[0] * np.ones((n, n, 3), np.float32), m)
        alb = base * (1 + 0.05 * nz - 0.1 * wear)[..., None]
        alb = _mix(alb, _col("#6c7077")[0] * np.ones_like(alb), np.clip(wear * 0.7, 0, 1))
        return finish(alb, 0.2 * nz - 0.8 * wear, 0.5 + 0.35 * wear, metal=np.clip(wear * 0.7, 0, 0.8), nstr=1.4)
    return fn


add("hazard_floor", hazard(), tile=2.0, group="floor")
add("hazard_floor_red", hazard(302, "#c4322a", "#e8e8e8", 8), tile=2.0, group="floor")


def _cargo_deck(n):
    x, y = coords(n)
    nz = noise(n, 311, 2.0, fmax=0.05)
    wear = np.clip(noise(n, 312, 1.4, fmax=0.1) - 1.0, 0, 3)
    base = _tone(hexc("#6b7078"), 1 + 0.05 * nz - 0.08 * wear)
    lane = soft(n * 0.025 - L.periodic_dist(x, n / 2), 2.0) + soft(n * 0.012 - np.abs(L.periodic_dist(x - n / 4, n / 2)), 2.0) * 0
    dash = soft(n * 0.012 - np.abs(L.periodic_dist(x - n / 4, n / 2)), 1.8) * (np.mod(y, n / 8) < n / 16)
    side = soft(n * 0.02 - L.periodic_dist(y, n), 2.0) * 0
    paint = np.clip(lane + dash + side, 0, 1) * (1 - 0.5 * np.clip(wear, 0, 1))
    alb = _mix(base, _col("#d8b523")[0] * np.ones_like(base), paint)
    plate = soft(2 - L.periodic_dist(y, n / 2), 1.6)
    alb = alb * (1 - 0.4 * plate)[..., None]
    return finish(alb, 0.2 * nz - 0.5 * plate - 0.2 * wear + paint * 0.15, 0.55 - 0.1 * paint + 0.2 * wear + 0.3 * plate,
                  metal=0.35 * (1 - paint) + 0.5 * wear * (1 - paint), nstr=1.4, ao=1 - 0.5 * plate)


add("cargo_deck_lanes", _cargo_deck, tile=4.0, group="floor")


def armour(kind, seed):
    def fn(n):
        x, y = coords(n)
        cols = 2
        pw = n / cols
        edge = np.minimum(L.periodic_dist(x, pw), L.periodic_dist(y, pw))
        seam = soft(3 - edge, 2.0)
        pid = (np.floor(x / pw) + np.floor(y / pw) * cols).astype(int)
        tone = L.rand_by_id(pid, seed, -0.05, 0.05, cols * cols)
        rp = pw / 4
        rr = np.hypot(L.periodic_dist(x - rp / 2, rp), L.periodic_dist(y - rp / 2, rp))
        rivet = soft(6 - rr, 2.0) * soft(26 - edge, 8.0)
        nz = noise(n, seed + 1, 2.2, fmax=0.05)
        base_c = {"clean": "#8c97a6", "weathered": "#7b8189", "scorched": "#4d4d50", "dark": "#32363e"}[kind]
        v = 1 + tone + 0.05 * nz - 0.3 * seam + 0.06 * rivet
        alb = _tone(hexc(base_c), v)
        rough = 0.45 + 0.05 * nz
        metal = np.full((n, n), 0.75, np.float32)
        h = rivet * 1.0 - seam * 1.4 + 0.1 * nz
        ao = 1 - 0.6 * seam
        if kind in ("weathered", "scorched"):
            chip = np.clip(noise(n, seed + 2, 1.5, fmax=0.1) - 1.0, 0, 3) * soft(14 - edge, 8.0) + np.clip(noise(n, seed + 3, 1.6, fmax=0.08) - 1.6, 0, 3)
            chip = np.clip(chip, 0, 1)
            streak = np.clip(streaks(n, seed + 4, 70, 3.0, vertical=True) - 0.6, 0, 3) * soft(n * 0.3 - L.periodic_dist(y, n), 40)
            streak = np.clip(streak, 0, 1)
            alb = _mix(alb, _col("#5a3a26")[0] * np.ones_like(alb), np.clip(streak * 0.5, 0, 1))
            alb = _mix(alb, _col("#9ea3a8")[0] * np.ones_like(alb), chip * 0.8)
            rough = rough + 0.3 * streak + 0.1 * chip
            metal = metal * (1 - 0.4 * streak) + 0.2 * chip
            h = h - 0.6 * chip
        if kind == "scorched":
            soot = np.clip(noise(n, seed + 5, 2.6, fmax=0.02) * 0.5 + 0.3, 0, 1)
            heat = np.clip(noise(n, seed + 6, 2.2, fmax=0.015) - 1.0, 0, 2) * 0.5
            alb = alb * (1 - 0.6 * soot)[..., None]
            alb = alb + np.stack([heat * 0.12, heat * 0.07, heat * -0.05], 2)
            rough = rough + 0.2 * soot
        return finish(alb, h, rough, ao=ao, metal=metal, nstr=2.0)
    return fn


add("armour_clean", armour("clean", 321), size=1024, tile=3.0, group="hull")
add("armour_weathered", armour("weathered", 322), size=1024, tile=3.0, group="hull")
add("armour_scorched", armour("scorched", 323), size=1024, tile=3.0, group="hull")
add("armour_dark", armour("dark", 324), tile=3.0, group="hull")


def _hull_tiles(n):
    x, y = coords(n)
    cells = 8
    p = n / cells
    edge = np.minimum(L.periodic_dist(x, p), L.periodic_dist(y, p))
    g = soft(3.5 - edge, 2.0)
    tid = (np.floor(x / p) + np.floor(y / p) * cells).astype(int)
    tone = L.rand_by_id(tid, 331, -0.08, 0.08, cells * cells)
    nz = noise(n, 332, 2.4, fmax=0.04)
    alb = _tone(hexc("#1d1f23"), 1 + tone + 0.1 * nz) * (1 - 0.5 * g)[..., None]
    return finish(alb, soft(edge - 3.5, 6.0) * 0.6 - g, 0.55 + 0.2 * g + 0.05 * nz, ao=1 - 0.5 * g, metal=0.0, nstr=1.4)


add("hull_ceramic_tiles", _hull_tiles, tile=2.0, group="hull")


def _pipe_wrap(n):
    x, y = coords(n)
    k = 8
    t = ((x + y) / n * k) % 1
    tape = soft((np.abs(t - 0.5) - 0.42) * (n / k) * 0.7 * -1, 1.8) * 0
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (x + y) / n * k)
    edge = soft(2.2 - np.minimum(t, 1 - t) * (n / k) * 0.7, 1.6)
    nz = noise(n, 341, 1.5, fmax=0.15)
    alb = _tone(hexc("#b9bdc3"), 0.85 + 0.15 * ridge + 0.06 * nz - 0.25 * edge)
    return finish(alb, ridge * 0.6 - edge + 0.3 * nz, 0.35 + 0.15 * edge + 0.05 * nz, metal=0.8, nstr=1.5)


add("pipe_wrap_foil", _pipe_wrap, tile=0.6, group="insulation")


def _foil_gold(n):
    a = noise(n, 351, 1.2, fmax=0.12)
    b = noise(n, 352, 1.8, fmax=0.05)
    alb = _tone(hexc("#c79a2c"), 0.85 + 0.12 * a + 0.08 * b)
    return finish(alb, a * 0.9 + b * 0.5, 0.28 + 0.06 * a, metal=1.0, nstr=1.4)


add("foil_gold_mylar", _foil_gold, tile=0.8, group="insulation")


def _blanket(n):
    x, y = coords(n)
    cells = 6
    p = n / cells
    pill = np.clip(1 - 2 * np.maximum(L.periodic_dist(x, p) / p * -1 + 0.5, L.periodic_dist(y, p) / p * -1 + 0.5) * 0, 0, 1)
    ex = soft(L.periodic_dist(x, p) - 2.5, 5.0)
    ey = soft(L.periodic_dist(y, p) - 2.5, 5.0)
    puff = ex * ey
    nz = noise(n, 361, 1.8, fmax=0.1)
    alb = _tone(hexc("#d9d8d2"), 0.8 + 0.2 * puff + 0.04 * nz)
    del pill
    return finish(alb, puff * 1.4 + 0.1 * nz, 0.9, ao=0.5 + 0.5 * puff, nstr=1.6, hblur=1.3)


add("insulation_blanket", _blanket, tile=1.0, group="insulation")


# ---------------------------------------------------------------- department sheet-metal panels
def dept_panel(color, accent, seed, rough=0.42):
    def fn(n):
        x, y = coords(n)
        pw, ph = n / 2, n / 4
        edge = np.minimum(L.periodic_dist(x, pw), L.periodic_dist(y, ph))
        seam = soft(2.6 - edge, 1.8)
        inset = soft(edge - 2.6, 3.0) - soft(edge - 12, 4.0)
        pid = (np.floor(x / pw) + np.floor(y / ph) * 2).astype(int)
        tone = L.rand_by_id(pid, seed, -0.03, 0.03, 8)
        nz = noise(n, seed + 1, 2.2, fmax=0.04)
        fx = L.periodic_dist(x - pw / 2 + 0.0, pw)
        fy = L.periodic_dist(y - ph / 2, ph)
        corner = np.hypot(np.abs(L.periodic_dist(x, pw)) - 0, 0)
        del fx, fy, corner
        bolt = soft(4.5 - np.hypot(L.periodic_dist(x, pw) - 14, L.periodic_dist(y, ph) - 14), 1.8)
        band = soft(n * 0.014 - np.abs(((y / n) % 0.25) * n - n * 0.04), 1.8)
        dirt = np.clip(noise(n, seed + 2, 2.0, fmax=0.03) * 0.5 + 0.2, 0, 1) * soft(20 - edge, 14)
        alb = _tone(hexc(color), 1 + tone + 0.04 * nz - 0.3 * seam - 0.12 * dirt + 0.08 * bolt)
        alb = _mix(alb, _col(accent)[0] * np.ones_like(alb), band * 0.9 * (1 - seam))
        return finish(alb, bolt * 0.8 + inset * 0.4 - seam * 1.5 + 0.05 * nz, rough + 0.2 * dirt + 0.2 * seam,
                      ao=1 - 0.55 * seam - 0.2 * dirt, metal=0.25, nstr=1.8)
    return fn


for _nm, _c, _a, _sd in (("panel_eng_orange", "#c9722a", "#2a2d33", 401), ("panel_med_teal", "#4fa8a4", "#e8eef0", 402),
                         ("panel_sec_red", "#a83830", "#2a2d33", 403), ("panel_sci_violet", "#6a5aa6", "#e8eef0", 404),
                         ("panel_cmd_blue", "#3f6aa6", "#d8dde4", 405), ("panel_life_green", "#4f8f5f", "#e8eef0", 406),
                         ("panel_cargo_yellow", "#c9a52a", "#2a2d33", 407), ("panel_crew_beige", "#b9a98a", "#6a5a44", 408),
                         ("panel_white", "#dfe3e6", "#7b8590", 409), ("panel_grey", "#8a9099", "#2a2d33", 410)):
    add(_nm, dept_panel(_c, _a, _sd), tile=2.0, group="panel")


# ---------------------------------------------------------------- laminates
def laminate(color, seed, rough=0.36, grain=0.02):
    def fn(n):
        f = noise(n, seed, 1.2, fmax=0.2)
        m = noise(n, seed + 1, 2.4, fmax=0.015)
        alb = _tone(hexc(color), 1 + grain * f + 0.015 * m)
        return finish(alb, 0.1 * f, rough + 0.03 * f, nstr=0.4)
    return fn


add("laminate_white", laminate("#e7eaeb", 421), size=256, tile=1.0, group="laminate")
add("laminate_clinic_blue", laminate("#c4dbe6", 422), size=256, tile=1.0, group="laminate")
add("laminate_grey", laminate("#a9aeb4", 423, 0.4), size=256, tile=1.0, group="laminate")
add("laminate_beige", laminate("#d8ccb4", 424, 0.4), size=256, tile=1.0, group="laminate")
add("laminate_black", laminate("#26282c", 425, 0.3), size=256, tile=1.0, group="laminate")


# ---------------------------------------------------------------- hydroponics / organic
def _grass(n):
    a = streaks(n, 431, 5, 1.2, vertical=True)
    b = noise(n, 432, 2.0, fmax=0.06)
    c = noise(n, 433, 2.6, fmax=0.015)
    base = _mix(_col("#2f5a1f")[0] * np.ones((n, n, 3), np.float32), _col("#7fae3c")[0] * np.ones((n, n, 3), np.float32),
                np.clip(0.5 + 0.25 * a + 0.12 * b, 0, 1))
    alb = base * (1 + 0.1 * c)[..., None]
    return finish(alb, a * 0.7 + 0.2 * b, 0.75, ao=0.6 + 0.4 * np.clip(0.5 + 0.2 * a, 0, 1), nstr=1.0, hblur=1.2)


add("grass", _grass, size=256, tile=1.0, group="organic")


def _moss(n):
    f1, f2, cid = voronoi(n, 36, 441, 1.0)
    a = noise(n, 442, 1.6, fmax=0.1)
    b = noise(n, 443, 2.4, fmax=0.02)
    t = np.clip(0.5 + 0.25 * a + 0.15 * (1 - f1), 0, 1)
    base = _mix(_col("#27481a")[0] * np.ones((n, n, 3), np.float32), _col("#6c9a3a")[0] * np.ones((n, n, 3), np.float32), t)
    return finish(base * (1 + 0.08 * b)[..., None], (1 - f1) * 0.9 + 0.3 * a, 0.9, ao=0.6 + 0.4 * t, nstr=1.3, hblur=1.3)


add("moss", _moss, size=256, tile=1.0, group="organic")


def _soil(n):
    f1, f2, cid = voronoi(n, 50, 451, 1.0)
    pebble = soft((0.25 - f1) * (n / 50) * 1.2, 2.0) * (L.rand_by_id(cid, 452, 0, 1, 2500) < 0.3)
    a = noise(n, 453, 1.6, fmax=0.1)
    b = noise(n, 454, 2.4, fmax=0.02)
    alb = _tone(hexc("#4a3524"), 1 + 0.12 * a + 0.1 * b)
    alb = _mix(alb, _col("#8a7b6a")[0] * np.ones_like(alb), pebble * 0.6)
    return finish(alb, 0.5 * a + pebble * 1.0, 0.92 - 0.1 * pebble, ao=1 - 0.2 * (1 - pebble) * np.clip(a, 0, 1), nstr=1.6, hblur=1.3)


add("soil", _soil, size=256, tile=1.0, group="organic")


def _gravel(n):
    f1, f2, cid = voronoi(n, 28, 461, 0.9)
    r = L.rand_by_id(cid, 462, 0.4, 0.95, 28 * 28)
    chip = soft((1 - f1 * 1.9) * (n / 28) * 0.5, 2.5)
    nz = noise(n, 463, 2.0, fmax=0.1)
    alb = _tone(hexc("#8d8a84"), r + 0.05 * nz) * (0.5 + 0.5 * chip)[..., None]
    return finish(alb, chip * 1.2 + (r - 0.6), 0.85, ao=0.4 + 0.6 * chip, nstr=1.6, hblur=1.3)


add("gravel", _gravel, size=256, tile=1.0, group="organic")


# ============================================================ neutral prop sets (tint friendly)
def _neutral(alb_v, h, rough_rel, ao=None, nstr=1.0):
    n = alb_v.shape[0]
    alb = np.stack([alb_v] * 3, 2)
    a, nrm, orm = finish(alb, h, rough_rel, ao=ao, metal=0.0, nstr=nstr, toksvig=0.0, rough_range=(0.5, 1.0))
    orm[..., 1] = np.clip(orm[..., 1], 0.6, 1.0)
    return a, nrm, orm


def p_wood(seed, rings):
    def fn(n):
        x, y = coords(n)
        wp = noise(n, seed, 2.2, fmax=0.012)
        fib = streaks(n, seed + 1, 50, 0.9, vertical=True)
        t = (x / n * rings + wp * 0.4)
        r = (t * 2) % 1
        ring = np.clip(np.abs(r - 0.5) * 2, 0, 1) ** 1.5
        v = 0.86 - 0.12 * ring + 0.025 * fib
        return _neutral(np.clip(v, 0, 1), -0.5 * fib - 0.3 * ring, 0.9 + 0.04 * fib, ao=1 - 0.1 * ring, nstr=0.8)
    return fn


add("p_wood_fine", p_wood(501, 9), size=256, tile=0.5, group="prop", neutral=True)
add("p_wood_coarse", p_wood(502, 5), size=256, tile=0.5, group="prop", neutral=True)


def _p_leather(n):
    f1, f2, cid = voronoi(n, 30, 511, 1.0)
    crease = np.clip(1 - (f2 - f1) * 4.0, 0, 1)
    puff = soft((f2 - f1) * (n / 30) - 1.5, 5.0)
    return _neutral(0.9 - 0.2 * crease, puff, 0.85 + 0.1 * crease, ao=1 - 0.3 * crease, nstr=1.2)


add("p_leather", _p_leather, size=256, tile=0.4, group="prop", neutral=True)


def _p_weave(n):
    x, y = coords(n)
    k = 32
    i, j = np.floor(x / n * k), np.floor(y / n * k)
    over = (i + j) % 2 == 0
    th = np.where(over, np.sin(np.pi * ((x / n * k) % 1)) ** 0.6, np.sin(np.pi * ((y / n * k) % 1)) ** 0.6)
    rnd = np.where(over, L.rand_by_id(i.astype(int) % 256, 521, -0.06, 0.06, 256), L.rand_by_id(j.astype(int) % 256, 522, -0.06, 0.06, 256))
    return _neutral(np.clip(0.72 + 0.2 * th + rnd, 0, 1), th, 0.98, ao=0.6 + 0.4 * th, nstr=1.2)


add("p_weave", _p_weave, size=256, tile=0.3, group="prop", neutral=True)


def _p_brushed(n):
    s = streaks(n, 531, 45, 0.8)
    s2 = streaks(n, 532, 12, 0.7)
    m = noise(n, 533, 2.5, fmax=0.01)
    a, nrm, orm = finish(np.stack([0.9 + 0.02 * s + 0.012 * s2 + 0.02 * m] * 3, 2), 0.5 * s + 0.3 * s2, 0.9 + 0.05 * s2, nstr=0.3,
                         hblur=0.7, toksvig=0.0, rough_range=(0.5, 1.0))
    return a, nrm, orm


add("p_brushed", _p_brushed, size=256, tile=0.5, group="prop", neutral=True)


def _p_scratched(n):
    sc = np.clip(streaks(n, 541, 80, 0.6) - 1.5, 0, 3) + np.clip(streaks(n, 542, 60, 0.6, vertical=True) - 1.8, 0, 3)
    nz = noise(n, 543, 2.2, fmax=0.05)
    return _neutral(np.clip(0.92 + 0.03 * nz - 0.06 * sc, 0, 1), -sc * 0.8 + 0.1 * nz, 0.9 + 0.05 * sc, ao=1 - 0.05 * sc, nstr=0.8)


add("p_scratched", _p_scratched, size=256, tile=0.8, group="prop", neutral=True)


def _p_concrete(n):
    a = noise(n, 551, 1.8, fmax=0.08)
    b = noise(n, 552, 2.8, fmax=0.01)
    pore = np.clip(noise(n, 553, 0.6, fmax=0.18) - 1.9, 0, 3)
    return _neutral(np.clip(0.88 + 0.04 * a + 0.05 * b - 0.2 * pore, 0, 1), 0.3 * a - pore, 0.95 - 0.05 * pore, ao=1 - 0.4 * pore, nstr=1.2)


add("p_concrete", _p_concrete, size=256, tile=1.5, group="prop", neutral=True)


def _p_cardboard(n):
    x, y = coords(n)
    corr = 0.5 + 0.5 * np.cos(2 * np.pi * x / (n / 8))
    fib = streaks(n, 561, 20, 0.8)
    nz = noise(n, 562, 1.4, fmax=0.2)
    return _neutral(np.clip(0.82 + 0.1 * corr + 0.04 * fib + 0.03 * nz, 0, 1), corr * 1.0 + 0.2 * fib, 0.97, ao=0.7 + 0.3 * corr, nstr=1.2)


add("p_cardboard", _p_cardboard, size=256, tile=0.4, group="prop", neutral=True)


def _p_foam(n):
    f1, f2, cid = voronoi(n, 44, 571, 1.0)
    pit = np.clip(1 - f1 * 3, 0, 1)
    nz = noise(n, 572, 1.2, fmax=0.2)
    return _neutral(np.clip(0.9 - 0.15 * pit + 0.03 * nz, 0, 1), -pit + 0.1 * nz, 0.98, ao=1 - 0.3 * pit, nstr=1.2)


add("p_foam", _p_foam, size=256, tile=0.4, group="prop", neutral=True)


def _p_rubber(n):
    nz = noise(n, 581, 1.2, fmax=0.2)
    nz2 = noise(n, 582, 2.0, fmax=0.04)
    return _neutral(np.clip(0.9 + 0.05 * nz + 0.03 * nz2, 0, 1), 0.4 * nz, 0.97, nstr=0.8)


add("p_rubber", _p_rubber, size=256, tile=0.4, group="prop", neutral=True)


def _p_plastic(n):
    nz = noise(n, 591, 1.0, fmax=0.18)
    m = noise(n, 592, 2.4, fmax=0.015)
    return _neutral(np.clip(0.93 + 0.015 * nz + 0.02 * m, 0, 1), 0.3 * nz, 0.92 + 0.03 * nz, nstr=0.5)


add("p_plastic", _p_plastic, size=256, tile=0.5, group="prop", neutral=True)


def _p_paint(n):
    nz = noise(n, 601, 1.0, fmax=0.16)
    m = noise(n, 602, 2.2, fmax=0.02)
    chip = np.clip(noise(n, 603, 0.5, fmax=0.2) - 2.1, 0, 3)
    return _neutral(np.clip(0.95 + 0.02 * nz + 0.03 * m - 0.08 * chip, 0, 1), 0.2 * nz - chip * 0.4, 0.9 + 0.04 * nz + 0.05 * chip,
                    nstr=0.6)


add("p_paint", _p_paint, size=256, tile=0.6, group="prop", neutral=True)


def _p_ceramic(n):
    f1, f2, cid = voronoi(n, 12, 611, 1.0)
    craze = np.clip(1 - (f2 - f1) * 14, 0, 1) * 0.5
    m = noise(n, 612, 2.4, fmax=0.015)
    return _neutral(np.clip(0.96 - 0.04 * craze + 0.02 * m, 0, 1), 0.1 * m, 0.88 + 0.05 * craze, nstr=0.3)


add("p_ceramic", _p_ceramic, size=256, tile=0.6, group="prop", neutral=True)


def _p_leaf(n):
    x, y = coords(n)
    f = noise(n, 621, 1.8, fmax=0.06)
    vein = soft(1.6 - L.periodic_dist(x, n / 2), 1.6) * 0.8 + soft(1.2 - L.periodic_dist(y - x * 0.5, n / 4) * 0.8, 1.6) * 0.5
    fine = noise(n, 622, 1.0, fmax=0.2)
    return _neutral(np.clip(0.88 + 0.06 * f + 0.1 * np.clip(vein, 0, 1) + 0.02 * fine, 0, 1), -vein * 0.5 + 0.2 * fine, 0.92 - 0.07 * vein, nstr=1.0)


add("p_leaf", _p_leaf, size=256, tile=0.3, group="prop", neutral=True)


def _p_soil(n):
    f1, f2, cid = voronoi(n, 40, 631, 1.0)
    a = noise(n, 632, 1.6, fmax=0.1)
    pebble = soft((0.28 - f1) * (n / 40) * 1.2, 2.0) * (L.rand_by_id(cid, 633, 0, 1, 1600) < 0.3)
    return _neutral(np.clip(0.86 + 0.07 * a + 0.08 * pebble, 0, 1), 0.5 * a + pebble, 0.97, ao=1 - 0.2 * np.clip(a, 0, 1), nstr=1.5)


add("p_soil", _p_soil, size=256, tile=0.6, group="prop", neutral=True)


def _p_panel(n):
    x, y = coords(n)
    edge = np.minimum(L.periodic_dist(x, n / 2), L.periodic_dist(y, n / 2))
    seam = soft(2.4 - edge, 1.8)
    nz = noise(n, 641, 2.2, fmax=0.04)
    bolt = soft(4 - np.hypot(L.periodic_dist(x, n / 2) - 14, L.periodic_dist(y, n / 2) - 14), 1.6)
    return _neutral(np.clip(0.93 + 0.03 * nz - 0.3 * seam + 0.04 * bolt, 0, 1), -1.4 * seam + 0.7 * bolt, 0.9 + 0.08 * seam,
                    ao=1 - 0.5 * seam, nstr=1.6)


add("p_panel_lines", _p_panel, size=256, tile=1.0, group="prop", neutral=True)


def _p_metal_hex(n):
    s = streaks(n, 651, 25, 0.9)
    nz = noise(n, 652, 2.2, fmax=0.04)
    return _neutral(np.clip(0.92 + 0.025 * s + 0.03 * nz, 0, 1), 0.3 * s + 0.2 * nz, 0.9 + 0.05 * s, nstr=0.6)


add("p_metal_satin", _p_metal_hex, size=256, tile=0.8, group="prop", neutral=True)


# ============================================================ build
def build_one(name):
    ent = REG[name]
    n = ent["size"]
    alb, nrm, orm = ent["fn"](n)
    assert alb.shape == (n, n, 3), (name, alb.shape)
    return name, alb, nrm, orm


def _work(name):
    n, a, nr, o = build_one(name)
    q = lambda x: np.round(np.clip(x, 0, 1) * 255).astype(np.uint8)
    return n, q(a), q(nr), q(o)


def make_ext_surfaces(outdir, names=None, jobs=None):
    """Generate every extended surface into <outdir>/surfaces and write surfaces/index.json."""
    sdir = os.path.join(outdir, "surfaces")
    os.makedirs(sdir, exist_ok=True)
    names = names or list(REG)
    jobs = jobs or min(4, os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for name, a, nr, o in ex.map(_work, names, chunksize=2):
            L.write_png(os.path.join(sdir, name + "_albedo.png"), a / 255.0)
            L.write_png(os.path.join(sdir, name + "_normal.png"), nr / 255.0, data=True)
            L.write_png(os.path.join(sdir, name + "_orm.png"), o / 255.0, data=True)
    write_index(outdir)


def index_entries():
    """Metadata of every extended surface (pure python; also used by the tests and the themes)."""
    return {k: {"size": v["size"], "tile_m": v["tile_m"], "group": v["group"], "neutral": v["neutral"]} for k, v in REG.items()}


def write_index(outdir):
    from . import textures as T
    from . import textures_arch as TA
    idx = {}
    for k in T.SURFACES:
        idx[k] = {"size": 512, "tile_m": 2.0, "group": "legacy", "neutral": False}
    for k, (_, s) in TA.ARCH_SURFACES.items():
        idx[k] = {"size": s, "tile_m": 4.0 if s >= 1024 else 2.0, "group": "legacy", "neutral": False}
    idx.update(index_entries())
    with open(os.path.join(outdir, "surfaces", "index.json"), "w") as fh:
        json.dump(idx, fh, indent=0, sort_keys=True)
