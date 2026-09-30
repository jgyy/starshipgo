#!/usr/bin/env python3
"""Build the architectural assets (stairs, guard, sign, hull fascia) and their textures.

    python blender/build_arch.py --out godot             # textures + godot/arch/*.glb + data/arch.json
    python blender/build_arch.py --out godot --only fascia
    python blender/build_arch.py --check                 # build one of each into a temp dir, write nothing to godot/

Deterministic; independent of the 1000-model catalogue (build_all.py).
"""
import argparse
import json
import os
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "godot"))
    ap.add_argument("--only", default="", help="regex on the model id")
    ap.add_argument("--check", action="store_true", help="build everything into a temp dir, leave --out untouched")
    ap.add_argument("--no-textures", action="store_true", help="reuse the existing arch textures")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    root = os.path.abspath(os.path.join(HERE, ".."))
    t0 = time.time()

    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from starship import kit, arch, textures_arch

    tmp = None
    if args.check:
        tmp = tempfile.TemporaryDirectory(prefix="arch_check_")
        out = tmp.name
    tex_dir = os.path.join(out, "textures")
    if not args.no_textures or args.check:
        print("generating arch textures ...")
        textures_arch.make_arch_textures(tex_dir)
    arch.TEX_DIR = tex_dir
    kit.TEXTURE_DIR = tex_dir

    rx = re.compile(args.only) if args.only else None
    hull = arch.load_hull(root)
    entries = []
    for mid, fn in arch.ARCH_MODELS.items():
        if rx and not rx.search(mid):
            continue
        m = kit.Model(mid)
        if mid == "arch_hull_fascia":
            fn(m, hull)
        else:
            fn(m)
        rel = f"arch/{mid}.glb"
        path = os.path.join(out, rel)
        info = arch.export_arch(m, path)
        size = os.path.getsize(path)
        entries.append({"id": mid, "file": rel, "bounds_min": info["bounds_min"], "bounds_max": info["bounds_max"],
                        "tris": info["tris"], "bytes": size})
        print(f"  {mid:20s} {info['tris']:6d} tris {size/1024:6.0f} KB")
        if size > 400 * 1024:
            print(f"WARNING: {mid} is larger than 400 KB", file=sys.stderr)

    if not args.check and not rx:
        data_path = os.path.join(out, "data", "arch.json")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        json.dump({"version": 1, "models": entries}, open(data_path, "w"), indent=1)
    elif not args.check and rx and os.path.exists(os.path.join(out, "data", "arch.json")):
        # partial rebuild: merge into the existing list
        data_path = os.path.join(out, "data", "arch.json")
        cur = {e["id"]: e for e in json.load(open(data_path))["models"]}
        for e in entries:
            cur[e["id"]] = e
        json.dump({"version": 1, "models": [cur[k] for k in sorted(cur)]}, open(data_path, "w"), indent=1)
    print(f"done in {time.time()-t0:.0f}s")
    if tmp:
        tmp.cleanup()


if __name__ == "__main__":
    main()
