"""General arrangement sheets: deck plans, hull lines, profile, ship sections."""
import math

from shipmodel import SLAB_T, STATION_M, line_interval, poly_area
from planview import (PV, draw_floor, draw_walls, draw_openings, draw_props, draw_holes, draw_stairs, draw_forcefields)
from sectionview import (SV, Cut, draw_room_section, draw_stairs_section, lv)
from hullview import skin_cut, skin_beyond, draw_fittings_section
from svgkit import Sheet, nice_scale, text_w, trunc

GA_SCALE = 250

# (sheet number, axis, plane position, title, description); the description is written from the rooms actually cut
SECTION_CUTS = [
    ("G-06", "x", 0.0, "Longitudinal section on centreline", ""),
    ("G-07", "z", 1.8, "Transverse section A - stair lobby", ""),
    ("G-08", "z", -28.0, "Transverse section B - bridge", ""),
    ("G-09", "z", -6.0, "Transverse section C - forward midship", ""),
    ("G-10", "z", 8.0, "Transverse section D - aft midship", ""),
    ("G-11", "z", 26.0, "Transverse section E - hangar bay and hold", ""),
    ("G-12", "z", -18.0, "Transverse section F - forward rooms", ""),
]

# Deck sheets keep their historic numbers G-01..G-03 (decks 1..3); further decks take the next free numbers.
DECK_SHEET_SLOT = {1: 1, 2: 2, 3: 3}


def deck_sheet_numbers(ship, first_free):
    """{deck: slot number}: decks 1..3 keep slots 1..3, every other deck gets first_free, first_free + 1, ..."""
    out, nxt = {}, first_free
    for d in ship.deck_ids:
        if d in DECK_SHEET_SLOT:
            out[d] = DECK_SHEET_SLOT[d]
        else:
            out[d] = nxt
            nxt += 1
    return out


def cut_description(ship, axis, c, maxn=9):
    cut = Cut(axis, c)
    names = []
    for d in ship.deck_ids:
        for r in sorted(ship.deck_rooms(d), key=lambda q: (cut.iv(q.poly) or (0, 0))[0]):
            iv = cut.iv(r.poly)
            if iv and iv[1] - iv[0] > 0.05 and not r.id.startswith(("tower", "cor", "lobby")):
                if r.name not in names:
                    names.append(r.name)
    stairs = any(cut.iv(t.poly) for t in ship.rooms if t.id.startswith("tower"))
    txt = ", ".join(n.lower() for n in names[:maxn]) + (" and %d more" % (len(names) - maxn) if len(names) > maxn else "")
    pre = "plane %s = %+.1f m through " % (axis, c)
    if stairs:
        txt = "stair lobby, both stair towers" + (", " + txt if txt else "")
    return pre + (txt or "corridors")


def bow_z(ship):
    return ship.fp_z


def stern_z(ship):
    return max(p[1] for pts in ship.hull.values() for p in pts)


# ------------------------------------------------------------------ deck plans
def room_label(sh, pv, room, small=False):
    s = pv.s
    cx, cy = pv.xy(room.cx, room.cz)
    wmm, hmm = room.w * s, room.dd * s
    name = room.name
    rot = 0
    size = 2.1
    if wmm < 17 and hmm > wmm * 1.6:
        rot = -90
        avail = hmm - 4
    else:
        avail = wmm - 3
    if room.id.startswith("tower"):
        name = "STAIR " + ("PORT" if room.id.startswith("towerA") else "STBD")
        size = 1.8
    if rot:
        sh.text(cx + 0.7, cy + text_w(trunc(name, avail, size), size) / 2, trunc(name.upper(), avail, size), size, rot=-90, halo=True, bold=True)
        sh.text(cx - 2.2, cy + text_w(room.code, 1.8) / 2, room.code, 1.8, rot=-90, halo=True, fill="#444")
        return
    # wrap into up to two lines
    lines = wrap_words(name.upper(), max(6, int(avail / (0.54 * size)))) or [""]
    lines = [trunc(l, avail, size) for l in lines[:2]]
    y = cy - 1.4 * (len(lines) - 1)
    for l in lines:
        sh.text(cx, y, l, size, "middle", bold=True, halo=True)
        y += 2.5
    sh.text(cx, y + 0.2, "%s  %.0f m2" % (room.code, room.area), 1.7, "middle", fill="#333", halo=True)


def station_grid(sh, pv, ship, xl, xr, deck):
    """Station lines every STATION_M metres from the forward perpendicular (station 0 = foremost point of the ship)."""
    hz0, hz1 = ship.bounds(deck)[1], ship.bounds(deck)[3]
    for k, z in ship.station_zs(hz0, hz1):
        y = pv.xy(0, z)[1]
        sh.line(xl, y, xr, y, "cl")
        sh.circ(xr + 3.0, y, 2.4, "f", "#fff")
        sh.text(xr + 3.0, y + .7, "%d" % k, 1.8, "middle", bold=True)


def cut_marks_on_plan(sh, pv, ship, deck):
    bx0, bz0, bx1, bz1 = ship.bounds(deck)
    for num, axis, c, title, desc in SECTION_CUTS:
        if axis == "x":
            if not (bx0 <= c <= bx1):
                continue
            ends = [(pv.xy(c, bz0 - 2.0), pv.xy(c, bz0 + 2.0)), (pv.xy(c, bz1 + 2.0), pv.xy(c, bz1 - 2.0))]
        else:
            if not (bz0 <= c <= bz1):
                continue
            if not any(r.deck == deck and Cut("z", c).iv(r.poly) for r in ship.rooms):
                continue
            ends = [(pv.xy(bx0 - 2.0, c), pv.xy(bx0 + 2.0, c)), (pv.xy(bx1 + 2.0, c), pv.xy(bx1 - 2.0, c))]
        for a, b in ends:
            sh.line(*a, *b, "cut")
            # circle beyond the outer end
            dx, dy = a[0] - b[0], a[1] - b[1]
            L = math.hypot(dx, dy) or 1
            cx, cy = a[0] + dx / L * 3.4, a[1] + dy / L * 3.4
            sh.circ(cx, cy, 3.0, "n", "#fff")
            sh.text(cx, cy + .6, num.replace("G-", ""), 1.8, "middle", bold=True)


SYMBOLS_H = 38.0


def ga_symbol_key(sh, x, y):
    sh.text(x, y, "SYMBOLS", 2.3, bold=True)
    y += 3.0
    # poche
    sh.rect(x, y, 8, 2.4, "n", "#1c1c1c")
    sh.text(x + 10, y + 1.9, "Wall (150 mm poche)", 1.8)
    y += 4.0
    sh.rect(x, y, 8, 3, "m", "#fff")
    sh.line(x + 0.6, y + 1.5, x + 4, y + 1.5, "dsh")
    sh.poly([(x + 4, y + .9), (x + 8, y + .9), (x + 8, y + 2.1), (x + 4, y + 2.1)], "f", "#7a8594")
    sh.text(x + 10, y + 2.0, "Sliding door (leaf) / D-mark", 1.8)
    y += 4.2
    sh.line(x, y + 1.5, x + 8, y + 1.5, "n")
    sh.line(x, y + 0.8, x + 8, y + 0.8, "n")
    sh.line(x, y + 2.2, x + 8, y + 2.2, "n")
    sh.text(x + 10, y + 2.0, "Window (hull wall)", 1.8)
    y += 4.2
    sh.line(x, y + 1.5, x + 8, y + 1.5, "dsh")
    sh.text(x + 10, y + 2.0, "Open arch / portal", 1.8)
    y += 4.0
    sh.rect(x, y, 8, 3.2, "dsh", "url(#hHole)")
    sh.text(x + 10, y + 2.3, "Slab opening (stair hole)", 1.8)
    y += 4.4
    sh.arrow(x, y + 1.5, x + 8, y + 1.5, "f", 1.4)
    sh.text(x + 10, y + 2.0, "Stair, UP / DN (cut at +1.2 m)", 1.8)
    y += 4.2
    sh.line(x, y + 1.5, x + 8, y + 1.5, "cut")
    sh.text(x + 10, y + 2.0, "Section line (sheet G-06 to G-12)", 1.8)
    y += 4.2
    sh.line(x, y + 1.5, x + 8, y + 1.5, "cl")
    sh.text(x + 10, y + 2.0, "Station every %g m from the forward perpendicular" % STATION_M, 1.8)
    return y + 5


def deck_ga(ship, deck, num=None):
    cat = ship.cat
    num = num or "G-%02d" % deck
    dname = ship.deck_name[deck]
    y0 = ship.deck_y[deck]
    sh = Sheet(num, "General arrangement - Deck %d (%s)" % (deck, dname),
               "DECK %d - %s - GENERAL ARRANGEMENT PLAN AT FFL %+.3f" % (deck, dname.upper(), y0), "1:%d" % GA_SCALE,
               "DECK %d" % deck, "ALL", "Deck %d" % deck,
               slug="general_arrangement_deck%d" % deck)
    s = 1000.0 / GA_SCALE
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    ox = 14 + 30 + (13.0) * s + 8
    oy = 8 + 30 - ship.bounds(deck)[1] * s
    pv = PV(s, ox, oy, 0.0, 0.0)
    rooms = ship.deck_rooms(deck)
    hull = ship.hull[deck]
    # floors, props
    xl = pv.xy(bx0 - 2, 0)[0]
    for r in rooms:
        draw_floor(sh, pv, r, k=0.45)
    xr_grid = pv.xy(13.0, 0)[0] + 22
    station_grid(sh, pv, ship, xl - 2, xr_grid, deck)
    for r in rooms:
        draw_holes(sh, pv, r, ceiling=False)
    for r in rooms:
        draw_props(sh, pv, r, cat, lite=True)
    draw_stairs(sh, pv, ship, deck)
    for r in rooms:
        draw_walls(sh, pv, r)
    for r in rooms:
        draw_openings(sh, pv, r, marks=True)
        draw_forcefields(sh, pv, r)
    sh.poly(pv.pts(hull), "h")
    for r in rooms:
        room_label(sh, pv, r)
    cut_marks_on_plan(sh, pv, ship, deck)
    # centre line
    hb0, hb1 = ship.bounds(deck)[1], ship.bounds(deck)[3]
    sh.line(pv.xy(0, 0)[0], pv.xy(0, hb0)[1] - 6, pv.xy(0, 0)[0], pv.xy(0, hb1)[1] + 4, "cl")
    sh.text(pv.xy(0, 0)[0], pv.xy(0, hb0)[1] - 6.6, "CL", 1.8, "middle", bold=True)
    # dimensions: beam (top), room widths (top chain), LOA (left), room depths (left chain)
    hx0, hz0, hx1, hz1 = ship.bounds(deck)
    top = pv.xy(0, hb0)[1] - 14
    sh.dim_h(pv.xy(hx0, 0)[0], pv.xy(hx1, 0)[0], top - 6, "BEAM %d" % round((hx1 - hx0) * 1000), ext_y=pv.xy(0, hz0)[1] - 3)
    xs_c = sorted({round(r.x0, 3) for r in rooms if abs(r.cz - hz0) < 99} | {round(r.x1, 3) for r in rooms})
    xs_c = [v for v in xs_c if -13.01 <= v <= 13.01]
    # chain of widths along the bow-most full rows: use the deck's mid-body columns
    cols = [-hx1, -1.5, 1.5, hx1]
    xs = [pv.xy(v, 0)[0] for v in cols]
    sh.chain_h(xs, top, [str(int(round((cols[i + 1] - cols[i]) * 1000))) for i in range(3)], ext_y=pv.xy(0, hz0)[1] - 3)
    left = pv.xy(hx0, 0)[0] - 13
    sh.dim_v(pv.xy(0, hz0)[1], pv.xy(0, hz1)[1], left - 7, "LOA (DECK %d) %d" % (deck, round((hz1 - hz0) * 1000)), ext_x=pv.xy(hx0, 0)[0] - 1)
    zs = sorted({round(v, 3) for r in rooms if r.x0 <= -12.9 for v in (r.z0, r.z1)})
    ys = [pv.xy(0, v)[1] for v in zs]
    if len(ys) > 1:
        sh.chain_v(ys, left, [str(int(round((zs[i + 1] - zs[i]) * 1000))) for i in range(len(zs) - 1)], ext_x=pv.xy(hx0, 0)[0] - 1)
    right = pv.xy(hx1, 0)[0] + 10
    zs = sorted({round(v, 3) for r in rooms if r.x1 >= 12.9 for v in (r.z0, r.z1)})
    ys = [pv.xy(0, v)[1] for v in zs]
    if len(ys) > 1:
        sh.chain_v(ys, right, [str(int(round((zs[i + 1] - zs[i]) * 1000))) for i in range(len(zs) - 1)], ext_x=pv.xy(hx1, 0)[0] + 1)
    sh.text(14 + 4, pv.xy(0, hb0)[1] - 24, "STATIONS every %g m from the forward perpendicular (station 0 at z = %+.1f m); outer skin: sheets G-04 to G-06" % (STATION_M, ship.fp_z), 1.6, fill="#555")
    # right column: tables
    x = 240.0
    sh.bow_arrow(x + 12, 20)
    sh.scalebar(x + 40, 26, s)
    rows = [(r.code, r.name, "%.1f" % r.area) for r in rooms]
    y = sh.table(x, 40, [16, 70, 22], rows, header=("CODE", "ROOM", "AREA m2"), title="ROOM LEGEND - DECK %d" % deck, rh=3.5, size=1.9,
                 bold_first=True)
    tot = sum(r.area for r in rooms)
    sh.rect(x, y, 108, 3.6, "n", "#dfe3ea")
    sh.text(x + 1, y + 2.6, "TOTAL (%d rooms)" % len(rooms), 1.9, bold=True)
    sh.text(x + 106, y + 2.6, "%.1f m2" % tot, 1.9, "end", bold=True)
    y += 10
    # deck facts
    facts = [("Floor level (FFL)", "%+.3f" % y0), ("Floor to floor", floor_to_floor(ship, y0)), ("Hull area (deck)", "%.1f m2" % abs(poly_area(ship.hull[deck]))),
             ("Overall length", "%.1f m" % (hz1 - hz0)), ("Beam (max)", "%.1f m" % (hx1 - hx0)),
             ("Doors / arches", str(sum(1 for d in ship.door_list if d["deck"] == deck))),
             ("Windows", str(sum(1 for w in ship.win_list if w["deck"] == deck))),
             ("Props", str(sum(len(r.props) for r in rooms)))]
    y = sh.table(x, y + 2, [50, 58], facts, title="DECK PARTICULARS", rh=3.4, size=1.8)
    ga_symbol_key(sh, x, y + 8)
    return sh


# ------------------------------------------------------------------ ship sections
def ship_key_plan(sh, ship, cut, x, y, w, h):
    """Key plan (bow to the right, starboard at the bottom) with the cut line and the viewing direction."""
    ox0, oy0, oz0, ox1, oy1, oz1 = ship.overall()
    s = min((w - 12) / (oz1 - oz0), (h - 14) / (ox1 - ox0))
    cx0 = x + (w - (oz1 - oz0) * s) / 2 + oz1 * s            # paper x of z = 0 (bow to the right: x = cx0 - z * s)
    cy0 = y + 9 + (h - 12 - (ox1 - ox0) * s) / 2 - ox0 * s    # paper y of x = 0 (starboard down)
    P = lambda xx, zz: (cx0 - zz * s, cy0 + xx * s)
    sh.rect(x, y, w, h, "f")
    sh.text(x + 1.5, y + 3.2, "KEY PLAN (all decks and skin; bow right)", 1.8, bold=True)
    sk = ship.skin
    if sk:
        for yy in (ship.deck_y[ship.deck_ids[-1]], ship.deck_y[ship.deck_ids[0]]):
            sh.poly([P(px, pz) for px, pz in sk.plan(yy)], "n" if yy == ship.deck_y[ship.deck_ids[0]] else "x", "#f1f3f6" if yy == ship.deck_y[ship.deck_ids[0]] else "none")
    for d in reversed(ship.deck_ids):
        sh.poly([P(px, pz) for px, pz in ship.hull[d]], "x", "#e2e6ee", op=0.5)
    for f in ship.fittings:
        sh.poly([P(px, pz) for px, pz in f.hull2(0, 2)], "x", "#d3dae6", op=0.6)
    if cut.axis == "x":
        a, b = P(cut.c, oz1 + 3), P(cut.c, oz0 - 3)
        look = ((a[0] + b[0]) / 2, a[1] + 2.0, (a[0] + b[0]) / 2, a[1] + 9.0)
    else:
        a, b = P(ox0 - 3, cut.c), P(ox1 + 3, cut.c)
        look = (a[0], (a[1] + b[1]) / 2, a[0] - 9.0, (a[1] + b[1]) / 2)
    sh.line(*a, *b, "cut")
    for p in (a, b):
        sh.circ(p[0], p[1], 2.0, "n", "#fff")
        sh.text(p[0], p[1] + .6, "A", 1.8, "middle", bold=True)
    sh.arrow(*look, "m", 2.0)
    sh.text(x + w - 2, y + 3.2, "BOW >", 1.6, "end", bold=True)


def _poly_pts(sv, poly):
    return [sv.xy(h, y) for h, y in poly]


def ship_section(ship, entry, pv_scale=None):
    num, axis, c, title, desc = entry
    desc = cut_description(ship, axis, c)
    cat = ship.cat
    cut = Cut(axis, c)
    sk = ship.skin
    rooms = [r for r in ship.rooms if cut.iv(r.poly) and cut.iv(r.poly)[1] - cut.iv(r.poly)[0] > 1e-3]
    skin_polys = skin_cut(sk, cut) if sk else []
    hs = [cut.iv(r.poly)[0] for r in rooms] + [cut.iv(r.poly)[1] for r in rooms] + [h for p in skin_polys for h, y in p]
    ys_all = [r.y - SLAB_T for r in rooms] + [r.top + SLAB_T for r in rooms] + [y for p in skin_polys for h, y in p]
    cut_fit, beyond_fit = [], []
    for f in ship.fittings:
        lo, hi = f.depth_range(cut.T)
        if hi < 1e-9:
            continue
        cp = f.cut_poly(cut.T) if lo < -1e-9 else None
        if cp:
            cut_fit.append(f)
            hs += [h for h, y in cp]
            ys_all += [y for h, y in cp]
    ymin, ymax = min(ys_all), max(ys_all)
    for f in ship.fittings:
        lo, hi = f.depth_range(cut.T)
        bp = f.beyond_poly(cut.T) if hi > 1e-9 else None
        if bp and f not in cut_fit and min(y for h, y in bp) >= ymin - 0.5 and max(y for h, y in bp) <= ymax + 0.5:
            beyond_fit.append(f)
            hs += [h for h, y in bp]
    a, b = min(hs), max(hs)
    area = (14.0, 8.0, 410.0, 200.0)
    n = nice_scale(area[2] - area[0] - 56, area[3] - area[1] - 50, b - a, ymax - ymin, options=(50, 75, 100, 150, 200, 250, 300, 400, 500))
    s = 1000.0 / n
    sh = Sheet(num, title, "SECTION A-A %s - %s" % (cut.label, desc), "1:%d" % n, "ALL", "ALL", "Section",
               slug=("longitudinal_section_centreline" if axis == "x" else "transverse_section_z%s" % ("%g" % c).replace("-", "m").replace(".", "p")))
    ox = (area[0] + area[2]) / 2 - (a + b) / 2 * s
    ybase = area[1] + 14 + (ymax - ymin) * s + (area[3] - area[1] - 50 - (ymax - ymin) * s) / 2
    sv = SV(s, ox, ybase, 0, ymin)
    sh.text(area[0] + 2, area[1] + 4, "SECTION A-A - %s" % title.upper(), 3.0, bold=True)
    sh.text(area[0] + 2, area[1] + 8.2, trunc(cut.label + "  -  " + desc, 330, 1.8), 1.8, fill="#555")
    p0, p1 = sv.xy(a, ymax), sv.xy(b, ymin)
    sh.clip_def("clipS", p0[0] - 0.5, p0[1] - 0.5, p1[0] - p0[0] + 1.0, p1[1] - p0[1] + 1.0)
    sh.open_g(clip="clipS")
    if sk:
        env = skin_beyond(sk, cut)
        if env:
            sh.poly(_poly_pts(sv, env), "hid")
    for f in beyond_fit:
        bp = f.beyond_poly(cut.T)
        sh.poly(_poly_pts(sv, bp), "hid")
    for poly in skin_polys:
        sh.poly(_poly_pts(sv, poly), "h", "#eef1f6")
    if sk:
        for d in ship.deck_ids:
            pl = sk.plan(ship.deck_y[d])
            iv = cut.iv(pl) if pl else None
            if iv:
                sh.line(*sv.xy(iv[0], ship.deck_y[d]), *sv.xy(iv[1], ship.deck_y[d]), "gg")
    for r in rooms:
        draw_room_section(sh, sv, cut, r, ship, cat, "beyond", depth_max=30.0)
    sids = [st["id"] for st in ship.stairs]
    if axis == "z":
        sids = [sid for sid in sids if any(t is not None and cut.iv(t.poly) for t in (ship.tower(sid, d) for d in ship.deck_ids))]
    if sids:
        draw_stairs_section(sh, sv, cut, ship, "beyond", handrail=True, only=sids)
    for r in rooms:
        draw_room_section(sh, sv, cut, r, ship, cat, "cut")
    if sids:
        draw_stairs_section(sh, sv, cut, ship, "cut", handrail=True, only=sids)
    for f in cut_fit:
        sh.poly(_poly_pts(sv, f.cut_poly(cut.T)), "m", "#cdd5e0")
    sh.close_g()
    for f in cut_fit:
        pts = _poly_pts(sv, f.cut_poly(cut.T))
        sh.text(sum(p[0] for p in pts) / len(pts), min(p[1] for p in pts) - 1.2, f.label.upper(), 1.5, "middle", bold=True, halo=True)
    # room names
    for r in sorted(rooms, key=lambda q: (q.deck, cut.iv(q.poly)[0])):
        iv = cut.iv(r.poly)
        cxp = sv.xy((iv[0] + iv[1]) / 2, 0)[0]
        wmm = (iv[1] - iv[0]) * s
        if wmm < 10:
            continue
        sh.text(cxp, sv.xy(0, r.y + r.h - 0.35)[1], trunc(r.name.upper(), wmm - 2, 1.9), 1.9, "middle", bold=True, halo=True)
    # level marks (left) and heights (right)
    xl = sv.xy(a, 0)[0] - 18
    for d in ship.deck_ids:
        y = ship.deck_y[d]
        sh.level_mark(xl, sv.xy(0, y)[1], "%s DECK %d" % (lv(y), d), 1.8, True)
    xr = sv.xy(b, 0)[0] + 6
    decks = sorted({r.deck for r in rooms}, reverse=True)
    ys = sorted({r.y for r in rooms})
    ylev = sorted({r.y for r in rooms} | {max(r.top for r in rooms if r.deck == d) for d in decks})
    yl = [sv.xy(0, v)[1] for v in ylev]
    if len(ylev) > 1:
        sh.chain_v(list(reversed(yl)), xr, [str(int(round((ylev[i + 1] - ylev[i]) * 1000))) for i in reversed(range(len(ylev) - 1))], ext_x=sv.xy(b, 0)[0] + 1)
    if len(ys) > 1:
        sh.dim_v(sv.xy(0, ys[-1])[1], sv.xy(0, ys[0])[1], xr + 9, "%d" % round((ys[-1] - ys[0]) * 1000), ext_x=sv.xy(b, 0)[0] + 1)
    if skin_polys:
        ky0 = min(y for p in skin_polys for h, y in p)
        ky1 = max(y for p in skin_polys for h, y in p)
        sh.dim_v(sv.xy(0, ky1)[1], sv.xy(0, ky0)[1], xr + 18, "SKIN %d" % round((ky1 - ky0) * 1000), ext_x=sv.xy(b, 0)[0] + 1)
    # bottom: overall skin width, then the widest deck row of rooms
    yb = sv.xy(0, ymin)[1] + 7
    if skin_polys:
        sa = min(h for p in skin_polys for h, y in p)
        sb_ = max(h for p in skin_polys for h, y in p)
        sh.dim_h(sv.xy(sa, 0)[0], sv.xy(sb_, 0)[0], yb, "SKIN %d" % round((sb_ - sa) * 1000), ext_y=sv.xy(0, ymin)[1] + 1)
        yb += 7
    if not skin_polys or abs(a - sa) > 0.5 or abs(b - sb_) > 0.5:        # a wider overall extent (nacelles in the plane)
        sh.dim_h(sv.xy(a, 0)[0], sv.xy(b, 0)[0], yb, "OVERALL %d" % round((b - a) * 1000), ext_y=sv.xy(0, ymin)[1] + 1)
        yb += 0
    best = None
    for d in decks:
        ivs = sorted(cut.iv(r.poly) for r in rooms if r.deck == d)
        span = ivs[-1][1] - ivs[0][0]
        if best is None or span > best[0]:
            best = (span, ivs)
    if best:
        pts = sorted({round(v, 3) for iv in best[1] for v in iv})
        if len(pts) > 1:
            xs = [sv.xy(p, 0)[0] for p in pts]
            sh.chain_h(xs, yb + 7, [str(int(round((pts[i + 1] - pts[i]) * 1000))) for i in range(len(pts) - 1)], ext_y=sv.xy(0, ymin)[1] + 1)
    # end labels
    sh.text(sv.xy(a, 0)[0], sv.xy(0, ymax)[1] - 3, cut.hmin_label(), 2.2, "start", bold=True)
    sh.text(sv.xy(b, 0)[0], sv.xy(0, ymax)[1] - 3, cut.hmax_label(), 2.2, "end", bold=True)
    if axis == "x" and ship.stairs:
        top = ship.deck_ids[0]
        st = ship.stairs[-1]
        t = ship.tower(st["id"], top)
        if t is not None:
            zs = (st["strip"][1] + st["strip"][3]) / 2
            x, y = sv.xy(zs, 0)[0], sv.xy(0, t.top)[1]
            sh.line(x, y - 2, x, y - 12, "f")
            sh.text(x, y - 13.5, "STBD STAIR TOWER BEYOND (flights / landings shaded)", 1.9, "middle", bold=True)
    sh.scalebar(area[2] - 70, area[3] - 4, s)
    ship_key_plan(sh, ship, cut, 14.0, 206.0, 118.0, 52.0)
    from sheets_room import section_legend
    section_legend(sh, 140.0, 212.0)
    sh.text(190.0, 212.0, "NOTES", 1.9, bold=True)
    notes = ["Heavy outline: outer skin cut by the plane; the hull sides lean outward with height.",
             "Thin dashed outline: skin and fittings behind the plane (looking %s)." % ("aft" if axis == "z" else "starboard"),
             "Grey horizontal lines: deck floor levels across the skin.",
             "Nacelles, deflector, masts, engines: boxes from arch.json bounds."]
    for k, t in enumerate(notes):
        sh.text(190.0, 216.5 + k * 3.6, t, 1.6, maxw=120)
    return sh
