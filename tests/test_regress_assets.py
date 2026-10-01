"""Regression tests for the asset-side defects fixed in the round-2 assets pass (docs/bugs/round2/assets.json).

Bare standard library: the committed catalog and GLBs are read directly, bpy is only needed for the (skipped
without it) rebuild-twice check.
"""
import ast
import collections
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG = os.path.join(ROOT, "godot", "data", "catalog.json")
CT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read(path):
    with open(path, "rb") as fh:
        data = fh.read()
    off, js, binc = 12, None, b""
    while off < len(data):
        n, t = struct.unpack_from("<I4s", data, off)
        body = data[off + 8: off + 8 + n]
        if t == b"JSON":
            js = json.loads(body)
        elif t == b"BIN\0":
            binc = body
        off += 8 + n
    return js, binc


def accessor(js, binc, i):
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    fmt, sz = CT[a["componentType"]]
    nc = NC[a["type"]]
    stride = bv.get("byteStride") or sz * nc
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    rows = [struct.unpack_from("<" + fmt * nc, binc, base + k * stride) for k in range(a["count"])]
    return [r[0] for r in rows] if nc == 1 else rows


def meshes(path):
    """[(positions with the node translation applied, triangles)] for every mesh primitive of the GLB."""
    js, binc = read(path)
    out = []
    for n in js["nodes"]:
        if "mesh" not in n:
            continue
        t = n.get("translation", (0, 0, 0))
        for p in js["meshes"][n["mesh"]]["primitives"]:
            pos = [(x + t[0], y + t[1], z + t[2]) for x, y, z in accessor(js, binc, p["attributes"]["POSITION"])]
            idx = accessor(js, binc, p["indices"])
            out.append((pos, [tuple(idx[k:k + 3]) for k in range(0, len(idx), 3)]))
    return out


def bounds(path):
    pts = [p for pos, _ in meshes(path) for p in pos]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def load_catalog():
    with open(CATALOG) as fh:
        return json.load(fh)["models"]


class CatalogMatchesGlbs(unittest.TestCase):
    def test_catalog_bounds_are_the_glb_bounds(self):
        """The catalog is what the layout engine trusts; a stale entry puts props into walls or the floor."""
        bad = []
        for e in load_catalog():
            lo, hi = bounds(os.path.join(ROOT, "godot", e["file"]))
            if max(abs(a - b) for a, b in zip(lo + hi, e["bounds_min"] + e["bounds_max"])) > 0.002:
                bad.append(e["id"])
        self.assertEqual(bad, [])


class MountOrigins(unittest.TestCase):
    """A001/A002: a floor/table model rests on y=0, a wall model's back is z=0, a ceiling model hangs from y=0."""
    HOVERS = {"medsupply_hover_stretcher"}          # 5 cm on purpose (thrusters)
    SUNK = {"duct_plenum_damper_box"}               # 5 cm into its wall

    def test_no_slop_left(self):
        bad = []
        for e in load_catalog():
            lo, hi, mount, i = e["bounds_min"], e["bounds_max"], e["mount"], e["id"]
            if mount in ("floor", "table") and abs(lo[1]) > 0.0015 and i not in self.HOVERS:
                bad.append((i, "y", lo[1]))
            elif mount == "wall" and abs(lo[2]) > 0.0015 and i not in self.SUNK:
                bad.append((i, "z", lo[2]))
            elif mount == "ceiling" and abs(hi[1]) > 0.0015:
                bad.append((i, "top", hi[1]))
        self.assertEqual(bad, [])


class NoInsideOutShells(unittest.TestCase):
    """A004: torus_prof walked its outline clockwise but lathe() wants counter-clockwise: donuts, bagels and the ice-cream
    rings were inside out (negative volume), i.e. invisible from outside with back-face culling."""
    MODELS = ["bakery_bagel_poppy", "bakery_donut_chocolate", "bakery_donut_pink_sprinkles", "dessert_ice_cream_cone_double"]

    def test_positive_volume(self):
        for mid in self.MODELS:
            e = next(e for e in load_catalog() if e["id"] == mid)
            vol = 0.0
            for pos, tris in meshes(os.path.join(ROOT, "godot", e["file"])):
                for a, b, c in tris:
                    ax, ay, az = pos[a]
                    bx, by, bz = pos[b]
                    cx, cy, cz = pos[c]
                    vol += (ax * (by * cz - bz * cy) - ay * (bx * cz - bz * cx) + az * (bx * cy - by * cx)) / 6.0
            with self.subTest(mid):
                self.assertGreater(vol, 0.0)


class VariantsDiffer(unittest.TestCase):
    """A005: CONVENTIONS.md - every variant must look different (door_cabin was a recolour of door_bulkhead)."""

    def test_no_two_models_share_geometry(self):
        by_key = collections.defaultdict(list)
        for e in load_catalog():
            if e["id"].startswith("sign_deck_"):  # the deck signs differ by their numeral texture only
                continue
            by_key[(e["tris"], tuple(e["size"]))].append(e)
        dup = []
        for group in by_key.values():
            if len(group) < 2:
                continue
            seen = {}
            for e in group:
                pts = sorted(p for pos, _ in meshes(os.path.join(ROOT, "godot", e["file"])) for p in pos)
                key = tuple(tuple(round(c, 3) for c in p) for p in pts)
                if key in seen:
                    dup.append((seen[key], e["id"]))
                seen[key] = e["id"]
        self.assertEqual(dup, [])


class ZfightLiftIsBounded(unittest.TestCase):
    """A003: fix_zfight lifted shared vertices on every pass and a six-pack of cans grew from 12.3 to 18 cm."""

    def test_sixpack_and_cucumbers_keep_their_size(self):
        by = {e["id"]: e for e in load_catalog()}
        self.assertLess(by["can_sixpack_cola"]["size"][1], 0.13)
        self.assertLess(by["veg_cucumbers_sliced"]["size"][0], 0.23)

    def test_no_model_grew_far_beyond_its_design(self):
        # table-top food is small; nothing in the food families may exceed 0.6 m in any direction
        for e in load_catalog():
            if e["mount"] == "table" and e["category"] in ("can", "veg", "bakery", "dessert", "bottle"):
                self.assertLess(max(e["size"]), 0.6, e["id"])


class Deterministic(unittest.TestCase):
    """A006: rebuilding must give identical GLBs (bevel output order followed pointer addresses)."""

    @unittest.skipUnless(os.environ.get("STARSHIP_BPY_PYTHON") or "bpy" in sys.modules, "needs a Python with bpy (set STARSHIP_BPY_PYTHON)")
    def test_build_twice_is_byte_identical(self):
        py = os.environ.get("STARSHIP_BPY_PYTHON", sys.executable)
        outs = []
        with tempfile.TemporaryDirectory() as tmp:
            tex = os.path.join(ROOT, "godot", "textures")
            for k in range(2):
                out = os.path.join(tmp, f"o{k}")
                os.makedirs(out)
                os.symlink(tex, os.path.join(out, "textures"))
                subprocess.run([py, os.path.join(ROOT, "blender", "build_all.py"), "--out", out, "--only",
                                "^(console_corner|desk_|door_officer|medbed_surgical|nozzle_rcs)", "--jobs", str(1 + k)],
                               check=True, capture_output=True, timeout=600)
                files = {}
                for dp, _, fs in os.walk(os.path.join(out, "models")):
                    for f in fs:
                        with open(os.path.join(dp, f), "rb") as fh:
                            files[f] = fh.read()
                outs.append(files)
            self.assertGreater(len(outs[0]), 5)
            self.assertEqual([f for f in outs[0] if outs[0][f] != outs[1].get(f)], [])

    def test_kit_never_iterates_sets_of_bmesh_elements(self):
        src = open(os.path.join(ROOT, "blender", "starship", "kit.py")).read()
        self.assertNotRegex(src, r"\{e for [^}]*link_(faces|edges)")
        self.assertNotRegex(src, r"\{f for [^}]*link_faces")
        self.assertIn("def canonical_order", src)


class UnusedImports(unittest.TestCase):
    """A007: the CI lint exempted blender/starship/components/, hiding dead imports."""

    def test_components_have_no_unused_imports(self):
        d = os.path.join(ROOT, "blender", "starship", "components")
        bad = []
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py") or f == "__init__.py":
                continue
            tree = ast.parse(open(os.path.join(d, f)).read())
            names = {}
            for n in ast.walk(tree):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    for a in n.names:
                        if a.name != "*":
                            names[(a.asname or a.name).split(".")[0]] = n.lineno
            used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | \
                   {n.value.id for n in ast.walk(tree) if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)}
            for nm, ln in names.items():
                if nm not in used and nm not in ("math",) and not re.search(r"\b%s\b" % nm, "\n".join(
                        l for l in open(os.path.join(d, f)).read().split("\n")[ln:])):
                    bad.append(f"{f}:{ln} {nm}")
        self.assertEqual(bad, [])


class DocsAndCiAgree(unittest.TestCase):
    """A008-A010: model counts quoted by README / CONVENTIONS / ci.yml must match the catalog."""

    def setUp(self):
        self.n = len(load_catalog())
        with open(os.path.join(ROOT, ".github", "workflows", "ci.yml")) as fh:
            self.ci = fh.read()

    def test_readme_and_conventions_quote_the_real_count(self):
        readme = open(os.path.join(ROOT, "README.md")).read()
        conv = open(os.path.join(ROOT, "blender", "CONVENTIONS.md")).read()
        self.assertIn(f"{self.n}-model component library", readme)
        self.assertIn(f"**{self.n}**", conv)
        self.assertNotRegex(readme, r"\b1000 GLBs|1000 x \.glb|regenerate 1000 models")

    def test_readme_decks_and_rooms(self):
        with open(os.path.join(ROOT, "godot", "data", "ship.json")) as fh:
            ship = json.load(fh)
        readme = open(os.path.join(ROOT, "README.md")).read()
        self.assertIn(f"{len(ship['rooms'])} rooms", readme)
        self.assertIn(f"{len(ship['doors'])} sliding doors", readme)
        self.assertEqual(len(ship["decks"]), 5)
        self.assertIn("five-deck", readme)

    def test_ci_catalog_check_is_not_pinned_to_1000(self):
        self.assertNotRegex(self.ci, r"len\(a\) == 1000")
        self.assertIn("tris", self.ci)           # the comparison covers triangle counts too
        self.assertIn("byte-identical", self.ci)  # and the reproducibility step exists

    def test_ci_lint_covers_components(self):
        self.assertNotIn("|^blender/starship/components/\"", self.ci)
        self.assertIn("assigned to but never used", self.ci)


if __name__ == "__main__":
    unittest.main()
