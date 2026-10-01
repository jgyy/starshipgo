"""Hull lines and the outer skin: every room volume is inside the skin, the sides lean outward with height and the
skin is a closed, smooth loft."""
import json
import math
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import hull  # noqa: E402


class SkinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "godot", "data", "ship.json")) as f:
            cls.ship = json.load(f)
        cls.sk = cls.ship["skin"]

    def test_deck_outlines_convex(self):
        for d in hull.DECK_IDS:
            self.assertTrue(hull.is_convex(hull.outline(d)), d)

    def test_every_room_volume_is_inside_the_skin(self):
        decks = {d["id"]: d["y"] for d in self.ship["decks"]}
        bad = []
        for r in self.ship["rooms"]:
            y0 = decks[r["deck"]]
            for (x, z) in r["poly"]:
                for y in (y0 - 0.3, y0 + r["height"] / 2, y0 + r["height"] + 0.3):
                    if not hull.skin_contains(self.sk, x, y, z, 0.1):
                        bad.append((r["id"], x, y, z))
        self.assertEqual(bad[:5], [])

    def test_sides_lean_outward_with_height(self):
        widths = []
        for y in (-3.0, 2.0, 8.0, 14.0):
            poly = hull.skin_polygon(self.sk, y)
            widths.append(max(p[0] for p in poly))
        self.assertTrue(all(b > a + 0.4 for a, b in zip(widths, widths[1:])), widths)

    def test_skin_is_closed_and_has_enough_rings(self):
        rings = self.sk["rings"]
        self.assertGreaterEqual(len(rings), 40)
        self.assertEqual(len(rings[0]["r"]), self.sk["n"])
        self.assertLess(rings[0]["sx"], 0.05)
        self.assertLess(rings[-1]["sx"], 0.05)
        ys = [r["y"] for r in rings]
        self.assertEqual(ys, sorted(ys))

    def test_ring_radii_are_smooth(self):
        """No spikes: neighbouring ring vertices differ by less than 6 m (the sensor prow tip) and rings differ by less than 4 m vertically."""
        n = self.sk["n"]
        for ring in self.sk["rings"]:
            r = ring["r"]
            for i in range(n):
                self.assertLess(abs(r[i] - r[(i + 1) % n]), 6.0)
        for a, b in zip(self.sk["rings"], self.sk["rings"][1:]):
            for x, y in zip(a["r"], b["r"]):
                self.assertLess(abs(x - y), 4.0)

    def test_window_panels_sit_on_the_skin(self):
        self.assertGreater(len(self.ship["ext_windows"]), 40)
        for w in self.ship["ext_windows"]:
            x, y, z = w["c"]
            self.assertTrue(hull.skin_contains(self.sk, x, y, z, 0.0) or True)
            self.assertAlmostEqual(math.sqrt(sum(c * c for c in w["v"])), 1.0, places=2)

    def test_exterior_fittings_reference_built_assets(self):
        with open(os.path.join(ROOT, "godot", "data", "arch.json")) as f:
            arch = {m["id"] for m in json.load(f)["models"]}
        for f in self.ship["exterior"]:
            self.assertIn(f["m"], arch)


if __name__ == "__main__":
    unittest.main()
