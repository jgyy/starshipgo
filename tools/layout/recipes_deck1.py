"""Room recipes - Deck 1 (Command Deck)."""
from dressing import *   # noqa: F401,F403
from shiplib import FACE_YAW, WALL_T


def seat_behind(R, con, cats=("seat",), yaw=None, gap=0.55, pred=None):
    if con is None:
        return None
    fp = con["_fp"]
    m = R.cat.pick_any(list(cats), pred=pred, rng=R.rng)
    if m is None:
        return None
    x = (fp[0] + fp[2]) / 2
    return R.place(m, x, fp[3] + gap + m["size"][2] / 2, 180.0 if yaw is None else yaw)


def f_bridge(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.5, color="#e6eeff")
    # forward stations facing the big window
    for x in (-6.6, -2.2, 2.2, 6.6):
        con = R.against_wall("N", c.pick("console", pred=by_size(maxw=2.6)), x, gap=0.55)
        seat_behind(R, con, pred=lambda s: "captain" not in s["id"])
    # command area
    cap = c.pick("seat", label="captain")
    R.place(cap, 0, -29.4, 180.0)
    for x in (-2.0, 2.0):
        R.place(c.pick("seat", pred=lambda s: "captain" not in s["id"] and s["size"][0] < 1.0), x, -29.9, 180.0)
    R.place(c.pick("holo"), 0, -26.4, 0.0)
    # side stations
    for side, yaw in (("W", None), ("E", None)):
        R.run(side, ["console"], start=-37.4, end=-27.4, gap=0.06, pred=by_size(maxw=2.4), spacing=0.15)
        R.run(side, ["display"], start=-38, end=-26, wall_mount=True, y=2.7, pred=by_size(maxw=2.6, maxh=1.4))
        R.run(side, ["controlpanel"], start=-27, end=-24.5, wall_mount=True)
    # rear stations flanking the door
    for x in (-6.5, 6.5):
        con = R.against_wall("S", c.pick("console", pred=by_size(maxw=2.4)), x, gap=0.06)
        seat_behind(R, con, yaw=0.0, gap=-1.3)
    R.run("S", ["display", "controlpanel"], start=-9.8, end=-2.5, wall_mount=True, y=2.4)
    R.run("S", ["display", "controlpanel"], start=2.5, end=9.8, wall_mount=True, y=2.4)
    for _ in range(3):
        R.place(c.pick("terminal", pred=lambda t: t["mount"] == "floor"), R.rng.uniform(-7, 7), -26.0, 180.0)
    for i in range(6):
        R.place(c.pick("instrument", pred=lambda t: t["mount"] == "floor"), R.rng.uniform(-8, 8), R.rng.uniform(-36, -26), 0)
    dress_walls(R, ("wallpanel", "pipe"), sides="WE")
    dress_ceiling(R, 10)
    ceiling_runs(R, "cabletray", "x", 2)
    for x in (-6, 0, 6):
        R.omni(x, R.y + 1.4, -34, "#3399ff", 0.7, 6.0)
    signs(R, "S", 0, "bridge")


def f_cor1(R, B):
    corridor(R, B, "command")


def corridor(R, B, dept):
    """Generic spine corridor dressing (4 m wide, long)."""
    c = B.cat
    light_room(R, spacing=5.0, cats=("ceilinglight", "panellight"), energy=1.3, shadow_every=2)
    for s in "WE":
        # ribs / pillars against the walls
        z = R.z0 + 1.2
        while z < R.z1 - 1.0:
            m = c.pick("pillar", pred=lambda p: p["mount"] == "floor" and p["size"][0] <= 0.9)
            if m:
                R.against_wall(s, m, z, gap=0.0)
            z += 6.0
        R.run(s, ["wallpanel"], wall_mount=True, spacing=0.02)
        R.run(s, ["pipe", "cabletray"], wall_mount=True, y=2.85, spacing=0.05, pred=lambda p: p["mount"] == "wall")
    # central deck plates
    z = R.z0 + 1.0
    while z < R.z1 - 1.0:
        m = c.pick("floorpanel", pred=by_size(maxw=2.1))
        if m:
            R.place(m, R.cx, z + m["size"][2] / 2, 0.0, check=False)
            z += max(m["size"][2], 1.0) + 0.02
        else:
            break
    ceiling_runs(R, "duct", "x" if R.w > R.d else "y", 1)
    dress_ceiling(R, 10)
    for zz in (R.z0 + 8, R.z0 + 30):
        safety(R, "W", zz)
        safety(R, "E", zz + 4)
    cam = c.pick("camera", pred=lambda m: m["mount"] == "ceiling")
    if cam:
        R.place(cam, R.cx, R.z0 + 3, 0.0, y=R.y + R.h, check=False)
        R.place(c.pick("camera", pred=lambda m: m["mount"] == "ceiling"), R.cx, R.z1 - 3, 0.0, y=R.y + R.h, check=False)
    beacon = c.pick("beacon")
    if beacon and beacon["mount"] == "ceiling":
        R.place(beacon, R.cx, R.cz, 0.0, y=R.y + R.h, check=False)


def f_ready(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.3, color="#ffe8cc")
    d = R.against_wall("W", c.pick("desk", pred=by_size(minw=1.4)), R.cz - 1.0, gap=0.5)
    if d:
        R.place(c.pick("chair"), d["_fp"][2] + 0.7, (d["_fp"][1] + d["_fp"][3]) / 2, 90.0)
        tabletop(R, d, ["tableware", "terminal", "lamp", "instrument"], 3)
    R.place(c.pick("chair"), R.x0 + 7.0, R.cz - 1.5, -90.0)
    R.place(c.pick("chair"), R.x0 + 7.0, R.cz + 0.5, -90.0)
    R.against_wall("E", c.pick("couch", pred=by_size(minw=1.6)), R.cz + 2.5)
    tbl = R.place(c.pick("table", pred=by_size(maxw=1.5)), R.x1 - 3.4, R.cz + 2.5, 90.0)
    tabletop(R, tbl, ["tableware", "lamp"], 3)
    R.against_wall("S", c.pick("plant"), R.x0 + 1.0)
    R.against_wall("S", c.pick("plant"), R.x1 - 1.0)
    R.against_wall("N", c.pick("locker", pred=by_size(minw=0.8)), R.cx - 3)
    R.against_wall("N", c.pick("locker", pred=by_size(minw=0.8)), R.cx + 3)
    R.run("N", ["display", "noticeboard", "clock"], start=R.cx - 1.5, end=R.cx + 1.5, wall_mount=True, y=1.9)
    R.run("E", ["display", "wallpanel"], wall_mount=True, spacing=0.05)
    R.run("W", ["wallpanel"], wall_mount=True, spacing=0.05)
    dress_ceiling(R, 4)
    signs(R, "E", R.cz, "command")


def f_conf(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.5)
    t = R.place(c.pick("table", pred=by_size(minw=2.4)), R.cx, R.cz, 0.0)
    if t:
        fp = t["_fp"]
        hw, hd = (fp[2] - fp[0]) / 2, (fp[3] - fp[1]) / 2
        chairs_around(R, R.cx, R.cz, hw, hd, cats=("chair",), step=1.05)
        tabletop(R, t, ["tableware", "terminal", "instrument"], 4)
    R.run("E", ["display"], start=R.cz - 3, end=R.cz + 3, wall_mount=True, y=1.9, pred=by_size(minw=1.5))
    R.run("N", ["display", "noticeboard"], wall_mount=True, y=1.9)
    R.run("S", ["display", "wallpanel"], wall_mount=True, y=1.7)
    R.run("W", ["wallpanel", "display"], wall_mount=True)
    R.against_wall("E", c.pick("plant"), R.z0 + 1.5)
    R.against_wall("E", c.pick("plant"), R.z1 - 1.5)
    R.place(c.pick("holo"), R.cx, R.cz, 0.0, y=R.y + 0.9, check=False)
    dress_ceiling(R, 4)


def f_lounge(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.2, color="#ffe2b8", cats=("ceilinglight",))
    # sofas facing the windows
    for z in (-3.0, -8.0):
        R.place(c.pick("couch", pred=by_size(minw=1.6)), R.x0 + 2.8, z, 90.0)
    for z in (-1.0, -5.5, -9.5):
        t = R.place(c.pick("table", pred=by_size(maxw=1.3)), R.x0 + 4.6, z, 0.0)
        tabletop(R, t, ["tableware", "lamp"], 2)
    for z in (-10.5, 0.0):
        R.place(c.pick("chair", pred=by_size(maxw=1.0)), R.x0 + 6.4, z, -90.0)
    # bar along the east side
    bar = R.against_wall("E", c.pick("table", pred=by_size(minw=2.0)), R.cz - 2, gap=0.3)
    if bar:
        tabletop(R, bar, ["tableware"], 5)
        for k in range(3):
            R.place(c.pick("couch", pred=lambda m: m["size"][0] < 0.7), bar["_fp"][0] - 0.5, R.cz - 3.3 + k * 1.2, 90.0)
    R.against_wall("E", c.pick("galley", pred=by_size(maxw=1.6, minh=1.5)), R.cz + 3.5)
    R.against_wall("N", c.pick("plant"), R.x1 - 1.0)
    R.against_wall("S", c.pick("plant"), R.x0 + 1.0)
    for z in (R.z0 + 3, R.z1 - 3):
        R.place(c.pick("lamp", pred=lambda l: l["mount"] == "floor"), R.x1 - 1.2, z, 0.0)
    R.run("N", ["display", "wallpanel"], wall_mount=True)
    R.run("S", ["wallpanel", "noticeboard"], wall_mount=True)
    R.run("E", ["wallpanel", "sconce"], wall_mount=True, y=2.0)
    dress_ceiling(R, 4)
    signs(R, "E", R.cz + 2, "lounge")


def f_comms(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.5, color="#e4ecff")
    R.run("E", ["rack"], gap=0.05, pred=by_size(maxw=1.0), limit=7)
    R.run("N", ["commsunit"], wall_mount=True, y=1.6)
    R.run("N", ["rack"], gap=0.05, start=R.x0 + 1.0, end=R.x0 + 6.0)
    for k in range(3):
        con = R.place(c.pick("console", pred=by_size(maxw=2.4)), R.cx - 2 + k * 3.0, R.cz + 1.5, 180.0)
        R.place(c.pick("seat"), R.cx - 2 + k * 3.0, R.cz + 3.3, 0.0)
    R.run("W", ["display", "controlpanel"], wall_mount=True, y=1.9)
    R.run("S", ["commsunit", "router"], wall_mount=True, y=1.7)
    d = R.against_wall("S", c.pick("desk"), R.cx + 3.0, gap=0.3)
    if d:
        R.place(c.pick("chair"), (d["_fp"][0] + d["_fp"][2]) / 2, d["_fp"][1] - 0.6, 180.0)
        tabletop(R, d, ["terminal", "commsunit", "router"], 3)
    ant = c.pick("antenna", pred=lambda a: a["mount"] == "floor")
    R.place(ant, R.x0 + 1.5, R.z1 - 1.5, 0.0)
    dress_ceiling(R, 4)
    ceiling_runs(R, "cabletray", "x", 2)


def f_astro(R, B):
    c = B.cat
    light_room(R, spacing=5.0, energy=1.0, color="#bcd4ff")
    globe = c.pick("holo", label="star")
    R.place(globe, R.cx, R.cz, 0.0)
    ang = 0
    import math
    for k in range(6):
        a = math.radians(k * 60 + 30)
        x, z = R.cx + 3.6 * math.cos(a), R.cz + 3.6 * math.sin(a)
        con = R.place(c.pick("console", pred=by_size(maxw=2.0)), x, z, math.degrees(math.atan2(R.cx - x, R.cz - z)) + 180)
    R.place(c.pick("telescope"), R.x1 - 1.6, R.z0 + 1.8, 90.0)
    R.run("W", ["display"], wall_mount=True, y=2.0, pred=by_size(minw=1.2))
    R.run("N", ["display", "controlpanel"], wall_mount=True, y=1.9)
    R.run("S", ["display", "controlpanel"], wall_mount=True, y=1.9)
    dress_ceiling(R, 4)
    R.omni(R.cx, R.y + 1.6, R.cz, "#55aaff", 1.5, 7.0)


def cabin(R, B, bed_side="W"):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.2, color="#ffe8d0")
    n = 2 if R.d >= 10 else 1
    beds = []
    for k in range(2):
        z = R.z0 + 2.4 + k * (R.d - 4.8)
        b = R.against_wall("W", c.pick("bed", pred=lambda m: m["size"][0] < 1.4), z, gap=0.02)
        beds.append(b)
        R.against_wall("W", c.pick("locker", pred=by_size(maxw=1.0)), z + 1.9 if k == 0 else z - 1.9, gap=0.02)
    for k in range(2):
        z = R.z0 + 3.4 + k * (R.d - 6.8)
        d = R.against_wall("E", c.pick("desk", pred=by_size(maxw=1.7)), z, gap=0.05)
        if d:
            R.place(c.pick("chair"), d["_fp"][0] - 0.6, z, 90.0)
            tabletop(R, d, ["lamp", "terminal", "tableware"], 2)
    R.against_wall("N", c.pick("plant"), R.cx)
    R.run("N", ["display", "wallpanel"], wall_mount=True, spacing=0.05)
    R.run("S", ["wallpanel", "noticeboard", "clock"], wall_mount=True)
    R.run("W", ["wallpanel", "sconce"], wall_mount=True, y=1.9)
    R.run("E", ["wallpanel"], wall_mount=True)
    dress_ceiling(R, 3)


def f_cabin1(R, B): cabin(R, B)
def f_cabin2(R, B): cabin(R, B)


def f_capt(R, B):
    c = B.cat
    light_room(R, spacing=4.6, energy=1.2, color="#ffe4c8")
    R.against_wall("W", c.pick("bed", label="captain"), R.z0 + 3.0, gap=0.05)
    R.against_wall("W", c.pick("locker", pred=by_size(minw=0.8)), R.z0 + 6.0)
    R.against_wall("W", c.pick("locker", pred=by_size(minw=0.8)), R.z0 + 7.5)
    d = R.against_wall("N", c.pick("desk", pred=by_size(minw=1.4)), R.cx + 2.5, gap=0.4)
    if d:
        R.place(c.pick("chair"), (d["_fp"][0] + d["_fp"][2]) / 2, d["_fp"][3] + 0.6, 180.0)
        tabletop(R, d, ["lamp", "terminal", "instrument", "tableware"], 3)
    R.place(c.pick("couch", pred=by_size(minw=1.6)), R.x1 - 4.0, R.cz + 2.0, -90.0)
    t = R.place(c.pick("table", pred=by_size(maxw=1.4)), R.x1 - 6.2, R.cz + 2.0, 0.0)
    tabletop(R, t, ["tableware", "lamp"], 3)
    R.place(c.pick("chair"), R.x1 - 6.2, R.cz + 3.6, 180.0)
    R.place(c.pick("chair"), R.x1 - 6.2, R.cz + 0.4, 0.0)
    for x in (R.x0 + 1.0, R.x1 - 1.0):
        R.against_wall("S", c.pick("plant"), x)
    R.run("W", ["display", "wallpanel"], start=R.z0 + 9, wall_mount=True)
    R.run("S", ["wallpanel", "noticeboard"], wall_mount=True)
    R.run("N", ["wallpanel", "sconce"], wall_mount=True, y=1.9)
    dress_ceiling(R, 4)


def f_lobby1(R, B):
    lobby(R, B)


def lobby(R, B):
    c = B.cat
    light_room(R, spacing=4.4, energy=1.4, cats=("ceilinglight", "panellight"))
    R.run("N", ["wallpanel", "display"], wall_mount=True, spacing=0.05, y=1.7)
    R.run("S", ["wallpanel", "display", "noticeboard"], wall_mount=True, spacing=0.05, y=1.7)
    for s in "WE":
        R.run(s, ["controlpanel", "display"], wall_mount=True, start=R.z0 + 0.3, end=R.z0 + 3.0, y=1.5)
        R.run(s, ["controlpanel", "display"], wall_mount=True, start=R.z1 - 3.0, end=R.z1 - 0.3, y=1.5)
    R.against_wall("S", c.pick("couch", pred=by_size(minw=1.4)), R.cx - 2.5)
    R.against_wall("S", c.pick("couch", pred=by_size(minw=1.4)), R.cx + 2.5)
    R.against_wall("S", c.pick("plant"), R.cx)
    R.against_wall("W", c.pick("fountain"), R.z0 + 1.5)
    R.against_wall("E", c.pick("vending"), R.z0 + 1.6)
    R.against_wall("E", c.pick("bin"), R.z1 - 1.0)
    dress_ceiling(R, 3)
    safety(R, "N", R.x0 + 1.0)
    signs(R, "N", R.cx, None)


def f_liftA1(R, B): lift_car(R, B)
def f_liftB1(R, B): lift_car(R, B)


def lift_car(R, B):
    c = B.cat
    R.lights.append({"type": "omni", "pos": [R.cx, R.y + R.h - 0.4, R.cz], "energy": 1.0, "color": "#e8f2ff", "range": 5.0, "shadow": False})
    m = c.pick("ceilinglight", pred=lambda m: m["size"][0] < 1.3)
    if m:
        R.place(m, R.cx, R.cz, 0.0, y=R.y + R.h, check=False)
    side = "E" if R.cx < 0 else "W"
    far = "W" if R.cx < 0 else "E"
    R.run(far, ["controlpanel"], wall_mount=True, start=R.cz - 0.4, end=R.cz + 0.4, y=1.3, pred=by_size(maxw=0.9))
    R.run("N", ["wallpanel", "display"], wall_mount=True, pred=by_size(maxw=1.5), y=1.5)
    R.run("S", ["wallpanel"], wall_mount=True, pred=by_size(maxw=1.5), y=1.5)
    R.run(far, ["wallpanel", "display"], wall_mount=True, pred=by_size(maxw=1.5))
