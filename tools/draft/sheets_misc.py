"""Stair tower detail, circulation / escape, schedules, index and contact sheets."""
import heapq
import math

from shipmodel import SLAB_T, PITCH
from planview import PV, draw_floor, draw_walls, draw_openings, draw_holes, draw_stairs
from sectionview import SV, Cut, draw_room_section, draw_stairs_section, lv
from svgkit import Sheet, nice_scale, trunc


# ------------------------------------------------------------------ G-13 stairs
def stair_sheet(ship):
    decks = ship.deck_ids                                     # top (sky) deck first
    if not ship.stair_geom("SA")[0]:
        return None                                           # a ship without stairs has no stair-tower sheet
    nruns = len(ship.stair_geom("SA")[0])
    sh = Sheet("G-13", "Stair tower details", "DOG-LEG STAIR TOWER: PLANS AT EACH LEVEL, SECTION ALONG THE FLIGHTS (%d FLIGHT RUNS, %d DECKS), TREAD / RISER DETAIL" % (nruns, len(decks)),
               "1:100 / 1:10", "ALL", "SP / SS", "Stair tower", slug="stair_tower_details")
    cat = ship.cat
    runs, st = ship.stair_geom("SA")                          # runs[0] = lowest storey ... runs[-1] = highest
    # ---------------- section along lane A (z = 0.85)
    zc = runs[0]["flights"][0]["z"]
    cut = Cut("z", zc)
    towers = [ship.tower("SA", d) for d in decks]
    a = min(cut.iv(r.poly)[0] for r in towers)
    b = max(cut.iv(r.poly)[1] for r in towers)
    ymin, ymax = min(r.y for r in towers) - SLAB_T, max(r.top for r in towers) + SLAB_T
    n = nice_scale(122.0, 236.0, b - a, ymax - ymin, options=(50, 75, 100, 150, 200))
    s = 1000.0 / n
    ox = 14 + 26 - a * s
    sv = SV(s, ox, 0, 0, ymin)
    sv.oy = 28 + (ymax - ymin) * s
    sh.text(16, 15, "SECTION B-B - ALONG THE FLIGHTS (lane A)  1:%d" % n, 2.8, bold=True)
    sh.text(16, 19, "Cut at z = %.2f m looking aft; port tower, all %d levels (%d flight runs)" % (zc, len(decks), len(runs)), 1.6, fill="#555")
    p0, p1 = sv.xy(a, ymax), sv.xy(b, ymin)
    sh.clip_def("clipB", p0[0] - 0.5, p0[1] - 0.5, p1[0] - p0[0] + 1.0, p1[1] - p0[1] + 1.0)
    sh.open_g(clip="clipB")
    for r in towers:
        draw_room_section(sh, sv, cut, r, ship, cat, "beyond", depth_max=6.0)
    draw_stairs_section(sh, sv, cut, ship, "beyond", handrail=True, only=["SA"])
    for r in towers:
        draw_room_section(sh, sv, cut, r, ship, cat, "cut")
    draw_stairs_section(sh, sv, cut, ship, "cut", handrail=True, only=["SA"])
    sh.close_g()
    # level marks
    for d in decks:
        y = ship.deck_y[d]
        sh.level_mark(sv.xy(a, 0)[0] - 22, sv.xy(0, y)[1], "%s D%d" % (lv(y), d), 1.8, True)
    for rn in runs:
        sh.level_mark(sv.xy(a, 0)[0] - 22, sv.xy(0, rn["landing_y"])[1], lv(rn["landing_y"]) + " LDG", 1.6, True)
    # dimensions on flight A of the lowest run
    f = runs[0]["flights"][0]
    r_ = f["rise"] / f["n"]
    xe = f["x"] + f["dir"] * f["tread"] * (f["n"] - 1)
    sh.dim_v(sv.xy(0, f["y"])[1], sv.xy(0, f["y"] + f["rise"])[1], sv.xy(-xe, 0)[0] - 7, "%d R @ 181.8 = %d" % (f["n"], round(f["rise"] * 1000)),
             ext_x=sv.xy(-xe, 0)[0] - 0.5)
    yb = sv.xy(0, ymin)[1] + 8
    sh.dim_h(sv.xy(-f["x"], 0)[0], sv.xy(-xe, 0)[0], yb, "%d G @ %d = %d" % (f["n"] - 1, round(f["tread"] * 1000), round(f["tread"] * (f["n"] - 1) * 1000)),
             ext_y=sv.xy(0, ymin)[1] + 1)
    # headroom above flight A (lowest run): up to the underside of the flight above
    k = 5
    xk = f["x"] + f["dir"] * f["tread"] * k
    y_low = f["y"] + (k + 1) * r_
    f2 = runs[1]["flights"][0] if len(runs) > 1 else None
    if f2:
        y_up = f2["y"] + (k + 1) * r_ - 0.24
        sh.dim_v(sv.xy(0, y_low)[1], sv.xy(0, y_up)[1], sv.xy(-xk, 0)[0] + 5, "HEADROOM %d" % round((y_up - y_low) * 1000), ext_x=sv.xy(-xk, 0)[0] + 0.3)
    y_h0 = f["y"] + (k + 1) * r_
    sh.dim_v(sv.xy(0, y_h0)[1], sv.xy(0, y_h0 + 0.9)[1], sv.xy(-xk, 0)[0] - 4, "HANDRAIL 900", ext_x=sv.xy(-xk, 0)[0] - 0.3)
    # slab opening dimension on the floor above the lowest run
    tw = ship.tower("SA", runs[0]["hi"])
    if tw is not None and tw.floor_holes:
        hx0, hx1 = tw.floor_holes[0][0], tw.floor_holes[0][2]
        yy = sv.xy(0, tw.y)[1] - 9
        sh.dim_h(sv.xy(-hx1, 0)[0], sv.xy(-hx0, 0)[0], yy, "SLAB OPENING %d" % round((hx1 - hx0) * 1000), ext_y=sv.xy(0, tw.y)[1] - 0.5)
    # a whole storey: 2 x 11 risers
    rn = runs[len(runs) // 2]
    y_lo_d, y_hi_d = ship.deck_y[rn["lo"]], ship.deck_y[rn["hi"]]
    sh.dim_v(sv.xy(0, y_lo_d)[1], sv.xy(0, y_hi_d)[1], sv.xy(b, 0)[0] + 7, "22 R @ 181.8 = %d (2 flights)" % round((y_hi_d - y_lo_d) * 1000),
             ext_x=sv.xy(b, 0)[0] + 1)
    lr = runs[0]["landing"]
    sh.text(sv.xy(-(lr[0] + lr[2]) / 2, 0)[0], sv.xy(0, runs[0]["landing_y"])[1] - 3, "MID-LANDING", 1.6, "middle", bold=True)
    sh.text(sv.xy(a, 0)[0], sv.xy(0, ymax)[1] - 3, "STBD side / hull", 1.6, "start")
    sh.text(sv.xy(b, 0)[0], sv.xy(0, ymax)[1] - 3, "lobby side", 1.6, "end")
    sh.scalebar(14 + 26, 287, s)
    # ---------------- plans, one per deck (top deck first), 3 per row
    ps = 1000.0 / 100
    for i, d in enumerate(decks):
        cx0, cy0 = 148.0 + (i % 3) * 85.0, 14.0 + (i // 3) * 60.0
        r = ship.tower("SA", d)
        pv = PV(ps, cx0 + 6 - r.x0 * ps, cy0 + 14 - r.z0 * ps, 0, 0)
        sh.text(cx0, cy0 + 3, "PLAN - DECK %d (FFL %+.3f)  1:100" % (d, r.y), 2.1, bold=True)
        draw_floor(sh, pv, r, k=0.7)
        draw_holes(sh, pv, r)
        draw_stairs(sh, pv, ship, d, only_side="SA")
        draw_walls(sh, pv, r)
        draw_openings(sh, pv, r)
        x0p, y0p = pv.xy(r.x0, r.z0)
        x1p, y1p = pv.xy(r.x1, r.z1)
        sh.dim_h(x0p, x1p, y0p - 4.5, "%d" % round(r.w * 1000), ext_y=y0p - 0.5)
        sh.dim_v(y0p, y1p, x1p + 6, "%d" % round(r.dd * 1000), ext_x=x1p + 1)
        g0 = runs[0]["flights"][0]
        sh.dim_h(pv.xy(g0["x"], 0)[0], pv.xy(g0["x"] + g0["dir"] * g0["tread"] * (g0["n"] - 1), 0)[0], y1p + 5,
                 "10 x 280 = 2800", ext_y=y1p + 0.5)
        up = next((q for q in runs if q["lo"] == d), None)
        dn = next((q for q in runs if q["hi"] == d), None)
        if up and dn:
            cap = "UP: flight A to the %s landing; DN: flight B arrives from the %s landing." % (lv(up["landing_y"]), lv(dn["landing_y"]))
        elif up:
            cap = "UP only (lowest deck): flight A rises to the %s landing; flight B returns to the strip above." % lv(up["landing_y"])
        elif dn:
            cap = "DN only (top deck): flight B arrives from the %s landing." % lv(dn["landing_y"])
        else:
            cap = ""
        sh.text(x0p, y1p + 10.0, trunc(cap, 80, 1.4), 1.4, fill="#555")
    # ---------------- detail A: tread / riser at 1:10
    x0, y0 = 150.0, 150.0
    sh.text(x0, y0, "DETAIL A - TREAD / RISER  1:10", 2.3, bold=True)
    ds = 100.0
    r_m, g_m = PITCH / 22.0, 0.28
    px, py = x0 + 10, y0 + 82
    pts = [(px, py)]
    for k in range(3):
        pts.append((px + k * g_m * ds, py - (k + 1) * r_m * ds))
        pts.append((px + (k + 1) * g_m * ds, py - (k + 1) * r_m * ds))
    pts += [(px + 3 * g_m * ds, py - 3 * r_m * ds), (px + 3 * g_m * ds, py - 3 * r_m * ds - 0.24 * ds), (px, py - 0.0)]
    sh.poly(pts, "m", "url(#hSlab)")
    sh.dim_v(py - 2 * r_m * ds, py - r_m * ds, px + 3 * g_m * ds + 8, "181.8 RISER", ext_x=px + 2 * g_m * ds + 0.5)
    sh.dim_h(px + g_m * ds, px + 2 * g_m * ds, py - 3 * r_m * ds - 4, "280 GOING", ext_y=py - 2 * r_m * ds - 0.5)
    ang = math.degrees(math.atan2(r_m, g_m))
    sh.text(px - 6, py + 6, "Pitch %.1f deg   2R + G = %.0f mm (comfort 550-700)" % (ang, 2 * r_m * 1000 + 280), 1.7)
    sh.text(px - 6, py + 10, "Waist (slab) thickness 240 mm measured vertically.", 1.7)
    # ---------------- stair data table
    xt = 262.0
    levels = ", ".join("%+.0f" % rn_["landing_y"] for rn_ in runs)
    data = [("Floor to floor", "4000 mm (2 x 2000 half-flights)"), ("Levels served", "%d decks, %d flight runs per tower (%d flights)" % (len(decks), len(runs), 2 * len(runs))),
            ("Risers", "22 per storey: 11 + 11"), ("Riser height", "181.8 mm (4000 / 22)"),
            ("Going (tread)", "280 mm; 10 goings / flight + landing"), ("Flight width", "1400 mm clear"),
            ("Going length", "2800 mm (11 risers: 10 goings)"), ("Handrails", "900 mm above nosing, both sides"),
            ("Headroom", "3760 mm (stacked flights 4000 - 240)"), ("Mid-landings (m)", levels),
            ("Deck strip", "1800 mm at each landing level"), ("Slab openings", "3 per slab: 2 flight lanes + landing"),
            ("Escape", "2 towers (port / starboard), 3.2 m arches")]
    yt = sh.table(xt, 140, [30, 85], data, title="STAIR DATA", rh=3.6, size=1.8, bold_first=True)
    notes = ["Geometry follows ship.json stairs[] (flights, landings, strip)", "and matches blender/starship/arch.py (arch_stair_flight).",
             "Dashed lines: flights above the plan cut plane (+1.2 m);", "thin solid lines: flights below the cut plane."]
    for i, t in enumerate(notes):
        sh.text(xt, yt + 6 + i * 4, t, 1.6)
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
    decks = ship.deck_ids
    sh = Sheet("G-14", "Circulation and escape diagram", "TRAVEL DISTANCE FROM EACH ROOM CENTRE TO THE NEAREST STAIR (via doors, straight legs), ALL %d DECKS" % len(decks),
               "1:400", "ALL", "ALL", "Escape", slug="circulation_escape_diagram")
    s = 1000.0 / 400
    pitch = min(66.0, 330.0 / max(len(decks), 1))
    results = []
    for k, d in enumerate(decks):
        dist, prev, pos = escape_graph(ship, d)
        hb = ship.bounds(d)
        x0 = 16 + k * pitch
        pv = PV(s, x0 + pitch / 2 - 1, 36 - ship.bounds(None)[1] * s, 0.0, 0.0)
        sh.text(x0, 20, "DECK %d" % d, 3.0, bold=True)
        sh.text(x0 + 22, 20, ship.deck_name[d], 1.8, fill="#444", maxw=pitch - 24)
        rooms = ship.deck_rooms(d)
        for r in rooms:
            dd = dist.get("c:" + r.id, 1e9)
            sh.poly(pv.pts(r.poly), "f", ("#dddddd" if dd > 1e8 else band_color(dd)) if not r.id.startswith("tower") else "#9fc6ee")
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
                sh.text(cx, cy + .7, "STAIR", 1.5, "middle", bold=True)
            else:
                sh.circ(cx, cy, 0.7, "n", "#b03030")
                sh.text(cx, cy - 1.2, r.code, 1.5, "middle", bold=True, halo=True)
                sh.text(cx, cy + 2.2, "-" if dd > 1e8 else "%.0f m" % dd, 1.5, "middle", halo=True)
            results.append((d, r, dd))
        fin = [v for dd_, r, v in results if dd_ == d and not r.id.startswith("tower") and v < 1e8]
        sh.text(x0 + 2, 36 + (ship.bounds(None)[3] - ship.bounds(None)[1]) * s + 8, "max %.0f m" % max(fin) if fin else "no route", 2.0, bold=True)
    # legend + table
    x = 16 + len(decks) * pitch + 2
    sh.bow_arrow(x + 12, 20, r=5.0)
    sh.text(x + 22, 14, "ESCAPE TRAVEL BANDS", 1.9, bold=True)
    for i, (lim, col, lab) in enumerate(BANDS):
        sh.rect(x + 22, 17 + i * 4.0, 7, 2.6, "n", col)
        sh.text(x + 31, 19.3 + i * 4.0, lab, 1.6)
    sh.line(x + 22, 33.2, x + 29, 33.2, "red")
    sh.text(x + 31, 33.9, "escape route", 1.6)
    rows = [("D%d" % d, r.code, r.name, "-" if v > 1e8 else "%.1f" % v) for d, r, v in sorted(results, key=lambda t: (t[0], -(t[2] if t[2] < 1e8 else 0)))
            if not r.id.startswith("tower")]
    cw = [7, 10, 410 - x - 7 - 10 - 11 - 6, 11]
    sh.table(x, 44, cw, rows, header=("DK", "CODE", "ROOM", "m"), title="TRAVEL DISTANCE TO NEAREST STAIR", rh=2.95, size=1.5)
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
    per = 70
    cw = [11, 9, 11, 11, 25, 12, 12, 52]
    hdr = ("MARK", "DECK", "FROM", "TO", "TYPE", "W mm", "H mm", "MODEL")
    x = 16.0
    ncol = max(1, -(-len(rows) // per))
    for k in range(ncol):
        sh.table(x + k * (sum(cw) + 4), 20, cw, rows[k * per:(k + 1) * per], header=hdr, rh=3.45, size=1.7, bold_first=True)
    wrows = []
    for w in ship.win_list:
        r = ship.by_id[w["room"]]
        area = w["w"] * (w["head"] - w["sill"])
        wrows.append((w["mark"], "D%d" % w["deck"], r.code, w["side"], "%d" % round(w["w"] * 1000), "%d" % round(w["sill"] * 1000),
                      "%d" % round(w["head"] * 1000), "%.2f" % area))
    x2 = 16.0 + (sum(cw) + 4) * ncol + 2
    wcw = [21, 8, 10, 9, 12, 11, 11, 13]
    wper = 66
    nwb = max(1, -(-len(wrows) // wper))
    nwb = min(nwb, max(1, int((410 - x2) // (sum(wcw) + 3))))
    sh.text(x2, 14, "WINDOW SCHEDULE (%d panes)" % len(wrows), 2.6, bold=True)
    for k in range(nwb):
        sh.table(x2 + k * (sum(wcw) + 3), 20, wcw, wrows[k * wper:(k + 1) * wper] if k < nwb - 1 else wrows[k * wper:], header=("MARK", "DECK", "ROOM", "WALL", "W mm", "SILL", "HEAD", "AREA m2"),
                 rh=3.45, size=1.6, bold_first=True, maxrows=wper)
    lastrows = max(1, len(wrows) - (nwb - 1) * wper) if nwb > 1 else min(len(wrows), wper)
    xn, yn = x2 + (nwb - 1) * (sum(wcw) + 3), 20 + 3.45 * (min(lastrows, wper) + 2) + 4
    nx = sum(1 for w in ship.ext_windows if w["kind"] == "window")
    notes = ["Doors: 2.36 m wide wall cut, head 2.76 m", "(catalog sliding door models).", "Arches: 3.0 - 4.0 m wide, head 3.0 - 3.2 m.",
             "Windows only on hull-exposed walls.", "Exterior window panels on the outer skin", "(ship.json ext_windows): %d, see G-05." % nx]
    for i, t in enumerate(notes):
        sh.text(xn, yn + i * 4, t, 1.6, fill="#444")
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
    sh.text(16, y + 14, "Contact sheets K-xx show all room plans of a deck as thumbnails (one per deck, numbered like the deck's G sheet).", 1.7)
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
    # lay out as grid of 10 columns x rows
    ncol = 10
    for i, c in enumerate(cats):
        col, row = i % ncol, i // ncol
        xx, yy = x4 + col * 40, y4 + 3 + row * 3.6
        sh.rect(xx, yy, 4, 2.4, "n", ship.cat.color[c])
        sh.text(xx + 5.2, yy + 1.9, c, 1.5, maxw=34)
    return sh


# ------------------------------------------------------------------ contact sheets
def contact_sheet(ship, deck, files, num=None):
    """files: room id -> relative file name of the plan sheet (SVG)."""
    num = num or "K-%02d" % deck
    sh = Sheet(num, "Contact sheet - Deck %d room plans" % deck, "%s - THUMBNAILS OF EVERY ROOM PLAN SHEET" % ship.deck_name[deck].upper(),
               "NTS", "DECK %d" % deck, "ALL", "Contact sheet deck %d" % deck, slug="contact_sheet_deck%d" % deck)
    rooms = ship.deck_rooms(deck)
    cols = 5 if len(rooms) <= 15 else 6
    tw = (394.0 - (cols - 1) * 4.5) / cols
    th = tw * 297 / 420
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
