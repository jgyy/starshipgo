"""Regression tests for the second round of Python defects (docs/bugs/round2/python.json, ids P001...).

Every test fails on the code as it was before the fix and passes now.  Run:  python -m unittest discover -s tests -v
"""
import ast
import csv
import gc
import glob
import importlib.util
import io
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
import zlib
from unittest import mock

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GODOT = os.path.join(ROOT, "godot", "data")
for sub in ("layout", "draft", "docs", "audio"):
    sys.path.insert(0, os.path.join(ROOT, "tools", sub))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit as A  # noqa: E402
import bom  # noqa: E402
import draft  # noqa: E402
import dressing  # noqa: E402
import generate_ship  # noqa: E402
import hull as hulllib  # noqa: E402
import policy  # noqa: E402
import shiplib as sl  # noqa: E402
import shipmodel as model  # noqa: E402
import svgkit  # noqa: E402
import test_audit as TA  # noqa: E402

SHIP_PATH = os.path.join(GODOT, "ship.json")
CAT_PATH = os.path.join(GODOT, "catalog.json")


def new_room(rect=(0.0, 0.0, 10.0, 10.0), height=3.4):
    """An unclipped room on a one-deck ship that uses the real catalog."""
    ship = sl.Ship(sl.Catalog(CAT_PATH))
    ship.decks = [{"id": 1, "y": 0.0}]
    room = sl.Room(ship, "t", "Test", 1, rect, height=height, clip=False)
    room.line("Test line", "x" * 50)
    return room


def run_ship(ship, **kw):
    return A.audit(ship, TA.CATALOG, **kw)


def mutated(fn):
    ship = TA.clean_ship()
    fn(TA.eng_of(ship), ship)
    return ship


def recorded_warnings(fn):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fn()
        gc.collect()
    return [str(w.message) for w in caught if issubclass(w.category, ResourceWarning)]


# ====================================================================== layout engine (shiplib / policy / dressing)
class EngineTests(unittest.TestCase):

    def test_P001_wall_item_bookkeeping_uses_the_real_vertical_extent(self):
        """64 of 274 wall models are not centred on their origin: the fold-down table spans 0.86..1.30 m at mount_y 0.9, the
        feed-horn panel 1.15..1.85 m at 1.5 m.  The engine recorded +-size/2 around the origin and let them overlap."""
        r = new_room()
        self.assertIsNotNone(r.wall_item("N", "table_fold_down_table", 5.0, y=0.9))
        self.assertIsNone(r.wall_item("N", "antenna_feed_horn_panel", 5.0, y=1.5))
        self.assertIsNotNone(r.wall_item("N", "antenna_feed_horn_panel", 5.0, y=1.9))      # 1.55..2.25 clears the table

    def test_P001_wall_item_top_is_checked_against_the_ceiling_with_real_bounds(self):
        r = new_room()        # ceiling at 3.4 m; pipe_elbow_up reaches +0.97 m above its origin (size/2 is only 0.52)
        self.assertIsNone(r.wall_item("S", "pipe_elbow_up", 5.0, y=2.5))
        self.assertIsNotNone(r.wall_item("S", "pipe_elbow_up", 5.0, y=2.3))

    def test_P002_engine_keeps_tall_floor_props_clear_of_windows(self):
        r = new_room()
        r.add_window("N", 5.0, 1.0)
        tall = next(m for m in r.cat.models.values() if m["mount"] == "floor" and 1.0 < m["size"][1] < 2.0
                    and m["size"][0] < 0.8 and m["size"][2] < 0.8)
        self.assertIsNone(r.place(tall, 5.0, 0.65, 0.0))             # 0.2 m from the window: audit rule window-blocked
        self.assertIsNotNone(r.place(tall, 5.0, 3.0, 0.0))           # 2.8 m away: fine
        short = next(m for m in r.cat.models.values() if m["mount"] == "floor" and m["size"][1] < 0.5 and m["size"][0] < 0.8
                     and m["size"][2] < 0.8)
        self.assertIsNotNone(r.place(short, 2.0, 0.65, 0.0))         # low props may stand under windows

    def test_P002_engine_and_audit_agree_on_random_wall_placements(self):
        """Fuzz: whatever Room.against_wall / wall_item / run accept must pass the audit rules about walls and windows."""
        import random
        generate_ship.ONLY_DECKS = set()
        try:
            cat = sl.Catalog(CAT_PATH)
            B = generate_ship.build(cat)
        finally:
            generate_ship.ONLY_DECKS = None
        rng = random.Random(7)
        floor = [m for m in cat.models.values() if m["mount"] == "floor"]
        wall = [m for m in cat.models.values() if m["mount"] == "wall"]
        for room in B.ship.rooms.values():
            room.line("fuzz", "x" * 50)
            for _ in range(40):
                side = rng.choice([e["side"] for e in room.edges])
                lo, hi = room.wall_span(side)
                if rng.random() < 0.5:
                    room.against_wall(side, rng.choice(floor), rng.uniform(lo, hi), gap=rng.choice([0.0, 0.04, 0.1]))
                else:
                    room.wall_item(side, rng.choice(wall), rng.uniform(lo, hi), y=rng.choice([None, 0.5, 1.5, 2.5]))
        ship = {"version": 2, "decks": B.ship.decks, "hull": {str(k): v for k, v in B.ship.hull.items()},
                "rooms": [r.to_json() for r in B.ship.rooms.values()], "doors": B.ship.doors, "stairs": B.ship.stairs}
        viol = A.audit(ship, cat.models, rules=["window-blocked", "wall-item-overlap", "wall-item-span", "wall-floor-clash",
                                                "outside-shell", "footprint-overlap"])
        self.assertEqual(viol, [], [v["msg"] for v in viol[:5]])

    def test_P004_room_key_of_an_empty_id(self):
        self.assertEqual(policy.room_key(""), "")
        self.assertEqual(policy.room_key("corF2"), "corF")
        self.assertEqual(policy.room_key("123"), "")
        self.assertEqual(policy.allowed(""), policy.UNIVERSAL)

    def test_P006_room_outside_the_hull_says_so(self):
        ship = sl.Ship(sl.Catalog(CAT_PATH))
        ship.decks = [{"id": 1, "y": 0.0}]
        ship.hull = {1: hulllib.outline(1)}
        with self.assertRaisesRegex(ValueError, "outside the deck 1 hull"):
            sl.Room(ship, "far", "Far", 1, (100, 100, 110, 110))

    def test_P007_light_grid_accepts_every_light_casting_a_shadow(self):
        r = new_room()
        r.light_grid(shadow_every=0)
        self.assertTrue(r.lights)
        self.assertTrue(all(light["shadow"] for light in r.lights))
        with self.assertRaises(ValueError):
            r.light_grid(spacing=0)

    def test_P008_pattern_helpers_take_tuples_and_reject_missing_families(self):
        r = new_room()
        self.assertGreater(len(r.grid(("crate", "barrel"), 1, 1, 9, 9, 3, 3)), 0)       # a tuple used to place nothing, silently
        self.assertGreater(len(dressing.row(r, ("crate", "barrel"), 2, 9, 8, 9, 3)), 0)
        with self.assertRaises(ValueError):
            dressing.arc(r, 5, 5, 2, 0, 90, 3)                                          # default cats=None used to be a TypeError
        self.assertEqual(sl.as_cats("crate"), ["crate"])

    def test_P009_link_rejects_unknown_kinds(self):
        ship = sl.Ship(sl.Catalog(CAT_PATH))
        ship.decks = [{"id": 1, "y": 0.0}]
        ship.add_room(sl.Room(ship, "a", "A", 1, (0, 0, 5, 5), clip=False))
        ship.add_room(sl.Room(ship, "b", "B", 1, (5, 0, 10, 5), clip=False))
        with self.assertRaisesRegex(ValueError, "unknown kind"):
            ship.link("a", "b", kind="doors")            # a typo used to silently become a 4 m wide open arch with no door
        self.assertEqual(ship.link("a", "b", kind="open"), 2.5)

    def test_P047_link_explains_a_catalog_without_doors(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "empty.json")
            with open(path, "w") as f:
                json.dump({"models": []}, f)
            ship = sl.Ship(sl.Catalog(path))
        ship.decks = [{"id": 1, "y": 0.0}]
        ship.add_room(sl.Room(ship, "a", "A", 1, (0, 0, 5, 5), clip=False))
        ship.add_room(sl.Room(ship, "b", "B", 1, (5, 0, 10, 5), clip=False))
        with self.assertRaisesRegex(ValueError, "no 'door' model"):          # was: TypeError 'NoneType' object is not subscriptable
            ship.link("a", "b", kind="door")
        with self.assertRaisesRegex(ValueError, "no 'doorframe' model"):
            ship.link("a", "b", kind="portal")
        with self.assertRaisesRegex(ValueError, "not in the catalog"):
            ship.link("a", "b", kind="door", model="door_nope")

    def test_P010_flat_floor_decals_do_not_count_as_occupancy(self):
        r = new_room()
        rug = next(m for m in r.cat.models.values() if m["mount"] == "floor" and m["size"][1] <= 0.15 and m["size"][0] * m["size"][2] > 3)
        self.assertIsNotNone(r.place(rug, 5, 5, 0.0))
        self.assertEqual(r.occupancy(), 0.0)

    def test_P010_all_three_occupancy_figures_agree_on_the_committed_ship(self):
        """BOM.md printed 61 % for the hangar (rugs and floor markings included) while rule `density` measured 25 %."""
        with open(SHIP_PATH, encoding="utf-8") as f:
            ship_json = json.load(f)
        cat = A.load_catalog(CAT_PATH)
        stats = {s["room"]: s["occupancy"] for s in A.audit_stats(ship_json, cat)}
        drawn = model.Ship(SHIP_PATH, CAT_PATH)
        ctx = A.Ctx(ship_json, cat)
        for room in ctx.rooms:
            density = sum(p.area for p in room.props if p.mount == "floor" and not p.arch and not p.flat) / max(room.area, 1.0)
            self.assertAlmostEqual(stats[room.id], density, delta=0.0006, msg=room.id)
            self.assertAlmostEqual(drawn.by_id[room.id].occupancy(), density, delta=0.002, msg=room.id)
        self.assertLess(stats["hangar"], 0.4)

    def test_P045_end_chairs_face_the_table(self):
        r = new_room()
        self.assertEqual(dressing.chairs_around(r, 5.0, 5.0, 1.0, 0.5, ends=True), 6)
        for p in r.props:
            fp = p["_fp"]
            fx, fz = sl.rot(0, 1, p["yaw"])                                  # front vector of the chair
            to_table = (5.0 - (fp[0] + fp[2]) / 2, 5.0 - (fp[1] + fp[3]) / 2)
            self.assertGreater(fx * to_table[0] + fz * to_table[1], 0.1, p)  # the two end chairs used to look away from the table

    def test_P042_deck1_tops_measures_the_host_width_for_tiny_negative_yaw(self):
        import recipes_deck1_helpers as H
        seen = []

        class FakeCat:
            def pick(self, c, label=None, pred=None):
                return {"mount": "table", "id": label}

        class FakeRoom:
            cat = FakeCat()

            def on_top(self, host, m, dx=0.0, dz=0.0):
                seen.append((dx, dz))

        host = {"_fp": (0.0, 0.0, 2.0, 0.5), "yaw": -0.4}           # unrotated 2.0 x 0.5 host
        H.tops(FakeRoom(), host, "c", ["a", "b"])
        self.assertAlmostEqual(abs(seen[0][0]), 0.25 * 2.0 * 0.7, places=2)       # width 2.0, not the depth 0.5


# ====================================================================== audit
class AuditGapTests(unittest.TestCase):

    def test_P003_touching_and_millimetre_contacts_are_not_clashes(self):
        """ship.json positions are rounded to 1 mm, so flush items measure sub-millimetre penetrations; the engine accepts
        them, the audit used to call them clashes (fuzz: wall-floor-clash with a 1 mm 'overlap')."""
        def ceiling(e, s):          # pod hangs 0.5 m down from 3.0 m (lowest 2.5 m); crate top 2.5005 m
            e["props"].append(TA.prop("pod", 15, 2, y=3.0))
            e["props"] = [p for p in e["props"] if not (p["m"] == "crate" or p["m"] == "box")]
            e["props"].append(TA.prop("crate", 15, 2, scale=[1.0, 2.5005, 1.0]))
        self.assertEqual(TA.rules(run_ship(mutated(ceiling))), [])

        def real_clash(e, s):
            ceiling(e, s)
            e["props"][-1]["scale"] = [1.0, 2.6, 1.0]
        self.assertEqual(TA.rules(run_ship(mutated(real_clash))), ["ceiling-floor-clash"])

        def wall(e, s):             # sign (S wall, lowest 1.35 m) over a crate whose top is 1.3505 m
            e["props"] = [p for p in e["props"] if p["m"] in ("lamp", "sign")]
            e["props"].append(TA.prop("crate", 16, 9.34, scale=[1.0, 1.3505, 1.0]))
        self.assertEqual(TA.rules(run_ship(mutated(wall))), [])

    def test_P005_core_is_not_a_circulation_space(self):
        ctx = A.Ctx({"rooms": [], "decks": []}, {})
        for rid, want in (("core", False), ("corF1", True), ("corA3", True), ("lobby2", True), ("towerB1", True), ("cargo", False),
                          ("corridor_x", False)):
            room = A.Room({"id": rid, "deck": 1, "rect": [0, 0, 5, 5]}, ctx)
            self.assertEqual(room.is_circulation(), want, rid)

        def f(e, s):        # an empty Computer Core must get the "very low density" warning, like any room
            s["rooms"][0]["id"] = "core"
        viol = run_ship(mutated(f))
        self.assertTrue(any(v["rule"] == "density" and v["room"] == "core" for v in viol))

    def test_P011_opening_heights_are_validated(self):
        def tall(e, s):
            e["openings"].append({"side": "N", "c": 15, "w": 1.0, "y0": 0.5, "y1": 9.0, "kind": "window"})
        self.assertEqual(TA.rules(run_ship(mutated(tall))), ["opening-validity"])

        def inverted(e, s):
            e["openings"].append({"side": "N", "c": 15, "w": 1.0, "y0": 2.0, "y1": 1.0, "kind": "window"})
        self.assertEqual(TA.rules(run_ship(mutated(inverted))), ["opening-validity"])

    def test_P012_doors_are_audited(self):
        def unknown(e, s):
            s["doors"].append({"m": "nodoor", "pos": [10, 0, 5], "yaw": 90, "a": "lobby1", "b": "eng"})
        viol = run_ship(mutated(unknown))
        self.assertIn("unknown-model", TA.rules(viol))

        def nowhere(e, s):
            s["doors"].append({"m": "crate", "pos": [3, 0, 3], "yaw": 90, "a": "lobby1", "b": "eng"})
        self.assertEqual(TA.rules(run_ship(mutated(nowhere))), ["ship-structure"])

        def ghost(e, s):
            s["doors"].append({"m": "crate", "pos": [10, 0, 5], "yaw": 90, "a": "lobby1", "b": "nowhere"})
        self.assertEqual(TA.rules(run_ship(mutated(ghost))), ["ship-structure"])

        def good(e, s):
            s["doors"].append({"m": "crate", "pos": [10, 0, 5], "yaw": 90, "a": "lobby1", "b": "eng"})
        self.assertEqual(TA.rules(run_ship(mutated(good))), [])

    def test_P013_door_zones_are_derived_even_when_the_generator_wrote_none(self):
        def f(e, s):
            for r in s["rooms"]:
                r["zones"] = []
            e["props"].append(TA.prop("crate", 11.2, 2.0))      # not in the walkway; only the derived zone covers x 10..12, z 3.6..6.4
            e["props"].append(TA.prop("crate", 11.2, 5.0))
        viol = run_ship(mutated(f))
        self.assertIn("door-clearance", TA.rules(viol))

    def test_P014_duplicate_bom_codes(self):
        self.assertEqual(TA.rules(run_ship(mutated(lambda e, s: e["bom"].append(dict(e["bom"][0]))))), ["bom-line"])

    def test_P015_lights_must_be_inside_their_room(self):
        def f(e, s):
            e["lights"].append({"type": "spot", "pos": [500, 2, 500]})
        self.assertEqual(TA.rules(run_ship(mutated(f))), ["lights"])
        self.assertEqual(TA.rules(run_ship(mutated(lambda e, s: e["lights"].append({"type": "spot", "pos": [15, 99, 5]})))), ["lights"])

    def test_P016_duplicate_room_ids_and_unknown_decks(self):
        import copy
        ship = mutated(lambda e, s: s["rooms"].append(copy.deepcopy(e)))
        self.assertIn("ship-structure", TA.rules(run_ship(ship)))
        ship = mutated(lambda e, s: s.update(decks=[{"id": 2, "y": 4.0}]))
        self.assertIn("ship-structure", TA.rules(run_ship(ship)))

    def test_P017_malformed_props_are_violations_not_crashes(self):
        for bad in ({"m": "crate"}, {"m": "crate", "pos": [float("nan"), 0, 1]}, {"pos": [1, 0, 1]}, {"m": "crate", "pos": [1, 2]}):
            viol = run_ship(mutated(lambda e, s, bad=bad: e["props"].append(dict(bad))))
            self.assertIn("ship-structure", TA.rules(viol), bad)

    def test_P018_unknown_room_filter_is_an_error_not_a_pass(self):
        with self.assertRaisesRegex(ValueError, "unknown room 'bridg'"):
            A.audit(TA.clean_ship(), TA.CATALOG, only_room="bridg")
        with tempfile.TemporaryDirectory() as d:
            ship_path, cat_path = os.path.join(d, "s.json"), os.path.join(d, "c.json")
            with open(ship_path, "w") as f:
                json.dump(TA.clean_ship(), f)
            with open(cat_path, "w") as f:
                json.dump({"models": list(TA.CATALOG.values())}, f)
            with mock.patch("sys.stderr", new=io.StringIO()):
                self.assertEqual(A.main(["--ship", ship_path, "--catalog", cat_path, "--room", "bridg"]), 2)
            with mock.patch("sys.stdout", new=io.StringIO()):
                self.assertEqual(A.main(["--ship", ship_path, "--catalog", cat_path, "--room", "eng"]), 0)

    def test_P049_every_audit_rule_fires_on_a_minimal_violation(self):
        """Mutation matrix: one deliberate violation per rule of audit.RULES; a rule that stops firing (or a new rule without
        a mutation here) fails this test."""
        def crate_wall(gap):
            def f(e, s):
                la, lb = 5.0 - gap / 2 - 0.15, 9.85 - 5.0 - gap / 2
                e["props"] = [p for p in e["props"] if p["m"] == "lamp"]
                e["props"] += [TA.prop("crate", 15, 0.15 + la / 2, scale=[1, 1, la]), TA.prop("crate", 15, 5.0 + gap / 2 + lb / 2, scale=[1, 1, lb])]
            return f

        def zones_off(e, s):
            for r in s["rooms"]:
                r["zones"] = []

        def window_blocked(e, s):
            e["openings"].append({"side": "N", "c": 15.0, "w": 3.0, "y0": 0.9, "y1": 2.4, "kind": "window"})
            e["props"].append(TA.prop("crate", 15, 0.8))

        def hole(e, s):
            e["floor_holes"].append([16, 7, 18, 9])
            e["props"].append(TA.prop("crate", 17, 8))

        def tabletop(e, s):
            e["props"] += [TA.prop("lockerbox", 17, 8), TA.prop("box", 17, 8, y=1.0)]

        def duplicates(e, s):
            e["props"] += [TA.prop("crate", 11.5 + i * 1.05, 8.5) for i in range(7)]

        def unreachable(e, s):
            e["props"].append(TA.prop("crate", 12.5, 5.0, scale=[1.0, 1.0, 9.7]))

        def hull_small(e, s):
            s["hull"]["1"] = [[0, 0], [19, 0], [19, 10], [0, 10]]

        def stair(e, s):
            e["ceiling_holes"].append([1, 1, 2, 2])

        def rename(e, s):
            s["rooms"][0]["id"] = "zzz1"
            e["id"] = "zzz2"

        def wall_floor(e, s):
            e["props"] += [TA.prop("crate", 13, 0.65), TA.prop("sign", 13, 0.15, y=0.8, yaw=0.0)]

        def ceil_floor(e, s):
            e["props"] += [TA.prop("tallcab", 17, 8), TA.prop("pod", 17, 8, y=3.0)]

        def opening_outside(e, s):
            for r in s["rooms"]:
                for o in r["openings"]:
                    o["c"] = 9.8

        def dup_id(e, s):
            import copy
            s["rooms"].append(copy.deepcopy(e))

        def density(e, s):
            e["props"] = [p for p in e["props"] if p["m"] == "lamp"] + [TA.prop("crate", 16, 5, scale=[7.5, 1.0, 8.2])]

        def no_bom(e, s):
            e["props"].append(TA.prop("crate", 17, 8, b=None))

        matrix = {
            "footprint-overlap": lambda e, s: e["props"].append(TA.prop("crate", 15.5, 2)),
            "outside-shell": lambda e, s: e["props"].append(TA.prop("crate", 19.8, 7)),
            "door-clearance": lambda e, s: e["props"].append(TA.prop("crate", 11, 5)),
            "window-blocked": window_blocked,
            "wall-item-overlap": lambda e, s: e["props"].append(TA.prop("sign", 16.2, 9.85, y=1.5, yaw=180.0)),
            "wall-item-span": lambda e, s: e["props"].append(TA.prop("sign", 19.9, 0.15, y=1.5, yaw=0.0)),
            "wall-facing": lambda e, s: e["props"].append(TA.prop("sign", 13, 0.15, y=1.5, yaw=90.0)),
            "ceiling-overlap": lambda e, s: e["props"].append(TA.prop("lamp", 15.2, 5.0, y=3.0)),
            "floating-floor": lambda e, s: e["props"].append(TA.prop("crate", 17, 8, y=0.5)),
            "table-support": lambda e, s: e["props"].append(TA.prop("box", 15, 2, y=1.4)),
            "hole-clash": hole,
            "policy-category": lambda e, s: e["props"].append(TA.prop("bed", 17, 8)),
            "unknown-room-policy": rename,
            "unknown-model": lambda e, s: e["props"].append(TA.prop("nomodel", 12, 2)),
            "walkable": lambda e, s: (zones_off(e, s), e["props"].append(TA.prop("crate", 11, 5, scale=[1.0, 1.0, 6.0]))),
            "unreachable-pocket": unreachable,
            "aisle-width": crate_wall(0.5),
            "density": density,
            "duplicates": duplicates,
            "bom-line": no_bom,
            "lights": lambda e, s: e.update(lights=[]),
            "stair-consistency": stair,
            "hull-containment": hull_small,
            "opening-validity": opening_outside,
            "wall-floor-clash": wall_floor,
            "ceiling-floor-clash": ceil_floor,
            "too-tall": lambda e, s: e["props"].append(TA.prop("giant", 17, 8)),
            "tabletop-host": tabletop,
            "mount-mismatch": lambda e, s: e["props"].append(TA.prop("lamp", 12, 8.0, y=2.5)),
            "ship-structure": dup_id,
        }
        self.assertEqual(sorted(matrix), sorted(A.RULES))
        for rule, fn in matrix.items():
            viol = run_ship(mutated(fn))
            self.assertIn(rule, {v["rule"] for v in viol}, rule)
        clean = {v["rule"] for v in run_ship(TA.clean_ship()) if v["severity"] == "error"}
        self.assertEqual(clean, set())

    def test_P003_every_rule_is_listed(self):
        self.assertIn("ship-structure", A.RULES)
        self.assertEqual(len(A.RULES), len(set(A.RULES)))


# ====================================================================== drawing tools
class DraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship = model.Ship(SHIP_PATH, CAT_PATH)

    def test_P019_text_fill_is_a_style_so_the_css_rule_does_not_override_it(self):
        sh = svgkit.Sheet("T", "t")
        sh.text(1, 1, "grey", fill="#444")
        self.assertIn('style="fill:#444"', sh.out[-1])
        self.assertNotIn(' fill="', sh.out[-1])          # `.t{fill:#111}` beats a presentation attribute: the colour never showed

    def test_P020_render_can_be_called_twice(self):
        sh = svgkit.Sheet("T", "t")
        sh.line(1, 1, 2, 2)
        first = sh.render()
        self.assertEqual(sh.render(), first)
        self.assertEqual(first.count("DRAWING TITLE"), 1)

    def test_P021_vertical_dimension_text_that_does_not_fit_is_nudged(self):
        sh = svgkit.Sheet("T", "t")
        w = svgkit.text_w("LONGLABEL", 2.0)
        tx = 50 - 0.7
        sh.reserve((tx - 1.8, 11 - w / 2, tx + 0.6, 11 + w / 2))
        sh.dim_v(10, 12, 50, "LONGLABEL")
        texts = [o for o in sh.out if o.startswith("<text")]
        self.assertEqual(len(texts), 1)
        self.assertNotIn('x="%s"' % svgkit.fmt(tx), texts[0])

    def test_P022_wrap_never_emits_an_empty_line(self):
        import sheets_room
        lines = sheets_room.wrap_lines("INTERCONTINENTALLYLONGWORD and more words", 10.0, 1.7)
        self.assertTrue(all(lines), lines)
        self.assertEqual(svgkit.wrap_words("abcdefghijklmnop qr", 5), ["abcdefghijklmnop", "qr"])
        self.assertEqual(svgkit.wrap_words("", 5), [])

    @staticmethod
    def png(path, W, H, ctype, rows, filters):
        bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
        raw, prev = b"", bytes(W * bpp)
        for row, ft in zip(rows, filters):
            out = bytearray()
            for i, v in enumerate(row):
                a = row[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                if ft == 0:
                    pr = 0
                elif ft == 1:
                    pr = a
                elif ft == 2:
                    pr = b
                elif ft == 3:
                    pr = (a + b) // 2
                else:
                    p = a + b - c
                    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                    pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                out.append((v - pr) & 255)
            raw += bytes([ft]) + bytes(out)
            prev = bytes(row)

        def chunk(t, b):
            return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b) & 0xffffffff)
        with open(path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, ctype, 0, 0, 0)) +
                    chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))

    @staticmethod
    def decode(path):
        with open(path, "rb") as f:
            data = f.read()
        pos, idat, ihdr = 8, b"", None
        while pos < len(data):
            ln, = struct.unpack(">I", data[pos:pos + 4])
            typ, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + ln]
            if typ == b"IHDR":
                ihdr = struct.unpack(">IIBBBBB", body)
            elif typ == b"IDAT":
                idat += body
            pos += 12 + ln
        W, H, _, ctype = ihdr[:4]
        bpp = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
        return W, H, draft._unfilter(zlib.decompress(idat), W, H, bpp)

    def test_P023_crop_png_crops_width_and_height_for_every_filter(self):
        import random
        rng = random.Random(3)
        W, H = 7, 6
        rows = [bytes(rng.randrange(256) for _ in range(W * 3)) for _ in range(H)]
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "a.png")
            self.png(p, W, H, 2, rows, [0, 1, 2, 3, 4, 1])
            caught = recorded_warnings(lambda: self.assertTrue(draft.crop_png(p, 4, 3)))
            self.assertEqual(caught, [])
            w, h, got = self.decode(p)
            self.assertEqual((w, h), (4, 3))
            self.assertEqual(got, [r[:12] for r in rows[:3]])
            q = os.path.join(d, "pal.png")
            self.png(q, 4, 4, 0, [bytes(range(4))] * 4, [0] * 4)
            with open(q, "rb") as f:
                before = f.read()
            ihdr_ctype = 3
            patched = before[:25] + bytes([ihdr_ctype]) + before[26:]           # palette image: unsupported, must not raise KeyError
            with open(q, "wb") as f:
                f.write(patched)
            self.assertFalse(draft.crop_png(q, 2, 2))

    def test_P024_chromium_timeout_does_not_abort_the_export(self):
        sh = svgkit.Sheet("G-01", "Test")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(draft, "find_chrome", return_value="/bin/true"), \
                mock.patch.object(draft.subprocess, "run", side_effect=subprocess.TimeoutExpired("chrome", 1)), \
                mock.patch("sys.stdout", new=io.StringIO()):
            self.assertEqual(draft.export_png(d, [sh]), 0)

    def test_P025_unknown_room_in_only_is_an_error(self):
        with tempfile.TemporaryDirectory() as d, mock.patch("sys.stderr", new=io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                draft.main(["--ship", SHIP_PATH, "--catalog", CAT_PATH, "--out", d, "--only", "bridg"])
            self.assertEqual(cm.exception.code, 2)
            self.assertEqual(os.listdir(d), [])

    def test_P026_a_tower_plan_shows_only_its_own_stair(self):
        import re
        import sheets_room
        for rid in ("towerA2", "towerB2"):
            svg = sheets_room.room_plan(self.ship, self.ship.by_id[rid]).render()
            xs = [float(x) for pts in re.findall(r'points="([^"]+)"', svg) for x, _ in (p.split(",") for p in pts.split())]
            self.assertTrue(xs and min(xs) > -5 and max(xs) < 425, (rid, min(xs), max(xs)))     # the other stair was drawn at x = 1057 mm

    def test_P027_window_schedule_lists_every_window(self):
        import sheets_misc
        svg = sheets_misc.schedule_sheet(self.ship).render()
        self.assertGreater(len(self.ship.win_list), 46)
        for w in self.ship.win_list:
            self.assertIn(">%s<" % w["mark"], svg)

    def test_P050_floor_to_floor_dimension_only_where_a_deck_lies_above(self):
        import sheets_room
        top = sheets_room.room_section(self.ship, self.ship.by_id["bridge"], "SL").render()          # deck 1: nothing above
        mid = sheets_room.room_section(self.ship, self.ship.by_id["mess"], "SL").render()
        self.assertNotIn("F-F", top)                           # a "4000 F-F" dimension to a floor that does not exist
        self.assertIn("4000 F-F", mid)

    def test_P051_general_arrangement_dimensions_come_from_the_ship_data(self):
        import sheets_ga
        with open(SHIP_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for pts in data["hull"].values():
            for p in pts:
                p[0] *= 2.0
        for d in data["decks"]:
            d["y"] = {1: 10.0, 2: 5.0, 3: 0.0}[d["id"]]
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "big.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            ship = model.Ship(path, CAT_PATH)
        lines = sheets_ga.hull_lines(ship).render()
        self.assertIn("BEAM 52000", lines)                                        # "BEAM 26000" was a literal
        self.assertNotIn("BEAM 26000", lines)
        profile = sheets_ga.profile_sheet(ship).render()
        self.assertIn(">5000<", profile)                                          # deck pitch from the decks, not "4000"
        self.assertNotIn(">4000<", profile)
        self.assertEqual(sheets_ga.floor_to_floor(ship, 5.0), "5000 mm")
        self.assertEqual(sheets_ga.floor_to_floor(ship, 10.0), "- (top deck)")

    def test_P048_a_ship_without_stairs_still_gets_its_drawings(self):
        with open(SHIP_PATH, encoding="utf-8") as f:
            data = json.load(f)
        data["stairs"] = []
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "nostairs.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            ship = model.Ship(path, CAT_PATH)
        sheets = draft.build_sheets(ship)                                   # was: IndexError in the stair-tower sheet
        nums = [s.num for s in sheets]
        self.assertNotIn("G-13", nums)
        self.assertIn("G-14", nums)
        self.assertEqual(len(nums), len(set(nums)))

    def test_P028_files_are_closed_and_the_index_is_utf8_lf(self):
        self.assertEqual(recorded_warnings(lambda: model.Ship(SHIP_PATH, CAT_PATH)), [])
        sheet = svgkit.Sheet("G-01", "T", scale="1:100", deck="DECK 1")
        with tempfile.TemporaryDirectory() as d:
            draft.write_index(d, [sheet], self.ship)
            with open(os.path.join(d, "INDEX.md"), "rb") as f:
                data = f.read()
        self.assertTrue(data.endswith(b"\n"))
        self.assertNotIn(b"\r", data)


# ====================================================================== bill of materials
class BomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ship, cls.cat = bom.load(ROOT)

    def test_P033_load_closes_its_files(self):
        self.assertEqual(recorded_warnings(lambda: bom.load(ROOT)), [])

    def test_P029_csv_lists_every_placement_including_doors_and_arches(self):
        with tempfile.TemporaryDirectory() as d:
            path = bom.write_csv(self.ship, self.cat, d)
            with open(path, newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        total = sum(len(r["props"]) for r in self.ship["rooms"]) + len(self.ship["doors"])
        self.assertEqual(sum(int(r["qty"]) for r in rows), total)       # 1368 of 1401 before: 26 doors and 7 frames were missing
        self.assertTrue(any(r["bom_line"] == "DOOR" for r in rows))

    def test_P030_items_without_a_bom_line_are_not_doorway_frames(self):
        room = json.loads(json.dumps(next(r for r in self.ship["rooms"] if r["id"] == "mess")))
        victim = next(p for p in room["props"] if p.get("b") not in (None, "ARCH"))
        victim["b"] = None
        lines, arch, loose = bom.room_items(room, self.cat)
        self.assertEqual(loose[victim["m"]], 1)
        self.assertNotIn(victim["m"], arch)

    def test_P031_escape_statement_matches_the_table(self):
        rows = bom.egress_table(self.ship)
        md = bom.generate(self.ship, self.cat)
        over = [r for r in rows if r[3] > bom.ESCAPE_LIMIT]
        self.assertEqual(md.count("**over the limit**"), len(over))
        if over:
            self.assertNotIn("Every room centre is within", md)
        else:
            self.assertIn("Every room centre is within", md)
        self.assertNotIn("Every point of every deck is within 35 m", md)

    def test_P046_bom_documents_the_ship_json_it_is_given(self):
        ship = json.loads(json.dumps(self.ship))
        for pts in ship["hull"].values():
            for p in pts:
                p[0] *= 2.0
        md = bom.generate(ship, self.cat)
        self.assertIn("| Beam | 52 m |", md)                      # hull.py's 26 m beam used to be printed whatever the ship.json said
        two = json.loads(json.dumps(self.ship))                   # a two-deck ship: no KeyError for the missing deck 3
        two["decks"] = [d for d in two["decks"] if d["id"] != 3]
        two["rooms"] = [r for r in two["rooms"] if r["deck"] != 3]
        ids = {r["id"] for r in two["rooms"]}
        two["doors"] = [d for d in two["doors"] if d["a"] in ids and d["b"] in ids]
        md2 = bom.generate(two, self.cat)
        self.assertIn("| Decks | 2 (floors at +4.0, +8.0 m) |", md2)
        self.assertNotIn("Engineering Deck", md2)

    def test_P032_counts_in_the_text_come_from_the_data(self):
        cat = dict(self.cat)
        for i in range(3):
            clone = dict(self.cat[next(iter(self.cat))])
            clone["id"] = "zz_extra_%d" % i
            cat[clone["id"]] = clone
        md = bom.generate(self.ship, cat)
        self.assertIn("catalog.json<br/>%d Blender models" % len(cat), md)
        self.assertNotIn("140+", md)


# ====================================================================== generators and misc tools
class GeneratorToolTests(unittest.TestCase):

    def test_P034_partial_furnishing_never_overwrites_the_game_data(self):
        with mock.patch("sys.stderr", new=io.StringIO()):
            with self.assertRaises(SystemExit) as cm:
                generate_ship.main(["--decks", "1"])
            self.assertEqual(cm.exception.code, 2)
            with self.assertRaises(SystemExit):
                generate_ship.main(["--decks", "one", "--out", os.path.join(tempfile.gettempdir(), "x.json")])
        self.assertIsNone(generate_ship.ONLY_DECKS)

    def test_P035_ledger_never_calls_errors_warnings(self):
        import bugs_ledger
        self.assertIn("ERRORS: density x2", bugs_ledger.remaining_text({("density", "error"): 2, ("duplicates", "warn"): 1}))
        self.assertIn("warnings only: duplicates x1", bugs_ledger.remaining_text({("duplicates", "warn"): 1}))
        self.assertIn("no remaining", bugs_ledger.remaining_text({}))

    def test_P036_preview_colours_are_stable_and_unique_per_family(self):
        try:
            import preview_room
        except ImportError:
            self.skipTest("matplotlib not available")
        cats = [m["category"] for m in bom.load(ROOT)[1].values()]
        a = preview_room.family_colors(cats)
        b = preview_room.family_colors(reversed(cats))
        self.assertEqual(a, b)
        self.assertEqual(len(set(a.values())), len(a))          # the old 20-colour cycle gave five families the same colour

    def test_P037_inspect_room_has_no_import_side_effects_and_reports_unknown_rooms(self):
        import inspect_room
        with mock.patch("sys.stderr", new=io.StringIO()) as err:
            self.assertEqual(inspect_room.main(["nosuchroom"]), 2)
        self.assertIn("unknown room", err.getvalue())
        with mock.patch("sys.stdout", new=io.StringIO()) as out:
            self.assertEqual(inspect_room.main(["bridge"]), 0)
        self.assertIn("== bridge", out.getvalue())


class AudioToolTests(unittest.TestCase):
    def setUp(self):
        if importlib.util.find_spec("numpy") is None:
            self.skipTest("numpy not available")

    def test_P038_silent_clip_stays_silent(self):
        import wave

        import generate_audio
        import numpy as np
        with tempfile.TemporaryDirectory() as d, warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            generate_audio.save(d, "s", np.zeros(100), peak=1000)
            with wave.open(os.path.join(d, "s.wav"), "rb") as w:
                pcm = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        self.assertEqual(int(np.abs(pcm).max()), 0)
        self.assertEqual([str(w.message) for w in caught], [])    # 0/0 -> NaN -> int16 cast: RuntimeWarnings (and -32768 on x86)

    def test_P039_generate_returns_only_what_it_wrote(self):
        import generate_audio
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "readme.txt"), "w") as f:
                f.write("not a sound")
            self.assertEqual(generate_audio.generate(d), sorted(generate_audio.WRITTEN))


# ====================================================================== code hygiene
class HygieneTests(unittest.TestCase):

    def test_P040_no_noop_statements_or_constant_conditions_in_the_tools(self):
        """Bare expression statements (`g["sgn"]`, `6.4 - 1.5 if True else 0`, `r.w * s`) and `if False` branches were left
        behind in generate_ship, bom, draft and dressing; recipes_deck*.py hold the room content and are not scanned."""
        found = []
        for f in sorted(glob.glob(os.path.join(ROOT, "tools", "**", "*.py"), recursive=True)):
            if os.path.basename(f) in ("recipes_deck1.py", "recipes_deck2.py", "recipes_deck3.py"):
                continue
            with open(f, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            for n in ast.walk(tree):
                if isinstance(n, ast.Expr) and not isinstance(n.value, (ast.Call, ast.Await, ast.Yield, ast.YieldFrom)) and \
                        not (isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)):
                    found.append("%s:%d no-op %s" % (os.path.relpath(f, ROOT), n.lineno, ast.unparse(n)[:50]))
                if isinstance(n, (ast.If, ast.IfExp, ast.While)) and isinstance(n.test, ast.Constant):
                    found.append("%s:%d constant condition %s" % (os.path.relpath(f, ROOT), n.lineno, ast.unparse(n.test)))
                if isinstance(n, ast.BoolOp) and any(isinstance(v, ast.Constant) and isinstance(v.value, bool) for v in n.values):
                    found.append("%s:%d constant operand %s" % (os.path.relpath(f, ROOT), n.lineno, ast.unparse(n)[:50]))
        self.assertEqual(found, [])

    def test_P041_tools_open_files_with_context_managers(self):
        """`json.load(open(path))` leaves the handle to the garbage collector (ResourceWarning under python -X dev)."""
        found = []
        for f in sorted(glob.glob(os.path.join(ROOT, "tools", "**", "*.py"), recursive=True)):
            with open(f, encoding="utf-8") as fh:
                tree = ast.parse(fh.read())
            with_calls = {id(i.context_expr) for n in ast.walk(tree) if isinstance(n, (ast.With, ast.AsyncWith)) for i in n.items}
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "open" and id(n) not in with_calls:
                    found.append("%s:%d" % (os.path.relpath(f, ROOT), n.lineno))
        self.assertEqual(found, [])


class WeakTestRepairs(unittest.TestCase):
    """The old tests were too lax to notice these regressions."""

    def test_P043_prop_origins_must_be_inside_the_room_polygon(self):
        import test_project
        with open(SHIP_PATH, encoding="utf-8") as f:
            ship = json.load(f)
        self.assertEqual(test_project.props_outside(ship), [])
        room = ship["rooms"][0]
        xs = [p[0] for p in room["poly"]]
        room["props"][0]["pos"][0] = min(xs) - 0.3                 # 0.3 m outside the west wall line: the old margin of -0.4 let it pass
        self.assertTrue(test_project.props_outside(ship))

    def test_P044_known_unreachable_pockets_are_an_allowlist(self):
        import test_walkable
        self.assertEqual(test_walkable.KNOWN_POCKET_ROOMS, {"airlock", "cabinB", "life"})


if __name__ == "__main__":
    unittest.main()
