"""Tests of tools/layout/audit.py: geometry helpers, each rule on a tiny synthetic ship, and the committed ship.json.

Run:  python -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import audit as A  # noqa: E402

WHY = "A sufficiently long justification that explains why these items are in the room."


def mk_model(mid, cat, mount, hx, y0, y1, hz, top_y=None, z0=None, solid=True, mount_y=None):
    lo = [-hx, y0, -hz if z0 is None else z0]
    hi = [hx, y1, hz]
    return {"id": mid, "category": cat, "mount": mount, "mount_y": mount_y, "solid": solid, "top_y": top_y,
            "bounds_min": lo, "bounds_max": hi, "size": [2 * hx, y1 - y0, hi[2] - lo[2]]}


CATALOG = {m["id"]: m for m in [
    mk_model("crate", "cabinet", "floor", 0.5, 0.0, 1.0, 0.5, top_y=1.0),
    mk_model("lockerbox", "locker", "floor", 0.5, 0.0, 1.0, 0.5, top_y=1.0),
    mk_model("tallcab", "cabinet", "floor", 0.3, 0.0, 2.8, 0.3),
    mk_model("giant", "cabinet", "floor", 0.3, 0.0, 2.98, 0.3),
    mk_model("pod", "ceilinglight", "ceiling", 0.3, -0.5, 0.0, 0.3),
    mk_model("bed", "bed", "floor", 0.5, 0.0, 0.5, 1.0),
    mk_model("box", "toolbox", "table", 0.1, 0.0, 0.1, 0.1),
    mk_model("sign", "sign", "wall", 0.25, -0.15, 0.15, 0.025, z0=0.0, mount_y=1.5),
    mk_model("lamp", "ceilinglight", "ceiling", 0.3, -0.1, 0.0, 0.3),
    mk_model("rug", "floorpanel", "floor", 1.0, 0.0, 0.02, 1.0, solid=False),
]}


def prop(m, x, z, y=0.0, yaw=0.0, b="EN-01", scale=None):
    p = {"m": m, "pos": [x, y, z], "yaw": yaw}
    if b:
        p["b"] = b
    if scale:
        p["scale"] = scale
    return p


def make_room(rid, rect, props, openings, zones, bom_code, dept="transit", height=3.0, lights=True):
    x0, z0, x1, z1 = rect
    poly = [[x0, z0], [x1, z0], [x1, z1], [x0, z1]]
    edges = [{"side": "N", "a": [x0, z0], "b": [x1, z0], "hull": False}, {"side": "E", "a": [x1, z0], "b": [x1, z1], "hull": False},
             {"side": "S", "a": [x1, z1], "b": [x0, z1], "hull": False}, {"side": "W", "a": [x0, z1], "b": [x0, z0], "hull": False}]
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    lamp = prop("lamp", cx, cz, y=height, b=bom_code)
    return {"id": rid, "name": rid, "deck": 1, "rect": rect, "poly": poly, "edges": edges, "height": height, "dept": dept,
            "openings": openings, "zones": zones, "floor_holes": [], "ceiling_holes": [], "links": [],
            "lights": [{"type": "spot", "pos": [cx, height - 0.2, cz]}] if lights else [],
            "props": [lamp] + props, "brief": {"purpose": "Synthetic test room."},
            "bom": [{"code": bom_code, "title": "Everything", "why": WHY}]}


def clean_ship():
    """Lobby (0..10) and engineering room (10..20) joined by a door at z=5; a crate with a box on it, a wall sign."""
    door = {"side": "E", "c": 5.0, "w": 2.36, "y0": 0.0, "y1": 2.76, "kind": "door"}
    lobby = make_room("lobby1", [0, 0, 10, 10], [], [dict(door)], [{"kind": "door", "rect": [8, 3.62, 10, 6.38], "why": "door"}], "LB-01")
    eng = make_room("eng", [10, 0, 20, 10],
                    [prop("crate", 15, 2), prop("box", 15, 2, y=1.0), prop("sign", 16, 9.85, y=1.5, yaw=180.0)],
                    [dict(door, side="W")], [{"kind": "door", "rect": [10, 3.62, 12, 6.38], "why": "door"}], "EN-01")
    return {"version": 2, "decks": [{"id": 1, "y": 0.0}], "hull": {"1": [[0, 0], [20, 0], [20, 10], [0, 10]]},
            "rooms": [lobby, eng], "doors": [], "stairs": []}


def eng_of(ship):
    return next(r for r in ship["rooms"] if r["id"] == "eng")


def rules(viol, sev="error"):
    return sorted({v["rule"] for v in viol if v["severity"] == sev})


class GeometryTests(unittest.TestCase):
    def test_touching_squares_do_not_overlap(self):
        a = A.rect_poly((0, 0, 1, 1))
        b = A.rect_poly((1, 0, 2, 1))
        self.assertFalse(A.polys_intersect(a, b)[0])
        c = A.rect_poly((0.999, 0, 2, 1))              # 1 mm of rounding noise is tolerated
        self.assertFalse(A.polys_intersect(a, c)[0])

    def test_overlapping_squares(self):
        hit, area, depth = A.polys_intersect(A.rect_poly((0, 0, 1, 1)), A.rect_poly((0.5, 0.5, 1.5, 1.5)))
        self.assertTrue(hit)
        self.assertAlmostEqual(area, 0.25, places=3)
        self.assertAlmostEqual(depth, 0.5, places=3)

    def test_rotated_footprint(self):
        p = A.Prop(prop("bed", 0, 0, yaw=90.0), CATALOG["bed"])       # 1 x 2 m, turned 90 degrees: 2 m along X
        self.assertAlmostEqual(p.aabb[2] - p.aabb[0], 2.0, places=3)
        self.assertAlmostEqual(p.aabb[3] - p.aabb[1], 1.0, places=3)

    def test_segment_polygon_distance(self):
        sq = A.rect_poly((0, 0, 1, 1))
        self.assertAlmostEqual(A.seg_poly_dist((0, 2), (1, 2), sq), 1.0, places=6)
        self.assertEqual(A.seg_poly_dist((0.5, -1), (0.5, 2), sq), 0.0)
        self.assertAlmostEqual(A.seg_poly_dist((3, 2), (4, 2), sq), (2 ** 2 + 1) ** 0.5, places=6)


class RuleTests(unittest.TestCase):
    def run_ship(self, ship, **kw):
        return A.audit(ship, CATALOG, **kw)

    def expect(self, ship, rule):
        viol = self.run_ship(ship)
        self.assertEqual(rules(viol), [rule], [(v["rule"], v["msg"]) for v in viol if v["severity"] == "error"])
        return [v for v in viol if v["rule"] == rule]

    def mutate(self, fn):
        ship = clean_ship()
        fn(eng_of(ship), ship)
        return ship

    def test_clean_ship_has_no_errors(self):
        viol = self.run_ship(clean_ship())
        self.assertEqual(rules(viol), [], [v["msg"] for v in viol])

    def test_clean_ship_v1_format(self):
        ship = clean_ship()
        ship["version"] = 1
        for r in ship["rooms"]:
            for k in ("poly", "edges", "zones", "bom", "brief", "floor_holes", "ceiling_holes", "links"):
                r.pop(k, None)
            for p in r["props"]:
                p.pop("b", None)
        del ship["hull"]
        self.assertEqual(rules(self.run_ship(ship)), [])

    def test_touching_props_are_fine(self):
        ship = self.mutate(lambda e, s: e["props"].append(prop("crate", 16.0, 2)))         # touches the crate at x=15 exactly
        self.assertEqual(rules(self.run_ship(ship)), [])
        ship = self.mutate(lambda e, s: e["props"].append(prop("crate", 15.999, 4.0)))      # 1 mm of overlap noise
        ship["rooms"][1]["props"][-1]["pos"][2] = 3.0
        self.assertEqual(rules(self.run_ship(ship)), [])

    def test_footprint_overlap(self):
        v = self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 15.5, 2))), "footprint-overlap")
        self.assertEqual(v[0]["room"], "eng")
        self.assertIn("crate", v[0]["msg"])

    def test_flat_items_may_lie_under_furniture(self):
        ship = self.mutate(lambda e, s: e["props"].append(prop("rug", 15, 2, b="EN-01")))
        self.assertEqual(rules(self.run_ship(ship)), [])

    def test_outside_shell(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 19.8, 7))), "outside-shell")

    def test_door_clearance(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 11, 5))), "door-clearance")

    def test_hole_clash(self):
        def f(e, s):
            e["floor_holes"].append([16, 7, 18, 9])
            e["props"].append(prop("crate", 17, 8))
        viol = self.run_ship(self.mutate(f))          # the hole has no matching ceiling hole below (single deck) -> also flagged
        self.assertEqual(rules(viol), ["hole-clash", "stair-consistency"])

    def test_window_blocked(self):
        def f(e, s):
            e["openings"].append({"side": "N", "c": 15.0, "w": 3.0, "y0": 0.9, "y1": 2.4, "kind": "window"})
            e["props"].append(prop("crate", 15, 0.8))
        self.expect(self.mutate(f), "window-blocked")

    def test_window_with_clear_floor_is_fine(self):
        def f(e, s):
            e["openings"].append({"side": "N", "c": 15.0, "w": 3.0, "y0": 0.9, "y1": 2.4, "kind": "window"})
        self.assertEqual(rules(self.run_ship(self.mutate(f))), [])

    def test_wall_item_across_window(self):
        def f(e, s):
            e["openings"].append({"side": "N", "c": 15.0, "w": 3.0, "y0": 0.9, "y1": 2.4, "kind": "window"})
            e["props"].append(prop("sign", 15.0, 0.15, y=1.5, yaw=0.0))
        self.expect(self.mutate(f), "wall-item-overlap")

    def test_wall_items_overlapping_each_other(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("sign", 16.2, 9.85, y=1.5, yaw=180.0))), "wall-item-overlap")

    def test_wall_item_beside_each_other_ok(self):
        ship = self.mutate(lambda e, s: e["props"].append(prop("sign", 16.6, 9.85, y=1.5, yaw=180.0)))
        self.assertEqual(rules(self.run_ship(ship)), [])

    def test_wall_item_beyond_wall_end(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("sign", 19.9, 0.15, y=1.5, yaw=0.0))), "wall-item-span")

    def test_wall_item_above_ceiling(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("sign", 13, 0.15, y=2.95, yaw=0.0))), "wall-item-span")

    def test_wall_item_in_mid_air(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("sign", 15, 5.0, y=1.5, yaw=0.0))), "mount-mismatch")

    def test_wall_facing(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("sign", 13, 0.15, y=1.5, yaw=90.0))), "wall-facing")

    def test_ceiling_overlap(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("lamp", 15.2, 5.0, y=3.0))), "ceiling-overlap")

    def test_ceiling_height(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("lamp", 12, 8.0, y=2.5))), "mount-mismatch")

    def test_ceiling_item_over_hole(self):
        def f(e, s):
            e["ceiling_holes"].append([12, 7, 14, 9])
            e["props"].append(prop("lamp", 13, 8.0, y=3.0))
            s["rooms"][0]["floor_holes"].append([12, 7, 14, 9])       # keep the stair rule quiet
        viol = self.run_ship(self.mutate(f))
        self.assertIn("ceiling-overlap", rules(viol))

    def test_wall_floor_clash(self):
        self.expect(self.mutate(lambda e, s: (e["props"].append(prop("crate", 13, 0.65)),
                                              e["props"].append(prop("sign", 13, 0.15, y=0.8, yaw=0.0)))), "wall-floor-clash")

    def test_wall_item_above_furniture_is_fine(self):
        ship = self.mutate(lambda e, s: (e["props"].append(prop("crate", 13, 0.65)),
                                         e["props"].append(prop("sign", 13, 0.15, y=1.5, yaw=0.0))))
        self.assertEqual(rules(self.run_ship(ship)), [])

    def test_ceiling_floor_clash(self):
        self.expect(self.mutate(lambda e, s: (e["props"].append(prop("tallcab", 17, 8)),
                                              e["props"].append(prop("pod", 17, 8, y=3.0)))), "ceiling-floor-clash")

    def test_too_tall(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("giant", 17, 8))), "too-tall")

    def test_tabletop_host(self):
        self.expect(self.mutate(lambda e, s: (e["props"].append(prop("lockerbox", 17, 8)),
                                              e["props"].append(prop("box", 17, 8, y=1.0)))), "tabletop-host")

    def test_hull_opening_needs_no_neighbour(self):
        def f(e, s):
            e["edges"][1]["hull"] = True
            e["openings"].append({"side": "E", "c": 5.0, "w": 3.0, "y0": 0.0, "y1": 3.0, "kind": "open"})
        self.assertEqual(rules(self.run_ship(self.mutate(f))), [])

    def test_rules_filter_and_list(self):
        ship = self.mutate(lambda e, s: e["props"].append(prop("crate", 15.5, 2)))
        self.assertEqual(rules(A.audit(ship, CATALOG, rules=["lights"])), [])
        self.assertEqual(rules(A.audit(ship, CATALOG, rules=["footprint-overlap"])), ["footprint-overlap"])
        for r in ("wall-floor-clash", "ceiling-floor-clash", "too-tall", "tabletop-host", "mount-mismatch", "footprint-overlap"):
            self.assertIn(r, A.RULES)

    def test_floating_floor(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 17, 8, y=0.5))), "floating-floor")

    def test_table_item_floating(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("box", 15, 2, y=1.4))), "table-support")

    def test_table_item_buried(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("box", 15, 2, y=0.5))), "table-support")

    def test_table_item_overhanging(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("box", 15.45, 2, y=1.0))), "table-support")

    def test_table_item_on_nothing(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("box", 17, 8, y=0.0))), "table-support")

    def test_policy_violation(self):
        v = self.expect(self.mutate(lambda e, s: e["props"].append(prop("bed", 17, 8))), "policy-category")
        self.assertIn("bed", v[0]["msg"])

    def test_bom_missing_line(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 17, 8, b=None))), "bom-line")

    def test_bom_unknown_line(self):
        self.expect(self.mutate(lambda e, s: e["props"].append(prop("crate", 17, 8, b="XX-99"))), "bom-line")

    def test_bom_empty_line_and_short_why(self):
        def f(e, s):
            e["bom"].append({"code": "EN-02", "title": "Nothing", "why": "short"})
        ship = self.mutate(f)
        viol = self.run_ship(ship)
        self.assertEqual(rules(viol), ["bom-line"])
        self.assertIn("bom-line", rules(viol, "warn"))

    def test_brief_required(self):
        self.expect(self.mutate(lambda e, s: e.update(brief={})), "bom-line")

    def test_lights(self):
        self.expect(self.mutate(lambda e, s: e.update(lights=[])), "lights")

    def test_ceiling_fixture_required(self):
        def f(e, s):
            e["props"] = [p for p in e["props"] if p["m"] != "lamp"]
        self.expect(self.mutate(f), "lights")

    def test_density_error(self):
        def f(e, s):
            e["props"] = [p for p in e["props"] if p["m"] == "lamp"]
            e["props"].append(prop("crate", 16, 5, scale=[7.5, 1.0, 8.2]))
        self.expect(self.mutate(f), "density")

    def test_walkable_door_blocked(self):
        def f(e, s):
            for r in s["rooms"]:
                r["zones"] = []
            e["props"].append(prop("crate", 11, 5, scale=[1.0, 1.0, 6.0]))
        viol = self.expect(self.mutate(f), "walkable")
        self.assertTrue(any("eng" == v["room"] for v in viol))

    def test_walkable_pocket_is_a_warning(self):
        def f(e, s):
            e["props"].append(prop("crate", 12.5, 5.0, scale=[1.0, 1.0, 9.7]))        # wall of crates splits the room
        ship = self.mutate(f)
        viol = self.run_ship(ship)
        self.assertEqual(rules(viol), [])
        self.assertIn("unreachable-pocket", rules(viol, "warn"))

    def test_opening_outside_wall(self):
        def f(e, s):
            for r in s["rooms"]:
                for o in r["openings"]:
                    o["c"] = 9.8
        ship = self.mutate(f)
        viol = self.run_ship(ship)
        self.assertEqual(rules(viol), ["opening-validity"])

    def test_opening_without_neighbour(self):
        def f(e, s):
            e["openings"] = []
            e["zones"] = []
        viol = self.run_ship(self.mutate(f))
        self.assertIn("opening-validity", rules(viol))

    def test_hull_containment(self):
        def f(e, s):
            s["hull"]["1"] = [[0, 0], [19, 0], [19, 10], [0, 10]]
        self.expect(self.mutate(f), "hull-containment")

    def test_rooms_overlap(self):
        def f(e, s):
            e["poly"] = [[9, 0], [20, 0], [20, 10], [9, 10]]
            e["edges"][0]["a"] = [9, 0]
            e["edges"][3]["a"] = [9, 10]
            e["edges"][3]["b"] = [9, 0]
            e["edges"][2]["b"] = [9, 10]
            e["rect"] = [9, 0, 20, 10]
        ship = self.mutate(f)
        ship["hull"]["1"] = [[0, 0], [20, 0], [20, 10], [0, 10]]
        self.assertIn("hull-containment", rules(self.run_ship(ship)))

    def test_stair_holes_must_match(self):
        self.expect(self.mutate(lambda e, s: e["ceiling_holes"].append([1, 1, 2, 2])), "stair-consistency")

    def test_stair_flight_outside_tower(self):
        def f(e, s):
            s["stairs"] = [{"id": "SA", "width": 1.4, "runs": [{"deck_lo": 1, "deck_hi": 1, "flights": [
                {"pos": [18.0, 0.0, 5.0], "yaw": 90.0, "rise": 2.0, "run": 4.0},
                {"pos": [14.0, 2.0, 5.0], "yaw": -90.0, "rise": 2.0, "run": 4.0}],
                "landing": {"rect": [12, 4, 14, 6], "y": 2.0}}]}]
        viol = self.run_ship(self.mutate(f))
        self.assertIn("stair-consistency", rules(viol))

    def test_unknown_room_policy_reported_once(self):
        ship = clean_ship()
        ship["rooms"][1]["id"] = "zzz1"
        ship["rooms"][0]["id"] = "zzz2"
        viol = self.run_ship(ship)
        self.assertEqual(sum(1 for v in viol if v["rule"] == "unknown-room-policy"), 1)

    def test_only_room_filter(self):
        ship = self.mutate(lambda e, s: e["props"].append(prop("crate", 15.5, 2)))
        self.assertEqual(rules(A.audit(ship, CATALOG, only_room="lobby1")), [])
        self.assertEqual(rules(A.audit(ship, CATALOG, only_room="eng")), ["footprint-overlap"])

    def test_stats(self):
        st = {r["room"]: r for r in A.audit_stats(clean_ship(), CATALOG)}
        self.assertEqual(st["eng"]["floor_props"], 1)
        self.assertAlmostEqual(st["eng"]["occupancy"], 0.01, places=3)
        self.assertEqual(st["eng"]["distinct_models"], 4)


class CommittedShipTests(unittest.TestCase):
    def test_committed_ship_has_no_audit_errors(self):
        godot = os.path.join(ROOT, "godot", "data")
        with open(os.path.join(godot, "ship.json")) as f:
            ship = json.load(f)
        cat = A.load_catalog(os.path.join(godot, "catalog.json"))
        errors = [v for v in A.audit(ship, cat) if v["severity"] == "error"]
        lines = [f"[{v['rule']}] {v['room']}: {v['msg']}" for v in errors[:40]]
        self.assertEqual(errors, [], f"{len(errors)} audit errors, first ones:\n" + "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
