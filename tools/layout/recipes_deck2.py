"""Room recipes - Deck 2 (Habitat Deck)."""
import math

from dressing import *   # noqa: F401,F403
from recipes_deck1 import corridor, lobby, lift_car, seat_behind
from shiplib import FACE_YAW, WALL_T


def f_cor2(R, B): corridor(R, B, "transit")
def f_lobby2(R, B): lobby(R, B)
def f_liftA2(R, B): lift_car(R, B)
def f_liftB2(R, B): lift_car(R, B)


def f_armory(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.5, color="#f4e8e8")
    R.run("W", ["weaponrack"], gap=0.03, spacing=0.05, pred=by_size(maxw=2.0))
    R.run("N", ["weaponrack"], gap=0.03, spacing=0.05, pred=by_size(maxw=2.0))
    R.run("S", ["weaponrack"], gap=0.03, spacing=0.05, pred=by_size(maxw=2.0), start=R.x0 + 0.5, end=R.x1 - 3.5)
    for k in range(2):
        b = R.place(c.pick("weaponrack", pred=lambda m: m["mount"] == "floor" and m["size"][0] > 1.0), R.cx + 1.2, R.cz - 1.5 + k * 3.0, 0.0)
        tabletop(R, b, ["tableware"], 0)
    R.run("E", ["suitrack", "safety"], gap=0.03, start=R.z0 + 1, end=R.z1 - 3)
    R.run("W", ["sign", "display"], wall_mount=True, y=2.4)
    dress_walls(R, ("wallpanel",))
    dress_ceiling(R, 4)
    ceiling_runs(R, "cabletray", "x", 1)
    cam = c.pick("camera", pred=lambda m: m["mount"] == "ceiling")
    R.place(cam, R.cx, R.cz, 0.0, y=R.y + R.h, check=False)


def f_galley(R, B):
    c = B.cat
    light_room(R, spacing=3.8, energy=1.8, color="#fffaf0", cats=("ceilinglight", "panellight"))
    R.run("N", ["galley"], gap=0.03, spacing=0.02, pred=lambda m: m["mount"] == "floor" and m["size"][0] <= 1.7 and m["size"][1] > 0.7)
    R.run("W", ["galley"], gap=0.03, spacing=0.02, pred=lambda m: m["mount"] == "floor" and m["size"][0] <= 1.7 and m["size"][1] > 0.7)
    isl = R.place(c.pick("galley", label="island"), R.cx + 1.5, R.cz, 0.0) or R.place(c.pick("galley", pred=by_size(minw=1.2)), R.cx + 1.5, R.cz, 0.0)
    tabletop(R, isl, ["tableware"], 4)
    R.run("S", ["galley"], gap=0.03, spacing=0.02, pred=lambda m: m["mount"] == "floor" and m["size"][0] <= 1.6, start=R.x0 + 0.5, end=R.x1 - 3)
    R.run("E", ["storagebin", "shelving"], gap=0.03, start=R.z0 + 0.5, end=R.z1 - 3.0, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.6)
    dress_walls(R, ("wallpanel", "pipe"), sides="NWS")
    dress_ceiling(R, 3)
    ceiling_runs(R, "duct", "x", 1)
    safety(R, "E", R.z1 - 1.0)


def f_mess(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.4, color="#fff4e4")
    ix0, iz0, ix1, iz1 = R.inner(0.6)
    # rows of mess tables with benches
    for tx in (R.x0 + 4.0, R.x0 + 8.4, R.x0 + 12.4):
        for tz in (R.z0 + 3.4, R.z0 + 7.6, R.z0 + 11.8, R.z0 + 15.0):
            t = R.place(c.pick("table", pred=lambda m: 1.3 < m["size"][0] < 3.2 and m["size"][2] < 1.2), tx, tz, 90.0)
            if t:
                fp = t["_fp"]
                tabletop(R, t, ["tableware"], 3)
                for sx in (fp[0] - 0.42, fp[2] + 0.42):
                    R.place(c.pick("bench", pred=by_size(maxw=2.8)), sx, (fp[1] + fp[3]) / 2, 90.0 if sx < tx else -90.0)
    R.run("W", ["galley"], gap=0.05, start=R.z0 + 1, end=R.z0 + 7, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.7 and m["size"][1] > 1.0)
    R.run("W", ["wallpanel", "display"], wall_mount=True, y=1.9)
    R.run("N", ["display", "noticeboard"], wall_mount=True, y=1.8)
    R.run("S", ["wallpanel", "display"], wall_mount=True, y=1.8)
    R.run("E", ["wallpanel", "clock", "sconce"], wall_mount=True, y=1.9)
    for z in (R.z0 + 1.0, R.z1 - 1.0):
        R.against_wall("E", c.pick("plant"), z)
    dress_ceiling(R, 5)
    ceiling_runs(R, "duct", "x", 1)
    signs(R, "E", R.cz, "mess")


def f_rec(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.5)
    R.run("W", ["gym"], gap=0.1, spacing=0.4, limit=4, pred=lambda m: m["mount"] == "floor")
    R.run("N", ["gym"], gap=0.1, spacing=0.4, limit=4, pred=lambda m: m["mount"] == "floor")
    R.grid(["gym"], R.x0 + 5.5, R.z0 + 2.5, R.x1 - 2.5, R.z1 - 2.5, 3, 3)
    R.run("S", ["bench", "locker"], gap=0.05, spacing=0.1, start=R.x0 + 0.5, end=R.x1 - 3, pred=lambda m: m["mount"] == "floor")
    R.run("E", ["display", "wallpanel"], wall_mount=True, y=1.9)
    R.run("W", ["wallpanel"], wall_mount=True)
    R.run("N", ["wallpanel"], wall_mount=True)
    R.against_wall("S", c.pick("fountain"), R.x1 - 1.5) if c.pick("fountain") else None
    dress_ceiling(R, 3)


def f_dorm(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.1, color="#ffe8d0")
    R.run("W", ["bed"], gap=0.03, spacing=0.9, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.4)
    R.run("E", ["bed"], gap=0.03, spacing=0.9, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.4)
    R.run("N", ["locker"], gap=0.03, spacing=0.05, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.2)
    R.run("S", ["locker"], gap=0.03, spacing=0.05, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.2, start=R.x0 + 0.5, end=R.x1 - 3.0)
    t = R.place(c.pick("table", pred=by_size(maxw=1.6)), R.cx - 2, R.cz, 0.0)
    tabletop(R, t, ["tableware", "lamp"], 2)
    R.place(c.pick("chair"), R.cx - 2, R.cz - 1.0, 180.0)
    R.place(c.pick("chair"), R.cx - 2, R.cz + 1.0, 0.0)
    R.place(c.pick("couch", pred=by_size(maxw=2.4)), R.cx + 3, R.cz, -90.0)
    R.run("N", ["display", "wallpanel", "noticeboard"], wall_mount=True, y=1.9)
    R.run("S", ["wallpanel", "clock"], wall_mount=True, y=1.9)
    R.run("W", ["sconce", "wallpanel"], wall_mount=True, y=1.9)
    R.against_wall("W", c.pick("plant"), R.z1 - 1.0)
    dress_ceiling(R, 3)


def f_brig(R, B):
    c = B.cat
    light_room(R, spacing=4.2, energy=1.4, color="#f0e8ff")
    # a row of cells along the bow wall
    for k in range(3):
        x = R.x0 + 2.8 + k * 4.6
        cell = R.against_wall("N", c.pick("cell", pred=by_size(maxw=4.6, maxd=3.4, minh=1.6)), x, gap=0.0)
    ff = c.pick("forcefield", pred=lambda m: m["mount"] == "floor")
    for k in range(3):
        R.place(c.pick("forcefield", pred=lambda m: m["mount"] == "floor"), R.x0 + 2.8 + k * 4.6, R.z0 + 4.6, 0.0)
    R.place(c.pick("desk", pred=by_size(minw=1.4)), R.cx + 4, R.z1 - 2.0, 180.0)
    R.place(c.pick("chair"), R.cx + 4, R.z1 - 3.2, 0.0)
    R.run("W", ["camera"], wall_mount=True, y=2.7)
    R.run("E", ["display", "controlpanel"], wall_mount=True, y=1.7, start=R.z0 + 5, end=R.z1 - 1)
    R.run("S", ["wallpanel", "sign"], wall_mount=True, y=1.9)
    dress_ceiling(R, 4)
    ceiling_runs(R, "cabletray", "x", 1)
    cam = c.pick("camera", pred=lambda m: m["mount"] == "ceiling")
    R.place(cam, R.cx, R.cz, 0.0, y=R.y + R.h, check=False)
    R.omni(R.cx, R.y + 2.5, R.cz, "#ff5544", 0.6, 7.0)


def f_secoff(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.4)
    for k in range(3):
        d = R.against_wall("N", c.pick("desk", pred=by_size(minw=1.3, maxw=2.2)), R.x0 + 3.0 + k * 4.6, gap=0.5)
        if d:
            R.place(c.pick("chair"), (d["_fp"][0] + d["_fp"][2]) / 2, d["_fp"][3] + 0.6, 180.0)
            tabletop(R, d, ["terminal", "lamp"], 2)
    R.run("S", ["locker", "weaponrack"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.4, start=R.x0 + 0.5, end=R.x1 - 4.5)
    R.place(c.pick("holo"), R.cx + 1.5, R.cz + 1.5, 0.0)
    R.run("W", ["display", "noticeboard", "wallpanel"], wall_mount=True, y=1.9)
    R.run("E", ["display", "camera", "wallpanel"], wall_mount=True, y=1.9)
    dress_ceiling(R, 4)


def f_medbay(R, B):
    c = B.cat
    light_room(R, spacing=4.0, energy=1.9, color="#f4ffff", cats=("ceilinglight", "panellight"))
    for k in range(4):
        b = R.against_wall("E", c.pick("medbed", pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.6), R.z0 + 2.6 + k * 3.3, gap=0.9)
        if b:
            R.against_wall("E", c.pick("medscanner", pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.2), R.z0 + 2.6 + k * 3.3, gap=0.0)
    # surgery
    R.place(c.pick("medbed", label="surg"), R.x0 + 4.6, R.z0 + 3.4, 0.0)
    R.place(c.pick("surgical", pred=lambda m: m["mount"] == "floor"), R.x0 + 3.0, R.z0 + 3.4, 90.0)
    R.place(c.pick("medscanner", pred=lambda m: m["mount"] == "floor" and m["size"][0] > 1.5), R.x0 + 8.0, R.z0 + 9.0, 0.0)
    R.run("N", ["medcabinet"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.4, start=R.x0 + 0.5, end=R.x1 - 5)
    R.run("W", ["medcabinet", "medscanner"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.4, start=R.z0 + 8, end=R.z1 - 1)
    for k in range(2):
        R.place(c.pick("cryo", pred=lambda m: m["mount"] == "floor"), R.x0 + 3.5 + k * 2.6, R.z1 - 2.2, 180.0)
    R.run("S", ["medsupply", "medcabinet"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.2, start=R.x0 + 9, end=R.x1 - 1)
    R.run("N", ["display", "medscanner"], wall_mount=True, y=1.9, start=R.x1 - 5, end=R.x1 - 0.5)
    R.run("S", ["display", "wallpanel"], wall_mount=True, y=1.9)
    R.run("E", ["display", "wallpanel"], wall_mount=True, y=2.0)
    R.run("W", ["display", "wallpanel"], wall_mount=True, y=2.0)
    for k in range(4):
        R.place(c.pick("surgical", pred=lambda m: m["mount"] == "ceiling"), R.x1 - 3.5, R.z0 + 2.6 + k * 3.3, 0.0, y=R.y + R.h, check=False)
    dress_ceiling(R, 4)
    R.omni(R.cx, R.y + 1.8, R.cz, "#66ffee", 0.7, 8.0)


def f_sci(R, B):
    c = B.cat
    light_room(R, spacing=4.0, energy=1.8, color="#f2fff4", cats=("ceilinglight", "panellight"))
    for k in range(3):
        b = R.place(c.pick("labbench", pred=lambda m: m["mount"] == "floor" and m["size"][0] > 1.5), R.cx - 3 + k * 4.6, R.cz, 0.0)
        tabletop(R, b, ["microscope", "specimen", "sciinstrument", "analyzer"], 3)
    R.run("N", ["analyzer", "labbench"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.7, start=R.x0 + 0.5, end=R.x1 - 0.5)
    R.run("S", ["analyzer", "specimen", "labbench"], gap=0.03, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 1.7, start=R.x0 + 0.5, end=R.x1 - 3)
    R.run("W", ["particle", "telescope"], gap=0.05, pred=lambda m: m["mount"] == "floor", limit=2)
    R.run("E", ["display", "wallpanel", "sciinstrument"], wall_mount=True, y=1.9)
    R.run("W", ["wallpanel", "display"], wall_mount=True, y=1.9)
    R.run("N", ["wallpanel", "display"], wall_mount=True, y=2.0)
    R.run("S", ["wallpanel", "noticeboard"], wall_mount=True, y=1.9)
    dress_ceiling(R, 4)
    ceiling_runs(R, "cabletray", "x", 1)
    safety(R, "S", R.x1 - 1.0)


def f_hydro(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.4, color="#f0ffe8", cats=("ceilinglight",))
    for i, x in enumerate((R.x0 + 3.2, R.x0 + 7.2, R.x0 + 11.2)):
        for z in (R.z0 + 2.6, R.z0 + 6.6):
            R.place(c.pick("planter", pred=lambda m: m["mount"] == "floor"), x, z, 0.0)
    R.run("N", ["planter"], gap=0.05, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 2.6)
    R.run("W", ["watertank", "scrubber"], gap=0.05, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 2.4, start=R.z0 + 1, end=R.z1 - 1)
    R.run("S", ["planter", "cylinder"], gap=0.05, pred=lambda m: m["mount"] == "floor" and m["size"][0] < 2.6, start=R.x0 + 0.5, end=R.x1 - 4)
    b = R.place(c.pick("bench", pred=by_size(maxw=2.2)), R.x1 - 3.0, R.cz, -90.0)
    R.run("E", ["planter"], gap=0.05, pred=lambda m: m["mount"] == "floor", start=R.z0 + 1, end=R.cz - 3, limit=3)
    for x in (R.x0 + 4, R.x0 + 8, R.x0 + 12):
        for z in (R.z0 + 2.6, R.z0 + 6.6):
            g = c.pick("planter", pred=lambda m: m["mount"] == "ceiling")
            R.place(g, x, z, 0.0, y=R.y + R.h, check=False)
    R.run("W", ["planter", "wallpanel"], wall_mount=True, y=1.6)
    R.run("S", ["duct", "wallpanel"], wall_mount=True, y=2.0)
    R.run("E", ["wallpanel", "sconce"], wall_mount=True, y=1.9)
    ceiling_runs(R, "duct", "x", 1)
    dress_ceiling(R, 3)
    R.omni(R.cx, R.y + 2.5, R.cz, "#99ff88", 0.8, 9.0)
