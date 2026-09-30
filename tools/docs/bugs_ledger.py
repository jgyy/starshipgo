#!/usr/bin/env python3
"""Write docs/BUGS.md: the ledger of the 113 audited defects of the original game and how each was resolved.

    python tools/docs/bugs_ledger.py

Input: docs/bugs/defects.json (verified findings of the audit of the original code, with file/line evidence),
docs/bugs/old_layout_audit.json (the original layout measured with tools/layout/audit.py) and, live, the audit of the
current ship.  The resolution text below says what changed and which test or check keeps it fixed.
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "layout"))

FIXED, KEPT = "fixed", "not changed"

R = {
    "B001": "The lifts are gone. Stairs are plain geometry, there is no teleport and no `lift` pointer on the player (`godot/scripts/lift.gd` deleted). `godot/tests/stair_test.gd` walks the player up and down both towers.",
    "B002": "The shell is built from explicit prisms with flat per-face normals (`ShipBuilder.Shell.prism`), no `generate_normals()` smoothing.",
    "B003": "`Room.free()` now calls `polys_overlap(corners, other, margin)` with the margin as required clearance. `tests/test_shiplib.py::test_margin_grows_the_clearance_instead_of_shrinking_it`.",
    "B004": "`Room.run(wall_mount=True)` only considers wall-mount models (and floor rows only floor/wall models). `test_run_with_wall_mount_hangs_only_wall_models`.",
    "B005": "`light_grid` only picks ceiling models and `place()` refuses wall models and wrong heights. `test_place_refuses_wall_models_and_wrong_heights`, audit rule `mount-mismatch`.",
    "B006": "CI runs Python 3.13 and installs `requirements-blender.txt` (`bpy>=5.2,<6`), the latest headless Blender.",
    "B007": "`player.gd` no longer has the dead `or true`; movement uses the simulated/real input vector only, the mouse is released on `ui_cancel`, focus loss and while the map is open.",
    "B008": "`door.gd` trigger is the door width + 0.6 m wide and 2.2 m deep (1.1 m each side of the door plane) instead of 3.6 x 3.8 m.",
    "B009": "`main.gd` tour checks the rendered image and exits with status 1 and a message when there is no renderer or the file cannot be written.",
    "B010": "Every room builds an `OccluderInstance3D` from its wall/slab prisms and `occlusion_culling/use_occlusion_culling=true` is set in `project.godot`.",
    "B011": "Props are batched into MultiMeshes per (room, model mesh) instead of one scene instance each, and the ship has 1.4 k props instead of 6.7 k. Measured: 17,950 -> ~355 draw calls, 16.6 k -> 3.5 k nodes (see README).",
    "B012": "Trim boxes (baseboard, stripe, cove) are visual only; they no longer get collision shapes (`prism(..., collide=false)`).",
    "B013": "At most 2 (3 in rooms over 150 m2) shadow-casting lights per room are kept; props under 0.6 m do not cast shadows.",
    "B014": "Balanced default (FXAA, cheap depth haze, half-resolution SSAO); volumetric fog, 4x MSAA are behind `--hq`.",
    "B015": "`Room.place()` honours the model mount: wall models are refused, floor models stay on the floor, ceiling models at the ceiling.",
    "B016": "`Catalog.pen` was removed; there is no placement-failure state left to leak across rooms.",
    "B017": "`Room.on_top` only accepts hosts from `shiplib.SURFACE_HOSTS` (tables, desks, benches, counters, racks ...). Audit rule `tabletop-host` (old layout: 943 violations, new: 0).",
    "B018": "Pillars and other full-height props are not in `SURFACE_HOSTS`; same rule as B017.",
    "B019": "`on_top` keeps the footprints of the items already on a host and rejects overlaps and overhangs. `test_table_items_only_on_work_surfaces_and_never_overlap`; audit `table-support`.",
    "B020": "Windows reserve their wall span and the audit rule `window-blocked` (floor props taller than 0.6 m within 0.5 m of a window) runs in CI; the new ship has 0.",
    "B021": "`place()` and `wall_item()` check each other: a wall item cannot intersect a tall floor prop and vice versa (`vboxes`). Audit `wall-floor-clash` (old layout 340, new 0).",
    "B022": "Ceiling items are checked against other ceiling items, holes and tall floor props. Audit `ceiling-floor-clash` (old 39, new 0) and `ceiling-overlap`.",
    "B023": "The random garnish pass is deleted. Every item comes from a written BOM line (`R.line`) and the placement policy (`tools/layout/policy.py`).",
    "B024": "The recipe helpers record every placement that does not fit (`RECIPE_DEBUG=1` prints them) and the audit fails on BOM lines without props (`bom-line`); the bridge now has its helm, ops, tactical and seats, all audited.",
    "B025": "Cargo Bay is a new, audited room: 0 overlapping floor props.",
    "B026": "`place()` refuses props taller than the room and the audit rule `too-tall` runs in CI (old 55, new 0).",
    "B027": "Computer Core is re-laid in hot/cold-aisle pods; the `walkable` audit proves every cell of the room is reachable.",
    "B028": "Cargo Bay keeps marked forklift aisles; `walkable` / `unreachable-pocket` audit.",
    "B029": "`textures._line()` clips both slice bounds (9,478 wrong hazard-screen pixels fixed).",
    "B030": "`tests/test_walkable.py` now runs the audit's capsule flood fill (reachability of every cell, pockets, aisle widths) instead of `> 12 cells`.",
    "B031": "`tests/test_project.py` checks polygon containment, hull convexity, taper, stair geometry and BOM completeness; `tests/test_audit.py` unit-tests all %d audit rules and runs them over the committed ship." % len(__import__("audit").RULES),
    "B032": "`smoke_test.gd` also checks hull, stairs, batching, room graph and lift-free scene; new `stair_test.gd` drives the player through all decks.",
    "B033": "CI installs Godot 4.7 (the version `project.godot` is saved for), overridable in *Run workflow*.",
    "B034": "The screenshot step is no longer `continue-on-error`; it must write at least 10 images.",
    "B035": "The Blender job compares mount, category, size and bounds of every regenerated model with the committed catalog.",
    "B036": "README states Python 3.13 / bpy 5.2 (the latest) consistently with CI.",
    "B037": "README claims are now backed by checks: the audit proves windows stay clear and every room is walkable.",
    "B038": "`door.gd` derives the collider size and leaf travel from the door model's leaf meshes.",
    "B039": "The dead `locked` feature and `is_open()` were removed from `door.gd`, `Ship.link()` and ship.json.",
    "B040": "Lifts (and their late fade/sound) are gone.",
    "B041": "`flash_fade()` was removed with the lifts.",
    "B042": "`main.gd` keeps one crossfade tween and kills it when the next room starts.",
    "B043": "Loop end computed from the WAV format and channel count.",
    "B044": "Escape uses `ui_cancel`, the pointer is released on focus loss, clicks do not recapture while the deck map is open, mouse sensitivity is an exported property, deck-number keys are removed with the lifts.",
    "B045": "Floor and ceiling holes are implemented (`floor_holes` / `ceiling_holes`, `ShipBuilder._slab`) for the stairwells.",
    "B046": "`load_data()` reports missing / invalid / wrong-version data files and `main.gd` quits with a clear message instead of crashing on a missing key.",
    "B047": "A failed model load is reported with the model id and is not cached.",
    "B048": "Doors fade with `VISIBILITY_RANGE_FADE_SELF` instead of popping; props are batched and culled by room.",
    "B049": "The deck map redraws only when deck, player position/heading or size change.",
    "B050": "`Catalog.pick(label=...)` records labels that matched nothing; the generator prints them and `test_no_label_misses` fails.",
    "B051": "`Ship.link()` validates that the opening lies inside both walls; `deck_y` raises a clear `KeyError`. `test_link_validates_the_opening`.",
    "B052": "Room RNG seeds use `zlib.crc32(room id)`. `test_room_rng_seed_is_unique_per_id`.",
    "B053": "Dead parameters (`light`, `pick_label`, unused `margin`, identical branches) removed or implemented (`margin` now reaches `against_wall`).",
    "B054": "Unused arguments removed from `dressing.py`; `tabletop()` is the single implementation.",
    "B055": "`signs()` respects the wall span bookkeeping (no `check=False`).",
    "B056": "Seats are placed with `seat_facing()` / `seat_behind()`, which derive the chair yaw from the host prop.",
    "B057": "Same as B056 (Ready Room desk chair).",
    "B058": "Lounge seating is placed in front of the window spans facing them.",
    "B059": "The hangar has a real 14 x 7 m stern opening closed by the force field.",
    "B060": "Spawn and all 25 interior camera positions are derived from room geometry and checked by `tests/test_shiplib.py` (inside the room, eye height, not inside a prop).",
    "B061": "The generator no longer exits after writing; leftover storage logic was deleted.",
    "B062": "Unused locals/params removed; CI runs pyflakes on tools, tests and the Blender scripts (the legacy component modules are excluded from the unused-variable check).",
    "B063": "`ceiling_runs` picks the least-used matching model and only runs where they fit; overhead services are explained per BOM line.",
    "B064": "Communications Centre is re-laid; audit 0 overlaps.",
    "B065": "Science Laboratory re-laid; audit 0 overlaps.",
    "B066": "Engineering Workshop re-laid; audit 0 overlaps.",
    "B067": "Brig re-laid; audit 0 overlaps.",
    "B068": "Hydroponics re-laid; audit 0 overlaps.",
    "B069": "Main Engineering re-laid; audit 0 overlaps.",
    "B070": "All rooms re-laid; `footprint-overlap` is an error in CI (old 142 violations, new 0).",
    "B071": "Lounge seating moved clear of the window spans; `window-blocked` audit.",
    "B072": "Bridge and captain's quarters keep windows clear; `window-blocked` audit.",
    "B073": "Wall/floor clash fixed at the engine level (B021).",
    "B074": "Wall/floor clash fixed at the engine level (B021).",
    "B075": "Wall/floor clash fixed at the engine level (B021).",
    "B076": "Wall/floor clash fixed at the engine level (B021).",
    "B077": "Wall/floor clash fixed at the engine level (B021).",
    "B078": "`wall-item-overlap` audit; engine `wall_span_free` bookkeeping (old 27, new 0).",
    "B079": "Duplicate flooding (65 ammo cans in one bay) is gone; the `duplicates` audit warns above 6 of a model per room.",
    "B080": "Family policy: galley equipment only where `policy.ROOM` allows it (old layout: 306 `policy-category` violations, new 0).",
    "B081": "Family policy (antennas only in rooms that need them).",
    "B082": "Family policy (no vending machines in cabins, no cleaning-bot spam).",
    "B083": "Family policy (cell equipment only in the brig and security).",
    "B084": "Family policy (astrometrics gets telescopes, sensors and a star map, not microscopes).",
    "B085": "Table items only stand on work surfaces (B017); tableware only in rooms where people eat.",
    "B086": "Corridors carry no floor panels; nothing is placed in a wall.",
    "B087": "`cleaningbot_wall_window_crawler` rebuilt so it stands on y = 0 (`m.ground()`), catalog entry updated.",
    "B088": "`make_sky`: dead code removed, nebula noise generated at full 2048 x 1024.",
    "B089": "Star latitudes sampled with `arcsin(uniform)` (no pole line).",
    "B090": "Bevel failures are collected in `kit.BEVEL_FAILURES` and reported per model by `build_all.py`.",
    "B091": "`Model.group()` raises on a pivot mismatch; the no-op line was removed.",
    "B092": "`mirror_x` lost its unused parameter; `export()` raises a clear error for an empty model.",
    "B093": "Eight floor models rebuilt to rest on y = 0 (launch rail, cargo door, pressure pod, drill rig, crawler, hover stretcher, x-ray table, stasis pod); `tests/test_blender_tools.py` scans all 1000 models and lists the 53 remaining feet/casters of at most 6 cm with reasons.",
    "B094": "Five models rebuilt: the three dome fixtures no longer stick above the ceiling origin, the EPS trunk and the valve wheel no longer start behind the wall plane; the convention test scans every model.",
    "B095": "`build_all.py` checks every expected texture file before skipping regeneration.",
    "B096": "File handles use context managers; `build_all.py --check` runs without bpy (kit imports bpy lazily), so CI validates the 1000-model plan on a bare Python.",
    "B097": "The grating PBR set is now used: the Power Distribution room has a grating floor.",
    "B098": "Footsteps are DC-free and normalised to one peak (23000/32768); `tests/test_audio.py`.",
    "B099": "`door.wav` is 0.45 s and peaks at the start like the animation; the lift sound was deleted.",
    "B100": "Each sound has its own crc32-seeded RNG; the dead `*0.0` term is gone; CI checks the WAVs are reproducible.",
    "B101": "`test_walkable` delegates to the audit flood fill that now uses the real 0.32 m player capsule and the same solid-prop rule as the builder.",
    "B102": "Stair data, hole alignment and flight connectivity are tested in `tests/test_project.py`; the Godot stair test exercises the real colliders.",
    "B103": "New unit tests for the layout engine, audit, drawings, BOM, audio and Blender tooling (`tests/test_shiplib.py`, `test_audit.py`, `test_draft.py`, `test_audio.py`, `test_blender_tools.py`).",
    "B104": "Every job has a timeout; the Blender job caches pip.",
    "B105": "CI adds pyflakes, BOM and drawing reproducibility, audio reproducibility, `permissions: contents: read` and concurrency cancel.",
    "B106": "README describes the hangar truthfully (stern platform with a force-field opening).",
    "B107": "README statements about furnishing are now backed by the BOM and the audit.",
    "B108": "README performance claims are replaced by measured numbers from `--bench`.",
    "B109": "CONVENTIONS.md lost its agent-only instructions and states the real budget (400 KB hard limit, enforced).",
    "B110": "The unused `triggers` physics layer name was removed.",
    "B111": "Kept on purpose: the ~2,600 machine-generated `.import` sidecars stay ignored and are regenerated by `godot --import` (README, CI); committing them would bury this change. Script `.uid` files are committed as before.",
    "B112": "`tools/preview/run.sh` validates its arguments, uses xvfb only without a display and preserves the exit status.",
    "B113": "`preview.gd` prints usage instead of crashing with no arguments.",
}


def load(p):
    with open(p) as f:
        return json.load(f)


def main():
    defects = load(os.path.join(ROOT, "docs", "bugs", "defects.json"))
    old = load(os.path.join(ROOT, "docs", "bugs", "old_layout_audit.json"))
    missing = [d["id"] for d in defects if d["id"] not in R]
    if missing:
        raise SystemExit("no resolution for " + ", ".join(missing))
    import audit
    ship = load(os.path.join(ROOT, "godot", "data", "ship.json"))
    cat = {m["id"]: m for m in load(os.path.join(ROOT, "godot", "data", "catalog.json"))["models"]}
    new = audit.audit(ship, cat)
    new_count = collections.Counter((v["rule"], v["severity"]) for v in new)
    fixed = [d for d in defects if not R[d["id"]].startswith("Kept on purpose")]
    out = []
    w = out.append
    w("# Bug ledger")
    w("")
    w("*Generated by `python tools/docs/bugs_ledger.py` from `docs/bugs/defects.json`; do not edit by hand.*")
    w("")
    w("Before changing anything, the original game was audited by reading every script and running it: **%d verified defects** "
      "(each with file, line numbers and evidence), plus **%d layout violations** found by running the new audit tool over the "
      "original `ship.json`. This ledger records how every defect was resolved. **%d of %d are fixed**; %d was deliberately kept (with the reason)." % (
          len(defects), old["total_errors"] + old["total_warnings"], len(fixed), len(defects), len(defects) - len(fixed)))
    w("")
    w("## Summary")
    w("")
    areas = collections.OrderedDict()
    for d in defects:
        areas.setdefault(d["area"], collections.Counter())[d["severity"]] += 1
    w("| Area | High | Medium | Low | Total |")
    w("|---|---|---|---|---|")
    for a, c in sorted(areas.items()):
        w("| %s | %d | %d | %d | %d |" % (a, c["high"], c["medium"], c["low"], sum(c.values())))
    tot = collections.Counter(d["severity"] for d in defects)
    w("| **all** | **%d** | **%d** | **%d** | **%d** |" % (tot["high"], tot["medium"], tot["low"], len(defects)))
    w("")
    w("## The original layout, measured")
    w("")
    w("`tools/layout/audit.py` checks footprints, walls, windows, ceilings, mounting, department policy, walkability, BOM and lights. "
      "Run over the original ship (6,679 props) and the new one (%d props):" % sum(len(r["props"]) for r in ship["rooms"]))
    w("")
    w("| Rule | What it catches | Original layout | New layout |")
    w("|---|---|---|---|")
    what = {
        "tabletop-host": "small items standing on chairs, couches, pillars ...", "wall-floor-clash": "wall equipment embedded in furniture",
        "table-support": "table items floating or buried", "policy-category": "equipment in the wrong department (beds in engineering ...)",
        "footprint-overlap": "furniture intersecting furniture", "mount-mismatch": "wall models mid-room, ceiling models on the floor",
        "floating-floor": "floor props not on the floor", "outside-shell": "props inside walls / outside the room",
        "too-tall": "props taller than the room", "ceiling-floor-clash": "ceiling items inside tall furniture",
        "wall-item-span": "wall items past the end of the wall", "wall-item-overlap": "wall items overlapping", "ceiling-overlap": "ceiling items overlapping",
        "lights": "rooms without light fixtures", "window-blocked": "tall props in front of windows", "door-clearance": "props in a doorway",
        "duplicates": "the same model over and over (warning)", "unreachable-pocket": "floor the player cannot reach (warning)",
        "aisle-width": "passages under 0.8 m (warning)", "unknown-room-policy": "rooms the policy does not know (warning)",
    }
    for rule, v in old["rules"].items():
        n_old = v["error"] + v["warn"]
        n_new = new_count.get((rule, "error"), 0) + new_count.get((rule, "warn"), 0)
        w("| `%s` | %s | %d | %d |" % (rule, what.get(rule, ""), n_old, n_new))
    w("| **total** | | **%d** | **%d** |" % (old["total_errors"] + old["total_warnings"], len(new)))
    w("")
    w("(The new layout's remaining entries are warnings only: %s.)" % ", ".join(
        "%s x%d" % (r, n) for (r, s), n in sorted(new_count.items()) if s == "warn") if new else "(none)")
    w("")
    w("## Defects")
    w("")
    for d in defects:
        res = R[d["id"]]
        status = KEPT if res.startswith("Kept on purpose") else FIXED
        w("### %s - %s" % (d["id"], d["title"]))
        w("")
        w("| | |")
        w("|---|---|")
        w("| Severity / area | %s / %s |" % (d["severity"], d["area"]))
        w("| Where | `%s` lines %s |" % (d["file"], d["lines"]))
        w("| Status | **%s** |" % status)
        w("")
        w("*Evidence.* %s" % d["evidence"].replace("\n", " "))
        w("")
        w("*Impact.* %s" % d["impact"].replace("\n", " "))
        w("")
        w("*Resolution.* %s" % res)
        w("")
    path = os.path.join(ROOT, "docs", "BUGS.md")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote %s (%d lines, %d/%d fixed)" % (path, len(out), len(fixed), len(defects)))


if __name__ == "__main__":
    main()
