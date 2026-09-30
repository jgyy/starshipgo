#!/usr/bin/env python3
"""Print the geometry of rooms from a generated ship.json:  python tools/layout/inspect_room.py mess bridge [--ship PATH]"""
import argparse
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ap = argparse.ArgumentParser()
ap.add_argument("rooms", nargs="*")
ap.add_argument("--ship", default=os.path.join(ROOT, "godot", "data", "ship.json"))
a = ap.parse_args()
ship = json.load(open(a.ship))
for r in ship["rooms"]:
    if a.rooms and r["id"] not in a.rooms:
        continue
    print(f"== {r['id']}  '{r['name']}'  deck {r['deck']}  dept {r['dept']}  area {r['area']} m2  height {r['height']} m  floor y={next(d['y'] for d in ship['decks'] if d['id']==r['deck'])}")
    print("   bbox x %.2f..%.2f  z %.2f..%.2f" % (r["rect"][0], r["rect"][2], r["rect"][1], r["rect"][3]))
    print("   walls (side: from -> to, length, on-hull):")
    for e in r["edges"]:
        ln = ((e["b"][0] - e["a"][0]) ** 2 + (e["b"][1] - e["a"][1]) ** 2) ** 0.5
        print("     %-3s (%.2f, %.2f) -> (%.2f, %.2f)  len %.2f %s" % (e["side"], *e["a"], *e["b"], ln, "HULL" if e["hull"] else ""))
    for o in r["openings"]:
        print("   opening %-6s on %-3s c=%.2f w=%.2f y %.1f..%.1f" % (o["kind"], o["side"], o["c"], o["w"], o["y0"], o["y1"]))
    for z in r["zones"]:
        print("   reserved %-5s rect %s  (%s)" % (z["kind"], z["rect"], z["why"]))
    print("   props:", len(r["props"]), " bom lines:", len(r["bom"]))
