#!/usr/bin/env python3
"""Contact sheet of every surface set (albedo | normal | roughness) and every screen texture.

    python tools/quality/texture_atlas.py                       # writes docs/screenshots/texture_atlas.jpg
    python tools/quality/texture_atlas.py --dir /tmp/prev --out /tmp/atlas.jpg --section surfaces

Needs pillow.  Each surface cell shows the albedo tiled 2x2 (so seams are visible), the normal map and the
roughness channel of the ORM map.
"""
import argparse
import glob
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))


def surface_names(d):
    return sorted(os.path.basename(p)[:-len("_albedo.png")] for p in glob.glob(os.path.join(d, "*_albedo.png")))


def surface_sheet(d, cell=112, cols=6):
    names = surface_names(d)
    rows = (len(names) + cols - 1) // cols
    pad, lab = 6, 14
    w = cols * (3 * cell + 4 * pad)
    h = rows * (cell + lab + pad)
    sheet = Image.new("RGB", (w, h), (18, 20, 24))
    dr = ImageDraw.Draw(sheet)
    for i, name in enumerate(names):
        x0 = (i % cols) * (3 * cell + 4 * pad) + pad
        y0 = (i // cols) * (cell + lab + pad) + pad
        a = Image.open(os.path.join(d, name + "_albedo.png")).convert("RGB")
        t = Image.new("RGB", (a.width * 2, a.height * 2))
        for ox in (0, 1):
            for oy in (0, 1):
                t.paste(a, (ox * a.width, oy * a.height))
        sheet.paste(t.resize((cell, cell), Image.LANCZOS), (x0, y0))
        n = Image.open(os.path.join(d, name + "_normal.png")).convert("RGB")
        sheet.paste(n.resize((cell, cell), Image.LANCZOS), (x0 + cell + pad, y0))
        o = Image.open(os.path.join(d, name + "_orm.png")).convert("RGB").split()[1]
        sheet.paste(o.resize((cell, cell), Image.LANCZOS).convert("RGB"), (x0 + 2 * (cell + pad), y0))
        dr.text((x0, y0 + cell + 1), name, fill=(220, 225, 235))
    return sheet


def screen_sheet(d, cell=96, cols=12):
    files = sorted(glob.glob(os.path.join(d, "*.png")))
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (cell + 6) + 6, rows * (cell + 18) + 6), (18, 20, 24))
    dr = ImageDraw.Draw(sheet)
    for i, p in enumerate(files):
        x0 = (i % cols) * (cell + 6) + 6
        y0 = (i // cols) * (cell + 18) + 6
        sheet.paste(Image.open(p).convert("RGB").resize((cell, cell), Image.LANCZOS), (x0, y0))
        dr.text((x0, y0 + cell + 1), os.path.basename(p)[:-4][:16], fill=(200, 210, 225))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(ROOT, "godot", "textures", "surfaces"))
    ap.add_argument("--screens", default=os.path.join(ROOT, "godot", "textures", "screens"))
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "screenshots", "texture_atlas.jpg"))
    ap.add_argument("--section", choices=("all", "surfaces", "screens"), default="all")
    a = ap.parse_args()
    parts = []
    if a.section in ("all", "surfaces"):
        parts.append(surface_sheet(a.dir))
    if a.section in ("all", "screens") and os.path.isdir(a.screens):
        parts.append(screen_sheet(a.screens))
    w = max(p.width for p in parts)
    sheet = Image.new("RGB", (w, sum(p.height for p in parts)), (18, 20, 24))
    y = 0
    for p in parts:
        sheet.paste(p, (0, y))
        y += p.height
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    sheet.save(a.out, quality=82, optimize=True)
    print(a.out, sheet.size)


if __name__ == "__main__":
    main()
