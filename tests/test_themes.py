"""Room themes only reference texture kinds that exist, and cover every room of the ship (bare python)."""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import themes  # noqa: E402

SURF = os.path.join(ROOT, "godot", "textures", "surfaces")
SLOTS = ("wall", "floor", "ceiling", "trim", "accent_tex", "clad")


class ThemeTests(unittest.TestCase):
    def test_every_referenced_kind_has_all_three_pngs(self):
        for kind in themes.kinds_used():
            for k in ("albedo", "normal", "orm"):
                self.assertTrue(os.path.exists(os.path.join(SURF, f"{kind}_{k}.png")), f"{kind}_{k}.png")

    def test_kinds_are_in_surface_index(self):
        with open(os.path.join(SURF, "index.json")) as fh:
            idx = json.load(fh)
        for kind in themes.kinds_used():
            self.assertIn(kind, idx)

    def test_all_ship_rooms_have_a_complete_theme(self):
        with open(os.path.join(ROOT, "godot", "data", "ship.json")) as fh:
            rooms = json.load(fh)["rooms"]
        self.assertGreater(len(rooms), 30)
        for r in rooms:
            t = themes.theme_for(r["id"], r.get("dept", ""))
            for s in SLOTS:
                self.assertIn(s, t, r["id"])
                self.assertTrue(t[s], r["id"])

    def test_named_rooms_use_their_own_entry(self):
        for rid in ("bridge", "ready", "lounge", "conf", "astro", "capt", "comms", "armory", "galley", "mess", "brig",
                    "secoff", "medbay", "rec", "dorm", "sci", "hydro", "life", "core", "airlock", "eng", "shop", "cargo",
                    "aux", "depot", "hangar"):
            self.assertIn(rid, themes.ROOM_THEME, rid)
        self.assertEqual(themes.theme_for("corF2", "transit")["wall"], themes.ROOM_THEME["corF"]["wall"])
        self.assertEqual(themes.theme_for("cabinB", "crew")["floor"], themes.ROOM_THEME["cabin"]["floor"])
        self.assertEqual(themes.theme_for("lobby3", "transit")["floor"], themes.ROOM_THEME["lobby"]["floor"])
        self.assertEqual(themes.theme_for("towerA2", "transit")["wall"], themes.ROOM_THEME["tower"]["wall"])

    def test_future_rooms_fall_back_to_department(self):
        for dept, want in themes.DEPT_THEME.items():
            t = themes.theme_for("zz_new_room", dept)
            self.assertEqual(t["wall"], want["wall"])
            self.assertEqual(t["clad"], themes.HULL_BY_DEPT[dept])
        self.assertEqual(themes.theme_for("zz", "unknown-dept")["wall"], themes.DEPT_THEME["transit"]["wall"])

    def test_theme_for_returns_fresh_dict(self):
        a = themes.theme_for("bridge", "command")
        a["wall"] = "x"
        self.assertNotEqual(themes.theme_for("bridge", "command")["wall"], "x")

    def test_screen_families_resolve(self):
        sys.path.insert(0, os.path.join(ROOT, "blender"))
        from starship import screen_families as sf
        self.assertEqual(sf.resolve("steel", "m"), "steel")
        self.assertEqual(sf.resolve("screen:unknown", "m"), "screen:unknown")
        seen = set()
        for i in range(200):
            r = sf.resolve("screen:radar", f"model_{i}")
            self.assertEqual(r, sf.resolve("screen:radar", f"model_{i}"))      # deterministic
            seen.add(r)
        self.assertEqual(seen, {"screen:" + v for v in sf.FAMILIES["radar"]})


if __name__ == "__main__":
    unittest.main()
