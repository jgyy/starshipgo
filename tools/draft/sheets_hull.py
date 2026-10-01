"""Hull sheets: hull lines plan (G-04), profile (G-05), body plan and principal particulars."""
import math

from shipmodel import SLAB_T, STATION_M, line_interval, poly_area
from sectionview import SV, Cut, lv
from hullview import skin_cut, skin_extreme, ext_window_quads, half_breadth
from svgkit import Sheet, nice_scale

DECK_COL = ["#7b3fa0", "#1f5fbf", "#1b8a5a", "#c47a00", "#b03030", "#2a8a9a", "#8a6a2a"]


def deck_color(ship, d):
    return DECK_COL[ship.deck_ids.index(d) % len(DECK_COL)]


def m_(v):
    """Metres -> millimetre string with a thin grouping, e.g. 111525."""
    return "%d" % round(v * 1000)


class PH:
    """Horizontal plan view, bow to the RIGHT (so starboard is at the bottom): (x, z) metres -> paper mm."""

    def __init__(self, s, ox, oy):
        self.s, self.ox, self.oy = s, ox, oy

    def xy(self, x, z):
        return (self.ox - z * self.s, self.oy + x * self.s)

    def pts(self, poly):
        return [self.xy(x, z) for x, z in poly]


def station_ticks(sh, ship, xfun, y0, y1, labels_top=True, labels_bottom=False, cls="cl"):
    for k, z in ship.station_zs():
        x = xfun(z)
        sh.line(x, y0, x, y1, cls)
        if labels_top:
            sh.circ(x, y0 - 2.6, 2.3, "f", "#fff")
            sh.text(x, y0 - 1.95, "%d" % k, 1.7, "middle", bold=True)
        if labels_bottom:
            sh.circ(x, y1 + 2.6, 2.3, "f", "#fff")
            sh.text(x, y1 + 3.25, "%d" % k, 1.7, "middle", bold=True)


def _legend_row(sh, x, y, cls, stroke, dash, text, fill="none"):
    if dash:
        sh.line(x, y, x + 10, y, "dsh", stroke=stroke)
    else:
        sh.line(x, y, x + 10, y, cls, stroke=stroke)
    sh.text(x + 12.5, y + 0.7, text, 1.7)


# ------------------------------------------------------------------ G-04 hull lines
def contour_levels(ship):
    sk = ship.skin
    lv_ = [sk.y0 + 0.4]
    v = math.ceil((sk.y0 + 0.9) / 2.0) * 2.0
    while v < sk.y1 - 0.9:
        lv_.append(v)
        v += 2.0
    lv_.append(sk.y1 - 0.1)
    for d in ship.deck_ids:
        y = ship.deck_y[d]
        if all(abs(y - q) > 0.05 for q in lv_):
            lv_.append(y)
    return sorted(lv_)


def hull_lines(ship):
    sk = ship.skin
    deck_levels = {round(ship.deck_y[d], 3): d for d in ship.deck_ids}
    sh = Sheet("G-04", "Hull lines plan", "HALF-BREADTH PLAN: SKIN CONTOURS EVERY 2 m, DECK FLOORS COLOURED",
               "1:400", "ALL", "HULL", "Hull lines", slug="hull_lines_plan")
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    s = 1000.0 / 400
    px_stern = 32.0
    ph = PH(s, px_stern + oz1 * s, 106.0)
    hb = max(abs(ox0), abs(ox1))
    ytop, ybot = ph.xy(-hb, 0)[1], ph.xy(hb, 0)[1]
    station_ticks(sh, ship, lambda z: ph.xy(0, z)[0], ytop - 6, ybot + 6, True, True)
    sh.text(14 + 2, 14, "HULL LINES - PLAN VIEW OF THE OUTER SKIN", 3.0, bold=True)
    sh.text(14 + 2, 18.4, "Bow to the right, starboard at the bottom. Stations every %g m from the forward perpendicular (FP, station 0, z = %+.1f m)." %
            (STATION_M, ship.fp_z), 1.8, fill="#555")
    # contours
    levels = contour_levels(ship)
    for y in levels:
        poly = sk.plan(y)
        if not poly:
            continue
        d = deck_levels.get(round(y, 3))
        if d is None:
            sh.poly(ph.pts(poly), "f", stroke="#8c8c8c")
    for y in levels:
        d = deck_levels.get(round(y, 3))
        if d is not None:
            sh.poly(ph.pts(sk.plan(y)), "m", stroke=deck_color(ship, d))
    for d in ship.deck_ids:
        sh.poly(ph.pts(ship.hull[d]), "dsh", stroke=deck_color(ship, d))
    # fittings
    for f in ship.fittings:
        pts = ph.pts(f.hull2(0, 2))
        sh.poly(pts, "n", "#dfe5ee", op=0.55)
    sh.line(ph.xy(0, oz1)[0] - 6, ph.oy, ph.xy(0, oz0)[0] + 6, ph.oy, "cl")
    sh.text(ph.xy(0, oz1)[0] - 7, ph.oy + 0.7, "CL", 1.8, "end", bold=True)
    for f in ship.fittings:
        if f.id.endswith("port") or "mast" in f.id and f.pos[2] > 0:
            continue
        cx, cy = ph.xy(f.pos[0], (f.bmin[2] + f.bmax[2]) / 2)
        if f.pos[0] > 1:
            cy = ph.xy(f.pos[0] + f.size[0] / 2, 0)[1] + 3.0
            sh.text(cx, cy, "NACELLES (P + S)", 1.7, "middle", bold=True)
        elif "mast" in f.id:
            sh.text(cx, cy - 4.5, "MAST", 1.5, "middle")
        elif "keel" not in f.id:
            sh.text(cx, cy - ph.s * f.size[0] / 2 - 1.2, f.label.upper(), 1.6, "middle", bold=True)
    # dimensions
    xs, xb = ph.xy(0, oz1)[0], ph.xy(0, oz0)[0]
    sh.dim_h(xs, xb, ybot + 24, "LENGTH OVERALL %s (incl. fittings)" % m_(oz1 - oz0), ext_y=ybot + 4)
    sh.dim_h(ph.xy(0, sk.z1)[0], ph.xy(0, sk.z0)[0], ybot + 17, "LENGTH OF SKIN %s" % m_(sk.z1 - sk.z0), ext_y=ybot + 4)
    sh.dim_v(ph.xy(ox0, 0)[1], ph.xy(ox1, 0)[1], px_stern - 14, "BEAM OVER NACELLES %s" % m_(ox1 - ox0), ext_x=px_stern - 3)
    sh.dim_v(ph.xy(sk.x0, 0)[1], ph.xy(sk.x1, 0)[1], px_stern - 6, "BEAM OF SKIN %s" % m_(sk.x1 - sk.x0), ext_x=px_stern - 3)
    # right column: arrow, scale, legend
    xr = ph.xy(0, oz0)[0] + 12
    sh.bow_arrow(xr + 16, 34)
    sh.scalebar(xr + 40, 40, s)
    y = 58.0
    sh.text(xr, y, "SKIN CONTOURS (waterline-style)", 2.2, bold=True)
    y += 5
    for d in ship.deck_ids:
        _legend_row(sh, xr, y, "m", deck_color(ship, d), False, "skin at Deck %d FFL %s" % (d, lv(ship.deck_y[d])))
        y += 4.0
    sh.line(xr, y, xr + 10, y, "f", stroke="#8c8c8c")
    sh.text(xr + 12.5, y + 0.7, "skin at other 2 m levels, keel and roof", 1.7)
    y += 4.6
    sh.text(xr, y, "DECK OUTLINES", 2.2, bold=True)
    y += 5
    _legend_row(sh, xr, y, "dsh", "#444", True, "deck outline (colour = deck as above)")
    y += 4.6
    sh.poly([(xr, y - 1.4), (xr + 10, y - 1.4), (xr + 10, y + 1.4), (xr, y + 1.4)], "n", "#dfe5ee", op=0.55)
    sh.text(xr + 12.5, y + 0.7, "exterior fitting (box from arch.json bounds)", 1.7)
    # offsets table
    cols = ship.deck_ids
    hdr = ["STN", "z m"] + ["HB D%d" % d for d in cols] + ["HB MAX", "KEEL y", "ROOF y"]
    cw = [11, 18] + [17] * len(cols) + [19, 18, 18]
    plans = {d: sk.plan(ship.deck_y[d]) for d in cols}
    rows = []
    for k, z in ship.station_zs(sk.z0 + 1e-3, sk.z1 - 1e-3):
        r = ["%d" % k, "%+.1f" % z]
        for d in cols:
            v = half_breadth(plans[d], z) if plans[d] else None
            r.append("-" if v is None else "%.2f" % v)
        polys = skin_cut(sk, Cut("z", z))
        r.append("%.2f" % max(abs(h) for p in polys for h, yy in p))
        r.append("%+.2f" % min(yy for p in polys for h, yy in p))
        r.append("%+.2f" % max(yy for p in polys for h, yy in p))
        rows.append(tuple(r))
    sh.table(14.0, 218.0, cw, rows, header=tuple(hdr), title="SKIN HALF-BREADTHS (m) AT THE STATIONS - at each deck floor level; HB = half-breadth", rh=3.0, size=1.6)
    sh.text(xr, 130, "Hull sides lean outward with height (about 9 deg);", 1.7)
    sh.text(xr, 134, "nacelles stand outside the skin on each beam.", 1.7)
    return sh


# ------------------------------------------------------------------ G-05 profile
def _union(iv):
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def profile_sheet(ship):
    sk = ship.skin
    sh = Sheet("G-05", "Profile - outer skin and fittings", "SIDE ELEVATION: SKIN SILHOUETTE, DECK LINES, WINDOWS, FITTINGS",
               "1:400", "ALL", "PROFILE", "Profile", slug="profile_outboard_elevation")
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    s = 1000.0 / 400
    sv = SV(s, 50.0, 0.0, -oz1, oy0)
    sv.oy = 150.0 + (0.0)                       # paper y of the lowest point (oy0)
    X = lambda z: sv.xy(-z, 0)[0]
    Y = lambda y: sv.xy(0, y)[1]
    sh.text(14 + 2, 14, "PROFILE - STARBOARD OUTBOARD ELEVATION OF THE OUTER SKIN", 3.0, bold=True)
    sh.text(14 + 2, 18.4, "Solid: skin silhouette (outermost outline over the beam). Dashed: skin on the centreline (x = 0). Thin boxes: room volumes. Panes: ext_windows facing starboard.", 1.8, fill="#555")
    fore, aft = sk.silhouette()
    sil = [sv.xy(-z, y) for z, y in fore] + [sv.xy(-z, y) for z, y in reversed(aft)]
    # port-side fittings (behind the skin) first
    for f in ship.fittings:
        if f.pos[0] < -1:
            sh.poly([sv.xy(-z, y) for z, y in f.hull2(2, 1)], "hid")
    sh.poly(sil, "h", "#edf1f7")
    for poly in skin_cut(sk, Cut("x", 0.0)):
        sh.poly([sv.xy(-h, y) for h, y in poly], "dsh")
    # room volumes
    groups = {}
    for r in ship.rooms:
        groups.setdefault((r.y, r.top), []).append((r.z0, r.z1))
    for (y, top), ivs in sorted(groups.items()):
        for a, b in _union(ivs):
            sh.poly(sv.box(-b, -a, y - SLAB_T, top + SLAB_T), "x", "#dfe5ee", op=0.7)
    # deck lines across the skin
    for d in ship.deck_ids:
        y = ship.deck_y[d]
        pl = sk.plan(y)
        if pl:
            za, zb = min(p[1] for p in pl), max(p[1] for p in pl)
            sh.line(X(zb), Y(y), X(za), Y(y), "cl")
    # window panes (starboard)
    for quad, kind, room in ext_window_quads(ship, 1):
        pts = [sv.xy(-c[2], c[1]) for c in quad]
        if kind == "mouth":
            sh.poly(pts, "n", "#bfe0f5", op=0.85)
        else:
            sh.poly(pts, "f", "url(#hGlass)")
    # fittings in front / on the centreline
    for f in ship.fittings:
        if f.pos[0] < -1:
            continue
        pts = [sv.xy(-z, y) for z, y in f.hull2(2, 1)]
        near = f.pos[0] > 1
        sh.poly(pts, "m", "#d3dae6", op=0.6 if near else 0.9)
    for f in ship.fittings:
        if f.pos[0] < -1:
            continue
        zc = (f.bmin[2] + f.bmax[2]) / 2
        if "mast" in f.id:
            if f.pos[2] < 0:
                sh.text(X(f.pos[2]), Y(f.bmax[1]) - 1.5, "MAST", 1.5, "middle", bold=True)
            continue
        if f.pos[0] > 1:
            sh.text(X(zc), Y(f.bmax[1]) - 1.5, "NACELLE (P + S)", 1.7, "middle", bold=True)
        elif "keel" in f.id:
            sh.text(X(zc), Y(f.bmin[1]) + 3.0, "KEEL FIN", 1.7, "middle", bold=True)
        elif "deflector" in f.id:
            sh.text(X(f.bmin[2]) - 1.5, Y(f.pos[1]) - 8.5, "DEFLECTOR", 1.7, "end", bold=True)
        else:
            sh.text(X(zc), Y(f.bmin[1]) + 3.0, f.label.upper(), 1.7, "middle", bold=True)
    # room names
    for rid, txt in (("hangar", "HANGAR"), ("bridge", "BRIDGE")):
        r = ship.by_id.get(rid)
        if r:
            sh.text(X((r.z0 + r.z1) / 2), Y(r.y + r.h / 2), txt, 1.8, "middle", bold=True, halo=True)
    # level marks on the right, centre-line datum
    xl = X(oz0) + 8
    for d in ship.deck_ids:
        sh.level_mark(xl, Y(ship.deck_y[d]), "%s DECK %d - %s" % (lv(ship.deck_y[d]), d, ship.deck_name[d].upper()), 1.6, True)
    sh.level_mark(xl, Y(sk.y1), "%s ROOF OF SKIN" % lv(sk.y1), 1.6, True)
    sh.level_mark(xl, Y(sk.y0), "%s KEEL OF SKIN" % lv(sk.y0), 1.6, True)
    # stations along the bottom
    yb = Y(oy0) + 6
    sh.line(X(oz1), yb, X(oz0), yb, "f")
    for k, z in ship.station_zs():
        x = X(z)
        sh.line(x, yb - 1.5, x, yb + 1.5, "m")
        sh.text(x, yb + 5, "%d" % k, 1.7, "middle")
        sh.line(x, yb - 1.5, x, Y(oy1) - 4, "gg")
    sh.text(X(oz1), yb + 9.5, "STATIONS every %g m from the forward perpendicular (station 0 at the bow end, z = %+.1f m)" % (STATION_M, ship.fp_z), 1.6, fill="#555")
    sh.dim_h(X(sk.z1), X(sk.z0), yb + 14, "LENGTH OF SKIN %s" % m_(sk.z1 - sk.z0), ext_y=Y(sk.y0) + 1)
    sh.dim_h(X(oz1), X(oz0), yb + 21, "LENGTH OVERALL %s" % m_(oz1 - oz0), ext_y=yb + 2)
    # vertical dims at the stern side (left)
    xd = X(oz1) - 8
    levels = sorted({ship.deck_y[d] for d in ship.deck_ids})
    ys = [Y(v) for v in levels]
    sh.chain_v(list(reversed(ys)), xd, [m_(levels[i + 1] - levels[i]) for i in reversed(range(len(levels) - 1))], ext_x=X(oz1) - 1)
    sh.dim_v(Y(sk.y1), Y(sk.y0), xd - 9, "SKIN KEEL TO ROOF %s" % m_(sk.y1 - sk.y0), ext_x=X(oz1) - 1)
    sh.dim_v(Y(oy1), Y(oy0), xd - 18, "OVERALL HEIGHT %s" % m_(oy1 - oy0), ext_x=X(oz1) - 1)
    # section markers
    from sheets_ga import SECTION_CUTS
    ytop = Y(oy1) - 6
    for num, axis, c, title, desc in SECTION_CUTS:
        if axis == "z":
            x = X(c)
            sh.line(x, ytop, x, Y(sk.y0) + 2, "cut")
            sh.circ(x, ytop - 3.2, 3.0, "n", "#fff")
            sh.text(x, ytop - 2.6, num.replace("G-", ""), 1.8, "middle", bold=True)
    sh.arrow(X(oz0) - 30, 35, X(oz0) - 6, 35, "m", 2.2)
    sh.text(X(oz0) - 4, 36, "BOW", 2.4, bold=True)
    sh.text(X(oz1), 36, "STERN", 2.4, bold=True)
    sh.scalebar(14 + 6, 280, s)
    # fittings table
    rows = []
    for f in ship.fittings:
        rows.append((f.label, "%+.1f / %+.1f / %+.1f" % f.pos, "%.1f x %.1f x %.1f" % f.size, "%+.1f .. %+.1f" % (f.bmin[2], f.bmax[2]), "%+.1f .. %+.1f" % (f.bmin[1], f.bmax[1])))
    sh.table(14.0, 200.0, [30, 36, 30, 28, 28], rows, header=("FITTING", "ORIGIN x / y / z m", "BOX L x H x W m", "z RANGE m", "y RANGE m"),
             title="EXTERIOR FITTINGS (boxes from godot/data/arch.json bounds)", rh=3.3, size=1.6)
    nw = sum(1 for w in ship.ext_windows if w["kind"] == "window")
    nm = sum(1 for w in ship.ext_windows if w["kind"] != "window")
    notes = ["%d window panes and %d hangar mouth panel(s) in ship.json ext_windows;" % (nw, nm), "the starboard half is drawn, the port half mirrors it.",
             "Decks: " + ", ".join("%d %s" % (d, lv(ship.deck_y[d])) for d in ship.deck_ids) + "."]
    for i, t in enumerate(notes):
        sh.text(14 + 170, 204 + i * 4.2, t, 1.7)
    return sh


# ------------------------------------------------------------------ body plan
def body_plan(ship, num="G-17"):
    sk = ship.skin
    stations = ship.station_zs(sk.z0 + 0.3, sk.z1 - 0.3)
    sh = Sheet(num, "Body plan - skin sections", "SKIN SECTIONS AT EVERY %g m STATION, LOOKING AFT, WITH DECK FLOORS" % STATION_M,
               "1:600", "ALL", "HULL", "Body plan", slug="body_plan")
    cols = 6
    nrow = max(1, -(-len(stations) // cols))
    area = (14.0, 8.0, 410.0, 250.0)
    cw = (area[2] - area[0]) / cols
    ch = min(80.0, (area[3] - area[1]) / nrow)
    wmax, hmax = sk.x1 - sk.x0, sk.y1 - sk.y0
    n = nice_scale(cw - 6, ch - 12, wmax, hmax, options=(400, 500, 600, 700, 800, 1000))
    s = 1000.0 / n
    sh.scale = "1:%d" % n
    ext = skin_extreme(sk, Cut("z", 0.0))
    for i, (k, z) in enumerate(stations):
        col, row = i % cols, i // cols
        cx = area[0] + (col + 0.5) * cw
        ybase = area[1] + (row + 1) * ch - 3.0 - 2.0
        sv = SV(s, cx, ybase, 0.0, sk.y0)
        sh.rect(area[0] + col * cw + 1, area[1] + row * ch + 1, cw - 2, ch - 2, "x")
        sh.text(area[0] + col * cw + 3, area[1] + row * ch + 5.0, "STATION %d" % k, 2.2, bold=True)
        sh.text(area[0] + col * cw + 3, area[1] + row * ch + 8.4, "z = %+.1f m" % z, 1.6, fill="#444")
        sh.poly([sv.xy(h, y) for h, y in ext], "gg")
        sh.line(*sv.xy(0, sk.y0 - 0.3), *sv.xy(0, sk.y1 + 0.5), "cl")
        for d in ship.deck_ids:
            iv = line_interval(ship.hull[d], 1, z)
            y = ship.deck_y[d]
            if iv:
                sh.line(*sv.xy(iv[0], y), *sv.xy(iv[1], y), "m", stroke=deck_color(ship, d))
        polys = skin_cut(sk, Cut("z", z))
        for poly in polys:
            sh.poly([sv.xy(h, y) for h, y in poly], "h", "#edf1f7", op=0.5)
        # deck lines again on top, thinner
        for d in ship.deck_ids:
            iv = line_interval(ship.hull[d], 1, z)
            if iv:
                x0, y0 = sv.xy(iv[0], ship.deck_y[d])
                x1, _ = sv.xy(iv[1], ship.deck_y[d])
                sh.line(x0, y0, x1, y0, "m", stroke=deck_color(ship, d))
        wd = max((max(h for h, y in p) - min(h for h, y in p)) for p in polys) if polys else 0
        sh.text(area[0] + col * cw + cw - 3, area[1] + row * ch + 5.0, "B %.1f m" % wd, 1.7, "end")
    # key: profile with the stations, and legend
    ky = area[1] + nrow * ch
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    ks = 0.55
    kx0 = 20.0
    kyb = 280.0 - 4
    sv = SV(ks, kx0 - (-oz1) * ks, kyb, 0.0, oy0)
    fore, aft = sk.silhouette()
    sh.poly([sv.xy(-z, y) for z, y in fore] + [sv.xy(-z, y) for z, y in reversed(aft)], "n", "#edf1f7")
    for f in ship.fittings:
        if f.pos[0] > -1:
            sh.poly([sv.xy(-z, y) for z, y in f.hull2(2, 1)], "f", "#d3dae6", op=0.6)
    for k, z in ship.station_zs():
        x = sv.xy(-z, 0)[0]
        sh.line(x, sv.xy(0, sk.y0)[1] - 1.0, x, sv.xy(0, sk.y1)[1] - 1.5, "gg")
        sh.text(x, sv.xy(0, sk.y1)[1] - 2.2, "%d" % k, 1.3, "middle")
    sh.text(14 + 2, ky + 4.0, "KEY - STATIONS ON THE PROFILE (bow right)", 1.9, bold=True)
    x = 14 + 140.0
    sh.text(x, ky + 4.0, "READING THE BODY PLAN", 1.9, bold=True)
    notes = ["Every cell is the cut of the skin on the plane z = station, looking aft", "(starboard on the left, as in sections G-07 to G-12), common scale %s." % sh.scale,
             "Grey dashed line: the largest section of the whole skin, repeated for comparison.",
             "Coloured horizontal lines: deck outline width at the floor of each deck;"]
    for i, t in enumerate(notes):
        sh.text(x, ky + 8.2 + 3.8 * i, t, 1.6)
    for j, d in enumerate(ship.deck_ids):
        yy = ky + 25.0 + j * 3.8
        if yy < 248 + 40:
            sh.line(x, yy - 0.6, x + 8, yy - 0.6, "m", stroke=deck_color(ship, d))
            sh.text(x + 10, yy, "Deck %d %s (FFL %s)" % (d, ship.deck_name[d], lv(ship.deck_y[d])), 1.6)
    return sh


# ------------------------------------------------------------------ principal particulars
def particulars_sheet(ship, num="G-18"):
    sk = ship.skin
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    sh = Sheet(num, "Principal particulars", "PARTICULARS, FITTINGS, DECKS AND SKIN STATION OFFSETS", "NTS", "ALL", "HULL",
               "Particulars", slug="principal_particulars")
    mast = [f for f in ship.fittings if "mast" in f.id]
    keelfin = [f for f in ship.fittings if "keel" in f.id]
    nac = [f for f in ship.fittings if "nacelle" in f.id]
    hb = ship.bounds(None)
    area_total = sum(r.area for r in ship.rooms)
    crew = sum(r.crew() for r in ship.rooms)
    datum = ship.deck_y[ship.deck_ids[-2]] if len(ship.deck_ids) > 1 else 0.0
    rows = [
        ("Length overall (incl. fittings)", "%.2f m" % (oz1 - oz0)),
        ("Length of skin", "%.2f m" % (sk.z1 - sk.z0)),
        ("Length of room decks (max)", "%.1f m" % (hb[3] - hb[1])),
        ("Beam over nacelles", "%.2f m" % (ox1 - ox0)),
        ("Beam of skin (max)", "%.2f m" % (sk.x1 - sk.x0)),
        ("Beam of deck outlines", "%.1f m" % (hb[2] - hb[0])),
        ("Height, skin keel to roof", "%.2f m" % (sk.y1 - sk.y0)),
        ("Height, keel (incl. fin) to mast top", "%.2f m" % (oy1 - oy0)),
        ("Height, skin keel to mast top", "%.2f m" % (max([f.bmax[1] for f in mast] + [sk.y1]) - sk.y0)),
        ("Draught (skin keel below datum %s)" % lv(datum), "%.2f m" % (datum - sk.y0)),
        ("Draught to the tip of the keel fin", "%.2f m" % (datum - min([f.bmin[1] for f in keelfin] + [sk.y0]))),
        ("Decks", "%d  (%s)" % (len(ship.deck_ids), ", ".join("%d: %s" % (d, lv(ship.deck_y[d])) for d in ship.deck_ids))),
        ("Floor to floor", "4.000 m"),
        ("Rooms / props", "%d / %d" % (len(ship.rooms), sum(len(r.props) for r in ship.rooms))),
        ("Room floor area (all decks)", "%.0f m2" % area_total),
        ("Skin enclosed volume", "%.0f m3" % sk.volume()),
        ("Crew (sum of room briefs)", str(crew)),
        ("Stations", "every %g m from FP (z = %+.1f m)" % (STATION_M, ship.fp_z)),
    ]
    y = sh.table(14.0, 24.0, [66, 96], rows, header=("ITEM", "VALUE"), title="PRINCIPAL PARTICULARS", rh=3.7, size=1.9, bold_first=True)
    # decks
    drows = []
    for d in ship.deck_ids:
        b = ship.bounds(d)
        rr = ship.deck_rooms(d)
        drows.append(("%d" % d, ship.deck_name[d], lv(ship.deck_y[d]), "%.1f" % (b[3] - b[1]), "%.1f" % (b[2] - b[0]), "%.0f" % abs(poly_area(ship.hull[d])),
                      "%.0f" % sum(r.area for r in rr), str(len(rr))))
    y = sh.table(14.0, y + 10, [10, 40, 22, 18, 18, 22, 22, 10], drows, header=("DK", "NAME", "FFL m", "L m", "B m", "AREA m2", "ROOMS m2", "N"),
                 title="DECKS", rh=3.7, size=1.8)
    # fittings
    frows = [(f.label, "%+.2f / %+.2f / %+.2f" % f.pos, "%.1f x %.1f x %.1f" % (f.size[2], f.size[1], f.size[0]), "%.1f" % f.yaw) for f in ship.fittings]
    y = sh.table(14.0, y + 10, [40, 52, 44, 24], frows, header=("FITTING", "POS x / y / z m", "L x H x W m", "YAW"), title="EXTERIOR FITTINGS", rh=3.7, size=1.8)
    # offsets
    sx = 204.0
    orows = []
    for k, z in ship.station_zs(sk.z0 + 1e-3, sk.z1 - 1e-3):
        polys = skin_cut(sk, Cut("z", z))
        ar = sum(abs(poly_area([(h, yy) for h, yy in p])) for p in polys)
        wd = max(max(h for h, yy in p) - min(h for h, yy in p) for p in polys)
        orows.append(("%d" % k, "%+.1f" % z, "%.2f" % wd, "%+.2f" % min(yy for p in polys for h, yy in p), "%+.2f" % max(yy for p in polys for h, yy in p),
                      "%.1f" % ar))
    sh.table(sx, 24.0, [14, 24, 28, 28, 28, 30], orows, header=("STN", "z m", "BEAM m", "KEEL y m", "TOP y m", "AREA m2"),
             title="SKIN STATION OFFSETS (section on z = station)", rh=3.7, size=1.8, bold_first=True)
    sh.text(sx, 24.0 + 3.7 * (len(orows) + 3) + 5, "Beam = full width of the skin section; KEEL / TOP = lowest and highest point of the section;", 1.6, fill="#555")
    sh.text(sx, 24.0 + 3.7 * (len(orows) + 3) + 8.6, "AREA = enclosed cross-section area. Plan contours: G-04, body plan: G-17.", 1.6, fill="#555")
    _dimension_diagrams(sh, ship, 176.0)
    return sh


def _dimension_diagrams(sh, ship, y0):
    """Plan and profile of the whole ship at 1:800 with the principal dimensions."""
    sk = ship.skin
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    s = 1000.0 / 800
    sh.text(14.0, y0 + 2, "PRINCIPAL DIMENSIONS - PLAN AND PROFILE  1:800", 2.3, bold=True)
    # plan (bow right, starboard down)
    ph = PH(s, 24.0 + oz1 * s, y0 + 14 + max(abs(ox0), abs(ox1)) * s + 4)
    big = max(sk.pts, key=lambda r: abs(poly_area(r)))
    sh.poly(ph.pts(big), "m", "#edf1f7")
    for f in ship.fittings:
        sh.poly(ph.pts(f.hull2(0, 2)), "n", "#d3dae6", op=0.6)
    sh.line(ph.xy(0, oz1)[0] - 3, ph.oy, ph.xy(0, oz0)[0] + 3, ph.oy, "cl")
    ytop, ybot = ph.xy(ox0, 0)[1], ph.xy(ox1, 0)[1]
    sh.dim_h(ph.xy(0, oz1)[0], ph.xy(0, oz0)[0], ybot + 7, "LENGTH OVERALL %s" % m_(oz1 - oz0), ext_y=ybot + 1)
    sh.dim_h(ph.xy(0, sk.z1)[0], ph.xy(0, sk.z0)[0], ybot + 14, "LENGTH OF SKIN %s" % m_(sk.z1 - sk.z0), ext_y=ybot + 1)
    sh.dim_v(ytop, ybot, ph.xy(0, oz1)[0] - 4, "BEAM OVER NACELLES %s" % m_(ox1 - ox0), ext_x=ph.xy(0, oz1)[0] + 3)
    sh.dim_v(ph.xy(sk.x0, 0)[1], ph.xy(sk.x1, 0)[1], ph.xy(0, oz0)[0] + 5, "BEAM OF SKIN %s" % m_(sk.x1 - sk.x0), ext_x=ph.xy(0, oz0)[0] - 3)
    # profile
    px = 200.0
    sv = SV(s, px, y0 + 20 + (oy1 - oy0) * s, -oz1, oy0)
    fore, aft = sk.silhouette()
    sh.poly([sv.xy(-z, y) for z, y in fore] + [sv.xy(-z, y) for z, y in reversed(aft)], "m", "#edf1f7")
    for f in ship.fittings:
        if f.pos[0] > -1:
            sh.poly([sv.xy(-z, y) for z, y in f.hull2(2, 1)], "n", "#d3dae6", op=0.6)
    for d in ship.deck_ids:
        pl = sk.plan(ship.deck_y[d])
        za, zb = min(p[1] for p in pl), max(p[1] for p in pl)
        sh.line(*sv.xy(-zb, ship.deck_y[d]), *sv.xy(-za, ship.deck_y[d]), "cl")
    xr = sv.xy(-oz0, 0)[0] + 6
    sh.dim_v(sv.xy(0, oy1)[1], sv.xy(0, oy0)[1], xr, "HEIGHT KEEL TO MAST %s" % m_(oy1 - oy0), ext_x=xr - 4)
    sh.dim_v(sv.xy(0, sk.y1)[1], sv.xy(0, sk.y0)[1], xr + 8, "SKIN %s" % m_(sk.y1 - sk.y0), ext_x=xr - 4)
    ydat = ship.deck_y[ship.deck_ids[-2]] if len(ship.deck_ids) > 1 else 0.0
    sh.dim_v(sv.xy(0, ydat)[1], sv.xy(0, sk.y0)[1], sv.xy(-oz1, 0)[0] - 6, "DRAUGHT %s" % m_(ydat - sk.y0), ext_x=sv.xy(-oz1, 0)[0] - 1)
    sh.text(px, y0 + 8, "Datum %s (deck %d floor); bow to the right." % (lv(ydat), ship.deck_ids[-2] if len(ship.deck_ids) > 1 else 0), 1.6, fill="#555")
