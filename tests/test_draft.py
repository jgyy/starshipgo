"""Tests for the drafting tool (tools/draft): builds every drawing sheet from the committed ship.json.

    python -m unittest tests.test_draft        (or: python tests/test_draft.py)

Pure standard library; must finish in well under a minute.
"""
import math
import os
import re
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SHIP = os.path.join(ROOT, "godot", "data", "ship.json")
CATALOG = os.path.join(ROOT, "godot", "data", "catalog.json")
sys.path.insert(0, os.path.join(ROOT, "tools", "draft"))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))

import draft  # noqa: E402
import shipmodel as model  # noqa: E402

SVG = "{http://www.w3.org/2000/svg}"


def build(outdir):
    ship = model.Ship(SHIP, CATALOG)
    draft.main(["--ship", SHIP, "--catalog", CATALOG, "--out", outdir])
    return ship


def read_all(outdir):
    out = {}
    for n in sorted(os.listdir(outdir)):
        with open(os.path.join(outdir, n), "rb") as f:
            out[n] = f.read()
    return out


class DraftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp1 = tempfile.TemporaryDirectory()
        cls.tmp2 = tempfile.TemporaryDirectory()
        t0 = time.time()
        cls.ship = build(cls.tmp1.name)
        cls.elapsed = time.time() - t0
        build(cls.tmp2.name)
        cls.files = read_all(cls.tmp1.name)
        cls.files2 = read_all(cls.tmp2.name)
        cls.svgs = {n: b for n, b in cls.files.items() if n.endswith(".svg")}

    @classmethod
    def tearDownClass(cls):
        cls.tmp1.cleanup()
        cls.tmp2.cleanup()

    def test_sheet_count(self):
        self.assertGreaterEqual(len(self.svgs), 100)
        nrooms = len(self.ship.rooms)
        self.assertEqual(sum(1 for n in self.svgs if n.startswith("R-")), 3 * nrooms)
        for k in range(1, 17):
            self.assertTrue(any(n.startswith("G-%02d_" % k) for n in self.svgs), "missing G-%02d" % k)
        for rid in ("bridge", "mess", "towerA2", "hangar"):
            for suf in ("P", "SL", "ST"):
                self.assertTrue(any(n.startswith("R-%s-%s_" % (rid, suf)) for n in self.svgs), (rid, suf))

    def test_well_formed_with_title_block(self):
        numbers = []
        for name, data in self.svgs.items():
            root = ET.fromstring(data)                      # raises on malformed XML
            self.assertEqual(root.tag, SVG + "svg", name)
            vb = [float(v) for v in root.get("viewBox").split()]
            self.assertEqual(vb, [0.0, 0.0, 420.0, 297.0], name)
            self.assertEqual(root.get("width"), "420mm")
            texts = [("".join(t.itertext())) for t in root.iter(SVG + "text")]
            self.assertIn("STARSHIPGO", texts, name)
            self.assertIn("DRAWING TITLE", texts, name)
            num = name.split("_", 1)[0]
            self.assertIn(num, texts, name + ": sheet number in the title block")
            numbers.append(num)
            self.assertIsNone(re.search(r"\b(nan|inf)\b", data.decode()), name + ": NaN / inf coordinate")
        self.assertEqual(len(numbers), len(set(numbers)), "sheet numbers must be unique")

    def test_deterministic(self):
        self.assertEqual(sorted(self.files), sorted(self.files2))
        for n in self.files:
            self.assertEqual(self.files[n], self.files2[n], n)

    def test_index_lists_every_sheet(self):
        idx = self.files["INDEX.md"].decode()
        for n in self.svgs:
            self.assertIn("(%s)" % n, idx, n)
        for head in ("General arrangement", "Deck 1", "Deck 2", "Deck 3"):
            self.assertIn("## " + head, idx)

    def test_size_budget(self):
        total = sum(len(b) for b in self.files.values())
        self.assertLess(total, 25 * 1024 * 1024)

    def test_runtime(self):
        self.assertLess(self.elapsed, 60.0)

    def test_prop_footprints_match_shiplib(self):
        """Footprints in the drawings use the same origin / centre offset as shiplib.Room.footprint."""
        import shiplib
        n = 0
        for room in self.ship.rooms:
            for p in room.props:
                m = p.m
                lo, hi = m["bounds_min"], m["bounds_max"]
                sc = p.d.get("scale", 1.0)
                ox, oz = shiplib.rot((lo[0] + hi[0]) / 2 * sc, (lo[2] + hi[2]) / 2 * sc, p.yaw)
                cx, cz = p.pos[0] + ox, p.pos[2] + oz
                self.assertAlmostEqual(p.cx, cx, 6)
                self.assertAlmostEqual(p.cz, cz, 6)
                ref = shiplib.obb_corners(cx, cz, (hi[0] - lo[0]) / 2 * sc, (hi[2] - lo[2]) / 2 * sc, p.yaw)
                for a in p.corners:
                    self.assertTrue(any(math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-6 for b in ref))
                n += 1
        self.assertGreater(n, 0)

    def test_prop_heights(self):
        for room in self.ship.rooms:
            for p in room.props:
                lo, hi = p.m["bounds_min"][1], p.m["bounds_max"][1]
                sc = p.d.get("scale", 1.0)
                self.assertAlmostEqual(p.y0, p.pos[1] + lo * sc, 6)
                self.assertAlmostEqual(p.y1, p.pos[1] + hi * sc, 6)
                if p.mount == "floor":                                # floor props stand on (or just above) the floor
                    self.assertTrue(room.y - 0.05 <= p.y0 <= room.top, (room.id, p.id, p.y0))

    def test_room_sheet_scales_are_standard(self):
        ok = {"1:20", "1:25", "1:50", "1:75", "1:100", "1:150", "1:200", "1:250", "1:300"}
        for n, data in self.svgs.items():
            if n.startswith("R-"):
                root = ET.fromstring(data)
                texts = ["".join(t.itertext()) for t in root.iter(SVG + "text")]
                self.assertTrue(any(t in ok for t in texts), n)


if __name__ == "__main__":
    unittest.main()
