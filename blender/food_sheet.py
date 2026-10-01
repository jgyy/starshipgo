#!/usr/bin/env python3
"""Render GLB models with Blender Cycles (headless) into a labelled contact sheet.

    python blender/food_sheet.py out.jpg --cols 6 --size 320 godot/models/meal/*.glb
    python blender/food_sheet.py out.jpg --ids meal_burger_with_fries,drink_latte_art   (ids looked up in the catalog)

Needs bpy and Pillow (development tool for docs/FOOD.md; not used by the build or CI).
"""
import argparse
import json
import math
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def setup_scene(bpy, size, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.78, 0.82, 0.88, 1)
    bg.inputs[1].default_value = 0.45
    sc.world = w
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 70
    sc.collection.objects.link(cam)
    sc.camera = cam
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 4.0
    sun.data.angle = math.radians(12)
    sun.rotation_euler = (math.radians(48), math.radians(8), math.radians(-35))
    sc.collection.objects.link(sun)
    fill = bpy.data.objects.new("fill", bpy.data.lights.new("fill", "AREA"))
    fill.data.energy = 160
    fill.data.size = 2.5
    fill.location = (1.2, -1.8, 1.0)
    fill.rotation_euler = (math.radians(70), 0, math.radians(25))
    sc.collection.objects.link(fill)
    pm = bpy.data.materials.new("floor")
    pm.use_nodes = True
    pm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.30, 0.27, 0.24, 1)
    pm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.55
    return sc, cam, pm


def render_one(bpy, sc, cam, pm, glb, out_png, az=35.0, el=27.0, fit=1.0):
    from mathutils import Vector
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    objs = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            lo = Vector(min(a, b) for a, b in zip(lo, p))
            hi = Vector(max(a, b) for a, b in zip(hi, p))
    ctr = (lo + hi) / 2
    rad = (hi - lo).length / 2
    pl = bpy.data.objects.new("floor", bpy.data.meshes.new("floor"))
    pl.data.from_pydata([(-3, -3, 0), (3, -3, 0), (3, 3, 0), (-3, 3, 0)], [], [(0, 1, 2, 3)])
    pl.data.materials.append(pm)
    pl.location = (0, 0, lo.z - 0.0005)
    sc.collection.objects.link(pl)
    d = rad / math.sin(math.atan(18.0 / cam.data.lens)) / fit
    a, e = math.radians(az), math.radians(el)
    cam.location = ctr + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * d
    direction = ctr - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = 0.01
    cam.data.sensor_width = 36
    sc.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    for o in objs + [pl]:
        me = o.data
        bpy.data.objects.remove(o)
        if me.users == 0:
            bpy.data.meshes.remove(me)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--ids", default="")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--size", type=int, default=320)
    ap.add_argument("--samples", type=int, default=24)
    ap.add_argument("--godot", default=os.path.join(HERE, "..", "godot"))
    ap.add_argument("--view", default="35,27", help="azimuth,elevation in degrees")
    ap.add_argument("--no-labels", action="store_true")
    a = ap.parse_args()
    files = list(a.files)
    if a.ids:
        cat = {m["id"]: m for m in json.load(open(os.path.join(a.godot, "data", "catalog.json")))["models"]}
        files += [os.path.join(a.godot, cat[i]["file"]) for i in a.ids.split(",")]
    import bpy
    from PIL import Image, ImageDraw
    sc, cam, pm = setup_scene(bpy, a.size, a.samples)
    az, el = [float(x) for x in a.view.split(",")]
    tmp = tempfile.mkdtemp()
    tiles = []
    for i, f in enumerate(files):
        png = os.path.join(tmp, "%03d.png" % i)
        render_one(bpy, sc, cam, pm, f, png, az, el)
        tiles.append((os.path.splitext(os.path.basename(f))[0], png))
    cols = min(a.cols, len(tiles))
    rows = (len(tiles) + cols - 1) // cols
    lab = 0 if a.no_labels else 16
    sheet = Image.new("RGB", (cols * a.size, rows * (a.size + lab)), (24, 24, 26))
    dr = ImageDraw.Draw(sheet)
    for i, (name, png) in enumerate(tiles):
        x, y = (i % cols) * a.size, (i // cols) * (a.size + lab)
        sheet.paste(Image.open(png).convert("RGB"), (x, y))
        if lab:
            dr.text((x + 4, y + a.size + 2), name, fill=(235, 235, 235))
    sheet.save(a.out, quality=88)
    print("wrote", a.out, len(tiles), "models")


if __name__ == "__main__":
    sys.exit(main())
