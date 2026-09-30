"""Room recipes - Deck 3 (Engineering Deck)."""
import math

from dressing import *   # noqa: F401,F403
from recipes_deck1 import corridor, lobby, lift_car, seat_behind
from shiplib import FACE_YAW, WALL_T

FLOOR = lambda m: m["mount"] == "floor"


def f_cor3(R, B): corridor(R, B, "engineering")
def f_lobby3(R, B): lobby(R, B)
def f_liftA3(R, B): lift_car(R, B)
def f_liftB3(R, B): lift_car(R, B)


def f_life(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.5, color="#eafff4", cats=("ceilinglight", "panellight"))
    R.run("W", ["scrubber", "watertank"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6)
    R.run("N", ["scrubber", "watertank"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6)
    R.run("S", ["cylinder", "scrubber"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6, start=R.x0 + 0.5, end=R.x1 - 3)
    R.grid(["watertank", "scrubber"], R.x0 + 4.5, R.z0 + 4.0, R.x1 - 3.0, R.z1 - 3.0, 2, 2, pred=FLOOR)
    R.run("E", ["duct", "valve", "controlpanel"], wall_mount=True, y=2.0)
    R.run("N", ["duct", "pipe"], wall_mount=True, y=2.7)
    R.run("W", ["duct", "valve"], wall_mount=True, y=2.4)
    ceiling_runs(R, "duct", "x", 2)
    ceiling_runs(R, "pipe", "y", 1)
    dress_ceiling(R, 3, cats=("ceilingpanel", "duct"))
    signs(R, "E", R.cz, None)
    R.omni(R.cx, R.y + 1.5, R.cz, "#66ffcc", 0.6, 8.0)


def f_core(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.1, color="#cfe4ff", cats=("ceilinglight", "panellight"))
    for row, x in enumerate((R.x0 + 3.5, R.x0 + 7.0, R.x0 + 10.5)):
        z = R.z0 + 1.2
        while z < R.z1 - 1.2:
            m = c.pick("rack", pred=lambda m: FLOOR(m) and m["size"][0] < 1.2)
            if not m:
                break
            p = R.place(m, x, z + m["size"][0] / 2, -90.0 if row % 2 == 0 else 90.0)
            z += (m["size"][0] + 0.05) if p else 0.4
    R.run("W", ["storage", "rack"], gap=0.03, pred=lambda m: FLOOR(m) and m["size"][0] < 1.5)
    R.run("E", ["storage"], gap=0.03, pred=FLOOR, start=R.z0 + 0.5, end=R.z1 - 3)
    R.run("N", ["router", "commsunit"], wall_mount=True, y=1.6)
    R.run("S", ["router", "controlpanel", "display"], wall_mount=True, y=1.8)
    R.run("W", ["router", "display"], wall_mount=True, y=2.4)
    ceiling_runs(R, "cabletray", "x", 3)
    dress_ceiling(R, 2, cats=("ceilingpanel",))
    R.omni(R.cx, R.y + 1.2, R.cz, "#3399ff", 1.2, 9.0)


def f_shop(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.7, color="#fff6e0")
    R.run("W", ["engtool"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.4)
    R.run("N", ["engtool", "storagebin", "shelving"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.4)
    R.run("S", ["engtool", "storagebin"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.4, start=R.x0 + 0.5, end=R.x1 - 3)
    for k in range(2):
        b = R.place(c.pick("engtool", pred=lambda m: FLOOR(m) and 1.2 < m["size"][0] < 2.6), R.cx + 1.0, R.cz - 2.0 + k * 4.0, 90.0)
        tabletop(R, b, ["engtool", "storagebin"], 3)
    R.run("E", ["engtool", "valve", "junction"], wall_mount=True, y=1.8)
    R.run("N", ["engtool", "junction"], wall_mount=True, y=1.8)
    R.run("W", ["engtool", "wallpanel"], wall_mount=True, y=1.8)
    dress_ceiling(R, 3, cats=("ceilingpanel", "duct"))
    ceiling_runs(R, "pipe", "x", 1)


def f_airlock(R, B):
    c = B.cat
    light_room(R, spacing=4.0, energy=1.5, color="#fffbe0", cats=("ceilinglight", "beacon"))
    R.run("N", ["suitrack"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.5)
    R.run("W", ["suitrack", "locker", "safety"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.0)
    R.run("E", ["suitrack", "cylinder"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.0, start=R.z0 + 0.5, end=R.z1 - 3)
    R.place(c.pick("suitrack", pred=lambda m: FLOOR(m) and m["size"][0] > 0.8), R.cx + 2, R.cz, 90.0)
    R.place(c.pick("bench", pred=by_size(maxw=2.6)), R.cx - 3, R.cz, 0.0)
    hatch = c.pick("hatch", pred=lambda m: m["mount"] == "wall")
    R.wall_item("N", hatch, R.cx, y=1.3, check=False)
    R.run("S", ["sign", "beacon", "controlpanel"], wall_mount=True, y=2.0)
    R.run("W", ["wallpanel"], wall_mount=True, y=1.7)
    dress_ceiling(R, 3)
    ceiling_runs(R, "pipe", "x", 1)


def f_eng(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.6, color="#ffeed8", cats=("ceilinglight",), pred=lambda m: True)
    # main reactor and safety railing
    reactor = R.place(c.pick("reactor", pred=lambda m: m["size"][1] > 2.0), R.cx, R.cz - 2, 0.0)
    if reactor:
        fp = reactor["_fp"]
        rx, rz = (fp[0] + fp[2]) / 2, (fp[1] + fp[3]) / 2
        hw, hd = (fp[2] - fp[0]) / 2 + 0.7, (fp[3] - fp[1]) / 2 + 0.7
        for sx in (-1, 1):
            rl = c.pick("railing", pred=lambda m: FLOOR(m) and 1.5 < m["size"][0] < 2.6)
            for k in range(int(hd * 2 // 2)):
                R.place(rl, rx + sx * hw, rz - hd + 1.0 + k * 2.0, 90.0, check=False)
        R.omni(rx, R.y + 1.6, rz, "#55ccff", 3.0, 12.0, shadow=False)
    # coils / capacitors
    R.place(c.pick("coil", pred=FLOOR), R.cx - 4.5, R.cz - 8.0, 0.0)
    R.place(c.pick("coil", pred=FLOOR), R.cx + 4.5, R.cz - 8.0, 0.0)
    R.run("N", ["capacitor", "generator"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6)
    R.run("W", ["generator", "tank", "capacitor"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6, start=R.z0 + 1, end=R.z1 - 1)
    R.run("E", ["tank", "turbine", "generator"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6, start=R.z0 + 1, end=R.z1 - 8)
    R.run("S", ["capacitor", "turbine", "tank"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.6, start=R.x0 + 1, end=R.x1 - 3)
    for k in range(3):
        con = R.place(c.pick("console", label="engineering", pred=by_size(maxw=2.4)), R.cx - 3.6 + k * 3.6, R.z1 - 5.2, 180.0)
    R.run("W", ["junction", "valve", "controlpanel"], wall_mount=True, y=1.8)
    R.run("E", ["junction", "valve", "display"], wall_mount=True, y=1.8, start=R.z1 - 8, end=R.z1 - 0.5)
    R.run("N", ["pipe", "junction", "valve"], wall_mount=True, y=2.2)
    R.run("S", ["pipe", "display", "junction"], wall_mount=True, y=2.2)
    R.place(c.pick("nozzle", pred=FLOOR), R.x1 - 2.2, R.z1 - 3.2, 0.0)
    ceiling_runs(R, "pipe", "x", 3)
    ceiling_runs(R, "cabletray", "y", 2)
    dress_ceiling(R, 4, cats=("ceilingpanel", "duct"))
    signs(R, "W", R.z1 - 2.5, "engineering")


def f_aux(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.5, color="#fff0dc")
    R.grid(["capacitor", "generator"], R.x0 + 3.5, R.z0 + 3.2, R.x1 - 3.5, R.z1 - 3.2, 3, 2, pred=lambda m: FLOOR(m) and m["size"][0] < 2.4)
    R.run("N", ["junction", "generator"], gap=0.03, pred=lambda m: FLOOR(m) and m["size"][0] < 1.6)
    R.run("W", ["junction", "capacitor"], gap=0.03, pred=lambda m: FLOOR(m) and m["size"][0] < 1.6)
    R.run("S", ["junction", "generator", "turbine"], gap=0.03, pred=lambda m: FLOOR(m) and m["size"][0] < 2.4, start=R.x0 + 0.5, end=R.x1 - 3)
    R.run("E", ["junction", "tank"], gap=0.03, pred=lambda m: FLOOR(m) and m["size"][0] < 1.6, start=R.z0 + 0.5, end=R.z1 - 0.5)
    R.run("N", ["junction", "valve"], wall_mount=True, y=1.8)
    R.run("W", ["junction", "valve"], wall_mount=True, y=1.8)
    R.run("E", ["junction", "controlpanel"], wall_mount=True, y=1.8)
    ceiling_runs(R, "cabletray", "x", 3)
    ceiling_runs(R, "pipe", "y", 1)
    dress_ceiling(R, 3)


def cargo_bay(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.5, color="#fff2e0", cats=("ceilinglight",))
    R.run("W" if R.cx < 0 else "E", ["shelving"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 3.2)
    R.run("N", ["shelving", "storagebin"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 3.2)
    # stacks of crates / pallets / barrels in the open floor
    ix0, iz0, ix1, iz1 = R.inner(2.4)
    n = 0
    for cat in ("crate", "pallet", "barrel", "crate", "pallet", "barrel", "storagebin", "crate"):
        for _ in range(9):
            m = c.pick(cat, pred=lambda m: FLOOR(m) and m["size"][0] < 2.8 and m["size"][2] < 2.8)
            if not m:
                break
            x = R.rng.uniform(ix0, ix1)
            z = R.rng.uniform(iz0 + 2.0, iz1)
            if R.place(m, x, z, R.rng.choice([0, 90, 180, 270]), margin=0.25):
                n += 1
    lo = c.pick("loader", pred=lambda m: FLOOR(m) and m["size"][0] < 3.5)
    R.place(lo, R.cx, R.cz + 2.0, 90.0)
    R.run("S", ["crate", "barrel"], gap=0.05, pred=lambda m: FLOOR(m) and m["size"][0] < 2.0, start=R.x0 + 0.5, end=R.x1 - 3)
    R.run("W", ["safety", "sign", "junction"], wall_mount=True, y=1.6)
    R.run("E", ["safety", "sign", "junction"], wall_mount=True, y=1.6)
    R.run("N", ["sign", "wallpanel"], wall_mount=True, y=2.2)
    ceiling_runs(R, "cabletray", "x", 2)
    dress_ceiling(R, 4)
    safety(R, "N", R.cx + 6)


def f_cargoA(R, B): cargo_bay(R, B)
def f_cargoB(R, B): cargo_bay(R, B)


def f_hangar(R, B):
    c = B.cat
    hi = lambda m: any(k in m["id"] for k in ("high", "bay", "industrial", "flood", "cage"))
    R.light_grid(cats=("ceilinglight",), spacing=6.0, energy=3.0, color="#f4f8ff", x_margin=2.0, range_mul=1.3, angle=80.0,
                 pred=hi if any(hi(m) for m in c.by_cat.get("ceilinglight", [])) else None, shadow_every=4)
    # landing pads with craft
    craft = [m for m in c.by_cat.get("craft", [])]
    slots = [(-11, 46), (0, 46), (11, 46), (-11, 55), (0, 55), (11, 55), (-14, 40), (14, 40), (-6, 40.5), (6, 40.5)]
    for i, (x, z) in enumerate(slots):
        m = c.pick("craft", pred=lambda m: m["size"][0] < 9 and m["size"][2] < 9)
        pad = c.pick("hangartool", pred=lambda m: m["mount"] == "floor" and m["size"][1] < 0.3 and m["size"][0] > 3)
        if m:
            R.place(m, x, z, 180.0, margin=0.0)
        if pad:
            R.place(pad, x, z, 0.0, check=False, reserve=False)
    for s in "WE":
        R.run(s, ["hangartool"], gap=0.1, spacing=0.4, pred=lambda m: FLOOR(m) and m["size"][0] < 2.5 and m["size"][1] > 0.4, start=R.z0 + 1, end=R.z1 - 1)
    R.run("N", ["hangartool", "shelving", "loader"], gap=0.1, spacing=0.3, pred=lambda m: FLOOR(m) and m["size"][0] < 4.0, start=R.x0 + 1, end=R.x0 + 12)
    R.run("N", ["hangartool", "shelving", "loader"], gap=0.1, spacing=0.3, pred=lambda m: FLOOR(m) and m["size"][0] < 4.0, start=R.x1 - 12, end=R.x1 - 1)
    R.run("W", ["sign", "junction", "controlpanel", "safety"], wall_mount=True, y=2.0)
    R.run("E", ["sign", "junction", "controlpanel", "safety"], wall_mount=True, y=2.0)
    R.run("W", ["pipe", "duct"], wall_mount=True, y=5.5)
    R.run("E", ["pipe", "duct"], wall_mount=True, y=5.5)
    for x in (-14, 14):
        R.place(c.pick("hangartool", label="light"), x, 44, 0.0)
    ceiling_runs(R, "pipe", "x", 3)
    ceiling_runs(R, "cabletray", "y", 2)
    R.omni(0, R.y + 4.0, 52, "#88bbff", 2.0, 20.0)
