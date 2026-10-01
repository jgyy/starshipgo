#!/usr/bin/env python3
"""Write room["mats"] = theme_for(...) into a ship.json (stop-gap until generate_ship.py does it itself).

    python tools/quality/apply_themes.py godot/data/ship.json [out.json]
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "layout"))
from themes import theme_for  # noqa: E402


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "godot/data/ship.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else src
    with open(src) as fh:
        ship = json.load(fh)
    for room in ship["rooms"]:
        room["mats"] = theme_for(room["id"], room.get("dept", ""))
    with open(dst, "w") as fh:
        json.dump(ship, fh, indent=1)
    print(f"themed {len(ship['rooms'])} rooms -> {dst}")


if __name__ == "__main__":
    main()
