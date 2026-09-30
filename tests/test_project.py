"""Invariants of the generated content. Run:  python -m unittest discover -s tests -v"""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GODOT = os.path.join(ROOT, "godot")
TARGET = 1000


def load(name):
    with open(os.path.join(GODOT, "data", name)) as f:
        return json.load(f)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load("catalog.json")
        cls.models = cls.cat["models"]

    def test_exactly_1000_models(self):
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

    def test_all_models_placed(self):
        used = {p["m"] for r in self.ship["rooms"] for p in r["props"]} | {d["m"] for d in self.ship["doors"]}
        missing = set(self.cat) - used
        self.assertFalse(missing, f"{len(missing)} models never placed: {sorted(missing)[:10]}")

    def test_no_unknown_models(self):
        for r in self.ship["rooms"]:
            for p in r["props"]:
                self.assertIn(p["m"], self.cat)

    def test_props_inside_their_room(self):
        for r in self.ship["rooms"]:
            x0, z0, x1, z1 = r["rect"]
            for p in r["props"]:
                x, _, z = p["pos"]
                self.assertTrue(x0 - 0.5 <= x <= x1 + 0.5 and z0 - 0.5 <= z <= z1 + 0.5, f"{p['m']} outside {r['id']}")

    def test_decks_and_rooms(self):
        self.assertEqual(len(self.ship["decks"]), 3)
        self.assertGreaterEqual(len(self.ship["rooms"]), 40)
        self.assertGreaterEqual(len(self.ship["doors"]), 25)
        self.assertGreaterEqual(len(self.ship["cameras"]), 20)

    def test_rooms_do_not_overlap(self):
        rooms = self.ship["rooms"]
        for i, a in enumerate(rooms):
            for b in rooms[i + 1:]:
                if a["deck"] != b["deck"]:
                    continue
                ax0, az0, ax1, az1 = a["rect"]
                bx0, bz0, bx1, bz1 = b["rect"]
                overlap = ax0 < bx1 - 1e-6 and ax1 > bx0 + 1e-6 and az0 < bz1 - 1e-6 and az1 > bz0 + 1e-6
                self.assertFalse(overlap, f"{a['id']} overlaps {b['id']}")

    def test_lifts_align_across_decks(self):
        cars = {}
        for l in self.ship["lifts"]:
            cars.setdefault(l["name"][0], set()).add((l["pos"][0], l["pos"][2]))
        for k, v in cars.items():
            self.assertEqual(len(v), 1, f"lift {k} misaligned")


if __name__ == "__main__":
    unittest.main()
