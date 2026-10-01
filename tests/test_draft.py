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
        for k in range(1, 21):
            self.assertTrue(any(n.startswith("G-%02d_" % k) for n in self.svgs), "missing G-%02d" % k)
        for k in range(1, 1 + len(self.ship.deck_ids)):
            self.assertTrue(any(n.startswith("K-%02d_" % k) for n in self.svgs), "missing K-%02d" % k)
        self.assertEqual(sum(1 for n in self.svgs if n.startswith("K-")), len(self.ship.deck_ids))
        for rid in ("bridge", "mess", "towerA2", "towerA0", "towerB4", "hangar", "starcart", "hold"):
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
        self.assertIn("## General arrangement", idx)
        for d in self.ship.deck_ids:
            self.assertIn("## Deck %d - %s" % (d, self.ship.deck_name[d]), idx)

    def test_size_budget(self):
        total = sum(len(b) for b in self.files.values())
        self.assertLess(total, 25 * 1024 * 1024)

    def test_runtime(self):
        self.assertLess(self.elapsed, 180.0)

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


    # ------------------------------------------------------------------ five decks and the skin
    def test_five_decks_have_sheets(self):
        self.assertEqual(self.ship.deck_ids, sorted(self.ship.deck_ids))
        self.assertGreaterEqual(len(self.ship.deck_ids), 5)
        for d in self.ship.deck_ids:
            hits = [n for n in self.svgs if n.startswith("G-") and "general_arrangement_deck%d." % d in n]
            self.assertEqual(len(hits), 1, d)
            root = ET.fromstring(self.svgs[hits[0]])
            texts = ["".join(t.itertext()) for t in root.iter(SVG + "text")]
            self.assertIn("DECK %d" % d, texts)
            self.assertTrue(any(n.startswith("K-") and "contact_sheet_deck%d." % d in n for n in self.svgs), d)
            for r in self.ship.deck_rooms(d):
                self.assertIn(r.code, texts, (d, r.id))
        idx = self.files["INDEX.md"].decode()
        for r in self.ship.rooms:
            self.assertIn("R-%s-P_" % r.id, idx)

    def test_stair_sheet_shows_every_deck(self):
        data = next(b for n, b in self.svgs.items() if n.startswith("G-13_")).decode()
        for d in self.ship.deck_ids:
            self.assertIn("PLAN - DECK %d " % d, data)
        runs, _ = self.ship.stair_geom("SA")
        self.assertEqual(len(runs), len(self.ship.deck_ids) - 1)

    def test_everything_inside_the_sheet(self):
        """Every drawn element (not text inside clipped groups) has its coordinates inside the 420 x 297 sheet."""
        bad = []
        num = re.compile(r"-?\d+(?:\.\d+)?")

        def check(name, tag, vals):
            for k in range(0, len(vals) - 1, 2):
                if not (-0.01 <= vals[k] <= 420.01 and -0.01 <= vals[k + 1] <= 297.01):
                    bad.append((name, tag, vals[k], vals[k + 1]))
                    return

        def walk(name, el, clipped):
            tag = el.tag.replace(SVG, "")
            if tag in ("defs", "clipPath", "pattern", "style", "title"):
                return
            if el.tag == SVG + "g" and el.get("clip-path"):
                clipped = True
            if not clipped:
                g = lambda k: float(el.get(k, 0))
                if tag == "line":
                    check(name, tag, [g("x1"), g("y1"), g("x2"), g("y2")])
                elif tag in ("polygon", "polyline"):
                    check(name, tag, [float(v) for v in num.findall(el.get("points", ""))])
                elif tag == "rect":
                    check(name, tag, [g("x"), g("y"), g("x") + g("width"), g("y") + g("height")])
                elif tag == "circle":
                    check(name, tag, [g("cx") - g("r"), g("cy") - g("r"), g("cx") + g("r"), g("cy") + g("r")])
                elif tag == "path":
                    check(name, tag, [float(v) for v in num.findall(el.get("d", ""))])
                elif tag == "text":
                    check(name, tag, [g("x"), g("y")])
                elif tag == "image":
                    check(name, tag, [g("x"), g("y"), g("x") + g("width"), g("y") + g("height")])
            for c in el:
                walk(name, c, clipped)

        for name, data in self.svgs.items():
            walk(name, ET.fromstring(data), False)
        self.maxDiff = None
        self.assertEqual(bad[:10], [])

    def test_no_stray_files(self):
        for n in self.files:
            self.assertTrue(n.endswith(".svg") or n == "INDEX.md", n)

    def test_skin_and_fittings_loaded(self):
        sk = self.ship.skin
        self.assertIsNotNone(sk)
        self.assertEqual(len(sk.pts), len(sk.rings))
        self.assertGreater(len(self.ship.fittings), 0)
        ids = {f.id for f in self.ship.fittings}
        for must in ("arch_nacelle_starboard", "arch_deflector", "arch_engine_cluster", "arch_mast", "arch_keel_fin"):
            self.assertIn(must, ids)
        ox0, oy0, oz0, ox1, oy1, oz1 = self.ship.overall()
        self.assertLessEqual(oz0, sk.z0)
        self.assertGreaterEqual(ox1 - ox0, sk.x1 - sk.x0)
        self.assertGreaterEqual(oy1, sk.y1)
        self.assertEqual(self.ship.fp_z, math.floor(oz0))
        zs = [z for k, z in self.ship.station_zs()]
        self.assertTrue(all(abs((b - a) - model.STATION_M) < 1e-9 for a, b in zip(zs, zs[1:])))

    def test_skin_encloses_every_room(self):
        import hull
        sk = self.ship.raw["skin"]
        for r in self.ship.rooms:
            for y in (r.y + 0.1, r.top - 0.1):
                for x, z in r.poly:
                    self.assertTrue(hull.skin_contains(sk, x, y, z), (r.id, x, y, z))

    def test_skin_cut_matches_reference_polygon(self):
        """The cross-section on a plane agrees with the slice of the reference loft at a ring height."""
        import hullview
        from sectionview import Cut
        sk = self.ship.skin
        for z in (-30.0, -6.0, 8.0, 26.0):
            polys = hullview.skin_cut(sk, Cut("z", z))
            self.assertEqual(len(polys), 1, z)
            poly = polys[0]
            for ring, y in list(zip(sk.pts, sk.ys))[8:-8:6]:
                iv = Cut("z", z).iv(ring)
                self.assertIsNotNone(iv)
                # the polygon boundary at height y (left and right side) equals the ring interval
                near = [p for p in poly if abs(p[1] - y) < 1e-6]
                self.assertTrue(near, (z, y))
                self.assertAlmostEqual(min(p[0] for p in near), iv[0], 4)
                self.assertAlmostEqual(max(p[0] for p in near), iv[1], 4)
            hs = [p[0] for p in poly]
            self.assertLessEqual(max(hs), -sk.x0 + 1e-6)
            self.assertGreaterEqual(min(hs), -sk.x1 - 1e-6)
        # centreline section covers the full length
        poly = hullview.skin_cut(sk, Cut("x", 0.0))[0]
        self.assertAlmostEqual(min(p[0] for p in poly), sk.z0, 0)
        self.assertAlmostEqual(max(p[0] for p in poly), sk.z1, 0)
        self.assertEqual(hullview.skin_cut(sk, Cut("z", sk.z1 + 5.0)), [])

    def test_fitting_boxes(self):
        by = {f.id: f for f in self.ship.fittings}
        nac = by["arch_nacelle_starboard"]
        self.assertAlmostEqual(nac.bmin[0], 14.04, 2)
        self.assertAlmostEqual(nac.bmax[0], 14.04 + 15.852, 2)
        self.assertAlmostEqual(nac.size[0], 15.852, 3)
        defl = by["arch_deflector"]
        self.assertAlmostEqual(defl.bmin[2], -60.437 - 1.85, 2)
        cp = nac.cut_poly(lambda x, z: (-x, z - 0.0))
        self.assertIsNotNone(cp)
        self.assertAlmostEqual(max(abs(h) for h, y in cp), 14.04 + 15.852, 2)

    def test_hull_sheets_content(self):
        def texts(prefix):
            n = next(k for k in self.svgs if k.startswith(prefix))
            return "\n".join("".join(t.itertext()) for t in ET.fromstring(self.svgs[n]).iter(SVG + "text")), self.svgs[n].decode()
        t, raw = texts("G-04_")
        self.assertIn("LENGTH OVERALL", t)
        self.assertIn("BEAM OVER NACELLES", t)
        self.assertGreaterEqual(raw.count("<polygon"), 20)           # skin contours + deck outlines + fittings
        t, raw = texts("G-05_")
        self.assertIn("KEEL FIN", t)
        self.assertIn("url(#hGlass)", raw)                           # window panels
        t, raw = texts("G-17_")
        self.assertGreaterEqual(t.count("STATION "), 15)
        t, raw = texts("G-18_")
        for key in ("Length overall", "Beam over nacelles", "Draught", "Decks", "Height, keel (incl. fin) to mast top"):
            self.assertIn(key, t)
        for n in sorted(self.svgs):
            if n.startswith(("G-06_", "G-07_", "G-08_", "G-09_", "G-10_", "G-11_", "G-12_")):
                t, raw = texts(n[:5])
                for d in self.ship.deck_ids:
                    self.assertIn("DECK %d" % d, t, n)
                self.assertIn("SKIN ", t, n)                        # skin dimension present on every section



if __name__ == "__main__":
    unittest.main()
