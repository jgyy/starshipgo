"""Small helpers shared by the deck 1 recipes."""
import sys
from dressing import yaw_to


def need(p, what, R=None):
    """Signature items must fit: report loudly when they do not."""
    if p is None:
        print("  !! %s: could not place %s" % (R.id if R else "?", what), file=sys.stderr)
    return p


def M(R, cat, label=None, pred=None):
    return R.cat.pick(cat, label=label, pred=pred)


def put(R, cat, label, x, z, face=None, yaw=None, what=None, pred=None):
    """Place the named model with its front toward point `face` (or with explicit yaw)."""
    m = R.cat.pick(cat, label=label, pred=pred)
    if m is None:
        return None
    if yaw is None:
        yaw = yaw_to(x, z, face[0], face[1]) if face else 0.0
    return need(R.place(m, x, z, yaw), what or m["id"], R)


def wall(R, side, cat, label, along, y=None, what=None, pred=None):
    m = R.cat.pick(cat, label=label, pred=pred)
    if m is None:
        return None
    return need(R.wall_item(side, m, along, y=y), what or m["id"], R)


def floor_wall(R, side, cat, label, along, what=None, pred=None, **kw):
    m = R.cat.pick(cat, label=label, pred=pred)
    if m is None:
        return None
    return need(R.against_wall(side, m, along, **kw), what or m["id"], R)


def tops(R, host, cat, labels, dxs=None):
    """Put named table-mount models on a host (labels list); offsets spread along the host width."""
    out = []
    if host is None:
        return out
    n = len(labels)
    fp = host["_fp"]
    w = (fp[2] - fp[0]) if host["yaw"] % 180 < 1 else (fp[3] - fp[1])
    for i, lab in enumerate(labels):
        if isinstance(lab, tuple):
            c, lb, dx, dz = lab
        else:
            c, lb = cat, lab
            dx, dz = ((i + 0.5) / n - 0.5) * w * 0.7, 0.0
        m = R.cat.pick(c, label=lb, pred=lambda q: q["mount"] == "table")
        if m is None:
            continue
        # offsets are given in host-local frame (x to the right of the host, z toward its front)
        import math
        t = math.radians(host["yaw"])
        wx, wz = dx * math.cos(t) + dz * math.sin(t), -dx * math.sin(t) + dz * math.cos(t)
        p = R.on_top(host, m, dx=wx, dz=wz)
        if p:
            out.append(p)
    return out
