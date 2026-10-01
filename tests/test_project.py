"""Invariants of the generated content. Run:  python -m unittest discover -s tests -v"""
import json
import math
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GODOT = os.path.join(ROOT, "godot")
TARGET = int(re.search(r"^TARGET = (\d+)", open(os.path.join(ROOT, "blender", "build_all.py")).read(), re.M).group(1))


def load(name):
    with open(os.path.join(GODOT, "data", name)) as f:
        return json.load(f)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load("catalog.json")
        cls.models = cls.cat["models"]

    def test_exact_model_count(self):
        self.assertEqual(len(self.models), TARGET)
        self.assertEqual(self.cat["count"], TARGET)

    def test_ids_unique(self):
        ids = [m["id"] for m in self.models]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_glb_exists_and_is_valid(self):
        for m in self.models:
            path = os.path.join(GODOT, m["file"])
            self.assertTrue(os.path.exists(path), path)
            with open(path, "rb") as f:
                head = f.read(12)
            self.assertEqual(head[:4], b"glTF", m["id"])
            self.assertEqual(int.from_bytes(head[4:8], "little"), 2, m["id"])
            self.assertEqual(int.from_bytes(head[8:12], "little"), os.path.getsize(path), m["id"])

    def test_no_orphan_glbs(self):
        on_disk = set()
        for base, _, files in os.walk(os.path.join(GODOT, "models")):
            for fn in files:
                if fn.endswith(".glb"):
                    on_disk.add(os.path.relpath(os.path.join(base, fn), GODOT))
        self.assertEqual(on_disk, {m["file"] for m in self.models})

    def test_sane_sizes(self):
        for m in self.models:
            self.assertTrue(all(0.005 < s < 40 for s in m["size"]), m["id"])
            self.assertLess(m["bytes"], 400_000, m["id"])
            self.assertGreater(m["tris"], 20, m["id"])

    def test_mounts(self):
        for m in self.models:
            self.assertIn(m["mount"], ("floor", "wall", "ceiling", "table"), m["id"])

    def test_categories_have_models(self):
        cats = {m["category"] for m in self.models}
        self.assertGreaterEqual(len(cats), 60)


class ShipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship = load("ship.json")
        cls.cat = {m["id"]: m for m in load("catalog.json")["models"]}
        sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
        import hull
        cls.hull = hull

    def test_ship_data_version(self):
        self.assertEqual(self.ship["version"], 2)

    def test_no_unknown_models(self):
        for r in self.ship["rooms"]:
            for p in r["props"]:
                self.assertIn(p["m"], self.cat)
        for d in self.ship["doors"]:
            self.assertIn(d["m"], self.cat)

    def test_placements_are_a_sensible_selection(self):
        """The ship is furnished from bills of materials, not by dumping the catalogue into it."""
        used = {p["m"] for r in self.ship["rooms"] for p in r["props"]} | {d["m"] for d in self.ship["doors"]}
        self.assertGreater(len(used), 300, "too few distinct models placed")
        total = sum(len(r["props"]) for r in self.ship["rooms"])
        self.assertLess(total, 3500, "ship is cluttered")
        self.assertGreater(total, 1000, "ship is bare")

    def test_props_inside_their_room(self):
        for r in self.ship["rooms"]:
            poly = r["poly"]
            for p in r["props"]:
                x, _, z = p["pos"]
                self.assertTrue(self._inside(poly, x, z, -0.4), f"{p['m']} outside {r['id']}")

    @staticmethod
    def _inside(poly, x, z, margin):
        n = len(poly)
        s = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
        sgn = 1 if s > 0 else -1
        for i in range(n):
            ax, az = poly[i]
            bx, bz = poly[(i + 1) % n]
            ln = math.hypot(bx - ax, bz - az) or 1
            if sgn * ((bx - ax) * (z - az) - (bz - az) * (x - ax)) / ln < margin:
                return False
        return True

    def test_decks_and_rooms(self):
        self.assertEqual(len(self.ship["decks"]), 3)
        self.assertGreaterEqual(len(self.ship["rooms"]), 40)
        self.assertGreaterEqual(len(self.ship["doors"]), 25)
        self.assertGreaterEqual(len([c for c in self.ship["cameras"] if not c.get("exterior")]), 20)
        self.assertGreaterEqual(len([c for c in self.ship["cameras"] if c.get("exterior")]), 3)

    def test_rooms_do_not_overlap(self):
        rooms = self.ship["rooms"]
        for i, a in enumerate(rooms):
            for b in rooms[i + 1:]:
                if a["deck"] != b["deck"]:
                    continue
                inter = self.hull.clip_convex([tuple(p) for p in a["poly"]], [tuple(p) for p in b["poly"]])
                ar = self.hull.area(inter) if len(inter) > 2 else 0.0
                self.assertLess(ar, 0.05, f"{a['id']} overlaps {b['id']} by {ar:.2f} m2")

    def test_hull_is_tapered_and_streamlined(self):
        """Every deck outline is convex, tapers to a narrow bow and stern, and the ship is compact."""
        for deck, pts in self.ship["hull"].items():
            pts = [tuple(p) for p in pts]
            self.assertTrue(self.hull.is_convex(pts), f"deck {deck} outline is not convex")
            zs = [p[1] for p in pts]
            xs = [abs(p[0]) for p in pts]
            length, beam = max(zs) - min(zs), 2 * max(xs)
            self.assertLessEqual(length, 60.0)
            self.assertLessEqual(beam, 26.5)
            bow = [abs(p[0]) for p in pts if p[1] < min(zs) + 1.0]
            stern = [abs(p[0]) for p in pts if p[1] > max(zs) - 1.0]
            self.assertLess(max(bow), 4.5, f"deck {deck} bow is not pointed")
            self.assertLess(max(stern), 10.5, f"deck {deck} stern does not taper")
        # rectangular rooms only amidships: bow and stern rooms have diagonal walls
        diag = [r["id"] for r in self.ship["rooms"] if any(e["side"].startswith("D") for e in r["edges"])]
        self.assertGreaterEqual(len(diag), 15)

    def test_overall_size_is_compact(self):
        xs = [p[0] for pts in self.ship["hull"].values() for p in pts]
        zs = [p[1] for pts in self.ship["hull"].values() for p in pts]
        self.assertLessEqual(max(zs) - min(zs), 70.0)       # old ship: ~102 m
        self.assertLessEqual(max(xs) - min(xs), 27.0)       # old ship: 36 m

    def test_stairs_replace_lifts(self):
        self.assertNotIn("lifts", self.ship)
        stairs = self.ship["stairs"]
        self.assertEqual(len(stairs), 2)
        decks = {d["id"]: d["y"] for d in self.ship["decks"]}
        for s in stairs:
            self.assertEqual(len(s["runs"]), 2)
            for run in s["runs"]:
                fa, fb = run["flights"]
                lo, hi = decks[run["deck_lo"]], decks[run["deck_hi"]]
                self.assertAlmostEqual(fa["pos"][1], lo, places=2)
                self.assertAlmostEqual(run["landing"]["y"], lo + 2.0, places=2)
                self.assertAlmostEqual(fb["pos"][1], lo + 2.0, places=2)
                self.assertAlmostEqual(fb["pos"][1] + 2.0, hi, places=2)
                self.assertEqual(round(fa["yaw"] - fb["yaw"]) % 360, 180)
        for r in self.ship["rooms"]:
            if r["id"].startswith("lift"):
                self.fail("lift room still present: " + r["id"])

    def test_stair_shafts_line_up(self):
        towers = {}
        for r in self.ship["rooms"]:
            if r["id"].startswith("tower"):
                towers.setdefault(r["id"][:-1], {})[r["deck"]] = r
        self.assertEqual(set(towers), {"towerA", "towerB"})
        for name, by in towers.items():
            self.assertEqual(set(by), {1, 2, 3})
            rects = {d: r["rect"] for d, r in by.items()}
            self.assertEqual(rects[1], rects[2])
            self.assertEqual(rects[2], rects[3])
            self.assertEqual(by[3]["ceiling_holes"], by[2]["floor_holes"])
            self.assertEqual(by[2]["ceiling_holes"], by[1]["floor_holes"])
            self.assertFalse(by[3]["floor_holes"] or by[1]["ceiling_holes"])

    def test_every_room_has_a_bill_of_materials(self):
        for r in self.ship["rooms"]:
            self.assertTrue(r["bom"], r["id"])
            self.assertTrue(r["brief"].get("purpose"), r["id"])
            codes = {l["code"] for l in r["bom"]}
            for p in r["props"]:
                if p.get("b") != "ARCH":
                    self.assertIn(p.get("b"), codes, f"{p['m']} in {r['id']} has no BOM line")


if __name__ == "__main__":
    unittest.main()
