"""General arrangement sheets: deck plans, hull lines, profile, ship sections."""
import math

from shipmodel import SLAB_T, line_interval, poly_area
from planview import (PV, draw_floor, draw_walls, draw_openings, draw_props, draw_holes, draw_stairs, draw_forcefields)
from sectionview import (SV, Cut, draw_room_section, draw_stairs_section, lv)
from svgkit import Sheet, nice_scale, text_w, trunc

GA_SCALE = 250

# (sheet number, axis, plane position, title, description)
SECTION_CUTS = [
    ("G-06", "x", 0.0, "Longitudinal section on centreline", "through corridors, stair lobby, bridge and hangar; starboard stair tower beyond"),
    ("G-07", "z", 1.8, "Transverse section A - stair lobby", "frame z=+1.8 m through lobby and BOTH stair towers (dog-leg flights)"),
    ("G-08", "z", -28.0, "Transverse section B - bridge", "frame z=-28 m through the bridge and armory / brig"),
    ("G-09", "z", -6.0, "Transverse section C - mess / medical / engineering", "frame z=-6 m through lounge, astro, mess, medbay, computer core and main engineering"),
    ("G-10", "z", 8.0, "Transverse section D - cabins row", "frame z=+8 m through officers' cabins, captain's quarters, recreation, science, workshop, power"),
    ("G-11", "z", 26.0, "Transverse section E - hangar bay", "frame z=+26 m through the 8 m high hangar bay"),
    ("G-12", "z", -18.0, "Transverse section F - forward rooms", "frame z=-18 m through ready room, conference, galley, security office, life support, airlock"),
]


def bow_z(ship):
    return min(p[1] for pts in ship.hull.values() for p in pts)


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
    words = name.upper().split()
    lines, cur = [], ""
    mx = max(6, int(avail / (0.54 * size)))
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= mx:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    lines = [trunc(l, avail, size) for l in lines[:2]]
    y = cy - 1.4 * (len(lines) - 1)
    for l in lines:
        sh.text(cx, y, l, size, "middle", bold=True, halo=True)
        y += 2.5
    sh.text(cx, y + 0.2, "%s  %.0f m2" % (room.code, room.area), 1.7, "middle", fill="#333", halo=True)


def station_grid(sh, pv, ship, xl, xr, deck):
    """Frame lines every 5 m measured from the bow of the ship (station 0 at the foremost point)."""
    z0 = bow_z(ship)
    hz0, hz1 = ship.bounds(deck)[1], ship.bounds(deck)[3]
    k = 0
    while z0 + 5 * k <= hz1 + 1e-6:
        z = z0 + 5 * k
        if z >= hz0 - 1e-6:
            y = pv.xy(0, z)[1]
            sh.line(xl, y, xr, y, "cl")
            sh.circ(xr + 3.0, y, 2.4, "f", "#fff")
            sh.text(xr + 3.0, y + .7, "%d" % (k * 5), 1.8, "middle", bold=True)
        k += 1


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
    sh.text(x + 10, y + 2.0, "Frame (station) every 5 m from bow", 1.8)
    return y + 5


def deck_ga(ship, deck):
    cat = ship.cat
    num = "G-%02d" % deck
    dname = ship.deck_name[deck]
    y0 = ship.deck_y[deck]
    sh = Sheet(num, "General arrangement - Deck %d (%s)" % (deck, dname),
               "DECK %d - %s - GENERAL ARRANGEMENT PLAN AT FFL %+.3f" % (deck, dname.upper(), y0), "1:%d" % GA_SCALE,
               "DECK %d" % deck, "ALL", "Deck %d" % deck,
               slug="general_arrangement_deck%d" % deck)
    s = 1000.0 / GA_SCALE
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    (14.0, 8.0, 232.0, 290.0)
    ox = 14 + 34 + 52 - 0          # plan centre line (x=0) on paper
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
    sh.text(14 + 4, pv.xy(0, hb0)[1] - 24, "FRAME GRID: m from bow (bow = station 0 at z = %.1f m)" % bz0, 1.6, fill="#555")
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
    facts = [("Floor level (FFL)", "%+.3f" % y0), ("Floor to floor", "4000 mm"), ("Hull area (deck)", "%.1f m2" % abs(poly_area(ship.hull[deck]))),
             ("Overall length", "%.1f m" % (hz1 - hz0)), ("Beam (max)", "%.1f m" % (hx1 - hx0)),
             ("Doors / arches", str(sum(1 for d in ship.door_list if d["deck"] == deck))),
             ("Windows", str(sum(1 for w in ship.win_list if w["deck"] == deck))),
             ("Props", str(sum(len(r.props) for r in rooms)))]
    y = sh.table(x, y + 2, [50, 58], facts, title="DECK PARTICULARS", rh=3.4, size=1.8)
    ga_symbol_key(sh, x, y + 8)
    return sh


# ------------------------------------------------------------------ hull lines
def half_breadth(poly, z):
    iv = line_interval(poly, 1, z)
    return None if iv is None else max(abs(iv[0]), abs(iv[1]))


def hull_lines(ship):
    sh = Sheet("G-04", "Hull lines plan", "HALF-BREADTH PLAN - THREE DECK OUTLINES SUPERIMPOSED", "1:300", "ALL", "HULL", "Hull lines",
               slug="hull_lines_plan")
    s = 1000.0 / 300
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    ox = 14 + 32 + 13 * s
    oy = 8 + 28 - bz0 * s
    pv = PV(s, ox, oy, 0, 0)
    styles = {1: ("m", "#dfe7f5"), 2: ("dsh", "none"), 3: ("n", "#eef0f2")}
    for d in (3, 2, 1):
        c, f = styles[d]
        sh.poly(pv.pts(ship.hull[d]), c, f, op=0.6 if f != "none" else None)
    # redraw deck1 outline heavy
    sh.poly(pv.pts(ship.hull[1]), "h")
    xl, xr = pv.xy(-14.5, 0)[0], pv.xy(14.5, 0)[0]
    z = bz0
    k = 0
    while z <= bz1 + 1e-6:
        y = pv.xy(0, z)[1]
        sh.line(xl, y, xr, y, "cl")
        sh.circ(xl - 3.2, y, 2.4, "f", "#fff")
        sh.text(xl - 3.2, y + .7, "%d" % (k * 5), 1.8, "middle", bold=True)
        z += 5
        k += 1
    sh.line(pv.xy(0, 0)[0], pv.xy(0, bz0)[1] - 8, pv.xy(0, 0)[0], pv.xy(0, bz1)[1] + 4, "cl")
    sh.text(pv.xy(0, 0)[0], pv.xy(0, bz0)[1] - 8.6, "CL", 1.8, "middle", bold=True)
    sh.dim_h(pv.xy(-13, 0)[0], pv.xy(13, 0)[0], pv.xy(0, bz0)[1] - 13, "BEAM 26000", ext_y=pv.xy(0, bz0)[1] - 2)
    sh.dim_v(pv.xy(0, bz0)[1], pv.xy(0, bz1)[1], pv.xy(-13, 0)[0] - 14, "LOA %d" % round((bz1 - bz0) * 1000), ext_x=pv.xy(-13, 0)[0] - 4)
    # labels of decks
    {1: "DECK 1 (bridge nose)", 2: "DECK 2", 3: "DECK 3 (hangar stern)"}
    for d in (1, 2, 3):
        b = ship.bounds(d)
        x, y = pv.xy(13.5 if d != 2 else 14.0, b[1] if d == 1 else (b[3] if d != 2 else b[3] - 2))
    sh.text(pv.xy(9, 0)[0], pv.xy(0, ship.bounds(1)[1])[1] - 1, "D1 nose", 1.7, bold=True)
    sh.text(pv.xy(9.5, 0)[0], pv.xy(0, ship.bounds(2)[1])[1] + 4, "D2 nose", 1.7, bold=True)
    sh.text(pv.xy(9.5, 0)[0], pv.xy(0, ship.bounds(3)[1])[1] + 4, "D3 nose", 1.7, bold=True)
    sh.text(pv.xy(9.5, 0)[0], pv.xy(0, ship.bounds(3)[3])[1] + 3.2, "D3 transom", 1.7, bold=True)
    # tables
    x = 195.0
    sh.bow_arrow(x + 12, 22)
    sh.scalebar(x + 40, 28, s)
    stations = []
    z = bz0
    while z <= bz1 + 1e-6:
        stations.append(z)
        z += 5
    rows = []
    for i, z in enumerate(stations):
        r = ["%d" % (i * 5), "%+.1f" % z]
        for d in (1, 2, 3):
            hb = half_breadth(ship.hull[d], z)
            r.append("-" if hb is None else "%d" % round(hb * 1000))
        rows.append(tuple(r))
    y = sh.table(x, 44, [22, 26, 40, 40, 40], rows, header=("STN m", "z m", "D1 HB mm", "D2 HB mm", "D3 HB mm"),
                 title="HALF-BREADTHS AT 5 m STATIONS (from bow)", rh=3.5, size=1.9)
    facts = []
    for d in (1, 2, 3):
        b = ship.bounds(d)
        facts.append(("DECK %d" % d, "%.1f" % (b[3] - b[1]), "%.1f" % (b[2] - b[0]), "%.1f" % abs(poly_area(ship.hull[d])), "%.1f" % b[1],
                      "%.1f" % b[3]))
    sh.table(x, y + 10, [22, 32, 28, 34, 26, 26], facts, header=("DECK", "LOA m", "BEAM m", "AREA m2", "BOW z", "STERN z"),
             title="PARTICULARS", rh=3.6, size=1.9)
    sh.text(x, y + 38, "Mid-body: parallel, 26 m beam, identical on all decks so the stair towers stack.", 1.8)
    sh.text(x, y + 42, "Deck 1 nose reaches furthest forward (bridge overhangs the bow);", 1.8)
    sh.text(x, y + 46, "Deck 3 reaches furthest aft (hangar forms a stern platform).", 1.8)
    return sh


# ------------------------------------------------------------------ profile
def union_intervals(iv):
    iv = sorted(iv)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def profile_sheet(ship):
    sh = Sheet("G-05", "Profile - starboard outboard elevation", "STARBOARD SIDE ELEVATION, BOW TO THE RIGHT", "1:200", "ALL", "PROFILE",
               "Profile", slug="profile_outboard_elevation")
    n = 200
    s = 1000.0 / n
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    # h = -z (bow right)
    h0 = -bz1
    ox = 14 + 30
    ybase = 140.0
    sv = SV(s, ox, ybase, h0, -0.6)
    # deck boxes per (y, top) group
    groups = {}
    for r in ship.rooms:
        groups.setdefault((r.y, r.top), []).append((r.z0, r.z1))
    {}
    for (y, top), ivs in sorted(groups.items()):
        for a, b in union_intervals(ivs):
            sh.poly(sv.box(-b, -a, y - SLAB_T, top + SLAB_T), "h", "#e9edf3")
    # slab lines
    for d in (1, 2, 3):
        y = ship.deck_y[d]
        b = ship.bounds(d)
        sh.line(*sv.xy(-b[3], y), *sv.xy(-b[1], y), "f")
        sh.line(*sv.xy(-b[3], y - SLAB_T), *sv.xy(-b[1], y - SLAB_T), "x")
    # windows on the starboard side
    for r in ship.rooms:
        for o in r.openings:
            if o["kind"] != "window":
                continue
            (p0, p1), e = r.opening_seg(o)
            if (p0[0] + p1[0]) / 2 < 1.0:
                continue
            sh.poly(sv.box(min(-p0[1], -p1[1]), max(-p0[1], -p1[1]), r.y + o["y0"], r.y + o["y1"]), "n", "url(#hGlass)")
    # hangar opening (stern forcefield) and labels
    hg = ship.by_id.get("hangar")
    if hg:
        sh.text(sv.xy(-(hg.z0 + hg.z1) / 2, 0)[0], sv.xy(0, hg.y + 4)[1], "HANGAR BAY (8.0 m clear)", 2.4, "middle", bold=True, halo=True)
    br = ship.by_id.get("bridge")
    if br:
        sh.text(sv.xy(-(br.z0 + br.z1) / 2, 0)[0], sv.xy(0, br.top + .6)[1] - 2, "BRIDGE (overhangs bow)", 2.0, "middle", bold=True)
    # deck level lines / marks
    for d in (1, 2, 3):
        y = ship.deck_y[d]
        sh.level_mark(ox - 20, sv.xy(0, y)[1], "%s  DECK %d" % (lv(y), d), 1.8, True)
        sh.line(ox - 10, sv.xy(0, y)[1], sv.xy(h0, 0)[0] - 1, sv.xy(0, y)[1], "cl")
    # frames along the bottom
    yb = sv.xy(0, -0.3)[1] + 3
    k = 0
    z = bz0
    while z <= bz1 + 1e-6:
        x = sv.xy(-z, 0)[0]
        sh.line(x, yb - 1.5, x, yb + 1.5, "m")
        sh.text(x, yb + 5, "%d" % (k * 5), 1.8, "middle")
        z += 5
        k += 1
    sh.line(sv.xy(-bz1, 0)[0], yb, sv.xy(-bz0, 0)[0], yb, "f")
    sh.text(sv.xy(-bz1, 0)[0], yb + 9, "FRAMES: metres from bow (right-hand end = station 0)", 1.7, fill="#555")
    sh.dim_h(sv.xy(-bz1, 0)[0], sv.xy(-bz0, 0)[0], yb + 14, "LOA %d" % round((bz1 - bz0) * 1000), ext_y=yb + 2)
    # heights on the right
    xr = sv.xy(-bz0, 0)[0] + 8
    [(ship.deck_y[d], max(r.top for r in ship.deck_rooms(d))) for d in (1, 2, 3)]
    ys = [sv.xy(0, v)[1] for v in (0.0, 4.0, 8.0)]
    sh.chain_v(list(reversed(ys)), xr, ["4000", "4000"], ext_x=sv.xy(-bz0, 0)[0] + 1)
    ymax = max(r.top for r in ship.rooms) + SLAB_T
    sh.dim_v(sv.xy(0, ymax)[1], sv.xy(0, -SLAB_T)[1], xr + 10, "OVERALL %d (keel to roof)" % round((ymax + SLAB_T) * 1000), ext_x=sv.xy(-bz0, 0)[0] + 1)
    # section markers
    ytop = sv.xy(0, ymax)[1] - 6
    for num, axis, c, title, desc in SECTION_CUTS:
        if axis == "z":
            x = sv.xy(-c, 0)[0]
            sh.line(x, ytop, x, sv.xy(0, -0.3)[1] + 2, "cut")
            sh.circ(x, ytop - 3.2, 3.0, "n", "#fff")
            sh.text(x, ytop - 2.6, num.replace("G-", ""), 1.8, "middle", bold=True)
    # bow arrow
    sh.arrow(sv.xy(-bz0, 0)[0] - 40, 40, sv.xy(-bz0, 0)[0] - 10, 40, "m", 2.2)
    sh.text(sv.xy(-bz0, 0)[0] - 8, 41, "BOW", 2.4, bold=True)
    sh.text(sv.xy(-bz1, 0)[0], 40, "STERN", 2.4, bold=True)
    sh.scalebar(ox, 240, s)
    sh.text(14 + 2, 14, "PROFILE - STARBOARD OUTBOARD ELEVATION", 3.0, bold=True)
    sh.text(14 + 2, 18.4, "Decks stacked at 0 / 4 / 8 m; stepped bow and stern terraces; window bands as built (starboard hull facets and side walls).", 1.8, fill="#555")
    # notes
    notes = ["Deck 1 (command): FFL +8.000, rooms 3.4 m (bridge 4.2 m, lounge 3.6 m).", "Deck 2 (habitat): FFL +4.000, rooms 3.4 m (3.6 m mess, medbay, hydroponics).",
             "Deck 3 (engineering): FFL +0.000, rooms 3.4 m; hangar 8.0 m clear height on the stern platform.", "Slabs 300 mm; walls 150 mm."]
    for i, t in enumerate(notes):
        sh.text(14 + 100, 190 + i * 4.2, t, 1.8)
    return sh


# ------------------------------------------------------------------ ship sections
def ship_key_plan(sh, ship, cut, x, y, w, h):
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    s = min((w - 14) / (bx1 - bx0), (h - 10) / (bz1 - bz0))
    ox = x + (w - (bx1 - bx0) * s) / 2
    oy = y + 7 + ((h - 10) - (bz1 - bz0) * s) / 2 - bz0 * s
    pv = PV(s, ox - bx0 * s, oy, 0, 0)
    sh.rect(x, y, w, h, "f")
    sh.text(x + 1.5, y + 3.2, "KEY PLAN (all decks)", 1.8, bold=True)
    for d, f in ((3, "#f4f4f4"), (2, "#ececec"), (1, "#e2e6ee")):
        sh.poly(pv.pts(ship.hull[d]), "f", f)
    if cut.axis == "x":
        a, b = pv.xy(cut.c, bz0 - 3), pv.xy(cut.c, bz1 + 3)
    else:
        a, b = pv.xy(bx0 - 3, cut.c), pv.xy(bx1 + 3, cut.c)
    sh.line(*a, *b, "cut")
    for p in (a, b):
        sh.circ(p[0], p[1], 2.0, "n", "#fff")
        sh.text(p[0], p[1] + .6, "A", 1.8, "middle", bold=True)
    sh.text(x + w - 2, y + 3.2, "BOW", 1.6, "end", bold=True)
    sh.poly([(x + w - 4, y + 4.5), (x + w - 2.6, y + 8), (x + w - 5.4, y + 8)], "f", "#111")


def ship_section(ship, entry, pv_scale=None):
    num, axis, c, title, desc = entry
    cat = ship.cat
    cut = Cut(axis, c)
    rooms = [r for r in ship.rooms if cut.iv(r.poly)]
    a = min(cut.iv(r.poly)[0] for r in rooms)
    b = max(cut.iv(r.poly)[1] for r in rooms)
    ymin = min(r.y for r in rooms) - SLAB_T
    ymax = max(r.top for r in rooms) + SLAB_T
    area = (14.0, 8.0, 410.0, 200.0)
    n = nice_scale(area[2] - area[0] - 52, area[3] - area[1] - 50, b - a, ymax - ymin, options=(50, 75, 100, 150, 200, 250))
    s = 1000.0 / n
    sh = Sheet(num, title, "SECTION A-A %s at %s = %+.2f m - %s" % (cut.label, axis, c, desc), "1:%d" % n, "ALL", "ALL", "Section",
               slug=("longitudinal_section_centreline" if axis == "x" else "transverse_section_z%s" % ("%g" % c).replace("-", "m").replace(".", "p")))
    ox = (area[0] + area[2]) / 2 - (a + b) / 2 * s
    ybase = area[1] + 14 + (ymax - ymin) * s + (area[3] - area[1] - 50 - (ymax - ymin) * s) / 2
    sv = SV(s, ox, ybase, 0, ymin)
    sh.text(area[0] + 2, area[1] + 4, "SECTION A-A - %s" % title.upper(), 3.0, bold=True)
    sh.text(area[0] + 2, area[1] + 8.2, cut.label + "  -  " + desc, 1.8, fill="#555")
    p0, p1 = sv.xy(a, ymax), sv.xy(b, ymin)
    sh.clip_def("clipS", p0[0] - 0.5, p0[1] - 0.5, p1[0] - p0[0] + 1.0, p1[1] - p0[1] + 1.0)
    sh.open_g(clip="clipS")
    for r in rooms:
        draw_room_section(sh, sv, cut, r, ship, cat, "beyond", depth_max=30.0)
    if axis == "x":
        sids = [st["id"] for st in ship.stairs]            # towers beyond the plane are shown for location
    else:
        sids = [st["id"] for st in ship.stairs if cut.iv(ship.by_id["tower%s%d" % (st["id"][1], 1)].poly)]
    draw_stairs_section(sh, sv, cut, ship, "beyond", handrail=True, only=sids)
    for r in rooms:
        draw_room_section(sh, sv, cut, r, ship, cat, "cut")
    draw_stairs_section(sh, sv, cut, ship, "cut", handrail=True, only=sids)
    sh.close_g()
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
    for d in (1, 2, 3):
        y = ship.deck_y[d]
        sh.level_mark(xl, sv.xy(0, y)[1], "%s DECK %d" % (lv(y), d), 1.8, True)
    xr = sv.xy(b, 0)[0] + 6
    decks = sorted({r.deck for r in rooms}, reverse=True)
    ys = sorted({r.y for r in rooms})
    for r in rooms:
        pass
    ylev = sorted({r.y for r in rooms} | {max(r.top for r in rooms if r.deck == d) for d in decks})
    yl = [sv.xy(0, v)[1] for v in ylev]
    if len(ylev) > 1:
        sh.chain_v(list(reversed(yl)), xr, [str(int(round((ylev[i + 1] - ylev[i]) * 1000))) for i in reversed(range(len(ylev) - 1))], ext_x=sv.xy(b, 0)[0] + 1)
    if len(ys) > 1:
        sh.dim_v(sv.xy(0, ys[-1])[1], sv.xy(0, ys[0])[1], xr + 9, "%d" % round((ys[-1] - ys[0]) * 1000), ext_x=sv.xy(b, 0)[0] + 1)
    # bottom: overall
    yb = sv.xy(0, ymin)[1] + 7
    sh.dim_h(sv.xy(a, 0)[0], sv.xy(b, 0)[0], yb, "%d" % round((b - a) * 1000), ext_y=sv.xy(0, ymin)[1] + 1)
    # bottom deck chain: room widths of the widest deck row
    drow = min(decks) if decks else 3
    ivs = sorted(cut.iv(r.poly) for r in rooms if r.deck == drow)
    pts = sorted({round(v, 3) for iv in ivs for v in iv})
    if len(pts) > 1:
        xs = [sv.xy(p, 0)[0] for p in pts]
        sh.chain_h(xs, yb + 7, [str(int(round((pts[i + 1] - pts[i]) * 1000))) for i in range(len(pts) - 1)], ext_y=sv.xy(0, ymin)[1] + 1)
    # end labels
    sh.text(sv.xy(a, 0)[0], sv.xy(0, ymax)[1] - 3, cut.hmin_label(), 2.2, "start", bold=True)
    sh.text(sv.xy(b, 0)[0], sv.xy(0, ymax)[1] - 3, cut.hmax_label(), 2.2, "end", bold=True)
    if axis == "x":
        # note where the stair tower beyond is
        sb = [st for st in ship.stairs if st["id"] == "SB"]
        if sb:
            zs = (sb[0]["strip"][1] + sb[0]["strip"][3]) / 2
            x, y = sv.xy(zs, 0)[0], sv.xy(0, ship.deck_y[1] + ship.by_id["towerB1"].h)[1]
            sh.line(x, y - 2, x, y - 12, "f")
            sh.text(x, y - 13.5, "STBD STAIR TOWER BEYOND (flights / landings shaded)", 1.9, "middle", bold=True)
    sh.scalebar(area[2] - 70, area[3] - 4, s)
    ship_key_plan(sh, ship, cut, 14.0, 206.0, 70.0, 84.0)
    from sheets_room import section_legend
    section_legend(sh, 90.0, 212.0)
    return sh
