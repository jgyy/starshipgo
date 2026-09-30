"""Plan-view drawing routines."""
import math

from shipmodel import WALL_T, rect_poly
from svgkit import fmt, text_w, trunc


class PV:
    """Plan view: model (x, z) metres -> paper mm; bow (-z) is up."""

    def __init__(self, s, ox, oy, x0, z0):
        self.s, self.ox, self.oy, self.x0, self.z0 = s, ox, oy, x0, z0

    def xy(self, x, z):
        return (self.ox + (x - self.x0) * self.s, self.oy + (z - self.z0) * self.s)

    def pts(self, poly):
        return [self.xy(x, z) for x, z in poly]


def blend(hexcol, k=0.55, to=(255, 255, 255)):
    h = hexcol.lstrip("#")
    try:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        r, g, b = 221, 221, 221
    return "#%02x%02x%02x" % (int(r + (to[0] - r) * k), int(g + (to[1] - g) * k), int(b + (to[2] - b) * k))


def ring_path(pv, outer, inner):
    d = ""
    for poly in (outer, inner):
        if not poly:
            continue
        pp = pv.pts(poly)
        d += "M" + " L".join("%s %s" % (fmt(x), fmt(y)) for x, y in pp) + "Z "
    return d


def draw_floor(sh, pv, room, fill=None, k=0.6):
    sh.poly(pv.pts(room.poly), "none", fill or blend(room.tint, k))


def draw_walls(sh, pv, room):
    sh.path(ring_path(pv, room.poly, room.inner), "none", "#1c1c1c", rule="evenodd")


def link_of(room, o):
    for lk in room.links:
        if lk["side"] == o["side"] and abs(lk["c"] - o["c"]) < 1e-3:
            return lk
    return None


def draw_openings(sh, pv, room, detail=True, marks=False):
    ship = room.ship
    pv.s
    for o in room.openings:
        r = room.opening_seg(o)
        if r is None:
            continue
        (p0, p1), e = r
        nx, nz = e["n"]
        T = WALL_T
        q = [p0, p1, (p1[0] + nx * T, p1[1] + nz * T), (p0[0] + nx * T, p0[1] + nz * T)]
        sh.poly(pv.pts(q), "none", "#ffffff")
        a0, a1 = pv.xy(*p0), pv.xy(*p1)
        b0, b1 = pv.xy(p0[0] + nx * T, p0[1] + nz * T), pv.xy(p1[0] + nx * T, p1[1] + nz * T)
        kind = o["kind"]
        lk = link_of(room, o)
        lkind = lk["kind"] if lk else kind
        if kind == "window":
            sh.line(*a0, *b0, "n")
            sh.line(*a1, *b1, "n")
            for t in (0.0, 0.5, 1.0):
                sh.line(a0[0] + (b0[0] - a0[0]) * t, a0[1] + (b0[1] - a0[1]) * t, a1[0] + (b1[0] - a1[0]) * t,
                        a1[1] + (b1[1] - a1[1]) * t, "f" if t == 0.5 else "n")
            if marks:
                w = ship.win_mark.get((room.id, o["side"], round(o["c"], 2)))
                if w:
                    mx, mz = (p0[0] + p1[0]) / 2 + nx * 0.8, (p0[1] + p1[1]) / 2 + nz * 0.8
                    sh.label(*pv.xy(mx, mz), w["mark"], 1.4, "middle", fill="#1d3c6e")
            continue
        # door / arch / open : jamb lines
        sh.line(*a0, *b0, "m")
        sh.line(*a1, *b1, "m")
        if lkind == "open":
            mid0 = ((a0[0] + b0[0]) / 2, (a0[1] + b0[1]) / 2)
            mid1 = ((a1[0] + b1[0]) / 2, (a1[1] + b1[1]) / 2)
            sh.line(*mid0, *mid1, "dsh")
        elif lkind == "portal":
            sh.line(*a0, *a1, "f")
            sh.line(*b0, *b1, "f")
            for pa, pb in ((a0, b0), (a1, b1)):
                sh.circ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, 0.45, "f", "#1c1c1c")
        else:
            # sliding door leaf, centred on the shared wall line: drawn by the lower-id room only
            other = lk["to"] if lk else None
            if other is None or room.id < other:
                ux, uz = e["u"]
                # leaf covers half of the opening, parked beside it; centre line of the combined wall is the room edge
                cx0, cz0 = p0
                (cx0 - nx * WALL_T / 2 + nx * 0.0, cz0 - nz * WALL_T / 2)
                t = 0.06
                w = o["w"]
                pts = [(p0[0] - nx * t, p0[1] - nz * t), (p0[0] + ux * w / 2 - nx * t, p0[1] + uz * w / 2 - nz * t),
                       (p0[0] + ux * w / 2 + nx * t, p0[1] + uz * w / 2 + nz * t), (p0[0] + nx * t, p0[1] + nz * t)]
                sh.poly(pv.pts(pts), "f", "#7a8594")
                sh.line(*pv.xy(p0[0] + ux * w / 2, p0[1] + uz * w / 2), *a1, "hid")
            if marks:
                d = ship.door_mark.get((room.id, o["side"], round(o["c"], 2)))
                if d and room.id == d["a"]:
                    mx, mz = (p0[0] + p1[0]) / 2 + nx * 0.9, (p0[1] + p1[1]) / 2 + nz * 0.9
                    sh.label(*pv.xy(mx, mz), d["mark"], 1.3, "middle", bold=True)


OUTLINE_ONLY = ("doorframe", "forcefield", "railing")


def draw_prop(sh, pv, cat, p, labels=False, lite=False):
    pts = pv.pts(p.corners)
    fill = cat.fill(p.m)
    if p.mount == "ceiling":
        sh.poly(pts, "dot")
        return
    if p.cat in OUTLINE_ONLY:
        sh.poly(pts, "m")
        return
    if p.mount == "wall":
        sh.poly(pts, "f", blend(fill, 0.0, (90, 90, 100)))
        return
    if p.mount == "table":
        sh.poly(pts, "f", blend(fill, 0.1), op=0.9)
    else:
        sh.poly(pts, "n", fill)
    if lite:
        return
    # front edge: heavier line + centre tick
    c0, c1 = pts[2], pts[3]          # local +z edge
    sh.line(*c0, *c1, "m")
    mx, my = (c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2
    cx, cy = pv.xy(p.cx, p.cz)
    L = math.hypot(mx - cx, my - cy)
    if L > 0.8:
        k = min(1.0, 1.2 / L)
        sh.line(mx, my, mx + (cx - mx) * k, my + (cy - my) * k, "f")


def prop_label(sh, pv, p):
    x0, z0, x1, z1 = p.bbox
    w = (x1 - x0) * pv.s
    h = (z1 - z0) * pv.s
    if p.mount == "wall" or p.mount == "ceiling":
        return
    size = 1.25
    if w < 7 or h < 3:
        return
    lab = trunc(p.label, w - 1, size)
    cx, cy = pv.xy(p.cx, p.cz)
    bb = (cx - text_w(lab, size) / 2, cy - size, cx + text_w(lab, size) / 2, cy + .3)
    if sh.box_free(bb, 0.1):
        sh.reserve(bb)
        sh.text(cx, cy + .3, lab, size, "middle", fill="#333")


def draw_props(sh, pv, room, cat, labels=False, lite=False):
    order = {"floor": 0, "table": 2, "wall": 3, "ceiling": 4}
    props = sorted(room.props, key=lambda p: (order.get(p.mount, 1), p.y0))
    for p in props:
        draw_prop(sh, pv, cat, p, labels, lite)
    if labels:
        for p in sorted(room.props, key=lambda q: -q.size[0] * q.size[2]):
            prop_label(sh, pv, p)


def draw_zones(sh, pv, room, labels=True):
    for z in room.zones:
        r = z["rect"]
        pts = pv.pts(rect_poly(r))
        sh.poly(pts, "red", "url(#hZone)")
        if labels:
            w = (r[2] - r[0]) * pv.s
            h = (r[3] - r[1]) * pv.s
            txt = "DOOR CLEAR" if z["kind"] == "door" else ("CLEAR: " + z.get("why", ""))
            if w > 14 and h > 3.5:
                # label at the side of the zone that is nearest the room centre (away from the wall)
                ccx, ccy = pv.xy(room.cx, room.cz)
                mids = [((pts[i][0] + pts[(i + 1) % 4][0]) / 2, (pts[i][1] + pts[(i + 1) % 4][1]) / 2) for i in range(4)]
                mx, my = min(mids, key=lambda q: (q[0] - ccx) ** 2 + (q[1] - ccy) ** 2)
                zx, zy = (pts[0][0] + pts[2][0]) / 2, (pts[0][1] + pts[2][1]) / 2
                L = math.hypot(zx - mx, zy - my) or 1
                tx, ty = mx + (zx - mx) / L * 1.6, my + (zy - my) / L * 1.6
                sh.text(tx, ty + .4, trunc(txt, w - 1, 1.2), 1.2, "middle", fill="#a04040", ital=True, halo=True)


def draw_holes(sh, pv, room, ceiling=True):
    for h in room.floor_holes:
        pts = pv.pts(rect_poly(h))
        sh.poly(pts, "dsh", "url(#hHole)")
    if ceiling:
        for h in room.ceiling_holes:
            pts = pv.pts(rect_poly(h))
            sh.poly(pts, "dot")


def draw_forcefields(sh, pv, room):
    for f in room.forcefields:
        x, y, z = f["pos"]
        half = f["size"][0] / 2
        yaw = math.radians(f.get("yaw", 0.0))
        dx, dz = math.cos(yaw) * half, -math.sin(yaw) * half
        a, b = pv.xy(x - dx, z - dz), pv.xy(x + dx, z + dz)
        sh.line(*a, *b, "cl")
        sh.text((a[0] + b[0]) / 2, a[1] - 1.0, "FORCE FIELD", 1.4, "middle", fill="#2060a0")


def draw_stairs(sh, pv, ship, deck, detail=True, only_side=None):
    """Stair flights as seen on the plan of `deck` (cut plane 1.2 m above the deck)."""
    ghosts, solids = [], []
    for st in ship.stairs:
        if only_side and st["id"] != only_side:
            continue
        runs, _ = ship.stair_geom(st["id"])
        for run in runs:
            if run["lo"] == deck:
                fa, fb = run["flights"]
                solids.append((fa, "UP", 0.6))
                ghosts.append(fb)
            elif run["hi"] == deck:
                fa, fb = run["flights"]
                solids.append((fb, "DN", 1.0))
                ghosts.append(fa)
    for f in ghosts:
        _flight_plan(sh, pv, f, "hid", None, 1.0, detail)
    for f, lab, frac in solids:
        _flight_plan(sh, pv, f, "f", lab, frac, detail)


def _flight_plan(sh, pv, f, cls, label, frac, detail):
    x0, z = f["x"], f["z"]
    d, n, t, w = f["dir"], f["n"], f["tread"], f["w"]
    L = t * (n - 1)
    za, zb = z - w / 2, z + w / 2
    pts = pv.pts([(x0, za), (x0 + d * L, za), (x0 + d * L, zb), (x0, zb)])
    if cls == "hid":
        sh.poly(pts, "hid")
        return
    sh.poly(pts, "n", "#ffffff", op=0.75)
    if detail:
        for k in range(n):
            xx = x0 + d * t * k
            if k / max(n - 1, 1) <= frac + 1e-9:
                sh.line(*pv.xy(xx, za), *pv.xy(xx, zb), "x")
            else:
                sh.line(*pv.xy(xx, za), *pv.xy(xx, zb), "gg")
    if frac < 1.0:
        xb = x0 + d * L * frac
        sh.break_line(*pv.xy(xb + d * 0.15, za), *pv.xy(xb - d * 0.15, zb))
    a = pv.xy(x0 + d * L * 0.05 if label == "UP" else x0 + d * L * 0.95, z)
    b = pv.xy(x0 + d * L * 0.85 if label == "UP" else x0 + d * L * 0.15, z)
    sh.arrow(a[0], a[1], b[0], b[1], "f", 1.3)
    if label and pv.s >= 3.5:
        sh.text(a[0], a[1] - 1.2, label, 1.7, "middle" if abs(a[0] - b[0]) > 6 else "middle", bold=True)
    if label and detail and pv.s >= 3.5:
        sh.circ(a[0], a[1], 0.5, "f", "#111")


def place_balloons(sh, pv, room, avoid=None, margin=7.0, r=3.3):
    """One balloon per BOM line, outside the room outline, with a leader to the nearest item of the line.
    Returns the number of slot rings used (0 = none)."""
    pts = pv.pts(room.poly)
    bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
    lines = []
    for ln in room.bom:
        ps = [pv.xy(p.cx, p.cz) for p in room.props if p.code == ln["code"]]
        if ps:
            lines.append((ln["code"], ps))
    slots = []
    step = 2 * r + 0.9
    for ring in range(0, 4):
        m = margin + ring * step
        x0, x1, y0, y1 = bx0 - m, bx1 + m, by0 - m, by1 + m
        nx = max(1, int((x1 - x0) / step))
        ny = max(1, int((y1 - y0) / step))
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            slots.append((ring, x, y0))
            slots.append((ring, x, y1))
        for j in range(1, ny):
            y = y0 + (y1 - y0) * j / ny
            slots.append((ring, x0, y))
            slots.append((ring, x1, y))
    used = []
    placed = []
    maxring = -1
    for code, ps in lines:
        best, bd = None, 1e18
        for (ring, x, y) in slots:
            if any((x - u[0]) ** 2 + (y - u[1]) ** 2 < (2 * r + 0.4) ** 2 for u in used):
                continue
            if avoid and any(x - r < a[2] and x + r > a[0] and y - r < a[3] and y + r > a[1] for a in avoid):
                continue
            tx, ty = min(ps, key=lambda q: (q[0] - x) ** 2 + (q[1] - y) ** 2)
            d = (x - tx) ** 2 + (y - ty) ** 2 + ring * 40.0
            if d < bd:
                best, bd = (ring, x, y, tx, ty), d
        if best is None:
            continue
        ring, x, y, tx, ty = best
        used.append((x, y))
        maxring = max(maxring, ring)
        placed.append((code, (x, y), (tx, ty)))
    for code, (x, y), (tx, ty) in placed:
        L = math.hypot(tx - x, ty - y) or 1
        sh.line(x + (tx - x) / L * r, y + (ty - y) / L * r, tx, ty, "x")
        sh.circ(tx, ty, 0.4, "none", "#b03030")
    for code, (x, y), _ in placed:
        sh.balloon(x, y, code, r)
        sh.reserve((x - r, y - r, x + r, y + r))
    return maxring + 1


def draw_dim_chains(sh, pv, room, off=13.0, ext=True):
    """Overall dimensions and door / window chains on the four sides of the room plan."""
    pts = pv.pts(room.poly)
    bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
    mm = lambda v: str(int(round(v * 1000)))
    # overall
    sh.dim_h(bx0, bx1, by0 - off - 5.5, mm(room.w), ext_y=by0 - 1.5)
    sh.dim_v(by0, by1, bx0 - off - 5.5, mm(room.dd), ext_x=bx0 - 1.5)
    for side in ("N", "S", "E", "W"):
        e = room.edge(side)
        if e is None:
            continue
        ops = sorted([o for o in room.openings if o["side"] == side], key=lambda o: o["c"])
        if not ops:
            continue
        if side in ("N", "S"):
            a, b = sorted((e["a"][0], e["b"][0]))
            cs = [a]
            for o in ops:
                cs += [o["c"] - o["w"] / 2, o["c"] + o["w"] / 2]
            cs.append(b)
            xs = [pv.xy(c, 0)[0] for c in cs]
            labels = [mm(cs[i + 1] - cs[i]) for i in range(len(cs) - 1)]
            y = (by0 - off) if side == "N" else (by1 + off)
            wall = pv.xy(0, e["a"][1])[1]
            sh.chain_h(xs, y, labels, ext_y=wall - (1.0 if side == "N" else -1.0))
        else:
            a, b = sorted((e["a"][1], e["b"][1]))
            cs = [a]
            for o in ops:
                cs += [o["c"] - o["w"] / 2, o["c"] + o["w"] / 2]
            cs.append(b)
            ys = [pv.xy(0, c)[1] for c in cs]
            labels = [mm(cs[i + 1] - cs[i]) for i in range(len(cs) - 1)]
            x = (bx0 - off) if side == "W" else (bx1 + off)
            wall = pv.xy(e["a"][0], 0)[0]
            sh.chain_v(ys, x, labels, ext_x=wall - (1.0 if side == "W" else -1.0))


def family_legend(sh, x, y, cat, props, cols=2, colw=38, maxn=24):
    """Legend of the categories present; returns bottom y."""
    cs = sorted({p.cat for p in props if p.mount != "ceiling" or True})
    sh.text(x, y, "FURNITURE FAMILIES", 1.9, bold=True)
    y += 2.2
    n = 0
    for c in cs[:maxn]:
        col, row = n % cols, n // cols
        xx, yy = x + col * colw, y + row * 3.4
        sh.rect(xx, yy, 4.2, 2.4, "n", cat.color.get(c, "#ddd"))
        sh.text(xx + 5.4, yy + 1.9, c, 1.6, maxw=colw - 7)
        n += 1
    if len(cs) > maxn:
        row = n // cols
        sh.text(x, y + row * 3.4 + 2, "+%d more" % (len(cs) - maxn), 1.5, ital=True)
        n += 1
    rows = (n + cols - 1) // cols
    return y + rows * 3.4 + 1
