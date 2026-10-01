"""Outer-skin geometry in drawing space: cross-sections on a cut plane, silhouettes, exterior fittings.

Everything here works in the (h, y) space of sectionview.Cut (h = z for a plane x = c, h = -x for a plane z = c)."""
from shipmodel import line_interval


def _chains(rows):
    """rows: [(y, h_lo, h_hi)] bottom to top -> closed polygon of (h, y) (left side up, right side down)."""
    left = [(a, y) for y, a, b in rows]
    right = [(b, y) for y, a, b in reversed(rows)]
    poly = left + right
    out = []
    for p in poly:                            # drop repeated points (tips where the interval collapses)
        if not out or abs(p[0] - out[-1][0]) > 1e-6 or abs(p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if len(out) > 1 and abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def _edge_row(skin, cut, y_in, iv_in, y_out):
    """Bisect between a ring that the plane crosses (y_in) and a neighbour it misses (y_out): the height where it stops."""
    a, b = y_in, y_out
    iv = iv_in
    for _ in range(26):
        m = (a + b) / 2
        pl = skin.plan(m)
        q = cut.iv(pl) if pl else None
        if q:
            a, iv = m, q
        else:
            b = m
    return (a, iv[0], iv[1])


def skin_cut(skin, cut):
    """Cross-section of the skin on the plane: a list of closed polygons of (h, y)."""
    rows = [(y, cut.iv(ring)) for ring, y in zip(skin.pts, skin.ys)]
    polys, run = [], []
    for i, (y, iv) in enumerate(rows):
        if iv is not None:
            if not run and i > 0:                                  # the plane starts to cross the skin between ring i-1 and i
                run.append(_edge_row(skin, cut, y, iv, rows[i - 1][0]))
            run.append((y, iv[0], iv[1]))
        else:
            if run:
                run.append(_edge_row(skin, cut, rows[i - 1][0], rows[i - 1][1], y))
                polys.append(_chains(run))
                run = []
    if run:
        polys.append(_chains(run))
    return [p for p in polys if len(p) >= 3]


def skin_beyond(skin, cut):
    """Outline (h, y) of everything of the skin behind the plane (envelope of the points with d >= 0)."""
    rows = []
    for ring, y in zip(skin.pts, skin.ys):
        hs = [h for h, d in (cut.T(x, z) for x, z in ring) if d >= -1e-9]
        if hs:
            rows.append((y, min(hs), max(hs)))
    return _chains(rows) if len(rows) > 1 else []


def skin_extreme(skin, cut):
    """Outline (h, y) of the largest section over the whole length: per ring, extreme h over all points."""
    rows = []
    for ring, y in zip(skin.pts, skin.ys):
        hs = [cut.T(x, z)[0] for x, z in ring]
        rows.append((y, min(hs), max(hs)))
    return _chains(rows)


def draw_fittings_section(sh, sv, cut, ship, labels=True):
    """Exterior fittings on a section: cut ones hatched, those behind the plane dashed, those in front omitted."""
    for f in ship.fittings:
        lo, hi = f.depth_range(cut.T)
        if hi < 1e-9:
            continue
        if hi > 1e-9:
            bp = f.beyond_poly(cut.T)
            if bp:
                sh.poly([sv.xy(h, y) for h, y in bp], "hid")
        if lo < -1e-9:
            cp = f.cut_poly(cut.T)
            if cp:
                pts = [sv.xy(h, y) for h, y in cp]
                sh.poly(pts, "m", "#cdd5e0")
                if labels:
                    x = sum(p[0] for p in pts) / len(pts)
                    y = min(p[1] for p in pts) - 1.2
                    sh.text(x, y, f.label.upper(), 1.5, "middle", bold=True, halo=True)


def ext_window_quads(ship, side=1):
    """Exterior window panels as 3D quads (c, u, v, w, h, kind) on the starboard (side=1) or port (-1) side."""
    out = []
    for w in ship.ext_windows:
        if w["kind"] != "mouth" and w["c"][0] * side <= 0:
            continue
        c, u, v = w["c"], w["u"], w["v"]
        hw, hh = w["w"] / 2, w["h"] / 2
        corners = []
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corners.append(tuple(c[i] + u[i] * hw * a + v[i] * hh * b for i in range(3)))
        out.append((corners, w["kind"], w["room"]))
    return out


def half_breadth(poly, z):
    iv = line_interval(poly, 1, z)
    return None if iv is None else max(abs(iv[0]), abs(iv[1]))
