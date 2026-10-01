"""Exterior fittings of the starship: warp nacelles on swept pylons, the deflector dish, sensor masts, the stern
engine cluster and the ventral keel fin.  They are bolted onto the outer skin (see tools/layout/hull.py `skin`)
and listed in ship.json["exterior"] by tools/layout/generate_ship.py.

Like the stair / fascia assets they are *not* part of the component catalogue; blender/build_arch.py builds them.
Authoring frame = glTF frame (+Y up, +Z front, metres).  Models that sit on the ship use the ship's axes: the bow is
-Z, so the nacelles are modelled nose first towards -Z.
"""
import math

from . import kit

kit.register_material("ext_glow_blue", "#58b4ff", 0, 0.35, emission=4.5)
kit.register_material("ext_glow_violet", "#a46bff", 0, 0.35, emission=4.0)
kit.register_material("ext_glow_white", "#e8f2ff", 0, 0.35, emission=5.0)
kit.register_material("ext_glow_amber", "#ffb04a", 0, 0.35, emission=3.5)
kit.register_material("ext_nav_red", "#ff2a2a", 0, 0.35, emission=6.0)
kit.register_material("ext_nav_green", "#2aff6a", 0, 0.35, emission=6.0)
kit.register_material("ext_dark", "#1a1d23", 0.7, 0.4)
kit.register_material("ext_panel", "#9aa3b2", 0.8, 0.45)


def _pylon(m, side):
    """Swept strut from the hull (x = 0 attach line) out to the nacelle; `side` +1 starboard / -1 port."""
    pts = [(0.0, -7.5), (10.5, -4.0), (10.5, 7.0), (0.0, 11.0)]
    m.prism([(side * x, z) for x, z in pts][::side], 0.95, (0, -1.15, 0), "arch_hull_plate", plane="xz", bevel=0.04)
    m.prism([(side * x, z) for x, z in [(1.0, -5.6), (10.3, -3.0), (10.3, -2.4), (1.0, -5.0)]][::side], 0.05, (0, -0.2, 0),
            "ext_glow_blue", plane="xz")


def _nacelle_at(m, x, y, z, length=46.0, radius=2.7):
    """Nacelle built around (x, y, z) instead of the origin (kit primitives take a position)."""
    half = length / 2
    m.sphere(1.0, (x, y, z), "arch_hull_plate", seg=32, ring=16, scale=(radius, radius * 0.94, half))
    for dz in (-18, -14, -10, -6, -2, 2, 6, 10, 14, 18):
        r = radius * 0.94 * math.sqrt(max(0.02, 1 - (dz / half) ** 2)) + 0.04
        m.cyl(r, 0.34, (x, y, z + dz), "arch_steel", axis="z", seg=28)
        m.cyl(r + 0.012, 0.05, (x, y, z + dz + 0.18), "ext_glow_blue", axis="z", seg=28)
    m.cyl(0.95, 0.9, (x, y, z - half + 1.05), "ext_dark", axis="z", seg=24, r2=0.45)
    m.sphere(0.46, (x, y, z - half + 0.62), "ext_glow_blue", seg=18, ring=9, scale=(1, 1, 1.35))
    for sx in (-1, 1):
        m.box((0.08, 0.2, 28.0), (x + sx * radius * 0.985, y + 0.2, z + 0.5), "ext_glow_blue")
        m.box((0.08, 0.12, 18.0), (x + sx * radius * 0.93, y - 0.7, z + 2.0), "ext_glow_white")
    spine = [(-13.0, radius * 0.9), (-4.0, radius * 1.55), (8.0, radius * 1.55), (17.0, radius * 0.7), (17.0, radius * 0.4),
             (-13.0, radius * 0.4)]
    m.prism([(z + dz, y + dy) for dz, dy in spine], 0.16, (x - 0.08, 0, 0), "arch_hull_plate", plane="zy")
    m.cyl(1.25, 1.2, (x, y, z + half - 0.6), "arch_dark_panel", axis="z", seg=28, r2=1.55)
    m.cyl(1.12, 0.1, (x, y, z + half + 0.02), "ext_dark", axis="z", seg=28)
    m.sphere(1.0, (x, y, z + half + 0.12), "ext_glow_violet", seg=24, ring=10, scale=(1.0, 1.0, 0.18))


def arch_nacelle_starboard(m):
    _pylon(m, 1)
    _nacelle_at(m, 13.0, -0.6, 2.0)
    m.sphere(0.16, (13.0 + 2.7, -0.6, -20.5), "ext_nav_green", seg=10, ring=6)
    return m


def arch_nacelle_port(m):
    _pylon(m, -1)
    _nacelle_at(m, -13.0, -0.6, 2.0)
    m.sphere(0.16, (-13.0 - 2.7, -0.6, -20.5), "ext_nav_red", seg=10, ring=6)
    return m


def arch_deflector(m):
    """Forward deflector: a faired housing with a concave blue-white dish.  Faces -Z (the bow); origin on the keel line."""
    m.cyl(3.4, 1.4, (0, 0, 0), "arch_hull_plate", axis="z", seg=36, r2=2.7)
    m.cyl(2.7, 0.3, (0, 0, -0.78), "arch_steel", axis="z", seg=36)
    m.cyl(2.45, 0.12, (0, 0, -0.97), "ext_dark", axis="z", seg=36)
    # concave dish: stacked rings of falling radius give a stepped bowl, the core glows
    for i in range(6):
        r = 2.4 * (1 - i / 6.0)
        m.cyl(max(r, 0.2), 0.05, (0, 0, -0.9 + 0.09 * i), "ext_glow_blue" if i % 2 == 0 else "ext_glow_white", axis="z", seg=36)
    m.cyl(0.18, 0.9, (0, 0, -1.4), "ext_panel", axis="z", seg=12, r2=0.05)
    m.torus(2.95, 0.07, (0, 0, -0.5), "ext_glow_blue", axis="z", seg=48, tseg=6)
    return m


def arch_mast(m):
    """Dorsal sensor mast: lattice spine, three dishes, strobe and aircraft-style beacons.  Origin at the base."""
    m.cyl(0.55, 0.6, (0, 0.3, 0), "arch_steel", axis="y", seg=16, r2=0.45)
    m.cyl(0.22, 8.5, (0, 4.6, 0), "ext_panel", axis="y", seg=12, r2=0.14)
    for y, r in ((2.2, 1.0), (4.6, 1.5), (6.8, 0.9)):
        m.sphere(1.0, (0, y, 0.2), "plastic_white", seg=18, ring=8, scale=(r, 0.18, r))
        m.cyl(0.05, 0.9, (0, y + 0.1, 0.6), "ext_panel", axis="z", seg=6)
        m.sphere(0.07, (0, y + 0.1, 1.0), "ext_glow_white", seg=8, ring=4)
    for sx in (-1, 1):
        m.box((2.4, 0.06, 0.06), (sx * 1.2, 7.8, 0), "ext_panel")
        m.sphere(0.1, (sx * 2.4, 7.8, 0), "ext_nav_red" if sx < 0 else "ext_nav_green", seg=8, ring=4)
    m.sphere(0.13, (0, 9.0, 0), "ext_glow_white", seg=8, ring=4)
    return m


def arch_engine_cluster(m):
    """Stern impulse engines: a faired housing with three big bells.  The bells point +Z; origin at the housing front."""
    m.box((14.0, 3.6, 3.0), (0, 0, 1.5), "arch_hull_plate", bevel=0.18)
    m.box((14.4, 0.25, 3.1), (0, 1.6, 1.5), "arch_steel", bevel=0.04)
    for x in (-4.4, 0.0, 4.4):
        m.cyl(1.55, 1.8, (x, 0, 3.8), "arch_dark_panel", axis="z", seg=28, r2=2.15)
        m.cyl(2.0, 0.12, (x, 0, 4.72), "ext_dark", axis="z", seg=28)
        m.sphere(1.0, (x, 0, 4.78), "ext_glow_white", seg=22, ring=9, scale=(1.55, 1.55, 0.2))
        m.torus(2.15, 0.07, (x, 0, 4.7), "ext_glow_violet", axis="z", seg=36, tseg=6)
    for sx in (-1, 1):
        m.box((0.3, 2.2, 2.2), (sx * 6.9, 0.1, 2.6), "hazard_yellow", bevel=0.03)
    return m


def arch_keel_fin(m):
    """Ventral fin / sensor blade under the keel.  Origin on top of the blade; it hangs down 4.4 m."""
    pts = [(-9.0, 0.0), (9.0, 0.0), (6.0, -2.4), (-2.0, -4.4), (-8.0, -3.2)]
    m.prism(pts, 0.34, (-0.17, 0, 0), "arch_hull_plate", plane="zy", bevel=0.03)
    m.box((0.38, 0.14, 12.0), (0, -0.4, 0.0), "ext_glow_blue")
    m.box((0.4, 0.5, 1.2), (0, -4.1, -2.6), "ext_dark")
    return m


EXTERIOR_MODELS = {
    "arch_nacelle_starboard": arch_nacelle_starboard,
    "arch_nacelle_port": arch_nacelle_port,
    "arch_deflector": arch_deflector,
    "arch_mast": arch_mast,
    "arch_engine_cluster": arch_engine_cluster,
    "arch_keel_fin": arch_keel_fin,
}
