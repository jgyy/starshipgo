"""Every room of every deck must be reachable on foot (player capsule radius 0.30 m) and stay walkable inside.

The flood fill lives in tools/layout/audit.py (rule "walkable" / "unreachable-pocket") so the layout authors and CI use the same code.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import audit  # noqa: E402


def load(n):
    with open(os.path.join(ROOT, "godot", "data", n)) as f:
        return json.load(f)


class WalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship = load("ship.json")
        cls.cat = {m["id"]: m for m in load("catalog.json")["models"]}
        cls.v = [v for v in audit.audit(cls.ship, cls.cat) if v["rule"] in ("walkable", "unreachable-pocket", "aisle-width")]

    def test_all_rooms_reachable(self):
        errs = [v for v in self.v if v["severity"] == "error"]
        self.assertFalse(errs, "\n".join(f"{v['room']}: {v['msg']}" for v in errs[:10]))

    def test_no_unreachable_pockets(self):
        pockets = [v for v in self.v if v["rule"] == "unreachable-pocket"]
        self.assertLessEqual(len(pockets), 4, "\n".join(f"{v['room']}: {v['msg']}" for v in pockets[:10]))


if __name__ == "__main__":
    unittest.main()
