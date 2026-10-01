#!/usr/bin/env python3
"""Generate the bill of materials of the starship from godot/data/ship.json.

    python tools/layout/bom.py                # writes docs/BOM.md and docs/bom/*.csv

Everything in the document comes from the same data the game is built from: the design brief and the BOM lines
written in the room recipes (``R.describe`` / ``R.line``), the placed models, the catalog and policy.py.  The output
is deterministic, so CI can check that the committed document is up to date.
"""
import argparse
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit  # noqa: E402
import hull as hulllib  # noqa: E402
import policy  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

DECK_TEXT = {
    1: ("Command Deck", "The command deck sits at the top of the ship and reaches furthest forward: the bridge overhangs the bow so the "
        "crew has an unobstructed view ahead over the tapered nose. Everything that steers, decides or communicates is here, "
        "with the officers' country aft where it is quietest and furthest from the engines."),
    2: ("Habitat Deck", "The habitat deck is the widest deck and holds everything that keeps the crew alive, fed, healthy and "
        "busy: mess and galley forward-port next to each other, medical and science on the starboard side, security in the bow "
        "where the hull narrows (small rooms with lots of wall), and quarters, recreation and the garden aft."),
    3: ("Engineering Deck", "The engineering deck is the ship's machinery floor: life support and the computer core forward, main "
        "engineering and power distribution amidships and aft, cargo and spares next to the hangar so stores never cross the crew "
        "areas, and the hangar on the stern platform where craft can launch straight aft."),
}

ZONING = [
    ("Hull lines", "The hull is drafted as one closed, convex outline per deck: an elliptical-sine bow that is tangent to a 26 m "
                   "parallel mid-body, then a rounded counter that tapers to a narrow transom. The decks are terraced like a cruise "
                   "ship (Deck 1 overhangs the bow, Deck 3 extends aft to form the hangar platform)."),
    ("Room shapes", "Rooms are drafted on a rectangular grid and clipped by the hull: amidships rooms stay rectangular, bow and stern "
                    "rooms get the diagonal, streamlined walls of the hull. Wedge rooms take equipment along their straight walls."),
    ("Circulation", "A 3 m spine corridor on the centreline, a mid-ship cross passage and two dog-leg stair towers (port and starboard) "
                    "stacked on every deck. There are no lifts. Corridors carry only wall and ceiling equipment so the escape route stays clear."),
    ("Escape", "%(escape)s There are always two towers; stair towers are protected "
               "spaces with extinguishers, emergency lighting and signage."),
]
ESCAPE_LIMIT = 35.0      # m, design limit of the walking distance to a stair tower

MM = lambda v: int(round(v * 1000))


def load(root=ROOT):
    with open(os.path.join(root, "godot", "data", "ship.json"), encoding="utf-8") as f:
        ship = json.load(f)
    with open(os.path.join(root, "godot", "data", "catalog.json"), encoding="utf-8") as f:
        cat = {m["id"]: m for m in json.load(f)["models"]}
    return ship, cat


def fmt_size(m):
    return "%d x %d x %d" % (MM(m["size"][0]), MM(m["size"][1]), MM(m["size"][2]))


def md_escape(s):
    return str(s).replace("|", "\\|")


def pretty(mid, cat):
    m = cat[mid]
    return m["label"].replace("_", " ").title() if m.get("label") else mid


def room_items(room, cat):
    """(BOM line code -> Counter of model ids, doorway frames, items that belong to no BOM line).

    An item without a (known) BOM line used to be reported as a "doorway frame"; it is its own group now."""
    lines = collections.OrderedDict((l["code"], collections.Counter()) for l in room["bom"])
    arch = collections.Counter()
    loose = collections.Counter()
    for p in room["props"]:
        b = p.get("b")
        if b == "ARCH":
            arch[p["m"]] += 1
        elif b not in lines:
            loose[p["m"]] += 1
        else:
            lines[b][p["m"]] += 1
    return lines, arch, loose


def egress_table(ship):
    rows = []
    for r in ship["rooms"]:
        if r["id"].startswith("tower") or r["id"].startswith("lobby"):
            continue
        cx, cz = sum(p[0] for p in r["poly"]) / len(r["poly"]), sum(p[1] for p in r["poly"]) / len(r["poly"])
        # walking route: to the spine corridor (x=0) along z, then along the corridor to the lobby (z = 1.8), then to the tower
        inside_spine = abs(cx) < 1.6
        to_spine = 0.0 if inside_spine else abs(cx) - 1.5
        dz = abs(cz - 1.8)
        best = to_spine + dz + 4.9
        rows.append((r["deck"], r["id"], r["name"], best))
    return rows


def write_csv(ship, cat, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "bill_of_materials.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["deck", "room_code", "room", "bom_line", "line_title", "model_id", "family", "item", "mount", "qty",
                    "width_mm", "height_mm", "depth_mm", "function", "why"])
        for r in ship["rooms"]:
            lines, arch, loose = room_items(r, cat)

            def row(code, title, mid, n, why):
                m = cat[mid]
                info = policy.CATEGORY_INFO.get(m["category"], ("", ""))
                w.writerow([r["deck"], r["code"], r["name"], code, title, mid, m["category"], pretty(mid, cat),
                            m["mount"], n, MM(m["size"][0]), MM(m["size"][1]), MM(m["size"][2]), info[1], why])
            for l in r["bom"]:
                for mid, n in sorted(lines[l["code"]].items()):
                    row(l["code"], l["title"], mid, n, l["why"])
            # doorway frames, doors and items outside every BOM line are bought too: the CSV lists every placement
            for mid, n in sorted(arch.items()):
                row("ARCH", "Doorway frames", mid, n, "Open doorway between spaces that need no door.")
            for mid, n in sorted(loose.items()):
                row("-", "Not in any BOM line", mid, n, "Placed without a BOM line (the audit rule bom-line fails on this).")
            for mid, n in sorted(collections.Counter(d["m"] for d in ship["doors"] if d["a"] == r["id"]).items()):
                row("DOOR", "Sliding doors", mid, n, "Pressure-tight compartment door (listed with the first room of the pair).")
    return path


def generate(ship, cat):
    stats = {s["room"]: s for s in audit.audit_stats(ship, cat)}
    out = []
    w = out.append
    decks = {d["id"]: d for d in ship["decks"]}
    total_props = sum(len(r["props"]) for r in ship["rooms"]) + len(ship["doors"])
    models_used = {p["m"] for r in ship["rooms"] for p in r["props"]} | {d["m"] for d in ship["doors"]}
    total_lines = sum(len(r["bom"]) for r in ship["rooms"])
    w("# StarshipGo - Bill of Materials")
    w("")
    w("*Generated by `python tools/layout/bom.py` from `godot/data/ship.json`; do not edit by hand.*")
    w("")
    w("Every room of the ship is furnished from a written bill of materials: each **BOM line** groups the models that serve one function "
      "and states **why** they are in the room, how many there are and why they stand where they do. The same data drives the game, the "
      "audit (`tools/layout/audit.py`) and the drawings in [`docs/drafts`](drafts/INDEX.md). The placement policy "
      "(`tools/layout/policy.py`) says which equipment families may appear in which room; the audit fails the build when a reactor "
      "turns up in the mess or a chair stands in a doorway.")
    w("")
    w("## 1. Ship summary")
    w("")
    w("| | |")
    w("|---|---|")
    deck_ids = sorted(decks)
    # the hull of the ship.json being documented, not whatever hull.py would draw today
    hl = {d: [tuple(p) for p in ship["hull"][str(d)]] for d in deck_ids if str(d) in ship.get("hull", {})}
    allz = [p[1] for d in hl.values() for p in d]
    allx = [abs(p[0]) for d in hl.values() for p in d]
    w("| Length overall | %.0f m |" % ((max(allz) - min(allz)) if allz else 0.0))
    w("| Beam | %.0f m |" % (2 * max(allx) if allx else 0.0))
    w("| Decks | %d (floors at %s m) |" % (len(ship["decks"]), ", ".join("%+.1f" % d["y"] for d in sorted(ship["decks"], key=lambda d: d["y"]))))
    w("| Rooms (incl. circulation) | %d |" % len(ship["rooms"]))
    w("| Doors / arches | %d sliding doors, %d open arches and portals |" % (
        len(ship["doors"]), sum(1 for r in ship["rooms"] for o in r["openings"] if o["kind"] == "open") // 2 +
        sum(1 for r in ship["rooms"] for p in r["props"] if p.get("b") == "ARCH")))
    w("| Stair towers | 2 (port / starboard), 4 dog-leg flight pairs, 22 risers of 181.8 mm per deck |")
    w("| BOM lines | %d |" % total_lines)
    w("| Placed items | %d |" % total_props)
    w("| Distinct models used | %d of %d in the catalogue |" % (len(models_used), len(cat)))
    w("")
    w("### Decks")
    w("")
    w("| Deck | Name | Hull area | Rooms | Room area | Items | BOM lines |")
    w("|---|---|---|---|---|---|---|")
    for d in deck_ids:
        rs = [r for r in ship["rooms"] if r["deck"] == d]
        w("| %d | %s | %.0f m2 | %d | %.0f m2 | %d | %d |" % (d, decks[d]["name"], hulllib.area(hl[d]) if d in hl else 0.0, len(rs), sum(r["area"] for r in rs),
                                                             sum(len(r["props"]) for r in rs), sum(len(r["bom"]) for r in rs)))
    w("")
    w("### Design principles")
    w("")
    eg = egress_table(ship)
    worst = max(eg, key=lambda r: r[3]) if eg else None
    over = [r for r in eg if r[3] > ESCAPE_LIMIT]
    if worst is None:
        escape = "(no rooms)"
    elif over:
        escape = "%d room(s) are further than the %.0f m design limit from a stair tower (longest: %s, %.1f m; see section 3)." % (
            len(over), ESCAPE_LIMIT, worst[2], worst[3])
    else:
        escape = "Every room centre is within the %.0f m design limit of a stair tower (longest: %s, %.1f m)." % (ESCAPE_LIMIT, worst[2], worst[3])
    for t, s in ZONING:
        w("* **%s.** %s" % (t, s % {"escape": escape} if "%(escape)s" in s else s))
    w("")
    w("```mermaid")
    w("flowchart LR")
    w("    brief[Room brief and BOM lines<br/>recipes_deck*.py] --> gen[generate_ship.py]")
    w("    cat[(catalog.json<br/>%d Blender models)] --> gen" % len(cat))
    w("    hull[hull.py<br/>tapered outlines] --> gen")
    w("    pol[policy.py<br/>allowed families] --> aud[audit.py]")
    w("    gen --> ship[(ship.json)]")
    w("    ship --> aud")
    w("    ship --> bom[bom.py -> this document]")
    w("    ship --> dr[draft.py -> plan and section sheets]")
    w("    ship --> game[Godot: build, cull, batch]")
    w("```")
    w("")
    # ---- totals by family
    fam = collections.Counter()
    fam_models = collections.defaultdict(set)
    for r in ship["rooms"]:
        for p in r["props"]:
            c = cat[p["m"]]["category"]
            fam[c] += 1
            fam_models[c].add(p["m"])
    w("## 2. Totals by equipment family")
    w("")
    w("| Family | What it is for | Qty | Distinct models |")
    w("|---|---|---|---|")
    for c, n in sorted(fam.items(), key=lambda kv: (-kv[1], kv[0])):
        info = policy.CATEGORY_INFO.get(c, (c, ""))
        w("| `%s` %s | %s | %d | %d |" % (c, info[0], md_escape(info[1]), n, len(fam_models[c])))
    w("")
    w("## 3. Means of escape")
    w("")
    w("Approximate walking distance (room centre -> spine corridor -> nearest stair tower) for every room; the design limit is %.0f m." % ESCAPE_LIMIT)
    w("")
    w("| Deck | Room | Walking distance to the nearest stair |")
    w("|---|---|---|")
    for deck, rid, name, dist in egress_table(ship):
        w("| %d | %s (`%s`) | %.1f m%s |" % (deck, name, rid, dist, " **over the limit**" if dist > ESCAPE_LIMIT else ""))
    w("")
    # ---- chapters
    chapter = 3
    for d in deck_ids:
        chapter += 1
        title, text = DECK_TEXT.get(d, (decks[d]["name"], ""))
        w("## %d. Deck %d - %s (floor +%.1f m)" % (chapter, d, title, decks[d]["y"]))
        w("")
        w(text)
        w("")
        rs = [r for r in ship["rooms"] if r["deck"] == d]
        w("| Code | Room | Area | Height | Items | BOM lines | Floor occupancy |")
        w("|---|---|---|---|---|---|---|")
        for r in rs:
            s = stats.get(r["id"], {})
            w("| [%s](#%s) | %s | %.1f m2 | %.1f m | %d | %d | %.0f %% |" % (r["code"], anchor(r), r["name"], r["area"], r["height"],
                                                                     len(r["props"]), len(r["bom"]), 100 * s.get("occupancy", 0.0)))
        w("")
        for r in rs:
            room_chapter(w, r, ship, cat, stats.get(r["id"], {}))
    w("## %d. Index of models used" % (chapter + 1))
    w("")
    w("Every distinct model in the ship with its total quantity and the rooms that use it.")
    w("")
    w("| Model | Family | Mount | Size mm (W x H x D) | Qty | Rooms |")
    w("|---|---|---|---|---|---|")
    use = collections.defaultdict(lambda: collections.Counter())
    for r in ship["rooms"]:
        for p in r["props"]:
            use[p["m"]][r["code"]] += 1
    for d in ship["doors"]:
        use[d["m"]][ship_room_code(ship, d["a"])] += 1
    for mid in sorted(use):
        m = cat[mid]
        rooms = ", ".join("%s x%d" % (k, v) if v > 1 else k for k, v in sorted(use[mid].items()))
        w("| `%s` | %s | %s | %s | %d | %s |" % (mid, m["category"], m["mount"], fmt_size(m), sum(use[mid].values()), rooms))
    w("")
    return "\n".join(out) + "\n"


def ship_room_code(ship, rid):
    for r in ship["rooms"]:
        if r["id"] == rid:
            return r["code"]
    return rid


def anchor(r):
    """GitHub heading anchor of the room chapter heading '### BR - Bridge'."""
    t = ("%s - %s" % (r["code"], r["name"])).lower()
    keep = "".join(ch if (ch.isalnum() or ch in " -") else "" for ch in t)
    return keep.replace(" ", "-")


def room_chapter(w, r, ship, cat, st):
    w("### %s - %s" % (r["code"], r["name"]))
    w("")
    b = r["brief"]
    w("> %s" % (b.get("purpose") or "-"))
    w("")
    w("| Property | Value |")
    w("|---|---|")
    w("| Room id | `%s` |" % r["id"])
    w("| Deck / department | %d / %s |" % (r["deck"], r["dept"]))
    w("| Floor area | %.1f m2 (plan bounding box %.1f x %.1f m) |" % (r["area"], r["rect"][2] - r["rect"][0], r["rect"][3] - r["rect"][1]))
    w("| Ceiling height / volume | %.1f m / %.0f m3 |" % (r["height"], r["area"] * r["height"]))
    diag = sum(1 for e in r["edges"] if e["side"].startswith("D"))
    hullw = sum(1 for e in r["edges"] if e["hull"])
    w("| Walls | %d (%d diagonal hull facets, %d on the outer hull) |" % (len(r["edges"]), diag, hullw))
    wins = [o for o in r["openings"] if o["kind"] == "window"]
    w("| Windows | %s |" % ("%d (%.1f m2 of glazing)" % (len(wins), sum(o["w"] * (o["y1"] - o["y0"]) for o in wins)) if wins else "none"))
    if b.get("crew"):
        w("| Design occupancy | %s persons |" % b["crew"])
    w("| Items placed / distinct models | %d / %d |" % (len(r["props"]), st.get("distinct_models", 0)))
    w("| Floor occupancy | %.0f %% (floor-standing footprints / floor area) |" % (100 * st.get("occupancy", 0.0)))
    w("| Lights | %d real lights, %d ceiling fixtures |" % (len(r["lights"]), sum(1 for p in r["props"] if cat[p["m"]]["category"] == "ceilinglight")))
    w("")
    if b.get("basis"):
        w("**Design basis.** %s" % b["basis"])
        w("")
    adj = b.get("adjacency")
    links = r.get("links", [])
    if links or adj:
        names = {x["id"]: x["name"] for x in ship["rooms"]}
        conn = ", ".join("%s (%s, %s)" % (names.get(l["to"], l["to"]), l["kind"], l["side"] + " wall") for l in links)
        w("**Adjacency.** %s%s" % (adj + " " if adj else "", ("Connected to: " + conn + ".") if conn else ""))
        w("")
    if b.get("notes"):
        w("**Notes.** %s" % b["notes"])
        w("")
    lines, arch, loose = room_items(r, cat)
    doors = [d for d in ship["doors"] if d["a"] == r["id"] or d["b"] == r["id"]]
    if loose:
        w("**Items not assigned to a BOM line (%d)**: %s." % (sum(loose.values()), ", ".join("`%s` x%d" % kv for kv in sorted(loose.items()))))
        w("")
    if doors or arch or wins:
        w("**Openings and architecture**")
        w("")
        w("| Element | Model | Qty | Purpose |")
        w("|---|---|---|---|")
        for d in doors:
            other = d["b"] if d["a"] == r["id"] else d["a"]
            w("| Sliding door to `%s` | `%s` | 1 | Pressure-tight compartment door; slides open when someone approaches. |" % (other, d["m"]))
        for mid, n in sorted(arch.items()):
            w("| Doorway frame | `%s` | %d | Open doorway between spaces that need no door. |" % (mid, n))
        if wins:
            w("| Viewport glazing | (built from hull data) | %d | Natural view and orientation for the crew; windows are only cut in hull walls. |" % len(wins))
        w("")
    w("**Bill of materials - %d lines, %d items**" % (len(r["bom"]), len(r["props"])))
    w("")
    for l in r["bom"]:
        items = lines[l["code"]]
        n = sum(items.values())
        w("#### %s - %s (%d item%s)" % (l["code"], l["title"], n, "" if n == 1 else "s"))
        w("")
        w("*Why:* %s" % l["why"])
        w("")
        if items:
            w("| Qty | Model | Family | Mount | Size mm (W x H x D) | Function of the family |")
            w("|---|---|---|---|---|---|")
            for mid, cnt in sorted(items.items(), key=lambda kv: (cat[kv[0]]["category"], kv[0])):
                m = cat[mid]
                info = policy.CATEGORY_INFO.get(m["category"], ("", ""))
                w("| %d | `%s` | %s | %s | %s | %s |" % (cnt, mid, info[0] or m["category"], m["mount"], fmt_size(m), md_escape(info[1])))
            w("")
    # room totals by family
    fam = collections.Counter(cat[p["m"]]["category"] for p in r["props"])
    w("**Room totals by family**: " + ", ".join("%s x%d" % (k, v) for k, v in sorted(fam.items(), key=lambda kv: (-kv[1], kv[0]))) + ".")
    w("")
    allowed = sorted(policy.allowed(r["id"]))
    w("<details><summary>Equipment families permitted in this room by the placement policy (%d)</summary>" % len(allowed))
    w("")
    w(", ".join("`%s`" % a for a in allowed))
    w("")
    w("Anything else (for example reactors, cargo crates or beds, unless listed above) is rejected by the audit.")
    w("")
    w("</details>")
    w("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", default=None, help="markdown output (default docs/BOM.md)")
    a = ap.parse_args()
    ship, cat = load(a.root)
    md = generate(ship, cat)
    out = a.out or os.path.join(a.root, "docs", "BOM.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    csv_path = write_csv(ship, cat, os.path.join(os.path.dirname(out), "bom"))
    print(f"{out}: {md.count(chr(10))} lines, {len(md) // 1024} KB; {csv_path}")


if __name__ == "__main__":
    main()
