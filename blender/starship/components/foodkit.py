"""Organic modelling helpers for the food and drink models (surfaces of revolution, noise displacement,
tubes along curves, scatter, UV projection).  Pure bmesh; everything works in the game frame (+Y up, +Z front).

Typical use (inside a family function):

    lathe(m, [(0, 0), (0.1, 0), (0.11, 0.03), (0, 0.03)], (0, y, 0), "tex:bread_crust", seg=24, disp=(0.004, 40))
    blob(m, (0.05, 0.04, 0.05), (0, 0.05, 0), "tex:tomato_skin")
    tube3(m, [(0, 0, 0), (0.1, 0.02, 0)], 0.01, "tex:sausage")
"""
import math
import zlib

from ..kit import g2b, register_material

try:
    import bmesh  # noqa: F401
    from mathutils import Vector, noise as _mn
except ImportError:  # pragma: no cover - bare python (--check): geometry is never built
    Vector = _mn = None

PI = math.pi
TAU = 2 * math.pi

# ------------------------------------------------------------------ shared plain materials
_MATS = {
    # name: (hex, metallic, roughness)
    "f_white": ("#f1efe8", 0.0, 0.25), "f_plate": ("#ecebe4", 0.0, 0.2), "f_plate_blue": ("#3b5f8f", 0.0, 0.25),
    "f_plate_dark": ("#2b2f36", 0.0, 0.3), "f_plate_sage": ("#9fb09a", 0.0, 0.3), "f_plate_cream": ("#e8dcc0", 0.0, 0.3),
    "f_plate_red": ("#a8362c", 0.0, 0.3),
    "f_steel": ("#c4c8cc", 0.95, 0.28), "f_steel_dark": ("#7a8088", 0.9, 0.4), "f_tray": ("#8f969e", 0.85, 0.35),
    "f_tray_blue": ("#3d5c80", 0.1, 0.5), "f_tray_grey": ("#7b818a", 0.1, 0.55),
    "f_cream": ("#f4ead0", 0.0, 0.45), "f_butter": ("#f2dc78", 0.0, 0.4), "f_yolk": ("#e8a010", 0.0, 0.18),
    "f_icing_pink": ("#f2a2c0", 0.0, 0.35), "f_icing_white": ("#faf6ee", 0.0, 0.35), "f_icing_choc": ("#3a1d10", 0.0, 0.3),
    "f_caramel": ("#b8701c", 0.0, 0.25), "f_gelatin": ("#d83a50", 0.0, 0.1), "f_jelly_green": ("#4fbf5a", 0.0, 0.1),
    "f_ice_cream_van": ("#f6e8c0", 0.0, 0.5), "f_ice_cream_straw": ("#f4a8b8", 0.0, 0.5),
    "f_ice_cream_choc": ("#4a2a1a", 0.0, 0.5), "f_ice_cream_mint": ("#a8e0c0", 0.0, 0.5),
    "f_cherry": ("#8a0a18", 0.0, 0.12), "f_cheese_yellow": ("#f0c030", 0.0, 0.4), "f_cheese_white": ("#f4eedc", 0.0, 0.45),
    "f_bun_seed": ("#efe0b0", 0.0, 0.5), "f_olive": ("#6a7a20", 0.0, 0.3), "f_olive_black": ("#1a1a14", 0.0, 0.3),
    "f_onion": ("#e8d4e0", 0.0, 0.4), "f_tomato": ("#d03020", 0.0, 0.3), "f_nori": ("#12201a", 0.0, 0.5),
    "f_salmon": ("#f08050", 0.0, 0.3), "f_tuna": ("#c0303a", 0.0, 0.3), "f_shrimp": ("#f0a080", 0.0, 0.3),
    "f_ginger": ("#f2b8c0", 0.0, 0.4), "f_wasabi": ("#8aba3a", 0.0, 0.5), "f_soy": ("#2a1208", 0.0, 0.1),
    "f_tortilla": ("#e8cc8a", 0.0, 0.7), "f_dough": ("#f0e4c0", 0.0, 0.6), "f_scallion": ("#6aba3a", 0.0, 0.5),
    "f_egg_white": ("#fbf9f1", 0.0, 0.2), "f_sesame": ("#f0e6c8", 0.0, 0.5), "f_pepper_flake": ("#802010", 0.0, 0.6),
    "f_herb": ("#3a7a28", 0.0, 0.6), "f_foil": ("#c8ccd2", 0.9, 0.3), "f_foil_gold": ("#d0a848", 0.9, 0.3),
    "f_cork": ("#b89060", 0.0, 0.8), "f_plastic_clear_cap": ("#2a6ac8", 0.0, 0.4), "f_cap_red": ("#c02a22", 0.0, 0.4),
    "f_cap_green": ("#2a8a40", 0.0, 0.4), "f_cap_black": ("#1a1a1c", 0.0, 0.4), "f_cap_gold": ("#c8a030", 0.8, 0.3),
    "f_wax_red": ("#8a1818", 0.0, 0.3), "f_label_cream": ("#eee6cf", 0.0, 0.6), "f_straw": ("#e84a6a", 0.0, 0.4),
    "f_straw_green": ("#3aa860", 0.0, 0.4), "f_napkin": ("#c0392b", 0.0, 0.9), "f_cardboard": ("#b08a58", 0.0, 0.9),
    "f_paper": ("#f4f0e4", 0.0, 0.9), "f_wood_light": ("#d0a468", 0.0, 0.6), "f_wood_dark": ("#5a3820", 0.0, 0.55),
    "f_hay": ("#d8b858", 0.0, 0.8), "f_stem": ("#4a6a22", 0.0, 0.6), "f_stem_brown": ("#5a4020", 0.0, 0.8),
    "f_lemon_flesh": ("#f4e060", 0.0, 0.3), "f_pomegranate_seed": ("#b01830", 0.0, 0.2),
    "f_pumpkin_seed": ("#d8c890", 0.0, 0.5), "f_corn_yellow": ("#f0c828", 0.0, 0.4), "f_bean_green": ("#5a9a30", 0.0, 0.5),
    "f_pea": ("#6aaa38", 0.0, 0.4), "f_carrot_cut": ("#f08a20", 0.0, 0.4), "f_mushroom_cut": ("#e8d8c0", 0.0, 0.6),
    "f_chip": ("#e4b858", 0.0, 0.6), "f_fry": ("#efc660", 0.0, 0.6), "f_nut": ("#a87a42", 0.0, 0.7),
    "f_honey": ("#d89a20", 0.0, 0.15), "f_chocolate_dark": ("#2c1810", 0.0, 0.35), "f_chocolate_milk": ("#6a3a20", 0.0, 0.35),
    "f_wrapper_gold": ("#d4a840", 0.85, 0.3), "f_wrapper_red": ("#b02a2a", 0.7, 0.3), "f_wrapper_blue": ("#2a4a9a", 0.7, 0.3),
    "f_pouch_edge": ("#a0a6ae", 0.9, 0.35), "f_rubber_grey": ("#5a5e64", 0.0, 0.7), "f_glass_rim": ("#e8f0f4", 0.0, 0.1),
}
for _n, (_h, _me, _ro) in _MATS.items():
    register_material(_n, _h, _me, _ro)

# transparent liquids / glass (alpha < 1 -> blended)
for _n, _h, _a in (("f_glass", "#cfe0e8", 0.09), ("f_glass_green", "#5a8a52", 0.45), ("f_glass_brown", "#5a3416", 0.6),
                   ("f_glass_dark", "#1e2a20", 0.7), ("f_water", "#bfe0f0", 0.45), ("f_juice_orange", "#f59a24", 0.82),
                   ("f_juice_apple", "#d8b040", 0.7), ("f_milk", "#f8f6f0", 0.97), ("f_wine_red", "#4a0a1c", 0.88),
                   ("f_wine_white", "#e8d878", 0.6), ("f_champagne", "#e8d070", 0.55), ("f_beer", "#d89818", 0.85),
                   ("f_stout", "#1c0f08", 0.96), ("f_whisky", "#b8681c", 0.8), ("f_lemonade", "#f0e890", 0.7),
                   ("f_tea_iced", "#a85a18", 0.8), ("f_martini", "#e8f0e8", 0.45), ("f_margarita", "#d4e888", 0.7),
                   ("f_mojito", "#d8f0c8", 0.55), ("f_cranberry", "#a01830", 0.85), ("f_blue_curacao", "#2aa8e8", 0.8),
                   ("f_coffee_iced", "#4a2a14", 0.9), ("f_clear_plastic", "#dceaf2", 0.14), ("f_olive_oil", "#b8a020", 0.75),
                   ("f_jelly_clear", "#f0b0c0", 0.6), ("f_ice_cube", "#e6f4fa", 0.5), ("f_blue_lagoon", "#18b4e8", 0.78),
                   ("f_cocoa_liquid", "#3a1c0e", 0.97), ("f_green_smoothie", "#7ab83a", 0.92), ("f_pink_smoothie", "#e87aa0", 0.92),
                   ("f_tea_hot", "#b86a20", 0.85), ("f_bubble_milk_tea", "#c8a074", 0.9), ("f_soda_dark", "#2a1208", 0.92), ("f_champagne_bubble", "#f4ecb0", 0.5)):
    register_material(_n, _h, 0.0, 0.1, alpha=_a)


# ------------------------------------------------------------------ noise
def fbm(x, y, z, seed=0.0, octaves=3):
    """Deterministic fractal noise in roughly -1..1."""
    v, a, f = 0.0, 1.0, 1.0
    tot = 0.0
    for _ in range(octaves):
        v += a * _mn.noise(Vector((x * f + seed * 17.3, y * f - seed * 5.1, z * f + seed * 9.7)))
        tot += a
        a *= 0.5
        f *= 2.0
    return v / tot


def _rotm(rot):
    rx, ry, rz = rot
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    # R = Rz @ Ry @ Rx
    return ((cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx),
            (sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx),
            (-sy, cy * sx, cy * cx))


def _rot(mm, p):
    return (mm[0][0] * p[0] + mm[0][1] * p[1] + mm[0][2] * p[2],
            mm[1][0] * p[0] + mm[1][1] * p[1] + mm[1][2] * p[2],
            mm[2][0] * p[0] + mm[2][1] * p[1] + mm[2][2] * p[2])


# ------------------------------------------------------------------ uv
def _uv_for(mode, p, nrm, ext, tile, cy):
    """UV of local point p (game frame) for projection `mode`.  ext = (extent_xz, y0, y1)."""
    R, y0, y1 = ext
    x, y, z = p
    if mode == "top":
        return (x / (2 * R) + 0.5) * tile[0], (0.5 - z / (2 * R)) * tile[1]
    if mode == "cyl":
        return (math.atan2(z, x) / TAU + 0.5) * tile[0], ((y - y0) / max(y1 - y0, 1e-6)) * tile[1]
    if mode == "sph":
        d = math.sqrt(x * x + (y - cy) ** 2 + z * z) or 1e-6
        return (math.atan2(z, x) / TAU + 0.5) * tile[0], (0.5 + math.asin(max(-1, min(1, (y - cy) / d))) / PI) * tile[1]
    # box: dominant normal axis
    ax, ay, az = abs(nrm[0]), abs(nrm[1]), abs(nrm[2])
    s = 1 / (2 * R)
    vy = (y - y0) / max(y1 - y0, 1e-6)
    if ay >= ax and ay >= az:
        return (x * s + 0.5) * tile[0], (z * s + 0.5) * tile[1]
    if ax >= az:
        return (z * s + 0.5) * tile[0], vy * tile[1]
    return (x * s + 0.5) * tile[0], vy * tile[1]


def _assign_uv(bm, faces, local, mode, ext, tile, cy):
    layer = bm.loops.layers.uv.verify()
    for f in faces:
        nl = (0.0, 0.0, 0.0)
        if mode == "box" or mode == "auto":
            n = f.normal
            nl = (n.x, n.z, -n.y)      # blender -> game
        fm = mode
        if mode == "auto":
            fm = "top" if nl[1] > 0.6 else "cyl"
        uvs = []
        cu = None
        for lp in f.loops:
            uvs.append(_uv_for(fm, local[lp.vert], nl, ext, tile, cy))
        if fm in ("cyl", "sph"):
            # seam fix and pole handling
            us = []
            for lp, uv in zip(f.loops, uvs):
                p = local[lp.vert]
                if abs(p[0]) < 1e-7 and abs(p[2]) < 1e-7:
                    us.append(None)
                else:
                    us.append(uv[0])
            good = [u for u in us if u is not None]
            if good:
                if max(good) - min(good) > 0.5 * tile[0]:
                    good_fix = [u + tile[0] if u < 0.5 * tile[0] else u for u in good]
                    it = iter(good_fix)
                    us = [None if u is None else next(it) for u in us]
                cu = sum(u for u in us if u is not None) / len([u for u in us if u is not None])
            uvs = [(cu if u is None else u, uv[1]) for u, uv in zip(us, uvs)]
        for lp, uv in zip(f.loops, uvs):
            lp[layer].uv = uv


# ------------------------------------------------------------------ surfaces of revolution
def lathe(m, prof, pos=(0, 0, 0), mat="f_plate", seg=24, rot=(0, 0, 0), scale=(1, 1, 1), uv=None, disp=None, warp=None,
          tile=(1, 1), arc=TAU, ext=None, a0=0.0, closed=False):
    """Surface of revolution about the local Y axis.

    prof : [(r, y), ...] walking the outline *clockwise* in the (r right, y up) plane (outside on the right):
           e.g. a solid disc: [(0,0),(R,0),(R,h),(0,h)].  r == 0 points collapse to a single pole vertex.
    uv   : None | 'cyl' | 'top' | 'sph' | 'box' | 'auto' projection (required for tex: materials)
    disp : (amplitude, frequency[, octaves]) radial noise displacement (metres) about the local centre
    warp : callable (x, y, z) -> (x, y, z) applied after scale and displacement (bends, wobble)
    arc  : sweep angle (default full turn); partial arcs leave an open seam (used for crescents)
    a0   : start angle of the sweep (a0 = pi/4 with seg = 4 gives an axis-aligned square prism)
    closed : the profile is a closed loop (donut / torus section): last point connects back to the first
    """
    bm = m.cur["bm"]
    mi = m._mi(mat)
    mm = _rotm(rot)
    full = abs(arc - TAU) < 1e-6
    n = seg if full else seg + 1
    ys = [p[1] for p in prof]
    cy = (min(ys) + max(ys)) / 2
    rmax = max(p[0] for p in prof) or 1e-3
    sd = (zlib.crc32(mat.encode()) % 997) / 100.0 + pos[0] * 13 + pos[1] * 7 + pos[2] * 3 if disp else 0.0
    local = {}
    rings = []

    def mk(x, y, z):
        if disp:
            amp, fr = disp[0], disp[1]
            octv = disp[2] if len(disp) > 2 else 3
            d = math.sqrt(x * x + (y - cy) ** 2 + z * z) or 1e-6
            k = amp * fbm(x * fr, (y - cy) * fr, z * fr, sd, octv) / d
            x, y, z = x + x * k * 1.0, y + (y - cy) * k, z + z * k
        x, y, z = x * scale[0], y * scale[1], z * scale[2]
        if warp:
            x, y, z = warp(x, y, z)
        return x, y, z

    for (r, y) in prof:
        if r < 1e-7:
            pts = [(0.0, y, 0.0)]
        else:
            pts = [(r * math.cos(a0 + arc * i / seg), y, r * math.sin(a0 + arc * i / seg)) for i in range(n)]
        ring = []
        for q in pts:
            lq = q
            gx, gy, gz = mk(*q)
            gx, gy, gz = _rot(mm, (gx, gy, gz))
            v = bm.verts.new(g2b((gx + pos[0], gy + pos[1], gz + pos[2])))
            local[v] = lq
            ring.append(v)
        rings.append(ring)
    faces = []
    for j in range(len(rings) if closed else len(rings) - 1):
        a, b = rings[j], rings[(j + 1) % len(rings)]
        for i in range(seg if full else seg):
            i2 = (i + 1) % n
            quad = []
            for v in (a[i if len(a) > 1 else 0], a[i2 if len(a) > 1 else 0], b[i2 if len(b) > 1 else 0], b[i if len(b) > 1 else 0]):
                if v not in quad:
                    quad.append(v)
            if len(quad) < 3:
                continue
            try:
                faces.append(bm.faces.new(list(reversed(quad))))
            except ValueError:
                pass
    for f in faces:
        f.material_index = mi
    if uv:
        _assign_uv(bm, faces, local, uv, ext or (rmax, min(ys), max(ys)), tile, cy)
    return faces


def slab(m, sx, sy, sz, pos=(0, 0, 0), mat="f_white", uv="box", rnd=0.002, rot=(0, 0, 0), disp=None, warp=None, tile=(1, 1)):
    """Axis-aligned rounded box (full size sx, sy, sz, base at pos.y) with box UVs: slices, bars, blocks of cheese ..."""
    c = min(rnd, sy * 0.4)
    k = 0.7071
    prof = [(0.0, 0.0), (k - c * 1.4, 0.0), (k, c), (k, sy - c), (k - c * 1.4, sy), (0.0, sy)]
    return lathe(m, prof, pos, mat, 4, rot, (sx, 1.0, sz), uv, disp, warp, tile, ext=(0.5, 0.0, sy), a0=PI / 4)


def extrude(m, pts, h, pos=(0, 0, 0), top="f_white", side=None, bottom=None, rot=(0, 0, 0), uvs=1.0):
    """Extrude a 2D outline [(x, z), ...] along +Y by h (base at pos), with UVs: planar on the caps, perimeter x height on the sides.
    top / side / bottom are materials (side and bottom default to `top`).  rot rotates the finished solid about pos."""
    bm = m.cur["bm"]
    side = side or top
    bottom = bottom or top
    mm = _rotm(rot)
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    P = list(pts) if area < 0 else list(reversed(pts))      # clockwise seen from +Y: the top face then points up
    xs = [p[0] for p in P]
    zs = [p[1] for p in P]
    cx, cz = (min(xs) + max(xs)) / 2, (min(zs) + max(zs)) / 2

    def V(x, y, z):
        gx, gy, gz = _rot(mm, (x, y, z))
        return bm.verts.new(g2b((gx + pos[0], gy + pos[1], gz + pos[2])))
    lo = [V(x, 0.0, z) for x, z in P]
    hi = [V(x, h, z) for x, z in P]
    layer = bm.loops.layers.uv.verify()
    faces = []

    def face(vs, mat, uvl):
        try:
            f = bm.faces.new(vs)
        except ValueError:
            return
        f.material_index = m._mi(mat)
        for lp, uv in zip(f.loops, uvl):
            lp[layer].uv = uv
        faces.append(f)
    face(list(reversed(hi)), top, [((x - cx) * uvs + 0.5, (z - cz) * uvs + 0.5) for x, z in reversed(P)])
    face(lo, bottom, [((x - cx) * uvs + 0.5, (z - cz) * uvs + 0.5) for x, z in P])
    d = 0.0
    for i in range(n):
        j = (i + 1) % n
        seg = math.hypot(P[j][0] - P[i][0], P[j][1] - P[i][1])
        face([lo[i], lo[j], hi[j], hi[i]], side, [(d * uvs, 0.0), ((d + seg) * uvs, 0.0), ((d + seg) * uvs, h * uvs), (d * uvs, h * uvs)])
        d += seg
    # make sure every face points outwards (outline orientation is not trusted)
    c = sum((v.co for v in lo + hi), Vector()) / (2 * n)
    for f in faces:
        if f.is_valid and f.normal.dot(f.calc_center_median() - c) < 0:
            f.normal_flip()
    return faces


def crate(m, w, d, h, mat="f_tray_grey", pos=(0, 0, 0), slots=3, t=0.012):
    """Open plastic harvest crate (w x d x h) with slotted walls; returns the inner floor height."""
    x, y, z = pos
    m.box((w, t, d), (x, y + t / 2, z), mat, 0.003)
    sl = (h - t) / (2 * slots + 1)
    for k in range(slots + 1):
        yy = y + t + sl * (2 * k + 0.5) + (0.0 if k < slots else sl * 0.5)
        hh = sl if k < slots else sl * 1.6
        m.box((w, hh, t), (x, yy, z - d / 2 + t / 2), mat, 0.002)
        m.box((w, hh, t), (x, yy, z + d / 2 - t / 2), mat, 0.002)
        m.box((t, hh, d - 2 * t), (x - w / 2 + t / 2, yy, z), mat, 0.002)
        m.box((t, hh, d - 2 * t), (x + w / 2 - t / 2, yy, z), mat, 0.002)
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box((t * 1.6, h, t * 1.6), (x + sx * (w / 2 - t * 0.8), y + h / 2, z + sz * (d / 2 - t * 0.8)), mat, 0.003)
    return y + t


def blob(m, radii, pos=(0, 0, 0), mat="f_white", seg=14, ring=10, disp=None, uv="sph", rot=(0, 0, 0), warp=None, tile=(1, 1)):
    """Ellipsoid (radii = (rx, ry, rz)) with optional noise displacement."""
    prof = [(math.sin(PI * k / ring), -math.cos(PI * k / ring)) for k in range(ring + 1)]
    prof[0] = (0.0, -1.0)
    prof[-1] = (0.0, 1.0)
    return lathe(m, prof, pos, mat, seg, rot, radii, uv, disp, warp, tile)


def dome(m, r, h, pos=(0, 0, 0), mat="f_white", seg=18, ring=6, disp=None, uv="sph", rot=(0, 0, 0), warp=None, tile=(1, 1)):
    """Upper half-ellipsoid on a flat base (bun top, cake dome, mound of food)."""
    prof = [(0.0, 0.0), (r, 0.0)]
    prof += [(r * math.cos(PI / 2 * k / ring), h * math.sin(PI / 2 * k / ring)) for k in range(1, ring + 1)]
    prof[-1] = (0.0, h)
    return lathe(m, prof, pos, mat, seg, rot, (1, 1, 1), uv, disp, warp, tile)


def disc(m, r, h, pos=(0, 0, 0), mat="f_white", seg=24, uv="auto", disp=None, edge=0.4, warp=None, tile=(1, 1), top=None, rot=(0, 0, 0)):
    """Rounded puck (pizza, pancake, cookie): radius r, thickness h, `edge` = rounding of the rim (0..1)."""
    e = h * edge
    prof = [(0.0, 0.0), (r - e, 0.0), (r, e * 0.6), (r, h - e), (r - e, h), (0.0, h if top is None else top)]
    return lathe(m, prof, pos, mat, seg, rot, (1, 1, 1), uv, disp, warp, tile)


def cyl_f(m, r, h, pos=(0, 0, 0), mat="f_white", seg=14, r2=None, uv=None, disp=None, rot=(0, 0, 0), scale=(1, 1, 1), warp=None,
          round_=0.0, tile=(1, 1)):
    """Cylinder / frustum along Y (base at pos), optionally with rounded top and bottom edges and a smooth finish."""
    r2 = r if r2 is None else r2
    rd = min(round_, r, r2, h / 2)
    if rd > 0:
        prof = [(0.0, 0.0), (r - rd, 0.0), (r, rd * 0.4), (r, rd), (r2, h - rd), (r2 - rd * 0.4, h - rd * 0.4), (r2 - rd, h), (0.0, h)]
    else:
        prof = [(0.0, 0.0), (r, 0.0), (r2, h), (0.0, h)]
    return lathe(m, prof, pos, mat, seg, rot, scale, uv, disp, warp, tile)


def vessel(m, outer, t, pos=(0, 0, 0), mat="f_plate", seg=24, **kw):
    """Open thin-walled vessel (cup, glass, bowl, plate) from its OUTER profile listed bottom-centre -> rim, e.g.
    [(0, 0), (0.03, 0), (0.04, 0.01), (0.045, 0.1)]; wall thickness t (inner wall = outer shifted inwards / upwards)."""
    out = [(r, y) for (r, y) in outer]
    yr = out[-1][1]
    inner = [(0.0, out[0][1] + t)]
    for (r, y) in out[1:]:
        inner.append((max(r - t, 0.0), min(y + t, yr)))
    prof = out + [(inner[-1][0], yr)] + list(reversed(inner[:-1])) if inner[-1][0] > 0 else out + list(reversed(inner[:-1]))
    prof[-1] = (0.0, prof[-1][1])
    return lathe(m, prof, pos, mat, seg, **kw)


def bowl_outer(R, h, foot=0.38, n=7, belly=1.0):
    """Outer profile of a round bowl (bottom-centre -> rim)."""
    out = [(0.0, 0.0), (R * foot, 0.0)]
    for k in range(1, n + 1):
        a = PI / 2 * k / n
        out.append((R * foot + R * (1 - foot) * math.sin(a) ** belly, h * (1 - math.cos(a))))
    return out


# ------------------------------------------------------------------ tubes / sweeps
def tube3(m, pts, radii, mat="f_white", seg=8, uv=None, caps=True, tile=(1, 1), disp=None, flat=1.0):
    """Smooth tube along a polyline / spline of game-space points.  radii: float or list (per point).
    caps=True rounds both ends.  uv: None or 'tube' (u around, v along)."""
    bm = m.cur["bm"]
    mi = m._mi(mat)
    n = len(pts)
    rad = [radii] * n if not isinstance(radii, (list, tuple)) else list(radii)
    P = [Vector(p) for p in pts]
    T = []
    for i in range(n):
        a = P[max(i - 1, 0)]
        b = P[min(i + 1, n - 1)]
        t = (b - a)
        T.append(t.normalized() if t.length > 1e-9 else Vector((0, 1, 0)))
    ref = Vector((0, 1, 0)) if abs(T[0].y) < 0.9 else Vector((1, 0, 0))
    nrm = (ref - T[0] * ref.dot(T[0])).normalized()
    frames = []
    for i in range(n):
        nrm = (nrm - T[i] * nrm.dot(T[i]))
        nrm = nrm.normalized() if nrm.length > 1e-9 else Vector((1, 0, 0))
        frames.append((nrm.copy(), T[i].cross(nrm)))
    rings = []
    dist = [0.0]
    for i in range(1, n):
        dist.append(dist[-1] + (P[i] - P[i - 1]).length)
    total = max(dist[-1], 1e-6)
    path = list(range(n))
    seq = []
    if caps:
        seq.append(("pole", P[0] - T[0] * rad[0] * 0.9, 0))
        seq.append(("ring", P[0] - T[0] * rad[0] * 0.45, 0, rad[0] * 0.85))
    for i in path:
        seq.append(("ring", P[i], i, rad[i]))
    if caps:
        seq.append(("ring", P[-1] + T[-1] * rad[-1] * 0.45, n - 1, rad[-1] * 0.85))
        seq.append(("pole", P[-1] + T[-1] * rad[-1] * 0.9, n - 1))
    uvdat = {}
    for item in seq:
        if item[0] == "pole":
            v = bm.verts.new(g2b(tuple(item[1])))
            rings.append([v])
            uvdat[v] = (0.5, dist[item[2]] / total)
            continue
        _, c, i, r = item
        nn, bb = frames[i]
        ring = []
        for k in range(seg):
            a = TAU * k / seg
            p = c + nn * (math.cos(a) * r) + bb * (math.sin(a) * r * flat)
            if disp:
                p = p + (p - c) * (disp[0] * fbm(p.x * disp[1], p.y * disp[1], p.z * disp[1], 1.0) / max(r, 1e-6))
            v = bm.verts.new(g2b(tuple(p)))
            ring.append(v)
            uvdat[v] = (k / seg, dist[i] / total)
        rings.append(ring)
    faces = []
    for j in range(len(rings) - 1):
        a, b = rings[j], rings[j + 1]
        for k in range(seg):
            k2 = (k + 1) % seg
            quad = []
            for v in (a[k % len(a)], a[k2 % len(a)], b[k2 % len(b)], b[k % len(b)]):
                if v not in quad:
                    quad.append(v)
            if len(quad) >= 3:
                try:
                    faces.append(bm.faces.new(quad))
                except ValueError:
                    pass
    # orientation: make the first ring's faces point away from the axis
    if faces:
        f0 = faces[len(faces) // 2]
        c = sum((v.co for v in f0.verts), Vector()) / len(f0.verts)
        # nearest axis point
        best = min(range(n), key=lambda i: (g2b(tuple(P[i])) - c).length)
        if f0.normal.dot(c - g2b(tuple(P[best]))) < 0:
            for f in faces:
                f.normal_flip()
    for f in faces:
        f.material_index = mi
    if uv:
        layer = bm.loops.layers.uv.verify()
        for f in faces:
            us = [uvdat[lp.vert][0] for lp in f.loops]
            if max(us) - min(us) > 0.5:
                us = [u + 1 if u < 0.5 else u for u in us]
            for lp, u in zip(f.loops, us):
                lp[layer].uv = (u * tile[0], uvdat[lp.vert][1] * tile[1])
    return faces


def spline(pts, n=6):
    """Catmull-Rom spline through game-space points (n samples per segment)."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
    out.append(tuple(pts[-1]))
    return out


def smooth_prof(ctrl, n=4):
    """Smooth lathe outline through control points [(r, y), ...] (first / last r should be 0 for closed fruit)."""
    pts = spline([(r, y, 0.0) for r, y in ctrl], n)
    out = [(max(r, 0.0), y) for r, y, _ in pts]
    out[0] = (ctrl[0][0], ctrl[0][1])
    out[-1] = (ctrl[-1][0], ctrl[-1][1])
    return out


def scaled(prof, sr, sy):
    return [(r * sr, y * sy) for r, y in prof]


def bend_flat(Rc):
    """Warp factory: bend a lathe made along +/-Y into a flat arc (curving towards +Z), cross-section X stays radial, Z becomes height."""
    def w(x, y, z):
        ph = y / Rc
        return Rc * math.sin(ph) + x * math.cos(ph), z, Rc * (1 - math.cos(ph)) + x * math.sin(ph)
    return w


def heap(rng, n, R, H, jitter=0.15):
    """n points (x, y, z) of a heap: Fibonacci spiral over a disc of radius R, dome height H (y of the surface at that point)."""
    out = []
    for k in range(n):
        a = k * 2.399963 + rng.random() * jitter
        r = R * math.sqrt((k + 0.5) / n)
        out.append((r * math.cos(a), H * (1 - (r / R) ** 2), r * math.sin(a)))
    return out


def arc_pts(c, r, a0, a1, n=8, plane="xy", sq=1.0):
    """Points on a circular arc (game space) in plane 'xy' | 'xz' | 'zy' around centre c."""
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        u, v = r * math.cos(a), r * math.sin(a) * sq
        if plane == "xy":
            out.append((c[0] + u, c[1] + v, c[2]))
        elif plane == "xz":
            out.append((c[0] + u, c[1], c[2] + v))
        else:
            out.append((c[0], c[1] + v, c[2] + u))
    return out


def bez(p0, p1, p2, n=8):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(tuple((1 - t) ** 2 * p0[k] + 2 * (1 - t) * t * p1[k] + t * t * p2[k] for k in range(3)))
    return out


# ------------------------------------------------------------------ small things
def seeds(m, rng, n, rect, y, mat="f_sesame", size=(0.003, 0.0015, 0.002), jitter_rot=True, ground=None, seg=5, ring=3):
    """Scatter n tiny ellipsoids (seeds, crumbs, herbs) over rect=(cx, cz, rx, rz) at height y (or ground(x, z))."""
    cx, cz, rx, rz = rect
    for _ in range(n):
        a = rng.random() * TAU
        d = math.sqrt(rng.random())
        x, z = cx + math.cos(a) * d * rx, cz + math.sin(a) * d * rz
        yy = ground(x, z) if ground else y
        blob(m, size, (x, yy, z), mat, seg, ring, uv=None, rot=(0, rng.random() * TAU, 0) if jitter_rot else (0, 0, 0))


def settle(m, mode="table"):
    """Move the model so its origin follows the mount convention (table / floor: bottom-centre; wall: back-centre)."""
    lo, hi = m.bounds()
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    if mode == "wall":
        m.shift(-cx, -(lo[1] + hi[1]) / 2, -lo[2])
    elif mode == "ceiling":
        m.shift(-cx, -hi[1], -cz)
    else:
        m.shift(-cx, -lo[1], -cz)


def torus_prof(R, rho, y, n=12, a_from=90.0, a_to=-270.0):
    """Outline points (r, y) of a circular cross-section (ring radius R, tube radius rho, centre height y) walking clockwise
    from angle a_from to a_to (degrees); a full -360 turn gives a closed loop for lathe(closed=True)."""
    out = []
    full = abs(a_from - a_to - 360) < 1e-6
    for k in range(n if full else n + 1):
        a = math.radians(a_from + (a_to - a_from) * k / n)
        out.append((R + rho * math.cos(a), y + rho * math.sin(a)))
    return out


class Menu:
    """Registry of builders that become model families: `menu = Menu()`; `@menu.cat('bakery', ...)('croissant')`."""

    def __init__(self):
        self.reg = {}
        self.meta = {}

    def cat(self, cat, mount="table", tags=("food",), solid=False, mount_y=None):
        self.meta[cat] = (mount, list(tags), solid, mount_y)
        reg = self.reg.setdefault(cat, {})

        def item(label):
            def deco(fn):
                reg[label] = fn
                return fn
            return deco
        return item

    def register(self):
        from ..kit import family
        for cat, reg in self.reg.items():
            mount, tags, solid, mount_y = self.meta[cat]

            def gen(m, i, label, rng, _reg=reg, _mount=mount):
                m.smooth_angle = math.radians(52)
                _reg[label](m, rng)
                settle(m, _mount)
            gen.__name__ = "food_" + cat
            family(cat, list(reg), mount=mount, tags=tags, solid=solid, mount_y=mount_y)(gen)


def ring_pos(rng, n, r, jitter=0.0, a0=0.0):
    """n positions on a circle (x, z, angle)."""
    out = []
    for i in range(n):
        a = a0 + TAU * i / n + (rng.random() - 0.5) * jitter
        out.append((r * math.cos(a), r * math.sin(a), a))
    return out


def sprig(m, pos, mat="f_herb", n=3, size=0.012, rng=None, rot=0.0):
    """A little herb sprig: a few flat leaf blobs fanned out."""
    for k in range(n):
        a = rot + (k - (n - 1) / 2) * 0.9
        blob(m, (size, size * 0.18, size * 0.55), (pos[0] + math.cos(a) * size * 0.8, pos[1] + 0.001 * k, pos[2] + math.sin(a) * size * 0.8),
             mat, 6, 4, uv=None, rot=(0, -a, 0))
