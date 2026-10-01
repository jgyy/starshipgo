"""Machine datasheets: every catalogue model has a plausible, deterministic spec; docs and BOM columns are consistent."""
import csv
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "specs"))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import gen_specs  # noqa: E402
import gen_ship_spec  # noqa: E402
import gen_lore  # noqa: E402
import specagg  # noqa: E402


def jload(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return json.load(f)


def read_text(path):
    with open(path) as f:
        return f.read()


class SpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = {m["id"]: m for m in jload("godot", "data", "catalog.json")["models"]}
        cls.specs = jload("godot", "data", "specs.json")
        cls.models = cls.specs["models"]

    def test_header(self):
        self.assertEqual(self.specs["version"], 1)
        self.assertEqual(self.specs["currency"], "cr")

    def test_every_model_has_a_spec(self):
        self.assertEqual(set(self.models), set(self.cat))

    def test_plausible_numbers(self):
        pns = set()
        for mid, s in self.models.items():
            m = self.cat[mid]
            self.assertGreater(s["kg"], 0, mid)
            self.assertGreater(s["cr"], 0, mid)
            self.assertTrue(all(x >= 0 for x in s["w"]), mid)
            self.assertLessEqual(s["w"][0], s["w"][1] + 1e-9, mid)
            self.assertLessEqual(s["w"][1], s["w"][2] + 1e-9, mid)
            self.assertEqual(s["dim"], [int(round(v * 1000)) for v in m["size"]], mid)
            self.assertIn(s["r"], "cpgsx")
            self.assertTrue(s["m"] and s["pn"] and s["d"], mid)
            self.assertNotIn(s["pn"], pns)
            pns.add(s["pn"])
            self.assertLessEqual(s["temp"][0], s["temp"][1])
            self.assertGreater(s["lead"], 0)
            if s["r"] == "p":
                self.assertEqual(s["w"], [0, 0, 0], mid)
                self.assertEqual(s["v"], "none")
            if s["r"] == "g":
                self.assertGreater(s["gen"], 0, mid)
            if s["r"] == "s":
                self.assertGreater(s["cap"], 0, mid)
            if s["r"] == "c":
                self.assertGreater(s["w"][1], 0, mid)
                self.assertIn(s["v"].split(" ")[1] if " " in s["v"] else s["v"], ("VDC", "VAC", "kVAC"))
            # bulk density sanity: between 0.5 kg/m3 and 8000 kg/m3 of bounding volume
            vol = m["size"][0] * m["size"][1] * m["size"][2]
            self.assertLess(s["kg"] / max(vol, 1e-4), 9000, mid)

    def test_category_plausibility(self):
        mm = self.models
        self.assertTrue(100 < mm["console_helm"]["kg"] < 600)
        self.assertTrue(1 < mm["display_vitals_monitor"]["kg"] < 15)
        self.assertGreater(mm["reactor_fusion_core_reactor"]["kg"], 10000)
        self.assertGreater(mm["reactor_fusion_core_reactor"]["gen"], 1000)
        self.assertEqual(mm["reactor_fusion_core_reactor"]["r"], "g")
        self.assertEqual(mm["capacitor_battery_rack"]["r"], "s")
        self.assertEqual(mm["chair_stool"]["w"][1], 0)
        self.assertGreater(mm["craft_cargo_shuttle"]["kg"], 10000)

    def test_software_ids_exist(self):
        apps = {a["id"] for a in jload("godot", "data", "software.json")["apps"]}
        for mid, s in self.models.items():
            for a in s["sw"]:
                self.assertIn(a, apps, mid)
        self.assertTrue(any(s["sw"] for s in self.models.values()))
        self.assertEqual(self.models["console_helm"]["sw"][0], "nav")

    def test_deterministic_and_up_to_date(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            gen_specs.write_all(ROOT, a)
            gen_specs.write_all(ROOT, b)
            for rel in ("godot/data/specs.json", "docs/MACHINE_SPECS.md", "docs/specs/specs.csv", "docs/specs/console.md"):
                self.assertEqual(read_text(os.path.join(a, rel)), read_text(os.path.join(b, rel)), rel)
                self.assertEqual(read_text(os.path.join(a, rel)), read_text(os.path.join(ROOT, rel)), "stale " + rel)
            self.assertEqual(sorted(os.listdir(os.path.join(a, "docs", "specs"))), sorted(f for f in os.listdir(os.path.join(ROOT, "docs", "specs"))))

    def test_docs(self):
        cats = {m["category"] for m in self.cat.values()}
        total = 0
        for c in cats:
            p = os.path.join(ROOT, "docs", "specs", c + ".md")
            self.assertTrue(os.path.exists(p), c)
            total += os.path.getsize(p)
        total += os.path.getsize(os.path.join(ROOT, "docs", "specs", "specs.csv"))
        self.assertLess(total, 6 * 1024 * 1024)
        with open(os.path.join(ROOT, "docs", "specs", "specs.csv")) as f:
            rows = list(csv.reader(f))
        self.assertEqual(len(rows) - 1, len(self.cat))
        text = read_text(os.path.join(ROOT, "docs", "MACHINE_SPECS.md"))
        for c in cats:
            self.assertIn("specs/%s.md" % c, text)

    def test_any_catalog_size(self):
        """A smaller / different catalogue (new food categories, a model without a GLB) still works."""
        with tempfile.TemporaryDirectory() as t:
            os.makedirs(os.path.join(t, "godot", "data"))
            cat = {"version": 1, "count": 3, "models": [
                {"id": "food_ramen", "category": "food", "label": "ramen", "file": "models/food/food_ramen.glb", "mount": "table", "tags": ["food"],
                 "solid": False, "size": [0.2, 0.1, 0.2], "tris": 300, "family": "food_table"},
                {"id": "mystery_box", "category": "mystery", "label": "box", "file": "", "mount": "floor", "tags": [], "solid": True,
                 "size": [1, 1, 1], "tris": 0, "family": "gen"},
                {"id": "console_x", "category": "console", "label": "x", "file": "nope.glb", "mount": "floor", "tags": [], "solid": True,
                 "size": [1, 1, 1], "tris": 100, "family": "bridge_console"}]}
            with open(os.path.join(t, "godot", "data", "catalog.json"), "w") as f:
                json.dump(cat, f)
            data = gen_specs.write_all(t)
            self.assertEqual(set(data["models"]), {"food_ramen", "mystery_box", "console_x"})
            for s in data["models"].values():
                self.assertGreater(s["kg"], 0)
                self.assertGreater(s["cr"], 0)
            self.assertEqual(data["models"]["food_ramen"]["cls"], "provision")
            self.assertEqual(data["models"]["console_x"]["sw"], ["nav"])
            self.assertTrue(os.path.exists(os.path.join(t, "docs", "specs", "food.md")))


class ShipSpecTests(unittest.TestCase):
    def test_ship_spec_up_to_date_and_complete(self):
        ship = jload("godot", "data", "ship.json")
        specs = specagg.load_specs(ROOT)
        md = gen_ship_spec.generate(ship, specs, gen_lore.build())
        self.assertEqual(md, read_text(os.path.join(ROOT, "docs", "SHIP_SPEC.md")))
        for d in ship["decks"]:
            self.assertIn("| %d | %s |" % (d["id"], d["name"]), md)
        for r in ship["rooms"]:
            self.assertIn(r["name"], md)
        for h in ("Mass budget", "Electrical power budget", "Thermal budget", "Life-support budget", "Costs", "Maintenance schedule", "Cargo capacity", "Compliance"):
            self.assertIn(h, md)
        self.assertIn("```mermaid", md)

    def test_ship_spec_without_specs_does_not_crash(self):
        ship = jload("godot", "data", "ship.json")
        md = gen_ship_spec.generate(ship, {}, gen_lore.build())
        self.assertIn("Ship Design Specification", md)

    def test_totals_consistent(self):
        ship = jload("godot", "data", "ship.json")
        specs = specagg.load_specs(ROOT)
        tot = specagg.blank()
        for r in ship["rooms"]:
            specagg.merge(tot, specagg.room_totals(r, ship, specs))
        self.assertEqual(tot["n"], sum(len(r["props"]) for r in ship["rooms"]) + len(ship["doors"]))
        self.assertEqual(tot["missing"], 0)
        self.assertGreater(tot["gen_kw"], tot["typ"] / 1000.0, "generation must cover the typical load")


class BomColumnsTests(unittest.TestCase):
    def test_bom_without_specs_degrades(self):
        import bom
        ship, cat = bom.load(ROOT)
        md = bom.generate(ship, cat, {})
        self.assertNotIn("Line subtotal", md)
        self.assertIn("Bill of Materials", md)

    def test_bom_with_specs_has_columns(self):
        text = read_text(os.path.join(ROOT, "docs", "BOM.md"))
        self.assertIn("Line subtotal", text)
        self.assertIn("Installed equipment mass", text)
        with open(os.path.join(ROOT, "docs", "bom", "bill_of_materials.csv")) as f:
            rows = list(csv.DictReader(f))
        self.assertIn("total_mass_kg", rows[0])
        self.assertTrue(all(r["total_price_cr"] for r in rows))

    def test_bom_partial_specs(self):
        import bom
        ship, cat = bom.load(ROOT)
        specs = specagg.load_specs(ROOT)
        some = dict(list(specs.items())[:50])
        md = bom.generate(ship, cat, some)
        self.assertIn("Bill of Materials", md)
        with tempfile.TemporaryDirectory() as t:
            bom.write_csv(ship, cat, t, some)
            self.assertTrue(os.path.exists(os.path.join(t, "bill_of_materials.csv")))


class SpecSheetTests(unittest.TestCase):
    def test_spec_sheets(self):
        sys.path.insert(0, os.path.join(ROOT, "tools", "draft"))
        import shipmodel
        import sheets_spec
        ship = shipmodel.Ship(os.path.join(ROOT, "godot", "data", "ship.json"), os.path.join(ROOT, "godot", "data", "catalog.json"))
        sheets = sheets_spec.spec_sheets(ship)
        nums = [s.num for s in sheets]
        self.assertEqual(len(nums), len(set(nums)))
        self.assertGreaterEqual(len(sheets), 12)
        self.assertEqual(nums[:2], ["S-01", "S-02"])
        for s in sheets:
            svg = s.render()
            self.assertIn("STARSHIPGO", svg)
            self.assertIsNone(re.search(r"\b(nan|inf)\b", svg), s.num)


if __name__ == "__main__":
    unittest.main()
