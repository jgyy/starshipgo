"""Unit tests of the layout engine (tools/layout/shiplib.py, hull.py, dressing.py) on a tiny synthetic catalogue."""
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
import hull  # noqa: E402
import shiplib  # noqa: E402


def model(mid, cat, mount, size, top_y=None, mount_y=None):
    w, h, d = size
    lo_y, hi_y = (-h, 0.0) if mount == "ceiling" else (0.0, h)     # ceiling models hang down from their origin
    return {"id": mid, "category": cat, "label": mid, "file": f"models/{cat}/{mid}.glb", "mount": mount, "mount_y": mount_y,
            "tags": [], "solid": True, "size": list(size), "bounds_min": [-w / 2, lo_y, -d / 2], "bounds_max": [w / 2, hi_y, d / 2],
            "tris": 100, "top_y": top_y, "bytes": 1000, "family": "x"}


MODELS = [
    model("table_a", "table", "floor", (1.6, 0.75, 0.8), top_y=0.75),
    model("chair_a", "chair", "floor", (0.5, 0.9, 0.5)),
    model("tall_a", "locker", "floor", (0.8, 2.0, 0.6)),
    model("panel_a", "wallpanel", "wall", (1.0, 1.2, 0.05), mount_y=1.5),
    model("sign_a", "sign", "wall", (0.6, 0.3, 0.05), mount_y=2.0),
    model("light_a", "ceilinglight", "ceiling", (0.6, 0.1, 0.6)),
    model("tall_b", "locker", "floor", (0.8, 3.3, 0.6)),
    model("cup_a", "tableware", "table", (0.1, 0.1, 0.1)),
    model("cup_b", "tableware", "table", (0.1, 0.1, 0.1)),
    model("chairhost_a", "chair", "floor", (0.5, 0.5, 0.5), top_y=0.5),
    model("door_a", "door", "floor", (2.0, 2.6, 0.2)),
    model("frame_a", "doorframe", "floor", (2.0, 2.6, 0.2)),
]


def make_ship(rect=(0.0, 0.0, 8.0, 6.0), clip=False):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"models": MODELS}, f)
    cat = shiplib.Catalog(f.name)
    os.unlink(f.name)
    ship = shiplib.Ship(cat)
    ship.decks = [{"id": 1, "name": "D", "y": 0.0}, {"id": 2, "name": "E", "y": 4.0}]
    room = shiplib.Room(ship, "r", "Room", 1, rect, clip=clip)
    ship.add_room(room)
    return ship, room, cat


class GeometryTests(unittest.TestCase):
    def test_hull_outlines_are_convex_and_tapered(self):
        for d in (1, 2, 3):
            o = hull.outline(d)
            self.assertTrue(hull.is_convex(o))
            self.assertGreater(hull.area(o), 800)
            half = max(abs(x) for x, _ in o)
            self.assertAlmostEqual(half, hull.BEAM_HALF, places=2)

    def test_clip_rectangle_by_hull_gives_diagonal_walls_at_the_bow(self):
        ship, _, cat = make_ship()
        ship.hull = {1: hull.outline(1)}
        bow = shiplib.Room(ship, "bow", "Bow", 1, (-13, -30, 13, -16), clip=True)
        sides = [e["side"] for e in bow.edges]
        self.assertTrue(any(s.startswith("D") for s in sides), sides)
        self.assertTrue(all(bow.inside(x, z, -1e-6) for x, z in bow.poly))
        mid = shiplib.Room(ship, "mid", "Mid", 1, (-13, -5, 13, 5), clip=True)
        self.assertEqual(sorted(e["side"] for e in mid.edges), ["E", "N", "S", "W"])

    def test_inside_uses_wall_margin(self):
        _, room, _ = make_ship()
        self.assertTrue(room.inside(4, 3, 0.15))
        self.assertFalse(room.inside(0.1, 3, 0.15))
        self.assertTrue(room.inside(0.1, 3, 0.0))

    def test_sat_overlap_and_margin(self):
        a = shiplib.obb_corners(0, 0, 0.5, 0.5, 0)
        b = shiplib.obb_corners(1.2, 0, 0.5, 0.5, 0)       # gap 0.2
        self.assertFalse(shiplib.polys_overlap(a, b))
        self.assertTrue(shiplib.polys_overlap(a, b, 0.3))   # needs 0.3 clearance -> clashes
        self.assertFalse(shiplib.polys_overlap(a, b, 0.1))


class PlacementTests(unittest.TestCase):
    def test_margin_grows_the_clearance_instead_of_shrinking_it(self):
        """B003: Room.free() applied the margin backwards so a clearance request allowed overlaps."""
        _, room, cat = make_ship()
        t = cat.models["table_a"]
        self.assertIsNotNone(room.place(t, 4, 3, 0.0))
        near = room.place(cat.models["chair_a"], 4, 3 + 0.4 + 0.25 + 0.2, 0.0, margin=0.3)   # 0.2 m gap, wants 0.3
        self.assertIsNone(near)
        ok = room.place(cat.models["chair_a"], 4, 3 + 0.4 + 0.25 + 0.4, 0.0, margin=0.3)
        self.assertIsNotNone(ok)

    def test_no_overlaps(self):
        _, room, cat = make_ship()
        self.assertIsNotNone(room.place(cat.models["table_a"], 4, 3, 0.0))
        self.assertIsNone(room.place(cat.models["table_a"], 4.5, 3.2, 90.0))

    def test_place_refuses_wall_models_and_wrong_heights(self):
        """B005/B015: place() used to drop wall-mount models mid-room or at ceiling height."""
        _, room, cat = make_ship()
        self.assertIsNone(room.place(cat.models["panel_a"], 4, 3, 0.0))
        self.assertIsNone(room.place(cat.models["tall_a"], 4, 3, 0.0, y=room.y + room.h))
        self.assertIsNone(room.place(cat.models["light_a"], 4, 3, 0.0, y=room.y + 1.0))
        self.assertIsNotNone(room.place(cat.models["light_a"], 4, 3, 0.0, y=room.y + room.h))

    def test_light_grid_only_hangs_ceiling_models(self):
        _, room, cat = make_ship()
        room.light_grid(cats=("ceilinglight", "wallpanel"), spacing=3.0)
        mounts = {cat.models[p["m"]]["mount"] for p in room.props}
        self.assertEqual(mounts, {"ceiling"})
        self.assertTrue(room.lights)

    def test_run_with_wall_mount_hangs_only_wall_models(self):
        """B004: run(wall_mount=True) mounted floor / ceiling / table models on the wall."""
        _, room, cat = make_ship()
        placed = room.run("N", ["wallpanel", "table", "tableware", "ceilinglight"], wall_mount=True)
        self.assertTrue(placed)
        self.assertTrue(all(cat.models[p["m"]]["mount"] == "wall" for p in placed))

    def test_wall_item_stays_on_the_wall_and_avoids_openings(self):
        _, room, cat = make_ship()
        self.assertIsNone(room.wall_item("N", cat.models["panel_a"], 0.3))         # sticks out past the wall end
        self.assertIsNotNone(room.wall_item("N", cat.models["panel_a"], 4.0))
        self.assertIsNone(room.wall_item("N", cat.models["panel_a"], 4.2))         # overlaps the first panel
        room.add_window("S", 4.0, 2.0, 0.9, 2.4)
        self.assertIsNone(room.wall_item("S", cat.models["panel_a"], 4.0))         # over a window

    def test_wall_items_and_tall_floor_props_do_not_intersect(self):
        """B021: floor props placed after wall items used to swallow them (and the other way round)."""
        _, room, cat = make_ship()
        self.assertIsNotNone(room.wall_item("N", cat.models["panel_a"], 4.0, y=1.4))
        self.assertIsNone(room.against_wall("N", cat.models["tall_a"], 4.0, gap=0.0))
        self.assertIsNotNone(room.against_wall("N", cat.models["tall_a"], 6.5, gap=0.0))
        self.assertIsNone(room.wall_item("N", cat.models["panel_a"], 6.5, y=1.4))

    def test_table_items_only_on_work_surfaces_and_never_overlap(self):
        """B017/B018/B019."""
        _, room, cat = make_ship()
        table = room.place(cat.models["table_a"], 4, 3, 0.0)
        a = room.on_top(table, cat.models["cup_a"], 0.0, 0.0)
        self.assertIsNotNone(a)
        self.assertIsNone(room.on_top(table, cat.models["cup_b"], 0.0, 0.0))         # same spot
        self.assertIsNotNone(room.on_top(table, cat.models["cup_b"], 0.4, 0.0))
        self.assertIsNone(room.on_top(table, cat.models["cup_a"], 1.5, 0.0))         # hangs over the edge
        chair = room.place(cat.models["chairhost_a"], 1.0, 1.0, 0.0)
        self.assertIsNone(room.on_top(chair, cat.models["cup_a"], 0.0, 0.0))         # a chair is not a table

    def test_table_item_rests_on_top_of_the_host(self):
        _, room, cat = make_ship()
        table = room.place(cat.models["table_a"], 4, 3, 0.0)
        cup = room.on_top(table, cat.models["cup_a"], 0.0, 0.0)
        self.assertAlmostEqual(cup["pos"][1], room.y + 0.75, places=3)

    def test_ceiling_items_clear_tall_floor_props(self):
        """B022: ceiling placements never looked at the floor props below them."""
        _, room, cat = make_ship()
        room.place(cat.models["tall_b"], 4, 3, 0.0)                                      # 3.3 m tall, top at 3.3 m
        self.assertIsNone(room.place(cat.models["light_a"], 4, 3, 0.0, y=room.y + room.h))
        self.assertIsNotNone(room.place(cat.models["light_a"], 6.5, 3, 0.0, y=room.y + room.h))

    def test_floor_props_cannot_poke_through_the_ceiling(self):
        _, room, cat = make_ship()
        ship = room.ship
        low = shiplib.Room(ship, "low", "Low", 1, (20, 0, 26, 6), height=2.5, clip=False)
        self.assertIsNotNone(low.place(cat.models["tall_a"], 23, 3, 0.0))                 # 2.0 m fits under 2.5 m
        self.assertIsNone(low.place(cat.models["tall_b"], 23, 3, 0.0))                    # 3.3 m does not

    def test_room_rng_seed_is_unique_per_id(self):
        """B052: a weak additive hash gave different ids the same seed."""
        ship, _, _ = make_ship()
        a = shiplib.Room(ship, "abc", "a", 1, (0, 0, 2, 2), clip=False)
        b = shiplib.Room(ship, "cba", "b", 1, (0, 0, 2, 2), clip=False)
        self.assertNotEqual(a.rng.random(), b.rng.random())

    def test_no_leaking_penalty_state(self):
        """B016: Catalog.pen leaked placement-failure penalties across rooms."""
        _, _, cat = make_ship()
        self.assertFalse(hasattr(cat, "pen"))

    def test_label_miss_is_recorded_not_silent(self):
        """B050."""
        _, _, cat = make_ship()
        m = cat.pick("table", label="does_not_exist")
        self.assertIsNotNone(m)
        self.assertIn(("table", "does_not_exist"), cat.missing_labels)
        cat.missing_labels.clear()
        cat.pick("table", label="table_a")
        self.assertFalse(cat.missing_labels)


class ShipTests(unittest.TestCase):
    def test_deck_y_unknown_deck_is_a_clear_error(self):
        """B051: bare StopIteration."""
        ship, _, _ = make_ship()
        with self.assertRaises(KeyError):
            ship.deck_y(9)

    def test_link_validates_the_opening(self):
        ship, room, cat = make_ship()
        other = shiplib.Room(ship, "o", "Other", 1, (8.0, 0.0, 14.0, 6.0), clip=False)
        ship.add_room(other)
        ship.link("r", "o", c=3.0)
        self.assertEqual(len(ship.doors), 1)
        with self.assertRaises(ValueError):
            ship.link("r", "o", c=0.2)              # opening would run off the end of the wall
        far = shiplib.Room(ship, "f", "Far", 1, (20.0, 0.0, 24.0, 6.0), clip=False)
        ship.add_room(far)
        with self.assertRaises(ValueError):
            ship.link("r", "f")                     # rooms do not touch

    def test_door_clearance_blocks_furniture(self):
        ship, room, cat = make_ship()
        other = shiplib.Room(ship, "o", "Other", 1, (8.0, 0.0, 14.0, 6.0), clip=False)
        ship.add_room(other)
        ship.link("r", "o", c=3.0)
        self.assertIsNone(room.place(cat.models["table_a"], 7.0, 3.0, 90.0))


class ShipGeneratorTests(unittest.TestCase):
    """The real generator: geometry sanity that the generator itself must guarantee (B060)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))
        import generate_ship
        cls.gs = generate_ship
        cls.cat = shiplib.Catalog(os.path.join(ROOT, "godot", "data", "catalog.json"))
        cls.B = generate_ship.build(cls.cat)

    def test_no_label_misses(self):
        self.assertEqual(sorted(self.cat.missing_labels), [])

    def test_spawn_and_cameras_are_inside_rooms(self):
        S = self.B.ship
        sp = S.spawn["pos"]
        self.assertTrue(any(r.deck == 2 and r.inside(sp[0], sp[2], 0.3) for r in S.rooms.values()), "spawn is not inside a deck-2 room")
        inside = 0
        for cam in S.cameras:
            if cam.get("exterior"):
                continue
            room = S.rooms[cam["room"]]
            x, y, z = cam["pos"]
            self.assertTrue(room.inside(x, z, 0.2), f"camera {cam['name']} is outside {room.id}")
            self.assertAlmostEqual(y - 1.62, room.y, places=2)
            inside += 1
        self.assertGreaterEqual(inside, 20)

    def test_camera_eyes_and_spawn_are_not_inside_props(self):
        """B060: two tour cameras used to sit inside a plasma chamber / crane arm."""
        S = self.B.ship
        pts = [(S.spawn["pos"][0], S.spawn["pos"][2], S.rooms["lobby2"])]
        for cam in S.cameras:
            if not cam.get("exterior"):
                pts.append((cam["pos"][0], cam["pos"][2], S.rooms[cam["room"]]))
        for x, z, room in pts:
            for p in room.props:
                m = p["_m"]
                if m["mount"] == "floor" and m["size"][1] > 0.3 and p.get("_obb") and shiplib._point_in_poly((x, z), p["_obb"], -0.1):
                    self.fail(f"({x:.2f}, {z:.2f}) is inside {p['m']} in {room.id}")

    def test_every_link_joins_two_walls_that_exist(self):
        for r in self.B.ship.rooms.values():
            for lk in r.links:
                self.assertIn(lk["to"], self.B.ship.rooms)
                self.assertIsNotNone(r.edge(lk["side"]))


if __name__ == "__main__":
    unittest.main()
