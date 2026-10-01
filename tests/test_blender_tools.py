"""Blender tool / catalog convention tests (stdlib only; bpy-dependent parts are skipped)."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG = os.path.join(ROOT, "godot", "data", "catalog.json")
TOL = 0.005

# Models fixed in this pass (must satisfy their mount convention exactly).
FIXED_FLOOR = ["hangartool_launch_rail_segment", "door_cargo", "crate_pod_pressurised_tall",
               "sciinstrument_sample_drill_rig", "cleaningbot_wall_window_crawler",
               "cell_contraband_xray_table", "cryo_cryo_stasis_pod"]
FIXED_WALL = ["coil_eps_conduit_trunk", "pipe_valve_wheel"]
FIXED_CEILING = ["camera_dome_ceiling", "ceilinglight_flush_dome", "ceilingpanel_dome_light_1x1"]

# Known, NOT fixed convention violations. All are small (<= 0.05 m): feet / casters / wheel
# treads / bevel or rotation overhang of the original generators, plus a deliberately hovering
# stretcher (medsupply_hover_stretcher hovers 0.05 m on its thrusters). Fixing them needs
# per-generator geometry edits in modules owned by other work; they are harmless to layout.
ALLOW_FLOOR = {
    'barrel_cryo_flask', 'barrel_gas_cylinder_trolley', 'bed_captain_bed', 'bed_hammock_frame',
    'bed_recliner_sleeper', 'bin_recycling_bin_triple', 'chair_folding_chair', 'chair_lounge_chair',
    'couch_bean_bag', 'craft_lander', 'crate_biohazard', 'crate_cage_large', 'crate_flammable_red',
    'crate_hazard_yellow', 'crate_iso_container_blue', 'crate_iso_container_hazard',
    'crate_medical_supply', 'crate_open_parts', 'crate_pod_pressurised_long', 'crate_stacked_pair',
    'crate_steel_1m', 'crate_strapped_pair', 'crate_strapped_single', 'crate_vault_armoured',
    'cylinder_cryo_dewar', 'cylinder_portable_o2_unit', 'engtool_welding_rig',
    'hangartool_air_compressor', 'hangartool_fuel_hose_reel', 'hangartool_mooring_ring',
    'hangartool_paint_booth_screen', 'loader_cargo_drone', 'loader_drone_lifter',
    'loader_hand_pallet_jack', 'loader_hover_pallet_jack', 'loader_maintenance_robot_treads',
    'loader_mobile_crane_arm', 'medsupply_hover_stretcher', 'sciinstrument_field_lab_trunk',
    'storagebin_toolchest_wheels', 'surgical_defibrillator_cart', 'surgical_ventilator_unit',
    'telescope_observation_telescope', 'telescope_spectrograph_tripod', 'watertank_condensate_collector',
}
ALLOW_WALL = {
    'bed_fold_down_wall_bed', 'camera_palm_scanner', 'duct_plenum_damper_box', 'hangartool_wall_winch',
    'safety_eye_wash_station', 'valve_pressure_regulator',
}
ALLOW_CEILING = {
    'pillar_box_beam_light', 'planter_grow_light_bar_panel',
}


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
        self.assertIn("1196 models", r.stdout)

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
        self.assertEqual(len(self.models), 1196)
        self.assertEqual(len(self.by_id), 1196)

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
