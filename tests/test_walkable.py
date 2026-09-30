"""Every room of every deck must be reachable on foot (player capsule radius 0.32 m)."""
import collections
import json
import math
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GODOT = os.path.join(ROOT, "godot")
CELL = 0.2
T = 0.15
RADIUS = 0.30


def load(n):
    with open(os.path.join(GODOT, "data", n)) as f:
        return json.load(f)


def rot(x, z, yaw):
    t = math.radians(yaw)
    return (math.cos(t) * x + math.sin(t) * z, -math.sin(t) * x + math.cos(t) * z)


class Grid:
    def __init__(self, x0, z0, x1, z1):
        self.x0, self.z0 = x0, z0
        self.nx, self.nz = int((x1 - x0) / CELL) + 1, int((z1 - z0) / CELL) + 1
        self.free = [[False] * self.nz for _ in range(self.nx)]

    def idx(self, x, z):
        return int(round((x - self.x0) / CELL)), int(round((z - self.z0) / CELL))

    def rect(self, x0, z0, x1, z1, value):
        i0, j0 = self.idx(x0, z0)
        i1, j1 = self.idx(x1, z1)
        for i in range(max(i0, 0), min(i1, self.nx - 1) + 1):
            row = self.free[i]
            for j in range(max(j0, 0), min(j1, self.nz - 1) + 1):
                row[j] = value


class WalkTests(unittest.TestCase):
    def test_all_rooms_reachable(self):
        ship, cat = load("ship.json"), {m["id"]: m for m in load("catalog.json")["models"]}
        for deck in ship["decks"]:
            rooms = [r for r in ship["rooms"] if r["deck"] == deck["id"]]
            xs = [r["rect"][0] for r in rooms] + [r["rect"][2] for r in rooms]
            zs = [r["rect"][1] for r in rooms] + [r["rect"][3] for r in rooms]
            g = Grid(min(xs) - 1, min(zs) - 1, max(xs) + 1, max(zs) + 1)
            for r in rooms:
                x0, z0, x1, z1 = r["rect"]
                g.rect(x0 + T + RADIUS, z0 + T + RADIUS, x1 - T - RADIUS, z1 - T - RADIUS, True)
            for r in rooms:
                x0, z0, x1, z1 = r["rect"]
                for o in r["openings"]:
                    if o["kind"] == "window":
                        continue
                    hw = o["w"] / 2 - 0.2
                    c = o["c"]
                    s = o["side"]
                    if s in "NS":
                        b = z0 if s == "N" else z1
                        g.rect(c - hw, b - T - RADIUS, c + hw, b + T + RADIUS, True)
                    else:
                        b = x0 if s == "W" else x1
                        g.rect(b - T - RADIUS, c - hw, b + T + RADIUS, c + hw, True)
            for r in rooms:
                for p in r["props"]:
                    m = cat[p["m"]]
                    if not (p.get("solid", m["solid"]) and m["size"][1] > 0.35 and (m["size"][0] > 0.25 or m["size"][2] > 0.25)):
                        continue
                    if m["mount"] != "floor":
                        continue
                    lo, hi = m["bounds_min"], m["bounds_max"]
                    pts = [rot(x * 0.95, z * 0.95, p["yaw"]) for x in (lo[0], hi[0]) for z in (lo[2], hi[2])]
                    px, _, pz = p["pos"]
                    g.rect(px + min(q[0] for q in pts) - RADIUS, pz + min(q[1] for q in pts) - RADIUS,
                           px + max(q[0] for q in pts) + RADIUS, pz + max(q[1] for q in pts) + RADIUS, False)
            lobby = next(r for r in rooms if r["id"].startswith("lobby"))
            sx, sz = (lobby["rect"][0] + lobby["rect"][2]) / 2, lobby["rect"][1] + 1.0
            start = g.idx(sx, sz)
            self.assertTrue(g.free[start[0]][start[1]], f"lobby start blocked on deck {deck['id']}")
            seen = {start}
            dq = collections.deque([start])
            while dq:
                i, j = dq.popleft()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    a, b = i + di, j + dj
                    if 0 <= a < g.nx and 0 <= b < g.nz and g.free[a][b] and (a, b) not in seen:
                        seen.add((a, b))
                        dq.append((a, b))
            for r in rooms:
                x0, z0, x1, z1 = r["rect"]
                got = sum(1 for (i, j) in seen if x0 <= g.x0 + i * CELL <= x1 and z0 <= g.z0 + j * CELL <= z1)
                self.assertGreater(got, 12, f"room {r['id']} (deck {deck['id']}) is not reachable on foot")


if __name__ == "__main__":
    unittest.main()
