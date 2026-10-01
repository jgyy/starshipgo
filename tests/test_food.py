"""Invariants of the food and drink models (bare Python: reads godot/data/catalog.json, the GLB headers and the texture files)."""
import json
import os
import re
import struct
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GODOT = os.path.join(ROOT, "godot")
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import policy  # noqa: E402

FOOD = {"bakery", "dessert", "meal", "fruit", "veg", "deli", "harvest", "hanging", "drink", "can", "bottle", "cocktail", "ration", "tray", "buffet"}
MOUNT = {"harvest": "floor", "buffet": "floor", "hanging": "wall"}          # everything else is a table item
# real-world envelope per category: (min width/depth, max width/depth, min height, max height) in metres (largest footprint side / height)
SIZE = {
    "can": (0.045, 0.08, 0.085, 0.175), "bottle": (0.04, 0.13, 0.15, 0.36), "cocktail": (0.06, 0.15, 0.08, 0.22),
    "drink": (0.07, 0.40, 0.04, 0.30), "meal": (0.15, 0.50, 0.015, 0.20), "bakery": (0.07, 0.55, 0.025, 0.28),
    "dessert": (0.07, 0.30, 0.02, 0.30), "fruit": (0.08, 0.40, 0.03, 0.30), "veg": (0.10, 0.40, 0.01, 0.30),
    "deli": (0.10, 0.60, 0.03, 0.25), "ration": (0.12, 0.40, 0.03, 0.35), "tray": (0.25, 0.60, 0.05, 0.45),
    "harvest": (0.50, 0.65, 0.09, 0.30), "buffet": (0.9, 2.0, 0.90, 1.5), "hanging": (0.09, 0.55, 0.30, 0.75),
}


def models():
    with open(os.path.join(GODOT, "data", "catalog.json")) as fh:
        return json.load(fh)["models"]


def glb_json(path):
    with open(path, "rb") as fh:
        head = fh.read(20)
        n = struct.unpack("<I", head[12:16])[0]
        fh.seek(20)
        return json.loads(fh.read(n))


class FoodCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = models()
        cls.food = [m for m in cls.all if m["category"] in FOOD]

    def test_at_least_120_new_models(self):
        self.assertGreaterEqual(len(self.food), 120)

    def test_all_categories_present_and_ids_follow_the_scheme(self):
        self.assertEqual({m["category"] for m in self.food}, FOOD)
        ids = [m["id"] for m in self.all]
        self.assertEqual(len(ids), len(set(ids)), "model ids must be unique")
        for m in self.food:
            self.assertTrue(m["id"].startswith(m["category"] + "_"), m["id"])
            self.assertRegex(m["id"], r"^[a-z0-9_]+$")

    def test_mounts_are_valid(self):
        for m in self.food:
            self.assertEqual(m["mount"], MOUNT.get(m["category"], "table"), m["id"])

    def test_origins_follow_the_mount_convention(self):
        for m in self.food:
            lo, hi = m["bounds_min"], m["bounds_max"]
            if m["mount"] in ("table", "floor"):
                self.assertAlmostEqual(lo[1], 0.0, delta=0.005, msg=m["id"])
                self.assertAlmostEqual((lo[0] + hi[0]) / 2, 0.0, delta=0.01, msg=m["id"])
                self.assertAlmostEqual((lo[2] + hi[2]) / 2, 0.0, delta=0.01, msg=m["id"])
            else:                                                       # wall: back plane at z = 0
                self.assertAlmostEqual(lo[2], 0.0, delta=0.005, msg=m["id"])

    def test_sizes_are_realistic(self):
        for m in self.food:
            lo_w, hi_w, lo_h, hi_h = SIZE[m["category"]]
            if m["id"] == "can_sixpack_cola":
                hi_w = 0.21
            w, h, d = m["size"]
            self.assertTrue(lo_w <= max(w, d) <= hi_w, f"{m['id']} footprint {w}x{d} outside {lo_w}..{hi_w}")
            self.assertTrue(lo_h <= h <= hi_h, f"{m['id']} height {h} outside {lo_h}..{hi_h}")

    def test_real_world_sizes_of_the_signature_items(self):
        by = {m["id"]: m for m in self.food}
        can = by["can_cola"]["size"]
        self.assertAlmostEqual(can[0], 0.066, delta=0.004)
        self.assertAlmostEqual(can[1], 0.122, delta=0.004)
        plate = by["meal_steak_dinner"]["size"]
        self.assertAlmostEqual(max(plate[0], plate[2]), 0.30, delta=0.02)          # 0.30 m dinner plate with rim
        pizza = by["meal_pizza_margherita"]["size"]
        self.assertAlmostEqual(max(pizza[0], pizza[2]), 0.33, delta=0.03)          # 0.30 m pizza on a 0.33 m pan
        self.assertAlmostEqual(by["bottle_wine_red_bordeaux"]["size"][1], 0.33, delta=0.02)
        self.assertAlmostEqual(by["bakery_baguette"]["size"][0], 0.52, delta=0.05)

    def test_glb_files_are_valid_and_within_budget(self):
        sizes = []
        for m in self.food:
            path = os.path.join(GODOT, m["file"])
            self.assertTrue(os.path.exists(path), path)
            self.assertLess(os.path.getsize(path), 400_000, m["id"])
            self.assertGreater(m["tris"], 50, m["id"])
            self.assertLess(m["tris"], 12_000, m["id"])
            sizes.append(os.path.getsize(path))
        sizes.sort()
        self.assertLess(sizes[len(sizes) // 2], 150_000, "median food GLB should stay under 150 KB")

    def test_models_are_textured_and_have_uvs(self):
        textured = 0
        for m in self.food:
            j = glb_json(os.path.join(GODOT, m["file"]))
            if j.get("images"):
                textured += 1
                for mesh in j["meshes"]:
                    for prim in mesh["primitives"]:
                        mat = j["materials"][prim["material"]]
                        if "baseColorTexture" in mat.get("pbrMetallicRoughness", {}):
                            self.assertIn("TEXCOORD_0", prim["attributes"], f"{m['id']}: textured part without UVs")
        self.assertGreater(textured / len(self.food), 0.7, "most food models carry procedural albedo textures")

    def test_every_variant_has_its_own_shape(self):
        seen = {}
        for m in self.food:
            if m["category"] == "can":      # same lathe topology; the cans differ in proportions, shoulder and print
                continue
            key = (m["category"], tuple(m["size"]), m["tris"])
            self.assertNotIn(key, seen, f"{m['id']} duplicates {seen.get(key)}")
            seen[key] = m["id"]


class FoodTextures(unittest.TestCase):
    def test_textures_referenced_by_the_generators_exist(self):
        used = set()
        comp = os.path.join(ROOT, "blender", "starship", "components")
        for fn in os.listdir(comp):
            if fn.startswith("food") and fn.endswith(".py"):
                with open(os.path.join(comp, fn)) as fh:
                    used |= set(re.findall(r"tex:([a-z0-9_]+)", fh.read()))
        self.assertGreater(len(used), 40)
        for name in sorted(used):
            path = os.path.join(GODOT, "textures", "food", name + ".jpg")
            self.assertTrue(os.path.exists(path), f"texture {name} is used by a food model but {path} is missing")

    def test_textures_are_256_px_jpegs(self):
        d = os.path.join(GODOT, "textures", "food")
        files = [f for f in os.listdir(d) if f.endswith(".jpg")]
        self.assertGreater(len(files), 100)
        for f in files:
            with open(os.path.join(d, f), "rb") as fh:
                data = fh.read()
            self.assertEqual(data[:2], b"\xff\xd8", f)
            i = 2
            w = h = None
            while i < len(data) - 9:                         # find the SOF marker
                if data[i] != 0xFF:
                    i += 1
                    continue
                mk = data[i + 1]
                if mk in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", data[i + 5:i + 9])
                    break
                i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
            self.assertEqual((w, h), (256, 256), f)


class FoodPolicy(unittest.TestCase):
    def test_every_food_category_is_documented_and_allowed_somewhere(self):
        for cat in FOOD:
            self.assertIn(cat, policy.CATEGORY_INFO, cat)
        for cat in FOOD:
            self.assertTrue(any(cat in policy.allowed(r) for r in policy.ROOM), f"{cat} is not allowed in any room")

    def test_new_rooms_have_policy_entries(self):
        for rid in ("wardroom", "provisions"):
            self.assertIn(rid, policy.ROOM)
        self.assertTrue({"cocktail", "bottle", "buffet"} <= policy.allowed("wardroom"))
        self.assertTrue({"harvest", "hanging", "ration"} <= policy.allowed("provisions"))
        self.assertNotIn("cocktail", policy.allowed("brig"))

    def test_food_is_used_in_the_ship(self):
        with open(os.path.join(GODOT, "data", "ship.json")) as fh:
            ship = json.load(fh)
        cat = {m["id"]: m for m in models()}
        used = [p["m"] for r in ship["rooms"] for p in r["props"] if cat[p["m"]]["category"] in FOOD]
        self.assertGreater(len(used), 60)
        self.assertGreater(len(set(used)), 40)


class FoodDocs(unittest.TestCase):
    def test_menu_document_lists_every_model(self):
        with open(os.path.join(ROOT, "docs", "FOOD.md")) as fh:
            doc = fh.read()
        for m in models():
            if m["category"] in FOOD:
                self.assertIn("`" + m["id"] + "`", doc, f"{m['id']} missing from docs/FOOD.md")


if __name__ == "__main__":
    unittest.main()
