"""Decals / signage / stencil labels (256x128 RGBA PNGs in godot/textures/decals).

They are plain alpha-cut stickers for Decal nodes or quads: door number plates, hazard labels, painted stencils and
direction chevrons.  Pure numpy; written through bpy by textures_lib.write_png.
"""
import os

import numpy as np

from . import textures_lib as L
from .textures_arch import _stencil

W, H = 256, 128


def _plate(text, base, ink, border):
    m = np.zeros((W, W), bool)               # _stencil wraps at the mask's first dimension: stamp on a square
    scale = 6 if len(text) <= 4 else 5
    width = len(text) * 6 * scale - scale
    _stencil(m, text, (W - width) // 2, (H - 7 * scale) // 2, scale)
    m = m[:H]
    y, x = np.mgrid[0:H, 0:W]
    edge = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y))
    rgb = np.ones((H, W, 3), np.float32) * np.array(L.hexc(base))
    rgb = np.where((edge < 8)[..., None], np.array(L.hexc(border)), rgb)
    ink_m = L.blur(m.astype(np.float32), 0.8)
    rgb = rgb * (1 - ink_m[..., None]) + np.array(L.hexc(ink)) * ink_m[..., None]
    return rgb, np.ones((H, W), np.float32)


def door_plate(n):
    return _plate(f"D-{n}", "#d8dde2", "#1d2430", "#3a6ea5")


def stencil(text, ink="#e8e8e0", base="#000000", alpha_ink=0.9):
    m = np.zeros((W, W), bool)               # _stencil wraps at the mask's first dimension: stamp on a square
    scale = 8 if len(text) <= 3 else 6
    width = len(text) * 6 * scale - scale
    _stencil(m, text, (W - width) // 2, (H - 7 * scale) // 2, scale)
    m = m[:H]
    a = L.blur(m.astype(np.float32), 0.9) * alpha_ink
    rgb = np.ones((H, W, 3), np.float32) * np.array(L.hexc(ink))
    return rgb, a


def hazard_stripe():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = ((x + y) / 32.0) % 1
    m = L.soft((np.abs(t - 0.5) - 0.25) * 32 * 0.7, 2.0)
    rgb = np.array(L.hexc("#e2b514")) * (1 - m[..., None]) + np.array(L.hexc("#1c1c1e")) * m[..., None]
    edge = np.minimum(np.minimum(x, W - 1 - x), np.minimum(y, H - 1 - y))
    return rgb, L.soft(edge - 1, 2.0)


def hazard_triangle(color="#e2b514"):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, base, top = W / 2, H - 8, 8
    half = (y - top) / (base - top) * 52
    edge = np.minimum(np.minimum(y - top, base - y), (half - np.abs(x - cx)) * 0.87)
    outline = L.soft(edge, 1.5) * (1 - L.soft(edge - 6, 1.5))
    body = L.soft(edge - 6, 1.5)
    bang = (np.abs(x - cx) < 4) & (y > 48) & (y < 88) | (np.hypot(x - cx, y - 98) < 5)
    rgb = np.ones((H, W, 3), np.float32) * np.array(L.hexc(color))
    ink = L.blur(bang.astype(np.float32), 0.8) * body
    rgb = rgb * (1 - ink[..., None]) + np.array(L.hexc("#111111")) * ink[..., None]
    return rgb, np.clip(outline + body, 0, 1)


def chevrons(color="#e2b514"):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.zeros((H, W), np.float32)
    for k in range(3):
        cx = 50 + k * 64
        d = np.abs((np.abs(y - H / 2) * 0.9) - (cx - x))
        a = np.maximum(a, L.soft(9 - d, 1.8) * (x < cx + 6) * (x > cx - 60))
    rgb = np.ones((H, W, 3), np.float32) * np.array(L.hexc(color))
    return rgb, a


DECALS = {
    "door_plate_101": lambda: door_plate("101"), "door_plate_204": lambda: door_plate("204"),
    "door_plate_305": lambda: door_plate("305"), "door_plate_a12": lambda: door_plate("A12"),
    "door_plate_c4": lambda: door_plate("C4"), "door_plate_h2": lambda: door_plate("H2"),
    "stencil_a12": lambda: stencil("A-12"), "stencil_c4": lambda: stencil("C4"),
    "stencil_d1": lambda: stencil("D1"), "stencil_cargo_s": lambda: stencil("CS-7", "#d8b523"),
    "hazard_stripe": hazard_stripe, "hazard_triangle": hazard_triangle,
    "chevrons_yellow": chevrons, "chevrons_white": lambda: chevrons("#e8e8e0"),
}


def make_decals(outdir):
    d = os.path.join(outdir, "decals")
    for name, fn in DECALS.items():
        rgb, a = fn()
        L.write_png(os.path.join(d, name + ".png"), np.concatenate([np.clip(rgb, 0, 1), np.clip(a, 0, 1)[..., None]], axis=2))
