"""Stair tower detail, circulation / escape, schedules, index and contact sheets."""
import heapq
import math

from shipmodel import SLAB_T, PITCH
from planview import PV, draw_floor, draw_walls, draw_openings, draw_holes, draw_stairs
from sectionview import SV, Cut, draw_room_section, draw_stairs_section, lv
from svgkit import Sheet


# ------------------------------------------------------------------ G-13 stairs
def stair_sheet(ship):
    sh = Sheet("G-13", "Stair tower details", "DOG-LEG STAIR TOWER: PLANS AT EACH LEVEL, SECTION ALONG THE FLIGHTS, TREAD / RISER DETAIL",
               "1:50 / 1:75 / 1:10", "ALL", "SP / SS", "Stair tower", slug="stair_tower_details")
    cat = ship.cat
    runs, st = ship.stair_geom("SA")
    # ---------------- section along lane A (z = 0.85)
    zc = runs[0]["flights"][0]["z"]
    cut = Cut("z", zc)
    s = 1000.0 / 50
    towers = [ship.by_id["towerA%d" % d] for d in (1, 2, 3)]
    a = min(cut.iv(r.poly)[0] for r in towers)
    b = max(cut.iv(r.poly)[1] for r in towers)
    ymin, ymax = -SLAB_T, ship.deck_y[1] + towers[0].h + SLAB_T
    ox = 14 + 26 - a * s
    sv = SV(s, ox, 0, 0, ymin)
    sv.oy = 12 + 16 + (ymax - ymin) * s
    sh.text(16, 15, "SECTION B-B - ALONG THE FLIGHTS (lane A)  1:50", 2.8, bold=True)
    sh.text(16, 19, "Cut at z = %.2f m looking aft; port tower, all three levels" % zc, 1.6, fill="#555")
    sh.open_g()
    for r in towers:
        draw_room_section(sh, sv, cut, r, ship, cat, "beyond", depth_max=6.0)
    draw_stairs_section(sh, sv, cut, ship, "beyond", handrail=True, only=["SA"])
    for r in towers:
        draw_room_section(sh, sv, cut, r, ship, cat, "cut")
    draw_stairs_section(sh, sv, cut, ship, "cut", handrail=True, only=["SA"])
    sh.close_g()
    # level marks
    sv.xy(a, 0)[0] - 4
    for d in (1, 2, 3):
        y = ship.deck_y[d]
        sh.level_mark(sv.xy(a, 0)[0] - 22, sv.xy(0, y)[1], lv(y), 1.8, True)
    for rn in runs:
        sh.level_mark(sv.xy(a, 0)[0] - 22, sv.xy(0, rn["landing_y"])[1], lv(rn["landing_y"]) + " LDG", 1.6, True)
    # dimensions on flight A of the lowest run
    f = runs[0]["flights"][0]
    r_ = f["rise"] / f["n"]
    xe = f["x"] + f["dir"] * f["tread"] * (f["n"] - 1)
    # rise chain (vertical) at the landing side
    sv.xy(-xe, 0)[0] + (6 if f["dir"] < 0 else -6)
    sh.dim_v(sv.xy(0, f["y"])[1], sv.xy(0, f["y"] + f["rise"])[1], sv.xy(-xe, 0)[0] - 7, "%d R @ 181.8 = %d" % (f["n"], round(f["rise"] * 1000)),
             ext_x=sv.xy(-xe, 0)[0] - 0.5)
    # going chain horizontal below the flight
    yb = sv.xy(0, 0)[1] + 8
    sh.dim_h(sv.xy(-f["x"], 0)[0], sv.xy(-xe, 0)[0], yb, "%d G @ %d = %d" % (f["n"] - 1, round(f["tread"] * 1000), round(f["tread"] * (f["n"] - 1) * 1000)),
             ext_y=sv.xy(0, 0)[1] + 1)
    # headroom above flight A (3,2): up to underside of flight above
    k = 5
    xk = f["x"] + f["dir"] * f["tread"] * k
    y_low = f["y"] + (k + 1) * r_
    f2 = runs[1]["flights"][0]
    y_up = f2["y"] + (k + 1) * r_ - 0.24
    sh.dim_v(sv.xy(0, y_low)[1], sv.xy(0, y_up)[1], sv.xy(-xk, 0)[0] + 5, "HEADROOM %d (min 2000)" % round((y_up - y_low) * 1000), ext_x=sv.xy(-xk, 0)[0] + 0.3)
    # handrail height
    y_h0 = f["y"] + (k + 1) * r_
    sh.dim_v(sv.xy(0, y_h0)[1], sv.xy(0, y_h0 + 0.9)[1], sv.xy(-xk, 0)[0] - 4, "HANDRAIL 900", ext_x=sv.xy(-xk, 0)[0] - 0.3)
    # slab opening dimensions on deck 2 floor
    holes = towers[1].floor_holes
    if holes:
        hx0, hx1 = holes[0][0], holes[0][2]
        yy = sv.xy(0, ship.deck_y[2])[1] - 9
        sh.dim_h(sv.xy(-hx1, 0)[0], sv.xy(-hx0, 0)[0], yy, "SLAB OPENING %d" % round((hx1 - hx0) * 1000), ext_y=sv.xy(0, ship.deck_y[2])[1] - 0.5)
    # whole storey: 2 x 11 risers
    runs[1]["flights"][0]
    sh.dim_v(sv.xy(0, ship.deck_y[2])[1], sv.xy(0, ship.deck_y[2] + PITCH)[1], sv.xy(b, 0)[0] + 7, "22 R @ 181.8 = 4000 (2 flights)",
             ext_x=sv.xy(b, 0)[0] + 1)
    # landing labels
    lr = runs[0]["landing"]
    sh.text(sv.xy(-(lr[0] + lr[2]) / 2, 0)[0], sv.xy(0, runs[0]["landing_y"])[1] - 3, "MID-LANDING", 1.6, "middle", bold=True)
    sh.text(sv.xy(a, 0)[0], sv.xy(0, ymax)[1] - 3, "STBD side / hull", 1.6, "start")
    sh.text(sv.xy(b, 0)[0], sv.xy(0, ymax)[1] - 3, "lobby side", 1.6, "end")
    sh.scalebar(14 + 26, 287, s)
    # ---------------- plans
    ps = 1000.0 / 75
    cells = [(3, 182.0, 14.0), (2, 182.0, 92.0), (1, 182.0, 170.0)]
    for d, cx0, cy0 in cells:
        r = ship.by_id["towerA%d" % d]
        pv = PV(ps, cx0 + 14 - r.x0 * ps, cy0 + 16 - r.z0 * ps, 0, 0)
        sh.text(cx0, cy0 + 3, "PLAN - DECK %d LEVEL (FFL %+.3f)  1:75" % (d, r.y), 2.3, bold=True)
        draw_floor(sh, pv, r, k=0.7)
        draw_holes(sh, pv, r)
        draw_stairs(sh, pv, ship, d, only_side="SA")
        draw_walls(sh, pv, r)
        draw_openings(sh, pv, r)
        x0p, y0p = pv.xy(r.x0, r.z0)
        x1p, y1p = pv.xy(r.x1, r.z1)
        sh.dim_h(x0p, x1p, y0p - 6, "%d" % round(r.w * 1000), ext_y=y0p - 1)
        sh.dim_v(y0p, y1p, x1p + 8, "%d" % round(r.dd * 1000), ext_x=x1p + 1)
        g0 = runs[0]["flights"][0]
        sh.dim_h(pv.xy(g0["x"], 0)[0], pv.xy(g0["x"] + g0["dir"] * g0["tread"] * (g0["n"] - 1), 0)[0], y1p + 6,
                 "10 x 280 = 2800", ext_y=y1p + 0.5)
        sh.dim_v(pv.xy(0, g0["z"] - 0.7)[1], pv.xy(0, g0["z"] + 0.7)[1], x1p + 16, "1400 flight", ext_x=x1p + 9)
        sh.text(x0p + 1, y1p + 11.5, {3: "Flight A rises to mid-landing +2.000; flight B returns to the deck-2 strip.",
                                      2: "UP: flight A to +6.000 landing; DN: flight B arrives from +2.000 landing.",
                                      1: "DN only: flight B arrives from the +6.000 landing; hull-side wall on the left."}[d], 1.5, fill="#555")
    # ---------------- detail A: tread / riser at 1:10
    x0, y0 = 304.0, 16.0
    sh.text(x0, y0, "DETAIL A - TREAD / RISER  1:10", 2.3, bold=True)
    ds = 100.0
    r_m, g_m = PITCH / 22.0, 0.28
    px, py = x0 + 10, y0 + 72
    pts = [(px, py)]
    for k in range(3):
        pts.append((px + k * g_m * ds, py - (k + 1) * r_m * ds))
        pts.append((px + (k + 1) * g_m * ds, py - (k + 1) * r_m * ds))
    pts += [(px + 3 * g_m * ds, py - 3 * r_m * ds), (px + 3 * g_m * ds, py - 3 * r_m * ds - 0.24 * ds), (px, py - 0.0)]
    sh.poly(pts, "m", "url(#hSlab)")
    sh.dim_v(py - 2 * r_m * ds, py - r_m * ds, px + 3 * g_m * ds + 8, "181.8 RISER", ext_x=px + 2 * g_m * ds + 0.5)
    sh.dim_h(px + g_m * ds, px + 2 * g_m * ds, py - 3 * r_m * ds - 4, "280 GOING", ext_y=py - 2 * r_m * ds - 0.5)
    ang = math.degrees(math.atan2(r_m, g_m))
    sh.text(px + 10, py + 6, "Pitch %.1f deg   2R + G = %.0f mm (comfort 550-700)" % (ang, 2 * r_m * 1000 + 280), 1.7)
    sh.text(px + 10, py + 10, "Waist (slab) thickness 240 mm measured vertically.", 1.7)
    # ---------------- stair data table
    data = [("Floor to floor", "4000 mm (2 x 2000 half-flights)"), ("Risers", "22 per storey: 11 + 11"), ("Riser height", "181.8 mm (4000 / 22)"),
            ("Going (tread)", "280 mm; 10 goings / flight + landing"), ("Flight width", "1400 mm clear"),
            ("Going length", "2800 mm (11 risers: 10 goings)"), ("Handrails", "900 mm above nosing, both sides"),
            ("Headroom", "3760 mm (stacked flights 4000 - 240)"), ("Mid-landing", "+2.000 / +6.000 (1420 x 3300 mm)"),
            ("Deck strip", "1800 mm at each landing level"), ("Slab openings", "3 per slab: 2 flight lanes + landing"),
            ("Escape", "2 towers (port / starboard), 3.2 m arches")]
    sh.table(x0, 100, [30, 79], data, title="STAIR DATA", rh=3.6, size=1.8, bold_first=True)
    notes = ["Geometry follows ship.json stairs[] (flights, landings, strip)", "and matches blender/starship/arch.py (arch_stair_flight).",
             "Dashed lines: flights above the plan cut plane (+1.2 m);", "thin solid lines: flights below the cut plane."]
    for i, t in enumerate(notes):
        sh.text(x0, 158 + i * 4, t, 1.6)
    return sh


# ------------------------------------------------------------------ G-14 circulation
def door_point(room, o):
    (p0, p1), e = room.opening_seg(o)
    return ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)


def escape_graph(ship, deck):
    """Dijkstra from the stair strips; returns (dist, prev, pos) over nodes."""
    pos, adj = {}, {}

    def node(k, p):
        pos[k] = p
        adj.setdefault(k, [])

    def edge(a, b):
        d = math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])
        adj[a].append((b, d))
        adj[b].append((a, d))

    rooms = ship.deck_rooms(deck)
    dpts = {}
    for r in rooms:
        node("c:" + r.id, (r.cx, r.cz))
        for lk in r.links:
            o = next((x for x in r.openings if x["side"] == lk["side"] and abs(x["c"] - lk["c"]) < 1e-3 and x["kind"] != "window"), None)
            if o is None:
                continue
            key = "d:" + "|".join(sorted((r.id, lk["to"]))) + "|%.2f" % lk["c"]
            node(key, door_point(r, o))
            dpts.setdefault(r.id, []).append(key)
    for r in rooms:
        ks = dpts.get(r.id, [])
        for k in ks:
            edge("c:" + r.id, k)
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                edge(ks[i], ks[j])
    src = []
    for st in ship.stairs:
        strip = st["strip"]
        k = "s:" + st["id"]
        node(k, ((strip[0] + strip[2]) / 2, (strip[1] + strip[3]) / 2))
        tower = ship.by_id["tower%s%d" % (st["id"][1], deck)]
        for dk in dpts.get(tower.id, []):
            edge(k, dk)
        edge(k, "c:" + tower.id)
        src.append(k)
    dist = {k: 1e9 for k in pos}
    prev = {}
    pq = []
    for k in src:
        dist[k] = 0.0
        heapq.heappush(pq, (0.0, k))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v] - 1e-9:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(pq, (d + w, v))
    return dist, prev, pos


BANDS = [(15.0, "#c4e8c6", "0 - 15 m"), (30.0, "#f4e8a8", "15 - 30 m"), (45.0, "#f6c896", "30 - 45 m"), (1e9, "#f3a4a4", "> 45 m")]


def band_color(d):
    for lim, col, _ in BANDS:
        if d <= lim:
            return col
    return BANDS[-1][1]


def circulation_sheet(ship):
    sh = Sheet("G-14", "Circulation and escape diagram", "TRAVEL DISTANCE FROM EACH ROOM CENTRE TO THE NEAREST STAIR (via doors, straight legs)",
               "1:400", "ALL", "ALL", "Escape", slug="circulation_escape_diagram")
    s = 1000.0 / 400
    bx0, bz0, bx1, bz1 = ship.bounds(None)
    results = []
    for k, d in enumerate((1, 2, 3)):
        dist, prev, pos = escape_graph(ship, d)
        hb = ship.bounds(d)
        x0 = 20 + k * 82
        pv = PV(s, x0 + 32.5 - 0, 30 - hb[1] * s + 12, 0, 0)
        pv.ox = x0 + 32
        sh.text(x0, 22, "DECK %d" % d, 3.0, bold=True)
        rooms = ship.deck_rooms(d)
        for r in rooms:
            dd = dist.get("c:" + r.id, 1e9)
            sh.poly(pv.pts(r.poly), "f", band_color(dd) if not r.id.startswith("tower") else "#9fc6ee")
        for r in rooms:
            draw_walls(sh, pv, r)
            draw_openings(sh, pv, r)
        sh.poly(pv.pts(ship.hull[d]), "m")
        draw_stairs(sh, pv, ship, d)
        # routes
        for r in rooms:
            k0 = "c:" + r.id
            if dist.get(k0, 1e9) > 1e8 or r.id.startswith("tower"):
                continue
            path = [k0]
            while path[-1] in prev:
                path.append(prev[path[-1]])
            pts = [pv.xy(*pos[q]) for q in path]
            sh.poly(pts, "red", close=False)
            if len(pts) > 1:
                sh.arrow(pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1], "none", 1.4, "#b03030")
        for r in rooms:
            cx, cy = pv.xy(r.cx, r.cz)
            dd = dist.get("c:" + r.id, 1e9)
            if r.id.startswith("tower"):
                sh.text(cx, cy + .7, "STAIR", 1.6, "middle", bold=True)
            else:
                sh.circ(cx, cy, 0.7, "n", "#b03030")
                r.w * s
                sh.text(cx, cy - 1.2, r.code, 1.6, "middle", bold=True, halo=True)
                sh.text(cx, cy + 2.2, "%.0f m" % dd, 1.6, "middle", halo=True)
            results.append((d, r, dd))
        sh.text(x0 + 2, 255, "max %.0f m" % max(v for dd_, r, v in results if dd_ == d and not r.id.startswith("tower")), 2.0, bold=True)
    # legend + table
    x = 272.0
    sh.bow_arrow(x + 10, 20)
    sh.text(x + 28, 14, "ESCAPE TRAVEL BANDS", 2.2, bold=True)
    for i, (lim, col, lab) in enumerate(BANDS):
        sh.rect(x + 28, 17 + i * 4.6, 8, 3, "n", col)
        sh.text(x + 38, 19.6 + i * 4.6, lab, 1.8)
    sh.line(x + 28, 37, x + 36, 37, "red")
    sh.text(x + 38, 37.7, "escape route to stair", 1.8)
    rows = [("D%d" % d, r.code, r.name, "%.1f" % v) for d, r, v in sorted(results, key=lambda t: (t[0], -t[2])) if not r.id.startswith("tower")]
    sh.table(x, 48, [10, 13, 54, 16], rows[:40], header=("DK", "CODE", "ROOM", "DIST m"), title="TRAVEL DISTANCE TO NEAREST STAIR", rh=3.0, size=1.6,
             maxrows=40)
    sh.text(14 + 6, 268, "Two stair towers per deck (port / starboard); distance = shortest path centre -> door -> ... -> stair strip.", 1.7, fill="#444")
    sh.text(14 + 6, 272, "Furniture is not considered; every room has one door to a spine corridor.", 1.7, fill="#444")
    return sh


# ------------------------------------------------------------------ G-15 schedules
def schedule_sheet(ship):
    sh = Sheet("G-15", "Door and window schedule", "DOORS / ARCHES (D-marks on plans) AND WINDOWS (W-marks)", "NTS", "ALL", "ALL", "Schedules",
               slug="door_window_schedule")
    rows = []
    for d in ship.door_list:
        a, b = ship.by_id[d["a"]], ship.by_id[d["b"]]
        kind = {"door": "sliding door", "portal": "portal arch", "open": "open arch"}.get(d["kind"], d["kind"])
        rows.append((d["mark"], "D%d" % d["deck"], a.code, b.code, kind, "%d" % round(d["w"] * 1000), "%d" % round(d["h"] * 1000), d["model"]))
    sh.text(14 + 2, 14, "DOOR SCHEDULE (%d openings)" % len(rows), 2.6, bold=True)
    per = 67
    cw = [11, 9, 11, 11, 25, 12, 12, 52]
    hdr = ("MARK", "DECK", "FROM", "TO", "TYPE", "W mm", "H mm", "MODEL")
    x = 16.0
    sh.table(x, 20, cw, rows[:per], header=hdr, rh=3.45, size=1.7, bold_first=True)
    if len(rows) > per:
        sh.table(x + sum(cw) + 4, 20, cw, rows[per:2 * per], header=hdr, rh=3.45, size=1.7, bold_first=True)
    wrows = []
    for w in ship.win_list:
        r = ship.by_id[w["room"]]
        area = w["w"] * (w["head"] - w["sill"])
        wrows.append((w["mark"], "D%d" % w["deck"], r.code, w["side"], "%d" % round(w["w"] * 1000), "%d" % round(w["sill"] * 1000),
                      "%d" % round(w["head"] * 1000), "%.2f" % area))
    x2 = 16.0 + (sum(cw) + 4) * (2 if len(rows) > per else 1) + 2
    x2 = max(x2, 242.0)
    sh.text(x2, 14, "WINDOW SCHEDULE (%d panes)" % len(wrows), 2.6, bold=True)
    sh.table(x2, 20, [22, 9, 11, 10, 14, 12, 12, 13], wrows[:46], header=("MARK", "DECK", "ROOM", "WALL", "W mm", "SILL", "HEAD", "AREA m2"),
             rh=3.45, size=1.7, bold_first=True, maxrows=46)
    sh.text(x2, 20 + 3.45 * 48 + 6, "Doors: 2.36 m wide wall cut, head 2.76 m (catalog sliding door models).", 1.6, fill="#444")
    sh.text(x2, 20 + 3.45 * 48 + 10, "Arches: 3.0 - 4.0 m wide, head 3.0 - 3.2 m. Windows only on hull-exposed walls.", 1.6, fill="#444")
    return sh


# ------------------------------------------------------------------ G-16 index / legend
def index_sheet(ship, ga_list):
    sh = Sheet("G-16", "Drawing index, legend and symbols", "SHEET INDEX, LINE WEIGHTS, HATCHES, SYMBOLS AND FURNITURE FAMILY COLOURS", "NTS", "ALL", "ALL", "Index",
               slug="drawing_index_legend_symbols")
    rows = [(n, t, sc) for n, t, sc in ga_list]
    y = sh.table(16, 20, [14, 74, 20], rows, header=("SHEET", "TITLE", "SCALE"), title="GENERAL ARRANGEMENT SHEETS", rh=3.4, size=1.8, bold_first=True)
    nroom = len(ship.rooms)
    sh.text(16, y + 6, "Room sheets: R-<roomid>-P plan, R-<roomid>-SL longitudinal section, R-<roomid>-ST transverse section", 1.7)
    sh.text(16, y + 10, "%d rooms x 3 sheets (see INDEX.md for the complete list, grouped by deck)." % nroom, 1.7)
    sh.text(16, y + 14, "Contact sheets K-01..K-03 show all room plans of a deck as thumbnails.", 1.7)
    # line weights
    x = 135.0
    sh.text(x, 18, "LINE WEIGHTS", 2.3, bold=True)
    lw = [("h", "Hull / sheet border 0.50"), ("m", "Cut furniture, door jambs 0.25"), ("n", "Room outlines, furniture 0.18"),
          ("f", "Furniture detail 0.13"), ("x", "Fine detail 0.07"), ("d", "Dimension line 0.10"), ("dsh", "Dashed: slab openings, arches"),
          ("dot", "Dotted: ceiling items"), ("hid", "Hidden / above cut plane"), ("cl", "Frame / centre line"), ("cut", "Section line")]
    for i, (c, t) in enumerate(lw):
        yy = 23 + i * 4.4
        sh.line(x, yy, x + 18, yy, c)
        sh.text(x + 21, yy + 0.7, t, 1.7)
    # hatches
    y2 = 23 + len(lw) * 4.4 + 6
    sh.text(x, y2, "HATCHES (SECTIONS / PLANS)", 2.3, bold=True)
    hat = [("#1c1c1c", "Cut wall, 150 mm"), ("url(#hHull)", "Cut hull wall"), ("url(#hSlab)", "Cut slab 300 mm / stair"),
           ("url(#hHole)", "Slab opening (plan)"), ("url(#hZone)", "Reserved clearance zone"), ("url(#hGlass)", "Glazing"), ("url(#hPlen)", "Plenum / service void")]
    for i, (f, t) in enumerate(hat):
        yy = y2 + 3 + i * 5
        sh.rect(x, yy, 18, 3.6, "n", f)
        sh.text(x + 21, yy + 2.7, t, 1.7)
    # symbols
    x3 = 230.0
    sh.text(x3, 18, "PLAN SYMBOLS", 2.3, bold=True)
    yy = 24
    sh.rect(x3, yy, 14, 3, "m", "#fff")
    sh.line(x3 + 0.6, yy + 1.5, x3 + 7, yy + 1.5, "dsh")
    sh.poly([(x3 + 7, yy + .9), (x3 + 14, yy + .9), (x3 + 14, yy + 2.1), (x3 + 7, yy + 2.1)], "f", "#7a8594")
    sh.text(x3 + 17, yy + 2.2, "Sliding door: leaf parked beside the opening", 1.7)
    yy += 6
    for t in (0, .5, 1):
        sh.line(x3, yy + t * 2.4, x3 + 14, yy + t * 2.4, "n")
    sh.text(x3 + 17, yy + 2.0, "Window: frame, glass, frame", 1.7)
    yy += 6
    sh.line(x3, yy + 1.2, x3 + 14, yy + 1.2, "dsh")
    sh.circ(x3, yy + 1.2, .5, "f", "#111")
    sh.circ(x3 + 14, yy + 1.2, .5, "f", "#111")
    sh.text(x3 + 17, yy + 2.0, "Open arch / portal frame", 1.7)
    yy += 6
    sh.rect(x3, yy, 14, 4, "n", "#dde6f5")
    sh.line(x3, yy + 4, x3 + 14, yy + 4, "m")
    sh.text(x3 + 17, yy + 2.6, "Furniture footprint, heavy front edge + tick", 1.7)
    yy += 7
    sh.rect(x3, yy, 14, 1.2, "f", "#5a5a64")
    sh.text(x3 + 17, yy + 1.6, "Wall-mounted item (bar on the wall face)", 1.7)
    yy += 5
    sh.rect(x3, yy, 14, 3.4, "dot")
    sh.text(x3 + 17, yy + 2.4, "Ceiling item (dotted)", 1.7)
    yy += 6
    sh.rect(x3, yy, 14, 4, "red", "url(#hZone)")
    sh.text(x3 + 17, yy + 2.8, "Reserved clearance / door swing zone", 1.7)
    yy += 7
    sh.balloon(x3 + 4, yy + 2, "BR-03", 3.3)
    sh.text(x3 + 17, yy + 2.6, "BOM balloon: code of the bill-of-materials line", 1.7)
    yy += 8
    sh.arrow(x3, yy + 1.5, x3 + 12, yy + 1.5, "f", 1.4)
    sh.text(x3 + 17, yy + 2.0, "UP / DN stair arrow", 1.7)
    yy += 6
    sh.level_mark(x3 + 4, yy + 3, "+4.000", 1.7, True)
    sh.text(x3 + 17, yy + 2.6, "Level mark (m above keel datum)", 1.7)
    yy += 7
    sh.line(x3, yy + 2, x3 + 14, yy + 2, "d")
    sh.tick(x3, yy + 2)
    sh.tick(x3 + 14, yy + 2)
    sh.text(x3 + 7, yy + 1.3, "2360", 1.7, "middle")
    sh.text(x3 + 17, yy + 2.6, "Dimension (mm)", 1.7)
    # family colours
    cats = ship.cat.cats
    x4 = 16.0
    y4 = 192.0
    sh.text(x4, y4, "FURNITURE FAMILY COLOURS (catalog category)", 2.3, bold=True)
    per_col = 24
    colw = 38
    for i, c in enumerate(cats):
        col, row = i // per_col, i % per_col
        xx, yy = x4 + col * colw, y4 + 3 + row * 0
    # lay out as grid of 11 columns x rows
    ncol = 10
    for i, c in enumerate(cats):
        col, row = i % ncol, i // ncol
        xx, yy = x4 + col * 40, y4 + 3 + row * 3.6
        sh.rect(xx, yy, 4, 2.4, "n", ship.cat.color[c])
        sh.text(xx + 5.2, yy + 1.9, c, 1.5, maxw=34)
    return sh


# ------------------------------------------------------------------ contact sheets
def contact_sheet(ship, deck, files):
    """files: room id -> relative file name of the plan sheet (SVG)."""
    k = deck
    sh = Sheet("K-%02d" % k, "Contact sheet - Deck %d room plans" % deck, "%s - THUMBNAILS OF EVERY ROOM PLAN SHEET" % ship.deck_name[deck].upper(),
               "NTS", "DECK %d" % deck, "ALL", "Contact sheet deck %d" % deck, slug="contact_sheet_deck%d" % deck)
    rooms = ship.deck_rooms(deck)
    cols = 5
    tw, th = 76.0, 76.0 * 297 / 420
    x0, y0 = 16.0, 14.0
    for i, r in enumerate(rooms):
        col, row = i % cols, i // cols
        x, y = x0 + col * (tw + 4.5), y0 + row * (th + 10.5)
        f = files.get(r.id)
        if f:
            sh.out.append('<image x="%s" y="%s" width="%s" height="%s" href="%s" xlink:href="%s"/>' % (x, y, tw, th, f, f))
        sh.rect(x, y, tw, th, "f")
        sh.text(x + 1, y + th + 3.6, "%s  %s" % (r.code, r.name), 2.0, bold=True, maxw=tw - 2)
    return sh
