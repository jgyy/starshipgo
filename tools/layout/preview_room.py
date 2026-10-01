#!/usr/bin/env python3
"""Developer preview of room plans from godot/data/ship.json (needs matplotlib; not used by CI).

    python tools/layout/preview_room.py bridge mess -o /tmp/plan.png       # one panel per room
    python tools/layout/preview_room.py --deck 2 -o /tmp/deck2.png         # whole deck

Floor items are drawn as their true oriented footprints (colour = family), wall items as thin bars on the wall,
ceiling items as dotted outlines, clearance zones hatched.  Labels are the model ids without the family prefix.
"""
import argparse
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import rot, obb_corners  # noqa: E402

PALETTE = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
           "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080"]


def family_colors(categories):
    """One stable colour per family, independent of which rooms are drawn first (the first 20 come from PALETTE, the rest
    from golden-ratio hues, so no two families share a colour)."""
    import colorsys
    out = {}
    for i, c in enumerate(sorted(set(categories))):
        if i < len(PALETTE):
            out[c] = PALETTE[i]
        else:
            r, g, b = colorsys.hsv_to_rgb((i * 0.61803398875) % 1.0, 0.55, 0.9)
            out[c] = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    return out


def draw_room(ax, r, cat, labels=True, colors=None):
    colors = colors or family_colors(m["category"] for m in cat.values())
    ax.add_patch(Polygon(r["poly"], closed=True, fc="#f4f6f9", ec="#222", lw=2.2, zorder=1))
    for z in r.get("zones", []):
        x0, z0, x1, z1 = z["rect"]
        ax.add_patch(Polygon([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], fc="none", ec="#c77", hatch="///", lw=0.4, zorder=1.5))
    for h in r.get("floor_holes", []):
        ax.add_patch(Polygon([(h[0], h[1]), (h[2], h[1]), (h[2], h[3]), (h[0], h[3])], fc="#555", alpha=0.5, zorder=1.5))
    edges = {e["side"]: e for e in r["edges"]}
    for o in r["openings"]:
        e = edges[o["side"]]
        a, b = e["a"], e["b"]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if o["side"] in ("N", "S"):
            px, pz, ux, uz = o["c"], a[1], 1.0, 0.0
        elif o["side"] in ("E", "W"):
            px, pz, ux, uz = a[0], o["c"], 0.0, 1.0
        else:
            ux, uz = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            px, pz = a[0] + ux * o["c"], a[1] + uz * o["c"]
        col = {"window": "#2b8cff", "door": "#d22", "open": "#2a2"}[o["kind"]]
        ax.plot([px - ux * o["w"] / 2, px + ux * o["w"] / 2], [pz - uz * o["w"] / 2, pz + uz * o["w"] / 2], color=col, lw=6, zorder=5, solid_capstyle="butt")
    for p in r["props"]:
        m = cat[p["m"]]
        col = colors[m["category"]]
        lo, hi = m["bounds_min"], m["bounds_max"]
        sc = p.get("scale", 1.0)
        cx, cz = (lo[0] + hi[0]) / 2 * sc, (lo[2] + hi[2]) / 2 * sc
        ox, oz = rot(cx, cz, p["yaw"])
        c = (p["pos"][0] + ox, p["pos"][2] + oz)
        pts = obb_corners(c[0], c[1], (hi[0] - lo[0]) / 2 * sc, (hi[2] - lo[2]) / 2 * sc, p["yaw"])
        if m["mount"] == "floor":
            ax.add_patch(Polygon(pts, fc=col, ec="k", lw=0.6, alpha=0.85, zorder=3))
            fx, fz = rot(0, (hi[2] - lo[2]) / 2 * sc, p["yaw"])       # front marker
            ax.plot([c[0], c[0] + fx], [c[1], c[1] + fz], color="k", lw=0.8, zorder=4)
        elif m["mount"] == "table":
            ax.add_patch(Polygon(pts, fc=col, ec="k", lw=0.4, alpha=0.95, zorder=4))
        elif m["mount"] == "wall":
            ax.add_patch(Polygon(pts, fc=col, ec="k", lw=0.4, alpha=0.9, zorder=2.5))
        else:
            ax.add_patch(Polygon(pts, fc="none", ec=col, lw=0.8, ls=":", zorder=2))
        if labels and m["mount"] in ("floor",) and (hi[0] - lo[0]) > 0.6:
            ax.text(c[0], c[1], m["id"].split("_", 1)[-1][:14], fontsize=4.2, ha="center", va="center", zorder=6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rooms", nargs="*")
    ap.add_argument("--deck", type=int)
    ap.add_argument("-o", "--out", default="plan.png")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--no-labels", action="store_true")
    ap.add_argument("--ship", default=os.path.join(ROOT, "godot", "data", "ship.json"))
    a = ap.parse_args()
    with open(a.ship, encoding="utf-8") as f:
        ship = json.load(f)
    with open(os.path.join(ROOT, "godot", "data", "catalog.json"), encoding="utf-8") as f:
        cat = {m["id"]: m for m in json.load(f)["models"]}
    colors = family_colors(m["category"] for m in cat.values())
    bad = [x for x in a.rooms if x not in {r["id"] for r in ship["rooms"]}]
    if bad:
        sys.exit("no such room: %s; have: %s" % (", ".join(bad), ", ".join(r["id"] for r in ship["rooms"])))
    rooms = [r for r in ship["rooms"] if (r["id"] in a.rooms) or (a.deck and r["deck"] == a.deck)]
    if not rooms:
        sys.exit("no such room; have: " + ", ".join(r["id"] for r in ship["rooms"]))
    if a.deck and not a.rooms:
        fig, ax = plt.subplots(figsize=(10, 16))
        for r in rooms:
            draw_room(ax, r, cat, not a.no_labels, colors)
            ax.text(r["rect"][0] + 0.3, r["rect"][1] + 0.6, r["name"], fontsize=6, weight="bold", zorder=7)
        ax.set_aspect("equal"); ax.invert_yaxis(); ax.autoscale_view()
    else:
        n = len(rooms)
        cols = min(n, 2)
        rows = (n + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(11 * cols, 9 * rows), squeeze=False)
        for ax, r in zip([x for row in axs for x in row], rooms):
            draw_room(ax, r, cat, not a.no_labels, colors)
            ax.set_aspect("equal"); ax.invert_yaxis(); ax.autoscale_view()
            ax.set_title("%s - %s (%.0f m2, %d props)" % (r["id"], r["name"], r["area"], len(r["props"])))
    plt.tight_layout()
    plt.savefig(a.out, dpi=a.dpi)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
