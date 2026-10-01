#!/usr/bin/env python3
"""Build the StarshipGo component library with headless Blender (bpy).

    python blender/build_all.py --out godot                # everything, 4 processes
    python blender/build_all.py --out godot --only door    # only categories/labels matching
    python blender/build_all.py --out godot --check        # validate catalog only (no export)

Outputs (relative to --out):
    models/<category>/<id>.glb     one GLB per component
    textures/screens|surfaces|sky  generated texture files
    data/catalog.json              machine readable catalogue (bounds, tags, mount ...)
"""
import argparse
import importlib
import json
import os
import pkgutil
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TARGET = 1198   # 1000 original components + 196 food and drink models + 2 deck signs (blender/starship/components/food*.py)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def load_families():
    from starship import kit
    import starship.components as comps
    for m in pkgutil.iter_modules(comps.__path__):
        importlib.import_module(f"starship.components.{m.name}")
    return kit.FAMILIES


def plan(families):
    """Expand families into the flat list of models (id, family, index, label)."""
    out, seen = [], set()
    for fam in families:
        for i, label in enumerate(fam["labels"]):
            mid = f"{fam['category']}_{slug(label)}"
            if mid in seen:
                raise SystemExit(f"duplicate model id {mid}")
            seen.add(mid)
            out.append({"id": mid, "fam": fam, "i": i, "label": label})
    return out


def missing_textures(tex_dir, textures):
    """Every texture file the generators produce that does not exist yet."""
    want = [os.path.join("screens", n + ".png") for n in textures.SCREENS]
    from starship import textures_ext
    for n in list(textures.SURFACES) + list(textures_ext.REG):
        want += [os.path.join("surfaces", f"{n}_{k}.png") for k in ("albedo", "normal", "orm")]
    want.append(os.path.join("surfaces", "index.json"))
    from starship import textures_decals
    want += [os.path.join("decals", n + ".png") for n in textures_decals.DECALS]
    want += [os.path.join("sky", "stars.png"), os.path.join("sky", "planet.png")]
    return [w for w in want if not os.path.exists(os.path.join(tex_dir, w))]


def food_textures(tex_dir):
    """Generate the procedural food albedo maps (godot/textures/food/*.jpg) that do not exist yet."""
    from starship import textures_food
    todo = textures_food.missing(tex_dir)
    if todo:
        print(f"generating {len(todo)} food textures ...")
        textures_food.make_all(tex_dir, only=set(todo))


def make_all_textures(tex_dir, jobs=4, only=""):
    """Screens (21 + 41 extended), the original + extended PBR surfaces, the sky and the surface index.
    only: regex - regenerate just the extended surfaces whose name matches (quick iteration)."""
    from starship import textures, textures_decals, textures_ext
    if only:
        rx = re.compile(only)
        textures_ext.make_ext_surfaces(tex_dir, names=[k for k in textures_ext.REG if rx.search(k)], jobs=jobs)
        return
    textures.make_screens(tex_dir)
    textures.make_surfaces(tex_dir)
    textures_ext.make_ext_surfaces(tex_dir, jobs=jobs)      # also writes surfaces/index.json
    textures_decals.make_decals(tex_dir)
    textures.make_sky(tex_dir)


def run_shard(args, shard, nshards):
    import bpy
    from starship import kit
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out = os.path.abspath(args.out)
    kit.TEXTURE_DIR = os.path.join(out, "textures")
    fams = load_families()
    items = plan(fams)
    if args.only:
        rx = re.compile(args.only)
        items = [it for it in items if rx.search(it["id"])]
    catalog = []
    t0 = time.time()
    for n, it in enumerate(items):
        if n % nshards != shard:
            continue
        fam = it["fam"]
        m = kit.Model(it["id"])
        m.mount = fam["mount"]
        rng = kit.seeded(it["id"])
        fam["fn"](m, it["i"], it["label"], rng)
        path = os.path.join(out, "models", fam["category"], it["id"] + ".glb")
        info = kit.export(m, path)
        lo, hi = info["bounds_min"], info["bounds_max"]
        catalog.append({
            "id": it["id"], "category": fam["category"], "label": it["label"],
            "file": f"models/{fam['category']}/{it['id']}.glb", "mount": fam["mount"],
            "mount_y": fam["mount_y"], "tags": fam["tags"], "solid": fam["solid"],
            "size": [round(hi[k] - lo[k], 3) for k in range(3)],
            "bounds_min": lo, "bounds_max": hi, "tris": info["tris"], "top_y": info["top_y"],
            "bytes": os.path.getsize(path), "family": fam["fn"].__name__,
        })
        if (len(catalog)) % 25 == 0:
            print(f"[shard {shard}] {len(catalog)} models, {time.time()-t0:.0f}s", flush=True)
    part = os.path.join(out, "data", f"catalog.part{shard}.json")
    os.makedirs(os.path.dirname(part), exist_ok=True)
    with open(part, "w") as fh:
        json.dump(catalog, fh)
    # bevel failures are swallowed by the kit (geometry stays un-bevelled): report one line per model
    per_model = {}
    for mname, prim in kit.BEVEL_FAILURES:
        per_model.setdefault(mname, []).append(prim)
    for mname, prims in sorted(per_model.items()):
        print(f"WARNING [shard {shard}] {mname}: {len(prims)} bevel failure(s) ({', '.join(sorted(set(prims)))})",
              flush=True)
    if per_model:
        print(f"[shard {shard}] bevel failures in {len(per_model)} model(s), "
              f"{len(kit.BEVEL_FAILURES)} primitive(s) total", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "godot"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", default="")
    ap.add_argument("--check", action="store_true", help="validate the plan without exporting")
    ap.add_argument("--textures", action="store_true", help="(re)generate textures only")
    ap.add_argument("--shard", default="", help="internal: i/n")
    args = ap.parse_args()
    out = os.path.abspath(args.out)

    if args.shard:
        i, n = map(int, args.shard.split("/"))
        run_shard(args, i, n)
        return

    if args.textures:
        print("generating textures ...")
        t0 = time.time()
        make_all_textures(os.path.join(out, "textures"), args.jobs, args.only)
        if not args.only:
            from starship import textures_arch
            textures_arch.make_arch_textures(os.path.join(out, "textures"))
        print(f"textures done in {time.time()-t0:.0f}s")
        food_textures(os.path.join(out, "textures"))
        return

    fams = load_families()
    items = plan(fams)
    cats = {}
    for it in items:
        cats[it["fam"]["category"]] = cats.get(it["fam"]["category"], 0) + 1
    print(f"{len(items)} models in {len(cats)} categories")
    if len(items) != TARGET and not args.only:
        print(f"ERROR: expected exactly {TARGET} models, planned {len(items)}", file=sys.stderr)
        for c, k in sorted(cats.items()):
            print(f"  {c}: {k}", file=sys.stderr)
        sys.exit(1)
    if args.check:
        return

    from starship import textures
    tex_dir = os.path.join(out, "textures")
    if missing_textures(tex_dir, textures):
        print("generating textures ...")
        make_all_textures(tex_dir, args.jobs)
    food_textures(tex_dir)
    t0 = time.time()
    procs = [subprocess.Popen([sys.executable, __file__, "--out", out, "--only", args.only,
                               "--shard", f"{k}/{args.jobs}"]) for k in range(args.jobs)]
    rc = [p.wait() for p in procs]
    if any(rc):
        sys.exit("a build shard failed")
    catalog = []
    ddir = os.path.join(out, "data")
    for k in range(args.jobs):
        p = os.path.join(ddir, f"catalog.part{k}.json")
        with open(p) as fh:
            catalog += json.load(fh)
        os.remove(p)
    catalog.sort(key=lambda c: (c["category"], c["id"]))
    if args.only in ("", "."):
        with open(os.path.join(ddir, "catalog.json"), "w") as fh:
            json.dump({"version": 1, "count": len(catalog), "models": catalog}, fh, indent=1)
    print(f"built {len(catalog)} GLBs in {time.time()-t0:.0f}s, "
          f"{sum(c['bytes'] for c in catalog)/1e6:.1f} MB, {sum(c['tris'] for c in catalog)} tris")


if __name__ == "__main__":
    main()
