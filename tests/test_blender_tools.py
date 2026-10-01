"""Blender tool / catalog convention tests (stdlib only; bpy-dependent parts are skipped)."""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG = os.path.join(ROOT, "godot", "data", "catalog.json")
TOL = 0.005
TARGET = int(re.search(r"^TARGET = (\d+)", open(os.path.join(ROOT, "blender", "build_all.py")).read(), re.M).group(1))

# Models fixed in this pass (must satisfy their mount convention exactly).
FIXED_FLOOR = ["hangartool_launch_rail_segment", "door_cargo", "crate_pod_pressurised_tall",
               "sciinstrument_sample_drill_rig", "cleaningbot_wall_window_crawler",
               "cell_contraband_xray_table", "cryo_cryo_stasis_pod"]
FIXED_WALL = ["coil_eps_conduit_trunk", "pipe_valve_wheel"]
FIXED_CEILING = ["camera_dome_ceiling", "ceilinglight_flush_dome", "ceilingpanel_dome_light_1x1"]

# kit.snap_origin() puts every model within 4.5 cm of its mount plane exactly on it; what is left is deliberate:
# the hover stretcher floats 5 cm on its thrusters and the damper box is sunk 5 cm into its wall.
ALLOW_FLOOR = {'medsupply_hover_stretcher'}
ALLOW_WALL = {'duct_plenum_damper_box'}
ALLOW_CEILING = set()


def load_models():
    with open(CATALOG) as fh:
        return json.load(fh)["models"]


def violations(models):
    out = {"floor": [], "wall": [], "ceiling": []}
    for e in models:
        lo, hi, mount = e["bounds_min"], e["bounds_max"], e["mount"]
        if mount == "floor" and abs(lo[1]) > TOL:
            out["floor"].append(e["id"])
        elif mount == "wall" and lo[2] < -TOL:
            out["wall"].append(e["id"])
        elif mount == "ceiling" and hi[1] > TOL:
            out["ceiling"].append(e["id"])
    return out


class BuildAllCheck(unittest.TestCase):
    def test_check_runs_without_bpy(self):
        # The system python has no bpy; --check must still plan every model (1000 components + 196 food and drink).
        r = subprocess.run([sys.executable, os.path.join(ROOT, "blender", "build_all.py"), "--check"],
                           capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("%d models" % TARGET, r.stdout)

    def test_kit_imports_without_bpy(self):
        sys.path.insert(0, os.path.join(ROOT, "blender"))
        try:
            from starship import kit
            self.assertTrue(hasattr(kit, "FAMILIES"))
            self.assertTrue(hasattr(kit, "BEVEL_FAILURES"))
        finally:
            sys.path.pop(0)


class CatalogConventions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = load_models()
        cls.by_id = {e["id"]: e for e in cls.models}

    def test_count_and_unique_ids(self):
        self.assertEqual(len(self.models), TARGET)
        self.assertEqual(len(self.by_id), TARGET)

    def test_fixed_floor_models(self):
        for mid in FIXED_FLOOR:
            with self.subTest(mid):
                self.assertEqual(self.by_id[mid]["mount"], "floor")
                self.assertLessEqual(abs(self.by_id[mid]["bounds_min"][1]), TOL)

    def test_fixed_wall_models(self):
        for mid in FIXED_WALL:
            with self.subTest(mid):
                self.assertEqual(self.by_id[mid]["mount"], "wall")
                self.assertGreaterEqual(self.by_id[mid]["bounds_min"][2], -TOL)

    def test_fixed_ceiling_models(self):
        for mid in FIXED_CEILING:
            with self.subTest(mid):
                self.assertEqual(self.by_id[mid]["mount"], "ceiling")
                self.assertLessEqual(self.by_id[mid]["bounds_max"][1], TOL)

    def test_hover_stretcher_hovers_at_most_5cm(self):
        self.assertLessEqual(self.by_id["medsupply_hover_stretcher"]["bounds_min"][1], 0.05 + 1e-6)

    def test_violations_within_allow_list(self):
        v = violations(self.models)
        self.assertLessEqual(len(v["floor"]), len(ALLOW_FLOOR))
        self.assertLessEqual(len(v["wall"]), len(ALLOW_WALL))
        self.assertLessEqual(len(v["ceiling"]), len(ALLOW_CEILING))
        self.assertEqual(set(v["floor"]) - ALLOW_FLOOR, set())
        self.assertEqual(set(v["wall"]) - ALLOW_WALL, set())
        self.assertEqual(set(v["ceiling"]) - ALLOW_CEILING, set())

    def test_violations_are_small(self):
        for e in self.models:
            lo, hi = e["bounds_min"], e["bounds_max"]
            off = {"floor": abs(lo[1]), "wall": max(0.0, -lo[2]), "ceiling": max(0.0, hi[1])}.get(e["mount"], 0)
            self.assertLessEqual(off, 0.06, e["id"])


if __name__ == "__main__":
    unittest.main()
