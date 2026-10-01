"""Modelling kit for the StarshipGo component library.

Authoring frame is the *game* frame (glTF / Godot): +X right, +Y up, +Z is the
front of the object.  Units are metres.  The kit converts to Blender's Z-up frame
internally, so the exporter's Y-up conversion round-trips exactly.

Mount conventions (origin of every model):
  floor   - bottom centre of the footprint, front faces +Z
  wall    - centre of the back plane (z = 0), object extends towards +Z
  ceiling - centre of the top surface, object extends downwards (-Y)
  table   - bottom centre; small item that rests on a surface
"""
import math
import os
import random

try:  # bpy is only needed to build geometry; plan/--check work on a bare Python
    import bpy  # noqa: F401  (must precede bmesh)
    import bmesh
    from mathutils import Matrix, Vector
    HAVE_BPY = True
except ImportError:  # pragma: no cover - exercised on bare python
    bpy = bmesh = Matrix = Vector = None
    HAVE_BPY = False

# --------------------------------------------------------------------------
# frame conversion (game -> blender)
if HAVE_BPY:
    _C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
    _CI = _C.inverted()
else:
    _C = _CI = None

# bevel failures collected during a build (reported by build_all): list of (model, primitive)
BEVEL_FAILURES = []


def _gm(pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    """Game-space TRS matrix converted into blender space (conjugation)."""
    t = Matrix.Translation(Vector(pos))
    r = Matrix.Rotation(rot[2], 4, "Z") @ Matrix.Rotation(rot[1], 4, "Y") @ Matrix.Rotation(rot[0], 4, "X")
    s = Matrix.Diagonal(Vector((scale[0], scale[1], scale[2], 1.0)))
    return _C @ (t @ r @ s) @ _CI


def g2b(v):
    return Vector((v[0], -v[2], v[1]))


def b2g(v):
    return (v[0], v[2], -v[1])


# --------------------------------------------------------------------------
# materials
# name: (hex colour, metallic, roughness, emission strength or 0, alpha)
_PALETTE = {
    "hull_light": ("#c9ced6", 0.55, 0.42), "hull_mid": ("#8d95a1", 0.6, 0.45),
    "hull_dark": ("#3c424c", 0.65, 0.5), "steel": ("#a7adb5", 0.9, 0.35),
    "brushed_alu": ("#c3c8ce", 0.95, 0.3), "chrome": ("#e6e9ee", 1.0, 0.08),
    "copper": ("#b4693f", 0.95, 0.3), "brass": ("#b8924a", 0.9, 0.32),
    "gold_trim": ("#d4a72c", 0.95, 0.25), "black_metal": ("#17191d", 0.8, 0.4),
    "gunmetal": ("#2b2f36", 0.85, 0.38), "rubber": ("#141414", 0.0, 0.85),
    "plastic_white": ("#e8eaed", 0.0, 0.4), "plastic_black": ("#1b1c1f", 0.0, 0.45),
    "plastic_grey": ("#6b7078", 0.0, 0.5), "ceramic": ("#f2f2ee", 0.0, 0.2),
    "hazard_yellow": ("#e8b80f", 0.2, 0.5), "paint_red": ("#b3271f", 0.3, 0.45),
    "paint_orange": ("#d2681c", 0.3, 0.45), "paint_blue": ("#2452a3", 0.3, 0.45),
    "paint_teal": ("#1f8a8a", 0.3, 0.45), "paint_green": ("#2f7d3b", 0.3, 0.45),
    "paint_white": ("#dfe3e6", 0.2, 0.4), "paint_gold": ("#c99a2e", 0.4, 0.4),
    "paint_grey": ("#7d838c", 0.3, 0.5), "paint_navy": ("#182a4f", 0.3, 0.45),
    "fabric_navy": ("#1f2c4d", 0.0, 0.95), "fabric_grey": ("#5b6068", 0.0, 0.95),
    "fabric_red": ("#7a1f1f", 0.0, 0.95), "fabric_tan": ("#a8916d", 0.0, 0.95),
    "fabric_teal": ("#1e5f66", 0.0, 0.95), "leather_black": ("#1d1b1a", 0.0, 0.55),
    "leather_brown": ("#4d2f1e", 0.0, 0.55), "wood_dark": ("#4a2f1c", 0.0, 0.6),
    "wood_light": ("#b68a5a", 0.0, 0.6), "foam": ("#d9d6cf", 0.0, 0.9),
    "cardboard": ("#a07d4f", 0.0, 0.9), "leaf": ("#2f6b2a", 0.0, 0.7),
    "soil": ("#3b2a1e", 0.0, 0.95), "water": ("#3a7bd5", 0.0, 0.1),
    "food_red": ("#a8322a", 0.0, 0.6), "food_green": ("#5d8a34", 0.0, 0.6),
    "food_brown": ("#7b4a25", 0.0, 0.7), "concrete": ("#737373", 0.0, 0.9),
    "carbon": ("#101215", 0.5, 0.3),
}
_EMISSIVE = {
    "em_white": ("#ffffff", 3.0), "em_warm": ("#ffd9a0", 3.0), "em_cyan": ("#33e0ff", 3.0),
    "em_blue": ("#3a7bff", 3.0), "em_amber": ("#ffab1f", 3.0), "em_red": ("#ff2a1f", 3.0),
    "em_green": ("#2dff6a", 3.0), "em_violet": ("#a24bff", 3.0), "em_orange": ("#ff6a1a", 3.0),
}
_GLASS = {"glass": ("#dbe9f2", 0.22), "glass_blue": ("#7db4e6", 0.3), "glass_dark": ("#20282e", 0.55),
          "glass_green": ("#8fe0a8", 0.3), "glass_amber": ("#e8b060", 0.35)}

def register_material(name, hexcolor, metallic=0.0, roughness=0.5, emission=0.0, alpha=1.0):
    """Add a material from a component module (use a module-specific prefix for the name)."""
    if emission > 0:
        _EMISSIVE[name] = (hexcolor, emission)
    elif alpha < 1.0:
        _GLASS[name] = (hexcolor, alpha)
    else:
        _PALETTE[name] = (hexcolor, metallic, roughness)


MATERIAL_NAMES = sorted(list(_PALETTE) + list(_EMISSIVE) + list(_GLASS) + ["screen_off"])


def _hex(h):
    h = h.lstrip("#")
    lin = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), 1.0)


def _new_material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    return mat, mat.node_tree.nodes["Principled BSDF"]


_mat_cache = {}


def mat(name):
    if name in _mat_cache:
        return _mat_cache[name]
    if name in _PALETTE:
        hx, met, rough = _PALETTE[name]
        m, b = _new_material(name)
        b.inputs["Base Color"].default_value = _hex(hx)
        b.inputs["Metallic"].default_value = met
        b.inputs["Roughness"].default_value = rough
    elif name in _EMISSIVE:
        hx, s = _EMISSIVE[name]
        m, b = _new_material(name)
        b.inputs["Base Color"].default_value = (0, 0, 0, 1)
        b.inputs["Roughness"].default_value = 0.4
        b.inputs["Emission Color"].default_value = _hex(hx)
        b.inputs["Emission Strength"].default_value = s
    elif name in _GLASS:
        hx, a = _GLASS[name]
        m, b = _new_material(name)
        b.inputs["Base Color"].default_value = _hex(hx)
        b.inputs["Roughness"].default_value = 0.05
        b.inputs["Alpha"].default_value = a
        m.surface_render_method = "BLENDED"
    elif name == "screen_off":
        m, b = _new_material(name)
        b.inputs["Base Color"].default_value = _hex("#050709")
        b.inputs["Roughness"].default_value = 0.08
        b.inputs["Metallic"].default_value = 0.2
    elif name.startswith("screen:"):
        m = _screen_material(name.split(":", 1)[1])
    else:
        raise KeyError(f"unknown material {name!r}")
    _mat_cache[name] = m
    return m


TEXTURE_DIR = None  # set by build_all (godot/textures)


def _screen_material(tex):
    m, b = _new_material("screen_" + tex)
    path = os.path.join(TEXTURE_DIR, "screens", tex + ".png")
    img = bpy.data.images.load(path)
    nt = m.node_tree
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = img
    t.interpolation = "Linear"
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Roughness"].default_value = 0.15
    nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.6
    return m


# --------------------------------------------------------------------------
class Model:
    """Accumulates primitives (in game coordinates) into one or more mesh groups."""

    def __init__(self, name):
        self.name = name
        self.groups = {}
        self.cur = None
        self.group("body")

    # -- groups -----------------------------------------------------------
    def group(self, gname, pivot=(0, 0, 0)):
        """Start/select a separate named mesh node (e.g. moving door leaf)."""
        if gname not in self.groups:
            self.groups[gname] = {"bm": bmesh.new(), "mats": [], "pivot": tuple(pivot)}
        elif tuple(pivot) != (0, 0, 0) and tuple(pivot) != self.groups[gname]["pivot"]:
            raise ValueError(f"{self.name}: group {gname!r} re-selected with pivot {tuple(pivot)} "
                             f"!= original {self.groups[gname]['pivot']}")
        self.cur = self.groups[gname]
        return self

    def _mi(self, matname):
        mats = self.cur["mats"]
        if matname not in mats:
            mats.append(matname)
        return mats.index(matname)

    def _tag(self, verts, matname, bevel=0.0, prim="?"):
        mi = self._mi(matname)
        faces = {f for v in verts for f in v.link_faces}
        for f in faces:
            f.material_index = mi
        if bevel > 0:
            edges = {e for f in faces for e in f.edges}
            try:
                bmesh.ops.bevel(self.cur["bm"], geom=list(edges), offset=bevel, offset_type="OFFSET",
                                segments=1, affect="EDGES", material=mi)
            except Exception:
                BEVEL_FAILURES.append((self.name, prim))
        return faces

    # -- primitives -------------------------------------------------------
    def box(self, size, pos=(0, 0, 0), mat="hull_mid", bevel=0.0, rot=(0, 0, 0)):
        """Box of full size (sx, sy, sz) centred at pos."""
        sx, sy, sz = size
        bevel = min(bevel, min(sx, sy, sz) * 0.45)
        r = bmesh.ops.create_cube(self.cur["bm"], size=1.0, matrix=_gm(pos, rot, (sx, sy, sz)))
        self._tag(r["verts"], mat, bevel, "box")
        return self

    def boxb(self, p0, p1, mat="hull_mid", bevel=0.0):
        """Box from corner p0 to corner p1."""
        c = tuple((a + b) / 2 for a, b in zip(p0, p1))
        s = tuple(abs(a - b) for a, b in zip(p0, p1))
        return self.box(s, c, mat, bevel)

    def cyl(self, r, h, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=16, r2=None, cap=True, rot=(0, 0, 0), bevel=0.0):
        """Cylinder / frustum. h along `axis`, pos is the centre. r2 = radius at +axis end (default r)."""
        r2 = r if r2 is None else r2
        pre = {"y": (0, 0, 0), "x": (0, 0, -math.pi / 2), "z": (math.pi / 2, 0, 0)}[axis]
        m = _gm(pos, rot) @ _gm((0, 0, 0), pre)
        rr = bmesh.ops.create_cone(self.cur["bm"], cap_ends=cap, cap_tris=False, segments=max(3, seg),
                                   radius1=r, radius2=r2, depth=h, matrix=m)
        self._tag(rr["verts"], mat, bevel, "cyl")
        return self

    def sphere(self, r, pos=(0, 0, 0), mat="hull_mid", seg=16, ring=10, scale=(1, 1, 1), clip_y=None):
        """UV sphere / ellipsoid. clip_y (game-space height) cuts away everything above that plane,
        leaving an open dome (used for flush ceiling domes whose top half would poke into the ceiling)."""
        bm = self.cur["bm"]
        rr = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=r,
                                       matrix=_gm(pos, (0, 0, 0), scale))
        verts = rr["verts"]
        if clip_y is not None:
            edges = {e for v in verts for e in v.link_edges}
            faces = {f for v in verts for f in v.link_faces}
            bmesh.ops.bisect_plane(bm, geom=list(verts) + list(edges) + list(faces), dist=1e-6,
                                   plane_co=(0, 0, clip_y), plane_no=(0, 0, 1), clear_outer=True)
            verts = [v for v in verts if v.is_valid]
        self._tag(verts, mat)
        return self

    def torus(self, R, r, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=24, tseg=8, arc=2 * math.pi, rot=(0, 0, 0)):
        """Torus (or arc of one) around `axis`."""
        bm = self.cur["bm"]
        pre = {"y": (0, 0, 0), "x": (0, 0, -math.pi / 2), "z": (math.pi / 2, 0, 0)}[axis]
        M = _gm(pos, rot) @ _gm((0, 0, 0), pre)
        full = abs(arc - 2 * math.pi) < 1e-6
        n = seg if full else seg + 1
        rings = []
        for i in range(n):
            a = arc * i / seg
            ring = []
            for j in range(tseg):
                b = 2 * math.pi * j / tseg
                # game-local: ring in XZ plane around Y
                gx = (R + r * math.cos(b)) * math.cos(a)
                gz = (R + r * math.cos(b)) * math.sin(a)
                gy = r * math.sin(b)
                ring.append(bm.verts.new(M @ g2b((gx, gy, gz))))
            rings.append(ring)
        faces = []
        for i in range(seg if full else seg):
            i2 = (i + 1) % n
            for j in range(tseg):
                j2 = (j + 1) % tseg
                try:
                    faces.append(bm.faces.new((rings[i][j], rings[i][j2], rings[i2][j2], rings[i2][j])))
                except ValueError:
                    pass
        mi = self._mi(mat)
        for f in faces:
            f.material_index = mi
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        return self

    def prism(self, pts, h, pos=(0, 0, 0), mat="hull_mid", plane="xz", rot=(0, 0, 0), bevel=0.0):
        """Extrude a 2D polygon. plane 'xz': polygon points are (x, z), extruded along +Y for h
        (base at pos.y). plane 'xy': points (x, y) extruded along +Z. plane 'zy': points (z, y) along +X."""
        bm = self.cur["bm"]
        M = _gm(pos, rot)

        def to3(p, d):
            if plane == "xz":
                return (p[0], d, p[1])
            if plane == "xy":
                return (p[0], p[1], d)
            return (d, p[1], p[0])

        bot = [bm.verts.new(M @ g2b(to3(p, 0))) for p in pts]
        f = bm.faces.new(bot)
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        verts = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=M.to_3x3() @ g2b(to3((0, 0), h)))
        allv = bot + verts
        bmesh.ops.recalc_face_normals(bm, faces=list({fc for v in allv for fc in v.link_faces}))
        self._tag(allv, mat, bevel, "prism")
        return self

    def quad(self, size, pos=(0, 0, 0), mat="hull_mid", rot=(0, 0, 0), uv=True):
        """Single-sided quad in local XY facing +Z, with UVs 0..1 (v up)."""
        bm = self.cur["bm"]
        M = _gm(pos, rot)
        w, h = size[0] / 2, size[1] / 2
        pts = [(-w, -h, 0), (w, -h, 0), (w, h, 0), (-w, h, 0)]
        vs = [bm.verts.new(M @ g2b(p)) for p in pts]
        f = bm.faces.new(vs)
        mi = self._mi(mat)
        f.material_index = mi
        if uv:
            layer = bm.loops.layers.uv.verify()
            for loop, (u, v) in zip(f.loops, [(0, 0), (1, 0), (1, 1), (0, 1)]):
                loop[layer].uv = (u, v)
        return self

    def screen(self, size, pos, tex, rot=(0, 0, 0), bezel=0.0, bezel_mat="black_metal"):
        """Emissive display quad using a generated screen texture (see textures.SCREENS)."""
        if bezel > 0:
            self.box((size[0] + 2 * bezel, size[1] + 2 * bezel, 0.012), (pos[0], pos[1], pos[2] - 0.006), bezel_mat, 0.004, rot)
        self.quad(size, pos, "screen:" + tex, rot)
        return self

    def tube(self, pts, r, mat="steel", seg=8, closed_ends=True):
        """Pipe following a polyline of game-space points (simple mitred sweep)."""
        for a, b in zip(pts[:-1], pts[1:]):
            self.link(a, b, r, mat, seg)
        for p in pts[1:-1]:
            self.sphere(r, p, mat, seg=seg, ring=max(4, seg // 2))
        return self

    def link(self, a, b, r, mat="steel", seg=8):
        """Cylinder from point a to point b (game space)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        if L < 1e-5:
            return self
        up = Vector((0, 1, 0))
        q = up.rotation_difference(d.normalized())
        R = q.to_matrix().to_4x4()
        T = Matrix.Translation((a + b) / 2)
        Mg = T @ R
        M = _C @ Mg @ _CI
        rr = bmesh.ops.create_cone(self.cur["bm"], cap_ends=True, cap_tris=False, segments=max(3, seg),
                                   radius1=r, radius2=r, depth=L, matrix=M)
        self._tag(rr["verts"], mat)
        return self

    def mirror_x(self):
        """Mirror everything built so far in the current group across x=0 (adds a copy)."""
        bm = self.cur["bm"]
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        ret = bmesh.ops.duplicate(bm, geom=geom)
        vs = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMVert)]
        for v in vs:
            v.co.x = -v.co.x
        fs = [g for g in ret["geom"] if isinstance(g, bmesh.types.BMFace)]
        bmesh.ops.reverse_faces(bm, faces=fs)
        return self

    # -- origin fixing ----------------------------------------------------
    def shift(self, dx=0.0, dy=0.0, dz=0.0):
        """Translate everything built so far (all groups, and group pivots) by a game-space offset."""
        for g in self.groups.values():
            if g["bm"].verts:
                bmesh.ops.translate(g["bm"], verts=list(g["bm"].verts), vec=g2b((dx, dy, dz)))
            px, py, pz = g["pivot"]
            g["pivot"] = (px + dx, py + dy, pz + dz)
        return self

    def ground(self, y=0.0):
        """Floor mount: move the model so its lowest point is at height y (default 0)."""
        return self.shift(dy=y - self.bounds()[0][1])

    def hang(self):
        """Ceiling mount: move the model so its highest point is at y = 0 (hangs down from the origin)."""
        return self.shift(dy=-self.bounds()[1][1])

    def to_wall(self):
        """Wall mount: move the model so its back is on the wall plane (z_min = 0)."""
        return self.shift(dz=-self.bounds()[0][2])

    # -- finishing --------------------------------------------------------
    def bounds(self):
        lo = [1e9] * 3
        hi = [-1e9] * 3
        n = 0
        for g in self.groups.values():
            for v in g["bm"].verts:
                p = b2g(v.co)
                for i in range(3):
                    lo[i] = min(lo[i], p[i])
                    hi[i] = max(hi[i], p[i])
                n += 1
        if n == 0:
            return [0, 0, 0], [0, 0, 0]
        return lo, hi

    def tris(self):
        return sum(len(f.verts) - 2 for g in self.groups.values() for f in g["bm"].faces)


def _smooth(bm, angle=math.radians(38)):
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle:
            e.smooth = False
        elif len(e.link_faces) != 2:
            e.smooth = False


ZFIGHT_EPS = 0.0015       # faces closer than this to one plane cannot be ordered by the depth buffer
ZFIGHT_LIFT = 0.003       # the smaller of two coplanar overlapping faces is lifted by this much along its normal
ZFIGHT_FIXED = []         # (model name, faces lifted) collected during a build (reported by build_all)


def _poly2d(face, u, v):
    return [(vt.co.dot(u), vt.co.dot(v)) for vt in face.verts]


def _convex_overlap(a, b):
    """Separating-axis overlap test of two convex 2D polygons (interiors overlap by more than a sliver)."""
    for poly in (a, b):
        n = len(poly)
        for i in range(n):
            p, q = poly[i], poly[(i + 1) % n]
            ax, ay = -(q[1] - p[1]), q[0] - p[0]
            ln = math.hypot(ax, ay)
            if ln < 1e-12:
                continue
            ax, ay = ax / ln, ay / ln
            pa = [ax * x + ay * y for x, y in a]
            pb = [ax * x + ay * y for x, y in b]
            if max(pa) <= min(pb) + 1e-5 or max(pb) <= min(pa) + 1e-5:
                return False
    return True


def fix_zfight(model, passes=8):
    """Lift one face of every pair of coplanar, same-facing, overlapping faces of different materials.

    Such a pair (an inlaid light strip flush with its panel, a screen quad on its bezel ...) gives the depth buffer the same
    depth for both, so the two surfaces flicker against each other as the camera moves.  The smaller face of the pair
    (a detail on a larger surface) is moved ZFIGHT_LIFT metres along its normal; returns the number of faces lifted."""
    lifted_total = 0
    for gname, g in model.groups.items():
        bm = g["bm"]
        if len(bm.faces) < 2:
            continue
        for _ in range(passes):
            bm.normal_update()
            buckets = {}
            for f in bm.faces:
                if f.calc_area() < 1e-8:
                    continue
                n = f.normal
                d = n.dot(f.verts[0].co)
                key = (round(n.x * 100), round(n.y * 100), round(n.z * 100), int(math.floor(d / ZFIGHT_EPS)))
                buckets.setdefault(key, []).append(f)
            lift = {}
            for key, faces in buckets.items():
                cand = list(faces)
                for dk in (-1, 1):
                    cand += buckets.get((key[0], key[1], key[2], key[3] + dk), [])
                for a in faces:
                    for b in cand:
                        if a is b or a.material_index == b.material_index or a.index > b.index and b in faces:
                            continue
                        if a.normal.dot(b.normal) < 0.9998 or abs(a.normal.dot(a.verts[0].co) - b.normal.dot(b.verts[0].co)) > ZFIGHT_EPS:
                            continue
                        n = a.normal
                        ref = Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))
                        u = n.cross(ref).normalized()
                        v = n.cross(u)
                        if not _convex_overlap(_poly2d(a, u, v), _poly2d(b, u, v)):
                            continue
                        loser = a if (a.calc_area(), a.material_index) <= (b.calc_area(), b.material_index) else b
                        lift[loser.index] = loser
            if not lift:
                break
            moved = set()
            for f in lift.values():
                for vt in f.verts:
                    if vt.index not in moved:
                        moved.add(vt.index)
                        vt.co += f.normal * ZFIGHT_LIFT
            lifted_total += len(lift)
    if lifted_total:
        ZFIGHT_FIXED.append((model.name, lifted_total))
    return lifted_total


def export(model, path):
    """Write the model as a GLB. Returns dict(bounds, tris)."""
    if not any(g["bm"].faces for g in model.groups.values()):
        raise ValueError(f"model {model.name!r} is empty (no faces); cannot export")
    objs = []
    fix_zfight(model)
    for gname, g in model.groups.items():
        bm = g["bm"]
        if not bm.faces:
            continue
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        _smooth(bm)
        me = bpy.data.meshes.new(gname)
        bm.to_mesh(me)
        for mn in g["mats"]:
            me.materials.append(mat(mn))
        if len(model.groups) == 1:
            oname = model.name
        else:
            oname = gname
        ob = bpy.data.objects.new(oname, me)
        bpy.context.scene.collection.objects.link(ob)
        pv = g["pivot"]
        if any(pv):
            # move object origin to pivot (mesh stays put)
            ob.location = g2b(pv)
            me.transform(Matrix.Translation(-g2b(pv)))
        objs.append(ob)
    lo, hi = model.bounds()
    tris = model.tris()
    top_y = _top_surface(model, lo, hi)
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_apply=False, export_yup=True,
        export_materials="EXPORT", export_image_format="AUTO", export_cameras=False, export_lights=False,
        export_normals=True, export_tangents=False, export_texcoords=True, export_extras=False,
        export_animations=False, export_skins=False, export_morph=False,
    )
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o)
        bpy.data.meshes.remove(me)
    for g in model.groups.values():
        g["bm"].free()
    return {"bounds_min": [round(x, 3) for x in lo], "bounds_max": [round(x, 3) for x in hi], "tris": tris,
            "top_y": top_y}


def _top_surface(model, lo, hi):
    """Height of the highest large upward-facing flat surface (a table top, desk, counter ...).
    Returns None when the model has no usable flat top. Used by the layout to stand small
    items on furniture."""
    foot = max((hi[0] - lo[0]) * (hi[2] - lo[2]), 1e-4)
    levels = {}
    for g in model.groups.values():
        bm = g["bm"]
        bm.normal_update()
        for f in bm.faces:
            if f.normal.z > 0.985:
                key = round(f.calc_center_median().z * 50) / 50.0
                levels[key] = levels.get(key, 0.0) + f.calc_area()
    best = None
    for z, a in levels.items():
        if a >= 0.22 * foot and a >= 0.06 and (best is None or z > best):
            best = z
    return None if best is None else round(best, 3)


# --------------------------------------------------------------------------
# family registry
FAMILIES = []


def family(category, labels, mount="floor", tags=(), solid=True, mount_y=None):
    """Register a family generator.

    labels : list of variant labels. The generator is called once per label as
             fn(m, i, label, rng) where i is the 0-based variant index, and must
             build a distinct-looking model inside `m` (a Model).
    """
    def deco(fn):
        FAMILIES.append({"fn": fn, "category": category, "labels": list(labels), "mount": mount,
                         "tags": list(tags), "solid": solid, "mount_y": mount_y, "module": fn.__module__})
        return fn
    return deco


def seeded(name):
    import zlib
    return random.Random(zlib.crc32(name.encode()))
