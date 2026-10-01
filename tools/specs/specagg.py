"""Shared aggregation of machine datasheets over placed items (used by gen_ship_spec.py and tools/layout/bom.py).

A model that is missing from specs.json simply contributes nothing (and is counted in ``missing``); nothing here raises for it.
Standard library only.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ZERO = {"n": 0, "kg": 0.0, "idle": 0.0, "typ": 0.0, "peak": 0.0, "cr": 0.0, "gen_kw": 0.0, "cap_kwh": 0.0, "store_kw": 0.0, "heat": 0.0, "missing": 0}


def load_specs(root=ROOT):
    """specs.json -> {model id: spec}; {} if the file does not exist."""
    p = os.path.join(root, "godot", "data", "specs.json")
    try:
        with open(p) as f:
            return json.load(f).get("models", {})
    except (OSError, ValueError):
        return {}


def blank():
    return dict(ZERO)


def add(total, mid, specs, qty=1):
    """Add qty units of model ``mid`` to the totals dict."""
    total["n"] += qty
    s = specs.get(mid)
    if s is None:
        total["missing"] += qty
        return total
    total["kg"] += s["kg"] * qty
    total["cr"] += s["cr"] * qty
    total["heat"] += s.get("heat", 0) * qty
    w = s.get("w", [0, 0, 0])
    total["idle"] += w[0] * qty
    total["typ"] += w[1] * qty
    total["peak"] += w[2] * qty
    if s.get("r") == "g":
        total["gen_kw"] += s.get("gen", 0) * qty
    if s.get("r") == "s":
        total["cap_kwh"] += s.get("cap", 0) * qty
        total["store_kw"] += s.get("gen", 0) * qty
    return total


def merge(a, b):
    for k in ZERO:
        a[k] += b[k]
    return a


def room_items(room, ship):
    """Model ids placed in a room: its props plus the doors it owns (side a of the door)."""
    ids = [p["m"] for p in room.get("props", [])]
    ids += [d["m"] for d in ship.get("doors", []) if d.get("a") == room["id"]]
    return ids


def room_totals(room, ship, specs):
    t = blank()
    for mid in room_items(room, ship):
        add(t, mid, specs)
    return t


def fmt_kg(kg):
    return "%.2f t" % (kg / 1000.0) if kg >= 1000 else "%.0f kg" % kg


def fmt_w(w):
    if w >= 1e6:
        return "%.2f MW" % (w / 1e6)
    if w >= 1e3:
        return "%.1f kW" % (w / 1e3)
    return "%.0f W" % w


def fmt_cr(c):
    if c >= 1e6:
        return "%.2f M" % (c / 1e6)
    if c >= 1e3:
        return "%.1f k" % (c / 1e3)
    return "%.0f" % c
