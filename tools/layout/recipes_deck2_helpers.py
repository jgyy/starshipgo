"""Small helpers for the Deck 2 recipes: explicit model ids, failure reporting, wall sequences."""
import sys

from dressing import *   # noqa: F401,F403  (re-exported to recipes_deck2)


STRICT = []   # (room, model) of every placement that did not fit - printed so nothing fails silently


def M(B, mid):
    return B.cat.models[mid]


def _miss(R, what, where):
    STRICT.append((R.id, what))
    print("  [miss] %s: %s %s" % (R.id, what, where), file=sys.stderr)


def put(R, B, mid, x, z, yaw=0.0, margin=0.0, quiet=False, **kw):
    """Place a floor model with its footprint centre at (x, z)."""
    p = R.place(M(B, mid), x, z, yaw, margin=margin, **kw)
    if p is None and not quiet:
        _miss(R, mid, "at (%.2f, %.2f) yaw %g" % (x, z, yaw))
    return p


def wall(R, B, side, mid, along, gap=0.04, quiet=False, **kw):
    """Floor item with its back to a wall."""
    p = R.against_wall(side, M(B, mid), along, gap=gap, **kw)
    if p is None and not quiet:
        _miss(R, mid, "on %s at %.2f" % (side, along))
    return p


def wi(R, B, side, mid, along, y=None, quiet=False, check=True):
    """Wall-mounted model."""
    p = R.wall_item(side, M(B, mid), along, y=y, check=check)
    if p is None and not quiet:
        _miss(R, mid, "wall item on %s at %.2f" % (side, along))
    return p


def top(R, B, host, mids, dx=0.0, dz=0.0, step=0.0, quiet=False):
    """Stand small table-mount models on a host, spreading them along its local x by `step`."""
    out = []
    if host is None:
        return out
    if isinstance(mids, str):
        mids = [mids]
    for i, mid in enumerate(mids):
        off = step * (i - (len(mids) - 1) / 2.0)
        if abs(round(host["yaw"]) % 180) == 90:          # host turned a quarter turn: its local x runs along world z
            p = R.on_top(host, M(B, mid), dx=dz, dz=dx + off)
        else:
            p = R.on_top(host, M(B, mid), dx=dx + off, dz=dz)
        if p is None and not quiet:
            _miss(R, mid, "on top of %s" % host["m"])
        out.append(p)
    return out


def seq(R, B, side, mids, start, gap=0.05, direction=1, quiet=False, **kw):
    """Row of floor models against a wall; `start` is the first model's near edge along the wall."""
    pos = start
    out = []
    for mid in mids:
        w = M(B, mid)["size"][0]
        c = pos + direction * w / 2
        out.append(wall(R, B, side, mid, c, quiet=quiet, **kw))
        pos += direction * (w + gap)
    return out


def ext_lights(R, B, spacing=4.2, energy=1.5, **kw):
    R.light_grid(cats=("ceilinglight",), spacing=spacing, energy=energy, color="#fff0dd",
                 pred=lambda m: m["mount"] == "ceiling" and m["size"][1] < 0.3 and m["size"][0] < 1.7 and m["size"][2] < 1.7, **kw)


def extinguisher(R, B, side, along, y=1.1):
    return wi(R, B, side, "safety_fire_extinguisher", along, y=y)


def dsign(R, B, side, c, label, y=2.75):
    m = B.cat.pick("sign", label=label, pred=lambda s: s["mount"] == "wall")
    if m is None:
        return None
    p = R.wall_item(side, m, c, y=y, check=False)
    return p


def first(R, B, mid, spots, quiet=False, **kw):
    """Try (x, z, yaw) candidates in order and keep the first that fits (a designer's 'nudge')."""
    for (x, z, yaw) in spots:
        p = R.place(M(B, mid), x, z, yaw, **kw)
        if p is not None:
            return p
    if not quiet:
        _miss(R, mid, "no spot among %d candidates" % len(spots))
    return None


def wall_first(R, B, side, mid, alongs, gap=0.04, quiet=False, **kw):
    """Try several positions along a wall and keep the first that fits."""
    for a in alongs:
        p = R.against_wall(side, M(B, mid), a, gap=gap, **kw)
        if p is not None:
            return p
    if not quiet:
        _miss(R, mid, "no spot on %s among %s" % (side, alongs))
    return None


def top_try(R, B, host, mid, offsets):
    """Stand one table-mount model on a host, trying several (dx, dz) offsets."""
    if host is None:
        return None
    for dx, dz in offsets:
        p = R.on_top(host, M(B, mid), dx=dx, dz=dz)
        if p is not None:
            return p
    _miss(R, mid, "on top of %s" % host["m"])
    return None
