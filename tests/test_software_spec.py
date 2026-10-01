"""Software specification: every application has a section, texture mapping is complete, output is deterministic."""
import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "specs"))
import gen_software  # noqa: E402
import software_data as sd  # noqa: E402

REQUIRED = """starmap nav sensors tactical warp reactor power engineering lifesupport hydroponics medical science comms security cargo fabricator
galley vending alert computer deckplan logbook roster clock atmosphere docking diagnostics datapad holo""".split()
EXISTING_TEXTURES = """radar waveform graph text starmap schematic bars warp vitals power nav alert tactical systems lifesigns comm medical periodic hazard
diagnostic globe""".split()


def read_text(path):
    with open(path) as f:
        return f.read()


class SoftwareSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "godot", "data", "software.json")) as f:
            cls.sw = json.load(f)
        cls.doc = read_text(os.path.join(ROOT, "docs", "SOFTWARE_SPEC.md"))
        cls.ids = [a["id"] for a in cls.sw["apps"]]

    def test_required_apps(self):
        self.assertEqual(sorted(self.ids), sorted(REQUIRED))
        self.assertEqual(len(set(self.ids)), len(self.ids))

    def test_schema(self):
        self.assertEqual(self.sw["version"], 1)
        self.assertEqual(self.sw["fallback"], "computer")
        for a in self.sw["apps"]:
            for k in ("id", "title", "version", "category", "description", "screen_textures", "categories", "rooms", "hosts"):
                self.assertIn(k, a, a["id"])
            self.assertTrue(a["description"])
            self.assertTrue(a["rooms"])
        cats = {c["id"] for c in self.sw["categories"]}
        for a in self.sw["apps"]:
            self.assertIn(a["category"], cats)

    def test_every_app_has_a_section(self):
        for i in self.ids:
            self.assertRegex(self.doc, r"(?m)^### 4\.\d+ `%s` - " % re.escape(i), i)
        for needle in ("Layout", "Widgets", "Data sources", "Interactions", "Alarms", "Effects on the game world", "Performance budget", "Accessibility",
                       "Acceptance tests"):
            self.assertEqual(self.doc.count("**" + needle), len(self.ids) if needle != "Interactions" else len(self.ids), needle)
        for sec in ("Visual language", "Input model", "Shared state", "Persistence", "Data schemas", "Error handling", "QA matrix", "Glossary"):
            self.assertIn(sec, self.doc)

    def test_texture_map(self):
        tm = self.sw["texture_map"]
        for t in EXISTING_TEXTURES:
            self.assertIn(t, tm)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "godot", "textures", "screens", t + ".png")), t)
        for t, a in tm.items():
            self.assertIn(a, self.ids, t)
        for k, a in self.sw["texture_prefix_map"].items():
            self.assertTrue(k.startswith("scr_"), k)
            self.assertIn(a, self.ids, k)
        # screen_textures of the apps agree with the texture map
        for a in self.sw["apps"]:
            for t in a["screen_textures"]:
                self.assertEqual(tm[t], a["id"])
        # every texture that exists on disk resolves to some app
        for f in os.listdir(os.path.join(ROOT, "godot", "textures", "screens")):
            if f.endswith(".png"):
                self.assertIn(sd.resolve_app(f[:-4]), self.ids, f)

    def test_resolution_order(self):
        self.assertEqual(sd.resolve_app("radar"), "sensors")
        self.assertEqual(sd.resolve_app("scr_reactor_core_2"), "reactor")
        self.assertEqual(sd.resolve_app("reactor_core_2"), "reactor")
        self.assertEqual(sd.resolve_app("screen_nav"), "nav")
        self.assertEqual(sd.resolve_app("totally_unknown", "vending"), "vending")
        self.assertEqual(sd.resolve_app("totally_unknown", "chair"), "computer")

    def test_deterministic_and_up_to_date(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            pa, ja = gen_software.write_all(a)
            pb, jb = gen_software.write_all(b)
            self.assertEqual(read_text(pa), read_text(pb))
            self.assertEqual(read_text(ja), read_text(jb))
            self.assertEqual(read_text(pa), self.doc)
            self.assertEqual(read_text(ja), read_text(os.path.join(ROOT, "godot", "data", "software.json")))

    def test_wireframes_and_acceptance(self):
        for a in sd.APPS:
            self.assertGreaterEqual(len(a["wireframe"].splitlines()), 5, a["id"])
            self.assertTrue(a["accept"], a["id"])
            self.assertTrue(a["widgets"] and a["data"] and a["interactions"], a["id"])


if __name__ == "__main__":
    unittest.main()
