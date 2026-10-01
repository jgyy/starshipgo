"""Texture library tests.

Header-level checks (existence, power-of-two square sizes, counts, index.json) run on bare Python.  Pixel checks
(normal length, tiling seams, NaN / black, ORM range) need numpy + pillow and are skipped without them.
"""
import json
import os
import struct
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEX = os.path.join(ROOT, "godot", "textures")
SURF = os.path.join(TEX, "surfaces")
SCR = os.path.join(TEX, "screens")
sys.path.insert(0, os.path.join(ROOT, "blender"))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))

try:
    import numpy as np
    from PIL import Image
except ImportError:
    np = Image = None

with open(os.path.join(SURF, "index.json")) as _fh:
    INDEX = json.load(_fh)


def png_size(path):
    with open(path, "rb") as fh:
        head = fh.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", path
    return struct.unpack(">II", head[16:24])


def pot(n):
    return n > 0 and n & (n - 1) == 0


def sets():
    return sorted(INDEX)


class HeaderTests(unittest.TestCase):
    def test_counts(self):
        ext = [k for k, v in INDEX.items() if v["group"] != "legacy"]
        self.assertGreaterEqual(len(ext), 60, "at least 60 new surface sets")
        screens = [f for f in os.listdir(SCR) if f.endswith(".png")]
        self.assertGreaterEqual(len(screens), 21 + 30, "at least 30 new screen textures")

    def test_every_set_has_three_square_pot_pngs(self):
        for name in sets():
            sizes = set()
            for k in ("albedo", "normal", "orm"):
                p = os.path.join(SURF, f"{name}_{k}.png")
                self.assertTrue(os.path.exists(p), p)
                w, h = png_size(p)
                self.assertEqual(w, h, p)
                self.assertTrue(pot(w), p)
                self.assertLessEqual(w, 1024, p)
                sizes.add(w)
            self.assertEqual(len(sizes), 1, name)
            self.assertEqual(sizes.pop(), INDEX[name]["size"], name)

    def test_no_orphan_surface_files(self):
        names = set(INDEX)
        for f in os.listdir(SURF):
            if f.endswith(".png"):
                base = f.rsplit("_", 1)[0]
                self.assertIn(base, names, f)

    def test_screens_are_256(self):
        for f in os.listdir(SCR):
            if f.endswith(".png"):
                self.assertEqual(png_size(os.path.join(SCR, f)), (256, 256), f)

    def test_total_size_budget(self):
        total = sum(os.path.getsize(os.path.join(SURF, f)) for f in os.listdir(SURF))
        self.assertLess(total, 40e6, "surface textures should stay below 40 MB")

    def test_generator_registry_matches_disk(self):
        try:
            from starship import textures_ext, textures, screen_families
        except ImportError:
            self.skipTest("numpy missing")
        for name in textures_ext.REG:
            self.assertIn(name, INDEX)
        for name in textures.SCREENS:
            self.assertTrue(os.path.exists(os.path.join(SCR, name + ".png")), name)
        for v in screen_families.all_variants():
            self.assertIn(v, textures.SCREENS, "screen family variant has no generator")

    def test_index_tile_sizes(self):
        for name, v in INDEX.items():
            self.assertGreater(v["tile_m"], 0, name)


@unittest.skipUnless(np is not None, "numpy / pillow not installed")
class PixelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = {}

    def load(self, name, kind):
        key = (name, kind)
        if key not in self.cache:
            self.cache[key] = np.asarray(Image.open(os.path.join(SURF, f"{name}_{kind}.png")).convert("RGB"), np.float32) / 255
        return self.cache[key]

    def test_normals_unit_length(self):
        for name in sets():
            n = self.load(name, "normal") * 2 - 1
            ln = np.linalg.norm(n, axis=2)
            self.assertLess(abs(float(ln.mean()) - 1), 0.03, name)
            self.assertGreater(float(n[..., 2].min()), 0.0, name + ": normal pointing into the surface")

    def test_normals_are_gentle(self):
        """Anti-flicker: the steepest texel stays below ~50 degrees, the mean tilt is small."""
        for name in sets():
            n = self.load(name, "normal") * 2 - 1
            tilt = np.degrees(np.arccos(np.clip(n[..., 2] / np.maximum(np.linalg.norm(n, axis=2), 1e-6), -1, 1)))
            legacy = INDEX[name]["group"] == "legacy"          # older hand-written sets: pre-filtered, but steeper
            self.assertLess(float(tilt.max()), 78.0 if legacy else 62.0, name)
            self.assertLess(float(tilt.mean()), 18.0 if legacy else 14.0, name)

    def test_tileable(self):
        """The wrap-around step (last -> first column / row) is no bigger than the biggest step inside the image:
        no seam.  (Features centred on the tile edge, e.g. a panel groove, make the step large inside as well.)"""
        for name in sets():
            for kind in ("albedo", "normal", "orm"):
                a = self.load(name, kind)
                for axis in (0, 1):
                    step = np.abs(np.diff(a, axis=axis))
                    wrap = float(np.abs(np.take(a, 0, axis=axis) - np.take(a, -1, axis=axis)).mean())
                    if kind == "normal":
                        # a groove centred on the tile edge flips the normal across the edge: compare with the
                        # steepest single step anywhere in the map
                        limit = float(step.max()) + 0.01
                    else:
                        limit = float(step.mean(axis=(1 - axis, 2)).max()) * 1.5 + 0.01
                    self.assertLess(wrap, limit, f"{name}_{kind} axis {axis}: wrap step {wrap:.4f} vs limit {limit:.4f}")

    def test_not_black_not_nan(self):
        for name in sets():
            a = self.load(name, "albedo")
            self.assertTrue(np.isfinite(a).all(), name)
            self.assertGreater(float(a.max()), 0.04, name + " albedo is black")
            self.assertGreater(float(a.mean()), 0.015, name)

    def test_orm_ranges(self):
        for name in sets():
            o = self.load(name, "orm")
            self.assertGreater(float(o[..., 0].min()), 0.1, name + " occlusion")
            self.assertGreaterEqual(float(o[..., 1].min()), 0.03, name + " roughness never mirror-smooth")
            self.assertLessEqual(float(o[..., 1].max()), 1.0, name)
            self.assertLessEqual(float(o[..., 2].max()), 1.0, name)

    def test_roughness_is_band_limited(self):
        """Specular anti-aliasing: roughness must not hold 1-px, high contrast detail."""
        for name in sets():
            r = self.load(name, "orm")[..., 1]
            hp = float(np.abs(r - 0.25 * (np.roll(r, 1, 0) + np.roll(r, -1, 0) + np.roll(r, 1, 1) + np.roll(r, -1, 1))).mean())
            self.assertLess(hp, 0.03, f"{name}: roughness high-frequency energy {hp:.4f}")

    def test_neutral_sets_are_tint_friendly(self):
        for name, v in INDEX.items():
            if v["neutral"]:
                a = self.load(name, "albedo")
                self.assertGreater(float(a.mean()), 0.7, name)
                self.assertLess(float((a.max(axis=2) - a.min(axis=2)).mean()), 0.05, name + " should be neutral grey")
                r = self.load(name, "orm")[..., 1]
                self.assertGreater(float(r.min()), 0.55, name)


if __name__ == "__main__":
    unittest.main()
