"""Per-room sheets: plan (P), longitudinal section (SL) and transverse section (ST)."""
from shipmodel import SLAB_T
from planview import (PV, draw_floor, draw_walls, draw_openings, draw_props, draw_zones, draw_holes, draw_forcefields, 
                  draw_stairs, place_balloons, draw_dim_chains, family_legend)
from sectionview import (SV, Cut, draw_room_section, draw_stairs_section, room_section_dims, wall_item_labels)
from svgkit import Sheet, nice_scale, wrap_words

LAY_A = (14.0, 9.0, 302.0, 249.0)       # plan area when the data panel is on the right
LAY_B = (14.0, 8.0, 410.0, 200.0)       # plan area when the panel is underneath


def _deck_title(ship, deck):
    return "DECK %d - %s" % (deck, ship.deck_name[deck].upper())


def room_info_rows(ship, room):
    nwin = sum(1 for o in room.openings if o["kind"] == "window")
    ndoor = sum(1 for o in room.openings if o["kind"] != "window")
    nprops = len(room.props)
    return [
        ("Room", "%s  %s" % (room.code, room.name)),
        ("Deck / level", "%d  (FFL %+.3f)" % (room.deck, room.y)),
        ("Department", room.dept),
        ("Floor area", "%.1f m2" % room.area),
        ("Clear height", "%d mm" % round(room.h * 1000)),
        ("Volume", "%.0f m3" % (room.area * room.h)),
        ("Floor occupancy", "%.0f %%" % (room.occupancy() * 100)),
        ("Crew", str(room.crew())),
        ("Props placed", str(nprops)),
        ("Doors / arches", str(ndoor)),
        ("Windows", str(nwin)),
            ]


def wrap_lines(text, maxw, size):
    return wrap_words(text, max(8, int(maxw / (0.54 * size))))


def wrap_block(sh, x, y, w, head, text, maxlines=4, size=1.7):
    sh.text(x, y + 2.2, head.upper() + ":", size, bold=True)
    ls = wrap_lines(text, w - 2, size)
    if len(ls) > maxlines:
        ls = ls[:maxlines]
        ls[-1] = ls[-1][:max(0, len(ls[-1]) - 3)] + "..."
    for i, l in enumerate(ls):
        sh.text(x, y + 2.2 + 3.1 * (i + 1), l, size)
    return y + 2.2 + 3.1 * (len(ls) + 1)


def bom_rows(room):
    rows = []
    for ln in room.bom:
        q = sum(1 for p in room.props if p.code == ln["code"])
        rows.append((ln["code"], ln["title"], str(q)))
    return rows


def draw_panel_tables(sh, ship, room, cat, layout):
    info = room_info_rows(ship, room)
    bom = bom_rows(room)
    if layout == "A":
        x, y, w = 307.0, 14.0, 106.0
        y = sh.table(x, y, [28, w - 28], info, title="ROOM DATA", rh=3.3, size=1.7, bold_first=True)
        y += 4
        y = wrap_block(sh, x, y, w, "Purpose", room.brief.get("purpose") or "-", 4)
        y += 5
        cw = [14, w - 14 - 8, 8]
        maxr = int((248 - 34 - y) / 3.0)
        y = sh.table(x, y, cw, bom, header=("CODE", "BOM LINE", "QTY"), title="BILL OF MATERIALS LINES", rh=3.0, size=1.6,
                     maxrows=max(4, maxr - 8))
        y += 7
        family_legend(sh, x, y, cat, room.props, cols=2, colw=53, maxn=30)
    else:
        y0 = 210.0
        yb = sh.table(14.0, y0 + 2, [26, 50], info, title="ROOM DATA", rh=3.2, size=1.6, bold_first=True)
        wrap_block(sh, 14.0, yb + 1, 76.0, "Purpose", room.brief.get("purpose") or "-", 4, 1.6)
        cw = [13, 43, 7]
        half = 24
        x = 94.0
        sh.text(x, y0, "BILL OF MATERIALS LINES", 2.3, bold=True)
        left = bom[:half]
        right = bom[half:2 * half]
        if len(bom) > 2 * half:
            sh.text(x, y0 + 2 + 2.9 * (half + 1) + 3, "... +%d more BOM lines (see docs/BOM.md)" % (len(bom) - 2 * half), 1.5, ital=True)
        sh.table(x, y0 + 2, cw, left, header=("CODE", "BOM LINE", "QTY"), rh=2.9, size=1.5)
        if right:
            sh.table(x + 65, y0 + 2, cw, right, header=("CODE", "BOM LINE", "QTY"), rh=2.9, size=1.5,
                     maxrows=None)
        family_legend(sh, 242.0, 214.0, cat, room.props, cols=3, colw=57, maxn=18)


def plan_extent(room):
    return room.w, room.dd


def room_plan(ship, room):
    cat = ship.cat
    w, d = room.w, room.dd
    scales = {}
    opts = (20, 25, 50, 75, 100, 150, 200, 250, 300)
    for lay, area in (("A", LAY_A), ("B", LAY_B)):
        # normal margin for dimension chains + two rings of balloons; long thin rooms may use a tighter one
        scales[lay] = min(nice_scale(area[2] - area[0] - 56.0, area[3] - area[1] - 56.0, w, d, options=opts),
                          nice_scale(area[2] - area[0] - 44.0, area[3] - area[1] - 44.0, w, d, options=opts) if len(room.bom) <= 8 else 999)
    lay = "B" if scales["B"] < scales["A"] or (scales["B"] == scales["A"] and w > d * 1.3) else "A"
    n = scales[lay]
    area = LAY_A if lay == "A" else LAY_B
    s = 1000.0 / n
    sh = Sheet("R-%s-P" % room.id, "%s - plan" % room.name, "%s  -  FLOOR PLAN AT FFL %+.3f" % (_deck_title(ship, room.deck), room.y),
               "1:%d" % n, "DECK %d" % room.deck, room.code, room.name)
    cx, cy = (area[0] + area[2]) / 2, (area[1] + area[3]) / 2
    pv = PV(s, cx - (room.x0 + room.x1) / 2 * s - 0 * 1, cy - (room.z0 + room.z1) / 2 * s, 0.0, 0.0)
    pv.ox = cx - (room.x0 + room.x1) / 2 * s
    pv.oy = cy - (room.z0 + room.z1) / 2 * s
    sh.rect(area[0] - 1, area[1] - 1, area[2] - area[0] + 2, area[3] - area[1] + 2, "x")
    draw_floor(sh, pv, room)
    draw_zones(sh, pv, room)
    draw_holes(sh, pv, room)
    draw_props(sh, pv, room, cat, labels=(s >= 10))
    if room.id.startswith("tower"):
        draw_stairs(sh, pv, ship, room.deck, only_side="S" + room.id[5:6].upper())
    draw_walls(sh, pv, room)
    draw_openings(sh, pv, room, marks=True)
    draw_forcefields(sh, pv, room)
    # room name inside
    rings = place_balloons(sh, pv, room, margin=7.0)
    draw_dim_chains(sh, pv, room, off=8.0 + 7.3 * max(rings, 1) + 1.0)
    # bow arrow, scale bar
    sh.bow_arrow(area[2] - 10, area[1] + 11)
    sh.scalebar(area[0] + 6, area[3] - 4, s)
    draw_panel_tables(sh, ship, room, cat, lay)
    sh.text(area[0] + 1, area[1] + 3.2, "PLAN - %s" % room.name.upper(), 2.6, bold=True)
    sh.text(area[0] + 1, area[1] + 6.4, "Floor props as oriented footprints (front edge heavy); wall items = bars on wall; ceiling items dotted", 1.4, fill="#555")
    return sh


# ------------------------------------------------------------------ sections
def key_plan(sh, ship, room, cut, x, y, w, h):
    """Small plan of the deck with the room highlighted and the cut line."""
    bx0, bz0, bx1, bz1 = ship.bounds(room.deck)
    s = min((w - 14) / (bx1 - bx0), (h - 10) / (bz1 - bz0))
    ox = x + (w - (bx1 - bx0) * s) / 2 - bx0 * s
    oy = y + 7 + ((h - 10) - (bz1 - bz0) * s) / 2 - bz0 * s
    pv = PV(s, ox, oy, 0, 0)
    sh.rect(x, y, w, h, "f")
    sh.text(x + 1.5, y + 3.2, "KEY PLAN", 1.8, bold=True)
    sh.poly(pv.pts(ship.hull[room.deck]), "n", "#f4f4f4")
    for r in ship.deck_rooms(room.deck):
        sh.poly(pv.pts(r.poly), "x", "#f7d9a8" if r.id == room.id else "none")
    sh.poly(pv.pts(ship.hull[room.deck]), "m")
    if cut.axis == "x":
        a, b = pv.xy(cut.c, bz0 - 3), pv.xy(cut.c, bz1 + 3)
    else:
        a, b = pv.xy(bx0 - 3, cut.c), pv.xy(bx1 + 3, cut.c)
    sh.line(*a, *b, "cut")
    lab = "A"
    for p in (a, b):
        sh.circ(p[0], p[1], 2.0, "n", "#fff")
        sh.text(p[0], p[1] + .6, lab, 1.8, "middle", bold=True)
    sh.text(x + w - 2, y + 3.2, "BOW", 1.6, "end", bold=True)
    sh.poly([(x + w - 4, y + 4.5), (x + w - 2.6, y + 8), (x + w - 5.4, y + 8)], "f", "#111")


def section_legend(sh, x, y):
    sh.text(x, y, "SECTION KEY", 1.9, bold=True)
    y += 2.4
    items = [("n", "#1c1c1c", "Cut wall (poche 150 mm)"), ("n", "url(#hHull)", "Cut hull wall"), ("n", "url(#hSlab)", "Cut slab 300 mm / stair"),
             ("m", "#e8d2a0", "Cut furniture (heavy outline)"), ("f", "#e8e0d0", "Beyond: silhouette, shaded by depth"),
             ("n", "url(#hGlass)", "Window (glazing / sill / head)"), ("dot", "none", "Ceiling item (dotted)"),
             ("n", "#c3cad6", "Door leaf in wall beyond")]
    for k, (c, f, t) in enumerate(items):
        yy = y + k * 3.5
        sh.rect(x, yy, 6, 2.4, c, f)
        sh.text(x + 8, yy + 1.9, t, 1.6)


def room_section(ship, room, kind):
    cat = ship.cat
    axis = "x" if kind == "SL" else "z"
    cut = Cut(axis, room.cx if axis == "x" else room.cz)
    iv = cut.iv(room.poly)
    a, b = iv
    H = room.h + 2 * SLAB_T
    area = (14.0, 8.0, 410.0, 200.0)
    n = nice_scale(area[2] - area[0] - 62, area[3] - area[1] - 38, b - a, H, options=(20, 25, 50, 75, 100, 150, 200))
    s = 1000.0 / n
    title = "%s - %s" % (room.name, "longitudinal section" if kind == "SL" else "transverse section")
    sub = "%s  -  SECTION A-A %s  (cut plane %s = %.2f m)" % (_deck_title(ship, room.deck), cut.label, axis, cut.c)
    sh = Sheet("R-%s-%s" % (room.id, kind), title, sub, "1:%d" % n, "DECK %d" % room.deck, room.code, room.name)
    cx = (area[0] + area[2]) / 2
    ox = cx - ((a + b) / 2) * s
    ybase = area[1] + 12 + (H * s) + (area[3] - area[1] - 38 - H * s) / 2     # paper y of y0 baseline
    sv = SV(s, ox, ybase, 0.0, room.y - SLAB_T)      # paper y of the underside of the floor slab = ybase
    sh.text(area[0] + 1, area[1] + 3.2, "SECTION A-A - %s" % room.name.upper(), 2.6, bold=True)
    sh.text(area[0] + 1, area[1] + 6.4, cut.label + "  -  %s on the left" % cut.hmin_label(), 1.6, fill="#555")
    p0, p1 = sv.xy(a, room.top + SLAB_T), sv.xy(b, room.y - SLAB_T)
    sh.clip_def("clipA", p0[0] - 0.3, p0[1] - 0.3, p1[0] - p0[0] + 0.6, p1[1] - p0[1] + 0.6)
    info = {}
    sh.open_g(clip="clipA")
    draw_room_section(sh, sv, cut, room, ship, cat, "beyond", labels=True, info=info)
    if room.id.startswith("tower"):
        draw_stairs_section(sh, sv, cut, ship, "beyond", region=room.poly)
    draw_room_section(sh, sv, cut, room, ship, cat, "cut", labels=True, info=info)
    if room.id.startswith("tower"):
        draw_stairs_section(sh, sv, cut, ship, "cut", region=room.poly)
    sh.close_g()
    wall_item_labels(sh, sv, info, room)
    # end labels
    sh.text(sv.xy(a, 0)[0], sv.xy(0, room.top + SLAB_T)[1] - 3, cut.hmin_label(), 1.8, "start", bold=True)
    sh.text(sv.xy(b, 0)[0], sv.xy(0, room.top + SLAB_T)[1] - 3, cut.hmax_label(), 1.8, "end", bold=True)
    room_section_dims(sh, sv, cut, room, iv, info, ship)
    sh.scalebar(area[2] - 70, area[3] - 4, s)
    key_plan(sh, ship, room, cut, 14.0, 206.0, 70.0, 84.0)
    section_legend(sh, 90.0, 212.0)
    sh.text(150.0, 212.0, "NOTES", 1.9, bold=True)
    notes = ["Walls 150 mm, slabs 300 mm (see ship_builder).", "Cut plane passes through the room centroid.",
             "Heights in mm above FFL; levels in m.", "Wall item numbers = mount height (origin) above FFL.",
             "Beyond items are projected silhouettes (width x height)."]
    for k, t in enumerate(notes):
        sh.text(150.0, 216.5 + k * 3.6, t, 1.6, maxw=84)
    return sh
