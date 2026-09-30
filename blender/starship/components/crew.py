"""Crew quarters, mess hall, galley, lounge and gym furnishing (125 labels, no humans)."""
import math

from ..kit import family, register_material

register_material("crew_seam", "#15181d", 0.0, 0.9)
register_material("crew_sheet", "#dcdcd4", 0.0, 0.95)
register_material("crew_pillow", "#e6e3da", 0.0, 0.95)
register_material("crew_mustard", "#b88a22", 0.0, 0.95)
register_material("crew_plum", "#4a2340", 0.0, 0.95)
register_material("crew_olive", "#4d5433", 0.0, 0.95)
register_material("crew_tile", "#cfd6da", 0.1, 0.3)
register_material("crew_pot", "#a5583a", 0.0, 0.8)
register_material("crew_flower", "#d94f7a", 0.0, 0.7)
register_material("crew_flower2", "#f0c93a", 0.0, 0.7)
register_material("crew_bread", "#c98d45", 0.0, 0.8)
register_material("crew_cheese", "#e8b53a", 0.0, 0.7)
register_material("crew_moss", "#3f7a2b", 0.0, 0.95)
register_material("crew_shade", "#efe2c4", 0.0, 0.8)

PI = math.pi
_D = {}     # category -> {label: builder}


def reg(cat, label):
    def deco(fn):
        _D.setdefault(cat, {})[label] = fn
        return fn
    return deco


class _Lean:
    """Model proxy that keeps GLBs small: bevels only on chunky boxes, plain screen bezels."""
    MAXB = 10
    TEX = {"radar": "tactical", "graph": "bars", "waveform": "bars", "systems": "diagnostic", "schematic": "diagnostic",
           "nav": "power", "starmap": "bars", "warp": "power", "alert": "comm", "hazard": "comm", "periodic": "text",
           "globe": "comm"}

    def __init__(self, m):
        self._m = m
        self._nb = 0
        self._tex = None

    def __getattr__(self, k):
        return getattr(self._m, k)

    def box(self, size, pos=(0, 0, 0), mat="hull_mid", bevel=0.0, rot=(0, 0, 0)):
        if bevel and (min(size) < 0.04 or self._nb >= self.MAXB or max(size) < 0.12):
            bevel = 0.0
        if bevel:
            self._nb += 1
        self._m.box(size, pos, mat, bevel, rot)
        return self

    def screen(self, size, pos, tex, rot=(0, 0, 0), bezel=0.0, bezel_mat="black_metal"):
        if bezel > 0:
            self._m.box((size[0] + 2 * bezel, size[1] + 2 * bezel, 0.012), (pos[0], pos[1], pos[2] - 0.006), bezel_mat, 0, rot)
        if self._tex is None:
            self._tex = self.TEX.get(tex, tex)
        self._m.quad(size, pos, "screen:" + self._tex, rot)
        return self

    def sphere(self, r, pos=(0, 0, 0), mat="hull_mid", seg=16, ring=10, scale=(1, 1, 1)):
        if r < 0.05:
            seg, ring = min(seg, 6), min(ring, 4)
        elif r < 0.15:
            seg, ring = min(seg, 8), min(ring, 5)
        self._m.sphere(r, pos, mat, seg, ring, scale)
        return self

    def cyl(self, r, h, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=16, r2=None, cap=True, rot=(0, 0, 0), bevel=0.0):
        seg = min(seg, 6 if r < 0.02 else 8 if r < 0.04 else 12 if r < 0.1 else 16 if r < 0.3 else 20)
        self._m.cyl(r, h, pos, mat, axis, seg, r2, cap, rot, 0.0 if (self._nb >= self.MAXB or r < 0.05) else bevel)
        if bevel and self._nb < self.MAXB and r >= 0.05:
            self._nb += 1
        return self

    def link(self, a, b, r, mat="steel", seg=8):
        self._m.link(a, b, r, mat, min(seg, 5 if r < 0.01 else 6 if r < 0.02 else 8))
        return self

    def torus(self, R, r, pos=(0, 0, 0), mat="hull_mid", axis="y", seg=24, tseg=8, arc=2 * PI, rot=(0, 0, 0)):
        seg = min(seg, 12 if R < 0.1 else 16 if R < 0.3 else 20)
        self._m.torus(R, r, pos, mat, axis, seg, min(tseg, 4 if r < 0.012 else 5), arc, rot)
        return self

    def prism(self, pts, h, pos=(0, 0, 0), mat="hull_mid", plane="xz", rot=(0, 0, 0), bevel=0.0):
        self._m.prism(pts, h, pos, mat, plane, rot, 0.0 if self._nb >= self.MAXB else bevel)
        return self


def make(cat, groups):
    """groups: list of (labels, mount, tags, solid, mount_y)."""
    for labels, mount, tags, solid, my in groups:
        def gen(m, i, label, rng, _cat=cat):
            _D[_cat][label](_Lean(m), rng)
        gen.__name__ = "crew_%s_%s" % (cat, mount)
        family(cat, labels, mount=mount, tags=tags, solid=solid, mount_y=my)(gen)


# ---------------------------------------------------------------- helpers
def cush(m, size, pos, mat, b=0.03, seam="crew_seam", grid=None):
    """Bevelled cushion with stitched top border (and optional tufting grid)."""
    sx, sy, sz = size
    x, y, z = pos
    m.box(size, pos, mat, min(b, sy * 0.4))
    if seam and sx > 0.16 and sz > 0.16:
        t = y + sy / 2 + 0.001
        ix, iz = sx / 2 - 0.05, sz / 2 - 0.05
        if sx >= sz:
            m.box((2 * ix, 0.004, 0.006), (x, t, z + iz), seam)
            m.box((2 * ix, 0.004, 0.006), (x, t, z - iz), seam)
        else:
            m.box((0.006, 0.004, 2 * iz), (x + ix, t, z), seam)
            m.box((0.006, 0.004, 2 * iz), (x - ix, t, z), seam)
        if grid:
            for k in range(1, grid):
                m.box((0.006, 0.004, 2 * iz), (x - ix + 2 * ix * k / grid, t, z), seam)


def legs(m, x0, x1, z0, z1, h, r=0.025, mat="steel", seg=8, y=0.0):
    for x in (x0, x1):
        for z in (z0, z1):
            m.cyl(r, h, (x, y + h / 2, z), mat, seg=seg)


def rails4(m, x0, x1, z0, z1, y, t, mat, th=0.04, b=0.008):
    """Rectangular frame of four bars."""
    m.box((x1 - x0, th, t), ((x0 + x1) / 2, y, z0), mat, b)
    m.box((x1 - x0, th, t), ((x0 + x1) / 2, y, z1), mat, b)
    m.box((t, th, z1 - z0), (x0, y, (z0 + z1) / 2), mat, b)
    m.box((t, th, z1 - z0), (x1, y, (z0 + z1) / 2), mat, b)


def handle(m, pos, w=0.12, mat="chrome", horiz=True):
    x, y, z = pos
    if horiz:
        m.box((w, 0.012, 0.022), (x, y, z + 0.011), mat)
    else:
        m.box((0.012, w, 0.022), (x, y, z + 0.011), mat)


def bolts(m, pts, r=0.008, mat="chrome", y_dir="z"):
    for p in pts:
        m.cyl(r, 0.008, p, mat, axis=y_dir, seg=6)


def drawer_face(m, cx, cy, z, w, h, mat, hmat="chrome"):
    m.box((w, h, 0.02), (cx, cy, z), mat, 0.004)
    handle(m, (cx, cy + h * 0.25, z + 0.01), min(0.14, w * 0.5), hmat)


def mattress(m, w, l, y, cz, top="crew_sheet", th=0.15):
    m.box((w, th, l), (0, y, cz), "fabric_grey", 0.03)
    cush(m, (w - 0.02, 0.03, l - 0.02), (0, y + th / 2, cz), top, 0.01, seam="crew_seam")


def blanket(m, w, l, y, cz, mat, th=0.05):
    m.box((w, th, l), (0, y, cz), mat, 0.02)
    m.box((w + 0.02, th * 0.9, 0.05), (0, y + 0.002, cz - l / 2 + 0.03), "crew_sheet", 0.01)


def pillow(m, pos, w=0.5, mat="crew_pillow", d=0.32):
    cush(m, (w, 0.1, d), pos, mat, 0.04, seam=None)


def led(m, pos, size=(0.05, 0.012, 0.012), mat="em_cyan"):
    m.box(size, pos, mat)


# ================================================================== BED
@reg("bed", "single bunk")
def _(m, rng):
    m.box((0.92, 0.2, 2.02), (0, 0.32, 0), "hull_mid", 0.015)
    legs(m, -0.42, 0.42, -0.94, 0.94, 0.22, 0.03, "black_metal", 8)
    m.box((0.92, 0.5, 0.05), (0, 0.55, -1.0), "hull_dark", 0.015)          # headboard
    m.box((0.92, 0.35, 0.05), (0, 0.48, 1.0), "hull_dark", 0.015)
    mattress(m, 0.86, 1.94, 0.5, 0)
    pillow(m, (0, 0.6, -0.78))
    blanket(m, 0.88, 1.15, 0.6, 0.35, "fabric_navy")
    for k in range(3):
        drawer_face(m, -0.25 + 0.25 * k, 0.32, 1.02, 0.22, 0.14, "hull_dark")
    led(m, (0.3, 0.72, -0.965), (0.14, 0.03, 0.012), "em_warm")


@reg("bed", "bunk bed")
def _(m, rng):
    W, L = 0.9, 2.0
    for x in (-W / 2 - 0.03, W / 2 + 0.03):
        for z in (-L / 2, L / 2):
            m.box((0.06, 1.95, 0.06), (x, 0.975, z), "hull_dark", 0.01)
    for y, bl, pl in ((0.4, "fabric_teal", "crew_pillow"), (1.3, "fabric_red", "crew_pillow")):
        m.box((W + 0.06, 0.05, L), (0, y - 0.05, 0), "steel", 0.01)
        m.box((0.04, 0.12, L), (-W / 2 - 0.03, y + 0.06, 0), "steel", 0.008)
        m.box((0.04, 0.12, L), (W / 2 + 0.03, y + 0.06, 0), "steel", 0.008)
        mattress(m, W - 0.04, L - 0.1, y + 0.05, 0)
        pillow(m, (0, y + 0.17, -0.75), 0.5, pl)
        blanket(m, W - 0.06, 1.1, y + 0.16, 0.35, bl)
    for k in range(6):   # ladder on the +x side
        m.box((0.05, 0.03, 0.03), (W / 2 + 0.1, 0.3 + k * 0.28, 0.7), "chrome")
    m.box((0.03, 1.6, 0.03), (W / 2 + 0.1, 1.05, 0.68), "steel")
    m.box((0.03, 1.6, 0.03), (W / 2 + 0.1, 1.05, 0.9), "steel")
    m.box((0.05, 1.6, 0.05), (W / 2 + 0.1, 1.05, 0.68), "steel")
    led(m, (0, 1.75, -1.0), (0.2, 0.03, 0.02), "em_warm")
    led(m, (0, 0.9, -1.0), (0.2, 0.03, 0.02), "em_warm")
    m.box((W, 0.3, 0.02), (0, 1.55, 0.98), "hull_dark", 0.005)


@reg("bed", "officer bed")
def _(m, rng):
    m.box((1.4, 0.3, 2.1), (0, 0.25, 0.02), "wood_dark", 0.02)
    m.box((1.5, 0.08, 2.15), (0, 0.42, 0.02), "wood_light", 0.02)
    mattress(m, 1.36, 2.0, 0.53, 0.02, "crew_sheet", 0.2)
    m.box((1.6, 1.0, 0.1), (0, 0.85, -1.05), "wood_dark", 0.02)                 # headboard
    m.box((1.3, 0.25, 0.04), (0, 1.0, -0.985), "hull_dark", 0.006)
    m.screen((0.5, 0.16), (0, 1.0, -0.96), "systems", bezel=0.01)
    for k in range(4):
        led(m, (-0.5 + k * 0.1, 0.8, -0.995), (0.04, 0.02, 0.012), ["em_green", "em_amber", "em_cyan", "em_green"][k])
    blanket(m, 1.4, 1.4, 0.68, 0.45, "fabric_teal", 0.08)
    m.box((1.42, 0.02, 0.18), (0, 0.72, 0.15), "gold_trim", 0.004)
    pillow(m, (-0.35, 0.72, -0.8), 0.55)
    pillow(m, (0.35, 0.72, -0.8), 0.55)
    for s in (-1, 1):
        m.box((0.35, 0.5, 0.4), (s * 0.95, 0.25, -0.8), "wood_dark", 0.015)
        m.box((0.3, 0.02, 0.35), (s * 0.95, 0.51, -0.8), "hull_dark")
        drawer_face(m, s * 0.95, 0.35, -0.6, 0.28, 0.12, "wood_light", "brass")


@reg("bed", "captain bed")
def _(m, rng):
    m.box((1.85, 0.32, 2.2), (0, 0.24, 0), "paint_navy", 0.03)
    m.box((1.9, 0.05, 2.25), (0, 0.42, 0), "gold_trim", 0.01)
    mattress(m, 1.8, 2.1, 0.55, 0, "crew_sheet", 0.22)
    m.box((2.05, 1.3, 0.14), (0, 0.85, -1.12), "paint_navy", 0.03)
    m.box((1.9, 0.06, 0.16), (0, 1.53, -1.12), "gold_trim", 0.01)
    m.box((0.06, 1.1, 0.15), (-0.95, 0.85, -1.12), "gold_trim", 0.008)
    m.box((0.06, 1.1, 0.15), (0.95, 0.85, -1.12), "gold_trim", 0.008)
    m.screen((0.9, 0.35), (0, 1.15, -1.04), "starmap", bezel=0.02, bezel_mat="gold_trim")
    m.box((1.5, 0.03, 0.03), (0, 0.85, -1.03), "em_cyan")
    blanket(m, 1.82, 1.5, 0.71, 0.4, "paint_navy", 0.09)
    m.box((1.84, 0.02, 0.28), (0, 0.76, 0.2), "gold_trim", 0.004)
    for x in (-0.5, 0.5):
        pillow(m, (x, 0.75, -0.85), 0.7, "crew_pillow")
    pillow(m, (0, 0.8, -0.65), 0.5, "fabric_red", 0.25)
    m.box((1.6, 0.4, 0.5), (0, 0.22, 1.42), "paint_navy", 0.03)                # foot bench
    cush(m, (1.5, 0.08, 0.42), (0, 0.44, 1.42), "leather_black", 0.03)
    m.box((1.62, 0.03, 0.03), (0, 0.4, 1.68), "gold_trim")


@reg("bed", "folding cot")
def _(m, rng):
    m.box((0.7, 0.03, 1.9), (0, 0.42, 0), "fabric_olive" if False else "crew_olive", 0.008)
    for x in (-0.36, 0.36):
        m.box((0.03, 0.04, 1.94), (x, 0.42, 0), "steel", 0.006)
    for z in (-0.85, 0.85):
        m.box((0.76, 0.03, 0.04), (0, 0.4, z), "steel", 0.006)
    for z in (-0.6, 0.6):
        for s in (-1, 1):
            m.link((s * 0.36, 0.4, z), (-s * 0.36, 0.02, z + (0.25 if z > 0 else -0.25)), 0.017, "steel", 6)
        m.box((0.78, 0.03, 0.04), (0, 0.02, z + (0.25 if z > 0 else -0.25)), "black_metal", 0.006)
    m.cyl(0.11, 0.6, (0, 0.53, -0.75), "fabric_grey", axis="x", seg=12)
    m.cyl(0.115, 0.03, (0.2, 0.53, -0.75), "crew_seam", axis="x", seg=12)
    m.cyl(0.115, 0.03, (-0.2, 0.53, -0.75), "crew_seam", axis="x", seg=12)
    blanket(m, 0.66, 0.7, 0.47, 0.3, "fabric_tan", 0.05)


@reg("bed", "sleeping pod")
def _(m, rng):
    m.box((1.3, 0.16, 2.5), (0, 0.42, 0), "hull_light", 0.04)
    m.box((1.0, 0.36, 2.1), (0, 0.24, 0), "hull_dark", 0.03)
    legs(m, -0.55, 0.55, -1.1, 1.1, 0.34, 0.05, "black_metal", 8)
    m.box((1.1, 0.14, 2.3), (0, 0.58, 0), "hull_mid", 0.03)
    mattress(m, 0.95, 2.0, 0.72, -0.05, "crew_sheet", 0.12)
    pillow(m, (0, 0.82, -0.8), 0.5)
    m.sphere(0.66, (0, 0.72, 0), "glass_blue", seg=14, ring=6, scale=(1.0, 0.85, 1.85))     # canopy
    m.box((1.3, 0.05, 2.5), (0, 0.5, 0), "hull_light", 0.01)
    m.box((0.5, 0.04, 0.3), (0, 1.3, 0.85), "hull_light", 0.01)
    m.box((0.3, 0.04, 0.3), (0, 1.42, -0.9), "black_metal", 0.01)
    m.box((0.05, 0.05, 2.5), (0.5, 0.52, 0), "em_cyan")
    m.box((0.05, 0.05, 2.5), (-0.5, 0.52, 0), "em_cyan")
    m.screen((0.22, 0.16), (0.63, 0.35, 1.26), "lifesigns", rot=(0, 0.25, 0), bezel=0.01)
    m.cyl(0.05, 0.12, (0.0, 0.44, 1.33), "chrome", axis="z", seg=10)


@reg("bed", "hammock frame")
def _(m, rng):
    for z in (-1.25, 1.25):
        m.link((-0.5, 0.0, z), (0, 1.6, z), 0.03, "steel")
        m.link((0.5, 0.0, z), (0, 1.6, z), 0.03, "steel")
        m.box((1.1, 0.05, 0.07), (0, 0.025, z), "black_metal", 0.008)
        m.box((0.16, 0.06, 0.08), (0, 1.62, z), "hull_dark", 0.01)
    m.cyl(0.025, 2.5, (0, 1.65, 0), "steel", axis="z", seg=10)
    m.box((1.0, 0.03, 0.05), (0, 0.3, -1.25), "steel", 0.005)
    m.box((1.0, 0.03, 0.05), (0, 0.3, 1.25), "steel", 0.005)
    n = 12
    pts = [(0, 1.15 - 0.45 * math.cos((k / n - 0.5) * PI * 0.98) + 0.0, -1.1 + 2.2 * k / n) for k in range(n + 1)]
    for a, b in zip(pts[:-1], pts[1:]):
        m.link((0, a[1], a[2]), (0, b[1], b[2]), 0.02, "fabric_tan", 4) if False else None
        my, mz = (a[1] + b[1]) / 2, (a[2] + b[2]) / 2
        ang = math.atan2(b[1] - a[1], b[2] - a[2])
        m.box((0.75, 0.035, math.hypot(b[1] - a[1], b[2] - a[2]) + 0.01), (0, my, mz), "fabric_tan", 0.012, rot=(-ang, 0, 0))
    for z, s in ((-1.1, -1), (1.1, 1)):
        y0 = pts[0][1] if s < 0 else pts[-1][1]
        for x in (-0.3, 0, 0.3):
            m.link((x, y0, z), (0, 1.6, s * 1.25), 0.008, "crew_seam", 4)
    pillow(m, (0, 0.78, -0.85), 0.45, "fabric_red", 0.3)
    blanket(m, 0.7, 0.9, 0.7, 0.55, "crew_olive", 0.04)


@reg("bed", "recliner sleeper")
def _(m, rng):
    m.box((0.95, 0.12, 1.1), (0, 0.22, 0.0), "black_metal", 0.02)
    m.cyl(0.09, 0.2, (0, 0.12, 0), "steel", seg=12)
    cush(m, (0.72, 0.16, 0.85), (0, 0.43, 0.05), "leather_brown", 0.05, grid=3)
    # tilted backrest and footrest
    m.box((0.72, 0.16, 1.05), (0, 0.72, -0.72), "leather_brown", 0.05, rot=(0.9, 0, 0))
    cush(m, (0.3, 0.12, 0.3), (0, 1.15, -1.02), "leather_black", 0.04, seam=None)
    m.box((0.68, 0.14, 0.75), (0, 0.32, 0.9), "leather_brown", 0.05, rot=(-0.25, 0, 0))
    m.box((0.5, 0.08, 0.25), (0, 0.14, 1.28), "black_metal", 0.01)
    for s in (-1, 1):
        m.box((0.13, 0.22, 1.0), (s * 0.47, 0.55, -0.05), "leather_black", 0.04)
        m.box((0.15, 0.04, 0.25), (s * 0.47, 0.68, 0.35), "chrome", 0.008)
    m.box((0.6, 0.2, 0.02), (0, 0.43, 0.06), "crew_seam")
    blanket(m, 0.64, 0.6, 0.53, 0.55, "fabric_grey", 0.04)
    led(m, (0.47, 0.68, 0.48), (0.03, 0.01, 0.03), "em_green")


@reg("bed", "couch bed")
def _(m, rng):
    m.box((2.0, 0.18, 0.95), (0, 0.29, -0.15), "black_metal", 0.02)
    legs(m, -0.95, 0.95, -0.55, 0.3, 0.2, 0.03, "black_metal", 8)
    for k in range(3):
        cush(m, (0.62, 0.2, 0.85), (-0.66 + 0.66 * k, 0.48, -0.1), "fabric_grey", 0.05, grid=2)
    for k in range(3):
        cush(m, (0.62, 0.55, 0.22), (-0.66 + 0.66 * k, 0.85, -0.5), "fabric_grey", 0.06, grid=None)
    for s in (-1, 1):
        cush(m, (0.18, 0.55, 0.95), (s * 1.09, 0.5, -0.1), "fabric_grey", 0.05, seam=None)
    # pull out section
    m.box((1.9, 0.05, 0.05), (0, 0.32, 0.55), "steel")
    cush(m, (1.9, 0.14, 0.95), (0, 0.4, 1.0), "fabric_grey", 0.04, grid=3)
    blanket(m, 1.6, 0.5, 0.5, 1.05, "crew_mustard", 0.05)
    pillow(m, (0.5, 0.65, -0.25), 0.5, "crew_mustard", 0.25)


@reg("bed", "fold-down wall bed")
def _(m, rng):
    m.box((1.1, 2.2, 0.25), (0, 0.1, 0.125), "hull_mid", 0.02)                     # cabinet back
    m.box((1.0, 0.1, 0.3), (0, 1.15, 0.14), "hull_dark", 0.01)
    m.box((1.0, 0.06, 2.0), (0, -0.55, 1.1), "hull_dark", 0.015)
    mattress(m, 0.96, 1.96, -0.44, 1.1, "crew_sheet", 0.14)
    pillow(m, (0, -0.32, 0.5), 0.5)
    blanket(m, 0.92, 1.0, -0.36, 1.55, "paint_teal", 0.05)
    for s in (-1, 1):
        m.link((s * 0.45, -0.55, 2.03), (s * 0.45, -1.05, 2.03), 0.02, "steel", 6)
        m.box((0.08, 0.02, 0.1), (s * 0.45, -1.06, 2.03), "black_metal")
        m.link((s * 0.52, -0.5, 1.9), (s * 0.52, 0.5, 0.15), 0.008, "chrome", 4)
    led(m, (0, 1.15, 0.31), (0.3, 0.03, 0.012), "em_amber")
    m.box((0.9, 0.7, 0.02), (0, 0.5, 0.26), "hull_light", 0.005)


make("bed", [
    (["single bunk", "bunk bed", "officer bed", "captain bed", "folding cot", "sleeping pod", "hammock frame",
      "recliner sleeper", "couch bed"], "floor", ["crew", "bed"], True, None),
    (["fold-down wall bed"], "wall", ["crew", "bed"], True, 1.0),
])


# ================================================================== LOCKER
def vents(m, cx, y0, z, w, n=5, gap=0.025, mat="black_metal"):
    for k in range(n):
        m.box((w, 0.008, 0.01), (cx, y0 + k * gap, z), mat)


def keypad(m, pos, rot=(0, 0, 0)):
    x, y, z = pos
    m.box((0.1, 0.14, 0.02), (x, y, z), "black_metal", 0.004)
    m.box((0.06, 0.025, 0.006), (x, y + 0.04, z + 0.012), "em_green")
    for r in range(3):
        for c in range(3):
            m.box((0.014, 0.014, 0.006), (x - 0.025 + c * 0.025, y + 0.005 - r * 0.026, z + 0.012), "plastic_grey")


@reg("locker", "tall vented locker")
def _(m, rng):
    m.box((0.5, 1.85, 0.5), (0, 0.925, 0), "hull_mid", 0.015)
    m.box((0.46, 1.75, 0.02), (0, 0.93, 0.255), "paint_blue", 0.008)
    vents(m, 0, 1.55, 0.267, 0.3, 6, 0.03)
    vents(m, 0, 0.2, 0.267, 0.3, 4, 0.03)
    handle(m, (0.15, 1.0, 0.265), 0.16, "chrome", False)
    m.box((0.12, 0.05, 0.01), (0, 1.35, 0.266), "brass")
    m.box((0.5, 0.05, 0.5), (0, 1.86, 0), "hull_dark", 0.01)
    m.box((0.52, 0.06, 0.52), (0, 0.03, 0), "black_metal", 0.01)
    m.box((0.02, 1.7, 0.02), (-0.15, 0.93, 0.27), "hull_dark")
    m.cyl(0.01, 0.01, (0.15, 0.7, 0.27), "steel", axis="z", seg=6)


@reg("locker", "double locker bank")
def _(m, rng):
    m.box((1.0, 1.8, 0.5), (0, 0.9, 0), "hull_dark", 0.015)
    for s, c in ((-1, "paint_orange"), (1, "paint_teal")):
        m.box((0.46, 1.7, 0.02), (s * 0.25, 0.9, 0.255), c, 0.006)
        vents(m, s * 0.25, 1.5, 0.267, 0.26, 5, 0.03)
        handle(m, (s * 0.25 - s * 0.14, 1.0, 0.265), 0.14, "chrome", False)
        m.box((0.1, 0.05, 0.01), (s * 0.25, 1.3, 0.266), "plastic_white")
    m.box((1.04, 0.06, 0.54), (0, 1.82, 0), "black_metal", 0.01)
    m.box((1.04, 0.08, 0.54), (0, 0.04, 0), "black_metal", 0.01)


@reg("locker", "wardrobe")
def _(m, rng):
    m.box((1.1, 2.0, 0.6), (0, 1.0, 0), "wood_dark", 0.02)
    for s in (-1, 1):
        m.box((0.52, 1.86, 0.03), (s * 0.27, 1.02, 0.31), "wood_light", 0.012)
        m.box((0.4, 1.7, 0.012), (s * 0.27, 1.02, 0.33), "wood_dark", 0.006)
        m.box((0.03, 0.2, 0.03), (-s * 0.04 + 0 * s, 1.0, 0.345), "brass", 0.005) if False else None
        handle(m, (s * 0.06, 1.0, 0.335), 0.18, "brass", False)
    m.box((1.16, 0.06, 0.66), (0, 2.03, 0), "wood_light", 0.015)
    m.box((1.0, 0.12, 0.5), (0, 0.06, 0.02), "black_metal", 0.01)
    for x in (-0.5, 0.5):
        m.cyl(0.04, 0.1, (x, 0.05, 0.24), "brass", seg=8)
    m.box((0.9, 0.35, 0.02), (0, 0.32, 0.32), "wood_light", 0.008)
    drawer_face(m, 0, 0.32, 0.335, 0.9, 0.3, "wood_light", "brass") if False else None


@reg("locker", "sea chest")
def _(m, rng):
    m.box((1.0, 0.45, 0.55), (0, 0.225, 0), "wood_dark", 0.02)
    m.box((1.02, 0.1, 0.57), (0, 0.5, 0), "wood_dark", 0.03)
    m.cyl(0.285, 1.0, (0, 0.5, 0), "wood_dark", axis="x", seg=14, r2=None) if False else None
    for x in (-0.4, -0.15, 0.15, 0.4):
        m.box((0.05, 0.56, 0.58), (x, 0.28, 0), "brass", 0.008)
    for s in (-1, 1):
        m.box((0.08, 0.1, 0.1), (s * 0.55, 0.3, 0), "brass", 0.01)
        m.torus(0.04, 0.008, (s * 0.58, 0.3, 0), "brass", axis="x", seg=10, tseg=4)
    m.box((0.12, 0.14, 0.03), (0, 0.42, 0.29), "brass", 0.006)
    m.box((0.05, 0.05, 0.03), (0, 0.42, 0.31), "black_metal")
    for x in (-0.46, 0.46):
        for z in (-0.24, 0.24):
            m.box((0.06, 0.06, 0.06), (x, 0.03, z), "brass", 0.01)


@reg("locker", "footlocker")
def _(m, rng):
    m.box((0.9, 0.42, 0.5), (0, 0.24, 0), "hull_dark", 0.02)
    m.box((0.9, 0.06, 0.5), (0, 0.48, 0), "hull_mid", 0.02)
    m.box((0.9, 0.02, 0.5), (0, 0.44, 0.005), "hazard_yellow")
    for x in (-0.35, 0.35):
        m.box((0.05, 0.42, 0.52), (x, 0.24, 0), "steel", 0.008)
        m.box((0.03, 0.04, 0.03), (x, 0.44, 0.26), "chrome")
    m.box((0.1, 0.12, 0.03), (0, 0.4, 0.26), "chrome", 0.006)
    m.box((0.5, 0.15, 0.01), (0, 0.24, 0.255), "plastic_white")
    for s in (-1, 1):
        m.box((0.04, 0.09, 0.05), (s * 0.47, 0.3, 0), "black_metal", 0.008)
    m.box((0.9, 0.04, 0.54), (0, 0.02, 0), "black_metal", 0.008)


@reg("locker", "under-bed drawers")
def _(m, rng):
    m.box((1.2, 0.22, 0.75), (0, 0.13, 0), "wood_dark", 0.015)
    for k in range(2):
        m.box((0.58, 0.18, 0.03), (-0.3 + 0.6 * k, 0.13, 0.385), "wood_light", 0.008)
        handle(m, (-0.3 + 0.6 * k, 0.16, 0.4), 0.14, "steel")
    m.box((0.2, 0.03, 0.02), (0.3, 0.12, 0.4), "plastic_white") if False else None
    for x in (-0.55, 0.55):
        for z in (-0.32, 0.32):
            m.cyl(0.03, 0.03, (x, 0.015, z), "rubber", seg=8)
    # half open drawer
    m.box((0.54, 0.03, 0.55), (0.3, 0.06, 0.66), "wood_light", 0.005) if False else None


@reg("locker", "gear locker keypad")
def _(m, rng):
    m.box((0.9, 1.4, 0.6), (0, 0.85, 0), "gunmetal", 0.02)
    m.box((0.94, 0.15, 0.64), (0, 0.075, 0), "black_metal", 0.01)
    m.box((0.82, 1.28, 0.03), (0, 0.85, 0.31), "hull_dark", 0.01)
    for k in range(3):
        m.box((0.76, 0.02, 0.012), (0, 0.5 + 0.35 * k, 0.33), "hazard_yellow")
    keypad(m, (0.25, 1.0, 0.33))
    m.box((0.05, 0.3, 0.03), (0.32, 0.75, 0.33), "chrome", 0.008)
    m.box((0.2, 0.08, 0.012), (-0.2, 1.3, 0.33), "hazard_yellow")
    m.box((0.2, 0.08, 0.012), (-0.2, 1.3, 0.335), "black_metal") if False else None
    for x in (-0.38, 0.38):
        for y in (0.3, 1.4):
            m.cyl(0.013, 0.01, (x, y, 0.33), "chrome", axis="z", seg=6)
    m.box((0.9, 0.06, 0.6), (0, 1.58, 0), "steel", 0.01)
    m.box((0.5, 0.12, 0.01), (0, 1.5, 0.33), "plastic_white")


@reg("locker", "shoe rack")
def _(m, rng):
    for x in (-0.4, 0.4):
        m.box((0.04, 0.9, 0.3), (x, 0.45, 0), "wood_dark", 0.008)
    for k in range(4):
        m.box((0.84, 0.03, 0.3), (0, 0.06 + k * 0.28, 0), "wood_light", 0.006)
        for b in range(2):
            m.box((0.11, 0.07, 0.28), (-0.2 + 0.4 * b, 0.12 + k * 0.28 + 0.0, 0), "black_metal", 0.02) if k in (0, 2) else None
    m.box((0.84, 0.06, 0.02), (0, 0.6, -0.14), "wood_dark")
    m.box((0.84, 0.6, 0.02), (0, 0.45, -0.14), "wood_dark")


@reg("locker", "wall cabinet")
def _(m, rng):
    m.box((0.9, 0.6, 0.3), (0, 0, 0.15), "hull_light", 0.015)
    for s in (-1, 1):
        m.box((0.43, 0.54, 0.02), (s * 0.22, 0, 0.31), "hull_mid", 0.006)
        handle(m, (-s * 0.02 + s * 0.05, 0.0, 0.32), 0.1, "chrome", False)
    m.box((0.9, 0.03, 0.32), (0, 0.31, 0.16), "hull_dark", 0.008)
    led(m, (0, -0.31, 0.3), (0.6, 0.012, 0.012), "em_warm")
    m.box((0.06, 0.04, 0.02), (0.38, 0.25, 0.32), "em_green")
    bolts(m, [(-0.41, 0.26, 0.316), (0.41, 0.26, 0.316), (-0.41, -0.26, 0.316), (0.41, -0.26, 0.316)], 0.008, "chrome", "z")


@reg("locker", "mirror cabinet")
def _(m, rng):
    m.box((0.6, 0.8, 0.14), (0, 0, 0.07), "plastic_white", 0.015)
    m.box((0.54, 0.74, 0.02), (0, 0, 0.15), "chrome", 0.008)
    m.box((0.5, 0.7, 0.01), (0, 0, 0.16), "glass_blue")
    m.box((0.5, 0.04, 0.011), (-0.0, 0.2, 0.165), "glass") if False else None
    m.link((-0.15, -0.3, 0.166), (0.1, 0.3, 0.166), 0.008, "glass", 4)
    m.link((-0.05, -0.3, 0.166), (0.2, 0.3, 0.166), 0.004, "glass", 4)
    m.box((0.62, 0.08, 0.16), (0, 0.44, 0.08), "steel", 0.01)
    m.box((0.5, 0.03, 0.03), (0, 0.38, 0.17), "em_white")
    m.box((0.03, 0.14, 0.03), (0.22, -0.0, 0.18), "chrome", 0.006)


@reg("locker", "kit bags on hooks")
def _(m, rng):
    m.box((1.2, 0.14, 0.05), (0, 0.55, 0.025), "wood_dark", 0.01)
    m.box((1.2, 0.05, 0.12), (0, 0.66, 0.06), "wood_dark", 0.008)
    m.box((1.2, 1.3, 0.03), (0, -0.05, 0.015), "hull_dark", 0.008)
    for k, (x, c, w) in enumerate(((-0.4, "crew_olive", 0.32), (0.05, "fabric_navy", 0.38), (0.45, "paint_orange", 0.28))):
        m.cyl(0.012, 0.13, (x, 0.55, 0.11), "chrome", axis="z", seg=6)
        m.sphere(0.02, (x, 0.55, 0.175), "chrome", 6, 4)
        m.box((w, 0.6 + 0.06 * k, 0.24), (x, 0.2 - 0.03 * k, 0.24), c, 0.05)
        m.box((w - 0.04, 0.05, 0.26), (x, 0.3, 0.24), "crew_seam", 0.01)
        m.box((w * 0.7, 0.2, 0.02), (x, 0.05, 0.37), "hull_dark", 0.008)
        m.box((0.04, 0.5, 0.26), (x + w / 3, 0.15, 0.245), "crew_seam") if False else None
        m.link((x - 0.03, 0.55, 0.13), (x - 0.06, 0.45, 0.2), 0.008, "leather_black", 4)
    m.box((0.5, 0.04, 0.34), (0, -0.7, 0.17), "wood_dark", 0.005) if False else None


@reg("locker", "display cabinet")
def _(m, rng):
    m.box((0.8, 0.9, 0.3), (0, 0, 0.15), "wood_dark", 0.015)
    m.box((0.7, 0.8, 0.02), (0, 0, 0.04), "hull_dark")
    for k in range(2):
        m.box((0.7, 0.02, 0.24), (0, -0.12 + 0.32 * k, 0.17), "wood_light")
    m.box((0.68, 0.78, 0.012), (0, 0, 0.305), "glass_blue")
    m.box((0.72, 0.04, 0.03), (0, 0.4, 0.305), "wood_light", 0.005)
    m.box((0.72, 0.04, 0.03), (0, -0.4, 0.305), "wood_light", 0.005)
    m.box((0.04, 0.8, 0.03), (-0.34, 0, 0.305), "wood_light", 0.005)
    m.box((0.04, 0.8, 0.03), (0.34, 0, 0.305), "wood_light", 0.005)
    m.cyl(0.05, 0.1, (-0.2, -0.05, 0.16), "gold_trim", seg=10, r2=0.03)
    m.sphere(0.06, (0.05, 0.05, 0.14), "brass", 10, 6)
    m.box((0.12, 0.08, 0.1), (0.2, -0.07, 0.16), "paint_red", 0.01) if False else None
    m.box((0.14, 0.02, 0.1), (0.15, -0.11, 0.16), "gold_trim")
    handle(m, (0.28, 0, 0.32), 0.16, "brass", False)


make("locker", [
    (["tall vented locker", "double locker bank", "wardrobe", "sea chest", "footlocker", "under-bed drawers",
      "gear locker keypad", "shoe rack"], "floor", ["crew", "locker"], True, None),
    (["wall cabinet", "mirror cabinet", "kit bags on hooks", "display cabinet"], "wall", ["crew", "locker"], False, 1.6),
])


# ================================================================== DESK
def monitor(m, pos, w=0.5, tex="systems", ry=0.0):
    x, y, z = pos
    m.box((0.22, 0.02, 0.16), (x, y + 0.01, z), "black_metal")
    m.box((0.04, 0.16, 0.04), (x, y + 0.09, z - 0.02), "black_metal")
    m.screen((w, w * 0.58), (x, y + 0.18 + w * 0.29, z), tex, rot=(-0.05, ry, 0), bezel=0.012)


def kbd(m, pos, w=0.42):
    x, y, z = pos
    m.box((w, 0.02, 0.15), (x, y + 0.01, z), "plastic_black")
    m.box((w - 0.04, 0.005, 0.11), (x, y + 0.022, z), "gunmetal")
    m.box((0.06, 0.01, 0.09), (x + w / 2 + 0.1, y + 0.005, z), "plastic_grey")


def desk_lamp(m, x, y, z, mat="paint_orange"):
    m.cyl(0.06, 0.02, (x, y + 0.01, z), "black_metal", seg=10)
    m.link((x, y + 0.02, z), (x + 0.05, y + 0.28, z - 0.06), 0.008, mat)
    m.link((x + 0.05, y + 0.28, z - 0.06), (x + 0.16, y + 0.34, z + 0.0), 0.008, mat)
    m.cyl(0.05, 0.08, (x + 0.19, y + 0.3, z + 0.02), mat, axis="x", r2=0.025, seg=10, rot=(0, 0, -0.5))


def desk_body(m, w, d, h, top="wood_light", frame="black_metal", t=0.04):
    m.box((w, t, d), (0, h - t / 2, 0), top, 0.012)
    m.box((w - 0.02, 0.015, d - 0.02), (0, h - t - 0.007, 0), frame)


def pedestal(m, x, d, h, n, mat="hull_mid", w=0.4, hm="chrome"):
    m.box((w, h, d - 0.04), (x, h / 2, 0), mat, 0.01)
    dh = (h - 0.06) / n
    for k in range(n):
        drawer_face(m, x, 0.04 + dh * (k + 0.5), d / 2 - 0.02, w - 0.03, dh - 0.02, "hull_light" if mat == "hull_mid" else "wood_light", hm)


@reg("desk", "officer desk")
def _(m, rng):
    W, D, H = 1.8, 0.85, 0.76
    desk_body(m, W, D, H, "wood_dark")
    m.box((W - 0.02, 0.02, D + 0.02), (0, H - 0.04, 0), "gold_trim", 0.004) if False else None
    m.box((W + 0.02, 0.012, 0.012), (0, H + 0.002, D / 2), "gold_trim")
    pedestal(m, -0.62, D, H - 0.05, 3, "wood_dark", 0.5, "brass")
    pedestal(m, 0.62, D, H - 0.05, 2, "wood_dark", 0.5, "brass")
    m.box((0.6, 0.6, 0.02), (0, 0.3, -0.38), "wood_dark")
    m.box((0.65, 0.01, 0.4), (0, H + 0.005, 0.0), "leather_black", 0.004)
    monitor(m, (0.25, H, -0.15), 0.45, "comm")
    kbd(m, (0.2, H, 0.15))
    desk_lamp(m, -0.7, H, -0.25, "brass")
    m.box((0.28, 0.06, 0.1), (-0.3, H + 0.03, -0.3), "wood_light", 0.01)
    m.box((0.14, 0.1, 0.06), (-0.6, H + 0.05, 0.15), "gold_trim", 0.01)


@reg("desk", "writing desk")
def _(m, rng):
    W, D, H = 1.2, 0.6, 0.75
    m.box((W, 0.035, D), (0, H - 0.0175, 0), "wood_light", 0.01)
    for x in (-1, 1):
        for z in (-1, 1):
            m.link((x * (W / 2 - 0.05), H - 0.04, z * (D / 2 - 0.05)), (x * (W / 2 - 0.08), 0.0, z * (D / 2 - 0.08)), 0.02, "wood_dark", 8)
    m.box((W - 0.16, 0.03, 0.03), (0, 0.3, D / 2 - 0.08), "wood_dark")
    m.box((W - 0.16, 0.03, 0.03), (0, 0.3, -D / 2 + 0.08), "wood_dark")
    m.box((0.5, 0.09, D - 0.1), (-0.25, H - 0.08, 0), "wood_dark", 0.008)
    drawer_face(m, -0.25, H - 0.08, D / 2 - 0.045, 0.46, 0.08, "wood_light", "brass")
    m.box((0.5, 0.008, 0.36), (0.15, H + 0.005, 0.02), "leather_brown")
    m.box((0.28, 0.005, 0.2), (0.15, H + 0.013, 0.02), "crew_pillow") if False else None
    m.box((0.22, 0.01, 0.3), (0.15, H + 0.014, 0.02), "crew_sheet", 0.002)
    m.cyl(0.03, 0.09, (-0.45, H + 0.045, -0.15), "ceramic", seg=10)
    for k in range(2):
        m.link((-0.45, H + 0.09, -0.15), (-0.5 + 0.08 * k, H + 0.2, -0.15), 0.004, "chrome" if k else "paint_red", 4)
    m.box((0.2, 0.05, 0.14), (-0.1, H + 0.025, -0.2), "paint_red", 0.006)
    m.box((0.2, 0.03, 0.14), (-0.1, H + 0.065, -0.2), "paint_blue", 0.006)


@reg("desk", "corner desk")
def _(m, rng):
    H = 0.75
    pts = [(-0.9, -0.9), (0.9, -0.9), (0.9, -0.3), (-0.3, -0.3), (-0.3, 0.9), (-0.9, 0.9)]
    m.prism(pts, 0.035, (0, H - 0.035, 0), "wood_light", "xz", bevel=0.008)
    for (x, z) in ((-0.85, -0.85), (0.85, -0.35), (-0.35, 0.85), (-0.85, 0.85), (-0.35, -0.35)):
        m.box((0.05, H - 0.035, 0.05), (x, (H - 0.035) / 2, z), "black_metal", 0.006)
    m.box((1.7, 0.03, 0.03), (0, 0.5, -0.87), "black_metal")
    m.box((0.03, 0.03, 1.7), (-0.87, 0.5, 0), "black_metal")
    monitor(m, (-0.2, H, -0.62), 0.5, "radar")
    monitor(m, (-0.62, H, -0.2), 0.42, "graph", 1.2)
    kbd(m, (-0.5, H, -0.5))
    m.box((0.5, 0.05, 0.4), (0.55, 0.3, -0.6), "hull_dark", 0.01)
    m.box((0.5, 0.35, 0.4), (0.55, 0.225, -0.6), "hull_mid", 0.01)
    drawer_face(m, 0.55, 0.3, -0.39, 0.44, 0.16, "hull_light")
    led(m, (0.7, 0.4, -0.385), (0.03, 0.03, 0.01), "em_green")


@reg("desk", "workstation")
def _(m, rng):
    W, D, H = 1.5, 0.75, 0.74
    desk_body(m, W, D, H, "plastic_white", "hull_mid")
    for x in (-1, 1):
        m.box((0.05, H - 0.05, D - 0.1), (x * (W / 2 - 0.05), (H - 0.05) / 2, 0), "hull_light", 0.01)
    m.box((W - 0.1, 0.5, 0.02), (0, 0.4, -D / 2 + 0.1), "hull_mid")
    monitor(m, (-0.35, H, -0.2), 0.5, "diagnostic")
    monitor(m, (0.3, H, -0.2), 0.42, "schematic")
    kbd(m, (0.0, H, 0.15))
    desk_lamp(m, 0.62, H, -0.2, "paint_red")
    m.box((0.3, 0.008, 0.3), (0, H + 0.006, 0.1), "rubber") if False else None
    m.box((0.2, 0.35, 0.44), (0.5, 0.2, 0.0), "hull_dark", 0.01)
    led(m, (0.5, 0.3, 0.225), (0.08, 0.012, 0.01), "em_cyan")
    m.box((0.2, 0.18, 0.1), (-0.6, H + 0.09, -0.3), "hull_mid", 0.01)
    led(m, (-0.6, H + 0.09, -0.245), (0.14, 0.02, 0.008), "em_amber")


@reg("desk", "drafting table")
def _(m, rng):
    for s in (-1, 1):
        m.box((0.06, 0.06, 0.7), (s * 0.5, 0.03, 0), "black_metal", 0.008)
        m.box((0.05, 0.8, 0.05), (s * 0.5, 0.45, -0.1), "steel", 0.008)
    m.box((1.0, 0.04, 0.05), (0, 0.5, 0.2), "steel")
    m.box((1.1, 0.04, 0.05), (0, 0.15, -0.1), "steel")
    m.box((1.2, 0.04, 0.85), (0, 1.0, 0.0), "wood_light", 0.01, rot=(-0.4, 0, 0))
    m.box((1.1, 0.01, 0.75), (0, 1.03, 0.0), "paint_green", 0.003, rot=(-0.4, 0, 0)) if False else None
    m.box((1.0, 0.006, 0.6), (0, 1.03, 0.02), "crew_sheet", rot=(-0.4, 0, 0))
    m.box((1.0, 0.03, 0.04), (0, 0.82, 0.31), "brass", rot=(-0.4, 0, 0))                # t-square
    m.box((0.04, 0.03, 0.6), (-0.3, 1.04, 0.0), "steel", rot=(-0.4, 0, 0))
    for k in range(3):
        m.box((0.014, 0.005, 0.5 - 0.1 * k), (-0.05 + 0.08 * k, 1.036, 0.03), "paint_blue", rot=(-0.4, 0, 0))
    m.box((0.5, 0.05, 0.05), (0, 0.9, 0.52), "wood_dark") if False else None
    m.box((0.4, 0.04, 0.06), (0, 0.78, 0.4), "wood_dark", 0.005, rot=(-0.4, 0, 0))


@reg("desk", "standing desk")
def _(m, rng):
    W, D, H = 1.4, 0.7, 1.1
    m.box((W, 0.035, D), (0, H - 0.0175, 0), "wood_light", 0.01)
    for s in (-1, 1):
        m.box((0.08, 0.05, D - 0.1), (s * 0.55, 0.025, 0), "black_metal", 0.01)
        m.box((0.07, H - 0.08, 0.07), (s * 0.55, 0.05 + (H - 0.08) / 2, 0), "black_metal", 0.01)
        m.box((0.05, H * 0.5, 0.05), (s * 0.55, H - 0.06 - H * 0.25, 0.0), "steel") if False else None
        m.box((0.08, 0.2, 0.08), (s * 0.55, H - 0.14, 0), "steel", 0.006)
    m.box((W - 0.2, 0.04, 0.06), (0, H - 0.06, -0.2), "black_metal")
    m.box((0.2, 0.06, 0.05), (0.4, H - 0.06, 0.32), "black_metal", 0.008)
    led(m, (0.4, H - 0.06, 0.348), (0.14, 0.03, 0.008), "em_cyan")
    for k in range(3):
        led(m, (0.32 + 0.04 * k, H - 0.05, 0.351), (0.02, 0.012, 0.005), "em_white")
    monitor(m, (0.0, H, -0.2), 0.5, "vitals")
    kbd(m, (0.0, H, 0.15))
    m.box((0.6, 0.008, 0.28), (-0.4, H + 0.004, 0.05), "rubber", 0.003)
    m.cyl(0.05, 0.1, (-0.55, H + 0.05, -0.25), "steel", seg=10)


@reg("desk", "computer desk")
def _(m, rng):
    W, D, H = 1.3, 0.65, 0.76
    m.box((W, 0.035, D), (0, H - 0.0175, 0), "carbon", 0.01)
    for s in (-1, 1):
        m.box((0.04, H - 0.035, D - 0.04), (s * (W / 2 - 0.02), (H - 0.035) / 2, 0), "hull_dark", 0.008)
    m.box((W - 0.1, H * 0.5, 0.02), (0, H * 0.75, -D / 2 + 0.04), "hull_dark")
    m.box((0.5, 0.03, 0.55), (0.0, 0.62, 0.0), "hull_mid", 0.006)                    # keyboard tray
    m.box((0.36, 0.5, 0.5), (-0.4, 0.28, 0.0), "hull_dark", 0.01)                     # tower
    m.box((0.3, 0.44, 0.01), (-0.4, 0.28, 0.255), "black_metal")
    led(m, (-0.4, 0.4, 0.26), (0.2, 0.012, 0.005), "em_violet")
    led(m, (-0.4, 0.15, 0.26), (0.03, 0.03, 0.005), "em_green")
    monitor(m, (0.15, H, -0.05), 0.55, "starmap")
    kbd(m, (0.0, 0.635, 0.05))
    m.box((0.1, 0.1, 0.1), (0.5, H + 0.05, 0.15), "plastic_white", 0.01) if False else None
    for x in (-0.35, 0.35):
        m.box((0.16, 0.24, 0.12), (x + (-0.15 if x < 0 else 0.3), H + 0.12, -0.15), "hull_dark", 0.01)
        m.cyl(0.05, 0.005, (x + (-0.15 if x < 0 else 0.3), H + 0.17, -0.09), "gunmetal", axis="z", seg=10)


@reg("desk", "drawer console")
def _(m, rng):
    W, D, H = 1.4, 0.55, 0.85
    m.box((W, 0.04, D), (0, H - 0.02, 0), "steel", 0.01)
    m.box((W - 0.04, H - 0.14, D - 0.04), (0, 0.07 + (H - 0.14) / 2, 0), "hull_mid", 0.012)
    m.box((W, 0.08, D), (0, 0.04, 0), "black_metal", 0.008)
    rows = [(0.65, 4), (0.3, 4)] if False else None
    ys = [0.68, 0.5, 0.32]
    for r, y in enumerate(ys):
        for c in range(3):
            x = -0.46 + 0.46 * c
            drawer_face(m, x, y, D / 2, 0.42, 0.16, ["paint_blue", "hull_light", "paint_teal"][(r + c) % 3])
            m.box((0.1, 0.03, 0.006), (x, y - 0.05, D / 2 + 0.012), "plastic_white")
    led(m, (0.6, H + 0.005, -0.2), (0.14, 0.01, 0.08), "em_amber")
    m.screen((0.3, 0.12), (0.0, H + 0.13, -0.22), "bars", rot=(-0.45, 0, 0), bezel=0.01)
    m.box((0.32, 0.06, 0.06), (0, H + 0.03, -0.2), "black_metal", 0.006)


@reg("desk", "secretary desk")
def _(m, rng):
    W, D, H = 1.0, 0.5, 0.75
    m.box((W, 0.035, D), (0, H - 0.0175, 0), "wood_dark", 0.01)
    for x in (-1, 1):
        m.box((0.04, H - 0.035, D - 0.05), (x * (W / 2 - 0.02), (H - 0.035) / 2, 0), "wood_dark", 0.008)
    m.box((W - 0.06, 0.08, D - 0.06), (0, H - 0.075, 0), "wood_dark", 0.006)
    drawer_face(m, 0, H - 0.075, D / 2 - 0.03, 0.4, 0.07, "wood_light", "brass")
    # hutch
    m.box((W, 0.6, 0.22), (0, H + 0.3, -0.14), "wood_dark", 0.012)
    m.box((W - 0.08, 0.02, 0.2), (0, H + 0.34, -0.13), "wood_light")
    for k in range(3):
        m.box((0.28, 0.24, 0.02), (-0.3 + 0.3 * k, H + 0.2, -0.03), "wood_light", 0.006) if k != 1 else None
    m.box((0.28, 0.24, 0.012), (0, H + 0.2, -0.02), "glass_blue")
    m.box((0.28, 0.14, 0.02), (-0.3, H + 0.47, -0.03), "wood_light", 0.006)
    m.box((0.28, 0.14, 0.02), (0.3, H + 0.47, -0.03), "wood_light", 0.006)
    m.box((W + 0.06, 0.04, 0.26), (0, H + 0.62, -0.14), "wood_light", 0.01)
    m.box((0.5, 0.008, 0.3), (0, H + 0.005, 0.05), "leather_brown")
    handle(m, (0.3, H + 0.47, -0.02), 0.06, "brass", False)
    for x in (-0.4, 0.4):
        m.cyl(0.03, 0.02, (x * 1.0, 0.01, 0.15), "brass", seg=8) if False else None


@reg("desk", "fold-down wall desk")
def _(m, rng):
    m.box((0.9, 0.7, 0.12), (0, 0.0, 0.06), "hull_mid", 0.012)
    m.box((0.84, 0.64, 0.02), (0, 0.0, 0.125), "hull_light", 0.006)
    m.screen((0.34, 0.2), (0, 0.15, 0.14), "text", bezel=0.01)
    m.box((0.9, 0.04, 0.6), (0, -0.35, 0.42), "hull_light", 0.01)
    m.box((0.86, 0.006, 0.56), (0, -0.328, 0.42), "leather_black")
    for s in (-1, 1):
        m.link((s * 0.4, -0.36, 0.6), (s * 0.4, -0.75, 0.05), 0.012, "steel", 6)
        m.box((0.04, 0.05, 0.04), (s * 0.44, -0.35, 0.13), "black_metal", 0.006)
    m.box((0.2, 0.012, 0.14), (-0.2, -0.32, 0.4), "crew_sheet")
    m.cyl(0.03, 0.08, (0.3, -0.29, 0.5), "ceramic", seg=8)
    led(m, (0, -0.31, 0.135), (0.5, 0.015, 0.008), "em_warm")


make("desk", [
    (["officer desk", "writing desk", "corner desk", "workstation", "drafting table", "standing desk",
      "computer desk", "drawer console", "secretary desk"], "floor", ["crew", "desk"], True, None),
    (["fold-down wall desk"], "wall", ["crew", "desk"], False, 1.1),
])


# ================================================================== CHAIR
def star_base(m, y_top, r=0.3, n=5, mat="black_metal", h=0.07, caster=True):
    m.cyl(0.03, y_top - h, (0, (y_top - h) / 2 + h * 0.5, 0), "chrome", seg=10)
    m.cyl(0.055, 0.06, (0, h + 0.03, 0), mat, seg=10)
    for k in range(n):
        a = 2 * PI * k / n + 0.3
        x, z = r * math.cos(a), r * math.sin(a)
        m.link((0, h + 0.02, 0), (x, h, z), 0.02, mat, 6)
        if caster:
            m.sphere(0.03, (x, 0.03, z), "rubber", 8, 5)


@reg("chair", "swivel office chair")
def _(m, rng):
    star_base(m, 0.42)
    m.box((0.1, 0.06, 0.1), (0, 0.44, 0), "black_metal", 0.01)
    cush(m, (0.5, 0.09, 0.5), (0, 0.5, 0.02), "fabric_navy", 0.04)
    cush(m, (0.46, 0.55, 0.09), (0, 0.85, -0.25), "fabric_navy", 0.04, seam=None, )
    m.box((0.06, 0.25, 0.04), (0, 0.6, -0.24), "black_metal", 0.008)
    for s in (-1, 1):
        m.box((0.04, 0.03, 0.26), (s * 0.28, 0.72, 0.0), "plastic_black", 0.008)
        m.box((0.03, 0.2, 0.03), (s * 0.28, 0.62, -0.05), "black_metal")
    m.box((0.2, 0.03, 0.02), (0, 0.57, 0.0), "chrome") if False else None


@reg("chair", "mess chair")
def _(m, rng):
    for x in (-0.19, 0.19):
        m.link((x, 0.0, 0.2), (x, 0.44, 0.19), 0.014, "steel", 6)
        m.link((x, 0.0, -0.2), (x, 0.44, -0.19), 0.014, "steel", 6)
        m.link((x, 0.44, -0.19), (x, 0.88, -0.22), 0.014, "steel", 6)
        m.box((0.02, 0.02, 0.44), (x, 0.44, 0.0), "steel")
        m.box((0.02, 0.02, 0.4), (x, 0.2, 0), "steel")
    m.box((0.42, 0.04, 0.42), (0, 0.47, 0.0), "paint_blue", 0.015)
    m.box((0.4, 0.2, 0.03), (0, 0.79, -0.225), "paint_blue", 0.012)
    m.box((0.4, 0.05, 0.03), (0, 0.66, -0.225), "steel")
    for x in (-0.19, 0.19):
        for z in (-0.2, 0.2):
            m.cyl(0.02, 0.012, (x, 0.006, z), "rubber", seg=6)


@reg("chair", "stool")
def _(m, rng):
    cush(m, (0.36, 0.07, 0.36), (0, 0.65, 0), "leather_black", 0.025, seam=None)
    m.cyl(0.19, 0.06, (0, 0.65, 0), "leather_black", seg=16, bevel=0.015) if False else None
    m.cyl(0.14, 0.02, (0, 0.6, 0), "steel", seg=14)
    for k in range(3):
        a = 2 * PI * k / 3 + 0.5
        m.link((0.05 * math.cos(a), 0.6, 0.05 * math.sin(a)), (0.2 * math.cos(a), 0.0, 0.2 * math.sin(a)), 0.016, "steel", 6)
    m.torus(0.14, 0.01, (0, 0.25, 0), "chrome", seg=16, tseg=5)


@reg("chair", "folding chair")
def _(m, rng):
    for s in (-1, 1):
        x = s * 0.2
        m.link((x, 0.0, 0.2), (x, 0.44, -0.17), 0.012, "steel", 6)
        m.link((x, 0.0, -0.22), (x, 0.44, 0.17), 0.012, "steel", 6)
        m.link((x, 0.44, -0.2), (x, 0.9, -0.24), 0.012, "steel", 6)
        m.sphere(0.017, (x, 0.22, 0.0), "chrome", 8, 5)
    m.box((0.44, 0.02, 0.38), (0, 0.45, 0.02), "hull_dark", 0.008)
    m.box((0.42, 0.14, 0.02), (0, 0.72, -0.21), "hull_dark", 0.008)
    m.box((0.42, 0.14, 0.02), (0, 0.85, -0.235), "hull_dark", 0.008)
    m.box((0.44, 0.02, 0.02), (0, 0.44, 0.2), "steel")


@reg("chair", "armchair")
def _(m, rng):
    legs(m, -0.36, 0.36, -0.32, 0.32, 0.1, 0.03, "wood_dark", 8)
    m.box((0.85, 0.25, 0.8), (0, 0.22, 0), "fabric_teal", 0.05)
    cush(m, (0.58, 0.14, 0.62), (0, 0.42, 0.06), "fabric_teal", 0.05, grid=2)
    cush(m, (0.62, 0.55, 0.2), (0, 0.72, -0.28), "fabric_teal", 0.07, seam=None)
    m.box((0.85, 0.75, 0.16), (0, 0.55, -0.32), "fabric_teal", 0.05)
    for s in (-1, 1):
        cush(m, (0.15, 0.32, 0.8), (s * 0.35, 0.5, 0.0), "fabric_teal", 0.05, seam=None)
        m.box((0.16, 0.03, 0.4), (s * 0.35, 0.67, 0.14), "wood_light", 0.008)
    m.box((0.3, 0.3, 0.05), (0.0, 0.7, -0.15), "fabric_tan", 0.05, rot=(-0.2, 0, 0.6)) if False else None


@reg("chair", "lounge chair")
def _(m, rng):
    for s in (-1, 1):
        m.link((s * 0.3, 0.0, 0.3), (s * 0.28, 0.32, 0.15), 0.02, "wood_dark", 6)
        m.link((s * 0.3, 0.0, -0.35), (s * 0.28, 0.32, -0.2), 0.02, "wood_dark", 6)
        m.box((0.05, 0.05, 0.75), (s * 0.29, 0.34, -0.03), "wood_dark", 0.01)
        m.link((s * 0.29, 0.35, -0.3), (s * 0.29, 0.62, -0.42), 0.02, "wood_dark", 6)
    cush(m, (0.56, 0.1, 0.62), (0, 0.42, 0.05), "leather_brown", 0.04, grid=2)
    cush(m, (0.56, 0.62, 0.12), (0, 0.72, -0.34), "leather_brown", 0.05, seam=None, ) 
    m.box((0.56, 0.62, 0.1), (0, 0.72, -0.34), "leather_brown", 0.05, rot=(-0.28, 0, 0)) if False else None
    m.box((0.5, 0.2, 0.09), (0, 1.0, -0.45), "leather_black", 0.04, rot=(-0.3, 0, 0))


@reg("chair", "gaming chair")
def _(m, rng):
    star_base(m, 0.4, 0.33, 5, "black_metal")
    m.box((0.12, 0.08, 0.12), (0, 0.44, 0), "black_metal", 0.01)
    cush(m, (0.54, 0.12, 0.5), (0, 0.5, 0.02), "leather_black", 0.04, grid=None)
    for s in (-1, 1):
        m.box((0.09, 0.14, 0.5), (s * 0.29, 0.56, 0.02), "paint_red", 0.04)
        m.box((0.05, 0.03, 0.26), (s * 0.4, 0.75, 0.0), "plastic_black", 0.008)
        m.box((0.03, 0.25, 0.04), (s * 0.4, 0.62, -0.05), "black_metal")
        m.box((0.13, 0.7, 0.1), (s * 0.24, 0.92, -0.27), "paint_red", 0.04, rot=(-0.17, 0, s * 0.08))
    m.box((0.36, 0.7, 0.1), (0, 0.92, -0.27), "leather_black", 0.04, rot=(-0.17, 0, 0))
    m.box((0.05, 0.4, 0.012), (0, 0.9, -0.21), "paint_red", rot=(-0.17, 0, 0))
    cush(m, (0.36, 0.2, 0.12), (0, 1.36, -0.3), "leather_black", 0.05, seam=None) if False else None
    m.box((0.32, 0.2, 0.1), (0, 1.36, -0.32), "leather_black", 0.04, rot=(-0.17, 0, 0))
    m.box((0.3, 0.15, 0.1), (0, 0.6, -0.16), "leather_black", 0.04) if False else None
    m.box((0.06, 0.16, 0.02), (0, 1.36, -0.26), "em_red", rot=(-0.17, 0, 0))


@reg("chair", "ergonomic chair")
def _(m, rng):
    star_base(m, 0.4, 0.31, 5, "gunmetal")
    m.box((0.14, 0.05, 0.14), (0, 0.45, 0), "gunmetal", 0.01)
    m.box((0.5, 0.06, 0.5), (0, 0.5, 0.02), "plastic_grey", 0.025)
    cush(m, (0.46, 0.05, 0.44), (0, 0.55, 0.03), "fabric_grey", 0.02, seam=None)
    m.link((0, 0.5, -0.1), (0, 0.78, -0.32), 0.02, "gunmetal", 6)
    # mesh back: frame plus lumbar pad
    rails4(m, -0.24, 0.24, -0.4, -0.4, 0.0, 0.0, "plastic_black") if False else None
    m.box((0.05, 0.68, 0.05), (-0.24, 0.98, -0.35), "plastic_black", 0.01, rot=(-0.15, 0, 0))
    m.box((0.05, 0.68, 0.05), (0.24, 0.98, -0.35), "plastic_black", 0.01, rot=(-0.15, 0, 0))
    m.box((0.5, 0.04, 0.05), (0, 1.32, -0.4), "plastic_black", 0.01)
    m.box((0.48, 0.04, 0.05), (0, 0.66, -0.3), "plastic_black", 0.01)
    for k in range(5):
        m.box((0.42, 0.012, 0.012), (0, 0.72 + k * 0.12, -0.33 - k * 0.018), "plastic_grey")
    m.box((0.36, 0.16, 0.06), (0, 0.9, -0.3), "paint_teal", 0.03)
    m.box((0.3, 0.14, 0.07), (0, 1.5, -0.44), "fabric_grey", 0.03, rot=(-0.15, 0, 0))
    m.link((0, 1.32, -0.4), (0, 1.44, -0.43), 0.015, "gunmetal", 6)
    for s in (-1, 1):
        m.box((0.05, 0.22, 0.05), (s * 0.29, 0.62, -0.05), "plastic_black", 0.008)
        m.box((0.07, 0.03, 0.28), (s * 0.29, 0.74, 0.02), "plastic_black", 0.012)


make("chair", [(["swivel office chair", "mess chair", "stool", "folding chair", "armchair", "lounge chair",
                 "gaming chair", "ergonomic chair"], "floor", ["crew", "chair"], True, None)])


# ================================================================== TABLE
def table_legs_pedestal(m, h, r=0.06, base=0.35, mat="steel"):
    m.cyl(base, 0.03, (0, 0.015, 0), "black_metal", seg=18, bevel=0.005)
    m.cyl(r, h - 0.05, (0, h / 2, 0), mat, seg=12)


@reg("table", "long mess table")
def _(m, rng):
    W, D, H = 3.0, 0.8, 0.76
    m.box((W, 0.04, D), (0, H - 0.02, 0), "crew_tile", 0.012)
    m.box((W + 0.02, 0.05, D + 0.02), (0, H - 0.06, 0), "steel", 0.008) if False else None
    m.box((W - 0.06, 0.03, 0.04), (0, H - 0.055, D / 2 - 0.05), "steel")
    m.box((W - 0.06, 0.03, 0.04), (0, H - 0.055, -D / 2 + 0.05), "steel")
    m.box((W, 0.012, 0.03), (0, H + 0.005, D / 2 - 0.01), "paint_orange") if False else None
    for x in (-1.3, 1.3):
        m.box((0.06, H - 0.04, 0.06), (x, (H - 0.04) / 2, 0), "steel", 0.008)
        m.box((0.06, 0.05, D - 0.1), (x, H - 0.065, 0), "steel", 0.008)
        m.box((0.08, 0.04, D), (x, 0.02, 0), "black_metal", 0.008)
    m.box((W - 0.1, 0.03, 0.05), (0, 0.25, 0), "steel")
    for k in range(4):
        m.box((0.02, 0.02, 0.02), (-1.2 + 0.8 * k, H + 0.01, 0), "brass") if False else None
    for x in (-1.4, 1.4):
        for z in (-0.3, 0.3):
            m.cyl(0.012, 0.01, (x, H + 0.002, z), "chrome", seg=6)


@reg("table", "round mess table")
def _(m, rng):
    H = 0.75
    m.cyl(0.6, 0.04, (0, H - 0.02, 0), "wood_light", seg=24, bevel=0.01)
    m.torus(0.6, 0.014, (0, H, 0), "steel", seg=24, tseg=5)
    table_legs_pedestal(m, H - 0.04, 0.06, 0.4)
    m.cyl(0.14, 0.05, (0, H - 0.065, 0), "black_metal", seg=12, r2=0.09) if False else None
    m.cyl(0.11, 0.03, (0, H - 0.055, 0), "steel", seg=12)


@reg("table", "square mess table")
def _(m, rng):
    H = 0.76
    m.box((0.9, 0.04, 0.9), (0, H - 0.02, 0), "paint_teal", 0.012)
    m.box((0.94, 0.05, 0.94), (0, H - 0.005, 0), "steel", 0.008) if False else None
    rails4(m, -0.45, 0.45, -0.45, 0.45, H + 0.005, 0.02, "steel", 0.02, 0.004)
    for x in (-0.38, 0.38):
        for z in (-0.38, 0.38):
            m.box((0.05, H - 0.04, 0.05), (x, (H - 0.04) / 2, z), "steel", 0.006)
    m.box((0.76, 0.04, 0.03), (0, H - 0.06, 0.38), "steel")
    m.box((0.76, 0.04, 0.03), (0, H - 0.06, -0.38), "steel")
    m.box((0.03, 0.04, 0.76), (0.38, H - 0.06, 0), "steel")
    m.box((0.03, 0.04, 0.76), (-0.38, H - 0.06, 0), "steel")
    m.box((0.1, 0.012, 0.1), (0, H + 0.006, 0), "hazard_yellow") if False else None


@reg("table", "coffee table")
def _(m, rng):
    H = 0.42
    m.box((1.1, 0.04, 0.6), (0, H - 0.02, 0), "glass_blue", 0.01)
    m.box((1.12, 0.03, 0.62), (0, H - 0.05, 0), "chrome", 0.006) if False else None
    rails4(m, -0.55, 0.55, -0.3, 0.3, H - 0.045, 0.02, "chrome", 0.03, 0.004)
    for x in (-0.5, 0.5):
        for z in (-0.25, 0.25):
            m.link((x, H - 0.05, z), (x * 1.06, 0.0, z * 1.1), 0.018, "chrome", 8)
    m.box((1.0, 0.02, 0.5), (0, 0.12, 0), "wood_dark", 0.006)
    m.box((0.5, 0.02, 0.3), (0.0, 0.135, 0.0), "fabric_red", 0.005) if False else None


@reg("table", "conference table")
def _(m, rng):
    W, D, H = 3.0, 1.2, 0.76
    m.box((W, 0.05, D), (0, H - 0.025, 0), "wood_dark", 0.02)
    m.box((W - 0.1, 0.008, D - 0.1), (0, H + 0.004, 0), "leather_black", 0.002) if False else None
    m.box((W + 0.01, 0.02, D + 0.01), (0, H - 0.05, 0), "gold_trim", 0.004)
    for x in (-1.0, 1.0):
        m.box((0.7, 0.1, 0.08), (x, 0.05, 0), "black_metal", 0.01)
        m.box((0.2, H - 0.08, D * 0.6), (x, 0.08 + (H - 0.16) / 2, 0), "wood_dark", 0.012)
    m.box((W * 0.6, 0.02, 0.18), (0, H + 0.01, 0), "hull_dark", 0.005)
    for k in range(4):
        x = -0.9 + 0.6 * k
        m.cyl(0.03, 0.012, (x, H + 0.02, 0), "black_metal", seg=10)
        m.cyl(0.01, 0.005, (x, H + 0.027, 0), "em_green", seg=6)
    m.box((0.04, 0.04, 0.6), (0.0, H - 0.08, 0.0), "black_metal", 0.004) if False else None


@reg("table", "bar counter")
def _(m, rng):
    W, D, H = 1.8, 0.6, 1.05
    m.box((W, 0.06, D + 0.1), (0, H - 0.03, 0.03), "wood_dark", 0.015)
    m.box((W - 0.1, H - 0.1, D - 0.1), (0, (H - 0.1) / 2 + 0.06 - 0.02, -0.05), "hull_dark", 0.012)
    m.box((W, 0.08, D), (0, 0.04, -0.03), "black_metal", 0.008)
    for k in range(6):
        m.box((0.24, H - 0.3, 0.02), (-0.75 + 0.3 * k, 0.55, D / 2 - 0.045), "wood_light" if k % 2 else "wood_dark", 0.006)
    m.cyl(0.025, W - 0.1, (0, 0.2, D / 2 + 0.06), "brass", axis="x", seg=12)
    for x in (-0.85, 0.85):
        m.box((0.04, 0.2, 0.04), (x, 0.15, D / 2 + 0.06), "brass", 0.004)
    m.box((W - 0.1, 0.012, 0.03), (0, H + 0.006, D / 2 + 0.02), "em_amber")


@reg("table", "side table")
def _(m, rng):
    H = 0.55
    m.cyl(0.25, 0.03, (0, H - 0.015, 0), "wood_light", seg=20, bevel=0.006)
    for k in range(3):
        a = 2 * PI * k / 3 + 0.4
        m.link((0.15 * math.cos(a), H - 0.03, 0.15 * math.sin(a)), (0.28 * math.cos(a), 0.0, 0.28 * math.sin(a)), 0.016, "wood_dark", 6)
    m.torus(0.19, 0.008, (0, 0.2, 0), "brass", seg=16, tseg=4)
    m.cyl(0.24, 0.015, (0, 0.2, 0), "wood_dark", seg=16) if False else None


@reg("table", "bolted table")
def _(m, rng):
    W, D, H = 1.4, 0.8, 0.76
    m.box((W, 0.05, D), (0, H - 0.025, 0), "hull_mid", 0.015)
    rails4(m, -W / 2 + 0.01, W / 2 - 0.01, -D / 2 + 0.01, D / 2 - 0.01, H + 0.012, 0.03, "hazard_yellow", 0.03, 0.006)
    for x in (-1, 1):
        m.box((0.1, H - 0.05, 0.1), (x * 0.55, (H - 0.05) / 2, 0), "hull_dark", 0.01)
        m.box((0.4, 0.02, 0.4), (x * 0.55, 0.01, 0), "steel", 0.006)
        for a in (-1, 1):
            for b in (-1, 1):
                m.cyl(0.02, 0.015, (x * 0.55 + a * 0.15, 0.026, b * 0.15), "chrome", seg=6)
    m.box((W - 0.2, 0.05, 0.05), (0, H - 0.075, 0), "hull_dark", 0.008)
    m.box((0.14, 0.008, 0.1), (0.3, H + 0.004, 0.0), "hazard_yellow") if False else None


@reg("table", "fold-down table")
def _(m, rng):
    m.box((1.0, 0.16, 0.08), (0, 0.32, 0.04), "hull_dark", 0.01)
    m.box((0.9, 0.04, 0.55), (0, 0.0, 0.36), "hull_light", 0.012)
    m.box((0.84, 0.008, 0.49), (0, 0.024, 0.36), "crew_tile")
    for s in (-1, 1):
        m.link((s * 0.42, -0.02, 0.6), (s * 0.3, 0.3, 0.1), 0.012, "steel", 6)
        m.box((0.05, 0.04, 0.04), (s * 0.45, 0.0, 0.1), "black_metal", 0.006)
    led(m, (0, 0.32, 0.085), (0.2, 0.02, 0.01), "em_amber")
    m.box((0.6, 0.02, 0.02), (0, -0.03, 0.62), "steel")


@reg("table", "briefing table")
def _(m, rng):
    H = 0.85
    pts = [(0.9 * math.cos(k * PI / 4 + PI / 8), 0.9 * math.sin(k * PI / 4 + PI / 8)) for k in range(8)]
    m.prism(pts, 0.05, (0, H - 0.05, 0), "hull_dark", "xz", bevel=0.01)
    pts2 = [(0.82 * math.cos(k * PI / 4 + PI / 8), 0.82 * math.sin(k * PI / 4 + PI / 8)) for k in range(8)]
    m.prism(pts2, 0.012, (0, H, 0), "black_metal", "xz")
    m.cyl(0.55, 0.014, (0, H + 0.02, 0), "glass_blue", seg=20)
    m.torus(0.55, 0.012, (0, H + 0.02, 0), "em_cyan", seg=20, tseg=4)
    m.sphere(0.12, (0, H + 0.17, 0), "em_cyan", 10, 6)
    m.torus(0.2, 0.006, (0, H + 0.17, 0), "em_blue", seg=16, tseg=3, axis="x")
    m.torus(0.2, 0.006, (0, H + 0.17, 0), "em_blue", seg=16, tseg=3, axis="z")
    m.cyl(0.25, H - 0.1, (0, (H - 0.1) / 2 + 0.03, 0), "hull_mid", seg=12, r2=0.18)
    m.cyl(0.6, 0.03, (0, 0.015, 0), "black_metal", seg=20)
    for k in range(8):
        a = k * PI / 4 + PI / 8
        m.box((0.05, 0.02, 0.03), (0.72 * math.cos(a), H + 0.008, 0.72 * math.sin(a)), "em_cyan" if k % 2 else "em_amber", rot=(0, -a, 0))


make("table", [
    (["long mess table", "round mess table", "square mess table", "coffee table", "conference table",
      "bar counter", "side table", "bolted table", "briefing table"], "floor", ["crew", "table"], True, None),
    (["fold-down table"], "wall", ["crew", "table", "mess"], False, 0.9),
])


# ================================================================== BENCH
@reg("bench", "mess bench")
def _(m, rng):
    L = 2.0
    m.box((L, 0.04, 0.32), (0, 0.44, 0), "plastic_white", 0.012)
    m.box((L, 0.012, 0.03), (0, 0.46, 0.15), "paint_orange")
    for x in (-0.85, 0.85):
        m.box((0.05, 0.42, 0.05), (x, 0.21, 0), "steel", 0.006)
        m.box((0.05, 0.05, 0.4), (x, 0.025, 0), "steel", 0.006)
        m.box((0.05, 0.05, 0.28), (x, 0.4, 0), "steel", 0.006)
    m.box((L - 0.2, 0.04, 0.04), (0, 0.15, 0), "steel")
    for x in (-0.6, 0, 0.6):
        m.cyl(0.012, 0.01, (x, 0.462, 0), "chrome", seg=6)


@reg("bench", "locker room bench")
def _(m, rng):
    L = 1.6
    for k in range(4):
        m.box((L, 0.03, 0.08), (0, 0.45, -0.15 + 0.1 * k), "wood_light", 0.006)
    for x in (-0.65, 0.65):
        m.box((0.04, 0.45, 0.04), (x, 0.225, -0.13), "black_metal")
        m.box((0.04, 0.45, 0.04), (x, 0.225, 0.13), "black_metal")
        m.box((0.05, 0.03, 0.38), (x, 0.42, 0), "black_metal")
        m.box((0.05, 0.04, 0.5), (x, 0.02, 0), "black_metal")
    m.box((L - 0.1, 0.03, 0.03), (0, 0.15, 0), "black_metal")
    m.box((L - 0.1, 0.03, 0.4), (0, 0.18, 0), "wood_dark") if False else None
    for x in (-0.5, 0.0, 0.5):
        m.cyl(0.02, 0.05, (x, 0.41, 0.0), "black_metal", axis="x", seg=6) if False else None
    m.box((1.5, 0.03, 0.1), (0, 0.9, -0.3), "hull_dark") if False else None
    for x in (-0.5, 0.0, 0.5):
        m.cyl(0.015, 0.05, (x, 0.9, 0), "chrome", seg=6) if False else None


@reg("bench", "curved lounge bench")
def _(m, rng):
    R, n = 1.5, 9
    for k in range(n):
        a = (k - (n - 1) / 2) * 0.17
        px, pz = R * math.sin(a), R - R * math.cos(a)
        cs = R * 0.17 + 0.03
        m.box((cs, 0.14, 0.5), (px, 0.4, pz), "fabric_teal" if k % 2 else "fabric_navy", 0.025, rot=(0, -a, 0))
        m.box((cs, 0.05, 0.44), (px, 0.29, pz), "steel", 0, rot=(0, -a, 0))
        m.box((cs, 0.3, 0.09), (px + 0.22 * math.sin(a), 0.6, pz - 0.22 * math.cos(a)), "fabric_teal" if k % 2 else "fabric_navy", 0.03, rot=(0, -a, 0))
    for a in (-0.68, -0.34, 0.0, 0.34, 0.68):
        px, pz = R * math.sin(a), R - R * math.cos(a)
        m.cyl(0.04, 0.27, (px, 0.135, pz), "chrome", seg=8)
        m.cyl(0.11, 0.02, (px, 0.01, pz), "black_metal", seg=10)


@reg("bench", "padded wall bench")
def _(m, rng):
    m.box((1.8, 0.1, 0.06), (0, 0.42, 0.03), "hull_dark", 0.01)
    for k in range(3):
        cush(m, (0.58, 0.55, 0.1), (-0.6 + 0.6 * k, 0.0, 0.11), "leather_black", 0.04, seam=None)
        m.cyl(0.012, 0.012, (-0.6 + 0.6 * k, 0.0, 0.17), "chrome", axis="z", seg=6)
        cush(m, (0.58, 0.08, 0.4), (-0.6 + 0.6 * k, -0.42, 0.26), "leather_black", 0.03)
    m.box((1.8, 0.05, 0.42), (0, -0.48, 0.24), "hull_mid", 0.008)
    for x in (-0.85, 0.85):
        m.link((x, -0.5, 0.42), (x, -0.9, 0.05), 0.014, "steel", 6)
    m.box((1.8, 0.03, 0.03), (0, -0.05, 0.2), "steel") if False else None


@reg("bench", "gym bench")
def _(m, rng):
    cush(m, (0.3, 0.09, 1.2), (0, 0.44, 0), "leather_black", 0.035, seam="hazard_yellow")
    m.box((0.06, 0.05, 1.1), (0, 0.375, 0), "black_metal", 0.008)
    for z in (-0.45, 0.45):
        m.box((0.55, 0.05, 0.06), (0, 0.025, z), "black_metal", 0.008)
        m.box((0.06, 0.32, 0.06), (0, 0.19, z), "black_metal", 0.008)
        for s in (-1, 1):
            m.cyl(0.02, 0.05, (s * 0.26, 0.025, z), "rubber", seg=6)
    m.cyl(0.02, 0.06, (0.0, 0.32, 0.0), "chrome", axis="x", seg=6) if False else None
    m.box((0.06, 0.1, 0.3), (0.18, 0.28, -0.2), "hazard_yellow") if False else None


@reg("bench", "window seat")
def _(m, rng):
    W = 1.8
    m.box((W, 0.4, 0.5), (0, 0.2, 0), "wood_light", 0.012)
    for k in range(3):
        m.box((W / 3 - 0.03, 0.34, 0.02), (-W / 3 + W / 3 * k, 0.2, 0.26), "wood_dark", 0.006)
        handle(m, (-W / 3 + W / 3 * k, 0.32, 0.27), 0.1, "brass")
    cush(m, (W - 0.04, 0.09, 0.48), (0, 0.445, 0), "fabric_tan", 0.035, grid=4)
    for x in (-0.65, 0.5):
        cush(m, (0.4, 0.4, 0.14), (x, 0.66, -0.12), "fabric_teal", 0.06, seam=None, ) 
    m.box((0.3, 0.3, 0.1), (0.62, 0.61, 0.0), "crew_mustard", 0.05, rot=(0, 0.3, 0)) if False else None
    m.box((W, 0.05, 0.02), (0, 0.42, 0.25), "wood_dark") if False else None
    m.box((W + 0.04, 0.04, 0.54), (0, 0.42, 0), "wood_dark", 0.006) if False else None


make("bench", [
    (["mess bench", "locker room bench", "curved lounge bench", "gym bench", "window seat"], "floor", ["crew", "bench"], True, None),
    (["padded wall bench"], "wall", ["crew", "bench", "lounge"], True, 0.9),
])


# ================================================================== COUCH
def sofa(m, W, mat, n, arm=0.16, depth=0.9, hgt=0.85, leg="black_metal", accent=None):
    m.box((W, 0.22, depth), (0, 0.27, 0), mat, 0.04)
    legs(m, -W / 2 + 0.1, W / 2 - 0.1, -depth / 2 + 0.1, depth / 2 - 0.1, 0.16, 0.03, leg, 8)
    sw = (W - 2 * arm) / n
    for k in range(n):
        x = -W / 2 + arm + sw * (k + 0.5)
        cush(m, (sw - 0.02, 0.15, depth - 0.25), (x, 0.46, 0.1), mat, 0.05, grid=None)
        cush(m, (sw - 0.02, hgt - 0.5, 0.2), (x, 0.55 + (hgt - 0.5) / 2, -depth / 2 + 0.2), mat, 0.07, seam=None)
    m.box((W, hgt - 0.3, 0.14), (0, 0.38 + (hgt - 0.3) / 2, -depth / 2 + 0.05), mat, 0.04)
    for s in (-1, 1):
        m.box((arm, hgt - 0.35, depth), (s * (W / 2 - arm / 2), 0.38 + (hgt - 0.35) / 2 - 0.02, 0), mat, 0.05)


@reg("couch", "two-seater sofa")
def _(m, rng):
    sofa(m, 1.6, "fabric_navy", 2)
    pillow(m, (-0.4, 0.62, 0.05), 0.4, "crew_mustard", 0.22)
    m.box((0.4, 0.4, 0.12), (-0.4, 0.75, -0.1), "crew_mustard", 0.05, rot=(-0.3, 0, 0)) if False else None


@reg("couch", "three-seater sofa")
def _(m, rng):
    sofa(m, 2.3, "leather_brown", 3, 0.2, 0.95, 0.9, "wood_dark")
    m.cyl(0.02, 0.01, (0, 0.55, 0.49), "brass", axis="z", seg=6) if False else None
    for x in (-0.55, 0.0, 0.55):
        m.cyl(0.015, 0.01, (x, 0.82, -0.38), "brass", axis="z", seg=6)


@reg("couch", "corner couch segment")
def _(m, rng):
    mat = "fabric_grey"
    m.box((1.0, 0.22, 1.0), (0, 0.27, 0), mat, 0.04)
    cush(m, (0.96, 0.15, 0.96), (0, 0.46, 0), mat, 0.05, grid=2)
    m.box((1.0, 0.55, 0.16), (0, 0.66, -0.42), mat, 0.05)
    m.box((0.16, 0.55, 1.0), (-0.42, 0.66, 0), mat, 0.05)
    cush(m, (0.55, 0.4, 0.18), (0.15, 0.7, -0.3), mat, 0.07, seam=None)
    cush(m, (0.18, 0.4, 0.55), (-0.3, 0.7, 0.15), mat, 0.07, seam=None)
    legs(m, -0.4, 0.4, -0.4, 0.4, 0.13, 0.025, "chrome", 8)
    pillow(m, (0.2, 0.6, 0.15), 0.3, "paint_teal", 0.3)
    m.box((0.04, 0.5, 0.04), (-0.5, 0.36, -0.5), "chrome", 0.004) if False else None


@reg("couch", "lounge armchair")
def _(m, rng):
    # swoopy scoop chair on pedestal
    m.cyl(0.32, 0.04, (0, 0.02, 0), "black_metal", seg=16, bevel=0.006)
    m.cyl(0.07, 0.3, (0, 0.19, 0), "chrome", seg=10)
    m.sphere(0.5, (0, 0.6, 0.0), "paint_white", 18, 10, scale=(0.95, 0.5, 0.9))
    m.sphere(0.5, (0, 0.74, 0.0), "paint_white", 18, 10, scale=(0.95, 0.45, 0.9)) if False else None
    cush(m, (0.6, 0.1, 0.6), (0, 0.76, 0.05), "paint_red", 0.05, grid=2) if False else None
    m.sphere(0.4, (0, 0.72, 0.03), "fabric_red", 16, 8, scale=(1.0, 0.3, 1.0))
    m.box((0.8, 0.55, 0.14), (0, 1.0, -0.36), "paint_white", 0.06, rot=(-0.2, 0, 0))
    m.box((0.66, 0.42, 0.1), (0, 1.0, -0.3), "fabric_red", 0.06, rot=(-0.2, 0, 0))
    m.torus(0.5, 0.01, (0, 0.6, 0), "chrome", seg=20, tseg=4)


@reg("couch", "seating pod")
def _(m, rng):
    m.cyl(0.85, 0.12, (0, 0.06, 0), "hull_dark", seg=20, bevel=0.012)
    m.cyl(0.6, 0.3, (0, 0.27, 0), "hull_mid", seg=20)
    cush(m, (1.0, 0.16, 0.6), (0, 0.5, 0.1), "leather_black", 0.06) if False else None
    m.cyl(0.62, 0.14, (0, 0.5, 0), "leather_black", seg=20, bevel=0.03)
    m.torus(0.62, 0.012, (0, 0.575, 0), "crew_seam", seg=20, tseg=4)
    m.torus(0.7, 0.03, (0, 1.0, 0.0), "hull_light", axis="y", seg=20, tseg=6, arc=PI * 1.35, rot=(0, 3.14 + PI * 0.325 - 1.57 + 1.57 - PI * 1.35 / 2 + PI / 2 * 0, 0)) if False else None
    # tall wrap-around back shell (partial cylinder made of segments)
    n = 9
    for k in range(n):
        a = -PI * 0.7 + PI * 1.4 * k / (n - 1)
        px, pz = 0.7 * math.sin(a), -0.7 * math.cos(a)
        m.box((0.24, 1.1, 0.08), (px, 0.7, pz * 1.0), "hull_light" if k % 2 else "paint_white", 0.012, rot=(0, -(a + PI), 0)) if False else None
        m.box((0.31, 0.95 - 0.25 * abs(a) / 2.2, 0.09), (px, 0.6 + 0.07 - 0.12 * abs(a) / 2.2, pz), "paint_teal" if k % 2 else "hull_light", 0.01, rot=(0, -a, 0))
    m.torus(0.72, 0.03, (0, 1.16, 0), "chrome", seg=20, tseg=4, arc=PI * 1.6, rot=(0, -PI * 0.7 - PI / 2 * 0, 0)) if False else None
    m.cyl(0.04, 0.03, (0, 0.6, 0.35), "em_cyan", seg=8) if False else None
    m.box((0.3, 0.03, 0.03), (0, 0.55, 0.55), "em_cyan")


@reg("couch", "observation sofa")
def _(m, rng):
    R, n = 2.0, 11
    for k in range(n):
        a = (k - (n - 1) / 2) * 0.13
        px, pz = R * math.sin(a), R - R * math.cos(a)
        cs = R * 0.13 + 0.02
        mat = "fabric_teal" if k % 2 == 0 else "fabric_navy"
        m.box((cs, 0.22, 0.85), (px, 0.29, pz), "hull_dark", 0.01, rot=(0, -a, 0))
        m.box((cs, 0.15, 0.6), (px, 0.48, pz + 0.1 * math.cos(a)), mat, 0.04, rot=(0, -a, 0))
        m.box((cs, 0.5, 0.16), (px + 0.36 * math.sin(a), 0.75, pz - 0.36 * math.cos(a)), mat, 0.05, rot=(0, -a, 0))
    for a in (-0.7, 0.0, 0.7):
        m.cyl(0.03, 0.18, (R * math.sin(a), 0.09, R - R * math.cos(a)), "chrome", seg=8)


@reg("couch", "ottoman")
def _(m, rng):
    m.cyl(0.4, 0.34, (0, 0.24, 0), "fabric_red", seg=18, bevel=0.03)
    m.cyl(0.36, 0.04, (0, 0.43, 0), "fabric_red", seg=18, r2=0.34) if False else None
    for k in range(6):
        a = k * PI / 3
        m.sphere(0.015, (0.18 * math.cos(a), 0.42, 0.18 * math.sin(a)), "brass", 6, 4)
    m.sphere(0.015, (0, 0.42, 0), "brass", 6, 4)
    m.torus(0.38, 0.01, (0, 0.4, 0), "crew_seam", seg=18, tseg=4)
    m.torus(0.39, 0.01, (0, 0.11, 0), "crew_seam", seg=18, tseg=4)
    m.cyl(0.36, 0.06, (0, 0.03, 0), "wood_dark", seg=14, r2=0.3)


@reg("couch", "bean bag")
def _(m, rng):
    m.sphere(0.55, (0, 0.32, 0), "crew_plum", 16, 10, scale=(1.0, 0.62, 1.0))
    m.sphere(0.4, (0, 0.5, -0.24), "crew_plum", 14, 8, scale=(1.0, 1.0, 0.7))
    m.sphere(0.22, (0, 0.62, -0.32), "crew_plum", 10, 6, scale=(1.3, 0.8, 0.7)) if False else None
    m.torus(0.5, 0.012, (0, 0.14, 0), "crew_seam", seg=16, tseg=4)
    for k in range(6):
        a = k * PI / 3
        m.box((0.012, 0.3, 0.012), (0.36 * math.cos(a), 0.34, 0.36 * math.sin(a)), "crew_seam", rot=(0.0, 0, 0.0)) if False else None
    m.box((0.14, 0.03, 0.03), (0.2, 0.52, 0.42), "chrome") if False else None
    m.cyl(0.05, 0.02, (0.0, 0.615, 0.0), "chrome", seg=8) if False else None
    m.box((0.1, 0.04, 0.02), (0.28, 0.05, 0.46), "crew_seam") if False else None
    m.box((0.14, 0.05, 0.02), (0, 0.6, 0.0), "chrome") if False else None


@reg("couch", "chaise")
def _(m, rng):
    mat = "fabric_tan"
    m.box((0.75, 0.2, 1.75), (0, 0.27, 0.0), "wood_dark", 0.03)
    legs(m, -0.3, 0.3, -0.8, 0.8, 0.17, 0.025, "wood_dark", 8)
    cush(m, (0.72, 0.16, 1.7), (0, 0.45, 0.0), mat, 0.05, grid=None)
    cush(m, (0.72, 0.5, 0.16), (0, 0.78, -0.82), mat, 0.07, seam=None)
    m.box((0.75, 0.5, 0.2), (0, 0.6, -0.82), mat, 0.05, rot=(0.1, 0, 0)) if False else None
    m.box((0.14, 0.3, 0.9), (-0.42, 0.5, -0.4), mat, 0.05)
    cush(m, (0.55, 0.14, 0.3), (0, 0.6, -0.55), "crew_mustard", 0.05, seam=None) if False else None
    m.box((0.5, 0.22, 0.14), (0, 0.66, -0.58), "crew_mustard", 0.05, rot=(-0.3, 0, 0))
    m.torus(0.0001, 0.0001, (0, 0, 0), "steel") if False else None


@reg("couch", "bar stool")
def _(m, rng):
    m.cyl(0.24, 0.03, (0, 0.015, 0), "chrome", seg=18, bevel=0.005)
    m.cyl(0.035, 0.6, (0, 0.33, 0), "chrome", seg=10)
    m.torus(0.18, 0.012, (0, 0.28, 0), "chrome", seg=16, tseg=5)
    for k in range(3):
        a = k * 2 * PI / 3
        m.link((0.035 * math.cos(a), 0.28, 0.035 * math.sin(a)), (0.18 * math.cos(a), 0.28, 0.18 * math.sin(a)), 0.008, "chrome", 5)
    m.cyl(0.19, 0.08, (0, 0.68, 0), "leather_black", seg=18, bevel=0.02)
    m.cyl(0.14, 0.03, (0, 0.62, 0), "black_metal", seg=12)
    m.torus(0.185, 0.008, (0, 0.72, 0), "crew_seam", seg=18, tseg=4)
    m.box((0.28, 0.12, 0.05), (0, 0.9, -0.2), "leather_black", 0.02)
    for s in (-1, 1):
        m.link((s * 0.12, 0.68, -0.14), (s * 0.12, 0.85, -0.2), 0.012, "chrome", 6)


make("couch", [(["two-seater sofa", "three-seater sofa", "corner couch segment", "lounge armchair", "seating pod",
                 "observation sofa", "ottoman", "bean bag", "chaise", "bar stool"], "floor", ["crew", "couch", "lounge"], True, None)])


# ================================================================== GALLEY
def knobs(m, x0, y, z, n, dx, r=0.02, mat="black_metal"):
    for k in range(n):
        m.cyl(r, 0.03, (x0 + k * dx, y, z + 0.015), mat, axis="z", seg=8)
        m.box((0.004, r * 1.2, 0.006), (x0 + k * dx, y + r * 0.5, z + 0.032), "chrome")


def burner(m, x, y, z, r=0.09, hot=False):
    m.cyl(r, 0.012, (x, y + 0.006, z), "black_metal", seg=14)
    m.torus(r * 0.55, 0.008, (x, y + 0.016, z), "em_orange" if hot else "gunmetal", seg=12, tseg=4)
    for a in (0, 1.57):
        m.box((r * 2.1, 0.012, 0.012), (x, y + 0.02, z), "black_metal", rot=(0, a + 0.4, 0))


def pot(m, x, y, z, r=0.11, h=0.14, mat="steel", lid=True):
    m.cyl(r, h, (x, y + h / 2, z), mat, seg=14, r2=r * 1.02)
    m.box((r * 2.6, 0.014, 0.03), (x, y + h * 0.85, z), "black_metal") if False else None
    for s in (-1, 1):
        m.box((0.05, 0.015, 0.03), (x + s * (r + 0.02), y + h * 0.85, z), "black_metal")
    if lid:
        m.cyl(r * 1.03, 0.015, (x, y + h + 0.007, z), "brushed_alu", seg=14)
        m.sphere(0.02, (x, y + h + 0.03, z), "black_metal", 6, 4)


def door_window(m, x, y, z, w, h, mat="glass_dark"):
    m.box((w, h, 0.01), (x, y, z), mat)


@reg("galley", "commercial oven")
def _(m, rng):
    m.box((0.95, 0.15, 0.8), (0, 0.075, 0), "black_metal", 0.01)
    m.box((0.9, 1.5, 0.78), (0, 0.9, 0), "steel", 0.02)
    for y in (0.6, 1.2):
        m.box((0.78, 0.5, 0.04), (-0.03, y, 0.4), "brushed_alu", 0.015)
        door_window(m, -0.03, y, 0.425, 0.6, 0.32)
        m.cyl(0.015, 0.7, (-0.03, y + 0.2, 0.46), "chrome", axis="x", seg=8)
        m.box((0.04, 0.04, 0.05), (-0.36, y + 0.2, 0.44), "chrome") if False else None
    m.box((0.12, 1.2, 0.03), (0.38, 0.9, 0.41), "black_metal", 0.005)
    for k in range(5):
        m.box((0.07, 0.03, 0.01), (0.38, 0.5 + 0.2 * k, 0.43), ["em_green", "em_amber", "em_green", "em_red", "em_cyan"][k])
    knobs(m, 0.38, 0.65, 0.41, 1, 0, 0.025)
    m.box((0.85, 0.06, 0.6), (0, 1.68, 0), "hull_dark", 0.01)
    m.cyl(0.08, 0.2, (0.25, 1.82, -0.15), "steel", seg=10)
    m.box((0.84, 0.12, 0.02), (0, 1.55, 0.395), "hull_dark")


@reg("galley", "range with hood")
def _(m, rng):
    m.box((0.9, 0.9, 0.75), (0, 0.45, 0), "steel", 0.015)
    m.box((0.9, 0.04, 0.75), (0, 0.92, 0), "black_metal", 0.01)
    for x in (-0.22, 0.22):
        for z in (-0.17, 0.17):
            burner(m, x, 0.94, z, 0.09, (x > 0) == (z > 0))
    m.box((0.76, 0.5, 0.03), (0, 0.4, 0.38), "brushed_alu", 0.01)
    door_window(m, 0, 0.4, 0.4, 0.55, 0.3)
    m.cyl(0.015, 0.7, (0, 0.68, 0.43), "chrome", axis="x", seg=8)
    knobs(m, -0.3, 0.78, 0.375, 4, 0.2, 0.025)
    pot(m, 0.22, 0.95, 0.17, 0.11, 0.14)
    m.cyl(0.09, 0.1, (-0.22, 0.99, -0.17), "black_metal", seg=12, r2=0.11) if False else None
    # hood
    m.box((0.9, 0.06, 0.7), (0, 1.75, -0.03), "brushed_alu", 0.01)
    m.prism([(-0.45, 0.35), (0.45, 0.35), (0.16, -0.05), (-0.16, -0.05)], 0.05, (0, 1.79, -0.05), "brushed_alu", "xz") if False else None
    m.box((0.36, 0.7, 0.36), (0, 2.15, -0.2), "brushed_alu", 0.01)
    m.box((0.86, 0.14, 0.02), (0, 1.86, 0.32), "brushed_alu", 0.005) if False else None
    m.box((0.9, 0.2, 0.5), (0, 1.9, -0.1), "brushed_alu", 0.012)
    led(m, (0, 1.79, 0.2), (0.6, 0.012, 0.1), "em_warm")
    m.box((0.6, 0.12, 0.02), (0, 0.06, 0.38), "black_metal")


@reg("galley", "refrigerator")
def _(m, rng):
    m.box((0.8, 1.9, 0.75), (0, 0.95, 0), "brushed_alu", 0.025)
    m.box((0.78, 0.6, 0.03), (0, 1.55, 0.39), "steel", 0.01)
    m.box((0.78, 1.2, 0.03), (0, 0.65, 0.39), "steel", 0.01)
    m.box((0.78, 0.015, 0.01), (0, 0.94, 0.4), "black_metal")
    m.box((0.04, 0.4, 0.05), (-0.3, 1.55, 0.44), "chrome", 0.01)
    m.box((0.04, 0.8, 0.05), (-0.3, 0.7, 0.44), "chrome", 0.01)
    m.box((0.2, 0.12, 0.01), (0.15, 1.6, 0.41), "black_metal")
    m.box((0.14, 0.05, 0.005), (0.15, 1.6, 0.416), "em_cyan")
    m.box((0.78, 0.06, 0.6), (0, 0.03, 0.02), "black_metal", 0.005)
    m.box((0.78, 0.1, 0.74), (0, 1.93, 0), "hull_dark", 0.01) if False else None
    for x in (-0.3, 0.3):
        m.cyl(0.02, 0.02, (x, 0.02, 0.32), "rubber", seg=6) if False else None


@reg("galley", "chest freezer")
def _(m, rng):
    m.box((1.5, 0.75, 0.75), (0, 0.45, 0), "plastic_white", 0.03)
    m.box((1.5, 0.07, 0.75), (0, 0.04, 0), "black_metal", 0.01)
    m.box((1.52, 0.06, 0.77), (0, 0.85, 0), "steel", 0.01)
    for s in (-1, 1):
        m.box((0.72, 0.03, 0.66), (s * 0.37, 0.885, 0), "glass_blue", 0.006)
        m.box((0.03, 0.05, 0.05), (s * 0.06, 0.9, 0.3), "chrome") if False else None
    m.box((0.05, 0.04, 0.68), (0, 0.9, 0), "steel", 0.005)
    m.box((0.2, 0.08, 0.02), (0.4, 0.55, 0.385), "black_metal")
    m.box((0.08, 0.04, 0.008), (0.4, 0.56, 0.397), "em_cyan")
    m.box((0.1, 0.03, 0.03), (0, 0.6, 0.39), "chrome", 0.005) if False else None
    for x in (-0.65, 0.65):
        m.cyl(0.04, 0.05, (x, 0.025, 0.3), "rubber", seg=8) if False else None
    m.box((0.5, 0.012, 0.005), (-0.4, 0.55, 0.377), "hazard_yellow")


@reg("galley", "food replicator")
def _(m, rng):
    m.box((0.9, 1.9, 0.5), (0, 0.95, 0), "hull_dark", 0.025)
    m.box((0.86, 0.5, 0.06), (0, 1.55, 0.27), "hull_light", 0.02)
    m.screen((0.6, 0.34), (0, 1.55, 0.31), "text", bezel=0.02)
    m.box((0.7, 0.55, 0.3), (0, 0.95, 0.15), "black_metal", 0.02)           # recess
    m.box((0.6, 0.4, 0.28), (0, 0.98, 0.16), "em_cyan") if False else None
    m.box((0.62, 0.42, 0.02), (0, 0.98, 0.31), "glass_blue")
    m.box((0.66, 0.05, 0.04), (0, 0.66, 0.32), "hull_light", 0.006)
    m.box((0.64, 0.03, 0.3), (0, 0.72, 0.28), "steel", 0.006)
    m.box((0.5, 0.03, 0.018), (0, 0.66, 0.35), "em_cyan")
    for k in range(6):
        m.box((0.09, 0.05, 0.02), (-0.33 + 0.132 * k, 1.28, 0.27), ["em_green", "em_amber", "em_cyan", "em_violet", "em_orange", "em_blue"][k])
    m.box((0.9, 0.04, 0.5), (0, 1.92, 0), "hull_light", 0.01)
    m.box((0.8, 0.02, 0.02), (0, 0.15, 0.27), "hazard_yellow")
    m.box((0.5, 0.2, 0.02), (0, 0.4, 0.26), "hull_mid", 0.005)
    m.cyl(0.1, 0.02, (0.0, 0.3, 0.27), "steel", axis="z", seg=10)


@reg("galley", "coffee machine")
def _(m, rng):
    m.box((0.9, 0.85, 0.6), (0, 0.425, 0), "hull_dark", 0.02)
    m.box((0.86, 0.6, 0.02), (0, 0.4, 0.31), "hull_mid", 0.006)
    handle(m, (0.3, 0.4, 0.32), 0.3, "chrome", False)
    m.box((0.82, 0.62, 0.55), (0, 1.2, -0.02), "brushed_alu", 0.03)
    m.box((0.82, 0.14, 0.57), (0, 1.46, -0.02), "chrome", 0.02) if False else None
    for s in (-1, 1):
        m.cyl(0.1, 0.16, (s * 0.25, 1.32, 0.2), "black_metal", seg=12, r2=0.1) if False else None
        m.box((0.16, 0.06, 0.1), (s * 0.25, 1.0, 0.25), "black_metal", 0.008)
        m.cyl(0.02, 0.06, (s * 0.25, 0.96, 0.27), "chrome", seg=8)
        m.cyl(0.05, 0.08, (s * 0.25, 0.84, 0.28), "ceramic", seg=10, r2=0.04)
        m.link((s * 0.25 + 0.05, 0.86, 0.28), (s * 0.25 + 0.05, 0.82, 0.28), 0.008, "ceramic", 4) if False else None
    m.screen((0.24, 0.16), (0, 1.25, 0.26), "vitals", bezel=0.01)
    knobs(m, -0.1, 1.05, 0.26, 3, 0.1, 0.025, "chrome")
    m.cyl(0.14, 0.2, (-0.28, 1.6, -0.05), "glass_amber", seg=12)
    m.cyl(0.15, 0.03, (-0.28, 1.5, -0.05), "black_metal", seg=12)
    m.cyl(0.15, 0.03, (-0.28, 1.71, -0.05), "black_metal", seg=12)
    m.box((0.06, 0.1, 0.06), (0.3, 1.55, -0.1), "paint_red", 0.01)
    m.box((0.5, 0.03, 0.3), (0, 0.9, 0.3), "steel") if False else None


@reg("galley", "sink unit")
def _(m, rng):
    W = 1.4
    m.box((W, 0.85, 0.65), (0, 0.425, 0), "steel", 0.015)
    m.box((W + 0.02, 0.05, 0.67), (0, 0.875, 0), "brushed_alu", 0.01)
    for s in (-1, 1):
        m.box((0.5, 0.025, 0.42), (s * 0.3, 0.9, 0.03), "black_metal") if False else None
        m.box((0.46, 0.018, 0.4), (s * 0.3 + (0.05 if s < 0 else 0), 0.905, 0.03), "hull_dark")
    m.box((0.4, 0.012, 0.6), (0.5, 0.906, 0), "black_metal", 0) if False else None
    for k in range(6):
        m.box((0.3, 0.006, 0.012), (0.5, 0.91, -0.22 + 0.09 * k), "steel")
    m.box((W + 0.02, 0.14, 0.03), (0, 1.0, -0.32), "brushed_alu", 0.008)
    m.cyl(0.03, 0.3, (-0.2, 1.05, -0.2), "chrome", seg=10)
    m.link((-0.2, 1.2, -0.2), (-0.2, 1.3, -0.05), 0.02, "chrome", 8)
    m.link((-0.2, 1.3, -0.05), (-0.2, 1.3, 0.05), 0.02, "chrome", 8) if False else None
    m.sphere(0.03, (-0.2, 1.2, -0.2), "chrome", 8, 5)
    m.cyl(0.02, 0.1, (-0.2, 1.28, 0.03), "chrome", seg=8, r2=0.015)
    for s in (-1, 1):
        m.cyl(0.02, 0.05, (-0.2 + s * 0.09, 0.95, -0.25), "paint_red" if s < 0 else "paint_blue", seg=8)
    for k in range(2):
        m.box((0.3 + 0.2 * k, 0.6, 0.02), (-0.35 + 0.7 * k, 0.4, 0.33), "hull_light", 0.008) if k == 0 else None
    m.box((0.6, 0.6, 0.02), (-0.35, 0.42, 0.335), "hull_light", 0.008)
    m.box((0.6, 0.6, 0.02), (0.3, 0.42, 0.335), "hull_light", 0.008)
    handle(m, (-0.35, 0.72, 0.35), 0.25)
    handle(m, (0.3, 0.72, 0.35), 0.25)
    m.box((W, 0.06, 0.66), (0, 0.03, 0), "black_metal") if False else None


@reg("galley", "dishwasher")
def _(m, rng):
    m.box((0.9, 0.9, 0.75), (0, 0.45, 0), "steel", 0.02)
    m.box((0.86, 0.68, 0.06), (0, 0.5, 0.39), "brushed_alu", 0.02)
    m.box((0.84, 0.14, 0.06), (0, 0.86, 0.39), "black_metal", 0.015)
    m.screen((0.24, 0.06), (0.25, 0.86, 0.425), "diagnostic", bezel=0.008)
    for k in range(3):
        m.cyl(0.018, 0.02, (-0.35 + 0.08 * k, 0.86, 0.43), "chrome", axis="z", seg=8)
    m.box((0.6, 0.03, 0.05), (0, 0.72, 0.44), "chrome", 0.01)
    m.box((0.5, 0.3, 0.012), (0, 0.4, 0.425), "glass_dark") if False else None
    m.box((0.62, 0.36, 0.01), (0, 0.42, 0.421), "glass_blue")
    m.box((0.86, 0.12, 0.02), (0, 0.06, 0.38), "black_metal")
    m.box((0.06, 0.08, 0.02), (-0.3, 0.86, 0.43), "em_cyan") if False else None
    m.box((0.02, 0.2, 0.02), (0.4, 0.5, 0.43), "hazard_yellow") if False else None
    m.box((0.1, 0.3, 0.005), (0.32, 0.4, 0.42), "plastic_white") if False else None


@reg("galley", "prep counter")
def _(m, rng):
    W, D = 1.8, 0.75
    m.box((W, 0.05, D), (0, 0.9, 0), "brushed_alu", 0.012)
    m.box((W, 0.2, 0.04), (0, 1.02, -D / 2 + 0.02), "brushed_alu", 0.008)
    for x in (-1, 1):
        for z in (-1, 1):
            m.box((0.05, 0.88, 0.05), (x * (W / 2 - 0.05), 0.44, z * (D / 2 - 0.05)), "steel", 0.006)
    m.box((W - 0.06, 0.03, D - 0.1), (0, 0.22, 0), "steel", 0.006)
    m.box((W - 0.06, 0.05, 0.03), (0, 0.85, D / 2 - 0.06), "steel")
    m.box((0.5, 0.03, 0.35), (-0.5, 0.945, 0.05), "wood_light", 0.01)
    m.box((0.3, 0.008, 0.02), (-0.5, 0.965, 0.05), "steel") if False else None
    m.box((0.32, 0.02, 0.06), (-0.5, 0.97, -0.05), "steel", 0.004) if False else None
    m.box((0.5, 0.14, 0.05), (0.5, 1.03, -0.05), "wood_dark", 0.01) if False else None
    for k in range(4):
        m.box((0.03, 0.14 + 0.02 * (k % 2), 0.03), (0.35 + 0.08 * k, 1.1, -D / 2 + 0.06), "black_metal", 0.004)
    m.box((0.4, 0.03, 0.05), (0.5, 1.03, -D / 2 + 0.05), "steel", 0.005)
    for k in range(3):
        m.box((0.28, 0.1, 0.28), (0.5, 0.29 + 0.0, 0.0), "cardboard", 0.01) if k == 0 else None
    m.box((0.3, 0.12, 0.3), (-0.55, 0.3, 0.0), "paint_blue", 0.012)
    pot(m, 0.45, 0.925, 0.12, 0.13, 0.16, "steel", False)
    m.box((0.35, 0.06, 0.25), (-0.5, 0.96, 0.05), "food_green", 0.03) if False else None


@reg("galley", "cutlery drawer")
def _(m, rng):
    m.box((1.0, 0.9, 0.65), (0, 0.45, 0), "hull_light", 0.02)
    m.box((1.04, 0.04, 0.68), (0, 0.92, 0), "wood_light", 0.01)
    for k, y in enumerate((0.76, 0.56, 0.36, 0.16)):
        z = 0.34 + (0.28 if k == 0 else 0)
        m.box((0.92, 0.16, 0.03), (0, y, z), "steel", 0.008)
        handle(m, (0, y + 0.02, z + 0.015), 0.4, "chrome")
    # open top drawer with cutlery tray
    m.box((0.9, 0.1, 0.5), (0, 0.72, 0.55), "steel", 0.006) if False else None
    m.box((0.88, 0.02, 0.5), (0, 0.7, 0.55), "steel")
    for k in range(4):
        m.box((0.2, 0.05, 0.42), (-0.33 + 0.22 * k, 0.72, 0.55), "plastic_grey", 0.004)
        for j in range(3):
            m.box((0.012, 0.012, 0.3), (-0.4 + 0.22 * k + 0.05 * j, 0.755, 0.55), "chrome")
    m.box((0.88, 0.06, 0.02), (0, 0.72, 0.8), "steel")
    m.box((0.88, 0.06, 0.02), (0, 0.72, 0.31), "steel")


@reg("galley", "kitchen island")
def _(m, rng):
    m.box((2.0, 0.88, 0.95), (0, 0.44, 0), "hull_dark", 0.025)
    m.box((2.06, 0.05, 1.0), (0, 0.9, 0), "wood_light", 0.015)
    m.box((0.9, 0.012, 0.65), (-0.4, 0.93, 0), "black_metal", 0.004)
    for x in (-0.6, -0.2):
        for z in (-0.15, 0.15):
            burner(m, x, 0.925, z, 0.08, x > -0.4 and z > 0)
    knobs(m, -0.7, 0.75, 0.475, 4, 0.11, 0.022, "chrome")
    for k in range(3):
        m.box((0.5, 0.2, 0.02), (0.55, 0.7 - 0.24 * k, 0.48), "hull_mid", 0.006) if False else None
    for k in range(2):
        m.box((0.4, 0.5, 0.02), (0.35 + 0.42 * k, 0.4, 0.48), "hull_mid", 0.006)
        handle(m, (0.35 + 0.42 * k, 0.6, 0.495), 0.16, "brass", False)
    pot(m, -0.6, 0.93, 0.12, 0.13, 0.14)
    m.box((0.3, 0.03, 0.2), (0.55, 0.95, 0.1), "wood_dark", 0.01)
    m.box((0.06, 0.1, 0.06), (0.9, 0.98, -0.3), "steel", 0.008) if False else None
    m.sphere(0.06, (0.4, 0.995, -0.2), "food_green", 8, 6)
    m.sphere(0.06, (0.53, 0.995, -0.25), "food_red", 8, 6)
    m.cyl(0.14, 0.03, (0.45, 0.945, -0.22), "ceramic", seg=12, r2=0.11)
    m.cyl(0.02, 0.5, (0.0, 1.78, 0), "black_metal", axis="y", seg=6) if False else None
    m.box((1.9, 0.03, 0.03), (0, 0.06, 0.49), "black_metal")


@reg("galley", "water cooler")
def _(m, rng):
    m.box((0.36, 0.95, 0.38), (0, 0.475, 0), "plastic_white", 0.03)
    m.box((0.32, 0.02, 0.05), (0, 0.5, 0.2), "black_metal", 0.004) if False else None
    m.box((0.28, 0.16, 0.1), (0, 0.85, 0.16), "hull_dark", 0.02) if False else None
    m.box((0.3, 0.14, 0.04), (0, 0.72, 0.2), "hull_dark", 0.01)
    for s, c in ((-1, "em_blue"), (1, "em_red")):
        m.cyl(0.02, 0.05, (s * 0.07, 0.72, 0.24), "chrome", axis="z", seg=8)
        m.box((0.04, 0.02, 0.012), (s * 0.07, 0.785, 0.22), c)
    m.box((0.2, 0.03, 0.14), (0, 0.55, 0.25), "steel") if False else None
    m.box((0.28, 0.02, 0.16), (0, 0.5, 0.24), "black_metal", 0.004)
    m.cyl(0.14, 0.4, (0, 1.2, 0), "glass_blue", seg=16, r2=0.14)
    m.cyl(0.14, 0.3, (0, 1.15, 0), "water", seg=16) if False else None
    m.cyl(0.13, 0.28, (0, 1.1, 0), "water", seg=16)
    m.cyl(0.05, 0.05, (0, 1.42, 0), "glass_blue", seg=10, r2=0.03)
    m.cyl(0.04, 0.04, (0, 1.46, 0), "plastic_white", seg=8) if False else None
    m.box((0.36, 0.03, 0.38), (0, 0.97, 0), "plastic_white", 0.008)
    m.box((0.36, 0.05, 0.38), (0, 0.025, 0), "black_metal", 0.008)
    for x in (-0.13, 0.13):
        m.cyl(0.015, 0.03, (x, 0.015, 0.16), "rubber", seg=6) if False else None


@reg("galley", "soup kettle")
def _(m, rng):
    m.box((0.8, 0.7, 0.8), (0, 0.35, 0), "steel", 0.02)
    m.box((0.76, 0.5, 0.02), (0, 0.4, 0.41), "hull_dark", 0.006)
    knobs(m, -0.2, 0.5, 0.41, 3, 0.2, 0.03, "black_metal")
    led(m, (0.28, 0.5, 0.435), (0.05, 0.05, 0.01), "em_orange")
    m.cyl(0.36, 0.45, (0, 0.925, 0), "brushed_alu", seg=22)
    m.cyl(0.38, 0.03, (0, 1.16, 0), "chrome", seg=22)
    m.cyl(0.37, 0.05, (0, 1.2, 0), "brushed_alu", seg=22, r2=0.35) if False else None
    m.cyl(0.35, 0.04, (0, 1.23, 0), "chrome", seg=22, r2=0.32)
    m.sphere(0.04, (0, 1.28, 0), "black_metal", 8, 6)
    for s in (-1, 1):
        m.box((0.1, 0.04, 0.04), (s * 0.4, 1.02, 0), "black_metal", 0.008)
        m.box((0.04, 0.06, 0.06), (s * 0.44, 1.02, 0), "black_metal", 0.008) if False else None
    m.cyl(0.03, 0.14, (0, 0.84, 0.38), "chrome", axis="z", seg=8)
    m.cyl(0.02, 0.1, (0, 0.78, 0.46), "chrome", seg=8)
    m.box((0.08, 0.04, 0.03), (0, 0.85, 0.46), "black_metal", 0.005) if False else None
    m.torus(0.35, 0.01, (0, 0.72, 0), "chrome", seg=18, tseg=4) if False else None
    legs(m, -0.35, 0.35, -0.35, 0.35, 0.05, 0.04, "black_metal", 6, 0.0) if False else None


@reg("galley", "steamer")
def _(m, rng):
    m.box((0.85, 1.7, 0.85), (0, 0.85, 0), "brushed_alu", 0.025)
    m.box((0.85, 0.14, 0.85), (0, 0.07, 0), "black_metal", 0.01)
    for y in (0.45, 1.15):
        m.box((0.72, 0.56, 0.04), (0, y, 0.44), "steel", 0.015)
        door_window(m, 0, y + 0.04, 0.465, 0.48, 0.3, "glass_blue")
        m.cyl(0.02, 0.4, (0.32, y - 0.15, 0.5), "black_metal", axis="y", seg=6) if False else None
        m.box((0.03, 0.4, 0.04), (0.33, y, 0.48), "black_metal", 0.006)
    m.box((0.78, 0.24, 0.02), (0, 1.55, 0.43), "hull_dark", 0.006)
    m.cyl(0.07, 0.025, (-0.25, 1.55, 0.45), "chrome", axis="z", seg=14)
    m.cyl(0.06, 0.01, (-0.25, 1.55, 0.465), "plastic_white", axis="z", seg=14)
    m.box((0.004, 0.05, 0.004), (-0.25, 1.56, 0.472), "paint_red") if False else None
    knobs(m, 0.0, 1.55, 0.44, 2, 0.15, 0.025)
    led(m, (0.32, 1.55, 0.44), (0.05, 0.05, 0.01), "em_green")
    m.cyl(0.05, 0.25, (0.25, 1.83, -0.2), "steel", seg=10)
    m.cyl(0.07, 0.03, (0.25, 1.96, -0.2), "steel", seg=10) if False else None


@reg("galley", "salad bar")
def _(m, rng):
    W = 2.0
    m.box((W, 0.8, 0.8), (0, 0.4, 0), "hull_light", 0.02)
    m.box((W + 0.04, 0.05, 0.84), (0, 0.825, 0), "brushed_alu", 0.01)
    m.box((W - 0.1, 0.1, 0.7), (0, 0.9, 0), "crew_tile", 0.005)
    cols = ["food_green", "food_red", "crew_cheese", "food_brown", "food_green", "food_red"]
    for k in range(6):
        x = -0.8 + 0.32 * k
        m.box((0.3, 0.08, 0.28), (x, 0.94, 0.15), "steel", 0.01)
        m.box((0.26, 0.04, 0.24), (x, 0.965, 0.15), cols[k], 0.01)
        m.box((0.3, 0.08, 0.28), (x, 0.94, -0.17), "steel", 0.01)
        m.box((0.26, 0.04, 0.24), (x, 0.965, -0.17), cols[(k + 2) % 6], 0.01)
    for s in (-1, 1):
        m.box((0.03, 0.4, 0.03), (s * 0.98, 1.2, 0.36), "chrome", 0.004)
    m.box((W - 0.05, 0.4, 0.02), (0, 1.22, 0.4), "glass", 0.0)
    m.box((W - 0.05, 0.02, 0.35), (0, 1.42, 0.22), "glass") if False else None
    m.prism([(0.4, 0.0), (0.4, 0.0), (0.2, 0.4), (0.4, 0.4)], 0.01, (0, 0, 0), "glass") if False else None
    m.box((W, 0.025, 0.06), (0, 1.42, 0.38), "chrome", 0.004) if False else None
    m.box((W - 0.05, 0.02, 0.32), (0, 1.42, 0.24), "glass_blue")
    led(m, (0, 1.4, 0.4), (W - 0.2, 0.012, 0.012), "em_white")
    m.box((W - 0.2, 0.03, 0.03), (0, 0.4, 0.42), "steel") if False else None
    m.box((0.6, 0.2, 0.02), (0, 0.45, 0.41), "paint_green", 0.005)


@reg("galley", "storage shelving")
def _(m, rng):
    W, D, H = 1.2, 0.5, 1.9
    for x in (-1, 1):
        for z in (-1, 1):
            m.box((0.04, H, 0.04), (x * W / 2, H / 2, z * D / 2), "steel", 0.005)
    for k in range(5):
        y = 0.15 + 0.4 * k
        m.box((W + 0.04, 0.03, D + 0.04), (0, y, 0), "brushed_alu", 0.005)
        for j in range(4):
            m.box((0.02, 0.01, D), (-0.45 + 0.3 * j, y + 0.02, 0), "steel") if False else None
    rr = [(0.2, "cardboard", 0.4, 0.3), (0.5, "paint_blue", 0.25, 0.3), (0.35, "crew_mustard", 0.3, 0.25)]
    for k in range(4):
        y = 0.165 + 0.4 * k
        m.box((0.4, 0.25, 0.36), (-0.35, y + 0.125, 0.0), "cardboard", 0.01)
        m.box((0.3, 0.28, 0.35), (0.05, y + 0.14, 0.0), ["paint_blue", "food_red", "paint_white", "paint_green"][k], 0.01)
        for j in range(3):
            m.cyl(0.05, 0.16, (0.38 + 0.11 * j, y + 0.08, 0.0), ["steel", "food_red", "crew_cheese"][(j + k) % 3], seg=10)
    m.box((W, 0.03, 0.02), (0, 0.4, 0.26), "hazard_yellow") if False else None
    m.box((0.6, 0.06, 0.005), (0, 0.06, 0.26), "hazard_yellow") if False else None


@reg("galley", "microwave")
def _(m, rng):
    m.box((0.5, 0.3, 0.38), (0, 0.15, 0), "plastic_white", 0.02)
    m.box((0.34, 0.24, 0.02), (-0.05, 0.16, 0.195), "glass_dark", 0.005)
    m.box((0.38, 0.28, 0.01), (-0.05, 0.16, 0.19), "steel", 0.004)
    m.box((0.11, 0.26, 0.02), (0.19, 0.16, 0.195), "hull_dark", 0.006)
    m.box((0.08, 0.04, 0.008), (0.19, 0.24, 0.207), "em_green")
    for k in range(3):
        m.box((0.03, 0.02, 0.008), (0.16 + 0.03 * k, 0.16, 0.207), "plastic_grey")
        m.box((0.03, 0.02, 0.008), (0.16 + 0.03 * k, 0.12, 0.207), "plastic_grey")
    m.box((0.02, 0.2, 0.02), (0.14, 0.16, 0.21), "chrome", 0.004)
    for x in (-0.2, 0.2):
        m.cyl(0.02, 0.01, (x, 0.005, 0.15), "rubber", seg=6) if False else None


@reg("galley", "toaster")
def _(m, rng):
    m.box((0.32, 0.18, 0.2), (0, 0.11, 0), "chrome", 0.03)
    m.box((0.34, 0.03, 0.22), (0, 0.02, 0), "black_metal", 0.008)
    for x in (-0.07, 0.07):
        m.box((0.02, 0.01, 0.15), (x * 1.0, 0.205, 0), "black_metal")
    m.box((0.02, 0.04, 0.09), (0.05, 0.14, 0.11), "black_metal", 0.004) if False else None
    m.box((0.05, 0.03, 0.03), (0.18, 0.14, 0.0), "black_metal", 0.006)
    m.cyl(0.02, 0.02, (0, 0.12, 0.11), "black_metal", axis="z", seg=8)
    m.cyl(0.015, 0.02, (0.1, 0.12, 0.11), "paint_red", axis="z", seg=8)
    m.box((0.06, 0.08, 0.02), (-0.09, 0.11, 0.11), "black_metal") if False else None
    m.box((0.06, 0.03, 0.03), (-0.18, 0.15, 0.0), "black_metal", 0.006)
    # toast slices
    for x in (-0.07, 0.07):
        m.box((0.02, 0.05, 0.11), (x, 0.24, 0.0), "food_brown", 0.005)


@reg("galley", "hanging pots rack")
def _(m, rng):
    m.box((1.2, 0.05, 0.4), (0, -0.025, 0), "black_metal", 0.008)
    m.box((1.0, 0.03, 0.04), (0, -0.065, 0), "steel")
    m.box((1.0, 0.03, 0.04), (0, -0.065, 0.14)) if False else None
    for s in (-1, 1):
        m.link((s * 0.5, -0.05, 0), (s * 0.5, -0.25, 0), 0.008, "chrome", 6)
        m.link((s * 0.5, -0.05, 0.15), (s * 0.5, -0.25, 0.15), 0.008, "chrome", 6) if False else None
    m.cyl(0.015, 1.1, (0, -0.28, 0), "chrome", axis="x", seg=8)
    for s in (-1, 1):
        m.box((0.04, 0.05, 0.04), (s * 0.5, -0.25, 0), "chrome", 0.005)
    for k, (x, r, mat) in enumerate(((-0.42, 0.11, "copper"), (-0.15, 0.09, "steel"), (0.12, 0.13, "copper"), (0.4, 0.08, "black_metal"))):
        m.link((x, -0.28, 0), (x, -0.34, 0), 0.006, "chrome", 4)
        m.cyl(r, 0.14, (x, -0.42 - 0.02 * (k % 2), 0), mat, seg=14)
        m.torus(r * 0.9, 0.006, (x, -0.35 - 0.02 * (k % 2), 0), "chrome", seg=12, tseg=4) if False else None
    for k in range(4):
        x = -0.3 + 0.2 * k
        m.link((x, -0.28, 0), (x, -0.32, 0.0), 0.006, "chrome", 4) if False else None
    for k in range(3):
        m.link((-0.05 + 0.16 * k, -0.3, 0.0), (-0.05 + 0.16 * k, -0.62 - 0.08 * k, 0.0), 0.012, "wood_dark", 6) if False else None
    m.box((0.02, 0.06, 0.02), (0.55, -0.32, 0.0), "chrome") if False else None
    for k in range(3):
        m.link((0.5, -0.3, 0), (0.5, -0.3, 0.0), 0.001) if False else None
    for k, x in enumerate((-0.55, -0.48)):
        m.cyl(0.05, 0.02, (x, -0.35, 0.0), "chrome", seg=6) if False else None


@reg("galley", "trash chute")
def _(m, rng):
    m.box((0.6, 0.8, 0.14), (0, 0, 0.07), "hull_mid", 0.02)
    m.box((0.46, 0.4, 0.04), (0, -0.05, 0.16), "hull_dark", 0.015)
    m.box((0.4, 0.34, 0.02), (0, -0.05, 0.19), "hazard_yellow", 0.005)
    m.box((0.34, 0.28, 0.02), (0, -0.05, 0.2), "black_metal")
    handle(m, (0, 0.05, 0.21), 0.2, "chrome")
    m.box((0.22, 0.1, 0.02), (0, 0.3, 0.145), "plastic_white", 0.004)
    m.box((0.05, 0.05, 0.01), (0.2, -0.28, 0.145), "em_green") if False else None
    m.box((0.05, 0.05, 0.02), (0.2, -0.3, 0.15), "em_red")
    for x in (-0.25, 0.25):
        for y in (-0.35, 0.35):
            m.cyl(0.012, 0.01, (x, y, 0.145), "chrome", axis="z", seg=6)
    m.box((0.2, 0.06, 0.02), (0, 0.3, 0.146), "paint_green") if False else None


make("galley", [
    (["commercial oven", "range with hood", "refrigerator", "chest freezer", "food replicator", "coffee machine",
      "sink unit", "dishwasher", "prep counter", "cutlery drawer", "kitchen island", "water cooler", "soup kettle",
      "steamer", "salad bar", "storage shelving"], "floor", ["crew", "galley"], True, None),
    (["microwave", "toaster"], "table", ["crew", "galley"], False, None),
    (["hanging pots rack"], "ceiling", ["crew", "galley"], False, None),
    (["trash chute"], "wall", ["crew", "galley"], False, 1.0),
])


# ================================================================== TABLEWARE
def plate(m, x, y, z, r=0.12, mat="ceramic", rim="paint_blue"):
    m.cyl(r, 0.012, (x, y + 0.006, z), mat, seg=16, r2=r * 0.9)
    m.torus(r * 0.75, 0.003, (x, y + 0.013, z), rim, seg=16, tseg=3) if rim else None


def cup(m, x, y, z, r=0.04, h=0.09, mat="ceramic", handle_side=1, fill="food_brown"):
    m.cyl(r, h, (x, y + h / 2, z), mat, seg=10, r2=r * 1.12)
    if fill:
        m.cyl(r * 1.05, 0.004, (x, y + h - 0.006, z), fill, seg=10)
    m.torus(r * 0.55, 0.008, (x + handle_side * r * 1.2, y + h * 0.55, z), mat, axis="z", seg=8, tseg=4)


@reg("tableware", "meal tray")
def _(m, rng):
    m.box((0.42, 0.015, 0.3), (0, 0.0075, 0), "plastic_grey", 0.005)
    m.box((0.42, 0.03, 0.012), (0, 0.02, 0.144), "plastic_grey")
    m.box((0.42, 0.03, 0.012), (0, 0.02, -0.144), "plastic_grey")
    m.box((0.012, 0.03, 0.3), (0.204, 0.02, 0), "plastic_grey")
    m.box((0.012, 0.03, 0.3), (-0.204, 0.02, 0), "plastic_grey")
    for i, (x, z, w, d, c) in enumerate(((-0.1, -0.05, 0.17, 0.17, "food_brown"), (0.08, -0.07, 0.12, 0.11, "food_green"),
                                       (0.09, 0.07, 0.13, 0.09, "food_red"))):
        m.box((w, 0.03, d), (x, 0.03, z), "paint_white", 0.006)
        m.box((w - 0.02, 0.03, d - 0.02), (x, 0.038, z), c, 0.01)
    m.cyl(0.035, 0.08, (-0.15, 0.055, 0.09), "glass_blue", seg=10)
    m.box((0.02, 0.008, 0.16), (0.0, 0.019, 0.12), "chrome")


@reg("tableware", "plate stack")
def _(m, rng):
    for k in range(6):
        m.cyl(0.13, 0.014, (0, 0.007 + 0.016 * k, 0), "ceramic", seg=18, r2=0.115)
        m.torus(0.1, 0.003, (0, 0.016 + 0.016 * k, 0), "paint_teal", seg=18, tseg=3)
    m.cyl(0.075, 0.02, (0.0, 0.11, 0), "food_brown", seg=10) if False else None


@reg("tableware", "bowls")
def _(m, rng):
    for k, (x, z, r) in enumerate(((-0.1, 0.0, 0.09), (0.08, -0.05, 0.075), (0.09, 0.09, 0.06))):
        m.cyl(r * 0.5, 0.03, (x, 0.015, z), "ceramic", seg=12, r2=r * 0.7) if False else None
        m.cyl(r * 0.45, 0.02, (x, 0.01, z), "ceramic", seg=12)
        m.cyl(r * 0.5, r * 0.9, (x, 0.02 + r * 0.45, z), ["paint_blue", "paint_teal", "paint_orange"][k], seg=14, r2=r)
        m.cyl(r * 0.92, 0.006, (x, 0.02 + r * 0.9 - 0.012, z), ["food_brown", "food_red", "food_green"][k], seg=14)


@reg("tableware", "cups and mugs")
def _(m, rng):
    cup(m, -0.1, 0, -0.03, 0.04, 0.09, "paint_white")
    cup(m, 0.0, 0, 0.06, 0.045, 0.1, "paint_red", -1)
    cup(m, 0.1, 0, -0.04, 0.038, 0.085, "hull_light")
    m.cyl(0.07, 0.008, (0.0, 0.004, 0.0), "steel", seg=16) if False else None
    m.cyl(0.05, 0.01, (-0.02, 0.005, 0.15), "ceramic", seg=14)
    m.cyl(0.032, 0.05, (-0.02, 0.035, 0.15), "ceramic", seg=10, r2=0.04)


@reg("tableware", "cutlery set")
def _(m, rng):
    m.box((0.2, 0.02, 0.24), (0, 0.01, 0), "crew_sheet", 0.004)
    for k in range(3):
        x = -0.07 + 0.07 * k
        m.box((0.014, 0.008, 0.06), (x, 0.024, 0.07), "brushed_alu", 0.002)
        m.box((0.02, 0.006, 0.05), (x, 0.024, -0.06), "brushed_alu", 0.002) if k != 1 else m.box((0.02, 0.006, 0.05), (x, 0.024, -0.06), "brushed_alu")
        m.box((0.008, 0.008, 0.09), (x, 0.026, 0.0), "brushed_alu")
    m.box((0.05, 0.03, 0.02), (0.0, 0.03, 0.115), "crew_seam") if False else None


@reg("tableware", "pitcher")
def _(m, rng):
    m.cyl(0.075, 0.24, (0, 0.13, 0), "glass_blue", seg=14, r2=0.08)
    m.cyl(0.07, 0.17, (0, 0.09, 0), "water", seg=14, r2=0.075)
    m.cyl(0.078, 0.01, (0, 0.01, 0), "glass_blue", seg=14)
    m.torus(0.08, 0.008, (0, 0.25, 0), "glass_blue", seg=14, tseg=4)
    m.torus(0.06, 0.009, (0.09, 0.14, 0), "glass_blue", axis="z", seg=10, tseg=4, arc=PI * 1.6, rot=(0, 0, 0)) if False else None
    m.torus(0.06, 0.01, (0.09, 0.14, 0), "glass_blue", axis="z", seg=10, tseg=4)
    m.box((0.06, 0.02, 0.05), (-0.09, 0.25, 0), "glass_blue")


@reg("tableware", "bottle and glasses")
def _(m, rng):
    m.cyl(0.04, 0.2, (-0.08, 0.1, 0), "glass_green", seg=12)
    m.cyl(0.04, 0.02, (-0.08, 0.21, 0), "glass_green", seg=12, r2=0.015) if False else None
    m.cyl(0.018, 0.09, (-0.08, 0.25, 0), "glass_green", seg=8)
    m.cyl(0.02, 0.02, (-0.08, 0.305, 0), "gold_trim", seg=8)
    m.box((0.06, 0.08, 0.002), (-0.08, 0.11, 0.041), "paint_white") if False else None
    m.cyl(0.041, 0.09, (-0.08, 0.1, 0), "paint_white", seg=12) if False else None
    for k, (x, z) in enumerate(((0.06, 0.05), (0.1, -0.03))):
        m.cyl(0.035, 0.1, (x, 0.05, z), "glass", seg=10, r2=0.04)
        m.cyl(0.03, 0.04, (x, 0.03, z), "water" if k == 0 else "food_red", seg=10)
        m.cyl(0.03, 0.006, (x, 0.003, z), "glass", seg=10)


@reg("tableware", "fruit bowl")
def _(m, rng):
    m.cyl(0.08, 0.03, (0, 0.015, 0), "wood_dark", seg=14)
    m.cyl(0.05, 0.02, (0, 0.04, 0), "wood_dark", seg=14, r2=0.16)
    m.cyl(0.155, 0.01, (0, 0.055, 0), "wood_dark", seg=16, r2=0.17) if False else None
    for k, (x, y, z, c, r) in enumerate(((-0.06, 0.1, 0.02, "food_red", 0.04), (0.05, 0.1, -0.04, "food_green", 0.04),
                                       (0.06, 0.1, 0.06, "paint_orange", 0.042), (-0.04, 0.09, -0.07, "crew_cheese", 0.035),
                                       (0.0, 0.14, 0.0, "food_red", 0.04))):
        m.sphere(r, (x, y, z), c, 8, 6)
    m.box((0.14, 0.02, 0.03), (0.02, 0.15, 0.07), "crew_cheese", rot=(0, 0.6, 0.2)) if False else None


@reg("tableware", "teapot")
def _(m, rng):
    m.sphere(0.09, (0, 0.1, 0), "ceramic", 14, 9, scale=(1, 0.9, 1))
    m.cyl(0.05, 0.02, (0, 0.012, 0), "ceramic", seg=12) if False else None
    m.torus(0.08, 0.01, (0, 0.03, 0), "paint_blue", seg=14, tseg=4)
    m.torus(0.08, 0.01, (0, 0.14, 0), "paint_blue", seg=14, tseg=4) if False else None
    m.cyl(0.05, 0.015, (0, 0.187, 0), "ceramic", seg=12)
    m.sphere(0.018, (0, 0.21, 0), "paint_blue", 8, 5)
    m.link((0.07, 0.09, 0), (0.17, 0.16, 0), 0.015, "ceramic", 8)
    m.link((0.17, 0.16, 0), (0.185, 0.185, 0), 0.01, "ceramic", 8)
    m.torus(0.05, 0.011, (-0.1, 0.11, 0), "ceramic", axis="z", seg=12, tseg=5)


@reg("tableware", "food container")
def _(m, rng):
    m.box((0.28, 0.09, 0.2), (0, 0.045, 0), "plastic_grey", 0.012)
    m.box((0.27, 0.03, 0.19), (0, 0.105, 0), "glass", 0.008)
    m.box((0.24, 0.04, 0.16), (0, 0.075, 0), "food_brown", 0.02)
    m.box((0.06, 0.03, 0.02), (0.0, 0.125, 0.0), "hull_dark") if False else None
    for s in (-1, 1):
        m.box((0.03, 0.04, 0.03), (s * 0.14, 0.09, 0.0), "plastic_black", 0.006)
    m.box((0.28, 0.006, 0.01), (0, 0.045, 0.101), "hazard_yellow") if False else None
    m.box((0.1, 0.03, 0.002), (0, 0.045, 0.101), "paint_white")


@reg("tableware", "condiments")
def _(m, rng):
    m.box((0.22, 0.02, 0.1), (0, 0.01, 0), "steel", 0.005)
    m.cyl(0.028, 0.14, (-0.07, 0.09, 0), "food_red", seg=10, r2=0.02)
    m.cyl(0.012, 0.03, (-0.07, 0.175, 0), "food_red", seg=8, r2=0.006)
    m.cyl(0.028, 0.14, (0.0, 0.09, 0.0), "crew_cheese", seg=10, r2=0.02)
    m.cyl(0.012, 0.03, (0.0, 0.175, 0), "crew_cheese", seg=8, r2=0.006)
    m.cyl(0.024, 0.08, (0.07, 0.06, -0.01), "glass", seg=10)
    m.cyl(0.026, 0.02, (0.07, 0.11, -0.01), "chrome", seg=10, r2=0.02)
    m.cyl(0.024, 0.08, (0.05, 0.06, 0.03), "glass", seg=10) if False else None


@reg("tableware", "napkin dispenser")
def _(m, rng):
    m.box((0.14, 0.12, 0.1), (0, 0.06, 0), "plastic_grey", 0.01)
    m.box((0.12, 0.09, 0.09), (0, 0.11, 0.0), "crew_sheet", 0.004)
    m.box((0.14, 0.008, 0.11), (0, 0.124, 0), "steel")
    m.box((0.1, 0.04, 0.008), (0, 0.07, 0.052), "hull_dark", 0.002)
    m.box((0.02, 0.008, 0.04), (0.0, 0.135, 0.02), "crew_sheet", rot=(0.3, 0, 0.2))
    m.box((0.02, 0.005, 0.02), (0.0, 0.07, 0.056), "em_amber") if False else None


@reg("tableware", "bread basket")
def _(m, rng):
    m.box((0.32, 0.02, 0.22), (0, 0.01, 0), "wood_light", 0.004)
    for s in (-1, 1):
        m.box((0.32, 0.08, 0.012), (0, 0.06, s * 0.11), "wood_light", 0.003, rot=(s * 0.15, 0, 0))
        m.box((0.012, 0.08, 0.22), (s * 0.16, 0.06, 0), "wood_light", 0.003, rot=(0, 0, -s * 0.15))
    for k in range(4):
        m.box((0.32, 0.008, 0.006), (0, 0.03 + 0.02 * k, 0.108 + 0.0), "wood_dark") if False else None
    m.sphere(0.06, (-0.07, 0.07, 0.0), "crew_bread", 10, 6, scale=(1.4, 0.7, 0.9))
    m.sphere(0.055, (0.07, 0.07, 0.03), "crew_bread", 10, 6, scale=(1.2, 0.7, 0.9))
    m.sphere(0.05, (0.01, 0.1, -0.03), "crew_bread", 10, 6, scale=(1.3, 0.7, 0.9))
    m.box((0.3, 0.005, 0.12), (0, 0.05, 0), "fabric_red", rot=(0, 0.2, 0)) if False else None


@reg("tableware", "salad")
def _(m, rng):
    m.cyl(0.07, 0.02, (0, 0.01, 0), "ceramic", seg=14)
    m.cyl(0.08, 0.1, (0, 0.07, 0), "glass", seg=16, r2=0.14)
    m.cyl(0.13, 0.05, (0, 0.05, 0), "food_green", seg=14, r2=0.135) if False else None
    for k in range(8):
        a = k * PI / 4 + rng.random()
        r = rng.uniform(0.02, 0.09)
        m.sphere(0.035, (r * math.cos(a), 0.11 + 0.01 * (k % 2), r * math.sin(a)), ["food_green", "leaf", "food_red", "food_green"][k % 4], 6, 4, scale=(1, 0.6, 1))
    m.cyl(0.12, 0.05, (0, 0.085, 0), "food_green", seg=12, r2=0.13)
    m.sphere(0.03, (0.04, 0.125, 0.03), "food_red", 6, 4)
    m.sphere(0.03, (-0.04, 0.125, -0.02), "food_red", 6, 4)
    m.sphere(0.025, (0.0, 0.13, -0.05), "crew_cheese", 6, 4)


@reg("tableware", "pizza meal")
def _(m, rng):
    m.cyl(0.19, 0.012, (0, 0.006, 0), "plastic_white", seg=20)
    m.cyl(0.17, 0.02, (0, 0.022, 0), "crew_bread", seg=20)
    m.cyl(0.155, 0.006, (0, 0.035, 0), "crew_cheese", seg=20)
    for k in range(9):
        a = k * 2 * PI / 9 + 0.3
        r = 0.06 if k % 2 else 0.11
        m.cyl(0.022, 0.006, (r * math.cos(a), 0.041, r * math.sin(a)), "food_red", seg=8)
    for k in range(4):
        m.sphere(0.01, (0.07 * math.cos(k * 1.57 + 0.6), 0.043, 0.07 * math.sin(k * 1.57 + 0.6)), "food_green", 5, 4)
    for a in (0.0, 0.8, 1.6, 2.4):
        m.box((0.34, 0.004, 0.004), (0, 0.044, 0), "crew_bread", rot=(0, a, 0))


@reg("tableware", "lunch box")
def _(m, rng):
    m.box((0.26, 0.09, 0.16), (0, 0.045, 0), "paint_orange", 0.015)
    m.box((0.27, 0.03, 0.17), (0, 0.105, 0), "hull_light", 0.012)
    m.box((0.02, 0.06, 0.02), (0, 0.09, 0.09), "chrome", 0.004)
    m.torus(0.06, 0.008, (0, 0.135, 0), "black_metal", axis="z", seg=12, tseg=4, arc=PI, rot=(0, 0, 0))
    for s in (-1, 1):
        m.cyl(0.012, 0.01, (s * 0.132, 0.115, 0), "black_metal", axis="x", seg=6)
    m.box((0.12, 0.05, 0.004), (0, 0.05, 0.082), "paint_white")
    m.box((0.08, 0.02, 0.004), (0, 0.05, 0.085), "paint_red")


make("tableware", [(["meal tray", "plate stack", "bowls", "cups and mugs", "cutlery set", "pitcher", "bottle and glasses",
                     "fruit bowl", "teapot", "food container", "condiments", "napkin dispenser", "bread basket",
                     "salad", "pizza meal", "lunch box"], "table", ["crew", "mess", "tableware"], False, None)])


# ================================================================== LAMP
@reg("lamp", "table lamp")
def _(m, rng):
    m.cyl(0.09, 0.02, (0, 0.01, 0), "brass", seg=14, bevel=0.005)
    m.cyl(0.03, 0.22, (0, 0.13, 0), "brass", seg=10)
    m.sphere(0.06, (0, 0.14, 0), "brass", 10, 6)
    m.cyl(0.12, 0.2, (0, 0.34, 0), "crew_shade", seg=18, r2=0.07, cap=False)
    m.sphere(0.035, (0, 0.34, 0), "em_warm", 8, 6)
    m.cyl(0.125, 0.01, (0, 0.24, 0), "brass", seg=18, r2=0.125, cap=False) if False else None
    m.torus(0.12, 0.005, (0, 0.24, 0), "brass", seg=16, tseg=4)
    m.torus(0.07, 0.005, (0, 0.44, 0), "brass", seg=16, tseg=4)
    m.sphere(0.012, (0, 0.46, 0), "brass", 6, 4)


@reg("lamp", "floor lamp")
def _(m, rng):
    m.cyl(0.16, 0.03, (0, 0.015, 0), "black_metal", seg=18, bevel=0.006)
    m.cyl(0.015, 1.5, (0, 0.78, 0), "black_metal", seg=8)
    m.link((0, 1.5, 0), (0.25, 1.72, 0), 0.015, "black_metal", 8)
    m.sphere(0.02, (0, 1.5, 0), "black_metal", 6, 4)
    m.cyl(0.16, 0.2, (0.3, 1.66, 0), "paint_teal", seg=16, r2=0.06, rot=(0, 0, 0.0))
    m.sphere(0.06, (0.3, 1.58, 0), "em_warm", 8, 6)
    m.sphere(0.02, (0.25, 1.72, 0), "black_metal", 6, 4)
    m.cyl(0.05, 0.02, (0, 0.5, 0), "black_metal", seg=8) if False else None
    m.box((0.06, 0.03, 0.03), (0, 0.9, 0.025), "black_metal") if False else None
    m.cyl(0.025, 0.05, (0, 0.95, 0), "brass", seg=8)


@reg("lamp", "architect desk lamp")
def _(m, rng):
    m.box((0.14, 0.03, 0.12), (0, 0.015, 0), "black_metal", 0.008)
    m.link((0, 0.03, 0), (0.05, 0.3, -0.05), 0.008, "paint_grey", 6)
    m.link((0.05, 0.3, -0.05), (0.3, 0.42, 0.05), 0.008, "paint_grey", 6)
    m.sphere(0.014, (0.05, 0.3, -0.05), "chrome", 6, 4)
    m.sphere(0.014, (0.3, 0.42, 0.05), "chrome", 6, 4)
    m.link((0.05, 0.3, -0.05), (0.05, 0.05, -0.03), 0.003, "chrome", 4)
    m.cyl(0.06, 0.12, (0.34, 0.38, 0.07), "paint_grey", seg=14, r2=0.03, rot=(0.3, 0, -0.9))
    m.sphere(0.028, (0.36, 0.34, 0.08), "em_white", 8, 6)
    m.box((0.02, 0.03, 0.02), (0.08, 0.035, 0.06), "paint_red") if False else None


@reg("lamp", "decorative lantern")
def _(m, rng):
    m.cyl(0.075, 0.02, (0, 0.01, 0), "black_metal", seg=6)
    m.cyl(0.07, 0.2, (0, 0.13, 0), "glass_amber", seg=6, r2=0.09)
    for k in range(6):
        a = k * PI / 3
        m.link((0.07 * math.cos(a), 0.03, 0.07 * math.sin(a)), (0.09 * math.cos(a), 0.23, 0.09 * math.sin(a)), 0.006, "black_metal", 4)
    m.cyl(0.03, 0.14, (0, 0.11, 0), "em_amber", seg=8)
    m.cyl(0.1, 0.03, (0, 0.245, 0), "black_metal", seg=6, r2=0.03)
    m.torus(0.05, 0.006, (0, 0.31, 0), "black_metal", axis="z", seg=8, tseg=4, arc=PI)
    m.sphere(0.016, (0, 0.27, 0), "black_metal", 6, 4)


@reg("lamp", "bedside light")
def _(m, rng):
    m.box((0.14, 0.03, 0.12), (0, 0.015, 0), "hull_dark", 0.008)
    m.cyl(0.05, 0.16, (0, 0.11, 0), "hull_light", seg=14, r2=0.04)
    m.sphere(0.1, (0, 0.23, 0), "glass", 14, 10)
    m.sphere(0.06, (0, 0.23, 0), "em_warm", 10, 6)
    m.cyl(0.05, 0.01, (0, 0.2, 0), "hull_light", seg=10) if False else None
    m.box((0.04, 0.012, 0.012), (0, 0.045, 0.06), "em_cyan")


@reg("lamp", "uplight")
def _(m, rng):
    m.box((0.36, 0.03, 0.36), (0, 0.015, 0), "black_metal", 0.008)
    m.box((0.05, 1.42, 0.05), (0, 0.74, 0), "brushed_alu", 0.01)
    m.box((0.36, 0.09, 0.36), (0, 1.52, 0), "hull_light", 0.02)
    m.box((0.32, 0.03, 0.32), (0, 1.575, 0), "em_white")
    m.box((0.34, 0.11, 0.02), (0, 1.55, 0.18), "hull_light") if False else None
    for s in (-1, 1):
        m.box((0.015, 0.11, 0.36), (s * 0.18, 1.6, 0), "hull_light") if False else None
    m.box((0.05, 0.03, 0.03), (0, 1.0, 0.04), "black_metal")
    m.cyl(0.012, 0.02, (0, 1.0, 0.055), "em_amber", axis="z", seg=6)
    m.box((0.05, 0.05, 0.05), (0, 0.06, 0.0), "brushed_alu") if False else None


@reg("lamp", "holo lamp")
def _(m, rng):
    m.cyl(0.13, 0.04, (0, 0.02, 0), "hull_dark", seg=16, bevel=0.008)
    m.torus(0.1, 0.008, (0, 0.045, 0), "em_cyan", seg=20, tseg=4)
    m.cyl(0.04, 0.03, (0, 0.06, 0), "black_metal", seg=10)
    m.cyl(0.02, 0.3, (0, 0.24, 0), "em_blue", seg=8, r2=0.1, cap=False) if False else None
    m.cyl(0.03, 0.34, (0, 0.24, 0), "glass_blue", seg=12, r2=0.1, cap=False)
    m.sphere(0.055, (0, 0.24, 0), "em_cyan", 10, 6)
    for k in range(3):
        m.torus(0.05 + 0.012 * k, 0.003, (0, 0.14 + 0.09 * k, 0), "em_cyan", seg=16, tseg=3)
    m.sphere(0.02, (0, 0.44, 0), "em_white", 6, 4)


@reg("lamp", "reading light")
def _(m, rng):
    m.box((0.1, 0.16, 0.03), (0, 0, 0.015), "hull_dark", 0.008)
    m.link((0, 0.02, 0.03), (0, 0.06, 0.16), 0.012, "chrome", 6)
    m.sphere(0.018, (0, 0.06, 0.16), "chrome", 6, 4)
    m.cyl(0.05, 0.1, (0, 0.03, 0.21), "hull_light", seg=12, r2=0.03, axis="z", rot=(0.4, 0, 0))
    m.sphere(0.028, (0, 0.0, 0.25), "em_warm", 8, 6)
    m.box((0.03, 0.012, 0.006), (0, -0.05, 0.032), "em_green")


make("lamp", [
    (["table lamp", "architect desk lamp", "decorative lantern", "bedside light", "holo lamp"], "table", ["crew", "lamp"], False, None),
    (["floor lamp", "uplight"], "floor", ["crew", "lamp"], False, None),
    (["reading light"], "wall", ["crew", "lamp"], False, 1.4),
])


# ================================================================== PLANT
def pot_(m, r, h, mat="crew_pot", y=0.0, soil=True):
    m.cyl(r * 0.75, h, (0, y + h / 2, 0), mat, seg=14, r2=r, bevel=0.008)
    m.torus(r, 0.014, (0, y + h, 0), mat, seg=14, tseg=4)
    if soil:
        m.cyl(r * 0.97, 0.01, (0, y + h - 0.02, 0), "soil", seg=14)


def leafcloud(m, rng, cx, cy, cz, spread, n, size, mats=("leaf", "food_green")):
    for k in range(n):
        a = rng.uniform(0, 2 * PI)
        r = rng.uniform(0.2, 1.0) * spread
        h = rng.uniform(-0.6, 0.6) * spread
        m.sphere(size * rng.uniform(0.7, 1.2), (cx + r * math.cos(a), cy + h, cz + r * math.sin(a)), mats[k % len(mats)], 6, 4,
                 scale=(1.2, 0.6, 1.0))


def frond(m, x, y, z, ang, length, mat="leaf", w=0.05, lift=0.8):
    """Arching two-segment frond radiating from (x,y,z) at heading ang."""
    dx, dz = math.cos(ang), math.sin(ang)
    p1 = (x + dx * length * 0.5, y + length * lift * 0.6, z + dz * length * 0.5)
    p2 = (x + dx * length, y + length * lift * 0.35, z + dz * length)
    m.link((x, y, z), p1, w * 0.12, "leaf", 4)
    m.link(p1, p2, w * 0.1, "leaf", 4)
    m.sphere(w, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2), mat, 6, 4, scale=(1.0, 0.25, 1.0)) if False else None
    m.sphere(w * 1.4, (p2[0], p2[1] - 0.02, p2[2]), mat, 6, 4, scale=(1.4, 0.35, 1.0))
    m.sphere(w * 1.2, (p1[0], p1[1], p1[2]), mat, 6, 4, scale=(1.4, 0.35, 1.0))


@reg("plant", "ficus tree")
def _(m, rng):
    pot_(m, 0.25, 0.4)
    m.cyl(0.03, 1.0, (0, 0.85, 0), "wood_dark", seg=8, r2=0.02)
    for k in range(3):
        a = k * 2.1
        m.link((0, 0.9 + 0.1 * k, 0), (0.22 * math.cos(a), 1.35 + 0.1 * k, 0.22 * math.sin(a)), 0.012, "wood_dark", 5)
    leafcloud(m, rng, 0, 1.6, 0, 0.42, 14, 0.13)
    m.sphere(0.24, (0, 1.6, 0), "leaf", 8, 6)
    for k in range(3):
        a = k * 2.1
        m.sphere(0.16, (0.25 * math.cos(a), 1.35 + 0.1 * k, 0.25 * math.sin(a)), "food_green", 7, 5)


@reg("plant", "fern")
def _(m, rng):
    pot_(m, 0.22, 0.3, "concrete")
    n = 11
    for k in range(n):
        a = 2 * PI * k / n + rng.uniform(-0.15, 0.15)
        frond(m, 0.03 * math.cos(a), 0.3, 0.03 * math.sin(a), a, rng.uniform(0.5, 0.7), "leaf" if k % 2 else "food_green", 0.06, 0.9 + 0.25 * (k % 3))
    m.sphere(0.08, (0, 0.38, 0), "leaf", 6, 4)


@reg("plant", "succulent set")
def _(m, rng):
    for i, (x, z, r) in enumerate(((-0.14, 0.0, 0.07), (0.05, 0.08, 0.06), (0.09, -0.08, 0.055))):
        m.cyl(r * 0.8, r * 1.2, (x, r * 0.6, z), ["ceramic", "paint_teal", "paint_orange"][i], seg=10, r2=r)
        m.cyl(r * 0.95, 0.006, (x, r * 1.2 - 0.005, z), "soil", seg=10)
        for k in range(5):
            a = k * 2 * PI / 5 + i
            m.sphere(r * 0.45, (x + r * 0.5 * math.cos(a), r * 1.4 + 0.02, z + r * 0.5 * math.sin(a)), "food_green" if i != 1 else "leaf", 5, 4, scale=(0.7, 1.0, 0.7))
        m.sphere(r * 0.45, (x, r * 1.55, z), "leaf", 6, 4)
    m.box((0.36, 0.015, 0.3), (0, 0.0075, 0), "wood_light", 0.004)


@reg("plant", "hanging plant")
def _(m, rng):
    m.cyl(0.05, 0.02, (0, -0.01, 0), "black_metal", seg=10)
    for k in range(3):
        a = k * 2 * PI / 3
        m.link((0, -0.02, 0), (0.15 * math.cos(a), -0.55, 0.15 * math.sin(a)), 0.004, "black_metal", 4)
    m.sphere(0.2, (0, -0.68, 0), "crew_pot", 14, 8, scale=(1.0, 0.7, 1.0))
    m.torus(0.17, 0.02, (0, -0.55, 0), "crew_pot", seg=14, tseg=4)
    m.cyl(0.16, 0.01, (0, -0.56, 0), "soil", seg=12)
    for k in range(7):
        a = k * 2 * PI / 7
        L = rng.uniform(0.35, 0.8)
        x, z = 0.16 * math.cos(a), 0.16 * math.sin(a)
        m.link((x, -0.6, z), (x * 1.5, -0.6 - L, z * 1.5), 0.005, "leaf", 4)
        for j in range(2):
            m.sphere(0.045, (x * (1.1 + 0.15 * j), -0.65 - L * (j + 1) / 2.6, z * (1.1 + 0.15 * j)), "food_green" if j % 2 else "leaf", 5, 4, scale=(1, 0.5, 1))
    m.sphere(0.14, (0, -0.55, 0), "leaf", 8, 5, scale=(1, 0.7, 1))


@reg("plant", "bonsai")
def _(m, rng):
    m.box((0.3, 0.05, 0.2), (0, 0.025, 0), "paint_navy", 0.01)
    m.box((0.26, 0.02, 0.16), (0, 0.06, 0), "soil", 0.004)
    for x in (-0.11, 0.11):
        for z in (-0.06, 0.06):
            m.box((0.03, 0.02, 0.03), (x, 0.0, z), "paint_navy") if False else None
    pts = [(0, 0.06, 0), (0.03, 0.14, 0.01), (-0.02, 0.22, 0.0), (0.03, 0.29, -0.01)]
    m.tube(pts, 0.012, "wood_dark", 6)
    m.link((0.03, 0.29, -0.01), (0.13, 0.33, 0.02), 0.007, "wood_dark", 5)
    m.link((-0.02, 0.22, 0.0), (-0.12, 0.26, 0.03), 0.007, "wood_dark", 5)
    for (x, y, z, r) in ((0.03, 0.34, -0.01, 0.09), (0.14, 0.34, 0.02, 0.06), (-0.13, 0.28, 0.03, 0.07)):
        m.sphere(r, (x, y, z), "leaf", 9, 6, scale=(1.3, 0.55, 1.0))
        m.sphere(r * 0.6, (x + 0.02, y + 0.03, z), "food_green", 6, 4, scale=(1.2, 0.5, 1.0))


@reg("plant", "planter box")
def _(m, rng):
    m.box((1.2, 0.4, 0.35), (0, 0.2, 0), "hull_mid", 0.02)
    m.box((1.24, 0.04, 0.39), (0, 0.42, 0), "steel", 0.008)
    m.box((1.1, 0.01, 0.28), (0, 0.415, 0), "soil")
    for x in (-0.5, 0.5):
        m.box((0.05, 0.42, 0.37), (x, 0.21, 0), "hull_dark") if False else None
    for k in range(5):
        x = -0.48 + 0.24 * k
        h = rng.uniform(0.3, 0.5)
        m.sphere(0.13, (x, 0.5 + h * 0.4, rng.uniform(-0.05, 0.05)), "leaf" if k % 2 else "food_green", 8, 5, scale=(1.0, 1.3, 1.0))
    for k in range(4):
        x = -0.36 + 0.24 * k
        m.link((x, 0.42, 0.08), (x, 0.62, 0.1), 0.006, "leaf", 4)
        m.sphere(0.035, (x, 0.65, 0.1), ["crew_flower", "crew_flower2"][k % 2], 6, 4)
    m.box((1.1, 0.03, 0.01), (0, 0.15, 0.176), "hazard_yellow")
    for x in (-0.55, 0.55):
        m.box((0.05, 0.05, 0.05), (x, 0.03, 0), "black_metal", 0.006)


@reg("plant", "flower vase")
def _(m, rng):
    m.cyl(0.05, 0.05, (0, 0.025, 0), "glass_blue", seg=12, r2=0.09)
    m.cyl(0.09, 0.1, (0, 0.1, 0), "glass_blue", seg=12, r2=0.05)
    m.cyl(0.05, 0.08, (0, 0.19, 0), "glass_blue", seg=12, r2=0.06)
    m.cyl(0.05, 0.14, (0, 0.09, 0), "water", seg=10)
    cols = ["crew_flower", "crew_flower2", "paint_red", "paint_white", "crew_flower"]
    for k in range(5):
        a = k * 2 * PI / 5
        tip = (0.11 * math.cos(a), 0.4 + 0.05 * (k % 2), 0.11 * math.sin(a))
        m.link((0.01 * math.cos(a), 0.1, 0.01 * math.sin(a)), tip, 0.004, "leaf", 4)
        m.sphere(0.04, tip, cols[k], 7, 5, scale=(1, 0.7, 1))
        m.sphere(0.015, (tip[0], tip[1] + 0.02, tip[2]), "crew_flower2" if k != 1 else "brass", 5, 4)
    m.link((0, 0.1, 0), (0, 0.46, 0), 0.004, "leaf", 4)
    m.sphere(0.04, (0, 0.47, 0), "crew_flower", 7, 5, scale=(1, 0.7, 1))


@reg("plant", "moss wall panel")
def _(m, rng):
    m.box((1.0, 0.7, 0.05), (0, 0, 0.025), "wood_dark", 0.01)
    m.box((0.9, 0.6, 0.02), (0, 0, 0.06), "soil")
    for i in range(6):
        for j in range(4):
            x = -0.38 + 0.152 * i + (0.07 if j % 2 else 0)
            y = -0.22 + 0.15 * j
            m.sphere(0.085, (x, y, 0.08), "crew_moss" if (i + j) % 3 else "leaf", 7, 4, scale=(1, 1, 0.4))
    for k in range(4):
        m.sphere(0.03, (rng.uniform(-0.35, 0.35), rng.uniform(-0.25, 0.25), 0.11), ["crew_flower", "crew_flower2"][k % 2], 5, 4, scale=(1, 1, 0.5))
    m.box((1.0, 0.03, 0.06), (0, -0.365, 0.03), "steel", 0.005)
    led(m, (0, 0.375, 0.07), (0.8, 0.02, 0.02), "em_white")


make("plant", [
    (["ficus tree", "fern", "planter box"], "floor", ["crew", "plant"], False, None),
    (["succulent set", "bonsai", "flower vase"], "table", ["crew", "plant"], False, None),
    (["hanging plant"], "ceiling", ["crew", "plant"], False, None),
    (["moss wall panel"], "wall", ["crew", "plant"], False, 1.5),
])


# ================================================================== GYM
def rubber_feet(m, pts, r=0.03):
    for x, z in pts:
        m.cyl(r, 0.03, (x, 0.015, z), "rubber", seg=8)


def plates(m, x, y, z, n=2, r=0.2, mat="black_metal"):
    for k in range(n):
        m.cyl(r - 0.02 * k, 0.03, (x + k * 0.035 * (1 if x > 0 else -1), y, z), mat, axis="x", seg=16)


@reg("gym", "treadmill")
def _(m, rng):
    m.box((0.85, 0.14, 1.85), (0, 0.16, 0.0), "hull_dark", 0.02)
    m.box((0.5, 0.02, 1.45), (0, 0.24, 0.05), "rubber", 0.005)
    for k in range(5):
        m.box((0.5, 0.004, 0.03), (0, 0.252, -0.5 + 0.25 * k), "plastic_grey")
    for s in (-1, 1):
        m.box((0.14, 0.04, 1.5), (s * 0.3, 0.25, 0.05), "hull_mid", 0.008)
        m.box((0.05, 0.02, 1.5), (s * 0.4, 0.27, 0.05), "black_metal") if False else None
        m.link((s * 0.36, 0.2, -0.8), (s * 0.36, 1.05, -0.85), 0.03, "hull_mid", 8)
        m.cyl(0.05, 0.3, (s * 0.36, 0.2, 0.9), "steel", axis="y", seg=6) if False else None
    m.cyl(0.07, 0.6, (0, 0.2, -0.85), "hull_mid", axis="x", seg=12)
    m.cyl(0.07, 0.6, (0, 0.2, 0.9), "hull_mid", axis="x", seg=12)
    m.box((0.78, 0.22, 0.14), (0, 1.1, -0.88), "hull_dark", 0.02)
    m.box((0.7, 0.12, 0.3), (0, 1.15, -0.76), "hull_dark", 0.02, rot=(0.35, 0, 0)) if False else None
    m.screen((0.32, 0.16), (0, 1.15, -0.795), "vitals", rot=(0.0, 0, 0), bezel=0.015)
    for k in range(4):
        m.box((0.05, 0.02, 0.005), (-0.3 + 0.05 * k, 1.05, -0.805), ["em_green", "em_amber", "em_cyan", "em_red"][k])
    m.cyl(0.02, 0.6, (0, 1.05, -0.7), "rubber", axis="x", seg=8) if False else None
    m.link((-0.36, 1.05, -0.85), (-0.38, 0.95, -0.55), 0.02, "rubber", 6)
    m.link((0.36, 1.05, -0.85), (0.38, 0.95, -0.55), 0.02, "rubber", 6)
    m.box((0.88, 0.08, 0.18), (0, 0.12, 0.92), "black_metal", 0.01)
    rubber_feet(m, [(-0.4, -0.85), (0.4, -0.85), (-0.4, 0.85), (0.4, 0.85)])


@reg("gym", "exercise bike")
def _(m, rng):
    m.box((0.6, 0.05, 0.08), (0, 0.025, -0.4), "black_metal", 0.008)
    m.box((0.6, 0.05, 0.08), (0, 0.025, 0.45), "black_metal", 0.008)
    m.link((0, 0.05, 0.0), (0, 0.5, 0.05), 0.04, "hull_mid", 8) if False else None
    m.link((0, 0.03, -0.4), (0, 0.45, -0.05), 0.035, "paint_red", 8) if False else None
    m.link((0, 0.03, -0.4), (0, 0.55, 0.1), 0.035, "paint_red", 8)
    m.link((0, 0.03, 0.45), (0, 0.75, 0.35), 0.03, "paint_red", 8)
    m.link((0, 0.55, 0.1), (0, 0.8, -0.3), 0.03, "paint_red", 8) if False else None
    m.link((0, 0.55, 0.1), (0, 1.05, -0.28), 0.03, "paint_red", 8) if False else None
    m.link((0, 0.3, -0.42), (0, 0.85, -0.2), 0.03, "paint_red", 8) if False else None
    m.cyl(0.26, 0.09, (0, 0.38, -0.32), "hull_dark", axis="x", seg=18)
    m.cyl(0.2, 0.1, (0, 0.38, -0.32), "steel", axis="x", seg=16)
    m.link((0, 0.38, -0.32), (0, 0.9, 0.05), 0.03, "paint_red", 8) if False else None
    m.link((0, 0.38, -0.32), (0, 0.85, 0.0), 0.035, "paint_red", 8) if False else None
    # seat post + seat
    m.link((0, 0.5, 0.1), (0, 0.98, 0.32), 0.03, "steel", 8) if False else None
    m.link((0, 0.55, 0.1), (0, 1.0, 0.3), 0.03, "steel", 8)
    m.box((0.22, 0.06, 0.28), (0, 1.03, 0.36), "leather_black", 0.025)
    # handle post
    m.link((0, 0.38, -0.32), (0, 1.05, -0.5), 0.03, "paint_red", 8)
    m.box((0.5, 0.04, 0.05), (0, 1.1, -0.55), "black_metal", 0.012)
    m.cyl(0.025, 0.14, (0.28, 1.1, -0.55), "rubber", axis="x", seg=8)
    m.cyl(0.025, 0.14, (-0.28, 1.1, -0.55), "rubber", axis="x", seg=8)
    m.box((0.2, 0.12, 0.06), (0, 1.2, -0.55), "hull_dark", 0.01)
    m.screen((0.14, 0.07), (0, 1.2, -0.518), "vitals")
    # pedals
    m.link((0.14, 0.38, -0.32), (0.22, 0.25, -0.15), 0.014, "steel", 6) if False else None
    for s in (-1, 1):
        m.box((0.09, 0.02, 0.14), (s * 0.2, 0.38 - s * 0.14, -0.32 + s * 0.02), "rubber", 0.005)
        m.link((s * 0.12, 0.38, -0.32), (s * 0.12, 0.38 - s * 0.14, -0.32 + s * 0.02), 0.012, "steel", 5)
    m.link((0, 0.55, 0.1), (0, 0.3, -0.42), 0.03, "paint_red", 8) if False else None
    m.link((0, 0.03, 0.45), (0, 0.5, 0.15), 0.025, "paint_red", 8) if False else None


@reg("gym", "weight bench and rack")
def _(m, rng):
    cush(m, (0.3, 0.09, 1.1), (0, 0.44, 0.25), "leather_black", 0.035, seam="hazard_yellow")
    cush(m, (0.3, 0.09, 0.3), (0, 0.55, 0.65), "leather_black", 0.035, seam=None) if False else None
    m.box((0.06, 0.05, 1.0), (0, 0.38, 0.25), "black_metal", 0.008)
    for z in (-0.1, 0.6):
        m.box((0.55, 0.05, 0.06), (0, 0.025, z), "black_metal", 0.008)
        m.box((0.06, 0.3, 0.06), (0, 0.2, z), "black_metal", 0.008)
    for s in (-1, 1):
        m.box((0.06, 1.4, 0.06), (s * 0.5, 0.7, -0.5), "hull_dark", 0.008)
        m.box((0.06, 0.05, 0.9), (s * 0.5, 0.025, -0.1), "hull_dark", 0.008)
        m.box((0.04, 0.05, 0.06), (s * 0.5, 1.0, -0.42), "hazard_yellow", 0.006) if False else None
        m.box((0.08, 0.04, 0.14), (s * 0.5, 0.95, -0.42), "hazard_yellow", 0.006)
        m.box((0.06, 0.6, 0.06), (s * 0.5, 0.3, 0.3), "hull_dark", 0.008) if False else None
        m.link((s * 0.5, 0.05, -0.1), (s * 0.5, 0.8, -0.5), 0.02, "hull_dark", 6) if False else None
    m.box((1.06, 0.06, 0.06), (0, 0.05, -0.5), "hull_dark", 0.008)
    m.box((1.06, 0.05, 0.05), (0, 1.35, -0.5), "hull_dark", 0.008)
    m.cyl(0.014, 1.9, (0, 1.02, -0.42), "chrome", axis="x", seg=8)
    plates(m, 0.7, 1.02, -0.42, 3, 0.2, "black_metal")
    plates(m, -0.7, 1.02, -0.42, 3, 0.2, "black_metal")
    plates(m, 0.7, 1.02, -0.42, 1, 0.0) if False else None
    m.cyl(0.045, 0.07, (0.52, 1.02, -0.42), "steel", axis="x", seg=8) if False else None
    for s in (-1, 1):
        m.cyl(0.03, 0.03, (s * 0.85, 1.02, -0.42), "chrome", axis="x", seg=8)


@reg("gym", "punching bag")
def _(m, rng):
    m.box((0.9, 0.05, 0.9), (0, 0.025, 0), "black_metal", 0.01)
    m.cyl(0.4, 0.3, (0, 0.2, 0), "black_metal", seg=16, r2=0.4) if False else None
    m.cyl(0.05, 2.1, (0, 1.05, -0.35), "hull_dark", seg=10)
    m.box((0.08, 0.08, 0.8), (0, 2.12, -0.05), "hull_dark", 0.01)
    m.cyl(0.4, 0.05, (0, 0.04, -0.35), "hull_dark", seg=16) if False else None
    m.box((0.1, 0.04, 0.12), (0, 2.08, 0.3), "steel") if False else None
    m.link((0, 2.1, 0.3), (0.06, 1.75, 0.3), 0.01, "chrome", 5)
    m.link((0, 2.1, 0.3), (-0.06, 1.75, 0.3), 0.01, "chrome", 5)
    m.cyl(0.16, 1.25, (0, 1.0, 0.3), "paint_red", seg=16, r2=0.16)
    m.cyl(0.165, 0.06, (0, 0.42, 0.3), "black_metal", seg=16) if False else None
    m.cyl(0.14, 0.05, (0, 1.65, 0.3), "black_metal", seg=16)
    m.cyl(0.14, 0.05, (0, 0.38, 0.3), "black_metal", seg=16)
    m.cyl(0.165, 0.03, (0, 1.0, 0.3), "crew_seam", seg=16)
    m.link((0, 1.65, 0.3), (0, 1.7, 0.3), 0.02, "chrome", 5) if False else None
    m.sphere(0.06, (0, 2.0, 0.28), "chrome", 6, 4) if False else None
    m.cyl(0.35, 0.07, (0, 0.085, -0.35), "hull_mid", seg=16, r2=0.33) if False else None
    for x in (-0.38, 0.38):
        for z in (-0.38, 0.38):
            m.cyl(0.025, 0.01, (x, 0.055, z), "chrome", seg=6)
    m.box((0.1, 0.5, 0.05), (0, 1.2, -0.28), "rubber", 0.012)
    m.box((0.22, 0.3, 0.02), (0, 0.5, 0.45), "hull_light") if False else None


@reg("gym", "rowing machine")
def _(m, rng):
    m.box((0.08, 0.06, 2.0), (0, 0.29, 0.0), "brushed_alu", 0.015)
    m.box((0.5, 0.05, 0.08), (0, 0.025, -0.9), "black_metal", 0.01)
    m.box((0.5, 0.05, 0.08), (0, 0.025, 0.85), "black_metal", 0.01)
    m.box((0.05, 0.28, 0.06), (0, 0.15, -0.9), "black_metal", 0.008)
    m.box((0.05, 0.28, 0.06), (0, 0.15, 0.85), "black_metal", 0.008)
    m.cyl(0.24, 0.16, (0, 0.5, -0.82), "hull_dark", axis="x", seg=18)
    m.cyl(0.2, 0.17, (0, 0.5, -0.82), "steel", axis="x", seg=16)
    for k in range(6):
        m.box((0.02, 0.4, 0.008), (0, 0.5, -0.82), "black_metal", rot=(k * 0.52, 0, 0)) if False else None
    m.box((0.16, 0.14, 0.08), (0, 0.85, -0.85), "hull_dark", 0.015) if False else None
    m.box((0.3, 0.16, 0.06), (0, 0.9, -0.88), "hull_dark", 0.015)
    m.screen((0.22, 0.1), (0, 0.9, -0.845), "vitals", bezel=0.01)
    m.link((0, 0.6, -0.85), (0, 0.85, -0.88), 0.025, "hull_mid", 8)
    m.link((0, 0.55, -0.85), (0.0, 0.5, -0.4), 0.004, "chrome", 4)
    m.box((0.3, 0.07, 0.03), (0, 0.55, -0.35), "black_metal", 0.008) if False else None
    m.box((0.4, 0.03, 0.03), (0, 0.55, -0.4), "chrome") if False else None
    m.cyl(0.015, 0.4, (0, 0.55, -0.4), "chrome", axis="x", seg=8)
    m.box((0.26, 0.09, 0.28), (0, 0.4, 0.15), "leather_black", 0.03)
    for s in (-1, 1):
        m.box((0.02, 0.03, 0.06), (s * 0.05, 0.36, 0.15), "steel", 0.004) if False else None
        m.box((0.13, 0.03, 0.4), (s * 0.2, 0.34, -0.55), "hull_mid", 0.008)
        m.box((0.1, 0.16, 0.03), (s * 0.2, 0.42, -0.4), "black_metal", 0.008, rot=(-0.3, 0, 0))
        m.box((0.03, 0.03, 0.03), (s * 0.05, 0.3, 0.15), "black_metal") if False else None
    m.box((0.28, 0.03, 0.14), (0, 0.33, 0.15), "steel", 0.005)


@reg("gym", "yoga mat rack")
def _(m, rng):
    m.box((1.4, 0.05, 0.45), (0, 0.025, 0), "wood_dark", 0.01)
    for s in (-1, 1):
        m.box((0.05, 1.0, 0.4), (s * 0.68, 0.5, 0), "wood_light", 0.01)
    m.box((1.4, 0.05, 0.45), (0, 1.02, 0), "wood_dark", 0.01)
    m.box((1.3, 0.04, 0.4), (0, 0.5, 0), "wood_light", 0.006)
    cols = ["paint_teal", "paint_red", "crew_plum", "paint_orange", "paint_blue", "paint_green"]
    for k in range(6):
        x = -0.55 + 0.22 * k
        yy = 0.15 if k < 3 else 0.65
        if k >= 3:
            x = -0.4 + 0.4 * (k - 3)
        else:
            x = -0.4 + 0.4 * k
        m.cyl(0.075, 0.42, (x, 0.05 + 0.075 + (0.0 if k < 3 else 0.5), 0.0), cols[k], axis="z", seg=12)
        m.cyl(0.078, 0.02, (x, 0.125 + (0.0 if k < 3 else 0.5), 0.17), "crew_seam", axis="z", seg=12)
    m.box((1.3, 0.1, 0.02), (0, 0.9, 0.2), "hull_dark") if False else None
    m.box((0.35, 0.16, 0.012), (0, 0.9, 0.226), "paint_white") if False else None
    m.box((0.3, 0.08, 0.012), (0, 0.95, 0.205), "brass")
    for s in (-1, 1):
        m.cyl(0.03, 0.03, (s * 0.6, 0.03, 0.18), "rubber", seg=6) if False else None


@reg("gym", "dumbbell rack")
def _(m, rng):
    for s in (-1, 1):
        m.box((0.06, 0.8, 0.5), (s * 0.7, 0.4, 0), "black_metal", 0.01)
    m.box((1.4, 0.06, 0.5), (0, 0.02, 0), "black_metal", 0.008) if False else None
    for k, y in enumerate((0.3, 0.6)):
        m.box((1.4, 0.04, 0.5), (0, y, 0.0), "gunmetal", 0.008)
        m.box((1.4, 0.06, 0.03), (0, y + 0.03, 0.245), "black_metal") if False else None
        m.box((1.4, 0.06, 0.03), (0, y + 0.03, -0.24), "black_metal")
    m.box((1.4, 0.04, 0.5), (0, 0.06, 0), "gunmetal", 0.008)
    m.box((1.4, 0.5, 0.03), (0, 0.4, -0.235), "hull_dark", 0.008) if False else None
    for k in range(6):
        x = -0.55 + 0.22 * k
        r = 0.05 + 0.0125 * k
        for j, y in enumerate((0.32, 0.62)):
            m.cyl(0.02, 0.16, (x, y + 0.055, 0.02 - 0.04 * j), "chrome", axis="z", seg=8) if False else None
        m.cyl(0.018, 0.2, (x, 0.65 + 0.03, 0.05), "chrome", axis="z", seg=8)
        m.cyl(r + 0.03, 0.07, (x, 0.65 + 0.03 + r * 0.0 + 0.0, 0.16), "black_metal", axis="z", seg=10) if False else None
        m.cyl(r, 0.06, (x, 0.65 + 0.02 + r, 0.14), "black_metal", axis="z", seg=10)
        m.cyl(r, 0.06, (x, 0.65 + 0.02 + r, -0.04), "black_metal", axis="z", seg=10)
        m.cyl(0.014, 0.2, (x, 0.65 + 0.02 + r, 0.05), "chrome", axis="z", seg=6)
        m.cyl(r, 0.06, (x, 0.35 + 0.02 + r, 0.14), "hull_dark", axis="z", seg=10)
        m.cyl(r, 0.06, (x, 0.35 + 0.02 + r, -0.04), "hull_dark", axis="z", seg=10)
        m.cyl(0.014, 0.2, (x, 0.35 + 0.02 + r, 0.05), "chrome", axis="z", seg=6)
        m.box((0.03, 0.03, 0.005), (x, 0.65, 0.26), "hazard_yellow") if False else None
    m.box((1.4, 0.3, 0.02), (0, 0.15, 0.245), "hull_dark") if False else None
    for s in (-1, 1):
        m.cyl(0.03, 0.03, (s * 0.7, 0.015, 0.2), "rubber", seg=6) if False else None


make("gym", [(["treadmill", "exercise bike", "weight bench and rack", "punching bag", "rowing machine", "yoga mat rack",
               "dumbbell rack"], "floor", ["crew", "gym"], True, None)])
