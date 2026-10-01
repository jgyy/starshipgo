"""Small placement helpers shared by the deck-3 recipes (explicit, deterministic, no randomness)."""
import os
import sys

from dressing import *   # noqa: F401,F403

DEBUG = bool(os.environ.get("RECIPE_DEBUG"))


def mm(B, mid):
    """Catalog model by exact id."""
    return B.cat.models[mid]


def _log(R, what, where):
    if DEBUG:
        print("  [%s] MISS %s @ %s" % (R.id, what, where), file=sys.stderr)


def put(R, B, mid, x, z, yaw=0.0, y=None, margin=0.0):
    """Place model `mid` with footprint centre (x, z); logs a miss (debug) and returns the prop or None."""
    m = mm(B, mid)
    p = R.place(m, x, z, yaw, y=y, margin=margin)
    if p is None:
        _log(R, mid, (round(x, 2), round(z, 2), yaw))
    return p


def wall_row(R, B, side, items, start, dirn=1, gap=0.06, item_gap=0.04):
    """Fill a wall with items one after another from `start` (absolute x / z, or distance on a diagonal).

    `items`: model ids, a float (gap in metres), or (id, y) for wall mounted models.  Returns the placed props
    (None where an item did not fit)."""
    cur, out = start, []
    for it in items:
        if isinstance(it, (int, float)):
            cur += dirn * it
            continue
        y = None
        if isinstance(it, tuple):
            it, y = it
        m = mm(B, it)
        w = m["size"][0]
        c = cur + dirn * w / 2
        if m["mount"] == "wall":
            p = R.wall_item(side, m, c, y=y)
        else:
            p = R.against_wall(side, m, c, gap=item_gap)
        if p is None:
            _log(R, it, (side, round(c, 2)))
        out.append(p)
        cur += dirn * (w + gap)
    return out


def line_x(R, B, ids, x, z, yaw=0.0, gap=0.06, dirn=1):
    """Items in a row along X starting at x (edge), footprint centres on z.  yaw 0/180 -> width along X."""
    out, cur = [], x
    for it in ids:
        if isinstance(it, (int, float)):
            cur += dirn * it
            continue
        m = mm(B, it)
        w = m["size"][0] if abs(yaw) % 180 < 1 else m["size"][2]
        p = put(R, B, it, cur + dirn * w / 2, z, yaw)
        out.append(p)
        cur += dirn * (w + gap)
    return out


def line_z(R, B, ids, x, z, yaw=90.0, gap=0.06, dirn=1):
    """Items in a row along Z starting at z (edge), footprint centres on x.  yaw +-90 -> width along Z."""
    out, cur = [], z
    for it in ids:
        if isinstance(it, (int, float)):
            cur += dirn * it
            continue
        m = mm(B, it)
        w = m["size"][0] if abs(yaw) % 180 > 89 else m["size"][2]
        p = put(R, B, it, x, cur + dirn * w / 2, yaw)
        out.append(p)
        cur += dirn * (w + gap)
    return out


def ceil_run(R, B, ids, x0, z0, axis="x", gap=0.03):
    """Ceiling services (pipes, trays, ducts) laid end to end from (x0, z0) along `axis`; pieces that do not fit are skipped."""
    cur = x0 if axis == "x" else z0
    out = []
    for it in ids:
        m = mm(B, it)
        assert m["mount"] == "ceiling", it
        w = m["size"][0]
        if axis == "x":
            p = R.place(m, cur + w / 2, z0, 0.0, y=R.y + R.h)
        else:
            p = R.place(m, x0, cur + w / 2, 90.0, y=R.y + R.h)
        if p is None:
            _log(R, it, (axis, round(cur, 2)))
        else:
            out.append(p)
        cur += w + gap
    return out


def wall_y(R, B, side, mid, along, y=None, check=True, bottom=None):
    """Wall item at origin height `y`, or with its lowest point at `bottom` metres above the floor."""
    m = mm(B, mid)
    if bottom is not None:
        y = bottom - m["bounds_min"][1]
    p = R.wall_item(side, m, along, y=y, check=check)
    if p is None:
        _log(R, mid, (side, round(along, 2)))
    return p


def lights(R, spacing=4.2, energy=1.6, color="#fff0dd", ids=None, **kw):
    ids = ids or ("ceilinglight_panel_troffer_0_6x1_2", "ceilinglight_square_panel_1x1", "ceilinglight_flush_dome",
                  "ceilinglight_linear_fixture_1_2")
    R.light_grid(cats=("ceilinglight",), spacing=spacing, energy=energy, color=color,
                 pred=lambda m: m["id"] in ids, **kw)


def tops(R, B, host, ids, offs):
    """Stand small table-mount items on a host; offs = [(dx, dz), ...]."""
    out = []
    if host is None:
        return out
    for it, (dx, dz) in zip(ids, offs):
        wx, wz = rot(dx, dz, host["yaw"])          # offsets are host-local: +x right, +z towards the front
        p = R.on_top(host, mm(B, it), wx, wz)
        if p is None:
            _log(R, it, "on_top")
        out.append(p)
    return out


def seat_for(R, B, host, mid="seat_ops_chair", gap=0.35):
    """Seat in front of a console / desk, facing it."""
    if host is None:
        return None
    m = mm(B, mid)
    hm = host["_m"]
    lo, hi = hm["bounds_min"], hm["bounds_max"]
    fx, fz = (lo[0] + hi[0]) / 2, hi[2] + gap + m["size"][2] / 2
    ox, oz = rot(fx, fz, host["yaw"])
    p = R.place(m, host["pos"][0] + ox, host["pos"][2] + oz, host["yaw"] + 180.0)
    if p is None:
        _log(R, mid, "seat")
    return p


def fe(R, B, side, along, y=1.1):
    return wall_y(R, B, side, "safety_fire_extinguisher", along, y)


def aw(R, B, side, mid, along, gap=0.04, yaw_extra=0.0):
    """Floor item against a wall, centred at `along`; logs a miss."""
    p = R.against_wall(side, mm(B, mid), along, gap=gap, yaw_extra=yaw_extra)
    if p is None:
        _log(R, mid, (side, round(along, 2)))
    return p


def wall_run(R, B, side, mid, start, end, y, gap=0.02):
    """Repeat a wall mounted model (duct, pipe, tray) along a wall between two coordinates at height y."""
    m = mm(B, mid)
    w = m["size"][0]
    out, cur = [], start
    while cur + w <= end + 1e-6:
        p = R.wall_item(side, m, cur + w / 2, y=y)
        if p is None:
            cur += 0.25
            continue
        out.append(p)
        cur += w + gap
    return out
