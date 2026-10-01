"""Lore and star map data: schema, geometry, ETAs and determinism."""
import json
import math
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "specs"))
import gen_lore  # noqa: E402

KINDS = {"home", "waypoint", "outpost", "anomaly", "uncharted", "hazard"}
STANCES = {"allied", "neutral", "rival", "unknown"}


def load():
    with open(os.path.join(ROOT, "godot", "data", "lore.json")) as f:
        return json.load(f)


def read_text(path):
    with open(path) as f:
        return f.read()


class LoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = load()
        cls.sys = {s["id"]: s for s in cls.d["systems"]}

    def test_committed_matches_generator(self):
        self.assertEqual(self.d, json.loads(json.dumps(gen_lore.build())))

    def test_deterministic_and_up_to_date(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ja, ma = gen_lore.write_all(a)
            jb, mb = gen_lore.write_all(b)
            self.assertEqual(read_text(ja), read_text(jb))
            self.assertEqual(read_text(ma), read_text(mb))
            self.assertEqual(read_text(ja), read_text(os.path.join(ROOT, "godot", "data", "lore.json")))
            self.assertEqual(read_text(ma), read_text(os.path.join(ROOT, "docs", "LORE.md")))

    def test_schema(self):
        d = self.d
        self.assertEqual(d["version"], 1)
        for k in ("name", "registry", "class", "builder", "commissioned", "motto", "crew", "cruise_warp", "top_warp", "ly_per_day_at_cruise", "description"):
            self.assertIn(k, d["ship"])
        self.assertIsInstance(d["ship"]["commissioned"], int)
        self.assertIsInstance(d["ship"]["crew"], int)
        self.assertGreater(d["ship"]["top_warp"], d["ship"]["cruise_warp"])
        self.assertTrue(4 <= len(d["factions"]) <= 6)
        fids = set()
        for f in d["factions"]:
            self.assertRegex(f["color"], r"^#[0-9a-f]{6}$")
            self.assertIn(f["stance"], STANCES)
            fids.add(f["id"])
        self.assertGreaterEqual(len(d["systems"]), 28)
        for s in d["systems"]:
            self.assertEqual(len(s["pos"]), 3)
            for k in ("class", "temp_k", "lum_solar"):
                self.assertIn(k, s["star"])
            self.assertIn(s["faction"], fids)
            self.assertIn(s["kind"], KINDS)
            self.assertIsInstance(s["visited"], bool)
            self.assertTrue(1 <= len(s["planets"]) <= 6, s["id"])
            for p in s["planets"]:
                for k in ("name", "type", "gravity_g", "atmosphere", "habitable", "moons", "notes"):
                    self.assertIn(k, p)
        self.assertEqual(len(self.sys), len(d["systems"]), "duplicate system ids")
        self.assertEqual(sum(1 for s in d["systems"] if s["kind"] == "home"), 1)
        self.assertTrue(any(s["kind"] == "anomaly" for s in d["systems"]))
        self.assertEqual(self.sys[next(s["id"] for s in d["systems"] if s["kind"] == "home")]["pos"], [0, 0, 0])

    def test_volume_radius(self):
        r = max(math.dist((0, 0, 0), s["pos"]) for s in self.d["systems"])
        self.assertLessEqual(r, 60.0)
        self.assertGreaterEqual(r, 35.0)

    def test_routes(self):
        seen = set()
        adj = {}
        for r in self.d["routes"]:
            self.assertIn(r["a"], self.sys)
            self.assertIn(r["b"], self.sys)
            self.assertNotEqual(r["a"], r["b"])
            self.assertTrue(0 <= r["hazard"] <= 5)
            key = tuple(sorted((r["a"], r["b"])))
            self.assertNotIn(key, seen, "duplicate lane")
            seen.add(key)
            true = math.dist(self.sys[r["a"]]["pos"], self.sys[r["b"]]["pos"])
            self.assertLess(abs(r["ly"] - true), 0.01 * true + 1e-9, key)
            adj.setdefault(r["a"], set()).add(r["b"])
            adj.setdefault(r["b"], set()).add(r["a"])
        # every system is reachable from home
        stack, reach = ["tessara"], {"tessara"}
        while stack:
            for v in adj.get(stack.pop(), ()):
                if v not in reach:
                    reach.add(v)
                    stack.append(v)
        self.assertEqual(reach, set(self.sys))

    def test_waypoints_and_eta(self):
        d = self.d
        speed = d["ship"]["ly_per_day_at_cruise"]
        prev = None
        statuses = []
        for wp in d["waypoints"]:
            self.assertIn(wp["system"], self.sys)
            self.assertIn(wp["status"], ("done", "active", "planned"))
            statuses.append(wp["status"])
            if prev:
                ly, _ = gen_lore.shortest_path(d["routes"], prev, wp["system"])
                self.assertIsNotNone(ly)
                self.assertLess(abs(wp["eta_days"] - ly / speed), 0.01 * ly / speed + 0.01)
            else:
                self.assertEqual(wp["eta_days"], 0)
            prev = wp["system"]
        # done ... active ... planned, in that order, exactly one active waypoint
        self.assertEqual(statuses.count("active"), 1)
        self.assertEqual(statuses, sorted(statuses, key=["done", "active", "planned"].index))

    def test_current_position(self):
        d = self.d
        cur = d["current"]
        self.assertIn(cur["system"], self.sys)
        self.assertTrue(self.sys[cur["system"]]["visited"])
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in cur["heading"])), 1.0, places=2)
        active = [w for w in d["waypoints"] if w["status"] == "active"][0]
        self.assertEqual(active["system"], cur["system"])
        for w in d["waypoints"]:
            if w["status"] == "done":
                self.assertTrue(self.sys[w["system"]]["visited"], w["system"])

    def test_logs(self):
        logs = self.d["logs"]
        self.assertGreaterEqual(len(logs), 24)
        roles = {l["role"] for l in logs}
        for r in ("captain", "chief engineer", "science officer", "medical officer", "helm", "quartermaster", "security chief", "hydroponics"):
            self.assertIn(r, roles)
        sd = [float(l["stardate"]) for l in logs]
        self.assertEqual(sd, sorted(sd))
        for l in logs:
            self.assertTrue(len(l["text"]) > 150, l["title"])
        story = [l for l in logs if any(w in l["text"].lower() for w in ("pulse", "heartbeat", "signal"))]
        self.assertGreaterEqual(len(story), 8, "mystery arc")
        ship = json.loads(read_text(os.path.join(ROOT, "godot", "data", "ship.json")))
        rooms = {r["id"] for r in ship["rooms"]}
        used = [l["room"] for l in logs if l["room"]]
        self.assertGreaterEqual(len(used), 20)
        ok = sum(1 for r in used if r in rooms)
        self.assertGreaterEqual(ok / len(used), 0.8, "logs should reference real rooms of ship.json")
        self.assertGreaterEqual(len(set(used)), 10)

    def test_datapads_glossary_timeline(self):
        d = self.d
        self.assertTrue(8 <= len(d["datapads"]) <= 12)
        self.assertEqual(len({p["id"] for p in d["datapads"]}), len(d["datapads"]))
        self.assertGreaterEqual(len(d["glossary"]), 12)
        years = [t["year"] for t in d["timeline"]]
        self.assertEqual(years, sorted(years))
        self.assertGreaterEqual(len(years), 10)
        self.assertIn(d["ship"]["commissioned"], years)

    def test_no_trademarked_names(self):
        text = json.dumps(self.d).lower()
        for bad in ("enterprise", "starfleet", "klingon", "vulcan", "federation", "tardis", "millennium falcon", "dilithium"):
            self.assertNotIn(bad, text)


if __name__ == "__main__":
    unittest.main()
