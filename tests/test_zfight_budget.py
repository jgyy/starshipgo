"""The committed component GLBs stay mostly free of coplanar overlapping faces of different materials (flicker)."""
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "quality"))
import glb_audit  # noqa: E402


class ZFightBudget(unittest.TestCase):
    def test_total_overlapping_coplanar_pairs_stay_small(self):
        total = models = 0
        for base, _, files in os.walk(os.path.join(ROOT, "godot", "models")):
            for fn in files:
                if fn.endswith(".glb"):
                    r = glb_audit.audit_model(os.path.join(base, fn))
                    if r["zfight"]:
                        models += 1
                        total += r["zfight"]
        # before the exporter fix: 23,128 pairs in 570 models
        self.assertLess(total, 4000, "%d coplanar pairs in %d models" % (total, models))
        self.assertLess(models, 130)

    def test_kit_lifts_coplanar_faces(self):
        src = open(os.path.join(ROOT, "blender", "starship", "kit.py"), encoding="utf-8").read()
        self.assertIn("def fix_zfight", src)
        self.assertIn("fix_zfight(model)", src)


if __name__ == "__main__":
    unittest.main()
