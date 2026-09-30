"""Architectural assets (stairs, guards, signs, exterior hull fascia).

These are *not* part of the 1000-model catalogue: nothing here is registered with @family.
They are built by blender/build_arch.py.  Authoring frame = glTF frame (+Y up, +Z front, metres).

Stair numbers (see blender/ARCH.md): width 1.40, 11 steps, riser 4.0/22, tread 0.28;
step i (1..11) top at y = i*riser, z in [-(i-1)*0.28, -i*0.28].
"""
import json
import math
import os

import bpy  # noqa: F401
import bmesh

from . import kit
from .kit import g2b, b2g

# ------------------------------------------------------------------ constants
STAIR_W = 1.40
STAIR_N = 11
STAIR_RISER = 4.0 / 22.0
STAIR_TREAD = 0.28
DECK_H = 3.4

TEX_DIR = None          # godot/textures (set by build_arch)
EMBED_PX = 256          # resolution of the textures embedded in the GLBs

# material name -> (texture set, metres per UV tile, metallic, roughness)
_TEXTURED = {
    "arch_tread": ("stair_tread", 0.5, 0.85, 0.55),
    "arch_riser": ("stair_riser", 0.7, 0.35, 0.5),
    "arch_steel": ("hull_dark", 1.0, 0.85, 0.5),
    "arch_hull_plate": ("hull_plate", 4.0, 0.85, 0.5),
}

kit.register_material("arch_nosing", "#3a3d43", 0.9, 0.38)
kit.register_material("arch_rail", "#c9cdd3", 1.0, 0.22)
kit.register_material("arch_post", "#2d3138", 0.85, 0.4)
kit.register_material("arch_led", "#6fb8ff", 0, 0.4, emission=1.2)
kit.register_material("arch_run_cyan", "#33e0ff", 0, 0.4, emission=3.0)
kit.register_material("arch_run_amber", "#ffab1f", 0, 0.4, emission=3.0)
kit.register_material("arch_run_white", "#cfe2ff", 0, 0.4, emission=3.0)
kit.register_material("arch_dark_panel", "#14171b", 0.6, 0.45)


# ------------------------------------------------------------------ textured materials
_TMP = None


def _load_scaled(path, name, colorspace):
    """Load a texture, shrink it to EMBED_PX and re-save as a small JPEG so the GLB stays light."""
    global _TMP
    import tempfile
    if _TMP is None:
        _TMP = tempfile.mkdtemp(prefix="arch_tex_")
    img = bpy.data.images.load(path, check_existing=False)
    img.colorspace_settings.name = colorspace
    if img.size[0] > EMBED_PX:
        img.scale(EMBED_PX, EMBED_PX)
    out = os.path.join(_TMP, name + ".jpg")
    st = bpy.context.scene.render.image_settings
    st.file_format, st.quality, st.color_mode = "JPEG", 72, "RGB"
    img.save_render(out)
    bpy.data.images.remove(img)
    small = bpy.data.images.load(out, check_existing=False)
    small.name = name
    small.colorspace_settings.name = colorspace
    return small


def _textured_material(name):
    tex, _tile, metal, rough = _TEXTURED[name]
    base = os.path.join(TEX_DIR, "surfaces", tex)
    if not os.path.exists(base + "_albedo.png"):        # pre-existing sets live in godot/textures
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "godot", "textures", "surfaces", tex)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    a = nt.nodes.new("ShaderNodeTexImage")
    a.image = _load_scaled(base + "_albedo.png", name + "_albedo", "sRGB")
    nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = _load_scaled(base + "_normal.png", name + "_normal", "Non-Color")
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 1.0
    nt.links.new(n.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def ensure_materials():
    """(Re)create the textured materials in the current bpy session and put them in kit's cache."""
    for name in _TEXTURED:
        cached = kit._mat_cache.get(name)
        if cached is None or cached.name not in bpy.data.materials:
            kit._mat_cache[name] = _textured_material(name)


# ------------------------------------------------------------------ UVs
def apply_uvs(m, riser_mat="arch_riser"):
    """Box-project UVs in game space: one UV tile = _TEXTURED tile size (metres), other
    materials get 1 m tiles. Risers map one riser height to V so the hazard band lines up."""
    for g in m.groups.values():
        bm = g["bm"]
        if not bm.faces:
            continue
        layer = bm.loops.layers.uv.verify()
        bm.normal_update()
        for f in bm.faces:
            mn = g["mats"][f.material_index] if f.material_index < len(g["mats"]) else ""
            tile = _TEXTURED.get(mn, (0, 1.0))[1]
            n = b2g(f.normal)
            ax = max(range(3), key=lambda k: abs(n[k]))
            for lp in f.loops:
                p = b2g(lp.vert.co)
                if mn == riser_mat and ax == 2:
                    u = p[0] / 0.7
                    c = b2g(f.calc_center_median())
                    kk = math.floor(c[1] / STAIR_RISER)
                    v = (p[1] - kk * STAIR_RISER) / (STAIR_RISER - 0.04)
                elif ax == 0:
                    u, v = p[2] / tile, p[1] / tile
                elif ax == 1:
                    u, v = p[0] / tile, p[2] / tile
                else:
                    u, v = p[0] / tile, p[1] / tile
                lp[layer].uv = (u, v)


def canonicalize(m):
    """kit's bevel ops iterate Python sets (address order), so vertex/face order can differ between
    runs. Sort geometry by position so identical inputs give byte-identical GLBs."""
    for g in m.groups.values():
        bm = g["bm"]
        if not bm.faces:
            continue
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        key = lambda v: (round(v.co.x, 4), round(v.co.y, 4), round(v.co.z, 4), round(v.co.x, 6), round(v.co.y, 6), round(v.co.z, 6))
        verts = sorted(bm.verts, key=key)
        pos = {v.index if False else id(v): i for i, v in enumerate(verts)}
        faces = sorted(((f.material_index, tuple(pos[id(v)] for v in f.verts)) for f in bm.faces),
                       key=lambda t: (t[0], tuple(sorted(t[1])), t[1]))
        nb = bmesh.new()
        nv = [nb.verts.new((round(v.co.x, 5), round(v.co.y, 5), round(v.co.z, 5))) for v in verts]
        nb.verts.ensure_lookup_table()
        for mi, idx in faces:
            try:
                f = nb.faces.new([nv[i] for i in idx])
                f.material_index = mi
            except ValueError:
                pass
        bm.free()
        g["bm"] = nb


def export_arch(m, path):
    ensure_materials()
    canonicalize(m)
    apply_uvs(m)
    return kit.export(m, path)


# ------------------------------------------------------------------ helpers
def _tube(m, pts, r, mat, seg=8, joints=True):
    for a, b in zip(pts[:-1], pts[1:]):
        m.link(a, b, r, mat, seg)
    if joints:
        for p in pts[1:-1]:
            m.sphere(r * 1.0, p, mat, seg=seg, ring=max(4, seg // 2))


def nose_y(z):
    """Height of the nosing line at z (front top edges of the treads)."""
    return STAIR_RISER + (STAIR_RISER / STAIR_TREAD) * (-z)


# ================================================================== stair flight
def arch_stair_flight(m):
    R, T, N = STAIR_RISER, STAIR_TREAD, STAIR_N
    W2 = STAIR_W / 2            # 0.70
    xi = W2 - 0.04              # inner face of stringer, 0.66
    kerb = 0.05
    slope = R / T
    # ---- steps --------------------------------------------------------------
    for i in range(1, N + 1):
        f = -(i - 1) * T                      # front (riser) plane of step i
        top = i * R
        # tread pan (full span, exact top height)
        m.boxb((-xi, top - 0.04, f - T), (xi, top, f), "arch_tread", bevel=0.004)
        # closed riser plate standing on the tread below
        m.boxb((-xi, (i - 1) * R, f - 0.02), (xi, top - 0.04, f), "arch_riser")
        # non-slip nosing strip on the tread front edge, amber edge line, LED under the nose
        m.boxb((-xi + 0.01, top, f - 0.055), (xi - 0.01, top + 0.006, f - 0.012), "arch_nosing", bevel=0.002)
        m.boxb((-xi + 0.01, top, f - 0.012), (xi - 0.01, top + 0.007, f), "em_amber")
        m.boxb((-xi + 0.06, top - 0.052, f), (xi - 0.06, top - 0.04, f + 0.006), "arch_led")
        for bx in (-0.56, 0.56):
            m.cyl(0.008, 0.004, (bx, top + 0.008, f - 0.034), "chrome", seg=6)
    # ---- stringers (closed side plates down to the floor line) --------------
    zb = -0.14 / slope                        # where the underside line meets the floor
    zend = -N * T
    poly = [(0.0, 0.0), (zb, 0.0), (zend, slope * -zend - 0.14), (zend, N * R + kerb)]
    for i in range(N, 0, -1):
        f = -(i - 1) * T
        poly.append((f, i * R + kerb))
        if i > 1:
            poly.append((f, (i - 1) * R + kerb))
    # poly: ... (zend, top) -> (f_N, N*R+kerb) ... goes front-ward along the sawtooth
    for x0 in (-W2, xi):
        m.prism(poly, 0.04, (x0, 0, 0), "arch_steel", plane="zy")
    # soffit plate + three cross ties between the stringers
    soff = [(zb, 0.0), (zend, slope * -zend - 0.14), (zend, slope * -zend - 0.11), (zb, 0.03)]
    m.prism(soff, 2 * xi, (-xi, 0, 0), "arch_steel", plane="zy")
    for zz in (-0.8, -1.7, -2.6):
        yy = slope * -zz - 0.14
        m.boxb((-xi, yy - 0.05, zz - 0.02), (xi, yy, zz + 0.02), "arch_post")
    # foot plates where the stringers meet the floor
    for sx in (-1, 1):
        m.boxb((min(sx * W2, sx * xi), 0.0, 0.0), (max(sx * W2, sx * xi), 0.012, 0.045), "arch_post")
    # ---- handrails ----------------------------------------------------------
    rail_r = 0.02
    rh = 0.90
    for sx in (-1, 1):
        x = sx * (W2 - 0.03)            # 0.67 -> rail outer edge 0.69, inside the +-0.75 shaft
        pb = (x, nose_y(0.0) + rh, 0.0)
        pt = (x, nose_y(-(N - 1) * T) + rh, -(N - 1) * T)
        pe = (x, pt[1], -N * T)         # level extension over the landing edge
        # main rail: bottom return (down to the floor as a newel), slope, level top, top return
        _tube(m, [(x, 0.0, 0.0), pb, pt, pe, (x, N * R, -N * T)], rail_r, "arch_rail", seg=10)
        # lower rail parallel to the slope
        lb = (x, nose_y(0.0) + 0.45, 0.0)
        lt = (x, nose_y(-(N - 1) * T) + 0.45, -(N - 1) * T)
        m.link(lb, lt, 0.012, "arch_rail", 8)
        # posts every 3 steps, bolted on the stringer kerb
        for i in (1, 4, 7, 10):
            zc = -(i - 0.5) * T
            yb = i * R + kerb
            yt = nose_y(zc) + rh
            m.link((x, yb, zc), (x, yt, zc), 0.014, "arch_post", 8)
            m.boxb((x - 0.028, yb, zc - 0.028), (x + 0.028, yb + 0.012, zc + 0.028), "arch_post", bevel=0.003)
            m.box((0.045, 0.03, 0.045), (x, yt - 0.02, zc), "arch_post", bevel=0.004)
        # end-post feet
        m.boxb((x - 0.035, 0.0, -0.035), (x + 0.035, 0.012, 0.035), "arch_post", bevel=0.003)
        m.cyl(0.03, 0.03, (x, 0.0 + 0.11, 0.0), "arch_post", seg=10)
    # amber safety edge on the landing end of each stringer
    for x0, x1 in ((-W2, -xi), (xi, W2)):
        m.boxb((x0, N * R + kerb, -N * T), (x1, N * R + kerb + 0.004, -N * T + 0.03), "em_amber")
    return m


# ================================================================== guard
def arch_stair_guard(m):
    """0.50 wide x 1.0 tall guard/gate panel. Origin: centre of the foot, on the floor; panel in the XY plane."""
    hw = 0.25
    for sx in (-1, 1):
        x = sx * (hw - 0.03)
        m.box((0.05, 1.0, 0.05), (x, 0.5, 0), "arch_post", bevel=0.004)
        m.box((0.07, 0.022, 0.07), (x, 1.0 - 0.011, 0), "arch_rail", bevel=0.004)
        m.box((0.11, 0.012, 0.11), (x, 0.006, 0), "arch_post", bevel=0.003)
        for k in range(4):
            sxx = x + (0.04 if k % 2 else -0.04)
            szz = 0.04 if k // 2 else -0.04
            m.cyl(0.007, 0.006, (sxx, 0.015, szz), "chrome", seg=6)
        m.box((0.052, 0.12, 0.052), (x, 0.82, 0), "hazard_yellow")
    L = 2 * (hw - 0.03) - 0.05
    m.cyl(0.02, L, (0, 0.93, 0), "arch_rail", axis="x", seg=10)
    m.cyl(0.014, L, (0, 0.62, 0), "arch_rail", axis="x", seg=8)
    m.box((L, 0.1, 0.014), (0, 0.06 + 0.02, 0), "arch_steel", bevel=0.004)
    for bx in (-0.1, 0.0, 0.1):
        m.cyl(0.009, 0.84, (bx, 0.49, 0), "arch_post", seg=6)
    m.box((L * 0.9, 0.012, 0.022), (0, 0.97, 0), "em_amber")      # amber top light strip
    m.box((0.14, 0.05, 0.012), (0, 0.78, 0.004), "hazard_yellow", bevel=0.002)
    m.box((L - 0.02, 0.008, 0.014), (0, 0.15, 0.0), "arch_led")
    return m


# ================================================================== wall sign
def arch_stair_sign(m):
    """0.6 x 0.3 wall sign. Origin: centre of the back plane, extends to +Z."""
    m.box((0.6, 0.3, 0.02), (0, 0, 0.01), "arch_dark_panel", bevel=0.008)
    m.box((0.58, 0.012, 0.004), (0, 0.128, 0.022), "em_amber")            # DECK strip (top)
    m.box((0.58, 0.012, 0.004), (0, -0.128, 0.022), "em_amber")           # bottom strip
    # arrow glyph (up arrow) on the left, emissive cyan
    arrow = [(-0.04, -0.09), (0.04, -0.09), (0.04, 0.0), (0.085, 0.0), (0.0, 0.09), (-0.085, 0.0), (-0.04, 0.0)]
    m.prism(arrow, 0.004, (-0.19, 0.0, 0.02), "em_cyan", plane="xy")
    m.box((0.004, 0.22, 0.004), (-0.085, 0.0, 0.022), "arch_rail")      # divider
    # level bars: 3 bars, the top one brightest (current deck)
    for k, (w, mt) in enumerate(((0.34, "em_white"), (0.26, "em_blue"), (0.18, "em_blue"))):
        y = 0.065 - k * 0.065
        m.box((w, 0.032, 0.004), (0.05 + (w - 0.34) / 2, y, 0.022), mt)
    for bx, by in ((-0.27, 0.12), (0.27, 0.12), (-0.27, -0.12), (0.27, -0.12)):
        m.cyl(0.007, 0.006, (bx, by, 0.023), "chrome", axis="z", seg=6)
    return m


# ================================================================== hull fascia
DECK_COL = {1: "arch_run_cyan", 2: "arch_run_amber", 3: "arch_run_white"}
HANGAR_W = 14.0
HANGAR_H = 7.0           # height of the hangar mouth (stern opening)
HANGAR_CEIL = 8.0        # hangar ceiling (the rest of deck 3 has 3.4 m)
HANGAR_Z0 = 18.0         # the ceiling rail of deck 3 steps up to the hangar ceiling from here ...
HANGAR_Z1 = 18.6         # ... to here (the hangar starts at z = 18 where cargo bay and spares depot end)
STERN_Z3 = 32.0

# (u = proud of the wall line, y relative to the slab level), closed profiles
FLOOR_PROFILE = [(-0.03, -0.33), (0.08, -0.33), (0.12, -0.29), (0.12, -0.15), (0.09, -0.11), (0.04, -0.11),
                 (0.04, -0.03), (0.09, -0.03), (0.11, 0.0), (0.11, 0.12), (0.08, 0.15), (-0.03, 0.15)]
FLOOR_STRIP = [(0.035, -0.10), (0.07, -0.10), (0.07, -0.04), (0.035, -0.04)]
CEIL_PROFILE = [(-0.03, 0.0), (0.08, 0.0), (0.12, 0.04), (0.12, 0.15), (0.09, 0.18), (0.04, 0.18),
                (0.04, 0.25), (0.09, 0.25), (0.11, 0.28), (0.11, 0.31), (0.08, 0.35), (-0.03, 0.35)]
CEIL_STRIP = [(0.035, 0.19), (0.07, 0.19), (0.07, 0.24), (0.035, 0.24)]


def load_hull(root=None):
    """-> {deck: {"outline": [(x,z)...], "y": floor_y, "h": ceiling}}.
    Uses godot/data/ship.json["hull"] when present (tolerant of a few layouts), otherwise
    tools/layout/hull.py and the ship.json deck heights."""
    root = root or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    ship = {}
    p = os.path.join(root, "godot", "data", "ship.json")
    if os.path.exists(p):
        try:
            ship = json.load(open(p))
        except Exception:
            ship = {}
    ys = {d["id"]: d["y"] for d in ship.get("decks", [])} or {1: 8.0, 2: 4.0, 3: 0.0}
    out = {}
    hull = ship.get("hull")
    if hull:
        src = hull.get("decks", hull.get("outlines", hull)) if isinstance(hull, dict) else hull
        items = src.items() if isinstance(src, dict) else [(d.get("deck", d.get("id", k + 1)), d) for k, d in enumerate(src)]
        for k, v in items:
            try:
                deck = int(k)
            except (TypeError, ValueError):
                continue
            if isinstance(v, dict):
                pts = v.get("outline") or v.get("polygon") or v.get("points")
                y = v.get("y", ys.get(deck))
                h = v.get("h", v.get("height", DECK_H))
            else:
                pts, y, h = v, ys.get(deck), DECK_H
            if pts:
                out[deck] = {"outline": [(float(a[0]), float(a[1])) for a in pts], "y": float(y), "h": float(h)}
    if len(out) < 3:
        import sys
        sys.path.insert(0, os.path.join(root, "tools", "layout"))
        import hull as hullmod
        for d in (1, 2, 3):
            out.setdefault(d, {"outline": [tuple(q) for q in hullmod.outline(d)], "y": ys.get(d, {1: 8.0, 2: 4.0, 3: 0.0}[d]), "h": DECK_H})
    return out


def _outward_normals(pts, closed):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1.0 if area > 0 else -1.0
    edges = range(n) if closed else range(n - 1)
    normals = []
    for i in edges:
        a, b = pts[i], pts[(i + 1) % n]
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz) or 1.0
        normals.append((sgn * dz / L, -sgn * dx / L))
    return normals


def _sweep(m, pts, profile, mat, closed=True, dy=None):
    """Sweep a closed 2D profile [(u, y)] along the plan polyline pts [(x, z)] (mitred corners).
    u = distance along the outward normal. dy(i) = extra height per plan vertex."""
    bm = m.cur["bm"]
    mi = m._mi(mat)
    n = len(pts)
    en = _outward_normals(pts, closed)
    off = []
    for i in range(n):
        if closed:
            n0, n1 = en[i - 1], en[i]
        else:
            n0 = en[max(i - 1, 0)]
            n1 = en[min(i, len(en) - 1)]
        mx, mz = n0[0] + n1[0], n0[1] + n1[1]
        L = math.hypot(mx, mz) or 1.0
        mx, mz = mx / L, mz / L
        k = 1.0 / max(mx * n1[0] + mz * n1[1], 0.4)
        off.append((mx * k, mz * k))
    rings = []
    for i, (x, z) in enumerate(pts):
        ring = []
        extra = dy(i) if dy else 0.0
        for (u, y) in profile:
            ring.append(bm.verts.new(g2b((x + off[i][0] * u, y + extra, z + off[i][1] * u))))
        rings.append(ring)
    faces = []
    segs = n if closed else n - 1
    P = len(profile)
    for i in range(segs):
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(P):
            j2 = (j + 1) % P
            try:
                faces.append(bm.faces.new((a[j], a[j2], b[j2], b[j])))
            except ValueError:
                pass
    if not closed:
        for ring in (rings[0], rings[-1]):
            try:
                faces.append(bm.faces.new(ring))
            except ValueError:
                pass
    for f in faces:
        f.material_index = mi
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return faces


def _lerp_ramp(z):
    t = min(max((z - HANGAR_Z0) / (HANGAR_Z1 - HANGAR_Z0), 0.0), 1.0)
    t = t * t * (3 - 2 * t)
    return t * (HANGAR_CEIL - DECK_H)


def arch_hull_fascia(m, hull=None):
    """World-space exterior fascia: per-deck rails + running lights, bow stems, stern transoms,
    hangar mouth frame and two engine nacelles. Node names: fascia_deckN, stem_deckN,
    transom_deckN, hangar_frame, nacelle_port, nacelle_starboard."""
    hull = hull or load_hull()
    for deck in (1, 2, 3):
        d = hull[deck]
        pts = list(d["outline"])
        y0, h = d["y"], d["h"]
        zmax = max(p[1] for p in pts)
        closed = True
        dyc = None
        if deck == 3:
            # open the chain at the flat stern (hangar mouth lives there)
            n = len(pts)
            k = next(i for i in range(n) if abs(pts[i][1] - zmax) < 1e-6 and abs(pts[(i + 1) % n][1] - zmax) < 1e-6)
            pts = pts[k + 1:] + pts[:k + 1]
            closed = False
            dyc = lambda i, pts=pts: _lerp_ramp(pts[i][1])
        col = DECK_COL[deck]
        m.group(f"fascia_deck{deck}")
        fl = [(u, y + y0) for u, y in FLOOR_PROFILE]
        fs = [(u, y + y0) for u, y in FLOOR_STRIP]
        _sweep(m, pts, fl, "arch_hull_plate", closed)
        _sweep(m, pts, fs, col, closed)
        cl = [(u, y + y0 + h) for u, y in CEIL_PROFILE]
        cs = [(u, y + y0 + h) for u, y in CEIL_STRIP]
        _sweep(m, pts, cl, "arch_hull_plate", closed, dyc)
        _sweep(m, pts, cs, col, closed, dyc)

        # ---- bow stem cap: pointed fairings on the sheer bands at the nose ---------
        m.group(f"stem_deck{deck}")
        zn = min(p[1] for p in pts)
        nose = [p for p in pts if abs(p[1] - zn) < 1e-6]
        bn = max(abs(p[0]) for p in nose)
        wedge = [(-bn - 0.05, zn + 0.1), (bn + 0.05, zn + 0.1), (bn * 0.55, zn - 0.45), (0.0, zn - 1.25),
                 (-bn * 0.55, zn - 0.45)]
        m.prism(wedge, 0.48, (0, y0 - 0.33, 0), "arch_hull_plate", plane="xz", bevel=0.03)
        m.prism(wedge, 0.35, (0, y0 + h, 0), "arch_hull_plate", plane="xz", bevel=0.03)
        m.box((0.06, 0.04, 0.9), (0, y0 + 0.17, zn - 0.35), col)
        # ---- stern transom plates (decks 1 and 2): apron below and band above the windows -----
        if deck != 3:
            m.group(f"transom_deck{deck}")
            bs = max(abs(p[0]) for p in pts if abs(p[1] - zmax) < 1e-6)
            m.boxb((-bs, y0 + 0.15, zmax - 0.02), (bs, y0 + 0.78, zmax + 0.08), "arch_hull_plate", bevel=0.02)
            m.boxb((-bs, y0 + 3.02, zmax - 0.02), (bs, y0 + h - 0.0, zmax + 0.08), "arch_hull_plate", bevel=0.02)
            m.box((bs * 1.2, 0.03, 0.02), (0, y0 + 0.47, zmax + 0.085), col)

    # ---- hangar mouth frame (deck 3 stern, z = 32) ------------------------------------
    d3 = hull[3]
    y0 = d3["y"]
    zs = max(p[1] for p in d3["outline"])
    hw = HANGAR_W / 2
    fw = 0.6            # member width
    dep = 0.45          # proud of the stern face
    m.group("hangar_frame")
    for sx in (-1, 1):
        xc = sx * (hw + fw / 2)
        m.boxb((xc - fw / 2, y0 - 0.35, zs - 0.05), (xc + fw / 2, y0 + HANGAR_H + 0.7, zs + dep), "arch_hull_plate", bevel=0.03)
        m.box((0.05, HANGAR_H, 0.05), (sx * (hw - 0.025), y0 + HANGAR_H / 2, zs + dep - 0.02), "arch_run_amber")
    m.boxb((-hw - fw, y0 + HANGAR_H, zs - 0.05), (hw + fw, y0 + HANGAR_H + 0.7, zs + dep), "arch_hull_plate", bevel=0.03)
    m.boxb((-hw - fw, y0 - 0.35, zs - 0.05), (hw + fw, y0 + 0.02, zs + dep), "arch_hull_plate", bevel=0.03)
    m.box((HANGAR_W, 0.05, 0.05), (0, y0 + HANGAR_H - 0.025, zs + dep - 0.02), "arch_run_amber")
    g = 0.9
    for sx in (-1, 1):
        tri = [(sx * hw, y0 + HANGAR_H - g), (sx * hw, y0 + HANGAR_H), (sx * (hw - g), y0 + HANGAR_H)]
        m.prism(tri, dep, (0, 0, zs - 0.02), "arch_hull_plate", plane="xy", bevel=0.02)
        tri = [(sx * hw, y0 + 0.02 + g), (sx * hw, y0 + 0.02), (sx * (hw - g), y0 + 0.02)]
        m.prism(tri, dep, (0, 0, zs - 0.02), "arch_hull_plate", plane="xy", bevel=0.02)
    for k in range(-3, 4):          # hazard-yellow marker blocks on the header
        m.box((0.7, 0.16, 0.03), (k * 2.0, y0 + HANGAR_H + 0.35, zs + dep + 0.012), "hazard_yellow", bevel=0.004)

    # ---- engine nacelles hung below the stern corners of deck 3 ----------------------------
    for name, sx in (("nacelle_port", -1), ("nacelle_starboard", 1)):
        m.group(name)
        xn, yn, zn0, L = sx * 11.6, y0 - 0.25, 28.6, 5.6
        pylon = [(sx * 7.6, zn0 - 2.2), (sx * 11.0, zn0 - 0.9), (sx * 11.0, zn0 + 1.9), (sx * 7.6, zn0 + 2.4)]
        m.prism(pylon, 0.85, (0, yn - 0.3, 0), "arch_hull_plate", plane="xz", bevel=0.03)
        m.sphere(1.0, (xn, yn, zn0), "arch_hull_plate", seg=20, ring=10, scale=(1.3, 1.3, L))
        for dz, dr in ((-2.4, 1.0), (0.4, 1.1), (2.2, 0.85)):      # armour / cooling bands
            r = 1.3 * math.sqrt(max(0.05, 1 - (dz / L) ** 2)) + 0.03
            m.cyl(r, 0.22, (xn, yn, zn0 + dz), "arch_steel", axis="z", seg=18)
            m.cyl(r + 0.0, 0.03, (xn, yn, zn0 + dz + 0.13), "arch_run_cyan", axis="z", seg=18)
        m.cyl(0.95, 0.5, (xn, yn, zn0 + L * 0.98), "arch_dark_panel", axis="z", seg=24, r2=0.75)
        m.cyl(0.7, 0.06, (xn, yn, zn0 + L * 0.98 + 0.27), "em_blue", axis="z", seg=24)
        m.torus(0.78, 0.05, (xn, yn, zn0 - L * 0.97), "arch_run_cyan", axis="z", seg=24, tseg=6)
    return m


# ------------------------------------------------------------------ registry
ARCH_MODELS = {
    "arch_stair_flight": arch_stair_flight,
    "arch_stair_guard": arch_stair_guard,
    "arch_stair_sign": arch_stair_sign,
    "arch_hull_fascia": arch_hull_fascia,
}
